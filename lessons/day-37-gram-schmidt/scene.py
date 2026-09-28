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
    parallelepiped,
    projected_arrow,
    projected_right_angle,
    spring,
    spring_soft,
)

X = [np.array(entries, dtype=float) for entries in ((1, 1, 0), (1, 0, 1), (0, 1, 1))]
V1 = X[0]
SHADOW_2 = 0.5 * V1
V2 = X[1] - SHADOW_2
SHADOW_31 = 0.5 * V1
SHADOW_32 = V2 / 3
V3 = X[2] - SHADOW_31 - SHADOW_32
V = [V1, V2, V3]
U = [vector / np.linalg.norm(vector) for vector in V]
SHADOWS = (np.zeros(3), SHADOW_2, SHADOW_31 + SHADOW_32)
COLORS = (Palette.yellow, Palette.blue, Palette.pink)
SHADOW = Palette.purple_gray

VIEW_ORIGIN = (-3.0, -1.35)
VIEW_UNIT = 3.85
ELEVATION = 22.0
AZIMUTH = -8.0
SPACE_REACH = ((-1, 1), (-1, 1), (0, 1))
PANEL_LEFT = 2.25
PANEL_TOP = 3.55

A_ROWS = [[1, 1, 0], [1, 0, 1], [0, 1, 1]]
R_SYMBOLS = [["r_{11}", "r_{12}", "r_{13}"], ["0", "r_{22}", "r_{23}"], ["0", "0", "r_{33}"]]
R_NUMBERS = [[r"\sqrt2", r"\tfrac{1}{\sqrt2}", r"\tfrac{1}{\sqrt2}"], ["0", r"\tfrac{3}{\sqrt6}", r"\tfrac{1}{\sqrt6}"], ["0", "0", r"\tfrac{2}{\sqrt3}"]]


def tinted(tex_parts, colors, font_size=42):
    formula = MathTex(*tex_parts, font_size=font_size)
    for part, color in zip(formula, colors):
        part.set_color(color)
    return formula


def small_column(entries, color, font_size=36):
    col = Matrix([[entry] for entry in entries], v_buff=0.55, bracket_h_buff=0.1, element_to_mobject_config={"font_size": font_size})
    col.get_brackets().scale(font_size / 40)
    return col.set_color(color)


def row_of(*parts, buff=0.14, font_size=40):
    return VGroup(*[MathTex(part, color=Palette.text, font_size=font_size) if isinstance(part, str) else part for part in parts]).arrange(RIGHT, buff=buff)


def safe_arrow(project, coords, color, start=(0, 0, 0), stroke_width=6):
    if np.linalg.norm(np.asarray(coords, dtype=float) - np.asarray(start, dtype=float)) < 0.03:
        return VMobject()
    return projected_arrow(project, coords, color, start=start, stroke_width=stroke_width)


def dashed(project, start, end, color, opacity=0.85, width=3):
    if np.linalg.norm(np.asarray(end, dtype=float) - np.asarray(start, dtype=float)) < 0.03:
        return VMobject()
    return DashedLine(project(start), project(end), color=color, stroke_width=width, stroke_opacity=opacity, dash_length=0.09)


def tag(project, point, tex, color, font_size=40, reach=0.42, nudge=(0, 0)):
    """A label just beyond `point`, pushed away from the origin along the screen direction to it."""
    tip = project(point)
    away = tip - project((0, 0, 0))
    length = np.linalg.norm(away)
    direction = away / length if length > 1e-6 else UP
    label = backed(MathTex(tex, color=color, font_size=font_size), padding=0.06)
    return label.move_to(tip + reach * direction + np.array([nudge[0], nudge[1], 0]))


def span_line(project, direction, color, low=-0.75, high=1.5):
    return Line(project(low * direction), project(high * direction), color=color, stroke_width=3, stroke_opacity=0.4)


def span_sheet_2d(project, first, second, box=((-0.6, 1.3), (-0.45, 1.2))):
    first, second = first / np.linalg.norm(first), second / np.linalg.norm(second)
    corners = [box[0][0] * first + box[1][0] * second, box[0][1] * first + box[1][0] * second, box[0][1] * first + box[1][1] * second, box[0][0] * first + box[1][1] * second]
    return Polygon(*[project(corner) for corner in corners], stroke_color=Palette.teal, stroke_width=1.5, stroke_opacity=0.6, fill_color=Palette.teal, fill_opacity=0.14)


def weight_equations():
    colors = {r"\mathbf u_1": Palette.yellow, r"\mathbf u_2": Palette.blue, r"\mathbf u_3": Palette.pink}
    specs = [
        (r"\mathbf x_1", "=", "r_{11}", r"\mathbf u_1"),
        (r"\mathbf x_2", "=", "r_{12}", r"\mathbf u_1", "+", "r_{22}", r"\mathbf u_2"),
        (r"\mathbf x_3", "=", "r_{13}", r"\mathbf u_1", "+", "r_{23}", r"\mathbf u_2", "+", "r_{33}", r"\mathbf u_3"),
    ]
    rows = VGroup()
    for index, spec in enumerate(specs):
        row = MathTex(*spec, font_size=44, color=Palette.text)
        row[0].set_color(COLORS[index])
        for part in row:
            part.set_color(colors.get(part.tex_string, part.get_color()))
        rows.add(row)
    rows.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
    for row in rows[1:]:
        row.shift(RIGHT * (rows[0][1].get_center()[0] - row[1].get_center()[0]))
    return rows.move_to([-3.2, -0.6, 0])

def r_matrix(entries, highlight_zeros=True):
    mat = Matrix(entries, v_buff=0.8, h_buff=1.15, bracket_h_buff=0.14).set_color(Palette.text)
    if highlight_zeros:
        for row, col in ((1, 0), (2, 0), (2, 1)):
            mat.get_rows()[row][col].set_color(Palette.glow)
    return mat


class Stage:
    """The three arrows and their shadows, all drawn through one orbiting view."""

    def __init__(self, view):
        self.view = view
        self.progress = [ValueTracker(1.0), ValueTracker(0.0), ValueTracker(0.0)]
        self.unit = ValueTracker(0.0)

    def project(self, point):
        return self.view.project(point)

    def current(self, index):
        base = X[index] - self.progress[index].get_value() * SHADOWS[index]
        return base * (1 + self.unit.get_value() * (1 / np.linalg.norm(V[index]) - 1))

    def left(self, index):
        return 1 - self.progress[index].get_value()

    def arrow(self, index):
        return always_redraw(lambda: safe_arrow(self.project, self.current(index), COLORS[index]))

    def label(self, index, tex):
        return always_redraw(lambda: tag(self.project, self.current(index), tex, COLORS[index]))

    def axes(self):
        return always_redraw(lambda: floor_and_axes(self.project, SPACE_REACH))

    def line_of_v1(self):
        return always_redraw(lambda: span_line(self.project, V1, Palette.yellow))

    def sheet(self):
        return always_redraw(lambda: span_sheet_2d(self.project, V1, V2))

    def second_shadow(self):
        return VGroup(
            always_redraw(lambda: safe_arrow(self.project, self.left(1) * SHADOW_2, SHADOW, stroke_width=7)),
            always_redraw(lambda: dashed(self.project, self.current(1), self.left(1) * SHADOW_2, Palette.blue)),
        )

    def third_shadow(self):
        foot = lambda: self.left(2) * (SHADOW_31 + SHADOW_32)  # noqa: E731
        return VGroup(
            always_redraw(lambda: safe_arrow(self.project, self.left(2) * SHADOW_31, SHADOW, stroke_width=7)),
            always_redraw(lambda: safe_arrow(self.project, self.left(2) * SHADOW_32, SHADOW, stroke_width=7)),
            always_redraw(lambda: dashed(self.project, self.left(2) * SHADOW_31, foot(), SHADOW, opacity=0.6, width=2)),
            always_redraw(lambda: dashed(self.project, self.left(2) * SHADOW_32, foot(), SHADOW, opacity=0.6, width=2)),
            always_redraw(lambda: dashed(self.project, self.current(2), foot(), Palette.pink)),
        )

    def corner(self, first, second):
        return always_redraw(lambda: projected_right_angle(self.project, self.current(first), self.current(second), size=0.13))


class Lesson(LessonScene):
    day = 37
    title = "Gram–Schmidt"

    def construct(self):
        pulse = self.open_episode()
        self.play(FadeOut(pulse), run_time=0.5)
        self.view = OrbitingView(VIEW_ORIGIN, VIEW_UNIT, azimuth=AZIMUTH - 14, elevation=ELEVATION)
        self.stage = Stage(self.view)
        line = self.meet_basis()
        line = self.keep_first(line)
        line = self.straighten_second(line)
        line = self.straighten_third(line)
        line = self.check_pairs(line)
        line = self.normalize(line)
        line = self.factor(line)
        self.close_episode(
            r"Gram--Schmidt subtracts each vector's shadow on the ones before it.\\"
            r"What is left meets all of them at right angles.",
            *self.drawn_mobjects(),
        )

    def drawn_mobjects(self):
        empty = [mobject for mobject in self.mobjects if not any(part.has_points() for part in mobject.get_family())]
        self.remove(*empty)
        return list(self.mobjects)

    def panel(self, *rows, buff=0.3):
        group = VGroup(*rows).arrange(DOWN, buff=buff, aligned_edge=LEFT)
        return group.move_to([PANEL_LEFT + group.width / 2, PANEL_TOP - group.height / 2, 0])

    def clear_stage(self, line):
        leaving = [mobject for mobject in self.mobjects if mobject is not line]
        for mobject in leaving:
            mobject.clear_updaters()
        self.play(*[FadeOut(mobject) for mobject in leaving if any(part.has_points() for part in mobject.get_family())], run_time=0.7)
        self.remove(*leaving)

    def rename(self, index, tex):
        old = self.labels[index]
        self.labels[index] = self.stage.label(index, tex)
        self.play(FadeOut(old), FadeIn(self.labels[index]), run_time=0.6)

    def meet_basis(self):
        stage = self.stage
        self.axes = stage.axes()
        self.arrows = [stage.arrow(index) for index in range(3)]
        self.labels = [stage.label(index, rf"\mathbf x_{index + 1}") for index in range(3)]
        line = self.say(r"These three arrows form a basis for $\mathbb R^3$.", hold=0.2)
        self.play(Create(self.axes), run_time=1.0)
        for arrow, label in zip(self.arrows, self.labels):
            self.play(GrowArrow(arrow), FadeIn(label), run_time=0.8, rate_func=spring_soft)
        self.add(*self.labels)
        line = self.say(r"But no two of them meet at a right angle.", line, hold=0.2)
        self.play(self.view.turn_to(AZIMUTH), run_time=2.0, rate_func=smooth)
        self.wait(Timing.beat)
        line = self.say(r"Gram--Schmidt straightens them, one vector at a time.", line, hold=Timing.read_long)
        return line

    def keep_first(self, line):
        self.v1_line = self.stage.line_of_v1()
        line = self.say(r"Keep the first one as it is: $\mathbf v_1 = \mathbf x_1$.", line, hold=0.2)
        self.rename(0, r"\mathbf v_1")
        self.bring_to_back(self.axes)
        self.play(Create(self.v1_line), run_time=0.8)
        self.bring_to_back(self.v1_line, self.axes)
        self.wait(Timing.beat)
        return line

    def second_formula(self):
        general = tinted(
            (r"\mathbf v_2", "=", r"\mathbf x_2", "-", r"\frac{\mathbf x_2\cdot\mathbf v_1}{\mathbf v_1\cdot\mathbf v_1}", r"\mathbf v_1"),
            (Palette.blue, Palette.text, Palette.blue, Palette.text, SHADOW, Palette.yellow),
        )
        weight = tinted((r"\frac{\mathbf x_2\cdot\mathbf v_1}{\mathbf v_1\cdot\mathbf v_1}", "=", r"\frac{1}{2}"), (SHADOW, Palette.text, SHADOW))
        numbers = row_of(
            "=", small_column(["1", "0", "1"], Palette.blue), r"-\tfrac12", small_column(["1", "1", "0"], Palette.yellow), "=",
            small_column([r"\tfrac12", r"-\tfrac12", "1"], Palette.blue),
        )
        numbers[2].set_color(SHADOW)
        return self.panel(general, weight.shift(RIGHT * 0.5), numbers.shift(RIGHT * 0.5))

    def straighten_second(self, line):
        stage = self.stage
        shadow = stage.second_shadow()
        shadow_tag = always_redraw(lambda: tag(stage.project, SHADOW_2, r"\tfrac12\mathbf v_1", SHADOW, font_size=36, reach=0.0, nudge=(0.25, -0.42)))
        general, weight, numbers = self.second_formula()
        line = self.say(r"$\mathbf x_2$ casts a shadow on the line through $\mathbf v_1$.", line, hold=0.2)
        self.play(Create(shadow[1]), run_time=0.8)
        self.play(GrowArrow(shadow[0]), FadeIn(shadow_tag), run_time=0.9, rate_func=spring_soft)
        self.play(Write(general), run_time=1.2)
        self.play(FadeIn(weight, shift=UP * 0.1), run_time=0.7)
        self.wait(Timing.beat)
        line = self.say(r"That shadow is the part of $\mathbf x_2$ that leans along $\mathbf v_1$.", line)
        line = self.say(r"Subtract it, and $\mathbf x_2$ swings up to a right angle.", line, hold=0.2)
        self.play(FadeOut(shadow_tag), run_time=0.4)
        self.sfx("slide", gain=-2)
        self.play(stage.progress[1].animate.set_value(1.0), run_time=2.0, rate_func=spring)
        self.remove(*shadow)
        self.corner_12 = stage.corner(0, 1)
        self.play(Create(self.corner_12), run_time=0.5)
        self.rename(1, r"\mathbf v_2")
        self.play(FadeIn(numbers, shift=UP * 0.1), run_time=0.9)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(general, weight, numbers)), run_time=0.5)
        return line

    def third_formula(self):
        first = tinted(
            (r"\mathbf v_3", "=", r"\mathbf x_3", "-", r"\frac{\mathbf x_3\cdot\mathbf v_1}{\mathbf v_1\cdot\mathbf v_1}", r"\mathbf v_1"),
            (Palette.pink, Palette.text, Palette.pink, Palette.text, SHADOW, Palette.yellow),
        )
        second = tinted(("-", r"\frac{\mathbf x_3\cdot\mathbf v_2}{\mathbf v_2\cdot\mathbf v_2}", r"\mathbf v_2"), (Palette.text, SHADOW, Palette.blue))
        second.next_to(first, DOWN, buff=0.25).align_to(first[3], LEFT)
        general = VGroup(first, second)
        numbers = row_of(
            "=", small_column(["0", "1", "1"], Palette.pink), r"-\tfrac12", small_column(["1", "1", "0"], Palette.yellow),
            r"-\tfrac13", small_column([r"\tfrac12", r"-\tfrac12", "1"], Palette.blue),
        )
        numbers[2].set_color(SHADOW)
        numbers[4].set_color(SHADOW)
        result = row_of("=", small_column([r"-\tfrac23", r"\tfrac23", r"\tfrac23"], Palette.pink))
        return self.panel(general, numbers.shift(RIGHT * 0.5), result.shift(RIGHT * 0.5), buff=0.25)

    def straighten_third(self, line):
        stage = self.stage
        self.sheet = stage.sheet()
        shadow = stage.third_shadow()
        tags = VGroup(
            always_redraw(lambda: tag(stage.project, SHADOW_31, r"\tfrac12\mathbf v_1", SHADOW, font_size=36, reach=0.0, nudge=(0.25, -0.42))),
            always_redraw(lambda: tag(stage.project, SHADOW_32, r"\tfrac13\mathbf v_2", SHADOW, font_size=36, reach=0.0, nudge=(-0.75, -0.1))),
        )
        general, numbers, result = self.third_formula()
        line = self.say(r"$\mathbf v_1$ and $\mathbf v_2$ span a plane.", line, hold=0.2)
        self.play(FadeIn(self.sheet), FadeOut(self.v1_line), run_time=0.9)
        self.bring_to_back(self.sheet, self.axes)
        line = self.say(r"$\mathbf x_3$ casts a shadow on each of them.", line, hold=0.2)
        self.play(Create(shadow[4]), run_time=0.8)
        self.play(GrowArrow(shadow[0]), GrowArrow(shadow[1]), FadeIn(tags), run_time=1.0, rate_func=spring_soft)
        self.play(Create(shadow[2]), Create(shadow[3]), run_time=0.6)
        self.play(Write(general), run_time=1.4)
        self.play(FadeIn(numbers, shift=UP * 0.1), run_time=0.8)
        line = self.say(r"Subtract both shadows, and $\mathbf x_3$ stands straight up.", line, hold=0.2)
        self.play(FadeOut(tags), run_time=0.4)
        self.sfx("slide", gain=-2)
        self.play(stage.progress[2].animate.set_value(1.0), run_time=2.2, rate_func=spring)
        self.remove(*shadow)
        self.corners_3 = VGroup(stage.corner(0, 2), stage.corner(1, 2))
        self.play(Create(self.corners_3), run_time=0.6)
        self.rename(2, r"\mathbf v_3")
        self.play(FadeIn(result, shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(general, numbers, result)), run_time=0.5)
        return line

    def check_pairs(self, line):
        checks = VGroup(
            tinted((r"\mathbf v_1", r"\cdot", r"\mathbf v_2", "=", "0"), (Palette.yellow, Palette.text, Palette.blue, Palette.text, Palette.text)),
            tinted((r"\mathbf v_1", r"\cdot", r"\mathbf v_3", "=", "0"), (Palette.yellow, Palette.text, Palette.pink, Palette.text, Palette.text)),
            tinted((r"\mathbf v_2", r"\cdot", r"\mathbf v_3", "=", "0"), (Palette.blue, Palette.text, Palette.pink, Palette.text, Palette.text)),
        )
        self.checks = self.panel(*checks, buff=0.28)
        line = self.say(r"Now every pair has dot product zero.", line, hold=0.2)
        self.play(FadeOut(self.sheet), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(check, shift=UP * 0.1) for check in checks], lag_ratio=0.35), run_time=1.4)
        self.play(self.view.turn_to(AZIMUTH - 40), run_time=2.4, rate_func=smooth)
        self.play(self.view.turn_to(AZIMUTH), run_time=2.0, rate_func=smooth)
        self.play(FadeOut(self.checks), run_time=0.4)
        return line

    def unit_formulas(self):
        general = tinted((r"\mathbf u_k", "=", r"\frac{\mathbf v_k}{\lVert\mathbf v_k\rVert}"), (Palette.teal, Palette.text, Palette.text))
        rows = VGroup(
            tinted((r"\mathbf u_1", r"= \tfrac{1}{\sqrt2}\,(1,\ 1,\ 0)"), (Palette.yellow, Palette.text), font_size=40),
            tinted((r"\mathbf u_2", r"= \tfrac{1}{\sqrt6}\,(1,\ -1,\ 2)"), (Palette.blue, Palette.text), font_size=40),
            tinted((r"\mathbf u_3", r"= \tfrac{1}{\sqrt3}\,(-1,\ 1,\ 1)"), (Palette.pink, Palette.text), font_size=40),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        return self.panel(general, rows)

    def normalize(self, line):
        stage = self.stage
        general, rows = self.unit_formulas()
        cube = always_redraw(lambda: parallelepiped(stage.project, *[stage.current(index) for index in range(3)], color=Palette.teal, opacity=0.08, stroke_width=1.5))
        line = self.say(r"Divide each one by its length to make it a unit vector.", line, hold=0.2)
        self.play(Write(general), run_time=1.0)
        self.sfx("slide", gain=-2)
        self.play(stage.unit.animate.set_value(1.0), run_time=1.8, rate_func=spring)
        for index in range(3):
            old = self.labels[index]
            self.labels[index] = stage.label(index, rf"\mathbf u_{index + 1}")
            self.play(FadeOut(old), FadeIn(self.labels[index]), run_time=0.35)
        self.bring_to_back(cube, self.axes)
        self.play(FadeIn(cube), FadeIn(rows, shift=UP * 0.1), run_time=1.0)
        line = self.say(r"They sit like the corner of a unit cube: an \emph{orthonormal} basis.", line, hold=0.2)
        self.play(self.view.turn_to(AZIMUTH + 10), run_time=2.2, rate_func=smooth)
        self.wait(Timing.beat)
        return line

    def factor_headers(self):
        a_mat = Matrix(A_ROWS, v_buff=0.62, h_buff=0.8, bracket_h_buff=0.14).set_color(Palette.text)
        for part, color in zip(a_mat.get_columns(), COLORS):
            part.set_color(color)
        a_group = VGroup(MathTex("A", "=", color=Palette.text, font_size=44), a_mat).arrange(RIGHT, buff=0.2)
        q_group = tinted(
            ("Q", "=", r"\big[\,", r"\mathbf u_1", r"\;\;", r"\mathbf u_2", r"\;\;", r"\mathbf u_3", r"\,\big]"),
            (Palette.text, Palette.text, Palette.text, COLORS[0], Palette.text, COLORS[1], Palette.text, COLORS[2], Palette.text),
            font_size=44,
        )
        headers = VGroup(a_group, q_group).arrange(RIGHT, buff=1.4)
        return headers.move_to([-2.3, 2.3, 0])

    def factor(self, line):
        headers = self.factor_headers()
        equations = weight_equations()
        line = self.say(r"Stack the $\mathbf x$'s into $A$ and the $\mathbf u$'s into $Q$.", line, hold=0.2)
        self.clear_stage(line)
        self.play(FadeIn(headers, shift=UP * 0.1), run_time=0.9)
        line = self.say(r"Each $\mathbf x_k$ uses only $\mathbf u_1$ through $\mathbf u_k$.", line, hold=0.2)
        for row in equations:
            self.play(Write(row), run_time=0.8)
        self.wait(Timing.beat)
        symbolic = r_matrix(R_SYMBOLS)
        r_group = VGroup(MathTex("R", "=", color=Palette.text, font_size=44), symbolic).arrange(RIGHT, buff=0.2).move_to([3.7, -0.6, 0])
        line = self.say(r"Those weights fill an upper triangular $R$, so $A = QR$.", line, hold=0.2)
        self.play_weights_into(equations, symbolic, r_group)
        self.wait(Timing.read_short)
        numeric = r_matrix(R_NUMBERS).move_to(symbolic)
        numeric_label = MathTex("R", "=", "Q^T\\!A", "=", color=Palette.text, font_size=44).next_to(numeric, LEFT, buff=0.2)
        line = self.say(r"Since $Q^TQ = I$, you can compute $R = Q^TA$.", line, hold=0.2)
        self.play(FadeOut(equations), FadeTransform(r_group[0], numeric_label), FadeTransform(symbolic, numeric), run_time=1.2)
        self.play(VGroup(numeric_label, numeric).animate.move_to([0, -0.6, 0]), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_long)
        return line

    def play_weights_into(self, equations, symbolic, r_group):
        places = {"r_{11}": (0, 0), "r_{12}": (0, 1), "r_{22}": (1, 1), "r_{13}": (0, 2), "r_{23}": (1, 2), "r_{33}": (2, 2)}
        sources = [part for row in equations for part in row if part.tex_string in places]
        targets = [symbolic.get_rows()[places[part.tex_string][0]][places[part.tex_string][1]] for part in sources]
        zeros = VGroup(*[symbolic.get_rows()[row][col] for row, col in ((1, 0), (2, 0), (2, 1))])
        self.play(FadeIn(r_group[0]), FadeIn(symbolic.get_brackets()), run_time=0.5)
        self.play(*[TransformFromCopy(source, target) for source, target in zip(sources, targets)], run_time=1.4)
        self.play(FadeIn(zeros, scale=1.3), run_time=0.7, rate_func=spring)
        self.add(r_group)


def still_stage(azimuth=AZIMUTH):
    view = OrbitingView(VIEW_ORIGIN, VIEW_UNIT, azimuth=azimuth, elevation=ELEVATION)
    return Stage(view)


class FigSecondStep(Scene):
    def construct(self):
        stage = still_stage()
        project = stage.project
        ghost = projected_arrow(project, X[1], Palette.blue, stroke_width=4).set_opacity(0.4)
        self.add(floor_and_axes(project, SPACE_REACH), span_line(project, V1, Palette.yellow))
        self.add(dashed(project, X[1], SHADOW_2, Palette.blue), dashed(project, X[1], V2, Palette.blue, opacity=0.5))
        self.add(ghost, projected_arrow(project, SHADOW_2, SHADOW, stroke_width=7), projected_arrow(project, V1, Palette.yellow), projected_arrow(project, V2, Palette.blue))
        self.add(projected_right_angle(project, V1, V2, size=0.13))
        self.add(
            tag(project, V1, r"\mathbf v_1", Palette.yellow),
            tag(project, X[1], r"\mathbf x_2", Palette.blue),
            tag(project, V2, r"\mathbf v_2", Palette.blue),
            tag(project, SHADOW_2, r"\tfrac12\mathbf v_1", SHADOW, font_size=36, reach=0.0, nudge=(0.25, -0.42)),
        )
        fit_to_frame(self)


class FigThirdStep(Scene):
    def construct(self):
        stage = still_stage()
        project = stage.project
        foot = SHADOW_31 + SHADOW_32
        self.add(floor_and_axes(project, SPACE_REACH), span_sheet_2d(project, V1, V2))
        self.add(dashed(project, SHADOW_31, foot, SHADOW, opacity=0.6, width=2), dashed(project, SHADOW_32, foot, SHADOW, opacity=0.6, width=2))
        self.add(dashed(project, X[2], foot, Palette.pink), dashed(project, X[2], V3, Palette.pink, opacity=0.5))
        self.add(projected_arrow(project, X[2], Palette.pink, stroke_width=4).set_opacity(0.4))
        self.add(*[projected_arrow(project, point, SHADOW, stroke_width=7) for point in (SHADOW_31, SHADOW_32)])
        self.add(*[projected_arrow(project, vector, color) for vector, color in zip(V, COLORS)])
        self.add(projected_right_angle(project, V1, V3, size=0.13), projected_right_angle(project, V2, V3, size=0.13), projected_right_angle(project, V1, V2, size=0.13))
        self.add(
            tag(project, V1, r"\mathbf v_1", Palette.yellow),
            tag(project, V2, r"\mathbf v_2", Palette.blue),
            tag(project, X[2], r"\mathbf x_3", Palette.pink),
            tag(project, V3, r"\mathbf v_3", Palette.pink),
        )
        fit_to_frame(self)


class FigQrWeights(Scene):
    def construct(self):
        equations = weight_equations()
        symbolic = r_matrix(R_SYMBOLS)
        r_group = VGroup(MathTex("R", "=", color=Palette.text, font_size=44), symbolic).arrange(RIGHT, buff=0.2)
        VGroup(equations, r_group).arrange(RIGHT, buff=1.2)
        self.add(equations, r_group)
        fit_to_frame(self, margin=0.8)


class Poster(Scene):
    def construct(self):
        view = OrbitingView((-1.2, -1.2), 3.7, azimuth=AZIMUTH, elevation=ELEVATION)
        project = view.project
        foot = SHADOW_31 + SHADOW_32
        self.add(floor_and_axes(project, SPACE_REACH), span_sheet_2d(project, V1, V2))
        self.add(dashed(project, X[2], foot, Palette.pink), dashed(project, X[2], V3, Palette.pink, opacity=0.5))
        self.add(projected_arrow(project, X[2], Palette.pink, stroke_width=5).set_opacity(0.4))
        self.add(*[projected_arrow(project, point, SHADOW, stroke_width=8) for point in (SHADOW_31, SHADOW_32)])
        self.add(*[projected_arrow(project, vector, color, stroke_width=8) for vector, color in zip(V, COLORS)])
        self.add(projected_right_angle(project, V1, V3, size=0.13), projected_right_angle(project, V2, V3, size=0.13), projected_right_angle(project, V1, V2, size=0.13))
