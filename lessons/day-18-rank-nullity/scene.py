import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    OrbitingView,
    Palette,
    Timing,
    backed,
    fit_to_frame,
    floor_and_axes,
    morph_matrix,
    origin_pulse,
    spring,
    spring_soft,
)

CUBE_MATRIX = np.array([[1.0, 0.0, -1.0], [0.0, 1.0, 1.0], [1.0, 1.0, 0.0]])
CUBE_ROWS = [[1, 0, -1], [0, 1, 1], [1, 1, 0]]
NULL_DIRECTION = np.array([1.0, -1.0, 1.0])
NULL_REACH = 1.35
A1 = CUBE_MATRIX[:, 0]
A2 = CUBE_MATRIX[:, 1]
IMAGE_HEXAGON = [(2, 0), (0, 2), (-2, 2), (-2, 0), (0, -2), (2, -2)]
SPACE_ORIGIN = (2.4, -0.15)
SPACE_UNIT = 1.5
SPACE_REACH = ((-2, 2), (-2, 2), (-1, 1))
ELEVATION = 20.0
FACE_ON = 60.0
SWUNG = 35.0

TALLY_ROWS = [[1, 0, 2, 0, 1], [1, 1, 1, 0, 3], [2, 1, 3, 1, 3], [3, 1, 5, 1, 4]]
TALLY_STEPS = [
    (r"R_2 - R_1,\ R_3 - 2R_1,\ R_4 - 3R_1", [[1, 0, 2, 0, 1], [0, 1, -1, 0, 2], [0, 1, -1, 1, 1], [0, 1, -1, 1, 1]]),
    (r"R_3 - R_2,\ R_4 - R_2", [[1, 0, 2, 0, 1], [0, 1, -1, 0, 2], [0, 0, 0, 1, -1], [0, 0, 0, 1, -1]]),
    (r"R_4 - R_3", [[1, 0, 2, 0, 1], [0, 1, -1, 0, 2], [0, 0, 0, 1, -1], [0, 0, 0, 0, 0]]),
]
TALLY_ECHELON = TALLY_STEPS[-1][1]
TALLY_PIVOTS = {0: 0, 1: 1, 3: 2}
SQUARE_ROWS = [[1, 2, 0], [0, 1, 3], [0, 0, 1]]
SQUARE_PIVOTS = {0: 0, 1: 1, 2: 2}
WIDE_ROWS = [[1, 2, 0, 1], [0, 0, 1, 3]]
WIDE_PIVOTS = {0: 0, 2: 1}

MATRIX_CENTER = np.array([-2.55, 0.75, 0.0])
BIG_SCALE = 1.15
CELL = 0.62
BLOCK = 0.72
BAR_LEFT = 2.55
RANK_BAR_Y = 1.75
NULLITY_BAR_Y = 0.55
PIVOT_COLOR = Palette.teal
FREE_COLOR = Palette.pink


def squashed(point, amount):
    """The point partway along its path from x to Ax."""
    point = np.asarray(point, dtype=float)
    return (1 - amount) * point + amount * (CUBE_MATRIX @ point)


def cube_lines(project, amount, opacity=0.6):
    """The lattice lines of the cube [-1, 1]^3, carried partway to their images under A."""
    lines = VGroup()
    for axis in range(3):
        others = [index for index in range(3) if index != axis]
        for u in (-1, 0, 1):
            for v in (-1, 0, 1):
                start, end = np.zeros(3), np.zeros(3)
                start[axis], end[axis] = -1, 1
                start[others[0]] = end[others[0]] = u
                start[others[1]] = end[others[1]] = v
                lines.add(Line(project(squashed(start, amount)), project(squashed(end, amount)), color=Palette.blue, stroke_width=1.8, stroke_opacity=opacity))
    return lines


def null_line(project, shrink, color=FREE_COLOR, width=6):
    reach = NULL_REACH * (1 - shrink)
    return Line(project(-reach * NULL_DIRECTION), project(reach * NULL_DIRECTION), color=color, stroke_width=width)


def image_sheet(project, opacity=0.24):
    corners = [s * A1 + t * A2 for s, t in IMAGE_HEXAGON]
    return Polygon(*[project(corner) for corner in corners], stroke_color=Palette.teal, stroke_width=2, stroke_opacity=0.8, fill_color=Palette.teal, fill_opacity=opacity)


def space_tag(project, point, tex, color, direction, font_size=38):
    return backed(MathTex(tex, color=color, font_size=font_size), padding=0.07).next_to(project(point), direction, buff=0.12)


def numbered_matrix(rows, h_buff=0.9):
    mat = Matrix([[str(entry) for entry in row] for row in rows], v_buff=0.62, h_buff=h_buff, bracket_h_buff=0.14)
    return mat.set_color(Palette.text)


def pivot_frames(mat, pivots):
    rows = mat.get_rows()
    return VGroup(*[SurroundingRectangle(rows[row][col], color=Palette.glow, buff=0.1, stroke_width=3.5) for col, row in pivots.items()])


def cell_row(mat, size=CELL, buff=0.35):
    """One empty square under each column of mat."""
    columns = mat.get_columns()
    bottom = mat.get_bottom()[1] - buff - size / 2
    return VGroup(*[Square(size, color=Palette.text_muted, stroke_width=2).move_to([column.get_center()[0], bottom, 0]) for column in columns])


def filled(cell, color):
    return Square(cell.width, stroke_width=0, fill_color=color, fill_opacity=0.9).move_to(cell)


def tint_colors(count, pivots):
    return [PIVOT_COLOR if index in pivots else FREE_COLOR for index in range(count)]


def small_tally(rows, pivots, shape_tex, sum_tex):
    """A small echelon matrix with tinted columns, pivot frames, filled cells, its shape above and its count below."""
    mat = numbered_matrix(rows)
    for column, color in zip(mat.get_columns(), tint_colors(len(rows[0]), pivots)):
        column.set_color(color)
    cells = cell_row(mat, size=0.5, buff=0.3)
    fills = VGroup(*[filled(cell, color) for cell, color in zip(cells, tint_colors(len(rows[0]), pivots))])
    shape = MathTex(shape_tex, color=Palette.text_muted, font_size=40).next_to(mat, UP, buff=0.35)
    count = MathTex(sum_tex, color=Palette.text, font_size=40).next_to(cells, DOWN, buff=0.3)
    return VGroup(shape, mat, pivot_frames(mat, pivots), cells, fills, count)


def bar_blocks(count, color, y, left=BAR_LEFT + 1.55):
    return VGroup(*[Square(BLOCK, stroke_width=0, fill_color=color, fill_opacity=0.9).move_to([left + BLOCK / 2 + index * (BLOCK + 0.06), y, 0]) for index in range(count)])


def merged_bar(y):
    """Three teal blocks then two pink, touching, the whole bar of n = 5 columns."""
    blocks = VGroup(*[Square(BLOCK, stroke_width=0, fill_color=color, fill_opacity=0.9) for color in [PIVOT_COLOR] * 3 + [FREE_COLOR] * 2])
    blocks.arrange(RIGHT, buff=0.06).move_to([BAR_LEFT + 2.1, y, 0])
    return blocks


def bar_braces(blocks):
    rank = Brace(blocks[:3], UP, color=PIVOT_COLOR)
    nullity = Brace(blocks[3:], UP, color=FREE_COLOR)
    total = Brace(blocks, DOWN, color=Palette.text_muted)
    return VGroup(
        rank,
        MathTex("3", color=PIVOT_COLOR, font_size=40).next_to(rank, UP, buff=0.1),
        nullity,
        MathTex("2", color=FREE_COLOR, font_size=40).next_to(nullity, UP, buff=0.1),
        total,
        MathTex("n = 5", color=Palette.text, font_size=40).next_to(total, DOWN, buff=0.1),
    )


def variable_row(mat):
    return VGroup(*[MathTex(f"x_{index + 1}", color=Palette.text_muted, font_size=34).next_to(column, UP, buff=0.45) for index, column in enumerate(mat.get_columns())]).align_to(mat.get_top() + UP * 0.45, DOWN)


class Lesson(LessonScene):
    day = 18
    title = "Rank and nullity"

    def construct(self):
        pulse = self.open_episode()
        self.play(FadeOut(pulse), run_time=0.5)
        self.view = OrbitingView(SPACE_ORIGIN, SPACE_UNIT, azimuth=SWUNG, elevation=ELEVATION)
        line = self.meet_the_cube()
        line = self.squash(line)
        line = self.crush_the_line(line)
        line = self.count_dimensions(line)
        line = self.bigger_matrix(line)
        line = self.sweep(line)
        line = self.merge_bars(line)
        line = self.rows_match(line)
        line = self.other_shapes(line)
        line = self.shape_only(line)
        self.close_episode(
            r"Every column is a pivot column or a free column.\\"
            r"So $\operatorname{rank}A + \operatorname{nullity}A = n$, the number of columns.",
            *self.mobjects,
        )

    def project(self, point):
        return self.view.project(point)

    def clear_stage(self, line, run_time=0.7):
        leaving = [mobject for mobject in self.mobjects if mobject is not line]
        for mobject in leaving:
            mobject.clear_updaters()
        self.play(*[FadeOut(mobject) for mobject in leaving], run_time=run_time)
        self.remove(*leaving)

    def meet_the_cube(self):
        self.squash_amount = ValueTracker(0.0)
        self.crush = ValueTracker(0.0)
        colored = numbered_matrix(CUBE_ROWS)
        for part, color in zip(colored.get_columns(), (Palette.i_hat, Palette.j_hat, Palette.pink)):
            part.set_color(color)
        self.cube_matrix = VGroup(MathTex("A", "=", color=Palette.text), colored).arrange(RIGHT, buff=0.2).move_to([-4.55, 2.35, 0])
        self.axes = always_redraw(lambda: floor_and_axes(self.project, SPACE_REACH))
        self.cube = always_redraw(lambda: cube_lines(self.project, self.squash_amount.get_value()))
        self.null = always_redraw(lambda: null_line(self.project, self.crush.get_value()))
        line = self.say(r"Days 16 and 17 gave every matrix two subspaces.", hold=0.2)
        self.play(Write(self.cube_matrix), run_time=1.2)
        self.wait(Timing.beat)
        line = self.say(r"Today we ask how their sizes are related.", line, hold=0.2)
        self.play(Create(self.axes), run_time=1.0)
        self.wait(Timing.beat)
        line = self.say(r"Day 16's matrix has three columns, so it acts on $\mathbb R^3$.", line, hold=0.2)
        self.play(Create(self.cube, lag_ratio=0.03), run_time=1.6)
        self.play(Create(self.null), run_time=0.8)
        self.play(self.view.turn_to(FACE_ON), run_time=2.2, rate_func=smooth)
        return line

    def squash(self, line):
        line = self.say(r"Watch a cube of inputs pass through $A$.", line, hold=0.3)
        self.sfx("slide", gain=-2)
        self.play(self.squash_amount.animate.set_value(1.0), self.crush.animate.set_value(1.0), run_time=3.0, rate_func=smooth)
        self.remove(self.null)
        self.center_glow = origin_pulse().move_to(self.project((0, 0, 0)))
        self.play(GrowFromCenter(self.center_glow), run_time=0.6, rate_func=spring)
        self.sheet = image_sheet(self.project)
        self.col_tag = space_tag(self.project, A1 - 2 * A2, r"\operatorname{Col}A", Palette.teal, DL)
        line = self.say(r"Everything lands flat on the plane $\operatorname{Col}A$.", line, hold=0.2)
        self.bring_to_back(self.sheet)
        self.bring_to_back(self.axes)
        self.sfx("shimmer", gain=-6)
        self.play(FadeIn(self.sheet), FadeIn(self.col_tag), run_time=1.0)
        self.wait(Timing.read_short)
        return line

    def crush_the_line(self, line):
        ghost = DashedLine(self.project(-NULL_REACH * NULL_DIRECTION), self.project(NULL_REACH * NULL_DIRECTION), color=FREE_COLOR, stroke_width=3, dash_length=0.1)
        ghost.set_opacity(0.7)
        nul_tag = space_tag(self.project, NULL_REACH * NULL_DIRECTION, r"\operatorname{Nul}A", FREE_COLOR, UP)
        line = self.say(r"One whole line of inputs lands on zero.", line, hold=0.2)
        self.play(Create(ghost), FadeIn(nul_tag), run_time=0.9)
        self.crush.set_value(0.0)
        self.add(self.null)
        self.play(self.crush.animate.set_value(1.0), run_time=1.8, rate_func=smooth)
        self.remove(self.null)
        self.play(Flash(self.project((0, 0, 0)), color=Palette.glow, line_length=0.3, flash_radius=0.4), run_time=0.8)
        self.wait(Timing.read_short)
        self.ghost, self.nul_tag = ghost, nul_tag
        return line

    def count_dimensions(self, line):
        rank = MathTex(r"\operatorname{rank}A", "=", r"\dim\operatorname{Col}A", "=", "2", font_size=40)
        nullity = MathTex(r"\operatorname{nullity}A", "=", r"\dim\operatorname{Nul}A", "=", "1", font_size=40)
        total = MathTex("2", "+", "1", "=", "3", font_size=44)
        for part in (rank[0], rank[4], total[0]):
            part.set_color(PIVOT_COLOR)
        for part in (nullity[0], nullity[4], total[2]):
            part.set_color(FREE_COLOR)
        VGroup(rank, nullity, total).arrange(DOWN, buff=0.45, aligned_edge=LEFT).next_to(self.cube_matrix, DOWN, buff=0.6).align_to(self.cube_matrix, LEFT)
        line = self.say(r"Two dimensions survive, so $\operatorname{rank}A = 2$.", line, hold=0.2)
        self.play(Write(rank), Indicate(VGroup(*self.col_tag.submobjects[1:]), color=Palette.teal), run_time=1.3)
        self.wait(Timing.read_short)
        line = self.say(r"One dimension is crushed, so $\operatorname{nullity}A = 1$.", line, hold=0.2)
        self.play(Write(nullity), Indicate(VGroup(*self.nul_tag.submobjects[1:]), color=FREE_COLOR), run_time=1.3)
        self.wait(Timing.read_short)
        line = self.say(r"Together they make 3, one for each column of $A$.", line, hold=0.2)
        self.play(Write(total), run_time=1.0)
        self.play(Indicate(self.cube_matrix[1].get_columns(), color=Palette.glow, scale_factor=1.1), run_time=1.0)
        self.wait(Timing.read_short)
        self.clear_stage(line)
        return line

    def bigger_matrix(self, line):
        self.big = numbered_matrix(TALLY_ROWS, h_buff=1.05).scale(BIG_SCALE).move_to(MATRIX_CENTER)
        self.big_name = MathTex("A", "=", color=Palette.text).scale(BIG_SCALE).next_to(self.big, LEFT, buff=0.2)
        line = self.say(r"Here is a bigger matrix with five columns.", line, hold=0.2)
        self.play(Write(VGroup(self.big_name, self.big)), run_time=1.6)
        self.wait(Timing.beat)
        line = self.say(r"Row reduce until the pivots show, since they decide both counts.", line, hold=0.2)
        operation = None
        for tex, rows in TALLY_STEPS:
            target = numbered_matrix(rows, h_buff=1.05).scale(BIG_SCALE).move_to(self.big)
            label = MathTex(tex, color=Palette.text_muted, font_size=36).next_to(self.big, DOWN, buff=0.4)
            self.play(*([FadeOut(operation)] if operation else []), FadeIn(label, shift=UP * 0.1), run_time=0.45)
            operation = label
            morph_matrix(self, self.big, target, run_time=1.2)
            self.wait(0.6)
        self.play(FadeOut(operation), run_time=0.35)
        self.remove(operation)
        return line

    def sweep(self, line):
        self.cells = cell_row(self.big)
        self.variables = variable_row(self.big)
        self.rank_blocks = bar_blocks(3, PIVOT_COLOR, RANK_BAR_Y)
        self.nullity_blocks = bar_blocks(2, FREE_COLOR, NULLITY_BAR_Y)
        rank_label = MathTex(r"\operatorname{rank}", color=PIVOT_COLOR, font_size=40).move_to([BAR_LEFT + 0.6, RANK_BAR_Y, 0])
        nullity_label = MathTex(r"\operatorname{nullity}", color=FREE_COLOR, font_size=40).move_to([BAR_LEFT + 0.6, NULLITY_BAR_Y, 0])
        self.bar_labels = VGroup(rank_label, nullity_label)
        line = self.say(r"Each column is either a pivot column or a free column.", line, hold=0.2)
        self.play(FadeIn(self.variables), Create(self.cells), FadeIn(self.bar_labels), run_time=1.0)
        self.scan = SurroundingRectangle(self.big.get_columns()[0], color=Palette.text_muted, buff=0.14, stroke_width=2)
        self.play(Create(self.scan), run_time=0.5)
        self.frames, self.fills = VGroup(), VGroup()
        counters = {"pivot": 0, "free": 0}
        captions = {
            0: r"A pivot column adds one dimension to $\operatorname{Col}A$.",
            2: r"A free column adds one free variable and one null direction.",
        }
        for index in range(5):
            if index in captions:
                line = self.say(captions[index], line, hold=0.2)
            self.classify(index, counters)
            self.wait(Timing.read_short if index in (0, 2) else Timing.beat)
        self.play(FadeOut(self.scan), run_time=0.4)
        return line

    def classify(self, index, counters):
        if index > 0:
            self.play(self.scan.animate.move_to(self.big.get_columns()[index]), run_time=0.6, rate_func=spring)
        column = self.big.get_columns()[index]
        pivot = index in TALLY_PIVOTS
        color = PIVOT_COLOR if pivot else FREE_COLOR
        if pivot:
            frame = pivot_frames(self.big, {index: TALLY_PIVOTS[index]})
            self.frames.add(frame)
            self.play(Create(frame), run_time=0.5)
        cell_fill = filled(self.cells[index], color)
        self.fills.add(cell_fill)
        tints = [column.animate.set_color(color), FadeIn(cell_fill, scale=0.6)]
        if not pivot:
            tints.append(self.variables[index].animate.set_color(FREE_COLOR))
        self.sfx("pop", gain=-6)
        self.play(*tints, run_time=0.6, rate_func=spring)
        kind = "pivot" if pivot else "free"
        block = (self.rank_blocks if pivot else self.nullity_blocks)[counters[kind]]
        counters[kind] += 1
        self.play(TransformFromCopy(cell_fill, block), run_time=0.8, rate_func=spring_soft)

    def merge_bars(self, line):
        bar = merged_bar((RANK_BAR_Y + NULLITY_BAR_Y) / 2)
        braces = bar_braces(bar)
        formula = MathTex(r"\operatorname{rank}A", "+", r"\operatorname{nullity}A", "=", "n", font_size=42)
        formula[0].set_color(PIVOT_COLOR)
        formula[2].set_color(FREE_COLOR)
        numbers = MathTex("3", "+", "2", "=", "5", font_size=42)
        numbers[0].set_color(PIVOT_COLOR)
        numbers[2].set_color(FREE_COLOR)
        VGroup(formula, numbers).arrange(DOWN, buff=0.3).next_to(bar, DOWN, buff=1.05)
        line = self.say(r"Rank plus nullity always equals the number of columns.", line, hold=0.2)
        blocks = [*self.rank_blocks, *self.nullity_blocks]
        self.play(FadeOut(self.bar_labels), *[block.animate.move_to(target) for block, target in zip(blocks, bar)], run_time=1.2, rate_func=spring)
        self.play(FadeIn(braces), run_time=0.8)
        self.play(Write(formula), run_time=1.2)
        self.play(FadeIn(numbers, shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(*blocks, braces, formula, numbers)), run_time=0.6)
        self.remove(*blocks, braces, formula, numbers, self.bar_labels)
        return line

    def rows_match(self, line):
        rows = self.big.get_rows()
        row_frames = VGroup(*[SurroundingRectangle(rows[index], color=Palette.glow, buff=0.08, stroke_width=2.5) for index in range(3)])
        statement = MathTex(r"\dim\operatorname{Row}A", "=", r"\dim\operatorname{Col}A", "=", "3", font_size=42)
        statement[4].set_color(PIVOT_COLOR)
        spaces = MathTex(r"\operatorname{Row}A \subseteq \mathbb R^5", r"\quad", r"\operatorname{Col}A \subseteq \mathbb R^4", color=Palette.text_muted, font_size=38)
        VGroup(statement, spaces).arrange(DOWN, buff=0.5, aligned_edge=LEFT).to_edge(RIGHT, buff=0.45).set_y(1.0)
        line = self.say(r"Each pivot also sits in its own nonzero row.", line, hold=0.2)
        self.play(FadeOut(self.frames), *[Create(frame) for frame in row_frames], run_time=1.0)
        self.play(Indicate(rows[3], color=Palette.text_muted, scale_factor=1.05), run_time=0.8)
        self.wait(Timing.beat)
        line = self.say(r"So $\dim\operatorname{Row}A$ equals $\dim\operatorname{Col}A$, the number of pivots.", line, hold=0.2)
        self.play(Write(statement), run_time=1.4)
        self.wait(Timing.read_short)
        line = self.say(r"The rows and columns live in different spaces, yet counts match.", line, hold=0.2)
        self.play(FadeIn(spaces, shift=UP * 0.1), run_time=0.8)
        self.wait(Timing.read_short)
        self.clear_stage(line)
        return line

    def other_shapes(self, line):
        square = small_tally(SQUARE_ROWS, SQUARE_PIVOTS, r"3 \times 3", r"3 + 0 = 3").scale(1.2).move_to([-3.3, 0.4, 0])
        wide = small_tally(WIDE_ROWS, WIDE_PIVOTS, r"2 \times 4", r"2 + 2 = 4").scale(1.2).move_to([3.3, 0.4, 0])
        line = self.say(r"The same tally works for any shape.", line, hold=0.2)
        self.play(FadeIn(square[:2]), run_time=0.8)
        self.play(Create(square[2]), Create(square[3]), run_time=0.8)
        self.play(FadeIn(square[4], lag_ratio=0.3), Write(square[5]), run_time=1.2)
        self.wait(Timing.read_short)
        line = self.say(r"Two rows allow only two pivots, so two columns are free.", line, hold=0.2)
        self.play(FadeIn(wide[:2]), run_time=0.8)
        self.play(Create(wide[2]), Create(wide[3]), run_time=0.8)
        self.play(FadeIn(wide[4], lag_ratio=0.3), Write(wide[5]), run_time=1.2)
        self.wait(Timing.read_long)
        self.clear_stage(line)
        return line

    def shape_only(self, line):
        question = MathTex(r"7 \times 9", r",\ \ \operatorname{nullity}A = 2", font_size=48).move_to([0, 2.4, 0])
        question[1].set_color(FREE_COLOR)
        cells = VGroup(*[Square(0.8, color=Palette.text_muted, stroke_width=2) for _ in range(9)]).arrange(RIGHT, buff=0.08).move_to([0, 0.7, 0])
        free = VGroup(*[filled(cell, FREE_COLOR) for cell in cells[7:]])
        pivots = VGroup(*[filled(cell, PIVOT_COLOR) for cell in cells[:7]])
        brace = Brace(pivots, DOWN, color=PIVOT_COLOR)
        answer = MathTex(r"\operatorname{rank}A = 9 - 2 = 7", color=PIVOT_COLOR, font_size=44).next_to(brace, DOWN, buff=0.15)
        line = self.say(r"A $7\times 9$ matrix with nullity 2 must have rank 7.", line, hold=0.2)
        self.play(Write(question), Create(cells), run_time=1.2)
        self.play(FadeIn(free, lag_ratio=0.4, scale=0.6), run_time=0.8, rate_func=spring)
        self.play(LaggedStart(*[FadeIn(block, scale=0.6) for block in pivots], lag_ratio=0.15), run_time=1.6)
        self.play(FadeIn(brace), Write(answer), run_time=1.0)
        self.wait(Timing.read_short)
        return self.too_few_rows(line, question, pivots)

    def too_few_rows(self, line, question, pivots):
        shorter = MathTex(r"6 \times 9", r",\ \ \operatorname{nullity}A = 2", font_size=48).move_to(question)
        shorter[1].set_color(FREE_COLOR)
        seventh = pivots[6]
        cross = VGroup(
            Line(seventh.get_corner(UL), seventh.get_corner(DR), color=Palette.glow, stroke_width=6),
            Line(seventh.get_corner(DL), seventh.get_corner(UR), color=Palette.glow, stroke_width=6),
        ).scale(0.7)
        line = self.say(r"A $6\times 9$ matrix cannot, since seven pivots need seven rows.", line, hold=0.2)
        self.play(FadeOut(question[0], shift=UP * 0.2), FadeIn(shorter[0], shift=UP * 0.2), run_time=0.7)
        self.remove(question[0])
        self.add(shorter[0])
        self.play(Create(cross), seventh.animate.set_opacity(0.3), run_time=0.8)
        self.wait(Timing.read_long)
        line = self.say(r"Tomorrow this count ties together the tests for an inverse.", line, hold=Timing.read_short)
        return line


class FigSquash(Scene):
    def construct(self):
        view = OrbitingView((0, 0), 1.0, azimuth=FACE_ON, elevation=ELEVATION)
        project = view.project
        ghost_cube = cube_lines(project, 0.0, opacity=0.16)
        ghost = DashedLine(project(-NULL_REACH * NULL_DIRECTION), project(NULL_REACH * NULL_DIRECTION), color=FREE_COLOR, stroke_width=3, dash_length=0.1)
        self.add(
            floor_and_axes(project, SPACE_REACH),
            ghost_cube,
            image_sheet(project),
            cube_lines(project, 1.0),
            ghost,
            origin_pulse(),
            space_tag(project, A1 - 2 * A2, r"\operatorname{Col}A", Palette.teal, DL),
            space_tag(project, NULL_REACH * NULL_DIRECTION, r"\operatorname{Nul}A", FREE_COLOR, UP),
        )
        fit_to_frame(self)


def tally_still(pivot_marks=True, with_bar=True):
    """The reduced 4 by 5 matrix with pivot and free columns tinted, for the figures and poster."""
    mat = numbered_matrix(TALLY_ECHELON, h_buff=1.05)
    for column, color in zip(mat.get_columns(), tint_colors(5, TALLY_PIVOTS)):
        column.set_color(color)
    variables = variable_row(mat)
    for index in (2, 4):
        variables[index].set_color(FREE_COLOR)
    cells = cell_row(mat)
    fills = VGroup(*[filled(cell, color) for cell, color in zip(cells, tint_colors(5, TALLY_PIVOTS))])
    group = VGroup(mat, variables, cells, fills)
    if pivot_marks:
        group.add(pivot_frames(mat, TALLY_PIVOTS))
    if with_bar:
        bar = merged_bar(0).next_to(mat, RIGHT, buff=1.2)
        group.add(bar, bar_braces(bar))
    return group


class FigTally(Scene):
    def construct(self):
        self.add(tally_still())
        fit_to_frame(self, margin=0.6)


class FigRowsAndColumns(Scene):
    def construct(self):
        mat = numbered_matrix(TALLY_ECHELON, h_buff=1.05)
        for column, color in zip(mat.get_columns(), tint_colors(5, TALLY_PIVOTS)):
            column.set_color(color)
        rows = mat.get_rows()
        row_frames = VGroup(*[SurroundingRectangle(rows[index], color=Palette.glow, buff=0.08, stroke_width=2.5) for index in range(3)])
        statement = MathTex(r"\dim\operatorname{Row}A", "=", "3", "=", r"\dim\operatorname{Col}A", font_size=44).next_to(mat, DOWN, buff=0.6)
        statement[2].set_color(PIVOT_COLOR)
        self.add(mat, row_frames, statement)
        fit_to_frame(self, margin=0.8)


class FigShapes(Scene):
    def construct(self):
        square = small_tally(SQUARE_ROWS, SQUARE_PIVOTS, r"3 \times 3", r"3 + 0 = 3")
        wide = small_tally(WIDE_ROWS, WIDE_PIVOTS, r"2 \times 4", r"2 + 2 = 4")
        VGroup(square, wide).arrange(RIGHT, buff=1.6, aligned_edge=DOWN)
        self.add(square, wide)
        fit_to_frame(self, margin=0.7)


class Poster(Scene):
    def construct(self):
        still = tally_still()
        still.scale_to_fit_width(config.frame_width - 1.6).move_to(ORIGIN)
        self.add(still)
