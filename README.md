# 나만의 용돈 기입장 (budget_app)

파일(JSONL)에 데이터를 영구 저장하는 **콘솔 가계부**입니다.
거래 추가/목록/검색/수정/삭제, 월별 요약, 예산 초과 경고, 카테고리 관리, CSV 가져오기/내보내기를 지원하고,
보너스 과제 4개(백업, 반복 내역, 표 정렬 출력, 원자적 저장)를 모두 구현했습니다.

- Python 3.10 이상, **표준 라이브러리만** 사용 (`pip install` 불필요)
- 저장 포맷: **JSONL** 고정 / `update`: **옵션 기반(안 A)** 고정 / 빈 카테고리: **기본 카테고리 자동 생성(안 A)** 고정

> 동료평가 문항(항목 1~5)별 답변과 코드 링크는 [docs/EVALUATION.md](docs/EVALUATION.md),
> 예상 질문·개념 정리·답변은 [docs/QNA.md](docs/QNA.md) 에 있습니다.

---

## 1. 실행 방법

프로젝트 폴더(이 README가 있는 곳)에서 실행합니다.

```bash
python -m budget_app <command> [options]
```

```bash
python -m budget_app --help
```

```bash
python -m budget_app add
```

- 모든 명령과 하위 명령은 `--help` 를 지원합니다. 예: `python -m budget_app search --help`
- 옵션 표기는 모두 `--` 로 통일했습니다.
- 공통 옵션 (명령 앞/뒤 어디에 써도 됩니다)

| 옵션 | 설명 |
| --- | --- |
| `--data-dir <폴더>` | 저장 폴더 변경 (기본 `./data`) |
| `--verbose` | 실행 로그와 소요 시간 출력 (데코레이터 `log_timed`) |

### 시연 스크립트 (동료평가용)

명령을 하나씩 입력하지 않고, 평가 항목 순서대로 전 기능을 자동으로 실행해 **명령 · 출력 · 종료 코드**를 보여 줍니다.

```bash
python demo.py
```

- 단계마다 Enter 로 진행합니다. 멈추지 않고 끝까지 보려면 `python demo.py --no-pause`
- Windows 에서는 `demo.bat` 을 더블클릭해도 됩니다. Mac/Linux 는 `python3 demo.py`
- 실제 데이터(`./data`)는 건드리지 않고 `./demo_data` 를 매번 새로 만들어 사용합니다.

### 테스트 실행

```bash
python -m unittest discover -s tests -v
```

전 기능을 임시 폴더에서 실제 CLI 진입점(`main`)으로 실행해 검증하는 21개 테스트입니다.
문서의 코드 링크가 현재 코드와 맞는지도 함께 검사합니다(아래 "문서 링크 갱신" 참고).

### 문서 링크 갱신 (코드를 수정했을 때)

`docs/` 의 코드 링크는 줄 번호(`#L62-L78`)로 이동합니다. GitHub 가 "함수로 가는 링크"를 지원하지 않기 때문입니다.
대신 각 링크에 **가리키는 함수/클래스 이름**을 적어 두었고, 아래 명령이 현재 코드에서 그 위치를 찾아 줄 번호를 다시 씁니다.

```bash
python tools/relink.py
```

- 코드를 고친 뒤 한 번 실행하면 됩니다. 실행하지 않으면 테스트(`test_docs_code_links_point_at_current_code`)가 실패해 알려 줍니다.
- 확인만 하려면 `python tools/relink.py --check`

---

## 2. 폴더 구조와 계층별 책임

```
budget_app/
├── __main__.py     진입점 (python -m budget_app)
├── cli.py          [CLI]   명령 해석(argparse), input() 대화형 입력, print() 출력
├── service.py      [서비스] 업무 규칙: 검증, 검색, 요약, 예산, import/export, 반복 내역
├── storage.py      [저장소] JSONL 파일 읽기(제너레이터)/쓰기(원자적 교체), 백업
├── models.py       [모델]   dataclass(Transaction, Budget, Recurring) + 입력 검증 함수
├── formatter.py    [출력]   표 정렬 문자열 생성 (한글 폭 계산)
├── decorators.py   [공통]   handle_errors, log_timed 데코레이터
└── errors.py       [공통]   AppError (원인 + 힌트)
tests/test_app.py   종단 테스트
tools/relink.py     문서의 코드 링크 줄 번호 자동 갱신
demo.py, demo.bat   동료평가 시연 스크립트
docs/QNA.md         예상 질문 / 개념 정리 / 답변
```

의존 방향은 한쪽으로만 흐릅니다: `cli → service → storage → models`.

| 계층 | 하는 일 | 하지 않는 일 |
| --- | --- | --- |
| CLI (`cli.py`) | 옵션 파싱, 재입력 루프, 결과 출력 | 파일 접근, 계산 |
| 서비스 (`service.py`) | "카테고리는 등록돼 있어야 한다" 같은 규칙, 집계 | `print`/`input`, 파일 열기 |
| 저장소 (`storage.py`) | 파일 한 줄 ↔ 객체 변환, 안전한 쓰기 | 업무 규칙 판단 |
| 모델 (`models.py`) | 데이터 모양 정의, 값 하나의 형식 검증 | 다른 계층 호출 |

클래스: `Transaction`, `Budget`, `Recurring`, `JsonlFile`, `TransactionRepository`, `CategoryStore`,
`BudgetStore`, `RecurringStore`, `BudgetService`, `SearchFilter`, `Summary`, `ImportResult`, `AppError`

---

## 3. 저장 파일 위치와 형식

기본 위치는 `./data` 이며 `--data-dir` 로 바꿀 수 있습니다. 모두 **UTF-8 JSONL**(한 줄 = JSON 객체 1개)입니다.

| 파일 | 내용 | 한 줄 예시 |
| --- | --- | --- |
| `transactions.jsonl` | 거래 내역 | `{"id": "TX-000001", "type": "expense", "date": "2024-01-15", "amount": 15000, "category": "food", "memo": "점심", "tags": ["meal"]}` |
| `categories.jsonl` | 카테고리 | `{"name": "food"}` |
| `budgets.jsonl` | 월 예산 | `{"month": "2024-01", "amount": 500000}` |
| `recurring.jsonl` | 반복 내역 규칙 (보너스) | `{"id": "RC-0001", "type": "expense", "day": 25, "amount": 500000, "category": "rent", "memo": "월세", "tags": []}` |
| `backups/<YYYYMMDD-HHMMSS>/` | `backup` 명령이 만든 복사본. `restore` 로 되돌림 (보너스) | |

### 초기 실행

저장 파일이 없으면 어떤 명령을 실행하든 **자동 생성**하고 안내 문구를 출력합니다.
카테고리 파일이 비어 있으면 기본 카테고리 `food, transport, rent, salary, etc` 를 만듭니다.

```
[안내] 기본 카테고리를 생성했습니다: food, transport, rent, salary, etc
[안내] 저장 파일을 생성했습니다: data (transactions.jsonl, budgets.jsonl, recurring.jsonl)
```

### Transaction 필드

| 필드 | 타입 | 규칙 |
| --- | --- | --- |
| `id` | str | 유일. `TX-000001` 형식, 남아 있는 가장 큰 번호 + 1 (중간 거래를 삭제해도 겹치지 않음) |
| `type` | str | `income` / `expense` |
| `date` | str | `YYYY-MM-DD`, 실제 존재하는 날짜 |
| `amount` | int | 양의 정수 |
| `category` | str | 등록된 카테고리 |
| `memo` | str | 선택 |
| `tags` | list[str] | 선택 |

---

## 4. 명령 사용법과 예시

아래 출력은 실제 실행 결과입니다.

### 4.1 add — 거래 추가 (대화형)

```
$ python -m budget_app add
날짜(YYYY-MM-DD): 2024-01-15
타입(income/expense): expense
카테고리(food, transport, rent, salary, etc): food
금액(양수): 15000
메모(선택): 점심
태그(쉼표로 구분, 없으면 엔터): meal
[저장 완료] id=TX-000001
```

잘못 입력하면 그 항목만 다시 묻습니다.

```
날짜(YYYY-MM-DD): 2024-13-40
[오류] 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).
[힌트] 예: 2024-01-15
날짜(YYYY-MM-DD):
```

### 4.2 list — 거래 목록 (최신순)

```
$ python -m budget_app list --limit 3
ID        | DATE       | TYPE    | CATEGORY |    AMOUNT | MEMO | TAGS
----------+------------+---------+----------+-----------+------+-----
TX-000003 | 2024-01-20 | expense | rent     |   150,000 | 월세 |
TX-000001 | 2024-01-15 | expense | food     |    15,000 | 점심 | meal
TX-000002 | 2024-01-14 | income  | salary   | 3,000,000 |      |
(3건)
```

- `--limit N` (기본 10). 정렬 기준은 날짜 내림차순, 같은 날짜면 id 내림차순입니다.

### 4.3 search — 조건 검색 (최신순)

| 옵션 | 의미 |
| --- | --- |
| `--from YYYY-MM-DD` / `--to YYYY-MM-DD` | 기간 (양 끝 포함) |
| `--category <이름>` | 카테고리 일치 |
| `--type income\|expense` | 타입 일치 |
| `--q <키워드>` | 메모에 포함 (대소문자 무시) |
| `--tag <태그>` | 태그 정확히 일치 |
| `--limit N` | 최대 건수 (기본 전체) |

조건을 여러 개 주면 모두 만족하는(AND) 거래만 나옵니다.

```bash
python -m budget_app search --from 2024-01-01 --to 2024-01-31 --type expense
```

```bash
python -m budget_app search --category food --tag meal
```

```bash
python -m budget_app search --q 점심
```

### 4.4 summary — 월별 요약

```
$ python -m budget_app summary --month 2024-01 --top 3
[2024-01 요약] 거래 3건
총 수입: 3000000원
총 지출: 165000원
잔액: 2835000원
예산: 100000원 (사용률 165.0%)
[경고] 예산을 65000원 초과했습니다!

지출 TOP 3
1) rent 150000원
2) food 15000원
```

- `--top N` (기본 3). 거래가 없는 달은 `[데이터 없음] 2030-01 에 해당하는 거래가 없습니다.` 를 출력합니다.
- 예산이 없으면 `예산: 미설정` 으로 안내합니다.

### 4.5 budget — 예산 설정/조회

```
$ python -m budget_app budget set --month 2024-01 --amount 500000
[저장 완료] 2024-01 예산 500000원
```

```bash
python -m budget_app budget show
```

같은 달에 다시 `set` 하면 덮어씁니다(한 달에 한 줄).

### 4.6 category — 카테고리 관리

```
$ python -m budget_app category add
카테고리명: hobby
[저장 완료] category=hobby

$ python -m budget_app category list
- food
- transport
- rent
- salary
- etc
- hobby
```

- `category add --name hobby` 처럼 옵션으로도 줄 수 있습니다. 이름은 소문자로 통일해 저장합니다.
- **사용 중인 카테고리 삭제**: 그냥 삭제는 막고, 대체 카테고리를 주면 거래를 옮긴 뒤 삭제합니다.

```
$ python -m budget_app category remove --name food
[오류] 'food' 카테고리는 거래 2건, 반복 내역 0건에서 사용 중이라 삭제할 수 없습니다.
[힌트] 대체 카테고리를 지정하세요: category remove --name food --replace-with <카테고리>

$ python -m budget_app category remove --name food --replace-with etc
[삭제 완료] category=food (거래 2건을 etc 로 이동)
```

### 4.7 update — 거래 수정 (옵션 기반으로 고정)

```
update --id <id> [--date ...] [--type ...] [--category ...] [--amount ...] [--memo ...] [--tags ...]
```

지정한 필드만 바뀌고 나머지는 유지됩니다. 태그를 비우려면 `--tags ""`.

```
$ python -m budget_app update --id TX-000001 --amount 18000
[수정 완료] id=TX-000001
ID        | DATE       | TYPE    | CATEGORY | AMOUNT | MEMO | TAGS
----------+------------+---------+----------+--------+------+-----
TX-000001 | 2024-01-15 | expense | food     | 18,000 | 점심 | meal
```

### 4.8 delete — 거래 삭제

```
$ python -m budget_app delete --id TX-000099
[오류] 없는 데이터입니다: id=TX-000099
[힌트] list 또는 search 로 id 를 확인하세요.
```

### 4.9 import / export — CSV

```
$ python -m budget_app export --out export.csv --month 2024-01
[완료] export.csv (3 records)

$ python -m budget_app import --from export.csv
[완료] imported=3, skipped=0
```

- `export` 는 `--month YYYY-MM` 또는 `--from/--to` 중 **하나 이상 필수**입니다(없으면 오류). 날짜 오름차순으로 씁니다.
- `import` 는 잘못된 행을 건너뛰고 사유를 행 번호와 함께 출력합니다. 올바른 행은 그대로 등록합니다.

```
[완료] imported=2, skipped=3
  - 건너뜀 3행: 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).
  - 건너뜀 4행: 등록되지 않은 카테고리입니다: 'nope'
  - 건너뜀 5행: 금액은 0보다 큰 양수여야 합니다.
```

#### CSV 스키마 (import/export 공통, 고정)

| column | required | 설명 |
| --- | --- | --- |
| `date` | Y | YYYY-MM-DD |
| `type` | Y | income / expense |
| `category` | Y | 등록된 카테고리 |
| `amount` | Y | 양수 정수 |
| `memo` | N | 문자열 |
| `tags` | N | 쉼표(,) 구분 문자열 |

- UTF-8, 첫 줄은 헤더 `date,type,category,amount,memo,tags`
- 태그가 여러 개면 쉼표가 들어가므로 CSV 규칙대로 따옴표로 감쌉니다: `2024-01-15,expense,food,15000,점심,"meal,daily"`
- `import` 는 엑셀이 붙이는 BOM이 있어도 읽습니다. `id` 는 CSV에 없고 가져올 때 새로 부여합니다.

### 4.10 보너스 명령

```bash
python -m budget_app backup
```

`data/backups/20261005-150231/` 처럼 타임스탬프 폴더에 모든 `.jsonl` 을 복사합니다.

```
$ python -m budget_app restore
[복원 완료] 20261005-174705 (4 files)
[안내] 복원 직전 상태는 20261005-174705-2 으로 백업했습니다. (되돌리려면 restore --name 20261005-174705-2)
```

- `restore`: 가장 최근 백업으로 되돌립니다. `restore --name <이름>` 으로 특정 백업을, `restore --list` 로 목록을 봅니다.
- 되돌리기 **전에 현재 상태를 자동으로 백업**하므로, 복원 자체도 취소할 수 있습니다.

**추가 도중 중단된 경우**: `add` 중 꺼져서 마지막 줄이 잘렸으면, 다음 실행 때 그 줄만 떼어 내고 무엇이 빠졌는지 보여 줍니다.

```
[안내] transactions.jsonl 의 마지막 줄이 저장 도중 끊겨 있어 떼어 냈습니다: '{"id": "TX-000099", "type": "expen'. 다른 데이터는 그대로입니다. 마지막에 추가하던 내역은 저장되지 않았으니 다시 입력하세요.
```

**수정 도중 중단된 경우**: 수정/삭제 중 프로그램이 꺼지면 임시 파일만 남고 원본은 수정 전 그대로입니다. 다음 실행 때 한 번 안내합니다.

```
[안내] 이전 수정 작업이 중단되어 반영되지 않았습니다 (transactions.jsonl). 데이터는 수정 전 상태 그대로입니다. 필요하면 마지막 명령을 다시 실행하세요.
```

```bash
python -m budget_app recurring add
```

```bash
python -m budget_app recurring apply --month 2024-02
```

- `recurring add`(대화형): 매월 며칠, 타입, 카테고리, 금액, 메모, 태그를 등록합니다. `recurring list`, `recurring remove --id RC-0001`.
- `recurring apply --month`: 등록된 규칙을 그 달의 거래로 생성합니다.
  - 생성된 거래에 `recurring:RC-0001` 태그를 붙여, 같은 달에 다시 실행해도 **중복 생성하지 않습니다**.
  - 31일 규칙은 2월처럼 31일이 없는 달에 **말일로 보정**합니다.

---

## 5. 과제 요구사항 대응표

| # | 요구사항 | 구현 위치 |
| --- | --- | --- |
| 1 | `python -m budget_app`, 전 명령 `--help`, `--` 옵션 | `__main__.py`, `cli.py: build_parser` |
| 2 | dataclass 모델, 클래스 2개 이상, 입력 검증 | `models.py` |
| 3 | JSONL 3개 이상 파일, `--data-dir`, 초기 자동 생성 | `storage.py`, `service.py: initialize` |
| 4 | add 대화형 + 재입력 + id 출력 | `cli.py: cmd_add, ask` |
| 5 | list 최신순, `--limit`, 스트리밍 | `service.py: recent` (`heapq.nlargest`) |
| 6 | update(옵션 기반)/delete, 없는 id 처리, 안전한 재작성 | `service.py`, `storage.py: rewrite_each, JsonlFile.rewrite` |
| 7 | search 조건 6종, 최신순, 스트리밍 | `service.py: SearchFilter, iter_filtered, search` |
| 8 | summary 수입/지출/잔액/TOP N, 데이터 없음 | `service.py: summarize`, `cli.py: cmd_summary` |
| 9 | budget set, 사용률/초과 경고 | `service.py: set_budget, Summary` |
| 10 | category add/list/remove, 사용 중 처리 | `service.py: remove_category` |
| 11 | import/export CSV, 기간 조건 필수 | `service.py: import_csv, export_csv` |
| 12 | 데코레이터 1개 이상 실제 적용 | `decorators.py: handle_errors, log_timed` |
| 13 | 스택트레이스 금지, 종료 코드 | `decorators.py: handle_errors` |
| 14 | 모듈 3개 이상 분리 | 8개 모듈 |
| 보너스 | 백업 / 반복 내역 / 표 정렬 / 원자적 저장 | `storage.py: backup_data` / `service.py: apply_recurring` / `formatter.py` / `JsonlFile.rewrite` |

---

## 6. 핵심 설계

### 6.1 제너레이터 스트리밍

`JsonlFile.iter_records()` 는 파일을 한 줄씩 읽어 `yield` 합니다. 파일이 아무리 커도 한 번에 한 줄만 메모리에 있습니다.

```python
def iter_records(self) -> Iterator[dict[str, Any]]:
    with self.path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            ...
            yield record
```

이 위에 제너레이터를 겹쳐 씁니다: `iter_records`(줄 → dict) → `iter_all`(dict → Transaction) → `iter_filtered`(조건 통과분만).

- **list**: `heapq.nlargest(limit, 제너레이터, key=날짜)` 로 흘려보내며 상위 N건만 유지합니다. 메모리는 N건 분량입니다.
- **summary**: 흘려보내며 합계만 누적합니다. 메모리는 카테고리 수만큼입니다.
- **update/delete**: 읽는 제너레이터를 그대로 쓰기에 연결해 한 줄씩 옮겨 씁니다.

### 6.2 원자적 저장 (임시 파일 + rename)

수정/삭제는 원본을 직접 고치지 않습니다. `transactions.jsonl.tmp` 에 전부 쓴 뒤 `os.replace()` 로 한 번에 교체합니다.
쓰는 도중 프로그램이 죽어도 원본은 그대로이고, 교체는 "완전히 옛 파일" 아니면 "완전히 새 파일" 둘 중 하나입니다.
검증(없는 id, 잘못된 값)은 파일을 건드리기 **전에** 끝내므로, 실패한 명령은 데이터를 바꾸지 않습니다.

### 6.3 데코레이터

| 데코레이터 | 적용 위치 | 역할 |
| --- | --- | --- |
| `@handle_errors` | `cli.main` | 모든 예외를 `[오류] 원인` / `[힌트] 해결 방법` 으로 출력하고 종료 코드로 변환 |
| `@log_timed` | 서비스의 주요 메서드 | 시작/종료와 소요 시간(ms) 로그. `--verbose` 일 때 표시 |

```
$ python -m budget_app search --q 점심 --verbose
[로그] 시작: search
[로그] 종료: search (2.41 ms)
```

### 6.4 오류 처리와 종료 코드

| 코드 | 상황 |
| --- | --- |
| 0 | 정상 |
| 1 | 입력/데이터 오류 (`AppError`: 없는 id, 잘못된 값, 손상된 파일 등) |
| 2 | 파일 시스템 오류(권한/경로) 또는 잘못된 명령·옵션(argparse) |
| 3 | 예상하지 못한 오류 |
| 130 | 입력 중단 (Ctrl+C, 입력 종료) |

오류 메시지는 표준 오류(stderr)로 나가며 스택트레이스는 출력하지 않습니다.

### 6.5 타입 힌트

모든 함수에 인자/반환 타입을 적었습니다. 예를 들어 `get(self, tx_id: str) -> Transaction | None` 은
"없을 수 있다"는 사실을 시그니처로 알려 주므로, 호출하는 쪽이 `None` 처리를 빠뜨리지 않게 됩니다.

---

## 7. 알려진 한계

- `search` 를 `--limit` 없이 쓰면 최신순 정렬을 위해 **조건에 맞는 결과**를 메모리에 올립니다(파일 전체는 아님). `export` 도 같습니다.
- 여러 터미널에서 동시에 쓰는 상황을 위한 파일 잠금은 없습니다(1인용 도구 가정).
- 수정/삭제 도중 프로그램이 중단되면 **진행 중이던 그 수정은 반영되지 않습니다.** 기존 데이터는 그대로이고, 다음 실행 때 안내가 나옵니다. 자동으로 이어서 실행하지는 않습니다.
- `add`·`import` 는 파일 끝에 한 줄씩 붙이는 방식이라, 쓰는 도중 중단되면 마지막 줄이 잘릴 수 있습니다. 다음 실행 때 **잘린 마지막 줄만 떼어 내고 안내**하며 다른 데이터는 그대로입니다. 추가하던 그 한 건은 다시 입력해야 합니다.
- 파일 **중간**의 줄이 깨진 경우(직접 편집 실수 등)는 원인을 알 수 없으므로 자동으로 고치지 않고 오류로 멈춥니다. 해당 줄을 고치거나 `restore` 로 되돌립니다.
- `import` 는 행마다 디스크 확정(`fsync`)을 하므로 수천 행 이상에서는 느려집니다.
- `add` 등 대화형 입력을 파이프로 넣을 때, 터미널 입력 인코딩이 UTF-8이 아니면 한글 메모가 깨질 수 있습니다. 키보드 입력은 문제없습니다.
