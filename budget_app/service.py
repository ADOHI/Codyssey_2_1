"""서비스 계층: 업무 규칙(검증, 검색, 요약, 가져오기/내보내기)을 담당한다.

화면 입출력(print/input)은 하지 않고, 저장소를 조합해 결과만 돌려준다.
"""

from __future__ import annotations

import calendar
import csv
import heapq
from collections import defaultdict
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Iterator

from .decorators import log_timed
from .errors import AppError
from .models import (
    Budget,
    Recurring,
    Transaction,
    parse_amount,
    parse_category_name,
    parse_date,
    parse_month,
    parse_tags,
    parse_type,
)
from .storage import (
    BudgetStore,
    CategoryStore,
    RecurringStore,
    TransactionRepository,
    backup_data,
    list_backups,
    restore_data,
)

CSV_COLUMNS = ["date", "type", "category", "amount", "memo", "tags"]
CSV_REQUIRED = CSV_COLUMNS[:4]


@dataclass
class SearchFilter:
    date_from: str | None = None
    date_to: str | None = None
    month: str | None = None
    category: str | None = None
    type: str | None = None
    q: str | None = None
    tag: str | None = None

    def matches(self, tx: Transaction) -> bool:
        # 날짜가 YYYY-MM-DD 문자열이라 문자열 비교가 곧 날짜 비교다.
        if self.date_from and tx.date < self.date_from:
            return False
        if self.date_to and tx.date > self.date_to:
            return False
        if self.month and not tx.date.startswith(self.month):
            return False
        if self.category and tx.category != self.category:
            return False
        if self.type and tx.type != self.type:
            return False
        if self.q and self.q.lower() not in tx.memo.lower():
            return False
        if self.tag and self.tag not in tx.tags:
            return False
        return True


@dataclass
class Summary:
    month: str
    count: int = 0
    income: int = 0
    expense: int = 0
    top: list[tuple[str, int]] = field(default_factory=list)
    budget: int | None = None

    @property
    def balance(self) -> int:
        return self.income - self.expense

    @property
    def usage_percent(self) -> float | None:
        return None if not self.budget else self.expense / self.budget * 100

    @property
    def over_budget(self) -> bool:
        return self.budget is not None and self.expense > self.budget


@dataclass
class ImportResult:
    imported: int = 0
    skipped: int = 0
    reasons: list[str] = field(default_factory=list)


def _newest_first(tx: Transaction) -> tuple[str, str]:
    return (tx.date, tx.id)


class BudgetService:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.transactions = TransactionRepository(data_dir)
        self.categories = CategoryStore(data_dir)
        self.budgets = BudgetStore(data_dir)
        self.recurring = RecurringStore(data_dir)

    def initialize(self) -> list[str]:
        """저장 파일이 없으면 만든다. 사용자에게 알릴 안내 문구를 돌려준다."""
        notes: list[str] = []
        stores = (self.transactions, self.categories, self.budgets, self.recurring)
        interrupted = [s.file.path.name for s in stores if s.file.clear_stale_tmp()]
        if interrupted:
            notes.append(
                f"이전 수정 작업이 중단되어 반영되지 않았습니다 ({', '.join(interrupted)}). "
                "데이터는 수정 전 상태 그대로입니다. 필요하면 마지막 명령을 다시 실행하세요."
            )
        for store in stores:
            fragment = store.file.repair_torn_tail()
            if fragment is not None:
                notes.append(
                    f"{store.file.path.name} 의 마지막 줄이 저장 도중 끊겨 있어 떼어 냈습니다: {fragment[:80]!r}. "
                    "다른 데이터는 그대로입니다. 마지막에 추가하던 내역은 저장되지 않았으니 다시 입력하세요."
                )
        created = [s.file.path.name for s in (self.transactions, self.budgets, self.recurring) if s.file.ensure()]
        if self.categories.ensure():
            notes.append(f"기본 카테고리를 생성했습니다: {', '.join(self.categories.names())}")
        if created:
            notes.append(f"저장 파일을 생성했습니다: {self.data_dir} ({', '.join(created)})")
        return notes

    # ---------- 카테고리 ----------

    def require_category(self, name: str) -> str:
        name = name.strip().lower()
        names = self.categories.names()
        if name not in names:
            raise AppError(
                f"등록되지 않은 카테고리입니다: {name!r}",
                f"사용 가능: {', '.join(names)} / 새로 만들려면 category add",
            )
        return name

    def add_category(self, name: str) -> str:
        name = parse_category_name(name)
        if name in self.categories.names():
            raise AppError(f"이미 있는 카테고리입니다: {name}", "category list 로 목록을 확인하세요.")
        self.categories.add(name)
        return name

    @log_timed
    def remove_category(self, name: str, replace_with: str | None = None) -> int:
        """카테고리를 삭제한다. 사용 중이면 대체 카테고리가 있어야 한다. 옮긴 건수 반환."""
        name = self.require_category(name)
        used = sum(1 for tx in self.transactions.iter_all() if tx.category == name)
        rules = [r for r in self.recurring.all() if r.category == name]
        if (used or rules) and not replace_with:
            raise AppError(
                f"'{name}' 카테고리는 거래 {used}건, 반복 내역 {len(rules)}건에서 사용 중이라 삭제할 수 없습니다.",
                f"대체 카테고리를 지정하세요: category remove --name {name} --replace-with <카테고리>",
            )
        if replace_with:
            target = self.require_category(replace_with)
            if target == name:
                raise AppError("대체 카테고리는 삭제할 카테고리와 달라야 합니다.", "다른 카테고리를 지정하세요.")
            if used:
                self.transactions.rewrite_each(
                    lambda tx: replace(tx, category=target) if tx.category == name else tx
                )
            if rules:
                self.recurring.file.rewrite(
                    {**r.__dict__, "category": target if r.category == name else r.category}
                    for r in self.recurring.all()
                )
        if len(self.categories.names()) == 1:
            raise AppError("마지막 카테고리는 삭제할 수 없습니다.", "다른 카테고리를 먼저 추가하세요.")
        self.categories.remove(name)
        return used

    # ---------- 거래 CRUD ----------

    def add_transaction(
        self, date: str, type_: str, category: str, amount: str | int, memo: str = "", tags: str = ""
    ) -> Transaction:
        tx = Transaction(
            id=self.transactions.format_id(self.transactions.next_number()),
            type=parse_type(type_),
            date=parse_date(date),
            amount=parse_amount(amount),
            category=self.require_category(category),
            memo=memo.strip(),
            tags=parse_tags(tags),
        )
        self.transactions.add(tx)
        return tx

    def _require_transaction(self, tx_id: str) -> Transaction:
        tx = self.transactions.get(tx_id)
        if tx is None:
            raise AppError(f"없는 데이터입니다: id={tx_id}", "list 또는 search 로 id 를 확인하세요.")
        return tx

    @log_timed
    def update_transaction(
        self,
        tx_id: str,
        date: str | None = None,
        type_: str | None = None,
        category: str | None = None,
        amount: str | int | None = None,
        memo: str | None = None,
        tags: str | None = None,
    ) -> Transaction:
        current = self._require_transaction(tx_id)
        changes: dict[str, object] = {}
        if date is not None:
            changes["date"] = parse_date(date)
        if type_ is not None:
            changes["type"] = parse_type(type_)
        if category is not None:
            changes["category"] = self.require_category(category)
        if amount is not None:
            changes["amount"] = parse_amount(amount)
        if memo is not None:
            changes["memo"] = memo.strip()
        if tags is not None:
            changes["tags"] = parse_tags(tags)
        if not changes:
            raise AppError("수정할 항목이 없습니다.", "예: update --id TX-000001 --amount 20000")
        updated = replace(current, **changes)
        self.transactions.rewrite_each(lambda tx: updated if tx.id == tx_id else tx)
        return updated

    @log_timed
    def delete_transaction(self, tx_id: str) -> Transaction:
        tx = self._require_transaction(tx_id)
        self.transactions.rewrite_each(lambda t: None if t.id == tx_id else t)
        return tx

    # ---------- 조회 ----------

    def iter_filtered(self, flt: SearchFilter) -> Iterator[Transaction]:
        """조건에 맞는 거래만 흘려보내는 제너레이터."""
        return (tx for tx in self.transactions.iter_all() if flt.matches(tx))

    @log_timed
    def recent(self, limit: int, flt: SearchFilter | None = None) -> list[Transaction]:
        """최신순 상위 limit 건. 힙으로 limit 건만 메모리에 유지한다."""
        source = self.iter_filtered(flt) if flt else self.transactions.iter_all()
        return heapq.nlargest(limit, source, key=_newest_first)

    @log_timed
    def search(self, flt: SearchFilter, limit: int | None = None) -> list[Transaction]:
        if limit:
            return self.recent(limit, flt)
        # ponytail: 최신순 정렬 때문에 '조건에 맞는 결과'는 메모리에 올린다(파일 전체는 아님).
        # 결과가 아주 커지면 --limit 을 쓰거나 날짜별 파일 분할로 바꾼다.
        return sorted(self.iter_filtered(flt), key=_newest_first, reverse=True)

    @log_timed
    def summarize(self, month: str, top: int = 3) -> Summary:
        month = parse_month(month)
        summary = Summary(month=month)
        by_category: defaultdict[str, int] = defaultdict(int)
        for tx in self.iter_filtered(SearchFilter(month=month)):
            summary.count += 1
            if tx.type == "income":
                summary.income += tx.amount
            else:
                summary.expense += tx.amount
                by_category[tx.category] += tx.amount
        summary.top = heapq.nlargest(top, by_category.items(), key=lambda kv: (kv[1], kv[0]))
        budget = self.budgets.get(month)
        summary.budget = budget.amount if budget else None
        return summary

    # ---------- 예산 ----------

    def set_budget(self, month: str, amount: str | int) -> Budget:
        budget = Budget(month=parse_month(month), amount=parse_amount(amount))
        self.budgets.set(budget)
        return budget

    # ---------- CSV 가져오기/내보내기 ----------

    @staticmethod
    def build_period_filter(month: str | None, date_from: str | None, date_to: str | None) -> SearchFilter:
        flt = SearchFilter(
            month=parse_month(month) if month else None,
            date_from=parse_date(date_from) if date_from else None,
            date_to=parse_date(date_to) if date_to else None,
        )
        if flt.date_from and flt.date_to and flt.date_from > flt.date_to:
            raise AppError("--from 날짜가 --to 날짜보다 늦습니다.", "기간의 시작과 끝을 확인하세요.")
        return flt

    @log_timed
    def export_csv(self, out: Path, flt: SearchFilter) -> int:
        if not (flt.month or flt.date_from or flt.date_to):
            raise AppError(
                "내보낼 기간 조건이 없습니다.",
                "--month YYYY-MM 또는 --from YYYY-MM-DD --to YYYY-MM-DD 를 지정하세요.",
            )
        rows = sorted(self.iter_filtered(flt), key=_newest_first)
        if out.parent != Path(""):
            out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)
            for tx in rows:
                writer.writerow([tx.date, tx.type, tx.category, tx.amount, tx.memo, ",".join(tx.tags)])
        return len(rows)

    @log_timed
    def import_csv(self, source: Path) -> ImportResult:
        if not source.is_file():
            raise AppError(f"CSV 파일을 찾을 수 없습니다: {source}", "--from 경로를 확인하세요.")
        result = ImportResult()
        number = self.transactions.next_number()
        try:
            # utf-8-sig: 엑셀이 붙이는 BOM 이 있어도 없어도 읽는다.
            with source.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                missing = [c for c in CSV_REQUIRED if c not in (reader.fieldnames or [])]
                if missing:
                    raise AppError(
                        f"CSV 헤더에 필수 컬럼이 없습니다: {', '.join(missing)}",
                        f"첫 줄은 {','.join(CSV_COLUMNS)} 형식이어야 합니다.",
                    )
                for line_no, row in enumerate(reader, start=2):
                    try:
                        tx = Transaction(
                            id=self.transactions.format_id(number),
                            type=parse_type(row["type"] or ""),
                            date=parse_date(row["date"] or ""),
                            amount=parse_amount(row["amount"] or ""),
                            category=self.require_category(row["category"] or ""),
                            memo=(row.get("memo") or "").strip(),
                            tags=parse_tags(row.get("tags") or ""),
                        )
                    except AppError as exc:
                        result.skipped += 1
                        result.reasons.append(f"{line_no}행: {exc.message}")
                        continue
                    self.transactions.add(tx)
                    number += 1
                    result.imported += 1
        except UnicodeDecodeError:
            raise AppError("CSV 파일이 UTF-8 인코딩이 아닙니다.", "UTF-8 로 다시 저장한 뒤 시도하세요.") from None
        return result

    # ---------- 보너스: 백업, 반복 내역 ----------

    def backup(self) -> tuple[Path, int]:
        return backup_data(self.data_dir)

    def backups(self) -> list[str]:
        return list_backups(self.data_dir)

    def restore(self, name: str | None = None) -> tuple[str, Path, int]:
        """백업으로 되돌린다. name 이 없으면 가장 최근 백업.

        되돌리기 전에 현재 상태를 먼저 백업해, 복원 자체도 취소할 수 있게 한다.
        반환값: (복원한 백업 이름, 복원 직전 상태를 담은 백업 폴더, 복원한 파일 수)
        """
        names = self.backups()
        if not names:
            raise AppError("복원할 백업이 없습니다.", "먼저 backup 명령으로 백업을 만드세요.")
        target = name or names[-1]
        if target not in names:
            raise AppError(f"없는 백업입니다: {target}", "restore --list 로 백업 이름을 확인하세요.")
        safety, _ = backup_data(self.data_dir)
        return target, safety, restore_data(self.data_dir, target)

    def add_recurring(
        self, day: str | int, type_: str, category: str, amount: str | int, memo: str = "", tags: str = ""
    ) -> Recurring:
        try:
            day_no = int(str(day).strip())
        except ValueError:
            day_no = 0
        if not 1 <= day_no <= 31:
            raise AppError("반복 일자는 1~31 사이의 정수여야 합니다.", "예: 25 (매월 25일)")
        numbers = (int(r.id[3:]) for r in self.recurring.all() if r.id[3:].isdigit())
        rule = Recurring(
            id=f"RC-{max(numbers, default=0) + 1:04d}",
            type=parse_type(type_),
            day=day_no,
            amount=parse_amount(amount),
            category=self.require_category(category),
            memo=memo.strip(),
            tags=parse_tags(tags),
        )
        self.recurring.add(rule)
        return rule

    def remove_recurring(self, rule_id: str) -> None:
        if not self.recurring.remove(rule_id):
            raise AppError(f"없는 반복 내역입니다: id={rule_id}", "recurring list 로 id 를 확인하세요.")

    @log_timed
    def apply_recurring(self, month: str) -> tuple[list[Transaction], int]:
        """해당 월에 반복 내역을 거래로 생성한다. 이미 만든 규칙은 건너뛴다.

        중복 판별은 생성된 거래에 붙이는 'recurring:<규칙 id>' 태그로 한다.
        반환값: (새로 만든 거래, 건너뛴 규칙 수)
        """
        month = parse_month(month)
        year, mon = int(month[:4]), int(month[5:])
        last_day = calendar.monthrange(year, mon)[1]
        done = {
            tag
            for tx in self.iter_filtered(SearchFilter(month=month))
            for tag in tx.tags
            if tag.startswith("recurring:")
        }
        created: list[Transaction] = []
        skipped = 0
        number = self.transactions.next_number()
        for rule in self.recurring.all():
            marker = f"recurring:{rule.id}"
            if marker in done:
                skipped += 1
                continue
            tx = Transaction(
                id=self.transactions.format_id(number),
                type=rule.type,
                date=f"{month}-{min(rule.day, last_day):02d}",  # 31일 규칙은 2월에 말일로 보정
                amount=rule.amount,
                category=self.require_category(rule.category),
                memo=rule.memo,
                tags=[*rule.tags, marker],
            )
            self.transactions.add(tx)
            created.append(tx)
            number += 1
        return created, skipped
