"""전 기능 종단 테스트. 실행: python -m unittest discover -s tests -v"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from budget_app.cli import main


class AppTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.data = self.root / "data"

    def run_cli(self, *argv: str, inputs: list[str] | None = None) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with mock.patch("builtins.input", side_effect=inputs or []):
                try:
                    code = main(["--data-dir", str(self.data), *argv])
                except SystemExit as exc:  # argparse(--help, 잘못된 옵션)
                    code = int(exc.code or 0)
        return code, out.getvalue(), err.getvalue()

    def add(self, date: str, type_: str, category: str, amount: str, memo: str = "", tags: str = "") -> str:
        code, out, _ = self.run_cli("add", inputs=[date, type_, category, amount, memo, tags])
        self.assertEqual(code, 0, out)
        return out.strip().rsplit("id=", 1)[1]

    def seed(self) -> None:
        self.add("2024-01-14", "income", "salary", "3000000")
        self.add("2024-01-12", "expense", "transport", "20000")
        self.add("2024-01-15", "expense", "food", "15000", "점심", "meal, daily")
        self.add("2024-01-20", "expense", "rent", "150000", "월세")
        self.add("2024-02-01", "expense", "food", "30000", "저녁 회식", "meal")

    def rows(self) -> list[dict]:
        text = (self.data / "transactions.jsonl").read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line]

    # ---- 초기화 / 저장 ----

    def test_first_run_creates_files_and_default_categories(self) -> None:
        code, out, _ = self.run_cli("category", "list")
        self.assertEqual(code, 0)
        self.assertIn("[안내]", out)
        self.assertIn("- food", out)
        for name in ("transactions", "categories", "budgets"):
            self.assertTrue((self.data / f"{name}.jsonl").exists(), name)

    def test_add_assigns_sequential_ids_and_persists(self) -> None:
        self.assertEqual(self.add("2024-01-15", "expense", "food", "15000", "점심", "meal"), "TX-000001")
        self.assertEqual(self.add("2024-01-16", "income", "salary", "100"), "TX-000002")
        self.assertEqual(self.rows()[0]["tags"], ["meal"])

    def test_add_reprompts_on_invalid_input(self) -> None:
        inputs = ["2024-13-40", "2024-01-15", "gift", "expense", "nope", "food", "-5", "0", "abc", "15000", "", ""]
        code, out, _ = self.run_cli("add", inputs=inputs)
        self.assertEqual(code, 0)
        self.assertIn("날짜 형식이 올바르지 않습니다", out)
        self.assertIn("허용되지 않은 타입", out)
        self.assertIn("등록되지 않은 카테고리", out)
        self.assertIn("양수", out)
        self.assertEqual(len(self.rows()), 1)

    # ---- 조회 ----

    def test_list_is_newest_first_with_limit(self) -> None:
        self.seed()
        code, out, _ = self.run_cli("list", "--limit", "3")
        dates = [line.split(" | ")[1] for line in out.splitlines() if line.startswith("TX-")]
        self.assertEqual(dates, ["2024-02-01", "2024-01-20", "2024-01-15"])

    def test_search_filters(self) -> None:
        self.seed()

        def ids(*argv: str) -> list[str]:
            _, out, _ = self.run_cli("search", *argv)
            return [line.split(" | ")[0].strip() for line in out.splitlines() if line.startswith("TX-")]

        self.assertEqual(ids("--from", "2024-01-13", "--to", "2024-01-20"), ["TX-000004", "TX-000003", "TX-000001"])
        self.assertEqual(ids("--category", "food"), ["TX-000005", "TX-000003"])
        self.assertEqual(ids("--type", "income"), ["TX-000001"])
        self.assertEqual(ids("--q", "회식"), ["TX-000005"])
        self.assertEqual(ids("--tag", "daily"), ["TX-000003"])
        self.assertEqual(ids("--tag", "meal", "--limit", "1"), ["TX-000005"])
        self.assertEqual(ids("--q", "없는말"), [])

    # ---- 요약 / 예산 ----

    def test_summary_with_budget_and_warning(self) -> None:
        self.seed()
        code, out, _ = self.run_cli("budget", "set", "--month", "2024-01", "--amount", "500000")
        self.assertIn("[저장 완료] 2024-01 예산 500000원", out)
        _, out, _ = self.run_cli("summary", "--month", "2024-01", "--top", "2")
        self.assertIn("총 수입: 3000000원", out)
        self.assertIn("총 지출: 185000원", out)
        self.assertIn("잔액: 2815000원", out)
        self.assertIn("사용률 37.0%", out)
        self.assertIn("1) rent 150000원", out)
        self.assertIn("2) transport 20000원", out)
        self.assertNotIn("3)", out)
        self.assertNotIn("[경고]", out)

        self.run_cli("budget", "set", "--month", "2024-01", "--amount", "100000")  # 덮어쓰기
        _, out, _ = self.run_cli("summary", "--month", "2024-01")
        self.assertIn("사용률 185.0%", out)
        self.assertIn("[경고]", out)
        self.assertEqual(len((self.data / "budgets.jsonl").read_text(encoding="utf-8").splitlines()), 1)

    def test_summary_empty_month(self) -> None:
        self.seed()
        code, out, _ = self.run_cli("summary", "--month", "2030-01")
        self.assertEqual(code, 0)
        self.assertIn("데이터 없음", out)

    # ---- 수정 / 삭제 ----

    def test_update_and_delete(self) -> None:
        self.seed()
        code, out, _ = self.run_cli("update", "--id", "TX-000003", "--amount", "18000", "--memo", "저녁", "--tags", "")
        self.assertEqual(code, 0, out)
        row = next(r for r in self.rows() if r["id"] == "TX-000003")
        self.assertEqual((row["amount"], row["memo"], row["tags"], row["date"]), (18000, "저녁", [], "2024-01-15"))

        code, out, _ = self.run_cli("delete", "--id", "TX-000003")
        self.assertEqual(code, 0)
        self.assertEqual([r["id"] for r in self.rows()], ["TX-000001", "TX-000002", "TX-000004", "TX-000005"])
        self.assertFalse((self.data / "transactions.jsonl.tmp").exists())
        # 삭제 후에도 id 는 재사용되지 않고 최댓값 다음 번호가 나온다.
        self.assertEqual(self.add("2024-03-01", "expense", "food", "1"), "TX-000006")

    def test_missing_id_and_invalid_update_fail_without_change(self) -> None:
        self.seed()
        before = self.rows()
        for argv in (
            ("delete", "--id", "TX-999999"),
            ("update", "--id", "TX-999999", "--amount", "1"),
            ("update", "--id", "TX-000001", "--amount", "-1"),
            ("update", "--id", "TX-000001", "--category", "nope"),
            ("update", "--id", "TX-000001", "--date", "2024-02-30"),
            ("update", "--id", "TX-000001"),
        ):
            code, out, err = self.run_cli(*argv)
            self.assertNotEqual(code, 0, argv)
            self.assertIn("[오류]", err)
            self.assertIn("[힌트]", err)
            self.assertNotIn("Traceback", out + err)
        self.assertIn("없는 데이터", self.run_cli("delete", "--id", "TX-999999")[2])
        self.assertEqual(self.rows(), before)

    # ---- 카테고리 ----

    def test_category_management(self) -> None:
        self.seed()
        code, out, _ = self.run_cli("category", "add", inputs=["Hobby"])
        self.assertIn("[저장 완료] category=hobby", out)
        self.assertNotEqual(self.run_cli("category", "add", "--name", "hobby")[0], 0)  # 중복

        self.assertEqual(self.run_cli("category", "remove", "--name", "hobby")[0], 0)  # 미사용: 삭제
        code, _, err = self.run_cli("category", "remove", "--name", "food")  # 사용 중: 차단
        self.assertNotEqual(code, 0)
        self.assertIn("사용 중", err)
        self.assertIn("--replace-with", err)

        code, out, _ = self.run_cli("category", "remove", "--name", "food", "--replace-with", "etc")
        self.assertEqual(code, 0, out)
        self.assertNotIn("food", {r["category"] for r in self.rows()})
        self.assertNotIn("- food", self.run_cli("category", "list")[1])

    # ---- import / export ----

    def test_export_then_import_roundtrip(self) -> None:
        self.seed()
        out_csv = self.root / "export.csv"
        code, out, _ = self.run_cli("export", "--out", str(out_csv), "--month", "2024-01")
        self.assertIn("(4 records)", out)
        lines = out_csv.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "date,type,category,amount,memo,tags")
        self.assertIn('2024-01-15,expense,food,15000,점심,"meal,daily"', lines)

        code, _, err = self.run_cli("export", "--out", str(out_csv))  # 기간 조건 없음
        self.assertNotEqual(code, 0)
        self.assertIn("기간", err)

        other = self.root / "data2"
        out2, err2 = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out2), contextlib.redirect_stderr(err2):
            code = main(["import", "--from", str(out_csv), "--data-dir", str(other)])  # 옵션을 명령 뒤에
        self.assertEqual(code, 0, err2.getvalue())
        self.assertIn("imported=4, skipped=0", out2.getvalue())

    def test_import_skips_bad_rows(self) -> None:
        src = self.root / "in.csv"
        src.write_text(
            "date,type,category,amount,memo,tags\n"
            "2024-01-01,expense,food,1000,ok,\"a,b\"\n"
            "2024-99-01,expense,food,1000,bad date,\n"
            "2024-01-02,expense,nope,1000,bad category,\n"
            "2024-01-03,expense,food,-1,bad amount,\n"
            "2024-01-04,income,salary,500,,\n",
            encoding="utf-8-sig",  # BOM 이 있어도 읽혀야 한다
        )
        code, out, _ = self.run_cli("import", "--from", str(src))
        self.assertEqual(code, 0)
        self.assertIn("imported=2, skipped=3", out)
        self.assertEqual(self.rows()[0]["tags"], ["a", "b"])

        bad = self.root / "bad.csv"
        bad.write_text("date,type\n2024-01-01,expense\n", encoding="utf-8")
        self.assertNotEqual(self.run_cli("import", "--from", str(bad))[0], 0)
        self.assertNotEqual(self.run_cli("import", "--from", str(self.root / "none.csv"))[0], 0)

    # ---- 보너스 ----

    def test_backup(self) -> None:
        self.seed()
        code, out, _ = self.run_cli("backup")
        self.assertEqual(code, 0)
        backups = list((self.data / "backups").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual(
            (backups[0] / "transactions.jsonl").read_bytes(), (self.data / "transactions.jsonl").read_bytes()
        )

    def test_restore_brings_back_backup_and_is_undoable(self) -> None:
        self.assertNotEqual(self.run_cli("restore")[0], 0)  # 백업 없음
        self.seed()
        self.run_cli("backup")
        saved = self.rows()
        self.run_cli("delete", "--id", "TX-000001")
        self.run_cli("category", "add", "--name", "hobby")
        after_changes = self.rows()

        code, out, _ = self.run_cli("restore")  # 가장 최근 백업으로
        self.assertEqual(code, 0, out)
        self.assertEqual(self.rows(), saved)
        self.assertNotIn("- hobby", self.run_cli("category", "list")[1])

        # 복원 직전 상태가 자동 백업되어 복원을 취소할 수 있다.
        names = [line[2:] for line in self.run_cli("restore", "--list")[1].splitlines() if line.startswith("- ")]
        self.assertEqual(len(names), 2)
        self.assertEqual(self.run_cli("restore", "--name", names[-1])[0], 0)
        self.assertEqual(self.rows(), after_changes)
        self.assertNotEqual(self.run_cli("restore", "--name", "nope")[0], 0)

    def test_interrupted_rewrite_is_reported_and_original_kept(self) -> None:
        self.seed()
        before = self.rows()
        # 수정 도중 프로그램이 죽은 상황: 임시 파일만 남고 교체는 일어나지 않았다.
        (self.data / "transactions.jsonl.tmp").write_text('{"id": "TX-0000', encoding="utf-8")
        code, out, _ = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertIn("중단", out)
        self.assertIn("transactions.jsonl", out)
        self.assertEqual(self.rows(), before)
        self.assertFalse((self.data / "transactions.jsonl.tmp").exists())
        self.assertNotIn("중단", self.run_cli("list")[1])  # 안내는 한 번만

    def test_torn_last_line_is_repaired_and_reported(self) -> None:
        self.seed()
        before = self.rows()
        path = self.data / "transactions.jsonl"
        # add 도중 전원이 꺼진 상황: 마지막 줄이 중간에서 끊기고 줄바꿈도 없다.
        with path.open("a", encoding="utf-8") as f:
            f.write('{"id": "TX-000006", "type": "expen')
        code, out, _ = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertIn("끊겨", out)
        self.assertIn("TX-000006", out)  # 무엇이 빠졌는지 보여 준다
        self.assertEqual(self.rows(), before)
        self.assertNotIn("끊겨", self.run_cli("list")[1])  # 안내는 한 번만
        self.assertEqual(self.add("2024-03-01", "expense", "food", "1"), "TX-000006")

    def test_complete_last_line_without_newline_is_kept(self) -> None:
        self.seed()
        path = self.data / "transactions.jsonl"
        path.write_bytes(path.read_bytes().rstrip(b"\n"))  # 내용은 온전하고 줄바꿈만 빠진 경우
        code, out, _ = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertNotIn("끊겨", out)
        self.assertEqual(len(self.rows()), 5)
        self.add("2024-03-01", "expense", "food", "1")  # 다음 추가가 앞줄에 이어 붙지 않아야 한다
        self.assertEqual([r["id"] for r in self.rows()][-2:], ["TX-000005", "TX-000006"])

    def test_docs_code_links_point_at_current_code(self) -> None:
        # 코드를 고친 뒤 `python tools/relink.py` 를 안 돌리면 여기서 걸린다.
        import subprocess
        import sys

        root = Path(__file__).resolve().parent.parent
        result = subprocess.run(
            [sys.executable, str(root / "tools" / "relink.py"), "--check"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_recurring_apply_is_idempotent_and_clamps_day(self) -> None:
        code, out, _ = self.run_cli("recurring", "add", inputs=["31", "expense", "rent", "500000", "월세", ""])
        self.assertIn("id=RC-0001", out)
        _, out, _ = self.run_cli("recurring", "apply", "--month", "2024-02")
        self.assertIn("created=1, skipped=0", out)
        self.assertEqual(self.rows()[0]["date"], "2024-02-29")  # 윤년 2월 말일로 보정
        _, out, _ = self.run_cli("recurring", "apply", "--month", "2024-02")
        self.assertIn("created=0, skipped=1", out)
        self.assertEqual(len(self.rows()), 1)
        self.assertEqual(self.run_cli("recurring", "remove", "--id", "RC-0001")[0], 0)
        self.assertNotEqual(self.run_cli("recurring", "remove", "--id", "RC-0001")[0], 0)

    # ---- 오류 처리 / 도움말 ----

    def test_corrupted_file_reports_cause_and_hint(self) -> None:
        self.seed()
        with (self.data / "transactions.jsonl").open("a", encoding="utf-8") as f:
            f.write("{broken\n")
        code, out, err = self.run_cli("list")
        self.assertEqual(code, 1)
        self.assertIn("손상", err)
        self.assertNotIn("Traceback", out + err)

    def test_help_for_every_command(self) -> None:
        commands = [
            [], ["add"], ["list"], ["search"], ["summary"], ["update"], ["delete"], ["import"], ["export"],
            ["backup"], ["restore"], ["budget"], ["budget", "set"], ["budget", "show"],
            ["category"], ["category", "add"], ["category", "list"], ["category", "remove"],
            ["recurring"], ["recurring", "add"], ["recurring", "list"], ["recurring", "remove"],
            ["recurring", "apply"],
        ]
        for cmd in commands:
            code, out, _ = self.run_cli(*cmd, "--help")
            self.assertEqual(code, 0, cmd)
            self.assertIn("usage:", out)
        self.assertNotEqual(self.run_cli("nope")[0], 0)
        self.assertNotEqual(self.run_cli("list", "--limit", "0")[0], 0)


if __name__ == "__main__":
    unittest.main()
