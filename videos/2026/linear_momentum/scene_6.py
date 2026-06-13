from manim import *
import numpy as np

#  ════════════════════════════════════════════════════════════════════════
#  SCENE 6 — "Why energy wasn't enough — and why p = mv had to be"
#  (linear_momentum series · FINALE)
#
#  ASSETS REQUIRED: none. This scene is 100% drawn Manim.
#
#  >>> EDIT (Premiere) — optional overlays, undercut, never replacing Manim:
#  · Act 2 — 1–2 s real top-down scatter ("pool break overhead slow motion"
#    or "carrom board strike slow motion top view") right before the vector
#    autopsy begins (real chaos → drawn order). Marked inline.
#  · Act 3 — 1–2 s "thermal camera impact slow motion" under the 8 J → 7 J
#    tick. Pure seasoning. Marked inline.
#  · Act 6 — your standard channel outro card lands after the final fade.
#
#  >>> POST (audio):
#  · Act 1 — soft "thread-pull" / un-mute swell as the gold ENERGY row wakes.
#    No hard transition from scene_5 — same continuous thought.
#  · Act 2 — drop the bed on the twin "E = 8 J" hold; ONE clean tick + the
#    white flash when the before/after resultants coincide (money moment).
#  · Act 3 — sizzle/hiss as the red heat bits escape; clean CLINK on the
#    arrow handoff. The hiss-vs-clink contrast is half the argument.
#  · Act 4 — discrete soft click per chain link, accelerating in tempo,
#    then a fuller resolving thunk on "CONSERVED."
#  · Act 5 — one resonant tone on the snap, then near-silence for the held
#    frame. The silence IS the sound design.
#  · Act 6 — gentle rising whoosh as the arrow bends; outro sting after the
#    end-card line.
#
#  FLAGGED DECISIONS (veto any of these in chat):
#  1. Momentum stays series VIOLET #C66BFF (brief said cyan; cyan is locked
#     to velocity since scene_2). Energy wears scene_1's GOLD #FFD166 (the
#     ledger row we are reopening), overriding scene_2's reserved green.
#  2. Act-4 chain: v joins as the series cyan arrow (brief said green); the
#     third-law gate is scene_5's RED force pair (brief said white) so both
#     callbacks read instantly.
#  3. Act-2 right collision = honest elastic equal-mass 2D scattering; the
#     resultants coincide because the physics makes them.
#  4. Act-5 snap: the two opposing gate arrows become the two bars of "=".
#  5. Act 6 ends on the teaser text; branded outro card is Premiere.
#  ════════════════════════════════════════════════════════════════════════

# ── BRAND PALETTE (series canvas, verbatim) ──
COLOR_BG     = "#0E1117"
COLOR_GROUND = "#8E8E93"
COLOR_WHITE  = "#E5E5EA"
COLOR_DIM    = "#3A3F47"

# ── MOMENTUM SERIES COLOR PROTOCOL (locked scenes 2–5) ──
COLOR_CUE      = "#E5E5EA"   # ball A — clean white
COLOR_TARGET   = "#FF5A5F"   # ball B — warm coral-red
COLOR_MASS     = "#F4B642"   # mass m — amber/gold
COLOR_VEL      = "#3FC8FF"   # velocity v — electric cyan, ALWAYS an arrow
COLOR_MOMENTUM = "#C66BFF"   # p — series hero violet (cool, pointed)
COLOR_P_A      = "#9B4DE0"   # ball A's momentum — deep violet
COLOR_P_B      = "#DDB8FF"   # ball B's momentum — pale violet
COLOR_TICK     = "#34C759"   # confirmation green
COLOR_RED      = "#FF3B30"   # force pair / heat / strike-through
COLOR_ENERGY   = "#FFD166"   # scene_1's gold — the rival (warm, shapeless)
COLOR_SOUND    = "#C9D6DF"   # pale rings — sound leaving the system

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
    """Top-down ball: base disc + sheen + specular (scene_1–5 vocabulary)."""
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


def vec_arrow(start, vec, color, sw=5.5):
    return Arrow(start, start + vec, buff=0, color=color, stroke_width=sw,
                 max_tip_length_to_length_ratio=0.24)


def heat_wiggle(start, direction, length=0.85, color=COLOR_RED):
    """A small red zigzag — one escaping bit of heat."""
    d = direction / np.linalg.norm(direction)
    perp = np.array([-d[1], d[0], 0.0])
    pts = [start + d * length * (i / 7) + perp * 0.085 * np.sin(i * PI * 0.85)
           for i in range(8)]
    v = VMobject(stroke_color=color, stroke_width=3)
    v.set_points_smoothly(pts)
    return v


# ═══════════════════════════════════════════════════════════════════════════
class Scene_6_TheConclusion(MovingCameraScene):

    # ── locked geometry ──
    LC = np.array([-3.55, -0.85, 0.0])     # left  panel contact (Act 2)
    RC = np.array([ 3.55, -0.85, 0.0])     # right panel contact (Act 2)
    R2 = 0.20                              # Act-2 panel ball radius
    Q0 = np.array([0.60, 1.70, 0.0])       # tip-to-tail lane anchor (Act 2)
    PS = 0.9                               # momentum-arrow scale (Act 2)
    KS = 0.8                               # screen speed scale  (Act 2)
    # honest elastic equal-mass 2D collision (CM-frame rotation = 75°):
    VA_IN  = np.array([2.000,  0.600, 0.0])
    VB_IN  = np.array([0.000, -0.600, 0.0])
    VA_OUT = np.array([0.679,  1.121, 0.0])
    VB_OUT = np.array([1.321, -1.121, 0.0])
    TRACK_Y = -1.35                        # Act-3 stage
    R3 = 0.28
    ROW_Y = -1.95                          # Act-3 under-ball momentum lane
    CHAIN_Y = 0.40                         # Act-4 assembly line

    def construct(self):
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        self.act0_inherit_scene5()
        self.act1_the_unfinished_ledger()
        self.act2_same_number_different_story()
        self.act3_transfer_vs_transform()
        self.act4_the_chain()
        self.act5_elevation()
        self.act6_teaser()

    def _clear_to_grid(self, run_time=0.9, keep=()):
        clear = Group(*[m for m in self.mobjects
                        if m is not self.grid and m not in keep])
        if len(clear):
            self.play(FadeOut(clear), run_time=run_time,
                      rate_func=rate_functions.ease_in_out_sine)

    # ===================================================================== A0
    def act0_inherit_scene5(self):
        # Hard-cut continuity: rebuild scene_5's exact closing frame — the
        # named law, the zero-sum line, and p = mv ghosting in the corner.
        final = MathTex(r"\Delta p_{A}", "+", r"\Delta p_{B}", "=", "0",
                        font_size=68).move_to([0, 0.45, 0]).set_z_index(9)
        final[0].set_color(COLOR_P_A)
        final[1].set_color(COLOR_RED)
        final[2].set_color(COLOR_P_B)
        title = Text("Conservation of Momentum", font=FONT, font_size=44,
                     weight=BOLD, color=COLOR_WHITE
                     ).move_to([0, 2.05, 0]).set_z_index(9)
        underline = RoundedRectangle(
            width=title.width + 0.25, height=0.075, corner_radius=0.037,
            stroke_width=0, fill_color=COLOR_MOMENTUM, fill_opacity=0.95)
        underline.next_to(title, DOWN, buff=0.22).set_z_index(8)
        pmv = MathTex("p", "=", "m", "v", font_size=30).set_z_index(5)
        pmv[0].set_color(COLOR_MOMENTUM)
        pmv[2].set_color(COLOR_MASS)
        pmv[3].set_color(COLOR_VEL)
        pmv.to_corner(DR, buff=0.65).set_opacity(0.14)

        self.add(title, underline, final, pmv)
        self.wait(0.8)                          # the inherited stillness

        # The quiet victory: the law recedes; the faint corner formula comes
        # forward and claims the frame. It WON — give it the tick it earned.
        pmv_hero = MathTex("p", "=", "m", "v", font_size=64
                           ).move_to(UP * 0.9).set_z_index(9)
        pmv_hero[0].set_color(COLOR_MOMENTUM)
        pmv_hero[2].set_color(COLOR_MASS)
        pmv_hero[3].set_color(COLOR_VEL)

        self.play(
            FadeOut(VGroup(title, underline), shift=UP * 0.25),
            FadeOut(final, shift=UP * 0.15),
            ReplacementTransform(pmv, pmv_hero),
            run_time=1.4, rate_func=rate_functions.ease_in_out_cubic,
        )                         # hold the win — then interrupt it

        self.pmv_hero = pmv_hero

    # ===================================================================== A1
    def act1_the_unfinished_ledger(self):
        # The conserved-quantities ledger — exactly as scene_1 left it:
        # momentum settled, energy never resolved.

        ene_word = Text("ENERGY", font=FONT, font_size=26, weight=BOLD,
                        color=COLOR_ENERGY).set_z_index(8)

        self.play(FadeIn(ene_word, shift=RIGHT * 0.12),
                  run_time=1.1, rate_func=rate_functions.ease_out_cubic)

        # Keynote move: the won formula docks top-left (scoreboard pattern);
        # don't cut — make room for the thread we're about to pull.
        pmv_dock = MathTex("p", "=", "m", "v", font_size=34)
        pmv_dock[0].set_color(COLOR_MOMENTUM)
        pmv_dock[2].set_color(COLOR_MASS)
        pmv_dock[3].set_color(COLOR_VEL)
        pmv_dock.to_corner(UL, buff=0.55).set_z_index(10)
        dock_pill = pill_bg(pmv_dock).set_z_index(9)
        self.play(
            FadeIn(dock_pill),
            ReplacementTransform(self.pmv_hero, pmv_dock),
            rate_func=rate_functions.ease_in_out_cubic)
        self.dock = VGroup(dock_pill, pmv_dock)

        # The energy row floats up to centre stage; the ledger withdraws.
        energy_stage = Text("ENERGY", font=FONT, font_size=46, weight=BOLD,
                            color=COLOR_ENERGY).move_to(UP * 2.45
                            ).set_z_index(8)
        question = Text("Why wasn't energy enough?", font=FONT, font_size=34,
                        weight=BOLD, color=COLOR_WHITE
                        ).move_to(UP * 1.45).set_z_index(8)
        self.play(
            ReplacementTransform(ene_word, energy_stage),
            rate_func=rate_functions.ease_in_out_cubic)
        
        self.play(FadeIn(question, shift=DOWN * 0.15), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)                          # "oh right — we never finished that"

        self.energy_stage, self.question = energy_stage, question

    # ── Act 2 internals ──────────────────────────────────────────────────
    def _energy_pill(self, pos):
        val = MathTex(r"E = 8\ \text{J}", font_size=34, color=COLOR_ENERGY)
        val.move_to(pos)
        bg = pill_bg(val)
        g = VGroup(bg, val).set_z_index(8)
        g.val = val
        return g

    # ===================================================================== A2
    def act2_same_number_different_story(self):
        # ── Stage: two collisions, side by side, top-down. Same gold number.
        # The ENERGY word splits into the two identical readouts (no cut).
        eL = self._energy_pill(np.array([-3.55, 1.95, 0]))
        eR = self._energy_pill(np.array([3.55, 1.95, 0]))
        divider = DashedLine(UP * 3.2, DOWN * 3.2, color=COLOR_GROUND,
                             stroke_width=1.5, stroke_opacity=0.35,
                             dash_length=0.18)
        self.play(
            FadeOut(self.question, shift=UP * 0.15),
            TransformFromCopy(self.energy_stage, eL),
            TransformFromCopy(self.energy_stage, eR),
            FadeOut(self.energy_stage),
            Create(divider),
            run_time=1.2, rate_func=rate_functions.ease_in_out_cubic,
        )

        cap_L = Text("head-on", font=FONT, font_size=22, color=COLOR_GROUND
                     ).move_to(self.LC + DOWN * 2.0).set_z_index(8)
        cap_R = Text("at an angle", font=FONT, font_size=22, color=COLOR_GROUND
                     ).move_to(self.RC + DOWN * 2.0).set_z_index(8)

        # left panel — 1D head-on
        lA0 = self.LC + LEFT * 1.95
        lB0 = self.LC + RIGHT * 1.95
        lA = make_pool_ball(COLOR_CUE, self.R2).move_to(lA0).set_z_index(5)
        lB = make_pool_ball(COLOR_TARGET, self.R2).move_to(lB0).set_z_index(5)

        # right panel — 2D, honest elastic numbers (see header flag #3)
        vA_s, vB_s = self.VA_IN * self.KS, self.VB_IN * self.KS
        vAo_s, vBo_s = self.VA_OUT * self.KS, self.VB_OUT * self.KS
        T_PRE, T_POST = 1.2, 1.15
        rA0 = self.RC - vA_s * T_PRE
        rB0 = self.RC - vB_s * T_PRE
        hatA = vA_s / np.linalg.norm(vA_s)
        hatB = vB_s / np.linalg.norm(vB_s)
        rA_stop = self.RC - hatA * 0.22
        rB_stop = self.RC - hatB * 0.22
        rA = make_pool_ball(COLOR_CUE, self.R2).move_to(rA0).set_z_index(5)
        rB = make_pool_ball(COLOR_TARGET, self.R2).move_to(rB0).set_z_index(5)

        self.play(LaggedStart(*[FadeIn(b, scale=0.85)
                                for b in (lA, lB, rA, rB)], lag_ratio=0.12),
                  FadeIn(cap_L, shift=UP * 0.08), FadeIn(cap_R, shift=UP * 0.08),
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        # BOTH collisions run at once — same instant, two different worlds.
        # Free travel = constant velocity = linear. Honest.
        self.play(
            lA.animate(rate_func=linear).move_to(self.LC + LEFT * 0.21),
            lB.animate(rate_func=linear).move_to(self.LC + RIGHT * 0.21),
            rA.animate(rate_func=linear).move_to(rA_stop),
            rB.animate(rate_func=linear).move_to(rB_stop),
            run_time=T_PRE,
        )
        ring_l = impact_ring(self.LC)
        ring_r = impact_ring(self.RC)
        self.add(ring_l, ring_r)
        self.play(
            ring_l.animate(rate_func=rate_functions.ease_out_quad)
                  .scale(9).set_stroke(opacity=0.0),
            ring_r.animate(rate_func=rate_functions.ease_out_quad)
                  .scale(9).set_stroke(opacity=0.0),
            run_time=0.32,
        )
        self.remove(ring_l, ring_r)
        self.play(
            lA.animate(rate_func=linear).move_to(lA0),      # straight back
            lB.animate(rate_func=linear).move_to(lB0),
            rA.animate(rate_func=linear).move_to(rA_stop + vAo_s * T_POST),
            rB.animate(rate_func=linear).move_to(rB_stop + vBo_s * T_POST),
            run_time=T_POST,
        )

        # Same gold number, two completely different outcomes. Let it sink in.
        # >>> POST: drop the music here — twin "8 J" in silence.
        self.play(VGroup(eL.val, eR.val).animate.scale(1.14), run_time=0.7,
                  rate_func=rate_functions.there_and_back)
        self.wait()

        no_dir = Text("Energy is just a number. No direction.", font=FONT,
                      font_size=28, color=COLOR_WHITE
                      ).move_to(UP * 3.05).set_z_index(9)
        self.play(FadeIn(no_dir, shift=UP * 0.12), run_time=0.6,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait()

        # >>> EDIT (Premiere): optional 1–2 s real top-down break/scatter clip
        #     lands HERE — real chaos, then cut back to our clean vectors.

        # ── Momentum's turn. Dim the energy world; lean into the right panel.
        energy_world = VGroup(eL, eR, cap_L, divider, lA, lB)
        self.play(
            FadeOut(no_dir, shift=DOWN * 0.1),
            energy_world.animate.set_opacity(0.15),
            self.camera.frame.animate.move_to([2.7, 0.45, 0]).set(width=10.5),
            run_time=1.3, rate_func=rate_functions.ease_in_out_cubic,
        )

        # The system resets ITSELF — the same two balls glide back (scene_1's
        # promise motif), ready to be interrogated properly this time.
        self.play(rA.animate.move_to(rA0), rB.animate.move_to(rB0),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)

        # incoming momenta, drawn ON the balls (length ∝ |p|)
        lenA_in = float(np.linalg.norm(self.VA_IN)) * self.PS
        lenB_in = float(np.linalg.norm(self.VB_IN)) * self.PS
        arrA_in = vec_arrow(rA.get_center() + hatA * 0.26, hatA * lenA_in,
                            COLOR_P_A).set_z_index(6)
        arrB_in = vec_arrow(rB.get_center() + hatB * 0.26, hatB * lenB_in,
                            COLOR_P_B).set_z_index(6)
        self.play(GrowArrow(arrA_in), GrowArrow(arrB_in), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        # Tip-to-tail addition in the lane above — momentum is a VECTOR,
        # so the addition is drawn as arrows (scene_3's grammar).
        pA_in = self.VA_IN * self.PS
        pB_in = self.VB_IN * self.PS
        lane1 = vec_arrow(self.Q0, pA_in, COLOR_P_A, sw=5).set_z_index(7)
        lane2 = vec_arrow(self.Q0 + pA_in, pB_in, COLOR_P_B, sw=5
                          ).set_z_index(7)
        self.play(TransformFromCopy(arrA_in, lane1),
                  TransformFromCopy(arrB_in, lane2),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_cubic)

        P_tot = pA_in + pB_in                     # = (1.8, 0): dead horizontal
        under = vec_arrow(self.Q0, P_tot, COLOR_WHITE, sw=10
                          ).set_opacity(0.28).set_z_index(7)
        res_before = vec_arrow(self.Q0, P_tot, COLOR_MOMENTUM, sw=6
                               ).set_z_index(8)
        res_lab = MathTex(r"P_{\text{total}}", font_size=28,
                          color=COLOR_MOMENTUM)
        res_lab.next_to(self.Q0, LEFT, buff=0.30).set_z_index(8)
        self.play(GrowArrow(under), GrowArrow(res_before),
                  FadeIn(res_lab, shift=RIGHT * 0.1),
                  run_time=0.8, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.7)

        # Park the BEFORE resultant as a ghost; clear the scaffolding.
        self.play(FadeOut(lane1), FadeOut(lane2), FadeOut(under),
                  FadeOut(arrA_in), FadeOut(arrB_in),
                  res_before.animate.set_opacity(0.32),
                  run_time=0.5, rate_func=rate_functions.ease_in_out_sine)

        # Run the collision again, for real, under the parked prediction.
        self.play(rA.animate(rate_func=linear).move_to(rA_stop),
                  rB.animate(rate_func=linear).move_to(rB_stop),
                  run_time=T_PRE)
        ring = impact_ring(self.RC)
        self.add(ring)
        self.play(ring.animate(rate_func=rate_functions.ease_out_quad)
                  .scale(9).set_stroke(opacity=0.0), run_time=0.30)
        self.remove(ring)
        self.play(rA.animate(rate_func=linear)
                  .move_to(rA_stop + vAo_s * T_POST),
                  rB.animate(rate_func=linear)
                  .move_to(rB_stop + vBo_s * T_POST),
                  run_time=T_POST)

        # outgoing momenta, on the scattered balls
        hatAo = vAo_s / np.linalg.norm(vAo_s)
        hatBo = vBo_s / np.linalg.norm(vBo_s)
        lenA_o = float(np.linalg.norm(self.VA_OUT)) * self.PS
        lenB_o = float(np.linalg.norm(self.VB_OUT)) * self.PS
        arrA_o = vec_arrow(rA.get_center() + hatAo * 0.26, hatAo * lenA_o,
                           COLOR_P_A).set_z_index(6)
        arrB_o = vec_arrow(rB.get_center() + hatBo * 0.26, hatBo * lenB_o,
                           COLOR_P_B).set_z_index(6)
        self.play(GrowArrow(arrA_o), GrowArrow(arrB_o), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)

        pA_out = self.VA_OUT * self.PS
        pB_out = self.VB_OUT * self.PS
        lane3 = vec_arrow(self.Q0, pA_out, COLOR_P_A, sw=5).set_z_index(7)
        lane4 = vec_arrow(self.Q0 + pA_out, pB_out, COLOR_P_B, sw=5
                          ).set_z_index(7)
        self.play(TransformFromCopy(arrA_o, lane3),
                  TransformFromCopy(arrB_o, lane4),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_cubic)

        # The AFTER resultant grows — and lands exactly on the ghost.
        res_after = vec_arrow(self.Q0, P_tot, COLOR_MOMENTUM, sw=6
                              ).set_z_index(9)
        self.play(GrowArrow(res_after), run_time=0.8,
                  rate_func=rate_functions.ease_out_cubic)
        # >>> POST: the clean confirming TICK + this white flash = money moment.
        snap = Line(self.Q0, self.Q0 + P_tot, color=COLOR_WHITE,
                    stroke_width=9).set_z_index(10)
        tick = check_mark(COLOR_TICK, 0.55).next_to(self.Q0 + P_tot, RIGHT,
                                                    buff=0.35).set_z_index(10)
        self.play(ShowPassingFlash(snap, time_width=0.7),
                  Flash(self.Q0 + P_tot / 2, color=COLOR_WHITE,
                        line_length=0.16, num_lines=12, flash_radius=0.45,
                        line_stroke_width=2.2),
                  run_time=0.8)
        self.play(Create(tick), run_time=0.4,
                  rate_func=rate_functions.ease_out_back)
        self.wait(0.5)        # the arrow predicted it; the number couldn't

        self._clear_to_grid(run_time=1.0, keep=(self.dock,))
        self.play(Restore(self.camera.frame), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)

    # ===================================================================== A3
    def act3_transfer_vs_transform(self):
        by = self.TRACK_Y + self.R3

        # spare stage: one quiet track line
        track = Line([-6.6, self.TRACK_Y, 0], [6.6, self.TRACK_Y, 0],
                     color=COLOR_GROUND, stroke_width=2.5,
                     stroke_opacity=0.55).set_z_index(1)
        self.play(Create(track), run_time=0.6,
                  rate_func=rate_functions.ease_in_out_sine)

        # ── PART 1 · energy's leak ────────────────────────────────────────
        kA = make_pool_ball(COLOR_CUE, self.R3).move_to([-4.7, by, 0]
                                                        ).set_z_index(5)
        kB = make_pool_ball(COLOR_TARGET, self.R3).move_to([1.1, by, 0]
                                                           ).set_z_index(5)
        e8 = MathTex(r"E_{\text{kinetic}} = 8\ \text{J}", font_size=36,
                     color=COLOR_ENERGY).move_to(UP * 1.95)
        e_pill = pill_bg(e8).set_z_index(7)
        e8.set_z_index(8)
        self.play(LaggedStart(FadeIn(kA, scale=0.85), FadeIn(kB, scale=0.85),
                              lag_ratio=0.2),
                  FadeIn(e_pill), FadeIn(e8, shift=DOWN * 0.1),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)

        contact_x = 1.1 - 2 * self.R3
        self.play(kA.animate(rate_func=linear).move_to([contact_x, by, 0]),
                  run_time=1.5)

        # IMPACT · the gold takes the hit and SPRINGS BITS OFF ITSELF:
        # red wiggles (heat) + pale rings (sound), and the number ticks down.
        # >>> EDIT (Premiere): optional thermal-cam impact undercut HERE.
        # >>> POST: small sizzle/hiss as the red bits escape.
        cp = np.array([1.1 - self.R3, by, 0.0])
        ring = impact_ring(cp)
        wiggles = VGroup(
            heat_wiggle(cp, np.array([-0.55, 1.0, 0])),
            heat_wiggle(cp, np.array([0.05, 1.0, 0])),
            heat_wiggle(cp, np.array([0.65, 0.85, 0])),
        ).set_z_index(7)
        s_ring1 = impact_ring(cp, color=COLOR_SOUND, r0=0.10, sw=2.5)
        s_ring2 = impact_ring(cp, color=COLOR_SOUND, r0=0.10, sw=2.5)
        e7 = MathTex(r"E_{\text{kinetic}} = 7\ \text{J}", font_size=36,
                     color=COLOR_ENERGY).move_to(e8).set_z_index(8)

        self.add(ring, s_ring1)
        self.play(
            ring.animate(rate_func=rate_functions.ease_out_quad)
                .scale(9).set_stroke(opacity=0.0),
            s_ring1.animate(rate_func=rate_functions.ease_out_sine)
                   .scale(14).set_stroke(opacity=0.0),
            LaggedStart(*[Create(w) for w in wiggles], lag_ratio=0.15),
            ReplacementTransform(e8, e7),
            run_time=0.8,
        )
        self.remove(ring, s_ring1)
        self.add(s_ring2)
        # heat drifts away and dies; the sticky pair limps off together
        self.play(
            *[w.animate(rate_func=rate_functions.ease_out_sine)
              .shift((w.get_end() - w.get_start()) * 0.9).set_opacity(0.0)
              for w in wiggles],
            s_ring2.animate(rate_func=rate_functions.ease_out_sine)
                   .scale(20).set_stroke(opacity=0.0),
            kA.animate(rate_func=linear).shift(RIGHT * 1.5),
            kB.animate(rate_func=linear).shift(RIGHT * 1.5),
            run_time=1.2,
        )
        self.remove(s_ring2, wiggles)

        cap1 = Text("Energy didn't vanish. It changed form.", font=FONT,
                    font_size=28, color=COLOR_WHITE
                    ).move_to(DOWN * 3.0).set_z_index(9)
        self.play(FadeIn(cap1, shift=UP * 0.12), run_time=0.6,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(1.3)

        # ── PART 2 · momentum's handoff (the baton) ───────────────────────
        self.play(FadeOut(VGroup(kA, kB, e_pill, e7)),
                  FadeOut(cap1, shift=DOWN * 0.1),
                  run_time=0.7, rate_func=rate_functions.ease_in_out_sine)

        hA = make_pool_ball(COLOR_CUE, self.R3).move_to([-4.7, by, 0]
                                                        ).set_z_index(5)
        hB = make_pool_ball(COLOR_TARGET, self.R3).move_to([0.9, by, 0]
                                                           ).set_z_index(5)
        self.play(LaggedStart(FadeIn(hA, scale=0.85), FadeIn(hB, scale=0.85),
                              lag_ratio=0.2),
                  run_time=0.7, rate_func=rate_functions.ease_out_cubic)

        P_LEN = 1.45
        p_arrow = Arrow([hA.get_center()[0] - 0.1, self.ROW_Y, 0],
                        [hA.get_center()[0] - 0.1 + P_LEN, self.ROW_Y, 0],
                        buff=0, color=COLOR_MOMENTUM, stroke_width=6,
                        max_tip_length_to_length_ratio=0.22).set_z_index(6)
        self.play(GrowArrow(p_arrow), run_time=0.6,
                  rate_func=rate_functions.ease_out_cubic)
        p_arrow.add_updater(lambda a: a.put_start_and_end_on(
            np.array([hA.get_center()[0] - 0.1, self.ROW_Y, 0]),
            np.array([hA.get_center()[0] - 0.1 + P_LEN, self.ROW_Y, 0])))

        h_contact = 0.9 - 2 * self.R3
        self.play(hA.animate(rate_func=linear).move_to([h_contact, by, 0]),
                  run_time=1.4)
        p_arrow.clear_updaters()

        # THE HANDOFF · the arrow slides cleanly from A to B — one object,
        # no bits, no form change, length pixel-for-pixel preserved.
        # >>> POST: the clean, satisfying CLINK lands on this glide.
        h_ring = impact_ring(np.array([0.9 - self.R3, by, 0.0]))
        self.add(h_ring)
        self.play(
            h_ring.animate(rate_func=rate_functions.ease_out_quad)
                  .scale(9).set_stroke(opacity=0.0),
            p_arrow.animate(rate_func=rate_functions.ease_in_out_cubic)
                   .put_start_and_end_on(
                       np.array([hB.get_center()[0] - 0.1, self.ROW_Y, 0]),
                       np.array([hB.get_center()[0] - 0.1 + P_LEN,
                                 self.ROW_Y, 0])),
            run_time=0.5,
        )
        self.remove(h_ring)
        p_arrow.add_updater(lambda a: a.put_start_and_end_on(
            np.array([hB.get_center()[0] - 0.1, self.ROW_Y, 0]),
            np.array([hB.get_center()[0] - 0.1 + P_LEN, self.ROW_Y, 0])))
        self.play(hB.animate(rate_func=linear).shift(RIGHT * 2.5),
                  run_time=1.3)
        p_arrow.clear_updaters()

        proof = Line(p_arrow.get_start(), p_arrow.get_end(),
                     color=COLOR_WHITE, stroke_width=8).set_z_index(7)
        self.play(ShowPassingFlash(proof, time_width=0.7), run_time=0.7)

        cap2 = Text("Momentum doesn't change form. It changes hands.",
                    font=FONT, font_size=28, color=COLOR_WHITE
                    ).move_to(DOWN * 3.0).set_z_index(9)
        self.play(FadeIn(cap2, shift=UP * 0.12), run_time=0.6,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(1.4)                # energy hides; momentum is honest

        self._clear_to_grid(run_time=0.9, keep=(self.dock,))

    # ===================================================================== A4
    def act4_the_chain(self):
        # The convergence montage. Every element is a RETURN — nothing new.
        # Tempo accelerates link by link: tick… tick… tick-thunk.
        y = self.CHAIN_Y

        # link 1 · m alone — and the scene_2 verdict, stamped small
        m_tok = MathTex("m", font_size=84, color=COLOR_MASS
                        ).move_to([-4.9, y, 0]).set_z_index(8)
        self.play(FadeIn(m_tok, scale=0.8), run_time=0.9,
                  rate_func=rate_functions.ease_out_cubic)
        st_txt = Text("INCOMPLETE", font=FONT, font_size=14, weight=BOLD,
                      color=COLOR_RED)
        st_box = SurroundingRectangle(st_txt, color=COLOR_RED, buff=0.07,
                                      stroke_width=2)
        stamp = VGroup(st_txt, st_box).rotate(10 * DEGREES)
        stamp.move_to(m_tok.get_center() + UR * 0.55).set_z_index(9)
        self.play(FadeIn(stamp.scale(1.7)), run_time=0.01)   # scene_2's slam
        self.play(stamp.animate.scale(1 / 1.7), run_time=0.22,
                  rate_func=rate_functions.ease_in_quad)
        self.play(m_tok.animate.set_opacity(0.45),           # mass alone: mute
                  stamp.animate.set_opacity(0.45),
                  run_time=0.4, rate_func=rate_functions.ease_in_out_sine)
        # >>> POST: chain click #1.

        # link 2 · v flies in (the 40 vs 100 km/h lesson, condensed to a glyph)
        v_arrow = Arrow([-3.85, y - 0.05, 0], [-2.55, y - 0.05, 0], buff=0,
                        color=COLOR_VEL, stroke_width=6,
                        max_tip_length_to_length_ratio=0.20).set_z_index(8)
        v_lab = MathTex("v", font_size=48, color=COLOR_VEL
                        ).next_to(v_arrow, UP, buff=0.18).set_z_index(8)
        v_grp = VGroup(v_arrow, v_lab)
        self.play(FadeIn(v_grp, shift=LEFT * 2.0), run_time=0.8,
                  rate_func=rate_functions.ease_out_cubic)
        # >>> POST: chain click #2.

        # link 3 · the fuse: m × v → p  (scene_3's naming, replayed in 1.3 s)
        self.play(m_tok.animate.set_opacity(1.0), FadeOut(stamp, scale=0.6),
                  run_time=0.35, rate_func=rate_functions.ease_out_sine)
        mxv = MathTex("m", r"\times", "v", font_size=64
                      ).move_to([-1.7, y, 0]).set_z_index(8)
        mxv[0].set_color(COLOR_MASS)
        mxv[2].set_color(COLOR_VEL)
        self.play(ReplacementTransform(m_tok, mxv[0]),
                  FadeIn(mxv[1], scale=0.5),
                  ReplacementTransform(v_grp, mxv[2]),
                  run_time=0.7, rate_func=rate_functions.ease_in_out_cubic)
        p_tok = MathTex("p", font_size=88, color=COLOR_MOMENTUM
                        ).move_to([-1.7, y, 0]).set_z_index(8)
        self.play(ReplacementTransform(mxv, p_tok),
                  Flash([-1.7, y, 0], color=COLOR_MOMENTUM, line_length=0.16,
                        num_lines=10, flash_radius=0.5, line_stroke_width=2.2),
                  run_time=0.55, rate_func=rate_functions.ease_in_out_cubic)
        # >>> POST: chain click #3.

        # link 4 · the gate: scene_5's equal-and-opposite pair clamps on
        gate_x = 1.1
        gL = Arrow([gate_x - 1.55, y, 0], [gate_x - 0.42, y, 0], buff=0,
                   color=COLOR_RED, stroke_width=6,
                   max_tip_length_to_length_ratio=0.20).set_z_index(7)
        gR = Arrow([gate_x + 1.55, y, 0], [gate_x + 0.42, y, 0], buff=0,
                   color=COLOR_RED, stroke_width=6,
                   max_tip_length_to_length_ratio=0.20).set_z_index(7)
        self.play(p_tok.animate.move_to([gate_x, y, 0]), run_time=0.5,
                  rate_func=rate_functions.ease_in_out_cubic)
        self.play(GrowArrow(gL), GrowArrow(gR), run_time=0.4,
                  rate_func=rate_functions.ease_out_cubic)
        # the scene_5 lock: both snap a hair past, settle TOGETHER
        self.play(gL.animate.scale(1.06, about_point=p_tok.get_center()),
                  gR.animate.scale(1.06, about_point=p_tok.get_center()),
                  run_time=0.14, rate_func=rate_functions.ease_out_quad)
        self.play(gL.animate.scale(1 / 1.06, about_point=p_tok.get_center()),
                  gR.animate.scale(1 / 1.06, about_point=p_tok.get_center()),
                  run_time=0.14, rate_func=rate_functions.ease_in_out_sine)
        # >>> POST: chain click #4.

        # link 5 · out the other side: CONSERVED. — the thunk
        conserved = Text("CONSERVED.", font=FONT, font_size=34, weight=BOLD,
                         color=COLOR_WHITE).move_to([4.35, y, 0]
                         ).set_z_index(8)
        tick_v = check_mark(COLOR_MOMENTUM, 0.55).next_to(conserved, DOWN,
                                                          buff=0.32)
        tick_v.set_z_index(8)
        self.play(p_tok.animate.move_to([2.55, y, 0]), run_time=0.4,
                  rate_func=rate_functions.ease_in_quad)   # accelerating out
        self.play(ReplacementTransform(p_tok, conserved),
                  Create(tick_v),
                  Flash([4.35, y, 0], color=COLOR_MOMENTUM, line_length=0.18,
                        num_lines=12, flash_radius=0.8, line_stroke_width=2.4),
                  run_time=0.55, rate_func=rate_functions.ease_out_back)
        # >>> POST: the resolving chord — tick… tick… tick-THUNK.
        self.wait()               # dominoes you pushed, fallen in sequence

        self._gate = VGroup(gL, gR)

    # ===================================================================== A5
    def act5_elevation(self):
        # ── Strip the world. Near-black. Then build the formula FROM the
        #    argument, not from memory. ──

        leftovers = Group(*[m for m in self.mobjects if m is not self.grid])
        self.play(FadeOut(leftovers),
                  rate_func=rate_functions.ease_in_out_sine)

        # The three argument-pieces of Act 4, dim, waiting in the dark.
        piece_mv = MathTex("m", r"\cdot", "v", font_size=40
                           ).move_to([-3.2, 1.3, 0]).set_z_index(8)
        piece_mv[0].set_color(COLOR_MASS)
        piece_mv[2].set_color(COLOR_VEL)
        gl = Arrow([2.5, 1.1, 0], [3.1, 1.1, 0], buff=0, color=COLOR_RED,
                   stroke_width=5, max_tip_length_to_length_ratio=0.35)
        gr = Arrow([3.9, 1.1, 0], [3.3, 1.1, 0], buff=0, color=COLOR_RED,
                   stroke_width=5, max_tip_length_to_length_ratio=0.35)
        piece_gate = VGroup(gl, gr).set_z_index(8)

        for p in (piece_mv, piece_gate):
            p.set_opacity(0.55)
        self.play(LaggedStart(FadeIn(piece_mv, shift=DOWN * 0.1),
                              FadeIn(piece_gate, shift=DOWN * 0.1),
                              lag_ratio=0.25),
                  rate_func=rate_functions.ease_out_sine)
        self.wait(0.5)

        # THE SNAP · the conserved tick becomes p; the equal-and-opposite
        # pair becomes the two bars of "="; the merged mv takes its seat.
        # >>> POST: one clean, resonant tone lands exactly on this click.
        eq = MathTex("p", "=", "m", "v", font_size=84
                     ).move_to(ORIGIN).set_z_index(9)
        eq[0].set_color(COLOR_MOMENTUM)
        eq[2].set_color(COLOR_MASS)
        eq[3].set_color(COLOR_VEL)
        self.play(FadeIn(eq[0], shift=UP * 0.12),
            ReplacementTransform(piece_gate, eq[1]),
            ReplacementTransform(piece_mv[0], eq[2]),
            ReplacementTransform(piece_mv[2], eq[3]),
            FadeOut(piece_mv[1], scale=0.3),
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(Flash(eq.get_center(), color=COLOR_WHITE, line_length=0.20,
                        num_lines=14, flash_radius=1.1, line_stroke_width=2.2),
                  run_time=0.5)

        # the living glow — rides the equation from here to the end of the act
        self.glow_op = ValueTracker(0.10)
        glow = always_redraw(lambda: Ellipse(
            width=eq.width + 1.7, height=eq.height + 1.3,
            fill_color=COLOR_MOMENTUM, fill_opacity=self.glow_op.get_value(),
            stroke_width=0).move_to(eq.get_center()).set_z_index(-1))
        self.add(glow)
        self.glow, self.eq = glow, eq
        self.wait(0.6)

        # ── The re-frame: MEMORIZE → struck → a conclusion → a necessity →
        #    it had to be. Each phrase replaces the last in the same spot. ──
        mem = Text("MEMORIZE", font=FONT, font_size=32, weight=BOLD,
                   color=COLOR_GROUND).next_to(eq, UP, buff=0.9).set_z_index(9)
        self.play(FadeIn(mem, shift=DOWN * 0.1), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)
        strike = Line(mem.get_left() + LEFT * 0.12,
                      mem.get_right() + RIGHT * 0.12,
                      color=COLOR_RED, stroke_width=4).set_z_index(10)
        self.play(Create(strike), run_time=0.4)
        self.wait(0.5)

        ph1 = Text("A conclusion.", font=FONT, font_size=30, slant=ITALIC,
                   color=COLOR_WHITE).move_to(mem).set_z_index(9)
        ph2 = Text("A necessity.", font=FONT, font_size=30, slant=ITALIC,
                   color=COLOR_WHITE).move_to(mem).set_z_index(9)
        ph3 = Text("It had to be.", font=FONT, font_size=30, slant=ITALIC,
                   color=COLOR_WHITE).move_to(mem).set_z_index(9)
        self.play(ReplacementTransform(VGroup(mem, strike), ph1),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.9)
        self.play(ReplacementTransform(ph1, ph2), run_time=0.7,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.9)
        self.play(ReplacementTransform(ph2, ph3), run_time=0.7,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)

        # ── THE HELD FRAME · no motion but a single slow breath of glow.
        #    >>> POST: drop the bed to near-silence HERE. The silence IS the
        #    sound design. Do not rush off this. ──
        self.play(self.glow_op.animate.set_value(0.20), run_time=1.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(self.glow_op.animate.set_value(0.10), run_time=1.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.2)

        self.ph3 = ph3

    # ===================================================================== A6
    def act6_teaser(self):
        eq = self.eq

        # Wake the frame: the formula recedes; its hero arrow steps forward.
        self.play(
            FadeOut(self.ph3, shift=UP * 0.12),
            self.glow_op.animate.set_value(0.0),
            eq.animate.scale(0.55).to_edge(UP, buff=0.9).set_opacity(0.40),
            run_time=1.1, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.glow.clear_updaters()
        self.remove(self.glow)

        straight = Arrow(LEFT * 1.5 + DOWN * 0.25, RIGHT * 1.5 + DOWN * 0.25,
                         buff=0, color=COLOR_MOMENTUM, stroke_width=6,
                         max_tip_length_to_length_ratio=0.14).set_z_index(8)
        self.play(GrowArrow(straight), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.6)

        # ── BEND IT · line → arc → circle. The straight-line story visibly
        #    curves into a new, unanswered shape. ──
        # >>> POST: gentle rising motion-whoosh across these two morphs.
        bend = ArcBetweenPoints(LEFT * 1.35 + DOWN * 0.55,
                                RIGHT * 1.35 + DOWN * 0.55,
                                angle=-PI * 0.55)
        bend.set_stroke(COLOR_MOMENTUM, width=6).add_tip(tip_length=0.24)
        bend.set_color(COLOR_MOMENTUM)
        bend.set_z_index(8)
        self.play(ReplacementTransform(straight, bend),
                  rate_func=rate_functions.ease_in_out_cubic)

        circle_arrow = Arc(radius=1.15, start_angle=PI / 2, angle=-TAU * 0.86,
                           arc_center=DOWN * 0.25)
        circle_arrow.set_stroke(COLOR_MOMENTUM, width=6).add_tip(
            tip_length=0.24)
        circle_arrow.set_color(COLOR_MOMENTUM)
        circle_arrow.set_z_index(8)
        self.play(ReplacementTransform(bend, circle_arrow), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_cubic)

        # one faint mote rides the new shape once — orbiting, not travelling.
        # Clockwise from the top, back to the top (matches circle_arrow's spin).
        mote = Dot(radius=0.07, color=COLOR_MOMENTUM, fill_opacity=0.85
                   ).set_z_index(9)
        loop = Arc(radius=1.15, start_angle=PI / 2, angle=-TAU,
                   arc_center=DOWN * 0.25)
        mote.move_to(loop.point_from_proportion(0.0))
        self.add(mote)
        self.play(MoveAlongPath(mote, loop), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)

        q = Text("What about spin?", font=FONT, font_size=28,
                 color=COLOR_WHITE).move_to(UP * 1.55).set_z_index(9)
        self.play(FadeIn(q, shift=DOWN * 0.12), run_time=0.8,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(1.4)                          # the itch. leave the door ajar.

        # drift off-frame; the question stays open
        self.play(
            FadeOut(circle_arrow, shift=UP * 0.4),
            FadeOut(mote, shift=UP * 0.4),
            FadeOut(q, shift=UP * 0.2),
            FadeOut(eq, shift=UP * 0.2),
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine,
        )

        endcard = Text("Next: when momentum goes in circles.", font=FONT,
                       font_size=24, slant=ITALIC, color=COLOR_GROUND
                       ).move_to(ORIGIN).set_z_index(9)
        self.play(FadeIn(endcard, shift=UP * 0.1), run_time=1.0,
                  rate_func=rate_functions.ease_out_sine)
        self.wait(1.8)
        # >>> POST: outro sting / channel music; branded outro card in Premiere.
        self.play(FadeOut(endcard), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)