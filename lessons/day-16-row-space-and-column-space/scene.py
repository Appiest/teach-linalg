import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    OrbitingView,
    Palette,
    Timing,
    backed,
    fit_to_frame,
    floor_and_axes,
    make_plane,
    matrix,
    morph_matrix,
    projected_arrow,
    spring,
    spring_soft,
    vector_arrow,
)

A1 = np.array([1.0, 0.0, 1.0])
A2 = np.array([0.0, 1.0, 1.0])
A3 = -A1 + A2
B_POINT = np.array([1.0, -1.0, 0.0])
B_INPUT = (1.0, -1.0)
C_POINT = np.array([1.0, 1.0, 0.0])
C_ABOVE = A1 + A2
ROW_TWO_START = A1 + A2
ROW_TWO_REDUCED = A2

INPUT_CENTER = np.array([-4.75, -0.95, 0.0])
INPUT_UNIT = 0.55
PATCH = 1.5
PATCH_STEPS = [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]
SPACE_ORIGIN = (3.1, -0.2)
SPACE_UNIT = 0.9
SPACE_REACH = ((-3, 3), (-3, 3), (-2, 2))
ELEVATION = 20.0
FACE_ON = 60.0
EDGE_ON = 45 + math.degrees(math.acos(math.tan(math.radians(ELEVATION)) / math.sqrt(2)))

GRID_COLUMNS = [(1, 0), (0, 1), (1, 1)]
THREE_COLUMNS = [[1, 0, -1], [0, 1, 1], [1, 1, 0]]
REDUCTION_STEPS = [
    (r"R_3 \leftarrow R_3 - R_1", [[1, 0, -1], [0, 1, 1], [0, 1, 1]]),
    (r"R_3 \leftarrow R_3 - R_2", [[1, 0, -1], [0, 1, 1], [0, 0, 0]]),
]
B_STEPS = [
    (r"R_3 \leftarrow R_3 - R_1", [[1, 0, 1], [0, 1, -1], [0, 1, -1]]),
    (r"R_3 \leftarrow R_3 - R_2", [[1, 0, 1], [0, 1, -1], [0, 0, 0]]),
]
C_STEPS = [
    (r"R_3 \leftarrow R_3 - R_1", [[1, 0, 1], [0, 1, 1], [0, 1, -1]]),
    (r"R_3 \leftarrow R_3 - R_2", [[1, 0, 1], [0, 1, 1], [0, 0, -2]]),
]
B_ROWS = [[1, 0, 1], [1, 1, 2]]
B_REDUCED = [[1, 0, 1], [0, 1, 1]]
COLUMN_COLORS = [Palette.i_hat, Palette.j_hat, Palette.pink]


def output(x1, x2):
    return x1 * A1 + x2 * A2


def input_plane():
    plane = make_plane(x_range=(-3, 3, 1), y_range=(-3, 3, 1), x_length=6 * INPUT_UNIT, y_length=6 * INPUT_UNIT)
    return plane.shift(INPUT_CENTER - plane.c2p(0, 0))


def colored_matrix(rows, colors=COLUMN_COLORS, by_row=False):
    mat = matrix([[str(entry) for entry in row] for row in rows])
    parts = mat.get_rows() if by_row else mat.get_columns()
    for part, color in zip(parts, colors):
        part.set_color(color)
    return mat


def augmented_with(rows, last_color):
    """A 3 by 3 augmented matrix [A b] with a bar before the last column, A's columns green and red."""
    mat = colored_matrix(rows, colors=[Palette.i_hat, Palette.j_hat, last_color])
    columns = mat.get_columns()
    bar_x = (columns[1].get_right()[0] + columns[2].get_left()[0]) / 2
    brackets = mat.get_brackets()
    bar = Line([bar_x, brackets.get_top()[1] - 0.12, 0], [bar_x, brackets.get_bottom()[1] + 0.12, 0], color=Palette.text, stroke_width=2.5)
    mat.add(bar)
    return mat


def sheet(project, reach=PATCH, opacity=0.2):
    corners = [output(s, t) for s, t in ((-reach, -reach), (reach, -reach), (reach, reach), (-reach, reach))]
    return Polygon(*[project(corner) for corner in corners], stroke_width=0, fill_color=Palette.teal, fill_opacity=opacity)


def image_line(project, index, k, reach=PATCH):
    """The image of the input grid line x1 = k (index 0) or x2 = k (index 1), for the other weight in [-reach, reach]."""
    ends = [(k, -reach), (k, reach)] if index == 0 else [(-reach, k), (reach, k)]
    return Line(project(output(*ends[0])), project(output(*ends[1])), color=Palette.teal, stroke_width=2, stroke_opacity=0.75)


def image_grid(project, reach=PATCH):
    return VGroup(*[image_line(project, index, k, reach) for index in (0, 1) for k in PATCH_STEPS])


def input_line(plane, index, k, reach=PATCH):
    ends = [(k, -reach), (k, reach)] if index == 0 else [(-reach, k), (reach, k)]
    return Line(plane.c2p(*ends[0]), plane.c2p(*ends[1]), color=Palette.teal, stroke_width=2, stroke_opacity=0.75)


def space_tag(project, point, tex, color, direction, font_size=34):
    return backed(MathTex(tex, color=color, font_size=font_size), padding=0.07).next_to(project(point), direction, buff=0.1)


def space_picture(project):
    """Axes, the column-space sheet, its grid and the two column arrows, as one still."""
    return VGroup(
        floor_and_axes(project, SPACE_REACH),
        sheet(project),
        image_grid(project),
        projected_arrow(project, A1, Palette.i_hat),
        projected_arrow(project, A2, Palette.j_hat),
        space_tag(project, A1, r"\mathbf a_1", Palette.i_hat, LEFT),
        space_tag(project, A2, r"\mathbf a_2", Palette.j_hat, DR),
    )


class Lesson(LessonScene):
    day = 16
    title = "Column space and row space"

    def construct(self):
        self.plane = input_plane()
        self.view = OrbitingView(SPACE_ORIGIN, SPACE_UNIT, azimuth=FACE_ON, elevation=ELEVATION)
        pulse = self.open_episode(self.plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.meet_the_matrix()
        line = self.columns_land(line)
        line = self.one_input(line)
        line = self.paint_the_plane(line)
        line = self.name_it(line)
        line = self.test_b(line)
        line = self.test_c(line)
        line = self.edge_on(line)
        line = self.third_column(line)
        line = self.pivot_columns(line)
        line = self.recipe_in_space(line)
        line = self.echelon_columns_leave(line)
        line = self.row_space(line)
        self.close_episode(
            r"The column space is everything $A$ can output.\\"
            r"Its pivot columns, taken from $A$ itself, are a basis.",
            *self.mobjects,
        )

    def project(self, point):
        return self.view.project(point)

    def meet_the_matrix(self):
        self.a_matrix = colored_matrix(GRID_COLUMNS)
        self.a_group = VGroup(MathTex("A", "=", color=Palette.text), self.a_matrix).arrange(RIGHT, buff=0.2)
        self.a_group.move_to(np.array([-4.75, 2.45, 0]))
        self.space = always_redraw(lambda: floor_and_axes(self.project, SPACE_REACH))
        in_tag = MathTex(r"\mathbb R^2", color=Palette.text_muted, font_size=40).next_to(self.plane, UP, buff=0.12).align_to(self.plane, RIGHT)
        out_tag = MathTex(r"\mathbb R^3", color=Palette.text_muted, font_size=40).move_to(np.array([5.9, 2.2, 0]))
        mapsto = MathTex(r"\mathbf x \mapsto A\mathbf x", color=Palette.text, font_size=40).move_to(np.array([-1.55, 0.9, 0]))
        self.tags = VGroup(in_tag, out_tag, mapsto)
        line = self.say(r"This $3\times 2$ matrix sends vectors in $\mathbb R^2$ to $\mathbb R^3$.", hold=0.2)
        self.play(Write(self.a_group), run_time=1.2)
        self.play(Create(self.space), FadeIn(self.tags), run_time=1.6)
        self.wait(Timing.read_short)
        return line

    def columns_land(self, line):
        line = self.say(r"Each basis vector lands on a column of $A$.", line, hold=0.2)
        self.column_arrows = VGroup()
        for index, (target, color, direction) in enumerate(((A1, Palette.i_hat, LEFT), (A2, Palette.j_hat, DR))):
            basis = vector_arrow((1, 0) if index == 0 else (0, 1), color, self.plane, stroke_width=5)
            name = backed(MathTex(rf"\mathbf e_{index + 1}", color=color, font_size=32), padding=0.06)
            name.next_to(basis.get_end(), DOWN if index == 0 else LEFT, buff=0.08)
            self.play(GrowArrow(basis), FadeIn(name), run_time=0.9, rate_func=spring_soft)
            self.play(Indicate(self.a_matrix.get_columns()[index], color=color, scale_factor=1.15), run_time=0.8)
            arrow = always_redraw(lambda t=target, c=color: projected_arrow(self.project, t, c))
            tag = always_redraw(lambda t=target, c=color, i=index, d=direction: space_tag(self.project, t, rf"\mathbf a_{i + 1}", c, d))
            self.play(GrowArrow(arrow), run_time=1.1, rate_func=spring_soft)
            self.play(FadeIn(tag), run_time=0.4)
            self.column_arrows.add(VGroup(basis, name), arrow, tag)
        self.wait(Timing.read_short)
        return line

    def one_input(self, line):
        self.x1, self.x2 = ValueTracker(1.0), ValueTracker(1.0)
        self.x_arrow = always_redraw(lambda: vector_arrow((self.x1.get_value(), self.x2.get_value()), Palette.yellow, self.plane, stroke_width=5))
        self.x_tag = always_redraw(
            lambda: backed(MathTex(r"\mathbf x", color=Palette.yellow, font_size=34), padding=0.06).next_to(
                self.plane.c2p(self.x1.get_value(), self.x2.get_value()), UR, buff=0.06
            )
        )
        self.output_arrow = always_redraw(lambda: projected_arrow(self.project, output(self.x1.get_value(), self.x2.get_value()), Palette.teal, stroke_width=7))
        self.output_tag = always_redraw(
            lambda: space_tag(self.project, output(self.x1.get_value(), self.x2.get_value()), r"A\mathbf x", Palette.teal, RIGHT)
        )
        line = self.say(r"Any input $\mathbf x$ lands at $x_1\mathbf a_1 + x_2\mathbf a_2$.", line, hold=0.2)
        self.play(FadeOut(self.column_arrows[0][1]), FadeOut(self.column_arrows[3][1]), run_time=0.4)
        self.play(GrowArrow(self.x_arrow), FadeIn(self.x_tag), run_time=1.0, rate_func=spring_soft)
        moved = projected_arrow(self.project, A1 + A2, Palette.j_hat, start=A1)
        self.play(TransformFromCopy(self.column_arrows[4], moved), run_time=1.3, rate_func=spring)
        self.play(GrowArrow(self.output_arrow), FadeIn(self.output_tag), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)
        self.play(FadeOut(moved), run_time=0.4)
        return line

    def paint_the_plane(self, line):
        line = self.say(r"Send every input across and the outputs paint a plane.", line, hold=0.2)
        sources = VGroup(*[input_line(self.plane, index, k) for index in (0, 1) for k in PATCH_STEPS])
        self.play(Create(sources), run_time=1.2)
        flights = [Transform(source.copy(), image_line(self.project, index, k)) for source, (index, k) in zip(sources, [(i, k) for i in (0, 1) for k in PATCH_STEPS])]
        self.play(LaggedStart(*flights, lag_ratio=0.12), run_time=3.2, rate_func=smooth)
        flown = [flight.mobject for flight in flights]
        self.remove(*flown)
        self.image = always_redraw(lambda: image_grid(self.project))
        self.sheet = always_redraw(lambda: sheet(self.project))
        self.add(self.image)
        self.bring_to_back(self.sheet)
        self.bring_to_back(self.space)
        self.sfx("shimmer", gain=-6)
        self.play(FadeIn(self.sheet), run_time=1.0)
        self.input_patch = sources
        self.wait(Timing.read_short)
        for target in ((1.5, -1.5), (1.0, 1.0)):
            self.play(self.x1.animate.set_value(target[0]), self.x2.animate.set_value(target[1]), run_time=1.1, rate_func=spring)
        return line

    def name_it(self, line):
        self.col_tag = always_redraw(lambda: space_tag(self.project, output(-1.5, 0), r"\operatorname{Col}A", Palette.teal, RIGHT, font_size=38))
        line = self.say(r"That tilted plane is the \emph{column space} of $A$.", line, hold=0.2)
        self.play(FadeIn(self.col_tag), run_time=0.8)
        self.wait(Timing.read_short)
        self.definition = backed(
            MathTex(r"\operatorname{Col}A", "=", r"\operatorname{Span}\{\mathbf a_1, \mathbf a_2\}", "=", r"\{A\mathbf x\}", font_size=40),
            padding=0.15,
        ).move_to(np.array([2.6, 3.35, 0]))
        self.definition[1].set_color(Palette.teal)
        line = self.say(r"It is the span of the columns, everything $A$ can output.", line, hold=0.2)
        self.play(Write(self.definition), run_time=1.6)
        self.wait(Timing.read_long)
        return line

    def swap_to_augmented(self, point, last_color):
        rows = [[*GRID_COLUMNS[row], int(point[row])] for row in range(3)]
        mat = augmented_with(rows, last_color).move_to(self.a_matrix, aligned_edge=LEFT)
        label = MathTex(r"\begin{bmatrix} A & \mathbf b \end{bmatrix}", color=Palette.text, font_size=36)
        self.play(FadeOut(self.a_group), FadeIn(mat), run_time=0.7)
        return mat, label

    def reduce_in_place(self, mat, steps, color):
        operation = None
        for tex, rows in steps:
            target = augmented_with(rows, color).move_to(mat)
            label = MathTex(tex, color=Palette.text_muted, font_size=34).next_to(mat, RIGHT, buff=0.35)
            if operation is None:
                self.play(FadeIn(label, shift=LEFT * 0.1), run_time=0.4)
            else:
                self.play(FadeOut(operation), FadeIn(label, shift=LEFT * 0.1), run_time=0.4)
            operation = label
            morph_matrix(self, mat, target, run_time=1.1)
            self.wait(0.3)
        return operation

    def test_b(self, line):
        b_dot = Dot(self.project(B_POINT), radius=0.09, color=Palette.yellow)
        b_tag = space_tag(self.project, B_POINT, r"\mathbf b", Palette.yellow, DL)
        self.play(FadeOut(self.output_tag), FadeOut(self.output_arrow), run_time=0.4)
        line = self.say(r"Is $\mathbf b = (1, -1, 0)$ an output? Row reduce $[A\ \mathbf b]$.", line, hold=0.2)
        self.play(GrowFromCenter(b_dot), FadeIn(b_tag), run_time=0.7, rate_func=spring)
        mat, _ = self.swap_to_augmented(B_POINT, Palette.yellow)
        operation = self.reduce_in_place(mat, B_STEPS, Palette.yellow)
        line = self.say(r"No row says $0 = $ something else, so a solution exists.", line, hold=0.2)
        self.play(Indicate(mat.get_rows()[2], color=Palette.teal, scale_factor=1.1), run_time=0.9)
        self.x1.set_value(0.0)
        self.x2.set_value(0.0)
        self.add(self.output_arrow)
        self.play(self.x1.animate.set_value(B_INPUT[0]), self.x2.animate.set_value(B_INPUT[1]), run_time=1.6, rate_func=spring)
        stamp = Circle(radius=0.2, color=Palette.glow, stroke_width=4).move_to(self.project(B_POINT))
        line = self.say(r"The input $(1, -1)$ lands on $\mathbf b$, so $\mathbf b$ is in $\operatorname{Col}A$.", line, hold=0.2)
        self.play(Create(stamp), run_time=0.6)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(mat, operation, stamp, b_tag, self.output_arrow)), b_dot.animate.set_opacity(0.6), run_time=0.6)
        self.b_dot = b_dot
        return line

    def test_c(self, line):
        c_dot = Dot(self.project(C_POINT), radius=0.09, color=Palette.yellow)
        c_tag = space_tag(self.project, C_POINT, r"\mathbf c", Palette.yellow, LEFT)
        line = self.say(r"Now try $\mathbf c = (1, 1, 0)$.", line, hold=0.2)
        self.play(GrowFromCenter(c_dot), FadeIn(c_tag), run_time=0.7, rate_func=spring)
        mat, _ = self.swap_to_augmented(C_POINT, Palette.yellow)
        operation = self.reduce_in_place(mat, C_STEPS, Palette.yellow)
        line = self.say(r"The last row says $0 = -2$, so no input reaches $\mathbf c$.", line, hold=0.2)
        self.play(Indicate(mat.get_rows()[2], color=Palette.glow, scale_factor=1.1), run_time=0.9)
        self.gap = always_redraw(
            lambda: DashedLine(self.project(C_POINT), self.project(C_ABOVE), color=Palette.glow, stroke_width=3, dash_length=0.07)
        )
        self.play(Create(self.gap), run_time=0.8)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(mat, operation)), FadeIn(self.a_group), run_time=0.6)
        self.remove(c_dot, c_tag, self.b_dot)
        self.c_dot = always_redraw(lambda: Dot(self.project(C_POINT), radius=0.09, color=Palette.yellow))
        self.c_tag = always_redraw(lambda: space_tag(self.project, C_POINT, r"\mathbf c", Palette.yellow, LEFT))
        self.b_marker = always_redraw(lambda: Dot(self.project(B_POINT), radius=0.09, color=Palette.yellow, fill_opacity=0.6))
        self.add(self.c_dot, self.c_tag, self.b_marker)
        return line

    def edge_on(self, line):
        line = self.say(r"Turn to see it edge on: the plane is perfectly flat.", line, hold=0.2)
        self.play(self.view.turn_to(EDGE_ON), run_time=2.6, rate_func=smooth)
        self.wait(Timing.read_short)
        line = self.say(r"$\mathbf b$ sits on it, and $\mathbf c$ floats off it.", line, hold=Timing.read_short)
        self.play(self.view.turn_to(FACE_ON), run_time=2.6, rate_func=smooth)
        self.play(FadeOut(VGroup(self.c_dot, self.c_tag, self.b_marker, self.gap)), run_time=0.5)
        return line

    def third_column(self, line):
        self.a3_arrow = always_redraw(lambda: projected_arrow(self.project, A3, Palette.pink))
        self.a3_tag = always_redraw(lambda: space_tag(self.project, A3, r"\mathbf a_3", Palette.pink, DOWN))
        three = colored_matrix(THREE_COLUMNS).move_to(self.a_matrix, aligned_edge=LEFT)
        self.three_group = VGroup(MathTex("A", "=", color=Palette.text).move_to(self.a_group[0]), three)
        line = self.say(r"Give $A$ a third column that already lies in the plane.", line, hold=0.2)
        self.play(FadeOut(self.a_group), FadeIn(self.three_group), run_time=0.8)
        self.play(GrowArrow(self.a3_arrow), run_time=1.2, rate_func=spring_soft)
        self.play(FadeIn(self.a3_tag), run_time=0.4)
        self.wait(Timing.beat)
        line = self.say(r"The span is the same plane, so one column is redundant.", line, hold=Timing.beat)
        self.three = three
        return line

    def pivot_columns(self, line):
        line = self.say(r"Row reduce $A$ to find its pivot columns.", line, hold=0.2)
        working = self.three.copy()
        self.play(FadeOut(self.plane), FadeOut(self.x_arrow), FadeOut(self.x_tag), FadeOut(self.input_patch), FadeOut(self.column_arrows[0]), FadeOut(self.column_arrows[3]), FadeOut(self.tags[0]), FadeOut(self.tags[2]), run_time=0.6)
        self.play(working.animate.next_to(self.three, DOWN, buff=0.35, aligned_edge=LEFT), run_time=0.9, rate_func=spring_soft)
        operation = None
        for tex, rows in REDUCTION_STEPS:
            target = colored_matrix(rows).move_to(working)
            label = MathTex(tex, color=Palette.text_muted, font_size=32).next_to(working, RIGHT, buff=0.3)
            self.play(*([FadeOut(operation)] if operation else []), FadeIn(label, shift=LEFT * 0.1), run_time=0.4)
            operation = label
            morph_matrix(self, working, target, run_time=1.1)
            self.wait(0.3)
        self.play(FadeOut(operation), run_time=0.3)
        frames = VGroup(*[SurroundingRectangle(working.get_columns()[i], color=Palette.glow, buff=0.1, stroke_width=3) for i in (0, 1)])
        line = self.say(r"Columns 1 and 2 hold the pivots.", line, hold=0.2)
        self.play(Create(frames), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"Column 3 of the reduced form reads $-1$ and $1$.", line, hold=0.2)
        self.play(Indicate(working.get_columns()[2][:2], color=Palette.glow, scale_factor=1.2), run_time=1.0)
        self.wait(Timing.beat)
        self.working, self.frames = working, frames
        return line

    def recipe_in_space(self, line):
        relation = backed(MathTex(r"\mathbf a_3", "=", r"-\mathbf a_1", "+", r"\mathbf a_2", font_size=40), padding=0.12)
        relation.next_to(self.working, RIGHT, buff=0.35)
        for part, color in zip(relation[1:], (Palette.pink, Palette.text, Palette.i_hat, Palette.text, Palette.j_hat)):
            part.set_color(color)
        line = self.say(r"Row operations keep that recipe, so it holds for $A$ too.", line, hold=0.2)
        self.play(Write(relation), run_time=1.2)
        first = projected_arrow(self.project, -A1, Palette.i_hat)
        second = projected_arrow(self.project, A3, Palette.j_hat, start=-A1)
        self.play(GrowArrow(first), run_time=1.0, rate_func=spring_soft)
        self.play(GrowArrow(second), run_time=1.1, rate_func=spring_soft)
        stamp = Circle(radius=0.2, color=Palette.glow, stroke_width=4).move_to(self.project(A3))
        self.play(Create(stamp), run_time=0.5)
        self.wait(Timing.read_short)
        line = self.say(r"So the pivot columns of $A$ are a basis for $\operatorname{Col}A$.", line, hold=Timing.read_short)
        self.play(FadeOut(VGroup(first, second, stamp)), run_time=0.5)
        self.relation = relation
        return line

    def echelon_columns_leave(self, line):
        points = ((1, 0, 0), (0, 1, 0))
        muted = [projected_arrow(self.project, point, Palette.purple_gray, stroke_width=6) for point in points]
        line = self.say(r"Take them from $A$ itself: reduced columns can leave the plane.", line, hold=0.2)
        self.play(*[TransformFromCopy(self.working.get_columns()[i], muted[i]) for i in (0, 1)], run_time=1.3, rate_func=spring)
        self.remove(*muted)
        live = VGroup(*[always_redraw(lambda p=point: projected_arrow(self.project, p, Palette.purple_gray, stroke_width=6)) for point in points])
        self.add(live)
        self.play(self.view.turn_to(EDGE_ON), run_time=2.6, rate_func=smooth)
        line = self.say(r"Edge on, the reduced columns stick out of the plane.", line, hold=Timing.read_short)
        self.play(self.view.turn_to(FACE_ON), run_time=2.6, rate_func=smooth)
        self.play(FadeOut(VGroup(live, self.working, self.frames, self.relation)), run_time=0.6)
        return line

    def row_space(self, line):
        self.row_two = ValueTracker(0.0)
        self.b_matrix = colored_matrix(B_ROWS, colors=[Palette.i_hat, Palette.j_hat], by_row=True)
        self.b_group = VGroup(MathTex("B", "=", color=Palette.text), self.b_matrix).arrange(RIGHT, buff=0.2)
        self.b_group.move_to(self.three_group, aligned_edge=LEFT)
        sliding = always_redraw(lambda: projected_arrow(self.project, self.row_two_tip(), Palette.j_hat))
        tags = VGroup(
            always_redraw(lambda: space_tag(self.project, A1, r"\mathbf r_1", Palette.i_hat, UP)),
            always_redraw(lambda: space_tag(self.project, self.row_two_tip(), r"\mathbf r_2", Palette.j_hat, UR)),
        )
        line = self.say(r"Now make two vectors in the plane the rows of $B$.", line, hold=0.2)
        self.play(
            FadeOut(self.three_group),
            FadeOut(VGroup(self.a3_arrow, self.a3_tag, self.column_arrows[2], self.column_arrows[4], self.column_arrows[5])),
            FadeIn(self.b_group),
            run_time=0.8,
        )
        self.play(Indicate(self.b_matrix.get_rows()[1], color=Palette.j_hat, scale_factor=1.1), GrowArrow(sliding), run_time=1.1, rate_func=spring_soft)
        self.play(FadeIn(tags), run_time=0.5)
        row_name = backed(MathTex(r"\operatorname{Row}B", "=", r"\operatorname{Span}\{\mathbf r_1, \mathbf r_2\}", font_size=40), padding=0.15)
        row_name.move_to(self.definition)
        row_name[1].set_color(Palette.teal)
        line = self.say(r"Their span, the \emph{row space} of $B$, is the same plane.", line, hold=0.2)
        self.play(FadeOut(self.definition), FadeIn(row_name), run_time=0.8)
        self.wait(Timing.read_short)
        return self.slide_row(line)

    def row_two_tip(self):
        return ROW_TWO_START + self.row_two.get_value() * (ROW_TWO_REDUCED - ROW_TWO_START)

    def slide_row(self, line):
        target = colored_matrix(B_REDUCED, colors=[Palette.i_hat, Palette.j_hat], by_row=True).move_to(self.b_matrix)
        operation = MathTex(r"R_2 \leftarrow R_2 - R_1", color=Palette.text_muted, font_size=34)
        operation.next_to(self.b_group, DOWN, buff=0.35, aligned_edge=LEFT)
        line = self.say(r"A row operation slides a row but never leaves the plane.", line, hold=0.2)
        self.play(FadeIn(operation, shift=LEFT * 0.1), run_time=0.4)
        morph_matrix(self, self.b_matrix, target, self.row_two.animate.set_value(1.0), run_time=2.0, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"Each new row mixes old rows, and the step can be undone.", line, hold=Timing.read_short)
        frames = VGroup(*[SurroundingRectangle(row, color=Palette.glow, buff=0.1, stroke_width=3) for row in self.b_matrix.get_rows()])
        line = self.say(r"So the nonzero rows of an echelon form are a basis.", line, hold=0.2)
        self.play(Create(frames), run_time=0.8)
        self.wait(Timing.read_long)
        return line


class FigColumnSpace(Scene):
    def construct(self):
        view = OrbitingView((0, 0), 1.0, azimuth=FACE_ON, elevation=ELEVATION)
        picture = space_picture(view.project)
        b_dot = Dot(view.project(B_POINT), radius=0.09, color=Palette.yellow)
        c_dot = Dot(view.project(C_POINT), radius=0.09, color=Palette.yellow)
        gap = DashedLine(view.project(C_POINT), view.project(C_ABOVE), color=Palette.glow, stroke_width=3, dash_length=0.07)
        tags = VGroup(
            space_tag(view.project, B_POINT, r"\mathbf b", Palette.yellow, DL),
            space_tag(view.project, C_POINT, r"\mathbf c", Palette.yellow, LEFT),
            space_tag(view.project, output(-1.5, 0), r"\operatorname{Col}A", Palette.teal, RIGHT, font_size=38),
        )
        self.add(picture, gap, b_dot, c_dot, tags)
        fit_to_frame(self)


class FigInputToOutput(Scene):
    def construct(self):
        plane = input_plane()
        view = OrbitingView(SPACE_ORIGIN, SPACE_UNIT, azimuth=FACE_ON, elevation=ELEVATION)
        sources = VGroup(*[input_line(plane, index, k) for index in (0, 1) for k in PATCH_STEPS])
        basis = VGroup(vector_arrow((1, 0), Palette.i_hat, plane, stroke_width=5), vector_arrow((0, 1), Palette.j_hat, plane, stroke_width=5))
        mapsto = MathTex(r"\mathbf x \mapsto A\mathbf x", color=Palette.text, font_size=40).move_to(np.array([-1.3, 1.2, 0]))
        a_group = VGroup(MathTex("A", "=", color=Palette.text), colored_matrix(GRID_COLUMNS)).arrange(RIGHT, buff=0.2).move_to(np.array([-4.75, 2.45, 0]))
        self.add(plane, sources, basis, space_picture(view.project), mapsto, a_group)
        fit_to_frame(self)


class FigPivotColumns(Scene):
    def construct(self):
        original = colored_matrix(THREE_COLUMNS)
        reduced = colored_matrix(REDUCTION_STEPS[-1][1])
        row = VGroup(MathTex("A", "=", color=Palette.text), original, MathTex(r"\sim", color=Palette.text), reduced).arrange(RIGHT, buff=0.3)
        frames = VGroup(
            *[SurroundingRectangle(original.get_columns()[i], color=Palette.glow, buff=0.1, stroke_width=3) for i in (0, 1)],
            *[DashedVMobject(SurroundingRectangle(reduced.get_columns()[i], color=Palette.text_muted, buff=0.1, stroke_width=2)) for i in (0, 1)],
        )
        relation = MathTex(r"\mathbf a_3", "=", r"-\mathbf a_1", "+", r"\mathbf a_2", font_size=44).next_to(row, DOWN, buff=0.6)
        for part, color in zip(relation, (Palette.pink, Palette.text, Palette.i_hat, Palette.text, Palette.j_hat)):
            part.set_color(color)
        self.add(row, frames, relation)
        fit_to_frame(self, margin=0.8)


class FigRowSpace(Scene):
    def construct(self):
        view = OrbitingView((0, 0), 1.0, azimuth=FACE_ON, elevation=ELEVATION)
        project = view.project
        before = projected_arrow(project, ROW_TWO_START, Palette.j_hat, stroke_width=4).set_opacity(0.4)
        path = DashedLine(project(ROW_TWO_START), project(ROW_TWO_REDUCED), color=Palette.glow, stroke_width=3, dash_length=0.08)
        self.add(
            floor_and_axes(project, SPACE_REACH),
            sheet(project),
            image_grid(project),
            path,
            projected_arrow(project, A1, Palette.i_hat),
            before,
            projected_arrow(project, ROW_TWO_REDUCED, Palette.j_hat),
            space_tag(project, A1, r"\mathbf r_1", Palette.i_hat, LEFT),
            space_tag(project, ROW_TWO_START, r"\mathbf r_2", Palette.j_hat, UP).set_opacity(0.6),
            space_tag(project, ROW_TWO_REDUCED, r"\mathbf r_2 - \mathbf r_1", Palette.j_hat, RIGHT),
            space_tag(project, output(-1.5, 0), r"\operatorname{Row}B", Palette.teal, RIGHT, font_size=38),
        )
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = input_plane()
        view = OrbitingView(SPACE_ORIGIN, SPACE_UNIT, azimuth=FACE_ON, elevation=ELEVATION)
        sources = VGroup(*[input_line(plane, index, k) for index in (0, 1) for k in PATCH_STEPS])
        x_arrow = vector_arrow((1, 1), Palette.yellow, plane, stroke_width=5)
        out = projected_arrow(view.project, output(1, 1), Palette.teal, stroke_width=7)
        name = backed(MathTex(r"\operatorname{Col}A", color=Palette.teal, font_size=64)).move_to(np.array([2.6, 3.0, 0]))
        a_group = VGroup(MathTex("A", "=", color=Palette.text), colored_matrix(GRID_COLUMNS)).arrange(RIGHT, buff=0.2).move_to(np.array([-4.75, 2.45, 0]))
        mapsto = MathTex(r"\mathbf x \mapsto A\mathbf x", color=Palette.text, font_size=40).move_to(np.array([-1.55, 0.9, 0]))
        self.add(plane, sources, space_picture(view.project), x_arrow, out, name, a_group, mapsto)
