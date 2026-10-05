"""저장소 계층: JSONL 파일 읽기/쓰기만 담당한다.

- 읽기: 한 줄씩 yield 하는 제너레이터(파일 전체를 메모리에 올리지 않는다)
- 쓰기: 추가는 append, 수정/삭제는 임시 파일에 다시 쓴 뒤 os.replace 로 원자적 교체
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator

from .errors import AppError
from .models import DEFAULT_CATEGORIES, Budget, Recurring, Transaction


class JsonlFile:
    """JSONL(한 줄 = JSON 객체 1개) 파일 하나를 다루는 공통 도구."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def ensure(self) -> bool:
        """파일이 없으면 빈 파일을 만든다. 새로 만들었으면 True."""
        if self.path.exists():
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch()
        return True

    def iter_records(self) -> Iterator[dict[str, Any]]:
        """한 줄씩 읽어 dict 로 yield 한다(스트리밍)."""
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    raise AppError(
                        f"저장 파일이 손상되었습니다: {self.path} {line_no}번째 줄",
                        "해당 줄을 직접 고치거나 backup 폴더의 백업으로 복구하세요.",
                    ) from None
                if not isinstance(record, dict):
                    raise AppError(
                        f"저장 파일 형식이 올바르지 않습니다: {self.path} {line_no}번째 줄",
                        "각 줄은 JSON 객체({ ... })여야 합니다.",
                    )
                yield record

    def append(self, record: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def rewrite(self, records: Iterable[dict[str, Any]]) -> None:
        """임시 파일에 전부 쓴 뒤 rename 으로 교체한다(원자적 저장).

        쓰는 도중 프로그램이 죽어도 원본 파일은 그대로 남는다.
        records 가 원본을 읽는 제너레이터여도 한 줄씩 흘려보내므로 메모리를 아낀다.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        try:
            with tmp.open("w", encoding="utf-8") as f:
                for record in records:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.path)
        finally:
            tmp.unlink(missing_ok=True)


class TransactionRepository:
    def __init__(self, data_dir: Path) -> None:
        self.file = JsonlFile(data_dir / "transactions.jsonl")

    def iter_all(self) -> Iterator[Transaction]:
        for record in self.file.iter_records():
            try:
                yield Transaction.from_dict(record)
            except (KeyError, TypeError) as exc:
                raise AppError(
                    f"거래 데이터에 필수 필드가 없습니다: {exc}",
                    f"{self.file.path} 파일을 확인하세요.",
                ) from None

    def next_number(self) -> int:
        """가장 큰 id 번호 + 1 (스트리밍으로 한 번 훑는다)."""
        numbers = (int(tx.id[3:]) for tx in self.iter_all() if tx.id[3:].isdigit())
        return max(numbers, default=0) + 1

    @staticmethod
    def format_id(number: int) -> str:
        return f"TX-{number:06d}"

    def add(self, tx: Transaction) -> None:
        self.file.append(tx.to_dict())

    def get(self, tx_id: str) -> Transaction | None:
        return next((tx for tx in self.iter_all() if tx.id == tx_id), None)

    def rewrite_each(self, fn: Callable[[Transaction], Transaction | None]) -> int:
        """모든 거래에 fn 을 적용해 파일을 다시 쓴다. None 을 돌려주면 그 거래는 삭제.

        반환값: 바뀌거나 삭제된 건수.
        """
        changed = 0

        def transformed() -> Iterator[dict[str, Any]]:
            nonlocal changed
            for tx in self.iter_all():
                new = fn(tx)
                if new is None:
                    changed += 1
                    continue
                if new != tx:
                    changed += 1
                yield new.to_dict()

        self.file.rewrite(transformed())
        return changed


class CategoryStore:
    def __init__(self, data_dir: Path) -> None:
        self.file = JsonlFile(data_dir / "categories.jsonl")

    def ensure(self) -> bool:
        """파일이 없거나 비어 있으면 기본 카테고리를 만든다(안 A). 만들었으면 True."""
        self.file.ensure()
        if self.names():
            return False
        self.file.rewrite({"name": name} for name in DEFAULT_CATEGORIES)
        return True

    def names(self) -> list[str]:
        return [str(r["name"]) for r in self.file.iter_records() if "name" in r]

    def add(self, name: str) -> None:
        self.file.append({"name": name})

    def remove(self, name: str) -> None:
        self.file.rewrite({"name": n} for n in self.names() if n != name)


class BudgetStore:
    def __init__(self, data_dir: Path) -> None:
        self.file = JsonlFile(data_dir / "budgets.jsonl")

    def iter_all(self) -> Iterator[Budget]:
        for r in self.file.iter_records():
            yield Budget(month=str(r["month"]), amount=int(r["amount"]))

    def get(self, month: str) -> Budget | None:
        return next((b for b in self.iter_all() if b.month == month), None)

    def set(self, budget: Budget) -> None:
        others = [b for b in self.iter_all() if b.month != budget.month]
        ordered = sorted(others + [budget], key=lambda b: b.month)
        self.file.rewrite(asdict(b) for b in ordered)


class RecurringStore:
    def __init__(self, data_dir: Path) -> None:
        self.file = JsonlFile(data_dir / "recurring.jsonl")

    def all(self) -> list[Recurring]:
        return [Recurring(**r) for r in self.file.iter_records()]

    def add(self, rule: Recurring) -> None:
        self.file.append(asdict(rule))

    def remove(self, rule_id: str) -> bool:
        rules = self.all()
        kept = [r for r in rules if r.id != rule_id]
        if len(kept) == len(rules):
            return False
        self.file.rewrite(asdict(r) for r in kept)
        return True


def backup_data(data_dir: Path, now: datetime | None = None) -> tuple[Path, int]:
    """data_dir 의 *.jsonl 을 backups/<타임스탬프>/ 로 복사한다. (폴더, 파일 수) 반환."""
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    target = data_dir / "backups" / stamp
    files = sorted(data_dir.glob("*.jsonl"))
    if not files:
        raise AppError("백업할 데이터 파일이 없습니다.", "먼저 add 등으로 데이터를 만든 뒤 실행하세요.")
    target.mkdir(parents=True, exist_ok=True)
    for src in files:
        shutil.copy2(src, target / src.name)
    return target, len(files)
