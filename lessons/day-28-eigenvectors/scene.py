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
    fit_to_frame,
    line_through_origin,
    make_plane,
    matrix,
    morph_matrix,
    plane_at,
    plate_for,
    scrim,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (0.0, -0.4)
PLANE_UNIT = 1.0
A = ((3, -2), (1, 0))
A_INVERSE = ((0, 1), (-0.5, 1.5))
A_MINUS_2I = ((1, -2), (1, -2))
U = (-1, 1)
V1 = (2, 1)
V2 = (1, 1)
FAN_LENGTH = 1.8
FAN_DEGREES = (0, math.degrees(math.atan2(1, 2)), 45, 67.5, 90, 112.5, 135, 157.5)
EIGEN_DEGREES = {FAN_DEGREES[1]: Palette.yellow, 45: Palette.blue}
TRIANGULAR = ((2, 5, 1), (0, -1, 4), (0, 0, 3))
BASIS_COLORS = (Palette.i_hat, Palette.j_hat)


def tex(*parts, colors=(), font_size=44):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def apply_rows(rows, point):
    return (rows[0][0] * point[0] + rows[0][1] * point[1], rows[1][0] * point[0] + rows[1][1] * point[1])


def basis_matrix(rows):
    """A 2x2 matrix whose first column is green (where e1 lands) and second red (where e2 lands)."""
    mat = matrix([[str(entry) for entry in row] for row in rows])
    for index, color in enumerate(BASIS_COLORS):
        mat.get_columns()[index].set_color(color)
    return mat


def named(name, mat, font_size=44):
    return VGroup(MathTex(name, "=", color=Palette.text, font_size=font_size), mat).arrange(RIGHT, buff=0.2)


def corner_panel(content, corner=UL):
    content.to_corner(corner, buff=0.55)
    return VGroup(plate_for(content), content).set_z_index(10)


def name_label(tex_string, color, point, direction, font_size=38):
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.08).next_to(point, direction, buff=0.12)


def tip_glow(point, scale=1.0):
    halo = Dot(point, radius=0.22 * scale, color=Palette.glow, fill_opacity=0.22)
    core = Dot(point, radius=0.075 * scale, color=Palette.glow)
    return VGroup(halo, core)


def origin_ring(plane):
    return Circle(radius=0.24, color=Palette.glow, stroke_width=4).move_to(plane.c2p(0, 0))


def safe_arrow(plane, coords, color, stroke_width=6):
    """An arrow to coords, or a dot at the origin once it has shrunk to nothing."""
    if math.hypot(*coords) < 0.08:
        return Dot(plane.c2p(0, 0), radius=0.08, color=color)
    return vector_arrow(coords, color, plane, stroke_width=stroke_width)


def riding_arrow(plane, live, coords, color, stroke_width=6):
    return safe_arrow(plane, tuple(live.point(coords)), color, stroke_width)


def fan_directions():
    angles = [math.radians(degrees + turn) for degrees in FAN_DEGREES for turn in (0, 180)]
    return [(FAN_LENGTH * math.cos(angle), FAN_LENGTH * math.sin(angle)) for angle in angles]


def is_eigen(direction):
    return any(abs(math.cos(math.radians(degrees)) * direction[1] - math.sin(math.radians(degrees)) * direction[0]) < 1e-6 for degrees in EIGEN_DEGREES)


def eigen_color(direction):
    for degrees, color in EIGEN_DEGREES.items():
        if abs(math.cos(math.radians(degrees)) * direction[1] - math.sin(math.radians(degrees)) * direction[0]) < 1e-6:
            return color
    return Palette.purple_gray


def off_line(direction, image):
    """The sine of the angle between image and the line through direction: 0 when image stays on that line."""
    length = math.hypot(*image)
    if length < 1e-6:
        return 0.0
    unit = np.array(direction) / math.hypot(*direction)
    return abs(unit[0] * image[1] - unit[1] * image[0]) / length


def fan_arrow(plane, image, direction):
    arrow = vector_arrow(image, Palette.purple_gray, plane, stroke_width=5)
    knocked = min(1.0, off_line(direction, image) / 0.3)
    return arrow.set_opacity(1.0 - 0.72 * knocked)


def fan_lines(plane, opacity=0.4):
    return VGroup(*[line_through_origin(plane, fan_directions()[2 * i], Palette.purple_gray, 2.5, dashed=True, opacity=opacity) for i in range(len(FAN_DEGREES))])


def eigen_lines(plane):
    return VGroup(line_through_origin(plane, V1, Palette.yellow, 4.5), line_through_origin(plane, V2, Palette.blue, 4.5))


def eigen_labels(plane):
    return VGroup(
        name_label(r"\lambda = 2", Palette.yellow, plane.c2p(5.4, 2.7), DR, font_size=40),
        name_label(r"\lambda = 1", Palette.blue, plane.c2p(3.5, 3.5), LEFT, font_size=40),
    )


def settled_fan(plane, rows=A, ghosts=False):
    """The fan after the map `rows`: knocked-off arrows faded, eigen arrows colored, glow on their tips."""
    parts = VGroup(fan_lines(plane, opacity=0.3), eigen_lines(plane))
    for direction in fan_directions():
        image = apply_rows(rows, direction)
        if ghosts:
            parts.add(vector_arrow(direction, Palette.purple_gray, plane, stroke_width=3).set_opacity(0.25))
        if is_eigen(direction):
            parts.add(vector_arrow(image, eigen_color(direction), plane, stroke_width=6), tip_glow(plane.c2p(*image)))
        else:
            parts.add(fan_arrow(plane, image, direction))
    return parts


def line_ends(plane, direction):
    return clip_line_to_box((direction[1], -direction[0], 0), plane.x_range[:2], plane.y_range[:2])


def moving_line(plane, live, direction, color, stroke_width=4.5):
    """The image of the whole line through direction under live's current matrix."""
    start, end = (live.point(point) for point in line_ends(plane, direction))
    if math.hypot(*(end - start)) < 0.1:
        return Dot(plane.c2p(0, 0), radius=0.08, color=color)
    return Line(plane.c2p(*start), plane.c2p(*end), color=color, stroke_width=stroke_width)


def triangular_matrix(entries, h_buff=1.95):
    mat = Matrix(entries, v_buff=0.72, h_buff=h_buff, bracket_h_buff=0.18)
    mat.set_color(Palette.text)
    return mat


def shifted_entries(shift):
    """Entries of T - shift*I, with the diagonal written out as 'a - shift'."""
    rows = []
    for i, row in enumerate(TRIANGULAR):
        rows.append([diagonal_entry(value, shift) if i == j else str(value) for j, value in enumerate(row)])
    return rows


def diagonal_entry(value, shift):
    if isinstance(shift, str):
        return f"{value} - {shift}"
    return str(value - shift)


def paint_diagonal(mat, color=Palette.glow):
    for index in range(3):
        mat.get_rows()[index][index].set_color(color)
    return mat


class Lesson(LessonScene):
    day = 28
    title = "Eigenvectors and eigenvalues"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        self.plane = plane
        self.live = LiveTransform()
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.meet_a()
        line = self.knock_u(line)
        line = self.stretch_v1(line)
        line = self.fan(line)
        line = self.definition(line)
        line = self.stretch_factors(line)
        line = self.flip_and_crush(line)
        line = self.zero_eigenvalue(line)
        line = self.eigenspace(line)
        line = self.triangular(line)
        self.close_episode(
            r"An eigenvector stays on its own line when $A$ acts.\\"
            r"Its eigenvalue $\lambda$ is the factor it gets stretched by.",
            *self.mobjects,
        )

    def move_grid(self, rows, run_time=2.6, rate_func=spring_soft):
        self.play(self.live.apply(rows), run_time=run_time, rate_func=rate_func)

    def meet_a(self):
        plane = self.plane
        self.a_panel = corner_panel(named("A", basis_matrix(A)))
        line = self.say(r"Here is a matrix $A$, and it moves the whole plane.", hold=0.2)
        self.play(FadeIn(self.a_panel, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)

        self.grid = always_redraw(lambda: self.live.grid(plane, opacity=0.8))
        self.play(plane.animate.set_opacity(0.3), FadeIn(self.grid), run_time=0.8)
        self.bring_to_front(self.a_panel)
        self.u_arrow = vector_arrow(U, Palette.purple_gray, plane)
        self.u_line = line_through_origin(plane, U, Palette.purple_gray, 3, dashed=True)
        self.u_label = name_label(r"\mathbf u", Palette.purple_gray, plane.c2p(*U), UR)
        line = self.say(r"Pick a vector $\mathbf u$ and draw the line through it.", line, hold=0.2)
        self.play(GrowArrow(self.u_arrow), FadeIn(self.u_label), run_time=1.1, rate_func=spring_soft)
        self.play(Create(self.u_line), run_time=1.2)
        self.bring_to_front(self.u_arrow, self.u_label)
        self.wait(Timing.read_short)
        return line

    def knock_u(self, line):
        plane = self.plane
        riding = always_redraw(lambda: riding_arrow(plane, self.live, U, Palette.teal))
        self.add(riding)
        self.bring_to_front(self.u_arrow, self.u_label, self.a_panel)
        line = self.say(r"Now let $A$ act, and follow where $\mathbf u$ goes.", line, hold=0.2)
        self.move_grid(A)
        landing = apply_rows(A, U)
        label = name_label(r"A\mathbf u", Palette.teal, plane.c2p(*landing), DOWN)
        line = self.say(r"$A\mathbf u$ lands far off the line through $\mathbf u$.", line, hold=0.2)
        self.play(FadeIn(label, shift=UP * 0.1), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        self.play(FadeOut(label), run_time=0.4)
        self.play(self.live.apply(A_INVERSE), FadeOut(VGroup(riding, self.u_arrow, self.u_label, self.u_line)), run_time=1.4, rate_func=spring_soft)
        return line

    def stretch_v1(self, line):
        plane = self.plane
        v_arrow = vector_arrow(V1, Palette.yellow, plane)
        v_line = line_through_origin(plane, V1, Palette.yellow, 3, dashed=True, opacity=0.8)
        v_label = name_label(r"\mathbf v_1", Palette.yellow, plane.c2p(*V1), DR)
        line = self.say(r"Now try $\mathbf v_1 = (2, 1)$ and the line through it.", line, hold=0.2)
        self.play(GrowArrow(v_arrow), FadeIn(v_label), run_time=1.1, rate_func=spring_soft)
        self.play(Create(v_line), run_time=1.2)

        riding = always_redraw(lambda: riding_arrow(plane, self.live, V1, Palette.teal))
        self.add(riding)
        self.bring_to_front(v_arrow, v_label, self.a_panel)
        line = self.say(r"This time the arrow slides along its own line.", line, hold=0.2)
        self.move_grid(A)
        landing = apply_rows(A, V1)
        glow = tip_glow(plane.c2p(*landing))
        label = name_label(r"A\mathbf v_1 = 2\,\mathbf v_1", Palette.teal, plane.c2p(*landing), UL, font_size=40)
        line = self.say(r"$A$ only doubled it and never turned it.", line, hold=0.2)
        self.play(GrowFromCenter(glow), run_time=0.6, rate_func=spring)
        self.play(FadeIn(label, shift=DOWN * 0.1), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(label, glow)), run_time=0.4)
        self.play(self.live.apply(A_INVERSE), FadeOut(VGroup(riding, v_arrow, v_label, v_line)), run_time=1.4, rate_func=spring_soft)
        return line

    def fan(self, line):
        plane = self.plane
        directions = fan_directions()
        lines = fan_lines(plane)
        still = VGroup(*[vector_arrow(d, Palette.purple_gray, plane, stroke_width=5) for d in directions])
        line = self.say(r"Now draw sixteen directions at once, each with its line.", line, hold=0.2)
        self.play(LaggedStart(*[GrowArrow(arrow) for arrow in still], lag_ratio=0.06), run_time=1.8)
        self.play(Create(lines, lag_ratio=0.1), run_time=1.4)
        self.bring_to_front(still, self.a_panel)

        live_fan = VGroup(*[always_redraw(lambda d=d: fan_arrow(plane, self.live.point(d), d)) for d in directions])
        self.remove(still)
        self.add(live_fan)
        self.bring_to_front(self.a_panel)
        line = self.say(r"Apply $A$, and almost every arrow is knocked off its line.", line, hold=0.2)
        self.move_grid(A, run_time=5.0, rate_func=smooth)
        self.wait(Timing.read_short)
        line = self.say(r"Two lines survive, and $A$ only stretches along them.", line, hold=0.2)
        self.light_eigen_lines(live_fan, directions)
        line = self.say(r"Those surviving arrows are the \emph{eigenvectors} of $A$.", line, hold=Timing.read_short)
        knocked = [arrow for arrow, d in zip(live_fan, directions) if not is_eigen(d)]
        self.play(FadeOut(VGroup(*knocked)), FadeOut(lines), run_time=0.8)
        return line

    def light_eigen_lines(self, live_fan, directions):
        plane = self.plane
        self.eigen_lines = eigen_lines(plane)
        colored = VGroup()
        glows = VGroup()
        for arrow, direction in zip(live_fan, directions):
            if is_eigen(direction):
                image = self.live.point(direction)
                self.remove(arrow)
                colored.add(vector_arrow(image, eigen_color(direction), plane, stroke_width=6))
                glows.add(tip_glow(plane.c2p(*image)))
        self.add(colored)
        self.play(Create(self.eigen_lines[0]), Create(self.eigen_lines[1]), run_time=1.2)
        self.bring_to_front(colored)
        self.play(LaggedStart(*[GrowFromCenter(glow) for glow in glows], lag_ratio=0.15), run_time=1.0)
        self.labels = eigen_labels(plane)
        self.play(FadeIn(self.labels[0], shift=LEFT * 0.1), run_time=0.6, rate_func=spring)
        self.play(FadeIn(self.labels[1], shift=LEFT * 0.1), run_time=0.6, rate_func=spring)
        self.eigen_arrows = VGroup(colored, glows)
        self.wait(Timing.read_short)

    def definition(self, line):
        veil = scrim().set_z_index(20)
        rule = tex(r"A", r"\mathbf v", "=", r"\lambda", r"\mathbf v", colors=(None, Palette.yellow, None, Palette.glow, Palette.yellow), font_size=110)
        nonzero = tex(r"\mathbf v \ne \mathbf 0", font_size=56)
        examples = VGroup(
            tex(r"A", r"\mathbf v_1", "=", "2", r"\,\mathbf v_1", colors=(None, Palette.yellow, None, Palette.glow, Palette.yellow)),
            tex(r"A", r"\mathbf v_2", "=", "1", r"\,\mathbf v_2", colors=(None, Palette.blue, None, Palette.glow, Palette.blue)),
        ).arrange(RIGHT, buff=1.6)
        board = VGroup(rule, nonzero, examples).arrange(DOWN, buff=0.55).move_to(UP * 0.45).set_z_index(21)
        line = self.say(r"An eigenvector is a nonzero $\mathbf v$ with $A\mathbf v = \lambda\mathbf v$.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(Write(rule), run_time=1.4)
        self.play(FadeIn(nonzero, shift=UP * 0.1), run_time=0.6)
        self.wait(Timing.read_short)
        line = self.say(r"Its \emph{eigenvalue} $\lambda$ says how much $A$ stretches $\mathbf v$.", line, hold=0.2)
        self.play(Indicate(rule[3], color=Palette.glow, scale_factor=1.25), run_time=0.9)
        self.play(FadeIn(examples, shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)

        self.remove(*self.eigen_arrows.get_family(), *self.labels.get_family())
        self.live = LiveTransform()
        self.play(FadeOut(board), FadeOut(veil), run_time=0.8)
        return line

    def stretch_factors(self, line):
        plane = self.plane
        points = [(t * V1[0], t * V1[1], Palette.yellow) for t in (-1, -0.5, 0.5, 1)]
        points += [(s * V2[0], s * V2[1], Palette.blue) for s in (-2, -1, 1, 2)]
        ghosts = VGroup(*[Dot(plane.c2p(x, y), radius=0.07, color=color).set_opacity(0.35) for x, y, color in points])
        riders = VGroup(*[always_redraw(lambda x=x, y=y, c=color: Dot(plane.c2p(*self.live.point((x, y))), radius=0.1, color=c)) for x, y, color in points])
        line = self.say(r"Apply $A$ once more and follow points on both lines.", line, hold=0.2)
        self.add(ghosts)
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in riders], lag_ratio=0.08), FadeIn(self.labels), run_time=1.2)
        self.move_grid(A, run_time=3.0)
        line = self.say(r"On the yellow line every point moves twice as far out.", line, hold=0.2)
        self.play(*[Flash(dot.get_center(), color=Palette.glow, line_length=0.18, flash_radius=0.22) for dot in riders[:4]], run_time=1.0)
        self.wait(Timing.beat)
        line = self.say(r"On the blue line every point stays exactly where it was.", line, hold=0.2)
        self.play(*[Flash(dot.get_center(), color=Palette.glow, line_length=0.18, flash_radius=0.22) for dot in riders[4:]], run_time=1.0)
        self.wait(Timing.beat)
        self.play(FadeOut(riders), FadeOut(ghosts), FadeOut(self.labels), run_time=0.6)
        self.move_grid(A_INVERSE, run_time=1.4)
        return line

    def flip_and_crush(self, line):
        plane = self.plane
        stretch = ValueTracker(2.0)
        ends = line_ends(plane, V1)
        image_line = always_redraw(lambda: self.scaled_line(ends, stretch.get_value()))
        image_arrow = always_redraw(lambda: safe_arrow(plane, (stretch.get_value() * V1[0], stretch.get_value() * V1[1]), Palette.teal, 7))
        v_arrow = vector_arrow(V1, Palette.yellow, plane)
        readout = self.stretch_readout(stretch)
        line = self.say(r"The size of $\lambda$ is the stretch, and its sign matters too.", line, hold=0.2)
        self.play(FadeOut(self.eigen_lines[1]), FadeIn(readout), run_time=0.7)
        self.add(image_line)
        self.bring_to_front(self.eigen_lines[0])
        self.play(GrowArrow(v_arrow), run_time=0.8, rate_func=spring_soft)
        self.add(image_arrow)
        self.bring_to_front(v_arrow, readout, self.a_panel)

        line = self.say(r"A negative $\lambda$ would flip the arrow but keep its line.", line, hold=0.2)
        self.play(stretch.animate.set_value(-1.0), run_time=2.2, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"And $\lambda = 0$ would crush the whole line onto $\mathbf 0$.", line, hold=0.2)
        self.play(stretch.animate.set_value(0.0), run_time=2.0, rate_func=spring_soft)
        ring = origin_ring(plane)
        self.play(GrowFromCenter(ring), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(image_line, image_arrow, v_arrow, readout, ring)), FadeIn(self.eigen_lines[1]), run_time=0.7)
        return line

    def scaled_line(self, ends, amount):
        start, end = amount * ends[0], amount * ends[1]
        if math.hypot(*(end - start)) < 0.1:
            return Dot(self.plane.c2p(0, 0), radius=0.08, color=Palette.teal)
        return Line(self.plane.c2p(*start), self.plane.c2p(*end), color=Palette.teal, stroke_width=12, stroke_opacity=0.45)

    def stretch_readout(self, stretch):
        label = MathTex(r"\lambda =", color=Palette.glow, font_size=48)
        number = DecimalNumber(stretch.get_value(), num_decimal_places=1, color=Palette.glow, font_size=48)
        widest = VGroup(label, number.copy().set_value(-1.0).next_to(label, RIGHT, buff=0.18)).move_to(np.array([2.6, 3.2, 0]))
        number.add_updater(lambda m: m.set_value(stretch.get_value()).next_to(label, RIGHT, buff=0.18).set_z_index(10))
        number.next_to(label, RIGHT, buff=0.18)
        return VGroup(plate_for(widest, padding=0.22), label, number).set_z_index(10)

    def zero_eigenvalue(self, line):
        veil = scrim().set_z_index(20)
        chain = VGroup(
            MathTex(r"0 \text{ is an eigenvalue of } A", color=Palette.text, font_size=48),
            MathTex(r"\iff A\mathbf v = 0\,\mathbf v = \mathbf 0 \text{ for some } \mathbf v \ne \mathbf 0", color=Palette.text, font_size=48),
            MathTex(r"\iff A \text{ is not invertible}", color=Palette.text, font_size=48),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(UP * 0.5).set_z_index(21)
        for step in chain[1:]:
            step[0][0].set_color(Palette.glow)
        line = self.say(r"An eigenvalue of 0 means $A$ sends some line to $\mathbf 0$.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(FadeIn(chain[0], shift=UP * 0.1), run_time=0.7)
        self.play(FadeIn(chain[1], shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        line = self.say(r"By Day 19, that happens exactly when $A$ is not invertible.", line, hold=0.2)
        self.play(FadeIn(chain[2], shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        self.play(FadeOut(chain), FadeOut(veil), run_time=0.7)
        return line

    def eigenspace(self, line):
        steps = VGroup(
            tex(r"A\mathbf v", "=", r"\lambda\mathbf v"),
            tex(r"A\mathbf v - \lambda I\mathbf v", "=", r"\mathbf 0"),
            tex(r"(A - \lambda I)\mathbf v", "=", r"\mathbf 0"),
        ).arrange(DOWN, buff=0.35)
        for step in steps[1:]:
            step.shift(RIGHT * (steps[0][1].get_x() - step[1].get_x()))
        steps.to_corner(UL, buff=0.55)
        plate = plate_for(steps).set_z_index(10)
        steps.set_z_index(11)
        line = self.say(r"To find the eigenvectors for a $\lambda$, move $\lambda\mathbf v$ left.", line, hold=0.2)
        self.play(FadeOut(self.a_panel), FadeIn(plate), FadeIn(steps[0]), run_time=0.8)
        self.play(FadeIn(steps[1], shift=DOWN * 0.1), run_time=0.8)
        self.play(FadeIn(steps[2], shift=DOWN * 0.1), run_time=0.8)
        self.wait(Timing.read_short)

        shifted = named(r"A - 2I", basis_matrix(A_MINUS_2I)).next_to(steps, DOWN, buff=0.5).align_to(steps, LEFT).set_z_index(11)
        line = self.say(r"For $\lambda = 2$, the matrix $A - 2I$ squashes the plane flat.", line, hold=0.2)
        self.play(plate.animate.become(plate_for(VGroup(steps, shifted)).set_z_index(10)), FadeIn(shifted), run_time=0.8)
        self.collapse_yellow_line()
        line = self.say(r"The whole yellow line lands on $\mathbf 0$.", line, hold=Timing.read_short)
        line = self.solve_for_line(line, plate, VGroup(steps, shifted))
        return line

    def collapse_yellow_line(self):
        plane = self.plane
        self.remove(self.eigen_lines[0])
        yellow = always_redraw(lambda: moving_line(plane, self.live, V1, Palette.yellow))
        self.add(yellow)
        self.bring_to_front(self.eigen_lines[1])
        self.move_grid(A_MINUS_2I, run_time=3.2)
        ring = origin_ring(plane)
        self.play(GrowFromCenter(ring), run_time=0.6, rate_func=spring)
        self.collapse_parts = VGroup(yellow, ring)

    def solve_for_line(self, line, plate, old):
        reduction = VGroup(
            MathTex(r"\begin{bmatrix} 1 & -2 & 0 \\ 1 & -2 & 0 \end{bmatrix}", r"\sim", r"\begin{bmatrix} 1 & -2 & 0 \\ 0 & 0 & 0 \end{bmatrix}", color=Palette.text, font_size=42),
            tex(r"\mathbf x", "=", r"x_2", r"\begin{bmatrix} 2 \\ 1 \end{bmatrix}", colors=(Palette.yellow, None, None, Palette.yellow), font_size=44),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT).to_corner(UL, buff=0.55).set_z_index(11)
        line = self.say(r"Row reducing $[\,A - 2I \mid \mathbf 0\,]$ leaves one free variable.", line, hold=0.2)
        self.play(FadeOut(old), plate.animate.become(plate_for(reduction).set_z_index(10)), run_time=0.6)
        self.play(FadeIn(reduction[0]), run_time=0.9)
        self.play(FadeIn(reduction[1], shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"So the \emph{eigenspace} for $\lambda$ is $\operatorname{Nul}(A - \lambda I)$.", line, hold=Timing.read_short)
        self.play(FadeOut(VGroup(plate, reduction, self.collapse_parts, self.grid, self.eigen_lines[1])), run_time=0.8)
        self.live = LiveTransform()
        return line

    def triangular(self, line):
        veil = scrim().set_z_index(20)
        original = named("T", triangular_matrix([[str(v) for v in row] for row in TRIANGULAR], h_buff=1.0), font_size=48)
        shifted_mat = paint_diagonal(triangular_matrix(shifted_entries(r"\lambda")))
        shifted = named(r"T - \lambda I", shifted_mat, font_size=48)
        VGroup(original, shifted).arrange(RIGHT, buff=1.0).move_to(UP * 0.7).set_z_index(21)
        paint_diagonal(original[1], Palette.glow)
        self.play(FadeIn(veil), FadeIn(original), run_time=0.9)
        line = self.say(r"Last, take a triangular matrix $T$.", line, hold=0.2)
        self.wait(Timing.beat)
        line = self.say(r"Subtracting $\lambda I$ only changes the diagonal, so it stays triangular.", line, hold=0.2)
        self.play(FadeIn(shifted), run_time=1.0)
        self.wait(Timing.read_short)

        at_three = paint_diagonal(triangular_matrix(shifted_entries(3))).move_to(shifted_mat).set_z_index(21)
        at_three.get_rows()[2][2].set_color(Palette.glow)
        three_name = MathTex(r"T - 3I", "=", color=Palette.text, font_size=48).move_to(shifted[0]).set_z_index(21)
        line = self.say(r"At $\lambda = 3$ a diagonal entry hits 0, leaving a free variable.", line, hold=0.2)
        self.play(FadeOut(shifted[0]), FadeIn(three_name), run_time=0.5)
        morph_matrix(self, shifted_mat, at_three, run_time=1.2, rate_func=spring)
        empty = SurroundingRectangle(shifted_mat.get_rows()[2], color=Palette.glow, buff=0.12, stroke_width=3).set_z_index(21)
        self.play(Create(empty), run_time=0.7)
        self.wait(Timing.read_short)
        return self.read_diagonal(line, original, VGroup(shifted_mat, three_name, empty), veil)

    def read_diagonal(self, line, original, leftovers, veil):
        diagonal = [original[1].get_rows()[i][i] for i in range(3)]
        values = tex(r"\lambda", "=", "2", ",", "-1", ",", "3", colors=(Palette.glow, None, Palette.glow, None, Palette.glow, None, Palette.glow), font_size=56)
        values.move_to(DOWN * 1.4).set_z_index(21)
        line = self.say(r"So the eigenvalues of $T$ are exactly its diagonal entries.", line, hold=0.2)
        self.play(FadeIn(values[:2]), FadeIn(values[3]), FadeIn(values[5]), run_time=0.5)
        self.play(*[TransformFromCopy(entry, values[k]) for entry, k in zip(diagonal, (2, 4, 6))], run_time=1.4, rate_func=spring)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(original, leftovers, values)), run_time=0.7)
        self.remove(veil)
        return line


def scene_plane():
    plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
    plane.set_opacity(0.55)
    return plane


class FigKnockedOff(Scene):
    def construct(self):
        plane = scene_plane()
        panel = corner_panel(named("A", basis_matrix(A)))
        self.add(plane, settled_fan(plane, ghosts=True), eigen_labels(plane), panel)


class FigStretchFactors(Scene):
    def construct(self):
        plane = scene_plane()
        self.add(plane, eigen_lines(plane))
        for t in (-1, -0.5, 0.5, 1):
            start, end = (t * V1[0], t * V1[1]), (2 * t * V1[0], 2 * t * V1[1])
            self.add(Dot(plane.c2p(*start), radius=0.08, color=Palette.yellow).set_opacity(0.4))
            self.add(Arrow(plane.c2p(*start), plane.c2p(*end), buff=0.12, color=Palette.glow, stroke_width=4, max_tip_length_to_length_ratio=0.3))
            self.add(Dot(plane.c2p(*end), radius=0.11, color=Palette.yellow))
        for s in (-2, -1, 1, 2):
            point = plane.c2p(s * V2[0], s * V2[1])
            self.add(Dot(point, radius=0.11, color=Palette.blue), Circle(radius=0.2, color=Palette.glow, stroke_width=3).move_to(point))
        self.add(eigen_labels(plane), corner_panel(named("A", basis_matrix(A))))


class FigSquash(Scene):
    def construct(self):
        before = self.small_plane(np.eye(2), show_yellow=True)
        after = self.small_plane(np.array(A_MINUS_2I, dtype=float), show_yellow=False)
        arrow = VGroup(Arrow(LEFT * 0.6, RIGHT * 0.6, color=Palette.text, stroke_width=5), MathTex(r"A - 2I", color=Palette.text, font_size=40))
        arrow[1].next_to(arrow[0], UP, buff=0.15)
        VGroup(before, arrow, after).arrange(RIGHT, buff=0.4)
        self.add(before, arrow, after)
        fit_to_frame(self)

    @staticmethod
    def small_plane(rows, show_yellow):
        plane = make_plane(x_range=(-4, 4, 1), y_range=(-4, 4, 1), x_length=6, y_length=6)
        plane.set_opacity(0.35)
        live = LiveTransform(rows)
        parts = VGroup(plane, live.grid(plane, opacity=0.8), line_through_origin(plane, V2, Palette.blue, 4.5))
        if show_yellow:
            parts.add(line_through_origin(plane, V1, Palette.yellow, 4.5), vector_arrow(V1, Palette.yellow, plane), name_label(r"\mathbf v_1", Palette.yellow, plane.c2p(*V1), DR))
        else:
            parts.add(origin_ring(plane), tip_glow(plane.c2p(0, 0)))
        return parts


class Poster(Scene):
    def construct(self):
        plane = scene_plane()
        formula = backed(tex(r"A", r"\mathbf v", "=", r"\lambda", r"\mathbf v", colors=(None, Palette.yellow, None, Palette.glow, Palette.yellow), font_size=72), padding=0.25)
        formula.to_corner(UL, buff=0.6)
        self.add(plane, settled_fan(plane, ghosts=True), formula)
