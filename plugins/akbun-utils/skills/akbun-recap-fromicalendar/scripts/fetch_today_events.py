#!/usr/bin/env python3
"""오늘(00:00~23:30) iCalendar 일정을 JSON으로 출력한다.

사용법:
    python3 fetch_today_events.py <ICS_PATH_OR_URL> [--date YYYY-MM-DD] [--end HH:MM]

표준 라이브러리만 사용한다. VEVENT의 DTSTART/DTEND, 날짜만 있는 종일 일정,
TZID/UTC 시각, 단순 RRULE(DAILY/WEEKLY/MONTHLY/YEARLY + INTERVAL/BYDAY/UNTIL),
EXDATE를 처리한다.
"""

import argparse
import datetime as dt
import json
import re
import sys
import urllib.request

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

WEEKDAYS = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}


def read_ics(source):
    if re.match(r"^https?://", source):
        with urllib.request.urlopen(source, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    with open(source, encoding="utf-8", errors="replace") as f:
        return f.read()


def unfold(text):
    """RFC 5545 line folding 해제."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    for line in lines:
        if line[:1] in (" ", "\t") and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return out


def parse_prop(line):
    """'NAME;PARAM=V:value' -> (name, params, value)"""
    m = re.match(r"^([^;:]+)((?:;[^:]*)?):(.*)$", line)
    if not m:
        return None
    name = m.group(1).upper()
    params = {}
    for part in m.group(2).lstrip(";").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            params[k.upper()] = v
    return name, params, m.group(3)


def tz_of(params, local_tz):
    tzid = params.get("TZID")
    if tzid and ZoneInfo:
        try:
            return ZoneInfo(tzid)
        except Exception:
            pass
    return local_tz


def parse_dt(value, params, local_tz):
    """(datetime | date, is_all_day) 반환. datetime은 local_tz 기준으로 변환."""
    value = value.strip()
    if params.get("VALUE") == "DATE" or re.fullmatch(r"\d{8}", value):
        d = dt.datetime.strptime(value[:8], "%Y%m%d").date()
        return d, True
    m = re.fullmatch(r"(\d{8})T(\d{6})(Z?)", value)
    if not m:
        return None, False
    naive = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
    if m.group(3) == "Z":
        aware = naive.replace(tzinfo=dt.timezone.utc)
    else:
        aware = naive.replace(tzinfo=tz_of(params, local_tz))
    return aware.astimezone(local_tz), False


def parse_events(lines, local_tz):
    events, cur = [], None
    for line in lines:
        if line == "BEGIN:VEVENT":
            cur = {"exdates": set()}
        elif line == "END:VEVENT" and cur is not None:
            events.append(cur)
            cur = None
        elif cur is not None:
            prop = parse_prop(line)
            if not prop:
                continue
            name, params, value = prop
            if name == "SUMMARY":
                cur["summary"] = value.replace("\\,", ",").replace("\\n", " ").strip()
            elif name == "LOCATION":
                cur["location"] = value.replace("\\,", ",").strip()
            elif name == "STATUS":
                cur["status"] = value.strip().upper()
            elif name == "DTSTART":
                cur["dtstart"], cur["all_day"] = parse_dt(value, params, local_tz)
            elif name == "DTEND":
                cur["dtend"], _ = parse_dt(value, params, local_tz)
            elif name == "RRULE":
                cur["rrule"] = dict(
                    p.split("=", 1) for p in value.split(";") if "=" in p
                )
            elif name == "EXDATE":
                for v in value.split(","):
                    d, _ = parse_dt(v, params, local_tz)
                    if d is not None:
                        date = d if isinstance(d, dt.date) and not isinstance(d, dt.datetime) else d.date()
                        cur["exdates"].add(date)
    return [e for e in events if e.get("dtstart") is not None]


def occurs_today(event, target, local_tz):
    """반복 규칙 포함, target 날짜에 발생하는지 판단."""
    start = event["dtstart"]
    start_date = start if event["all_day"] else start.date()
    if target in event["exdates"]:
        return False
    rrule = event.get("rrule")
    if not rrule:
        return start_date <= target <= end_date_of(event, start_date)
    if target < start_date:
        return False
    until = rrule.get("UNTIL")
    if until:
        u, _ = parse_dt(until, {}, local_tz)
        u_date = u if isinstance(u, dt.date) and not isinstance(u, dt.datetime) else u.date()
        if target > u_date:
            return False
    freq = rrule.get("FREQ", "").upper()
    interval = int(rrule.get("INTERVAL", 1) or 1)
    delta_days = (target - start_date).days
    if freq == "DAILY":
        return delta_days % interval == 0
    if freq == "WEEKLY":
        byday = [d for d in rrule.get("BYDAY", "").split(",") if d in WEEKDAYS]
        weekdays = {WEEKDAYS[d] for d in byday} if byday else {start_date.weekday()}
        weeks = (target - (start_date - dt.timedelta(days=start_date.weekday()))).days // 7
        return target.weekday() in weekdays and weeks % interval == 0
    if freq == "MONTHLY":
        months = (target.year - start_date.year) * 12 + target.month - start_date.month
        return target.day == start_date.day and months % interval == 0
    if freq == "YEARLY":
        return (
            (target.year - start_date.year) % interval == 0
            and (target.month, target.day) == (start_date.month, start_date.day)
        )
    return False


def end_date_of(event, start_date):
    """단발 일정의 마지막 포함 날짜."""
    end = event.get("dtend")
    if end is None:
        return start_date
    if event["all_day"]:
        return end - dt.timedelta(days=1)  # DTEND(DATE)는 exclusive
    end_date = end.date()
    if end.time() == dt.time(0, 0) and end_date > start_date:
        return end_date - dt.timedelta(days=1)
    return end_date


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help=".ics 파일 경로 또는 URL")
    ap.add_argument("--date", help="대상 날짜(YYYY-MM-DD), 기본은 오늘")
    ap.add_argument("--end", default="23:30", help="집계 종료 시각(HH:MM), 기본 23:30")
    args = ap.parse_args()

    local_tz = dt.datetime.now().astimezone().tzinfo
    target = (
        dt.datetime.strptime(args.date, "%Y-%m-%d").date()
        if args.date
        else dt.datetime.now(local_tz).date()
    )
    end_h, end_m = (int(x) for x in args.end.split(":"))
    window_start = dt.datetime.combine(target, dt.time(0, 0), tzinfo=local_tz)
    window_end = dt.datetime.combine(target, dt.time(end_h, end_m), tzinfo=local_tz)

    events = parse_events(unfold(read_ics(args.source)), local_tz)
    result = []
    for e in events:
        if e.get("status") == "CANCELLED":
            continue
        if not occurs_today(e, target, local_tz):
            continue
        if e["all_day"]:
            result.append({
                "start": None,
                "end": None,
                "all_day": True,
                "summary": e.get("summary", "(제목 없음)"),
                "location": e.get("location"),
            })
            continue
        start = e["dtstart"]
        occ_start = dt.datetime.combine(target, start.timetz())
        duration = (e["dtend"] - e["dtstart"]) if e.get("dtend") else dt.timedelta(0)
        occ_end = occ_start + duration
        if occ_end < window_start or occ_start > window_end:
            continue
        result.append({
            "start": occ_start.strftime("%H:%M"),
            "end": occ_end.strftime("%H:%M") if duration else None,
            "all_day": False,
            "summary": e.get("summary", "(제목 없음)"),
            "location": e.get("location"),
        })

    result.sort(key=lambda x: (0 if x["all_day"] else 1, x["start"] or ""))
    json.dump(
        {"date": target.isoformat(), "window": f"00:00-{args.end}", "events": result},
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    print()


if __name__ == "__main__":
    main()
