from enum import Enum


class CacheType(Enum):
    COMPOSITION = 0
    LAYER = 1


class AttributeType(Enum):
    SCALAR = 0
    VECTOR2D = 1
    VECTOR3D = 2
    ANGLE = 3
    COLOR = 4

    @staticmethod
    def from_string(s: str) -> "AttributeType":
        if s == 'scalar':
            return AttributeType.SCALAR
        elif s == 'vector2d':
            return AttributeType.VECTOR2D
        elif s == 'vector3d':
            return AttributeType.VECTOR3D
        elif s == 'angle':
            return AttributeType.ANGLE
        else:
            raise ValueError(f"Unknown attribute type: {s}")


class MotionType(Enum):
    LINEAR = 0
    EASE_IN = 1
    EASE_OUT = 2
    EASE_IN_OUT = 3
    EASE_IN2 = 102
    EASE_IN3 = 103
    EASE_IN4 = 104
    EASE_IN5 = 105
    EASE_IN6 = 106
    EASE_IN7 = 107
    EASE_IN8 = 108
    EASE_IN9 = 109
    EASE_IN10 = 110
    EASE_IN12 = 112
    EASE_IN14 = 114
    EASE_IN16 = 116
    EASE_IN18 = 118
    EASE_IN20 = 120
    EASE_IN25 = 125
    EASE_IN30 = 130
    EASE_IN35 = 135
    EASE_OUT2 = 202
    EASE_OUT3 = 203
    EASE_OUT4 = 204
    EASE_OUT5 = 205
    EASE_OUT6 = 206
    EASE_OUT7 = 207
    EASE_OUT8 = 208
    EASE_OUT9 = 209
    EASE_OUT10 = 210
    EASE_OUT12 = 212
    EASE_OUT14 = 214
    EASE_OUT16 = 216
    EASE_OUT18 = 218
    EASE_OUT20 = 220
    EASE_OUT25 = 225
    EASE_OUT30 = 230
    EASE_OUT35 = 235
    EASE_IN_OUT2 = 302
    EASE_IN_OUT3 = 303
    EASE_IN_OUT4 = 304
    EASE_IN_OUT5 = 305
    EASE_IN_OUT6 = 306
    EASE_IN_OUT7 = 307
    EASE_IN_OUT8 = 308
    EASE_IN_OUT9 = 309
    EASE_IN_OUT10 = 310
    EASE_IN_OUT12 = 312
    EASE_IN_OUT14 = 314
    EASE_IN_OUT16 = 316
    EASE_IN_OUT18 = 318
    EASE_IN_OUT20 = 320
    EASE_IN_OUT25 = 325
    EASE_IN_OUT30 = 330
    EASE_IN_OUT35 = 335

    @staticmethod
    def from_string(s: str) -> "MotionType":
        if s in STRING_TO_MOTION_TYPE:
            return STRING_TO_MOTION_TYPE[s]
        else:
            raise ValueError(f"Unknown motion type: {s}")


STRING_TO_MOTION_TYPE = {
    "linear": MotionType.LINEAR,
    "ease_in": MotionType.EASE_IN,
    "ease_out": MotionType.EASE_OUT,
    "ease_in_out": MotionType.EASE_IN_OUT,
    "ease_in2": MotionType.EASE_IN2,
    "ease_in3": MotionType.EASE_IN3,
    "ease_in4": MotionType.EASE_IN4,
    "ease_in5": MotionType.EASE_IN5,
    "ease_in6": MotionType.EASE_IN6,
    "ease_in7": MotionType.EASE_IN7,
    "ease_in8": MotionType.EASE_IN8,
    "ease_in9": MotionType.EASE_IN9,
    "ease_in10": MotionType.EASE_IN10,
    "ease_in12": MotionType.EASE_IN12,
    "ease_in14": MotionType.EASE_IN14,
    "ease_in16": MotionType.EASE_IN16,
    "ease_in18": MotionType.EASE_IN18,
    "ease_in20": MotionType.EASE_IN20,
    "ease_in25": MotionType.EASE_IN25,
    "ease_in30": MotionType.EASE_IN30,
    "ease_in35": MotionType.EASE_IN35,
    "ease_out2": MotionType.EASE_OUT2,
    "ease_out3": MotionType.EASE_OUT3,
    "ease_out4": MotionType.EASE_OUT4,
    "ease_out5": MotionType.EASE_OUT5,
    "ease_out6": MotionType.EASE_OUT6,
    "ease_out7": MotionType.EASE_OUT7,
    "ease_out8": MotionType.EASE_OUT8,
    "ease_out9": MotionType.EASE_OUT9,
    "ease_out10": MotionType.EASE_OUT10,
    "ease_out12": MotionType.EASE_OUT12,
    "ease_out14": MotionType.EASE_OUT14,
    "ease_out16": MotionType.EASE_OUT16,
    "ease_out18": MotionType.EASE_OUT18,
    "ease_out20": MotionType.EASE_OUT20,
    "ease_out25": MotionType.EASE_OUT25,
    "ease_out30": MotionType.EASE_OUT30,
    "ease_out35": MotionType.EASE_OUT35,
    "ease_in_out2": MotionType.EASE_IN_OUT2,
    "ease_in_out3": MotionType.EASE_IN_OUT3,
    "ease_in_out4": MotionType.EASE_IN_OUT4,
    "ease_in_out5": MotionType.EASE_IN_OUT5,
    "ease_in_out6": MotionType.EASE_IN_OUT6,
    "ease_in_out7": MotionType.EASE_IN_OUT7,
    "ease_in_out8": MotionType.EASE_IN_OUT8,
    "ease_in_out9": MotionType.EASE_IN_OUT9,
    "ease_in_out10": MotionType.EASE_IN_OUT10,
    "ease_in_out12": MotionType.EASE_IN_OUT12,
    "ease_in_out14": MotionType.EASE_IN_OUT14,
    "ease_in_out16": MotionType.EASE_IN_OUT16,
    "ease_in_out18": MotionType.EASE_IN_OUT18,
    "ease_in_out20": MotionType.EASE_IN_OUT20,
    "ease_in_out25": MotionType.EASE_IN_OUT25,
    "ease_in_out30": MotionType.EASE_IN_OUT30,
    "ease_in_out35": MotionType.EASE_IN_OUT35,
}


class BlendingMode(Enum):
    NORMAL = 0
    MULTIPLY = 1
    SCREEN = 2
    OVERLAY = 3
    DARKEN = 4
    LIGHTEN = 5
    COLOR_DODGE = 6
    COLOR_BURN = 7
    LINEAR_DODGE = 8
    LINEAR_BURN = 9
    HARD_LIGHT = 10
    SOFT_LIGHT = 11
    VIVID_LIGHT = 12
    LINEAR_LIGHT = 13
    PIN_LIGHT = 14
    DIFFERENCE = 15
    EXCLUSION = 16
    SUBTRACT = 17

    @staticmethod
    def from_string(s: str) -> "BlendingMode":
        if s in STRING_TO_BLENDING_MODE:
            return STRING_TO_BLENDING_MODE[s]
        else:
            raise ValueError(f"Unknown blending mode: {s}")


STRING_TO_BLENDING_MODE = {
    "normal": BlendingMode.NORMAL,
    "multiply": BlendingMode.MULTIPLY,
    "screen": BlendingMode.SCREEN,
    "overlay": BlendingMode.OVERLAY,
    "darken": BlendingMode.DARKEN,
    "lighten": BlendingMode.LIGHTEN,
    "color_dodge": BlendingMode.COLOR_DODGE,
    "color_burn": BlendingMode.COLOR_BURN,
    "linear_dodge": BlendingMode.LINEAR_DODGE,
    "linear_burn": BlendingMode.LINEAR_BURN,
    "hard_light": BlendingMode.HARD_LIGHT,
    "soft_light": BlendingMode.SOFT_LIGHT,
    "vivid_light": BlendingMode.VIVID_LIGHT,
    "linear_light": BlendingMode.LINEAR_LIGHT,
    "pin_light": BlendingMode.PIN_LIGHT,
    "difference": BlendingMode.DIFFERENCE,
    "exclusion": BlendingMode.EXCLUSION,
    "subtract": BlendingMode.SUBTRACT,
}


class MatteMode(Enum):
    NONE = 0
    ALPHA = 1
    LUMINANCE = 2

    @staticmethod
    def from_string(s: str) -> "MatteMode":
        if s in STRING_TO_MATTE_MODE:
            return STRING_TO_MATTE_MODE[s]
        else:
            raise ValueError(f"Unknown matte mode: {s}")


STRING_TO_MATTE_MODE = {
    "none": MatteMode.NONE,
    "alpha": MatteMode.ALPHA,
    "luminance": MatteMode.LUMINANCE,
}


class Direction(Enum):
    BOTTOM_LEFT = 1
    BOTTOM_CENTER = 2
    BOTTOM_RIGHT = 3
    CENTER_LEFT = 4
    CENTER = 5
    CENTER_RIGHT = 6
    TOP_LEFT = 7
    TOP_CENTER = 8
    TOP_RIGHT = 9

    @staticmethod
    def from_string(s: str) -> "Direction":
        if s in STRING_TO_DIRECTION:
            return STRING_TO_DIRECTION[s]
        else:
            raise ValueError(f"Unknown origin point: {s}")

    @staticmethod
    def to_vector(d: "Direction", size: tuple[float, float]) -> tuple[float, float]:
        if d == Direction.BOTTOM_LEFT:
            return (0, size[1])
        elif d == Direction.BOTTOM_CENTER:
            return (size[0] / 2, size[1])
        elif d == Direction.BOTTOM_RIGHT:
            return (size[0], size[1])
        elif d == Direction.CENTER_LEFT:
            return (0, size[1] / 2)
        elif d == Direction.CENTER:
            return (size[0] / 2, size[1] / 2)
        elif d == Direction.CENTER_RIGHT:
            return (size[0], size[1] / 2)
        elif d == Direction.TOP_LEFT:
            return (0, 0)
        elif d == Direction.TOP_CENTER:
            return (size[0] / 2, 0)
        elif d == Direction.TOP_RIGHT:
            return (size[0], 0)
        else:
            raise ValueError(f"Unknown direction: {d}")


STRING_TO_DIRECTION = {
    "bottom_left": Direction.BOTTOM_LEFT,
    "bottom_center": Direction.BOTTOM_CENTER,
    "bottom_right": Direction.BOTTOM_RIGHT,
    "center_left": Direction.CENTER_LEFT,
    "center": Direction.CENTER,
    "center_right": Direction.CENTER_RIGHT,
    "top_left": Direction.TOP_LEFT,
    "top_center": Direction.TOP_CENTER,
    "top_right": Direction.TOP_RIGHT,
}


class TextAlignment(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2

    @staticmethod
    def from_string(s: str) -> "TextAlignment":
        if s in STRING_TO_TEXT_ALIGNMENT:
            return STRING_TO_TEXT_ALIGNMENT[s]
        else:
            raise ValueError(f"Unknown text alignment: {s}")


STRING_TO_TEXT_ALIGNMENT = {
    "left": TextAlignment.LEFT,
    "center": TextAlignment.CENTER,
    "right": TextAlignment.RIGHT,
}
