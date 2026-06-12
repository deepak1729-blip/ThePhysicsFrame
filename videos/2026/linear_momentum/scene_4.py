from manim import *
import numpy as np

#  ════════════════════════════════════════════════════════════════════════
#  SCENE 4 — "THE DERIVATION"   (linear_momentum series)
#
#  ASSETS REQUIRED: none. This scene is 100% drawn Manim — no images, no
#  video, no fonts beyond the series stack.
#
#  >>> EDIT (Premiere):
#  · Act 5 — OPTIONAL 1–2 s real clip: a person pushing a stalled car,
#    side-on (steady force over a long time slowly building real speed).
#    If used, undercut it UNDER the Manim comparison, never instead of it.
#    Skip if the pure ball demo already lands — it probably does.
#
#  >>> POST (audio):
#  · Act 4 — drop the music to near-silence on the still equation; ONE soft
#    sub-bass "thoom" exactly as m·Δv ignites violet. Nothing else.
#  · Act 6 — one clean typographic "tick" as the IMPULSE tag lands.
#    Then silence into the Scene-5 transition.
#
#  FLAGGED DECISIONS (veto any of these in chat):
#  1. COLOR RECONCILIATION — the brief casts momentum=gold / impulse=violet,
#     but the series protocol locked in Scenes 2–3 already owns both hues:
#     violet #C66BFF IS momentum (three scenes of equity), amber-gold
#     #F4B642 IS mass. So: momentum-change keeps series VIOLET, and impulse
#     debuts in a genuinely new color — magenta #FF5FA2. Same dramaturgy
#     (ignition + christening), reconciled palette.
#  2. Δt gets a new quiet color: slate-green #8FB3A6 (COLOR_TIME). Greyer
#     than tick-green and energy-green — no collision.
#  3. 'a' wears a temporary teal #49C5BB — deliberately NEAR cyan, because
#     in Act 2 it unpacks into Δv/Δt. The hue is the foreshadow.
#  4. Act 0 added (series convention): rebuilds scene_3's exact closing
#     frame — the hanging WHY? — so F = ma arrives as the answer reached
#     for, not a cold open.
#  5. Act 5 "orange ball" → mass-amber ball (it's a generic massive object;
#     amber is what mass looks like in this series).
#  6. "values visibly scaling in lockstep" → twin meter bars expanding
#     symmetrically under each side of the equation, driven by ONE tracker.
#     Cleaner than live numbers, and the single tracker makes the lockstep
#     literal.
#  7. New helper: make_clock() — time gains a face this scene; built in the
#     series stroke/pill vocabulary.
#  ════════════════════════════════════════════════════════════════════════

# ── BRAND PALETTE (series canvas, verbatim) ──
COLOR_BG     = "#0E1117"
COLOR_GROUND = "#8E8E93"
COLOR_WHITE  = "#E5E5EA"
COLOR_DIM    = "#3A3F47"

# ── MOMENTUM SERIES COLOR PROTOCOL (locked in scene_2) ──
COLOR_MASS     = "#F4B642"   # mass m — warm amber/gold
COLOR_VEL      = "#3FC8FF"   # velocity v — electric cyan, ALWAYS an arrow
COLOR_MOMENTUM = "#C66BFF"   # p / m·Δv — the series hero violet
COLOR_TICK     = "#34C759"   # confirmation green
COLOR_RED      = "#FF3B30"   # series UI red

# NEW this scene (flagged above)
COLOR_TIME    = "#8FB3A6"    # Δt — quiet slate-green, the "how long" element
COLOR_A_TMP   = "#49C5BB"    # 'a' — temporary teal; dissolves in Act 2
COLOR_IMPULSE = "#FF5FA2"    # F·Δt — christened magenta in Act 6

FONT = "Segoe UI"
config.background_color = COLOR_BG
RNG = np.random.default_rng(7)   # deterministic → stable render cache

EQ_Y = 0.45                      # the hero equation line, Acts 1–4


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
    """Top-down ball: base disc + sheen + specular (series shading)."""
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


def pill_bg(w, h, stroke=COLOR_GROUND):
    return RoundedRectangle(width=w, height=h, corner_radius=0.18,
                            stroke_color=stroke, stroke_width=1.4,
                            stroke_opacity=0.50,
                            fill_color="#11151C", fill_opacity=0.92)


def make_clock(radius=0.32, color=COLOR_TIME):
    """NEW helper (flagged) — time's face. Series pill fill, quiet stroke.
    Rotate clock.hand about clock.face.get_center() to run it."""
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
class Scene_4_TheDerivation(MovingCameraScene):

    def construct(self):
        self.camera.frame.save_state()
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.grid = grid

        self.act0_inherit_scene3()
        self.act1_the_tool()
        self.act2_crack_open_the_a()
        self.act3_time_crosses_the_bridge()
        self.act4_read_what_you_wrote()
        self.act5_more_push_more_time()
        self.act6_give_it_a_name()

    # ===================================================================== A0
    def act0_inherit_scene3(self):
        # Hard-cut continuity: rebuild scene_3's exact closing frame —
        # the unflinching claim and the hanging WHY?. No entrance.
        claim = MathTex(r"P_{\text{total}}", "=", r"\text{constant}",
                        font_size=60).move_to(ORIGIN).set_z_index(8)
        claim[0].set_color(COLOR_MOMENTUM)
        claim[2].set_color(COLOR_WHITE)
        why = Text("WHY?", font=FONT, font_size=92, weight=BOLD,
                   color=COLOR_WHITE).move_to(UP * 1.9).set_z_index(9)
        self.add(claim, why)
        self.wait(1.0)                       # the inherited itch

        # The claim steps aside; the question shrinks but keeps hanging —
        # it watches us go fetch the tool.
        self.play(
            FadeOut(claim, shift=DOWN * 0.3),
            why.animate.scale(0.42).move_to(UP * 3.15).set_opacity(0.22),
            run_time=1.3, rate_func=rate_functions.ease_in_out_sine,
        )
        self.why = why
        self.wait(0.4)

    # ===================================================================== A1
    def act1_the_tool(self):
        # F = ma arrives like a known tool off the shelf — pieces materialise
        # slightly apart, then slide together and lock.
        spots = [[-2.9, EQ_Y, 0], [-1.0, EQ_Y, 0], [0.9, EQ_Y, 0],
                 [2.8, EQ_Y, 0]]
        cols = [COLOR_WHITE, COLOR_WHITE, COLOR_MASS, COLOR_A_TMP]
        loose = VGroup(*[
            MathTex(s, font_size=84, color=c).move_to(p)
            for s, c, p in zip(["F", "=", "m", "a"], cols, spots)])
        self.play(LaggedStart(*[FadeIn(t, scale=0.85) for t in loose],
                              lag_ratio=0.12),
                  run_time=1.0, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        eq1 = MathTex("F", "=", "m", "a", font_size=84
                      ).move_to([0, EQ_Y, 0]).set_z_index(8)
        for i, c in enumerate(cols):
            eq1[i].set_color(c)
        self.play(*[ReplacementTransform(loose[i], eq1[i]) for i in range(4)],
                  run_time=1.1, rate_func=rate_functions.ease_in_out_cubic)
        # keynote settle: ~3% overshoot, then snap
        self.play(eq1.animate.scale(1.03), run_time=0.14,
                  rate_func=rate_functions.ease_out_quad)
        self.play(eq1.animate.scale(1 / 1.03), run_time=0.18,
                  rate_func=rate_functions.ease_in_out_sine)
        self.eq1 = eq1

        # Naming the tool, not lingering on it.
        tag = Text("NEWTON'S SECOND LAW", font=FONT, font_size=20,
                   color=COLOR_GROUND, weight=BOLD)
        tag.next_to(eq1, UP, buff=0.75).set_z_index(8)
        self.play(FadeIn(tag, shift=DOWN * 0.10), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(1.1)
        self.play(FadeOut(tag, shift=UP * 0.10),
                  FadeOut(self.why),          # the tool is in hand
                  run_time=0.7, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)                        # calm, familiar ground

    # ===================================================================== A2
    def act2_crack_open_the_a(self):
        eq1 = self.eq1
        a = eq1[3]

        # Interrogate the 'a' — one brief pulse: "this one."
        self.play(a.animate.scale(1.20).set_color("#7EEFE6"), run_time=0.35,
                  rate_func=rate_functions.ease_out_quad)
        self.play(a.animate.scale(1 / 1.20).set_color(COLOR_A_TMP),
                  run_time=0.40, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)

        # ── corner intuition inset: an arrow lengthening while a clock runs.
        #    That is all acceleration is. ──
        C = np.array([4.45, 2.35, 0.0])
        box = pill_bg(3.05, 1.95).move_to(C).set_z_index(9)
        a0 = C + LEFT * 1.20 + UP * 0.34
        vlen = ValueTracker(0.55)
        ins_arr = always_redraw(lambda: Arrow(
            a0, a0 + RIGHT * vlen.get_value(), buff=0, color=COLOR_VEL,
            stroke_width=5, max_tip_length_to_length_ratio=0.30
        ).set_z_index(10))
        clock = make_clock(0.30).move_to(C + DOWN * 0.44).set_z_index(10)

        self.play(FadeIn(box, scale=0.94), FadeIn(clock, scale=0.9),
                  run_time=0.7, rate_func=rate_functions.ease_out_cubic)
        self.add(ins_arr)
        # constant force → velocity grows LINEARLY with time; the clock and
        # the arrow share one honest linear ramp
        self.play(vlen.animate.set_value(2.25),
                  Rotate(clock.hand, -TAU * 0.65,
                         about_point=clock.face.get_center(),
                         rate_func=linear),
                  run_time=2.4, rate_func=linear)
        self.wait(0.7)                        # let "change over time" be felt
        ins_arr.clear_updaters()
        self.play(FadeOut(box), FadeOut(clock), FadeOut(ins_arr),
                  run_time=0.6, rate_func=rate_functions.ease_in_out_sine)

        # ── the unpack: ONLY the a-region expands. F, =, m do not move. ──
        cdot = MathTex(r"\cdot", font_size=84, color=COLOR_WHITE
                       ).next_to(eq1[2], RIGHT, buff=0.22).set_z_index(8)
        y_axis = eq1[1].get_center()[1]       # math-axis height of the line
        fx = cdot.get_right()[0] + 0.85
        bar = Line([fx - 0.55, y_axis, 0], [fx + 0.55, y_axis, 0],
                   stroke_width=3.2, color=COLOR_WHITE).set_z_index(8)
        dv = MathTex(r"\Delta v", font_size=64, color=COLOR_VEL
                     ).move_to([fx, y_axis + 0.46, 0]).set_z_index(8)
        dt = MathTex(r"\Delta t", font_size=64, color=COLOR_TIME
                     ).move_to([fx, y_axis - 0.50, 0]).set_z_index(8)

        # a rises and BECOMES Δv (the teal pays off as cyan); the bar draws
        # itself beneath; Δt slots in below. The equation grows out of itself.
        self.play(LaggedStart(
            AnimationGroup(ReplacementTransform(a, dv),
                           FadeIn(cdot, scale=0.7)),
            Create(bar),
            FadeIn(dt, shift=UP * 0.14),
            lag_ratio=0.45),
            run_time=2.1, rate_func=rate_functions.ease_in_out_cubic)
        self.wait(0.9)                        # "oh — a was never a mystery"

        self.F, self.eqs, self.m = eq1[0], eq1[1], eq1[2]
        self.cdot1, self.dv, self.bar, self.dt = cdot, dv, bar, dt

    # ===================================================================== A3
    def act3_time_crosses_the_bridge(self):
        # Target layout: F · Δt = m · Δv, centred.
        eq3 = MathTex("F", r"\cdot", r"\Delta t", "=", "m", r"\cdot",
                      r"\Delta v", font_size=76).move_to([0, EQ_Y, 0])
        eq3.set_z_index(8)
        for i, c in enumerate([COLOR_WHITE, COLOR_WHITE, COLOR_TIME,
                               COLOR_WHITE, COLOR_MASS, COLOR_WHITE,
                               COLOR_VEL]):
            eq3[i].set_color(c)

        # Δt detaches; the fraction bar dissolves under it.
        self.play(self.dt.animate.shift(DOWN * 0.12 + RIGHT * 0.06),
                  FadeOut(self.bar),
                  run_time=0.7, rate_func=rate_functions.ease_in_out_sine)

        # The signature move: Δt arcs OVER the equals sign and docks by F.
        # Everything else glides to its new mark; the eye follows the green.
        # path_arc > 0 (CCW) bulges the right→left journey upward.
        self.play(
            ReplacementTransform(self.dt, eq3[2], path_arc=2.4),
            ReplacementTransform(self.F, eq3[0]),
            ReplacementTransform(self.eqs, eq3[3]),
            ReplacementTransform(self.m, eq3[4]),
            ReplacementTransform(self.cdot1, eq3[5]),
            ReplacementTransform(self.dv, eq3[6]),
            run_time=2.3, rate_func=rate_functions.ease_in_out_cubic,
        )
        # the landing nudge: F and Δt fuse into a product
        self.play(FadeIn(eq3[1], scale=0.5), run_time=0.35,
                  rate_func=rate_functions.ease_out_cubic)

        self.eq3 = eq3
        self.lhs = VGroup(eq3[0], eq3[1], eq3[2])
        self.rhs = VGroup(eq3[4], eq3[5], eq3[6])

        # Two clean products facing each other — underline sweeps say so,
        # and a tiny push-in says "we've landed somewhere."
        sweep_l = Line(self.lhs.get_corner(DL) + DOWN * 0.25,
                       self.lhs.get_corner(DR) + DOWN * 0.25,
                       color=COLOR_WHITE, stroke_width=3)
        sweep_r = Line(self.rhs.get_corner(DL) + DOWN * 0.25,
                       self.rhs.get_corner(DR) + DOWN * 0.25,
                       color=COLOR_WHITE, stroke_width=3)
        self.play(ShowPassingFlash(sweep_l, time_width=0.6),
                  ShowPassingFlash(sweep_r, time_width=0.6),
                  self.camera.frame.animate.scale(0.93),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)                        # the Rubik's-face click

    # ===================================================================== A4
    def act4_read_what_you_wrote(self):
        eq3, lhs, rhs = self.eq3, self.lhs, self.rhs

        # >>> POST: music to near-silence HERE. The equation holds dead still.
        self.wait(1.0)

        # Annotate one side at a time. English labels (series rule).
        br_l = Brace(lhs, DOWN, buff=0.30, color=COLOR_GROUND)
        lab_l = Text("force × how long it acts", font=FONT, font_size=24,
                     color=COLOR_GROUND).next_to(br_l, DOWN, buff=0.22)
        self.play(GrowFromCenter(br_l), FadeIn(lab_l, shift=UP * 0.10),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.9)

        br_r = Brace(rhs, DOWN, buff=0.30, color=COLOR_GROUND)
        lab_r = Text("change in momentum", font=FONT, font_size=24,
                     color=COLOR_GROUND).next_to(br_r, DOWN, buff=0.22)
        self.play(GrowFromCenter(br_r), FadeIn(lab_r, shift=UP * 0.10),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.7)

        # The callback: scene_3's definition ghosts in, in its own colours.
        ghost = MathTex("p", "=", "m", r"\times", "v", font_size=44)
        ghost[0].set_color(COLOR_MOMENTUM)
        ghost[2].set_color(COLOR_MASS)
        ghost[4].set_color(COLOR_VEL)
        ghost.move_to(rhs.get_center() + UP * 1.65 + RIGHT * 0.30)
        ghost.set_opacity(0.0).set_z_index(7)
        self.add(ghost)
        self.play(ghost.animate.set_opacity(0.40), run_time=1.1,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.7)

        # The glow rides the right side from here to the end of the scene —
        # always_redraw so it survives every later move/scale untouched.
        self.glow_op = ValueTracker(0.0)
        self.glow = always_redraw(lambda: Ellipse(
            width=self.rhs.width + 1.15, height=self.rhs.height + 0.95,
            fill_color=COLOR_MOMENTUM,
            fill_opacity=self.glow_op.get_value(), stroke_width=0
        ).move_to(self.rhs.get_center()).set_z_index(-1))
        self.add(self.glow)

        # IGNITION: the ghost sinks into m·Δv and m·Δv becomes what it always
        # was — a change in momentum. Violet (flagged: series hero colour).
        # >>> POST: the single sub-bass "thoom" lands exactly here.
        self.play(
            ghost.animate.move_to(rhs.get_center()).set_opacity(0.0),
            self.glow_op.animate.set_value(0.16),
            rhs.animate.set_color(COLOR_MOMENTUM),
            lab_r.animate.set_color(COLOR_MOMENTUM),
            run_time=1.7, rate_func=rate_functions.ease_in_out_sine,
        )
        self.remove(ghost)

        # Change is the operative idea — the Δ itself takes one breath.
        delta_glyph = eq3[6][0]
        self.play(delta_glyph.animate.scale(1.35), run_time=0.9,
                  rate_func=rate_functions.there_and_back)

        # Left side white, right side glowing violet, staring at each other.
        # Hold a full beat longer than feels comfortable.
        self.wait(2.2)

        self.br_l, self.lab_l, self.br_r, self.lab_r = br_l, lab_l, br_r, lab_r

    # ── Act 5 internals ──────────────────────────────────────────────────
    def _push_scenario(self, lane_y, caption_text, f_len, t_push, d_push,
                       sweep, imp_to, v_len, d_coast, t_coast):
        """One push experiment. Motion is honest end-to-end:
        push phase x ∝ t² (ease_in_quad IS constant-force kinematics) and
        the coast speed equals the push's exit speed (2·d_push/t_push)."""
        R = 0.26
        ball = make_pool_ball(COLOR_MASS, R).move_to([-4.7, lane_y, 0])
        ball.set_z_index(5)
        clock = make_clock(0.30).move_to([-6.05, lane_y, 0]).set_z_index(5)
        cap = Text(caption_text, font=FONT, font_size=22, color=COLOR_GROUND)
        cap.move_to([-5.45, lane_y - 0.92, 0]).set_z_index(5)
        self.play(FadeIn(ball, scale=0.85), FadeIn(clock, scale=0.9),
                  FadeIn(cap, shift=UP * 0.08),
                  run_time=0.7, rate_func=rate_functions.ease_out_cubic)

        tip = lambda: ball.get_center() + LEFT * (R + 0.05)
        f_arr = Arrow(tip() + LEFT * f_len, tip(), buff=0, color=COLOR_WHITE,
                      stroke_width=6, max_tip_length_to_length_ratio=0.30
                      ).set_z_index(6)
        self.play(GrowArrow(f_arr), run_time=0.5,
                  rate_func=rate_functions.ease_out_cubic)
        f_arr.add_updater(
            lambda a: a.put_start_and_end_on(tip() + LEFT * f_len, tip()))
        self.wait(0.2)

        # THE PUSH — ball accelerates, clock runs, both meter bars grow in
        # lockstep (one tracker drives both sides: that IS the equation).
        self.play(
            ball.animate(rate_func=rate_functions.ease_in_quad)
                .shift(RIGHT * d_push),
            Rotate(clock.hand, sweep, about_point=clock.face.get_center(),
                   rate_func=linear),
            self.imp.animate(rate_func=linear).set_value(imp_to),
            run_time=t_push,
        )
        f_arr.clear_updaters()

        # Force ends — what remains is velocity (cyan) and the momentum it
        # bought (violet, under the ball: scene_3's grammar).
        v_anchor = lambda: ball.get_center() + RIGHT * (R + 0.06)
        p_anchor = lambda: np.array([ball.get_center()[0], lane_y - 0.55, 0])
        v_arr = Arrow(v_anchor(), v_anchor() + RIGHT * v_len, buff=0,
                      color=COLOR_VEL, stroke_width=5.5,
                      max_tip_length_to_length_ratio=0.25).set_z_index(6)
        dp_arr = Arrow(p_anchor(), p_anchor() + RIGHT * v_len, buff=0,
                       color=COLOR_MOMENTUM, stroke_width=5,
                       max_tip_length_to_length_ratio=0.25).set_z_index(6)
        self.play(FadeOut(f_arr, shift=LEFT * 0.2),
                  GrowArrow(v_arr), GrowArrow(dp_arr),
                  run_time=0.6, rate_func=rate_functions.ease_out_cubic)
        v_arr.add_updater(lambda a: a.put_start_and_end_on(
            v_anchor(), v_anchor() + RIGHT * v_len))
        dp_arr.add_updater(lambda a: a.put_start_and_end_on(
            p_anchor(), p_anchor() + RIGHT * v_len))

        # free travel — constant velocity, linear, honest
        self.play(ball.animate(rate_func=linear).shift(RIGHT * d_coast),
                  run_time=t_coast)
        v_arr.clear_updaters()
        dp_arr.clear_updaters()
        self.wait(0.4)
        return VGroup(ball, clock, cap, v_arr, dp_arr)

    # ===================================================================== A5
    def act5_more_push_more_time(self):
        # The annotated equation withdraws to the top and shrinks; the camera
        # returns to full frame. The glow rides along on its own.
        self.play(
            FadeOut(VGroup(self.br_l, self.lab_l, self.br_r, self.lab_r)),
            self.eq3.animate.scale(0.62).move_to([0, 3.0, 0]),
            Restore(self.camera.frame),
            run_time=1.4, rate_func=rate_functions.ease_in_out_cubic,
        )

        # Lockstep meters: one tracker, two bars, expanding symmetrically
        # under each side — stretch either input and BOTH sides stretch.
        MY = 2.28
        self.imp = ValueTracker(0.0)

        def meter(side_getter, color, op):
            def make():
                c = side_getter().get_center()[0]
                w = max(self.imp.get_value(), 0.012)
                return Line([c - w / 2, MY, 0], [c + w / 2, MY, 0],
                            stroke_width=7, color=color,
                            stroke_opacity=op).set_z_index(7)
            return always_redraw(make)

        bar_l = meter(lambda: self.lhs, COLOR_WHITE, 0.85)
        bar_r = meter(lambda: self.rhs, COLOR_MOMENTUM, 0.95)
        self.add(bar_l, bar_r)
        self.wait(0.3)

        # >>> EDIT (Premiere): the optional car-push clip would undercut HERE,
        #     under scenario A — never replacing the Manim.

        # Scenario A — small force, short time.
        grpA = self._push_scenario(
            lane_y=0.85, caption_text="small force · short time",
            f_len=0.70, t_push=1.0, d_push=0.45, sweep=-TAU * 0.30,
            imp_to=0.60, v_len=0.70, d_coast=1.26, t_coast=1.4)
        self.wait(0.4)

        # Ghost ticks remember A's level on both meters...
        ticks = VGroup()
        wA = self.imp.get_value()
        for grp in (self.lhs, self.rhs):
            c = grp.get_center()[0]
            for s in (-1, 1):
                ticks.add(Line([c + s * wA / 2, MY - 0.11, 0],
                               [c + s * wA / 2, MY + 0.11, 0],
                               stroke_width=2.5, color=COLOR_GROUND,
                               stroke_opacity=0.8).set_z_index(7))
        self.play(FadeIn(ticks), run_time=0.4)
        # ...then the bench resets for the second run; A's result stays,
        # dimmed, as the thing to beat.
        self.play(self.imp.animate.set_value(0.0),
                  grpA.animate.set_opacity(0.25),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_sine)

        # Scenario B — big force, long time. Same ball, same mass.
        grpB = self._push_scenario(
            lane_y=-1.45, caption_text="big force · long time",
            f_len=1.70, t_push=2.0, d_push=3.00, sweep=-TAU * 0.60,
            imp_to=1.60, v_len=2.25, d_coast=4.50, t_coast=1.5)

        # Both sides blew past the ghost ticks together — one shared breath.
        self.play(self.lhs.animate.scale(1.06), self.rhs.animate.scale(1.06),
                  run_time=0.9, rate_func=rate_functions.there_and_back)
        self.wait(1.0)                        # the muscle-memory beat

        # Clear the bench; only the equation (and its glow) survives.
        self.play(FadeOut(VGroup(grpA, grpB, ticks)),
                  self.imp.animate.set_value(0.0),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
        self.remove(bar_l, bar_r)

    # ===================================================================== A6
    def act6_give_it_a_name(self):
        eq3, lhs, rhs = self.eq3, self.lhs, self.rhs

        # Return to the clean equation, centre stage.
        self.play(eq3.animate.scale(1.45).move_to([0, 0.55, 0]),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_cubic)
        self.wait(0.5)

        # Spotlight the left side: F·Δt lifts off the line; the rest dims.
        self.play(
            lhs.animate.shift(UP * 0.55),
            eq3[3].animate.set_opacity(0.30),
            rhs.animate.set_opacity(0.40),
            self.glow_op.animate.set_value(0.05),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )

        # The christening. >>> POST: soft typographic "tick" lands with it.
        imp_tag = Text("IMPULSE", font=FONT, font_size=30, weight=BOLD,
                       color=COLOR_IMPULSE)
        imp_tag.next_to(lhs, DOWN, buff=0.42).set_z_index(9)
        outline = SurroundingRectangle(lhs, color=COLOR_IMPULSE, buff=0.20,
                                       corner_radius=0.14, stroke_width=2.5)
        outline.set_z_index(9)
        self.play(Write(imp_tag), run_time=0.9)
        self.play(Create(outline), lhs.animate.set_color(COLOR_IMPULSE),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)                        # the quiet authority of a name

        # Settle back into the line; the whole equation re-lights.
        self.play(
            FadeOut(outline),
            lhs.animate.shift(DOWN * 0.55),
            imp_tag.animate.shift(DOWN * 0.55),
            eq3[3].animate.set_opacity(1.0),
            rhs.animate.set_opacity(1.0),
            self.glow_op.animate.set_value(0.16),
            run_time=1.1, rate_func=rate_functions.ease_in_out_cubic,
        )

        # Both sides carry their meanings now.
        mom_tag = Text("change in momentum", font=FONT, font_size=24,
                       color=COLOR_MOMENTUM).set_z_index(9)
        mom_tag.move_to([rhs.get_center()[0], imp_tag.get_center()[1], 0])
        self.play(FadeIn(mom_tag, shift=UP * 0.10), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.9)

        # Park for the Scene-5 handoff: the launchpad rises to the top of
        # frame and keeps drifting, as if waiting for what's next.
        assembly = VGroup(eq3, imp_tag, mom_tag)
        self.play(assembly.animate.scale(0.88).move_to([0, 2.30, 0]),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)
        # the waiting drift — slow, unresolved on purpose
        self.play(assembly.animate.shift(UP * 0.22), run_time=2.6,
                  rate_func=linear)
        self.wait(1.0)                        # Scene 5 inherits this frame
