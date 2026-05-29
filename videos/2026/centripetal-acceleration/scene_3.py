from manim import *
import numpy as np
import math

# ─────────────────────────────────────────────
#  BRAND PALETTE  (consistent with the series)
# ─────────────────────────────────────────────
COLOR_BG        = "#0E1117"
COLOR_GROUND    = "#8E8E93"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F     = "#FF3B30"   # red — force
COLOR_VEC_V     = "#32ADE6"   # cyan — velocity / the ghost timeline
COLOR_GREEN     = "#34C759"
COLOR_AMBER     = "#FFCC00"   # the measured quantities (AB drops, BC)
COLOR_PINK      = "#FF2D55"
COLOR_PURPLE    = "#AF52DE"
COLOR_ORANGE    = "#FF9500"
COLOR_WHITE     = "#E5E5EA"
COLOR_CYAN      = "#32ADE6"


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
            op = peak_op * 0.35 * (1 - (2 * t - 1) ** 2)
            segs.add(Line(p1, p2, stroke_opacity=op,
                          stroke_width=1, color=COLOR_WHITE))
        return segs

    for x in np.arange(-max_x, max_x + 0.1, spacing):
        peak = 0.30 * (1 - (abs(x) / max_x) ** 1.5)
        if peak > 0:
            grid.add(fading_line(UP * max_y + RIGHT * x,
                                 DOWN * max_y + RIGHT * x, peak))
    for y in np.arange(-max_y, max_y + 0.1, spacing):
        peak = 0.30 * (1 - (abs(y) / max_y) ** 1.5)
        if peak > 0:
            grid.add(fading_line(LEFT * max_x + UP * y,
                                 RIGHT * max_x + UP * y, peak))
    return grid


def pill_bg(text_mob, buff=0.18, fill=COLOR_BG, fill_opacity=0.82,
            stroke=COLOR_GROUND, stroke_w=1.0, stroke_op=0.45):
    h = text_mob.height + buff * 1.6
    w = text_mob.width + buff * 2.4
    bg = RoundedRectangle(
        corner_radius=min(h * 0.5, 0.22),
        height=h, width=w,
        stroke_color=stroke, stroke_width=stroke_w, stroke_opacity=stroke_op,
        fill_color=fill, fill_opacity=fill_opacity,
    ).move_to(text_mob.get_center())
    return bg


def make_liquid_glass_card(width, height):
    """Creates a glassmorphism card with an iridescent rim and glossy sheen."""
    card = VGroup()

    # 1. The Base Plate: Semi-transparent to let the background peak through
    base = RoundedRectangle(
        corner_radius=0.3,
        width=width,
        height=height,
        fill_color=COLOR_GREY_BALL,
        fill_opacity=0.12, 
        stroke_width=0
    )

    # 2. The Specular Highlight: A soft wash of white that fades out, faking surface reflection
    highlight = RoundedRectangle(
        corner_radius=0.3,
        width=width,
        height=height,
        fill_color=COLOR_WHITE,
        fill_opacity=0.08,
        stroke_width=0
    )
    # Sheen directs the gradient fade. -0.5 pulls it to the top left.
    highlight.set_sheen(-0.5, UL) 

    # 3. The Iridescent Rim: Simulates chromatic refraction on the glass edge
    rim = RoundedRectangle(
        corner_radius=0.3,
        width=width,
        height=height,
        stroke_width=2.5,
        fill_opacity=0
    )
    # Using your Apple palette to create that colorful edge
    rim.set_color([COLOR_PURPLE, COLOR_CYAN, COLOR_GREEN, COLOR_PINK])
    rim.set_stroke(opacity=0.85)

    card.add(base, highlight, rim)
    return card

def make_center_point(scale=1.0):
    """The grip/anchor at the orbit center: a dot with an addressable
    strain-shimmer ring we can pulse without touching the dot.
    NOTE: this is the single anchor helper for the whole scene — Acts 4
    and 5 route through here too (no separate make_hand_anchor)."""
    g = VGroup()
    dot = Dot(point=ORIGIN, radius=0.05 * scale, color=COLOR_GREY_BALL)
    dot.set_fill(COLOR_GREY_BALL, opacity=1.0)
    shimmer = Circle(radius=0.18 * scale,
                     stroke_color=COLOR_VEC_F, stroke_width=3,
                     stroke_opacity=0.0, fill_opacity=0)
    g.add(shimmer, dot)
    g.shimmer = shimmer
    return g

def make_stone(radius=0.26):
    """Generates a static, non-random irregular stone to preserve caching."""
    g = VGroup()

    shape_profile = [1.1, 0.9, 1.15, 0.85, 1.05, 0.95, 1.2, 0.82, 1.08, 0.9, 1.1]
    pts = []
    N = len(shape_profile)
    for i in range(N):
        a = TAU * i / N
        r = radius * shape_profile[i]
        pts.append(np.array([r * np.cos(a), r * np.sin(a), 0]))

    body = Polygon(*pts, color="#3A3A3C")
    body.set_fill("#8E8E93", opacity=1.0)
    body.set_stroke(color="#3A3A3C", width=1.6, opacity=0.9)
    body.set_sheen(-0.35, DR)
    g.add(body)

    spec_data = [
        (0.3 * radius, 1.2, 0.08 * radius),
        (0.5 * radius, 3.5, 0.06 * radius),
        (0.25 * radius, 5.0, 0.09 * radius)
    ]
    for r, a, sr in spec_data:
        spec = Dot(point=np.array([r * np.cos(a), r * np.sin(a), 0]),
                   radius=sr, color="#3A3A3C")
        spec.set_fill("#3A3A3C", opacity=0.75)
        g.add(spec)

    return g

def orbit_point(center, radius, angle):
    return center + radius * np.array([np.cos(angle), np.sin(angle), 0])



# ═══════════════════════════════════════════════════════════════════
#  SCENE 3 · Huygens Freezes the Frame — discovering BC = ½at²
#  (one continuous geometric sequence, five acts)
# ═══════════════════════════════════════════════════════════════════
class Scene3_HuygensFreeze(MovingCameraScene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.camera.frame.save_state()

        # ── Geometry constants (shared by every act) ──────────────
        O = np.array([0.0, 0.0, 0.0])          # circle centre
        R = 2.5                                   # radius
        A = O + R * UP                             # frozen stone, 12 o'clock
        D_TANGENT = R * math.tan(37 * DEGREES)     # straight-line travel v·t
        B = A + LEFT * D_TANGENT                  # where the ghost flies to
        # C = where ray O→B pierces the circle  →  B, C, O are colinear,
        # so the BC "drop" and the inward string-tug share one line.
        C = O + R * (B - O) / np.linalg.norm(B - O)



        # ══════════════════════════════════════════════════════════
        #  ACT 1
        # ══════════════════════════════════════════════════════════

        stone = make_stone(radius=0.2).set_z_index(3)
        orbit = Circle(radius=2.5, color=COLOR_GREY_BALL, stroke_width=1.5,
                            stroke_opacity=0.18).move_to(ORIGIN)
        hand = make_center_point(scale=0.8).move_to(ORIGIN).set_z_index(2)
        th5 = ValueTracker(0.0)

        def s5_pos():
            return orbit_point(ORIGIN, 2.5, th5.get_value())
        stone.move_to(s5_pos())
        string = Line(ORIGIN, s5_pos(), color=COLOR_GREY_BALL,
                        stroke_width=2, stroke_opacity=0.7).set_z_index(1)

        self.play(
            FadeIn(orbit), FadeIn(hand, scale=0.6),
            Create(stone), Create(string)
        )
        stone.add_updater(lambda m: m.move_to(s5_pos()))
        string.add_updater(lambda m: m.put_start_and_end_on(ORIGIN, s5_pos()))
        calm_blur = TracedPath(stone.get_center, stroke_color=COLOR_GREY_BALL,
                               stroke_width=3, stroke_opacity=0.4,
                               dissipating_time=0.2).set_z_index(1)
        self.add(calm_blur)

        # spin exactly 2 full rotations, stopping with string vertical (top), ease out
        self.play(th5.animate.set_value(TAU * 2 + PI / 2), run_time=3.0, rate_func=linear)

        stone.clear_updaters()
        string.clear_updaters()
        self.remove(calm_blur)

        ripple = Circle(radius=0.18, color=COLOR_BLUE_BALL,
                        stroke_width=3.5).move_to(A).set_z_index(5)
        self.play(
            ripple.animate.scale(13).set_stroke(opacity=0.0))

        self.wait()

        A_label = MathTex("A", font_size=40, color=COLOR_WHITE)
        A_label.next_to(A, UP, buff=0.22).set_z_index(8)

        self.play(
            FadeIn(A_label, scale=1.9),
            run_time=0.55, rate_func=rate_functions.ease_out_back,
        )

        self.wait(0.8)

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · IF THE STRING SNAPPED — the ghost timeline
        # ══════════════════════════════════════════════════════════

        v_arrow = Arrow(A, A + LEFT * 1.25, color=COLOR_VEC_V, buff=0,
                        stroke_width=6,
                        max_tip_length_to_length_ratio=0.30).set_z_index(7)
        v_lbl = MathTex("v", color=COLOR_VEC_V, font_size=38)
        v_lbl.next_to(v_arrow, UP, buff=0.12).set_z_index(7)

        self.play(GrowArrow(v_arrow), FadeIn(v_lbl, shift=UP * 0.1),
                  run_time=0.7, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.7)

        # Snap the string: break-flash, then the radius recoils slack toward O.
        slack_target = Line(O, O + UP * 0.85, color=COLOR_GROUND,
                            stroke_width=2.2, stroke_opacity=0.5)
        self.play(Flash(A, color=COLOR_WHITE, line_length=0.22, num_lines=12,
                        flash_radius=0.34, line_stroke_width=2.5),
                  run_time=0.5)
        self.play(Transform(string, slack_target),
                  run_time=0.5, rate_func=rate_functions.ease_out_back)
        
        self.wait()

        # The velocity arrow BECOMES the path: it stretches into a dashed
        # tangent line as the ghost stone rides out to B. Constant speed → linear.
        ghost_stone = make_stone(radius=0.2).move_to(A).set_z_index(6)
        self.add(ghost_stone)
        self.remove(stone)  # the real stone is paused at A; ghost takes over

        ab_line = DashedLine(A, B, color=COLOR_VEC_V, stroke_width=4,
                             dash_length=0.14, dashed_ratio=0.6).set_z_index(5)
        v_lbl.clear_updaters()
        self.play(
            ReplacementTransform(v_arrow, ab_line),
            MoveAlongPath(ghost_stone, Line(A, B)),
            v_lbl.animate.next_to(Line(A, B).point_from_proportion(0.5),
                                  UP, buff=0.14),
            run_time=1.4, rate_func=linear,   # the physics demands constant v
        )
        self.wait(0.5)

        # Name the segment, then clarify it to AB = v·t.
        b_lbl = MathTex("B", color=COLOR_WHITE, font_size=40)
        b_lbl.next_to(B, UP, buff=0.22).set_z_index(8)
        self.play(
            FadeIn(b_lbl, scale=1.9),
            run_time=0.55, rate_func=rate_functions.ease_out_back,
        )
        self.wait(0.4)

        eq_ab = MathTex("AB", "=", "v", r"\cdot", "t",
                        font_size=40).set_z_index(9)
        eq_ab[0].set_color(COLOR_VEC_V)
        eq_ab[2].set_color(COLOR_VEC_V)
        eq_ab[4].set_color(COLOR_WHITE)
        eq_ab.next_to(Line(A, B).get_center(), LEFT, buff=2.0)
        eq_ab_bg = pill_bg(eq_ab).set_z_index(8)

        # Transform labels into their counterparts in eq_ab, write the rest
        self.play(
            FadeIn(eq_ab_bg),
            TransformFromCopy(A_label, eq_ab[0][0]),   # A_label → "A" in "AB"
            TransformFromCopy(b_lbl,   eq_ab[0][1]),   # b_lbl   → "B" in "AB"
            TransformFromCopy(v_lbl,   eq_ab[2]),       # v_lbl   → "v" in equation
            FadeIn(eq_ab[1]),                   # "="
            FadeIn(eq_ab[3]),                   # "·"
            FadeIn(eq_ab[4]),                   # "t"
            run_time=1.5, rate_func=rate_functions.ease_in_out_sine
        )
        self.wait()

        ab_fact = VGroup(eq_ab_bg, eq_ab)
        self.play(ab_fact.animate.scale(0.78).to_corner(UL, buff=0.55),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)
        
        # ══════════════════════════════════════════════════════════
        #  ACT 3 · REALITY PULLS IT BACK TO C
        # ══════════════════════════════════════════════════════════
        # Un-break the string: snaps taut again with a satisfying overshoot.
        taut = Line(O, A, color=COLOR_GREY_BALL, stroke_width=2.6)
        self.play(Transform(string, taut),
                  run_time=0.7, rate_func=rate_functions.ease_out_back)
        self.wait()

        # Real run: stone hugs the circle from A to C, string taut throughout.
        phi_c = math.atan2((B - O)[0], (B - O)[1])  # clockwise angle to C
        # Clean Arc used purely as the motion path (not drawn directly).
        real_arc = Arc(radius=R, start_angle=PI / 2, angle=-phi_c,
                       arc_center=O)
        
        real_stone = make_stone(radius=0.2).move_to(A).set_z_index(6)
        # The warm-white arc is drawn by tracing the stone — it draws itself.
        arc_trace = TracedPath(real_stone.get_center, stroke_color=COLOR_WHITE,
                               stroke_width=2.2, stroke_opacity=0.9)
        arc_trace.set_z_index(2)
        self.add(real_stone, arc_trace)
        string.add_updater(
            lambda m: m.put_start_and_end_on(O, real_stone.get_center()))

        self.play(
            MoveAlongPath(real_stone, real_arc),
            run_time=1.5, rate_func=linear,
        )
        string.clear_updaters()
        arc_trace.clear_updaters()
        string.put_start_and_end_on(O, C)

        self.wait(0.6)

        C_label = MathTex("C", font_size=40, color=COLOR_WHITE)
        C_label.next_to(C, RIGHT, buff=0.20).set_z_index(8)
        self.play(FadeIn(C_label, scale=1.6),
                  run_time=0.5, rate_func=rate_functions.ease_out_back)
        self.wait(0.6)

        replay_ghost = make_stone(radius=0.2).move_to(A).set_z_index(7)
        replay_real = make_stone(radius=0.2).move_to(A).set_z_index(7)
        self.add(replay_ghost, replay_real)
        # Fade the two resting stones so the replay reads as the only motion.
        self.play(ghost_stone.animate.set_opacity(0.18),
                  real_stone.animate.set_opacity(0.18), run_time=0.3)

        self.play(
            MoveAlongPath(replay_ghost, Line(A, B)),
            MoveAlongPath(replay_real, real_arc),
            run_time=1.4, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.2)
        # Land them exactly on the parked stones, then drop the replay dots.
        self.play(ghost_stone.animate.set_opacity(1.0),
                  real_stone.animate.set_opacity(1.0),
                  FadeOut(replay_ghost), FadeOut(replay_real),
                  run_time=0.4)
        self.wait()

        # ══════════════════════════════════════════════════════════
        #  ACT 4 · THE GAP IS THE DROP   (hero zoom)
        # ══════════════════════════════════════════════════════════

        gap_mid = (B + C) / 2.0

        beta = math.atan2((B - O)[1], (B - O)[0])
        frame_rot = beta - PI / 2

        self.play(
            self.camera.frame.animate.set(width=5.0).move_to(gap_mid),     # declutter for the close-up
            run_time=1.6, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.4)

        # Draw BC — the quantity — in amber.
        bc_line = Line(B, C, color=COLOR_AMBER, stroke_width=4).set_z_index(8)
        self.play(Create(bc_line),
                  rate_func=rate_functions.ease_out_cubic)

        # FRAMING 1 — the plain gap. (No pill: amber on dark reads clean, and
        # an unrotated pill would look tilted behind the upright text.)
        # Offset perpendicular to BC so the label sits just beside the gap.
        perp = np.array([-(C - B)[1], (C - B)[0], 0.0])
        perp = perp / np.linalg.norm(perp)
        
        # FRAMING 2 — rename it the drop.
        self.play(
            Indicate(bc_line, color=COLOR_AMBER, scale_factor=1.12),
            run_time=0.8,
        )
        self.wait(0.8)

        # FRAMING 3 — the cause: inward tug along the re-taut string toward O.
        # It is the SAME radial line as BC, continuing past C inward.
        tug_dir = (O - C) / np.linalg.norm(O - C)
        tug = Arrow(C, C + tug_dir * 0.85, color=COLOR_AMBER, buff=0,
                    stroke_width=5,
                    max_tip_length_to_length_ratio=0.34).set_z_index(9)

        self.play(GrowArrow(tug), run_time=0.6)

        # Heartbeat: pulse the tug inward a couple of times.
        for _ in range(2):
            self.play(tug.animate.scale(1.18,
                      about_point=C).set_color(COLOR_ORANGE),
                      run_time=0.28, rate_func=rate_functions.ease_out_quad)
            self.play(tug.animate.scale(1 / 1.18,
                      about_point=C).set_color(COLOR_AMBER),
                      run_time=0.28, rate_func=rate_functions.ease_in_quad)
        self.wait(1.0)

        # ══════════════════════════════════════════════════════════
        #  ACT 5 · BC = ½at²
        # ══════════════════════════════════════════════════════════

        self.play(
            Restore(self.camera.frame),
            FadeOut(tug),
            run_time=1.3, rate_func=rate_functions.ease_in_out_cubic,
        )

        self.wait(0.4)

        dark_card = Rectangle(width=20, height=10,
                                     fill_color=COLOR_BG, fill_opacity=0.5,
                                     stroke_width=0).set_z_index(9)

        glass_card = make_liquid_glass_card(width=4.5, height=2.8).set_z_index(10)
        self.play(FadeIn(dark_card), FadeIn(glass_card, scale=0.8, rate_func=rate_functions.ease_out_back))
        self.wait(0.6)
        equation = MathTex(
            "s", "=", "ut", "+", r"\frac{1}{2}", "a", "t^2",
            font_size=42,
            color=COLOR_WHITE
        ).move_to(ORIGIN).set_z_index(10)
        self.play(Write(equation), run_time=1.5)

        self.wait(0.8)

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
        self.wait(0.5)

        # ── Build the FINAL equation as one MathTex so spacing is clean ──
        # BC = ½at²  — "BC" is two glyphs, so building it as text (rather than
        # dropping a stand-alone "BC" where the single "s" sat) keeps the
        # equation properly kerned and aligned.
        final_eq = MathTex(
            "BC", "=", r"\frac{1}{2}", "a", "t^2",
            font_size=42, color=COLOR_WHITE,
        ).set_z_index(11)
        final_eq[0].set_color(COLOR_AMBER)
        # Anchor it so the "= ½at²" tail lines up with the existing "= ½at²".
        # equation[1] is the on-screen "="; align our "=" onto it.
        final_eq.shift(equation[1].get_center() - final_eq[1].get_center())

        # Fade out "s" the same way "ut" was faded (upward shift), then grow
        # "BC" from copies of the on-screen B and C point labels.
        self.play(
            FadeOut(equation[0], shift=UP * 0.6),
            TransformFromCopy(b_lbl,   final_eq[0][0]),   # B label → "B" in "BC"
            TransformFromCopy(C_label, final_eq[0][1]),   # C label → "C" in "BC"
            ReplacementTransform(equation[1], final_eq[1]),   # reuse "="
            ReplacementTransform(equation[4], final_eq[2]),   # reuse "½"
            ReplacementTransform(equation[5], final_eq[3]),   # reuse "a"
            ReplacementTransform(equation[6], final_eq[4]),   # reuse "t²"
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.4)

        # ── Give it the SAME pill treatment as AB = vt, then dock it in the
        #    top-left corner directly under AB = vt with matching formatting. ──
        final_bg = pill_bg(final_eq).set_z_index(10)
        bc_fact = VGroup(final_bg, final_eq)

        self.play(
            FadeOut(dark_card),
            FadeOut(glass_card),
            FadeIn(final_bg),
            run_time=0.6, rate_func=rate_functions.ease_in_out_sine,
        )

        # Match AB = vt: same 0.78 scale, left-aligned beneath the AB pill.
        bc_target = bc_fact.copy().scale(0.78)
        bc_target.next_to(ab_fact, DOWN, buff=0.22, aligned_edge=LEFT)

        self.play(
            bc_fact.animate.scale(0.78).move_to(bc_target),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait()