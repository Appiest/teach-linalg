import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    Palette,
    Timing,
    arrow_between,
    augmented,
    backed,
    column,
    fit_to_frame,
    matrix,
    morph_matrix,
    oblique_projector,
    plane_at,
    projected_arrow,
    projected_axes,
    skewed_grid,
    spring,
    spring_soft,
    vector_arrow,
)

B1 = (2, 1)
B2 = (-1, 2)
X = (3, 4)
X_COORDS = (2, 1)
W_VEC = (3, -1)
C1 = (1, 1)
C2 = (-1, 1)
PLANE_ORIGIN = (-3.4, -1.6)
PLANE_UNIT = 0.85

P = (2, -1, 3)
Q = (1, 4, -1)
P_PLUS_Q = (3, 3, 2)
T_RANGE = (-1, 1)
GRAPH_CENTER = (-3.7, -0.75)
SPACE_ORIGIN = (1.2, -0.6)
COEFFICIENT_REACH = ((-1, 3), (-2, 4), (-1, 3))
MAP_Y = 2.95

project = oblique_projector(SPACE_ORIGIN, unit=0.85, azimuth=-PI / 9)
subspace_view = oblique_projector((-3.3, -0.5), unit=1.35)

LINE_DIRECTION = (0.6, 1.4, 1.0)
PLANE_SPAN = ((1.2, 0.0, 0.5), (0.0, 1.4, 0.7))
THIRD_DIRECTION = (0.4, -0.6, 1.5)

POLYNOMIALS = {
    "p": (r"\mathbf p(t)", ("2", "-", "t", "+", "3t^2"), Palette.yellow, ((2,), (3, 4), (6,))),
    "q": (r"\mathbf q(t)", ("1", "+", "4t", "-", "t^2"), Palette.blue, ((2,), (4,), (5, 6))),
    "sum": (r"(\mathbf p + \mathbf q)(t)", ("3", "+", "3t", "+", "2t^2"), Palette.teal, ((2,), (4,), (6,))),
}
COEFFICIENTS = {"p": P, "q": Q, "sum": P_PLUS_Q}
ARROW_LABELS = {
    "p": (r"\mathbf p", DL),
    "q": (r"\mathbf q", RIGHT),
    "sum": (r"\mathbf p + \mathbf q", UR),
}

DIMENSION_TABLE = (
    (r"\mathbb R^2", r"\mathbf e_1,\ \mathbf e_2", "2"),
    (r"\mathbb R^n", r"\mathbf e_1,\ \dots,\ \mathbf e_n", "n"),
    (r"\mathbb P_2", r"1,\ t,\ t^2", "3"),
    (r"\mathbb P_n", r"1,\ t,\ \dots,\ t^n", "n + 1"),
)
SUBSPACE_ROWS = (
    ("0", r"the origin"),
    ("1", r"lines through the origin"),
    ("2", r"planes through the origin"),
    ("3", r"all of $\mathbb R^3$"),
)


def tex(*parts, colors=(), font_size=44):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def basis_column(entries, colors=(Palette.i_hat, Palette.j_hat)):
    col = column([str(value) for value in entries])
    for entry, color in zip(col.get_entries(), colors):
        entry.set_color(color)
    return col


def basis_matrix(first, second):
    mat = matrix([[first[0], second[0]], [first[1], second[1]]])
    columns = mat.get_columns()
    columns[0].set_color(Palette.i_hat)
    columns[1].set_color(Palette.j_hat)
    return mat


def basis_pair(plane, first, second, names=(r"\mathbf b_1", r"\mathbf b_2")):
    """The two basis arrows in green and red, each with a backed label past its tip."""
    arrows = VGroup(vector_arrow(first, Palette.i_hat, plane), vector_arrow(second, Palette.j_hat, plane))
    labels = VGroup(
        backed(MathTex(names[0], color=Palette.i_hat, font_size=40), padding=0.08).next_to(plane.c2p(*first), DR, buff=0.08),
        backed(MathTex(names[1], color=Palette.j_hat, font_size=40), padding=0.08).next_to(plane.c2p(*second), LEFT, buff=0.12),
    )
    return arrows, labels


def basis_grid(plane, first, second):
    return skewed_grid(plane, first, second, reach=14, color=Palette.purple_gray, opacity=0.6)


def coordinate_walk(plane):
    """Two steps of b1 and one of b2, tip to tail, ending at x."""
    twice = (2 * B1[0], 2 * B1[1])
    return VGroup(
        arrow_between(plane, B1, twice, Palette.i_hat, stroke_width=5),
        arrow_between(plane, twice, X, Palette.j_hat, stroke_width=5),
    )


def x_label(plane):
    return backed(MathTex(r"\mathbf x", color=Palette.yellow, font_size=40), padding=0.08).next_to(plane.c2p(*X), UL, buff=0.08)


def coordinate_vector_row():
    return VGroup(MathTex(r"[\mathbf x]_{\mathcal B}", "=", color=Palette.yellow, font_size=44), basis_column(X_COORDS)).arrange(RIGHT, buff=0.2)


def change_of_coordinates_row():
    product = VGroup(
        MathTex(r"P_{\mathcal B}", color=Palette.text, font_size=44),
        basis_matrix(B1, B2),
        basis_column(X_COORDS),
        MathTex("=", color=Palette.text, font_size=44),
        column([str(value) for value in X], color=Palette.yellow),
    ).arrange(RIGHT, buff=0.26)
    return product


def polynomial(coeffs):
    return lambda t: coeffs[0] + coeffs[1] * t + coeffs[2] * t * t


def graph_axes():
    axes = Axes(
        x_range=(-1.2, 1.2, 1),
        y_range=(-5, 9, 2),
        x_length=4.6,
        y_length=4.3,
        tips=False,
        axis_config={"color": Palette.axis, "stroke_width": 2, "tick_size": 0.05},
    )
    axes.move_to(np.array([*GRAPH_CENTER, 0]))
    axes.get_x_axis().add_numbers([-1, 1], font_size=26, color=Palette.text_muted)
    axes.get_y_axis().add_numbers([-4, 4, 8], font_size=26, color=Palette.text_muted)
    t_label = MathTex("t", color=Palette.text_muted, font_size=32).next_to(axes.c2p(1.2, 0), UR, buff=0.1)
    return VGroup(axes, t_label)


def curve(axes, coeffs, color):
    return axes.plot(polynomial(coeffs), x_range=[*T_RANGE, 0.02], color=color, stroke_width=5)


def poly_formula(key):
    name, terms, color, _ = POLYNOMIALS[key]
    formula = MathTex(name, "=", *terms, color=color, font_size=38)
    formula[1].set_color(Palette.text)
    return formula


def coefficient_terms(formula, key):
    groups = POLYNOMIALS[key][3]
    return [VGroup(*[formula[index] for index in group]) for group in groups]


def formula_stack():
    formulas = {key: poly_formula(key) for key in POLYNOMIALS}
    VGroup(*formulas.values()).arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to(np.array([-6.6, 3.6, 0]), aligned_edge=UL)
    return formulas


def coefficient_column(key):
    color = POLYNOMIALS[key][2]
    return column([str(value) for value in COEFFICIENTS[key]], color=color).scale(0.72)


def column_row():
    parts = {
        "p": coefficient_column("p"),
        "plus": MathTex("+", color=Palette.text, font_size=40),
        "q": coefficient_column("q"),
        "equals": MathTex("=", color=Palette.text, font_size=40),
        "sum": coefficient_column("sum"),
    }
    VGroup(*parts.values()).arrange(RIGHT, buff=0.25).move_to(np.array([6.9, 3.65, 0]), aligned_edge=UR)
    return parts


def map_arrow(columns):
    end = np.array([columns["p"].get_left()[0] - 0.3, MAP_Y, 0])
    return Arrow(np.array([-2.7, MAP_Y, 0]), end, buff=0, color=Palette.text_muted, stroke_width=4, max_tip_length_to_length_ratio=0.06)


def map_label(arrow, tex_string):
    return MathTex(tex_string, color=Palette.text, font_size=34).next_to(arrow, UP, buff=0.12)


def coefficient_space():
    return projected_axes(project, COEFFICIENT_REACH, labels=("1", "t", "t^2"))


def coefficient_vector(key, start=(0, 0, 0), color=None):
    coeffs = COEFFICIENTS[key]
    color = color or POLYNOMIALS[key][2]
    floor = (coeffs[0], coeffs[1], 0)
    drop = DashedLine(project(floor), project(coeffs), color=color, stroke_width=2, stroke_opacity=0.7, dash_length=0.08)
    return VGroup(drop, projected_arrow(project, coeffs, color, start=start))


def coefficient_label(key):
    tex_string, direction = ARROW_LABELS[key]
    color = POLYNOMIALS[key][2]
    return backed(MathTex(tex_string, color=color, font_size=34), padding=0.08).next_to(project(COEFFICIENTS[key]), direction, buff=0.12)


def dimension_table():
    header = VGroup(*[Tex(text, color=Palette.text_muted, font_size=34) for text in ("Space", "A basis", "Dimension")])
    rows = [header] + [
        VGroup(
            MathTex(space, color=Palette.text, font_size=46),
            MathTex(basis, color=Palette.text, font_size=42),
            MathTex(size, color=Palette.teal, font_size=46),
        )
        for space, basis, size in DIMENSION_TABLE
    ]
    for row_index, row in enumerate(rows):
        for x_center, cell in zip((-4.2, 0.0, 4.2), row):
            cell.move_to(np.array([x_center, 2.9 - 1.1 * row_index, 0]))
    return VGroup(*rows)


def subspace_rows():
    rows = VGroup()
    for index, (size, words) in enumerate(SUBSPACE_ROWS):
        number = MathTex(size, color=Palette.teal, font_size=52)
        description = Tex(words, color=Palette.text, font_size=36)
        number.move_to(np.array([1.3, 2.0 - 1.15 * index, 0]))
        description.move_to(np.array([2.1, number.get_center()[1], 0]), aligned_edge=LEFT)
        rows.add(VGroup(number, description))
    header = VGroup(
        Tex("Dimension", color=Palette.text_muted, font_size=32).move_to(np.array([1.3, 3.1, 0])),
        Tex("Subspace", color=Palette.text_muted, font_size=32).move_to(np.array([2.5, 3.1, 0]), aligned_edge=LEFT),
    )
    return header, rows


def subspace_axes(view):
    return projected_axes(view, ((-2, 2), (-2, 2), (-1, 2)), labels=("x_1", "x_2", "x_3"))


def scaled(direction, amount):
    return tuple(amount * value for value in direction)


def subspace_line(view):
    return Line(view(scaled(LINE_DIRECTION, -1.6)), view(scaled(LINE_DIRECTION, 1.6)), color=Palette.teal, stroke_width=5)


def subspace_sheet(view, reach=1.4):
    first, second = (np.array(vector) for vector in PLANE_SPAN)
    corners = [view(reach * (a * first + b * second)) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return Polygon(*corners, color=Palette.teal, fill_opacity=0.28, stroke_width=1.5, stroke_opacity=0.7)


def space_lattice(view):
    dots = VGroup()
    for x in range(-1, 2):
        for y in range(-2, 3):
            for z in range(-1, 3):
                dots.add(Dot(view((x, y, z)), radius=0.04, color=Palette.teal, fill_opacity=0.7))
    dots.submobjects.sort(key=lambda dot: np.linalg.norm(dot.get_center() - view((0, 0, 0))))
    return dots


def subspace_arrows(view):
    return VGroup(
        projected_arrow(view, LINE_DIRECTION, Palette.yellow, stroke_width=5),
        projected_arrow(view, PLANE_SPAN[1], Palette.blue, stroke_width=5),
        projected_arrow(view, THIRD_DIRECTION, Palette.pink, stroke_width=5),
    )


class Lesson(LessonScene):
    day = 15
    title = "Coordinates and dimension"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.basis_in_the_plane(plane)
        line = self.walk_to_x(plane, line)
        line = self.change_of_coordinates(line)
        line = self.clear_stage(line)
        line = self.polynomial_to_column(line)
        line = self.column_to_polynomial(line)
        line = self.add_both(line)
        line = self.isomorphism(line)
        line = self.too_many(line)
        line = self.too_few(line)
        line = self.dimension_table(line)
        line = self.subspaces_of_space(line)
        self.close_episode(
            r"Every basis of a space has the same number of vectors.\\"
            r"That number is the dimension of the space.",
            *self.mobjects,
        )

    def clear_stage(self, line):
        self.play(*[FadeOut(m) for m in self.mobjects if m is not line], run_time=0.7)
        return line

    def basis_in_the_plane(self, plane):
        self.plane = plane
        self.b_arrows, self.b_labels = basis_pair(plane, B1, B2)
        line = self.say(r"Yesterday a basis gave every vector one address.", hold=0.2)
        self.play(GrowArrow(self.b_arrows[0]), FadeIn(self.b_labels[0]), run_time=1.0, rate_func=spring_soft)
        self.play(GrowArrow(self.b_arrows[1]), FadeIn(self.b_labels[1]), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Today we write that address as numbers, then count the basis.", line, hold=Timing.read_short)
        self.grid = basis_grid(plane, B1, B2)
        line = self.say(r"Here $\mathbf b_1$ and $\mathbf b_2$ make a basis $\mathcal B$.", line, hold=0.2)
        self.play(plane.animate.set_opacity(0.35), run_time=0.6)
        self.add(self.grid, self.b_arrows, self.b_labels)
        self.play(Create(self.grid, lag_ratio=0.01), run_time=1.6)
        self.wait(Timing.read_short)
        return line

    def walk_to_x(self, plane, line):
        x_arrow = vector_arrow(X, Palette.yellow, plane)
        self.x_parts = VGroup(x_arrow, x_label(plane))
        self.walk = coordinate_walk(plane)
        line = self.say(r"Reach $\mathbf x$ with 2 steps of $\mathbf b_1$ and 1 of $\mathbf b_2$.", line, hold=0.2)
        self.play(GrowArrow(x_arrow), FadeIn(self.x_parts[1]), run_time=1.1, rate_func=spring_soft)
        self.play(Indicate(self.b_arrows[0], color=Palette.glow, scale_factor=1.08), run_time=0.8)
        self.play(TransformFromCopy(self.b_arrows[0], self.walk[0]), run_time=1.2, rate_func=spring)
        self.play(TransformFromCopy(self.b_arrows[1], self.walk[1]), run_time=1.2, rate_func=spring)
        self.wait(Timing.beat)

        self.coords_row = backed(coordinate_vector_row(), padding=0.2).move_to(np.array([4.6, 2.55, 0]))
        line = self.say(r"Those weights form the coordinate vector $[\mathbf x]_{\mathcal B}$.", line, hold=0.2)
        self.play(FadeIn(self.coords_row, shift=LEFT * 0.2), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return line

    def change_of_coordinates(self, line):
        product = backed(change_of_coordinates_row().scale(0.82), padding=0.2)
        product.next_to(self.coords_row, DOWN, buff=0.35)
        product.align_to(np.array([6.9, 0, 0]), RIGHT)
        line = self.say(r"The matrix $P_{\mathcal B}$ turns coordinates back into $\mathbf x$.", line, hold=0.2)
        self.play(FadeIn(product, shift=LEFT * 0.2), run_time=1.0, rate_func=spring_soft)
        self.play(
            Indicate(product[2], color=Palette.glow, scale_factor=1.08),
            Indicate(self.b_arrows, color=Palette.glow, scale_factor=1.06),
            run_time=1.0,
        )
        self.wait(Timing.read_short)
        line = self.say(r"Day 22 reuses $P_{\mathcal B}$ to switch between two bases.", line, hold=Timing.read_short)

        start = augmented([[2, -1, 3], [1, 2, 4]]).scale(0.82)
        finish = augmented([[1, 0, 2], [0, 1, 1]]).scale(0.82)
        reduce_sign = MathTex(r"\sim", color=Palette.text, font_size=44)
        row = backed(VGroup(start, reduce_sign, finish.copy()).arrange(RIGHT, buff=0.3), padding=0.2)
        row.next_to(product, DOWN, buff=0.35).align_to(np.array([6.9, 0, 0]), RIGHT)
        finish.move_to(row[3])
        reduced = start.copy()
        line = self.say(r"Row reduce $[\,\mathbf b_1\ \mathbf b_2 \mid \mathbf x\,]$ until the last column shows the weights.", line, hold=0.2)
        self.play(FadeIn(row.background_rectangle), FadeIn(start), FadeIn(reduce_sign), run_time=0.8)
        self.add(reduced)
        self.play(reduced.animate.move_to(finish), run_time=1.0, rate_func=spring_soft)
        morph_matrix(self, reduced, finish, run_time=1.2)
        last = VGroup(reduced.get_columns()[2])
        self.play(Indicate(last, color=Palette.glow, scale_factor=1.15), run_time=0.9)
        self.wait(Timing.read_short)
        line = self.say(r"Coordinates let column tools work in any space with a basis.", line, hold=Timing.read_short)
        return line

    def polynomial_to_column(self, line):
        self.graph = graph_axes()
        self.axes = self.graph[0]
        self.space = coefficient_space()
        self.formulas = formula_stack()
        self.columns = column_row()
        self.map = map_arrow(self.columns)
        line = self.say(r"Polynomials get coordinates too, from the basis $1, t, t^2$.", line, hold=0.2)
        self.play(Create(self.graph), Create(self.space), run_time=1.6)
        self.wait(Timing.beat)

        self.curves = {"p": curve(self.axes, P, Palette.yellow)}
        line = self.say(r"Here is a polynomial in $\mathbb P_2$.", line, hold=0.2)
        self.play(Write(self.formulas["p"]), run_time=1.0)
        self.play(Create(self.curves["p"]), run_time=1.6, rate_func=smooth)
        self.wait(Timing.beat)

        self.map_name = map_label(self.map, r"\mathbf p \mapsto [\mathbf p]_{\mathcal B}")
        line = self.say(r"Its coordinates are its three coefficients, stacked in a column.", line, hold=0.2)
        self.play(GrowArrow(self.map), FadeIn(self.map_name), run_time=1.0, rate_func=spring_soft)
        terms = coefficient_terms(self.formulas["p"], "p")
        self.play(Indicate(VGroup(*terms), color=Palette.glow, scale_factor=1.1), run_time=0.8)
        self.play(
            *[FadeTransform(term.copy(), entry) for term, entry in zip(terms, self.columns["p"].get_entries())],
            FadeIn(self.columns["p"].get_brackets()),
            run_time=1.4,
        )
        self.wait(Timing.beat)

        self.vectors = {"p": VGroup(*coefficient_vector("p"), coefficient_label("p"))}
        line = self.say(r"That column is also an arrow in $\mathbb R^3$.", line, hold=0.2)
        self.play(FadeIn(self.vectors["p"][0]), GrowArrow(self.vectors["p"][1]), run_time=1.2, rate_func=spring_soft)
        self.play(FadeIn(self.vectors["p"][2]), run_time=0.4)
        self.wait(Timing.read_short)
        return line

    def column_to_polynomial(self, line):
        line = self.say(r"Every column of three numbers turns back into one polynomial.", line, hold=0.2)
        q_col = self.columns["q"]
        self.play(FadeIn(q_col, shift=DOWN * 0.2), run_time=0.8, rate_func=spring_soft)
        back_name = map_label(self.map, r"[\mathbf q]_{\mathcal B} \mapsto \mathbf q")
        self.sfx("swish", gain=-4)
        self.play(Rotate(self.map, PI), FadeTransform(self.map_name, back_name), run_time=1.0, rate_func=spring)
        self.map_name = back_name
        formula = self.formulas["q"]
        terms = coefficient_terms(formula, "q")
        coefficient_parts = {id(part) for term in terms for part in term}
        scaffold = VGroup(*[part for part in formula if id(part) not in coefficient_parts])
        self.play(
            *[FadeTransform(entry.copy(), term) for entry, term in zip(q_col.get_entries(), terms)],
            FadeIn(scaffold),
            run_time=1.4,
        )
        self.curves["q"] = curve(self.axes, Q, Palette.blue)
        self.play(Create(self.curves["q"]), run_time=1.6, rate_func=smooth)
        self.vectors["q"] = VGroup(*coefficient_vector("q"), coefficient_label("q"))
        self.play(FadeIn(self.vectors["q"][0]), GrowArrow(self.vectors["q"][1]), FadeIn(self.vectors["q"][2]), run_time=1.2, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return line

    def add_both(self, line):
        line = self.say(r"Adding polynomials adds their columns and their arrows too.", line, hold=0.2)
        self.curves["sum"] = curve(self.axes, P_PLUS_Q, Palette.teal)
        self.play(Write(self.formulas["sum"]), Create(self.curves["sum"]), run_time=1.6)
        moved = projected_arrow(project, P_PLUS_Q, Palette.blue, start=P)
        self.play(TransformFromCopy(self.vectors["q"][1], moved), run_time=1.4, rate_func=spring)
        self.vectors["moved"] = VGroup(moved)
        self.vectors["sum"] = VGroup(*coefficient_vector("sum"), coefficient_label("sum"))
        self.play(FadeIn(self.vectors["sum"][0]), GrowArrow(self.vectors["sum"][1]), FadeIn(self.vectors["sum"][2]), run_time=1.2, rate_func=spring_soft)
        self.play(
            FadeIn(self.columns["plus"]),
            FadeIn(self.columns["equals"]),
            FadeIn(self.columns["sum"], shift=LEFT * 0.2),
            run_time=1.0,
            rate_func=spring,
        )
        self.wait(Timing.read_short)
        return line

    def isomorphism(self, line):
        polynomials = MathTex(r"\mathbb P_2", color=Palette.yellow, font_size=110).move_to(np.array([-3.6, 0.4, 0]))
        columns = MathTex(r"\mathbb R^3", color=Palette.teal, font_size=110).move_to(np.array([3.6, 0.4, 0]))
        link = DoubleArrow(
            polynomials.get_right() + RIGHT * 0.5,
            columns.get_left() + LEFT * 0.5,
            buff=0,
            color=Palette.text_muted,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.08,
        )
        name = MathTex(r"\mathbf p \mapsto [\mathbf p]_{\mathcal B}", color=Palette.text, font_size=40).next_to(link, UP, buff=0.2)
        left = VGroup(self.graph, *self.curves.values(), *self.formulas.values())
        right = VGroup(self.space, *self.columns.values(), *self.vectors.values())
        line = self.say(r"The map is one-to-one, onto $\mathbb R^3$, and linear.", line, hold=0.2)
        self.play(
            FadeTransform(left, polynomials),
            FadeTransform(right, columns),
            ReplacementTransform(self.map, link),
            FadeTransform(self.map_name, name),
            run_time=1.6,
            rate_func=spring_soft,
        )
        self.remove(*left.get_family(), *right.get_family())
        self.wait(Timing.read_short)
        word = Tex("isomorphism", color=Palette.glow, font_size=44).next_to(link, DOWN, buff=0.25)
        line = self.say(r"A map like that is called an isomorphism.", line, hold=0.2)
        self.play(FadeIn(word, shift=UP * 0.15), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"Day 21 uses this map to write $d/dt$ as a matrix.", line, hold=Timing.read_short)
        self.play(FadeOut(VGroup(polynomials, columns, link, name, word)), run_time=0.7)
        return line

    def too_many(self, line):
        plane = self.plane
        self.b_arrows, self.b_labels = basis_pair(plane, B1, B2)
        self.grid = basis_grid(plane, B1, B2)
        line = self.say(r"How many vectors can a basis of the plane hold?", line, hold=0.2)
        self.play(FadeIn(plane), FadeIn(self.grid), run_time=1.0)
        self.play(GrowArrow(self.b_arrows[0]), GrowArrow(self.b_arrows[1]), FadeIn(self.b_labels), run_time=1.1, rate_func=spring_soft)
        self.wait(Timing.beat)

        w_arrow = vector_arrow(W_VEC, Palette.blue, plane)
        w_name = backed(MathTex(r"\mathbf w", color=Palette.blue, font_size=40), padding=0.08).next_to(plane.c2p(*W_VEC), RIGHT, buff=0.12)
        line = self.say(r"A third vector $\mathbf w$ already has an address on the grid.", line, hold=0.2)
        self.play(GrowArrow(w_arrow), FadeIn(w_name), run_time=1.1, rate_func=spring_soft)
        back_step = arrow_between(plane, B1, W_VEC, Palette.j_hat, stroke_width=5)
        self.play(Indicate(self.b_arrows[0], color=Palette.glow, scale_factor=1.08), run_time=0.8)
        self.play(TransformFromCopy(self.b_arrows[1], back_step), run_time=1.3, rate_func=spring)
        self.wait(Timing.beat)

        relation = backed(
            tex(r"\mathbf w", "=", r"\mathbf b_1", "-", r"\mathbf b_2", colors=(Palette.blue, None, Palette.i_hat, None, Palette.j_hat), font_size=48),
            padding=0.22,
        ).move_to(np.array([4.6, 2.7, 0]))
        line = self.say(r"So $\mathbf w = \mathbf b_1 - \mathbf b_2$, and the three are dependent.", line, hold=0.2)
        self.play(FadeIn(relation, shift=LEFT * 0.2), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(w_arrow, w_name, back_step, relation)), run_time=0.6)
        return line

    def too_few(self, line):
        plane = self.plane
        far = 8
        span_line = Line(plane.c2p(-far * B1[0], -far * B1[1]), plane.c2p(far * B1[0], far * B1[1]), color=Palette.purple_gray, stroke_width=4)
        line = self.say(r"One vector alone spans only a line, not the plane.", line, hold=0.2)
        self.play(FadeOut(self.b_arrows[1]), FadeOut(self.b_labels[1]), FadeOut(self.grid), FadeIn(span_line), run_time=1.2)
        self.add(self.b_arrows[0], self.b_labels[0])
        self.wait(Timing.read_short)

        c_arrows, c_labels = basis_pair(plane, C1, C2, names=(r"\mathbf c_1", r"\mathbf c_2"))
        c_labels[0].next_to(plane.c2p(*C1), RIGHT, buff=0.12)
        c_grid = basis_grid(plane, C1, C2)
        line = self.say(r"Every basis of the plane has exactly two vectors.", line, hold=0.2)
        self.play(FadeOut(VGroup(span_line, self.b_arrows[0], self.b_labels[0])), run_time=0.6)
        self.add(c_grid)
        self.play(Create(c_grid, lag_ratio=0.01), run_time=1.2)
        self.play(GrowArrow(c_arrows[0]), GrowArrow(c_arrows[1]), FadeIn(c_labels), run_time=1.1, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return line

    def dimension_table(self, line):
        line = self.clear_stage(line)
        table = dimension_table()
        line = self.say(r"That shared count is the dimension of the space.", line, hold=0.2)
        self.play(FadeIn(table[0]), run_time=0.6)
        for row in table[1:]:
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.7, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"$\mathbb P_2$ has dimension 3 because $1, t, t^2$ is a basis.", line, hold=0.2)
        self.play(Indicate(table[3], color=Palette.glow, scale_factor=1.06), run_time=1.0)
        self.wait(Timing.read_short)
        self.play(FadeOut(table), run_time=0.6)
        return line

    def subspaces_of_space(self, line):
        view = subspace_view
        axes = subspace_axes(view)
        header, rows = subspace_rows()
        arrows = subspace_arrows(view)
        origin = Dot(view((0, 0, 0)), radius=0.11, color=Palette.teal)
        self.play(Create(axes), FadeIn(header), run_time=1.2)
        steps = [
            (r"The origin alone has dimension 0.", [GrowFromCenter(origin)]),
            (r"A line through the origin has dimension 1.", [Create(subspace_line(view)), GrowArrow(arrows[0])]),
            (r"A plane through the origin has dimension 2.", [FadeIn(subspace_sheet(view)), GrowArrow(arrows[1])]),
            (r"Only $\mathbb R^3$ itself has dimension 3.", [LaggedStart(*[GrowFromCenter(dot) for dot in space_lattice(view)], lag_ratio=0.01), GrowArrow(arrows[2])]),
        ]
        for index, (text, animations) in enumerate(steps):
            line = self.say(text, line, hold=0.2)
            fades = [rows[index - 1].animate.set_opacity(0.45)] if index else []
            self.play(FadeIn(rows[index], shift=LEFT * 0.15), *fades, run_time=0.6)
            self.play(*animations, run_time=1.4, rate_func=spring_soft)
            self.wait(Timing.read_short)
        self.play(rows.animate.set_opacity(1), run_time=0.6)
        self.wait(Timing.beat)
        line = self.say(r"Next, Day 16 finds bases for a matrix's column and row spaces.", line, hold=Timing.read_short)
        return line


def centerpiece(scene):
    """The polynomial side and the coordinate side, joined by the coordinate map."""
    graph = graph_axes()
    axes = graph[0]
    formulas = formula_stack()
    columns = column_row()
    arrow = map_arrow(columns)
    curves = VGroup(curve(axes, P, Palette.yellow), curve(axes, Q, Palette.blue), curve(axes, P_PLUS_Q, Palette.teal))
    vectors = VGroup(
        coefficient_vector("p"),
        coefficient_vector("q"),
        projected_arrow(project, P_PLUS_Q, Palette.blue, start=P),
        coefficient_vector("sum"),
        *[coefficient_label(key) for key in ARROW_LABELS],
    )
    scene.add(graph, coefficient_space(), curves, *formulas.values(), *columns.values(), arrow, map_label(arrow, r"\mathbf p \mapsto [\mathbf p]_{\mathcal B}"), vectors)


class FigCoordinates(Scene):
    def construct(self):
        plane = plane_at((-3.0, -2.2), 0.9)
        arrows, labels = basis_pair(plane, B1, B2)
        coords = backed(coordinate_vector_row(), padding=0.2).move_to(np.array([3.9, 1.2, 0]))
        self.add(plane.set_opacity(0.35), basis_grid(plane, B1, B2), coordinate_walk(plane), arrows, vector_arrow(X, Palette.yellow, plane), labels, x_label(plane), coords)


class FigPolynomialToColumn(Scene):
    def construct(self):
        centerpiece(self)
        fit_to_frame(self)


class FigThirdVector(Scene):
    def construct(self):
        plane = plane_at((-3.0, -0.6), 0.9)
        arrows, labels = basis_pair(plane, B1, B2)
        relation = backed(
            tex(r"\mathbf w", "=", r"\mathbf b_1", "-", r"\mathbf b_2", colors=(Palette.blue, None, Palette.i_hat, None, Palette.j_hat), font_size=52),
            padding=0.22,
        ).move_to(np.array([3.9, 2.4, 0]))
        w_name = backed(MathTex(r"\mathbf w", color=Palette.blue, font_size=40), padding=0.08).next_to(plane.c2p(*W_VEC), RIGHT, buff=0.12)
        self.add(
            plane.set_opacity(0.35),
            basis_grid(plane, B1, B2),
            arrow_between(plane, B1, W_VEC, Palette.j_hat, stroke_width=5),
            arrows,
            vector_arrow(W_VEC, Palette.blue, plane),
            labels,
            w_name,
            relation,
        )


class FigSubspaces(Scene):
    def construct(self):
        panels = VGroup()
        for size in range(4):
            view = oblique_projector((0, 0), unit=0.8)
            panel = VGroup(subspace_axes(view))
            panel.add(Dot(view((0, 0, 0)), radius=0.1, color=Palette.teal))
            arrows = subspace_arrows(view)
            extras = [VGroup(), VGroup(subspace_line(view), arrows[0]), VGroup(subspace_sheet(view), arrows[:2]), VGroup(space_lattice(view), arrows)]
            panel.add(extras[size])
            title = Tex(f"Dimension {size}", color=Palette.text, font_size=44).next_to(panel, UP, buff=0.3)
            panels.add(VGroup(title, panel))
        panels.arrange(RIGHT, buff=0.6)
        self.add(panels)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        centerpiece(self)
