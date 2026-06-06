from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE  (series-consistent canvas)
# ─────────────────────────────────────────────
COLOR_BG       = "#0E1117"
COLOR_GROUND   = "#8E8E93"
COLOR_WHITE    = "#E5E5EA"
COLOR_DIM      = "#3A3F47"
COLOR_VEC_F    = "#FF3B30"   # red — force vectors (series)
COLOR_R        = "#34C759"   # green — distance / measurement
COLOR_AMBER    = "#FFCC00"
COLOR_G_GOLD   = "#E8B53A"   # warm antique gold (G in scene_0)

# Per the cue: F lands in gold ("your gravity color"). Flip to COLOR_VEC_F
# here if you want the series-red force glyph instead.
COLOR_F_GOLD   = COLOR_G_GOLD

FONT = "Segoe UI"

config.background_color = COLOR_BG

# Optional archival overlay (degrades to a labelled placeholder if absent),
# matching scene_0's missing-asset convention.
IMG_PRINCIPIA = "Newton's_Principia_title_page.png"


# ═══════════════════════════════════════════════════════════════════
#  HELPERS  (same construction vocabulary as the rest of the series)
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
        peak = 0.30 * (1 - (abs(x) / max_x) ** 1.5)
        if peak > 0:
            grid.add(fading_line(UP * max_y + RIGHT * x,
                                 DOWN * max_y + RIGHT * x, peak))
    for y in np.arange(-max_y, max_y + 0.1, spacing):
        peak = 0.30 * (1 - (abs(y) / max_y) ** 1.5)
        if peak > 0:
            grid.add(fading_line(LEFT * max_x + UP * y,
                                 RIGHT * max_x + UP * y, peak))
    return grid


def make_blob():
    """The dreamy 'idea' — soft amber halos, slightly amorphous, warm core.
    Built from the series' particle-halo vocabulary; offsets keep it from
    reading as a clean circle (it should feel like a thought, not a diagram)."""
    g = VGroup()
    layers = [(1.55, 0.05, [0.10, 0.06]),
              (1.15, 0.08, [-0.07, 0.10]),
              (0.85, 0.12, [0.05, -0.06]),
              (0.55, 0.18, [-0.04, -0.03])]
    for r, op, off in layers:
        g.add(Dot(np.array([off[0], off[1], 0]), radius=r, color=COLOR_AMBER,
                  fill_opacity=op, stroke_width=0))
    g.add(Dot(ORIGIN, radius=0.30, color=COLOR_G_GOLD, fill_opacity=0.45,
              stroke_width=0))
    g.add(Dot(ORIGIN, radius=0.16, color=COLOR_WHITE, fill_opacity=0.85,
              stroke_width=0))
    return g


def _corner(pt, dx, dy, length, color, sw=3):
    """One L-shaped focus-bracket corner anchored at pt, opening inward."""
    h = Line(pt, pt + np.array([dx * length, 0, 0]), color=color, stroke_width=sw)
    v = Line(pt, pt + np.array([0, dy * length, 0]), color=color, stroke_width=sw)
    return VGroup(h, v)


def focus_frame(center, half, length=0.24, color=COLOR_WHITE, sw=3):
    """Four corner brackets framing a square of half-width `half` about center.
    Used to 'clamp' the soft blob into an exact location."""
    cx, cy, _ = center
    return VGroup(
        _corner([cx - half, cy + half, 0], +1, -1, length, color, sw),
        _corner([cx + half, cy + half, 0], -1, -1, length, color, sw),
        _corner([cx - half, cy - half, 0], +1, +1, length, color, sw),
        _corner([cx + half, cy - half, 0], -1, +1, length, color, sw),
    )


def safe_image(path, width, fallback_label):
    """ImageMobject with graceful placeholder so the scene always renders."""
    try:
        return ImageMobject(path).scale_to_fit_width(width)
    except Exception:
        box = Rectangle(width=width, height=width * 1.3, color=COLOR_GROUND,
                        stroke_width=1.5, fill_color=COLOR_BG, fill_opacity=0.9)
        lbl = Text(fallback_label, font=FONT, font_size=16, color=COLOR_GROUND)
        lbl.scale_to_fit_width(width * 0.8).move_to(box)
        return VGroup(box, lbl)


# ============================================================================
class Scene_2_ProveItCliffhanger(MovingCameraScene):

    def construct(self):
        self.camera.background_color = COLOR_BG
        self.camera.frame.save_state()

        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # --- Wonder: the idea drifts, breathes. Camera leans in (intimate). ---
        blob = make_blob().move_to(UP * 0.3).set_z_index(2)
        self.play(FadeIn(blob, scale=0.7), run_time=1.0,
                  rate_func=rate_functions.ease_out_sine)
        self.play(self.camera.frame.animate.scale(0.85).move_to(blob),
                  run_time=1.3, rate_func=rate_functions.ease_in_out_sine)
        # A single slow breath — alive, unfixed.
        self.play(blob.animate.scale(1.08).shift(RIGHT * 0.18 + UP * 0.06),
                  run_time=1.8, rate_func=rate_functions.there_and_back)
        self.wait(0.4)

        self.play(
            Restore(self.camera.frame, rate_func=rate_functions.ease_in_out_sine),
            run_time=0.65
        )
        # Pre-arrange the cliffhanger so the pinned point knows where to land.
        F = MathTex("F", color=COLOR_F_GOLD, font_size=88)
        eq = MathTex("=", color=COLOR_WHITE, font_size=64)
        # Split substrings so each blank is individually addressable:
        #   0:f  1:(  2:?  3:,  4:?  5:,  6:?  7:)
        rhs = MathTex("f", "(", "?", ",", "?", ",", "?", ")",
                      color=COLOR_WHITE, font_size=64)
        equation = VGroup(F, eq, rhs).arrange(RIGHT, buff=0.30)
        equation.move_to(DOWN * 0.1).set_z_index(5)

        blanks = VGroup(rhs[2], rhs[4], rhs[6])

        # The pin becomes the quantity we set out to find: point → gold F,
        # while the coordinate scaffolding dissolves. One continuous thread.
        self.play(
            ReplacementTransform(blob, F,
                                 rate_func=rate_functions.ease_in_out_cubic),
            run_time=1.5
        )
        self.wait(0.3)

        # "= f( , , )" assembles — pieces fly in and settle (back-ease snap).
        self.play(FadeIn(eq, shift=LEFT * 0.18), run_time=0.4)
        self.play(
            LaggedStart(*[FadeIn(s, shift=DOWN * 0.15) for s in rhs],
                        lag_ratio=0.12),
            run_time=1.8, rate_func=rate_functions.ease_out_back,
        )
        self.wait(0.5)

        # Final held frame: the blanks breathe — waiting to be filled.
        # That waiting IS the promise of the next scene.
        self.play(blanks.animate.scale(1.18), run_time=0.9,
                  rate_func=rate_functions.there_and_back)
        self.play(blanks.animate.scale(1.18), run_time=0.9,
                  rate_func=rate_functions.there_and_back)
        self.wait()
