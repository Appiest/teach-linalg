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
    clip_line_to_box,
    column,
    fit_to_frame,
    matrix,
    plate_for,
    scrim,
    skewed_grid,
    spring,
    spring_soft,
    vector_arrow,
    wide_plane_at,
)

A = ((1, 2), (1, 0))
E1, E2 = (1, 0), (0, 1)
V1, V2 = (2, 1), (-1, 1)
DAY22_B2 = (-1, 2)
X = (1, 2)
X_IN_B = (1, 1)
AX = (5, 1)
AX_IN_B = (2, -1)

UNIT = 0.95
LEFT_ORIGIN = (-5.5, -1.5)
RIGHT_ORIGIN = (1.6, -1.5)
HALF_GAP = 0.1
LEFT_BOX = ((-7.2, -HALF_GAP), (-4.1, 4.1))
RIGHT_BOX = ((HALF_GAP, 7.2), (-4.1, 4.1))

STANDARD_COLORS = (Palette.i_hat, Palette.j_hat)
EIGEN_COLORS = (Palette.yellow, Palette.blue)
GRID_REACH = 22

ORBIT_ORIGIN = (-6.3, -2.2)
ORBIT_UNIT = 1.0
ORBIT_BOX = ((-7.2, 2.2), (-4.1, 4.1))
ORBIT_START = (0.25, 1.0)
ORBIT_STEPS = 4


def scene_box_in_plane(box, origin, unit):
    """A box given in scene coordinates, rewritten in the plane coordinates of a grid at `origin`."""
    (x0, x1), (y0, y1) = box
    return ((x0 - origin[0]) / unit, (x1 - origin[0]) / unit), ((y0 - origin[1]) / unit, (y1 - origin[1]) / unit)


def in_basis(weights, basis):
    return (weights[0] * basis[0][0] + weights[1] * basis[1][0], weights[0] * basis[0][1] + weights[1] * basis[1][1])


def tex(*parts, colors=(), font_size=40):
    """MathTex split into parts, with parts[i] painted colors[i] where a color is given."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def name_label(tex_string, color, point, direction, font_size=34):
    return backed(MathTex(tex_string, color=color, font_size=font_size), padding=0.07).next_to(point, direction, buff=0.1)


def colored_column(entries, colors, scale=0.72):
    col = column([format_entry(value) for value in entries]).scale(scale)
    for entry, color in zip(col.get_entries(), colors):
        entry.set_color(color)
    return col


def format_entry(value):
    fractions = {0.25: r"\tfrac14", 0.5: r"\tfrac12"}
    if value in fractions:
        return fractions[value]
    return str(int(value)) if float(value).is_integer() else str(value)


def column_matrix(rows, colors, scale=0.72):
    """A matrix whose columns are painted one color each."""
    mat = matrix([[str(entry) for entry in row] for row in rows]).scale(scale)
    for col, color in zip(mat.get_columns(), colors):
        col.set_color(color)
    return mat


def named(name_tex, body, font_size=36, colors=()):
    name = tex(*name_tex, "=", colors=colors, font_size=font_size) if isinstance(name_tex, tuple) else tex(name_tex, "=", font_size=font_size)
    return VGroup(name, body).arrange(RIGHT, buff=0.18)


def clipped_line(plane, direction, box, color, stroke_width=2.4, opacity=0.9):
    ends = clip_line_to_box((direction[1], -direction[0], 0), box[0], box[1])
    return Line(plane.c2p(*ends[0]), plane.c2p(*ends[1]), color=color, stroke_width=stroke_width, stroke_opacity=opacity)


def safe_arrow(plane, start, end, color, stroke_width=6):
    """An arrow from start to end, or nothing while the two points nearly meet."""
    if np.hypot(end[0] - start[0], end[1] - start[1]) < 0.08:
        return VMobject()
    return arrow_between(plane, start, end, color, stroke_width=stroke_width)


class Half:
    """One copy of the plane, clipped to half the frame, with a grid built from a basis."""

    def __init__(self, origin, box, basis, colors, grid_color):
        self.plane = wide_plane_at(origin, UNIT, reach=30)
        self.box = scene_box_in_plane(box, origin, UNIT)
        self.basis = basis
        self.colors = colors
        self.grid_color = grid_color

    def point(self, coords):
        return self.plane.c2p(*coords)

    def static_grid(self, opacity=0.28):
        grid = skewed_grid(self.plane, *self.basis, reach=GRID_REACH, color=self.grid_color, opacity=opacity, box=self.box)
        axes = VGroup(*[clipped_line(self.plane, v, self.box, color, 2.2, 0.55) for v, color in zip(self.basis, self.axis_colors())])
        return VGroup(grid, axes)

    def axis_colors(self):
        return (Palette.axis, Palette.axis) if self.colors == STANDARD_COLORS else self.colors

    def moving_grid(self, live):
        return always_redraw(
            lambda: skewed_grid(
                self.plane, live.point(self.basis[0]), live.point(self.basis[1]), reach=GRID_REACH, color=self.grid_color, opacity=0.85, box=self.box
            )
        )

    def moving_basis(self, live):
        return VGroup(*[always_redraw(lambda v=v, c=c: safe_arrow(self.plane, (0, 0), live.point(v), c)) for v, c in zip(self.basis, self.colors)])

    def x_arrow(self, coords=X, color=Palette.yellow):
        return vector_arrow(coords, color, self.plane)


def top_plate(rows, corner_x, y_top=3.85):
    content = VGroup(*rows).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    content.move_to(np.array([corner_x + content.width / 2, y_top - content.height / 2, 0]))
    return content


def mapping_readout(names, entries, colors, name_colors):
    """name0 = column0  |->  name1 = column1, each part separately addressable."""
    first = tex(names[0], "=", colors=(name_colors[0],), font_size=36)
    first_col = colored_column(entries[0], colors)
    arrow = MathTex(r"\mapsto", color=Palette.text_muted, font_size=40)
    second = tex(names[1], "=", colors=(name_colors[1],), font_size=36)
    second_col = colored_column(entries[1], colors)
    return VGroup(first, first_col, arrow, second, second_col).arrange(RIGHT, buff=0.16)


def commuting_square():
    corners = {"bl": np.array([-3.0, -0.2, 0]), "tl": np.array([-3.0, 2.5, 0]), "tr": np.array([3.0, 2.5, 0]), "br": np.array([3.0, -0.2, 0])}
    nodes = VGroup(
        MathTex(r"[\mathbf x]_{\mathcal B}", color=Palette.yellow, font_size=50).move_to(corners["bl"]),
        MathTex(r"\mathbf x", color=Palette.yellow, font_size=50).move_to(corners["tl"]),
        MathTex(r"A\mathbf x", color=Palette.teal, font_size=50).move_to(corners["tr"]),
        MathTex(r"[A\mathbf x]_{\mathcal B}", color=Palette.teal, font_size=50).move_to(corners["br"]),
    )
    edges = VGroup(
        square_edge(corners["bl"] + UP * 0.45, corners["tl"] + DOWN * 0.4, "P", LEFT),
        square_edge(corners["tl"] + RIGHT * 0.45, corners["tr"] + LEFT * 0.6, "A", UP),
        square_edge(corners["tr"] + DOWN * 0.4, corners["br"] + UP * 0.45, "P^{-1}", RIGHT),
        square_edge(corners["bl"] + RIGHT * 0.75, corners["br"] + LEFT * 0.95, "D", DOWN),
    )
    return VGroup(nodes, edges)


def square_edge(start, end, name, side):
    arrow = Arrow(start, end, buff=0, color=Palette.text_muted, stroke_width=5, max_tip_length_to_length_ratio=0.1)
    label = MathTex(name, color=Palette.text, font_size=44).next_to(arrow, side, buff=0.18)
    return VGroup(arrow, label)


def square_numbers():
    return MathTex(
        r"\tfrac13\begin{bmatrix} 1 & 1 \\ -1 & 2 \end{bmatrix}",
        r"\begin{bmatrix} 1 & 2 \\ 1 & 0 \end{bmatrix}",
        r"\begin{bmatrix} 2 & -1 \\ 1 & 1 \end{bmatrix}",
        "=",
        r"\begin{bmatrix} 2 & 0 \\ 0 & -1 \end{bmatrix}",
        color=Palette.text,
        font_size=40,
    )


def diagonal_matrix(zero_color=Palette.glow):
    mat = column_matrix(((2, 0), (0, -1)), EIGEN_COLORS)
    for row, col in ((0, 1), (1, 0)):
        mat.get_rows()[row][col].set_color(zero_color)
    return mat


class Lesson(LessonScene):
    day = 33
    title = "Diagonalizing a linear transformation"

    def construct(self):
        pulse = self.open_episode()
        self.play(FadeOut(pulse), run_time=0.5)
        self.left = Half(LEFT_ORIGIN, LEFT_BOX, (E1, E2), STANDARD_COLORS, Palette.grid)
        self.right = Half(RIGHT_ORIGIN, RIGHT_BOX, (V1, V2), EIGEN_COLORS, Palette.purple_gray)
        self.live = LiveTransform()
        line = self.two_grids()
        line = self.track_x(line)
        line = self.act(line)
        line = self.read_matrix(line)
        line = self.square(line)
        line = self.similar(line)
        line = self.powers(line)
        self.close_episode(
            r"In a basis of eigenvectors, the map only stretches each axis.\\"
            r"So its matrix there is the diagonal matrix $D = P^{-1}AP$.",
            *self.mobjects,
        )

    def two_grids(self):
        left, right = self.left, self.right
        self.left_static, self.right_static = left.static_grid(), right.static_grid()
        self.left_moving, self.right_moving = left.moving_grid(self.live), right.moving_grid(self.live)
        self.left_basis, self.right_basis = left.moving_basis(self.live), right.moving_basis(self.live)
        self.a_row = named("A", column_matrix(A, STANDARD_COLORS))
        self.left_plate_rows = VGroup(self.a_row)
        top_plate([self.a_row], -6.85)
        self.left_plate = plate_for(self.a_row, padding=0.2).set_z_index(9)
        self.play(FadeIn(self.left_static), Create(self.left_moving, lag_ratio=0.01), run_time=1.4)
        line = self.say(r"Here is Day 22's matrix $A$ on the standard grid.", hold=0.2)
        self.play(*[GrowArrow(a) for a in self.left_basis], FadeIn(self.left_plate), FadeIn(self.a_row), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.beat)

        self.b_row = named(r"\mathcal B", tex(r"\{", r"\mathbf v_1", ",", r"\mathbf v_2", r"\}", colors=(None, Palette.yellow, None, Palette.blue), font_size=36))
        top_plate([self.b_row], 0.45)
        self.right_plate = plate_for(self.b_row, padding=0.2).set_z_index(9)
        self.v_labels = VGroup(
            name_label(r"\mathbf v_1", Palette.yellow, right.point(V1), DR),
            name_label(r"\mathbf v_2", Palette.blue, right.point(V2), UP),
        )
        self.play(FadeIn(self.right_static), Create(self.right_moving, lag_ratio=0.01), run_time=1.4)
        line = self.say(r"Its eigenvectors make a basis $\mathcal B$ with its own grid.", line, hold=0.2)
        self.play(*[GrowArrow(a) for a in self.right_basis], FadeIn(self.v_labels), FadeIn(self.right_plate), FadeIn(self.b_row), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)
        return line

    def track_x(self, line):
        left, right = self.left, self.right
        self.x_left, self.x_right = left.x_arrow(), right.x_arrow()
        self.x_names = VGroup(name_label(r"\mathbf x", Palette.yellow, left.point(X), UL), name_label(r"\mathbf x", Palette.yellow, right.point(X), UL))
        self.blue_leg = always_redraw(lambda: safe_arrow(right.plane, self.live.point(V1), self.live.point(V1) + self.live.point(V2), Palette.blue, stroke_width=5))
        self.left_readout = mapping_readout((r"\mathbf x", r"A\mathbf x"), (X, AX), STANDARD_COLORS, (Palette.yellow, Palette.teal))
        self.right_readout = mapping_readout((r"[\mathbf x]_{\mathcal B}", r"[A\mathbf x]_{\mathcal B}"), (X_IN_B, AX_IN_B), EIGEN_COLORS, (Palette.yellow, Palette.teal))
        self.place_readouts()
        line = self.say(r"Track one vector $\mathbf x$ in both coordinate systems.", line, hold=0.2)
        self.play(GrowArrow(self.x_left), GrowArrow(self.x_right), FadeIn(self.x_names), run_time=1.1, rate_func=spring_soft)
        self.play(GrowArrow(self.blue_leg), run_time=0.9, rate_func=spring_soft)
        self.play(
            self.left_plate.animate.become(plate_for(VGroup(self.a_row, self.left_readout), padding=0.2).set_z_index(9)),
            self.right_plate.animate.become(plate_for(VGroup(self.b_row, self.right_readout), padding=0.2).set_z_index(9)),
            FadeIn(self.left_readout[:2]),
            FadeIn(self.right_readout[:2]),
            run_time=0.9,
        )
        self.wait(Timing.read_short)
        return line

    def place_readouts(self):
        for row, readout in ((self.a_row, self.left_readout), (self.b_row, self.right_readout)):
            readout.next_to(row, DOWN, buff=0.3).align_to(row, LEFT)
            readout.set_z_index(10)
        self.a_row.set_z_index(10)
        self.b_row.set_z_index(10)

    def act(self, line):
        left, right = self.left, self.right
        riders = VGroup(
            always_redraw(lambda: vector_arrow(tuple(self.live.point(X)), Palette.teal, left.plane)),
            always_redraw(lambda: vector_arrow(tuple(self.live.point(X)), Palette.teal, right.plane)),
        )
        self.add(riders)
        self.bring_to_front(self.x_left, self.x_right, self.left_basis, self.right_basis, self.blue_leg)
        line = self.say(r"Now let $A$ act on both pictures at once.", line, hold=0.2)
        self.play(FadeOut(self.v_labels), FadeOut(self.x_names), run_time=0.4)
        self.play(self.live.apply(A), run_time=4.0, rate_func=spring_soft)
        self.riders = riders
        line = self.say(r"On the standard grid, every cell slants and turns.", line, hold=Timing.read_short)
        line = self.say(r"On the eigen-grid, lines slide onto lines and cells only stretch.", line, hold=Timing.read_short)
        return self.land_x(line)

    def land_x(self, line):
        left, right = self.left, self.right
        self.ax_names = VGroup(name_label(r"A\mathbf x", Palette.teal, left.point(AX), UR), name_label(r"A\mathbf x", Palette.teal, right.point(AX), DOWN))
        self.steps = VGroup(*[Dot(right.point(in_basis((k, 0), (V1, V2))), radius=0.08, color=Palette.yellow) for k in (1, 2)])
        self.steps.add(Dot(right.point(AX), radius=0.08, color=Palette.blue))
        line = self.say(r"In $\mathcal B$-coordinates, $A$ doubles the first entry and flips the second.", line, hold=0.2)
        self.play(FadeIn(self.ax_names), FadeIn(self.left_readout[2:]), FadeIn(self.right_readout[2:]), run_time=0.9)
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in self.steps], lag_ratio=0.35), run_time=1.3)
        self.wait(Timing.read_short)
        return line

    def read_matrix(self, line):
        right = self.right
        av1 = backed(colored_column((2, 0), EIGEN_COLORS), padding=0.1).next_to(right.point((4, 2)), UR, buff=0.12)
        av2 = backed(colored_column((0, -1), EIGEN_COLORS), padding=0.1).next_to(right.point((1, -1)), RIGHT, buff=0.3).shift(UP * 0.4)
        av1.set_z_index(8)
        av2.set_z_index(8)
        blank = column_matrix(((2, 0), (0, -1)), EIGEN_COLORS)
        t_row = named(r"[T]_{\mathcal B}", blank).set_z_index(10)
        t_row.move_to(self.b_row, aligned_edge=LEFT)
        line = self.say(r"Column $j$ of $[T]_{\mathcal B}$ is $[A\mathbf v_j]_{\mathcal B}$, as on Day 21.", line, hold=0.2)
        self.play(FadeOut(self.steps), FadeOut(self.ax_names), FadeIn(av1, shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        self.play(FadeIn(av2, shift=UP * 0.1), run_time=0.7, rate_func=spring_soft)
        self.play(FadeOut(self.b_row), FadeIn(t_row[0]), FadeIn(blank.get_brackets()), run_time=0.6)
        self.play(TransformFromCopy(av1.get_entries(), blank.get_columns()[0]), run_time=1.1, rate_func=spring)
        self.play(TransformFromCopy(av2.get_entries(), blank.get_columns()[1]), run_time=1.1, rate_func=spring)
        self.add(t_row)
        zeros = [blank.get_rows()[0][1], blank.get_rows()[1][0]]
        line = self.say(r"Eigenvectors only stretch, so every entry off the diagonal is 0.", line, hold=0.2)
        self.play(*[zero.animate.set_color(Palette.glow) for zero in zeros], *[Flash(zero.get_center(), color=Palette.glow, line_length=0.14, flash_radius=0.24) for zero in zeros], run_time=1.0)
        self.wait(Timing.read_short)
        self.play(FadeOut(av1), FadeOut(av2), run_time=0.5)
        self.t_row = t_row
        return line

    def square(self, line):
        veil = scrim().set_z_index(20)
        nodes, edges = commuting_square().set_z_index(21)
        numbers = square_numbers().set_z_index(21).move_to(DOWN * 2.05)
        numbers[-1].set_color(Palette.teal)
        line = self.say(r"Up by $P$, across by $A$, down by $P^{-1}$: the same map as $D$.", line, hold=0.2)
        self.play(FadeIn(veil), run_time=0.6)
        self.play(FadeIn(nodes), FadeIn(edges), run_time=1.0)
        for edge in edges[:3]:
            self.play(edge[0].animate.set_color(Palette.glow), run_time=0.7)
        self.play(edges[3][0].animate.set_color(Palette.teal), run_time=0.7)
        self.wait(Timing.beat)
        line = self.say(r"So an eigenvector basis turns $A$ into the diagonal matrix $D$.", line, hold=0.2)
        self.play(FadeIn(numbers, shift=UP * 0.15), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_long)
        self.remove(*[m for m in self.mobjects if m.z_index < 20])
        self.live = LiveTransform()
        self.play(FadeOut(VGroup(nodes, edges, numbers)), run_time=0.6)
        self.veil = veil
        return line

    def similar(self, line):
        panels = [
            SmallView(-4.6, (E1, E2), STANDARD_COLORS, Palette.grid, r"[T]_{\mathcal E}", column_matrix(A, STANDARD_COLORS)),
            SmallView(0.0, (V1, DAY22_B2), (Palette.yellow, Palette.pink), Palette.pink, r"[T]_{\mathcal C}", column_matrix(((2, 1), (0, -1)), (Palette.yellow, Palette.pink))),
            SmallView(4.6, (V1, V2), EIGEN_COLORS, Palette.purple_gray, r"[T]_{\mathcal B}", diagonal_matrix(Palette.text)),
        ]
        drawings = VGroup(*[panel.drawing(self.live) for panel in panels])
        names = VGroup(*[panel.caption() for panel in panels])
        line = self.say(r"Every basis gives its own matrix for the same map.", line, hold=0.2)
        self.play(FadeIn(drawings), FadeOut(self.veil), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(name, shift=UP * 0.1) for name in names], lag_ratio=0.3), run_time=1.4)
        self.play(self.live.apply(A), run_time=3.0, rate_func=spring_soft)
        invariants = MathTex(r"\operatorname{tr} = 1 \qquad \det = -2 \qquad \lambda = 2,\ -1", color=Palette.text_muted, font_size=34).move_to(DOWN * 2.55)
        line = self.say(r"These matrices are all similar, so they share trace and determinant.", line, hold=0.2)
        self.play(FadeIn(invariants, shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        outline = SurroundingRectangle(names[2], color=Palette.glow, buff=0.14, stroke_width=3)
        line = self.say(r"Only the eigenbasis makes the matrix diagonal.", line, hold=0.2)
        self.play(Create(outline), run_time=0.8)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(drawings, names, invariants, outline)), run_time=0.7)
        return line

    def powers(self, line):
        orbit = Orbit()
        panel = orbit.panel()
        self.play(FadeIn(orbit.backdrop), run_time=0.9)
        line = self.say(r"Powers of $A$ are where the eigenbasis pays off.", line, hold=0.2)
        dot, arrow = orbit.dot_at(0), orbit.arrow_to(0)
        self.play(FadeIn(dot), FadeIn(arrow), FadeIn(panel.plate), FadeIn(panel.rows[0]), run_time=0.9)
        line = self.say(r"Each step doubles the $\mathbf v_1$ part and flips the $\mathbf v_2$ part.", line, hold=0.2)
        ghosts = VGroup()
        for k in range(1, ORBIT_STEPS + 1):
            ghosts.add(orbit.ghost(k - 1), orbit.step_path(k))
            self.add(ghosts[-2:])
            self.play(Transform(dot, orbit.dot_at(k)), Transform(arrow, orbit.arrow_to(k)), FadeIn(panel.rows[k], shift=UP * 0.08), run_time=0.9, rate_func=spring)
        self.wait(Timing.beat)
        line = self.say(r"So $A^k\mathbf x_0 = \tfrac14\,2^k\,\mathbf v_1 + (-1)^k\,\mathbf v_2$, no matrix products.", line, hold=0.2)
        self.play(FadeIn(panel.formula, shift=UP * 0.1), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"In the long run the arrow lines up with $\mathbf v_1$.", line, hold=0.2)
        self.play(Create(orbit.eigenline()), run_time=1.0)
        self.wait(Timing.read_short)
        return line


class SmallView:
    """A small copy of the plane showing one basis, its grid moving with the map, and the map's matrix in that basis."""

    def __init__(self, center_x, basis, colors, grid_color, name, mat):
        self.origin = (center_x - 1.0, 0.6)
        self.plane = wide_plane_at(self.origin, 0.6, reach=30)
        self.box = scene_box_in_plane(((center_x - 2.05, center_x + 2.05), (-0.75, 3.1)), self.origin, 0.6)
        self.center_x, self.basis, self.colors, self.grid_color = center_x, basis, colors, grid_color
        self.name, self.mat = name, mat

    def drawing(self, live):
        plane, box = self.plane, self.box
        static = skewed_grid(plane, *self.basis, reach=GRID_REACH, color=self.grid_color, opacity=0.22, box=box)
        moving = always_redraw(lambda: skewed_grid(plane, live.point(self.basis[0]), live.point(self.basis[1]), reach=GRID_REACH, color=self.grid_color, opacity=0.8, box=box))
        arrows = VGroup(*[always_redraw(lambda v=v, c=c: safe_arrow(plane, (0, 0), live.point(v), c, stroke_width=5)) for v, c in zip(self.basis, self.colors)])
        return VGroup(static, moving, arrows)

    def caption(self):
        return named(self.name, self.mat, font_size=34).move_to(np.array([self.center_x, -1.55, 0]))


class Orbit:
    """The orbit x_k = A^k x_0 drawn on the eigen-grid, with its B-coordinates listed beside it."""

    def __init__(self):
        self.plane = wide_plane_at(ORBIT_ORIGIN, ORBIT_UNIT, reach=30)
        self.box = scene_box_in_plane(ORBIT_BOX, ORBIT_ORIGIN, ORBIT_UNIT)
        grid = skewed_grid(self.plane, V1, V2, reach=GRID_REACH, color=Palette.purple_gray, opacity=0.5, box=self.box)
        axes = VGroup(*[clipped_line(self.plane, v, self.box, c, 2.2, 0.45) for v, c in zip((V1, V2), EIGEN_COLORS)])
        self.backdrop = VGroup(grid, axes)

    def weights(self, k):
        return (ORBIT_START[0] * 2**k, ORBIT_START[1] * (-1) ** k)

    def position(self, k):
        return in_basis(self.weights(k), (V1, V2))

    def dot_at(self, k):
        return Dot(self.plane.c2p(*self.position(k)), radius=0.1, color=Palette.teal).set_z_index(3)

    def ghost(self, k):
        point = self.plane.c2p(*self.position(k))
        dot = Dot(point, radius=0.08, color=Palette.teal).set_opacity(0.6)
        side = RIGHT if self.weights(k)[1] < 0 else UP
        name = MathTex(rf"\mathbf x_{k}", color=Palette.teal, font_size=30).set_opacity(0.8).next_to(point, side, buff=0.12)
        return VGroup(dot, name)

    def step_path(self, k):
        return DashedLine(self.plane.c2p(*self.position(k - 1)), self.plane.c2p(*self.position(k)), color=Palette.teal, stroke_width=2, stroke_opacity=0.5, dash_length=0.1)

    def arrow_to(self, k):
        return vector_arrow(self.position(k), Palette.teal, self.plane, stroke_width=4).set_opacity(0.8)

    def eigenline(self):
        return clipped_line(self.plane, V1, self.box, Palette.yellow, 4.0, 0.9)

    def panel(self):
        rows = VGroup()
        for k in range(ORBIT_STEPS + 1):
            coefficient = "" if self.weights(k)[0] == 1 else format_entry(self.weights(k)[0])
            sign = "+" if self.weights(k)[1] > 0 else "-"
            rows.add(tex(rf"\mathbf x_{k}", "=", coefficient, r"\,\mathbf v_1", sign, r"\mathbf v_2", colors=(None, None, Palette.yellow, Palette.yellow, Palette.blue, Palette.blue), font_size=40))
        rows.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        for row in rows[1:]:
            row.shift(RIGHT * (rows[0][1].get_x() - row[1].get_x()))
        formula = MathTex(r"A^k = P D^k P^{-1}", color=Palette.text, font_size=40)
        body = VGroup(rows, formula).arrange(DOWN, buff=0.45)
        body.move_to(np.array([4.75, 0.55, 0]))
        plate = plate_for(body, padding=0.3)
        panel = VGroup(plate, body).set_z_index(10)
        panel.plate, panel.rows, panel.formula = plate, rows, formula
        return panel


def split_picture(scene, acted=True):
    left = Half(LEFT_ORIGIN, LEFT_BOX, (E1, E2), STANDARD_COLORS, Palette.grid)
    right = Half(RIGHT_ORIGIN, RIGHT_BOX, (V1, V2), EIGEN_COLORS, Palette.purple_gray)
    live = LiveTransform(A if acted else None)
    for half in (left, right):
        scene.add(half.static_grid(), half.moving_grid(live), half.moving_basis(live))
        scene.add(half.x_arrow())
        if acted:
            scene.add(half.x_arrow(AX, Palette.teal))
    scene.add(safe_arrow(right.plane, live.point(V1), live.point(V1) + live.point(V2), Palette.blue, stroke_width=5))
    return left, right


class FigTwoGrids(Scene):
    def construct(self):
        left, right = split_picture(self)
        a_row = named("A", column_matrix(A, STANDARD_COLORS))
        t_row = named(r"[T]_{\mathcal B}", diagonal_matrix())
        readouts = (
            mapping_readout((r"\mathbf x", r"A\mathbf x"), (X, AX), STANDARD_COLORS, (Palette.yellow, Palette.teal)),
            mapping_readout((r"[\mathbf x]_{\mathcal B}", r"[A\mathbf x]_{\mathcal B}"), (X_IN_B, AX_IN_B), EIGEN_COLORS, (Palette.yellow, Palette.teal)),
        )
        for row, readout, x in ((a_row, readouts[0], -6.85), (t_row, readouts[1], 0.45)):
            content = top_plate([row, readout], x)
            self.add(plate_for(content, padding=0.2), content)
        self.add(name_label(r"A\mathbf x", Palette.teal, left.point(AX), UR), name_label(r"A\mathbf x", Palette.teal, right.point(AX), DOWN))
        self.add(name_label(r"\mathbf x", Palette.yellow, left.point(X), UL), name_label(r"\mathbf x", Palette.yellow, right.point(X), UL))


class FigSquare(Scene):
    def construct(self):
        self.add(commuting_square(), square_numbers().move_to(DOWN * 2.05))
        fit_to_frame(self)


class FigOrbit(Scene):
    def construct(self):
        orbit = Orbit()
        panel = orbit.panel()
        self.add(orbit.backdrop, orbit.eigenline())
        self.add(*[orbit.step_path(k) for k in range(1, ORBIT_STEPS + 1)])
        self.add(*[orbit.ghost(k) for k in range(ORBIT_STEPS)], orbit.arrow_to(ORBIT_STEPS), orbit.dot_at(ORBIT_STEPS), panel)


class Poster(Scene):
    def construct(self):
        split_picture(self)
        a_row = named("A", column_matrix(A, STANDARD_COLORS), font_size=44)
        t_row = named(r"[T]_{\mathcal B}", diagonal_matrix(), font_size=44)
        for row, x in ((a_row, -6.85), (t_row, 0.45)):
            content = top_plate([row.scale(1.2)], x)
            self.add(plate_for(content, padding=0.2), content)
