import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    Palette,
    Timing,
    backed,
    clipped_plot,
    fit_to_frame,
    make_plane,
    plane_at,
    scrim,
    spring,
    spring_soft,
)

RECALL_ORIGIN = (0.8, 0.1)
RECALL_UNIT = 0.85
NULL_REACH = 2.6
NULL_STOPS = (-2.5, -2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0, 2.5)

D_T = (-2.0, 2.0)
D_Y = (-3.0, 3.0)
D_WIDTH, D_HEIGHT = 5.8, 4.6
D_LEFT, D_RIGHT = (-3.7, 0.35), (3.7, 0.35)
CONSTANTS = (2, 1, -1, -2)

EVAL_CENTER = (-3.0, 0.35)
EVAL_WIDTH, EVAL_HEIGHT = 7.2, 5.0
EVAL_T = (-1.3, 1.8)
EVAL_Y = (-1.6, 3.4)
CODOMAIN_CENTER = (4.6, 0.35)
CODOMAIN_SIZE = 3.9
TOP_ROW_Y = 3.45
PINS = ((0.0, Palette.i_hat, "t = 0"), (1.0, Palette.j_hat, "t = 1"))
THIRD_PIN = (-1.0, Palette.purple_gray, "t = -1")
B_POINT = (0.0, 1.0)
KERNEL_STOPS = (2.0, -1.0, 0.5)
FAMILY_STOPS = (1.0, -1.0, -0.5)


def u_curve(t):
    return t * t


def v_curve(t):
    return t


def kernel_curve(t):
    return t * t - t


def family(c):
    return lambda t: u_curve(t) + c * kernel_curve(t)


def multiple(c):
    return lambda t: c * kernel_curve(t)


def graph_panel(center, t_range, y_range, width, height):
    """Unnumbered axes over a faint plate, centered at `center`."""
    axes = Axes(
        x_range=(*t_range, 1),
        y_range=(*y_range, 1),
        x_length=width,
        y_length=height,
        tips=False,
        axis_config={"color": Palette.axis, "stroke_width": 2, "include_ticks": False},
    )
    axes.shift(np.array([center[0], center[1], 0]) - axes.get_center())
    plate = Rectangle(width=width, height=height, fill_color=Palette.grid_faint, fill_opacity=0.35, stroke_width=0).move_to(axes)
    return VGroup(plate, axes)


def eval_panel():
    return graph_panel(EVAL_CENTER, EVAL_T, EVAL_Y, EVAL_WIDTH, EVAL_HEIGHT)


def draw(panel, function, color, stroke_width=5, opacity=1.0):
    curve = clipped_plot(panel[1], function, EVAL_T, EVAL_Y, color, stroke_width=stroke_width)
    return curve.set_stroke(opacity=opacity)


def pin_line(panel, pin):
    t, color, label_tex = pin
    axes = panel[1]
    line = DashedLine(axes.c2p(t, EVAL_Y[0]), axes.c2p(t, EVAL_Y[1]), color=color, stroke_width=3, dash_length=0.12)
    label = backed(MathTex(label_tex, color=color, font_size=30), padding=0.06)
    label.next_to(axes.c2p(t, EVAL_Y[1]), DR, buff=0.12)
    return VGroup(line, label)


def pin_dots(panel, function, pins=PINS):
    axes = panel[1]
    return VGroup(*[Dot(axes.c2p(t, function(t)), radius=0.085, color=color).set_z_index(4) for t, color, _ in pins])


def codomain_plane():
    plane = make_plane(x_range=(-1, 2, 1), y_range=(-1, 2, 1), x_length=CODOMAIN_SIZE, y_length=CODOMAIN_SIZE)
    plane.shift(np.array([*CODOMAIN_CENTER, 0]) - plane.c2p(0.5, 0.5))
    name = backed(MathTex(r"\mathbb R^2", color=Palette.text_muted, font_size=34), padding=0.06)
    name.move_to(plane.c2p(1.7, -0.75))
    return plane, name


def domain_name(panel):
    name = backed(MathTex(r"\mathbb P_2", color=Palette.text_muted, font_size=34), padding=0.06)
    return name.move_to(panel[1].c2p(1.55, -1.25))


def map_arrow(start_x, end_x, y, tex):
    arrow = Arrow(np.array([start_x, y, 0]), np.array([end_x, y, 0]), buff=0, color=Palette.text_muted, stroke_width=5, max_tip_length_to_length_ratio=0.25)
    label = MathTex(tex, color=Palette.text, font_size=38).next_to(arrow, UP, buff=0.12)
    return VGroup(arrow, label)


def eval_header():
    header = MathTex(r"T(\mathbf p) = (", r"\mathbf p(0)", r",\ ", r"\mathbf p(1)", ")", color=Palette.text, font_size=38)
    header[1].set_color(Palette.i_hat)
    header[3].set_color(Palette.j_hat)
    return header.move_to(np.array([CODOMAIN_CENTER[0], TOP_ROW_Y, 0]))


def three_pin_header():
    header = MathTex(r"T(\mathbf p) = (", r"\mathbf p(-1)", r",\ ", r"\mathbf p(0)", r",\ ", r"\mathbf p(1)", ")", color=Palette.text, font_size=38)
    for index, color in ((1, Palette.purple_gray), (3, Palette.i_hat), (5, Palette.j_hat)):
        header[index].set_color(color)
    return header.move_to(np.array([CODOMAIN_CENTER[0], TOP_ROW_Y, 0]))


def legend_items():
    return VGroup(
        MathTex(r"\mathbf u = t^2", color=Palette.yellow, font_size=36),
        MathTex(r"\mathbf v = t", color=Palette.blue, font_size=36),
        MathTex(r"\mathbf u - \mathbf v = t^2 - t", color=Palette.pink, font_size=36),
    )


def place_legend(items, panel):
    items.arrange(RIGHT, buff=0.6)
    items.move_to(np.array([0, TOP_ROW_Y, 0]))
    items.align_to(panel[0], LEFT)
    return items


def readout_at(tex, color=Palette.text, font_size=36):
    text = MathTex(tex, color=color, font_size=font_size)
    return text.move_to(np.array([CODOMAIN_CENTER[0], CODOMAIN_CENTER[1] - CODOMAIN_SIZE / 2 - 0.42, 0]))


def one_place(value):
    return f"{round(value, 1) + 0.0:.1f}"


def glow_ring(point, radius=0.22):
    return Circle(radius=radius, color=Palette.glow, stroke_width=4).move_to(point)


def output_arrow(plane, point, color=Palette.teal):
    return Arrow(plane.c2p(0, 0), plane.c2p(*point), buff=0, color=color, stroke_width=6, max_tip_length_to_length_ratio=0.25)


def d_panels():
    left = graph_panel(D_LEFT, D_T, D_Y, D_WIDTH, D_HEIGHT)
    right = graph_panel(D_RIGHT, D_T, D_Y, D_WIDTH, D_HEIGHT)
    arrow = map_arrow(-0.6, 0.6, D_LEFT[1], "D")
    return left, right, arrow


def flat_line(panel, height, color, stroke_width=5):
    axes = panel[1]
    return Line(axes.c2p(D_T[0], height), axes.c2p(D_T[1], height), color=color, stroke_width=stroke_width)


def corner_tag(panel, tex, color):
    tag = backed(MathTex(tex, color=color, font_size=34), padding=0.08)
    return tag.move_to(panel[0].get_corner(UL) + np.array([0.2, -0.2, 0]), aligned_edge=UL).set_z_index(3)


def subspace_rows():
    rows = VGroup(
        MathTex(r"T(\mathbf 0)", "=", r"\mathbf 0"),
        MathTex(r"T(\mathbf u + \mathbf v)", "=", r"T(\mathbf u) + T(\mathbf v)", "=", r"\mathbf 0 + \mathbf 0", "=", r"\mathbf 0"),
        MathTex(r"T(c\,\mathbf u)", "=", r"c\,T(\mathbf u)", "=", r"c\,\mathbf 0", "=", r"\mathbf 0"),
    )
    for row in rows:
        row.set_color(Palette.text).scale(1.15)
    rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
    return rows


class Lesson(LessonScene):
    day = 23
    title = "Kernel"

    def construct(self):
        plane = plane_at(RECALL_ORIGIN, RECALL_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.recall_null_space(plane)
        line = self.define_kernel(line)
        line = self.derivative_kernel(line)
        line = self.subspace_proof(line)
        line = self.evaluation_map(line)
        line = self.centerpiece(line)
        line = self.kernel_line(line)
        line = self.pinned_family(line)
        line = self.theorem(line)
        self.third_pin(line)
        self.close_episode(
            r"The kernel is everything $T$ sends to $\mathbf 0$.\\"
            r"$T$ is one-to-one exactly when the kernel is only $\mathbf 0$.",
            *self.mobjects,
        )

    def recall_null_space(self, plane):
        s = ValueTracker(0.0)
        at = lambda k: plane.c2p(k * (1 - s.get_value()), -k * (1 - s.get_value()))  # noqa: E731
        null_line = always_redraw(lambda: Line(at(-NULL_REACH), at(NULL_REACH), color=Palette.pink, stroke_width=5))
        dots = VGroup(*[always_redraw(lambda k=k: Dot(at(k), radius=0.08, color=Palette.pink)) for k in NULL_STOPS])
        formula = backed(MathTex(r"P = \tfrac12\begin{bmatrix} 1 & 1 \\ 1 & 1 \end{bmatrix}", color=Palette.text, font_size=40), padding=0.25)
        formula.to_corner(UL, buff=0.5)
        line = self.say(r"On Day 17, this $P$ sent a whole pink line to $\mathbf 0$.", hold=0.2)
        self.play(FadeIn(formula, shift=DOWN * 0.1), Create(null_line), run_time=1.2)
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in dots], lag_ratio=0.08), run_time=1.0)
        self.play(s.animate.set_value(1.0), run_time=2.0, rate_func=spring_soft)
        self.play(Flash(plane.c2p(0, 0), color=Palette.glow, flash_radius=0.4), run_time=0.8)
        name = backed(MathTex(r"\operatorname{Nul}P = \operatorname{Span}\{(1, -1)\}", color=Palette.pink, font_size=38), padding=0.2)
        name.next_to(formula, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(s.animate.set_value(0.0), run_time=1.4, rate_func=spring_soft)
        line = self.say(r"That line was $\operatorname{Nul}P$, the null space of $P$.", line, hold=0.2)
        self.play(FadeIn(name, shift=DOWN * 0.1), run_time=0.7)
        self.wait(Timing.read_short)
        return line

    def define_kernel(self, line):
        veil = scrim()
        rule = MathTex(r"\ker T", "=", r"\{\, \mathbf u \in V", r": T(\mathbf u) = \mathbf 0 \,\}", color=Palette.text, font_size=60)
        rule[0].set_color(Palette.pink)
        card = VGroup(
            Tex(r"The \emph{kernel} of a linear map $T : V \to W$ is", color=Palette.text, font_size=44),
            rule,
            Tex(r"For $T(\mathbf x) = A\mathbf x$, the kernel is exactly $\operatorname{Nul}A$.", color=Palette.text_muted, font_size=40),
        ).arrange(DOWN, buff=0.55).move_to(UP * 0.5)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(FadeIn(card[0], shift=UP * 0.15), run_time=0.8, rate_func=spring_soft)
        line = self.say(r"Any linear map $T : V \to W$ can ask that question.", line, hold=Timing.beat)
        line = self.say(r"Its \emph{kernel} is everything $T$ sends to $\mathbf 0$.", line, hold=0.2)
        self.play(Write(rule), run_time=1.4)
        self.wait(Timing.beat)
        line = self.say(r"The kernel is a set of inputs, so it lives in $V$.", line, hold=0.2)
        self.play(Indicate(rule[2], color=Palette.glow, scale_factor=1.1), run_time=0.9)
        self.wait(Timing.beat)
        self.play(FadeIn(card[2], shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)
        return None

    def derivative_kernel(self, line):
        left, right, arrow = d_panels()
        constants = VGroup(*[flat_line(left, c, Palette.pink) for c in CONSTANTS])
        zero = flat_line(right, 0, Palette.teal, stroke_width=8)
        self.play(FadeIn(left), FadeIn(right), GrowArrow(arrow[0]), FadeIn(arrow[1]), run_time=1.0)
        line = self.say(r"Try the derivative $D$ on $\mathbb P_3$.", line, hold=0.2)
        self.play(LaggedStart(*[Create(c) for c in constants], lag_ratio=0.2), FadeIn(corner_tag(left, r"\mathbf p = c", Palette.pink)), run_time=1.4)

        line = self.say(r"Every constant has slope 0, so it flattens to zero.", line, hold=0.2)
        copies = [c.copy() for c in constants]
        offset = right[1].get_center() - left[1].get_center()
        self.play(*[c.animate.shift(offset) for c in copies], run_time=1.4, rate_func=spring_soft)
        landings = [zero.copy() for _ in copies]
        self.play(*[ReplacementTransform(c, landing) for c, landing in zip(copies, landings)], run_time=1.2, rate_func=spring_soft)
        self.remove(*landings)
        self.add(zero)
        self.play(Indicate(zero, color=Palette.glow, scale_factor=1.0), FadeIn(corner_tag(right, r"D\mathbf p = 0", Palette.teal)), run_time=0.9)

        line = self.say(r"So $\ker D$ is the constants, $\operatorname{Span}\{1\}$.", line, hold=Timing.read_short)
        line = self.say(r"That is why every antiderivative carries a $+\,C$.", line, hold=Timing.read_short)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.7)
        return None

    def subspace_proof(self, line):
        title = Tex(r"$\ker T$ is a subspace of $V$", color=Palette.text, font_size=52)
        given = Tex(r"for $\mathbf u, \mathbf v$ in $\ker T$ and any scalar $c$", color=Palette.text_muted, font_size=38)
        rows = subspace_rows()
        card = VGroup(VGroup(title, given).arrange(DOWN, buff=0.25), rows).arrange(DOWN, buff=0.6).move_to(UP * 0.45)
        self.play(FadeIn(title, shift=UP * 0.15), FadeIn(given), run_time=0.9, rate_func=spring_soft)
        line = self.say(r"The kernel is always a subspace.", line, hold=Timing.beat)
        captions = (
            r"It holds $\mathbf 0$, since every linear map sends $\mathbf 0$ to $\mathbf 0$.",
            r"Sums of kernel vectors stay in the kernel.",
            r"Multiples stay in too, by linearity.",
        )
        for row, text in zip(rows, captions):
            line = self.say(text, line, hold=0.2)
            self.play(FadeIn(row, shift=RIGHT * 0.15), run_time=0.9, rate_func=spring_soft)
            self.play(Indicate(row[-1], color=Palette.glow, scale_factor=1.25), run_time=0.7)
            row[-1].set_color(Palette.glow)
            self.wait(0.5)
        self.play(FadeOut(card), FadeOut(line), run_time=0.6)
        return None

    def evaluation_map(self, line):
        panel = eval_panel()
        plane, plane_name = codomain_plane()
        pins = VGroup(*[pin_line(panel, pin) for pin in PINS])
        arrow = map_arrow(0.85, 2.3, EVAL_CENTER[1], "T")
        header = eval_header()
        self.panel, self.plane, self.pins = panel, plane, pins
        self.play(FadeIn(panel), FadeIn(domain_name(panel)), Create(plane, lag_ratio=0.02), FadeIn(plane_name), run_time=1.4)
        self.play(GrowArrow(arrow[0]), FadeIn(arrow[1]), Write(header), run_time=1.0)
        line = self.say(r"Now let $T$ read a curve's height at two pins.", line, hold=0.2)
        self.play(LaggedStart(*[Create(pin) for pin in pins], lag_ratio=0.3), run_time=1.0)
        self.wait(Timing.beat)

        self.legend = place_legend(legend_items(), panel)
        self.u = draw(panel, u_curve, Palette.yellow)
        line = self.say(r"$\mathbf u = t^2$ lands on $\mathbf b = (0, 1)$.", line, hold=0.2)
        self.play(Create(self.u), FadeIn(self.legend[0]), run_time=1.4, rate_func=smooth)
        self.u_arrow = self.send_through(u_curve, Palette.teal)
        self.b_tag = backed(MathTex(r"\mathbf b", color=Palette.teal, font_size=38), padding=0.06).next_to(plane.c2p(*B_POINT), RIGHT, buff=0.34)
        self.readout = readout_at(r"T(\mathbf u) = (0, 1)", Palette.teal)
        self.play(FadeIn(self.b_tag), FadeIn(self.readout), run_time=0.6)
        self.wait(Timing.beat)

        self.v = draw(panel, v_curve, Palette.blue)
        line = self.say(r"$\mathbf v = t$ is a different input with the same output.", line, hold=0.2)
        self.play(Create(self.v), FadeIn(self.legend[1]), run_time=1.4, rate_func=smooth)
        self.send_through(v_curve, Palette.teal)
        self.ring_b = glow_ring(plane.c2p(*B_POINT))
        both = readout_at(r"T(\mathbf u) = T(\mathbf v) = \mathbf b", Palette.teal)
        self.play(Create(self.ring_b), FadeTransform(self.readout, both), run_time=0.8)
        self.readout = both
        line = self.say(r"So this $T$ is not one-to-one.", line, hold=Timing.read_short)
        return line

    def send_through(self, function, color):
        """Pin dots on the curve fly to the axes of the codomain, then the output arrow grows to their point."""
        dots = pin_dots(self.panel, function)
        first, second = function(PINS[0][0]), function(PINS[1][0])
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in dots], lag_ratio=0.25), run_time=0.7)
        flying = dots.copy()
        self.play(
            flying[0].animate.move_to(self.plane.c2p(first, 0)),
            flying[1].animate.move_to(self.plane.c2p(0, second)),
            run_time=1.3,
            rate_func=spring_soft,
        )
        arrow = output_arrow(self.plane, (first, second), color)
        if np.hypot(first, second) < 1e-6:
            self.remove(flying)
            return dots
        self.play(GrowArrow(arrow), FadeOut(flying), run_time=0.9, rate_func=spring_soft)
        self.pin_marks = dots
        return arrow

    def centerpiece(self, line):
        panel = self.panel
        self.k = draw(panel, kernel_curve, Palette.pink, stroke_width=6)
        line = self.say(r"Subtract them: $\mathbf u - \mathbf v = t^2 - t$.", line, hold=0.2)
        self.play(FadeTransform(VGroup(self.u.copy(), self.v.copy()), self.k), FadeIn(self.legend[2]), run_time=1.6)
        self.wait(Timing.beat)

        line = self.say(r"Both pins read 0, so $\mathbf u - \mathbf v$ is in $\ker T$.", line, hold=0.2)
        zero_dots = pin_dots(panel, kernel_curve)
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in zero_dots], lag_ratio=0.25), run_time=0.7)
        flying = zero_dots.copy()
        origin = self.plane.c2p(0, 0)
        self.play(*[dot.animate.move_to(origin) for dot in flying], run_time=1.3, rate_func=spring_soft)
        self.zero_mark = Dot(origin, radius=0.1, color=Palette.pink).set_z_index(5)
        self.play(FadeOut(flying), GrowFromCenter(self.zero_mark), Flash(origin, color=Palette.glow, flash_radius=0.35), run_time=0.9)
        self.pin_marks = VGroup(self.pin_marks, zero_dots)
        self.wait(Timing.beat)

        proof = readout_at(r"T(\mathbf u - \mathbf v) = \mathbf b - \mathbf b = \mathbf 0", Palette.pink)
        line = self.say(r"Linearity forces it: $T(\mathbf u) - T(\mathbf v) = \mathbf 0$.", line, hold=0.2)
        self.play(FadeTransform(self.readout, proof), run_time=0.9)
        self.readout = proof
        self.wait(Timing.read_short)
        return line

    def kernel_line(self, line):
        panel = self.panel
        c = ValueTracker(1.0)
        live = always_redraw(lambda: draw(panel, multiple(c.get_value()), Palette.pink, stroke_width=6))
        self.remove(self.k)
        self.add(live)
        zero_ring = glow_ring(self.plane.c2p(0, 0))
        line = self.say(r"Every multiple of $t^2 - t$ lands on $\mathbf 0$ too.", line, hold=0.2)
        self.play(Create(zero_ring), run_time=0.6)
        ghosts = VGroup()
        for stop in KERNEL_STOPS:
            self.play(c.animate.set_value(stop), run_time=1.5, rate_func=spring)
            ghost = draw(panel, multiple(stop), Palette.pink, stroke_width=3, opacity=0.4)
            ghosts.add(ghost)
            self.add(ghost)
            self.wait(0.2)
        self.play(c.animate.set_value(1.0), run_time=1.2, rate_func=spring)
        self.remove(live)
        self.add(self.k)
        span = readout_at(r"\ker T = \operatorname{Span}\{t^2 - t\}", Palette.pink)
        line = self.say(r"So $\ker T = \operatorname{Span}\{t^2 - t\}$.", line, hold=0.2)
        self.play(FadeTransform(self.readout, span), run_time=0.9)
        self.readout = span
        self.wait(Timing.read_short)
        self.play(FadeOut(ghosts), FadeOut(zero_ring), self.k.animate.set_stroke(opacity=0.45), run_time=0.7)
        return line

    def pinned_family(self, line):
        panel = self.panel
        c = ValueTracker(0.0)
        live = always_redraw(lambda: draw(panel, family(c.get_value()), Palette.yellow, stroke_width=6))
        self.remove(self.u)
        self.add(live)
        self.bring_to_front(self.pin_marks)
        same = readout_at(r"T(\mathbf u + c\,(t^2 - t)) = \mathbf b", Palette.teal)
        line = self.say(r"Now add any kernel vector to $\mathbf u$.", line, hold=0.2)
        self.play(FadeTransform(self.readout, same), run_time=0.8)
        self.readout = same
        ghosts = VGroup()
        for stop in FAMILY_STOPS:
            self.play(c.animate.set_value(stop), run_time=1.6, rate_func=spring)
            ghost = draw(panel, family(stop), Palette.yellow, stroke_width=3, opacity=0.4)
            ghosts.add(ghost)
            self.add(ghost)
            self.play(Indicate(self.ring_b, color=Palette.glow, scale_factor=1.3), run_time=0.6)
        line = self.say(r"Every curve stays pinned, so every output is $\mathbf b$.", line, hold=0.2)
        self.play(c.animate.set_value(0.0), run_time=1.4, rate_func=spring)
        self.remove(live)
        self.add(self.u)
        self.bring_to_front(self.pin_marks)
        self.wait(Timing.read_short)
        self.family_ghosts = ghosts
        return line

    def theorem(self, line):
        veil = scrim().set_z_index(20)
        statement = Tex(r"$T$ is one-to-one exactly when $\ker T = \{\mathbf 0\}$.", color=Palette.text, font_size=50)
        reasons = VGroup(
            MathTex(r"T(\mathbf u) = T(\mathbf v)", r"\ \Longrightarrow\ ", r"\mathbf u - \mathbf v \in \ker T", color=Palette.text, font_size=46),
            MathTex(r"\mathbf k \in \ker T", r"\ \Longrightarrow\ ", r"T(\mathbf u + \mathbf k) = T(\mathbf u)", color=Palette.text, font_size=46),
        ).arrange(DOWN, buff=0.45)
        reasons[0][2].set_color(Palette.pink)
        reasons[1][0].set_color(Palette.pink)
        VGroup(statement, reasons).arrange(DOWN, buff=0.8).move_to(UP * 0.45).set_z_index(21)
        line = self.say(r"Two inputs with one output differ by a kernel vector.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(FadeIn(reasons[0], shift=UP * 0.15), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"A nonzero kernel vector gives two inputs one output.", line, hold=0.2)
        self.play(FadeIn(reasons[1], shift=UP * 0.15), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"So $T$ is one-to-one exactly when $\ker T = \{\mathbf 0\}$.", line, hold=0.2)
        self.play(FadeIn(statement, shift=DOWN * 0.15), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)
        keep = {id(self.panel), id(self.k), id(line)}
        leaving = [m for m in self.mobjects if id(m) not in keep and m not in self.pins]
        self.play(*[FadeOut(m) for m in leaving], self.k.animate.set_stroke(opacity=1.0), run_time=0.8)
        return line

    def third_pin(self, line):
        panel = self.panel
        third = pin_line(panel, THIRD_PIN)
        header = three_pin_header()
        c = ValueTracker(1.0)
        live = always_redraw(lambda: draw(panel, multiple(c.get_value()), Palette.pink, stroke_width=6))
        height = always_redraw(lambda: self.third_height(c.get_value()))
        reading = always_redraw(lambda: self.three_readings(c.get_value()))
        self.remove(self.k)
        self.add(live)
        line = self.say(r"Add a third pin at $t = -1$.", line, hold=0.2)
        self.play(Create(third), FadeIn(header), run_time=1.0)
        line = self.say(r"There $t^2 - t$ reads 2, not 0.", line, hold=0.2)
        self.play(FadeIn(height), FadeIn(reading), run_time=0.9)
        self.wait(Timing.read_short)
        line = self.say(r"A nonzero quadratic can't be zero at three places.", line, hold=0.2)
        self.play(c.animate.set_value(-0.6), run_time=1.6, rate_func=spring)
        self.wait(Timing.beat)
        self.play(c.animate.set_value(0.0), run_time=1.6, rate_func=spring)
        self.wait(Timing.beat)
        line = self.say(r"So this new $T$ has $\ker T = \{\mathbf 0\}$ and is one-to-one.", line, hold=Timing.read_long)
        return line

    def third_height(self, c_value):
        axes = self.panel[1]
        top = multiple(c_value)(THIRD_PIN[0])
        base = axes.c2p(THIRD_PIN[0], 0)
        tip = axes.c2p(THIRD_PIN[0], top)
        marks = VGroup(Dot(tip, radius=0.1, color=Palette.glow).set_z_index(5))
        if abs(top) > 0.05:
            marks.add(Line(base, tip, color=Palette.glow, stroke_width=6))
        label = backed(MathTex(one_place(top), color=Palette.glow, font_size=34), padding=0.06).next_to(tip, RIGHT, buff=0.18)
        return marks.add(label)

    def three_readings(self, c_value):
        k = multiple(c_value)
        entries = [one_place(k(t)) for t, _, _ in (THIRD_PIN, *PINS)]
        text = MathTex(
            r"T(c\,(t^2 - t)) = \begin{bmatrix} " + r" \\ ".join(entries) + r" \end{bmatrix}",
            color=Palette.text,
            font_size=42,
        )
        return text.move_to(np.array([CODOMAIN_CENTER[0], CODOMAIN_CENTER[1], 0]))


def eval_scene_base(scene, with_readout=True):
    panel = eval_panel()
    plane, plane_name = codomain_plane()
    pins = VGroup(*[pin_line(panel, pin) for pin in PINS])
    legend = place_legend(legend_items(), panel)
    scene.add(panel, domain_name(panel), plane, plane_name, pins, map_arrow(0.85, 2.3, EVAL_CENTER[1], "T"), eval_header(), legend)
    for stop in FAMILY_STOPS[:1] + FAMILY_STOPS[2:]:
        scene.add(draw(panel, family(stop), Palette.yellow, stroke_width=3, opacity=0.4))
    scene.add(draw(panel, kernel_curve, Palette.pink, stroke_width=6), draw(panel, v_curve, Palette.blue), draw(panel, u_curve, Palette.yellow))
    scene.add(pin_dots(panel, u_curve), pin_dots(panel, kernel_curve))
    scene.add(output_arrow(plane, B_POINT), glow_ring(plane.c2p(*B_POINT)), Dot(plane.c2p(0, 0), radius=0.1, color=Palette.pink))
    scene.add(backed(MathTex(r"\mathbf b", color=Palette.teal, font_size=38), padding=0.06).next_to(plane.c2p(*B_POINT), RIGHT, buff=0.34))
    if with_readout:
        scene.add(readout_at(r"T(\mathbf u) = T(\mathbf v) = \mathbf b", Palette.teal))


class FigSameOutput(Scene):
    def construct(self):
        eval_scene_base(self)
        fit_to_frame(self)


class FigConstantsFlatten(Scene):
    def construct(self):
        left, right, arrow = d_panels()
        self.add(left, right, arrow)
        self.add(*[flat_line(left, c, Palette.pink) for c in CONSTANTS], flat_line(right, 0, Palette.teal, stroke_width=8))
        self.add(corner_tag(left, r"\mathbf p = c", Palette.pink), corner_tag(right, r"D\mathbf p = 0", Palette.teal))
        fit_to_frame(self)


class FigThirdPin(Scene):
    def construct(self):
        panel = eval_panel()
        self.add(panel, *[pin_line(panel, pin) for pin in (THIRD_PIN, *PINS)], draw(panel, kernel_curve, Palette.pink, stroke_width=6))
        self.add(pin_dots(panel, kernel_curve))
        axes = panel[1]
        tip = axes.c2p(THIRD_PIN[0], kernel_curve(THIRD_PIN[0]))
        self.add(Line(axes.c2p(THIRD_PIN[0], 0), tip, color=Palette.glow, stroke_width=6), Dot(tip, radius=0.1, color=Palette.glow))
        self.add(backed(MathTex("2", color=Palette.glow, font_size=34), padding=0.06).next_to(tip, RIGHT, buff=0.18))
        self.add(backed(MathTex(r"t^2 - t", color=Palette.pink, font_size=36), padding=0.06).move_to(axes.c2p(1.45, 1.4)))
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        eval_scene_base(self, with_readout=False)
