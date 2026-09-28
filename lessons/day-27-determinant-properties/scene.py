import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    LiveTransform,
    OrbitingView,
    Palette,
    Timing,
    arrow_between,
    backed,
    column,
    column_parallelogram,
    fit_to_frame,
    make_plane,
    floor_and_axes,
    matrix,
    morph_matrix,
    parallelepiped,
    plane_at,
    projected_arrow,
    scrim,
    spring,
    spring_soft,
    vector_arrow,
)

BASE = (3, 0)
X_START = (1, 1)
U = (1, 1)
V = (-2, 2)
LINEAR_ORIGIN = (-2.8, -1.5)
LINEAR_UNIT = 1.1
BAR_X = (4.5, 5.0, 5.6)

B_ROWS = ((1, 1), (0, 2))
A_ROWS = ((2, 1), (-1, 1))
AB_ROWS = ((2, 4), (-1, 1))
UNIT_SQUARE = ((0, 0), (1, 0), (1, 1), (0, 1))
PRODUCT_ORIGIN = (-6.2, -0.6)
PRODUCT_UNIT = 1.4
PRODUCT_LEFT = 2.7

CRAMER_A1 = np.array([2.0, 1.0])
CRAMER_A2 = np.array([-1.0, 2.0])
CRAMER_B = (3, 4)
CRAMER_ORIGIN = (-5.0, -3.0)
CRAMER_UNIT = 0.95

BOX = (np.array([3.0, 0.0, 0.0]), np.array([0.0, 2.0, 0.0]), np.array([0.0, 0.0, 2.0]))
BOX_STEPS = ([[3, 0, 0], [0, 2, 0], [0, 0, 2]], [[3, 0, 1], [0, 2, 1], [0, 0, 2]], [[3, 1, 1], [0, 2, 1], [0, 0, 2]])
BOX_COLORS = (Palette.i_hat, Palette.j_hat, Palette.pink)
BOX_ORIGIN = (-3.3, -0.7)
BOX_UNIT = 1.2

PANEL_LEFT = 1.4
PROOF_CENTER = (4.3, 0.3, 0)
PROOF_WIDTH = 5.0


def det_tex(first, second, first_color=Palette.i_hat, second_color=Palette.yellow, font_size=40, tail=()):
    """det[first second] with each column name in its arrow's color, followed by optional plain parts."""
    formula = MathTex(r"\det\big[", first, r"\;\;" + second, r"\big]", *tail, color=Palette.text, font_size=font_size)
    formula[1].set_color(first_color)
    formula[2].set_color(second_color)
    return formula


def capped(mobject, width=PROOF_WIDTH):
    if mobject.width > width:
        mobject.scale_to_fit_width(width)
    return mobject


def height_mark(plane, tip):
    """An orange dashed drop from the tip of x to the base line, labelled h."""
    if abs(tip[1]) < 0.05:
        return VGroup()
    drop = DashedLine(plane.c2p(*tip), plane.c2p(tip[0], 0), color=Palette.glow, stroke_width=4, dash_length=0.12)
    label = MathTex("h", color=Palette.glow, font_size=38).next_to(drop, RIGHT, buff=0.12)
    return VGroup(drop, label)


def height_bar(plane, x, low, high, color):
    return Line(plane.c2p(x, low), plane.c2p(x, high), color=color, stroke_width=12)


def colored_matrix(rows, colors, font_size=40):
    mat = matrix([[str(entry) for entry in row] for row in rows], element_to_mobject_config={"font_size": font_size})
    for part, color in zip(mat.get_columns(), colors):
        if color:
            part.set_color(color)
    return mat


def named(name, mat, font_size=40):
    return VGroup(MathTex(name, "=", color=Palette.text, font_size=font_size), mat).arrange(RIGHT, buff=0.18)


def live_polygon(plane, live, tint, corners=UNIT_SQUARE):
    color = interpolate_color(ManimColor(Palette.yellow), ManimColor(Palette.teal), tint.get_value())
    return Polygon(*[plane.c2p(*live.point(corner)) for corner in corners], color=color, fill_opacity=0.35, stroke_width=3)


def outline(plane, rows, color, corners=UNIT_SQUARE):
    transform = np.array(rows, dtype=float)
    shape = Polygon(*[plane.c2p(*(transform @ np.array(corner, dtype=float))) for corner in corners], color=color, stroke_width=3, fill_opacity=0)
    return DashedVMobject(shape, num_dashes=40)


def safe_arrow(plane, coords, color, stroke_width=6):
    if np.hypot(*coords) < 0.05:
        return VGroup()
    return vector_arrow(coords, color, plane, stroke_width=stroke_width)


def box_edges(tops, sides):
    first = BOX[0]
    second = BOX[1] + sides * np.array([1.0, 0.0, 0.0])
    third = BOX[2] + tops * np.array([1.0, 1.0, 0.0])
    return first, second, third


class Lesson(LessonScene):
    day = 27
    title = "Determinant properties and Cramer's rule"

    def construct(self):
        plane = plane_at(LINEAR_ORIGIN, LINEAR_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.signed_area(plane)
        line = self.stacked_heights(plane, line)
        line = self.below_the_base(line)
        line = self.swap_flips(line)
        line = self.equal_columns(line)
        line = self.replacement_is_free(line)
        line = self.clear_stage(line)
        line = self.product_rule(line)
        line = self.clear_stage(line)
        line = self.cramer(line)
        line = self.adjugate(line)
        line = self.volume(line)
        self.close_episode(
            r"The determinant is linear in each column and flips sign on a swap.\\"
            r"That is why $\det(AB) = \det A\,\det B$ and Cramer's rule work.",
            *self.mobjects,
        )

    def clear_stage(self, line, run_time=0.7):
        leaving = list(self.mobjects)
        for mobject in leaving:
            mobject.clear_updaters()
        self.play(*[FadeOut(mobject) for mobject in leaving], run_time=run_time)
        self.remove(*leaving)
        return None

    def x_value(self):
        return (self.x_tip[0].get_value(), self.x_tip[1].get_value())

    def move_x(self, target, run_time=1.6, rate_func=spring):
        self.play(*[tracker.animate.set_value(value) for tracker, value in zip(self.x_tip, target)], run_time=run_time, rate_func=rate_func)

    def panel_row(self, mobject, y):
        mobject.move_to([0, y, 0])
        return mobject.shift(RIGHT * (PANEL_LEFT - mobject.get_left()[0]))

    def proof_box(self, mobject):
        return backed(capped(mobject).move_to(PROOF_CENTER), padding=0.2)

    def signed_area(self, plane):
        self.plane = plane
        self.x_tip = [ValueTracker(value) for value in X_START]
        self.base_arrow = vector_arrow(BASE, Palette.i_hat, plane)
        self.base_name = MathTex(r"\mathbf a_1", color=Palette.i_hat, font_size=40).next_to(plane.c2p(*BASE), DOWN, buff=0.2)
        self.x_arrow = always_redraw(lambda: vector_arrow(self.x_value(), Palette.yellow, plane))
        self.x_name = always_redraw(lambda: MathTex(r"\mathbf x", color=Palette.yellow, font_size=40).next_to(plane.c2p(*self.x_value()), UL, buff=0.08))
        self.area = always_redraw(lambda: column_parallelogram(plane, BASE, self.x_value()))
        self.readout = det_tex(r"\mathbf a_1", r"\mathbf x", tail=("=",))
        self.value = DecimalNumber(3.0, num_decimal_places=1, color=Palette.text, font_size=40)
        self.value.add_updater(lambda m: m.set_value(3 * self.x_tip[1].get_value()).next_to(self.readout, RIGHT, buff=0.18))
        self.panel_row(self.readout, 3.45)
        self.value.next_to(self.readout, RIGHT, buff=0.18)

        line = self.say(r"The determinant is the signed area of the columns' parallelogram.", hold=0.2)
        self.play(GrowArrow(self.base_arrow), FadeIn(self.base_name), run_time=1.0, rate_func=spring_soft)
        self.play(GrowArrow(vector_arrow(X_START, Palette.yellow, plane)), FadeIn(self.x_name), run_time=1.0, rate_func=spring_soft)
        self.remove(*[m for m in self.mobjects if isinstance(m, Arrow) and m is not self.base_arrow])
        self.add(self.x_arrow)
        self.bring_to_back(self.area)
        self.bring_to_back(plane)
        self.play(FadeIn(self.area), Write(self.readout), FadeIn(self.value), run_time=1.0)
        self.wait(Timing.beat)

        self.height = always_redraw(lambda: height_mark(plane, self.x_value()))
        self.base_times = MathTex("=", r"3", r"\,h", color=Palette.text, font_size=40)
        self.base_times[2].set_color(Palette.glow)
        self.base_times.next_to(self.readout, DOWN, buff=0.35, aligned_edge=LEFT).shift(RIGHT * (self.readout[-1].get_left()[0] - self.readout.get_left()[0]))
        line = self.say(r"With $\mathbf a_1$ as the base, only the height of $\mathbf x$ matters.", line, hold=0.2)
        self.play(Create(self.height), FadeIn(self.base_times), run_time=1.0)
        self.wait(Timing.beat)

        line = self.say(r"Doubling $\mathbf x$ doubles the height, so the determinant doubles.", line, hold=0.2)
        self.move_x((2, 2), run_time=1.8)
        self.wait(Timing.beat)
        self.move_x(X_START, run_time=1.2, rate_func=spring_soft)
        return line

    def stacked_heights(self, plane, line):
        x_parts = VGroup(self.x_arrow, self.x_name, self.area, self.height)
        self.play(FadeOut(x_parts), FadeOut(self.readout), FadeOut(self.value), FadeOut(self.base_times), run_time=0.6)
        self.remove(x_parts)

        choices = VGroup()
        rows = VGroup()
        for vector, tex, color, y in ((U, r"\mathbf u", Palette.yellow, 3.45), (V, r"\mathbf v", Palette.blue, 2.9)):
            arrow = vector_arrow(vector, color, plane)
            name = MathTex(tex, color=color, font_size=40).next_to(plane.c2p(*vector), UL, buff=0.08)
            shape = column_parallelogram(plane, BASE, vector, color=color, opacity=0.22)
            choices.add(VGroup(shape, arrow, name))
            rows.add(self.panel_row(det_tex(r"\mathbf a_1", tex, second_color=color, tail=("=", str(3 * vector[1]))), y))

        line = self.say(r"Now take two choices, $\mathbf u$ and $\mathbf v$.", line, hold=0.2)
        for choice, row in zip(choices, rows):
            self.play(FadeIn(choice[0]), GrowArrow(choice[1]), FadeIn(choice[2]), FadeIn(row), run_time=1.1, rate_func=spring_soft)
        bars = VGroup(height_bar(plane, BAR_X[0], 0, U[1], Palette.yellow), height_bar(plane, BAR_X[1], 0, V[1], Palette.blue))
        self.play(Create(bars[0]), Create(bars[1]), run_time=0.9)
        self.wait(Timing.beat)

        total = (U[0] + V[0], U[1] + V[1])
        sum_arrow = vector_arrow(total, Palette.teal, plane)
        sum_name = MathTex(r"\mathbf u + \mathbf v", color=Palette.teal, font_size=40).next_to(plane.c2p(*total), UP, buff=0.12)
        sum_shape = column_parallelogram(plane, BASE, total, color=Palette.teal, opacity=0.3)
        sum_bar = height_bar(plane, BAR_X[2], 0, total[1], Palette.teal)
        sum_row = det_tex(r"\mathbf a_1", r"\mathbf u + \mathbf v", second_color=Palette.teal, tail=("=", "9", "=", "3", "+", "6"))
        sum_row[5].set_color(Palette.teal)
        sum_row[7].set_color(Palette.yellow)
        sum_row[9].set_color(Palette.blue)
        self.panel_row(sum_row, 2.35)

        line = self.say(r"Their heights stack, so their determinants add.", line, hold=0.2)
        self.play(bars[1].animate.move_to(plane.c2p(BAR_X[0], U[1] + V[1] / 2)), run_time=1.3, rate_func=spring)
        self.play(FadeOut(choices), FadeIn(sum_shape), GrowArrow(sum_arrow), FadeIn(sum_name), run_time=1.2, rate_func=spring_soft)
        self.play(Create(sum_bar), FadeIn(sum_row), run_time=1.0)
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(sum_shape, sum_arrow, sum_name, sum_bar, bars, rows, sum_row)), run_time=0.6)
        return line

    def below_the_base(self, line):
        line = self.say(r"Below the base, height and determinant both turn negative.", line, hold=0.2)
        self.add(self.area)
        self.bring_to_back(self.area)
        self.bring_to_back(self.plane)
        self.play(FadeIn(self.x_arrow), FadeIn(self.x_name), FadeIn(self.area), FadeIn(self.height), FadeIn(self.readout), FadeIn(self.value), FadeIn(self.base_times), run_time=0.8)
        self.move_x((1, -1), run_time=2.0)
        self.wait(Timing.beat)

        rules = MathTex(
            r"T(\mathbf x) &= \det[\,\mathbf a_1\;\; \mathbf x\,]\\"
            r"T(c\,\mathbf x) &= c\,T(\mathbf x)\\"
            r"T(\mathbf u + \mathbf v) &= T(\mathbf u) + T(\mathbf v)",
            color=Palette.text,
            font_size=36,
        )
        self.rules = self.proof_box(rules)
        line = self.say(r"So the determinant is linear in each column separately.", line, hold=0.2)
        self.move_x(X_START, run_time=1.2, rate_func=spring_soft)
        self.play(FadeIn(self.rules, shift=UP * 0.15), run_time=0.9)
        self.wait(Timing.read_long)
        self.play(FadeOut(self.rules), run_time=0.5)
        return line

    def swap_flips(self, line):
        center = self.plane.c2p(0, 0)
        turn = Arc(radius=0.75, start_angle=0, angle=PI / 4, arc_center=center, color=Palette.glow, stroke_width=5).add_tip(tip_length=0.18)
        back = Arc(radius=0.75, start_angle=PI / 4, angle=-PI / 4, arc_center=center, color=Palette.glow, stroke_width=5).add_tip(tip_length=0.18)
        swapped = det_tex(r"\mathbf x", r"\mathbf a_1", first_color=Palette.yellow, second_color=Palette.i_hat, tail=("=", "-3"))
        swapped.next_to(self.base_times, DOWN, buff=0.45).align_to(self.readout, LEFT)
        still = column_parallelogram(self.plane, BASE, X_START)

        line = self.say(r"Swap the two columns and the sign flips.", line, hold=0.2)
        self.play(Create(turn), run_time=0.8)
        self.remove(self.area)
        self.add(still)
        self.bring_to_back(still)
        self.bring_to_back(self.plane)
        self.play(
            FadeIn(VGroup(swapped[0], swapped[3], swapped[4], swapped[5])),
            TransformFromCopy(self.readout[1], swapped[2]),
            TransformFromCopy(self.readout[2], swapped[1]),
            FadeOut(turn),
            Create(back),
            still.animate.set_fill(Palette.pink),
            run_time=1.4,
        )
        self.wait(Timing.beat)
        self.play(FadeOut(back), FadeOut(swapped), still.animate.set_fill(Palette.yellow), run_time=0.7)
        self.remove(still)
        self.add(self.area)
        self.bring_to_back(self.area)
        self.bring_to_back(self.plane)
        return line

    def equal_columns(self, line):
        proof = MathTex(
            r"\det[\,\mathbf a\;\;\mathbf a\,] = -\det[\,\mathbf a\;\;\mathbf a\,]",
            r"\text{so }\det[\,\mathbf a\;\;\mathbf a\,] = 0",
            color=Palette.text,
            font_size=34,
        )
        proof.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        proof = self.proof_box(proof)
        line = self.say(r"Swapping two equal columns changes nothing, so det must be 0.", line, hold=0.2)
        self.move_x(BASE, run_time=1.8, rate_func=spring_soft)
        self.play(FadeIn(proof, shift=UP * 0.15), run_time=0.9)
        self.wait(Timing.read_short)
        self.play(FadeOut(proof), run_time=0.5)
        self.move_x(X_START, run_time=1.2, rate_func=spring_soft)
        return line

    def replacement_is_free(self, line):
        track = DashedLine(self.plane.c2p(-3.2, 1), self.plane.c2p(6.2, 1), color=Palette.yellow, stroke_width=2.5, dash_length=0.15).set_opacity(0.6)
        proof = VGroup(
            MathTex(r"\det[\,\mathbf a_1\;\; \mathbf x + c\,\mathbf a_1\,]", color=Palette.text, font_size=36),
            MathTex(r"= \det[\,\mathbf a_1\;\; \mathbf x\,] + c\,\det[\,\mathbf a_1\;\; \mathbf a_1\,]", color=Palette.text, font_size=36),
            MathTex(r"= \det[\,\mathbf a_1\;\; \mathbf x\,] + 0", color=Palette.text, font_size=36),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        proof[1:].shift(RIGHT * 0.4)
        proof = self.proof_box(proof)

        line = self.say(r"Adding a multiple of $\mathbf a_1$ slides $\mathbf x$ parallel to the base.", line, hold=0.2)
        self.play(Create(track), run_time=0.8)
        self.move_x((4, 1), run_time=1.6, rate_func=smooth)
        self.move_x((-2, 1), run_time=2.0, rate_func=smooth)
        line = self.say(r"The height never changes, so the determinant stays the same.", line, hold=0.2)
        self.play(FadeIn(proof, shift=UP * 0.15), run_time=0.9)
        self.move_x(X_START, run_time=1.4, rate_func=smooth)
        self.wait(Timing.beat)
        line = self.say(r"Rows follow the same rules, because $\det A^T = \det A$.", line, hold=Timing.read_short)
        return line

    def product_rule(self, line):
        plane = plane_at(PRODUCT_ORIGIN, PRODUCT_UNIT)
        plane.background_lines.set_stroke(opacity=0.25)
        plane.faded_lines.set_stroke(opacity=0.15)
        live = LiveTransform()
        tint = ValueTracker(0.0)
        grid = always_redraw(lambda: live.grid(plane, color=Palette.blue, opacity=0.55, cap=30))
        shape = always_redraw(lambda: live_polygon(plane, live, tint))
        basis = VGroup(
            always_redraw(lambda: safe_arrow(plane, live.point((1, 0)), Palette.i_hat)),
            always_redraw(lambda: safe_arrow(plane, live.point((0, 1)), Palette.j_hat)),
        )
        area_label = MathTex(r"\text{area}", "=", color=Palette.text, font_size=52)
        counter = DecimalNumber(1.0, num_decimal_places=1, color=Palette.yellow, font_size=52)
        area_row = VGroup(area_label, counter).arrange(RIGHT, buff=0.2).move_to([-4.6, 3.25, 0])
        counter.add_updater(lambda m: m.set_value(abs(np.linalg.det(live.value))).next_to(area_label, RIGHT, buff=0.2))
        counter.add_updater(lambda m: m.set_color(interpolate_color(ManimColor(Palette.yellow), ManimColor(Palette.teal), tint.get_value())))

        line = self.say(r"Here is why $\det(AB)$ equals $\det A$ times $\det B$.", line, hold=0.2)
        self.add(grid)
        self.play(FadeIn(plane), FadeIn(grid), FadeIn(shape), GrowArrow(vector_arrow((1, 0), Palette.i_hat, plane)), GrowArrow(vector_arrow((0, 1), Palette.j_hat, plane)), FadeIn(area_row), run_time=1.0)
        self.remove(*[m for m in self.mobjects if isinstance(m, Arrow)])
        self.add(basis)
        square_trace = outline(plane, ((1, 0), (0, 1)), Palette.yellow).set_opacity(0.6)
        self.add(square_trace)
        self.wait(Timing.beat)

        b_row = named("B", colored_matrix(B_ROWS, (Palette.i_hat, Palette.j_hat), font_size=36), font_size=36)
        b_det = MathTex(r"\det B = 2", color=Palette.text, font_size=38)
        self.product_row(VGroup(b_row, b_det).arrange(RIGHT, buff=0.4), 2.55)
        line = self.say(r"First $B$ turns the unit square into area $\det B = 2$.", line, hold=0.2)
        self.play(FadeIn(b_row), run_time=0.7)
        self.play(live.apply(B_ROWS), run_time=2.4, rate_func=spring_soft)
        self.play(FadeIn(b_det, shift=LEFT * 0.2), run_time=0.6)
        self.wait(Timing.beat)

        b_trace = outline(plane, B_ROWS, Palette.yellow)
        a_row = named("A", colored_matrix(A_ROWS, (None, None), font_size=36), font_size=36)
        a_det = MathTex(r"\det A = 3", color=Palette.text, font_size=38)
        self.product_row(VGroup(a_row, a_det).arrange(RIGHT, buff=0.4), 0.95)
        line = self.say(r"Then $A$ multiplies every area by $\det A = 3$.", line, hold=0.2)
        self.add(b_trace)
        self.play(FadeIn(a_row), run_time=0.7)
        self.play(live.apply(A_ROWS), tint.animate.set_value(1.0), run_time=2.8, rate_func=spring_soft)
        self.play(FadeIn(a_det, shift=LEFT * 0.2), run_time=0.6)
        self.wait(Timing.beat)

        ab_trace = outline(plane, AB_ROWS, Palette.teal)
        line = self.say(r"The single map $AB$ lands on the very same shape.", line, hold=0.2)
        self.add(ab_trace)
        self.play(live.apply(np.linalg.inv(np.array(AB_ROWS, dtype=float))), tint.animate.set_value(0.0), run_time=1.8, rate_func=smooth)
        ab_row = self.product_row(named("AB", colored_matrix(AB_ROWS, (Palette.i_hat, Palette.j_hat), font_size=36), font_size=36), -0.65)
        self.play(FadeIn(ab_row), run_time=0.7)
        self.play(live.apply(AB_ROWS), tint.animate.set_value(1.0), run_time=2.6, rate_func=spring_soft)
        self.play(Indicate(ab_trace, color=Palette.glow, scale_factor=1.0), run_time=0.9)

        product = MathTex(r"\det(AB)", "=", r"\det A", r"\,\det B", color=Palette.text, font_size=44)
        numbers = MathTex("6", "=", "3", r"\cdot", "2", color=Palette.text, font_size=44)
        numbers[0].set_color(Palette.teal)
        result = VGroup(product, numbers).arrange(DOWN, buff=0.25)
        result = backed(result, padding=0.2).move_to([4.8, -2.15, 0])
        line = self.say(r"Areas multiply, so determinants multiply.", line, hold=0.2)
        self.play(Write(result), run_time=1.3)
        self.wait(Timing.read_long)
        counter.clear_updaters()
        return line

    def product_row(self, group, y):
        capped(group, 4.2).move_to([0, y, 0])
        return group.shift(RIGHT * (PRODUCT_LEFT - group.get_left()[0]))

    def cramer(self, line):
        plane = plane_at(CRAMER_ORIGIN, CRAMER_UNIT)
        stretch = ValueTracker(1.0)
        shear = ValueTracker(0.0)

        def first_column():
            return stretch.get_value() * CRAMER_A1 + shear.get_value() * CRAMER_A2

        shape = always_redraw(lambda: column_parallelogram(plane, first_column(), CRAMER_A2, opacity=0.32))
        mover = always_redraw(
            lambda: vector_arrow(first_column(), interpolate_color(ManimColor(Palette.i_hat), ManimColor(Palette.yellow), shear.get_value()), plane)
        )
        arrows = VGroup(vector_arrow(CRAMER_A1, Palette.i_hat, plane), vector_arrow(CRAMER_A2, Palette.j_hat, plane), vector_arrow(CRAMER_B, Palette.yellow, plane))
        names = VGroup(
            MathTex(r"\mathbf a_1", color=Palette.i_hat, font_size=40).next_to(plane.c2p(*CRAMER_A1), DOWN, buff=0.15),
            MathTex(r"\mathbf a_2", color=Palette.j_hat, font_size=40).next_to(plane.c2p(*CRAMER_A2), LEFT, buff=0.15),
            MathTex(r"\mathbf b", color=Palette.yellow, font_size=40).next_to(plane.c2p(*CRAMER_B), RIGHT, buff=0.15),
        )
        a_mat = colored_matrix(((2, -1), (1, 2)), (Palette.i_hat, Palette.j_hat))
        unknowns = column([r"x_1", r"x_2"])
        b_col = column(CRAMER_B, color=Palette.yellow)
        system = VGroup(a_mat, unknowns, MathTex("=", color=Palette.text), b_col).arrange(RIGHT, buff=0.2).move_to([2.4, 2.55, 0])
        det_a = MathTex(r"\det A = 5", color=Palette.text, font_size=40).move_to([0.9, 1.15, 0])
        area_label = MathTex(r"\text{area}", "=", color=Palette.text, font_size=44)
        counter = DecimalNumber(5.0, num_decimal_places=1, color=Palette.yellow, font_size=44)
        area_row = VGroup(area_label, counter).arrange(RIGHT, buff=0.2).move_to([4.0, 1.15, 0])
        counter.add_updater(lambda m: m.set_value(abs(np.cross(first_column(), CRAMER_A2))).next_to(area_label, RIGHT, buff=0.2))

        line = self.say(r"Cramer's rule solves $A\mathbf x = \mathbf b$ using determinants.", line, hold=0.2)
        self.play(FadeIn(plane), FadeIn(system), run_time=1.0)
        self.play(*[GrowArrow(arrow) for arrow in arrows], FadeIn(names), run_time=1.1, rate_func=spring_soft)
        self.add(shape, mover)
        self.bring_to_back(shape)
        self.bring_to_back(plane)
        self.play(FadeIn(shape), FadeIn(det_a), FadeIn(area_row), run_time=0.9)
        self.wait(Timing.beat)

        track = DashedLine(plane.c2p(*(2 * CRAMER_A1 - 0.15 * CRAMER_A2)), plane.c2p(*(2 * CRAMER_A1 + 1.3 * CRAMER_A2)), color=Palette.glow, stroke_width=3, dash_length=0.12)
        line = self.say(r"Here $\mathbf b = 2\mathbf a_1 + \mathbf a_2$, so first stretch $\mathbf a_1$ by 2.", line, hold=0.2)
        self.play(stretch.animate.set_value(2.0), run_time=1.8, rate_func=spring)
        self.wait(Timing.beat)
        line = self.say(r"Adding $\mathbf a_2$ is a shear, so the area stays 10.", line, hold=0.2)
        self.play(Create(track), run_time=0.7)
        self.play(shear.animate.set_value(1.0), run_time=2.2, rate_func=smooth)
        self.wait(Timing.beat)
        self.cramer_columns(line, a_mat, b_col, system, det_a, area_row, counter)
        self.cramer_line = self.say(r"Put $\mathbf b$ in column $i$, then divide by $\det A$.", self.cramer_line, hold=0.2)
        self.play(FadeOut(system), FadeOut(det_a), FadeOut(area_row), run_time=0.5)
        self.play(FadeIn(self.cramer_rule, shift=UP * 0.15), run_time=0.9)
        self.wait(Timing.read_long)
        return self.cramer_line

    def cramer_columns(self, line, a_mat, b_col, system, det_a, area_row, counter):
        counter.clear_updaters()
        first = self.replaced(a_mat, b_col, 0).move_to([0, -0.1, 0])
        first.shift(RIGHT * (-0.85 - first.get_left()[0]))
        first_value = MathTex(r"x_1 = \dfrac{10}{5} = 2", color=Palette.text, font_size=36).next_to(first, RIGHT, buff=0.4)
        line = self.say(r"Column 1 is now $\mathbf b$, so $\det A_1(\mathbf b) = x_1 \det A$.", line, hold=0.2)
        self.slide_in(a_mat, b_col, first, 0)
        self.play(FadeIn(first_value, shift=LEFT * 0.2), run_time=0.7)
        self.wait(Timing.read_short)

        second = self.replaced(a_mat, b_col, 1).next_to(first, DOWN, buff=0.4).align_to(first, LEFT)
        second_value = MathTex(r"x_2 = \dfrac{5}{5} = 1", color=Palette.text, font_size=36).next_to(second, RIGHT, buff=0.4)
        self.slide_in(a_mat, b_col, second, 1)
        self.play(FadeIn(second_value, shift=LEFT * 0.2), run_time=0.7)
        rule = MathTex(r"x_i = \frac{\det A_i(\mathbf b)}{\det A}", color=Palette.text, font_size=46)
        self.cramer_rule = backed(rule, padding=0.22).move_to([2.4, 2.4, 0])
        self.cramer_line = line

    def replaced(self, a_mat, b_col, index):
        rows = [["2", "-1"], ["1", "2"]]
        for row, entry in zip(rows, ("3", "4")):
            row[index] = entry
        colors = [Palette.i_hat, Palette.j_hat]
        colors[index] = Palette.yellow
        mat = colored_matrix(rows, colors, font_size=34)
        name = MathTex(rf"\det A_{index + 1}(\mathbf b)", color=Palette.text, font_size=36)
        tail = MathTex("=", "10" if index == 0 else "5", color=Palette.text, font_size=36)
        prefix = MathTex(r"=\det", color=Palette.text, font_size=36)
        return VGroup(name, prefix, mat, tail).arrange(RIGHT, buff=0.15)

    def slide_in(self, a_mat, b_col, target, index):
        name, prefix, mat, tail = target
        keep = 1 - index
        self.play(
            FadeIn(prefix),
            FadeIn(name),
            FadeIn(mat.get_brackets()),
            TransformFromCopy(b_col.get_entries(), VGroup(*[mat.get_rows()[row][index] for row in range(2)]), path_arc=-0.6),
            TransformFromCopy(a_mat.get_columns()[keep], mat.get_columns()[keep]),
            run_time=1.4,
        )
        self.play(FadeIn(tail, shift=LEFT * 0.2), run_time=0.6)

    def adjugate(self, line):
        veil = scrim()
        veil.set_fill(opacity=0)
        self.add(veil)
        self.bring_to_front(line)
        self.play(veil.animate.set_fill(opacity=0.96), run_time=0.7)
        for mobject in self.mobjects:
            mobject.clear_updaters()
        self.remove(*[mobject for mobject in self.mobjects if mobject not in (veil, line)])

        formula = MathTex(r"A^{-1}", "=", r"\frac{1}{\det A}", r"\operatorname{adj} A", color=Palette.text, font_size=60).move_to([0, 2.3, 0])
        formula[3].set_color(Palette.teal)
        line = self.say(r"Cramer's rule on each column of $I$ gives $A^{-1}$.", line, hold=0.2)
        self.play(Write(formula), run_time=1.3)
        self.wait(Timing.beat)

        source = named(r"A", matrix([["a", "b"], ["c", "d"]]), font_size=48)
        cofactors = named(r"C", matrix([["d", "-c"], ["-b", "a"]]), font_size=48)
        adjugate = named(r"\operatorname{adj}A = C^T", matrix([["d", "-b"], ["-c", "a"]]), font_size=48)
        adjugate[1].set_color(Palette.teal)
        row = VGroup(source, cofactors, adjugate).arrange(RIGHT, buff=0.9).move_to([0, -0.2, 0])
        line = self.say(r"The adjugate is the cofactor matrix, transposed.", line, hold=0.2)
        self.play(FadeIn(source), run_time=0.7)
        self.play(FadeIn(cofactors), run_time=0.9)
        c_entries, adj_entries = cofactors[1].get_entries(), adjugate[1].get_entries()
        self.play(
            FadeIn(adjugate[0]),
            FadeIn(adjugate[1].get_brackets()),
            *[TransformFromCopy(c_entries[i], adj_entries[j], path_arc=0.8 if i != j else 0) for i, j in ((0, 0), (1, 2), (2, 1), (3, 3))],
            run_time=1.6,
        )
        day_seven = Tex(r"For $2 \times 2$ matrices this is Day 7's inverse formula.", color=Palette.text_muted, font_size=36).next_to(row, DOWN, buff=0.7)
        self.play(FadeIn(day_seven, shift=UP * 0.15), run_time=0.7)
        self.wait(Timing.read_short)
        self.adjugate_parts = VGroup(formula, row, day_seven)
        self.veil = veil
        return line

    def volume(self, line):
        view = OrbitingView(BOX_ORIGIN, BOX_UNIT, azimuth=-35.0, elevation=22.0)
        tops = ValueTracker(0.0)
        sides = ValueTracker(0.0)
        floor = always_redraw(lambda: floor_and_axes(view.project, ((-1, 4), (-1, 4), (-1, 3))))
        solid = always_redraw(lambda: parallelepiped(view.project, *box_edges(tops.get_value(), sides.get_value()), opacity=0.12))
        edges = VGroup(*[
            always_redraw(lambda index=index, color=color: projected_arrow(view.project, box_edges(tops.get_value(), sides.get_value())[index], color))
            for index, color in enumerate(BOX_COLORS)
        ])
        box_matrix = colored_matrix(BOX_STEPS[0], BOX_COLORS)
        volume_row = MathTex(r"\text{volume} = 12", color=Palette.teal, font_size=48)
        panel = VGroup(named("A", box_matrix), volume_row).arrange(DOWN, buff=0.5).move_to([4.7, 1.3, 0])

        self.play(FadeOut(self.adjugate_parts), run_time=0.6)
        self.add(floor)
        self.bring_to_back(floor)
        self.remove(self.adjugate_parts)
        line = self.say(r"Three columns in $\mathbb R^3$ build a box called a parallelepiped.", line, hold=0.2)
        self.play(FadeOut(self.veil), *[Create(edge) for edge in edges], FadeIn(panel[0]), run_time=1.2)
        self.play(FadeIn(solid), FadeIn(volume_row), run_time=1.0)
        self.wait(Timing.beat)

        line = self.say(r"Column replacement slides a face, and the volume stays 12.", line, hold=0.2)
        self.sfx("slide", gain=-2)
        target = colored_matrix(BOX_STEPS[1], BOX_COLORS).move_to(box_matrix)
        morph_matrix(self, box_matrix, target, tops.animate.set_value(1.0), view.turn_to(-27.0), run_time=2.6, rate_func=smooth)
        target = colored_matrix(BOX_STEPS[2], BOX_COLORS).move_to(box_matrix)
        morph_matrix(self, box_matrix, target, sides.animate.set_value(1.0), view.turn_to(-20.0), run_time=2.6, rate_func=smooth)
        self.play(Indicate(volume_row, color=Palette.glow, scale_factor=1.08), run_time=0.9)

        rule = MathTex(r"\lvert\det A\rvert = 3 \cdot 2 \cdot 2 = 12", color=Palette.text, font_size=40).next_to(panel, DOWN, buff=0.5)
        line = self.say(r"So the volume of the box is $\lvert\det A\rvert$.", line, hold=0.2)
        self.play(FadeIn(rule, shift=UP * 0.15), view.turn_to(-30.0), run_time=2.0)
        self.wait(Timing.read_short)
        return line


class FigHeights(Scene):
    def construct(self):
        plane = plane_at((-3.2, -1.6), 1.25)
        total = (U[0] + V[0], U[1] + V[1])
        self.add(plane)
        for vector, color, opacity in ((U, Palette.yellow, 0.2), (V, Palette.blue, 0.2), (total, Palette.teal, 0.25)):
            self.add(column_parallelogram(plane, BASE, vector, color=color, opacity=opacity, stroke_width=2))
        self.add(vector_arrow(BASE, Palette.i_hat, plane))
        labels = ((U, r"\mathbf u", Palette.yellow, RIGHT), (V, r"\mathbf v", Palette.blue, LEFT), (total, r"\mathbf u + \mathbf v", Palette.teal, UP))
        for vector, tex, color, direction in labels:
            self.add(vector_arrow(vector, color, plane), backed(MathTex(tex, color=color, font_size=40), padding=0.08).next_to(plane.c2p(*vector), direction, buff=0.12))
        self.add(backed(MathTex(r"\mathbf a_1", color=Palette.i_hat, font_size=40), padding=0.08).next_to(plane.c2p(*BASE), DOWN, buff=0.15))
        self.add(
            height_bar(plane, BAR_X[0], 0, U[1], Palette.yellow),
            height_bar(plane, BAR_X[0], U[1], U[1] + V[1], Palette.blue),
            height_bar(plane, BAR_X[0] + 0.6, 0, total[1], Palette.teal),
        )
        equation = backed(MathTex(r"9 = 3 + 6", color=Palette.text, font_size=48), padding=0.15).next_to(plane.c2p(BAR_X[0] + 0.3, 3), UP, buff=0.3)
        equation[1][0].set_color(Palette.teal)
        equation[1][2].set_color(Palette.yellow)
        equation[1][4].set_color(Palette.blue)
        self.add(equation)


class FigProduct(Scene):
    def construct(self):
        stages = (((1, 0), (0, 1)), B_ROWS, AB_ROWS)
        colors = (Palette.yellow, Palette.yellow, Palette.teal)
        titles = (r"\text{area } 1", r"\text{area } 2", r"\text{area } 6")
        panels = VGroup()
        for rows, color, title in zip(stages, colors, titles):
            plane = make_plane(x_range=(-1, 6, 1), y_range=(-2, 3, 1), x_length=7 * 0.55, y_length=5 * 0.55)
            transform = np.array(rows, dtype=float)
            shape = Polygon(*[plane.c2p(*(transform @ np.array(corner, dtype=float))) for corner in UNIT_SQUARE], color=color, fill_opacity=0.35, stroke_width=3)
            arrows = VGroup(vector_arrow(transform[:, 0], Palette.i_hat, plane, stroke_width=5), vector_arrow(transform[:, 1], Palette.j_hat, plane, stroke_width=5))
            label = MathTex(title, color=color, font_size=40).next_to(plane, DOWN, buff=0.25)
            panels.add(VGroup(plane, shape, arrows, label))
        panels.arrange(RIGHT, buff=1.1)
        hops = VGroup()
        for left, right, name, text in ((panels[0], panels[1], "B", r"\times 2"), (panels[1], panels[2], "A", r"\times 3")):
            hop = Arrow(left[0].get_right(), right[0].get_left(), buff=0.15, color=Palette.text_muted, stroke_width=4)
            hops.add(hop, MathTex(name, color=Palette.text, font_size=40).next_to(hop, UP, buff=0.1), MathTex(text, color=Palette.glow, font_size=36).next_to(hop, DOWN, buff=0.1))
        self.add(panels, hops)
        fit_to_frame(self)


class FigCramer(Scene):
    def construct(self):
        plane = plane_at((-3.0, -3.2), 1.0)
        stretched = 2 * CRAMER_A1
        self.add(plane)
        self.add(column_parallelogram(plane, CRAMER_A1, CRAMER_A2, color=Palette.i_hat, opacity=0.25, stroke_width=2))
        self.add(column_parallelogram(plane, CRAMER_B, CRAMER_A2, color=Palette.yellow, opacity=0.25, stroke_width=2))
        self.add(DashedLine(plane.c2p(*stretched), plane.c2p(*CRAMER_B), color=Palette.glow, stroke_width=3, dash_length=0.12))
        self.add(arrow_between(plane, (0, 0), stretched, Palette.i_hat, stroke_width=4).set_opacity(0.6))
        for coords, color in ((CRAMER_A1, Palette.i_hat), (CRAMER_A2, Palette.j_hat), (CRAMER_B, Palette.yellow)):
            self.add(vector_arrow(coords, color, plane))
        for coords, tex, color, direction in (
            (CRAMER_A1, r"\mathbf a_1", Palette.i_hat, DOWN),
            (CRAMER_A2, r"\mathbf a_2", Palette.j_hat, LEFT),
            (CRAMER_B, r"\mathbf b", Palette.yellow, RIGHT),
            (stretched, r"2\mathbf a_1", Palette.i_hat, RIGHT),
        ):
            self.add(backed(MathTex(tex, color=color, font_size=40), padding=0.08).next_to(plane.c2p(*coords), direction, buff=0.12))
        areas = VGroup(
            MathTex(r"\det A = 5", color=Palette.i_hat, font_size=44),
            MathTex(r"\det A_1(\mathbf b) = 10 = 2 \cdot 5", color=Palette.yellow, font_size=44),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        self.add(backed(areas, padding=0.2).move_to([3.4, 1.6, 0]))


class FigVolume(Scene):
    def construct(self):
        view = OrbitingView((-0.8, -1.3), 1.15, azimuth=25.0, elevation=22.0)
        edges = box_edges(1.0, 1.0)
        self.add(floor_and_axes(view.project, ((-1, 4), (-1, 4), (-1, 3))))
        self.add(parallelepiped(view.project, *BOX, color=Palette.text_muted, opacity=0.0, stroke_width=1.5).set_stroke(opacity=0.45))
        self.add(parallelepiped(view.project, *edges, opacity=0.14))
        for edge, color in zip(edges, BOX_COLORS):
            self.add(projected_arrow(view.project, edge, color))
        mat = colored_matrix(BOX_STEPS[2], BOX_COLORS)
        panel = VGroup(named("A", mat), MathTex(r"\text{volume} = \lvert\det A\rvert = 12", color=Palette.teal, font_size=44)).arrange(DOWN, buff=0.4)
        self.add(panel.move_to([4.2, 0.8, 0]))
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = plane_at(PRODUCT_ORIGIN, PRODUCT_UNIT)
        plane.background_lines.set_stroke(opacity=0.25)
        plane.faded_lines.set_stroke(opacity=0.15)
        live = LiveTransform(AB_ROWS)
        tint = ValueTracker(1.0)
        self.add(plane, live.grid(plane, color=Palette.blue, opacity=0.55, cap=30))
        self.add(outline(plane, ((1, 0), (0, 1)), Palette.yellow).set_opacity(0.7), outline(plane, B_ROWS, Palette.yellow))
        self.add(live_polygon(plane, live, tint))
        self.add(vector_arrow((2, -1), Palette.i_hat, plane), vector_arrow((4, 1), Palette.j_hat, plane))
        formula = MathTex(r"\det(AB)", "=", r"\det A", r"\,\det B", color=Palette.text, font_size=62)
        numbers = MathTex("6", "=", "3", r"\cdot", "2", color=Palette.text, font_size=62)
        numbers[0].set_color(Palette.teal)
        self.add(backed(VGroup(formula, numbers).arrange(DOWN, buff=0.35), padding=0.3).move_to([3.2, 2.6, 0]))
