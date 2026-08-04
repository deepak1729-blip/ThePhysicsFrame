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
AMBER     = "#FFA540"   # focus — amber follows the eye
CYAN      = "#4DB4E0"   # series pigment for LENGTH / r — every radius here

C_LEN     = "#5B8FB0"
C_GROUND  = "#7F8A99"

SERIF = "Spectral"
MONO  = "Space Mono"

config.background_color = VOID
RNG     = np.random.default_rng(3)
SKY_RNG = np.random.default_rng(1729)   # Scene 1's seed — the SAME sky again


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
                weight=weight, font_size=size, color=color)


def mono(s, color=DUST, size=13, spacing=0.28):
    t = Text(s, font=MONO, font_size=size, color=color)
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


# ═══════════════════════════════════════════════════════════════════════════
class Scene3_TheLightThatHasntArrivedYet(MovingCameraScene):
    """SCENE 3 — the resolution.  Nothing new is invented here: the ray, the
    shells and the dome all return, and one added fact — light takes time,
    and time itself had a start — quietly reorganises everything the last
    two scenes built.  Holds are never frozen: some honest piece of the
    world (streaming light, breathing cells, a glint riding the boundary)
    keeps moving, softly, so the pause stays alive without performing."""

    # ── director toggles ──────────────────────────────────────────────────
    CURL_TIMELINE = True    # A2→A3 magic move (False = plain crossfade)
    VAST_FIELD    = True    # A4: genuinely vast ghost field vs modest hint
    CLOSING_TEXT  = True    # A5: closing line (False = sky + silence)
    RING_TIMES    = True    # A3: travel-time tags on the inner rings

    # ── locked geometry ───────────────────────────────────────────────────
    STAR_P   = np.array([-4.70, 0.90, 0.0])    # A1 star
    OBS_P    = np.array([4.70, 0.90, 0.0])     # A1 observer
    TL_Y     = -2.55        # the timeline IS Scene 1's horizon line
    TL_X     = 5.20         # today / beginning tick positions (±)
    R_BOUND  = 3.34         # how far light has come — one radius, every act
    RAD_A0   = 52.0         # angle of the time-radius before the sweep (°)
    STACK_R0 = 1.05         # Scene 2 Act 7's display radii, verbatim
    STACK_DR = 0.62
    N_IN     = 4            # shells inside the boundary (lit)
    N_ALL    = 7            # shells drawn in total (5–7 stay dark)
    DOME_CAM   = np.array([0.0, 1.60, 0.0])
    DOME_R_IN  = 0.55
    DOME_R_OUT = 5.20
    DOME_BANDS = 5          # band seam 3 sits exactly at R_BOUND
    DOME_COLS  = 28
    AGE_BY   = 13.8         # billions of years — the one real number

    # Scene 1's baseline-sky constants, verbatim
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

        self.act1_light_takes_time()
        self.act2_a_universe_with_a_birthday()
        self.act3_only_the_shells_light_has_reached()
        self.act4_not_missing_just_not_here_yet()
        self.act5_what_the_darkness_actually_tells_us()

    # ── plumbing ──────────────────────────────────────────────────────────
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
        """Scene 1's sampler, bit for bit — same seed, same draws, same sky."""
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

    def _make_ticker(self, anchor, unit, size=20, decimals=1):
        """The elapsed-time device: a live counter with a soft tick-blink.
        (>>> POST: a quiet, steady tick lives under this counter whenever
        it is running.)"""
        tr = ValueTracker(0.0)
        head = mono("ELAPSED", DUST, 14).move_to(anchor + UP * 0.34)
        val = mono(f"{0:.{decimals}f} {unit}", STARLIGHT, size)
        val.move_to(anchor)
        blink = Dot(ORIGIN, radius=0.035, fill_color=AMBER, fill_opacity=0.9)
        grp = VGroup(head, val, blink)
        grp.t_acc = 0.0

        def upd(g, dt):
            g.t_acc += dt
            v = tr.get_value()
            new = mono(f"{v:.{decimals}f} {unit}", STARLIGHT, size)
            new.move_to(anchor)
            g[1].become(new)
            g[2].next_to(g[1], LEFT, buff=0.22)
            g[2].set_fill(opacity=0.9 if (g.t_acc * 2.0) % 1.0 < 0.5
                          else 0.25)
        grp.add_updater(upd)
        return grp, tr

    # ═══════════════════════════════════════════════════════ ACT 1 ═══════
    def act1_light_takes_time(self):
        """One pulse, one trip, one counter.  The ray every diagram draws
        as already-there is rebuilt as the wake of something that had to
        TRAVEL — and the instant version is flashed once, then thrown away
        for the lie it is."""
        star = soft_dot(self.STAR_P, 0.09, STARLIGHT, 0.95)
        obs = soft_dot(self.OBS_P, 0.055, AMBER, 1.0)
        stag = mono("A STAR", DUST, 14).next_to(star, DOWN, buff=0.26)
        otag = mono("YOU", DUST, 14).next_to(obs, DOWN, buff=0.26)
        stag.set_opacity(0.55)
        otag.set_opacity(0.55)
        dist = mono("42 LIGHT-YEARS", DUST, 16)
        dist.move_to(0.5 * (self.STAR_P + self.OBS_P) + DOWN * 0.55)

        self.play(FadeIn(star, scale=0.6), FadeIn(obs, scale=0.6),
                  FadeIn(stag), FadeIn(otag), run_time=1.1,
                  rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(dist), run_time=0.6)

        ticker, tval = self._make_ticker(np.array([0.0, 3.05, 0.0]), "YR")
        self.add(ticker)
        self.play(FadeIn(ticker[0]), run_time=0.5)
        self.wait(0.6)

        # the trip itself — constant pace, real screen-time, no easing:
        # light does not accelerate for anyone's impatience
        prog = ValueTracker(0.0)
        start = self.STAR_P + RIGHT * 0.14
        end = self.OBS_P + LEFT * 0.10

        def pulse_pos():
            return start + (end - start) * prog.get_value()
        pulse = always_redraw(
            lambda: soft_dot(pulse_pos(), 0.05, STARLIGHT, 0.95,
                             halo=2.6, halo_op=0.4))
        trail = always_redraw(
            lambda: Line(start, pulse_pos(), stroke_color=STARLIGHT,
                         stroke_width=1.6, stroke_opacity=0.32))
        self.add(trail, pulse)
        self.play(prog.animate.set_value(1.0),
                  tval.animate.set_value(42.0),
                  run_time=5.6, rate_func=linear)

        ripple = Circle(radius=0.07, stroke_color=STARLIGHT,
                        stroke_width=2.0, stroke_opacity=0.6
                        ).move_to(self.OBS_P)
        self.add(ripple)
        self.play(ripple.animate.scale(7).set_stroke(opacity=0.0),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self.remove(ripple)
        self.wait(1.2)   # forty-two years, spent on screen in six seconds

        # freeze the real version; flash the instant lie
        self.remove(pulse, trail)
        real_trail = Line(start, end, stroke_color=STARLIGHT,
                          stroke_width=1.6, stroke_opacity=0.32)
        self.add(real_trail)
        self.play(real_trail.animate.set_stroke(opacity=0.10),
                  run_time=0.7, rate_func=rate_functions.ease_in_out_sine)

        tval.set_value(0.0)                       # the counter never moved
        iray = Line(start, end, stroke_color=DUST, stroke_width=2.2,
                    stroke_opacity=0.9)
        itag = mono("INSTANT", DUST, 15).move_to(
            0.5 * (start + end) + UP * 0.40)
        self.add(iray, itag)                      # one frame.  Zero duration.
        self.wait(1.3)
        self.play(FadeOut(iray, shift=DOWN * 0.35),
                  FadeOut(itag, shift=DOWN * 0.35),
                  run_time=0.7, rate_func=rate_functions.ease_in_sine)

        # the real, duration-filled version comes back — and stays alive:
        # after the first arrival, light KEEPS arriving
        tval.set_value(42.0)
        self.play(real_trail.animate.set_stroke(opacity=0.32), run_time=0.7)
        stream = VGroup(*[Dot(start, radius=0.028, fill_color=STARLIGHT,
                              fill_opacity=0.0) for _ in range(3)])
        stream.t_acc = 0.0

        def flow(grp, dt):
            grp.t_acc += dt
            for i, d in enumerate(grp):
                s = (grp.t_acc * 0.26 + i / 3.0) % 1.0
                d.move_to(start + (end - start) * s)
                d.set_fill(opacity=0.45 * smoothstep(min(s, 1 - s) * 7.0))
        stream.add_updater(flow)
        self.add(stream)
        self.wait(2.4)   # the hold breathes: the trip, repeating quietly

        stream.clear_updaters()
        ticker.clear_updaters()
        self.play(FadeOut(VGroup(star, obs, stag, otag, dist, real_trail,
                                 stream, ticker)),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)

    # ═══════════════════════════════════════════════════════ ACT 2 ═══════
    def act2_a_universe_with_a_birthday(self):
        """A timeline with a left edge.  The frame starts at genuinely
        zero, populates as time sweeps forward — into Scene 1's exact sky —
        and then the timeline itself turns into a radius and sweeps out the
        one circle the rest of the scene will live on."""
        tl = Line([-5.7, self.TL_Y, 0], [5.7, self.TL_Y, 0],
                  stroke_color=C_GROUND, stroke_width=1.6,
                  stroke_opacity=0.55)
        tick_b = Line([-self.TL_X, self.TL_Y - 0.14, 0],
                      [-self.TL_X, self.TL_Y + 0.14, 0],
                      stroke_color=DUST, stroke_width=1.6)
        tick_t = Line([self.TL_X, self.TL_Y - 0.14, 0],
                      [self.TL_X, self.TL_Y + 0.14, 0],
                      stroke_color=DUST, stroke_width=1.6)
        lab_b = mono("THE BEGINNING", DUST, 15).move_to(
            [-self.TL_X, self.TL_Y - 0.45, 0])
        lab_t = mono("TODAY", DUST, 15).move_to(
            [self.TL_X, self.TL_Y - 0.45, 0])
        observer = soft_dot([self.TL_X, self.TL_Y, 0], 0.055, AMBER, 1.0)

        self.play(Create(tl), run_time=1.1,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeIn(tick_b), FadeIn(lab_b), FadeIn(tick_t),
                  FadeIn(lab_t), FadeIn(observer, scale=0.5),
                  run_time=1.0, rate_func=rate_functions.ease_out_cubic)
        self.wait(1.2)   # above this line: nothing.  Not sparse — nothing.

        # the sweep: stars are BORN as the marker passes their birthdays,
        # sparse at first, denser toward today — ending on the exact sky
        # every scene so far has shown
        self._sample_baseline_sky()
        n = len(self.sky_pts)
        order = list(RNG.permutation(n))
        born = sorted(1.0 - (1.0 - (i + 1) / (n + 1)) ** 0.5
                      for i in range(n))
        births = [0.0] * n
        for rank, idx in enumerate(order):
            births[idx] = born[rank]

        sweep = ValueTracker(0.0)
        mist = ValueTracker(0.0)     # later: dims the sky to a ghost
        stars = VGroup(*[soft_dot(p, r, STARLIGHT, 0.0)
                         for p, r in zip(self.sky_pts, self.sky_radii)])
        stars.t_acc = 0.0

        def grow(grp, dt):
            grp.t_acc += dt
            s = sweep.get_value()
            dim = 1.0 - 0.88 * mist.get_value()
            for i, st in enumerate(grp):
                f = smoothstep((s - births[i]) / 0.05)
                sh = 0.86 + 0.14 * math.sin(self.sky_rate[i] * grp.t_acc
                                            + self.sky_phase[i])
                glow, core = st
                core.set_fill(opacity=self.sky_ops[i] * f * sh * dim)
                glow.set_fill(opacity=self.sky_ops[i] * 0.35 * f * sh * dim)
        stars.add_updater(grow)
        self.add(stars)

        cursor = Line([-self.TL_X, self.TL_Y + 0.06, 0],
                      [-self.TL_X, self.TL_Y + 0.40, 0],
                      stroke_color=STARLIGHT, stroke_width=2.0,
                      stroke_opacity=0.9)

        def ride(m):
            x = -self.TL_X + 2 * self.TL_X * sweep.get_value()
            m.put_start_and_end_on([x, self.TL_Y + 0.06, 0],
                                   [x, self.TL_Y + 0.40, 0])
        cursor.add_updater(ride)
        self.add(cursor)

        # (>>> POST: Act 1's tick returns here, attached to the sweep —
        #  the same sound meaning the same thing, one scale up.)
        self.play(sweep.animate.set_value(1.0), run_time=6.5,
                  rate_func=linear)
        self.wait(1.4)   # the sky, assembled.  Cursor resting on today.

        cursor.clear_updaters()
        if not self.CURL_TIMELINE:
            # fallback: plain crossfade to the boundary circle
            boundary = Circle(radius=self.R_BOUND, stroke_color=C_LEN,
                              stroke_width=2.2, stroke_opacity=0.9)
            obs2 = soft_dot(ORIGIN, 0.055, AMBER, 1.0)
            self.play(FadeOut(VGroup(tl, tick_b, tick_t, lab_b, lab_t,
                                     cursor, observer)),
                      mist.animate.set_value(1.0),
                      FadeIn(obs2), Create(boundary), run_time=2.0)
            self._boundary, self._observer = boundary, obs2
            self._stars2, self._mist = stars, mist
            return

        # the magic move: the time-axis becomes a radius.  TODAY comes to
        # rest on you; THE BEGINNING points away, as far as light has come.
        a0 = math.radians(self.RAD_A0)
        tip = self.R_BOUND * np.array([math.cos(a0), math.sin(a0), 0.0])
        radius = Line(ORIGIN, tip, stroke_color=C_LEN, stroke_width=2.2,
                      stroke_opacity=0.9)
        lab_t2 = mono("TODAY", DUST, 10).move_to(
            DOWN * 0.42 + LEFT * 0.10)
        lab_b2 = mono("THE BEGINNING", DUST, 10).move_to(tip * 1.16)
        self.play(
            mist.animate.set_value(1.0),
            Transform(tl, radius),
            observer.animate.move_to(ORIGIN),
            Transform(lab_t, lab_t2), Transform(lab_b, lab_b2),
            FadeOut(tick_b), FadeOut(tick_t), FadeOut(cursor),
            run_time=2.2, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.6)

        # …and sweeps.  Distance back in time IS distance out in space.
        ticker, tval = self._make_ticker(np.array([0.0, 3.42, 0.0]),
                                         "BILLION YR")
        self.add(ticker)
        ang = ValueTracker(0.0)

        def spin(m):
            a = a0 + ang.get_value()
            m.put_start_and_end_on(
                ORIGIN, self.R_BOUND * np.array([math.cos(a),
                                                 math.sin(a), 0.0]))
        tl.add_updater(spin)
        arc = always_redraw(lambda: Arc(
            radius=self.R_BOUND, start_angle=a0,
            angle=max(ang.get_value(), 1e-3), stroke_color=C_LEN,
            stroke_width=2.2, stroke_opacity=0.9))
        self.add(arc)
        self.play(ang.animate.set_value(TAU),
                  tval.animate.set_value(self.AGE_BY),
                  FadeOut(lab_b, run_time=0.8),
                  run_time=3.0, rate_func=rate_functions.ease_in_out_sine)
        tl.clear_updaters()

        boundary = Circle(radius=self.R_BOUND, stroke_color=C_LEN,
                          stroke_width=2.2, stroke_opacity=0.9)
        self.remove(arc)
        self.add(boundary)
        self.play(FadeOut(tl), FadeOut(lab_t), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)

        # the counter settles onto the circle it just measured
        ticker.clear_updaters()
        blabel = mono(f"{self.AGE_BY} BILLION YEARS", C_LEN, 11)
        blabel.move_to([0, self.R_BOUND + 0.30, 0])
        self.play(Transform(ticker, blabel), run_time=1.1,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)

        self._boundary, self._observer = boundary, observer
        self._stars2, self._mist = stars, mist
        self._blabel = ticker

    # ═══════════════════════════════════════════════════════ ACT 3 ═══════
    def act3_only_the_shells_light_has_reached(self):
        """Scene 2's stack again — but now the boundary is already standing
        in it.  A light-wave sweeps outward and simply stops where it must.
        Then the dome one more time, cascading — and halting — the same
        way.  The dark patch is not a failure of the argument.  It IS the
        argument."""
        # travel-time tags are schematic (display radii are compressed);
        # what is honest is the ORDER: farther ring, older light
        ring_years = ["2,000 YR", "8,000 YR", "50,000 YR", "1 MILLION YR"]

        rings, pts_shells, tags = VGroup(), [], VGroup()
        shell_units = []          # one (ring, extras) unit per shell, in order
        for k in range(1, self.N_ALL + 1):
            rk = self.STACK_R0 + (k - 1) * self.STACK_DR
            inside = rk < self.R_BOUND
            ring = Circle(radius=rk, stroke_color=C_LEN if inside else DUST,
                          stroke_width=1.8 if inside else 1.2,
                          stroke_opacity=0.45 if inside else 0.25)
            rings.add(ring)
            extras = []
            if inside:
                npts = 8 * k * k
                shell = VGroup()
                for j in range(npts):
                    a = TAU * j / npts + 0.10 + 0.07 * k
                    shell.add(Dot(rk * np.array([math.cos(a),
                                                 math.sin(a), 0]),
                                  radius=0.045 / (k ** 0.6),
                                  fill_color=STARLIGHT, fill_opacity=0.16))
                pts_shells.append((rk, k, shell))
                extras.append(shell)
                if self.RING_TIMES:
                    t = mono(ring_years[k - 1], DUST, 9)
                    aa = math.radians(112 + 9 * k)
                    t.move_to((rk + 0.22) * np.array([math.cos(aa),
                                                      math.sin(aa), 0]))
                    tags.add(t)
                    extras.append(t)
            else:
                dots = DashedVMobject(Circle(radius=rk),
                                      num_dashes=10 * k * k // 4,
                                      dashed_ratio=0.35)
                dots.set_stroke(color=DUST, width=1.3, opacity=0.22)
                rings.add(dots)
                extras.append(dots)
            shell_units.append((ring, extras))

        run_times = [0.85, 0.70, 0.58, 0.48, 0.42, 0.38, 0.35]
        for i, (ring, extras) in enumerate(shell_units):
            self.play(Create(ring),
                      *[FadeIn(e) for e in extras],
                      run_time=run_times[i],
                      rate_func=rate_functions.ease_out_cubic)
        self.wait(0.9)   # the stack that would not stop.  And its fence.

        # the wave: light, doing what it has been doing since the start —
        # and running out of time exactly at the line
        wr = ValueTracker(0.01)
        front = always_redraw(lambda: Circle(
            radius=max(wr.get_value(), 1e-3), stroke_color=STARLIGHT,
            stroke_width=2.6,
            stroke_opacity=0.38 * (1.0 - smoothstep(
                (wr.get_value() - self.R_BOUND + 0.12) / 0.12))))
        bright_targets = {1: 0.95, 2: 0.62, 3: 0.46, 4: 0.38}

        def shine(_grp, dt):
            w = wr.get_value()
            for rk, k, shell in pts_shells:
                f = smoothstep((w - rk) / 0.22)
                op = 0.16 + (bright_targets[k] - 0.16) * f
                for d in shell:
                    d.set_fill(opacity=op)
        carrier = VGroup()
        carrier.add_updater(shine)
        self.add(carrier, front)
        # (>>> POST: the tick keeps running under this sweep — and CUTS
        #  DEAD the instant the wave stops at the boundary.)
        self.play(wr.animate.set_value(self.R_BOUND), run_time=3.0,
                  rate_func=linear)
        self.play(self._boundary.animate.set_stroke(width=4.2),
                  run_time=0.25, rate_func=rate_functions.ease_out_cubic)
        self.play(self._boundary.animate.set_stroke(width=2.2),
                  run_time=0.45, rate_func=rate_functions.ease_in_out_sine)
        carrier.clear_updaters()
        self.remove(front, carrier)

        # the hold breathes: a glint rides the boundary; the lit shells
        # shimmer faintly.  The dark shells hold perfectly still.
        glint = Arc(radius=self.R_BOUND, start_angle=0.7, angle=0.45,
                    stroke_color=STARLIGHT, stroke_width=2.6,
                    stroke_opacity=0.55)
        glint.t_acc = 0.0

        def orbit(m, dt):
            m.t_acc += dt
            m.become(Arc(radius=self.R_BOUND,
                         start_angle=0.7 + 0.35 * m.t_acc, angle=0.45,
                         stroke_color=STARLIGHT, stroke_width=2.6,
                         stroke_opacity=0.55))
        glint.add_updater(orbit)
        shimmer = VGroup()
        shimmer.t_acc = 0.0

        def breathe(_g, dt):
            _g.t_acc += dt
            for rk, k, shell in pts_shells:
                for j, d in enumerate(shell):
                    b = bright_targets[k] * (
                        1.0 + 0.05 * math.sin(0.9 * _g.t_acc + j * 0.7 + k))
                    d.set_fill(opacity=b)
        shimmer.add_updater(breathe)
        self.add(glint, shimmer)
        self.wait(2.2)

        # → the dome, one more time.  The boundary rides along.
        glint.clear_updaters()
        shimmer.clear_updaters()
        self.remove(glint, shimmer)
        mesh, cells, meta = self._build_dome_mesh_cells()
        ground = Line([-7.2, 0, 0], [7.2, 0, 0], stroke_color=C_GROUND,
                      stroke_width=1.6, stroke_opacity=0.55)
        silhouette = Dot(ORIGIN, radius=0.06, fill_color=VOID,
                         fill_opacity=1.0).set_z_index(5)
        b_arc = Arc(radius=self.R_BOUND, start_angle=0, angle=PI,
                    stroke_color=C_LEN, stroke_width=2.2,
                    stroke_opacity=0.9)
        field = VGroup(rings, *[s for _, _, s in pts_shells], tags,
                       self._stars2)
        self._stars2.clear_updaters()
        self.add(cells)
        self.play(
            self.camera.frame.animate.move_to(self.DOME_CAM),
            FadeOut(field),
            FadeIn(mesh), Create(ground),
            ReplacementTransform(self._boundary, b_arc),
            self._blabel.animate.move_to([0, self.R_BOUND + 0.30, 0]),
            run_time=2.0, rate_func=rate_functions.ease_in_out_sine,
        )

        # the cascade — Scene 1's avalanche, but radial and mortal:
        # it lights exactly what light has had time to light
        adv = ValueTracker(0.0)
        lit = [k for k, (rm, tm) in enumerate(meta) if rm < self.R_BOUND]
        base_fire = {k: meta[k][0] / self.R_BOUND for k in lit}

        def cascade(_g):
            w = adv.get_value()
            for k in lit:
                f = smoothstep((w - base_fire[k]) / 0.10)
                cells[k].set_fill(opacity=0.92 * f)
        driver = VGroup()
        driver.add_updater(cascade)
        wave2 = always_redraw(lambda: Arc(
            radius=max(adv.get_value() * self.R_BOUND, 1e-3),
            start_angle=0, angle=PI, stroke_color=STARLIGHT,
            stroke_width=2.6,
            stroke_opacity=0.35 * (1.0 - smoothstep(
                (adv.get_value() - 0.95) / 0.05))))
        self.add(driver, wave2, silhouette)
        self.play(adv.animate.set_value(1.0), run_time=2.8,
                  rate_func=linear)
        # (>>> POST: tick out.  DEAD silence from here through the hold —
        #  the silence is the boundary, audible.)
        self.play(b_arc.animate.set_stroke(width=4.0), run_time=0.25,
                  rate_func=rate_functions.ease_out_cubic)
        self.play(b_arc.animate.set_stroke(width=2.2), run_time=0.45)
        driver.clear_updaters()
        self.remove(wave2, driver)

        # THE crux frame of the scene: a half-lit dome, held long.  The lit
        # cells breathe by a whisper; the dark cells do not move at all.
        breath = VGroup()
        breath.t_acc = 0.0

        def cell_breathe(_g, dt):
            _g.t_acc += dt
            for i, k in enumerate(lit):
                cells[k].set_fill(opacity=0.92 + 0.030 * math.sin(
                    0.7 * _g.t_acc + i * 0.45))
        breath.add_updater(cell_breathe)
        glint2 = Arc(radius=self.R_BOUND, start_angle=1.2, angle=0.35,
                     stroke_color=STARLIGHT, stroke_width=2.4,
                     stroke_opacity=0.5)
        glint2.t_acc = 0.0

        def orbit2(m, dt):
            m.t_acc += dt
            a = 1.2 + 0.22 * math.sin(0.5 * m.t_acc)   # sways, never leaves
            m.become(Arc(radius=self.R_BOUND, start_angle=a, angle=0.35,
                         stroke_color=STARLIGHT, stroke_width=2.4,
                         stroke_opacity=0.5))
        glint2.add_updater(orbit2)
        self.add(breath, glint2)
        self.wait(4.2)

        glint2.clear_updaters()
        breath.clear_updaters()
        self.remove(glint2, breath)
        self._dome_parts = VGroup(mesh, ground, silhouette, b_arc)
        self._cells, self._lit = cells, lit

    # ═══════════════════════════════════════════════════════ ACT 4 ═══════
    def act4_not_missing_just_not_here_yet(self):
        """Pull back to the God's-eye and let scale do the talking: a small
        solid bubble of the seen, adrift in an unbounded, ghost-outlined
        rest-of-everything that is slowly, indifferently turning."""
        # rebuild the lit field (fresh, final-state — cheaper than thawing)
        bright_targets = {1: 0.95, 2: 0.62, 3: 0.46, 4: 0.38}
        field = VGroup()
        for k in range(1, self.N_ALL + 1):
            rk = self.STACK_R0 + (k - 1) * self.STACK_DR
            inside = rk < self.R_BOUND
            field.add(Circle(radius=rk,
                             stroke_color=C_LEN if inside else DUST,
                             stroke_width=1.8 if inside else 1.2,
                             stroke_opacity=0.45 if inside else 0.22))
            if inside:
                npts = 8 * k * k
                for j in range(npts):
                    a = TAU * j / npts + 0.10 + 0.07 * k
                    field.add(Dot(rk * np.array([math.cos(a),
                                                 math.sin(a), 0]),
                                  radius=0.045 / (k ** 0.6),
                                  fill_color=STARLIGHT,
                                  fill_opacity=bright_targets[k]))
        boundary = Circle(radius=self.R_BOUND, stroke_color=C_LEN,
                          stroke_width=2.4, stroke_opacity=0.95)
        bglow = Circle(radius=self.R_BOUND, stroke_color=C_LEN,
                       stroke_width=9.0, stroke_opacity=0.16)
        observer = soft_dot(ORIGIN, 0.055, AMBER, 1.0)

        ghosts = VGroup()
        if self.VAST_FIELD:
            n_g = 640
            r_lo, r_hi = self.R_BOUND + 0.35, 11.5
            for _ in range(n_g):
                u = RNG.uniform(0, 1)
                rr = math.sqrt(u * (r_hi ** 2 - r_lo ** 2) + r_lo ** 2)
                a = RNG.uniform(0, TAU)
                ghosts.add(Dot([rr * math.cos(a), rr * math.sin(a), 0],
                               radius=float(RNG.uniform(0.008, 0.020)),
                               fill_color=STARLIGHT,
                               fill_opacity=float(RNG.uniform(0.05, 0.15))))
        ghosts.t_acc = 0.0

        def turn(g, dt):     # the rest of everything, slowly turning
            g.rotate(dt * 0.018, about_point=ORIGIN)
        ghosts.add_updater(turn)

        self.play(
            self.camera.frame.animate.move_to(ORIGIN).scale(1.45),
            FadeOut(self._dome_parts),
            FadeOut(self._cells), FadeOut(self._blabel),
            FadeIn(field), FadeIn(observer),
            FadeIn(bglow), FadeIn(boundary),
            run_time=2.2, rate_func=rate_functions.ease_in_out_sine,
        )
        self.play(FadeIn(ghosts), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        ptr_a = math.radians(38)
        p_in = (self.R_BOUND + 0.06) * np.array(
            [math.cos(ptr_a), math.sin(ptr_a), 0])
        p_out = (self.R_BOUND + 0.85) * np.array(
            [math.cos(ptr_a), math.sin(ptr_a), 0])
        ptr = Line(p_in, p_out, stroke_color=C_LEN, stroke_width=1.4,
                   stroke_opacity=0.8)
        see = mono("WHAT WE CAN SEE", C_LEN, 18).next_to(
            p_out, UR, buff=0.10)
        self.play(Create(ptr), FadeIn(see), run_time=0.9,
                  rate_func=rate_functions.ease_out_cubic)

        line = serif("not missing \u2014 just not here yet", STARLIGHT, 38)
        line.move_to([0, -4.35, 0])
        self.play(FadeIn(line, shift=UP * 0.15), run_time=1.2,
                  rate_func=rate_functions.ease_in_out_sine)

        # the hold IS a motion: a slow, continuous drift outward — the
        # bubble staying exactly the same size while the frame lets go
        self.play(self.camera.frame.animate.scale(1.09), run_time=4.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)

        ghosts.clear_updaters()
        self.play(FadeOut(VGroup(field, boundary, bglow, observer, ghosts,
                                 ptr, see, line)),
                  Restore(self.camera.frame),
                  run_time=1.8, rate_func=rate_functions.ease_in_out_sine)

    # ═══════════════════════════════════════════════════════ ACT 5 ═══════
    def act5_what_the_darkness_actually_tells_us(self):
        """Back to the first image of the series.  One quick hypothetical —
        a universe with no beginning floods the sky white, again — then a
        hard cut back to the real, dark, finite night.  The darkness is
        the evidence."""
        horizon = Line([-7.3, self._SKY_HORIZON, 0],
                       [7.3, self._SKY_HORIZON, 0],
                       stroke_color=C_GROUND, stroke_width=1.6,
                       stroke_opacity=0.55)
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
        self.add(stars)
        self.play(Create(horizon), veil.animate.set_value(1.0),
                  run_time=1.8, rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.2)

        # the hypothetical: no birthday, no boundary — no darkness
        hyp = mono("IF THERE WERE NO BEGINNING \u2014", DUST, 18)
        hyp.move_to([0, 3.30, 0])
        nb = Circle(radius=0.30, stroke_color=C_LEN, stroke_width=2.2,
                    stroke_opacity=0.9)
        cover = Rectangle(width=16, height=9.2, stroke_width=0,
                          fill_color=STARLIGHT, fill_opacity=0.0)
        cover.set_z_index(40)
        self.play(FadeIn(hyp), run_time=0.7)
        self.add(nb, cover)
        flood_rate = lambda t: smoothstep(max(0.0, (t - 0.45) / 0.55))
        self.play(nb.animate.scale(46).set_stroke(opacity=0.0),
                  cover.animate(rate_func=flood_rate).set_fill(opacity=1.0),
                  run_time=2.6, rate_func=rate_functions.ease_in_sine)
        self.wait(0.7)   # the whiteout — one last time, as a hypothetical

        self.remove(cover, nb, hyp)   # hard cut.  There WAS a beginning.
        self.wait(1.6)

        if self.CLOSING_TEXT:
            close = serif("the darkness has an age.", STARLIGHT, 40)
            close.move_to(UP * 1.35)
            # (>>> POST: a settled, resolved tone — calmer than anything in
            #  Scenes 1 or 2.  This is the answer landing, not tension.)
            self.play(FadeIn(close, shift=UP * 0.12), run_time=1.8,
                      rate_func=rate_functions.ease_in_out_sine)
        self.wait(4.0)   # only the stars move.  That is the whole point.

        stars.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects
                    if m is not self.frame_marks],
                  self.frame_marks.animate.set_opacity(0.0),
                  run_time=2.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

    # ── dome builder (Scene 1/2 grammar; band seam 3 == R_BOUND) ──────────
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