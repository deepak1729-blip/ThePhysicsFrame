from manim import *
import numpy as np

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
COLOR_BG       = "#0E1117"
COLOR_GROUND   = "#8E8E93"
COLOR_WHITE    = "#E5E5EA"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F    = "#FF3B30"   # red  = gravity / force
COLOR_VEC_V    = "#32ADE6"   # cyan = velocity
COLOR_GREEN    = "#34C759"
COLOR_AMBER    = "#FFCC00"   # sun / time / Newton
COLOR_PINK     = "#FF2D55"
COLOR_ORANGE   = "#FF9500"
COLOR_COVER    = "#22262E"   # book cover slate

FONT = "Segoe UI"

config.background_color = COLOR_BG

# Deterministic randomness (stable shapes -> stable caching)
RNG = np.random.default_rng(7)


# ----------------------------------------------------------------------------
# Helpers — same construction vocabulary as the rest of the series
# ----------------------------------------------------------------------------
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


def make_particle(color, radius=0.10):
    """Bright point of light with soft halos (from the centripetal episode)."""
    g = VGroup()
    for i, (r_mult, op) in enumerate([(4.2, 0.05), (2.8, 0.10), (1.7, 0.20)]):
        g.add(Dot(ORIGIN, radius=radius * r_mult, color=color,
                  fill_opacity=op, stroke_width=0))
    core = Dot(ORIGIN, radius=radius, color=COLOR_WHITE, fill_opacity=1.0,
               stroke_width=0)
    glow = Dot(ORIGIN, radius=radius * 1.25, color=color, fill_opacity=0.9,
               stroke_width=0)
    g.add(glow, core)
    return g

# A single frozen irregular profile -> stable across stones (good for caching)
_STONE_PROFILE = None
def _stone_profile():
    global _STONE_PROFILE
    if _STONE_PROFILE is None:
        n = 11
        angs = np.linspace(0, TAU, n, endpoint=False)
        rs = 1.0 + 0.22 * (RNG.random(n) - 0.5) * 2
        _STONE_PROFILE = [(float(r * np.cos(a)), float(r * np.sin(a)))
                          for a, r in zip(angs, rs)]
    return _STONE_PROFILE


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


def _earth_glyph():
    """Cover glyph for Earth's book: a stone, a downward hint, a ground tick."""
    g = VGroup()
    s = make_stone(0.16)
    arr = Arrow(s.get_center() + DOWN * 0.06, s.get_center() + DOWN * 0.42,
                buff=0, color=COLOR_GROUND, stroke_width=3,
                max_tip_length_to_length_ratio=0.4).set_opacity(0.7)
    tick = Line(LEFT * 0.34, RIGHT * 0.34, color=COLOR_GROUND,
                stroke_width=2.5).move_to(s.get_center() + DOWN * 0.56)
    g.add(arr, s, tick)
    return g


def _sky_glyph():
    """Cover glyph for Sky's book: an orbit with an amber sun dot."""
    g = VGroup()
    orbit = Ellipse(width=0.92, height=0.60, color=COLOR_BLUE_BALL,
                    stroke_width=2.5, fill_opacity=0)
    sun = Dot(orbit.get_center() + RIGHT * 0.14, radius=0.055,
              color=COLOR_AMBER, fill_opacity=1.0, stroke_width=0)
    planet = Dot(orbit.get_center() + LEFT * 0.40, radius=0.035,
                 color=COLOR_BLUE_BALL, fill_opacity=1.0, stroke_width=0)
    g.add(orbit, sun, planet)
    return g


def make_book(spine_color, glow_color, glyph, width=1.7, height=2.3):
    """Front-facing closed rule book — ADAPTED from the third-law table-book
    into an upright/floating book (same shading vocabulary: cover fill,
    accent spine, page-edge lines, sheen, specular, soft colored edge-glow).
    Returns a VGroup; glyph is centred on the cover."""
    g = VGroup()

    # Soft colored edge-glow behind the cover
    glow = RoundedRectangle(width=width + 0.34, height=height + 0.34,
                            corner_radius=0.14, stroke_width=0,
                            fill_color=glow_color, fill_opacity=0.16)
    g.add(glow)

    # Cover
    cover = RoundedRectangle(width=width, height=height, corner_radius=0.08,
                             fill_color=COLOR_COVER, fill_opacity=1.0,
                             stroke_color=spine_color, stroke_width=2.2)
    g.add(cover)

    # Spine (left band, accent colour)
    spine = Rectangle(width=0.16, height=height - 0.06, fill_color=spine_color,
                      fill_opacity=1.0, stroke_width=0)
    spine.move_to(cover.get_left() + RIGHT * 0.12)
    g.add(spine)

    # Sheen + specular on the cover
    sheen = Polygon([-width / 2 + 0.10, height / 2 - 0.10, 0],
                    [-width / 2 + 0.55, height / 2 - 0.10, 0],
                    [-width / 2 + 0.10, height / 2 - 0.70, 0],
                    color=COLOR_WHITE, fill_opacity=0.05, stroke_width=0)
    g.add(sheen)

    # Glyph on the cover
    glyph.move_to(cover.get_center())
    g.add(glyph)
    return g


# ----------------------------------------------------------------------------
# Kepler orbit (Act 3) — true fast-perihelion / slow-aphelion motion
# ----------------------------------------------------------------------------
A_ELL = 3.0
B_ELL = 2.0
C_ELL = float(np.sqrt(A_ELL**2 - B_ELL**2))   # ~2.236
ECC   = C_ELL / A_ELL                          # ~0.745
SUN_POS = np.array([C_ELL, 0.0, 0.0])          # right focus


def _ecc_anomaly(M):
    """Solve Kepler's equation M = E - e sinE (Newton iteration)."""
    E = M
    for _ in range(6):
        E = E - (E - ECC * np.sin(E) - M) / (1 - ECC * np.cos(E))
    return E


def planet_pos(M):
    E = _ecc_anomaly(M)
    return np.array([A_ELL * np.cos(E), B_ELL * np.sin(E), 0.0])


def planet_state(M):
    """Return (position, unit velocity dir, scaled speed)."""
    E = _ecc_anomaly(M)
    pos = np.array([A_ELL * np.cos(E), B_ELL * np.sin(E), 0.0])
    dx, dy = -A_ELL * np.sin(E), B_ELL * np.cos(E)
    denom = 1 - ECC * np.cos(E)
    speed = np.hypot(dx, dy) / max(denom, 1e-6)
    vlen = np.hypot(dx, dy)
    vdir = np.array([dx / vlen, dy / vlen, 0.0]) if vlen > 1e-6 else RIGHT
    return pos, vdir, speed


# ============================================================================
class Scene_1_TwoRuleBooks(MovingCameraScene):
    def construct(self):
        self.camera.frame.save_state()   # default frame, restored later

        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        self.act1_two_rule_books()
        self.act2_galileo()
        self.act3_kepler()
        self.act4_the_divide()

    # ------------------------------------------------------------------ ACT 1
    def act1_two_rule_books(self):
        # The seam — the divide. Persists through the act.
        # POST: a single clean tick lands here.
        self.seam = Line([-7.2, 0, 0], [7.2, 0, 0], color=COLOR_WHITE,
                         stroke_width=1.6, stroke_opacity=0.45)
        self.play(Create(self.seam), run_time=0.7)

        self.EARTH_REST = np.array([-3.5, -1.7, 0])
        self.SKY_REST   = np.array([3.5, 1.7, 0])

        earth = make_book(COLOR_GROUND, COLOR_ORANGE, _earth_glyph())
        sky   = make_book(COLOR_BLUE_BALL, COLOR_BLUE_BALL, _sky_glyph())

        # Fly in from opposite edges, slightly oversized, settle to 1.0.
        earth.scale(1.06).move_to(self.EARTH_REST + LEFT * 9)
        sky.scale(1.06).move_to(self.SKY_REST + RIGHT * 9)
        self.add(earth, sky)

        self.play(
            LaggedStart(
                earth.animate(rate_func=rate_functions.ease_out_cubic)
                     .scale(1 / 1.06).move_to(self.EARTH_REST),
                sky.animate(rate_func=rate_functions.ease_out_cubic)
                   .scale(1 / 1.06).move_to(self.SKY_REST),
                lag_ratio=0.30),
            run_time=1.3)

        self.earth_book, self.sky_book = earth, sky
        self.wait()

    # ------------------------------------------------------------------ ACT 2
    def act2_galileo(self):
        # Drill into Earth's book, then emerge into the page.
        self.play(self.camera.frame.animate.scale(0.4).move_to(self.earth_book),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeOut(self.earth_book), FadeOut(self.sky_book),
                  FadeOut(self.seam), Restore(self.camera.frame),
                  run_time=0.7)
        self.play(Restore(self.camera.frame),
                  run_time=1.2)

        # Ground with hatch
        GY = -2.9
        ground = Line([-7, GY, 0], [7, GY, 0], color=COLOR_GROUND,
                      stroke_width=3)
        hatch = VGroup(*[
            Line([x, GY, 0], [x - 0.28, GY - 0.28, 0], color=COLOR_GROUND,
                 stroke_width=1.6, stroke_opacity=0.5)
            for x in np.arange(-6.6, 7.0, 0.5)])
        self.play(Create(ground), run_time=0.5)
        self.add(hatch)

        # Two stones, different mass, held aloft at the same height.
        Y0 = 2.3
        BIG_X, SMALL_X = -1.3, 1.3
        big   = make_stone(0.36).move_to([BIG_X, Y0, 0])
        small = make_stone(0.24).move_to([SMALL_X, Y0, 0])
        self.play(LaggedStart(FadeIn(big, shift=DOWN * 0.2),
                              FadeIn(small, shift=DOWN * 0.2),
                              lag_ratio=0.2), run_time=0.7)

        # ---- Wrong intuition first (ghosts): heavy lands sooner ----
        ghost_big   = big.copy().set_opacity(0.30)
        ghost_small = small.copy().set_opacity(0.30)
        path_big   = DashedLine([BIG_X, Y0, 0], [BIG_X, GY + 0.36, 0],
                                color=COLOR_WHITE, stroke_opacity=0.25,
                                dash_length=0.12)
        path_small = DashedLine([SMALL_X, Y0, 0], [SMALL_X, GY + 0.24, 0],
                                color=COLOR_WHITE, stroke_opacity=0.25,
                                dash_length=0.12)
        caption = Text("Shouldn't the heavy one win?", font=FONT,
                       slant=ITALIC, color=COLOR_GROUND, font_size=26)
        caption.to_edge(UP, buff=0.6)
        self.add(ghost_big, ghost_small)
        self.play(Create(path_big), Create(path_small), FadeIn(caption),
                  run_time=0.5)
        accel = (lambda a: a * a)   # position ~ t^2
        self.play(ghost_big.animate(rate_func=accel)
                  .move_to([BIG_X, GY + 0.36, 0]), run_time=0.7)
        self.play(ghost_small.animate(rate_func=accel)
                  .move_to([SMALL_X, GY + 0.24, 0]), run_time=1.0)
        self.wait(0.3)
        self.play(FadeOut(ghost_big), FadeOut(ghost_small),
                  FadeOut(path_big), FadeOut(path_small), FadeOut(caption),
                  run_time=0.5)

        # ---- Quiet red plant: identical-length gravity arrows ----
        # (No label. We don't explain it yet.)
        def g_arrow(stone):
            c = stone.get_center()
            return Arrow(c + DOWN * 0.08, c + DOWN * 0.78, buff=0,
                         color=COLOR_VEC_F, stroke_width=4,
                         max_tip_length_to_length_ratio=0.32)
        ga_big, ga_small = g_arrow(big), g_arrow(small)
        self.play(GrowArrow(ga_big), GrowArrow(ga_small), run_time=0.5)
        self.wait(0.25)

        # ---- The real drop: both CENTERS follow the same y(t) ----
        REST_C = GY + 0.30
        T_LAND = 1.8
        g_acc = 2 * (Y0 - REST_C) / T_LAND**2

        def y_of(t):
            return max(Y0 - 0.5 * g_acc * t * t, REST_C)

        t = ValueTracker(0.0)
        big.add_updater(lambda m: m.move_to([BIG_X, y_of(t.get_value()), 0]))
        small.add_updater(lambda m: m.move_to([SMALL_X, y_of(t.get_value()), 0]))

        # Live amber connector between the two centres — stays dead flat.
        connector = always_redraw(lambda: DashedLine(
            big.get_center(), small.get_center(),
            color=COLOR_AMBER, stroke_width=2.5, dash_length=0.12))
        self.add(connector)
        self.play(FadeOut(ga_big), FadeOut(ga_small), run_time=0.3)

        # Strobe: stamp faint afterimages at growing gaps (= acceleration).
        stamps = VGroup()
        last = 0.0
        for tp in [0.7, 1.1, 1.45]:
            self.play(t.animate.set_value(tp), run_time=(tp - last),
                      rate_func=linear)
            yb = y_of(tp)
            stamps.add(
                Dot([BIG_X, yb, 0], radius=0.05, color=COLOR_WHITE,
                    fill_opacity=0.22, stroke_width=0),
                Dot([SMALL_X, yb, 0], radius=0.05, color=COLOR_WHITE,
                    fill_opacity=0.22, stroke_width=0),
                DashedLine([BIG_X, yb, 0], [SMALL_X, yb, 0], color=COLOR_AMBER,
                           stroke_width=1.6, stroke_opacity=0.22,
                           dash_length=0.10))
            self.add(stamps)
            last = tp
        self.play(t.animate.set_value(T_LAND), run_time=(T_LAND - last),
                  rate_func=linear)

        # Freeze + land.
        big.clear_updaters()
        small.clear_updaters()
        self.remove(connector)
        flat = DashedLine(big.get_center(), small.get_center(),
                          color=COLOR_AMBER, stroke_width=2.5, dash_length=0.12)
        self.add(flat)
        self.play(
            Flash([BIG_X, GY, 0], color=COLOR_GROUND, line_length=0.18,
                  num_lines=8, flash_radius=0.4),
            Flash([SMALL_X, GY, 0], color=COLOR_GROUND, line_length=0.16,
                  num_lines=8, flash_radius=0.34),
            run_time=0.5)
        self.wait(0.8)

        # Clear everything except the grid.
        self.play(*[FadeOut(m) for m in [ground, hatch, big, small, flat,
                                         stamps]],
                  run_time=0.8)

    # ------------------------------------------------------------------ ACT 3
    def act3_kepler(self):
        # (1) The swarm of numbers — overwhelming human labour.
        frags = VGroup()
        sample = ["23.51", "0.387", "1601", "365.25", "11.86", "4332",
                  "1.524", "29.46", "9.539", "5.203", "687", "224.7",
                  "0.723", "1.881", "19.18", "84.01", "27.32", "0.967",
                  "13.06", "248", "0.206", "778.5", "1.000", "149.6"]
        for s in sample:
            x = float(RNG.uniform(-6.4, 6.4))
            y = float(RNG.uniform(-3.4, 3.4))
            frags.add(Text(s, font=FONT, color=COLOR_GROUND, font_size=22)
                      .move_to([x, y, 0]).set_opacity(0.38))
        self.play(LaggedStart(*[FadeIn(f) for f in frags], lag_ratio=0.08),
                  run_time=2.6)
        self.wait(0.3)

        # (2) Condense: observations settle onto an ellipse.
        n_dots = 40
        dots = VGroup()
        targets = []
        for i in range(n_dots):
            th = TAU * i / n_dots
            tgt = np.array([A_ELL * np.cos(th), B_ELL * np.sin(th), 0])
            targets.append(tgt)
            start = np.array([float(RNG.uniform(-6, 6)),
                              float(RNG.uniform(-3.2, 3.2)), 0])
            dots.add(Dot(start, radius=0.04, color=COLOR_WHITE,
                         fill_opacity=0, stroke_width=0))
        self.add(dots)
        self.play(
            LaggedStart(*[d.animate.move_to(t).set_fill(opacity=0.9)
                          for d, t in zip(dots, targets)], lag_ratio=0.03),
            FadeOut(frags), run_time=2.4)

        ellipse = Ellipse(width=2 * A_ELL, height=2 * B_ELL,
                          color=COLOR_WHITE, stroke_width=2.5, fill_opacity=0)
        sun = ImageMobject("sun.png").scale_to_fit_width(0.58).move_to(SUN_POS)
        self.play(ReplacementTransform(dots, ellipse), run_time=1.0)
        self.play(FadeIn(sun, scale=0.4), run_time=0.6)

        # Pull the camera back — reveal how small & lonely the curve is.
        self.play(self.camera.frame.animate.scale(1.45), run_time=2.0,
                  rate_func=rate_functions.ease_in_out_sine)

        # (3) Speed & time — the planet runs the orbit.
        planet_M = ValueTracker(0.0)
        planet = ImageMobject("earth.png").scale_to_fit_width(0.36)
        planet.add_updater(lambda m: m.move_to(planet_pos(planet_M.get_value())))
        self.add(planet)

        vel = always_redraw(lambda: (lambda st: Arrow(
            st[0], st[0] + st[1] * float(np.clip(0.16 * st[2], 0.30, 1.5)),
            buff=0, color=COLOR_VEC_V, stroke_width=4,
            max_tip_length_to_length_ratio=0.3))(planet_state(planet_M.get_value())))
        # Faint red tether to the sun — the Act-3 plant.
        tether = always_redraw(lambda: Line(
            planet_pos(planet_M.get_value()), SUN_POS,
            color=COLOR_VEC_F, stroke_width=1.8, stroke_opacity=0.35))
        self.add(tether, vel)

        # Clock (lower-right), one full turn per orbit.
        clk_c = np.array([7.4, -4.2, 0])
        clk_r = 0.6
        clock_face = Circle(radius=clk_r, color=COLOR_AMBER, stroke_width=2,
                            stroke_opacity=0.5).move_to(clk_c)
        clock_ticks = VGroup(*[
            Line(clk_c + 0.85 * clk_r * np.array([np.cos(a), np.sin(a), 0]),
                 clk_c + clk_r * np.array([np.cos(a), np.sin(a), 0]),
                 color=COLOR_AMBER, stroke_width=1.6, stroke_opacity=0.5)
            for a in np.linspace(0, TAU, 12, endpoint=False)])
        hand = always_redraw(lambda: Line(
            clk_c, clk_c + 0.78 * clk_r * np.array([
                np.cos(PI / 2 - planet_M.get_value()),
                np.sin(PI / 2 - planet_M.get_value()), 0]),
            color=COLOR_AMBER, stroke_width=2.5))
        self.add(clock_face, clock_ticks, hand)

        # Sweep 8 equal-time segments; each stamps an equal-area pie slice.
        slices = VGroup()
        Ms = np.linspace(0, TAU, 9)
        for k in range(8):
            m0, m1 = Ms[k], Ms[k + 1]
            arc_pts = [planet_pos(m) for m in np.linspace(m0, m1, 7)]
            sl = Polygon(SUN_POS, *arc_pts, color=COLOR_VEC_V,
                         fill_opacity=0.09, stroke_width=0)
            self.play(planet_M.animate.set_value(m1), FadeIn(sl),
                      run_time=0.85, rate_func=linear)
            slices.add(sl)

        # The harmonic nod, then move on.
        planet.clear_updaters()
        try:
            harmonic = MathTex(r"T^2 \propto a^3", color=COLOR_AMBER,
                               font_size=46).move_to([0, 0, 0])
        except Exception:
            harmonic = Text("T^2 \u221d a^3", font=FONT, color=COLOR_AMBER,
                            font_size=44).move_to([0, 0, 0])
        self.play(FadeIn(harmonic, scale=0.8),
                  Flash(clk_c, color=COLOR_AMBER, line_length=0.2,
                        num_lines=10, flash_radius=0.7), run_time=0.7)
        self.wait(0.8)

        # Clear updaters and pull back to the Act-1 composition.
        for m in (vel, tether, hand):
            m.clear_updaters()
        self.play(
            *[FadeOut(m) for m in [ellipse, sun, planet, vel, tether, slices,
                                   clock_face, clock_ticks, hand, harmonic]],
            Restore(self.camera.frame), run_time=1.1)

    # ------------------------------------------------------------------ ACT 4
    def act4_the_divide(self):
        # Rebuild the divide at the Act-1 composition.
        seam = Line([-7.2, 0, 0], [7.2, 0, 0], color=COLOR_WHITE,
                    stroke_width=1.6, stroke_opacity=0.45)
        earth = make_book(COLOR_GROUND, COLOR_ORANGE,
                          _earth_glyph()).move_to(self.EARTH_REST)
        sky   = make_book(COLOR_BLUE_BALL, COLOR_BLUE_BALL,
                          _sky_glyph()).move_to(self.SKY_REST)
        self.play(FadeIn(seam), FadeIn(earth), FadeIn(sky), run_time=0.9)

        # The void grows.
        self.play(earth.animate.shift(DL * 0.7), sky.animate.shift(UR * 0.7),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait()
        
        self.play(FadeOut(seam), FadeOut(earth), FadeOut(sky), run_time=0.7)
