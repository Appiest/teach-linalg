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
    make_plane,
    matrix,
    morph_matrix,
    moved_grid,
    moved_polygon,
    plane_at,
    plate_for,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (0.8, -0.9)
PLANE_UNIT = 1.15
IDENTITY = ((1, 0), (0, 1))
SHEAR = ((1, 1), (0, 1))
QUARTER_TURN = ((0, -1), (1, 0))
WALK_MATRIX = ((2, -1), (1, 1))
X_SHEAR = (1, 2)
X_WALK = (2, 1)
UNIT_SQUARE = ((0, 0), (1, 0), (1, 1), (0, 1))
GALLERY = [
    (((2, 0), (0, 1)), r"A stretch doubles $\mathbf e_1$ and leaves $\mathbf e_2$ alone."),
    (((-1, 0), (0, 1)), r"A reflection flips $\mathbf e_1$ over to the left."),
    (((1, 0), (1, 1)), r"A vertical shear lifts $\mathbf e_1$ and keeps $\mathbf e_2$."),
    (((1, 0), (0, 0)), r"A projection sends $\mathbf e_2$ to the origin."),
]
BASIS_COLORS = (Palette.i_hat, Palette.j_hat)


def tex(*parts, colors=(), font_size=46):
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


def unknown_matrix():
    mat = matrix([["?", "?"], ["?", "?"]])
    mat.get_entries().set_color(Palette.text_muted)
    return mat


def named(mat, name="A"):
    return VGroup(tex(name, "="), mat).arrange(RIGHT, buff=0.2)


def landing_label(plane, coords, color, direction):
    col = column([str(value) for value in coords], color=color).scale(0.8)
    return backed(col, padding=0.12).next_to(plane.c2p(*coords), direction, buff=0.14)


def live_arrow(plane, tracker, point, color, stroke_width=6):
    tip = tracker.apply(point)
    base = tracker.apply((0, 0))
    if np.hypot(tip[0] - base[0], tip[1] - base[1]) < 0.06:
        return Dot(plane.c2p(*base), radius=0.07, color=color)
    return arrow_between(plane, base, tip, color, stroke_width=stroke_width)


def basis_arrows(plane, tracker):
    return VGroup(
        always_redraw(lambda: live_arrow(plane, tracker, (1, 0), Palette.i_hat)),
        always_redraw(lambda: live_arrow(plane, tracker, (0, 1), Palette.j_hat)),
    )


def square_color(tracker):
    (a, b), (c, d) = tracker.rows()
    return Palette.pink if a * d - b * c < -1e-6 else Palette.yellow


def walk_points(tracker, weights):
    """The corners of a walk of weights[0] green steps then weights[1] red steps, after the map."""
    corners = [(0, 0)] + [(step, 0) for step in range(1, weights[0] + 1)]
    corners += [(weights[0], step) for step in range(1, weights[1] + 1)]
    return [tracker.apply(corner) for corner in corners]


def walk_arrows(plane, tracker, weights):
    points = walk_points(tracker, weights)
    arrows = VGroup()
    for index in range(len(points) - 1):
        color = Palette.i_hat if index < weights[0] else Palette.j_hat
        arrows.add(arrow_between(plane, points[index], points[index + 1], color, stroke_width=5))
    return arrows


class Lesson(LessonScene):
    day = 5
    title = "Matrices are transformations"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        self.plane = plane
        self.tracker = MatrixTracker()
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.one_vector()
        line = self.whole_plane(line)
        line = self.landing_spots(line)
        line = self.grid_rules(line)
        line = self.quarter_turn(line)
        line = self.walk(line)
        line = self.gallery(line)
        line = self.slide(line)
        self.close_episode(
            r"A matrix moves every point of the plane.\\"
            r"Its columns record where $\mathbf e_1$ and $\mathbf e_2$ land.",
            *self.mobjects,
        )

    def one_vector(self):
        plane = self.plane
        self.a_mat = basis_matrix(SHEAR)
        self.x_col = column(X_SHEAR, color=Palette.yellow)
        self.product = VGroup(self.a_mat, self.x_col).arrange(RIGHT, buff=0.15).to_corner(UL, buff=0.6)
        self.plate = plate_for(self.product)
        self.x_arrow = vector_arrow(X_SHEAR, Palette.yellow, plane)
        line = self.say(r"Here is a matrix $A$ and a vector $\mathbf x$.", hold=0.2)
        self.play(FadeIn(self.plate), Write(self.product), run_time=1.2)
        self.play(GrowArrow(self.x_arrow), run_time=1.2, rate_func=spring_soft)
        self.wait(Timing.beat)

        output = tuple(self.tracker_free_apply(SHEAR, X_SHEAR))
        self.answer = VGroup(tex("="), column(output, color=Palette.teal)).arrange(RIGHT, buff=0.2)
        self.answer.next_to(self.product, RIGHT, buff=0.2)
        self.ring = Circle(radius=0.2, color=Palette.glow, stroke_width=4).move_to(plane.c2p(*output))
        line = self.say(r"Yesterday you computed $A\mathbf x$ as a single vector.", line, hold=0.2)
        self.play(self.plate.animate.become(plate_for(VGroup(self.product, self.answer))), run_time=0.5, rate_func=spring_soft)
        self.play(FadeIn(self.answer, shift=LEFT * 0.2), run_time=0.8, rate_func=spring)
        self.play(GrowFromCenter(self.ring), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        return line

    @staticmethod
    def tracker_free_apply(rows, point):
        return (rows[0][0] * point[0] + rows[0][1] * point[1], rows[1][0] * point[0] + rows[1][1] * point[1])

    def whole_plane(self, line):
        plane, tracker = self.plane, self.tracker
        self.grid = always_redraw(lambda: moved_grid(plane, tracker))
        self.basis = basis_arrows(plane, tracker)
        riding_x = always_redraw(lambda: vector_arrow(tracker.apply(X_SHEAR), Palette.yellow, plane))
        line = self.say(r"Now let $A$ move every point of the plane.", line, hold=0.2)
        self.play(plane.animate.set_opacity(0.35), FadeIn(self.grid), run_time=1.0)
        self.remove(self.x_arrow)
        self.add(riding_x)
        still_basis = VGroup(vector_arrow((1, 0), Palette.i_hat, plane), vector_arrow((0, 1), Palette.j_hat, plane))
        self.play(GrowArrow(still_basis[0]), GrowArrow(still_basis[1]), run_time=1.0, rate_func=spring_soft)
        self.remove(*still_basis)
        self.add(self.basis)
        self.bring_to_front(self.plate, self.product, self.answer, self.ring)
        self.wait(Timing.beat)

        line = self.say(r"The grid shears, and $\mathbf x$ rides along to $A\mathbf x$.", line, hold=0.2)
        self.play(*tracker.to(SHEAR), run_time=2.6, rate_func=spring_soft)
        self.play(Flash(self.ring, color=Palette.glow, line_length=0.25), run_time=0.8)
        self.wait(Timing.beat)
        self.play(FadeOut(riding_x), FadeOut(self.ring), run_time=0.5)
        return line

    def landing_spots(self, line):
        plane = self.plane
        labels = VGroup(
            landing_label(plane, (1, 0), Palette.i_hat, DR),
            landing_label(plane, (1, 1), Palette.j_hat, UR),
        )
        line = self.say(r"$\mathbf e_1$ stays put and $\mathbf e_2$ lands on $(1, 1)$.", line, hold=0.2)
        for label in labels:
            self.play(FadeIn(label, scale=0.8), run_time=0.6, rate_func=spring)
        self.wait(Timing.beat)

        line = self.say(r"Those landing spots are exactly the columns of $A$.", line, hold=0.2)
        for label, col in zip(labels, self.a_mat.get_columns()):
            landing = col.copy()
            self.play(TransformFromCopy(label.get_entries(), landing), run_time=1.1)
            self.remove(landing)
            self.play(Indicate(col, color=Palette.glow, scale_factor=1.15), run_time=0.7)
        self.wait(Timing.read_short)
        self.labels = labels
        return line

    def grid_rules(self, line):
        plane = self.plane
        steps = VGroup(*[Dot(plane.c2p(1 + t, t), radius=0.08, color=Palette.glow) for t in range(-1, 4)])
        line = self.say(r"Grid lines stay straight, parallel and evenly spaced.", line, hold=0.2)
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in steps], lag_ratio=0.25), run_time=1.4)
        self.wait(Timing.read_short)
        line = self.say(r"The origin never moves.", line, hold=0.2)
        self.play(FadeOut(steps), run_time=0.4)
        self.play(Flash(plane.c2p(0, 0), color=Palette.glow, line_length=0.3, flash_radius=0.35), run_time=0.9)
        self.wait(Timing.read_short)
        return line

    def quarter_turn(self, line):
        tracker = self.tracker
        question = named(unknown_matrix()).to_corner(UL, buff=0.6)
        line = self.say(r"Now build the matrix for a quarter turn.", line, hold=0.2)
        self.play(FadeOut(self.labels), *tracker.to(IDENTITY), run_time=1.4, rate_func=spring_soft)
        self.play(
            FadeOut(VGroup(self.product, self.answer), shift=UP * 0.2),
            self.plate.animate.become(plate_for(question)),
            run_time=0.6,
        )
        self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7, rate_func=spring_soft)
        self.wait(Timing.beat)

        line = self.say(r"A quarter turn sends $\mathbf e_1$ up and $\mathbf e_2$ left.", line, hold=0.2)
        self.sfx("slide", gain=-2)
        self.play(tracker.turn_to(PI / 2), run_time=2.4, rate_func=spring_soft)
        self.wait(Timing.beat)
        labels = VGroup(
            landing_label(self.plane, (0, 1), Palette.i_hat, UR),
            landing_label(self.plane, (-1, 0), Palette.j_hat, UL),
        )
        for label in labels:
            self.play(FadeIn(label, scale=0.8), run_time=0.6, rate_func=spring)

        answer = named(basis_matrix(QUARTER_TURN)).to_corner(UL, buff=0.6)
        line = self.say(r"Write each landing spot in as a column.", line, hold=0.2)
        self.play(self.plate.animate.become(plate_for(answer)), ReplacementTransform(question[0], answer[0]), ReplacementTransform(question[1].get_brackets(), answer[1].get_brackets()), run_time=0.5)
        for index, label in enumerate(labels):
            self.play(
                FadeOut(question[1].get_columns()[index]),
                TransformFromCopy(label.get_entries(), answer[1].get_columns()[index]),
                run_time=1.1,
            )
        self.wait(Timing.beat)
        line = self.say(r"Two columns are enough to move every point.", line, hold=Timing.beat)
        self.sfx("slide", gain=-2)
        self.remove(question)
        self.play(tracker.turn_to(0, start=PI / 2), FadeOut(labels), FadeOut(answer), FadeOut(self.plate), run_time=1.6, rate_func=spring_soft)
        self.wait(Timing.beat)
        return line

    def walk(self, line):
        plane, tracker = self.plane, self.tracker
        steps = always_redraw(lambda: walk_arrows(plane, tracker, X_WALK))
        riding_x = always_redraw(lambda: vector_arrow(tracker.apply(X_WALK), Palette.yellow, plane))
        line = self.say(r"Every vector is a walk of $\mathbf e_1$ and $\mathbf e_2$ steps.", line, hold=0.2)
        still_x = vector_arrow(X_WALK, Palette.yellow, plane)
        self.play(GrowArrow(still_x), run_time=1.0, rate_func=spring_soft)
        self.remove(still_x)
        self.add(riding_x)
        self.play(FadeOut(self.basis), FadeIn(steps), run_time=1.0)
        self.wait(Timing.read_short)

        line = self.say(r"Move the steps, and the walk moves with them.", line, hold=0.2)
        self.play(*tracker.to(WALK_MATRIX), run_time=2.6, rate_func=spring_soft)
        self.wait(Timing.beat)

        line = self.say(r"So $T(\mathbf x) = x_1T(\mathbf e_1) + x_2T(\mathbf e_2)$ for every $\mathbf x$.", line, hold=0.2)
        panel = self.walk_panel()
        self.plate = plate_for(panel)
        self.play(FadeIn(self.plate), Write(panel[0]), run_time=1.4)
        self.play(FadeIn(panel[1], shift=DOWN * 0.15), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)

        rules = tex(r"T(\mathbf u+\mathbf v) = T(\mathbf u)+T(\mathbf v)", r"\qquad", r"T(c\mathbf u) = c\,T(\mathbf u)", font_size=40)
        rules.next_to(panel, DOWN, buff=0.35, aligned_edge=LEFT)
        line = self.say(r"That works because $T$ keeps sums and multiples.", line, hold=0.2)
        self.play(self.plate.animate.become(plate_for(VGroup(panel, rules))), run_time=0.5, rate_func=spring_soft)
        self.play(FadeIn(rules, shift=DOWN * 0.15), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(panel, rules, self.plate, steps, riding_x)), *tracker.to(IDENTITY), run_time=1.4, rate_func=spring_soft)
        return line

    def walk_panel(self):
        g, r, y, t = Palette.i_hat, Palette.j_hat, Palette.yellow, Palette.teal
        first = tex(r"T(\mathbf x)", "=", "2", r"\,T(\mathbf e_1)", "+", "1", r"\,T(\mathbf e_2)", colors=(y, None, y, g, None, y, r))
        second = VGroup(
            tex("=", "2", colors=(None, y)),
            column((2, 1), color=g),
            tex("+", "1", colors=(None, y)),
            column((-1, 1), color=r),
            tex("="),
            column((3, 3), color=t),
        ).arrange(RIGHT, buff=0.18)
        second.next_to(first, DOWN, buff=0.3, aligned_edge=LEFT).shift(RIGHT * first[0].width)
        return VGroup(first, second).to_corner(UL, buff=0.6)

    def gallery(self, line):
        plane, tracker = self.plane, self.tracker
        square = always_redraw(lambda: moved_polygon(plane, tracker, UNIT_SQUARE, color=square_color(tracker)))
        widest = named(basis_matrix(((-1, 0), (1, 1)))).to_corner(UL, buff=0.6)
        panel = named(basis_matrix(IDENTITY)).move_to(widest, aligned_edge=LEFT)
        self.plate = plate_for(widest)
        line = self.say(r"Here is a small gallery of other moves.", line, hold=0.2)
        self.add(square)
        self.play(FadeIn(square), FadeIn(self.basis), FadeIn(self.plate), FadeIn(panel), run_time=1.0)
        self.bring_to_front(self.basis)
        self.wait(Timing.beat)
        for index, (rows, text) in enumerate(GALLERY):
            if index:
                self.set_gallery_matrix(panel, IDENTITY, run_time=1.0)
            line = self.say(text, line, hold=0.2)
            self.set_gallery_matrix(panel, rows, run_time=2.2)
            self.wait(Timing.read_short)
        self.set_gallery_matrix(panel, IDENTITY, run_time=1.0)
        self.play(FadeOut(VGroup(square, self.basis, panel, self.plate)), run_time=0.6)
        return line

    def set_gallery_matrix(self, panel, rows, run_time):
        target = basis_matrix(rows).next_to(panel[0], RIGHT, buff=0.2)
        morph_matrix(self, panel[1], target, *self.tracker.to(rows), run_time=run_time, rate_func=spring_soft)

    def slide(self, line):
        plane, tracker = self.plane, self.tracker
        moving_origin = always_redraw(lambda: Dot(plane.c2p(*tracker.apply((0, 0))), radius=0.09, color=Palette.glow))
        true_origin = Circle(radius=0.2, color=Palette.glow, stroke_width=4).move_to(plane.c2p(0, 0))
        line = self.say(r"Sliding the plane by $(1, 1)$ moves the origin.", line, hold=0.2)
        self.play(GrowFromCenter(moving_origin), run_time=0.5, rate_func=spring)
        self.play(*tracker.slide_to((1, 1)), run_time=2.0, rate_func=spring_soft)
        self.play(Create(true_origin), run_time=0.7)
        self.wait(Timing.beat)
        line = self.say(r"Since $A\mathbf 0 = \mathbf 0$, no matrix can do that.", line, hold=Timing.read_long)
        return line


def still_tracker(rows):
    return MatrixTracker(rows)


def transformed_picture(plane, rows):
    """A dimmed original grid, the moved grid and the moved basis arrows for a fixed matrix."""
    tracker = still_tracker(rows)
    plane.set_opacity(0.35)
    return VGroup(moved_grid(plane, tracker), live_arrow(plane, tracker, (1, 0), Palette.i_hat), live_arrow(plane, tracker, (0, 1), Palette.j_hat))


def panel_at(mobject, corner_point):
    group = backed(mobject, padding=0.25)
    return group.move_to(corner_point, aligned_edge=UL)


class FigShear(Scene):
    def construct(self):
        plane = make_plane(x_range=(-6, 5, 1), y_range=(-2, 4, 1))
        picture = transformed_picture(plane, SHEAR)
        labels = VGroup(landing_label(plane, (1, 0), Palette.i_hat, DR), landing_label(plane, (1, 1), Palette.j_hat, UL))
        output = Lesson.tracker_free_apply(SHEAR, X_SHEAR)
        x_arrow = vector_arrow(output, Palette.yellow, plane)
        x_name = backed(tex(r"A\mathbf x", colors=(Palette.yellow,), font_size=40)).next_to(plane.c2p(*output), RIGHT, buff=0.15)
        panel = panel_at(named(basis_matrix(SHEAR)), plane.c2p(-5.7, 3.7))
        self.add(plane, picture, x_arrow, x_name, labels, panel)
        fit_to_frame(self)


class FigQuarterTurn(Scene):
    def construct(self):
        plane = make_plane(x_range=(-6, 4, 1), y_range=(-2, 3, 1))
        picture = transformed_picture(plane, QUARTER_TURN)
        labels = VGroup(landing_label(plane, (0, 1), Palette.i_hat, UR), landing_label(plane, (-1, 0), Palette.j_hat, UL))
        panel = panel_at(named(basis_matrix(QUARTER_TURN)), plane.c2p(1.6, 2.8))
        self.add(plane, picture, labels, panel)
        fit_to_frame(self)


class FigWalk(Scene):
    def construct(self):
        plane = make_plane(x_range=(-4, 6, 1), y_range=(-2, 4, 1))
        tracker = still_tracker(WALK_MATRIX)
        picture = transformed_picture(plane, WALK_MATRIX)
        steps = walk_arrows(plane, tracker, X_WALK)
        x_arrow = vector_arrow(tracker.apply(X_WALK), Palette.yellow, plane)
        name = backed(tex(r"T(\mathbf x)", colors=(Palette.yellow,), font_size=40)).next_to(plane.c2p(3, 3), UL, buff=0.1)
        step_names = VGroup(
            backed(tex(r"T(\mathbf e_1)", colors=(Palette.i_hat,), font_size=36)).next_to(plane.c2p(1, 0.5), DR, buff=0.1),
            backed(tex(r"T(\mathbf e_2)", colors=(Palette.j_hat,), font_size=36)).next_to(plane.c2p(4.1, 2.6), RIGHT, buff=0.1),
        )
        self.add(plane, picture[0], steps, x_arrow, name, step_names)
        fit_to_frame(self)


def gallery_tile(rows):
    plane = make_plane(x_range=(-2, 3, 1), y_range=(-2, 3, 1), x_length=4.2, y_length=4.2)
    tracker = still_tracker(rows)
    picture = transformed_picture(plane, rows)
    square = moved_polygon(plane, tracker, UNIT_SQUARE, color=square_color(tracker))
    ghost = moved_polygon(plane, still_tracker(IDENTITY), UNIT_SQUARE, color=Palette.text, opacity=0.0)
    ghost.set_stroke(Palette.text_muted, width=2, opacity=0.8)
    label = basis_matrix(rows).scale(0.8).next_to(plane, DOWN, buff=0.3)
    return VGroup(plane, picture[0], ghost, square, picture[1], picture[2], label)


class FigGallery(Scene):
    def construct(self):
        tiles = VGroup(*[gallery_tile(rows) for rows, _ in GALLERY]).arrange(RIGHT, buff=0.6)
        self.add(tiles)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        picture = transformed_picture(plane, SHEAR)
        square = moved_polygon(plane, still_tracker(SHEAR), UNIT_SQUARE)
        labels = VGroup(landing_label(plane, (1, 0), Palette.i_hat, DR), landing_label(plane, (1, 1), Palette.j_hat, UR))
        panel = named(basis_matrix(SHEAR), "A").scale(1.2).to_corner(UL, buff=0.7)
        self.add(plane, picture[0], square, picture[1], picture[2], labels, plate_for(panel), panel)
