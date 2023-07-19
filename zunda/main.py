import argparse
import os
import hashlib
import math
import ffmpeg
import pkg_resources
import yaml

import MeCab
import pandas as pd
from pydub import AudioSegment

from zunda.action import make_action_functions_from_timeline
from zunda.layer import Composition
from zunda.subtitle import make_ass_file
from zunda.utils import make_voicevox_dataframe, get_audio_length, get_paths


def make_wav_file(
        audio_dir: str, bgm_path: str, dst_wav_path: str, bgm_volume: int = -20,
        fadein_duration: int = 0, fadeout_duration: int = 5000) -> None:
    wav_files = get_paths(audio_dir, '.wav')
    concatenated_audio = AudioSegment.empty()

    for wav_file in wav_files:
        audio = AudioSegment.from_wav(wav_file)
        concatenated_audio += audio

    # Load BGM
    bgm = AudioSegment.from_wav(bgm_path)
    bgm = bgm + bgm_volume  # Decrease the volume
    # Repeat the BGM to be at least as long as the main audio
    bgm_repeat_times = int(math.ceil(
        concatenated_audio.duration_seconds / get_audio_length(bgm_path)))
    bgm = bgm * bgm_repeat_times
    # Trim the BGM to the same length as the main audio
    bgm = bgm[:len(concatenated_audio)]
    if 0 < fadein_duration:
        bgm = bgm.fade_in(fadein_duration)
    if 0 < fadeout_duration:
        bgm = bgm.fade_out(fadeout_duration)
    # Overlay the main audio with the BGM
    final_output = concatenated_audio.overlay(bgm)

    final_output.export(dst_wav_path, format="wav")


def _get_hash_prefix(text):
    text_bytes = text.encode("utf-8")
    sha1_hash = hashlib.sha1(text_bytes)
    hashed_text = sha1_hash.hexdigest()
    prefix = hashed_text[:6]
    return prefix


def _insert_newlines(text: str, max_length: int) -> str:
    tagger = MeCab.Tagger()
    parsed = tagger.parse(text).split("\n")
    words = [p.split("\t")[0] for p in parsed[:-2]]
    lines: list[str] = []
    for w in words:
        if len(lines) == 0 or max_length < len(lines[-1]) + len(w):
            lines.append('')
        lines[-1] = lines[-1] + w
    return '\\n'.join(lines)


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
            result['action'] = row['action']
        else:
            result['slide'] = 0
            result['status'] = 'n'
            result['action'] = ''
        return result

    txt_files = get_paths(audio_dir, '.txt')
    lines = []
    for txt_file in txt_files:
        raw_text = open(txt_file, 'r', encoding='utf-8-sig').read()
        if raw_text == '':
            raise RuntimeError(
                f'Empty text file: {txt_file}. Please remove it and try again.')
        character_dict = {
            '四国めたん（ノーマル）': 'metan',
            'ずんだもん（ノーマル）': 'zunda',
        }
        filename = os.path.splitext(os.path.basename(txt_file))[0]
        character = filename.split('_')[1]
        dic = {
            'character': character_dict[character],
            'hash': _get_hash_prefix(raw_text),
        }
        dic.update(get_extra_columns(raw_text))
        lines.append(dic)
    frame = pd.DataFrame(lines)
    frame.to_csv(dst_timeline_path, index=False)


def init(args: argparse.Namespace):
    current_directory = os.getcwd()
    asset_dir = os.path.abspath(pkg_resources.resource_filename(__name__, '../assets'))
    config_data = {
        'audio': {
            'bgm_path': os.path.join(asset_dir, 'bgm2.wav'),
            'bgm_volume': -20,
            'fadein_duration': 0,
            'fadeout_duration': 0,
            'audio_dir': 'audio',
            'dst_audio_path': 'outputs/dialogue.wav',
        },
        'video': {
            'height': 1080,
            'width': 1920,
            'fps': 30.0,
            'subtitle_path': 'outputs/subtitile.ass',
            'dst_tmp_video_path': 'outputs/dst_wo_audio.mp4',
            'layers': [
                {
                    'type': 'image',
                    'name': 'bg',
                    'img_path': os.path.join(asset_dir, 'bg2.png'),
                    'anchor_point': [0, 0],
                    'position': [960, 540],
                    'scale': 1.0,
                },
                {
                    'type': 'slide',
                    'name': 'slide',
                    'slide_path': 'slide.pdf',
                    'anchor_point': [0, 0],
                    'position': [960, 421],
                    'scale': 0.71,
                },
                {
                    'type': 'character',
                    'name': 'zunda',
                    'character_dir': os.path.join(asset_dir, 'character', 'zunda'),
                    'character_name': 'zunda',
                    'blink_per_minute': 3,
                    'blink_duration': 0.2,
                    'anchor_point': [0, 0],
                    'position': [1779, 878],
                    'scale': 0.7,
                },
                {
                    'type': 'character',
                    'name': 'metan',
                    'character_dir': os.path.join(asset_dir, 'character', 'metan'),
                    'character_name': 'metan',
                    'blink_per_minute': 3,
                    'blink_duration': 0.2,
                    'anchor_point': [0, 0],
                    'position': [79, 1037],
                    'scale': 0.7,
                }
            ],
        },
        'dst_video_path': 'outputs/dst.mp4',
        'timeline_path': 'outputs/timeline.csv',
        'font': "Hiragino Maru Gothic Pro",
    }
    config_file_path = os.path.join(current_directory, 'config.yaml')
    with open(config_file_path, 'w') as config_file:
        yaml.dump(config_data, config_file, sort_keys=False)
    os.makedirs(os.path.join(current_directory, 'outputs'), exist_ok=True)
    os.makedirs(os.path.join(current_directory, 'audio'), exist_ok=True)


def make_timeline(args: argparse.Namespace):
    config_file_path = os.path.join(os.getcwd(), 'config.yaml')
    config = yaml.load(open(config_file_path, 'r'), Loader=yaml.FullLoader)
    make_timeline_file(config['audio']['audio_dir'], config['timeline_path'])


def make_video(args: argparse.Namespace):
    config_file_path = os.path.join(os.getcwd(), 'config.yaml')
    config = yaml.load(open(config_file_path, 'r'), Loader=yaml.FullLoader)
    make_wav_file(
        config['audio']['audio_dir'], config['audio']['bgm_path'],
        config['audio']['dst_audio_path'],
        bgm_volume=config['audio']['bgm_volume'],
        fadein_duration=config['audio'].get('fadein_duration', 0),
        fadeout_duration=config['audio'].get('fadeout_duration', 0))
    timeline = pd.DataFrame(pd.read_csv(config['timeline_path']))
    timeline = pd.merge(
        timeline, make_voicevox_dataframe(config['audio']['audio_dir']),
        left_index=True, right_index=True)
    make_ass_file(timeline, config['video']['subtitle_path'], config['font'])
    render_video(
        config['video'], config['timeline_path'], config['audio']['audio_dir'], config['video']['dst_tmp_video_path'])
    render_subtitle_video(
        config['video']['dst_tmp_video_path'], config['video']['subtitle_path'],
        config['audio']['dst_audio_path'], config['dst_video_path'])


def render_video(
        video_config: dict, timeline_path: str,
        audio_dir: str, dst_video_path: str) -> None:
    timeline = pd.read_csv(timeline_path)
    audio_df = make_voicevox_dataframe(audio_dir)
    timeline = pd.merge(timeline, audio_df, left_index=True, right_index=True)
    size = (video_config['width'], video_config['height'])
    scene = Composition(timeline=timeline, size=size)
    scene.add_layers_from_config(video_config['layers'])
    animations = make_action_functions_from_timeline(timeline)
    for layer_name, animation_func in animations:
        animation_func(scene, layer_name)
    scene.make_video(dst_video_path, fps=video_config['fps'])


def render_subtitle_video(
        video_path: str, subtitle_path: str, audio_path: str, dst_video_path: str) -> None:
    video_option_str = f"ass={subtitle_path}"
    video_input = ffmpeg.input(video_path)
    audio_input = ffmpeg.input(audio_path)
    output = ffmpeg.output(
        video_input.video, audio_input.audio, dst_video_path,
        vf=video_option_str, acodec='aac', ab='128k')
    output.run(overwrite_output=True)


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
