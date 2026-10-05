# 동료평가 문항별 답변 정리

평가지의 **항목 1~5** 순서 그대로 정리했습니다. 문항마다 ① 쉬운 말로 ② 한 줄 답 ③ 자세한 설명 ④ 보여 줄 코드(링크) ⑤ 시연 명령 순서입니다.
코드 링크는 해당 줄로 바로 이동합니다(GitHub·에디터 공통).

기초 지식이 없어도 읽을 수 있도록 문항마다 **쉬운 말로** 설명을 먼저 두었습니다. 모르는 단어는 [용어 사전(QNA 0부)](QNA.md#0부-용어-사전-기초-지식이-없어도-읽을-수-있게)에서, "왜 이 방법을 골랐는지"는 [설계 선택 비교(QNA 1.5부)](QNA.md#15부-설계-선택-비교--왜-이것을-골랐나)에서 확인하세요.

- [항목 1. 기능 동작](#항목-1-기능-동작)
- [항목 2. 구조와 안전한 수정/삭제](#항목-2-구조와-안전한-수정삭제)
- [항목 3. 제너레이터 · 데코레이터 · 타입 힌트](#항목-3-제너레이터--데코레이터--타입-힌트)
- [항목 4. 설계 판단](#항목-4-설계-판단)
- [항목 5. 보너스](#항목-5-보너스)
- [부록. 평가 전 체크리스트](#부록-평가-전-체크리스트)

---

## 항목 1. 기능 동작

> **한 번에 보여 주기**: `python demo.py` 를 실행하면 아래 7개 문항과 보너스가 순서대로 시연됩니다(단계마다 Enter). 스크립트: [demo.py](../demo.py)
>
> 평가자가 직접 실행해 확인하는 항목입니다. 아래 명령을 위에서부터 그대로 실행하면 7개 문항이 모두 확인됩니다.
> 깨끗한 상태에서 보여 주려면 `--data-dir demo` 를 붙여 새 폴더에서 시작하세요.

### 1-1. add/list/search/summary/export/import/update/delete가 요구사항대로 동작하는가?

> **쉬운 말로**: 이 프로그램은 터미널에 명령어를 쳐서 쓰는 가계부입니다. `add` 는 기록 추가, `list` 는 최근 기록 보기, `search` 는 조건으로 찾기, `summary` 는 한 달 결산, `update`/`delete` 는 고치기/지우기, `export`/`import` 는 엑셀용 파일로 내보내기/가져오기입니다. 평가자는 이 8개를 직접 실행해 봅니다.
>
> **용어 풀이**: [명령·옵션·대화형 입력](QNA.md#g-run) · [CRUD](QNA.md#g-data) · [테스트](QNA.md#g-quality)

**한 줄 답**: 8개 명령 모두 동작하며, 자동 테스트 21개가 각 명령의 출력·종료 코드·저장 파일 내용을 확인합니다.

| 명령 | 요구사항 | 처리 코드 | 확인하는 테스트 |
| --- | --- | --- | --- |
| add | 대화형 입력, 검증 실패 시 재입력, id 출력 | [cli.py `cmd_add`](../budget_app/cli.py#L52-L60 "sym:cmd_add"), [`ask`](../budget_app/cli.py#L29-L37 "sym:ask"), [service.py `add_transaction`](../budget_app/service.py#L187-L200 "sym:BudgetService.add_transaction") | [test L59](../tests/test_app.py#L59-L62 "sym:AppTest.test_add_assigns_sequential_ids_and_persists"), [L64](../tests/test_app.py#L64-L72 "sym:AppTest.test_add_reprompts_on_invalid_input") |
| list | 최신순, `--limit`(기본 10), 스트리밍 | [`cmd_list`](../budget_app/cli.py#L63-L64 "sym:cmd_list"), [`recent`](../budget_app/service.py#L251-L255 "sym:BudgetService.recent") | [test L76](../tests/test_app.py#L76-L80 "sym:AppTest.test_list_is_newest_first_with_limit") |
| search | `--from/--to/--category/--type/--q/--tag`, 최신순 | [`cmd_search`](../budget_app/cli.py#L67-L71 "sym:cmd_search"), [`SearchFilter.matches`](../budget_app/service.py#L53-L69 "sym:SearchFilter.matches"), [`search`](../budget_app/service.py#L257-L263 "sym:BudgetService.search") | [test L82](../tests/test_app.py#L82-L95 "sym:AppTest.test_search_filters") |
| summary | 수입/지출/잔액, TOP N, 데이터 없음 | [`summarize`](../budget_app/service.py#L265-L280 "sym:BudgetService.summarize"), [`cmd_summary`](../budget_app/cli.py#L82-L103 "sym:cmd_summary") | [test L99](../tests/test_app.py#L99-L117 "sym:AppTest.test_summary_with_budget_and_warning"), [L119](../tests/test_app.py#L119-L123 "sym:AppTest.test_summary_empty_month") |
| update | 옵션 기반, 지정 필드만 변경, 없는 id 처리 | [`update_transaction`](../budget_app/service.py#L208-L237 "sym:BudgetService.update_transaction") | [test L127](../tests/test_app.py#L127-L139 "sym:AppTest.test_update_and_delete"), [L141](../tests/test_app.py#L141-L158 "sym:AppTest.test_missing_id_and_invalid_update_fail_without_change") |
| delete | `--id`, 없는 id는 "없는 데이터" | [`delete_transaction`](../budget_app/service.py#L239-L243 "sym:BudgetService.delete_transaction") | 위와 동일 |
| export | 기간 조건 필수, CSV 생성, 건수 출력 | [`export_csv`](../budget_app/service.py#L302-L317 "sym:BudgetService.export_csv") | [test L181](../tests/test_app.py#L181-L199 "sym:AppTest.test_export_then_import_roundtrip") |
| import | 일괄 등록, 처리 건수 출력 | [`import_csv`](../budget_app/service.py#L319-L355 "sym:BudgetService.import_csv") | [test L201](../tests/test_app.py#L201-L220 "sym:AppTest.test_import_skips_bad_rows") |

**시연**

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
python -m budget_app update --id TX-000001 --amount 18000
```

```bash
python -m budget_app delete --id TX-000001
```

모든 명령의 `--help` 도 동작합니다: [build_parser](../budget_app/cli.py#L220-L312 "sym:build_parser"), [test L329](../tests/test_app.py#L329-L342 "sym:AppTest.test_help_for_every_command").

### 1-2. 프로그램 재실행 후에도 거래/카테고리/예산 데이터가 유지되는가? (저장 파일 3개 이상)

> **쉬운 말로**: 프로그램 안의 변수는 프로그램이 끝나면 사라집니다. 그래서 기록을 **파일**에 적어 둡니다. 이 프로그램은 명령 하나를 실행할 때마다 켜졌다가 꺼지므로, 방금 추가한 거래가 다음 명령에서 보인다면 파일에 저장됐다는 뜻입니다. 공책 한 권에 다 쓰지 않고 거래·카테고리·예산 공책을 따로 두는 것이 "파일 3개 이상"입니다.
>
> **용어 풀이**: [영구 저장·JSONL](QNA.md#g-data)

**한 줄 답**: 명령 한 번이 프로그램 실행 한 번입니다. 매 명령이 파일에 쓰고 끝나며 다음 명령이 파일에서 다시 읽으므로, "add 후 list에 보인다"는 것 자체가 재실행 후 유지의 증거입니다.

- 저장 파일은 4개입니다: `transactions.jsonl`, `categories.jsonl`, `budgets.jsonl`, `recurring.jsonl`
- 파일 경로가 정해지는 곳: [TransactionRepository](../budget_app/storage.py#L133-L135 "span:TransactionRepository..TransactionRepository.__init__"), [CategoryStore](../budget_app/storage.py#L184-L186 "span:CategoryStore..CategoryStore.__init__"), [BudgetStore](../budget_app/storage.py#L206-L208 "span:BudgetStore..BudgetStore.__init__"), [RecurringStore](../budget_app/storage.py#L223-L225 "span:RecurringStore..RecurringStore.__init__")
- 첫 실행 시 자동 생성 + 기본 카테고리: [`initialize`](../budget_app/service.py#L113-L135 "sym:BudgetService.initialize"), [`CategoryStore.ensure`](../budget_app/storage.py#L188-L194 "sym:CategoryStore.ensure"), [test L51](../tests/test_app.py#L51-L57 "sym:AppTest.test_first_run_creates_files_and_default_categories")

**시연**: 명령 실행 후 파일을 직접 열어 보여 주는 것이 가장 확실합니다.

```bash
python -m budget_app category list
```

`data/` 폴더의 `transactions.jsonl` 을 에디터로 열어 한 줄 = 거래 1건임을 보여 주세요.

### 1-3. category add/list/remove가 정상 동작하는가? (삭제 시 사용 중인 카테고리 처리 포함)

> **쉬운 말로**: 카테고리는 거래에 붙이는 분류 이름표(식비, 교통비…)입니다. 문제는 이미 거래에 붙어 있는 이름표를 지울 때입니다. 그냥 지우면 그 거래들은 "존재하지 않는 분류"를 가리키게 됩니다. 그래서 기본적으로 막고, "이 거래들을 어디로 옮길지" 알려 주면 옮긴 뒤에 지웁니다.
>
> **용어 풀이**: [검증](QNA.md#g-data)
>
> **다른 방법과의 비교**: [선택 3. 빈 카테고리](QNA.md#c-category-init) · [선택 4. 사용 중 카테고리 삭제](QNA.md#c-category-remove)

**한 줄 답**: 사용 중인 카테고리는 기본적으로 삭제를 **막고**, `--replace-with` 로 대체 카테고리를 주면 거래를 **옮긴 뒤** 삭제합니다. 과제가 제시한 두 방법을 모두 지원합니다.

- 코드: [`add_category`](../budget_app/service.py#L149-L154 "sym:BudgetService.add_category"), [`remove_category`](../budget_app/service.py#L156-L183 "sym:BudgetService.remove_category"), [`require_category`](../budget_app/service.py#L139-L147 "sym:BudgetService.require_category")
- 설명 포인트
  - 삭제 전 사용 건수를 스트리밍으로 셉니다([L160](../budget_app/service.py#L160 "at:0,0:used = sum(1 for tx in self.transactions.iter_all() if tx.category == name)")). 반복 내역에서 쓰이는 경우도 함께 확인합니다.
  - 오류 메시지에 "몇 건이 사용 중인지"와 "어떻게 하면 되는지(명령 예시)"를 같이 넣었습니다([L162-L166](../budget_app/service.py#L162-L166 "at:0,4:if (used or rules) and not replace_with:")).
  - 이름은 소문자로 통일하고 중복 추가를 막습니다.
  - 마지막 남은 카테고리는 삭제할 수 없습니다(카테고리 없이는 add가 불가능해지므로).
- 테스트: [test L162](../tests/test_app.py#L162-L177 "sym:AppTest.test_category_management")

**시연**

```bash
python -m budget_app category add --name hobby
```

```bash
python -m budget_app category remove --name food
```

```bash
python -m budget_app category remove --name food --replace-with etc
```

### 1-4. budget set이 저장되며, summary에서 예산 사용률/초과 여부가 출력되는가?

> **쉬운 말로**: 예산은 "이번 달에 이만큼만 쓰겠다"는 목표 금액입니다. 결산(summary)할 때 실제 지출을 예산으로 나눠 몇 %를 썼는지 보여 주고, 100%를 넘으면 경고합니다. 예: 예산 10만 원, 지출 16만 5천 원 → 사용률 165%, 6만 5천 원 초과.
>
> **용어 풀이**: [영구 저장](QNA.md#g-data)

**한 줄 답**: `budget set` 은 `budgets.jsonl` 에 한 달에 한 줄로 저장되고, `summary` 는 `지출 ÷ 예산 × 100` 을 사용률로, 지출이 예산보다 크면 `[경고]` 를 출력합니다.

- 저장: [`set_budget`](../budget_app/service.py#L284-L287 "sym:BudgetService.set_budget"), [`BudgetStore.set`](../budget_app/storage.py#L217-L220 "sym:BudgetStore.set") (같은 달은 덮어쓰기)
- 계산: [`Summary.usage_percent`, `over_budget`](../budget_app/service.py#L85-L91 "span:Summary.usage_percent..Summary")
- 출력: [`cmd_summary` L93-L96](../budget_app/cli.py#L93-L96 "at:1,2:print(f&quot;예산: {s.budget}원 (사용률 {s.usage_percent:.1f}%)&quot;)")
- 테스트: [test L99](../tests/test_app.py#L99-L117 "sym:AppTest.test_summary_with_budget_and_warning") — 사용률 37.0%(경고 없음) → 예산을 낮춰 185.0%(경고 있음)까지 확인

**시연**

```bash
python -m budget_app budget set --month 2024-01 --amount 100000
```

```bash
python -m budget_app summary --month 2024-01 --top 3
```

### 1-5. import/export가 명시된 CSV 스키마(UTF-8, 헤더, 컬럼)로 동작하는가?

> **쉬운 말로**: CSV는 쉼표로 칸을 나눈 표 파일이라 엑셀에서 바로 열립니다. "스키마"는 칸의 순서와 이름에 대한 약속입니다. 첫 줄(헤더)에 칸 이름을 적고, 그 아래 한 줄이 거래 한 건입니다. 내보낸 파일을 그대로 다시 가져올 수 있도록 내보내기와 가져오기가 같은 약속을 씁니다.
>
> **용어 풀이**: [CSV·헤더·스키마·UTF-8·BOM](QNA.md#g-data)
>
> **다른 방법과의 비교**: [선택 1. 저장 포맷](QNA.md#c-format)

**한 줄 답**: 헤더는 `date,type,category,amount,memo,tags` 로 고정이고 UTF-8로 읽고 씁니다. export한 파일을 그대로 import할 수 있습니다(왕복 테스트로 확인).

- 스키마 상수: [`CSV_COLUMNS`, `CSV_REQUIRED`](../budget_app/service.py#L39-L40 "at:0,1:CSV_COLUMNS = [&quot;date&quot;, &quot;type&quot;, &quot;category&quot;, &quot;amount&quot;, &quot;memo&quot;, &quot;tags&quot;]")
- export: [`export_csv`](../budget_app/service.py#L302-L317 "sym:BudgetService.export_csv") — 기간 조건이 없으면 오류([L304-L308](../budget_app/service.py#L304-L308 "at:0,4:if not (flt.month or flt.date_from or flt.date_to):"))
- import: [`import_csv`](../budget_app/service.py#L319-L355 "sym:BudgetService.import_csv") — 헤더에 필수 컬럼이 없으면 한 건도 넣지 않고 오류([L329-L334](../budget_app/service.py#L329-L334 "at:0,5:missing = [c for c in CSV_REQUIRED if c not in (reader.fieldnames or [])]"))
- 설명 포인트
  - 태그가 여러 개면 값 안에 쉼표가 생깁니다. `csv` 모듈이 `"meal,daily"` 처럼 따옴표로 감싸 주고 읽을 때 되돌려 줍니다. 직접 `split(",")` 하지 않은 이유입니다.
  - 읽을 때 `utf-8-sig` 를 써서 엑셀이 붙이는 BOM이 있어도 읽습니다.
  - `id` 는 CSV에 없습니다. 가져올 때 새로 부여해 기존 id와 충돌하지 않습니다.
- 테스트: [test L181](../tests/test_app.py#L181-L199 "sym:AppTest.test_export_then_import_roundtrip")

**시연**

```bash
python -m budget_app export --out export.csv --month 2024-01
```

```bash
python -m budget_app import --from export.csv
```

### 1-6. 잘못된 입력/파일 오류에서 스택트레이스 없이 오류 메시지와 해결 힌트를 출력하는가?

> **쉬운 말로**: 스택트레이스는 오류가 났을 때 화면에 쏟아지는 긴 영어 줄들입니다. 개발자에게는 단서지만 사용자에게는 무슨 말인지 알 수 없습니다. 그래서 대신 두 줄만 보여 줍니다: **무엇이 잘못됐는지**(`[오류]`)와 **어떻게 하면 되는지**(`[힌트]`).
>
> **용어 풀이**: [예외·try/except·raise·스택트레이스](QNA.md#g-python) · [데코레이터](QNA.md#g-python)
>
> **다른 방법과의 비교**: [선택 11. 오류 처리](QNA.md#c-error)

**한 줄 답**: 모든 오류는 `[오류] 원인` / `[힌트] 해결 방법` 두 줄로 나옵니다. `main` 전체를 데코레이터로 감싸서 스택트레이스가 나올 경로가 없습니다.

- 오류 객체: [`AppError`](../budget_app/errors.py#L4-L13 "sym:AppError") — 원인(`message`)과 힌트(`hint`)를 함께 가집니다.
- 한 곳에서 처리: [`handle_errors`](../budget_app/decorators.py#L19-L40 "sym:handle_errors"), 적용 위치 [`@handle_errors def main`](../budget_app/cli.py#L315-L324 "sym:main")
- 마지막에 `Exception` 전체를 잡으므로([L35-L38](../budget_app/decorators.py#L35-L38 "at:0,3:except Exception as exc:  # 예상 못 한 오류도 스택트레이스 없이 끝낸다.")) 예상하지 못한 오류도 한 줄로 끝납니다.

| 상황 | 출력 | 코드 |
| --- | --- | --- |
| 잘못된 날짜 | `날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).` / `예: 2024-01-15` | [`parse_date`](../budget_app/models.py#L20-L28 "sym:parse_date") |
| 0·음수·문자 금액 | `금액은 0보다 큰 양수여야 합니다.` | [`parse_amount`](../budget_app/models.py#L48-L55 "sym:parse_amount") |
| 허용 안 된 타입 | `허용되지 않은 타입입니다` | [`parse_type`](../budget_app/models.py#L41-L45 "sym:parse_type") |
| 없는 카테고리 | `등록되지 않은 카테고리입니다` + 사용 가능 목록 | [`require_category`](../budget_app/service.py#L139-L147 "sym:BudgetService.require_category") |
| 없는 id | `없는 데이터입니다: id=...` | [`_require_transaction`](../budget_app/service.py#L202-L206 "sym:BudgetService._require_transaction") |
| 저장 파일 손상 | `저장 파일이 손상되었습니다: 경로 N번째 줄` | [`iter_records` L91-L102](../budget_app/storage.py#L91-L102 "at:1,10:record = json.loads(line)") |
| CSV 없음/헤더 불량 | `CSV 파일을 찾을 수 없습니다` / `필수 컬럼이 없습니다` | [`import_csv`](../budget_app/service.py#L321-L334 "at:0,13:if not source.is_file():") |

- 테스트: [test L141](../tests/test_app.py#L141-L158 "sym:AppTest.test_missing_id_and_invalid_update_fail_without_change")(`Traceback` 문자열이 없음을 확인), [test L320](../tests/test_app.py#L320-L327 "sym:AppTest.test_corrupted_file_reports_cause_and_hint")(손상 파일)

**시연**

```bash
python -m budget_app delete --id TX-999999
```

```bash
python -m budget_app update --id TX-000001 --amount -5
```

### 1-7. 오류 상황에서 종료 코드가 0이 아님을 확인할 수 있는가?

> **쉬운 말로**: 프로그램은 끝날 때 운영체제에 숫자 하나를 남깁니다. 0이면 "잘 끝났다", 0이 아니면 "문제가 있었다"는 뜻입니다. 사람은 화면 글씨를 보면 되지만, 다른 프로그램(자동화 스크립트)은 이 숫자로 성공 여부를 판단합니다. 그래서 오류 메시지만 출력하고 0으로 끝내면 안 됩니다.
>
> **용어 풀이**: [종료 코드·stdout/stderr](QNA.md#g-run)

**한 줄 답**: `main` 이 정수를 돌려주고 [`sys.exit(main())`](../budget_app/__main__.py#L7-L11 "at:0,4:if __name__ == &quot;__main__&quot;:") 로 운영체제에 전달합니다. 정상 0, 오류는 1·2·3·130입니다.

| 코드 | 상황 | 코드 위치 |
| --- | --- | --- |
| 0 | 정상 | [cli.py L324](../budget_app/cli.py#L324 "at:0,0:return 0") |
| 1 | 입력/데이터 오류 (`AppError`) | [decorators.py L26-L28](../budget_app/decorators.py#L26-L28 "at:0,2:except AppError as exc:") |
| 130 | 입력 중단 (Ctrl+C) | [L29-L31](../budget_app/decorators.py#L29-L31 "at:0,2:except (KeyboardInterrupt, EOFError):") |
| 2 | 파일 시스템 오류, 잘못된 옵션(argparse) | [L32-L34](../budget_app/decorators.py#L32-L34 "at:0,2:except OSError as exc:") |
| 3 | 예상하지 못한 오류 | [L35-L38](../budget_app/decorators.py#L35-L38 "at:0,3:except Exception as exc:  # 예상 못 한 오류도 스택트레이스 없이 끝낸다.") |

**시연**: 오류 명령 직후에 종료 코드를 출력합니다.

PowerShell:

```powershell
python -m budget_app delete --id TX-999999; echo $LASTEXITCODE
```

macOS / Linux / Git Bash:

```bash
python -m budget_app delete --id TX-999999; echo $?
```

---

## 항목 2. 구조와 안전한 수정/삭제

### 2-1. 코드가 3개 이상 모듈로 분리되어 있고, 각 모듈의 책임을 "어떻게" 나눴는지 설명할 수 있는가?

> **쉬운 말로**: 식당에 비유하면 이렇습니다. **홀 직원(CLI)** 은 주문을 받고 음식을 내갑니다. **요리사(서비스)** 는 레시피(규칙)대로 요리합니다. **창고 담당(저장소)** 은 재료를 넣고 꺼냅니다. **식재료 규격(모델)** 은 재료가 어떤 모양인지 정합니다. 홀 직원이 창고에 직접 들어가지 않고, 창고 담당이 손님을 응대하지 않습니다. 이렇게 나누면 메뉴판 디자인을 바꿔도 요리법은 그대로이고, 창고를 옮겨도 홀은 그대로입니다.
>
> **용어 풀이**: [모듈·패키지·계층·책임·관심사 분리](QNA.md#g-code)
>
> **다른 방법과의 비교**: [선택 12. 명령줄 해석](QNA.md#c-argparse)

**한 줄 답**: 8개 모듈입니다. 나눈 기준은 **"무엇이 바뀌면 이 파일을 고치게 되는가"** 입니다.

| 모듈 | 책임 | 이 파일을 고치는 경우 |
| --- | --- | --- |
| [cli.py](../budget_app/cli.py) | 명령·옵션 해석, `input()` 재입력 루프, `print()` | 명령/옵션/출력 문구를 바꿀 때 |
| [service.py](../budget_app/service.py) | 업무 규칙, 검색·집계, import/export | 규칙이나 계산 방식이 바뀔 때 |
| [storage.py](../budget_app/storage.py) | 파일 한 줄 ↔ 객체, 안전한 쓰기 | 저장 포맷/위치가 바뀔 때 |
| [models.py](../budget_app/models.py) | 데이터 모양, 값 하나의 형식 검증 | 필드가 추가/변경될 때 |
| [formatter.py](../budget_app/formatter.py) | 표 정렬 문자열 | 표 모양을 바꿀 때 |
| [decorators.py](../budget_app/decorators.py) | 예외 처리, 로그/시간 측정 | 오류 출력 형식·로그 정책이 바뀔 때 |
| [errors.py](../budget_app/errors.py) | `AppError` | (거의 없음) |
| [\_\_main\_\_.py](../budget_app/__main__.py) | 진입점 | (거의 없음) |

**"어떻게" 나눴는지 — 지킨 규칙 3가지**

1. **호출은 한 방향**: `cli → service → storage → models`. 아래 계층은 위 계층을 모릅니다. import 문으로 확인됩니다: [cli.py L11-L15](../budget_app/cli.py#L11-L15 "at:0,4:from .decorators import handle_errors"), [service.py L17-L29](../budget_app/service.py#L17-L29 "at:0,12:from .errors import AppError"), [storage.py L17-L18](../budget_app/storage.py#L17-L18 "at:0,1:from .errors import AppError"), [models.py L12](../budget_app/models.py#L12 "at:0,0:from .errors import AppError").
2. **`print`/`input` 은 CLI에만 있습니다.** 서비스는 값을 받아 결과 객체([`Summary`](../budget_app/service.py#L72-L91 "sym:Summary"), [`ImportResult`](../budget_app/service.py#L94-L98 "sym:ImportResult"))를 돌려줄 뿐입니다. 그래서 같은 서비스를 다른 화면(웹, GUI)에 붙일 수 있고, 테스트에서 결과만 확인할 수 있습니다.
3. **파일을 여는 코드는 저장소에만 있습니다.** 서비스는 "거래를 하나씩 달라"([`iter_all`](../budget_app/storage.py#L137-L145 "sym:TransactionRepository.iter_all"))고만 요청합니다. JSONL을 다른 포맷으로 바꿔도 서비스는 그대로입니다.

**예시로 설명하기**: "delete 한 번"이 계층을 지나는 길
[`cmd_delete`](../budget_app/cli.py#L145-L147 "sym:cmd_delete") (출력 담당) → [`delete_transaction`](../budget_app/service.py#L239-L243 "sym:BudgetService.delete_transaction") (없는 id면 거부하는 규칙) → [`rewrite_each`](../budget_app/storage.py#L162-L181 "sym:TransactionRepository.rewrite_each") (파일 다시 쓰기) → [`Transaction`](../budget_app/models.py#L72-L95 "sym:Transaction") (데이터 모양)

### 2-2. 최소 2개 이상의 클래스에 부여한 책임 경계를 "어떻게" 정했는지 설명할 수 있는가?

> **쉬운 말로**: 클래스는 "관련된 데이터와 기능을 묶은 설계도"입니다. 책임 경계란 **"이 클래스는 여기까지만 안다"** 는 선입니다. 예를 들어 카테고리 저장소는 카테고리 파일만 압니다. 거래 파일은 모릅니다. 그러면 "거래에서 쓰는 카테고리는 못 지운다"는 규칙은 어디에 둘까요? 두 파일을 모두 볼 수 있는 한 단계 위(서비스)에 둡니다.
>
> **용어 풀이**: [클래스·객체·메서드·포함·상속](QNA.md#g-code) · [dataclass](QNA.md#g-code)
>
> **다른 방법과의 비교**: [선택 8. 데이터를 담는 방법](QNA.md#c-model) · [선택 14. 포함 vs 상속](QNA.md#c-reuse)

**한 줄 답**: 클래스는 13개이고, **"데이터를 담는 클래스 / 파일 하나를 책임지는 클래스 / 규칙을 조합하는 클래스"** 세 종류로 경계를 정했습니다.

| 종류 | 클래스 | 책임 | 모르는 것 |
| --- | --- | --- | --- |
| 데이터 | [`Transaction`](../budget_app/models.py#L72-L95 "sym:Transaction"), [`Budget`](../budget_app/models.py#L98-L101 "sym:Budget"), [`Recurring`](../budget_app/models.py#L104-L114 "sym:Recurring") | 필드 묶음, dict 변환 | 파일, 화면 |
| 파일 도구 | [`JsonlFile`](../budget_app/storage.py#L21-L130 "sym:JsonlFile") | JSONL 읽기(제너레이터)·추가·원자적 재작성 | 안에 든 것이 거래인지 예산인지 |
| 저장소 | [`TransactionRepository`](../budget_app/storage.py#L133-L181 "sym:TransactionRepository"), [`CategoryStore`](../budget_app/storage.py#L184-L203 "sym:CategoryStore"), [`BudgetStore`](../budget_app/storage.py#L206-L220 "sym:BudgetStore"), [`RecurringStore`](../budget_app/storage.py#L223-L239 "sym:RecurringStore") | **파일 1개 = 클래스 1개**. dict ↔ 모델 변환 | 업무 규칙 |
| 서비스 | [`BudgetService`](../budget_app/service.py#L105-L111 "span:BudgetService..BudgetService.__init__") | 여러 저장소를 조합해 규칙 적용 | `print`, 파일 경로 |
| 값 객체 | [`SearchFilter`](../budget_app/service.py#L43-L69 "sym:SearchFilter"), [`Summary`](../budget_app/service.py#L72-L91 "sym:Summary"), [`ImportResult`](../budget_app/service.py#L94-L98 "sym:ImportResult") | 검색 조건 / 결과 묶음 | 저장 방식 |
| 오류 | [`AppError`](../budget_app/errors.py#L4-L13 "sym:AppError") | 원인 + 힌트 | |

**경계를 정한 기준을 보여 주는 예 2가지**

1. **"카테고리가 사용 중이면 삭제 금지"는 어디에 둘까?**
   이 규칙은 카테고리 파일과 거래 파일을 **둘 다** 봐야 합니다. `CategoryStore` 는 자기 파일만 알아야 하므로 여기에 두면 경계가 깨집니다. 그래서 두 저장소를 모두 가진 `BudgetService` 의 [`remove_category`](../budget_app/service.py#L156-L183 "sym:BudgetService.remove_category") 에 두었습니다. `CategoryStore.remove` 는 [묻지 않고 지우기만](../budget_app/storage.py#L202-L203 "sym:CategoryStore.remove") 합니다.
2. **`JsonlFile` 과 `TransactionRepository` 를 왜 나눴나?**
   "한 줄씩 읽기 / 안전하게 다시 쓰기"는 4개 파일에 똑같이 필요합니다. 이것을 `JsonlFile` 하나에 두고 4개 저장소가 [하나씩 가져다 씁니다](../budget_app/storage.py#L134-L135 "sym:TransactionRepository.__init__")(상속이 아니라 포함). 원자적 쓰기 코드가 한 곳에만 있어서, 고칠 때도 한 곳만 고치면 됩니다.

### 2-3. 파일 기반 update/delete를 "어떻게" 안전하게 처리했는지 설명할 수 있는가?

> **쉬운 말로**: 공책의 한 줄을 고치려는데, 지우개로 지우고 다시 쓰다가 정전이 되면 그 줄은 반쯤 지워진 채로 남습니다. 대신 **새 공책에 전체를 옮겨 적으면서** 그 줄만 고쳐 쓰고, 다 끝난 뒤에 헌 공책과 새 공책을 **한 번에 바꿔치기**하면 어떨까요? 옮겨 적다가 정전이 돼도 헌 공책은 멀쩡합니다. 이것이 "임시 파일 + 교체"이고, 이런 성질을 원자적이라고 합니다.
>
> **용어 풀이**: [원자적·임시 파일·os.replace·flush/fsync·재작성](QNA.md#g-data)
>
> **다른 방법과의 비교**: [선택 5. 파일을 고치는 방법](QNA.md#c-rewrite)

**한 줄 답**: **① 먼저 검증하고 ② 임시 파일에 전부 쓴 뒤 ③ `os.replace` 로 한 번에 교체**합니다. 어느 단계에서 실패해도 원본은 온전합니다.

**왜 그 줄만 고치지 않나?** 파일은 디스크 위의 바이트 배열이라 "특정 위치 덮어쓰기"와 "끝에 붙이기"만 됩니다. 줄 길이가 달라지면(금액 15000 → 8) 그 뒤 내용을 파일 끝까지 전부 옮겨 써야 하므로, 제자리 수정도 O(1)이 아니라 **O(n)** 입니다. 줄 길이가 제각각이라 그 줄의 위치를 찾는 것도 처음부터 읽어야 합니다. 게다가 제자리에서 덮어쓰다 꺼지면 반쯤 바뀐 줄이 남습니다. 어차피 O(n)이라면 **다시 쓰는 도중의 실패**에 안전한 방식을 택하는 것이 맞습니다.

> 길이가 정확히 같을 때(15000 → 18000), 고정 길이 레코드, 색인, 삭제 표시 같은 조건에서는 제자리 O(1) 수정이 가능합니다. 데이터베이스가 쓰는 방식이며, 비교표는 [QNA 선택 5](QNA.md#c-rewrite)에 있습니다.

**3단계**

| 단계 | 하는 일 | 코드 | 실패하면 |
| --- | --- | --- | --- |
| ① 검증 | id 존재 확인, 새 값 전부 검증, 수정된 객체를 메모리에 완성 | [`update_transaction` L219-L235](../budget_app/service.py#L219-L235 "at:0,16:current = self._require_transaction(tx_id)") | 파일을 열지도 않고 종료 |
| ② 임시 파일 | 원본을 한 줄씩 읽어 `transactions.jsonl.tmp` 에 기록, `flush`+`fsync` 로 디스크에 확정 | [`JsonlFile.rewrite` L121-L127](../budget_app/storage.py#L121-L127 "at:0,6:tmp = self.tmp_path") | 원본 그대로, `.tmp` 는 `finally` 에서 삭제 |
| ③ 교체 | `os.replace(tmp, 원본)` | [L128](../budget_app/storage.py#L128 "at:0,0:os.replace(tmp, self.path)") | 운영체제가 한 동작으로 처리 → "반쯤 바뀐 파일"이 없음 |

- 읽기와 쓰기를 잇는 부분: [`rewrite_each`](../budget_app/storage.py#L162-L181 "sym:TransactionRepository.rewrite_each"). 안쪽의 `transformed` 제너레이터가 원본을 한 줄씩 읽어 바꾸거나(update) 건너뛰어(delete) 넘겨줍니다. 메모리에는 한 줄만 있습니다.
- update와 delete는 같은 함수를 씁니다: update는 [`updated if tx.id == tx_id else tx`](../budget_app/service.py#L236 "at:0,0:self.transactions.rewrite_each(lambda tx: updated if tx.id == tx_id else tx)"), delete는 [`None if t.id == tx_id else t`](../budget_app/service.py#L242 "at:0,0:self.transactions.rewrite_each(lambda t: None if t.id == tx_id else t)") (`None` = 그 줄 삭제).
- 읽는 파일(원본)과 쓰는 파일(`.tmp`)이 달라서, 읽으면서 쓰는 충돌이 없습니다.

**증거(테스트)**: [test L141](../tests/test_app.py#L141-L158 "sym:AppTest.test_missing_id_and_invalid_update_fail_without_change") — 없는 id, 음수 금액, 없는 카테고리, 없는 날짜로 6번 실패시킨 뒤 **파일 내용이 한 글자도 바뀌지 않았음**을 확인합니다. [test L137](../tests/test_app.py#L137-L138 "at:1,0:# 삭제 후에도 id 는 재사용되지 않고 최댓값 다음 번호가 나온다.") 은 작업 후 `.tmp` 가 남지 않음을 확인합니다.

**이 방식이 지키는 것과 못 지키는 것** ("그러면 고치던 내용은 날아가는 것 아닌가요?")

| | 고치던 그 1건 | 나머지 데이터 |
| --- | --- | --- |
| 원본을 직접 덮어쓰다 중단 | 날아감 | **중단 지점 이후가 깨지거나 사라짐** |
| 임시 파일 + 교체 중 중단 | 반영 안 됨 (수정 전 값으로 남음) | 온전함 |

- 보장하는 것은 "파일이 항상 **수정 전 전체** 아니면 **수정 후 전체**"라는 점(원자성)입니다. "시작한 수정은 반드시 끝난다"가 아닙니다.
- `[수정 완료]` 는 교체가 끝난 뒤에만 출력됩니다. 메시지를 못 봤다면 반영되지 않은 것입니다. "됐다고 했는데 안 돼 있는" 경우가 없습니다.
- 중단된 사실은 **다음 실행 때 알려 줍니다.** 남아 있는 임시 파일을 발견하면 지우고 안내합니다: [`clear_stale_tmp`](../budget_app/storage.py#L31-L39 "sym:JsonlFile.clear_stale_tmp"), [`initialize`](../budget_app/service.py#L113-L135 "sym:BudgetService.initialize"), [테스트](../tests/test_app.py#L255-L266 "sym:AppTest.test_interrupted_rewrite_is_reported_and_original_kept")
- 중단된 수정을 **자동으로 이어서 실행하지는 않습니다.** 데이터베이스도 완료 응답 전에 끊긴 작업은 취소합니다. 사용자는 안 된 것으로 알고 있는데 나중에 몰래 반영되면 오히려 예상과 어긋나고, 이미 다시 실행했다면 두 번 적용되기 때문입니다.

**보장 범위 밖 (물으면 솔직하게)**

- 두 터미널에서 동시에 수정하면 한쪽 변경이 사라질 수 있습니다(파일 잠금 없음).
- `add`·`import` 는 임시 파일 방식이 아니라 **파일 끝에 붙이기**입니다. 한 건 추가하려고 파일 전체를 다시 쓰는 것은 낭비이고, 끝에 붙이기는 기존 데이터를 건드리지 않아 중단돼도 피해가 **마지막 한 줄**로 한정되기 때문입니다. 그 잘린 한 줄은 다음 실행 때 **자동으로 떼어 내고 무엇이 빠졌는지 안내**합니다: [`repair_torn_tail`](../budget_app/storage.py#L41-L73 "sym:JsonlFile.repair_torn_tail"), [테스트](../tests/test_app.py#L268-L281 "sym:AppTest.test_torn_last_line_is_repaired_and_reported"). 판별 기준은 "파일이 줄바꿈으로 끝나지 않는다"입니다. 추가는 항상 `한 줄 + 줄바꿈`을 쓰므로 줄바꿈이 없으면 마지막 쓰기가 끊긴 것입니다. 내용은 다 쓰였고 줄바꿈만 빠진 경우는 버리지 않고 줄바꿈만 채웁니다([테스트](../tests/test_app.py#L283-L292 "sym:AppTest.test_complete_last_line_without_newline_is_kept")). 또 `[저장 완료]` 를 알리기 전에 `flush`+`fsync` 로 디스크까지 확정합니다([`append`](../budget_app/storage.py#L105-L112 "sym:JsonlFile.append")).
- 파일 **중간** 줄이 깨진 경우는 자동으로 고치지 않고 멈춥니다. 추가 도중 중단으로는 생길 수 없는 손상이라 원인을 알 수 없고, 조용히 지우면 데이터가 사라진 것을 모르게 되기 때문입니다.

**추가 안전장치**: `backup` 으로 타임스탬프 폴더에 복사본을 남기고([`backup_data`](../budget_app/storage.py#L242-L257 "sym:backup_data")), `restore` 로 되돌립니다([`restore_data`](../budget_app/storage.py#L268-L281 "sym:restore_data"), [`restore`](../budget_app/service.py#L365-L378 "sym:BudgetService.restore")). 되돌리기 전에 현재 상태를 자동 백업하므로 복원도 취소할 수 있습니다.

---

## 항목 3. 제너레이터 · 데코레이터 · 타입 힌트

### 3-1. list/search를 제너레이터로 스트리밍 처리한 방식을 "어떻게" 구현했고, "왜" 유리한지 설명할 수 있는가?

> **쉬운 말로**: 책 1000쪽에서 "최근 일기 10개"를 찾는다고 합시다. **리스트 방식**은 1000쪽을 전부 복사해 책상에 펼쳐 놓고 고릅니다(책상 = 메모리). **제너레이터 방식**은 책을 한 쪽씩 넘기면서, 손에는 "지금까지 본 것 중 최신 10개"만 들고 있습니다. 책이 10만 쪽이 돼도 손에 든 것은 10개뿐입니다. `yield` 는 "한 쪽 보여 주고 다음 쪽을 달라고 할 때까지 기다림"입니다.
>
> **용어 풀이**: [리스트·이터레이터·제너레이터·yield·지연 평가·스트리밍·메모리·힙](QNA.md#g-python)
>
> **다른 방법과의 비교**: [선택 6. 파일을 읽는 방법](QNA.md#c-read) · [선택 7. 최신순 N건](QNA.md#c-latest)

**한 줄 답**: 파일을 한 줄 읽어 `yield` 하는 제너레이터를 3겹으로 쌓았습니다. 파일 크기와 상관없이 메모리는 "지금 보는 한 줄 + 보여 줄 N건"만 씁니다.

**어떻게 — 3겹 파이프라인**

| 단계 | 제너레이터 | 하는 일 |
| --- | --- | --- |
| 1 | [`JsonlFile.iter_records`](../budget_app/storage.py#L83-L103 "sym:JsonlFile.iter_records") | 파일 한 줄 → dict (`yield record`, [L103](../budget_app/storage.py#L103 "at:0,0:yield record")) |
| 2 | [`TransactionRepository.iter_all`](../budget_app/storage.py#L137-L145 "sym:TransactionRepository.iter_all") | dict → `Transaction` |
| 3 | [`BudgetService.iter_filtered`](../budget_app/service.py#L247-L249 "sym:BudgetService.iter_filtered") | 조건에 맞는 것만 통과 (제너레이터 표현식) |

- **list**: [`heapq.nlargest(limit, 흐름, key=날짜)`](../budget_app/service.py#L251-L255 "sym:BudgetService.recent"). 거래가 흘러오는 동안 "지금까지 본 것 중 최신 N건"만 들고 있고 나머지는 버립니다.
- **search**: 조건 검사는 [`SearchFilter.matches`](../budget_app/service.py#L53-L69 "sym:SearchFilter.matches"). `--limit` 이 있으면 list와 같은 방식, 없으면 조건을 통과한 결과만 정렬합니다([`search`](../budget_app/service.py#L257-L263 "sym:BudgetService.search")).

**동작 방식을 말로 설명하기**
`yield` 를 만나면 함수가 값을 하나 넘기고 **그 자리에서 멈춥니다**. 받는 쪽이 다음 값을 요구하면 멈춘 곳에서 이어서 한 줄을 더 읽습니다. 즉 "다 읽고 나서 주는" 것이 아니라 "달라고 할 때마다 한 줄씩" 줍니다. 호출만 해서는 파일을 열지도 않습니다(지연 평가).

**왜 유리한가 — 실측 (거래 10만 건, 14MB 파일)**

| 명령 | 최대 메모리 사용 |
| --- | --- |
| `list --limit 10` | 0.3 MB |
| `summary --month` | 0.2 MB |
| `search --category food --limit 10` | 0.2 MB |
| `search --category food` (limit 없음, 결과 약 2만 건을 정렬) | 26.8 MB |

스트리밍으로 처리한 명령은 파일이 14MB여도 1MB 미만입니다. 같은 파일을 리스트로 전부 올리면 100MB 이상이 필요합니다. 표의 마지막 줄이 "스트리밍하지 않으면 어떻게 되는지"를 보여 주는 대조군입니다.

그 밖의 이점: [`get(id)`](../budget_app/storage.py#L159-L160 "sym:TransactionRepository.get") 은 `next(...)` 로 **찾는 즉시 멈춰서** 뒤쪽은 읽지도 않습니다.

**예상되는 반문과 답**

- *"최신순이면 어차피 전부 읽잖아요?"* → 전부 **훑지만** 전부 **들고 있지는** 않습니다. 시간은 건수에 비례하고, 메모리는 N건으로 고정입니다. 파일에는 입력 순서대로 쌓이고 과거 날짜도 추가할 수 있어서, 파일 끝 N줄만 읽는 방식으로는 "날짜 최신순"이 되지 않습니다.
- *"search도 완전히 스트리밍인가요?"* → 필터링까지는 스트리밍입니다. `--limit` 없이 전체를 최신순으로 보여 줄 때는 정렬 때문에 **통과한 결과만** 메모리에 올립니다. 이 한계는 코드 주석([L261-L262](../budget_app/service.py#L261-L262 "at:0,1:# ponytail: 최신순 정렬 때문에 &#x27;조건에 맞는 결과&#x27;는 메모리에 올린다(파일 전체는 아님)."))과 README에 적어 두었습니다.

### 3-2. 데코레이터로 분리한 공통 기능이 무엇이며, "왜" 분리가 필요했는지 설명할 수 있는가?

> **쉬운 말로**: 데코레이터는 함수에 씌우는 **포장지**입니다. 선물(함수)은 그대로 두고 포장지가 앞뒤로 일을 덧붙입니다. 예를 들어 모든 명령에 "오류가 나면 친절한 두 줄로 바꿔 보여 준다"가 필요한데, 이것을 명령 20개 안에 각각 적는 대신 포장지 하나로 만들어 맨 바깥에 한 번 씌웁니다. 함수 위의 `@handle_errors` 한 줄이 "이 포장지를 씌워라"는 표시입니다.
>
> **용어 풀이**: [데코레이터·래퍼·공통 관심사·로그](QNA.md#g-python)
>
> **다른 방법과의 비교**: [선택 11. 오류 처리](QNA.md#c-error)

**한 줄 답**: **예외 처리**(`handle_errors`)와 **실행 로그·시간 측정**(`log_timed`) 두 가지입니다. 모든 명령에 똑같이 필요한 코드라서, 각 함수에 복사하지 않고 한 곳에 두었습니다.

| 데코레이터 | 정의 | 적용한 곳 | 하는 일 |
| --- | --- | --- | --- |
| `handle_errors` | [decorators.py L19-L40](../budget_app/decorators.py#L19-L40 "sym:handle_errors") | [`main`](../budget_app/cli.py#L315-L316 "at:0,1:@handle_errors") 1곳 | 예외 → `[오류]`/`[힌트]` 출력 + 종료 코드 |
| `log_timed` | [decorators.py L43-L55](../budget_app/decorators.py#L43-L55 "sym:log_timed") | 서비스 메서드 9곳 (예: [`search`](../budget_app/service.py#L257-L258 "at:1,0:def search(self, flt: SearchFilter, limit: int &#124; None = None) -&gt; list[Transaction]:"), [`summarize`](../budget_app/service.py#L265-L266 "at:1,0:def summarize(self, month: str, top: int = 3) -&gt; Summary:"), [`update_transaction`](../budget_app/service.py#L208-L209 "at:1,0:def update_transaction(")) | 시작/종료 로그 + 소요 시간(ms) |

**왜 분리했나**

1. **중복 제거**: 데코레이터가 없으면 명령 함수 20여 개마다 같은 `try/except` 를 써야 합니다. 문구 하나 바꾸려면 전부 고쳐야 합니다.
2. **빠뜨릴 수 없음**: `main` 한 곳을 감쌌으므로 나중에 명령을 추가해도 자동으로 보호됩니다. 함수마다 넣는 방식이면 하나만 빠뜨려도 그 명령에서 스택트레이스가 나옵니다.
3. **본래 코드가 깨끗함**: [`summarize`](../budget_app/service.py#L265-L280 "sym:BudgetService.summarize") 안에는 집계 코드만 있고 시간 측정 코드는 한 줄도 없습니다. `@log_timed` 한 줄을 떼면 측정이 꺼집니다.

**동작 원리**
`@handle_errors` 를 붙이면 `main = handle_errors(main)` 과 같습니다. 이후 `main()` 을 부르면 실제로는 안쪽의 [`wrapper`](../budget_app/decorators.py#L23-L38 "at:0,15:def wrapper(*args: P.args, **kwargs: P.kwargs) -&gt; int:") 가 실행되고, 그 안에서 `try` 로 원래 `main` 을 호출합니다.

- [`functools.wraps`](../budget_app/decorators.py#L46-L47 "at:1,0:def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:"): 감싼 뒤에도 원래 함수 이름이 유지됩니다. `log_timed` 가 로그에 [`func.__name__`](../budget_app/decorators.py#L49 "at:0,0:logger.debug(&quot;시작: %s&quot;, func.__name__)") 을 찍는데, 이것이 없으면 전부 `wrapper` 로 나옵니다.
- `log_timed` 의 [`try/finally`](../budget_app/decorators.py#L50-L53 "at:2,1:finally:"): 함수가 예외로 끝나도 종료 로그는 남습니다.

**시연**

```bash
python -m budget_app search --q 점심 --verbose
```

`[로그] 시작: search` / `[로그] 종료: search (2.41 ms)` 가 출력됩니다. `--verbose` 가 없으면 조용합니다.

### 3-3. 타입 힌트를 적용해 얻는 이점을 실제 코드 예로 "어떻게" 확인했고 "왜" 도움이 되는지 설명할 수 있는가?

> **쉬운 말로**: 타입 힌트는 함수에 붙이는 **사용 설명 라벨**입니다. `get(tx_id: str) -> Transaction | None` 은 "문자열 id를 주면 거래를 돌려주는데, **없을 수도 있다**"는 뜻입니다. 이 라벨이 없으면 함수 안을 읽어 봐야 알 수 있습니다. 라벨이 있으면 에디터가 "없을 때 처리를 안 했네요" 하고 미리 알려 줍니다. 단, 라벨일 뿐이라 실행 중에 강제하지는 않습니다.
>
> **용어 풀이**: [타입·타입 힌트·None·X | None](QNA.md#g-python)
>
> **다른 방법과의 비교**: [선택 9. 날짜와 금액의 타입](QNA.md#c-types)

**한 줄 답**: 함수의 입력과 출력을 시그니처에 적어 두면, 호출하는 쪽이 **본문을 읽지 않고도** 올바르게 쓸 수 있습니다. 코드에서 실제로 도움이 된 예 4가지입니다.

| 예 | 시그니처 | 타입이 알려 주는 것 → 그래서 한 일 |
| --- | --- | --- |
| 1 | [`get(tx_id: str) -> Transaction \| None`](../budget_app/storage.py#L159 "at:0,0:def get(self, tx_id: str) -&gt; Transaction &#124; None:") | "없을 수 있다" → [`_require_transaction`](../budget_app/service.py#L202-L206 "sym:BudgetService._require_transaction") 에서 `None` 을 `AppError` 로 바꿔, 이후 코드는 항상 `Transaction` 이라고 믿고 씁니다 |
| 2 | [`iter_all() -> Iterator[Transaction]`](../budget_app/storage.py#L85) | "리스트가 아니라 흐름" → `len()`·인덱싱·두 번 순회를 하면 안 된다는 것을 알 수 있습니다 |
| 3 | [`rewrite_each(fn: Callable[[Transaction], Transaction \| None]) -> int`](../budget_app/storage.py#L110) | "거래를 받아 거래 또는 None을 돌려주는 함수를 넘겨라" → `None` 이 삭제를 뜻한다는 계약이 시그니처에 드러납니다 |
| 4 | [`ask(prompt: str, parse: Callable[[str], T]) -> T`](../budget_app/cli.py#L29) | "넘긴 검증 함수의 반환 타입이 곧 결과 타입" → `parse_amount` 를 넘기면 `int`, `parse_date` 를 넘기면 `str` |

**"어떻게" 확인했나**: 에디터(VS Code 등)에서 함수에 마우스를 올리면 시그니처가 보이고, `svc.` 까지 치면 자동완성이 됩니다. 예 1에서 `None` 처리를 빼면 타입 검사 도구가 "`None` 에는 `.id` 가 없다"고 경고합니다.

**"왜" 도움이 되나**

- **문서 역할**: 주석은 코드와 어긋날 수 있지만 시그니처는 코드 자체입니다.
- **계층 사이의 계약**: 서비스가 CLI에 돌려주는 것이 [`Summary`](../budget_app/service.py#L72-L91 "sym:Summary") 라는 것이 정해져 있어서, CLI는 `s.income`, `s.over_budget` 을 믿고 씁니다.
- **실수를 일찍 발견**: 실행해 보기 전에 에디터가 알려 줍니다.

**한계도 함께 말하기**: 타입 힌트는 실행 중에 검사되지 않습니다. 그래서 외부에서 들어오는 값(사용자 입력, 파일, CSV)은 [`parse_*` 함수](../budget_app/models.py#L20-L66 "at:0,46:def parse_date(text: str) -&gt; str:")로 **직접** 검증합니다. 파일에서 읽은 dict도 [`Transaction.from_dict`](../budget_app/models.py#L85-L95 "sym:Transaction.from_dict") 에서 다시 검증합니다.

---

## 항목 4. 설계 판단

### 4-1. JSONL과 CSV 중 선택한 저장 포맷의 장단점을 비교하고, "왜" 그 포맷을 택했는지 근거를 말할 수 있는가?

> **쉬운 말로**: 둘 다 글자로 된 파일입니다. **CSV**는 표처럼 쉼표로 칸을 나누고(엑셀로 열림), **JSONL**은 한 줄마다 `{"이름": 값}` 꾸러미를 하나씩 적습니다. 차이는 "값의 종류를 기억하느냐"입니다. CSV는 모든 것이 글자라서 `15000` 이 숫자인지 글자인지 모르고, 태그 여러 개도 한 칸에 욱여넣어야 합니다. JSONL은 숫자는 숫자로, 목록은 목록으로 기억합니다.
>
> **용어 풀이**: [JSON·JSONL·CSV·스키마](QNA.md#g-data)
>
> **다른 방법과의 비교**: [선택 1. 저장 포맷](QNA.md#c-format)

**한 줄 답**: **JSONL**을 택했습니다. 결정적인 이유는 `tags` 가 리스트이고 `amount` 가 숫자라는 점입니다.

| 기준 | JSONL | CSV |
| --- | --- | --- |
| 리스트(`tags`) | `["meal","daily"]` 그대로 저장 | 쉼표로 합친 문자열로 바꿨다가 되돌려야 함 |
| 숫자(`amount`) | 숫자로 저장·복원 | 전부 문자열 → 읽을 때마다 `int()` 변환 |
| 메모 안의 쉼표·줄바꿈 | JSON이 이스케이프 → 항상 한 줄 | 따옴표 처리 필요, 값 안의 줄바꿈으로 "한 줄 = 한 건"이 깨질 수 있음 |
| 스트리밍 | 한 줄 = 한 건 | 대체로 가능 (위 줄바꿈 예외) |
| 추가(append) | 끝에 한 줄 | 끝에 한 줄 |
| 필드 추가 | 줄마다 키가 있어 옛 데이터와 공존 가능 | 헤더와 모든 행을 맞춰야 함 |
| 파일 크기 | 키 이름이 줄마다 반복 → 더 큼 | 헤더 한 번 → 더 작음 |
| 사람이 보기 | 텍스트 에디터로 읽을 수 있음 | **엑셀로 바로 열림** |

**근거**

1. 데이터 모델에 리스트가 있어서 CSV로는 변환 코드가 늘어납니다.
2. 한 줄이 반드시 한 건이라 "한 줄씩 읽는 제너레이터"와 정확히 맞습니다([`iter_records`](../budget_app/storage.py#L83-L103 "sym:JsonlFile.iter_records")).
3. 손상 시 "N번째 줄"을 정확히 짚어 줄 수 있습니다([L91-L102](../budget_app/storage.py#L91-L102 "at:1,10:record = json.loads(line)")).

**CSV의 장점은 버리지 않았습니다.** 엑셀에서 보고 싶을 때를 위해 import/export는 CSV로 제공합니다. 즉 **내부 저장은 타입이 보존되는 JSONL, 외부 교환은 누구나 여는 CSV**로 역할을 나눴습니다.

**JSONL의 단점도 인정하기**: 파일이 더 크고(키 반복), 엑셀로 바로 열 수 없습니다.

### 4-2. 거래가 10만 건으로 늘어난다면, 현재 구조에서 병목이 어디이며 "어떻게" 개선할지 설명할 수 있는가?

> **쉬운 말로**: 병목은 병의 좁은 목처럼 **전체 속도를 결정하는 가장 느린 부분**입니다. 지금 구조는 무엇을 하든 공책을 첫 쪽부터 끝까지 넘깁니다. 기록이 100건이면 순식간이지만 10만 건이면 매번 1초가 걸리고, 한 줄을 고치려고 공책 전체를 새로 옮겨 적으면 4초가 걸립니다. 해결책은 공책을 **달마다 한 권씩** 나누는 것입니다. 그러면 1월을 볼 때 1월 공책만 펴면 됩니다.
>
> **용어 풀이**: [병목·프로파일링·인덱스·데이터베이스](QNA.md#g-quality) · [스트리밍·메모리](QNA.md#g-python)
>
> **다른 방법과의 비교**: [선택 5. 파일을 고치는 방법](QNA.md#c-rewrite) · [선택 10. id 만들기](QNA.md#c-id)

**한 줄 답**: 메모리는 문제없고 **시간**이 병목입니다. 모든 명령이 파일을 처음부터 끝까지 읽고, update/delete는 파일 전체를 다시 쓰기 때문입니다.

**실측 (거래 10만 건, 14MB, 개발 PC 기준 근삿값)**

| 명령 | 소요 시간 | 파일을 읽는 횟수 |
| --- | --- | --- |
| `list --limit 10` | 약 0.9초 | 전체 1회 |
| `search --limit 10` | 약 0.9초 | 전체 1회 |
| `search` (limit 없음) | 약 1.8초 | 전체 1회 + 정렬 |
| `export --month` | 약 1.2초 | 전체 1회 |
| `add` | 약 0.9초 | 전체 1회 (다음 id를 찾느라) |
| `update` / `delete` | 약 4초 | 전체 2회 읽기 + 전체 1회 쓰기 |

**병목 4가지와 개선 방법**

| # | 병목 | 원인 코드 | 개선 방법 |
| --- | --- | --- | --- |
| 1 | 읽을 때마다 모든 줄의 날짜를 다시 검증 (프로파일 결과 읽기 시간의 절반 이상) | [`from_dict`](../budget_app/models.py#L85-L95 "sym:Transaction.from_dict") → [`parse_date`](../budget_app/models.py#L20-L28 "sym:parse_date") 의 `strptime` | 검증은 **쓸 때만** 하고, 읽을 때는 신뢰하거나 가벼운 형식 검사만 |
| 2 | `add` 한 건에 파일 전체 스캔 | [`next_number`](../budget_app/storage.py#L147-L150 "sym:TransactionRepository.next_number") | 마지막 번호를 작은 메타 파일에 저장 → 읽기 1줄로 끝 |
| 3 | update/delete가 한 건 때문에 14MB를 다시 씀 | [`_require_transaction`](../budget_app/service.py#L202-L206 "sym:BudgetService._require_transaction") + [`rewrite_each`](../budget_app/storage.py#L162-L181 "sym:TransactionRepository.rewrite_each") | **월별 파일 분할**(`transactions-2024-01.jsonl`) → 해당 월 파일만 다시 씀 |
| 4 | summary/search가 다른 달 데이터까지 읽음 | [`iter_filtered`](../budget_app/service.py#L247-L249 "sym:BudgetService.iter_filtered") | 월별 파일 분할 → 필요한 달만 읽음 |

**단계별 개선안**

1. **작은 수정**: 1번과 2번. 코드 몇 줄로 읽기 시간이 절반 이하가 됩니다.
2. **구조 변경**: 월별 파일 분할. summary·search·update·delete가 모두 "해당 월"만 다루게 됩니다. 가계부는 대부분 월 단위로 조회하므로 효과가 큽니다.
3. **그 이상**: 표준 라이브러리의 `sqlite3` 로 이전. 인덱스로 id·날짜 조회가 즉시 끝나고, 트랜잭션으로 원자성도 보장됩니다.

**구조 덕분에 가능한 점**: 위 변경은 모두 **저장소 계층 안**에서 끝납니다. 서비스는 `iter_all()`·`rewrite_each()` 만 부르므로 서비스와 CLI는 고칠 필요가 없습니다. 계층을 나눈 이유가 여기서 드러납니다.

**이미 대비된 부분**: 메모리. 10만 건에서도 스트리밍 명령은 1MB 미만입니다(3-1의 표).

### 4-3. import CSV에 일부 깨진 행이 섞이면, "어떻게" 처리해 사용자 신뢰를 지킬지(부분 성공/롤백/리포트) 설명할 수 있는가?

> **쉬운 말로**: 엑셀 파일 100줄을 가져오는데 3줄에 오타가 있다면 세 가지 방법이 있습니다. ① 전부 취소한다(롤백). ② 97줄만 넣고 아무 말도 안 한다. ③ 97줄을 넣고 **"3줄은 이런 이유로 빠졌습니다"** 라고 알려 준다. ②가 가장 위험합니다. 사용자는 100줄이 다 들어간 줄 알기 때문입니다. 이 프로그램은 ③을 택했습니다. 신뢰는 "틀리지 않는 것"보다 "무슨 일이 있었는지 숨기지 않는 것"에서 나옵니다.
>
> **용어 풀이**: [롤백·부분 성공](QNA.md#g-quality) · [검증](QNA.md#g-data)
>
> **다른 방법과의 비교**: [선택 13. 잘못된 행 처리](QNA.md#c-import)

**한 줄 답**: **부분 성공 + 리포트**를 택했습니다. 올바른 행은 등록하고, 깨진 행은 건너뛰며 **몇 행이 왜 빠졌는지**를 행 번호와 함께 모두 보여 줍니다.

**실제 출력**

```
[완료] imported=2, skipped=3
  - 건너뜀 3행: 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).
  - 건너뜀 4행: 등록되지 않은 카테고리입니다: 'nope'
  - 건너뜀 5행: 금액은 0보다 큰 양수여야 합니다.
```

**처리 방식을 두 단계로 나눴습니다**

| 문제의 범위 | 처리 | 이유 | 코드 |
| --- | --- | --- | --- |
| **파일 자체가 잘못됨** (파일 없음, 헤더에 필수 컬럼 없음, UTF-8 아님) | **전체 거부** — 한 건도 넣지 않음 | 형식이 틀린 파일은 어떤 행도 믿을 수 없음 | [L321-L322](../budget_app/service.py#L321-L322 "at:0,1:if not source.is_file():"), [L329-L334](../budget_app/service.py#L329-L334 "at:0,5:missing = [c for c in CSV_REQUIRED if c not in (reader.fieldnames or [])]"), [L353-L354](../budget_app/service.py#L353-L354 "at:0,1:except UnicodeDecodeError:") |
| **일부 행만 잘못됨** | **부분 성공** — 그 행만 건너뛰고 사유 기록 | 아래 참고 | [L335-L352](../budget_app/service.py#L335-L352 "at:0,17:for line_no, row in enumerate(reader, start=2):") |

**세 방식 비교와 선택 이유**

| 방식 | 장점 | 단점 |
| --- | --- | --- |
| 전체 롤백 (하나라도 틀리면 전부 취소) | 결과가 단순함 ("전부 아니면 전무") | 1000행 중 1행 오타로 999행을 못 넣음. 고치고 다시 돌려야 함 |
| 조용한 부분 성공 (틀린 행을 말없이 버림) | 편해 보임 | **데이터가 빠진 것을 사용자가 모름 → 신뢰를 잃는 가장 나쁜 방식** |
| **부분 성공 + 리포트 (선택)** | 넣을 수 있는 것은 넣고, 빠진 것은 정확히 알려 줌 | 사용자가 빠진 행을 따로 처리해야 함 |

가계부 CSV는 은행 내역처럼 사람이 손본 파일이 많아 한두 행의 오류가 흔합니다. 그때마다 전체를 거부하면 쓰기 불편합니다.

**신뢰를 지키는 장치 4가지**

1. **숫자가 맞아떨어짐**: `imported + skipped = CSV의 데이터 행 수`. 사용자가 검산할 수 있습니다([`ImportResult`](../budget_app/service.py#L94-L98 "sym:ImportResult")).
2. **행 번호가 엑셀과 같음**: 헤더가 1행이므로 [`start=2`](../budget_app/service.py#L335 "at:0,0:for line_no, row in enumerate(reader, start=2):") 부터 셉니다. 엑셀에서 그 행으로 바로 갈 수 있습니다.
3. **사유가 add와 같은 문구**: add와 같은 검증 함수(`parse_date`, `parse_amount`, `require_category`)를 [그대로 재사용](../budget_app/service.py#L337-L345 "at:2,6:type=parse_type(row[&quot;type&quot;] or &quot;&quot;),")하므로 규칙이 한 벌입니다. import로만 들어올 수 있는 잘못된 데이터가 없습니다.
4. **깨진 데이터는 저장 파일에 절대 들어가지 않음**: 검증을 통과해 `Transaction` 객체가 만들어진 뒤에만 [`add`](../budget_app/service.py#L350-L352 "at:2,0:result.imported += 1") 합니다.

**한계와 보완 (물으면 답하기)**

- *"import 도중에 프로그램이 꺼지면요?"* → 그때까지 넣은 행은 남습니다(행마다 append). 같은 파일을 다시 import하면 앞부분이 중복됩니다. 보완책: 실행 전에 `backup` 을 해 두거나, 개선한다면 임시 파일에 모아 한 번에 교체하는 방식으로 전체를 원자적으로 만들 수 있습니다.
- *"전부 아니면 전무가 필요하면요?"* → `--strict` 옵션을 추가해 건너뛴 행이 하나라도 있으면 아무것도 넣지 않게 할 수 있습니다. 검증과 저장이 분리돼 있어 "먼저 전부 검증 → 통과 시 저장"으로 바꾸기 쉽습니다. 현재는 구현하지 않았습니다.
- *"고친 행만 다시 넣으려면요?"* → 건너뛴 행 번호가 나오므로 그 행들만 모은 CSV를 만들어 다시 import하면 됩니다.

테스트: [test L201](../tests/test_app.py#L201-L220 "sym:AppTest.test_import_skips_bad_rows") — 5행 중 3행이 깨진 CSV로 `imported=2, skipped=3` 과, 헤더 불량·파일 없음의 전체 거부를 확인합니다.

---

## 항목 5. 보너스

4개 모두 구현했습니다.

| 보너스 | 구현 | 코드 | 테스트 | 시연 |
| --- | --- | --- | --- | --- |
| 1. 백업 + 복원 | `data/backups/<YYYYMMDD-HHMMSS>/` 에 모든 `.jsonl` 복사, `restore` 로 되돌리기 | [`backup_data`](../budget_app/storage.py#L242-L257 "sym:backup_data"), [`restore_data`](../budget_app/storage.py#L268-L281 "sym:restore_data"), [`restore`](../budget_app/service.py#L365-L378 "sym:BudgetService.restore") | [백업](../tests/test_app.py#L224-L232 "sym:AppTest.test_backup"), [복원](../tests/test_app.py#L234-L253 "sym:AppTest.test_restore_brings_back_backup_and_is_undoable") | `python -m budget_app backup` → `python -m budget_app restore` |
| 2. 반복 내역 | 규칙 등록 후 특정 월에 거래로 자동 생성 | [`add_recurring`](../budget_app/service.py#L380-L400 "sym:BudgetService.add_recurring"), [`apply_recurring`](../budget_app/service.py#L406-L442 "sym:BudgetService.apply_recurring") | [L306](../tests/test_app.py#L306-L316 "sym:AppTest.test_recurring_apply_is_idempotent_and_clamps_day") | `python -m budget_app recurring apply --month 2024-02` |
| 3. 표 정렬 출력 | 외부 라이브러리 없이 열 맞춤, 금액 오른쪽 정렬 | [formatter.py](../budget_app/formatter.py#L13-L38 "span:display_width..format_transactions") | list 출력으로 확인 | `python -m budget_app list` |
| 4. 저장 원자성 | 임시 파일 + `os.replace` | [`JsonlFile.rewrite`](../budget_app/storage.py#L114-L130 "sym:JsonlFile.rewrite") | [L137](../tests/test_app.py#L137-L138 "at:1,0:# 삭제 후에도 id 는 재사용되지 않고 최댓값 다음 번호가 나온다."), [L141](../tests/test_app.py#L141-L158 "sym:AppTest.test_missing_id_and_invalid_update_fail_without_change") | 항목 2-3 참고 |

**보너스별 설명 포인트**

- **백업과 복원**: `restore` 는 가장 최근 백업으로 되돌리고, `--name` 으로 특정 백업을, `--list` 로 목록을 고릅니다. 되돌리기 **전에 현재 상태를 자동으로 백업**하므로 잘못 복원해도 다시 돌아올 수 있습니다. 복원도 파일마다 임시 파일에 복사한 뒤 교체해, 도중에 중단돼도 반쯤 복사된 파일이 남지 않습니다. 같은 초에 두 번 백업해도 폴더 이름 뒤에 `-2` 를 붙여 기존 백업을 덮어쓰지 않습니다.
- **반복 내역 — 규칙 기반 생성과 예외 처리**
  - **중복 방지**: 생성된 거래에 `recurring:RC-0001` 태그를 붙입니다. 같은 달에 다시 apply하면 이 태그를 보고 건너뜁니다([L416-L429](../budget_app/service.py#L416-L429 "at:0,13:done = {")). 그래서 몇 번을 실행해도 결과가 같습니다.
  - **없는 날짜 보정**: 31일 규칙을 2월에 적용하면 [`min(rule.day, last_day)`](../budget_app/service.py#L433 "at:0,0:date=f&quot;{month}-{min(rule.day, last_day):02d}&quot;,  # 31일 규칙은 2월에 말일로 보정") 로 말일(28/29일)이 됩니다. 말일은 `calendar.monthrange` 로 구합니다.
- **표 정렬 — 한글 폭 문제**: 한글은 터미널에서 2칸을 차지합니다. `len()` 이나 `ljust()` 로 맞추면 한글이 있는 줄이 밀립니다. [`display_width`](../budget_app/formatter.py#L13-L15 "sym:display_width") 가 `unicodedata.east_asian_width` 로 실제 칸 수를 계산합니다. 포맷터를 별도 모듈로 분리해 CLI는 "무엇을 보여 줄지"만, 포맷터는 "어떻게 맞출지"만 압니다.
- **원자성**: 항목 2-3과 같은 내용입니다. 카테고리·예산 파일을 고칠 때도 같은 `rewrite` 를 씁니다.

---

## 부록. 평가 전 체크리스트

- [ ] `python --version` 이 3.10 이상인지 확인
- [ ] `python -m unittest discover -s tests -v` 가 `OK` 인지 확인
- [ ] `python demo.py --no-pause` 를 한 번 돌려 끝까지 오류 없이 도는지 확인
- [ ] 시연용 데이터 준비 — 깨끗한 폴더에서 시작하려면 모든 명령에 `--data-dir demo` 를 붙이기
- [ ] 거래 3~4건 미리 추가 (수입 1건, 지출 2건 이상, 태그·메모 포함)
- [ ] 종료 코드 확인 명령 연습 (`echo $LASTEXITCODE` 또는 `echo $?`)
- [ ] 아래 4개 코드를 열어 두기 — 질문이 가장 많이 나오는 곳입니다
  - [`iter_records`](../budget_app/storage.py#L83-L103 "sym:JsonlFile.iter_records") (제너레이터)
  - [`rewrite`](../budget_app/storage.py#L114-L130 "sym:JsonlFile.rewrite") (원자적 저장)
  - [`handle_errors`](../budget_app/decorators.py#L19-L40 "sym:handle_errors") (데코레이터)
  - [`import_csv`](../budget_app/service.py#L319-L355 "sym:BudgetService.import_csv") (부분 성공 + 리포트)

> 이 문서의 줄 번호 링크는 현재 코드 기준입니다. 코드를 수정하면 줄 번호가 달라질 수 있습니다.
