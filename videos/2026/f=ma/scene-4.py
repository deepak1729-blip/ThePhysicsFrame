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
COLOR_PURPLE    = "#AF52DE"   # Apple Purple
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


class Scene4_K(Scene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        merge_scale = 0.78

        # ── starting state: F ∝ m·a inside a box ──────────────────────
        combined_eq = MathTex(
            "F", r"\propto", "m", r"\cdot", "a",
            font_size=110, color=COLOR_WHITE
        )
        combined_eq[0].set_color(COLOR_VEC_F)
        combined_eq[2].set_color(COLOR_AMBER)
        combined_eq[3].set_color(COLOR_GROUND)
        combined_eq[4].set_color(COLOR_AMBER)
        combined_eq.scale(merge_scale).move_to(DOWN * 0.4)

        combined_box = RoundedRectangle(
            corner_radius=0.18 * merge_scale,
            width=combined_eq.width + 1.2 * merge_scale,
            height=combined_eq.height + 0.7 * merge_scale,
            stroke_color=COLOR_AMBER, stroke_width=2.5,
            stroke_opacity=0.85, fill_opacity=0
        ).move_to(combined_eq.get_center())

        self.add(combined_eq, combined_box)
        self.wait(0.8)

        # ── target state: F = k·m·a, no box ────────────────────────
        target_eq = MathTex(
            "F", "=", "k", r"\cdot", "m", r"\cdot", "a",
            font_size=110, color=COLOR_WHITE
        )
        target_eq[0].set_color(COLOR_VEC_F)
        target_eq[2].set_color(COLOR_PURPLE)
        target_eq[3].set_color(COLOR_GROUND)
        target_eq[4].set_color(COLOR_AMBER)
        target_eq[5].set_color(COLOR_GROUND)
        target_eq[6].set_color(COLOR_AMBER)
        target_eq.scale(merge_scale).move_to(DOWN * 0.4)

        self.play(
            FadeOut(combined_box),
            TransformMatchingTex(combined_eq, target_eq),
            run_time=1.5
        )
        self.wait(1.0)

        k_box = SurroundingRectangle(
            target_eq[2],
            color=COLOR_PURPLE,
            buff=0.12,
            stroke_width=2.2,
            corner_radius=0.08,
        )
        self.play(
            Create(k_box),
            Indicate(target_eq[2], scale_factor=1.35, color=COLOR_PURPLE),
            run_time=1.2,
        )
        self.wait(0.5)

        # k = 1 reveal below
        k_value = MathTex("k", "=", "1", font_size=82, color=COLOR_WHITE)
        k_value[0].set_color(COLOR_PURPLE)
        k_value[2].set_color(COLOR_GREEN)
        k_value.next_to(target_eq, DOWN, buff=1.0)

        self.play(FadeIn(k_value, shift=UP * 0.2), run_time=0.9)
        self.play(
            Indicate(k_value[2], scale_factor=1.45, color=COLOR_GREEN),
            Flash(
                k_value[2].get_center(),
                color=COLOR_GREEN,
                line_length=0.25,
                num_lines=14,
                flash_radius=0.55,
                line_stroke_width=2.5,
            ),
            run_time=0.95,
        )
        self.wait(1.0)

        eq_at_top = target_eq.copy().scale(0.6).to_edge(UP, buff=0.85)
        self.play(
            FadeOut(k_value),
            FadeOut(k_box),
            Transform(target_eq, eq_at_top),
            run_time=1.1,
        )
        self.wait(0.3)

        newton_tag = Text(
            "Isaac Newton, 1687",
            font_size=28,
            color=COLOR_AMBER,
            slant=ITALIC,
        ).move_to(UP * 1.6)

        line1 = Text(
            "Force had no fixed number yet.",
            font_size=36,
            color=COLOR_GROUND,
        ).move_to(UP * 0.2)

        line2 = Text(
            "Newton got to choose the unit.",
            font_size=42,
            color=COLOR_GREEN,
            weight=BOLD,
        ).next_to(line1, DOWN, buff=0.7)

        self.play(FadeIn(newton_tag, shift=DOWN * 0.2), run_time=0.6)
        self.wait(0.4)
        self.play(Write(line1), run_time=1.4)
        self.wait(0.8)
        self.play(Write(line2), run_time=1.6)
        self.wait(2.2)

        # ═══════════════════════════════════════════════════════════
        # BEAT 4 — The definition of 1 Newton (visualized)
        # Script: "1 Newton ko aisa define kiya — woh force jo
        #          1 kg ke object ko exactly 1 m/s² ka acceleration de."
        # ═══════════════════════════════════════════════════════════
        self.play(
            FadeOut(newton_tag),
            FadeOut(line1),
            FadeOut(line2),
            run_time=0.7,
        )

        # ground
        ground_line = Line(
            LEFT * 5.5 + DOWN * 1.7,
            RIGHT * 5.5 + DOWN * 1.7,
            color=COLOR_GROUND,
            stroke_width=2,
            stroke_opacity=0.7,
        )
        self.play(Create(ground_line), run_time=0.5)

        # 1 kg block
        block = Square(
            side_length=0.95,
            fill_color=COLOR_BLUE_BALL,
            fill_opacity=0.9,
            stroke_color=COLOR_WHITE,
            stroke_width=2,
        ).move_to(DOWN * 1.22 + LEFT * 2.3)
        mass_label = MathTex(r"1\,\text{kg}", font_size=30, color=COLOR_WHITE)\
            .move_to(block.get_center())
        block_group = VGroup(block, mass_label)

        # force arrow
        force_arrow = Arrow(
            start=LEFT * 4.0 + DOWN * 1.22,
            end=LEFT * 2.78 + DOWN * 1.22,
            color=COLOR_VEC_F,
            stroke_width=8,
            buff=0,
            max_tip_length_to_length_ratio=0.28,
        )
        force_label = MathTex("F", font_size=48, color=COLOR_VEC_F)\
            .next_to(force_arrow, UP, buff=0.15)

        # acceleration label
        a_label = MathTex(r"a = 1\,\text{m/s}^2", font_size=38, color=COLOR_AMBER)\
            .next_to(block, UP, buff=0.55)

        self.play(FadeIn(block_group, scale=0.85), run_time=0.7)
        self.play(GrowArrow(force_arrow), FadeIn(force_label), run_time=0.7)
        self.play(FadeIn(a_label, shift=DOWN * 0.15), run_time=0.6)
        self.wait(0.4)

        # animate block accelerating to the right
        motion_group = VGroup(block_group, force_arrow, force_label, a_label)
        self.play(
            motion_group.animate.shift(RIGHT * 4.4),
            rate_func=rate_functions.ease_in_quad,
            run_time=1.9,
        )
        self.wait(0.5)

        # Definition appears just above the visualization
        definition = MathTex(
            r"1\,\text{N}",
            r"\;\equiv\;",
            r"\text{force that gives}",
            r"\;1\,\text{kg}\;",
            r"\text{an acceleration of}",
            r"\;1\,\text{m/s}^2",
            font_size=34,
        )
        definition[0].set_color(COLOR_VEC_F)
        definition[1].set_color(COLOR_GROUND)
        definition[2].set_color(COLOR_WHITE)
        definition[3].set_color(COLOR_BLUE_BALL)
        definition[4].set_color(COLOR_WHITE)
        definition[5].set_color(COLOR_AMBER)
        definition.move_to(UP * 0.5)

        self.play(FadeIn(definition, shift=DOWN * 0.2), run_time=1.1)
        self.wait(2.2)

        # ═══════════════════════════════════════════════════════════
        # BEAT 5 — Substitute into F = k·m·a → derive k = 1
        # Script: "Is definition ko agar formula mein rakho — F = k·ma —
        #          to 1 = k·1·1, yani k = 1."
        # ═══════════════════════════════════════════════════════════
        self.play(
            FadeOut(motion_group),
            FadeOut(ground_line),
            run_time=0.7,
        )

        # bring F = k·m·a from top back to center for manipulation
        center_eq = MathTex(
            "F", "=", "k", r"\cdot", "m", r"\cdot", "a",
            font_size=92, color=COLOR_WHITE
        )
        center_eq[0].set_color(COLOR_VEC_F)
        center_eq[2].set_color(COLOR_PURPLE)
        center_eq[3].set_color(COLOR_GROUND)
        center_eq[4].set_color(COLOR_AMBER)
        center_eq[5].set_color(COLOR_GROUND)
        center_eq[6].set_color(COLOR_AMBER)
        center_eq.move_to(UP * 0.6)

        self.play(
            FadeOut(definition),
            Transform(target_eq, center_eq),
            run_time=1.0,
        )
        self.wait(0.6)

        # Substitution: F=1, m=1, a=1  →  1 = k·1·1
        sub_eq = MathTex(
            "1", "=", "k", r"\cdot", "1", r"\cdot", "1",
            font_size=92, color=COLOR_WHITE
        )
        sub_eq[0].set_color(COLOR_VEC_F)
        sub_eq[2].set_color(COLOR_PURPLE)
        sub_eq[3].set_color(COLOR_GROUND)
        sub_eq[4].set_color(COLOR_AMBER)
        sub_eq[5].set_color(COLOR_GROUND)
        sub_eq[6].set_color(COLOR_AMBER)
        sub_eq.move_to(UP * 0.6)

        self.play(ReplacementTransform(target_eq, sub_eq), run_time=1.5)
        self.wait(1.3)

        # Conclude k = 1
        result = MathTex(r"\Rightarrow", "k", "=", "1",
                         font_size=72, color=COLOR_WHITE)
        result[0].set_color(COLOR_GROUND)
        result[1].set_color(COLOR_PURPLE)
        result[2].set_color(COLOR_GROUND)
        result[3].set_color(COLOR_GREEN)
        result.next_to(sub_eq, DOWN, buff=0.9)

        self.play(FadeIn(result, shift=UP * 0.2), run_time=0.9)
        self.play(
            Flash(
                result[3].get_center(),
                color=COLOR_GREEN,
                line_length=0.22,
                num_lines=12,
                flash_radius=0.45,
                line_stroke_width=2.3,
            ),
            run_time=0.8,
        )
        self.wait(2.2)

        # ═══════════════════════════════════════════════════════════
        # BEAT 6 — The final reveal: F = ma
        # Script: "Kyunki unit hi is tarah banai gayi thi ki constant
        #          apne aap 1 ban jaye, isliye hum seedha likh sakte
        #          hain: F = ma."
        # ═══════════════════════════════════════════════════════════
        # First, transform sub_eq back into F = k·m·a (so the
        # viewer can see the k disappear from the canonical form)
        canonical_eq = MathTex(
            "F", "=", "k", r"\cdot", "m", r"\cdot", "a",
            font_size=110, color=COLOR_WHITE
        )
        canonical_eq[0].set_color(COLOR_VEC_F)
        canonical_eq[2].set_color(COLOR_PURPLE)
        canonical_eq[3].set_color(COLOR_GROUND)
        canonical_eq[4].set_color(COLOR_AMBER)
        canonical_eq[5].set_color(COLOR_GROUND)
        canonical_eq[6].set_color(COLOR_AMBER)
        canonical_eq.move_to(ORIGIN)

        self.play(
            FadeOut(result),
            ReplacementTransform(sub_eq, canonical_eq),
            run_time=1.2,
        )
        self.wait(0.6)

        # Now k gracefully disappears — leaving F = m·a
        final_eq = MathTex(
            "F", "=", "m", r"\cdot", "a",
            font_size=110, color=COLOR_WHITE
        )
        final_eq[0].set_color(COLOR_VEC_F)
        final_eq[2].set_color(COLOR_AMBER)
        final_eq[3].set_color(COLOR_GROUND)
        final_eq[4].set_color(COLOR_AMBER)
        final_eq.move_to(ORIGIN)

        # animate: k pulses, then fades out & shrinks; remaining
        # pieces slide together into the final compact form
        self.play(
            Indicate(canonical_eq[2], scale_factor=1.3, color=COLOR_PURPLE),
            run_time=0.7,
        )
        self.play(
            FadeOut(canonical_eq[2], scale=0.0, shift=UP * 0.3),
            FadeOut(canonical_eq[3], scale=0.0),  # the · after k
            run_time=0.9,
        )

        # The remaining pieces (F, =, m, ·, a) reassemble into final_eq
        remaining = VGroup(
            canonical_eq[0], canonical_eq[1],
            canonical_eq[4], canonical_eq[5], canonical_eq[6]
        )
        self.play(
            ReplacementTransform(remaining, final_eq),
            run_time=1.1,
        )
        self.wait(0.5)

        # Final flourish — soft glow box + flash, matching the channel's signature
        glow_box = RoundedRectangle(
            corner_radius=0.22,
            width=final_eq.width + 1.1,
            height=final_eq.height + 0.75,
            stroke_color=COLOR_AMBER,
            stroke_width=2.5,
            stroke_opacity=0.65,
            fill_opacity=0,
        ).move_to(final_eq.get_center())

        self.play(
            Create(glow_box),
            Flash(
                final_eq.get_center(),
                color=COLOR_AMBER,
                line_length=0.5,
                num_lines=22,
                flash_radius=2.8,
                line_stroke_width=3,
            ),
            run_time=1.5,
        )
        self.wait(2.8)