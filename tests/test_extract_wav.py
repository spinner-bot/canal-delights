from pathlib import Path

from tools.extract_wav import build_command


def test_video_extraction_command_discards_video_and_normalizes_pcm():
    command = build_command('ffmpeg', Path('source.mp4'), Path('bgm.wav'))
    assert command == [
        'ffmpeg', '-y', '-i', 'source.mp4', '-vn',
        '-acodec', 'pcm_s24le', '-ac', '2', 'bgm.wav',
    ]

    assert '-ar' in build_command('ffmpeg', Path('source.mp4'), Path('bgm.wav'), 48000)
