import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    Palette,
    Timing,
    backed,
    cell_outline,
    column,
    fit_to_frame,
    make_plane,
    matrix,
    morph_matrix,
    plane_at,
    plate_for,
    skewed_grid,
    spring,
    spring_soft,
    vector_arrow,
    wide_plane_at,
)

SMALL_A = [[1, 1], [2, 3]]
SMALL_L = [[1, 0], [2, 1]]
SMALL_U = [[1, 1], [0, 1]]
SMALL_X = (1, 1)
SMALL_Y = (2, 1)
SMALL_B = (2, 5)
PLANE_ORIGIN = (1.2, -2.7)
PLANE_UNIT = 0.85

A = [[2, 1, -1], [4, 5, 0], [-2, 8, 5]]
A_STEP = [[2, 1, -1], [0, 3, 2], [0, 9, 4]]
U = [[2, 1, -1], [0, 3, 2], [0, 0, -2]]
L = [[1, 0, 0], [2, 1, 0], [-1, 3, 1]]
PIVOTS = [(0, 0), (1, 1), (2, 2)]
FIRST_B, FIRST_Y, FIRST_X = (-1, -1, 0), (-1, 1, -4), (1, -1, 2)
SECOND_B, SECOND_Y, SECOND_X = (0, 5, 13), (0, 5, -2), (0, 1, 1)

FORWARD_WORK = (r"y_1 = -1", r"y_2 = -1 - 2(-1) = 1", r"y_3 = 0 + (-1) - 3(1) = -4")
BACK_WORK = (r"x_1 = \big(-1 - (-1) + 2\big) \div 2 = 1", r"x_2 = (1 - 2\cdot 2) \div 3 = -1", r"x_3 = (-4) \div (-2) = 2")

FLOPS_PER_FACTOR = 2 / 3
FLOPS_PER_SOLVE = 0.002


def tex(*parts, colors=(), font_size=48):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def l_matrix(rows):
    """L with its below-diagonal multipliers in pink and its zeros muted."""
    mat = matrix(rows)
    for (row, col), entry in zip(((r, c) for r in range(len(rows)) for c in range(len(rows))), mat.get_entries()):
        if row > col:
            entry.set_color(Palette.pink)
        elif row < col:
            entry.set_color(Palette.text_muted)
    return mat


def work_matrix(rows):
    """The matrix being eliminated. Entries that elimination cleared are muted."""
    mat = matrix(rows)
    width = len(rows[0])
    for index, entry in enumerate(mat.get_entries()):
        row, col = divmod(index, width)
        if row > col and rows[row][col] == 0:
            entry.set_color(Palette.text_muted)
    return mat


SOLVE_SCALE = 0.72


def vector_column(entries, color):
    return column([str(entry) for entry in entries], color=color).scale(SOLVE_SCALE)


def slot(entry):
    return Square(side_length=0.42, color=Palette.text_muted, stroke_width=2, stroke_opacity=0.6).move_to(entry)


def pivot_box(mat, row, col, depth):
    cells = VGroup(*[mat.get_rows()[r][col] for r in range(row, depth)])
    return SurroundingRectangle(cells, color=Palette.glow, buff=0.1, stroke_width=3, corner_radius=0)


def divided_column(values, anchors, x):
    """The pivot column divided by its pivot: a muted 1, then pink multipliers, each level with its row."""
    entries = VGroup()
    for index, (value, anchor) in enumerate(zip(values, anchors)):
        color = Palette.text_muted if index == 0 else Palette.pink
        entries.add(MathTex(str(value), color=color, font_size=48).move_to([x, anchor.get_center()[1], 0]))
    return entries


def row_ops_label(ops):
    """Row replacements R_i <- R_i - m R_j with every multiplier m in pink."""
    parts, colors = [], []
    for index, (target, multiplier, source) in enumerate(ops):
        lead = r",\quad " if index else ""
        shown = f"({multiplier})" if multiplier < 0 else str(multiplier)
        parts += [f"{lead}R_{target} \\leftarrow R_{target} -", shown, f"R_{source}"]
        colors += [None, Palette.pink, None]
    return tex(*parts, colors=colors, font_size=40)


def small_panel():
    parts = [
        tex("A", "="),
        matrix(SMALL_A),
        tex("="),
        l_matrix(SMALL_L),
        matrix(SMALL_U),
    ]
    parts[4].get_entries()[2].set_color(Palette.text_muted)
    row = VGroup(*parts).arrange(RIGHT, buff=0.2)
    names = VGroup(
        MathTex("L", color=Palette.text_muted, font_size=40).next_to(parts[3], DOWN, buff=0.15),
        MathTex("U", color=Palette.text_muted, font_size=40).next_to(parts[4], DOWN, buff=0.15),
    )
    return VGroup(row, names).scale(0.8)


def name_tag(tex_string, color, point, direction):
    return backed(MathTex(tex_string, color=color, font_size=40)).next_to(point, direction, buff=0.12)


def cost_axes():
    axes = Axes(
        x_range=[0, 100, 20],
        y_range=[0, 70, 10],
        x_length=9.0,
        y_length=4.6,
        axis_config={"color": Palette.axis, "stroke_width": 2, "include_tip": False, "font_size": 28},
        x_axis_config={"numbers_to_include": [0, 20, 40, 60, 80, 100]},
        y_axis_config={"numbers_to_include": [0, 20, 40, 60]},
    )
    for number in [*axes.x_axis.numbers, *axes.y_axis.numbers]:
        number.set_color(Palette.text_muted)
    x_name = Tex(r"right-hand sides $k$", color=Palette.text_muted, font_size=32).next_to(axes.x_axis, DOWN, buff=0.55)
    y_name = Tex(r"billions of flops", color=Palette.text_muted, font_size=32).next_to(axes.y_axis, UP, buff=0.2).align_to(axes.y_axis, LEFT)
    return axes, VGroup(x_name, y_name)


def cost_lines(axes):
    each_time = axes.plot(lambda k: FLOPS_PER_FACTOR * k, x_range=[0, 100], color=Palette.purple_gray, stroke_width=5)
    once = axes.plot(lambda k: FLOPS_PER_FACTOR + FLOPS_PER_SOLVE * k, x_range=[0, 100], color=Palette.teal, stroke_width=5)
    return each_time, once


def cost_labels(axes):
    top = axes.c2p(100, FLOPS_PER_FACTOR * 100)
    bottom = axes.c2p(100, FLOPS_PER_FACTOR + FLOPS_PER_SOLVE * 100)
    each_label = VGroup(
        Tex(r"row reduce each time", color=Palette.purple_gray, font_size=34).next_to(axes.c2p(58, FLOPS_PER_FACTOR * 58), UL, buff=0.15),
        MathTex(r"\approx 67", color=Palette.purple_gray, font_size=36).next_to(top, RIGHT, buff=0.2),
    )
    once_label = VGroup(
        Tex(r"LU once", color=Palette.teal, font_size=34).next_to(axes.c2p(58, 0), UP, buff=0.25),
        MathTex(r"\approx 0.87", color=Palette.teal, font_size=36).next_to(bottom, RIGHT, buff=0.2),
    )
    marks = VGroup(Dot(top, radius=0.08, color=Palette.glow), Dot(bottom, radius=0.08, color=Palette.glow))
    return each_label, once_label, marks


class Lesson(LessonScene):
    day = 9
    title = "LU decomposition"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.two_shears(plane)
        line = self.undo_shears(line)
        self.play(FadeOut(VGroup(plane, self.grid, self.panel_group, self.arrow, self.arrow_name)), run_time=1.0)
        line = self.set_up_elimination(line)
        line = self.first_column(line)
        line = self.second_column(line)
        line = self.name_factors(line)
        line = self.rebuild_a(line)
        line = self.forward_substitution(line)
        line = self.back_substitution(line)
        line = self.new_right_side(line)
        line = self.cost_chart(line)
        self.close_episode(
            r"$A = LU$ records elimination once.\\"
            r"Each new $\mathbf b$ is then two quick triangular solves.",
            *self.mobjects,
        )

    # The 2 by 2 picture: U and L are two shears.

    def two_shears(self, plane):
        self.origin = plane.c2p(0, 0)
        self.grid = wide_plane_at(PLANE_ORIGIN, PLANE_UNIT, reach=60)
        self.panel = small_panel().to_corner(UL, buff=0.5)
        self.plate = plate_for(self.panel)
        self.panel_group = VGroup(self.plate, self.panel)
        line = self.say(r"Here a matrix $A$ is written as a product $LU$.", hold=0.2)
        self.play(FadeIn(self.plate), Write(self.panel), run_time=1.6)
        self.arrow = vector_arrow(SMALL_X, Palette.yellow, plane)
        self.arrow_name = name_tag(r"\mathbf x", Palette.yellow, plane.c2p(*SMALL_X), UR)
        self.play(GrowArrow(self.arrow), FadeIn(self.arrow_name), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)

        row = self.panel[0]

        self.add(self.grid, plane)
        plane.set_opacity(0.25)
        self.bring_to_front(self.arrow, self.arrow_name, self.panel_group)
        line = self.say(r"Multiplying by $U$ first shears the grid sideways.", line, hold=0.2)
        self.shear(SMALL_U, SMALL_Y, Palette.blue, r"\mathbf y", highlight=row[4])
        self.wait(Timing.beat)
        line = self.say(r"Then $L$ shears it vertically and lands on $\mathbf b$.", line, hold=0.2)
        self.shear(SMALL_L, SMALL_B, Palette.teal, r"\mathbf b", highlight=row[3])
        self.wait(Timing.read_short)
        return line

    def shear(self, mat, tip, color, name, highlight=None, direction=UR):
        target = Arrow(self.origin, self.grid_point(tip), buff=0, color=color, stroke_width=6, max_tip_length_to_length_ratio=0.18, max_stroke_width_to_length_ratio=12)
        new_name = name_tag(name, color, target.get_end(), direction)
        extra = [Indicate(highlight, color=Palette.glow, scale_factor=1.08)] if highlight is not None else []
        self.play(
            ApplyMatrix(mat, self.grid, about_point=self.origin, rate_func=spring_soft),
            Transform(self.arrow, target, rate_func=spring_soft),
            FadeTransform(self.arrow_name, new_name, rate_func=spring_soft),
            *extra,
            run_time=2.2,
        )
        self.arrow_name = new_name

    def grid_point(self, coords):
        return self.origin + PLANE_UNIT * np.array([coords[0], coords[1], 0.0])

    def undo_shears(self, line):
        inverse_l = [[1, 0], [-2, 1]]
        inverse_u = [[1, -1], [0, 1]]
        step = tex(r"L", r"\mathbf y", "=", r"\mathbf b", colors=(None, Palette.blue, None, Palette.teal))
        step.next_to(self.panel, DOWN, buff=0.35).align_to(self.panel, LEFT)
        second = tex(r"U", r"\mathbf x", "=", r"\mathbf y", colors=(None, Palette.yellow, None, Palette.blue)).move_to(step, aligned_edge=LEFT)
        line = self.say(r"To solve $A\mathbf x = \mathbf b$, undo $L$ first, then $U$.", line, hold=0.2)
        self.play(self.plate.animate.become(plate_for(VGroup(self.panel, step))), FadeIn(step, shift=UP * 0.1), run_time=0.8)
        self.shear(inverse_l, SMALL_Y, Palette.blue, r"\mathbf y")
        self.wait(Timing.beat)
        self.play(FadeOut(step, shift=UP * 0.1), run_time=0.3)
        self.play(FadeIn(second, shift=UP * 0.1), run_time=0.4)
        self.shear(inverse_u, SMALL_X, Palette.yellow, r"\mathbf x")
        self.wait(Timing.beat)
        self.panel_group.add(second)
        return line

    # The centerpiece: multipliers drop into L while U forms.

    def set_up_elimination(self, line):
        self.work = work_matrix(A).move_to(RIGHT * 2.6 + UP * 0.5)
        self.lower = l_matrix(L).move_to(LEFT * 3.4 + UP * 0.5)
        self.slots = VGroup()
        for index, entry in enumerate(self.lower.get_entries()):
            row, col = divmod(index, 3)
            if row > col:
                entry.set_opacity(0)
                self.slots.add(slot(entry))
        self.work_name = MathTex("A", color=Palette.text, font_size=48).next_to(self.work, UP, buff=0.3)
        self.lower_name = MathTex("L", color=Palette.pink, font_size=48).next_to(self.lower, UP, buff=0.3)
        line = self.say(r"Elimination builds $L$ and $U$ at the same time.", line, hold=0.2)
        self.play(FadeIn(self.work), FadeIn(self.work_name), run_time=0.8)
        self.play(FadeIn(self.lower), FadeIn(self.lower_name), Create(self.slots), run_time=1.0)
        self.wait(Timing.read_short)
        self.op_label = None
        return line

    def divide_pivot_column(self, pivot, current_rows):
        row, col = pivot
        box = pivot_box(self.work, row, col, 3)
        values = [current_rows[r][col] for r in range(row, 3)]
        pivot_value = values[0]
        quotients = [value // pivot_value if value % pivot_value == 0 else value / pivot_value for value in values]
        anchors = [self.work.get_rows()[r] for r in range(row, 3)]
        column_x = (self.lower.get_right()[0] + self.work.get_left()[0]) / 2
        divided = divided_column(quotients, anchors, column_x)
        divisor = MathTex(rf"\div {pivot_value}" if pivot_value > 0 else rf"\div ({pivot_value})", color=Palette.glow, font_size=40)
        divisor.next_to(divided, UP, buff=0.3)
        self.play(Create(box), run_time=0.7)
        sources = VGroup(*[self.work.get_rows()[r][col] for r in range(row, 3)])
        self.play(FadeTransform(sources.copy(), divided), FadeIn(divisor, shift=LEFT * 0.2), run_time=1.3, rate_func=spring_soft)
        return box, divided, divisor

    def drop_into_l(self, pivot, divided):
        row, col = pivot
        entries = self.lower.get_entries()
        landings = [entries[r * 3 + col] for r in range(row, 3)]
        moves = []
        for index, (flying, landing) in enumerate(zip(divided, landings)):
            target = landing.copy().set_opacity(1)
            if index == 0:
                target.set_color(Palette.text)
            moves.append(Transform(flying, target, path_arc=-0.6))
        filled = VGroup(*self.slots[: len(landings) - 1])
        self.play(LaggedStart(*moves, lag_ratio=0.25), FadeOut(filled), run_time=1.6, rate_func=spring_soft)
        for landing in landings[1:]:
            landing.set_opacity(1)
        self.remove(*divided)
        self.slots.remove(*filled)

    def eliminate(self, rows, ops):
        label = row_ops_label(ops).next_to(self.work, DOWN, buff=0.45)
        overflow = label.get_right()[0] - (config.frame_width / 2 - 0.4)
        if overflow > 0:
            label.shift(LEFT * overflow)
        swap = [FadeOut(self.op_label)] if self.op_label is not None else []
        self.play(*swap, FadeIn(label, shift=UP * 0.1), run_time=0.6)
        self.op_label = label
        target = work_matrix(rows).move_to(self.work)
        morph_matrix(self, self.work, target, run_time=1.6, rate_func=spring_soft)

    def first_column(self, line):
        line = self.say(r"Divide the pivot column by its pivot.", line, hold=0.2)
        box, divided, divisor = self.divide_pivot_column(PIVOTS[0], A)
        self.wait(Timing.read_short)
        line = self.say(r"Those numbers drop into column 1 of $L$.", line, hold=0.2)
        self.play(FadeOut(divisor), run_time=0.3)
        self.drop_into_l(PIVOTS[0], divided)
        self.wait(Timing.beat)
        line = self.say(r"The same multipliers clear the entries below the pivot.", line, hold=0.2)
        self.eliminate(A_STEP, [(2, 2, 1), (3, -1, 1)])
        self.play(FadeOut(box), run_time=0.4)
        self.wait(Timing.read_short)
        return line

    def second_column(self, line):
        line = self.say(r"Repeat one column over, using the current matrix.", line, hold=0.2)
        box, divided, divisor = self.divide_pivot_column(PIVOTS[1], A_STEP)
        self.wait(Timing.beat)
        self.play(FadeOut(divisor), run_time=0.3)
        self.drop_into_l(PIVOTS[1], divided)
        self.eliminate(U, [(3, 3, 2)])
        self.play(FadeOut(box), run_time=0.4)
        self.wait(Timing.beat)

        last = pivot_box(self.work, 2, 2, 3)
        line = self.say(r"The last pivot has nothing below it, so we are done.", line, hold=0.2)
        self.play(Create(last), FadeOut(self.op_label), run_time=0.7)
        self.wait(Timing.beat + 0.5)
        self.play(FadeOut(last), run_time=0.4)
        return line

    def name_factors(self, line):
        u_name = MathTex("U", color=Palette.text, font_size=48).move_to(self.work_name)
        below = cell_outline(self.work, lower=True)
        above = cell_outline(self.lower, lower=False)
        line = self.say(r"$U$ is an echelon form, all zeros below the diagonal.", line, hold=0.2)
        self.play(FadeTransform(self.work_name, u_name), run_time=0.8)
        self.work_name = u_name
        self.play(Create(below), run_time=1.0)
        self.wait(Timing.read_short)
        line = self.say(r"$L$ has 1s on its diagonal and zeros above.", line, hold=0.2)
        self.play(Create(above), run_time=1.0)
        self.wait(Timing.read_short)
        self.play(FadeOut(below), FadeOut(above), run_time=0.5)
        return line

    def rebuild_a(self, line):
        original = matrix(A)
        equals = tex("=")
        name = MathTex("A", color=Palette.text, font_size=48)
        product = VGroup(original, equals, self.lower.copy(), self.work.copy()).arrange(RIGHT, buff=0.3).scale(0.85).move_to(UP * 0.7)
        lower_target, work_target = product[2], product[3]
        name.next_to(original, UP, buff=0.3)
        line = self.say(r"Multiplying $LU$ adds the multiples back and rebuilds $A$.", line, hold=0.2)
        self.play(
            self.lower.animate.become(lower_target),
            self.work.animate.become(work_target),
            self.lower_name.animate.next_to(lower_target, UP, buff=0.3),
            self.work_name.animate.next_to(work_target, UP, buff=0.3),
            run_time=1.2,
            rate_func=spring_soft,
        )
        self.play(FadeIn(original, shift=RIGHT * 0.2), FadeIn(equals), FadeIn(name), run_time=0.9)
        self.wait(Timing.beat)

        line = self.say(r"Row 2 of $A$ is 2 copies of row 1 of $U$ plus row 2.", line, hold=0.2)
        marks = VGroup(
            SurroundingRectangle(self.lower.get_rows()[1], color=Palette.glow, buff=0.08, stroke_width=3, corner_radius=0),
            SurroundingRectangle(VGroup(self.work.get_rows()[0], self.work.get_rows()[1]), color=Palette.glow, buff=0.08, stroke_width=3, corner_radius=0),
        )
        result = SurroundingRectangle(original.get_rows()[1], color=Palette.teal, buff=0.08, stroke_width=3, corner_radius=0)
        self.play(Create(marks), run_time=0.8)
        self.play(TransformFromCopy(marks, result), run_time=1.0)
        self.wait(Timing.read_short + 0.5)
        self.play(FadeOut(marks), FadeOut(result), run_time=0.4)

        elimination = MathTex(r"E_2E_1A = U", color=Palette.text, font_size=46).next_to(product, DOWN, buff=0.6)
        solved = MathTex(r"A = (E_2E_1)^{-1}U = LU", color=Palette.text, font_size=46).move_to(elimination)
        line = self.say(r"Elimination is $E_2E_1A = U$, so $L$ is $(E_2E_1)^{-1}$.", line, hold=0.2)
        self.play(Write(elimination), run_time=1.0)
        self.wait(Timing.beat)
        self.play(FadeTransform(elimination, solved), run_time=1.0)
        self.wait(Timing.read_short + 0.5)
        self.play(FadeOut(VGroup(original, equals, name, solved)), run_time=0.6)
        return line

    # Solving with the factors: two triangular solves.

    def stage(self, mat, unknowns, right, y):
        mat.generate_target()
        mat.target.set(height=matrix(L).height * SOLVE_SCALE)
        row = VGroup(mat.target, unknowns, tex("="), right).arrange(RIGHT, buff=0.22)
        row.move_to([-3.2, y, 0])
        return row

    def forward_substitution(self, line):
        self.y_col = vector_column(("y_1", "y_2", "y_3"), Palette.blue)
        self.b_col = vector_column(FIRST_B, Palette.teal)
        top = self.stage(self.lower, self.y_col, self.b_col, 1.75)
        self.x_col = vector_column(("x_1", "x_2", "x_3"), Palette.yellow)
        self.y_copy = vector_column(("y_1", "y_2", "y_3"), Palette.blue)
        bottom = self.stage(self.work, self.x_col, self.y_copy, -1.35)
        self.top_row, self.bottom_row = top, bottom

        line = self.say(r"First solve $L\mathbf y = \mathbf b$ from the top row down.", line, hold=0.2)
        self.play(
            MoveToTarget(self.lower),
            FadeOut(self.lower_name),
            MoveToTarget(self.work),
            FadeOut(self.work_name),
            run_time=1.2,
            rate_func=spring_soft,
        )
        self.play(FadeIn(VGroup(top[1], top[2], top[3])), run_time=0.8)
        self.forward_lines = self.cascade(self.lower, (self.y_col, Palette.blue), FORWARD_WORK, FIRST_Y, range(3), line)
        return self.last_line

    def cascade(self, mat, unknowns_and_color, work, values, order, line):
        unknowns, color = unknowns_and_color
        lines = VGroup()
        solved = [entry.get_tex_string() for entry in unknowns.get_entries()]
        for step, index in enumerate(order):
            if step == 1:
                line = self.say(self.cascade_caption(unknowns), line, hold=0.2)
            box = SurroundingRectangle(mat.get_rows()[index], color=Palette.glow, buff=0.08, stroke_width=3, corner_radius=0)
            work_line = MathTex(work[index], color=Palette.text, font_size=36)
            work_line.move_to([0, mat.get_rows()[index].get_center()[1], 0]).align_to(RIGHT * 0.9, LEFT)
            solved[index] = str(values[index])
            target = vector_column(solved, color).move_to(unknowns)
            self.play(Create(box), FadeIn(work_line, shift=RIGHT * 0.15), run_time=0.8)
            morph_matrix(self, unknowns, target, run_time=0.8)
            self.wait(0.5)
            self.play(FadeOut(box), run_time=0.3)
            lines.add(work_line)
        self.last_line = line
        return lines

    def cascade_caption(self, unknowns):
        if unknowns is self.y_col:
            return r"Each row adds one new unknown, so plug in and go."
        return r"Work upward, plugging in what is already known."

    def back_substitution(self, line):
        line = self.say(r"Then solve $U\mathbf x = \mathbf y$ from the bottom row up.", line, hold=0.2)
        solved_y = vector_column(FIRST_Y, Palette.blue).move_to(self.y_copy)
        self.y_copy = solved_y
        self.play(FadeIn(VGroup(self.bottom_row[1], self.bottom_row[2])), TransformFromCopy(self.y_col, solved_y), run_time=1.2)
        self.back_lines = self.cascade(self.work, (self.x_col, Palette.yellow), BACK_WORK, FIRST_X, (2, 1, 0), line)
        line = self.say(r"So $\mathbf x = (1, -1, 2)$ solves $A\mathbf x = \mathbf b$.", self.last_line, hold=0.2)
        self.play(Indicate(self.x_col, color=Palette.yellow, scale_factor=1.1), run_time=0.9)
        self.wait(Timing.read_short)
        return line

    def new_right_side(self, line):
        line = self.say(r"A new $\mathbf b$ reuses $L$ and $U$, with no elimination.", line, hold=0.2)
        self.play(FadeOut(self.forward_lines), FadeOut(self.back_lines), run_time=0.5)
        for mat, values, color in (
            (self.b_col, SECOND_B, Palette.teal),
            (self.y_col, SECOND_Y, Palette.blue),
            (self.y_copy, SECOND_Y, Palette.blue),
            (self.x_col, SECOND_X, Palette.yellow),
        ):
            morph_matrix(self, mat, vector_column(values, color).move_to(mat), run_time=0.8)
            self.wait(0.3)
        self.wait(Timing.read_short)
        leaving = VGroup(self.lower, self.work, self.y_col, self.b_col, self.top_row[2], self.x_col, self.bottom_row[2], self.y_copy)
        self.play(FadeOut(leaving), run_time=0.7)
        return line

    # Why it saves work.

    def cost_chart(self, line):
        axes, names = cost_axes()
        chart = VGroup(axes, names).move_to(UP * 0.55)
        each_time, once = cost_lines(axes)
        each_label, once_label, marks = cost_labels(axes)
        line = self.say(r"For $n = 1000$, row reducing costs $\tfrac23 n^3$ flops each time.", line, hold=0.2)
        self.play(FadeIn(chart), run_time=0.8)
        self.play(Create(each_time), run_time=1.6, rate_func=smooth)
        self.play(FadeIn(each_label, shift=LEFT * 0.1), GrowFromCenter(marks[0]), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        line = self.say(r"LU pays $\tfrac23 n^3$ once, then about $2n^2$ per $\mathbf b$.", line, hold=0.2)
        self.play(Create(once), run_time=1.6, rate_func=smooth)
        self.play(FadeIn(once_label, shift=UP * 0.1), GrowFromCenter(marks[1]), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        line = self.say(r"At 100 right-hand sides, LU does 77 times less work.", line, hold=0.2)
        self.play(Indicate(once_label, color=Palette.teal), run_time=1.0)
        self.wait(Timing.read_short)
        self.play(FadeOut(line), run_time=0.4)
        return None


def shear_panel(mat, tip, color, name):
    plane = make_plane(x_range=(-1, 4, 1), y_range=(-1, 6, 1), x_length=5, y_length=7)
    plane.set_opacity(0.3)
    box = ((-1, 4), (-1, 6))
    grid = skewed_grid(plane, (mat[0][0], mat[1][0]), (mat[0][1], mat[1][1]), color=Palette.grid, opacity=0.9, box=box)
    arrow = vector_arrow(tip, color, plane, stroke_width=7)
    tag = backed(MathTex(name, color=color, font_size=64)).next_to(plane.c2p(*tip), RIGHT, buff=0.2)
    return VGroup(plane, grid, arrow, tag)


class FigShears(Scene):
    def construct(self):
        panels = VGroup(*[
            shear_panel(mat, tip, color, name)
            for mat, tip, color, name in (
                ([[1, 0], [0, 1]], SMALL_X, Palette.yellow, r"\mathbf x"),
                (SMALL_U, SMALL_Y, Palette.blue, r"\mathbf y"),
                (SMALL_A, SMALL_B, Palette.teal, r"\mathbf b"),
            )
        ]).arrange(RIGHT, buff=1.6)
        arrows = VGroup(*[
            MathTex(rf"\xrightarrow{{\;{name}\;}}", color=Palette.text, font_size=110).move_to((left.get_right() + right.get_left()) / 2)
            for name, left, right in (("U", panels[0], panels[1]), ("L", panels[1], panels[2]))
        ])
        self.add(panels, arrows)
        fit_to_frame(self)


class FigFactor(Scene):
    def construct(self):
        product = VGroup(matrix(A), tex("="), l_matrix(L), work_matrix(U)).arrange(RIGHT, buff=0.35)
        names = VGroup(*[
            MathTex(name, color=color, font_size=48).next_to(product[index], UP, buff=0.3)
            for index, name, color in ((0, "A", Palette.text), (2, "L", Palette.pink), (3, "U", Palette.text))
        ])
        boxes = VGroup(*[pivot_box(product[3], row, col, row + 1) for row, col in PIVOTS])
        self.add(product, names, boxes)
        fit_to_frame(self, margin=0.9)


class FigCost(Scene):
    def construct(self):
        axes, names = cost_axes()
        each_time, once = cost_lines(axes)
        each_label, once_label, marks = cost_labels(axes)
        self.add(axes, names, each_time, once, each_label, once_label, marks)
        fit_to_frame(self, margin=0.5)


class Poster(Scene):
    def construct(self):
        grid = wide_plane_at((0, -1.5), 0.9, reach=60)
        grid.apply_matrix(SMALL_A, about_point=grid.c2p(0, 0))
        grid.set_stroke(opacity=0.35)
        lower, upper = l_matrix(L), work_matrix(U)
        product = VGroup(lower, upper).arrange(RIGHT, buff=0.35).scale(1.7)
        boxes = VGroup(*[pivot_box(upper, row, col, row + 1) for row, col in PIVOTS])
        group = VGroup(product, boxes)
        self.add(grid, plate_for(group, padding=0.45), group)
