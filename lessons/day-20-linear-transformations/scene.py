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
    fit_to_frame,
    make_plane,
    matrix,
    origin_pulse,
    plane_at,
    scrim,
    spring,
    spring_soft,
    vector_arrow,
)

V = (3, 2)
W = (-1, 2)
V_PLUS_W = (2, 4)
SHIFT = (1, -1)
T_RANGE = (-1.5, 1.5)
PLANE_ORIGIN = (-0.6, -0.9)
PLANE_UNIT = 1.15

PANEL_WIDTH = 5.2
PANEL_HEIGHT = 2.5
TOP_Y, BOTTOM_Y = 2.5, -0.9
LEFT_X, RIGHT_X = -3.6, 3.6
TOP_RANGE = (-2.5, 7)
BOTTOM_RANGE = (-7, 5.5)
SCALE_RANGE = (-7, 7)


def p(t):
    return 1 + 2 * t + t * t


def q(t):
    return t - t**3


def p_prime(t):
    return 2 + 2 * t


def q_prime(t):
    return 1 - 3 * t * t


def sum_curve(t):
    return p(t) + q(t)


def sum_prime(t):
    return p_prime(t) + q_prime(t)


def turned(point):
    return (-point[1], point[0])


def shifted(point):
    return (point[0] + SHIFT[0], point[1] + SHIFT[1])


def graph_panel(center, y_range, width=PANEL_WIDTH, height=PANEL_HEIGHT):
    """Axes for t in T_RANGE on a faint plate, with no numbers, centered at `center`."""
    axes = Axes(
        x_range=(*T_RANGE, 0.5),
        y_range=(*y_range, 1),
        x_length=width,
        y_length=height,
        tips=False,
        axis_config={"color": Palette.axis, "stroke_width": 2, "include_ticks": False},
    )
    axes.move_to(np.array([center[0], center[1], 0]))
    plate = Rectangle(width=width, height=height, fill_color=Palette.grid_faint, fill_opacity=0.35, stroke_width=0).move_to(axes)
    return VGroup(plate, axes)


def plot(panel, function, color, stroke_width=5, t_range=T_RANGE):
    return panel[1].plot(function, x_range=[*t_range, 0.01], color=color, stroke_width=stroke_width)


def dashed(curve, color=Palette.text, stroke_width=3):
    line = DashedVMobject(curve.copy().set_stroke(color, stroke_width), num_dashes=60, dashed_ratio=0.55)
    return line


def panel_formulas(panel, *entries, font_size=30, corner=UL):
    """Formulas stacked in one corner of the panel, above its curves, each (tex, color)."""
    lines = VGroup(*[MathTex(tex, color=color, font_size=font_size) for tex, color in entries])
    lines.arrange(DOWN, buff=0.12, aligned_edge=LEFT)
    inset = np.array([-0.15 * corner[0], -0.12 * corner[1], 0])
    lines.move_to(panel[0].get_corner(corner) + inset, aligned_edge=corner)
    return backed(lines, padding=0.06, opacity=0.9).set_z_index(3)


def square_panels(bottom_range=BOTTOM_RANGE, top_range=TOP_RANGE):
    return {
        "tl": graph_panel((LEFT_X, TOP_Y), top_range),
        "tr": graph_panel((RIGHT_X, TOP_Y), top_range),
        "bl": graph_panel((LEFT_X, BOTTOM_Y), bottom_range),
        "br": graph_panel((RIGHT_X, BOTTOM_Y), bottom_range),
    }


def route_arrow(start, end, tex, side, is_math=True):
    arrow = Arrow(np.array([*start, 0]), np.array([*end, 0]), buff=0, color=Palette.text_muted, stroke_width=5, max_tip_length_to_length_ratio=0.3)
    label = (MathTex if is_math else Tex)(tex, color=Palette.text, font_size=34).next_to(arrow, side, buff=0.12)
    return VGroup(arrow, label)


def square_arrows(across_tex=r"add", across_math=False):
    gap_top, gap_bottom = TOP_Y - PANEL_HEIGHT / 2 - 0.08, BOTTOM_Y + PANEL_HEIGHT / 2 + 0.08
    inner_left, inner_right = LEFT_X + PANEL_WIDTH / 2 + 0.12, RIGHT_X - PANEL_WIDTH / 2 - 0.12
    return {
        "top": route_arrow((inner_left, TOP_Y), (inner_right, TOP_Y), across_tex, UP, across_math),
        "right": route_arrow((RIGHT_X, gap_top), (RIGHT_X, gap_bottom), "D", RIGHT),
        "left": route_arrow((LEFT_X, gap_top), (LEFT_X, gap_bottom), "D", LEFT),
        "bottom": route_arrow((inner_left, BOTTOM_Y), (inner_right, BOTTOM_Y), across_tex, UP, across_math),
    }


def tangent_mark(panel, function, slope, t_value, length=1.1):
    """A short orange tangent segment and dot at t on the curve drawn in `panel`."""
    axes = panel[1]
    point = axes.c2p(t_value, function(t_value))
    ahead = axes.c2p(t_value + 0.01, function(t_value) + 0.01 * slope(t_value)) - point
    direction = ahead / np.linalg.norm(ahead)
    segment = Line(point - direction * length / 2, point + direction * length / 2, color=Palette.glow, stroke_width=4)
    return VGroup(segment, Dot(point, radius=0.06, color=Palette.glow))


def partial_plot(panel, function, color, upto):
    if upto <= T_RANGE[0] + 0.02:
        return VGroup()
    return plot(panel, function, color, t_range=(T_RANGE[0], upto))


INPUTS = [(0, Palette.yellow, "t^2"), (1, Palette.blue, "t^2 + 1"), (-2, Palette.pink, "t^2 - 2")]


def collapse_panels(center_y):
    left = graph_panel((-3.6, center_y), (-2.5, 7), width=5.6, height=4.4)
    right = graph_panel((3.6, center_y), (-4, 4), width=5.6, height=4.4)
    arrow = route_arrow((-0.6, center_y), (0.6, center_y), "D", UP)
    return left, right, arrow


def output_legend(panel):
    return panel_formulas(panel, ("2t", Palette.teal))


def cubic_legend(panel):
    legend = panel_formulas(panel, ("t^3", Palette.text_muted))
    return legend.shift(DOWN * 0.5)


class Lesson(LessonScene):
    day = 20
    title = "Linear transformations between vector spaces"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.pose_question()
        line = self.turn_keeps_sums(plane, line)
        line = self.translation_fails(plane, line)
        line = self.general_definition(line)
        line = self.derivative_square(line)
        line = self.derivative_scales(line)
        line = self.transpose(line)
        line = self.not_one_to_one(line)
        self.close_episode(
            r"A linear transformation is any map that keeps sums and multiples.\\"
            r"Matrix maps, derivatives and transposes all qualify.",
            *self.mobjects,
        )

    def parallelogram(self, plane, corners, opacity=0.14):
        return Polygon(*[plane.c2p(*corner) for corner in corners], stroke_width=0, fill_color=Palette.teal, fill_opacity=opacity)

    def pose_question(self):
        spaces = VGroup(
            MathTex(r"1 + 2t + t^2", r"\text{ in }", r"\mathbb P_3", color=Palette.text, font_size=40),
            MathTex(r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}", r"\text{ in }", r"M_{2\times 2}", color=Palette.text, font_size=40),
            MathTex(r"(3, 2)", r"\text{ in }", r"\mathbb R^2", color=Palette.text, font_size=40),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        question = MathTex(r"T : V \to W", color=Palette.text, font_size=44).next_to(spaces, DOWN, buff=0.4, aligned_edge=LEFT)
        panel = backed(VGroup(spaces, question), padding=0.3).to_corner(UL, buff=0.5)
        line = self.say(r"Since Day 10, polynomials and matrices count as vectors too.", hold=0.2)
        self.play(FadeIn(panel.background_rectangle), LaggedStart(*[FadeIn(row, shift=DOWN * 0.1) for row in spaces], lag_ratio=0.3), run_time=1.6)
        self.wait(0.5)
        line = self.say(r"So which maps between vector spaces deserve the name linear?", line, hold=0.2)
        self.play(Write(question), run_time=1.0)
        self.wait(Timing.beat + 0.5)
        self.play(FadeOut(panel), run_time=0.5)
        return line

    def turn_keeps_sums(self, plane, line):
        shape = self.parallelogram(plane, [(0, 0), V, V_PLUS_W, W])
        arrows = VGroup(
            vector_arrow(V, Palette.yellow, plane),
            vector_arrow(W, Palette.blue, plane),
            vector_arrow(V_PLUS_W, Palette.teal, plane),
        )
        names = VGroup(
            backed(MathTex(r"\mathbf v", color=Palette.yellow)).next_to(plane.c2p(*V), RIGHT, buff=0.15),
            backed(MathTex(r"\mathbf w", color=Palette.blue)).next_to(plane.c2p(*W), LEFT, buff=0.15),
            backed(MathTex(r"\mathbf v + \mathbf w", color=Palette.teal)).next_to(plane.c2p(*V_PLUS_W), UP, buff=0.12),
        )
        line = self.say(r"On Day 5, a matrix moved the plane and kept sums.", line, hold=0.2)
        self.play(GrowArrow(arrows[0]), GrowArrow(arrows[1]), FadeIn(names[:2]), run_time=1.2, rate_func=spring_soft)
        self.play(FadeIn(shape), GrowArrow(arrows[2]), FadeIn(names[2]), run_time=1.2, rate_func=spring_soft)
        self.wait(Timing.read_short)

        figure = VGroup(shape, arrows)
        line = self.say(r"A quarter turn carries the whole parallelogram along.", line, hold=0.2)
        self.play(FadeOut(names), run_time=0.4)
        self.play(Rotate(figure, PI / 2, about_point=plane.c2p(0, 0)), run_time=2.0, rate_func=spring_soft)
        images = VGroup(
            backed(MathTex(r"T(\mathbf v)", color=Palette.yellow)).next_to(plane.c2p(*turned(V)), UP, buff=0.12),
            backed(MathTex(r"T(\mathbf w)", color=Palette.blue)).next_to(plane.c2p(*turned(W)), DOWN, buff=0.12),
            backed(MathTex(r"T(\mathbf v + \mathbf w)", color=Palette.teal)).next_to(plane.c2p(*turned(V_PLUS_W)), UP, buff=0.3),
        )
        ring = Circle(radius=0.2, color=Palette.glow, stroke_width=4).move_to(plane.c2p(*turned(V_PLUS_W)))
        self.play(FadeIn(images, shift=UP * 0.1), run_time=0.8, rate_func=spring)
        line = self.say(r"So $T(\mathbf v + \mathbf w)$ is still $T(\mathbf v) + T(\mathbf w)$.", line, hold=0.2)
        self.play(Create(ring), run_time=0.7)
        self.wait(Timing.read_short)

        rules = backed(
            VGroup(
                MathTex(r"T(\mathbf u + \mathbf v) = T(\mathbf u) + T(\mathbf v)", color=Palette.text, font_size=40),
                MathTex(r"T(c\,\mathbf u) = c\,T(\mathbf u)", color=Palette.text, font_size=40),
            ).arrange(DOWN, buff=0.25, aligned_edge=LEFT),
            padding=0.3,
        ).to_corner(UR, buff=0.5)
        line = self.say(r"Maps that keep sums and multiples are called \emph{linear}.", line, hold=0.2)
        self.play(FadeIn(rules, shift=DOWN * 0.15), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(rules, images, ring)), run_time=0.6)
        self.play(Rotate(figure, -PI / 2, about_point=plane.c2p(0, 0)), run_time=1.4, rate_func=spring_soft)
        self.figure = figure
        return line

    def translation_fails(self, plane, line):
        figure = self.figure
        pulse = origin_pulse(plane)
        self.play(GrowFromCenter(pulse), run_time=0.6, rate_func=spring)
        offset = plane.c2p(*SHIFT) - plane.c2p(0, 0)
        line = self.say(r"A translation slides everything, even the origin.", line, hold=0.2)
        self.play(figure.animate.shift(offset), pulse.animate.shift(offset), run_time=1.8, rate_func=spring_soft)
        origin_tag = backed(MathTex(r"T(\mathbf 0)", color=Palette.glow, font_size=38)).next_to(pulse, LEFT, buff=0.15)
        self.play(FadeIn(origin_tag, shift=UP * 0.1), run_time=0.6)
        self.wait(Timing.read_short)

        corner = Dot(plane.c2p(*shifted(V_PLUS_W)), radius=0.09, color=Palette.teal)
        corner_tag = backed(MathTex(r"T(\mathbf v + \mathbf w)", color=Palette.teal, font_size=38)).next_to(corner, UP, buff=0.15)
        self.play(FadeOut(figure[1]), FadeIn(corner), FadeIn(corner_tag), run_time=0.8)
        line = self.say(r"Now add $T(\mathbf v)$ and $T(\mathbf w)$ from the true origin.", line, hold=0.2)
        tip = self.tip_to_tail_images(plane)
        line = self.say(r"The sum misses $T(\mathbf v + \mathbf w)$ by the shift itself.", line, hold=0.2)
        gap = DashedLine(plane.c2p(*tip), corner.get_center(), color=Palette.glow, stroke_width=4, dash_length=0.1)
        self.play(Create(gap), Flash(corner, color=Palette.glow), run_time=0.9)
        self.wait(Timing.read_short)

        line = self.zero_goes_to_zero(line)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not line and m is not plane], run_time=0.7)
        return line

    def tip_to_tail_images(self, plane):
        t_v, t_w = shifted(V), shifted(W)
        tip = (t_v[0] + t_w[0], t_v[1] + t_w[1])
        v_image = vector_arrow(t_v, Palette.yellow, plane)
        w_image = vector_arrow(t_w, Palette.blue, plane)
        tags = VGroup(
            backed(MathTex(r"T(\mathbf v)", color=Palette.yellow, font_size=36)).next_to(plane.c2p(*t_v), DR, buff=0.08),
            backed(MathTex(r"T(\mathbf w)", color=Palette.blue, font_size=36)).next_to(plane.c2p(*t_w), LEFT, buff=0.15),
        )
        self.play(GrowArrow(v_image), GrowArrow(w_image), FadeIn(tags), run_time=1.2, rate_func=spring_soft)
        moved = arrow_between(plane, t_v, tip, Palette.blue)
        self.play(TransformFromCopy(w_image, moved), run_time=1.3, rate_func=spring)
        total = vector_arrow(tip, Palette.pink, plane)
        total_tag = backed(MathTex(r"T(\mathbf v) + T(\mathbf w)", color=Palette.pink, font_size=36)).next_to(plane.c2p(*tip), RIGHT, buff=0.2)
        self.play(GrowArrow(total), FadeIn(total_tag), run_time=1.1, rate_func=spring_soft)
        self.wait(Timing.beat)
        return tip

    def zero_goes_to_zero(self, line):
        steps = MathTex(
            r"T(\mathbf 0)", r"&= T(0\,\mathbf u)", r"\\ &= 0\,T(\mathbf u)", r"\\ &= \mathbf 0",
            color=Palette.text,
            font_size=42,
        )
        panel = backed(steps, padding=0.3).to_corner(UL, buff=0.5)
        line = self.say(r"Every linear map must send $\mathbf 0$ to $\mathbf 0$.", line, hold=0.2)
        self.play(FadeIn(panel.background_rectangle), Write(steps[:2]), run_time=1.0)
        for part in steps[2:]:
            self.play(FadeIn(part, shift=DOWN * 0.1), run_time=0.7, rate_func=spring)
        self.wait(Timing.read_short)
        line = self.say(r"A translation moves $\mathbf 0$, so it is not linear.", line, hold=Timing.read_short)
        return line

    def general_definition(self, line):
        veil = scrim()
        card = VGroup(
            Tex(r"A \emph{linear transformation} $T : V \to W$ satisfies", color=Palette.text, font_size=44),
            MathTex(r"T(\mathbf u + \mathbf v) = T(\mathbf u) + T(\mathbf v)", color=Palette.text, font_size=48),
            MathTex(r"T(c\,\mathbf u) = c\,T(\mathbf u)", color=Palette.text, font_size=48),
            Tex(r"for all $\mathbf u, \mathbf v$ in $V$ and every scalar $c$.", color=Palette.text_muted, font_size=40),
        ).arrange(DOWN, buff=0.4).move_to(UP * 0.5)
        line = self.say(r"The same two rules make sense in any vector space.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(FadeIn(card[0], shift=UP * 0.15), run_time=0.8, rate_func=spring_soft)
        self.play(FadeIn(card[1:3], shift=UP * 0.15), run_time=0.8, rate_func=spring_soft)
        self.play(FadeIn(card[3]), run_time=0.6)
        self.wait(Timing.read_long)
        line = self.say(r"Let's test them on the derivative.", line, hold=Timing.beat)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not line], run_time=0.7)
        return line

    def derivative_square(self, line):
        panels = square_panels()
        routes = square_arrows()
        self.panels, self.routes = panels, routes
        self.play(LaggedStart(*[FadeIn(panel) for panel in panels.values()], lag_ratio=0.15), run_time=1.2)

        curves = {"p": plot(panels["tl"], p, Palette.yellow), "q": plot(panels["tl"], q, Palette.blue)}
        top_left = panel_formulas(panels["tl"], (r"\mathbf p = 1 + 2t + t^2", Palette.yellow), (r"\mathbf q = t - t^3", Palette.blue))
        line = self.say(r"Here are two polynomials in $\mathbb P_3$.", line, hold=0.2)
        self.play(FadeIn(top_left), Create(curves["p"]), Create(curves["q"]), run_time=1.6, rate_func=smooth)
        self.wait(Timing.beat)
        line = self.say(r"If $D$ is linear, both routes around this square agree.", line, hold=0.2)
        self.play(Indicate(VGroup(curves["p"], curves["q"]), color=Palette.glow, scale_factor=1.04), run_time=1.0)
        self.wait(0.5)

        line = self.say(r"First add them, then take the derivative.", line, hold=0.2)
        curves["sum"] = self.add_across(panels["tl"], panels["tr"], [curves["p"], curves["q"]], plot(panels["tr"], sum_curve, Palette.teal), routes["top"])
        top_right = panel_formulas(panels["tr"], (r"\mathbf p + \mathbf q = 1 + 3t + t^2 - t^3", Palette.teal), corner=DR)
        self.play(FadeIn(top_right), run_time=0.6)
        self.wait(Timing.beat)

        line = self.say(r"The height of the new curve is the slope of the old one.", line, hold=0.2)
        self.play(GrowArrow(routes["right"][0]), FadeIn(routes["right"][1]), run_time=0.8, rate_func=spring_soft)
        curves["sum_prime"] = self.trace_derivatives(panels["tr"], panels["br"], [(sum_curve, sum_prime, Palette.teal)])[0]
        bottom_right = panel_formulas(panels["br"], (r"D(\mathbf p + \mathbf q) = 3 + 2t - 3t^2", Palette.teal), corner=DR)
        self.play(FadeIn(bottom_right), run_time=0.6)
        self.wait(Timing.beat)

        line = self.say(r"Now take each derivative first.", line, hold=0.2)
        self.play(GrowArrow(routes["left"][0]), FadeIn(routes["left"][1]), run_time=0.8, rate_func=spring_soft)
        pieces = [(p, p_prime, Palette.yellow), (q, q_prime, Palette.blue)]
        curves["p_prime"], curves["q_prime"] = self.trace_derivatives(panels["tl"], panels["bl"], pieces)
        bottom_left = panel_formulas(panels["bl"], (r"D\mathbf p = 2 + 2t", Palette.yellow), (r"D\mathbf q = 1 - 3t^2", Palette.blue))
        self.play(FadeIn(bottom_left), run_time=0.6)
        self.wait(Timing.beat)

        line = self.say(r"Then add the two derivatives.", line, hold=0.2)
        second_route = dashed(plot(panels["br"], sum_prime, Palette.text))
        self.add_across(panels["bl"], panels["br"], [curves["p_prime"], curves["q_prime"]], second_route, routes["bottom"])
        line = self.say(r"Both routes land on the same curve.", line, hold=0.2)
        self.stamp_matches(panels["br"])
        line = self.say(r"So $D(\mathbf p + \mathbf q) = D\mathbf p + D\mathbf q$.", line, hold=Timing.read_short)
        self.curves = curves
        self.square_extras = VGroup(top_left, top_right, bottom_right, bottom_left, second_route)
        return line

    def add_across(self, source, target, pieces, result, route):
        """Copies of `pieces` slide from panel `source` to `target` and merge into `result`."""
        self.play(GrowArrow(route[0]), FadeIn(route[1]), run_time=0.8, rate_func=spring_soft)
        offset = target[1].get_center() - source[1].get_center()
        self.merge_copies(pieces, offset, result)
        return result

    def merge_copies(self, pieces, offset, result):
        """Copies of `pieces` shift by `offset`, then all morph into `result`."""
        copies = [piece.copy() for piece in pieces]
        landings = [result.copy() for _ in pieces]
        self.play(*[piece.animate.shift(offset) for piece in copies], run_time=1.4, rate_func=spring_soft)
        self.play(*[ReplacementTransform(piece, landing) for piece, landing in zip(copies, landings)], run_time=1.2)
        self.remove(*landings)
        self.add(result)

    def trace_derivatives(self, source, target, pieces):
        """Tangents slide along each curve in `source` while the slope is drawn in `target`."""
        sweep = ValueTracker(T_RANGE[0])
        marks = VGroup(*[always_redraw(lambda f=f, df=df: tangent_mark(source, f, df, sweep.get_value())) for f, df, _ in pieces])
        traces = VGroup(*[always_redraw(lambda df=df, c=c: partial_plot(target, df, c, sweep.get_value())) for _, df, c in pieces])
        pens = VGroup(*[always_redraw(lambda df=df: Dot(target[1].c2p(sweep.get_value(), df(sweep.get_value())), radius=0.07, color=Palette.glow)) for _, df, _ in pieces])
        self.play(FadeIn(marks), FadeIn(pens), run_time=0.4)
        self.add(traces)
        self.play(sweep.animate.set_value(T_RANGE[1]), run_time=3.6, rate_func=smooth)
        finished = [plot(target, df, c) for _, df, c in pieces]
        self.remove(traces)
        self.add(*finished)
        self.play(FadeOut(marks), FadeOut(pens), run_time=0.4)
        return finished

    def stamp_matches(self, panel):
        stamps = VGroup(*[Dot(panel[1].c2p(t, sum_prime(t)), radius=0.08, color=Palette.glow) for t in (-1.0, 0.0, 1.0)])
        self.play(LaggedStart(*[GrowFromCenter(stamp) for stamp in stamps], lag_ratio=0.3), run_time=1.0)
        self.play(*[Flash(stamp, color=Palette.glow, flash_radius=0.25) for stamp in stamps], run_time=0.8)
        self.wait(Timing.beat)
        self.play(FadeOut(stamps), run_time=0.4)

    def derivative_scales(self, line):
        panels, curves = self.panels, self.curves
        leaving = VGroup(self.square_extras, curves["q"], curves["sum"], curves["sum_prime"], curves["q_prime"], self.routes["top"], self.routes["bottom"])
        self.play(FadeOut(leaving), FadeOut(curves["p"]), FadeOut(curves["p_prime"]), run_time=0.7)
        scaled = square_panels(bottom_range=SCALE_RANGE, top_range=SCALE_RANGE)
        self.play(*[ReplacementTransform(panels[key], scaled[key]) for key in panels], run_time=0.8)
        panels = scaled

        c = ValueTracker(1.0)
        fixed = VGroup(plot(panels["tl"], p, Palette.yellow), plot(panels["bl"], p_prime, Palette.yellow))
        live = VGroup(
            always_redraw(lambda: plot(panels["tr"], lambda t: c.get_value() * p(t), Palette.teal)),
            always_redraw(lambda: plot(panels["br"], lambda t: c.get_value() * p_prime(t), Palette.teal, stroke_width=7)),
            always_redraw(lambda: dashed(plot(panels["br"], lambda t: c.get_value() * p_prime(t), Palette.text))),
        )
        routes = square_arrows(r"\times c", across_math=True)
        readout = always_redraw(lambda: self.c_readout(c.get_value()))
        labels = VGroup(
            panel_formulas(panels["tl"], (r"\mathbf p", Palette.yellow)),
            panel_formulas(panels["bl"], (r"D\mathbf p", Palette.yellow)),
            panel_formulas(panels["tr"], (r"c\,\mathbf p", Palette.teal)),
            panel_formulas(panels["br"], (r"D(c\,\mathbf p) = c\,D\mathbf p", Palette.teal)),
        )
        line = self.say(r"Scaling works the same way.", line, hold=0.2)
        self.play(FadeIn(fixed), FadeIn(labels), FadeIn(routes["top"]), FadeIn(routes["bottom"]), FadeIn(readout), run_time=1.0)
        self.play(FadeIn(live), run_time=0.8)
        for target in (-1.0, 0.5):
            self.play(c.animate.set_value(target), run_time=1.8, rate_func=spring)
            self.wait(Timing.beat)
        line = self.say(r"$D(c\,\mathbf p) = c\,D\mathbf p$ for every $c$, so $D$ is linear.", line, hold=0.2)
        self.play(c.animate.set_value(1.0), run_time=1.8, rate_func=spring)
        self.wait(Timing.beat)
        self.leftovers = [m for m in self.mobjects if m is not line]
        return line

    @staticmethod
    def c_readout(c_value):
        text = MathTex(rf"c = {c_value:.2f}", color=Palette.teal, font_size=36)
        return text.move_to(np.array([0, (TOP_Y + BOTTOM_Y) / 2, 0]))

    def transpose(self, line):
        a = matrix([[1, 4], [-2, 3]], color=Palette.yellow)
        a_t = matrix([[1, -2], [4, 3]], color=Palette.yellow)
        name = MathTex(r"A", "=", color=Palette.yellow, font_size=48)
        name_t = MathTex(r"A^T", "=", color=Palette.yellow, font_size=48)
        top = VGroup(name, a).arrange(RIGHT, buff=0.25)
        bottom = VGroup(name_t, a_t).arrange(RIGHT, buff=0.25)
        VGroup(top, bottom).arrange(RIGHT, buff=1.6).scale(1.35).move_to(UP * 1.3)
        swap = Arrow(top.get_right(), bottom.get_left(), buff=0.3, color=Palette.text_muted, stroke_width=5)
        line = self.say(r"Transposing a matrix is linear too.", line, hold=0.2)
        self.play(*[FadeOut(m) for m in self.leftovers], FadeIn(top, shift=UP * 0.15), run_time=0.9, rate_func=spring_soft)
        self.play(GrowArrow(swap), FadeIn(name_t), FadeIn(a_t.get_brackets()), run_time=0.8)
        self.swap_entries(a.get_entries(), a_t.get_entries())
        rules = VGroup(
            MathTex(r"(A + B)^T = A^T + B^T", color=Palette.text, font_size=56),
            MathTex(r"(cA)^T = c\,A^T", color=Palette.text, font_size=56),
        ).arrange(DOWN, buff=0.35).move_to(DOWN * 1.3)
        line = self.say(r"It only moves entries, so sums and multiples come along.", line, hold=0.2)
        self.play(FadeIn(rules, shift=UP * 0.15), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_long)
        self.leftovers = [m for m in self.mobjects if m is not line]
        return line

    def swap_entries(self, entries, targets):
        """Copy A's entries into A^T's brackets in place, then swap the off-diagonal pair across the diagonal."""
        copies = [entry.copy() for entry in entries]
        self.play(*[copy.animate(path_arc=-0.9).move_to(target) for copy, target in zip(copies, targets)], run_time=1.2, rate_func=spring_soft)
        off_diagonal = VGroup(copies[1], copies[2])
        self.play(Indicate(off_diagonal, color=Palette.glow, scale_factor=1.15), run_time=0.7)
        self.play(
            copies[1].animate(path_arc=-PI / 2).move_to(targets[2]),
            copies[2].animate(path_arc=-PI / 2).move_to(targets[1]),
            run_time=1.3,
            rate_func=spring_soft,
        )
        self.wait(Timing.beat)

    def not_one_to_one(self, line):
        left, right, arrow = collapse_panels(0.55)
        parabolas = VGroup(*[plot(left, lambda t, k=k: t * t + k, color) for k, color, _ in INPUTS])
        tags = panel_formulas(left, *[(tex, color) for _, color, tex in sorted(INPUTS, key=lambda item: -item[0])])
        self.play(*[FadeOut(m) for m in self.leftovers], FadeIn(left), FadeIn(right), GrowArrow(arrow[0]), FadeIn(arrow[1]), run_time=1.0)
        line = self.say(r"Different inputs can share one output under $D$.", line, hold=0.2)
        self.play(LaggedStart(*[Create(curve) for curve in parabolas], lag_ratio=0.25), FadeIn(tags), run_time=1.8)
        tangents = VGroup(*[tangent_mark(left, lambda t, k=k: t * t + k, lambda t: 2 * t, 1.0, length=1.8) for k, _, _ in INPUTS])
        self.play(LaggedStart(*[GrowFromCenter(mark) for mark in tangents], lag_ratio=0.2), run_time=1.0)
        self.wait(Timing.beat)

        output = plot(right, lambda t: 2 * t, Palette.teal)
        offset = right[1].get_center() - left[1].get_center()
        self.merge_copies(list(parabolas), offset, output)
        self.play(FadeIn(output_legend(right)), run_time=0.5)
        line = self.say(r"So $D$ is not one-to-one.", line, hold=Timing.read_short)
        line = self.missing_cubic(right, line)
        line = self.say(r"So $D$ is not onto $\mathbb P_3$ either.", line, hold=Timing.read_short)
        line = self.say(r"Next, Day 21 writes maps like $D$ as matrices.", line, hold=0.2)
        self.play(Indicate(arrow, color=Palette.glow, scale_factor=1.15), run_time=1.0)
        self.wait(Timing.read_short)
        return line

    def missing_cubic(self, right, line):
        cubic = dashed(plot(right, lambda t: t**3, Palette.text_muted), color=Palette.text_muted, stroke_width=4)
        cubic_tag = cubic_legend(right)
        ring = Circle(radius=0.22, color=Palette.glow, stroke_width=4).move_to(right[1].c2p(-1.0, -1.0))
        line = self.say(r"No polynomial in $\mathbb P_3$ has derivative $t^3$.", line, hold=0.2)
        self.play(Create(cubic), FadeIn(cubic_tag), run_time=1.4)
        self.play(Create(ring), run_time=0.6)
        self.wait(Timing.read_short)
        return line


def full_square(scene):
    panels = square_panels()
    routes = square_arrows()
    curves = VGroup(
        plot(panels["tl"], p, Palette.yellow),
        plot(panels["tl"], q, Palette.blue),
        plot(panels["tr"], sum_curve, Palette.teal),
        plot(panels["bl"], p_prime, Palette.yellow),
        plot(panels["bl"], q_prime, Palette.blue),
        plot(panels["br"], sum_prime, Palette.teal, stroke_width=7),
        dashed(plot(panels["br"], sum_prime, Palette.text)),
    )
    formulas = VGroup(
        panel_formulas(panels["tl"], (r"\mathbf p = 1 + 2t + t^2", Palette.yellow), (r"\mathbf q = t - t^3", Palette.blue)),
        panel_formulas(panels["tr"], (r"\mathbf p + \mathbf q = 1 + 3t + t^2 - t^3", Palette.teal), corner=DR),
        panel_formulas(panels["bl"], (r"D\mathbf p = 2 + 2t", Palette.yellow), (r"D\mathbf q = 1 - 3t^2", Palette.blue)),
        panel_formulas(panels["br"], (r"D(\mathbf p + \mathbf q) = 3 + 2t - 3t^2", Palette.teal), corner=DR),
    )
    scene.add(*panels.values(), *[route for route in routes.values()], curves, formulas)


class FigDerivativeSquare(Scene):
    def construct(self):
        full_square(self)
        fit_to_frame(self)


class FigTranslationMisses(Scene):
    def construct(self):
        plane = make_plane(x_range=(-2, 6, 1), y_range=(-2, 4.5, 1))
        corners = [shifted(point) for point in [(0, 0), V, V_PLUS_W, W]]
        shape = Polygon(*[plane.c2p(*corner) for corner in corners], stroke_width=0, fill_color=Palette.teal, fill_opacity=0.14)
        t_v, t_w = shifted(V), shifted(W)
        tip = (t_v[0] + t_w[0], t_v[1] + t_w[1])
        corner = plane.c2p(*shifted(V_PLUS_W))
        labels = VGroup(
            backed(MathTex(r"T(\mathbf 0)", color=Palette.glow, font_size=36)).next_to(plane.c2p(*SHIFT), LEFT, buff=0.35),
            backed(MathTex(r"T(\mathbf v)", color=Palette.yellow, font_size=36)).next_to(plane.c2p(*t_v), DR, buff=0.08),
            backed(MathTex(r"T(\mathbf w)", color=Palette.blue, font_size=36)).next_to(plane.c2p(*t_w), LEFT, buff=0.15),
            backed(MathTex(r"T(\mathbf v) + T(\mathbf w)", color=Palette.pink, font_size=36)).next_to(plane.c2p(*tip), RIGHT, buff=0.2),
            backed(MathTex(r"T(\mathbf v + \mathbf w)", color=Palette.teal, font_size=36)).next_to(corner, UP, buff=0.15),
        )
        self.add(
            plane,
            shape,
            origin_pulse(plane).shift(plane.c2p(*SHIFT) - plane.c2p(0, 0)),
            vector_arrow(t_v, Palette.yellow, plane),
            vector_arrow(t_w, Palette.blue, plane),
            arrow_between(plane, t_v, tip, Palette.blue),
            vector_arrow(tip, Palette.pink, plane),
            Dot(corner, radius=0.09, color=Palette.teal),
            DashedLine(plane.c2p(*tip), corner, color=Palette.glow, stroke_width=4, dash_length=0.1),
            labels,
        )
        fit_to_frame(self)


class FigSharedDerivative(Scene):
    def construct(self):
        left, right, arrow = collapse_panels(0)
        self.add(left, right, arrow)
        for k, color, _ in INPUTS:
            self.add(plot(left, lambda t, k=k: t * t + k, color))
            self.add(tangent_mark(left, lambda t, k=k: t * t + k, lambda t: 2 * t, 1.0, length=1.8))
        self.add(panel_formulas(left, *[(tex, color) for _, color, tex in sorted(INPUTS, key=lambda item: -item[0])]))
        self.add(plot(right, lambda t: 2 * t, Palette.teal))
        self.add(dashed(plot(right, lambda t: t**3, Palette.text_muted), color=Palette.text_muted, stroke_width=4))
        self.add(output_legend(right), cubic_legend(right))
        self.add(Circle(radius=0.22, color=Palette.glow, stroke_width=4).move_to(right[1].c2p(-1.0, -1.0)))
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        full_square(self)
