import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    LiveMatrix,
    Palette,
    Timing,
    backed,
    fit_to_frame,
    live_basis_arrows,
    clip_to_box,
    make_plane,
    matrix,
    orientation_arc,
    plane_at,
    signed_area,
    signed_parallelogram,
    skewed_grid,
    spring,
    spring_soft,
    vector_arrow,
)

PLANE_ORIGIN = (-6.1, -1.2)
PLANE_UNIT = 1.45
PANEL_LEFT = 1.45
PANEL_X = 4.3

A = ((3, 1), (1, 2))
FIRST, SECOND = (3, 1), (1, 2)
SWING_RADIUS = math.sqrt(5)
SWING_START = math.atan2(2, 1)
SWING_FLAT = math.atan2(1, 3)
SWING_END = math.atan2(-1, 2)
SWAP = ((0, 1), (1, 0))
COPY_CELLS = ((-1, 0), (-1, 1), (0, 1), (1, -1))

LETTER_COLORS = {"a": Palette.i_hat, "c": Palette.i_hat, "b": Palette.j_hat, "d": Palette.j_hat}

AC_TRIANGLES = (((0, 0), (3, 0), (3, 1)), ((1, 2), (1, 3), (4, 3)))
BD_TRIANGLES = (((3, 1), (4, 1), (4, 3)), ((0, 0), (0, 2), (1, 2)))
BC_RECTANGLES = (((3, 0), (4, 0), (4, 1), (3, 1)), ((0, 2), (1, 2), (1, 3), (0, 3)))

# Side lengths along the bounding box: (letter, midpoint in plane coords, direction to push the label out).
BOX_SIDES = (
    ("a", (1.5, 0), DOWN),
    ("b", (3.5, 0), DOWN),
    ("c", (4, 0.5), RIGHT),
    ("d", (4, 2), RIGHT),
    ("b", (0.5, 3), UP),
    ("a", (2.5, 3), UP),
    ("d", (0, 1), LEFT),
    ("c", (0, 2.5), LEFT),
)
BOX_TICKS = (((3, 0), DOWN), ((4, 1), RIGHT), ((1, 3), UP), ((0, 2), LEFT))


def lettered(*parts, font_size=40):
    """MathTex split into parts, with each lone letter a, b, c, d painted in its column's color."""
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, text in zip(formula, parts):
        if text in LETTER_COLORS:
            part.set_color(LETTER_COLORS[text])
    return formula


def tex(*parts, colors=(), font_size=40):
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def column_colored(rows, scale=0.85):
    mat = matrix(rows).scale(scale)
    for col, color in zip(mat.get_columns(), (Palette.i_hat, Palette.j_hat)):
        col.set_color(color)
    return mat


def side_panel():
    panel = Rectangle(
        width=config.frame_width / 2 - PANEL_LEFT + 0.2,
        height=config.frame_height + 0.2,
        fill_color=Palette.background,
        fill_opacity=0.94,
        stroke_width=0,
    )
    return panel.move_to(np.array([PANEL_LEFT + panel.width / 2, 0, 0])).set_z_index(5)


def on_panel(mobject, y, x=PANEL_X):
    return mobject.move_to(np.array([x, y, 0])).set_z_index(6)


def piece(plane, corners, color=Palette.purple_gray, opacity=0.55):
    return Polygon(*[plane.c2p(*corner) for corner in corners], color=color, fill_opacity=opacity, stroke_width=2, stroke_opacity=0.9)


def bounding_box(plane):
    outline = Polygon(*[plane.c2p(*corner) for corner in ((0, 0), (4, 0), (4, 3), (0, 3))], color=Palette.text_muted, stroke_width=3)
    return DashedVMobject(outline, num_dashes=56)


def side_labels(plane, font_size=40):
    labels = VGroup()
    for letter, point, direction in BOX_SIDES:
        label = MathTex(letter, color=LETTER_COLORS[letter], font_size=font_size)
        labels.add(backed(label, padding=0.06).next_to(plane.c2p(*point), direction, buff=0.14))
    for point, direction in BOX_TICKS:
        center = plane.c2p(*point)
        labels.add(Line(center, center + direction * 0.22, color=Palette.text_muted, stroke_width=3))
    return labels


def flatness(first, second):
    """1 when the columns lie on one line, falling to 0 once |det| reaches 0.9."""
    return max(0.0, 1.0 - abs(signed_area(first, second)) / 0.9)


def fading_grid(plane, first, second):
    """The moved grid, thinning out as it nears a single line so the squash reads without a wall of lines."""
    opacity = 0.55 * (1 - flatness(first, second))
    if opacity < 0.02:
        return VMobject()
    return skewed_grid(plane, first, second, reach=20, color=Palette.blue, opacity=opacity)


def collapse_line(plane, first, second):
    """The line through the first column, brightening as the whole grid falls onto it."""
    strength = flatness(first, second)
    if strength < 0.02:
        return VMobject()
    direction = np.array(first, dtype=float) * 40
    ends = clip_to_box(-direction, direction, tuple(plane.x_range[:2]), tuple(plane.y_range[:2]))
    return Line(plane.c2p(*ends[0]), plane.c2p(*ends[1]), color=Palette.blue, stroke_width=5, stroke_opacity=strength)


def strike(mobject):
    return Line(mobject.get_corner(DL) + LEFT * 0.04, mobject.get_corner(UR) + RIGHT * 0.04, color=Palette.glow, stroke_width=3)


def number_label(text, plane, point, font_size=48):
    return backed(MathTex(text, color=Palette.text, font_size=font_size), padding=0.1).move_to(plane.c2p(*point))


def grid_copy(plane, cell):
    corner = (3 * cell[0] + cell[1], cell[0] + 2 * cell[1])
    return signed_parallelogram(plane, FIRST, SECOND, opacity=0.12, stroke_width=2, offset=corner)


class Lesson(LessonScene):
    day = 25
    title = "The determinant measures area"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        self.plane = plane
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.unit_square()
        line = self.apply_a(line)
        line = self.box_argument(line)
        line = self.name_determinant(line)
        line = self.copies(line)
        line = self.swing_to_flat(line)
        line = self.swing_past(line)
        line = self.mirror(line)
        self.close_episode(
            r"The determinant is the factor by which $A$ scales area.\\"
            r"Its sign says whether $A$ turns the plane over.",
            *self.mobjects,
        )

    def adopt(self, group):
        """Make `group` the only top-level owner of its parts, so fading it later removes all of them."""
        self.remove(*group.get_family())
        group.z_index = max(part.z_index for part in group.get_family())
        self.add(group)

    def live_pictures(self):
        plane, live = self.plane, self.live
        self.grid = VGroup(
            always_redraw(lambda: fading_grid(plane, live.column(0), live.column(1))),
            always_redraw(lambda: collapse_line(plane, live.column(0), live.column(1))),
        )
        self.shape = always_redraw(lambda: signed_parallelogram(plane, live.column(0), live.column(1)))
        self.arrows = live_basis_arrows(plane, live)

    def unit_square(self):
        self.live = LiveMatrix()
        self.live_pictures()
        line = self.say(r"On Day 7, $ad - bc$ decided whether a matrix is invertible.", hold=0.2)
        self.play(self.plane.animate.set_opacity(0.3), FadeIn(self.grid), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"Today we find out what that number measures.", line, hold=0.2)
        self.play(FadeIn(self.shape), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"The unit square has area 1.", line, hold=0.2)
        self.play(GrowArrow(self.arrows[0]), GrowArrow(self.arrows[1]), run_time=1.0, rate_func=spring_soft)
        self.one = number_label("1", self.plane, (0.5, 0.5), font_size=44)
        self.play(FadeIn(self.one, scale=0.8), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_short)
        return line

    def apply_a(self, line):
        self.panel = side_panel()
        self.a_name = MathTex("A", "=", color=Palette.text, font_size=44)
        self.a_numbers = column_colored([["3", "1"], ["1", "2"]])
        on_panel(VGroup(self.a_name, self.a_numbers).arrange(RIGHT, buff=0.2), 2.7)
        line = self.say(r"Here is a matrix $A$.", line, hold=0.2)
        self.play(FadeIn(self.panel), FadeIn(self.a_name), FadeIn(self.a_numbers, shift=LEFT * 0.2), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.beat)
        line = self.say(r"$A$ carries the square onto a parallelogram.", line, hold=0.2)
        self.play(FadeOut(self.one), run_time=0.3)
        self.play(*self.live.move_to(A), run_time=2.6, rate_func=smooth)
        self.wait(Timing.beat)

        line = self.say(r"Its sides are the two columns of $A$.", line, hold=0.2)
        for index in range(2):
            color = (Palette.i_hat, Palette.j_hat)[index]
            glow = vector_arrow(self.live.column(index), color, self.plane, stroke_width=10)
            self.play(Indicate(self.a_numbers.get_columns()[index], color=Palette.glow, scale_factor=1.15), FadeIn(glow), run_time=0.9)
            self.play(FadeOut(glow), run_time=0.4)
        self.wait(Timing.beat)
        return line

    def show_letters(self):
        letters = matrix([["a", "b"], ["c", "d"]]).scale(0.85)
        for col, color in zip(letters.get_columns(), (Palette.i_hat, Palette.j_hat)):
            col.set_color(color)
        equals = MathTex("=", color=Palette.text, font_size=44)
        target = VGroup(self.a_name.copy(), letters, equals, self.a_numbers.copy()).arrange(RIGHT, buff=0.2)
        on_panel(target, 2.7)
        self.play(
            self.a_name.animate.move_to(target[0]),
            self.a_numbers.animate.move_to(target[3]),
            FadeIn(letters, shift=RIGHT * 0.2),
            FadeIn(equals),
            run_time=0.9,
            rate_func=spring_soft,
        )
        self.a_row = VGroup(self.a_name, letters, equals, self.a_numbers)
        self.adopt(self.a_row)

    def box_argument(self, line):
        plane = self.plane
        self.play(FadeOut(self.grid), run_time=0.6)
        line = self.say(r"Now find its area using only $a$, $b$, $c$ and $d$.", line, hold=0.2)
        self.show_letters()
        box, sides = bounding_box(plane), side_labels(plane)
        line = self.say(r"Put a box around it, $a+b$ wide and $c+d$ tall.", line, hold=0.2)
        self.play(Create(box), run_time=1.2)
        self.play(FadeIn(sides, lag_ratio=0.15), run_time=1.4)
        first = on_panel(lettered(r"\text{area}", "=", "(", "a", "+", "b", ")", "(", "c", "+", "d", ")"), 1.3)
        first.align_to(np.array([PANEL_LEFT + 0.5, 0, 0]), LEFT)
        self.play(FadeIn(first, shift=DOWN * 0.15), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)

        steps = (
            (r"Cut away two triangles of area $\tfrac12 ac$.", AC_TRIANGLES, ("-", "a", "c")),
            (r"Two more triangles have area $\tfrac12 bd$.", BD_TRIANGLES, ("-", "b", "d")),
            (r"Two rectangles have area $bc$ each.", BC_RECTANGLES, ("-", "2", "b", "c")),
        )
        terms, pieces = VGroup(), VGroup()
        anchor = first[2].get_left()
        for caption_text, shapes, term_parts in steps:
            line = self.say(caption_text, line, hold=0.2)
            pair = VGroup(*[piece(plane, corners) for corners in shapes]).set_z_index(-1)
            term = lettered(*term_parts).set_z_index(6)
            if len(terms):
                term.next_to(terms, RIGHT, buff=0.22)
            else:
                term.move_to(np.array([anchor[0], 0.45, 0]), aligned_edge=LEFT)
            self.play(FadeIn(pair, lag_ratio=0.4), run_time=1.0)
            self.play(FadeIn(term, shift=LEFT * 0.2), run_time=0.7, rate_func=spring_soft)
            terms.add(term)
            pieces.add(pair)
            self.wait(Timing.beat)
        return self.cancel_terms(line, first, terms, pieces, box, sides)

    def cancel_terms(self, line, first, terms, pieces, box, sides):
        expanded = lettered("(", "a", "+", "b", ")", "(", "c", "+", "d", ")", "=", "a", "c", "+", "a", "d", "+", "b", "c", "+", "b", "d", font_size=32)
        on_panel(expanded, -0.45).align_to(np.array([PANEL_LEFT + 0.25, 0, 0]), LEFT)
        result = lettered(r"\text{area}", "=", "a", "d", "-", "b", "c", font_size=44)
        on_panel(result, -1.5).align_to(first, LEFT)
        line = self.say(r"Expand the box and almost everything cancels.", line, hold=0.2)
        self.play(FadeIn(expanded, shift=DOWN * 0.15), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.beat)
        cancelled = (expanded[11:13], expanded[17:19], expanded[20:22], terms[0][1:3], terms[1][1:3], terms[2][1])
        crossed = VGroup(*[strike(part) for part in cancelled]).set_z_index(7)
        self.play(Create(crossed, lag_ratio=0.3), run_time=1.4)
        self.play(FadeIn(result, shift=UP * 0.15), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_short)
        self.play(FadeOut(VGroup(first, terms, expanded, crossed)), FadeOut(pieces), FadeOut(box), FadeOut(sides), run_time=0.7)
        self.result = result
        return line

    def name_determinant(self, line):
        named = lettered(r"\det A", "=", "a", "d", "-", "b", "c", font_size=44)
        on_panel(named, 1.1).align_to(np.array([PANEL_LEFT + 0.5, 0, 0]), LEFT)
        numbers = tex("=", "3", r"\cdot", "2", "-", "1", r"\cdot", "1", "=", "5", colors=(None, Palette.i_hat, None, Palette.j_hat, None, Palette.j_hat, None, Palette.i_hat), font_size=44)
        on_panel(numbers, 0.1).align_to(named[1], LEFT)
        line = self.say(r"That leftover number is the determinant of $A$.", line, hold=0.2)
        self.play(FadeTransform(self.result, named), run_time=1.0)
        self.wait(Timing.beat)
        line = self.say(r"For our $A$, it is $3\cdot 2 - 1\cdot 1 = 5$.", line, hold=0.2)
        self.play(FadeIn(numbers[:8], shift=DOWN * 0.15), run_time=0.9, rate_func=spring_soft)
        self.play(FadeIn(numbers[8:], shift=LEFT * 0.2), run_time=0.7, rate_func=spring)
        self.five = number_label("5", self.plane, (2, 1.5), font_size=52).set_z_index(6)
        self.play(FadeIn(self.five.background_rectangle), TransformFromCopy(numbers[9], self.five[1]), run_time=1.1, rate_func=spring)
        self.remove(self.five[1], self.five.background_rectangle)
        self.add(self.five)
        self.wait(Timing.read_short)
        self.det_lines = VGroup(named, numbers)
        self.adopt(self.det_lines)
        return line

    def copies(self, line):
        copies = VGroup(*[grid_copy(self.plane, cell) for cell in COPY_CELLS])
        self.add(self.grid)
        self.bring_to_front(self.shape, self.arrows, self.five)
        line = self.say(r"Every grid square lands on a copy of this parallelogram.", line, hold=0.2)
        self.play(FadeIn(self.grid), run_time=0.8)
        self.add(copies)
        self.bring_to_front(self.shape, self.arrows, self.five)
        self.play(LaggedStart(*[FadeIn(copy) for copy in copies], lag_ratio=0.35), run_time=2.0)
        self.wait(Timing.beat)
        line = self.say(r"So $A$ multiplies every area by 5.", line, hold=Timing.read_short)
        self.play(FadeOut(copies), FadeOut(self.five), run_time=0.6)
        return line

    def live_panel(self):
        template = column_colored([["-0.0", "-0.0"], ["-0.0", "-0.0"]])
        name = MathTex("A", "=", color=Palette.text, font_size=44)
        row = on_panel(VGroup(name, template).arrange(RIGHT, buff=0.2), 2.2)
        entries = VGroup()
        colors = (Palette.i_hat, Palette.j_hat)
        for index, slot in enumerate(template.get_entries()):
            number = DecimalNumber(0, num_decimal_places=1, color=colors[index % 2], font_size=44).scale(0.85).set_z_index(6)
            number.add_updater(lambda m, i=index, c=slot.get_center(): m.set_value(self.live.value()[i // 2, i % 2]).move_to(c).set_z_index(6))
            entries.add(number)
        det_name = MathTex(r"\det A", "=", color=Palette.text, font_size=56)
        counter = DecimalNumber(0, num_decimal_places=1, color=Palette.yellow, font_size=56).set_z_index(6)
        det_row = on_panel(VGroup(det_name, counter).arrange(RIGHT, buff=0.25), 0.2)
        spot = counter.get_left()
        counter.add_updater(lambda m: self.update_counter(m, spot))
        return VGroup(row[0], template.get_brackets(), entries, det_row)

    def current_det(self):
        value = signed_area(self.live.column(0), self.live.column(1))
        return 0.0 if abs(value) < 0.005 else value

    def update_counter(self, counter, spot):
        value = self.current_det()
        counter.set_value(value)
        counter.set_color(Palette.pink if value < 0 else Palette.yellow)
        counter.move_to(spot, aligned_edge=LEFT).set_z_index(6)

    def swing(self, start, end, run_time):
        tracker = self.live.trackers

        def set_angle(_, alpha):
            angle = start + (end - start) * alpha
            tracker[0][1].set_value(SWING_RADIUS * math.cos(angle))
            tracker[1][1].set_value(SWING_RADIUS * math.sin(angle))

        self.sfx("slide", gain=-2)
        self.play(UpdateFromAlphaFunc(tracker[0][1], set_angle), run_time=run_time, rate_func=smooth)

    def swing_to_flat(self, line):
        plane, live = self.plane, self.live
        self.play(FadeOut(self.det_lines), FadeOut(self.a_row), run_time=0.6)
        readouts = self.live_panel()
        self.arc = always_redraw(lambda: orientation_arc(plane, live.column(0), live.column(1), radius=1.0))
        line = self.say(r"Swing the red column down toward the green one.", line, hold=0.2)
        self.play(FadeIn(readouts), run_time=0.7)
        self.sfx("tick", gain=-4)
        self.play(FadeIn(self.arc), run_time=0.6)
        self.readouts = readouts
        self.wait(Timing.beat)
        self.swing(SWING_START, SWING_FLAT, run_time=4.5)
        line = self.say(r"At $\det A = 0$ the parallelogram is flat.", line, hold=Timing.read_short)
        line = self.say(r"The whole plane is squashed onto one line.", line, hold=0.2)
        self.play(Indicate(self.grid, color=Palette.glow, scale_factor=1.0), run_time=1.2)
        self.wait(Timing.beat)
        line = self.say(r"Flat means no inverse, as on Day 7.", line, hold=Timing.read_short)
        line = self.say(r"Day 29 finds eigenvalues by hunting for this flatness.", line, hold=Timing.read_short)
        return line

    def swing_past(self, line):
        line = self.say(r"Past the line, the determinant turns negative.", line, hold=0.2)
        self.swing(SWING_FLAT, SWING_END, run_time=4.5)
        self.wait(Timing.beat)
        line = self.say(r"The turn from green to red is now clockwise.", line, hold=0.2)
        self.play(Indicate(self.arc, color=Palette.text, scale_factor=1.25), run_time=1.0)
        self.wait(Timing.beat)
        line = self.say(r"The plane has been flipped over, like a mirror image.", line, hold=Timing.read_short)
        line = self.say(r"Its area is $|\det A| = 5$, and the sign records the flip.", line, hold=Timing.read_long)
        return line

    def mirror(self, line):
        live = self.live
        self.play(FadeOut(self.shape), FadeOut(self.arrows), FadeOut(self.arc), FadeOut(self.grid), run_time=0.6)
        for tracker, value in zip([t for row in live.trackers for t in row], (1, 0, 0, 1)):
            tracker.set_value(value)
        for drawing in (self.grid, self.shape, *self.arrows, self.arc):
            drawing.update()
        line = self.say(r"Swapping the columns mirrors the plane across $y = x$.", line, hold=0.2)
        self.play(FadeIn(self.grid), FadeIn(self.shape), FadeIn(self.arrows), FadeIn(self.arc), run_time=0.8)
        self.wait(Timing.beat)
        self.play(*live.move_to(SWAP), run_time=4.0, rate_func=smooth)
        self.wait(Timing.beat)
        line = self.say(r"A mirror keeps area and flips the plane, so $\det = -1$.", line, hold=Timing.read_long)
        self.play(FadeOut(line), run_time=0.4)
        for number in self.readouts.get_family():
            number.clear_updaters()
        return None


def figure_plane(x_range, y_range):
    return make_plane(x_range=(*x_range, 1), y_range=(*y_range, 1))


class FigBox(Scene):
    def construct(self):
        plane = figure_plane((-1, 5), (-1, 4))
        pieces = VGroup(*[piece(plane, corners) for corners in AC_TRIANGLES + BD_TRIANGLES + BC_RECTANGLES])
        shape = signed_parallelogram(plane, FIRST, SECOND, opacity=0.38)
        arrows = VGroup(vector_arrow(FIRST, Palette.i_hat, plane), vector_arrow(SECOND, Palette.j_hat, plane))
        self.add(plane, pieces, shape, bounding_box(plane), arrows, side_labels(plane, font_size=44))
        fit_to_frame(self)


class FigShear(Scene):
    def construct(self):
        plane = figure_plane((-1, 6), (-1, 3))
        base, slanted, upright = (3, 0), (2, 2), (0, 2)
        guide = DashedLine(plane.c2p(-1, 2), plane.c2p(6, 2), color=Palette.text_muted, stroke_width=3)
        rectangle = DashedVMobject(signed_parallelogram(plane, base, upright, opacity=0, stroke_width=4), num_dashes=40)
        leaning = signed_parallelogram(plane, base, slanted, opacity=0.35)
        arrows = VGroup(
            vector_arrow(base, Palette.i_hat, plane),
            vector_arrow(slanted, Palette.j_hat, plane),
            vector_arrow(upright, Palette.j_hat, plane, stroke_width=5),
        )
        labels = VGroup(
            backed(MathTex(r"\mathbf a_1", color=Palette.i_hat, font_size=40), padding=0.06).next_to(plane.c2p(1.5, 0), DOWN, buff=0.15),
            backed(MathTex(r"\mathbf a_2", color=Palette.j_hat, font_size=40), padding=0.06).next_to(plane.c2p(2, 2), UP, buff=0.15),
            backed(MathTex(r"\mathbf a_2 + c\,\mathbf a_1", color=Palette.j_hat, font_size=40), padding=0.06).next_to(plane.c2p(0, 2), UL, buff=0.1),
        )
        self.add(plane, rectangle, leaning, guide, arrows, labels)
        fit_to_frame(self)


def sign_panel(second, name):
    plane = figure_plane((-1, 5), (-2, 4))
    shape = signed_parallelogram(plane, FIRST, second, opacity=0.35)
    grid = skewed_grid(plane, FIRST, second, reach=14, color=Palette.blue, opacity=0.35) if abs(signed_area(FIRST, second)) > 1e-9 else VGroup()
    arrows = VGroup(vector_arrow(FIRST, Palette.i_hat, plane), vector_arrow(second, Palette.j_hat, plane))
    area = signed_area(FIRST, second)
    color = Palette.pink if area < 0 else (Palette.yellow if area > 0 else Palette.text)
    label = backed(MathTex(name, color=color, font_size=48), padding=0.12).move_to(plane.c2p(2.2, 3.4))
    return VGroup(plane, grid, shape, arrows, orientation_arc(plane, FIRST, second, radius=0.9), label)


class FigSigns(Scene):
    def construct(self):
        panels = VGroup(
            sign_panel(SECOND, r"\det A = 5"),
            sign_panel((1.5, 0.5), r"\det A = 0"),
            sign_panel((2, -1), r"\det A = -5"),
        ).arrange(RIGHT, buff=0.5)
        self.add(panels)
        fit_to_frame(self)


class Poster(Scene):
    def construct(self):
        plane = plane_at((-2.2, -0.9), 1.45)
        plane.set_opacity(0.45)
        flipped = (2, -1)
        line_through = DashedLine(plane.c2p(-1.2, -0.4), plane.c2p(5.4, 1.8), color=Palette.text_muted, stroke_width=3)
        shapes = VGroup(signed_parallelogram(plane, FIRST, SECOND, opacity=0.4), signed_parallelogram(plane, FIRST, flipped, opacity=0.4))
        arrows = VGroup(
            vector_arrow(FIRST, Palette.i_hat, plane),
            vector_arrow(SECOND, Palette.j_hat, plane),
            vector_arrow(flipped, Palette.j_hat, plane),
        )
        arcs = VGroup(orientation_arc(plane, FIRST, SECOND, radius=1.0), orientation_arc(plane, FIRST, flipped, radius=1.0))
        labels = VGroup(
            backed(MathTex(r"\det = 5", color=Palette.yellow, font_size=60), padding=0.12).move_to(plane.c2p(-1.1, 2.3)),
            backed(MathTex(r"\det = -5", color=Palette.pink, font_size=60), padding=0.12).move_to(plane.c2p(4.6, -1.3)),
        )
        self.add(plane, line_through, shapes, arrows, arcs, labels)
