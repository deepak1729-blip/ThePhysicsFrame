from manim import *
import numpy as np
import math

# ─────────────────────────────────────────────────────────────────────────
#  OBSERVATORY PALETTE  (verbatim from the series design system)
# ─────────────────────────────────────────────────────────────────────────
VOID      = "#0A0C10"   # base background
PANEL     = "#11151C"   # lifted surfaces
STARLIGHT = "#E8E6DF"   # primary text · the light itself
DUST      = "#9A958C"   # secondary · metadata · the dimmed (ghost) state
AMBER     = "#D98A3D"   # primary accent · focus  (amber follows the eye)
CYAN      = "#5B8FB0"   # secondary · sparing  (here: glass / lenses)

# quantity pigments — each keeps its colour across the whole series
C_ANGLE   = "#E08AAB"   # ANGLE θ — the swept wedge (resolution)
C_LEN     = "#5B8FB0"   # LENGTH / r  (== CYAN)
C_MASS    = "#B89A86"   # MATTER — warm organic tone (Jupiter here)
C_GROUND  = "#7F8A99"   # ground / reference axis

SERIF = "Spectral"      # ideas; italic is the channel's voice & every equation
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(3)      # deterministic -> stable render cache


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION VOCABULARY  (inlined per-file, matching Scenes 1–6 grammar)
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


def serif(s, color=STARLIGHT, size=44, italic=True, weight=NORMAL):
    """The channel's idea voice: Spectral, italic by default."""
    return Text(s, font=SERIF, slant=ITALIC if italic else NORMAL,
                weight=weight, font_size=size, color=color)


def mono(s, color=DUST, size=13, spacing=0.28):
    """Labels & metadata only — Space Mono."""
    t = Text(s, font=MONO, font_size=size, color=color)
    if spacing:
        t.set(width=t.width * (1 + spacing * 0.5))
    return t


def make_aperture(radius=0.34, color=AMBER, width=2.2):
    """THE circle — carried from Scene 1's beaker-mouth/pupil. Any
    light-catching opening in this series is this same plain circle."""
    return Circle(radius=radius, stroke_color=color, stroke_width=width,
                  fill_color=color, fill_opacity=0.10)


def biconvex(h=1.1, bulge=1.15, color=CYAN, width=2.4, fill_op=0.12):
    """A lens cross-section — identical builder to Scene 2's lentil/vesica."""
    top = np.array([0.0,  h / 2, 0.0])
    bot = np.array([0.0, -h / 2, 0.0])
    a = ArcBetweenPoints(top, bot, angle=bulge)     # right cheek
    b = ArcBetweenPoints(bot, top, angle=bulge)     # left cheek
    lens = VMobject()
    lens.set_points(np.vstack([a.get_points(), b.get_points()]))
    lens.set_stroke(color, width)
    lens.set_fill(color, fill_op)
    lens.h = h
    return lens


def soft_blob(radius=0.9, layers=7, color=STARLIGHT, seed=7):
    """Scene 1/2's poorly-resolved-star texture, reused verbatim — the Act-3
    re-blur deliberately IS the opening blur, not a lookalike."""
    rng = np.random.default_rng(seed)
    g = VGroup()
    for i in range(layers):
        frac = 1.0 - i / layers
        r = radius * frac * float(rng.uniform(0.9, 1.12))
        c = Circle(radius=r, stroke_width=0, fill_color=color,
                   fill_opacity=0.10 + 0.06 * (i / layers))
        c.shift(np.array([rng.uniform(-0.05, 0.05),
                          rng.uniform(-0.05, 0.05), 0]) * radius)
        g.add(c)
    return g


def soft_dot(center, r, color, opacity, halo=2.2, halo_op=0.35):
    """A dot with a breathing halo — reads as light, not as ink."""
    core = Circle(radius=r, stroke_width=0, fill_color=color,
                  fill_opacity=opacity).move_to(center)
    glow = Circle(radius=r * halo, stroke_width=0, fill_color=color,
                  fill_opacity=opacity * halo_op).move_to(center)
    return VGroup(glow, core)


def focal_crosshair(point, color=AMBER, r=0.10, arm=0.24):
    """NEW SERIES UNIT — the landmark wherever rays cross. Scenes 5 & 6
    reuse this exact mark; keep it visually identical there."""
    p = np.array([point[0], point[1], 0.0])
    ring = Circle(radius=r, stroke_color=color, stroke_width=2.0).move_to(p)
    h = Line(p + LEFT * arm, p + RIGHT * arm, stroke_color=color,
             stroke_width=1.5, stroke_opacity=0.9)
    v = Line(p + DOWN * arm, p + UP * arm, stroke_color=color,
             stroke_width=1.5, stroke_opacity=0.9)
    core = Dot(p, radius=0.035, color=color)
    return VGroup(h, v, ring, core)


# ═══════════════════════════════════════════════════════════════════════════
class Scene3_FunnelAndCatch(MovingCameraScene):
    """SCENE 3 — 'The Funnel and the Catch'. One lens funnels starlight to a
    focal point (Problem 1 from Scene 1: solved) — then the light overruns
    the point and re-spreads, re-creating the opening blur. A second lens,
    placed just past the focal point, catches the diverging cone and threads
    a narrowed parallel bundle straight into the pupil.

    THE BEAM IS ONE OBJECT. Every ray is a single polyline whose visible
    extent is a lone frontier tracker (`reach`) — light *travels* forward at
    constant speed (linear rate: physics honesty), overruns the focus in
    Act 3, is rewound in Act 4, and completes the path once the eyepiece
    lands. Acts 2→4 are literally the same rays; the viewer's eye never has
    to re-acquire the light."""

    # ── director toggles (each is a one-line flip) ────────────────────────
    SHOW_DOUBT_TEXT = True    # Act-1 quiet italic doubt under the lone lens
    SHOW_MM_LABELS  = True    # Act-2 comparison carries the 5 MM / 10 CM text
    COUNT_400       = True    # Act-2 literal 0→400 count-up during the pour
    REUSE_S1_BLUR   = True    # Act-3 blur = Scene 1/2 texture (False = fresh)
    CINCH_LITERAL   = False   # Act-4 drawstring: True = playful over-tighten,
                              # False = strict geometric snap + width pulse

    # ── locked optical geometry (thin lens — every act reads from these) ──
    X_IN   = -7.7             # rays enter from off-frame left
    L1X    = -3.3             # objective (funnel) plane
    A1     = 1.5              # objective half-aperture
    F1     = 3.7              # objective focal length
    F2     = 0.95             # eyepiece focal length
    FX     = L1X + F1         # focal point x  (= 0.4)
    L2X    = FX + F2          # eyepiece plane (= 1.35) — afocal, Keplerian
    K      = F2 / F1          # exit-bundle compression (≈ 0.26 — the narrowing)
    PUPIL_X   = 3.95
    PUPIL_R   = 0.42
    X_END     = 4.45          # frontier terminus — inside the eye
    X_DIV_MAX = 3.4           # how far the Act-3 overrun is allowed to spread
    EYE3_X    = 2.7           # the naive eye's position in the diverging cone

    HIT_YS   = list(np.linspace(-1.41, 1.41, 11))     # rays that meet glass
    WASTE_YS = [-3.5, -2.9, -2.35, -1.85, 1.85, 2.35, 2.9, 3.5]

    def construct(self):
        self.camera.frame.save_state()
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()

        self.wait(0.4)
        self.add(self.frame_marks)
        self.play(self.frame_marks.animate.set_opacity(0.5), run_time=0.8)

        self._build_beam()          # trackers + ray plumbing (nothing visible yet)

        self.act1_one_lens_isnt_enough()
        self.act2_the_funnel()
        self.act3_the_trap()
        self.act4_the_catch()
        self.act5_the_machine_assembled()

    # ── frame-mark plumbing (constant screen size under zoom) ─────────────
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

    # ═══════════════════════════════════════════════════════════════════
    #  THE BEAM — one frontier, one bundle, three acts
    # ═══════════════════════════════════════════════════════════════════
    def _build_beam(self):
        self.reach     = ValueTracker(self.X_IN)   # how far light has travelled
        self.beam_dim  = ValueTracker(1.0)         # global beam opacity
        self.pulse_on  = ValueTracker(0.0)         # flowing-light quanta gate
        self.w_pulse   = ValueTracker(0.0)         # Act-4 thread-the-pupil pulse
        self._cinch    = ValueTracker(1.0)         # exit-height factor (drawstring)
        self._lens2_on = False                     # flipped when the catch lands

        def lay(line, p, q, color, width, op):
            """Position a pre-built Line; hide it if degenerate."""
            if op <= 1e-3 or math.hypot(q[0] - p[0], q[1] - p[1]) < 1e-3:
                line.set_stroke(opacity=0.0)
                return
            line.put_start_and_end_on(np.array([p[0], p[1], 0.0]),
                                      np.array([q[0], q[1], 0.0]))
            line.set_stroke(color=color, width=width, opacity=op)

        # ── rays that meet the glass: three welded segments each ─────────
        self.hit_rays = VGroup()
        for y0 in self.HIT_YS:
            s1 = Line(ORIGIN, RIGHT * 0.01)   # parallel entry
            s2 = Line(ORIGIN, RIGHT * 0.01)   # converge → cross → diverge
            s3 = Line(ORIGIN, RIGHT * 0.01)   # re-collimated exit

            def u1(m, y0=y0):
                r, d = self.reach.get_value(), self.beam_dim.get_value()
                lay(m, (self.X_IN, y0), (min(r, self.L1X), y0),
                    STARLIGHT, 1.9, 0.75 * d)

            def u2(m, y0=y0):
                r, d = self.reach.get_value(), self.beam_dim.get_value()
                xe = min(r, self.L2X) if self._lens2_on else min(r, self.X_END)
                if xe <= self.L1X + 1e-3:
                    m.set_stroke(opacity=0.0)
                    return
                he = y0 * (1.0 - (xe - self.L1X) / self.F1)
                lay(m, (self.L1X, y0), (xe, he), STARLIGHT, 1.9, 0.9 * d)

            def u3(m, y0=y0):
                r, d = self.reach.get_value(), self.beam_dim.get_value()
                if (not self._lens2_on) or r <= self.L2X + 1e-3:
                    m.set_stroke(opacity=0.0)
                    return
                h2 = -y0 * self.K * self._cinch.get_value()
                wp = self.w_pulse.get_value()
                lay(m, (self.L2X, h2), (min(r, self.X_END), h2),
                    STARLIGHT, 1.9 + 1.3 * wp, min(1.0, 0.95 + 0.2 * wp) * d)

            s1.add_updater(u1); s2.add_updater(u2); s3.add_updater(u3)
            self.hit_rays.add(s1, s2, s3)
        self.hit_rays.set_z_index(3)

        # ── wasted-ray fade: the uncaught majority sails on, unbent ──────
        #    (the direct rhyme with Scene 1's spilled rain)
        self.waste_rays = VGroup()
        for y0 in self.WASTE_YS:
            wa = Line(ORIGIN, RIGHT * 0.01)   # bright approach
            wb = Line(ORIGIN, RIGHT * 0.01)   # dust-faded continuation

            def wfront(self=self):
                # nothing stops these rays — their frontier outruns the beam's
                return min(self.X_IN + (self.reach.get_value() - self.X_IN) * 1.5,
                           7.9)

            def ua(m, y0=y0):
                d = self.beam_dim.get_value()
                lay(m, (self.X_IN, y0), (min(wfront(), self.L1X), y0),
                    STARLIGHT, 1.5, 0.42 * d)

            def ub(m, y0=y0):
                d = self.beam_dim.get_value()
                r = wfront()
                if r <= self.L1X + 1e-3:
                    m.set_stroke(opacity=0.0)
                    return
                lay(m, (self.L1X, y0), (r, y0), DUST, 1.3, 0.15 * d)

            wa.add_updater(ua); wb.add_updater(ub)
            self.waste_rays.add(wa, wb)
        self.waste_rays.set_z_index(2)

        # ── the funnel body: a soft fill so the fan reads as ONE gesture ─
        def cone_maker():
            r, d = self.reach.get_value(), self.beam_dim.get_value()
            g = VGroup()
            y0 = float(max(self.HIT_YS))
            if r <= self.L1X + 0.03 or d <= 0.02:
                return g
            op = 0.05 * d

            def H(x):
                return y0 * (1.0 - (x - self.L1X) / self.F1)

            xa = min(r, self.FX)
            g.add(Polygon([self.L1X, y0, 0], [xa, H(xa), 0],
                          [xa, -H(xa), 0], [self.L1X, -y0, 0],
                          stroke_width=0, fill_color=STARLIGHT,
                          fill_opacity=op))
            if r > self.FX + 1e-3:                       # the un-funnel
                xb = min(r, self.L2X) if self._lens2_on else min(r, self.X_END)
                if xb > self.FX + 1e-3:
                    g.add(Polygon([self.FX, 0, 0], [xb, H(xb), 0],
                                  [xb, -H(xb), 0],
                                  stroke_width=0, fill_color=STARLIGHT,
                                  fill_opacity=op))
            if self._lens2_on and r > self.L2X + 1e-3:   # the caught bundle
                h2 = y0 * self.K * self._cinch.get_value()
                xc = min(r, self.X_END)
                g.add(Polygon([self.L2X, h2, 0], [xc, h2, 0],
                              [xc, -h2, 0], [self.L2X, -h2, 0],
                              stroke_width=0, fill_color=STARLIGHT,
                              fill_opacity=op * 1.4))
            return g
        self.cone = always_redraw(cone_maker)
        self.cone.set_z_index(1)

        # ── flowing light: one quantum per ray, constant speed forever ───
        n = len(self.HIT_YS)
        phases = RNG.uniform(0.0, 12.0, n)
        self.pulses = VGroup(*[Dot(radius=0.026, color=STARLIGHT,
                                   fill_opacity=0.0) for _ in range(n)])
        self.pulses.t = 0.0
        self.pulses.set_z_index(6)

        def height_at(x, y0):
            if x <= self.L1X:
                return y0
            if (not self._lens2_on) or x <= self.L2X:
                return y0 * (1.0 - (x - self.L1X) / self.F1)
            return -y0 * self.K * self._cinch.get_value()

        def pulse_update(grp, dt):
            grp.t += dt
            span = self.reach.get_value() - self.X_IN
            gate = self.pulse_on.get_value() * self.beam_dim.get_value()
            for i, dm in enumerate(grp):
                if span < 1.0 or gate <= 0.02:
                    dm.set_opacity(0.0)
                    continue
                x = self.X_IN + (phases[i] + 2.6 * grp.t) % span
                dm.move_to([x, height_at(x, self.HIT_YS[i]), 0.0])
                edge = min((x - self.X_IN) / 0.5,
                           (self.X_IN + span - x) / 0.35, 1.0)
                dm.set_opacity(0.85 * max(edge, 0.0) * gate)
        self.pulses.add_updater(pulse_update)

    # ═══════════════════════════════════════════════════════ ACT 1 ═══════
    def act1_one_lens_isnt_enough(self):
        """Sub-two-second recall of Scene 2's payoff — Moon, Jupiter, Venus —
        then a hard cut to the bare lens, stripped of tube and history, and a
        slow, slightly ominous push. Toy → pure geometry."""

        # HARD CUT — no transition. The toy is gone; only its glass remains.
        self.lens1 = biconvex(h=2 * self.A1 + 0.1, bulge=0.82, color=CYAN,
                              width=2.6, fill_op=0.10)
        self.lens1.move_to([self.L1X, 0, 0]).set_z_index(5)
        self.add(self.lens1)
        self.wait(0.5)

        # the patient, slightly ominous push — we're hunting for the crack
        push = [self.camera.frame.animate.scale(0.66)
                .move_to([self.L1X + 0.3, 0, 0])]
        self.play(*push, run_time=2.8,
                  rate_func=rate_functions.ease_in_out_sine)

        if self.SHOW_DOUBT_TEXT:
            doubt = serif("it worked, but why?", DUST, 26)
            doubt.move_to(self.camera.frame.get_center() + DOWN * 2.25)
            self.play(FadeIn(doubt, shift=UP * 0.08), run_time=0.9)
            self.wait(1.1)
            self.play(FadeOut(doubt), run_time=0.6)
        else:
            self.wait(1.2)

    # ═══════════════════════════════════════════════════════ ACT 2 ═══════
    def act2_the_funnel(self):
        """The ray-fan sweeps in at constant speed (linear — light doesn't
        ease). Missed rays sail past and fade to dust; caught rays bend and
        close into the funnel. Crosshair the crossing, then the to-scale
        pupil-vs-lens pour: 1 dot against 400."""
        self.play(self.camera.frame.animate.restore(), run_time=1.4,
                  rate_func=rate_functions.ease_in_out_sine)

        self.add(self.cone, self.waste_rays, self.hit_rays, self.pulses)

        # light propagates — linear because c is constant, not for style
        self.play(self.reach.animate.set_value(self.L1X), run_time=1.15,
                  rate_func=linear)
        self.play(self.reach.animate.set_value(self.FX + 0.02), run_time=1.0,
                  rate_func=linear)

        # the landmark: rays cross HERE (new series unit — reuse in 5 & 6)
        self.crosshair = focal_crosshair([self.FX, 0]).set_z_index(7)
        self.cross_lbl = mono("FOCAL POINT", AMBER, 18)
        self.cross_lbl.next_to(self.crosshair, DOWN, buff=0.75)
        self.play(GrowFromCenter(self.crosshair), run_time=0.6,
                  rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(self.cross_lbl, shift=UP * 0.08), run_time=0.5)

        # let the funnel breathe as one continuous gesture — light flowing
        self.play(self.pulse_on.animate.set_value(1.0), run_time=0.8)
        self.wait(1.4)

        self._scale_comparison()

    def _scale_comparison(self):
        """Face-on, drawn to true 20:1 scale: a 5 mm pupil beside a 10 cm
        lens. Rain the same density into both — the pupil catches ONE dot
        while the lens catches four hundred. The number arrives only after
        the density has already made the argument."""
        beam_extras = VGroup(self.crosshair, self.cross_lbl, self.lens1)
        self.play(self.beam_dim.animate.set_value(0.05),
                  beam_extras.animate.set_opacity(0.05),
                  rate_func=rate_functions.ease_in_out_sine)

        pupil_c = make_aperture(0.11, width=2.0).move_to([-3.6, 0.15, 0])
        lens_c = Circle(radius=2.2, stroke_color=CYAN, stroke_width=2.4,
                        fill_color=CYAN, fill_opacity=0.05).move_to([1.5, 0.15, 0])
        scale_tag = mono("DRAWN TO SCALE", DUST, 18).to_edge(UP, buff=0.5)
        self.play(GrowFromCenter(pupil_c), GrowFromCenter(lens_c),
                  FadeIn(scale_tag), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)

        labels = VGroup()
        if self.SHOW_MM_LABELS:
            plab = mono("YOUR PUPIL · 5 MM", DUST, 18)
            plab.next_to(pupil_c, DOWN, buff=0.5)
            llab = mono("A 10 CM LENS", DUST, 18)
            llab.next_to(lens_c, DOWN, buff=0.4)
            labels.add(plab, llab)
            self.play(FadeIn(plab), FadeIn(llab), run_time=0.6)

        # the pour — same photon density falling on both openings
        n_show = ValueTracker(0.0)
        drops = VGroup()
        for _ in range(400):
            u, th = RNG.uniform(0, 1), RNG.uniform(0, TAU)
            r = 2.2 * 0.93 * math.sqrt(u)
            drops.add(Dot(lens_c.get_center()
                          + np.array([r * math.cos(th), r * math.sin(th), 0]),
                          radius=0.022, color=STARLIGHT, fill_opacity=0.0))
        drops.set_z_index(6)

        def drops_reveal(grp):
            n = n_show.get_value()
            for i, dm in enumerate(grp):
                dm.set_opacity(0.85 if i < n else 0.0)
        drops.add_updater(drops_reveal)
        self.add(drops)

        one_dot = Dot(pupil_c.get_center(), radius=0.028,
                      color=STARLIGHT, fill_opacity=0.0).set_z_index(6)
        self.add(one_dot)

        counter = VGroup()
        if self.COUNT_400:
            cpos = lens_c.get_top() + UP * 0.45

            def make_count():
                return serif(f"{int(round(n_show.get_value()))}", AMBER, 40,
                             italic=False).move_to(cpos)
            counter = make_count()
            counter.add_updater(lambda m: m.become(make_count()))
            self.add(counter)

        # one photon lands in the pupil the instant the pour begins…
        self.play(one_dot.animate.set_opacity(0.95), run_time=0.4)
        # …and the lens drinks. (>>> POST: soft rising chime under this pour,
        # landing as the counter settles on 400.)
        self.play(n_show.animate.set_value(400), run_time=2.6,
                  rate_func=rate_functions.ease_out_cubic)
        if self.COUNT_400:
            counter.clear_updaters()
        drops.clear_updaters()
        one_tag = serif("1", AMBER, 40, italic=False)
        one_tag.move_to(pupil_c.get_top() + UP * 0.45)
        self.play(FadeIn(one_tag, scale=1.25), run_time=0.5)
        self.wait(0.5)

        verdict = serif("four hundred times more light.", STARLIGHT, 32)
        verdict.to_edge(DOWN, buff=0.9)
        self.play(Write(verdict), run_time=1.1)
        self.wait(1.4)   # Problem 1 — solved. Let it sit.

        # clear the interlude — but the pupil circle is NOT discarded: it
        # parks in the corner, dimmed, waiting to be threaded in Act 4.
        self.pupil_parked = pupil_c
        clearing = VGroup(lens_c, drops, one_dot, one_tag, verdict,
                          scale_tag, labels)
        if self.COUNT_400:
            clearing.add(counter)
        self.play(
            FadeOut(clearing),
            pupil_c.animate.move_to([self.PUPIL_X, 2.8, 0])
                   .set_stroke(opacity=0.35).set_fill(opacity=0.04),
            self.beam_dim.animate.set_value(1.0),
            beam_extras.animate.set_opacity(1.0),
            run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)

    # ═══════════════════════════════════════════════════════ ACT 3 ═══════
    def act3_the_trap(self):
        """Don't stop at the crosshair. The SAME rays keep travelling —
        through the focus, out the other side, un-funnelling into a mirrored
        cone. An eye parked in that cone gets Scene 1's blur back, texture
        and all. The rug, pulled gently."""
        # light does not stop for narrative — it overruns the focus, linear
        self.play(self.reach.animate.set_value(self.X_DIV_MAX), run_time=1.15,
                  rate_func=linear)
        self.wait(0.8)   # let the flip read: the funnel, undone

        # the naive move — put your eye right behind the focal point
        ball = Circle(radius=0.62, stroke_color=STARLIGHT, stroke_width=1.6,
                      stroke_opacity=0.6, fill_color=PANEL, fill_opacity=0.5)
        ball.move_to([self.EYE3_X + 0.44, 0, 0])
        eye_pupil = make_aperture(0.20, width=2.2)
        eye_pupil.move_to([self.EYE3_X - 0.12, 0, 0])
        eye3 = VGroup(ball, eye_pupil).set_z_index(7)
        self.play(FadeIn(eye3, shift=LEFT * 0.25), run_time=0.9,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        # a hopeful sharp point… racking out of focus into the opening blur.
        # (>>> POST: the small dissonant note lands as the blob overtakes.)
        point = Dot(ball.get_center(), radius=0.05, color=STARLIGHT,
                    fill_opacity=0.95).set_z_index(8)
        self.play(FadeIn(point, scale=0.4), run_time=0.5)
        self.wait(0.4)
        seed = 7 if self.REUSE_S1_BLUR else 11
        blob = soft_blob(0.52, color=STARLIGHT, seed=seed)
        blob.move_to(ball.get_center()).set_z_index(8)
        self.play(ReplacementTransform(point, blob), run_time=1.5,
                  rate_func=rate_functions.ease_in_out_sine)

        blur_lbl = mono("THE SAME BLUR", DUST, 18)     # Scene-2 echo, on purpose
        blur_lbl.next_to(eye3, DOWN, buff=0.75)
        self.play(FadeIn(blur_lbl, shift=UP * 0.08), run_time=0.6)
        self.wait(1.3)

        back = serif("right back where we started.", DUST, 26)
        back.to_edge(DOWN, buff=0.85)
        self.play(FadeIn(back), run_time=0.8)
        self.wait(1.2)

        self._act3_debris = VGroup(eye3, blob, blur_lbl, back)

    # ═══════════════════════════════════════════════════════ ACT 4 ═══════
    def act4_the_catch(self):
        """Rewind the overrun to the instant the cone has *just* started to
        re-spread. The eyepiece slides in exactly there; the rays snap back
        to parallel — visibly narrower than what entered — and thread the
        parked pupil circle. The crux frame; everything before it exists to
        earn this hold."""
        # rewind the mistake — pull the frontier back to just-past-focus
        self.play(FadeOut(self._act3_debris),
                  self.reach.animate.set_value(self.L2X + 0.02),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)

        # the pupil returns from its parking spot — the SAME circle from the
        # comparison, grown to the series' aperture, with an eye behind it
        pupil = make_aperture(self.PUPIL_R, width=2.6)
        pupil.move_to([self.PUPIL_X, 0, 0]).set_z_index(7)
        ball = Circle(radius=0.95, stroke_color=STARLIGHT, stroke_width=1.6,
                      stroke_opacity=0.45, fill_color=PANEL, fill_opacity=0.4)
        ball.move_to([self.PUPIL_X + 0.72, 0, 0]).set_z_index(6)
        self.play(FadeIn(ball),
                  ReplacementTransform(self.pupil_parked, pupil),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
        self.eye_final = VGroup(ball, pupil)
        self.wait(0.4)

        # the catch lens — one clean Keynote slide-in, no fuss
        self.lens2 = biconvex(h=1.35, bulge=1.5, color=CYAN, width=2.4,
                              fill_op=0.14)
        self.lens2.move_to([self.L2X, 3.6, 0]).set_z_index(5)
        self.add(self.lens2)
        self.play(self.lens2.animate.move_to([self.L2X, 0, 0]),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self._lens2_on = True                       # the geometry flips here
        self.play(Flash(Point([self.L2X, 0, 0]), color=CYAN,
                        line_length=0.12, num_lines=12, flash_radius=0.75),
                  run_time=0.4)

        # light completes the journey — bent parallel, narrowed, threaded
        anims = [self.reach.animate.set_value(self.X_END)]
        self.play(*anims, run_time=1.0, rate_func=linear)

        # the cinch. (>>> POST: the scene's one hero sound — a clean lock —
        # lands exactly on this flash. Nothing else competes with it.)
        if self.CINCH_LITERAL:
            self.play(self._cinch.animate.set_value(0.86), run_time=0.25,
                      rate_func=rate_functions.ease_in_sine)
            self.play(self._cinch.animate.set_value(1.0), run_time=0.35,
                      rate_func=rate_functions.ease_out_back)
        self.play(
            self.w_pulse.animate.set_value(1.0),
            Flash(Point([self.PUPIL_X, 0, 0]), color=AMBER, line_length=0.16,
                  num_lines=14, flash_radius=self.PUPIL_R + 0.28),
            run_time=0.55, rate_func=rate_functions.ease_out_cubic)
        self.play(self.w_pulse.animate.set_value(0.0), run_time=0.7,
                  rate_func=rate_functions.ease_in_out_sine)

        caught = mono("EVERY RAY ACCOUNTED FOR", AMBER, 18)
        caught.next_to(pupil, DOWN, buff=0.75)
        self.play(FadeIn(caught, shift=UP * 0.08), run_time=0.5)

        self.wait(2.7)   # ── THE HELD FRAME. Sit still. Nothing moves. ──
        self.play(FadeOut(caught), run_time=0.5)
        self._caught_lbl = caught

    # ═══════════════════════════════════════════════════════ ACT 5 ═══════
    def act5_the_machine_assembled(self):
        """Pull back; freeze the light; label the machine like a blueprint.
        This exact frame — funnel lens, crosshair, catch lens, eye — is the
        asset Scene 4 reopens with. Magic-move it back in there; don't rebuild."""
        # still the flowing quanta, then freeze the beam — near-silence
        self.play(self.pulse_on.animate.set_value(0.0), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)
        for grp in (self.hit_rays, self.waste_rays):
            for m in grp:
                m.clear_updaters()
        self.pulses.clear_updaters()
        self.cone.clear_updaters()

        self.play(self.camera.frame.animate.scale(1.1).move_to([0.25, 0, 0]),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)

        # blueprint labels on one quiet baseline, tied by faint leaders
        base_y = -2.35

        def label_with_leader(text, x, top_y):
            lbl = mono(text, DUST, 18).move_to([x, base_y, 0])
            leader = DashedLine([x, base_y + 0.28, 0], [x, top_y, 0],
                                dash_length=0.08, dashed_ratio=0.5,
                                stroke_color=DUST, stroke_width=1.0,
                                stroke_opacity=0.3)
            return VGroup(leader, lbl)

        lab_obj = label_with_leader("OBJECTIVE · THE FUNNEL",
                                    self.L1X, -self.A1 - 0.25)
        lab_eyp = label_with_leader("EYEPIECE · THE CATCH",
                                    self.L2X, -0.85)
        lab_eye = label_with_leader("EYE", self.PUPIL_X + 0.4, -1.15)
        labels = VGroup(lab_obj, lab_eyp, lab_eye)

        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.08) for l in labels],
                              lag_ratio=0.2, run_time=1.4),
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        # one light magic-move: everything settles a breath tighter — the
        # pieces built across three acts visibly become ONE machine
        machine = VGroup(self.cone, self.waste_rays, self.hit_rays,
                         self.lens1, self.lens2, self.crosshair,
                         self.cross_lbl, self.eye_final, labels)
        self.telescope_asset = machine          # <<< Scene 4 reopens with this
        self.play(machine.animate.scale(0.96, about_point=np.array([0.25, 0, 0])),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_sine)

        self.wait(2.4)   # near-silence. Scene 4 asks its question, not us.

        self.play(FadeOut(machine), FadeOut(self.pulses),
                  FadeOut(self.frame_marks),
                  run_time=2.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)