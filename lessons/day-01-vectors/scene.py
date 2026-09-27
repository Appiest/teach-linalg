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
    slider,
    spring,
    spring_soft,
    vector_arrow,
)

V = (3, 2)
W = (-1, 2)


def walk_guides(plane, coords):
    run = DashedLine(plane.c2p(0, 0), plane.c2p(coords[0], 0), color=Palette.i_hat, stroke_width=4)
    rise = DashedLine(plane.c2p(coords[0], 0), plane.c2p(*coords), color=Palette.j_hat, stroke_width=4)
    run_label = backed(Tex(f"{coords[0]} right", color=Palette.i_hat, font_size=34)).next_to(run, DOWN, buff=0.15)
    rise_label = backed(Tex(f"{coords[1]} up", color=Palette.j_hat, font_size=34)).next_to(rise, RIGHT, buff=0.15)
    return run, rise, run_label, rise_label


def colored_column(entries):
    col = column(entries)
    col.get_entries()[0].set_color(Palette.i_hat)
    col.get_entries()[1].set_color(Palette.j_hat)
    return col


class Lesson(LessonScene):
    day = 1
    title = "Vectors"

    def construct(self):
        plane = make_plane()
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        v_arrow, line = self.arrow_is_a_list(plane)
        line = self.addition(plane, v_arrow, line)
        line = self.scaling(plane, v_arrow, line)
        line = self.combinations(plane, line)
        self.close_episode(
            r"A vector is an arrow and a list of numbers at once.\\"
            r"Adding and scaling mean the same thing in both pictures.",
            *self.mobjects,
        )

    def arrow_is_a_list(self, plane):
        v_arrow = vector_arrow(V, Palette.yellow, plane)
        line = self.say(r"A vector is an arrow that starts at the origin.", hold=0.2)
        self.play(GrowArrow(v_arrow), run_time=1.4, rate_func=spring_soft)
        self.wait(Timing.read_short)

        run, rise, run_label, rise_label = walk_guides(plane, V)
        line = self.say(r"Its coordinates tell you how to walk to its tip.", line, hold=0.2)
        self.play(Create(run), FadeIn(run_label), run_time=1.2)
        self.play(Create(rise), FadeIn(rise_label), run_time=1.2)
        self.wait(Timing.read_short)

        col = backed(colored_column(V)).next_to(plane.c2p(*V), UR, buff=0.25)
        line = self.say(r"So the same vector is also a list of numbers.", line, hold=0.2)
        self.play(
            TransformFromCopy(run_label, col.get_entries()[0]),
            TransformFromCopy(rise_label, col.get_entries()[1]),
            FadeIn(col.get_brackets()),
            FadeIn(col.background_rectangle),
            run_time=1.4,
        )
        self.wait(Timing.read_long)
        self.play(FadeOut(VGroup(run, rise, run_label, rise_label, col)), run_time=0.6)
        return v_arrow, line

    def addition(self, plane, v_arrow, line):
        w_arrow = vector_arrow(W, Palette.blue, plane)
        v_name = backed(MathTex(r"\vec v", color=Palette.yellow)).next_to(plane.c2p(*V), RIGHT, buff=0.15)
        w_name = backed(MathTex(r"\vec w", color=Palette.blue)).next_to(plane.c2p(*W), LEFT, buff=0.15)
        line = self.say(r"Here is a second vector, $\vec w$.", line, hold=0.2)
        self.play(FadeIn(v_name), GrowArrow(w_arrow), FadeIn(w_name), run_time=1.2, rate_func=spring_soft)
        self.wait(Timing.beat)

        line = self.say(r"To add them, slide $\vec w$ so it starts where $\vec v$ ends.", line, hold=0.2)
        moved_w = w_arrow.copy()
        self.add(moved_w)
        self.play(moved_w.animate.shift(plane.c2p(*V) - plane.c2p(0, 0)), run_time=1.6, rate_func=spring)
        self.wait(Timing.beat)

        total = (V[0] + W[0], V[1] + W[1])
        sum_arrow = vector_arrow(total, Palette.teal, plane)
        sum_name = backed(MathTex(r"\vec v + \vec w", color=Palette.teal)).next_to(plane.c2p(*total), UP, buff=0.15)
        line = self.say(r"The sum is the arrow from the origin to where you ended up.", line, hold=0.2)
        self.play(GrowArrow(sum_arrow), FadeIn(sum_name), run_time=1.3, rate_func=spring_soft)
        self.wait(Timing.read_short)

        line = self.say(r"In the list picture, you add entry by entry.", line, hold=0.2)
        self.entrywise_sum(total)
        self.play(FadeOut(VGroup(w_arrow, moved_w, w_name, sum_arrow, sum_name, v_name)), run_time=0.7)
        return line

    def entrywise_sum(self, total):
        v_col = column(V, color=Palette.yellow)
        w_col = column(W, color=Palette.blue)
        answer = column([total[0], total[1]], color=Palette.teal)
        symbols = [MathTex("+", color=Palette.text), MathTex("=", color=Palette.text)]
        equation = backed(VGroup(v_col, symbols[0], w_col, symbols[1], answer).arrange(RIGHT, buff=0.3), padding=0.3)
        equation.to_corner(UL, buff=0.5)
        self.play(
            FadeIn(equation.background_rectangle),
            *[FadeIn(m) for m in (v_col, w_col, *symbols)],
            FadeIn(answer.get_brackets()),
            run_time=1.0,
        )
        for row in range(2):
            pair = VGroup(v_col.get_entries()[row], w_col.get_entries()[row])
            self.play(Indicate(pair, color=Palette.glow, scale_factor=1.15), run_time=0.9)
            self.play(FadeIn(answer.get_entries()[row], shift=LEFT * 0.2), run_time=0.6, rate_func=spring)
        self.wait(Timing.read_long)
        self.play(FadeOut(equation), run_time=0.6)

    def scaling(self, plane, v_arrow, line):
        c = ValueTracker(1.0)
        scaled = always_redraw(lambda: vector_arrow((c.get_value() * V[0], c.get_value() * V[1]), Palette.yellow, plane))
        self.remove(v_arrow)
        self.add(scaled)
        control = backed(slider(r"c", c, Palette.yellow), padding=0.25).to_corner(UL, buff=0.5)
        readout = always_redraw(lambda: self.scaled_column(c.get_value(), control))
        line = self.say(r"Multiplying by a number $c$ is called scaling.", line, hold=0.2)
        self.play(FadeIn(control), FadeIn(readout), run_time=0.8)
        self.wait(Timing.beat)

        steps = [
            (2.0, r"$c = 2$ doubles the length and keeps the direction."),
            (0.5, r"$c = \tfrac12$ shrinks it to half."),
            (-1.0, r"A negative $c$ flips it to point the opposite way."),
            (1.0, r"Every entry of the list gets multiplied by $c$."),
        ]
        for target, text in steps:
            line = self.say(text, line, hold=0.1)
            self.play(c.animate.set_value(target), run_time=1.8, rate_func=spring)
            self.wait(Timing.read_short)
        self.play(FadeOut(control), FadeOut(readout), FadeOut(scaled), run_time=0.6)
        return line

    def scaled_column(self, c_value, control):
        numbers = [f"{c_value * V[0]:.2f}", f"{c_value * V[1]:.2f}"]
        parts = VGroup(
            MathTex(r"c", color=Palette.yellow),
            colored_column(V),
            MathTex("=", color=Palette.text),
            column(numbers, color=Palette.yellow),
        ).arrange(RIGHT, buff=0.25)
        return backed(parts, padding=0.25).next_to(control, DOWN, buff=0.3, aligned_edge=LEFT)

    def combinations(self, plane, line):
        a = ValueTracker(1.0)
        b = ValueTracker(1.0)
        a_part = always_redraw(lambda: vector_arrow((a.get_value() * V[0], a.get_value() * V[1]), Palette.yellow, plane))
        b_part = always_redraw(lambda: self.tip_to_tail(plane, a.get_value(), b.get_value()))
        result = always_redraw(lambda: vector_arrow(self.combo(a.get_value(), b.get_value()), Palette.teal, plane, stroke_width=7))
        controls = backed(
            VGroup(slider(r"a", a, Palette.yellow), slider(r"b", b, Palette.blue)).arrange(DOWN, buff=0.35, aligned_edge=RIGHT),
            padding=0.25,
        ).to_corner(UL, buff=0.5)
        formula = backed(MathTex(r"a\,\vec v", "+", r"b\,\vec w", font_size=48)).to_corner(UR, buff=0.6)
        formula[1].set_color(Palette.yellow)
        formula[2].set_color(Palette.text)
        formula[3].set_color(Palette.blue)

        line = self.say(r"Now scale both and add: that's a \emph{linear combination}.", line, hold=0.2)
        self.play(FadeIn(controls), Write(formula), GrowArrow(a_part), run_time=1.2)
        self.add(b_part)
        self.play(GrowArrow(result), run_time=1.0, rate_func=spring_soft)
        self.wait(Timing.read_short)

        line = self.say(r"Each choice of $a$ and $b$ lands the tip somewhere new.", line, hold=0.2)
        stamps = self.stamp_choices(plane, a, b, [(-0.8, 1.2), (0.6, -1.0), (-0.4, -0.9), (1.2, 0.6)])
        self.add_foreground_mobjects(controls, formula, a_part, b_part, result, stamps)

        line = self.say(r"Try every choice and the tips fill the whole plane.", line, hold=0.2)
        self.play(a.animate.set_value(1.0), b.animate.set_value(1.0), run_time=1.2, rate_func=spring_soft)
        self.play(LaggedStart(*[GrowFromCenter(dot) for dot in reachable_lattice(plane)], lag_ratio=0.004), run_time=4.0)
        self.wait(Timing.read_short)
        line = self.say(r"The set of places you can reach is called the \emph{span}. That's tomorrow.", line, hold=Timing.read_long)
        self.foreground_mobjects.clear()
        self.remove(stamps)
        return line

    def stamp_choices(self, plane, a, b, choices):
        stamps = VGroup()
        for a_value, b_value in choices:
            self.play(a.animate.set_value(a_value), b.animate.set_value(b_value), run_time=1.6, rate_func=spring)
            stamp = Dot(plane.c2p(*self.combo(a_value, b_value)), radius=0.09, color=Palette.glow)
            stamps.add(stamp)
            self.play(GrowFromCenter(stamp), run_time=0.4, rate_func=spring)
            self.wait(0.4)
        return stamps

    @staticmethod
    def combo(a_value, b_value):
        return (a_value * V[0] + b_value * W[0], a_value * V[1] + b_value * W[1])

    @staticmethod
    def tip_to_tail(plane, a_value, b_value):
        start = plane.c2p(a_value * V[0], a_value * V[1])
        end = plane.c2p(*Lesson.combo(a_value, b_value))
        return Arrow(start, end, buff=0, color=Palette.blue, stroke_width=6, max_tip_length_to_length_ratio=0.18, max_stroke_width_to_length_ratio=12)


def reachable_lattice(plane, step: float = 0.25):
    frame_x, frame_y = config.frame_width / 2, config.frame_height / 2
    dots = VGroup()
    for i in range(-24, 25):
        for j in range(-24, 25):
            point = plane.c2p(*Lesson.combo(i * step, j * step))
            if abs(point[0]) < frame_x and abs(point[1]) < frame_y:
                dots.add(Dot(point, radius=0.035, color=Palette.glow, fill_opacity=0.75))
    dots.submobjects.sort(key=lambda dot: np.linalg.norm(dot.get_center()))
    return dots


class FigArrowAndList(Scene):
    def construct(self):
        plane = make_plane(x_range=(-2, 5, 1), y_range=(-1, 3.5, 1))
        run, rise, run_label, rise_label = walk_guides(plane, V)
        col = backed(colored_column(V)).next_to(plane.c2p(*V), RIGHT, buff=0.4)
        self.add(plane, run, rise, run_label, rise_label, vector_arrow(V, Palette.yellow, plane), col)
        fit_to_frame(self)


class FigAddition(Scene):
    def construct(self):
        plane = make_plane(x_range=(-3, 5, 1), y_range=(-1, 5, 1))
        total = (V[0] + W[0], V[1] + W[1])
        moved = vector_arrow(W, Palette.blue, plane).shift(plane.c2p(*V) - plane.c2p(0, 0))
        labels = VGroup(
            backed(MathTex(r"\vec v", color=Palette.yellow)).next_to(plane.c2p(1.5, 1), DR, buff=0.1),
            backed(MathTex(r"\vec w", color=Palette.blue)).next_to(plane.c2p(-0.5, 1), LEFT, buff=0.15),
            backed(MathTex(r"\vec v+\vec w", color=Palette.teal)).next_to(plane.c2p(*total), UL, buff=0.1),
        )
        self.add(plane, vector_arrow(V, Palette.yellow, plane), vector_arrow(W, Palette.blue, plane), moved, vector_arrow(total, Palette.teal, plane), labels)
        fit_to_frame(self)


class FigScaling(Scene):
    def construct(self):
        plane = make_plane(x_range=(-4, 7, 1), y_range=(-3, 4.5, 1))
        arrows = VGroup()
        for factor, tex, color in [(2, r"2\vec v", Palette.yellow), (1, r"\vec v", Palette.text), (-1, r"-\vec v", Palette.pink)]:
            arrow = vector_arrow((factor * V[0], factor * V[1]), color, plane, stroke_width=5)
            label = backed(MathTex(tex, color=color, font_size=40))
            label.next_to(arrow.get_end(), UR if factor > 0 else DL, buff=0.1)
            arrows.add(arrow, label)
        self.add(plane, arrows)
        fit_to_frame(self)


class FigSpan(Scene):
    def construct(self):
        plane = make_plane(x_range=(-7, 7, 1), y_range=(-4, 4, 1))
        self.add(plane, reachable_lattice(plane), vector_arrow(V, Palette.yellow, plane), vector_arrow(W, Palette.blue, plane))


class Poster(Scene):
    def construct(self):
        plane = make_plane()
        formula = backed(MathTex(r"a\,\vec v", "+", r"b\,\vec w", font_size=64)).to_corner(UR, buff=0.6)
        formula[1].set_color(Palette.yellow)
        formula[3].set_color(Palette.blue)
        self.add(plane, reachable_lattice(plane), Lesson.tip_to_tail(plane, 1, 1))
        self.add(vector_arrow(V, Palette.yellow, plane), vector_arrow(Lesson.combo(1, 1), Palette.teal, plane, stroke_width=7), formula)
