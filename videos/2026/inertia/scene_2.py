from manim import *
import numpy as np
import math

# ── CORE PALETTE (project canvas) ──
VOID      = "#0A0C10"   # base background — every scene
PANEL     = "#11151C"   # lifted surfaces
STARLIGHT = "#E8E6DF"   # primary text / default stroke / the ball
DUST      = "#9A958C"   # secondary text, metadata, dimmed state
AMBER     = "#D98A3D"   # the single focus accent
CYAN      = "#5B8FB0"   # secondary accent, sparing
SPEC      = "#F6F4EE"   # ball specular highlight

# ── QUANTITY PIGMENTS (held for the whole video) ──
VEL    = "#57C08A"   # velocity v
FORCE  = "#E06450"   # force F  (the nudge / the stop-tap)
GROUND = "#7F8A99"   # the ground / the ramp apparatus

FONT_SERIF = "Spectral"
FONT_MONO  = "Space Mono"

config.background_color = VOID

# ── SCENE GEOMETRY (one source of truth) ──
VALLEY_Y = -2.55          # surface y at the valley vertex V
HEIGHT_Y = 0.55           # ball-CENTRE release height  →  the dashed line
R_BALL   = 0.26
R_FILLET = 0.85           # smooth valley fillet radius
AL_DEG   = 56             # left ramp angle (fixed — the constant side)
FLAT_LEN = 7.5            # how far the flat floor runs before perspective
GRAV     = 6.0            # gravity scale (tunes run feel)
SIM_DT   = 1 / 60
V_FLOOR  = 0.12           # tiny minimum speed so a run gets going / finishes
MAXSTEPS = 1500


# ═══════════════════════════════════════════════════════════════════════════
#  BACKDROP & CHARACTER
# ═══════════════════════════════════════════════════════════════════════════
def build_backdrop():
    """A barely-there dust grid — texture without clutter (near-empty frame)."""
    grid = VGroup()
    max_x, max_y, spacing = 14, 8, 0.7

    def fading_line(start, end, peak):
        segs = VGroup()
        vec = end - start
        N = 26
        for i in range(N):
            p1 = start + vec * (i / N)
            p2 = start + vec * ((i + 1) / N)
            t = (i + 0.5) / N
            op = peak * (1 - (2 * t - 1) ** 2)
            segs.add(Line(p1, p2, stroke_color=DUST, stroke_width=1,
                          stroke_opacity=op))
        return segs

    for x in np.arange(-max_x, max_x + 0.1, spacing):
        peak = 0.05 * (1 - (abs(x) / max_x) ** 1.5)
        if peak > 0:
            grid.add(fading_line(UP * max_y + RIGHT * x,
                                 DOWN * max_y + RIGHT * x, peak))
    for y in np.arange(-max_y, max_y + 0.1, spacing):
        peak = 0.05 * (1 - (abs(y) / max_y) ** 1.5)
        if peak > 0:
            grid.add(fading_line(LEFT * max_x + UP * y,
                                 RIGHT * max_x + UP * y, peak))
    return grid


def make_ball(radius=R_BALL, color=STARLIGHT):
    """The recurring character: soft halo + sheen + specular. Reused all scene."""
    g = VGroup()
    halo = Circle(radius=radius * 1.7, stroke_width=0)
    halo.set_fill(color, opacity=0.05)
    core = Circle(radius=radius)
    core.set_fill(color, opacity=1.0)
    core.set_sheen(-0.5, DR)
    core.set_stroke(DUST, width=1.1, opacity=0.35)
    rim = Circle(radius=radius)
    rim.set_fill(opacity=0)
    rim.set_stroke(color, width=2.2, opacity=0.5)
    spec = Ellipse(width=radius * 0.5, height=radius * 0.32)
    spec.set_fill(SPEC, opacity=0.7)
    spec.set_stroke(width=0)
    spec.move_to(np.array([-radius * 0.30, radius * 0.32, 0]))
    spec.rotate(-20 * DEGREES)
    g.add(halo, core, rim, spec)
    return g


def contact_shadow(radius=R_BALL):
    sh = Ellipse(width=radius * 2.1, height=radius * 0.55, stroke_width=0)
    sh.set_fill(BLACK, opacity=0.32)
    return sh


# ═══════════════════════════════════════════════════════════════════════════
#  RAMP GEOMETRY  (left ramp fixed; right ramp angle = the variable)
# ═══════════════════════════════════════════════════════════════════════════
def ramp_geometry(aR_deg):
    aL = math.radians(AL_DEG)
    aR = math.radians(aR_deg)
    V = np.array([0.0, VALLEY_Y, 0.0])
    dirL = np.array([-math.cos(aL), math.sin(aL), 0.0])   # up the left ramp
    dirR = np.array([math.cos(aR),  math.sin(aR), 0.0])   # up the right ramp
    nL = np.array([math.sin(aL),  math.cos(aL), 0.0])     # outward normal (left)
    nR = np.array([-math.sin(aR), math.cos(aR), 0.0])     # outward normal (right)

    bis = dirL + dirR
    bis = bis / np.linalg.norm(bis)
    beta = math.acos(max(-1.0, min(1.0, float(np.dot(dirL, dirR)))))
    Cf = V + bis * (R_FILLET / math.sin(beta / 2))
    tL = V + dirL * float(np.dot(Cf - V, dirL))
    tR = V + dirR * float(np.dot(Cf - V, dirR))

    sL = (HEIGHT_Y - VALLEY_Y - R_BALL * math.cos(aL)) / math.sin(aL)
    L_top = V + dirL * sL

    if aR_deg > 0.5:
        sR = (HEIGHT_Y - VALLEY_Y - R_BALL * math.cos(aR)) / math.sin(aR)
        R_top = V + dirR * sR
        reaches = True
    else:
        R_top = V + dirR * FLAT_LEN
        reaches = False

    return dict(V=V, dirL=dirL, dirR=dirR, nL=nL, nR=nR, Cf=Cf,
                tL=tL, tR=tR, L_top=L_top, R_top=R_top, reaches=reaches)


def _arc_samples(center, p_start, p_end, n):
    a0 = math.atan2((p_start - center)[1], (p_start - center)[0])
    a1 = math.atan2((p_end - center)[1], (p_end - center)[0])
    d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi          # short sweep
    r = float(np.linalg.norm(p_start - center))
    return [center + r * np.array([math.cos(a0 + d * t),
                                   math.sin(a0 + d * t), 0.0])
            for t in np.linspace(0, 1, n)]


def surface_group(aR_deg):
    """The drawn ramp surface (ground pigment) + a faint under-glow."""
    g = ramp_geometry(aR_deg)
    pts = [g["L_top"], g["tL"]]
    pts += _arc_samples(g["Cf"], g["tL"], g["tR"], 28)[1:-1]
    pts += [g["tR"], g["R_top"]]
    line = VMobject(stroke_color=GROUND, stroke_width=3.4)
    line.set_points_as_corners(pts)
    glow = VMobject(stroke_color=GROUND, stroke_width=9, stroke_opacity=0.07)
    glow.set_points_as_corners(pts)
    return VGroup(glow, line)


def center_path(aR_deg):
    """Dense ball-CENTRE positions from release (left) to far end (right)."""
    g = ramp_geometry(aR_deg)
    L_top, tL, tR, R_top = g["L_top"], g["tL"], g["tR"], g["R_top"]
    nL, nR, Cf = g["nL"], g["nR"], g["Cf"]

    def lin(a, b, n):
        return [a + (b - a) * t for t in np.linspace(0, 1, max(n, 2))]

    n_left = int(np.linalg.norm(tL - L_top) / 0.045) + 2
    n_arc = 26
    n_right = int(np.linalg.norm(R_top - tR) / 0.045) + 2

    left_c = [p + R_BALL * nL for p in lin(L_top, tL, n_left)]
    arc_c = [p + R_BALL * (Cf - p) / np.linalg.norm(Cf - p)
             for p in _arc_samples(Cf, tL, tR, n_arc)]
    right_c = [p + R_BALL * nR for p in lin(tR, R_top, n_right)]
    return left_c + arc_c[1:-1] + right_c


def simulate(pts):
    """Energy-honest trajectory: v = sqrt(2g·drop) integrated along the path."""
    P = [np.array(p) for p in pts]
    HY = P[0][1]
    seg = [float(np.linalg.norm(P[i + 1] - P[i])) for i in range(len(P) - 1)]
    cum = [0.0]
    for s in seg:
        cum.append(cum[-1] + s)
    total = cum[-1]

    def point_at(s):
        s = min(max(s, 0.0), total)
        lo, hi = 0, len(cum) - 1
        while lo < hi - 1:
            mid = (lo + hi) // 2
            if cum[mid] <= s:
                lo = mid
            else:
                hi = mid
        f = (s - cum[lo]) / max(seg[lo], 1e-9)
        return P[lo] * (1 - f) + P[lo + 1] * f

    out = [P[0]]
    s = 0.0
    for _ in range(MAXSTEPS):
        y = point_at(s)[1]
        v = math.sqrt(max(2 * GRAV * (HY - y), 0.0))
        v = max(v, V_FLOOR)
        s += v * SIM_DT
        out.append(point_at(s))
        if s >= total:
            break
    out.append(P[-1])
    return out


def subsample(pts, n=90):
    if len(pts) <= n:
        return pts
    idx = np.linspace(0, len(pts) - 1, n).astype(int)
    return [pts[i] for i in idx]


# convenient constants derived from the fixed left ramp
_REL = ramp_geometry(56)
RELEASE_CENTER = _REL["L_top"] + R_BALL * _REL["nL"]


# ═══════════════════════════════════════════════════════════════════════════
class Scene2_WhatStopsIt(MovingCameraScene):

    def construct(self):
        self.camera.frame.save_state()
        self.backdrop = build_backdrop().set_z_index(-20)
        self.add(self.backdrop)

        self.aR = ValueTracker(56)          # the variable: right-ramp angle
        self.ghosts = VGroup().set_z_index(1)   # accumulating arcs (Act 4)
        self.landing_dots = VGroup().set_z_index(2)

        self.act1_the_question()
        self.act2_same_height()
        self.act3_gentle_the_slope()
        self.act4_gentler()
        self.act5_flat_forever()
        self.act6_the_flip()

    # ── shared run helper: play a pre-simulated trajectory, honestly ──
    def run_ball(self, ball, positions, run_time, trail=True,
                 trail_color=STARLIGHT, stop_index=None):
        N = len(positions)
        end = (stop_index if stop_index is not None else N - 1)
        idx = ValueTracker(0)
        ball.add_updater(
            lambda m: m.move_to(positions[int(np.clip(idx.get_value(), 0, N - 1))]))
        tr = None
        if trail:
            tr = TracedPath(ball.get_center, stroke_color=trail_color,
                            stroke_width=3, dissipating_time=0.5)
            tr.set_stroke(opacity=0.5)
            tr.set_z_index(ball.z_index - 1)
            self.add(tr)
        self.play(idx.animate.set_value(end), run_time=run_time,
                  rate_func=linear)
        ball.clear_updaters()
        return tr

    # ===================================================================== A1
    def act1_the_question(self):
        # Cold open: a single faint floor line, low and centred.
        floor = Line([-4.4, VALLEY_Y, 0], [4.4, VALLEY_Y, 0],
                     color=GROUND, stroke_width=3.0, stroke_opacity=0.85)
        self.play(Create(floor), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)

        # A small abstract block slides in from the left and DECELERATES.
        block = RoundedRectangle(width=0.5, height=0.5, corner_radius=0.08,
                                 stroke_color=STARLIGHT, stroke_width=2.2,
                                 fill_color=PANEL, fill_opacity=1.0)
        block.move_to([-6.3, VALLEY_Y + 0.25, 0]).set_z_index(5)
        sh = contact_shadow(0.25).move_to([-6.3, VALLEY_Y - 0.02, 0]).set_z_index(4)
        sh.add_updater(lambda m: m.move_to([block.get_center()[0],
                                            VALLEY_Y - 0.02, 0]))
        self.add(sh)
        self.play(block.animate.move_to([-1.4, VALLEY_Y + 0.25, 0]),
                  run_time=1.6, rate_func=rate_functions.ease_out_cubic)
        sh.clear_updaters()
        self.wait(0.4)

        # The question writes above it.
        q = Text("What actually stops it?", font=FONT_SERIF, font_size=38,
                 weight="LIGHT", color=STARLIGHT)
        q.move_to([0, 1.7, 0]).set_z_index(8)
        self.play(Write(q), run_time=1.1)
        self.wait(0.9)

        # METHOD BEAT — don't cut, TRANSFORM: the floor bends & extrudes up at
        # both ends into the U-shaped ramp track. Apparatus replaces object.
        # >>> EDIT: optional Galileo-ramp cutaway lands right here.
        target = surface_group(56).set_z_index(3)
        self.play(
            ReplacementTransform(floor, target[1]),
            FadeIn(target[0]),
            FadeOut(block, scale=0.6),
            FadeOut(sh),
            q.animate.set_opacity(0.0).shift(UP * 0.2),
            run_time=1.5, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.remove(q, target)

        # Hand the static target over to the LIVE, angle-driven surface.
        self.surface = always_redraw(lambda: surface_group(self.aR.get_value()))
        self.surface.set_z_index(3)
        self.add(self.surface)
        self.wait(0.6)

    # ===================================================================== A2
    def act2_same_height(self):
        # The ball appears at the top of the LEFT ramp.
        ball = make_ball().move_to(RELEASE_CENTER).set_z_index(5)
        self.ball = ball
        self.play(FadeIn(ball, scale=0.7), run_time=0.6,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.3)

        # THE most important reveal: draw the dashed HEIGHT LINE, left→right,
        # anchored at release height. It persists, unchanged, forever after.
        glow = Line([-7, HEIGHT_Y, 0], [34, HEIGHT_Y, 0],
                    color=STARLIGHT, stroke_width=7, stroke_opacity=0.05)
        dash = DashedLine([-7, HEIGHT_Y, 0], [34, HEIGHT_Y, 0],
                          color=STARLIGHT, stroke_width=2.2,
                          dash_length=0.16, dashed_ratio=0.55)
        dash.set_stroke(opacity=0.8)
        tag = Text("RELEASE HEIGHT", font=FONT_MONO, font_size=28, color=DUST)
        tag.next_to([-4.6, HEIGHT_Y, 0], UP, buff=0.14).align_to([-4.6, 0, 0], LEFT)
        self.height_line = VGroup(glow, dash, tag).set_z_index(2)

        self.play(Create(dash), FadeIn(glow), run_time=1.1,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeIn(tag, shift=DOWN * 0.06), run_time=0.5)
        self.wait(0.6)

        # Release — roll down, through the valley, up the right ramp.
        # A friction-truncated run: it stops a hair BELOW the line.
        pts = simulate(center_path(56))
        gap = 0.20
        stop_i = len(pts) - 1
        for i in range(len(pts) - 1, -1, -1):
            if pts[i][0] > 0.2 and pts[i][1] < HEIGHT_Y - gap:
                stop_i = i
                break
        tr = self.run_ball(ball, pts, run_time=2.3, stop_index=stop_i,
                           trail_color=STARLIGHT)
        self.wait(0.4)
        self.remove(tr)

        # Push in slightly on the gap. A tiny "should-have-reached" tick.
        peak = ball.get_center()
        line_pt = np.array([peak[0], HEIGHT_Y, 0])
        tick = Line(line_pt + LEFT * 0.16, line_pt + RIGHT * 0.16,
                    color=STARLIGHT, stroke_width=2).set_z_index(7)
        ping = Circle(radius=0.05, color=STARLIGHT, stroke_width=2.5,
                      fill_opacity=0).move_to(line_pt).set_z_index(7)
        bracket = VGroup(
            Line(peak + UP * (R_BALL + 0.02), line_pt + DOWN * 0.02,
                 color=DUST, stroke_width=2),
            Line(peak + UP * (R_BALL + 0.02) + LEFT * 0.08,
                 peak + UP * (R_BALL + 0.02) + RIGHT * 0.08,
                 color=DUST, stroke_width=2),
        ).set_z_index(7)
        fric = Text("friction", font=FONT_SERIF, font_size=20, slant=ITALIC,
                    color=DUST).next_to(bracket, RIGHT, buff=0.16).set_z_index(7)

        self.play(self.camera.frame.animate.set(width=8.5)
                  .move_to(peak + UP * 0.55 + RIGHT * 0.2),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_cubic)
        self.play(Create(tick), FadeIn(ping), run_time=0.4)
        self.play(ping.animate.scale(2.4).set_stroke(opacity=0.0), run_time=0.5)
        self.remove(ping)
        self.play(Create(bracket), FadeIn(fric, shift=LEFT * 0.08), run_time=0.6)
        self.wait(0.9)

        # IDEALIZE. "Ignore friction." A clean shimmer; the gap CLOSES; the
        # ball kisses the line exactly. From here every run returns to the line.
        ideal = Text("Ignore friction.", font=FONT_SERIF, font_size=26,
                     slant=ITALIC, color=CYAN).move_to(peak + UP * 1.45 + RIGHT * 0.2)
        ideal.set_z_index(8)
        self.play(FadeIn(ideal, shift=DOWN * 0.1), run_time=0.6)

        shimmer = self.surface.copy()
        shimmer.set_z_index(4)
        for sub in shimmer:
            sub.set_stroke(CYAN, opacity=0.0)
        self.add(shimmer)
        self.play(
            FadeOut(bracket), FadeOut(fric), FadeOut(tick),
            shimmer[1].animate.set_stroke(CYAN, width=4, opacity=0.7),
            run_time=0.5)
        self.play(
            ball.animate.move_to(pts[-1]),       # gap closes — kisses the line
            shimmer[1].animate.set_stroke(opacity=0.0),
            run_time=0.7, rate_func=rate_functions.ease_in_out_sine)
        self.remove(shimmer)

        kiss = Circle(radius=0.05, color=STARLIGHT, stroke_width=2.5,
                      fill_opacity=0).move_to(pts[-1]).set_z_index(7)
        self.add(kiss)
        self.play(kiss.animate.scale(3).set_stroke(opacity=0.0), run_time=0.5)
        self.remove(kiss)
        self.wait(0.7)

        self.act2_landing_x = float(pts[-1][0])

        self.play(
            FadeOut(ideal, shift=UP * 0.1),
            Restore(self.camera.frame),
            run_time=1.1, rate_func=rate_functions.ease_in_out_cubic)
        self.wait(0.4)

    # ===================================================================== A3
    def act3_gentle_the_slope(self):
        ball = self.ball

        # Reset the ball to the release point (same height, every run).
        self.play(FadeOut(ball, scale=0.7), run_time=0.4)
        ball.move_to(RELEASE_CENTER)
        self.play(FadeIn(ball, scale=0.7), run_time=0.4)

        # ROTATE the right ramp gentler — a deliberate, visible pivot at the
        # valley bottom. The height line does NOT move. Hold the contrast.
        pivot = Dot(ramp_geometry(38)["V"], radius=0.045, color=DUST).set_z_index(4)
        self.play(FadeIn(pivot, scale=0.6), run_time=0.3)
        self.play(self.aR.animate.set_value(38), run_time=0.85,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.7)

        # Release again — travels noticeably farther to the SAME line.
        pts = simulate(center_path(38))
        tr = self.run_ball(ball, pts, run_time=2.5, trail_color=STARLIGHT)
        self.wait(0.6)
        self.play(FadeOut(tr), run_time=0.3)
        self.remove(tr)

        land_x = float(pts[-1][0])

        # Faint GHOST of Act-2's shorter landing point, beside the new one.
        ghost = Dot([self.act2_landing_x, HEIGHT_Y, 0], radius=0.06,
                    color=DUST).set_z_index(5).set_opacity(0.5)
        new_dot = Dot([land_x, HEIGHT_Y, 0], radius=0.07,
                      color=AMBER).set_z_index(5)
        self.play(FadeIn(ghost, scale=0.6), FadeIn(new_dot, scale=0.6),
                  run_time=0.5)

        # DISTANCE bracket along the floor — the VARIABLE, in Amber focus.
        by = VALLEY_Y - 0.7
        dist = VGroup(
            Line([0, by, 0], [land_x, by, 0], color=AMBER, stroke_width=2.4),
            Line([0, by - 0.12, 0], [0, by + 0.12, 0], color=AMBER, stroke_width=2.4),
            Line([land_x, by - 0.12, 0], [land_x, by + 0.12, 0],
                 color=AMBER, stroke_width=2.4),
        ).set_z_index(6)
        dist_lab = Text("distance", font=FONT_SERIF, font_size=22, slant=ITALIC,
                        color=AMBER).next_to(dist[0], DOWN, buff=0.14).set_z_index(6)
        self.play(Create(dist), FadeIn(dist_lab, shift=UP * 0.08), run_time=0.8)
        self.wait(1.1)

        # tidy up, keep the new landing dot as the first of the procession
        self.landing_dots.add(new_dot)
        self.add(self.landing_dots)
        self.play(FadeOut(VGroup(dist, dist_lab, ghost, pivot)), run_time=0.7)
        self.wait(0.3)

    # ===================================================================== A4
    def act4_gentler(self):
        ball = self.ball
        angles = [30, 24, 19, 15]
        rhythm = [2.0, 1.7, 1.45, 1.25]   # accelerate the flipbook

        for k, (aR, rt) in enumerate(zip(angles, rhythm)):
            # age the older ghosts — the newest run will be the crispest "now"
            for gm in self.ghosts:
                gm.set_stroke(opacity=max(gm.get_stroke_opacity() * 0.6, 0.05))

            # reset the ball; swing the ramp gentler (height line stays pinned)
            ball.move_to(RELEASE_CENTER)
            self.play(self.aR.animate.set_value(aR), run_time=0.6,
                      rate_func=rate_functions.ease_in_out_sine)

            pts = simulate(center_path(aR))
            land_x = float(pts[-1][0])

            # pull the camera back as the dots march toward the horizon
            cam_w = min(land_x * 1.55 + 8.5, 26)
            cam_c = np.array([land_x * 0.42, 0.1, 0])
            self.play(self.camera.frame.animate.set(width=cam_w).move_to(cam_c),
                      run_time=0.7, rate_func=rate_functions.ease_in_out_sine)

            tr = self.run_ball(ball, pts, run_time=rt, trail_color=STARLIGHT)
            self.play(FadeOut(tr), run_time=0.25)
            self.remove(tr)

            # the run leaves a persistent ghost arc + an Amber landing dot
            arc = VMobject(stroke_color=STARLIGHT, stroke_width=2.4,
                           stroke_opacity=0.55)
            arc.set_points_as_corners([np.array(p) for p in subsample(pts, 90)])
            self.ghosts.add(arc)
            self.add(self.ghosts)
            dot = Dot([land_x, HEIGHT_Y, 0], radius=0.07, color=AMBER).set_z_index(2)
            self.landing_dots.add(dot)
            self.add(self.landing_dots)
            self.play(FadeIn(dot, scale=0.5), run_time=0.3)
            self.wait(0.25)

        self.wait(0.8)

    # ===================================================================== A5
    def act5_flat_forever(self):
        ball = self.ball

        # Frame the contrast cleanly before the final rotation.
        self.play(self.camera.frame.animate.set(width=20).move_to([4.0, 0.0, 0]),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_cubic)

        ball.move_to(RELEASE_CENTER)

        # FINAL ROTATION: the right ramp all the way down to FLAT — now
        # perfectly parallel to the dashed height line. Pause on the payoff:
        # parallel forever; the gap never closes; the meeting point fled to ∞.
        self.play(self.aR.animate.set_value(0.0), run_time=1.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)

        # a quiet "the gap never closes" double-tick at two far separations
        g_far = VGroup(
            Line([6, VALLEY_Y + R_BALL * 2, 0], [6, HEIGHT_Y, 0],
                 color=DUST, stroke_width=1.4, stroke_opacity=0.5),
            Line([10.5, VALLEY_Y + R_BALL * 2, 0], [10.5, HEIGHT_Y, 0],
                 color=DUST, stroke_width=1.4, stroke_opacity=0.5),
        ).set_z_index(4)
        self.play(Create(g_far), run_time=0.6)
        self.wait(0.6)
        self.play(FadeOut(g_far), run_time=0.5)

        # Release one last time — down the left, through the valley, onto the
        # flat — and it just KEEPS GOING. Camera tracks; it does not slow.
        pts = simulate(center_path(0.0))
        N = len(pts)
        idx = ValueTracker(0)
        ball.add_updater(
            lambda m: m.move_to(pts[int(np.clip(idx.get_value(), 0, N - 1))]))
        tr = TracedPath(ball.get_center, stroke_color=STARLIGHT,
                        stroke_width=3, dissipating_time=0.55)
        tr.set_stroke(opacity=0.5)
        self.add(tr)
        # camera follows the ball's x once it's on the flat
        cam = self.camera.frame
        cam.add_updater(lambda m: m.move_to(
            [max(4.0, ball.get_center()[0] + 2.0), 0.0, 0]))
        self.play(idx.animate.set_value(N - 1), run_time=3.0, rate_func=linear)
        cam.clear_updaters()
        ball.clear_updaters()
        self.remove(tr)
        self.wait(0.4)

        # ── THE HOLD OF THE SCENE: extend the floor to a vanishing point. ──
        # >>> EDIT: the air-hockey / curling cut belongs right here (~2 s).
        self.play(Restore(self.camera.frame), run_time=1.2,
                  rate_func=rate_functions.ease_in_out_cubic)

        # perspective road that recedes to the right, meeting the horizon
        # (= the height line) only at infinity.
        self.VP = np.array([5.8, HEIGHT_Y, 0.0])
        self.FG = np.array([-5.2, VALLEY_Y + R_BALL, 0.0])
        self.WMAX = 2.0
        self.road_phase = ValueTracker(0.0)
        NR = 16

        def road_point(p):                # p: 0 = at VP (far), 1 = foreground
            g = p ** 1.7
            return self.VP + (self.FG - self.VP) * g, self.WMAX * (p ** 1.7), g

        def make_rungs():
            grp = VGroup()
            ph = self.road_phase.get_value()
            for k in range(NR):
                p = (ph + k / NR) % 1.0
                c, hw, g = road_point(p)
                op = float(np.clip(g * 1.6, 0, 0.5)) * float(np.clip((1.04 - g) * 4, 0, 1))
                grp.add(Line(c + UP * hw, c + DOWN * hw, color=DUST,
                             stroke_width=0.8 + 2.2 * g, stroke_opacity=op))
            return grp.set_z_index(-2)

        top_rail = Line(self.VP, self.FG + UP * self.WMAX, color=DUST,
                        stroke_width=1.4, stroke_opacity=0.32).set_z_index(-2)
        bot_rail = Line(self.VP, self.FG + DOWN * self.WMAX, color=DUST,
                        stroke_width=1.4, stroke_opacity=0.32).set_z_index(-2)

        # the ball becomes a steady, shrinking dot receding toward the VP
        dot_p = 0.55
        dc, _, _ = road_point(dot_p)
        dot = make_ball(radius=0.09).move_to(dc).set_z_index(3)

        self.play(
            FadeOut(self.ghosts), FadeOut(self.landing_dots),
            FadeOut(self.surface),
            Create(top_rail), Create(bot_rail),
            ReplacementTransform(ball, dot),
            run_time=1.3, rate_func=rate_functions.ease_in_out_sine)

        rungs = always_redraw(make_rungs)
        self.add(rungs)

        # the flow never stops — constant speed, forever
        driver = Mobject()
        driver.add_updater(lambda m, dt: self.road_phase.increment_value(dt * 0.10))
        self.add(driver)

        # a faint mote-trail keeps the steady dot alive without it moving
        trail = TracedPath(dot.get_center, stroke_color=STARLIGHT,
                           stroke_width=2, dissipating_time=0.6)
        trail.set_stroke(opacity=0.0)
        self.add(trail)

        self.wait(4.0)        # the longest hold in the scene — let it sit

        driver.clear_updaters()
        self.play(
            FadeOut(VGroup(rungs, top_rail, bot_rail, dot)),
            self.height_line.animate.set_opacity(0.0),
            self.backdrop.animate.set_opacity(0.0),
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.remove(rungs, driver, trail)
        self.wait(0.3)

    # ===================================================================== A6
    def act6_the_flip(self):
        # Cut the apparatus. Bring up the old belief.
        pre = Text("Things need a reason to", font=FONT_SERIF, font_size=34,
                   weight="LIGHT", color=STARLIGHT)
        move = Text("MOVE", font=FONT_SERIF, font_size=34, weight="SEMIBOLD",
                    color=STARLIGHT)
        line = VGroup(pre, move).arrange(RIGHT, buff=0.28).move_to(UP * 0.4)
        line.set_z_index(8)
        self.play(Write(pre), run_time=0.9)
        self.play(FadeIn(move, shift=UP * 0.08), run_time=0.5)
        self.wait(1.0)

        # Morph MOVE → STOP in place — watch the inversion happen.
        stop = Text("STOP", font=FONT_SERIF, font_size=34, weight="SEMIBOLD",
                    color=AMBER).move_to(move).set_z_index(8)
        self.play(TransformMatchingShapes(move, stop), run_time=1.1)
        self.wait(1.1)
        self.play(VGroup(pre, stop).animate.scale(0.8).move_to(UP * 2.6),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_sine)

        # Personify: two tiny side-by-side demos of the same stubbornness.
        gy = -1.4
        gL = Line([-6.0, gy, 0], [-0.6, gy, 0], color=GROUND, stroke_width=2.5,
                  stroke_opacity=0.7)
        gR = Line([0.6, gy, 0], [6.0, gy, 0], color=GROUND, stroke_width=2.5,
                  stroke_opacity=0.7)
        self.play(Create(gL), Create(gR), run_time=0.6)

        # LEFT — a resting ball gets a nudge and DIGS IN (refuses to budge).
        rest = make_ball(radius=0.22).move_to([-3.0, gy + 0.22, 0]).set_z_index(5)
        rest_sh = contact_shadow(0.22).move_to([-3.0, gy + 0.01, 0]).set_z_index(4)
        self.play(FadeIn(rest, scale=0.7), FadeIn(rest_sh), run_time=0.5)
        nudge = Arrow([-4.1, gy + 0.22, 0], [-3.35, gy + 0.22, 0], buff=0,
                      color=FORCE, stroke_width=5,
                      max_tip_length_to_length_ratio=0.32).set_z_index(6)
        self.play(GrowArrow(nudge), run_time=0.4)
        # it gives the tiniest twitch and settles right back
        self.play(rest.animate.shift(RIGHT * 0.07), run_time=0.18,
                  rate_func=rate_functions.ease_out_quad)
        self.play(rest.animate.shift(LEFT * 0.07), run_time=0.45,
                  rate_func=rate_functions.ease_out_elastic)
        self.play(FadeOut(nudge, shift=LEFT * 0.2), run_time=0.4)

        # RIGHT — a moving ball gets a "stop" tap and GLIDES RIGHT THROUGH IT.
        glide = make_ball(radius=0.22).move_to([0.9, gy + 0.22, 0]).set_z_index(5)
        glide_sh = contact_shadow(0.22).set_z_index(4)
        glide_sh.add_updater(lambda m: m.move_to([glide.get_center()[0],
                                                  gy + 0.01, 0]))
        v_arr = always_redraw(lambda: Arrow(
            glide.get_center() + RIGHT * 0.28,
            glide.get_center() + RIGHT * 0.78, buff=0, color=VEL,
            stroke_width=4, max_tip_length_to_length_ratio=0.4).set_z_index(6))
        self.add(glide_sh, v_arr)
        self.play(FadeIn(glide, scale=0.7), run_time=0.5)

        voice = Text("\u201cI'll keep doing what I'm doing.\u201d",
                     font=FONT_SERIF, font_size=20, slant=ITALIC, color=DUST)
        voice.move_to([2.9, gy + 1.1, 0]).set_z_index(7)

        tap = Arrow([4.6, gy + 0.22, 0], [3.9, gy + 0.22, 0], buff=0,
                    color=FORCE, stroke_width=5,
                    max_tip_length_to_length_ratio=0.32).set_z_index(6)
        # the ball just keeps going at constant speed — the tap does nothing
        self.play(
            glide.animate(rate_func=linear).move_to([5.4, gy + 0.22, 0]),
            FadeIn(voice, shift=UP * 0.08),
            Succession(Wait(0.7), GrowArrow(tap), Wait(0.2),
                       FadeOut(tap, scale=0.6)),
            run_time=2.4)
        glide_sh.clear_updaters()
        self.wait(0.5)

        # Land on a single word.
        self.play(
            FadeOut(VGroup(gL, gR, rest, rest_sh, glide, glide_sh, voice)),
            FadeOut(v_arr),
            VGroup(pre, stop).animate.set_opacity(0.0).shift(UP * 0.2),
            run_time=0.9, rate_func=rate_functions.ease_in_out_sine)
        self.remove(v_arr)

        lazy = Text("lazy", font=FONT_SERIF, font_size=72, weight="LIGHT",
                    slant=ITALIC, color=AMBER).move_to(ORIGIN).set_z_index(9)
        lazy_glow = lazy.copy().set_color(AMBER).set_opacity(0.0)
        self.play(Write(lazy), run_time=1.3)
        # one last lazy little settle
        self.play(lazy.animate.shift(DOWN * 0.06), run_time=0.5,
                  rate_func=rate_functions.ease_out_sine)
        self.play(lazy.animate.shift(UP * 0.06), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.0)

        # Optional forward-lean (cuttable — your handoff control).
        tease = Text("\u2026but is everything equally lazy?",
                     font=FONT_SERIF, font_size=24, slant=ITALIC, color=DUST)
        tease.move_to(DOWN * 1.9).set_z_index(8)
        self.play(FadeIn(tease, shift=UP * 0.1), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(1.6)

        self.play(FadeOut(VGroup(lazy, tease)), run_time=1.0)
        self.wait(0.5)
