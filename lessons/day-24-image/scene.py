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
    matrix,
    origin_pulse,
    projected_arrow,
    projected_axes,
    spring,
    spring_soft,
)

A = np.array([[1.0, 0.0, -1.0], [0.0, 1.0, 1.0], [1.0, 1.0, 0.0]])
A_ROWS = [[1, 0, -1], [0, 1, 1], [1, 1, 0]]
A1 = A[:, 0]
A2 = A[:, 1]
KERNEL = np.array([1.0, -1.0, 1.0])
KERNEL_REACH = 1.1
X = np.array([2.0, 0.0, 1.0])
FLOOR_PART = np.array([1.0, 1.0, 0.0])
T_X = A @ X
U_OUT = np.array([2.0, -1.0, 1.0])
W_OUT = np.array([-1.0, 2.0, 1.0])
B_POINT = np.array([1.0, 1.0, 0.0])
B_ABOVE = A @ FLOOR_PART
INPUT_DOTS = [
    (1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (-1, 0, 1),
    (1, 0, -1), (0, -1, -1), (-1, -1, 0), (-1, 1, 1), (1, -1, 1),
]
HEXAGON = [(2, 0), (0, 2), (-2, 2), (-2, 0), (0, -2), (2, -2)]
FLOOR_STEPS = [-2, -1, 0, 1, 2]

SPACE_ORIGIN = (2.3, -0.3)
SPACE_UNIT = 1.5
SPACE_REACH = ((-2, 2), (-2, 2), (-2, 2))
ELEVATION = 28.0
FACE_ON = 60.0
SWUNG = 35.0
PANEL_LEFT = -6.7
COLUMN_COLORS = [Palette.i_hat, Palette.j_hat, Palette.pink]
KERNEL_COLOR = Palette.pink
RANGE_COLOR = Palette.teal
INPUT_COLOR = Palette.blue


def moved(point, amount):
    """The point partway along its straight path from p to Ap."""
    point = np.asarray(point, dtype=float)
    return (1 - amount) * point + amount * (A @ point)


def colored_matrix(rows):
    mat = matrix([[str(entry) for entry in row] for row in rows])
    for part, color in zip(mat.get_columns(), COLUMN_COLORS):
        part.set_color(color)
    return mat


def range_sheet(project, opacity=0.22):
    corners = [s * A1 + t * A2 for s, t in HEXAGON]
    return Polygon(*[project(corner) for corner in corners], stroke_color=RANGE_COLOR, stroke_width=2, stroke_opacity=0.8, fill_color=RANGE_COLOR, fill_opacity=opacity)


def range_tag(project, above=False):
    """The range label, right of the sheet's lowest corner on screen, or above its highest corner."""
    corners = [s * A1 + t * A2 for s, t in HEXAGON]
    heights = [project(corner)[1] for corner in corners]
    pick = max if above else min
    corner = corners[heights.index(pick(heights))]
    return space_tag(project, corner, r"\operatorname{range}T", RANGE_COLOR, UP if above else RIGHT)


def floor_segments():
    """Grid lines of the floor x3 = 0, clipped to the hexagon |s|, |t|, |s + t| <= 2 that A carries onto the sheet."""
    segments = []
    for k in FLOOR_STEPS:
        low, high = max(-2, -2 - k), min(2, 2 - k)
        segments.append(((k, low, 0), (k, high, 0)))
        segments.append(((low, k, 0), (high, k, 0)))
    return segments


def floor_grid(project, amount, color=INPUT_COLOR, opacity=0.7):
    lines = VGroup()
    for start, end in floor_segments():
        lines.add(Line(project(moved(start, amount)), project(moved(end, amount)), color=color, stroke_width=2, stroke_opacity=opacity))
    return lines


def floor_fill(project, amount, color=INPUT_COLOR, opacity=0.12):
    corners = [moved((s, t, 0), amount) for s, t in HEXAGON]
    return Polygon(*[project(corner) for corner in corners], stroke_width=0, fill_color=color, fill_opacity=opacity)


def kernel_line(project, amount, width=6):
    reach = KERNEL_REACH * (1 - amount)
    if reach < 0.02:
        return VGroup()
    return Line(project(-reach * KERNEL), project(reach * KERNEL), color=KERNEL_COLOR, stroke_width=width)


def space_tag(project, point, tex, color, direction, font_size=36):
    return backed(MathTex(tex, color=color, font_size=font_size), padding=0.07).next_to(project(point), direction, buff=0.12)


def split_arrows(project, amount):
    """The input x drawn as its floor part plus its kernel part, all carried partway to their images."""
    floor_tip = project(moved(FLOOR_PART, amount))
    x_tip = project(moved(X, amount))
    parts = VGroup(projected_arrow(project, moved(FLOOR_PART, amount), INPUT_COLOR, stroke_width=9))
    if np.linalg.norm(x_tip - floor_tip) > 0.08:
        parts.add(Line(floor_tip, x_tip, color=KERNEL_COLOR, stroke_width=7))
    parts.add(projected_arrow(project, moved(X, amount), Palette.yellow, stroke_width=5))
    return parts


def count_lines():
    kernel = MathTex(r"\dim\ker T", "=", "1", font_size=42)
    image = MathTex(r"\dim\operatorname{range}T", "=", "2", font_size=42)
    total = MathTex("1", "+", "2", "=", "3", "=", r"\dim\mathbb R^3", font_size=42)
    for part in (kernel[0], kernel[2], total[0]):
        part.set_color(KERNEL_COLOR)
    for part in (image[0], image[2], total[2]):
        part.set_color(RANGE_COLOR)
    return VGroup(kernel, image, total).arrange(DOWN, buff=0.4, aligned_edge=LEFT)


def budget_cells(count, filled_colors, size=0.62):
    """A row of square cells; the first len(filled_colors) are filled with those colors, the rest stay outlined."""
    cells = VGroup()
    for index in range(count):
        cell = Square(size, color=Palette.text_muted, stroke_width=2)
        cells.add(cell)
        if index < len(filled_colors):
            cell.set_fill(filled_colors[index], opacity=0.9).set_stroke(width=0)
    return cells.arrange(RIGHT, buff=0.08)


def budget_row(map_tex, kernel_dim, domain_dim, codomain_dim, y):
    """A map's name, its domain cells split pink and teal, an arrow, and its codomain cells, all on one row."""
    name = MathTex(map_tex, color=Palette.text, font_size=40)
    domain = budget_cells(domain_dim, [KERNEL_COLOR] * kernel_dim + [RANGE_COLOR] * (domain_dim - kernel_dim))
    codomain = budget_cells(codomain_dim, [])
    arrow = MathTex(r"\xrightarrow{\;T\;}", color=Palette.text_muted, font_size=44)
    name.move_to([-3.4, y, 0])
    domain.next_to([-1.0, y, 0], RIGHT, buff=0)
    arrow.next_to(domain, RIGHT, buff=0.35)
    codomain.next_to(arrow, RIGHT, buff=0.35)
    return VGroup(name, domain, arrow, codomain)


def budget_headers(row):
    """Labels V and W above a budget row's domain and codomain cells."""
    return VGroup(
        MathTex(r"\dim V", color=Palette.text_muted, font_size=34).next_to(row[1], UP, buff=0.3),
        MathTex(r"\dim W", color=Palette.text_muted, font_size=34).next_to(row[3], UP, buff=0.3),
    )


def filled_copy(cell, color):
    return Square(cell.width, stroke_width=0, fill_color=color, fill_opacity=0.9).move_to(cell)


def cross_mark(cell):
    return VGroup(
        Line(cell.get_corner(UL), cell.get_corner(DR), color=Palette.glow, stroke_width=5),
        Line(cell.get_corner(DL), cell.get_corner(UR), color=Palette.glow, stroke_width=5),
    ).scale(0.6)


class Lesson(LessonScene):
    day = 24
    title = "Image (range)"

    def construct(self):
        pulse = self.open_episode()
        self.play(FadeOut(pulse), run_time=0.5)
        self.view = OrbitingView(SPACE_ORIGIN, SPACE_UNIT, azimuth=SWUNG, elevation=ELEVATION)
        line = self.meet_the_map()
        line = self.send_inputs(line)
        line = self.name_the_range(line)
        line = self.closure(line)
        line = self.not_onto(line)
        line = self.split_inputs(line)
        line = self.collapse(line)
        line = self.count(line)
        line = self.theorem(line)
        line = self.budgets(line)
        self.close_episode(
            r"The range is every output $T$ can make, and it is a subspace.\\"
            r"Kernel and range share the input: $\dim\ker T + \dim\operatorname{range}T = \dim V$.",
            *self.mobjects,
        )

    def project(self, point):
        return self.view.project(point)

    def clear_stage(self, keep=(), run_time=0.7):
        kept = {member for mobject in keep for member in mobject.get_family()}
        leaving = [mobject for mobject in self.mobjects if kept.isdisjoint(mobject.get_family())]
        for mobject in leaving:
            mobject.clear_updaters()
        self.play(*[FadeOut(mobject) for mobject in leaving], run_time=run_time)
        self.remove(*leaving)

    def meet_the_map(self):
        self.amount = ValueTracker(0.0)
        name = MathTex(r"T(\mathbf x)", "=", "A", r"\mathbf x", ",", r"\quad A", "=", color=Palette.text, font_size=44)
        self.a_matrix = colored_matrix(A_ROWS)
        self.map_group = VGroup(name, self.a_matrix).arrange(RIGHT, buff=0.2).to_corner(UL, buff=0.45)
        self.axes = always_redraw(lambda: projected_axes(self.project, SPACE_REACH, labels=("x_1", "x_2", "x_3"), floor=False))
        self.dots = always_redraw(self.input_dots)
        line = self.say(r"Day 18's matrix gives a map $T$ from $\mathbb R^3$ to $\mathbb R^3$.", hold=0.2)
        self.play(Write(self.map_group), run_time=1.3)
        self.play(Create(self.axes), run_time=1.0)
        self.play(FadeIn(self.dots, lag_ratio=0.1), run_time=1.0)
        self.play(self.view.turn_to(FACE_ON), run_time=2.2, rate_func=smooth)
        return line

    def input_dots(self):
        amount = self.amount.get_value()
        color = interpolate_color(ManimColor(INPUT_COLOR), ManimColor(RANGE_COLOR), amount)
        return VGroup(*[Dot(self.project(moved(point, amount)), radius=0.085, color=color) for point in INPUT_DOTS])

    def send_inputs(self, line):
        line = self.say(r"Send each input $\mathbf x$ to its output $A\mathbf x$.", line, hold=0.2)
        self.sfx("slide", gain=-2)
        self.play(self.amount.animate.set_value(1.0), run_time=3.0, rate_func=smooth)
        self.glow = origin_pulse().move_to(self.project((0, 0, 0)))
        self.play(GrowFromCenter(self.glow), run_time=0.6, rate_func=spring)
        self.sheet = range_sheet(self.project)
        self.range_tag = range_tag(self.project)
        line = self.say(r"Every output lands on one tilted plane.", line, hold=0.2)
        self.bring_to_back(self.sheet)
        self.bring_to_back(self.axes)
        self.sfx("shimmer", gain=-6)
        self.play(FadeIn(self.sheet), FadeIn(self.range_tag), run_time=1.0)
        self.wait(Timing.read_short)
        return line

    def name_the_range(self, line):
        definition = MathTex(r"\operatorname{range}T", "=", r"\{\,T(\mathbf x) : \mathbf x \in \mathbb R^3\,\}", font_size=36)
        column_space = MathTex("=", r"\operatorname{Col}A", font_size=36)
        definition[0].set_color(RANGE_COLOR)
        column_space[1].set_color(RANGE_COLOR)
        definition.next_to(self.map_group, DOWN, buff=0.55).set_x(PANEL_LEFT, LEFT)
        column_space.next_to(definition, DOWN, buff=0.3).align_to(definition[1], LEFT)
        line = self.say(r"The set of all outputs is the \emph{range}, or \emph{image}, of $T$.", line, hold=0.2)
        self.play(Write(definition), run_time=1.4)
        self.wait(Timing.read_short)
        columns = VGroup(projected_arrow(self.project, A1, Palette.i_hat), projected_arrow(self.project, A2, Palette.j_hat))
        line = self.say(r"Every $A\mathbf x$ combines the columns, so the range is $\operatorname{Col}A$.", line, hold=0.2)
        self.play(Write(column_space), Indicate(self.a_matrix.get_columns()[:2], color=Palette.glow, scale_factor=1.08), run_time=1.2)
        self.play(*[GrowArrow(arrow) for arrow in columns], run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)
        self.play(FadeOut(columns), FadeOut(self.dots), run_time=0.6)
        self.remove(columns, self.dots)
        self.panel = VGroup(definition, column_space)
        return line

    def closure(self, line):
        u_arrow = projected_arrow(self.project, U_OUT, Palette.yellow)
        w_arrow = projected_arrow(self.project, W_OUT, Palette.blue)
        u_tag = space_tag(self.project, U_OUT, r"T(\mathbf u)", Palette.yellow, UP)
        w_tag = space_tag(self.project, W_OUT, r"T(\mathbf w)", Palette.blue, UP)
        total = U_OUT + W_OUT
        moved_w = projected_arrow(self.project, total, Palette.blue, start=U_OUT)
        sum_arrow = projected_arrow(self.project, total, Palette.teal, stroke_width=7)
        sum_tag = space_tag(self.project, total, r"T(\mathbf u + \mathbf w)", Palette.teal, UP)
        rules = VGroup(
            MathTex(r"T(\mathbf u) + T(\mathbf w)", "=", r"T(\mathbf u + \mathbf w)", font_size=38),
            MathTex(r"c\,T(\mathbf u)", "=", r"T(c\,\mathbf u)", font_size=38),
            MathTex(r"\mathbf 0", "=", r"T(\mathbf 0)", font_size=38),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        rules.next_to(self.panel, DOWN, buff=0.55).set_x(PANEL_LEFT, LEFT)
        line = self.say(r"Take two outputs, $T(\mathbf u)$ and $T(\mathbf w)$.", line, hold=0.2)
        self.play(FadeOut(self.range_tag), GrowArrow(u_arrow), GrowArrow(w_arrow), FadeIn(u_tag), FadeIn(w_tag), run_time=1.2, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Their sum is $T(\mathbf u + \mathbf w)$, so it is an output too.", line, hold=0.2)
        self.play(TransformFromCopy(w_arrow, moved_w), run_time=1.2, rate_func=spring)
        self.play(GrowArrow(sum_arrow), FadeIn(sum_tag), run_time=1.0, rate_func=spring_soft)
        self.play(Write(rules[0]), run_time=1.2)
        self.wait(Timing.read_short)
        line = self.say(r"Multiples and zero stay too, so the range is a subspace.", line, hold=0.2)
        self.play(Write(rules[1]), run_time=0.9)
        self.play(Write(rules[2]), Flash(self.project((0, 0, 0)), color=Palette.glow, line_length=0.25, flash_radius=0.35), run_time=0.9)
        self.wait(Timing.read_long)
        leaving = VGroup(u_arrow, w_arrow, u_tag, w_tag, moved_w, sum_arrow, sum_tag, rules)
        self.play(FadeOut(leaving), FadeIn(self.range_tag), run_time=0.7)
        self.remove(leaving)
        return line

    def not_onto(self, line):
        ring = Circle(radius=0.2, color=Palette.glow, stroke_width=4).move_to(self.project(B_POINT))
        b_dot = Dot(self.project(B_POINT), radius=0.08, color=Palette.glow)
        b_tag = space_tag(self.project, B_POINT, r"\mathbf b", Palette.glow, LEFT)
        gap = DashedLine(self.project(B_POINT), self.project(B_ABOVE), color=Palette.glow, stroke_width=3, dash_length=0.08)
        onto = MathTex(r"T \text{ is onto}", r"\iff", r"\operatorname{range}T = W", font_size=40)
        onto[2].set_color(RANGE_COLOR)
        onto.next_to(self.panel, DOWN, buff=0.7).set_x(PANEL_LEFT, LEFT)
        line = self.say(r"Day 16 showed that no input reaches $\mathbf b = (1, 1, 0)$.", line, hold=0.2)
        self.play(GrowFromCenter(b_dot), Create(ring), FadeIn(b_tag), run_time=0.8, rate_func=spring)
        self.play(Create(gap), run_time=0.8)
        self.wait(Timing.read_short)
        line = self.say(r"A map is \emph{onto} when its range is the whole codomain $W$.", line, hold=0.2)
        self.play(Write(onto), run_time=1.3)
        self.wait(Timing.read_short)
        line = self.say(r"This range is only a plane in $\mathbb R^3$, so $T$ is not onto.", line, hold=0.2)
        self.play(Indicate(self.sheet, color=RANGE_COLOR, scale_factor=1.0), Indicate(ring, color=Palette.glow), run_time=1.0)
        self.wait(Timing.read_short)
        self.clear_stage(keep=(line, self.map_group, self.axes))
        return line

    def split_inputs(self, line):
        self.amount.set_value(0.0)
        self.floor = always_redraw(lambda: floor_grid(self.project, self.amount.get_value()))
        self.floor_fill = always_redraw(lambda: floor_fill(self.project, self.amount.get_value()))
        self.kernel = always_redraw(lambda: kernel_line(self.project, self.amount.get_value()))
        kernel_tag = space_tag(self.project, KERNEL_REACH * KERNEL, r"\ker T", KERNEL_COLOR, RIGHT)
        floor_tag = space_tag(self.project, (-2, 1, 0), r"x_3 = 0", INPUT_COLOR, UP)
        line = self.say(r"Now go back to the inputs and split them in two.", line, hold=0.2)
        self.play(Create(self.kernel), FadeIn(kernel_tag), run_time=1.0)
        self.wait(Timing.beat)
        line = self.say(r"Yesterday's kernel is this pink line, and the floor is $x_3 = 0$.", line, hold=0.2)
        self.add(self.floor_fill)
        self.bring_to_back(self.floor_fill)
        self.play(FadeIn(self.floor_fill), Create(self.floor, lag_ratio=0.05), FadeIn(floor_tag), run_time=1.4)
        self.wait(Timing.read_short)
        self.arrows = always_redraw(lambda: split_arrows(self.project, self.amount.get_value()))
        x_tag = space_tag(self.project, X, r"\mathbf x", Palette.yellow, RIGHT)
        parts = MathTex(r"\mathbf x", "=", r"\begin{bmatrix}1\\1\\0\end{bmatrix}", "+", r"\begin{bmatrix}1\\-1\\1\end{bmatrix}", font_size=40)
        parts[0].set_color(Palette.yellow)
        parts[2].set_color(INPUT_COLOR)
        parts[4].set_color(KERNEL_COLOR)
        parts.next_to(self.map_group, DOWN, buff=0.6).set_x(PANEL_LEFT, LEFT)
        line = self.say(r"Every input is a floor part plus a kernel part.", line, hold=0.2)
        self.play(FadeIn(self.arrows), FadeIn(x_tag), run_time=1.0)
        self.play(Write(parts), run_time=1.4)
        self.wait(Timing.read_short)
        self.play(FadeOut(kernel_tag), FadeOut(floor_tag), FadeOut(x_tag), run_time=0.5)
        self.remove(kernel_tag, floor_tag, x_tag)
        self.parts = parts
        return line

    def collapse(self, line):
        line = self.say(r"Apply $T$: the kernel part collapses to zero.", line, hold=0.2)
        self.sfx("slide", gain=-2)
        self.play(self.amount.animate.set_value(1.0), run_time=4.0, rate_func=smooth)
        self.play(Flash(self.project((0, 0, 0)), color=Palette.glow, line_length=0.3, flash_radius=0.4), run_time=0.8)
        tx_tag = space_tag(self.project, T_X, r"T(\mathbf x)", Palette.yellow, UP)
        image = MathTex(r"T(\mathbf x)", "=", r"T\!\left(\begin{bmatrix}1\\1\\0\end{bmatrix}\right)", "=", r"\begin{bmatrix}1\\1\\2\end{bmatrix}", font_size=40)
        image[0].set_color(Palette.yellow)
        image[4].set_color(RANGE_COLOR)
        image.next_to(self.parts, DOWN, buff=0.45).set_x(PANEL_LEFT, LEFT)
        self.play(FadeIn(tx_tag), Write(image), run_time=1.3)
        self.wait(Timing.read_short)
        self.sheet = range_sheet(self.project, opacity=0.18)
        line = self.say(r"The floor tilts up onto the range, one point for one point.", line, hold=0.2)
        self.add(self.sheet)
        self.bring_to_back(self.sheet)
        self.play(FadeIn(self.sheet), run_time=0.8)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(self.parts, image, tx_tag)), run_time=0.6)
        self.remove(self.parts, image, tx_tag)
        return line

    def count(self, line):
        lines = count_lines().next_to(self.map_group, DOWN, buff=0.7).set_x(PANEL_LEFT, LEFT)
        line = self.say(r"One input dimension is crushed and two survive.", line, hold=0.2)
        self.play(Write(lines[0]), run_time=1.1)
        self.play(Write(lines[1]), run_time=1.1)
        self.wait(Timing.read_short)
        line = self.say(r"Crushed plus surviving gives back all three input dimensions.", line, hold=0.2)
        self.play(Write(lines[2]), run_time=1.2)
        self.wait(Timing.read_long)
        self.clear_stage(keep=(line,))
        return line

    def theorem(self, line):
        statement = MathTex(r"\dim\ker T", "+", r"\dim\operatorname{range}T", "=", r"\dim V", font_size=58)
        statement[0].set_color(KERNEL_COLOR)
        statement[2].set_color(RANGE_COLOR)
        statement.move_to([0, 2.7, 0])
        line = self.say(r"The same count holds for any linear map $T : V \to W$.", line, hold=0.2)
        self.play(Write(statement), run_time=1.6)
        self.wait(Timing.read_short)
        self.statement = statement
        return line

    def budgets(self, line):
        rows = [
            (r"T : \mathbb P_2 \to \mathbb R^2", r"Evaluating at 0 and 1 kills the line through $t^2 - t$.", 1, 3, 2),
            (r"D : \mathbb P_3 \to \mathbb P_2", r"Differentiation on $\mathbb P_3$ kills only the constants.", 1, 4, 3),
            (r"T : \mathbb R^3 \to \mathbb R^4", r"Even with a zero kernel, three dimensions cannot fill $\mathbb R^4$.", 0, 3, 4),
        ]
        for index, (map_tex, text, kernel_dim, domain_dim, codomain_dim) in enumerate(rows):
            row = budget_row(map_tex, kernel_dim, domain_dim, codomain_dim, 1.2 - 1.35 * index)
            line = self.say(text, line, hold=0.2)
            if index == 0:
                self.play(FadeIn(budget_headers(row)), run_time=0.5)
            self.fill_budget(row, kernel_dim, domain_dim, codomain_dim)
            self.wait(Timing.read_short)
        return line

    def fill_budget(self, row, kernel_dim, domain_dim, codomain_dim):
        name, domain, arrow, codomain = row
        self.play(FadeIn(name), FadeIn(arrow), Create(codomain), run_time=0.8)
        self.sfx("pop", gain=-6)
        self.play(LaggedStart(*[FadeIn(cell, scale=0.6) for cell in domain], lag_ratio=0.2), run_time=1.0)
        survivors = domain[kernel_dim:]
        landed = VGroup(*[filled_copy(codomain[index], RANGE_COLOR) for index in range(len(survivors))])
        self.play(*[TransformFromCopy(cell, target) for cell, target in zip(survivors, landed)], run_time=1.1, rate_func=spring_soft)
        if len(survivors) < codomain_dim:
            self.play(Create(cross_mark(codomain[-1])), run_time=0.6)
        else:
            self.play(Indicate(codomain, color=RANGE_COLOR, scale_factor=1.06), run_time=0.8)


class FigRangePlane(Scene):
    def construct(self):
        view = OrbitingView((0, 0), 1.0, azimuth=FACE_ON, elevation=ELEVATION)
        project = view.project
        dots = VGroup(*[Dot(project(A @ np.array(point, dtype=float)), radius=0.07, color=RANGE_COLOR) for point in INPUT_DOTS if point not in ((1, 0, 0), (0, 1, 0))])
        self.add(
            projected_axes(project, SPACE_REACH, labels=("x_1", "x_2", "x_3"), floor=False),
            range_sheet(project),
            dots,
            projected_arrow(project, A1, Palette.i_hat),
            projected_arrow(project, A2, Palette.j_hat),
            DashedLine(project(B_POINT), project(B_ABOVE), color=Palette.glow, stroke_width=3, dash_length=0.08),
            Circle(radius=0.16, color=Palette.glow, stroke_width=4).move_to(project(B_POINT)),
            Dot(project(B_POINT), radius=0.06, color=Palette.glow),
            space_tag(project, B_POINT, r"\mathbf b", Palette.glow, LEFT),
            range_tag(project, above=True),
            space_tag(project, A1, r"\mathbf a_1", Palette.i_hat, LEFT, font_size=32),
            space_tag(project, A2, r"\mathbf a_2", Palette.j_hat, RIGHT, font_size=32),
            origin_pulse().move_to(project((0, 0, 0))),
        )
        fit_to_frame(self)


def split_picture(amount):
    """The split input space at one moment of the slide from p to Ap, for the figures and poster."""
    view = OrbitingView((0, 0), 1.0, azimuth=FACE_ON, elevation=ELEVATION)
    project = view.project
    group = VGroup(
        projected_axes(project, SPACE_REACH, labels=("x_1", "x_2", "x_3"), floor=False),
        floor_fill(project, amount),
        floor_grid(project, amount),
    )
    if amount >= 1:
        group.add(range_sheet(project, opacity=0.18))
    group.add(kernel_line(project, amount), split_arrows(project, amount), origin_pulse().move_to(project((0, 0, 0))))
    return group, project


def split_pair():
    """The split inputs before T and the same objects after T, side by side."""
    before, project_before = split_picture(0.0)
    before.add(
        space_tag(project_before, KERNEL_REACH * KERNEL, r"\ker T", KERNEL_COLOR, RIGHT),
        space_tag(project_before, X, r"\mathbf x", Palette.yellow, UP),
    )
    after, project_after = split_picture(1.0)
    after.add(space_tag(project_after, T_X, r"T(\mathbf x)", Palette.yellow, UP))
    arrow = MathTex(r"\xrightarrow{\;T\;}", color=Palette.text_muted, font_size=64)
    return VGroup(before, arrow, after).arrange(RIGHT, buff=0.6)


class FigSplit(Scene):
    def construct(self):
        self.add(split_pair())
        fit_to_frame(self)


class FigBudget(Scene):
    def construct(self):
        rows = VGroup(
            budget_row(r"T : \mathbb P_2 \to \mathbb R^2", 1, 3, 2, 1.4),
            budget_row(r"D : \mathbb P_3 \to \mathbb P_2", 1, 4, 3, 0.0),
            budget_row(r"T : \mathbb R^3 \to \mathbb R^4", 0, 3, 4, -1.4),
        )
        for row, survivors in zip(rows, (2, 3, 3)):
            row.add(*[filled_copy(row[3][index], RANGE_COLOR) for index in range(survivors)])
        rows.add(cross_mark(rows[2][3][-1]), budget_headers(rows[0]))
        self.add(rows)
        fit_to_frame(self, margin=0.6)


class Poster(Scene):
    def construct(self):
        self.add(split_pair())
        fit_to_frame(self, margin=0.3)
