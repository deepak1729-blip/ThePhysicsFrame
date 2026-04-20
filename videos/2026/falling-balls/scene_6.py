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
COLOR_PINK      = "#FF2D55"
COLOR_WHITE     = "#E5E5EA"
COLOR_PURPLE    = "#BF5AF2"


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
            t = (i + 0.5) / N
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
    spec.move_to(np.array([-radius * 0.28, radius * 0.30, 0]))
    spec.rotate(-20 * DEGREES)
    g.add(spec)
    return g


# ═══════════════════════════════════════════════════════════════════
#  SCENE 6 · The Takeaway  (Final)
# ═══════════════════════════════════════════════════════════════════

class Scene6_TheTakeaway(Scene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # ──────────────────────────────────────────────────────────
        # AMBIENT CLOCK (drives breathing animations)
        # ──────────────────────────────────────────────────────────
        clock = ValueTracker(0)
        clock_driver = Mobject()
        clock_driver.add_updater(lambda m, dt: clock.increment_value(dt))
        self.add(clock_driver)

        # ──────────────────────────────────────────────────────────
        # SOFT RADIAL PULSE — act divider
        # ──────────────────────────────────────────────────────────
        def act_pulse(color=COLOR_WHITE, duration=0.8):
            ring = Circle(radius=0.2, color=color,
                          stroke_width=2, stroke_opacity=0.0).move_to(ORIGIN)
            ring.set_z_index(15)
            self.add(ring)
            self.play(
                ring.animate.scale(40).set_stroke(width=0.3, opacity=0),
                rate_func=rate_functions.ease_out_expo,
                run_time=duration
            )
            self.remove(ring)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · OPENING — Radial burst → Title cascade
        # ══════════════════════════════════════════════════════════

        burst_rings = VGroup()
        for i in range(3):
            ring = Circle(radius=0.05, color=COLOR_GREEN,
                          stroke_width=3, stroke_opacity=0.0)
            burst_rings.add(ring)
        self.add(burst_rings)

        self.play(
            AnimationGroup(
                *[
                    AnimationGroup(
                        ring.animate.scale(60).set_stroke(
                            width=0.5, opacity=0
                        ),
                        run_time=1.8,
                        rate_func=rate_functions.ease_out_expo
                    )
                    for ring in burst_rings
                ],
                lag_ratio=0.18
            ),
            run_time=1.8,
        )
        self.remove(burst_rings)

        # Eyebrow label
        eyebrow = Text(
            "ONE THING TO REMEMBER",
            font="Segoe UI", font_size=18,
            weight=BOLD, color=COLOR_GROUND
        )
        eyebrow_line_l = Line(LEFT * 0.6, ORIGIN,
                              color=COLOR_GROUND, stroke_width=1, stroke_opacity=0.6)
        eyebrow_line_r = Line(ORIGIN, RIGHT * 0.6,
                              color=COLOR_GROUND, stroke_width=1, stroke_opacity=0.6)
        eyebrow_line_l.next_to(eyebrow, LEFT, buff=0.25)
        eyebrow_line_r.next_to(eyebrow, RIGHT, buff=0.25)
        eyebrow_group = VGroup(eyebrow_line_l, eyebrow, eyebrow_line_r)
        eyebrow_group.move_to(UP * 1.1)

        self.play(
            FadeIn(eyebrow, shift=UP * 0.15),
            Create(eyebrow_line_l), Create(eyebrow_line_r),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic
        )

        # Main title — letter-by-letter cascade
        title = Text(
            "The Key Takeaway",
            font="Segoe UI", font_size=66,
            weight=BOLD, color=COLOR_WHITE
        ).move_to(ORIGIN)

        letter_anims = []
        for letter in title:
            letter.save_state()
            letter.shift(DOWN * 0.4).set_opacity(0).rotate(-8 * DEGREES)
            letter_anims.append(Restore(letter, rate_func=rate_functions.ease_out_back))

        self.play(
            LaggedStart(*letter_anims, lag_ratio=0.06),
            run_time=1.4
        )
        self.wait(1.5)

        header_full = VGroup(eyebrow_group, title)

        self.play(
            header_full.animate.scale(0.52).to_edge(UP, buff=0.4).set_opacity(0.72),
            run_time=1.1,
            rate_func=rate_functions.ease_in_out_quint
        )

        act_pulse(color=COLOR_GREEN, duration=0.7)

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · PRINCIPLE 01 — Step back. Visualize.
        # ══════════════════════════════════════════════════════════

        big_01 = Text("01", font="Segoe UI", font_size=240,
                      weight=BOLD, color=COLOR_WHITE)
        big_01.set_opacity(0.06).move_to(LEFT * 3.8 + DOWN * 0.3)

        num_badge = Text("01", font="Segoe UI", font_size=28,
                         weight=BOLD, color=COLOR_GREEN)
        num_underline = Line(LEFT * 0.35, RIGHT * 0.35,
                             color=COLOR_GREEN, stroke_width=2)
        num_underline.next_to(num_badge, DOWN, buff=0.12)
        num_group = VGroup(num_badge, num_underline)

        p1_head = Text(
            "Step back and Visualize.",
            font="Segoe UI", font_size=48,
            weight=BOLD, color=COLOR_WHITE
        )
        p1_sub = Text(
            "Don't rush to solve — first see what's actually happening.",
            font="Segoe UI", font_size=22,
            color=COLOR_GROUND
        )

        p1_block = VGroup(num_group, p1_head, p1_sub).arrange(
            DOWN, buff=0.35, aligned_edge=LEFT
        ).move_to(ORIGIN + DOWN * 0.1)

        self.play(
            FadeIn(big_01, shift=RIGHT * 0.4),
            run_time=1.0,
            rate_func=rate_functions.ease_out_expo
        )

        self.play(
            FadeIn(num_badge, shift=UP * 0.25),
            GrowFromCenter(num_underline),
            run_time=0.5
        )

        self.play(
            LaggedStart(
                FadeIn(p1_head[:10], shift=UP * 0.25),
                FadeIn(p1_head[10:], shift=UP * 0.25),
                lag_ratio=0.4
            ),
            run_time=2.5,
            rate_func=rate_functions.ease_out_cubic
        )

        self.play(FadeIn(p1_sub, shift=UP * 0.15), run_time=0.7)

        self.wait(2.2)

        self.play(
            FadeOut(p1_block, shift=UP * 0.3),
            FadeOut(big_01, shift=LEFT * 0.4),
            run_time=0.7,
            rate_func=rate_functions.ease_in_cubic
        )

        act_pulse(color=COLOR_AMBER, duration=0.7)

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · PRINCIPLE 02 — Break it down. (with hero visual)
        # ══════════════════════════════════════════════════════════

        big_02 = Text("02", font="Segoe UI", font_size=240,
                      weight=BOLD, color=COLOR_WHITE)
        big_02.set_opacity(0.06).move_to(RIGHT * 3.8 + UP * 1.2)

        num_badge2 = Text("02", font="Segoe UI", font_size=28,
                          weight=BOLD, color=COLOR_AMBER)
        num_underline2 = Line(LEFT * 0.35, RIGHT * 0.35,
                              color=COLOR_AMBER, stroke_width=2)
        num_underline2.next_to(num_badge2, DOWN, buff=0.12)
        num_group2 = VGroup(num_badge2, num_underline2)

        p2_head = Text(
            "Break it down.",
            font="Segoe UI", font_size=48,
            weight=BOLD, color=COLOR_WHITE
        )

        p2_top = VGroup(num_group2, p2_head).arrange(
            DOWN, buff=0.3, aligned_edge=LEFT
        ).move_to(UP * 2.1 + LEFT * 3.2)

        self.play(
            FadeIn(big_02, shift=LEFT * 0.4),
            run_time=0.7,
            rate_func=rate_functions.ease_out_expo
        )
        self.play(
            FadeIn(num_badge2, shift=UP * 0.2),
            GrowFromCenter(num_underline2),
            run_time=0.5
        )
        self.play(
            LaggedStart(
                *[FadeIn(letter, shift=UP * 0.2) for letter in p2_head],
                lag_ratio=0.04
            ),
            run_time=0.9
        )

        # HERO VISUAL — projectile box cracks into vertical + horizontal
        big_box = RoundedRectangle(
            corner_radius=0.2, width=3.0, height=1.8,
            stroke_color=COLOR_BLUE_BALL, stroke_width=3, stroke_opacity=0.9,
            fill_color=COLOR_BLUE_BALL, fill_opacity=0.04
        ).move_to(ORIGIN + DOWN * 0.8)

        big_box_label = Text(
            "Projectile",
            font="Segoe UI", font_size=22,
            weight=BOLD, color=COLOR_BLUE_BALL
        ).move_to(big_box.get_center() + UP * 0.3)
        tiny_ball = make_ball(COLOR_BLUE_BALL, radius=0.14).move_to(
            big_box.get_center() + DOWN * 0.3
        )

        self.play(
            # FadeIn(big_box_glow),
            FadeIn(big_box_label, shift=UP * 0.15),
            FadeIn(tiny_ball, scale=0.5),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(0.4)

        # THE SPLIT
        flash_line = Line(
            big_box.get_top() + UP * 0.05,
            big_box.get_bottom() + DOWN * 0.05,
            color=COLOR_WHITE, stroke_width=0, stroke_opacity=0
        )
        self.add(flash_line)
        self.play(
            flash_line.animate.set_stroke(width=6, opacity=1),
            run_time=0.2,
            rate_func=rate_functions.ease_out_expo
        )

        def make_small_box(color, label_txt, eq_tex, target_pos):
            box = RoundedRectangle(
                corner_radius=0.18, width=2.5, height=1.5,
                stroke_color=color, stroke_width=2.5, stroke_opacity=0.9,
                fill_color=color, fill_opacity=0.05
            ).move_to(target_pos)
            lbl = Text(label_txt, font="Segoe UI", font_size=18,
                       weight=BOLD, color=color).move_to(box.get_top() + DOWN * 0.28)
            eq = MathTex(eq_tex, font_size=34,
                         color=COLOR_WHITE).move_to(box.get_center() + DOWN * 0.15)
            return VGroup(box, lbl, eq)

        small_v = make_small_box(
            COLOR_VEC_G, "Vertical", r"h = \tfrac{1}{2} g t^2",
            LEFT * 3.2 + DOWN * 1.0
        )
        small_h = make_small_box(
            COLOR_VEC_V_X, "Horizontal", r"x = v_0 \, t",
            RIGHT * 3.2 + DOWN * 1.0
        )
       
        self.play(
            flash_line.animate.set_stroke(width=0, opacity=0).scale(3),
            FadeOut(big_box_label, scale=0.8),
            FadeOut(tiny_ball, scale=0.3),
            TransformFromCopy(big_box, small_v[0]),
            TransformFromCopy(big_box, small_h[0]),
            run_time=0.9,
            rate_func=rate_functions.ease_out_expo
        )
        self.remove(flash_line)

        self.play(
            FadeIn(small_v[1], shift=DOWN * 0.15),
            FadeIn(small_h[1], shift=DOWN * 0.15),
            Write(small_v[2]),
            Write(small_h[2]),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic
        )

        def box_breath_v(mob):
            s = 0.18 + 0.08 * np.sin(clock.get_value() * 2.2)
            for halo in mob:
                halo.set_stroke(opacity=s)

        def box_breath_h(mob):
            s = 0.18 + 0.08 * np.sin(clock.get_value() * 2.2 + PI)
            for halo in mob:
                halo.set_stroke(opacity=s)

        self.wait(2.0)

        act3_all = VGroup(
            big_02, p2_top,
            small_v, small_h
        )
        self.play(
            FadeOut(act3_all, shift=DOWN * 0.3),
            run_time=0.8,
            rate_func=rate_functions.ease_in_cubic
        )

        act_pulse(color=COLOR_GREEN, duration=0.7)

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · THE BIG IDEA — "Most physics problems..."
        # ══════════════════════════════════════════════════════════

        line_a = Text(
            "Most physics problems",
            font="Segoe UI", font_size=40, color=COLOR_GROUND
        )
        line_b = Text(
            "are really just visualization problems.",
            font="Segoe UI", font_size=40, color=COLOR_WHITE,
            weight=BOLD,
            t2c={"visualization": COLOR_GREEN}
        )
        big_idea = VGroup(line_a, line_b).arrange(DOWN, buff=0.35).move_to(UP * 0.2)

        line_a.save_state()
        line_b.save_state()
        line_a.scale(1.25).set_opacity(0)
        line_b.scale(1.25).set_opacity(0)

        self.play(
            Restore(line_a),
            run_time=1.0,
            rate_func=rate_functions.ease_out_quint
        )
        self.play(
            Restore(line_b),
            run_time=1.2,
            rate_func=rate_functions.ease_out_quint
        )

        self.wait(3.0)

        self.play(
            FadeOut(big_idea, shift=UP * 0.3),
            run_time=0.8,
            rate_func=rate_functions.ease_in_cubic
        )

        act_pulse(color=COLOR_BLUE_BALL, duration=0.7)

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · WHAT'S NEXT — teaser with soft corner accents
        # ══════════════════════════════════════════════════════════

        next_eyebrow = Text(
            "WHAT'S NEXT?",
            font="Segoe UI", font_size=18,
            weight=BOLD, color=COLOR_GROUND
        )
        next_eyebrow_l = Line(LEFT * 0.5, ORIGIN,
                              color=COLOR_GROUND, stroke_width=1, stroke_opacity=0.6)
        next_eyebrow_r = Line(ORIGIN, RIGHT * 0.5,
                              color=COLOR_GROUND, stroke_width=1, stroke_opacity=0.6)
        next_eyebrow_l.next_to(next_eyebrow, LEFT, buff=0.25)
        next_eyebrow_r.next_to(next_eyebrow, RIGHT, buff=0.25)
        next_eyebrow_group = VGroup(next_eyebrow_l, next_eyebrow, next_eyebrow_r)

        next_head = Text(
            "More problems. Pure visualization.",
            font="Segoe UI", font_size=40,
            weight=BOLD, color=COLOR_WHITE
        )
        next_sub = Text(
            "We'll keep solving them the way they're meant to be solved — by seeing them.",
            font="Segoe UI", font_size=20,
            color=COLOR_GROUND
        )
        next_group = VGroup(next_eyebrow_group, next_head, next_sub).arrange(
            DOWN, buff=0.45
        ).move_to(ORIGIN)

        bracket_len = 0.45
        bracket_color = COLOR_BLUE_BALL
        bracket_width = 2

        frame_w = next_head.width / 2 + 0.8
        frame_h = next_group.height / 2 + 0.5
        c = next_group.get_center()

        def corner_bracket(origin, dx, dy):
            h_line = Line(origin, origin + RIGHT * dx * bracket_len,
                          color=bracket_color, stroke_width=bracket_width,
                          stroke_opacity=0.55)
            v_line = Line(origin, origin + UP * dy * bracket_len,
                          color=bracket_color, stroke_width=bracket_width,
                          stroke_opacity=0.55)
            return VGroup(h_line, v_line)

        tl = corner_bracket(c + LEFT * frame_w + UP * frame_h,  1, -1)
        tr = corner_bracket(c + RIGHT * frame_w + UP * frame_h, -1, -1)
        bl = corner_bracket(c + LEFT * frame_w + DOWN * frame_h,  1, 1)
        br = corner_bracket(c + RIGHT * frame_w + DOWN * frame_h, -1, 1)
        corners = VGroup(tl, tr, bl, br)

        self.play(
            LaggedStart(
                Create(tl), Create(tr), Create(bl), Create(br),
                lag_ratio=0.1
            ),
            run_time=0.9,
            rate_func=rate_functions.ease_out_cubic
        )
        self.play(
            FadeIn(next_eyebrow, shift=UP * 0.15),
            Create(next_eyebrow_l), Create(next_eyebrow_r),
            run_time=0.7
        )
        self.play(
            LaggedStart(
                *[FadeIn(letter, shift=UP * 0.2) for letter in next_head],
                lag_ratio=0.025
            ),
            run_time=2.5,
            rate_func=rate_functions.ease_out_cubic
        )
        self.play(FadeIn(next_sub, shift=UP * 0.15), run_time=0.7)

        def corners_breath(mob):
            s = 0.55 + 0.2 * np.sin(clock.get_value() * 1.8)
            for bracket in mob:
                for line in bracket:
                    line.set_stroke(opacity=s)

        corners.add_updater(corners_breath)

        self.wait(2.8)
        corners.clear_updaters()

        # ══════════════════════════════════════════════════════════
        #  FINAL FADE
        # ══════════════════════════════════════════════════════════
        self.play(
            FadeOut(next_group, shift=UP * 0.3),
            FadeOut(corners, shift=UP * 0.3),
            FadeOut(header_full),
            run_time=1.5,
            rate_func=rate_functions.ease_in_out_quint
        )
        self.wait(0.5)