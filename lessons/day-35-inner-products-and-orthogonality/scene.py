import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    Palette,
    Timing,
    arrow_between,
    backed,
    column,
    fit_to_frame,
    line_through_origin,
    plane_at,
    plate_for,
    scrim,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (0.3, -0.1)
PLANE_UNIT = 1.2
V = (3, 2)
W = (-1, 2)
U = (-2, 3)
Y = (5, -1)
V_ANGLE = math.atan2(V[1], V[0])
W_LENGTH = math.hypot(*W)
THETA_START = math.degrees(math.atan2(W[1], W[0]) - V_ANGLE)
PANEL_Z = 10


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def spun(theta_degrees, length=W_LENGTH):
    """The vector at angle theta (degrees) counterclockwise from v."""
    angle = V_ANGLE + math.radians(theta_degrees)
    return (length * math.cos(angle), length * math.sin(angle))


def unit(vector):
    length = math.hypot(*vector)
    return (vector[0] / length, vector[1] / length)


def tex(*parts, colors=(), font_size=44):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def panel(content, corner=UL, buff=0.5):
    content.to_corner(corner, buff=buff)
    return VGroup(plate_for(content), content).set_z_index(PANEL_Z)


def low_panel(content, bottom=-2.5):
    """A plate in the lower right, below the vectors and above the caption band."""
    content.to_edge(RIGHT, buff=0.55)
    content.shift((bottom - content.get_bottom()[1]) * UP)
    return VGroup(plate_for(content), content).set_z_index(PANEL_Z)


def name_label(tex_string, color, point, direction, font_size=40):
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.08).next_to(point, direction, buff=0.12)


def radial_label(plane, tex_string, color, coords, reach=0.5, font_size=40, turn=0.0):
    """A name placed just beyond the tip of an arrow from the origin, along its direction turned by `turn` degrees."""
    angle = math.atan2(coords[1], coords[0]) + math.radians(turn)
    direction = (math.cos(angle), math.sin(angle))
    point = plane.c2p(coords[0] + reach * direction[0], coords[1] + reach * direction[1])
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.06).move_to(point)


def shadow_color(value):
    if abs(value) < 0.02:
        return Palette.glow
    return Palette.teal if value > 0 else Palette.pink


def right_angle_mark(plane, first, second, size=0.32, color=Palette.glow):
    a, b = unit(first), unit(second)
    corners = [(size * a[0], size * a[1]), (size * (a[0] + b[0]), size * (a[1] + b[1])), (size * b[0], size * b[1])]
    return VMobject(color=color, stroke_width=4).set_points_as_corners([plane.c2p(*corner) for corner in corners])


def shadow_parts(plane, w):
    """The dashed drop from the tip of w to the line of v, and the signed shadow bar along that line."""
    direction = unit(V)
    length = dot(w, direction)
    foot = (length * direction[0], length * direction[1])
    parts = VGroup()
    if math.hypot(w[0] - foot[0], w[1] - foot[1]) > 0.08:
        parts.add(DashedLine(plane.c2p(*w), plane.c2p(*foot), color=Palette.text_muted, stroke_width=3, dash_length=0.12))
    if abs(length) > 0.03:
        parts.add(Line(plane.c2p(0, 0), plane.c2p(*foot), color=shadow_color(length), stroke_width=16, stroke_opacity=0.8))
    parts.add(Dot(plane.c2p(*foot), radius=0.07, color=shadow_color(length)))
    return parts


def angle_mark(plane, w, radius=0.6):
    """An orange arc for theta, or a right-angle mark when w is perpendicular to v."""
    theta = math.degrees(math.atan2(w[1], w[0]) - V_ANGLE) % 360
    if abs(theta - 90) < 0.6:
        return right_angle_mark(plane, V, w)
    if theta < 6:
        return VMobject()
    arc = Arc(radius=radius * PLANE_UNIT, start_angle=V_ANGLE, angle=math.radians(theta), arc_center=plane.c2p(0, 0), color=Palette.glow, stroke_width=4)
    middle = V_ANGLE + math.radians(theta) / 2
    label = MathTex(r"\theta", color=Palette.glow, font_size=34)
    label.move_to(plane.c2p((radius + 0.32) * math.cos(middle), (radius + 0.32) * math.sin(middle)))
    return VGroup(arc, label)


def number_readout(label_tex, value, color, anchor, decimals=2):
    label = MathTex(label_tex, color=Palette.text, font_size=44)
    number = DecimalNumber(value, num_decimal_places=decimals, color=color, font_size=44)
    label.move_to(anchor, aligned_edge=LEFT)
    number.next_to(label, RIGHT, buff=0.2)
    return VGroup(label, number).set_z_index(PANEL_Z + 1)


def fixed_plate(*templates, corner=UL, buff=0.5, padding=0.25):
    """A plate sized for the widest version of a live readout, and the left anchors of its lines."""
    stack = VGroup(*templates).arrange(DOWN, buff=0.3, aligned_edge=LEFT).to_corner(corner, buff=buff)
    anchors = [template.get_left() for template in stack]
    return plate_for(stack, padding=padding).set_z_index(PANEL_Z), anchors


class Lesson(LessonScene):
    day = 35
    title = "Dot products and orthogonality"

    def construct(self):
        self.plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        pulse = self.open_episode(self.plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.meet_the_dot()
        line = self.length(line)
        line = self.distance(line)
        line = self.shadow_sweep(line)
        line = self.equal_distances(line)
        line = self.pythagoras(line)
        line = self.complement(line)
        line = self.orthogonal_basis(line)
        self.close_episode(
            r"The dot product measures how much two vectors point the same way.\\"
            r"A dot product of zero means they are perpendicular.",
            *self.mobjects,
        )

    def meet_the_dot(self):
        plane = self.plane
        self.v_arrow = vector_arrow(V, Palette.yellow, plane)
        self.w_arrow = vector_arrow(W, Palette.blue, plane)
        self.v_name = name_label(r"\mathbf v", Palette.yellow, plane.c2p(*V), RIGHT)
        self.w_name = name_label(r"\mathbf w", Palette.blue, plane.c2p(*W), LEFT)
        line = self.say(r"Here are Day 1's vectors $\mathbf v$ and $\mathbf w$ again.", hold=0.2)
        self.play(GrowArrow(self.v_arrow), GrowArrow(self.w_arrow), FadeIn(self.v_name), FadeIn(self.w_name), run_time=1.3, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"So far we have only added and scaled vectors.", line, hold=Timing.beat)
        line = self.say(r"Closest answers on Day 38 need lengths and right angles.", line, hold=0.2)
        self.play(Indicate(self.v_arrow, color=Palette.glow, scale_factor=1.05), Indicate(self.w_arrow, color=Palette.glow, scale_factor=1.05), run_time=1.0)
        line = self.say(r"Today one number will measure both.", line, hold=Timing.beat)

        v_col, w_col = column(V, color=Palette.yellow), column(W, color=Palette.blue)
        terms = tex("=", "(3)(-1)", "+", "(2)(2)", "=", "1", colors=(None, None, None, None, None, Palette.glow))
        equation = VGroup(v_col, MathTex(r"\cdot", color=Palette.text, font_size=56), w_col, terms).arrange(RIGHT, buff=0.25)
        self.dot_panel = low_panel(equation)
        line = self.say(r"The dot product multiplies matching entries and adds them.", line, hold=0.2)
        self.play(FadeIn(self.dot_panel[0]), FadeIn(VGroup(v_col, equation[1], w_col, terms[0])), run_time=0.8)
        for row, term in ((0, terms[1]), (1, terms[3])):
            pair = VGroup(v_col.get_entries()[row], w_col.get_entries()[row])
            self.play(Indicate(pair, color=Palette.glow, scale_factor=1.15), run_time=0.8)
            self.play(FadeIn(term, shift=LEFT * 0.2), *([FadeIn(terms[2])] if row else []), run_time=0.5, rate_func=spring)
        self.play(FadeIn(terms[4]), FadeIn(terms[5], scale=1.3), run_time=0.6, rate_func=spring)
        line = self.say(r"The result $\mathbf v\cdot\mathbf w = 1$ is a number, not a vector.", line, hold=Timing.read_short)
        return line

    def length(self, line):
        plane = self.plane
        run = DashedLine(plane.c2p(0, 0), plane.c2p(V[0], 0), color=Palette.i_hat, stroke_width=4)
        rise = DashedLine(plane.c2p(V[0], 0), plane.c2p(*V), color=Palette.j_hat, stroke_width=4)
        run_label = backed(MathTex("3", color=Palette.i_hat, font_size=38), padding=0.08).next_to(run, DOWN, buff=0.12)
        rise_label = backed(MathTex("2", color=Palette.j_hat, font_size=38), padding=0.08).next_to(rise, RIGHT, buff=0.12)
        squares = tex(r"\mathbf v\cdot\mathbf v", "=", "3^2", "+", "2^2", "=", "13", colors=(Palette.yellow, None, Palette.i_hat, None, Palette.j_hat))
        norm = tex(r"\|\mathbf v\|", "=", r"\sqrt{\mathbf v\cdot\mathbf v}", "=", r"\sqrt{13}", colors=(Palette.yellow,))
        stack = VGroup(squares, norm).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        length_panel = low_panel(stack)

        line = self.say(r"Dot $\mathbf v$ with itself and you get $3^2 + 2^2 = 13$.", line, hold=0.2)
        self.play(FadeOut(self.dot_panel), run_time=0.4)
        self.play(Create(run), FadeIn(run_label), run_time=0.9)
        self.play(Create(rise), FadeIn(rise_label), run_time=0.9)
        self.play(FadeIn(length_panel[0]), Write(squares), run_time=1.0)
        line = self.say(r"By Pythagoras that is the squared length, so $\|\mathbf v\| = \sqrt{13}$.", line, hold=0.2)
        self.play(length_panel[0].animate.become(plate_for(stack)), FadeIn(norm, shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        self.play(Indicate(self.v_arrow, color=Palette.glow, scale_factor=1.05), run_time=0.9)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(run, rise, run_label, rise_label, length_panel)), run_time=0.6)
        return line

    def distance(self, line):
        plane = self.plane
        gap = arrow_between(plane, W, V, Palette.teal)
        moved = vector_arrow((V[0] - W[0], V[1] - W[1]), Palette.teal, plane)
        moved_name = name_label(r"\mathbf v - \mathbf w", Palette.teal, moved.get_center(), DOWN, font_size=38)
        formula = tex(
            r"\operatorname{dist}(\mathbf v, \mathbf w)", "=", r"\|\mathbf v - \mathbf w\|", "=", r"\left\|\begin{bmatrix} 4 \\ 0 \end{bmatrix}\right\|", "=", "4",
            colors=(None, None, Palette.teal, None, Palette.teal, None, Palette.glow),
        )
        distance_panel = low_panel(formula)
        line = self.say(r"The distance between the tips is the length of $\mathbf v - \mathbf w$.", line, hold=0.2)
        self.play(GrowArrow(gap), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Moved to the origin, $\mathbf v - \mathbf w = (4, 0)$, so the distance is 4.", line, hold=0.2)
        self.play(TransformFromCopy(gap, moved), run_time=1.4, rate_func=spring)
        self.play(FadeIn(moved_name), FadeIn(distance_panel, shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(gap, moved, moved_name, distance_panel)), run_time=0.6)
        return line

    def live_w(self):
        plane, theta = self.plane, self.theta
        w_arrow = always_redraw(lambda: vector_arrow(spun(theta.get_value()), Palette.blue, plane))
        w_name = always_redraw(lambda: radial_label(plane, r"\mathbf w", Palette.blue, spun(theta.get_value()), reach=0.45, turn=45))
        return w_arrow, w_name

    def shadow_sweep(self, line):
        plane = self.plane
        self.theta = theta = ValueTracker(THETA_START)
        w_arrow, w_name = self.live_w()
        self.remove(self.w_arrow, self.w_name)
        self.add(w_arrow, w_name)
        self.live_w_parts = VGroup(w_arrow, w_name)
        self.v_line = line_through_origin(plane, V, Palette.yellow, 2.5, opacity=0.45)
        shadow = always_redraw(lambda: shadow_parts(plane, spun(theta.get_value())))
        arc = always_redraw(lambda: angle_mark(plane, spun(theta.get_value())))
        rule = tex(r"\mathbf v\cdot\mathbf w", "=", r"\|\mathbf v\|\,\|\mathbf w\|\cos\theta", colors=(None, None, None))
        plate, anchors = fixed_plate(number_readout(r"\mathbf v\cdot\mathbf w =", -8.06, Palette.pink, ORIGIN))
        rule.next_to(plate, DOWN, buff=0.4, aligned_edge=LEFT).shift(RIGHT * 0.25)
        rule_panel = VGroup(plate_for(rule), rule).set_z_index(PANEL_Z)
        readout = always_redraw(lambda: self.dot_readout(anchors[0]))

        line = self.say(r"Spin $\mathbf w$ and watch the shadow it casts on the line of $\mathbf v$.", line, hold=0.2)
        self.play(Create(self.v_line), run_time=0.9)
        self.bring_to_front(self.v_arrow, self.v_name)
        self.add(shadow)
        self.bring_to_front(w_arrow, w_name, self.v_arrow)
        self.play(FadeIn(plate), FadeIn(readout), FadeIn(arc), run_time=0.7)
        self.wait(Timing.beat)
        stops = [
            (0, r"Lined up with $\mathbf v$, the shadow and $\mathbf v\cdot\mathbf w$ are largest.", spring_soft),
            (60, r"Turn away and the shadow shrinks, and so does $\mathbf v\cdot\mathbf w$.", spring_soft),
            (90, r"At a right angle the shadow vanishes and $\mathbf v\cdot\mathbf w = 0$.", spring_soft),
            (180, r"Past $90^\circ$ the shadow points backward, so $\mathbf v\cdot\mathbf w < 0$.", smooth),
        ]
        for target, text, rate in stops:
            line = self.say(text, line, hold=0.1)
            self.play(theta.animate.set_value(target), run_time=2.4, rate_func=rate)
            if target == 90:
                self.play(Flash(plane.c2p(0, 0), color=Palette.glow, line_length=0.2, flash_radius=0.35), run_time=0.7)
            self.wait(Timing.read_short)
        line = self.say(r"In every position, $\mathbf v\cdot\mathbf w = \|\mathbf v\|\,\|\mathbf w\|\cos\theta$.", line, hold=0.2)
        self.play(FadeIn(rule_panel, shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        line = self.say(r"Vectors with $\mathbf v\cdot\mathbf w = 0$ are called \emph{orthogonal}.", line, hold=0.1)
        self.play(theta.animate.set_value(90), run_time=2.2, rate_func=spring_soft)
        self.wait(Timing.read_short)
        for part in (shadow, arc, readout):
            part.clear_updaters()
        self.play(FadeOut(VGroup(shadow, arc, readout, rule_panel, plate)), run_time=0.6)
        return line

    def dot_readout(self, anchor):
        value = dot(V, spun(self.theta.get_value()))
        value = 0.0 if abs(value) < 0.005 else value
        return number_readout(r"\mathbf v\cdot\mathbf w =", value, shadow_color(value), anchor)

    def equal_distances(self, line):
        plane, theta = self.plane, self.theta
        minus_w = always_redraw(lambda: vector_arrow(spun(theta.get_value() + 180), Palette.purple_gray, plane))
        minus_name = always_redraw(lambda: radial_label(plane, r"-\mathbf w", Palette.purple_gray, spun(theta.get_value() + 180), reach=0.5, turn=-120))
        to_w = always_redraw(lambda: DashedLine(plane.c2p(*V), plane.c2p(*spun(theta.get_value())), color=Palette.blue, stroke_width=4))
        to_minus = always_redraw(lambda: DashedLine(plane.c2p(*V), plane.c2p(*spun(theta.get_value() + 180)), color=Palette.purple_gray, stroke_width=4))
        plate, anchors = fixed_plate(
            number_readout(r"\|\mathbf v - \mathbf w\| =", 4.24, Palette.blue, ORIGIN),
            number_readout(r"\|\mathbf v + \mathbf w\| =", 4.24, Palette.blue, ORIGIN),
        )
        readouts = always_redraw(lambda: self.distance_readouts(anchors))

        line = self.say(r"Compare how far the tip of $\mathbf v$ is from $\mathbf w$ and $-\mathbf w$.", line, hold=0.2)
        self.play(GrowArrow(minus_w), FadeIn(minus_name), run_time=1.0, rate_func=spring_soft)
        self.play(Create(to_w), Create(to_minus), FadeIn(plate), FadeIn(readouts), run_time=1.0)
        self.bring_to_front(self.v_arrow, self.v_name)
        self.play(theta.animate.set_value(140), run_time=2.2, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"The two distances agree only when $\mathbf w$ is at a right angle.", line, hold=0.1)
        self.play(theta.animate.set_value(90), run_time=2.2, rate_func=spring_soft)
        mark = right_angle_mark(plane, V, spun(90))
        self.play(Create(mark), run_time=0.5)
        self.wait(Timing.read_short)
        for part in (minus_w, minus_name, to_w, to_minus, readouts):
            part.clear_updaters()
        self.equal_parts = VGroup(minus_w, minus_name, to_w, to_minus, readouts, plate, mark)
        return line

    def distance_readouts(self, anchors):
        w = spun(self.theta.get_value())
        gaps = (math.hypot(V[0] - w[0], V[1] - w[1]), math.hypot(V[0] + w[0], V[1] + w[1]))
        return VGroup(
            number_readout(r"\|\mathbf v - \mathbf w\| =", gaps[0], Palette.blue, anchors[0]),
            number_readout(r"\|\mathbf v + \mathbf w\| =", gaps[1], Palette.purple_gray, anchors[1]),
        )

    def pythagoras(self, line):
        veil = scrim().set_z_index(20)
        minus = tex(r"\|\mathbf v - \mathbf w\|^2", "=", r"\|\mathbf v\|^2 + \|\mathbf w\|^2", "-", r"2\,\mathbf v\cdot\mathbf w", colors=(Palette.blue, None, None, Palette.glow, Palette.glow), font_size=52)
        plus = tex(r"\|\mathbf v + \mathbf w\|^2", "=", r"\|\mathbf v\|^2 + \|\mathbf w\|^2", "+", r"2\,\mathbf v\cdot\mathbf w", colors=(Palette.purple_gray, None, None, Palette.glow, Palette.glow), font_size=52)
        pythagoras = tex(r"\|\mathbf v + \mathbf w\|^2", "=", r"\|\mathbf v\|^2", "+", r"\|\mathbf w\|^2", font_size=64)
        numbers = tex("18", "=", "13", "+", "5", colors=(Palette.teal, None, Palette.yellow, None, Palette.blue), font_size=52)
        rows = VGroup(minus, plus).arrange(DOWN, buff=0.45)
        for row in (plus,):
            row.shift((minus[1].get_x() - row[1].get_x()) * RIGHT)
        board = VGroup(rows, pythagoras, numbers).arrange(DOWN, buff=0.7).move_to(UP * 0.5).set_z_index(21)

        line = self.say(r"Expand both with dot products to see why.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(FadeIn(minus, shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        self.play(FadeIn(plus, shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        line = self.say(r"They are equal exactly when $\mathbf v\cdot\mathbf w = 0$.", line, hold=0.2)
        self.play(Indicate(VGroup(minus[3:], plus[3:]), color=Palette.glow, scale_factor=1.15), run_time=1.0)
        self.wait(Timing.beat)
        line = self.say(r"Then the middle terms drop out and Pythagoras appears.", line, hold=0.2)
        self.play(FadeIn(pythagoras, shift=UP * 0.1), run_time=0.9, rate_func=spring_soft)
        self.play(FadeIn(numbers, shift=UP * 0.1), run_time=0.7, rate_func=spring_soft)
        self.wait(Timing.read_short)
        self.remove(*self.live_w_parts, *self.equal_parts)
        self.play(FadeOut(board), FadeOut(veil), run_time=0.8)
        return line

    def complement(self, line):
        plane = self.plane
        perp_line = line_through_origin(plane, U, Palette.blue, 4)
        self.u_arrow = vector_arrow(U, Palette.blue, plane)
        self.u_name = name_label(r"\mathbf u", Palette.blue, plane.c2p(*U), RIGHT)
        mark = right_angle_mark(plane, V, U)
        w_label = name_label(r"W", Palette.yellow, plane.c2p(4.4, 4.4 * V[1] / V[0]), DR)
        perp_label = name_label(r"W^\perp", Palette.blue, plane.c2p(-1.3, 1.95), LEFT)
        row_matrix = Matrix([["3", "2"]], h_buff=0.9, bracket_h_buff=0.14).set_color(Palette.yellow)
        stack = VGroup(
            VGroup(MathTex("A =", color=Palette.text, font_size=44), row_matrix).arrange(RIGHT, buff=0.2),
            tex(r"A\mathbf x", "=", r"\mathbf v\cdot\mathbf x"),
            tex(r"\operatorname{Nul}A", "=", r"(\operatorname{Row}A)^\perp", colors=(Palette.blue, None, Palette.blue)),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        stack.to_edge(LEFT, buff=0.6).shift(UP * 0.6)
        row_panel = VGroup(plate_for(stack), stack).set_z_index(PANEL_Z)

        line = self.say(r"Let $W$ be the line through $\mathbf v$.", line, hold=0.2)
        self.play(self.v_line.animate.set_stroke(width=4, opacity=0.9), FadeIn(w_label), run_time=0.8)
        line = self.say(r"The vectors orthogonal to all of $W$ fill another line, $W^\perp$.", line, hold=0.2)
        self.play(Create(perp_line), run_time=1.2)
        self.play(GrowArrow(self.u_arrow), FadeIn(self.u_name), FadeIn(perp_label), Create(mark), run_time=1.0, rate_func=spring_soft)
        self.bring_to_front(self.v_arrow, self.v_name)
        self.wait(Timing.beat)

        line = self.say(r"Put $\mathbf v$ in the row of a matrix $A$.", line, hold=0.2)
        self.play(FadeIn(row_panel[0]), FadeIn(stack[0]), run_time=0.7)
        self.play(FadeIn(stack[1], shift=UP * 0.1), run_time=0.7, rate_func=spring_soft)
        line = self.say(r"Solving $A\mathbf x = \mathbf 0$ finds every $\mathbf x$ orthogonal to that row.", line, hold=0.2)
        self.play(Indicate(perp_line, color=Palette.glow, scale_factor=1.0), run_time=1.0)
        line = self.say(r"So the null space of $A$ is $W^\perp$, the complement of its row space.", line, hold=0.2)
        self.play(FadeIn(stack[2], shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"Day 36 splits vectors into pieces in $W$ and $W^\perp$.", line, hold=0.2)
        self.play(Indicate(self.v_line, color=Palette.glow, scale_factor=1.0), Indicate(perp_line, color=Palette.glow, scale_factor=1.0), run_time=1.0)
        self.wait(Timing.beat)
        self.basis_mark = mark
        self.play(FadeOut(VGroup(perp_line, self.v_line, w_label, perp_label, row_panel)), run_time=0.7)
        return line

    def orthogonal_basis(self, line):
        plane = self.plane
        y_arrow = vector_arrow(Y, Palette.teal, plane)
        y_name = name_label(r"\mathbf y", Palette.teal, plane.c2p(*Y), RIGHT)
        back_step = arrow_between(plane, V, Y, Palette.blue)
        back_name = name_label(r"-\mathbf u", Palette.blue, back_step.get_center(), UR, font_size=38)
        weights = VGroup(
            tex("c_1", "=", r"\dfrac{\mathbf y\cdot\mathbf v}{\mathbf v\cdot\mathbf v}", "=", r"\dfrac{13}{13}", "=", "1", colors=(Palette.yellow,)),
            tex("c_2", "=", r"\dfrac{\mathbf y\cdot\mathbf u}{\mathbf u\cdot\mathbf u}", "=", r"\dfrac{-13}{13}", "=", "-1", colors=(Palette.blue,)),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        weights.to_edge(LEFT, buff=0.6).shift(UP * 0.4)
        weight_panel = VGroup(plate_for(weights), weights).set_z_index(PANEL_Z)

        line = self.say(r"Since $\mathbf v\cdot\mathbf u = 0$, the set $\{\mathbf v, \mathbf u\}$ is an \emph{orthogonal} basis.", line, hold=0.2)
        self.wait(Timing.beat)
        line = self.say(r"We want coordinates in this basis without row reduction.", line, hold=Timing.beat)
        line = self.say(r"To write $\mathbf y$ in it, each weight is one ratio of dot products.", line, hold=0.2)
        self.play(GrowArrow(y_arrow), FadeIn(y_name), run_time=1.0, rate_func=spring_soft)
        self.play(FadeIn(weight_panel[0]), FadeIn(weights[0], shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        self.play(FadeIn(weights[1], shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"So $\mathbf y = \mathbf v - \mathbf u$, and no row reduction was needed.", line, hold=0.2)
        self.play(TransformFromCopy(self.u_arrow, back_step), run_time=1.3, rate_func=spring)
        self.play(FadeIn(back_name), Indicate(y_arrow, color=Palette.glow, scale_factor=1.05), run_time=0.9)
        self.wait(Timing.beat)
        line = self.say(r"Day 36 projects onto subspaces with these same ratios.", line, hold=0.2)
        self.play(Indicate(weight_panel, color=Palette.glow, scale_factor=1.03), run_time=0.9)
        self.wait(Timing.beat)
        self.play(FadeOut(VGroup(y_arrow, y_name, back_step, back_name, weight_panel)), run_time=0.6)
        return self.normalize(line)

    def normalize(self, line):
        plane = self.plane
        shrink = 1 / math.sqrt(13)
        v_short, u_short = (V[0] * shrink, V[1] * shrink), (U[0] * shrink, U[1] * shrink)
        circle = always_redraw(lambda: unit_circle(plane))
        line = self.say(r"Divide each by its length $\sqrt{13}$ and the set is \emph{orthonormal}.", line, hold=0.2)
        self.play(Create(circle), FadeOut(self.basis_mark), FadeOut(self.v_name), FadeOut(self.u_name), run_time=0.8)
        self.play(
            Transform(self.v_arrow, vector_arrow(v_short, Palette.yellow, plane, stroke_width=5)),
            Transform(self.u_arrow, vector_arrow(u_short, Palette.blue, plane, stroke_width=5)),
            run_time=1.6, rate_func=spring_soft,
        )
        live = VGroup(
            always_redraw(lambda: vector_arrow(v_short, Palette.yellow, plane)),
            always_redraw(lambda: vector_arrow(u_short, Palette.blue, plane)),
            always_redraw(lambda: right_angle_mark(plane, V, U, size=0.25)),
        )
        self.remove(self.v_arrow, self.u_arrow)
        self.add(live)
        self.play(plane.animate.scale(2.3, about_point=plane.c2p(0, 0)).shift(UP * -PLANE_ORIGIN[1]), run_time=1.6, rate_func=spring_soft)
        labels = VGroup(
            name_label(r"\mathbf v/\sqrt{13}", Palette.yellow, plane.c2p(*v_short), RIGHT),
            name_label(r"\mathbf u/\sqrt{13}", Palette.blue, plane.c2p(*u_short), LEFT),
        )
        self.play(FadeIn(labels, shift=UP * 0.1), run_time=0.7, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return line


def unit_circle(plane):
    radius = plane.c2p(1, 0)[0] - plane.c2p(0, 0)[0]
    return DashedVMobject(Circle(radius=radius, color=Palette.text_muted, stroke_width=3).move_to(plane.c2p(0, 0)), num_dashes=48)


def shadow_still(plane, theta, show_value=True, box=None):
    """v, its faint line, w at angle theta, the shadow, the angle mark and the dot product, for figures."""
    w = spun(theta)
    value = dot(V, w)
    value = 0.0 if abs(value) < 0.005 else value
    v_line = clipped_line(plane, V, box, Palette.yellow).set_stroke(width=2.5, opacity=0.45) if box else line_through_origin(plane, V, Palette.yellow, 2.5, opacity=0.45)
    parts = VGroup(
        v_line,
        shadow_parts(plane, w),
        vector_arrow(V, Palette.yellow, plane),
        vector_arrow(w, Palette.blue, plane),
        angle_mark(plane, w),
        radial_label(plane, r"\mathbf w", Palette.blue, w),
        radial_label(plane, r"\mathbf v", Palette.yellow, V, reach=0.45),
    )
    if show_value:
        readout = MathTex(r"\mathbf v\cdot\mathbf w =", f"{value:.2f}", color=Palette.text, font_size=44)
        readout[1].set_color(shadow_color(value))
        bottom = box[1][0] if box else -2.7
        parts.add(backed(readout, padding=0.14).next_to(plane.c2p(0.5, bottom), DOWN, buff=0.3))
    return parts


class FigShadow(Scene):
    def construct(self):
        stills = VGroup()
        for theta in (40, 90, 140):
            plane = plane_at((0, 0), 1.0)
            box = ((-3, 4), (-3, 3))
            stills.add(VGroup(local_grid(plane, *box), shadow_still(plane, theta, box=box)))
        stills.arrange(RIGHT, buff=0.7)
        self.add(stills)
        fit_to_frame(self)


class FigEqualDistances(Scene):
    def construct(self):
        plane = plane_at((0, 0), 1.0)
        w = spun(90)
        minus = (-w[0], -w[1])
        parts = VGroup(
            DashedLine(plane.c2p(*V), plane.c2p(*w), color=Palette.blue, stroke_width=4),
            DashedLine(plane.c2p(*V), plane.c2p(*minus), color=Palette.purple_gray, stroke_width=4),
            vector_arrow(w, Palette.blue, plane),
            vector_arrow(minus, Palette.purple_gray, plane),
            vector_arrow(V, Palette.yellow, plane),
            right_angle_mark(plane, V, w),
            radial_label(plane, r"\mathbf w", Palette.blue, w),
            radial_label(plane, r"-\mathbf w", Palette.purple_gray, minus),
            radial_label(plane, r"\mathbf v", Palette.yellow, V, reach=0.45),
            name_label(r"\|\mathbf v - \mathbf w\|", Palette.blue, plane.c2p(1.0, 2.35), UP, font_size=38),
            name_label(r"\|\mathbf v + \mathbf w\|", Palette.purple_gray, plane.c2p(2.4, -0.2), RIGHT, font_size=38),
        )
        window = local_grid(plane, (-3, 5), (-3, 4))
        self.add(window, parts)
        fit_to_frame(self)


def local_grid(plane, x_range, y_range):
    """A cropped piece of the grid for figures, with its axes."""
    grid = VGroup()
    for x in range(x_range[0], x_range[1] + 1):
        grid.add(Line(plane.c2p(x, y_range[0]), plane.c2p(x, y_range[1]), color=Palette.axis if x == 0 else Palette.grid, stroke_width=2 if x == 0 else 1.4, stroke_opacity=0.9 if x == 0 else 0.5))
    for y in range(y_range[0], y_range[1] + 1):
        grid.add(Line(plane.c2p(x_range[0], y), plane.c2p(x_range[1], y), color=Palette.axis if y == 0 else Palette.grid, stroke_width=2 if y == 0 else 1.4, stroke_opacity=0.9 if y == 0 else 0.5))
    return grid


class FigComplement(Scene):
    def construct(self):
        plane = plane_at((0, 0), 1.0)
        box = ((-4, 5), (-4, 4))
        parts = VGroup(
            clipped_line(plane, V, box, Palette.yellow),
            clipped_line(plane, U, box, Palette.blue),
            vector_arrow(V, Palette.yellow, plane),
            vector_arrow(U, Palette.blue, plane),
            right_angle_mark(plane, V, U),
            name_label(r"\mathbf v", Palette.yellow, plane.c2p(*V), DR),
            name_label(r"\mathbf u", Palette.blue, plane.c2p(*U), RIGHT),
            name_label(r"W", Palette.yellow, plane.c2p(5, 10 / 3), DOWN),
            name_label(r"W^\perp", Palette.blue, plane.c2p(-8 / 3, 4), LEFT),
        )
        row_matrix = Matrix([["3", "2"]], h_buff=0.9, bracket_h_buff=0.14).set_color(Palette.yellow)
        stack = VGroup(
            VGroup(MathTex("A =", color=Palette.text, font_size=44), row_matrix).arrange(RIGHT, buff=0.2),
            tex(r"\operatorname{Nul}A", "=", r"(\operatorname{Row}A)^\perp", colors=(Palette.blue, None, Palette.blue)),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        stack.next_to(plane.c2p(5.4, -3.6), RIGHT, buff=0.2, aligned_edge=DOWN)
        self.add(local_grid(plane, *box), parts, plate_for(stack), stack)
        fit_to_frame(self)


def clipped_line(plane, direction, box, color):
    reach = min(box[0][1] / abs(direction[0]) if direction[0] else 99, box[1][1] / abs(direction[1]) if direction[1] else 99)
    reach = min(reach, abs(box[0][0]) / abs(direction[0]) if direction[0] else 99, abs(box[1][0]) / abs(direction[1]) if direction[1] else 99)
    return Line(plane.c2p(-reach * direction[0], -reach * direction[1]), plane.c2p(reach * direction[0], reach * direction[1]), color=color, stroke_width=4, stroke_opacity=0.8)


class FigOrthogonalWeights(Scene):
    def construct(self):
        plane = plane_at((0, 0), 1.0)
        parts = VGroup(
            vector_arrow(V, Palette.yellow, plane),
            vector_arrow(U, Palette.blue, plane),
            arrow_between(plane, V, Y, Palette.blue),
            vector_arrow(Y, Palette.teal, plane),
            right_angle_mark(plane, V, U),
            name_label(r"\mathbf v", Palette.yellow, plane.c2p(1.5, 1), UL),
            name_label(r"\mathbf u", Palette.blue, plane.c2p(*U), RIGHT),
            name_label(r"-\mathbf u", Palette.blue, plane.c2p(4, 0.5), RIGHT),
            name_label(r"\mathbf y = \mathbf v - \mathbf u", Palette.teal, plane.c2p(*Y), DOWN),
        )
        weights = VGroup(
            tex("c_1", "=", r"\dfrac{\mathbf y\cdot\mathbf v}{\mathbf v\cdot\mathbf v}", "=", r"\dfrac{13}{13}", "=", "1", colors=(Palette.yellow,)),
            tex("c_2", "=", r"\dfrac{\mathbf y\cdot\mathbf u}{\mathbf u\cdot\mathbf u}", "=", r"\dfrac{-13}{13}", "=", "-1", colors=(Palette.blue,)),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        weights.next_to(plane.c2p(-3.4, 1), LEFT, buff=0.4)
        self.add(local_grid(plane, (-3, 6), (-2, 4)), parts, plate_for(weights), weights)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        theta = 128
        w = spun(theta)
        ghosts = VGroup(*[vector_arrow(spun(angle), Palette.blue, plane, stroke_width=4).set_opacity(0.18) for angle in (20, 55, 90)])
        rule = tex(r"\mathbf v\cdot\mathbf w", "=", r"\|\mathbf v\|\,\|\mathbf w\|\cos\theta", font_size=60)
        rule.to_corner(UL, buff=0.6)
        value = tex(r"\mathbf v\cdot\mathbf w", "=", f"{dot(V, w):.2f}", colors=(None, None, Palette.pink), font_size=60)
        value.next_to(rule, DOWN, buff=0.35, aligned_edge=LEFT)
        text = VGroup(rule, value)
        self.add(plane, ghosts, shadow_still(plane, theta, show_value=False), plate_for(text), text)
