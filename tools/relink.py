"""문서의 코드 링크 줄 번호를 '이름'으로부터 다시 계산한다.

GitHub 는 소스 파일의 함수/클래스로 가는 링크를 지원하지 않고 줄 번호(#L10-L20)만 지원한다.
그래서 링크의 title(마우스를 올리면 보이는 글)에 "무엇을 가리키는지"를 적어 두고,
이 스크립트가 현재 코드에서 그 위치를 찾아 줄 번호를 고쳐 쓴다.

    [`rewrite`](../budget_app/storage.py#L62-L78 "sym:JsonlFile.rewrite")

title 형식
    sym:Class.method        그 함수/클래스 전체 (데코레이터 포함)
    span:A..B               A 의 시작부터 B 의 끝까지
    at:앞,뒤:코드 한 줄      파일에서 유일한 그 줄을 찾아, 위로 '앞'줄 아래로 '뒤'줄

사용법
    python tools/relink.py            코드 수정 후 실행 → 문서의 줄 번호 갱신
    python tools/relink.py --check    어긋난 링크가 있으면 종료 코드 1 (테스트에서 사용)
    python tools/relink.py --migrate  title 이 없는 줄 링크에 title 을 붙인다(줄 번호가 맞을 때 1회)
"""

from __future__ import annotations

import ast
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
LINK = re.compile(r'\[([^\]]*)\]\(([^)\s#]+\.py)#L(\d+)(?:-L(\d+))?(?: "([^"]*)")?\)')


def symbols(source: str) -> dict[str, tuple[int, int]]:
    """{'Class.method': (시작 줄, 끝 줄)} — 시작 줄은 데코레이터를 포함한다."""
    found: dict[str, tuple[int, int]] = {}

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = prefix + child.name
                start = min([d.lineno for d in child.decorator_list] + [child.lineno])
                found[name] = (start, child.end_lineno or child.lineno)
                visit(child, name + ".")
            else:
                visit(child, prefix)

    visit(ast.parse(source), "")
    return found


def esc(text: str) -> str:
    return html.escape(text, quote=True).replace("|", "&#124;")


def resolve(title: str, source: str) -> tuple[int, int]:
    kind, _, rest = html.unescape(title).partition(":")
    syms = symbols(source)
    if kind == "sym":
        return syms[rest]
    if kind == "span":
        first, last = rest.split("..")
        return syms[first][0], syms[last][1]
    if kind == "at":
        nums, _, text = rest.partition(":")
        before, after = map(int, nums.split(","))
        hits = [i for i, line in enumerate(source.splitlines(), 1) if line.strip() == text]
        if len(hits) != 1:
            raise KeyError(f"'{text}' 는 {len(hits)}곳에 있음(1곳이어야 함)")
        return hits[0] - before, hits[0] + after
    raise KeyError(f"알 수 없는 title: {title}")


def describe(start: int, end: int, source: str) -> str:
    """현재 맞는 줄 범위를 title 로 바꾼다(--migrate)."""
    syms = symbols(source)
    by_range = {span: name for name, span in syms.items()}
    if (start, end) in by_range:
        return "sym:" + by_range[(start, end)]
    starts = {s: n for n, (s, _) in syms.items()}
    ends = {e: n for n, (_, e) in sorted(syms.items(), key=lambda kv: kv[1][0], reverse=True)}
    if start in starts and end in ends:
        return f"span:{starts[start]}..{ends[end]}"
    lines = [line.strip() for line in source.splitlines()]
    for i in range(start, end + 1):  # 범위 안에서 파일 전체에 하나뿐인 줄을 기준으로 삼는다
        if lines[i - 1] and lines.count(lines[i - 1]) == 1:
            return f"at:{i - start},{end - i}:{lines[i - 1]}"
    raise KeyError(f"L{start}-L{end}: 기준으로 삼을 유일한 줄이 없음")


def process(doc: Path, mode: str) -> list[str]:
    """문서 하나를 처리하고 문제 목록을 돌려준다."""
    problems: list[str] = []
    text = doc.read_text(encoding="utf-8")

    def fix(m: re.Match[str]) -> str:
        label, href, a, b, title = m.group(1), m.group(2), int(m.group(3)), m.group(4), m.group(5)
        b = int(b or a)
        source_path = (doc.parent / href).resolve()
        where = f"{doc.name}: [{label}]({href}#L{a}-L{b})"
        try:
            source = source_path.read_text(encoding="utf-8")
            if title is None:
                if mode != "migrate":
                    problems.append(f"{where}: title 없음 (--migrate 필요)")
                    return m.group(0)
                title = esc(describe(a, b, source))
            start, end = resolve(title, source)
        except (OSError, KeyError, ValueError, SyntaxError) as exc:
            problems.append(f"{where}: {exc}")
            return m.group(0)
        # 링크 글자에 줄 번호를 적어 둔 경우("test L59", "L32-L34")도 함께 맞춘다.
        new_label = re.sub(r"L\d+(-L\d+)?", lambda n: f"L{start}-L{end}" if n.group(1) else f"L{start}", label)
        if ((start, end) != (a, b) or new_label != label) and mode == "check":
            problems.append(f"{where}: 실제 위치는 L{start}-L{end}")
        anchor = f"#L{start}" + (f"-L{end}" if end != start else "")
        return f'[{new_label}]({href}{anchor} "{title}")'

    updated = LINK.sub(fix, text)
    if mode != "check" and updated != text:
        doc.write_text(updated, encoding="utf-8")
    return problems


def main() -> int:
    mode = "check" if "--check" in sys.argv else "migrate" if "--migrate" in sys.argv else "update"
    problems = [p for doc in DOCS for p in process(doc, mode)]
    for p in problems:
        print(p)
    count = sum(len(LINK.findall(d.read_text(encoding="utf-8"))) for d in DOCS)
    print(f"[{mode}] 코드 링크 {count}개, 문제 {len(problems)}개")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(errors="replace")
    sys.exit(main())
