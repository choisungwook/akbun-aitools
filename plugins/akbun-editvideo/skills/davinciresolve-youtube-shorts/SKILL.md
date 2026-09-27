---
name: davinciresolve-youtube-shorts
description: Create vertical YouTube Shorts candidates from the selected DaVinci Resolve timeline, preserve its media and audio processing, and publish the approved exports.
disable-model-invocation: true
---

# DaVinci Resolve YouTube Shorts

Use the currently selected timeline as the source. Before editing, record its name, start/end frames, frame rate, video/audio track counts, per-track item counts, and resolution. Do not modify the source timeline.

Create a candidate list first: each of the 20 suggestions needs a distinct hook and exact short in/out timecodes. Candidates may overlap; do not imply they are independent sections when they reuse footage. Convert seconds to frames using the source frame rate and compute `short duration + pre-handle + post-handle` before creating anything. Check each candidate against the timeline start/end bounds.

For each feasible candidate, duplicate the source into a uniquely named timeline. Confirm the duplicate retains the original audio track count, per-track item counts, and processing before changing settings. Set custom timeline settings before setting portrait 2160×3840, square pixels, and fill-screen scaling. Check every API return value and re-read settings to confirm the applied dimensions, frame rate, and scaling. If a duplicate, setting, or re-read check fails, stop and report the completed candidates; do not silently continue with a partial batch.

Run Smart Reframe on each video clip and check the call result. Inspect representative frames for clipped or misplaced subjects. A successful API call is not proof that framing is acceptable. Preserve source audio tracks and processing. Add a duration marker spanning only the suggested short; use a frame position relative to the timeline start plus its start frame, and a duration in frames. Verify the marker stays within the duplicate's bounds and has the intended duration.

Check feasibility first: a 60-second short plus two 15-second handles requires at least 90 seconds of usable timeline. If the source is shorter, report the maximum feasible short duration and handle lengths, and ask which constraint to relax before creating candidate timelines. Do not pad with black, silently shorten the short, or claim unavailable handles.

Render only the requested candidates using an available vertical YouTube 2160p preset. Do not assume a preset named `YouTube - 2160p` is portrait: inspect the selected preset and confirm the output is 2160×3840. Before upload, inspect the rendered dimensions, duration, audio, title, description, category, location, thumbnail, and visibility. Upload only when explicitly requested; default visibility to Private. Report each timeline name, marker range, render path, and upload status.

After the batch, compare the source timeline's name, bounds, settings, and track counts with the preflight record. Report any mismatch instead of claiming the source was preserved.
