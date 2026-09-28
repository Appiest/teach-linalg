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
    arrow_between,
    backed,
    circle_image,
    fit_to_frame,
    line_through_origin,
    make_plane,
    matrix,
    plane_at,
    plate_for,
    right_angle_mark,
    scrim,
    spring,
    spring_soft,
)

PLANE_ORIGIN = (0.3, 0.35)
PLANE_UNIT = 0.68
A = ((7, 2), (2, 4))
B = ((7, 2), (-4, 1))
D = ((8, 0), (0, 3))
V1 = (2, 1)
V2 = (-1, 2)
U1 = np.array(V1) / math.sqrt(5)
U2 = np.array(V2) / math.sqrt(5)
THETA = math.atan2(1, 2)
B_V1 = (1, -1)
B_V2 = (1, -2)
X_START = math.pi / 2
DAY32_V1 = (2, 1)
DAY32_V2 = (1, 1)
PERP_TURN = math.atan2(V2[1], V2[0]) - math.atan2(DAY32_V2[1], DAY32_V2[0])


def inverse(rows):
    return np.linalg.inv(np.array(rows, dtype=float))


def tex(*parts, colors=(), font_size=44):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def named(name, mat, font_size=44):
    return VGroup(MathTex(name, "=", color=Palette.text, font_size=font_size), mat).arrange(RIGHT, buff=0.2)


def number_matrix(rows):
    return matrix([[str(entry) for entry in row] for row in rows])


def corner_panel(content, corner=UL):
    content.to_corner(corner, buff=0.5)
    return VGroup(plate_for(content), content).set_z_index(10)


def name_label(tex_string, color, font_size=36):
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.08).set_z_index(6)


def tip_glow(point, scale=1.0):
    halo = Dot(point, radius=0.22 * scale, color=Palette.glow, fill_opacity=0.22)
    core = Dot(point, radius=0.075 * scale, color=Palette.glow)
    return VGroup(halo, core)


def safe_arrow_between(plane, start, end, color, stroke_width=6):
    """An arrow from start to end, or an empty mobject once it has shrunk to nothing."""
    if math.hypot(end[0] - start[0], end[1] - start[1]) < 0.12:
        return VMobject()
    return arrow_between(plane, start, end, color, stroke_width=stroke_width)


def riding_arrow(plane, live, coords, color, stroke_width=6):
    return safe_arrow_between(plane, (0, 0), tuple(live.point(coords)), color, stroke_width)


def follow_tip(label, plane, live, coords, direction, buff=0.14):
    label.add_updater(lambda m: m.next_to(plane.c2p(*live.point(coords)), direction, buff=buff))
    return label


def ellipse_axes(plane, rows, color=Palette.teal):
    """The two principal axes of the ellipse that `rows` makes from the unit circle, drawn end to end."""
    directions, lengths, _ = np.linalg.svd(np.array(rows, dtype=float))
    axes = VGroup()
    for index in range(2):
        reach = lengths[index] * directions[:, index]
        axes.add(DashedLine(plane.c2p(*-reach), plane.c2p(*reach), color=color, stroke_width=3, dash_length=0.12))
    return axes


def shadow_parts(x):
    """The pieces of the spectral decomposition for input x: its shadows on the eigenlines, and A x."""
    first = float(U1 @ x) * U1
    second = float(U2 @ x) * U2
    return first, second, 8 * first, 3 * second


class Lesson(LessonScene):
    day = 34
    title = "Symmetric matrices and the spectral theorem"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        self.plane = plane
        self.live = LiveTransform()
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.mirror()
        line = self.circle_to_ellipse(line)
        line = self.dot_product(line)
        line = self.not_symmetric(line)
        line = self.why_perpendicular(line)
        line = self.three_moves(line)
        line = self.shadow_pieces(line)
        self.close_episode(
            r"A symmetric matrix stretches along perpendicular eigenvectors,\\"
            r"so every one of them factors as $A = PDP^T$.",
            *self.mobjects,
        )

    def move_grid(self, rows, run_time=3.0, rate_func=spring_soft):
        self.play(self.live.apply(rows), run_time=run_time, rate_func=rate_func)

    def ask_question(self):
        day32_lines = VGroup(
            line_through_origin(self.plane, DAY32_V1, Palette.yellow, 4, dashed=True),
            line_through_origin(self.plane, DAY32_V2, Palette.blue, 4, dashed=True),
        )
        self.play(Create(day32_lines), run_time=1.0)
        line = self.say(r"On Day 32, eigenvectors could point in any directions.", hold=Timing.read_short)
        line = self.say(r"Which matrices always get eigenvectors at right angles?", line, hold=0.2)
        self.play(Rotate(day32_lines[1], angle=PERP_TURN, about_point=self.plane.c2p(0, 0)), run_time=1.4, rate_func=spring_soft)
        self.wait(Timing.beat)
        self.play(FadeOut(day32_lines), run_time=0.5)
        return line

    def mirror(self):
        line = self.ask_question()
        veil = scrim().set_z_index(20)
        self.add(veil)
        original = named("A", number_matrix(A), font_size=60).scale(1.25).move_to(LEFT * 3 + UP * 0.6)
        flipped = named("A^T", number_matrix(A), font_size=60).scale(1.25).move_to(RIGHT * 3 + UP * 0.6)
        VGroup(original, flipped).set_z_index(21)
        line = self.say(r"A matrix is \emph{symmetric} when it mirrors across its diagonal.", line, hold=0.2)
        self.play(FadeIn(original, shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        entries = original[1].get_entries()
        diagonal = DashedLine(entries[0].get_center() + UL * 0.45, entries[3].get_center() + DR * 0.45, color=Palette.text_muted, stroke_width=3).set_z_index(20.5)
        rings = VGroup(*[Circle(radius=0.36, color=Palette.glow, stroke_width=4).move_to(entries[i]) for i in (1, 2)]).set_z_index(22)
        self.play(Create(diagonal), run_time=0.8)
        self.play(Create(rings), run_time=0.8)
        self.wait(Timing.read_short)

        line = self.say(r"Flipping it over the diagonal gives its transpose $A^T$.", line, hold=0.2)
        targets = flipped[1].get_entries()
        pairs = ((0, 0), (1, 2), (2, 1), (3, 3))
        copies = [entries[i].copy() for i, _ in pairs]
        brackets = flipped[1].get_brackets()
        self.play(
            *[Transform(copy, targets[j], path_arc=-PI / 2 if i != j else 0) for copy, (i, j) in zip(copies, pairs)],
            FadeIn(brackets),
            run_time=1.6,
            rate_func=spring_soft,
        )
        self.play(FadeIn(flipped[0], shift=RIGHT * 0.1), run_time=0.5)
        self.remove(*copies, brackets, flipped[0])
        self.add(flipped)
        verdict = tex(r"A^T", "=", "A", colors=(None, Palette.glow, None), font_size=64).move_to(DOWN * 1.6).set_z_index(21)
        line = self.say(r"Every entry lands on its twin, so $A^T = A$.", line, hold=0.2)
        self.play(FadeIn(verdict, shift=UP * 0.1), run_time=0.7, rate_func=spring)
        self.wait(Timing.read_short)

        content = named("A", number_matrix(A))
        self.a_panel = corner_panel(content)
        self.play(
            FadeOut(VGroup(flipped, diagonal, rings, verdict)),
            Transform(original, content),
            FadeIn(self.a_panel[0]),
            FadeOut(veil),
            run_time=1.0,
        )
        self.remove(original)
        self.add(self.a_panel)
        return line

    def circle_to_ellipse(self, line):
        plane = self.plane
        self.grid = always_redraw(lambda: self.live.grid(plane, opacity=0.55))
        self.ghost = Circle(radius=PLANE_UNIT, color=Palette.purple_gray, stroke_width=3).move_to(plane.c2p(0, 0))
        self.curve = always_redraw(lambda: circle_image(plane, self.live.value, color=Palette.teal))
        line = self.say(r"Start with the unit circle, every vector of length 1.", line, hold=0.2)
        self.play(plane.animate.set_opacity(0.25), FadeIn(self.grid), run_time=0.8)
        self.play(Create(self.ghost), run_time=1.0)
        self.add(self.curve)
        self.bring_to_front(self.a_panel)

        line = self.say(r"Mark the unit eigenvectors $\mathbf u_1$ and $\mathbf u_2$ of $A$.", line, hold=0.2)
        self.eigen_lines = VGroup(
            line_through_origin(plane, V1, Palette.yellow, 3, dashed=True, opacity=0.7),
            line_through_origin(plane, V2, Palette.blue, 3, dashed=True, opacity=0.7),
        )
        self.play(Create(self.eigen_lines), run_time=1.0)
        self.eigen_arrows = self.riding_eigen_arrows(U1, U2)
        self.grow_then_follow(self.eigen_arrows, U1, U2)
        self.bring_to_front(self.a_panel)
        self.wait(Timing.beat)

        line = self.say(r"Now let $A$ act on the whole plane.", line, hold=0.2)
        self.move_grid(A, run_time=4.0)
        line = self.say(r"The circle becomes an ellipse whose axes are the eigenvectors.", line, hold=0.2)
        self.play(*[Flash(plane.c2p(*self.live.point(u)), color=Palette.glow, line_length=0.2, flash_radius=0.3) for u in (U1, U2)], run_time=1.0)
        self.wait(Timing.read_short)
        return self.name_half_lengths(line)

    def grow_then_follow(self, riders, first, second):
        """Grow still copies of the two eigenvector arrows, then hand over to the arrows that ride the transform."""
        stills = VGroup(*[arrow_between(self.plane, (0, 0), self.live.point(u), color) for u, color in ((first, Palette.yellow), (second, Palette.blue))])
        self.play(*[GrowArrow(still) for still in stills], FadeIn(riders[1]), run_time=0.9, rate_func=spring_soft)
        self.remove(*stills)
        self.add(riders)

    def riding_eigen_arrows(self, first, second, labels=(r"\mathbf u_1", r"\mathbf u_2")):
        plane, live = self.plane, self.live
        arrows = VGroup(
            always_redraw(lambda: riding_arrow(plane, live, first, Palette.yellow)),
            always_redraw(lambda: riding_arrow(plane, live, second, Palette.blue)),
        )
        tags = VGroup(
            follow_tip(name_label(labels[0], Palette.yellow), plane, live, first, DR),
            follow_tip(name_label(labels[1], Palette.blue), plane, live, second, LEFT),
        )
        return VGroup(arrows, tags)

    def name_half_lengths(self, line):
        plane = self.plane
        glows = VGroup(*[tip_glow(plane.c2p(*self.live.point(u))) for u in (U1, U2)])
        stretch_tags = VGroup(
            name_label(r"8\,\mathbf u_1", Palette.yellow, font_size=40).next_to(plane.c2p(*(8 * U1)), UP, buff=0.2),
            name_label(r"3\,\mathbf u_2", Palette.blue, font_size=40).next_to(plane.c2p(*(3 * U2)), UL, buff=0.1),
        )
        line = self.say(r"Its half-lengths are the eigenvalues, 8 and 3.", line, hold=0.2)
        self.play(FadeOut(self.eigen_arrows[1]), LaggedStart(*[GrowFromCenter(glow) for glow in glows], lag_ratio=0.2), run_time=0.8)
        self.play(FadeIn(stretch_tags, shift=UP * 0.1), run_time=0.7, rate_func=spring)
        self.wait(Timing.read_short)
        self.corner = right_angle_mark(plane, V1, V2, size=0.34)
        line = self.say(r"And the two eigenvectors meet at a right angle.", line, hold=0.2)
        self.play(Create(self.corner), run_time=0.8)
        self.wait(Timing.read_short)
        self.centerpiece_marks = VGroup(glows, stretch_tags)
        return line

    def dot_product(self, line):
        rows = VGroup(
            tex(r"\mathbf u \cdot \mathbf v = u_1v_1 + u_2v_2", font_size=36),
            tex(r"\begin{bmatrix} 2 \\ 1 \end{bmatrix}", r"\cdot", r"\begin{bmatrix} -1 \\ 2 \end{bmatrix}", r"= -2 + 2 = 0", colors=(Palette.yellow, None, Palette.blue, None), font_size=36),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        rows.to_edge(RIGHT, buff=0.55).set_y(-1.85).set_z_index(11)
        plate = plate_for(rows).set_z_index(10)
        line = self.say(r"The \emph{dot product} multiplies matching entries and adds.", line, hold=0.2)
        self.play(FadeIn(plate), FadeIn(rows[0], shift=DOWN * 0.1), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"A dot product of 0 means the arrows are perpendicular.", line, hold=0.2)
        self.play(FadeIn(rows[1], shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.play(Indicate(self.corner, color=Palette.glow, scale_factor=1.4), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"Day 35 explains why a zero dot product means a right angle.", line)
        self.play(FadeOut(VGroup(plate, rows, self.centerpiece_marks, self.eigen_arrows[0], self.corner, self.eigen_lines)), run_time=0.8)
        self.move_grid(inverse(A), run_time=1.6)
        return line

    def not_symmetric(self, line):
        plane = self.plane
        b_panel = corner_panel(VGroup(named("B", number_matrix(B)), tex(r"B^T \ne B", font_size=40)).arrange(DOWN, buff=0.3), corner=UR)
        lines = VGroup(
            line_through_origin(plane, B_V1, Palette.yellow, 3, dashed=True, opacity=0.7),
            line_through_origin(plane, B_V2, Palette.blue, 3, dashed=True, opacity=0.7),
        )
        line = self.say(r"Compare a matrix $B$ that is not symmetric.", line, hold=0.2)
        self.play(FadeOut(self.a_panel), FadeIn(b_panel, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        line = self.say(r"Its two eigenlines are not perpendicular.", line, hold=0.2)
        self.play(Create(lines), run_time=1.0)
        first, second = (np.array(v) / np.linalg.norm(v) for v in (B_V1, B_V2))
        arrows = self.riding_eigen_arrows(first, second, labels=(r"\mathbf v_1", r"\mathbf v_2"))
        self.grow_then_follow(arrows, first, second)
        self.wait(Timing.beat)

        line = self.say(r"Apply $B$, and the circle still becomes an ellipse.", line, hold=0.2)
        self.move_grid(B, run_time=3.5)
        axes = ellipse_axes(plane, B)
        line = self.say(r"But its axes point in directions of their own.", line, hold=0.2)
        self.play(Create(axes), run_time=1.2)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(axes, lines, arrows)), FadeOut(b_panel), run_time=0.8)
        self.move_grid(inverse(B), run_time=1.4)
        return line

    def why_perpendicular(self, line):
        veil = scrim().set_z_index(20)
        steps = VGroup(
            tex(r"(A\mathbf v_1) \cdot \mathbf v_2", "=", r"\mathbf v_1^T", r"A^T", r"\mathbf v_2", "=", r"\mathbf v_1 \cdot (A\mathbf v_2)", colors=(None, None, None, Palette.glow), font_size=50),
            tex(r"\lambda_1\,\mathbf v_1 \cdot \mathbf v_2", "=", r"\lambda_2\,\mathbf v_1 \cdot \mathbf v_2", font_size=50),
            tex(r"(\lambda_1 - \lambda_2)\,\mathbf v_1 \cdot \mathbf v_2 = 0", r"\;\Longrightarrow\;", r"\mathbf v_1 \cdot \mathbf v_2 = 0", colors=(None, None, Palette.glow), font_size=50),
        ).arrange(DOWN, buff=0.6).move_to(UP * 0.5).set_z_index(21)
        line = self.say(r"Here is why a symmetric $A$ forces the right angle.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(FadeIn(steps[0], shift=UP * 0.1), run_time=0.8)
        line = self.say(r"Because $A^T = A$, the matrix can hop across the dot.", line, hold=Timing.read_short)
        line = self.say(r"Each side is an eigenvector times its eigenvalue.", line, hold=0.2)
        self.play(FadeIn(steps[1], shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"Different eigenvalues leave only $\mathbf v_1 \cdot \mathbf v_2 = 0$.", line, hold=0.2)
        self.play(FadeIn(steps[2], shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        self.play(FadeOut(steps), FadeOut(veil), run_time=0.7)
        return line

    def three_moves(self, line):
        formula = tex("A", "=", "P", "D", "P^T", font_size=60)
        key = VGroup(
            tex(r"P = \begin{bmatrix} \mathbf u_1 & \mathbf u_2 \end{bmatrix}", font_size=38),
            tex(r"D = \begin{bmatrix} 8 & 0 \\ 0 & 3 \end{bmatrix}", font_size=38),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        key[0][0][3:5].set_color(Palette.yellow)
        key[0][0][5:7].set_color(Palette.blue)
        panel = corner_panel(VGroup(formula, key).arrange(DOWN, buff=0.35, aligned_edge=LEFT))
        self.moves_panel = panel
        self.eigen_arrows = self.riding_eigen_arrows(U1, U2)
        line = self.say(r"Every symmetric matrix splits into three simple moves.", line, hold=0.2)
        self.play(FadeIn(panel, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        self.play(Create(self.eigen_lines), run_time=0.9)
        self.grow_then_follow(self.eigen_arrows, U1, U2)
        self.bring_to_front(panel)
        self.wait(Timing.beat)
        line = self.say(r"Perpendicular unit eigenvectors make $P^{-1}$ simply $P^T$.", line)

        cursor = SurroundingRectangle(formula[4], color=Palette.glow, buff=0.1, stroke_width=3).set_z_index(12)
        line = self.say(r"First $P^T$ turns the eigenvectors onto the axes.", line, hold=0.2)
        self.play(Create(cursor), run_time=0.5)
        self.play(self.live.rotate(-THETA), run_time=2.2, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Then $D$ stretches along the axes by 8 and 3.", line, hold=0.2)
        self.play(cursor.animate.become(SurroundingRectangle(formula[3], color=Palette.glow, buff=0.1, stroke_width=3)), run_time=0.5, rate_func=spring)
        self.move_grid(D, run_time=2.6)
        self.wait(Timing.beat)
        line = self.say(r"Then $P$ turns everything back, and the result is $A$.", line, hold=0.2)
        self.play(cursor.animate.become(SurroundingRectangle(formula[2], color=Palette.glow, buff=0.1, stroke_width=3)), run_time=0.5, rate_func=spring)
        self.play(self.live.rotate(THETA), run_time=2.2, rate_func=spring_soft)
        self.wait(Timing.beat)
        self.play(FadeOut(cursor), run_time=0.4)
        line = self.say(r"The \emph{spectral theorem} says every symmetric matrix works this way.", line, hold=Timing.read_short)
        return line

    def shadow_pieces(self, line):
        plane = self.plane
        angle = ValueTracker(X_START)
        self.play(FadeOut(self.eigen_arrows), FadeOut(self.moves_panel), run_time=0.6)
        self.remove(self.curve, self.grid)
        self.add(circle_image(plane, A, color=Palette.teal).set_stroke(opacity=0.7), self.live.grid(plane, opacity=0.35))
        self.bring_to_front(self.ghost, self.eigen_lines)

        def current():
            return np.array([math.cos(angle.get_value()), math.sin(angle.get_value())])

        x_arrow = always_redraw(lambda: safe_arrow_between(plane, (0, 0), current(), Palette.purple_gray, 6))
        drops = always_redraw(lambda: self.shadow_drops(current()))
        pieces = always_redraw(lambda: self.shadow_arrows(current()))
        result = always_redraw(lambda: safe_arrow_between(plane, (0, 0), 8 * shadow_parts(current())[0] + 3 * shadow_parts(current())[1], Palette.teal, 6))
        x_tag = name_label(r"\mathbf x", Palette.purple_gray).next_to(plane.c2p(0, 1), UP, buff=0.1)

        line = self.say(r"Now split a vector $\mathbf x$ into its shadows on the eigenlines.", line, hold=0.2)
        x_still = safe_arrow_between(plane, (0, 0), current(), Palette.purple_gray, 6)
        self.play(GrowArrow(x_still), FadeIn(x_tag), run_time=0.8, rate_func=spring_soft)
        self.remove(x_still)
        self.add(x_arrow)
        self.play(FadeIn(drops), run_time=0.8)
        self.wait(Timing.beat)
        formula = tex(r"A\mathbf x", "=", r"8\,(\mathbf u_1 \cdot \mathbf x)\,\mathbf u_1", "+", r"3\,(\mathbf u_2 \cdot \mathbf x)\,\mathbf u_2", colors=(Palette.teal, None, Palette.yellow, None, Palette.blue), font_size=40)
        panel = corner_panel(formula)
        line = self.say(r"$A$ stretches one shadow by 8 and the other by 3.", line, hold=0.2)
        self.play(FadeIn(panel, shift=DOWN * 0.1), FadeIn(pieces), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.beat)
        ax_tag = name_label(r"A\mathbf x", Palette.teal, font_size=40).next_to(plane.c2p(*A[1]), UL, buff=0.1)
        line = self.say(r"Added tip to tail, the two pieces rebuild $A\mathbf x$.", line, hold=0.2)
        result_still = safe_arrow_between(plane, (0, 0), (2, 4), Palette.teal, 6)
        self.play(GrowArrow(result_still), FadeIn(ax_tag), run_time=0.9, rate_func=spring_soft)
        self.remove(result_still)
        self.add(result)
        self.wait(Timing.beat)

        line = self.say(r"As $\mathbf x$ circles, $A\mathbf x$ traces out the ellipse.", line, hold=0.2)
        self.play(FadeOut(x_tag), FadeOut(ax_tag), run_time=0.4)
        self.play(angle.animate.set_value(X_START + 2 * PI), run_time=6.0, rate_func=smooth)
        self.wait(Timing.beat)
        whole = tex("A", "=", r"8\,\mathbf u_1\mathbf u_1^T", "+", r"3\,\mathbf u_2\mathbf u_2^T", colors=(None, None, Palette.yellow, None, Palette.blue), font_size=48)
        new_panel = corner_panel(whole)
        line = self.say(r"So $A$ is a sum of stretched projections, its \emph{spectral decomposition}.", line, hold=0.2)
        self.play(FadeOut(panel), FadeIn(new_panel, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_long)
        return line

    def shadow_drops(self, x):
        plane = self.plane
        first, second, _, _ = shadow_parts(x)
        parts = VGroup()
        for foot, color in ((first, Palette.yellow), (second, Palette.blue)):
            if np.linalg.norm(x - foot) > 0.05:
                parts.add(DashedLine(plane.c2p(*x), plane.c2p(*foot), color=color, stroke_width=3.5, dash_length=0.06))
            parts.add(Dot(plane.c2p(*foot), radius=0.08, color=color))
        return parts

    def shadow_arrows(self, x):
        _, _, stretched_first, stretched_second = shadow_parts(x)
        return VGroup(
            safe_arrow_between(self.plane, (0, 0), stretched_first, Palette.yellow, 5),
            safe_arrow_between(self.plane, stretched_first, stretched_first + stretched_second, Palette.blue, 5),
        )


def scene_plane(origin=PLANE_ORIGIN):
    plane = plane_at(origin, PLANE_UNIT)
    plane.set_opacity(0.25)
    return plane


def centerpiece(plane, rows=A, with_tags=True):
    """The unit circle, its ellipse under a symmetric matrix, and the stretched eigenvectors on its axes."""
    parts = VGroup(
        LiveTransform(rows).grid(plane, opacity=0.4),
        Circle(radius=PLANE_UNIT, color=Palette.purple_gray, stroke_width=3).move_to(plane.c2p(0, 0)),
        line_through_origin(plane, V1, Palette.yellow, 3, dashed=True, opacity=0.7),
        line_through_origin(plane, V2, Palette.blue, 3, dashed=True, opacity=0.7),
        circle_image(plane, rows, color=Palette.teal),
        arrow_between(plane, (0, 0), 8 * U1, Palette.yellow),
        arrow_between(plane, (0, 0), 3 * U2, Palette.blue),
        tip_glow(plane.c2p(*(8 * U1))),
        tip_glow(plane.c2p(*(3 * U2))),
        right_angle_mark(plane, V1, V2, size=0.34),
    )
    if with_tags:
        parts.add(
            name_label(r"8\,\mathbf u_1", Palette.yellow, font_size=40).next_to(plane.c2p(*(8 * U1)), UP, buff=0.2),
            name_label(r"3\,\mathbf u_2", Palette.blue, font_size=40).next_to(plane.c2p(*(3 * U2)), UL, buff=0.1),
        )
    return parts


class FigCircleToEllipse(Scene):
    def construct(self):
        plane = scene_plane()
        self.add(plane, centerpiece(plane), corner_panel(named("A", number_matrix(A))))


class FigNotSymmetric(Scene):
    def construct(self):
        plane = scene_plane()
        first, second = (np.array(v) / np.linalg.norm(v) for v in (B_V1, B_V2))
        self.add(
            plane,
            LiveTransform(B).grid(plane, opacity=0.4),
            Circle(radius=PLANE_UNIT, color=Palette.purple_gray, stroke_width=3).move_to(plane.c2p(0, 0)),
            line_through_origin(plane, B_V1, Palette.yellow, 3, dashed=True, opacity=0.7),
            line_through_origin(plane, B_V2, Palette.blue, 3, dashed=True, opacity=0.7),
            circle_image(plane, B, color=Palette.teal),
            ellipse_axes(plane, B),
            arrow_between(plane, (0, 0), 5 * first, Palette.yellow),
            arrow_between(plane, (0, 0), 3 * second, Palette.blue),
            name_label(r"5\,\mathbf v_1", Palette.yellow, font_size=40).next_to(plane.c2p(*(5 * first)), RIGHT, buff=0.15),
            name_label(r"3\,\mathbf v_2", Palette.blue, font_size=40).next_to(plane.c2p(*(3 * second)), LEFT, buff=0.15),
            corner_panel(VGroup(named("B", number_matrix(B)), tex(r"B^T \ne B", font_size=40)).arrange(DOWN, buff=0.3), corner=UR),
        )


class FigThreeMoves(Scene):
    def construct(self):
        stages = (np.eye(2), rotation(-THETA), np.array(D) @ rotation(-THETA), np.array(A, dtype=float))
        panels = VGroup(*[self.small_plane(rows) for rows in stages])
        panels[0].move_to(LEFT * 3.1 + UP * 2.25)
        panels[1].move_to(RIGHT * 3.1 + UP * 2.25)
        panels[2].move_to(RIGHT * 3.1 + DOWN * 2.25)
        panels[3].move_to(LEFT * 3.1 + DOWN * 2.25)
        self.add(panels)
        moves = (
            (panels[0].get_right(), panels[1].get_left(), "P^T", UP),
            (panels[1].get_bottom(), panels[2].get_top(), "D", RIGHT),
            (panels[2].get_left(), panels[3].get_right(), "P", UP),
        )
        for start, end, name, side in moves:
            arrow = Arrow(start, end, buff=0.15, color=Palette.text, stroke_width=5)
            self.add(arrow, MathTex(name, color=Palette.glow, font_size=48).next_to(arrow, side, buff=0.15))
        fit_to_frame(self)

    @staticmethod
    def small_plane(rows):
        unit = 0.3
        plane = make_plane(x_range=(-8, 8, 1), y_range=(-5, 5, 1), x_length=16 * unit, y_length=10 * unit)
        plane.set_opacity(0.2)
        first, second = rows @ U1, rows @ U2
        return VGroup(
            plane,
            Circle(radius=unit, color=Palette.purple_gray, stroke_width=2.5).move_to(plane.c2p(0, 0)),
            circle_image(plane, rows, color=Palette.teal, stroke_width=4),
            arrow_between(plane, (0, 0), first, Palette.yellow, stroke_width=5),
            arrow_between(plane, (0, 0), second, Palette.blue, stroke_width=5),
            right_angle_mark(plane, first, second, size=0.1, stroke_width=2.5),
        )


def rotation(angle):
    return np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])


class FigShadowPieces(Scene):
    def construct(self):
        plane = scene_plane()
        x = np.array([0.0, 1.0])
        first, second, stretched_first, stretched_second = shadow_parts(x)
        self.add(
            plane,
            Circle(radius=PLANE_UNIT, color=Palette.purple_gray, stroke_width=3).move_to(plane.c2p(0, 0)),
            line_through_origin(plane, V1, Palette.yellow, 3, dashed=True, opacity=0.7),
            line_through_origin(plane, V2, Palette.blue, 3, dashed=True, opacity=0.7),
            circle_image(plane, A, color=Palette.teal).set_stroke(opacity=0.7),
            DashedLine(plane.c2p(*x), plane.c2p(*first), color=Palette.yellow, stroke_width=2.5, dash_length=0.06),
            DashedLine(plane.c2p(*x), plane.c2p(*second), color=Palette.blue, stroke_width=2.5, dash_length=0.06),
            arrow_between(plane, (0, 0), stretched_first, Palette.yellow, stroke_width=5),
            arrow_between(plane, stretched_first, stretched_first + stretched_second, Palette.blue, stroke_width=5),
            arrow_between(plane, (0, 0), (2, 4), Palette.teal),
            arrow_between(plane, (0, 0), x, Palette.purple_gray, stroke_width=5),
            name_label(r"\mathbf x", Palette.purple_gray).next_to(plane.c2p(0, 1), UP, buff=0.1),
            name_label(r"A\mathbf x", Palette.teal, font_size=40).next_to(plane.c2p(2, 4), UL, buff=0.1),
            corner_panel(tex(r"A\mathbf x", "=", r"8\,(\mathbf u_1 \cdot \mathbf x)\,\mathbf u_1", "+", r"3\,(\mathbf u_2 \cdot \mathbf x)\,\mathbf u_2", colors=(Palette.teal, None, Palette.yellow, None, Palette.blue), font_size=40)),
        )


class Poster(Scene):
    def construct(self):
        plane = scene_plane()
        formula = backed(tex("A", "=", "P", "D", "P^T", font_size=72), padding=0.25).to_corner(UL, buff=0.6)
        self.add(plane, centerpiece(plane, with_tags=False), formula)
