import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    Palette,
    Timing,
    arrow_between,
    augmented_block,
    backed,
    column,
    fit_to_frame,
    matrix,
    morph_matrix,
    plane_at,
    scrim,
    skewed_grid,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (-4.9, -1.4)
PLANE_UNIT = 1.0
PANEL_LEFT = 2.3
PANEL_X = 4.72
FIG_ORIGIN = (-4.9, -2.0)
FIG_UNIT = 1.0

B1, B2 = (2, 1), (-1, 2)
C1, C2 = (1, 0), (-1, 1)
X = (3, 4)
X_IN_B = (2, 1)
X_IN_C = (7, 4)
B1_IN_C = (3, 1)
B2_IN_C = (1, 2)
T_B1 = (4, 2)
T_B2 = (3, -1)

B_COLORS = (Palette.i_hat, Palette.j_hat)
C_COLORS = (Palette.pink, Palette.blue)


def plus(p, q, weight=1.0):
    return (p[0] + weight * q[0], p[1] + weight * q[1])


def scaled(v, amount):
    return (v[0] * amount, v[1] * amount)


def tex(*parts, colors=(), font_size=40):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def name_label(tex_string, color, point, direction, font_size=38):
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.08).next_to(point, direction, buff=0.1)


def colored_column(entries, colors):
    col = column([str(value) for value in entries])
    for entry, color in zip(col.get_entries(), colors):
        entry.set_color(color)
    return col


def column_colored_matrix(rows, colors=B_COLORS):
    mat = matrix(rows)
    for col, color in zip(mat.get_columns(), colors):
        col.set_color(color)
    return mat


def side_panel():
    panel = Rectangle(
        width=config.frame_width / 2 - PANEL_LEFT + 0.2,
        height=config.frame_height + 0.2,
        fill_color=Palette.background,
        fill_opacity=0.94,
        stroke_width=0,
    )
    return panel.move_to(np.array([PANEL_LEFT + panel.width / 2, 0, 0])).set_z_index(5)


def on_panel(mobject, y):
    return mobject.move_to(np.array([PANEL_X, y, 0])).set_z_index(6)


def basis_parts(plane, vectors, colors, names, sides):
    arrows = VGroup(*[vector_arrow(v, c, plane) for v, c in zip(vectors, colors)])
    labels = VGroup(*[name_label(n, c, plane.c2p(*v), side) for v, c, n, side in zip(vectors, colors, names, sides)])
    return arrows, labels


def b_parts(plane):
    return basis_parts(plane, (B1, B2), B_COLORS, (r"\mathbf b_1", r"\mathbf b_2"), (UL, LEFT))


def c_parts(plane):
    return basis_parts(plane, (C1, C2), C_COLORS, (r"\mathbf c_1", r"\mathbf c_2"), (DOWN, LEFT))


def b_grid(plane):
    return skewed_grid(plane, B1, B2, reach=14, color=Palette.purple_gray, opacity=0.6)


def c_grid(plane):
    return skewed_grid(plane, C1, C2, reach=24, color=Palette.pink, opacity=0.42)


def walk(plane, weights, vectors, colors, amount=1.0, stroke_width=5):
    """Tip-to-tail arrows for weights[0] steps of vectors[0], then weights[1] of vectors[1], all scaled by amount."""
    corner = scaled(vectors[0], weights[0] * amount)
    end = plus(corner, vectors[1], weights[1] * amount)
    return VGroup(
        arrow_between(plane, (0, 0), corner, colors[0], stroke_width=stroke_width),
        arrow_between(plane, corner, end, colors[1], stroke_width=stroke_width),
    )


def step_dots(plane, weights, vectors, colors):
    """A dot at every whole step of a walk, so the steps can be counted."""
    dots, start = VGroup(), (0, 0)
    for weight, vector, color in zip(weights, vectors, colors):
        sign = 1 if weight > 0 else -1
        for k in range(1, abs(weight) + 1):
            dots.add(Dot(plane.c2p(*plus(start, vector, sign * k)), radius=0.075, color=color))
        start = plus(start, vector, weight)
    return dots


def x_arrow(plane, amount=1.0):
    return vector_arrow(scaled(X, amount), Palette.yellow, plane)


def x_label(plane):
    return name_label(r"\mathbf x", Palette.yellow, plane.c2p(*X), UL).shift(UL * 0.12)


def address(name, entries, colors, font_size=40):
    return VGroup(MathTex(name, "=", color=Palette.text, font_size=font_size), colored_column(entries, colors).scale(0.85)).arrange(RIGHT, buff=0.18)


def count_up(frame, tracker, entries):
    """Numbers that sit in the frame's entry slots and show entries times the tracker's value."""
    numbers = VGroup()
    for slot, value in zip(frame[1].get_entries(), entries):
        number = DecimalNumber(0, num_decimal_places=1, color=slot.get_color(), font_size=48).scale(0.76).set_z_index(6)
        number.add_updater(lambda m, v=value, c=slot.get_center(): m.set_value(v * tracker.get_value()).move_to(c).set_z_index(6))
        numbers.add(number)
    return numbers


def recipe(target, target_color, weights, names, colors, font_size=40):
    """target = w1 name1 + w2 name2, with the weights in plain text so they can fly into a column."""
    second = str(weights[1]) if weights[1] >= 0 else str(-weights[1])
    sign = "+" if weights[1] >= 0 else "-"
    formula = tex(target, "=", str(weights[0]), names[0], sign, second, names[1], colors=(target_color, None, None, colors[0], None, None, colors[1]), font_size=font_size)
    formula.weights = (formula[2], formula[5] if weights[1] >= 0 else VGroup(formula[4], formula[5]))
    return formula


class Lesson(LessonScene):
    day = 22
    title = "Change of basis"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        self.plane = plane
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.recall_b(plane)
        line = self.add_c(plane, line)
        line = self.grow_together(plane, line)
        line = self.columns_of_p(plane, line)
        line = self.combine_columns(line)
        line = self.inverse(line)
        line = self.row_reduce(line)
        line = self.map_in_b(plane, line)
        line = self.similarity_square(line)
        self.close_episode(
            r"A change-of-basis matrix renames a vector without moving it.\\"
            r"Its columns are the old basis written in the new one.",
            *self.mobjects,
        )

    def adopt(self, group):
        """Make `group` the only top-level owner of its parts, so fading it later removes all of them."""
        self.remove(*group.get_family())
        group.z_index = max(part.z_index for part in group.get_family())
        self.add(group)

    def clear_panel(self):
        leaving = [m for m in self.mobjects if 6 <= m.z_index < 20]
        if leaving:
            self.play(*[FadeOut(m) for m in leaving], run_time=0.6)

    def recall_b(self, plane):
        self.b_arrows, self.b_labels = b_parts(plane)
        self.b_grid = b_grid(plane)
        line = self.say(r"Day 15 gave $\mathbf x$ an address in the basis $\mathcal B$.", hold=0.2)
        self.play(plane.animate.set_opacity(0.22), run_time=0.6)
        self.add(self.b_grid)
        self.play(Create(self.b_grid, lag_ratio=0.01), run_time=1.4)
        self.play(GrowArrow(self.b_arrows[0]), GrowArrow(self.b_arrows[1]), FadeIn(self.b_labels), run_time=1.1, rate_func=spring_soft)
        self.x = x_arrow(plane)
        self.x_name = x_label(plane)
        self.play(GrowArrow(self.x), FadeIn(self.x_name), run_time=1.1, rate_func=spring_soft)
        self.wait(Timing.beat)

        self.b_walk = walk(plane, X_IN_B, (B1, B2), B_COLORS)
        line = self.say(r"Two steps of $\mathbf b_1$ and one of $\mathbf b_2$ reach $\mathbf x$.", line, hold=0.2)
        self.play(TransformFromCopy(self.b_arrows[0], self.b_walk[0]), run_time=1.1, rate_func=spring)
        self.play(TransformFromCopy(self.b_arrows[1], self.b_walk[1]), run_time=1.1, rate_func=spring)
        self.panel = side_panel()
        self.x_in_b = on_panel(address(r"[\mathbf x]_{\mathcal B}", X_IN_B, B_COLORS), 2.75)
        self.x_in_b.shift(LEFT * 1.15)
        self.play(FadeIn(self.panel), FadeIn(self.x_in_b, shift=LEFT * 0.2), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return line

    def add_c(self, plane, line):
        self.c_arrows, self.c_labels = c_parts(plane)
        self.c_grid = c_grid(plane)
        line = self.say(r"A second basis $\mathcal C$ lays another grid over the same plane.", line, hold=0.2)
        self.play(GrowArrow(self.c_arrows[0]), GrowArrow(self.c_arrows[1]), FadeIn(self.c_labels), run_time=1.1, rate_func=spring_soft)
        self.add(self.c_grid)
        self.bring_arrows_forward()
        self.play(Create(self.c_grid, lag_ratio=0.01), run_time=1.6)
        self.wait(Timing.read_short)
        return line

    def bring_arrows_forward(self):
        on_top = [self.b_walk, self.b_arrows, self.c_arrows, self.x, self.b_labels, self.c_labels, self.x_name]
        self.bring_to_front(*[m for m in on_top if m in self.mobjects])

    def grow_together(self, plane, line):
        growth = ValueTracker(0.0)
        self.play(FadeOut(self.b_walk), FadeOut(self.x), FadeOut(self.x_name), FadeOut(self.x_in_b[1].get_entries()), run_time=0.8)
        self.remove(self.x_in_b)
        b_frame = on_panel(address(r"[\mathbf x]_{\mathcal B}", X_IN_B, B_COLORS), 2.75).shift(LEFT * 1.15)
        c_frame = on_panel(address(r"[\mathbf x]_{\mathcal C}", X_IN_C, C_COLORS), 2.75).shift(RIGHT * 1.15)
        counters = VGroup(count_up(b_frame, growth, X_IN_B), count_up(c_frame, growth, X_IN_C))
        self.add(b_frame[0], b_frame[1].get_brackets())
        live = self.live_pictures(plane, growth)
        line = self.say(r"Grow $\mathbf x$ and read both addresses as it grows.", line, hold=0.2)
        self.play(FadeIn(c_frame[0]), FadeIn(c_frame[1].get_brackets()), run_time=0.6)
        self.add(live, counters)
        self.play(growth.animate.set_value(1), run_time=4.0, rate_func=smooth)
        self.wait(Timing.beat)
        self.remove(b_frame[0], b_frame[1].get_brackets(), c_frame[0], c_frame[1].get_brackets())
        return self.settle_growth(plane, live, counters, line)

    def live_pictures(self, plane, growth):
        def amount():
            return max(growth.get_value(), 0.004)

        return VGroup(
            always_redraw(lambda: walk(plane, X_IN_B, (B1, B2), B_COLORS, amount())),
            always_redraw(lambda: walk(plane, X_IN_C, (C1, C2), C_COLORS, amount())),
            always_redraw(lambda: x_arrow(plane, amount())),
        )

    def settle_growth(self, plane, live, counters, line):
        self.b_walk = walk(plane, X_IN_B, (B1, B2), B_COLORS)
        self.c_walk = walk(plane, X_IN_C, (C1, C2), C_COLORS)
        self.x = x_arrow(plane)
        self.remove(live)
        self.add(self.b_walk, self.c_walk, self.x)
        self.bring_arrows_forward()
        self.x_name = x_label(plane)
        self.x_in_b = on_panel(address(r"[\mathbf x]_{\mathcal B}", X_IN_B, B_COLORS), 2.75).shift(LEFT * 1.15)
        self.x_in_c = on_panel(address(r"[\mathbf x]_{\mathcal C}", X_IN_C, C_COLORS), 2.75).shift(RIGHT * 1.15)
        for number in counters.get_family():
            number.clear_updaters()
        self.add(self.x_in_b[0], self.x_in_b[1].get_brackets(), self.x_in_c[0], self.x_in_c[1].get_brackets())
        self.play(FadeOut(counters), FadeIn(self.x_in_b[1].get_entries()), FadeIn(self.x_in_c[1].get_entries()), FadeIn(self.x_name), run_time=0.5)
        self.adopt(self.x_in_b)
        self.adopt(self.x_in_c)

        dots = step_dots(plane, X_IN_C, (C1, C2), C_COLORS)
        line = self.say(r"In $\mathcal C$ it takes 7 steps of $\mathbf c_1$ and 4 of $\mathbf c_2$.", line, hold=0.2)
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in dots], lag_ratio=0.25), run_time=2.2)
        self.play(Indicate(self.x_in_c[1], color=Palette.glow, scale_factor=1.1), run_time=0.9)
        self.wait(Timing.beat)

        self.ring = Circle(radius=0.26, color=Palette.glow, stroke_width=4).move_to(plane.c2p(*X))
        line = self.say(r"The arrow stays put while each grid names it differently.", line, hold=0.2)
        self.play(FadeOut(dots), GrowFromCenter(self.ring), run_time=0.8, rate_func=spring)
        self.play(Indicate(self.x_in_b[1], color=Palette.glow, scale_factor=1.1), Indicate(self.x_in_c[1], color=Palette.glow, scale_factor=1.1), run_time=1.0)
        self.wait(Timing.read_short)
        return line

    def columns_of_p(self, plane, line):
        line = self.say(r"To translate, write each $\mathcal B$ vector in $\mathcal C$ coordinates.", line, hold=0.2)
        self.play(FadeOut(self.b_walk), FadeOut(self.c_walk), FadeOut(self.ring), self.x.animate.set_opacity(0.35), self.x_name.animate.set_opacity(0.35), run_time=0.7)
        self.p_label = MathTex(r"P_{\mathcal C \leftarrow \mathcal B}", "=", color=Palette.text, font_size=44)
        self.p_matrix = column_colored_matrix([["3", "1"], ["1", "2"]]).scale(0.85)
        p_row = on_panel(VGroup(self.p_label, self.p_matrix).arrange(RIGHT, buff=0.2), -1.25)
        self.recipes = VGroup()
        for index, (vector, weights, name, y) in enumerate(((B1, B1_IN_C, r"\mathbf b_1", 1.3), (B2, B2_IN_C, r"\mathbf b_2", 0.35))):
            steps = walk(plane, weights, (C1, C2), C_COLORS, stroke_width=5)
            equation = on_panel(recipe(name, B_COLORS[index], weights, (r"\mathbf c_1", r"\mathbf c_2"), C_COLORS), y)
            self.play(Indicate(self.b_arrows[index], color=Palette.glow, scale_factor=1.08), run_time=0.7)
            self.play(TransformFromCopy(self.c_arrows[0], steps[0]), run_time=1.0, rate_func=spring)
            self.play(TransformFromCopy(self.c_arrows[1], steps[1]), run_time=1.0, rate_func=spring)
            self.play(FadeIn(equation, shift=LEFT * 0.2), run_time=0.7, rate_func=spring_soft)
            self.recipes.add(equation)
            self.wait(Timing.beat)
            if index == 0:
                line = self.say(r"Those columns build the matrix $P_{\mathcal C \leftarrow \mathcal B}$.", line, hold=0.2)
                self.play(FadeIn(self.p_label), FadeIn(self.p_matrix.get_brackets()), run_time=0.6)
            column_entries = self.p_matrix.get_columns()[index]
            self.play(*[TransformFromCopy(weight, entry) for weight, entry in zip(equation.weights, column_entries)], run_time=1.2, rate_func=spring)
            self.play(FadeOut(steps), run_time=0.5)
        self.adopt(p_row)
        self.adopt(self.recipes)
        self.p_row = p_row
        self.wait(Timing.read_short)
        return line

    def combine_columns(self, line):
        product = VGroup(
            column_colored_matrix([["3", "1"], ["1", "2"]]).scale(0.8),
            colored_column(X_IN_B, B_COLORS).scale(0.8),
        ).arrange(RIGHT, buff=0.12)
        expansion = VGroup(
            MathTex("=", "2", color=Palette.text, font_size=40),
            colored_column(B1_IN_C, (Palette.i_hat, Palette.i_hat)).scale(0.8),
            MathTex("+", "1", color=Palette.text, font_size=40),
            colored_column(B2_IN_C, (Palette.j_hat, Palette.j_hat)).scale(0.8),
            MathTex("=", color=Palette.text, font_size=40),
            colored_column(X_IN_C, C_COLORS).scale(0.8),
        ).arrange(RIGHT, buff=0.2)
        expansion[0][1].set_color(Palette.i_hat)
        expansion[2][1].set_color(Palette.j_hat)
        product_name = MathTex(r"P_{\mathcal C \leftarrow \mathcal B}\,[\mathbf x]_{\mathcal B}", color=Palette.text, font_size=36)
        on_panel(product, 0.75)
        on_panel(product_name.next_to(product, UP, buff=0.2), product_name.get_y())
        on_panel(expansion, -0.75)
        line = self.say(r"Since $\mathbf x = 2\mathbf b_1 + \mathbf b_2$, the same weights combine the columns.", line, hold=0.2)
        self.play(FadeOut(self.recipes), FadeOut(self.p_label), run_time=0.5)
        self.play(Transform(self.p_matrix, product[0]), TransformFromCopy(self.x_in_b[1], product[1]), FadeIn(product_name), run_time=1.2, rate_func=spring_soft)
        self.remove(self.p_row)
        self.add(product)
        self.play(FadeIn(expansion[:4], shift=DOWN * 0.15), run_time=1.0, rate_func=spring_soft)
        self.play(FadeIn(expansion[4:], shift=LEFT * 0.15), run_time=0.8, rate_func=spring_soft)
        self.play(Indicate(expansion[5], color=Palette.glow, scale_factor=1.1), Indicate(self.x_in_c[1], color=Palette.glow, scale_factor=1.1), run_time=1.0)
        self.adopt(expansion)
        self.wait(Timing.read_short)
        return line

    def inverse(self, line):
        self.clear_panel()
        left = colored_column(X_IN_B, B_COLORS).scale(0.85).move_to(np.array([PANEL_X - 1.6, 1.0, 0]))
        right = colored_column(X_IN_C, C_COLORS).scale(0.85).move_to(np.array([PANEL_X + 1.6, 1.0, 0]))
        names = VGroup(
            MathTex(r"[\mathbf x]_{\mathcal B}", color=Palette.text, font_size=38).next_to(left, UP, buff=0.3),
            MathTex(r"[\mathbf x]_{\mathcal C}", color=Palette.text, font_size=38).next_to(right, UP, buff=0.3),
        )
        over = Arrow(left.get_right() + UP * 0.35 + RIGHT * 0.15, right.get_left() + UP * 0.35 + LEFT * 0.15, buff=0, color=Palette.text_muted, stroke_width=4, max_tip_length_to_length_ratio=0.12)
        back = Arrow(right.get_left() + DOWN * 0.35 + LEFT * 0.15, left.get_right() + DOWN * 0.35 + RIGHT * 0.15, buff=0, color=Palette.text_muted, stroke_width=4, max_tip_length_to_length_ratio=0.12)
        over_name = MathTex(r"P_{\mathcal C \leftarrow \mathcal B}", color=Palette.text, font_size=34).next_to(over, UP, buff=0.12)
        back_name = MathTex(r"P_{\mathcal B \leftarrow \mathcal C}", color=Palette.text, font_size=34).next_to(back, DOWN, buff=0.12)
        diagram = VGroup(left, right, names, over, over_name).set_z_index(6)
        line = self.say(r"Read the subscript right to left, from $\mathcal B$ into $\mathcal C$.", line, hold=0.2)
        self.play(FadeIn(diagram), run_time=0.9)
        self.play(over.animate.set_color(Palette.glow), run_time=0.8)
        self.wait(Timing.beat)

        formula = VGroup(
            MathTex(r"P_{\mathcal B \leftarrow \mathcal C}", "=", r"\big(P_{\mathcal C \leftarrow \mathcal B}\big)^{-1}", color=Palette.text, font_size=38),
            MathTex(r"=", r"\tfrac15", r"\begin{bmatrix} 2 & -1 \\ -1 & 3 \end{bmatrix}", color=Palette.text, font_size=38),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        on_panel(formula, -1.45)
        line = self.say(r"Its inverse translates back from $\mathcal C$ to $\mathcal B$.", line, hold=0.2)
        self.play(GrowArrow(back.set_z_index(6)), FadeIn(back_name.set_z_index(6)), run_time=0.9, rate_func=spring_soft)
        self.play(over.animate.set_color(Palette.text_muted), back.animate.set_color(Palette.glow), FadeIn(formula[0]), run_time=1.0)
        self.play(FadeIn(formula[1], shift=UP * 0.15), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Its columns are independent, so it is always invertible.", line, hold=Timing.read_short)
        self.adopt(VGroup(diagram, back, back_name, formula))
        return line

    def row_reduce(self, line):
        veil = scrim().set_z_index(20)
        start = augmented_block([[1, -1, 2, -1], [0, 1, 1, 2]], split=2)
        finish = augmented_block([[1, 0, 3, 1], [0, 1, 1, 2]], split=2)
        for mat, colors in ((start, (Palette.pink, Palette.blue, Palette.i_hat, Palette.j_hat)), (finish, (Palette.text, Palette.text, Palette.i_hat, Palette.j_hat))):
            for col, color in zip(mat.get_columns(), colors):
                col.set_color(color)
        step = VGroup(MathTex(r"\sim", color=Palette.text, font_size=56), MathTex(r"R_1 + R_2", color=Palette.text_muted, font_size=32)).arrange(DOWN, buff=0.15)
        row = VGroup(start, step, finish.copy()).arrange(RIGHT, buff=0.6).scale(1.15).move_to(UP * 0.5)
        finish.scale(1.15).move_to(row[2])
        heads = VGroup(*[
            MathTex(name, color=color, font_size=40).next_to(col, UP, buff=0.35)
            for name, color, col in zip((r"\mathbf c_1", r"\mathbf c_2", r"\mathbf b_1", r"\mathbf b_2"), (Palette.pink, Palette.blue, Palette.i_hat, Palette.j_hat), start.get_columns())
        ])
        heads.align_to(heads[0], DOWN)
        stage = VGroup(start, step, heads).set_z_index(21)
        line = self.say(r"With real vectors, row reduce $[\,\mathbf c_1\ \mathbf c_2 \mid \mathbf b_1\ \mathbf b_2\,]$.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.7)
        self.play(FadeIn(start), FadeIn(heads, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        self.play(FadeIn(step), run_time=0.5)
        reduced = start.copy().set_z_index(21)
        self.add(reduced)
        self.play(reduced.animate.move_to(finish), run_time=1.0, rate_func=spring_soft)
        morph_matrix(self, reduced, finish.set_z_index(21), run_time=1.2)
        self.wait(Timing.beat)

        right_block = VGroup(*reduced.get_columns()[2:])
        brace = Brace(right_block, DOWN, color=Palette.text_muted).set_z_index(21)
        brace_name = MathTex(r"P_{\mathcal C \leftarrow \mathcal B}", color=Palette.text, font_size=40).next_to(brace, DOWN, buff=0.15).set_z_index(21)
        line = self.say(r"The basis you translate into goes on the left.", line, hold=0.2)
        self.play(Indicate(heads[:2], color=Palette.glow, scale_factor=1.15), run_time=1.0)
        self.play(Indicate(right_block, color=Palette.glow, scale_factor=1.1), GrowFromCenter(brace), FadeIn(brace_name), run_time=1.0)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(stage, reduced, brace, brace_name)), run_time=0.6)
        self.veil = veil
        return line

    def map_in_b(self, plane, line):
        leaving = [m for m in self.mobjects if 6 <= m.z_index < 20] + [self.c_grid, self.c_arrows, self.c_labels, self.x, self.x_name]
        self.remove(*[part for m in leaving for part in m.get_family()])
        a_row = on_panel(VGroup(MathTex(r"T(\mathbf x) = A\mathbf x,\quad A =", color=Palette.text, font_size=38), matrix([["1", "2"], ["1", "0"]]).scale(0.8)).arrange(RIGHT, buff=0.2).scale(0.9), 2.7)
        self.play(FadeOut(self.veil), run_time=0.8)
        line = self.say(r"Change of basis also rewrites the matrix of a map.", line, hold=0.2)
        self.play(FadeIn(a_row, shift=LEFT * 0.2), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)

        images = VGroup(vector_arrow(T_B1, Palette.teal, plane), vector_arrow(T_B2, Palette.teal, plane))
        image_names = VGroup(
            name_label(r"T(\mathbf b_1)", Palette.teal, plane.c2p(*T_B1), UR),
            name_label(r"T(\mathbf b_2)", Palette.teal, plane.c2p(*T_B2), RIGHT),
        )
        back_step = arrow_between(plane, B1, T_B2, Palette.j_hat, stroke_width=5)
        equations = VGroup(
            recipe(r"T(\mathbf b_1)", Palette.teal, (2, 0), (r"\mathbf b_1", r"\mathbf b_2"), B_COLORS, font_size=38),
            recipe(r"T(\mathbf b_2)", Palette.teal, (1, -1), (r"\mathbf b_1", r"\mathbf b_2"), B_COLORS, font_size=38),
        )
        on_panel(equations[0], 1.25)
        on_panel(equations[1], 0.35)
        line = self.say(r"$T$ doubles $\mathbf b_1$ and sends $\mathbf b_2$ to $\mathbf b_1 - \mathbf b_2$.", line, hold=0.2)
        self.play(TransformFromCopy(self.b_arrows[0], images[0]), FadeIn(image_names[0]), run_time=1.2, rate_func=spring)
        self.bring_to_front(self.b_arrows, self.b_labels)
        self.play(FadeIn(equations[0], shift=LEFT * 0.2), run_time=0.6)
        self.play(TransformFromCopy(self.b_arrows[1], images[1]), FadeIn(image_names[1]), run_time=1.2, rate_func=spring)
        self.play(Indicate(self.b_arrows[0], color=Palette.glow, scale_factor=1.08), run_time=0.7)
        self.play(Create(back_step), run_time=0.9)
        self.play(FadeIn(equations[1], shift=LEFT * 0.2), run_time=0.6)
        self.wait(Timing.beat)

        t_matrix = column_colored_matrix([["2", "1"], ["0", "-1"]], (Palette.teal, Palette.teal)).scale(0.85)
        t_row = on_panel(VGroup(MathTex(r"[T]_{\mathcal B}", "=", color=Palette.text, font_size=44), t_matrix).arrange(RIGHT, buff=0.2), -1.3)
        line = self.say(r"In $\mathcal B$ coordinates, $T$ has a simpler matrix.", line, hold=0.2)
        self.play(FadeIn(t_row[0]), FadeIn(t_matrix.get_brackets()), run_time=0.6)
        for index in range(2):
            self.play(*[FadeTransform(weight.copy(), entry) for weight, entry in zip(equations[index].weights, t_matrix.get_columns()[index])], run_time=1.1, rate_func=spring_soft)
        self.adopt(t_row)
        self.wait(Timing.read_short)
        return line

    def similarity_square(self, line):
        veil = scrim().set_z_index(20)
        square = similarity_square().set_z_index(21)
        nodes, edges, formula = square.nodes, square.edges, square.formula
        line = self.say(r"Go to standard coordinates with $P$, apply $A$, then come back.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.7)
        self.play(FadeIn(nodes), FadeIn(edges), run_time=1.0)
        self.play(FadeIn(formula[:2]), run_time=0.5)
        for edge, part in zip(edges[:3], (formula[4], formula[3], formula[2])):
            self.play(edge[0].animate.set_color(Palette.glow), FadeIn(part, shift=UP * 0.1), run_time=1.2)
        self.wait(Timing.beat)
        self.play(Indicate(edges[3], color=Palette.glow, scale_factor=1.05), Indicate(formula, color=Palette.glow, scale_factor=1.06), run_time=1.0)
        numbers = similarity_numbers().set_z_index(21).next_to(formula, DOWN, buff=0.35)
        line = self.say(r"So $[T]_{\mathcal B} = P^{-1}AP$, and the two matrices are similar.", line, hold=0.2)
        self.play(FadeIn(numbers, shift=UP * 0.15), run_time=0.9, rate_func=spring_soft)
        self.remove(*[m for m in self.mobjects if m.z_index < 20])
        self.wait(Timing.read_long)
        return line


def square_node(tex_string, color, point):
    return MathTex(tex_string, color=color, font_size=50).move_to(point)


def square_edge(start, end, name, side):
    arrow = Arrow(start, end, buff=0.2, color=Palette.text_muted, stroke_width=5, max_tip_length_to_length_ratio=0.1)
    label = MathTex(name, color=Palette.text, font_size=44).next_to(arrow, side, buff=0.18)
    return VGroup(arrow, label)


def level(point, corner, axis):
    """`point` with coordinate `axis` taken from the corner, so square edges stay straight."""
    straight = np.array(point, dtype=float)
    straight[axis] = corner[axis]
    return straight


def similarity_square():
    corners = {"bl": np.array([-3.0, 0.45, 0]), "tl": np.array([-3.0, 2.95, 0]), "tr": np.array([3.0, 2.95, 0]), "br": np.array([3.0, 0.45, 0])}
    nodes = VGroup(
        square_node(r"[\mathbf x]_{\mathcal B}", Palette.yellow, corners["bl"]),
        square_node(r"\mathbf x", Palette.yellow, corners["tl"]),
        square_node(r"A\mathbf x", Palette.teal, corners["tr"]),
        square_node(r"[A\mathbf x]_{\mathcal B}", Palette.teal, corners["br"]),
    )
    edges = VGroup(
        square_edge(level(nodes[0].get_top(), corners["bl"], 0), level(nodes[1].get_bottom(), corners["tl"], 0), "P", LEFT),
        square_edge(level(nodes[1].get_right(), corners["tl"], 1), level(nodes[2].get_left(), corners["tr"], 1), "A", UP),
        square_edge(level(nodes[2].get_bottom(), corners["tr"], 0), level(nodes[3].get_top(), corners["br"], 0), "P^{-1}", RIGHT),
        square_edge(level(nodes[0].get_right(), corners["bl"], 1), level(nodes[3].get_left(), corners["br"], 1), r"[T]_{\mathcal B}", DOWN),
    )
    formula = MathTex(r"[T]_{\mathcal B}", "=", "P^{-1}", "A", "P", color=Palette.text, font_size=56).move_to(DOWN * 0.95)
    square = VGroup(nodes, edges, formula)
    square.nodes, square.edges, square.formula = nodes, edges, formula
    return square


def similarity_numbers():
    return MathTex(
        r"\tfrac15\begin{bmatrix} 2 & 1 \\ -1 & 2 \end{bmatrix}"
        r"\begin{bmatrix} 1 & 2 \\ 1 & 0 \end{bmatrix}"
        r"\begin{bmatrix} 2 & -1 \\ 1 & 2 \end{bmatrix}"
        r"= \begin{bmatrix} 2 & 1 \\ 0 & -1 \end{bmatrix}",
        color=Palette.text,
        font_size=36,
    )


def two_grid_picture(scene, plane):
    arrows_b, labels_b = b_parts(plane)
    arrows_c, labels_c = c_parts(plane)
    scene.add(
        plane.set_opacity(0.22),
        b_grid(plane),
        c_grid(plane),
        walk(plane, X_IN_B, (B1, B2), B_COLORS),
        walk(plane, X_IN_C, (C1, C2), C_COLORS),
        step_dots(plane, X_IN_C, (C1, C2), C_COLORS),
        arrows_b,
        arrows_c,
        x_arrow(plane),
        labels_b,
        labels_c,
        x_label(plane),
        Circle(radius=0.26, color=Palette.glow, stroke_width=4).move_to(plane.c2p(*X)),
    )


class FigTwoGrids(Scene):
    def construct(self):
        plane = plane_at(FIG_ORIGIN, FIG_UNIT)
        two_grid_picture(self, plane)
        self.add(side_panel())
        self.add(on_panel(address(r"[\mathbf x]_{\mathcal B}", X_IN_B, B_COLORS, font_size=48), 1.3))
        self.add(on_panel(address(r"[\mathbf x]_{\mathcal C}", X_IN_C, C_COLORS, font_size=48), -1.1))


class FigColumns(Scene):
    def construct(self):
        plane = plane_at(FIG_ORIGIN, FIG_UNIT)
        arrows_b, labels_b = b_parts(plane)
        arrows_c, labels_c = c_parts(plane)
        self.add(
            plane.set_opacity(0.22),
            c_grid(plane),
            walk(plane, B1_IN_C, (C1, C2), C_COLORS),
            walk(plane, B2_IN_C, (C1, C2), C_COLORS),
            arrows_c,
            arrows_b,
            labels_c,
            labels_b,
            side_panel(),
        )
        self.add(on_panel(recipe(r"\mathbf b_1", Palette.i_hat, B1_IN_C, (r"\mathbf c_1", r"\mathbf c_2"), C_COLORS, font_size=44), 2.0))
        self.add(on_panel(recipe(r"\mathbf b_2", Palette.j_hat, B2_IN_C, (r"\mathbf c_1", r"\mathbf c_2"), C_COLORS, font_size=44), 0.9))
        p_row = VGroup(MathTex(r"P_{\mathcal C \leftarrow \mathcal B}", "=", color=Palette.text, font_size=48), column_colored_matrix([["3", "1"], ["1", "2"]]).scale(0.9))
        self.add(on_panel(p_row.arrange(RIGHT, buff=0.2), -1.0))


class FigSimilarity(Scene):
    def construct(self):
        square = similarity_square()
        self.add(square, similarity_numbers().next_to(square.formula, DOWN, buff=0.35))
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = plane_at(FIG_ORIGIN, FIG_UNIT)
        two_grid_picture(self, plane)
        self.add(side_panel())
        self.add(on_panel(address(r"[\mathbf x]_{\mathcal B}", X_IN_B, B_COLORS, font_size=52), 1.3))
        self.add(on_panel(address(r"[\mathbf x]_{\mathcal C}", X_IN_C, C_COLORS, font_size=52), -1.1))
