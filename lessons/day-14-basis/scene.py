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
    equation_line,
    fit_to_frame,
    make_plane,
    plane_at,
    plate_for,
    skewed_grid,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (-2.6, -2.2)
PLANE_UNIT = 0.88
X = (1, 5)
E1, E2 = (1, 0), (0, 1)
B1, B2 = (2, 1), (-1, 1)
C1, C2 = (3, 1), (-1, 2)
U = (1, 2)
RECIPES = ((2, 3, 0), (1, 2, 1), (0, 1, 2))
POLY_P = (1, 2, -1)

BASES = {
    "e": {"vectors": (E1, E2), "colors": (Palette.i_hat, Palette.j_hat), "names": (r"\mathbf e_1", r"\mathbf e_2"), "address": (1, 5)},
    "b": {"vectors": (B1, B2), "colors": (Palette.yellow, Palette.blue), "names": (r"\mathbf b_1", r"\mathbf b_2"), "address": (2, 3)},
    "c": {"vectors": (C1, C2), "colors": (Palette.pink, Palette.purple_gray), "names": (r"\mathbf c_1", r"\mathbf c_2"), "address": (1, 2)},
}
LABEL_SIDES = {"e": (DOWN, LEFT), "b": (DR, DL), "c": (DR, LEFT)}


def plus(p, q, weight=1.0):
    return (p[0] + weight * q[0], p[1] + weight * q[1])


def name_label(tex, color, point, direction, font_size=38):
    return backed(MathTex(tex, color=color, font_size=font_size), padding=0.08).next_to(point, direction, buff=0.12)


def light(on: bool) -> VGroup:
    ring = Circle(radius=0.15, stroke_color=Palette.teal if on else Palette.text_muted, stroke_width=3)
    core = Dot(radius=0.1, color=Palette.teal, fill_opacity=1 if on else 0)
    return VGroup(ring, core)


class Checklist:
    """Two lights, one for each test a basis must pass."""

    def __init__(self):
        self.lights = [light(False), light(False)]
        labels = [Tex(r"Spans $\mathbb{R}^2$", color=Palette.text, font_size=36), Tex("Independent", color=Palette.text, font_size=36)]
        rows = VGroup(*[VGroup(lamp, label).arrange(RIGHT, buff=0.3) for lamp, label in zip(self.lights, labels)])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_corner(UR, buff=0.6)
        self.state = [False, False]
        self.group = VGroup(plate_for(rows), rows)

    def switch(self, spans: bool, independent: bool) -> list:
        changes = []
        for index, wanted in enumerate((spans, independent)):
            if self.state[index] != wanted:
                lamp = self.lights[index]
                changes.append(Transform(lamp, light(wanted).move_to(lamp)))
                self.state[index] = wanted
        return changes


def recipe_tex(weights, names, colors):
    tokens = [r"\mathbf x", "="]
    for index, weight in enumerate(weights):
        tokens += (["+"] if index else []) + [str(weight), names[index]]
    formula = MathTex(*tokens, color=Palette.text, font_size=38)
    for index, color in enumerate(colors):
        offset = 2 + 3 * index
        formula[offset].set_color(color)
        formula[offset + 1].set_color(color)
    return formula


def walk_path(plane, weights, vectors, colors, stroke_width=5):
    """Tip-to-tail arrows that follow a recipe of weights, skipping zero weights."""
    path, start = VGroup(), (0, 0)
    for weight, vector, color in zip(weights, vectors, colors):
        if weight == 0:
            continue
        end = plus(start, vector, weight)
        path.add(arrow_between(plane, start, end, color, stroke_width=stroke_width))
        start = end
    return path


def step_walk(plane, weights, vectors, colors):
    """Dashed legs with a dot at every whole step, so the weights can be counted."""
    legs, start = VGroup(), (0, 0)
    for weight, vector, color in zip(weights, vectors, colors):
        end = plus(start, vector, weight)
        dashes = DashedLine(plane.c2p(*start), plane.c2p(*end), color=color, stroke_width=4, dash_length=0.12)
        steps = VGroup(*[Dot(plane.c2p(*plus(start, vector, k * np.sign(weight))), radius=0.07, color=color) for k in range(1, abs(weight) + 1)]) if weight else VGroup()
        legs.add(VGroup(dashes, steps))
        start = end
    return legs


def point_x(plane):
    dot = Dot(plane.c2p(*X), radius=0.11, color=Palette.teal)
    label = name_label(r"\mathbf x", Palette.teal, plane.c2p(*X), UL)
    return VGroup(dot, label)


def basis_arrows(plane, key):
    basis = BASES[key]
    arrows = VGroup(*[vector_arrow(v, c, plane) for v, c in zip(basis["vectors"], basis["colors"])])
    labels = VGroup(
        *[
            name_label(name, color, plane.c2p(*vector), side)
            for name, color, vector, side in zip(basis["names"], basis["colors"], basis["vectors"], LABEL_SIDES[key])
        ]
    )
    return arrows, labels


def address_row(key):
    basis = BASES[key]
    return recipe_tex(basis["address"], basis["names"], basis["colors"])


class Morph:
    """A basis that springs from one pair of arrows to another, carrying its grid and colors along."""

    def __init__(self, key):
        self.start = self.end = key
        self.progress = ValueTracker(1)

    def _mix(self, first, second):
        s = self.progress.get_value()
        return (first[0] + s * (second[0] - first[0]), first[1] + s * (second[1] - first[1]))

    def vector(self, index):
        return self._mix(BASES[self.start]["vectors"][index], BASES[self.end]["vectors"][index])

    def color(self, index):
        s = min(max(self.progress.get_value(), 0), 1)
        return interpolate_color(ManimColor(BASES[self.start]["colors"][index]), ManimColor(BASES[self.end]["colors"][index]), s)

    def to(self, key):
        self.start, self.end = self.end, key
        self.progress.set_value(0)
        return self.progress.animate.set_value(1)


def polynomial_axes():
    axes = Axes(
        x_range=(-0.5, 2.5, 1),
        y_range=(-2.5, 4.5, 1),
        x_length=5.6,
        y_length=5.0,
        tips=False,
        axis_config={"color": Palette.axis, "stroke_width": 2, "tick_size": 0.05},
    )
    axes.move_to(np.array([-3.4, 0.4, 0]))
    axes.get_x_axis().add_numbers([1, 2], font_size=26, color=Palette.text_muted)
    axes.get_y_axis().add_numbers([-2, 2, 4], font_size=26, color=Palette.text_muted)
    t_label = MathTex("t", color=Palette.text_muted, font_size=32).next_to(axes.c2p(2.5, 0), UR, buff=0.1)
    return VGroup(axes, t_label)


def quadratic(axes, weights, color, stroke_width=5):
    c0, c1, c2 = weights
    return axes.plot(lambda t: c0 + c1 * t + c2 * t * t, x_range=[-0.3, 2.3, 0.02], color=color, stroke_width=stroke_width)


POWER_CURVES = (
    ((1, 0, 0), Palette.i_hat, "1", 2.3),
    ((0, 1, 0), Palette.j_hat, "t", 2.3),
    ((0, 0, 1), Palette.pink, "t^2", 2.0),
)


def power_curves(axes):
    curves = VGroup()
    for weights, color, tex, t_end in POWER_CURVES:
        curve = axes.plot(lambda t, w=weights: w[0] + w[1] * t + w[2] * t * t, x_range=[-0.3, t_end, 0.02], color=color, stroke_width=4)
        label = name_label(tex, color, curve.get_end(), RIGHT, font_size=36)
        curves.add(VGroup(curve, label))
    return curves


def weight_column(values):
    entries = [f"{value + 0.0:.1f}".replace("-0.0", "0.0") for value in values]
    col = column(entries).scale(0.8)
    for entry, color in zip(col.get_entries(), (Palette.i_hat, Palette.j_hat, Palette.pink)):
        entry.set_color(color)
    return col


class Lesson(LessonScene):
    day = 14
    title = "Basis"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        self.plane = plane
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.standard_basis()
        line = self.two_tests(line)
        line = self.many_recipes(line)
        line = self.trim_to_basis(line)
        line = self.one_address_each(line)
        line = self.polynomial_basis(line)
        self.close_episode(
            r"A basis spans the space with no spare vectors,\\"
            r"so every vector has exactly one address.",
            *self.mobjects,
        )

    def standard_basis(self):
        plane = self.plane
        arrows, labels = basis_arrows(plane, "e")
        line = self.say(r"The usual grid is built from two arrows, $\mathbf e_1$ and $\mathbf e_2$.", hold=0.2)
        self.play(*[GrowArrow(a) for a in arrows], run_time=1.2, rate_func=spring_soft)
        self.play(FadeIn(labels), run_time=0.5)
        self.wait(Timing.beat)

        self.x_point = point_x(plane)
        line = self.say(r"This point is 1 step of $\mathbf e_1$ plus 5 of $\mathbf e_2$.", line, hold=0.2)
        self.play(GrowFromCenter(self.x_point[0]), FadeIn(self.x_point[1]), run_time=0.7, rate_func=spring)
        walk = step_walk(plane, (1, 5), (E1, E2), (Palette.i_hat, Palette.j_hat))
        for leg in walk:
            self.play(Create(leg[0]), LaggedStart(*[GrowFromCenter(d) for d in leg[1]], lag_ratio=0.3), run_time=1.2)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(arrows, labels, walk)), run_time=0.6)
        return line

    def two_tests(self, line):
        plane = self.plane
        self.checklist = Checklist()
        line = self.say(r"A basis must pass two tests at once.", line, hold=0.2)
        self.play(FadeIn(self.checklist.group, shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)

        self.set_arrows, self.set_labels = basis_arrows(plane, "b")
        self.span_line = equation_line(plane, (B1[1], -B1[0], 0), color=Palette.teal, stroke_width=4)
        line = self.say(r"One arrow is independent, but it only spans a line.", line, hold=0.2)
        self.play(GrowArrow(self.set_arrows[0]), FadeIn(self.set_labels[0]), run_time=1.0, rate_func=spring_soft)
        self.play(Create(self.span_line), *self.checklist.switch(False, True), run_time=1.2)
        self.wait(Timing.read_short)

        self.span_grid = skewed_grid(plane, B1, B2, reach=14, color=Palette.teal, opacity=0.45)
        line = self.say(r"Two arrows in different directions pass both tests.", line, hold=0.2)
        self.play(GrowArrow(self.set_arrows[1]), FadeIn(self.set_labels[1]), run_time=1.0, rate_func=spring_soft)
        self.play(Create(self.span_grid, lag_ratio=0.01), FadeOut(self.span_line), *self.checklist.switch(True, True), run_time=1.6)
        self.bring_to_front(self.set_arrows, self.set_labels, self.x_point)
        self.wait(Timing.read_short)
        return line

    def many_recipes(self, line):
        plane = self.plane
        self.u_arrow = vector_arrow(U, Palette.pink, plane)
        self.u_label = name_label(r"\mathbf u", Palette.pink, plane.c2p(*U), UR)
        parallelogram = VGroup(
            DashedLine(plane.c2p(*B1), plane.c2p(*U), color=Palette.blue, stroke_width=3),
            DashedLine(plane.c2p(*B2), plane.c2p(*U), color=Palette.yellow, stroke_width=3),
        )
        line = self.say(r"A third arrow adds nothing new, so the set is dependent.", line, hold=0.2)
        self.play(GrowArrow(self.u_arrow), FadeIn(self.u_label), run_time=1.0, rate_func=spring_soft)
        self.play(Create(parallelogram), *self.checklist.switch(True, False), run_time=1.2)
        self.wait(Timing.read_short)
        self.play(FadeOut(parallelogram), run_time=0.4)

        names = (r"\mathbf b_1", r"\mathbf b_2", r"\mathbf u")
        colors = (Palette.yellow, Palette.blue, Palette.pink)
        rows = VGroup(*[recipe_tex(weights, names, colors) for weights in RECIPES]).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        rows.next_to(self.checklist.group, DOWN, buff=0.4).align_to(self.checklist.group, RIGHT).shift(LEFT * 0.25)
        for row in rows:
            backed(row, padding=0.12)
        line = self.say(r"With a spare arrow, $\mathbf x$ has many recipes.", line, hold=0.2)
        path = None
        for weights, row in zip(RECIPES, rows):
            new_path = walk_path(plane, weights, (B1, B2, U), colors)
            fade = [FadeOut(path)] if path is not None else []
            self.play(*fade, FadeIn(row, shift=LEFT * 0.15), LaggedStart(*[GrowArrow(a) for a in new_path], lag_ratio=0.6), run_time=1.8)
            self.wait(Timing.beat)
            path = new_path
        line = self.say(r"So the weights no longer give $\mathbf x$ one address.", line, hold=Timing.read_short)
        self.recipe_rows, self.recipe_path = rows, path
        return line

    def trim_to_basis(self, line):
        plane = self.plane
        line = self.say(r"Drop the spare arrow and the span does not shrink.", line, hold=0.2)
        self.play(FadeOut(VGroup(self.u_arrow, self.u_label, self.recipe_path, self.recipe_rows)), run_time=0.8)
        self.play(*self.checklist.switch(True, True), run_time=0.8)
        self.wait(Timing.read_short)

        line = self.say(r"Drop one more and the span shrinks to a line.", line, hold=0.2)
        self.play(FadeOut(self.set_arrows[1]), FadeOut(self.set_labels[1]), run_time=0.6)
        self.play(FadeOut(self.span_grid), FadeIn(self.span_line), *self.checklist.switch(False, True), run_time=1.2)
        miss = Circle(radius=0.26, color=Palette.glow, stroke_width=4).move_to(plane.c2p(*X))
        self.play(Create(miss), run_time=0.6)
        self.wait(Timing.read_short)

        line = self.say(r"A basis is a spanning set with nothing left to drop.", line, hold=0.2)
        self.play(FadeOut(miss), FadeOut(self.span_line), FadeIn(self.span_grid), GrowArrow(self.set_arrows[1]), FadeIn(self.set_labels[1]), *self.checklist.switch(True, True), run_time=1.2)
        self.bring_to_front(self.set_arrows, self.set_labels, self.x_point)
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(self.span_grid, self.set_arrows, self.set_labels, self.checklist.group)), run_time=0.7)
        return line

    def start_morph(self):
        plane = self.plane
        self.morph = Morph("e")
        morph = self.morph
        self.live_grid = always_redraw(lambda: skewed_grid(plane, morph.vector(0), morph.vector(1), reach=14, color=Palette.grid, opacity=0.95))
        self.live_arrows = VGroup(
            always_redraw(lambda: vector_arrow(morph.vector(0), morph.color(0), plane)),
            always_redraw(lambda: vector_arrow(morph.vector(1), morph.color(1), plane)),
        )
        self.play(plane.animate.set_stroke(opacity=0.18), FadeIn(self.live_grid), run_time=1.0)
        self.play(*[GrowArrow(a) for a in self.live_arrows], run_time=1.0, rate_func=spring_soft)
        self.bring_to_front(self.x_point)

    def read_address(self, key, row, *extra):
        basis = BASES[key]
        _, labels = basis_arrows(self.plane, key)
        walk = step_walk(self.plane, basis["address"], basis["vectors"], basis["colors"])
        self.play(FadeIn(labels), run_time=0.4)
        for leg in walk:
            self.play(Create(leg[0]), LaggedStart(*[GrowFromCenter(d) for d in leg[1]], lag_ratio=0.3), run_time=1.2)
        self.bring_to_front(self.x_point)
        self.play(*extra, FadeIn(row, shift=LEFT * 0.15), run_time=0.7, rate_func=spring_soft)
        return VGroup(labels, walk)

    def one_address_each(self, line):
        rows = VGroup(*[address_row(key) for key in "ebc"]).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_corner(UR, buff=0.6)
        for row in rows:
            backed(row, padding=0.12)
        line = self.say(r"Now read the address of $\mathbf x$ in each basis.", line, hold=0.2)
        self.start_morph()
        marks = self.read_address("e", rows[0])
        self.wait(Timing.beat)

        line = self.say(r"Skew the grid to match $\mathbf b_1$ and $\mathbf b_2$.", line, hold=0.2)
        self.play(FadeOut(marks), run_time=0.5)
        self.play(self.morph.to("b"), run_time=2.6, rate_func=spring_soft)
        line = self.say(r"Now $\mathbf x$ is 2 steps of $\mathbf b_1$ plus 3 of $\mathbf b_2$.", line, hold=0.2)
        marks = self.read_address("b", rows[1])
        self.wait(Timing.read_short)

        line = self.say(r"A different basis gives a different grid and address.", line, hold=0.2)
        self.play(FadeOut(marks), run_time=0.5)
        self.play(self.morph.to("c"), run_time=2.6, rate_func=spring_soft)
        marks = self.read_address("c", rows[2])
        self.wait(Timing.read_short)

        line = self.say(r"Each basis gives $\mathbf x$ exactly one address.", line, hold=0.2)
        for row in rows:
            self.play(Indicate(row, color=Palette.glow, scale_factor=1.06), run_time=0.8)
        self.play(Indicate(self.x_point[0], color=Palette.glow, scale_factor=1.6), run_time=0.8)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(marks, rows, self.live_grid, self.live_arrows, self.x_point, self.plane)), run_time=0.8)
        return line

    def polynomial_basis(self, line):
        graph = polynomial_axes()
        axes = graph[0]
        curves = power_curves(axes)
        line = self.say(r"In $\mathbb P_2$ the standard basis is $1$, $t$ and $t^2$.", line, hold=0.2)
        self.play(Create(graph), run_time=1.0)
        self.play(LaggedStart(*[Create(c[0]) for c in curves], lag_ratio=0.4), LaggedStart(*[FadeIn(c[1]) for c in curves], lag_ratio=0.4), run_time=2.0)
        self.wait(Timing.read_short)

        formula = MathTex(r"\mathbf p(t)", "=", "1", r"\cdot 1", "+", "2", r"\cdot t", "+", "(-1)", r"\cdot t^2", color=Palette.yellow, font_size=40)
        for index, color in ((2, Palette.i_hat), (5, Palette.j_hat), (8, Palette.pink)):
            formula[index].set_color(color)
        formula.move_to(np.array([3.4, 2.6, 0]))
        address = column(["1", "2", "-1"]).scale(0.8)
        for entry, color in zip(address.get_entries(), (Palette.i_hat, Palette.j_hat, Palette.pink)):
            entry.set_color(color)
        address.next_to(formula, DOWN, buff=0.6)
        p_curve = quadratic(axes, POLY_P, Palette.yellow)
        line = self.say(r"In this basis, a polynomial's address is its coefficient list.", line, hold=0.2)
        dim = [c[0].animate.set_stroke(opacity=0.3) for c in curves] + [c[1].animate.set_opacity(0.35) for c in curves]
        self.play(*dim, Create(p_curve), Write(formula), run_time=1.6)
        self.play(
            *[FadeTransform(formula[i].copy(), entry) for i, entry in zip((2, 5, 8), address.get_entries())],
            FadeIn(address.get_brackets()),
            run_time=1.2,
        )
        self.remove(*address.get_entries(), address.get_brackets())
        self.add(address)
        self.wait(Timing.read_short)
        self.only_zero_is_flat(axes, p_curve, VGroup(formula, address), line)
        return line

    def only_zero_is_flat(self, axes, p_curve, readout, line):
        weights = [ValueTracker(float(w)) for w in POLY_P]
        values = lambda: [w.get_value() for w in weights]  # noqa: E731
        live_curve = always_redraw(lambda: quadratic(axes, values(), Palette.yellow))
        live_column = always_redraw(lambda: weight_column(values()).move_to(readout[1]))
        self.remove(p_curve, readout[1])
        self.add(live_curve, live_column)
        self.play(FadeOut(readout[0]), run_time=0.4)

        line = self.say(r"A nonzero quadratic is zero at two values of $t$ at most.", line, hold=0.2)
        self.play(weights[0].animate.set_value(0), run_time=1.6, rate_func=spring)
        roots = VGroup(*[Dot(axes.c2p(t, 0), radius=0.09, color=Palette.glow) for t in (0, 2)])
        self.play(LaggedStart(*[GrowFromCenter(r) for r in roots], lag_ratio=0.4), run_time=0.8)
        self.wait(Timing.read_short)

        line = self.say(r"So only zero weights give the zero polynomial.", line, hold=0.2)
        self.play(FadeOut(roots), *[w.animate.set_value(0) for w in weights[1:]], run_time=2.0, rate_func=spring)
        self.play(Indicate(live_column, color=Palette.glow, scale_factor=1.1), run_time=0.9)
        self.wait(Timing.read_long)
        return line


def two_grid_panel(key):
    plane = make_plane(x_range=(-3, 5, 1), y_range=(-1, 6, 1))
    basis = BASES[key]
    grid = skewed_grid(plane, *basis["vectors"], reach=12, color=Palette.grid, opacity=0.95, box=((-3, 5), (-1, 6)))
    plane.set_stroke(opacity=0.18)
    arrows, labels = basis_arrows(plane, key)
    walk = step_walk(plane, basis["address"], basis["vectors"], basis["colors"])
    row = backed(address_row(key), padding=0.15).next_to(plane, DOWN, buff=0.3)
    return VGroup(plane, grid, walk, arrows, labels, point_x(plane), row)


class FigSameGrids(Scene):
    def construct(self):
        panels = VGroup(two_grid_panel("e"), two_grid_panel("b")).arrange(RIGHT, buff=0.8)
        self.add(panels)
        fit_to_frame(self)


def three_sets_panel(vectors, colors, names, spans_plane):
    box = ((-3, 4), (-2, 4))
    plane = make_plane(x_range=(-3, 4, 1), y_range=(-2, 4, 1))
    if spans_plane:
        span = skewed_grid(plane, B1, B2, reach=12, color=Palette.teal, opacity=0.45, box=box)
    else:
        span = equation_line(plane, (B1[1], -B1[0], 0), color=Palette.teal, stroke_width=4)
    arrows = VGroup(*[vector_arrow(v, c, plane) for v, c in zip(vectors, colors)])
    labels = VGroup(*[name_label(n, c, plane.c2p(*v), UR if v == U else DR if v == B1 else UL) for v, c, n in zip(vectors, colors, names)])
    return VGroup(plane, span, arrows, labels)


class FigThreeSets(Scene):
    def construct(self):
        names = (r"\mathbf b_1", r"\mathbf b_2", r"\mathbf u")
        vectors = (B1, B2, U)
        colors = (Palette.yellow, Palette.blue, Palette.pink)
        panels = VGroup(
            three_sets_panel(vectors[:1], colors[:1], names[:1], False),
            three_sets_panel(vectors[:2], colors[:2], names[:2], True),
            three_sets_panel(vectors, colors, names, True),
        ).arrange(RIGHT, buff=0.6)
        self.add(panels)
        fit_to_frame(self)


class FigPolynomialBasis(Scene):
    def construct(self):
        graph = polynomial_axes()
        axes = graph[0]
        curves = power_curves(axes)
        p_curve = quadratic(axes, POLY_P, Palette.yellow)
        p_label = backed(MathTex(r"\mathbf p(t) = 1 + 2t - t^2", color=Palette.yellow, font_size=36), padding=0.08).move_to(axes.c2p(0.6, 3.3))
        self.add(graph, curves, p_curve, p_label)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        plane.set_stroke(opacity=0.22)
        grid = skewed_grid(plane, B1, B2, reach=14, color=Palette.grid, opacity=0.95)
        arrows, labels = basis_arrows(plane, "b")
        standard = step_walk(plane, (1, 5), (E1, E2), (Palette.i_hat, Palette.j_hat))
        skewed = step_walk(plane, (2, 3), (B1, B2), (Palette.yellow, Palette.blue))
        rows = VGroup(address_row("e"), address_row("b")).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_corner(UR, buff=0.6)
        self.add(plane, grid, standard.set_opacity(0.55), skewed, arrows, labels, point_x(plane), plate_for(rows), rows)
