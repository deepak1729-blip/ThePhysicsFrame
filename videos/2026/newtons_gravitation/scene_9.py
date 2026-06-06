from manim import *
import numpy as np

# ─────────────────────────────────────────────────────────────────────────
#  THE PHYSICS FRAME · Gravitation series — CLOSING / EPILOGUE SCENE
#  "Chaar Log. Dedh Sau Saal. Ek Line."
#
#  This is the emotional landing strip. Five movements:
#    A1  Four medallions (Galileo · Kepler · Newton · Cavendish) light up.
#    A2  They fall inward like a gravitational well → dissolve → the LAW rises.
#    A3  Each term is unpacked as a "memory" the formula carries.
#    A4  The exam-stamp gag → the formula re-saturates like a sunrise.
#    A5  The universe reassembles around the equation → sign-off → fade to black.
#  Renders fully asset-free (every glyph is drawn). Swap in logo.png in A5 if
#  you want the real channel mark.
# ─────────────────────────────────────────────────────────────────────────

# ── BRAND PALETTE (series canvas, verbatim) ──
COLOR_BG        = "#0E1117"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_DIM       = "#3A3F47"
COLOR_VEC_F     = "#FF3B30"
COLOR_AMBER     = "#FFCC00"
COLOR_G_GOLD    = "#E8B53A"   # the mysterious constant G (its own gold)
COLOR_BLUE_BALL = "#007AFF"   # the masses M·m
COLOR_GREEN     = "#34C759"   # the inverse-square geometry r²
COLOR_MOON      = "#A8C4D4"

# Formula colour logic for THIS scene (per the director's note):
#   F = white · G = gold · M·m = blue · r² = green
# (scene_0 painted the small mass m amber — flip COLOR_BLUE_BALL→COLOR_AMBER on
#  the m handle below if you want strict continuity with that earlier choice.)

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


def build_formula(fs=60):
    """F = GMm/r² assembled from individually addressable glyphs (from scene_0).
    Named handles let every act grab single symbols (.G/.M/.m/.r/.exp/.bar)."""
    F   = MathTex("F", font_size=fs, color=COLOR_WHITE)
    eq  = MathTex("=", font_size=fs, color=COLOR_WHITE)
    G   = MathTex("G", font_size=fs, color=COLOR_WHITE)
    M   = MathTex("M", font_size=fs, color=COLOR_WHITE)
    mm  = MathTex("m", font_size=fs, color=COLOR_WHITE)
    r   = MathTex("r", font_size=fs, color=COLOR_WHITE)
    exp = MathTex("2", font_size=int(fs * 0.6), color=COLOR_WHITE)

    num = VGroup(G, M, mm).arrange(RIGHT, buff=0.10)
    exp.next_to(r, UR, buff=0.0).shift(DOWN * 0.04 + LEFT * 0.02)
    den = VGroup(r, exp)

    bar_w = max(num.width, den.width) + 0.28
    bar = Line(LEFT * bar_w / 2, RIGHT * bar_w / 2, stroke_width=3, color=COLOR_WHITE)
    num.next_to(bar, UP, buff=0.12)
    den.next_to(bar, DOWN, buff=0.12)
    frac = VGroup(num, bar, den)

    whole = VGroup(F, eq, frac).arrange(RIGHT, buff=0.22)
    whole.F, whole.eq, whole.G, whole.M, whole.m = F, eq, G, M, mm
    whole.r, whole.exp, whole.bar = r, exp, bar
    whole.num, whole.den, whole.frac = num, den, frac
    return whole


def make_medallion(name, accent, radius=0.66):
    """A glowing 'monument' name-card: soft halo + ringed disc + serif name."""
    g = VGroup()
    for rm, op in [(1.70, 0.05), (1.38, 0.08), (1.14, 0.12)]:
        g.add(Dot(ORIGIN, radius=radius * rm, color=accent,
                  fill_opacity=op, stroke_width=0))
    ring = Circle(radius=radius, color=accent, stroke_width=2.4,
                  fill_color=COLOR_BG, fill_opacity=0.70)
    g.add(ring)
    label = Tex(name, color=COLOR_WHITE)          # serif (Computer Modern) reads classical
    label.scale_to_fit_width(radius * 1.28).move_to(ORIGIN)
    g.add(label)
    g.ring, g.label, g.accent = ring, label, accent
    return g


# ── the four iconic symbols (drawn, with handles for their micro-animations) ──
def galileo_glyph(color=COLOR_BLUE_BALL):
    heavy = Dot(LEFT * 0.17, radius=0.085, color=color, fill_opacity=1.0, stroke_width=0)
    light = Dot(RIGHT * 0.17, radius=0.060, color=color, fill_opacity=1.0, stroke_width=0)
    g = VGroup(heavy, light)
    g.heavy, g.light = heavy, light
    return g


def kepler_glyph(color=COLOR_GREEN):
    a, b = 0.46, 0.28
    orbit = Ellipse(width=2 * a, height=2 * b, color=color,
                    stroke_width=2.0, fill_opacity=0)
    focus_off = RIGHT * 0.14
    sun = Dot(orbit.get_center() + focus_off, radius=0.05,
              color=COLOR_AMBER, fill_opacity=1.0, stroke_width=0)
    pt = orbit.get_center() + np.array([a * np.cos(2.6), b * np.sin(2.6), 0])
    planet = Dot(pt, radius=0.038, color=color, fill_opacity=1.0, stroke_width=0)
    g = VGroup(orbit, sun, planet)
    g.orbit, g.sun, g.planet = orbit, sun, planet
    g.a, g.b, g.focus_off = a, b, focus_off
    return g


def newton_glyph(color=COLOR_WHITE):
    """Cannonball parabola: dashed trajectory + ground + a ball at the start."""
    xs = np.linspace(-0.50, 0.55, 28)
    pts = [np.array([x, 0.26 - 0.62 * (x + 0.50) ** 2, 0]) for x in xs]
    path = VMobject().set_points_smoothly(pts).set_stroke(width=0, opacity=0)  # invisible mover-path
    arc = DashedVMobject(VMobject().set_points_smoothly(pts), num_dashes=20
                         ).set_stroke(color=color, width=2.0)
    ground = Line(LEFT * 0.55, RIGHT * 0.60, color=COLOR_GROUND,
                  stroke_width=1.5).move_to([0.0, pts[-1][1] - 0.02, 0])
    ball = Dot(pts[0], radius=0.05, color=color, fill_opacity=1.0, stroke_width=0)
    g = VGroup(ground, path, arc, ball)
    g.path, g.arc, g.ball = path, arc, ball
    g.scale_to_fit_height(0.62)
    return g


def cavendish_glyph(color=COLOR_G_GOLD):
    wire = Line(UP * 0.34, ORIGIN, color=COLOR_GROUND, stroke_width=1.6)
    rod = Line(LEFT * 0.42, RIGHT * 0.42, color=color, stroke_width=2.6)
    s1 = Dot(LEFT * 0.42, radius=0.06, color=color, fill_opacity=1.0, stroke_width=0)
    s2 = Dot(RIGHT * 0.42, radius=0.06, color=color, fill_opacity=1.0, stroke_width=0)
    bar = VGroup(rod, s1, s2)
    g = VGroup(wire, bar)
    g.wire, g.bar = wire, bar
    return g


# ═══════════════════════════════════════════════════════════════════════════
class Scene_9_Epilogue(MovingCameraScene):

    # locked layout
    MED_Y    = 1.15
    XS       = [-4.70, -1.57, 1.57, 4.70]
    ARC_DY   = [-0.30, 0.10, 0.10, -0.30]          # shallow "monument" arc
    PANEL_C  = np.array([3.70, 1.55, 0.0])         # Act-3 inset anchor (upper right)

    def construct(self):
        np.random.seed(7)
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        self.act1_four_faces()
        self.act2_collapse()
        self.act3_unpack_memory()
        self.act4_meta_lesson()
        self.act5_signoff()

    # ===================================================================== A1
    def act1_four_faces(self):
        specs = [
            ("GALILEO",   COLOR_BLUE_BALL, galileo_glyph),
            ("KEPLER",    COLOR_GREEN,     kepler_glyph),
            ("NEWTON",    COLOR_WHITE,     newton_glyph),
            ("CAVENDISH", COLOR_G_GOLD,    cavendish_glyph),
        ]
        self.meds, self.glyphs = [], []

        for i, (name, accent, glyph_fn) in enumerate(specs):
            c = np.array([self.XS[i], self.MED_Y + self.ARC_DY[i], 0.0])
            med = make_medallion(name, accent).move_to(c)
            sym = glyph_fn().next_to(med, DOWN, buff=0.40)
            self.meds.append(med)
            self.glyphs.append(sym)

            # pulse-in: scale from 0, ease-out, no bounce.
            self.play(GrowFromCenter(med, rate_func=rate_functions.ease_out_cubic),
                      run_time=0.7)
            self.play(FadeIn(sym, shift=UP * 0.12), run_time=0.45)

            # each symbol gives one brief, characteristic motion.
            if name == "GALILEO":                                   # equal fall
                self.play(sym.animate.shift(DOWN * 0.13),
                          run_time=0.7, rate_func=rate_functions.there_and_back)
            elif name == "KEPLER":                                  # swept sector
                o = sym.orbit.get_center()
                a, b = sym.a, sym.b
                ts = np.linspace(2.6, 2.6 - 0.95, 8)
                arc_pts = [o + np.array([a * np.cos(t), b * np.sin(t), 0]) for t in ts]
                sector = Polygon(o + sym.focus_off, *arc_pts,
                                 color=COLOR_GREEN, fill_opacity=0.18, stroke_width=0)
                self.play(FadeIn(sector), sym.planet.animate.move_to(arc_pts[-1]),
                          run_time=0.8)
                self.play(FadeOut(sector), run_time=0.35)
            elif name == "NEWTON":                                  # cannonball arc
                self.play(MoveAlongPath(sym.ball, sym.path),
                          run_time=0.9, rate_func=rate_functions.ease_in_quad)
            else:                                                   # CAVENDISH twist
                piv = sym.bar.get_center()
                self.play(Rotate(sym.bar, 14 * DEGREES, about_point=piv), run_time=0.35)
                self.play(Rotate(sym.bar, -26 * DEGREES, about_point=piv), run_time=0.45)
                self.play(Rotate(sym.bar, 12 * DEGREES, about_point=piv), run_time=0.35)

            # dim back to ambient — no one leaves, the others stay lit but quieter.
            self.play(VGroup(med, sym).animate.set_opacity(0.50), run_time=0.40)

        self.wait(0.8)   # 150 years, coexisting on one screen — let it land.

    # ===================================================================== A2
    def act2_collapse(self):
        all_meds  = VGroup(*self.meds)
        all_glyph = VGroup(*self.glyphs)

        # everyone brightens for the final convergence.
        self.play(all_meds.animate.set_opacity(1.0),
                  all_glyph.animate.set_opacity(1.0), run_time=0.6)
        self.wait(0.3)

        # the well: symbols float ahead to centre, medallions follow and shrink.
        self.play(
            LaggedStart(*[g.animate.move_to(ORIGIN).scale(0.45).set_opacity(0.0)
                          for g in self.glyphs], lag_ratio=0.08),
            LaggedStart(*[m.animate.move_to(ORIGIN).scale(0.22).set_opacity(0.0)
                          for m in self.meds], lag_ratio=0.08),
            run_time=1.7, rate_func=rate_functions.ease_in_cubic)   # falling inward
        self.remove(all_meds, all_glyph)

        # particle-merge: a scatter of coloured motes that coalesce to a point.
        cols = [COLOR_AMBER, COLOR_WHITE, COLOR_BLUE_BALL, COLOR_GREEN, COLOR_G_GOLD]
        seeds = VGroup()
        for _ in range(26):
            ang = float(np.random.uniform(0, TAU))
            rad = float(np.random.uniform(0.35, 1.45))
            seeds.add(Dot([rad * np.cos(ang), rad * np.sin(ang), 0], radius=0.045,
                          color=cols[np.random.randint(len(cols))],
                          fill_opacity=0.9, stroke_width=0))
        self.play(LaggedStart(*[FadeIn(s, scale=0.25) for s in seeds],
                              lag_ratio=0.02), run_time=0.6)
        self.play(seeds.animate.scale(0.02, about_point=ORIGIN).set_opacity(0.0),
                  run_time=0.7, rate_func=rate_functions.ease_in_cubic)
        self.remove(seeds)

        # ── the law rises, piece by piece, each term in its colour ──
        formula = build_formula(fs=64).move_to(UP * 0.12)
        formula.F.set_color(COLOR_WHITE);   formula.eq.set_color(COLOR_WHITE)
        formula.G.set_color(COLOR_G_GOLD)
        formula.M.set_color(COLOR_BLUE_BALL); formula.m.set_color(COLOR_BLUE_BALL)
        formula.bar.set_color(COLOR_WHITE)
        formula.r.set_color(COLOR_GREEN);   formula.exp.set_color(COLOR_GREEN)

        self.play(FadeIn(formula.F, shift=DOWN * 0.10),
                  FadeIn(formula.eq, shift=DOWN * 0.10), run_time=0.6)
        self.play(LaggedStart(FadeIn(formula.G, shift=UP * 0.12),
                              FadeIn(formula.M, shift=UP * 0.12),
                              FadeIn(formula.m, shift=UP * 0.12),
                              lag_ratio=0.30), run_time=1.2)
        self.play(Create(formula.bar), run_time=0.5)
        self.play(FadeIn(formula.den, shift=UP * 0.45), run_time=0.8)  # r² slides up beneath

        # arrive: a touch larger, centred, breathing alone — with a soft radiant
        # bloom behind it, the visual equivalent of the held-chord landing.
        bloom = VGroup(*[
            Dot(ORIGIN, radius=br, color=COLOR_WHITE, fill_opacity=0.0,
                stroke_width=0).set_z_index(-1)
            for br in (2.6, 1.9, 1.3)
        ]).move_to(ORIGIN)   # formula lands at ORIGIN; bloom sits with it
        self.add(bloom)
        self.play(
            formula.animate.scale(1.08).move_to(ORIGIN),
            AnimationGroup(*[d.animate.set_opacity(op)
                             for d, op in zip(bloom, (0.04, 0.06, 0.09))]),
            run_time=0.9, rate_func=rate_functions.ease_in_out_sine)
        # POST: this is the held-chord / soft resonant tone hit. Let it ring,
        # then let the bloom settle back so the line breathes alone.
        self.play(bloom.animate.set_opacity(0.0), run_time=1.3,
                  rate_func=rate_functions.ease_out_sine)
        self.remove(bloom)
        # almost-imperceptible lean-in — the camera quietly leans toward the line,
        # easing out so it comes to rest (no velocity cut into the next act).
        self.play(self.camera.frame.animate.scale(0.97), run_time=4.0,
                  rate_func=rate_functions.ease_out_sine)

        self.formula = formula
        self.fparts = [formula.F, formula.eq, formula.G, formula.M, formula.m,
                       formula.bar, formula.r, formula.exp]

    # ===================================================================== A3
    def _spotlight(self, hi):
        others = VGroup(*[p for p in self.fparts if p not in hi])
        self.play(others.animate.set_opacity(0.32),
                  VGroup(*hi).animate.scale(1.16), run_time=0.4,
                  rate_func=rate_functions.smooth)

    def _restore(self, hi):
        others = VGroup(*[p for p in self.fparts if p not in hi])
        self.play(others.animate.set_opacity(1.0),
                  VGroup(*hi).animate.scale(1 / 1.16), run_time=0.4,
                  rate_func=rate_functions.smooth)

    def _panel(self, accent):
        p = RoundedRectangle(width=3.25, height=2.55, corner_radius=0.12,
                             stroke_color=accent, stroke_width=2.0,
                             fill_color="#11151C", fill_opacity=0.97)
        p.move_to(self.PANEL_C).set_z_index(20)
        return p

    def act3_unpack_memory(self):
        f = self.formula
        PC = self.PANEL_C

        # ── M·m  →  Galileo's equal fall + Newton's proportionality (blue) ──
        hi = [f.M, f.m]
        self._spotlight(hi)
        panel = self._panel(COLOR_BLUE_BALL)
        conn = DashedLine(VGroup(*hi).get_top(), panel.get_corner(DL),
                          color=COLOR_BLUE_BALL, stroke_width=1.6,
                          stroke_opacity=0.4, dash_length=0.08).set_z_index(19)
        self.play(FadeIn(panel, scale=0.92), Create(conn), run_time=0.5)

        d1 = Dot(PC + np.array([-0.55, 0.62, 0]), radius=0.10,
                 color=COLOR_BLUE_BALL, z_index=21)
        d2 = Dot(PC + np.array([0.55, 0.62, 0]), radius=0.072,
                 color=COLOR_BLUE_BALL, z_index=21)
        # static link drawn first (so FadeIn is actually visible), THEN made live.
        link = DashedLine(d1.get_center(), d2.get_center(), color=COLOR_AMBER,
                          stroke_width=2.0, dash_length=0.09).set_z_index(21)
        lab = MathTex("F", r"\propto", "M", r"\cdot", "m", font_size=30)
        lab[2].set_color(COLOR_BLUE_BALL); lab[4].set_color(COLOR_BLUE_BALL)
        lab.move_to(PC + DOWN * 0.78).set_z_index(21)
        self.play(FadeIn(d1), FadeIn(d2), FadeIn(link), run_time=0.4)
        # now bind the link to the dots so it tracks them during the fall.
        link.add_updater(lambda m: m.put_start_and_end_on(
            d1.get_center(), d2.get_center()))
        self.play(d1.animate.shift(DOWN * 0.85), d2.animate.shift(DOWN * 0.85),
                  run_time=0.9, rate_func=rate_functions.ease_in_quad)  # equal fall, flat link
        link.clear_updaters()
        self.play(Write(lab), run_time=0.6)
        self.wait(0.9)
        self.play(FadeOut(VGroup(panel, conn, d1, d2, link, lab)), run_time=0.45)
        self._restore(hi)

        # ── r²  →  brightness spread over area (green) ──
        hi = [f.r, f.exp]
        self._spotlight(hi)
        panel = self._panel(COLOR_GREEN)
        conn = DashedLine(VGroup(*hi).get_top(), panel.get_corner(DL),
                          color=COLOR_GREEN, stroke_width=1.6,
                          stroke_opacity=0.4, dash_length=0.08).set_z_index(19)
        self.play(FadeIn(panel, scale=0.92), Create(conn), run_time=0.5)

        src = VGroup(
            Dot(PC + np.array([-1.20, 0.20, 0]), radius=0.12, color=COLOR_AMBER,
                fill_opacity=0.30, stroke_width=0),
            Dot(PC + np.array([-1.20, 0.20, 0]), radius=0.07, color=COLOR_AMBER,
                fill_opacity=1.0, stroke_width=0),
        ).set_z_index(21)
        near = Square(side_length=0.34, stroke_color=COLOR_GREEN, stroke_width=1.6,
                      fill_color=COLOR_GREEN, fill_opacity=0.80
                      ).move_to(PC + np.array([-0.30, 0.20, 0])).set_z_index(21)
        far = VGroup(*[
            Square(side_length=0.34, stroke_color=COLOR_GREEN, stroke_width=1.4,
                   fill_color=COLOR_GREEN, fill_opacity=0.28
                   ).move_to(PC + np.array([0.95 + (cc - 0.5) * 0.34,
                                            0.20 + (rr - 0.5) * 0.34, 0]))
            for rr in range(2) for cc in range(2)]).set_z_index(21)
        rays = VGroup(
            Line(src.get_center(), far.get_corner(UR), color=COLOR_AMBER,
                 stroke_width=1.2, stroke_opacity=0.35),
            Line(src.get_center(), far.get_corner(DR), color=COLOR_AMBER,
                 stroke_width=1.2, stroke_opacity=0.35),
        ).set_z_index(20)
        l_near = MathTex("1", color=COLOR_WHITE, font_size=28
                         ).next_to(near, DOWN, buff=0.16).set_z_index(21)
        l_far = MathTex(r"\tfrac{1}{4}", color=COLOR_GREEN, font_size=28
                        ).next_to(far, DOWN, buff=0.16).set_z_index(21)
        self.play(FadeIn(src), Create(rays), run_time=0.5)
        self.play(FadeIn(near, scale=0.85), FadeIn(l_near, shift=UP * 0.08),
                  run_time=0.5)
        self.play(FadeIn(far, scale=0.85), FadeIn(l_far, shift=UP * 0.08),
                  run_time=0.6)   # twice as far → four times the area → ¼ as bright
        self.wait(0.9)
        self.play(FadeOut(VGroup(panel, conn, src, near, far, rays, l_near, l_far)),
                  run_time=0.45)
        self._restore(hi)

        # ── G  →  Cavendish's torsion balance, measured 1798 (gold) ──
        hi = [f.G]
        self._spotlight(hi)
        panel = self._panel(COLOR_G_GOLD)
        conn = DashedLine(f.G.get_top(), panel.get_corner(DL),
                          color=COLOR_G_GOLD, stroke_width=1.6,
                          stroke_opacity=0.4, dash_length=0.08).set_z_index(19)
        self.play(FadeIn(panel, scale=0.92), Create(conn), run_time=0.5)

        cav = cavendish_glyph().scale(1.7).move_to(PC + UP * 0.30).set_z_index(21)
        lab = Text("measured · 1798", font=FONT, slant=ITALIC,
                   color=COLOR_G_GOLD, font_size=20
                   ).move_to(PC + DOWN * 0.85).set_z_index(21)
        self.play(FadeIn(cav, shift=DOWN * 0.1), run_time=0.5)
        piv = cav.bar.get_center()
        self.play(Rotate(cav.bar, 16 * DEGREES, about_point=piv), run_time=0.45)
        self.play(Rotate(cav.bar, -16 * DEGREES, about_point=piv), run_time=0.55)
        self.play(FadeIn(lab, shift=UP * 0.08), run_time=0.5)
        self.wait(0.9)
        self.play(FadeOut(VGroup(panel, conn, cav, lab)), run_time=0.45)
        self._restore(hi)

        # the line stands alone again — heavier now, more earned.
        self.wait(1.0)

    # ===================================================================== A4
    def act4_meta_lesson(self):
        f = self.formula

        # desaturate to chalk-grey.
        self.play(VGroup(*self.fparts).animate.set_color(COLOR_DIM), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)

        # re-saturate left → right, like a sunrise over the equation.
        restore = [
            f.F.animate.set_color(COLOR_WHITE),
            f.eq.animate.set_color(COLOR_WHITE),
            f.G.animate.set_color(COLOR_G_GOLD),
            f.M.animate.set_color(COLOR_BLUE_BALL),
            f.m.animate.set_color(COLOR_BLUE_BALL),
            f.bar.animate.set_color(COLOR_WHITE),
            f.r.animate.set_color(COLOR_GREEN),
            f.exp.animate.set_color(COLOR_GREEN),
        ]
        self.play(LaggedStart(*restore, lag_ratio=0.16), run_time=2.0)
        self.wait(0.5)

        # >>> EDIT (Premiere): the one real-world beat — a single apple falling
        #     in slow-mo, cross-cut against the equation for ~3s. The apple
        #     landing while the line just sits there is the quietly devastating
        #     image. Hold the beat below for that cut.
        self.wait(0.6)

        # the formula rises; a faint line settles below it (series rule: EN on screen).
        self.play(f.animate.shift(UP * 0.75), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        shadow = Text("It describes what is really happening in your world.",
                      font=FONT, slant=ITALIC, color=COLOR_GROUND, font_size=24
                      ).next_to(f, DOWN, buff=0.95).set_opacity(0.0)
        self.play(shadow.animate.set_opacity(0.55), run_time=1.2)
        self.wait(1.2)
        self.shadow = shadow

    # ===================================================================== A5
    def act5_signoff(self):
        f = self.formula

        self.play(FadeOut(self.shadow), run_time=0.8)

        # very slow pull-back — the equation sitting in a growing cosmos.
        self.play(self.camera.frame.animate.scale(1.12), run_time=3.0,
                  rate_func=rate_functions.ease_in_out_sine)

        # exhale into darkness — slow FadeToBlack, never an abrupt cut.
        self.play(FadeOut(Group(*self.mobjects)), run_time=2.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.0)