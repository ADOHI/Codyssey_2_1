"""공통 관심사(예외 처리, 실행 로그/시간 측정)를 분리한 데코레이터."""

from __future__ import annotations

import functools
import logging
import sys
import time
from typing import Callable, ParamSpec, TypeVar

from .errors import AppError

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger("budget_app")


def handle_errors(func: Callable[P, int]) -> Callable[P, int]:
    """예외를 '원인 + 힌트'로 출력하고 종료 코드로 바꾼다(스택트레이스 금지)."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> int:
        try:
            return func(*args, **kwargs)
        except AppError as exc:
            _print_error(exc.message, exc.hint)
            return 1
        except (KeyboardInterrupt, EOFError):
            _print_error("입력이 중단되었습니다.", "명령을 다시 실행하세요.")
            return 130
        except OSError as exc:
            _print_error(f"파일 처리 중 문제가 발생했습니다: {exc}", "경로와 쓰기 권한(--data-dir)을 확인하세요.")
            return 2
        except Exception as exc:  # 예상 못 한 오류도 스택트레이스 없이 끝낸다.
            logger.debug("unexpected error", exc_info=True)
            _print_error(f"예상하지 못한 오류입니다: {exc}", "--verbose 옵션으로 자세한 로그를 확인하세요.")
            return 3

    return wrapper


def log_timed(func: Callable[P, R]) -> Callable[P, R]:
    """함수 실행 시작/종료와 소요 시간을 로그로 남긴다(--verbose일 때 보인다)."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        logger.debug("시작: %s", func.__name__)
        try:
            return func(*args, **kwargs)
        finally:
            logger.debug("종료: %s (%.2f ms)", func.__name__, (time.perf_counter() - start) * 1000)

    return wrapper


def _print_error(message: str, hint: str) -> None:
    print(f"[오류] {message}", file=sys.stderr)
    if hint:
        print(f"[힌트] {hint}", file=sys.stderr)
