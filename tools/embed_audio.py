"""Embed a finished WAV as a Python Base64(zlib(WAV)) constant.

Usage: python tools/embed_audio.py finished_bgm.wav
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from canal_delights.core.audio_codec import encode_wav  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('wav', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'src/canal_delights/core/embedded_bgm.py')
    args = parser.parse_args()
    wav = args.wav.read_bytes()
    encoded = encode_wav(wav)
    wrapped = '\n'.join(f"    {encoded[i:i + 88]!r}" for i in range(0, len(encoded), 88))
    text = ('"""Generated BGM resource. Do not edit by hand."""\n\n'
            'BGM_WAV_ZLIB_BASE64 = (\n' + wrapped + '\n)\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding='utf-8')
    print(f'embedded {len(wav):,} WAV bytes -> {len(encoded):,} Base64 chars in {args.output}')


if __name__ == '__main__':
    main()
