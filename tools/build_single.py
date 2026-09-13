"""Build a readable single-file distribution: source plain, audio encoded."""
from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '拼装版' / '运河风物志（Canal delights）.py'


def main() -> None:
    modules = {}
    for path in sorted((ROOT / 'src').rglob('*.py')):
        if path.name == 'embedded_bgm.py':
            continue
        name = '.'.join(path.relative_to(ROOT / 'src').with_suffix('').parts)
        modules[name] = path.read_text(encoding='utf-8')
    modules['canal_delights.core.embedded_mp3'] = 'BGM_MP3_BASE64 = __canal_audio_payload__\n'
    mp3 = base64.b64encode((ROOT / 'resource' / 'BGM_preview_48k.mp3').read_bytes()).decode('ascii')
    source_modules = repr(modules)
    audio_chunks = '\n'.join(f'    {mp3[i:i + 4096]!r}' for i in range(0, len(mp3), 4096))
    source = f'''"""Canal Delights 单文件发行版（源码明文拼装，音频压缩存储）。"""

import importlib.abc
import importlib.util
import sys
import base64

_MODULE_SOURCES = {source_modules}


class _SourceLoader(importlib.abc.Loader):
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        if module.__name__ == 'canal_delights.core.embedded_mp3':
            module.__dict__['__canal_audio_payload__'] = _AUDIO_MP3_BASE64
        exec(compile(_MODULE_SOURCES[module.__name__], module.__name__, 'exec'), module.__dict__)


class _SourceFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname not in _MODULE_SOURCES:
            return None
        package = fullname + '.__init__' in _MODULE_SOURCES
        return importlib.util.spec_from_loader(fullname, _SourceLoader(), is_package=package)


sys.meta_path.insert(0, _SourceFinder())


def _run():
    from canal_delights.app import main
    main()


# The only intentionally opaque section: 48 kbps MP3 audio, kept at EOF.
_AUDIO_MP3_BASE64 = (
{audio_chunks}
)


if __name__ == '__main__':
    _run()
'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(source, encoding='utf-8', newline='\n')
    print(f'written {{OUTPUT}} ({{OUTPUT.stat().st_size:,}} bytes)')


if __name__ == '__main__':
    main()
