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
    column,
    fit_to_frame,
    make_plane,
    matrix,
    morph_matrix,
    plane_at,
    plate_for,
    scrim,
    skewed_grid,
    spring,
    spring_soft,
    vector_arrow,
)

A = ((2, 1), (1, 1))
A_INV = ((1, -1), (-1, 2))
X = (1, 1)
B = (4, 3)
X_SOLVED = (1, 2)
SHEAR = ((1, 1), (0, 1))
SHEAR_INV = ((1, -1), (0, 1))
QUARTER_TURN = PI / 2
SINGULAR = ((1, 2), (2, 4))
PREIMAGES = ((1, 0), (-1, 1), (3, -1))
SHARED_IMAGE = (1, 2)
PLANE_ORIGIN = (-0.6, -1.2)
PLANE_UNIT = 0.8
BASIS_COLORS = (Palette.i_hat, Palette.j_hat)


def tex(*parts, colors=(), font_size=48):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def basis_matrix(rows):
    """A matrix whose first column is green and second column red, like the arrows they record."""
    mat = matrix([[str(entry) for entry in row] for row in rows])
    for index, color in enumerate(BASIS_COLORS):
        mat.get_columns()[index].set_color(color)
    return mat


def pink_matrix(rows):
    return matrix([[str(entry) for entry in row] for row in rows], color=Palette.pink)


def named(name_parts, mat, colors=()):
    return VGroup(tex(*name_parts, "=", colors=colors), mat).arrange(RIGHT, buff=0.2)


def identity():
    return matrix([["1", "0"], ["0", "1"]])


def product_line(left, right, left_name, right_name):
    return VGroup(tex(*left_name, *right_name, "="), left, right, tex("="), identity()).arrange(RIGHT, buff=0.18)


def definition_products():
    forward = product_line(basis_matrix(A), pink_matrix(A_INV), ["A"], [r"A^{-1}"])
    backward = product_line(pink_matrix(A_INV), basis_matrix(A), [r"A^{-1}"], ["A"])
    forward[0][1].set_color(Palette.pink)
    backward[0][0].set_color(Palette.pink)
    return VGroup(forward, backward).arrange(DOWN, buff=0.6)


def formula_row():
    work_slot = pink_matrix(A_INV)
    fraction = MathTex(r"\frac{1}{2\cdot 1 - 1\cdot 1}", color=Palette.text, font_size=48)
    return VGroup(tex(r"A^{-1}", "=", colors=(Palette.pink,)), fraction, work_slot, tex("="), pink_matrix(A_INV)).arrange(RIGHT, buff=0.3)


def general_formula():
    return MathTex(
        r"\begin{bmatrix} a & b \\ c & d \end{bmatrix}^{-1}",
        "=",
        r"\frac{1}{ad - bc}",
        r"\begin{bmatrix} d & -b \\ -c & a \end{bmatrix}",
        color=Palette.text,
        font_size=54,
    )


LIVE_GRID_OPACITY = 0.15
LIVE_GRID_WIDTH = 4.0
LIVE_AXIS_OPACITY = 0.7
LIVE_AXIS_WIDTH = 2.0


def styled_like_live_grid(plane):
    """Draw the opening grid exactly as the live grid will look, so the swap between them costs no crossfade."""
    plane.background_lines.set_stroke(color=Palette.grid, width=LIVE_GRID_WIDTH, opacity=LIVE_GRID_OPACITY)
    plane.faded_lines.set_stroke(opacity=0)
    plane.axes.set_stroke(color=Palette.axis, width=LIVE_AXIS_WIDTH, opacity=LIVE_AXIS_OPACITY)
    return plane


def live_arrow(plane, live, coords, color, stroke_width=6):
    return always_redraw(lambda: vector_arrow(live.point(coords), color, plane, stroke_width=stroke_width))


def live_dot(plane, live, coords, color):
    return always_redraw(lambda: Dot(plane.c2p(*live.point(coords)), radius=0.09, color=color))


def live_axes(plane, live):
    def draw():
        lines = VGroup()
        for index in range(2):
            direction = live.value[:, index]
            if np.linalg.norm(direction) > 1e-6:
                far = 60 * direction
                lines.add(Line(plane.c2p(*-far), plane.c2p(*far), color=Palette.axis, stroke_width=LIVE_AXIS_WIDTH, stroke_opacity=LIVE_AXIS_OPACITY))
        return lines

    return always_redraw(draw)


def stamp(plane, coords):
    return Dot(plane.c2p(*coords), radius=0.09, color=Palette.glow)


def ring(plane, coords, color=Palette.glow):
    return Circle(radius=0.22, color=color, stroke_width=4).move_to(plane.c2p(*coords))


def name_label(parts, colors, anchor, direction, font_size=40):
    return backed(tex(*parts, colors=colors, font_size=font_size)).next_to(anchor, direction, buff=0.12)


class Lesson(LessonScene):
    day = 7
    title = "The inverse of a matrix"

    def construct(self):
        plane = styled_like_live_grid(plane_at(PLANE_ORIGIN, PLANE_UNIT))
        self.plane = plane
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.meet_a()
        line = self.play_backwards(line)
        line = self.inverse_columns(line)
        line = self.definition_and_formula(line)
        line = self.solve_with_inverse(line)
        line = self.socks_and_shoes(line)
        line = self.singular(line)
        self.close_episode(
            r"$A^{-1}$ is the transformation that undoes $A$.\\"
            r"It exists exactly when $A$ does not flatten the plane.",
            *self.mobjects,
        )

    def set_panel(self, content, run_time=0.7):
        """Swap the top-left panel's content, growing its plate to fit."""
        content.to_corner(UL, buff=0.6)
        new_plate = plate_for(content)
        if getattr(self, "panel", None) is None:
            self.plate = new_plate
            self.play(FadeIn(self.plate), FadeIn(content, shift=DOWN * 0.1), run_time=run_time)
        else:
            self.play(FadeOut(self.panel), self.plate.animate.become(new_plate), run_time=0.5)
            self.play(FadeIn(content, shift=DOWN * 0.1), run_time=run_time, rate_func=spring_soft)
        self.panel = content

    def clear_panel(self):
        self.play(FadeOut(self.panel), FadeOut(self.plate), run_time=0.5)
        self.panel = None

    def start_live_grid(self):
        plane = self.plane
        self.live = LiveTransform()
        self.grid = always_redraw(lambda: self.live.grid(plane, opacity=LIVE_GRID_OPACITY, cap=20).set_stroke(width=LIVE_GRID_WIDTH))
        self.axes = live_axes(plane, self.live)
        self.basis = VGroup(live_arrow(plane, self.live, (1, 0), Palette.i_hat), live_arrow(plane, self.live, (0, 1), Palette.j_hat))
        self.remove(plane)
        self.add(self.grid, self.axes)
        self.play(*[GrowArrow(arrow) for arrow in self.basis], run_time=1.0, rate_func=spring_soft)

    def move(self, animation, run_time=1.8, rate_func=spring_soft):
        self.play(animation, run_time=run_time, rate_func=rate_func)

    def meet_a(self):
        line = self.say(r"Here is a matrix $A$ and a point $\mathbf x$.", hold=0.2)
        self.set_panel(named(["A"], basis_matrix(A)))
        self.start_live_grid()
        self.x_arrow = live_arrow(self.plane, self.live, X, Palette.yellow)
        self.x_name = name_label([r"\mathbf x"], [Palette.yellow], self.plane.c2p(*X), UR)
        self.play(GrowArrow(self.x_arrow), FadeIn(self.x_name), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)

        line = self.say(r"$A$ moves every point of the plane.", line, hold=0.2)
        self.play(FadeOut(self.x_name), run_time=0.3)
        self.move(self.live.apply(A), run_time=2.0)
        self.ax_stamp = stamp(self.plane, (3, 2))
        self.ax_name = name_label([r"A\mathbf x"], [Palette.yellow], self.plane.c2p(3, 2), UR)
        self.play(GrowFromCenter(self.ax_stamp), FadeIn(self.ax_name), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        return line

    def play_backwards(self, line):
        line = self.say(r"Can we play that motion backwards?", line, hold=Timing.beat)
        self.play(FadeOut(self.ax_name), FadeOut(self.ax_stamp), run_time=0.3)
        self.move(self.live.apply(np.linalg.inv(A)), run_time=2.6)
        home = stamp(self.plane, X)
        self.play(GrowFromCenter(home), run_time=0.5, rate_func=spring)
        self.wait(Timing.beat)

        line = self.say(r"The matrix that undoes $A$ is its inverse, $A^{-1}$.", line, hold=0.2)
        both = VGroup(named(["A"], basis_matrix(A)), named([r"A^{-1}"], pink_matrix(A_INV), colors=(Palette.pink,))).arrange(RIGHT, buff=0.6)
        self.set_panel(both)
        self.play(FadeOut(home), run_time=0.4)
        self.wait(Timing.read_short)
        return line

    def inverse_columns(self, line):
        line = self.say(r"Its columns are the points $A$ sends to $\hat\imath$ and $\hat\jmath$.", line, hold=0.2)
        inverse_columns = self.panel[1][1].get_columns()
        self.inverse_arrows = VGroup(
            live_arrow(self.plane, self.live, (1, -1), Palette.pink, stroke_width=5),
            live_arrow(self.plane, self.live, (-1, 2), Palette.pink, stroke_width=5),
        )
        for col, arrow in zip(inverse_columns, self.inverse_arrows):
            self.play(Indicate(col, color=Palette.glow, scale_factor=1.12), run_time=0.7)
            self.play(GrowArrow(arrow), run_time=1.0, rate_func=spring_soft)
        self.play(FadeOut(self.x_arrow), run_time=0.4)
        self.move(self.live.apply(A), run_time=2.0)
        marks = VGroup(stamp(self.plane, (1, 0)), stamp(self.plane, (0, 1)))
        self.play(LaggedStart(*[GrowFromCenter(mark) for mark in marks], lag_ratio=0.3), run_time=0.7)
        self.wait(Timing.read_short)
        self.play(FadeOut(marks), run_time=0.3)
        return line

    def definition_and_formula(self, line):
        veil = scrim()
        products = definition_products().move_to(UP * 0.5)
        line = self.say(r"Undo after $A$, or $A$ after undo: both give $I$.", line, hold=0.2)
        self.add(veil)
        self.bring_to_front(line)
        self.play(FadeIn(veil), FadeOut(self.panel), FadeOut(self.plate), run_time=0.7)
        self.panel = None
        self.reset_behind_scrim()
        for product in products:
            self.play(FadeIn(VGroup(*product[:3])), run_time=0.9)
            self.play(FadeIn(product[3]), FadeIn(product[4], shift=LEFT * 0.3), run_time=0.9, rate_func=spring)
            self.wait(0.5)
        self.wait(Timing.read_short)
        self.play(FadeOut(products), run_time=0.6)
        line = self.formula(line)
        self.play(FadeOut(veil), run_time=0.7)
        return line

    def reset_behind_scrim(self):
        """While the scrim hides the plane, return the grid to the identity without spending motion on it."""
        self.remove(*self.inverse_arrows)
        self.live.apply(np.linalg.inv(self.live.value))
        self.live.progress.set_value(1)

    def formula(self, line):
        general = general_formula().move_to(UP * 2.0)
        row = formula_row().move_to(DOWN * 0.8)
        start = named(["A"], basis_matrix(A))
        start.shift(row[2].get_center() - start[1].get_center())
        line = self.say(r"A $2\times 2$ inverse has a formula.", line, hold=0.2)
        self.play(Write(general), run_time=1.6)
        self.play(FadeIn(start), run_time=0.7)

        line = self.say(r"Swap the diagonal and flip the other two signs.", line, hold=0.2)
        self.play(FadeOut(start[0]), run_time=0.4)
        self.remove(start)
        self.add(start[1])
        work = self.swap_diagonal(start[1], row[2])
        self.flip_signs(work, row[2])
        self.wait(Timing.beat)

        line = self.say(r"Then divide by $ad - bc$, the determinant.", line, hold=0.2)
        self.play(Indicate(general[2], color=Palette.glow, scale_factor=1.1), run_time=0.9)
        self.play(FadeIn(row[0]), FadeIn(row[1], shift=DOWN * 0.2), run_time=0.9, rate_func=spring_soft)
        self.play(FadeIn(row[3]), FadeIn(row[4], shift=LEFT * 0.3), run_time=0.9, rate_func=spring)
        self.wait(Timing.read_short)

        line = self.say(r"When $ad - bc = 0$, the formula divides by zero.", line, hold=0.2)
        self.play(Circumscribe(general[2], color=Palette.glow, buff=0.1), run_time=1.2)
        self.wait(Timing.read_short)
        self.play(FadeOut(general), FadeOut(VGroup(row[0], row[1], row[3], row[4], work)), run_time=0.6)
        return line

    def swap_diagonal(self, work, slot):
        entries = work.get_entries()
        top_left, bottom_right = entries[0], entries[3]
        swapped = basis_matrix(((1, 1), (1, 2))).move_to(slot)
        before = list(self.mobjects)
        self.play(
            top_left.animate.move_to(swapped.get_entries()[3]).set_color(Palette.j_hat),
            bottom_right.animate.move_to(swapped.get_entries()[0]).set_color(Palette.i_hat),
            work.get_brackets().animate.become(swapped.get_brackets()),
            path_arc=PI / 2,
            run_time=1.2,
            rate_func=spring_soft,
        )
        self.remove(work, *[mob for mob in self.mobjects if mob not in before])
        self.add(swapped)
        return swapped

    def flip_signs(self, work, slot):
        target = basis_matrix(A_INV).move_to(slot)
        morph_matrix(self, work, target, run_time=0.9)
        self.play(work.animate.set_color(Palette.pink), run_time=0.6)

    def solve_with_inverse(self, line):
        plane = self.plane
        tint = ValueTracker(0)
        self.b_arrow = always_redraw(
            lambda: vector_arrow(self.live.point(B), interpolate_color(ManimColor(Palette.teal), ManimColor(Palette.yellow), tint.get_value()), plane)
        )
        b_ring = ring(plane, B, Palette.teal)
        b_name = name_label([r"\mathbf b"], [Palette.teal], plane.c2p(*B), UR)
        line = self.say(r"To solve $A\mathbf x = \mathbf b$, send $\mathbf b$ back through $A^{-1}$.", line, hold=0.2)
        self.set_panel(named([r"A^{-1}"], pink_matrix(A_INV), colors=(Palette.pink,)))
        self.play(GrowArrow(self.b_arrow), Create(b_ring), FadeIn(b_name), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.beat)
        self.move(self.live.apply(A_INV), run_time=2.2)
        self.play(tint.animate.set_value(1), run_time=0.6)
        x_name = name_label([r"\mathbf x"], [Palette.yellow], plane.c2p(*X_SOLVED), LEFT)
        answer = VGroup(
            tex(r"\mathbf x", "=", r"A^{-1}", r"\mathbf b", "=", colors=(Palette.yellow, None, Palette.pink, Palette.teal)),
            pink_matrix(A_INV),
            column(B, color=Palette.teal),
            tex("="),
            column(X_SOLVED, color=Palette.yellow),
        ).arrange(RIGHT, buff=0.18)
        self.set_panel(answer)
        self.play(FadeIn(x_name), run_time=0.5)
        self.wait(Timing.read_short)

        line = self.say(r"As a check, $A$ sends $\mathbf x$ forward onto $\mathbf b$.", line, hold=0.2)
        self.play(FadeOut(x_name), run_time=0.3)
        self.move(self.live.apply(A), run_time=1.8)
        self.play(tint.animate.set_value(0), Indicate(b_ring, color=Palette.teal, scale_factor=1.3), run_time=0.8)
        line = self.say(r"$A^{-1}$ gives one answer, so the solution is unique.", line, hold=Timing.read_short)
        self.play(FadeOut(self.b_arrow), FadeOut(b_ring), FadeOut(b_name), run_time=0.6)
        return line

    def socks_and_shoes(self, line):
        plane = self.plane
        self.x_arrow = live_arrow(plane, self.live, X, Palette.yellow)
        home = ring(plane, X)
        moves = VGroup(named(["S"], basis_matrix(SHEAR)), named(["R"], basis_matrix(((0, -1), (1, 0))))).arrange(RIGHT, buff=0.6)
        line = self.say(r"Shear with $S$, then turn with $R$: that is $RS$.", line, hold=0.2)
        self.set_panel(moves)
        self.play(GrowArrow(self.x_arrow), Create(home), run_time=0.9, rate_func=spring_soft)
        self.move(self.live.apply(SHEAR), run_time=1.3)
        self.move(self.live.rotate(QUARTER_TURN), run_time=1.3)
        self.wait(Timing.beat)

        line = self.say(r"Undoing the shear first leaves the grid skewed.", line, hold=0.2)
        self.move(self.live.apply(SHEAR_INV), run_time=1.3)
        self.move(self.live.rotate(-QUARTER_TURN), run_time=1.3)
        self.play(Flash(plane.c2p(*self.live.point(X)), color=Palette.glow, line_length=0.25), run_time=0.8)
        self.wait(Timing.read_short)
        turn_then_shear = np.array(((0, -1), (1, 0))) @ np.array(SHEAR)
        self.move(self.live.apply(turn_then_shear @ np.linalg.inv(self.live.value)), run_time=1.2)

        line = self.say(r"Undo the turn first, then the shear.", line, hold=0.2)
        self.move(self.live.rotate(-QUARTER_TURN), run_time=1.3)
        self.move(self.live.apply(SHEAR_INV), run_time=1.3)
        self.play(home.animate.set_color(Palette.teal), Flash(plane.c2p(*X), color=Palette.teal, line_length=0.25), run_time=0.8)
        self.wait(Timing.beat)

        rule = VGroup(
            tex(r"(RS)^{-1}", "=", r"S^{-1}R^{-1}"),
            tex(r"(AB)^{-1}", "=", r"B^{-1}A^{-1}"),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        line = self.say(r"Shoes come off before socks, so the order reverses.", line, hold=0.2)
        self.set_panel(rule)
        self.wait(Timing.read_long)
        self.play(FadeOut(self.x_arrow), FadeOut(home), run_time=0.5)
        return line

    def singular(self, line):
        plane = self.plane
        panel = VGroup(named(["M"], matrix([["1", "2"], ["2", "4"]])), tex(r"\det M", "=", r"1\cdot 4 - 2\cdot 2", "=", "0", colors=(None, None, None, None, Palette.glow))).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        line = self.say(r"When $ad - bc = 0$, the plane flattens onto a line.", line, hold=0.2)
        self.set_panel(panel)
        ghosts = VGroup(*[Dot(plane.c2p(*point), radius=0.09, color=Palette.yellow, fill_opacity=0.35) for point in PREIMAGES])
        dots = VGroup(*[live_dot(plane, self.live, point, Palette.yellow) for point in PREIMAGES])
        preimage_line = DashedLine(plane.c2p(5, -2), plane.c2p(-3, 2), color=Palette.text_muted, stroke_width=3)
        self.play(Create(preimage_line), LaggedStart(*[GrowFromCenter(dot) for dot in dots], lag_ratio=0.3), run_time=1.2)
        self.add(ghosts)
        self.bring_to_front(dots)
        self.move(self.live.apply(SINGULAR), run_time=2.2)
        self.wait(Timing.beat)

        line = self.say(r"Three different points land on the same spot.", line, hold=0.2)
        landing = stamp(plane, SHARED_IMAGE)
        self.play(GrowFromCenter(landing), Flash(plane.c2p(*SHARED_IMAGE), color=Palette.glow, line_length=0.25), run_time=0.8)
        self.wait(Timing.read_short)

        line = self.say(r"Going back would need three answers, so no inverse exists.", line, hold=0.2)
        paths = VGroup(*[DashedLine(plane.c2p(*SHARED_IMAGE), plane.c2p(*point), color=Palette.glow, stroke_width=3).add_tip(tip_length=0.18) for point in PREIMAGES])
        self.play(LaggedStart(*[Create(path) for path in paths], lag_ratio=0.25), ghosts.animate.set_opacity(1), run_time=1.6)
        self.wait(Timing.read_long)
        return line


def forward_back_panel(start_label, grid_matrix, point, point_color):
    plane = make_plane(x_range=(-2, 5, 1), y_range=(-2, 4, 1))
    live = LiveTransform(grid_matrix)
    layers = VGroup(plane)
    layers.add(skewed_grid(plane, live.value[:, 0], live.value[:, 1], reach=20, color=Palette.blue, opacity=0.7))
    layers.add(vector_arrow(live.point((1, 0)), Palette.i_hat, plane), vector_arrow(live.point((0, 1)), Palette.j_hat, plane))
    image = live.point(point)
    layers.add(vector_arrow(image, point_color, plane), stamp(plane, image))
    layers.add(name_label(start_label, [point_color], plane.c2p(*image), UR))
    return layers


class FigUndo(Scene):
    def construct(self):
        before = forward_back_panel([r"\mathbf x"], np.eye(2), X, Palette.yellow)
        after = forward_back_panel([r"A\mathbf x"], A, X, Palette.teal)
        forward = VGroup(Arrow(LEFT, RIGHT, color=Palette.text, buff=0), tex("A", font_size=56))
        backward = VGroup(Arrow(RIGHT, LEFT, color=Palette.pink, buff=0), tex(r"A^{-1}", colors=(Palette.pink,), font_size=56))
        forward[1].next_to(forward[0], UP, buff=0.15)
        backward[1].next_to(backward[0], DOWN, buff=0.15)
        middle = VGroup(forward, backward).arrange(DOWN, buff=0.8)
        self.add(VGroup(before, middle, after).arrange(RIGHT, buff=0.6))
        fit_to_frame(self)


class FigFormula(Scene):
    def construct(self):
        general = general_formula()
        example = VGroup(
            tex(r"A^{-1}", "=", colors=(Palette.pink,)),
            MathTex(r"\frac{1}{2\cdot 1 - 1\cdot 1}", color=Palette.text, font_size=48),
            matrix([["1", "-1"], ["-1", "2"]]),
            tex("="),
            pink_matrix(A_INV),
        ).arrange(RIGHT, buff=0.2)
        example[2].get_entries()[0].set_color(Palette.j_hat)
        example[2].get_entries()[3].set_color(Palette.i_hat)
        self.add(VGroup(general, example).arrange(DOWN, buff=0.9))
        fit_to_frame(self, margin=0.8)


def mini_grid(grid_matrix, point_color=Palette.yellow):
    plane = make_plane(x_range=(-3, 3, 1), y_range=(-3, 3, 1))
    live = LiveTransform(grid_matrix)
    return VGroup(
        plane.set_stroke(opacity=0.3),
        skewed_grid(plane, live.value[:, 0], live.value[:, 1], reach=12, color=Palette.blue, opacity=0.8),
        vector_arrow(live.point((1, 0)), Palette.i_hat, plane),
        vector_arrow(live.point((0, 1)), Palette.j_hat, plane),
        vector_arrow(live.point(X), point_color, plane),
    )


def labelled_hop(label_tex, color, direction):
    arrow = Arrow(LEFT * 0.7, RIGHT * 0.7, color=color, buff=0) if direction == "forward" else Arrow(RIGHT * 0.7, LEFT * 0.7, color=color, buff=0)
    label = tex(label_tex, font_size=48).set_color(color)
    label.next_to(arrow, UP if direction == "forward" else DOWN, buff=0.12)
    return VGroup(arrow, label)


class FigUndoOrder(Scene):
    def construct(self):
        turn = ((0, -1), (1, 0))
        sheared = np.array(SHEAR, dtype=float)
        grids = VGroup(mini_grid(np.eye(2)), mini_grid(sheared), mini_grid(np.array(turn) @ sheared))
        hops = [
            VGroup(labelled_hop("S", Palette.text, "forward"), labelled_hop(r"S^{-1}", Palette.pink, "back")).arrange(DOWN, buff=0.5),
            VGroup(labelled_hop("R", Palette.text, "forward"), labelled_hop(r"R^{-1}", Palette.pink, "back")).arrange(DOWN, buff=0.5),
        ]
        self.add(VGroup(grids[0], hops[0], grids[1], hops[1], grids[2]).arrange(RIGHT, buff=0.4))
        fit_to_frame(self)


class FigSingular(Scene):
    def construct(self):
        plane = make_plane(x_range=(-4, 6, 1), y_range=(-3, 5, 1))
        image_line = Line(plane.c2p(-1.5, -3), plane.c2p(2.5, 5), color=Palette.teal, stroke_width=4)
        preimage_line = DashedLine(plane.c2p(6, -2.5), plane.c2p(-4, 2.5), color=Palette.text_muted, stroke_width=3)
        dots = VGroup(*[Dot(plane.c2p(*point), radius=0.1, color=Palette.yellow) for point in PREIMAGES])
        paths = VGroup(*[DashedLine(plane.c2p(*point), plane.c2p(*SHARED_IMAGE), color=Palette.glow, stroke_width=3, buff=0.2).add_tip(tip_length=0.18) for point in PREIMAGES])
        labels = VGroup(*[name_label([f"({point[0]}, {point[1]})"], [Palette.yellow], plane.c2p(*point), DOWN, font_size=34) for point in PREIMAGES])
        target = VGroup(stamp(plane, SHARED_IMAGE), name_label([r"(1, 2)"], [Palette.teal], plane.c2p(*SHARED_IMAGE), RIGHT, font_size=34).shift(RIGHT * 0.15))
        self.add(plane, image_line, preimage_line, paths, dots, labels, target)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = plane_at((-1.6, -2.4), 1.2).set_stroke(opacity=0.22)
        live = LiveTransform(A)
        image = live.point(X)
        forward = vector_arrow(image, Palette.yellow, plane, stroke_width=7)
        home = VGroup(ring(plane, X, Palette.yellow), Dot(plane.c2p(*X), radius=0.08, color=Palette.yellow))
        back = CurvedArrow(plane.c2p(*image) + 0.25 * DR, plane.c2p(*X) + 0.3 * DR, angle=-PI / 1.6, color=Palette.pink, stroke_width=6, tip_length=0.3)
        labels = VGroup(
            name_label([r"A\mathbf x"], [Palette.yellow], plane.c2p(*image), UP, font_size=48),
            name_label([r"\mathbf x"], [Palette.yellow], plane.c2p(*X), UL, font_size=48),
            name_label([r"A^{-1}"], [Palette.pink], back.point_from_proportion(0.5), DR, font_size=52),
        )
        panel = VGroup(named(["A"], basis_matrix(A)), named([r"A^{-1}"], pink_matrix(A_INV), colors=(Palette.pink,))).arrange(RIGHT, buff=0.6)
        panel = backed(panel.to_corner(UL, buff=0.6), padding=0.25)
        self.add(plane, live.grid(plane), forward, stamp(plane, image), home, back, labels, panel)
