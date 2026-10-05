"""CLI 계층: 명령어 해석(argparse), 대화형 입력(input), 화면 출력(print)만 담당한다."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Callable, Sequence, TypeVar

from .decorators import handle_errors
from .errors import AppError
from .formatter import format_table, format_transactions
from .models import TYPES, parse_amount, parse_category_name, parse_date, parse_type
from .service import CSV_COLUMNS, BudgetService, SearchFilter

T = TypeVar("T")

DEFAULT_LIMIT = 10


# ---------- 입력 도우미 ----------

def read_line(prompt: str) -> str:
    # PowerShell 파이프는 입력 맨 앞에 BOM을 붙이므로 제거한다.
    return input(prompt).lstrip("\ufeff")


def ask(prompt: str, parse: Callable[[str], T]) -> T:
    """올바른 값이 들어올 때까지 다시 묻는다."""
    while True:
        try:
            return parse(read_line(prompt))
        except AppError as exc:
            print(f"[오류] {exc.message}")
            if exc.hint:
                print(f"[힌트] {exc.hint}")


def positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        value = 0
    if value <= 0:
        raise argparse.ArgumentTypeError(f"1 이상의 정수여야 합니다: {text!r}")
    return value


# ---------- 명령 핸들러 ----------

def cmd_add(svc: BudgetService, args: argparse.Namespace) -> None:
    date = ask("날짜(YYYY-MM-DD): ", parse_date)
    type_ = ask("타입(income/expense): ", parse_type)
    category = ask(f"카테고리({', '.join(svc.categories.names())}): ", svc.require_category)
    amount = ask("금액(양수): ", parse_amount)
    memo = read_line("메모(선택): ")
    tags = read_line("태그(쉼표로 구분, 없으면 엔터): ")
    tx = svc.add_transaction(date, type_, category, amount, memo, tags)
    print(f"[저장 완료] id={tx.id}")


def cmd_list(svc: BudgetService, args: argparse.Namespace) -> None:
    _print_transactions(svc.recent(args.limit))


def cmd_search(svc: BudgetService, args: argparse.Namespace) -> None:
    flt = svc.build_period_filter(None, args.date_from, args.date_to)
    flt.category = svc.require_category(args.category) if args.category else None
    flt.type, flt.q, flt.tag = args.type, args.q, args.tag
    _print_transactions(svc.search(flt, args.limit))


def _print_transactions(transactions: list) -> None:
    if not transactions:
        print("[데이터 없음] 조건에 맞는 거래가 없습니다.")
        return
    print(format_transactions(transactions))
    print(f"({len(transactions)}건)")


def cmd_summary(svc: BudgetService, args: argparse.Namespace) -> None:
    s = svc.summarize(args.month, args.top)
    if s.count == 0:
        print(f"[데이터 없음] {s.month} 에 해당하는 거래가 없습니다.")
        if s.budget is not None:
            print(f"예산: {s.budget}원 (사용률 0.0%)")
        return
    print(f"[{s.month} 요약] 거래 {s.count}건")
    print(f"총 수입: {s.income}원")
    print(f"총 지출: {s.expense}원")
    print(f"잔액: {s.balance}원")
    if s.budget is not None:
        print(f"예산: {s.budget}원 (사용률 {s.usage_percent:.1f}%)")
        if s.over_budget:
            print(f"[경고] 예산을 {s.expense - s.budget}원 초과했습니다!")
    else:
        print("예산: 미설정 (budget set --month ... --amount ... 로 설정)")
    print(f"\n지출 TOP {args.top}")
    if not s.top:
        print("(지출 내역 없음)")
    for rank, (category, total) in enumerate(s.top, start=1):
        print(f"{rank}) {category} {total}원")


def cmd_budget_set(svc: BudgetService, args: argparse.Namespace) -> None:
    budget = svc.set_budget(args.month, args.amount)
    print(f"[저장 완료] {budget.month} 예산 {budget.amount}원")


def cmd_budget_show(svc: BudgetService, args: argparse.Namespace) -> None:
    budgets = [b for b in svc.budgets.iter_all() if not args.month or b.month == args.month]
    if not budgets:
        print("[데이터 없음] 설정된 예산이 없습니다.")
        return
    for b in budgets:
        print(f"{b.month} 예산 {b.amount}원")


def cmd_category_add(svc: BudgetService, args: argparse.Namespace) -> None:
    name = args.name if args.name is not None else ask("카테고리명: ", parse_category_name)
    print(f"[저장 완료] category={svc.add_category(name)}")


def cmd_category_list(svc: BudgetService, args: argparse.Namespace) -> None:
    for name in svc.categories.names():
        print(f"- {name}")


def cmd_category_remove(svc: BudgetService, args: argparse.Namespace) -> None:
    name = args.name if args.name is not None else ask("삭제할 카테고리명: ", parse_category_name)
    moved = svc.remove_category(name, args.replace_with)
    extra = f" (거래 {moved}건을 {args.replace_with} 로 이동)" if args.replace_with else ""
    print(f"[삭제 완료] category={name.strip().lower()}{extra}")


def cmd_update(svc: BudgetService, args: argparse.Namespace) -> None:
    tx = svc.update_transaction(
        args.id, args.date, args.type, args.category, args.amount, args.memo, args.tags
    )
    print(f"[수정 완료] id={tx.id}")
    print(format_transactions([tx]))


def cmd_delete(svc: BudgetService, args: argparse.Namespace) -> None:
    tx = svc.delete_transaction(args.id)
    print(f"[삭제 완료] id={tx.id} ({tx.date} {tx.category} {tx.amount}원)")


def cmd_import(svc: BudgetService, args: argparse.Namespace) -> None:
    result = svc.import_csv(Path(args.source))
    print(f"[완료] imported={result.imported}, skipped={result.skipped}")
    for reason in result.reasons:
        print(f"  - 건너뜀 {reason}")


def cmd_export(svc: BudgetService, args: argparse.Namespace) -> None:
    flt = svc.build_period_filter(args.month, args.date_from, args.date_to)
    count = svc.export_csv(Path(args.out), flt)
    print(f"[완료] {args.out} ({count} records)")


def cmd_backup(svc: BudgetService, args: argparse.Namespace) -> None:
    target, count = svc.backup()
    print(f"[백업 완료] {target} ({count} files)")


def cmd_restore(svc: BudgetService, args: argparse.Namespace) -> None:
    if args.list:
        names = svc.backups()
        if not names:
            print("[데이터 없음] 백업이 없습니다. (backup 명령으로 생성)")
        for name in names:
            print(f"- {name}")
        return
    name, safety, count = svc.restore(args.name)
    print(f"[복원 완료] {name} ({count} files)")
    print(f"[안내] 복원 직전 상태는 {safety.name} 으로 백업했습니다. (되돌리려면 restore --name {safety.name})")


def cmd_recurring_add(svc: BudgetService, args: argparse.Namespace) -> None:
    def parse_day(text: str) -> int:
        if not text.strip().isdigit() or not 1 <= int(text) <= 31:
            raise AppError("반복 일자는 1~31 사이의 정수여야 합니다.", "예: 25 (매월 25일)")
        return int(text)

    day = ask("매월 며칠(1~31): ", parse_day)
    type_ = ask("타입(income/expense): ", parse_type)
    category = ask(f"카테고리({', '.join(svc.categories.names())}): ", svc.require_category)
    amount = ask("금액(양수): ", parse_amount)
    memo = read_line("메모(선택): ")
    tags = read_line("태그(쉼표로 구분, 없으면 엔터): ")
    rule = svc.add_recurring(day, type_, category, amount, memo, tags)
    print(f"[저장 완료] id={rule.id}")


def cmd_recurring_list(svc: BudgetService, args: argparse.Namespace) -> None:
    rules = svc.recurring.all()
    if not rules:
        print("[데이터 없음] 등록된 반복 내역이 없습니다.")
        return
    rows = [[r.id, f"매월 {r.day}일", r.type, r.category, f"{r.amount:,}", r.memo, ",".join(r.tags)] for r in rules]
    print(format_table(["ID", "DAY", "TYPE", "CATEGORY", "AMOUNT", "MEMO", "TAGS"], rows, right_align=(4,)))


def cmd_recurring_remove(svc: BudgetService, args: argparse.Namespace) -> None:
    svc.remove_recurring(args.id)
    print(f"[삭제 완료] id={args.id}")


def cmd_recurring_apply(svc: BudgetService, args: argparse.Namespace) -> None:
    created, skipped = svc.apply_recurring(args.month)
    print(f"[완료] created={len(created)}, skipped={skipped} (이미 생성된 규칙은 건너뜀)")
    if created:
        print(format_transactions(created))


# ---------- argparse 구성 ----------

def build_parser() -> argparse.ArgumentParser:
    # 공통 옵션은 명령 앞/뒤 어디에 써도 되도록 부모 파서로 공유한다.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--data-dir", default=argparse.SUPPRESS, help="저장 폴더 (기본: ./data)")
    common.add_argument("--verbose", action="store_true", default=argparse.SUPPRESS, help="실행 로그/시간 출력")

    parser = argparse.ArgumentParser(
        prog="python -m budget_app",
        description="파일(JSONL) 기반 콘솔 가계부",
        epilog="각 명령의 사용법: python -m budget_app <command> --help",
    )
    parser.add_argument("--data-dir", default="./data", help="저장 폴더 (기본: ./data)")
    parser.add_argument("--verbose", action="store_true", help="실행 로그/시간 출력")
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    def command(parent, name: str, handler: Callable, help_: str) -> argparse.ArgumentParser:
        p = parent.add_parser(name, help=help_, description=help_, parents=[common])
        p.set_defaults(handler=handler)
        return p

    def group(name: str, help_: str):
        p = sub.add_parser(name, help=help_, description=help_, parents=[common])
        return p.add_subparsers(dest="action", required=True, metavar="<action>")

    command(sub, "add", cmd_add, "거래 추가 (대화형 입력)")

    p = command(sub, "list", cmd_list, "거래 목록 (최신순)")
    p.add_argument("--limit", type=positive_int, default=DEFAULT_LIMIT, help=f"출력 건수 (기본 {DEFAULT_LIMIT})")

    p = command(sub, "search", cmd_search, "조건 검색 (최신순)")
    p.add_argument("--from", dest="date_from", metavar="YYYY-MM-DD", help="시작 날짜(포함)")
    p.add_argument("--to", dest="date_to", metavar="YYYY-MM-DD", help="끝 날짜(포함)")
    p.add_argument("--category", help="카테고리")
    p.add_argument("--type", choices=TYPES, help="income 또는 expense")
    p.add_argument("--q", help="메모에 포함된 키워드")
    p.add_argument("--tag", help="태그(정확히 일치)")
    p.add_argument("--limit", type=positive_int, help="최대 출력 건수 (기본: 전체)")

    p = command(sub, "summary", cmd_summary, "월별 요약")
    p.add_argument("--month", required=True, metavar="YYYY-MM", help="대상 월")
    p.add_argument("--top", type=positive_int, default=3, help="카테고리별 지출 상위 N개 (기본 3)")

    budget = group("budget", "예산 설정/조회")
    p = command(budget, "set", cmd_budget_set, "월 예산 저장")
    p.add_argument("--month", required=True, metavar="YYYY-MM", help="대상 월")
    p.add_argument("--amount", required=True, help="예산 금액(양수)")
    p = command(budget, "show", cmd_budget_show, "저장된 예산 조회")
    p.add_argument("--month", metavar="YYYY-MM", help="특정 월만 조회")

    category = group("category", "카테고리 관리")
    p = command(category, "add", cmd_category_add, "카테고리 추가 (대화형, --name 으로 생략 가능)")
    p.add_argument("--name", help="카테고리명")
    command(category, "list", cmd_category_list, "카테고리 목록")
    p = command(category, "remove", cmd_category_remove, "카테고리 삭제 (사용 중이면 --replace-with 필요)")
    p.add_argument("--name", help="삭제할 카테고리명")
    p.add_argument("--replace-with", help="사용 중인 거래를 옮길 대체 카테고리")

    p = command(sub, "update", cmd_update, "거래 수정 (옵션 기반: 지정한 필드만 변경)")
    p.add_argument("--id", required=True, help="거래 id (예: TX-000001)")
    p.add_argument("--date", metavar="YYYY-MM-DD")
    p.add_argument("--type", choices=TYPES)
    p.add_argument("--category")
    p.add_argument("--amount")
    p.add_argument("--memo")
    p.add_argument("--tags", help='쉼표 구분. 비우려면 --tags ""')

    p = command(sub, "delete", cmd_delete, "거래 삭제")
    p.add_argument("--id", required=True, help="거래 id (예: TX-000001)")

    p = command(sub, "import", cmd_import, f"CSV 가져오기 (헤더: {','.join(CSV_COLUMNS)})")
    p.add_argument("--from", dest="source", required=True, metavar="CSV", help="가져올 CSV 파일")

    p = command(sub, "export", cmd_export, "CSV 내보내기 (--month 또는 --from/--to 중 하나 이상 필수)")
    p.add_argument("--out", required=True, metavar="CSV", help="저장할 CSV 파일")
    p.add_argument("--month", metavar="YYYY-MM")
    p.add_argument("--from", dest="date_from", metavar="YYYY-MM-DD")
    p.add_argument("--to", dest="date_to", metavar="YYYY-MM-DD")

    command(sub, "backup", cmd_backup, "데이터 파일을 타임스탬프 폴더로 백업")

    p = command(sub, "restore", cmd_restore, "백업으로 되돌리기 (기본: 가장 최근 백업)")
    p.add_argument("--name", help="백업 이름 (예: 20240115-093000). 생략하면 가장 최근 백업")
    p.add_argument("--list", action="store_true", help="백업 목록만 출력")

    recurring = group("recurring", "반복 내역(월급/월세 등) 관리")
    command(recurring, "add", cmd_recurring_add, "반복 내역 등록 (대화형)")
    command(recurring, "list", cmd_recurring_list, "반복 내역 목록")
    p = command(recurring, "remove", cmd_recurring_remove, "반복 내역 삭제")
    p.add_argument("--id", required=True, help="반복 내역 id (예: RC-0001)")
    p = command(recurring, "apply", cmd_recurring_apply, "특정 월에 반복 내역을 거래로 생성")
    p.add_argument("--month", required=True, metavar="YYYY-MM")

    return parser


@handle_errors
def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format="[로그] %(message)s")
    svc = BudgetService(Path(args.data_dir))
    for note in svc.initialize():
        print(f"[안내] {note}")
    args.handler(svc, args)
    return 0
