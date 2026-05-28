from manim import *
import numpy as np
from collections import deque

# ─────────────────────────────────────────────
#  BRAND PALETTE  (consistent with the series)
# ─────────────────────────────────────────────
COLOR_BG        = "#0E1117"   # Dark Gray
COLOR_GROUND    = "#8E8E93"   # Mid Gray
COLOR_WHITE     = "#E5E5EA"   # Light Gray
COLOR_BLUE_BALL = "#007AFF"   # Apple Blue
COLOR_VEC_F     = "#FF3B30"   # Apple Red — force
COLOR_VEC_V     = "#32ADE6"   # Apple Cyan — velocity
COLOR_AMBER     = "#FFCC00"   # Apple Yellow


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

def make_particle(color=COLOR_WHITE, radius=0.085):
    """A bright point with a soft halo — the 'object' of the universe."""
    g = VGroup()
    # outer halo
    for r, op in [(radius * 4.0, 0.06),
                  (radius * 2.6, 0.14),
                  (radius * 1.7, 0.28)]:
        halo = Circle(radius=r, color=color,
                      stroke_width=0, fill_opacity=op).set_fill(color, opacity=op)
        g.add(halo)
    # core
    core = Dot(point=ORIGIN, radius=radius, color=color)
    core.set_fill(color, opacity=1.0)
    g.add(core)
    return g


# ═══════════════════════════════════════════════════════════════════
#  SCENE · Huygens Intro — Inertia → Force → Curvature
# ═══════════════════════════════════════════════════════════════════

class Scene1_HuygensIntro(Scene):
    def construct(self):
        self.camera.background_color = COLOR_BG
        grid = build_grid()
        grid.set_z_index(-10)
        self.add(grid)

        # ══════════════════════════════════════════════════════════
        #  ACT 1
        # ══════════════════════════════════════════════════════════
        self.wait(0.5)

        # Particle enters from far left, just off-screen
        START_X, END_X_STRAIGHT, Y_LINE = -7.5, 0.0, 1.2
        particle = make_particle(color=COLOR_WHITE, radius=0.085)
        particle.move_to([START_X, Y_LINE, 0]).set_z_index(5)

        TRAIL_LEN = 28          # number of stored samples
        TRAIL_WIDTH = 4.5

        trail_pts = deque(maxlen=TRAIL_LEN)
        trail_pts.append(particle.get_center().copy())

        trail = VGroup().set_z_index(4)
        self.add(trail)

        def update_trail(mob):
            trail_pts.append(particle.get_center().copy())
            
            pts = list(trail_pts)
            n = len(pts)
            
            # If there aren't enough points yet, make the trail an empty VGroup
            if n < 2:
                mob.become(VGroup())
                return
            
            # Build the new trail frame in a temporary VGroup
            new_trail = VGroup()
            for i in range(n - 1):
                # i = 0 is oldest (most faded); i = n-2 is newest (brightest)
                t = i / (n - 2) if n > 2 else 1.0
                op = t ** 1.8
                seg = Line(
                    pts[i], pts[i + 1],
                    stroke_width=TRAIL_WIDTH * (0.35 + 0.65 * t),
                    color=COLOR_WHITE,
                    stroke_opacity=op,
                )
                new_trail.add(seg)
            
            # Safely replace the on-screen trail with the newly calculated one
            mob.become(new_trail)

        trail.add_updater(update_trail)

        self.play(FadeIn(particle, scale=0.6),
                  run_time=0.6, rate_func=rate_functions.ease_out_cubic)

        self.play(
            particle.animate.move_to([END_X_STRAIGHT, Y_LINE, 0]),
            run_time=2.6,
            rate_func=linear,
        )

        self.wait(0.9)

        # ══════════════════════════════════════════════════════════
        #  ACT 2
        # ══════════════════════════════════════════════════════════
        particle_pos = particle.get_center()
  
        R = 1.6
        circle_center = particle_pos + DOWN * R

        F_LEN = 0.85
        F_STROKE = 5
        F_TIP_LEN = 0.22

        def make_force_arrow(tail, tip):
            return Arrow(
                tail, tip,
                color=COLOR_VEC_F, buff=0,
                stroke_width=F_STROKE,
                tip_length=F_TIP_LEN,
                max_tip_length_to_length_ratio=1.0,
                max_stroke_width_to_length_ratio=999,
            ).set_z_index(6)

        f_arrow = make_force_arrow(particle_pos, particle_pos + DOWN * F_LEN)

        self.play(
            GrowArrow(f_arrow),
            run_time=0.55,
            rate_func=rate_functions.ease_out_cubic,
        )

        self.wait(0.35)

        # ══════════════════════════════════════════════════════════
        #  ACT 3
        # ══════════════════════════════════════════════════════════

        theta = ValueTracker(PI / 2)

        def particle_position():
            a = theta.get_value()
            return circle_center + R * np.array([np.cos(a), np.sin(a), 0])

        particle.add_updater(lambda m: m.move_to(particle_position()))

        stroke_tracker = ValueTracker(F_STROKE)

        self.remove(f_arrow)

        def redraw_force():
            tail = particle_position()
            direction = circle_center - tail
            norm = np.linalg.norm(direction)
            if norm < 1e-6:
                return make_force_arrow(tail, tail + DOWN * F_LEN)
            tip = tail + (direction / norm) * F_LEN
            arr = Arrow(
                tail, tip,
                color=COLOR_VEC_F, buff=0,
                stroke_width=stroke_tracker.get_value(),
                tip_length=F_TIP_LEN,
                max_tip_length_to_length_ratio=1.0,
                max_stroke_width_to_length_ratio=999,
            ).set_z_index(6)
            return arr

        f_arrow = always_redraw(redraw_force)
        self.add(f_arrow)

        self.play(
            stroke_tracker.animate.set_value(F_STROKE + 4),
            run_time=0.16,
            rate_func=rate_functions.ease_out_quad,
        )
        self.play(
            stroke_tracker.animate.set_value(F_STROKE),
            run_time=0.18,
            rate_func=rate_functions.ease_in_quad,
        )
        self.play(
            theta.animate.set_value(PI / 2 - 2 * PI),
            run_time=4.2,
            rate_func=rate_functions.ease_in_out_sine,
        )

        particle.clear_updaters()
        trail.clear_updaters()  # Pause the trail to prevent shrinking

        self.wait(1.2)

        # ══════════════════════════════════════════════════════════
        #  ACT 4
        # ══════════════════════════════════════════════════════════

        self.play(
            FadeOut(particle, scale=0.5),
            FadeOut(trail), # Fade the trail cleanly 
            FadeOut(f_arrow),
            run_time=0.9,
            rate_func=rate_functions.ease_in_out_sine,
        )

        pulse_ring = Circle(radius=R, color=COLOR_WHITE,
                            stroke_width=2, stroke_opacity=0).move_to(circle_center)
        pulse_ring.set_z_index(3)
        self.add(pulse_ring)
        self.play(
            pulse_ring.animate.scale(1.18).set_stroke(opacity=0),
            run_time=1.6,
            rate_func=rate_functions.ease_out_quad,
        )
        self.remove(pulse_ring)

        self.wait(0.5)