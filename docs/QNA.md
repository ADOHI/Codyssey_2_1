# 동료평가 대비: 개념 정리 · 예상 질문 · 답변

읽는 순서: **1부 개념 정리**로 용어를 잡고 → **2부 예상 질문**을 소리 내어 답해 본 뒤 → **3부 시연 순서**대로 직접 실행해 보세요.

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

# 2부. 예상 질문과 답변

## A. 전체 구조

**Q1. 프로그램 구조를 설명해 주세요.**
8개 모듈, 4계층입니다. `cli.py` 가 명령을 해석하고 입출력을 맡고, `service.py` 가 업무 규칙을, `storage.py` 가 파일 읽기/쓰기를, `models.py` 가 데이터 구조와 값 검증을 담당합니다. 호출은 CLI → 서비스 → 저장소 → 모델 한 방향입니다.

**Q2. 왜 한 파일에 다 쓰지 않고 나눴나요?**
바뀌는 이유가 다르기 때문입니다. 출력 문구를 바꾸는 일과 저장 포맷을 바꾸는 일이 서로 영향을 주지 않습니다. 또 서비스 계층에 `print`/`input` 이 없어서 테스트하기 쉽습니다.

**Q3. 명령 하나가 실행되는 흐름을 따라가 보세요. (예: `delete --id TX-000003`)**
`__main__.py` → `cli.main()` (`@handle_errors` 로 감싸져 있음) → argparse가 `delete` 와 `id` 를 해석 → `BudgetService` 생성, `initialize()` 로 파일 확인 → `cmd_delete` → `service.delete_transaction()` 이 먼저 id가 있는지 확인(없으면 `AppError`) → `repository.rewrite_each()` 가 한 줄씩 읽으며 해당 id만 빼고 임시 파일에 기록 → `os.replace` 로 교체 → 결과 출력, 0 반환 → `sys.exit(0)`.

**Q4. 클래스는 무엇이 있고 각각 무슨 일을 하나요?**
모델 `Transaction`/`Budget`/`Recurring`, 파일 도구 `JsonlFile`, 파일별 저장소 `TransactionRepository`/`CategoryStore`/`BudgetStore`/`RecurringStore`, 규칙을 묶는 `BudgetService`, 검색 조건 `SearchFilter`, 결과 묶음 `Summary`/`ImportResult`, 오류 `AppError` 입니다.

## B. 저장

**Q5. 왜 CSV가 아니라 JSONL인가요?**
`tags` 가 리스트라서입니다. CSV에 넣으려면 쉼표 구분 문자열로 바꿨다 되돌려야 하고, 금액도 문자열로 읽힙니다. JSONL은 타입이 그대로 보존되고, 한 줄이 한 건이라 한 줄씩 읽는 제너레이터와 딱 맞습니다. 추가도 파일 끝에 한 줄만 붙이면 됩니다.

**Q6. 저장 파일은 몇 개이고 왜 나눴나요?**
`transactions`, `categories`, `budgets`, `recurring` 4개입니다. 성격과 변경 빈도가 다른 데이터를 나누면, 거래를 수정할 때 예산 파일을 건드릴 일이 없고 파일 하나가 손상돼도 나머지는 무사합니다.

**Q7. 처음 실행하면 어떻게 되나요?**
`initialize()` 가 없는 파일을 만들고 안내를 출력합니다. 카테고리가 비어 있으면 기본 5개를 만듭니다(안 A). 바로 `add` 를 쓸 수 있게 하기 위해서입니다.

**Q8. id는 어떻게 만들고, 유일함은 어떻게 보장하나요?**
파일을 한 번 훑어 가장 큰 번호를 찾고 +1 해서 `TX-000001` 형식으로 만듭니다. "개수 + 1" 이 아니라 "최댓값 + 1" 이라, 중간 거래를 삭제해도 남아 있는 id와 겹치지 않습니다. (마지막 거래를 지운 직후에는 그 번호가 다시 쓰일 수 있습니다. 완전한 재사용 금지가 필요하면 마지막 번호를 별도 파일에 저장해야 합니다.)

**Q9. update/delete는 파일에서 어떻게 처리하나요? 왜 그 줄만 고치지 않나요?**
텍스트 파일은 줄 길이가 달라지면 뒤 내용을 전부 밀어야 해서 "한 줄만 수정"이 안 됩니다. 그래서 전체를 다시 쓰되, 임시 파일에 쓰고 `os.replace` 로 교체합니다. 읽기는 제너레이터라 다시 쓰는 동안에도 메모리에는 한 줄씩만 있습니다.

**Q10. 쓰는 도중 전원이 꺼지면요?**
교체 전이면 원본이 그대로이고 `.tmp` 만 남습니다. `os.replace` 는 운영체제가 한 동작으로 처리하므로 "반쯤 바뀐 파일"은 생기지 않습니다. 디스크에 실제로 내려가도록 교체 전에 `flush` + `fsync` 를 합니다.

**Q11. 저장 파일의 한 줄이 깨져 있으면요?**
`json.loads` 실패를 잡아 `[오류] 저장 파일이 손상되었습니다: 경로 N번째 줄` 과 복구 힌트를 출력하고 종료 코드 1로 끝납니다. 조용히 건너뛰면 데이터가 사라진 걸 모르게 되므로 일부러 멈춥니다.

## C. 제너레이터

**Q12. 제너레이터를 어디에 썼고, 왜 썼나요?**
`JsonlFile.iter_records`, `TransactionRepository.iter_all`, `BudgetService.iter_filtered`, `BudgetStore.iter_all`, 그리고 `rewrite_each` 안의 `transformed` 입니다. 거래가 계속 쌓이는 파일을 통째로 메모리에 올리지 않기 위해서입니다.

**Q13. `return 리스트` 와 `yield` 의 차이를 이 코드로 설명해 보세요.**
리스트로 돌려주면 모든 줄을 읽어 객체로 만든 뒤에야 첫 건을 쓸 수 있고 메모리도 전체만큼 듭니다. `yield` 는 한 건 만들 때마다 넘겨주고 멈추므로, 받는 쪽이 필요한 만큼만 꺼내 쓸 수 있습니다. `get(id)` 는 `next(...)` 로 찾는 즉시 멈춰서 뒤는 읽지도 않습니다.

**Q14. list는 최신순인데, 정렬하려면 전부 읽어야 하지 않나요?**
전부 **훑기는** 하지만 전부 **들고 있지는** 않습니다. `heapq.nlargest(limit, 제너레이터, key=...)` 는 지금까지 본 것 중 상위 N건만 유지하고 나머지는 버립니다. 메모리는 N건, 시간은 대략 전체 건수 × log N 입니다. 파일은 입력 순서대로 쌓이고 과거 날짜도 추가할 수 있어서, 파일 끝 N줄만 읽는 방식은 "날짜 최신순"이 되지 않습니다.

**Q15. search도 스트리밍인가요?**
필터링까지는 스트리밍입니다. `--limit` 을 주면 list와 같은 방식으로 N건만 유지합니다. `--limit` 없이 전체를 최신순으로 보여 줄 때는 정렬 때문에 **조건을 통과한 결과만** 메모리에 올립니다. 파일 전체가 아니라는 점이 차이이고, 이 한계는 README에 적어 두었습니다.

**Q16. 제너레이터를 두 번 순회하면요?**
두 번째에는 아무것도 안 나옵니다. 그래서 필요할 때마다 `iter_all()` 을 다시 호출합니다.

**Q17. 읽으면서 같은 파일에 쓰면 문제 없나요?**
읽는 건 원본, 쓰는 건 `.tmp` 라 서로 다른 파일입니다. 읽기가 끝나 원본이 닫힌 뒤에 교체합니다.

## D. 데코레이터

**Q18. 어떤 데코레이터를 만들었고 어디에 적용했나요?**
`handle_errors`(예외 → 원인+힌트 출력+종료 코드)를 `cli.main` 에, `log_timed`(실행 로그+시간 측정)를 서비스의 `search`, `recent`, `summarize`, `update_transaction`, `delete_transaction`, `import_csv`, `export_csv`, `remove_category`, `apply_recurring` 에 적용했습니다.

**Q19. 데코레이터 없이 하면 어떻게 되나요?**
모든 명령 함수마다 같은 `try/except` 와 시간 측정 코드를 복사해야 합니다. 문구 하나 바꾸려면 전부 고쳐야 하고, 하나라도 빠뜨리면 그 명령만 스택트레이스가 나옵니다.

**Q20. `@handle_errors` 가 붙으면 내부적으로 어떻게 동작하나요?**
`main = handle_errors(main)` 과 같습니다. 이후 `main()` 을 부르면 실제로는 `wrapper` 가 실행되고, 그 안에서 `try` 로 원래 `main` 을 호출합니다. 예외가 나면 종류별로 메시지와 종료 코드를 정합니다.

**Q21. `functools.wraps` 는 왜 쓰나요?**
감싼 뒤에도 `func.__name__` 이 원래 이름으로 남게 합니다. `log_timed` 가 로그에 함수 이름을 찍는데, 없으면 전부 `wrapper` 로 나옵니다.

**Q22. `--verbose` 가 없을 때 `log_timed` 는 어떻게 되나요?**
여전히 실행되지만 로그 레벨이 DEBUG라 출력되지 않습니다. `--verbose` 일 때만 `logging.basicConfig(level=DEBUG)` 로 켭니다.

## E. 타입 힌트

**Q23. 타입 힌트로 얻은 이점을 코드 예로 설명해 주세요.**
`get(tx_id: str) -> Transaction | None` 은 "없을 수 있다"를 시그니처로 알려 줍니다. 그래서 서비스에 `_require_transaction` 을 두어 `None` 이면 `AppError` 로 바꾸고, 그 뒤 코드는 항상 `Transaction` 이라고 믿고 씁니다. 또 `iter_all() -> Iterator[Transaction]` 은 리스트가 아니라 흐름이라는 걸 알려 줘서 `len()` 이나 인덱싱을 하면 안 된다는 걸 알 수 있습니다.

**Q24. 타입 힌트가 틀리면 실행 중에 오류가 나나요?**
아니요. 파이썬은 실행 중에 검사하지 않습니다. 그래서 외부에서 들어온 값(사용자 입력, 파일, CSV)은 `parse_date`, `parse_amount` 같은 검증 함수로 **직접** 확인합니다.

**Q25. `ask(prompt: str, parse: Callable[[str], T]) -> T` 의 `T` 는 뭔가요?**
"어떤 타입이든 되지만 같은 타입"이라는 표시입니다. `parse_amount` 를 넘기면 결과가 `int`, `parse_date` 를 넘기면 `str` 이 된다는 걸 표현합니다.

## F. 검증과 오류 처리

**Q26. 입력 검증은 어디서 하나요?**
값 하나의 형식(날짜, 금액, 타입)은 `models.py` 의 `parse_*` 함수, 데이터가 필요한 규칙(카테고리 존재 여부, id 존재 여부)은 서비스에서 합니다. `add` 는 틀리면 그 항목만 다시 묻고, 옵션 방식 명령은 오류 메시지를 내고 종료합니다.

**Q27. `2024-02-30` 이나 `2024-1-5` 는 어떻게 걸러지나요?**
`datetime.strptime` 이 존재하지 않는 날짜를 거부합니다. `2024-1-5` 는 strptime이 통과시키기 때문에, 다시 `YYYY-MM-DD` 로 포맷한 결과가 입력과 같은지 비교해 걸러냅니다. 날짜를 문자열로 비교(기간 검색)하므로 자릿수가 꼭 맞아야 합니다.

**Q28. 날짜를 문자열로 비교해도 되나요?**
`YYYY-MM-DD` 는 큰 단위가 앞에 있고 자릿수가 고정이라, 사전순 비교가 곧 날짜순입니다. 그래서 검증에서 형식을 엄격히 맞춥니다.

**Q29. 스택트레이스가 절대 안 나온다고 어떻게 보장하나요?**
`handle_errors` 가 `AppError`, 입력 중단, `OSError` 뿐 아니라 마지막에 `Exception` 전체를 잡습니다. 예상 못 한 오류도 한 줄 원인과 힌트로 끝나고, 자세한 내용은 `--verbose` 로그로만 봅니다.

**Q30. 종료 코드는 어떻게 정했나요?**
0 정상, 1 입력/데이터 오류, 2 파일 시스템 오류와 잘못된 옵션(argparse 기본값), 3 예상 못 한 오류, 130 입력 중단입니다. `main` 이 정수를 돌려주고 `sys.exit()` 에 넘깁니다.

**Q31. update에 잘못된 값을 주면 파일이 일부만 바뀌나요?**
아니요. 모든 값을 검증해 새 객체를 만든 **뒤에** 파일을 다시 씁니다. 검증에서 실패하면 파일을 열지도 않습니다. 테스트 `test_missing_id_and_invalid_update_fail_without_change` 가 이를 확인합니다.

## G. 기능별

**Q32. summary는 어떻게 계산하나요?**
그 달의 거래를 흘려보내며 수입/지출 합계와 카테고리별 지출 딕셔너리를 누적합니다. TOP N은 `heapq.nlargest` 로 뽑고, 예산이 있으면 `지출 / 예산 × 100` 을 사용률로, `지출 > 예산` 이면 경고를 출력합니다.

**Q33. 사용 중인 카테고리를 삭제하면요?**
기본은 차단하고 몇 건이 사용 중인지와 해결 방법을 알려 줍니다. `--replace-with` 를 주면 해당 거래(와 반복 내역)를 대체 카테고리로 옮긴 뒤 삭제합니다. 과제의 두 선택지를 모두 지원합니다.

**Q34. import에서 잘못된 행이 있으면요?**
그 행만 건너뛰고 `skipped` 로 세며 행 번호와 사유를 출력합니다. 올바른 행은 등록합니다. 헤더에 필수 컬럼이 없으면 한 건도 넣지 않고 오류로 끝냅니다.

**Q35. CSV에서 태그의 쉼표는 어떻게 구분하나요?**
`csv` 모듈이 쉼표가 든 값을 자동으로 따옴표로 감쌉니다(`"meal,daily"`). 읽을 때도 `csv.DictReader` 가 하나의 값으로 되돌려 줍니다. 직접 `split(",")` 을 하지 않은 이유입니다.

**Q36. export에 기간 조건이 왜 필수인가요?**
과제 요구사항이고, 실수로 전체를 내보내는 것을 막습니다. 조건이 없으면 오류와 사용법 힌트를 출력합니다.

**Q37. 반복 내역을 같은 달에 두 번 적용하면요?**
생성된 거래에 `recurring:RC-0001` 태그를 붙여 둡니다. 다시 적용할 때 그 달에 이 태그가 있으면 건너뜁니다. 31일 규칙은 `calendar.monthrange` 로 구한 말일로 보정합니다.

**Q38. 표 정렬은 어떻게 했나요? 한글이 섞이면 줄이 안 맞지 않나요?**
한글은 터미널에서 2칸을 차지합니다. `unicodedata.east_asian_width` 로 실제 표시 폭을 계산해 공백을 채웁니다. `len()` 이나 `ljust()` 만 쓰면 한글이 있는 줄이 밀립니다.

## H. 한계와 개선

**Q39. 이 프로그램의 한계는 무엇인가요?**
① `--limit` 없는 search와 export는 결과를 메모리에 올립니다. ② 동시 실행을 위한 파일 잠금이 없습니다. ③ 수정/삭제는 매번 파일 전체를 다시 씁니다. ④ id를 찾으려면 파일을 처음부터 훑습니다.

**Q40. 데이터가 아주 커지면 어떻게 바꾸겠습니까?**
월별로 파일을 나누면 summary/search가 해당 월 파일만 읽습니다. 그 이상이면 SQLite 같은 데이터베이스로 옮기는 게 맞습니다. 저장소 계층만 교체하면 되고 서비스/CLI는 그대로 둘 수 있도록 계층을 나눠 두었습니다.

**Q41. 테스트는 어떻게 했나요?**
`tests/test_app.py` 에서 임시 폴더를 만들고 실제 진입점 `main()` 을 명령 인자와 가짜 입력으로 실행해, 출력·종료 코드·저장 파일 내용을 확인합니다. 16개 테스트가 필수 기능과 보너스, 오류 경로를 다룹니다.

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
python -m unittest discover -s tests -v
```

시연 중 보여 줄 포인트

1. `add` 에서 일부러 `2024-13-40` 을 넣어 재입력 흐름 보여 주기
2. `data/transactions.jsonl` 을 열어 한 줄 = 한 건임을 보여 주기
3. `delete --id TX-999999` 후 종료 코드 확인 (PowerShell: `$LASTEXITCODE`, bash: `echo $?`)
4. `summary` 의 예산 초과 경고
5. `--verbose` 로 데코레이터 로그 보여 주기
