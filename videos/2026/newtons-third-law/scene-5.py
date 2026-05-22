# scene-4.py — Newton's Third Law · "Force Pair" doubt-buster
from manim import *
import numpy as np


# ─────────────────────────────────────────────
#  BRAND PALETTE  (consistent with the series)
# ─────────────────────────────────────────────
COLOR_BG        = "#1C1C1E"
COLOR_GROUND    = "#8E8E93"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F     = "#FF3B30"
COLOR_VEC_V     = "#32ADE6"
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
    """Sleek rounded pill behind a text mobject — series convention."""
    h = text_mob.height + buff * 2
    w = text_mob.width + buff * 3
    bg = RoundedRectangle(
        corner_radius=min(h * 0.5, 0.25),
        height=h, width=w,
        color=fill, stroke_width=0,
        fill_color=fill, fill_opacity=fill_opacity,
    ).move_to(text_mob.get_center())
    return bg


def make_clock(radius=0.55):
    """Analog clock face with a second hand we can rotate via updaters."""
    face = Circle(radius=radius, color=COLOR_WHITE,
                  stroke_width=2.0, stroke_opacity=0.85)
    face.set_fill(COLOR_BG, opacity=0.92)

    # Hour ticks at 12 / 3 / 6 / 9 only — keeps it clean
    ticks = VGroup()
    for ang in [PI / 2, 0, -PI / 2, PI]:
        outer = np.array([np.cos(ang) * radius * 0.92,
                          np.sin(ang) * radius * 0.92, 0])
        inner = np.array([np.cos(ang) * radius * 0.76,
                          np.sin(ang) * radius * 0.76, 0])
        ticks.add(Line(inner, outer, color=COLOR_WHITE,
                       stroke_width=1.6, stroke_opacity=0.7))

    # Centre dot
    pivot = Dot(ORIGIN, radius=0.035, color=COLOR_WHITE)

    # Second hand — long & thin, points UP at start (12 o'clock)
    hand = Line(ORIGIN, UP * radius * 0.82,
                color=COLOR_AMBER, stroke_width=2.6)

    g = VGroup(face, ticks, pivot, hand)
    g.hand = hand
    g.pivot = pivot
    return g


# ═══════════════════════════════════════════════════════════════════
#  SCENE 4 · "Action & Reaction are simultaneous — call it a Force Pair"
# ═══════════════════════════════════════════════════════════════════

class Scene5_ForcePair(MovingCameraScene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.camera.frame.save_state()

        # ── Series eyebrow ────────────────────────────────────────
        eyebrow_text = Text("COMMON DOUBT", font="Segoe UI",
                            font_size=18, weight=BOLD, color=COLOR_GROUND)
        eb_l = Line(LEFT * 0.55, ORIGIN, color=COLOR_GROUND,
                    stroke_width=1, stroke_opacity=0.7)
        eb_r = Line(ORIGIN, RIGHT * 0.55, color=COLOR_GROUND,
                    stroke_width=1, stroke_opacity=0.7)
        eb_l.next_to(eyebrow_text, LEFT, buff=0.25)
        eb_r.next_to(eyebrow_text, RIGHT, buff=0.25)
        eyebrow = VGroup(eb_l, eyebrow_text, eb_r).to_edge(UP, buff=0.55)

        self.play(
            LaggedStart(
                Create(eb_l),
                FadeIn(eyebrow_text, shift=DOWN * 0.1),
                Create(eb_r),
                lag_ratio=0.3,
            ),
            run_time=0.9,
        )
        self.wait(0.3)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · The misconception — "Action first, then Reaction"
        # ══════════════════════════════════════════════════════════
        # Minimal echo of the Scene-2 contact geometry: a contact line
        # with two arrows sitting on either side. No book/table needed
        # — viewer already has the memory, we just need the pair.
        contact_y = -1.4
        contact_line = Line(
            LEFT * 2.5 + UP * contact_y, RIGHT * 2.5 + UP * contact_y,
            color=COLOR_GROUND, stroke_width=2.0, stroke_opacity=0.55,
        )
        self.play(Create(contact_line), run_time=0.55)

        # Arrow geometry — symmetric about the contact line
        arr_x_left  = -0.85
        arr_x_right =  0.85
        arr_len     =  0.95

        # Action: above the line, pointing DOWN onto the surface
        action_arr = Arrow(
            np.array([arr_x_left, contact_y + arr_len, 0]),
            np.array([arr_x_left, contact_y + 0.05,   0]),
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.22,
        )
        action_lbl = Text("Action", font="Segoe UI",
                          font_size=22, weight=BOLD, color=COLOR_VEC_F)
        action_lbl.next_to(action_arr, UP, buff=0.14)

        # Reaction: below the line, pointing UP at the surface
        reaction_arr = Arrow(
            np.array([arr_x_right, contact_y - arr_len, 0]),
            np.array([arr_x_right, contact_y - 0.05,    0]),
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.22,
        )
        reaction_lbl = Text("Reaction", font="Segoe UI",
                            font_size=22, weight=BOLD, color=COLOR_VEC_F)
        reaction_lbl.next_to(reaction_arr, DOWN, buff=0.14)

        # The misconception headline
        wrong_q = Text(
            "Action first, then Reaction?",
            font="Segoe UI", font_size=26, slant=ITALIC, color=COLOR_WHITE,
            t2c={"Action": COLOR_VEC_F, "Reaction": COLOR_VEC_F},
        ).move_to(UP * 2.2)
        self.play(FadeIn(wrong_q, shift=DOWN * 0.15), run_time=0.7)
        self.wait(0.3)

        # --- Step 1: Action appears alone ---
        self.play(
            GrowArrow(action_arr),
            FadeIn(action_lbl, shift=DOWN * 0.08),
            run_time=0.55,
            rate_func=rate_functions.ease_out_cubic,
        )

        # --- Step 2: Clock appears and ticks three times ---
        # Clock placed to the right of the contact, in the negative space
        clock = make_clock(radius=0.55)
        clock.move_to(RIGHT * 4.2 + UP * 0.0)
        clock_caption = Text("time passes...", font="Segoe UI",
                             font_size=16, slant=ITALIC, color=COLOR_GROUND)
        clock_caption.next_to(clock, DOWN, buff=0.22)

        self.play(
            FadeIn(clock, scale=0.85),
            FadeIn(clock_caption, shift=UP * 0.08),
            run_time=0.5,
        )

        # Three discrete ticks — each a 90° jump with a tiny bounce-out
        # rate function. Each tick also flashes the clock face faintly
        # so the viewer feels the discreteness of waiting.
        for _ in range(3):
            self.play(
                Rotate(clock.hand, angle=-PI / 2,
                       about_point=clock.pivot.get_center()),
                Flash(clock.pivot, color=COLOR_AMBER,
                      line_length=0.10, num_lines=8,
                      flash_radius=0.18, run_time=0.35),
                run_time=0.35,
                rate_func=rate_functions.ease_out_back,
            )
            self.wait(0.12)

        # --- Step 3: Reaction finally shows up (the wrong picture) ---
        self.play(
            GrowArrow(reaction_arr),
            FadeIn(reaction_lbl, shift=UP * 0.08),
            run_time=0.55,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.7)

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · The correction — collapse the gap, Δt → 0
        # ══════════════════════════════════════════════════════════
        # Rewind: clear the wrong question, dismiss the clock by
        # shrinking it to nothing — the visual cue that "time gap = lie".
        wrong_strike = Line(
            wrong_q.get_corner(DL) + LEFT * 0.15 + DOWN * 0.05,
            wrong_q.get_corner(UR) + RIGHT * 0.15 + UP * 0.05,
            color=COLOR_PINK, stroke_width=4,
        )
        self.play(Create(wrong_strike), run_time=0.35,
                  rate_func=rate_functions.ease_in_out_expo)
        self.wait(0.2)
        self.play(
            FadeOut(wrong_q, shift=UP * 0.15),
            FadeOut(wrong_strike, shift=UP * 0.15),
            clock.animate.scale(0.05).set_opacity(0),
            FadeOut(clock_caption, shift=DOWN * 0.1),
            run_time=0.7,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.remove(clock)

        # Truth: Δt = 0. The two arrows pulse together — same instant.
        truth = MathTex(r"\Delta t = 0", font_size=44, color=COLOR_GREEN)
        truth.move_to(UP * 2.2)
        self.play(Write(truth), run_time=0.7)

        # Synchronous amber pulse — both arrows at the same time,
        # zero lag. This is the visual proof of simultaneity.
        self.play(
            Indicate(action_arr,   color=COLOR_AMBER, scale_factor=1.12),
            Indicate(reaction_arr, color=COLOR_AMBER, scale_factor=1.12),
            run_time=0.85,
        )
        self.wait(0.7)

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · The reframe — labels merge into "Force Pair"
        # ══════════════════════════════════════════════════════════
        # First, dissolve the Δt tag — it served its purpose.
        self.play(FadeOut(truth, shift=UP * 0.1), run_time=0.4)

        # Setup-line for the reframe
        better_name = Text(
            "Calling it a 'Force Pair' is more accurate.",
            font="Segoe UI", font_size=24, color=COLOR_WHITE,
            t2c={"'Force Pair'": COLOR_AMBER},
        ).move_to(UP * 2.2)
        self.play(FadeIn(better_name, shift=DOWN * 0.12), run_time=0.7)
        self.wait(0.3)

        # Detach labels from their arrows and drift them toward the
        # centre. The arrows stay put — same forces, new name.
        merge_point = ORIGIN + DOWN * 0.05
        action_lbl_target_pos   = merge_point + LEFT * 0.45
        reaction_lbl_target_pos = merge_point + RIGHT * 0.45

        self.play(
            action_lbl.animate.move_to(action_lbl_target_pos),
            reaction_lbl.animate.move_to(reaction_lbl_target_pos),
            run_time=0.9,
            rate_func=rate_functions.ease_in_out_sine,
        )

        # Now collapse both into a single label "Force Pair"
        force_pair_lbl = Text("Force Pair", font="Segoe UI",
                              font_size=30, weight=BOLD, color=COLOR_AMBER)
        force_pair_lbl.move_to(merge_point)

        self.play(
            ReplacementTransform(
                VGroup(action_lbl, reaction_lbl),
                force_pair_lbl,
            ),
            run_time=0.9,
            rate_func=rate_functions.ease_in_out_cubic,
        )

        # Halo box wraps the new name — locks in the reframe
        halo = SurroundingRectangle(
            force_pair_lbl, color=COLOR_AMBER, corner_radius=0.12,
            buff=0.18, stroke_width=2.0, stroke_opacity=0.0,
        )
        self.play(halo.animate.set_stroke(opacity=0.85), run_time=0.45)
        self.wait(0.8)

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · "Born together, live together, die together"
        # ══════════════════════════════════════════════════════════
        # Dismiss the setup line; keep the label + halo as the
        # heading for the rhythm beats.
        self.play(
            FadeOut(better_name, shift=UP * 0.12),
            VGroup(force_pair_lbl, halo).animate
                .scale(0.85).to_edge(UP, buff=1.0),
            run_time=0.7,
            rate_func=rate_functions.ease_in_out_sine,
        )

        # Caption slot below the contact line — three beats cycle here
        caption_pos = UP * 1.0

        # ─── Beat 1: BORN together ───────────────────────────────
        # The arrows are currently on screen. Fade them out cleanly,
        # then bring them back together for the "born" beat.
        self.play(
            FadeOut(action_arr, shift=UP * 0.1),
            FadeOut(reaction_arr, shift=DOWN * 0.1),
            run_time=0.45,
        )

        born_cap = Text("Born together", font="Segoe UI",
                        font_size=24, weight=BOLD, color=COLOR_GREEN)
        born_cap.move_to(caption_pos)

        # Re-create arrows fresh so they fade in cleanly together
        action_arr2 = Arrow(
            np.array([arr_x_left, contact_y + arr_len, 0]),
            np.array([arr_x_left, contact_y + 0.05,   0]),
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.22,
        )
        reaction_arr2 = Arrow(
            np.array([arr_x_right, contact_y - arr_len, 0]),
            np.array([arr_x_right, contact_y - 0.05,    0]),
            color=COLOR_VEC_F, buff=0, stroke_width=5,
            max_tip_length_to_length_ratio=0.22,
        )

        # lag_ratio=0 → genuine simultaneity, no stagger
        self.play(
            AnimationGroup(
                GrowArrow(action_arr2),
                GrowArrow(reaction_arr2),
                lag_ratio=0.0,
            ),
            FadeIn(born_cap, shift=UP * 0.12),
            run_time=0.7,
            rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.7)

        # ─── Beat 2: LIVE together (sync breath) ─────────────────
        live_cap = Text("Live together", font="Segoe UI",
                        font_size=24, weight=BOLD, color=COLOR_AMBER)
        live_cap.move_to(caption_pos)

        self.play(
            ReplacementTransform(born_cap, live_cap),
            run_time=0.4,
        )

        # Two synchronized breaths — scale up, scale down, both arrows
        # in perfect lockstep. lag_ratio=0 again.
        for _ in range(2):
            self.play(
                action_arr2.animate.scale(1.10),
                reaction_arr2.animate.scale(1.10),
                run_time=0.45,
                rate_func=rate_functions.ease_in_out_sine,
            )
            self.play(
                action_arr2.animate.scale(1 / 1.10),
                reaction_arr2.animate.scale(1 / 1.10),
                run_time=0.45,
                rate_func=rate_functions.ease_in_out_sine,
            )

        # ─── Beat 3: DIE together ────────────────────────────────
        die_cap = Text("Die together", font="Segoe UI",
                       font_size=24, weight=BOLD, color=COLOR_PINK)
        die_cap.move_to(caption_pos)

        self.play(
            ReplacementTransform(live_cap, die_cap),
            run_time=0.4,
        )

        self.play(
            AnimationGroup(
                FadeOut(action_arr2, shift=UP * 0.2),
                FadeOut(reaction_arr2, shift=DOWN * 0.2),
                lag_ratio=0.0,
            ),
            run_time=0.7,
            rate_func=rate_functions.ease_in_cubic,
        )
        self.wait(0.9)

        # ══════════════════════════════════════════════════════════
        #  Clean exit — leave the Force Pair name + halo lingering
        # ══════════════════════════════════════════════════════════
        self.play(
            FadeOut(die_cap, shift=DOWN * 0.1),
            FadeOut(contact_line),
            FadeOut(eyebrow, shift=UP * 0.1),
            run_time=0.6,
        )
        self.wait(0.6)

        # Final fade of the Force Pair badge itself
        self.play(
            FadeOut(VGroup(force_pair_lbl, halo), shift=UP * 0.15),
            run_time=0.7,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.4)