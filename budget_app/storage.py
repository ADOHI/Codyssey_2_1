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

    @property
    def tmp_path(self) -> Path:
        return self.path.with_name(self.path.name + ".tmp")

    def clear_stale_tmp(self) -> bool:
        """이전 실행이 수정 도중 중단되어 남긴 임시 파일을 지운다. 지웠으면 True.

        교체(os.replace) 전에 중단된 것이므로 원본은 수정 전 상태 그대로다.
        """
        if not self.tmp_path.exists():
            return False
        self.tmp_path.unlink()
        return True

    def repair_torn_tail(self) -> str | None:
        """추가(append) 도중 중단되어 잘린 마지막 줄을 떼어 낸다. 떼어 낸 조각을 돌려준다(없으면 None).

        append 는 항상 '한 줄 + 줄바꿈'을 쓰므로, 파일이 줄바꿈으로 끝나지 않으면 마지막 쓰기가 끊긴 것이다.
        끝에 붙이기는 기존 내용을 건드리지 않으므로 손상은 이 마지막 줄 하나로 한정된다.
        """
        if not self.path.exists():
            return None
        with self.path.open("rb+") as f:
            size = f.seek(0, os.SEEK_END)
            if size == 0:
                return None
            f.seek(size - 1)
            if f.read(1) == b"\n":
                return None
            pos, tail = size, b""  # 파일 전체를 읽지 않고 뒤에서부터 마지막 줄바꿈을 찾는다
            while pos > 0 and b"\n" not in tail:
                step = min(4096, pos)
                pos -= step
                f.seek(pos)
                tail = f.read(step) + tail
            cut = tail.rfind(b"\n") + 1
            fragment = tail[cut:]
            try:
                complete = isinstance(json.loads(fragment.decode("utf-8")), dict)
            except ValueError:  # JSON 오류와 UTF-8 디코딩 오류 모두 ValueError 의 하위 타입
                complete = False
            if complete:  # 내용은 다 쓰였고 줄바꿈만 빠졌다: 버리지 않고 줄바꿈만 채운다
                f.seek(size)
                f.write(b"\n")
                return None
            f.truncate(pos + cut)
            return fragment.decode("utf-8", errors="replace")

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
                        "해당 줄을 직접 고치거나, 백업이 있으면 restore 명령으로 되돌리세요.",
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
            # '저장 완료'를 알리기 전에 디스크까지 확정한다.
            # ponytail: 건마다 fsync 라 대량 import 는 느려진다. 느리면 여러 줄을 모아 한 번에 확정.
            f.flush()
            os.fsync(f.fileno())

    def rewrite(self, records: Iterable[dict[str, Any]]) -> None:
        """임시 파일에 전부 쓴 뒤 rename 으로 교체한다(원자적 저장).

        쓰는 도중 프로그램이 죽어도 원본 파일은 그대로 남는다.
        records 가 원본을 읽는 제너레이터여도 한 줄씩 흘려보내므로 메모리를 아낀다.
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.tmp_path
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
    files = sorted(data_dir.glob("*.jsonl"))
    if not files:
        raise AppError("백업할 데이터 파일이 없습니다.", "먼저 add 등으로 데이터를 만든 뒤 실행하세요.")
    # 같은 초에 두 번 백업해도 기존 백업을 덮어쓰지 않도록 이름을 겹치지 않게 한다.
    target = data_dir / "backups" / stamp
    suffix = 2
    while target.exists():
        target = data_dir / "backups" / f"{stamp}-{suffix}"
        suffix += 1
    target.mkdir(parents=True)
    for src in files:
        shutil.copy2(src, target / src.name)
    return target, len(files)


def list_backups(data_dir: Path) -> list[str]:
    """백업 폴더 이름 목록(오래된 것부터). 폴더는 만들어진 순서대로 정렬한다."""
    root = data_dir / "backups"
    if not root.is_dir():
        return []
    return [p.name for p in sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: (p.stat().st_mtime, p.name))]


def restore_data(data_dir: Path, name: str) -> int:
    """backups/<name>/ 의 *.jsonl 을 data_dir 로 되돌린다. 복원한 파일 수 반환.

    파일마다 임시 파일로 복사한 뒤 os.replace 로 교체하므로, 도중에 중단돼도 반쯤 복사된 파일은 남지 않는다.
    """
    files = sorted((data_dir / "backups" / name).glob("*.jsonl"))
    for src in files:
        tmp = data_dir / (src.name + ".tmp")
        try:
            shutil.copyfile(src, tmp)
            os.replace(tmp, data_dir / src.name)
        finally:
            tmp.unlink(missing_ok=True)
    return len(files)
