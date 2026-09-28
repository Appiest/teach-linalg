"""Shared look and motion for every lesson video.

Import with `from engine.theme import *` from a lesson's scene.py.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    Arrow,
    Create,
    DecimalNumber,
    Dot,
    FadeIn,
    FadeOut,
    GrowFromCenter,
    Line,
    MathTex,
    Matrix,
    NumberLine,
    NumberPlane,
    Scene,
    Tex,
    ValueTracker,
    VGroup,
    config,
)

PALETTE = json.loads((Path(__file__).with_name("palette.json")).read_text())
Palette = type("Palette", (), PALETTE)
config.background_color = PALETTE["background"]


class Timing:
    beat = 1.0
    read_short = 2.0
    read_long = 3.5


def spring(t: float, damping: float = 0.78, stiffness: float = 11.0) -> float:
    """Closed-form underdamped step response, pinned so spring(1) == 1.

    damping 0.78 gives roughly 2% overshoot.
    """
    omega_d = stiffness * math.sqrt(1 - damping**2)
    decay = math.exp(-damping * stiffness * t)
    raw = 1 - decay * (math.cos(omega_d * t) + (damping * stiffness / omega_d) * math.sin(omega_d * t))
    end = 1 - math.exp(-damping * stiffness) * (
        math.cos(omega_d) + (damping * stiffness / omega_d) * math.sin(omega_d)
    )
    return raw + t * (1 - end)


def spring_soft(t: float) -> float:
    return spring(t, damping=0.92, stiffness=8.0)


def make_plane(x_range=(-8, 8, 1), y_range=(-5, 5, 1), **kwargs) -> NumberPlane:
    return NumberPlane(
        x_range=x_range,
        y_range=y_range,
        background_line_style={"stroke_color": Palette.grid, "stroke_width": 1.6, "stroke_opacity": 0.55},
        faded_line_style={"stroke_color": Palette.grid_faint, "stroke_width": 1, "stroke_opacity": 0.5},
        faded_line_ratio=2,
        axis_config={"stroke_color": Palette.axis, "stroke_width": 2.2},
        **kwargs,
    )


def vector_arrow(coords, color: str = Palette.yellow, plane: NumberPlane | None = None, stroke_width: float = 6) -> Arrow:
    start = plane.c2p(0, 0) if plane else ORIGIN
    end = plane.c2p(*coords[:2]) if plane else np.array([coords[0], coords[1], 0.0])
    return Arrow(
        start,
        end,
        buff=0,
        color=color,
        stroke_width=stroke_width,
        max_tip_length_to_length_ratio=0.18,
        max_stroke_width_to_length_ratio=12,
    )


def column(entries, color: str = Palette.text, **kwargs) -> Matrix:
    col = Matrix([[e] for e in entries], v_buff=0.62, bracket_h_buff=0.14, **kwargs)
    col.set_color(color)
    return col


def matrix(rows, color: str = Palette.text, **kwargs) -> Matrix:
    mat = Matrix(rows, v_buff=0.62, h_buff=0.9, bracket_h_buff=0.14, **kwargs)
    mat.set_color(color)
    return mat


def slider(label_tex: str, tracker: ValueTracker, color: str, x_range=(-3, 3, 1), length: float = 3.2) -> VGroup:
    """A labelled track whose knob and readout follow the tracker."""
    track = NumberLine(x_range=x_range, length=length, color=Palette.text_muted, stroke_width=2, include_ticks=True, tick_size=0.05)
    knob = Dot(radius=0.1, color=color)
    knob.add_updater(lambda m: m.move_to(track.n2p(tracker.get_value())))
    label = MathTex(label_tex, "=", color=color, font_size=38)
    label.next_to(track, LEFT, buff=0.35)
    readout = DecimalNumber(tracker.get_value(), num_decimal_places=2, include_sign=True, color=color, font_size=38)
    readout.add_updater(lambda m: m.set_value(tracker.get_value()).next_to(label, RIGHT, buff=0.15))
    track.shift(RIGHT * 1.6)
    label.next_to(track, LEFT, buff=1.75)
    return VGroup(label, readout, track, knob)


def backed(mobject, padding: float = 0.18, opacity: float = 0.92):
    """Put a dark plate behind text that sits on top of the grid."""
    mobject.add_background_rectangle(color=Palette.background, opacity=opacity, buff=padding)
    return mobject


def caption(text: str, **kwargs) -> Tex:
    """One line of on-screen explanation at the bottom of frame."""
    line = Tex(text, color=Palette.text, font_size=kwargs.pop("font_size", 40), **kwargs)
    line.to_edge(DOWN, buff=0.55)
    return backed(line, padding=0.22, opacity=0.9)


def fit_to_frame(scene: Scene, margin: float = 0.35) -> None:
    """Scale a still figure's contents to fill the frame."""
    group = VGroup(*scene.mobjects)
    factor = min((config.frame_width - 2 * margin) / group.width, (config.frame_height - 2 * margin) / group.height)
    group.scale(factor).move_to(ORIGIN)


def origin_pulse(plane: NumberPlane | None = None) -> VGroup:
    """The series motif: every episode begins from a glowing origin."""
    center = plane.c2p(0, 0) if plane else ORIGIN
    halo = Dot(center, radius=0.32, color=Palette.glow, fill_opacity=0.18)
    core = Dot(center, radius=0.07, color=Palette.glow)
    return VGroup(halo, core)


SOUNDS = Path(__file__).with_name("sounds")

# First matching animation in a play() call picks its sound: (sound, gain in dB).
# Render with --disable_caching: cached animations skip play() and drop their sounds.
ANIMATION_SOUNDS = {
    "LaggedStart": ("shimmer", -4),
    "GrowArrow": ("whoosh", -2),
    "GrowFromCenter": ("pop", -9),
    "GrowFromPoint": ("pop", -9),
    "Create": ("sweep", -3),
    "DrawBorderThenFill": ("sweep", -6),
    "Write": ("swish", -8),
    "TransformFromCopy": ("swish", -3),
    "Transform": ("swish", -4),
    "ReplacementTransform": ("swish", -4),
    "Indicate": ("tick", -2),
    "Flash": ("tick", -2),
    "Circumscribe": ("tick", -4),
    "_MethodAnimation": ("slide", -2),
    "_AnimationBuilder": ("slide", -2),
    "ApplyMatrix": ("slide", -2),
}


def sound_for(animations) -> tuple[str, float] | None:
    names = [type(animation).__name__ for animation in animations]
    for name, cue in ANIMATION_SOUNDS.items():
        if name in names:
            return cue
    return None


class LessonScene(Scene):
    """Base scene with the shared opening, captions, closing card and automatic sound effects."""

    day: int = 0
    title: str = ""
    quiet: bool = False

    def sfx(self, name: str, gain: float = 0) -> None:
        self.add_sound(str(SOUNDS / f"{name}.wav"), gain=gain)

    def play(self, *animations, **kwargs):
        cue = None if self.quiet else sound_for(animations)
        if cue:
            self.sfx(*cue)
        return super().play(*animations, **kwargs)

    def open_episode(self, plane: NumberPlane | None = None) -> VGroup:
        title = Tex(self.title, color=Palette.text, font_size=84)
        title.width = min(title.width, config.frame_width - 1.5)
        day = Tex(f"Day {self.day}", color=Palette.text_muted, font_size=40)
        card = VGroup(title, day).arrange(DOWN, buff=0.35)
        self.sfx("chime", gain=-2)
        self.play(FadeIn(card, shift=UP * 0.2), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_long)
        self.play(FadeOut(card, shift=UP * 0.2), run_time=0.7)
        pulse = origin_pulse(plane)
        self.play(GrowFromCenter(pulse), run_time=0.8, rate_func=spring)
        if plane is not None:
            self.play(Create(plane, lag_ratio=0.02), run_time=2.2)
        return pulse

    def say(self, text: str, current: Tex | None = None, hold: float = Timing.read_short, **kwargs) -> Tex:
        """Swap the bottom caption. Old line leaves before the new one enters."""
        line = caption(text, **kwargs)
        if current is not None:
            self.play(FadeOut(current, shift=DOWN * 0.15), run_time=0.35)
        self.play(FadeIn(line, shift=UP * 0.15), run_time=0.5)
        self.wait(hold)
        return line

    def close_episode(self, takeaway_tex: str, *leftovers) -> None:
        if leftovers:
            self.play(*[FadeOut(m) for m in leftovers], run_time=0.8)
        idea = Tex(takeaway_tex, color=Palette.text, font_size=48)
        idea.width = min(idea.width, config.frame_width - 2)
        pulse = origin_pulse().next_to(idea, DOWN, buff=0.7)
        self.sfx("chime", gain=-4)
        self.play(FadeIn(idea, shift=UP * 0.2), run_time=1.0, rate_func=spring_soft)
        self.play(GrowFromCenter(pulse), run_time=0.8, rate_func=spring)
        self.wait(Timing.read_long + 1.5)
        self.play(FadeOut(idea), FadeOut(pulse), run_time=0.8)


def augmented(rows, color: str = Palette.text, **kwargs) -> Matrix:
    """An augmented matrix: a vertical bar separates the last column (the constants) from the coefficients."""
    mat = matrix([[str(entry) for entry in row] for row in rows], **kwargs)
    mat.set_color(color)
    entries = mat.get_columns()
    bar_x = (entries[-2].get_right()[0] + entries[-1].get_left()[0]) / 2
    brackets = mat.get_brackets()
    top, bottom = brackets.get_top()[1] - 0.12, brackets.get_bottom()[1] + 0.12
    bar = Line([bar_x, top, 0], [bar_x, bottom, 0], color=color, stroke_width=2.5)
    mat.add(bar)
    mat.bar = bar
    return mat


def clip_line_to_box(coeffs, x_range, y_range):
    """Endpoints of a*x + b*y = c inside the box, or None when the line misses it or is degenerate."""
    a, b, c = coeffs
    norm = a * a + b * b
    if norm < 1e-12:
        return None
    base = np.array([a * c / norm, b * c / norm])
    direction = np.array([-b, a]) / math.sqrt(norm)
    low, high = -1e9, 1e9
    for axis, (lo, hi) in enumerate((x_range, y_range)):
        if abs(direction[axis]) < 1e-12:
            if not lo <= base[axis] <= hi:
                return None
            continue
        ends = sorted(((lo - base[axis]) / direction[axis], (hi - base[axis]) / direction[axis]))
        low, high = max(low, ends[0]), min(high, ends[1])
    if low >= high:
        return None
    return base + low * direction, base + high * direction


def equation_line(plane: NumberPlane, coeffs, color: str = Palette.yellow, stroke_width: float = 5):
    """The line a*x1 + b*x2 = c across the visible plane. Invisible when it misses the plane."""
    ends = clip_line_to_box(coeffs, plane.x_range[:2], plane.y_range[:2])
    if ends is None:
        return Line(plane.c2p(0, 0), plane.c2p(0, 0), stroke_opacity=0)
    return Line(plane.c2p(*ends[0]), plane.c2p(*ends[1]), color=color, stroke_width=stroke_width)
