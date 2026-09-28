import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    Palette,
    Timing,
    backed,
    column,
    fit_to_frame,
    matrix,
    morph_matrix,
    plane_at,
    plate_for,
    scrim,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (0.9, -0.25)
PLANE_UNIT = 0.85
LATTICE = [(x, y) for x in range(-9, 8) for y in range(-3, 5)]
NULL_DIRECTION = np.array([1.0, -1.0])
NULL_ENDS = ((-4.6, 4.6), (3.2, -3.2))
COL_ENDS = ((-3.2, -3.2), (4.5, 4.5))
B_POINT = (2.0, 2.0)
P_POINT = (4.0, 0.0)
SOLUTION_REACH = (-4.5, 3.0)
TEST_POINT = (2.0, 1.0)
PANEL_Z = 10
PROOF_Z = 50

A_ROWS = [[1, -2, 0, 3], [2, -4, 1, 4]]
A_REDUCED = [[1, -2, 0, 3], [0, 0, 1, -2]]
FREE_COLORS = {1: Palette.yellow, 3: Palette.blue}
U_ENTRIES = [2, 1, 0, 0]
V_ENTRIES = [-3, 0, 2, 1]

CHECKS = (
    (r"(a)", r"A\mathbf 0 = \mathbf 0"),
    (r"(b)", r"A(\mathbf u + \mathbf v) = A\mathbf u + A\mathbf v = \mathbf 0 + \mathbf 0 = \mathbf 0"),
    (r"(c)", r"A(c\,\mathbf u) = c\,A\mathbf u = c\,\mathbf 0 = \mathbf 0"),
)


def project(point):
    """Where P sends a point: halfway to the diagonal along (1, -1)."""
    middle = (point[0] + point[1]) / 2
    return np.array([middle, middle])


def slid(point, s):
    point = np.array(point, dtype=float)
    return (1 - s) * point + s * project(point)


def on_null_line(point):
    return point[0] + point[1] == 0


def on_solution_line(point):
    return point[0] + point[1] == 4


def tex_parts(*parts, colors=(), font_size=40):
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def p_definition():
    return tex_parts("P", "=", r"\tfrac12", r"\begin{bmatrix} 1 & 1 \\ 1 & 1 \end{bmatrix}", font_size=42)


def null_definition():
    return tex_parts(r"\operatorname{Nul}P", "=", r"\{\mathbf x : P\mathbf x = \mathbf 0\}", colors=(Palette.pink,))


def product_line(entries, image, input_color):
    return tex_parts(
        "P",
        rf"\begin{{bmatrix}} {entries[0]} \\ {entries[1]} \end{{bmatrix}}",
        "=",
        rf"\begin{{bmatrix}} {image[0]} \\ {image[1]} \end{{bmatrix}}",
        colors=(None, input_color, None, Palette.teal),
    )


def shifted_rule():
    return tex_parts(
        r"\{\mathbf x : P\mathbf x = \mathbf b\}",
        "=",
        r"\mathbf p",
        "+",
        r"\operatorname{Nul}P",
        colors=(None, None, Palette.yellow, None, Palette.pink),
    )


def lattice_dot(plane, point, tracker):
    dot = Dot(plane.c2p(*point), radius=0.055, color=Palette.purple_gray)
    dot.add_updater(lambda m: m.move_to(plane.c2p(*slid(point, tracker.get_value()))))
    return dot


def plane_line(plane, ends, color, stroke_width=5):
    start, end = plane.c2p(*ends[0]), plane.c2p(*ends[1])
    if np.linalg.norm(end - start) < 1e-3:
        end = start + np.array([1e-3, 0, 0])
    return Line(start, end, color=color, stroke_width=stroke_width)


def solution_ends(t_range=SOLUTION_REACH):
    return tuple(np.array(P_POINT) + t * NULL_DIRECTION for t in t_range)


def tag(tex, color, anchor, direction, font_size=38, buff=0.14):
    return backed(MathTex(tex, color=color, font_size=font_size), padding=0.08).next_to(anchor, direction, buff=buff)


def ring(point, color=Palette.glow, radius=0.22):
    return Circle(radius=radius, color=color, stroke_width=4).move_to(point)


def tick_mark(color=Palette.teal):
    mark = VMobject(color=color, stroke_width=6)
    mark.set_points_as_corners([LEFT * 0.16 + UP * 0.02, DOWN * 0.14 + LEFT * 0.02, RIGHT * 0.2 + UP * 0.2])
    return mark


def proof_rows():
    given = tex_parts(r"\text{Suppose } A\mathbf u = \mathbf 0 \text{ and } A\mathbf v = \mathbf 0.", font_size=40)
    given.set_color(Palette.text_muted)
    rows = VGroup()
    for letter, statement in CHECKS:
        label = Tex(letter, color=Palette.text_muted, font_size=38)
        body = MathTex(statement, color=Palette.text, font_size=44)
        rows.add(VGroup(label, body).arrange(RIGHT, buff=0.3))
    rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
    return VGroup(given, rows).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to(UP * 0.35)


def free_matrix(rows):
    mat = matrix([[str(entry) for entry in row] for row in rows])
    for index, color in FREE_COLORS.items():
        mat.get_columns()[index].set_color(color)
    return mat


def solved_equations():
    first = tex_parts("x_1", "=", "2", "x_2", "-", "3", "x_4", colors=(None, None, None, Palette.yellow, None, None, Palette.blue), font_size=50)
    second = tex_parts("x_3", "=", "2", "x_4", colors=(None, None, None, Palette.blue), font_size=50)
    VGroup(first, second).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
    second.shift((first[1].get_center()[0] - second[1].get_center()[0]) * RIGHT)
    return VGroup(first, second)


def parametric_row():
    """x = [x1..x4] = [general] = x2 u + x4 v, with each piece kept addressable."""
    variables = column(["x_1", "x_2", "x_3", "x_4"])
    general = column([r"2x_2 - 3x_4", "x_2", "2x_4", "x_4"])
    u_col = column(U_ENTRIES, color=Palette.yellow)
    v_col = column(V_ENTRIES, color=Palette.blue)
    row = VGroup(
        MathTex(r"\mathbf x", "=", color=Palette.text),
        variables,
        MathTex("=", color=Palette.text),
        general,
        MathTex("=", color=Palette.text),
        MathTex("x_2", color=Palette.yellow),
        u_col,
        MathTex("+", color=Palette.text),
        MathTex("x_4", color=Palette.blue),
        v_col,
    ).arrange(RIGHT, buff=0.22)
    row.scale(1.08)
    names = VGroup(
        MathTex(r"\mathbf u", color=Palette.yellow, font_size=40).next_to(u_col, DOWN, buff=0.2),
        MathTex(r"\mathbf v", color=Palette.blue, font_size=40).next_to(v_col, DOWN, buff=0.2),
    )
    return row, names


def identity_frames(row, rows=(1, 3)):
    u_col, v_col = row[6], row[9]
    return VGroup(
        *[
            SurroundingRectangle(col.get_entries()[index], color=Palette.glow, buff=0.08, stroke_width=3)
            for col in (u_col, v_col)
            for index in rows
        ]
    )


class Lesson(LessonScene):
    day = 17
    title = "Null space"

    def construct(self):
        self.plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        pulse = self.open_episode(self.plane)
        self.play(FadeOut(pulse), run_time=0.5)
        self.s = ValueTracker(0.0)
        self.panel_lines = []
        self.panel_plate = None
        line = self.meet_p()
        line = self.project_everything(line)
        line = self.collapse_null_line(line)
        line = self.name_null_space(line)
        line = self.membership(line)
        line = self.subspace_proof(line)
        line = self.land_on_b(line)
        line = self.shifted_copy(line)
        line = self.reduce_a(line)
        line = self.split_by_free(line)
        line = self.independence(line)
        self.close_episode(
            r"The null space holds every input that $A$ sends to $\mathbf 0$.\\"
            r"The solutions of $A\mathbf x = \mathbf b$ form the shifted copy $\mathbf p + \operatorname{Nul}A$.",
            *self.mobjects,
        )

    def at(self, point):
        return self.plane.c2p(*point)

    def panel_layout(self, lines):
        return VGroup(*lines).arrange(DOWN, buff=0.35, aligned_edge=LEFT).to_corner(UL, buff=0.55)

    def panel_add(self, new_line, run_time=0.8):
        """Append a line to the top-left panel, growing its plate to fit."""
        self.panel_layout([*[old.copy() for old in self.panel_lines], new_line])
        self.panel_lines.append(new_line)
        new_line.set_z_index(PANEL_Z + 1)
        plate = plate_for(VGroup(*self.panel_lines)).set_z_index(PANEL_Z)
        if self.panel_plate is None:
            self.panel_plate = plate
            self.play(FadeIn(plate), Write(new_line), run_time=run_time)
            return
        self.play(self.panel_plate.animate.become(plate), FadeIn(new_line, shift=DOWN * 0.1), run_time=run_time, rate_func=spring_soft)

    def panel_swap_last(self, new_line, run_time=0.8):
        old = self.panel_lines.pop()
        self.play(FadeOut(old), run_time=0.35)
        self.panel_add(new_line, run_time=run_time)

    def meet_p(self):
        plane = self.plane
        self.dots = {point: lattice_dot(plane, point, self.s) for point in LATTICE}
        ordered = sorted(self.dots.items(), key=lambda item: item[0][0] ** 2 + item[0][1] ** 2)
        line = self.say(r"Yesterday we collected every output of a matrix.", hold=Timing.read_short)
        line = self.say(r"Today we ask which inputs land on $\mathbf 0$.", line, hold=0.2)
        self.panel_add(p_definition(), run_time=1.2)
        self.play(LaggedStart(*[GrowFromCenter(dot) for _, dot in ordered], lag_ratio=0.012), run_time=2.0)
        self.wait(Timing.beat)
        return line

    def project_everything(self, line):
        line = self.say(r"This $P$ projects the plane onto the diagonal.", line, hold=0.2)
        self.play(self.s.animate.set_value(1.0), run_time=2.6, rate_func=spring_soft)
        self.col_line = plane_line(self.plane, COL_ENDS, Palette.teal, stroke_width=4)
        self.col_tag = tag(r"\operatorname{Col}P", Palette.teal, self.at((3.6, 3.6)), RIGHT)
        self.bring_to_back(self.col_line)
        self.bring_to_back(self.plane)
        self.play(Create(self.col_line), FadeIn(self.col_tag), run_time=1.2)
        self.wait(Timing.read_short)
        return line

    def collapse_null_line(self, line):
        self.play(self.s.animate.set_value(0.0), run_time=1.6, rate_func=smooth)
        self.null_dots = VGroup(*[dot for point, dot in self.dots.items() if on_null_line(point)])
        self.null_line = always_redraw(
            lambda: plane_line(self.plane, [slid(end, self.s.get_value()) for end in NULL_ENDS], Palette.pink, stroke_width=5)
        )
        line = self.say(r"Now follow the dots on this pink line.", line, hold=0.2)
        self.play(self.null_dots.animate.set_color(Palette.pink).scale(1.5), run_time=0.8)
        self.add(self.null_line)
        self.bring_to_front(*self.null_dots)
        self.play(Create(self.null_line), run_time=1.2)
        self.wait(Timing.beat)

        line = self.say(r"The whole pink line collapses onto the origin.", line, hold=0.2)
        self.play(self.s.animate.set_value(1.0), run_time=3.0, rate_func=spring_soft)
        halo = Dot(self.at((0, 0)), radius=0.3, color=Palette.glow, fill_opacity=0.25)
        landing = ring(self.at((0, 0)))
        self.sfx("chime", gain=-6)
        self.play(Flash(self.at((0, 0)), color=Palette.glow, line_length=0.3, num_lines=12), GrowFromCenter(halo), Create(landing), run_time=0.9)
        self.wait(Timing.read_short)
        self.play(FadeOut(halo), FadeOut(landing), self.s.animate.set_value(0.0), run_time=1.8, rate_func=smooth)
        return line

    def name_null_space(self, line):
        others = VGroup(*[dot for point, dot in self.dots.items() if not on_null_line(point)])
        self.null_tag = tag(r"\operatorname{Nul}P", Palette.pink, self.at((-2.6, 2.6)), RIGHT, buff=0.25)
        line = self.say(r"That line is the \emph{null space} of $P$.", line, hold=0.2)
        self.play(others.animate.set_opacity(0.3), FadeIn(self.null_tag, shift=LEFT * 0.1), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"It holds every input that $P$ sends to $\mathbf 0$.", line, hold=0.2)
        self.panel_add(null_definition())
        self.wait(Timing.read_short)
        self.others = others
        return line

    def membership(self, line):
        null_arrow = vector_arrow((1, -1), Palette.pink, self.plane, stroke_width=6)
        line = self.say(r"To test one vector, just multiply by $P$.", line, hold=0.2)
        self.play(GrowArrow(null_arrow), run_time=0.9, rate_func=spring_soft)
        self.panel_add(product_line((1, -1), (0, 0), Palette.pink))
        self.wait(Timing.read_short)

        test_arrow = vector_arrow(TEST_POINT, Palette.yellow, self.plane, stroke_width=6)
        image_arrow = vector_arrow(project(TEST_POINT), Palette.teal, self.plane, stroke_width=6)
        line = self.say(r"$(2, 1)$ lands at $(1.5, 1.5)$, so it is not in $\operatorname{Nul}P$.", line, hold=0.2)
        self.play(GrowArrow(test_arrow), run_time=0.9, rate_func=spring_soft)
        self.panel_swap_last(product_line((2, 1), (1.5, 1.5), Palette.yellow))
        self.play(TransformFromCopy(test_arrow, image_arrow), run_time=1.2, rate_func=spring)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(null_arrow, test_arrow, image_arrow)), run_time=0.5)
        return line

    def subspace_proof(self, line):
        veil = scrim(0.95).set_z_index(PROOF_Z)
        proof = proof_rows().set_z_index(PROOF_Z + 1)
        given, rows = proof
        line = self.say(r"The null space of any matrix is a subspace.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(FadeIn(given, shift=DOWN * 0.1), run_time=0.7)
        captions = (
            r"It contains $\mathbf 0$, because $A\mathbf 0 = \mathbf 0$.",
            r"Sums stay in, because $A(\mathbf u + \mathbf v) = A\mathbf u + A\mathbf v$.",
            r"Multiples stay in, because $A(c\,\mathbf u) = c\,A\mathbf u$.",
        )
        marks = VGroup()
        for row, text in zip(rows, captions):
            line = self.say(text, line, hold=0.2)
            self.play(Write(row), run_time=1.3)
            mark = tick_mark().next_to(rows, RIGHT, buff=0.5).set_y(row.get_center()[1]).set_z_index(PROOF_Z + 1)
            self.sfx("pop", gain=-6)
            self.play(Create(mark), run_time=0.4)
            marks.add(mark)
            self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(veil, proof, marks)), run_time=0.7)
        return line

    def land_on_b(self, line):
        self.b_ring = ring(self.at(B_POINT))
        self.b_tag = tag(r"\mathbf b", Palette.teal, self.at(B_POINT), RIGHT, buff=0.3)
        self.solution_dots = VGroup(*[dot for point, dot in self.dots.items() if on_solution_line(point)])
        self.solution_line = always_redraw(
            lambda: plane_line(self.plane, [slid(end, self.s.get_value()) for end in solution_ends()], Palette.yellow, stroke_width=5)
        )
        line = self.say(r"Now ask which inputs land on $\mathbf b = (2, 2)$.", line, hold=0.2)
        self.play(Create(self.b_ring), FadeIn(self.b_tag), run_time=0.7)
        self.play(self.solution_dots.animate.set_color(Palette.yellow).set_opacity(1).scale(1.5), run_time=0.8)
        self.add(self.solution_line)
        self.bring_to_front(*self.solution_dots, self.b_ring, self.b_tag)
        self.play(Create(self.solution_line), run_time=1.2)
        line = self.say(r"Every yellow dot lands on $\mathbf b$.", line, hold=0.2)
        self.play(self.s.animate.set_value(1.0), run_time=2.6, rate_func=spring_soft)
        self.play(Flash(self.at(B_POINT), color=Palette.glow, line_length=0.3, num_lines=12), run_time=0.8)
        self.wait(Timing.beat)
        self.play(self.s.animate.set_value(0.0), run_time=1.6, rate_func=smooth)
        return line

    def shifted_copy(self, line):
        p_arrow = vector_arrow(P_POINT, Palette.yellow, self.plane, stroke_width=6)
        p_tag = tag(r"\mathbf p", Palette.yellow, self.at(P_POINT), UR, buff=0.12)
        copy = plane_line(self.plane, NULL_ENDS, Palette.pink, stroke_width=5)
        line = self.say(r"The solutions are the null space, shifted by $\mathbf p$.", line, hold=0.2)
        self.play(GrowArrow(p_arrow), FadeIn(p_tag), run_time=1.0, rate_func=spring_soft)
        self.play(copy.animate.shift(self.at(P_POINT) - self.at((0, 0))), run_time=1.8, rate_func=spring_soft)
        self.play(FadeOut(copy), run_time=0.5)

        t = ValueTracker(0.0)
        rider = always_redraw(lambda: Dot(self.at(np.array(P_POINT) + t.get_value() * NULL_DIRECTION), radius=0.12, color=Palette.yellow))
        step = always_redraw(
            lambda: DashedLine(self.at(P_POINT), self.at(np.array(P_POINT) + t.get_value() * NULL_DIRECTION), color=Palette.pink, stroke_width=7, dash_length=0.12)
        )
        line = self.say(r"Each solution is $\mathbf p$ plus a vector in $\operatorname{Nul}P$.", line, hold=0.2)
        self.add(step, rider)
        self.panel_swap_last(shifted_rule())
        for value in (-1.0, 2.0, -3.0):
            self.play(t.animate.set_value(value), run_time=1.3, rate_func=spring)
        self.wait(Timing.beat)

        miss = ring(self.at((0, 0)))
        line = self.say(r"The shifted line misses $\mathbf 0$, so it is not a subspace.", line, hold=0.2)
        self.play(Create(miss), run_time=0.6)
        self.wait(Timing.read_short)
        return line

    def reduce_a(self, line):
        leaving = [mobject for mobject in self.mobjects if mobject is not line]
        line = self.say(r"Bigger matrices need row reduction to find $\operatorname{Nul}A$.", line, hold=0.2)
        self.play(*[FadeOut(mobject) for mobject in leaving], run_time=0.9)
        self.remove(*leaving)
        self.a_matrix = free_matrix(A_ROWS)
        self.a_group = VGroup(MathTex("A", "=", color=Palette.text), self.a_matrix).arrange(RIGHT, buff=0.2).scale(1.2).move_to(np.array([-3.4, 2.3, 0]))
        self.play(Write(self.a_group), run_time=1.2)
        self.wait(Timing.beat)

        operation = MathTex(r"R_2 \leftarrow R_2 - 2R_1", color=Palette.text_muted, font_size=34).next_to(self.a_group, DOWN, buff=0.3)
        line = self.say(r"Row reduce $A$. The zero column of $[A\ \mathbf 0]$ never changes.", line, hold=0.2)
        self.play(FadeIn(operation, shift=LEFT * 0.1), run_time=0.4)
        morph_matrix(self, self.a_matrix, free_matrix(A_REDUCED).scale(1.2).move_to(self.a_matrix), run_time=1.2)
        self.wait(Timing.beat)
        self.play(FadeOut(operation), run_time=0.3)

        columns = self.a_matrix.get_columns()
        frames = VGroup(*[SurroundingRectangle(columns[i], color=Palette.glow, buff=0.1, stroke_width=3) for i in (0, 2)])
        free_tags = VGroup(*[MathTex(f"x_{i + 1}", color=color, font_size=36).next_to(columns[i], DOWN, buff=0.3) for i, color in FREE_COLORS.items()])
        line = self.say(r"Columns 2 and 4 have no pivot, so $x_2$ and $x_4$ are free.", line, hold=0.2)
        self.play(Create(frames), run_time=0.8)
        self.play(FadeIn(free_tags, shift=UP * 0.1), run_time=0.7)
        self.wait(Timing.read_short)

        self.equations = solved_equations().next_to(self.a_group, RIGHT, buff=1.1)
        line = self.say(r"Solve for $x_1$ and $x_3$ in terms of the free ones.", line, hold=0.2)
        for equation in self.equations:
            self.play(Write(equation), run_time=1.1)
        self.wait(Timing.read_short)
        self.play(FadeOut(frames), FadeOut(free_tags), run_time=0.4)
        return line

    def split_by_free(self, line):
        self.row, self.names = parametric_row()
        VGroup(self.row, self.names).move_to(np.array([0, -1.0, 0]))
        row = self.row
        head, variables, general = row[0], row[1], row[3]
        line = self.say(r"Write $\mathbf x$ with only the free variables left.", line, hold=0.2)
        self.play(FadeIn(head), FadeIn(variables), run_time=0.7)
        first, second = self.equations
        self.play(
            FadeIn(row[2]),
            FadeIn(general.get_brackets()),
            TransformMatchingShapes(first[2:].copy(), general.get_entries()[0]),
            TransformMatchingShapes(second[2:].copy(), general.get_entries()[2]),
            FadeIn(general.get_entries()[1]),
            FadeIn(general.get_entries()[3]),
            run_time=1.4,
        )
        self.wait(Timing.read_short)

        line = self.say(r"Split by free variable: one vector for each.", line, hold=0.2)
        self.play(FadeIn(row[4]), FadeIn(row[5]), FadeIn(row[6]), run_time=0.9, rate_func=spring_soft)
        self.play(FadeIn(row[7]), FadeIn(row[8]), FadeIn(row[9]), run_time=0.9, rate_func=spring_soft)
        self.play(FadeIn(self.names, shift=UP * 0.1), run_time=0.6)
        self.wait(Timing.read_short)
        return line

    def independence(self, line):
        general = self.row[3]
        frames = identity_frames(self.row)
        variable_frames = VGroup(*[SurroundingRectangle(general.get_entries()[i], color=Palette.glow, buff=0.08, stroke_width=3) for i in (1, 3)])
        line = self.say(r"Rows 2 and 4 of $\mathbf x$ are just $x_2$ and $x_4$.", line, hold=0.2)
        self.play(Create(variable_frames), run_time=0.8)
        self.play(Create(frames), run_time=0.9)
        self.wait(Timing.read_short)
        line = self.say(r"So only zero weights give $\mathbf 0$, and $\{\mathbf u, \mathbf v\}$ is a basis.", line, hold=Timing.read_short)
        self.play(FadeOut(variable_frames), run_time=0.4)

        sizes = VGroup(
            MathTex(r"\operatorname{Nul}A \subseteq \mathbb R^4", color=Palette.pink, font_size=42),
            MathTex(r"\operatorname{Col}A \subseteq \mathbb R^2", color=Palette.teal, font_size=42),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        sizes.move_to(self.equations, aligned_edge=LEFT)
        line = self.say(r"$A$ has 4 columns, so $\operatorname{Nul}A$ lives in $\mathbb R^4$.", line, hold=0.2)
        self.play(FadeOut(self.equations), FadeIn(sizes[0], shift=UP * 0.1), run_time=0.8)
        self.play(Indicate(VGroup(self.row[6], self.row[9]), color=Palette.glow, scale_factor=1.06), run_time=1.0)
        line = self.say(r"Each output has 2 entries, so $\operatorname{Col}A$ lives in $\mathbb R^2$.", line, hold=0.2)
        self.play(FadeIn(sizes[1], shift=UP * 0.1), run_time=0.7)
        self.wait(Timing.read_short)
        return line


def centerpiece_base(scene, with_null=True):
    plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
    scene.add(plane, plane_line(plane, COL_ENDS, Palette.teal, stroke_width=4))
    if with_null:
        scene.add(plane_line(plane, NULL_ENDS, Palette.pink, stroke_width=5))
    return plane


def trail(plane, point, s, color=Palette.purple_gray, opacity=0.55):
    return Line(plane.c2p(*point), plane.c2p(*slid(point, s)), color=color, stroke_width=2, stroke_opacity=opacity)


def panel_at_corner(*lines):
    content = VGroup(*lines).arrange(DOWN, buff=0.35, aligned_edge=LEFT).to_corner(UL, buff=0.55)
    return VGroup(plate_for(content), content)


class FigCollapse(Scene):
    def construct(self):
        plane = centerpiece_base(self)
        movers = [(4, -2), (1, -3), (-3, -1), (-2, 4), (0, 3), (5, 1)]
        for point in movers:
            self.add(
                Arrow(plane.c2p(*point), plane.c2p(*project(point)), buff=0.08, color=Palette.purple_gray, stroke_width=3, max_tip_length_to_length_ratio=0.12),
                Dot(plane.c2p(*point), radius=0.07, color=Palette.purple_gray),
            )
        for point in [(x, -x) for x in range(-4, 4) if x != 0]:
            self.add(Dot(plane.c2p(*point), radius=0.09, color=Palette.pink))
        self.add(
            Dot(plane.c2p(0, 0), radius=0.3, color=Palette.glow, fill_opacity=0.25),
            ring(plane.c2p(0, 0)),
            tag(r"\operatorname{Nul}P", Palette.pink, plane.c2p(-2.6, 2.6), RIGHT, buff=0.25),
            tag(r"\operatorname{Col}P", Palette.teal, plane.c2p(3.6, 3.6), RIGHT),
            panel_at_corner(p_definition(), product_line((1, -1), (0, 0), Palette.pink)),
        )


class FigShiftedCopy(Scene):
    def construct(self):
        plane = centerpiece_base(self)
        solution = plane_line(plane, solution_ends(), Palette.yellow, stroke_width=5)
        self.add(
            solution,
            vector_arrow(P_POINT, Palette.yellow, plane, stroke_width=6),
            DashedLine(plane.c2p(*P_POINT), plane.c2p(1, 3), color=Palette.pink, stroke_width=7, dash_length=0.12),
            Dot(plane.c2p(1, 3), radius=0.12, color=Palette.yellow),
            ring(plane.c2p(*B_POINT)),
            ring(plane.c2p(0, 0)),
            tag(r"\mathbf b", Palette.teal, plane.c2p(*B_POINT), RIGHT, buff=0.3),
            tag(r"\mathbf p", Palette.yellow, plane.c2p(*P_POINT), UR, buff=0.12),
            tag(r"\operatorname{Nul}P", Palette.pink, plane.c2p(-2.6, 2.6), RIGHT, buff=0.25),
            tag(r"\operatorname{Col}P", Palette.teal, plane.c2p(3.6, 3.6), RIGHT),
            panel_at_corner(p_definition(), shifted_rule()),
        )


class FigFreeVariables(Scene):
    def construct(self):
        row, names = parametric_row()
        reduced = VGroup(MathTex("A", r"\sim", color=Palette.text), free_matrix(A_REDUCED)).arrange(RIGHT, buff=0.2)
        equations = solved_equations()
        top = VGroup(reduced, equations).arrange(RIGHT, buff=1.2)
        VGroup(top, VGroup(row, names)).arrange(DOWN, buff=0.8)
        names[0].next_to(row[6], DOWN, buff=0.2)
        names[1].next_to(row[9], DOWN, buff=0.2)
        self.add(top, row, names, identity_frames(row))
        fit_to_frame(self, margin=0.6)


class Poster(Scene):
    def construct(self):
        plane = centerpiece_base(self, with_null=False)
        s = 0.62
        for point in LATTICE:
            if on_null_line(point):
                continue
            self.add(trail(plane, point, s, opacity=0.35), Dot(plane.c2p(*slid(point, s)), radius=0.06, color=Palette.purple_gray))
        self.add(plane_line(plane, [slid(end, s) for end in NULL_ENDS], Palette.pink, stroke_width=6))
        for point in LATTICE:
            if on_null_line(point) and point != (0, 0):
                self.add(trail(plane, point, s, color=Palette.pink, opacity=0.5), Dot(plane.c2p(*slid(point, s)), radius=0.09, color=Palette.pink))
        self.add(Dot(plane.c2p(0, 0), radius=0.34, color=Palette.glow, fill_opacity=0.28), Dot(plane.c2p(0, 0), radius=0.09, color=Palette.glow))
