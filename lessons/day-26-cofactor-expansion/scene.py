import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene,
    LiveMatrix,
    Palette,
    Timing,
    cell_outline,
    fit_to_frame,
    live_basis_arrows,
    make_plane,
    matrix,
    morph_matrix,
    plane_at,
    plate_for,
    scrim,
    spring,
    spring_soft,
    vector_arrow,
)

A_ROWS = ((2, 2, 1), (1, 0, 1), (0, -2, -1))
U_ROWS = ((3, 1, 4), (0, 2, 5), (0, 0, -1))
B_STATES = [
    ((0, 1, 2), (1, 2, 1), (2, 3, 4)),
    ((1, 2, 1), (0, 1, 2), (2, 3, 4)),
    ((1, 2, 1), (0, 1, 2), (0, -1, 2)),
    ((1, 2, 1), (0, 1, 2), (0, 0, 4)),
]
B_STEPS = [
    (r"R_1 \leftrightarrow R_2", r"Swapping rows 1 and 2 puts a minus sign in front."),
    (r"R_3 \leftarrow R_3 - 2R_1", r"Replacements leave the determinant alone."),
    (r"R_3 \leftarrow R_3 + R_2", r"One more replacement makes it triangular."),
]
IDENTITY = ((1, 0), (0, 1))
M_ROWS = ((2, 1), (1, 2))
N_ROWS = ((1, 2), (0, 2))
MN_ROWS = ((2, 6), (1, 6))
ROW_OPERATIONS = [
    (((1, 0), (-1, 1)), r"R_2 \leftarrow R_2 - R_1", r"\det \text{ stays } 3"),
    (((0, 1), (1, 0)), r"R_1 \leftrightarrow R_2", r"\det \text{ flips to } {-3}"),
    (((2, 0), (0, 1)), r"R_1 \leftarrow 2R_1", r"\det \text{ doubles to } {-6}"),
]
ROW_OPERATION_CAPTIONS = [
    (r"Adding a multiple of another row shears the picture.", r"The area never changes, so $\det$ stays 3."),
    (r"Swapping two rows flips the picture, so $\det$ turns negative.", None),
    (r"Scaling a row by 2 doubles the area and $\det$.", None),
]

PLANE_ORIGIN = (2.4, -1.2)
PLANE_UNIT = 1.1
MATRIX_SCALE = 1.2
MATRIX_CENTER = LEFT * 4.3 + UP * 0.35
LINES_LEFT = -1.3
LINE_SLOTS = (2.55, 1.1, -0.35)
TOTAL_SLOTS = (-1.55, -2.3)
DIM = 0.22


def minor_of(rows, i, j):
    return tuple(tuple(value for c, value in enumerate(row) if c != j) for r, row in enumerate(rows) if r != i)


def det2(rows):
    (a, b), (c, d) = rows
    return a * d - b * c


def sign_of(i, j):
    return 1 if (i + j) % 2 == 0 else -1


def wrapped(value):
    return f"({value})" if value < 0 else str(value)


def cross_tex(minor):
    (a, b), (c, d) = minor
    return rf"{wrapped(a)} \cdot {wrapped(d)} - {wrapped(b)} \cdot {wrapped(c)}"


def signed(value, first):
    return str(value) if first or value < 0 else f"+{value}"


def grid(rows, **kwargs):
    return matrix([[str(value) for value in row] for row in rows], **kwargs)


def bars(rows):
    """A determinant written with vertical bars, entries blue because they are a minor."""
    mat = grid(rows, left_bracket="|", right_bracket="|")
    mat.get_entries().set_color(Palette.blue)
    return mat


def roomy(mat, room=0.22):
    """Push the left bracket out so the checkerboard marks of column 1 sit clear of it."""
    mat.get_brackets()[0].shift(LEFT * room)
    return mat


def named(name, mat, font_size=48):
    return VGroup(MathTex(name, "=", color=Palette.text, font_size=font_size), mat).arrange(RIGHT, buff=0.2)


def entries_of(mat):
    return [list(row) for row in mat.get_rows()]


def sign_marks(mat, font_size=28, lift=0.3, gap=0.13):
    """The checkerboard of + and - signs, one small mark at the upper left of each entry."""
    rows, columns = mat.get_rows(), mat.get_columns()
    marks = VGroup()
    for i, row in enumerate(rows):
        for j in range(len(columns)):
            mark = MathTex("+" if sign_of(i, j) > 0 else "-", color=Palette.text_muted, font_size=font_size)
            mark.move_to([columns[j].get_left()[0] - gap, row.get_center()[1] + lift, 0], aligned_edge=RIGHT)
            marks.add(mark)
    return marks


def entry_style(r, c, i, j):
    """Color and opacity of entry (r, c) while entry (i, j) is expanded."""
    if (r, c) == (i, j):
        return Palette.yellow, 1.0
    if r != i and c != j:
        return Palette.blue, 1.0
    return Palette.text, DIM


def mark_style(r, c, i, j):
    return (Palette.glow, 1.0) if (r, c) == (i, j) else (Palette.text_muted, 0.35)


def focus_styles(mat, marks, i, j):
    """(mobject, color, opacity) for every entry and sign mark while entry (i, j) is expanded."""
    size = len(mat.get_rows())
    styles = [(entry, *entry_style(r, c, i, j)) for r, row in enumerate(entries_of(mat)) for c, entry in enumerate(row)]
    if marks is not None:
        styles += [(mark, *mark_style(*divmod(index, size), i, j)) for index, mark in enumerate(marks)]
    return styles


def rest_styles(mat, marks):
    styles = [(entry, Palette.text, 1.0) for entry in mat.get_entries()]
    if marks is not None:
        styles += [(mark, Palette.text_muted, 1.0) for mark in marks]
    return styles


def entry_part(value):
    """The entry as it is written in a term, in parentheses when negative. Returns (group, bare number)."""
    if value < 0:
        part = MathTex("(", str(value), ")", color=Palette.yellow)
        return part, part[1]
    part = MathTex(str(value), color=Palette.yellow)
    return part, part


class ExpansionLine:
    """One term of a cofactor expansion: sign, entry, minor, its cross product, and the term."""

    def __init__(self, rows, i, j, first, font_size=44):
        entry = rows[i][j]
        self.minor_rows = minor_of(rows, i, j)
        sign = sign_of(i, j)
        value = det2(self.minor_rows)
        self.term = sign * entry * value
        prefix = ("+" if sign > 0 else "-") + wrapped(entry)
        self.sign = MathTex("+" if sign > 0 else "-", color=Palette.glow, font_size=font_size)
        self.entry, self.entry_core = entry_part(entry)
        self.entry.scale(font_size / 48)
        self.minor = bars(self.minor_rows).scale(0.82)
        self.equals = MathTex("=", color=Palette.text, font_size=font_size)
        self.product = MathTex(rf"{prefix}\,({value})", color=Palette.text, font_size=font_size)
        self.equals_again = MathTex("=", color=Palette.text, font_size=font_size)
        self.result = MathTex(signed(self.term, first), color=Palette.teal, font_size=font_size)
        self.group = VGroup(self.sign, self.entry, self.minor, self.equals, self.product, self.equals_again, self.result)
        self.group.arrange(RIGHT, buff=0.2)
        self.entry.next_to(self.sign, RIGHT, buff=0.08)
        self.cross = MathTex(rf"{prefix}\,({cross_tex(self.minor_rows)})", color=Palette.text, font_size=font_size)

    def place(self, left, y):
        self.group.move_to([left, y, 0], aligned_edge=LEFT)
        self.cross.move_to(self.product, aligned_edge=LEFT)
        return self

    def diagonals(self):
        cells = entries_of(self.minor)
        return VGroup(
            Line(cells[0][0].get_center(), cells[1][1].get_center(), color=Palette.glow, stroke_width=4, stroke_opacity=0.7),
            Line(cells[0][1].get_center(), cells[1][0].get_center(), color=Palette.glow, stroke_width=4, stroke_opacity=0.7),
        )


def total_line(label, terms, answer, font_size=44):
    parts = MathTex(rf"\text{{{label}}}", r"\quad \det A", "=", *terms, "=", str(answer), color=Palette.text, font_size=font_size)
    for part in parts[3 : 3 + len(terms)]:
        part.set_color(Palette.teal)
    parts[-1].set_color(Palette.teal)
    return parts


def parallelogram(plane, columns, opacity=0.3):
    first, second = (np.array(column, dtype=float) for column in columns)
    determinant = first[0] * second[1] - first[1] * second[0]
    color = Palette.yellow if determinant >= 0 else Palette.pink
    corners = [plane.c2p(0, 0), plane.c2p(*first), plane.c2p(*(first + second)), plane.c2p(*second)]
    return Polygon(*corners, color=color, fill_opacity=opacity, stroke_width=0)


def live_columns(live):
    return live.column(0), live.column(1)


def number_text(value):
    rounded = round(value, 1)
    if abs(rounded) < 0.05:
        return "0"
    if rounded == int(rounded):
        return str(int(rounded))
    return f"{rounded:.1f}"


def column_colored(rows):
    mat = grid(rows)
    for column, color in zip(mat.get_columns(), (Palette.i_hat, Palette.j_hat)):
        column.set_color(color)
    return mat


def centerpiece_layout():
    """A, its sign marks, the three expansion lines for row 1, and the running total, all in final position."""
    a_group = named("A", roomy(grid(A_ROWS))).scale(MATRIX_SCALE).move_to(MATRIX_CENTER)
    marks = sign_marks(a_group[1])
    lines = [ExpansionLine(A_ROWS, 0, j, first=j == 0).place(LINES_LEFT, y) for j, y in enumerate(LINE_SLOTS)]
    total = total_line("row 1:", [line.result.get_tex_string() for line in lines], 4)
    total.move_to([LINES_LEFT, TOTAL_SLOTS[0], 0], aligned_edge=LEFT)
    return a_group, marks, lines, total


def apply_styles(styles):
    for mobject, color, opacity in styles:
        mobject.set_color(color).set_opacity(opacity)


class Lesson(LessonScene):
    day = 26
    title = "Computing determinants"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        self.live = LiveMatrix(IDENTITY)
        line = self.area_recall(plane)
        line = self.submatrices(line)
        line = self.expand_row_one(line)
        line = self.expand_column_two(line)
        line = self.triangular(line)
        line = self.row_operations(plane, line)
        line = self.reduce_to_triangular(line)
        line = self.transpose_and_product(line)
        self.close_episode(
            r"Expand along any row or column, with checkerboard signs.\\"
            r"Row operations change $\det$ in three predictable ways.",
            *self.mobjects,
        )

    def dismiss(self, *mobjects, run_time=0.6):
        """Fade mobjects out and drop every piece of them that was added to the scene on its own."""
        self.play(*[FadeOut(mobject) for mobject in mobjects], run_time=run_time)
        self.drop(*mobjects)

    def drop(self, *mobjects):
        """Remove every top-level mobject that holds any piece of these, so no stray piece stays on screen."""
        family = {id(part) for mobject in mobjects for part in mobject.get_family()}
        self.remove(*[mobject for mobject in self.mobjects if any(id(part) in family for part in mobject.get_family())])

    def restyle(self, styles, run_time=0.7):
        self.play(*[mobject.animate.set_color(color).set_opacity(opacity) for mobject, color, opacity in styles], run_time=run_time)

    def area_recall(self, plane):
        self.shape = always_redraw(lambda: parallelogram(plane, live_columns(self.live)))
        self.arrows = live_basis_arrows(plane, self.live)
        line = self.say(r"On Day 25, $\det$ measured how a matrix scales area.", hold=0.2)
        self.play(FadeIn(self.shape), FadeIn(self.arrows, scale=0.6), run_time=0.8, rate_func=spring_soft)
        self.play(*self.live.move_to(M_ROWS), run_time=1.4, rate_func=spring)
        card = named("M", column_colored(M_ROWS)).to_corner(UL, buff=0.6)
        formula = MathTex(r"\det M = 2 \cdot 2 - 1 \cdot 1 = 3", color=Palette.text, font_size=44)
        formula.next_to(card, DOWN, buff=0.4).align_to(card, LEFT)
        plate = plate_for(VGroup(card, formula))
        self.play(FadeIn(plate), FadeIn(card, shift=UP * 0.15), run_time=0.8, rate_func=spring_soft)
        line = self.say(r"For 2 by 2, the formula $ad - bc$ gives it.", line, hold=0.2)
        self.play(Write(formula), run_time=1.2)
        self.wait(Timing.read_short)
        self.dismiss(plate, card, formula)
        return line

    def submatrices(self, line):
        self.veil = scrim()
        self.a_group = named("A", roomy(grid(A_ROWS))).scale(MATRIX_SCALE).move_to(MATRIX_CENTER)
        self.a_mat = self.a_group[1]
        self.marks = sign_marks(self.a_mat)
        line = self.say(r"Bigger matrices need a recipe built from 2 by 2 pieces.", line, hold=0.2)
        self.play(FadeIn(self.veil), run_time=0.6)
        self.play(Write(self.a_group), run_time=1.4)

        line = self.say(r"Delete row 2 and column 3, and a 2 by 2 matrix remains.", line, hold=0.2)
        self.restyle([(entry, Palette.text, DIM if r == 1 or c == 2 else 1.0) for r, row in enumerate(entries_of(self.a_mat)) for c, entry in enumerate(row)])
        piece = named("A_{23}", grid(minor_of(A_ROWS, 1, 2))).move_to(RIGHT * 1.6 + UP * 1.9)
        sources = [entry for r, row in enumerate(entries_of(self.a_mat)) for c, entry in enumerate(row) if r != 1 and c != 2]
        self.play(
            *[TransformFromCopy(source, target) for source, target in zip(sources, piece[1].get_entries())],
            FadeIn(piece[1].get_brackets()),
            FadeIn(piece[0]),
            run_time=1.2,
            rate_func=spring_soft,
        )
        self.wait(Timing.beat)

        minor_value = MathTex(r"\det A_{23} = 2 \cdot (-2) - 2 \cdot 0 = -4", color=Palette.text, font_size=44)
        cofactor = MathTex(r"C_{23} = (-1)^{2+3} \det A_{23} = 4", color=Palette.text, font_size=44)
        VGroup(minor_value, cofactor).arrange(DOWN, buff=0.45, aligned_edge=LEFT).next_to(piece, DOWN, buff=0.55).align_to(piece, LEFT)
        line = self.say(r"Its determinant is called a \emph{minor}.", line, hold=0.2)
        self.play(Write(minor_value), run_time=1.2)
        self.wait(Timing.beat)
        line = self.say(r"The \emph{cofactor} $C_{23}$ gives that minor a sign.", line, hold=0.2)
        self.play(Write(cofactor), run_time=1.2)
        self.wait(Timing.read_short)

        line = self.say(r"The sign depends only on the position, like a checkerboard.", line, hold=0.2)
        self.restyle(rest_styles(self.a_mat, None), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(mark, scale=0.5) for mark in self.marks], lag_ratio=0.12), run_time=1.4)
        self.play(self.marks[5].animate.set_color(Palette.glow).scale(1.4), run_time=0.5, rate_func=spring_soft)
        self.wait(Timing.beat)
        self.marks[5].scale(1 / 1.4)
        self.dismiss(piece, minor_value, cofactor)
        self.play(self.marks[5].animate.set_color(Palette.text_muted), run_time=0.3)
        return line

    def expansion_term(self, expansion, i, j, total_part, diagonals=True, pace=1.0):
        """Pull one term out of A: the sign and entry, then the minor, then its cross product, then the term."""
        self.restyle(focus_styles(self.a_mat, self.marks, i, j), run_time=0.7 * pace)
        cells = entries_of(self.a_mat)
        extras = [] if expansion.entry is expansion.entry_core else [FadeIn(expansion.entry[0]), FadeIn(expansion.entry[2])]
        self.play(
            TransformFromCopy(self.marks[3 * i + j], expansion.sign),
            TransformFromCopy(cells[i][j], expansion.entry_core),
            *extras,
            run_time=0.8 * pace,
            rate_func=spring_soft,
        )
        sources = [cells[r][c] for r in range(3) for c in range(3) if r != i and c != j]
        self.play(
            *[TransformFromCopy(source, target) for source, target in zip(sources, expansion.minor.get_entries())],
            FadeIn(expansion.minor.get_brackets()),
            run_time=1.0 * pace,
            rate_func=spring_soft,
        )
        marks = expansion.diagonals()
        if diagonals:
            self.play(Create(marks[0]), run_time=0.5 * pace)
            self.play(Create(marks[1]), run_time=0.5 * pace)
        self.play(FadeIn(expansion.equals), FadeIn(expansion.cross, shift=LEFT * 0.15), run_time=0.7 * pace)
        self.wait(0.6 * pace)
        leaving = [FadeOut(marks)] if diagonals else []
        self.play(FadeTransform(expansion.cross, expansion.product), *leaving, run_time=0.8 * pace)
        self.play(FadeIn(expansion.equals_again), FadeIn(expansion.result, scale=0.7), run_time=0.6 * pace, rate_func=spring_soft)
        self.play(TransformFromCopy(expansion.result, total_part), run_time=0.8 * pace, rate_func=spring_soft)

    def expand_row_one(self, line):
        _, _, self.lines, self.total = centerpiece_layout()
        captions = [
            r"Cover its row and column, and a 2 by 2 minor remains.",
            r"Position $(1, 2)$ takes a minus sign from the checkerboard.",
            r"The last entry adds its own term the same way.",
        ]
        line = self.say(r"Expand along row 1: each entry times its cofactor.", line, hold=0.2)
        self.play(FadeIn(self.total[:3], shift=UP * 0.15), run_time=0.6)
        for j, (expansion, words) in enumerate(zip(self.lines, captions)):
            line = self.say(words, line, hold=0.1)
            self.expansion_term(expansion, 0, j, self.total[3 + j], diagonals=j == 0, pace=0.85)
            self.wait(0.4)
        line = self.say(r"The three terms add up to $\det A = 4$.", line, hold=0.2)
        self.restyle(rest_styles(self.a_mat, self.marks), run_time=0.5)
        self.play(FadeIn(self.total[-2:]), run_time=0.6)
        self.play(Indicate(self.total[-1], color=Palette.glow, scale_factor=1.3), run_time=0.9)
        self.wait(Timing.read_short)
        return line

    def zero_term(self, i, j, left, y, total_part):
        sign = MathTex("+" if sign_of(i, j) > 0 else "-", color=Palette.glow, font_size=44)
        zero = MathTex("0", color=Palette.yellow, font_size=44)
        rest = MathTex("=", "0", color=Palette.text, font_size=44)
        rest[1].set_color(Palette.teal)
        row = VGroup(sign, zero, rest).arrange(RIGHT, buff=0.2).move_to([left, y, 0], aligned_edge=LEFT)
        zero.next_to(sign, RIGHT, buff=0.08)
        self.restyle(focus_styles(self.a_mat, self.marks, i, j))
        self.play(
            TransformFromCopy(self.marks[3 * i + j], sign),
            TransformFromCopy(entries_of(self.a_mat)[i][j], zero),
            run_time=0.8,
            rate_func=spring_soft,
        )
        self.play(FadeIn(rest), run_time=0.5)
        self.play(FadeTransform(rest[1].copy(), total_part), run_time=0.8, rate_func=spring_soft)
        return VGroup(row)

    def expand_column_two(self, line):
        self.dismiss(*[expansion.group for expansion in self.lines])
        column_lines = [ExpansionLine(A_ROWS, i, 1, first=i == 0).place(LINES_LEFT, y) for i, y in zip((0, 2), (LINE_SLOTS[0], LINE_SLOTS[2]))]
        total = total_line("column 2:", ["2", "+0", "+2"], 4)
        total.move_to([0, TOTAL_SLOTS[1], 0])
        total.shift(RIGHT * (self.total[2].get_center()[0] - total[2].get_center()[0]))
        line = self.say(r"Any row or column gives the same number.", line, hold=0.2)
        column = [entries_of(self.a_mat)[r][1] for r in range(3)]
        self.restyle([(entry, Palette.yellow, 1.0) for entry in column] + [(self.marks[3 * r + 1], Palette.glow, 1.0) for r in range(3)], run_time=0.6)
        self.play(FadeIn(total[:3], shift=UP * 0.15), run_time=0.6)
        self.expansion_term(column_lines[0], 0, 1, total[3], diagonals=False, pace=0.7)
        line = self.say(r"A zero entry makes its whole term zero.", line, hold=0.1)
        zero_row = self.zero_term(1, 1, LINES_LEFT, LINE_SLOTS[1], total[4])
        line = self.say(r"A minus position times the entry $-2$ gives plus 2.", line, hold=0.1)
        self.expansion_term(column_lines[1], 2, 1, total[5], diagonals=False, pace=0.7)
        line = self.say(r"Pick the line with the most zeros to save work.", line, hold=0.2)
        self.restyle(rest_styles(self.a_mat, self.marks), run_time=0.5)
        self.play(FadeIn(total[-2:]), run_time=0.6)
        self.play(Indicate(total[-1], color=Palette.glow, scale_factor=1.3), Indicate(self.total[-1], color=Palette.glow, scale_factor=1.3), run_time=1.0)
        self.wait(Timing.beat)
        self.dismiss(self.a_group, self.marks, total, self.total, zero_row, *[expansion.group for expansion in column_lines])
        return line

    def triangular(self, line):
        u_group = named("U", grid(U_ROWS)).scale(MATRIX_SCALE).move_to(MATRIX_CENTER)
        u_mat = u_group[1]
        outline = cell_outline(u_mat, lower=True)
        head = MathTex(r"\det U", "=", color=Palette.text, font_size=44)
        top, top_core = entry_part(3)
        top.scale(44 / 48)
        minor = bars(minor_of(U_ROWS, 0, 0)).scale(0.82)
        tail = MathTex("=", r"3 \cdot 2 \cdot (-1)", "=", "-6", color=Palette.text, font_size=44)
        tail[3].set_color(Palette.teal)
        VGroup(head, top, minor, tail).arrange(RIGHT, buff=0.2).move_to([LINES_LEFT, MATRIX_CENTER[1], 0], aligned_edge=LEFT)
        top.next_to(head, RIGHT, buff=0.2)

        line = self.say(r"In a triangular matrix, every entry below the diagonal is 0.", line, hold=0.2)
        self.play(Write(u_group), run_time=1.2)
        self.play(Create(outline), run_time=1.0)

        line = self.say(r"Down column 1, only the top entry survives.", line, hold=0.2)
        self.restyle(focus_styles(u_mat, None, 0, 0))
        cells = entries_of(u_mat)
        self.play(FadeIn(head), TransformFromCopy(cells[0][0], top_core), run_time=0.8, rate_func=spring_soft)
        sources = [cells[r][c] for r in (1, 2) for c in (1, 2)]
        self.play(*[TransformFromCopy(source, target) for source, target in zip(sources, minor.get_entries())], FadeIn(minor.get_brackets()), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.beat)

        diagonal = VGroup(*[cells[k][k] for k in range(3)])
        self.restyle(rest_styles(u_mat, None) + [(entry, Palette.yellow, 1.0) for entry in diagonal], run_time=0.5)
        line = self.say(r"The minor is triangular too, so multiply down the diagonal.", line, hold=0.2)
        self.play(FadeIn(tail[:2]), run_time=0.8)
        self.play(FadeIn(tail[2:], shift=LEFT * 0.15), run_time=0.6)
        self.play(Indicate(diagonal, color=Palette.glow, scale_factor=1.2), Indicate(tail[3], color=Palette.glow), run_time=1.0)
        self.wait(Timing.read_short)
        self.dismiss(u_group, outline, head, top, minor, tail)
        return line

    def row_operation_panel(self):
        card = named("M", column_colored(M_ROWS)).to_corner(UL, buff=0.6)
        readout_anchor = card.get_corner(DL) + DOWN * 0.55
        rules = VGroup(*[MathTex(rf"{op}:\ \ {effect}", color=Palette.text, font_size=38) for _, op, effect in ROW_OPERATIONS])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(card, DOWN, buff=1.05).align_to(card, LEFT)
        sample = MathTex(r"\det M = -3.0", font_size=44).move_to(readout_anchor, aligned_edge=LEFT)
        plate = plate_for(VGroup(card, sample, rules))
        return card, readout_anchor, rules, plate

    def live_readout(self, anchor):
        def draw():
            value = float(np.linalg.det(self.live.value()))
            color = Palette.yellow if value >= -0.05 else Palette.pink
            return MathTex(rf"\det M = {number_text(value)}", color=color, font_size=44).move_to(anchor, aligned_edge=LEFT)

        return always_redraw(draw)

    def row_operations(self, plane, line):
        card, anchor, rules, plate = self.row_operation_panel()
        readout = self.live_readout(anchor)
        line = self.say(r"Row operations change $\det$ in three predictable ways.", line, hold=0.2)
        self.play(FadeOut(self.veil), run_time=0.8)
        self.play(FadeIn(plate), FadeIn(card, shift=UP * 0.15), FadeIn(readout), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.beat)
        rows = M_ROWS
        for (factor, _, _), rule, (doing, after) in zip(ROW_OPERATIONS, rules, ROW_OPERATION_CAPTIONS):
            line = self.say(doing, line, hold=0.2)
            rows = tuple(tuple(sum(factor[r][k] * rows[k][c] for k in range(2)) for c in range(2)) for r in range(2))
            target = column_colored(rows).move_to(card[1])
            morph_matrix(self, card[1], target, *self.live.left_multiply(factor), run_time=1.6, rate_func=spring_soft)
            self.play(FadeIn(rule, shift=RIGHT * 0.15), run_time=0.6)
            if after:
                line = self.say(after, line, hold=0.2)
            self.wait(Timing.beat)
        self.dismiss(plate, card, readout, rules)
        return line

    def reduce_to_triangular(self, line):
        self.veil = scrim()
        head = MathTex(r"\det B", "=", color=Palette.text, font_size=48)
        minus = MathTex("-", color=Palette.glow, font_size=48)
        b_mat = grid(B_STATES[0]).scale(MATRIX_SCALE)
        tail = MathTex("=", r"-(1 \cdot 1 \cdot 4)", "=", "-4", color=Palette.text, font_size=48)
        tail[3].set_color(Palette.teal)
        VGroup(head, minus, b_mat, tail).arrange(RIGHT, buff=0.22).move_to(UP * 0.5)
        label = MathTex(B_STEPS[0][0], color=Palette.text_muted, font_size=40).next_to(b_mat, DOWN, buff=0.45)

        line = self.say(r"So row reduce to a triangular matrix, tracking every change.", line, hold=0.2)
        self.play(FadeIn(self.veil), run_time=0.6)
        self.play(Write(head), Write(b_mat), run_time=1.2)
        for index, (op, words) in enumerate(B_STEPS):
            line = self.say(words, line, hold=0.1)
            new_label = MathTex(op, color=Palette.text_muted, font_size=40).move_to(label)
            if index:
                self.play(FadeOut(label), run_time=0.25)
            self.play(FadeIn(new_label, shift=DOWN * 0.15), run_time=0.4)
            label = new_label
            b_mat = self.swap_rows(b_mat, minus) if index == 0 else self.replace_rows(b_mat, index)
            self.wait(Timing.beat)

        line = self.say(r"Multiply the diagonal and keep the sign: $\det B = -4$.", line, hold=0.2)
        diagonal = VGroup(*[entries_of(b_mat)[k][k] for k in range(3)])
        self.restyle([(entry, Palette.yellow, 1.0) for entry in diagonal], run_time=0.5)
        self.play(FadeIn(tail[:2], shift=LEFT * 0.15), run_time=0.7)
        self.play(FadeIn(tail[2:], shift=LEFT * 0.15), run_time=0.6)
        self.play(Indicate(tail[3], color=Palette.glow, scale_factor=1.3), run_time=0.9)
        self.wait(Timing.read_short)
        self.dismiss(head, minus, b_mat, tail, label)
        return line

    def swap_rows(self, b_mat, minus):
        rows = b_mat.get_rows()
        first, second = rows[0].get_center(), rows[1].get_center()
        self.play(
            rows[0].animate(path_arc=-PI / 2).move_to(second),
            rows[1].animate(path_arc=-PI / 2).move_to(first),
            FadeIn(minus, scale=0.5),
            run_time=1.1,
            rate_func=spring_soft,
        )
        swapped = grid(B_STATES[1]).scale(MATRIX_SCALE).move_to(b_mat)
        self.drop(b_mat)
        self.add(swapped)
        return swapped

    def replace_rows(self, b_mat, index):
        target = grid(B_STATES[index + 1]).scale(MATRIX_SCALE).move_to(b_mat)
        morph_matrix(self, b_mat, target, run_time=1.0, rate_func=spring_soft)
        return b_mat

    def transpose_and_product(self, line):
        a_group = named("A", grid(A_ROWS)).scale(1.1).move_to(LEFT * 3.3 + UP * 0.9)
        t_group = named("A^{T}", grid(tuple(zip(*A_ROWS)))).scale(1.1).move_to(RIGHT * 3.3 + UP * 0.9)
        equal = MathTex(r"\det A^{T} = \det A = 4", color=Palette.text, font_size=48).move_to(DOWN * 1.6)
        line = self.say(r"Flipping $A$ over its diagonal gives its transpose $A^T$.", line, hold=0.2)
        self.play(FadeIn(a_group), run_time=0.6)
        a_cells, t_cells = entries_of(a_group[1]), entries_of(t_group[1])
        self.play(
            FadeIn(t_group[0]),
            FadeIn(t_group[1].get_brackets()),
            *[TransformFromCopy(a_cells[r][c], t_cells[c][r], path_arc=-PI / 3) for r in range(3) for c in range(3)],
            run_time=1.6,
            rate_func=spring_soft,
        )
        self.wait(Timing.beat)
        line = self.say(r"Rows of $A^T$ are columns of $A$, so $\det A^T = \det A$.", line, hold=0.2)
        self.restyle([(a_cells[r][1], Palette.yellow, 1.0) for r in range(3)] + [(entry, Palette.yellow, 1.0) for entry in t_cells[1]], run_time=0.6)
        self.play(Write(equal), run_time=1.0)
        self.wait(Timing.beat)
        self.dismiss(a_group, t_group, equal)
        return self.product_rule(line)

    def product_rule(self, line):
        names = ("M", "N", "MN")
        values = (3, 2, 6)
        cards = VGroup(*[named(name, grid(rows)) for name, rows in zip(names, (M_ROWS, N_ROWS, MN_ROWS))])
        cards.arrange(RIGHT, buff=1.2).move_to(UP * 1.0)
        dets = VGroup(*[MathTex(rf"\det {name} = {value}", color=Palette.text, font_size=44) for name, value in zip(names, values)])
        for det_line, card in zip(dets, cards):
            det_line.next_to(card, DOWN, buff=0.5)
        dets[2].set_color(Palette.teal)
        rule = MathTex(r"\det MN = (\det M)(\det N) = 3 \cdot 2", color=Palette.text, font_size=48).move_to(DOWN * 1.9)
        line = self.say(r"$N$ scales area by 2, then $M$ scales it by 3.", line, hold=0.2)
        self.play(LaggedStart(*[FadeIn(VGroup(card, det_line), shift=UP * 0.15) for card, det_line in zip(cards, dets)], lag_ratio=0.3), run_time=1.6)
        self.wait(Timing.beat)
        line = self.say(r"So $\det MN = \det M \det N$ for any square $M$ and $N$.", line, hold=0.2)
        self.play(Write(rule), run_time=1.2)
        self.play(Indicate(dets[2], color=Palette.glow, scale_factor=1.15), run_time=0.9)
        self.wait(Timing.read_short)
        return line


class FigCheckerboard(Scene):
    def construct(self):
        a_group = named("A", roomy(grid(A_ROWS))).scale(MATRIX_SCALE)
        marks = sign_marks(a_group[1])
        for r, row in enumerate(entries_of(a_group[1])):
            for c, entry in enumerate(row):
                entry.set_opacity(DIM if r == 1 or c == 2 else 1.0)
        marks[5].set_color(Palette.glow).scale(1.4)
        piece = named("A_{23}", grid(minor_of(A_ROWS, 1, 2)))
        piece[1].get_entries().set_color(Palette.blue)
        minor_value = MathTex(r"\det A_{23} = 2 \cdot (-2) - 2 \cdot 0 = -4", color=Palette.text, font_size=44)
        cofactor = MathTex(r"C_{23} = (-1)^{2+3} \det A_{23} = 4", color=Palette.text, font_size=44)
        right = VGroup(piece, minor_value, cofactor).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        VGroup(VGroup(a_group, marks), right).arrange(RIGHT, buff=1.2)
        self.add(a_group, marks, right)
        fit_to_frame(self, margin=0.5)


class FigExpansion(Scene):
    def construct(self):
        a_group, marks, lines, total = centerpiece_layout()
        for mark in marks[:3]:
            mark.set_color(Palette.glow)
        for entry in entries_of(a_group[1])[0]:
            entry.set_color(Palette.yellow)
        self.add(a_group, marks, *[expansion.group for expansion in lines], total)
        fit_to_frame(self, margin=0.4)


def small_panel(rows, label):
    plane = make_plane(x_range=(-3, 4, 1), y_range=(-2, 4, 1), x_length=3.5, y_length=3.0)
    plane.background_lines.set_stroke(opacity=0.3)
    plane.faded_lines.set_stroke(opacity=0.2)
    columns = ((rows[0][0], rows[1][0]), (rows[0][1], rows[1][1]))
    shape = parallelogram(plane, columns, opacity=0.35)
    arrows = VGroup(*[vector_arrow(column, color, plane, stroke_width=4) for column, color in zip(columns, (Palette.i_hat, Palette.j_hat))])
    value = det2(rows)
    caption = VGroup(column_colored(rows).scale(0.7), MathTex(rf"\det = {value}", color=Palette.yellow if value > 0 else Palette.pink, font_size=36))
    caption.arrange(DOWN, buff=0.2)
    return VGroup(VGroup(plane, shape, arrows), caption, MathTex(label, color=Palette.text_muted, font_size=32)).arrange(DOWN, buff=0.3)


class FigRowOperations(Scene):
    def construct(self):
        rows = M_ROWS
        panels = VGroup(small_panel(rows, r"M"))
        for factor, op, _ in ROW_OPERATIONS:
            rows = tuple(tuple(sum(factor[r][k] * rows[k][c] for k in range(2)) for c in range(2)) for r in range(2))
            panels.add(small_panel(rows, op))
        panels.arrange(RIGHT, buff=0.7, aligned_edge=UP)
        self.add(panels)
        fit_to_frame(self, margin=0.4)


class Poster(Scene):
    def construct(self):
        a_group, marks, lines, total = centerpiece_layout()
        apply_styles(focus_styles(a_group[1], marks, 0, 1))
        second = lines[1]
        partial = VGroup(second.sign, second.entry, second.minor)
        self.add(a_group, marks, lines[0].group, partial, second.diagonals(), total[:4])
        fit_to_frame(self, margin=0.7)
