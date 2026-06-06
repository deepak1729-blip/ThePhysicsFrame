from manim import *
import numpy as np

def _get_parts_by_tex(self, search_string):
    """Returns a VGroup of all MathTex parts matching the exact string."""
    return VGroup(*[p for p in self if getattr(p, "tex_string", "") == search_string])

MathTex.get_parts_by_tex = _get_parts_by_tex

# ─────────────────────────────────────────────────────────────────────────
#  BRAND PALETTE  (carried verbatim from the series canvas; two new constants)
# ─────────────────────────────────────────────────────────────────────────
COLOR_BG        = "#0E1117"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_VEC_F     = "#FF3B30"   # red    — the centripetal pull / force
COLOR_VEC_V     = "#32ADE6"   # cyan   — velocity / the tangent "wants to go straight"
COLOR_GREEN     = "#34C759"   # green  — confirmation (and scene_6's distance r)
COLOR_AMBER     = "#FFCC00"   # amber  — Sun / the precious distance r / the payoff gold
COLOR_BLUE_BALL = "#007AFF"   # blue   — Earth (in Kepler's planet family)
COLOR_CORAL     = "#FF6F61"   # coral  — Jupiter (Kepler family) / accent
COLOR_DIM       = "#3A3F47"   # ghost / cancelled stroke
COLOR_ORBIT     = "#4A90D9"   # NEW    — the orbit track (a path, not a mass)
COLOR_KEPLER    = "#A78BFA"   # NEW    — RESERVED: Kepler's rule, the gift from the past

# This scene paints distance r GOLD (the breakdown's Act-7 motif: the r that
# cancels is the same gold as the planet). scene_6 used green for r — flip the
# line below to COLOR_GREEN if you want strict cross-scene continuity instead.
COLOR_DIST = COLOR_AMBER

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


def orbit_point(a, R):
    """Point on a circle of radius R at angle a, centred on the origin."""
    return np.array([R * np.cos(a), R * np.sin(a), 0.0])


PLANET_IMAGES = ["mercury.png", "venus.png", "earth.png", "mars.png"]


def make_sun(width=0.55):
    return ImageMobject("sun.png").scale_to_fit_width(width)


def make_planet(width=0.28, index=2):
    """Returns an ImageMobject for the planet at PLANET_IMAGES[index] (default: earth)."""
    return ImageMobject(PLANET_IMAGES[index]).scale_to_fit_width(width)


def frac(num, den, pad=0.24, sw=3, color=COLOR_WHITE):
    """A fraction bar between an already-built numerator and denominator.
    Returns a VGroup with .num/.bar/.den handles so glyphs stay addressable."""
    bar_w = max(num.width, den.width) + pad
    bar = Line(LEFT * bar_w / 2, RIGHT * bar_w / 2, stroke_width=sw, color=color)
    num.next_to(bar, UP, buff=0.12)
    den.next_to(bar, DOWN, buff=0.12)
    g = VGroup(num, bar, den)
    g.num, g.bar, g.den = num, bar, den
    return g


def safe_image(path, width, fallback_label):
    """ImageMobject with a labelled placeholder so the scene always renders
    even before the real asset is dropped next to the script (series convention)."""
    try:
        return ImageMobject(path).scale_to_fit_width(width)
    except Exception:
        box = Rectangle(width=width, height=width * 0.72, color=COLOR_GROUND,
                        stroke_width=1.5, fill_color=COLOR_BG, fill_opacity=0.92)
        lbl = Text(fallback_label, font=FONT, font_size=18, color=COLOR_GROUND)
        lbl.scale_to_fit_width(min(width * 0.82, lbl.width)).move_to(box)
        return VGroup(box, lbl)


def build_cf(fs=46):
    """F = m v² / r assembled from individually addressable glyphs.
    v is cyan (velocity), r is gold (the distance motif). Named handles let the
    substitution acts grab single symbols (.v, .v2, .r, .m, .bar)."""
    F  = MathTex("F", font_size=fs, color=COLOR_WHITE)
    eq = MathTex("=", font_size=fs, color=COLOR_WHITE)
    m  = MathTex("m", font_size=fs, color=COLOR_WHITE)
    v  = MathTex("v", font_size=fs, color=COLOR_VEC_V)
    v2 = MathTex("2", font_size=int(fs * 0.62), color=COLOR_VEC_V)
    r  = MathTex("r", font_size=fs, color=COLOR_DIST)

    mv = VGroup(m, v).arrange(RIGHT, buff=0.06)
    v2.next_to(v, UR, buff=0.0).shift(DOWN * 0.05 + LEFT * 0.02)
    num = VGroup(mv, v2)

    fr = frac(num, r)
    whole = VGroup(F, eq, fr).arrange(RIGHT, buff=0.20)
    whole.F, whole.eq, whole.m, whole.v, whole.v2 = F, eq, m, v, v2
    whole.r, whole.bar, whole.num, whole.frac = r, fr.bar, num, fr
    return whole


def build_v_eq(fs=44):
    """v = 2πr/T : cyan expression, but the r inside it glows gold (it is the
    precious distance, even when it lives inside the velocity). .rhs is the
    fraction; .r is the gold r so later acts can pluck it."""
    lhs = MathTex("v", font_size=fs, color=COLOR_VEC_V)
    eq  = MathTex("=", font_size=fs, color=COLOR_WHITE)
    twopi = MathTex(r"2\pi", font_size=fs, color=COLOR_VEC_V)
    r   = MathTex("r", font_size=fs, color=COLOR_DIST)
    num = VGroup(twopi, r).arrange(RIGHT, buff=0.06)
    T   = MathTex("T", font_size=fs, color=COLOR_WHITE)
    fr  = frac(num, T, color=COLOR_VEC_V)            # cyan bar = velocity expression
    whole = VGroup(lhs, eq, fr).arrange(RIGHT, buff=0.16)
    whole.lhs, whole.eq, whole.rhs, whole.r, whole.T = lhs, eq, fr, r, T
    return whole


def tinted(mt):
    """Recolour an isolated MathTex: everything white, r→gold, v→cyan, T→white."""
    mt.set_color(COLOR_WHITE)
    for p in mt.get_parts_by_tex("r"):
        p.set_color(COLOR_DIST)
    for p in mt.get_parts_by_tex("v"):
        p.set_color(COLOR_VEC_V)
    return mt


# ═══════════════════════════════════════════════════════════════════════════
class Scene_7_KeplerToInverseSquare(MovingCameraScene):

    # ── locked geometry ──
    R_ORBIT = 1.9
    SUN_L   = LEFT * 3.4 + DOWN * 0.1     # parked Sun centre for the split-screen
    EQ_C    = RIGHT * 3.0 + UP * 0.4      # equation zone (right of the orbit)

    def construct(self):
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        self.act1_inertia_vs_pull()
        self.act2_centripetal_formula()
        self.act3_period()
        self.act4_substitute()
        self.act5_the_gap()
        self.act6_kepler_gift()
        self.act7_the_cancellation()

    def _clear_to_grid(self, run_time=1.0):
        clear = Group(*[m for m in self.mobjects if m is not self.grid])
        if len(clear):
            self.play(FadeOut(clear), run_time=run_time,
                      rate_func=rate_functions.ease_in_out_sine)

    # helpers that read the CURRENT (frozen) orbit state ----------------------
    def _planet_P(self):
        return self.sun.get_center() + orbit_point(self.ang.get_value(), self.R_ORBIT)

    def _vel_arrow(self, length=1.05):
        a = self.ang.get_value()
        P = self._planet_P()
        tdir = np.array([-np.sin(a), np.cos(a), 0])      # CCW tangent
        return Arrow(P, P + tdir * length, buff=0, color=COLOR_VEC_V,
                     stroke_width=4, max_tip_length_to_length_ratio=0.26)

    def _radius_line(self):
        return DashedLine(self.sun.get_center(), self._planet_P(),
                          color=COLOR_DIST, stroke_width=3, dash_length=0.12)

    # ===================================================================== A1
    def act1_inertia_vs_pull(self):
        # ── "Seedha space mein nikal jaata." Inertia vs. the pull. ──
        R = self.R_ORBIT
        self.ang = ValueTracker(-55 * DEGREES)
        self.sun = make_sun().move_to(ORIGIN).set_z_index(2)

        # The Sun materialises and gives one slow, living breath.
        self.play(FadeIn(self.sun, scale=0.5), run_time=1.0,
                  rate_func=rate_functions.ease_out_sine)
        self.play(self.sun.animate.scale(1.07), run_time=1.0,
                  rate_func=rate_functions.there_and_back)

        # The planet fades in already on its orbit, then eases to a freeze.
        self.planet = make_planet().move_to(self._planet_P()).set_z_index(3)
        self.play(FadeIn(self.planet, scale=0.5), run_time=0.7)
        self.planet.add_updater(lambda m: m.move_to(self._planet_P()))
        self.play(self.ang.animate.set_value(-18 * DEGREES),
                  run_time=1.3, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)                                    # frozen mid-orbit

        # The natural tendency: a cyan tangent, and a ghost that drifts off it.
        a = self.ang.get_value()
        P = self._planet_P()
        tdir = np.array([-np.sin(a), np.cos(a), 0])
        tangent = DashedLine(P, P + tdir * 3.6, color=COLOR_VEC_V,
                             stroke_width=3, dash_length=0.14)
        ghost = make_planet().move_to(P).set_opacity(0.55)
        self.play(Create(tangent), run_time=0.8)
        self.play(ghost.animate.move_to(P + tdir * 2.1).set_opacity(0.30),
                  tangent.animate.set_stroke(opacity=0.5),
                  run_time=1.5, rate_func=rate_functions.ease_out_sine)
        self.wait(1.6)                                    # let inertia hang

        # The rubber-band snap: ghost yanked home, orbit closes, the pull appears.
        orbit = Circle(radius=R, color=COLOR_ORBIT, stroke_width=2
                       ).move_to(self.sun.get_center())
        toward = self.sun.get_center() - P
        toward = toward / np.linalg.norm(toward)
        f_arrow = Arrow(P, P + toward * 0.95, buff=0, color=COLOR_VEC_F,
                        stroke_width=4, max_tip_length_to_length_ratio=0.28
                        ).set_z_index(4)
        f_lab = MathTex("F", color=COLOR_VEC_F, font_size=40
                        ).next_to(f_arrow.get_center(), UR, buff=0.10)
        self.play(ghost.animate.move_to(P).set_opacity(0.0),
                  FadeOut(tangent),
                  Create(orbit),
                  run_time=0.7, rate_func=rate_functions.ease_in_back)  # the snap
        self.remove(ghost)
        self.play(GrowArrow(f_arrow), FadeIn(f_lab, shift=DOWN * 0.05),
                  run_time=0.6)
        self.orbit = orbit
        self.wait(0.8)

        # The planet resumes — a slow quarter-turn, the pull tracking inward.
        f_live = always_redraw(lambda: (lambda P=self._planet_P(): Arrow(
            P, P + (self.sun.get_center() - P) /
            np.linalg.norm(self.sun.get_center() - P) * 0.95,
            buff=0, color=COLOR_VEC_F, stroke_width=4,
            max_tip_length_to_length_ratio=0.28))())
        self.play(FadeOut(f_arrow), FadeOut(f_lab), run_time=0.2)
        self.add(f_live)
        self.play(self.ang.animate.increment_value(70 * DEGREES),
                  run_time=2.0, rate_func=rate_functions.ease_in_out_sine)
        f_live.clear_updaters()
        self.play(FadeOut(f_live), run_time=0.3)
        self.wait(0.4)

    # ===================================================================== A2
    def act2_centripetal_formula(self):
        # ── "Formula Newton ko pehle se pata tha." Open the equation zone. ──
        # Slide the whole orbit system left; the planet rides along (updater).
        shift = self.SUN_L - self.sun.get_center()
        self.play(self.sun.animate.shift(shift), self.orbit.animate.shift(shift),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)

        formula = build_cf(fs=48).move_to(self.EQ_C)
        self.formula = formula

        # F = , and the bar of the fraction.
        self.play(FadeIn(formula.F, shift=RIGHT * 0.1),
                  FadeIn(formula.eq, shift=RIGHT * 0.1), run_time=0.5)
        self.play(Create(formula.bar), run_time=0.3)

        # m → a thin pointer flicks to the planet, then leaves (no on-screen word).
        self.play(FadeIn(formula.m, shift=DOWN * 0.12), run_time=0.4)
        m_ptr = Arrow(formula.m.get_corner(DL) + DL * 0.05,
                      self.planet.get_center() + UR * 0.12, buff=0.15,
                      color=COLOR_WHITE, stroke_width=2.5, stroke_opacity=0.7,
                      max_tip_length_to_length_ratio=0.06)
        self.play(GrowArrow(m_ptr), self.planet.animate.scale(1.18), run_time=0.5)
        self.play(self.planet.animate.scale(1 / 1.18), FadeOut(m_ptr), run_time=0.4)

        # v → the cyan velocity arrow is born at the planet.
        self.play(FadeIn(formula.v, shift=DOWN * 0.12),
                  FadeIn(formula.v2, shift=DOWN * 0.12), run_time=0.4)
        self.vel = self._vel_arrow()
        self.play(GrowArrow(self.vel), run_time=0.6)

        # r → the gold radius is drawn from Sun to planet (plants the motif).
        self.play(FadeIn(formula.r, shift=UP * 0.12), run_time=0.4)
        self.rad = self._radius_line()
        self.play(Create(self.rad), run_time=0.6)
        self.wait(0.7)

        # The problem surfaces: a "?" blinks over v, and v dims — "we can't grab it".
        q = MathTex("?", color=COLOR_VEC_V, font_size=42
                    ).next_to(formula.v, UP, buff=0.16)
        self.play(FadeIn(q, scale=0.4), run_time=0.20)
        self.play(FadeOut(q, scale=0.4),
                  VGroup(formula.v, formula.v2).animate.set_opacity(0.40),
                  run_time=0.30)
        self.wait(0.9)

    # ===================================================================== A3
    def act3_period(self):
        # ── "T: woh cheez jo hum naap sakte hain." One full, deliberate loop. ──
        start = self.ang.get_value()

        # Fade the static spokes; let the bare loop be the whole story.
        self.play(FadeOut(self.vel), self.rad.animate.set_opacity(0.22),
                  run_time=0.4)

        # A faint white trace draws itself as the planet runs exactly one orbit.
        trace = TracedPath(self.planet.get_center, stroke_color=COLOR_WHITE,
                           stroke_width=2.5, stroke_opacity=0.7)
        self.add(trace)
        # Uniform circular motion ⇒ constant speed ⇒ linear is the honest easing.
        self.play(self.ang.animate.set_value(start + TAU),
                  run_time=3.4, rate_func=linear)
        self.wait(0.3)

        # T lands at the return-to-start point, with a small tick.
        P0 = self._planet_P()
        tick = Line(P0 + UP * 0.16, P0 + DOWN * 0.16, color=COLOR_WHITE,
                    stroke_width=2.5).rotate(self.ang.get_value())
        T_lab = MathTex("T", color=COLOR_WHITE, font_size=36
                        ).next_to(P0, UR, buff=0.12)
        self.play(Create(tick), FadeIn(T_lab, scale=0.6), run_time=0.5)
        self.play(T_lab.animate.scale(1.18), run_time=0.4,
                  rate_func=rate_functions.there_and_back)
        self.wait(0.5)

        # The key under the doormat: v = 2πr/T writes itself in the corner.
        v_eq = build_v_eq(fs=44).move_to(self.EQ_C + DOWN * 2.0)
        self.v_eq = v_eq
        q = MathTex("?", color=COLOR_VEC_V, font_size=44).move_to(v_eq.rhs)
        self.play(FadeIn(v_eq.lhs, shift=RIGHT * 0.1),
                  FadeIn(v_eq.eq, shift=RIGHT * 0.1),
                  FadeIn(q, scale=0.5), run_time=0.5)
        # the "?" dissolves into the measured expression
        self.play(FadeOut(q, scale=1.4), run_time=0.25)
        self.play(Write(v_eq.rhs), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)
        self.play(VGroup(v_eq.r).animate.scale(1.22), run_time=0.5,
                  rate_func=rate_functions.there_and_back)   # the gold r winks
        self.wait(0.7)

        # tidy the loop trace + tick; keep both equations for the substitution
        self.play(FadeOut(trace), FadeOut(tick), FadeOut(T_lab),
                  self.rad.animate.set_opacity(0.0), run_time=0.6)
        self.remove(self.rad)

    # ===================================================================== A4
    def act4_substitute(self):
        # ── "Daal do, simplify karo." Algebra-in-motion. Orbit dims to 30%. ──
        self.diagram = Group(self.sun, self.orbit, self.planet)
        self.play(self.diagram.animate.set_opacity(0.30),
                  self.formula.animate.move_to(UP * 0.9),
                  self.v_eq.animate.scale(0.9).to_corner(DR, buff=0.7)
                       .set_opacity(0.5),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)

        # Lock-and-key: pulse v, then slide a copy of 2πr/T onto the v-slot.
        self.play(VGroup(self.formula.v, self.formula.v2).animate
                  .set_opacity(1.0).set_color(COLOR_VEC_V).scale(1.12),
                  run_time=0.4)
        key = self.v_eq.rhs.copy().set_opacity(0.9)
        self.play(key.animate.scale(0.62).move_to(self.formula.v),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_cubic)

        # State B: F = m (2πr/T)² / r  — the v is now the cyan expression, squared.
        B = MathTex(
            "F", "=",
            r"\frac{", "m", r"\left( \frac{", r"2\pi", r"\,", "r", "}{", "T", r"} \right)^{2}}{", "r", "}",
            font_size=46
        )
        tinted(B)
        for p in B.get_parts_by_tex(r"2\pi"):
            p.set_color(COLOR_VEC_V)
        B.move_to(UP * 0.9)
        
        self.play(FadeOut(key, scale=0.4),
                  ReplacementTransform(self.formula, B),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_cubic)
        self.wait(0.7)

        # State C: expand the square → 4π² m r² / (T² r). 4π² is "just a number".
        C = MathTex(
            "F", "=", 
            r"\frac{", r"4\pi^{2}", r"\,", "m", r"\,", "r", r"^{2}}{", "T", r"^{2}\,", "r", "}",
            font_size=46
        )
        tinted(C)
        C.move_to(UP * 0.9)
        self.play(ReplacementTransform(B, C), run_time=0.9)
        self.wait(0.4)

        const = C.get_parts_by_tex(r"4\pi^{2}")
        box = SurroundingRectangle(const, color=COLOR_GROUND, buff=0.08,
                                   stroke_width=2)
        note = Text("just a number", font=FONT, slant=ITALIC,
                    color=COLOR_GROUND, font_size=22).next_to(box, UP, buff=0.18)
        self.play(Create(box), FadeIn(note, shift=DOWN * 0.08), run_time=0.6)
        self.play(const.animate.set_color(COLOR_DIM).set_opacity(0.5),
                  run_time=0.5)
        self.wait(0.5)

        # State D: drop the constant → F ∝ m r² / (T² r).
        D = MathTex(
            "F", r"\propto", 
            r"\frac{", "m", r"\,", "r", r"^{2}}{", "T", r"^{2}\,", "r", "}",
            font_size=46
        )
        tinted(D)
        D.move_to(UP * 0.9)
        self.play(FadeOut(box), FadeOut(note), ReplacementTransform(C, D),
                  run_time=0.9)
        self.wait(0.5)

        # The cancellation: one r upstairs, one r downstairs — both gold, struck.
        rs = D.get_parts_by_tex("r")            # [ r (num, the base of r²), r (den) ]
        r_num, r_den = rs[0], rs[-1]
        self.play(r_num.animate.scale(1.28), r_den.animate.scale(1.28),
                  run_time=0.4, rate_func=rate_functions.ease_out_cubic)
        sl_n = Line(r_num.get_corner(UL) + UL * 0.04,
                    r_num.get_corner(DR) + DR * 0.04,
                    color=COLOR_DIST, stroke_width=3)
        sl_d = Line(r_den.get_corner(UL) + UL * 0.04,
                    r_den.get_corner(DR) + DR * 0.04,
                    color=COLOR_DIST, stroke_width=3)
        self.play(Create(sl_n), Create(sl_d), run_time=0.45)
        self.play(VGroup(r_num, r_den, sl_n, sl_d).animate
                  .set_color(COLOR_DIM).set_opacity(0.35), run_time=0.5)
        self.wait(0.3)

        # State E: the survivor — F ∝ m r / T². Hold; the viewer reads it.
        E = MathTex(
            "F", r"\propto", 
            r"\frac{", "m", r"\,", "r", "}{", "T", r"^{2}}",
            font_size=52
        )
        tinted(E)
        E.move_to(UP * 0.9)
        self.eqE = E
        self.play(ReplacementTransform(VGroup(D, sl_n, sl_d), E),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_cubic)
        self.play(E.animate.scale(1.08), run_time=0.5,
                  rate_func=rate_functions.there_and_back)
        self.wait(0.8)

        # the corner v = 2πr/T has done its job — retire it
        self.play(FadeOut(self.v_eq), run_time=0.4)

    # ===================================================================== A5
    def act5_the_gap(self):
        # ── "Aur yahan dikkat aayegi." T² is downstairs; I need r. ──
        E = self.eqE
        Tpart = E.get_parts_by_tex("T")
        ring = SurroundingRectangle(Tpart, color=COLOR_VEC_F, buff=0.16,
                                    corner_radius=0.10, stroke_width=3)
        self.play(Create(ring), run_time=0.5)
        self.play(ring.animate.scale(1.12), run_time=0.55,
                  rate_func=rate_functions.there_and_back)      # a blinking cursor

        # a question mark surfaces below T², then fades
        q = MathTex("?", color=COLOR_VEC_F, font_size=46
                    ).next_to(ring, DOWN, buff=0.22)
        self.play(FadeIn(q, shift=UP * 0.1), run_time=0.4)
        self.wait(0.6)
        self.play(FadeOut(q), FadeOut(ring), run_time=0.4)

        # The deliberate friction: dim the equation and let the screen breathe.
        self.play(E.animate.set_opacity(0.45), run_time=0.6)
        self.wait(1.0)

        # The ONE historical cut: drop kepler.png next to the script.
        engraving = safe_image("kepler.png", 4.6,
                               "kepler.png")
        engraving.move_to(DOWN * 0.4).set_z_index(20)
        cap = Text("the answer comes from data, not algebra", font=FONT,
                   slant=ITALIC, color=COLOR_GROUND, font_size=22)
        cap.next_to(engraving, DOWN, buff=0.25).set_z_index(20)
        self.play(FadeIn(engraving, scale=0.96), FadeIn(cap, shift=UP * 0.1),
                  run_time=0.8, rate_func=rate_functions.ease_out_sine)
        self.wait(1.5)
        self.play(FadeOut(engraving), FadeOut(cap), run_time=0.7)
        self.wait(0.3)

    # ===================================================================== A6
    def act6_kepler_gift(self):
        # ── "Kepler ka tohfa." Give it its own visual language. ──
        E = self.eqE
        # Park F ∝ mr/T² up top, dimmed — it waits for its missing piece.
        self.play(E.animate.scale(0.8).to_edge(UP, buff=0.55).set_opacity(0.5),
                  FadeOut(self.diagram), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)

        # A small planet family, real relative speeds (Kepler: ω ∝ r^-1.5).
        C = LEFT * 3.4 + DOWN * 0.2
        sun_k = make_sun(0.26).move_to(C).set_z_index(2)
        radii   = [0.85, 1.55, 2.45]
        # Mercury (0), Venus (1), Earth (2) — inner to outer, matching PLANET_IMAGES indices
        p_idx   = [0, 1, 2]
        p_sizes = [0.13, 0.16, 0.15]
        phase   = [0.4, 2.1, 4.0]
        w0 = 1.0
        w = [w0 * (radii[0] / r) ** 1.5 for r in radii]

        rings = VGroup(*[
            DashedVMobject(Circle(radius=r, color=COLOR_ORBIT, stroke_width=1.6),
                           num_dashes=64).set_stroke(opacity=0.4).move_to(C)
            for r in radii])
        kt = ValueTracker(0.0)
        planets = []
        for i, (r, ph, idx, sz) in enumerate(zip(radii, phase, p_idx, p_sizes)):
            p = make_planet(width=sz, index=idx)
            p.move_to(C + orbit_point(ph, r)).set_z_index(3)
            p.add_updater(lambda m, i=i, r=r, ph=ph:
                          m.move_to(C + orbit_point(ph + kt.get_value() * w[i], r)))
            planets.append(p)

        self.play(FadeIn(sun_k, scale=0.6),
                  LaggedStart(*[Create(rg) for rg in rings], lag_ratio=0.2),
                  run_time=1.2)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in planets],
                              lag_ratio=0.15), run_time=0.8)
        # let the family run — inner fast, outer slow
        self.play(kt.animate.set_value(7.0), run_time=4.0, rate_func=linear)

        # Kepler's rule writes itself in lavender.
        law_k = MathTex("T^{2}", r"\propto", "r^{3}", font_size=64,
                        color=COLOR_KEPLER).move_to(RIGHT * 3.0 + UP * 2.1)
        self.play(Write(law_k), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        # A tiny graph: T² vs r³ — three planets, one lavender line through O.
        o = RIGHT * 1.9 + DOWN * 1.9
        x_ax = Arrow(o, o + RIGHT * 3.4, buff=0, color=COLOR_GROUND,
                     stroke_width=2.2, max_tip_length_to_length_ratio=0.05)
        y_ax = Arrow(o, o + UP * 3.2, buff=0, color=COLOR_GROUND,
                     stroke_width=2.2, max_tip_length_to_length_ratio=0.05)
        x_lab = MathTex("r^{3}", color=COLOR_GROUND, font_size=28
                        ).next_to(x_ax, RIGHT, buff=0.12)
        y_lab = MathTex("T^{2}", color=COLOR_GROUND, font_size=28
                        ).next_to(y_ax, UP, buff=0.10)
        self.play(Create(x_ax), Create(y_ax), FadeIn(x_lab), FadeIn(y_lab),
                  run_time=0.7)

        # T² ∝ r³ ⇒ the points sit exactly on a straight line through the origin.
        dot_cols = [COLOR_GROUND, COLOR_CORAL, COLOR_BLUE_BALL]  # Mercury / Venus / Earth
        fracs = [0.30, 0.58, 0.88]
        line_dir = (RIGHT * 3.0 + UP * 2.8)
        data = VGroup()
        for i, f in enumerate(fracs):
            pt = o + line_dir * f
            data.add(Dot(pt, radius=0.075, color=dot_cols[i]))
        line = Line(o, o + line_dir * 0.98, color=COLOR_KEPLER, stroke_width=3)

        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in data],
                              lag_ratio=0.25), run_time=1.0)
        self.play(Create(line), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(law_k.animate.scale(1.12), run_time=0.5,
                  rate_func=rate_functions.there_and_back)
        self.wait(1.0)

        # Dissolve the family + graph; the lavender law travels up beside F∝mr/T².
        for p in planets:
            p.clear_updaters()
        kep_target = MathTex("T^{2}", r"\propto", "r^{3}", font_size=44,
                             color=COLOR_KEPLER)
        kep_target.next_to(E, DOWN, buff=0.35).align_to(E, LEFT)
        self.eqK = kep_target
        self.play(
            FadeOut(sun_k), FadeOut(rings), FadeOut(x_ax), FadeOut(y_ax),
            FadeOut(x_lab), FadeOut(y_lab), FadeOut(data), FadeOut(line),
            FadeOut(Group(*planets)),
            ReplacementTransform(law_k, kep_target),
            E.animate.set_opacity(1.0),
            run_time=1.1, rate_func=rate_functions.ease_in_out_sine)

        # Bring the single-orbit spine back, faded — we never truly left it.
        self.diagram.set_opacity(0.30)
        self.play(FadeIn(self.diagram), run_time=0.7)
        self.wait(0.6)

    # ===================================================================== A7
    def act7_the_cancellation(self):
        # ── "Newton ne Kepler ka rule uthaaya." The climax: replace T² with r³. ──
        E, K = self.eqE, self.eqK

        # Centre the two relations, side by side in the mind.
        pair = VGroup(E, K)
        self.play(FadeOut(self.diagram),
                  pair.animate.arrange(DOWN, buff=0.55).move_to(ORIGIN),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)

        # The T² in F∝mr/T² takes Kepler's lavender — the connection lights up.
        Tpart = E.get_parts_by_tex("T")
        self.play(Tpart.animate.set_color(COLOR_KEPLER).scale(1.12),
                  K.animate.scale(1.06), run_time=0.6,
                  rate_func=rate_functions.there_and_back)
        self.play(Tpart.animate.set_color(COLOR_KEPLER), run_time=0.2)

        # The transplant: a copy of Kepler's r³ lifts out and flies to the slot.
        r3 = K[2].copy()
        self.play(r3.animate.move_to(Tpart).scale(1.05),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_cubic)

        # State F: F ∝ m r / r³  (T² has become r³).
        F = MathTex(
            "F", r"\propto", 
            r"\frac{", "m", r"\,", "r", "}{", "r", r"^{3}}", 
            font_size=54
        )
        tinted(F)
        F.move_to(E)
        self.play(FadeOut(r3, scale=0.4),
                  ReplacementTransform(E, F),
                  K.animate.set_opacity(0.4).shift(DOWN * 0.2),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_cubic)
        self.wait(0.8)

        # The cancellation — both r's glow gold, struck together, dissolved.
        rs = F.get_parts_by_tex("r")          # [ r (num), r (den, base of r³) ]
        r_num, r_den = rs[0], rs[-1]
        self.play(r_num.animate.set_color(COLOR_AMBER).scale(1.30),
                  r_den.animate.set_color(COLOR_AMBER).scale(1.30),
                  run_time=0.5, rate_func=rate_functions.ease_out_cubic)
        sl_n = Line(r_num.get_corner(UL) + UL * 0.04,
                    r_num.get_corner(DR) + DR * 0.04,
                    color=COLOR_AMBER, stroke_width=3)
        sl_d = Line(r_den.get_corner(UL) + UL * 0.04,
                    r_den.get_corner(DR) + DR * 0.04,
                    color=COLOR_AMBER, stroke_width=3)
        self.play(Create(sl_n), Create(sl_d), run_time=0.45)
        self.play(VGroup(r_num, r_den, sl_n, sl_d).animate
                  .set_color(COLOR_DIM).set_opacity(0.3), run_time=0.5)
        self.wait(0.3)

        # State G: the earned result — F ∝ m / r², grown a touch and turned gold.
        G = MathTex(
            "F", r"\propto", 
            r"\frac{", "m", "}{", "r", r"^{2}}", 
            font_size=58
        )
        G.set_color(COLOR_WHITE)
        G.move_to(ORIGIN).scale(0.9)
        self.play(FadeOut(K), ReplacementTransform(VGroup(F, sl_n, sl_d), G),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_cubic)
        # subtle scale-up 0.9 → 1.0 and the whole expression resolves to gold
        self.play(G.animate.scale(1 / 0.9).set_color(COLOR_AMBER),
                  run_time=0.8, rate_func=rate_functions.ease_out_cubic)
        self.wait(1.2)

        # POST: single soft piano note lands here. Cut to black, hold 1.5 s.
        self.play(G.animate.scale(1.02), run_time=0.4,
                  rate_func=rate_functions.there_and_back)
        self.play(FadeOut(Group(*self.mobjects)), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.5)
