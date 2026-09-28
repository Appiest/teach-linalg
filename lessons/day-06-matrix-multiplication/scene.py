import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    Palette,
    Timing,
    backed,
    column,
    fit_to_frame,
    make_plane,
    matrix,
    matrix_grid,
    plane_at,
    plate_for,
    scrim,
    shear_matrix,
    spring,
    spring_soft,
    turn_matrix,
    vector_arrow,
)

X = (1, 1)
S = ((1, 1), (0, 1))
R = ((0, -1), (1, 0))
RS = ((0, -1), (1, 1))
SR = ((1, -1), (1, 0))
A = ((1, 2), (-3, 4))
B = ((2, 0, -1), (5, 1, 3))
AB = ((12, 2, 5), (14, 4, 15))
PLANE_ORIGIN = (1.6, -1.3)
PLANE_UNIT = 1.25
PANEL_UNIT = 0.75
PANEL_BOX = ((-3, 3), (-2, 3))
BASIS_COLORS = (Palette.i_hat, Palette.j_hat)
STEPS = {"S": shear_matrix, "R": lambda t: turn_matrix(t * PI / 2)}


class Composition:
    """Two steps applied one after the other, each driven by a tracker that runs from 0 to 1."""

    def __init__(self, first: str, second: str):
        self.first, self.second = first, second
        self.first_done = ValueTracker(0)
        self.second_done = ValueTracker(0)

    def matrix(self):
        return STEPS[self.second](self.second_done.get_value()) @ STEPS[self.first](self.first_done.get_value())

    def image(self, point):
        return tuple(self.matrix() @ np.array(point, dtype=float))


def tex(*parts, colors=(), font_size=48):
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def basis_matrix(rows, **kwargs):
    """A 2x2 matrix whose columns wear the colors of the basis arrows they record."""
    mat = matrix(rows, **kwargs)
    for index, color in enumerate(BASIS_COLORS):
        mat.get_columns()[index].set_color(color)
    return mat


def named_matrix(name, rows, font_size=48):
    return VGroup(tex(name, "=", font_size=font_size), basis_matrix(rows)).arrange(RIGHT, buff=0.2)


def live_pieces(plane, composition, box=None):
    """The moving grid, basis arrows and yellow x for one composition."""
    grid = always_redraw(lambda: matrix_grid(plane, composition.matrix(), box=box))
    arrows = [
        always_redraw(lambda point=point, color=color: vector_arrow(composition.image(point), color, plane))
        for point, color in (((1, 0), Palette.i_hat), ((0, 1), Palette.j_hat))
    ]
    x_arrow = always_redraw(lambda: vector_arrow(composition.image(X), Palette.yellow, plane))
    return VGroup(grid, *arrows, x_arrow)


def hop(plane, start, end, color, name, angle=-PI / 3, direction=UP, along=0.5):
    arc = CurvedArrow(plane.c2p(*start), plane.c2p(*end), angle=angle, color=color, stroke_width=4, tip_length=0.2)
    label = backed(tex(name, font_size=40).set_color(color)).next_to(arc.point_from_proportion(along), direction, buff=0.12)
    return VGroup(arc, label)


def dimmed_hop(hop_group, amount=0.6):
    """The same hop pushed toward the background, recolored rather than made transparent so the arc never fills."""
    arc, label = hop_group.copy()
    arc.set_color(interpolate_color(ManimColor(arc.get_color()), ManimColor(Palette.background), amount))
    label.set_opacity(1 - amount)
    return VGroup(arc, label)


def ghost(plane, point):
    return Dot(plane.c2p(*point), radius=0.07, color=Palette.yellow, fill_opacity=0.5)


def sized(mat, rows, cols, font_size=36):
    """An m x n size tag set under a matrix, split so each number can move on its own."""
    tag = tex(str(rows), r"\times", str(cols), font_size=font_size).set_color(Palette.text_muted)
    return tag.next_to(mat, DOWN, buff=0.3)


def column_rule_rows():
    """R s1 and R s2 written out, each colored by the basis arrow its column records."""
    rows = VGroup()
    for index, color in enumerate(BASIS_COLORS):
        s_col = column([S[0][index], S[1][index]], color=color)
        image = column([RS[0][index], RS[1][index]], color=color)
        name = tex("R", rf"\mathbf s_{index + 1}", "=", colors=(None, color))
        rows.add(VGroup(name, matrix(R), s_col, tex("="), image).arrange(RIGHT, buff=0.2))
    return rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)


def product_layout():
    a_mat, b_mat = matrix(A), matrix(B)
    blank = matrix(AB)
    product = VGroup(a_mat, b_mat, tex("="), blank).arrange(RIGHT, buff=0.25)
    sizes = VGroup(sized(a_mat, 2, 2), sized(b_mat, 2, 3), sized(blank, 2, 3))
    return product, sizes


def panel_plane(center):
    (x_min, x_max), (y_min, y_max) = PANEL_BOX
    plane = make_plane(
        x_range=(x_min, x_max, 1),
        y_range=(y_min, y_max, 1),
        x_length=(x_max - x_min) * PANEL_UNIT,
        y_length=(y_max - y_min) * PANEL_UNIT,
    )
    plane.shift(np.array([*center, 0.0]) - plane.c2p(0, 0))
    return plane


def panel_header(words, name):
    return VGroup(Tex(words, color=Palette.text, font_size=36), tex(name, font_size=40)).arrange(RIGHT, buff=0.3)


def order_panels():
    """Shear-then-rotate on the left and rotate-then-shear on the right, with their headers."""
    panels = []
    for center_x, words, name, order in ((-3.45, "Shear, then rotate", "RS", ("S", "R")), (3.45, "Rotate, then shear", "SR", ("R", "S"))):
        plane = panel_plane((center_x, 0.1))
        header = panel_header(words, name).next_to(plane, UP, buff=0.25)
        panels.append((plane, header, Composition(*order), name))
    return panels


def transpose_pair():
    b_mat = matrix(B)
    b_t = matrix([[B[0][0], B[1][0]], [B[0][1], B[1][1]], [B[0][2], B[1][2]]])
    names = (tex("B", "="), tex("B^T", "="))
    group = VGroup(VGroup(names[0], b_mat).arrange(RIGHT, buff=0.2), VGroup(names[1], b_t).arrange(RIGHT, buff=0.2))
    return group.arrange(RIGHT, buff=1.2), b_mat, b_t


class Lesson(LessonScene):
    day = 6
    title = "Matrix multiplication is composition"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.two_steps(plane)
        line = self.one_matrix(plane, line)
        line = self.column_rule(line)
        line = self.row_column_rule(line)
        line = self.order_matters(plane, line)
        line = self.transpose(line)
        self.close_episode(
            r"$AB$ means do $B$ first, then $A$.\\"
            r"Each column of $AB$ is $A$ times a column of $B$.",
            *self.mobjects,
        )

    def clear_behind(self, *keep):
        """Drop everything hidden under a full-frame veil except the given mobjects."""
        for mobject in self.mobjects:
            mobject.clear_updaters()
        self.remove(*[mobject for mobject in self.mobjects if mobject not in keep])

    def raise_veil(self, veil, line):
        """Fade the veil in underneath the current caption, then drop what it hides."""
        veil.set_fill(opacity=0)
        self.add(veil)
        self.bring_to_front(line)
        self.play(veil.animate.set_fill(opacity=0.96), run_time=0.7)
        self.clear_behind(veil, line)

    def two_steps(self, plane):
        self.walk = Composition("S", "R")
        self.live = live_pieces(plane, self.walk)
        grid, i_arrow, j_arrow, x_arrow = self.live
        self.x_name = backed(tex(r"\mathbf x", font_size=40).set_color(Palette.yellow)).next_to(plane.c2p(*X), RIGHT, buff=0.12)
        self.panel = named_matrix("S", S).scale(0.8).to_corner(UL, buff=0.6)
        self.plate = plate_for(self.panel)
        line = self.say(r"Start with yesterday's shear $S$.", hold=0.2)
        self.add(grid)
        self.play(GrowArrow(i_arrow), GrowArrow(j_arrow), run_time=1.0, rate_func=spring_soft)
        self.play(GrowArrow(x_arrow), FadeIn(self.x_name), run_time=1.0, rate_func=spring_soft)
        self.play(FadeIn(self.plate), Write(self.panel), run_time=1.2)
        self.wait(Timing.beat)

        line = self.say(r"The shear moves $\mathbf x$ to $S\mathbf x$.", line, hold=0.2)
        self.ghosts = VGroup(ghost(plane, X), ghost(plane, (2, 1)))
        self.add(self.ghosts[0])
        self.play(FadeOut(self.x_name), self.walk.first_done.animate.set_value(1), run_time=2.2, rate_func=spring)
        self.hops = VGroup(hop(plane, X, (2, 1), Palette.yellow, "S", angle=-PI / 2, direction=DOWN))
        self.play(Create(self.hops[0]), run_time=0.9)
        self.wait(Timing.read_short)

        line = self.say(r"Then rotate everything a quarter turn with $R$.", line, hold=0.2)
        second = named_matrix("R", R).scale(0.8).next_to(self.panel, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(self.plate.animate.become(plate_for(VGroup(self.panel, second))), run_time=0.5, rate_func=spring_soft)
        self.play(Write(second), run_time=1.0)
        self.panel.add(second)
        self.add(self.ghosts[1])
        self.play(self.walk.second_done.animate.set_value(1), run_time=2.6, rate_func=spring)
        self.hops.add(hop(plane, (2, 1), (-1, 2), Palette.yellow, "R", angle=PI / 3))
        self.play(Create(self.hops[1]), run_time=1.1)
        self.wait(Timing.read_short)
        return line

    def one_matrix(self, plane, line):
        line = self.say(r"Two moves in a row act like one transformation.", line, hold=0.2)
        direct = hop(plane, X, (-1, 2), Palette.teal, "RS", angle=-PI / 4, direction=UP, along=0.55)
        self.play(*[Transform(step, dimmed_hop(step)) for step in self.hops], run_time=0.5)
        self.play(Create(direct), run_time=1.2)
        self.hops.add(direct)
        self.wait(Timing.read_short)
        self.play(FadeOut(self.hops), FadeOut(self.ghosts), run_time=0.6)

        line = self.say(r"Its columns are where $\hat\imath$ and $\hat\jmath$ finally land.", line, hold=0.2)
        product = named_matrix("RS", RS).scale(0.8).next_to(self.panel, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(self.plate.animate.become(plate_for(VGroup(self.panel, product))), run_time=0.5, rate_func=spring_soft)
        self.play(FadeIn(product[0]), FadeIn(product[1].get_brackets()), run_time=0.6)
        tags = VGroup()
        for index, (point, direction) in enumerate((((0, 1), RIGHT), ((-1, 1), LEFT))):
            tag = backed(column(point, color=BASIS_COLORS[index]).scale(0.6)).next_to(plane.c2p(*point), direction, buff=0.2)
            self.play(Indicate(self.live[1 + index], color=Palette.glow), FadeIn(tag), run_time=0.8)
            self.play(TransformFromCopy(tag.get_entries(), product[1].get_columns()[index]), run_time=1.1, rate_func=spring_soft)
            tags.add(tag)
        self.panel.add(product)
        self.play(FadeOut(tags), run_time=0.5)
        self.wait(Timing.read_short)

        line = self.say(r"Read right to left: $S$ touches $\mathbf x$ first.", line, hold=0.2)
        self.read_right_to_left()
        return line

    def read_right_to_left(self):
        equation = tex("R", "(", "S", r"\mathbf x", ")", "=", "(", "R", "S", ")", r"\mathbf x", font_size=44)
        equation.scale(0.9).next_to(self.panel, DOWN, buff=0.45, aligned_edge=LEFT)
        pointer = Arrow(equation[3].get_bottom() + DOWN * 0.2, equation[0].get_bottom() + DOWN * 0.2, buff=0, color=Palette.glow, stroke_width=3, max_tip_length_to_length_ratio=0.12)
        pointer.shift(DOWN * 0.05)
        self.play(self.plate.animate.become(plate_for(VGroup(self.panel, equation, pointer))), run_time=0.5, rate_func=spring_soft)
        self.play(Write(equation), run_time=1.4)
        self.play(GrowArrow(pointer), run_time=0.9)
        self.play(Indicate(equation[2], color=Palette.glow, scale_factor=1.3), run_time=0.8)
        self.play(Indicate(equation[0], color=Palette.glow, scale_factor=1.3), run_time=0.8)
        self.panel.add(equation, pointer)
        self.wait(Timing.read_long)

    def column_rule(self, line):
        veil = scrim()
        symbolic = tex(
            "RS", "=", "R", r"\begin{bmatrix} \mathbf s_1 & \mathbf s_2 \end{bmatrix}", "=", r"\begin{bmatrix} R\mathbf s_1 & R\mathbf s_2 \end{bmatrix}"
        )
        rows = column_rule_rows()
        result = named_matrix("RS", RS)
        right = VGroup(rows, result).arrange(RIGHT, buff=1.2)
        VGroup(symbolic, right).arrange(DOWN, buff=0.7).move_to(UP * 0.5)
        line = self.say(r"Each column of $RS$ is $R$ applied to a column of $S$.", line, hold=0.2)
        self.raise_veil(veil, line)
        self.play(Write(symbolic), run_time=1.6)
        self.play(FadeIn(result[0]), FadeIn(result[1].get_brackets()), run_time=0.6)
        for row, target in zip(rows, result[1].get_columns()):
            self.play(FadeIn(row[:4]), run_time=0.9)
            self.play(FadeIn(row[4], shift=LEFT * 0.2), run_time=0.7, rate_func=spring)
            self.play(TransformFromCopy(row[4].get_entries(), target), run_time=1.1, rate_func=spring_soft)
            self.wait(Timing.beat)

        line = self.say(r"That is the column rule for any product.", line, hold=0.2)
        general = tex(
            "AB", "=", "A", r"\begin{bmatrix} \mathbf b_1 & \cdots & \mathbf b_p \end{bmatrix}", "=",
            r"\begin{bmatrix} A\mathbf b_1 & \cdots & A\mathbf b_p \end{bmatrix}",
        ).move_to(symbolic)
        self.play(FadeOut(right, shift=DOWN * 0.2), FadeTransform(symbolic, general), run_time=1.2)
        self.wait(Timing.read_long)
        self.play(FadeOut(general), run_time=0.6)
        self.veil = veil
        return line

    def row_column_rule(self, line):
        product, sizes = product_layout()
        stage = VGroup(product, sizes).move_to(UP * 1.0)
        entries = product[3].get_entries()
        entries.set_opacity(0)
        line = self.say(r"Inner sizes must match; outer sizes give the product's size.", line, hold=0.2)
        self.play(FadeIn(product[:3]), FadeIn(product[3].get_brackets()), FadeIn(sizes[0]), FadeIn(sizes[1]), run_time=1.0)
        self.play(Indicate(VGroup(sizes[0][2], sizes[1][0]), color=Palette.glow, scale_factor=1.3), run_time=1.0)
        self.play(
            TransformFromCopy(sizes[0][0], sizes[2][0]),
            TransformFromCopy(sizes[1][2], sizes[2][2]),
            FadeIn(sizes[2][1]),
            run_time=1.2,
        )
        self.wait(Timing.read_short)

        line = self.say(r"One entry is a row of $A$ times a column of $B$.", line, hold=0.2)
        self.one_entry(product)
        line = self.say(r"Every entry of $AB$ works the same way.", line, hold=0.2)
        rest = [entry for index, entry in enumerate(entries) if index != 5]
        self.play(LaggedStart(*[entry.animate.set_opacity(1) for entry in rest], lag_ratio=0.25), run_time=2.0)
        self.wait(Timing.read_short)

        line = self.say(r"In the other order, $3 \neq 2$, so $BA$ is undefined.", line, hold=0.2)
        self.other_order(stage)
        return line

    def one_entry(self, product):
        a_mat, b_mat, _, result = product
        marks = VGroup(
            SurroundingRectangle(a_mat.get_rows()[1], color=Palette.glow, buff=0.1),
            SurroundingRectangle(b_mat.get_columns()[2], color=Palette.glow, buff=0.1),
        )
        work = tex("(-3)(-1)", "+", r"4\cdot 3", "=", "15").next_to(product, DOWN, buff=1.3)
        slot = result.get_entries()[5]
        self.play(Create(marks), run_time=0.8)
        self.play(Write(work), run_time=1.6)
        self.wait(Timing.beat)
        copy = work[4].copy()
        self.play(copy.animate.move_to(slot).match_height(slot), run_time=1.1, rate_func=spring_soft)
        slot.set_opacity(1)
        self.add(slot)
        self.remove(copy)
        self.wait(Timing.read_short)
        self.play(FadeOut(marks), FadeOut(work), run_time=0.5)

    def other_order(self, stage):
        swapped = VGroup(matrix(B), matrix(A)).arrange(RIGHT, buff=0.25)
        tags = VGroup(sized(swapped[0], 2, 3), sized(swapped[1], 2, 2))
        other = VGroup(tex("BA", ":"), VGroup(swapped, tags)).arrange(RIGHT, buff=0.4)
        other.scale(0.8).next_to(stage, DOWN, buff=0.5)
        self.play(FadeIn(other, shift=UP * 0.2), run_time=0.9, rate_func=spring_soft)
        self.play(Indicate(VGroup(tags[0][2], tags[1][0]), color=Palette.j_hat, scale_factor=1.3), run_time=1.0)
        self.wait(Timing.read_short)
        self.play(FadeOut(stage), FadeOut(other), run_time=0.6)

    def order_matters(self, plane, line):
        panels = order_panels()
        line = self.say(r"Now do the same two moves in the other order.", line, hold=0.2)
        self.clear_behind(self.veil, line)
        pieces = []
        for panel_plane_, header, composition, _ in panels:
            pieces.append(live_pieces(panel_plane_, composition, box=PANEL_BOX))
        self.play(*[FadeIn(VGroup(p[0], p[1])) for p in panels], FadeOut(self.veil), run_time=1.0)
        self.add(*pieces)
        self.wait(Timing.read_short)

        line = self.say(r"First moves happen together, then second moves.", line, hold=0.2)
        for step in ("first_done", "second_done"):
            self.play(*[getattr(p[2], step).animate.set_value(1) for p in panels], run_time=2.6, rate_func=spring)
            self.wait(Timing.beat)

        line = self.say(r"They end in different places, so $RS \neq SR$.", line, hold=0.2)
        self.write_landings(panels)
        return line

    def write_landings(self, panels):
        stamps, names = VGroup(), VGroup()
        for panel_plane_, _, composition, name in panels:
            stamps.add(Dot(panel_plane_.c2p(*composition.image(X)[:2]), radius=0.08, color=Palette.glow))
            rows = RS if name == "RS" else SR
            names.add(named_matrix(name, rows, font_size=40).scale(0.75).next_to(panel_plane_, DOWN, buff=0.15))
        self.play(LaggedStart(*[GrowFromCenter(stamp) for stamp in stamps], lag_ratio=0.4), run_time=0.9)
        self.play(FadeIn(names, shift=UP * 0.15), run_time=1.0, rate_func=spring_soft)
        self.landings = VGroup(stamps, names)
        self.wait(Timing.read_long)

    def transpose(self, line):
        veil = scrim()
        pair, b_mat, b_t = transpose_pair()
        pair.move_to(UP * 1.4)
        line = self.say(r"The transpose turns each row into a column.", line, hold=0.2)
        self.raise_veil(veil, line)
        self.play(FadeIn(pair[0]), FadeIn(pair[1][0]), FadeIn(b_t.get_brackets()), run_time=0.9)
        for row, target in zip(b_mat.get_rows(), b_t.get_columns()):
            mark = SurroundingRectangle(row, color=Palette.glow, buff=0.1)
            self.play(Create(mark), run_time=0.5)
            self.play(TransformFromCopy(row, target), FadeOut(mark), run_time=1.3, rate_func=spring_soft)
        self.wait(Timing.read_short)

        line = self.say(r"Transposing a product reverses the order.", line, hold=0.2)
        rule = tex("(AB)^T", "=", "B^T", "A^T").next_to(pair, DOWN, buff=0.9)
        tags = tex(r"(3\times", "2", r")\,(", "2", r"\times 2)", r"\;\to\; 3\times 2", font_size=36).set_color(Palette.text_muted)
        tags.next_to(rule, DOWN, buff=0.35)
        self.play(Write(rule), run_time=1.4)
        self.play(FadeIn(tags, shift=UP * 0.15), run_time=0.8)
        self.play(Indicate(VGroup(tags[1], tags[3]), color=Palette.glow, scale_factor=1.3), run_time=1.0)
        self.wait(Timing.read_long)
        return line


def walk_picture(plane):
    """x, its two hops through S and R, and the single RS jump, over the final grid."""
    composition = Composition("S", "R")
    composition.first_done.set_value(1)
    composition.second_done.set_value(1)
    pieces = VGroup(
        matrix_grid(plane, composition.matrix()),
        vector_arrow(composition.image((1, 0)), Palette.i_hat, plane),
        vector_arrow(composition.image((0, 1)), Palette.j_hat, plane),
        vector_arrow(X, Palette.yellow, plane).set_opacity(0.45),
        vector_arrow(composition.image(X), Palette.yellow, plane),
    )
    hops = VGroup(
        hop(plane, X, (2, 1), Palette.yellow, "S", angle=-PI / 2, direction=DOWN),
        hop(plane, (2, 1), (-1, 2), Palette.yellow, "R", angle=PI / 3),
        hop(plane, X, (-1, 2), Palette.teal, "RS", angle=-PI / 4, direction=UP, along=0.55),
    )
    hops[0].become(dimmed_hop(hops[0], 0.4))
    hops[1].become(dimmed_hop(hops[1], 0.4))
    return VGroup(pieces, hops, ghost(plane, X), ghost(plane, (2, 1)))


def finished_panels():
    group = VGroup()
    for panel_plane_, header, composition, name in order_panels():
        composition.first_done.set_value(1)
        composition.second_done.set_value(1)
        final = composition.image(X)
        pieces = VGroup(
            matrix_grid(panel_plane_, composition.matrix(), box=PANEL_BOX),
            vector_arrow(composition.image((1, 0)), Palette.i_hat, panel_plane_),
            vector_arrow(composition.image((0, 1)), Palette.j_hat, panel_plane_),
            vector_arrow(final, Palette.yellow, panel_plane_),
            Dot(panel_plane_.c2p(*final[:2]), radius=0.08, color=Palette.glow),
        )
        rows = RS if name == "RS" else SR
        label = named_matrix(name, rows, font_size=40).scale(0.75).next_to(panel_plane_, DOWN, buff=0.15)
        group.add(VGroup(panel_plane_, pieces, header, label))
    return group


class FigComposition(Scene):
    def construct(self):
        plane = make_plane(x_range=(-3, 4, 1), y_range=(-1, 3.5, 1))
        panel = backed(named_matrix("RS", RS), padding=0.25).scale(0.8).next_to(plane, RIGHT, buff=0.4)
        self.add(plane, walk_picture(plane), panel)
        fit_to_frame(self)


class FigRowColumn(Scene):
    def construct(self):
        product, sizes = product_layout()
        marks = VGroup(
            SurroundingRectangle(product[0].get_rows()[1], color=Palette.glow, buff=0.1),
            SurroundingRectangle(product[1].get_columns()[2], color=Palette.glow, buff=0.1),
            SurroundingRectangle(product[3].get_entries()[5], color=Palette.glow, buff=0.1),
        )
        work = tex("(-3)(-1)", "+", r"4\cdot 3", "=", "15").next_to(VGroup(product, sizes), DOWN, buff=0.6)
        self.add(product, sizes, marks, work)
        fit_to_frame(self, margin=0.8)


class FigOrderMatters(Scene):
    def construct(self):
        self.add(finished_panels())
        fit_to_frame(self, margin=0.4)


class Poster(Scene):
    def construct(self):
        self.add(finished_panels().scale(1.08).move_to(ORIGIN))
