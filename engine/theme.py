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
    Arrow3D,
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
    Surface,
    Tex,
    ThreeDScene,
    Transform,
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


CAPTION_Z = 100


def caption(text: str, **kwargs) -> Tex:
    """One line of on-screen explanation at the bottom of frame."""
    line = Tex(text, color=Palette.text, font_size=kwargs.pop("font_size", 40), **kwargs)
    line.to_edge(DOWN, buff=0.55)
    return backed(line, padding=0.22, opacity=0.9).set_z_index(CAPTION_Z)


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


def clip_to_box(start, end, x_limits, y_limits):
    """The part of segment start-end inside the box, or None (Liang-Barsky)."""
    start, end = np.asarray(start, dtype=float), np.asarray(end, dtype=float)
    delta = end - start
    low, high = 0.0, 1.0
    for axis, (lower, upper) in enumerate((x_limits, y_limits)):
        for step, gap in ((-delta[axis], start[axis] - lower), (delta[axis], upper - start[axis])):
            if step == 0:
                if gap < 0:
                    return None
                continue
            ratio = gap / step
            low, high = (max(low, ratio), high) if step < 0 else (low, min(high, ratio))
    return (start + low * delta, start + high * delta) if low < high else None


def skewed_grid(plane: NumberPlane, v, w, reach: int = 12, color: str = Palette.teal, opacity: float = 0.5, box=None) -> VGroup:
    """Lines of a*v + t*w and t*v + b*w for integer a and b, clipped to box (plane coords, default the plane)."""
    v = np.array([v[0], v[1]], dtype=float)
    w = np.array([w[0], w[1]], dtype=float)
    x_limits, y_limits = box or (tuple(plane.x_range[:2]), tuple(plane.y_range[:2]))
    lines = VGroup()
    for k in range(-reach, reach + 1):
        for offset, direction in ((k * v, w), (k * w, v)):
            segment = clip_to_box(offset - reach * direction, offset + reach * direction, x_limits, y_limits)
            if segment is not None:
                lines.add(Line(plane.c2p(*segment[0]), plane.c2p(*segment[1]), color=color, stroke_width=1.6, stroke_opacity=opacity))
    return lines


def vector_arrow_3d(axes, coords, color: str = Palette.yellow, start=(0, 0, 0)) -> Arrow3D:
    return Arrow3D(axes.c2p(*start), axes.c2p(*coords), color=color, thickness=0.025, height=0.28, base_radius=0.09, resolution=12)


def span_sheet(axes, u, v, s_range=(-1, 1), t_range=(-1, 1), color: str = Palette.teal, resolution=(8, 8), opacity: float = 0.32) -> Surface:
    """The parallelogram of combinations s*u + t*v over the given weight ranges."""
    u = np.array(u, dtype=float)
    v = np.array(v, dtype=float)
    return Surface(
        lambda s, t: axes.c2p(*(s * u + t * v)),
        u_range=s_range,
        v_range=t_range,
        resolution=resolution,
        checkerboard_colors=[color, color],
        fill_opacity=opacity,
        stroke_color=color,
        stroke_width=0.8,
        stroke_opacity=0.6,
    )


class LessonScene3D(LessonScene, ThreeDScene):
    """LessonScene with a 3D camera. It opens flat, and captions and overlays stay pinned to the screen."""

    def pin(self, *mobjects):
        self.add_fixed_in_frame_mobjects(*mobjects)
        return mobjects[0] if len(mobjects) == 1 else VGroup(*mobjects)

    def say(self, text: str, current: Tex | None = None, hold: float = Timing.read_short, **kwargs) -> Tex:
        line = caption(text, **kwargs)
        if current is not None:
            self.play(FadeOut(current, shift=DOWN * 0.15), run_time=0.35)
        self.pin(line)
        self.play(FadeIn(line, shift=UP * 0.15), run_time=0.5)
        self.wait(hold)
        return line


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


def morph_matrix(scene: Scene, mat: Matrix, target: Matrix, *extra, **play_kwargs) -> None:
    """Morph mat into target. Entries whose value changes crossfade instead of melting between glyph shapes."""
    old_entries, new_entries = mat.get_entries(), target.get_entries()
    changed = [i for i, (old, new) in enumerate(zip(old_entries, new_entries)) if old.get_tex_string() != new.get_tex_string()]
    leaving = VGroup(*[old_entries[i].copy() for i in changed])
    arriving = VGroup(*[new_entries[i].copy() for i in changed])
    for i in changed:
        old_entries[i].set_opacity(0)
        new_entries[i].set_opacity(0)
    scene.add(leaving)
    scene.play(Transform(mat, target), FadeOut(leaving), FadeIn(arriving), *extra, **play_kwargs)
    for i in changed:
        old_entries[i].set_opacity(1)
    scene.remove(arriving)


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


def plane_at(origin, unit: float = 1.0) -> NumberPlane:
    """A grid that fills the frame, with its origin placed at `origin` and `unit` scene units per grid step."""
    half_width, half_height = config.frame_width / 2, config.frame_height / 2
    x_min = math.floor((-half_width - origin[0]) / unit) - 1
    x_max = math.ceil((half_width - origin[0]) / unit) + 1
    y_min = math.floor((-half_height - origin[1]) / unit) - 1
    y_max = math.ceil((half_height - origin[1]) / unit) + 1
    plane = make_plane(
        x_range=(x_min, x_max, 1),
        y_range=(y_min, y_max, 1),
        x_length=(x_max - x_min) * unit,
        y_length=(y_max - y_min) * unit,
    )
    plane.shift(np.array([origin[0], origin[1], 0.0]) - plane.c2p(0, 0))
    return plane


def arrow_between(plane: NumberPlane, start, end, color: str, stroke_width: float = 6) -> Arrow:
    """A vector drawn from `start` to `end` in plane coordinates, for tip-to-tail pictures."""
    return Arrow(
        plane.c2p(*start[:2]),
        plane.c2p(*end[:2]),
        buff=0,
        color=color,
        stroke_width=stroke_width,
        max_tip_length_to_length_ratio=0.18,
        max_stroke_width_to_length_ratio=12,
    )


def plate_for(mobject, padding: float = 0.25, opacity: float = 0.92):
    """A borderless dark plate sized to `mobject`, for panels that grow as content is added."""
    from manim import Rectangle

    plate = Rectangle(
        width=mobject.width + 2 * padding,
        height=mobject.height + 2 * padding,
        fill_color=Palette.background,
        fill_opacity=opacity,
        stroke_width=0,
    )
    return plate.move_to(mobject)


def scrim(opacity: float = 0.96):
    """A full-frame veil that pushes the plane into the background while math takes the stage."""
    from manim import Rectangle

    return Rectangle(
        width=config.frame_width + 1,
        height=config.frame_height + 1,
        fill_color=Palette.background,
        fill_opacity=opacity,
        stroke_width=0,
    )


class MatrixTracker:
    """A 2x2 matrix held in four value trackers, so grids and arrows can follow it as it springs to a new matrix."""

    def __init__(self, rows=((1, 0), (0, 1)), offset=(0, 0)):
        self.entries = [ValueTracker(value) for row in rows for value in row]
        self.shift = [ValueTracker(value) for value in offset]

    def rows(self):
        a, b, c, d = (tracker.get_value() for tracker in self.entries)
        return (a, b), (c, d)

    def offset(self):
        return tuple(tracker.get_value() for tracker in self.shift)

    def apply(self, point):
        (a, b), (c, d) = self.rows()
        dx, dy = self.offset()
        return (a * point[0] + b * point[1] + dx, c * point[0] + d * point[1] + dy)

    def columns(self):
        (a, b), (c, d) = self.rows()
        return (a, c), (b, d)

    def to(self, rows):
        values = [value for row in rows for value in row]
        return [tracker.animate.set_value(value) for tracker, value in zip(self.entries, values)]

    def slide_to(self, offset):
        return [tracker.animate.set_value(value) for tracker, value in zip(self.shift, offset)]

    def turn_to(self, angle: float, start: float = 0.0):
        """Rotate from angle `start` to `angle` through true rotations, so the grid turns instead of shrinking."""
        from manim import UpdateFromAlphaFunc

        def set_angle(_, alpha):
            phi = start + (angle - start) * alpha
            for tracker, value in zip(self.entries, (math.cos(phi), -math.sin(phi), math.sin(phi), math.cos(phi))):
                tracker.set_value(value)

        return UpdateFromAlphaFunc(self.entries[0], set_angle)


def moved_grid(plane: NumberPlane, tracker: MatrixTracker, reach: int = 14, color: str = Palette.blue, opacity: float = 0.6) -> VGroup:
    """The image of the integer grid under tracker's current map, clipped to the plane, with the image axes brighter."""
    i_image, j_image = (np.array(column, dtype=float) for column in tracker.columns())
    shift = np.array(tracker.offset(), dtype=float)
    x_limits, y_limits = tuple(plane.x_range[:2]), tuple(plane.y_range[:2])
    lines = VGroup()
    for k in range(-reach, reach + 1):
        for base, direction in ((k * i_image, j_image), (k * j_image, i_image)):
            if np.linalg.norm(direction) < 1e-6:
                continue
            segment = clip_to_box(shift + base - reach * direction, shift + base + reach * direction, x_limits, y_limits)
            if segment is None:
                continue
            axis = k == 0
            lines.add(
                Line(
                    plane.c2p(*segment[0]),
                    plane.c2p(*segment[1]),
                    color=Palette.axis if axis else color,
                    stroke_width=2.4 if axis else 1.8,
                    stroke_opacity=0.95 if axis else opacity,
                )
            )
    return lines


def moved_polygon(plane: NumberPlane, tracker: MatrixTracker, corners, color: str = Palette.yellow, opacity: float = 0.3):
    """The image of a polygon (plane coords) under tracker's current map, filled and without an outline."""
    from manim import Polygon

    return Polygon(*[plane.c2p(*tracker.apply(corner)) for corner in corners], color=color, fill_opacity=opacity, stroke_width=0)
def shear_matrix(amount: float = 1.0) -> np.ndarray:
    """The horizontal shear [[1, amount], [0, 1]]."""
    return np.array([[1.0, amount], [0.0, 1.0]])


def turn_matrix(angle: float) -> np.ndarray:
    """Counterclockwise rotation by `angle` radians."""
    return np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])


def matrix_grid(plane: NumberPlane, transform, box=None, color: str = Palette.blue, opacity: float = 0.6, reach: int = 12) -> VGroup:
    """The plane's integer grid carried by a 2x2 matrix, clipped to box (plane coords, default the plane)."""
    transform = np.asarray(transform, dtype=float)
    return skewed_grid(plane, transform[:, 0], transform[:, 1], reach=reach, color=color, opacity=opacity, box=box)
def oblique_projector(origin=(0.0, 0.0), unit: float = 1.0, azimuth: float = math.radians(30), elevation: float = math.radians(25)):
    """A fixed orthographic view of 3D coordinates drawn in a flat scene: x toward the viewer, y right, z up."""
    center = np.array([origin[0], origin[1], 0.0])

    def project(point):
        x, y, z = (float(value) for value in point)
        across = -x * math.sin(azimuth) + y * math.cos(azimuth)
        depth = x * math.cos(azimuth) + y * math.sin(azimuth)
        up = z * math.cos(elevation) - depth * math.sin(elevation)
        return center + unit * np.array([across, up, 0.0])

    return project


def projected_axes(project, reach=((-1, 3), (-2, 4), (-2, 2)), labels=("x", "y", "z"), floor: bool = True) -> VGroup:
    """Three labelled axes seen through `project`, with a faint grid on the floor plane z = 0 for depth."""
    axes = VGroup()
    if floor:
        for x in range(reach[0][0], reach[0][1] + 1):
            axes.add(Line(project((x, reach[1][0], 0)), project((x, reach[1][1], 0)), color=Palette.grid_faint, stroke_width=1.2))
        for y in range(reach[1][0], reach[1][1] + 1):
            axes.add(Line(project((reach[0][0], y, 0)), project((reach[0][1], y, 0)), color=Palette.grid_faint, stroke_width=1.2))
    for index, (low, high) in enumerate(reach):
        start, end = np.zeros(3), np.zeros(3)
        start[index], end[index] = low, high + 0.4
        axes.add(Line(project(start), project(end), color=Palette.axis, stroke_width=2))
        label = MathTex(labels[index], color=Palette.text_muted, font_size=34)
        tip = project(end)
        away = tip - project((0, 0, 0))
        label.move_to(tip + 0.32 * away / np.linalg.norm(away))
        axes.add(label)
    return axes


def projected_arrow(project, coords, color: str = Palette.yellow, start=(0, 0, 0), stroke_width: float = 6) -> Arrow:
    """An arrow between two 3D points seen through `project`."""
    return Arrow(
        project(start),
        project(coords),
        buff=0,
        color=color,
        stroke_width=stroke_width,
        max_tip_length_to_length_ratio=0.2,
        max_stroke_width_to_length_ratio=12,
    )
def wide_plane_at(origin, unit: float = 1.0, reach: int = 40) -> NumberPlane:
    """A grid far larger than the frame, origin at `origin`, so it still fills the frame after a shear or stretch."""
    plane = make_plane(
        x_range=(-reach, reach, 1),
        y_range=(-reach, reach, 1),
        x_length=2 * reach * unit,
        y_length=2 * reach * unit,
    )
    plane.shift(np.array([origin[0], origin[1], 0.0]) - plane.c2p(0, 0))
    return plane


def cell_outline(mat: Matrix, lower: bool = True, color: str = Palette.text_muted, pad: float = 0.1):
    """A dashed staircase around the entries strictly below (or above) the main diagonal of a square Matrix."""
    from manim import DashedVMobject, VMobject

    rows = mat.get_rows()
    size = len(rows)
    first = rows[0][0].get_center()
    step_x = mat.get_columns()[1].get_center()[0] - mat.get_columns()[0].get_center()[0]
    step_y = rows[0].get_center()[1] - rows[1].get_center()[1]
    staircase = [point for i in range(1, size) for point in ((i - 0.62, i - 0.5), (i - 0.62, i + 0.5))]
    staircase += [(-0.5, size - 0.5), (-0.5, 0.5)]
    if not lower:
        staircase = [(row, col) for col, row in staircase]
    cells = VGroup(*[rows[r][c] for r in range(size) for c in range(size) if (r > c if lower else r < c)])
    x_low, x_high = cells.get_left()[0] - pad, cells.get_right()[0] + pad
    y_low, y_high = cells.get_bottom()[1] - pad, cells.get_top()[1] + pad
    corners = [
        [min(max(first[0] + col * step_x, x_low), x_high), min(max(first[1] - row * step_y, y_low), y_high), 0]
        for col, row in staircase
    ]
    outline = VMobject(color=color, stroke_width=3).set_points_as_corners([*corners, corners[0]])
    return DashedVMobject(outline, num_dashes=48)
class LiveMatrix:
    """A 2x2 matrix held in ValueTrackers, so a grid and its basis arrows can follow it while it changes."""

    def __init__(self, entries=((1, 0), (0, 1))):
        self.trackers = [[ValueTracker(float(value)) for value in row] for row in entries]

    def value(self) -> np.ndarray:
        return np.array([[tracker.get_value() for tracker in row] for row in self.trackers])

    def column(self, index: int):
        current = self.value()
        return (current[0, index], current[1, index])

    def move_to(self, target) -> list:
        """Animations that carry every entry to `target`. Entries move linearly, so the grid moves like ApplyMatrix."""
        return [
            tracker.animate.set_value(float(value))
            for tracker_row, value_row in zip(self.trackers, target)
            for tracker, value in zip(tracker_row, value_row)
        ]

    def left_multiply(self, factor) -> list:
        """Animations that apply `factor` after the current matrix, as a row operation does."""
        return self.move_to(np.array(factor, dtype=float) @ self.value())


def live_grid(plane: NumberPlane, live: LiveMatrix, color: str = Palette.blue, opacity: float = 0.55, reach: int = 20):
    """The image of the integer grid under `live`, redrawn every frame and clipped to the plane."""
    from manim import always_redraw

    return always_redraw(lambda: skewed_grid(plane, live.column(0), live.column(1), reach=reach, color=color, opacity=opacity))


def live_basis_arrows(plane: NumberPlane, live: LiveMatrix) -> VGroup:
    """Green and red arrows to where i-hat and j-hat land under `live`: its two columns."""
    from manim import always_redraw

    return VGroup(
        always_redraw(lambda: vector_arrow(live.column(0), Palette.i_hat, plane)),
        always_redraw(lambda: vector_arrow(live.column(1), Palette.j_hat, plane)),
    )


def augmented_block(rows, split: int, color: str = Palette.text, **kwargs) -> Matrix:
    """A matrix with a vertical bar after column `split`, like [A | I]. Entries may be numbers or TeX strings."""
    mat = matrix([[str(entry) for entry in row] for row in rows], **kwargs)
    mat.set_color(color)
    columns = mat.get_columns()
    bar_x = (columns[split - 1].get_right()[0] + columns[split].get_left()[0]) / 2
    brackets = mat.get_brackets()
    top, bottom = brackets.get_top()[1] - 0.12, brackets.get_bottom()[1] + 0.12
    bar = Line([bar_x, top, 0], [bar_x, bottom, 0], color=color, stroke_width=2.5)
    mat.add(bar)
    mat.bar = bar
    return mat
def rotation_2d(angle: float) -> np.ndarray:
    cosine, sine = math.cos(angle), math.sin(angle)
    return np.array([[cosine, -sine], [sine, cosine]])


class LiveTransform:
    """A 2x2 matrix that changes one move at a time, for grids and arrows drawn with always_redraw.

    Each move left-multiplies the current matrix. A plain move follows (1 - s)I + sE, so undoing A walks the straight
    path from A back to I. A rotation turns through its angle so the grid never shrinks on the way.
    """

    def __init__(self, start=None):
        self.base = np.eye(2) if start is None else np.array(start, dtype=float)
        self.step = lambda s: np.eye(2)
        self.progress = ValueTracker(0)

    @property
    def value(self) -> np.ndarray:
        return self.step(self.progress.get_value()) @ self.base

    def apply(self, move):
        self.base = self.value
        target = np.array(move, dtype=float)
        self.step = lambda s: (1 - s) * np.eye(2) + s * target
        self.progress.set_value(0)
        return self.progress.animate.set_value(1)

    def rotate(self, angle: float):
        self.base = self.value
        self.step = lambda s: rotation_2d(s * angle)
        self.progress.set_value(0)
        return self.progress.animate.set_value(1)

    def point(self, coords) -> np.ndarray:
        return self.value @ np.asarray(coords[:2], dtype=float)

    def reach(self, plane: NumberPlane, cap: int = 40) -> int:
        """How many grid steps the transformed grid needs so it still covers the visible plane."""
        corners = [(x, y) for x in plane.x_range[:2] for y in plane.y_range[:2]]
        if abs(np.linalg.det(self.value)) < 1e-3:
            return cap
        inverse = np.linalg.inv(self.value)
        return min(cap, int(max(np.abs(inverse @ np.array(corner)).max() for corner in corners)) + 2)

    def grid(self, plane: NumberPlane, color: str = Palette.grid, opacity: float = 0.85, cap: int = 40) -> VGroup:
        first, second = self.value[:, 0], self.value[:, 1]
        return skewed_grid(plane, first, second, reach=self.reach(plane, cap), color=color, opacity=opacity)


class OrbitingView:
    """An oblique 3D view in a flat scene whose azimuth (degrees) is a ValueTracker, so always_redraw drawings orbit."""

    def __init__(self, origin, unit: float = 1.0, azimuth: float = -30.0, elevation: float = 25.0):
        self.origin, self.unit, self.elevation = origin, unit, elevation
        self.azimuth = ValueTracker(azimuth)

    def project(self, point) -> np.ndarray:
        view = oblique_projector(self.origin, self.unit, math.radians(self.azimuth.get_value()), math.radians(self.elevation))
        return view(point)

    def turn_to(self, azimuth: float):
        return self.azimuth.animate.set_value(azimuth)


def floor_and_axes(project, reach=((-2, 3), (-2, 3), (-2, 2))) -> VGroup:
    """Unlabelled x, y and z axes seen through `project`, over a faint grid on the floor z = 0."""
    parts = VGroup()
    for x in range(reach[0][0], reach[0][1] + 1):
        parts.add(Line(project((x, reach[1][0], 0)), project((x, reach[1][1], 0)), color=Palette.grid_faint, stroke_width=1.2))
    for y in range(reach[1][0], reach[1][1] + 1):
        parts.add(Line(project((reach[0][0], y, 0)), project((reach[0][1], y, 0)), color=Palette.grid_faint, stroke_width=1.2))
    for index, (low, high) in enumerate(reach):
        start, end = np.zeros(3), np.zeros(3)
        start[index], end[index] = low, high + 0.4
        parts.add(Line(project(start), project(end), color=Palette.axis, stroke_width=2))
    return parts


def clipped_plot(axes, function, x_range, y_range, color: str, stroke_width: float = 5, samples: int = 240) -> VGroup:
    """The graph of `function` on `axes` over x_range, cut wherever it leaves y_range so it stays inside its panel."""
    from manim import VMobject

    pieces, run = VGroup(), []
    for x in np.linspace(x_range[0], x_range[1], samples):
        y = function(x)
        if y_range[0] <= y <= y_range[1]:
            run.append(axes.c2p(x, y))
            continue
        if len(run) > 1:
            pieces.add(VMobject(color=color, stroke_width=stroke_width).set_points_smoothly(run))
        run = []
    if len(run) > 1:
        pieces.add(VMobject(color=color, stroke_width=stroke_width).set_points_smoothly(run))
    return pieces
def line_through_origin(plane: NumberPlane, direction, color: str = Palette.yellow, stroke_width: float = 4, dashed: bool = False, opacity: float = 1.0):
    """The whole line through the origin along `direction`, clipped to the plane: a span, or an eigenspace."""
    from manim import DashedLine

    ends = clip_line_to_box((direction[1], -direction[0], 0), plane.x_range[:2], plane.y_range[:2])
    kind = DashedLine if dashed else Line
    return kind(plane.c2p(*ends[0]), plane.c2p(*ends[1]), color=color, stroke_width=stroke_width, stroke_opacity=opacity)
def signed_area(first, second) -> float:
    """det [first second]: the parallelogram's area, negative when the turn from first to second is clockwise."""
    return float(first[0] * second[1] - first[1] * second[0])


def signed_parallelogram(plane: NumberPlane, first, second, opacity: float = 0.32, stroke_width: float = 3, offset=(0, 0)):
    """The parallelogram on two columns: yellow when they turn counterclockwise, pink when the plane is flipped."""
    from manim import Polygon

    color = Palette.pink if signed_area(first, second) < -1e-9 else Palette.yellow
    corners = [(0, 0), first, (first[0] + second[0], first[1] + second[1]), second]
    points = [plane.c2p(corner[0] + offset[0], corner[1] + offset[1]) for corner in corners]
    return Polygon(*points, color=color, fill_opacity=opacity, stroke_width=stroke_width, stroke_opacity=0.95)


def orientation_arc(plane: NumberPlane, first, second, radius: float = 0.8, color: str = Palette.glow, min_turn: float = 0.22):
    """A small curved arrow at the origin turning the short way from `first` to `second`; empty when they nearly align."""
    from manim import Arc, VMobject

    start = math.atan2(first[1], first[0])
    turn = (math.atan2(second[1], second[0]) - start + math.pi) % (2 * math.pi) - math.pi
    if abs(turn) < min_turn:
        return VMobject()
    arc = Arc(radius=radius, start_angle=start, angle=turn, arc_center=plane.c2p(0, 0), color=color, stroke_width=4)
    return arc.add_tip(tip_length=0.18, tip_width=0.18)
