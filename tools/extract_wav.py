"""Extract a normalized WAV soundtrack from a video for later embedding.

Requires ffmpeg on the build machine only. The final application does not
load the video, call ffmpeg, or retain the source video.

Usage: python tools/extract_wav.py source.mp4 --output bgm.wav
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import wave


def build_command(ffmpeg: str, video: Path, output: Path, sample_rate: int | None = None,
                  sample_format: str = 'pcm_s24le') -> list[str]:
    """Return a deterministic ffmpeg extraction command."""
    command = [ffmpeg, '-y', '-i', str(video), '-vn', '-acodec', sample_format]
    if sample_rate is not None:
        command.extend(['-ar', str(sample_rate)])
    command.extend(['-ac', '2', str(output)])
    return command


def extract_wav(video: Path, output: Path, ffmpeg: str = 'ffmpeg', sample_rate: int | None = None,
                sample_format: str = 'pcm_s24le') -> Path:
    """Extract high-precision stereo PCM WAV, preserving source rate by default."""
    video, output = Path(video), Path(output)
    if not video.is_file():
        raise FileNotFoundError(f'video not found: {video}')
    executable = shutil.which(ffmpeg) or (ffmpeg if Path(ffmpeg).is_file() else None)
    if executable is None:
        raise RuntimeError('ffmpeg not found; install it or pass --ffmpeg PATH')
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(build_command(executable, video, output, sample_rate), check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f'ffmpeg extraction failed with exit code {exc.returncode}') from exc
    with wave.open(str(output), 'rb') as wav:
        if wav.getnchannels() != 2 or wav.getsampwidth() not in (2, 3, 4):
            raise RuntimeError('extracted WAV does not match stereo PCM target format')
        if sample_rate is not None and wav.getframerate() != sample_rate:
            raise RuntimeError('extracted WAV sample rate does not match requested target')
        if wav.getnframes() == 0:
            raise RuntimeError('extracted WAV contains no audio frames')
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ffmpeg', default='ffmpeg', help='ffmpeg executable or full path')
    parser.add_argument('--sample-rate', type=int, default=None, help='optional resample rate; omitted preserves source rate')
    parser.add_argument('--sample-format', choices=('pcm_s16le', 'pcm_s24le', 'pcm_s32le'), default='pcm_s24le')
    args = parser.parse_args()
    try:
        result = extract_wav(args.video, args.output, args.ffmpeg, args.sample_rate, args.sample_format)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2
    print(f'extracted WAV: {result}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
