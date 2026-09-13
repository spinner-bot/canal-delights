"""Build a self-contained launcher with the package embedded as a zip payload."""

from __future__ import annotations

import base64
import io
import textwrap
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '拼装版' / '运河风物志（Canal delights）.py'


def make_archive() -> bytes:
    stream = io.BytesIO()
    # The embedded BGM is already zlib-compressed Base64. Store package files
    # directly so rebuilding the single-file distribution stays fast.
    with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as archive:
        for path in sorted((ROOT / 'src').rglob('*.py')):
            archive.write(path, path.relative_to(ROOT / 'src').as_posix())
    return stream.getvalue()


def main() -> None:
    payload = base64.b64encode(make_archive()).decode('ascii')
    source = f'''"""Canal Delights 单文件发行版。运行：python 此文件.py"""

import base64
import sys
import tempfile
import zipfile
from pathlib import Path

_PACKAGE_ZIP_B64 = (
    {payload!r}
)


def _run() -> None:
    archive_path = Path(tempfile.gettempdir()) / 'canal_delights_embedded.zip'
    archive_path.write_bytes(base64.b64decode(_PACKAGE_ZIP_B64))
    sys.path.insert(0, str(archive_path))
    from canal_delights.app import main
    main()


if __name__ == '__main__':
    _run()
'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(source, encoding='utf-8', newline='\n')
    print(f'written {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)')


if __name__ == '__main__':
    main()
