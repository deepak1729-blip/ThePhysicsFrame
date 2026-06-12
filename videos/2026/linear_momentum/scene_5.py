from manim import *
import numpy as np

#
#  >>> POST (audio):
#  · Act 1 — one clean CLACK on the contact ring, then near-silence for the
#    push-in and squash. Hold the silence a full second.
#  · Act 2 — a soft symmetrical "lock" click the moment both arrows snap to
#    equal length. One clock-tick texture under the Δt sweep.
#  · Act 3 — one low "settle" tone per cascade resolution (four total).
#    Drop narration volume; let the transforms land in sequence.
#  · Act 4 — soft violet "pour" whoosh during the transfer; faint steady
#    heartbeat under the Total bar.
#  · Act 5 — one clean resolved chord on the title write-in. Then silence.

# ── BRAND PALETTE (series canvas, verbatim) ──
COLOR_BG     = "#0E1117"
COLOR_GROUND = "#8E8E93"
COLOR_WHITE  = "#E5E5EA"
COLOR_DIM    = "#3A3F47"

# ── MOMENTUM SERIES COLOR PROTOCOL (locked scenes 2–4) ──
COLOR_CUE      = "#E5E5EA"   # ball A — clean white
COLOR_TARGET   = "#FF5A5F"   # ball B — warm coral-red
COLOR_MASS     = "#F4B642"   # mass m — amber/gold
COLOR_VEL      = "#3FC8FF"   # velocity v — electric cyan
COLOR_MOMENTUM = "#C66BFF"   # p — series hero violet (the TOTAL)
COLOR_P_A      = "#9B4DE0"   # ball A's momentum — deep violet (scene_3)
COLOR_P_B      = "#DDB8FF"   # ball B's momentum — pale violet (scene_3)
COLOR_TIME     = "#8FB3A6"   # Δt — slate-green (scene_4)
COLOR_IMPULSE  = "#FF5FA2"   # F·Δt — magenta (christened scene_4)
COLOR_RED      = "#FF3B30"   # the force pair AND the minus sign

FONT = "Segoe UI"
config.background_color = COLOR_BG


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
    """Top-down ball: base disc + sheen + specular (scene_1/2/3 vocabulary)."""
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


def pill_bg(text_mob, buff=0.18, fill="#11151C", fill_opacity=0.92,
            stroke=COLOR_GROUND, stroke_w=1.2, stroke_op=0.45):
    h = text_mob.height + buff * 1.6
    w = text_mob.width + buff * 2.4
    return RoundedRectangle(
        corner_radius=min(h * 0.5, 0.20), height=h, width=w,
        stroke_color=stroke, stroke_width=stroke_w, stroke_opacity=stroke_op,
        fill_color=fill, fill_opacity=fill_opacity,
    ).move_to(text_mob.get_center())


def make_clock(radius=0.32, color=COLOR_TIME):
    """Time's face (scene_4 helper, verbatim)."""
    face = Circle(radius=radius, stroke_color=color, stroke_width=3,
                  fill_color="#11151C", fill_opacity=0.92)
    ticks = VGroup(*[
        Line(UP * (radius - 0.07), UP * radius, stroke_width=2,
             color=color, stroke_opacity=0.7).rotate(
                 k * TAU / 4, about_point=ORIGIN)
        for k in range(4)])
    hand = Line(ORIGIN, UP * radius * 0.62, stroke_width=3.5,
                color=COLOR_WHITE)
    pivot = Dot(ORIGIN, radius=0.035, color=color)
    g = VGroup(face, ticks, hand, pivot)
    g.face, g.hand = face, hand
    return g


# ═══════════════════════════════════════════════════════════════════════════
class Scene_5_TheCollisionProof(MovingCameraScene):

    # ── locked geometry ──
    R       = 0.28
    BALL_Y  = -1.35
    XC      = 0.0                       # contact x — surfaces meet here
    A_START = -4.8
    EQ_Y    = 1.72                      # the cascade line's home
    F_LEN   = 1.49                      # force-arrow length (identical, locked)
    MET_W, MET_H   = 1.25, 0.16        # under-ball momentum meters
    LANE_A, LANE_B = -2.25, -2.70      # scene_3's two-lane grammar
    TB_C    = np.array([0.0, 0.35, 0.0])  # Total bar centre
    TB_W, TB_H = 3.6, 0.32

    def construct(self):
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        self.act0_inherit_scene4()
        self.act1_the_contact()
        self.act2_equal_and_opposite()
        self.act3_the_cascade()
        self.act4_gain_and_loss()
        self.act5_conservation()

    # ===================================================================== A0
    def act0_inherit_scene4(self):
        # Hard-cut continuity: rebuild scene_4's exact closing frame — the
        # christened equation drifting at the top, waiting. No entrance.
        eq3 = MathTex("F", r"\cdot", r"\Delta t", "=", "m", r"\cdot",
                      r"\Delta v", font_size=76).scale(0.79)
        for i in range(3):
            eq3[i].set_color(COLOR_IMPULSE)
        eq3[3].set_color(COLOR_WHITE)
        for i in range(4, 7):
            eq3[i].set_color(COLOR_MOMENTUM)
        eq3.move_to([0, 2.52, 0]).set_z_index(8)

        lhs, rhs = eq3[0:3], eq3[4:7]
        imp_tag = Text("IMPULSE", font=FONT, font_size=26, weight=BOLD,
                       color=COLOR_IMPULSE).next_to(lhs, DOWN, buff=0.35)
        mom_tag = Text("change in momentum", font=FONT, font_size=21,
                       color=COLOR_MOMENTUM)
        mom_tag.move_to([rhs.get_center()[0], imp_tag.get_center()[1], 0])
        glow = Ellipse(width=rhs.width + 1.0, height=rhs.height + 0.85,
                       fill_color=COLOR_MOMENTUM, fill_opacity=0.16,
                       stroke_width=0).move_to(rhs).set_z_index(7)

        self.add(glow, eq3, imp_tag, mom_tag)
        self.wait(0.2)                       # the inherited, unresolved drift

        assembly = VGroup(eq3, imp_tag, mom_tag)
        self.play(assembly.animate.shift(UP * 0.10),
                  glow.animate.shift(UP * 0.10),
                  run_time=0.5, rate_func=linear)   # still waiting

        # The tool condenses into a docked fact (the ledger we'll bank on):
        # F·Δt = Δp. m·Δv collapses to the Δp it was revealed to be.
        eq_dock = MathTex(r"F \cdot \Delta t", "=", r"\Delta p",
                          font_size=34)
        eq_dock[0].set_color(COLOR_IMPULSE)
        eq_dock[2].set_color(COLOR_MOMENTUM)
        eq_dock.to_corner(UL, buff=0.55).set_z_index(10)
        dock_pill = pill_bg(eq_dock).set_z_index(9)

        self.play(
            FadeIn(dock_pill),
            ReplacementTransform(assembly, eq_dock),
            FadeOut(glow),
            run_time=0.5, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.dock = VGroup(dock_pill, eq_dock)
        self.wait(0.2)

    # ===================================================================== A1
    def act1_the_contact(self):
        CP = np.array([self.XC, self.BALL_Y, 0.0])     # contact point

        ball_a = make_pool_ball(COLOR_CUE, self.R).move_to(
            [self.A_START, self.BALL_Y, 0]).set_z_index(5)
        ball_b = make_pool_ball(COLOR_TARGET, self.R).move_to(
            [self.XC + self.R, self.BALL_Y, 0]).set_z_index(5)
        self.ball_a, self.ball_b, self.CP = ball_a, ball_b, CP

        self.play(LaggedStart(FadeIn(ball_b, scale=0.85),
                              FadeIn(ball_a, scale=0.85), lag_ratio=0.25), rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        # The slow approach — free travel = constant velocity = linear. Honest.
        self.play(ball_a.animate(rate_func=linear)
                  .move_to([self.XC - self.R, self.BALL_Y, 0]),
                  run_time=1.5)

        # CONTACT. The clack ring fires; the world freezes on this instant.
        # >>> POST: the single CLACK lands here, then near-silence.
        ring = impact_ring(CP)
        self.add(ring)
        self.play(ring.animate(rate_func=rate_functions.ease_out_quad)
                  .scale(9).set_stroke(opacity=0.0), run_time=0.32)
        self.remove(ring)

        # Do not cut — push the camera into the frozen instant.
        self.play(
            self.camera.frame.animate.set(width=7.0).move_to([0, -0.90, 0]),
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )

        # Name the two characters while the frame is still.
        tag_a = MathTex("A", font_size=26, color=COLOR_GROUND
                        ).next_to(ball_a, UP, buff=0.20).set_z_index(7)
        tag_b = MathTex("B", font_size=26, color=COLOR_GROUND
                        ).next_to(ball_b, UP, buff=0.20).set_z_index(7)
        self.tag_a, self.tag_b = tag_a, tag_b
        self.play(FadeIn(tag_a, shift=DOWN * 0.08),
                  FadeIn(tag_b, shift=DOWN * 0.08), run_time=0.5)

        self.play(
            ball_a.animate(rate_func=there_and_back, run_time=0.5)
                  .stretch(0.96, 0, about_edge=RIGHT).stretch(1.035, 1),
            ball_b.animate(rate_func=there_and_back, run_time=0.5)
                  .stretch(0.96, 0, about_edge=LEFT).stretch(1.035, 1),
        )

        # >>> POST: hold here. Full second of near-silence. "Wait — what
        #     actually happens in that instant?"
        self.wait(0.5)

    # ===================================================================== A2
    def act2_equal_and_opposite(self):
        CP = self.CP

        # Out of the frozen contact point, the force pair grows SIMULTANEOUSLY
        # — locked symmetry, one GrowArrow each, identical rate, identical
        # length. Same red on purpose: same color screams same magnitude.
        arrow_FAB = Arrow(CP + RIGHT * 0.06, CP + RIGHT * (0.06 + self.F_LEN),
                          buff=0, color=COLOR_RED, stroke_width=6,
                          max_tip_length_to_length_ratio=0.16).set_z_index(6)
        arrow_FBA = Arrow(CP + LEFT * 0.06, CP + LEFT * (0.06 + self.F_LEN),
                          buff=0, color=COLOR_RED, stroke_width=6,
                          max_tip_length_to_length_ratio=0.16).set_z_index(6)
        self.play(GrowArrow(arrow_FAB), GrowArrow(arrow_FBA), rate_func=rate_functions.ease_out_cubic)

        # The lock: both snap a hair past full length and settle TOGETHER.
        # >>> POST: one soft symmetrical "lock" click on this snap.
        self.play(arrow_FAB.animate.scale(1.05, about_point=CP),
                  arrow_FBA.animate.scale(1.05, about_point=CP),
                  run_time=0.15, rate_func=rate_functions.ease_out_quad)
        self.play(arrow_FAB.animate.scale(1 / 1.05, about_point=CP),
                  arrow_FBA.animate.scale(1 / 1.05, about_point=CP),
                  run_time=0.15, rate_func=rate_functions.ease_in_out_sine)

        lbl_FAB = MathTex(r"F_{AB}", font_size=30, color=COLOR_RED
                          ).next_to(arrow_FAB, UP, buff=0.16).set_z_index(7)
        lbl_FBA = MathTex(r"F_{BA}", font_size=30, color=COLOR_RED
                          ).next_to(arrow_FBA, UP, buff=0.16).set_z_index(7)
        self.play(FadeIn(lbl_FAB, shift=DOWN * 0.08),
                  FadeIn(lbl_FBA, shift=DOWN * 0.08), run_time=0.5)

        # Dimension-line proof of equal length: dashed span tip-to-tip with
        # end ticks. Confirms, then withdraws.
        DIM_Y = self.BALL_Y - 0.62
        tipL = CP + LEFT * (0.06 + self.F_LEN)
        tipR = CP + RIGHT * (0.06 + self.F_LEN)
        dim = VGroup(
            DashedLine([tipL[0], DIM_Y, 0], [tipR[0], DIM_Y, 0],
                       color=COLOR_WHITE, stroke_width=1.6,
                       stroke_opacity=0.5, dash_length=0.09),
            Line([tipL[0], DIM_Y - 0.09, 0], [tipL[0], DIM_Y + 0.09, 0],
                 color=COLOR_WHITE, stroke_width=1.8, stroke_opacity=0.6),
            Line([tipR[0], DIM_Y - 0.09, 0], [tipR[0], DIM_Y + 0.09, 0],
                 color=COLOR_WHITE, stroke_width=1.8, stroke_opacity=0.6),
        ).set_z_index(4)
        self.play(Create(dim), run_time=0.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeOut(dim), run_time=0.5)

        # ── "Same time tak" — its own visual statement. ONE shared clock,
        #    ONE Δt bracket spanning the contact. Not two. Both forces are
        #    stuck inside the same interval; the geometry refuses otherwise.
        brace = Brace(VGroup(self.ball_a, self.ball_b), DOWN, buff=0.33,
                      color=COLOR_TIME).set_z_index(6)
        dt_label = MathTex(r"\Delta t", font_size=36, color=COLOR_TIME
                           ).next_to(brace, DOWN, buff=0.16).set_z_index(7)
        clock = make_clock(0.30).move_to([0, 0.08, 0]).set_z_index(7)

        self.play(GrowFromCenter(brace), FadeIn(dt_label, shift=UP * 0.08),
                  run_time=0.5, rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(clock, scale=0.85), run_time=0.5)
        # one clean sweep — one contact, one interval, both forces inside it
        self.play(Rotate(clock.hand, -TAU * 0.75,
                         about_point=clock.face.get_center()), rate_func=linear)

        # >>> POST: hold the symmetry. Two equal red arrows mirrored across
        #     one shared clock — it should feel almost unfair.
        self.wait(0.5)

        self.arrow_FAB, self.arrow_FBA = arrow_FAB, arrow_FBA
        self.lbl_FAB, self.lbl_FBA = lbl_FAB, lbl_FBA
        self.brace, self.dt_label, self.clock = brace, dt_label, clock

    # ── Act 3 internals ──────────────────────────────────────────────────
    def _cascade_line(self, parts, colors, minus_idx, fs):
        """A cascade line with a phantom minus slot, aligned so that slot sits
        exactly on MINUS_C. The one real minus mobject is never rebuilt."""
        ln = MathTex(*parts, font_size=fs).set_z_index(8)
        for i, c in colors.items():
            ln[i].set_color(c)
        ln.shift(self.MINUS_C - ln[minus_idx].get_center())
        ln[minus_idx].set_opacity(0)
        return ln

    # ===================================================================== A3
    def act3_the_cascade(self):
        # Pull back out; the frozen collision stays at the bottom of frame.
        self.play(Restore(self.camera.frame),
                  FadeOut(self.clock, scale=0.8),
                  run_time=1.5, rate_func=rate_functions.ease_in_out_cubic)
        self.wait(0.5)

        # ── STEP 1 · birth the minus sign from the arrow ──────────────────
        # Reference line fixes every slot; the minus slot defines MINUS_C,
        # the one point in space the minus will own for the rest of the act.
        l1 = MathTex(r"F_{AB}", "=", "-", r"F_{BA}", font_size=58
                     ).move_to([0, self.EQ_Y, 0]).set_z_index(8)
        l1[0].set_color(COLOR_RED)
        l1[3].set_color(COLOR_RED)
        self.MINUS_C = l1[2].get_center().copy()
        l1[2].set_opacity(0)

        minus = MathTex("-", font_size=58, color=COLOR_RED
                        ).move_to(self.MINUS_C).set_z_index(9)

        self.play(ReplacementTransform(self.lbl_FAB, l1[0]),
                  FadeIn(l1[1]), rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        # THE move of the scene: the leftward arrow and its label rise as one
        # — the arrow becomes the red minus, the label becomes the term.
        # "−F_BA" is the leftward arrow, written in algebra.
        self.play(
            ReplacementTransform(self.arrow_FBA, minus),
            ReplacementTransform(self.lbl_FBA, l1[3]),
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )
        # >>> POST: settle tone #1.
        self.wait()

        # The geometry has spoken; its scaffolding recedes (labels go, the
        # surviving rightward arrow ghosts to 25%).
        self.play(FadeOut(self.lbl_FAB), FadeOut(self.lbl_FBA),
                  self.arrow_FAB.animate.set_opacity(0.25),
                  run_time=0.5, rate_func=rate_functions.ease_in_out_sine)

        # ── STEP 2 · the SHARED Δt lands on both sides at once ────────────
        l2 = self._cascade_line(
            [r"F_{AB}", r"\cdot", r"\Delta t", "=", "-",
             r"F_{BA}", r"\cdot", r"\Delta t"],
            {0: COLOR_RED, 2: COLOR_TIME, 5: COLOR_RED, 7: COLOR_TIME},
            minus_idx=4, fs=58)

        # One green token splits into two identical Δt's — visual proof the
        # t is the same t. Everything else glides; the minus does not move.
        self.play(
            ReplacementTransform(l1[0], l2[0]),
            FadeIn(l2[1], scale=0.6),
            ReplacementTransform(self.dt_label, l2[2]),
            ReplacementTransform(l1[1], l2[3]),
            ReplacementTransform(l1[3], l2[5]),
            FadeIn(l2[6], scale=0.6),
            ReplacementTransform(self.dt_label.copy(), l2[7]),
            rate_func=rate_functions.ease_in_out_cubic,
        )
        # >>> POST: settle tone #2.
        self.wait()
        self.play(FadeOut(self.brace), run_time=0.5)

        # ── STEP 3 · each product earns scene_4's name: IMPULSE ───────────
        self.play(Indicate(self.dock, color=COLOR_WHITE, scale_factor=1.06),
                  run_time=0.5)
        l3 = self._cascade_line(
            [r"\text{Impulse}_{B}", "=", "-", r"\text{Impulse}_{A}"],
            {0: COLOR_IMPULSE, 3: COLOR_IMPULSE},
            minus_idx=2, fs=50)
        # F_AB acts ON B, so F_AB·Δt is B's impulse — the bookkeeping is
        # honest, and the minus still hasn't moved.
        self.play(
            ReplacementTransform(VGroup(l2[0], l2[1], l2[2]), l3[0]),
            ReplacementTransform(l2[3], l3[1]),
            ReplacementTransform(VGroup(l2[5], l2[6], l2[7]), l3[3]),
            rate_func=rate_functions.ease_in_out_cubic,
        )
        # >>> POST: settle tone #3.
        self.wait()

        # ── STEP 4 · impulse = Δp (the banked fact pays out) ──────────────
        l4 = self._cascade_line(
            [r"\Delta p_{B}", "=", "-", r"\Delta p_{A}"],
            {0: COLOR_P_B, 3: COLOR_P_A},
            minus_idx=2, fs=58)
        self.play(
            ReplacementTransform(l3[0], l4[0]),
            ReplacementTransform(l3[1], l4[1]),
            ReplacementTransform(l3[3], l4[3]),
            rate_func=rate_functions.ease_in_out_cubic,
        )
        # >>> POST: settle tone #4. Four lines, one motionless red minus —
        #     the "opposite-ness" survived every algebraic step because it
        #     came from a physical law, not from the algebra.
        self.wait(0.5)
        self.play(Indicate(VGroup(l4[0], l4[1], l4[3], minus),
                           color=COLOR_WHITE, scale_factor=1.06),
                  run_time=0.7)
        self.wait(0.5)

        self.l4, self.minus = l4, minus

    # ── Act 4 internals ──────────────────────────────────────────────────
    def _meter_frame(self, ball, lane_y, color):
        """One ball's momentum meter, riding the ball in its own lane.
        Fill width reads straight off the A-fraction tracker."""
        cx = ball.get_center()[0]
        f = self._frac_a() if color == COLOR_P_A else 1.0 - self._frac_a()
        track = RoundedRectangle(
            width=self.MET_W, height=self.MET_H,
            corner_radius=self.MET_H / 2,
            stroke_color=COLOR_GROUND, stroke_width=1.4, stroke_opacity=0.6,
            fill_opacity=0).move_to([cx, lane_y, 0])
        g = VGroup(track).set_z_index(6)
        w = (self.MET_W - 0.06) * f
        if w > 0.045:
            ih = self.MET_H * 0.60
            fill = RoundedRectangle(
                width=w, height=ih,
                corner_radius=min(ih / 2, w / 2),
                stroke_width=0, fill_color=color, fill_opacity=0.95)
            fill.move_to([cx - self.MET_W / 2 + 0.03 + w / 2, lane_y, 0])
            g.add(fill)
        return g

    def _total_frame(self):
        """The killer image: a fixed bar whose internal divider slides.
        Total width never changes by a single pixel."""
        fA = float(np.clip(self._frac_a(), 0.0, 1.0))
        wA = self.TB_W * fA
        g = VGroup().set_z_index(7)
        glow = RoundedRectangle(width=self.TB_W + 0.34,
                                height=self.TB_H + 0.30, corner_radius=0.20,
                                stroke_width=0, fill_color=COLOR_MOMENTUM,
                                fill_opacity=0.07).move_to(self.TB_C)
        g.add(glow)
        if wA > 0.03:
            rectA = Rectangle(width=wA, height=self.TB_H, stroke_width=0,
                              fill_color=COLOR_P_A, fill_opacity=0.92)
            rectA.move_to(self.TB_C + RIGHT * (-self.TB_W / 2 + wA / 2))
            g.add(rectA)
        wB = self.TB_W - wA
        if wB > 0.03:
            rectB = Rectangle(width=wB, height=self.TB_H, stroke_width=0,
                              fill_color=COLOR_P_B, fill_opacity=0.92)
            rectB.move_to(self.TB_C + RIGHT * (self.TB_W / 2 - wB / 2))
            g.add(rectB)
        if 0.03 < wA < self.TB_W - 0.03:
            div_x = self.TB_C[0] - self.TB_W / 2 + wA
            g.add(Line([div_x, self.TB_C[1] - self.TB_H * 0.72, 0],
                       [div_x, self.TB_C[1] + self.TB_H * 0.72, 0],
                       color=COLOR_WHITE, stroke_width=2.5))
        outline = RoundedRectangle(width=self.TB_W, height=self.TB_H,
                                   corner_radius=0.05, fill_opacity=0,
                                   stroke_color=COLOR_WHITE, stroke_width=2,
                                   stroke_opacity=0.85).move_to(self.TB_C)
        g.add(outline)
        return g

    # ===================================================================== A4
    def act4_gain_and_loss(self):
        ball_a, ball_b = self.ball_a, self.ball_b

        # System reset — the SAME objects returning (scene_1's promise motif).
        # The ghost force arrow has done its job.
        self.tag_a.add_updater(lambda m: m.next_to(ball_a, UP, buff=0.20))
        self.tag_b.add_updater(lambda m: m.next_to(ball_b, UP, buff=0.20))
        self.play(
            FadeOut(self.arrow_FAB),
            ball_a.animate.move_to([-3.95, self.BALL_Y, 0]),
            rate_func=rate_functions.ease_in_out_sine,
        )

        # One tracker is the whole act: A's share of the momentum. Everything
        # violet — both meters AND the Total bar — redraws from this number.
        self._pa = ValueTracker(1.0)
        self._frac_a = lambda: self._pa.get_value()

        mA_st = self._meter_frame(ball_a, self.LANE_A, COLOR_P_A)
        mB_st = self._meter_frame(ball_b, self.LANE_B, COLOR_P_B)
        self.play(FadeIn(mA_st, shift=UP * 0.08),
                  FadeIn(mB_st, shift=UP * 0.08),
                  run_time=0.7, rate_func=rate_functions.ease_out_cubic)
        mA = always_redraw(
            lambda: self._meter_frame(ball_a, self.LANE_A, COLOR_P_A))
        mB = always_redraw(
            lambda: self._meter_frame(ball_b, self.LANE_B, COLOR_P_B))
        self.add(mA, mB)
        self.remove(mA_st, mB_st)

        # The Total bar — built once, then watched. Divider left, all of it A.
        total_st = self._total_frame()
        total_lbl = Text("Total", font=FONT, font_size=22,
                         color=COLOR_MOMENTUM)
        total_lbl.next_to([self.TB_C[0] - self.TB_W / 2, self.TB_C[1], 0],
                          LEFT, buff=0.32).set_z_index(7)
        self.play(FadeIn(total_st, scale=0.96),
                  FadeIn(total_lbl, shift=RIGHT * 0.1),
                  run_time=0.8, rate_func=rate_functions.ease_out_cubic)
        total = always_redraw(self._total_frame)
        self.add(total)
        self.remove(total_st)
        self.wait(0.5)

        # ── slow-motion replay ── free travel: constant velocity, linear.
        self.play(ball_a.animate(rate_func=linear)
                  .move_to([self.XC - self.R, self.BALL_Y, 0]),
                  run_time=1.5)

        # IMPACT · the pour. Violet drains out of A and into B — relocation,
        # not consumption — while the divider slides and the bar's outer
        # edges do not move. The squash returns as a quiet callback.
        # >>> POST: soft violet whoosh under the transfer.
        ring = impact_ring(self.CP)
        self.add(ring)
        self.play(
            ring.animate(rate_func=rate_functions.ease_out_quad,
                         run_time=0.5).scale(10).set_stroke(opacity=0.0),
            ball_a.animate(rate_func=there_and_back, run_time=0.5)
                  .stretch(0.96, 0, about_edge=RIGHT),
            ball_b.animate(rate_func=there_and_back, run_time=0.5)
                  .stretch(0.96, 0, about_edge=LEFT),
            self._pa.animate(rate_func=rate_functions.ease_in_out_sine).set_value(0.0),
        )
        self.remove(ring)
        self.wait(0.5)

        # Departure — full handoff: A stops dead, B leaves at A's old speed
        # (scene_1's founding image, finally explained).
        self.play(ball_b.animate(rate_func=linear)
                  .move_to([3.35, self.BALL_Y, 0]),
                  run_time=1.5)
        self.wait(0.5)

        # The one thing that never flinched takes a single quiet bow.
        outline_flash = RoundedRectangle(
            width=self.TB_W, height=self.TB_H, corner_radius=0.05,
            fill_opacity=0, stroke_color=COLOR_MOMENTUM,
            stroke_width=4).move_to(self.TB_C).set_z_index(8)
        self.play(ShowPassingFlash(outline_flash, time_width=0.7),
                  run_time=1.5)
        self.wait(0.5)

        self.mA, self.mB, self.total, self.total_lbl = mA, mB, total, total_lbl

    # ===================================================================== A5
    def act5_conservation(self):
        l4, minus = self.l4, self.minus
        for m in (self.mA, self.mB, self.total):
            m.clear_updaters()
        self.tag_a.clear_updaters()
        self.tag_b.clear_updaters()

        # Everything recedes; the surviving line and the Total bar remain.
        eq_grp = VGroup(l4[0], l4[1], l4[3], minus)
        self.play(
            FadeOut(VGroup(self.mA, self.mB, self.tag_a, self.tag_b)),
            FadeOut(self.ball_a, scale=0.85), FadeOut(self.ball_b, scale=0.85),
            FadeOut(self.dock, shift=UP * 0.2),
            self.total.animate.scale(0.85).move_to([0, -1.75, 0]),
            self.total_lbl.animate.move_to([-2.35, -1.75, 0]),
            eq_grp.animate.scale(1.12).move_to([0, 0.45, 0]),
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.5)

        # One step further: the red minus — finally free to move — arcs over
        # the equals sign and becomes the plus. "Opposite" matures into
        # "together they cancel." (Scene_4's Δt-arc, answered.)
        final = MathTex(r"\Delta p_{A}", "+", r"\Delta p_{B}", "=", "0",
                        font_size=68).move_to([0, 0.45, 0]).set_z_index(9)
        final[0].set_color(COLOR_P_A)
        final[1].set_color(COLOR_RED)
        final[2].set_color(COLOR_P_B)
        self.play(
            ReplacementTransform(l4[3], final[0], path_arc=1.5),
            ReplacementTransform(minus, final[1], path_arc=2.4),
            ReplacementTransform(l4[0], final[2], path_arc=1.5),
            ReplacementTransform(l4[1], final[3]),
            FadeIn(final[4], shift=LEFT * 0.12),
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait()

        # The name. >>> POST: one clean resolved chord on this write-in.
        title = Text("Conservation of Momentum", font=FONT, font_size=44,
                     weight=BOLD, color=COLOR_WHITE
                     ).move_to([0, 2.05, 0]).set_z_index(9)
        self.play(Write(title), run_time=1.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        # Closing morph: the thing that stayed constant literally becomes the
        # line under the name of the law.
        underline = RoundedRectangle(
            width=title.width + 0.25, height=0.075, corner_radius=0.037,
            stroke_width=0, fill_color=COLOR_MOMENTUM, fill_opacity=0.95)
        underline.next_to(title, DOWN, buff=0.22).set_z_index(8)
        self.play(
            ReplacementTransform(VGroup(self.total, self.total_lbl), underline),
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.5)

        # Continuity tease for Scene 6: p = mv lingers faintly in the corner —
        # the formula is no longer just a thing to memorise.
        pmv = MathTex("p", "=", "m", "v", font_size=30).set_z_index(5)
        pmv[0].set_color(COLOR_MOMENTUM)
        pmv[2].set_color(COLOR_MASS)
        pmv[3].set_color(COLOR_VEL)
        pmv.to_corner(DR, buff=0.65).set_opacity(0.0)
        self.add(pmv)
        self.play(pmv.animate.set_opacity(0.14), run_time=1.5,
                  rate_func=rate_functions.ease_in_out_sine)

        # One slow breath, then stillness — the landing of the whole argument.
        self.play(final.animate.scale(1.03), run_time=1.5,
                  rate_func=rate_functions.there_and_back)
        self.wait()