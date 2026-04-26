from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE  (consistent with the series)
# ─────────────────────────────────────────────
COLOR_BG        = "#1C1C1E"
COLOR_GROUND    = "#8E8E93"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F     = "#FF3B30"   # red — for force
COLOR_VEC_V     = "#32ADE6"   # cyan — for velocity
COLOR_GREEN     = "#34C759"
COLOR_AMBER     = "#FFCC00"
COLOR_PINK      = "#FF2D55"
COLOR_PURPLE    = "#BF5AF2"
COLOR_WHITE     = "#E5E5EA"


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
            op = peak_op * 0.3 * (1 - (2 * t - 1) ** 2)
            segs.add(Line(p1, p2, stroke_opacity=op,
                          stroke_width=1, color=COLOR_WHITE))
        return segs

    for x in np.arange(-max_x, max_x + 0.1, spacing):
        peak = 0.3 * (1 - (abs(x) / max_x) ** 1.5)
        if peak > 0:
            grid.add(fading_line(UP * max_y + RIGHT * x,
                                 DOWN * max_y + RIGHT * x, peak))
    for y in np.arange(-max_y, max_y + 0.1, spacing):
        peak = 0.3 * (1 - (abs(y) / max_y) ** 1.5)
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
#  SCENE 2 · "What IS force?"
# ═══════════════════════════════════════════════════════════════════

class Scene2_WhatIsForce(Scene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · The Opening Question
        # ══════════════════════════════════════════════════════════
        big_q = Text("What is force?", font="Segoe UI", font_size=72,
                     weight=BOLD, color=COLOR_WHITE)

        self.play(Write(big_q), run_time=2.0)
        self.wait()

        # Tuck the question into the top corner so it stays as context
        self.play(
            big_q.animate.scale(0.5).to_edge(UP, buff=0.6).set_opacity(0.5),
            run_time=0.9,
            rate_func=rate_functions.ease_in_out_sine
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · "Don't say push or pull"
        # ══════════════════════════════════════════════════════════
        dont_say = Text("Don't say...", font="Segoe UI", font_size=26,
                        color=COLOR_GROUND, slant=ITALIC).move_to(UP * 1.4)
        push_pull = Text('"A push or a pull."', font="Segoe UI", font_size=48,
                         weight=BOLD, color=COLOR_WHITE).move_to(UP * 0.3)

        self.play(FadeIn(dont_say, shift=DOWN * 0.2), run_time=0.6)
        self.play(FadeIn(push_pull, shift=UP * 0.15), run_time=0.9)
        self.wait(1.0)

        # The strike — pink, slight upward angle
        strike = Line(
            push_pull.get_left()  + LEFT  * 0.25 + DOWN * 0.06,
            push_pull.get_right() + RIGHT * 0.25 + UP   * 0.06,
            color=COLOR_PINK, stroke_width=5
        )
        self.play(Create(strike), run_time=0.5,
                  rate_func=rate_functions.ease_out_sine)

        not_phys1 = Text("That's a dictionary definition.", font="Segoe UI",
                         font_size=26, color=COLOR_GROUND).move_to(DOWN * 0.6)
        not_phys2 = Text("Not physics.", font="Segoe UI", font_size=30,
                         weight=BOLD, color=COLOR_PINK).next_to(not_phys1, DOWN, buff=0.3)

        self.play(FadeIn(not_phys1, shift=UP * 0.15), run_time=0.7)
        self.play(FadeIn(not_phys2, shift=UP * 0.15), run_time=0.7)
        self.wait(1.8)

        self.play(
            FadeOut(VGroup(dont_say, push_pull, strike, not_phys1, not_phys2)),
            run_time=0.7
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · The Real Definition
        # ══════════════════════════════════════════════════════════
        in_physics = Text("In physics, force is...", font="Segoe UI", font_size=28,
                          color=COLOR_GROUND).move_to(UP * 1.0)
        defn = Text("anything that changes motion.", font="Segoe UI",
                    font_size=44, weight=BOLD, color=COLOR_WHITE,
                    t2c={"changes motion": COLOR_GREEN}).move_to(ORIGIN)

        self.play(FadeIn(in_physics, shift=DOWN * 0.2), run_time=0.7)
        self.play(Write(defn), run_time=3.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.5)

        # Move the definition to the top so we can demonstrate it
        self.play(
            FadeOut(big_q),
            FadeOut(in_physics, shift=UP * 0.2),
            defn.animate.scale(0.55).to_edge(UP, buff=0.55),
            run_time=1.0,
            rate_func=rate_functions.ease_in_out_sine
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · Four Demonstrations
        # ══════════════════════════════════════════════════════════
        # Each case: situation label  →  force applied  →  outcome label

        def case_intro_label(text):
            return Text(text, font="Segoe UI", font_size=24,
                        slant=ITALIC, color=COLOR_GROUND).move_to(DOWN * 2.7)

        def case_outcome_label(text):
            return Text(text, font="Segoe UI", font_size=24,
                        color=COLOR_GREEN).move_to(DOWN * 2.7)

        # ────────────────────────────────────────
        #  CASE 1 · At rest → starts moving
        # ────────────────────────────────────────
        c1_lbl = case_intro_label("If at rest...")
        ball1 = make_ball(COLOR_BLUE_BALL, 0.30).move_to(LEFT * 3.5 + UP * 0.3).set_z_index(3)

        self.play(FadeIn(ball1, scale=0.5), FadeIn(c1_lbl), run_time=0.7)
        self.wait(0.4)

        # Force on the left, pointing right into the ball
        f_arr1 = Arrow(
            ball1.get_left() + LEFT * 0.85, ball1.get_left() + LEFT * 0.05,
            color=COLOR_VEC_F, buff=0, stroke_width=5
        ).set_z_index(2)
        f_lbl1 = MathTex("F", color=COLOR_VEC_F, font_size=30).next_to(f_arr1, UP, buff=0.05)

        self.play(GrowArrow(f_arr1), Write(f_lbl1), run_time=0.4)
        self.wait(0.3)

        c1_outcome = case_outcome_label("→ force makes it move")
        group1 = VGroup(ball1, f_arr1, f_lbl1)

        self.play(
            Transform(c1_lbl, c1_outcome),
            group1.animate.shift(RIGHT * 5.5),
            run_time=1.5,
            rate_func=rate_functions.ease_in_quad   # accelerating from rest
        )
        self.wait()
        self.play(FadeOut(group1), FadeOut(c1_lbl), run_time=0.5)
        self.wait()

        # ────────────────────────────────────────
        #  CASE 2 · Moving → stops
        # ────────────────────────────────────────
        c2_lbl = case_intro_label("If already moving...")
        ball2 = make_ball(COLOR_BLUE_BALL, 0.30).move_to(LEFT * 5.0 + UP * 0.3).set_z_index(3)
        v_arr2 = Arrow(
            ball2.get_top() + LEFT * 0.3 + UP * 0.4,
            ball2.get_top() + RIGHT * 0.5 + UP * 0.4,
            color=COLOR_VEC_V, buff=0, stroke_width=4
        )
        v_lbl2 = MathTex("v", color=COLOR_VEC_V, font_size=26).next_to(v_arr2, UP, buff=0.05)

        self.play(
            FadeIn(ball2, scale=0.5),
            GrowArrow(v_arr2), Write(v_lbl2),
            FadeIn(c2_lbl),
            run_time=0.7
        )

        # First, let it cruise at constant velocity
        moving2 = VGroup(ball2, v_arr2, v_lbl2)
        self.play(moving2.animate.shift(RIGHT * 2.5), run_time=0.9, rate_func=linear)

        # Trackers drive velocity shrinkage; force is constant length throughout
        v_init_len2 = 0.8
        v_len2 = ValueTracker(v_init_len2)
        f_full2 = 0.8

        v_arr2.add_updater(lambda a: a.put_start_and_end_on(
            ball2.get_top() + LEFT * 0.3 + UP * 0.4,
            ball2.get_top() + LEFT * 0.3 + UP * 0.4 + RIGHT * max(0.001, v_len2.get_value())
        ).set_opacity(min(1.0, v_len2.get_value() / v_init_len2)))
        v_lbl2.add_updater(lambda l: l.next_to(v_arr2, UP, buff=0.05).set_opacity(
            min(1.0, v_len2.get_value() / v_init_len2)
        ))

        f_arr2 = Arrow(
            ball2.get_right() + RIGHT * (0.06 + f_full2), ball2.get_right() + RIGHT * 0.06,
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.25
        ).set_z_index(2)
        f_lbl2 = MathTex("F", color=COLOR_VEC_F, font_size=30).next_to(f_arr2, UP, buff=0.05)

        self.play(GrowArrow(f_arr2), Write(f_lbl2), run_time=0.4)

        def f2_updater(arr):
            end = ball2.get_right() + RIGHT * 0.06
            arr.put_start_and_end_on(end + RIGHT * f_full2, end)
        f_arr2.add_updater(f2_updater)
        f_lbl2.add_updater(lambda l: l.next_to(f_arr2, UP, buff=0.05))

        c2_outcome = case_outcome_label("→ force can stop it")

        # Force is constant while the ball decelerates; velocity shrinks to zero
        self.play(
            Transform(c2_lbl, c2_outcome),
            ball2.animate.shift(RIGHT * 3.5),
            v_len2.animate.set_value(0.0),
            run_time=1.8,
            rate_func=rate_functions.ease_out_quad   # easing into a stop
        )

        v_arr2.clear_updaters()
        v_lbl2.clear_updaters()
        f_arr2.clear_updaters()
        f_lbl2.clear_updaters()

        slowing2 = VGroup(ball2, v_arr2, v_lbl2, f_arr2, f_lbl2)
        self.wait()
        self.play(FadeOut(slowing2), FadeOut(c2_lbl), run_time=0.5)
        self.wait()

        # ────────────────────────────────────────
        #  CASE 3 · Moving → changes direction
        # ────────────────────────────────────────
        c3_lbl = case_intro_label("...or change its direction")
        ball3_start = LEFT * 4.5 + UP * 1.5
        ball3 = make_ball(COLOR_BLUE_BALL, 0.30).move_to(ball3_start).set_z_index(3)
        v_arr3 = Arrow(
            ball3.get_top() + LEFT * 0.3 + UP * 0.35,
            ball3.get_top() + RIGHT * 0.5 + UP * 0.35,
            color=COLOR_VEC_V, buff=0, stroke_width=4
        )
        v_lbl3 = MathTex("v", color=COLOR_VEC_V, font_size=26).next_to(v_arr3, UP, buff=0.05)

        self.play(
            FadeIn(ball3, scale=0.5),
            GrowArrow(v_arr3), Write(v_lbl3),
            FadeIn(c3_lbl),
            run_time=0.7
        )

        moving3 = VGroup(ball3, v_arr3, v_lbl3)
        self.play(moving3.animate.shift(RIGHT * 1.8), run_time=0.7, rate_func=linear)

        # Build the parabolic path from the ball's current position
        start_pos = ball3.get_center()
        path3 = ParametricFunction(
            lambda s: start_pos + np.array([2.8 * s, -2.2 * s * s, 0]),
            t_range=[0, 1, 0.02],
            color=COLOR_BLUE_BALL, stroke_opacity=0.40, stroke_width=2
        )

        # Constant downward force arrow that follows the ball
        f_full3 = 0.7

        f_arr3 = Arrow(
            ball3.get_center() + DOWN * 0.30,
            ball3.get_center() + DOWN * 0.30 + DOWN * f_full3,
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.25
        ).set_z_index(2)
        f_lbl3 = MathTex("F", color=COLOR_VEC_F, font_size=30).next_to(f_arr3, RIGHT, buff=0.1)

        self.play(GrowArrow(f_arr3), Write(f_lbl3), run_time=0.4)

        def f3_updater(arr):
            start = ball3.get_center() + DOWN * 0.30
            arr.put_start_and_end_on(start, start + DOWN * f_full3)
        f_arr3.add_updater(f3_updater)
        f_lbl3.add_updater(lambda l: l.next_to(f_arr3, RIGHT, buff=0.1))

        # Force is constant while the ball curves along the path; velocity fades during the bend
        self.play(
            MoveAlongPath(ball3, path3),
            FadeOut(v_arr3), FadeOut(v_lbl3),
            FadeIn(path3),
            run_time=1.7,
            rate_func=linear
        )

        f_arr3.clear_updaters()
        f_lbl3.clear_updaters()

        self.wait()
        self.play(FadeOut(ball3), FadeOut(path3),
                  FadeOut(f_arr3), FadeOut(f_lbl3),
                  FadeOut(c3_lbl), run_time=0.5)
        self.wait()

        # ────────────────────────────────────────
        #  CASE 4 · Moving → speeds up
        # ────────────────────────────────────────
        c4_lbl = case_intro_label("...or speed it up")
        ball4 = make_ball(COLOR_BLUE_BALL, 0.30).move_to(LEFT * 4.7 + UP * 0.3).set_z_index(3)
        v_arr4 = Arrow(
            ball4.get_top() + LEFT * 0.2 + UP * 0.35,
            ball4.get_top() + RIGHT * 0.4 + UP * 0.35,
            color=COLOR_VEC_V, buff=0, stroke_width=4
        )
        v_lbl4 = MathTex("v", color=COLOR_VEC_V, font_size=26).next_to(v_arr4, UP, buff=0.05)

        self.play(
            FadeIn(ball4, scale=0.5),
            GrowArrow(v_arr4), Write(v_lbl4),
            FadeIn(c4_lbl),
            run_time=0.7
        )

        # Cruise at constant speed
        moving4 = VGroup(ball4, v_arr4, v_lbl4)
        self.play(moving4.animate.shift(RIGHT * 1.6), run_time=1.0, rate_func=linear)

        # Trackers drive velocity-vector enlargement; force is constant length throughout
        v_init_len4 = 0.6
        v_grown_len4 = 1.4
        v_len4 = ValueTracker(v_init_len4)
        f_full4 = 0.8

        v_arr4.add_updater(lambda a: a.put_start_and_end_on(
            ball4.get_top() + LEFT * 0.2 + UP * 0.35,
            ball4.get_top() + LEFT * 0.2 + UP * 0.35 + RIGHT * v_len4.get_value()
        ))
        v_lbl4.add_updater(lambda l: l.next_to(v_arr4, UP, buff=0.05))

        f_arr4 = Arrow(
            ball4.get_left() + LEFT * (0.05 + f_full4), ball4.get_left() + LEFT * 0.05,
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.25
        ).set_z_index(2)
        f_lbl4 = MathTex("F", color=COLOR_VEC_F, font_size=30).next_to(f_arr4, DOWN, buff=0.05)

        self.play(GrowArrow(f_arr4), Write(f_lbl4), run_time=0.4)

        def f4_updater(arr):
            end = ball4.get_left() + LEFT * 0.05
            arr.put_start_and_end_on(end + LEFT * f_full4, end)
        f_arr4.add_updater(f4_updater)
        f_lbl4.add_updater(lambda l: l.next_to(f_arr4, DOWN, buff=0.05))

        c4_outcome = case_outcome_label("→ force speeds it up")

        # Force is constant while the ball accelerates and the velocity vector grows
        self.play(
            Transform(c4_lbl, c4_outcome),
            ball4.animate.shift(RIGHT * 4.0),
            v_len4.animate.set_value(v_grown_len4),
            run_time=1.7,
            rate_func=rate_functions.ease_in_quad
        )

        v_arr4.clear_updaters()
        v_lbl4.clear_updaters()
        f_arr4.clear_updaters()
        f_lbl4.clear_updaters()

        all4 = VGroup(ball4, v_arr4, v_lbl4, f_arr4, f_lbl4)
        self.wait()
        self.play(FadeOut(all4), FadeOut(c4_lbl), FadeOut(defn), run_time=0.5)
        self.wait()

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · Force → Acceleration
        # ══════════════════════════════════════════════════════════

        f_word     = Text("Force", font="Segoe UI", font_size=54,
                          weight=BOLD, color=COLOR_VEC_F)
        arrow_word = MathTex(r"\longrightarrow", color=COLOR_WHITE, font_size=64)
        a_word     = Text("Acceleration", font="Segoe UI", font_size=54,
                          weight=BOLD, color=COLOR_AMBER)
        force_to_accel = VGroup(f_word, arrow_word, a_word).arrange(RIGHT, buff=0.4)
        force_to_accel.move_to(ORIGIN)

        self.play(
            LaggedStart(
                FadeIn(f_word, shift=UP * 0.2),
                Write(arrow_word),
                FadeIn(a_word, shift=UP * 0.2),
                lag_ratio=0.4
            ),
            run_time=1.6,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(2.0)

        # ══════════════════════════════════════════════════════════
        #  ACT 6 · The Cliffhanger
        # ══════════════════════════════════════════════════════════
        # Move the conclusion to top, drop the older definition
        self.play(
            force_to_accel.animate.scale(0.5).to_edge(UP, buff=0.55).set_opacity(0.55),
            run_time=1.0,
            rate_func=rate_functions.ease_in_out_sine
        )

        # The big question — letter cascade for emphasis
        how_much = Text("How much force?", font="Segoe UI", font_size=58,
                        weight=BOLD, color=COLOR_WHITE).move_to(ORIGIN)
        self.play(
            LaggedStart(
                *[FadeIn(letter, shift=UP * 0.25) for letter in how_much],
                lag_ratio=0.04
            ),
            run_time=1.5,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(0.6)

        depends = Text("What does it depend on?", font="Segoe UI", font_size=34,
                       weight=BOLD, color=COLOR_AMBER
                       ).next_to(how_much, DOWN, buff=0.6)
        self.play(FadeIn(depends, shift=UP * 0.2), run_time=0.9,
                  rate_func=rate_functions.ease_out_back)
        self.wait(2.0)

        # Final fade — leave only the grid behind
        self.play(
            FadeOut(how_much), FadeOut(depends),
            FadeOut(force_to_accel),
            run_time=1.2,
            rate_func=rate_functions.ease_in_cubic
        )
        self.wait(0.5)