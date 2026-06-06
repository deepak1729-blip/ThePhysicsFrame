from manim import *
import numpy as np

# ─────────────────────────────────────────────────────────────────────────
#  BRAND PALETTE  (carried verbatim from the series canvas; a few new bodies)
# ─────────────────────────────────────────────────────────────────────────
COLOR_BG        = "#0E1117"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_VEC_F     = "#FF3B30"   # red    — gravity / force (series-locked)
COLOR_GREEN     = "#34C759"   # green  — confirmation tick / distance r
COLOR_AMBER     = "#FFCC00"   # amber  — connector / time / measured-length motif
COLOR_BLUE_BALL = "#007AFF"   # blue   — LOCKED: the big mass M (Earth)
COLOR_CORAL     = "#FF6F61"   # coral  — LOCKED (scene_4): the small mass m (apple)
COLOR_G_GOLD    = "#E8B53A"   # warm antique gold — the constant G (born in scene_0)
COLOR_DIM       = "#3A3F47"   # ghost / cancelled / "unknown" stroke

# ── new physical bodies for this scene get their own named constants, the same
#    way scene_6 added COLOR_MOON and scene_7 added COLOR_ORBIT/COLOR_KEPLER. ──
COLOR_WIRE      = "#C7D0DA"   # NEW — the torsion wire: light silver, luminous
COLOR_LEAD_SM   = "#C7CDD4"   # NEW — small lead spheres (cool silver-grey)
COLOR_LEAD_LG   = "#5A6068"   # NEW — large lead spheres (darker, heavier)
COLOR_BEAM      = "#FFE680"   # NEW — the reflected light-beam (warm, pale gold)

# Semantic aliases for this scene.
COLOR_M = COLOR_BLUE_BALL     # Earth's mass
COLOR_m = COLOR_CORAL         # apple / lab-object mass

FONT = "Segoe UI"
config.background_color = COLOR_BG
RNG = np.random.default_rng(7)   # deterministic → stable render cache

PLANET_IMAGES = ["mercury.png", "venus.png", "earth.png", "mars.png"]

def orbit_point(a, R):
    """Point on a circle of radius R at angle a, centred on the origin."""
    return np.array([R * np.cos(a), R * np.sin(a), 0.0])

# ── overlay assets (drop next to the script; degrade to placeholders if absent)
IMG_CAVENDISH = "Cavendish_Experiment.png"   # Act 6 — replica plate (matches scene_0)


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


def make_ball(color: str, radius: float = 0.30) -> VGroup:
    """
    Returns a VGroup that looks like a lit 3-D sphere:
      • solid body with set_sheen() gradient (bright top-left → dark bottom-right)
      • thin rim-highlight stroke
      • white specular ellipse (upper-left)

    The VGroup's reference point is the centre of the sphere, so you can
    call  ball.move_to(pos)  and  ball.get_center()  exactly like a Circle.
    """
    g = VGroup()

    # Glow aura — four concentric halos, outermost first (drawn first = behind)

    # Main sphere body
    sphere = Circle(radius=radius)
    sphere.set_fill(color, opacity=1.0)
    sphere.set_sheen(-0.45, DR)          # darkens bottom-right, brightens top-left
    sphere.set_stroke(color=WHITE, width=1.5, opacity=0.22)
    g.add(sphere)

    # Rim light (coloured stroke, gives the "lit edge" feel)
    rim = Circle(radius=radius)
    rim.set_fill(opacity=0)
    rim.set_stroke(color=color, width=3, opacity=0.50)
    g.add(rim)

    # Specular highlight — small white ellipse offset to upper-left
    spec = Ellipse(width=radius * 0.52, height=radius * 0.34)
    spec.set_fill(WHITE, opacity=0.62)
    spec.set_stroke(width=0)
    spec.move_to(
        np.array([-radius * 0.28,  radius * 0.30, 0])   # offset from origin
    )
    spec.rotate(-20 * DEGREES)
    g.add(spec)

    return g


def check_mark(color=COLOR_GREEN, scale=0.5):
    """The series' satisfying tick (scene_0/5/6)."""
    m = VMobject(stroke_color=color, stroke_width=6)
    m.set_points_as_corners([
        LEFT * 0.18 + DOWN * 0.02, DOWN * 0.20, RIGHT * 0.30 + UP * 0.26,
    ])
    return m.scale(scale)


def down_arrow(top, length, color, sw=5):
    return Arrow(top, top + DOWN * length, buff=0, color=color,
                 stroke_width=sw, max_tip_length_to_length_ratio=0.28)


def frac(num, den, pad=0.22, sw=3, color=COLOR_WHITE):
    """A fraction bar laid between an already-built numerator and denominator.
    Returns a VGroup with .num/.bar/.den handles so glyphs stay addressable."""
    bar_w = max(num.width, den.width) + pad
    bar = Line(LEFT * bar_w / 2, RIGHT * bar_w / 2, stroke_width=sw, color=color)
    num.next_to(bar, UP, buff=0.10)
    den.next_to(bar, DOWN, buff=0.10)
    g = VGroup(num, bar, den)
    g.num, g.bar, g.den = num, bar, den
    return g


def build_formula(fs=60):
    """F = GMm/r² assembled from individually addressable glyphs (scene_0/3).
    Named handles let every act grab single symbols."""
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
    fr = VGroup(num, bar, den)

    whole = VGroup(F, eq, fr).arrange(RIGHT, buff=0.22)
    whole.F, whole.eq, whole.G, whole.M, whole.m = F, eq, G, M, mm
    whole.r, whole.exp, whole.bar = r, exp, bar
    whole.num, whole.den, whole.frac = num, den, fr
    return whole

def make_stone(radius=0.26):
    """Generates a static, non-random irregular stone to preserve caching."""
    g = VGroup()

    shape_profile = [1.1, 0.9, 1.15, 0.85, 1.05, 0.95, 1.2, 0.82, 1.08, 0.9, 1.1]
    pts = []
    N = len(shape_profile)
    for i in range(N):
        a = TAU * i / N
        r = radius * shape_profile[i]
        pts.append(np.array([r * np.cos(a), r * np.sin(a), 0]))

    body = Polygon(*pts, color="#3A3A3C")
    body.set_fill("#8E8E93", opacity=1.0)
    body.set_stroke(color="#3A3A3C", width=1.6, opacity=0.9)
    body.set_sheen(-0.35, DR)
    g.add(body)

    spec_data = [
        (0.3 * radius, 1.2, 0.08 * radius),
        (0.5 * radius, 3.5, 0.06 * radius),
        (0.25 * radius, 5.0, 0.09 * radius)
    ]
    for r, a, sr in spec_data:
        spec = Dot(point=np.array([r * np.cos(a), r * np.sin(a), 0]),
                   radius=sr, color="#3A3A3C")
        spec.set_fill("#3A3A3C", opacity=0.75)
        g.add(spec)

    return g


def safe_image(path, width, fallback_label, ratio=1.25):
    """ImageMobject with a labelled placeholder so the scene always renders
    even before the real asset is dropped next to the script (series convention)."""
    try:
        return ImageMobject(path).scale_to_fit_width(width)
    except Exception:
        box = Rectangle(width=width, height=width * ratio, color=COLOR_GROUND,
                        stroke_width=1.5, fill_color=COLOR_BG, fill_opacity=0.92)
        lbl = Text(fallback_label, font=FONT, font_size=16, color=COLOR_GROUND)
        lbl.scale_to_fit_width(min(width * 0.82, lbl.width)).move_to(box)
        return VGroup(box, lbl)


def safe_earth(width):
    """earth.png, with a drawn-disc fallback so the scene always renders."""
    try:
        return ImageMobject("earth.png").scale_to_fit_width(width)
    except Exception:
        body = Circle(radius=width / 2, stroke_width=0, fill_opacity=1.0,
                      color=COLOR_BLUE_BALL)
        sheen = Circle(radius=width / 2 * 0.6, stroke_width=0,
                       fill_opacity=0.16, color=COLOR_WHITE)
        sheen.move_to(body.get_center()
                      + np.array([-width * 0.16, width * 0.16, 0]))
        return Group(body, sheen)


def make_figure(color=COLOR_GROUND, s=1.0, seated=False):
    """An abstract human silhouette — head + body, optionally hunched at a desk.
    Deliberately spare (the cue: 'abstract, not cartoonish')."""
    g = VGroup()
    head = Circle(radius=0.17 * s, color=color, stroke_width=3, fill_opacity=0)
    if seated:
        head.move_to([0.0, 0.62 * s, 0])
        back = VMobject(stroke_color=color, stroke_width=3)
        back.set_points_smoothly([[0.0, 0.45 * s, 0],
                                  [0.06 * s, 0.10 * s, 0],
                                  [0.0, -0.18 * s, 0]])
        thigh = Line([0.0, -0.18 * s, 0], [0.42 * s, -0.18 * s, 0],
                     color=color, stroke_width=3)
        arm = Line([0.02 * s, 0.28 * s, 0], [0.40 * s, 0.02 * s, 0],
                   color=color, stroke_width=3)
        desk = Line([0.18 * s, -0.02 * s, 0], [0.78 * s, -0.02 * s, 0],
                    color=color, stroke_width=2.5, stroke_opacity=0.7)
        g.add(back, thigh, arm, head, desk)
    else:
        head.move_to([0.0, 0.74 * s, 0])
        body = Line([0.0, 0.55 * s, 0], [0.0, -0.10 * s, 0],
                    color=color, stroke_width=3)
        legL = Line([0.0, -0.10 * s, 0], [-0.16 * s, -0.58 * s, 0],
                    color=color, stroke_width=3)
        legR = Line([0.0, -0.10 * s, 0], [0.16 * s, -0.58 * s, 0],
                    color=color, stroke_width=3)
        arms = Line([-0.20 * s, 0.34 * s, 0], [0.20 * s, 0.34 * s, 0],
                    color=color, stroke_width=3)
        g.add(body, legL, legR, arms, head)
    return g


# ═══════════════════════════════════════════════════════════════════════════
class Scene_8_TheConstantG(MovingCameraScene):

    # ── locked timeline geometry (shared by Act 3 and Act 5) ──
    TL_Y      = -0.6
    YR_LO, YR_HI = 1675, 1810
    TL_LEFT, TL_RIGHT = -5.6, 5.6

    def construct(self):
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        self.act1_three_clues()
        self.act2_introduce_G()
        self.act3_newton_never_knew()
        self.act4_why_so_hard()
        self.act5_cavendish_enters()
        self.act6_the_apparatus()
        self.act7_telescope_outside()
        self.act8_the_solve()
        self.act9_smallness_lands()
        self.act10_weighing_the_earth()

    # ---- shared utilities --------------------------------------------------
    def _clear_to_grid(self, run_time=1.0):
        clear = Group(*[m for m in self.mobjects if m is not self.grid])
        if len(clear):
            self.play(FadeOut(clear), run_time=run_time,
                      rate_func=rate_functions.ease_in_out_sine)

    def _year_x(self, year):
        t = (year - self.YR_LO) / (self.YR_HI - self.YR_LO)
        return interpolate(self.TL_LEFT, self.TL_RIGHT, t)

    # ===================================================================== A1
    def act1_three_clues(self):
        # ── "Teeno clues." The series' three relations, recalled and fused. ──
        prop = MathTex(r"\propto", font_size=150, color=COLOR_G_GOLD)
        prop.set_z_index(5)
        self.play(FadeIn(prop, scale=0.6), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)
        # a symbol treated like it matters — one slow gold pulse
        self.play(prop.animate.scale(1.12), run_time=0.9,
                  rate_func=rate_functions.there_and_back)
        self.wait(0.4)

        # ---- Card 1 : F ∝ m  (two balls fall in sync, parallel paths) -------
        c1 = VGroup(
            MathTex("F", font_size=54, color=COLOR_WHITE),
            MathTex(r"\propto", font_size=54, color=COLOR_G_GOLD),
            MathTex("m", font_size=54, color=COLOR_WHITE),
        ).arrange(RIGHT, buff=0.22)
        c1.move_to(UP * 1.9 + LEFT * 1.4)
        # the big gold ∝ becomes this card's ∝ — one continuous thread
        self.play(ReplacementTransform(prop, c1[1]),
                  FadeIn(c1[0], shift=RIGHT * 0.1),
                  FadeIn(c1[2], shift=LEFT * 0.1),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_cubic)

        # spare falling sketch to the right: two dots, different size, same speed
        sk_x = 2.7
        topY, botY = 2.6, 1.25
        pa = DashedLine([sk_x - 0.35, topY, 0], [sk_x - 0.35, botY, 0],
                        color=COLOR_WHITE, stroke_opacity=0.18, dash_length=0.10)
        pb = DashedLine([sk_x + 0.35, topY, 0], [sk_x + 0.35, botY, 0],
                        color=COLOR_WHITE, stroke_opacity=0.18, dash_length=0.10)
        b_big   = make_stone(radius=0.11).move_to([sk_x - 0.35, topY, 0])
        b_small = make_stone(radius=0.07).move_to([sk_x + 0.35, topY, 0])
        self.play(Create(pa), Create(pb),
                  FadeIn(b_big), FadeIn(b_small), run_time=0.4)
        self.play(b_big.animate.move_to([sk_x - 0.35, botY, 0]),
                  b_small.animate.move_to([sk_x + 0.35, botY, 0]),
                  run_time=0.7, rate_func=lambda a: a * a)   # ~t² fall, together
        sketch1 = VGroup(pa, pb, b_big, b_small)
        self.wait(0.4)

        # ---- Card 2 : F ∝ Mm  (the two masses find each other) --------------
        c2 = VGroup(
            MathTex("F", font_size=54, color=COLOR_WHITE),
            MathTex(r"\propto", font_size=54, color=COLOR_G_GOLD),
            MathTex("M", font_size=54, color=COLOR_M),
            MathTex("m", font_size=54, color=COLOR_m),
        ).arrange(RIGHT, buff=0.14)
        c2[2:].arrange(RIGHT, buff=0.06).next_to(c2[1], RIGHT, buff=0.22)
        c2.move_to(UP * 0.2 + LEFT * 1.4)
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.12) for s in c2],
                              lag_ratio=0.12),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        # sketch: two dots joined by gravity's soft dotted reach; product lights
        dM = ImageMobject("earth.png").scale_to_fit_width(0.36).move_to([sk_x - 0.45, 0.2, 0])
        dm = ImageMobject("apple.png").scale_to_fit_width(0.24).move_to([sk_x + 0.45, 0.2, 0])
        reach = DashedLine(dM.get_center(), dm.get_center(), color=COLOR_AMBER,
                           stroke_width=2, dash_length=0.08).set_opacity(0.7)
        self.play(FadeIn(dM, scale=0.5), FadeIn(dm, scale=0.5), run_time=0.4)
        self.play(Create(reach),
                  c2[2].animate.set_color(COLOR_M),
                  c2[3].animate.set_color(COLOR_m), run_time=0.5)
        self.play(VGroup(c2[2], c2[3]).animate.scale(1.12), run_time=0.4,
                  rate_func=rate_functions.there_and_back)   # they "found each other"
        sketch2 = Group(dM, dm, reach)
        self.wait(0.4)

        # ---- Card 3 : F ∝ 1/r²  (distance dilutes; ripples spread; pull-back)
        one = MathTex("1", font_size=46, color=COLOR_WHITE)
        rden = VGroup(MathTex("r", font_size=46, color=COLOR_GREEN),
                      MathTex("2", font_size=29, color=COLOR_GREEN))
        rden[1].next_to(rden[0], UR, buff=0.0).shift(DOWN * 0.03 + LEFT * 0.02)
        f3 = frac(one, rden, pad=0.18)
        c3 = VGroup(MathTex("F", font_size=54, color=COLOR_WHITE),
                    MathTex(r"\propto", font_size=54, color=COLOR_G_GOLD),
                    f3).arrange(RIGHT, buff=0.22)
        c3.move_to(DOWN * 1.6 + LEFT * 1.4)
        self.play(LaggedStart(FadeIn(c3[0], shift=DOWN * 0.12),
                              FadeIn(c3[1], shift=DOWN * 0.12),
                              Write(c3[2]), lag_ratio=0.18),
                  run_time=1.0)
        # three planets orbiting at the sketch position (from scene_7 act6_kepler_gift)
        orbit_C = np.array([sk_x, -1.6, 0])
        sun_s8 = ImageMobject("sun.png").scale_to_fit_width(0.22).move_to(orbit_C).set_z_index(2)
        s8_radii   = [0.34, 0.62, 0.98]
        s8_p_idx   = [0, 1, 2]   # Mercury, Venus, Earth
        s8_p_sizes = [0.08, 0.10, 0.09]
        s8_phase   = [0.4, 2.1, 4.0]
        s8_w0 = 1.0
        s8_w = [s8_w0 * (s8_radii[0] / r) ** 1.5 for r in s8_radii]
        s8_rings = VGroup(*[
            DashedVMobject(Circle(radius=r, color=COLOR_GREEN, stroke_width=1.2),
                           num_dashes=48).set_stroke(opacity=0.35).move_to(orbit_C)
            for r in s8_radii])
        s8_kt = ValueTracker(0.0)
        s8_planets = []
        for i, (r, ph, idx, sz) in enumerate(zip(s8_radii, s8_phase, s8_p_idx, s8_p_sizes)):
            p = ImageMobject(PLANET_IMAGES[idx]).scale_to_fit_width(sz)
            p.move_to(orbit_C + orbit_point(ph, r)).set_z_index(3)
            p.add_updater(lambda m, i=i, r=r, ph=ph:
                          m.move_to(orbit_C + orbit_point(ph + s8_kt.get_value() * s8_w[i], r)))
            s8_planets.append(p)
        self.play(FadeIn(sun_s8, scale=0.5),
                  LaggedStart(*[Create(rg) for rg in s8_rings], lag_ratio=0.2),
                  run_time=0.7)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in s8_planets], lag_ratio=0.12),
                  run_time=0.5)
        self.play(s8_kt.animate.set_value(6.0), run_time=1.6, rate_func=linear)
        for p in s8_planets:
            p.clear_updaters()
        sketch3 = Group(sun_s8, s8_rings, *s8_planets)
        self.wait(0.3)

        # ---- The compression: three lines snap into one sentence ------------
        _tr = MathTex("r", font_size=64, color=COLOR_GREEN)
        _texp = MathTex("2", font_size=38, color=COLOR_GREEN)
        _texp.next_to(_tr, UR, buff=0.0).shift(DOWN * 0.04 + LEFT * 0.02)
        target = VGroup(
            MathTex("F", font_size=72, color=COLOR_WHITE),
            MathTex(r"\propto", font_size=72, color=COLOR_G_GOLD),
            frac(VGroup(MathTex("M", font_size=64, color=COLOR_M),
                        MathTex("m", font_size=64, color=COLOR_m))
                 .arrange(RIGHT, buff=0.06),
                 VGroup(_tr, _texp), pad=0.26),
        ).arrange(RIGHT, buff=0.26).move_to(ORIGIN)

        self.play(FadeOut(sketch1), FadeOut(sketch2), FadeOut(sketch3),
                  Restore(self.camera.frame), run_time=0.6)
        self.play(
            ReplacementTransform(VGroup(c1, c2, c3), target),
            run_time=1.2, rate_func=rate_functions.ease_out_back)   # the snap
        self.play(Flash(target.get_center(), color=COLOR_G_GOLD, line_length=0.22,
                        num_lines=12, flash_radius=1.4), run_time=0.5)
        self.wait(1.0)

        self.prop_form = target   # hand to Act 2

    # ===================================================================== A2
    def act2_introduce_G(self):
        # ── "Proportional ko equal banana." The ∝ BECOMES = G. ──
        pf = self.prop_form
        self.play(pf.animate.move_to(ORIGIN).scale(56 / 72), run_time=0.7,
                  rate_func=rate_functions.ease_in_out_sine)
        propsym = pf[1]

        # spotlight the ∝ — it pulses once, demanding to be replaced
        ring = Circle(radius=0.42, color=COLOR_G_GOLD, stroke_width=3).move_to(propsym)
        self.play(Create(ring), run_time=0.4)
        self.play(ring.animate.scale(1.2).set_stroke(opacity=0.0), run_time=0.6)
        self.remove(ring)

        # the ∝ morphs into "=" ; then G is inserted as the missing scale,
        # pushing the fraction right to make room (a piece slotting in).
        eq = MathTex("=", font_size=56, color=COLOR_WHITE).move_to(propsym)
        self.play(Transform(propsym, eq), run_time=0.6,
                  rate_func=rate_functions.ease_in_out_cubic)
        fr = pf[2]
        G = MathTex("G", font_size=56, color=COLOR_WHITE)
        G.next_to(propsym, RIGHT, buff=0.20)
        dx = (G.get_right()[0] + 0.22 + fr.width / 2) - fr.get_center()[0]
        self.play(fr.animate.shift(RIGHT * dx),
                  FadeIn(G, scale=0.4, shift=DOWN * 0.1),
                  run_time=0.8, rate_func=rate_functions.ease_out_back)
        self.wait(0.5)

        # G earns its own colour + a zoom + a soft pulse: the protagonist.
        self.play(self.camera.frame.animate.scale(0.62).move_to(G),
                  G.animate.set_color(COLOR_G_GOLD),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.play(G.animate.scale(1.25), run_time=0.6,
                  rate_func=rate_functions.there_and_back)
        glow = Dot(G.get_center(), radius=0.45, color=COLOR_G_GOLD,
                   fill_opacity=0.0, stroke_width=0).set_z_index(-1)
        self.add(glow)
        self.play(glow.animate.set_opacity(0.40), run_time=0.5)
        self.play(glow.animate.set_opacity(0.18), run_time=0.5)
        self.wait(0.6)

        self.play(Restore(self.camera.frame), FadeOut(glow),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)

        # Rebuild as the canonical, addressable formula for the acts that follow.
        formula = build_formula(fs=56).move_to(ORIGIN)
        formula.G.set_color(COLOR_G_GOLD)
        self.play(ReplacementTransform(pf, formula), G.animate.set_opacity(0),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_cubic)
        self.remove(G)
        self.formula = formula
        self.wait(0.6)

    # ===================================================================== A3
    def act3_newton_never_knew(self):
        # ── "Newton ka tragedy." The skeleton is complete; one bone is missing.
        f = self.formula
        self.play(f.animate.to_edge(UP, buff=1.1).scale(0.9), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)

        # Redaction — melancholic, not aggressive: G greys out, a "?" hovers.
        qmark = MathTex("?", font_size=40, color=COLOR_DIM).move_to(f.G)
        self.play(f.G.animate.set_color(COLOR_DIM).set_opacity(0.45),
                  run_time=0.7)
        self.play(FadeIn(qmark, scale=0.5), run_time=0.4)
        self.wait(0.6)

        # The timeline slides in from the left.
        line = Line([self.TL_LEFT, self.TL_Y, 0], [self.TL_RIGHT, self.TL_Y, 0],
                    color=COLOR_GROUND, stroke_width=2.5)
        self.play(Create(line), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)

        def marker(year, label, col=COLOR_WHITE):
            x = self._year_x(year)
            tick = Line([x, self.TL_Y - 0.14, 0], [x, self.TL_Y + 0.14, 0],
                        color=col, stroke_width=3)
            yr = Text(str(year), font=FONT, font_size=22, color=col
                      ).next_to(tick, DOWN, buff=0.12)
            lab = Text(label, font=FONT, font_size=18, color=COLOR_GROUND,
                       slant=ITALIC).next_to(tick, UP, buff=0.12)
            return VGroup(tick, yr, lab)

        m1687 = marker(1687, "Principia")
        m1727 = marker(1727, "Newton dies")
        self.play(FadeIn(m1687, shift=UP * 0.1), run_time=0.6)
        self.wait(0.3)
        self.play(FadeIn(m1727, shift=UP * 0.1), run_time=0.6)

        # The grey "?" hangs over the whole span of his life — never resolves.
        span = Line([self._year_x(1687), self.TL_Y + 0.7, 0],
                    [self._year_x(1727), self.TL_Y + 0.7, 0],
                    color=COLOR_WHITE, stroke_width=2).set_opacity(0.7)
        span_q = MathTex("G = ?", font_size=30, color=COLOR_WHITE
                         ).next_to(span, UP, buff=0.12)
        self.play(Create(span), FadeIn(span_q), run_time=0.7)
        self.wait(0.6)

        self._clear_to_grid()

    # ===================================================================== A4
    def act4_why_so_hard(self):
        # ── "G itna mushkil kyun?" Make the scale problem viscerally felt. ──
        # LEFT: two lab spheres on a table, an almost-invisible force between.
        table = Line([-6.2, -1.4, 0], [-1.2, -1.4, 0], color=COLOR_GROUND,
                     stroke_width=2.5)
        m1 = make_ball(COLOR_LEAD_SM, 0.26).move_to([-4.6, -1.14, 0])
        m2 = make_ball(COLOR_LEAD_SM, 0.26).move_to([-2.8, -1.14, 0])
        l1 = MathTex("m_1", font_size=30, color=COLOR_GROUND).next_to(m1, DOWN, buff=0.28)
        l2 = MathTex("m_2", font_size=30, color=COLOR_GROUND).next_to(m2, DOWN, buff=0.28)
        self.play(Create(table),
                  FadeIn(m1, shift=DOWN * 0.1), FadeIn(m2, shift=DOWN * 0.1),
                  FadeIn(l1), FadeIn(l2), run_time=0.9)
        # the absurdly tiny pull — a stub of an arrow, barely a tip
        tiny_l = Arrow(m1.get_right() + RIGHT * 0.55, m1.get_right() + RIGHT * 0.32,
                       buff=0, color=COLOR_VEC_F, stroke_width=2,
                       max_tip_length_to_length_ratio=0.9)
        tiny_r = Arrow(m2.get_left() + LEFT * 0.55, m2.get_left() + LEFT * 0.32,
                       buff=0, color=COLOR_VEC_F, stroke_width=2,
                       max_tip_length_to_length_ratio=0.9)
        self.play(GrowArrow(tiny_l), GrowArrow(tiny_r), run_time=0.5)
        # zoom a hair to even SEE it, then back — the point is its invisibility
        self.play(self.camera.frame.animate.scale(0.7)
                  .move_to([-3.7, -1.1, 0]), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)
        self.play(Restore(self.camera.frame), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)

        # RIGHT: Earth dragging an apple — same law, overwhelming arrow.
        earth = safe_earth(2.4).move_to([4.3, -1.7, 0]).set_z_index(1)
        apple = make_ball(COLOR_CORAL, 0.16).move_to([4.3, 0.55, 0]).set_z_index(2)
        self.play(FadeIn(earth, shift=UP * 0.15), FadeIn(apple), run_time=0.8)
        big = down_arrow(apple.get_bottom() + DOWN * 0.06, 1.5, COLOR_VEC_F, sw=8)
        self.play(GrowArrow(big), run_time=0.6)
        same_law = Text("same formula", font=FONT, slant=ITALIC,
                        color=COLOR_GROUND, font_size=22).to_edge(UP, buff=0.7)
        self.play(FadeIn(same_law), run_time=0.4)
        self.wait(1.0)

        self.play(*[FadeOut(m) for m in (table, m1, m2, l1, l2, tiny_l, tiny_r,
                                          earth, apple, big, same_law)],
                  run_time=0.7)

        # The checklist — easy for Earth, then it fails for the lab.
        rows = [r"\text{Force } F", r"\text{Mass } M", r"\text{Mass } m",
                r"\text{Distance } r"]
        labels = VGroup(*[MathTex(t, font_size=34, color=COLOR_WHITE)
                          for t in rows]).arrange(DOWN, buff=0.42,
                                                  aligned_edge=LEFT)
        labels.move_to(LEFT * 1.2)
        ticks = VGroup(*[check_mark(COLOR_GREEN, 0.5).next_to(lab, LEFT, buff=0.4)
                         for lab in labels])
        head_e = Text("For Earth:", font=FONT, font_size=26, color=COLOR_GROUND
                      ).next_to(labels, UP, buff=0.6, aligned_edge=LEFT)
        self.play(FadeIn(head_e), run_time=0.4)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(lab, shift=RIGHT * 0.1),
                                               Create(tk))
                                for lab, tk in zip(labels, ticks)],
                              lag_ratio=0.25), run_time=1.8)
        self.wait(0.8)

        # Same list, two lab objects — the Force row flickers, fails, near-zero.
        head_l = Text("For two lab objects:", font=FONT, font_size=26,
                      color=COLOR_GROUND).move_to(head_e)
        self.play(ReplacementTransform(head_e, head_l), run_time=0.5)
        force_tick = ticks[0]
        cross = VGroup(
            Line(UL * 0.16, DR * 0.16, color=COLOR_VEC_F, stroke_width=5),
            Line(UR * 0.16, DL * 0.16, color=COLOR_VEC_F, stroke_width=5),
        ).move_to(force_tick)
        tiny_num = MathTex(r"\approx 10^{-9}\ \text{N}", font_size=28,
                           color=COLOR_VEC_F).next_to(labels[0], RIGHT, buff=0.5)
        # flicker the row red before it breaks
        for _ in range(2):
            self.play(labels[0].animate.set_color(COLOR_VEC_F), run_time=0.12)
            self.play(labels[0].animate.set_color(COLOR_WHITE), run_time=0.12)
        self.play(FadeOut(force_tick), FadeIn(cross, scale=0.5),
                  labels[0].animate.set_color(COLOR_VEC_F),
                  FadeIn(tiny_num, shift=LEFT * 0.1), run_time=0.6)
        self.wait(1.0)

        self.play(*[FadeOut(m) for m in (labels, ticks[1:], cross, tiny_num,
                                          head_l)], run_time=0.6)

        # The circular dependency, shown as a loop that eats its own tail.
        boxG = VGroup(RoundedRectangle(width=2.6, height=1.0, corner_radius=0.12,
                                       stroke_color=COLOR_G_GOLD, stroke_width=2.5),
                      MathTex("G", font_size=40, color=COLOR_G_GOLD))
        boxG.move_to(LEFT * 2.6 + UP * 0.2)
        boxG[1].move_to(boxG[0])
        boxM = VGroup(RoundedRectangle(width=2.6, height=1.0, corner_radius=0.12,
                                       stroke_color=COLOR_M, stroke_width=2.5),
                      MathTex(r"M_{\oplus}", font_size=36, color=COLOR_M))
        boxM.move_to(RIGHT * 2.6 + UP * 0.2)
        boxM[1].move_to(boxM[0])
        self.play(FadeIn(boxG, shift=RIGHT * 0.1), FadeIn(boxM, shift=LEFT * 0.1),
                  run_time=0.7)
        top = CurvedArrow(boxG[0].get_top() + UP * 0.05,
                          boxM[0].get_top() + UP * 0.05,
                          color=COLOR_GROUND, stroke_width=3, angle=-PI / 3)
        bot = CurvedArrow(boxM[0].get_bottom() + DOWN * 0.05,
                          boxG[0].get_bottom() + DOWN * 0.05,
                          color=COLOR_GROUND, stroke_width=3, angle=-PI / 3)
        need1 = Text("need this to find", font=FONT, font_size=18,
                     color=COLOR_GROUND, slant=ITALIC).next_to(top, UP, buff=0.05)
        need2 = Text("need this to find", font=FONT, font_size=18,
                     color=COLOR_GROUND, slant=ITALIC).next_to(bot, DOWN, buff=0.05)
        self.play(Create(top), FadeIn(need1), run_time=0.6)
        self.play(Create(bot), FadeIn(need2), run_time=0.6)
        # the trap spins once
        loop = VGroup(top, bot)
        self.play(loop.animate.set_color(COLOR_VEC_F), run_time=0.4)
        self.play(loop.animate.set_color(COLOR_GROUND), run_time=0.5)
        self.wait(1.2)

        self._clear_to_grid()

    # ===================================================================== A5
    def act5_cavendish_enters(self):
        # ── "Cavendish aata hai." Seventy years of silence, then one dot. ──
        line = Line([self.TL_LEFT, self.TL_Y, 0], [self.TL_RIGHT, self.TL_Y, 0],
                    color=COLOR_GROUND, stroke_width=2.5)
        self.play(Create(line), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)

        def marker(year, label, col=COLOR_WHITE, lab_col=COLOR_GROUND):
            x = self._year_x(year)
            tick = Line([x, self.TL_Y - 0.14, 0], [x, self.TL_Y + 0.14, 0],
                        color=col, stroke_width=3)
            yr = Text(str(year), font=FONT, font_size=22, color=col
                      ).next_to(tick, DOWN, buff=0.12)
            lab = Text(label, font=FONT, font_size=18, color=lab_col,
                       slant=ITALIC).next_to(tick, UP, buff=0.12)
            return VGroup(tick, yr, lab)

        m1727 = marker(1727, "Newton dies")
        self.play(FadeIn(m1727, shift=UP * 0.1), run_time=0.5)

        # the uncomfortable empty stretch before the answer arrives
        gap = Line([self._year_x(1727), self.TL_Y, 0],
                   [self._year_x(1798), self.TL_Y, 0],
                   color=COLOR_DIM, stroke_width=5)
        gap_lab = Text("70 years", font=FONT, font_size=22, color=COLOR_WHITE,
                       slant=ITALIC).next_to(gap, UP, buff=0.45)
        self.play(Create(gap), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeIn(gap_lab), run_time=0.5)
        self.wait(1.0)   # let the silence sit

        # the dot lands — a relief.
        m1798 = marker(1798, "Henry Cavendish", col=COLOR_G_GOLD,
                       lab_col=COLOR_G_GOLD)
        x98 = self._year_x(1798)
        drop = Dot([x98, self.TL_Y + 1.4, 0], radius=0.10, color=COLOR_G_GOLD)
        self.play(FadeIn(drop), run_time=0.3)
        self.play(drop.animate.move_to([x98, self.TL_Y, 0]), run_time=0.6,
                  rate_func=rate_functions.ease_in_quad)   # falls into place
        self.play(FadeOut(drop),
                  FadeIn(m1798, shift=UP * 0.1),
                  Flash([x98, self.TL_Y, 0], color=COLOR_G_GOLD, line_length=0.18,
                        num_lines=10, flash_radius=0.5), run_time=0.5)
        self.wait(1.0)

        # the timeline yields to one word.
        self.play(FadeOut(VGroup(line, m1727, m1798, gap, gap_lab)),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_sine)
        title = Text("Torsion Balance", font=FONT, font_size=58,
                     color=COLOR_WHITE).move_to(ORIGIN)
        self.play(FadeIn(title, shift=UP * 0.15), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(1.4)   # don't rush past it
        self.play(FadeOut(title, shift=DOWN * 0.1), run_time=0.8)

    # ===================================================================== A6
    def act6_the_apparatus(self):
        # ── "The apparatus." Build it as a reveal — each part a character. ──
        P = np.array([0.0, 0.7, 0.0])          # the wire's base / pivot
        TOPY = 3.4

        # 1) The wire — descends slowly, settles with an elastic wobble.
        wire = Line([P[0], TOPY, 0], [P[0], P[1], 0], color=COLOR_WIRE,
                    stroke_width=2.5)
        wire_glow = Line([P[0], TOPY, 0], [P[0], P[1], 0], color=COLOR_WIRE,
                         stroke_width=7, stroke_opacity=0.12)
        self.play(Create(wire), Create(wire_glow), run_time=1.2,
                  rate_func=rate_functions.ease_out_cubic)
        self.play(Rotate(VGroup(wire, wire_glow), 4 * DEGREES, about_point=[P[0], TOPY, 0]),
                  run_time=0.7, rate_func=rate_functions.wiggle)   # delicate settle
        w_lab = Text("sensitive torsion wire", font=FONT, font_size=18,
                     color=COLOR_WIRE, slant=ITALIC).next_to(
                        [P[0], (TOPY + P[1]) / 2, 0], RIGHT, buff=0.3)
        self.play(FadeIn(w_lab, shift=LEFT * 0.1), run_time=0.5)
        self.wait(0.4)

        # 2) The rod — drops in vertical, swings 90° to horizontal, balanced.
        ROD_L = 1.7
        rod = Line(P, P + UP * ROD_L, color=COLOR_GROUND, stroke_width=5)
        self.play(FadeIn(rod), run_time=0.3)
        rod_target_angle = -90 * DEGREES
        self.play(Rotate(rod, rod_target_angle, about_point=P),
                  run_time=1.0, rate_func=rate_functions.ease_out_back)
        # the rod is now horizontal, pointing RIGHT from P; mirror its left arm
        rod_full = Line(P + LEFT * ROD_L, P + RIGHT * ROD_L, color=COLOR_GROUND,
                        stroke_width=5)
        self.play(ReplacementTransform(rod, rod_full), run_time=0.4)
        r_lab = Text("lightweight rod", font=FONT, font_size=18,
                     color=COLOR_GROUND, slant=ITALIC).next_to(rod_full, DOWN, buff=0.25)
        self.play(FadeIn(r_lab), run_time=0.4)
        self.wait(0.4)

        # 3) The small balls — bounce in symmetrically at the rod's ends.
        smL = make_ball(COLOR_LEAD_SM, 0.16).move_to(P + LEFT * ROD_L)
        smR = make_ball(COLOR_LEAD_SM, 0.16).move_to(P + RIGHT * ROD_L)
        self.play(FadeIn(smL, scale=0.4), FadeIn(smR, scale=0.4),
                  run_time=0.6, rate_func=rate_functions.ease_out_back)
        m_lab = MathTex("m", font_size=30, color=COLOR_LEAD_SM
                        ).next_to(smR, UP, buff=0.18)
        self.play(FadeIn(m_lab), run_time=0.35)
        self.wait(0.3)

        # group the rotating beam (rod + small balls + their reference)
        beam = VGroup(rod_full, smL, smR)

        # 4) The large balls — roll in from the sides; placed off-axis so they
        #    pull the small balls tangentially → a torque. Force arrows appear.
        lgT = make_ball(COLOR_LEAD_LG, 0.30).move_to([P[0] - ROD_L - 0.7,
                                                      P[1] + 0.9, 0])
        lgB = make_ball(COLOR_LEAD_LG, 0.30).move_to([P[0] + ROD_L + 0.7,
                                                      P[1] - 0.9, 0])
        self.play(FadeOut(r_lab), FadeOut(m_lab), FadeOut(w_lab), run_time=0.3)
        lgT.move_to([P[0] - ROD_L - 4.0, P[1] + 0.9, 0])
        lgB.move_to([P[0] + ROD_L + 4.0, P[1] - 0.9, 0])
        self.add(lgT, lgB)
        self.play(lgT.animate.move_to([P[0] - ROD_L - 0.45, P[1] + 0.55, 0]),
                  lgB.animate.move_to([P[0] + ROD_L + 0.45, P[1] - 0.55, 0]),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        M_lab = MathTex("M", font_size=34, color=COLOR_LEAD_LG
                        ).next_to(lgB, DOWN, buff=0.18)
        self.play(FadeIn(M_lab), run_time=0.35)

        # tiny dotted attraction arrows: each small ball nudged toward its big one
        pullL = Arrow(smL.get_center(), smL.get_center() + UP * 0.5, buff=0.18,
                      color=COLOR_VEC_F, stroke_width=2.5,
                      max_tip_length_to_length_ratio=0.4).set_opacity(0.7)
        pullR = Arrow(smR.get_center(), smR.get_center() + DOWN * 0.5, buff=0.18,
                      color=COLOR_VEC_F, stroke_width=2.5,
                      max_tip_length_to_length_ratio=0.4).set_opacity(0.7)
        self.play(GrowArrow(pullL), GrowArrow(pullR), run_time=0.6)
        self.wait(0.4)

        # the beam twists — ever so slightly (exaggerated here for the eye).
        TWIST = 9 * DEGREES
        ref = Line(P + LEFT * ROD_L, P + RIGHT * ROD_L, color=COLOR_DIM,
                   stroke_width=2, stroke_opacity=0.5)   # ghost of the rest position
        self.add(ref)
        self.play(FadeOut(pullL), FadeOut(pullR),
                  Rotate(beam, -TWIST, about_point=P),
                  run_time=1.2, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        # 5) The twist angle θ — the money shot. Zoom in; make smallness matter.
        arc = Arc(radius=0.9, start_angle=0, angle=-TWIST, arc_center=P,
                  color=COLOR_AMBER, stroke_width=3)
        th = MathTex(r"\theta", font_size=34, color=COLOR_AMBER
                     ).move_to(P + RIGHT * 1.15 + UP * 0.18)
        self.play(self.camera.frame.animate.scale(0.5).move_to(P + RIGHT * 0.6),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.play(Create(arc), FadeIn(th, scale=0.5), run_time=0.7)
        self.play(arc.animate.set_stroke(width=5), run_time=0.4,
                  rate_func=rate_functions.there_and_back)
        self.wait(0.8)
        self.play(Restore(self.camera.frame), run_time=1.1,
                  rate_func=rate_functions.ease_in_out_sine)

        # ── Mechanical amplification: small twist → mirror → long beam → big shift.
        apparatus = VGroup(wire, wire_glow, beam, ref, lgT, lgB, M_lab, arc, th)


        # OVERLAY — a physical anchor: a replica photograph, one beat.
        plate = safe_image(IMG_CAVENDISH, 4.4, "Cavendish_Experiment.png", ratio=0.7)
        plate.move_to(ORIGIN).set_z_index(30)
        self.play(FadeIn(plate, scale=0.97), run_time=0.7)
        self.wait(1.4)
        self.play(FadeOut(plate), run_time=0.6)

        self._clear_to_grid()

    # ===================================================================== A7
    def act7_telescope_outside(self):
        # ── "Telescope se bahar khada." The paranoid-genius detail. ──
        # Top-down floor plan: the shed. Apparatus = a dot inside.
        room = Rectangle(width=4.6, height=3.4, color=COLOR_GROUND, stroke_width=2.5,
                         fill_opacity=0).move_to(LEFT * 0.4)
        # leave a window gap on the right wall
        win = Line(room.get_right() + UP * 0.5, room.get_right() + DOWN * 0.5,
                   color=COLOR_BG, stroke_width=6)
        appdot = VGroup(Dot(room.get_center(), radius=0.12, color=COLOR_WIRE),
                        Circle(radius=0.32, color=COLOR_WIRE, stroke_width=1.5,
                               stroke_opacity=0.5).move_to(room.get_center()))
        self.play(Create(room), run_time=0.8)
        self.add(win)
        self.play(FadeIn(appdot, scale=0.6), run_time=0.5)

        # a tiny needle on the apparatus we can watch wobble.
        needle = Line(room.get_center(), room.get_center() + RIGHT * 0.5,
                      color=COLOR_AMBER, stroke_width=3)
        self.add(needle)

        # heat shimmer and air arrows to represent convection disturbance.
        INSIDE_POS = room.get_center() + RIGHT * 1.4 + DOWN * 0.6
        def shimmer(at, h=0.7):
            v = VMobject(stroke_color=COLOR_VEC_F, stroke_width=2,
                         stroke_opacity=0.45)
            pts = [at + UP * (h * k / 6) + RIGHT * 0.10 * np.sin(k)
                   for k in range(7)]
            v.set_points_smoothly(pts)
            return v
        sh = VGroup(shimmer(INSIDE_POS + UP * 0.05),
                    shimmer(INSIDE_POS + UP * 0.05 + RIGHT * 0.18))
        air = VGroup(*[Arrow(INSIDE_POS + LEFT * 0.1 + UP * 0.1,
                             room.get_center() + RIGHT * 0.5,
                             buff=0.1, color=COLOR_VEC_F, stroke_width=2,
                             max_tip_length_to_length_ratio=0.2).set_opacity(0.35)])
        self.play(Create(sh), run_time=0.6)
        self.play(LaggedStart(*[Create(a) for a in air], lag_ratio=0.2),
                  run_time=0.5)
        # the needle wobbles chaotically
        for dx in (12, -16, 9, -7, 5):
            self.play(Rotate(needle, dx * DEGREES, about_point=room.get_center()),
                      run_time=0.10)
        self.wait(0.5)

        # the disturbance moves OUTSIDE; the air settles; the needle stills.
        out_pos = room.get_right() + RIGHT * 1.7
        self.play(FadeOut(air), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        # heat shimmer moves outside; the air settles; the needle stills.
        sh2 = VGroup(shimmer(out_pos + DOWN * 0.1),
                     shimmer(out_pos + DOWN * 0.1 + RIGHT * 0.18))
        self.play(Transform(sh, sh2), run_time=0.6)
        self.play(Rotate(needle,
                         -needle.get_angle(),  # snap back to flat RIGHT
                         about_point=room.get_center()),
                  run_time=0.8, rate_func=rate_functions.ease_out_elastic)
        stable = Text("stable", font=FONT, font_size=22, slant=ITALIC,
                      color=COLOR_GREEN).next_to(room, UP, buff=0.4)
        self.play(FadeIn(stable), run_time=0.4)
        self.wait(1.2)

        self._clear_to_grid()

    # ===================================================================== A8
    def act8_the_solve(self):
        # ── "G nikla." Rearrange, load each measured value in, reveal G. ──
        f = build_formula(fs=54)
        f.G.set_color(COLOR_G_GOLD)
        f.to_edge(UP, buff=1.1)
        self.play(Write(f), run_time=1.2, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        arrow = MathTex(r"\downarrow", font_size=44, color=COLOR_GROUND
                        ).next_to(f, DOWN, buff=0.35)
        self.play(FadeIn(arrow, shift=DOWN * 0.1), run_time=0.4)

        # Build  G = F r² / (M m)  from addressable glyphs.
        Gs_G = MathTex("G", font_size=58, color=COLOR_G_GOLD)
        Gs_eq = MathTex("=", font_size=58, color=COLOR_WHITE)
        F_g = MathTex("F", font_size=54, color=COLOR_WHITE)
        r_g = MathTex("r", font_size=54, color=COLOR_WHITE)
        r_e = MathTex("2", font_size=33, color=COLOR_WHITE)
        r_e.next_to(r_g, UR, buff=0.0).shift(DOWN * 0.04 + LEFT * 0.02)
        num = VGroup(F_g, VGroup(r_g, r_e)).arrange(RIGHT, buff=0.10)
        M_g = MathTex("M", font_size=54, color=COLOR_WHITE)
        m_g = MathTex("m", font_size=54, color=COLOR_WHITE)
        den = VGroup(M_g, m_g).arrange(RIGHT, buff=0.10)
        fr = frac(num, den, pad=0.28)
        Gsolve = VGroup(Gs_G, Gs_eq, fr).arrange(RIGHT, buff=0.22)
        Gsolve.next_to(arrow, DOWN, buff=0.35)
        self.play(Write(Gsolve), run_time=1.3,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        # Each measured value is "loaded in" — a pulse in its semantic colour.
        loads = [(F_g, COLOR_VEC_F, "from the twist"),
                 (VGroup(r_g, r_e), COLOR_GREEN, "from the geometry"),
                 (M_g, COLOR_M, "known mass"),
                 (m_g, COLOR_m, "known mass")]
        for glyph, col, note in loads:
            cap = Text(note, font=FONT, font_size=18, slant=ITALIC,
                       color=col).next_to(Gsolve, DOWN, buff=0.5)
            self.play(glyph.animate.set_color(col).scale(1.22),
                      FadeIn(cap, shift=UP * 0.08), run_time=0.45)
            self.play(glyph.animate.scale(1 / 1.22), FadeOut(cap), run_time=0.35)
        self.wait(0.5)

        # the answer arrives in two parts: 6.674 (gold), then the apologetic 10⁻¹¹
        self.play(FadeOut(arrow), FadeOut(f),
                  Gsolve.animate.to_edge(UP, buff=1.2).scale(0.85),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_sine)

        head = MathTex("6.674", font_size=80, color=COLOR_G_GOLD).move_to(DOWN * 0.2)
        self.play(FadeIn(head, shift=UP * 0.1), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)
        tail = MathTex(r"\times 10^{-11}", font_size=44, color=COLOR_G_GOLD
                       ).next_to(head, RIGHT, buff=0.18)
        units = MathTex(r"\text{N·m}^2/\text{kg}^2", font_size=34,
                        color=COLOR_GROUND).next_to(tail, RIGHT, buff=0.25)
        self.play(FadeIn(tail, scale=0.6), run_time=0.7)   # the exponent is the punchline
        self.play(FadeIn(units, shift=LEFT * 0.1), run_time=0.5)
        self.play(tail.animate.scale(1.18), run_time=0.5,
                  rate_func=rate_functions.there_and_back)
        self.wait(1.4)

        self._clear_to_grid()

    # ===================================================================== A9
    def act9_smallness_lands(self):
        # ── "Itna chhota kyun?" Make 10⁻¹¹ feel real. ──
        # LEFT: two lab masses 1 m apart — a mosquito's worth of pull.
        pL = make_ball(COLOR_LEAD_SM, 0.18).move_to([-4.6, -0.4, 0])
        pR = make_ball(COLOR_LEAD_SM, 0.18).move_to([-2.4, -0.4, 0])
        gap = DoubleArrow([-4.3, -1.2, 0], [-2.7, -1.2, 0], buff=0,
                          color=COLOR_GROUND, stroke_width=2,
                          max_tip_length_to_length_ratio=0.08)
        self.play(FadeIn(pL), FadeIn(pR), GrowFromCenter(gap),
                  run_time=0.8)
        tiny = Arrow(pL.get_right() + RIGHT * 0.45, pL.get_right() + RIGHT * 0.28,
                     buff=0, color=COLOR_VEC_F, stroke_width=2,
                     max_tip_length_to_length_ratio=0.9)
        fnum_l = MathTex(r"\approx 3\times10^{-7}\ \text{N}", font_size=26,
                         color=COLOR_VEC_F).next_to(VGroup(pL, pR), UP, buff=0.5)
        self.wait(0.8)

        divider = DashedLine([0, 2.6, 0], [0, -2.6, 0], color=COLOR_WHITE,
                             stroke_width=2, dash_length=0.14).set_opacity(0.4)
        self.play(Create(divider), run_time=0.5)

        # RIGHT: Earth pulling a small mass — overwhelming.
        earth = safe_earth(2.6).move_to([3.6, -1.5, 0]).set_z_index(1)
        person = make_ball(COLOR_LEAD_SM, 0.18).move_to([3.6, 1.5, 0]).set_z_index(2)
        fnum_r = MathTex(r"\approx 700\ \text{N}", font_size=30, color=COLOR_VEC_F
                         ).next_to(person, RIGHT, buff=0.4)
        self.play(FadeIn(earth, shift=UP * 0.15), FadeIn(person), run_time=0.7)
        self.play(FadeIn(fnum_r), run_time=0.6)

        # collapse to G alone — small, golden — and the Hinglish line.
        self.play(*[FadeOut(m) for m in (pL, pR, gap, tiny, fnum_l,
                                          divider, earth, person, fnum_r)], run_time=0.8)
        G = MathTex("G", font_size=120, color=COLOR_G_GOLD).move_to(UP * 0.4)
        glow = Dot(G.get_center(), radius=0.7, color=COLOR_G_GOLD,
                   fill_opacity=0.0, stroke_width=0).set_z_index(-1)
        self.add(glow)
        self.play(FadeIn(G, scale=0.7), glow.animate.set_opacity(0.25),
                  run_time=0.9)
        self.wait(0.6)

        self._clear_to_grid()

    # ===================================================================== A10
    def act10_weighing_the_earth(self):
        # ── "Earth ko tol diya." Run the formula in reverse. End with scale. ──
        f = build_formula(fs=54)
        f.G.set_color(COLOR_G_GOLD)
        f.move_to(UP * 1.0)
        self.play(Write(f), run_time=1.0, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        self.play(FadeOut(f), run_time=0.2)

        # M_⊕ = F r² / (G m), built addressable for the lock-in.
        Me = MathTex(r"M_{\oplus}", font_size=58, color=COLOR_M)
        eq = MathTex("=", font_size=58, color=COLOR_WHITE)
        F_g = MathTex("F", font_size=54, color=COLOR_VEC_F)
        r_g = MathTex("r", font_size=54, color=COLOR_GREEN)
        r_e = MathTex("2", font_size=33, color=COLOR_GREEN)
        r_e.next_to(r_g, UR, buff=0.0).shift(DOWN * 0.04 + LEFT * 0.02)
        num = VGroup(F_g, VGroup(r_g, r_e)).arrange(RIGHT, buff=0.10)
        G_g = MathTex("G", font_size=54, color=COLOR_G_GOLD)
        m_g = MathTex("m", font_size=54, color=COLOR_m)
        den = VGroup(G_g, m_g).arrange(RIGHT, buff=0.10)
        fr = frac(num, den, pad=0.28)
        Msolve = VGroup(Me, eq, fr).arrange(RIGHT, buff=0.22).move_to(UP * 1.0)
        self.play(Write(Msolve), run_time=1.0)
        self.wait(0.5)

        # each known quantity locks in (G pulses gold) — a satisfying click each.
        for glyph in (G_g, F_g, r_g, m_g):
            self.play(glyph.animate.scale(1.25), run_time=0.28,
                      rate_func=rate_functions.there_and_back)
            self.play(Flash(glyph.get_center(), color=glyph.get_color(),
                            line_length=0.10, num_lines=8, flash_radius=0.28),
                      run_time=0.22)
        self.wait(0.5)

        # the Earth's mass falls out of the math.
        result = MathTex(r"M_{\oplus} \approx 5.97 \times 10^{24}\ \text{kg}",
                         font_size=46, color=COLOR_WHITE).move_to(DOWN * 0.6)
        result[0][:3].set_color(COLOR_M)
        self.play(Msolve.animate.to_edge(UP, buff=1.0).scale(0.8),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeIn(result, shift=UP * 0.1), run_time=0.8)
        self.wait(1.0)

        # the Earth — now weighed — arrives on a balance; the camera pulls back.
        self.play(FadeOut(Msolve), result.animate.to_edge(UP, buff=0.8),
                  run_time=0.8)

        earth = safe_earth(2.2).move_to(UP * 0.3).set_z_index(2)
        self.play(FadeIn(earth, scale=0.6), run_time=0.9)

        # a simple balance beneath the planet.
        fulcrum = Triangle(color=COLOR_GROUND, fill_opacity=0.0, stroke_width=3)
        fulcrum.scale(0.4).move_to(DOWN * 2.4)
        beam = Line(LEFT * 2.2, RIGHT * 2.2, color=COLOR_GROUND, stroke_width=4
                    ).move_to(DOWN * 1.9)
        pan = Line(LEFT * 0.7, RIGHT * 0.7, color=COLOR_GROUND, stroke_width=3
                   ).move_to(DOWN * 1.55)
        hangers = VGroup(
            Line(beam.get_center() + LEFT * 0.7 + UP * 0.0, pan.get_left(),
                 color=COLOR_GROUND, stroke_width=2),
            Line(beam.get_center() + RIGHT * 0.7 + UP * 0.0, pan.get_right(),
                 color=COLOR_GROUND, stroke_width=2))
        self.play(self.camera.frame.animate.scale(1.25).move_to(DOWN * 0.4),
                  LaggedStart(Create(fulcrum), Create(beam), Create(pan),
                              Create(hangers), lag_ratio=0.15),
                  earth.animate.move_to(DOWN * 0.9).scale(0.85),
                  run_time=1.8, rate_func=rate_functions.ease_in_out_sine)

        self.wait(0.8)

        # POST: fade the world to near-black; number + Earth remain. Hold, cut.
        keep = Group(earth, result)
        rest = Group(*[m for m in self.mobjects
                       if m not in (earth, result) and m is not self.grid])
        self.play(FadeOut(rest), self.grid.animate.set_opacity(0.0),
                  run_time=1.5, rate_func=rate_functions.ease_in_out_sine)
        self.play(result.animate.next_to(earth, UP, buff=0.6), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(2.5)
        self.play(FadeOut(keep), run_time=1.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)   # hard cut to black happens in Premiere