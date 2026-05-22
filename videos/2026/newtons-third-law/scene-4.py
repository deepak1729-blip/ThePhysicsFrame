from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE  (Apple — identical to scene-3a)
# ─────────────────────────────────────────────
COLOR_BG        = "#1C1C1E"
COLOR_DARK_GRAY = "#3A3A3C"
COLOR_GROUND    = "#8E8E93"
COLOR_WHITE     = "#E5E5EA"
COLOR_VEC_F     = "#FF3B30"   # red — internal rope forces F, F'
COLOR_GREEN     = "#34C759"   # ground push P (forward)
COLOR_YELLOW    = "#FFCC00"   # eyebrows + key callouts
COLOR_PINK      = "#FF2D55"   # friction f (resistive)


# ═══════════════════════════════════════════════════════════════════
#  HELPERS  (mirrored from scene-3a so visuals match exactly)
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


def pill_bg(text_mob, fill=COLOR_BG, fill_opacity=0.85, buff=0.10):
    """Sleek rounded pill behind a text/MathTex mobject."""
    h = text_mob.height + buff * 2
    w = text_mob.width + buff * 3
    return RoundedRectangle(
        corner_radius=min(h * 0.5, 0.25),
        height=h, width=w,
        color=fill, stroke_width=0,
        fill_color=fill, fill_opacity=fill_opacity,
    ).move_to(text_mob.get_center())


# ═══════════════════════════════════════════════════════════════════
#  SCENE 4 · THE SYSTEM VIEW
# ═══════════════════════════════════════════════════════════════════

class Scene4_SystemView(MovingCameraScene):
    def construct(self):
        self.camera.background_color = COLOR_BG

        # ── Match scene-3a's final camera state (scaled 1.15× at [0.5, 0.2])
        self.camera.frame.scale(1.15).move_to(RIGHT * 0.5 + UP * 0.2)

        # ── Grid (identical params to scene-3a) ───────────────────────
        grid = build_grid()
        grid.set_z_index(-10)

        # ── Ground line + hatching (identical to scene-3a) ────────────
        ground_y = -2.2
        shift_amount = 2.0

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

        # ── Horse-cart (identical sizing/position to scene-3a) ────────
        try:
            hc = ImageMobject("horse_cart.png")
        except Exception:
            hc = Rectangle(width=6.16, height=2.6, color=COLOR_WHITE)\
                .set_fill(COLOR_DARK_GRAY, 0.5)
        hc.set_z_index(2)
        hc.scale_to_fit_height(2.6)
        hc.move_to(np.array([shift_amount, ground_y + hc.height / 2 + 0.05, 0]))

        # Scene 4 opens with scene-3a's stage already set
        self.add(grid, ground, hatching, hc)
        self.wait(0.5)

        # ════════════════════════════════════════════════════════════
        #  ACT 1 · Eyebrow + title (top-left, clear of the diagram)
        # ════════════════════════════════════════════════════════════
        eyebrow = Text(
            "STEPPING BACK", font="sans-serif", weight=MEDIUM,
            color=COLOR_YELLOW, font_size=22
        ).set_opacity(0.9).set_z_index(10)
        title = Text(
            "One System, One Picture", font="sans-serif", weight=SEMIBOLD,
            color=COLOR_WHITE, font_size=34
        ).set_z_index(10)
        title_block = VGroup(eyebrow, title).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        title_block.move_to(np.array([-3.6, 3.5, 0]))

        self.play(FadeIn(eyebrow, shift=DOWN * 0.1), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(ch, shift=UP * 0.08) for ch in title],
                              lag_ratio=0.05, run_time=1.0))
        self.wait(0.5)

        # ════════════════════════════════════════════════════════════
        #  ACT 2 · Reveal all four forces
        #         (external: P on horse hoof, f on cart wheel;
        #          internal: F on cart, F' on horse — rope tension pair)
        # ════════════════════════════════════════════════════════════

        # Anchors carried over from scene-3a (kept verbatim so they line up
        # with the actual hoof / wheel positions on the silhouette).
        rear_hoof  = np.array([ 0.70 + shift_amount, ground_y, 0])   # [2.70, -2.20]
        cart_wheel = np.array([-2.20 + shift_amount, ground_y, 0])   # [-0.20, -2.20]

        arr_y_top = hc.get_top()[1] + 0.45                            # ≈ 0.90
        # F  on cart  (over cart, pointing RIGHT — pulls cart forward)
        F_tail  = np.array([-2.55 + shift_amount, arr_y_top, 0])      # [-0.55, 0.90]
        F_head  = np.array([-0.45 + shift_amount, arr_y_top, 0])      # [ 1.55, 0.90]
        # F' on horse (over horse, pointing LEFT — pulls horse backward)
        Fp_tail = np.array([ 2.55 + shift_amount, arr_y_top, 0])      # [ 4.55, 0.90]
        Fp_head = np.array([ 0.45 + shift_amount, arr_y_top, 0])      # [ 2.45, 0.90]

        # ── External vectors (the ones that survive) ───────────────
        P_arr = Arrow(
            rear_hoof, rear_hoof + RIGHT * 1.45, color=COLOR_GREEN, buff=0,
            stroke_width=7, max_tip_length_to_length_ratio=0.22
        ).set_z_index(6)
        f_arr = Arrow(
            cart_wheel, cart_wheel + LEFT * 0.75, color=COLOR_PINK, buff=0,
            stroke_width=7, max_tip_length_to_length_ratio=0.22
        ).set_z_index(6)

        # Labels — BELOW the arrows, sitting in the hatching zone with pills.
        P_lbl = MathTex("P", color=COLOR_GREEN, font_size=42)\
            .next_to(P_arr, DOWN, buff=0.32).set_z_index(8)
        P_pill = pill_bg(P_lbl).set_z_index(7)
        f_lbl = MathTex("f", color=COLOR_PINK, font_size=42)\
            .next_to(f_arr, DOWN, buff=0.32).set_z_index(8)
        f_pill = pill_bg(f_lbl).set_z_index(7)

        # ── Internal rope-tension pair ─────────────────────────────
        F_arr = Arrow(
            F_tail, F_head, color=COLOR_VEC_F, buff=0,
            stroke_width=6, max_tip_length_to_length_ratio=0.20
        ).set_z_index(5)
        Fp_arr = Arrow(
            Fp_tail, Fp_head, color=COLOR_VEC_F, buff=0,
            stroke_width=6, max_tip_length_to_length_ratio=0.20
        ).set_z_index(5)
        F_lbl = MathTex("F", color=COLOR_VEC_F, font_size=40)\
            .next_to(F_arr, UP, buff=0.18).set_z_index(7)
        F_pill = pill_bg(F_lbl).set_z_index(6)
        Fp_lbl = MathTex("F'", color=COLOR_VEC_F, font_size=40)\
            .next_to(Fp_arr, UP, buff=0.18).set_z_index(7)
        Fp_pill = pill_bg(Fp_lbl).set_z_index(6)

        # External first (P and f at the contact points)
        self.play(
            LaggedStart(GrowArrow(P_arr), GrowArrow(f_arr),
                        lag_ratio=0.2),
            run_time=0.9
        )
        self.play(
            FadeIn(P_pill), FadeIn(P_lbl),
            FadeIn(f_pill), FadeIn(f_lbl),
            run_time=0.5
        )
        self.wait(0.3)

        # Then the internal rope pair
        self.play(
            LaggedStart(GrowArrow(F_arr), GrowArrow(Fp_arr),
                        lag_ratio=0.2),
            run_time=0.9
        )
        self.play(
            FadeIn(F_pill), FadeIn(F_lbl),
            FadeIn(Fp_pill), FadeIn(Fp_lbl),
            run_time=0.5
        )
        self.wait(0.7)

        # ════════════════════════════════════════════════════════════
        #  ACT 3 · The SYSTEM box wraps horse + cart
        # ════════════════════════════════════════════════════════════
        box = RoundedRectangle(
            corner_radius=0.22,
            width=hc.width + 0.9, height=hc.height + 0.7,
            stroke_color=COLOR_YELLOW, stroke_width=2.5, stroke_opacity=0.0,
            fill_opacity=0,
        ).move_to(hc.get_center()).set_z_index(3)

        system_tag = Text(
            "SYSTEM", font="sans-serif", weight=MEDIUM,
            color=COLOR_YELLOW, font_size=20
        ).set_opacity(0).set_z_index(10)
        system_tag.next_to(box, UP, buff=0.15).align_to(box, LEFT).shift(RIGHT * 0.2)

        self.play(box.animate.set_stroke(opacity=0.95), run_time=0.9)
        self.play(system_tag.animate.set_opacity(0.9), run_time=0.4)
        self.wait(0.5)

        # ════════════════════════════════════════════════════════════
        #  ACT 4 · F and F' slide together → annihilate (soft puff)
        # ════════════════════════════════════════════════════════════
        # Dim externals + horse so the internal pair owns the moment.
        self.play(
            P_arr.animate.set_stroke(opacity=0.25),
            f_arr.animate.set_stroke(opacity=0.25),
            P_lbl.animate.set_opacity(0.3),
            f_lbl.animate.set_opacity(0.3),
            P_pill.animate.set_opacity(0.2),
            f_pill.animate.set_opacity(0.2),
            hc.animate.set_opacity(0.55),
            run_time=0.7
        )
        self.wait(0.3)

        # Converge toward the rope midpoint (between the two arrowheads).
        rope_mid = np.array([(F_head[0] + Fp_head[0]) / 2, arr_y_top, 0])

        F_target = Arrow(
            rope_mid - RIGHT * 0.05, rope_mid - RIGHT * 0.95,
            color=COLOR_VEC_F, buff=0, stroke_width=6,
            max_tip_length_to_length_ratio=0.20
        )
        Fp_target = Arrow(
            rope_mid + RIGHT * 0.05, rope_mid + RIGHT * 0.95,
            color=COLOR_VEC_F, buff=0, stroke_width=6,
            max_tip_length_to_length_ratio=0.20
        )
        F_lbl_t  = MathTex("F",  color=COLOR_VEC_F, font_size=40)\
            .next_to(F_target,  UP, buff=0.18)
        Fp_lbl_t = MathTex("F'", color=COLOR_VEC_F, font_size=40)\
            .next_to(Fp_target, UP, buff=0.18)

        self.play(
            Transform(F_arr,  F_target),
            Transform(Fp_arr, Fp_target),
            Transform(F_lbl,  F_lbl_t),
            Transform(Fp_lbl, Fp_lbl_t),
            F_pill.animate.move_to(F_lbl_t.get_center()),
            Fp_pill.animate.move_to(Fp_lbl_t.get_center()),
            run_time=1.1
        )
        self.wait(0.3)

        # The puff: a tiny burst of red dots fades outward as F and F' vanish.
        puff = VGroup(*[
            Dot(rope_mid, radius=0.06, color=COLOR_VEC_F, fill_opacity=0.7)
            for _ in range(8)
        ]).set_z_index(8)
        burst_dirs = [
            RIGHT * 0.55,                 LEFT  * 0.55,
            RIGHT * 0.35 + UP   * 0.30,   LEFT  * 0.35 + UP   * 0.30,
            RIGHT * 0.35 + DOWN * 0.30,   LEFT  * 0.35 + DOWN * 0.30,
            UP    * 0.50,                 DOWN  * 0.50,
        ]
        self.add(puff)

        self.play(
            *[d.animate.shift(v).set_opacity(0) for d, v in zip(puff, burst_dirs)],
            FadeOut(F_arr,  scale=0.6),
            FadeOut(Fp_arr, scale=0.6),
            FadeOut(F_lbl),  FadeOut(F_pill),
            FadeOut(Fp_lbl), FadeOut(Fp_pill),
            run_time=0.9, rate_func=rate_functions.ease_out_cubic
        )
        self.remove(puff)

        # Aside annotation — top-right, clear of title (top-left) and box.
        internal_note = VGroup(
            Text("Internal forces", font="sans-serif", weight=MEDIUM,
                 color=COLOR_VEC_F, font_size=22),
            Text("cancel inside the system", font="sans-serif",
                 color=COLOR_WHITE, font_size=18).set_opacity(0.8),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.10)
        internal_note.move_to(np.array([6.4, 3.0, 0])).set_z_index(11)
        note_pill = pill_bg(internal_note, fill_opacity=0.6, buff=0.18).set_z_index(10)

        self.play(
            FadeIn(note_pill),
            FadeIn(internal_note, shift=LEFT * 0.15),
            run_time=0.6
        )
        self.wait(1.0)

        # ════════════════════════════════════════════════════════════
        #  ACT 5 · External forces restored — they're all that matters
        # ════════════════════════════════════════════════════════════
        self.play(
            P_arr.animate.set_stroke(opacity=1.0),
            f_arr.animate.set_stroke(opacity=1.0),
            P_lbl.animate.set_opacity(1.0),
            f_lbl.animate.set_opacity(1.0),
            P_pill.animate.set_opacity(0.85),
            f_pill.animate.set_opacity(0.85),
            hc.animate.set_opacity(1.0),
            run_time=0.7
        )

        external_note = VGroup(
            Text("External forces", font="sans-serif", weight=MEDIUM,
                 color=COLOR_YELLOW, font_size=22),
            Text("ground push  +  friction", font="sans-serif",
                 color=COLOR_WHITE, font_size=18).set_opacity(0.8),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.10)
        external_note.move_to(internal_note).set_z_index(11)
        ext_pill = pill_bg(external_note, fill_opacity=0.6, buff=0.18).set_z_index(10)

        self.play(
            ReplacementTransform(internal_note, external_note),
            ReplacementTransform(note_pill, ext_pill),
            run_time=0.6
        )
        self.wait(0.5)

        # Halo pulses — anchor attention on the survivors.
        for arrow, color in [(P_arr, COLOR_GREEN), (f_arr, COLOR_PINK)]:
            halo = arrow.copy().set_stroke(color=color, width=14, opacity=0.35).set_z_index(5)
            self.play(FadeIn(halo, run_time=0.25), FadeOut(halo, run_time=0.4))
        self.wait(0.4)

        # ════════════════════════════════════════════════════════════
        #  ACT 6 · P > f → the whole system drifts right
        # ════════════════════════════════════════════════════════════
        # Lengthen P so the imbalance is unmistakable.
        P_long = Arrow(
            rear_hoof, rear_hoof + RIGHT * 2.5, color=COLOR_GREEN, buff=0,
            stroke_width=7, max_tip_length_to_length_ratio=0.22
        )
        P_lbl_t = MathTex("P", color=COLOR_GREEN, font_size=42)\
            .next_to(P_long, DOWN, buff=0.32)
        P_pill_t = pill_bg(P_lbl_t)

        self.play(
            Transform(P_arr, P_long),
            Transform(P_lbl, P_lbl_t),
            Transform(P_pill, P_pill_t),
            run_time=0.8
        )
        self.wait(0.4)

        # Inequality callout — well below the ground, in its own clear zone.
        inequality = MathTex("P", ">", "f", font_size=54)
        inequality[0].set_color(COLOR_GREEN)
        inequality[2].set_color(COLOR_PINK)
        inequality.move_to(np.array([0.5, -3.6, 0])).set_z_index(11)
        ineq_pill = pill_bg(inequality, fill_opacity=0.9, buff=0.20).set_z_index(10)

        self.play(FadeIn(ineq_pill), Write(inequality), run_time=0.8)
        self.wait(0.6)

        # System drifts right as ONE unit (the point of the box).
        system_unit = Group(
            hc, box, system_tag,
            P_arr, P_pill, P_lbl,
            f_arr, f_pill, f_lbl,
        )
        self.play(
            system_unit.animate.shift(RIGHT * 1.3),
            run_time=1.8, rate_func=rate_functions.ease_in_out_cubic
        )
        self.wait(0.7)

        # ════════════════════════════════════════════════════════════
        #  ACT 7 · Takeaway — the closing line of the video
        # ════════════════════════════════════════════════════════════
        diagram = Group(
            grid, ground, hatching, hc, box, system_tag,
            P_arr, P_lbl, P_pill,
            f_arr, f_lbl, f_pill,
            inequality, ineq_pill,
            ext_pill, external_note,
            eyebrow, title,
        )
        self.play(diagram.animate.set_opacity(0.18), run_time=0.9)
        self.wait(2.2)
