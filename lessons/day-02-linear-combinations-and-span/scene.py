import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene3D,
    Palette,
    Timing,
    backed,
    clip_to_box,
    column,
    fit_to_frame,
    make_plane,
    matrix,
    skewed_grid,
    span_sheet,
    spring,
    spring_soft,
    vector_arrow,
    vector_arrow_3d,
)

V = (3, 2)
W = (-1, 2)
B_FLAT = (5, -2)
B_WEIGHTS = (1, -2)

U3 = np.array([2, -1, 1])
V3 = np.array([1, 2, 1])
B3_WEIGHTS = (1, 2)
B3 = B3_WEIGHTS[0] * U3 + B3_WEIGHTS[1] * V3
B3_OFF_ENTRY = -1
SHEET_S = (-1.5, 2.0)
SHEET_T = (-1.5, 2.5)


def swung_w(progress):
    """W turned and stretched toward -V along an arc."""
    start_angle, end_angle = np.arctan2(W[1], W[0]), np.arctan2(-V[1], -V[0]) + TAU
    start_length, end_length = np.hypot(*W), np.hypot(*V)
    angle = interpolate(start_angle, end_angle, progress)
    length = interpolate(start_length, end_length, progress)
    return (length * np.cos(angle), length * np.sin(angle))


def name_tag(tex, color, point, direction, font_size=44):
    return backed(MathTex(tex, color=color, font_size=font_size)).next_to(point, direction, buff=0.12)


def equals_aligned(rows):
    """Stack MathTex rows of the form (left, '=', right) so their equals signs line up."""
    group = VGroup(*rows).arrange(DOWN, buff=0.28)
    for row in rows:
        row.shift(RIGHT * (rows[0][1].get_center()[0] - row[1].get_center()[0]))
    return group


def span_line_2d(plane, direction):
    ends = clip_to_box(np.multiply(-20, direction), np.multiply(20, direction), plane.x_range[:2], plane.y_range[:2])
    return Line(plane.c2p(*ends[0]), plane.c2p(*ends[1]), color=Palette.teal, stroke_width=5)


def make_axes_3d():
    return ThreeDAxes(
        x_range=(-6, 6, 1),
        y_range=(-6, 6, 1),
        z_range=(-4, 5, 1),
        x_length=6,
        y_length=6,
        z_length=4.5,
        axis_config={"stroke_color": Palette.axis, "stroke_width": 2, "include_tip": False, "tick_size": 0.04},
    )


def sheet_at(axes, extent):
    s_range = (SHEET_S[0] * extent, SHEET_S[1] * extent)
    t_range = (SHEET_T[0] * extent, SHEET_T[1] * extent)
    return span_sheet(axes, U3, V3, s_range, t_range, resolution=(7, 8))


def u_line(axes, reach=2.4):
    return Line(axes.c2p(*(-reach * U3)), axes.c2p(*(reach * U3)), color=Palette.teal, stroke_width=4)


class Lesson(LessonScene3D):
    day = 2
    title = "Linear combinations and span"

    def construct(self):
        plane = make_plane().set_z_index(-2)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        w_turn = ValueTracker(0.0)
        line = self.span_is_everything(plane, w_turn)
        line = self.parallel_collapse(plane, w_turn, line)
        line = self.membership(plane, line)
        self.play(*[FadeOut(m) for m in self.mobjects if isinstance(m, VMobject) and m is not line], run_time=0.8)
        axes, line = self.enter_space(line)
        pieces, line = self.plane_in_space(axes, line)
        line = self.flat_or_off(axes, pieces, line)
        self.stop_ambient_camera_rotation()
        self.play(*[FadeOut(m) for m in self.mobjects if isinstance(m, VMobject)], run_time=0.8)
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1)
        self.close_episode(
            r"The span of some vectors is every place\\"
            r"you can reach by scaling and adding them.",
        )

    def span_is_everything(self, plane, w_turn):
        v_arrow = vector_arrow(V, Palette.yellow, plane)
        w_arrow = always_redraw(lambda: vector_arrow(swung_w(w_turn.get_value()), Palette.blue, plane))
        v_tag = name_tag(r"\vec v", Palette.yellow, plane.c2p(*V), RIGHT)
        w_tag = always_redraw(lambda: name_tag(r"\vec w", Palette.blue, plane.c2p(*swung_w(w_turn.get_value())), UL))
        line = self.say(r"Yesterday we scaled and added $\vec v$ and $\vec w$.", hold=0.2)
        self.play(GrowArrow(v_arrow), FadeIn(v_tag), run_time=1.2, rate_func=spring_soft)
        grow_w = w_arrow.copy()
        self.play(GrowArrow(grow_w), FadeIn(w_tag), run_time=1.2, rate_func=spring_soft)
        self.remove(grow_w)
        self.add(w_arrow)
        self.wait(Timing.beat)

        grid = always_redraw(lambda: skewed_grid(plane, V, swung_w(w_turn.get_value())))
        line = self.say(r"Every choice of weights $a$ and $b$ lands somewhere.", line, hold=0.2)
        drawn = skewed_grid(plane, V, W)
        self.play(Create(drawn, lag_ratio=0.01), run_time=2.6)
        self.remove(drawn)
        self.add(grid)
        self.bring_to_front(v_arrow, w_arrow, v_tag, w_tag)
        self.wait(Timing.read_short)

        definition = backed(
            MathTex(r"\operatorname{Span}\{\vec v,\vec w\}", r"=", r"\{\,a\vec v + b\vec w\,\}", font_size=44),
            padding=0.22,
        ).to_corner(UL, buff=0.45).set_z_index(5)
        line = self.say(r"The set of all those places is called the \emph{span}.", line, hold=0.2)
        self.play(Write(definition), run_time=1.6)
        self.wait(Timing.read_long)

        line = self.say(r"Weights of zero land on the origin, so the span contains it.", line, hold=0.2)
        self.play(Flash(plane.c2p(0, 0), color=Palette.glow, line_length=0.3, flash_radius=0.35), run_time=1.0)
        self.wait(Timing.read_short)
        return line

    def parallel_collapse(self, plane, w_turn, line):
        line = self.say(r"Two arrows in different directions fill the whole plane.", line, hold=Timing.read_short)
        line = self.say(r"Now turn $\vec w$ until it lines up with $\vec v$.", line, hold=0.2)
        self.play(w_turn.animate.set_value(1.0), run_time=3.2, rate_func=smooth)
        self.wait(Timing.beat)

        formula = backed(MathTex(r"a\vec v + b(-\vec v) = (a-b)\,\vec v", font_size=44), padding=0.22).to_corner(UR, buff=0.45).set_z_index(5)
        span_line = span_line_2d(plane, V).set_z_index(-1)
        line = self.say(r"Now $\vec w = -\vec v$, so every combination is a multiple of $\vec v$.", line, hold=0.2)
        self.play(FadeIn(formula, shift=DOWN * 0.15), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"Parallel vectors only span a line through the origin.", line, hold=0.2)
        self.play(Create(span_line), run_time=1.2)
        self.wait(Timing.read_short)

        line = self.say(r"Turn $\vec w$ back and the whole plane returns.", line, hold=0.2)
        self.play(FadeOut(span_line), FadeOut(formula), run_time=0.5)
        self.play(w_turn.animate.set_value(0.0), run_time=1.8, rate_func=spring)
        self.wait(Timing.beat)
        return line

    def membership(self, plane, line):
        b_arrow = vector_arrow(B_FLAT, Palette.pink, plane)
        b_tag = name_tag(r"\vec b", Palette.pink, plane.c2p(*B_FLAT), RIGHT)
        line = self.say(r"Is $\vec b$ in the span? Look for weights that reach it.", line, hold=0.2)
        self.play(GrowArrow(b_arrow), FadeIn(b_tag), run_time=1.2, rate_func=spring_soft)
        self.wait(Timing.beat)

        equation = self.vector_equation()
        line = self.say(r"We need numbers $x_1$ and $x_2$ that solve this equation.", line, hold=0.2)
        self.play(FadeOut(self.find_definition()), run_time=0.4)
        self.play(FadeIn(equation), run_time=1.0)
        self.wait(Timing.read_short)

        system = self.system_from(equation)
        line = self.say(r"Matching entries gives one equation for each row.", line, hold=0.2)
        self.wait(Timing.read_short)

        augmented = self.augmented_from(equation, system)
        line = self.say(r"The vectors become the columns of an \emph{augmented matrix}.", line, hold=Timing.read_long)

        solution = backed(MathTex(r"x_1 = 1,\quad x_2 = -2", color=Palette.text, font_size=44), padding=0.2)
        solution.next_to(augmented, DOWN, buff=0.35, aligned_edge=LEFT)
        line = self.say(r"Solving the two equations gives $x_1 = 1$ and $x_2 = -2$.", line, hold=0.2)
        self.play(FadeIn(solution, shift=UP * 0.15), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)

        line = self.say(r"Walk $\vec v$, then $-2\vec w$, and you land on $\vec b$.", line, hold=0.2)
        self.walk_to_b(plane)
        self.wait(Timing.read_short)
        return line

    def find_definition(self):
        return next(m for m in self.mobjects if isinstance(m, MathTex) and r"\operatorname{Span}" in m.get_tex_string())

    def vector_equation(self):
        parts = VGroup(
            MathTex("x_1", font_size=40),
            column(V, color=Palette.yellow),
            MathTex(r"+\;x_2", font_size=40),
            column(W, color=Palette.blue),
            MathTex("=", font_size=40),
            column(B_FLAT, color=Palette.pink),
        ).arrange(RIGHT, buff=0.18)
        parts.scale(0.82)
        columns = [parts[1], parts[3], parts[5]]
        equation = backed(parts, padding=0.22).to_corner(UL, buff=0.45)
        equation.columns = columns
        return equation

    def system_from(self, equation):
        rows = [
            MathTex(r"3x_1 - x_2", "=", "5", font_size=40),
            MathTex(r"2x_1 + 2x_2", "=", "-2", font_size=40),
        ]
        system = backed(equals_aligned(rows), padding=0.2).next_to(equation, DOWN, buff=0.3, aligned_edge=LEFT)
        columns = equation.columns
        for index, row in enumerate(rows):
            entries = VGroup(*[col.get_entries()[index] for col in columns])
            self.play(Indicate(entries, color=Palette.glow, scale_factor=1.15), run_time=0.8)
            self.play(FadeIn(system.background_rectangle) if index == 0 else Wait(0.01), FadeIn(row, shift=DOWN * 0.15), run_time=0.7, rate_func=spring)
        return system

    def augmented_from(self, equation, system):
        augmented = matrix([["3", "-1", "5"], ["2", "2", "-2"]])
        colors = (Palette.yellow, Palette.blue, Palette.pink)
        for index, color in enumerate(colors):
            augmented.get_columns()[index].set_color(color)
        divider = DashedLine(UP * 0.55, DOWN * 0.55, color=Palette.text_muted, stroke_width=2)
        augmented.scale(0.82)
        backed(augmented, padding=0.2).next_to(system, DOWN, buff=0.3, aligned_edge=LEFT)
        divider.scale(0.82).move_to(
            (augmented.get_columns()[1].get_right() + augmented.get_columns()[2].get_left()) / 2
        )
        self.play(FadeIn(augmented.background_rectangle), FadeIn(augmented.get_brackets()), run_time=0.5)
        for index, source in enumerate(equation.columns):
            self.play(Indicate(source, color=Palette.glow, scale_factor=1.1), run_time=0.6)
            self.play(TransformFromCopy(source.get_entries(), augmented.get_columns()[index]), run_time=0.9)
        self.play(Create(divider), run_time=0.4)
        augmented.add(divider)
        return augmented

    def walk_to_b(self, plane):
        first = vector_arrow(V, Palette.yellow, plane, stroke_width=8)
        step = vector_arrow(np.multiply(B_WEIGHTS[1], W), Palette.blue, plane, stroke_width=8)
        step.shift(plane.c2p(*V) - plane.c2p(0, 0))
        self.play(GrowArrow(first), run_time=1.0, rate_func=spring_soft)
        self.play(GrowArrow(step), run_time=1.2, rate_func=spring_soft)
        stamp = Dot(plane.c2p(*B_FLAT), radius=0.11, color=Palette.glow)
        self.play(GrowFromCenter(stamp), run_time=0.5, rate_func=spring)

    def enter_space(self, line):
        axes = make_axes_3d()
        line = self.say(r"In space, two vectors can't reach everywhere.", line, hold=0.2)
        self.move_camera(phi=66 * DEGREES, theta=-115 * DEGREES, zoom=1.3, added_anims=[Create(axes)], run_time=2.4)
        self.begin_ambient_camera_rotation(rate=0.035)
        self.wait(Timing.beat)
        return axes, line

    def plane_in_space(self, axes, line):
        u_arrow = vector_arrow_3d(axes, U3, Palette.yellow)
        v_arrow = vector_arrow_3d(axes, V3, Palette.blue)
        line = self.say(r"One vector $\vec u$ spans a line through the origin.", line, hold=0.2)
        self.sfx("whoosh", gain=-2)
        self.play(GrowFromPoint(u_arrow, axes.c2p(0, 0, 0)), run_time=1.2, rate_func=spring_soft)
        u_tag = self.tag_3d(axes, r"\vec u", Palette.yellow, U3)
        self.play(Create(u_line(axes)), FadeIn(u_tag), run_time=1.6)
        self.wait(Timing.read_short)

        extent = ValueTracker(0.02)
        sheet = always_redraw(lambda: sheet_at(axes, extent.get_value()))
        line = self.say(r"A second direction $\vec v$ sweeps out a whole plane.", line, hold=0.2)
        self.sfx("whoosh", gain=-2)
        v_tag = self.tag_3d(axes, r"\vec v", Palette.blue, V3)
        self.play(GrowFromPoint(v_arrow, axes.c2p(0, 0, 0)), FadeIn(v_tag), run_time=1.2, rate_func=spring_soft)
        self.add(sheet)
        self.sfx("sweep", gain=-3)
        self.play(extent.animate.set_value(1.0), run_time=3.6, rate_func=smooth)
        self.wait(Timing.read_short)
        return VGroup(u_arrow, v_arrow), line

    def tag_3d(self, axes, tex, color, point):
        tag = backed(MathTex(tex, color=color, font_size=40), padding=0.07).move_to(axes.c2p(*(point * 1.18)) + OUT * 0.25)
        self.add_fixed_orientation_mobjects(tag)
        self.remove(tag)
        return tag

    def flat_or_off(self, axes, pieces, line):
        last_entry = ValueTracker(B3[2])
        b_arrow = always_redraw(lambda: vector_arrow_3d(axes, (B3[0], B3[1], last_entry.get_value()), Palette.pink))
        line = self.say(r"Here is $\vec b = (4, 3, 3)$. Does it lie in the plane?", line, hold=0.2)
        self.play(GrowFromPoint(vector_arrow_3d(axes, B3, Palette.pink), axes.c2p(0, 0, 0)), run_time=1.2, rate_func=spring_soft)
        self.add(b_arrow)
        self.wait(Timing.beat)

        line = self.say(r"Walk $\vec u$, then $2\vec v$, and you land exactly on $\vec b$.", line, hold=0.2)
        stamp = self.walk_in_space(axes, pieces)
        self.wait(Timing.read_short)

        gap = always_redraw(lambda: DashedLine(axes.c2p(*B3), axes.c2p(B3[0], B3[1], last_entry.get_value()), color=Palette.glow, stroke_width=4))
        line = self.say(r"Change its last entry to $-1$ and it leaves the plane.", line, hold=0.2)
        self.add(gap)
        self.play(last_entry.animate.set_value(B3_OFF_ENTRY), run_time=2.0, rate_func=spring_soft)
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=80 * DEGREES, theta=-38 * DEGREES, run_time=2.4, rate_func=smooth)
        self.wait(Timing.beat)

        line = self.show_contradiction(line)
        line = self.say(r"Only a last entry of $3$ puts $\vec b$ back on the plane.", line, hold=0.2)
        self.play(last_entry.animate.set_value(B3[2]), run_time=1.8, rate_func=spring)
        self.play(Indicate(stamp, color=Palette.glow, scale_factor=1.8), run_time=0.8)
        self.wait(Timing.read_short)
        return line

    def walk_in_space(self, axes, pieces):
        u_tip = B3_WEIGHTS[0] * U3
        step = vector_arrow_3d(axes, B3, Palette.blue, start=u_tip)
        self.play(Indicate(pieces[0], color=Palette.glow, scale_factor=1.05), run_time=0.8)
        self.sfx("whoosh", gain=-2)
        self.play(GrowFromPoint(step, axes.c2p(*u_tip)), run_time=1.4, rate_func=spring_soft)
        stamp = Dot3D(axes.c2p(*B3), radius=0.09, color=Palette.glow)
        self.play(GrowFromCenter(stamp), run_time=0.5, rate_func=spring)
        self.wait(Timing.beat)
        self.play(FadeOut(step), run_time=0.5)
        return stamp

    def show_contradiction(self, line):
        header = MathTex(r"x_1\vec u + x_2\vec v = \vec b", font_size=40)
        header[0][0:4].set_color(Palette.yellow)
        header[0][5:9].set_color(Palette.blue)
        header[0][10:].set_color(Palette.pink)
        rows = [
            MathTex(r"2x_1 + x_2", "=", "4", font_size=40),
            MathTex(r"-x_1 + 2x_2", "=", "3", font_size=40),
            MathTex(r"x_1 + x_2", "=", "-1", font_size=40),
        ]
        panel = backed(VGroup(header, equals_aligned(rows)).arrange(DOWN, buff=0.35, aligned_edge=LEFT), padding=0.25)
        panel.to_corner(UL, buff=0.45)
        self.pin(panel)
        self.play(FadeIn(panel), run_time=0.8)

        forced = MathTex(r"\Rightarrow\; x_1 = 1,\ x_2 = 2", font_size=40).next_to(VGroup(rows[0], rows[1]), RIGHT, buff=0.35)
        clash = MathTex(r"\Rightarrow\; 3 = -1", color=Palette.glow, font_size=40).next_to(rows[2], RIGHT, buff=0.35)
        self.pin(backed(forced), backed(clash))
        self.remove(forced, clash)
        line = self.say(r"The first two rows force $x_1 = 1$ and $x_2 = 2$.", line, hold=0.2)
        self.play(Indicate(VGroup(rows[0], rows[1]), color=Palette.glow, scale_factor=1.08), run_time=0.9)
        self.play(FadeIn(forced, shift=LEFT * 0.15), run_time=0.7, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"Then the third row says $3 = -1$, which is impossible.", line, hold=0.2)
        self.play(Indicate(rows[2], color=Palette.glow, scale_factor=1.12), run_time=0.9)
        self.play(FadeIn(clash, shift=LEFT * 0.15), run_time=0.7, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"No weights reach it, so this $\vec b$ is not in the span.", line, hold=Timing.read_short)
        self.play(FadeOut(VGroup(panel, forced, clash)), run_time=0.6)
        return line


class FigTwoSpans(Scene):
    def construct(self):
        panels = VGroup(self.panel(W, r"\vec w"), self.panel((-1.5, -1), r"\vec w = -\tfrac12\vec v")).arrange(RIGHT, buff=0.6)
        self.add(panels)
        fit_to_frame(self)

    @staticmethod
    def panel(w, w_tex):
        plane = make_plane(x_range=(-5, 5, 1), y_range=(-4, 4, 1))
        pieces = VGroup(plane, skewed_grid(plane, V, w, reach=8, opacity=0.75))
        if V[0] * w[1] - V[1] * w[0] == 0:
            pieces.add(span_line_2d(plane, V))
        pieces.add(vector_arrow(V, Palette.yellow, plane), vector_arrow(w, Palette.blue, plane))
        pieces.add(name_tag(r"\vec v", Palette.yellow, plane.c2p(*V), RIGHT, font_size=56))
        pieces.add(name_tag(w_tex, Palette.blue, plane.c2p(*w), DOWN if w[1] < 0 else UL, font_size=56))
        return pieces


class FigReachB(Scene):
    def construct(self):
        plane = make_plane(x_range=(-2, 7, 1), y_range=(-3, 4, 1))
        step = vector_arrow(np.multiply(B_WEIGHTS[1], W), Palette.blue, plane)
        step.shift(plane.c2p(*V) - plane.c2p(0, 0))
        tags = VGroup(
            name_tag(r"\vec v", Palette.yellow, plane.c2p(1.5, 1), UL),
            name_tag(r"-2\vec w", Palette.blue, plane.c2p(4.3, 0.6), RIGHT),
            name_tag(r"\vec b = \vec v - 2\vec w", Palette.pink, plane.c2p(*B_FLAT), DOWN),
            name_tag(r"\vec w", Palette.blue, plane.c2p(*W), LEFT),
        )
        self.add(plane, vector_arrow(W, Palette.blue, plane), vector_arrow(V, Palette.yellow, plane), step)
        self.add(vector_arrow(B_FLAT, Palette.pink, plane), Dot(plane.c2p(*B_FLAT), radius=0.1, color=Palette.glow), tags)
        fit_to_frame(self)


class FigPlaneInSpace(ThreeDScene):
    def construct(self):
        axes = make_axes_3d()
        self.set_camera_orientation(phi=72 * DEGREES, theta=-78 * DEGREES, zoom=1.55)
        off = (B3[0], B3[1], B3_OFF_ENTRY)
        self.add(axes, sheet_at(axes, 1.0), u_line(axes))
        self.add(vector_arrow_3d(axes, U3, Palette.yellow), vector_arrow_3d(axes, V3, Palette.blue))
        self.add(vector_arrow_3d(axes, B3, Palette.pink), Dot3D(axes.c2p(*B3), radius=0.09, color=Palette.glow))
        self.add(vector_arrow_3d(axes, off, Palette.pink), DashedLine(axes.c2p(*B3), axes.c2p(*off), color=Palette.glow, stroke_width=4))
        labels = [
            (r"\vec u", Palette.yellow, U3 * 1.25, OUT),
            (r"\vec v", Palette.blue, V3 * 1.25, OUT),
            (r"(4, 3, 3)", Palette.pink, B3, OUT),
            (r"(4, 3, -1)", Palette.pink, off, IN),
        ]
        for tex, color, point, direction in labels:
            tag = backed(MathTex(tex, color=color, font_size=34), padding=0.06).move_to(axes.c2p(*point) + direction * 0.3)
            self.add_fixed_orientation_mobjects(tag)


class Poster(ThreeDScene):
    def construct(self):
        axes = make_axes_3d()
        self.set_camera_orientation(phi=68 * DEGREES, theta=-70 * DEGREES, zoom=1.6)
        self.add(axes, sheet_at(axes, 1.0), u_line(axes))
        self.add(vector_arrow_3d(axes, U3, Palette.yellow), vector_arrow_3d(axes, V3, Palette.blue))
        self.add(vector_arrow_3d(axes, B3, Palette.blue, start=U3), vector_arrow_3d(axes, B3, Palette.pink))
        self.add(Dot3D(axes.c2p(*B3), radius=0.1, color=Palette.glow))
