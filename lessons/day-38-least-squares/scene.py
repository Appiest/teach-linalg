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
    equation_line,
    fit_to_frame,
    floor_and_axes,
    make_plane,
    matrix,
    projected_arrow,
    spring,
    spring_soft,
)

XS = (0, 1, 2)
YS = (0, 4, 2)
A1 = np.array([1.0, 1.0, 1.0])
A2 = np.array([0.0, 1.0, 2.0])
Y_VEC = np.array([0.0, 4.0, 2.0])
BEST = (1.0, 1.0)
TWO_POINT_LINE = (0.0, 1.0)
FLAT_LINE = (2.0, 0.0)
TRIAL_LINES = [(0.0, 1.5)]
SQUARE_SIDES = (-1, -1, 1)

PLOT_UNIT = 0.9
PLOT_ORIGIN = np.array([-4.8, -1.4, 0.0])
SPACE_ORIGIN = (1.75, -1.95)
SPACE_UNIT = 1.02
SPACE_REACH = ((0, 3), (0, 3), (0, 4))
AZIMUTH = -75.0
ELEVATION = 25.0
SHEET_S = (-0.3, 2.3)
SHEET_T = (-0.3, 1.6)
COL_TAG_POINT = 2.3 * A1 + 0.6 * A2


def predicted(beta):
    return [beta[0] + beta[1] * x for x in XS]


def residuals(beta):
    return [y - p for y, p in zip(YS, predicted(beta))]


def sum_of_squares(beta):
    return sum(r * r for r in residuals(beta))


def prediction_vector(beta):
    return beta[0] * A1 + beta[1] * A2


def data_plane():
    plane = make_plane(x_range=(-2, 4, 1), y_range=(-1, 5, 1), x_length=6 * PLOT_UNIT, y_length=6 * PLOT_UNIT)
    return plane.shift(PLOT_ORIGIN - plane.c2p(0, 0))


def data_dots(plane):
    return VGroup(*[Dot(plane.c2p(x, y), radius=0.1, color=Palette.yellow) for x, y in zip(XS, YS)]).set_z_index(5)


def fit_line(plane, beta):
    return equation_line(plane, (beta[1], -1, -beta[0]), color=Palette.teal, stroke_width=5)


def residual_segments(plane, beta):
    group = VGroup()
    for x, y, p in zip(XS, YS, predicted(beta)):
        if abs(y - p) > 1e-3:
            group.add(Line(plane.c2p(x, p), plane.c2p(x, y), color=Palette.pink, stroke_width=5))
    return group.set_z_index(3)


def residual_squares(plane, beta):
    group = VGroup()
    for x, y, p, side in zip(XS, YS, predicted(beta), SQUARE_SIDES):
        width = side * abs(y - p)
        if abs(width) < 1e-3:
            continue
        corners = [(x, p), (x, y), (x + width, y), (x + width, p)]
        group.add(Polygon(*[plane.c2p(*corner) for corner in corners], stroke_width=0, fill_color=Palette.pink, fill_opacity=0.3))
    return group


def total_readout(beta, prefix=None):
    parts = [MathTex(r"r_1^2 + r_2^2 + r_3^2", "=", color=Palette.pink, font_size=38)]
    if prefix is not None:
        parts.insert(0, prefix)
    parts.append(DecimalNumber(sum_of_squares(beta), num_decimal_places=2, color=Palette.pink, font_size=38))
    row = VGroup(*parts).arrange(RIGHT, buff=0.18)
    return backed(row, padding=0.14).move_to(np.array([PLOT_ORIGIN[0] + 1.0 * PLOT_UNIT, 3.55, 0]))


def length_prefix():
    return MathTex(r"\|\mathbf y - X\boldsymbol\beta\|^2", "=", color=Palette.pink, font_size=38)


def column_sheet(project):
    corners = [s * A1 + t * A2 for s, t in ((SHEET_S[0], SHEET_T[0]), (SHEET_S[1], SHEET_T[0]), (SHEET_S[1], SHEET_T[1]), (SHEET_S[0], SHEET_T[1]))]
    return Polygon(*[project(corner) for corner in corners], stroke_width=0, fill_color=Palette.teal, fill_opacity=0.16)


def sheet_grid(project):
    lines = VGroup()
    for s in (0, 1, 2):
        lines.add(Line(project(s * A1 + SHEET_T[0] * A2), project(s * A1 + SHEET_T[1] * A2)))
    for t in (0, 0.5, 1):
        lines.add(Line(project(SHEET_S[0] * A1 + t * A2), project(SHEET_S[1] * A1 + t * A2)))
    return lines.set_stroke(Palette.teal, width=1.6, opacity=0.5)


def space_tag(project, point, tex, color, direction, font_size=36):
    return backed(MathTex(tex, color=color, font_size=font_size), padding=0.07).next_to(project(point), direction, buff=0.12)


def column_arrows(project):
    return VGroup(
        projected_arrow(project, A1, Palette.i_hat),
        projected_arrow(project, A2, Palette.j_hat),
        space_tag(project, A1, r"\mathbf a_1", Palette.i_hat, DOWN),
        space_tag(project, A2, r"\mathbf a_2", Palette.j_hat, UP),
    )


def residual_vector(project, beta):
    return Line(project(prediction_vector(beta)), project(Y_VEC), color=Palette.pink, stroke_width=6).set_z_index(4)


def prediction_arrow(project, beta):
    return projected_arrow(project, prediction_vector(beta), Palette.teal, stroke_width=6)


def prediction_tag(project, beta, tex=r"X\boldsymbol\beta"):
    return space_tag(project, prediction_vector(beta), tex, Palette.teal, DR)


def right_angle_mark(project, size=0.32):
    foot = prediction_vector(BEST)
    up = (Y_VEC - foot) / np.linalg.norm(Y_VEC - foot)
    along = -foot / np.linalg.norm(foot)
    corners = [foot + size * up, foot + size * (up + along), foot + size * along]
    mark = VMobject(color=Palette.glow, stroke_width=4).set_points_as_corners([project(corner) for corner in corners])
    return mark.set_z_index(6)


def colored_x_matrix():
    mat = matrix([["1", "0"], ["1", "1"], ["1", "2"]])
    mat.get_columns()[0].set_color(Palette.i_hat)
    mat.get_columns()[1].set_color(Palette.j_hat)
    return mat


def system_equation():
    beta = matrix([[r"\beta_0"], [r"\beta_1"]])
    heights = matrix([[str(y)] for y in YS], color=Palette.yellow)
    return VGroup(colored_x_matrix(), beta, MathTex("=", color=Palette.text), heights).arrange(RIGHT, buff=0.2)


def point_equation(x, y):
    eq = MathTex(r"\beta_0", "+", str(x), r"\,\beta_1", "=", str(y), color=Palette.text, font_size=44)
    eq[0].set_color(Palette.text)
    eq[2].set_color(Palette.j_hat)
    eq[5].set_color(Palette.yellow)
    return eq


def data_picture(plane, beta):
    return VGroup(plane, residual_squares(plane, beta), fit_line(plane, beta), residual_segments(plane, beta), data_dots(plane))


def data_projector(view):
    """Draw the second entry upward, so the residual (-1, 2, -1) rises off Col X like b above the plane in Lay."""
    return lambda point: view.project((point[0], point[2], point[1]))


def space_picture(view, beta, marked=True):
    project = data_projector(view)
    parts = VGroup(
        floor_and_axes(view.project, SPACE_REACH),
        column_sheet(project),
        sheet_grid(project),
        column_arrows(project),
        projected_arrow(project, Y_VEC, Palette.yellow),
        space_tag(project, Y_VEC, r"\mathbf y", Palette.yellow, UR),
        prediction_arrow(project, beta),
        residual_vector(project, beta),
        prediction_tag(project, beta, r"X\hat{\boldsymbol\beta}"),
        space_tag(project, COL_TAG_POINT, r"\operatorname{Col}X", Palette.teal, RIGHT),
    )
    if marked:
        parts.add(right_angle_mark(project))
    return parts


class Lesson(LessonScene):
    day = 38
    title = "Least squares"

    def construct(self):
        self.plane = data_plane()
        self.view = OrbitingView(SPACE_ORIGIN, SPACE_UNIT, azimuth=AZIMUTH, elevation=ELEVATION)
        self.beta0, self.beta1 = ValueTracker(FLAT_LINE[0]), ValueTracker(FLAT_LINE[1])
        pulse = self.open_episode(self.plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.meet_the_data()
        line = self.no_exact_line(line)
        line = self.residuals(line)
        line = self.stack_the_heights(line)
        line = self.settle(line)
        line = self.normal_equations(line)
        line = self.general_case(line)
        self.close_episode(
            r"When $A\mathbf x = \mathbf b$ has no solution, project $\mathbf b$ onto $\operatorname{Col}A$.\\"
            r"The weights that get there solve $A^TA\hat{\mathbf x} = A^T\mathbf b$.",
            *self.mobjects,
        )

    def project(self, point):
        return data_projector(self.view)(point)

    def beta(self):
        return (self.beta0.get_value(), self.beta1.get_value())

    def move_beta(self, target, rate_func=spring, run_time=1.8, *extra):
        self.play(
            self.beta0.animate(rate_func=rate_func).set_value(target[0]),
            self.beta1.animate(rate_func=rate_func).set_value(target[1]),
            *extra,
            run_time=run_time,
        )

    def meet_the_data(self):
        self.dots = data_dots(self.plane)
        self.coordinates = VGroup(
            *[
                backed(MathTex(f"({x}, {y})", color=Palette.yellow, font_size=32), padding=0.06).next_to(dot, direction, buff=0.12)
                for x, y, dot, direction in zip(XS, YS, self.dots, (LEFT, UP, RIGHT))
            ]
        )
        line = self.say(r"Three measurements, and we want one line through them.", hold=0.2)
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in self.dots], lag_ratio=0.3), run_time=1.2)
        self.play(FadeIn(self.coordinates), run_time=0.6)
        self.wait(Timing.read_short)

        self.model = MathTex("y", "=", r"\beta_0", "+", r"\beta_1", "x", color=Palette.text, font_size=52)
        self.model[2].set_color(Palette.i_hat)
        self.model[4].set_color(Palette.j_hat)
        self.model.move_to(np.array([3.4, 3.2, 0]))
        line = self.say(r"A line $y = \beta_0 + \beta_1 x$ has two numbers to choose.", line, hold=0.2)
        self.play(Write(self.model), run_time=1.2)
        self.wait(Timing.read_short)

        line = self.say(r"Each point asks the line to pass through it.", line, hold=0.2)
        self.equations = VGroup(*[point_equation(x, y) for x, y in zip(XS, YS)]).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        self.equations.move_to(np.array([3.4, 1.0, 0]))
        for dot, eq in zip(self.dots, self.equations):
            self.play(Indicate(dot, color=Palette.glow, scale_factor=1.6), FadeIn(eq, shift=RIGHT * 0.2), run_time=1.0)
        self.wait(Timing.beat)

        self.system = system_equation().move_to(np.array([3.4, 0.9, 0]))
        line = self.say(r"Together they form one system, $X\boldsymbol\beta = \mathbf y$.", line, hold=0.2)
        self.play(FadeTransform(self.equations, self.system), run_time=1.4)
        self.wait(Timing.read_short)
        return line

    def no_exact_line(self, line):
        attempt = fit_line(self.plane, TWO_POINT_LINE)
        miss = residual_segments(self.plane, TWO_POINT_LINE)
        line = self.say(r"A line through two of the points misses the third.", line, hold=0.2)
        self.play(Create(attempt), run_time=1.2)
        self.play(Create(miss), run_time=0.8)
        self.wait(Timing.read_short)
        line = self.say(r"No line hits all three, so $X\boldsymbol\beta = \mathbf y$ has no solution.", line, hold=Timing.read_short)
        self.attempt = VGroup(attempt, miss)
        return line

    def residuals(self, line):
        self.line = always_redraw(lambda: fit_line(self.plane, self.beta()))
        self.misses = always_redraw(lambda: residual_segments(self.plane, self.beta()))
        line = self.say(r"So settle for a line that misses by as little as possible.", line, hold=0.2)
        self.play(FadeOut(self.attempt), FadeOut(self.coordinates), Create(self.line), run_time=1.2)
        self.wait(Timing.beat)
        line = self.say(r"Each vertical miss is a \emph{residual}: observed minus predicted.", line, hold=0.2)
        self.play(Create(self.misses), run_time=1.0)
        self.wait(Timing.read_short)

        self.squares = always_redraw(lambda: residual_squares(self.plane, self.beta()))
        self.readout = always_redraw(lambda: total_readout(self.beta()))
        line = self.say(r"Square the residuals and add them up.", line, hold=0.2)
        self.sfx("pop", gain=-6)
        self.play(FadeIn(self.squares), FadeIn(self.readout), run_time=1.0)
        self.wait(Timing.read_short)

        line = self.say(r"\emph{Least squares} picks the line with the smallest total.", line, hold=0.2)
        for target in TRIAL_LINES:
            self.move_beta(target)
            self.wait(1.2)
        return line

    def stack_the_heights(self, line):
        self.space = always_redraw(lambda: floor_and_axes(self.view.project, SPACE_REACH))
        line = self.say(r"Now stack the three heights into one vector $\mathbf y$.", line, hold=0.2)
        heights = self.system[3].copy()
        self.remove(self.system)
        self.add(heights)
        self.play(FadeOut(self.model), FadeOut(self.system[:3]), run_time=0.6)
        self.play(heights.animate.move_to(np.array([-0.2, 1.2, 0])), run_time=0.9, rate_func=spring)
        self.play(Create(self.space), run_time=1.4)
        self.y_arrow = always_redraw(lambda: projected_arrow(self.project, Y_VEC, Palette.yellow))
        self.y_tag = always_redraw(lambda: space_tag(self.project, Y_VEC, r"\mathbf y", Palette.yellow, UR))
        landing = self.y_tag.copy()
        self.play(GrowArrow(self.y_arrow), FadeTransform(heights, landing), run_time=1.4, rate_func=spring_soft)
        self.remove(landing)
        self.add(self.y_tag)
        self.wait(Timing.read_short)

        self.sheet = always_redraw(lambda: column_sheet(self.project))
        self.sheet_lines = always_redraw(lambda: sheet_grid(self.project))
        self.columns = always_redraw(lambda: column_arrows(self.project))
        self.col_tag = always_redraw(lambda: space_tag(self.project, COL_TAG_POINT, r"\operatorname{Col}X", Palette.teal, RIGHT))
        line = self.say(r"Every prediction $X\boldsymbol\beta$ lies on the plane $\operatorname{Col}X$.", line, hold=0.2)
        self.play(FadeIn(self.columns), run_time=1.0)
        self.bring_to_back(self.space)
        self.add(self.sheet, self.sheet_lines)
        self.bring_to_back(self.sheet_lines, self.sheet, self.space)
        self.sfx("shimmer", gain=-6)
        self.play(FadeIn(self.sheet), Create(self.sheet_lines), FadeIn(self.col_tag), run_time=1.2)
        self.wait(Timing.read_short)

        self.guess = always_redraw(lambda: prediction_arrow(self.project, self.beta()))
        self.guess_tag = always_redraw(lambda: prediction_tag(self.project, self.beta()))
        self.gap = always_redraw(lambda: residual_vector(self.project, self.beta()))
        line = self.say(r"The residual vector joins $X\boldsymbol\beta$ to $\mathbf y$.", line, hold=0.2)
        self.play(GrowArrow(self.guess), FadeIn(self.guess_tag), run_time=1.0, rate_func=spring_soft)
        self.play(Create(self.gap), run_time=0.9)
        self.wait(Timing.read_short)

        line = self.say(r"Its squared length is the same sum of squares.", line, hold=0.2)
        longer = always_redraw(lambda: total_readout(self.beta(), prefix=length_prefix()))
        self.play(FadeOut(self.readout), FadeIn(longer), run_time=0.8)
        self.readout = longer
        self.wait(Timing.read_short)
        return line

    def settle(self, line):
        line = self.say(r"Now let the line settle into its best position.", line, hold=0.2)
        self.move_beta(BEST, spring_soft, 3.2, self.view.turn_to(AZIMUTH + 14))
        self.wait(Timing.beat)
        mark = always_redraw(lambda: right_angle_mark(self.project))
        line = self.say(r"The best residual is perpendicular to the plane.", line, hold=0.2)
        self.sfx("tick", gain=-2)
        self.play(Create(mark), run_time=0.6)
        self.wait(Timing.read_short)
        best_tag = always_redraw(lambda: prediction_tag(self.project, BEST, r"X\hat{\boldsymbol\beta}"))
        line = self.say(r"So $X\hat{\boldsymbol\beta}$ is the projection of $\mathbf y$ onto $\operatorname{Col}X$.", line, hold=0.2)
        self.play(FadeOut(self.guess_tag), FadeIn(best_tag), run_time=0.8)
        self.wait(Timing.read_long)
        self.mark = mark
        return line

    def normal_equations(self, line):
        self.play(FadeOut(VGroup(self.plane, self.dots, self.line, self.misses, self.squares, self.readout)), run_time=0.8)
        self.remove(self.line, self.misses, self.squares, self.readout)
        first = MathTex(r"\mathbf a_1", r"\cdot", r"(\mathbf y - X\hat{\boldsymbol\beta})", "=", "0", color=Palette.text, font_size=52)
        second = MathTex(r"\mathbf a_2", r"\cdot", r"(\mathbf y - X\hat{\boldsymbol\beta})", "=", "0", color=Palette.text, font_size=52)
        for eq, color in ((first, Palette.i_hat), (second, Palette.j_hat)):
            eq[0].set_color(color)
            eq[2].set_color(Palette.pink)
        pair = VGroup(first, second).arrange(DOWN, buff=0.3).move_to(np.array([-3.7, 2.75, 0]))
        line = self.say(r"Perpendicular to the plane means perpendicular to both columns.", line, hold=0.2)
        self.play(Write(first), run_time=1.1)
        self.play(Write(second), run_time=1.1)
        self.wait(Timing.read_short)

        transpose = MathTex(r"X^T", r"(\mathbf y - X\hat{\boldsymbol\beta})", "=", r"\mathbf 0", color=Palette.text, font_size=52)
        transpose[1].set_color(Palette.pink)
        transpose.next_to(pair, DOWN, buff=0.45)
        line = self.say(r"Stack the two dot products into one equation.", line, hold=0.2)
        self.play(FadeIn(transpose, shift=DOWN * 0.3), run_time=1.1, rate_func=spring_soft)
        self.wait(Timing.read_short)

        normal = MathTex(r"X^TX", r"\hat{\boldsymbol\beta}", "=", r"X^T\mathbf y", color=Palette.text, font_size=62)
        normal.next_to(transpose, DOWN, buff=0.5)
        frame = SurroundingRectangle(normal, color=Palette.glow, buff=0.18, stroke_width=3)
        line = self.say(r"These are the \emph{normal equations}.", line, hold=0.2)
        self.play(FadeIn(normal, shift=DOWN * 0.3), run_time=1.1, rate_func=spring_soft)
        self.play(Create(frame), run_time=0.6)
        self.wait(Timing.read_short)
        self.derivation = VGroup(pair, transpose, normal, frame)
        return self.solve_numbers(line)

    def solve_numbers(self, line):
        gram = matrix([["3", "3"], ["3", "5"]])
        right = matrix([["6"], ["8"]], color=Palette.yellow)
        numbers = VGroup(gram, MathTex(r"\hat{\boldsymbol\beta}", "=", color=Palette.text), right).arrange(RIGHT, buff=0.2)
        answer = MathTex(r"\hat{\boldsymbol\beta}", "=", color=Palette.text)
        solved = VGroup(answer, matrix([["1"], ["1"]], color=Palette.teal)).arrange(RIGHT, buff=0.2)
        row = VGroup(numbers, solved).arrange(RIGHT, buff=0.6).scale(0.95)
        row.next_to(self.derivation, DOWN, buff=0.4).set_x(-3.6)
        line = self.say(r"Here they give $\hat{\boldsymbol\beta} = (1,\ 1)$, so the best line is $y = 1 + x$.", line, hold=0.2)
        self.play(FadeIn(numbers, shift=UP * 0.15), run_time=0.9)
        self.play(FadeIn(solved, shift=LEFT * 0.2), run_time=0.9, rate_func=spring)
        self.wait(Timing.read_long)
        self.derivation.add(row)
        return line

    def general_case(self, line):
        general = MathTex(r"A^TA", r"\hat{\mathbf x}", "=", r"A^T\mathbf b", color=Palette.text, font_size=64)
        general.move_to(np.array([-3.6, 0.4, 0]))
        frame = SurroundingRectangle(general, color=Palette.glow, buff=0.22, stroke_width=3)
        line = self.say(r"Any system $A\mathbf x = \mathbf b$ with no solution works the same way.", line, hold=0.2)
        self.play(FadeOut(self.derivation), run_time=0.6)
        self.play(FadeIn(general, shift=UP * 0.2), Create(frame), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_long)
        return line


class FigResiduals(Scene):
    def construct(self):
        plane = data_plane()
        tags = VGroup(
            *[
                backed(MathTex(rf"r_{index + 1}", color=Palette.pink, font_size=34), padding=0.06).next_to(
                    plane.c2p(x + 0.5 * side * abs(r), (y + p) / 2), ORIGIN, buff=0
                )
                for index, (x, y, p, r, side) in enumerate(zip(XS, YS, predicted(BEST), residuals(BEST), SQUARE_SIDES))
            ]
        )
        formula = backed(MathTex(r"y = 1 + x", color=Palette.teal, font_size=40)).move_to(plane.c2p(2.75, 0.55))
        self.add(data_picture(plane, BEST), tags, formula)
        fit_to_frame(self)


class FigProjection(Scene):
    def construct(self):
        view = OrbitingView((0, 0), SPACE_UNIT, azimuth=AZIMUTH + 14, elevation=ELEVATION)
        self.add(space_picture(view, BEST))
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = data_plane()
        view = OrbitingView(SPACE_ORIGIN, SPACE_UNIT, azimuth=AZIMUTH + 14, elevation=ELEVATION)
        self.add(data_picture(plane, BEST), space_picture(view, BEST))
