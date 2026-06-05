from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE  (series-consistent canvas kept identical)
# ─────────────────────────────────────────────
COLOR_BG        = "#0E1117"   # near-black canvas (unchanged from the series)
COLOR_GROUND    = "#8E8E93"   # desaturated grey — the "exam / mechanical" world
COLOR_WHITE     = "#E5E5EA"   # F / the result
COLOR_DIM       = "#3A3F47"   # ghost stroke / unlit "dark zone"
COLOR_VEC_F     = "#FF3B30"   # red — force (carried over from the series)

# ── locked semantic colours for the gravitation series ──
COLOR_M         = "#007AFF"   # blue  — the big mass M
COLOR_m         = "#FFCC00"   # amber — the small mass m   (blue vs amber: multiply-vs-add reads instantly)
COLOR_R         = "#34C759"   # green — distance r
COLOR_G_GOLD    = "#E8B53A"   # warm antique gold — the mysterious constant G (its own colour)

# ── editable copy (on-screen captions). Series rule = English on screen.
#    Swap to Hinglish here if you want the spoken phrasing baked in. ──
QUESTION_TEXT = "A satellite of mass 200 kg orbits Earth\nat radius 7.0 × 10\u2076 m.  Find the gravitational force."
QUESTIONS = [
    "Why multiply, not add?",
    "Why squared?",
    "Why weaker with distance?",
    "Where did G come from?",
]

# ── historical overlay assets (you arrange the files next to the script).
#    Missing files degrade to a labelled placeholder so the scene still renders. ──
IMG_CAVENDISH = "Cavendish_Experiment.png"   # Cavendish torsion-balance plate (Act 3d)
IMG_PRINCIPIA = "Newton's_Principia_title_page.png"        # Newton's Principia page (Act 4)


# ═══════════════════════════════════════════════════════════════════
#  HELPERS  (matches the rest of the series — unchanged)
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


def check_mark(color=COLOR_GROUND, scale=0.5):
    """A satisfying tick that snaps in after the boxed answer."""
    m = VMobject(stroke_color=color, stroke_width=6)
    m.set_points_as_corners([
        LEFT * 0.18 + DOWN * 0.02, DOWN * 0.20, RIGHT * 0.30 + UP * 0.26,
    ])
    return m.scale(scale)


def build_formula(fs=60):
    """F = GMm/r² assembled from individually addressable glyphs.
    Returns a VGroup with named handles so every act can grab single symbols."""
    F    = MathTex("F", font_size=fs, color=COLOR_WHITE)
    eq   = MathTex("=", font_size=fs, color=COLOR_WHITE)
    G    = MathTex("G", font_size=fs, color=COLOR_WHITE)
    M    = MathTex("M", font_size=fs, color=COLOR_WHITE)
    mm   = MathTex("m", font_size=fs, color=COLOR_WHITE)
    r2   = MathTex(r"r^2", font_size=fs, color=COLOR_WHITE)
    # expose sub-glyphs: [0][0] = r, [0][1] = 2
    r    = r2[0][0]
    exp  = r2[0][1]

    num = VGroup(G, M, mm).arrange(RIGHT, buff=0.10)
    den = r2

    bar_w = max(num.width, den.width) + 0.28
    bar = Line(LEFT * bar_w / 2, RIGHT * bar_w / 2, stroke_width=3, color=COLOR_WHITE)
    num.next_to(bar, UP, buff=0.12)
    den.next_to(bar, DOWN, buff=0.12)
    frac = VGroup(num, bar, den)

    whole = VGroup(F, eq, frac).arrange(RIGHT, buff=0.22)

    whole.F, whole.eq, whole.G, whole.M, whole.m = F, eq, G, M, mm
    whole.r, whole.exp, whole.bar = r, exp, bar
    whole.num, whole.den, whole.frac = num, den, frac
    # keep r2 as handle so Act 2 can animate the full r^2 term
    whole.r2 = r2
    return whole

class Scene0_GravitationColdOpen(MovingCameraScene):

    # fixed bands — every act reads from these, so nothing free-floats
    STRIP_Y = UP * 3.0          # the mystery-strip spine
    SUB_Y   = UP * 1.7          # the subtitle band
    STAGE   = DOWN * 0.4        # the single centre-stage anchor
    CELL_X  = {"M": LEFT * 4.6, "m": LEFT * 1.55,
               "r2": RIGHT * 1.55, "G": RIGHT * 4.6}

    def construct(self):
        np.random.seed(7)   # deterministic scatter → preserves Manim's render cache
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.camera.frame.save_state()

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · EXAM MODE — the formula as a vending machine
        # ══════════════════════════════════════════════════════════
        question = Text(QUESTION_TEXT, font="Segoe UI", font_size=24,
                        color=COLOR_WHITE, line_spacing=0.9)
        question.to_edge(UP, buff=0.7).set_z_index(5)
        

        formula = build_formula(fs=56)
        formula.set_color(COLOR_WHITE)
        formula.set_z_index(5)
        self.play(Write(formula), run_time=4, rate_func=rate_functions.ease_out_cubic)
        self.wait()

        self.play(FadeIn(question, shift=DOWN * 0.15))
        self.wait()

        # Numbers cascade into their slots — robotic, almost automated.
        tags = VGroup(
            MathTex(r"6.674\times10^{-11}", font_size=34, color=COLOR_GROUND).next_to(formula.G, UL, buff=0.55),
            MathTex(r"6.0\times10^{24}",   font_size=34, color=COLOR_GROUND).next_to(formula.M, UP, buff=0.55),
            MathTex(r"200",                font_size=34, color=COLOR_GROUND).next_to(formula.m, UR, buff=0.55),
            MathTex(r"7.0\times10^{6}",    font_size=34, color=COLOR_GROUND).next_to(formula.den, DOWN, buff=0.45),
        ).set_z_index(5)
        srcs = [formula.G, formula.M, formula.m, formula.den]
        # top three tags sit above their symbols; bottom tag sits below den
        src_anchors = [s.get_top() for s in srcs[:3]] + [srcs[3].get_bottom()]
        tag_anchors = [t.get_bottom() for t in tags[:3]] + [tags[3].get_top()]
        connectors = VGroup(*[
            DashedLine(sa, ta, color=COLOR_GROUND,
                       stroke_width=1.2, stroke_opacity=0.4, dash_length=0.06)
            for sa, ta in zip(src_anchors, tag_anchors)
        ])
        self.play(
            LaggedStart(*[FadeIn(t, shift=DOWN * 0.18) for t in tags],
                        lag_ratio=0.18),
            LaggedStart(*[Create(c) for c in connectors], lag_ratio=0.18),
            run_time=1.0, rate_func=rate_functions.ease_out_quad,   # quick, mechanical
        )
        self.wait(0.2)

        # The answer STAMPS down to the right of the fraction (overshoot + settle).
        answer = MathTex(r"\approx 1634\ \text{N}", font_size=38, color=COLOR_WHITE)
        answer.next_to(formula, RIGHT, buff=0.55).set_z_index(6)
        self.play(FadeIn(answer.scale(1.6)), run_time=0.01)  # pre-place oversized
        self.play(answer.animate.scale(1 / 1.6), run_time=0.32,
                  rate_func=rate_functions.ease_out_back)     # the stamp
        box = SurroundingRectangle(answer, color=COLOR_GROUND, buff=0.16,
                                   stroke_width=2.5)
        tick = check_mark(COLOR_R).next_to(box, RIGHT, buff=0.18)
        self.play(Create(box), run_time=0.35)
        self.play(Create(tick), run_time=0.28,
                  rate_func=rate_functions.ease_out_back)      # ka-ching
        self.wait()

        exercise = VGroup(question, tags, connectors, answer, box, tick)
        self.play(
            FadeOut(exercise, shift=DOWN * 0.4),
            formula.animate.set_color(COLOR_WHITE).scale(1.4).move_to(ORIGIN),
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · LOOK CLOSER — the formula wakes, then becomes the spine
        # ══════════════════════════════════════════════════════════
        self.play(self.camera.frame.animate.scale(0.74).move_to(formula),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait()


        self.play(Restore(self.camera.frame),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_sine)
        
        # Highlight M and m, emphasize multiplication over addition
        self.play(
            formula.M.animate.scale(1.3).set_color(COLOR_M),
            formula.m.animate.scale(1.3).set_color(COLOR_m),
            run_time=0.4
        )
        
        # Shift m to the right to make room for the plus sign
        self.play(formula.m.animate.shift(RIGHT * 0.35), run_time=0.3)
        
        plus_sign = MathTex("+", font_size=50, color=COLOR_VEC_F)
        plus_sign.move_to((formula.M.get_right() + formula.m.get_left()) / 2)
        
        self.play(FadeIn(plus_sign, scale=0.5), run_time=0.3)
        self.wait(0.4)
        
        # Fade out plus and cross, shift m back
        self.play(
            FadeOut(plus_sign),
            formula.m.animate.shift(LEFT * 0.35),
            run_time=0.3
        )
        
        self.play(
            formula.M.animate.scale(1/1.3).set_color(COLOR_WHITE),
            formula.m.animate.scale(1/1.3).set_color(COLOR_WHITE),
            run_time=0.4
        )

        # Highlight r squared, emphasize squared over cubed or simple r
        self.play(
            formula.den.animate.scale(1.3).set_color(COLOR_R),
            run_time=0.4
        )
        self.wait(0.4)

        # Swap r^2 → r^3
        den_3 = MathTex(r"r^3", font_size=60, color=COLOR_R).scale(1.4)
        den_3.next_to(formula.bar, DOWN, buff=0.12)
        self.play(Transform(formula.den, den_3), run_time=0.3)
        self.wait(0.5)

        # Swap r^3 → r (no exponent)
        den_r = MathTex(r"r", font_size=60, color=COLOR_R).scale(1.4)
        den_r.next_to(formula.bar, DOWN, buff=0.12)
        self.play(Transform(formula.den, den_r), run_time=0.3)
        self.wait(0.5)

        # Swap r → r^2
        den_2 = MathTex(r"r^2", font_size=60, color=COLOR_R).scale(1.4)
        den_2.next_to(formula.bar, DOWN, buff=0.12)
        self.play(Transform(formula.den, den_2), run_time=0.3)
        self.wait(0.4)

        self.play(
            formula.den.animate.scale(1/1.3).set_color(COLOR_WHITE),
            run_time=0.4
        )

        # Highlight divide line and r squared
        self.play(
            formula.bar.animate.scale(1.15).set_color(COLOR_R),
            formula.den.animate.scale(1.3).set_color(COLOR_R),
            run_time=0.4
        )
        self.wait(0.6)
        self.play(
            formula.bar.animate.scale(1/1.15).set_color(COLOR_WHITE),
            formula.den.animate.scale(1/1.3).set_color(COLOR_WHITE),
            run_time=0.4
        )

        # Highlight G
        self.play(
            formula.G.animate.scale(1.3).set_color(COLOR_G_GOLD),
            run_time=0.4
        )

        digits = "0.00000000006674"
        num_grp = VGroup(*[MathTex(ch, font_size=42, color=COLOR_G_GOLD) for ch in digits])
        num_grp.arrange(RIGHT, buff=0.06)
        g_eq = MathTex("G =", font_size=42, color=COLOR_G_GOLD)
        
        # Group them to center properly just below the formula
        g_val_group = VGroup(g_eq, num_grp).arrange(RIGHT, buff=0.2)
        g_val_group.next_to(formula, DOWN, buff=0.6).set_z_index(8)

        self.play(FadeIn(g_eq), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.1) for d in num_grp],
                              lag_ratio=0.10), run_time=1.8)   # feel the smallness
        self.wait(0.6)

        self.play(
            formula.G.animate.scale(1/1.3).set_color(COLOR_WHITE),
            FadeOut(g_val_group, shift=DOWN * 0.1)
        )
        self.wait()

        # clear everything but the grid for the tools act
        act3_clear = Group(*[m for m in self.mobjects if m is not grid])
        self.play(FadeOut(act3_clear), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · NO SATELLITES, NO COMPUTERS, NO TELESCOPES
        # ══════════════════════════════════════════════════════════

        sat = self._icon_satellite().move_to(LEFT * 4.0 + UP * 0.4)
        lap = self._icon_laptop().move_to(UP * 0.4)
        tel = self._icon_telescope().move_to(RIGHT * 4.0 + UP * 0.4)
        icons = [sat, lap, tel]
        for ic in icons:
            ic.set_z_index(5)
        self.play(LaggedStart(*[FadeIn(ic, shift=UP * 0.15) for ic in icons],
                              lag_ratio=0.15), run_time=1.0)
        self.wait(0.5)

        # power them down: desaturate → "no" slash → dissolve to dust
        for ic in icons:
            slash = Line(ic.get_corner(UL) + UP * 0.1 + LEFT * 0.1,
                         ic.get_corner(DR) + DOWN * 0.1 + RIGHT * 0.1,
                         color=COLOR_VEC_F, stroke_width=5).set_z_index(6)
            self.play(ic.animate.set_color(COLOR_DIM).set_stroke(opacity=0.5),
                      run_time=0.35)
            self.play(Create(slash), run_time=0.3)
            dust = VGroup(*[Dot(ic.get_center()
                                + np.array([np.random.uniform(-0.3, 0.3),
                                            np.random.uniform(-0.3, 0.3), 0]),
                                radius=0.03, color=COLOR_DIM)
                            for _ in range(9)]).set_z_index(6)
            self.add(dust)
            self.play(
                FadeOut(ic, scale=0.6), FadeOut(slash),
                *[d.animate.shift(DOWN * np.random.uniform(0.4, 1.0)
                                  + RIGHT * np.random.uniform(-0.4, 0.4)).set_opacity(0)
                  for d in dust],
                run_time=0.7, rate_func=rate_functions.ease_in_quad,
            )
            self.remove(dust)

            self.wait(0.5)

    def _icon_satellite(self):
        body = RoundedRectangle(width=0.7, height=0.5, corner_radius=0.08,
                                stroke_color=COLOR_WHITE, stroke_width=3,
                                fill_opacity=0)
        panel_l = Rectangle(width=0.55, height=0.32, stroke_color=COLOR_WHITE,
                            stroke_width=3, fill_opacity=0).next_to(body, LEFT, buff=0.12)
        panel_r = Rectangle(width=0.55, height=0.32, stroke_color=COLOR_WHITE,
                            stroke_width=3, fill_opacity=0).next_to(body, RIGHT, buff=0.12)
        for p in (panel_l, panel_r):
            p.add(Line(p.get_top() + DOWN * 0.0, p.get_bottom(), color=COLOR_WHITE,
                       stroke_width=1.5))
        antenna = Line(body.get_top(), body.get_top() + UP * 0.4, color=COLOR_WHITE,
                       stroke_width=3)
        dish = Arc(radius=0.18, start_angle=PI * 0.15, angle=PI * 0.7,
                   color=COLOR_WHITE, stroke_width=3).next_to(antenna, UP, buff=0.0)
        return VGroup(panel_l, panel_r, body, antenna, dish)

    def _icon_laptop(self):
        screen = RoundedRectangle(width=1.1, height=0.72, corner_radius=0.05,
                                  stroke_color=COLOR_WHITE, stroke_width=3,
                                  fill_opacity=0)
        base = Polygon([-0.75, -0.36, 0], [0.75, -0.36, 0],
                       [0.6, -0.5, 0], [-0.6, -0.5, 0],
                       color=COLOR_WHITE, stroke_width=3, fill_opacity=0)
        return VGroup(screen, base)

    def _icon_telescope(self):
        tube = RoundedRectangle(width=1.0, height=0.28, corner_radius=0.1,
                                stroke_color=COLOR_WHITE, stroke_width=3,
                                fill_opacity=0).rotate(28 * DEGREES)
        eyepiece = Line(tube.get_start(), tube.get_start() + DOWN * 0.2 + LEFT * 0.1,
                        color=COLOR_WHITE, stroke_width=3)
        leg1 = Line(ORIGIN, DOWN * 0.5 + LEFT * 0.28, color=COLOR_WHITE, stroke_width=3)
        leg2 = Line(ORIGIN, DOWN * 0.5 + RIGHT * 0.28, color=COLOR_WHITE, stroke_width=3)
        legs = VGroup(leg1, leg2).next_to(tube, DOWN, buff=0.0)
        return VGroup(tube, eyepiece, legs)
