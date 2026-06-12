from manim import *
import numpy as np

#  >>> EDIT (Premiere):
#  · Act 3 — optional 1–2 s real air-track glider collision clip on the cut
#    to the lab stage (marked inline). Skip if it breaks rhythm.

#  >>> POST: sub-bass swell on the movimentum→momentum morph (Act 1);


# ── BRAND PALETTE (series canvas, verbatim from linear_momentum/scene_2) ──
COLOR_BG     = "#0E1117"
COLOR_GROUND = "#8E8E93"
COLOR_WHITE  = "#E5E5EA"
COLOR_DIM    = "#3A3F47"

# ── MOMENTUM SERIES COLOR PROTOCOL (locked in scene_2) ──
COLOR_CUE      = "#E5E5EA"   # ball A — clean white
COLOR_TARGET   = "#FF5A5F"   # ball B — warm coral-red
COLOR_MASS     = "#F4B642"   # mass m — warm amber/gold
COLOR_VEL      = "#3FC8FF"   # velocity v — electric cyan, ALWAYS an arrow
COLOR_MOMENTUM = "#C66BFF"   # p = mv — claims its identity THIS scene
COLOR_TICK     = "#34C759"   # confirmation green
COLOR_RED      = "#FF3B30"   # strike-through / wrongness

# NEW this scene — two violet shades so the eye can track who-gave-what.
# The bright series violet is reserved for the TOTAL. (Flagged in chat.)
COLOR_P_A = "#9B4DE0"        # ball A's momentum — deep violet
COLOR_P_B = "#DDB8FF"        # ball B's momentum — pale violet

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
    """Top-down ball: base disc + sheen + specular (scene_1/2 vocabulary)."""
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


def pill_bg(text_mob, buff=0.18, fill="#11151C", fill_opacity=0.92,
            stroke=COLOR_GROUND, stroke_w=1.2, stroke_op=0.45):
    h = text_mob.height + buff * 1.6
    w = text_mob.width + buff * 2.4
    return RoundedRectangle(
        corner_radius=min(h * 0.5, 0.20), height=h, width=w,
        stroke_color=stroke, stroke_width=stroke_w, stroke_opacity=stroke_op,
        fill_color=fill, fill_opacity=fill_opacity,
    ).move_to(text_mob.get_center())


def optional_image(path, width):
    """Returns the image or None — for true seasoning overlays (no placeholder)."""
    try:
        return ImageMobject(path).scale_to_fit_width(width)
    except Exception:
        return None


def speed_dashes(n, color=COLOR_GROUND):
    """Grey trailing speed-dashes (scene_1's motion_icon vocabulary)."""
    g = VGroup()
    for i in range(n):
        op = 0.55 * (1 - i / max(n, 1) * 0.7)
        g.add(Line(ORIGIN, RIGHT * 0.16, stroke_width=3, color=color,
                   stroke_opacity=op).shift(LEFT * (0.12 + i * 0.26)))
    return g


# ═══════════════════════════════════════════════════════════════════════════
class Scene_3_QuantityOfMotion(MovingCameraScene):

    # ── locked geometry ──
    TRACK_Y = -1.6                  # the frictionless track (Acts 3–4)
    XC      = 0.30                  # collision contact x (all four runs)
    S       = 0.45                  # lane scale: screen-units per momentum unit
    S_BALL  = 0.30                  # under-ball arrow scale (smaller, no clutter)
    SUM_X0  = -0.90                 # lane left anchor → total spans −0.9 … +0.9
    LANE_Y1 = 2.95                  # component row A
    LANE_Y2 = 2.52                  # component row B (tip-to-tail drop)
    TOTAL_Y = 1.86                  # the untouchable total
    ROW_A   = -2.25                 # under-ball arrow lane (ball A)
    ROW_B   = -2.72                 # under-ball arrow lane (ball B)
    P_TOT   = 4.0                   # every scenario sums to this — by design
    R_OF    = {1: 0.22, 2: 0.277, 3: 0.317}   # radius from mass (∝ m^⅓-ish)

    def construct(self):
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        self.act0_inherit_scene2()
        self.act1_the_naming()
        self.act2_measurement_of_motion()
        self.act3_just_a_definition()
        self.act4_experimental_fact()
        self.act5_but_why()

    def _clear_to_grid(self, run_time=0.9, keep=()):
        clear = Group(*[m for m in self.mobjects
                        if m is not self.grid and m not in keep])
        if len(clear):
            self.play(FadeOut(clear), run_time=run_time,
                      rate_func=rate_functions.ease_in_out_sine)

    # ===================================================================== A0
    def act0_inherit_scene2(self):
        # Hard-cut continuity: rebuild scene_2's exact closing frame —
        # the charged, unfused pair. m (amber) · v (cyan arrow). No entrance.
        m_token = MathTex("m", font_size=110, color=COLOR_MASS
                          ).move_to([-1.5, 0.25, 0]).set_z_index(8)
        v_arrow = Arrow([0.5, 0.25, 0], [2.7, 0.25, 0], buff=0,
                        color=COLOR_VEL, stroke_width=7,
                        max_tip_length_to_length_ratio=0.18).set_z_index(8)
        v_lab = MathTex("v", font_size=60, color=COLOR_VEL
                        ).next_to(v_arrow, UP, buff=0.22).set_z_index(8)
        caption = Text("Both matter.", font=FONT, font_size=34,
                       color=COLOR_WHITE).move_to(DOWN * 1.75).set_z_index(8)
        self.add(m_token, v_arrow, v_lab, caption)
        self.wait(0.8)                       # the inherited breath

        # The leads step to the wings and dim — we step back in time, before
        # anyone knew what to do with them. They will be recalled in Act 2.
        v_grp = VGroup(v_arrow, v_lab)
        self.play(
            FadeOut(caption, shift=DOWN * 0.15),
            m_token.animate.scale(0.40).move_to([-5.7, 2.7, 0]).set_opacity(0.30),
            v_grp.animate.scale(0.40).move_to([5.3, 2.7, 0]).set_opacity(0.30),
            run_time=1.3, rate_func=rate_functions.ease_in_out_sine,
        )
        self.m_token, self.v_grp = m_token, v_grp
        self.wait(0.4)

    # ===================================================================== A1
    def act1_the_naming(self):
        
        # Kinetic typography — one phrase at a time, each holding a beat.
        # Slow ~3% camera push spread across the act (gravity, not motion).
        ph1 = Text("quantity of motion", font=FONT, font_size=38,
                   color=COLOR_WHITE).move_to(UP * 1.9).set_z_index(5)
        ph2 = Text("moving power", font=FONT, font_size=38,
                   color=COLOR_WHITE).move_to(UP * 1.1).set_z_index(5)
        ph3 = Text("movement", font=FONT, font_size=38,
                   color=COLOR_WHITE).move_to(UP * 0.3).set_z_index(5)

        self.play(Write(ph1), self.camera.frame.animate.scale(0.992),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.7)
        self.play(Write(ph2), ph1.animate.set_opacity(0.35),
                  self.camera.frame.animate.scale(0.992),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.7)
        self.play(Write(ph3), ph2.animate.set_opacity(0.35),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)

        # The Latin root — italic reads "old" against the clean sans stack.
        movi = Text("movimentum", font=FONT, font_size=68, slant=ITALIC,
                    color=COLOR_WHITE).move_to(DOWN * 0.9).set_z_index(6)
        self.play(Write(movi), ph3.animate.set_opacity(0.35),
                  self.camera.frame.animate.scale(0.992),
                  run_time=1.6, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.9)

        # The stack withdraws; the Latin word takes centre stage alone.
        self.play(
            FadeOut(VGroup(ph1, ph2, ph3), shift=UP * 0.25),
            movi.animate.move_to(ORIGIN),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.5)

        # ── THE MORPH: movimentum → momentum, letter by letter. ──
        # 'v','i' (glyphs 2,3) dissolve; the survivors slide inward to close
        # the gap. The Latin literally contracts into the modern word.
        # >>> POST: single soft sub-bass swell lands exactly on this morph.
        target = Text("momentum", font=FONT, font_size=68, weight=BOLD,
                      color=COLOR_WHITE).move_to(ORIGIN).set_z_index(6)
        # free the glyphs so each can travel independently
        self.remove(movi)
        self.add(*movi.submobjects)
        mapping = [(0, 0), (1, 1), (4, 2), (5, 3), (6, 4), (7, 5), (8, 6), (9, 7)]
        self.play(
            FadeOut(movi[2], scale=0.55),
            FadeOut(movi[3], scale=0.55),
            *[ReplacementTransform(movi[i], target[j]) for i, j in mapping],
            run_time=1.6, rate_func=rate_functions.ease_in_out_cubic,
        )
        # re-parent the landed glyphs so the word animates as one mobject
        for j in range(len(target.submobjects)):
            self.remove(target[j])
        self.add(target)
        self.wait(0.6)

        # The word claims its permanent colour in the same breath it is named.
    
        anims = [target.animate.set_color(COLOR_MOMENTUM)]
        self.play(*anims, run_time=1.3,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)                       # let the naming breathe

        self.play(FadeOut(target, shift=UP * 0.3),
                  Restore(self.camera.frame),
                  run_time=0.5, rate_func=rate_functions.ease_in_out_sine)

    # ===================================================================== A2
    def act2_measurement_of_motion(self):
        # ── A single moving ball — the scene_1 motif — and the question. ──
        ball = make_pool_ball(COLOR_CUE, 0.28).move_to([-5.0, -0.55, 0])
        ball.set_z_index(5)
        question = Text("how much motion does it carry?", font=FONT,
                        font_size=30, color=COLOR_GROUND, slant=ITALIC)
        question.move_to(UP * 1.7).set_z_index(5)

        self.play(FadeIn(ball, scale=0.85), run_time=0.5,
                  rate_func=rate_functions.ease_out_cubic)
        self.play(
            ball.animate(rate_func=linear).move_to([1.6, -0.55, 0]),  # free glide — honest
            FadeIn(question, shift=DOWN * 0.12,
                   rate_func=rate_functions.ease_out_cubic),
            run_time=2.0,
        )
        self.wait(0.6)
        self.play(ball.animate.move_to([5.6, -0.55, 0]).set_opacity(0.25),
                  FadeOut(question, shift=UP * 0.12),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_sine)

        # ── MOMENTUM-AS-AREA: m is a height, v is a length, p is the area. ──
        O2 = np.array([-1.5, -0.6, 0.0])
        H, V = 1.7, 2.3

        bar = RoundedRectangle(width=0.16, height=H, corner_radius=0.08,
                               stroke_width=0, fill_color=COLOR_MASS,
                               fill_opacity=1.0)
        bar.move_to(O2 + LEFT * 0.16 + UP * H / 2).set_z_index(5)
        m_lab = MathTex("m", font_size=44, color=COLOR_MASS
                        ).next_to(bar, LEFT, buff=0.22).set_z_index(5)

        v_arr = Arrow(O2 + DOWN * 0.22, O2 + DOWN * 0.22 + RIGHT * V, buff=0,
                      color=COLOR_VEL, stroke_width=6,
                      max_tip_length_to_length_ratio=0.14).set_z_index(5)
        v_lab2 = MathTex("v", font_size=44, color=COLOR_VEL
                         ).next_to(v_arr, DOWN, buff=0.18).set_z_index(5)

        # The dimmed leads from Act 1 fly back and BECOME the construction.
        self.play(
            ReplacementTransform(self.m_token, bar), FadeIn(m_lab, shift=RIGHT * 0.1),
            ReplacementTransform(self.v_grp, VGroup(v_arr, v_lab2)),
            rate_func=rate_functions.ease_in_out_cubic,
        )

        # The sweep: a ghost of the mass bar rides the velocity, painting area.
        rect = Rectangle(width=V, height=H, stroke_color=COLOR_MOMENTUM,
                         stroke_width=2, stroke_opacity=0.8,
                         fill_color=COLOR_MOMENTUM, fill_opacity=0.40)
        rect.move_to(O2 + RIGHT * V / 2 + UP * H / 2).set_z_index(3)
        sweep = bar.copy().set_opacity(0.5).move_to(
            O2 + RIGHT * 0.08 + UP * H / 2).set_z_index(4)
        self.add(sweep)
        self.play(
            GrowFromEdge(rect, LEFT),
            sweep.animate.move_to(O2 + RIGHT * (V - 0.08) + UP * H / 2),
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.play(FadeOut(sweep), run_time=0.3)

        p_lab = MathTex("p", font_size=64, color=COLOR_MOMENTUM
                        ).move_to(rect).set_z_index(6)
        self.play(FadeIn(p_lab, scale=0.5), run_time=0.3,
                  rate_func=rate_functions.ease_out_back)
        self.wait(0.5)

        # The definition writes itself FROM the picture (colour-matched).
        eq = MathTex("p", "=", "m", r"\times", "v", font_size=54)
        eq[0].set_color(COLOR_MOMENTUM)
        eq[2].set_color(COLOR_MASS)
        eq[4].set_color(COLOR_VEL)
        eq.move_to(DOWN * 1.9 + RIGHT * 0.4).set_z_index(8)
        self.play(
            TransformFromCopy(p_lab, eq[0]),
            FadeIn(eq[1]), FadeIn(eq[3]),
            TransformFromCopy(bar, eq[2]),
            TransformFromCopy(v_arr, eq[4]),
            run_time=1.3, rate_func=rate_functions.ease_in_out_sine,
        )
        self.eq_pmv = eq
        self.wait(0.5)

        # ── THE HELD BEAT: two very different objects, the SAME violet area. ──
        def area_diagram(O, h, v):
            g = VGroup()
            b = RoundedRectangle(width=0.14, height=h, corner_radius=0.07,
                                 stroke_width=0, fill_color=COLOR_MASS,
                                 fill_opacity=1.0)
            b.move_to(O + LEFT * 0.14 + UP * h / 2)
            a = Arrow(O + DOWN * 0.20, O + DOWN * 0.20 + RIGHT * v, buff=0,
                      color=COLOR_VEL, stroke_width=5,
                      max_tip_length_to_length_ratio=min(0.5, 0.14 * 2.3 / v))
            r = Rectangle(width=v, height=h, stroke_color=COLOR_MOMENTUM,
                          stroke_width=2, stroke_opacity=0.8,
                          fill_color=COLOR_MOMENTUM, fill_opacity=0.40)
            r.move_to(O + RIGHT * v / 2 + UP * h / 2)
            g.add(r, b, a)
            g.rect, g.bar, g.arr = r, b, a
            return g

        OL = np.array([-4.4, -1.7, 0.0])     # heavy & slow: tall, short
        OR = np.array([1.5, -1.7, 0.0])      # light & fast: short, long
        diagL = area_diagram(OL, 2.0, 0.9).set_z_index(4)
        diagR = area_diagram(OR, 0.9, 2.0).set_z_index(4)

        heavy = make_pool_ball(COLOR_TARGET, 0.36).move_to(
            OL + RIGHT * 0.45 + UP * 2.85).set_z_index(5)
        heavy_d = speed_dashes(1).next_to(heavy, LEFT, buff=0.10)
        light = make_pool_ball(COLOR_CUE, 0.20).move_to(
            OR + RIGHT * 1.0 + UP * 2.45).set_z_index(5)
        light_d = speed_dashes(3).next_to(light, LEFT, buff=0.10)

        # The hero construction MORPHS into the heavy-slow diagram — no cut.
        self.play(
            FadeOut(VGroup(m_lab, v_lab2, p_lab)),
            FadeOut(ball),
            ReplacementTransform(rect, diagL.rect),
            ReplacementTransform(bar, diagL.bar),
            ReplacementTransform(v_arr, diagL.arr),
            eq.animate.move_to(UP * 2.9),
            run_time=1.3, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(
            FadeIn(heavy, scale=0.85), FadeIn(heavy_d),
            LaggedStart(GrowFromEdge(diagR.rect, LEFT),
                        FadeIn(diagR.bar, shift=RIGHT * 0.1),
                        GrowArrow(diagR.arr),
                        FadeIn(light, scale=0.85), FadeIn(light_d),
                        lag_ratio=0.15),
            run_time=1.4, rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(1.0)                       # tall-thin vs short-wide. look.

        # Proof by coincidence: copies fly to centre; the tall one morphs
        # (area-preserving) into the wide one's exact shape. They coincide.
        # >>> POST: light tick/click as the outlines land — "they match."
        centre_target = Rectangle(width=2.0, height=0.9,
                                  stroke_color=COLOR_WHITE, stroke_width=2.5,
                                  fill_color=COLOR_MOMENTUM, fill_opacity=0.45)
        centre_target.move_to(UP * 0.9).set_z_index(7)
        cL = diagL.rect.copy().set_z_index(7)
        cR = diagR.rect.copy().set_z_index(6)
        self.add(cL, cR)
        self.play(
            Transform(cL, centre_target),
            cR.animate.move_to(centre_target.get_center()),
            run_time=1.3, rate_func=rate_functions.ease_in_out_cubic,
        )
        same = Text("same amount of motion", font=FONT, font_size=26,
                    color=COLOR_GROUND, slant=ITALIC)
        same.next_to(centre_target, UP, buff=0.30).set_z_index(8)
        tick = check_mark(COLOR_TICK, 0.55).next_to(centre_target, RIGHT,
                                                    buff=0.4).set_z_index(8)
        self.play(Flash(centre_target.get_center(), color=COLOR_MOMENTUM,
                        line_length=0.18, num_lines=12, flash_radius=1.25,
                        line_stroke_width=2.2),
                  FadeIn(same, shift=DOWN * 0.1), run_time=0.6)
        self.play(Create(tick), run_time=0.4,
                  rate_func=rate_functions.ease_out_back)
        self.wait(1.3)                       # the intuition unlock. hold it.

        self._clear_to_grid(run_time=0.9, keep=(self.eq_pmv,))

    # ===================================================================== A3
    def act3_just_a_definition(self):
        eq = self.eq_pmv

        # Let the energy go cold: the equation alone, centre, slow push-in.
        self.play(
            eq.animate.move_to(ORIGIN).scale(1.25),
            self.camera.frame.animate.scale(0.92),
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine,
        )

        eq_dock = eq.copy().scale(0.52)
        dock_pill = pill_bg(eq_dock)
        eq_dock.to_corner(UL, buff=0.45)
        dock_pill.move_to(eq_dock.get_center())
        self.scoreboard = VGroup(dock_pill, eq_dock).set_z_index(9)

        # >>> EDIT: optional 1–2 s real air-track glider collision clip lands
        #     exactly on this cut to the lab (Premiere). Skip if it breaks rhythm.
        track = Line([-6.6, self.TRACK_Y, 0], [6.6, self.TRACK_Y, 0],
                     color=COLOR_GROUND, stroke_width=3).set_z_index(1)
        hatch = VGroup(*[
            Line([x, self.TRACK_Y, 0], [x - 0.22, self.TRACK_Y - 0.22, 0],
                 color=COLOR_GROUND, stroke_width=1.5, stroke_opacity=0.45)
            for x in np.arange(-6.4, 6.6, 0.5)]).set_z_index(1)

        # Balls parked at scenario-1 starts (Act 4 inherits them in place).
        r = self.R_OF[2]
        self._r1 = self._r2 = r
        x1c, x2c = self.XC - r, self.XC + r
        self.ball1 = make_pool_ball(COLOR_CUE, r).move_to(
            [x1c - 2.5 * 1.15, self.TRACK_Y + r, 0]).set_z_index(5)
        self.ball2 = make_pool_ball(COLOR_TARGET, r).move_to(
            [x2c - (-0.5) * 1.15, self.TRACK_Y + r, 0]).set_z_index(5)

        self.play(
            FadeIn(dock_pill),
            Transform(eq, eq_dock),
            Restore(self.camera.frame),
            Create(track), FadeIn(hatch),
            LaggedStart(FadeIn(self.ball1, scale=0.85),
                        FadeIn(self.ball2, scale=0.85), lag_ratio=0.25),
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.remove(eq)
        self.add(self.scoreboard)
        self.track_grp = VGroup(track, hatch)
        self.wait(0.6)

    # ── Act 4 internals ─────────────────────────────────────────────────
    def _h_arrow(self, anchor, length, color, sw=5.5):
        """Horizontal arrow with a zero-momentum guard (dot, not broken arrow)."""
        anchor = np.array([anchor[0], anchor[1], 0.0])
        if abs(length) < 0.07:
            return Dot(anchor, radius=0.05, color=color, fill_opacity=0.9)
        return Arrow(anchor, anchor + RIGHT * length, buff=0, color=color,
                     stroke_width=sw, max_tip_length_to_length_ratio=0.25)

    def _ball_arrow_maker(self, ball_attr, tracker, color, y_row, label_tex):
        def make():
            p = tracker.get_value()
            bx = getattr(self, ball_attr).get_center()[0]
            anchor = np.array([bx, y_row, 0.0])
            arr = self._h_arrow(anchor, p * self.S_BALL, color)
            lab = MathTex(label_tex, font_size=26, color=color)
            side = LEFT if p >= 0 else RIGHT
            lab.next_to(anchor, side, buff=0.16)
            return VGroup(arr, lab).set_z_index(6)
        return make

    def _lane_components(self):
        """Tip-to-tail vector sum of the two momenta — rebuilt every frame.
        Because momentum is a VECTOR, the addition is drawn as arrows."""
        p1, p2 = self._pa.get_value(), self._pb.get_value()
        x0 = self.SUM_X0
        tip1 = x0 + p1 * self.S
        g = VGroup()
        g.add(self._h_arrow([x0, self.LANE_Y1], p1 * self.S, COLOR_P_A, sw=5))
        
        # FIX: Added the 0 for the Z-axis in both coordinates
        g.add(DashedLine([tip1, self.LANE_Y1, 0], [tip1, self.LANE_Y2, 0],
                         color=COLOR_GROUND, stroke_width=1.4,
                         stroke_opacity=0.45, dash_length=0.06))
                         
        g.add(self._h_arrow([tip1, self.LANE_Y2], p2 * self.S, COLOR_P_B, sw=5))
        return g.set_z_index(7)

    def _stage_scenario(self, m1, m2, v1, v2, T_pre, caption_text):
        """Apple-keynote transition: same balls resize & glide to new marks,
        component arrows morph to the new split — the TOTAL is never touched."""
        r1, r2 = self.R_OF[m1], self.R_OF[m2]
        x1c, x2c = self.XC - r1, self.XC + r2
        start1 = [x1c - v1 * T_pre, self.TRACK_Y + r1, 0]
        start2 = [x2c - v2 * T_pre, self.TRACK_Y + r2, 0]

        new_cap = Text(caption_text, font=FONT, font_size=24,
                       color=COLOR_GROUND).move_to(DOWN * 3.25).set_z_index(8)
        self.play(
            self.ball1.animate.scale(r1 / self._r1).move_to(start1),
            self.ball2.animate.scale(r2 / self._r2).move_to(start2),
            self._pa.animate.set_value(m1 * v1),
            self._pb.animate.set_value(m2 * v2),
            ReplacementTransform(self._caption, new_cap),
            run_time=1.2, rate_func=rate_functions.ease_in_out_cubic,
        )
        self._caption = new_cap
        self._r1, self._r2 = r1, r2
        self.wait(0.5)

    def _play_collision(self, v1, v2, p1f, p2f, v1f, v2f,
                        T_pre, T_post, sticky=False, hero=False):
        r1, r2 = self._r1, self._r2
        x1c, x2c = self.XC - r1, self.XC + r2
        y1, y2 = self.TRACK_Y + r1, self.TRACK_Y + r2

        # Phase 1 · approach. Free travel = constant velocity = linear. Honest.
        self.play(
            self.ball1.animate(rate_func=linear).move_to([x1c, y1, 0]),
            self.ball2.animate(rate_func=linear).move_to([x2c, y2, 0]),
            run_time=T_pre,
        )

        # IMPACT · the individual arrows violently redistribute —
        # everything below changes; the TOTAL does not move. Not one pixel.
        ring = impact_ring([self.XC, (y1 + y2) / 2, 0])
        self.add(ring)
        self.play(
            ring.animate(rate_func=rate_functions.ease_out_quad)
                .scale(10).set_stroke(opacity=0.0),
            self._pa.animate.set_value(p1f),
            self._pb.animate.set_value(p2f),
            run_time=0.40, rate_func=rate_functions.ease_out_cubic,
        )
        self.remove(ring)

        if hero:
            # >>> POST: kill the music HERE for ~0.5 s. Chaos below,
            #     perfect stillness on top — held a beat past comfortable.
            self.wait(1.5)
        else:
            self.wait(0.4)

        # Phase 2 · departure. Same constant-velocity honesty.
        if sticky:
            self.play(
                self.ball1.animate(rate_func=linear)
                    .move_to([x1c + v1f * T_post, y1, 0]),
                self.ball2.animate(rate_func=linear)
                    .move_to([x2c + v2f * T_post, y2, 0]),
                run_time=T_post,
            )
        else:
            self.play(
                self.ball1.animate(rate_func=linear)
                    .move_to([x1c + v1f * T_post, y1, 0]),
                self.ball2.animate(rate_func=linear)
                    .move_to([x2c + v2f * T_post, y2, 0]),
                run_time=T_post,
            )
        self.wait(0.7)

    # ===================================================================== A4
    def act4_experimental_fact(self):
        # ── Trackers drive EVERYTHING violet: under-ball arrows AND the
        #    tip-to-tail lane redraw from the same two numbers, so the
        #    redistribution is one synchronised motion. ──
        self._pa = ValueTracker(2 * 2.5)     # scenario 1: p_A = 5
        self._pb = ValueTracker(2 * (-0.5))  # scenario 1: p_B = −1

        arrA = always_redraw(self._ball_arrow_maker(
            "ball1", self._pa, COLOR_P_A, self.ROW_A, "p_A"))
        arrB = always_redraw(self._ball_arrow_maker(
            "ball2", self._pb, COLOR_P_B, self.ROW_B, "p_B"))
        self.play(FadeIn(arrA), FadeIn(arrB), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.arrA, self.arrB = arrA, arrB
        self.wait(0.5)

        # The addition is BUILT from the balls' own arrows — copies fly up
        # and land tip-to-tail. Then the live lane takes over.
        snap = self._lane_components()
        self.play(
            TransformFromCopy(arrA, snap[0]),
            TransformFromCopy(arrB, snap[2]),
            FadeIn(snap[1]),
            run_time=1.2, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.lane = always_redraw(self._lane_components)
        self.add(self.lane)
        self.remove(snap)

        # The TOTAL — built once, then NEVER touched again. White underlay
        # makes it the brightest thing on screen; the eye locks to it.
        x0 = self.SUM_X0
        x_end = x0 + self.P_TOT * self.S
        under = Arrow([x0, self.TOTAL_Y, 0], [x_end, self.TOTAL_Y, 0], buff=0,
                      color=COLOR_WHITE, stroke_width=11,
                      max_tip_length_to_length_ratio=0.22
                      ).set_opacity(0.30).set_z_index(7)
        total = Arrow([x0, self.TOTAL_Y, 0], [x_end, self.TOTAL_Y, 0], buff=0,
                      color=COLOR_MOMENTUM, stroke_width=6.5,
                      max_tip_length_to_length_ratio=0.22).set_z_index(8)
        t_lab = MathTex(r"P_{\text{total}}", font_size=36,
                        color=COLOR_MOMENTUM)
        t_lab.next_to([x0, self.TOTAL_Y, 0], LEFT, buff=0.35).set_z_index(8)
        # the mark the components must always hit — a quiet vertical seam
        tipline = DashedLine([x_end, self.TOTAL_Y - 0.35, 0],
                             [x_end, self.LANE_Y1 + 0.30, 0],
                             color=COLOR_WHITE, stroke_width=1.5,
                             stroke_opacity=0.45, dash_length=0.08
                             ).set_z_index(6)
        self.play(GrowArrow(under), GrowArrow(total),
                  FadeIn(t_lab, shift=RIGHT * 0.1),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self.play(Create(tipline), run_time=0.5)
        self.total_grp = VGroup(under, total)
        self.wait(0.7)

        self._caption = Text("equal masses · head-on", font=FONT, font_size=24,
                             color=COLOR_GROUND).move_to(DOWN * 3.25
                             ).set_z_index(8)
        self.play(FadeIn(self._caption, shift=UP * 0.1), run_time=0.5)
        self.wait(0.4)

        # ── THE MONTAGE. Every scenario sums to P = 4 by construction, so
        #    the total arrow is literally one frozen object the whole act. ──

        # 1 · equal masses, head-on (elastic: velocities swap)
        self._play_collision(v1=2.5, v2=-0.5, p1f=-1.0, p2f=5.0,
                             v1f=-0.5, v2f=2.5, T_pre=1.15, T_post=1.1,
                             hero=True)

        # 2 · heavy hits light — the heavy ball stops DEAD (p_A → a dot)
        self._stage_scenario(3, 1, 2.0, -2.0, 1.0, "heavy meets light")
        self._play_collision(v1=2.0, v2=-2.0, p1f=0.0, p2f=4.0,
                             v1f=0.0, v2f=4.0, T_pre=1.0, T_post=0.95)

        # 3 · one starts at rest — "where did its motion come from?"
        self._stage_scenario(2, 2, 2.0, 0.0, 1.4, "one starts at rest")
        self._play_collision(v1=2.0, v2=0.0, p1f=0.0, p2f=4.0,
                             v1f=0.0, v2f=2.0, T_pre=1.4, T_post=1.2)

        # 4 · they stick together (perfectly inelastic) — the total STILL holds
        self._stage_scenario(1, 2, 3.0, 0.5, 1.3, "they stick together")
        self._play_collision(v1=3.0, v2=0.5, p1f=4.0 / 3.0, p2f=8.0 / 3.0,
                             v1f=4.0 / 3.0, v2f=4.0 / 3.0,
                             T_pre=1.3, T_post=1.3, sticky=True)

        self.wait(0.8)                       # four worlds. one rigid arrow.

        # Freeze the live machinery before the dissolve.
        self.lane.clear_updaters()
        self.arrA.clear_updaters()
        self.arrB.clear_updaters()
        self._act4_rest = Group(self.lane, self.arrA, self.arrB, tipline,
                                t_lab, self._caption, self.ball1, self.ball2,
                                self.track_grp, self.scoreboard)

    # ===================================================================== A5
    def act5_but_why(self):
        # ── Strip the stage bare. Only the survivor remains. ──
        self.play(FadeOut(self._act4_rest),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)

        # The total — the thing that refused to flinch — BECOMES the claim.
        eq = MathTex(r"P_{\text{total}}", "=", r"\text{constant}",
                     font_size=60).move_to(ORIGIN).set_z_index(8)
        eq[0].set_color(COLOR_MOMENTUM)
        eq[2].set_color(COLOR_WHITE)
        self.play(ReplacementTransform(self.total_grp, eq),
                  run_time=1.3, rate_func=rate_functions.ease_in_out_cubic)
        self.wait(0.8)

        # One slow, daring pulse: "I always hold... and nothing has told
        # you I must." Camera dead still from here to the end.
        glow = Dot(eq.get_center(), radius=1.6, color=COLOR_MOMENTUM,
                   fill_opacity=0.0, stroke_width=0).set_z_index(-1)
        self.add(glow)
        self.play(glow.animate.set_opacity(0.14), eq.animate.scale(1.04),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)
        self.play(glow.animate.set_opacity(0.0), eq.animate.scale(1 / 1.04),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)
        self.remove(glow)
        self.wait(0.6)

        # The discomfort. WHY? rises and HANGS.
        # >>> POST: full near-silence drop lands here. One low tone, then hold.
        why = Text("WHY?", font=FONT, font_size=92, weight=BOLD,
                   color=COLOR_WHITE).move_to(UP * 1.9).set_z_index(9)
        self.play(FadeIn(why, shift=UP * 0.35), run_time=1.6,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(1.8)

        # The forward-pull: F = ma ghosts in the deep background for one
        # breath, then withdraws before it resolves. (Delete these three
        # plays to keep the question entirely pure — flagged in chat.)
        fma = MathTex("F", "=", "ma", font_size=44, color=COLOR_DIM
                      ).move_to(DOWN * 2.4).set_opacity(0.0).set_z_index(2)
        self.add(fma)
        self.play(fma.animate.set_opacity(0.10), run_time=1.4,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(fma.animate.set_opacity(0.0), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.remove(fma)

        # End on the itch, not the scratch. Hold a beat past comfortable.
        self.wait()