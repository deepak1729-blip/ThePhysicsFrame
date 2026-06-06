from manim import *
import numpy as np

# ─────────────────────────────────────────────────────────────────────────
#  BRAND PALETTE  (carried verbatim from the series canvas; one new constant)
# ─────────────────────────────────────────────────────────────────────────
COLOR_BG        = "#0E1117"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_VEC_F     = "#FF3B30"   # red    — gravity / the pull / "falling"
COLOR_VEC_V     = "#32ADE6"   # cyan   — velocity / the tangent ("wants to go")
COLOR_GREEN     = "#34C759"   # green  — confirmation tick
COLOR_AMBER     = "#FFCC00"   # amber  — the tether + the KEY idea (gravity gold)
COLOR_BLUE_BALL = "#007AFF"   # blue   — LOCKED: Earth's mass M
COLOR_CORAL     = "#FF6F61"   # coral  — LOCKED (scene_4): the apple / the punch number
COLOR_DIM       = "#3A3F47"   # ghost / cancelled stroke
COLOR_MOON      = "#A8C4D4"   # NEW    — silver-blue Moon (a new body, not a re-skin)

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
    return ImageMobject("earth.png").scale_to_fit_width(width)



def safe_apple(width):
    return ImageMobject("apple.png").scale_to_fit_width(width)


def safe_moon(width):
    return ImageMobject("moon.png").scale_to_fit_width(width)


def make_moon(radius=None):
    """Thin wrapper: returns a safe_moon sized to match the old particle radius."""
    if radius is None:
        return safe_moon()
    return safe_moon(width=radius * 2)


def down_arrow(top, length, color, sw=5):
    return Arrow(top, top + DOWN * length, buff=0, color=color,
                 stroke_width=sw, max_tip_length_to_length_ratio=0.28)


def check_mark(color=COLOR_GREEN, scale=0.5):
    """The series' satisfying tick (from scene_0/scene_5)."""
    m = VMobject(stroke_color=color, stroke_width=6)
    m.set_points_as_corners([
        LEFT * 0.18 + DOWN * 0.02, DOWN * 0.20, RIGHT * 0.30 + UP * 0.26,
    ])
    return m.scale(scale)


def inv_sq_formula(fs=60):
    """F ∝ 1/r² built from addressable glyphs so acts can grab .r / .exp.
    Numerator '1', a bar, denominator 'r' with a separate gold-able exponent."""
    F    = MathTex("F", font_size=fs, color=COLOR_WHITE)
    prop = MathTex(r"\propto", font_size=fs, color=COLOR_WHITE)
    one  = MathTex("1", font_size=fs, color=COLOR_WHITE)
    r    = MathTex("r", font_size=fs, color=COLOR_GREEN)
    exp  = MathTex("2", font_size=int(fs * 0.62), color=COLOR_AMBER)

    exp.next_to(r, UR, buff=0.0).shift(DOWN * 0.05 + LEFT * 0.02)
    den = VGroup(r, exp)
    bar_w = max(one.width, den.width) + 0.26
    bar = Line(LEFT * bar_w / 2, RIGHT * bar_w / 2, stroke_width=3,
               color=COLOR_WHITE)
    one.next_to(bar, UP, buff=0.10)
    den.next_to(bar, DOWN, buff=0.10)
    frac = VGroup(one, bar, den)

    whole = VGroup(F, prop, frac).arrange(RIGHT, buff=0.24)
    whole.F, whole.prop, whole.one = F, prop, one
    whole.r, whole.exp, whole.bar, whole.frac, whole.den = r, exp, bar, frac, den
    return whole


def wire_sphere(R, color=COLOR_AMBER, n_lat=4, n_lon=7, squash=0.34, sw=2.0):
    """A faked 3-D globe: silhouette circle + foreshortened latitude rings +
    meridian ellipses. Stays in 2-D so the whole scene is one MovingCameraScene
    and renders deterministically — no real ThreeDScene camera collision."""
    g = VGroup()
    # Silhouette (the round outline).
    g.add(Circle(radius=R, color=color, stroke_width=sw, fill_opacity=0))
    # Latitudes: horizontal rings, foreshortened to read as a tilted globe.
    for lat in np.linspace(-1, 1, n_lat + 2)[1:-1]:
        ang = lat * (PI / 2) * 0.82
        rr = R * np.cos(ang)
        yy = R * np.sin(ang)
        ring = Ellipse(width=2 * rr, height=2 * rr * squash,
                       color=color, stroke_width=sw * 0.8, fill_opacity=0)
        ring.shift(UP * yy)
        g.add(ring)
    # Meridians: vertical ellipses whose width collapses toward the edges.
    for t in np.linspace(0, PI, n_lon, endpoint=False):
        w = max(2 * R * abs(np.cos(t)), 0.001)
        mer = Ellipse(width=w, height=2 * R, color=color,
                      stroke_width=sw * 0.8, fill_opacity=0)
        g.add(mer)
    return g


def orbit_point(a, R):
    return np.array([R * np.cos(a), R * np.sin(a), 0.0])


# ═══════════════════════════════════════════════════════════════════════════
class Scene_6_DistanceAndTheSquare(MovingCameraScene):

    # ── locked geometry ──
    EARTH_W   = 2.0                       # Act-1 Earth image width (radius ≈ 1.0)
    APPLE_W   = 0.5
    APPLE_POS = np.array([0.0, 1.22, 0.0])  # apple resting on Earth's north pole
    R_ORBIT   = 3.5                       # Act-1 Moon orbit radius
    LESSON_A  = 30 * DEGREES              # where the "falling" lesson is staged

    def construct(self):
        self.camera.frame.save_state()    # default frame — restored after zooms
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        self.act1_moon_is_falling()
        self.act2_two_numbers()
        self.act4_why_the_square()
        # self.act5_3d_geometry()
        # self.act6_recap()

    def _clear_to_grid(self, run_time=1.0):
        clear = Group(*[m for m in self.mobjects if m is not self.grid])
        if len(clear):
            self.play(FadeOut(clear), run_time=run_time,
                      rate_func=rate_functions.ease_in_out_sine)

    # ===================================================================== A1
    def act1_moon_is_falling(self):
        # ── Handoff from scene_5: F ∝ M·m lingers, then yields to the new question. ──
        # Re-create the scene_5 closing law so the two scenes feel continuous.
        law_M = MathTex("F", r"\propto", "M", r"\cdot", "m",
                        font_size=64, color=COLOR_WHITE)
        law_M[2].set_color(COLOR_BLUE_BALL)   # M in blue
        law_M[4].set_color(COLOR_CORAL)        # m in coral
        law_M.move_to(UP * 0.2)
        self.add(law_M)
        self.wait(0.6)
        self.play(FadeOut(law_M, shift=UP * 0.15), run_time=0.9,
                  rate_func=rate_functions.ease_in_sine)

        # The big pull-back: the apple is on Earth; the cosmos opens up.
        earth = safe_earth(self.EARTH_W).move_to(ORIGIN).set_z_index(1)
        self.play(
            Restore(self.camera.frame),
            FadeIn(earth),
            run_time=1.5, rate_func=rate_functions.ease_in_out_sine)

        # The Moon appears far out; its orbit is drawn like a pencilled circle.
        theta = ValueTracker(-40 * DEGREES)
        moon = make_moon(self.EARTH_W/4).move_to(orbit_point(theta.get_value(), self.R_ORBIT))
        moon.set_z_index(3)
        orbit = DashedVMobject(
            Circle(radius=self.R_ORBIT, color=COLOR_MOON, stroke_width=1.8),
            num_dashes=80).set_stroke(opacity=0.5)
        self.play(FadeIn(moon, scale=0.5), run_time=0.6)
        self.play(Create(orbit), run_time=2.0,
                  rate_func=rate_functions.ease_in_out_sine)  # drawn slowly

        # Let it breathe — the Moon eases up to the lesson position.
        moon.add_updater(
            lambda m: m.move_to(orbit_point(theta.get_value(), self.R_ORBIT)))
        self.play(theta.animate.set_value(self.LESSON_A),
                  run_time=3.0, rate_func=rate_functions.ease_in_out_sine)

        # ── Newton's insight: tangent (would-be path) vs the curve it follows.
        P = orbit_point(self.LESSON_A, self.R_ORBIT)
        tdir = np.array([-np.sin(self.LESSON_A), np.cos(self.LESSON_A), 0])  # CCW
        tangent = Arrow(P, P + tdir * 1.7, buff=0, color=COLOR_VEC_V,
                        stroke_width=4, max_tip_length_to_length_ratio=0.22)
        t_lab = Text("straight line", font=FONT, slant=ITALIC,
                     color=COLOR_VEC_V, font_size=20)
        t_lab.next_to(tangent.get_end(), UP, buff=0.12)

        actual = Arc(radius=self.R_ORBIT, start_angle=self.LESSON_A,
                     angle=26 * DEGREES, arc_center=ORIGIN,
                     color=COLOR_WHITE, stroke_width=3)
        Q = orbit_point(self.LESSON_A + 26 * DEGREES, self.R_ORBIT)

        self.play(GrowArrow(tangent), FadeIn(t_lab, shift=UP * 0.1),
                  run_time=0.7)
        self.wait(0.4)
        self.play(Create(actual), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)

        # The gap between "where it would go" and "where it goes" IS the fall.
        fall = Arrow(tangent.get_end(), Q, buff=0.05, color=COLOR_VEC_F,
                     stroke_width=4, max_tip_length_to_length_ratio=0.3)
        fall_lab = Text("fall", font=FONT,
                        color=COLOR_VEC_F, font_size=22)
        fall_lab.next_to(fall, RIGHT, buff=0.18)
        self.play(GrowArrow(fall), FadeIn(fall_lab, shift=LEFT * 0.1),
                  run_time=0.8)
        self.wait(1.2)

        self.play(FadeOut(VGroup(tangent, t_lab, actual, fall, fall_lab)),
                  run_time=0.6)

        # ── The rain: perpetually falling, perpetually missing = orbit. ──
        # Step the Moon a full loop; at each step stamp a faint inward pull.
        steps = 16
        start_a = self.LESSON_A
        rain = VGroup()
        for k in range(1, steps + 1):
            a = start_a + TAU * k / steps
            p = orbit_point(a, self.R_ORBIT)
            inward = (ORIGIN - p)
            inward = inward / np.linalg.norm(inward)
            tick = Arrow(p, p + inward * 0.5, buff=0, color=COLOR_VEC_F,
                         stroke_width=2.5,
                         max_tip_length_to_length_ratio=0.4).set_opacity(0.35)
            rain.add(tick)
            self.play(theta.animate.set_value(a), FadeIn(tick),
                      run_time=0.42, rate_func=linear)  # constant = inevitable
        moon.clear_updaters()
        self.wait(0.5)

        self._clear_to_grid()

    # ===================================================================== A2
    def act2_two_numbers(self):

        SCALE = 0.43
        R_LEN = 0.5                                 # r_line length before scaling
        LONG_LEN = 60 * R_LEN                      # = 30 units before scaling

        # Earth positioned so its right edge has a small margin from screen left.
        earth_w = 1.0 * SCALE
        earth = safe_earth(earth_w)
        # Place earth so its center is at x = -frame_half + earth_radius + margin
        frame_half = self.camera.frame_width / 2
        earth.move_to(LEFT * (frame_half - earth_w / 2 - 0.15))
        ec = earth.get_center()

        apple = safe_apple(0.15 * SCALE).move_to(ec + RIGHT * R_LEN * SCALE)
        self.play(FadeIn(earth, scale=0.7), run_time=0.8)
        self.play(FadeIn(apple, scale=0.5), run_time=0.5)

        # Short distance r (amber tether motif).
        r_line = Line(ec, apple.get_center(), color=COLOR_AMBER,
                      stroke_width=4 * SCALE)
        r_lab = MathTex("r", color=COLOR_AMBER, font_size=34
                        ).next_to(r_line, DOWN, buff=0.10)
        self.play(Create(r_line), FadeIn(r_lab), run_time=0.6)
        self.wait(0.5)

        # The distance stretches to the Moon — a running counter sells the 60×.
        moon_end = ec + RIGHT * LONG_LEN * SCALE    # exact 60r endpoint
        moon = make_moon(0.14 * SCALE).move_to(moon_end)
        long_line = Line(ec, ec + RIGHT * R_LEN * SCALE, color=COLOR_AMBER,
                         stroke_width=4 * SCALE)
        self.add(long_line)
        counter = MathTex(r"\times 1", color=COLOR_AMBER, font_size=30
                          ).next_to(long_line.get_end(), UP, buff=0.12)
        self.play(FadeIn(counter), run_time=0.3)

        for mult, frac in [(10, 10/60), (20, 20/60), (40, 40/60), (60, 1.0)]:
            tip = ec + RIGHT * LONG_LEN * SCALE * frac
            new_counter = MathTex(rf"\times {mult}", color=COLOR_AMBER,
                                  font_size=30).next_to(tip, UP, buff=0.12)
            self.play(
                long_line.animate.put_start_and_end_on(ec, tip),
                ReplacementTransform(counter, new_counter),
                run_time=0.5, rate_func=rate_functions.ease_out_cubic)
            counter = new_counter
        self.play(FadeIn(moon), run_time=0.4)

        sixtyr = MathTex("60r", color=COLOR_AMBER, font_size=38
                         ).move_to(counter)
        self.play(ReplacementTransform(counter, sixtyr),
                  sixtyr.animate.scale(1.15),
                  run_time=0.5, rate_func=rate_functions.ease_out_back)
        self.wait(0.8)

        # Sweep the geometry up; the two acceleration numbers take the stage.
        diagram = Group(earth, apple, r_line, r_lab, long_line, moon,
                         sixtyr)
        self.play(diagram.animate.scale(0.62).to_edge(UP, buff=0.3)
                  .set_opacity(0.5), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)

        a_seb = MathTex(r"a_{\text{apple}}", "=", r"9.8", r"\ \text{m/s}^2",
                        font_size=46)
        a_seb[0].set_color(COLOR_CORAL)
        a_seb.move_to(UP * 0.4)

        a_moon = MathTex(r"a_{\text{moon}}", "=", r"\frac{9.8}{3600}",
                         r"\approx", r"0.0027\ \text{m/s}^2", font_size=46)
        a_moon[0].set_color(COLOR_MOON)
        a_moon.next_to(a_seb, DOWN, buff=0.7, aligned_edge=LEFT)

        self.play(Write(a_seb), run_time=0.9)
        self.wait(0.3)
        # 9.8 appears, then it is divided, then the small result fades in.
        self.play(Write(a_moon[0]), Write(a_moon[1]), run_time=0.6)
        self.play(Write(a_moon[2]), run_time=0.7)
        self.play(Write(a_moon[3]), Write(a_moon[4]), run_time=0.7)
        self.wait(0.4)

        # Flash the punchline number 3600 in coral.
        flash3600 = SurroundingRectangle(a_moon[2], color=COLOR_CORAL,
                                         buff=0.06, stroke_width=2.5)
        self.play(Create(flash3600), a_moon[2].animate.set_color(COLOR_CORAL),
                  run_time=0.5)
        self.play(flash3600.animate.set_stroke(opacity=0.0), run_time=0.4)
        self.remove(flash3600)
        self.wait(0.6)

        # ── The click of recognition: 60² = 3600. ──
        self.play(FadeOut(a_seb), a_moon.animate.to_edge(UP, buff=1.4)
                  .set_opacity(0.4), FadeOut(diagram), run_time=0.8)

        eq = MathTex("60^2", "=", "3600", font_size=80).move_to(DOWN * 0.3)
        eq[0].set_color(COLOR_AMBER)   # 60²
        eq[1].set_color(COLOR_WHITE)   # =
        eq[2].set_color(COLOR_CORAL)   # 3600

        self.play(FadeIn(eq[0], shift=UP * 0.1), run_time=0.5)
        self.play(FadeIn(eq[1]), FadeIn(eq[2], shift=UP * 0.1), run_time=0.6)
        self.wait(0.3)
        # The exponent pulses gold — the whole point. (post: one ding)
        self.play(eq[0].animate.scale(1.25), run_time=0.4,
                  rate_func=rate_functions.there_and_back)
        self.wait(1.4)

        self._clear_to_grid()

    # ===================================================================== A4
    def act4_why_the_square(self):
        # ── The bulb metaphor → the canonical inverse-square tile diagram. ──
        # >>> EDIT: optional ~3s real footage here — a flashlight on a wall at
        #     30 / 60 / 120 cm, the bright circle spreading and dimming. Premiere
        #     cross-dissolve from that into this Manim build (tangible → abstract).
        S = np.array([-5.6, 0.0, 0.0])             # the point source
        source = VGroup(
            Dot(S, radius=0.34, color=COLOR_AMBER, fill_opacity=0.10,
                stroke_width=0),
            Dot(S, radius=0.20, color=COLOR_AMBER, fill_opacity=0.30,
                stroke_width=0),
            Dot(S, radius=0.11, color=COLOR_AMBER, fill_opacity=1.0,
                stroke_width=0),
        )
        self.play(FadeIn(source, scale=0.6), run_time=0.7)

        # A breath of "light leaving" — a couple of wavefronts spread and fade.
        for rad in (0.9, 1.7):
            ring = Circle(radius=0.05, color=COLOR_AMBER, stroke_width=2.5
                          ).move_to(S)
            self.add(ring)
            self.play(ring.animate.scale(rad / 0.05).set_stroke(opacity=0.0),
                      run_time=0.9, rate_func=rate_functions.ease_out_sine)
            self.remove(ring)

        # The honest geometry: ONE patch of light spread over an n×n grid.
        # n=1 → 1 cell, n=2 → 4 cells, n=3 → 9 cells. Side grows as the distance,
        # so AREA grows as the square — and per-cell brightness drops as 1/n².
        k = 0.50                                   # screen-units per "unit side"
        dists = [2.0, 4.5, 7.6]                    # frame distances from source
        cells_each = [1, 2, 3]
        bright = [0.90, 0.45, 0.25]                # per-cell brightness, dimming
        frames = VGroup()
        labels = VGroup()
        for d, n, b in zip(dists, cells_each, bright):
            cx = S[0] + d
            side = k * d
            cell = side / n
            patch = VGroup(*[
                Square(side_length=cell, stroke_color=COLOR_AMBER,
                       stroke_width=1.6, fill_color=COLOR_AMBER, fill_opacity=b
                       ).move_to([cx + (col - (n - 1) / 2) * cell,
                                  (row - (n - 1) / 2) * cell, 0])
                for row in range(n) for col in range(n)])
            frames.add(patch)
            lab = MathTex(rf"\tfrac{{1}}{{{n}}}", color=COLOR_WHITE,
                          font_size=34).next_to(patch, DOWN, buff=0.25)
            labels.add(lab)

        # Cone rays graze the outermost frame's top & bottom.
        top_o = frames[-1].get_top()
        bot_o = frames[-1].get_bottom()
        rays = VGroup(
            Line(S, top_o, color=COLOR_AMBER, stroke_width=1.4,
                 stroke_opacity=0.35),
            Line(S, bot_o, color=COLOR_AMBER, stroke_width=1.4,
                 stroke_opacity=0.35),
        )
        self.play(Create(rays), run_time=0.7)

        # Reveal the three frames in turn — watch the light thin out.
        for patch, lab in zip(frames, labels):
            self.play(FadeIn(patch, scale=0.85),
                      FadeIn(lab, shift=UP * 0.1),
                      run_time=0.7, rate_func=rate_functions.ease_out_cubic)
            self.wait(0.35)
        self.wait(0.6)

        # The pattern names itself: 1/1², 1/2², 1/3² — denominators squared, gold.
        new_labels = VGroup()
        for n, lab in zip(cells_each, labels):
            nl = MathTex(r"\tfrac{1}{%d^{2}}" % n, font_size=34
                         ).move_to(lab)
            nl[0][-1].set_color(COLOR_AMBER)   # the exponent pops gold
            new_labels.add(nl)
        self.play(LaggedStart(*[ReplacementTransform(o, n)
                                for o, n in zip(labels, new_labels)],
                              lag_ratio=0.2), run_time=1.2)
        self.wait(1.2)

        self._clear_to_grid()

    # ===================================================================== A5
    def act5_3d_geometry(self):
        # ── The real reason: it is the shape of space. 4πr². ──
        sphere = wire_sphere(1.6).move_to(LEFT * 2.4)
        area = MathTex(r"4\pi", "r", "^2", font_size=64).move_to(RIGHT * 3.0)
        area[1].set_color(COLOR_GREEN)
        area[2].set_color(COLOR_AMBER)

        self.play(GrowFromCenter(sphere), run_time=2.0,
                  rate_func=rate_functions.ease_out_sine)   # soap-bubble growth
        self.play(Write(area), run_time=0.9)
        self.play(VGroup(area[1], area[2]).animate.scale(1.25), run_time=0.5,
                  rate_func=rate_functions.there_and_back)   # r² pulses
        self.wait(0.8)
        self.play(FadeOut(sphere), FadeOut(area), run_time=0.6)

        # Three shells: area grows by the square. Same gravity, more skin.
        radii = [0.55, 1.0, 1.45]
        xs = [-4.3, 0.0, 4.3]
        areas = [r"4\pi\cdot 1^2", r"4\pi\cdot 4", r"4\pi\cdot 9"]
        shells = VGroup()
        slabs = VGroup()
        for R, x, a in zip(radii, xs, areas):
            s = wire_sphere(R, n_lat=3, n_lon=6).move_to([x, 0.4, 0])
            lab = MathTex(a, color=COLOR_WHITE, font_size=30
                          ).next_to(s, DOWN, buff=0.4)
            lab[0][-1].set_color(COLOR_AMBER)
            shells.add(s)
            slabs.add(lab)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in shells],
                              lag_ratio=0.25), run_time=1.8)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in slabs],
                              lag_ratio=0.2), run_time=1.0)
        self.wait(1.0)

        # ── Climax: the formula confesses its own geometry. ──
        self.play(
            FadeOut(slabs),
            FadeOut(shells[0]), FadeOut(shells[1]),
            shells[2].animate.scale(0.62).move_to(RIGHT * 3.4 + UP * 0.2)
                     .set_stroke(opacity=0.55),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine)

        formula = inv_sq_formula(fs=78).move_to(LEFT * 1.4 + UP * 0.2)
        self.play(Write(formula), run_time=1.4,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        brace = Brace(formula.den, DOWN).set_color(COLOR_AMBER)
        arrow = CurvedArrow(brace.get_bottom() + DOWN * 0.1,
                            shells[2].get_left() + LEFT * 0.05,
                            color=COLOR_AMBER, stroke_width=3, angle=-PI / 4)
        geo = Text("3D geometry", font=FONT, slant=ITALIC, color=COLOR_AMBER,
                   font_size=26).next_to(brace, DOWN, buff=0.2)
        self.play(GrowFromCenter(brace), FadeIn(geo, shift=DOWN * 0.1),
                  run_time=0.7)
        self.play(Create(arrow), run_time=0.7)
        self.play(VGroup(formula.r, formula.exp).animate.scale(1.18),
                  run_time=0.5, rate_func=rate_functions.there_and_back)
        self.wait(0.8)

        # Slow zoom-out, let the silence work. The 3B1B "earned wonder" beat.
        self.play(self.camera.frame.animate.scale(1.18), run_time=2.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(2.0)

        self._clear_to_grid()
