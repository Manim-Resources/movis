from pathlib import Path
from typing import NamedTuple, Optional, Sequence, Union

from .enum import Direction


class ASSStyleType(NamedTuple):

    name: str = 'Default'
    font_name: str = 'Helvetica'
    font_size: int = 60
    primary_color: str = '&Hffffff'
    secondary_color: str = '&Hffffff'
    outline_color: str = '&H0'
    back_color: str = '&H0'
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strike_out: bool = False
    scale_x: int = 100
    scale_y: int = 100
    spacing: int = 0
    angle: int = 0
    border_style: int = 1
    outline: int = 5
    shadow: int = 0
    alignment: Direction = Direction.BOTTOM_CENTER
    margin_l: int = 10
    margin_r: int = 10
    margin_v: int = 30


def rgb_to_ass_color(rgb_array: Sequence[int]) -> str:
    if len(rgb_array) == 3:
        return "&H{:02x}{:02x}{:02x}".format(rgb_array[2], rgb_array[1], rgb_array[0])
    elif len(rgb_array) == 4:
        return "&H{:02x}{:02x}{:02x}{:02x}".format(rgb_array[3], rgb_array[2], rgb_array[1], rgb_array[0])
    else:
        raise ValueError('length of rgb_array must be 3(rgb) or 4(rgba)')


def _make_ass_style_header():
    format_str = "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, " \
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, " \
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, " \
        "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding"
    return '\n'.join(["[V4+ Styles]", format_str])


def _make_ass_style(s: ASSStyleType):
    style_str = f'Style: {s.name},{s.font_name},{s.font_size},{s.primary_color},{s.secondary_color},' \
        f'{s.outline_color},{s.back_color},' \
        f'{int(s.bold)},{int(s.italic)},{int(s.underline)},{int(s.strike_out)},' \
        f'{s.scale_x},{s.scale_y},{s.spacing},{s.angle},{s.border_style},' \
        f'{s.outline},{s.shadow},2,{s.margin_l},{s.margin_r},{s.margin_v},1'
    return style_str


def write_ass_file(
    start_times: Sequence[float],
    end_times: Sequence[float],
    texts: Sequence[str],
    dst_ass_file: Union[Path, str],
    size: tuple[int, int] = (1920, 1080),
    characters: Optional[Sequence[str]] = None,
    styles: Optional[Sequence[ASSStyleType]] = None,
) -> None:
    assert len(start_times) == len(end_times) == len(texts)

    if characters is None:
        characters = ['Default'] * len(texts)

    if styles is None:
        styles = [ASSStyleType()]

    ass_style_header = _make_ass_style_header()
    ass_style_body = '\n'.join([_make_ass_style(style) for style in styles])

    header = f"""[Script Info]
; Script generated by FFmpeg/Lavc60.14.101
ScriptType: v4.00+
PlayResX: {size[0]}
PlayResY: {size[1]}
ScaledBorderAndShadow: yes
YCbCr Matrix: None

{ass_style_header}
{ass_style_body}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    line_template = "Dialogue: 0,{start_time},{end_time},{character},,0,0,0,,{text}"

    def get_time(t):
        return "{:02d}:{:02d}:{:02d}.{:02d}".format(
            int(t / 3600), int((t / 60) % 60), int(t % 60), int((t % 1) * 100)
        )

    lines = []
    for t0, t1, character, text in zip(start_times, end_times, characters, texts):
        text0, text1 = get_time(t0), get_time(t1)
        x = line_template.format(
            start_time=text0, end_time=text1, character=character, text=text)
        lines.append(x)
    body = "\n".join(lines)
    with open(dst_ass_file, "w") as fp:
        fp.write(header + body)


def write_srt_file(
        start_times: Sequence[float], end_times: Sequence[float], texts: Sequence[str],
        dst_srt_file: Union[Path, str]) -> None:
    assert len(start_times) == len(end_times) == len(texts)
    with open(dst_srt_file, 'w') as srt:
        for i, (start_time, end_time, text) in enumerate(zip(start_times, end_times, texts)):
            srt.write('{}\n'.format(i + 1))
            srt.write('{:02d}:{:02d}:{:02d},{:03d} --> {:02d}:{:02d}:{:02d},{:03d}\n'.format(
                int(start_time / 3600), int((start_time / 60) % 60),
                int(start_time % 60), int((start_time % 1) * 1000),
                int(end_time / 3600), int((end_time / 60) % 60),
                int(end_time % 60), int((end_time % 1) * 1000),
            ))
            cleaned_text = text.replace(r"\n", "").replace("\n", "")
            srt.write(cleaned_text + '\n\n')
