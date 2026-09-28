import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    Palette,
    Timing,
    arrow_between,
    augmented,
    backed,
    fit_to_frame,
    morph_matrix,
    oblique_projector,
    plane_at,
    plate_for,
    projected_arrow,
    spring,
    spring_soft,
    vector_arrow,
)

V = (3, 2)
W = (-1, 2)
B = (5, 6)
LOOP_WEIGHTS = (2, 1, -1)
PLANE_ORIGIN = (-1.4, -2.75)
PLANE_UNIT = 0.8

U3 = np.array([1.0, -1.0, 0.0])
V3 = np.array([1.0, 2.0, 0.0])
W_FLOOR = U3 + V3
H_START = 2.0
BASE_AREA = 3
VIEW_ORIGIN = (2.9, 0.45)
VIEW_UNIT = 1.1
ELEVATION = 28 * DEGREES
AZIMUTH_START = 24 * DEGREES
DRIFT_PER_SECOND = 0.3 * DEGREES
FLOOR_REACH = ((-1, 4), (-2, 3))
PATCH_WEIGHTS = (-0.35, 2.15)

COLUMN_COLORS = (Palette.yellow, Palette.blue, Palette.pink, Palette.text)
PANEL_LEFT = -6.7


def w_vector(h):
    return W_FLOOR + np.array([0.0, 0.0, h])


def chain_points(weights, vectors):
    """Partial sums 0, c1 v1, c1 v1 + c2 v2, ... in the plane."""
    points = [np.zeros(2)]
    for weight, vector in zip(weights, vectors):
        points.append(points[-1] + weight * np.array(vector, dtype=float))
    return points


def chain_arrows(plane, weights, colors=(Palette.yellow, Palette.blue, Palette.pink)):
    """Each weighted vector drawn from the tip of the one before, skipping any that shrink to nothing."""
    points = chain_points(weights, (V, W, B))
    arrows = VGroup()
    for start, end, color in zip(points, points[1:], colors):
        if np.linalg.norm(end - start) > 0.12:
            arrows.add(arrow_between(plane, start, end, color, stroke_width=5))
    return arrows


def point_on_path(points, progress):
    """The point a fraction `progress` of the way along the polyline through `points` (by segment count)."""
    segments = len(points) - 1
    index = min(int(progress * segments), segments - 1)
    local = progress * segments - index
    return (1 - local) * np.asarray(points[index]) + local * np.asarray(points[index + 1])


def walker(position):
    """A small orange dot that follows `position()` every frame."""
    return always_redraw(lambda: Dot(position(), radius=0.11, color=Palette.glow))


def colored_columns(mat):
    for index, entries in enumerate(mat.get_columns()):
        entries.set_color(COLUMN_COLORS[index % len(COLUMN_COLORS)])
    return mat


def column_matrix(rows):
    return colored_columns(augmented(rows))


def plain_columns(rows):
    from engine.theme import matrix

    mat = matrix([[str(entry) for entry in row] for row in rows])
    for index, entries in enumerate(mat.get_columns()):
        entries.set_color(COLUMN_COLORS[index])
    return mat


def pivot_box(entry, opacity=1.0):
    return SurroundingRectangle(entry, color=Palette.glow, buff=0.1, stroke_width=3, stroke_opacity=opacity, corner_radius=0)


def relation_tex(parts, font_size=40):
    """A colored sum like 2v + w - b = 0 from (tex, color) parts."""
    tex = MathTex(*[part for part, _ in parts], font_size=font_size)
    for piece, (_, color) in zip(tex, parts):
        piece.set_color(color)
    return tex


class View:
    """A fixed oblique view of 3D space whose azimuth lives in a tracker, so the camera can drift."""

    def __init__(self, origin=VIEW_ORIGIN, unit=VIEW_UNIT, azimuth=AZIMUTH_START):
        self.origin = origin
        self.unit = unit
        self.azimuth = ValueTracker(azimuth)

    def project(self, point):
        return oblique_projector(self.origin, self.unit, self.azimuth.get_value(), ELEVATION)(point)

    def floor_and_axes(self):
        (x_low, x_high), (y_low, y_high) = FLOOR_REACH
        lines = VGroup()
        for x in range(x_low, x_high + 1):
            lines.add(Line(self.project((x, y_low, 0)), self.project((x, y_high, 0)), color=Palette.grid_faint, stroke_width=1.2))
        for y in range(y_low, y_high + 1):
            lines.add(Line(self.project((x_low, y, 0)), self.project((x_high, y, 0)), color=Palette.grid_faint, stroke_width=1.2))
        for tip in self.axis_tips():
            lines.add(Line(self.project((0, 0, 0)), self.project(tip), color=Palette.axis, stroke_width=2))
        return lines

    @staticmethod
    def axis_tips():
        return ((FLOOR_REACH[0][1] + 0.4, 0, 0), (0, FLOOR_REACH[1][1] + 0.4, 0), (0, 0, 2.9))

    def axis_labels(self):
        labels = VGroup()
        for name, tip in zip(("x_1", "x_2", "x_3"), self.axis_tips()):
            label = MathTex(name, color=Palette.text_muted, font_size=32)
            label.add_updater(lambda m, tip=tip: m.move_to(self.beyond(tip)))
            labels.add(label)
        return labels

    def beyond(self, tip, gap=0.32):
        end = self.project(tip)
        away = end - self.project((0, 0, 0))
        return end + gap * away / np.linalg.norm(away)

    def patch(self):
        low, high = PATCH_WEIGHTS
        corners = [(low, low), (high, low), (high, high), (low, high)]
        return Polygon(
            *[self.project(s * U3 + t * V3) for s, t in corners],
            fill_color=Palette.teal,
            fill_opacity=0.16,
            stroke_color=Palette.teal,
            stroke_width=1.5,
            stroke_opacity=0.55,
        )

    def box(self, h):
        """The solid built on u, v and w: faint faces with its twelve edges."""
        w = w_vector(h)
        corner = {(a, b, c): a * U3 + b * V3 + c * w for a in (0, 1) for b in (0, 1) for c in (0, 1)}
        faces = VGroup()
        for axis in range(3):
            for side in (0, 1):
                keys = [key for key in corner if key[axis] == side]
                keys = sorted(keys, key=lambda key: np.arctan2(key[(axis + 2) % 3] - 0.5, key[(axis + 1) % 3] - 0.5))
                faces.add(Polygon(*[self.project(corner[key]) for key in keys], fill_color=Palette.purple_gray, fill_opacity=0.1, stroke_width=0))
        edges = VGroup()
        for key in corner:
            for axis in range(3):
                if key[axis] == 0:
                    other = tuple(1 if index == axis else value for index, value in enumerate(key))
                    edges.add(Line(self.project(corner[key]), self.project(corner[other]), color=Palette.purple_gray, stroke_width=2, stroke_opacity=0.75))
        return VGroup(faces, edges)

    def arrow(self, coords, color, start=(0, 0, 0)):
        if np.linalg.norm(np.array(coords) - np.array(start)) < 0.05:
            return VMobject()
        return projected_arrow(self.project, coords, color, start=start, stroke_width=5)

    def drop(self, h):
        if h < 0.06:
            return VMobject()
        return DashedLine(self.project(w_vector(h)), self.project(W_FLOOR), color=Palette.pink, stroke_width=2, stroke_opacity=0.8, dash_length=0.08)


class Lesson(LessonScene):
    day = 13
    title = "Linear independence"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.redundant_third(plane)
        line = self.closed_loop(plane, line)
        line = self.trivial_solution(plane, line)
        line = self.into_space(line)
        line = self.pivot_test(line)
        line = self.flatten(line)
        line = self.space_relation(line)
        line = self.too_many_vectors(line)
        self.close_episode(
            r"Vectors are independent when none of them is redundant.\\"
            r"Then only zero weights combine them to $\mathbf 0$.",
            *self.mobjects,
        )

    def name(self, plane, tex, coords, color, direction):
        return backed(MathTex(tex, color=color, font_size=40), padding=0.1).next_to(plane.c2p(*coords), direction, buff=0.12)

    def redundant_third(self, plane):
        self.v_arrow = vector_arrow(V, Palette.yellow, plane)
        self.w_arrow = vector_arrow(W, Palette.blue, plane)
        self.names = VGroup(
            self.name(plane, r"\mathbf v", V, Palette.yellow, DR),
            self.name(plane, r"\mathbf w", W, Palette.blue, LEFT),
        )
        line = self.say(r"Day 1's $\mathbf v$ and $\mathbf w$ already span the whole plane.", hold=0.2)
        self.play(GrowArrow(self.v_arrow), GrowArrow(self.w_arrow), FadeIn(self.names), run_time=1.3, rate_func=spring_soft)
        self.wait(Timing.read_short)

        self.b_arrow = vector_arrow(B, Palette.pink, plane)
        b_name = self.name(plane, r"\mathbf b", B, Palette.pink, UP)
        self.names.add(b_name)
        line = self.say(r"Now we add a third vector, $\mathbf b$.", line, hold=0.2)
        self.play(GrowArrow(self.b_arrow), FadeIn(b_name), run_time=1.2, rate_func=spring_soft)
        self.wait(Timing.beat)

        line = self.say(r"It equals $2\mathbf v + \mathbf w$, so it adds nothing new.", line, hold=0.2)
        self.double_v = vector_arrow((2 * V[0], 2 * V[1]), Palette.yellow, plane, stroke_width=5)
        self.play(TransformFromCopy(self.v_arrow, self.double_v), self.v_arrow.animate.set_opacity(0.35), run_time=1.4, rate_func=spring)
        self.moved_w = arrow_between(plane, (2 * V[0], 2 * V[1]), B, Palette.blue, stroke_width=5)
        self.play(TransformFromCopy(self.w_arrow, self.moved_w), self.w_arrow.animate.set_opacity(0.35), run_time=1.4, rate_func=spring)
        self.wait(Timing.read_short)
        return line

    def closed_loop(self, plane, line):
        line = self.say(r"Walking back along $-\mathbf b$ returns you to the origin.", line, hold=0.2)
        reversed_b = arrow_between(plane, B, (0, 0), Palette.pink, stroke_width=5)
        self.play(Transform(self.b_arrow, reversed_b), run_time=1.4, rate_func=spring)
        self.walk(lambda: [plane.c2p(*point) for point in chain_points(LOOP_WEIGHTS, (V, W, B))])
        self.wait(Timing.beat)

        self.relation = backed(
            relation_tex([("2", Palette.yellow), (r"\mathbf v", Palette.yellow), ("+", Palette.text), (r"\mathbf w", Palette.blue),
                          ("-", Palette.pink), (r"\mathbf b", Palette.pink), (r"= \mathbf 0", Palette.text)]),
            padding=0.2,
        ).move_to(np.array([PANEL_LEFT, 3.2, 0]), aligned_edge=LEFT)
        line = self.say(r"That loop says $2\mathbf v + \mathbf w - \mathbf b = \mathbf 0$.", line, hold=0.2)
        self.play(Write(self.relation), run_time=1.2)
        self.wait(Timing.read_short)
        return line

    def walk(self, points, run_time=2.4):
        progress = ValueTracker(0)
        dot = walker(lambda: point_on_path(points(), progress.get_value()))
        self.add(dot)
        self.sfx("sweep", gain=-4)
        self.play(progress.animate.set_value(1), run_time=run_time, rate_func=smooth)
        self.play(FadeOut(dot, scale=2), run_time=0.4)

    def trivial_solution(self, plane, line):
        weights = [ValueTracker(value) for value in LOOP_WEIGHTS]
        chain = always_redraw(lambda: chain_arrows(plane, [tracker.get_value() for tracker in weights]))
        self.remove(self.double_v, self.moved_w, self.b_arrow)
        self.add(chain)

        general = backed(
            relation_tex([("c_1", Palette.yellow), (r"\mathbf v", Palette.yellow), ("+", Palette.text), ("c_2", Palette.blue),
                          (r"\mathbf w", Palette.blue), ("+", Palette.text), ("c_3", Palette.pink), (r"\mathbf b", Palette.pink),
                          (r"= \mathbf 0", Palette.text)]),
            padding=0.2,
        ).move_to(self.relation, aligned_edge=LEFT)
        readout = self.weight_readout(weights).next_to(general, DOWN, buff=0.3, aligned_edge=LEFT)
        line = self.say(r"Zero weights always work, and that is the trivial solution.", line, hold=0.2)
        self.play(FadeTransform(self.relation, general), FadeIn(readout), run_time=1.0)
        self.play(*[tracker.animate.set_value(0) for tracker in weights], run_time=1.8, rate_func=spring)
        self.play(Flash(plane.c2p(0, 0), color=Palette.glow, line_length=0.2, flash_radius=0.3), run_time=0.6)
        self.wait(Timing.beat)

        line = self.say(r"Vectors are independent when that is the only solution.", line, hold=Timing.read_short)
        line = self.say(r"These three are dependent, because other weights also work.", line, hold=0.2)
        self.play(*[tracker.animate.set_value(value) for tracker, value in zip(weights, LOOP_WEIGHTS)], run_time=1.8, rate_func=spring)
        self.walk(lambda: [plane.c2p(*point) for point in chain_points(LOOP_WEIGHTS, (V, W, B))], run_time=2.0)
        self.wait(Timing.beat)
        self.play(FadeOut(VGroup(plane, chain, self.v_arrow, self.w_arrow, self.names, general, readout)), run_time=0.8)
        return line

    @staticmethod
    def weight_readout(weights):
        rows = VGroup()
        for index, (tracker, color) in enumerate(zip(weights, COLUMN_COLORS)):
            label = MathTex(f"c_{index + 1} =", color=color, font_size=38)
            number = DecimalNumber(tracker.get_value(), num_decimal_places=1, include_sign=True, color=color, font_size=38)
            number.next_to(label, RIGHT, buff=0.15)
            number.add_updater(lambda m, tracker=tracker, label=label: m.set_value(tracker.get_value()).next_to(label, RIGHT, buff=0.15))
            rows.add(VGroup(label, number))
        rows.arrange(RIGHT, buff=0.55)
        return backed(rows, padding=0.18)

    def into_space(self, line):
        self.view = View()
        self.h = ValueTracker(H_START)
        view = self.view
        floor = always_redraw(view.floor_and_axes)
        labels = view.axis_labels()
        line = self.say(r"In space, $\mathbf u$ and $\mathbf v$ span a flat plane.", line, hold=0.2)
        still_floor = view.floor_and_axes()
        self.play(Create(still_floor), FadeIn(labels), run_time=1.6)
        self.remove(still_floor)
        self.add(floor)
        self.bring_to_back(floor)

        self.grow_live(view.arrow(U3, Palette.yellow), lambda: view.arrow(U3, Palette.yellow))
        self.grow_live(view.arrow(V3, Palette.blue), lambda: view.arrow(V3, Palette.blue))
        patch = always_redraw(view.patch)
        still_patch = view.patch()
        self.play(FadeIn(still_patch), run_time=1.0)
        self.remove(still_patch)
        self.add(patch)
        self.bring_to_back(patch)
        self.bring_to_back(floor)
        self.space_names = self.live_names()
        self.play(FadeIn(self.space_names[:3]), run_time=0.6)
        self.wait(Timing.beat)

        line = self.say(r"A third vector $\mathbf w$ rises above that plane.", line, hold=0.2)
        self.grow_live(view.arrow(w_vector(H_START), Palette.pink), lambda: view.arrow(w_vector(self.h.get_value()), Palette.pink))
        drop = always_redraw(lambda: view.drop(self.h.get_value()))
        still_drop = view.drop(H_START)
        self.play(Create(still_drop), FadeIn(self.space_names[3]), run_time=0.8)
        self.remove(still_drop)
        self.add(drop)
        self.wait(Timing.beat)

        line = self.say(r"Together the three arrows build a box with real volume.", line, hold=0.2)
        box = always_redraw(lambda: view.box(self.h.get_value()))
        self.volume = self.volume_readout()
        still_box = view.box(H_START)
        self.play(FadeIn(still_box), FadeIn(self.volume), run_time=1.2)
        self.remove(still_box)
        self.add(box)
        self.bring_to_back(box)
        self.bring_to_back(patch)
        self.bring_to_back(floor)
        view.azimuth.add_updater(lambda m, dt: m.increment_value(DRIFT_PER_SECOND * dt))
        self.add(view.azimuth)
        self.wait(Timing.read_short)
        return line

    def grow_live(self, still, redraw):
        """Grow a still arrow, then hand over to a live copy that follows the view and the trackers."""
        self.play(GrowArrow(still), run_time=1.1, rate_func=spring_soft)
        self.remove(still)
        self.add(always_redraw(redraw))

    def live_names(self):
        view = self.view
        specs = (
            (r"\mathbf u", Palette.yellow, lambda: U3, LEFT),
            (r"\mathbf v", Palette.blue, lambda: V3, RIGHT),
            (r"\operatorname{Span}\{\mathbf u, \mathbf v\}", Palette.teal, lambda: 2.15 * U3 + 2.15 * V3, DOWN),
            (r"\mathbf w", Palette.pink, lambda: w_vector(self.h.get_value()), None),
        )
        names = VGroup()
        for tex, color, where, direction in specs:
            label = backed(MathTex(tex, color=color, font_size=36), padding=0.08)
            label.add_updater(lambda m, where=where, direction=direction: m.next_to(view.project(where()), self.w_side() if direction is None else direction, buff=0.15))
            names.add(label)
        return names

    def w_side(self):
        return UP if self.h.get_value() > 0.6 else DR

    def volume_readout(self):
        word = Tex("volume", color=Palette.purple_gray, font_size=38)
        formula = MathTex(rf"= {BASE_AREA}h =", color=Palette.purple_gray, font_size=38)
        number = DecimalNumber(BASE_AREA * H_START, num_decimal_places=1, color=Palette.purple_gray, font_size=38)
        group = VGroup(word, formula, number).arrange(RIGHT, buff=0.18)
        group.move_to(np.array([6.8, 3.4, 0]), aligned_edge=RIGHT)
        number.add_updater(lambda m: m.set_value(BASE_AREA * self.h.get_value()).next_to(formula, RIGHT, buff=0.18))
        return group

    def pivot_test(self, line):
        header = relation_tex([("x_1", Palette.yellow), (r"\mathbf u", Palette.yellow), ("+", Palette.text), ("x_2", Palette.blue),
                               (r"\mathbf v", Palette.blue), ("+", Palette.text), ("x_3", Palette.pink), (r"\mathbf w", Palette.pink),
                               (r"= \mathbf 0", Palette.text)], font_size=38)
        header.move_to(np.array([PANEL_LEFT, 3.3, 0]), aligned_edge=LEFT)
        self.mat = column_matrix([[1, 1, 2, 0], [-1, 2, 1, 0], [0, 0, 2, 0]])
        self.mat.next_to(header, DOWN, buff=0.45).align_to(header, LEFT)
        line = self.say(r"Row reduce the matrix whose columns are $\mathbf u$, $\mathbf v$ and $\mathbf w$.", line, hold=0.2)
        self.play(Write(header), run_time=1.0)
        self.play(FadeIn(self.mat, shift=RIGHT * 0.2), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.beat)

        reduced = column_matrix([[1, 0, 1, 0], [0, 1, 1, 0], [0, 0, 2, 0]]).move_to(self.mat)
        line = self.say(r"Every column has a pivot, so no variable is free.", line, hold=0.2)
        morph_matrix(self, self.mat, reduced, run_time=1.4)
        rows = self.mat.get_rows()
        self.pivots = VGroup(pivot_box(rows[0][0]), pivot_box(rows[1][1]))
        still_third = pivot_box(rows[2][2])
        self.play(LaggedStart(*[Create(box) for box in self.pivots], Create(still_third), lag_ratio=0.3), run_time=1.2)
        self.remove(still_third)
        self.h_entry = rows[2][2]
        self.third_pivot = always_redraw(lambda: pivot_box(self.h_entry, opacity=min(1.0, self.h.get_value() / 0.6)))
        self.add(self.third_pivot)
        self.header = header
        self.wait(Timing.beat)
        line = self.say(r"The only solution is zero, so they are independent.", line, hold=Timing.read_short)
        return line

    def flatten(self, line):
        entry = self.mat.get_rows()[2][2]
        live_entry = DecimalNumber(H_START, num_decimal_places=1, color=Palette.pink, font_size=48)
        live_entry.move_to(entry)
        live_entry.add_updater(lambda m: m.set_value(self.h.get_value()).move_to(entry))
        entry.set_opacity(0)
        self.add(live_entry)
        self.h_entry = live_entry
        line = self.say(r"Watch the box as $\mathbf w$ drops toward the plane.", line, hold=0.2)
        self.sfx("slide", gain=-2)
        self.play(self.h.animate.set_value(0), run_time=5.0, rate_func=spring_soft)
        zero = MathTex("0", color=Palette.pink).move_to(entry)
        self.play(FadeOut(live_entry), FadeIn(zero), run_time=0.4)
        self.zero_entry = zero
        line = self.say(r"At $h = 0$ the box is flat and the pivot vanishes.", line, hold=Timing.read_short)
        return line

    def space_relation(self, line):
        free = MathTex(r"x_1 = -x_3,\quad x_2 = -x_3,\quad x_3 \text{ free}", color=Palette.text, font_size=36)
        free.next_to(self.mat, DOWN, buff=0.45).align_to(self.mat, LEFT)
        line = self.say(r"Column three is free, so a nonzero solution appears.", line, hold=0.2)
        self.play(Write(free), run_time=1.2)
        self.wait(Timing.read_short)

        view = self.view
        relation = relation_tex([(r"\mathbf u", Palette.yellow), ("+", Palette.text), (r"\mathbf v", Palette.blue), ("-", Palette.pink),
                                 (r"\mathbf w", Palette.pink), (r"= \mathbf 0", Palette.text)], font_size=40)
        relation.next_to(free, DOWN, buff=0.4).align_to(free, LEFT)
        choice = MathTex(r"x_3 = -1:", color=Palette.text_muted, font_size=36).next_to(relation, LEFT, buff=0.25)
        VGroup(choice, relation).align_to(free, LEFT)
        line = self.say(r"It reads $\mathbf u + \mathbf v - \mathbf w = \mathbf 0$, so $\mathbf w$ is redundant.", line, hold=0.2)
        self.grow_live(view.arrow(W_FLOOR, Palette.blue, start=U3), lambda: view.arrow(W_FLOOR, Palette.blue, start=U3))
        self.play(Write(choice), Write(relation), run_time=1.2)
        self.walk(lambda: [view.project(point) for point in (np.zeros(3), U3, W_FLOOR, np.zeros(3))], run_time=2.4)
        self.wait(Timing.read_short)
        return line

    def too_many_vectors(self, line):
        self.view.azimuth.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects if m is not line], run_time=0.8)
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        weights = LOOP_WEIGHTS
        arrows = VGroup(vector_arrow(V, Palette.yellow, plane).set_opacity(0.35), vector_arrow(W, Palette.blue, plane).set_opacity(0.35))
        names = VGroup(
            self.name(plane, r"\mathbf v", V, Palette.yellow, DR),
            self.name(plane, r"\mathbf w", W, Palette.blue, LEFT),
            self.name(plane, r"\mathbf b", B, Palette.pink, UP),
        )
        line = self.say(r"Back in the plane, $[\,\mathbf v\ \mathbf w\ \mathbf b\,]$ has only two rows.", line, hold=0.2)
        self.play(FadeIn(plane), FadeIn(arrows), FadeIn(chain_arrows(plane, weights)), FadeIn(names), run_time=1.0)

        mat = plain_columns([[3, -1, 5], [2, 2, 6]])
        plate = plate_for(mat, padding=0.3)
        panel = VGroup(plate, mat).move_to(np.array([PANEL_LEFT, 2.7, 0]), aligned_edge=LEFT)
        self.play(FadeIn(plate), FadeIn(mat, shift=RIGHT * 0.2), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.beat)

        reduced = plain_columns([[1, 0, 2], [0, 1, 1]]).move_to(mat)
        line = self.say(r"Two rows hold two pivots, so one column is always free.", line, hold=0.2)
        morph_matrix(self, mat, reduced, run_time=1.4)
        rows = mat.get_rows()
        self.play(LaggedStart(Create(pivot_box(rows[0][0])), Create(pivot_box(rows[1][1])), lag_ratio=0.3), run_time=1.0)
        free_label = MathTex(r"x_3 \text{ free}", color=Palette.pink, font_size=34).next_to(panel, DOWN, buff=0.2)
        free_label.set_x(mat.get_columns()[2].get_x())
        self.play(Indicate(mat.get_columns()[2], color=Palette.glow, scale_factor=1.15), FadeIn(backed(free_label, padding=0.1)), run_time=1.0)
        self.wait(Timing.beat)
        line = self.say(r"More vectors than entries always makes a set dependent.", line, hold=Timing.read_long)
        return line


def space_figure(scene, view, h, loop=False, w_side=UP):
    """Axes, the span patch, u, v, w and the box at height h, all seen through `view`."""
    labels = view.axis_labels()
    labels.update()
    labels.clear_updaters()
    scene.add(view.floor_and_axes(), labels, view.patch(), view.box(h))
    scene.add(view.arrow(U3, Palette.yellow), view.arrow(V3, Palette.blue), view.arrow(w_vector(h), Palette.pink), view.drop(h))
    if loop:
        scene.add(view.arrow(W_FLOOR, Palette.blue, start=U3))
    names = VGroup(
        backed(MathTex(r"\mathbf u", color=Palette.yellow, font_size=36), padding=0.08).next_to(view.project(U3), LEFT, buff=0.15),
        backed(MathTex(r"\mathbf v", color=Palette.blue, font_size=36), padding=0.08).next_to(view.project(V3), RIGHT, buff=0.15),
        backed(MathTex(r"\mathbf w", color=Palette.pink, font_size=36), padding=0.08).next_to(view.project(w_vector(h)), w_side, buff=0.15),
    )
    scene.add(names)
    return names


class FigClosedLoop(Scene):
    def construct(self):
        plane = make_plane_window()
        self.add(plane, vector_arrow(V, Palette.yellow, plane).set_opacity(0.35), vector_arrow(W, Palette.blue, plane).set_opacity(0.35))
        self.add(chain_arrows(plane, LOOP_WEIGHTS))
        self.add(
            backed(MathTex(r"2\mathbf v", color=Palette.yellow, font_size=40), padding=0.08).next_to(plane.c2p(5, 3.3), DR, buff=0.05),
            backed(MathTex(r"\mathbf w", color=Palette.blue, font_size=40), padding=0.08).next_to(plane.c2p(5.5, 5), RIGHT, buff=0.12),
            backed(MathTex(r"-\mathbf b", color=Palette.pink, font_size=40), padding=0.08).next_to(plane.c2p(2.5, 3), UL, buff=0.1),
            backed(MathTex(r"\mathbf v", color=Palette.yellow, font_size=36), padding=0.08).next_to(plane.c2p(*V), DR, buff=0.05),
            backed(MathTex(r"\mathbf w", color=Palette.blue, font_size=36), padding=0.08).next_to(plane.c2p(*W), LEFT, buff=0.1),
        )
        fit_to_frame(self)


def make_plane_window():
    from engine.theme import make_plane

    return make_plane(x_range=(-2, 7, 1), y_range=(-1, 7, 1))


class FigFlatBox(Scene):
    def construct(self):
        lifted = View(origin=(-3.6, 0.0), unit=0.8, azimuth=34 * DEGREES)
        flat = View(origin=(3.6, 0.0), unit=0.8, azimuth=34 * DEGREES)
        space_figure(self, lifted, H_START)
        space_figure(self, flat, 0.0, loop=True, w_side=DR)
        notes = VGroup(
            MathTex(r"h = 2:\ \text{independent}", color=Palette.text_muted, font_size=40).move_to(np.array([-3.6, -3.0, 0])),
            relation_tex([(r"h = 0:\ ", Palette.text_muted), (r"\mathbf u", Palette.yellow), ("+", Palette.text), (r"\mathbf v", Palette.blue),
                          ("-", Palette.pink), (r"\mathbf w", Palette.pink), (r"= \mathbf 0", Palette.text)]).move_to(np.array([3.6, -3.0, 0])),
        )
        self.add(notes)
        fit_to_frame(self)


class FigPivotColumns(Scene):
    def construct(self):
        independent = column_matrix([[1, 0, 1, 0], [0, 1, 1, 0], [0, 0, 2, 0]])
        dependent = column_matrix([[1, 0, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]])
        wide = plain_columns([[1, 0, 2], [0, 1, 1]])
        panels = VGroup()
        for mat, pivots, heading in (
            (independent, 3, r"h = 2"),
            (dependent, 2, r"h = 0"),
            (wide, 2, r"[\,\mathbf v\ \mathbf w\ \mathbf b\,]"),
        ):
            boxes = VGroup(*[pivot_box(mat.get_rows()[index][index]) for index in range(pivots)])
            title = MathTex(heading, color=Palette.text_muted, font_size=40).next_to(mat, UP, buff=0.4)
            panels.add(VGroup(title, mat, boxes))
        VGroup(panels[0], panels[1]).arrange(RIGHT, buff=1.0, aligned_edge=DOWN)
        panels[2].next_to(VGroup(panels[0], panels[1]), DOWN, buff=0.8)
        self.add(panels)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        view = View(origin=(0.6, 0.2), unit=1.25, azimuth=38 * DEGREES)
        self.add(view.box(0.0)[1].set_stroke(Palette.teal, width=2, opacity=0.45))
        space_figure(self, view, H_START, w_side=UR)
        fit_to_frame(self, margin=0.5)
