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
    fit_to_frame,
    line_through_origin,
    make_plane,
    matrix,
    plane_at,
    plate_for,
    scrim,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (-4.0, -1.5)
PLANE_UNIT = 1.0
A = ((2, 1), (1, 2))
A_INVERSE = ((2 / 3, -1 / 3), (-1 / 3, 2 / 3))
A_MINUS_2I = ((0, 1), (1, 0))
V1 = (1, 1)
V2 = (1, -1)
X0 = (1, 0)
BASIS_COLORS = (Palette.i_hat, Palette.j_hat)
SWING_STEPS = (3, 4, 5, 6)


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


def corner_panel(content, corner=UR):
    content.to_corner(corner, buff=0.55)
    return VGroup(plate_for(content), content).set_z_index(10)


def name_label(tex_string, color, point, direction, font_size=38):
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.08).next_to(point, direction, buff=0.12)


def tip_glow(point, scale=1.0):
    halo = Dot(point, radius=0.22 * scale, color=Palette.glow, fill_opacity=0.22)
    core = Dot(point, radius=0.075 * scale, color=Palette.glow)
    return VGroup(halo, core)


def safe_arrow(plane, coords, color, stroke_width=6):
    """An arrow to coords, or a dot at the origin once it has shrunk to nothing."""
    if math.hypot(*coords) < 0.08:
        return Dot(plane.c2p(0, 0), radius=0.08, color=color)
    return vector_arrow(coords, color, plane, stroke_width=stroke_width)


def piece_arrow(plane, start, end, color, stroke_width=5):
    """A tip-to-tail arrow from start to end in plane coordinates, or nothing once it is too short to draw."""
    if math.hypot(end[0] - start[0], end[1] - start[1]) < 0.12:
        return VMobject()
    return Arrow(
        plane.c2p(*start),
        plane.c2p(*end),
        buff=0,
        color=color,
        stroke_width=stroke_width,
        max_tip_length_to_length_ratio=0.25,
        max_stroke_width_to_length_ratio=12,
    )


def eigen_lines(plane, stroke_width=4.5):
    return VGroup(line_through_origin(plane, V1, Palette.yellow, stroke_width), line_through_origin(plane, V2, Palette.blue, stroke_width))


def eigen_labels(plane):
    return VGroup(
        name_label(r"\lambda = 3", Palette.yellow, plane.c2p(1.8, 1.8), UL, font_size=40),
        name_label(r"\lambda = 1", Palette.blue, plane.c2p(-1.6, 1.6), DL, font_size=40),
    )


def box_corners(v, w):
    return ((0, 0), v, (v[0] + w[0], v[1] + w[1]), w)


def moving_box(plane, live):
    corners = [plane.c2p(*live.point(corner)) for corner in box_corners(V1, V2)]
    return Polygon(*corners, color=Palette.yellow, fill_opacity=0.22, stroke_width=0)


def swing_point(k):
    """x_k = (1/2) 3^k v1 + (1/2) v2, for real k so it can move continuously."""
    grow = 0.5 * 3**k
    return (grow * V1[0] + 0.5 * V2[0], grow * V1[1] + 0.5 * V2[1])


def rescaled(point, length):
    size = math.hypot(*point)
    return (point[0] * length / size, point[1] * length / size)


def yellow_piece(k, length):
    """The v1 part of x_k after x_k is rescaled to `length`."""
    factor = length / math.hypot(*swing_point(k))
    grow = 0.5 * 3**k * factor
    return (grow * V1[0], grow * V1[1])


SWING_LENGTH = math.hypot(*swing_point(2))


def swing_arrow(plane, k, color=Palette.teal, opacity=1.0, stroke_width=6):
    return vector_arrow(rescaled(swing_point(k), SWING_LENGTH), color, plane, stroke_width=stroke_width).set_opacity(opacity)


def swing_pieces(plane, k):
    tip = rescaled(swing_point(k), SWING_LENGTH)
    corner = yellow_piece(k, SWING_LENGTH)
    return VGroup(
        piece_arrow(plane, (0, 0), corner, Palette.yellow, 4),
        piece_arrow(plane, corner, tip, Palette.blue, 4),
    )


def split_pieces(plane, live):
    corner = live.point((0.5 * V1[0], 0.5 * V1[1]))
    tip = live.point(X0)
    return VGroup(piece_arrow(plane, (0, 0), corner, Palette.yellow, 4), piece_arrow(plane, corner, tip, Palette.blue, 4))


def factor_table():
    """Rows of matrix, stretch on v1, stretch on v2."""
    entries = (
        (r"A", "3", "1"),
        (r"A^2", "9", "1"),
        (r"A^{-1}", r"\tfrac13", "1"),
        (r"A - 2I", "1", "-1"),
    )
    header = VGroup(MathTex("", font_size=40), MathTex(r"\mathbf v_1", color=Palette.yellow, font_size=40), MathTex(r"\mathbf v_2", color=Palette.blue, font_size=40))
    rows = [header]
    for name, first, second in entries:
        rows.append(
            VGroup(
                MathTex(name, color=Palette.text, font_size=40),
                MathTex(first, color=Palette.yellow, font_size=40),
                MathTex(second, color=Palette.blue, font_size=40),
            )
        )
    cells = VGroup(*[cell for row in rows for cell in row])
    cells.arrange_in_grid(rows=len(rows), cols=3, buff=(0.7, 0.32), col_alignments="rcc")
    return VGroup(*[VGroup(*cells[3 * i : 3 * i + 3]) for i in range(len(rows))])


class Lesson(LessonScene):
    day = 30
    title = "Properties of eigenvalues"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        self.plane = plane
        self.live = LiveTransform()
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.meet_a()
        line = self.area_triples(line)
        line = self.trace_and_determinant(line)
        line = self.similar_matrices(line)
        line = self.stretch_table(line)
        line = self.split_start(line)
        line = self.swing(line)
        self.close_episode(
            r"The eigenvalues add up to the trace and multiply to the determinant.\\"
            r"Powers of $A$ raise them to powers, so the biggest one takes over.",
            *self.mobjects,
        )

    def move_grid(self, rows, *extra, run_time=2.4, rate_func=spring_soft):
        self.play(self.live.apply(rows), *extra, run_time=run_time, rate_func=rate_func)

    def meet_a(self):
        plane = self.plane
        self.a_panel = corner_panel(named("A", basis_matrix(A)))
        self.grid = always_redraw(lambda: self.live.grid(plane, opacity=0.8))
        line = self.say(r"Day 29 found the eigenvalues, so what do they tell us?", hold=0.2)
        self.play(plane.animate.set_opacity(0.3), FadeIn(self.grid), FadeIn(self.a_panel, shift=DOWN * 0.1), run_time=0.9)
        self.wait(Timing.read_short)
        self.lines = eigen_lines(plane)
        self.labels = eigen_labels(plane)
        self.riders = VGroup(
            always_redraw(lambda: safe_arrow(plane, self.live.point(V1), Palette.yellow)),
            always_redraw(lambda: safe_arrow(plane, self.live.point(V2), Palette.blue)),
        )
        line = self.say(r"This $A$ stretches the yellow line by 3 and the blue by 1.", line, hold=0.2)
        self.play(Create(self.lines[0]), Create(self.lines[1]), run_time=1.2)
        self.add(self.riders)
        self.play(GrowArrow(self.riders[0]), GrowArrow(self.riders[1]), run_time=0.9, rate_func=spring_soft)
        self.play(FadeIn(self.labels[0], shift=LEFT * 0.1), FadeIn(self.labels[1], shift=LEFT * 0.1), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        return line

    def area_readout(self, value):
        text = tex(r"\text{area} = " + value, font_size=40)
        text.next_to(self.a_panel, DOWN, buff=0.35).align_to(self.a_panel, RIGHT)
        return VGroup(plate_for(text, padding=0.18), text).set_z_index(10)

    def area_triples(self, line):
        plane = self.plane
        box = always_redraw(lambda: moving_box(plane, self.live))
        before = self.area_readout("2")
        after = self.area_readout(r"6 = 3 \cdot 2")
        line = self.say(r"Build a box on the two eigenvectors and apply $A$.", line, hold=0.2)
        self.add(box)
        self.bring_to_front(self.riders)
        self.play(FadeIn(box), FadeIn(before), run_time=0.8)
        self.move_grid(A, run_time=2.8)
        line = self.say(r"One side triples and one stays, so the area triples.", line, hold=0.2)
        self.play(FadeOut(before), FadeIn(after, shift=UP * 0.1), run_time=0.7)
        self.wait(Timing.read_short)
        line = self.say(r"That makes $\det A = 3 \cdot 1$, the product of the eigenvalues.", line, hold=Timing.read_short)
        self.move_grid(A_INVERSE, FadeOut(box), FadeOut(after), run_time=1.4)
        return line

    def trace_and_determinant(self, line):
        self.veil = scrim().set_z_index(20)
        big = named("A", basis_matrix(A), font_size=52)
        diagonal = [big[1].get_rows()[i][i] for i in range(2)]
        trace = tex(r"\operatorname{tr} A", "=", "2 + 2", "=", "4", "=", "3", "+", "1", colors=(None, None, Palette.glow, None, None, None, Palette.yellow, None, Palette.blue), font_size=52)
        det = tex(r"\det A", "=", r"2 \cdot 2 - 1 \cdot 1", "=", "3", "=", "3", r"\cdot", "1", colors=(None, None, None, None, None, None, Palette.yellow, None, Palette.blue), font_size=52)
        facts = VGroup(trace, det).arrange(DOWN, buff=0.45)
        for row in facts[1:]:
            row.shift(RIGHT * (trace[1].get_x() - row[1].get_x()))
        board = VGroup(big, facts).arrange(DOWN, buff=0.6).move_to(UP * 0.55).set_z_index(21)
        self.board = board
        line = self.say(r"The \emph{trace} of $A$ adds up its diagonal entries.", line, hold=0.2)
        self.play(FadeIn(self.veil), FadeIn(big), run_time=0.8)
        self.play(*[entry.animate.set_color(Palette.glow) for entry in diagonal], run_time=0.6)
        self.play(FadeIn(trace[:5], shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"The trace equals the sum of the eigenvalues.", line, hold=0.2)
        self.play(FadeIn(trace[5:], shift=LEFT * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"The determinant equals their product.", line, hold=0.2)
        self.play(FadeIn(det[:5], shift=UP * 0.1), run_time=0.8)
        self.play(FadeIn(det[5:], shift=LEFT * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return self.characteristic(line)

    def characteristic(self, line):
        big, facts = self.board
        poly = tex(r"\det(A - \lambda I)", "=", r"\lambda^2 -", "4", r"\lambda +", "3", "=", r"(\lambda - 3)(\lambda - 1)", colors=(None, None, None, Palette.glow, None, Palette.glow), font_size=52)
        poly.move_to(facts).set_z_index(21)
        names = VGroup(
            MathTex(r"\operatorname{tr} A", color=Palette.glow, font_size=38).next_to(poly[3], DOWN, buff=0.3),
            MathTex(r"\det A", color=Palette.glow, font_size=38).next_to(poly[5], DOWN, buff=0.3),
        ).set_z_index(21)
        line = self.say(r"The characteristic polynomial from Day 29 shows why.", line, hold=0.2)
        self.play(FadeOut(facts, shift=UP * 0.1), run_time=0.5)
        self.play(FadeIn(poly, shift=UP * 0.1), run_time=0.9)
        self.play(FadeIn(names, shift=UP * 0.1), run_time=0.7)
        self.wait(Timing.read_long)
        rules = VGroup(
            tex(r"\operatorname{tr} A", "=", r"\lambda_1 + \lambda_2 + \cdots + \lambda_n", colors=(None, None, Palette.glow), font_size=52),
            tex(r"\det A", "=", r"\lambda_1 \lambda_2 \cdots \lambda_n", colors=(None, None, Palette.glow), font_size=52),
        ).arrange(DOWN, buff=0.45)
        rules[1].shift(RIGHT * (rules[0][1].get_x() - rules[1][1].get_x()))
        rules.move_to(poly).set_z_index(21)
        line = self.say(r"It works for every $n \times n$ matrix, counting repeats.", line, hold=0.2)
        self.play(FadeOut(VGroup(poly, names), shift=UP * 0.1), run_time=0.5)
        self.play(FadeIn(rules, shift=UP * 0.1), run_time=0.9)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(big, rules)), run_time=0.6)
        self.remove(*big.get_family(), *facts.get_family(), *poly.get_family(), *names.get_family(), *rules.get_family())
        return line

    def similar_matrices(self, line):
        steps = VGroup(
            tex("B", "=", r"P^{-1} A P", font_size=52),
            tex(r"B - \lambda I", "=", r"P^{-1}(A - \lambda I)P", font_size=48),
            tex(r"\det(B - \lambda I)", "=", r"\det P^{-1}\,\det(A - \lambda I)\,\det P", font_size=48),
            tex("", "=", r"\det(A - \lambda I)", colors=(None, None, Palette.glow), font_size=48),
        ).arrange(DOWN, buff=0.42)
        for step in steps[1:]:
            step.shift(RIGHT * (steps[0][1].get_x() - step[1].get_x()))
        steps.move_to(UP * 0.5).set_z_index(21)
        line = self.say(r"On Day 22, $B = P^{-1}AP$ was the same map in a new basis.", line, hold=0.2)
        self.play(FadeIn(steps[0], shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        line = self.say(r"Subtracting $\lambda I$ keeps the $P^{-1}$ and $P$ outside.", line, hold=0.2)
        self.play(FadeIn(steps[1], shift=UP * 0.1), run_time=0.8)
        self.play(FadeIn(steps[2], shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"Since $\det P^{-1} \det P = 1$, the polynomials match.", line, hold=0.2)
        self.play(FadeIn(steps[3], shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        line = self.say(r"So \emph{similar} matrices share eigenvalues, trace and determinant.", line, hold=Timing.read_short)
        line = self.say(r"Day 33 uses this to pick a map's simplest basis.", line, hold=Timing.read_short)
        self.play(FadeOut(steps), FadeOut(self.veil), FadeOut(self.a_panel), run_time=0.8)
        self.remove(*steps.get_family(), *self.a_panel.get_family())
        return line

    def stretch_table(self, line):
        table = factor_table().to_corner(UR, buff=0.7)
        plate = plate_for(table, padding=0.3).set_z_index(10)
        table.set_z_index(11)
        self.play(FadeIn(plate), FadeIn(table[0]), FadeIn(table[1]), run_time=0.8)
        line = self.say(r"Back to $A$: it stretches $\mathbf v_1$ by 3 and $\mathbf v_2$ by 1.", line, hold=0.2)
        self.move_grid(A)
        line = self.say(r"We want $A^k$ without multiplying by $A$ a full $k$ times.", line, hold=Timing.read_short)
        self.move_grid(A_INVERSE, run_time=1.2)
        line = self.show_power(line, table)
        line = self.show_inverse(line, table)
        line = self.show_shift(line, table)
        line = self.say(r"The eigenlines never move, and only the stretch factors change.", line, hold=Timing.read_short)
        self.play(FadeOut(VGroup(plate, table)), run_time=0.6)
        self.remove(*table.get_family(), plate)
        return line

    def derivation(self, *parts):
        formula = tex(*parts, font_size=42).to_corner(UL, buff=0.55)
        return VGroup(plate_for(formula, padding=0.22), formula).set_z_index(10)

    def show_power(self, line, table):
        proof = self.derivation(r"A^2\mathbf v = A(\lambda\mathbf v) = \lambda A\mathbf v = \lambda^2\mathbf v")
        line = self.say(r"Apply $A$ twice and each stretch factor gets squared.", line, hold=0.2)
        self.play(FadeIn(proof, shift=DOWN * 0.1), run_time=0.8)
        self.play(FadeIn(table[2], shift=LEFT * 0.1), run_time=0.7, rate_func=spring_soft)
        self.wait(Timing.read_short)
        self.proof = proof
        return line

    def show_inverse(self, line, table):
        proof = self.derivation(r"\mathbf v = A^{-1}(\lambda \mathbf v) \;\Rightarrow\; A^{-1}\mathbf v = \tfrac{1}{\lambda}\mathbf v")
        line = self.say(r"Undoing $A$ divides by each stretch factor instead.", line, hold=0.2)
        self.play(FadeOut(self.proof), FadeIn(proof, shift=DOWN * 0.1), run_time=0.8)
        self.move_grid(A_INVERSE, FadeIn(table[3], shift=LEFT * 0.1))
        self.wait(Timing.read_short)
        self.move_grid(A, run_time=1.2)
        self.proof = proof
        return line

    def show_shift(self, line, table):
        proof = self.derivation(r"(A - 2I)\mathbf v = \lambda\mathbf v - 2\mathbf v = (\lambda - 2)\mathbf v")
        line = self.say(r"Subtracting $2I$ subtracts 2 from each stretch factor.", line, hold=0.2)
        self.play(FadeOut(self.proof), FadeIn(proof, shift=DOWN * 0.1), run_time=0.8)
        self.move_grid(A_MINUS_2I, FadeIn(table[4], shift=LEFT * 0.1), run_time=2.8)
        line = self.say(r"The blue factor becomes $1 - 2 = -1$, so $\mathbf v_2$ flips.", line, hold=Timing.read_short)
        self.move_grid(A_MINUS_2I, FadeOut(proof), run_time=1.4)
        self.remove(*proof.get_family())
        return line

    def split_start(self, line):
        plane = self.plane
        claim = self.derivation(r"\lambda_1 \ne \lambda_2", r"\;\Rightarrow\;", r"\{\mathbf v_1, \mathbf v_2\} \text{ is independent}")
        line = self.say(r"Eigenvectors for different eigenvalues are always independent.", line, hold=0.2)
        self.play(FadeIn(claim, shift=DOWN * 0.1), FadeOut(self.riders), run_time=0.8)
        self.wait(Timing.read_short)
        self.start_arrow = vector_arrow(X0, Palette.purple_gray, plane)
        self.start_label = name_label(r"\mathbf x_0", Palette.purple_gray, plane.c2p(*X0), DOWN)
        line = self.say(r"So any $\mathbf x_0$ splits into a yellow piece and a blue piece.", line, hold=0.2)
        self.play(GrowArrow(self.start_arrow), FadeIn(self.start_label), run_time=0.9, rate_func=spring_soft)
        self.pieces = always_redraw(lambda: split_pieces(plane, self.live))
        self.play(Create(self.pieces), run_time=1.2)
        self.wait(Timing.read_short)
        line = self.say(r"Day 32 turns this eigenvector basis into a diagonal matrix.", line, hold=Timing.read_short)
        self.play(FadeOut(claim), run_time=0.5)
        self.remove(*claim.get_family())
        return line

    def swing_board(self):
        formula = tex(r"\mathbf x_k", "=", r"\tfrac12\,", r"3^k", r"\mathbf v_1", "+", r"\tfrac12\,", r"1^k", r"\mathbf v_2",
                      colors=(Palette.teal, None, None, Palette.glow, Palette.yellow, None, None, Palette.glow, Palette.blue), font_size=50)
        formula.move_to(RIGHT * 4.1 + DOWN * 1.9)
        return VGroup(plate_for(formula, padding=0.25), formula).set_z_index(10)

    def step_label(self, k):
        label = tex(r"\mathbf x_{" + str(k) + "}", colors=(Palette.teal,), font_size=38)
        return backed(label, padding=0.08)

    def swing(self, line):
        plane = self.plane
        board = self.swing_board()
        riding = always_redraw(lambda: safe_arrow(plane, self.live.point(X0), Palette.teal))
        line = self.say(r"Now apply $A$ again and again, starting from $\mathbf x_0 = (1, 0)$.", line, hold=0.2)
        self.play(FadeIn(board, shift=DOWN * 0.1), run_time=0.8)
        self.add(riding)
        self.bring_to_front(self.pieces)
        trail = VGroup()
        for k in (1, 2):
            self.move_grid(A, run_time=2.2)
            trail.add(self.stamp_iterate(k))
            if k == 1:
                line = self.say(r"The yellow piece triples each step, and the blue piece stays.", line, hold=Timing.beat)
        self.wait(Timing.beat)
        return self.rescaled_swing(line, VGroup(riding, trail), board)

    def stamp_iterate(self, k):
        plane = self.plane
        point = self.live.point(X0)
        ghost = vector_arrow(point, Palette.teal, plane, stroke_width=4).set_opacity(0.35)
        label = self.step_label(k).next_to(plane.c2p(*point), UR, buff=0.08)
        self.add(ghost)
        self.play(FadeIn(label, shift=DOWN * 0.1), run_time=0.5, rate_func=spring)
        return VGroup(ghost, label)

    def rescaled_swing(self, line, leftovers, board):
        plane = self.plane
        k_value = ValueTracker(2.0)
        pieces = always_redraw(lambda: swing_pieces(plane, k_value.get_value()))
        arrow = always_redraw(lambda: swing_arrow(plane, k_value.get_value()))
        line = self.say(r"The arrows grow fast, so rescale each one to this length.", line, hold=0.2)
        self.remove(self.pieces)
        self.add(pieces, arrow)
        self.play(FadeOut(leftovers), FadeOut(self.grid), FadeOut(self.start_arrow), FadeOut(self.start_label), plane.animate.set_opacity(0.7), run_time=1.0)
        self.remove(*leftovers.get_family(), self.start_arrow, self.start_label)
        self.wait(Timing.beat)
        line = self.say(r"The blue piece shrinks by 3 against the yellow each time.", line, hold=0.2)
        ghosts = VGroup()
        for k in SWING_STEPS:
            ghost = swing_arrow(plane, k - 1, opacity=0.3, stroke_width=4)
            ghosts.add(ghost)
            self.add(ghost)
            self.bring_to_front(pieces, arrow)
            self.play(k_value.animate.set_value(k), run_time=1.3, rate_func=spring_soft)
        glow = tip_glow(plane.c2p(*rescaled(swing_point(6), SWING_LENGTH)))
        line = self.say(r"$\mathbf x_k$ swings onto the line with the largest $|\lambda|$.", line, hold=0.2)
        self.play(GrowFromCenter(glow), Indicate(board[1][3], color=Palette.glow, scale_factor=1.3), run_time=0.9)
        self.wait(Timing.read_long)
        return line


def figure_plane(x_range=(-3, 5), y_range=(-3, 5), size=6):
    plane = make_plane(x_range=(*x_range, 1), y_range=(*y_range, 1), x_length=size * (x_range[1] - x_range[0]) / 8, y_length=size * (y_range[1] - y_range[0]) / 8)
    return plane.set_opacity(0.45)


def scene_plane():
    plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
    plane.set_opacity(0.55)
    return plane


class FigAreaTriples(Scene):
    def construct(self):
        before = self.box_plane(np.eye(2), r"\text{area} = 2")
        after = self.box_plane(np.array(A, dtype=float), r"\text{area} = 6")
        arrow = VGroup(Arrow(LEFT * 0.6, RIGHT * 0.6, color=Palette.text, stroke_width=5), MathTex("A", color=Palette.text, font_size=44))
        arrow[1].next_to(arrow[0], UP, buff=0.15)
        VGroup(before, arrow, after).arrange(RIGHT, buff=0.4)
        self.add(before, arrow, after)
        fit_to_frame(self)

    @staticmethod
    def box_plane(rows, area):
        plane = figure_plane(x_range=(-2, 5), y_range=(-2, 5))
        live = LiveTransform(rows)
        parts = VGroup(plane, live.grid(plane, opacity=0.7), eigen_lines(plane), moving_box(plane, live))
        parts.add(vector_arrow(live.point(V1), Palette.yellow, plane), vector_arrow(live.point(V2), Palette.blue, plane))
        parts.add(name_label(area, Palette.text, plane.c2p(1.8, -1.3), RIGHT, font_size=40))
        return parts


class FigTraceDeterminant(Scene):
    def construct(self):
        mat = named("A", basis_matrix(A), font_size=52)
        for i in range(2):
            mat[1].get_rows()[i][i].set_color(Palette.glow)
        rows = VGroup(
            tex(r"\operatorname{tr} A", "=", "2 + 2", "=", "3", "+", "1", colors=(None, None, Palette.glow, None, Palette.yellow, None, Palette.blue)),
            tex(r"\det A", "=", r"2 \cdot 2 - 1 \cdot 1", "=", "3", r"\cdot", "1", colors=(None, None, None, None, Palette.yellow, None, Palette.blue)),
            tex(r"\det(A - \lambda I)", "=", r"\lambda^2 -", "4", r"\lambda +", "3", colors=(None, None, None, Palette.glow, None, Palette.glow)),
        ).arrange(DOWN, buff=0.45)
        for row in rows[1:]:
            row.shift(RIGHT * (rows[0][1].get_x() - row[1].get_x()))
        self.add(VGroup(mat, rows).arrange(RIGHT, buff=1.2))
        fit_to_frame(self, margin=0.8)


class FigSameLines(Scene):
    def construct(self):
        panels = VGroup(
            self.panel(A, "A", ("3", "1")),
            self.panel(A_INVERSE, r"A^{-1}", (r"\tfrac13", "1")),
            self.panel(A_MINUS_2I, r"A - 2I", ("1", "-1")),
        ).arrange(RIGHT, buff=0.5)
        self.add(panels)
        fit_to_frame(self)

    @staticmethod
    def panel(rows, name, factors):
        plane = figure_plane(x_range=(-3, 5), y_range=(-3, 5), size=5)
        live = LiveTransform(rows)
        parts = VGroup(plane, live.grid(plane, opacity=0.55), eigen_lines(plane))
        for vector, color in (((1.5, 1.5), Palette.yellow), ((1.5, -1.5), Palette.blue)):
            parts.add(vector_arrow(vector, color, plane, stroke_width=4).set_opacity(0.35))
            parts.add(safe_arrow(plane, live.point(vector), color))
        title = MathTex(name, color=Palette.text, font_size=48).next_to(plane, UP, buff=0.25)
        readout = tex(r"\times", factors[0], r"\quad \times", factors[1], colors=(Palette.yellow, Palette.yellow, Palette.blue, Palette.blue), font_size=40)
        readout.next_to(plane, DOWN, buff=0.25)
        return VGroup(parts, title, readout)


class FigSwing(Scene):
    def construct(self):
        plane = scene_plane()
        self.add(plane, eigen_lines(plane))
        for k in range(0, 6):
            self.add(swing_arrow(plane, k, opacity=0.25 + 0.12 * k, stroke_width=4))
        self.add(swing_arrow(plane, 6))
        for k in (0, 1, 2):
            tip = plane.c2p(*rescaled(swing_point(k), SWING_LENGTH))
            self.add(backed(MathTex(r"\mathbf x_{" + str(k) + "}", color=Palette.teal, font_size=36), padding=0.08).next_to(tip, DR, buff=0.08))
        self.add(tip_glow(plane.c2p(*rescaled(swing_point(6), SWING_LENGTH))), eigen_labels(plane))


class Poster(Scene):
    def construct(self):
        plane = scene_plane()
        self.add(plane, eigen_lines(plane, stroke_width=5))
        for k in range(0, 6):
            self.add(swing_arrow(plane, k, opacity=0.2 + 0.13 * k, stroke_width=5))
        self.add(swing_arrow(plane, 6, stroke_width=7), tip_glow(plane.c2p(*rescaled(swing_point(6), SWING_LENGTH)), scale=1.3))
        formula = tex(r"\mathbf x_k", "=", r"\tfrac12\,", r"3^k", r"\mathbf v_1", "+", r"\tfrac12\,", r"1^k", r"\mathbf v_2",
                      colors=(Palette.teal, None, None, Palette.glow, Palette.yellow, None, None, Palette.glow, Palette.blue), font_size=60)
        self.add(backed(formula, padding=0.25).move_to(RIGHT * 3.5 + DOWN * 2.9))
