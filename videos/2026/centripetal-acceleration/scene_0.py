from manim import *
import numpy as np

# ─────────────────────────────────────────────
#  BRAND PALETTE  (series-consistent)
# ─────────────────────────────────────────────
COLOR_BG        = "#0E1117"
COLOR_GROUND    = "#8E8E93"
COLOR_GREY_BALL = "#E5E5EA"
COLOR_BLUE_BALL = "#007AFF"
COLOR_VEC_F     = "#FF3B30"
COLOR_VEC_V     = "#32ADE6"
COLOR_GREEN     = "#34C759"
COLOR_AMBER     = "#FFCC00"
COLOR_PINK      = "#FF2D55"
COLOR_PURPLE    = "#AF52DE"
COLOR_WHITE     = "#E5E5EA"


# ═══════════════════════════════════════════════════════════════════
#  HELPERS  (matches the rest of the series)
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


def make_ball(color, radius=0.45):
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
#  SCENE · Stationary Ball with Uniform Motion
#  Ball is pinned. The world moves past it.
# ═══════════════════════════════════════════════════════════════════

class StationaryBallUniformMotion(Scene):
    def construct(self):
        self.camera.background_color = COLOR_BG

        # ── ambient backdrop ──────────────────────────────────────
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # ─────────────────────────────────────────────────────────
        #  GEOMETRY
        # ─────────────────────────────────────────────────────────
        GROUND_Y      = -2.3
        BALL_X        = -2.5
        BALL_RADIUS   = 0.45
        BALL_Y        = GROUND_Y + BALL_RADIUS    # sitting on the ground

        # ─────────────────────────────────────────────────────────
        #  HATCHED GROUND
        #  Two pieces side-by-side wider than the screen, so we can
        #  scroll them leftward and wrap without ever showing a seam.
        # ─────────────────────────────────────────────────────────
        TILE_WIDTH    = 16.0        # one tile spans well past the frame
        HATCH_SPACING = 0.32

        def make_ground_tile():
            tile = VGroup()
            # the solid top edge of the ground
            top = Line(
                np.array([-TILE_WIDTH / 2, GROUND_Y, 0]),
                np.array([ TILE_WIDTH / 2, GROUND_Y, 0]),
                color=COLOR_GROUND, stroke_width=2.5,
            )
            tile.add(top)
            # diagonal hatch strokes hanging below the top edge
            for x in np.arange(-TILE_WIDTH / 2, TILE_WIDTH / 2 + 0.01, HATCH_SPACING):
                tile.add(Line(
                    np.array([x, GROUND_Y, 0]),
                    np.array([x - 0.18, GROUND_Y - 0.25, 0]),
                    color=COLOR_GROUND, stroke_width=1.5, stroke_opacity=0.45,
                ))
            return tile

        ground_a = make_ground_tile()
        ground_b = make_ground_tile().shift(RIGHT * TILE_WIDTH)
        ground   = VGroup(ground_a, ground_b)
        ground.set_z_index(-5)

        # Scrolling updater: shift left, wrap when a tile leaves the frame.
        # Constant velocity is intentional — physics-honest, no easing here.
        GROUND_SPEED = 3.2  # units / second

        def scroll_ground(mob, dt):
            mob.shift(LEFT * GROUND_SPEED * dt)
            for tile in mob:
                # when a tile's right edge passes the left side of its pair,
                # leapfrog it to the right of the other tile
                if tile.get_right()[0] < -TILE_WIDTH / 2:
                    tile.shift(RIGHT * TILE_WIDTH * 2)

        # ─────────────────────────────────────────────────────────
        #  THE BALL
        #  Pinned to (BALL_X, BALL_Y). A gentle 1–2% vertical squash
        #  cycle sells "rolling contact" without being noticeable.
        # ─────────────────────────────────────────────────────────
        ball = make_ball(COLOR_BLUE_BALL, radius=BALL_RADIUS)
        ball.move_to(np.array([BALL_X, BALL_Y, 0]))

        squash_clock = ValueTracker(0)

        def squash_ball(mob):
            t = squash_clock.get_value()
            # small periodic squash; amplitude ~1.5%
            sx = 1.0 + 0.015 * np.sin(2 * PI * 2.2 * t)
            sy = 1.0 - 0.015 * np.sin(2 * PI * 2.2 * t)
            mob.become(make_ball(COLOR_BLUE_BALL, radius=BALL_RADIUS))
            mob.stretch_to_fit_width(2 * BALL_RADIUS * sx)
            mob.stretch_to_fit_height(2 * BALL_RADIUS * sy)
            # keep contact point on the ground line
            mob.move_to(np.array([BALL_X, GROUND_Y + BALL_RADIUS * sy, 0]))

        # drive the squash clock forward in real time
        clock_driver = Mobject()
        clock_driver.add_updater(lambda m, dt: squash_clock.increment_value(dt))
        self.add(clock_driver)

        # ─────────────────────────────────────────────────────────
        #  STAGE 1 · Quiet entrance
        # ─────────────────────────────────────────────────────────
        self.play(
            FadeIn(ground, shift=UP * 0.3),
            run_time=0.5, rate_func=smooth,
        )
        self.play(FadeIn(ball, scale=0.9), run_time=0.5, rate_func=smooth)
        self.wait(0.4)

        # ─────────────────────────────────────────────────────────
        #  STAGE 2 · The world starts moving
        # ─────────────────────────────────────────────────────────
        # speed multiplier — drives ground scroll AND streak velocity
        # so they decelerate together (they share the same airflow)
        speed_factor = ValueTracker(1.0)

        def scroll_ground_scaled(mob, dt):
            v = GROUND_SPEED * speed_factor.get_value()
            mob.shift(LEFT * v * dt)
            for tile in mob:
                if tile.get_right()[0] < -TILE_WIDTH / 2:
                    tile.shift(RIGHT * TILE_WIDTH * 2)

        

        ground.add_updater(scroll_ground_scaled)
        ball.add_updater(squash_ball)

        self.wait(1.6)

        # ─────────────────────────────────────────────────────────
        #  STAGE 3 · A force appears, opposing the motion
        #  Arrow points LEFT (against the ball's apparent rightward
        #  travel). It enters first, holds a beat — cause before effect.
        # ─────────────────────────────────────────────────────────
        force_arrow = Arrow(
            start=ball.get_right() + RIGHT * 1.6,
            end=ball.get_right() + RIGHT * 0.15,
            color=COLOR_VEC_F,
            stroke_width=7,
            max_tip_length_to_length_ratio=0.28,
            buff=0,
        )
        force_label = MathTex("F", color=COLOR_VEC_F, font_size=44)
        force_label.next_to(force_arrow, UP, buff=0.18)

        self.play(
            GrowArrow(force_arrow, rate_func=smooth),
            FadeIn(force_label, shift=DOWN * 0.15),
            run_time=0.5,
        )
        self.wait(0.5)   # hold — let the viewer register the cause

        # ─────────────────────────────────────────────────────────
        #  STAGE 4 · Constant force → uniform deceleration
        #  speed_factor: 1.0 → 0.0 LINEARLY over 2.5s.
        #  Linear (not eased) because constant F means constant a.
        # ─────────────────────────────────────────────────────────
        self.play(
            speed_factor.animate.set_value(0.0),
            run_time=2.0,
            rate_func=linear,
        )

        # at rest — hold the moment
        self.wait(0.3)

        # ─────────────────────────────────────────────────────────
        #  STAGE 5 · Force removed, scene settles, fade
        # ─────────────────────────────────────────────────────────
        ground.remove_updater(scroll_ground_scaled)
        ball.remove_updater(squash_ball)

        self.play(
            FadeOut(force_arrow, shift=LEFT * 0.3),
            FadeOut(force_label, shift=LEFT * 0.3),
            run_time=0.6, rate_func=smooth,
        )
        self.wait(0.4)
        self.play(
            FadeOut(ball, scale=0.9, run_time=0.9),
            FadeOut(ground, shift=DOWN * 0.3, run_time=1.1),
            rate_func=smooth,
        )
        self.wait(0.4)
