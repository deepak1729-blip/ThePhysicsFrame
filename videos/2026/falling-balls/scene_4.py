from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE 
# ─────────────────────────────────────────────
COLOR_BG        = "#1C1C1E"
COLOR_GROUND    = "#8E8E93"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_G     = "#FF3B30"
COLOR_VEC_V_X   = "#32ADE6"
COLOR_GREEN     = "#34C759"
COLOR_AMBER     = "#FFCC00"
COLOR_WHITE     = "#E5E5EA"

MIN_VEC_LEN = 0.02

# ═══════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════

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
            op = peak_op * 0.25 * (1 - (2 * t - 1) ** 2)
            segs.add(Line(p1, p2, stroke_opacity=op,
                          stroke_width=1, color=COLOR_WHITE))
        return segs

    for x in np.arange(-max_x, max_x + 0.1, spacing):
        peak = 0.2 * (1 - (abs(x) / max_x) ** 1.5)
        if peak > 0:
            grid.add(fading_line(UP * max_y + RIGHT * x,
                                 DOWN * max_y + RIGHT * x, peak))
    for y in np.arange(-max_y, max_y + 0.1, spacing):
        peak = 0.2 * (1 - (abs(y) / max_y) ** 1.5)
        if peak > 0:
            grid.add(fading_line(LEFT * max_x + UP * y,
                                 RIGHT * max_x + UP * y, peak))
    return grid

def make_ball(color: str, radius: float = 0.28) -> VGroup:
    """
    Returns a VGroup that looks like a lit 3-D sphere:
      • solid body with set_sheen() gradient (bright top-left → dark bottom-right)
      • thin rim-highlight stroke
      • specular ellipse (upper-left)
    """
    g = VGroup()

    # Main sphere body
    sphere = Circle(radius=radius)
    sphere.set_fill(color, opacity=1.0)
    sphere.set_sheen(-0.45, DR)          # darkens bottom-right, brightens top-left
    sphere.set_stroke(color=COLOR_WHITE, width=1.5, opacity=0.22)
    g.add(sphere)

    # Rim light (coloured stroke, gives the "lit edge" feel)
    rim = Circle(radius=radius)
    rim.set_fill(opacity=0)
    rim.set_stroke(color=color, width=3, opacity=0.50)
    g.add(rim)

    # Specular highlight — small ellipse offset to upper-left
    spec = Ellipse(width=radius * 0.52, height=radius * 0.34)
    spec.set_fill(COLOR_WHITE, opacity=0.62)
    spec.set_stroke(width=0)
    spec.move_to(
        np.array([-radius * 0.28,  radius * 0.30, 0])   # offset from origin
    )
    spec.rotate(-20 * DEGREES)
    g.add(spec)

    return g

def safe_put(arrow, start, end):
    if np.linalg.norm(end - start) < MIN_VEC_LEN:
        end = start + np.array([0.0, -MIN_VEC_LEN, 0.0])
    arrow.put_start_and_end_on(start, end)

def text_bg(text_mob, fill_color=COLOR_BG, fill_opacity=0.80,
            pad_x=0.22, pad_y=0.18, stroke=False,
            stroke_color=COLOR_WHITE, stroke_opacity=0.3):
    bg = Rectangle(
        width=text_mob.width + pad_x * 2,
        height=text_mob.height + pad_y * 2,
        fill_color=fill_color, fill_opacity=fill_opacity,
        stroke_width=1 if stroke else 0,
        stroke_color=stroke_color,
        stroke_opacity=stroke_opacity if stroke else 0,
    ).move_to(text_mob.get_center()).set_z_index(text_mob.get_z_index() - 1)
    return VGroup(bg, text_mob)

# ═══════════════════════════════════════════════════════════════════
#  SCENE 4 · "Same Height, Every Time"
# ═══════════════════════════════════════════════════════════════════

class Scene4_SameHeightProof(Scene):

    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        self.add(grid)

        # ─── Physics Constants ────────────────────────────────────
        START_Y   =  2.5           # both balls start here
        GROUND_Y  = -3.0           # visual ground level
        BALL_A_X  = -4.5           # Ball A column (dropped)
        BALL_B_X0 = -1.5           # Ball B launch x (thrown)
        t_final   =  2.0           # seconds of fall
        fall_dist = START_Y - (GROUND_Y + 0.28)
        GRAVITY   = 2.0 * fall_dist / t_final**2   # 2.7 units·s⁻²
        H_VEL     =  2.8           # Ball B horizontal speed → lands at x ≈ 4.1

        def pos_a(t):
            return np.array([BALL_A_X,
                             START_Y - 0.5 * GRAVITY * t**2,
                             0.0])

        def pos_b(t):
            return np.array([BALL_B_X0 + H_VEL * t,
                             START_Y - 0.5 * GRAVITY * t**2,
                             0.0])

        # ─── Ground Line ──────────────────────────────────────────
        ground = Line(LEFT * 7.5, RIGHT * 7.5,
                      color="#3A3A3C", stroke_width=2.5).set_z_index(0)
        ground.move_to([0, GROUND_Y, 0])

        # ─── Faint horizontal reference at start height ───────────
        start_ref = DashedLine(
            [-7.0, START_Y, 0], [7.0, START_Y, 0],
            color=COLOR_GROUND, stroke_width=1.0,
            dash_length=0.22, dashed_ratio=0.40,
            stroke_opacity=0.20
        ).set_z_index(0)

        # ─── Ghost paths for both balls ───────────────────────────────
        ghost_path_a = ParametricFunction(
            lambda s: pos_a(s * t_final),
            t_range=[0, 1, 0.02],
            color=COLOR_GREY_BALL,
            stroke_opacity=0.15,
            stroke_width=1.8
        ).set_z_index(0)

        ghost_path_b_straight = ParametricFunction(
            lambda s: np.array([BALL_B_X0 + H_VEL * (s * t_final), START_Y, 0.0]),
            t_range=[0, 1, 0.02],
            color=COLOR_BLUE_BALL,
            stroke_opacity=0.15,
            stroke_width=1.8
        ).set_z_index(0)

        ghost_arc = ParametricFunction(
            lambda s: pos_b(s * t_final),
            t_range=[0, 1, 0.02],
            color=COLOR_BLUE_BALL,
            stroke_opacity=0.15,
            stroke_width=1.8
        ).set_z_index(0)

        # ─── Balls ────────────────────────────────────────────────
        ball_a = make_ball(COLOR_GREY_BALL, radius=0.28).move_to(pos_a(0)).set_z_index(3)
        ball_b = make_ball(COLOR_BLUE_BALL, radius=0.28).move_to(pos_b(0)).set_z_index(3)

        # ─── Force Arrows (Static at start positions) ─────────────
        g_arrow_a = Arrow(
            pos_a(0), pos_a(0) + DOWN * 0.90,
            color=COLOR_VEC_G, buff=0, stroke_width=4
        ).set_z_index(1)
        g_lbl_a = MathTex(r"g", color=COLOR_VEC_G, font_size=26).set_z_index(1)
        g_lbl_a.next_to(g_arrow_a, RIGHT, buff=0.08)

        g_arrow_b = Arrow(
            pos_b(0), pos_b(0) + DOWN * 0.90,
            color=COLOR_VEC_G, buff=0, stroke_width=4
        ).set_z_index(1)
        g_lbl_b = MathTex(r"g", color=COLOR_VEC_G, font_size=26).set_z_index(1)
        g_lbl_b.next_to(g_arrow_b, RIGHT, buff=0.08)

        vx_arrow = Arrow(
            pos_b(0), pos_b(0) + RIGHT * 1.15,
            color=COLOR_VEC_V_X, buff=0, stroke_width=4
        ).set_z_index(1)
        vx_lbl = MathTex(r"v_x", color=COLOR_VEC_V_X, font_size=26).set_z_index(1)
        vx_lbl.next_to(vx_arrow, UP, buff=0.06)

        # ─── Ball Labels ──────────────────────────────────────────
        lbl_a = Text("Ball A", font="Segoe UI", font_size=24,
                     weight=BOLD, color=COLOR_GREY_BALL).set_z_index(6)
        lbl_a.next_to(ball_a, UP, buff=0.28)
        sub_a = Text("(dropped)", font="Segoe UI", font_size=14,
                     color=COLOR_GROUND, slant=ITALIC).set_z_index(6)
        sub_a.next_to(lbl_a, DOWN, buff=0.03)

        lbl_b = Text("Ball B", font="Segoe UI", font_size=24,
                     weight=BOLD, color=COLOR_BLUE_BALL).set_z_index(6)
        lbl_b.next_to(ball_b, UP, buff=0.28)
        sub_b = Text("(thrown)", font="Segoe UI", font_size=14,
                     color=COLOR_GROUND, slant=ITALIC).set_z_index(6)
        sub_b.next_to(lbl_b, DOWN, buff=0.03)

        # ─── Height Indicator H ───────────────────────────────────
        H_X = BALL_A_X - 0.9

        h_vert = DashedLine(
            [H_X, START_Y, 0], [H_X, GROUND_Y, 0],
            color=COLOR_AMBER, stroke_width=1.8,
            dash_length=0.12, dashed_ratio=0.50
        ).set_z_index(1)
        h_top_tick = Line([H_X - 0.12, START_Y,  0],
                          [H_X + 0.12, START_Y,  0],
                          color=COLOR_AMBER, stroke_width=2)
        h_bot_tick = Line([H_X - 0.12, GROUND_Y, 0],
                          [H_X + 0.12, GROUND_Y, 0],
                          color=COLOR_AMBER, stroke_width=2)
        h_lbl = MathTex("h", color=COLOR_AMBER, font_size=34).set_z_index(6)
        h_lbl.move_to([H_X - 0.45, (START_Y + GROUND_Y) / 2, 0])
        h_indicator = VGroup(h_vert, h_top_tick, h_bot_tick, h_lbl)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · INTRO
        # ══════════════════════════════════════════════════════════
        prev_title = Text("Independence of Motion", font="Segoe UI", font_size=46,
                          weight=BOLD, color=COLOR_GREEN).to_edge(UP, buff=0.25)
        self.add(prev_title, ground)

        self.play(FadeIn(start_ref), run_time=0.6)
        self.wait(0.5)

        self.play(
            ReplacementTransform(prev_title, VGroup(ball_a, ball_b)),
            run_time=1.5,
            rate_func=rate_functions.ease_in_out_back
        )
        self.wait(0.5)

        self.play(
            FadeIn(lbl_a, shift=UP*0.2), FadeIn(sub_a, shift=UP*0.2),
            FadeIn(lbl_b, shift=UP*0.2), FadeIn(sub_b, shift=UP*0.2)
        )
        self.wait()

        self.play(
            Create(h_vert),
            FadeIn(h_top_tick), FadeIn(h_bot_tick),
            Write(h_lbl)
        )
        self.wait()

        self.play(
            GrowArrow(vx_arrow), Write(vx_lbl),
            Create(ghost_path_b_straight),
            run_time=0.9
        )
        self.wait(0.5)

        self.play(
            GrowArrow(g_arrow_a), Write(g_lbl_a),
            GrowArrow(g_arrow_b), Write(g_lbl_b),
            ReplacementTransform(ghost_path_b_straight, ghost_arc),
            Create(ghost_path_a),
            run_time=1.2 
        )
        self.wait(0.6)

        # Dim the labels and clear out vectors before motion begins
        self.play(
            FadeOut(lbl_a), FadeOut(sub_a),
            FadeOut(lbl_b), FadeOut(sub_b),
            FadeOut(g_arrow_a), FadeOut(g_lbl_a),   # <-- Fading out gravity A
            FadeOut(g_arrow_b), FadeOut(g_lbl_b),   # <-- Fading out gravity B
            FadeOut(vx_arrow), FadeOut(vx_lbl),     # <-- Fading out velocity B
            h_indicator.animate.set_opacity(0.28),
            run_time=0.5
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · ANIMATED DROP WITH PAUSES
        # ══════════════════════════════════════════════════════════
        t_tracker = ValueTracker(0.0)

        timer_lbl = Text("t = ", font="monospace", font_size=22,
                         color=COLOR_GROUND).set_z_index(7)
        timer_dyn = always_redraw(lambda: Text(
            f"{t_tracker.get_value():.2f} s",
            font="monospace", font_size=22, color=COLOR_WHITE
        ).set_z_index(7).next_to(timer_lbl, RIGHT, buff=0.09))

        VGroup(timer_lbl, Text("0.00 s", font="monospace", font_size=22)).arrange(RIGHT, buff=0.09).to_edge(DOWN, buff=0.42)
        timer_lbl.to_edge(DOWN, buff=0.42)
        timer_lbl.set_x(-0.55)
        self.add(timer_lbl, timer_dyn)

        # Vectors are NO LONGER updated here, keeping them static
        def update_a(mob):
            mob.move_to(pos_a(t_tracker.get_value()))

        def update_b(mob):
            mob.move_to(pos_b(t_tracker.get_value()))

        ball_a.add_updater(update_a)
        ball_b.add_updater(update_b)

        # Stops at 1.5 now so we can sync 2.0 with the ripples
        pauses = [0.5, 1.0, 1.5] 
        prev_t = 0.0
        rung_lines = VGroup()

        for pt in pauses:
            dt = pt - prev_t
            self.play(t_tracker.animate.set_value(pt), run_time=dt, rate_func=linear)

            pa = pos_a(pt)
            pb = pos_b(pt)

            conn_line = DashedLine(pa, pb, color=COLOR_AMBER, stroke_width=2.5, dash_length=0.1).set_z_index(1)
            rung_lines.add(conn_line)
            
            ghost_a = Dot(pa, radius=0.06, color=COLOR_GREY_BALL).set_z_index(1)
            ghost_b = Dot(pb, radius=0.06, color=COLOR_BLUE_BALL).set_z_index(1)
            
            # Re-added text background and explicitly playing it!
            t_text = Text(f"t = {pt:.1f} s", font="monospace", font_size=18, color=COLOR_AMBER).set_z_index(8)
            t_text.next_to(conn_line, UP, buff=0.1)

            self.play(
                Create(conn_line),
                FadeIn(ghost_a), FadeIn(ghost_b),
                FadeIn(t_text),
                run_time=0.6
            )
            self.wait()
            prev_t = pt

        # ─── Final chunk to t = 2.0 ───────────────────────────────
        self.play(t_tracker.animate.set_value(t_final), run_time=(t_final - prev_t), rate_func=linear)

        ball_a.clear_updaters()
        ball_b.clear_updaters()
        timer_dyn.clear_updaters()

        # ══════════════════════════════════════════════════════════
        #  IMPACT — simultaneous ripples & final rung
        # ══════════════════════════════════════════════════════════
        final_pa = pos_a(t_final)
        final_pb = pos_b(t_final)

        # Setup final rung
        final_conn_line = DashedLine(final_pa, final_pb, color=COLOR_AMBER, stroke_width=2.5, dash_length=0.1).set_z_index(1)
        rung_lines.add(final_conn_line)
        final_ghost_a = Dot(final_pa, radius=0.06, color=COLOR_GREY_BALL).set_z_index(1)
        final_ghost_b = Dot(final_pb, radius=0.06, color=COLOR_BLUE_BALL).set_z_index(1)
        final_t_text = Text("t = 2.0 s", font="monospace", font_size=18, color=COLOR_AMBER).set_z_index(8).next_to(final_conn_line, UP, buff=0.1)

        # Setup Ripples
        ripple_a1 = Circle(radius=0.30, color=COLOR_GREY_BALL, stroke_width=3.0).move_to(final_pa).set_z_index(5)
        ripple_a2 = Circle(radius=0.30, color=COLOR_GREY_BALL, stroke_width=1.2, stroke_opacity=0.55).move_to(final_pa).set_z_index(5)
        ripple_b1 = Circle(radius=0.30, color=COLOR_BLUE_BALL, stroke_width=3.0).move_to(final_pb).set_z_index(5)
        ripple_b2 = Circle(radius=0.30, color=COLOR_BLUE_BALL, stroke_width=1.2, stroke_opacity=0.55).move_to(final_pb).set_z_index(5)

        # Play EVERYTHING exactly as it hits the ground
        self.play(
            ripple_a1.animate.scale(3.5).set_opacity(0),
            ripple_a2.animate.scale(5.5).set_opacity(0),
            ripple_b1.animate.scale(3.5).set_opacity(0),
            ripple_b2.animate.scale(5.5).set_opacity(0),
            Create(final_conn_line),
            FadeIn(final_ghost_a), FadeIn(final_ghost_b),
            FadeIn(final_t_text),
            run_time=0.75,
            rate_func=rate_functions.ease_out_quad
        )
        self.wait(0.7)

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · THE KEY INSIGHT
        # ══════════════════════════════════════════════════════════
        self.play(rung_lines.animate.set_color(COLOR_WHITE).set_stroke(width=4), run_time=0.5)
        self.play(rung_lines.animate.set_color(COLOR_AMBER).set_stroke(width=2.5), run_time=0.5)

        msg1 = Text(
            "Exact same time.",
            font="Segoe UI", font_size=50, weight=BOLD, color=COLOR_GREEN
        ).set_z_index(9).to_edge(UP, buff=0.30)

        self.play(Write(msg1), run_time=3)
        self.wait()

        msg2 = Text(
            "Horizontal journey is completely irrelevant.",
            font="Segoe UI", font_size=20, color=COLOR_WHITE
        ).set_z_index(9).next_to(msg1, DOWN, buff=0.35)
        msg2_bg = text_bg(msg2, fill_opacity=0.86)

        self.play(FadeIn(msg2_bg))
        self.wait(0.5)

        msg3 = Text(
            "Gravity simply does not care.",
            font="Segoe UI", font_size=24, weight=BOLD, color=COLOR_VEC_G
        ).set_z_index(9).next_to(msg2, DOWN, buff=0.30)
        msg3_bg = text_bg(msg3, fill_opacity=0.86)

        self.play(FadeIn(msg3_bg, scale=0.92))
        self.wait(2.0)

        # ══════════════════════════════════════════════════════════
        #  THE GRAND FINALE — UNIFIED TRANSFORMATION
        # ══════════════════════════════════════════════════════════

        # Clean, uncolored equation using your white hex
        equation = MathTex(
            r"s=ut+\frac{1}{2}at^2",
            font_size=42,
            color=COLOR_WHITE
        ).move_to(ORIGIN).set_z_index(10)

        # Grab everything on screen, but ONLY if it's a visual Vector Mobject
        mobs_to_transform = VGroup(
            *[m for m in self.mobjects if isinstance(m, VMobject) and m is not grid]
        )

        # Morph the entire scene into the final formula
        self.play(
            ReplacementTransform(mobs_to_transform, equation),
            run_time=3,
            rate_func=rate_functions.ease_in_out_back
        )
        self.wait()