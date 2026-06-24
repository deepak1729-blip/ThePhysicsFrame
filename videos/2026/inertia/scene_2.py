"""
THE PHYSICS FRAME — SCENE 2 · GALILEO'S RAMPS
=============================================

PHYSICS HONESTY (series principle)
  The ball's motion is NOT driven by easing curves. Its speed at every point
  comes from energy conservation:  v(s) = sqrt( 2 g [ (y0 - y(s)) - mu * X(s) ] )
  where y0 is the release height, y(s) the current height, X(s) the horizontal
  distance covered, and mu the friction coefficient. Friction work = mu*m*g*X
  (kinetic friction over horizontal travel) is what makes the first run fall
  "just short" by exactly the right amount. On the flat floor a = 0, so the
  motion is genuinely constant-velocity (the only place `linear` is allowed).

TUNING KNOBS (eyeball after first render): G, TROUGH_X, R, the THETA_* angles,
RUN_TIME values, and the Act-4 camera zoom. Geometry is fully parametric.

Optional grounding overlays (halfpipe / air-hockey) are OFF by default; flip
USE_OVERLAYS to True and drop the named stills in beside this file.
"""

from manim import *
import numpy as np
import math

# ─────────────────────────────────────────────────────────────────────────
#  OBSERVATORY PALETTE  (verbatim from the series design system)
# ─────────────────────────────────────────────────────────────────────────
VOID      = "#0A0C10"   # base background
PANEL     = "#11151C"   # lifted surfaces
STARLIGHT = "#E8E6DF"   # primary text / the ball-as-character
DUST      = "#9A958C"   # secondary · metadata · the dimmed state
AMBER     = "#D98A3D"   # primary accent · focus  (THE LINE = the goal)
CYAN      = "#5B8FB0"   # secondary · sparing

# quantity pigments
C_GROUND  = "#7F8A99"   # ground / reference axis (the apparatus)
C_FORCE   = "#E06450"   # force pigment — used once, for the friction deficit
C_VEL     = "#57C08A"   # velocity — one quiet cameo

SERIF = "Spectral"      # ideas; italic is the channel's speaking voice
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION VOCABULARY  (carried over / extended from Scene 1)
# ═══════════════════════════════════════════════════════════════════════════
def corner_L(orientation, size=0.20, color=AMBER, width=1.4, opacity=0.7):
    """Registration corner — the Observatory mark that frames the animation."""
    sx = -1 if orientation[0] > 0 else 1
    sy = -1 if orientation[1] > 0 else 1
    h = Line(ORIGIN, RIGHT * size * sx, stroke_color=color,
             stroke_width=width, stroke_opacity=opacity)
    v = Line(ORIGIN, UP * size * sy, stroke_color=color,
             stroke_width=width, stroke_opacity=opacity)
    g = VGroup(h, v)
    g.anchor = orientation
    return g


def make_ball(color, radius=0.17):
    """Top-down ball: base disc + sheen + specular (series shading vocabulary).
    Exposes `.disc` (the base sphere, used as the trail anchor) and `.radius`."""
    g = VGroup()
    sphere = Circle(radius=radius)
    sphere.set_fill(color, opacity=1.0)
    sphere.set_sheen(-0.40, DR)
    sphere.set_stroke(color=STARLIGHT, width=1.4, opacity=0.18)
    g.add(sphere)
    rim = Circle(radius=radius)
    rim.set_fill(opacity=0)
    rim.set_stroke(color=color, width=2.6, opacity=0.45)
    g.add(rim)
    spec = Ellipse(width=radius * 0.50, height=radius * 0.32)
    spec.set_fill(STARLIGHT, opacity=0.62)
    spec.set_stroke(width=0)
    spec.move_to(np.array([-radius * 0.28, radius * 0.30, 0]))
    spec.rotate(-20 * DEGREES)
    g.add(spec)
    g.disc = sphere
    g.radius = radius
    return g


# ═══════════════════════════════════════════════════════════════════════════
class Scene2_GalileosRamps(MovingCameraScene):

    # ── locked geometry (every act reads from these) ──────────────────────
    G        = 11.0          # gravity in scene-units/s^2 (paces the runs)
    TROUGH_X = -2.40         # x of the valley centre
    GROUND_Y = -2.55         # the ground line / flat-floor height
    R        = 0.95          # trough radius (the rounded valley bottom)
    LINE_Y   =  0.60         # release height -> THE dashed reference line
    THETA_L  = 60            # fixed left-ramp angle (degrees)
    BALL_R   = 0.17

    # the right-ramp angle for each release, in order (degrees). 0 == flat.
    THETA_RUN_IDEAL = 50     # Act 2 ideal touch
    THETA_RUN_A3    = 34     # Act 3 gentler
    THETA_RUN_A4    = [25, 17, 11]   # Act 4 cadence (gentler, gentler, gentler)

    NL, NA, NR = 26, 44, 60  # fixed sample counts -> 1:1 track morphs

    def construct(self):
        self.A = np.array([self.TROUGH_X, self.GROUND_Y + self.R, 0.0])  # trough centre
        self.camera.frame.save_state()
        self.ghosts = VGroup()        # accumulating fan of past runs
        self.summit_ticks = VGroup()

        # Observatory frame marks, pinned to the camera so they survive zooms.
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()

        self.act1_assemble_and_flip()
        self.act2_anchor_and_almost()
        self.act3_gentler()
        self.act4_cadence()
        self.act5_flat_forever()
        self.act6_reframe()
        self.act7_lazy()

    # ── frame-mark plumbing ───────────────────────────────────────────────
    def _pin_frame_marks(self):
        inset = 0.34

        def updater(grp):
            f = self.camera.frame
            scl = f.get_width() / config.frame_width
            for c in grp:
                o = c.anchor
                c.set(width=0.40 * scl, height=0.40 * scl)
                c.move_to(f.get_corner(o) - o * inset * scl, aligned_edge=o)
        self.frame_marks.add_updater(updater)

    # ═══════════════════════════════════════════════ geometry / physics ═══
    def _tangent_left(self):
        t = math.radians(self.THETA_L)
        return self.A + self.R * np.array([-math.sin(t), -math.cos(t), 0])

    def _tangent_right(self, theta_deg):
        t = math.radians(theta_deg)
        return self.A + self.R * np.array([math.sin(t), -math.cos(t), 0])

    def _top_left(self):
        t = math.radians(self.THETA_L)
        P = self._tangent_left()
        s = (self.LINE_Y - P[1]) / math.sin(t)
        return P + s * np.array([-math.cos(t), math.sin(t), 0])

    def _top_right(self, theta_deg):
        t = math.radians(theta_deg)
        P = self._tangent_right(theta_deg)
        s = (self.LINE_Y - P[1]) / math.sin(t)
        return P + s * np.array([math.cos(t), math.sin(t), 0])

    def _rest_left(self):
        """Ball-CENTRE release point on the left ramp: the surface top-left
        pushed out by BALL_R along the ramp normal (so the ball rests on it)."""
        t = math.radians(self.THETA_L)
        # left ramp rises up-left; upward-facing normal points up-right
        normal = np.array([math.sin(t), math.cos(t), 0.0])
        return self._top_left() + self.BALL_R * normal

    def center_samples(self, theta_deg, x_cap=None):
        """Ball-centre trajectory (== the visible track line) for a given
        right-ramp angle. Left ramp + rounded trough arc + right ramp.
        `x_cap` ends the right side at a given x instead of at the line
        (used for the endless flat run). Fixed point counts -> clean morphs."""
        A = self.A
        P_L = self._tangent_left()
        T_L = self._top_left()
        ramp1 = np.array([T_L + (P_L - T_L) * i / (self.NL - 1)
                          for i in range(self.NL)])

        P_R = self._tangent_right(theta_deg)
        aL = math.atan2(P_L[1] - A[1], P_L[0] - A[0])
        aR = math.atan2(P_R[1] - A[1], P_R[0] - A[0])
        arc = np.array([A + self.R * np.array(
            [math.cos(aL + (aR - aL) * i / (self.NA - 1)),
             math.sin(aL + (aR - aL) * i / (self.NA - 1)), 0])
            for i in range(self.NA)])

        t = math.radians(theta_deg)
        direction = np.array([math.cos(t), math.sin(t), 0])
        if x_cap is not None:                       # flat / capped run
            s = (x_cap - P_R[0]) / max(math.cos(t), 1e-3)
            end = P_R + s * direction
        else:
            end = self._top_right(theta_deg)
        ramp2 = np.array([P_R + (end - P_R) * i / (self.NR - 1)
                          for i in range(self.NR)])

        return np.vstack([ramp1, arc, ramp2])

    def ball_center_path(self, theta_deg, x_cap=None):
        """The ball-CENTRE trajectory: the track surface (center_samples) pushed
        outward by BALL_R along the local surface normal, so the ball rests ON
        the track instead of sitting centred on it. The normal always points to
        the side the ball sits (upward, away from the U-track interior)."""
        surf = self.center_samples(theta_deg, x_cap=x_cap)
        n = len(surf)
        offset = np.empty_like(surf)
        for i in range(n):
            # local tangent via central differences (forward/backward at ends)
            if i == 0:
                tan = surf[1] - surf[0]
            elif i == n - 1:
                tan = surf[-1] - surf[-2]
            else:
                tan = surf[i + 1] - surf[i - 1]
            L = math.hypot(tan[0], tan[1])
            if L < 1e-9:
                normal = np.array([0.0, 1.0, 0.0])
            else:
                # rotate tangent +90°; flip so it points up (ball rests on top)
                normal = np.array([-tan[1], tan[0], 0.0]) / L
                if normal[1] < 0:
                    normal = -normal
            offset[i] = surf[i] + self.BALL_R * normal
        return offset

    def make_motion(self, pts, mu=0.0):
        """Honest energy-conservation profile along `pts`. Returns pos(u) with
        u in [0,1], total physics-time T, and the actually-traversed points
        (truncated at the turning point if friction stops it short)."""
        xs, ys = pts[:, 0], pts[:, 1]
        y0 = ys[0]
        times = [0.0]
        Xh = 0.0
        v_prev = 0.0
        turn = len(pts) - 1
        for i in range(1, len(pts)):
            dx, dy = xs[i] - xs[i - 1], ys[i] - ys[i - 1]
            ds = math.hypot(dx, dy)
            Xh += abs(dx)
            avail = self.G * (y0 - ys[i]) - mu * self.G * Xh
            if avail <= 1e-6:                       # ran out of energy -> stops
                turn = i
                times.append(times[-1] + ds / max(v_prev / 2, 1e-3))
                break
            v_i = math.sqrt(2 * avail)
            v_avg = max((v_prev + v_i) / 2, 1e-3)
            times.append(times[-1] + ds / v_avg)
            v_prev = v_i
        times = np.array(times)
        seg = pts[:turn + 1]
        sx, sy, st = seg[:, 0], seg[:, 1], times
        T = float(st[-1])

        def pos(u):
            tt = u * T
            return np.array([np.interp(tt, st, sx), np.interp(tt, st, sy), 0.0])
        return pos, T, seg

    def v_bottom(self):
        return math.sqrt(2 * self.G * (self.LINE_Y - self.GROUND_Y))

    # ═══════════════════════════════════════════════ run choreography ═════
    def roll_run(self, theta_deg, mu=0.0, run_time=2.2, ghost_color=DUST,
                 return_swing=False, tick=True, x_cap=None):
        """One release. Drives the ball along the honest profile, lays a live
        trail, freezes it into the ghost fan, and (optionally) drops a vertical
        tick up to the line and swings the ball back to the start."""
        pts = self.ball_center_path(theta_deg, x_cap=x_cap)        # ball centre
        surf = self.center_samples(theta_deg, x_cap=x_cap)         # contact line
        pos, T, _ = self.make_motion(pts, mu=mu)
        _, _, seg_surf = self.make_motion(surf, mu=mu)             # ghost on track

        self.ball.move_to(pos(0.0))
        u = ValueTracker(0.0)
        self.ball.add_updater(lambda m: m.move_to(pos(u.get_value())))

        trail = TracedPath(self.ball.disc.get_center, stroke_color=ghost_color,
                           stroke_width=3, dissipating_time=0.6,
                           stroke_opacity=0.7)
        self.add(trail)
        self.play(u.animate.set_value(1.0), run_time=run_time, rate_func=linear)
        self.ball.clear_updaters()
        self.remove(trail)

        # freeze the actual trajectory as a persistent ghost arc (on the track)
        ghost = VMobject().set_points_as_corners([p for p in seg_surf])
        ghost.set_stroke(ghost_color, width=2, opacity=0.0)
        self.ghosts.set_stroke(opacity=0.14)        # dim the older fan further
        self.add(ghost)
        self.play(ghost.animate.set_stroke(opacity=0.30), run_time=0.4)
        self.ghosts.add(ghost)

        end = self.ball.get_center()
        if tick:
            t_line = DashedLine(end, np.array([end[0], self.LINE_Y, 0]),
                                dash_length=0.10, color=AMBER,
                                stroke_width=1.4, stroke_opacity=0.0)
            self.add(t_line)
            self.play(t_line.animate.set_stroke(opacity=0.55), run_time=0.4)
            self.summit_ticks.add(t_line)

        if return_swing:                            # honest: it returns to height
            self.ball.add_updater(lambda m: m.move_to(pos(u.get_value())))
            self.play(u.animate.set_value(0.0), run_time=run_time * 0.92,
                      rate_func=linear)
            self.ball.clear_updaters()

    def fade_reset_to_left(self):
        """Quietly return the live ball to the left release point (used in the
        rapid Act-4 cadence where a full return swing would kill the rhythm)."""
        self.play(self.ball.animate.set_opacity(0.0), run_time=0.18)
        self.ball.move_to(self._rest_left())
        self.play(self.ball.animate.set_opacity(1.0), run_time=0.18)

    # ═══════════════════════════════════════════════════════════════ A1 ═══
    def act1_assemble_and_flip(self):
        # 1) The character arrives FIRST, alone, before any world exists.
        self.ball = make_ball(STARLIGHT, radius=self.BALL_R)
        self.ball.move_to(UP * 1.4)
        self.ball.set_z_index(8)
        self.play(FadeIn(self.ball, shift=DOWN * 0.5, scale=0.6),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        # 2) The world assembles AROUND it. Ground draws L->R; the U-track grows.
        self.ground = Line(LEFT * 14 + UP * self.GROUND_Y,
                           RIGHT * 14 + UP * self.GROUND_Y,
                           color=C_GROUND, stroke_width=2.0, stroke_opacity=0.85)
        self.play(Create(self.ground), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.add(self.frame_marks)
        self.play(self.frame_marks.animate.set_opacity(0.5), run_time=0.7)

        # settle the ball onto the left top as the track is carved beneath it
        self.track = VMobject().set_points_as_corners(
            [p for p in self.center_samples(self.THETA_RUN_IDEAL)])
        self.track.set_stroke(DUST, width=3, opacity=0.0)
        self.add(self.track)
        self.play(
            self.track.animate.set_stroke(opacity=0.8),
            self.ball.animate.move_to(self._rest_left()),
            run_time=1.3, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.current_theta = self.THETA_RUN_IDEAL
        self.wait(0.5)

        # 3) The reversed question. Show the OLD framing, then physically flip
        #    it (magic-move) into the real one. The flip IS the thesis.
        old = Text("What makes it stop?", font=SERIF, font_size=46,
                   color=STARLIGHT).move_to(UP * 2.45).set_z_index(12)
        self.play(Write(old), run_time=1.1)
        self.wait(0.9)
        new = Text("What keeps it going?", font=SERIF, font_size=46,
                   color=STARLIGHT, t2c={"going": AMBER},
                   t2w={"going": BOLD}).move_to(UP * 2.45).set_z_index(12)
        self.play(TransformMatchingShapes(old, new),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_sine)
        self.question = new
        self.wait(1.0)
        self.play(self.question.animate.scale(0.62).to_edge(UP, buff=0.45)
                  .set_opacity(0.65), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_cubic)

    # ═══════════════════════════════════════════════════════════════ A2 ═══
    def act2_anchor_and_almost(self):
        # THE LINE — the single most important object. Treat it as a reveal.
        self.line = DashedLine(
            np.array([self._top_left()[0], self.LINE_Y, 0]),
            RIGHT * 14 + UP * self.LINE_Y,
            dash_length=0.16, dashed_ratio=0.6, color=AMBER,
            stroke_width=2.4, stroke_opacity=0.95)
        self.play(Create(self.line), run_time=1.2,
                  rate_func=rate_functions.ease_in_out_sine)
        glow = self.line.copy().set_stroke(AMBER, width=7, opacity=0.5)
        self.play(ShowPassingFlash(glow, time_width=0.5), run_time=1.0)
        rel = Text("RELEASE HEIGHT", font=MONO, font_size=13, color=AMBER)
        rel.next_to(self.line.get_start(), UP, buff=0.14).align_to(
            self.line.get_start(), LEFT)
        self.play(FadeIn(rel, shift=UP * 0.06), run_time=0.5)
        self.wait(0.4)
        self.play(FadeOut(rel), run_time=0.5)

        # First release WITH friction -> stops just short. The gap is real:
        # it is exactly the friction work mu*g*X expressed as lost height.
        self.roll_run(self.THETA_RUN_IDEAL, mu=0.085, run_time=2.3,
                      ghost_color=DUST, tick=False)
        end = self.ball.get_center()

        # bracket the deficit and name it: friction (force pigment, used once)
        gap_top = np.array([end[0], self.LINE_Y, 0])
        brace = VGroup(
            Line(end + RIGHT * 0.16, gap_top + RIGHT * 0.16,
                 color=C_FORCE, stroke_width=2),
            Line(end + RIGHT * 0.10, end + RIGHT * 0.22,
                 color=C_FORCE, stroke_width=2),
            Line(gap_top + RIGHT * 0.10, gap_top + RIGHT * 0.22,
                 color=C_FORCE, stroke_width=2),
        )
        flbl = Text("FRICTION", font=MONO, font_size=13, color=C_FORCE)
        flbl.next_to(brace, RIGHT, buff=0.16)
        self.play(Create(brace), FadeIn(flbl, shift=RIGHT * 0.06), run_time=0.7)
        self.wait(1.0)

        # "Idealize away the mess" — the shimmer sweeps the track clean.
        shimmer = self.track.copy().set_stroke(STARLIGHT, width=5, opacity=0.9)
        self.play(
            ShowPassingFlash(shimmer, time_width=0.45),
            FadeOut(brace), FadeOut(flbl),
            self.track.animate.set_stroke(STARLIGHT, width=3, opacity=0.7),
            FadeOut(self.ghosts),
            run_time=1.3, rate_func=rate_functions.ease_in_out_sine,
        )
        self.ghosts = VGroup()
        # clean reset of the character to the top — the ideal world begins
        self.play(self.ball.animate.set_opacity(0.0), run_time=0.25)
        self.ball.move_to(self._rest_left())
        self.play(self.ball.animate.set_opacity(1.0), run_time=0.3)
        self.wait(0.4)

        # Frictionless release -> touches the line EXACTLY, then returns.
        self.roll_run(self.THETA_RUN_IDEAL, mu=0.0, run_time=2.2,
                      ghost_color=DUST, return_swing=True, tick=True)
        self.wait(0.8)

    # ═══════════════════════════════════════════════════════════════ A3 ═══
    def act3_gentler(self):
        new_track = VMobject().set_points_as_corners(
            [p for p in self.center_samples(self.THETA_RUN_A3)])
        new_track.match_style(self.track)
        # The LINE holds; only the right ramp lies back.
        self.play(Transform(self.track, new_track), run_time=1.3,
                  rate_func=rate_functions.ease_in_out_cubic)
        self.current_theta = self.THETA_RUN_A3
        self.wait(0.4)

        # Same height, longer reach. Keep the previous ghost arc beside it.
        self.roll_run(self.THETA_RUN_A3, mu=0.0, run_time=2.7,
                      ghost_color=DUST, return_swing=True, tick=True)
        self.wait(0.9)

    # ═══════════════════════════════════════════════════════════════ A4 ═══
    def act4_cadence(self):
        # three quick beats — gentler... gentler... gentler — camera easing back
        zooms = [1.18, 1.42, 1.72]
        run_times = [2.4, 2.7, 3.0]
        for theta, zoom, rt in zip(self.THETA_RUN_A4, zooms, run_times):
            new_track = VMobject().set_points_as_corners(
                [p for p in self.center_samples(theta)])
            new_track.match_style(self.track)
            self.play(
                Transform(self.track, new_track),
                self.camera.frame.animate.scale(
                    zoom / (self.camera.frame.get_width() / config.frame_width)
                ).move_to(RIGHT * (zoom - 1) * 3.2 + UP * (zoom - 1) * 0.6),
                run_time=1.0, rate_func=rate_functions.ease_in_out_cubic,
            )
            self.current_theta = theta
            self.roll_run(theta, mu=0.0, run_time=rt, ghost_color=DUST,
                          return_swing=False, tick=True)
            self.fade_reset_to_left()

        # The fan of ghost-arcs is the argument: height invariant, reach exploding.
        self.wait(1.0)

    # ═══════════════════════════════════════════════════════════════ A5 ═══
    def act5_flat_forever(self):
        # Restore a calm, stable framing centred on the ball's cruise line.
        self.play(
            self.camera.frame.animate.restore().move_to(RIGHT * 0.4 + UP * 0.2),
            FadeOut(self.ghosts), FadeOut(self.summit_ticks),
            run_time=1.2, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.ghosts = VGroup()
        self.summit_ticks = VGroup()

        # Final rotation: the right ramp lies all the way down to horizontal.
        flat_track = VMobject().set_points_as_corners(
            [p for p in self.center_samples(0.001, x_cap=12.0)])
        flat_track.match_style(self.track)
        self.play(Transform(self.track, flat_track), run_time=1.4,
                  rate_func=rate_functions.ease_in_out_cubic)

        # Make the geometric fact land: ramp and line are now parallel.
        par = Text("parallel lines never meet", font=SERIF, slant=ITALIC,
                   font_size=24, color=DUST).move_to(UP * 2.3 + RIGHT * 0.4)
        self.play(FadeIn(par, shift=UP * 0.08), run_time=0.7)
        self.wait(0.8)
        self.play(FadeOut(par), run_time=0.6)

        # Release onto the flat. Roll honestly down + through to centre frame...
        center_x = 0.4
        pts = self.ball_center_path(0.001, x_cap=center_x)
        pos, T, seg = self.make_motion(pts, mu=0.0)
        self.ball.move_to(pos(0.0))
        u = ValueTracker(0.0)
        self.ball.add_updater(lambda m: m.move_to(pos(u.get_value())))
        trail = TracedPath(self.ball.disc.get_center, stroke_color=DUST,
                           stroke_width=3, dissipating_time=0.7,
                           stroke_opacity=0.6)
        self.add(trail)
        self.play(u.animate.set_value(1.0), run_time=2.2, rate_func=linear)
        self.ball.clear_updaters()
        self.remove(trail)

        # ...then LOCK the ball at centre and scroll the world past it forever.
        v = min(self.v_bottom(), 3.0)               # constant cruise (no easing)
        line_y, ground_y = self.LINE_Y, self.GROUND_Y
        cy = self.ball.get_center()[1]

        world = VGroup()
        ground_long = Line(LEFT * 60 + UP * ground_y, RIGHT * 60 + UP * ground_y,
                           color=C_GROUND, stroke_width=2.0, stroke_opacity=0.85)
        line_long = DashedLine(LEFT * 60 + UP * line_y, RIGHT * 60 + UP * line_y,
                               dash_length=0.16, dashed_ratio=0.6, color=AMBER,
                               stroke_width=2.4, stroke_opacity=0.95)
        world.add(ground_long, line_long)
        for k in range(-120, 360):                  # floor markers, evenly spaced
            tx = k * 0.5
            tk = Line(UP * 0.06, DOWN * 0.06, color=C_GROUND, stroke_width=1.2,
                      stroke_opacity=0.30).move_to(RIGHT * tx + UP * ground_y)
            world.add(tk)
        world.set_z_index(-1)
        self.add(world)
        self.remove(self.track, self.ground, self.line)

        state = {"t": 0.0, "emit": 0.0}

        def scroll(m, dt):
            m.shift(LEFT * v * dt)
            state["t"] += dt
            state["emit"] += dt
            if state["emit"] >= 0.16:               # ball "emits" a fading dot
                state["emit"] = 0.0
                d = Dot(radius=0.05, color=DUST, fill_opacity=0.5)
                d.move_to(self.ball.disc.get_center())
                m.add(d)
        world.add_updater(scroll)

        self.ball.set_z_index(8)
        # Let it run LONGER than feels comfortable — that unease is the point.
        self.wait(5.5)
        self.scroll_world = world
        self.scroll_fn = scroll

    # ═══════════════════════════════════════════════════════════════ A6 ═══
    def act6_reframe(self):
        # A clean text beat against the still-cruising ball. One swapped word.
        old = Text("To MOVE, you need a reason.", font=SERIF, font_size=40,
                   color=STARLIGHT, t2c={"MOVE": AMBER}, t2w={"MOVE": BOLD})
        old.move_to(UP * 2.4 + RIGHT * 0.4).set_z_index(14)
        self.play(Write(old), run_time=1.1)
        self.wait(1.2)
        new = Text("To STOP, you need a reason.", font=SERIF, font_size=40,
                   color=STARLIGHT, t2c={"STOP": AMBER}, t2w={"STOP": BOLD})
        new.move_to(UP * 2.4 + RIGHT * 0.4).set_z_index(14)
        self.play(TransformMatchingShapes(old, new), run_time=1.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.reframe = new
        self.wait(1.8)
        self.play(self.reframe.animate.scale(0.7).to_edge(UP, buff=0.5)
                  .set_opacity(0.6), self.question.animate.scale(0.7).move_to([0,8,0]).set_opacity(0.0), 
                  rate_func=rate_functions.ease_in_out_cubic)

    # ═══════════════════════════════════════════════════════════════ A7 ═══
    def act7_lazy(self):
        # Ease the world to a stop and return full focus to the character.
        if hasattr(self, "scroll_world"):
            self.scroll_world.remove_updater(self.scroll_fn)
            self.play(self.scroll_world.animate.shift(LEFT * 0.6), run_time=1.4,
                      rate_func=rate_functions.ease_out_cubic)
        self.play(
            self.camera.frame.animate.move_to(self.ball.get_center() + UP * 0.6),
            run_time=1.0, rate_func=rate_functions.ease_in_out_cubic,
        )

        # Give it a voice — a thought resolving beside it.
        thought = VGroup(
            Text("Moving? I'll keep moving.", font=SERIF, slant=ITALIC,
                 font_size=24, color=STARLIGHT),
            Text("At rest? I'll stay at rest.", font=SERIF, slant=ITALIC,
                 font_size=24, color=STARLIGHT),
            Text("Don't disturb me.", font=SERIF, slant=ITALIC,
                 font_size=24, color=DUST),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        thought.next_to(self.ball, UR, buff=0.5).shift(UP * 0.3)
        thought.set_z_index(14)
        dots = VGroup(*[Dot(radius=0.03, color=STARLIGHT, fill_opacity=0.6)
                        for _ in range(3)])
        for i, d in enumerate(dots):
            d.move_to(self.ball.get_center()
                      + np.array([0.35 + i * 0.18, 0.30 + i * 0.16, 0]))
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots],
                              lag_ratio=0.3), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.06) for t in thought],
                              lag_ratio=0.25), run_time=1.4)
        self.wait(1.6)

        # Two paired vignettes — moving-continuing vs resting-staying: same attitude.
        self.play(FadeOut(thought), FadeOut(dots), run_time=0.6)
        v_move = self._vignette(moving=True).move_to(
            self.ball.get_center() + LEFT * 2.4 + DOWN * 1.7)
        v_rest = self._vignette(moving=False).move_to(
            self.ball.get_center() + RIGHT * 2.4 + DOWN * 1.7)
        eq = Text("same attitude", font=MONO, font_size=15, color=AMBER)
        eq.move_to(self.ball.get_center() + DOWN * 1.7)
        self.play(LaggedStart(FadeIn(v_move, shift=UP * 0.1),
                              FadeIn(v_rest, shift=UP * 0.1), lag_ratio=0.25),
                  run_time=0.9)
        self.play(FadeIn(eq, scale=0.7), run_time=0.5)
        self.play(eq.animate.scale(1.12), rate_func=there_and_back,
                  run_time=0.7)
        self.wait(1.0)
        self.play(FadeOut(v_move), FadeOut(v_rest), FadeOut(eq), run_time=0.7)

        # Land on the one-word distillation. Hold the ball with the word.
        lazy = Text("Lazy", font=SERIF, slant=ITALIC, font_size=58,
                    color=STARLIGHT).next_to(self.ball, UP, buff=0.55)
        lazy.set_z_index(14)
        self.play(Write(lazy), run_time=1.0)
        self.wait(0.8)

    def _vignette(self, moving):
        g = VGroup()
        b = Circle(radius=0.16, stroke_color=STARLIGHT, stroke_width=2,
                   fill_color=STARLIGHT, fill_opacity=0.9)
        base = Line(LEFT * 0.9, RIGHT * 0.9, color=C_GROUND, stroke_width=1.6,
                    stroke_opacity=0.6).next_to(b, DOWN, buff=0.16)
        g.add(base, b)
        if moving:
            for i, op in enumerate((0.5, 0.32, 0.16)):
                d = Line(ORIGIN, RIGHT * 0.16, stroke_color=C_VEL,
                         stroke_width=2.4, stroke_opacity=op)
                d.next_to(b, LEFT, buff=0.06 + i * 0.16)
                g.add(d)
            cap = Text("keeps going", font=MONO, font_size=12, color=DUST)
        else:
            cap = Text("stays put", font=MONO, font_size=12, color=DUST)
        cap.next_to(base, DOWN, buff=0.18)
        g.add(cap)
        return g
