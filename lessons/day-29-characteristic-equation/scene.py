import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    LiveTransform,
    Palette,
    Timing,
    backed,
    clip_line_to_box,
    clipped_plot,
    column_parallelogram,
    fit_to_frame,
    line_through_origin,
    make_plane,
    matrix,
    plane_at,
    plate_for,
    scrim,
    skewed_grid,
    spring,
    spring_soft,
    vector_arrow,
)

RECAP_A = ((3, -2), (1, 0))
RECAP_SQUASH = ((1, -2), (1, -2))
RECAP_V1 = (2, 1)
RECAP_V2 = (1, 1)

A = ((1, 2), (2, 1))
V1 = (1, 1)
V2 = (1, -1)
ROOTS = ((-1, V2, Palette.blue), (3, V1, Palette.yellow))
BASIS_COLORS = (Palette.i_hat, Palette.j_hat)

LEFT_ORIGIN = (-3.7, 0.45)
LEFT_UNIT = 0.53
LEFT_REACH = 6
LAMBDA_RANGE = (-2.5, 4.5)
P_RANGE = (-4.5, 6.0)
PLOT_CENTER = (3.45, -0.15)
PLOT_SIZE = (5.8, 5.0)

M = ((4, 0, 0), (-3, 1, 2), (2, 0, 3))
M_ROOTS = r"4,\ 1,\ 3"
B = ((2, 1, 0), (0, 2, 3), (0, 0, 4))


def char_poly(lam):
    return lam * lam - 2 * lam - 3


def repeated_poly(lam):
    return (2 - lam) ** 2 * (4 - lam)


def shifted(lam):
    return np.array([[A[0][0] - lam, A[0][1]], [A[1][0], A[1][1] - lam]], dtype=float)


def tex(*parts, colors=(), font_size=44):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def basis_matrix(rows):
    mat = matrix([[str(entry) for entry in row] for row in rows])
    for index, color in enumerate(BASIS_COLORS):
        mat.get_columns()[index].set_color(color)
    return mat


def named(name, mat, font_size=44):
    return VGroup(MathTex(name, "=", color=Palette.text, font_size=font_size), mat).arrange(RIGHT, buff=0.2)


def name_label(tex_string, color, point, direction, font_size=38):
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.08).next_to(point, direction, buff=0.12)


def origin_ring(plane, radius=0.24):
    return Circle(radius=radius, color=Palette.glow, stroke_width=4).move_to(plane.c2p(0, 0))


def safe_arrow(plane, coords, color, stroke_width=6):
    """An arrow to coords, or a dot at the origin once it has shrunk to nothing."""
    if math.hypot(*coords) < 0.12:
        return Dot(plane.c2p(0, 0), radius=0.07, color=color)
    return vector_arrow(coords, color, plane, stroke_width=stroke_width)


def moving_line(plane, live, direction, color, stroke_width=4.5):
    """The image of the whole line through direction under live's current matrix."""
    ends = clip_line_to_box((direction[1], -direction[0], 0), plane.x_range[:2], plane.y_range[:2])
    start, end = (live.point(point) for point in ends)
    if math.hypot(*(end - start)) < 0.1:
        return Dot(plane.c2p(0, 0), radius=0.08, color=color)
    return Line(plane.c2p(*start), plane.c2p(*end), color=color, stroke_width=stroke_width)


def grid_reach(transform, limit=LEFT_REACH, cap=40):
    """How many grid steps the image grid needs to still cover the square window of half-width `limit`."""
    if abs(np.linalg.det(transform)) < 1e-3:
        return cap
    inverse = np.linalg.inv(transform)
    corners = [np.array((x, y)) for x in (-limit, limit) for y in (-limit, limit)]
    return min(cap, int(max(np.abs(inverse @ corner).max() for corner in corners)) + 2)


def left_plane(origin=LEFT_ORIGIN, unit=LEFT_UNIT, reach=LEFT_REACH):
    plane = make_plane(x_range=(-reach, reach, 1), y_range=(-reach, reach, 1), x_length=2 * reach * unit, y_length=2 * reach * unit)
    plane.shift(np.array([origin[0], origin[1], 0.0]) - plane.c2p(0, 0))
    return plane.set_opacity(0.3)


def square_color(lam):
    return Palette.teal if char_poly(lam) >= 0 else Palette.pink


def eigen_image(lam, direction, eigenvalue):
    return ((eigenvalue - lam) * direction[0], (eigenvalue - lam) * direction[1])


def plane_state(plane, lam, reach=LEFT_REACH, stroke_width=6):
    """What A - lambda I does to the plane: the moved grid, the image of the unit square, and both eigen-arrows."""
    transform = shifted(lam)
    grid = skewed_grid(plane, transform[:, 0], transform[:, 1], reach=grid_reach(transform, reach), color=Palette.grid, opacity=0.85)
    square = column_parallelogram(plane, transform[:, 0], transform[:, 1], color=square_color(lam), opacity=0.38, stroke_width=2.5)
    square.set_stroke(color=square_color(lam), opacity=0.9)
    arrows = VGroup(*[safe_arrow(plane, eigen_image(lam, direction, root), color, stroke_width) for root, direction, color in ROOTS])
    return VGroup(grid, square, arrows)


def faint_lines(plane):
    return VGroup(*[line_through_origin(plane, direction, color, 2.5, dashed=True, opacity=0.55) for _, direction, color in ROOTS])


def lit_line(plane, direction, color):
    return line_through_origin(plane, direction, color, 5)


def plot_axes(center=PLOT_CENTER, size=PLOT_SIZE, x_range=LAMBDA_RANGE, y_range=P_RANGE):
    axes = Axes(
        x_range=(*x_range, 1),
        y_range=(*y_range, 1),
        x_length=size[0],
        y_length=size[1],
        tips=False,
        axis_config={"color": Palette.axis, "stroke_width": 2, "include_ticks": True, "tick_size": 0.06},
    )
    axes.shift(np.array([center[0], center[1], 0]) - axes.get_center())
    return axes


CENTER_LABEL_SIDES = {-1: (DOWN, LEFT * 0.22), 0: (UP, LEFT * 0.2), 1: (UP, ORIGIN), 2: (UP, ORIGIN), 3: (DOWN, RIGHT * 0.22)}


def tick_labels(axes, values, font_size=28, sides=None):
    """Axis numbers placed on the side of the axis the curve and the stem leave free."""
    labels = VGroup()
    for value in values:
        side, nudge = (sides or {}).get(value, (DOWN, ORIGIN))
        label = MathTex(str(value), color=Palette.text_muted, font_size=font_size)
        label.next_to(axes.c2p(value, 0), side, buff=0.22).shift(nudge)
        labels.add(label)
    return labels


def lambda_axis_label(axes, x_end):
    return MathTex(r"\lambda", color=Palette.glow, font_size=38).next_to(axes.c2p(x_end, 0), RIGHT, buff=0.14)


def plot_panel():
    axes = plot_axes()
    curve = clipped_plot(axes, char_poly, LAMBDA_RANGE, P_RANGE, Palette.text, stroke_width=4.5)
    heading = tex(r"\det(A - \lambda I)", "=", r"\lambda^2 - 2\lambda - 3", font_size=40)
    heading.next_to(axes, UP, buff=0.35)
    return VGroup(axes, tick_labels(axes, range(-2, 5), sides=CENTER_LABEL_SIDES), lambda_axis_label(axes, LAMBDA_RANGE[1]), curve, heading)


def plot_tracker(axes, lam):
    """The orange dot riding the curve at lambda, its stem down to the axis, and the lambda mark on the axis."""
    value = char_poly(lam)
    on_axis = axes.c2p(lam, 0)
    on_curve = axes.c2p(lam, value)
    parts = VGroup()
    if abs(on_curve[1] - on_axis[1]) > 0.06:
        parts.add(DashedLine(on_axis, on_curve, color=Palette.glow, stroke_width=3, dash_length=0.08))
    parts.add(Dot(on_axis, radius=0.08, color=Palette.glow))
    parts.add(Dot(on_curve, radius=0.11, color=Palette.glow))
    return parts


def root_mark(axes, root, color):
    point = axes.c2p(root, 0)
    return VGroup(Dot(point, radius=0.12, color=color), Circle(radius=0.22, color=Palette.glow, stroke_width=3).move_to(point))


def lambda_readout(axes, tracker):
    label = MathTex(r"\lambda =", color=Palette.glow, font_size=44)
    label.move_to(axes.c2p(1.1, 5.0))
    number = DecimalNumber(tracker.get_value(), num_decimal_places=1, color=Palette.glow, font_size=44)
    number.next_to(label, RIGHT, buff=0.18)
    number.add_updater(lambda m: m.set_value(tracker.get_value()).next_to(label, RIGHT, buff=0.18))
    return VGroup(label, number)


def diagonal_matrix_tex(rows, font_size=44, h_buff=1.5):
    """A square matrix of TeX entries with its diagonal glowing, spaced for entries like 3 - lambda."""
    mat = Matrix([[str(entry) for entry in row] for row in rows], v_buff=0.72, h_buff=h_buff, bracket_h_buff=0.16, element_to_mobject_config={"font_size": font_size})
    mat.set_color(Palette.text)
    for index in range(len(rows)):
        mat.get_rows()[index][index].set_color(Palette.glow)
    return mat


def minus_lambda_rows(rows):
    return [[f"{value} - \\lambda" if i == j else str(value) for j, value in enumerate(row)] for i, row in enumerate(rows)]


def aligned_steps(first, *continuations):
    """Stack a first line (name, =, value) over lines that start with =, with every = sign in one column."""
    group = VGroup(first, *continuations).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
    for step in continuations:
        step.shift(RIGHT * (first[1].get_x() - step[0].get_x()))
    return group


def cofactor_steps(font_size=42):
    return aligned_steps(
        tex(r"\det(M - \lambda I)", "=", r"(4 - \lambda)\det\begin{bmatrix} 1 - \lambda & 2 \\ 0 & 3 - \lambda \end{bmatrix}", font_size=font_size),
        tex("=", r"(4 - \lambda)(1 - \lambda)(3 - \lambda)", font_size=font_size),
    )


def repeated_plot(center=(0, -1.15), size=(8.6, 3.3)):
    x_range, y_range = (0.5, 5.0), (-3.0, 3.5)
    axes = plot_axes(center, size, x_range, y_range)
    curve = clipped_plot(axes, repeated_poly, x_range, y_range, Palette.text, stroke_width=4.5)
    labels = tick_labels(axes, range(1, 6), font_size=26)
    marks = VGroup(root_mark(axes, 2, Palette.glow), root_mark(axes, 4, Palette.glow))
    notes = VGroup(
        Tex("multiplicity 2", color=Palette.glow, font_size=32).next_to(axes.c2p(2, 0), UP, buff=0.35),
        Tex("multiplicity 1", color=Palette.text_muted, font_size=32).next_to(axes.c2p(4, 0), UR, buff=0.2),
    )
    return VGroup(axes, labels, lambda_axis_label(axes, x_range[1]), curve), marks, notes


class Lesson(LessonScene):
    day = 29
    title = "Finding eigenvalues"

    def construct(self):
        plane = plane_at((0.0, -0.4), 1.0)
        self.plane = plane
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.recap()
        line = self.chain(line)
        line = self.two_by_two(line)
        line = self.centerpiece(line)
        line = self.eigenvectors(line)
        line = self.three_by_three(line)
        line = self.multiplicity(line)
        self.close_episode(
            r"$\lambda$ is an eigenvalue exactly when $\det(A - \lambda I) = 0$.\\"
            r"Solve for $\lambda$, then row reduce $A - \lambda I$ for the eigenvectors.",
            *self.mobjects,
        )

    def recap(self):
        plane = self.plane
        live = LiveTransform()
        grid = always_redraw(lambda: live.grid(plane, opacity=0.8))
        panel_content = named("A", basis_matrix(RECAP_A)).to_corner(UL, buff=0.55)
        panel = VGroup(plate_for(panel_content), panel_content).set_z_index(10)
        blue = line_through_origin(plane, RECAP_V2, Palette.blue, 4.5)
        yellow = always_redraw(lambda: moving_line(plane, live, RECAP_V1, Palette.yellow))
        labels = VGroup(
            name_label(r"\lambda = 2", Palette.yellow, plane.c2p(5.4, 2.7), DR, font_size=40),
            name_label(r"\lambda = 1", Palette.blue, plane.c2p(3.5, 3.5), LEFT, font_size=40),
        )
        line = self.say(r"Yesterday's $A$ kept two lines, with $\lambda = 2$ and $\lambda = 1$.", hold=0.2)
        self.play(plane.animate.set_opacity(0.3), FadeIn(grid), FadeIn(panel, shift=DOWN * 0.1), run_time=0.9)
        self.play(Create(yellow), Create(blue), run_time=1.0)
        self.play(FadeIn(labels), run_time=0.5)
        self.wait(Timing.beat)
        line = self.say(r"We could check each $\lambda$, but only after guessing it.", line, hold=Timing.read_short)
        line = self.say(r"Today we find every eigenvalue directly, with no guessing.", line, hold=Timing.read_short)
        line = self.say(r"Then $A - 2I$ squashed the whole plane flat.", line, hold=0.2)
        self.play(FadeOut(labels), run_time=0.4)
        self.play(live.apply(RECAP_SQUASH), run_time=3.0, rate_func=spring_soft)
        ring = origin_ring(plane)
        self.play(GrowFromCenter(ring), run_time=0.6, rate_func=spring)
        verdict = tex(r"\det(A - 2I)", "=", "0", colors=(None, None, Palette.glow), font_size=44)
        verdict.next_to(panel_content, DOWN, buff=0.4).align_to(panel_content, LEFT).set_z_index(11)
        line = self.say(r"A flat plane has area scale $\det(A - 2I) = 0$.", line, hold=0.2)
        self.play(panel[0].animate.become(plate_for(VGroup(panel_content, verdict)).set_z_index(10)), FadeIn(verdict, shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        self.recap_parts = VGroup(plane, grid, panel, verdict, blue, yellow, ring)
        return line

    def chain(self, line):
        self.veil = scrim().set_z_index(20)
        steps = VGroup(
            MathTex(r"\lambda \text{ is an eigenvalue of } A", color=Palette.text, font_size=48),
            MathTex(r"\iff (A - \lambda I)\mathbf x = \mathbf 0 \text{ has a nonzero solution}", color=Palette.text, font_size=48),
            MathTex(r"\iff A - \lambda I \text{ is not invertible}", color=Palette.text, font_size=48),
            MathTex(r"\iff \det(A - \lambda I) = 0", color=Palette.text, font_size=48),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to(UP * 0.55).set_z_index(21)
        line = self.say(r"The goal is an equation whose only unknown is $\lambda$.", line, hold=Timing.read_short)
        line = self.say(r"The same test works for any $\lambda$ and any $A$.", line, hold=0.2)
        self.play(FadeIn(self.veil), run_time=0.6)
        self.remove(*self.recap_parts)
        self.play(FadeIn(steps[0], shift=UP * 0.1), run_time=0.6)
        self.play(FadeIn(steps[1], shift=UP * 0.1), run_time=0.7)
        line = self.say(r"A nonzero solution means $A - \lambda I$ has no inverse.", line, hold=0.2)
        self.play(FadeIn(steps[2], shift=UP * 0.1), run_time=0.7)
        self.wait(Timing.beat)
        line = self.say(r"And no inverse means the determinant is $0$.", line, hold=0.2)
        self.play(FadeIn(steps[3], shift=UP * 0.1), run_time=0.7)
        box = SurroundingRectangle(steps[3][0][1:], color=Palette.glow, buff=0.14, stroke_width=3).set_z_index(21)
        self.play(Create(box), run_time=0.7)
        line = self.say(r"This equation has only $\lambda$ in it, so nothing is guessed.", line, hold=Timing.read_short)
        self.play(FadeOut(VGroup(steps, box)), run_time=0.6)
        return line

    def two_by_two(self, line):
        original = named("A", basis_matrix(A), font_size=48)
        minus = named(r"A - \lambda I", diagonal_matrix_tex(minus_lambda_rows(A)), font_size=48)
        VGroup(original, minus).arrange(RIGHT, buff=1.1).move_to(UP * 2.2).set_z_index(21)
        steps = aligned_steps(
            tex(r"\det(A - \lambda I)", "=", r"(1 - \lambda)(1 - \lambda) - 2 \cdot 2", font_size=46),
            tex("=", r"\lambda^2 - 2\lambda - 3", font_size=46),
            tex("=", r"(\lambda - 3)(\lambda + 1)", font_size=46),
        ).move_to(DOWN * 0.75).set_z_index(21)
        line = self.say(r"Here is a new $A$, and we want its eigenvalues.", line, hold=0.2)
        self.play(FadeIn(original, shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Subtract $\lambda$ from each diagonal entry.", line, hold=0.2)
        self.play(FadeIn(minus, shift=LEFT * 0.2), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Expand the $2 \times 2$ determinant as on Day 26.", line, hold=0.2)
        self.play(FadeIn(steps[0], shift=DOWN * 0.1), run_time=0.9)
        self.wait(Timing.beat)
        self.play(FadeIn(steps[1], shift=DOWN * 0.1), run_time=0.8)
        line = self.say(r"This is the \emph{characteristic polynomial} of $A$.", line, hold=0.2)
        self.play(Indicate(steps[1][1], color=Palette.glow, scale_factor=1.1), run_time=0.9)
        self.wait(Timing.beat)
        line = self.say(r"It factors, and its roots are $3$ and $-1$.", line, hold=0.2)
        self.play(FadeIn(steps[2], shift=DOWN * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(original, minus, steps)), run_time=0.6)
        return line

    def centerpiece(self, line):
        self.build_stage()
        line = self.say(r"Slide $\lambda$ and watch what $A - \lambda I$ does to the plane.", line, hold=0.2)
        self.play(FadeOut(self.veil), run_time=0.9)
        self.wait(Timing.beat)
        line = self.say(r"At $\lambda = -1$ the plane squashes flat.", line, hold=0.2)
        self.play(self.lam.animate.set_value(-1), run_time=2.6, rate_func=spring_soft)
        self.light_root(0)
        line = self.say(r"At that same moment the curve touches zero.", line, hold=0.2)
        self.play(Flash(self.axes.c2p(-1, 0), color=Palette.glow, line_length=0.2, flash_radius=0.3), run_time=0.9)
        self.wait(Timing.beat)
        line = self.say(r"In between, the square flips and its area turns negative.", line, hold=0.2)
        self.play(FadeOut(self.ring), run_time=0.3)
        self.play(self.lam.animate.set_value(1), run_time=3.0, rate_func=smooth)
        self.wait(Timing.read_short)
        line = self.say(r"At $\lambda = 3$ the plane squashes flat again.", line, hold=0.2)
        self.play(self.lam.animate.set_value(3), run_time=3.0, rate_func=smooth)
        self.light_root(1)
        self.wait(Timing.read_short)
        line = self.say(r"Every other $\lambda$ leaves a real parallelogram.", line, hold=0.2)
        self.play(FadeOut(self.ring), run_time=0.3)
        self.play(self.lam.animate.set_value(4), run_time=2.0, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return line

    def build_stage(self):
        plane = left_plane()
        self.left = plane
        self.lam = ValueTracker(-2.0)
        state = always_redraw(lambda: plane_state(plane, self.lam.get_value()))
        self.lines = faint_lines(plane)
        self.plot = plot_panel()
        self.axes = self.plot[0]
        self.tracker = always_redraw(lambda: plot_tracker(self.axes, self.lam.get_value()))
        self.readout = lambda_readout(self.axes, self.lam)
        self.lit = VGroup()
        self.marks = VGroup()
        self.ring = VGroup()
        self.add(plane, self.lines, state, self.plot, self.tracker, self.readout)
        self.bring_to_front(self.veil)

    def light_root(self, index):
        root, direction, color = ROOTS[index]
        lit = lit_line(self.left, direction, color)
        self.ring = origin_ring(self.left, radius=0.2)
        mark = root_mark(self.axes, root, color)
        self.lit.add(lit)
        self.marks.add(mark)
        self.play(Create(lit), run_time=0.8)
        self.play(GrowFromCenter(self.ring), GrowFromCenter(mark), run_time=0.6, rate_func=spring)

    def eigenvectors(self, line):
        rows = VGroup(
            tex(r"A - 3I", r"\sim", r"\begin{bmatrix} 1 & -1 \\ 0 & 0 \end{bmatrix}", r"\quad \mathbf x = x_2", r"\begin{bmatrix} 1 \\ 1 \end{bmatrix}", colors=(Palette.yellow, None, None, None, Palette.yellow), font_size=40),
            tex(r"A + I", r"\sim", r"\begin{bmatrix} 1 & 1 \\ 0 & 0 \end{bmatrix}", r"\quad \mathbf x = x_2", r"\begin{bmatrix} 1 \\ -1 \end{bmatrix}", colors=(Palette.blue, None, None, None, Palette.blue), font_size=40),
        ).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        rows[1].shift(RIGHT * (rows[0][1].get_x() - rows[1][1].get_x()))
        rows.move_to(np.array([PLOT_CENTER[0], 0.6, 0]))
        line = self.say(r"The line that lands on $\mathbf 0$ holds the eigenvectors.", line, hold=0.2)
        self.play(FadeOut(VGroup(self.plot, self.readout, self.marks, self.tracker)), run_time=0.6)
        self.play(self.lam.animate.set_value(3), run_time=1.6, rate_func=spring_soft)
        self.play(FadeIn(rows[0], shift=LEFT * 0.15), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"Row reduce $A - \lambda I$ at each root to find them.", line, hold=0.2)
        self.play(self.lam.animate.set_value(-1), run_time=2.2, rate_func=spring_soft)
        self.play(FadeIn(rows[1], shift=LEFT * 0.15), run_time=0.8)
        self.wait(Timing.read_short)
        self.play(FadeIn(self.veil), run_time=0.6)
        self.remove(*[m for m in self.mobjects if m is not self.veil and m is not line])
        self.add(self.veil)
        return line

    def three_by_three(self, line):
        original = named("M", matrix([[str(v) for v in row] for row in M]), font_size=44)
        minus_mat = diagonal_matrix_tex(minus_lambda_rows(M), font_size=40, h_buff=1.55)
        minus = named(r"M - \lambda I", minus_mat, font_size=44)
        VGroup(original, minus).arrange(RIGHT, buff=0.9).move_to(UP * 1.75).set_z_index(21)
        steps = cofactor_steps().move_to(DOWN * 1.1).set_z_index(21)
        values = tex(r"\lambda", "=", M_ROOTS, colors=(Palette.glow, None, Palette.glow), font_size=46).next_to(steps, RIGHT, buff=0.6)
        values.set_z_index(21)
        VGroup(steps, values).move_to(DOWN * 1.1)
        line = self.say(r"A $3 \times 3$ matrix gives a polynomial of degree 3.", line, hold=0.2)
        self.play(FadeIn(original, shift=UP * 0.1), run_time=0.7)
        self.play(FadeIn(minus, shift=LEFT * 0.2), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"Row 1 has two zeros, so only one term survives.", line, hold=0.2)
        first_row = minus_mat.get_rows()[0]
        box = SurroundingRectangle(first_row, color=Palette.glow, buff=0.14, stroke_width=3).set_z_index(21)
        self.play(Create(box), run_time=0.7)
        self.play(first_row[1].animate.set_color(Palette.text_muted), first_row[2].animate.set_color(Palette.text_muted), run_time=0.5)
        self.play(FadeIn(steps[0], shift=DOWN * 0.1), run_time=0.9)
        self.wait(Timing.read_short)
        line = self.say(r"The minor is triangular, so its determinant is its diagonal.", line, hold=0.2)
        self.play(FadeIn(steps[1], shift=DOWN * 0.1), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"Leave it factored and read off the three roots.", line, hold=0.2)
        self.play(FadeIn(values, shift=LEFT * 0.15), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(original, minus, box, steps, values)), run_time=0.6)
        return line

    def multiplicity(self, line):
        triangular = named("B", diagonal_matrix_tex([[str(v) for v in row] for row in B], font_size=40, h_buff=0.95), font_size=44)
        poly = tex(r"\det(B - \lambda I)", "=", r"(2 - \lambda)^2", r"(4 - \lambda)", colors=(None, None, Palette.glow, None), font_size=44)
        top = VGroup(triangular, poly).arrange(RIGHT, buff=0.9).move_to(UP * 2.35).set_z_index(21)
        graph, marks, notes = repeated_plot()
        stage = VGroup(graph, marks, notes).set_z_index(21)
        line = self.say(r"Here the factor $2 - \lambda$ appears twice.", line, hold=0.2)
        self.play(FadeIn(top, shift=UP * 0.1), run_time=0.8)
        self.play(FadeIn(graph[:3]), Create(graph[3]), run_time=1.4)
        self.play(GrowFromCenter(marks[0]), GrowFromCenter(marks[1]), run_time=0.6, rate_func=spring)
        self.wait(Timing.beat)
        line = self.say(r"So $\lambda = 2$ has \emph{algebraic multiplicity} 2.", line, hold=0.2)
        self.play(FadeIn(notes, shift=UP * 0.1), run_time=0.7)
        self.wait(Timing.read_short)
        line = self.say(r"Day 31 asks whether a double root gives two eigenvectors.", line, hold=Timing.read_long)
        self.play(FadeOut(VGroup(top, stage)), FadeOut(line), run_time=0.6)
        self.remove(self.veil)
        return None


class FigSnapshots(Scene):
    def construct(self):
        panels = VGroup(*[self.snapshot(lam) for lam in (-1, 1, 3)]).arrange(RIGHT, buff=0.7)
        self.add(panels)
        fit_to_frame(self)

    @staticmethod
    def snapshot(lam):
        plane = left_plane(origin=(0, 0), unit=0.6, reach=5)
        parts = VGroup(plane, faint_lines(plane), plane_state(plane, lam, reach=5, stroke_width=5))
        for root, direction, color in ROOTS:
            if root == lam:
                parts.add(lit_line(plane, direction, color), origin_ring(plane, radius=0.2))
        heading = tex(r"\lambda", "=", str(lam).replace("-", "{-}"), colors=(Palette.glow, None, Palette.glow), font_size=44)
        heading.next_to(plane, UP, buff=0.3)
        value = tex(r"\det(A - \lambda I)", "=", str(char_poly(lam)), colors=(None, None, square_color(lam) if char_poly(lam) else Palette.glow), font_size=36)
        value.next_to(plane, DOWN, buff=0.3)
        return VGroup(heading, parts, value)


class FigCofactor(Scene):
    def construct(self):
        minus = named(r"M - \lambda I", diagonal_matrix_tex(minus_lambda_rows(M), font_size=40, h_buff=1.55), font_size=44)
        first_row = minus[1].get_rows()[0]
        first_row[1].set_color(Palette.text_muted)
        first_row[2].set_color(Palette.text_muted)
        box = SurroundingRectangle(first_row, color=Palette.glow, buff=0.14, stroke_width=3)
        steps = cofactor_steps()
        values = tex(r"\lambda", "=", M_ROOTS, colors=(Palette.glow, None, Palette.glow), font_size=46)
        self.add(VGroup(VGroup(minus, box), steps, values).arrange(DOWN, buff=0.6))
        fit_to_frame(self)


class FigMultiplicity(Scene):
    def construct(self):
        poly = tex(r"\det(B - \lambda I)", "=", r"(2 - \lambda)^2", r"(4 - \lambda)", colors=(None, None, Palette.glow, None), font_size=44)
        graph, marks, notes = repeated_plot(center=(0, 0), size=(8.0, 4.4))
        poly.next_to(graph, UP, buff=0.4)
        self.add(poly, graph, marks, notes)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = left_plane()
        plot = plot_panel()
        axes = plot[0]
        self.add(plane, faint_lines(plane), plane_state(plane, 3), lit_line(plane, V1, Palette.yellow), origin_ring(plane, radius=0.2))
        self.add(plot, plot_tracker(axes, 3), root_mark(axes, 3, Palette.yellow), root_mark(axes, -1, Palette.blue))
        VGroup(*self.mobjects).shift(DOWN * 0.45)
