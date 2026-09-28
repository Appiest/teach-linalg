import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    Palette,
    Timing,
    augmented,
    backed,
    equation_line,
    fit_to_frame,
    make_plane,
    morph_matrix,
    spring,
    spring_soft,
)

ROW_ONE = (1, -2, -1)
ROW_TWO = (-1, 3, 3)
PARALLEL = (-1, 2, 3)
SAME_LINE = (-1, 2, 1)
SOLUTION = (3, 2)
ROW_COLORS = (Palette.yellow, Palette.blue)

BIG_START = [[1, -2, 3, 1, 4], [2, -4, 7, 0, 9], [-1, 2, -2, -3, -3]]
BIG_CLEARED = [[1, -2, 3, 1, 4], [0, 0, 1, -2, 1], [0, 0, 1, -2, 1]]
BIG_ECHELON = [[1, -2, 3, 1, 4], [0, 0, 1, -2, 1], [0, 0, 0, 0, 0]]
BIG_REDUCED = [[1, -2, 0, 7, 1], [0, 0, 1, -2, 1], [0, 0, 0, 0, 0]]
BIG_PIVOTS = [(0, 0), (1, 2)]
BIG_SCALE = 1.25


def combine(row, other, factor):
    return tuple(a + factor * b for a, b in zip(row, other))


def tidy(value):
    return int(round(value)) if abs(value - round(value)) < 1e-9 else value


def system_matrix(rows):
    mat = augmented([[tidy(v) for v in row] for row in rows])
    for index, color in enumerate(ROW_COLORS):
        mat.get_rows()[index].set_color(color)
    return mat


def panel_matrix(rows):
    return backed(system_matrix(rows).scale(0.85), padding=0.2)


def equation_tex(coeffs, color):
    a, b, c = (tidy(v) for v in coeffs)
    first = {1: "x_1", -1: "-x_1"}.get(a, f"{a}x_1")
    sign = "-" if b < 0 else "+"
    second = "x_2" if abs(b) == 1 else f"{abs(b)}x_2"
    return MathTex(first, sign, second, "=", str(c), color=color, font_size=46)


class TrackedLine:
    """A line whose three coefficients are ValueTrackers, so it can pivot and slide while the matrix changes."""

    def __init__(self, plane, coeffs, color):
        self.trackers = [ValueTracker(v) for v in coeffs]
        self.mobject = always_redraw(lambda: equation_line(plane, self.values(), color))

    def values(self):
        return tuple(tracker.get_value() for tracker in self.trackers)

    def move_to(self, coeffs):
        return [tracker.animate.set_value(v) for tracker, v in zip(self.trackers, coeffs)]


def staircase(mat, pivots, color=Palette.glow):
    """Steps drawn under the leading entries of an echelon matrix."""
    rows, columns = mat.get_rows(), mat.get_columns()
    half_gap = (columns[1].get_center()[0] - columns[0].get_center()[0]) / 2
    half_row = (rows[0].get_center()[1] - rows[1].get_center()[1]) / 2

    def left_of(col):
        return columns[col].get_center()[0] - half_gap * 0.8

    def below(row):
        return rows[row].get_center()[1] - half_row

    first_row, first_col = pivots[0]
    points = [[left_of(first_col) + half_gap * 0.2, below(first_row), 0]]
    for (row, col), following in zip(pivots, [*pivots[1:], None]):
        points.append([left_of(col), below(row), 0])
        next_x = left_of(following[1]) if following else columns[-2].get_right()[0] + 0.15
        points.append([next_x, below(row), 0])
    return VMobject(color=color, stroke_width=4).set_points_as_corners(points)


def readable_lines(plane):
    """Dashed previews of x1 = 3 and x2 = 2, the system row reduction is aiming for."""
    return VGroup(*[
        DashedLine(*equation_line(plane, coeffs).get_start_and_end(), color=color, stroke_width=4, stroke_opacity=0.9)
        for coeffs, color in (((1, 0, 3), Palette.yellow), ((0, 1, 2), Palette.blue))
    ])


def pivot_boxes(mat, pivots):
    return VGroup(*[
        SurroundingRectangle(mat.get_rows()[row][col], color=Palette.glow, buff=0.08, stroke_width=3, corner_radius=0)
        for row, col in pivots
    ])


class Lesson(LessonScene):
    day = 3
    title = "Systems of equations and row reduction"

    def construct(self):
        plane = make_plane()
        self.plane = plane
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        yellow, blue, line = self.two_lines(plane)
        line = self.three_outcomes(plane, yellow, blue, line)
        mat, line = self.to_matrix(line)
        line = self.operations_card(line)
        mat, line = self.scaling_keeps_line(plane, mat, line)
        mat, line = self.pivot_to_answer(plane, yellow, blue, mat, line)
        line = self.inconsistent(plane, yellow, blue, mat, line)
        line = self.echelon(line)
        self.close_episode(
            r"Row operations change the equations but never the solutions.\\"
            r"So keep simplifying until you can read the answer.",
            *self.mobjects,
        )

    def two_lines(self, plane):
        equations = VGroup(equation_tex(ROW_ONE, Palette.yellow), equation_tex(ROW_TWO, Palette.blue))
        equations.arrange(DOWN, buff=0.35, aligned_edge=RIGHT)
        self.equation_rows = list(equations)
        self.equations = backed(equations, padding=0.25).to_corner(UL, buff=0.5)
        line = self.say(r"Yesterday, asking if $\mathbf b$ is in a span meant solving equations.", hold=0.2)
        self.play(Write(self.equations), run_time=1.6)
        self.wait(Timing.beat)
        line = self.say(r"Today we learn a method that solves any linear system.", line, hold=Timing.read_short)
        line = self.say(r"A linear system is equations that share the same unknowns.", line, hold=0.2)
        self.play(Indicate(self.equations, color=Palette.glow, scale_factor=1.04), run_time=1.0)
        self.wait(Timing.beat)

        yellow = TrackedLine(plane, ROW_ONE, Palette.yellow)
        blue = TrackedLine(plane, ROW_TWO, Palette.blue)
        line = self.say(r"Every point on a line satisfies that line's equation.", line, hold=0.2)
        self.play(Create(yellow.mobject), run_time=1.4)
        self.play(Create(blue.mobject), run_time=1.4)
        self.wait(Timing.read_short)

        self.dot = Dot(plane.c2p(*SOLUTION), radius=0.12, color=Palette.teal)
        self.dot_label = backed(MathTex(r"(3,\,2)", color=Palette.teal, font_size=40)).next_to(self.dot, DR, buff=0.12)
        line = self.say(r"A solution satisfies both, so it sits where they cross.", line, hold=0.2)
        self.play(GrowFromCenter(self.dot), FadeIn(self.dot_label), run_time=0.8, rate_func=spring)
        self.wait(Timing.read_short)
        return yellow, blue, line

    def retarget_second(self, blue, coeffs, *extra):
        new_tex = equation_tex(coeffs, Palette.blue).move_to(self.equation_rows[1], aligned_edge=RIGHT)
        self.play(*blue.move_to(coeffs), Transform(self.equation_rows[1], new_tex), *extra, run_time=1.8, rate_func=spring_soft)

    def three_outcomes(self, plane, yellow, blue, line):
        line = self.say(r"Parallel lines never meet, so there is no solution.", line, hold=0.2)
        self.retarget_second(blue, PARALLEL, FadeOut(self.dot), FadeOut(self.dot_label))
        self.wait(Timing.read_short)

        line = self.say(r"The same line twice gives infinitely many solutions.", line, hold=0.2)
        self.retarget_second(blue, SAME_LINE)
        solution_set = equation_line(plane, ROW_ONE, Palette.teal, stroke_width=9)
        self.play(Create(solution_set), run_time=1.2)
        self.wait(Timing.read_short)

        line = self.say(r"Lines that cross give exactly one solution.", line, hold=0.2)
        self.play(FadeOut(solution_set), run_time=0.4)
        self.retarget_second(blue, ROW_TWO)
        self.play(GrowFromCenter(self.dot), FadeIn(self.dot_label), run_time=0.8, rate_func=spring)
        self.wait(Timing.read_short)
        return line

    def to_matrix(self, line):
        mat = panel_matrix([ROW_ONE, ROW_TWO])
        mat.next_to(self.equations, RIGHT, buff=0.6)
        line = self.say(r"Keeping only the numbers gives the \emph{augmented matrix}.", line, hold=0.2)
        self.play(FadeIn(mat.background_rectangle), FadeIn(mat.get_brackets()), FadeIn(mat.bar), run_time=0.6)
        for index in range(2):
            self.play(TransformFromCopy(self.equation_rows[index], mat.get_rows()[index]), run_time=1.3)
        self.wait(Timing.read_short)
        line = self.say(r"It has 2 rows and 3 columns, so it is $2 \times 3$.", line, hold=0.2)
        self.play(Indicate(VGroup(*mat.get_rows()), color=Palette.glow, scale_factor=1.08), run_time=1.0)
        self.wait(Timing.beat)
        self.play(FadeOut(self.equations), mat.animate.to_corner(UL, buff=0.3), run_time=1.0, rate_func=spring_soft)
        return mat, line

    def operations_card(self, line):
        rows = [
            (r"Replacement", r"R_2 \leftarrow R_2 + c\,R_1", r"R_2 \leftarrow R_2 - c\,R_1"),
            (r"Interchange", r"R_1 \leftrightarrow R_2", r"R_1 \leftrightarrow R_2"),
            (r"Scaling", r"R_2 \leftarrow c\,R_2,\ c \neq 0", r"R_2 \leftarrow \tfrac{1}{c}\,R_2"),
        ]
        cells = [Tex(r"Operation", color=Palette.text_muted, font_size=34), Tex(r"\phantom{x}", font_size=34), Tex(r"Undo it with", color=Palette.text_muted, font_size=34)]
        for name, op, undo in rows:
            cells += [Tex(name, color=Palette.text, font_size=38), MathTex(op, color=Palette.text, font_size=40), MathTex(undo, color=Palette.text_muted, font_size=40)]
        table = VGroup(*cells).arrange_in_grid(rows=4, cols=3, buff=(0.6, 0.35), col_alignments="lll")
        card = backed(table, padding=0.4, opacity=0.96).move_to(RIGHT * 1.9 + UP * 0.2)
        line = self.say(r"Row reduction simplifies the system until you can read the answer.", line, hold=0.2)
        goal_lines = readable_lines(self.plane)
        self.play(Create(goal_lines), run_time=1.2)
        self.wait(Timing.beat)
        line = self.say(r"Its moves must never change which point solves the system.", line, hold=0.2)
        self.play(Flash(self.dot, color=Palette.glow, line_length=0.25, flash_radius=0.3), run_time=0.8)
        self.wait(Timing.beat)
        self.play(FadeOut(goal_lines), run_time=0.5)
        line = self.say(r"Three \emph{row operations} change a matrix.", line, hold=0.2)
        self.play(FadeIn(card.background_rectangle), *[FadeIn(cell) for cell in cells[:3]], run_time=0.8)
        self.play(LaggedStart(*[FadeIn(cell, shift=RIGHT * 0.15) for cell in cells[3:]], lag_ratio=0.12), run_time=1.6)
        self.wait(Timing.read_short)
        line = self.say(r"Each one can be undone by an operation of the same kind.", line, hold=0.2)
        self.play(Indicate(VGroup(*cells[5::3]), color=Palette.glow, scale_factor=1.06), run_time=1.0)
        self.wait(Timing.read_long)
        self.play(FadeOut(card), run_time=0.6)
        return line

    def op_label(self, mat, tex):
        return backed(MathTex(tex, color=Palette.text, font_size=42)).next_to(mat, RIGHT, buff=0.4)

    def swap_rows(self, mat):
        rows = mat.get_rows()
        offset = rows[0].get_center() - rows[1].get_center()
        self.play(rows[0].animate.shift(-offset), rows[1].animate.shift(offset), run_time=1.0, path_arc=PI / 2, rate_func=spring_soft)

    def scaling_keeps_line(self, plane, mat, line):
        label = self.op_label(mat, r"R_1 \leftrightarrow R_2")
        line = self.say(r"Swapping two rows only changes the order of the equations.", line, hold=0.2)
        self.play(FadeIn(label), run_time=0.4)
        self.swap_rows(mat)
        self.wait(Timing.beat)
        self.swap_rows(mat)
        self.wait(Timing.beat)

        doubled = self.op_label(mat, r"R_2 \leftarrow 2R_2")
        scaled = panel_matrix([ROW_ONE, combine(ROW_TWO, ROW_TWO, 1)]).move_to(mat, aligned_edge=LEFT)
        line = self.say(r"Scaling a row changes its numbers but not its line.", line, hold=0.2)
        self.play(Transform(label, doubled), run_time=0.5)
        morph_matrix(self, mat, scaled, run_time=1.2)
        self.play(ShowPassingFlash(equation_line(plane, ROW_TWO, Palette.blue, stroke_width=12), time_width=0.6), run_time=1.2)
        self.wait(Timing.read_short)
        halved = self.op_label(mat, r"R_2 \leftarrow \tfrac12 R_2")
        restored = panel_matrix([ROW_ONE, ROW_TWO]).move_to(mat, aligned_edge=LEFT)
        self.play(Transform(label, halved), run_time=0.5)
        morph_matrix(self, mat, restored, run_time=1.2)
        self.wait(Timing.beat)
        self.play(FadeOut(label), run_time=0.4)
        return mat, line

    def replace_row(self, mat, line_obj, new_rows, coeffs, run_time=2.6):
        target = panel_matrix(new_rows).move_to(mat, aligned_edge=LEFT)
        morph_matrix(self, mat, target, *line_obj.move_to(coeffs), run_time=run_time, rate_func=spring_soft)

    def pivot_to_answer(self, plane, yellow, blue, mat, line):
        self.add_foreground_mobjects(self.dot)
        label = self.op_label(mat, r"R_2 \leftarrow R_2 + R_1")
        line = self.say(r"A \emph{replacement} adds a multiple of one row to another.", line, hold=0.2)
        self.play(FadeIn(label), run_time=0.4)
        self.play(Indicate(mat.get_rows()[0], color=Palette.glow), run_time=0.8)
        new_two = combine(ROW_TWO, ROW_ONE, 1)
        line = self.say(r"The blue line turns, but the crossing point never moves.", line, hold=0.2)
        self.replace_row(mat, blue, [ROW_ONE, new_two], new_two)
        self.play(Flash(self.dot, color=Palette.glow, line_length=0.25, flash_radius=0.3), run_time=0.8)
        self.wait(Timing.read_short)

        new_one = combine(ROW_ONE, new_two, 2)
        label2 = self.op_label(mat, r"R_1 \leftarrow R_1 + 2R_2")
        line = self.say(r"Add two copies of row 2 to row 1.", line, hold=0.2)
        self.play(Transform(label, label2), run_time=0.5)
        self.replace_row(mat, yellow, [new_one, new_two], new_one)
        self.play(Flash(self.dot, color=Palette.glow, line_length=0.25, flash_radius=0.3), run_time=0.8)
        self.wait(Timing.beat)

        reads = VGroup(
            backed(MathTex(r"x_1 = 3", color=Palette.yellow, font_size=40)).next_to(plane.c2p(3, 3.3), RIGHT, buff=0.15),
            backed(MathTex(r"x_2 = 2", color=Palette.blue, font_size=40)).next_to(plane.c2p(6.2, 2), UP, buff=0.15),
        )
        line = self.say(r"Now each row reads off one unknown: $x_1 = 3$, $x_2 = 2$.", line, hold=0.2)
        self.play(*[TransformFromCopy(mat.get_rows()[i], reads[i]) for i in range(2)], run_time=1.4)
        self.wait(Timing.read_long)
        self.play(FadeOut(reads), FadeOut(label), run_time=0.5)
        self.foreground_mobjects.clear()
        return mat, line

    def inconsistent(self, plane, yellow, blue, mat, line):
        start = panel_matrix([ROW_ONE, PARALLEL]).move_to(mat, aligned_edge=LEFT)
        line = self.say(r"Try the same move on the parallel lines.", line, hold=0.2)
        morph_matrix(
            self, mat, start, *yellow.move_to(ROW_ONE), *blue.move_to(PARALLEL),
            FadeOut(self.dot), FadeOut(self.dot_label), run_time=1.8, rate_func=spring_soft,
        )
        label = self.op_label(mat, r"R_2 \leftarrow R_2 + R_1")
        self.play(FadeIn(label), run_time=0.4)
        self.wait(Timing.beat)
        escape = combine(PARALLEL, ROW_ONE, 0.96)
        target = panel_matrix([ROW_ONE, (0, 0, 2)]).move_to(mat, aligned_edge=LEFT)
        morph_matrix(self, mat, target, *blue.move_to(escape), run_time=2.6, rate_func=rush_into)
        ring = SurroundingRectangle(mat.get_rows()[1], color=Palette.glow, buff=0.1, stroke_width=3)
        line = self.say(r"The row $[\,0\ \ 0 \mid 2\,]$ says $0 = 2$, so nothing solves it.", line, hold=0.2)
        self.play(Create(ring), run_time=0.8)
        self.wait(Timing.read_long)
        self.play(FadeOut(ring), FadeOut(label), run_time=0.5)
        self.play(FadeOut(VGroup(mat, yellow.mobject, blue.mobject, plane)), run_time=1.0)
        return line

    def big_step(self, mat, rows, tex, label):
        target = augmented(rows).scale(BIG_SCALE).move_to(mat, aligned_edge=LEFT)
        new_label = MathTex(tex, color=Palette.text, font_size=44).next_to(target, DOWN, buff=0.5)
        self.play(FadeOut(label), FadeIn(new_label, shift=UP * 0.1), run_time=0.5)
        morph_matrix(self, mat, target, run_time=1.4, rate_func=spring_soft)
        self.wait(Timing.beat)
        return new_label

    def echelon(self, line):
        mat = augmented(BIG_START).scale(BIG_SCALE).move_to(LEFT * 2.6 + UP * 0.4)
        names = VGroup(*[
            MathTex(f"x_{i + 1}", color=Palette.text_muted, font_size=42).next_to(mat.get_columns()[i], UP, buff=0.4)
            for i in range(4)
        ])
        label = MathTex(r"\phantom{R}", font_size=42).next_to(mat, DOWN, buff=0.5)
        line = self.say(r"Bigger systems use the same moves, one column at a time.", line, hold=0.2)
        self.play(FadeIn(mat), FadeIn(names), FadeIn(label), run_time=1.0)
        line = self.say(r"The first target is a staircase shape called \emph{echelon form}.", line, hold=Timing.read_short)
        label = self.big_step(mat, BIG_CLEARED, r"R_2 \leftarrow R_2 - 2R_1, \quad R_3 \leftarrow R_3 + R_1", label)
        label = self.big_step(mat, BIG_ECHELON, r"R_3 \leftarrow R_3 - R_2", label)

        steps = staircase(mat, BIG_PIVOTS)
        line = self.say(r"In echelon form, each leading entry sits right of the one above.", line, hold=0.2)
        self.play(Create(steps), run_time=1.4)
        self.wait(Timing.read_short)

        line = self.say(r"In reduced form, each \emph{pivot} is 1 and alone in its column.", line, hold=0.2)
        label = self.big_step(mat, BIG_REDUCED, r"R_1 \leftarrow R_1 - 3R_2", label)
        boxes = pivot_boxes(mat, BIG_PIVOTS)
        self.play(Create(boxes), run_time=1.0)
        self.wait(Timing.read_short)
        line = self.free_variables(mat, names, label, line)
        return line

    def free_variables(self, mat, names, label, line):
        free_tags = VGroup(*[
            Tex("free", color=Palette.glow, font_size=38).next_to(names[i], UP, buff=0.15) for i in (1, 3)
        ])
        line = self.say(r"Columns without a pivot belong to \emph{free variables}.", line, hold=0.2)
        self.play(FadeOut(label), *[FadeIn(tag, shift=DOWN * 0.1) for tag in free_tags], run_time=0.8)
        self.play(*[names[i].animate.set_color(Palette.glow) for i in (1, 3)], run_time=0.5)
        self.wait(Timing.read_short)

        solution = MathTex(
            r"x_1 &= 1 + 2x_2 - 7x_4 \\ x_2 &\text{ is free} \\ x_3 &= 1 + 2x_4 \\ x_4 &\text{ is free}",
            color=Palette.text, font_size=46,
        ).next_to(mat, RIGHT, buff=1.0)
        line = self.say(r"Choose any free values and the other unknowns follow.", line, hold=0.2)
        self.play(Write(solution), run_time=2.2)
        self.wait(Timing.read_long + 1.0)
        return line


class FigThreeOutcomes(Scene):
    def construct(self):
        panels = VGroup()
        for second, solution in ((PARALLEL, None), (ROW_TWO, "point"), (SAME_LINE, "line")):
            plane = make_plane(x_range=(-4, 6, 1), y_range=(-2, 5, 1))
            parts = [plane, equation_line(plane, ROW_ONE, Palette.yellow), equation_line(plane, second, Palette.blue)]
            if solution == "line":
                parts.append(equation_line(plane, ROW_ONE, Palette.teal, stroke_width=9))
            if solution == "point":
                parts.append(Dot(plane.c2p(*SOLUTION), radius=0.16, color=Palette.teal))
            system = VGroup(equation_tex(ROW_ONE, Palette.yellow), equation_tex(second, Palette.blue)).arrange(DOWN, buff=0.3, aligned_edge=RIGHT)
            system.scale(1.4).next_to(plane, UP, buff=0.5)
            panels.add(VGroup(system, *parts))
        panels.arrange(RIGHT, buff=0.8)
        self.add(panels)
        fit_to_frame(self)


class FigPivot(Scene):
    def construct(self):
        plane = make_plane(x_range=(-3, 8, 1), y_range=(-1, 5, 1))
        ghosts = VGroup(
            DashedLine(*equation_line(plane, ROW_ONE).get_start_and_end(), color=Palette.yellow, stroke_width=3, stroke_opacity=0.6),
            DashedLine(*equation_line(plane, ROW_TWO).get_start_and_end(), color=Palette.blue, stroke_width=3, stroke_opacity=0.6),
        )
        final = VGroup(equation_line(plane, (1, 0, 3), Palette.yellow), equation_line(plane, (0, 1, 2), Palette.blue))
        dot = Dot(plane.c2p(*SOLUTION), radius=0.13, color=Palette.teal)
        self.add(plane, ghosts, final, dot)
        fit_to_frame(self)


class FigEchelon(Scene):
    def construct(self):
        mat = augmented(BIG_REDUCED)
        names = VGroup(*[
            MathTex(f"x_{i + 1}", color=Palette.glow if i in (1, 3) else Palette.text_muted, font_size=36).next_to(mat.get_columns()[i], UP, buff=0.35)
            for i in range(4)
        ])
        self.add(mat, names, staircase(mat, BIG_PIVOTS), pivot_boxes(mat, BIG_PIVOTS))
        fit_to_frame(self, margin=1.2)


class Poster(Scene):
    def construct(self):
        plane = make_plane()
        fan = VGroup(*[
            equation_line(plane, combine(ROW_TWO, ROW_ONE, t), Palette.blue, stroke_width=3).set_stroke(opacity=0.18 + 0.5 * t)
            for t in (0.0, 0.2, 0.4, 0.6, 0.8)
        ])
        final = equation_line(plane, (0, 1, 2), Palette.blue, stroke_width=6)
        yellow = equation_line(plane, ROW_ONE, Palette.yellow, stroke_width=6)
        dot = Dot(plane.c2p(*SOLUTION), radius=0.16, color=Palette.teal)
        halo = Dot(plane.c2p(*SOLUTION), radius=0.38, color=Palette.glow, fill_opacity=0.22)
        mat = backed(system_matrix([ROW_ONE, (0, 1, 2)]).scale(1.2), padding=0.3).to_corner(DR, buff=0.6)
        self.add(plane, fan, yellow, final, halo, dot, mat)
