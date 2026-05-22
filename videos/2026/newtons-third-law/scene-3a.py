from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE  (Apple)
# ─────────────────────────────────────────────
COLOR_BG        = "#1C1C1E"
COLOR_DARK_GRAY = "#3A3A3C"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_GREY_BALL = "#D1D1D6"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F     = "#FF3B30"
COLOR_VEC_V     = "#32ADE6"
COLOR_GREEN     = "#34C759"
COLOR_YELLOW    = "#FFCC00"
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

def pill_bg(text_mob, fill=COLOR_BG, fill_opacity=0.85, stroke_color=None, stroke_width=0, buff=0.10):
    """Sleek rounded pill behind a text mobject."""
    h = text_mob.height + buff * 2
    w = text_mob.width + buff * 3
    bg = RoundedRectangle(
        corner_radius=min(h * 0.5, 0.25),
        height=h, width=w,
        color=stroke_color if stroke_color else fill,
        stroke_width=stroke_width,
        fill_color=fill, fill_opacity=fill_opacity,
    ).move_to(text_mob.get_center())
    return bg


# ═══════════════════════════════════════════════════════════════════
#  SCENE 3A · The Hidden Hero: Ground
# ═══════════════════════════════════════════════════════════════════

class Scene3A_GroundReaction(MovingCameraScene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # ── Carried over from Scene 3 ─────────────────────────────
        ground_y = -2.2
        shift_amount = 2.0

        self.camera.frame.move_to(RIGHT * 1.0 + UP * 0.2)

        # ── Ground line + hatching ────────────────────────────────
        ground = Line(
            LEFT * 6.5 + UP * ground_y, RIGHT * 6.5 + UP * ground_y,
            color=COLOR_GROUND, stroke_width=3, stroke_opacity=0.9
        ).set_z_index(1)

        hatching = VGroup()
        for x in np.arange(-6.2, 6.5, 0.32):
            h = Line(
                np.array([x, ground_y, 0]),
                np.array([x - 0.18, ground_y - 0.25, 0]),
                color=COLOR_GROUND, stroke_width=1.5, stroke_opacity=0.5
            )
            hatching.add(h)
        hatching.set_z_index(1)

        # ── Horse-cart image ──────────────────────────────────────
        try:
            hc = ImageMobject("horse_cart.png")
        except Exception:
            hc = Rectangle(width=5, height=2.6, color=COLOR_WHITE).set_fill(COLOR_DARK_GRAY, 0.5)
        hc.set_z_index(2)
        hc.scale_to_fit_height(2.6)
        hc.move_to(np.array([shift_amount, ground_y + hc.height / 2 + 0.05, 0]))

        # ── F' arrow on the horse ─────────────────────────────────
        arr_y_h = hc.get_top()[1] + 0.45
        Fp2_tail = np.array([2.55 + shift_amount, arr_y_h, 0])
        Fp2_head = np.array([0.45 + shift_amount, arr_y_h, 0])

        Fp2_arr = Arrow(
            Fp2_tail, Fp2_head, color=COLOR_VEC_F, buff=0,
            stroke_width=6, max_tip_length_to_length_ratio=0.20
        ).set_z_index(4)
        Fp2_lbl = MathTex("F'", color=COLOR_VEC_F, font_size=44).next_to(Fp2_arr, UP, buff=0.18).set_z_index(5)
        Fp2_pill = pill_bg(Fp2_lbl).set_z_index(4)

        self.add(ground, hatching, hc, Fp2_arr, Fp2_pill, Fp2_lbl)
        self.wait(0.5)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · ENTER THE GROUND
        # ══════════════════════════════════════════════════════════
        chapter = Text(
            "ENTER: THE GROUND", font="sans-serif", font_size=30, weight=BOLD, color=COLOR_YELLOW
        ).move_to(UP * 3.4 + RIGHT * 1.0).set_z_index(10)
        chapter_underline = Line(
            chapter.get_corner(DL) + LEFT * 0.05 + DOWN * 0.08,
            chapter.get_corner(DR) + RIGHT * 0.05 + DOWN * 0.08,
            color=COLOR_YELLOW, stroke_width=2.5,
        ).set_z_index(10)

        self.play(
            FadeIn(chapter, shift=DOWN * 0.25),
            run_time=1.0, rate_func=rate_functions.ease_out_expo
        )
        self.play(Create(chapter_underline), run_time=0.5)

        # Sweep across the ground
        ground_sweep = Line(
            LEFT * 6.5 + UP * ground_y, RIGHT * 6.5 + UP * ground_y,
            color=COLOR_YELLOW, stroke_width=5
        ).set_z_index(5)
        self.play(
            Create(ground_sweep),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine
        )
        self.play(FadeOut(ground_sweep), run_time=0.5)
        self.wait(0.3)

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · HORSE PUSHES GROUND BACKWARD
        # ══════════════════════════════════════════════════════════
        # Rear-leg hoof of a right-facing horse sits LEFT of the horse body's
        # geometric center, near the back of the visible silhouette.
        rear_hoof = np.array([0.70 + shift_amount, ground_y, 0])

        # Mirror-magnitude action/reaction pair (horizontal)
        push_vec = LEFT * 1.45
        reac_vec = RIGHT * 1.45

        p_horse_arr = Arrow(
            rear_hoof, rear_hoof + push_vec, color=COLOR_PURPLE, buff=0,
            stroke_width=7, max_tip_length_to_length_ratio=0.22
        ).set_z_index(5)

        p_horse_lbl = MathTex(
            r"P_{\text{push}}", color=COLOR_PURPLE, font_size=34
        ).next_to(p_horse_arr.get_end(), UP, buff=0.18).set_z_index(7)
        p_horse_pill = pill_bg(p_horse_lbl).set_z_index(6)
        p_horse_tag = Text(
            "Horse pushes ground", font="sans-serif", font_size=18, color=COLOR_WHITE
        ).next_to(p_horse_pill, UP, buff=0.12).set_z_index(7)
        p_horse_tag_pill = pill_bg(p_horse_tag, fill_opacity=0.7).set_z_index(6)

        self.play(
            GrowArrow(p_horse_arr),
            run_time=0.8, rate_func=rate_functions.ease_out_expo
        )
        self.play(
            FadeIn(p_horse_pill, shift=UP * 0.1),
            FadeIn(p_horse_lbl, shift=UP * 0.1),
            FadeIn(p_horse_tag_pill, shift=UP * 0.1),
            FadeIn(p_horse_tag, shift=UP * 0.1),
            run_time=0.5
        )
        self.wait(0.8)

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · NEWTON'S 3RD LAW — GROUND PUSHES BACK
        # ══════════════════════════════════════════════════════════
        # Ground reaction vector
        P_arr = Arrow(
            rear_hoof, rear_hoof + reac_vec, color=COLOR_YELLOW, buff=0,
            stroke_width=9, max_tip_length_to_length_ratio=0.22
        ).set_z_index(7)

        P_lbl = MathTex("P", color=COLOR_YELLOW, font_size=54).next_to(
            P_arr.get_end(), UP + RIGHT * 0.3, buff=0.15
        ).set_z_index(9)
        P_pill = pill_bg(P_lbl).set_z_index(8)

        # 3rd Law badge — placed clear of horse + arrows
        badge_text = Text(
            "3rd Law Pair", font="sans-serif", font_size=18, weight=BOLD, color=COLOR_YELLOW
        )
        badge_bg = RoundedRectangle(
            corner_radius=0.18,
            height=badge_text.height + 0.28,
            width=badge_text.width + 0.55,
            color=COLOR_YELLOW, stroke_width=1.5,
            fill_color=COLOR_BG, fill_opacity=0.92,
        )
        badge = VGroup(badge_bg, badge_text).move_to(
            rear_hoof + UP * 2.6 + RIGHT * 3.2
        ).set_z_index(10)
        # Subtle connector from badge to P arrow tip
        badge_connector = DashedLine(
            badge.get_corner(DL),
            P_arr.get_end() + UP * 0.15 + RIGHT * 0.05,
            color=COLOR_YELLOW, stroke_width=1.4, stroke_opacity=0.55,
            dash_length=0.10,
        ).set_z_index(9)

        self.play(
            GrowArrow(P_arr),
            run_time=0.9, rate_func=rate_functions.ease_out_expo
        )
        self.play(
            FadeIn(P_pill, shift=DOWN * 0.1),
            FadeIn(P_lbl, shift=DOWN * 0.1),
            FadeIn(badge, scale=0.7),
            Create(badge_connector),
            run_time=0.7, rate_func=rate_functions.ease_out_back
        )
        self.wait(1.2)

        # Dim P_push to focus on forces ON the horse
        self.play(
            FadeOut(badge), FadeOut(badge_connector),
            p_horse_arr.animate.set_stroke(opacity=0.20),
            p_horse_lbl.animate.set_opacity(0.25),
            p_horse_pill.animate.set_opacity(0),
            FadeOut(p_horse_tag),
            FadeOut(p_horse_tag_pill),
            run_time=0.8
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · TWO FORCES ON THE HORSE  (P  vs  F')
        # ══════════════════════════════════════════════════════════
        focus_title = Text(
            "Forces on the Horse", font="sans-serif", font_size=30, weight=BOLD, color=COLOR_WHITE
        ).move_to(UP * 3.4 + RIGHT * 1.0).set_z_index(10)

        self.play(
            ReplacementTransform(chapter, focus_title),
            FadeOut(chapter_underline),
            run_time=0.8
        )

        self.play(Wiggle(P_arr, rotation_angle=0.04, scale_value=1.10), run_time=0.8)
        self.play(Wiggle(Fp2_arr, rotation_angle=0.04, scale_value=1.10), run_time=0.8)

        # Verdict equation
        eq_bg = RoundedRectangle(
            corner_radius=0.3, width=5.8, height=1.05,
            color=COLOR_DARK_GRAY, stroke_width=1.5,
            fill_color=COLOR_BG, fill_opacity=0.92
        ).move_to(UP * 2.3 + RIGHT * 1.0).set_z_index(10)
        verdict = MathTex(
            "P", r"\;>\;", "F'", r"\;\Rightarrow\;", r"\text{Forward Acceleration}",
            font_size=36
        ).move_to(eq_bg.get_center()).set_z_index(11)
        verdict[0].set_color(COLOR_YELLOW)
        verdict[2].set_color(COLOR_VEC_F)
        verdict[4].set_color(COLOR_GREEN)

        self.play(FadeIn(eq_bg, shift=UP * 0.2), Write(verdict), run_time=1.0)
        self.wait(1.5)

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · THE CHAIN OF FORCES
        # ══════════════════════════════════════════════════════════
        self.play(
            FadeOut(eq_bg), FadeOut(verdict), FadeOut(focus_title),
            FadeOut(p_horse_arr), FadeOut(p_horse_lbl), FadeOut(p_horse_pill),
            self.camera.frame.animate.scale(1.15).move_to(RIGHT * 0.5 + UP * 0.2),
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine
        )

        background_group = Group(hc, ground, hatching)
        self.play(
            background_group.animate.set_opacity(0.25),
            Fp2_arr.animate.set_stroke(opacity=0.3),
            Fp2_pill.animate.set_opacity(0),
            Fp2_lbl.animate.set_opacity(0.3),
            P_arr.animate.set_stroke(opacity=0.3),
            P_pill.animate.set_opacity(0),
            P_lbl.animate.set_opacity(0.3),
            run_time=0.8
        )

        # Chain HUD
        chain_title = Text(
            "The Chain of Forces", font="sans-serif", font_size=30, weight=BOLD, color=COLOR_WHITE
        ).to_edge(UP, buff=0.5).set_z_index(10)

        chain_hud = VGroup(
            Text("Ground", font="sans-serif", font_size=24, color=COLOR_WHITE),
            MathTex(r"\rightarrow", color=COLOR_GROUND, font_size=36),
            Text("Horse", font="sans-serif", font_size=24, color=COLOR_WHITE),
            MathTex(r"\rightarrow", color=COLOR_GROUND, font_size=36),
            Text("Cart", font="sans-serif", font_size=24, color=COLOR_WHITE)
        ).arrange(RIGHT, buff=0.45).next_to(chain_title, DOWN, buff=0.4).set_z_index(10)

        self.play(FadeIn(chain_title, shift=DOWN * 0.1), FadeIn(chain_hud, shift=DOWN * 0.1), run_time=0.8)

        # Link 1: Ground → Horse (P)
        self.play(
            chain_hud[0].animate.set_color(COLOR_YELLOW),
            chain_hud[1].animate.set_color(COLOR_YELLOW),
            chain_hud[2].animate.set_color(COLOR_YELLOW),
            P_arr.animate.set_stroke(opacity=1.0),
            P_lbl.animate.set_opacity(1.0),
            run_time=0.6
        )
        self.wait(0.6)

        # Link 2 & 3: Rope interaction (F' on horse + F on cart)
        arr_y_c = hc.get_top()[1] + 0.45
        F_tail = np.array([-2.55 + shift_amount, arr_y_c, 0])
        F_head = np.array([-0.45 + shift_amount, arr_y_c, 0])

        F_arr = Arrow(
            F_tail, F_head, color=COLOR_VEC_F, buff=0,
            stroke_width=6, max_tip_length_to_length_ratio=0.20
        ).set_z_index(4)
        F_lbl = MathTex("F", color=COLOR_VEC_F, font_size=44).next_to(F_arr, UP, buff=0.18).set_z_index(5)
        F_pill = pill_bg(F_lbl).set_z_index(4)

        self.play(
            chain_hud[0].animate.set_color(COLOR_WHITE),
            chain_hud[1].animate.set_color(COLOR_GROUND),
            chain_hud[2].animate.set_color(COLOR_VEC_F),
            chain_hud[3].animate.set_color(COLOR_VEC_F),
            chain_hud[4].animate.set_color(COLOR_VEC_F),
            Fp2_arr.animate.set_stroke(opacity=1.0),
            Fp2_lbl.animate.set_opacity(1.0),
            Fp2_pill.animate.set_opacity(0.85),
            GrowArrow(F_arr),
            FadeIn(F_pill, shift=DOWN * 0.1),
            FadeIn(F_lbl, shift=DOWN * 0.1),
            run_time=0.8
        )
        self.wait(1.2)

        # ══════════════════════════════════════════════════════════
        #  ACT 6 · TAKEAWAY
        # ══════════════════════════════════════════════════════════
        self.play(FadeOut(chain_title), FadeOut(chain_hud), run_time=0.6)

        takeaway_bg = RoundedRectangle(
            corner_radius=0.3, width=7.4, height=1.7,
            color=COLOR_YELLOW, stroke_width=1.8,
            fill_color=COLOR_BG, fill_opacity=0.95
        ).move_to(UP * 2.9 + RIGHT * 0.5).set_z_index(10)

        t1 = Text(
            "Forces in a pair always act on",
            font="sans-serif", font_size=24, color=COLOR_WHITE
        )
        t2 = Text(
            "DIFFERENT BODIES",
            font="sans-serif", font_size=38, weight=BOLD, color=COLOR_YELLOW
        )
        takeaway = VGroup(t1, t2).arrange(DOWN, buff=0.18).move_to(takeaway_bg.get_center()).set_z_index(11)

        self.play(FadeIn(takeaway_bg, shift=UP * 0.1), run_time=0.5)
        self.play(FadeIn(t1, shift=UP * 0.1), run_time=0.5)
        self.play(FadeIn(t2, shift=UP * 0.1), run_time=0.6, rate_func=rate_functions.ease_out_back)

        self.wait(2.5)

        # Clean dissolve
        self.play(
            FadeOut(Group(
                hc, ground, hatching,
                P_arr, P_lbl, P_pill,
                Fp2_arr, Fp2_lbl, Fp2_pill,
                F_arr, F_lbl, F_pill,
                takeaway_bg, takeaway
            )),
            run_time=1.5, rate_func=rate_functions.ease_in_out_sine
        )
        self.wait(0.5)
