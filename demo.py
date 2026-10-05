"""동료평가 시연 스크립트: 평가 항목 순서대로 명령을 실행하고 출력과 종료 코드를 보여 준다.

    python demo.py             단계마다 Enter 로 진행
    python demo.py --no-pause  멈추지 않고 끝까지 실행

실제 데이터(./data)는 건드리지 않고 ./demo_data 폴더를 새로 만들어 사용한다.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "demo_data"
PAUSE = "--no-pause" not in sys.argv


def section(title: str) -> None:
    if PAUSE:
        input("\n(Enter 를 누르면 다음 단계로) ")
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def run(*args: str, inputs: list[str] | None = None, note: str = "") -> None:
    """budget_app 명령 하나를 실행하고 명령줄, 출력, 종료 코드를 보여 준다."""
    shown = " ".join(f'"{a}"' if (" " in a or a == "") else a for a in args)
    print(f"\n$ python -m budget_app {shown}")
    if note:
        print(f"  # {note}")
    if inputs is not None:
        print(f"  # 대화형 입력: {' / '.join(i or '(엔터)' for i in inputs)}")
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(
        [sys.executable, "-m", "budget_app", "--data-dir", str(DATA), *args],
        input="\n".join(inputs) + "\n" if inputs is not None else None,
        capture_output=True, text=True, encoding="utf-8", env=env, cwd=ROOT,
    )
    for line in (result.stdout + result.stderr).rstrip().splitlines():
        print(f"  {line}")
    print(f"  → 종료 코드: {result.returncode}")


def show_file(path: Path) -> None:
    print(f"\n[파일 내용] {path.relative_to(ROOT)}")
    for line in path.read_text(encoding="utf-8").splitlines():
        print(f"  {line}")


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(errors="replace")
    shutil.rmtree(DATA, ignore_errors=True)  # 매번 깨끗한 상태에서 시작
    print("budget_app 시연을 시작합니다. 데이터 폴더:", DATA.relative_to(ROOT))

    section("0. 도움말 (--help)")
    run("--help")
    run("search", "--help", note="모든 명령이 --help 를 지원")

    section("1-2. 첫 실행: 저장 파일 자동 생성 + 기본 카테고리")
    run("category", "list")
    print("\n[생성된 파일]", ", ".join(sorted(p.name for p in DATA.glob("*.jsonl"))))

    section("1-1. add: 대화형 거래 추가 (잘못된 입력은 다시 물어봄)")
    run("add", inputs=["2024-13-40", "2024-01-15", "gift", "expense", "food", "-5", "15000", "점심", "meal, daily"],
        note="날짜/타입/금액을 일부러 틀리게 입력")
    run("add", inputs=["2024-01-14", "income", "salary", "3000000", "1월 월급", ""])
    run("add", inputs=["2024-01-20", "expense", "rent", "150000", "월세", ""])
    run("add", inputs=["2024-01-12", "expense", "transport", "20000", "", "commute"])
    run("add", inputs=["2024-02-01", "expense", "food", "30000", "저녁 회식", "meal"])
    show_file(DATA / "transactions.jsonl")
    print("  ↑ 한 줄 = 거래 1건(JSONL). 명령마다 프로그램이 새로 실행되므로 파일에 영구 저장된 것")

    section("1-1. list / search: 최신순, 조건 검색")
    run("list", "--limit", "3")
    run("search", "--from", "2024-01-13", "--to", "2024-01-31", "--type", "expense")
    run("search", "--category", "food", "--tag", "meal")
    run("search", "--q", "회식")

    section("1-4. budget + summary: 예산 사용률과 초과 경고")
    run("budget", "set", "--month", "2024-01", "--amount", "500000")
    run("summary", "--month", "2024-01", "--top", "3", note="예산 이내")
    run("budget", "set", "--month", "2024-01", "--amount", "100000", note="같은 달은 덮어쓰기")
    run("summary", "--month", "2024-01", note="예산 초과 → 경고")
    run("summary", "--month", "2030-01", note="데이터 없는 달")

    section("1-1 / 2-3. update, delete: 원자적 재작성")
    run("update", "--id", "TX-000001", "--amount", "18000", "--memo", "점심(수정)")
    run("delete", "--id", "TX-000004")
    run("list")
    print("\n[임시 파일이 남지 않음]", not (DATA / "transactions.jsonl.tmp").exists())

    section("1-6 / 1-7. 오류: 스택트레이스 없이 원인 + 힌트, 종료 코드 0 아님")
    run("delete", "--id", "TX-999999", note="없는 id")
    run("update", "--id", "TX-000001", "--amount", "-5", note="음수 금액")
    run("update", "--id", "TX-000001", "--date", "2024-02-30", note="존재하지 않는 날짜")
    run("update", "--id", "TX-000001", "--category", "nope", note="없는 카테고리")
    run("export", "--out", str(DATA / "x.csv"), note="기간 조건 누락")
    run("list", "--limit", "0", note="잘못된 옵션 값 (argparse)")
    show_file(DATA / "transactions.jsonl")
    print("  ↑ 실패한 명령들은 파일을 전혀 바꾸지 않았음 (TX-000001 은 여전히 18000)")

    section("1-3. category: 추가 / 사용 중 삭제 차단 / 대체 후 삭제")
    run("category", "add", inputs=["Hobby"], note="대화형, 소문자로 통일")
    run("category", "add", "--name", "hobby", note="중복")
    run("category", "remove", "--name", "food", note="사용 중 → 차단")
    run("category", "remove", "--name", "food", "--replace-with", "etc", note="거래를 옮긴 뒤 삭제")
    run("category", "list")
    run("search", "--category", "etc")

    section("1-5 / 4-3. export / import: CSV 스키마, 깨진 행은 부분 성공 + 리포트")
    out = DATA / "export.csv"
    run("export", "--out", str(out), "--month", "2024-01")
    show_file(out)
    run("import", "--from", str(out), note="내보낸 파일을 그대로 가져오기")
    bad = DATA / "broken.csv"
    bad.write_text(
        "date,type,category,amount,memo,tags\n"
        '2024-03-01,expense,etc,1000,정상,"a,b"\n'
        "2024-99-01,expense,etc,1000,날짜 오류,\n"
        "2024-03-02,expense,nope,1000,없는 카테고리,\n"
        "2024-03-03,expense,etc,-1,음수 금액,\n"
        "2024-03-04,income,salary,500,정상,\n",
        encoding="utf-8",
    )
    show_file(bad)
    run("import", "--from", str(bad), note="5행 중 3행이 깨짐")
    nohdr = DATA / "no_header.csv"
    nohdr.write_text("date,type\n2024-03-01,expense\n", encoding="utf-8")
    run("import", "--from", str(nohdr), note="헤더 불량 → 전체 거부")

    section("3-2. 데코레이터: --verbose 로 실행 로그/시간 확인")
    run("search", "--type", "income", "--verbose")

    section("5. 보너스: 반복 내역 / 백업과 복원 / 표 정렬")
    run("recurring", "add", inputs=["31", "expense", "rent", "500000", "월세(반복)", ""], note="매월 31일")
    run("recurring", "list")
    run("recurring", "apply", "--month", "2024-02", note="2월엔 31일이 없음 → 말일(29일)로 보정")
    run("recurring", "apply", "--month", "2024-02", note="다시 실행해도 중복 생성 안 함")
    run("backup")
    run("delete", "--id", "TX-000002", note="백업 뒤에 실수로 월급 내역을 지움")
    run("restore", note="가장 최근 백업으로 되돌리기 (되돌리기 전 상태도 자동 백업)")
    run("search", "--type", "income", note="지웠던 TX-000002 가 돌아옴")
    run("restore", "--list")

    section("2-3. 수정 도중 중단된 상황: 원본은 그대로, 다음 실행 때 안내")
    (DATA / "transactions.jsonl.tmp").write_text('{"id": "TX-0000', encoding="utf-8")
    print("\n[상황 재현] 수정 중 전원이 꺼져 임시 파일(transactions.jsonl.tmp)만 남은 상태를 만듦")
    run("list", "--limit", "2", note="[안내] 가 한 번 나오고 데이터는 그대로")

    section("2-3. add 도중 중단된 상황: 잘린 마지막 줄만 떼어 내고 나머지는 보존")
    with (DATA / "transactions.jsonl").open("a", encoding="utf-8") as f:
        f.write('{"id": "TX-000099", "type": "expen')
    print("\n[상황 재현] 거래를 추가하다 전원이 꺼져 마지막 줄이 중간에서 끊긴 상태를 만듦")
    run("list", "--limit", "2", note="끊긴 줄을 떼어 내고 무엇이 빠졌는지 안내")
    run("list", "--limit", "2", note="다시 실행하면 안내 없이 정상")

    print(f"\n시연 끝. 사용한 데이터는 {DATA.relative_to(ROOT)}/ 에 남아 있습니다 (다시 실행하면 초기화).")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n시연을 중단했습니다.")
