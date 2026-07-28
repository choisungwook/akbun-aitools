# Cloud Custodian으로 AWS FinOps 자동화하기 (EC2 / RDS)

## 목적

- Cloud Custodian 정책으로 EC2, EBS, RDS의 낭비 자원을 탐지하고 중지·정리까지 자동화한다

<!-- akbun-writing: 왜 이 실습을 했는지 배경 추가 -->

## 원리

### Custodian 정책의 3요소

Custodian 정책 하나는 `resource` -> `filters` -> `actions` 순서로 실행된다.

| 요소 | 역할 | FinOps에서의 의미 |
|---|---|---|
| `resource` | 대상 AWS 리소스 타입 (`aws.ec2`, `aws.rds`) | 비용이 발생하는 자원의 범위 |
| `filters` | 조건에 맞는 리소스만 남김 (tag, metrics, age) | "낭비"의 정의 |
| `actions` | 남은 리소스에 수행할 작업 (`stop`, `delete`, `tag`) | 비용 절감 실행 |

### 비용이 새는 지점과 대응 filter

| 낭비 유형 | 탐지 filter | 대응 action |
|---|---|---|
| 야간·주말에 켜둔 dev 서버 | `offhour` / `onhour` | `stop` / `start` |
| 저사용률 instance | `metrics` (CPUUtilization) | `mark-for-op` -> `stop` |
| 주인 없는 자원 | `tag:Owner` absent | `mark-for-op` -> `stop` |
| orphan EBS volume | `State: available` | `mark-for-op` -> `delete` |
| 접속 없는 RDS | `metrics` (DatabaseConnections) | `stop` |
| 오래된 수동 snapshot | `age` | `delete` |

### mark-for-op: 유예 기간을 둔 삭제

Custodian의 FinOps 정책은 대부분 즉시 삭제하지 않고 두 단계로 나눈다.

1. 1단계 정책이 `mark-for-op` action으로 리소스에 tag를 붙인다. tag 값에 `실행할 op`와 `실행 날짜`가 들어간다.
2. 2단계 정책이 `marked-for-op` filter로 날짜가 지난 리소스만 골라 실제 작업을 수행한다.

이 구조 덕분에 소유자가 유예 기간 안에 tag를 지우면 대상에서 빠진다. 상태는 AWS tag에만 저장되므로 Custodian 자체는 상태를 갖지 않는다.

### 실행 모드

| mode | 실행 주체 | 용도 |
|---|---|---|
| pull (기본) | 로컬 CLI | 실습, 일회성 점검 |
| periodic | Lambda + EventBridge 스케줄 | 매일 정기 점검 |
| cloudtrail | Lambda + CloudTrail event | 자원 생성 즉시 tag 검사 |

<!-- akbun-writing: 실무에서 어떤 mode를 골랐고 왜 그랬는지 추가 -->

## 환경

| 항목 | 값 |
|---|---|
| OS | Ubuntu 24.04 |
| Python | 3.12 |
| Cloud Custodian (c7n) | 0.9.51 |
| AWS Region | ap-northeast-2 |

## 사전 준비

- EC2, EBS, RDS, CloudWatch 조회 및 stop/start 권한이 있는 AWS 자격 증명
- Python 3.10 이상
- 실습 대상 리소스에 `Environment: dev` tag 부여 (offhours 정책의 대상 조건)

## 단계

1. 가상환경을 만들고 Cloud Custodian을 설치한다.

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install c7n==0.9.51
   custodian version
   ```

2. AWS 자격 증명과 region을 설정한다.

   ```sh
   export AWS_PROFILE=finops
   export AWS_DEFAULT_REGION=ap-northeast-2
   aws sts get-caller-identity
   ```

3. 정책 파일 문법을 검증한다. AWS 호출 없이 스키마만 확인한다.

   ```sh
   custodian validate policies/*.yml
   ```

4. dry-run으로 대상 리소스만 조회한다. `--dryrun`은 filter까지만 실행하고 action은 건너뛴다.

   ```sh
   custodian run --dryrun --output-dir=out policies/ec2-idle-cpu-mark.yml
   ```

5. dry-run 결과를 표로 확인한다.

   ```sh
   custodian report --format grid --output-dir=out policies/ec2-idle-cpu-mark.yml
   ```

6. EC2 야간 중지 정책을 실제로 적용한다.

   ```sh
   custodian run --output-dir=out policies/ec2-offhours-stop.yml
   ```

7. 태그 없는 EC2를 표시하고, 유예 기간이 지난 것만 중지한다. 두 정책은 순서대로 실행한다.

   ```sh
   custodian run --output-dir=out policies/ec2-untagged-mark-stop.yml
   custodian run --output-dir=out policies/ec2-marked-stop.yml
   ```

8. RDS 정책을 적용한다. 유휴 instance 중지와 만료된 수동 snapshot 삭제를 함께 돌린다.

   ```sh
   custodian run --output-dir=out policies/rds-idle-stop.yml
   custodian run --output-dir=out policies/rds-snapshot-expired-delete.yml
   ```

9. 사용하지 않는 EBS volume을 삭제 대상으로 표시한다.

   ```sh
   custodian run --output-dir=out policies/ebs-unattached-mark-delete.yml
   ```

<!-- akbun-writing: 중간에 실패했던 경험이나 잘못 지운 리소스가 있으면 여기 추가 -->

## 정책 목록

| 파일 | 대상 | 동작 |
|---|---|---|
| `policies/ec2-offhours-stop.yml` | EC2 | 평일 20시 이후·주말 dev instance 중지 |
| `policies/ec2-onhours-start.yml` | EC2 | 평일 09시 dev instance 재시작 |
| `policies/ec2-untagged-mark-stop.yml` | EC2 | Owner/CostCenter tag 누락 시 3일 뒤 stop 표시 |
| `policies/ec2-marked-stop.yml` | EC2 | 표시된 instance 중 유예 기간 경과분 중지 |
| `policies/ec2-idle-cpu-mark.yml` | EC2 | 14일 평균 CPU 5% 미만이면 7일 뒤 stop 표시 |
| `policies/ebs-unattached-mark-delete.yml` | EBS | 미연결 volume을 7일 뒤 delete 표시 |
| `policies/rds-idle-stop.yml` | RDS | 14일간 접속 0인 dev instance 중지 |
| `policies/rds-oversized-storage-mark.yml` | RDS | storage 과다 할당 후보에 검토 tag 부여 |
| `policies/rds-snapshot-expired-delete.yml` | RDS snapshot | 30일 초과 수동 snapshot 삭제 |

## 검증

정책 문법이 모두 유효한지 확인한다.

```sh
custodian validate policies/*.yml
```

기대 결과:

- 정책 파일 9개 각각에 대해 `Configuration valid: policies/...` 출력
- 오류 시 비정상 종료 코드와 함께 스키마 위반 위치 출력

실행 결과로 어떤 리소스가 걸렸는지 확인한다.

```sh
custodian report --format grid --output-dir=out policies/ec2-offhours-stop.yml
```

기대 결과:

- 대상 instance의 `InstanceId`, `InstanceType`, `LaunchTime` 컬럼이 있는 표 출력
- 대상이 없으면 빈 표 출력

`mark-for-op`이 남긴 tag를 직접 확인한다.

```sh
aws ec2 describe-instances \
  --filters "Name=tag-key,Values=c7n-untagged-stop" \
  --query "Reservations[].Instances[].[InstanceId,Tags[?Key=='c7n-untagged-stop'].Value|[0]]" \
  --output table
```

기대 결과:

- tag 값이 `Resource does not meet policy: stop@2026/07/31` 형태로 출력 (op와 실행 예정일 포함)

<!-- akbun-writing: 검증 중 만난 예상 외 결과가 있으면 추가 -->

## 주의

- `rds-snapshot-expired-delete`와 `ebs-unattached-mark-delete`는 복구 불가능한 삭제를 포함한다. 먼저 `--dryrun`으로 대상을 확인한다.
- `offhour`/`onhour` filter는 정책이 실행되는 시각을 기준으로 판단한다. pull mode로 임의 시각에 돌리면 대상이 잡히지 않는다.
- RDS `stop`은 Multi-AZ, read replica, Aurora instance에서 동작하지 않는다. 중지된 RDS는 7일 후 AWS가 자동으로 다시 시작한다.
- `metrics` filter는 CloudWatch API를 호출하므로 리소스가 많으면 조회 비용과 시간이 늘어난다.

## 참고자료

- Cloud Custodian 공식 문서: https://cloudcustodian.io/docs/
- AWS resource 별 filter/action 레퍼런스: https://cloudcustodian.io/docs/aws/resources/index.html
- offhours 가이드: https://cloudcustodian.io/docs/aws/usage.html
- Cloud Custodian repo: https://github.com/cloud-custodian/cloud-custodian
