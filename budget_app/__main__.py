"""python -m budget_app 진입점."""

import sys

from .cli import main

if __name__ == "__main__":
    # 콘솔 인코딩(cp949 등)에 없는 글자가 있어도 죽지 않고 '?' 로 바꿔 출력한다.
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(errors="replace")
    sys.exit(main())
