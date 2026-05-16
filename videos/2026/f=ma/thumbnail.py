from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE  (consistent with the series)
# ─────────────────────────────────────────────
COLOR_BG        = "#1C1C1E"
COLOR_GROUND    = "#8E8E93"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F     = "#FF3B30"
COLOR_VEC_V     = "#32ADE6"
COLOR_GREEN     = "#34C759"
COLOR_AMBER     = "#FFCC00"
COLOR_PINK      = "#FF2D55"
COLOR_PURPLE    = "#AF52DE"
COLOR_WHITE     = "#E5E5EA"


# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════

def build_grid():
    grid = VGroup()
    max_x, max_y, spacing = 12, 8, 0.5

    def fading_line(start, end, peak_op):
        segs = VGroup()
        vec = end - start
        N = 30
        for i in range(N):
            p1 = start + vec * (i / N)
            p2 = start + vec * ((i + 1) / N)
            t  = (i + 0.5) / N
            op = peak_op * 0.35 * (1 - (2 * t - 1) ** 2)
            segs.add(Line(p1, p2, stroke_opacity=op,
                          stroke_width=1, color=COLOR_WHITE))
        return segs

    for x in np.arange(-max_x, max_x + 0.1, spacing):
        peak = 0.35 * (1 - (abs(x) / max_x) ** 1.5)
        if peak > 0:
            grid.add(fading_line(UP * max_y + RIGHT * x,
                                 DOWN * max_y + RIGHT * x, peak))
    for y in np.arange(-max_y, max_y + 0.1, spacing):
        peak = 0.35 * (1 - (abs(y) / max_y) ** 1.5)
        if peak > 0:
            grid.add(fading_line(LEFT * max_x + UP * y,
                                 RIGHT * max_x + UP * y, peak))
    return grid

# ═══════════════════════════════════════════════════════════════════
#  THUMBNAIL
# ═══════════════════════════════════════════════════════════════════

class Thumbnail(Scene):
    def construct(self):
        self.camera.background_color = COLOR_BG

        # ── ambient grid ──────────────────────────────────────────
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        but = Text("But", font="Segoe UI", font_size=32,
                   slant=ITALIC, color=COLOR_WHITE)
        why = Text("WHY?", font="Segoe UI", font_size=52,
                   weight=BOLD, color=COLOR_WHITE)
        hook = VGroup(but, why).arrange(RIGHT, buff=0.35, aligned_edge=DOWN)
        hook.to_corner(UL, buff=0.75).shift(RIGHT * 0.5)

        # ══════════════════════════════════════════════════════════
        #  HERO — F = m · a, huge and centered
        # ══════════════════════════════════════════════════════════
        fma = MathTex("F", "=", "m", r"\cdot", "a",
                      font_size=135)
        fma[0].set_color(COLOR_WHITE)
        fma[2].set_color(COLOR_WHITE)
        fma[3].set_color(COLOR_WHITE)
        fma[4].set_color(COLOR_WHITE)
        fma.next_to(hook, DOWN, buff=0.55, aligned_edge=LEFT)

        # ══════════════════════════════════════════════════════════
        #  BOTTOM TAG — the curiosity payoff
        # ══════════════════════════════════════════════════════════
        sub = Text(
            "the equation everyone memorized.",
            font="Segoe UI", font_size=40, slant=ITALIC,
            color=COLOR_WHITE
        )
        sub.to_edge(DOWN, buff=0.5)

        # ══════════════════════════════════════════════════════════
        #  LOWER SCENE
        # ══════════════════════════════════════════════════════════
        ground_y = -2.2

        ground = Line(LEFT * 7.5, RIGHT * 7.5,
                      color=COLOR_GROUND, stroke_width=5)
        ground.move_to(np.array([0, ground_y, 0]))

        hashes = VGroup()
        for x in np.arange(-7.0, 7.5, 0.34):
            h = Line(np.array([x, ground_y, 0]),
                     np.array([x - 0.22, ground_y - 0.30, 0]),
                     color=COLOR_GROUND,
                     stroke_width=2, stroke_opacity=0.65)
            hashes.add(h)

        block_size = 1.75
        block = Square(
            side_length=block_size,
            color=COLOR_BLUE_BALL,
            fill_color=COLOR_BLUE_BALL, fill_opacity=0.95,
            stroke_color=COLOR_WHITE, stroke_width=2.5,
        )
        block.set_sheen(-0.40, DR)
        block.move_to(np.array([0.45, ground_y + block_size / 2 + 0.01, 0]))

        m_lbl = MathTex("m", color=COLOR_WHITE, font_size=72)
        m_lbl.move_to(block.get_center())

        f_arr = Arrow(
            block.get_left() + LEFT * 1.90,
            block.get_left() + LEFT * 0.06,
            color=COLOR_VEC_F, buff=0, stroke_width=12,
            max_tip_length_to_length_ratio=0.30,
        )
        f_lbl = MathTex("F", color=COLOR_VEC_F, font_size=72)
        f_lbl.next_to(f_arr, UP, buff=0.12)

        a_arr = Arrow(
            block.get_right() + RIGHT * 0.06,
            block.get_right() + RIGHT * 1.70,
            color=COLOR_AMBER, buff=0, stroke_width=10,
            max_tip_length_to_length_ratio=0.28,
        ).next_to(block, UP, buff=0.06)
        a_lbl = MathTex("a", color=COLOR_AMBER, font_size=72)
        a_lbl.next_to(a_arr, UP, buff=0.12)

        # Speed-line streaks trailing behind the block
        motion = VGroup()

        # Dust kicked up at the trailing edge along the ground
        np.random.seed(7)
        dust = VGroup()
        for i in range(16):
            r = 0.05 + 0.05 * np.random.rand()
            x = block.get_left()[0] - 0.05 - i * 0.18 - 0.10 * np.random.rand()
            y = ground_y + 0.05 + 0.45 * np.random.rand()
            op = max(0.0, 0.60 * (1 - i / 18))
            dust.add(Dot(np.array([x, y, 0]), radius=r,
                         color=COLOR_GROUND, fill_opacity=op))

        # ══════════════════════════════════════════════════════════
        #  ASSEMBLE
        # ══════════════════════════════════════════════════════════
        self.add(
            fma, hook, sub,
            hashes, ground,
            motion, dust,
            block, m_lbl,
            f_arr, f_lbl,
            a_arr, a_lbl,
        )

