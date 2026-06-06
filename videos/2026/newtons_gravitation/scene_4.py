from manim import *
import numpy as np

# ─────────────────────────────────────────────────────────────────────────
#  BRAND PALETTE  (carried verbatim from scene_3 / the series canvas)
# ─────────────────────────────────────────────────────────────────────────
COLOR_BG        = "#0E1117"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_VEC_F     = "#FF3B30"   # red   — gravity / "the force we already know"
COLOR_GREEN     = "#34C759"
COLOR_AMBER     = "#FFCC00"   # amber — was the locked small-mass m (scene_0/3)
COLOR_BLUE_BALL = "#007AFF"   # blue  — LOCKED: the big mass M (Earth)
COLOR_DIM       = "#3A3F47"
COLOR_CORAL     = "#FF6F61"   # NEW   — the apple = small mass m (see chat note)

# Semantic aliases for this scene. Flip COLOR_m back to COLOR_AMBER if you
# want strict colour continuity with scene_3's amber m handoff.
COLOR_M = COLOR_BLUE_BALL     # Earth's mass
COLOR_m = COLOR_CORAL         # apple's mass

FONT = "Segoe UI"
config.background_color = COLOR_BG
RNG = np.random.default_rng(7)   # deterministic → stable render cache


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS — same construction vocabulary as the rest of the series
# ═══════════════════════════════════════════════════════════════════════════
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


def safe_earth(width):
    """earth.png, with a drawn-disc fallback so the scene always renders."""
    try:
        return ImageMobject("earth.png").scale_to_fit_width(width)
    except Exception:
        body = Circle(radius=width / 2, stroke_width=0, fill_opacity=1.0,
                      color=COLOR_BLUE_BALL)
        sheen = Circle(radius=width / 2 * 0.62, stroke_width=0,
                       fill_opacity=0.16, color=COLOR_WHITE)
        sheen.move_to(body.get_center()
                      + np.array([-width * 0.16, width * 0.16, 0]))
        return Group(body, sheen)


def safe_apple(width):
    """apple.png, with a drawn fallback so the scene always renders."""
    try:
        return ImageMobject("apple.png").scale_to_fit_width(width)
    except Exception:
        body = Circle(radius=width / 2, stroke_width=0, fill_opacity=1.0,
                      color=COLOR_CORAL)
        spec = Dot(radius=width * 0.12, color=COLOR_WHITE, fill_opacity=0.9)
        spec.move_to(body.get_center()
                     + np.array([-width * 0.20, width * 0.20, 0]))
        stem = Line(body.get_top() + DOWN * width * 0.04,
                    body.get_top() + UP * width * 0.22,
                    color="#6B4423", stroke_width=3)
        return Group(body, spec, stem)


def down_arrow(top, length, color, sw=5):
    return Arrow(top, top + DOWN * length, buff=0, color=color,
                 stroke_width=sw, max_tip_length_to_length_ratio=0.28)


def prop_eq(mass_symbol, mass_color, fs=54):
    """F ∝ <mass>, with F white and the mass glyph coloured + addressable.
    Returns the VGroup; .mass is the coloured mass glyph."""
    eq = MathTex("F", r"\propto", mass_symbol, font_size=fs)
    eq[0].set_color(COLOR_WHITE)
    eq[1].set_color(COLOR_WHITE)
    eq[2].set_color(mass_color)
    eq.mass = eq[2]
    return eq


# ═══════════════════════════════════════════════════════════════════════════
class Scene_4_TheProduct(MovingCameraScene):

    # Locked anchors so nothing free-floats between acts.
    APPLE_TOP = np.array([0.0,  1.9, 0.0])
    EARTH_CTR = np.array([0.0, -4.6, 0.0])     # planet anchored low, off-frame
    BODY_Y    = 0.2                            # symmetric-bodies lane (Act 2/…)
    APPLE_SYM = np.array([-3.2, 0.2, 0.0])
    EARTH_SYM = np.array([ 3.2, 0.2, 0.0])
    ARROW_L   = 1.15                           # the matched force-arrow length

    def construct(self):
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        self.act1_both_pull()
        self.act2_symmetry()

    # ===================================================================== A1
    def act1_both_pull(self):
        # ── New shot: Earth low, apple hovering above. Nothing cuts after this.
        earth = safe_earth(5.2).move_to(self.EARTH_CTR).set_z_index(1)
        apple = safe_apple(0.62).move_to(self.APPLE_TOP).set_z_index(3)
        self.play(FadeIn(earth, shift=UP * 0.25),
                  FadeIn(apple, shift=DOWN * 0.25),
                  run_time=1.1, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        # The one force we already know: Earth → apple, downward, red.
        f_down = down_arrow(apple.get_bottom() + DOWN * 0.05, self.ARROW_L,
                            COLOR_VEC_F).set_z_index(4)
        self.play(GrowArrow(f_down), run_time=0.6)
        self.wait(0.5)

        # "har action ka equal-opposite reaction" — re-anchor on the known pull.
        self.play(f_down.animate.set_stroke(width=9), run_time=0.22,
                  rate_func=rate_functions.there_and_back)
        self.wait(0.4)

        f_up_target = Arrow(earth.get_top() + UP * 0.05,
                            earth.get_top() + UP * (0.05 + self.ARROW_L),
                            buff=0, color=COLOR_CORAL, stroke_width=5,
                            max_tip_length_to_length_ratio=0.28).set_z_index(4)
        mirror = f_down.copy()
        self.add(mirror)
        self.play(Transform(mirror, f_up_target), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_cubic)
        self.wait(0.3)

        # Hammer EQUAL: a small "=" flashed in the gap between the two heads.
        gap_mid = (f_down.get_end() + mirror.get_end()) / 2
        eq = MathTex("=", color=COLOR_WHITE, font_size=44).move_to(gap_mid)
        eq.set_z_index(5)
        self.play(FadeIn(eq, scale=0.35), run_time=0.22)
        self.play(eq.animate.scale(1.35), run_time=0.22,
                  rate_func=rate_functions.there_and_back)
        self.wait(0.5)
        self.play(FadeOut(eq), run_time=0.2)

        # ── Vsauce gut-punch: release both. Apple lunges; Earth creeps a sliver.
        self.play(FadeOut(f_down), FadeOut(mirror), run_time=0.4)

        apex0 = earth.get_top().copy()                 # Earth's ORIGINAL apex

        EARTH_RISE = 0.02   # invisible at this zoom; everything later proves it
        self.play(
            apple.animate.move_to(earth.get_top() + UP * 0.55),  # big visible drop
            earth.animate.shift(UP * EARTH_RISE),
            run_time=1.0, rate_func=rate_functions.ease_in_quad)  # accel feel
        self.wait(0.7)


        self.play(self.camera.frame.animate.scale(0.06).move_to(apex0),
                  run_time=1.5, rate_func=rate_functions.ease_in_out_sine)
        # Tremble — it really did move.
        for dy in (0.006, -0.006, 0.004, -0.004, 0.003):
            self.play(earth.animate.shift(UP * dy), run_time=0.07)
        self.wait(1.1)

        self.play(Restore(self.camera.frame),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)

        self.apple, self.earth = apple, earth

    # ===================================================================== A2
    def act2_symmetry(self):
        apple, earth = self.apple, self.earth

        # "Ab dhyaan se socho" — leave the physical world: drift to symmetric
        # left/right bodies and dim slightly (Earth shrinks to an abstract body).
        self.play(
            apple.animate.scale_to_fit_width(0.78).move_to(self.APPLE_SYM)
                 .set_opacity(0.85),
            earth.animate.scale_to_fit_width(0.95).move_to(self.EARTH_SYM)
                 .set_opacity(0.85),
            run_time=1.3, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)

        m_lab = MathTex("m", color=COLOR_m, font_size=46).next_to(apple, DOWN, buff=0.3)
        M_lab = MathTex("M", color=COLOR_M, font_size=46).next_to(earth, DOWN, buff=0.3)
        self.play(FadeIn(m_lab, shift=UP * 0.1), FadeIn(M_lab, shift=UP * 0.1),
                  run_time=0.6)

        # The relation we already earned (apple's bookkeeping): F ∝ m, m coral.
        eq_m = prop_eq("m", COLOR_m).to_edge(UP, buff=1.0)
        self.play(Write(eq_m), run_time=0.8)
        self.play(eq_m.mass.animate.scale(1.22), run_time=0.5,
                  rate_func=rate_functions.there_and_back)   # the m glows
        self.wait(0.4)

        # The literal axis of symmetry, straight down the middle.
        axis = DashedLine([0, 2.5, 0], [0, -1.9, 0], color=COLOR_WHITE,
                          stroke_width=2, dash_length=0.14).set_opacity(0.5)
        self.play(Create(axis), run_time=0.6)

        y = self.BODY_Y
        arr_l = Arrow([-2.35, y, 0], [-0.45, y, 0], buff=0, color=COLOR_VEC_F,
                      stroke_width=4, max_tip_length_to_length_ratio=0.16)
        arr_r = Arrow([ 2.35, y, 0], [ 0.45, y, 0], buff=0, color=COLOR_CORAL,
                      stroke_width=4, max_tip_length_to_length_ratio=0.16)
        self.play(GrowArrow(arr_l), GrowArrow(arr_r), run_time=0.6)
        self.wait(0.6)

        self.play(FadeOut(arr_l), FadeOut(arr_r), FadeOut(eq_m), run_time=0.3)
        apple_grp = Group(apple, m_lab)
        earth_grp = Group(earth, M_lab)

        SQUASH = 0.03
        self.play(
            apple_grp.animate.stretch(SQUASH, 0).move_to([-0.12, y, 0]),
            earth_grp.animate.stretch(SQUASH, 0).move_to([ 0.12, y, 0]),
            run_time=0.42, rate_func=rate_functions.ease_in_sine)
        self.play(
            apple_grp.animate.stretch(1 / SQUASH, 0).move_to(self.EARTH_SYM),
            earth_grp.animate.stretch(1 / SQUASH, 0).move_to(self.APPLE_SYM),
            run_time=0.42, rate_func=rate_functions.ease_out_sine)
        self.wait(0.4)

        # The flipped situation is identical — so it DEMANDS its own relation.
        # F ∝ m  (apple's view, kept on top)  vs  F ∝ M  (Earth's view, below).
        eq_m_top = prop_eq("m", COLOR_m).to_edge(UP, buff=1.0)
        self.play(Write(eq_m_top), run_time=0.6)
        eq_M = prop_eq("M", COLOR_M).next_to(eq_m_top, DOWN, buff=0.45)
        src = eq_m_top.copy()
        self.play(TransformMatchingTex(src, eq_M), run_time=0.9)  # m morphs to M
        self.wait(0.9)   # let the two relations contradict each other

        # "dono same role play kar rahe hain" — they lean together, demanding
        # to be reconciled (which Act 3 does).
        self.play(eq_m_top.animate.shift(DOWN * 0.12),
                  eq_M.animate.shift(UP * 0.12),
                  run_time=0.6, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)


        # Slide the two relations to centre — they want to merge.
        pair = VGroup(eq_m_top, eq_M)
        self.play(FadeOut(apple), FadeOut(earth), FadeOut(m_lab),
                  FadeOut(M_lab), FadeOut(axis),
                  pair.animate.move_to(ORIGIN).scale(1.1),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)

        # MERGE: the m and M the viewer already knows travel into one relation,
        # a "·" snapping between them with a magnetic click. F ∝ M·m.
        self.play(FadeOut(eq_m_top[0]), FadeOut(eq_m_top[1]), run_time=0.3)  # drop dup "F ∝"
        dot = MathTex(r"\cdot", font_size=60, color=COLOR_WHITE)
        dot.next_to(eq_M.mass, RIGHT, buff=0.14)
        self.play(
            eq_m_top.mass.animate.next_to(dot, RIGHT, buff=0.14),
            FadeIn(dot, scale=0.3),
            run_time=0.7, rate_func=rate_functions.ease_in_out_cubic)
        self.play(Flash(dot.get_center(), color=COLOR_WHITE, line_length=0.13,
                        num_lines=8, flash_radius=0.26), run_time=0.3)  # click
        product = VGroup(eq_M[0], eq_M[1], eq_M.mass, dot, eq_m_top.mass)
        self.wait(0.6)

        self.play(product.animate.to_edge(UP, buff=1.0), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)

        # Left panel: the tempting "+" → two segments laid end-to-end (a length).
        plus_eq = MathTex("M", "+", "m", font_size=46)
        plus_eq[0].set_color(COLOR_M); plus_eq[1].set_color(COLOR_WHITE)
        plus_eq[2].set_color(COLOR_m)
        plus_eq.move_to([-3.0, 0.0, 0]).set_opacity(0.55)

        # Right panel: the law's "·" → the rectangle (an area).
        prod_eq = MathTex("M", r"\cdot", "m", font_size=46)
        prod_eq[0].set_color(COLOR_M); prod_eq[1].set_color(COLOR_WHITE)
        prod_eq[2].set_color(COLOR_m)
        prod_eq.move_to([3.0, 0, 0])


        self.play(FadeIn(plus_eq, shift=UP * 0.1),
                  FadeIn(prod_eq, shift=UP * 0.1), run_time=0.6)

        # The unresolved question — the cliffhanger into the next scene.
        q = MathTex("?", color=COLOR_AMBER, font_size=110).move_to([0, 0, 0])
        self.play(FadeIn(q, scale=0.4), run_time=0.5)
        self.play(q.animate.scale(1.18), run_time=0.9,
                  rate_func=rate_functions.there_and_back)
        self.play(q.animate.scale(1.18), run_time=0.9,
                  rate_func=rate_functions.there_and_back)
        self.wait()
