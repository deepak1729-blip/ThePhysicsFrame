from manim import *
import numpy as np
import math

# ─────────────────────────────────────────────────────────────────────────
#  OBSERVATORY PALETTE  (verbatim from the series design system)
# ─────────────────────────────────────────────────────────────────────────
VOID      = "#0A0C10"
PANEL     = "#11151C"
STARLIGHT = "#F7F6F1"
DUST      = "#C7C1B3"
AMBER     = "#FFA540"
CYAN      = "#4DB4E0"

C_LEN     = "#5B8FB0"
C_GROUND  = "#7F8A99"
C_RED     = "#E06450"   # the long end of what eyes can do

SERIF = "Spectral"
MONO  = "Space Mono"

MIN_FONT = 14

config.background_color = VOID
RNG     = np.random.default_rng(4)
SKY_RNG = np.random.default_rng(1729)   # Scene 1's seed — the same sky,
                                        # one last time

# ═══════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION VOCABULARY  (inlined per-file, series grammar)
# ═══════════════════════════════════════════════════════════════════════════
def corner_L(orientation, size=0.20, color=AMBER, width=1.4, opacity=0.7):
    sx = -1 if orientation[0] > 0 else 1
    sy = -1 if orientation[1] > 0 else 1
    h = Line(ORIGIN, RIGHT * size * sx, stroke_color=color,
             stroke_width=width, stroke_opacity=opacity)
    v = Line(ORIGIN, UP * size * sy, stroke_color=color,
             stroke_width=width, stroke_opacity=opacity)
    g = VGroup(h, v)
    g.anchor = orientation
    return g
 
 
def serif(s, color=STARLIGHT, size=44, italic=True, weight=NORMAL):
    return Text(s, font=SERIF, slant=ITALIC if italic else NORMAL,
                weight=weight, font_size=max(size, MIN_FONT), color=color)
 
 
def mono(s, color=DUST, size=MIN_FONT, spacing=0.28):
    t = Text(s, font=MONO, font_size=max(size, MIN_FONT), color=color)
    if spacing:
        t.set(width=t.width * (1 + spacing * 0.5))
    return t
 
 
def soft_dot(center, r, color, opacity, halo=2.2, halo_op=0.35):
    core = Circle(radius=r, stroke_width=0, fill_color=color,
                  fill_opacity=opacity).move_to(center)
    glow = Circle(radius=r * halo, stroke_width=0, fill_color=color,
                  fill_opacity=opacity * halo_op).move_to(center)
    return VGroup(glow, core)
 
 
def smoothstep(x):
    x = float(np.clip(x, 0.0, 1.0))
    return x * x * (3.0 - 2.0 * x)
 
 
def tile_frame(w=3.2, h=2.0):
    plate = RoundedRectangle(width=w, height=h, corner_radius=0.08,
                             stroke_color=DUST, stroke_width=1.4,
                             stroke_opacity=0.5, fill_color=PANEL,
                             fill_opacity=0.55)
    marks = VGroup()
    for o in (UL, UR, DL, DR):
        c = corner_L(o, size=0.16, color=AMBER, opacity=0.6)
        c.move_to(plate.get_corner(o), aligned_edge=o)
        marks.add(c)
    return VGroup(plate, marks)
 
 
def wave_color(g):
    """0 → starlight, 0.55 → amber, 1 → the red edge of visibility."""
    g = float(np.clip(g, 0.0, 1.0))
    if g < 0.55:
        return interpolate_color(ManimColor(STARLIGHT), ManimColor(AMBER),
                                 g / 0.55)
    return interpolate_color(ManimColor(AMBER), ManimColor(C_RED),
                             (g - 0.55) / 0.45)
 
 
# ═══════════════════════════════════════════════════════════════════════════
class Scene4_TheSkyIsStillGlowing(MovingCameraScene):
    """SCENE 4 — the twist that closes the series: Scene 1's 'impossible'
    bright sky was real all along.  Space stretches the light out of the
    narrow window eyes can read, the oldest light of all arrives as a
    microwave glow with no gaps in it, and the dome fills edge to edge one
    last time — true, current, and invisible.  Then back to the first
    frame of Scene 1, fully understood."""
 
    # ── director toggles ──────────────────────────────────────────────────
    VISIBLE_DIAL  = True    # A4: on-screen control (False = straight cut)
    OBS_BOOKEND   = True    # A5: the small observer returns on the horizon
    END_TAG       = False   # A5: channel sign-off line after the sky
 
    # ── locked geometry ───────────────────────────────────────────────────
    A1_AMAX  = 2.80          # Act 1 mesh expansion — big enough to SEE
    A1_SRC   = -2.00         # comoving coords chosen so the endpoints ride
    A1_OBS   = 1.75          # from mid-frame out to the edges as space grows
    A1_YC    = 0.40
    A1_LAM0  = 0.30          # emitted wavelength (display units)
    A3_AMAX  = 4.20          # Act 3 stretch — schematic (real ratio ≈ 1100)
    A3_SRC   = -1.85
    A3_OBS   = 1.19
    A3_LAM0  = 0.30
    STRIP_Y  = 0.80          # Act 2 spectrum strip
    STRIP_L  = -5.8
    STRIP_R  = 5.8
    VIS_END  = -3.40         # zone dividers: VISIBLE | INFRARED | MICROWAVE
    IR_END   = 0.40
    STRIP_H  = 1.05
    MARK_A   = -4.60         # marker start: centred in the VISIBLE box
    MARK_B   = 3.00          # marker end: centred in the MICROWAVE box
    MARK_L0  = 0.16          # marker wavelength law: exponential growth —
    MARK_LF  = 2.30          # each zone MULTIPLIES the wavelength (log-honest)
    DOME_CAM   = np.array([0.0, 1.60, 0.0])
    DOME_R_IN  = 0.55
    DOME_R_OUT = 5.20
    DOME_BANDS = 5
    DOME_COLS  = 28
    R_BOUND    = 3.34        # Scene 3's boundary, verbatim
    DIAL_C     = np.array([-4.60, -1.35, 0.0])
 
    _SKY_HORIZON = -2.55
    _SKY_N       = 26
    _SKY_SUN     = np.array([2.90, -2.05, 0.0])
    _SKY_FORCED  = np.array([-1.70, 1.35, 0.0])
 
    def construct(self):
        self.camera.frame.save_state()
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()
 
        self.wait(0.5)
        self.add(self.frame_marks)
        self.play(self.frame_marks.animate.set_opacity(0.5), run_time=0.8)
 
        self.act1_the_stretching_fabric()
        self.act2_out_of_sight()
        self.act3_the_oldest_light_of_all()
        self.act4_the_sky_is_still_glowing()
        self.act5_the_message_in_the_dark()
 
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
 
    def _sample_baseline_sky(self):
        pts, tries = [], 0
        forced = [self._SKY_FORCED.copy()]
        while len(pts) < self._SKY_N - len(forced) and tries < 4000:
            tries += 1
            p = np.array([SKY_RNG.uniform(-6.6, 6.6),
                          SKY_RNG.uniform(self._SKY_HORIZON + 0.55, 3.75),
                          0.0])
            if np.linalg.norm(p - self._SKY_SUN) < 0.9:
                continue
            if all(np.linalg.norm(p - q) > 0.62 for q in pts + forced):
                pts.append(p)
        pts = forced + pts
        self.sky_pts   = pts
        self.sky_radii = [0.045] + [float(SKY_RNG.uniform(0.016, 0.040))
                                    for _ in pts[1:]]
        self.sky_ops   = [0.95] + [float(SKY_RNG.uniform(0.45, 0.92))
                                   for _ in pts[1:]]
        self.sky_rate  = [float(SKY_RNG.uniform(1.1, 2.6)) for _ in pts]
        self.sky_phase = [float(SKY_RNG.uniform(0, TAU)) for _ in pts]
 
    # ── the honest wave engine ────────────────────────────────────────────
    def _make_stretch_wave(self, chi_s, chi_o, a_max, lam0, y_c, f_tr,
                           amp=0.27, n=240):
        """A wave in expanding space, done properly: crests live in comoving
        coordinates, and each segment's wavelength carries the stretch since
        ITS emission — so the leading edge (the oldest light) is visibly the
        most stretched, and the newest, at the source, barely at all."""
        k0 = TAU / lam0
 
        def a_of(t):
            return 1.0 + (a_max - 1.0) * float(np.clip(t, 0, 1))
 
        wave = VMobject(stroke_width=2.4)
 
        def rebuild(m):
            f = f_tr.get_value()
            a_now = a_of(f)
            us = np.linspace(0.0, 1.0, n)
            chi_tip = chi_s + (chi_o - chi_s) * f
            chi = chi_s + (chi_tip - chi_s) * us
            t_emit = f * (1.0 - us)               # tip left first
            stretch = a_now / np.array([a_of(t) for t in t_emit])
            x = chi * a_now
            dx = np.diff(x, prepend=x[0])
            theta = np.cumsum((k0 / stretch) * dx)
            taper = np.minimum(us * 22.0, 1.0)    # soft birth at the source
            y = y_c * a_now + amp * np.sin(theta) * taper
            pts = np.stack([x, y, np.zeros(n)], axis=1)
            m.set_points_as_corners(pts)
            g = (a_of(f) - 1.0) / (a_max - 1.0)
            m.set_stroke(color=wave_color(g),
                         opacity=0.9 if f > 0.002 else 0.0)
        wave.add_updater(rebuild)
        return wave, a_of
 
    # ═══════════════════════════════════════════════════════ ACT 1 ═══════
    def act1_the_stretching_fabric(self):
        """Space itself is the mesh; the wave's crests are pinned to it.
        As the mesh grows, the wave is pulled physically apart — not a
        metaphor, a mechanism."""
        a_tr = ValueTracker(0.0)      # shared clock: mesh AND wave read it
        base = []
        for gx in np.arange(-6.6, 6.61, 0.85):
            for gy in np.arange(-3.6, 3.61, 0.85):
                base.append(np.array([gx, gy, 0.0]))
        grid = VGroup(*[Dot(p, radius=0.014, fill_color=DUST,
                            fill_opacity=0.45) for p in base])
 
        def ride(g):
            a = 1.0 + (self.A1_AMAX - 1.0) * a_tr.get_value()
            for d, b in zip(g, base):
                d.move_to(b * a)
        grid.add_updater(ride)
 
        src_b = np.array([self.A1_SRC, self.A1_YC, 0.0])
        obs_b = np.array([self.A1_OBS, self.A1_YC, 0.0])
        src = soft_dot(src_b, 0.085, STARLIGHT, 0.95)
        obs = soft_dot(obs_b, 0.055, AMBER, 1.0)
 
        def ride_pt(m, b):
            a = 1.0 + (self.A1_AMAX - 1.0) * a_tr.get_value()
            m.move_to(b * a)
        src.add_updater(lambda m: ride_pt(m, src_b))
        obs.add_updater(lambda m: ride_pt(m, obs_b))
        stag = mono("A DISTANT STAR", DUST, 14).next_to(src, DOWN, buff=0.30)
        otag = mono("YOU", DUST, 14).next_to(obs, DOWN, buff=0.30)
        stag.set_opacity(0.55)
        otag.set_opacity(0.55)
 
        self.play(FadeIn(grid), run_time=1.4,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeIn(src, scale=0.6), FadeIn(obs, scale=0.6),
                  FadeIn(stag), FadeIn(otag),
                  run_time=1.0, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.6)
 
        wave, _ = self._make_stretch_wave(self.A1_SRC, self.A1_OBS,
                                          self.A1_AMAX, self.A1_LAM0,
                                          self.A1_YC, a_tr)
        self.add(wave)
        self.play(stag.animate.set_opacity(0.0),
                  otag.animate.set_opacity(0.0), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)
        # one tracker drives the mesh, the riding endpoints and the wave —
        # the sync is structural, not choreographed
        # (>>> POST: a low pitch runs under this trip and slides DOWNWARD
        #  in step with the stretch — the sound stretching with the light.)
        self.play(a_tr.animate.set_value(1.0), run_time=6.4,
                  rate_func=linear)
        self.wait(0.9)
 
        # the crux pair: what left, beside what arrived
        wave.clear_updaters()
        t1 = tile_frame(3.4, 1.9).move_to([-2.55, -2.35, 0])
        t2 = tile_frame(3.4, 1.9).move_to([2.55, -2.35, 0])
        lab1 = mono("AT DEPARTURE", DUST, 14).next_to(t1, DOWN, buff=0.24)
        lab2 = mono("AT ARRIVAL", DUST, 14).next_to(t2, DOWN, buff=0.24)
 
        def sample_wave(center, lam, color, ph_rate):
            w = VMobject(stroke_width=2.6)
            w.t_acc = 0.0
            w.veil = ValueTracker(0.0)
 
            def upd(m, dt):
                m.t_acc += dt
                xs = np.linspace(-1.25, 1.25, 160)
                ys = 0.42 * np.sin(TAU * xs / lam - ph_rate * m.t_acc)
                ys -= ys.mean()          # dead-centred in its frame
                pts = np.stack([xs + center[0], ys + center[1],
                                np.zeros(160)], axis=1)
                m.set_points_as_corners(pts)
                m.set_stroke(color=color, opacity=0.9 * m.veil.get_value())
            w.add_updater(upd)
            return w
        # the pair carries the trip's own on-screen ratio (x2.8): same wave
        # speed both sides, so crests pass 2.8x SLOWER on the right —
        # redshift is a slow-down too, countable in the two windows
        s1 = sample_wave(t1.get_center(), self.A1_LAM0, STARLIGHT, 4.6)
        s2 = sample_wave(t2.get_center(), self.A1_LAM0 * self.A1_AMAX,
                         C_RED, 4.6 / self.A1_AMAX)
        self.add(s1, s2)
        self.play(FadeIn(t1), FadeIn(t2), FadeIn(lab1), FadeIn(lab2),
                  s1.veil.animate.set_value(1.0),
                  s2.veil.animate.set_value(1.0),
                  run_time=1.1, rate_func=rate_functions.ease_out_cubic)
        self.wait(2.4)   # the waves keep waving — only their spacing differs
 
        s1.clear_updaters()
        s2.clear_updaters()
        grid.clear_updaters()
        src.clear_updaters()
        obs.clear_updaters()
        self.play(FadeOut(VGroup(grid, src, obs, stag, otag, wave,
                                 t1, t2, lab1, lab2, s1, s2)),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_sine)
 
    # ── the spectrum strip (built once, reused by Act 3) ──────────────────
    def _build_strip(self, y=None):
        y = self.STRIP_Y if y is None else y
        h = self.STRIP_H
        zones = [(self.STRIP_L, self.VIS_END, "VISIBLE", STARLIGHT),
                 (self.VIS_END, self.IR_END, "INFRARED", DUST),
                 (self.IR_END, self.STRIP_R, "MICROWAVE", DUST)]
        strip = VGroup()
        labels = VGroup()
        for x0, x1, name, col in zones:
            z = Rectangle(width=x1 - x0, height=h, stroke_color=DUST,
                          stroke_width=1.2, stroke_opacity=0.5,
                          fill_color=PANEL, fill_opacity=0.55)
            z.move_to([(x0 + x1) / 2, y, 0])
            lbl = mono(name, col, 15).move_to([(x0 + x1) / 2,
                                               y + h / 2 + 0.30, 0])
            strip.add(z)
            labels.add(lbl)
        return strip, labels
 
    def _make_marker(self, mpos, y=None):
        """A little living wave riding the strip.  Its wavelength grows
        EXPONENTIALLY along the map — visible light is a sliver, microwave
        is long and lazy — and by the far end it stretches out to fill its
        whole zone.  The drawn window is re-centred on its own mean every
        frame so it always sits exactly on the strip's centreline."""
        y = self.STRIP_Y if y is None else y
        ratio = self.MARK_LF / self.MARK_L0
        mk = VMobject(stroke_width=2.6)
        mk.t_acc = 0.0
 
        def upd(m, dt):
            m.t_acc += dt
            x0 = mpos.get_value()
            u = float(np.clip((x0 - self.MARK_A)
                              / (self.MARK_B - self.MARK_A), 0.0, 1.0))
            lam = self.MARK_L0 * ratio ** u
            hw = max(0.60, 1.15 * lam)
            hw = min(hw, 5.70 - x0, x0 + 5.70)     # stay inside the strip
            n = int(90 + 90 * hw)
            xs = np.linspace(-hw, hw, n)
            ys = 0.26 * np.sin(TAU * xs / lam - (3.4 / lam) * m.t_acc)
            ys -= ys.mean()
            pts = np.stack([xs + x0, ys + y, np.zeros(n)], axis=1)
            m.set_points_as_corners(pts)
            m.set_stroke(color=wave_color(u), opacity=0.95)
        mk.add_updater(upd)
        return mk
 
    def _make_eye(self, center):
        l, r = center + LEFT * 0.44, center + RIGHT * 0.44
        top = ArcBetweenPoints(l, r, angle=-1.05, stroke_color=STARLIGHT,
                               stroke_width=2.0, stroke_opacity=0.9)
        bot = ArcBetweenPoints(l, r, angle=1.05, stroke_color=STARLIGHT,
                               stroke_width=2.0, stroke_opacity=0.9)
        iris = Dot(center, radius=0.105, fill_color=AMBER, fill_opacity=0.9)
        pupil = Dot(center, radius=0.045, fill_color=VOID, fill_opacity=1.0)
        return VGroup(bot, iris, pupil, top)
 
    # ═══════════════════════════════════════════════════════ ACT 2 ═══════
    def act2_out_of_sight(self):
        """The same journey, measured against the narrow window eyes can
        read.  The light isn't destroyed and isn't blocked — the third
        false answer dies the way the first two did: it just slides off
        the map."""
        strip, labels = self._build_strip()
        eye = self._make_eye(np.array([-6.35, 2.55, 0.0]))
        etag = mono("HUMAN EYES", DUST, 14).next_to(eye, DOWN, buff=0.22)
        etag.set_opacity(0.6)
 
        self.play(LaggedStart(*[FadeIn(z, shift=UP * 0.1) for z in strip],
                              lag_ratio=0.12),
                  LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.12),
                  run_time=1.3, rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(eye), FadeIn(etag), run_time=0.8,
                  rate_func=rate_functions.ease_out_cubic)
 
        mpos = ValueTracker(self.MARK_A)
        marker = self._make_marker(mpos)
        self.add(marker)
        self.wait(0.9)   # the star's light, sitting where we can see it
 
        # slide to the visible/infrared line…
        self.play(mpos.animate.set_value(self.VIS_END - 0.05),
                  run_time=1.6, rate_func=rate_functions.ease_in_sine)
        # …and the instant it crosses, vision is over
        # (>>> POST: a soft shutter-click EXACTLY here — invisibility as a
        #  crossing, not a fade.)
        closed = ArcBetweenPoints(eye[3].get_start(), eye[3].get_end(),
                                  angle=1.05, stroke_color=STARLIGHT,
                                  stroke_width=2.0, stroke_opacity=0.9)
        self.play(Transform(eye[3], closed),
                  eye[1].animate.set_fill(opacity=0.12),
                  eye[2].animate.set_fill(opacity=0.12),
                  etag.animate.set_opacity(0.3),
                  run_time=0.4, rate_func=rate_functions.ease_in_sine)
        self.play(mpos.animate.set_value(self.MARK_B), run_time=2.8,
                  rate_func=rate_functions.ease_out_sine)
        self.wait(2.0)   # still real.  Still arriving.  Just off the map.
 
        marker.clear_updaters()
        self.play(FadeOut(VGroup(strip, labels, eye, etag, marker)),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)
 
    # ═══════════════════════════════════════════════════════ ACT 3 ═══════
    def act3_the_oldest_light_of_all(self):
        """The beginning of the timeline is not empty — it is a wall of
        light with no gaps.  The whiteout the paradox demanded really did
        happen once.  Its light has been traveling ever since, stretching
        the whole way — and it arrives today deep in the microwave, as a
        real, famous measurement."""
        tl = Line([-5.7, self._SKY_HORIZON, 0], [5.7, self._SKY_HORIZON, 0],
                  stroke_color=C_GROUND, stroke_width=1.6,
                  stroke_opacity=0.55)
        tick_b = Line([-5.2, self._SKY_HORIZON - 0.14, 0],
                      [-5.2, self._SKY_HORIZON + 0.14, 0],
                      stroke_color=DUST, stroke_width=1.6)
        tick_t = Line([5.2, self._SKY_HORIZON - 0.14, 0],
                      [5.2, self._SKY_HORIZON + 0.14, 0],
                      stroke_color=DUST, stroke_width=1.6)
        lab_b = mono("THE BEGINNING", DUST, 14).move_to(
            [-5.2, self._SKY_HORIZON - 0.45, 0])
        lab_t = mono("TODAY", DUST, 14).move_to(
            [5.2, self._SKY_HORIZON - 0.45, 0])
        self.play(Create(tl), FadeIn(tick_b), FadeIn(lab_b),
                  FadeIn(tick_t), FadeIn(lab_t),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)
 
        # the wall: everywhere, glowing, no structure and no gaps.
        # (>>> POST: the score is allowed ONE modest swell, and it starts
        #  under this wall and holds through the arrival on the strip.)
        wall = Rectangle(width=16, height=9.4, stroke_width=0,
                         fill_color=STARLIGHT, fill_opacity=0.0)
        mottle = VGroup()
        m_data = []
        for _ in range(9):
            c = np.array([RNG.uniform(-6, 6), RNG.uniform(-3, 3.4), 0.0])
            e = Ellipse(width=RNG.uniform(3.0, 5.5),
                        height=RNG.uniform(1.8, 3.4), stroke_width=0,
                        fill_color=VOID, fill_opacity=0.030).move_to(c)
            mottle.add(e)
            m_data.append((c, RNG.uniform(0, TAU),
                           RNG.uniform(0.04, 0.09)))
        mottle.t_acc = 0.0
 
        def drift(g, dt):     # the faintest unevenness, breathing slowly
            g.t_acc += dt
            for e, (c, ph, sp) in zip(g, m_data):
                e.move_to(c + np.array([math.cos(sp * g.t_acc + ph),
                                        math.sin(0.8 * sp * g.t_acc + ph),
                                        0.0]) * 0.35)
        mottle.add_updater(drift)
        wtag = mono("AT THE BEGINNING \u00b7 EVERYWHERE, GLOWING",
                    PANEL, 15).move_to([0, 3.30, 0]).set_opacity(0.0)
        self.add(wall, mottle, wtag)
        self.play(wall.animate.set_fill(opacity=0.92),
                  wtag.animate.set_opacity(0.85),
                  run_time=2.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait(2.6)   # the whiteout was real once.  Hold that.
 
        # the wall recedes to the beginning-edge, and its light sets out
        band = Rectangle(width=1.15, height=9.4, stroke_width=0,
                         fill_color=STARLIGHT, fill_opacity=0.55)
        band.move_to([-6.55, 0, 0])
        a_tr = ValueTracker(0.0)
        base = []
        for gx in np.arange(-6.6, 6.61, 0.55):
            for gy in np.arange(-3.3, 3.31, 0.55):
                base.append(np.array([gx, gy, 0.0]))
        grid = VGroup(*[Dot(p, radius=0.011, fill_color=DUST,
                            fill_opacity=0.0) for p in base])
 
        def ride(g):
            a = 1.0 + (self.A3_AMAX - 1.0) * a_tr.get_value()
            for d, b in zip(g, base):
                d.move_to(b * a)
        grid.add_updater(ride)
        self.add(grid)
        self.play(Transform(wall, band), FadeOut(wtag), FadeOut(mottle),
                  grid.animate.set_fill(opacity=0.35),
                  run_time=1.7, rate_func=rate_functions.ease_in_out_sine)
        mottle.clear_updaters()
 
        wave, _ = self._make_stretch_wave(self.A3_SRC, self.A3_OBS,
                                          self.A3_AMAX, self.A3_LAM0,
                                          0.42, a_tr, amp=0.30)
        arrive = soft_dot([self.A3_OBS * self.A3_AMAX, 0.42 * self.A3_AMAX,
                           0], 0.055, AMBER, 0.0)
        self.add(wave, arrive)
        # NOTE: the display stretch (×3.2) is schematic — the real number
        # is ≈ ×1100.  What is honest is the mechanism and the ORDER.
        self.play(a_tr.animate.set_value(1.0), run_time=5.4,
                  rate_func=linear)
        self.play(arrive[0].animate.set_fill(opacity=0.35),
                  arrive[1].animate.set_fill(opacity=1.0),
                  run_time=0.5, rate_func=rate_functions.ease_out_cubic)
 
        # …and lands on the strip: already deep in the microwave
        strip, labels = self._build_strip(y=2.85)
        mpos = ValueTracker(self.MARK_A)
        marker = self._make_marker(mpos, y=2.85)
        self.play(FadeIn(strip), FadeIn(labels), run_time=0.9,
                  rate_func=rate_functions.ease_out_cubic)
        self.add(marker)
        self.play(mpos.animate.set_value(self.MARK_B + 0.40), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(3.4)   # the oldest light there is, arriving right now —
                         # held unhurried, everything still quietly waving
 
        marker.clear_updaters()
        grid.clear_updaters()
        self.play(FadeOut(VGroup(strip, labels, marker, wave, arrive, grid,
                                 wall, tl, tick_b, tick_t, lab_b, lab_t)),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)
 
    # ═══════════════════════════════════════════════════════ ACT 4 ═══════
    def act4_the_sky_is_still_glowing(self):
        """Scene 3's half-lit dome, one dial-flip away from the truth: in
        the microwave, the whole sky — dark patch included — is softly,
        evenly glowing.  Every whiteout in the series was this picture,
        seen the only way it can actually be seen."""
        mesh, cells, meta = self._build_dome_mesh_cells()
        lit = [k for k, (rm, tm) in enumerate(meta) if rm < self.R_BOUND]
        for k in lit:
            cells[k].set_fill(opacity=0.92)
        ground = Line([-7.2, 0, 0], [7.2, 0, 0], stroke_color=C_GROUND,
                      stroke_width=1.6, stroke_opacity=0.55).set_z_index(5)
        silhouette = Dot(ORIGIN, radius=0.06, fill_color=VOID,
                         fill_opacity=1.0).set_z_index(5)
        b_arc = Arc(radius=self.R_BOUND, start_angle=0, angle=PI,
                    stroke_color=C_LEN, stroke_width=2.2,
                    stroke_opacity=0.9)
 
        self.play(
            self.camera.frame.animate.move_to(self.DOME_CAM),
            FadeIn(cells), FadeIn(mesh), FadeIn(ground),
            FadeIn(silhouette), FadeIn(b_arc),
            run_time=1.8, rate_func=rate_functions.ease_in_out_sine,
        )
        breath = VGroup()
        breath.t_acc = 0.0
 
        def cell_breathe(_g, dt):
            _g.t_acc += dt
            for i, k in enumerate(lit):
                cells[k].set_fill(opacity=0.92 + 0.030 * math.sin(
                    0.7 * _g.t_acc + i * 0.45))
        breath.add_updater(cell_breathe)
        self.add(breath)
        self.wait(1.4)   # the real sky, real dark patch and all
 
        dial = None
        knob_from = knob_to = None
        if self.VISIBLE_DIAL:
            pill = RoundedRectangle(width=2.0, height=0.5,
                                    corner_radius=0.25, stroke_color=DUST,
                                    stroke_width=1.4, stroke_opacity=0.7,
                                    fill_color=PANEL, fill_opacity=0.9)
            pill.move_to(self.DIAL_C)
            knob_from = self.DIAL_C + LEFT * 0.62
            knob_to = self.DIAL_C + RIGHT * 0.62
            knob = Dot(knob_from, radius=0.155, fill_color=AMBER,
                       fill_opacity=1.0)
            lab_v = mono("VISIBLE", STARLIGHT, 14).next_to(
                pill, LEFT, buff=0.30)
            lab_m = mono("MICROWAVE", DUST, 14).next_to(
                pill, RIGHT, buff=0.30)
            dial = VGroup(pill, knob, lab_v, lab_m)
            self.play(FadeIn(dial, shift=UP * 0.15), run_time=0.9,
                      rate_func=rate_functions.ease_out_cubic)
            self.wait(0.7)
 
        # the flip.
        # (>>> POST: whatever has been building CRESTS exactly on this
        #  flip — then near-silence through the glow: Scene 1 Act 5's
        #  silence again, but as awe this time, not wrongness.)
        glow = AnnularSector(inner_radius=0.0, outer_radius=self.DOME_R_OUT,
                             angle=PI, start_angle=0, fill_color=STARLIGHT,
                             fill_opacity=0.0, stroke_width=0)
        g_mottle = VGroup()
        g_data = []
        for _ in range(7):
            aa = RNG.uniform(0.25, PI - 0.25)
            rr = RNG.uniform(1.4, 4.4)
            c = rr * np.array([math.cos(aa), math.sin(aa), 0.0])
            e = Ellipse(width=RNG.uniform(1.6, 3.0),
                        height=RNG.uniform(0.9, 1.8), stroke_width=0,
                        fill_color=VOID, fill_opacity=0.0).move_to(c)
            g_mottle.add(e)
            g_data.append((c, RNG.uniform(0, TAU), RNG.uniform(0.05, 0.10)))
        g_mottle.t_acc = 0.0
 
        def g_drift(g, dt):
            g.t_acc += dt
            for e, (c, ph, sp) in zip(g, g_data):
                e.move_to(c + np.array([math.cos(sp * g.t_acc + ph),
                                        math.sin(0.7 * sp * g.t_acc + ph),
                                        0.0]) * 0.28)
        g_mottle.add_updater(g_drift)
        self.add(glow, g_mottle)
 
        flip = []
        if self.VISIBLE_DIAL:
            flip = [dial[1].animate.move_to(knob_to),
                    dial[2].animate.set_color(DUST),
                    dial[3].animate.set_color(STARLIGHT)]
        if flip:
            self.play(*flip, run_time=0.9,
                      rate_func=rate_functions.ease_in_out_sine)
        breath.clear_updaters()
        self.remove(breath)
        self.play(glow.animate.set_fill(opacity=0.82),
                  g_mottle.animate.set_fill(opacity=0.035),
                  b_arc.animate.set_stroke(opacity=0.0),
                  mesh.animate.set_stroke(opacity=0.0),
                  run_time=2.4, rate_func=rate_functions.ease_in_out_sine)
        self.remove(cells, b_arc, mesh)
        self.wait(4.6)   # no gaps.  Anywhere.  Right now, above everyone.
 
        self._glow, self._g_mottle = glow, g_mottle
        self._ground, self._silhouette = ground, silhouette
        self._dial, self._knob_from = dial, knob_from
 
    # ═══════════════════════════════════════════════════════ ACT 5 ═══════
    def act5_the_message_in_the_dark(self):
        """Dial back to the eyes we actually have.  The glow lifts, the
        first frame of Scene 1 returns — same stars, same horizon — and
        four scenes of argument settle into one quiet, ordinary, fully
        understood picture of the night."""
        back = []
        if self.VISIBLE_DIAL and self._dial is not None:
            back = [self._dial[1].animate.move_to(self._knob_from),
                    self._dial[2].animate.set_color(STARLIGHT),
                    self._dial[3].animate.set_color(DUST)]
        if back:
            self.play(*back, run_time=0.9,
                      rate_func=rate_functions.ease_in_out_sine)
 
        self._sample_baseline_sky()
        horizon = Line([-7.3, self._SKY_HORIZON, 0],
                       [7.3, self._SKY_HORIZON, 0],
                       stroke_color=C_GROUND, stroke_width=1.6,
                       stroke_opacity=0.0)
        stars = VGroup(*[soft_dot(p, r, STARLIGHT, op)
                         for p, r, op in zip(self.sky_pts, self.sky_radii,
                                             self.sky_ops)])
        stars.t_acc = 0.0
        veil = ValueTracker(0.0)
        stars.veil = veil
 
        def twinkle(grp, dt):
            grp.t_acc += dt
            g = veil.get_value()
            for i, star in enumerate(grp):
                f = 0.80 + 0.20 * math.sin(self.sky_rate[i] * grp.t_acc
                                           + self.sky_phase[i])
                glow, core = star
                core.set_fill(opacity=self.sky_ops[i] * f * g)
                glow.set_fill(opacity=self.sky_ops[i] * 0.35 * f * g)
        stars.add_updater(twinkle)
        self.add(stars, horizon)
 
        self._g_mottle.clear_updaters()
        fades = [FadeOut(self._glow), FadeOut(self._g_mottle),
                 FadeOut(self._silhouette)]
        if self._dial is not None:
            fades.append(FadeOut(self._dial))
        # (>>> POST: a slow fade to silence lives under this pull-back —
        #  nothing competes with the image from here on.)
        fades.append(FadeOut(self._ground))
        self.play(
            *fades,
            horizon.animate.set_stroke(opacity=0.55),
            veil.animate.set_value(1.0),
            Restore(self.camera.frame),
            run_time=3.2, rate_func=rate_functions.ease_in_out_sine,
        )
 
        if self.OBS_BOOKEND:
            watcher = soft_dot([2.40, self._SKY_HORIZON, 0], 0.045,
                               AMBER, 0.0)
            self.add(watcher)
            self.play(watcher[0].animate.set_fill(opacity=0.30),
                      watcher[1].animate.set_fill(opacity=0.85),
                      run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
 
        self.wait(4.6)   # the first image of the series, understood.
 
        if self.END_TAG:
            tag = mono("THE PHYSICS FRAME", DUST, 14).move_to([0, -3.35, 0])
            self.play(FadeIn(tag), run_time=1.0)
            self.wait(2.0)
 
        stars.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects
                    if m is not self.frame_marks],
                  self.frame_marks.animate.set_opacity(0.0),
                  run_time=3.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)
 
    # ── dome builder (Scene 1/2/3 grammar) ────────────────────────────────
    def _build_dome_mesh_cells(self):
        r_in, r_out = self.DOME_R_IN, self.DOME_R_OUT
        bands, cols = self.DOME_BANDS, self.DOME_COLS
        b_edges = np.linspace(r_in, r_out, bands + 1)
        c_edges = np.linspace(0, PI, cols + 1)
        mesh = VGroup()
        for r in b_edges:
            mesh.add(Arc(radius=r, start_angle=0, angle=PI,
                         stroke_color=DUST, stroke_width=0.8,
                         stroke_opacity=0.22))
        for th in c_edges:
            dv = np.array([math.cos(th), math.sin(th), 0.0])
            mesh.add(Line(dv * r_in, dv * r_out, stroke_color=DUST,
                          stroke_width=0.8, stroke_opacity=0.22))
        cells, meta = VGroup(), []
        for i in range(bands):
            for j in range(cols):
                cells.add(AnnularSector(
                    inner_radius=b_edges[i], outer_radius=b_edges[i + 1],
                    angle=c_edges[j + 1] - c_edges[j],
                    start_angle=c_edges[j], fill_color=STARLIGHT,
                    fill_opacity=0.0, stroke_width=0))
                meta.append((0.5 * (b_edges[i] + b_edges[i + 1]),
                             0.5 * (c_edges[j] + c_edges[j + 1])))
        return mesh, cells, meta