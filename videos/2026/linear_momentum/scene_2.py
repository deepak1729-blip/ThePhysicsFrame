from manim import *
import numpy as np

# ── BRAND PALETTE (series canvas, verbatim) ──
COLOR_BG     = "#0E1117"   # kept from scene_1 (brief said #0E0E10 — flagged)
COLOR_GROUND = "#8E8E93"
COLOR_WHITE  = "#E5E5EA"
COLOR_DIM    = "#3A3F47"

# ── MOMENTUM SERIES COLOR PROTOCOL (locked for Scenes 2–7) ──
COLOR_CUE      = "#E5E5EA"   # cue ball A (scene_1)
COLOR_TARGET   = "#FF5A5F"   # target ball B (scene_1)
COLOR_MASS     = "#F4B642"   # mass m — warm amber/gold
COLOR_VEL      = "#3FC8FF"   # velocity v — electric cyan, ALWAYS an arrow
COLOR_MOMENTUM = "#C66BFF"   # p = mv — debuts Scene 3; one subliminal pulse here
COLOR_ENERGY   = "#5FE38B"   # RESERVED for Scene 6 — not used in this file
COLOR_TICK     = "#34C759"   # series confirmation green (≠ energy green)
COLOR_RED      = "#FF3B30"   # series UI red — the INCOMPLETE stamp

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
            t = (i + 0.5) / N
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


def make_pool_ball(color, radius=0.28):
    """Top-down ball: base disc + sheen + specular (scene_1 vocabulary)."""
    g = VGroup()
    sphere = Circle(radius=radius)
    sphere.set_fill(color, opacity=1.0)
    sphere.set_sheen(-0.40, DR)
    sphere.set_stroke(color=COLOR_WHITE, width=1.4, opacity=0.18)
    g.add(sphere)
    rim = Circle(radius=radius)
    rim.set_fill(opacity=0)
    rim.set_stroke(color=color, width=2.6, opacity=0.45)
    g.add(rim)
    spec = Ellipse(width=radius * 0.50, height=radius * 0.32)
    spec.set_fill(COLOR_WHITE, opacity=0.62)
    spec.set_stroke(width=0)
    spec.move_to(np.array([-radius * 0.28, radius * 0.30, 0]))
    spec.rotate(-20 * DEGREES)
    g.add(spec)
    return g


def impact_ring(point, color=COLOR_WHITE, r0=0.06, sw=3.5):
    return Circle(radius=r0, color=color, stroke_width=sw,
                  fill_opacity=0).move_to(point).set_z_index(6)


def check_mark(color=COLOR_TICK, scale=0.6):
    m = VMobject(stroke_color=color, stroke_width=6)
    m.set_points_as_corners([
        LEFT * 0.18 + DOWN * 0.02, DOWN * 0.20, RIGHT * 0.30 + UP * 0.26,
    ])
    return m.scale(scale)


def safe_table(width=12.4):
    """table.png with a drawn-slate fallback (series asset-free convention)."""
    try:
        img = ImageMobject("table.png")
        img.set(width=width)
        return img
    except Exception:
        slab = RoundedRectangle(width=width, height=width * 0.52,
                                corner_radius=0.3, stroke_color="#5A4632",
                                stroke_width=10, fill_color="#1C3A2A",
                                fill_opacity=1.0)
        return Group(slab)


def safe_stick(tip_point, length=2.8):
    """stick.png sized with its tip at tip_point; tapered-polygon fallback."""
    try:
        stick = ImageMobject("stick.png")
        stick.set(width=length)
        stick.move_to(tip_point + LEFT * (length / 2))
        return stick
    except Exception:
        butt = tip_point + LEFT * length
        poly = Polygon(tip_point + UP * 0.025, tip_point + DOWN * 0.025,
                       butt + DOWN * 0.07, butt + UP * 0.07,
                       stroke_width=0, fill_color="#B08D57", fill_opacity=1.0)
        return Group(poly)


def make_gauge(label_text, color=COLOR_GROUND, decimals=1, w=1.85, h=0.92):
    """A churning readout: pill + small label + DecimalNumber, with handles."""
    box = RoundedRectangle(width=w, height=h, corner_radius=0.16,
                           stroke_color=color, stroke_width=1.5,
                           stroke_opacity=0.6,
                           fill_color="#11151C", fill_opacity=0.92)
    lab = Text(label_text, font=FONT, font_size=15, color=color)
    lab.move_to(box.get_top() + DOWN * 0.25)
    val = DecimalNumber(0, num_decimal_places=decimals, font_size=30,
                        color=COLOR_WHITE)
    val.move_to(box.get_center() + DOWN * 0.15)
    g = VGroup(box, lab, val)
    g.box, g.lab, g.val = box, lab, val
    return g


def make_car():
    img = ImageMobject("car.png")
    img.set(width=3.0)
    return img


def label_pill(mobj, buff=0.16, stroke=COLOR_GROUND):
    return RoundedRectangle(
        corner_radius=0.14, width=mobj.width + buff * 2.4,
        height=mobj.height + buff * 1.6,
        stroke_color=stroke, stroke_width=1.2, stroke_opacity=0.45,
        fill_color="#11151C", fill_opacity=0.92,
    ).move_to(mobj.get_center())


# ═══════════════════════════════════════════════════════════════════════════
class Scene_2_WhatHoldsStill(MovingCameraScene):

    # ── locked geometry (inherited from scene_1 where shared) ──
    R         = 0.28
    TABLE_Y   = -0.35
    CUE_START = np.array([-4.6, -0.35, 0.0])
    TARGET_0  = np.array([0.2, -0.35, 0.0])
    TOKEN_POS = np.array([0.0, 2.65, 0.0])     # the Σ-token pin, Acts 2–3
    BALL_A2   = np.array([-2.8, -0.6, 0.0])    # Act-2 collision lane
    BALL_B2   = np.array([1.6, -0.6, 0.0])

    def construct(self):
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        self.act0_inherit_scene1()
        self.act1_the_hunt()
        self.act2_candidate_mass()
        self.act3_mass_says_nothing()
        self.act4_speed_matters()

    def _clear_to_grid(self, run_time=0.9, keep=()):
        clear = Group(*[m for m in self.mobjects
                        if m is not self.grid and m not in keep])
        if len(clear):
            self.play(FadeOut(clear), run_time=run_time,
                      rate_func=rate_functions.ease_in_out_sine)

    # ===================================================================== A0
    def act0_inherit_scene1(self):
        # Hard-cut continuity: rebuild scene_1's exact closing frame —
        # table, both balls, re-cocked stick, the held question. No entrance.
        cushion = safe_table(12.4)
        cushion.set_z_index(-6)
        cue    = make_pool_ball(COLOR_CUE, self.R).move_to(self.CUE_START)
        target = make_pool_ball(COLOR_TARGET, self.R).move_to(self.TARGET_0)
        cue.set_z_index(5)
        target.set_z_index(5)
        tip_ready = self.CUE_START + LEFT * (self.R + 0.45)
        stick = safe_stick(tip_ready)
        stick.set_z_index(5)
        stick.shift(LEFT * 0.18)                       # scene_1's re-cock offset
        title = Text("What stays constant?", font=FONT, font_size=50,
                     color=COLOR_WHITE, weight=BOLD)
        title.move_to(UP * 2.25).set_z_index(10)

        self.add(cushion, cue, target, stick, title)
        self.cue, self.target = cue, target
        self.wait()                                 # the inherited tension

        # The world peels away; only the two characters survive the dissolve.
        self.play(
            FadeOut(title, shift=UP * 0.2),
            FadeOut(target, shift=UP * 0.2),
            FadeOut(stick, shift=LEFT * 0.5),
            cushion.animate.set_opacity(0.0),
            run_time=0.3, rate_func=rate_functions.ease_in_out_sine,
        )
        self.remove(cushion)

    # ===================================================================== A1
    def act1_the_hunt(self):
        cue = self.cue

        # The coral ball waits backstage; the cue ball BECOMES the first demo.
        self.play(
            cue.animate.move_to([-3.1, 2.35, 0]),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )

        # ── live gauges ──
        g_h  = make_gauge("height", COLOR_GROUND).move_to([-5.55, 0.95, 0])
        g_v  = make_gauge("speed", COLOR_GROUND).move_to([-5.55, -0.45, 0])
        amb1 = make_gauge("position", COLOR_GROUND).move_to([-5.55, 2.35, 0])
        gauges = VGroup(g_h, g_v, amb1)
        for g in gauges:
            g.set_z_index(4)

        self.play(LaggedStart(*[FadeIn(g, scale=0.92) for g in gauges],
                              lag_ratio=0.10),
                  run_time=1.0, rate_func=rate_functions.ease_out_cubic)

        # global clock for the ambient churn
        clock = ValueTracker(0.0)
        driver = Mobject()
        driver.add_updater(lambda m, dt: clock.increment_value(dt))
        self.add(driver)

        def churn(g, base, amp, freq, ph, dec_anchor=DOWN * 0.15):
            anchor = g.box.get_center() + dec_anchor
            g.val.add_updater(
                lambda m: m.set_value(
                    base + amp * np.sin(freq * clock.get_value() + ph)
                ).move_to(anchor)).set_color(COLOR_WHITE)

        churn(amb1, 12.0, 6.0, 3.1, 0.4)

        # ── event 1 · the parabola drop (cue ball, real projectile y(t)) ──
        X0, Y0, VX, GA, T_FL = -3.1, 2.35, 1.85, 2.70, 1.85
        t1 = ValueTracker(0.0)
        cue.add_updater(lambda m: m.move_to([
            X0 + VX * t1.get_value(),
            Y0 - 0.5 * GA * t1.get_value() ** 2, 0]))
        h_anchor = g_h.box.get_center() + DOWN * 0.15
        v_anchor = g_v.box.get_center() + DOWN * 0.15
        g_h.val.add_updater(lambda m: m.set_value(
            max((Y0 - 0.5 * GA * t1.get_value() ** 2) + 2.27, 0.0) * 2.0
        ).move_to(h_anchor).set_color(COLOR_WHITE))
        g_v.val.add_updater(lambda m: m.set_value(
            float(np.hypot(VX, GA * t1.get_value())) * 8.0
        ).move_to(v_anchor).set_color(COLOR_WHITE))

        drop_trail = TracedPath(cue.get_center, stroke_color=COLOR_WHITE,
                                stroke_width=2.2, stroke_opacity=0.30,
                                dissipating_time=0.8).set_z_index(2)
        self.add(drop_trail)
        # gravity's own easing IS t² — the tracker runs linear on purpose
        self.play(t1.animate.set_value(T_FL), run_time=T_FL, rate_func=linear)
        cue.clear_updaters()
        self.remove(drop_trail)

        self.play(
            FadeOut(cue), FadeOut(g_h), FadeOut(g_v), FadeOut(amb1),
            run_time=0.3
        )

        # ── event 2 · the car drains to zero ──
        road = Line([-6.0, -2.45, 0], [6.0, -2.45, 0], color=COLOR_GROUND,
                    stroke_width=2, stroke_opacity=0.4)
        car = make_car().move_to([-5.3, -1.875, 0]).set_z_index(4)
        self.play(Create(road), FadeIn(car, shift=RIGHT * 0.2), run_time=0.6)

        car_v = ValueTracker(64.0)
        self.play(
            car.animate(rate_func=rate_functions.ease_out_quad)
               .shift(RIGHT * 8.0),
            car_v.animate(rate_func=linear).set_value(0.0)
        )
        self.wait(0.5)

        # ── THE FREEZE · everything stops; the hunt begins ──
        driver.clear_updaters()
        for g in gauges:
            g.val.clear_updaters()

        vignette = Rectangle(width=30, height=18, fill_color=COLOR_BG,
                             fill_opacity=0.0, stroke_width=0).set_z_index(7)
        self.add(vignette)

        montage = Group(road, car)
        qmark = MathTex("?", font_size=130, color=COLOR_WHITE).set_z_index(10)

        # POST: the drone resolves to near-silence on this exact cut.
        self.play(
            montage.animate.set_opacity(0.22),
            vignette.animate.set_opacity(0.62),
            run_time=0.9, rate_func=rate_functions.ease_in_out_sine,
        )
        self.play(FadeIn(qmark, scale=0.6),
                  run_time=0.8, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)                                  # let the question breathe

        # ── the prediction graph: only the flat thing projects forward ──
        self.play(FadeOut(montage),
                  vignette.animate.set_opacity(0.0),
                  qmark.animate.scale(0.42).move_to([5.05, 1.55, 0]),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
        self.remove(vignette)

        O = np.array([-4.6, -1.7, 0.0])
        NOW_DX, END_DX = 4.4, 8.6
        x_ax = Arrow(O, O + RIGHT * (END_DX + 0.5), buff=0, color=COLOR_GROUND,
                     stroke_width=2.4, max_tip_length_to_length_ratio=0.025)
        y_ax = Arrow(O, O + UP * 3.7, buff=0, color=COLOR_GROUND,
                     stroke_width=2.4, max_tip_length_to_length_ratio=0.06)
        t_lab = Text("time", font=FONT, font_size=20, color=COLOR_GROUND
                     ).next_to(x_ax.get_end(), DOWN, buff=0.18)
        self.play(Create(x_ax), Create(y_ax), FadeIn(t_lab), run_time=0.8)

        def jitter_curve(y_base, drift, amp):
            xs = np.linspace(0.15, NOW_DX, 26)
            pts = [O + RIGHT * x
                   + UP * (y_base + drift * x / NOW_DX
                           + amp * float(RNG.uniform(-1, 1)))
                   for x in xs]
            v = VMobject(stroke_color=COLOR_GROUND, stroke_width=2.2,
                         stroke_opacity=0.55)
            v.set_points_smoothly(pts)
            return v

        c1 = jitter_curve(2.9, -2.1, 0.16)     # the draining quantity
        c2 = jitter_curve(0.9, 1.1, 0.22)      # the wandering quantity
        flat_y = 2.0
        flat = Line(O + RIGHT * 0.15 + UP * flat_y, O + RIGHT * NOW_DX + UP * flat_y,
                    color=COLOR_WHITE, stroke_width=3.5)
        flat_glow = flat.copy().set_stroke(width=10, opacity=0.10)

        self.play(Create(c1), Create(c2), run_time=1.3,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(Create(flat_glow), Create(flat), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        # the "now" seam + the shaded future
        now_line = DashedLine(O + RIGHT * NOW_DX + DOWN * 0.1,
                              O + RIGHT * NOW_DX + UP * 3.5,
                              color=COLOR_WHITE, stroke_width=1.6,
                              stroke_opacity=0.4, dash_length=0.10)
        future = Rectangle(width=END_DX - NOW_DX, height=3.5, stroke_width=0,
                           fill_color=COLOR_WHITE, fill_opacity=0.045)
        future.move_to(O + RIGHT * (NOW_DX + (END_DX - NOW_DX) / 2) + UP * 1.75)
        fut_lab = Text("future", font=FONT, slant=ITALIC, font_size=20,
                       color=COLOR_GROUND).move_to(future.get_bottom() + UP * 0.3)
        self.play(Create(now_line), FadeIn(future), FadeIn(fut_lab),
                  run_time=0.8)

        # only the flat line crosses the seam — and it lands ON the question.
        ext = DashedLine(O + RIGHT * NOW_DX + UP * flat_y,
                         O + RIGHT * (END_DX - 0.9) + UP * flat_y,
                         color=COLOR_WHITE, stroke_width=3, dash_length=0.14)
        ext_tip = Arrow(O + RIGHT * (END_DX - 0.9) + UP * flat_y,
                        O + RIGHT * (END_DX - 0.35) + UP * flat_y,
                        buff=0, color=COLOR_WHITE, stroke_width=3,
                        max_tip_length_to_length_ratio=0.9)
        q_target = O + RIGHT * (END_DX - 0.35) + UP * (flat_y + 0.55)
        self.play(Create(ext), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(GrowArrow(ext_tip),
                  qmark.animate.move_to(q_target),
                  run_time=0.7, rate_func=rate_functions.ease_out_cubic)
        self.play(qmark.animate.scale(1.18), run_time=0.5,
                  rate_func=rate_functions.there_and_back)
        self.wait()                                   # hold this frame

        self._clear_to_grid(run_time=1.0)

    # ===================================================================== A2
    def act2_candidate_mass(self):
        # The pair returns — same two characters, clean stage, calm camera.
        cue    = make_pool_ball(COLOR_CUE, self.R).move_to(self.BALL_A2)
        target = make_pool_ball(COLOR_TARGET, self.R).move_to(self.BALL_B2)
        cue.set_z_index(5)
        target.set_z_index(5)
        self.cue, self.target = cue, target
        self.play(LaggedStart(FadeIn(cue, scale=0.85),
                              FadeIn(target, scale=0.85), lag_ratio=0.2),
                  run_time=0.8, rate_func=rate_functions.ease_out_cubic)

        lab_a = MathTex(r"0.5\ \text{kg}", font_size=34, color=COLOR_MASS
                        ).next_to(cue, DOWN, buff=0.32)
        lab_b = MathTex(r"0.5\ \text{kg}", font_size=34, color=COLOR_MASS
                        ).next_to(target, DOWN, buff=0.32)
        self.play(FadeIn(lab_a, shift=UP * 0.1), FadeIn(lab_b, shift=UP * 0.1),
                  run_time=0.6)
        self.wait(0.5)

        # Magic-move: the two labels travel up and FUSE into the Σ-token.
        token = MathTex(r"\Sigma\ \text{mass} \,=\, 1.0\ \text{kg}",
                        font_size=44, color=COLOR_MASS).move_to(self.TOKEN_POS)
        token.set_z_index(10)
        token_glow = RoundedRectangle(
            width=token.width + 0.7, height=token.height + 0.5,
            corner_radius=0.22, stroke_width=0,
            fill_color=COLOR_MASS, fill_opacity=0.09,
        ).move_to(self.TOKEN_POS).set_z_index(9)
        underline = Line(token.get_corner(DL) + DOWN * 0.16,
                         token.get_corner(DR) + DOWN * 0.16,
                         color=COLOR_MASS, stroke_width=2).set_z_index(10)

        ca, cb = lab_a.copy(), lab_b.copy()
        self.play(
            ReplacementTransform(VGroup(ca, cb), token),
            FadeIn(token_glow),
            run_time=1.1, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(Create(underline), run_time=0.4)
        self.wait(0.5)

        # The collision plays UNDER the pinned total. The total does not flinch.
        contact = self.BALL_B2 + LEFT * (2 * self.R)
        clack   = self.BALL_B2 + LEFT * self.R
        # constant approach speed — honest, no easing on free travel
        self.play(cue.animate(rate_func=linear).move_to(contact),
                  lab_a.animate(rate_func=linear)
                       .move_to(contact + DOWN * (self.R + 0.32 + 0.12)),
                  run_time=0.8)

        ring = impact_ring(clack)
        self.add(ring)
        # impact: target departs at the same constant speed; the token LOCKS —
        # underline flares, one tiny held pulse. (POST: warm click here.)
        self.play(
            target.animate(rate_func=linear, run_time=0.8)
                  .move_to(self.BALL_B2 + RIGHT * 2.3),
            lab_b.animate(rate_func=linear, run_time=0.8)
                 .shift(RIGHT * 2.3),
            ring.animate(rate_func=rate_functions.ease_out_quad,
                         run_time=0.3).scale(10).set_stroke(opacity=0.0),
            underline.animate(rate_func=rate_functions.there_and_back,
                              run_time=0.55).set_stroke(width=5.5),
            token.animate(rate_func=rate_functions.there_and_back,
                          run_time=0.55).scale(1.05),
        )
        self.remove(ring)
        self.wait(0.5)

        # Before / after — the identical amber total on both sides of time.
        def ba_pill(word, x):
            head = Text(word, font=FONT, font_size=20, color=COLOR_GROUND,
                        weight=BOLD)
            num = MathTex(r"1.0\ \text{kg}", font_size=34, color=COLOR_MASS)
            col = VGroup(head, num).arrange(DOWN, buff=0.16).move_to([x, 1.35, 0])
            bg = label_pill(col)
            return VGroup(bg, col).set_z_index(8)

        before = ba_pill("BEFORE", -2.7)
        after  = ba_pill("AFTER", 2.7)
        eqs = MathTex("=", font_size=44, color=COLOR_WHITE
                      ).move_to([0, 1.35, 0]).set_z_index(8)
        self.play(LaggedStart(FadeIn(before, shift=RIGHT * 0.18),
                              FadeIn(eqs, scale=0.6),
                              FadeIn(after, shift=RIGHT * 0.18),
                              lag_ratio=0.35),
                  run_time=1.2, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        tick = check_mark(COLOR_TICK).next_to(token, RIGHT, buff=0.45)
        tick.set_z_index(10)
        self.play(Create(tick), run_time=0.4,
                  rate_func=rate_functions.ease_out_back)   # POST: clean chime
        self.wait()                       # comfortable. solved. (the rug)

        self._a2 = dict(token=token, token_glow=token_glow, underline=underline,
                        tick=tick, before=before, after=after, eqs=eqs,
                        cue=cue, target=target, lab_a=lab_a, lab_b=lab_b)

    # ===================================================================== A3
    def act3_mass_says_nothing(self):
        s = self._a2

        # Kill the comfort: ✓ → ?, the amber drains, slow push-in.
        broke = MathTex("?", font_size=46, color=COLOR_GROUND
                        ).move_to(s["tick"]).set_z_index(10)
        # POST: reverse / record-lift of the Act-2 chime lands on this morph.
        self.play(
            ReplacementTransform(s["tick"], broke),
            s["token"].animate.set_color("#A89B72"),
            s["underline"].animate.set_color("#A89B72").set_stroke(opacity=0.5),
            s["token_glow"].animate.set_opacity(0.04),
            self.camera.frame.animate.scale(0.90),
            run_time=1.6, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.5)

        # Isolate one ball; everything else withdraws.
        BALL_P = np.array([0.0, -0.45, 0.0])
        self.play(
            FadeOut(VGroup(s["before"], s["after"], s["eqs"])),
            FadeOut(s["target"]), FadeOut(s["lab_b"]),
            FadeOut(VGroup(s["token"], s["token_glow"], s["underline"], broke),
                    shift=UP * 0.2),
            s["cue"].animate.move_to(BALL_P),
            s["lab_a"].animate.move_to(BALL_P + LEFT * 1.35 + UP * 0.0),
            run_time=1.1, rate_func=rate_functions.ease_in_out_sine,
        )
        cue, lab = s["cue"], s["lab_a"]
        self.wait(0.5)

        # The three questions mass cannot answer — one line at a time.
        qs = VGroup(
            Text("How far?", font=FONT, font_size=28, color=COLOR_WHITE),
            Text("Which direction?", font=FONT, font_size=28, color=COLOR_WHITE),
            Text("How fast?", font=FONT, font_size=28, color=COLOR_WHITE),
        )
        for i, q in enumerate(qs):
            q.move_to([0, 2.55 - i * 0.55, 0]).set_z_index(8)
        for q in qs:
            self.play(Write(q), run_time=0.55)
            self.wait(0.35)
        self.play(qs.animate.set_opacity(0.30), run_time=0.5)

        # ── the killer image: every future is equally allowed by "0.5 kg" ──
        fan_specs = [
            (152 * DEGREES, 2.6), (122 * DEGREES, 1.9), (62 * DEGREES, 1.8),
            (28 * DEGREES, 3.3), (0 * DEGREES, 2.2), (-32 * DEGREES, 3.0),
            (-72 * DEGREES, 1.7), (-128 * DEGREES, 2.4),
        ]
        paths, ghosts, moves = VGroup(), VGroup(), []
        for ang, L in fan_specs:
            d = np.array([np.cos(ang), np.sin(ang), 0])
            end = BALL_P + d * L
            path = DashedLine(BALL_P + d * 0.35, end, color=COLOR_WHITE,
                              stroke_width=2, stroke_opacity=0.22,
                              dash_length=0.11)
            ghost = make_pool_ball(COLOR_CUE, self.R).move_to(BALL_P)
            ghost.set_opacity(0.20).set_z_index(3)
            paths.add(path)
            ghosts.add(ghost)
            moves.append(AnimationGroup(
                Create(path),
                ghost.animate(rate_func=rate_functions.ease_out_sine)
                     .move_to(end)))
        self.add(ghosts)
        self.play(LaggedStart(*moves, lag_ratio=0.12), run_time=2.6)
        # POST: hold SILENCE on the fanned ghosts. The image finishes the thought.
        self.wait(1.5)

        # Collapse the futures; the fact becomes paperwork.
        self.play(
            FadeOut(paths),
            *[g.animate.move_to(BALL_P).set_opacity(0.0) for g in ghosts],
            FadeOut(qs),
            run_time=0.8, rate_func=rate_functions.ease_in_cubic,
        )
        self.remove(ghosts)

        # The ID card: one field filled, three blank. INCOMPLETE.
        card = RoundedRectangle(width=4.7, height=2.75, corner_radius=0.18,
                                stroke_color=COLOR_GROUND, stroke_width=1.6,
                                stroke_opacity=0.6, fill_color="#11151C",
                                fill_opacity=0.95).move_to([0.7, 0.1, 0])
        card.set_z_index(8)
        fields = [("Mass", r"0.5\ \text{kg}", True),
                  ("Direction", r"\text{------}", False),
                  ("Speed", r"\text{------}", False),
                  ("Distance", r"\text{------}", False)]
        rows = VGroup()
        for i, (name, val, filled) in enumerate(fields):
            n = Text(name, font=FONT, font_size=21, color=COLOR_GROUND)
            v = MathTex(val, font_size=29,
                        color=COLOR_MASS if filled else COLOR_DIM)
            n.move_to(card.get_left() + RIGHT * 1.05
                      + UP * (0.92 - i * 0.58))
            v.move_to(card.get_left() + RIGHT * 3.05
                      + UP * (0.92 - i * 0.58))
            row = VGroup(n, v)
            row.value = v
            rows.add(row)
        rows.set_z_index(9)
        mini_tick = check_mark(COLOR_TICK, 0.34).next_to(rows[0].value, RIGHT,
                                                         buff=0.22)
        mini_tick.set_z_index(9)

        self.play(
            FadeIn(card, scale=0.95),
            cue.animate.move_to([-3.4, 0.1, 0]).set_opacity(0.45),
            run_time=0.8, rate_func=rate_functions.ease_out_cubic,
        )
        # the floating fact files itself into the one field it can fill
        self.play(ReplacementTransform(lab, rows[0].value),
                  FadeIn(rows[0][0]), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_cubic)
        self.play(Create(mini_tick), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rows[1:]],
                              lag_ratio=0.2), run_time=0.9)
        self.wait(0.5)

        stamp_txt = Text("INCOMPLETE", font=FONT, font_size=40,
                         color=COLOR_RED, weight=BOLD)
        stamp_box = SurroundingRectangle(stamp_txt, color=COLOR_RED, buff=0.14,
                                         stroke_width=3.5)
        stamp = VGroup(stamp_txt, stamp_box).rotate(12 * DEGREES)
        stamp.move_to(card.get_center()).set_z_index(11)
        # the stamp pattern from scene_0: pre-place oversized, slam to size
        self.play(FadeIn(stamp.scale(1.9)), run_time=0.01)
        self.play(stamp.animate.scale(1 / 1.9), run_time=0.28,
                  rate_func=rate_functions.ease_in_quad)        # the slam
        self.play(Flash(stamp.get_center(), color=COLOR_RED, line_length=0.16,
                        num_lines=10, flash_radius=1.2,
                        line_stroke_width=2.2), run_time=0.4)
        self.wait(0.5)

        self._clear_to_grid(run_time=0.9)
        self.play(Restore(self.camera.frame), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)

    # ===================================================================== A4
    def act4_speed_matters(self):
        # ── the control: SAME mass, twice ──
        LANE_T, LANE_B = 1.15, -1.15
        START_X = -4.3
        WALL_X = 4.9
        STOP_X = WALL_X - 0.06 - self.R

        wall = Line([WALL_X, 2.4, 0], [WALL_X, -2.4, 0], color=COLOR_GROUND,
                    stroke_width=5)
        wall_hatch = VGroup(*[
            Line([WALL_X, y, 0], [WALL_X + 0.26, y + 0.26, 0],
                 color=COLOR_GROUND, stroke_width=1.6, stroke_opacity=0.5)
            for y in np.arange(-2.4, 2.3, 0.4)])
        self.play(Create(wall), FadeIn(wall_hatch), run_time=0.5)

        ball_t = make_pool_ball(COLOR_CUE, self.R).move_to([START_X, LANE_T, 0])
        ball_b = make_pool_ball(COLOR_CUE, self.R).move_to([START_X, LANE_B, 0])
        for b in (ball_t, ball_b):
            b.set_z_index(5)
        lab_t = MathTex(r"0.5\ \text{kg}", font_size=30, color=COLOR_MASS
                        ).next_to(ball_t, DOWN, buff=0.28)
        lab_b = MathTex(r"0.5\ \text{kg}", font_size=30, color=COLOR_MASS
                        ).next_to(ball_b, DOWN, buff=0.28)
        self.play(LaggedStart(FadeIn(ball_t, scale=0.85),
                              FadeIn(ball_b, scale=0.85), lag_ratio=0.2),
                  run_time=0.7, rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(lab_t, shift=UP * 0.08), FadeIn(lab_b, shift=UP * 0.08),
                  run_time=0.5)
        # call out the sameness — both amber facts pulse as one
        self.play(VGroup(lab_t, lab_b).animate.scale(1.15), run_time=0.5,
                  rate_func=rate_functions.there_and_back)
        self.wait(0.5)

        # ── velocity enters in its series grammar: cyan arrow, LENGTH = speed ──
        def vel_arrow(ball, length):
            p = ball.get_center() + RIGHT * (self.R + 0.06)
            return Arrow(p, p + RIGHT * length, buff=0, color=COLOR_VEL,
                         stroke_width=5,
                         max_tip_length_to_length_ratio=0.22).set_z_index(6)

        L_SLOW, L_FAST = 0.85, 2.125
        arr_t = vel_arrow(ball_t, L_SLOW)
        arr_b = vel_arrow(ball_b, L_FAST)
        sp_t = MathTex(r"40\ \text{km/h}", font_size=28, color=COLOR_VEL
                       ).next_to(arr_t, UP, buff=0.14)
        sp_b = MathTex(r"100\ \text{km/h}", font_size=28, color=COLOR_VEL
                       ).next_to(arr_b, UP, buff=0.14)
        self.play(GrowArrow(arr_t), FadeIn(sp_t, shift=UP * 0.08), run_time=0.6)
        self.play(GrowArrow(arr_b), FadeIn(sp_b, shift=UP * 0.08), run_time=0.6)
        self.wait(0.5)

        # arrows ride their balls — constant length = constant speed, honest
        arr_t.add_updater(lambda a: a.put_start_and_end_on(
            ball_t.get_center() + RIGHT * (self.R + 0.06),
            ball_t.get_center() + RIGHT * (self.R + 0.06 + L_SLOW)))
        arr_b.add_updater(lambda a: a.put_start_and_end_on(
            ball_b.get_center() + RIGHT * (self.R + 0.06),
            ball_b.get_center() + RIGHT * (self.R + 0.06 + L_FAST)))

        self.play(ball_t.animate(rate_func=linear).move_to([STOP_X, LANE_T, 0]),
                  run_time=1.2)
        arr_t.clear_updaters()
        ring_s = impact_ring([WALL_X, LANE_T, 0])
        self.add(ring_s)
        self.play(
            ring_s.animate(rate_func=rate_functions.ease_out_quad)
                  .scale(6).set_stroke(opacity=0.0),
            ball_t.animate(rate_func=rate_functions.ease_out_cubic)
                  .shift(LEFT * 0.35),
            FadeOut(arr_t),
            run_time=0.5,
        )
        self.remove(ring_s)
        self.wait(0.5)

        self.play(ball_b.animate(rate_func=linear).move_to([STOP_X, LANE_B, 0]),
                  run_time=0.5)
        arr_b.clear_updaters()
        ring_v = impact_ring([WALL_X, LANE_B, 0], sw=5)
        self.add(ring_v)
        cam_c = self.camera.frame.get_center()
        self.play(
            ring_v.animate(rate_func=rate_functions.ease_out_quad)
                  .scale(16).set_stroke(opacity=0.0),
            Flash([WALL_X, LANE_B, 0], color=COLOR_WHITE, line_length=0.30,
                  num_lines=12, flash_radius=0.6, line_stroke_width=3),
            ball_b.animate(rate_func=rate_functions.ease_out_cubic)
                  .shift(LEFT * 1.45),
            FadeOut(arr_b),
            run_time=0.55,
        )
        self.remove(ring_v)
        # camera shake — brief, decaying, then dead level again
        for k, off in enumerate([UR * 0.11, DL * 0.09, UP * 0.05, DOWN * 0.03]):
            self.play(self.camera.frame.animate.move_to(cam_c + off),
                      run_time=0.05, rate_func=linear)
        self.play(self.camera.frame.animate.move_to(cam_c), run_time=0.12,
                  rate_func=rate_functions.ease_out_sine)
        self.wait()                      # same mass, opposite consequence

        # ── casting the two leads: m and v, adjacent, NOT multiplied ──
        m_token = MathTex("m", font_size=110, color=COLOR_MASS
                          ).move_to([-1.5, 0.25, 0]).set_z_index(8)
        v_arrow = Arrow([0.5, 0.25, 0], [2.7, 0.25, 0], buff=0,
                        color=COLOR_VEL, stroke_width=7,
                        max_tip_length_to_length_ratio=0.18).set_z_index(8)
        v_lab = MathTex("v", font_size=60, color=COLOR_VEL
                        ).next_to(v_arrow, UP, buff=0.22).set_z_index(8)

        # continuity: the surviving fact and the surviving arrow BECOME the leads
        arr_seed = Arrow(ball_b.get_center() + RIGHT * (self.R + 0.06),
                         ball_b.get_center() + RIGHT * (self.R + 0.06 + L_FAST),
                         buff=0, color=COLOR_VEL, stroke_width=5,
                         max_tip_length_to_length_ratio=0.22)
        self.add(arr_seed)
        self.play(
            FadeOut(VGroup(wall, wall_hatch, sp_t, sp_b, lab_t)),
            FadeOut(ball_t), FadeOut(ball_b),
            ReplacementTransform(lab_b, m_token),
            ReplacementTransform(arr_seed, v_arrow),
            run_time=1.3, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(FadeIn(v_lab, shift=DOWN * 0.1), run_time=0.5)

        caption = Text("Both matter.", font=FONT, font_size=34,
                       color=COLOR_WHITE).move_to(DOWN * 1.75).set_z_index(8)
        self.play(Write(caption), run_time=0.9)
        self.wait(0.5)
        # one quiet synchronised breath — adjacent, charged, unfused.
        self.play(m_token.animate.scale(1.06),
                  VGroup(v_arrow, v_lab).animate.scale(1.06),
                  run_time=0.9, rate_func=rate_functions.there_and_back)

        self.wait()