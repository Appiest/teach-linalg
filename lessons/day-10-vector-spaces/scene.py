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
    make_plane,
    matrix,
    oblique_projector,
    plane_at,
    projected_arrow,
    projected_axes,
    slider,
    spring,
    spring_soft,
    vector_arrow,
)

V = (3, 2)
W = (-1, 2)
P = (1, 2, -1)
Q = (2, -1, 1)
P_PLUS_Q = (3, 1, 0)
SAMPLE_TIMES = (0, 1, 2)
T_RANGE = (-0.25, 2.25)
GRAPH_CENTER = (-3.55, -0.95)
SPACE_ORIGIN = (2.3, 0.3)
COEFFICIENT_REACH = ((-1, 3), (-2, 4), (-2, 1))
U_SET = (2, 1)
V_SET = (-1, -3)
SET_ORIGIN = (-0.6, 0.55)
SET_UNIT = 0.85

AXIOMS = {
    1: r"\mathbf u + \mathbf v \text{ is in } V",
    2: r"\mathbf u + \mathbf v = \mathbf v + \mathbf u",
    3: r"(\mathbf u + \mathbf v) + \mathbf w = \mathbf u + (\mathbf v + \mathbf w)",
    4: r"\mathbf u + \mathbf 0 = \mathbf u",
    5: r"\mathbf u + (-\mathbf u) = \mathbf 0",
    6: r"c\,\mathbf u \text{ is in } V",
    7: r"c(\mathbf u + \mathbf v) = c\,\mathbf u + c\,\mathbf v",
    8: r"(c + d)\mathbf u = c\,\mathbf u + d\,\mathbf u",
    9: r"c(d\,\mathbf u) = (cd)\mathbf u",
    10: r"1\mathbf u = \mathbf u",
}
AXIOM_GROUPS = (
    ("Closure", (1, 6)),
    ("A zero and negatives", (4, 5)),
    ("Ordinary algebra", (2, 3, 7, 8, 9, 10)),
)

project = oblique_projector(SPACE_ORIGIN, unit=0.8)


def polynomial(coeffs, scale_by=1.0):
    return lambda t: scale_by * (coeffs[0] + coeffs[1] * t + coeffs[2] * t * t)


def scaled(coeffs, factor):
    return tuple(factor * value for value in coeffs)


def graph_axes():
    axes = Axes(
        x_range=(-0.5, 2.5, 1),
        y_range=(-2.5, 5.5, 1),
        x_length=5.0,
        y_length=4.2,
        tips=False,
        axis_config={"color": Palette.axis, "stroke_width": 2, "tick_size": 0.05},
    )
    axes.move_to(np.array([*GRAPH_CENTER, 0]))
    axes.get_x_axis().add_numbers([1, 2], font_size=26, color=Palette.text_muted)
    axes.get_y_axis().add_numbers([-2, 2, 4], font_size=26, color=Palette.text_muted)
    t_label = MathTex("t", color=Palette.text_muted, font_size=32).next_to(axes.c2p(2.5, 0), UR, buff=0.1)
    return VGroup(axes, t_label)


def curve(axes, coeffs, color, scale_by=1.0, t_range=T_RANGE):
    return axes.plot(polynomial(coeffs, scale_by), x_range=[*t_range, 0.02], color=color, stroke_width=5)


def poly_formula(name, terms, color):
    formula = MathTex(name, "=", *terms, color=color, font_size=38)
    formula[1].set_color(Palette.text)
    return formula


def coefficient_column(coeffs, color):
    return column([str(value) for value in coeffs], color=color).scale(0.72)


def drop_line(coeffs, color):
    floor = (coeffs[0], coeffs[1], 0)
    return DashedLine(project(floor), project(coeffs), color=color, stroke_width=2, stroke_opacity=0.7, dash_length=0.08)


def coefficient_vector(coeffs, color):
    """The arrow for a coefficient list plus a dashed drop to the floor, or a dot when the list is zero."""
    if max(abs(value) for value in coeffs) < 0.03:
        return VGroup(Dot(project((0, 0, 0)), radius=0.09, color=color))
    return VGroup(drop_line(coeffs, color), projected_arrow(project, coeffs, color))


def coefficient_label(coeffs, tex, color, direction):
    return backed(MathTex(tex, color=color, font_size=34), padding=0.08).next_to(project(coeffs), direction, buff=0.12)


VECTOR_LABELS = {
    "p": (P, r"\mathbf p", Palette.yellow, DR),
    "q": (Q, r"\mathbf q", Palette.blue, LEFT),
    "sum": (P_PLUS_Q, r"\mathbf p + \mathbf q", Palette.teal, DOWN),
}


def vector_label(key):
    return coefficient_label(*VECTOR_LABELS[key])


def coefficient_space():
    return projected_axes(project, COEFFICIENT_REACH, labels=("1", "t", "t^2"))


def stems(axes, coeffs, color, times=SAMPLE_TIMES, offset=0.0, base=None):
    """Vertical bars from `base(t)` (default 0) up by the polynomial's value at each sample time."""
    values = polynomial(coeffs)
    lift = base or (lambda t: 0)
    return VGroup(
        *[
            Line(axes.c2p(t + offset, lift(t)), axes.c2p(t + offset, lift(t) + values(t)), color=color, stroke_width=7)
            for t in times
        ]
    )


def axiom_item(number):
    label = Tex(f"{number}.", color=Palette.text_muted, font_size=34)
    body = MathTex(AXIOMS[number], color=Palette.text, font_size=36)
    return VGroup(label, body).arrange(RIGHT, buff=0.2)


def numbered_layout(items):
    """Axioms 1 to 5 down the left and 6 to 10 down the right."""
    targets = {}
    for number, item in items.items():
        column_x = -5.6 if number <= 5 else 0.6
        row = (number - 1) % 5
        spot = item.copy()
        spot.move_to(np.array([column_x, 2.6 - 0.95 * row, 0]), aligned_edge=LEFT)
        targets[number] = spot.get_center()
    return targets


def grouped_layout(items):
    """Each group gets a muted label on the left and its axioms in two columns beside it."""
    targets, labels = {}, VGroup()
    top = 2.9
    for name, numbers in AXIOM_GROUPS:
        label = Tex(name, color=Palette.glow if name == "Closure" else Palette.text_muted, font_size=34)
        label.move_to(np.array([-3.1, top, 0]), aligned_edge=RIGHT)
        labels.add(label)
        for index, number in enumerate(numbers):
            spot = items[number].copy()
            spot.move_to(np.array([-2.7 + 4.6 * (index % 2), top - 0.8 * (index // 2), 0]), aligned_edge=LEFT)
            targets[number] = spot.get_center()
        top -= 0.8 * ((len(numbers) + 1) // 2) + 0.45
    return targets, labels


def function_axes():
    axes = Axes(
        x_range=(0, 4, 1),
        y_range=(0, 6.5, 1),
        x_length=5.2,
        y_length=4.0,
        tips=False,
        axis_config={"color": Palette.axis, "stroke_width": 2, "tick_size": 0.05},
    )
    axes.move_to(np.array([-3.5, -0.2, 0]))
    axes.get_x_axis().add_numbers([1, 2, 3, 4], font_size=26, color=Palette.text_muted)
    axes.get_y_axis().add_numbers([2, 4, 6], font_size=26, color=Palette.text_muted)
    return axes


def function_f(t):
    return 1 + np.sin(2 * t)


def function_g(t):
    return 2 + 0.5 * t


FUNCTION_POINTS = {
    "0": np.array([1.3, -1.9, 0]),
    "f": np.array([4.4, -1.1, 0]),
    "g": np.array([2.1, 0.9, 0]),
}
FUNCTION_POINTS["f+g"] = FUNCTION_POINTS["f"] + FUNCTION_POINTS["g"] - FUNCTION_POINTS["0"]


def function_point(name, color, direction):
    dot = Dot(FUNCTION_POINTS[name], radius=0.1, color=color)
    tex = {"0": r"\mathbf 0", "f": r"\mathbf f", "g": r"\mathbf g", "f+g": r"\mathbf f + \mathbf g"}[name]
    label = MathTex(tex, color=color, font_size=38).next_to(dot, direction, buff=0.15)
    return VGroup(dot, label)


def parallelogram_edges():
    points = FUNCTION_POINTS
    corners = [points["0"], points["f"], points["f+g"], points["g"]]
    return VGroup(
        *[
            DashedLine(corners[i], corners[(i + 1) % 4], color=Palette.text_muted, stroke_width=2, dash_length=0.1)
            for i in range(4)
        ]
    )


def quadrant_shading(plane):
    x_min, x_max = plane.x_range[:2]
    y_min, y_max = plane.y_range[:2]
    corners = [(x_max, y_max), (x_min, y_min)]
    return VGroup(
        *[
            Polygon(
                plane.c2p(0, 0),
                plane.c2p(sx, 0),
                plane.c2p(sx, sy),
                plane.c2p(0, sy),
                stroke_width=0,
                fill_color=Palette.purple_gray,
                fill_opacity=0.16,
            )
            for sx, sy in corners
        ]
    )


def matrix_sum_rows():
    y, b, t = Palette.yellow, Palette.blue, Palette.teal
    first = VGroup(
        matrix([[1, -2], [0, 3]], color=y),
        MathTex("+", color=Palette.text),
        matrix([[4, 1], [-1, 2]], color=b),
        MathTex("=", color=Palette.text),
        matrix([[5, -1], [-1, 5]], color=t),
    ).arrange(RIGHT, buff=0.3)
    second = VGroup(
        matrix([[1, -2], [0, 3]], color=y),
        MathTex("+", color=Palette.text),
        MathTex("(-1)", color=Palette.text),
        matrix([[1, -2], [0, 3]], color=y),
        MathTex("=", color=Palette.text),
        matrix([[0, 0], [0, 0]], color=t),
    ).arrange(RIGHT, buff=0.3)
    return VGroup(first, second).arrange(DOWN, buff=0.7).scale(0.85).move_to(UP * 0.35)


class Lesson(LessonScene):
    day = 10
    title = "What is a vector space?"

    def construct(self):
        plane = make_plane()
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.arrows_recap(plane)
        line = self.polynomial_curves(line)
        line = self.add_polynomials(line)
        line = self.add_arrows(line)
        line = self.scale_both(line)
        line = self.the_rules(line)
        line = self.functions_as_points(line)
        line = self.matrices(line)
        line = self.closure_fails(line)
        self.close_episode(
            r"Anything you can add and scale by the usual rules\\"
            r"is a vector space, and its elements are vectors.",
            *self.mobjects,
        )

    def arrows_recap(self, plane):
        v_arrow = vector_arrow(V, Palette.yellow, plane)
        w_arrow = vector_arrow(W, Palette.blue, plane)
        total = (V[0] + W[0], V[1] + W[1])
        line = self.say(r"On Day 1, vectors were arrows you could add and scale.", hold=0.2)
        self.play(GrowArrow(v_arrow), GrowArrow(w_arrow), run_time=1.2, rate_func=spring_soft)
        moved = arrow_between(plane, V, total, Palette.blue)
        self.play(TransformFromCopy(w_arrow, moved), run_time=1.2, rate_func=spring)
        sum_arrow = vector_arrow(total, Palette.teal, plane)
        self.play(GrowArrow(sum_arrow), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"Span and linear maps used nothing but adding and scaling.", line, hold=Timing.read_short)
        line = self.say(r"So they work for anything else that adds and scales.", line, hold=Timing.read_short)
        line = self.say(r"Today curves will do the same two things.", line, hold=0.2)
        self.play(FadeOut(VGroup(plane, v_arrow, w_arrow, moved, sum_arrow)), run_time=0.8)
        return line

    def polynomial_curves(self, line):
        graph = graph_axes()
        self.graph = graph
        self.axes = graph[0]
        self.space = coefficient_space()
        self.play(Create(graph), Create(self.space), run_time=1.6)

        self.p_formula = poly_formula(r"\mathbf p(t)", ("1", "+", "2t", "-", "t^2"), Palette.yellow)
        self.q_formula = poly_formula(r"\mathbf q(t)", ("2", "-", "t", "+", "t^2"), Palette.blue)
        self.sum_formula = poly_formula(r"(\mathbf p + \mathbf q)(t)", ("3", "+", "t"), Palette.teal)
        formulas = VGroup(self.p_formula, self.q_formula, self.sum_formula).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        formulas.move_to(np.array([-6.6, 3.6, 0]), aligned_edge=UL)

        self.p_curve = curve(self.axes, P, Palette.yellow)
        line = self.say(r"Here is a polynomial, drawn as a curve.", line, hold=0.2)
        self.play(Write(self.p_formula), run_time=1.0)
        self.play(Create(self.p_curve), run_time=1.6, rate_func=smooth)
        self.wait(Timing.read_short)

        self.build_column_row()
        line = self.say(r"Its three coefficients also make an arrow in 3D.", line, hold=0.2)
        self.p_vector = self.fly_coefficients(self.p_formula, self.p_col, P, Palette.yellow, "p")
        self.wait(Timing.read_short)

        self.q_curve = curve(self.axes, Q, Palette.blue)
        line = self.say(r"Here is a second polynomial and its arrow.", line, hold=0.2)
        self.play(Write(self.q_formula), Create(self.q_curve), run_time=1.4)
        self.q_vector = self.fly_coefficients(self.q_formula, self.q_col, Q, Palette.blue, "q")
        self.wait(Timing.read_short)
        return line

    def build_column_row(self):
        self.p_col = coefficient_column(P, Palette.yellow)
        self.q_col = coefficient_column(Q, Palette.blue)
        self.sum_col = coefficient_column(P_PLUS_Q, Palette.teal)
        self.plus_sign = MathTex("+", color=Palette.text, font_size=40)
        self.equals_sign = MathTex("=", color=Palette.text, font_size=40)
        row = VGroup(self.p_col, self.plus_sign, self.q_col, self.equals_sign, self.sum_col).arrange(RIGHT, buff=0.25)
        row.move_to(np.array([6.9, 3.65, 0]), aligned_edge=UR)

    def fly_coefficients(self, formula, col, coeffs, color, key):
        terms = [formula[2], formula[4], VGroup(formula[5], formula[6])]
        self.play(Indicate(VGroup(*terms), color=Palette.glow, scale_factor=1.1), run_time=0.8)
        self.play(
            *[FadeTransform(term.copy(), entry) for term, entry in zip(terms, col.get_entries())],
            FadeIn(col.get_brackets()),
            run_time=1.2,
        )
        vector = coefficient_vector(coeffs, color)
        label = vector_label(key)
        self.play(FadeIn(vector[0]), GrowArrow(vector[1]), run_time=1.2, rate_func=spring_soft)
        self.play(FadeIn(label), run_time=0.4)
        vector.add(label)
        return vector

    def add_polynomials(self, line):
        axes = self.axes
        p_stems = stems(axes, P, Palette.yellow)
        q_stems = stems(axes, Q, Palette.blue, offset=0.1)
        line = self.say(r"Add polynomials by adding their values at every $t$.", line, hold=0.2)
        self.play(Create(p_stems), run_time=1.0)
        self.play(Create(q_stems), run_time=1.0)
        stacked = stems(axes, Q, Palette.blue, base=polynomial(P))
        self.play(Transform(q_stems, stacked), run_time=1.4, rate_func=spring)
        sum_dots = VGroup(*[Dot(axes.c2p(t, polynomial(P_PLUS_Q)(t)), radius=0.08, color=Palette.teal) for t in SAMPLE_TIMES])
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in sum_dots], lag_ratio=0.25), run_time=1.0)
        self.wait(Timing.beat)

        self.sum_curve = curve(axes, P_PLUS_Q, Palette.teal)
        line = self.say(r"The $t^2$ terms cancel, so the sum is $3 + t$.", line, hold=0.2)
        self.play(Create(self.sum_curve), Write(self.sum_formula), run_time=1.6)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(p_stems, q_stems, sum_dots)), run_time=0.6)
        return line

    def add_arrows(self, line):
        line = self.say(r"The arrows add tip to tail and land on the same answer.", line, hold=0.2)
        moved = VGroup(projected_arrow(project, P_PLUS_Q, Palette.blue, start=P))
        self.play(TransformFromCopy(self.q_vector[1], moved[0]), run_time=1.4, rate_func=spring)
        self.sum_vector = coefficient_vector(P_PLUS_Q, Palette.teal)
        self.sum_vector.add(vector_label("sum"))
        self.play(GrowArrow(self.sum_vector[1]), FadeIn(self.sum_vector[0]), FadeIn(self.sum_vector[2]), run_time=1.2, rate_func=spring_soft)
        self.play(FadeIn(self.plus_sign), FadeIn(self.equals_sign), FadeIn(self.sum_col, shift=LEFT * 0.2), run_time=1.0, rate_func=spring)
        self.wait(Timing.read_long)
        self.play(
            FadeOut(VGroup(moved, self.sum_vector, self.sum_curve, self.q_curve, self.q_vector)),
            FadeOut(VGroup(self.q_formula, self.sum_formula, self.p_formula)),
            FadeOut(VGroup(self.plus_sign, self.q_col, self.equals_sign, self.sum_col, self.p_col)),
            run_time=0.8,
        )
        return line

    def scale_both(self, line):
        c = ValueTracker(1.0)
        live_curve = always_redraw(lambda: curve(self.axes, P, Palette.yellow, scale_by=c.get_value()))
        live_vector = always_redraw(lambda: self.scaled_vector(c.get_value()))
        self.remove(self.p_curve, self.p_vector, *self.p_vector)
        self.add(live_curve, live_vector)
        control = backed(slider(r"c", c, Palette.yellow, x_range=(-2, 2, 1), length=2.6), padding=0.2).to_corner(UL, buff=0.45)
        rule = MathTex(r"(c\,\mathbf p)(t) = c\,(1 + 2t - t^2)", color=Palette.yellow, font_size=36)
        rule.next_to(control, DOWN, buff=0.25, aligned_edge=LEFT)
        readout = always_redraw(lambda: self.scaled_readout(c.get_value()))
        line = self.say(r"Scaling works the same way in both pictures.", line, hold=0.2)
        self.play(FadeIn(control), FadeIn(rule), FadeIn(readout), run_time=0.8)
        steps = [
            (2.0, r"Scaling by 2 doubles every value and every coefficient."),
            (-1.0, r"Scaling by $-1$ flips both and gives the negative $-\mathbf p$."),
            (0.0, r"Scaling by 0 flattens both into the zero vector."),
            (1.0, r"Here the zero vector is the zero polynomial."),
        ]
        for target, text in steps:
            line = self.say(text, line, hold=0.1)
            self.play(c.animate.set_value(target), run_time=1.8, rate_func=spring)
            self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(control, rule, readout, live_curve, live_vector, self.graph, self.space)), run_time=0.8)
        return line

    @staticmethod
    def scaled_vector(c_value):
        coeffs = scaled(P, c_value)
        vector = coefficient_vector(coeffs, Palette.yellow)
        direction = DR if c_value >= 0 else UR
        label = backed(MathTex(r"c\,\mathbf p", color=Palette.yellow, font_size=34), padding=0.08)
        return vector.add(label.next_to(project(coeffs), direction, buff=0.12))

    def scaled_readout(self, c_value):
        numbers = [f"{c_value * value + 0.0:.1f}".replace("-0.0", "0.0") for value in P]
        parts = VGroup(
            MathTex(r"c", color=Palette.yellow, font_size=40),
            coefficient_column(P, Palette.yellow),
            MathTex("=", color=Palette.text, font_size=40),
            column(numbers, color=Palette.yellow).scale(0.72),
        ).arrange(RIGHT, buff=0.2)
        return backed(parts, padding=0.18).move_to(np.array([6.9, 3.65, 0]), aligned_edge=UR)

    def the_rules(self, line):
        self.play(*[FadeOut(m) for m in self.mobjects if m is not line], run_time=0.5)
        items = {number: axiom_item(number) for number in AXIOMS}
        for number, spot in numbered_layout(items).items():
            items[number].move_to(spot)
        line = self.say(r"A vector space is any set where these ten rules hold.", line, hold=0.2)
        self.play(LaggedStart(*[FadeIn(items[n], shift=UP * 0.15) for n in AXIOMS], lag_ratio=0.12), run_time=2.4)
        self.wait(Timing.read_short)

        targets, labels = grouped_layout(items)
        line = self.say(r"Two rules say adding and scaling never leave the set.", line, hold=0.2)
        self.play(*[items[n].animate.move_to(targets[n]) for n in AXIOMS], run_time=1.8, rate_func=spring)
        self.play(FadeIn(labels[0], shift=RIGHT * 0.15), Indicate(VGroup(items[1], items[6]), color=Palette.glow, scale_factor=1.05), run_time=1.0)
        self.wait(Timing.read_short)
        line = self.say(r"The others give a zero, negatives and ordinary algebra.", line, hold=0.2)
        self.play(FadeIn(labels[1], shift=RIGHT * 0.15), FadeIn(labels[2], shift=RIGHT * 0.15), run_time=0.8)
        self.wait(Timing.read_short)
        line = self.say(r"Days 11 to 19 rebuild span and independence on these rules.", line, hold=Timing.read_short)
        self.play(FadeOut(VGroup(*items.values(), labels)), run_time=0.7)
        return line

    def functions_as_points(self, line):
        axes = function_axes()
        f_curve = axes.plot(function_f, x_range=[0, 4, 0.02], color=Palette.yellow, stroke_width=5)
        g_curve = axes.plot(function_g, x_range=[0, 4, 0.02], color=Palette.blue, stroke_width=5)
        fg_curve = axes.plot(lambda t: function_f(t) + function_g(t), x_range=[0, 4, 0.02], color=Palette.teal, stroke_width=5)
        formulas = VGroup(
            MathTex(r"\mathbf f(t) = 1 + \sin 2t", color=Palette.yellow, font_size=36),
            MathTex(r"\mathbf g(t) = 2 + 0.5t", color=Palette.blue, font_size=36),
            MathTex(r"(\mathbf f + \mathbf g)(t) = 3 + \sin 2t + 0.5t", color=Palette.teal, font_size=36),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to(np.array([-6.6, 3.55, 0]), aligned_edge=UL)
        line = self.say(r"Functions add the same way, one value of $t$ at a time.", line, hold=0.2)
        self.play(Create(axes), FadeIn(formulas[:2]), run_time=1.2)
        self.play(Create(f_curve), Create(g_curve), run_time=1.6, rate_func=smooth)
        self.wait(Timing.read_short)

        line = self.say(r"Each whole function is one point in a vector space.", line, hold=0.2)
        points = {
            "0": function_point("0", Palette.text, DOWN),
            "f": function_point("f", Palette.yellow, DR),
            "g": function_point("g", Palette.blue, UL),
            "f+g": function_point("f+g", Palette.teal, UR),
        }
        self.play(GrowFromCenter(points["0"]), run_time=0.6, rate_func=spring)
        for name, source in (("f", f_curve), ("g", g_curve)):
            self.play(Transform(source.copy(), points[name][0], remover=True), FadeIn(points[name][1]), run_time=1.3, rate_func=spring_soft)
            self.add(points[name])
        edges = parallelogram_edges()
        self.play(Create(edges), run_time=1.2)
        self.play(GrowFromCenter(points["f+g"]), run_time=0.7, rate_func=spring)
        self.wait(Timing.beat)
        self.play(GrowFromPoint(fg_curve, FUNCTION_POINTS["f+g"]), FadeIn(formulas[2]), run_time=1.6, rate_func=spring_soft)
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(axes, f_curve, g_curve, fg_curve, formulas, edges, *points.values())), run_time=0.7)
        return line

    def matrices(self, line):
        rows = matrix_sum_rows()
        line = self.say(r"2 by 2 matrices form a vector space as well.", line, hold=0.2)
        self.play(FadeIn(rows[0], shift=UP * 0.15), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"Their zero vector is the zero matrix.", line, hold=0.2)
        self.play(FadeIn(rows[1], shift=UP * 0.15), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_long)
        self.play(FadeOut(rows), run_time=0.6)
        return line

    def closure_fails(self, line):
        plane = plane_at(SET_ORIGIN, SET_UNIT)
        shading = quadrant_shading(plane)
        name = backed(MathTex(r"W = \{(x, y) : xy \geq 0\}", color=Palette.purple_gray, font_size=38))
        name.move_to(plane.c2p(4.2, 3.4))
        self.play(Create(plane, lag_ratio=0.02), run_time=1.2)
        line = self.say(r"Now keep only the points with $xy \geq 0$.", line, hold=0.2)
        self.play(FadeIn(shading), FadeIn(name), run_time=1.0)
        self.wait(Timing.beat)
        line = self.say(r"To rule $W$ out, we need one rule it breaks.", line, hold=Timing.read_short)

        u_arrow = vector_arrow(U_SET, Palette.yellow, plane)
        line = self.say(r"Scaling never leaves the shaded set.", line, hold=0.2)
        u_name = backed(MathTex(r"\mathbf u", color=Palette.yellow, font_size=38)).next_to(plane.c2p(*U_SET), UR, buff=0.1)
        self.play(GrowArrow(u_arrow), FadeIn(u_name), run_time=1.0, rate_func=spring_soft)
        ghost = u_arrow.copy().set_opacity(0.3)
        self.add(ghost)
        self.play(Transform(u_arrow, vector_arrow(scaled(U_SET, -1.5), Palette.yellow, plane)), run_time=1.6, rate_func=spring)
        self.play(Transform(u_arrow, vector_arrow(U_SET, Palette.yellow, plane)), run_time=1.2, rate_func=spring)
        self.remove(ghost)
        self.wait(Timing.beat)

        line = self.say(r"But this sum lands outside, so closure fails.", line, hold=0.2)
        self.show_escaping_sum(plane)
        line = self.say(r"One failed rule means $W$ is not a vector space.", line, hold=Timing.read_long)
        return line

    def show_escaping_sum(self, plane):
        total = (U_SET[0] + V_SET[0], U_SET[1] + V_SET[1])
        v_arrow = vector_arrow(V_SET, Palette.blue, plane)
        v_name = backed(MathTex(r"\mathbf v", color=Palette.blue, font_size=38)).next_to(plane.c2p(*V_SET), LEFT, buff=0.15)
        self.play(GrowArrow(v_arrow), FadeIn(v_name), run_time=1.0, rate_func=spring_soft)
        moved = arrow_between(plane, U_SET, total, Palette.blue)
        self.play(TransformFromCopy(v_arrow, moved), run_time=1.4, rate_func=spring)
        sum_arrow = vector_arrow(total, Palette.teal, plane)
        self.play(GrowArrow(sum_arrow), run_time=1.0, rate_func=spring_soft)
        ring = Circle(radius=0.22, color=Palette.glow, stroke_width=4).move_to(plane.c2p(*total))
        label = backed(MathTex(r"\mathbf u + \mathbf v \text{ is not in } W", color=Palette.teal, font_size=36))
        label.next_to(ring, RIGHT, buff=0.2)
        self.play(Create(ring), FadeIn(label), run_time=0.8)
        self.wait(Timing.read_short)


def centerpiece(scene):
    """The polynomial sum on the left and its coefficient arrows adding tip to tail on the right."""
    graph = graph_axes()
    axes = graph[0]
    formulas = VGroup(
        poly_formula(r"\mathbf p(t)", ("1", "+", "2t", "-", "t^2"), Palette.yellow),
        poly_formula(r"\mathbf q(t)", ("2", "-", "t", "+", "t^2"), Palette.blue),
        poly_formula(r"(\mathbf p + \mathbf q)(t)", ("3", "+", "t"), Palette.teal),
    ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
    formulas.move_to(np.array([-6.6, 3.6, 0]), aligned_edge=UL)
    curves = VGroup(curve(axes, P, Palette.yellow), curve(axes, Q, Palette.blue), curve(axes, P_PLUS_Q, Palette.teal))
    row = VGroup(
        coefficient_column(P, Palette.yellow),
        MathTex("+", color=Palette.text, font_size=40),
        coefficient_column(Q, Palette.blue),
        MathTex("=", color=Palette.text, font_size=40),
        coefficient_column(P_PLUS_Q, Palette.teal),
    ).arrange(RIGHT, buff=0.25).move_to(np.array([6.9, 3.65, 0]), aligned_edge=UR)
    vectors = VGroup(
        coefficient_vector(P, Palette.yellow),
        coefficient_vector(Q, Palette.blue),
        projected_arrow(project, P_PLUS_Q, Palette.blue, start=P),
        coefficient_vector(P_PLUS_Q, Palette.teal),
        *[vector_label(key) for key in VECTOR_LABELS],
    )
    scene.add(graph, coefficient_space(), curves, formulas, row, vectors)


class FigPolynomialsAsArrows(Scene):
    def construct(self):
        centerpiece(self)
        fit_to_frame(self)


class FigFunctionsAsPoints(Scene):
    def construct(self):
        axes = function_axes()
        curves = VGroup(
            axes.plot(function_f, x_range=[0, 4, 0.02], color=Palette.yellow, stroke_width=5),
            axes.plot(function_g, x_range=[0, 4, 0.02], color=Palette.blue, stroke_width=5),
            axes.plot(lambda t: function_f(t) + function_g(t), x_range=[0, 4, 0.02], color=Palette.teal, stroke_width=5),
        )
        points = VGroup(
            function_point("0", Palette.text, DOWN),
            function_point("f", Palette.yellow, DR),
            function_point("g", Palette.blue, UL),
            function_point("f+g", Palette.teal, UR),
        )
        self.add(axes, curves, parallelogram_edges(), points)
        fit_to_frame(self)


class FigClosureFails(Scene):
    def construct(self):
        plane = make_plane(x_range=(-4, 5, 1), y_range=(-4, 3, 1))
        total = (U_SET[0] + V_SET[0], U_SET[1] + V_SET[1])
        ring = Circle(radius=0.22, color=Palette.glow, stroke_width=4).move_to(plane.c2p(*total))
        labels = VGroup(
            backed(MathTex(r"\mathbf u", color=Palette.yellow)).next_to(plane.c2p(*U_SET), UR, buff=0.1),
            backed(MathTex(r"\mathbf v", color=Palette.blue)).next_to(plane.c2p(*V_SET), LEFT, buff=0.15),
            backed(MathTex(r"\mathbf u + \mathbf v", color=Palette.teal)).next_to(ring, RIGHT, buff=0.15),
        )
        self.add(
            plane,
            quadrant_shading(plane),
            vector_arrow(U_SET, Palette.yellow, plane),
            vector_arrow(V_SET, Palette.blue, plane),
            arrow_between(plane, U_SET, total, Palette.blue),
            vector_arrow(total, Palette.teal, plane),
            ring,
            labels,
        )
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        centerpiece(self)
