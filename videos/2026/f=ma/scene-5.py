from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE  (consistent with the series)
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
COLOR_PURPLE    = "#AF52DE"
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


def text_bg(text_mob, fill_color=COLOR_BG, fill_opacity=0.85,
            pad_x=0.25, pad_y=0.20, stroke=False,
            stroke_color=COLOR_WHITE, stroke_opacity=0.3):
    bg = RoundedRectangle(
        corner_radius=0.1,
        width=text_mob.width + pad_x * 2,
        height=text_mob.height + pad_y * 2,
        fill_color=fill_color, fill_opacity=fill_opacity,
        stroke_width=1 if stroke else 0,
        stroke_color=stroke_color,
        stroke_opacity=stroke_opacity if stroke else 0
    ).move_to(text_mob.get_center()).set_z_index(text_mob.get_z_index() - 1)
    return VGroup(bg, text_mob)


def make_badge(num_str, color):
    """Numbered badge with underline — for the 01/02/03 insight tags."""
    badge = Text(num_str, font="Segoe UI", font_size=24,
                 weight=BOLD, color=color)
    underline = Line(LEFT * 0.32, RIGHT * 0.32,
                     color=color, stroke_width=2)
    underline.next_to(badge, DOWN, buff=0.10)
    return VGroup(badge, underline)


def make_bottle(filled=False, scale=1.0,
                body_color=COLOR_GREY_BALL,
                liquid_color=COLOR_BLUE_BALL):
    """Simple stylised bottle. `filled=True` draws a liquid level inside."""
    g = VGroup()
    # body
    body = RoundedRectangle(
        corner_radius=0.18 * scale,
        width=0.85 * scale, height=1.9 * scale,
        fill_color=body_color, fill_opacity=0.10,
        stroke_color=body_color, stroke_width=2.2
    )
    # shoulder taper
    shoulder = Polygon(
        body.get_corner(UL) + RIGHT * 0.12 * scale,
        body.get_corner(UR) + LEFT  * 0.12 * scale,
        body.get_corner(UR) + LEFT  * 0.27 * scale + UP * 0.28 * scale,
        body.get_corner(UL) + RIGHT * 0.27 * scale + UP * 0.28 * scale,
        fill_color=body_color, fill_opacity=0.10,
        stroke_color=body_color, stroke_width=2.2,
    )
    # neck
    neck = Rectangle(
        width=0.32 * scale, height=0.32 * scale,
        fill_color=body_color, fill_opacity=0.10,
        stroke_color=body_color, stroke_width=2.2
    )
    neck.next_to(shoulder, UP, buff=0)
    # cap
    cap = RoundedRectangle(
        corner_radius=0.04 * scale,
        width=0.42 * scale, height=0.18 * scale,
        fill_color=body_color, fill_opacity=0.55,
        stroke_color=body_color, stroke_width=1.8
    )
    cap.next_to(neck, UP, buff=0)
    g.add(body, shoulder, neck, cap)

    if filled:
        liquid = RoundedRectangle(
            corner_radius=0.14 * scale,
            width=0.72 * scale, height=1.55 * scale,
            fill_color=liquid_color, fill_opacity=0.70,
            stroke_width=0
        )
        liquid.move_to(body.get_center() + DOWN * 0.12 * scale)
        # subtle surface line
        surface = Line(
            liquid.get_corner(UL) + RIGHT * 0.04 * scale,
            liquid.get_corner(UR) + LEFT  * 0.04 * scale,
            color=COLOR_WHITE, stroke_width=1.2, stroke_opacity=0.55
        )
        g.add(liquid, surface)
    return g


# ═══════════════════════════════════════════════════════════════════
#  SCENE 5 · The Closing — "Why Multiply?" + Real Takeaway + Challenge
# ═══════════════════════════════════════════════════════════════════

class Scene5_Closing(Scene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # ──────────────────────────────────────────────────────────
        # AMBIENT CLOCK — drives breathing animations
        # ──────────────────────────────────────────────────────────
        clock = ValueTracker(0)
        clock_driver = Mobject()
        clock_driver.add_updater(lambda m, dt: clock.increment_value(dt))
        self.add(clock_driver)

        def act_pulse(color=COLOR_WHITE, duration=0.7):
            ring = Circle(radius=0.1, color=color, stroke_width=2,
                          stroke_opacity=0.7, fill_opacity=0)
            self.add(ring)
            self.play(
                ring.animate.scale(60).set_stroke(opacity=0),
                run_time=duration,
                rate_func=rate_functions.ease_out_quart
            )
            self.remove(ring)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · "But why MULTIPLY? Why not add?"
        #  Voice: "Humne kaha Force mass aur acceleration dono par
        #          depend karta hai. Toh maine F = m + a kyun nahi likha?"
        # ══════════════════════════════════════════════════════════

        fma = MathTex("F", "=", "m", r"\cdot", "a",
                      font_size=110, color=COLOR_WHITE)
        fma[0].set_color(COLOR_VEC_F)
        fma[2].set_color(COLOR_AMBER)
        fma[3].set_color(COLOR_GROUND)
        fma[4].set_color(COLOR_AMBER)

        self.add(fma)

        self.wait(0.4)

        # Spotlight the operator — the dot is the suspect
        spotlight = Circle(radius=0.45, color=COLOR_AMBER,
                           stroke_width=2.5, stroke_opacity=0.8,
                           fill_opacity=0).move_to(fma[3].get_center())
        self.play(
            Create(spotlight),
            Indicate(fma[3], color=COLOR_AMBER, scale_factor=2.0),
            run_time=0.9
        )
        self.play(FadeOut(spotlight), run_time=0.3)

        # The tempting wrong version below
        alt_eq = MathTex("F", "=", "m", "+", "a",
                         font_size=110, color=COLOR_WHITE)
        alt_eq[0].set_color(COLOR_VEC_F)
        alt_eq[2].set_color(COLOR_AMBER)
        alt_eq[3].set_color(COLOR_PINK)
        alt_eq[4].set_color(COLOR_AMBER)
        alt_eq.move_to(DOWN * 1.7)

        why_not = Text("…why not just add?", font="Segoe UI",
                       font_size=30, color=COLOR_GROUND, slant=ITALIC)
        why_not.next_to(alt_eq, UP, buff=0.4)

        self.play(FadeIn(why_not, shift=UP * 0.15), run_time=0.6)
        self.play(
            TransformFromCopy(fma[0], alt_eq[0]),
            TransformFromCopy(fma[1], alt_eq[1]),
            TransformFromCopy(fma[2], alt_eq[2]),
            FadeIn(alt_eq[3], scale=0.5),
            TransformFromCopy(fma[4], alt_eq[4]),
            run_time=1.4,
            rate_func=rate_functions.ease_in_out_sine
        )
        # pulse the suspect operator
        self.play(
            Indicate(alt_eq[3], color=COLOR_PINK, scale_factor=1.6),
            run_time=0.7
        )
        self.wait(0.8)

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · THE UNIT TEST
        # ══════════════════════════════════════════════════════════

        # Tuck the real equation into the top-right corner;
        # bring the wrong one up as the thing we're going to test
        self.play(
            FadeOut(why_not, shift=UP * 0.2),
            fma.animate.scale(0.32).to_corner(UR, buff=0.55).set_opacity(0.45),
            alt_eq.animate.scale(0.55).move_to(UP * 2.85),
            run_time=0.9,
            rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.2)

        # ── Phase A · plug in real numbers ──
        m_val = MathTex(r"m = 2\,\text{kg}",
                        font_size=42, color=COLOR_AMBER)
        a_val = MathTex(r"a = 3\,\text{m/s}^2",
                        font_size=42, color=COLOR_AMBER)
        vals = VGroup(m_val, a_val).arrange(RIGHT, buff=1.6)
        vals.move_to(UP * 1.4)

        self.play(
            LaggedStart(
                FadeIn(m_val, shift=UP * 0.2),
                FadeIn(a_val, shift=UP * 0.2),
                lag_ratio=0.35
            ),
            run_time=1.0
        )
        self.wait(0.4)

        # The naive addition result
        result_eq = MathTex("F", "=", "2", "+", "3", "=", "5",
                            font_size=80, color=COLOR_WHITE)
        result_eq[0].set_color(COLOR_VEC_F)
        result_eq[2].set_color(COLOR_AMBER)
        result_eq[3].set_color(COLOR_PINK)
        result_eq[4].set_color(COLOR_AMBER)
        result_eq[6].set_color(COLOR_WHITE)
        result_eq.move_to(UP * 0.05)

        # 2 and 3 flow from the values; the + is borrowed from alt_eq
        self.play(
            TransformFromCopy(m_val[0][2], result_eq[2]),
            TransformFromCopy(a_val[0][2], result_eq[4]),
            FadeIn(result_eq[0], shift=RIGHT * 0.3),
            FadeIn(result_eq[1], shift=RIGHT * 0.3),
            FadeIn(result_eq[3], scale=0.5),
            run_time=1.2,
            rate_func=rate_functions.ease_in_out_sine
        )
        self.play(
            FadeIn(result_eq[5], shift=LEFT * 0.15),
            FadeIn(result_eq[6], shift=LEFT * 0.15),
            run_time=0.6
        )
        self.wait(0.4)

        # let the question hang
        self.play(
            Indicate(result_eq[6], color=COLOR_PINK, scale_factor=1.3),
            run_time=0.6
        )
        self.wait(1.0)

        # ── Phase B · the showdown of units ──
        self.play(
            FadeOut(vals, shift=UP * 0.15),
            FadeOut(result_eq, shift=DOWN * 0.15),
            alt_eq.animate.move_to(UP * 3.1),
            run_time=0.7
        )

        # Two unit blocks, colour-keyed (amber = mass-unit, cyan = accel-unit)
        kg_block = RoundedRectangle(
            corner_radius=0.18, width=2.1, height=1.4,
            fill_color=COLOR_AMBER, fill_opacity=0.16,
            stroke_color=COLOR_AMBER, stroke_width=2.5
        )
        kg_lbl = MathTex(r"\text{kg}", font_size=62, color=COLOR_AMBER)
        kg_lbl.move_to(kg_block.get_center())
        kg_group = VGroup(kg_block, kg_lbl).move_to(LEFT * 3.4 + DOWN * 0.2)

        ms2_block = RoundedRectangle(
            corner_radius=0.18, width=2.4, height=1.4,
            fill_color=COLOR_VEC_V, fill_opacity=0.16,
            stroke_color=COLOR_VEC_V, stroke_width=2.5
        )
        ms2_lbl = MathTex(r"\text{m/s}^{2}", font_size=52, color=COLOR_VEC_V)
        ms2_lbl.move_to(ms2_block.get_center())
        ms2_group = VGroup(ms2_block, ms2_lbl).move_to(RIGHT * 3.4 + DOWN * 0.2)

        op_sign = MathTex("+", font_size=88, color=COLOR_WHITE)
        op_sign.move_to(DOWN * 0.2)

        self.play(
            FadeIn(kg_group, shift=RIGHT * 0.3),
            FadeIn(ms2_group, shift=LEFT * 0.3),
            FadeIn(op_sign, scale=0.5),
            run_time=0.9
        )
        self.wait(0.4)

        # Try to push them together — they collide and reject each other
        self.play(
            kg_group.animate.shift(RIGHT * 1.55),
            ms2_group.animate.shift(LEFT * 1.55),
            run_time=0.6,
            rate_func=rate_functions.ease_in_quad
        )
        # COLLISION — bounce back with a pink spark
        spark = Flash(op_sign.get_center(), color=COLOR_PINK,
                      line_length=0.28, num_lines=12,
                      flash_radius=0.55, line_stroke_width=2.6)
        self.play(
            kg_group.animate.shift(LEFT * 0.45),
            ms2_group.animate.shift(RIGHT * 0.45),
            op_sign.animate.set_color(COLOR_PINK),
            spark,
            run_time=0.55
        )

        not_a_thing = Text("not a real quantity",
                           font="Segoe UI", font_size=26,
                           color=COLOR_PINK, slant=ITALIC)
        not_a_thing.move_to(DOWN * 1.7)
        self.play(FadeIn(not_a_thing, shift=UP * 0.15), run_time=0.5)
        self.wait(1.1)

        # ── Phase C · the multiplication accepts ──
        self.play(
            FadeOut(not_a_thing, shift=DOWN * 0.1),
            run_time=0.45
        )

        op_times = MathTex(r"\times", font_size=88, color=COLOR_GREEN)
        op_times.move_to(op_sign.get_center())
        self.play(Transform(op_sign, op_times), run_time=0.6)
        self.play(
            Indicate(op_sign, color=COLOR_GREEN, scale_factor=1.35),
            run_time=0.5
        )

        # They fuse into a compound unit
        compound_block = RoundedRectangle(
            corner_radius=0.20, width=4.4, height=1.55,
            fill_color=COLOR_GREEN, fill_opacity=0.14,
            stroke_color=COLOR_GREEN, stroke_width=3
        )
        compound_lbl = MathTex(r"\text{kg} \cdot \text{m/s}^{2}",
                               font_size=56, color=COLOR_WHITE)
        compound_lbl.move_to(compound_block.get_center())
        compound = VGroup(compound_block, compound_lbl).move_to(DOWN * 0.2)

        self.play(ReplacementTransform(VGroup(kg_group, ms2_group, op_sign), compound), 
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)

        # self.play(
        #     FadeOut(VGroup(kg_group, ms2_group, op_sign), scale=0.55),
        #     FadeIn(compound, scale=0.85),
        #     run_time=1.0,
        #     rate_func=rate_functions.ease_in_out_sine
        # )
        self.wait(1.5)

        # Closing thought of Act 2
        self.play(
            FadeOut(compound, shift=UP * 0.2),
            FadeOut(alt_eq, shift=UP * 0.2),
            run_time=0.7
        )

        lesson_a = Text("Units demand multiplication.",
                        font="Segoe UI", font_size=42,
                        color=COLOR_WHITE, weight=BOLD,
                        t2c={"multiplication": COLOR_GREEN})
        lesson_a.move_to(ORIGIN)

        self.play(
            LaggedStart(
                *[FadeIn(ch, shift=UP * 0.18) for ch in lesson_a],
                lag_ratio=0.03
            ),
            run_time=1.3
        )
        self.wait(1.6)

        self.play(FadeOut(lesson_a, shift=UP * 0.2),
                  FadeOut(fma, shift=UP * 0.2),
                  run_time=0.7)

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · THREE LESSONS HIDDEN IN F = ma
        # ══════════════════════════════════════════════════════════

        fma_top = MathTex("F", "=", "m", r"\cdot", "a",
                          font_size=66, color=COLOR_WHITE)
        fma_top[0].set_color(COLOR_VEC_F)
        fma_top[2].set_color(COLOR_AMBER)
        fma_top[3].set_color(COLOR_GROUND)
        fma_top[4].set_color(COLOR_AMBER)
        fma_top.to_edge(UP, buff=0.55)

        sub_head = Text("Three lessons inside one little equation.",
                        font="Segoe UI", font_size=22,
                        color=COLOR_GROUND, slant=ITALIC)
        sub_head.next_to(fma_top, DOWN, buff=0.25)

        self.play(FadeIn(fma_top, shift=DOWN * 0.15), run_time=0.6)
        self.play(FadeIn(sub_head, shift=DOWN * 0.1), run_time=0.5)
        self.wait(0.4)

        # ── LESSON 01 · Same F, more m → less a ──
        badge_1 = make_badge("01", COLOR_GREEN)
        badge_1.move_to(LEFT * 5.4 + UP * 1.3)
        self.play(FadeIn(badge_1, shift=RIGHT * 0.15), run_time=0.4)

        # Two balls: small mass on top, big mass below — both pushed with same F
        small_ball = make_ball(COLOR_BLUE_BALL, 0.26).move_to(LEFT * 3.6 + UP * 1.3)
        big_ball   = make_ball(COLOR_BLUE_BALL, 0.55).move_to(LEFT * 3.6 + DOWN * 1.3)

        m_tag_small = MathTex("m", font_size=22, color=COLOR_AMBER)
        m_tag_small.move_to(small_ball.get_center())
        m_tag_big = MathTex("M", font_size=36, color=COLOR_AMBER)
        m_tag_big.move_to(big_ball.get_center())

        f_len = 0.85
        f_arr_top = Arrow(
            small_ball.get_left() + LEFT * (0.05 + f_len),
            small_ball.get_left() + LEFT * 0.05,
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.25
        )
        f_arr_bot = Arrow(
            big_ball.get_left() + LEFT * (0.1 + f_len),
            big_ball.get_left() + LEFT * 0.1,
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.25
        )
        f_lbl_top = MathTex("F", font_size=28, color=COLOR_VEC_F)
        f_lbl_top.next_to(f_arr_top, DOWN, buff=0.08)
        f_lbl_bot = MathTex("F", font_size=28, color=COLOR_VEC_F)
        f_lbl_bot.next_to(f_arr_bot, DOWN, buff=0.08)

        self.play(
            FadeIn(small_ball, scale=0.7), FadeIn(m_tag_small),
            FadeIn(big_ball,   scale=0.7), FadeIn(m_tag_big),
            run_time=0.6
        )
        self.play(
            GrowArrow(f_arr_top), FadeIn(f_lbl_top),
            GrowArrow(f_arr_bot), FadeIn(f_lbl_bot),
            run_time=0.5
        )

        # Force arrows track each ball
        f_arr_top.add_updater(lambda a: a.put_start_and_end_on(
            small_ball.get_left() + LEFT * (0.05 + f_len),
            small_ball.get_left() + LEFT * 0.05
        ))
        f_lbl_top.add_updater(lambda l: l.next_to(f_arr_top, DOWN, buff=0.08))
        f_arr_bot.add_updater(lambda a: a.put_start_and_end_on(
            big_ball.get_left() + LEFT * (0.1 + f_len),
            big_ball.get_left() + LEFT * 0.1
        ))
        f_lbl_bot.add_updater(lambda l: l.next_to(f_arr_bot, DOWN, buff=0.08))
        m_tag_small.add_updater(lambda l: l.move_to(small_ball.get_center()))
        m_tag_big.add_updater(lambda l: l.move_to(big_ball.get_center()))

        # Race — small zooms; big crawls
        ball_pair_1 = VGroup(small_ball)
        ball_pair_2 = VGroup(big_ball)
        self.play(
            small_ball.animate.shift(RIGHT * 6.5),
            big_ball.animate.shift(RIGHT * 1.4),
            run_time=2.0,
            rate_func=rate_functions.ease_in_quad
        )
        for m in (f_arr_top, f_lbl_top, f_arr_bot, f_lbl_bot,
                  m_tag_small, m_tag_big):
            m.clear_updaters()

        # Caption — the lesson
        cap_1 = Text("Same F, more m  →  less a",
                     font="Segoe UI", font_size=28,
                     color=COLOR_WHITE, weight=BOLD,
                     t2c={"less a": COLOR_AMBER})
        cap_1.move_to(DOWN * 3.05)
        self.play(FadeIn(cap_1, shift=UP * 0.15), run_time=0.6)
        self.wait(1.0)

        # Clear lesson 1
        lesson_1_all = VGroup(badge_1, small_ball, big_ball,
                              m_tag_small, m_tag_big,
                              f_arr_top, f_lbl_top, f_arr_bot, f_lbl_bot,
                              cap_1)
        self.play(FadeOut(lesson_1_all, shift=UP * 0.1), run_time=0.6)

        # ── LESSON 02 · Same m, more F → more a ──
        badge_2 = make_badge("02", COLOR_AMBER)
        badge_2.move_to(LEFT * 5.4 + UP * 1.3)
        self.play(FadeIn(badge_2, shift=RIGHT * 0.15), run_time=0.4)

        ball_top2 = make_ball(COLOR_BLUE_BALL, 0.32).move_to(LEFT * 3.6 + UP * 1.3)
        ball_bot2 = make_ball(COLOR_BLUE_BALL, 0.32).move_to(LEFT * 3.6 + DOWN * 1.3)
        m_tag_top2 = MathTex("m", font_size=24, color=COLOR_AMBER)
        m_tag_top2.move_to(ball_top2.get_center())
        m_tag_bot2 = MathTex("m", font_size=24, color=COLOR_AMBER)
        m_tag_bot2.move_to(ball_bot2.get_center())

        small_f_len = 0.45
        big_f_len   = 1.4
        f_small_arr = Arrow(
            ball_top2.get_left() + LEFT * (0.05 + small_f_len),
            ball_top2.get_left() + LEFT * 0.05,
            color=COLOR_VEC_F, buff=0, stroke_width=4,
            max_tip_length_to_length_ratio=0.30
        )
        f_big_arr = Arrow(
            ball_bot2.get_left() + LEFT * (0.05 + big_f_len),
            ball_bot2.get_left() + LEFT * 0.05,
            color=COLOR_VEC_F, buff=0, stroke_width=6,
            max_tip_length_to_length_ratio=0.22
        )
        f_small_lbl = Text("small F", font="Segoe UI",
                           font_size=20, weight=BOLD, color=COLOR_VEC_F)
        f_small_lbl.next_to(f_small_arr, DOWN, buff=0.1)
        f_big_lbl = Text("HUGE F", font="Segoe UI",
                         font_size=22, weight=BOLD, color=COLOR_VEC_F)
        f_big_lbl.next_to(f_big_arr, DOWN, buff=0.1)

        self.play(
            FadeIn(ball_top2, scale=0.7), FadeIn(m_tag_top2),
            FadeIn(ball_bot2, scale=0.7), FadeIn(m_tag_bot2),
            run_time=0.5
        )
        self.play(
            GrowArrow(f_small_arr), FadeIn(f_small_lbl),
            GrowArrow(f_big_arr),   FadeIn(f_big_lbl),
            run_time=0.5
        )

        f_small_arr.add_updater(lambda a: a.put_start_and_end_on(
            ball_top2.get_left() + LEFT * (0.05 + small_f_len),
            ball_top2.get_left() + LEFT * 0.05
        ))
        f_small_lbl.add_updater(lambda l: l.next_to(f_small_arr, DOWN, buff=0.1))
        f_big_arr.add_updater(lambda a: a.put_start_and_end_on(
            ball_bot2.get_left() + LEFT * (0.05 + big_f_len),
            ball_bot2.get_left() + LEFT * 0.05
        ))
        f_big_lbl.add_updater(lambda l: l.next_to(f_big_arr, DOWN, buff=0.1))
        m_tag_top2.add_updater(lambda l: l.move_to(ball_top2.get_center()))
        m_tag_bot2.add_updater(lambda l: l.move_to(ball_bot2.get_center()))

        self.play(
            ball_top2.animate.shift(RIGHT * 1.5),
            ball_bot2.animate.shift(RIGHT * 6.5),
            run_time=2.0,
            rate_func=rate_functions.ease_in_quad
        )
        for m in (f_small_arr, f_small_lbl, f_big_arr, f_big_lbl,
                  m_tag_top2, m_tag_bot2):
            m.clear_updaters()

        cap_2 = Text("Same m, more F  →  more a",
                     font="Segoe UI", font_size=28,
                     color=COLOR_WHITE, weight=BOLD,
                     t2c={"more a": COLOR_AMBER})
        cap_2.move_to(DOWN * 3.05)
        self.play(FadeIn(cap_2, shift=UP * 0.15), run_time=0.6)
        self.wait(1.0)

        lesson_2_all = VGroup(badge_2, ball_top2, ball_bot2,
                              m_tag_top2, m_tag_bot2,
                              f_small_arr, f_small_lbl,
                              f_big_arr, f_big_lbl, cap_2)
        self.play(FadeOut(lesson_2_all, shift=UP * 0.1), run_time=0.6)

        # ── LESSON 03 · Zero F → Zero a (the BIG one) ──
        badge_3 = make_badge("03", COLOR_PINK)
        badge_3.move_to(LEFT * 5.4 + UP * 1.3)
        self.play(FadeIn(badge_3, shift=RIGHT * 0.15), run_time=0.4)

        # A single ball, already in motion, no force
        ball3 = make_ball(COLOR_BLUE_BALL, 0.32).move_to(LEFT * 5.5)
        v_arr = Arrow(
            ball3.get_top() + UP * 0.25,
            ball3.get_top() + UP * 0.25 + RIGHT * 0.95,
            color=COLOR_VEC_V, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.28
        )
        v_lbl = MathTex("v", color=COLOR_VEC_V, font_size=30)
        v_lbl.next_to(v_arr, UP, buff=0.06)

        self.play(FadeIn(ball3, scale=0.7), run_time=0.4)
        self.play(GrowArrow(v_arr), FadeIn(v_lbl), run_time=0.45)

        # Where the force WOULD be — but isn't
        f_ghost = MathTex("F = 0", font_size=40, color=COLOR_VEC_F)
        f_ghost.move_to(ball3.get_center() + DOWN * 1.1)
        self.play(FadeIn(f_ghost, shift=UP * 0.15), run_time=0.5)
        # X out the F=0 — actually, let it stay; it's the point
        self.wait(0.4)

        # vectors track the ball
        v_arr.add_updater(lambda a: a.put_start_and_end_on(
            ball3.get_top() + UP * 0.25,
            ball3.get_top() + UP * 0.25 + RIGHT * 0.95
        ))
        v_lbl.add_updater(lambda l: l.next_to(v_arr, UP, buff=0.06))
        f_ghost.add_updater(lambda l: l.move_to(ball3.get_center() + DOWN * 1.1))

        # Constant velocity — no acceleration. linear rate.
        self.play(
            ball3.animate.shift(RIGHT * 9.5),
            run_time=3.0,
            rate_func=linear
        )
        v_arr.clear_updaters()
        v_lbl.clear_updaters()
        f_ghost.clear_updaters()

        cap_3 = Text("No F  →  no change in motion",
                     font="Segoe UI", font_size=28,
                     color=COLOR_WHITE, weight=BOLD,
                     t2c={"No F": COLOR_VEC_F,
                          "no change": COLOR_GREEN})
        cap_3.move_to(DOWN * 3.05)
        self.play(FadeIn(cap_3, shift=UP * 0.15), run_time=0.6)
        self.wait(1.2)

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · NEWTON'S FIRST LAW WAS ALWAYS INSIDE
        # ══════════════════════════════════════════════════════════

        # Clear lesson 3's caption, keep the ball-snapshot off-screen
        lesson_3_all = VGroup(badge_3, ball3, v_arr, v_lbl, f_ghost, cap_3, fma_top)

        # The big stamp — Newton's First Law was always in here
        nfl_stamp = Text("Newton's First Law",
                         font="Segoe UI", font_size=44,
                         color=COLOR_PINK, weight=BOLD)


        stamp_box = RoundedRectangle(
            corner_radius=0.15,
            width=nfl_stamp.width + 0.7,
            height=nfl_stamp.height + 0.45,
            stroke_color=COLOR_PINK, stroke_width=2.2,
            stroke_opacity=0.85, fill_opacity=0
        ).move_to(nfl_stamp.get_center())

        self.play(
            LaggedStart(
                *[FadeIn(ch, shift=UP * 0.2) for ch in nfl_stamp],
                lag_ratio=0.04
            ),
            run_time=1.1
        )
        self.play(Create(stamp_box), run_time=0.5)
        self.wait(1.8)

        # Sweep this section out

        self.play(FadeOut(lesson_3_all, shift=UP * 0.1),
                  FadeOut(sub_head, shift=UP * 0.1),
                  FadeOut(nfl_stamp, shift=UP * 0.1),
                  run_time=0.6)
        self.play(
            FadeOut(stamp_box, shift=UP * 0.2),
            run_time=0.8
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · THE REAL TAKEAWAY — don't memorize, question
        # ══════════════════════════════════════════════════════════

        # Small "THE TAKEAWAY" eyebrow header
        eyebrow = Text("THE REAL TAKEAWAY", font="Segoe UI",
                       font_size=18, weight=BOLD, color=COLOR_GROUND)
        eb_l = Line(LEFT * 0.55, ORIGIN, color=COLOR_GROUND,
                    stroke_width=1, stroke_opacity=0.6).next_to(eyebrow, LEFT, buff=0.25)
        eb_r = Line(ORIGIN, RIGHT * 0.55, color=COLOR_GROUND,
                    stroke_width=1, stroke_opacity=0.6).next_to(eyebrow, RIGHT, buff=0.25)
        eyebrow_grp = VGroup(eb_l, eyebrow, eb_r).move_to(UP * 2.7)

        self.play(
            FadeIn(eyebrow, shift=UP * 0.15),
            Create(eb_l), Create(eb_r),
            run_time=0.7
        )

        # F = ma in the centre, surrounded by question marks that morph to checks
        fma_focus = MathTex("F", "=", "m", r"\cdot", "a",
                            font_size=100, color=COLOR_WHITE)
        fma_focus[0].set_color(COLOR_VEC_F)
        fma_focus[2].set_color(COLOR_AMBER)
        fma_focus[3].set_color(COLOR_GROUND)
        fma_focus[4].set_color(COLOR_AMBER)
        fma_focus.move_to(UP * 0.3)

        self.play(Write(fma_focus), run_time=1.0)

        # Question marks orbit in, six of them at different angles
        q_marks = VGroup()
        positions = [
            UP * 1.7 + LEFT * 3.0,
            UP * 1.7 + RIGHT * 3.0,
            DOWN * 1.3 + LEFT * 3.4,
            DOWN * 1.3 + RIGHT * 3.4,
            UP * 0.3 + LEFT * 4.7,
            UP * 0.3 + RIGHT * 4.7,
        ]
        for pos in positions:
            q = Text("?", font="Segoe UI", font_size=54,
                     color=COLOR_PINK, weight=BOLD)
            q.move_to(pos)
            q_marks.add(q)

        self.play(
            LaggedStart(
                *[FadeIn(q, scale=0.5) for q in q_marks],
                lag_ratio=0.08
            ),
            run_time=1.4
        )
        self.wait(0.6)

        # Each ? transforms into a ✓ (in green)
        checks = VGroup()
        for q in q_marks:
            c = Text("✓", font="Segoe UI", font_size=48,
                     color=COLOR_GREEN, weight=BOLD)
            c.move_to(q.get_center())
            checks.add(c)

        self.play(
            LaggedStart(
                *[Transform(q, c) for q, c in zip(q_marks, checks)],
                lag_ratio=0.12
            ),
            run_time=1.6,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(0.4)

        # Clear takeaway
        takeaway_all = VGroup(eyebrow_grp, fma_focus, q_marks, checks)
        self.play(FadeOut(takeaway_all, shift=UP * 0.15), run_time=0.8)


        # ══════════════════════════════════════════════════════════
        #  ACT 6 · YOUR CHALLENGE — find F = ma in your own kitchen
        # ══════════════════════════════════════════════════════════

        ch_eyebrow = Text("YOUR CHALLENGE", font="Segoe UI",
                          font_size=20, weight=BOLD, color=COLOR_AMBER)
        ch_eb_l = Line(LEFT * 0.6, ORIGIN, color=COLOR_AMBER,
                       stroke_width=1.2, stroke_opacity=0.75).next_to(ch_eyebrow, LEFT, buff=0.25)
        ch_eb_r = Line(ORIGIN, RIGHT * 0.6, color=COLOR_AMBER,
                       stroke_width=1.2, stroke_opacity=0.75).next_to(ch_eyebrow, RIGHT, buff=0.25)
        ch_header = VGroup(ch_eb_l, ch_eyebrow, ch_eb_r).to_edge(UP, buff=0.7)

        self.play(
            FadeIn(ch_eyebrow, shift=UP * 0.15),
            Create(ch_eb_l), Create(ch_eb_r),
            run_time=0.7
        )

        # Two stacked "tables" — upper shelf and lower shelf
        table_top = Line(LEFT * 6.5 + DOWN * 0.3, RIGHT * 6.5 + DOWN * 0.3,
                         color=COLOR_GROUND, stroke_width=2, stroke_opacity=0.55)
        table = Line(LEFT * 6.5 + DOWN * 2.7, RIGHT * 6.5 + DOWN * 2.7,
                     color=COLOR_GROUND, stroke_width=2, stroke_opacity=0.7)

        self.play(Create(table_top), Create(table), run_time=0.8)

        # Two bottles — empty up top, full on the bottom shelf
        empty_bottle = make_bottle(filled=False, scale=0.7,
                                   body_color=COLOR_GREY_BALL,
                                   liquid_color=COLOR_BLUE_BALL)
        full_bottle  = make_bottle(filled=True,  scale=0.7,
                                   body_color=COLOR_GREY_BALL,
                                   liquid_color=COLOR_BLUE_BALL)

        # Sit each bottle on its shelf, near the left edge
        empty_bottle.next_to(table_top, UP, buff=0)
        empty_bottle.shift(RIGHT * (-5.0 - empty_bottle.get_x()))
        full_bottle.next_to(table, UP, buff=0)
        full_bottle.shift(RIGHT * (-5.0 - full_bottle.get_x()))

        # tags for empty vs full
        empty_tag = Text("empty", font="Segoe UI", font_size=20,
                         color=COLOR_GROUND).next_to(empty_bottle, LEFT, buff=0.25).shift(UP * 0.3)
        full_tag = Text("full", font="Segoe UI", font_size=20,
                        color=COLOR_BLUE_BALL, weight=BOLD).next_to(full_bottle, LEFT, buff=0.25).shift(UP * 0.3)

        self.play(
            FadeIn(empty_bottle, shift=UP * 0.2),
            FadeIn(full_bottle,  shift=UP * 0.2),
            run_time=0.7
        )
        self.play(FadeIn(empty_tag), FadeIn(full_tag), run_time=0.4)

        # Same push arrow on both — same length, same colour
        push_len = 0.85
        push_arr_e = Arrow(
            empty_bottle.get_left() + LEFT * (0.08 + push_len),
            empty_bottle.get_left() + LEFT * 0.08,
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.25
        )
        push_arr_f = Arrow(
            full_bottle.get_left() + LEFT * (0.08 + push_len),
            full_bottle.get_left() + LEFT * 0.08,
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.25
        )
        push_lbl_e = MathTex("F", font_size=26, color=COLOR_VEC_F)
        push_lbl_e.next_to(push_arr_e, DOWN, buff=0.08)
        push_lbl_f = MathTex("F", font_size=26, color=COLOR_VEC_F)
        push_lbl_f.next_to(push_arr_f, DOWN, buff=0.08)

        self.play(
            GrowArrow(push_arr_e), FadeIn(push_lbl_e),
            GrowArrow(push_arr_f), FadeIn(push_lbl_f),
            run_time=0.6
        )
        self.wait(0.6)

        # Arrows follow their bottles during the push
        push_arr_e.add_updater(lambda a: a.put_start_and_end_on(
            empty_bottle.get_left() + LEFT * (0.08 + push_len),
            empty_bottle.get_left() + LEFT * 0.08
        ))
        push_lbl_e.add_updater(lambda l: l.next_to(push_arr_e, DOWN, buff=0.08))
        push_arr_f.add_updater(lambda a: a.put_start_and_end_on(
            full_bottle.get_left() + LEFT * (0.08 + push_len),
            full_bottle.get_left() + LEFT * 0.08
        ))
        push_lbl_f.add_updater(lambda l: l.next_to(push_arr_f, DOWN, buff=0.08))
        empty_tag.add_updater(lambda l: l.next_to(empty_bottle, LEFT, buff=0.25).shift(UP * 0.3))
        full_tag.add_updater(lambda l: l.next_to(full_bottle, LEFT, buff=0.25).shift(UP * 0.3))

        # The empty zooms; the full barely budges
        self.play(
            empty_bottle.animate.shift(RIGHT * 8.5),
            full_bottle.animate.shift(RIGHT * 1.6),
            run_time=2.2,
            rate_func=rate_functions.ease_in_quad
        )
        for m in (push_arr_e, push_lbl_e, push_arr_f, push_lbl_f,
                  empty_tag, full_tag):
            m.clear_updaters()

        # The synthesis caption
        verdict = Text("F = ma: right there, on your table.",
                       font="Segoe UI", font_size=30,
                       color=COLOR_WHITE, weight=BOLD,
                       t2c={"F = ma": COLOR_AMBER,
                            "on your table": COLOR_GREEN})
        verdict.move_to(DOWN * 3.55)
        self.play(
            LaggedStart(
                *[FadeIn(ch, shift=UP * 0.15) for ch in verdict],
                lag_ratio=0.03
            ),
            run_time=1.3
        )
        self.wait(2.0)

        # Clear the challenge scene
        challenge_all = VGroup(
            ch_header, table, table_top,
            empty_bottle, full_bottle, empty_tag, full_tag,
            push_arr_e, push_lbl_e, push_arr_f, push_lbl_f,
            verdict
        )
        self.play(FadeOut(challenge_all, shift=UP * 0.15), run_time=0.9)