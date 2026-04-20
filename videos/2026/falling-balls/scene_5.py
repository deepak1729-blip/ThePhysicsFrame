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
    Returns a VGroup that looks like a lit 3-D sphere.
    """
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

# ═══════════════════════════════════════════════════════════════════
#  SCENE 5 · The Math Agrees
# ═══════════════════════════════════════════════════════════════════

class Scene5_TheMathAgrees(Scene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        self.add(grid)

        # ──────────────────────────────────────────────────────────
        # ACT 1 · THE EQUATION BREAKDOWN (UPDATED)
        # ──────────────────────────────────────────────────────────

        equation = MathTex(
            "s", "=", "ut", "+", r"\frac{1}{2}", "a", "t^2",
            font_size=42,
            color=COLOR_WHITE
        ).move_to(ORIGIN).set_z_index(10)
        self.add(equation)

        title = Text("Newton's 2nd Equation of Motion", font="Segoe UI", font_size=32, color=COLOR_WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.8)
        self.play(FadeIn(title, shift=DOWN*0.2))
        self.wait()

        # ──────────────────────────────────────────────────────────
        # ACT 2 · REMOVING INITIAL VELOCITY (ut)
        # ──────────────────────────────────────────────────────────

        new_layout = VGroup(equation[0:2].copy(), equation[4:7].copy())
        new_layout.arrange(RIGHT, buff=0.2).move_to(ORIGIN)

        self.play(
            FadeOut(equation[2], shift=UP * 0.6),
            FadeOut(equation[3], scale=0.3),
            equation[0:2].animate.move_to(new_layout[0]),
            equation[4:7].animate.move_to(new_layout[1]),
            run_time=1.2,
            rate_func=smooth
        )
        self.wait()

        # ──────────────────────────────────────────────────────────
        # ACT 3 · ACCELERATION BECOMES GRAVITY (a -> g)
        # ──────────────────────────────────────────────────────────

        g_char = MathTex("g", font_size=42, color=COLOR_AMBER)
        
        g_char.move_to(equation[5]).align_to(equation[5], UP)

        self.play(
            equation[5].animate.set_color(COLOR_AMBER),
            run_time=0.3
        )

        self.play(
            Transform(equation[5], g_char, path_arc=0.3),
            run_time=0.8,
            rate_func=smooth
        )

        self.play(
            equation[5].animate.set_color(COLOR_WHITE),
            run_time=0.4,
            rate_func=rate_functions.ease_in_sine
        )
        self.wait()

        h_char = MathTex("h", font_size=42, color=COLOR_AMBER)
        h_char.move_to(equation[0]).align_to(equation[0], UP)
        self.play(
            Transform(equation[0], h_char),
            run_time=0.8,
            rate_func=smooth
        )
        self.wait()

        # ──────────────────────────────────────────────────────────
        # ACT 4 · ISOLATING THE TIME VARIABLE (t)
        # ──────────────────────────────────────────────────────────

        eq_t_squared = MathTex("t^2", "=", r"\frac{2h}{g}", font_size=42, color=COLOR_WHITE)

        eq_t_squared[0].set_color(COLOR_VEC_V_X) 

        current_visible = VGroup(equation[0:2], equation[4:7])

        self.play(
            TransformMatchingShapes(current_visible, eq_t_squared, path_arc=0.4),
            run_time=1.5,
            rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.5)

        eq_t_final = MathTex("t", "=", r"\sqrt{\frac{2h}{g}}", font_size=42, color=COLOR_WHITE)
        eq_t_final[0].set_color(COLOR_VEC_V_X) 

        self.play(
            TransformMatchingShapes(eq_t_squared, eq_t_final),
            run_time=2,
            rate_func=rate_functions.ease_out_back 
        )
        self.wait(0.5)

        self.play(
            eq_t_final[0].animate.set_color(COLOR_WHITE),
            run_time=0.5,
            rate_func=rate_functions.ease_in_sine
        )
        self.wait()

        # ACT 5 NO HORIZONTAL VELOCITY

        self.play(
            eq_t_final.animate.shift(LEFT * 1.5),
            run_time=1.2,
            rate_func=rate_functions.ease_in_out_sine
        )

        insight_title = Text("KEY INSIGHT", font="Segoe UI", font_size=18, color=COLOR_GROUND, weight=BOLD)
        
        row1_text = Text("Depends only on height", font="Segoe UI", font_size=22, color=COLOR_WHITE)
        row1_var = MathTex("h", font_size=36, color=COLOR_GREEN)
        row1 = VGroup(row1_text, row1_var).arrange(RIGHT, buff=0.2)

        row2_text = Text("Independent of", font="Segoe UI", font_size=22, color=COLOR_WHITE)
        row2_var = MathTex("v_x", font_size=36, color=COLOR_VEC_V_X)
        row2 = VGroup(row2_text, row2_var).arrange(RIGHT, buff=0.2)

        content = VGroup(insight_title, row1, row2).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        
        card = text_bg(
            content, 
            fill_color=COLOR_BG, 
            fill_opacity=0.75, 
            pad_x=0.6, pad_y=0.5, 
            stroke=True, stroke_color=COLOR_GROUND, stroke_opacity=0.4
        )
        card.next_to(eq_t_final, RIGHT, buff=1.0)

        card.scale(0.8)
        self.play(
            FadeIn(card, shift=LEFT * 0.4),
            card.animate.scale(1 / 0.8),
            run_time=1.2,
            rate_func=rate_functions.ease_out_back
        )
        self.wait(0.5)

        self.play(
            Indicate(row1_var, color=COLOR_GREEN, scale_factor=1.2),
            run_time=0.8
        )
        self.wait(0.2)

        strike_line = Line(
            row2_var.get_bottom() + LEFT * 0.15, 
            row2_var.get_top() + RIGHT * 0.15, 
            color=COLOR_PINK, 
            stroke_width=4
        )
        self.play(
            Create(strike_line), 
            run_time=0.5, 
            rate_func=rate_functions.ease_out_sine
        )
        
        self.wait(2)

        # ──────────────────────────────────────────────────────────
        # ACT 6 · SETTING THE STAGE FOR THE DROP
        # ──────────────────────────────────────────────────────────

        self.play(
            FadeOut(card, shift=RIGHT * 0.5),
            FadeOut(strike_line),
            
            eq_t_final.animate.scale(0.7).to_corner(UR, buff=0.6),
            
            run_time=1.2,
            rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.5)

        START_Y = 2.5
        GROUND_Y = -3.0
        START_X = -5.0
        t_final = 2.0
        drop_dist = START_Y - (GROUND_Y + 0.28)
        G_VAL = 2 * drop_dist / (t_final ** 2)

        ground = Line(start=LEFT*7, end=RIGHT*7, color=COLOR_GROUND, stroke_width=2)
        ground.to_edge(DOWN, buff=1)

        self.play(Create(ground), run_time=1.0, rate_func=rate_functions.ease_out_sine)

        b1 = make_ball(COLOR_GREY_BALL).set_z_index(3).move_to([START_X, START_Y, 0])
        b2 = make_ball(COLOR_BLUE_BALL).set_z_index(2).move_to([START_X, START_Y, 0])
        b3 = make_ball(COLOR_PINK).set_z_index(1).move_to([START_X, START_Y, 0])

        self.wait(0.5)

        self.play(
            FadeIn(b1, shift=DOWN*0.3), 
            FadeIn(b2, shift=DOWN*0.3), 
            FadeIn(b3, shift=DOWN*0.3),
            run_time=0.8,
            rate_func=rate_functions.ease_out_back
        )

        self.wait(1)

        v1, v2, v3 = 0.0, 2.8, 5.0

        t_tracker = ValueTracker(0)

        def make_updater(mob, vx):
            def updater(m):
                t = t_tracker.get_value()
                x = START_X + vx * t
                y = START_Y - 0.5 * G_VAL * (t ** 2)
                m.move_to([x, y, 0])
            return updater

        b1.add_updater(make_updater(b1, v1))
        b2.add_updater(make_updater(b2, v2))
        b3.add_updater(make_updater(b3, v3))

        # Trail paths
        trail1 = TracedPath(b1.get_center, stroke_width=2, stroke_color=COLOR_GREY_BALL, stroke_opacity=0.4).set_z_index(1)
        trail2 = TracedPath(b2.get_center, stroke_width=2, stroke_color=COLOR_BLUE_BALL, stroke_opacity=0.4).set_z_index(1)
        trail3 = TracedPath(b3.get_center, stroke_width=2, stroke_color=COLOR_PINK, stroke_opacity=0.4).set_z_index(1)
        self.add(trail1, trail2, trail3)

        self.play(t_tracker.animate.set_value(t_final), run_time=2.0, rate_func=linear)

        b1.clear_updaters()
        b2.clear_updaters()
        b3.clear_updaters()

        rip1 = Circle(radius=0.3, color=COLOR_GREY_BALL, stroke_width=3).move_to(b1.get_center())
        rip2 = Circle(radius=0.3, color=COLOR_BLUE_BALL, stroke_width=3).move_to(b2.get_center())
        rip3 = Circle(radius=0.3, color=COLOR_PINK, stroke_width=3).move_to(b3.get_center())
        self.play(
            rip1.animate.scale(3).set_opacity(0),
            rip2.animate.scale(3).set_opacity(0),
            rip3.animate.scale(3).set_opacity(0),
            run_time=0.6, rate_func=rate_functions.ease_out_quad
        )
        self.wait(1.5)

        # Clean up
        self.play(
            FadeOut(b1), FadeOut(b2), FadeOut(b3),
            FadeOut(trail1), FadeOut(trail2), FadeOut(trail3),
            FadeOut(ground)
        )

        # ══════════════════════════════════════════════════════════════════
        #  ACT 7 · HORIZONTAL WORLD — "Let's look at the horizontal side..."
        # ══════════════════════════════════════════════════════════════════

        BLUE_VERT  = COLOR_BLUE_BALL   
        ORG_HORIZ  = "#FF9500"       
        GOLD_TIME  = COLOR_AMBER

        self.play(
            FadeOut(title),
            FadeOut(eq_t_final),
            run_time=0.7,
            rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.3)

        act7_header = Text(
            "Let's look at the horizontal side...",
            font="Segoe UI", font_size=26, color=COLOR_WHITE
        ).to_edge(UP, buff=0.75)
        self.play(FadeIn(act7_header, shift=DOWN * 0.2))
        self.wait(0.8)

        eq_horiz = MathTex(
            "x", "=", "v_0", r"\cdot", "t",
            font_size=56, color=COLOR_WHITE
        ).move_to(ORIGIN)

        words = ["distance", "=", "speed", "×", "time"]

        sub_horiz = VGroup(*[
        Text(word, font="Segoe UI", font_size=20, color=COLOR_GROUND)
        for word in words
        ]).arrange(RIGHT, buff=0.4).next_to(eq_horiz, DOWN, buff=0.6)

        self.play(Write(eq_horiz), run_time=2.0, rate_func=smooth)
        self.wait(0.5)
        self.play(
        LaggedStart(
        *[FadeIn(word, shift=UP * 0.2) for word in sub_horiz],
        lag_ratio=0.4 
        ),
        run_time=1.5
        )
        self.wait(2.0)

        # ══════════════════════════════════════════════════════════════════
        #  ACT 8 · G IS MISSING — "Horizontal motion ko gravity se koi matlab nahi"
        # ══════════════════════════════════════════════════════════════════

        g_query = MathTex("g", "=", "?", font_size=44, color=COLOR_AMBER)
        g_query.next_to(eq_horiz, RIGHT, buff=1.5)

        self.play(FadeIn(g_query, shift=LEFT * 0.3), run_time=0.7)
        self.wait(0.8)

        xline_a = Line(
            g_query[0].get_corner(UR) + RIGHT * 0.06,
            g_query[0].get_corner(DL) + LEFT * 0.06,
            color=COLOR_PINK, stroke_width=3.5
        )
        self.play(Create(xline_a), run_time=0.4)
        self.wait(1.8)

        self.play(
            FadeOut(sub_horiz),
            FadeOut(g_query),
            FadeOut(xline_a),
            FadeOut(act7_header),
            run_time=0.7
        )

        # ══════════════════════════════════════════════════════════════════
        #  ACT 9 · TWO WORLDS SIDE BY SIDE
        # ══════════════════════════════════════════════════════════════════

        lbl_vert = Text(
            "VERTICAL", font="Segoe UI", font_size=15,
            color=BLUE_VERT, weight=BOLD
        )
        eq_vert_card = MathTex(
            "h", "=", r"\frac{1}{2}", "g", "t^2",
            font_size=44, color=COLOR_WHITE
        )
        eq_vert_card[3].set_color(BLUE_VERT)   # g  → blue
        eq_vert_card[4].set_color(GOLD_TIME)   # t² → gold

        dep_vert = Text(
            "Depends on  g  and  t",
            font="Segoe UI", font_size=15, color=COLOR_GROUND
        )

        vert_inner = VGroup(lbl_vert, eq_vert_card, dep_vert).arrange(
            DOWN, buff=0.38, aligned_edge=LEFT
        )
        vert_card_bg = RoundedRectangle(
            corner_radius=0.18,
            width=vert_inner.width + 1.1,
            height=vert_inner.height + 0.9,
            fill_color=COLOR_BG, fill_opacity=0.92,
            stroke_width=2.5, stroke_color=BLUE_VERT, stroke_opacity=0.8
        ).move_to(vert_inner.get_center()).set_z_index(vert_inner.get_z_index() - 1)

        vert_card = VGroup(vert_card_bg, vert_inner)
        vert_card.move_to(LEFT * 3.3)

        lbl_horiz_card = Text(
            "HORIZONTAL", font="Segoe UI", font_size=15,
            color=ORG_HORIZ, weight=BOLD
        )
        eq_horiz_card = MathTex(
            "x", "=", "v_0", "t",
            font_size=44, color=COLOR_WHITE
        )
        eq_horiz_card[2].set_color(ORG_HORIZ)  
        eq_horiz_card[3].set_color(GOLD_TIME)  

        dep_horiz_card = Text(
            "Depends on  v₀  and  t",
            font="Segoe UI", font_size=15, color=COLOR_GROUND
        )

        horiz_inner = VGroup(lbl_horiz_card, eq_horiz_card, dep_horiz_card).arrange(
            DOWN, buff=0.38, aligned_edge=LEFT
        )
        horiz_inner.move_to(RIGHT * 3.3)

        horiz_card_bg = RoundedRectangle(
            corner_radius=0.18,
            width=horiz_inner.width + 1.1,
            height=horiz_inner.height + 0.9,
            fill_color=COLOR_BG, fill_opacity=0.92,
            stroke_width=2.5, stroke_color=ORG_HORIZ, stroke_opacity=0.8
        ).move_to(horiz_inner.get_center()).set_z_index(horiz_inner.get_z_index() - 1)

        self.play(
            eq_horiz.animate.move_to(eq_horiz_card.get_center()),
            run_time=0.9, rate_func=smooth
        )

        self.play(
            TransformMatchingShapes(eq_horiz, eq_horiz_card),
            FadeIn(vert_card, shift=RIGHT * 0.4),
            FadeIn(horiz_card_bg),
            FadeIn(lbl_horiz_card, shift=DOWN * 0.2),
            FadeIn(dep_horiz_card, shift=UP * 0.2),
            run_time=1.5, rate_func=smooth
        )
        self.wait(1.8)

        two_worlds_txt = Text(
            "Both equations are living in separate worlds...",
            font="Segoe UI", font_size=20, color=COLOR_GROUND
        ).to_edge(DOWN, buff=1.1)
        self.play(FadeIn(two_worlds_txt, shift=UP * 0.2), run_time=0.7)
        self.wait(2.0)

        # ══════════════════════════════════════════════════════════════════
        #  ACT 10 · TIME — THE BRIDGE
        # ══════════════════════════════════════════════════════════════════

        self.play(
            Indicate(eq_vert_card[4],  color=GOLD_TIME, scale_factor=1.55),
            Indicate(eq_horiz_card[3], color=GOLD_TIME, scale_factor=1.55),
            run_time=1.1
        )
        self.wait(0.3)

        t_pos_L = eq_vert_card[4].get_center()  + UP * 0.15
        t_pos_R = eq_horiz_card[3].get_center() + UP * 0.15

        bridge = ArcBetweenPoints(
            t_pos_L, t_pos_R,
            angle=-TAU / 6,
            color=GOLD_TIME,
            stroke_width=3.5
        )
        bridge_glow = ArcBetweenPoints(
            t_pos_L, t_pos_R,
            angle=-TAU / 6,
            color=GOLD_TIME,
            stroke_width=12,
            stroke_opacity=0.15
        )
        bridge_label = Text(
            "TIME  —  The Bridge",
            font="Segoe UI", font_size=26, color=GOLD_TIME, weight=BOLD
        ).next_to(bridge, UP, buff=0.38)

        self.play(
            Create(bridge),
            FadeIn(bridge_glow),
            run_time=1.0, rate_func=rate_functions.ease_out_sine
        )
        self.play(FadeIn(bridge_label, shift=DOWN * 0.2), run_time=0.7)
        self.wait(2.8)

        self.play(FadeOut(two_worlds_txt), run_time=0.5)

        secret_box = text_bg(
            Text("Solve Separately. Connect via Time.", font="Segoe UI", font_size=22, color=COLOR_WHITE),
            fill_color=COLOR_BG, fill_opacity=0.9, pad_x=0.6, pad_y=0.4, 
            stroke=True, stroke_color=COLOR_BLUE_BALL
        )
        secret_box.to_edge(DOWN, buff=0.8)
        
        self.play(FadeIn(secret_box, shift=UP*0.5), run_time=1, rate_func=rate_functions.ease_out_back)
        self.wait(2.5)

        horiz_all = VGroup(horiz_card_bg, lbl_horiz_card, eq_horiz_card, dep_horiz_card)
        self.play(
            FadeOut(vert_card),
            FadeOut(horiz_all),
            FadeOut(bridge),
            FadeOut(bridge_glow),
            FadeOut(bridge_label),
            FadeOut(secret_box)
        )
        # ══════════════════════════════════════════════════════════════════
        #  ACT 13 · NEWTON'S 2ND LAW — Force acts only in its own direction
        # ══════════════════════════════════════════════════════════════════

        newt_title = Text(
            "Newton's 2nd Law:",
            font="Segoe UI", font_size=24, color=COLOR_WHITE, weight=BOLD
        ).to_edge(UP, buff=0.9)
        self.play(FadeIn(newt_title, shift=DOWN * 0.2), run_time=0.6)

        f_eq = MathTex(r"\vec{F}", "=", "m", r"\vec{a}", font_size=56, color=COLOR_WHITE)
        f_eq.move_to(ORIGIN + UP * 0.7)
        self.play(Write(f_eq), run_time=2.0, rate_func=smooth)

        direction_note = Text(
            "Acceleration only in the direction of force",
            font="Segoe UI", font_size=22, color=COLOR_AMBER
        ).next_to(f_eq, DOWN, buff=0.5)
        self.play(FadeIn(direction_note, shift=UP * 0.2), run_time=1.5)
        self.wait(1.8)

        content_group = VGroup(f_eq, direction_note)

        BALL_POS2 = np.array([0.0, 0.5, 0])
        demo_ball3 = make_ball(COLOR_BLUE_BALL).move_to(BALL_POS2).set_z_index(5)

        self.play(
            ReplacementTransform(content_group, demo_ball3), 
            run_time=1.5
        )

        self.remove(content_group)

        g_arrow2 = Arrow(
            start=BALL_POS2,
            end=BALL_POS2 + DOWN * 2.0,
            color=COLOR_VEC_G, stroke_width=6,
            max_tip_length_to_length_ratio=0.16
        ).set_z_index(4)
        g_arrow_lbl = MathTex("g", font_size=36, color=COLOR_VEC_G)
        g_arrow_lbl.next_to(g_arrow2, RIGHT, buff=0.2)

        self.play(GrowArrow(g_arrow2), FadeIn(g_arrow_lbl), run_time=0.9)
        self.wait(0.8)

        no_horiz_txt = Text(
            "← No horizontal force →",
            font="Segoe UI", font_size=20, color=COLOR_GROUND
        ).next_to(demo_ball3, UP, buff=0.55)
        self.play(FadeIn(no_horiz_txt, shift=DOWN * 0.15), run_time=0.6)
        self.wait(1.0)

        consequence = Text(
            "∴  Horizontal speed never changes",
            font="Segoe UI", font_size=24, color=COLOR_GREEN
        ).to_edge(DOWN, buff=1.2)
        self.play(FadeIn(consequence, shift=UP * 0.2), run_time=0.7)
        self.wait(2.2)

        fall_dep = Text(
            "Time to fall depends only on  g  and  h  (not horizontal speed)",
            font="Segoe UI", font_size=20, color=COLOR_WHITE
        ).to_edge(DOWN, buff=1.5)
        self.play(
            FadeOut(consequence),
            FadeIn(fall_dep, shift=UP * 0.2),
            run_time=0.7
        )
        self.wait(2.5)

        self.play(
            FadeOut(demo_ball3),
            FadeOut(g_arrow2),
            FadeOut(g_arrow_lbl),
            FadeOut(no_horiz_txt),
            FadeOut(fall_dep),
            FadeOut(newt_title),
            run_time=0.9
        )