import pathlib
import sys
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    LiveMatrix,
    Palette,
    Timing,
    augmented_block,
    fit_to_frame,
    live_basis_arrows,
    live_grid,
    make_plane,
    matrix,
    morph_matrix,
    plane_at,
    plate_for,
    scrim,
    skewed_grid,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (3.0, 0.0)
PLANE_UNIT = 1.25
GRID_MOVE = 1.0
GRID_OPACITY = 0.55
GRID_REACH = 4
IDENTITY = ((1, 0), (0, 1))
A = ((2, 1), (1, 1))
A_INVERSE = ((1, -1), (-1, 2))
SINGULAR = ((1, 2), (1, 2))
SINGULAR_STEP = ((1, 0), (-1, 1))

SHEAR = ((1, 0), (-2, 1))
SHEAR_UNDO = ((1, 0), (2, 1))
SWAP = ((0, 1), (1, 0))
STRETCH = ((2, 0), (0, 1))
STRETCH_UNDO = ((Fraction(1, 2), 0), (0, 1))

KINDS = [
    (SHEAR, r"R_2 \leftarrow R_2 - 2R_1", SHEAR_UNDO, r"R_2 \leftarrow R_2 + 2R_1"),
    (SWAP, r"R_1 \leftrightarrow R_2", SWAP, r"R_1 \leftrightarrow R_2"),
    (STRETCH, r"R_1 \leftarrow 2R_1", STRETCH_UNDO, r"R_1 \leftarrow \tfrac12 R_1"),
]

STEPS = [
    (SWAP, r"R_1 \leftrightarrow R_2", r"Swap the rows, and the grid reflects."),
    (((1, 0), (-2, 1)), r"R_2 \leftarrow R_2 - 2R_1", r"Subtract 2 times row 1, and the grid shears."),
    (((1, 0), (0, -1)), r"R_2 \leftarrow -R_2", r"Scale row 2 by $-1$, and the grid flips over."),
    (((1, -1), (0, 1)), r"R_1 \leftarrow R_1 - R_2", r"Subtract row 2 from row 1, and the grid squares up."),
]
INVERSE_FACTORS = [
    ((1, 1), (0, 1)),
    ((1, 0), (0, -1)),
    ((1, 0), (2, 1)),
    SWAP,
]


def entry_tex(value):
    value = Fraction(value).limit_denominator(12)
    if value.denominator == 1:
        return str(value.numerator)
    sign = "-" if value < 0 else ""
    return rf"{sign}\tfrac{{{abs(value.numerator)}}}{{{value.denominator}}}"


def multiply(first, second):
    return tuple(tuple(sum(Fraction(first[i][k]) * Fraction(second[k][j]) for k in range(2)) for j in range(2)) for i in range(2))


def left_multiply_block(factor, rows):
    return [[sum(Fraction(factor[i][k]) * Fraction(rows[k][j]) for k in range(2)) for j in range(len(rows[0]))] for i in range(2)]


def paint_columns(mat, colors):
    for col, color in zip(mat.get_columns(), colors):
        if color:
            col.set_color(color)
    return mat


def square_matrix(rows):
    """A 2x2 matrix whose columns wear the colors of where i-hat and j-hat land."""
    return paint_columns(matrix([[entry_tex(v) for v in row] for row in rows]), (Palette.i_hat, Palette.j_hat))


def block(rows, right_color=None):
    """[left | right] with the left columns green and red, because they are the arrows on the grid."""
    mat = augmented_block([[entry_tex(v) for v in row] for row in rows], split=2)
    return paint_columns(mat, (Palette.i_hat, Palette.j_hat, right_color, right_color))


def joined(left, right):
    return [list(left[0]) + list(right[0]), list(left[1]) + list(right[1])]


def reduction_states(start, steps):
    states = [joined(start, IDENTITY)]
    for factor, *_ in steps:
        states.append(left_multiply_block(factor, states[-1]))
    return states


def op_tex(tex, font_size=40):
    return MathTex(tex, color=Palette.text, font_size=font_size)


def named_matrix(name, rows):
    return VGroup(MathTex(rf"{name} =", color=Palette.text, font_size=48), square_matrix(rows)).arrange(RIGHT, buff=0.2)


def kind_card(name, rows, tex):
    """`E = [..]` with its row operation written underneath."""
    equation = named_matrix(name, rows)
    label = op_tex(tex, font_size=36).next_to(equation[1], DOWN, buff=0.3)
    return VGroup(equation, label)


def product_sheet():
    """E times a general matrix, with the answer showing the row operation."""
    general = Matrix([["a", "b"], ["c", "d"]], v_buff=0.62, h_buff=0.9, bracket_h_buff=0.14).set_color(Palette.text)
    answer = Matrix([["a", "b"], ["c - 2a", "d - 2b"]], v_buff=0.62, h_buff=1.9, bracket_h_buff=0.14).set_color(Palette.text)
    equals = MathTex("=", color=Palette.text, font_size=48)
    return VGroup(square_matrix(SHEAR), general, equals, answer).arrange(RIGHT, buff=0.25).scale(1.15)


def small_grid(rows, size=2.6, reach=3):
    """A small square plane showing the grid after `rows`, with i-hat and j-hat, for side-by-side figures."""
    plane = make_plane(x_range=(-reach, reach, 1), y_range=(-reach, reach, 1), x_length=size, y_length=size)
    plane.background_lines.set_stroke(opacity=0.25)
    plane.faded_lines.set_stroke(opacity=0.2)
    columns = [(float(rows[0][i]), float(rows[1][i])) for i in range(2)]
    grid = skewed_grid(plane, columns[0], columns[1], reach=12, color=Palette.blue, opacity=0.6)
    arrows = VGroup(
        vector_arrow(columns[0], Palette.i_hat, plane, stroke_width=4),
        vector_arrow(columns[1], Palette.j_hat, plane, stroke_width=4),
    )
    return VGroup(plane, grid, arrows)


class Lesson(LessonScene):
    day = 8
    title = "Elementary matrices and computing inverses"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        self.live = LiveMatrix(IDENTITY)
        line = self.grid_appears(plane)
        line = self.identity_to_e(line)
        line = self.e_times_a(line)
        line = self.kinds_and_undo(line)
        line = self.centerpiece(line)
        line = self.why_it_works(line)
        line = self.product_of_elementaries(line)
        line = self.singular(line)
        self.close_episode(
            r"Every row operation is multiplication by an elementary matrix.\\"
            r"Reducing $[A\ \ I]$ to $[I\ \ A^{-1}]$ builds the inverse.",
            *self.mobjects,
        )

    def grid_appears(self, plane):
        self.grid = live_grid(plane, self.live, opacity=GRID_OPACITY, reach=GRID_REACH)
        self.arrows = live_basis_arrows(plane, self.live)
        line = self.say(r"Row operations from Day 3 can be written as matrices.", hold=0.2)
        self.play(
            plane.background_lines.animate.set_stroke(opacity=0.25),
            plane.faded_lines.animate.set_stroke(opacity=0.2),
            FadeIn(self.grid),
            run_time=1.0,
        )
        self.play(FadeIn(self.arrows, scale=0.6), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return line

    def show_panel(self, content, *extra, run_time=0.8):
        self.plate = plate_for(content)
        self.play(FadeIn(self.plate), FadeIn(content, shift=UP * 0.15), *extra, run_time=run_time, rate_func=spring_soft)

    def grow_plate(self, *contents):
        self.play(self.plate.animate.become(plate_for(VGroup(*contents))), run_time=0.5, rate_func=spring_soft)

    def identity_to_e(self, line):
        self.card = kind_card("I", IDENTITY, KINDS[0][1]).to_corner(UL, buff=0.6)
        equation, label = self.card
        line = self.say(r"Start with $I$ and do one row operation to it.", line, hold=0.2)
        self.show_panel(equation)
        self.wait(Timing.beat)
        self.grow_plate(self.card)
        self.play(FadeIn(label, shift=DOWN * 0.15), run_time=0.6)
        self.play(Indicate(equation[1].get_rows()[1], color=Palette.glow, scale_factor=1.15), run_time=0.9)
        e_card = kind_card("E", SHEAR, KINDS[0][1]).move_to(self.card, aligned_edge=UL)
        e_name = e_card[0][0]
        morph_matrix(self, equation[1], e_card[0][1], FadeTransform(equation[0], e_name), run_time=1.2, rate_func=spring)
        equation.submobjects[0] = e_name
        line = self.say(r"The result is called an elementary matrix, $E$.", line, hold=Timing.read_short)
        return line

    def e_times_a(self, line):
        veil = scrim()
        sheet = product_sheet().move_to(UP * 0.5)
        e_rows, answer_rows = sheet[0].get_rows(), sheet[3].get_rows()
        line = self.say(r"Multiplying by $E$ does that row operation to any matrix.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(Write(sheet), run_time=2.0)
        self.wait(Timing.read_short)

        line = self.say(r"Row 2 of $E$ asks for $-2R_1 + R_2$.", line, hold=0.2)
        marks = VGroup(
            SurroundingRectangle(e_rows[1], color=Palette.glow, buff=0.1, corner_radius=0),
            SurroundingRectangle(answer_rows[1], color=Palette.glow, buff=0.1, corner_radius=0),
        )
        self.play(Create(marks), run_time=0.8)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(sheet, marks)), FadeOut(veil), run_time=0.7)
        return line

    def kinds_and_undo(self, line):
        captions = [
            (r"As a move of the plane, $E$ is a shear.", r"Adding 2 times row 1 back undoes it."),
            (r"A swap reflects the plane, and swapping again undoes it.", None),
            (r"Scaling by 2 stretches the plane, and scaling by $\tfrac12$ undoes it.", None),
        ]
        for index, ((rows, tex, undo_rows, undo_tex), (doing, undoing)) in enumerate(zip(KINDS, captions)):
            if index:
                self.switch_kind(rows, tex)
            line = self.say(doing, line, hold=0.2)
            self.play(*self.live.left_multiply(rows), run_time=GRID_MOVE, rate_func=spring)
            self.wait(Timing.beat)
            if undoing:
                line = self.say(undoing, line, hold=0.2)
            self.undo_kind(undo_rows, undo_tex)
        self.play(FadeOut(self.card), FadeOut(self.undo_card), FadeOut(self.plate), run_time=0.6)
        return line

    def switch_kind(self, rows, tex):
        new_card = kind_card("E", rows, tex).move_to(self.card, aligned_edge=UL)
        self.play(FadeOut(self.undo_card), run_time=0.4)
        self.grow_plate(new_card)
        morph_matrix(self, self.card[0][1], new_card[0][1], FadeTransform(self.card[1], new_card[1]), run_time=1.0, rate_func=spring_soft)
        self.card = VGroup(self.card[0], new_card[1])

    def undo_kind(self, rows, tex):
        self.undo_card = kind_card("E^{-1}", rows, tex).next_to(self.card, RIGHT, buff=0.6, aligned_edge=UP)
        self.grow_plate(self.card, self.undo_card)
        self.play(FadeIn(self.undo_card, shift=LEFT * 0.2), run_time=0.7, rate_func=spring_soft)
        self.play(*self.live.move_to(IDENTITY), run_time=GRID_MOVE, rate_func=spring)
        self.wait(Timing.beat)

    def centerpiece(self, line):
        states = reduction_states(A, STEPS)
        a_card = named_matrix("A", A).to_corner(UL, buff=0.6)
        line = self.say(r"Here is a matrix $A$ and the grid it makes.", line, hold=0.2)
        self.show_panel(a_card)
        self.play(*self.live.move_to(A), run_time=GRID_MOVE, rate_func=spring)
        self.wait(Timing.beat)

        line = self.say(r"Row reduce $A$ to $I$, doing each step to $I$ too.", line, hold=0.2)
        self.block = block(states[0]).to_corner(UL, buff=0.6)
        self.grow_plate(self.block)
        left_entries = VGroup(*[self.block.get_rows()[r][c] for r in range(2) for c in range(2)])
        right_entries = VGroup(*[self.block.get_rows()[r][c] for r in range(2) for c in (2, 3)])
        self.play(
            FadeOut(a_card[0]),
            ReplacementTransform(a_card[1].get_entries(), left_entries),
            ReplacementTransform(a_card[1].get_brackets(), self.block.get_brackets()),
            run_time=1.0,
            rate_func=spring_soft,
        )
        self.play(FadeIn(right_entries, shift=LEFT * 0.2), Create(self.block.bar), run_time=0.8)
        self.add(self.block)
        self.wait(Timing.beat)

        for index, (factor, tex, words) in enumerate(STEPS):
            line = self.reduction_step(index, factor, tex, words, states[index + 1], line)
        return self.reveal_inverse(line)

    def step_labels(self, index, tex):
        name = op_tex(rf"E_{index + 1}:\ {tex}", font_size=36)
        product = op_tex("".join(f"E_{k}" for k in range(index + 1, 0, -1)), font_size=36)
        name.next_to(self.block, DOWN, buff=0.35).align_to(self.block, LEFT)
        product.next_to(name, DOWN, buff=0.3).align_to(self.block.get_columns()[2], LEFT)
        return name, product

    def reduction_step(self, index, factor, tex, words, rows, line):
        line = self.say(words, line, hold=0.2)
        name, product = self.step_labels(index, tex)
        if index == 0:
            self.grow_plate(self.block, name, product)
            self.play(FadeIn(name, shift=DOWN * 0.15), FadeIn(product, shift=DOWN * 0.15), run_time=0.7)
        else:
            self.grow_plate(self.block, name, product, self.step_name, self.step_product)
            self.play(FadeTransform(self.step_name, name), FadeTransform(self.step_product, product), run_time=0.7)
        self.step_name, self.step_product = name, product
        target = block(rows).move_to(self.block)
        morph_matrix(self, self.block, target, *self.live.left_multiply(factor), run_time=GRID_MOVE, rate_func=spring)
        self.wait(Timing.read_short)
        return line

    def reveal_inverse(self, line):
        line = self.say(r"The left half is $I$, so the right half is $A^{-1}$.", line, hold=0.2)
        rows = self.block.get_rows()
        right = VGroup(*[rows[r][c] for r in range(2) for c in (2, 3)])
        named = op_tex(r"E_4E_3E_2E_1 = A^{-1}", font_size=36).move_to(self.step_product, aligned_edge=DOWN)
        named.align_to(self.step_product, LEFT)
        self.grow_plate(self.block, self.step_name, named)
        self.play(right.animate.set_color(Palette.teal), FadeTransform(self.step_product, named), run_time=1.0)
        self.play(Indicate(right, color=Palette.glow, scale_factor=1.15), run_time=0.9)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(self.block, named, self.step_name)), FadeOut(self.plate), run_time=0.6)
        return line

    def why_it_works(self, line):
        veil = scrim()
        rows = VGroup(
            MathTex(r"E_4E_3E_2E_1", r"A", "=", "I", color=Palette.text, font_size=56),
            MathTex(r"E_4E_3E_2E_1", "=", r"A^{-1}", color=Palette.text, font_size=56),
            MathTex(r"E_4E_3E_2E_1", r"\begin{bmatrix} A & I \end{bmatrix}", "=", r"\begin{bmatrix} I & A^{-1} \end{bmatrix}", color=Palette.text, font_size=56),
        ).arrange(DOWN, buff=0.6).move_to(UP * 0.5)
        for row, equals in ((rows[1], rows[1][1]), (rows[2], rows[2][2])):
            row.shift(RIGHT * (rows[0][2].get_center()[0] - equals.get_center()[0]))
        rows[1][2].set_color(Palette.teal)
        rows[2][3].set_color(Palette.teal)
        line = self.say(r"Four steps turned $A$ into $I$.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(Write(rows[0]), run_time=1.4)
        self.wait(Timing.read_short)
        line = self.say(r"Multiply both sides by $A^{-1}$ to see the product is $A^{-1}$.", line, hold=0.2)
        self.play(FadeTransform(rows[0].copy(), rows[1]), run_time=1.2)
        self.wait(Timing.read_short)
        line = self.say(r"The right half applied that same product to $I$.", line, hold=0.2)
        self.play(FadeTransform(rows[1].copy(), rows[2]), run_time=1.2)
        self.wait(Timing.read_long)
        self.play(FadeOut(rows), FadeOut(veil), run_time=0.7)
        return line

    def product_of_elementaries(self, line):
        formula = MathTex("A", "=", r"E_1^{-1}", r"E_2^{-1}", r"E_3^{-1}", r"E_4^{-1}", color=Palette.text, font_size=52)
        formula.to_corner(UL, buff=0.6)
        line = self.say(r"Run the steps backwards, last one first.", line, hold=0.2)
        self.plate = plate_for(formula)
        self.play(FadeIn(self.plate), FadeIn(formula[1]), run_time=0.6)
        for part, factor in zip(reversed(formula[2:]), INVERSE_FACTORS):
            self.play(FadeIn(part, shift=DOWN * 0.2), *self.live.left_multiply(factor), run_time=GRID_MOVE, rate_func=spring)
            self.wait(0.4)
        self.play(FadeIn(formula[0], shift=RIGHT * 0.2), run_time=0.6)
        line = self.say(r"So $A$ is a product of elementary matrices.", line, hold=Timing.read_short)
        line = self.say(r"Every invertible matrix can be built this way.", line, hold=Timing.beat)
        self.play(FadeOut(formula), FadeOut(self.plate), run_time=0.6)
        return line

    def singular(self, line):
        start = joined(SINGULAR, IDENTITY)
        self.block = block(start).to_corner(UL, buff=0.6)
        line = self.say(r"This $B$ flattens the whole plane onto one line.", line, hold=0.2)
        self.show_panel(self.block)
        self.play(*self.live.move_to(SINGULAR), run_time=GRID_MOVE, rate_func=spring)
        self.wait(Timing.beat)

        line = self.say(r"Row reducing leaves a zero row, so no step reaches $I$.", line, hold=0.2)
        name = op_tex(r"R_2 \leftarrow R_2 - R_1", font_size=36).next_to(self.block, DOWN, buff=0.4).align_to(self.block, LEFT)
        self.grow_plate(self.block, name)
        self.play(FadeIn(name, shift=DOWN * 0.15), run_time=0.6)
        target = block(left_multiply_block(SINGULAR_STEP, start)).move_to(self.block)
        morph_matrix(self, self.block, target, *self.live.left_multiply(SINGULAR_STEP), run_time=GRID_MOVE, rate_func=spring)
        zero_row = VGroup(self.block.get_rows()[1][0], self.block.get_rows()[1][1])
        self.play(zero_row.animate.set_color(Palette.glow), run_time=0.5)
        self.play(Indicate(zero_row, color=Palette.glow, scale_factor=1.2), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"A flattened plane can't be unflattened, so $B$ has no inverse.", line, hold=Timing.read_short)
        return line


class FigThreeKinds(Scene):
    def construct(self):
        panels = VGroup()
        for rows, tex, undo_rows, undo_tex in KINDS:
            cards = VGroup(kind_card("E", rows, tex), kind_card("E^{-1}", undo_rows, undo_tex)).arrange(RIGHT, buff=0.5, aligned_edge=UP)
            panels.add(VGroup(small_grid(rows, size=3.4), cards.scale(0.75)).arrange(DOWN, buff=0.4))
        panels.arrange(RIGHT, buff=0.9, aligned_edge=UP)
        self.add(panels)
        fit_to_frame(self, margin=0.5)


class FigInverseSteps(Scene):
    def construct(self):
        states = reduction_states(A, STEPS)
        stages = VGroup()
        for index, rows in enumerate(states):
            left = [row[:2] for row in rows]
            color = Palette.teal if index == len(STEPS) else None
            stages.add(VGroup(block(rows, right_color=color), small_grid(left, size=2.6)).arrange(DOWN, buff=0.35))
        stages.arrange(RIGHT, buff=0.9, aligned_edge=UP)
        links = VGroup()
        for index, (_, tex, _) in enumerate(STEPS):
            first, second = stages[index][0], stages[index + 1][0]
            label = op_tex(rf"E_{index + 1}", font_size=34)
            arrow = Arrow(first.get_right(), second.get_left(), buff=0.12, color=Palette.text_muted, stroke_width=3, max_tip_length_to_length_ratio=0.25)
            links.add(VGroup(arrow, label.next_to(arrow, UP, buff=0.12)))
        operations = VGroup(*[op_tex(tex, font_size=30).next_to(stage[1], DOWN, buff=0.3) for stage, (_, tex, _) in zip(stages[1:], STEPS)])
        self.add(stages, links, operations)
        fit_to_frame(self, margin=0.4)


class FigProductSteps(Scene):
    def construct(self):
        running = IDENTITY
        stages = VGroup(VGroup(small_grid(running), op_tex("I", font_size=40)).arrange(DOWN, buff=0.3))
        for index, factor in enumerate(INVERSE_FACTORS):
            running = multiply(factor, running)
            name = "".join(rf"E_{k}^{{-1}}" for k in range(4 - index, 5))
            if index == len(INVERSE_FACTORS) - 1:
                name = rf"A = {name}"
            stages.add(VGroup(small_grid(running), op_tex(name, font_size=34)).arrange(DOWN, buff=0.3))
        stages.arrange(RIGHT, buff=1.1, aligned_edge=UP)
        self.add(stages)
        fit_to_frame(self, margin=0.4)


class Poster(Scene):
    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        plane.background_lines.set_stroke(opacity=0.25)
        plane.faded_lines.set_stroke(opacity=0.2)
        live = LiveMatrix(A)
        states = reduction_states(A, STEPS)
        panel = VGroup(block(states[0]), MathTex(r"\sim", color=Palette.text, font_size=56), block(states[-1], right_color=Palette.teal))
        panel.arrange(RIGHT, buff=0.3).scale(0.8).to_corner(UL, buff=0.6)
        self.add(plane, live_grid(plane, live, opacity=GRID_OPACITY, reach=GRID_REACH), live_basis_arrows(plane, live), plate_for(panel), panel)
