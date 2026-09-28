import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    OrbitingView,
    Palette,
    Timing,
    arrow_between,
    backed,
    fit_to_frame,
    floor_and_axes,
    line_through_origin,
    plane_at,
    plate_for,
    projected_arrow,
    projected_patch,
    corner_mark,
    spring,
    spring_soft,
    vector_arrow,
)

U_LINE = np.array([1.0, 1.0])
Y_FLAT = np.array([1.0, 5.0])
YHAT_FLAT = np.array([3.0, 3.0])
FLAT_ORIGIN = (-4.6, -2.6)
FLAT_UNIT = 1.1

U1 = np.array([1.0, 1.0, 0.0])
U2 = np.array([-1.0, 1.0, 1.0])
Y = np.array([2.0, 2.0, 3.0])
YHAT = np.array([1.0, 3.0, 1.0])
Z = Y - YHAT
SPACE_ORIGIN = (-4.4, 1.0)
SPACE_UNIT = 1.2
AZIMUTH = 30.0
SWUNG = 46.0
ELEVATION = 25.0
PATCH_S = (-0.8, 2.7)
PATCH_T = (-1.0, 1.8)
SPACE_REACH = ((-1, 3), (-1, 4), (-1, 3))

PANEL_LEFT = 0.7
PANEL_TOP = 3.7
FLAT_PANEL_LEFT = 1.9
WANDER = [(-0.6, -0.8), (2.4, -0.8), (0.5, 1.5)]


def bmatrix(*entries):
    return r"\begin{bmatrix}" + r"\\".join(str(entry) for entry in entries) + r"\end{bmatrix}"


def tex_parts(*parts, colors=(), font_size=38):
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def flat_point(plane, coords):
    return plane.c2p(*coords)


def line_formula():
    return tex_parts(
        r"\hat{\mathbf y}", "=", r"{\mathbf y\cdot\mathbf u \over \mathbf u\cdot\mathbf u}", r"\,\mathbf u",
        colors=(Palette.teal, None, None, Palette.i_hat), font_size=44,
    )


def line_numbers():
    return tex_parts(
        "=", r"{6 \over 2}", r"\,\mathbf u", "=", bmatrix(3, 3),
        colors=(None, None, Palette.i_hat, None, Palette.teal), font_size=44,
    )


def line_check():
    return tex_parts(r"\mathbf z", r"\cdot", r"\mathbf u", "=", r"-2 + 2 = 0", colors=(Palette.pink, None, Palette.i_hat), font_size=44)


def day17_projection():
    return tex_parts(r"P\mathbf y", "=", r"\tfrac12\begin{bmatrix} 1 & 1 \\ 1 & 1 \end{bmatrix}", bmatrix(1, 5), "=", bmatrix(3, 3),
                     colors=(None, None, None, Palette.yellow, None, Palette.teal), font_size=40)


def plane_givens():
    return tex_parts(
        r"\mathbf u_1", "=", bmatrix(1, 1, 0), r",\ \ ", r"\mathbf u_2", "=", bmatrix(-1, 1, 1), r",\ \ ", r"\mathbf y", "=", bmatrix(2, 2, 3),
        colors=(Palette.i_hat, None, Palette.i_hat, None, Palette.j_hat, None, Palette.j_hat, None, Palette.yellow, None, Palette.yellow),
        font_size=30,
    )


def plane_formula():
    return tex_parts(
        r"\hat{\mathbf y}", "=", r"{\mathbf y\cdot\mathbf u_1 \over \mathbf u_1\cdot\mathbf u_1}", r"\,\mathbf u_1", "+",
        r"{\mathbf y\cdot\mathbf u_2 \over \mathbf u_2\cdot\mathbf u_2}", r"\,\mathbf u_2",
        colors=(Palette.teal, None, None, Palette.i_hat, None, None, Palette.j_hat), font_size=34,
    )


def plane_numbers():
    return tex_parts(
        "=", r"{4 \over 2}", r"\,\mathbf u_1", "+", r"{3 \over 3}", r"\,\mathbf u_2", "=", bmatrix(1, 3, 1),
        colors=(None, None, Palette.i_hat, None, None, Palette.j_hat, None, Palette.teal), font_size=34,
    )


def plane_checks():
    first = tex_parts(r"\mathbf z", r"\cdot", r"\mathbf u_1", "=", r"1 - 1 + 0 = 0", colors=(Palette.pink, None, Palette.i_hat), font_size=34)
    second = tex_parts(r"\mathbf z", r"\cdot", r"\mathbf u_2", "=", r"-1 - 1 + 2 = 0", colors=(Palette.pink, None, Palette.j_hat), font_size=34)
    return VGroup(first, second).arrange(DOWN, aligned_edge=LEFT, buff=0.25)


def decomposition():
    return tex_parts(
        r"\mathbf y", "=", r"\hat{\mathbf y}", "+", r"\mathbf z", r",\quad", r"\hat{\mathbf y}\in W", r",\quad", r"\mathbf z\in W^\perp",
        colors=(Palette.yellow, None, Palette.teal, None, Palette.pink, None, Palette.teal, None, Palette.pink), font_size=34,
    )


def pythagoras():
    return tex_parts(
        r"\|\mathbf y-\mathbf v\|^2", "=", r"\|\mathbf z\|^2", "+", r"\|\hat{\mathbf y}-\mathbf v\|^2",
        colors=(Palette.blue, None, Palette.pink, None, Palette.teal), font_size=34,
    )


def pythagoras_numbers(v_point):
    far = float(np.sum((Y - v_point) ** 2))
    near = float(np.sum((YHAT - v_point) ** 2))
    return tex_parts(
        f"{far:g}", "=", f"{float(np.sum(Z ** 2)):g}", "+", f"{near:g}",
        colors=(Palette.blue, None, Palette.pink, None, Palette.teal), font_size=34,
    )


def stack_in_panel(*rows, buff=0.4, left=PANEL_LEFT):
    column_of_rows = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=buff)
    return column_of_rows.next_to([left, PANEL_TOP, 0], DR, buff=0).shift(DOWN * 0.1)


class Lesson(LessonScene):
    day = 36
    title = "Orthogonal projection"

    def construct(self):
        plane = plane_at(FLAT_ORIGIN, FLAT_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.meet_the_line(plane)
        line = self.drop_to_line(plane, line)
        line = self.line_weight(line)
        line = self.recall_day17(line)
        self.clear_stage()
        line = None
        self.view = OrbitingView(SPACE_ORIGIN, SPACE_UNIT, azimuth=AZIMUTH, elevation=ELEVATION)
        line = self.meet_the_plane(line)
        line = self.drop_to_plane(line)
        line = self.sum_of_shadows(line)
        line = self.check_both(line)
        line = self.split_uniquely(line)
        line = self.search_the_plane(line)
        line = self.closest_point(line)
        self.close_episode(
            r"Projecting onto a subspace finds its closest point.\\"
            r"The leftover piece is perpendicular to the subspace.",
            *self.mobjects,
        )

    def project(self, point):
        return self.view.project(point)

    def clear_stage(self, run_time=0.7):
        leaving = list(self.mobjects)
        for mobject in leaving:
            mobject.clear_updaters()
        self.play(*[FadeOut(mobject) for mobject in leaving], run_time=run_time)
        self.remove(*leaving)

    def flat_label(self, plane, coords, tex, color, direction, buff=0.14):
        return backed(MathTex(tex, color=color, font_size=42), padding=0.07).next_to(flat_point(plane, coords), direction, buff=buff)

    def meet_the_line(self, plane):
        self.line_l = line_through_origin(plane, U_LINE, color=Palette.teal, stroke_width=3, opacity=0.75)
        self.u_arrow = vector_arrow(U_LINE, Palette.i_hat, plane)
        self.y_arrow = vector_arrow(Y_FLAT, Palette.yellow, plane)
        self.flat_labels = VGroup(
            self.flat_label(plane, U_LINE, r"\mathbf u", Palette.i_hat, DR, buff=0.05),
            self.flat_label(plane, (4.6, 4.6), "L", Palette.teal, DR, buff=0.1),
            self.flat_label(plane, Y_FLAT, r"\mathbf y", Palette.yellow, LEFT),
        )
        line = self.say(r"Here is a vector $\mathbf y$ and the line $L$ through $\mathbf u$.", hold=0.2)
        self.play(Create(self.line_l), run_time=1.0)
        self.play(GrowArrow(self.u_arrow), FadeIn(self.flat_labels[:2]), run_time=0.9, rate_func=spring_soft)
        self.play(GrowArrow(self.y_arrow), FadeIn(self.flat_labels[2]), run_time=1.1, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Yesterday the dot product told us when vectors are perpendicular.", line, hold=Timing.beat)
        line = self.say(r"Today we find the point of $L$ closest to $\mathbf y$.", line, hold=0.2)
        self.play(Indicate(self.line_l, color=Palette.glow, scale_factor=1.0), run_time=1.0)
        line = self.say(r"Day 38 needs this when $A\mathbf x = \mathbf b$ has no solution.", line, hold=Timing.read_short)
        return line

    def drop_to_line(self, plane, line):
        drop = DashedLine(flat_point(plane, Y_FLAT), flat_point(plane, YHAT_FLAT), color=Palette.text_muted, stroke_width=3)
        foot = Dot(flat_point(plane, YHAT_FLAT), radius=0.08, color=Palette.teal)
        line = self.say(r"Drop a perpendicular from the tip of $\mathbf y$ onto $L$.", line, hold=0.2)
        self.play(Create(drop), run_time=1.2)
        self.play(GrowFromCenter(foot), run_time=0.5, rate_func=spring)
        self.wait(Timing.beat)

        yhat = vector_arrow(YHAT_FLAT, Palette.teal, plane, stroke_width=7)
        yhat_label = self.flat_label(plane, YHAT_FLAT, r"\hat{\mathbf y}", Palette.teal, DR, buff=0.1)
        line = self.say(r"Its foot is the projection $\hat{\mathbf y}$, a multiple of $\mathbf u$.", line, hold=0.2)
        self.play(GrowArrow(yhat), FadeIn(yhat_label), FadeOut(foot), run_time=1.2, rate_func=spring_soft)
        self.bring_to_front(self.u_arrow)
        self.wait(Timing.read_short)

        z_arrow = arrow_between(plane, YHAT_FLAT, Y_FLAT, Palette.pink)
        z_label = self.flat_label(plane, (YHAT_FLAT + Y_FLAT) / 2, r"\mathbf z", Palette.pink, UR, buff=0.08)
        mark = corner_mark(lambda point: plane.c2p(*point), YHAT_FLAT, Y_FLAT - YHAT_FLAT, -YHAT_FLAT, size=0.4)
        line = self.say(r"The leftover $\mathbf z = \mathbf y - \hat{\mathbf y}$ meets $L$ at a right angle.", line, hold=0.2)
        self.play(FadeOut(drop), GrowArrow(z_arrow), FadeIn(z_label), run_time=1.1, rate_func=spring_soft)
        self.play(Create(mark), run_time=0.6)
        self.play(Flash(mark.get_center(), color=Palette.glow, line_length=0.25, flash_radius=0.45), run_time=0.8)
        self.wait(Timing.read_short)
        self.flat_labels.add(yhat_label, z_label)
        return line

    def line_weight(self, line):
        formula = line_formula()
        numbers = line_numbers()
        check = line_check()
        stack_in_panel(formula, numbers, check, buff=0.5, left=FLAT_PANEL_LEFT)
        numbers.shift(RIGHT * (formula[1].get_left()[0] - numbers[0].get_left()[0]))
        self.panel_rows = VGroup(formula, numbers, check)
        self.panel_plate = plate_for(formula, padding=0.3)
        line = self.say(r"The weight on $\mathbf u$ is $\mathbf y\cdot\mathbf u$ over $\mathbf u\cdot\mathbf u$.", line, hold=0.2)
        self.play(FadeIn(self.panel_plate), Write(formula), run_time=1.4)
        self.wait(Timing.beat)
        line = self.say(r"Here $\mathbf y\cdot\mathbf u = 6$ and $\mathbf u\cdot\mathbf u = 2$, so $\hat{\mathbf y} = 3\mathbf u$.", line, hold=0.2)
        self.play(Transform(self.panel_plate, plate_for(self.panel_rows[:2], padding=0.3)), FadeIn(numbers, shift=DOWN * 0.15), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"Check the right angle with a dot product.", line, hold=0.2)
        self.play(Transform(self.panel_plate, plate_for(self.panel_rows, padding=0.3)), FadeIn(check, shift=DOWN * 0.15), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return line

    def recall_day17(self, line):
        callback = day17_projection().move_to(self.panel_rows[2], aligned_edge=LEFT)
        line = self.say(r"Day 17's matrix $P$ was this same projection onto $L$.", line, hold=0.2)
        self.play(FadeOut(self.panel_rows[2], shift=UP * 0.15), FadeIn(callback, shift=UP * 0.15), run_time=0.9)
        self.panel_rows.remove(self.panel_rows[2])
        self.panel_rows.add(callback)
        self.play(Transform(self.panel_plate, plate_for(self.panel_rows, padding=0.3)), run_time=0.5)
        self.wait(Timing.read_long)
        return line

    def meet_the_plane(self, line):
        self.axes = always_redraw(lambda: floor_and_axes(self.project, SPACE_REACH))
        self.sheet = always_redraw(lambda: projected_patch(self.project, U1, U2, PATCH_S, PATCH_T, color=Palette.teal, opacity=0.2))
        self.w_tag = always_redraw(lambda: self.space_tag(PATCH_S[0] * U1 + PATCH_T[0] * U2, "W", Palette.teal, UP, buff=0.3))
        self.y_space = always_redraw(lambda: projected_arrow(self.project, Y, Palette.yellow))
        self.y_tag = always_redraw(lambda: self.space_tag(Y, r"\mathbf y", Palette.yellow, UP))
        line = self.say(r"Now project $\mathbf y$ onto a plane $W$ in $\mathbb R^3$.", line, hold=0.2)
        self.play(Create(self.axes), run_time=1.0)
        self.play(FadeIn(self.sheet), FadeIn(self.w_tag), run_time=1.0)
        self.play(GrowArrow(self.y_space), FadeIn(self.y_tag), run_time=1.1, rate_func=spring_soft)
        self.wait(Timing.beat)
        return line

    def space_tag(self, point, tex, color, direction, buff=0.12):
        return backed(MathTex(tex, color=color, font_size=40), padding=0.07).next_to(self.project(point), direction, buff=buff)

    def drop_to_plane(self, line):
        drop = always_redraw(lambda: DashedLine(self.project(Y), self.project(YHAT), color=Palette.text_muted, stroke_width=3))
        self.yhat_space = always_redraw(lambda: projected_arrow(self.project, YHAT, Palette.teal, stroke_width=7))
        self.yhat_tag = always_redraw(lambda: self.space_tag(YHAT, r"\hat{\mathbf y}", Palette.teal, DR, buff=0.08))
        line = self.say(r"Drop a perpendicular from $\mathbf y$ straight down to $W$.", line, hold=0.2)
        self.play(Create(drop), run_time=1.2)
        self.play(GrowArrow(self.yhat_space), FadeIn(self.yhat_tag), run_time=1.1, rate_func=spring_soft)
        self.wait(Timing.beat)

        self.halo = always_redraw(lambda: Line(self.project(YHAT), self.project(Y), color=Palette.glow, stroke_width=18, stroke_opacity=0.28))
        self.z_space = always_redraw(lambda: projected_arrow(self.project, Y, Palette.pink, start=YHAT))
        self.z_tag = always_redraw(lambda: self.space_tag((Y + YHAT) / 2, r"\mathbf z", Palette.pink, RIGHT, buff=0.18))
        self.mark = always_redraw(lambda: corner_mark(self.project, YHAT, Z, -YHAT, size=0.35))
        line = self.say(r"The error $\mathbf z$ stands at a right angle to all of $W$.", line, hold=0.2)
        self.play(FadeOut(drop), GrowArrow(self.z_space), FadeIn(self.z_tag), run_time=1.1, rate_func=spring_soft)
        self.remove(drop)
        self.bring_to_back(self.halo)
        self.bring_to_back(self.sheet)
        self.bring_to_back(self.axes)
        self.play(FadeIn(self.halo), Create(self.mark), run_time=0.8)
        self.sfx("sweep", gain=-6)
        self.play(self.view.turn_to(SWUNG), run_time=3.2, rate_func=smooth)
        self.play(self.view.turn_to(AZIMUTH), run_time=2.6, rate_func=smooth)
        self.wait(Timing.beat)
        return line

    def sum_of_shadows(self, line):
        axis1 = always_redraw(lambda: DashedLine(self.project(PATCH_S[0] * U1), self.project(PATCH_S[1] * U1), color=Palette.i_hat, stroke_width=2.5, stroke_opacity=0.8))
        axis2 = always_redraw(lambda: DashedLine(self.project(PATCH_T[0] * U2), self.project(PATCH_T[1] * U2), color=Palette.j_hat, stroke_width=2.5, stroke_opacity=0.8))
        u1_arrow = always_redraw(lambda: projected_arrow(self.project, U1, Palette.i_hat, stroke_width=5))
        u2_arrow = always_redraw(lambda: projected_arrow(self.project, U2, Palette.j_hat, stroke_width=5))
        givens = plane_givens()
        formula = plane_formula()
        numbers = plane_numbers()
        stack_in_panel(givens, formula, numbers, buff=0.45)
        numbers.shift(RIGHT * (formula[1].get_left()[0] - numbers[0].get_left()[0]))
        self.panel_rows = VGroup(givens, formula, numbers)
        self.panel_plate = plate_for(self.panel_rows, padding=0.3)
        line = self.say(r"We want a formula for $\hat{\mathbf y}$, not just a picture.", line, hold=Timing.beat)
        line = self.say(r"Give $W$ a basis whose vectors are perpendicular.", line, hold=0.2)
        self.play(FadeIn(self.panel_plate), FadeIn(givens), run_time=0.8)
        self.play(Create(axis1), Create(axis2), run_time=1.0)
        self.play(GrowArrow(u1_arrow), GrowArrow(u2_arrow), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.beat)

        first_shadow, second_shadow = 2 * U1, 1 * U2
        drops = VGroup(
            DashedLine(self.project(Y), self.project(first_shadow), color=Palette.i_hat, stroke_width=2.5),
            DashedLine(self.project(Y), self.project(second_shadow), color=Palette.j_hat, stroke_width=2.5),
        )
        shadow1 = projected_arrow(self.project, first_shadow, Palette.i_hat, stroke_width=7)
        shadow2 = projected_arrow(self.project, second_shadow, Palette.j_hat, stroke_width=7)
        line = self.say(r"Project $\mathbf y$ onto each basis line separately.", line, hold=0.2)
        self.play(Write(formula), run_time=1.4)
        self.play(Create(drops[0]), GrowArrow(shadow1), run_time=1.2)
        self.play(Create(drops[1]), GrowArrow(shadow2), run_time=1.2)
        self.play(FadeIn(numbers, shift=DOWN * 0.15), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.beat)

        line = self.say(r"Add the two shadows and you land exactly on $\hat{\mathbf y}$.", line, hold=0.2)
        moved = shadow2.copy()
        self.add(moved)
        self.play(FadeOut(drops), moved.animate.shift(self.project(first_shadow) - self.project((0, 0, 0))), run_time=1.5, rate_func=spring)
        self.play(Flash(self.project(YHAT), color=Palette.glow, line_length=0.25, flash_radius=0.4), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"Day 37 builds a perpendicular basis from any basis.", line, hold=0.2)
        self.play(Indicate(VGroup(u1_arrow, u2_arrow), color=Palette.glow, scale_factor=1.0), run_time=1.0)
        self.wait(Timing.beat)
        self.play(FadeOut(VGroup(shadow1, shadow2, moved)), run_time=0.6)
        self.remove(drops)
        self.basis_parts = VGroup(axis1, axis2, u1_arrow, u2_arrow)
        return line

    def check_both(self, line):
        checks = plane_checks().next_to(self.panel_rows, DOWN, buff=0.45, aligned_edge=LEFT)
        self.panel_rows.add(checks)
        grown = plate_for(self.panel_rows, padding=0.3)
        line = self.say(r"Check: $\mathbf z$ is perpendicular to both $\mathbf u_1$ and $\mathbf u_2$.", line, hold=0.2)
        self.play(Transform(self.panel_plate, grown), FadeIn(checks[0], shift=DOWN * 0.15), run_time=0.9, rate_func=spring_soft)
        self.play(FadeIn(checks[1], shift=DOWN * 0.15), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return line

    def split_uniquely(self, line):
        statement = decomposition().next_to(self.panel_rows[:2], DOWN, buff=0.5, aligned_edge=LEFT)
        leaving = VGroup(self.panel_rows[2], self.panel_rows[3])
        line = self.say(r"Every $\mathbf y$ splits in exactly one way like this.", line, hold=0.2)
        self.play(FadeOut(leaving, shift=UP * 0.15), FadeIn(statement, shift=UP * 0.15), run_time=0.9)
        self.panel_rows.remove(*leaving)
        self.panel_rows.add(statement)
        self.play(Transform(self.panel_plate, plate_for(self.panel_rows, padding=0.3)), run_time=0.6)
        self.play(Circumscribe(statement, color=Palette.glow, buff=0.1), run_time=1.2)
        self.wait(Timing.read_short)
        return line

    def v_point(self):
        return self.weight_a.get_value() * U1 + self.weight_b.get_value() * U2

    def distance_readout(self):
        distance = float(np.linalg.norm(Y - self.v_point()))
        label = MathTex(r"\|\mathbf y-\mathbf v\|", "=", color=Palette.text, font_size=40)
        label[0].set_color(Palette.blue)
        value = DecimalNumber(distance, num_decimal_places=2, color=Palette.blue, font_size=40)
        value.next_to(label, RIGHT, buff=0.18)
        return VGroup(label, value).next_to(self.panel_rows[-1], DOWN, buff=0.55, aligned_edge=LEFT)

    def search_the_plane(self, line):
        self.weight_a, self.weight_b = ValueTracker(WANDER[0][0]), ValueTracker(WANDER[0][1])
        self.gap = always_redraw(lambda: Line(self.project(Y), self.project(self.v_point()), color=Palette.blue, stroke_width=4))
        self.v_dot = always_redraw(lambda: Dot(self.project(self.v_point()), radius=0.09, color=Palette.blue))
        self.v_tag = always_redraw(lambda: self.space_tag(self.v_point(), r"\mathbf v", Palette.blue, DL, buff=0.08))
        self.readout = always_redraw(self.distance_readout)
        line = self.say(r"Is $\hat{\mathbf y}$ really the closest point of $W$ to $\mathbf y$?", line, hold=0.2)
        self.play(FadeOut(self.basis_parts), run_time=0.6)
        self.remove(*self.basis_parts)
        self.play(Transform(self.panel_plate, plate_for(VGroup(self.panel_rows, self.distance_readout()), padding=0.3)), run_time=0.6)
        self.play(Create(self.gap), GrowFromCenter(self.v_dot), FadeIn(self.v_tag), FadeIn(self.readout), run_time=1.0)
        line = self.say(r"Slide another point $\mathbf v$ around $W$ and watch the distance.", line, hold=0.2)
        for a_value, b_value in WANDER[1:]:
            self.play(self.weight_a.animate.set_value(a_value), self.weight_b.animate.set_value(b_value), run_time=1.8, rate_func=spring_soft)
            self.wait(0.5)
        return line

    def closest_point(self, line):
        v_now = self.v_point()
        leg = always_redraw(lambda: DashedLine(self.project(YHAT), self.project(self.v_point()), color=Palette.teal, stroke_width=3))
        corner = corner_mark(self.project, YHAT, Z, v_now - YHAT, size=0.3)
        law = pythagoras()
        values = pythagoras_numbers(v_now)
        stack = VGroup(law, values).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        stack.next_to(self.distance_readout(), DOWN, buff=0.45, aligned_edge=LEFT)
        values.shift(RIGHT * (law[1].get_center()[0] - values[1].get_center()[0]))
        line = self.say(r"The path through $\hat{\mathbf y}$ makes a right triangle.", line, hold=0.2)
        self.play(Transform(self.panel_plate, plate_for(VGroup(self.panel_rows, self.distance_readout(), stack), padding=0.3)), Create(leg), Create(corner), run_time=0.9)
        self.play(Write(law), run_time=1.2)
        self.play(FadeIn(values, shift=DOWN * 0.15), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"The distance is smallest exactly when $\mathbf v = \hat{\mathbf y}$.", line, hold=0.2)
        self.play(FadeOut(corner), FadeOut(values), run_time=0.5)
        self.play(self.weight_a.animate.set_value(2.0), self.weight_b.animate.set_value(1.0), run_time=2.0, rate_func=spring_soft)
        self.play(Flash(self.project(YHAT), color=Palette.glow, line_length=0.25, flash_radius=0.4), run_time=0.8)
        self.wait(Timing.read_short)
        line = self.say(r"So $\hat{\mathbf y}$ is the best approximation to $\mathbf y$ in $W$.", line, hold=Timing.read_long)
        return line


def flat_scene_parts(plane):
    mark = corner_mark(lambda point: plane.c2p(*point), YHAT_FLAT, Y_FLAT - YHAT_FLAT, -YHAT_FLAT, size=0.4)
    labels = VGroup(
        backed(MathTex(r"\mathbf u", color=Palette.i_hat, font_size=42), padding=0.07).next_to(plane.c2p(*U_LINE), DR, buff=0.05),
        backed(MathTex("L", color=Palette.teal, font_size=42), padding=0.07).next_to(plane.c2p(4.6, 4.6), DR, buff=0.1),
        backed(MathTex(r"\mathbf y", color=Palette.yellow, font_size=42), padding=0.07).next_to(plane.c2p(*Y_FLAT), LEFT, buff=0.14),
        backed(MathTex(r"\hat{\mathbf y}", color=Palette.teal, font_size=42), padding=0.07).next_to(plane.c2p(*YHAT_FLAT), DR, buff=0.1),
        backed(MathTex(r"\mathbf z", color=Palette.pink, font_size=42), padding=0.07).next_to(plane.c2p(*((YHAT_FLAT + Y_FLAT) / 2)), UR, buff=0.08),
    )
    return VGroup(
        line_through_origin(plane, U_LINE, color=Palette.teal, stroke_width=3, opacity=0.75),
        vector_arrow(YHAT_FLAT, Palette.teal, plane, stroke_width=7),
        vector_arrow(U_LINE, Palette.i_hat, plane),
        vector_arrow(Y_FLAT, Palette.yellow, plane),
        arrow_between(plane, YHAT_FLAT, Y_FLAT, Palette.pink),
        mark,
        labels,
    )


class FigLineProjection(Scene):
    def construct(self):
        plane = plane_at((-3.2, -2.4), 1.0)
        parts = flat_scene_parts(plane)
        formula = line_formula()
        numbers = line_numbers()
        rows = VGroup(formula, numbers).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        numbers.shift(RIGHT * (formula[1].get_left()[0] - numbers[0].get_left()[0]))
        rows.move_to([4.6, -1.3, 0])
        self.add(plane, parts, plate_for(rows, padding=0.3), rows)


def space_figure_parts(project, tag):
    return VGroup(
        floor_and_axes(project, SPACE_REACH),
        projected_patch(project, U1, U2, PATCH_S, PATCH_T, color=Palette.teal, opacity=0.2),
        Line(project(YHAT), project(Y), color=Palette.glow, stroke_width=18, stroke_opacity=0.28),
        projected_arrow(project, YHAT, Palette.teal, stroke_width=7),
        projected_arrow(project, Y, Palette.yellow),
        projected_arrow(project, Y, Palette.pink, start=YHAT),
        corner_mark(project, YHAT, Z, -YHAT, size=0.35),
        tag(Y, r"\mathbf y", Palette.yellow, UP),
        tag(YHAT, r"\hat{\mathbf y}", Palette.teal, DR),
        tag((Y + YHAT) / 2, r"\mathbf z", Palette.pink, RIGHT),
        tag(PATCH_S[0] * U1 + PATCH_T[0] * U2, "W", Palette.teal, UP),
    )


def figure_tag(project):
    def tag(point, tex, color, direction):
        return backed(MathTex(tex, color=color, font_size=40), padding=0.07).next_to(project(point), direction, buff=0.12)

    return tag


class FigPlaneProjection(Scene):
    def construct(self):
        view = OrbitingView((-3.4, 0.2), SPACE_UNIT, azimuth=AZIMUTH, elevation=ELEVATION)
        project = view.project
        tag = figure_tag(project)
        parts = space_figure_parts(project, tag)
        shadows = VGroup(
            DashedLine(project(PATCH_S[0] * U1), project(PATCH_S[1] * U1), color=Palette.i_hat, stroke_width=2.5, stroke_opacity=0.8),
            DashedLine(project(PATCH_T[0] * U2), project(PATCH_T[1] * U2), color=Palette.j_hat, stroke_width=2.5, stroke_opacity=0.8),
            projected_arrow(project, 2 * U1, Palette.i_hat, stroke_width=6),
            projected_arrow(project, U2, Palette.j_hat, stroke_width=6),
            projected_arrow(project, 2 * U1 + U2, Palette.j_hat, start=2 * U1, stroke_width=6),
            tag(2 * U1, r"2\mathbf u_1", Palette.i_hat, DOWN),
            tag(U2, r"\mathbf u_2", Palette.j_hat, LEFT),
        )
        rows = VGroup(plane_formula(), plane_numbers()).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        rows[1].shift(RIGHT * (rows[0][1].get_left()[0] - rows[1][0].get_left()[0]))
        rows.move_to([3.7, 0.9, 0])
        self.add(parts, shadows, plate_for(rows, padding=0.3), rows)
        fit_to_frame(self)


class FigClosestPoint(Scene):
    def construct(self):
        view = OrbitingView((-3.4, 0.2), SPACE_UNIT, azimuth=AZIMUTH, elevation=ELEVATION)
        project = view.project
        tag = figure_tag(project)
        v_point = WANDER[2][0] * U1 + WANDER[2][1] * U2
        parts = space_figure_parts(project, tag)
        triangle = VGroup(
            Line(project(Y), project(v_point), color=Palette.blue, stroke_width=4),
            DashedLine(project(YHAT), project(v_point), color=Palette.teal, stroke_width=3),
            Dot(project(v_point), radius=0.09, color=Palette.blue),
            tag(v_point, r"\mathbf v", Palette.blue, DL),
        )
        rows = VGroup(pythagoras(), pythagoras_numbers(v_point)).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        rows[1].shift(RIGHT * (rows[0][1].get_center()[0] - rows[1][1].get_center()[0]))
        rows.move_to([3.8, 0.9, 0])
        self.add(parts, triangle, plate_for(rows, padding=0.3), rows)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        view = OrbitingView((-0.9, 0.5), 1.4, azimuth=40.0, elevation=ELEVATION)
        project = view.project
        self.add(space_figure_parts(project, figure_tag(project)))
