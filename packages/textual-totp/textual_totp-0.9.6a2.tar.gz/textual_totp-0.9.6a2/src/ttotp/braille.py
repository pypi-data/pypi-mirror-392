# SPDX-FileCopyrightText: 2023 Jeff Epler
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Generator, Sequence

    MatrixType = Sequence[Sequence[bool]]
    SixelMapType = dict[tuple[int, int, int, int, int, int], str]

def _braille_gen(m: MatrixType) -> Generator[str]:
    n_rows = len(m)
    n_cols = len(m[0])

    def get(r: int, c: int) -> bool:
        if r >= n_rows or c >= n_cols:
            return False
        return m[r][c]

    for r in range(0, n_rows, 4):
        for c in range(0, n_cols, 2):
            subpixels = (
                get(r    , c    ),
                get(r + 1, c    ),
                get(r + 2, c    ),
                get(r    , c + 1),
                get(r + 1, c + 1),
                get(r + 2, c + 1),
                get(r + 3, c    ),
                get(r + 3, c + 1),
            )
            yield chr(0x2800 + sum(2**i for i, r in enumerate(subpixels) if r))
        yield "\n"


def matrix_to_braille(m: MatrixType) -> str:
    return "".join(_braille_gen(m))
