import pathlib
import sys
from collections import deque

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
    morph_matrix,
    plane_at,
    plate_for,
    scrim,
    skewed_grid,
    spring_soft,
    vector_arrow,
)

A = ((2, 1), (1, 1))
M = ((1, 2), (2, 4))
X = (2, -1)
B_TARGET = (3, 1)
M_LINE = (1, 2)
PLANE_ORIGIN = (0.9, -1.3)
PLANE_UNIT = 1.1
BASIS_COLORS = (Palette.i_hat, Palette.j_hat)

B_ROWS = [[2, 1, 0], [1, 3, 1], [0, 1, 2]]
B_STEPS = [
    [[2, 1, 0], [0, 5, 2], [0, 1, 2]],
    [[2, 1, 0], [0, 5, 2], [0, 0, 8]],
]
C_ROWS = [[1, 2, -1], [2, 4, 0], [3, 6, 1]]
VOCABULARY = (
    r"independent columns",
    r"columns span $\mathbb R^n$",
    r"$n$ pivot positions",
    r"$\operatorname{Nul}A = \{\mathbf 0\}$",
    r"$\operatorname{rank}A = n$",
    r"$A^{-1}$ exists",
)

NODE_FONT = 30
SIDE_WIDTH = 3.7
SIDE_X = 4.95
SIDE_ROWS = (2.3, 1.35, 0.4, -0.55, -1.5)
LIT_FILL = interpolate_color(ManimColor(Palette.background), ManimColor(Palette.teal), 0.2)
NODE_FILL = interpolate_color(ManimColor(Palette.background), ManimColor(Palette.grid_faint), 0.55)
BLOCK_FILL = Palette.grid_faint

NODES = {
    "e": (r"columns are independent", (-SIDE_X, SIDE_ROWS[0])),
    "f": (r"$\mathbf x \mapsto A\mathbf x$ is one-to-one", (-SIDE_X, SIDE_ROWS[1])),
    "d": (r"$A\mathbf x = \mathbf 0$ only for $\mathbf x = \mathbf 0$", (-SIDE_X, SIDE_ROWS[2])),
    "q": (r"$\operatorname{Nul}A = \{\mathbf 0\}$", (-SIDE_X, SIDE_ROWS[3])),
    "r": (r"$\dim\operatorname{Nul}A = 0$", (-SIDE_X, SIDE_ROWS[4])),
    "h": (r"columns span $\mathbb R^n$", (SIDE_X, SIDE_ROWS[0])),
    "i": (r"$\mathbf x \mapsto A\mathbf x$ is onto $\mathbb R^n$", (SIDE_X, SIDE_ROWS[1])),
    "g": (r"every $A\mathbf x = \mathbf b$ has a solution", (SIDE_X, SIDE_ROWS[2])),
    "n": (r"$\operatorname{Col}A = \mathbb R^n$", (SIDE_X, SIDE_ROWS[3])),
    "o": (r"$\dim\operatorname{Col}A = n$", (SIDE_X, SIDE_ROWS[4])),
    "m": (r"columns form a basis of $\mathbb R^n$", (0, 3.5)),
    "l": (r"$A^T$ is invertible", (0, 2.66)),
    "a": (r"$A$ is invertible", (0, 1.82)),
    "j": (r"$CA = I$", (-1.15, 0.98)),
    "k": (r"$AD = I$", (1.15, 0.98)),
    "b": (r"$A \sim I_n$", (0, -0.05)),
    "c": (r"$n$ pivot positions", (0, -0.95)),
    "p": (r"$\operatorname{rank}A = n$", (0, -1.85)),
}

IMPLIES, SAME = "implies", "same"
EDGE_STAGES = [
    (r"$A^{-1}$ itself serves as $C$ in $CA = I$ and $D$ in $AD = I$.", [("a", "j", IMPLIES, 0), ("a", "k", IMPLIES, 0), ("a", "l", SAME, 0)]),
    (r"If $CA = I$ and $A\mathbf x = \mathbf 0$, then $\mathbf x = CA\mathbf x = \mathbf 0$.", [("j", "d", IMPLIES, 0)]),
    (r"No free variables gives $n$ pivots, which reduce $A$ to $I$.", [("d", "c", IMPLIES, 0), ("c", "b", IMPLIES, 0)]),
    (r"Row reducing $[\,A\ \ I\,]$ then produces $A^{-1}$.", [("b", "a", IMPLIES, 0)]),
    (r"If $AD = I$, then $\mathbf x = D\mathbf b$ solves $A\mathbf x = \mathbf b$.", [("k", "g", IMPLIES, 0)]),
    (r"A square matrix with a pivot in every row has $n$ pivots.", [("g", "c", IMPLIES, 0)]),
    (
        r"Inside each block, neighbours say the same thing in new words.",
        [("e", "f", SAME, 0), ("f", "d", SAME, 0), ("h", "i", SAME, 0), ("i", "g", SAME, 0), ("m", "e", SAME, 0), ("m", "h", SAME, 0),
         ("g", "n", IMPLIES, 0), ("n", "o", IMPLIES, 0), ("r", "q", IMPLIES, 0), ("q", "d", IMPLIES, 0)],
    ),
    (r"The rank theorem turns rank $n$ into nullity $0$.", [("o", "p", IMPLIES, 0), ("p", "r", IMPLIES, 0)]),
]


def tex(*parts, colors=(), font_size=48):
    formula = MathTex(*parts, color=Palette.text, font_size=font_size)
    for part, color in zip(formula, colors):
        if color:
            part.set_color(color)
    return formula


def basis_matrix(rows):
    mat = matrix([[str(entry) for entry in row] for row in rows])
    for index, color in enumerate(BASIS_COLORS):
        mat.get_columns()[index].set_color(color)
    return mat


def plain_matrix(rows):
    return matrix([[str(entry) for entry in row] for row in rows])


def named(name, mat, font_size=48):
    return VGroup(tex(name, "=", font_size=font_size), mat).arrange(RIGHT, buff=0.2)


def pivot_box(entry):
    return SurroundingRectangle(entry, color=Palette.glow, buff=0.1, stroke_width=3, corner_radius=0)


def ring(plane, coords, color=Palette.teal):
    return Circle(radius=0.24, color=color, stroke_width=4).move_to(plane.c2p(*coords))


def name_label(parts, colors, anchor, direction, font_size=40):
    return backed(tex(*parts, colors=colors, font_size=font_size)).next_to(anchor, direction, buff=0.12)


def safe_arrow(plane, coords, color, stroke_width=6):
    if np.hypot(*coords) < 0.04:
        return VectorizedPoint(plane.c2p(0, 0))
    return vector_arrow(coords, color, plane, stroke_width=stroke_width)


def live_arrow(plane, live, coords, color, stroke_width=6):
    return always_redraw(lambda: safe_arrow(plane, live.point(coords), color, stroke_width))


def rank_cells(survivors, total=2):
    cells = VGroup()
    for index in range(total):
        cell = Square(side_length=0.6, stroke_width=0)
        if index < survivors:
            cell.set_fill(Palette.teal, opacity=0.85)
        else:
            cell.set_fill(Palette.background, opacity=0)
            cell = VGroup(cell, DashedVMobject(Square(side_length=0.6, color=Palette.text_muted, stroke_width=2.5), num_dashes=16))
        cells.add(cell)
    return cells.arrange(RIGHT, buff=0.08)


def rank_row(name, survivors):
    label = tex(name, font_size=52)
    readout = Tex(f"rank {survivors}, nullity {2 - survivors}", color=Palette.text, font_size=42)
    return VGroup(label, rank_cells(survivors), readout).arrange(RIGHT, buff=0.35)


class Node(VGroup):
    """One statement of the theorem: text on a sharp plate that can light up or go dark."""

    def __init__(self, key, text, center, width=None, font_size=NODE_FONT):
        label = Tex(text, color=Palette.text, font_size=font_size)
        if width and label.width > width - 0.3:
            label.scale_to_fit_width(width - 0.3)
        plate = Rectangle(width=width or label.width + 0.34, height=label.height + 0.22, stroke_width=0, fill_color=NODE_FILL, fill_opacity=1)
        super().__init__(plate, label)
        self.key = key
        self.plate, self.label = plate, label
        self.move_to([center[0], center[1], 0])

    def lit(self):
        return AnimationGroup(self.plate.animate.set_fill(LIT_FILL, opacity=1), self.label.animate.set_color(Palette.teal))

    def dark(self):
        return AnimationGroup(self.plate.animate.set_fill(Palette.background, opacity=1), self.label.animate.set_color(Palette.text_muted).set_opacity(0.4))

    def neutral(self):
        return AnimationGroup(self.plate.animate.set_fill(NODE_FILL, opacity=1), self.label.animate.set_color(Palette.text).set_opacity(1))

    def rim(self, toward):
        """The point where the ray from this node's center toward `toward` leaves its plate."""
        center = self.plate.get_center()
        delta = np.asarray(toward) - center
        half_w, half_h = self.plate.width / 2 + 0.06, self.plate.height / 2 + 0.06
        scale = min(half_w / abs(delta[0]) if abs(delta[0]) > 1e-9 else np.inf, half_h / abs(delta[1]) if abs(delta[1]) > 1e-9 else np.inf)
        return center + delta * scale


def build_nodes():
    nodes = {}
    for key, (text, center) in NODES.items():
        width = SIDE_WIDTH if abs(center[0]) > 3 else None
        size = 36 if key == "a" else NODE_FONT
        nodes[key] = Node(key, text, center, width=width, font_size=size)
    return nodes


def side_block(nodes, keys, title):
    members = VGroup(*[nodes[key] for key in keys])
    heading = Tex(title, color=Palette.text_muted, font_size=30).next_to(members, DOWN, buff=0.2)
    body = VGroup(heading, members)
    plate = Rectangle(width=members.width + 0.3, height=body.height + 0.34, stroke_width=0, fill_color=BLOCK_FILL, fill_opacity=0.45).move_to(body)
    return VGroup(plate, heading)


def center_block(nodes, keys):
    members = VGroup(*[nodes[key] for key in keys])
    return Rectangle(width=max(members.width + 0.3, 3.4), height=members.height + 0.3, stroke_width=0, fill_color=BLOCK_FILL, fill_opacity=0.45).move_to(members)


def edge_mobject(nodes, start, end, kind, arc):
    head, tail = nodes[start], nodes[end]
    begin = head.rim(tail.get_center())
    finish = tail.rim(head.get_center())
    style = {"color": Palette.text_muted, "stroke_width": 3, "buff": 0, "tip_length": 0.16, "max_tip_length_to_length_ratio": 0.4}
    if kind == SAME:
        return DoubleArrow(begin, finish, **style)
    return Arrow(begin, finish, path_arc=arc, **style)


class Web(VGroup):
    """Lay's eighteen statements, the blocks that group them and the arrows of the proof."""

    def __init__(self):
        self.nodes = build_nodes()
        self.blocks = VGroup(
            side_block(self.nodes, "efdqr", r"Nothing is crushed"),
            side_block(self.nodes, "higno", r"Every target is reached"),
            center_block(self.nodes, "lajk"),
            center_block(self.nodes, "bcp"),
        )
        self.edges = {}
        self.stages = []
        for caption_text, stage in EDGE_STAGES:
            drawn = []
            for start, end, kind, arc in stage:
                edge = edge_mobject(self.nodes, start, end, kind, arc)
                self.edges[(start, end)] = (edge, kind)
                drawn.append(edge)
            self.stages.append((caption_text, VGroup(*drawn)))
        self.arrows = VGroup(*[edge for edge, _ in self.edges.values()])
        super().__init__(self.blocks, self.arrows, *self.nodes.values())

    def neighbours(self, key, reverse=False):
        found = []
        for (start, end), (edge, kind) in self.edges.items():
            if kind == SAME or not reverse:
                if start == key:
                    found.append((end, edge, False))
            if kind == SAME or reverse:
                if end == key:
                    found.append((start, edge, True))
        return found

    def spread(self, seed, reverse=False):
        """Breadth-first levels from `seed`: each is a list of (node key, edge, travel backwards along the edge)."""
        seen = {seed}
        frontier = deque([seed])
        levels = []
        while frontier:
            level = []
            for _ in range(len(frontier)):
                key = frontier.popleft()
                for other, edge, backwards in self.neighbours(key, reverse):
                    if other not in seen:
                        seen.add(other)
                        level.append((other, edge, backwards))
                        frontier.append(other)
            if level:
                levels.append(level)
        return levels


def travelling_light(edge, backwards):
    path = Line(edge.get_end(), edge.get_start()) if backwards else Line(edge.get_start(), edge.get_end())
    dot = Dot(path.get_start(), radius=0.08, color=Palette.glow)
    return dot, path


class Lesson(LessonScene):
    day = 19
    title = "The invertible matrix theorem"

    def construct(self):
        plane = plane_at(PLANE_ORIGIN, PLANE_UNIT)
        plane.background_lines.set_stroke(color=Palette.grid, width=3.0, opacity=0.32)
        plane.faded_lines.set_stroke(opacity=0)
        plane.axes.set_stroke(color=Palette.axis, width=2.0, opacity=0.7)
        self.plane = plane
        self.panel = None
        pulse = self.open_episode(plane)
        self.play(FadeOut(pulse), run_time=0.5)
        line = self.pose_question()
        line = self.nothing_squashed(line)
        line = self.squashed(line)
        line = self.rank_bars(line)
        line, web = self.build_web(line)
        line = self.light_flood(line, web)
        line = self.dark_flood(line, web)
        line = self.determinant_preview(line, web)
        self.close_episode(
            r"For a square matrix, all eighteen statements are one fact.\\"
            r"Either $A$ squashes no direction, or every statement fails.",
            *self.mobjects,
        )

    def set_panel(self, content, run_time=0.7):
        content.to_corner(UL, buff=0.55)
        new_plate = plate_for(content)
        if self.panel is None:
            self.plate = new_plate
            self.play(FadeIn(self.plate), FadeIn(content, shift=DOWN * 0.1), run_time=run_time)
        else:
            self.play(FadeOut(self.panel), self.plate.animate.become(new_plate), run_time=0.5)
            self.play(FadeIn(content, shift=DOWN * 0.1), run_time=run_time, rate_func=spring_soft)
        self.panel = content

    def start_live_grid(self):
        plane = self.plane
        self.live = LiveTransform()
        self.grid = always_redraw(lambda: self.live.grid(plane, opacity=0.32, cap=20).set_stroke(width=3.0))
        self.basis = VGroup(live_arrow(plane, self.live, (1, 0), Palette.i_hat), live_arrow(plane, self.live, (0, 1), Palette.j_hat))
        plane.background_lines.set_stroke(opacity=0)
        self.add(self.grid)
        self.bring_to_front(plane)
        self.play(*[GrowArrow(arrow) for arrow in self.basis], run_time=1.0, rate_func=spring_soft)

    def move(self, animation, run_time=1.8):
        self.play(animation, run_time=run_time, rate_func=spring_soft)

    def pose_question(self):
        words = VGroup(*[Tex(text, color=Palette.text, font_size=36) for text in VOCABULARY]).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        line = self.say(r"Days 12 to 18 gave square matrices many new words.", hold=0.2)
        self.set_panel(words, run_time=1.2)
        self.wait(Timing.beat)
        line = self.say(r"Do these all say the same thing about a square matrix?", line, hold=0.2)
        self.play(LaggedStart(*[Indicate(word, color=Palette.teal, scale_factor=1.06) for word in words], lag_ratio=0.25), run_time=1.6)
        self.wait(Timing.beat)
        return line

    def nothing_squashed(self, line):
        plane = self.plane
        line = self.say(r"Day 7's matrix $A$ moves every point of the plane.", line, hold=0.2)
        self.set_panel(named("A", basis_matrix(A)))
        self.start_live_grid()
        self.wait(Timing.beat)

        line = self.say(r"Follow the pink $\mathbf x$ and the ring at $\mathbf b$.", line, hold=0.2)
        self.x_arrow = live_arrow(plane, self.live, X, Palette.pink)
        self.target = ring(plane, B_TARGET)
        self.target_name = name_label([r"\mathbf b"], [Palette.teal], self.target, UR, font_size=38)
        x_name = name_label([r"\mathbf x"], [Palette.pink], plane.c2p(*X), DR, font_size=38)
        self.play(GrowArrow(self.x_arrow), FadeIn(x_name), run_time=1.0, rate_func=spring_soft)
        self.play(Create(self.target), FadeIn(self.target_name), run_time=0.8)
        self.wait(Timing.beat)

        line = self.say(r"$A$ sends $\mathbf x$ onto $\mathbf b$, not onto $\mathbf 0$.", line, hold=0.2)
        self.play(FadeOut(x_name), run_time=0.3)
        self.move(self.live.apply(A), run_time=2.0)
        self.play(Indicate(self.target, color=Palette.teal, scale_factor=1.3), run_time=0.8)
        self.wait(Timing.beat)

        line = self.say(r"The grid still covers the plane, so every target is hit.", line, hold=Timing.read_short)
        return line

    def squashed(self, line):
        plane = self.plane
        line = self.say(r"Now try $M$, whose columns point along one line.", line, hold=0.2)
        self.move(self.live.apply(np.linalg.inv(self.live.value)), run_time=1.2)
        self.set_panel(named("M", basis_matrix(M)))
        self.move(self.live.apply(M), run_time=2.2)
        self.play(Flash(plane.c2p(0, 0), color=Palette.glow, line_length=0.3, flash_radius=0.35), run_time=0.8)
        line = self.say(r"$M$ crushes $\mathbf x$ all the way to $\mathbf 0$.", line, hold=Timing.read_short)

        line = self.say(r"Everything lands on one line, so $\mathbf b$ is never reached.", line, hold=0.2)
        foot = np.dot(B_TARGET, M_LINE) / np.dot(M_LINE, M_LINE) * np.array(M_LINE, dtype=float)
        self.gap = DashedLine(plane.c2p(*B_TARGET), plane.c2p(*foot), color=Palette.glow, stroke_width=3)
        self.play(Create(self.gap), Circumscribe(self.target, shape=Circle, color=Palette.glow, buff=0.08), run_time=1.2)
        self.wait(Timing.read_short)
        return line

    def rank_bars(self, line):
        rows = VGroup(rank_row("A", 2), rank_row("M", 1)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        line = self.say(r"Two input directions go in, and each survives or is crushed.", line, hold=0.2)
        self.play(FadeOut(self.panel), FadeOut(self.plate), run_time=0.5)
        self.panel = None
        self.set_panel(rows)
        self.wait(Timing.read_short)
        line = self.say(r"Rank plus nullity always equals $2$ for a $2\times 2$ matrix.", line, hold=Timing.read_long)
        line = self.say(r"So a square matrix that crushes nothing reaches everything.", line, hold=Timing.read_long)
        return line

    def build_web(self, line):
        veil = scrim()
        web = Web()
        self.add(veil)
        self.bring_to_front(line)
        line = self.say(r"For a square $n\times n$ matrix, Lay lists eighteen statements.", line, hold=0.05)
        self.play(FadeIn(veil), FadeOut(self.panel), FadeOut(self.plate), run_time=0.8)
        self.panel = None
        self.clear_plane()
        self.play(LaggedStart(*[FadeIn(node, shift=UP * 0.1) for node in web.nodes.values()], lag_ratio=0.06), run_time=2.4)
        self.wait(Timing.beat)

        line = self.say(r"Some say nothing is crushed, and others say every target is hit.", line, hold=0.2)
        self.add(web.blocks)
        self.bring_to_front(*web.nodes.values())
        self.play(FadeIn(web.blocks), run_time=0.9)
        self.wait(Timing.read_short)

        self.add(web.arrows)
        web.arrows.set_opacity(0)
        for caption_text, edges in web.stages:
            line = self.say(caption_text, line, hold=0.1)
            edges.set_opacity(1)
            self.play(*[GrowArrow(edge) for edge in edges], run_time=1.0)
            self.wait(Timing.read_short)
        line = self.say(r"So the eighteen are all true or all false together.", line, hold=Timing.read_short)
        return line, web

    def clear_plane(self):
        for mob in (self.grid, *self.basis, self.x_arrow, self.target, self.target_name, self.gap, self.plane):
            self.remove(mob)

    def center_stage(self, content):
        stage = Rectangle(width=4.9, height=3.4, stroke_width=0, fill_color=Palette.background, fill_opacity=0.97).move_to([0, 1.3, 0])
        content.move_to(stage)
        return stage

    def feed(self, content, stage, node):
        self.play(FadeOut(stage), content.animate.scale(0.18).move_to(node.get_center()).set_opacity(0), run_time=1.1, rate_func=spring_soft)
        self.remove(content)

    def light_flood(self, line, web):
        b_mat = named("B", plain_matrix(B_ROWS), font_size=44)
        stage = self.center_stage(b_mat)
        line = self.say(r"So we can check one cheap statement and trust the rest.", line, hold=0.2)
        self.play(FadeIn(stage), FadeIn(b_mat), run_time=0.8)
        line = self.say(r"Row reduce $B$ only far enough to count its pivots.", line, hold=0.2)
        for rows in B_STEPS:
            morph_matrix(self, b_mat[1], plain_matrix(rows).move_to(b_mat[1]), run_time=0.9)
            self.wait(0.4)
        entries = b_mat[1].get_entries()
        boxes = VGroup(*[pivot_box(entries[index]) for index in (0, 4, 8)])
        self.play(LaggedStart(*[Create(box) for box in boxes], lag_ratio=0.3), run_time=1.0)
        line = self.say(r"$B$ has three pivots. Watch that one fact travel.", line, hold=0.2)
        self.feed(VGroup(b_mat, boxes), stage, web.nodes["c"])
        self.play(web.nodes["c"].lit(), Flash(web.nodes["c"].get_left(), color=Palette.glow, line_length=0.2), run_time=0.6)
        self.flood(web, "c", reverse=False)
        line = self.say(r"The light reaches every statement, so $B$ is invertible.", line, hold=Timing.read_long)
        return line

    def flood(self, web, seed, reverse):
        color = Palette.text_muted if reverse else Palette.teal
        for level in web.spread(seed, reverse):
            lights = [travelling_light(edge, backwards) for _, edge, backwards in level]
            dots = [dot for dot, _ in lights]
            self.add(*dots)
            self.play(
                *[MoveAlongPath(dot, path) for dot, path in lights],
                *[edge.animate.set_color(color).set_opacity(0.35 if reverse else 1) for _, edge, _ in level],
                run_time=0.55,
                rate_func=smooth,
            )
            self.remove(*dots)
            changes = [web.nodes[key].dark() if reverse else web.nodes[key].lit() for key, _, _ in level]
            self.play(*changes, run_time=0.3)
        self.play(web.arrows.animate.set_color(color).set_opacity(0.35 if reverse else 1), run_time=0.5)

    def dark_flood(self, line, web):
        line = self.say(r"Here is $C$, whose second column is twice its first.", line, hold=0.05)
        self.play(*[node.neutral() for node in web.nodes.values()], web.arrows.animate.set_color(Palette.text_muted).set_opacity(1), run_time=0.8)
        c_mat = named("C", plain_matrix(C_ROWS), font_size=44)
        relation = tex(r"\mathbf c_2", "=", r"2\,\mathbf c_1", font_size=44)
        group = VGroup(c_mat, relation).arrange(DOWN, buff=0.3)
        stage = self.center_stage(group)
        self.play(FadeIn(stage), FadeIn(c_mat), run_time=0.8)
        columns = c_mat[1].get_columns()
        self.play(Indicate(columns[0], color=Palette.glow, scale_factor=1.15), run_time=0.8)
        self.play(Indicate(columns[1], color=Palette.glow, scale_factor=1.15), run_time=0.8)
        self.play(Write(relation), run_time=0.9)
        self.wait(Timing.beat)

        line = self.say(r"Independence fails, and the failure spreads to every statement.", line, hold=0.2)
        seed = web.nodes["e"]
        self.feed(group, stage, seed)
        self.play(seed.dark(), Circumscribe(seed, color=Palette.glow, buff=0.06), run_time=0.9)
        self.flood(web, "e", reverse=True)
        line = self.say(r"So $C$ is singular, and no row reduction was needed.", line, hold=Timing.read_long)
        return line

    def determinant_preview(self, line, web):
        label = Tex(r"$\det A \neq 0$", color=Palette.text_muted, font_size=NODE_FONT)
        frame = DashedVMobject(Rectangle(width=label.width + 0.4, height=label.height + 0.3, color=Palette.text_muted, stroke_width=2), num_dashes=24)
        preview = VGroup(frame, label).move_to([SIDE_X, 3.3, 0])
        line = self.say(r"On Day 26, $\det A \neq 0$ joins the list.", line, hold=0.2)
        self.play(FadeIn(preview, shift=UP * 0.1), run_time=0.8, rate_func=spring_soft)
        self.wait(Timing.read_short)
        line = self.say(r"Day 29 uses this list to hunt for eigenvalues.", line, hold=0.2)
        self.play(Indicate(web.nodes["a"], color=Palette.glow, scale_factor=1.08), run_time=1.0)
        self.wait(Timing.read_short)
        return line


def squash_panel(rows, name):
    plane = make_plane(x_range=(-3, 5, 1), y_range=(-3, 4, 1)).set_stroke(opacity=0.25)
    live = LiveTransform(rows)
    image = live.point(X)
    layers = VGroup(plane, skewed_grid(plane, live.value[:, 0], live.value[:, 1], reach=20, color=Palette.blue, opacity=0.7))
    layers.add(vector_arrow(live.point((1, 0)), Palette.i_hat, plane), vector_arrow(live.point((0, 1)), Palette.j_hat, plane))
    layers.add(ring(plane, B_TARGET), name_label([r"\mathbf b"], [Palette.teal], plane.c2p(*B_TARGET) + 0.15 * UP, UP, font_size=38))
    if np.hypot(*image) > 0.1:
        layers.add(vector_arrow(image, Palette.pink, plane), name_label([name + r"\mathbf x"], [Palette.pink], plane.c2p(*image), DR, font_size=38))
    else:
        foot = np.dot(B_TARGET, M_LINE) / np.dot(M_LINE, M_LINE) * np.array(M_LINE, dtype=float)
        layers.add(DashedLine(plane.c2p(*B_TARGET), plane.c2p(*foot), color=Palette.glow, stroke_width=3))
        layers.add(Dot(plane.c2p(0, 0), radius=0.11, color=Palette.glow), name_label([name + r"\mathbf x = \mathbf 0"], [Palette.glow], plane.c2p(0, 0), DR, font_size=38))
    title = named(name, basis_matrix(rows), font_size=44)
    return VGroup(title, layers).arrange(DOWN, buff=0.35)


class FigSquash(Scene):
    def construct(self):
        self.add(VGroup(squash_panel(A, "A"), squash_panel(M, "M")).arrange(RIGHT, buff=0.8, aligned_edge=UP))
        fit_to_frame(self)


def web_scene(scene, state=None):
    web = Web()
    scene.add(web)
    if state == "lit":
        for node in web.nodes.values():
            node.plate.set_fill(LIT_FILL, opacity=1)
            node.label.set_color(Palette.teal)
        web.arrows.set_color(Palette.teal)
    return web


class FigWeb(Scene):
    def construct(self):
        web_scene(self)
        fit_to_frame(self, margin=0.25)


class FigDecide(Scene):
    def construct(self):
        b_mat = named("B", plain_matrix(B_ROWS), font_size=44)
        echelon = plain_matrix(B_STEPS[-1])
        entries = echelon.get_entries()
        b_side = VGroup(b_mat, tex(r"\sim", font_size=44), echelon).arrange(RIGHT, buff=0.3)
        b_side.add(*[pivot_box(entries[index]) for index in (0, 4, 8)])
        c_mat = named("C", plain_matrix(C_ROWS), font_size=44)
        columns = c_mat[1].get_columns()
        c_mat.add(*[SurroundingRectangle(columns[index], color=Palette.glow, buff=0.1, stroke_width=3, corner_radius=0) for index in (0, 1)])
        c_side = VGroup(c_mat, tex(r"\mathbf c_2", "=", r"2\,\mathbf c_1", font_size=44)).arrange(RIGHT, buff=0.5)
        self.add(VGroup(b_side, c_side).arrange(DOWN, buff=0.8))
        fit_to_frame(self, margin=0.8)


class Poster(Scene):
    def construct(self):
        web = web_scene(self, state="lit")
        seed = web.nodes["c"]
        self.add(SurroundingRectangle(seed, color=Palette.glow, buff=0.08, stroke_width=4, corner_radius=0))
