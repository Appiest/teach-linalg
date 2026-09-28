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
    skewed_grid,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (0.6, -1.5)
PLANE_UNIT = 1.4
A = ((3, -2), (1, 0))
A_INVERSE = ((0, 1), (-0.5, 1.5))
P = ((2, 1), (1, 1))
P_INVERSE = ((1, -1), (-1, 2))
D = ((2, 0), (0, 1))
SHEAR = ((1, 1), (0, 1))
V1 = (2, 1)
V2 = (1, 1)
U = (0, 1)
U_EIGEN = (-1, 2)
U_STRETCHED = (-2, 2)
AU = (-2, 0)
EIGEN_COLORS = (Palette.yellow, Palette.blue)
BASIS_COLORS = (Palette.i_hat, Palette.j_hat)
CELL = ((0, 0), (1, 0), (1, 1), (0, 1))


def tex(*parts, colors=(), font_size=44):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def colored_matrix(rows, column_colors=(None, None), diagonal=None, **kwargs):
    mat = matrix([[str(entry) for entry in row] for row in rows], **kwargs)
    for index, color in enumerate(column_colors):
        if color:
            mat.get_columns()[index].set_color(color)
    if diagonal:
        for index in range(len(rows)):
            mat.get_rows()[index][index].set_color(diagonal)
    return mat


def named(name, mat, font_size=44):
    return VGroup(MathTex(name, "=", color=Palette.text, font_size=font_size), mat).arrange(RIGHT, buff=0.2)


def corner_panel(content, corner=UL):
    content.to_corner(corner, buff=0.5)
    return VGroup(plate_for(content), content).set_z_index(10)


def name_label(tex_string, color, point, direction, font_size=38):
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.08).next_to(point, direction, buff=0.12)


def target_ring(point):
    return VGroup(
        Dot(point, radius=0.3, color=Palette.glow, fill_opacity=0.14),
        Circle(radius=0.3, color=Palette.glow, stroke_width=4).move_to(point),
    )


def wide_matrix(rows, h_buff, diagonal=None, font_size=42):
    """A matrix with room for multi-digit entries."""
    mat = Matrix(
        [[str(entry) for entry in row] for row in rows],
        v_buff=0.62,
        h_buff=h_buff,
        bracket_h_buff=0.14,
        element_to_mobject_config={"font_size": font_size},
    )
    mat.set_color(Palette.text)
    if diagonal:
        for index in range(len(rows)):
            mat.get_rows()[index][index].set_color(diagonal)
    return mat


def factor_block(name, mat):
    label = MathTex(name, color=Palette.text, font_size=38).next_to(mat, DOWN, buff=0.18)
    return VGroup(mat, label)


def factor_panel():
    """A = P D P^-1 in the top right: P's columns yellow and blue, D's diagonal orange, a name under each factor."""
    size = {"font_size": 32}
    blocks = VGroup(
        factor_block("P", colored_matrix(P, EIGEN_COLORS, element_to_mobject_config=size)),
        factor_block("D", colored_matrix(D, diagonal=Palette.glow, element_to_mobject_config=size)),
        factor_block("P^{-1}", colored_matrix(P_INVERSE, element_to_mobject_config=size)),
    ).arrange(RIGHT, buff=0.22, aligned_edge=UP)
    equals = MathTex("A", "=", color=Palette.text, font_size=44).next_to(blocks[0][0], LEFT, buff=0.22)
    content = VGroup(equals, blocks).to_corner(UR, buff=0.45)
    panel = VGroup(plate_for(content, padding=0.2), content).set_z_index(10)
    panel.blocks = blocks
    return panel


def focus_box(block):
    return SurroundingRectangle(block, color=Palette.glow, buff=0.08, stroke_width=3.5).set_z_index(12)


def eigen_arrows(plane, live):
    return VGroup(*[
        always_redraw(lambda c=coords, color=color: vector_arrow(tuple(live.point(c)), color, plane))
        for coords, color in (((1, 0), Palette.yellow), ((0, 1), Palette.blue))
    ])


def live_cell(plane, live, color=Palette.purple_gray):
    return always_redraw(lambda: Polygon(*[plane.c2p(*live.point(corner)) for corner in CELL], color=color, fill_opacity=0.28, stroke_width=0))


def eigen_lines(plane, stroke_width=4.5):
    return VGroup(*[line_through_origin(plane, v, color, stroke_width) for v, color in zip((V1, V2), EIGEN_COLORS)])


def live_eigen_lines(plane, live, stroke_width=4.5):
    """The two eigen-lines as the lines through the images of the eigen-grid's axes, so they turn with the grid."""
    return VGroup(*[
        always_redraw(lambda c=coords, color=color: line_through_origin(plane, tuple(live.point(c)), color, stroke_width))
        for coords, color in (((1, 0), Palette.yellow), ((0, 1), Palette.blue))
    ])


def coordinate_tag(plane, coords, direction=UP):
    return name_label(f"({coords[0]}, {coords[1]})", Palette.purple_gray, plane.c2p(*coords), direction, font_size=34)


def small_plane():
    plane = make_plane(x_range=(-3, 3, 1), y_range=(-3, 3, 1), x_length=4.0, y_length=4.0)
    plane.set_opacity(0.3)
    return plane


def basis_panel():
    plane = small_plane()
    parts = VGroup(
        plane,
        skewed_grid(plane, V1, V2, reach=6, color=Palette.purple_gray, opacity=0.6),
        eigen_lines(plane, stroke_width=4),
        vector_arrow(V1, Palette.yellow, plane, stroke_width=5),
        vector_arrow(V2, Palette.blue, plane, stroke_width=5),
    )
    title = named("A", colored_matrix(A, BASIS_COLORS, element_to_mobject_config={"font_size": 30}), font_size=34)
    return VGroup(parts, title.next_to(parts, DOWN, buff=0.2))


def shear_panel():
    plane = small_plane()
    live = LiveTransform(SHEAR)
    test_arrow = vector_arrow((0, 2), Palette.purple_gray, plane, stroke_width=5)
    parts = VGroup(
        plane,
        live.grid(plane, color=Palette.purple_gray, opacity=0.6),
        line_through_origin(plane, (0, 1), Palette.purple_gray, 2.5, dashed=True, opacity=0.6),
        line_through_origin(plane, (1, 0), Palette.yellow, 4),
        test_arrow,
    )
    title = named("S", colored_matrix(SHEAR, BASIS_COLORS, element_to_mobject_config={"font_size": 30}), font_size=34)
    panel = VGroup(parts, title.next_to(parts, DOWN, buff=0.2))
    panel.test_arrow, panel.plane = test_arrow, plane
    return panel


def shear_image(panel):
    """Where the shear sends the panel's test arrow (0, 2): to (2, 2), off its dashed line."""
    return vector_arrow((2, 2), Palette.teal, panel.plane, stroke_width=5)


class Lesson(LessonScene):
    day = 32
    title = "Diagonalization"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        self.plane = plane
        self.live = LiveTransform(P)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.recall_eigenvectors()
        line = self.stretch_eigen_grid(line)
        line = self.three_moves(line)
        line = self.columns(line)
        line = self.theorem(line)
        line = self.powers(line)
        self.close_episode(
            r"If the eigenvectors of $A$ form a basis, then $A = PDP^{-1}$.\\"
            r"In that eigenbasis, $A$ only stretches each axis.",
            *self.mobjects,
        )

    def move_grid(self, rows, *extra, run_time=2.6, rate_func=spring_soft):
        self.play(self.live.apply(rows), *extra, run_time=run_time, rate_func=rate_func)

    def recall_eigenvectors(self):
        plane = self.plane
        self.a_panel = corner_panel(named("A", colored_matrix(A, BASIS_COLORS)))
        line = self.say(r"Day 28's matrix $A$ keeps two lines through the origin.", hold=0.2)
        self.play(FadeIn(self.a_panel, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        self.lines = live_eigen_lines(plane, self.live)
        self.play(Create(self.lines[0]), Create(self.lines[1]), run_time=1.4)
        self.arrows = eigen_arrows(plane, self.live)
        self.labels = VGroup(
            name_label(r"\mathbf v_1", Palette.yellow, plane.c2p(*V1), DR),
            name_label(r"\mathbf v_2", Palette.blue, plane.c2p(*V2), UL),
        )
        self.play(GrowArrow(self.arrows[0]), GrowArrow(self.arrows[1]), FadeIn(self.labels), run_time=1.1, rate_func=spring_soft)
        line = self.say(r"Yesterday's shear had one such line, but $A$ has two.", line, hold=Timing.beat)
        line = self.say(r"Can two eigenvectors make $A$ as simple as a diagonal matrix?", line, hold=Timing.read_short)

        line = self.say(r"Use its eigenvectors $\mathbf v_1$ and $\mathbf v_2$ as new axes.", line, hold=0.2)
        self.grid = always_redraw(lambda: self.live.grid(plane, color=Palette.purple_gray, opacity=0.6))
        self.cell = live_cell(plane, self.live)
        self.play(plane.animate.set_opacity(0.25), FadeIn(self.grid), run_time=1.2)
        self.play(FadeIn(self.cell), run_time=0.6)
        self.bring_to_front(self.lines, self.arrows, self.labels, self.a_panel)
        self.wait(Timing.read_short)
        return line

    def stretch_eigen_grid(self, line):
        line = self.say(r"Let $A$ act on this eigen-grid.", line, hold=0.2)
        self.play(FadeOut(self.labels), run_time=0.4)
        self.move_grid(A, run_time=3.0)
        line = self.say(r"Every yellow step doubles and every blue step stays put.", line, hold=Timing.read_short)
        line = self.say(r"On this grid $A$ only stretches each axis.", line, hold=Timing.read_short)
        self.move_grid(A_INVERSE, run_time=1.6)
        return line

    def three_moves(self, line):
        plane = self.plane
        self.panel = factor_panel()
        self.play(FadeOut(self.a_panel), FadeIn(self.panel, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        line = self.say(r"This factorization will make powers of $A$ easy to compute.", line, hold=Timing.read_short)
        line = self.meet_u(line)
        line = self.say(r"Now do $A$ in three moves, starting from the right.", line, hold=Timing.beat)
        box = focus_box(self.panel.blocks[2])
        self.play(Create(box), run_time=0.6)
        line = self.say(r"$P^{-1}$ turns the eigen-grid into the ordinary grid.", line, hold=0.2)
        self.move_grid(P_INVERSE, run_time=3.2)
        basis_tags = VGroup(
            name_label(r"\mathbf e_1", Palette.yellow, plane.c2p(1, 0), DOWN, font_size=34),
            name_label(r"\mathbf e_2", Palette.blue, plane.c2p(0, 1), UR, font_size=34),
        )
        self.play(FadeIn(basis_tags), run_time=0.5)
        line = self.say(r"Now $\mathbf u$ sits at its eigen-coordinates $(-1, 2)$.", line, hold=0.2)
        tag = coordinate_tag(plane, U_EIGEN, LEFT)
        self.play(FadeIn(tag, shift=RIGHT * 0.1), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)

        line = self.say(r"$D$ stretches along the axes by 2 and by 1.", line, hold=0.2)
        self.play(FadeOut(basis_tags), FadeOut(tag), box.animate.become(focus_box(self.panel.blocks[1])), run_time=0.6)
        self.move_grid(D, run_time=2.6)
        tag = coordinate_tag(plane, U_STRETCHED, LEFT)
        self.play(FadeIn(tag, shift=RIGHT * 0.1), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)

        line = self.say(r"$P$ turns the ordinary grid back into the eigen-grid.", line, hold=0.2)
        self.play(FadeOut(tag), box.animate.become(focus_box(self.panel.blocks[0])), run_time=0.6)
        self.move_grid(P, run_time=3.0)
        line = self.say(r"The three moves land exactly on $A\mathbf u$.", line, hold=0.2)
        self.play(Indicate(self.ring, color=Palette.glow, scale_factor=1.35), run_time=0.9)
        self.play(FadeOut(box), run_time=0.4)
        self.wait(Timing.read_short)
        return line

    def meet_u(self, line):
        plane = self.plane
        self.u_ghost = vector_arrow(U, Palette.purple_gray, plane, stroke_width=4).set_opacity(0.35)
        self.u_rider = always_redraw(lambda: vector_arrow(tuple(self.live.point(U_EIGEN)), Palette.purple_gray, plane))
        u_label = name_label(r"\mathbf u", Palette.purple_gray, plane.c2p(*U), UP)
        self.ring = target_ring(plane.c2p(*AU))
        self.ring_label = name_label(r"A\mathbf u", Palette.glow, plane.c2p(*AU), DOWN * 2.2)
        line = self.say(r"Take a vector $\mathbf u$ that $A$ turns, and mark $A\mathbf u$.", line, hold=0.2)
        self.play(GrowArrow(self.u_rider), FadeIn(u_label), run_time=1.0, rate_func=spring_soft)
        self.play(GrowFromCenter(self.ring), FadeIn(self.ring_label), run_time=0.8, rate_func=spring)
        self.add(self.u_ghost)
        self.bring_to_front(self.u_rider, self.panel)
        self.wait(Timing.read_short)
        self.play(FadeOut(u_label), run_time=0.4)
        return line

    def columns(self, line):
        self.veil = scrim().set_z_index(20)
        rows = self.column_rows()
        line = self.say(r"Here is why: look at $AP$ one column at a time.", line, hold=0.2)
        self.play(FadeIn(self.veil), run_time=0.6)
        self.play(FadeIn(rows[0]), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"Each column is an eigenvector times its eigenvalue.", line, hold=0.2)
        self.play(FadeIn(rows[1], shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)
        self.play(FadeIn(rows[2], shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)

        self.result = tex("A", "=", "P", "D", "P^{-1}", colors=(None, None, None, Palette.glow), font_size=80)
        self.result.next_to(rows, DOWN, buff=0.55).set_z_index(21)
        line = self.say(r"$P$ has independent columns, so $P^{-1}$ exists.", line, hold=0.2)
        self.play(FadeIn(self.result, shift=UP * 0.1), run_time=0.9, rate_func=spring_soft)
        self.play(Circumscribe(self.result, color=Palette.glow, buff=0.15), run_time=1.0)
        self.wait(Timing.read_short)
        self.play(FadeOut(rows), self.result.animate.scale(0.8).to_edge(UP, buff=0.5), run_time=0.8, rate_func=spring_soft)
        return line

    def column_rows(self):
        first = named("AP", self.vector_row(r"A\mathbf v_1", r"A\mathbf v_2", 1))
        second = self.equals_row(self.vector_row(r"2\,\mathbf v_1", r"1\,\mathbf v_2", 2, lead=Palette.glow))
        right = VGroup(
            self.vector_row(r"\mathbf v_1", r"\mathbf v_2", 0),
            colored_matrix(D, diagonal=Palette.glow),
            MathTex("=", "PD", color=Palette.text, font_size=44),
        ).arrange(RIGHT, buff=0.2)
        third = self.equals_row(right)
        rows = VGroup(first, second, third).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        for row in (second, third):
            row.shift(RIGHT * (first[0][1].get_x() - row[0].get_x()))
        rows.scale(1.3).move_to(UP * 1.1).set_z_index(21)
        return rows

    @staticmethod
    def equals_row(content):
        return VGroup(MathTex("=", color=Palette.text, font_size=44), content).arrange(RIGHT, buff=0.2)

    @staticmethod
    def vector_row(first, second, skip, lead=None):
        """A 1x2 bracket of two column expressions: skip glyphs before the v's, which go yellow and blue."""
        mat = Matrix([[first, second]], h_buff=1.45, bracket_h_buff=0.14)
        mat.set_color(Palette.text)
        for entry, color in zip(mat.get_entries(), EIGEN_COLORS):
            entry[0][skip:].set_color(color)
            if lead:
                entry[0][0].set_color(lead)
        return mat

    def theorem(self, line):
        statement = Tex(r"$A$ is diagonalizable $\iff$ $A$ has $n$ independent eigenvectors", color=Palette.text, font_size=46)
        statement.to_edge(UP, buff=0.4).set_z_index(21)
        line = self.say(r"$A$ is \emph{diagonalizable} when $A = PDP^{-1}$ with $D$ diagonal.", line, hold=Timing.read_short)
        line = self.say(r"That works exactly when $A$ has $n$ independent eigenvectors.", line, hold=0.2)
        self.play(FadeOut(self.result, shift=UP * 0.1), FadeIn(statement, shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)

        good, bad = basis_panel(), shear_panel()
        VGroup(good, bad).arrange(RIGHT, buff=1.6).next_to(statement, DOWN, buff=0.3).set_z_index(21)
        bad.test_image = shear_image(bad).set_z_index(22)
        self.play(FadeIn(good), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"The shear from Day 31 has only one eigen-line.", line, hold=0.2)
        self.play(FadeIn(bad), run_time=0.8)
        self.play(TransformFromCopy(bad.test_arrow, bad.test_image), run_time=1.2, rate_func=spring_soft)
        self.wait(Timing.read_short)

        distinct = Tex(r"$n$ distinct eigenvalues $\Rightarrow$ diagonalizable", color=Palette.text, font_size=46)
        distinct.move_to(statement).set_z_index(21)
        values = tex(r"\lambda", "=", "2", ",", "1", colors=(Palette.glow, None, Palette.yellow, None, Palette.blue), font_size=56)
        values.move_to(bad[0]).set_z_index(21)
        line = self.say(r"Distinct eigenvalues always give enough eigenvectors.", line, hold=0.2)
        self.play(FadeOut(bad), FadeOut(bad.test_image), FadeOut(statement), FadeIn(distinct), run_time=0.8)
        self.play(FadeIn(values, shift=LEFT * 0.1), run_time=0.7, rate_func=spring)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(good, distinct, values)), run_time=0.6)
        return line

    def powers(self, line):
        steps = VGroup(
            tex("A^2", "=", r"(PDP^{-1})(PDP^{-1})", font_size=52),
            tex("=", "PD", r"(P^{-1}P)", r"DP^{-1}", font_size=52),
            tex("=", "PD^2P^{-1}", font_size=52),
        ).arrange(DOWN, buff=0.35)
        for step in steps[1:]:
            step.shift(RIGHT * (steps[0][1].get_x() - step[0].get_x()))
        general = tex("A^k", "=", "P", "D^k", "P^{-1}", colors=(None, None, None, Palette.glow), font_size=64)
        diagonal = tex(r"D^k = \begin{bmatrix} 2^k & 0 \\ 0 & 1^k \end{bmatrix}", font_size=50)
        side = VGroup(general, diagonal).arrange(DOWN, buff=0.45).next_to(steps, RIGHT, buff=1.4)
        product = self.tenth_power_row()
        board = VGroup(VGroup(steps, side), product).arrange(DOWN, buff=0.7)
        board.scale(min(1.2, 12.5 / board.width)).move_to(UP * 0.45).set_z_index(21)
        brute = tex("A^{10}", "=", r"A\,A\,A\,A\,A\,A\,A\,A\,A\,A", font_size=60).move_to(UP * 0.45).set_z_index(21)
        self.play(FadeIn(brute, shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        line = self.say(r"Computing $A^{10}$ directly takes nine matrix products.", line, hold=Timing.read_short)
        self.play(FadeOut(brute), FadeIn(steps[0]), run_time=0.8)
        line = self.say(r"Squaring $A$ puts $P^{-1}P = I$ in the middle.", line, hold=0.2)
        self.play(FadeIn(steps[1], shift=DOWN * 0.1), run_time=0.8)
        self.play(steps[1][2].animate.set_color(Palette.glow), run_time=0.6)
        self.play(FadeIn(steps[2], shift=DOWN * 0.1), run_time=0.8)
        self.wait(Timing.beat)

        line = self.say(r"So $A^k = PD^kP^{-1}$, and only $D$ takes the power.", line, hold=0.2)
        self.play(FadeIn(general, shift=LEFT * 0.1), run_time=0.8, rate_func=spring_soft)
        self.play(FadeIn(diagonal, shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)

        line = self.say(r"$A^{10}$ now takes two products instead of nine.", line, hold=0.2)
        self.play(FadeIn(product[:4], shift=UP * 0.1), run_time=0.9, rate_func=spring_soft)
        self.play(FadeIn(product[4:], shift=LEFT * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"Day 33 uses these powers to predict where $A^k\mathbf x$ heads.", line, hold=Timing.read_short)
        self.play(FadeOut(line), run_time=0.35)
        return board

    @staticmethod
    def tenth_power_row():
        size = {"font_size": 42}
        return VGroup(
            MathTex("A^{10}", "=", color=Palette.text, font_size=50),
            colored_matrix(P, EIGEN_COLORS, element_to_mobject_config=size),
            wide_matrix(((1024, 0), (0, 1)), 1.35, diagonal=Palette.glow),
            colored_matrix(P_INVERSE, element_to_mobject_config=size),
            MathTex("=", color=Palette.text, font_size=50),
            wide_matrix(((2047, -2046), (1023, -1022)), 1.75),
        ).arrange(RIGHT, buff=0.22)


def scene_plane(origin=PLANE_ORIGIN):
    plane = plane_at(origin, PLANE_UNIT)
    plane.set_opacity(0.3)
    return plane


def move_stage(live_rows, u_coords, title, show_basis=True):
    """One panel of the three-moves figure: the eigen-grid carried to `live_rows` and u at `u_coords`."""
    plane = make_plane(x_range=(-3, 5, 1), y_range=(-1, 3, 1), x_length=8 * 0.62, y_length=4 * 0.62)
    plane.set_opacity(0.3)
    live = LiveTransform(live_rows)
    parts = VGroup(plane, live.grid(plane, color=Palette.purple_gray, opacity=0.6))
    if show_basis:
        parts.add(*[vector_arrow(tuple(live.point(c)), color, plane, stroke_width=5) for c, color in (((1, 0), Palette.yellow), ((0, 1), Palette.blue))])
    parts.add(target_ring(plane.c2p(*AU)).scale(0.7))
    parts.add(vector_arrow(u_coords, Palette.purple_gray, plane, stroke_width=5))
    heading = MathTex(title, color=Palette.text, font_size=40).next_to(plane, UP, buff=0.2)
    return VGroup(parts, heading)


class FigThreeMoves(Scene):
    def construct(self):
        stages = [
            move_stage(P, U, r"\text{start}"),
            move_stage(np.eye(2), U_EIGEN, r"\text{after } P^{-1}"),
            move_stage(D, U_STRETCHED, r"\text{after } D"),
            move_stage(np.array(A) @ np.array(P), AU, r"\text{after } P"),
        ]
        row = VGroup(*stages).arrange_in_grid(rows=2, cols=2, buff=(0.45, 0.35))
        self.add(row)
        fit_to_frame(self)


class FigEigenGridStretch(Scene):
    def construct(self):
        panels = []
        for rows, title in ((P, r"\text{eigen-grid}"), (np.array(A) @ np.array(P), r"\text{after } A")):
            plane = make_plane(x_range=(-3, 6, 1), y_range=(-2, 4, 1), x_length=9 * 0.8, y_length=6 * 0.8)
            plane.set_opacity(0.3)
            live = LiveTransform(rows)
            parts = VGroup(
                plane,
                live.grid(plane, color=Palette.purple_gray, opacity=0.6),
                Polygon(*[plane.c2p(*live.point(c)) for c in CELL], color=Palette.purple_gray, fill_opacity=0.3, stroke_width=0),
                eigen_lines(plane, 4),
                vector_arrow(tuple(live.point((1, 0))), Palette.yellow, plane),
                vector_arrow(tuple(live.point((0, 1))), Palette.blue, plane),
            )
            panels.append(VGroup(parts, MathTex(title, color=Palette.text, font_size=44).next_to(plane, UP, buff=0.2)))
        self.add(VGroup(*panels).arrange(RIGHT, buff=0.6))
        fit_to_frame(self)


class FigEnoughEigenvectors(Scene):
    def construct(self):
        good, bad = basis_panel(), shear_panel()
        self.add(VGroup(good, bad).arrange(RIGHT, buff=1.2))
        self.add(shear_image(bad))
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = scene_plane((0.9, -1.1))
        live = LiveTransform(P)
        formula = backed(tex("A", "=", "P", "D", "P^{-1}", colors=(None, None, None, Palette.glow), font_size=80), padding=0.25)
        formula.to_corner(UL, buff=0.6)
        self.add(
            plane,
            live.grid(plane, color=Palette.purple_gray, opacity=0.65),
            Polygon(*[plane.c2p(*live.point(c)) for c in CELL], color=Palette.purple_gray, fill_opacity=0.3, stroke_width=0),
            eigen_lines(plane, 5),
            vector_arrow(V1, Palette.yellow, plane, stroke_width=7),
            vector_arrow(V2, Palette.blue, plane, stroke_width=7),
            formula,
        )
