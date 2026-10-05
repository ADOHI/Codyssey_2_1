"""콘솔 출력 포맷터: 외부 라이브러리 없이 표를 정렬해 문자열로 만든다."""

from __future__ import annotations

import unicodedata
from typing import Iterable, Sequence

from .models import Transaction

TX_HEADERS = ["ID", "DATE", "TYPE", "CATEGORY", "AMOUNT", "MEMO", "TAGS"]


def display_width(text: str) -> int:
    """터미널에서 차지하는 칸 수. 한글 같은 전각 문자는 2칸으로 센다."""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def _pad(text: str, width: int, right: bool = False) -> str:
    space = " " * (width - display_width(text))
    return space + text if right else text + space


def format_table(headers: Sequence[str], rows: Iterable[Sequence[str]], right_align: Sequence[int] = ()) -> str:
    rows = [list(map(str, row)) for row in rows]
    widths = [max(display_width(cell) for cell in col) for col in zip(headers, *rows)]

    def line(cells: Sequence[str]) -> str:
        return " | ".join(_pad(c, w, i in right_align) for i, (c, w) in enumerate(zip(cells, widths))).rstrip()

    return "\n".join([line(headers), "-+-".join("-" * w for w in widths), *map(line, rows)])


def format_transactions(transactions: Iterable[Transaction]) -> str:
    rows = [
        [tx.id, tx.date, tx.type, tx.category, f"{tx.amount:,}", tx.memo, ",".join(tx.tags)]
        for tx in transactions
    ]
    return format_table(TX_HEADERS, rows, right_align=(4,))
