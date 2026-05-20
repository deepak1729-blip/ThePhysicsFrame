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

# ─────────────────────────────────────────────
#  IMAGE-SPECIFIC TUNABLES — adjust for the artwork
# ─────────────────────────────────────────────
HORSE_CART_WIDTH  = 6.0   # rendered width in scene units
ROPE_CENTER_X     = -0.4  # absolute x of rope center (independent of image)
ROPE_CENTER_Y     = -1.0  # absolute y of rope center (independent of image)
ROPE_HALF_WIDTH   = 0.65  # how far each arrow tail sits from rope center


# ═══════════════════════════════════════════════════════════════════
#  HELPERS  (consistent with the rest of the series)
# ═══════════════════════════════════════════════════════════════════
def make_ball(color: str, radius: float = 0.30) -> VGroup:
    g = VGroup()

    # Glow aura — four concentric halos, outermost first (drawn first = behind)

    # Main sphere body
    sphere = Circle(radius=radius)
    sphere.set_fill(color, opacity=1.0)
    sphere.set_sheen(-0.45, DR)          # darkens bottom-right, brightens top-left
    sphere.set_stroke(color=WHITE, width=1.5, opacity=0.22)
    g.add(sphere)

    # Rim light (coloured stroke, gives the "lit edge" feel)
    rim = Circle(radius=radius)
    rim.set_fill(opacity=0)
    rim.set_stroke(color=color, width=3, opacity=0.50)
    g.add(rim)

    # Specular highlight — small white ellipse offset to upper-left
    spec = Ellipse(width=radius * 0.52, height=radius * 0.34)
    spec.set_fill(WHITE, opacity=0.62)
    spec.set_stroke(width=0)
    spec.move_to(
        np.array([-radius * 0.28,  radius * 0.30, 0])   # offset from origin
    )
    spec.rotate(-20 * DEGREES)
    g.add(spec)

    return g

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


def place_on_ground(mob, x_position, ground_y):
    """Position a mobject so its bottom sits on the ground at given x."""
    mob.shift(np.array([
        x_position - mob.get_x(),
        ground_y - mob.get_bottom()[1],
        0
    ]))
    return mob

# ═══════════════════════════════════════════════════════════════════
#  SCENE 1 · The Hook — Newton's Third Law & the Horse-Cart Paradox
# ═══════════════════════════════════════════════════════════════════

class Scene1_HookThirdLaw(MovingCameraScene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)
        self.camera.frame.save_state()

        # Radial act divider — same as other scenes in the series
        def act_pulse(color=COLOR_WHITE, duration=0.7):
            ring = Circle(radius=0.1, color=color, stroke_width=2,
                          stroke_opacity=0.7, fill_opacity=0)
            ring.move_to(self.camera.frame.get_center())
            ring.set_z_index(20)
            self.add(ring)
            self.play(
                ring.animate.scale(60).set_stroke(width=0.3, opacity=0),
                run_time=duration,
                rate_func=rate_functions.ease_out_expo
            )
            self.remove(ring)

        # ══════════════════════════════════════════════════════════
        #  ACT 1 · Hook
        # ══════════════════════════════════════════════════════════
        eyebrow = Text("NEWTON'S THIRD LAW",
                       font="Segoe UI", font_size=18,
                       weight=BOLD, color=COLOR_GROUND)
        eyebrow_l = Line(LEFT * 0.5, ORIGIN, color=COLOR_GROUND,
                         stroke_width=1, stroke_opacity=0.6)
        eyebrow_r = Line(ORIGIN, RIGHT * 0.5, color=COLOR_GROUND,
                         stroke_width=1, stroke_opacity=0.6)
        eyebrow_l.next_to(eyebrow, LEFT, buff=0.25)
        eyebrow_r.next_to(eyebrow, RIGHT, buff=0.25)
        eyebrow_group = VGroup(eyebrow_l, eyebrow, eyebrow_r).move_to(UP * 3.0)

        self.play(
            FadeIn(eyebrow, shift=UP * 0.15),
            Create(eyebrow_l), Create(eyebrow_r),
            run_time=0.7
        )

        # ── Ground (persists into Act 2) ──
        ground_y = -2.5
        ground = Line(
            LEFT * 7.5 + UP * ground_y, RIGHT * 7.5 + UP * ground_y,
            color=COLOR_GROUND, stroke_width=2, stroke_opacity=0.55
        )
        self.play(Create(ground), run_time=0.55)

        # ── The ball: simple, everyday, instantly recognizable ──
        ball_radius = 0.30
        ball = make_ball(COLOR_GREY_BALL, radius=0.30)
        # Resting pose: bottom on the ground
        ball.move_to(np.array([0, ground_y + ball_radius, 0]))
        ball.save_state()
        # Lift to drop start
        ball.move_to(np.array([0, 1.6, 0]))

        self.play(FadeIn(ball, shift=DOWN * 0.15), run_time=0.45)
        self.wait(0.15)

        # Gravity drop — accelerating ease_in
        self.play(
            ball.animate.move_to(np.array([0, ground_y + ball_radius, 0])),
            run_time=0.7,
            rate_func=rate_functions.ease_in_quad
        )

        # Squash on impact — bottom edge stays planted on the ground
        self.play(
            ball.animate
                .stretch(1.32, 0, about_edge=DOWN)
                .stretch(0.58, 1, about_edge=DOWN),
            run_time=0.14,
            rate_func=rate_functions.ease_out_cubic
        )

        # ── Action / Reaction arrows reveal at the contact ──
        arrow_x        = 1.10                  # outside the squashed ball
        arrow_top_y    = ground_y + 0.95
        arrow_bottom_y = ground_y + 0.08       # just above the ground line

        # Action — ball pushes ground DOWN (left side, points down)
        action_arrow = Arrow(
            np.array([-arrow_x, arrow_top_y,    0]),
            np.array([-arrow_x, arrow_bottom_y, 0]),
            color=COLOR_VEC_F, stroke_width=4.5, buff=0,
            max_tip_length_to_length_ratio=0.22
        )
        action_label = Text("Action", font="Segoe UI", font_size=22,
                            color=COLOR_VEC_F, weight=BOLD)
        action_label.next_to(action_arrow, UP, buff=0.12)

        # Reaction — ground pushes ball UP (right side, points up)
        reaction_arrow = Arrow(
            np.array([arrow_x, arrow_bottom_y, 0]),
            np.array([arrow_x, arrow_top_y,    0]),
            color=COLOR_VEC_F, stroke_width=4.5, buff=0,
            max_tip_length_to_length_ratio=0.22
        )
        reaction_label = Text("Reaction", font="Segoe UI", font_size=22,
                              color=COLOR_VEC_F, weight=BOLD)
        reaction_label.next_to(reaction_arrow, UP, buff=0.12)

        self.play(
            GrowArrow(action_arrow),
            GrowArrow(reaction_arrow),
            FadeIn(action_label,   shift=DOWN * 0.06),
            FadeIn(reaction_label, shift=DOWN * 0.06),
            run_time=0.7,
            rate_func=rate_functions.ease_out_cubic
        )
        self.wait(0.5)

        # "Equal & opposite" — amber pulse together
        self.play(
            Indicate(action_arrow,   color=COLOR_AMBER, scale_factor=1.10),
            Indicate(reaction_arrow, color=COLOR_AMBER, scale_factor=1.10),
            run_time=0.85
        )
        self.wait(0.25)

        # Bounce — un-squash + arrows fade, then ball lifts off and clears
        self.play(
            ball.animate.restore(),
            FadeOut(action_arrow,   shift=DOWN * 0.08),
            FadeOut(reaction_arrow, shift=UP   * 0.08),
            FadeOut(action_label,   shift=DOWN * 0.05),
            FadeOut(reaction_label, shift=UP   * 0.05),
            run_time=0.2,
            rate_func=rate_functions.ease_out_cubic
        )
        self.play(
            ball.animate.move_to(np.array([0, 1.0, 0])),
            run_time=0.55,
            rate_func=rate_functions.ease_out_quad
        )
        self.wait(0.5)
        self.play(FadeOut(ball, shift=UP * 0.2), run_time=0.3)

        # ══════════════════════════════════════════════════════════
        #  ACT 2 · Horse-cart enters; both move forward together
        # ══════════════════════════════════════
        statement_group = VGroup(eyebrow_group)
        self.play(
            statement_group.animate
                .scale(0.80)
                .to_edge(UP, buff=0.35)
                .set_opacity(0.45),
            rate_func=rate_functions.ease_in_out_sine
        )

        # ══════════════════════════════════════════════════════════
        #  ACT 3 · Zoom into the rope; F and F' arrows reveal
        # ══════════════════════════════════════════════════════════
        rope_center = np.array([ROPE_CENTER_X, ROPE_CENTER_Y, 0])
        rope_left   = rope_center + LEFT  * ROPE_HALF_WIDTH
        rope_right  = rope_center + RIGHT * ROPE_HALF_WIDTH

        # Camera moves in to the rope — slow ease-in for "lean in and look"
        self.play(
            self.camera.frame.animate
                .scale(0.45)
                .move_to([-0.5,-1,0]),
            run_time=1.4,
            rate_func=rate_functions.linear
        )
        self.wait(0.5)
