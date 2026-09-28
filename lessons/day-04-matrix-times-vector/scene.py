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
    column,
    fit_to_frame,
    make_plane,
    matrix,
    plane_at,
    plate_for,
    scrim,
    slider,
    spring,
    spring_soft,
    vector_arrow,
)

A1 = (3, 2)
A2 = (-1, 2)
X = (2, 1)
B = (7, 2)
A2_PARALLEL = (6, 4)
PLANE_ORIGIN = (-1.0, -2.4)
PLANE_UNIT = 0.75
COLUMN_COLORS = (Palette.yellow, Palette.blue)


def combo(x1, x2, a1=A1, a2=A2):
    return (x1 * a1[0] + x2 * a2[0], x1 * a1[1] + x2 * a2[1])


def matrix_a(a1=A1, a2=A2):
    mat = matrix([[a1[0], a2[0]], [a1[1], a2[1]]])
    for index, color in enumerate(COLUMN_COLORS):
        mat.get_columns()[index].set_color(color)
    return mat


def weights_column(entries, **kwargs):
    col = column(entries, **kwargs)
    for index, color in enumerate(COLUMN_COLORS):
        col.get_entries()[index].set_color(color)
    return col


def tex(*parts, colors=(), font_size=48):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def term_column(top, bottom):
    """A column whose entries are colored sums, one term per column of A."""
    rows = [tex(*top, colors=(Palette.yellow, None, Palette.blue)), tex(*bottom, colors=(Palette.yellow, None, Palette.blue))]
    mat = MobjectMatrix([[rows[0]], [rows[1]]], v_buff=0.9, bracket_h_buff=0.14)
    mat.get_brackets().set_color(Palette.text)
    return mat


def column_sum_equation():
    """2 a1 + 1 a2 written out entry by entry, then its answer."""
    total = combo(*X)
    wide = term_column((r"2\cdot 3", "+", r"1\cdot(-1)"), (r"2\cdot 2", "+", r"1\cdot 2"))
    return VGroup(
        tex("2", colors=(Palette.yellow,)),
        column(A1, color=Palette.yellow),
        tex("+"),
        tex("1", colors=(Palette.blue,)),
        column(A2, color=Palette.blue),
        tex("="),
        wide,
        tex("="),
        column(total, color=Palette.teal),
    ).arrange(RIGHT, buff=0.2)


def row_rule_equation():
    """A x computed one row at a time, each term colored by the column it came from."""
    total = combo(*X)
    wide = term_column((r"3\cdot 2", "+", r"(-1)\cdot 1"), (r"2\cdot 2", "+", r"2\cdot 1"))
    return VGroup(matrix_a(), weights_column(X), tex("="), wide, tex("="), column(total, color=Palette.teal)).arrange(RIGHT, buff=0.2)


def three_forms():
    y, b, t = Palette.yellow, Palette.blue, Palette.teal
    system = tex(r"3x_1", r"-\,x_2", "&=", "7", r"\\", r"2x_1", r"+\,2x_2", "&=", "2", colors=(y, b, None, t, None, y, b, None, t))
    vector_form = VGroup(
        tex("x_1", colors=(y,)), column(A1, color=y), tex("+"), tex("x_2", colors=(b,)), column(A2, color=b), tex("="), column(B, color=t)
    ).arrange(RIGHT, buff=0.18)
    unknowns = weights_column(("x_1", "x_2"))
    matrix_form = VGroup(matrix_a(), unknowns, tex("="), column(B, color=t)).arrange(RIGHT, buff=0.18)
    return VGroup(system, vector_form, matrix_form).arrange(DOWN, buff=0.5, aligned_edge=LEFT)


def form_labels(forms):
    names = ["system", "vector equation", "matrix equation"]
    labels = VGroup(*[Tex(name, color=Palette.text_muted, font_size=32) for name in names])
    for label, form in zip(labels, forms):
        label.next_to(form, LEFT, buff=0.5)
    right_edge = max(label.get_right()[0] for label in labels)
    for label in labels:
        label.shift(RIGHT * (right_edge - label.get_right()[0]))
    return labels


def augmented(rows, last_color=Palette.teal):
    mat = matrix(rows)
    columns = mat.get_columns()
    for index, color in enumerate((*COLUMN_COLORS, last_color)):
        columns[index].set_color(color)
    return mat


def row_reduction():
    start = augmented([[3, -1, 7], [2, 2, 2]])
    reduced = augmented([[1, 0, 2], [0, 1, -1]])
    answer = VGroup(tex(r"\mathbf x", "="), weights_column((2, -1))).arrange(RIGHT, buff=0.18)
    return VGroup(start, tex(r"\sim"), reduced), answer


def parallel_reduction():
    start = augmented([[3, 6, 7], [2, 4, 2]])
    reduced = augmented([[3, 6, 7], [0, 0, -8]])
    return VGroup(start, tex(r"\sim"), reduced).arrange(RIGHT, buff=0.25)


def augment_from(matrix_form, augmented_matrix):
    coefficients, right_side = matrix_form[0], matrix_form[3]
    columns = augmented_matrix.get_columns()
    return [
        TransformFromCopy(coefficients.get_columns()[0], columns[0]),
        TransformFromCopy(coefficients.get_columns()[1], columns[1]),
        TransformFromCopy(right_side.get_entries(), columns[2]),
        FadeIn(augmented_matrix.get_brackets()),
    ]


def name_label(parts, colors, anchor, direction):
    return backed(tex(*parts, colors=colors, font_size=40)).next_to(anchor, direction, buff=0.12)


def span_line(plane, direction):
    far = 20
    return Line(
        plane.c2p(-far * direction[0], -far * direction[1]),
        plane.c2p(far * direction[0], far * direction[1]),
        color=Palette.teal,
        stroke_width=3,
        stroke_opacity=0.55,
    )


def target_ring(plane, point):
    return Circle(radius=0.2, color=Palette.glow, stroke_width=4).move_to(plane.c2p(*point))


class Lesson(LessonScene):
    day = 4
    title = "Matrix times vector"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.columns_fly_out(plane)
        line = self.scale_and_add(plane, line)
        line = self.name_the_product(line)
        line = self.row_rule(line)
        line = self.solve_for_b(plane, line)
        line = self.three_forms(line)
        line = self.parallel_columns(plane, line)
        self.close_episode(
            r"$A\mathbf x$ is a linear combination of the columns of $A$,\\"
            r"and the entries of $\mathbf x$ are the weights.",
            *self.mobjects,
        )

    def columns_fly_out(self, plane):
        self.a_mat = matrix_a()
        self.x_col = weights_column(X)
        self.product = VGroup(self.a_mat, self.x_col).arrange(RIGHT, buff=0.15).to_corner(UL, buff=0.6)
        self.plate = plate_for(self.product)
        line = self.say(r"Here is a matrix $A$ and a vector $\mathbf x$.", hold=0.2)
        self.play(FadeIn(self.plate), Write(self.product), run_time=1.4)
        self.wait(Timing.read_short)

        line = self.say(r"Read $A$ as two columns, each one a vector.", line, hold=0.2)
        self.a1 = vector_arrow(A1, Palette.yellow, plane)
        self.a2 = vector_arrow(A2, Palette.blue, plane)
        self.a1_name = name_label([r"\mathbf a_1"], [Palette.yellow], plane.c2p(*A1), DR)
        self.a2_name = name_label([r"\mathbf a_2"], [Palette.blue], plane.c2p(*A2), LEFT)
        for col, arrow, name in zip(self.a_mat.get_columns(), (self.a1, self.a2), (self.a1_name, self.a2_name)):
            self.play(Indicate(col, color=Palette.glow, scale_factor=1.12), run_time=0.8)
            self.play(GrowArrow(arrow), TransformFromCopy(col, name), run_time=1.3, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return line

    def scale_and_add(self, plane, line):
        line = self.say(r"The entries of $\mathbf x$ are weights, one for each column.", line, hold=0.2)
        stretched = vector_arrow((2 * A1[0], 2 * A1[1]), Palette.yellow, plane)
        scaled_name = name_label(["2", r"\mathbf a_1"], [Palette.yellow, Palette.yellow], plane.c2p(*A1), DR)
        self.play(Indicate(self.x_col.get_entries()[0], color=Palette.glow, scale_factor=1.3), run_time=0.8)
        self.play(
            Transform(self.a1, stretched),
            ReplacementTransform(self.a1_name, scaled_name),
            run_time=1.4,
            rate_func=spring,
        )
        self.a1_name = scaled_name
        one_name = name_label(["1", r"\mathbf a_2"], [Palette.blue, Palette.blue], plane.c2p(*A2), LEFT)
        self.play(Indicate(self.x_col.get_entries()[1], color=Palette.glow, scale_factor=1.3), run_time=0.8)
        self.play(ReplacementTransform(self.a2_name, one_name), run_time=0.8, rate_func=spring)
        self.a2_name = one_name
        self.wait(Timing.read_short)

        line = self.say(r"Scale each column, then add them tip to tail.", line, hold=0.2)
        self.moved_a2 = arrow_between(plane, (2 * A1[0], 2 * A1[1]), combo(*X), Palette.blue)
        slide_copy = self.a2.copy()
        self.play(ReplacementTransform(slide_copy, self.moved_a2), run_time=1.6, rate_func=spring)
        self.result = vector_arrow(combo(*X), Palette.teal, plane, stroke_width=7)
        self.stamp = Dot(plane.c2p(*combo(*X)), radius=0.09, color=Palette.glow)
        self.result_name = name_label([r"A\mathbf x"], [Palette.teal], plane.c2p(*combo(*X)), UR)
        self.play(GrowArrow(self.result), run_time=1.3, rate_func=spring_soft)
        self.play(GrowFromCenter(self.stamp), FadeIn(self.result_name), run_time=0.5, rate_func=spring)
        self.wait(Timing.read_short)
        return line

    def name_the_product(self, line):
        extension = VGroup(
            tex("=", "2", r"\mathbf a_1", "+", "1", r"\mathbf a_2", "=", colors=(None, Palette.yellow, Palette.yellow, None, Palette.blue, Palette.blue)),
            column(combo(*X), color=Palette.teal),
        ).arrange(RIGHT, buff=0.2)
        extension.next_to(self.product, RIGHT, buff=0.2)
        line = self.say(r"So $A\mathbf x$ is a combination of the columns of $A$.", line, hold=0.2)
        self.play(self.plate.animate.become(plate_for(VGroup(self.product, extension))), run_time=0.6, rate_func=spring_soft)
        self.play(
            FadeIn(extension[0][0]),
            TransformFromCopy(VGroup(*self.a1_name[1:3]), extension[0][1:3]),
            FadeIn(extension[0][3]),
            TransformFromCopy(VGroup(*self.a2_name[1:3]), extension[0][4:6]),
            FadeIn(extension[0][6]),
            run_time=1.4,
        )
        self.play(TransformFromCopy(self.result_name[1], extension[1]), run_time=1.0)
        self.wait(Timing.read_long)

        general = MathTex(
            r"A\mathbf x &= \begin{bmatrix}\mathbf a_1 & \cdots & \mathbf a_n\end{bmatrix}\begin{bmatrix}x_1\\ \vdots\\ x_n\end{bmatrix}\\",
            r"&= x_1\mathbf a_1 + \cdots + x_n\mathbf a_n",
            color=Palette.text, font_size=44,
        ).to_corner(UL, buff=0.6)
        self.general = general
        line = self.say(r"$\mathbf x$ needs exactly one entry for each column of $A$.", line, hold=0.2)
        self.play(
            FadeOut(VGroup(self.product, extension), shift=UP * 0.2),
            self.plate.animate.become(plate_for(general)),
            run_time=0.6,
        )
        self.play(FadeIn(general, shift=UP * 0.2), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_long)
        return line

    def row_rule(self, line):
        veil = scrim()
        by_columns = column_sum_equation()
        by_rows = row_rule_equation()
        VGroup(by_columns, by_rows).arrange(DOWN, buff=0.7).move_to(UP * 0.55)
        line = self.say(r"Write the sum out entry by entry.", line, hold=0.2)
        self.play(FadeIn(veil), FadeOut(self.general), FadeOut(self.plate), run_time=0.7)
        self.play(Write(by_columns), run_time=2.0)
        self.wait(Timing.read_short)

        line = self.say(r"Each entry uses one row of $A$ and all of $\mathbf x$.", line, hold=0.2)
        wide = by_rows[3]
        self.play(FadeIn(VGroup(by_rows[0], by_rows[1], by_rows[2], wide.get_brackets())), run_time=0.8)
        for row in range(2):
            self.highlight_row(by_columns, by_rows, row)
        self.play(FadeIn(by_rows[4]), FadeIn(by_rows[5]), run_time=0.7)
        self.wait(Timing.beat)

        line = self.say(r"That shortcut is the row rule, and it agrees.", line, hold=0.2)
        self.play(Indicate(by_columns[-1], color=Palette.teal), Indicate(by_rows[-1], color=Palette.teal), run_time=1.0)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(by_columns, by_rows)), FadeOut(veil), run_time=0.7)
        return line

    def highlight_row(self, by_columns, by_rows, row):
        marks = VGroup(
            SurroundingRectangle(by_rows[0].get_rows()[row], color=Palette.glow, buff=0.1),
            SurroundingRectangle(by_rows[1], color=Palette.glow, buff=0.08),
            SurroundingRectangle(by_columns[6].get_entries()[row], color=Palette.glow, buff=0.08),
        )
        self.play(Create(marks), run_time=0.7)
        self.play(FadeIn(by_rows[3].get_entries()[row], shift=LEFT * 0.2), run_time=0.8, rate_func=spring)
        self.wait(Timing.read_short)
        self.play(FadeOut(marks), run_time=0.4)

    def solve_for_b(self, plane, line):
        self.x1 = ValueTracker(X[0])
        self.x2 = ValueTracker(X[1])
        self.a2_tip = [ValueTracker(A2[0]), ValueTracker(A2[1])]
        self.swap_to_live_arrows(plane)
        ring = target_ring(plane, B)
        b_name = name_label([r"\mathbf b"], [Palette.teal], plane.c2p(*B), RIGHT).shift(RIGHT * 0.15)
        self.target = VGroup(ring, b_name)
        self.controls = VGroup(slider(r"x_1", self.x1, Palette.yellow), slider(r"x_2", self.x2, Palette.blue)).arrange(DOWN, buff=0.35, aligned_edge=RIGHT)
        self.controls.to_corner(UL, buff=0.6)
        self.plate = plate_for(self.controls)

        line = self.say(r"Now flip the question: which $\mathbf x$ lands on $\mathbf b$?", line, hold=0.2)
        self.play(FadeIn(self.plate), FadeIn(self.controls), GrowFromCenter(ring), FadeIn(b_name), run_time=1.0)
        self.wait(Timing.beat)
        for x1, x2 in [(3, -1), (1, -1), (2, -1)]:
            self.play(self.x1.animate.set_value(x1), self.x2.animate.set_value(x2), run_time=1.6, rate_func=spring)
            self.wait(0.5)
        self.play(Flash(plane.c2p(*B), color=Palette.glow, line_length=0.25), run_time=0.8)
        line = self.say(r"Solving $A\mathbf x = \mathbf b$ asks whether $\mathbf b$ is in the span.", line, hold=Timing.read_short)
        return line

    def swap_to_live_arrows(self, plane):
        live_a1 = always_redraw(lambda: vector_arrow(self.scaled_a1(), Palette.yellow, plane))
        live_a2 = always_redraw(lambda: arrow_between(plane, self.scaled_a1(), self.live_result(), Palette.blue))
        live_result = always_redraw(lambda: vector_arrow(self.live_result(), Palette.teal, plane, stroke_width=7))
        base_a2 = always_redraw(lambda: vector_arrow(self.a2_value(), Palette.blue, plane).set_opacity(0.3))
        self.remove(self.a1, self.moved_a2, self.result, self.a2)
        self.add(base_a2, live_a1, live_a2, live_result)
        self.play(FadeOut(VGroup(self.a1_name, self.a2_name, self.result_name, self.stamp)), run_time=0.6)
        self.live = VGroup(base_a2, live_a1, live_a2, live_result)

    def a2_value(self):
        return (self.a2_tip[0].get_value(), self.a2_tip[1].get_value())

    def scaled_a1(self):
        x1 = self.x1.get_value()
        return (x1 * A1[0], x1 * A1[1])

    def live_result(self):
        return combo(self.x1.get_value(), self.x2.get_value(), A1, self.a2_value())

    def three_forms(self, line):
        veil = scrim()
        forms = three_forms()
        labels = form_labels(forms)
        reduction, answer = row_reduction()
        reduction.arrange(RIGHT, buff=0.25)
        left = VGroup(labels, forms)
        right = VGroup(reduction, answer).arrange(DOWN, buff=0.6)
        stage = VGroup(left, right).arrange(RIGHT, buff=1.0)
        stage.scale(min(1.0, (config.frame_width - 1.2) / stage.width, 5.6 / stage.height)).move_to(UP * 0.5)
        line = self.say(r"Here is the same problem written three ways.", line, hold=0.2)
        self.play(FadeIn(veil), FadeOut(self.plate), FadeOut(self.controls), run_time=0.7)
        self.play(FadeIn(labels[0]), Write(forms[0]), run_time=1.4)
        for index in (1, 2):
            self.play(FadeIn(labels[index]), TransformFromCopy(forms[index - 1], forms[index]), run_time=1.4)
            self.wait(Timing.beat)
        self.wait(Timing.beat)

        line = self.say(r"One augmented matrix solves all three.", line, hold=0.2)
        self.play(*augment_from(forms[2], reduction[0]), run_time=1.4)
        self.wait(Timing.beat)
        line = self.say(r"Row reduction confirms the weights $2$ and $-1$.", line, hold=0.2)
        self.play(FadeIn(reduction[1]), FadeIn(reduction[2], shift=LEFT * 0.3), run_time=1.0, rate_func=spring)
        self.play(TransformFromCopy(reduction[2].get_columns()[2], answer), run_time=1.2)
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(labels, forms, reduction, answer)), FadeOut(veil), run_time=0.7)
        return line

    def parallel_columns(self, plane, line):
        line = self.say(r"Parallel columns only span a line.", line, hold=0.2)
        panel = VGroup(tex("A", "="), matrix_a(A1, A2_PARALLEL)).arrange(RIGHT, buff=0.2).to_corner(UL, buff=0.6)
        self.plate = plate_for(panel)
        self.play(FadeIn(self.plate), FadeIn(panel), run_time=0.8)
        self.play(*[tip.animate.set_value(value) for tip, value in zip(self.a2_tip, A2_PARALLEL)], self.x2.animate.set_value(0.5), run_time=1.8, rate_func=spring)
        span = span_line(plane, A1)
        self.play(Create(span), run_time=1.4)
        self.bring_to_front(self.live, self.target)
        self.wait(Timing.beat)

        line = self.say(r"Now $\mathbf b$ is off the line, so no $\mathbf x$ works.", line, hold=0.2)
        for x1, x2 in [(1.0, 0.25), (0.5, 0.75), (1.0, 0.0)]:
            self.play(self.x1.animate.set_value(x1), self.x2.animate.set_value(x2), run_time=1.4, rate_func=spring)
        self.play(Indicate(VGroup(self.target[0], self.target[1][1]), color=Palette.j_hat), run_time=1.0)

        reduction = parallel_reduction().to_corner(UL, buff=0.6)
        last_row = SurroundingRectangle(reduction[2].get_rows()[1], color=Palette.glow, buff=0.1)
        line = self.say(r"Row reduction agrees: the last row says $0 = -8$.", line, hold=0.2)
        self.play(FadeOut(panel), self.plate.animate.become(plate_for(reduction)), run_time=0.6)
        self.play(FadeIn(reduction[0]), run_time=0.8)
        self.play(FadeIn(reduction[1]), FadeIn(reduction[2], shift=LEFT * 0.3), run_time=1.0, rate_func=spring)
        self.play(Create(last_row), run_time=0.7)
        self.wait(Timing.read_long)
        return line


def column_picture(plane):
    total = combo(*X)
    arrows = VGroup(
        vector_arrow((2 * A1[0], 2 * A1[1]), Palette.yellow, plane),
        vector_arrow(A2, Palette.blue, plane),
        arrow_between(plane, (2 * A1[0], 2 * A1[1]), total, Palette.blue),
        vector_arrow(total, Palette.teal, plane, stroke_width=7),
    )
    labels = VGroup(
        name_label(["2", r"\mathbf a_1"], [Palette.yellow, Palette.yellow], plane.c2p(*A1), DR),
        name_label([r"\mathbf a_2"], [Palette.blue], plane.c2p(*A2), LEFT),
        name_label([r"A\mathbf x"], [Palette.teal], plane.c2p(*total), UR),
    )
    return arrows, labels, Dot(plane.c2p(*total), radius=0.09, color=Palette.glow)


def product_panel(font_size=48):
    equation = VGroup(
        matrix_a(),
        weights_column(X),
        tex("=", "2", r"\mathbf a_1", "+", "1", r"\mathbf a_2", "=", colors=(None, Palette.yellow, Palette.yellow, None, Palette.blue, Palette.blue), font_size=font_size),
        column(combo(*X), color=Palette.teal),
    ).arrange(RIGHT, buff=0.18)
    return backed(equation, padding=0.25)


class FigColumnPicture(Scene):
    def construct(self):
        plane = make_plane(x_range=(-3, 8, 1), y_range=(-1, 7, 1))
        arrows, labels, stamp = column_picture(plane)
        self.add(plane, arrows, labels, stamp)
        fit_to_frame(self)


class FigRowRule(Scene):
    def construct(self):
        by_columns = column_sum_equation()
        by_rows = row_rule_equation()
        VGroup(by_columns, by_rows).arrange(DOWN, buff=0.8)
        marks = VGroup(
            SurroundingRectangle(by_rows[0].get_rows()[0], color=Palette.glow, buff=0.1),
            SurroundingRectangle(by_rows[1], color=Palette.glow, buff=0.08),
            SurroundingRectangle(by_rows[3].get_entries()[0], color=Palette.glow, buff=0.08),
        )
        self.add(by_columns, by_rows, marks)
        fit_to_frame(self, margin=0.8)


class FigThreeForms(Scene):
    def construct(self):
        forms = three_forms()
        labels = form_labels(forms)
        reduction, answer = row_reduction()
        reduction.arrange(RIGHT, buff=0.25)
        right = VGroup(reduction, answer).arrange(DOWN, buff=0.6)
        self.add(VGroup(VGroup(labels, forms), right).arrange(RIGHT, buff=1.0))
        fit_to_frame(self, margin=0.6)


class FigParallelColumns(Scene):
    def construct(self):
        plane = make_plane(x_range=(-2, 9, 1), y_range=(-2, 6, 1))
        arrows = VGroup(
            vector_arrow(A2_PARALLEL, Palette.blue, plane),
            vector_arrow(A1, Palette.yellow, plane),
        )
        labels = VGroup(
            name_label([r"\mathbf a_1"], [Palette.yellow], plane.c2p(*A1), DR),
            name_label([r"\mathbf a_2"], [Palette.blue], plane.c2p(*A2_PARALLEL), RIGHT),
            name_label([r"\mathbf b"], [Palette.teal], plane.c2p(*B), RIGHT).shift(RIGHT * 0.15),
        )
        line = span_line(plane, A1)
        line.put_start_and_end_on(plane.c2p(-2, -4 / 3), plane.c2p(9, 6))
        self.add(plane, line, arrows, target_ring(plane, B), labels)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        arrows, labels, stamp = column_picture(plane)
        panel = product_panel().to_corner(UL, buff=0.6)
        self.add(plane, arrows, labels, stamp, panel)
