from manim import *
import numpy as np

# ── palette (verbatim from scene_1) ──
COLOR_BG        = "#0E1117"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_VEC_F     = "#FF3B30"   # red  — gravity / force
COLOR_VEC_V     = "#32ADE6"   # cyan — velocity (reserved; not used here)
COLOR_GREEN     = "#34C759"
COLOR_ACCEL     = COLOR_GREEN  # green — acceleration (semantic alias)
COLOR_AMBER     = "#FFCC00"   # amber — connector / time / the mass m
COLOR_BLUE_BALL = "#007AFF"
COLOR_ORANGE    = "#FF9500"
COLOR_DIM       = "#3A3F47"   # ghost / dead-zone stroke (from scene_0)

FONT = "Segoe UI"
config.background_color = COLOR_BG

RNG = np.random.default_rng(7)   # deterministic → stable render cache


# ============================================================================
#  HELPERS — same construction vocabulary as the rest of the series
# ============================================================================
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


def make_stone(radius=0.26):
    """Static, non-random irregular stone (frozen profile -> stable caching).
    Identical construction to scene_1 so the callback reads instantly."""
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
    spec_data = [(0.3 * radius, 1.2, 0.08 * radius),
                 (0.5 * radius, 3.5, 0.06 * radius),
                 (0.25 * radius, 5.0, 0.09 * radius)]
    for r, a, sr in spec_data:
        spec = Dot(point=np.array([r * np.cos(a), r * np.sin(a), 0]),
                   radius=sr, color="#3A3A3C")
        spec.set_fill("#3A3A3C", opacity=0.75)
        g.add(spec)
    return g


def ground_with_hatch(GY=-2.9):
    """Scene_1's ground line + diagonal hatch, returned as a single group."""
    ground = Line([-7, GY, 0], [7, GY, 0], color=COLOR_GROUND, stroke_width=3)
    hatch = VGroup(*[
        Line([x, GY, 0], [x - 0.28, GY - 0.28, 0], color=COLOR_GROUND,
             stroke_width=1.6, stroke_opacity=0.5)
        for x in np.arange(-6.6, 7.0, 0.5)])
    return ground, hatch


def down_arrow(top, length, color, sw=4):
    """Vertical (downward) arrow of an exact length — for F and a."""
    return Arrow(top, top + DOWN * length, buff=0, color=color, stroke_width=sw,
                 max_tip_length_to_length_ratio=0.32)


def inertia_meter(frac, full_w=1.9, h=0.16, color=COLOR_GROUND):
    """Horizontal bar whose fill is proportional to mass. The mapping is locked
    once (frac = mass / max_mass) so every act calls back to the same scale."""
    track = RoundedRectangle(width=full_w, height=h, corner_radius=h / 2,
                             stroke_color=color, stroke_width=1.6, fill_opacity=0)
    fill = RoundedRectangle(width=max(full_w * frac, h), height=h,
                            corner_radius=h / 2, stroke_width=0,
                            fill_color=color, fill_opacity=0.85)
    fill.align_to(track, LEFT)
    g = VGroup(track, fill)
    g.track, g.fill = track, fill
    return g


def dig_in_ticks(stone, n=3, color=COLOR_WHITE):
    """Braced-feet ticks under a stone resisting a push."""
    base = stone.get_bottom()
    g = VGroup()
    for i in range(n):
        x = base[0] + (i - (n - 1) / 2) * 0.18
        g.add(Line([x, base[1] - 0.02, 0], [x - 0.13, base[1] - 0.20, 0],
                   color=color, stroke_width=2, stroke_opacity=0.7))
    return g


def implode_burst(point, color, n=9, r=0.42):
    """Radial ticks at radius r — animate scaling to 0 about `point` to read
    as a Flash running BACKWARD (the landing un-happening)."""
    g = VGroup()
    for a in np.linspace(0, TAU, n, endpoint=False):
        d = np.array([np.cos(a), np.sin(a), 0])
        g.add(Line(point + d * r, point + d * (r + 0.16),
                   color=color, stroke_width=3))
    return g


def build_formula(fs=60):
    """F = GMm/r² assembled from individually addressable glyphs (from scene_0).
    Named handles let Act 6 grab single symbols (.m, .M, .G, .r, .exp, .bar)."""
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


# ============================================================================
class Scene_3_ForceProportionalToMass(MovingCameraScene):

    # ── locked geometry (shared by every act) ──
    GY      = -2.9          # ground line
    Y0      = 2.3           # drop height
    REST_C  = -2.9 + 0.30   # landed centre y (matches scene_1 exactly)
    BIG_X, SMALL_X = -2.2, 2.2
    METER_W = 1.9           # inertia-meter full width (the locked mass scale)
    FRAC_BIG, FRAC_SMALL = 1.0, 0.5   # mass 2:1 -> meter fill

    def construct(self):
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # The two stones are the spine — built ONCE, carried through every act.
        self.big   = make_stone(0.36)
        self.small = make_stone(0.24)

        self.act1_rewind()
        self.act2_inertia()
        self.act3_wrong_answer()
        self.act4_reality()
        self.act5_resolution()
        self.act6_law()

    # ===================================================================== A1
    def act1_rewind(self):
        # ── Wapas Galileo ke paas — scrub scene_1's ending backward. ──
        ground, hatch = ground_with_hatch(self.GY)
        self.add(ground, hatch)

        # Start in the LANDED state (the frame scene_1 left us on).
        self.big.move_to([self.BIG_X, self.REST_C, 0])
        self.small.move_to([self.SMALL_X, self.REST_C, 0])
        self.add(self.big, self.small)

        # 1) The two impact flashes run in reverse — ticks rush inward.
        burst_b = implode_burst([self.BIG_X, self.GY, 0], COLOR_GROUND)
        burst_s = implode_burst([self.SMALL_X, self.GY, 0], COLOR_GROUND)
        self.add(burst_b, burst_s)
        self.play(
            burst_b.animate.scale(0.02, about_point=[self.BIG_X, self.GY, 0]).set_opacity(0),
            burst_s.animate.scale(0.02, about_point=[self.SMALL_X, self.GY, 0]).set_opacity(0),
            run_time=0.5, rate_func=rate_functions.ease_in_cubic)   # rush-in = un-impact
        self.remove(burst_b, burst_s)

        # 2) Both stones lift back to height (reverse-whoosh easing).
        self.play(
            self.big.animate.move_to([self.BIG_X, self.Y0, 0]),
            self.small.animate.move_to([self.SMALL_X, self.Y0, 0]),
            run_time=1.4, rate_func=rate_functions.ease_in_out_sine)

        # 3) The dead-flat amber connector ghosts in, then fades — the motif we
        #    will be watching all episode. Flat, because they sit level.
        connector = DashedLine([self.BIG_X, self.Y0, 0], [self.SMALL_X, self.Y0, 0],
                               color=COLOR_AMBER, stroke_width=2.5, dash_length=0.12)
        self.play(FadeIn(connector), run_time=0.4)
        self.play(FadeOut(connector), run_time=0.5)

        # Hold — "we thought we were done with this; we weren't."
        self.wait(1.2)

        self._a1_ground, self._a1_hatch = ground, hatch

    # ===================================================================== A2
    def act2_inertia(self):
        # ── Ziddi patthar — kill gravity, study stubbornness alone. ──
        # Lift both into clean grid: big to the upper lane, small to the lower.
        BIG_LANE, SMALL_LANE = 0.9, -1.4
        START_X = -3.4
        self.play(
            FadeOut(self._a1_ground), FadeOut(self._a1_hatch),
            self.big.animate.move_to([START_X, BIG_LANE, 0]),
            self.small.animate.move_to([START_X, SMALL_LANE, 0]),
            run_time=1.3, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)

        # ── Push-test on the HEAVY stone: shove it, it digs in. ──
        push_b = Arrow([START_X - 1.7, BIG_LANE, 0],
                       self.big.get_left() + LEFT * 0.04,
                       buff=0, color=COLOR_WHITE, stroke_width=5,
                       max_tip_length_to_length_ratio=0.32)
        self.play(GrowArrow(push_b), run_time=0.45)
        ticks_b = dig_in_ticks(self.big)
        # Barely creeps + the arrow compresses (tail catches the tip) against it.
        self.play(
            self.big.animate.shift(RIGHT * 0.16),
            push_b.animate.put_start_and_end_on(
                [START_X - 1.7 + 0.32, BIG_LANE, 0], self.big.get_left() + RIGHT * 0.16),
            Create(ticks_b),
            run_time=0.55, rate_func=rate_functions.ease_out_cubic)
        # Defiant shake on "ziddi hai" — jitters, refuses to go further.
        for dx, rt in [(-0.05, 0.07), (0.05, 0.07), (-0.03, 0.06), (0.03, 0.06)]:
            self.play(self.big.animate.shift(RIGHT * dx), run_time=rt)
        self.wait(0.4)
        self.play(FadeOut(push_b), FadeOut(ticks_b), run_time=0.3)

        # ── Identical push on the LIGHT stone: it shoots off. ──
        push_s = Arrow([START_X - 1.7, SMALL_LANE, 0],
                       self.small.get_left() + LEFT * 0.04,
                       buff=0, color=COLOR_WHITE, stroke_width=5,
                       max_tip_length_to_length_ratio=0.32)
        self.play(GrowArrow(push_s), run_time=0.45)
        self.play(
            self.small.animate.shift(RIGHT * 3.0),
            push_s.animate.shift(RIGHT * 1.0).set_opacity(0),
            run_time=0.55, rate_func=rate_functions.ease_out_quad)  # whoosh — light flies
        self.remove(push_s)
        self.wait(0.3)

        # Same push, wildly different response. That contrast IS a = F/m.
        # ── Inertia meters: lock the mass mapping the rest of the episode reuses.
        self.play(
            self.big.animate.move_to([self.BIG_X, 0.45, 0]),
            self.small.animate.move_to([self.SMALL_X, 0.45, 0]),
            run_time=0.9, rate_func=rate_functions.ease_in_out_sine)

        meter_b = inertia_meter(self.FRAC_BIG, self.METER_W).next_to(self.big, DOWN, buff=0.5)
        meter_s = inertia_meter(self.FRAC_SMALL, self.METER_W).next_to(self.small, DOWN, buff=0.5)
        cap = Text("more mass  →  more inertia", font=FONT, slant=ITALIC,
                   color=COLOR_GROUND, font_size=24).next_to(VGroup(meter_b, meter_s), DOWN, buff=0.6)
        self.play(
            LaggedStart(
                Create(meter_b.track), Create(meter_s.track), lag_ratio=0.2),
            run_time=0.6)
        self.play(
            GrowFromEdge(meter_b.fill, LEFT), GrowFromEdge(meter_s.fill, LEFT),
            run_time=0.7, rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(cap, shift=UP * 0.1), run_time=0.5)
        self.wait(1.0)

        # >>> EDIT: optional ~2s real-footage cut-in here — loaded trolley vs
        #     empty trolley, locked-off side-by-side. The bodily "it won't move"
        #     sells stubbornness harder than any arrow. Held beat below for it.
        self.wait(0.5)

        self.play(FadeOut(meter_b), FadeOut(meter_s), FadeOut(cap), run_time=0.6)

    # ===================================================================== A3
    def act3_wrong_answer(self):
        # ── Agar same force ho toh… — build the believable wrong answer. ──
        ground, hatch = ground_with_hatch(self.GY)
        self.play(
            FadeIn(ground), FadeIn(hatch),
            self.big.animate.move_to([self.BIG_X, self.Y0, 0]),
            self.small.animate.move_to([self.SMALL_X, self.Y0, 0]),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine)

        # Mark the whole frame as a GUESS: a dashed hypothesis box + label.
        hypo = DashedVMobject(
            RoundedRectangle(width=12.6, height=6.7, corner_radius=0.2,
                             stroke_color=COLOR_GROUND, stroke_width=2),
            num_dashes=120)
        hypo.set_stroke(opacity=0.55)
        label = Text("IF :  same force", font=FONT, slant=ITALIC,
                     color=COLOR_GROUND, font_size=26)
        label.next_to(hypo.get_top(), DOWN, buff=0.18)
        self.play(Create(hypo), FadeIn(label), run_time=0.9)

        # The "quiet red plant" from scene_1 cashes in: identical red F arrows.
        gF_b = down_arrow(self.big.get_bottom() + DOWN * 0.06, 0.72, COLOR_VEC_F)
        gF_s = down_arrow(self.small.get_bottom() + DOWN * 0.06, 0.72, COLOR_VEC_F)
        self.play(GrowArrow(gF_b), GrowArrow(gF_s), run_time=0.5)
        self.wait(0.4)

        # Inertia meters return (callback) — and they differ.
        meter_b = inertia_meter(self.FRAC_BIG, 1.4).next_to(self.big, LEFT, buff=0.35)
        meter_s = inertia_meter(self.FRAC_SMALL, 1.4).next_to(self.small, RIGHT, buff=0.35)
        self.play(GrowFromEdge(meter_b.fill, LEFT), Create(meter_b.track),
                  GrowFromEdge(meter_s.fill, LEFT), Create(meter_s.track),
                  run_time=0.7)

        # Same F, different mass -> different acceleration. Green = accel.
        # Heavy gets a SHORT green arrow, light a LONG one.
        aG_b = down_arrow(self.big.get_right() + RIGHT * 0.25 + UP * 0.1, 0.42,
                          COLOR_ACCEL, sw=4)
        aG_s = down_arrow(self.small.get_left() + LEFT * 0.25 + UP * 0.1, 0.95,
                          COLOR_ACCEL, sw=4)
        self.play(GrowArrow(aG_b), GrowArrow(aG_s), run_time=0.6)
        self.wait(0.8)

        # Clear the scaffolding; keep the IF-frame. Now run the drop UNDER this
        # (wrong) rule — light accelerates harder and lands first.
        self.play(*[FadeOut(m) for m in (gF_b, gF_s, aG_b, aG_s, meter_b, meter_s)],
                  run_time=0.5)

        fall = self.Y0 - self.REST_C
        T_LIGHT = 1.4
        a_light = 2 * fall / T_LIGHT ** 2          # light reaches the ground at T
        a_heavy = a_light * 0.56                    # heavy lags badly (still aloft)

        def y_light(t): return max(self.Y0 - 0.5 * a_light * t * t, self.REST_C)
        def y_heavy(t): return max(self.Y0 - 0.5 * a_heavy * t * t, self.REST_C)

        t = ValueTracker(0.0)
        self.big.add_updater(lambda m: m.move_to([self.BIG_X, y_heavy(t.get_value()), 0]))
        self.small.add_updater(lambda m: m.move_to([self.SMALL_X, y_light(t.get_value()), 0]))

        # The lie-detector: connector between centres — it will TILT.
        connector = always_redraw(lambda: DashedLine(
            self.big.get_center(), self.small.get_center(),
            color=COLOR_AMBER, stroke_width=2.5, dash_length=0.12))
        self.add(connector)

        # Strobe afterimages — the light stamps spread apart faster.
        stamps = VGroup()
        last = 0.0
        for tp in [0.5, 0.9, 1.2]:
            self.play(t.animate.set_value(tp), run_time=(tp - last), rate_func=linear)
            stamps.add(
                Dot([self.BIG_X, y_heavy(tp), 0], radius=0.05, color=COLOR_WHITE,
                    fill_opacity=0.22, stroke_width=0),
                Dot([self.SMALL_X, y_light(tp), 0], radius=0.05, color=COLOR_WHITE,
                    fill_opacity=0.22, stroke_width=0))
            self.add(stamps)
            last = tp
        self.play(t.animate.set_value(T_LIGHT), run_time=(T_LIGHT - last), rate_func=linear)

        # Light lands; heavy frozen mid-air. The connector is now tilted = doubt.
        self.big.clear_updaters()
        self.small.clear_updaters()
        self.remove(connector)
        tilted = DashedLine(self.big.get_center(), self.small.get_center(),
                            color=COLOR_AMBER, stroke_width=2.5, dash_length=0.12)
        self.add(tilted)
        self.play(Flash([self.SMALL_X, self.GY, 0], color=COLOR_GROUND,
                        line_length=0.16, num_lines=8, flash_radius=0.34),
                  run_time=0.45)
        self.wait(1.0)   # let the wrongness sit — a held, unresolved breath

        # Hand state to Act 4.
        self._a3 = dict(ground=ground, hatch=hatch, hypo=hypo, label=label,
                        tilted=tilted, stamps=stamps, gF_b=gF_b, gF_s=gF_s)

    # ===================================================================== A4
    def act4_reality(self):
        s = self._a3
        # Hard cut on "nahi!" — a beat of pure silence.
        self.wait(0.5)

        # Freeze the prediction and ghost it down to dim — but KEEP it on screen.
        ghost = s["tilted"].copy().set_color(COLOR_DIM).set_stroke(opacity=0.55)
        self.play(Transform(s["tilted"], ghost), run_time=0.6)

        # Reset both stones to height to replay the REAL drop over the ghost.
        self.play(
            self.big.animate.move_to([self.BIG_X, self.Y0, 0]),
            self.small.animate.move_to([self.SMALL_X, self.Y0, 0]),
            FadeOut(s["stamps"]),
            FadeOut(ghost),
            run_time=0.6, rate_func=rate_functions.ease_in_out_sine)

        # Real drop: ONE acceleration for both. They fall together.
        fall = self.Y0 - self.REST_C
        T_REAL = 1.3
        a_real = 2 * fall / T_REAL ** 2

        def y_real(t): return max(self.Y0 - 0.5 * a_real * t * t, self.REST_C)

        t = ValueTracker(0.0)
        self.big.add_updater(lambda m: m.move_to([self.BIG_X, y_real(t.get_value()), 0]))
        self.small.add_updater(lambda m: m.move_to([self.SMALL_X, y_real(t.get_value()), 0]))
        flat_live = always_redraw(lambda: DashedLine(
            self.big.get_center(), self.small.get_center(),
            color=COLOR_AMBER, stroke_width=2.5, dash_length=0.12))
        self.add(flat_live)
        self.play(t.animate.set_value(T_REAL), run_time=1.1, rate_func=linear)

        self.big.clear_updaters()
        self.small.clear_updaters()
        self.remove(flat_live)

        # The flat reality SLAMS over the dim tilted ghost — prediction vs truth.
        flat = DashedLine(self.big.get_center(), self.small.get_center(),
                          color=COLOR_AMBER, stroke_width=3.0, dash_length=0.12)
        self.play(
            Create(flat),
            Flash([self.BIG_X, self.GY, 0], color=COLOR_GROUND,
                  line_length=0.18, num_lines=8, flash_radius=0.4),
            Flash([self.SMALL_X, self.GY, 0], color=COLOR_GROUND,
                  line_length=0.16, num_lines=8, flash_radius=0.34),
            run_time=0.5)
        self.wait(0.8)

        # >>> EDIT: cut to ~3s real footage right here — Apollo 15 hammer+feather
        #     (or Brian Cox vacuum chamber). Grainy reality landing together hits
        #     like a thunderclap, then snap back to Manim. Held beat below.
        self.wait(0.6)


        
        self.play(
            FadeOut(s["hypo"]), FadeOut(s["label"]), FadeOut(s["tilted"]), FadeOut(ghost),
            run_time=0.8)

        # Truth left glowing: stones landed together, flat connector pulses.
        self.play(flat.animate.set_stroke(width=4.0, opacity=1.0), run_time=0.3)
        self.play(flat.animate.set_stroke(width=3.0), run_time=0.3)
        self.wait(0.8)

        self._a4 = dict(ground=s["ground"], hatch=s["hatch"], flat=flat)

    # ===================================================================== A5
    def act5_resolution(self):
        s = self._a4
        # ── Gravity zyada zor se kheench rahi hai — resolve, then cancel. ──
        # Clear the ground/connector; lift the pair to mid-air and FREEZE them
        # falling (acceleration is the fixed fact now).
        MID = 0.7
        self.play(
            FadeOut(s["ground"]), FadeOut(s["hatch"]), FadeOut(s["flat"]),
            self.big.animate.move_to([self.BIG_X, MID, 0]),
            self.small.animate.move_to([self.SMALL_X, MID, 0]),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine)

        # Fact: they fall together -> equal green acceleration arrows.
        aG_b = down_arrow(self.big.get_right() + RIGHT * 0.3, 0.8, COLOR_ACCEL)
        aG_s = down_arrow(self.small.get_left() + LEFT * 0.3, 0.8, COLOR_ACCEL)
        a_lab = Text("same acceleration", font=FONT, slant=ITALIC,
                     color=COLOR_ACCEL, font_size=22)
        a_lab.next_to(VGroup(aG_b, aG_s), DOWN, buff=0.25).shift(UP*0.1)
        self.play(GrowArrow(aG_b), GrowArrow(aG_s), run_time=0.5)
        self.play(FadeIn(a_lab, shift=UP * 0.1), run_time=0.4)
        self.wait(0.5)
        
        # Heavy force doubles (mass ×2 ⇒ pull ×2); acceleration arrow unchanged.
        big_F_target = Arrow(self.big.get_top() + UP * 0.06,
                             self.big.get_top() + UP * 1.26, buff=0,
                             color=COLOR_VEC_F, stroke_width=4,
                             max_tip_length_to_length_ratio=0.32)
        
        self.wait()

        # Sweep the stage for the centrepiece.
        stage = VGroup(self.big, self.small, aG_b, aG_s, a_lab)
        self.play(FadeOut(stage, shift=DOWN * 0.3), run_time=0.8)
        
        self.wait(0.4)

    # ===================================================================== A6
    def act6_law(self):
        # ── Force ∝ mass — the law, then the hook. ──
        # Stepped proof: stone + red arrow; ×2 mass -> ×2 arrow; ×3 -> ×3.
        axes_o = np.array([-4.2, -2.2, 0])      # graph origin
        x_axis = Arrow(axes_o, axes_o + RIGHT * 7.2, buff=0, color=COLOR_GROUND,
                       stroke_width=2.5, max_tip_length_to_length_ratio=0.03)
        y_axis = Arrow(axes_o, axes_o + UP * 5.0, buff=0, color=COLOR_GROUND,
                       stroke_width=2.5, max_tip_length_to_length_ratio=0.04)
        x_lab = Text("mass", font=FONT, color=COLOR_GROUND, font_size=22).next_to(x_axis, RIGHT, buff=0.15)
        y_lab = Text("force", font=FONT, color=COLOR_VEC_F, font_size=22).next_to(y_axis, UP, buff=0.12)
        self.play(Create(x_axis), Create(y_axis), FadeIn(x_lab), FadeIn(y_lab),
                  run_time=0.8)

        dx, dy = 1.7, 1.15           # graph units -> screen units
        pts = []
        dots = VGroup()
        for k in (1, 2, 3):
            # tip must land exactly on the line through axes_o with slope dy/dx
            tip = np.array([axes_o[0] + dx * k, axes_o[1] + dy * k, 0])
            # stone sits just below the x-axis tick; arrow rises from x-axis up to tip
            base = np.array([axes_o[0] + dx * k, axes_o[1] + 0.25, 0])
            stone = make_stone(0.18 + 0.05 * k)
            stone.move_to(base)
            arr = Arrow(base + UP * 0.18, tip, buff=0,
                        color=COLOR_VEC_F, stroke_width=4,
                        max_tip_length_to_length_ratio=0.16)
            self.play(FadeIn(stone, shift=UP * 0.1), GrowArrow(arr),
                      run_time=0.5, rate_func=rate_functions.ease_out_cubic)
            self.wait(0.25)
            dot = Dot(tip, radius=0.07, color=COLOR_VEC_F)
            pts.append(tip)
            dots.add(dot)
            # the arrow-tip lifts off as a data point; stone+shaft fade
            self.play(FadeIn(dot, scale=0.5),
                      FadeOut(stone), FadeOut(arr), run_time=0.4)

        # The unmistakable signature: a straight line through the origin.
        line = Line(axes_o, pts[-1] + (pts[-1] - axes_o) * 0.12,
                    color=COLOR_WHITE, stroke_width=3)
        self.play(Create(line), run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
        prop = MathTex(r"F \propto m", font_size=52, color=COLOR_WHITE)
        prop.next_to(pts[1], UL, buff=0.3)
        self.play(Write(prop), run_time=0.6)
        word = Text("PROPORTIONAL", font=FONT, color=COLOR_AMBER, font_size=30,
                    weight=BOLD).to_edge(UP, buff=0.7)
        self.play(FadeIn(word, scale=1.1), run_time=0.5)
        self.wait(1.0)

        graph = VGroup(x_axis, y_axis, x_lab, y_lab, dots, line, prop, word)
        self.play(FadeOut(graph, shift=DOWN * 0.2), run_time=0.8)

        # ── Reconnect to the series spine: F = GMm/r². ──
        formula = build_formula(fs=64).move_to(ORIGIN)
        self.play(Write(formula), run_time=1.4, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        # Pulse the m — the one symbol we just earned.
        self.play(formula.m.animate.set_color(COLOR_AMBER).scale(1.3), run_time=0.5)
        self.play(formula.m.animate.scale(1 / 1.3 * 1.18), run_time=0.3)  # settle a touch big

        # The rest ghosts into the dark — "still coming."
        rest = VGroup(formula.F, formula.eq, formula.G, formula.M,
                      formula.r, formula.exp, formula.bar)
        self.play(rest.animate.set_color(COLOR_DIM).set_opacity(0.45), run_time=0.8)

        # Symmetry knocks: M (the OTHER mass) gives one faint pulse, then settles.
        self.play(formula.M.animate.set_color(COLOR_BLUE_BALL).set_opacity(0.7),
                  run_time=0.3)
        self.play(formula.M.animate.set_color(COLOR_DIM).set_opacity(0.45),
                  run_time=0.5)

        # Push in on the lonely glowing m and hold the tease.
        self.play(self.camera.frame.animate.scale(0.7).move_to(formula.m),
                  formula.m.animate.set_color(COLOR_AMBER),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.5)
