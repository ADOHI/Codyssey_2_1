# 동료평가 대비: 개념 정리 · 예상 질문 · 답변

> 평가지 문항(항목 1~5)별 답변은 [EVALUATION.md](EVALUATION.md) 에 따로 정리했습니다. 각 답변 아래 `코드:` 링크는 해당 줄로 바로 이동합니다.

읽는 순서: **0부 용어 사전**에서 모르는 단어를 확인하고 → **1부 개념 정리**로 원리를 잡고 → **1.5부 설계 선택 비교**로 "왜"를 익힌 뒤 → **2부 예상 질문**을 소리 내어 답해 보고 → **3부 시연 순서**대로 직접 실행해 보세요.

---

# 0부. 용어 사전 (기초 지식이 없어도 읽을 수 있게)

문서와 코드에 나오는 용어를 **쉬운 말 → 이 프로젝트에서의 예** 순서로 풀었습니다. 모르는 단어가 나오면 여기로 돌아오세요.

<a id="g-run"></a>
## 0-1. 실행 환경

| 용어 | 쉬운 설명 | 이 프로젝트에서 |
| --- | --- | --- |
| 터미널 (콘솔) | 글자로 명령을 입력하고 글자로 결과를 받는 창. Windows의 PowerShell, Mac의 터미널 | 이 프로그램은 창·버튼 없이 터미널에서만 동작 |
| CLI | Command Line Interface. 터미널에서 명령어로 쓰는 프로그램 방식 (반대: 마우스로 쓰는 GUI) | `python -m budget_app list` |
| 명령 (command) | 프로그램에게 시키는 일의 이름 | `add`, `list`, `search` |
| 하위 명령 | 명령 안의 세부 명령 | `category add`, `budget set` |
| 옵션 | 명령의 세부 조건. `--이름 값` 형태 | `--limit 3`, `--month 2024-01` |
| 인자 (argument) | 명령 뒤에 붙여 넘기는 값 전체 | `list --limit 3` 에서 `--limit 3` |
| 대화형 입력 | 프로그램이 질문하고 사용자가 답하는 방식 | `add` 가 날짜, 타입… 을 차례로 물어봄 |
| `python -m 이름` | "이 이름의 패키지를 프로그램으로 실행해라" | `budget_app/__main__.py` 가 실행됨 |
| 표준 라이브러리 | 파이썬을 설치하면 **기본으로 들어 있는** 도구 모음. 따로 설치할 필요 없음 | `json`, `csv`, `argparse`, `heapq` 등. 이 과제는 이것만 허용 |
| 외부 라이브러리 | `pip install` 로 따로 설치해야 하는 도구 | 사용 금지 → 하나도 쓰지 않음 |
| 종료 코드 | 프로그램이 끝나면서 운영체제에 남기는 숫자. **0 = 성공, 0이 아니면 실패** | 없는 id 삭제 → 1 |
| stdout / stderr | 프로그램의 출력 통로 두 개. stdout은 정상 결과용, stderr는 오류용 | `[오류]`, `[힌트]` 는 stderr로 나감 |
| 파이프 | 한 프로그램의 출력을 다른 프로그램의 입력으로 연결하는 것 (`\|`) | 테스트·자동화에서 입력을 대신 넣을 때 |

<a id="g-code"></a>
## 0-2. 코드 구조

| 용어 | 쉬운 설명 | 이 프로젝트에서 |
| --- | --- | --- |
| 모듈 | `.py` 파일 하나 | `cli.py`, `service.py` 등 8개 |
| 패키지 | 모듈을 모아 둔 폴더 | `budget_app/` |
| import | 다른 모듈의 기능을 가져와 쓰는 것 | `from .models import Transaction` |
| 함수 | 이름을 붙인 코드 묶음. 값을 받아 일을 하고 결과를 돌려줌 | `parse_date("2024-01-15")` |
| 클래스 | 관련된 데이터와 함수를 하나로 묶은 **설계도** | `Transaction`, `BudgetService` |
| 객체 (인스턴스) | 설계도로 실제로 만든 것 | 거래 한 건 = `Transaction` 객체 하나 |
| 메서드 | 클래스 안에 들어 있는 함수 | `svc.summarize("2024-01")` |
| 속성 (필드) | 객체가 가진 값 | `tx.amount`, `tx.date` |
| `self` | 메서드 안에서 "나 자신(이 객체)"을 가리키는 이름 | `self.path` |
| dataclass | 데이터를 담는 클래스를 짧게 만드는 문법 | `@dataclass class Transaction` |
| 계층 (layer) | 역할별로 나눈 코드의 층. 위층이 아래층만 부름 | CLI → 서비스 → 저장소 → 모델 |
| 모델 | 데이터의 모양을 정의한 것 | 거래는 id, type, date, amount… 를 가진다 |
| 저장소 (Repository/Store) | 파일을 읽고 쓰는 일만 맡은 부분 | `TransactionRepository` |
| 서비스 | 규칙과 계산을 맡은 부분 | "카테고리는 등록돼 있어야 한다" |
| 책임 | 그 코드가 **맡은 일의 범위** | 저장소의 책임 = 파일 I/O |
| 관심사 분리 | 서로 다른 일을 서로 다른 곳에 두는 원칙 | 출력은 CLI에만, 파일은 저장소에만 |
| 포함 (composition) | 클래스가 다른 클래스의 객체를 **가지고** 쓰는 것 | 저장소가 `JsonlFile` 을 가짐 |
| 상속 | 클래스가 다른 클래스의 기능을 **물려받는** 것 | `AppError(Exception)` 한 곳만 사용 |

<a id="g-data"></a>
## 0-3. 데이터와 파일

| 용어 | 쉬운 설명 | 이 프로젝트에서 |
| --- | --- | --- |
| 영구 저장 | 프로그램을 꺼도 남는 저장 (↔ 변수는 끄면 사라짐) | `data/` 폴더의 파일 |
| 파일 I/O | 파일 읽기(Input)/쓰기(Output) | `storage.py` |
| JSON | `{"이름": 값}` 형태로 데이터를 적는 약속. 숫자·문자·목록을 구분 | `{"amount": 15000, "tags": ["meal"]}` |
| JSONL | JSON Lines. **한 줄에 JSON 하나씩** 적은 파일 | `transactions.jsonl` |
| CSV | 쉼표로 칸을 나눈 표 형식 텍스트. 엑셀로 열림 | import/export 파일 |
| 헤더 | CSV의 첫 줄. 각 칸의 이름 | `date,type,category,amount,memo,tags` |
| 스키마 | 데이터가 어떤 칸(필드)으로 이루어지는지 정한 규칙 | CSV 6개 컬럼 |
| 인코딩 | 글자를 컴퓨터가 저장하는 숫자로 바꾸는 규칙 | 모든 파일을 UTF-8로 |
| UTF-8 | 한글 포함 전 세계 글자를 다루는 표준 인코딩 | `encoding="utf-8"` |
| BOM | 파일 맨 앞에 붙는 보이지 않는 표식. 엑셀이 붙이곤 함 | `utf-8-sig` 로 읽어 무시 |
| append (추가) | 파일 **끝에** 덧붙여 쓰기. 기존 내용은 그대로 | 거래 추가 |
| 재작성 (rewrite) | 파일 전체를 새로 쓰기 | 수정·삭제 |
| 임시 파일 | 작업 중에만 쓰는 파일 | `transactions.jsonl.tmp` |
| 원자적 (atomic) | **전부 되거나 전혀 안 되거나.** 중간 상태가 없음 | 임시 파일을 다 쓴 뒤 한 번에 교체 |
| `os.replace` | 파일 이름을 바꿔 다른 파일을 대체. 운영체제가 한 동작으로 처리 | `.tmp` → 원본 교체 |
| flush / fsync | 메모리에 대기 중인 내용을 실제 디스크에 쓰라고 재촉하는 것 | 교체 직전에 호출 |
| CRUD | Create(생성)·Read(조회)·Update(수정)·Delete(삭제) | add / list·search / update / delete |
| 검증 (validation) | 들어온 값이 규칙에 맞는지 확인 | 날짜 형식, 양수 금액 |
| id (식별자) | 각 데이터를 구분하는 유일한 이름 | `TX-000001` |

<a id="g-python"></a>
## 0-4. 이 과제의 핵심 파이썬 개념

| 용어 | 쉬운 설명 | 이 프로젝트에서 |
| --- | --- | --- |
| 리스트 | 여러 값을 순서대로 **전부 메모리에** 담은 것 | `tags: ["meal", "daily"]` |
| 이터레이터 | 값을 **하나씩 꺼낼 수 있는** 것. `for` 로 돌릴 수 있음 | 파일 객체, 제너레이터 |
| 제너레이터 | 값을 한꺼번에 만들지 않고 **달라고 할 때마다 하나씩** 만들어 주는 함수 | `iter_records` |
| `yield` | "값 하나 내주고 여기서 잠깐 멈춤" | `yield record` |
| `return` | "결과를 내주고 함수 끝" | 일반 함수 |
| 지연 평가 (lazy) | 필요해질 때까지 계산을 미루는 것 | 제너레이터는 `for` 를 돌기 전엔 파일을 열지도 않음 |
| 스트리밍 | 데이터를 통째로 올리지 않고 **흘려보내며** 처리 | 파일을 한 줄씩 읽어 처리 |
| 메모리 | 프로그램이 일하는 동안 데이터를 올려 두는 작업 공간. 한정돼 있음 | 스트리밍은 한 줄 분량만 사용 |
| 데코레이터 | 함수에 **포장지를 씌워** 기능을 덧붙이는 것. `@이름` | `@handle_errors` |
| 래퍼 (wrapper) | 포장지 역할을 하는 안쪽 함수 | `decorators.py` 의 `wrapper` |
| 공통 관심사 | 여러 함수에 똑같이 필요한 부가 기능 | 예외 처리, 로그, 시간 측정 |
| 타입 | 값의 종류. `str`(문자열), `int`(정수), `list`, `bool`(참/거짓) | `amount: int` |
| 타입 힌트 | 함수가 **무엇을 받고 무엇을 돌려주는지** 적어 둔 표시 | `-> Transaction \| None` |
| `None` | "값이 없음"을 뜻하는 특별한 값 | 없는 id를 찾으면 `None` |
| `X \| None` | X이거나 없을 수 있음 | `get()` 의 반환 타입 |
| 예외 (exception) | 실행 중 생긴 문제를 알리는 신호. 처리하지 않으면 프로그램이 멈춤 | `AppError` |
| `try / except` | "해 보고, 문제가 생기면 이렇게 처리" | `handle_errors` 안 |
| `raise` | 예외를 일부러 발생시킴 | `raise AppError("없는 데이터입니다")` |
| 스택트레이스 | 오류 때 나오는 긴 영어 줄들(어느 파일 몇 번째 줄…). 개발자용 | 사용자에게는 보여 주지 않음 |
| 로그 | 프로그램이 무엇을 했는지 남기는 기록 | `--verbose` 때 `[로그] 시작: search` |
| 힙 (heap) | "가장 큰/작은 값"을 빠르게 유지하는 자료구조 | `heapq.nlargest` 로 최신 N건 |
| 람다 (lambda) | 이름 없는 한 줄짜리 함수 | `lambda t: None if t.id == tx_id else t` |

<a id="g-quality"></a>
## 0-5. 품질과 성능

| 용어 | 쉬운 설명 | 이 프로젝트에서 |
| --- | --- | --- |
| 테스트 | 코드가 기대대로 동작하는지 **코드로** 확인하는 것 | `tests/test_app.py` 21개 |
| 종단(E2E) 테스트 | 사용자가 쓰는 것처럼 처음부터 끝까지 실행해 보는 테스트 | 실제 `main()` 을 명령 인자로 실행 |
| 병목 | 전체를 느리게 만드는 **가장 느린 부분** | 10만 건일 때 파일 전체 읽기 |
| 프로파일링 | 어느 코드가 시간을 얼마나 쓰는지 재는 것 | 날짜 검증이 읽기 시간의 절반 이상 |
| 인덱스 | 책의 색인처럼, 원하는 데이터를 바로 찾게 해 주는 목록 | 현재 없음 (개선안) |
| 데이터베이스 | 데이터를 저장·검색하는 전용 프로그램 | 쓰지 않음. 개선안으로 SQLite 언급 |
| 롤백 | 작업을 취소하고 **이전 상태로 되돌리기** | import의 대안 방식으로 비교 |
| 부분 성공 | 되는 것만 처리하고 안 되는 것은 건너뛰기 | import가 택한 방식 |
| 멱등 | 여러 번 실행해도 결과가 같음 | `recurring apply` 를 두 번 해도 중복 없음 |
| 유지보수 | 완성 후에 고치고 기능을 더하는 일 | 계층을 나눈 목적 |

---

# 1부. 개념 정리

## 1. 파일 기반 영구 저장과 JSONL

- **영구 저장**: 변수는 프로그램이 끝나면 사라진다. 파일에 써 두면 다음 실행 때 다시 읽을 수 있다.
- **JSONL**(JSON Lines): 한 줄에 JSON 객체 하나.

```
{"id": "TX-000001", "type": "expense", "date": "2024-01-15", "amount": 15000, ...}
{"id": "TX-000002", "type": "income", "date": "2024-01-14", "amount": 3000000, ...}
```

- 일반 JSON 파일(`[ {...}, {...} ]`)은 전체를 읽어야 해석할 수 있지만, JSONL은 **한 줄만 읽어도** 한 건을 해석할 수 있다. 그래서 스트리밍과 잘 맞고, 추가는 파일 끝에 한 줄 붙이기(append)만 하면 된다.
- CSV 대비 장점: `tags` 같은 리스트와 숫자 타입이 그대로 보존된다.

## 2. CRUD

Create(add) / Read(list, search, summary) / Update(update) / Delete(delete). 데이터를 다루는 프로그램의 기본 4동작이다.

## 3. dataclass

`@dataclass` 를 붙이면 `__init__`, `__repr__`, `__eq__` 를 자동으로 만들어 준다.

```python
@dataclass
class Transaction:
    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str = ""
    tags: list[str] = field(default_factory=list)
```

- `field(default_factory=list)`: 기본값으로 `[]` 를 직접 쓰면 모든 객체가 **같은 리스트를 공유**하는 버그가 생긴다. 객체마다 새 리스트를 만들라는 뜻이다.
- `asdict(tx)`: 객체 → dict (저장할 때), `replace(tx, amount=100)`: 일부만 바꾼 **새 객체** 생성 (update에서 사용).
- `__eq__` 가 자동 생성되므로 `new != tx` 로 "값이 바뀌었는지" 비교할 수 있다.

## 4. 제너레이터와 yield

- 일반 함수는 `return` 으로 결과를 **한꺼번에** 돌려주고 끝난다.
- 제너레이터 함수는 `yield` 로 값을 **하나 주고 멈췄다가**, 다음 값을 요청받으면 이어서 실행한다.

```python
def iter_records(self):
    with self.path.open("r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)   # 한 줄 주고 멈춤
```

- **지연 평가(lazy)**: 호출만으로는 아무것도 읽지 않는다. `for` 로 꺼낼 때 한 줄씩 읽는다.
- **메모리**: 100만 줄이어도 메모리에는 지금 처리 중인 한 줄만 있다. `readlines()` 나 리스트는 100만 줄을 전부 올린다.
- **한 번만 순회 가능**: 다 꺼내면 끝이다. 다시 쓰려면 함수를 다시 호출한다.
- **파이프라인**: 제너레이터를 겹쳐 쓴다. `줄 → dict → Transaction → 조건 통과분`.
- 제너레이터 표현식: `(tx for tx in self.iter_all() if flt.matches(tx))` — 괄호를 쓰면 리스트가 아니라 제너레이터다.

## 5. 데코레이터

함수를 받아서 **기능을 덧붙인 새 함수**를 돌려주는 함수. `@이름` 은 `func = 이름(func)` 의 줄임 표기다.

```python
def handle_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AppError as exc:
            print(f"[오류] {exc.message}", file=sys.stderr)
            return 1
    return wrapper
```

- **공통 관심사**: 예외 처리, 로그, 시간 측정처럼 여러 함수에 똑같이 필요한 코드. 각 함수 안에 복사하지 않고 한 곳에 둔다.
- `functools.wraps`: 감싼 뒤에도 원래 함수의 이름(`__name__`)과 설명이 유지되게 한다. 없으면 로그에 전부 `wrapper` 로 찍힌다.
- `*args, **kwargs`: 어떤 인자를 받는 함수든 감쌀 수 있게 그대로 전달한다.

## 6. 타입 힌트

`def get(self, tx_id: str) -> Transaction | None:` 처럼 인자와 반환값의 타입을 적는 것.

- 실행 중에 검사하지는 않는다(틀려도 그냥 실행된다). 사람·에디터·검사 도구(mypy 등)를 위한 **계약서**다.
- `X | None`: 없을 수 있음 / `list[str]`: 문자열 리스트 / `Iterator[Transaction]`: 하나씩 꺼내는 흐름 / `Callable[[str], T]`: 문자열을 받아 T를 돌려주는 함수.

## 7. 계층 구조 (관심사 분리)

`CLI → 서비스 → 저장소 → 모델` 한 방향으로만 호출한다.

- 화면을 바꿔도(예: 출력 문구) 계산 코드는 그대로, 저장 방식을 바꿔도(예: JSONL → CSV) 규칙 코드는 그대로다.
- 서비스에 `print`/`input` 이 없어서 테스트에서 값을 넣고 결과만 확인할 수 있다.

## 8. 원자적 쓰기

"전부 되거나, 전혀 안 되거나". 임시 파일에 다 쓴 뒤 `os.replace(tmp, 원본)` 으로 교체한다.
원본을 직접 덮어쓰다가 중간에 꺼지면 반쯤 쓰인 파일이 남지만, 이 방식은 교체 순간 전까지 원본이 온전하다.

## 9. argparse, 종료 코드, stderr

- `argparse`: 표준 라이브러리의 명령줄 해석기. 옵션 정의만 하면 `--help` 를 자동으로 만들어 준다. `add_subparsers` 로 `add`, `list` 같은 하위 명령을 만든다.
- **종료 코드**: 프로그램이 끝나며 운영체제에 남기는 숫자. 0은 성공, 0이 아니면 실패. 다른 프로그램/스크립트가 성공 여부를 판단하는 데 쓴다.
- **stderr**: 오류 전용 출력 통로. 정상 결과(stdout)와 섞이지 않아, 결과를 파일로 저장해도 오류 문구가 끼어들지 않는다.

---

# 1.5부. 설계 선택 비교 — "왜 이것을 골랐나"

평가에서 가장 자주 나오는 질문은 **"왜 그렇게 했나요? 다른 방법은요?"** 입니다.
선택마다 ① 후보 ② 장단점 ③ 고른 것과 이유를 정리했습니다. **굵은 글씨**가 실제로 고른 방식입니다.

<a id="c-format"></a>
### 선택 1. 저장 포맷

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| **JSONL** | 리스트(`tags`)·숫자 타입 보존, 한 줄 = 한 건이라 스트리밍과 맞음, 추가는 끝에 한 줄 | 줄마다 키 이름이 반복돼 파일이 큼, 엑셀로 바로 못 엶 |
| CSV | 파일이 작음, 엑셀로 바로 열림 | 전부 문자열(숫자 변환 필요), 리스트를 문자열로 바꿔야 함, 값 안의 쉼표·줄바꿈 처리 필요 |
| JSON 파일 하나 (`[ {...}, {...} ]`) | 구조가 단순 | **전체를 읽어야 해석 가능** → 스트리밍 불가, 한 건 추가에도 전체 재작성 (과제 허용 포맷도 아님) |
| 데이터베이스(SQLite) | 빠른 검색, 안전한 수정 | 과제가 JSONL/CSV 중 선택을 요구 |

**이유**: 거래에 `tags` 리스트와 숫자 `amount` 가 있어 타입이 보존되는 쪽이 코드가 단순합니다. 그리고 과제의 핵심인 "제너레이터 스트리밍"에 한 줄 = 한 건 구조가 정확히 맞습니다. 엑셀이 필요할 때는 `export` 로 CSV를 뽑으면 됩니다.

> 코드: [`iter_records`](../budget_app/storage.py#L83-L103 "sym:JsonlFile.iter_records") · [`append`](../budget_app/storage.py#L105-L112 "sym:JsonlFile.append")

<a id="c-update"></a>
### 선택 2. update 방식

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| **옵션 기반** (`update --id X --amount 100`) | 한 줄로 끝남, 바꿀 것만 적으면 됨, 자동화·테스트가 쉬움 | 옵션 이름을 알아야 함 (`--help` 로 해결) |
| 대화형 (필드마다 질문) | 처음 쓰는 사람에게 친절 | 금액 하나 바꾸려 해도 질문을 여러 번 거침, 자동 테스트가 번거로움 |

**이유**: 수정은 보통 "한두 필드만" 바꿉니다. 옵션 방식이 그 상황에 가장 짧고, 지정하지 않은 필드는 그대로 둔다는 규칙이 명확합니다.

> 코드: [`update_transaction`](../budget_app/service.py#L208-L237 "sym:BudgetService.update_transaction")

<a id="c-category-init"></a>
### 선택 3. 카테고리가 비어 있을 때

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| **기본 카테고리 자동 생성** (food, transport, rent, salary, etc) | 설치 직후 바로 `add` 가능 | 원치 않는 카테고리가 생길 수 있음 (삭제 가능) |
| `category add` 를 먼저 하도록 막기 | 사용자가 직접 정한 카테고리만 존재 | 첫 실행에서 바로 막혀 불편 |

**이유**: 처음 실행한 사람이 한 번에 거래를 추가할 수 있어야 합니다. 필요 없는 카테고리는 `category remove` 로 지울 수 있어 단점이 작습니다.

> 코드: [`CategoryStore.ensure`](../budget_app/storage.py#L188-L194 "sym:CategoryStore.ensure")

<a id="c-category-remove"></a>
### 선택 4. 사용 중인 카테고리 삭제

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| 그냥 삭제 | 구현이 쉬움 | **거래가 존재하지 않는 카테고리를 가리킴** → 데이터가 어긋남 |
| 삭제 막기 | 데이터가 항상 일관됨 | 정말 지우고 싶을 때 방법이 없음 |
| 대체 카테고리 요구 | 지우면서도 일관성 유지 | 옵션을 하나 더 알아야 함 |
| **기본은 막고, `--replace-with` 를 주면 옮긴 뒤 삭제** | 실수는 막고, 의도한 삭제는 가능 | (없음에 가까움) |

**이유**: "실수로 지워서 데이터가 깨지는 일"은 막되, 정리하고 싶은 사용자에게는 길을 열어 둡니다. 오류 메시지에 해결 명령을 그대로 적어 줍니다.

> 코드: [`remove_category`](../budget_app/service.py#L156-L183 "sym:BudgetService.remove_category")

<a id="c-rewrite"></a>
### 선택 5. 수정/삭제 시 파일을 고치는 방법

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| 파일의 그 줄만 제자리에서 고치기 | 길이가 같으면 그 위치만 덮어써서 빠름 | 길이가 달라지면 **뒤 내용을 전부 옮겨야 해서 O(n)**, 쓰는 도중 꺼지면 반쯤 바뀐 줄이 남음(원자적이지 않음), 줄 위치를 찾는 것부터 O(n) |
| 원본을 열어 처음부터 덮어쓰기 | 구현이 쉬움 | 쓰다가 꺼지면 **반쯤 쓰인 파일**이 남아 데이터 손실 |
| 전부 메모리에 읽고 → 고치고 → 다시 쓰기 | 구현이 쉬움 | 파일이 크면 메모리를 많이 씀 |
| **임시 파일에 한 줄씩 쓰고 → `os.replace` 로 교체** | 중간에 실패해도 원본 안전, 메모리는 한 줄 분량 | 파일 전체를 다시 쓰므로 큰 파일에서 느림 |

**"그 줄만 고치면 O(1) 아닌가요?"에 대한 답**
파일은 디스크 위의 **바이트 배열**입니다(연결 리스트가 아님). 운영체제가 주는 연산은 "특정 위치 덮어쓰기"와 "끝에 붙이기"뿐이고, "중간에 끼워 넣기/빼기"는 없습니다. 배열 중간에 원소를 넣으면 뒤를 전부 옮겨야 하는 것과 같습니다.

```
수정 전: ...{"amount": 15000}⏎{"id": "TX-2"...}⏎{"id": "TX-3"...
수정 후: ...{"amount": 8}⏎{"id": "TX-2"...}⏎{"id": "TX-3"...
                         ↑ 여기부터 파일 끝까지 전부 4바이트 앞으로 당겨야 함 (⏎ = 줄바꿈 문자)
```

당기지 않으면 4바이트의 쓰레기가 남아 그 줄이 깨지고, 반대로 `8 → 15000` 처럼 늘어나면 다음 줄의 앞부분을 덮어씁니다. 그래서 수정 지점부터 끝까지 다시 써야 하고(O(n)), JSONL은 줄 길이가 제각각이라 그 줄이 **어디 있는지** 찾는 것도 처음부터 읽어야 합니다(O(n)).

제자리 수정이 실제로 O(1)이 되는 조건은 따로 있습니다.

| 조건 | 방법 | 대가 |
| --- | --- | --- |
| 수정 전후 길이가 정확히 같음 | 그 위치만 덮어쓰기 | `15000 → 18000` 은 되지만 `15000 → 8` 은 안 됨 |
| 모든 줄을 고정 길이로 저장 | `줄번호 × 길이` 로 위치 계산 | 짧은 값도 공백으로 채워야 하고 최대 길이 제한이 생김 |
| 줄 위치를 적어 둔 색인(인덱스) 보유 | 색인으로 바로 이동 | 색인 파일을 따로 관리해야 함 |
| 삭제는 지우지 않고 "삭제됨" 표시만 | 한 바이트 덮어쓰기 | 쓰레기가 쌓여 주기적 정리 필요 |

데이터베이스가 빠른 이유가 이 기법들의 조합입니다. 이 과제에서 쓰지 않은 이유는 ① JSONL이 가변 길이라 조건이 안 맞고 ② 제자리 덮어쓰기는 원자적이지 않아 과제가 요구한 "안전한 수정"과 반대이며 ③ 임시 파일 방식도 어차피 O(n)이라 같은 비용이면 안전한 쪽이 낫기 때문입니다.

**이유**: 가계부에서 가장 나쁜 일은 데이터가 날아가는 것입니다. 속도보다 안전을 우선했습니다. 느려지는 문제는 [EVALUATION 4-2](EVALUATION.md#4-2-거래가-10만-건으로-늘어난다면-현재-구조에서-병목이-어디이며-어떻게-개선할지-설명할-수-있는가)의 개선안(월별 파일 분할)으로 풀 수 있습니다.

> 코드: [`rewrite`](../budget_app/storage.py#L114-L130 "sym:JsonlFile.rewrite") · [`rewrite_each`](../budget_app/storage.py#L162-L181 "sym:TransactionRepository.rewrite_each")

<a id="c-read"></a>
### 선택 6. 파일을 읽는 방법

| 후보 | 메모리 | 특징 |
| --- | --- | --- |
| `f.read()` / `readlines()` / 리스트로 반환 | 파일 전체만큼 | 간단하지만 파일이 커질수록 메모리가 늘어남 |
| **제너레이터 (`yield`)** | 한 줄 분량 | 필요한 만큼만 읽고 멈출 수 있음. 한 번만 순회 가능 |

**이유**: 거래는 계속 쌓이는 데이터입니다. 10만 건 실측에서 스트리밍 명령은 0.3MB, 결과를 전부 올리는 경우는 26.8MB였습니다.

> 코드: [`iter_records`](../budget_app/storage.py#L83-L103 "sym:JsonlFile.iter_records") · [`iter_all`](../budget_app/storage.py#L137-L145 "sym:TransactionRepository.iter_all")

<a id="c-latest"></a>
### 선택 7. "최신순 N건"을 구하는 방법

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| 전부 읽어 정렬한 뒤 앞 N개 | 간단 | 전부 메모리에 올림 |
| 파일 끝에서 N줄만 읽기 | 매우 빠름 | **입력 순서 ≠ 날짜 순서.** 어제 날짜를 오늘 입력하면 틀린 결과 |
| **`heapq.nlargest(N, 흐름)`** | 한 번 훑으면서 상위 N건만 유지 → 메모리 N건 | 파일을 끝까지 읽기는 해야 함 |

**이유**: 과거 날짜의 거래도 나중에 추가할 수 있으므로 "파일 끝 = 최신"이 아닙니다. 정확성을 지키면서 메모리를 아끼는 방법이 힙입니다.

> 코드: [`recent`](../budget_app/service.py#L251-L255 "sym:BudgetService.recent")

<a id="c-model"></a>
### 선택 8. 거래 데이터를 담는 방법

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| dict (`{"id": ..., "amount": ...}`) | 따로 정의할 것이 없음 | 키 오타(`"amout"`)를 실행 전에 알 수 없음, 어떤 필드가 있는지 코드만 봐서는 모름 |
| 일반 클래스 | 자유로움 | `__init__`, 비교, 출력 코드를 직접 써야 함 |
| **dataclass** | 필드와 타입이 한눈에 보임, `__init__`·비교 자동 생성, `asdict`·`replace` 제공 | (과제 요구사항이기도 함) |

**이유**: 필드 목록이 곧 문서가 되고, `tx.amount` 의 오타는 에디터가 바로 알려 줍니다. 자동 생성된 비교(`==`) 덕분에 "값이 바뀌었는지"를 한 줄로 확인합니다.

> 코드: [`Transaction`](../budget_app/models.py#L72-L95 "sym:Transaction")

<a id="c-types"></a>
### 선택 9. 날짜와 금액의 타입

| 항목 | 고른 것 | 다른 후보 | 이유 |
| --- | --- | --- | --- |
| 날짜 | **문자열 `YYYY-MM-DD`** | `date` 객체 | JSON에 그대로 저장되고, 이 형식은 **문자열 비교가 곧 날짜 비교**라 기간 검색이 간단함. 대신 입력 때 형식을 엄격히 검증 |
| 금액 | **정수 `int`** | 소수 `float` | 원화는 소수점이 없고, `float` 는 `0.1 + 0.2 = 0.30000000000000004` 같은 오차가 있어 돈 계산에 부적합 |

> 코드: [`parse_date`](../budget_app/models.py#L20-L28 "sym:parse_date") · [`parse_amount`](../budget_app/models.py#L48-L55 "sym:parse_amount")

<a id="c-id"></a>
### 선택 10. id를 만드는 방법

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| 거래 개수 + 1 | 간단 | 중간 것을 삭제하면 **이미 있는 id와 겹침** |
| 무작위 UUID (`3f2a9c...`) | 절대 안 겹침, 파일을 안 읽어도 됨 | 길어서 `--id` 로 입력하기 불편 |
| 마지막 번호를 별도 파일에 저장 | 빠름, 재사용 없음 | 파일이 하나 더 필요, 두 파일이 어긋날 수 있음 |
| **남아 있는 가장 큰 번호 + 1** | 짧고 읽기 쉬움, 남은 id와 절대 안 겹침 | 추가할 때 파일을 한 번 훑음, 마지막 거래를 지운 직후엔 그 번호 재사용 |

**이유**: 사용자가 id를 직접 입력하므로 `TX-000012` 처럼 짧아야 합니다. 느려지는 문제는 데이터가 아주 커졌을 때의 개선 과제로 남겼습니다.

> 코드: [`next_number`](../budget_app/storage.py#L147-L150 "sym:TransactionRepository.next_number")

<a id="c-error"></a>
### 선택 11. 오류를 다루는 방법

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| 오류가 나면 그대로 둠 | 코드가 없음 | 스택트레이스가 사용자에게 노출 (과제 금지) |
| 함수마다 `try/except` + `print` | 직관적 | 같은 코드가 수십 번 반복, 하나만 빠뜨려도 스택트레이스 |
| 오류 때 `None`/`False` 반환 | 예외가 없음 | 호출한 쪽이 매번 확인해야 하고, **왜** 실패했는지 전달이 어려움 |
| **`AppError`(원인+힌트)를 `raise` → 데코레이터 한 곳에서 출력** | 어디서든 `raise` 만 하면 됨, 출력 형식이 한 곳, 빠뜨릴 수 없음 | 데코레이터 개념을 알아야 함 |

**이유**: 문제가 생긴 곳은 "무엇이 왜 잘못됐는지"만 알고, 화면에 어떻게 보여 줄지는 몰라도 됩니다. 두 일을 분리한 것입니다.

> 코드: [`AppError`](../budget_app/errors.py#L4-L13 "sym:AppError") · [`handle_errors`](../budget_app/decorators.py#L19-L40 "sym:handle_errors")

<a id="c-argparse"></a>
### 선택 12. 명령줄을 해석하는 방법

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| `sys.argv` 를 직접 분석 | 의존이 없음 | 옵션 순서·누락·`--help` 를 전부 직접 구현 |
| 숫자 메뉴 (`1. 추가 2. 목록…`) | 초보자에게 쉬움 | 과제가 `python -m budget_app <command>` 형태를 요구, 자동화 불가 |
| **`argparse` (표준 라이브러리)** | `--help` 자동 생성, 필수 옵션·잘못된 값 자동 검사, 하위 명령 지원 | 설정 코드가 김 |

**이유**: "모든 명령이 `--help` 를 지원"이라는 요구를 가장 확실하게 만족합니다.

> 코드: [`build_parser`](../budget_app/cli.py#L220-L312 "sym:build_parser")

<a id="c-import"></a>
### 선택 13. import 중 잘못된 행 처리

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| 전체 롤백 (하나라도 틀리면 전부 취소) | 결과가 단순 | 1000행 중 1행 때문에 999행을 못 넣음 |
| 조용히 건너뛰기 | 편해 보임 | **빠진 것을 모름** → 신뢰를 잃음 |
| **부분 성공 + 리포트** | 넣을 수 있는 건 넣고, 빠진 행 번호와 사유를 전부 알려 줌 | 빠진 행은 사용자가 따로 처리 |

단, 파일 자체가 잘못된 경우(헤더 불량, 파일 없음, 인코딩 오류)는 **전체 거부**합니다.

> 코드: [`import_csv`](../budget_app/service.py#L319-L355 "sym:BudgetService.import_csv") · 자세한 설명: [EVALUATION 4-3](EVALUATION.md#4-3-import-csv에-일부-깨진-행이-섞이면-어떻게-처리해-사용자-신뢰를-지킬지부분-성공롤백리포트-설명할-수-있는가)

<a id="c-reuse"></a>
### 선택 14. 공통 파일 기능을 나누는 방법

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| 저장소마다 읽기/쓰기 코드를 각각 작성 | 서로 독립적 | 원자적 쓰기 코드가 4번 중복 |
| 상속 (`class TransactionRepository(JsonlFile)`) | 코드가 짧음 | "거래 저장소는 JSONL 파일이다"라는 관계가 굳어져 포맷 교체가 어려움 |
| **포함 (저장소가 `JsonlFile` 을 하나 가짐)** | 중복 없음, 저장소는 "어떻게 저장되는지"를 몰라도 됨 | `self.file.` 을 한 번 더 거침 |

> 코드: [`JsonlFile`](../budget_app/storage.py#L21-L130 "sym:JsonlFile") · [`TransactionRepository`](../budget_app/storage.py#L133-L135 "span:TransactionRepository..TransactionRepository.__init__")

<a id="c-recurring"></a>
### 선택 15. 반복 내역의 중복 방지

| 후보 | 장점 | 단점 |
| --- | --- | --- |
| 방지하지 않음 | 간단 | 같은 달에 두 번 실행하면 월세가 두 번 들어감 |
| "적용한 달" 목록을 별도 파일에 기록 | 명확 | 파일이 늘고, 거래를 지워도 기록은 남아 어긋남 |
| 거래에 전용 필드 추가 | 깔끔 | 과제가 정한 거래 필드 구성을 바꿔야 함 |
| **생성된 거래에 `recurring:RC-0001` 태그** | 기존 필드만 사용, 거래를 지우면 다시 생성 가능, `search --tag` 로 찾을 수 있음 | 사용자가 태그를 직접 지우면 중복 생성 가능 |

> 코드: [`apply_recurring`](../budget_app/service.py#L406-L442 "sym:BudgetService.apply_recurring")

---

# 2부. 예상 질문과 답변

## A. 전체 구조

**Q1. 프로그램 구조를 설명해 주세요.**
8개 모듈, 4계층입니다. `cli.py` 가 명령을 해석하고 입출력을 맡고, `service.py` 가 업무 규칙을, `storage.py` 가 파일 읽기/쓰기를, `models.py` 가 데이터 구조와 값 검증을 담당합니다. 호출은 CLI → 서비스 → 저장소 → 모델 한 방향입니다.

> 코드: [cli.py](../budget_app/cli.py) · [service.py](../budget_app/service.py) · [storage.py](../budget_app/storage.py) · [models.py](../budget_app/models.py)

**Q2. 왜 한 파일에 다 쓰지 않고 나눴나요?**
바뀌는 이유가 다르기 때문입니다. 출력 문구를 바꾸는 일과 저장 포맷을 바꾸는 일이 서로 영향을 주지 않습니다. 또 서비스 계층에 `print`/`input` 이 없어서 테스트하기 쉽습니다.

> 코드: [`Summary` (서비스가 돌려주는 결과)](../budget_app/service.py#L72-L91 "sym:Summary") · [`cmd_summary` (출력만 담당)](../budget_app/cli.py#L82-L103 "sym:cmd_summary")

**Q3. 명령 하나가 실행되는 흐름을 따라가 보세요. (예: `delete --id TX-000003`)**
`__main__.py` → `cli.main()` (`@handle_errors` 로 감싸져 있음) → argparse가 `delete` 와 `id` 를 해석 → `BudgetService` 생성, `initialize()` 로 파일 확인 → `cmd_delete` → `service.delete_transaction()` 이 먼저 id가 있는지 확인(없으면 `AppError`) → `repository.rewrite_each()` 가 한 줄씩 읽으며 해당 id만 빼고 임시 파일에 기록 → `os.replace` 로 교체 → 결과 출력, 0 반환 → `sys.exit(0)`.

> 코드: [`__main__`](../budget_app/__main__.py#L7-L11 "at:0,4:if __name__ == &quot;__main__&quot;:") · [`main`](../budget_app/cli.py#L315-L324 "sym:main") · [`cmd_delete`](../budget_app/cli.py#L145-L147 "sym:cmd_delete") · [`delete_transaction`](../budget_app/service.py#L239-L243 "sym:BudgetService.delete_transaction") · [`rewrite_each`](../budget_app/storage.py#L162-L181 "sym:TransactionRepository.rewrite_each") · [`rewrite`](../budget_app/storage.py#L114-L130 "sym:JsonlFile.rewrite")

**Q4. 클래스는 무엇이 있고 각각 무슨 일을 하나요?**
모델 `Transaction`/`Budget`/`Recurring`, 파일 도구 `JsonlFile`, 파일별 저장소 `TransactionRepository`/`CategoryStore`/`BudgetStore`/`RecurringStore`, 규칙을 묶는 `BudgetService`, 검색 조건 `SearchFilter`, 결과 묶음 `Summary`/`ImportResult`, 오류 `AppError` 입니다.

> 코드: [모델 3개](../budget_app/models.py#L72-L114 "span:Transaction..Recurring") · [`JsonlFile`](../budget_app/storage.py#L21-L130 "sym:JsonlFile") · [저장소 4개](../budget_app/storage.py#L133-L239 "span:TransactionRepository..RecurringStore") · [`BudgetService`](../budget_app/service.py#L105-L111 "span:BudgetService..BudgetService.__init__") · [`SearchFilter`·`Summary`·`ImportResult`](../budget_app/service.py#L43-L98 "span:SearchFilter..ImportResult")

## B. 저장

**Q5. 왜 CSV가 아니라 JSONL인가요?**
`tags` 가 리스트라서입니다. CSV에 넣으려면 쉼표 구분 문자열로 바꿨다 되돌려야 하고, 금액도 문자열로 읽힙니다. JSONL은 타입이 그대로 보존되고, 한 줄이 한 건이라 한 줄씩 읽는 제너레이터와 딱 맞습니다. 추가도 파일 끝에 한 줄만 붙이면 됩니다.

> 코드: [`iter_records`](../budget_app/storage.py#L83-L103 "sym:JsonlFile.iter_records") · [`append`](../budget_app/storage.py#L105-L112 "sym:JsonlFile.append") · [`Transaction`](../budget_app/models.py#L72-L95 "sym:Transaction")

**Q6. 저장 파일은 몇 개이고 왜 나눴나요?**
`transactions`, `categories`, `budgets`, `recurring` 4개입니다. 성격과 변경 빈도가 다른 데이터를 나누면, 거래를 수정할 때 예산 파일을 건드릴 일이 없고 파일 하나가 손상돼도 나머지는 무사합니다.

> 코드: [transactions](../budget_app/storage.py#L133-L135 "span:TransactionRepository..TransactionRepository.__init__") · [categories](../budget_app/storage.py#L184-L186 "span:CategoryStore..CategoryStore.__init__") · [budgets](../budget_app/storage.py#L206-L208 "span:BudgetStore..BudgetStore.__init__") · [recurring](../budget_app/storage.py#L223-L225 "span:RecurringStore..RecurringStore.__init__")

**Q7. 처음 실행하면 어떻게 되나요?**
`initialize()` 가 없는 파일을 만들고 안내를 출력합니다. 카테고리가 비어 있으면 기본 5개를 만듭니다(안 A). 바로 `add` 를 쓸 수 있게 하기 위해서입니다.

> 코드: [`initialize`](../budget_app/service.py#L113-L135 "sym:BudgetService.initialize") · [`CategoryStore.ensure`](../budget_app/storage.py#L188-L194 "sym:CategoryStore.ensure") · [테스트](../tests/test_app.py#L51-L57 "sym:AppTest.test_first_run_creates_files_and_default_categories")

**Q8. id는 어떻게 만들고, 유일함은 어떻게 보장하나요?**
파일을 한 번 훑어 가장 큰 번호를 찾고 +1 해서 `TX-000001` 형식으로 만듭니다. "개수 + 1" 이 아니라 "최댓값 + 1" 이라, 중간 거래를 삭제해도 남아 있는 id와 겹치지 않습니다. (마지막 거래를 지운 직후에는 그 번호가 다시 쓰일 수 있습니다. 완전한 재사용 금지가 필요하면 마지막 번호를 별도 파일에 저장해야 합니다.)

> 코드: [`next_number`](../budget_app/storage.py#L147-L150 "sym:TransactionRepository.next_number") · [`format_id`](../budget_app/storage.py#L152-L154 "sym:TransactionRepository.format_id") · [테스트](../tests/test_app.py#L138-L139 "at:0,1:# 삭제 후에도 id 는 재사용되지 않고 최댓값 다음 번호가 나온다.")

**Q9. update/delete는 파일에서 어떻게 처리하나요? 왜 그 줄만 고치지 않나요?**
파일은 바이트 배열이라 "중간에 끼워 넣기/빼기" 연산이 없습니다. 줄 길이가 달라지면 그 뒤 내용을 전부 옮겨 써야 해서 제자리 수정도 O(n)이고, 쓰는 도중 꺼지면 반쯤 바뀐 줄이 남습니다(길이가 같을 때만 그 위치를 덮어쓰는 O(1) 수정이 가능). 같은 O(n)이라면 안전한 쪽이 낫기 때문에 전체를 다시 쓰되, 임시 파일에 쓰고 `os.replace` 로 교체합니다. 읽기는 제너레이터라 다시 쓰는 동안에도 메모리에는 한 줄씩만 있습니다.

> 코드: [`rewrite_each`](../budget_app/storage.py#L162-L181 "sym:TransactionRepository.rewrite_each") · [`rewrite`](../budget_app/storage.py#L114-L130 "sym:JsonlFile.rewrite") · 자세한 비교: [선택 5](#c-rewrite)

**Q10. 쓰는 도중 전원이 꺼지면요?**
교체 전이면 원본이 그대로이고 `.tmp` 만 남습니다. `os.replace` 는 운영체제가 한 동작으로 처리하므로 "반쯤 바뀐 파일"은 생기지 않습니다. 디스크에 실제로 내려가도록 교체 전에 `flush` + `fsync` 를 합니다. 남은 `.tmp` 는 다음 실행 때 발견해 지우고 "이전 수정이 중단되어 반영되지 않았다"고 안내합니다.

> 코드: [`rewrite` (flush·fsync·replace·finally)](../budget_app/storage.py#L121-L130 "at:0,9:tmp = self.tmp_path")

**Q10-1. 그러면 고치던 내용은 결국 날아가는 것 아닌가요? 그게 안전한 건가요?**
네, 고치던 그 한 건은 반영되지 않습니다. 이 방식이 지키는 것은 진행 중이던 수정이 아니라 **나머지 전부**입니다. 원본을 직접 덮어쓰다 꺼지면 중단 지점 이후의 다른 거래까지 깨지지만, 임시 파일 방식은 파일이 항상 "수정 전 전체" 아니면 "수정 후 전체"입니다(원자성). `[수정 완료]` 는 교체 뒤에만 출력되므로 "됐다고 했는데 안 돼 있는" 일이 없고, 중단된 사실은 다음 실행 때 안내합니다.

> 코드: [`rewrite`](../budget_app/storage.py#L114-L130 "sym:JsonlFile.rewrite") · [`clear_stale_tmp`](../budget_app/storage.py#L31-L39 "sym:JsonlFile.clear_stale_tmp") · [`initialize`](../budget_app/service.py#L113-L135 "sym:BudgetService.initialize") · [테스트](../tests/test_app.py#L255-L266 "sym:AppTest.test_interrupted_rewrite_is_reported_and_original_kept")

**Q10-2. 중단된 수정을 프로그램이 알아서 마저 해 줘야 하지 않나요?**
일부러 하지 않았습니다. 사용자는 완료 메시지를 못 봤으니 안 된 것으로 알고 있습니다. 나중에 몰래 반영되면 예상과 어긋나고, 이미 다시 실행했다면 두 번 적용됩니다. 데이터베이스도 완료 응답 전에 끊긴 작업은 취소합니다. 자동 복구가 책임질 범위는 "완료했다고 알려 준 것은 잃지 않는다"와 "무슨 일이 있었는지 알려 준다"입니다. 그래서 중단을 감지해 안내하고, 더 큰 사고에 대비해 `backup`/`restore` 를 제공합니다.

> 코드: [`initialize`](../budget_app/service.py#L113-L135 "sym:BudgetService.initialize") · [`restore`](../budget_app/service.py#L365-L378 "sym:BudgetService.restore") · [`cmd_restore`](../budget_app/cli.py#L168-L178 "sym:cmd_restore")

**Q10-3. add는 왜 임시 파일 방식이 아닌가요?**
두 가지 이유입니다. ① 비용: 임시 파일 방식은 한 건을 추가하려고 파일 전체를 다시 써야 합니다(10만 건이면 150바이트 때문에 14MB). 끝에 붙이기는 파일 크기와 무관하게 한 줄만 씁니다. ② 피해 범위: 끝에 붙이기는 **이미 있는 데이터를 건드리지 않습니다.** 중단돼도 깨질 수 있는 것은 마지막 한 줄뿐이고 위치도 항상 파일 끝입니다. 제자리 덮어쓰기는 기존 데이터 한가운데를 건드려 어디까지 깨졌는지 알 수 없다는 점이 다릅니다. 그래서 복구도 기계적으로 가능합니다. 다음 실행 때 파일이 줄바꿈으로 끝나지 않으면 마지막 쓰기가 끊긴 것으로 보고, 그 줄만 떼어 낸 뒤 무엇이 빠졌는지 안내합니다. 데이터베이스의 로그 파일이 쓰는 방식과 같습니다(끝에만 쓰고, 재시작 때 잘린 꼬리를 정리). `[저장 완료]` 전에 `fsync` 로 디스크까지 확정합니다.

> 코드: [`append`](../budget_app/storage.py#L105-L112 "sym:JsonlFile.append") · [`repair_torn_tail`](../budget_app/storage.py#L41-L73 "sym:JsonlFile.repair_torn_tail") · [테스트](../tests/test_app.py#L268-L281 "sym:AppTest.test_torn_last_line_is_repaired_and_reported")

**Q10-5. 마지막 줄은 자동으로 고치면서 중간 줄이 깨지면 왜 멈추나요?**
원인을 아는지의 차이입니다. 마지막 줄이 줄바꿈 없이 끝난 것은 "추가 도중 중단"으로만 생기고, 떼어 내도 잃는 것은 어차피 저장되지 않은 그 한 건뿐입니다. 중간 줄 손상은 추가 중단으로는 생길 수 없어(끝에만 쓰므로) 직접 편집 실수나 디스크 문제일 수 있고, 무엇을 잃는지 프로그램이 판단할 수 없습니다. 조용히 지우면 데이터가 사라진 것을 사용자가 모르게 되므로, 줄 번호를 알려 주고 멈춥니다.

> 코드: [`repair_torn_tail`](../budget_app/storage.py#L41-L73 "sym:JsonlFile.repair_torn_tail") · [`iter_records` 의 손상 감지](../budget_app/storage.py#L83-L103 "sym:JsonlFile.iter_records") · [테스트](../tests/test_app.py#L320-L327 "sym:AppTest.test_corrupted_file_reports_cause_and_hint")

**Q10-4. 백업은 어떻게 되돌리나요?**
`restore` 가 가장 최근 백업으로 되돌립니다(`--name` 으로 지정, `--list` 로 목록). 되돌리기 전에 현재 상태를 자동으로 백업하므로 잘못 복원해도 다시 돌아올 수 있습니다. 복원도 파일마다 임시 파일에 복사한 뒤 교체하므로 도중에 중단돼도 반쯤 복사된 파일이 남지 않습니다.

> 코드: [`restore_data`](../budget_app/storage.py#L268-L281 "sym:restore_data") · [`restore`](../budget_app/service.py#L365-L378 "sym:BudgetService.restore") · [테스트](../tests/test_app.py#L234-L253 "sym:AppTest.test_restore_brings_back_backup_and_is_undoable")

**Q11. 저장 파일의 한 줄이 깨져 있으면요?**
`json.loads` 실패를 잡아 `[오류] 저장 파일이 손상되었습니다: 경로 N번째 줄` 과 복구 힌트를 출력하고 종료 코드 1로 끝납니다. 조용히 건너뛰면 데이터가 사라진 걸 모르게 되므로 일부러 멈춥니다.

> 코드: [`iter_records` 오류 처리](../budget_app/storage.py#L91-L102 "at:1,10:record = json.loads(line)") · [테스트](../tests/test_app.py#L320-L327 "sym:AppTest.test_corrupted_file_reports_cause_and_hint")

## C. 제너레이터

**Q12. 제너레이터를 어디에 썼고, 왜 썼나요?**
`JsonlFile.iter_records`, `TransactionRepository.iter_all`, `BudgetService.iter_filtered`, `BudgetStore.iter_all`, 그리고 `rewrite_each` 안의 `transformed` 입니다. 거래가 계속 쌓이는 파일을 통째로 메모리에 올리지 않기 위해서입니다.

> 코드: [`iter_records`](../budget_app/storage.py#L83-L103 "sym:JsonlFile.iter_records") · [`iter_all`](../budget_app/storage.py#L137-L145 "sym:TransactionRepository.iter_all") · [`iter_filtered`](../budget_app/service.py#L247-L249 "sym:BudgetService.iter_filtered") · [`BudgetStore.iter_all`](../budget_app/storage.py#L210-L212 "sym:BudgetStore.iter_all") · [`transformed`](../budget_app/storage.py#L169-L178 "sym:TransactionRepository.rewrite_each.transformed")

**Q13. `return 리스트` 와 `yield` 의 차이를 이 코드로 설명해 보세요.**
리스트로 돌려주면 모든 줄을 읽어 객체로 만든 뒤에야 첫 건을 쓸 수 있고 메모리도 전체만큼 듭니다. `yield` 는 한 건 만들 때마다 넘겨주고 멈추므로, 받는 쪽이 필요한 만큼만 꺼내 쓸 수 있습니다. `get(id)` 는 `next(...)` 로 찾는 즉시 멈춰서 뒤는 읽지도 않습니다.

> 코드: [`get` (찾으면 즉시 멈춤)](../budget_app/storage.py#L159-L160 "sym:TransactionRepository.get") · [`iter_records`](../budget_app/storage.py#L83-L103 "sym:JsonlFile.iter_records")

**Q14. list는 최신순인데, 정렬하려면 전부 읽어야 하지 않나요?**
전부 **훑기는** 하지만 전부 **들고 있지는** 않습니다. `heapq.nlargest(limit, 제너레이터, key=...)` 는 지금까지 본 것 중 상위 N건만 유지하고 나머지는 버립니다. 메모리는 N건, 시간은 대략 전체 건수 × log N 입니다. 파일은 입력 순서대로 쌓이고 과거 날짜도 추가할 수 있어서, 파일 끝 N줄만 읽는 방식은 "날짜 최신순"이 되지 않습니다.

> 코드: [`recent`](../budget_app/service.py#L251-L255 "sym:BudgetService.recent") · [정렬 기준 `_newest_first`](../budget_app/service.py#L101-L102 "sym:_newest_first") · [테스트](../tests/test_app.py#L76-L80 "sym:AppTest.test_list_is_newest_first_with_limit")

**Q15. search도 스트리밍인가요?**
필터링까지는 스트리밍입니다. `--limit` 을 주면 list와 같은 방식으로 N건만 유지합니다. `--limit` 없이 전체를 최신순으로 보여 줄 때는 정렬 때문에 **조건을 통과한 결과만** 메모리에 올립니다. 파일 전체가 아니라는 점이 차이이고, 이 한계는 README에 적어 두었습니다.

> 코드: [`search`](../budget_app/service.py#L257-L263 "sym:BudgetService.search") · [`SearchFilter.matches`](../budget_app/service.py#L53-L69 "sym:SearchFilter.matches") · [테스트](../tests/test_app.py#L82-L95 "sym:AppTest.test_search_filters")

**Q16. 제너레이터를 두 번 순회하면요?**
두 번째에는 아무것도 안 나옵니다. 그래서 필요할 때마다 `iter_all()` 을 다시 호출합니다.

> 코드: [`iter_all`](../budget_app/storage.py#L137-L145 "sym:TransactionRepository.iter_all")

**Q17. 읽으면서 같은 파일에 쓰면 문제 없나요?**
읽는 건 원본, 쓰는 건 `.tmp` 라 서로 다른 파일입니다. 읽기가 끝나 원본이 닫힌 뒤에 교체합니다.

> 코드: [`rewrite`](../budget_app/storage.py#L114-L130 "sym:JsonlFile.rewrite")

## D. 데코레이터

**Q18. 어떤 데코레이터를 만들었고 어디에 적용했나요?**
`handle_errors`(예외 → 원인+힌트 출력+종료 코드)를 `cli.main` 에, `log_timed`(실행 로그+시간 측정)를 서비스의 `search`, `recent`, `summarize`, `update_transaction`, `delete_transaction`, `import_csv`, `export_csv`, `remove_category`, `apply_recurring` 에 적용했습니다.

> 코드: [`handle_errors`](../budget_app/decorators.py#L19-L40 "sym:handle_errors") · [`log_timed`](../budget_app/decorators.py#L43-L55 "sym:log_timed") · [`main` 에 적용](../budget_app/cli.py#L315-L316 "at:0,1:@handle_errors") · [`search` 에 적용](../budget_app/service.py#L257-L258 "at:1,0:def search(self, flt: SearchFilter, limit: int &#124; None = None) -&gt; list[Transaction]:")

**Q19. 데코레이터 없이 하면 어떻게 되나요?**
모든 명령 함수마다 같은 `try/except` 와 시간 측정 코드를 복사해야 합니다. 문구 하나 바꾸려면 전부 고쳐야 하고, 하나라도 빠뜨리면 그 명령만 스택트레이스가 나옵니다.

> 코드: [`handle_errors`](../budget_app/decorators.py#L19-L40 "sym:handle_errors")

**Q20. `@handle_errors` 가 붙으면 내부적으로 어떻게 동작하나요?**
`main = handle_errors(main)` 과 같습니다. 이후 `main()` 을 부르면 실제로는 `wrapper` 가 실행되고, 그 안에서 `try` 로 원래 `main` 을 호출합니다. 예외가 나면 종류별로 메시지와 종료 코드를 정합니다.

> 코드: [`wrapper`](../budget_app/decorators.py#L23-L38 "at:0,15:def wrapper(*args: P.args, **kwargs: P.kwargs) -&gt; int:") · [`@handle_errors def main`](../budget_app/cli.py#L315-L316 "at:0,1:@handle_errors")

**Q21. `functools.wraps` 는 왜 쓰나요?**
감싼 뒤에도 `func.__name__` 이 원래 이름으로 남게 합니다. `log_timed` 가 로그에 함수 이름을 찍는데, 없으면 전부 `wrapper` 로 나옵니다.

> 코드: [`functools.wraps` 와 `func.__name__`](../budget_app/decorators.py#L46-L49 "at:1,2:def wrapper(*args: P.args, **kwargs: P.kwargs) -&gt; R:")

**Q22. `--verbose` 가 없을 때 `log_timed` 는 어떻게 되나요?**
여전히 실행되지만 로그 레벨이 DEBUG라 출력되지 않습니다. `--verbose` 일 때만 `logging.basicConfig(level=DEBUG)` 로 켭니다.

> 코드: [`--verbose` 일 때만 로그 켜기](../budget_app/cli.py#L318-L319 "at:0,1:if args.verbose:") · [`log_timed`](../budget_app/decorators.py#L43-L55 "sym:log_timed")

## E. 타입 힌트

**Q23. 타입 힌트로 얻은 이점을 코드 예로 설명해 주세요.**
`get(tx_id: str) -> Transaction | None` 은 "없을 수 있다"를 시그니처로 알려 줍니다. 그래서 서비스에 `_require_transaction` 을 두어 `None` 이면 `AppError` 로 바꾸고, 그 뒤 코드는 항상 `Transaction` 이라고 믿고 씁니다. 또 `iter_all() -> Iterator[Transaction]` 은 리스트가 아니라 흐름이라는 걸 알려 줘서 `len()` 이나 인덱싱을 하면 안 된다는 걸 알 수 있습니다.

> 코드: [`get -> Transaction | None`](../budget_app/storage.py#L159-L160 "sym:TransactionRepository.get") · [`_require_transaction`](../budget_app/service.py#L202-L206 "sym:BudgetService._require_transaction") · [`iter_all -> Iterator[Transaction]`](../budget_app/storage.py#L85-L93)

**Q24. 타입 힌트가 틀리면 실행 중에 오류가 나나요?**
아니요. 파이썬은 실행 중에 검사하지 않습니다. 그래서 외부에서 들어온 값(사용자 입력, 파일, CSV)은 `parse_date`, `parse_amount` 같은 검증 함수로 **직접** 확인합니다.

> 코드: [`parse_*` 검증 함수](../budget_app/models.py#L20-L66 "at:0,46:def parse_date(text: str) -&gt; str:") · [`from_dict`](../budget_app/models.py#L85-L95 "sym:Transaction.from_dict")

**Q25. `ask(prompt: str, parse: Callable[[str], T]) -> T` 의 `T` 는 뭔가요?**
"어떤 타입이든 되지만 같은 타입"이라는 표시입니다. `parse_amount` 를 넘기면 결과가 `int`, `parse_date` 를 넘기면 `str` 이 된다는 걸 표현합니다.

> 코드: [`ask`](../budget_app/cli.py#L29-L37 "sym:ask") · [사용 예 `cmd_add`](../budget_app/cli.py#L52-L60 "sym:cmd_add")

## F. 검증과 오류 처리

**Q26. 입력 검증은 어디서 하나요?**
값 하나의 형식(날짜, 금액, 타입)은 `models.py` 의 `parse_*` 함수, 데이터가 필요한 규칙(카테고리 존재 여부, id 존재 여부)은 서비스에서 합니다. `add` 는 틀리면 그 항목만 다시 묻고, 옵션 방식 명령은 오류 메시지를 내고 종료합니다.

> 코드: [`parse_*`](../budget_app/models.py#L20-L66 "at:0,46:def parse_date(text: str) -&gt; str:") · [`require_category`](../budget_app/service.py#L139-L147 "sym:BudgetService.require_category") · [`_require_transaction`](../budget_app/service.py#L202-L206 "sym:BudgetService._require_transaction") · [재입력 `ask`](../budget_app/cli.py#L29-L37 "sym:ask")

**Q27. `2024-02-30` 이나 `2024-1-5` 는 어떻게 걸러지나요?**
`datetime.strptime` 이 존재하지 않는 날짜를 거부합니다. `2024-1-5` 는 strptime이 통과시키기 때문에, 다시 `YYYY-MM-DD` 로 포맷한 결과가 입력과 같은지 비교해 걸러냅니다. 날짜를 문자열로 비교(기간 검색)하므로 자릿수가 꼭 맞아야 합니다.

> 코드: [`parse_date`](../budget_app/models.py#L20-L28 "sym:parse_date")

**Q28. 날짜를 문자열로 비교해도 되나요?**
`YYYY-MM-DD` 는 큰 단위가 앞에 있고 자릿수가 고정이라, 사전순 비교가 곧 날짜순입니다. 그래서 검증에서 형식을 엄격히 맞춥니다.

> 코드: [`SearchFilter.matches` 의 날짜 비교](../budget_app/service.py#L54-L60 "at:0,6:# 날짜가 YYYY-MM-DD 문자열이라 문자열 비교가 곧 날짜 비교다.")

**Q29. 스택트레이스가 절대 안 나온다고 어떻게 보장하나요?**
`handle_errors` 가 `AppError`, 입력 중단, `OSError` 뿐 아니라 마지막에 `Exception` 전체를 잡습니다. 예상 못 한 오류도 한 줄 원인과 힌트로 끝나고, 자세한 내용은 `--verbose` 로그로만 봅니다.

> 코드: [`except Exception`](../budget_app/decorators.py#L35-L38 "at:0,3:except Exception as exc:  # 예상 못 한 오류도 스택트레이스 없이 끝낸다.") · [테스트](../tests/test_app.py#L141-L158 "sym:AppTest.test_missing_id_and_invalid_update_fail_without_change")

**Q30. 종료 코드는 어떻게 정했나요?**
0 정상, 1 입력/데이터 오류, 2 파일 시스템 오류와 잘못된 옵션(argparse 기본값), 3 예상 못 한 오류, 130 입력 중단입니다. `main` 이 정수를 돌려주고 `sys.exit()` 에 넘깁니다.

> 코드: [종료 코드 결정](../budget_app/decorators.py#L24-L38 "at:2,12:except AppError as exc:") · [`sys.exit(main())`](../budget_app/__main__.py#L7-L11 "at:0,4:if __name__ == &quot;__main__&quot;:")

**Q31. update에 잘못된 값을 주면 파일이 일부만 바뀌나요?**
아니요. 모든 값을 검증해 새 객체를 만든 **뒤에** 파일을 다시 씁니다. 검증에서 실패하면 파일을 열지도 않습니다. 테스트 `test_missing_id_and_invalid_update_fail_without_change` 가 이를 확인합니다.

> 코드: [`update_transaction` (검증 후 재작성)](../budget_app/service.py#L219-L236 "at:0,17:current = self._require_transaction(tx_id)") · [테스트](../tests/test_app.py#L141-L158 "sym:AppTest.test_missing_id_and_invalid_update_fail_without_change")

## G. 기능별

**Q32. summary는 어떻게 계산하나요?**
그 달의 거래를 흘려보내며 수입/지출 합계와 카테고리별 지출 딕셔너리를 누적합니다. TOP N은 `heapq.nlargest` 로 뽑고, 예산이 있으면 `지출 / 예산 × 100` 을 사용률로, `지출 > 예산` 이면 경고를 출력합니다.

> 코드: [`summarize`](../budget_app/service.py#L265-L280 "sym:BudgetService.summarize") · [`usage_percent`·`over_budget`](../budget_app/service.py#L85-L91 "span:Summary.usage_percent..Summary") · [테스트](../tests/test_app.py#L99-L117 "sym:AppTest.test_summary_with_budget_and_warning")

**Q33. 사용 중인 카테고리를 삭제하면요?**
기본은 차단하고 몇 건이 사용 중인지와 해결 방법을 알려 줍니다. `--replace-with` 를 주면 해당 거래(와 반복 내역)를 대체 카테고리로 옮긴 뒤 삭제합니다. 과제의 두 선택지를 모두 지원합니다.

> 코드: [`remove_category`](../budget_app/service.py#L156-L183 "sym:BudgetService.remove_category") · [테스트](../tests/test_app.py#L162-L177 "sym:AppTest.test_category_management")

**Q34. import에서 잘못된 행이 있으면요?**
그 행만 건너뛰고 `skipped` 로 세며 행 번호와 사유를 출력합니다. 올바른 행은 등록합니다. 헤더에 필수 컬럼이 없으면 한 건도 넣지 않고 오류로 끝냅니다.

> 코드: [`import_csv`](../budget_app/service.py#L319-L355 "sym:BudgetService.import_csv") · [테스트](../tests/test_app.py#L201-L220 "sym:AppTest.test_import_skips_bad_rows")

**Q35. CSV에서 태그의 쉼표는 어떻게 구분하나요?**
`csv` 모듈이 쉼표가 든 값을 자동으로 따옴표로 감쌉니다(`"meal,daily"`). 읽을 때도 `csv.DictReader` 가 하나의 값으로 되돌려 줍니다. 직접 `split(",")` 을 하지 않은 이유입니다.

> 코드: [`export_csv` 의 csv.writer](../budget_app/service.py#L312-L316 "at:0,4:with out.open(&quot;w&quot;, encoding=&quot;utf-8&quot;, newline=&quot;&quot;) as f:") · [`import_csv` 의 csv.DictReader](../budget_app/service.py#L327-L328 "at:0,1:with source.open(&quot;r&quot;, encoding=&quot;utf-8-sig&quot;, newline=&quot;&quot;) as f:")

**Q36. export에 기간 조건이 왜 필수인가요?**
과제 요구사항이고, 실수로 전체를 내보내는 것을 막습니다. 조건이 없으면 오류와 사용법 힌트를 출력합니다.

> 코드: [기간 조건 검사](../budget_app/service.py#L304-L308 "at:0,4:if not (flt.month or flt.date_from or flt.date_to):") · [`build_period_filter`](../budget_app/service.py#L291-L300 "sym:BudgetService.build_period_filter")

**Q37. 반복 내역을 같은 달에 두 번 적용하면요?**
생성된 거래에 `recurring:RC-0001` 태그를 붙여 둡니다. 다시 적용할 때 그 달에 이 태그가 있으면 건너뜁니다. 31일 규칙은 `calendar.monthrange` 로 구한 말일로 보정합니다.

> 코드: [`apply_recurring`](../budget_app/service.py#L406-L442 "sym:BudgetService.apply_recurring") · [테스트](../tests/test_app.py#L306-L316 "sym:AppTest.test_recurring_apply_is_idempotent_and_clamps_day")

**Q38. 표 정렬은 어떻게 했나요? 한글이 섞이면 줄이 안 맞지 않나요?**
한글은 터미널에서 2칸을 차지합니다. `unicodedata.east_asian_width` 로 실제 표시 폭을 계산해 공백을 채웁니다. `len()` 이나 `ljust()` 만 쓰면 한글이 있는 줄이 밀립니다.

> 코드: [`display_width`](../budget_app/formatter.py#L13-L15 "sym:display_width") · [`format_table`](../budget_app/formatter.py#L23-L30 "sym:format_table")

## H. 한계와 개선

**Q39. 이 프로그램의 한계는 무엇인가요?**
① `--limit` 없는 search와 export는 결과를 메모리에 올립니다. ② 동시 실행을 위한 파일 잠금이 없습니다. ③ 수정/삭제는 매번 파일 전체를 다시 씁니다. ④ id를 찾으려면 파일을 처음부터 훑습니다.

> 코드: [정렬 한계 주석](../budget_app/service.py#L261-L262 "at:0,1:# ponytail: 최신순 정렬 때문에 &#x27;조건에 맞는 결과&#x27;는 메모리에 올린다(파일 전체는 아님).") · [`next_number`](../budget_app/storage.py#L147-L150 "sym:TransactionRepository.next_number") · [`rewrite_each`](../budget_app/storage.py#L162-L181 "sym:TransactionRepository.rewrite_each")

**Q40. 데이터가 아주 커지면 어떻게 바꾸겠습니까?**
월별로 파일을 나누면 summary/search가 해당 월 파일만 읽습니다. 그 이상이면 SQLite 같은 데이터베이스로 옮기는 게 맞습니다. 저장소 계층만 교체하면 되고 서비스/CLI는 그대로 둘 수 있도록 계층을 나눠 두었습니다.

> 코드: [저장소 계층](../budget_app/storage.py) · [10만 건 실측과 개선안](EVALUATION.md#4-2-거래가-10만-건으로-늘어난다면-현재-구조에서-병목이-어디이며-어떻게-개선할지-설명할-수-있는가)

**Q41. 테스트는 어떻게 했나요?**
`tests/test_app.py` 에서 임시 폴더를 만들고 실제 진입점 `main()` 을 명령 인자와 가짜 입력으로 실행해, 출력·종료 코드·저장 파일 내용을 확인합니다. 21개 테스트가 필수 기능과 보너스, 오류 경로를 다루고, 문서의 코드 링크가 현재 코드와 맞는지도 검사합니다.

> 코드: [`run_cli` 테스트 도우미](../tests/test_app.py#L23-L31 "sym:AppTest.run_cli") · [테스트 전체](../tests/test_app.py)

---

# 3부. 시연 순서 (약 5분)

```bash
python -m budget_app --help
```

```bash
python -m budget_app add
```

```bash
python -m budget_app list --limit 5
```

```bash
python -m budget_app search --type expense --from 2024-01-01 --to 2024-01-31
```

```bash
python -m budget_app budget set --month 2024-01 --amount 100000
```

```bash
python -m budget_app summary --month 2024-01 --top 3
```

```bash
python -m budget_app update --id TX-000001 --amount 18000
```

```bash
python -m budget_app delete --id TX-999999
```

```bash
python -m budget_app export --out export.csv --month 2024-01
```

```bash
python -m budget_app category remove --name food
```

```bash
python -m budget_app backup
```

```bash
python -m budget_app restore --list
```

```bash
python -m unittest discover -s tests -v
```

시연 중 보여 줄 포인트

1. `add` 에서 일부러 `2024-13-40` 을 넣어 재입력 흐름 보여 주기
2. `data/transactions.jsonl` 을 열어 한 줄 = 한 건임을 보여 주기
3. `delete --id TX-999999` 후 종료 코드 확인 (PowerShell: `$LASTEXITCODE`, bash: `echo $?`)
4. `summary` 의 예산 초과 경고
5. `--verbose` 로 데코레이터 로그 보여 주기
