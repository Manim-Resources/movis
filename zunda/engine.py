import argparse
import os
import hashlib
import math
import pkg_resources
import subprocess
import tempfile
from typing import List
import yaml

import pandas as pd
from pydub import AudioSegment
from PIL import Image


def _get_audio_length(filename: str) -> float:
    audio = AudioSegment.from_file(filename, format="wav")
    return audio.duration_seconds


def _concat_audio_files(
        wav_files: List[str], bgm_file: str, wav_path: str, bgm_volume: int = -15,
        fadein_duration: int = 0, fadeout_duration: int = 5000) -> None:
    concatenated_audio = AudioSegment.empty()

    for wav_file in wav_files:
        audio = AudioSegment.from_wav(wav_file)
        concatenated_audio += audio

    # Load BGM
    bgm = AudioSegment.from_wav(bgm_file)
    bgm = bgm + bgm_volume  # Decrease the volume
    # Repeat the BGM to be at least as long as the main audio
    bgm_repeat_times = int(math.ceil(
        concatenated_audio.duration_seconds / _get_audio_length(bgm_file)))
    bgm = bgm * bgm_repeat_times
    # Trim the BGM to the same length as the main audio
    bgm = bgm[:len(concatenated_audio)]
    if 0 < fadein_duration:
        bgm = bgm.fade_in(fadein_duration)
    if 0 < fadeout_duration:
        bgm = bgm.fade_out(fadeout_duration)
    # Overlay the main audio with the BGM
    final_output = concatenated_audio.overlay(bgm)

    final_output.export(wav_path, format="wav")


def _insert_newlines(text: str, max_length: int) -> str:
    import MeCab
    tagger = MeCab.Tagger()
    parsed = tagger.parse(text).split("\n")
    words = [p.split("\t")[0] for p in parsed[:-2]]
    lines = []
    for w in words:
        if len(lines) == 0 or max_length < len(lines[-1]) + len(w):
            lines.append('')
        lines[-1] = lines[-1] + w
    return '\\n'.join(lines)


def _get_paths(src_dir: str, ext: str) -> List[str]:
    return sorted([
        os.path.join(src_dir, f)
        for f in os.listdir(src_dir) if f.endswith(ext)])


def make_wav_file(audio_dir: str, bgm_path: str, dst_wav_path: str, bgm_volume: int = -20) -> None:
    wav_files = _get_paths(audio_dir, '.wav')
    _concat_audio_files(wav_files, bgm_path, dst_wav_path, bgm_volume)


def _get_hash_prefix(text):
    text_bytes = text.encode("utf-8")
    sha1_hash = hashlib.sha1(text_bytes)
    hashed_text = sha1_hash.hexdigest()
    prefix = hashed_text[:6]
    return prefix


def make_timeline_file(audio_dir: str, dst_timeline_path: str, max_length: int = 25) -> None:
    prev_timeline = None
    if os.path.exists(dst_timeline_path):
        prev_timeline = pd.read_csv(dst_timeline_path)

    def get_extra_columns(text):
        def transform_text(raw_text):
            if 0 < max_length:
                return _insert_newlines(raw_text, max_length=max_length)
            else:
                return raw_text

        row = None
        if prev_timeline is not None:
            hash = _get_hash_prefix(text)
            filtered_tl = prev_timeline[prev_timeline['hash'] == hash]
            if 0 < len(filtered_tl):
                row = filtered_tl.iloc[0]
                modified_text = row['text']
            else:
                modified_text = transform_text(raw_text)
        else:
            modified_text = transform_text(raw_text)

        result = {'text': modified_text}
        if row is not None:
            result['slide'] = row['slide']
            result['status'] = row['status']
        else:
            result['slide'] = 0
            result['status'] = 'n'
        return result

    wav_files = _get_paths(audio_dir, '.wav')
    txt_files = _get_paths(audio_dir, '.txt')
    frame = []
    start_time = 0
    for wav_file, txt_file in zip(wav_files, txt_files):
        duration = _get_audio_length(wav_file)
        end_time = start_time + duration

        raw_text = open(txt_file, 'r', encoding='utf-8-sig').read()
        character_dict = {
            '四国めたん（ノーマル）': 'metan',
            'ずんだもん（ノーマル）': 'zunda',
        }
        filename = os.path.splitext(os.path.basename(txt_file))[0]
        character = filename.split('_')[1]
        dic = {
            'start_time': start_time,
            'end_time': end_time,
            'character': character_dict[character],
            'hash': _get_hash_prefix(raw_text),
        }
        dic.update(get_extra_columns(raw_text))
        frame.append(dic)
        start_time = end_time
    frame = pd.DataFrame(frame)
    frame.to_csv(dst_timeline_path, index=False)


def make_srt_file(timeline_path: str, dst_srt_path: str) -> None:
    timeline = pd.read_csv(timeline_path)
    with open(dst_srt_path, 'w') as srt:
        for i, row in timeline.iterrows():
            start_time = row['start_time']
            end_time = row['end_time']
            srt.write('{}\n'.format(i + 1))
            srt.write('{:02d}:{:02d}:{:02d},{:03d} --> {:02d}:{:02d}:{:02d},{:03d}\n'.format(
                int(start_time / 3600), int((start_time / 60) % 60),
                int(start_time % 60), int((start_time % 1) * 1000),
                int(end_time / 3600), int((end_time / 60) % 60),
                int(end_time % 60), int((end_time % 1) * 1000),
            ))
            text = row['text']
            srt.write(text + '\n\n')


def make_ass_file(timeline_path: str, dst_ass_path: str) -> None:
    timeline = pd.read_csv(timeline_path)
    header = """[Script Info]
; Script generated by FFmpeg/Lavc60.14.101
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Hiragino Maru Gothic Pro,96,&Hffffff,&Hffffff,&H0,&H0,0,0,0,0,100,100,0,0,1,5,0,2,10,10,25,1
Style: zunda,Hiragino Maru Gothic Pro,96,&Hffffff,&Hffffff,&H38a65e,&HA0000000,0,0,0,0,100,100,0,0,1,5,3,2,10,10,30,1
Style: metan,Hiragino Maru Gothic Pro,96,&Hffffff,&Hffffff,&H734aab,&HA0000000,0,0,0,0,100,100,0,0,1,5,3,2,10,10,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    line_template = "Dialogue: 0,{start_time},{end_time},{character},,0,0,0,,{text}"

    def get_time(t):
        return "{:02d}:{:02d}:{:02d}.{:02d}".format(
            int(t / 3600), int((t / 60) % 60), int(t % 60), int((t % 1) * 100))

    lines = []
    for _, row in timeline.iterrows():
        start_time = get_time(row['start_time'])
        end_time = get_time(row['end_time'])
        lines.append(line_template.format(
            start_time=start_time, end_time=end_time,
            character=row['character'], text=row['text']))
    body = '\n'.join(lines)
    with open(dst_ass_path, 'w') as fp:
        fp.write(header + body)


def make_still_video(bg_path: str, audio_path: str, dst_video_path: str) -> None:
    import ffmpeg

    ffmpeg.input(bg_path, loop=1, r=5).output(
        dst_video_path, vcodec='libx264', tune='stillimage',
        acodec='aac', audio_bitrate='192k', pix_fmt='yuv420p', shortest=None) \
        .global_args('-i', audio_path).run(overwrite_output=True)


def make_still_images(
        bg_path: str, character_dir: str, slide_path: str,
        timeline_path: str, video_config: str, dst_dir: str) -> None:
    from pdf2image import convert_from_path

    bg_image = Image.open(bg_path).convert('RGBA')
    timeline = pd.read_csv(timeline_path)
    character_imgs = {}
    for c in os.listdir(character_dir):
        c_dir = os.path.join(character_dir, c)
        if not os.path.isdir(c_dir):
            continue
        status_filenames = [x for x in os.listdir(c_dir) if os.path.splitext(x)[1] == '.png']
        ratio = video_config['character'][c]['ratio']
        images = {}
        for fn in status_filenames:
            key = os.path.splitext(fn)[0]
            img = Image.open(os.path.join(c_dir, fn)).convert('RGBA')
            w, h = img.size
            img = img.resize(
                (int(w * ratio), int(h * ratio)), Image.Resampling.BICUBIC)
            images[key] = img
        character_imgs[c] = images
    status = {k: v['initial_status'] for k, v in video_config['character'].items()}

    slide_images = []
    for img in convert_from_path(slide_path):
        img = img.convert('RGBA')
        w, h = img.size
        ratio = video_config['slide']['ratio']
        img = img.resize(
            (int(w * ratio), int(h * ratio)), Image.Resampling.BICUBIC)
        slide_images.append(img)
    slide_number = 0
    os.makedirs(dst_dir, exist_ok=True)
    for t, row in timeline.iterrows():
        status[row['character']] = row['status']
        slide_number += row['slide']

        img_t = bg_image.copy()
        img_t.alpha_composite(slide_images[slide_number], tuple(video_config['slide']['offset']))
        for c, imgs in character_imgs.items():
            img_t.alpha_composite(imgs[status[c]], tuple(video_config['character'][c]['offset']))
        dst_path = os.path.join(dst_dir, f'{t:03d}.png')
        img_t.save(dst_path)


def make_video_from_images(
        images_dir: str, audio_path: str, timeline_path: str, dst_video_path: str) -> None:
    timeline = pd.read_csv(timeline_path)
    temp_file = None
    try:
        current_directory = os.getcwd()
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', dir=current_directory, delete=False)
        duration_path = temp_file.name
        duration = timeline['end_time'] - timeline['start_time']
        with open(duration_path, 'w') as fp:
            for i, d in enumerate(duration):
                file_path = os.path.join(images_dir, f'{i:03d}.png')
                fp.write(f"file '{file_path}'\n")
                fp.write(f"duration {d}\n")

            # Handle the known bug where the last duration of ffmpeg is ignored
            fp.write(f"file '{file_path}'\n")
            fp.write("duration 0.1\n")

        # Use subprocess since concat is not available in ffmpeg-python
        command = f'ffmpeg -y -f concat -i {duration_path} -i {audio_path}' \
            f' -c:v libx264 -c:a aac -b:a 192k -pix_fmt yuv420p -r 30 {dst_video_path}'
        subprocess.call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print("subprocess execution failed:", e)
    finally:
        if temp_file:
            temp_file.close()
            os.remove(duration_path)


def make_subtitle_video(
        video_path: str, srt_path: str, timeline_path: str, dst_video_path: str) -> None:
    import ffmpeg
    timeline = pd.read_csv(timeline_path)
    length = timeline['end_time'].iloc[-1]

    video_option_str = f"ass={srt_path}"
    ffmpeg.input(video_path).output(
        dst_video_path, vf=video_option_str, t=length).run(overwrite_output=True)


def init(args: argparse.Namespace):
    current_directory = os.getcwd()
    asset_dir = os.path.abspath(pkg_resources.resource_filename(__name__, '../assets'))
    config_data = dict(
        audio_dir='audio',
        slide_path='slide.pdf',
        bgm_path=os.path.join(asset_dir, 'bgm2.wav'),
        character_dir=os.path.join(asset_dir, 'character'),
        bg_path=os.path.join(asset_dir, 'bg.png'),
        audio_path='outputs/dialogue.wav',
        subtitle_path='outputs/subtitile.ass',
        timeline_path='outputs/timeline.csv',
        images_dir='outputs/images',
        video_wo_subtitle_path='outputs/dst_wo_subtitle.mp4',
        video_path='outputs/dst.mp4',
        layers={
            'slide': {'offset': [250, 22], 'ratio': 0.71},
            'character': {
                'zunda': {'initial_status': 'n', 'offset': [1400, 300], 'ratio': 0.7},
                'metan': {'initial_status': 'n', 'offset': [-300, 400], 'ratio': 0.7},
            }
        },
    )
    config_file_path = os.path.join(current_directory, 'config.yaml')
    with open(config_file_path, 'w') as config_file:
        yaml.dump(config_data, config_file)
    os.makedirs(os.path.join(current_directory, 'outputs'), exist_ok=True)


def make_timeline(args: argparse.Namespace):
    config_file_path = os.path.join(os.getcwd(), 'config.yaml')
    config = yaml.load(open(config_file_path, 'r'), Loader=yaml.FullLoader)
    make_timeline_file(config['audio_dir'], config['timeline_path'])


def make_video(args: argparse.Namespace):
    config_file_path = os.path.join(os.getcwd(), 'config.yaml')
    config = yaml.load(open(config_file_path, 'r'), Loader=yaml.FullLoader)
    make_wav_file(config['audio_dir'], config['bgm_path'], config['audio_path'])
    make_ass_file(config['timeline_path'], config['subtitle_path'])
    make_still_images(
        config['bg_path'], config['character_dir'], config['slide_path'],
        config['timeline_path'], config['layers'], config['images_dir'])
    make_video_from_images(
        config['images_dir'], config['audio_path'], config['timeline_path'],
        config['video_wo_subtitle_path'])
    make_subtitle_video(
        config['video_wo_subtitle_path'], config['subtitle_path'],
        config['timeline_path'], config['video_path'])


def main():
    parser = argparse.ArgumentParser(prog="zunda")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "init", help="Initialize a project").set_defaults(func=init)

    make_parser = subparsers.add_parser("make", help="Make Zunda-related files")
    make_subparsers = make_parser.add_subparsers(dest="make_command")
    make_subparsers.add_parser(
        "timeline", help="Make timeline").set_defaults(func=make_timeline)
    make_subparsers.add_parser(
        "video", help="Make video").set_defaults(func=make_video)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
