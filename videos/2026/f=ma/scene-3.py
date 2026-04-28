from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE
# ─────────────────────────────────────────────
COLOR_BG        = "#1C1C1E"
COLOR_GROUND    = "#8E8E93"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F     = "#FF3B30"   # red — force
COLOR_VEC_V     = "#32ADE6"   # cyan — velocity
COLOR_GREEN     = "#34C759"
COLOR_AMBER     = "#FFCC00"
COLOR_PINK      = "#FF2D55"
COLOR_PURPLE    = "#AF52DE"   # updated to match Apple Purple specification
COLOR_ORANGE    = "#FF9500"
COLOR_WHITE     = "#E5E5EA"


# ═══════════════════════════════════════════════════════════════════
#  HELPERS  (consistent with the rest of the series)
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


def make_ball(color, radius=0.28):
    g = VGroup()
    sphere = Circle(radius=radius)
    sphere.set_fill(color, opacity=1.0)
    sphere.set_sheen(-0.45, DR)
    sphere.set_stroke(color=COLOR_WHITE, width=1.5, opacity=0.22)
    g.add(sphere)
    rim = Circle(radius=radius)
    rim.set_fill(opacity=0)
    rim.set_stroke(color=color, width=3, opacity=0.50)
    g.add(rim)
    spec = Ellipse(width=radius * 0.52, height=radius * 0.34)
    spec.set_fill(COLOR_WHITE, opacity=0.62)
    spec.set_stroke(width=0)
    spec.move_to(np.array([-radius * 0.28,  radius * 0.30, 0]))
    spec.rotate(-20 * DEGREES)
    g.add(spec)
    return g


# ═══════════════════════════════════════════════════════════════════
#  SCENE · Acceleration Matters — discovering F ∝ a
# ═══════════════════════════════════════════════════════════════════

class Scene2_ForceAndAcceleration(Scene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · INTRO — "Now imagine another situation..."
        # ══════════════════════════════════════════════════════════
        eyebrow = Text(
            "ANOTHER THOUGHT EXPERIMENT",
            font="Segoe UI", font_size=18,
            weight=BOLD, color=COLOR_GROUND
        )
        eyebrow_l = Line(LEFT * 0.5, ORIGIN,
                         color=COLOR_GROUND, stroke_width=1, stroke_opacity=0.6)
        eyebrow_r = Line(ORIGIN, RIGHT * 0.5,
                         color=COLOR_GROUND, stroke_width=1, stroke_opacity=0.6)
        eyebrow_l.next_to(eyebrow, LEFT, buff=0.25)
        eyebrow_r.next_to(eyebrow, RIGHT, buff=0.25)
        eyebrow_group = VGroup(eyebrow_l, eyebrow, eyebrow_r).move_to(UP * 0.5)

        intro_text = Text(
            "Imagine another situation...",
            font="Segoe UI", font_size=42,
            color=COLOR_WHITE, weight=BOLD
        ).move_to(DOWN * 0.3)

        self.play(
            FadeIn(eyebrow, shift=UP * 0.15),
            Create(eyebrow_l), Create(eyebrow_r)
        )
        self.play(
            FadeIn(intro_text, shift=UP * 0.2),
            run_time=1.0,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(1.0)

        self.play(
            FadeOut(eyebrow_group, shift=UP * 0.2),
            FadeOut(intro_text, shift=UP * 0.2),
            run_time=0.5
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · "A ball in your hand" — same mass in both cases
        # ══════════════════════════════════════════════════════════
        ball_intro = make_ball(COLOR_BLUE_BALL, 0.42).move_to(ORIGIN).set_z_index(3)
        ball_text = Text(
            "A ball in your hand.",
            font="Segoe UI", font_size=34,
            color=COLOR_WHITE, weight=BOLD
        ).next_to(ball_intro, DOWN, buff=0.7)

        self.play(
            FadeIn(ball_intro, scale=0.7),
            FadeIn(ball_text, shift=UP * 0.15),
            run_time=0.9,
            rate_func=rate_functions.ease_out_back
        )
        self.wait(0.7)

        self.play(
            FadeOut(ball_intro), FadeOut(ball_text),
            run_time=0.5
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · CASE 1 — Gentle push (slow acceleration)
        # ══════════════════════════════════════════════════════════
        case1_title = Text(
            "Case 1: Gentle push",
            font="Segoe UI", font_size=28,
            color=COLOR_BLUE_BALL, weight=BOLD
        ).to_edge(UP, buff=0.7)
        self.play(FadeIn(case1_title, shift=DOWN * 0.15), run_time=0.5)

        ball1 = make_ball(COLOR_BLUE_BALL, 0.32).move_to(LEFT * 5).set_z_index(3)

        f1_full = 0.65
        f1_arrow = Arrow(
            ball1.get_left() + LEFT * (0.05 + f1_full),
            ball1.get_left() + LEFT * 0.05,
            color=COLOR_VEC_F, buff=0, stroke_width=4,
            max_tip_length_to_length_ratio=0.25
        ).set_z_index(2)
        f1_label = Text("small F", font_size=20, color=COLOR_VEC_F,
                        font="Segoe UI", weight=BOLD)
        f1_label.next_to(f1_arrow, DOWN, buff=0.12)

        # Safe starting length for internal geometry (prevents crash)
        safe_min_len = 0.05 
        
        v1_init = 0.0
        v1_final = 0.7
        v1_len = ValueTracker(v1_init)

        v1_arrow = Arrow(
            ball1.get_top() + UP * 0.25,
            ball1.get_top() + UP * 0.25 + RIGHT * safe_min_len,
            color=COLOR_VEC_V, buff=0, stroke_width=3.5,
            max_tip_length_to_length_ratio=0.30
        )
        v1_arrow.set_opacity(0)  # Hide initially instead of using 0 length
        v1_label = MathTex("v", color=COLOR_VEC_V, font_size=24).set_opacity(0)

        v1_arrow.add_updater(lambda a: a.put_start_and_end_on(
            ball1.get_top() + UP * 0.25,
            ball1.get_top() + UP * 0.25 + RIGHT * max(safe_min_len, v1_len.get_value())
        ).set_opacity(min(1.0, v1_len.get_value() / 0.12)))
        
        v1_label.add_updater(lambda l: l.next_to(v1_arrow, UP, buff=0.05).set_opacity(
            min(1.0, v1_len.get_value() / 0.12)
        ))

        # 1. PLAY THE ANIMATIONS FIRST
        self.play(FadeIn(ball1, scale=0.7), run_time=0.4)
        self.play(GrowArrow(f1_arrow), FadeIn(f1_label), run_time=0.4)

        # 2. ATTACH THE UPDATERS AFTER THE ANIMATIONS FINISH
        f1_arrow.add_updater(lambda a: a.put_start_and_end_on(
            ball1.get_left() + LEFT * (0.05 + f1_full),
            ball1.get_left() + LEFT * 0.05
        ))
        f1_label.add_updater(lambda l: l.next_to(f1_arrow, DOWN, buff=0.12))
        self.add(v1_arrow, v1_label)

        self.play(
            ball1.animate.shift(RIGHT * 8),
            v1_len.animate.set_value(v1_final),
            run_time=3.0,
            rate_func=rate_functions.ease_in_quad
        )

        f1_arrow.clear_updaters()
        f1_label.clear_updaters()
        v1_arrow.clear_updaters()
        v1_label.clear_updaters()

        a1_text = Text(
            "→ slow acceleration",
            font="Segoe UI", font_size=28,
            color=COLOR_AMBER, weight=BOLD
        ).move_to(DOWN * 2.7)
        self.play(FadeIn(a1_text, shift=UP * 0.15), run_time=0.5)
        self.wait(1.0)

        self.play(
            FadeOut(case1_title),
            FadeOut(ball1), FadeOut(f1_arrow), FadeOut(f1_label),
            FadeOut(v1_arrow), FadeOut(v1_label),
            FadeOut(a1_text),
            run_time=0.5
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · CASE 2 — Hard throw (fast acceleration)
        # ══════════════════════════════════════════════════════════
        case2_title = Text(
            "Case 2: Hard throw",
            font="Segoe UI", font_size=28,
            color=COLOR_PINK, weight=BOLD
        ).to_edge(UP, buff=0.7)
        self.play(FadeIn(case2_title, shift=DOWN * 0.15), run_time=0.5)

        ball2 = make_ball(COLOR_BLUE_BALL, 0.32).move_to(LEFT * 5).set_z_index(3)

        f2_full = 1.5
        f2_arrow = Arrow(
            ball2.get_left() + LEFT * (0.05 + f2_full),
            ball2.get_left() + LEFT * 0.05,
            color=COLOR_VEC_F, buff=0, stroke_width=6,
            max_tip_length_to_length_ratio=0.22
        ).set_z_index(2)
        f2_label = Text("HUGE F!", font_size=22, color=COLOR_VEC_F,
                        font="Segoe UI", weight=BOLD)
        f2_label.next_to(f2_arrow, DOWN, buff=0.15)

        v2_init = 0.0
        v2_final = 1.6
        v2_len = ValueTracker(v2_init)

        v2_arrow = Arrow(
            ball2.get_top() + UP * 0.25,
            ball2.get_top() + UP * 0.25 + RIGHT * safe_min_len,
            color=COLOR_VEC_V, buff=0, stroke_width=4.5,
            max_tip_length_to_length_ratio=0.25
        )
        v2_arrow.set_opacity(0)
        v2_label = MathTex("v", color=COLOR_VEC_V, font_size=26).set_opacity(0)

        v2_arrow.add_updater(lambda a: a.put_start_and_end_on(
            ball2.get_top() + UP * 0.25,
            ball2.get_top() + UP * 0.25 + RIGHT * max(safe_min_len, v2_len.get_value())
        ).set_opacity(min(1.0, v2_len.get_value() / 0.25)))

        v2_label.add_updater(lambda l: l.next_to(v2_arrow, UP, buff=0.05).set_opacity(
            min(1.0, v2_len.get_value() / 0.25)
        ))

        self.play(FadeIn(ball2, scale=0.7), run_time=0.4)
        self.play(GrowArrow(f2_arrow), FadeIn(f2_label), run_time=0.3)

        # Attach updaters AFTER GrowArrow finishes to avoid zero-dimension crash
        f2_arrow.add_updater(lambda a: a.put_start_and_end_on(
            ball2.get_left() + LEFT * (0.05 + f2_full),
            ball2.get_left() + LEFT * 0.05
        ))
        f2_label.add_updater(lambda l: l.next_to(f2_arrow, DOWN, buff=0.15))

        self.add(v2_arrow, v2_label)

        flash = Rectangle(
            width=15, height=9, fill_color=COLOR_AMBER,
            fill_opacity=0.0, stroke_width=0
        ).set_z_index(20)
        self.add(flash)

        self.play(
            ball2.animate.shift(RIGHT * 8),
            v2_len.animate.set_value(v2_final),
            flash.animate.set_fill(opacity=0.12),
            run_time=0.45,
            rate_func=rate_functions.ease_out_expo
        )
        self.play(flash.animate.set_fill(opacity=0), run_time=0.15)
        self.remove(flash)

        f2_arrow.clear_updaters()
        f2_label.clear_updaters()
        v2_arrow.clear_updaters()
        v2_label.clear_updaters()

        a2_text = Text(
            "→ fast acceleration!",
            font="Segoe UI", font_size=32,
            color=COLOR_PINK, weight=BOLD
        ).move_to(DOWN * 2.7)
        self.play(FadeIn(a2_text, shift=UP * 0.15, scale=0.85), run_time=0.6)
        self.wait(1.2)

        self.play(
            FadeOut(case2_title),
            FadeOut(ball2), FadeOut(f2_arrow), FadeOut(f2_label),
            FadeOut(v2_arrow), FadeOut(v2_label),
            FadeOut(a2_text),
            run_time=0.5
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · COMPARISON CHART
        # ══════════════════════════════════════════════════════════
        LEFT_X  = -3.5
        RIGHT_X =  3.0
        TOP_Y   =  2.4

        cmp_ball1 = make_ball(COLOR_BLUE_BALL, 0.30)
        cmp_ball1.move_to([LEFT_X, TOP_Y - 0.7, 0]).set_z_index(3)
        cmp_f1 = Arrow(
            cmp_ball1.get_left() + LEFT * 0.6,
            cmp_ball1.get_left() + LEFT * 0.05,
            color=COLOR_VEC_F, buff=0, stroke_width=3.5,
            max_tip_length_to_length_ratio=0.25
        )
        cmp_v1 = Arrow(
            cmp_ball1.get_top() + UP * 0.20,
            cmp_ball1.get_top() + UP * 0.20 + RIGHT * 0.55,
            color=COLOR_VEC_V, buff=0, stroke_width=3,
            max_tip_length_to_length_ratio=0.30
        )
        title1 = Text(
            "Gentle Push", font_size=22,
            color=COLOR_BLUE_BALL, font="Segoe UI", weight=BOLD
        )
        title1.move_to([LEFT_X, TOP_Y, 0])

        cmp_ball2 = make_ball(COLOR_BLUE_BALL, 0.30)
        cmp_ball2.move_to([RIGHT_X, TOP_Y - 0.7, 0]).set_z_index(3)
        cmp_f2 = Arrow(
            cmp_ball2.get_left() + LEFT * 1.4,
            cmp_ball2.get_left() + LEFT * 0.05,
            color=COLOR_VEC_F, buff=0, stroke_width=6,
            max_tip_length_to_length_ratio=0.22
        )
        cmp_v2 = Arrow(
            cmp_ball2.get_top() + UP * 0.20,
            cmp_ball2.get_top() + UP * 0.20 + RIGHT * 1.4,
            color=COLOR_VEC_V, buff=0, stroke_width=4,
            max_tip_length_to_length_ratio=0.25
        )
        title2 = Text(
            "Hard Throw", font_size=22,
            color=COLOR_PINK, font="Segoe UI", weight=BOLD
        )
        title2.move_to([RIGHT_X, TOP_Y, 0])

        self.play(
            FadeIn(title1, shift=DOWN * 0.15),
            FadeIn(title2, shift=DOWN * 0.15),
            FadeIn(cmp_ball1, scale=0.8),
            FadeIn(cmp_ball2, scale=0.8),
            GrowArrow(cmp_f1), GrowArrow(cmp_f2),
            GrowArrow(cmp_v1), GrowArrow(cmp_v2),
            run_time=1.0
        )
        self.wait(0.4)

        def stat_at(symbol, value, color, x, y, font_size=28):
            t = MathTex(symbol, "=", value, font_size=font_size, color=color)
            t.move_to([x, y, 0])
            return t

        m_y = 0.4
        m1 = stat_at("m", r"\text{ball}", COLOR_BLUE_BALL, LEFT_X, m_y)
        m2 = stat_at("m", r"\text{ball}", COLOR_PINK, RIGHT_X, m_y)
        check_m = Text("✓ Same", font_size=20, color=COLOR_GREEN,
                       weight=BOLD, font="Segoe UI").move_to([0, m_y, 0])

        a_y = -0.9
        a1 = stat_at("a", r"\text{small}", COLOR_BLUE_BALL, LEFT_X, a_y)
        a2 = stat_at("a", r"\text{HUGE}", COLOR_PINK, RIGHT_X, a_y)
        cross_a = Text("✗ Different", font_size=20, color=COLOR_PINK,
                       weight=BOLD, font="Segoe UI").move_to([0, a_y, 0])

        F_y = -2.2
        F1 = stat_at("F", r"\text{small}", COLOR_BLUE_BALL, LEFT_X, F_y)
        F2 = stat_at("F", r"\text{HUGE}", COLOR_PINK, RIGHT_X, F_y)
        cross_F = Text("✗ Different", font_size=20, color=COLOR_PINK,
                       weight=BOLD, font="Segoe UI").move_to([0, F_y, 0])

        self.play(
            FadeIn(m1, shift=UP * 0.1), FadeIn(m2, shift=UP * 0.1),
            run_time=0.5
        )
        self.play(
            FadeIn(check_m, scale=0.85),
            Indicate(m1, color=COLOR_AMBER, scale_factor=1.10),
            Indicate(m2, color=COLOR_AMBER, scale_factor=1.10),
            run_time=0.7
        )
        self.wait(0.3)

        self.play(
            FadeIn(a1, shift=UP * 0.1), FadeIn(a2, shift=UP * 0.1),
            run_time=0.5
        )
        self.play(
            FadeIn(cross_a, scale=0.85),
            Indicate(a1, color=COLOR_AMBER, scale_factor=1.10),
            Indicate(a2, color=COLOR_AMBER, scale_factor=1.15),
            run_time=0.7
        )
        self.wait(0.3)

        self.play(
            FadeIn(F1, shift=UP * 0.1), FadeIn(F2, shift=UP * 0.1),
            run_time=0.5
        )
        self.play(
            FadeIn(cross_F, scale=0.85),
            Indicate(F1, color=COLOR_PINK, scale_factor=1.10),
            Indicate(F2, color=COLOR_PINK, scale_factor=1.15),
            run_time=0.8
        )
        self.wait(1.5)

        # ══════════════════════════════════════════════════════════
        #  ACT 6 · THE INSIGHT — More acceleration → More force
        # ══════════════════════════════════════════════════════════
        self.play(
            FadeOut(m1), FadeOut(m2), FadeOut(check_m),
            FadeOut(a1), FadeOut(a2), FadeOut(cross_a),
            FadeOut(F1), FadeOut(F2), FadeOut(cross_F),
            FadeOut(title1), FadeOut(title2),
            FadeOut(cmp_ball1), FadeOut(cmp_ball2),
            FadeOut(cmp_f1), FadeOut(cmp_f2),
            FadeOut(cmp_v1), FadeOut(cmp_v2),
            run_time=0.6
        )

        more_a = Text("More acceleration",
                      font="Segoe UI", font_size=42,
                      color=COLOR_AMBER, weight=BOLD)
        arrow_mid = MathTex(r"\rightarrow",
                            font_size=56, color=COLOR_WHITE)
        more_F = Text("More force",
                      font="Segoe UI", font_size=42,
                      color=COLOR_VEC_F, weight=BOLD)
        relation = VGroup(more_a, arrow_mid, more_F).arrange(RIGHT, buff=0.5)
        relation.move_to(UP * 0.7)

        self.play(
            LaggedStart(
                FadeIn(more_a, shift=UP * 0.2),
                FadeIn(arrow_mid, scale=0.7),
                FadeIn(more_F, shift=UP * 0.2),
                lag_ratio=0.4
            ),
            run_time=1.5,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(1.0)

        running_label = Text(
            "i.e.,", font="Segoe UI", font_size=22,
            color=COLOR_GROUND
        ).move_to(DOWN * 0.6)

        prop_eq = MathTex("F", r"\propto", "a",
                          font_size=110, color=COLOR_WHITE)
        prop_eq[0].set_color(COLOR_VEC_F)
        prop_eq[2].set_color(COLOR_AMBER)
        prop_eq.move_to(DOWN * 1.9)

        self.play(FadeIn(running_label, shift=DOWN * 0.1), run_time=0.4)

        f_src = more_F[5]  # index 4 is the space; 5 is 'f' of "force"
        a_src = more_a[5]  # index 4 is the space; 5 is 'a' of "acceleration"
        self.play(
            TransformFromCopy(f_src, prop_eq[0]),
            TransformFromCopy(arrow_mid, prop_eq[1]),
            TransformFromCopy(a_src, prop_eq[2]),
            run_time=1.5,
            rate_func=rate_functions.ease_in_out_sine
        )
        self.wait()

        eq_box = RoundedRectangle(
            corner_radius=0.18,
            width=prop_eq.width + 1.2,
            height=prop_eq.height + 0.7,
            stroke_color=COLOR_AMBER, stroke_width=2,
            stroke_opacity=0.45,
            fill_opacity=0
        ).move_to(prop_eq.get_center())
        self.play(Create(eq_box), run_time=0.7)
        self.wait(2.0)

        # ══════════════════════════════════════════════════════════
        #  ACT 7 · TWO PIECES OF THE PUZZLE — recall F ∝ m
        # ══════════════════════════════════════════════════════════
        self.play(
            FadeOut(more_a), FadeOut(arrow_mid), FadeOut(more_F),
            FadeOut(running_label),
            run_time=0.5
        )

        target_scale = 0.65
        target_pos_a = RIGHT * 3.2 + DOWN * 0.4
        self.play(
            VGroup(prop_eq, eq_box).animate
                .scale(target_scale).move_to(target_pos_a),
            run_time=1.0,
            rate_func=rate_functions.ease_in_out_sine
        )

        title = Text(
            "Two pieces of the puzzle",
            font="Segoe UI", font_size=34,
            color=COLOR_WHITE, weight=BOLD
        ).to_edge(UP, buff=1.0)
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.7)

        target_pos_m = LEFT * 3.2 + DOWN * 0.4
        prop_eq_m = MathTex("F", r"\propto", "m",
                            font_size=110, color=COLOR_WHITE)
        prop_eq_m[0].set_color(COLOR_VEC_F)
        prop_eq_m[2].set_color(COLOR_AMBER)
        prop_eq_m.scale(target_scale).move_to(target_pos_m)

        eq_box_m = RoundedRectangle(
            corner_radius=0.18 * target_scale,
            width=prop_eq_m.width + 1.2 * target_scale,
            height=prop_eq_m.height + 0.7 * target_scale,
            stroke_color=COLOR_AMBER, stroke_width=2,
            stroke_opacity=0.45, fill_opacity=0
        ).move_to(prop_eq_m.get_center())

        subtitle_m = Text(
            "From last time",
            font="Segoe UI", font_size=18,
            color=COLOR_GROUND, slant=ITALIC
        )
        subtitle_m.next_to(eq_box_m, UP, buff=0.3)

        subtitle_a = Text(
            "Just discovered",
            font="Segoe UI", font_size=18,
            color=COLOR_AMBER, slant=ITALIC
        )
        subtitle_a.next_to(eq_box, UP, buff=0.3)

        self.play(
            FadeIn(subtitle_m, shift=DOWN * 0.1),
            FadeIn(prop_eq_m), Create(eq_box_m),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic
        )
        self.play(FadeIn(subtitle_a, shift=DOWN * 0.1), run_time=0.4)
        self.wait(2.0)

        cliff = Text(
            "Can we combine them?",
            font="Segoe UI", font_size=32,
            color=COLOR_AMBER, weight=BOLD, slant=ITALIC
        ).to_edge(DOWN, buff=0.8)
        self.play(
            FadeIn(cliff, shift=UP * 0.15),
            run_time=0.7,
            rate_func=rate_functions.ease_out_back
        )
        self.wait(2.5)

        # ══════════════════════════════════════════════════════════
        #  FINAL FADE
        # ══════════════════════════════════════════════════════════
        objects_to_fade = [m for m in self.mobjects if m is not grid]
        self.play(FadeOut(Group(*objects_to_fade)), run_time=1.0)
        self.wait(0.4)