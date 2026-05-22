from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE 
# ─────────────────────────────────────────────
COLOR_BG        = "#1C1C1E"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_GREY_BALL = "#D1D1D6"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F     = "#FF3B30"
COLOR_VEC_V     = "#32ADE6"
COLOR_GREEN     = "#34C759"
COLOR_AMBER     = "#FFCC00"
COLOR_PINK      = "#FF2D55"
COLOR_PURPLE    = "#AF52DE"
COLOR_ORANGE    = "#FF9500"
COLOR_BROWN     = "#A2845E"

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
            op = peak_op * 0.40 * (1 - (2 * t - 1) ** 2)
            segs.add(Line(p1, p2, stroke_opacity=op,
                          stroke_width=1, color=COLOR_WHITE))
        return segs

    for x in np.arange(-max_x, max_x + 0.1, spacing):
        peak = 0.35 * (1 - (abs(x) / max_x) ** 1.5)
        if peak > 0:
            grid.add(fading_line(UP * max_y + RIGHT * x,
                                 DOWN * max_y + RIGHT * x, peak))
    for y in np.arange(-max_y, max_y + 0.1, spacing):
        peak = 0.35 * (1 - (abs(y) / max_y) ** 1.5)
        if peak > 0:
            grid.add(fading_line(LEFT * max_x + UP * y,
                                 RIGHT * max_x + UP * y, peak))
    return grid

# ═══════════════════════════════════════════════════════════════════
#  SCENE 3 · Horse–Cart 
# ═══════════════════════════════════════════════════════════════════

class Scene3_HorseCartFBD(MovingCameraScene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · DYNAMIC INTRO
        # ══════════════════════════════════════════════════════════
        eyebrow_text = Text("BACK TO THE HORSE & CART",
                            font="Segoe UI", font_size=18,
                            weight=BOLD, color=COLOR_GROUND)
        
        eb_l = Line(eyebrow_text.get_left() + LEFT * 0.3, eyebrow_text.get_left() + LEFT * 0.85, 
                    color=COLOR_GROUND, stroke_width=2, stroke_opacity=0.7)
        eb_r = Line(eyebrow_text.get_right() + RIGHT * 0.3, eyebrow_text.get_right() + RIGHT * 0.85, 
                    color=COLOR_GROUND, stroke_width=2, stroke_opacity=0.7)
        
        eyebrow = VGroup(eb_l, eyebrow_text, eb_r).to_edge(UP, buff=0.55)
        
        self.play(
            Write(eyebrow_text),
            Create(eb_l), 
            Create(eb_r),
            run_time=2.0,
            rate_func=rate_functions.ease_out_back
        )

        ground_y = -2.2
        ground = Line(
            LEFT * 6.5 + UP * ground_y, RIGHT * 6.5 + UP * ground_y,
            color=COLOR_GROUND, stroke_width=2, stroke_opacity=0.75
        )
        hatching = VGroup()
        for x in np.arange(-6.2, 6.5, 0.32):
            h = Line(
                np.array([x, ground_y, 0]),
                np.array([x - 0.18, ground_y - 0.25, 0]),
                color=COLOR_GROUND, stroke_width=1.5, stroke_opacity=0.45
            )
            hatching.add(h)
            
        self.play(Create(ground), run_time=0.8)
        self.play(LaggedStartMap(Create, hatching, lag_ratio=0.01), run_time=0.8)

        hc = ImageMobject("horse_cart.png").set_z_index(2)
        hc.scale_to_fit_height(2.6)
        hc.move_to(np.array([0.0, ground_y + hc.height / 2 + 0.05, 0]))

        self.play(FadeIn(hc, shift=UP * 0.3, scale=0.95))
        self.wait(0.5)

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · POPPING VECTORS
        # ══════════════════════════════════════════════════════════
        arr_y = hc.get_top()[1] + 0.40

        # --- F on cart
        F_tail = np.array([-2.40, arr_y, 0])
        F_head = np.array([-0.35, arr_y, 0])
        F_arr = Arrow(F_tail, F_head, color=COLOR_VEC_F, buff=0,
                      stroke_width=6, max_tip_length_to_length_ratio=0.22).set_z_index(4)
        F_lbl = MathTex("F", color=COLOR_VEC_F, font_size=44).next_to(F_arr, UP, buff=0.10).set_z_index(4)
        F_tag = Text("on cart", font="Segoe UI", font_size=20, color=COLOR_GROUND, slant=ITALIC).next_to(F_arr, DOWN, buff=0.12).set_z_index(4)

        self.play(GrowArrow(F_arr), run_time=0.6, rate_func=rate_functions.ease_out_expo)
        self.play(
            FadeIn(F_lbl, shift=DOWN*0.2), 
            FadeIn(F_tag, shift=UP*0.2),
            run_time=0.5
        )

        # --- F' on horse
        Fp_tail = np.array([ 2.40, arr_y, 0])
        Fp_head = np.array([ 0.35, arr_y, 0])
        Fp_arr = Arrow(Fp_tail, Fp_head, color=COLOR_VEC_F, buff=0,
                       stroke_width=6, max_tip_length_to_length_ratio=0.22).set_z_index(4)
        Fp_lbl = MathTex("F'", color=COLOR_VEC_F, font_size=44).next_to(Fp_arr, UP, buff=0.10).set_z_index(4)
        Fp_tag = Text("on horse", font="Segoe UI", font_size=20, color=COLOR_GROUND, slant=ITALIC).next_to(Fp_arr, DOWN, buff=0.12).set_z_index(4)

        self.play(GrowArrow(Fp_arr), run_time=0.6, rate_func=rate_functions.ease_out_expo)
        self.play(
            FadeIn(Fp_lbl, shift=DOWN*0.2), 
            FadeIn(Fp_tag, shift=UP*0.2),
            run_time=0.5
        )
        self.wait(0.8)

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · MORPHING TEXT & SHAKING THE ERROR
        # ══════════════════════════════════════════════════════════
        looks_like = Text("It looks like they cancel...",
                          font="Segoe UI", font_size=22,
                          color=COLOR_GROUND, slant=ITALIC).move_to(np.array([0, 3.45, 0]))

        self.play(
            ReplacementTransform(eyebrow_text, looks_like),
            FadeOut(eb_l, shift=LEFT), FadeOut(eb_r, shift=RIGHT),
            run_time=1.2
        )

        wrong_eq = MathTex("F", "-", "F'", "=", "0", font_size=55, color=COLOR_WHITE)
        wrong_eq[0].set_color(COLOR_VEC_F)
        wrong_eq[2].set_color(COLOR_VEC_F)
        wrong_eq.next_to(looks_like, DOWN, buff=0.28)

        self.play(Write(wrong_eq), run_time=0.8)
        self.wait(0.5)

        strike = Line(
            wrong_eq.get_corner(DL) + LEFT * 0.40 + DOWN * 0.1,
            wrong_eq.get_corner(UR) + RIGHT * 0.40 + UP * 0.1,
            color=COLOR_PINK, stroke_width=6
        )
        
        self.play(Create(strike), rate_func=rate_functions.ease_in_out_expo, run_time=0.3)
        self.play(Wiggle(VGroup(wrong_eq, strike)), run_time=0.6)

        verdict = Text("They act on DIFFERENT bodies.",
                       font="Segoe UI", font_size=28, weight=BOLD,
                       color=COLOR_WHITE,
                       t2c={"DIFFERENT bodies": COLOR_PINK}).next_to(wrong_eq, DOWN, buff=0.40)

        self.play(
            FadeIn(verdict, shift=UP * 0.2),
            Indicate(F_tag, color=COLOR_PINK, scale_factor=1.4),
            Indicate(Fp_tag, color=COLOR_PINK, scale_factor=1.4),
            run_time=1.2
        )
        self.wait(1.2)

        self.play(
            FadeOut(wrong_eq, shift=DOWN*0.2), 
            FadeOut(strike, shift=DOWN*0.2),
            FadeOut(looks_like, shift=UP*0.2)
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · CAMERA ZOOM & CART ISOLATION (No Masks)
        # ══════════════════════════════════════════════════════════
        focus_title = Text("Forces on the CART",
                           font="Segoe UI", font_size=32, weight=BOLD,
                           color=COLOR_WHITE,
                           t2c={"CART": COLOR_AMBER}).to_edge(UP, buff=0.55)
        
        self.play(ReplacementTransform(verdict, focus_title), run_time=0.8)

        fp_group = VGroup(Fp_arr, Fp_lbl, Fp_tag)
        
        # Fade out F' and physically zoom the camera in on the cart
        self.play(
            FadeOut(fp_group, scale=0.5),
            self.camera.frame.animate.scale(0.85).move_to(LEFT * 1.5),
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine
        )

        # Ground friction f exactly at the wheel contact point
        f_contact = np.array([-2.8, ground_y + 0.05, 0])
        f_tail = f_contact + RIGHT * 0.4
        f_head = f_contact + LEFT * 0.6
        f_arr = Arrow(f_tail, f_head, color=COLOR_VEC_F, buff=0,
                      stroke_width=5, max_tip_length_to_length_ratio=0.28).set_z_index(4)
        
        f_lbl = MathTex("f", color=COLOR_VEC_F, font_size=38).next_to(f_arr, DOWN, buff=0.15).set_z_index(4)

        self.play(GrowArrow(f_arr), run_time=0.6)
        self.play(FadeIn(f_lbl, shift=UP*0.1))

        verdict_cart = Text("If  F  >  f  →  cart moves forward.",
                            font="Segoe UI", font_size=28, weight=BOLD, color=COLOR_WHITE,
                            t2c={" F ": COLOR_VEC_F, " f ": COLOR_VEC_F, "cart moves forward": COLOR_GREEN})
        verdict_cart.move_to(np.array([-1.5, 2.0, 0])) 

        self.play(Write(verdict_cart), run_time=0.8)
        self.wait(0.5)

        moving_group = Group(
            hc,
            F_arr, F_lbl, F_tag,
            f_arr, f_lbl
        )
        
        shift_amount = 2.0
        self.play(
            moving_group.animate.shift(RIGHT * shift_amount),
            self.camera.frame.animate.shift(RIGHT * shift_amount),
            run_time=2.5,
            rate_func=rate_functions.ease_in_out_quad
        )
        self.wait(0.5)

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · PAN TO THE HORSE & THE GLOWING MYSTERY (No Masks)
        # ══════════════════════════════════════════════════════════
        cart_visuals = VGroup(F_arr, F_lbl, F_tag, f_arr, f_lbl)
        
        focus_title_h = Text("Forces on the HORSE",
                             font="Segoe UI", font_size=32, weight=BOLD, color=COLOR_WHITE,
                             t2c={"HORSE": COLOR_AMBER}).to_edge(UP, buff=0.55)

        # Pan camera right to the horse and zoom out slightly
        self.play(
            ReplacementTransform(focus_title, focus_title_h),
            ReplacementTransform(verdict_cart, focus_title_h), 
            FadeOut(cart_visuals, shift=LEFT*0.5),
            self.camera.frame.animate.scale(1/0.85).move_to(RIGHT * 1.0 + UP * 0.2),
            run_time=1.5,
            rate_func=rate_functions.ease_in_out_sine
        )

        arr_y_h = hc.get_top()[1] + 0.40
        horse_contact_h = np.array([0.55 + shift_amount, hc.get_top()[1] + 0.05, 0])
        
        Fp2_tail = np.array([ 2.40 + shift_amount, arr_y_h, 0])
        Fp2_head = np.array([ 0.35 + shift_amount, arr_y_h, 0])
        Fp2_arr = Arrow(Fp2_tail, Fp2_head, color=COLOR_VEC_F, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.22).set_z_index(4)
        Fp2_lbl = MathTex("F'", color=COLOR_VEC_F, font_size=44).next_to(Fp2_arr, UP, buff=0.10).set_z_index(4)
        Fp2_tag = Text("cart pulls horse back", font="Segoe UI", font_size=20, color=COLOR_GROUND, slant=ITALIC).next_to(Fp2_arr, DOWN, buff=0.12).set_z_index(4)

        self.play(GrowArrow(Fp2_arr), run_time=0.6)
        self.play(FadeIn(Fp2_lbl, shift=UP*0.1), FadeIn(Fp2_tag, shift=DOWN*0.1))
        
        question = Text("So what pushes the HORSE forward?",
                        font="Segoe UI", font_size=34, weight=BOLD, color=COLOR_WHITE,
                        t2c={"HORSE": COLOR_AMBER, "forward": COLOR_AMBER}).move_to(np.array([1.0, 2.55, 0]))

        self.play(Write(question), run_time=1.0)

        mystery_y = ground_y - 0.65
        mystery_x_contact = 1.50 + shift_amount
        mystery_tail = np.array([mystery_x_contact - 0.55, mystery_y, 0])
        mystery_head = np.array([mystery_x_contact + 0.55, mystery_y, 0])
        
        mystery_arr = Arrow(mystery_tail, mystery_head, color=COLOR_AMBER, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.28).set_z_index(4)
        mystery_leader = DashedLine(
            np.array([mystery_x_contact, ground_y - 0.05, 0]),
            np.array([mystery_x_contact, mystery_y + 0.20, 0]),
            color=COLOR_AMBER, stroke_width=2, stroke_opacity=0.8, dash_length=0.07
        )
        mystery_lbl = MathTex("?", color=COLOR_AMBER, font_size=60).next_to(mystery_arr, LEFT, buff=0.2).set_z_index(4)

        self.play(
            GrowArrow(mystery_arr), Create(mystery_leader), 
            FadeIn(mystery_lbl, scale=0.2), 
            run_time=0.8, rate_func=rate_functions.ease_out_back
        )

        for _ in range(2):
            self.play(
                mystery_lbl.animate.scale(1.4),
                mystery_arr.animate.set_stroke(width=9),
                run_time=0.4, rate_func=rate_functions.ease_out_sine
            )
            self.play(
                mystery_lbl.animate.scale(1/1.4),
                mystery_arr.animate.set_stroke(width=6),
                run_time=0.4, rate_func=rate_functions.ease_in_sine
            )

        self.wait()

        # ══════════════════════════════════════════════════════════
        #  ACT 6 · THE FADE TO BLACK (End of Scene 2)
        # ══════════════════════════════════════════════════════════
        # Fade out all text and context
        self.play(
            FadeOut(question, shift=UP * 0.2),
            FadeOut(focus_title_h, shift=UP * 0.2),
            run_time=0.8
        )
        
        # Fade out the horse, vectors, and ground
        self.play(
            FadeOut(Group(hc, ground, hatching, Fp2_arr, Fp2_lbl, Fp2_tag)),
            run_time=1.2,
            rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.5)

        # The mystery mark shrinks and vanishes into the darkness
        self.play(
            mystery_lbl.animate.scale(0.1).set_opacity(0),
            FadeOut(mystery_arr, shift=RIGHT * 0.2),
            FadeOut(mystery_leader),
            run_time=1.0,
            rate_func=rate_functions.ease_in_back
        )
        self.wait()