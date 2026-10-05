"""데이터 구조(모델)와 입력 검증 함수.

파일 I/O나 화면 출력은 전혀 모르는, 가장 안쪽 계층이다.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from .errors import AppError

TYPES = ("income", "expense")
DEFAULT_CATEGORIES = ("food", "transport", "rent", "salary", "etc")


# ---------- 검증 함수: 문자열을 받아 검증된 값을 돌려주거나 AppError ----------

def parse_date(text: str) -> str:
    text = text.strip()
    try:
        # strptime은 2024-1-5도 통과시키므로 다시 포맷해 원본과 비교한다.
        if datetime.strptime(text, "%Y-%m-%d").strftime("%Y-%m-%d") != text:
            raise ValueError
    except ValueError:
        raise AppError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).", "예: 2024-01-15") from None
    return text


def parse_month(text: str) -> str:
    text = text.strip()
    try:
        if datetime.strptime(text, "%Y-%m").strftime("%Y-%m") != text:
            raise ValueError
    except ValueError:
        raise AppError("월 형식이 올바르지 않습니다 (YYYY-MM).", "예: 2024-01") from None
    return text


def parse_type(text: str) -> str:
    text = text.strip().lower()
    if text not in TYPES:
        raise AppError(f"허용되지 않은 타입입니다: {text!r}", "income 또는 expense 중 하나를 입력하세요.")
    return text


def parse_amount(text: str | int) -> int:
    try:
        amount = int(str(text).strip().replace(",", ""))
    except ValueError:
        raise AppError(f"금액은 정수여야 합니다: {text!r}", "예: 15000") from None
    if amount <= 0:
        raise AppError("금액은 0보다 큰 양수여야 합니다.", "예: 15000")
    return amount


def parse_tags(text: str) -> list[str]:
    """'a, b,,a' -> ['a', 'b'] (공백 제거, 빈 값/중복 제거, 순서 유지)."""
    return list(dict.fromkeys(t.strip() for t in text.split(",") if t.strip()))


def parse_category_name(text: str) -> str:
    name = text.strip().lower()
    if not name or "," in name:
        raise AppError("카테고리명은 비어 있거나 쉼표를 포함할 수 없습니다.", "예: food")
    return name


# ---------- 모델 ----------

@dataclass
class Transaction:
    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Transaction:
        return cls(
            id=str(data["id"]),
            type=parse_type(str(data["type"])),
            date=parse_date(str(data["date"])),
            amount=parse_amount(data["amount"]),
            category=str(data["category"]),
            memo=str(data.get("memo", "")),
            tags=list(data.get("tags", [])),
        )


@dataclass
class Budget:
    month: str
    amount: int


@dataclass
class Recurring:
    """매월 반복되는 내역 규칙(월급, 월세 등)."""

    id: str
    type: str
    day: int  # 매월 며칠(1~31). 그 달에 없는 날이면 말일로 보정한다.
    amount: int
    category: str
    memo: str = ""
    tags: list[str] = field(default_factory=list)
