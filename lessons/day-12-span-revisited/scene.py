import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from manim import *  # noqa: E402,F403

from engine.theme import (  # noqa: E402
    LessonScene3D,
    Palette,
    Timing,
    backed,
    fit_to_frame,
    morph_matrix,
    plate_for,
    span_sheet,
    spring,
    spring_soft,
    vector_arrow_3d,
)

U = np.array([2, -1, 1])
V = np.array([1, 2, 1])
W_IN = U + 2 * V
W_OFF_ENTRY = -1
W_OFF = np.array([W_IN[0], W_IN[1], W_OFF_ENTRY])
SHEET_S = (-1.2, 1.6)
SHEET_T = (-1.0, 2.3)
STACK_WEIGHTS = (-0.75, -0.5, -0.25, 0.25, 0.5, 0.75)

COLUMN_COLORS = (Palette.yellow, Palette.blue, Palette.pink)
MATRIX_IN = [[2, 1, 4], [-1, 2, 3], [1, 1, 3]]
ECHELON_IN = [[2, 1, 4], [0, 5, 10], [0, 0, 0]]
MATRIX_OFF = [[2, 1, 4], [-1, 2, 3], [1, 1, -1]]
ECHELON_OFF = [[2, 1, 4], [0, 5, 10], [0, 0, -40]]
MATRIX_UV = [[2, 1], [-1, 2], [1, 1]]
ECHELON_UV = [[2, 1], [0, 5], [0, 0]]

POLYNOMIALS = (
    (("1", "+", "t"), (1, 1, 0)),
    (("t", "+", "t^2"), (0, 1, 1)),
    (("1", "+", "t^2"), (1, 0, 1)),
)
POLY_ECHELON = [[1, 0, 1], [0, 1, -1], [0, 0, 2]]
FULL_PIVOTS = ((0, 0), (1, 1), (2, 2))
PLANE_PIVOTS = ((0, 0), (1, 1))


def make_axes_3d():
    return ThreeDAxes(
        x_range=(-6, 6, 1),
        y_range=(-6, 6, 1),
        z_range=(-4, 5, 1),
        x_length=6,
        y_length=6,
        z_length=4.5,
        axis_config={"stroke_color": Palette.axis, "stroke_width": 2, "include_tip": False, "tick_size": 0.04},
    )


def sheet_at(axes, extent=1.0, opacity=0.32):
    s_range = (SHEET_S[0] * extent, SHEET_S[1] * extent)
    t_range = (SHEET_T[0] * extent, SHEET_T[1] * extent)
    return span_sheet(axes, U, V, s_range, t_range, resolution=(7, 8), opacity=opacity)


def multiples_line(axes, direction, color, reach=1.9):
    return Line(axes.c2p(*(-reach * direction)), axes.c2p(*(reach * direction)), color=color, stroke_width=3, stroke_opacity=0.8)


def stacked_sheets(axes):
    """Copies of the span sheet slid along the off-plane w, one per weight in STACK_WEIGHTS."""
    sheets = VGroup()
    for weight in STACK_WEIGHTS:
        sheet = sheet_at(axes, 0.8, opacity=0.14)
        sheet.shift(axes.c2p(*(weight * W_OFF)) - axes.c2p(0, 0, 0))
        sheets.add(sheet)
    return sheets


def spaced_matrix(rows):
    return Matrix([[str(entry) for entry in row] for row in rows], v_buff=0.62, h_buff=1.15, bracket_h_buff=0.14).set_color(Palette.text)


def coloured_matrix(rows, colors=COLUMN_COLORS, scale=0.78):
    mat = spaced_matrix(rows)
    for index, col in enumerate(mat.get_columns()):
        col.set_color(colors[index % len(colors)])
    return mat.scale(scale)


def plain_matrix(rows, scale=0.78):
    return spaced_matrix(rows).scale(scale)


def pivot_rings(mat, cells):
    rows = mat.get_rows()
    return VGroup(
        *[
            Ellipse(width=max(0.42, rows[r][c].width + 0.2), height=0.42, color=Palette.glow, stroke_width=3.5).move_to(rows[r][c])
            for r, c in cells
        ]
    )


def empty_row_outline(mat, row_index):
    row = mat.get_rows()[row_index]
    outline = DashedVMobject(
        Rectangle(width=row.width + 0.3, height=row.height + 0.16),
        num_dashes=40,
    )
    return outline.set_stroke(Palette.text_muted, width=2.5).move_to(row)


def reduction_row(start_rows, end_rows, scale=0.78):
    start = coloured_matrix(start_rows, scale=scale)
    tilde = MathTex(r"\sim", font_size=48, color=Palette.text)
    end = plain_matrix(end_rows, scale=scale)
    return VGroup(start, tilde, end).arrange(RIGHT, buff=0.45)


def panel_line(tex, color=Palette.text):
    return MathTex(tex, color=color, font_size=38)


class Lesson(LessonScene3D):
    day = 12
    title = "Span as the smallest subspace"

    def construct(self):
        pulse = self.open_episode()
        axes = make_axes_3d()
        self.move_camera(phi=66 * DEGREES, theta=-115 * DEGREES, zoom=1.0, added_anims=[Create(axes), FadeOut(pulse)], run_time=2.4)
        self.begin_ambient_camera_rotation(rate=-0.01)
        line, sheet = self.plane_recap(axes)
        line, sheet = self.smallest_subspace(axes, line, sheet)
        line, w_parts = self.redundant_vector(axes, line, sheet)
        line = self.new_direction(axes, line, sheet, w_parts)
        line = self.flatten(line)
        line = self.pivot_cases(line)
        line = self.pivot_theorem(line)
        line = self.polynomials(line)
        self.close_episode(
            r"The span of some vectors is the smallest subspace holding them.\\"
            r"They span $\mathbb{R}^m$ exactly when every row has a pivot.",
            *[m for m in self.mobjects if isinstance(m, VMobject)],
        )

    def tag_3d(self, axes, tex, color, point, push=1.18):
        tag = backed(MathTex(tex, color=color, font_size=40), padding=0.07).move_to(axes.c2p(*(np.array(point) * push)) + OUT * 0.25)
        self.add_fixed_orientation_mobjects(tag)
        self.remove(tag)
        return tag

    def plane_recap(self, axes):
        u_arrow = vector_arrow_3d(axes, U, Palette.yellow)
        v_arrow = vector_arrow_3d(axes, V, Palette.blue)
        self.u_tag = self.tag_3d(axes, r"\mathbf u", Palette.yellow, U)
        self.v_tag = self.tag_3d(axes, r"\mathbf v", Palette.blue, V)
        line = self.say(r"On Day 2, $\mathbf u$ and $\mathbf v$ spanned this plane.", hold=0.2)
        self.sfx("whoosh", gain=-2)
        self.play(
            GrowFromPoint(u_arrow, axes.c2p(0, 0, 0)),
            GrowFromPoint(v_arrow, axes.c2p(0, 0, 0)),
            FadeIn(self.u_tag),
            FadeIn(self.v_tag),
            run_time=1.2,
            rate_func=spring_soft,
        )
        extent = ValueTracker(0.02)
        growing = always_redraw(lambda: sheet_at(axes, extent.get_value()))
        self.add(growing)
        self.sfx("sweep", gain=-3)
        self.play(extent.animate.set_value(1.0), run_time=3.0, rate_func=smooth)
        sheet = sheet_at(axes)
        self.remove(growing)
        self.add(sheet)
        self.wait(Timing.beat)
        line = self.say(r"Day 11 showed that every span is a subspace.", line)
        return line, sheet

    def smallest_subspace(self, axes, line, sheet):
        line = self.say(r"Now take any subspace $H$ that holds $\mathbf u$ and $\mathbf v$.", line, hold=0.2)
        self.play(FadeOut(sheet), run_time=0.8)
        self.wait(Timing.read_short)

        steps = [
            panel_line(r"c\,\mathbf u \text{ and } d\,\mathbf v \text{ are in } H"),
            panel_line(r"c\,\mathbf u + d\,\mathbf v \text{ is in } H"),
            panel_line(r"\operatorname{Span}\{\mathbf u, \mathbf v\} \subseteq H", Palette.glow),
        ]
        stack = VGroup(*steps).arrange(DOWN, buff=0.3, aligned_edge=LEFT).to_corner(UL, buff=0.6)
        plate = plate_for(stack)
        self.add_fixed_in_frame_mobjects(plate, *steps)
        self.remove(plate, *steps)

        lines = VGroup(multiples_line(axes, U, Palette.yellow), multiples_line(axes, V, Palette.blue))
        line = self.say(r"Closed under scaling, $H$ holds every $c\mathbf u$ and $d\mathbf v$.", line, hold=0.2)
        self.play(Create(lines), FadeIn(plate), FadeIn(steps[0], shift=DOWN * 0.1), run_time=1.6)
        self.wait(Timing.read_short)

        extent = ValueTracker(0.02)
        growing = always_redraw(lambda: sheet_at(axes, extent.get_value()))
        line = self.say(r"Closed under addition, it holds every sum $c\mathbf u + d\mathbf v$.", line, hold=0.2)
        self.add(growing)
        self.sfx("sweep", gain=-3)
        self.play(extent.animate.set_value(1.0), FadeIn(steps[1], shift=DOWN * 0.1), run_time=2.6, rate_func=smooth)
        sheet = sheet_at(axes)
        self.remove(growing)
        self.add(sheet)
        self.wait(Timing.read_short)

        line = self.say(r"So every such $H$ contains the whole span.", line, hold=0.2)
        self.play(FadeIn(steps[2], shift=DOWN * 0.1), run_time=0.8, rate_func=spring_soft)
        self.play(Indicate(steps[2], color=Palette.glow, scale_factor=1.1), run_time=1.0)
        self.wait(Timing.read_short)
        line = self.say(r"The span is the smallest subspace holding $\mathbf u$ and $\mathbf v$.", line, hold=Timing.read_long)
        line = self.say(r"$\{\mathbf u, \mathbf v\}$ is a spanning set, a recipe for this plane.", line, hold=0.2)
        self.play(FadeOut(VGroup(plate, *steps)), FadeOut(lines), run_time=0.8)
        self.wait(Timing.read_short)
        return line, sheet

    def redundant_vector(self, axes, line, sheet):
        w_arrow = vector_arrow_3d(axes, W_IN, Palette.pink)
        w_tag = self.tag_3d(axes, r"\mathbf w", Palette.pink, W_IN, push=1.1)
        line = self.say(r"Add Day 2's $(4, 3, 3)$ as a third vector $\mathbf w$.", line, hold=0.2)
        self.sfx("whoosh", gain=-2)
        self.play(GrowFromPoint(w_arrow, axes.c2p(0, 0, 0)), FadeIn(w_tag), run_time=1.2, rate_func=spring_soft)
        self.wait(Timing.beat)

        line = self.say(r"It lies in the plane, because $\mathbf w = \mathbf u + 2\mathbf v$.", line, hold=0.2)
        step = vector_arrow_3d(axes, W_IN, Palette.blue, start=U)
        self.sfx("whoosh", gain=-2)
        self.play(GrowFromPoint(step, axes.c2p(*U)), run_time=1.4, rate_func=spring_soft)
        stamp = Dot3D(axes.c2p(*W_IN), radius=0.08, color=Palette.glow)
        self.play(GrowFromCenter(stamp), run_time=0.5, rate_func=spring)
        self.wait(Timing.read_short)
        self.play(FadeOut(step), FadeOut(stamp), run_time=0.5)

        fold = MathTex(
            r"c_1", r"\mathbf u", r"+ c_2", r"\mathbf v", r"+ c_3", r"\mathbf w",
            r"= (c_1 + c_3)", r"\mathbf u", r"+ (c_2 + 2c_3)", r"\mathbf v",
            font_size=38,
        )
        for index, color in ((1, Palette.yellow), (3, Palette.blue), (5, Palette.pink), (7, Palette.yellow), (9, Palette.blue)):
            fold[index].set_color(color)
        fold_panel = backed(fold, padding=0.22).to_corner(UL, buff=0.45)
        self.pin(fold_panel)
        self.remove(fold_panel)
        line = self.say(r"Any combination using $\mathbf w$ folds back into $\mathbf u$ and $\mathbf v$.", line, hold=0.2)
        self.play(FadeIn(fold_panel, shift=DOWN * 0.1), run_time=0.9, rate_func=spring_soft)
        self.wait(Timing.read_long)

        line = self.say(r"So this $\mathbf w$ is redundant, and the span stays put.", line, hold=0.2)
        self.play(sheet.animate(rate_func=there_and_back).set_fill(opacity=0.6), run_time=1.2)
        self.wait(Timing.read_short)
        self.play(FadeOut(fold_panel), run_time=0.5)
        return line, (w_arrow, w_tag)

    def new_direction(self, axes, line, sheet, w_parts):
        w_arrow, w_tag = w_parts
        last_entry = ValueTracker(W_IN[2])
        live_w = always_redraw(lambda: vector_arrow_3d(axes, (W_IN[0], W_IN[1], last_entry.get_value()), Palette.pink))
        gap = always_redraw(
            lambda: DashedLine(axes.c2p(*W_IN), axes.c2p(W_IN[0], W_IN[1], last_entry.get_value()), color=Palette.glow, stroke_width=4)
        )
        line = self.say(r"Now change its last entry to $-1$.", line, hold=0.2)
        self.play(FadeOut(w_tag), run_time=0.3)
        self.remove(w_arrow)
        self.add(live_w, gap)
        self.play(last_entry.animate.set_value(W_OFF_ENTRY), run_time=2.0, rate_func=spring_soft)
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=78 * DEGREES, theta=-303 * DEGREES, run_time=2.4, rate_func=smooth)
        new_tag = self.tag_3d(axes, r"\mathbf w", Palette.pink, W_OFF, push=1.12)
        self.play(FadeIn(new_tag), run_time=0.4)
        self.wait(Timing.beat)

        stack = stacked_sheets(axes)
        sliding = VGroup(*[sheet_at(axes, 0.8, opacity=0.14) for _ in STACK_WEIGHTS])
        line = self.say(r"Adding $c_3\mathbf w$ slides the whole plane along $\mathbf w$.", line, hold=0.2)
        self.add(*sliding)
        self.sfx("sweep", gain=-3)
        self.play(
            *[Transform(moving, target) for moving, target in zip(sliding, stack)],
            run_time=3.2,
            rate_func=spring_soft,
        )
        self.wait(Timing.read_short)
        line = self.say(r"The slid planes stack up and fill all of space.", line, hold=0.2)
        self.begin_ambient_camera_rotation(rate=-0.05)
        self.wait(Timing.read_long)
        line = self.say(r"One new direction grows the span from a plane to $\mathbb R^3$.", line, hold=0.2)
        self.play(LaggedStart(*[piece.animate(rate_func=there_and_back).set_fill(opacity=0.4) for piece in sliding], lag_ratio=0.15), run_time=1.8)
        self.wait(Timing.read_short)
        self.stop_ambient_camera_rotation()
        return line

    def flatten(self, line):
        for mobject in self.mobjects:
            mobject.clear_updaters()
        leaving = [m for m in self.mobjects if not isinstance(m, ValueTracker) and m is not line]
        self.play(*[FadeOut(m) for m in leaving], run_time=0.8)
        self.remove(*leaving)
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1)
        return line

    def pivot_cases(self, line):
        top = reduction_row(MATRIX_IN, ECHELON_IN).move_to(UP * 1.3 + LEFT * 1.2)
        bottom = reduction_row(MATRIX_OFF, ECHELON_OFF).move_to(DOWN * 1.35 + LEFT * 1.2)
        bottom.align_to(top, LEFT)
        header = VGroup(*[MathTex(tex, color=color, font_size=38) for tex, color in zip((r"\mathbf u", r"\mathbf v", r"\mathbf w"), COLUMN_COLORS)])
        for tag, col in zip(header, top[0].get_columns()):
            tag.next_to(top[0], UP, buff=0.2).set_x(col.get_center()[0])

        line = self.say(r"Row reduction tells the two cases apart.", line, hold=0.2)
        self.play(FadeIn(top[0]), FadeIn(header), run_time=1.0)
        self.wait(Timing.beat)
        line = self.say(r"With $\mathbf w = (4, 3, 3)$, the third row becomes all zeros.", line, hold=0.2)
        self.play(FadeIn(top[1]), FadeTransform(top[0].copy(), top[2]), run_time=1.4)
        top_rings = pivot_rings(top[2], PLANE_PIVOTS)
        zero_row = empty_row_outline(top[2], 2)
        self.play(Create(top_rings), run_time=0.9)
        self.play(Create(zero_row), run_time=0.8)
        top_result = Tex(r"a plane", color=Palette.teal, font_size=40).next_to(top[2], RIGHT, buff=0.5)
        self.play(FadeIn(top_result, shift=LEFT * 0.15), run_time=0.6)
        self.wait(Timing.read_short)

        line = self.say(r"With $\mathbf w = (4, 3, -1)$, every row gets a pivot.", line, hold=0.2)
        moving = top[0].copy()
        self.add(moving)
        morph_matrix(self, moving, bottom[0], run_time=1.2, rate_func=spring)
        self.play(Indicate(moving.get_rows()[2][2], color=Palette.glow, scale_factor=1.4), run_time=0.8)
        self.play(FadeIn(bottom[1]), FadeTransform(moving.copy(), bottom[2]), run_time=1.4)
        bottom_rings = pivot_rings(bottom[2], FULL_PIVOTS)
        self.play(Create(bottom_rings), run_time=1.0)
        bottom_result = MathTex(r"\mathbb R^3", color=Palette.teal, font_size=44).next_to(bottom[2], RIGHT, buff=0.5)
        bottom_result.align_to(top_result, LEFT)
        self.play(FadeIn(bottom_result, shift=LEFT * 0.15), run_time=0.6)
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(top, moving, bottom[1:], header, top_rings, zero_row, top_result, bottom_rings, bottom_result)), run_time=0.7)
        return line

    def pivot_theorem(self, line):
        statement = MathTex(
            r"\text{columns of } A \text{ span } \mathbb R^m",
            r"\iff",
            r"A \text{ has a pivot in every row}",
            font_size=44,
            color=Palette.text,
        ).move_to(UP * 2.2)
        statement[1].set_color(Palette.glow)
        line = self.say(r"The columns span $\mathbb R^m$ exactly when every row has a pivot.", line, hold=0.2)
        self.play(FadeIn(statement, shift=UP * 0.15), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_long)

        pair = reduction_row(MATRIX_UV, ECHELON_UV).move_to(DOWN * 0.5)
        header = VGroup(*[MathTex(tex, color=color, font_size=38) for tex, color in zip((r"\mathbf u", r"\mathbf v"), COLUMN_COLORS)])
        for tag, col in zip(header, pair[0].get_columns()):
            tag.next_to(pair[0], UP, buff=0.2).set_x(col.get_center()[0])
        line = self.say(r"Two vectors give at most two pivots, one per column.", line, hold=0.2)
        self.play(FadeIn(pair[0]), FadeIn(header), run_time=0.9)
        self.play(FadeIn(pair[1]), FadeTransform(pair[0].copy(), pair[2]), run_time=1.3)
        rings = pivot_rings(pair[2], PLANE_PIVOTS)
        empty = empty_row_outline(pair[2], 2)
        self.play(Create(rings), run_time=0.8)
        self.play(Create(empty), run_time=0.8)
        self.wait(Timing.read_short)
        line = self.say(r"So two vectors can never span all of $\mathbb R^3$.", line, hold=Timing.read_long)
        self.play(FadeOut(VGroup(statement, pair, header, rings, empty)), run_time=0.7)
        return line

    def polynomials(self, line):
        formulas = VGroup(
            *[
                MathTex(rf"\mathbf p_{index + 1}", "=", *terms, color=color, font_size=42)
                for index, ((terms, _), color) in enumerate(zip(POLYNOMIALS, COLUMN_COLORS))
            ]
        ).arrange(RIGHT, buff=1.0).move_to(UP * 2.6)
        for formula in formulas:
            formula[1].set_color(Palette.text)
        line = self.say(r"Polynomials in $\mathbb P_2$ work the same way.", line, hold=0.2)
        self.play(LaggedStart(*[FadeIn(formula, shift=DOWN * 0.1) for formula in formulas], lag_ratio=0.3), run_time=1.6)
        self.wait(Timing.beat)

        coefficients = coloured_matrix([[coeffs[row] for _, coeffs in POLYNOMIALS] for row in range(3)], scale=0.85)
        coefficients.move_to(DOWN * 0.7 + LEFT * 1.8)
        row_names = VGroup(*[MathTex(tex, color=Palette.text_muted, font_size=36) for tex in ("1", "t", "t^2")])
        for name, row in zip(row_names, coefficients.get_rows()):
            name.next_to(coefficients, LEFT, buff=0.35).set_y(row.get_center()[1])
        line = self.say(r"List the coefficients of $1$, $t$ and $t^2$ as columns.", line, hold=0.2)
        self.play(FadeIn(coefficients.get_brackets()), FadeIn(row_names), run_time=0.6)
        for index, formula in enumerate(formulas):
            self.play(Indicate(formula, color=Palette.glow, scale_factor=1.08), run_time=0.6)
            self.play(FadeTransform(formula[2:].copy(), coefficients.get_columns()[index]), run_time=0.9)
        self.wait(Timing.beat)

        tilde = MathTex(r"\sim", font_size=48).next_to(coefficients, RIGHT, buff=0.45)
        echelon = plain_matrix(POLY_ECHELON, scale=0.85).next_to(tilde, RIGHT, buff=0.45)
        line = self.say(r"Every row has a pivot, so these three span $\mathbb P_2$.", line, hold=0.2)
        self.play(FadeIn(tilde), FadeTransform(coefficients.copy(), echelon), run_time=1.4)
        self.play(Create(pivot_rings(echelon, FULL_PIVOTS)), run_time=1.0)
        self.wait(Timing.read_long)
        return line


def space_camera(scene, phi=70, theta=-100, zoom=1.45):
    scene.set_camera_orientation(phi=phi * DEGREES, theta=theta * DEGREES, zoom=zoom)


def fixed_tag(scene, axes, tex, color, point, direction=OUT):
    tag = backed(MathTex(tex, color=color, font_size=36), padding=0.06).move_to(axes.c2p(*point) + direction * 0.3)
    scene.add_fixed_orientation_mobjects(tag)
    return tag


class FigRedundantVector(ThreeDScene):
    def construct(self):
        axes = make_axes_3d()
        space_camera(self, phi=70, theta=-100)
        self.add(axes, sheet_at(axes))
        self.add(vector_arrow_3d(axes, U, Palette.yellow), vector_arrow_3d(axes, V, Palette.blue))
        self.add(vector_arrow_3d(axes, W_IN, Palette.blue, start=U), vector_arrow_3d(axes, W_IN, Palette.pink))
        self.add(Dot3D(axes.c2p(*W_IN), radius=0.08, color=Palette.glow))
        fixed_tag(self, axes, r"\mathbf u", Palette.yellow, U * 1.2)
        fixed_tag(self, axes, r"\mathbf v", Palette.blue, V * 1.25)
        fixed_tag(self, axes, r"2\mathbf v", Palette.blue, U + V + np.array([0.6, 0, 0]))
        fixed_tag(self, axes, r"\mathbf w = \mathbf u + 2\mathbf v", Palette.pink, W_IN * 1.08)


class FigNewDirection(ThreeDScene):
    def construct(self):
        axes = make_axes_3d()
        space_camera(self, phi=78, theta=57, zoom=1.3)
        self.add(axes, sheet_at(axes), stacked_sheets(axes))
        self.add(vector_arrow_3d(axes, U, Palette.yellow), vector_arrow_3d(axes, V, Palette.blue), vector_arrow_3d(axes, W_OFF, Palette.pink))
        self.add(DashedLine(axes.c2p(*W_IN), axes.c2p(*W_OFF), color=Palette.glow, stroke_width=4))
        fixed_tag(self, axes, r"\mathbf u", Palette.yellow, U * 1.2)
        fixed_tag(self, axes, r"\mathbf v", Palette.blue, V * 1.25)
        fixed_tag(self, axes, r"\mathbf w = (4, 3, -1)", Palette.pink, W_OFF * 1.1, IN)


class FigPivotRows(Scene):
    def construct(self):
        top = reduction_row(MATRIX_IN, ECHELON_IN)
        bottom = reduction_row(MATRIX_OFF, ECHELON_OFF)
        rows = VGroup(top, bottom).arrange(DOWN, buff=0.8, aligned_edge=LEFT)
        top_result = Tex(r"a plane", color=Palette.teal, font_size=40).next_to(top[2], RIGHT, buff=0.5)
        bottom_result = MathTex(r"\mathbb R^3", color=Palette.teal, font_size=44).next_to(bottom[2], RIGHT, buff=0.5).align_to(top_result, LEFT)
        self.add(rows, pivot_rings(top[2], PLANE_PIVOTS), empty_row_outline(top[2], 2), pivot_rings(bottom[2], FULL_PIVOTS))
        self.add(top_result, bottom_result)
        fit_to_frame(self, margin=0.6)


class Poster(ThreeDScene):
    def construct(self):
        axes = make_axes_3d()
        space_camera(self, phi=74, theta=62, zoom=1.45)
        self.add(axes, sheet_at(axes, opacity=0.4), stacked_sheets(axes))
        self.add(vector_arrow_3d(axes, U, Palette.yellow), vector_arrow_3d(axes, V, Palette.blue), vector_arrow_3d(axes, W_OFF, Palette.pink))
        self.add(DashedLine(axes.c2p(*W_IN), axes.c2p(*W_OFF), color=Palette.glow, stroke_width=4))
