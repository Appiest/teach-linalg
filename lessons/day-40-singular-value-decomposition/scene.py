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
    make_plane,
    matrix,
    origin_pulse,
    plane_at,
    plate_for,
    scrim,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (2.3, 0.55)
PLANE_UNIT = 1.1
ROOT5 = math.sqrt(5)
A = np.array([[2.0, -1.0], [2.0, 2.0]])
A_INVERSE = np.linalg.inv(A)
SIGMA = np.diag([3.0, 2.0])
V1 = np.array([2, 1]) / ROOT5
V2 = np.array([-1, 2]) / ROOT5
U1 = np.array([1, 2]) / ROOT5
U2 = np.array([-2, 1]) / ROOT5
V_TURN = -math.atan2(1, 2)
U_TURN = math.atan2(2, 1)
PAIR_COLORS = (Palette.yellow, Palette.blue)
BASIS_COLORS = (Palette.i_hat, Palette.j_hat)
IMAGE_ROWS, IMAGE_COLS = 90, 135
RANK_STEPS = (1, 2, 5, 20)
BARS_SHOWN = 30
COURSE_THANKS = r"Forty days ago you drew one arrow, and now you can take any matrix apart."


def landscape(rows=IMAGE_ROWS, cols=IMAGE_COLS):
    """A grayscale picture drawn from formulas: a sky, a round sun and two ridges of hills."""
    y = (np.arange(rows)[:, None] + 0.5) / rows
    x = (np.arange(cols)[None, :] + 0.5) / cols
    image = 0.42 + 0.4 * (1 - y) * np.ones_like(x)
    sun = (x - 0.72) ** 2 * (cols / rows) ** 2 + (y - 0.3) ** 2 < 0.12**2
    image = np.where(sun, 0.97, image)
    far = 0.52 + 0.09 * np.sin(2 * math.pi * 1.3 * x + 0.5) + 0.04 * np.sin(2 * math.pi * 3.1 * x + 1.2)
    image = np.where(y > far, 0.32, image)
    near = 0.72 + 0.07 * np.sin(2 * math.pi * 0.8 * x + 2.0) + 0.03 * np.sin(2 * math.pi * 4.3 * x)
    return np.where(y > near, 0.12, image)


def hex_rgb(color):
    return np.array([int(color[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)


def picture(values, height=4.6):
    """Brightness values drawn from the background color (0) to the text color (1), pixels kept square."""
    dark, light = hex_rgb(Palette.background), hex_rgb(Palette.text)
    clipped = np.clip(values, 0, 1)[..., None]
    rgb = (dark + clipped * (light - dark)).astype(np.uint8)
    image = ImageMobject(rgb)
    image.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
    image.height = height
    return image


class Layers:
    """The picture's SVD, so any rank-k copy is one product away."""

    def __init__(self):
        self.original = landscape()
        self.left, self.values, self.right = np.linalg.svd(self.original)

    def rank(self, k):
        return (self.left[:, :k] * self.values[:k]) @ self.right[:k]


def unit_circle_points(samples=160):
    angles = np.linspace(0, 2 * math.pi, samples, endpoint=False)
    return [(math.cos(t), math.sin(t)) for t in angles]


def ellipse_shape(plane, carry, color=Palette.teal, fill=0.12, stroke_width=4):
    """The image of the unit circle under `carry`, a function from plane coordinates to plane coordinates."""
    points = [plane.c2p(*carry(point)) for point in unit_circle_points()]
    return Polygon(*points, color=color, fill_opacity=fill, stroke_width=stroke_width)


def static_ellipse(plane, transform, **style):
    transform = np.asarray(transform, dtype=float)
    return ellipse_shape(plane, lambda point: transform @ np.asarray(point), **style)


def name_label(tex_string, color, point, direction, font_size=38, buff=0.12):
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.08).next_to(point, direction, buff=buff)


def colored_matrix(rows, column_colors=None, row_colors=None, diagonal=None, font_size=36):
    mat = matrix([[str(entry) for entry in row] for row in rows], element_to_mobject_config={"font_size": font_size})
    for index, color in enumerate(column_colors or ()):
        mat.get_columns()[index].set_color(color)
    for index, color in enumerate(row_colors or ()):
        mat.get_rows()[index].set_color(color)
    for index in (range(len(rows)) if diagonal else ()):
        mat.get_rows()[index][index].set_color(diagonal)
    return mat


def over_root5(mat, font_size=36):
    return VGroup(MathTex(r"\tfrac{1}{\sqrt5}", color=Palette.text, font_size=font_size), mat).arrange(RIGHT, buff=0.08)


def corner_panel(content, corner=UL, buff=0.45):
    content.to_corner(corner, buff=buff)
    return VGroup(plate_for(content, padding=0.2), content).set_z_index(10)


def a_panel():
    return corner_panel(VGroup(MathTex("A", "=", color=Palette.text, font_size=44), colored_matrix(A.astype(int), BASIS_COLORS)).arrange(RIGHT, buff=0.2))


def factor_panel():
    """A = U Σ V^T with U's columns and V^T's rows in the pair colors and Σ's diagonal orange."""
    factors = VGroup(
        over_root5(colored_matrix(((1, -2), (2, 1)), column_colors=PAIR_COLORS)),
        colored_matrix(((3, 0), (0, 2)), diagonal=Palette.glow),
        over_root5(colored_matrix(((2, 1), (-1, 2)), row_colors=PAIR_COLORS)),
    ).arrange(RIGHT, buff=0.18)
    names = VGroup(*[
        MathTex(name, color=Palette.text, font_size=36).next_to(factor, DOWN, buff=0.15)
        for name, factor in zip(("U", r"\Sigma", "V^T"), factors)
    ])
    equals = MathTex("A", "=", color=Palette.text, font_size=44).next_to(factors, LEFT, buff=0.2)
    content = VGroup(equals, factors, names)
    content.scale_to_fit_width(min(content.width, 6.3))
    panel = corner_panel(content)
    panel.factors = factors
    return panel


def focus_box(factor):
    return SurroundingRectangle(factor, color=Palette.glow, buff=0.08, stroke_width=3.5).set_z_index(12)


def right_angle_mark(plane, first, second, size=0.28):
    origin = plane.c2p(0, 0)
    step_a = (plane.c2p(*first) - origin) / np.linalg.norm(plane.c2p(*first) - origin) * size
    step_b = (plane.c2p(*second) - origin) / np.linalg.norm(plane.c2p(*second) - origin) * size
    corners = [origin + step_a, origin + step_a + step_b, origin + step_b]
    return VMobject(color=Palette.glow, stroke_width=3).set_points_as_corners(corners)


def board_row(*parts, colors=(), font_size=52):
    row = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(row, colors):
        if color:
            part.set_color(color)
    return row


def singular_bars(values, kept, height=3.2, width=4.6):
    """Bars for the first singular values on a log scale from 0.1 to 100; the kept ones are teal."""
    shown = values[:BARS_SHOWN]
    step = width / len(shown)
    bars = VGroup()
    for index, value in enumerate(shown):
        tall = max(0.04, (math.log10(value) + 1) / 3 * height)
        color = Palette.teal if index < kept else Palette.text_muted
        bar = Rectangle(width=step * 0.7, height=tall, fill_color=color, fill_opacity=0.9 if index < kept else 0.35, stroke_width=0)
        bars.add(bar.move_to([index * step, tall / 2, 0]))
    return bars


def bar_chart(values, kept):
    bars = singular_bars(values, kept)
    floor = Line(bars.get_corner(DL) + LEFT * 0.1, bars.get_corner(DR) + RIGHT * 0.1, color=Palette.axis, stroke_width=2)
    name = MathTex(r"\sigma_i", color=Palette.text_muted, font_size=36).next_to(bars, UP, buff=0.2).align_to(bars, LEFT)
    return VGroup(bars, floor, name)


def storage_tex(k):
    stored = k * (IMAGE_ROWS + IMAGE_COLS + 1)
    return MathTex(rf"k = {k}", r"\quad", rf"{stored:,}".replace(",", "{,}") + r"\text{ numbers}", color=Palette.text, font_size=40)


class Lesson(LessonScene):
    day = 40
    title = "The singular value decomposition"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        self.plane = plane
        self.live = LiveTransform()
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.circle_to_ellipse()
        line = self.longest_stretch(line)
        line = self.undo(line)
        line = self.three_moves(line)
        line = self.where_sigmas_come_from(line)
        self.compress_picture(line)
        self.close_episode(
            r"Every matrix is a turn, a stretch along the axes, and a turn.\\"
            r"The largest singular values carry most of the matrix.",
            *self.mobjects,
        )

    def close_episode(self, takeaway_tex, *leftovers):
        """The shared closing card with one more line for the end of the course."""
        self.play(*[FadeOut(m) for m in leftovers], run_time=0.8)
        idea = Tex(takeaway_tex, color=Palette.text, font_size=48)
        idea.width = min(idea.width, config.frame_width - 2)
        thanks = Tex(COURSE_THANKS, color=Palette.text_muted, font_size=36).next_to(idea, DOWN, buff=0.6)
        card = VGroup(idea, thanks).move_to(UP * 0.4)
        pulse = origin_pulse().next_to(card, DOWN, buff=0.6)
        self.sfx("chime", gain=-4)
        self.play(FadeIn(idea, shift=UP * 0.2), run_time=1.0, rate_func=spring_soft)
        self.play(FadeIn(thanks, shift=UP * 0.1), run_time=0.9, rate_func=spring_soft)
        self.play(GrowFromCenter(pulse), run_time=0.8, rate_func=spring)
        self.wait(Timing.read_long + 1.5)
        self.play(FadeOut(card), FadeOut(pulse), run_time=0.8)

    def move(self, animation, run_time=2.6, rate_func=spring_soft):
        self.play(animation, run_time=run_time, rate_func=rate_func)

    def circle_to_ellipse(self):
        plane, live = self.plane, self.live
        self.panel = a_panel()
        line = self.say(r"Day 32 could diagonalize only some square matrices.", hold=0.2)
        self.play(FadeIn(self.panel, shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Today we take apart every matrix, square or not.", line, hold=0.2)
        self.grid = always_redraw(lambda: live.grid(plane, color=Palette.purple_gray, opacity=0.55))
        self.play(plane.animate.set_opacity(0.2), FadeIn(self.grid), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"Yesterday's quadratic forms are the tool that makes it work.", line, hold=Timing.read_short)
        line = self.say(r"Here is a matrix $A$ and the unit circle.", line, hold=0.2)
        self.circle = always_redraw(lambda: ellipse_shape(plane, live.point))
        self.play(Create(self.circle), run_time=1.2)
        self.bring_to_front(self.panel)
        self.wait(Timing.beat)
        line = self.say(r"$A$ turns the circle into a tilted ellipse.", line, hold=0.2)
        self.move(live.apply(A), run_time=3.0)
        self.ghost = DashedVMobject(static_ellipse(plane, np.eye(2), color=Palette.text_muted, fill=0, stroke_width=3), num_dashes=60)
        self.play(FadeIn(self.ghost), run_time=0.6)
        self.wait(Timing.read_short)
        return line

    def longest_stretch(self, line):
        plane = self.plane
        angle = ValueTracker(math.pi / 2)

        def unit():
            return np.array([math.cos(angle.get_value()), math.sin(angle.get_value())])

        x_arrow = always_redraw(lambda: vector_arrow(unit(), Palette.purple_gray, plane))
        ax_arrow = always_redraw(lambda: vector_arrow(A @ unit(), Palette.teal, plane))
        readout = always_redraw(lambda: self.length_readout(np.linalg.norm(A @ unit())))
        line = self.say(r"Which unit input gets stretched the most?", line, hold=0.2)
        self.play(GrowArrow(x_arrow), GrowArrow(ax_arrow), FadeIn(readout), run_time=1.0, rate_func=spring_soft)
        self.play(angle.animate.set_value(math.atan2(1, 2) + 2 * math.pi), run_time=6.0, rate_func=smooth)
        self.wait(Timing.beat)

        live_arrows = self.live_pair_arrows()
        inputs = VGroup(vector_arrow(V1, Palette.yellow, plane, stroke_width=5), vector_arrow(V2, Palette.blue, plane, stroke_width=5))
        self.v1_label = name_label(r"\mathbf v_1", Palette.yellow, plane.c2p(*V1), RIGHT)
        self.v2_label = name_label(r"\mathbf v_2", Palette.blue, plane.c2p(*V2), UP, buff=0.08)
        line = self.say(r"The longest output comes from the input $\mathbf v_1$.", line, hold=0.2)
        self.play(FadeIn(inputs[0]), FadeIn(live_arrows[0]), FadeIn(self.v1_label), run_time=0.8)
        line = self.say(r"Its length $\sigma_1 = 3$ is the first \emph{singular value}.", line, hold=Timing.read_short)

        line = self.say(r"At right angles, $\mathbf v_2$ gets the shortest output, $\sigma_2 = 2$.", line, hold=0.2)
        self.play(angle.animate.set_value(math.atan2(2, -1) + 2 * math.pi), run_time=1.6, rate_func=spring_soft)
        self.play(FadeIn(inputs[1]), FadeIn(live_arrows[1]), FadeIn(self.v2_label), run_time=0.8)
        self.wait(Timing.read_short)
        mark = right_angle_mark(plane, U1, U2)
        line = self.say(r"The two outputs are perpendicular too.", line, hold=0.2)
        self.play(FadeOut(x_arrow), FadeOut(ax_arrow), Create(mark), run_time=0.8)
        self.wait(Timing.read_short)
        self.sweep_leftovers = VGroup(readout, inputs, mark, self.ghost, self.v1_label, self.v2_label)
        return line

    def length_readout(self, length):
        text = MathTex(r"\|A\mathbf x\| = " + f"{length:.2f}", color=Palette.teal, font_size=40)
        return backed(text, padding=0.15).next_to(self.panel, DOWN, buff=0.3, aligned_edge=LEFT).set_z_index(10)

    def live_pair_arrows(self):
        plane, live = self.plane, self.live
        self.pair_arrows = VGroup(*[
            always_redraw(lambda d=direction, c=color: vector_arrow(tuple(live.point(d)), c, plane))
            for direction, color in zip((V1, V2), PAIR_COLORS)
        ])
        return self.pair_arrows

    def undo(self, line):
        line = self.say(r"The goal is to split $A$ into three simple moves.", line, hold=0.2)
        self.play(FadeOut(self.sweep_leftovers), run_time=0.6)
        self.move(self.live.apply(A_INVERSE), run_time=2.2)
        self.wait(Timing.beat)
        return line

    def three_moves(self, line):
        plane, live = self.plane, self.live
        factors = factor_panel()
        self.play(FadeOut(self.panel), FadeIn(factors, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        self.panel = factors
        box = focus_box(factors.factors[2])
        line = self.say(r"$V^T$ turns $\mathbf v_1$ and $\mathbf v_2$ onto the axes.", line, hold=0.2)
        self.play(Create(box), run_time=0.6)
        self.move(live.rotate(V_TURN), run_time=2.6)
        line = self.say(r"The circle looks the same, but its arrows moved.", line, hold=Timing.read_short)

        line = self.say(r"$\Sigma$ stretches the axes by $\sigma_1 = 3$ and $\sigma_2 = 2$.", line, hold=0.2)
        self.play(box.animate.become(focus_box(factors.factors[1])), run_time=0.6)
        self.move(live.apply(SIGMA), run_time=2.8)
        self.wait(Timing.beat)

        line = self.say(r"$U$ turns the axes onto $\mathbf u_1$ and $\mathbf u_2$.", line, hold=0.2)
        self.play(box.animate.become(focus_box(factors.factors[0])), run_time=0.6)
        self.move(live.rotate(U_TURN), run_time=2.8)
        self.axis_labels = VGroup(
            name_label(r"\sigma_1\mathbf u_1", Palette.yellow, plane.c2p(*(3 * U1)), RIGHT),
            name_label(r"\sigma_2\mathbf u_2", Palette.blue, plane.c2p(*(2 * U2)), LEFT),
        )
        self.play(FadeIn(self.axis_labels), run_time=0.6)
        self.wait(Timing.beat)

        line = self.say(r"One step of $A$ draws exactly the same ellipse.", line, hold=0.2)
        check = DashedVMobject(static_ellipse(plane, A, color=Palette.text, fill=0, stroke_width=3), num_dashes=70)
        self.play(FadeOut(box), Create(check), run_time=1.6)
        self.wait(Timing.beat)
        line = self.say(r"Every matrix works this way: turn, stretch, turn.", line, hold=Timing.read_short)
        self.check = check
        return line

    def where_sigmas_come_from(self, line):
        veil = scrim().set_z_index(20)
        rows = VGroup(
            board_row(r"\|A\mathbf x\|^2", "=", r"\mathbf x^T(A^TA)\mathbf x"),
            board_row(r"A^TA = \begin{bmatrix} 8 & 2 \\ 2 & 5 \end{bmatrix}", r"\qquad", r"\lambda = 9,\ 4"),
            board_row(r"\sigma_1 = \sqrt9 = ", "3", r",\qquad", r"\sigma_2 = \sqrt4 = ", "2", colors=(None, Palette.glow, None, None, Palette.glow)),
            board_row(r"\mathbf u_i", "=", r"A\mathbf v_i", "/", r"\sigma_i"),
        ).arrange(DOWN, buff=0.5).move_to(UP * 0.5).set_z_index(21)
        line = self.say(r"Now we compute the three factors, starting with $V$.", line, hold=Timing.read_short)
        line = self.say(r"The stretches come from the symmetric matrix $A^TA$.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(FadeIn(rows[0], shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Day 39 showed this form peaks at the top eigenvector.", line, hold=Timing.read_short)
        line = self.say(r"Its eigenvalues are 9 and 4, with eigenvectors $\mathbf v_1$ and $\mathbf v_2$.", line, hold=0.2)
        self.play(FadeIn(rows[1], shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"The singular values are their square roots, 3 and 2.", line, hold=0.2)
        self.play(FadeIn(rows[2], shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"Each $\mathbf u_i$ is $A\mathbf v_i$ divided by $\sigma_i$.", line, hold=0.2)
        self.play(FadeIn(rows[3], shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)

        layers = board_row(
            "A", "=", r"\sigma_1", r"\mathbf u_1\mathbf v_1^T", "+", r"\sigma_2", r"\mathbf u_2\mathbf v_2^T",
            colors=(None, None, Palette.glow, Palette.yellow, None, Palette.glow, Palette.blue), font_size=64,
        ).move_to(UP * 0.5).set_z_index(21)
        line = self.say(r"Written out, $A$ is a sum of rank-one layers.", line, hold=0.2)
        self.play(FadeOut(rows, shift=UP * 0.1), FadeIn(layers, shift=UP * 0.1), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_short)
        self.board = VGroup(veil, layers)
        return line

    def compress_picture(self, line):
        layers = Layers()
        image = picture(layers.original).move_to(RIGHT * 2.9 + UP * 0.55).set_z_index(22)
        size_note = MathTex(r"90 \times 135 = 12{,}150 \text{ numbers}", color=Palette.text_muted, font_size=34)
        size_note.next_to(image, UP, buff=0.2).set_z_index(22)
        line = self.say(r"Dropping the weakest layers stores a big matrix in fewer numbers.", line, hold=Timing.read_short)
        line = self.say(r"A grayscale picture is a matrix of brightness values.", line, hold=0.2)
        self.play(self.board[1].animate.scale(0.6).to_edge(UP, buff=0.35).to_edge(LEFT, buff=0.5), run_time=0.8, rate_func=spring_soft)
        self.play(FadeIn(image), FadeIn(size_note), run_time=0.8)
        self.wait(Timing.read_short)

        chart = bar_chart(layers.values, 0).move_to(LEFT * 3.6 + DOWN * 0.1).set_z_index(22)
        self.play(FadeIn(chart), run_time=0.8)
        line = self.say(r"Keep only the first $k$ layers to get a rank-$k$ copy.", line, hold=Timing.read_short)
        notes = {
            1: r"One layer gets only rough bands of light and dark.",
            2: r"A second layer starts to find the sun.",
            5: r"Five layers already show the sun and the hills.",
            20: r"Twenty layers look almost exactly like the original.",
        }
        count = None
        for k in RANK_STEPS:
            line = self.say(notes[k], line, hold=0.1)
            chart, image, count = self.show_rank(layers, k, chart, image, count)
            self.wait(Timing.read_short)
        line = self.say(r"Rank 20 stores 4,520 numbers instead of 12,150.", line, hold=Timing.read_short)
        self.play(Indicate(count, color=Palette.glow, scale_factor=1.08), run_time=0.9)
        self.wait(Timing.beat)
        line = self.say(r"The whole course has been building to this one factorization.", line, hold=Timing.read_short)

    def show_rank(self, layers, k, chart, image, count):
        new_chart = bar_chart(layers.values, k).move_to(chart).set_z_index(22)
        new_image = picture(layers.rank(k)).move_to(image).set_z_index(23)
        new_count = storage_tex(k).next_to(new_chart, DOWN, buff=0.4).set_z_index(22)
        new_count[0].set_color(Palette.teal)
        self.sfx("tick", gain=-4)
        if count is not None:
            self.play(FadeOut(count), run_time=0.25)
        self.play(FadeIn(new_image), FadeOut(chart), FadeIn(new_chart), FadeIn(new_count), run_time=0.8)
        self.remove(image)
        new_image.set_z_index(22)
        return new_chart, new_image, new_count


def small_stage(transform, title, turned=np.eye(2), show_ellipse_axes=False):
    """One panel of the three-moves figure: the grid and circle carried by `transform`, with the pair arrows."""
    plane = make_plane(x_range=(-3.5, 3.5, 1), y_range=(-3.5, 3.5, 1), x_length=4.2, y_length=4.2)
    plane.set_opacity(0.3)
    live = LiveTransform(transform)
    parts = VGroup(plane, live.grid(plane, color=Palette.purple_gray, opacity=0.5), ellipse_shape(plane, live.point, stroke_width=3))
    for direction, color in zip((V1, V2), PAIR_COLORS):
        parts.add(vector_arrow(tuple(live.point(direction)), color, plane, stroke_width=5))
    heading = MathTex(title, color=Palette.text, font_size=40).next_to(plane, UP, buff=0.2)
    return VGroup(parts, heading)


class FigThreeMoves(Scene):
    def construct(self):
        turn_v = np.array([[math.cos(V_TURN), -math.sin(V_TURN)], [math.sin(V_TURN), math.cos(V_TURN)]])
        stages = VGroup(
            small_stage(np.eye(2), r"\text{start}"),
            small_stage(turn_v, r"\text{after } V^T"),
            small_stage(SIGMA @ turn_v, r"\text{after } \Sigma"),
            small_stage(A, r"\text{after } U"),
        ).arrange_in_grid(rows=2, cols=2, buff=(0.5, 0.35))
        self.add(stages)
        fit_to_frame(self)


class FigSingularAxes(Scene):
    def construct(self):
        plane = make_plane(x_range=(-3, 3, 1), y_range=(-3.5, 3.5, 1), x_length=6 * 1.1, y_length=7 * 1.1)
        plane.set_opacity(0.4)
        parts = VGroup(
            plane,
            static_ellipse(plane, A),
            DashedVMobject(static_ellipse(plane, np.eye(2), color=Palette.text_muted, fill=0, stroke_width=3), num_dashes=40),
            vector_arrow(V1, Palette.yellow, plane, stroke_width=5),
            vector_arrow(V2, Palette.blue, plane, stroke_width=5),
            vector_arrow(3 * U1, Palette.yellow, plane),
            vector_arrow(2 * U2, Palette.blue, plane),
            right_angle_mark(plane, U1, U2, size=0.25),
            name_label(r"\mathbf v_1", Palette.yellow, plane.c2p(*V1), DR, font_size=34),
            name_label(r"\mathbf v_2", Palette.blue, plane.c2p(*V2), RIGHT, font_size=34),
            name_label(r"A\mathbf v_1 = 3\mathbf u_1", Palette.yellow, plane.c2p(*(3 * U1)), RIGHT, font_size=34),
            name_label(r"A\mathbf v_2 = 2\mathbf u_2", Palette.blue, plane.c2p(*(2 * U2)), DL, font_size=34, buff=0.05),
        )
        self.add(parts)
        fit_to_frame(self)


class FigRankCopies(Scene):
    def construct(self):
        layers = Layers()
        tiles = Group()
        for k in (1, 2, 5, 20):
            tile = picture(layers.rank(k), height=2.2)
            tiles.add(Group(tile, MathTex(rf"k = {k}", color=Palette.text, font_size=34).next_to(tile, UP, buff=0.15)))
        original = picture(layers.original, height=2.2)
        tiles.add(Group(original, Tex("original", color=Palette.text, font_size=34).next_to(original, UP, buff=0.15)))
        tiles.arrange_in_grid(rows=2, cols=3, buff=(0.3, 0.35))
        chart = bar_chart(layers.values, 20).scale_to_fit_height(2.3).move_to(tiles[-1]).shift(RIGHT * 3.4)
        tiles.add(chart)
        tiles.move_to(ORIGIN)
        self.add(tiles)
        scale = min((config.frame_width - 0.7) / tiles.width, (config.frame_height - 0.7) / tiles.height)
        tiles.scale(scale).move_to(ORIGIN)


class Poster(Scene):
    def construct(self):
        plane = plane_at((2.2, -0.1), 1.25)
        plane.set_opacity(0.25)
        live = LiveTransform(A)
        formula = backed(board_row("A", "=", "U", r"\Sigma", "V^T", colors=(None, None, Palette.yellow, Palette.glow, Palette.blue), font_size=96), padding=0.3)
        formula.to_corner(UL, buff=0.7)
        self.add(
            plane,
            live.grid(plane, color=Palette.purple_gray, opacity=0.55),
            DashedVMobject(static_ellipse(plane, np.eye(2), color=Palette.text_muted, fill=0, stroke_width=3), num_dashes=50),
            static_ellipse(plane, A, stroke_width=5),
            vector_arrow(3 * U1, Palette.yellow, plane, stroke_width=7),
            vector_arrow(2 * U2, Palette.blue, plane, stroke_width=7),
            vector_arrow(V1, Palette.yellow, plane, stroke_width=5),
            vector_arrow(V2, Palette.blue, plane, stroke_width=5),
            formula,
        )
