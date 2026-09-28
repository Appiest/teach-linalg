import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    Palette,
    Timing,
    arrow_between,
    backed,
    equation_line,
    fit_to_frame,
    make_plane,
    oblique_projector,
    plane_at,
    projected_arrow,
    projected_axes,
    slider,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (-1.5, -1.3)
PLANE_UNIT = 0.9
SLOPE = 0.5

U_ON = (2, 1)
V_ON = (4, 2)
U_OFF = (2, 2)
V_OFF = (-4, -1)
NAME_X = 7
TAGS_ON = (DR, DR, DR)
TAGS_OFF = (DR, LEFT, UL)

SPACE_ORIGIN = (0.4, -0.7)
SPACE_REACH = ((-2, 3), (-3, 4), (-1, 3))
V1 = (0, 2, 1)
V2 = (2, 0, -1)
PATCH_WEIGHTS = (-1.0, 1.25)
LIFT = (0, 0, 1)

CHECKS = (
    r"\mathbf 0 \text{ is in } H",
    r"\mathbf u + \mathbf v \text{ is in } H",
    r"c\,\mathbf u \text{ is in } H",
)

project = oblique_projector(SPACE_ORIGIN, unit=0.95)


def added(a, b):
    return tuple(x + y for x, y in zip(a, b))


def scaled(v, c):
    return tuple(c * x for x in v)


def line_coeffs(shift):
    """y = SLOPE * x + shift, written as a*x + b*y = c for equation_line."""
    return (-SLOPE, 1, shift)


def set_line(plane, shift):
    return equation_line(plane, line_coeffs(shift), color=Palette.purple_gray, stroke_width=6)


def line_rule(shift):
    return r"y = \tfrac12 x" if shift == 0 else rf"y = \tfrac12 x + {shift}"


def set_name(plane, shift):
    """The set's name, tucked above the right end of its line."""
    name = backed(MathTex(r"H:\;", line_rule(shift), color=Palette.purple_gray, font_size=40), padding=0.14)
    return name.next_to(plane.c2p(NAME_X, SLOPE * NAME_X + shift), UL, buff=0.05)


def tick_mark(color=Palette.teal):
    mark = VMobject(color=color, stroke_width=6)
    mark.set_points_as_corners([LEFT * 0.16 + UP * 0.02, DOWN * 0.14 + LEFT * 0.02, RIGHT * 0.2 + UP * 0.2])
    return mark


def cross_mark(color=Palette.glow):
    size = 0.15
    return VGroup(
        Line(UL * size, DR * size, color=color, stroke_width=6),
        Line(UR * size, DL * size, color=color, stroke_width=6),
    )


def checklist():
    rows = VGroup()
    for letter, statement in zip("abc", CHECKS):
        label = Tex(f"({letter})", color=Palette.text_muted, font_size=36)
        body = MathTex(statement, color=Palette.text, font_size=38)
        rows.add(VGroup(label, body).arrange(RIGHT, buff=0.25))
    rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    return backed(rows, padding=0.22).to_corner(UL, buff=0.45)


def mark_slot(rows, index):
    """Where the tick or cross for row `index` sits, just right of the widest row."""
    right = max(row.get_right()[0] for row in rows[:3])
    return np.array([right + 0.45, rows[index].get_center()[1], 0])


def name_tag(tex, color, point, direction, buff=0.12):
    return backed(MathTex(tex, color=color, font_size=38), padding=0.08).next_to(point, direction, buff=buff)


def ring_at(point, radius=0.24):
    return Circle(radius=radius, color=Palette.glow, stroke_width=4).move_to(point)


def gap_segment(plane, bottom, top):
    return DashedLine(plane.c2p(*bottom), plane.c2p(*top), color=Palette.glow, stroke_width=4, dash_length=0.08)


def space_point(coords):
    return project(coords)


def patch_corners(offset=(0, 0, 0)):
    low, high = PATCH_WEIGHTS
    weights = [(low, low), (high, low), (high, high), (low, high)]
    return [project(added(added(scaled(V1, s), scaled(V2, t)), offset)) for s, t in weights]


def plane_patch(offset=(0, 0, 0)):
    return Polygon(
        *patch_corners(offset),
        color=Palette.purple_gray,
        fill_color=Palette.purple_gray,
        fill_opacity=0.22,
        stroke_width=2.5,
    )


def space_axes():
    return projected_axes(project, SPACE_REACH, labels=("x_1", "x_2", "x_3"))


def combination(s, t):
    return added(scaled(V1, s), scaled(V2, t))


def span_row(letter, left, right):
    label = Tex(f"({letter})", color=Palette.text_muted, font_size=38)
    body = MathTex(left, "=", right, color=Palette.text, font_size=42, substrings_to_isolate=[r"\mathbf v_1", r"\mathbf v_2"])
    body.set_color_by_tex(r"\mathbf v_1", Palette.yellow)
    body.set_color_by_tex(r"\mathbf v_2", Palette.blue)
    return VGroup(label, body).arrange(RIGHT, buff=0.3)


class Lesson(LessonScene):
    day = 11
    title = "Subspaces"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        self.plane = plane
        line = self.meet_the_line()
        line = self.through_origin(line)
        line = self.shift_the_line(line)
        line = self.shifted_sum(line)
        line = self.shifted_scaling(line)
        line = self.plane_in_space(line)
        line = self.any_span(line)
        self.close_episode(
            r"A subspace is a flat piece through the origin.\\"
            r"Adding and scaling never take you out of it.",
            *self.mobjects,
        )

    def meet_the_line(self):
        plane = self.plane
        self.h_line = set_line(plane, 0)
        self.h_name = set_name(plane, 0)
        line = self.say(r"Yesterday's vector spaces were sets closed under adding and scaling.", hold=0.2)
        self.play(Create(self.h_line), run_time=1.4, rate_func=smooth)
        self.play(FadeIn(self.h_name, shift=LEFT * 0.2), run_time=0.6)
        self.wait(Timing.beat)
        line = self.say(r"Is this line inside $\mathbb R^2$ a vector space on its own?", line, hold=Timing.read_short)
        line = self.say(r"A subspace sits inside a vector space and is one itself.", line, hold=Timing.read_short)
        line = self.say(r"Most spaces from here on sit inside a bigger one.", line, hold=Timing.read_short)

        self.checks = checklist()
        line = self.say(r"To test a set, three checks replace yesterday's ten rules.", line, hold=0.2)
        self.play(FadeIn(self.checks.background_rectangle), run_time=0.3)
        for row in self.checks[1:]:
            self.play(FadeIn(row, shift=RIGHT * 0.15), run_time=0.6, rate_func=spring_soft)
            self.wait(0.8)
        self.wait(Timing.read_short)
        return line

    def check_row(self, index, passed):
        mark = tick_mark() if passed else cross_mark()
        mark.move_to(mark_slot(self.checks[1:], index))
        self.sfx("pop" if passed else "tick", gain=-6)
        self.play(Create(mark), run_time=0.5)
        return mark

    def through_origin(self, line):
        plane = self.plane
        ring = ring_at(plane.c2p(0, 0))
        line = self.say(r"The origin is on the line, so (a) passes.", line, hold=0.2)
        self.play(Create(ring), run_time=0.7)
        marks = VGroup(self.check_row(0, True))
        self.wait(Timing.read_short)
        self.play(FadeOut(ring), run_time=0.4)

        line = self.say(r"The sum of two vectors on the line stays on it.", line, hold=0.2)
        u_arrow, v_arrow, sum_arrow, tags = self.add_on_line(U_ON, V_ON, TAGS_ON)
        marks.add(self.check_row(1, True))
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(v_arrow, sum_arrow, tags[1:])), u_arrow.animate.set_opacity(1), run_time=0.6)
        self.remove(u_arrow, tags[0])

        line = self.say(r"Scaling slides $c\,\mathbf u$ back and forth along the line.", line, hold=0.2)
        control = self.scale_along(U_ON, (2.5, -1.0, 0.0, 1.0), Palette.yellow, r"c\,\mathbf u")
        marks.add(self.check_row(2, True))
        line = self.say(r"This line passes all three checks, so it is a subspace.", line, hold=Timing.read_short)
        self.play(FadeOut(VGroup(control, marks)), run_time=0.6)
        return line

    def add_on_line(self, u, v, sides):
        """Grow u and v, slide v tip to tail onto u, then grow the teal sum. Returns the pieces."""
        plane = self.plane
        total = added(u, v)
        u_side, v_side, sum_side = sides
        u_arrow = vector_arrow(u, Palette.yellow, plane)
        v_arrow = vector_arrow(v, Palette.blue, plane)
        u_tag = name_tag(r"\mathbf u", Palette.yellow, plane.c2p(*u), u_side)
        v_tag = name_tag(r"\mathbf v", Palette.blue, plane.c2p(*v), v_side)
        self.play(GrowArrow(u_arrow), FadeIn(u_tag), run_time=1.0, rate_func=spring_soft)
        self.play(GrowArrow(v_arrow), FadeIn(v_tag), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.beat)
        self.play(
            Transform(v_arrow, arrow_between(plane, u, total, Palette.blue)),
            v_tag.animate.next_to(plane.c2p(*added(u, scaled(v, 0.5))), UP, buff=0.12),
            run_time=1.4,
            rate_func=spring,
        )
        sum_arrow = vector_arrow(total, Palette.teal, plane)
        sum_tag = name_tag(r"\mathbf u + \mathbf v", Palette.teal, plane.c2p(*total), sum_side, buff=0.3)
        self.play(u_arrow.animate.set_opacity(0.35), v_arrow.animate.set_opacity(0.35), run_time=0.4)
        self.play(GrowArrow(sum_arrow), FadeIn(sum_tag), run_time=1.1, rate_func=spring_soft)
        return u_arrow, v_arrow, sum_arrow, VGroup(u_tag, v_tag, sum_tag)

    def scale_along(self, base, targets, color, tex):
        """A slider c and a live arrow c * base that springs through each target value."""
        c = ValueTracker(1.0)
        arrow = always_redraw(lambda: self.live_multiple(base, c.get_value(), color))
        tag = always_redraw(lambda: self.live_tag(base, c.get_value(), color, tex))
        control = backed(slider("c", c, color, x_range=(-1, 3, 1), length=2.4), padding=0.2)
        control.next_to(self.checks, DOWN, buff=0.3, aligned_edge=LEFT)
        self.slider_tracker = c
        self.add(arrow, tag)
        self.play(FadeIn(control), run_time=0.6)
        for value in targets:
            self.play(c.animate.set_value(value), run_time=1.6, rate_func=spring)
            self.wait(0.6)
        self.wait(Timing.beat)
        return VGroup(control, arrow, tag)

    def live_multiple(self, base, c_value, color):
        if abs(c_value) < 0.04:
            return Dot(self.plane.c2p(0, 0), radius=0.1, color=color)
        return vector_arrow(scaled(base, c_value), color, self.plane)

    def live_tag(self, base, c_value, color, tex):
        tip = self.plane.c2p(*scaled(base, c_value))
        return name_tag(tex, color, tip, DR if c_value >= 0 else UL)

    def shift_the_line(self, line):
        plane = self.plane
        line = self.say(r"Now slide the same line up by one unit.", line, hold=0.2)
        shifted_name = set_name(plane, 1)
        self.play(
            Transform(self.h_line, set_line(plane, 1)),
            FadeTransform(self.h_name, shifted_name),
            run_time=1.6,
            rate_func=spring_soft,
        )
        self.h_name = shifted_name
        self.wait(Timing.beat)

        line = self.say(r"The shifted line misses the origin, so (a) fails.", line, hold=0.2)
        ring = ring_at(plane.c2p(0, 0))
        gap = gap_segment(plane, (0, 0), (0, 1))
        self.play(Create(ring), run_time=0.7)
        self.play(Create(gap), run_time=0.6)
        self.marks = VGroup(self.check_row(0, False))
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(ring, gap)), run_time=0.4)
        return line

    def shifted_sum(self, line):
        plane = self.plane
        total = added(U_OFF, V_OFF)
        line = self.say(r"Their sum jumps one unit above the line.", line, hold=0.2)
        u_arrow, v_arrow, sum_arrow, tags = self.add_on_line(U_OFF, V_OFF, TAGS_OFF)
        on_line = (total[0], SLOPE * total[0] + 1)
        ring = ring_at(plane.c2p(*total))
        gap = gap_segment(plane, on_line, total)
        self.play(Create(ring), Create(gap), run_time=0.8)
        self.marks.add(self.check_row(1, False))
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(u_arrow, v_arrow, sum_arrow, tags, ring, gap)), run_time=0.6)
        return line

    def shifted_scaling(self, line):
        plane = self.plane
        ray = DashedLine(plane.c2p(-1.4, -1.4), plane.c2p(4.4, 4.4), color=Palette.text_muted, stroke_width=2, dash_length=0.1)
        line = self.say(r"Scaling $\mathbf u$ slides its tip off the line too.", line, hold=0.2)
        self.play(Create(ray), run_time=0.8)
        control = self.scale_along(U_OFF, (2.0,), Palette.yellow, r"c\,\mathbf u")
        line = self.say(r"At $c = 0$ it reaches the origin, which the line missed.", line, hold=0.2)
        c_tracker = self.slider_tracker
        self.play(c_tracker.animate.set_value(0.0), run_time=1.6, rate_func=spring)
        ring = ring_at(plane.c2p(0, 0))
        self.play(Create(ring), run_time=0.6)
        self.marks.add(self.check_row(2, False))
        line = self.say(r"A line that misses the origin is not a subspace.", line, hold=Timing.read_long)
        self.play(FadeOut(VGroup(control, ray, ring, self.marks, self.checks, self.h_line, self.h_name, plane)), run_time=0.8)
        return line

    def plane_in_space(self, line):
        axes = space_axes()
        patch = plane_patch()
        v1_arrow = projected_arrow(project, V1, Palette.yellow)
        v2_arrow = projected_arrow(project, V2, Palette.blue)
        v1_tag = name_tag(r"\mathbf v_1", Palette.yellow, project(V1), UR)
        v2_tag = name_tag(r"\mathbf v_2", Palette.blue, project(V2), DOWN)
        line = self.say(r"In 3D, planes through the origin are subspaces as well.", line, hold=0.2)
        self.play(Create(axes), run_time=1.4)
        self.play(FadeIn(patch), run_time=1.0)
        self.play(GrowArrow(v1_arrow), GrowArrow(v2_arrow), FadeIn(v1_tag), FadeIn(v2_tag), run_time=1.2, rate_func=spring_soft)
        self.wait(Timing.beat)

        line = self.say(r"Every combination of $\mathbf v_1$ and $\mathbf v_2$ stays on the plane.", line, hold=0.2)
        roam = self.roam_combinations()
        self.play(FadeOut(roam), run_time=0.5)

        line = self.say(r"Lift the plane off the origin and it fails the test.", line, hold=0.2)
        origin = Dot(project((0, 0, 0)), radius=0.08, color=Palette.text)
        self.add(origin)
        self.play(FadeOut(VGroup(v1_arrow, v2_arrow, v1_tag, v2_tag)), run_time=0.5)
        ghost = DashedVMobject(plane_patch().set_fill(opacity=0).set_stroke(Palette.text_muted, width=2), num_dashes=48)
        self.add(ghost)
        self.play(Transform(patch, plane_patch(LIFT)), run_time=1.8, rate_func=spring_soft)
        ring = ring_at(project((0, 0, 0)))
        gap = DashedLine(project((0, 0, 0)), project(LIFT), color=Palette.glow, stroke_width=4, dash_length=0.08)
        above = Dot(project(LIFT), radius=0.08, color=Palette.purple_gray)
        self.play(Create(ring), run_time=0.7)
        self.play(Create(gap), GrowFromCenter(above), run_time=0.8)
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(axes, patch, origin, ring, ghost, gap, above)), run_time=0.7)
        return line

    def roam_combinations(self):
        s = ValueTracker(1.0)
        t = ValueTracker(1.0)
        arrow = always_redraw(lambda: projected_arrow(project, combination(s.get_value(), t.get_value()), Palette.teal))
        readout = always_redraw(lambda: self.weights_readout(s.get_value(), t.get_value()))
        first = projected_arrow(project, combination(1.0, 1.0), Palette.teal)
        self.play(GrowArrow(first), FadeIn(readout), run_time=0.9, rate_func=spring_soft)
        self.remove(first)
        self.add(arrow)
        for s_value, t_value in ((1.0, -0.6), (-1.0, 0.8), (1.1, 0.5)):
            self.play(s.animate.set_value(s_value), t.animate.set_value(t_value), run_time=1.6, rate_func=spring)
            self.wait(0.5)
        return VGroup(arrow, readout)

    @staticmethod
    def weights_readout(s_value, t_value):
        text = MathTex(rf"({s_value:.1f})", r"\mathbf v_1", "+", rf"({t_value:.1f})", r"\mathbf v_2", font_size=40)
        text.set_color(Palette.teal)
        text[1].set_color(Palette.yellow)
        text[4].set_color(Palette.blue)
        return backed(text, padding=0.14).to_corner(UR, buff=0.45)

    def any_span(self, line):
        rows = VGroup(
            span_row("a", r"\mathbf 0", r"0\,\mathbf v_1 + 0\,\mathbf v_2"),
            span_row("b", r"(s_1\mathbf v_1 + s_2\mathbf v_2) + (t_1\mathbf v_1 + t_2\mathbf v_2)", r"(s_1 + t_1)\mathbf v_1 + (s_2 + t_2)\mathbf v_2"),
            span_row("c", r"c\,(s_1\mathbf v_1 + s_2\mathbf v_2)", r"(c s_1)\mathbf v_1 + (c s_2)\mathbf v_2"),
        ).arrange(DOWN, buff=0.7, aligned_edge=LEFT)
        rows.width = min(rows.width, config.frame_width - 2.6)
        rows.move_to(DOWN * 0.1)
        header = MathTex(r"H = \operatorname{Span}\{\mathbf v_1, \mathbf v_2\}", color=Palette.purple_gray, font_size=44)
        header.next_to(rows, UP, buff=0.7)
        line = self.say(r"The span of any vectors passes all three checks.", line, hold=0.2)
        self.play(FadeIn(header, shift=DOWN * 0.15), run_time=0.8, rate_func=spring_soft)
        captions = (
            r"Zero weights give the zero vector.",
            r"Adding two combinations adds their weights.",
            r"Scaling a combination scales its weights.",
        )
        for row, text in zip(rows, captions):
            line = self.say(text, line, hold=0.2)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.9, rate_func=spring_soft)
            mark = tick_mark().next_to(row, RIGHT, buff=0.4)
            self.sfx("pop", gain=-6)
            self.play(Create(mark), run_time=0.5)
            row.add(mark)
            self.wait(Timing.read_short)
        line = self.say(r"Tomorrow we use spans to build subspaces on purpose.", line, hold=Timing.read_short)
        return line


def panel_plane(center, x_range):
    width = x_range[1] - x_range[0]
    plane = make_plane(x_range=(*x_range, 1), y_range=(-2, 5, 1), x_length=width * 0.62, y_length=7 * 0.62)
    return plane.shift(np.array([*center, 0]) - plane.get_center())


def panel_tags(plane, u, v, sides):
    total = added(u, v)
    points = (u, added(u, scaled(v, 0.5)), total)
    texts = (r"\mathbf u", r"\mathbf v", r"\mathbf u + \mathbf v")
    colors = (Palette.yellow, Palette.blue, Palette.teal)
    return VGroup(
        *[
            backed(MathTex(tex, color=color, font_size=30), padding=0.06).next_to(plane.c2p(*point), side, buff=0.1)
            for tex, color, point, side in zip(texts, colors, points, sides)
        ]
    )


def panel(center, shift, u, v, x_range, sides):
    """One side of the comparison: a line, two vectors on it placed tip to tail, and where their sum lands."""
    plane = panel_plane(center, x_range)
    total = added(u, v)
    pieces = VGroup(
        plane,
        equation_line(plane, line_coeffs(shift), color=Palette.purple_gray, stroke_width=5),
        vector_arrow(u, Palette.yellow, plane, stroke_width=5),
        arrow_between(plane, u, total, Palette.blue, stroke_width=5),
    )
    name = backed(MathTex(line_rule(shift), color=Palette.purple_gray, font_size=34), padding=0.1)
    pieces.add(name.next_to(plane, UP, buff=0.2))
    if shift != 0:
        on_line = (total[0], SLOPE * total[0] + shift)
        pieces.add(vector_arrow(total, Palette.teal, plane, stroke_width=5))
        pieces.add(gap_segment(plane, on_line, total), ring_at(plane.c2p(*total), radius=0.16))
        pieces.add(gap_segment(plane, (0, 0), (0, shift)))
    pieces.add(Dot(plane.c2p(*total), radius=0.08, color=Palette.teal), panel_tags(plane, u, v, sides))
    return pieces


def comparison(scene):
    scene.add(
        panel((-3.6, 0), 0, U_ON, V_ON, (-2, 7), (DR, UP, UL)),
        panel((3.6, 0), 1, U_OFF, V_OFF, (-5, 4), (DR, UP, UL)),
    )


class FigShiftedLine(Scene):
    def construct(self):
        comparison(self)
        fit_to_frame(self)


class FigPlaneThroughOrigin(Scene):
    def construct(self):
        total = combination(1, 1)
        self.add(
            space_axes(),
            plane_patch(),
            Dot(project((0, 0, 0)), radius=0.07, color=Palette.text),
            projected_arrow(project, V1, Palette.yellow),
            projected_arrow(project, V2, Palette.blue),
            projected_arrow(project, total, Palette.teal),
            name_tag(r"\mathbf v_1", Palette.yellow, project(V1), UR),
            name_tag(r"\mathbf v_2", Palette.blue, project(V2), DOWN),
            name_tag(r"\mathbf v_1 + \mathbf v_2", Palette.teal, project(total), RIGHT),
        )
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        comparison(self)
        fit_to_frame(self, margin=0.6)
