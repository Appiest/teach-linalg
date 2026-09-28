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
    clip_to_box,
    column,
    fit_to_frame,
    floor_and_axes,
    height_field,
    matrix,
    plane_at,
    plate_for,
    skewed_grid,
    spring,
    spring_soft,
    vector_arrow,
)

A = ((2, 1), (1, 2))
LEVEL = 14
ROOT2 = math.sqrt(2)
U1 = (1 / ROOT2, 1 / ROOT2)
U2 = (-1 / ROOT2, 1 / ROOT2)
LAMBDA1 = 3
X = (1, 2)
LEVEL_POINTS = [(x, y) for x in range(-4, 5) for y in range(-4, 5) if x * x + x * y + y * y == LEVEL // 2]

PLANE_ORIGIN = (-2.9, 0.45)
TURN_BOX = ((-4.8, 3.1), (-4.9, 3.6))
PANEL_LEFT = 0.75

SURFACE_ORIGIN = (-1.7, -0.15)
SURFACE_UNIT = 2.1
SURFACE_RADIUS = 1.3
Z_SCALE = 0.22
FLOOR_REACH = ((-2, 2), (-2, 2), (-1, 1))


def tex(*parts, colors=(), font_size=44):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def name_label(tex_string, color, point, direction, font_size=36):
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.07).next_to(point, direction, buff=0.12)


def form_value(point, second=1.0):
    """Q(x) for A = P diag(3, second) P^T, written through the principal coordinates y = P^T x."""
    along_first = point[0] * U1[0] + point[1] * U1[1]
    along_second = point[0] * U2[0] + point[1] * U2[1]
    return LAMBDA1 * along_first**2 + second * along_second**2


def turned_coefficients(angle):
    """Coefficients of y1^2, y1*y2 and y2^2 when A's form is written in axes turned by `angle`."""
    return 2 + math.sin(2 * angle), 2 * math.cos(2 * angle), 2 - math.sin(2 * angle)


def boxed_axis(plane, direction, color, stroke_width=4, box=TURN_BOX):
    """The line through the origin along `direction`, clipped to `box` (plane coords)."""
    far = 30
    ends = clip_to_box((-far * direction[0], -far * direction[1]), (far * direction[0], far * direction[1]), *box)
    return Line(plane.c2p(*ends[0]), plane.c2p(*ends[1]), color=color, stroke_width=stroke_width)


def level_ellipse(plane, stroke_width=6):
    first, second = math.sqrt(LEVEL / LAMBDA1), math.sqrt(LEVEL)

    def point(t):
        return plane.c2p(first * math.cos(t) * U1[0] + second * math.sin(t) * U2[0], first * math.cos(t) * U1[1] + second * math.sin(t) * U2[1])

    return ParametricFunction(point, t_range=[0, TAU], color=Palette.teal, stroke_width=stroke_width)


def turned_grid(plane, angle, box=TURN_BOX):
    c, s = math.cos(angle), math.sin(angle)
    return skewed_grid(plane, (c, s), (-s, c), reach=12, color=Palette.purple_gray, opacity=0.5, box=box)


def turned_axes(plane, angle):
    c, s = math.cos(angle), math.sin(angle)
    first = boxed_axis(plane, (c, s), Palette.purple_gray, stroke_width=3.5)
    second = boxed_axis(plane, (-s, c), Palette.purple_gray, stroke_width=3.5)
    first_name = name_label("y_1", Palette.purple_gray, plane.c2p(2.5 * c, 2.5 * s), DOWN + RIGHT * 0.4)
    second_name = name_label("y_2", Palette.purple_gray, plane.c2p(-3.3 * s, 3.3 * c), RIGHT)
    return VGroup(first, second, first_name, second_name)


def product_row():
    row = matrix([["x_1", "x_2"]])
    mat = matrix([["2", "1"], ["1", "2"]])
    col = column(["x_1", "x_2"])
    return VGroup(MathTex("=", color=Palette.text), row, mat, col).arrange(RIGHT, buff=0.15)


def principal_view(origin=SURFACE_ORIGIN, unit=SURFACE_UNIT, azimuth=-75.0, elevation=30.0):
    return OrbitingView(origin, unit, azimuth=azimuth, elevation=elevation)


def floor_with_lines(view):
    project = view.project
    parts = floor_and_axes(project, FLOOR_REACH)
    for direction, color in ((U1, Palette.yellow), (U2, Palette.blue)):
        reach = 2.1
        parts.add(Line(project((-reach * direction[0], -reach * direction[1], 0)), project((reach * direction[0], reach * direction[1], 0)), color=color, stroke_width=4))
    return parts


def bowl(view, second, opacity=0.5):
    return height_field(view, lambda x, y: form_value((x, y), second), radius=SURFACE_RADIUS, rings=10, spokes=44, z_scale=Z_SCALE, opacity=opacity)


def lifted_circle(view, second, color=Palette.text, stroke_width=5):
    def point(t):
        x, y = math.cos(t), math.sin(t)
        return view.project((x, y, Z_SCALE * form_value((x, y), second)))

    return ParametricFunction(point, t_range=[0, TAU], color=color, stroke_width=stroke_width)


def floor_circle(view):
    circle = ParametricFunction(lambda t: view.project((math.cos(t), math.sin(t), 0)), t_range=[0, TAU], color=Palette.text_muted, stroke_width=3)
    return DashedVMobject(circle, num_dashes=40)


def lifted_point(view, direction, second):
    return view.project((direction[0], direction[1], Z_SCALE * form_value(direction, second)))


def surface_mark(view, direction, second, color):
    point = lifted_point(view, direction, second)
    return VGroup(Dot(point, radius=0.2, color=color, fill_opacity=0.25), Dot(point, radius=0.09, color=color))


def walker(view, angle):
    direction = (math.cos(angle), math.sin(angle))
    top = lifted_point(view, direction, 1.0)
    foot = view.project((direction[0], direction[1], 0))
    return VGroup(DashedLine(foot, top, color=Palette.glow, stroke_width=3, dash_length=0.08), Dot(foot, radius=0.06, color=Palette.glow), Dot(top, radius=0.1, color=Palette.glow))


def definiteness_name(second):
    if second > 1e-9:
        return "positive definite"
    if second > -1e-9:
        return "positive semidefinite"
    return "indefinite"


class Lesson(LessonScene):
    day = 39
    title = "Quadratic forms"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, 1.0)
        self.plane = plane
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.recall_eigenvectors()
        line = self.meet_form(line)
        line = self.level_curve(line)
        line = self.turn_axes(line)
        line = self.read_eigenvalues(line)
        line = self.graph_surface(line)
        line = self.walk_circle(line)
        line = self.morph_surface(line)
        self.close_episode(
            r"The eigenvalues of $A$ decide whether $\mathbf x^TA\mathbf x$ is a bowl or a saddle.\\"
            r"The eigenvectors are its principal axes.",
            *self.mobjects,
        )

    def place_panel(self, rows):
        rows.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        rows.next_to([PANEL_LEFT, 0, 0], RIGHT, buff=0).to_edge(UP, buff=0.55)
        return rows

    def recall_eigenvectors(self):
        plane = self.plane
        lines = VGroup(boxed_axis(plane, U1, Palette.yellow, 5), boxed_axis(plane, U2, Palette.blue, 5))
        names = VGroup(
            name_label(r"\lambda = 3", Palette.yellow, plane.c2p(2.3, 2.3), RIGHT),
            name_label(r"\lambda = 1", Palette.blue, plane.c2p(-2.3, 2.3), LEFT),
        )
        line = self.say(r"Day 34 gave every symmetric matrix perpendicular eigenvectors.", hold=0.2)
        self.play(Create(lines[0]), Create(lines[1]), run_time=1.0)
        self.play(FadeIn(names[0], shift=LEFT * 0.1), FadeIn(names[1], shift=RIGHT * 0.1), run_time=0.6, rate_func=spring)
        self.wait(Timing.beat)
        line = self.say(r"Today we ask what shape $\mathbf x^TA\mathbf x$ has, and where it peaks.", line, hold=Timing.read_short)
        self.intro_lines = VGroup(lines, names)
        return line

    def meet_form(self, line):
        title_row = tex(r"Q(\mathbf x)", "=", r"\mathbf x^T A\,\mathbf x", colors=(Palette.teal,))
        product = product_row()
        expanded = tex("=", "2x_1^2", "+", "2x_1x_2", "+", "2x_2^2")
        rows = self.place_panel(VGroup(title_row, product, expanded))
        rows.scale(min(1, 6.1 / rows.width), about_edge=UL)
        self.plate = Rectangle(width=config.frame_width / 2 - PANEL_LEFT + 0.6, height=6.4, fill_color=Palette.background, fill_opacity=0.92, stroke_width=0)
        self.plate.align_to([config.frame_width / 2 + 0.1, 0, 0], RIGHT).align_to(rows, UP).shift(UP * 0.35)
        self.rows = rows
        line = self.say(r"A symmetric $A$ turns each vector $\mathbf x$ into one number.", line, hold=0.2)
        self.play(FadeOut(self.intro_lines), FadeIn(self.plate), FadeIn(title_row, shift=DOWN * 0.1), run_time=0.8)
        self.play(FadeIn(product, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.beat)
        self.play(FadeIn(expanded, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Squared lengths and variances are numbers of this kind.", line, hold=Timing.read_short)
        entries = product[2].get_entries()
        line = self.say(r"The diagonal gives the squares, and both 1s make the cross term.", line, hold=0.2)
        squares = VGroup(entries[0], entries[3], expanded[1], expanded[5])
        cross = VGroup(entries[1], entries[2], expanded[3])
        self.play(squares.animate.set_color(Palette.glow), run_time=0.6)
        self.wait(Timing.beat)
        self.play(squares.animate.set_color(Palette.text), cross.animate.set_color(Palette.glow), run_time=0.6)
        self.wait(Timing.read_short)
        self.play(cross.animate.set_color(Palette.text), run_time=0.5)
        return line

    def level_curve(self, line):
        plane = self.plane
        arrow = vector_arrow(X, Palette.purple_gray, plane)
        tag = name_label(r"\mathbf x", Palette.purple_gray, plane.c2p(*X), UL)
        value = tex(r"Q(1, 2)", "=", "2 + 4 + 8", "=", "14", colors=(None, None, None, None, Palette.teal))
        value.next_to(self.rows, DOWN, buff=0.4, aligned_edge=LEFT)
        line = self.say(r"At $\mathbf x = (1, 2)$ the form gives $14$.", line, hold=0.2)
        self.play(GrowArrow(arrow), FadeIn(tag), run_time=1.0, rate_func=spring_soft)
        self.play(FadeIn(value, shift=DOWN * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        dots = VGroup(*[Dot(plane.c2p(*point), radius=0.09, color=Palette.teal) for point in LEVEL_POINTS])
        ellipse = level_ellipse(plane)
        line = self.say(r"Every point with $Q = 14$ lies on one tilted ellipse.", line, hold=0.2)
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in dots], lag_ratio=0.12), run_time=1.8)
        self.play(Create(ellipse), run_time=1.8)
        self.bring_to_front(dots)
        self.wait(Timing.read_short)
        self.play(FadeOut(arrow), FadeOut(tag), FadeOut(dots), FadeOut(value), run_time=0.6)
        self.ellipse = ellipse
        return line

    def live_row(self, angle):
        """= a y1^2 + b y1y2 + c y2^2 with a, b, c following the turned axes."""
        static = tex("=", "y_1^2", "+", "y_1y_2", "+", "y_2^2")
        numbers = [DecimalNumber(value, num_decimal_places=2, color=color, font_size=44) for value, color in zip(turned_coefficients(angle.get_value()), (Palette.text, Palette.glow, Palette.text))]
        row = VGroup(static[0], numbers[0], static[1], static[2], numbers[1], static[3], static[4], numbers[2], static[5]).arrange(RIGHT, buff=0.12)
        row.next_to(self.rows, DOWN, buff=0.45, aligned_edge=LEFT)
        for index, number in enumerate(numbers):
            number.add_updater(lambda m, index=index: m.set_value(max(0.0, turned_coefficients(angle.get_value())[index])))
        return row, numbers

    def turn_axes(self, line):
        plane = self.plane
        expanded = self.rows[2]
        cross_box = SurroundingRectangle(expanded[3], color=Palette.glow, buff=0.08, stroke_width=3)
        line = self.say(r"The cross term $2x_1x_2$ is what tilts the ellipse.", line, hold=0.2)
        self.play(Create(cross_box), run_time=0.7)
        self.wait(Timing.read_short)
        angle = ValueTracker(0.0)
        grid = always_redraw(lambda: turned_grid(plane, angle.get_value()))
        axes = always_redraw(lambda: turned_axes(plane, angle.get_value()))
        row, numbers = self.live_row(angle)
        line = self.say(r"We want axes where the cross term disappears.", line, hold=0.2)
        self.play(plane.animate.set_opacity(0.35), FadeIn(grid), FadeIn(axes), FadeIn(row, shift=DOWN * 0.1), run_time=1.0)
        self.bring_to_front(self.ellipse, self.plate, self.rows, cross_box, row)
        self.play(angle.animate.set_value(math.radians(20)), run_time=2.2, rate_func=smooth)
        self.wait(Timing.beat)
        line = self.say(r"Along the eigenvectors the cross term reaches zero.", line, hold=0.2)
        self.play(angle.animate.set_value(math.radians(45)), run_time=2.4, rate_func=spring_soft)
        for number in numbers:
            number.clear_updaters()
        self.wait(Timing.beat)
        self.grid, self.axes, self.row, self.cross_box = grid, axes, row, cross_box
        return line

    def read_eigenvalues(self, line):
        plane = self.plane
        eigen_axes = VGroup(boxed_axis(plane, U1, Palette.yellow, 5), boxed_axis(plane, U2, Palette.blue, 5))
        eigen_names = VGroup(
            name_label(r"\lambda = 3", Palette.yellow, plane.c2p(2.3, 2.3), RIGHT),
            name_label(r"\lambda = 1", Palette.blue, plane.c2p(2.9, -2.9), RIGHT),
        )
        settled = tex("=", "3", "y_1^2", "+", "1", "y_2^2", colors=(None, Palette.yellow, None, None, Palette.blue))
        settled.next_to(self.rows, DOWN, buff=0.45, aligned_edge=LEFT)
        self.play(FadeOut(self.axes), Create(eigen_axes[0]), Create(eigen_axes[1]), FadeOut(self.row), FadeIn(settled), FadeOut(self.cross_box), run_time=1.2)
        self.bring_to_front(self.ellipse, self.plate, self.rows, settled)
        line = self.say(r"The new coefficients are the eigenvalues 3 and 1.", line, hold=0.2)
        self.play(FadeIn(eigen_names[0], shift=LEFT * 0.1), FadeIn(eigen_names[1], shift=RIGHT * 0.1), run_time=0.8, rate_func=spring)
        self.wait(Timing.read_short)
        line = self.half_axes(line)
        theorem = tex(r"\mathbf x = P\mathbf y", r"\;\Rightarrow\;", r"\mathbf x^TA\,\mathbf x = \mathbf y^T D\,\mathbf y")
        theorem.scale(min(1, 6.0 / theorem.width)).next_to(settled, DOWN, buff=0.5, aligned_edge=LEFT)
        line = self.say(r"$A = PDP^T$ from Day 34 does this for any form.", line, hold=0.2)
        self.play(FadeIn(theorem, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_long)
        leaving = [self.grid, eigen_axes, eigen_names, settled, theorem, self.ellipse, self.plate, self.rows, self.half, plane]
        self.play(*[FadeOut(item) for item in leaving], run_time=0.9)
        return line

    def half_axes(self, line):
        plane = self.plane
        first, second = math.sqrt(LEVEL / 3), math.sqrt(LEVEL)
        short = Line(plane.c2p(0, 0), plane.c2p(first * U1[0], first * U1[1]), color=Palette.yellow, stroke_width=11)
        long = Line(plane.c2p(0, 0), plane.c2p(second * U2[0], second * U2[1]), color=Palette.blue, stroke_width=11)
        short_name = name_label(r"\sqrt{14/3}", Palette.yellow, short.get_center(), DR, font_size=34)
        long_name = name_label(r"\sqrt{14/1}", Palette.blue, long.get_center(), DL, font_size=34)
        line = self.say(r"The bigger eigenvalue gives the shorter axis.", line, hold=0.2)
        self.play(Create(short), FadeIn(short_name), run_time=1.0, rate_func=spring_soft)
        self.play(Create(long), FadeIn(long_name), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)
        self.half = VGroup(short, long, short_name, long_name)
        return line

    def graph_surface(self, line):
        view = principal_view()
        self.view = view
        self.second = ValueTracker(1.0)
        floor = always_redraw(lambda: floor_with_lines(view))
        surface = always_redraw(lambda: bowl(view, self.second.get_value()))
        self.play(FadeIn(floor), run_time=0.9)
        line = self.say(r"Now graph $z = Q(\mathbf x)$ above the plane.", line, hold=0.2)
        self.play(FadeIn(surface, shift=UP * 0.3), run_time=1.4, rate_func=spring_soft)
        self.play(view.turn_to(-40.0), run_time=3.0, rate_func=smooth)
        self.floor, self.surface = floor, surface
        return line

    def walk_circle(self, line):
        view = self.view
        angle = ValueTracker(0.0)
        base = always_redraw(lambda: floor_circle(view))
        path = always_redraw(lambda: lifted_circle(view, self.second.get_value()))
        step = always_redraw(lambda: walker(view, angle.get_value()))
        readout_label = tex(r"\|\mathbf x\| = 1", font_size=42).set_color(Palette.text_muted)
        value_label = tex(r"Q(\mathbf x) =", colors=(Palette.teal,), font_size=48)
        value = DecimalNumber(2.0, num_decimal_places=2, color=Palette.teal, font_size=48)
        value.add_updater(lambda m: m.set_value(form_value((math.cos(angle.get_value()), math.sin(angle.get_value())))))
        value_row = VGroup(value_label, value).arrange(RIGHT, buff=0.2)
        readout = VGroup(readout_label, value_row).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to([4.6, 2.4, 0])
        line = self.say(r"Which unit vector makes $Q$ largest? Walk the circle.", line, hold=0.2)
        self.play(Create(base), run_time=1.0)
        self.play(Create(path), FadeIn(step), FadeIn(readout), run_time=1.2)
        self.play(angle.animate.set_value(PI / 4), run_time=2.0, rate_func=smooth)
        top = always_redraw(lambda: surface_mark(view, U1, self.second.get_value(), Palette.yellow))
        line = self.say(r"The highest point sits above $\mathbf u_1$, at height $3$.", line, hold=0.2)
        self.play(GrowFromCenter(top), run_time=0.6, rate_func=spring)
        self.wait(Timing.beat)
        line = self.say(r"Day 40 uses this peak to find singular values.", line, hold=Timing.read_short)
        self.play(angle.animate.set_value(3 * PI / 4), run_time=2.4, rate_func=smooth)
        low = always_redraw(lambda: surface_mark(view, U2, self.second.get_value(), Palette.blue))
        line = self.say(r"The lowest sits above $\mathbf u_2$, at height $1$.", line, hold=0.2)
        self.play(GrowFromCenter(low), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        value.clear_updaters()
        self.play(FadeOut(step), FadeOut(readout), run_time=0.6)
        self.marks = VGroup(top, low)
        return line

    def eigen_meter(self):
        second = self.second
        track = NumberLine(x_range=(-3, 4, 1), length=5.2, color=Palette.text_muted, stroke_width=2.5, include_numbers=True, font_size=32)
        track.numbers.set_color(Palette.text_muted)
        track.move_to([4.5, 2.6, 0])
        first_dot = Dot(track.n2p(LAMBDA1), radius=0.11, color=Palette.yellow)
        first_name = MathTex(r"\lambda_1", color=Palette.yellow, font_size=36).next_to(first_dot, UP, buff=0.15)
        second_dot = always_redraw(lambda: Dot(track.n2p(second.get_value()), radius=0.11, color=Palette.blue))
        second_name = always_redraw(lambda: MathTex(r"\lambda_2", color=Palette.blue, font_size=36).next_to(track.n2p(second.get_value()), UP, buff=0.2))
        zero_tick = Line(track.n2p(0) + DOWN * 0.18, track.n2p(0) + UP * 0.18, color=Palette.glow, stroke_width=3)
        return VGroup(track, zero_tick, first_dot, first_name, second_dot, second_name)

    def kind_label(self, second):
        return Tex(definiteness_name(second), color=Palette.text, font_size=42).move_to([4.5, 1.35, 0])

    def morph_surface(self, line):
        meter = self.eigen_meter()
        kind = self.kind_label(1.0)
        line = self.say(r"The eigenvalues decide whether $Q$ is ever negative.", line, hold=0.2)
        self.play(FadeIn(meter, shift=DOWN * 0.1), run_time=0.9)
        self.wait(Timing.beat)
        line = self.say(r"Both eigenvalues are positive, so every value is positive.", line, hold=0.2)
        self.play(FadeIn(kind, shift=DOWN * 0.1), run_time=0.7)
        self.wait(Timing.read_short)
        line = self.say(r"At $\lambda_2 = 0$ the bowl flattens into a trough.", line, hold=0.2)
        self.play(self.second.animate.set_value(0.0), run_time=2.6, rate_func=spring_soft)
        kind = self.swap_kind(kind, 0.0)
        self.wait(Timing.read_short)
        line = self.say(r"A negative eigenvalue bends the bowl into a saddle.", line, hold=0.2)
        fresh = self.kind_label(-2.0)
        early = lambda t: min(1.0, 5 * t)  # noqa: E731
        self.play(
            self.second.animate(rate_func=spring_soft).set_value(-2.0),
            FadeOut(kind, shift=UP * 0.1, rate_func=early),
            FadeIn(fresh, shift=UP * 0.1, rate_func=early),
            run_time=3.0,
        )
        kind = fresh
        self.play(self.view.turn_to(-20.0), run_time=3.0, rate_func=smooth)
        self.wait(Timing.read_short)
        return line

    def swap_kind(self, kind, second):
        fresh = self.kind_label(second)
        self.play(FadeOut(kind, shift=UP * 0.1), FadeIn(fresh, shift=UP * 0.1), run_time=0.6)
        return fresh


class FigPrincipalAxes(Scene):
    def construct(self):
        plane = plane_at((-2.2, 0), 1.1)
        whole = ((-5, 9), (-4, 4))
        first, second = math.sqrt(LEVEL / 3), math.sqrt(LEVEL)
        self.add(plane.set_opacity(0.3), turned_grid(plane, math.radians(45), whole))
        self.add(boxed_axis(plane, U1, Palette.yellow, 5, whole), boxed_axis(plane, U2, Palette.blue, 5, whole), level_ellipse(plane))
        self.add(Line(plane.c2p(0, 0), plane.c2p(first * U1[0], first * U1[1]), color=Palette.yellow, stroke_width=11))
        self.add(Line(plane.c2p(0, 0), plane.c2p(second * U2[0], second * U2[1]), color=Palette.blue, stroke_width=11))
        self.add(name_label(r"y_1", Palette.yellow, plane.c2p(2.6, 2.6), RIGHT, font_size=40))
        self.add(name_label(r"y_2", Palette.blue, plane.c2p(-2.6, 2.6), LEFT, font_size=40))
        before = tex("2x_1^2", "+", "2x_1x_2", "+", "2x_2^2", "=", "14", colors=(None, None, Palette.glow), font_size=44)
        after = tex("3", "y_1^2", "+", "1", "y_2^2", "=", "14", colors=(Palette.yellow, None, None, Palette.blue), font_size=44)
        equations = VGroup(before, after).arrange(DOWN, buff=0.35, aligned_edge=RIGHT).move_to([3.95, -0.6, 0])
        self.add(plate_for(equations, padding=0.25), equations)


class FigBowlTroughSaddle(Scene):
    def construct(self):
        panels = VGroup()
        for index, (second, words) in enumerate(((1.0, "positive definite"), (0.0, "positive semidefinite"), (-2.0, "indefinite"))):
            view = principal_view(origin=(-4.8 + 4.8 * index, 0.3), unit=1.25, azimuth=-30.0)
            picture = VGroup(floor_with_lines(view), bowl(view, second, opacity=0.55), lifted_circle(view, second, stroke_width=4))
            eigen = tex(r"\lambda_1 = 3", ",", rf"\;\lambda_2 = {second:g}", colors=(Palette.yellow, None, Palette.blue), font_size=38)
            name = Tex(words, color=Palette.text, font_size=36)
            caption_block = VGroup(eigen, name).arrange(DOWN, buff=0.2).next_to(picture, DOWN, buff=0.35)
            panels.add(VGroup(picture, caption_block))
        lowest = min(panel[0].get_bottom()[1] for panel in panels)
        for panel in panels:
            panel[1].set_y(lowest - 0.35 - panel[1].height / 2)
        self.add(panels)
        fit_to_frame(self)


class FigUnitCircleHeights(Scene):
    def construct(self):
        axes = Axes(
            x_range=(0, 360, 45),
            y_range=(0, 3.5, 1),
            x_length=11,
            y_length=5.2,
            axis_config={"color": Palette.axis, "stroke_width": 2, "include_ticks": True},
            tips=False,
        )
        labels = VGroup(*[MathTex(rf"{degrees}^\circ", color=Palette.text_muted, font_size=30).next_to(axes.c2p(degrees, 0), DOWN, buff=0.2) for degrees in range(0, 361, 90)])
        heights = VGroup(*[MathTex(str(level), color=Palette.text_muted, font_size=30).next_to(axes.c2p(0, level), LEFT, buff=0.2) for level in (1, 2, 3)])
        curve = axes.plot(lambda d: 2 + math.sin(2 * math.radians(d)), x_range=(0, 360), color=Palette.teal, stroke_width=6)
        guides = VGroup(*[DashedLine(axes.c2p(0, level), axes.c2p(360, level), color=Palette.text_muted, stroke_width=2) for level in (1, 3)])
        marks = VGroup()
        for degrees, level, color in ((45, 3, Palette.yellow), (225, 3, Palette.yellow), (135, 1, Palette.blue), (315, 1, Palette.blue)):
            marks.add(Dot(axes.c2p(degrees, level), radius=0.12, color=color))
        names = VGroup(
            tex(r"M = \lambda_1 = 3", colors=(Palette.yellow,), font_size=38).next_to(axes.c2p(45, 3), UP, buff=0.25),
            tex(r"m = \lambda_2 = 1", colors=(Palette.blue,), font_size=38).next_to(axes.c2p(135, 1), DOWN, buff=0.3),
        )
        theta = MathTex(r"\theta", color=Palette.text_muted, font_size=34).next_to(axes.c2p(360, 0), RIGHT, buff=0.25)
        height = MathTex(r"Q(\cos\theta, \sin\theta)", color=Palette.teal, font_size=34).next_to(axes.c2p(0, 3.5), UP, buff=0.2)
        self.add(axes, guides, curve, marks, names, labels, heights, theta, height)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        view = principal_view(origin=(0.0, 0.1), unit=2.1, azimuth=-45.0, elevation=30.0)
        self.add(floor_with_lines(view), bowl(view, -2.0, opacity=0.6), lifted_circle(view, -2.0, stroke_width=6))
        self.add(surface_mark(view, U1, -2.0, Palette.yellow), surface_mark(view, U2, -2.0, Palette.blue))
        fit_to_frame(self, margin=0.3)
