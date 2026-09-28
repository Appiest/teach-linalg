import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    MatrixTracker,
    Palette,
    Timing,
    arrow_between,
    backed,
    column,
    fit_to_frame,
    matrix,
    moved_grid,
    plane_at,
    plate_for,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (0.8, -0.9)
PLANE_UNIT = 1.15
PLANE_MAP = ((2, -1), (1, 1))
X_WEIGHTS = (1, 2)
X_IMAGE = (0, 3)
WALK_CORNERS = ((0, 0), (2, 1), (1, 2), (0, 3))

BASIS_COLORS = (Palette.i_hat, Palette.j_hat, Palette.blue)
BASIS_NAMES = ("1", "t", "t^2")
BASIS_COEFFS = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
DERIVATIVES = (
    {"parts": ("0",), "coeffs": (0, 0, 0), "flights": {0: (0, 1, 2)}},
    {"parts": ("1",), "coeffs": (1, 0, 0), "flights": {0: (0,)}},
    {"parts": ("2", "t"), "coeffs": (0, 2, 0), "flights": {0: (1,)}},
)
DERIVATIVE_MATRIX = ((0, 1, 0), (0, 0, 2), (0, 0, 0))

INPUT_CENTER = (-5.1, 0.95)
OUTPUT_CENTER = (-1.2, 0.95)
FORMULA_Y = -0.75
COLUMN_AT = (1.95, 0.95)
MATRIX_AT = (4.75, 0.95)
LOG_Y = -1.95

P_PARTS = (r"\mathbf p(t)", "=", "3", "+", "5", "t", "-", "2", "t^2")
P_GROUPS = ((2,), (4,), (6, 7))
P_COORDS = (3, 5, -2)
DP_PARTS = (r"\mathbf p'(t)", "=", "5", "-", "4", "t")
DP_GROUPS = ((2,), (3, 4))
DP_COORDS = (5, -4, 0)
SQUARE_LEFT = -4.4
SQUARE_RIGHT = 4.3
SQUARE_TOP = 2.8
SQUARE_BOTTOM = -1.05


def tex(*parts, colors=(), font_size=46):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def point(xy):
    return np.array([xy[0], xy[1], 0.0])


def plane_matrix(rows):
    """A 2x2 matrix whose first column is green (where e1 lands) and second red (where e2 lands)."""
    mat = matrix([[str(entry) for entry in row] for row in rows])
    for index, color in enumerate(BASIS_COLORS[:2]):
        mat.get_columns()[index].set_color(color)
    return mat


def unknown_matrix():
    mat = matrix([["?", "?"], ["?", "?"]])
    mat.get_entries().set_color(Palette.text_muted)
    return mat


def landing_label(plane, coords, color, direction):
    col = column([str(value) for value in coords], color=color).scale(0.8)
    return backed(col, padding=0.12).next_to(plane.c2p(*coords), direction, buff=0.14)


def live_arrow(plane, tracker, target, color):
    tip = tracker.apply(target)
    if np.hypot(*tip) < 0.06:
        return Dot(plane.c2p(0, 0), radius=0.07, color=color)
    return vector_arrow(tip, color, plane)


def basis_arrows(plane, tracker):
    return VGroup(
        always_redraw(lambda: live_arrow(plane, tracker, (1, 0), Palette.i_hat)),
        always_redraw(lambda: live_arrow(plane, tracker, (0, 1), Palette.j_hat)),
    )


def walk_arrows(plane):
    """One green step of T(e1) and two red steps of T(e2), tip to tail, ending at T(x)."""
    colors = (Palette.i_hat, Palette.j_hat, Palette.j_hat)
    return VGroup(*[
        arrow_between(plane, start, end, color, stroke_width=5)
        for start, end, color in zip(WALK_CORNERS, WALK_CORNERS[1:], colors)
    ])


def image_label(plane):
    return backed(tex(r"T(\mathbf x)", colors=(Palette.teal,), font_size=40), padding=0.08).next_to(plane.c2p(*X_IMAGE), RIGHT, buff=0.15)


def standard_panel():
    first = VGroup(tex("A", "="), plane_matrix(PLANE_MAP)).arrange(RIGHT, buff=0.2)
    second = VGroup(
        tex("A"),
        column([str(value) for value in X_WEIGHTS], color=Palette.yellow),
        tex("="),
        column([str(value) for value in X_IMAGE], color=Palette.teal),
    ).arrange(RIGHT, buff=0.2)
    second.next_to(first, DOWN, buff=0.35, aligned_edge=LEFT)
    return VGroup(first, second).to_corner(UL, buff=0.6)


def polynomial(coeffs):
    return lambda t: coeffs[0] + coeffs[1] * t + coeffs[2] * t * t


def mini_axes(center):
    axes = Axes(
        x_range=(-1.2, 1.2, 1),
        y_range=(-2.4, 2.4, 1),
        x_length=3.0,
        y_length=2.4,
        tips=False,
        axis_config={"color": Palette.axis, "stroke_width": 2, "include_ticks": False},
    )
    axes.shift(point(center) - axes.c2p(0, 0))
    return axes


def mini_curve(axes, coeffs, color):
    return axes.plot(polynomial(coeffs), x_range=[-1.2, 1.2, 0.02], color=color, stroke_width=6)


def gate(left_x, right_x, label_tex):
    y = INPUT_CENTER[1]
    arrow = Arrow(point((left_x, y)), point((right_x, y)), buff=0, color=Palette.text_muted, stroke_width=4, max_tip_length_to_length_ratio=0.22)
    label = MathTex(label_tex, color=Palette.text, font_size=38).next_to(arrow, UP, buff=0.15)
    return VGroup(arrow, label)


def header():
    parts = tex(r"T = \tfrac{d}{dt}", r"\qquad", r"\mathcal B = \{", "1", ",", "t", ",", "t^2", r"\}", font_size=46)
    for index, color in zip((3, 5, 7), BASIS_COLORS):
        parts[index].set_color(color)
    return parts.to_corner(UL, buff=0.5)


def header_basis(parts):
    return [parts[3], parts[5], parts[7]]


def derivative_matrix(rows=DERIVATIVE_MATRIX):
    mat = Matrix([[str(entry) for entry in row] for row in rows], v_buff=0.62, h_buff=0.78, bracket_h_buff=0.14)
    for index, color in enumerate(BASIS_COLORS):
        mat.get_columns()[index].set_color(color)
    return mat


def column_headers(mat, names=BASIS_NAMES):
    headers = VGroup()
    top = mat.get_top()[1] + 0.35
    for col, name, color in zip(mat.get_columns(), names, BASIS_COLORS):
        headers.add(MathTex(name, color=color, font_size=34).move_to(point((col.get_center()[0], top))))
    return headers


def row_labels(mat, names=BASIS_NAMES):
    labels = VGroup()
    right = mat.get_right()[0] + 0.45
    for row, name in zip(mat.get_rows(), names):
        labels.add(MathTex(name, color=Palette.text_muted, font_size=32).move_to(point((right, row.get_center()[1]))))
    return labels


def column_slots(mat):
    height = mat.get_brackets().height - 0.3
    return VGroup(*[
        Rectangle(width=0.72, height=height, fill_color=Palette.text, fill_opacity=0.07, stroke_width=0).move_to(col.get_center() * np.array([1, 0, 0]) + mat.get_center() * np.array([0, 1, 0]))
        for col in mat.get_columns()
    ])


def log_entry(index):
    name, color = BASIS_NAMES[index], BASIS_COLORS[index]
    output = "".join(DERIVATIVES[index]["parts"])
    return tex("T(", name, ")", "=", output, colors=(None, color, None, None, color), font_size=40)


def pipeline_log():
    entries = VGroup(*[log_entry(index) for index in range(3)]).arrange(RIGHT, buff=0.9)
    return entries.move_to(point(((INPUT_CENTER[0] + COLUMN_AT[0]) / 2, LOG_Y)))


def pipeline_stage():
    """Everything that stays on screen while the three basis polynomials pass through."""
    mat = derivative_matrix().scale(1.3).move_to(point(MATRIX_AT))
    name = MathTex(r"[T]_{\mathcal B}", color=Palette.text, font_size=50)
    headers = column_headers(mat)
    name.next_to(headers, UP, buff=0.3)
    return {
        "header": header(),
        "input_axes": mini_axes(INPUT_CENTER),
        "output_axes": mini_axes(OUTPUT_CENTER),
        "gates": VGroup(gate(-3.45, -2.85, r"\tfrac{d}{dt}"), gate(0.45, 1.4, r"[\,\cdot\,]_{\mathcal B}")),
        "matrix": mat,
        "slots": column_slots(mat),
        "name": name,
        "headers": headers,
        "rows": row_labels(mat),
        "log": pipeline_log(),
    }


def input_formula(index):
    return MathTex(BASIS_NAMES[index], color=BASIS_COLORS[index], font_size=60).move_to(point((INPUT_CENTER[0], FORMULA_Y)))


def output_formula(index):
    return MathTex(*DERIVATIVES[index]["parts"], color=BASIS_COLORS[index], font_size=60).move_to(point((OUTPUT_CENTER[0], FORMULA_Y)))


def coordinate_column(entries, color, scale=0.95):
    return column([str(value) for value in entries], color=color).scale(scale)


def square_formula(parts, color, x):
    formula = MathTex(*parts, color=color, font_size=52)
    formula[1].set_color(Palette.text)
    return formula.move_to(point((x, SQUARE_TOP)))


def square_stage():
    p_formula = square_formula(P_PARTS, Palette.yellow, SQUARE_LEFT)
    dp_formula = square_formula(DP_PARTS, Palette.teal, SQUARE_RIGHT)
    p_col = coordinate_column(P_COORDS, Palette.yellow).move_to(point((SQUARE_LEFT, SQUARE_BOTTOM)))
    dp_col = coordinate_column(DP_COORDS, Palette.teal).move_to(point((SQUARE_RIGHT, SQUARE_BOTTOM)))
    arrow_style = {"buff": 0, "color": Palette.text_muted, "stroke_width": 4, "max_tip_length_to_length_ratio": 0.1}
    top = Arrow(p_formula.get_right() + RIGHT * 0.3, dp_formula.get_left() + LEFT * 0.3, **arrow_style)
    bottom = Arrow(p_col.get_right() + RIGHT * 0.3, dp_col.get_left() + LEFT * 0.3, **arrow_style)
    left = Arrow(point((SQUARE_LEFT, SQUARE_TOP - 0.45)), p_col.get_top() + UP * 0.2, **arrow_style)
    right = Arrow(point((SQUARE_RIGHT, SQUARE_TOP - 0.45)), dp_col.get_top() + UP * 0.2, **arrow_style)
    coordinate_tex = r"[\,\cdot\,]_{\mathcal B}"
    labels = VGroup(
        MathTex(r"\tfrac{d}{dt}", color=Palette.text, font_size=40).next_to(top, UP, buff=0.12),
        MathTex(coordinate_tex, color=Palette.text, font_size=38).next_to(left, LEFT, buff=0.15),
        MathTex(coordinate_tex, color=Palette.text, font_size=38).next_to(right, RIGHT, buff=0.15),
    )
    mat = derivative_matrix().scale(0.85).next_to(bottom, UP, buff=0.3)
    name = MathTex(r"[T]_{\mathcal B}", color=Palette.text, font_size=46).next_to(mat, LEFT, buff=0.2)
    return {
        "p": p_formula,
        "dp": dp_formula,
        "p_col": p_col,
        "dp_col": dp_col,
        "arrows": {"top": top, "bottom": bottom, "left": left, "right": right},
        "labels": labels,
        "matrix": mat,
        "name": name,
    }


def coefficient_groups(formula, groups):
    return [VGroup(*[formula[index] for index in group]) for group in groups]


class Lesson(LessonScene):
    day = 21
    title = "The matrix of a linear transformation"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        self.plane = plane
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.landing_spots()
        line = self.standard_matrix(line)
        line = self.walk(line)
        line = self.clear_stage(line, r"Polynomials are not arrows, but they still have a basis.")
        line = self.set_up_pipeline(line)
        line = self.feed_all(line)
        line = self.read_the_matrix(line)
        line = self.two_routes(line)
        line = self.output_basis(line)
        line = self.recipe(line)
        self.close_episode(
            r"Pick a basis on each side, and a linear map becomes a matrix.\\"
            r"Column $j$ is where $\mathbf b_j$ lands, written in coordinates.",
            *self.mobjects,
        )

    def clear_stage(self, line, text):
        line = self.say(text, line, hold=0.2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not line], run_time=0.8)
        return line

    def landing_spots(self):
        plane = self.plane
        self.tracker = MatrixTracker()
        grid = always_redraw(lambda: moved_grid(plane, self.tracker))
        arrows = basis_arrows(plane, self.tracker)
        line = self.say(r"Day 20 showed that maps like $\tfrac{d}{dt}$ are linear.", hold=0.2)
        still = VGroup(vector_arrow((1, 0), Palette.i_hat, plane), vector_arrow((0, 1), Palette.j_hat, plane))
        self.play(GrowArrow(still[0]), GrowArrow(still[1]), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Today we write every linear map as a matrix.", line, hold=Timing.read_short)
        line = self.say(r"A linear map $T$ moves the whole plane.", line, hold=0.2)
        self.remove(*still)
        self.add(arrows)
        self.play(plane.animate.set_opacity(0.35), FadeIn(grid), run_time=0.8)
        self.bring_to_front(arrows)
        self.play(*self.tracker.to(PLANE_MAP), run_time=2.6, rate_func=spring_soft)
        self.wait(Timing.beat)

        self.landings = VGroup(
            landing_label(plane, (2, 1), Palette.i_hat, RIGHT),
            landing_label(plane, (-1, 1), Palette.j_hat, UL),
        )
        line = self.say(r"It is pinned down by where $\mathbf e_1$ and $\mathbf e_2$ land.", line, hold=0.2)
        for label in self.landings:
            self.play(FadeIn(label, scale=0.8), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        return line

    def standard_matrix(self, line):
        self.panel = standard_panel()
        name, answer = self.panel[0]
        question = unknown_matrix()
        for mark, slot in zip(question.get_entries(), answer.get_entries()):
            mark.move_to(slot)
        self.plate = plate_for(self.panel[0])
        line = self.say(r"Stack the landing spots as columns to get the standard matrix.", line, hold=0.2)
        self.play(FadeIn(self.plate), FadeIn(name), FadeIn(answer.get_brackets()), FadeIn(question.get_entries()), run_time=0.8)
        for index, label in enumerate(self.landings):
            self.play(
                FadeOut(question.get_columns()[index]),
                TransformFromCopy(label.get_entries(), answer.get_columns()[index]),
                run_time=1.1,
            )
            self.play(Indicate(answer.get_columns()[index], color=Palette.glow, scale_factor=1.15), run_time=0.6)
        self.remove(*question.get_entries(), *answer.get_columns(), answer.get_brackets())
        self.add(answer)
        self.wait(Timing.read_short)
        return line

    def walk(self, line):
        plane = self.plane
        steps = walk_arrows(plane)
        line = self.say(r"$\mathbf x = \mathbf e_1 + 2\mathbf e_2$ lands on $T(\mathbf e_1) + 2\,T(\mathbf e_2)$.", line, hold=0.2)
        self.play(FadeOut(self.landings), run_time=0.4)
        for step in steps:
            self.play(GrowArrow(step), run_time=0.8, rate_func=spring_soft)
        image = vector_arrow(X_IMAGE, Palette.teal, plane, stroke_width=7)
        self.play(GrowArrow(image), FadeIn(image_label(plane)), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.beat)

        line = self.say(r"That sum is exactly $A\mathbf x$, so $A$ does everything $T$ does.", line, hold=0.2)
        self.play(self.plate.animate.become(plate_for(self.panel)), run_time=0.5, rate_func=spring_soft)
        self.play(FadeIn(self.panel[1], shift=DOWN * 0.15), run_time=0.9, rate_func=spring_soft)
        self.play(Indicate(self.panel[1][3], color=Palette.glow, scale_factor=1.15), run_time=0.8)
        self.wait(Timing.read_long)
        return line

    def set_up_pipeline(self, line):
        stage = pipeline_stage()
        self.stage = stage
        line = self.say(r"We want a matrix that differentiates by multiplying coordinates.", line, hold=0.2)
        self.play(Write(stage["header"]), run_time=1.2)
        self.wait(Timing.beat)
        line = self.say(r"Build the matrix of $\tfrac{d}{dt}$ on $\mathbb P_2$ one column at a time.", line, hold=0.2)
        self.play(Create(stage["input_axes"]), Create(stage["output_axes"]), FadeIn(stage["gates"]), run_time=1.2)
        self.play(
            FadeIn(stage["matrix"].get_brackets()),
            FadeIn(stage["slots"]),
            FadeIn(stage["name"]),
            FadeIn(stage["headers"]),
            FadeIn(stage["rows"]),
            run_time=1.0,
        )
        self.wait(Timing.read_short)
        return line

    def feed_all(self, line):
        captions = (
            (r"A constant has slope 0, so $T(1) = 0$.", r"Its coordinates are all zero, and that column goes in slot 1."),
            (r"The derivative of $t$ is $1$, with coordinates $(1, 0, 0)$.", None),
            (r"The derivative of $t^2$ is $2t$, with coordinates $(0, 2, 0)$.", None),
        )
        for index, texts in enumerate(captions):
            line = self.feed(index, line, texts)
        self.play(Indicate(self.stage["matrix"].get_entries(), color=Palette.glow, scale_factor=1.08), run_time=1.0)
        self.wait(Timing.read_short)
        return line

    def feed(self, index, line, texts):
        stage = self.stage
        color = BASIS_COLORS[index]
        entry, exit_ = input_formula(index), output_formula(index)
        in_curve = mini_curve(stage["input_axes"], BASIS_COEFFS[index], color)
        out_curve = mini_curve(stage["output_axes"], DERIVATIVES[index]["coeffs"], color)
        line = self.say(texts[0], line, hold=0.2)
        self.play(TransformFromCopy(header_basis(stage["header"])[index], entry), run_time=1.0, rate_func=spring)
        self.play(Create(in_curve), run_time=0.9)
        self.play(ReplacementTransform(in_curve.copy(), out_curve), FadeTransform(entry.copy(), exit_), run_time=1.5, rate_func=spring_soft)
        self.play(FadeIn(stage["log"][index], shift=UP * 0.15), run_time=0.6, rate_func=spring_soft)
        self.wait(Timing.beat)

        if texts[1]:
            line = self.say(texts[1], line, hold=0.2)
        col = self.drop_into_column(index, exit_)
        self.fly_into_slot(index, col)
        self.wait(Timing.beat)
        self.play(FadeOut(VGroup(entry, exit_, in_curve, out_curve)), run_time=0.5)
        return line

    def drop_into_column(self, index, formula):
        derivative = DERIVATIVES[index]
        col = coordinate_column(derivative["coeffs"], BASIS_COLORS[index]).move_to(point(COLUMN_AT))
        entries = col.get_entries()
        flights = [(part, row) for part, rows in derivative["flights"].items() for row in rows]
        landed = {row for _, row in flights}
        self.play(
            FadeIn(col.get_brackets()),
            *[TransformFromCopy(formula[part], entries[row]) for part, row in flights],
            *[FadeIn(entries[row], shift=DOWN * 0.2) for row in range(3) if row not in landed],
            run_time=1.3,
            rate_func=spring_soft,
        )
        return col

    def fly_into_slot(self, index, col):
        target = self.stage["matrix"].get_columns()[index]
        self.play(
            *[ReplacementTransform(source, destination) for source, destination in zip(col.get_entries(), target)],
            FadeOut(col.get_brackets()),
            FadeOut(self.stage["slots"][index]),
            run_time=1.3,
            rate_func=spring,
        )
        self.play(Indicate(target, color=Palette.glow, scale_factor=1.12), run_time=0.6)

    def read_the_matrix(self, line):
        mat = self.stage["matrix"]
        self.remove(*mat.get_entries(), mat.get_brackets())
        self.add(mat)
        line = self.say(r"Column 1 is all zeros because $T$ sends $1$ to $0$.", line, hold=0.2)
        self.play(Indicate(mat.get_columns()[0], color=Palette.glow, scale_factor=1.15), Indicate(self.stage["log"][0], color=Palette.glow, scale_factor=1.1), run_time=1.2)
        self.wait(Timing.read_short)
        return line

    def two_routes(self, line):
        square = square_stage()
        self.square = square
        stage = self.stage
        line = self.say(r"Now send $\mathbf p(t) = 3 + 5t - 2t^2$ along two routes.", line, hold=0.2)
        keep = {id(stage["matrix"]), id(stage["name"]), id(line)}
        self.play(*[FadeOut(m) for m in self.mobjects if id(m) not in keep], run_time=0.7)
        self.play(
            ReplacementTransform(stage["matrix"], square["matrix"]),
            ReplacementTransform(stage["name"], square["name"]),
            run_time=1.3,
            rate_func=spring_soft,
        )
        self.play(Write(square["p"]), run_time=1.0)
        self.wait(Timing.beat)
        line = self.down_then_across(line)
        line = self.across_then_down(line)
        line = self.say(r"So $[T(\mathbf p)]_{\mathcal B} = [T]_{\mathcal B}\,[\mathbf p]_{\mathcal B}$ for every $\mathbf p$.", line, hold=Timing.read_long)
        return line

    def down_then_across(self, line):
        square = self.square
        arrows = square["arrows"]
        p_col = square["p_col"]
        line = self.say(r"Down, then across: take coordinates, then multiply by $[T]_{\mathcal B}$.", line, hold=0.2)
        self.play(GrowArrow(arrows["left"]), FadeIn(square["labels"][1]), run_time=0.8, rate_func=spring_soft)
        groups = coefficient_groups(square["p"], P_GROUPS)
        self.play(
            FadeIn(p_col.get_brackets()),
            *[FadeTransform(group.copy(), entry) for group, entry in zip(groups, p_col.get_entries())],
            run_time=1.3,
        )
        self.play(GrowArrow(arrows["bottom"]), run_time=0.8, rate_func=spring_soft)
        result = square["dp_col"]
        self.play(FadeIn(result.get_brackets()), run_time=0.4)
        rows = square["matrix"].get_rows()
        for row, entry in zip(rows, result.get_entries()):
            self.play(Indicate(row, color=Palette.glow, scale_factor=1.12), Indicate(p_col.get_entries(), color=Palette.glow, scale_factor=1.05), run_time=0.7)
            self.play(FadeIn(entry, shift=RIGHT * 0.2), run_time=0.5, rate_func=spring)
        self.wait(Timing.beat)
        return line

    def across_then_down(self, line):
        square = self.square
        arrows = square["arrows"]
        line = self.say(r"Across, then down: differentiate first, then take coordinates.", line, hold=0.2)
        self.play(GrowArrow(arrows["top"]), FadeIn(square["labels"][0]), run_time=0.8, rate_func=spring_soft)
        self.play(Write(square["dp"]), run_time=1.0)
        self.play(GrowArrow(arrows["right"]), FadeIn(square["labels"][2]), run_time=0.8, rate_func=spring_soft)
        result = square["dp_col"]
        arrivals = result.get_entries().copy()
        groups = coefficient_groups(square["dp"], DP_GROUPS)
        self.play(
            *[FadeTransform(group.copy(), entry) for group, entry in zip(groups, arrivals[:2])],
            FadeIn(arrivals[2], shift=DOWN * 0.2),
            run_time=1.3,
        )
        self.remove(*arrivals)
        ring = SurroundingRectangle(result, color=Palette.glow, buff=0.14, stroke_width=4)
        line = self.say(r"Both routes land on the same column.", line, hold=0.2)
        self.play(Create(ring), Flash(result, color=Palette.glow, line_length=0.3, flash_radius=1.1), run_time=0.9)
        self.wait(Timing.read_short)
        return line

    def output_basis(self, line):
        square = self.square
        big = derivative_matrix().scale(1.2).move_to(point((0.4, 0.5)))
        name = tex(r"[T]_{\mathcal B}", "=", font_size=54).next_to(big, LEFT, buff=0.25)
        headers, labels = column_headers(big), row_labels(big)
        line = self.say(r"Every derivative here lies in $\mathbb P_1$, with basis $\mathcal C = \{1, t\}$.", line, hold=0.2)
        keep = {id(square["matrix"]), id(line)}
        self.play(*[FadeOut(m) for m in self.mobjects if id(m) not in keep], run_time=0.7)
        self.play(ReplacementTransform(square["matrix"], big), run_time=1.2, rate_func=spring_soft)
        self.play(FadeIn(name), FadeIn(headers), FadeIn(labels), run_time=0.8)
        self.play(Indicate(big.get_rows()[2], color=Palette.glow, scale_factor=1.12), Indicate(labels[2], color=Palette.glow), run_time=0.9)
        self.wait(Timing.beat)

        small = derivative_matrix(DERIVATIVE_MATRIX[:2]).scale(1.2)
        small.move_to(big, aligned_edge=UP)
        new_name = tex(r"[T]_{\mathcal C \leftarrow \mathcal B}", "=", font_size=54).next_to(small, LEFT, buff=0.25)
        kept = [(big.get_rows()[r][c], small.get_rows()[r][c]) for r in range(2) for c in range(3)]
        line = self.say(r"Using $\mathcal C$ for the outputs drops the zero row.", line, hold=0.2)
        self.play(
            FadeOut(big.get_rows()[2], shift=DOWN * 0.2),
            FadeOut(labels[2]),
            FadeTransform(big.get_brackets(), small.get_brackets()),
            *[ReplacementTransform(old, new) for old, new in kept],
            FadeTransform(name, new_name),
            labels[:2].animate.move_to(row_labels(small)[:2]),
            run_time=1.4,
            rate_func=spring_soft,
        )
        self.wait(Timing.beat)
        line = self.say(r"Columns follow the input basis, and rows follow the output basis.", line, hold=0.2)
        self.play(Indicate(headers, color=Palette.glow, scale_factor=1.1), run_time=0.9)
        self.play(Indicate(labels[:2], color=Palette.glow, scale_factor=1.2), run_time=0.9)
        self.wait(Timing.read_short)
        return line

    def recipe(self, line):
        general = tex(
            r"[T]_{\mathcal C\leftarrow\mathcal B}", "=",
            r"\big[\;[T(\mathbf b_1)]_{\mathcal C}", r"\;\;\cdots\;\;", r"[T(\mathbf b_n)]_{\mathcal C}\;\big]",
            font_size=58,
        )
        standard = tex("A", "=", r"\big[\;T(\mathbf e_1)", r"\;\;\cdots\;\;", r"T(\mathbf e_n)\;\big]", font_size=58)
        VGroup(general, standard).arrange(DOWN, buff=1.0).move_to(point((0, 0.6)))
        standard.shift(RIGHT * (general[1].get_center()[0] - standard[1].get_center()[0]))
        line = self.say(r"The recipe works for any bases.", line, hold=0.2)
        self.play(*[FadeOut(m) for m in self.mobjects if m is not line], run_time=0.7)
        self.play(FadeIn(general, shift=UP * 0.2), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"With standard bases on $\mathbb R^n$, it gives the standard matrix.", line, hold=0.2)
        self.play(FadeIn(standard, shift=UP * 0.2), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"Tomorrow $T$ is the identity, and the matrix changes basis.", line, hold=Timing.read_short)
        return line


def standard_matrix_still(scene):
    plane = plane_at((1.4, -2.2), 1.15)
    tracker = MatrixTracker(PLANE_MAP)
    plane.set_opacity(0.35)
    panel = standard_panel()
    scene.add(
        plane,
        moved_grid(plane, tracker),
        walk_arrows(plane),
        vector_arrow(X_IMAGE, Palette.teal, plane, stroke_width=7),
        live_arrow(plane, tracker, (1, 0), Palette.i_hat),
        live_arrow(plane, tracker, (0, 1), Palette.j_hat),
        landing_label(plane, (2, 1), Palette.i_hat, RIGHT),
        landing_label(plane, (-1, 1), Palette.j_hat, UL),
        image_label(plane),
        plate_for(panel),
        panel,
    )


def pipeline_still(scene, index=2):
    stage = pipeline_stage()
    color = BASIS_COLORS[index]
    col = coordinate_column(DERIVATIVES[index]["coeffs"], color).move_to(point(COLUMN_AT))
    scene.add(
        *[stage[key] for key in ("header", "input_axes", "output_axes", "gates", "matrix", "name", "headers", "rows", "log")],
        mini_curve(stage["input_axes"], BASIS_COEFFS[index], color),
        mini_curve(stage["output_axes"], DERIVATIVES[index]["coeffs"], color),
        input_formula(index),
        output_formula(index),
        col,
    )


def two_routes_still(scene):
    square = square_stage()
    ring = SurroundingRectangle(square["dp_col"], color=Palette.glow, buff=0.14, stroke_width=4)
    scene.add(square["p"], square["dp"], square["p_col"], square["dp_col"], *square["arrows"].values(), square["labels"], square["matrix"], square["name"], ring)


class FigStandardMatrix(Scene):
    def construct(self):
        standard_matrix_still(self)


class FigDerivativeMatrix(Scene):
    def construct(self):
        pipeline_still(self)
        fit_to_frame(self)


class FigTwoRoutes(Scene):
    def construct(self):
        two_routes_still(self)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        pipeline_still(self)
        fit_to_frame(self, margin=0.5)
