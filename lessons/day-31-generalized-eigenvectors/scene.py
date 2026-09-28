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
    patch_image,
    plane_at,
    plate_for,
    scrim,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (0.0, -0.1)
PLANE_UNIT = 1.2
S = ((1, 1), (0, 1))
S_INVERSE = ((1, -1), (0, 1))
N = ((0, 1), (0, 0))
V2 = (1, 2)
S_V2 = (3, 2)
V1 = (2, 0)
FAN_LENGTH = 1.5
FAN_DEGREES = (0, 30, 60, 90, 120, 150)
BASIS_COLORS = (Palette.i_hat, Palette.j_hat)
CHAIN_TEX = (r"\mathbf v_2", r"\xrightarrow{\;S - I\;}", r"\mathbf v_1", r"\xrightarrow{\;S - I\;}", r"\mathbf 0")
CHAIN_COLORS = (Palette.blue, None, Palette.yellow, None, Palette.glow)


def tex(*parts, colors=(), font_size=44):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def basis_matrix(rows):
    """A 2x2 matrix whose first column is green (where e1 lands) and second red (where e2 lands)."""
    mat = matrix([[str(entry) for entry in row] for row in rows])
    for index, color in enumerate(BASIS_COLORS):
        mat.get_columns()[index].set_color(color)
    return mat


def named(name, mat, font_size=44):
    return VGroup(MathTex(name, "=", color=Palette.text, font_size=font_size), mat).arrange(RIGHT, buff=0.2)


def corner_panel(content, corner=UL):
    content.to_corner(corner, buff=0.5)
    return VGroup(plate_for(content), content).set_z_index(10)


def name_label(tex_string, color, point, direction, font_size=38, buff=0.12):
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.08).next_to(point, direction, buff=buff)


def tip_glow(point, scale=1.0):
    halo = Dot(point, radius=0.22 * scale, color=Palette.glow, fill_opacity=0.22)
    core = Dot(point, radius=0.075 * scale, color=Palette.glow)
    return VGroup(halo, core)


def origin_ring(plane):
    return Circle(radius=0.26, color=Palette.glow, stroke_width=4).move_to(plane.c2p(0, 0))


def safe_arrow(plane, coords, color, stroke_width=6):
    """An arrow to coords, or a dot at the origin once it has shrunk to nothing."""
    if math.hypot(*coords) < 0.08:
        return Dot(plane.c2p(0, 0), radius=0.08, color=color)
    return vector_arrow(coords, color, plane, stroke_width=stroke_width)


def riding_arrow(plane, live, coords, color, stroke_width=6):
    return safe_arrow(plane, tuple(live.point(coords)), color, stroke_width)


def fan_directions():
    angles = [math.radians(degrees + turn) for degrees in FAN_DEGREES for turn in (0, 180)]
    return [(FAN_LENGTH * math.cos(angle), FAN_LENGTH * math.sin(angle)) for angle in angles]


def is_horizontal(direction):
    return abs(direction[1]) < 1e-6


def off_line(direction, image):
    """The sine of the angle between image and the line through direction: 0 when image stays on that line."""
    length = math.hypot(*image)
    if length < 1e-6:
        return 0.0
    unit = np.array(direction) / math.hypot(*direction)
    return abs(unit[0] * image[1] - unit[1] * image[0]) / length


def fan_arrow(plane, image, direction):
    arrow = vector_arrow(image, Palette.purple_gray, plane, stroke_width=5)
    knocked = min(1.0, off_line(direction, image) / 0.3)
    return arrow.set_opacity(1.0 - 0.72 * knocked)


def fan_lines(plane, opacity=0.4):
    return VGroup(*[line_through_origin(plane, fan_directions()[2 * i], Palette.purple_gray, 2.5, dashed=True, opacity=opacity) for i in range(len(FAN_DEGREES))])


def eigenline(plane):
    return line_through_origin(plane, (1, 0), Palette.yellow, 5)


def eigen_label(plane):
    return name_label(r"\lambda = 1", Palette.yellow, plane.c2p(4.6, 0), UP, font_size=40)


def chain_label(font_size=44):
    return tex(*CHAIN_TEX, colors=CHAIN_COLORS, font_size=font_size)


def live_patch(plane, live):
    return always_redraw(lambda: patch_image(plane, live.value))


def block_frame(mat, rows, columns):
    """A thin sharp rectangle around the entries in the given row and column ranges of a Matrix."""
    cells = VGroup(*[mat.get_rows()[r][c] for r in rows for c in columns])
    return SurroundingRectangle(cells, color=Palette.text_muted, buff=0.14, stroke_width=2.5)


class Lesson(LessonScene):
    day = 31
    title = "Generalized eigenvectors"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        self.plane = plane
        self.live = LiveTransform()
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.meet_shear()
        line = self.tip_the_fan(line)
        line = self.multiplicities(line)
        line = self.push_v2(line)
        line = self.slide_push(line)
        line = self.squash_twice(line)
        line = self.generalized(line)
        line = self.jordan_block(line)
        line = self.jordan_form(line)
        self.close_episode(
            r"When eigenvectors run short, $A - \lambda I$ builds a chain.\\"
            r"Each push moves a vector one step down, until it reaches $\mathbf 0$.",
            *self.mobjects,
        )

    def move_grid(self, rows, run_time=2.4, rate_func=spring_soft, *extra):
        self.play(self.live.apply(rows), *extra, run_time=run_time, rate_func=rate_func)

    def meet_shear(self):
        plane = self.plane
        self.s_panel = corner_panel(named("S", basis_matrix(S)))
        line = self.say(r"Here is the shear $S$ from Day 5.", hold=0.2)
        self.play(FadeIn(self.s_panel, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        self.patch = live_patch(plane, self.live)
        self.play(plane.animate.set_opacity(0.25), FadeIn(self.patch), run_time=0.9)
        self.bring_to_front(self.s_panel)
        self.wait(Timing.beat)
        return line

    def tip_the_fan(self, line):
        plane = self.plane
        directions = fan_directions()
        lines = fan_lines(plane)
        still = VGroup(*[vector_arrow(d, Palette.purple_gray, plane, stroke_width=5) for d in directions])
        line = self.say(r"Draw twelve directions, then let $S$ act.", line, hold=0.2)
        self.play(LaggedStart(*[GrowArrow(arrow) for arrow in still], lag_ratio=0.06), run_time=1.5)
        self.play(Create(lines, lag_ratio=0.1), run_time=1.1)
        live_fan = VGroup(*[always_redraw(lambda d=d: fan_arrow(plane, self.live.point(d), d)) for d in directions])
        self.remove(*still)
        self.add(*live_fan)
        self.bring_to_front(self.s_panel)
        self.move_grid(S, run_time=3.6, rate_func=smooth)
        line = self.say(r"Every arrow tips over except the horizontal pair.", line, hold=Timing.read_short)
        line = self.light_eigenline(line, live_fan, directions)
        tipped = [arrow for arrow, d in zip(live_fan, directions) if not is_horizontal(d)]
        self.play(*[FadeOut(arrow) for arrow in tipped], FadeOut(lines), FadeOut(self.eigen_arrows), run_time=0.7)
        self.move_grid(S_INVERSE, run_time=1.4)
        return line

    def light_eigenline(self, line, live_fan, directions):
        plane = self.plane
        self.eigenline = eigenline(plane)
        self.eigen_label = eigen_label(plane)
        yellow = VGroup()
        glows = VGroup()
        for arrow, direction in zip(live_fan, directions):
            if is_horizontal(direction):
                self.remove(arrow)
                yellow.add(vector_arrow(direction, Palette.yellow, plane, stroke_width=6))
                glows.add(tip_glow(plane.c2p(*direction)))
        self.add(yellow)
        line = self.say(r"So $S$ has just one line of eigenvectors, for $\lambda = 1$.", line, hold=0.2)
        self.play(Create(self.eigenline), run_time=1.0)
        self.bring_to_front(yellow)
        self.play(LaggedStart(*[GrowFromCenter(glow) for glow in glows], lag_ratio=0.2), run_time=0.8)
        self.play(FadeIn(self.eigen_label, shift=UP * 0.1), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        self.eigen_arrows = VGroup(yellow, glows)
        return line

    def multiplicities(self, line):
        veil = scrim().set_z_index(20)
        poly = tex(r"\det(S - \lambda I) = (1 - \lambda)", "^2", colors=(None, Palette.glow), font_size=60)
        algebraic = tex(r"\text{algebraic multiplicity}", "=", "2", colors=(None, None, Palette.glow), font_size=46)
        shifted = named(r"S - I", matrix([["0", "1"], ["0", "0"]]), font_size=54)
        null = tex(r"\operatorname{Nul}(S - I) = \operatorname{Span}\{\mathbf e_1\}", font_size=46)
        geometric = tex(r"\text{geometric multiplicity}", "=", "1", colors=(None, None, Palette.yellow), font_size=46)
        left = VGroup(poly, algebraic).arrange(DOWN, buff=0.55)
        right = VGroup(VGroup(shifted, null).arrange(RIGHT, buff=0.5), geometric).arrange(DOWN, buff=0.55)
        board = VGroup(left, right).arrange(DOWN, buff=0.7).set_z_index(21)
        line = self.say(r"The characteristic polynomial counts $\lambda = 1$ twice.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(Write(poly), run_time=1.2)
        self.play(FadeIn(algebraic, shift=UP * 0.1), run_time=0.7)
        self.wait(Timing.read_short)
        line = self.say(r"But $S - I$ has rank 1, so its null space is one line.", line, hold=0.2)
        self.play(FadeIn(right[0], shift=UP * 0.1), run_time=0.9, rate_func=spring_soft)
        self.play(FadeIn(geometric, shift=UP * 0.1), run_time=0.7)
        self.wait(Timing.read_short)
        return self.call_defective(line, board, veil, algebraic, geometric)

    def call_defective(self, line, board, veil, algebraic, geometric):
        verdict = tex(r"1 < 2", font_size=56).set_z_index(21)
        word = Tex(r"defective", color=Palette.glow, font_size=56).set_z_index(21)
        VGroup(verdict, word).arrange(RIGHT, buff=0.6).next_to(board, DOWN, buff=0.5)
        VGroup(board, verdict, word).move_to(UP * 0.55)
        line = self.say(r"One eigen-direction short, $S$ is called \emph{defective}.", line, hold=0.2)
        self.play(TransformFromCopy(geometric[2], verdict[0][0]), TransformFromCopy(algebraic[2], verdict[0][2]), FadeIn(verdict[0][1]), run_time=1.1, rate_func=spring)
        self.play(FadeIn(word, shift=LEFT * 0.1), run_time=0.7, rate_func=spring)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(board, verdict, word)), FadeOut(veil), run_time=0.8)
        return line

    def push_v2(self, line):
        plane = self.plane
        self.v2_arrow = vector_arrow(V2, Palette.blue, plane)
        self.v2_label = name_label(r"\mathbf v_2", Palette.blue, plane.c2p(*V2), LEFT)
        self.v2_line = line_through_origin(plane, V2, Palette.blue, 2.5, dashed=True, opacity=0.6)
        line = self.say(r"Take $\mathbf v_2 = (1, 2)$, which sits off the eigenline.", line, hold=0.2)
        self.play(GrowArrow(self.v2_arrow), FadeIn(self.v2_label), run_time=1.0, rate_func=spring_soft)
        self.play(Create(self.v2_line), run_time=0.9)
        self.bring_to_front(self.v2_arrow, self.v2_label)
        self.wait(Timing.beat)

        riding = always_redraw(lambda: riding_arrow(plane, self.live, V2, Palette.teal))
        self.add(riding)
        self.bring_to_front(self.v2_arrow, self.v2_label, self.s_panel)
        line = self.say(r"The shear carries $\mathbf v_2$ to $S\mathbf v_2 = (3, 2)$.", line, hold=0.2)
        self.move_grid(S, run_time=2.4)
        self.remove(riding)
        self.sv2_arrow = vector_arrow(S_V2, Palette.teal, plane)
        self.add(self.sv2_arrow)
        self.bring_to_front(self.v2_arrow, self.v2_label)
        self.sv2_label = name_label(r"S\mathbf v_2", Palette.teal, plane.c2p(*S_V2), RIGHT)
        self.play(FadeIn(self.sv2_label, shift=LEFT * 0.1), run_time=0.6, rate_func=spring)
        self.wait(Timing.beat)

        self.push = Arrow(plane.c2p(*V2), plane.c2p(*S_V2), buff=0, color=Palette.pink, stroke_width=7, max_tip_length_to_length_ratio=0.18)
        self.push_label = name_label(r"(S - I)\mathbf v_2", Palette.pink, self.push.get_center(), UP, font_size=36, buff=0.2)
        line = self.say(r"The push between them is $(S - I)\mathbf v_2 = S\mathbf v_2 - \mathbf v_2$.", line, hold=0.2)
        self.play(GrowArrow(self.push), run_time=1.0, rate_func=spring_soft)
        self.play(FadeIn(self.push_label, shift=DOWN * 0.1), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        return line

    def slide_push(self, line):
        plane = self.plane
        self.chain = chain_label()
        self.chain_panel = corner_panel(self.chain, UR)
        v1_label = name_label(r"\mathbf v_1", Palette.yellow, plane.c2p(*V1), DOWN, buff=0.2)
        glow = tip_glow(plane.c2p(*V1))
        line = self.say(r"Slid to the origin, the push lies on the eigenline.", line, hold=0.2)
        self.play(FadeOut(self.push_label), run_time=0.4)
        self.play(self.push.animate.shift(plane.c2p(0, 0) - plane.c2p(*V2)).set_color(Palette.yellow), run_time=1.6, rate_func=spring_soft)
        self.play(GrowFromCenter(glow), FadeIn(v1_label, shift=UP * 0.1), run_time=0.7, rate_func=spring)
        self.chain_panel[0].set_z_index(10)
        self.play(FadeIn(self.chain_panel[0]), FadeIn(self.chain[:3], shift=LEFT * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"So $\mathbf v_1 = (S - I)\mathbf v_2$ is an eigenvector of $S$.", line, hold=Timing.read_short)
        self.play(FadeOut(VGroup(self.sv2_arrow, self.sv2_label, glow, v1_label)), run_time=0.6)
        self.move_grid(S_INVERSE, run_time=1.4)
        self.v1_arrow = self.push
        return line

    def squash_twice(self, line):
        plane = self.plane
        self.remove(self.v2_arrow, self.v1_arrow)
        ghost = vector_arrow(V2, Palette.blue, plane, stroke_width=4).set_opacity(0.3)
        riders = VGroup(
            always_redraw(lambda: riding_arrow(plane, self.live, V1, Palette.yellow)),
            always_redraw(lambda: riding_arrow(plane, self.live, V2, Palette.blue)),
        )
        self.bring_to_front(self.patch)
        self.add(ghost, riders)
        self.bring_to_front(self.v2_label, self.s_panel, self.chain_panel)
        line = self.say(r"Apply $S - I$ to the patch, and it squashes onto the eigenline.", line, hold=0.2)
        self.move_grid(N, 3.0, spring_soft, FadeOut(self.v2_label), FadeOut(self.v2_line))
        landed = name_label(r"(S - I)\mathbf v_2 = \mathbf v_1", Palette.blue, plane.c2p(*V1), DOWN, font_size=36, buff=0.2)
        self.play(FadeIn(landed, shift=UP * 0.1), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        line = self.say(r"A second push sends the whole line to $\mathbf 0$.", line, hold=0.2)
        self.play(FadeOut(landed), run_time=0.4)
        self.move_grid(N, run_time=2.4)
        ring = origin_ring(plane)
        self.play(GrowFromCenter(ring), FadeIn(self.chain[3:], shift=LEFT * 0.1), run_time=0.8, rate_func=spring)
        self.wait(Timing.read_short)
        self.squash_parts = VGroup(ghost, riders, ring)
        return line

    def generalized(self, line):
        self.veil = scrim().set_z_index(20)
        first = tex(r"(S - I)\mathbf v_2", r"\ne", r"\mathbf 0", colors=(Palette.blue,), font_size=54)
        second = tex(r"(S - I)^2\mathbf v_2", "=", r"\mathbf 0", colors=(Palette.blue,), font_size=54)
        general = tex(r"(A - \lambda I)^k\mathbf v = \mathbf 0", font_size=64)
        board = VGroup(VGroup(first, second).arrange(RIGHT, buff=1.2), general).arrange(DOWN, buff=0.9).move_to(UP * 0.5).set_z_index(21)
        self.bring_to_front(self.chain_panel)
        self.chain_panel.set_z_index(22)
        line = self.say(r"$\mathbf v_2$ needs two pushes, so it is a \emph{generalized eigenvector}.", line, hold=0.2)
        self.play(FadeIn(self.veil), run_time=0.6)
        self.play(FadeIn(first, shift=UP * 0.1), run_time=0.7)
        self.play(FadeIn(second, shift=UP * 0.1), run_time=0.7)
        self.wait(Timing.read_short)
        line = self.say(r"In general, some power of $A - \lambda I$ sends $\mathbf v$ to $\mathbf 0$.", line, hold=0.2)
        self.play(Write(general), run_time=1.2)
        self.wait(Timing.read_short)
        self.remove(*self.squash_parts.get_family(), self.patch, self.eigenline, self.eigen_label, self.s_panel)
        self.play(FadeOut(board), run_time=0.6)
        return line

    def jordan_block(self, line):
        equations = VGroup(
            tex(r"A", r"\mathbf v_1", "=", r"\lambda", r"\,\mathbf v_1", colors=(None, Palette.yellow, None, None, Palette.yellow), font_size=52),
            tex(r"A", r"\mathbf v_2", "=", "1", r"\,\mathbf v_1", "+", r"\lambda", r"\,\mathbf v_2", colors=(None, Palette.blue, None, None, Palette.yellow, None, None, Palette.blue), font_size=52),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        equations[1].shift(RIGHT * (equations[0][2].get_x() - equations[1][2].get_x()))
        block = matrix([[r"\lambda", "1"], ["0", r"\lambda"]])
        block.get_columns()[0].set_color(Palette.yellow)
        block.get_columns()[1].set_color(Palette.blue)
        similar = VGroup(MathTex(r"P^{-1}AP", "=", color=Palette.text, font_size=52), block).arrange(RIGHT, buff=0.25)
        basis = tex(r"P = \begin{bmatrix} \mathbf v_1 & \mathbf v_2 \end{bmatrix}", font_size=46)
        right = VGroup(basis, similar).arrange(DOWN, buff=0.5)
        VGroup(equations, right).arrange(RIGHT, buff=1.4).move_to(UP * 0.2).set_z_index(21)
        line = self.say(r"Read the chain as two equations about $A$.", line, hold=0.2)
        self.play(FadeIn(equations[0], shift=UP * 0.1), run_time=0.7)
        self.play(FadeIn(equations[1], shift=UP * 0.1), run_time=0.7)
        self.wait(Timing.read_short)
        line = self.say(r"In the basis $\mathbf v_1, \mathbf v_2$ they become the columns of $J$.", line, hold=0.2)
        entries = block.get_entries()
        self.play(FadeIn(basis), FadeIn(similar[0]), FadeIn(block.get_brackets()), run_time=0.7)
        self.play(TransformFromCopy(equations[0][3], entries[0]), FadeIn(entries[2]), run_time=1.0, rate_func=spring)
        self.play(TransformFromCopy(equations[1][3], entries[1]), TransformFromCopy(equations[1][6], entries[3]), run_time=1.0, rate_func=spring)
        self.wait(Timing.beat)
        line = self.say(r"The 1 above the diagonal records the push onto $\mathbf v_1$.", line, hold=0.2)
        self.play(Indicate(entries[1], color=Palette.glow, scale_factor=1.3), Indicate(equations[1][3], color=Palette.glow, scale_factor=1.3), run_time=1.0)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(equations, right)), run_time=0.6)
        return line

    def jordan_form(self, line):
        form = Matrix([["1", "0", "0"], ["0", "-2", "1"], ["0", "0", "-2"]], v_buff=0.9, h_buff=1.3, bracket_h_buff=0.3).set_color(Palette.text)
        framed = VGroup(MathTex("J", "=", color=Palette.text, font_size=56), form).arrange(RIGHT, buff=0.25)
        framed.move_to(UP * 0.4).set_z_index(21)
        blocks = VGroup(block_frame(form, [0], [0]), block_frame(form, [1, 2], [1, 2])).set_z_index(21)
        form.get_rows()[1][2].set_color(Palette.glow)
        line = self.say(r"Stacking such blocks along the diagonal gives the \emph{Jordan form}.", line, hold=0.2)
        self.play(FadeIn(framed, shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        self.play(Create(blocks[0]), run_time=0.6)
        self.play(Create(blocks[1]), run_time=0.8)
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(framed, blocks)), run_time=0.6)
        return line


def figure_plane():
    plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
    plane.set_opacity(0.3)
    return plane


def settled_fan(plane):
    """The fan after the shear: tipped arrows faded, the horizontal pair yellow with glowing tips."""
    parts = VGroup(fan_lines(plane, opacity=0.3), eigenline(plane))
    for direction in fan_directions():
        image = (direction[0] + direction[1], direction[1])
        if is_horizontal(direction):
            parts.add(vector_arrow(image, Palette.yellow, plane, stroke_width=6), tip_glow(plane.c2p(*image)))
            continue
        parts.add(vector_arrow(direction, Palette.purple_gray, plane, stroke_width=3).set_opacity(0.22), fan_arrow(plane, image, direction))
    return parts


def chain_picture(plane, labels=True):
    push = Arrow(plane.c2p(*V2), plane.c2p(*S_V2), buff=0, color=Palette.pink, stroke_width=7, max_tip_length_to_length_ratio=0.18)
    parts = VGroup(
        patch_image(plane, S),
        eigenline(plane),
        vector_arrow(S_V2, Palette.teal, plane),
        vector_arrow(V2, Palette.blue, plane),
        push,
        vector_arrow(V1, Palette.yellow, plane),
        tip_glow(plane.c2p(*V1)),
    )
    if labels:
        parts.add(
            name_label(r"\mathbf v_2", Palette.blue, plane.c2p(*V2), LEFT),
            name_label(r"S\mathbf v_2", Palette.teal, plane.c2p(*S_V2), RIGHT),
            name_label(r"(S - I)\mathbf v_2", Palette.pink, push.get_center(), UP, font_size=36, buff=0.2),
            name_label(r"\mathbf v_1", Palette.yellow, plane.c2p(*V1), DOWN, buff=0.2),
            eigen_label(plane),
        )
    return parts


class FigOneEigenline(Scene):
    def construct(self):
        plane = figure_plane()
        self.add(plane, patch_image(plane, S, opacity=0.55), settled_fan(plane), eigen_label(plane), corner_panel(named("S", basis_matrix(S))))


class FigChain(Scene):
    def construct(self):
        plane = figure_plane()
        self.add(plane, chain_picture(plane), corner_panel(chain_label(), DR))


class FigSquash(Scene):
    def construct(self):
        stages = VGroup(*[self.stage(rows, index) for index, rows in enumerate((((1, 0), (0, 1)), N, ((0, 0), (0, 0))))])
        arrows = VGroup()
        stages.arrange(RIGHT, buff=1.6)
        for left, right in zip(stages[:-1], stages[1:]):
            arrow = Arrow(left.get_right() + RIGHT * 0.1, right.get_left() + LEFT * 0.1, buff=0, color=Palette.text, stroke_width=5, max_tip_length_to_length_ratio=0.25)
            name = MathTex(r"S - I", color=Palette.text, font_size=40).next_to(arrow, UP, buff=0.15)
            arrows.add(VGroup(arrow, name))
        self.add(stages, arrows)
        fit_to_frame(self)

    @staticmethod
    def stage(rows, index):
        plane = make_plane(x_range=(-3, 3, 1), y_range=(-3, 3, 1), x_length=6, y_length=6)
        plane.set_opacity(0.3)
        live = LiveTransform(rows)
        parts = VGroup(plane, patch_image(plane, rows), line_through_origin(plane, (1, 0), Palette.yellow, 4))
        carried = [tuple(live.point(point)) for point in (V1, V2)]
        parts.add(safe_arrow(plane, carried[0], Palette.yellow), safe_arrow(plane, carried[1], Palette.blue))
        if index == 2:
            parts.add(origin_ring(plane))
        return parts


class Poster(Scene):
    def construct(self):
        plane = plane_at((0.3, -0.7), 1.3).set_opacity(0.3)
        formula = backed(chain_label(font_size=64), padding=0.25)
        formula.to_corner(UL, buff=0.5)
        self.add(plane, chain_picture(plane, labels=False), formula)
