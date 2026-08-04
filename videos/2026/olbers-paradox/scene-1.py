from manim import *
import numpy as np
import math

# ─────────────────────────────────────────────────────────────────────────
#  OBSERVATORY PALETTE  (verbatim from the series design system)
# ─────────────────────────────────────────────────────────────────────────
VOID      = "#0A0C10"   # base background
PANEL     = "#11151C"   # lifted surfaces
STARLIGHT = "#F7F6F1"   # primary text · the light itself
DUST      = "#C7C1B3"   # secondary · metadata · the dimmed (ghost) state
AMBER     = "#FFA540"   # primary accent · focus  (amber follows the eye)
CYAN      = "#4DB4E0"   # secondary · sparing  (here: the rare cool star)

# quantity pigments — each keeps its colour across the whole series
C_GROUND  = "#7F8A99"   # ground / reference axis

SERIF = "Spectral"      # ideas; italic is the channel's voice & every equation
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(1729)   # deterministic -> stable render cache


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION VOCABULARY  (inlined per-file, matching the telescope grammar)
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


def safe_image(name, target_width, fallback_label):
    """Load an image by name; if it isn't present yet, return a framed
    placeholder slot so the script always runs as-is."""
    try:
        img = ImageMobject(name)
        img.set(width=target_width)
        return img
    except Exception:
        h = target_width * 0.62
        slot = VGroup()
        plate = Rectangle(width=target_width, height=h,
                          fill_color=PANEL, fill_opacity=1.0,
                          stroke_color=DUST, stroke_width=1.2,
                          stroke_opacity=0.4)
        lbl = Text(fallback_label, font=MONO, font_size=14, color=DUST)
        lbl.move_to(plate.get_center())
        slot.add(plate, lbl)
        for o in (UL, UR, DL, DR):
            c = corner_L(o, size=0.14, color=AMBER, opacity=0.55)
            c.move_to(plate.get_corner(o), aligned_edge=o)
            slot.add(c)
        return slot


def serif(s, color=STARLIGHT, size=44, italic=True, weight=NORMAL):
    """The channel's idea voice: Spectral, italic by default."""
    return Text(s, font=SERIF, slant=ITALIC if italic else NORMAL,
                weight=weight, font_size=size, color=color)


def mono(s, color=DUST, size=13, spacing=0.28):
    """Labels & metadata only — Space Mono, letter-spaced small caps feel."""
    t = Text(s, font=MONO, font_size=size, color=color)
    if spacing:
        t.set(width=t.width * (1 + spacing * 0.5))     # gentle tracking
    return t


def soft_dot(center, r, color, opacity, halo=2.2, halo_op=0.35):
    """A dot with a breathing halo — reads as light, not as ink."""
    core = Circle(radius=r, stroke_width=0, fill_color=color,
                  fill_opacity=opacity).move_to(center)
    glow = Circle(radius=r * halo, stroke_width=0, fill_color=color,
                  fill_opacity=opacity * halo_op).move_to(center)
    return VGroup(glow, core)


def smoothstep(x):
    x = float(np.clip(x, 0.0, 1.0))
    return x * x * (3.0 - 2.0 * x)


# ═══════════════════════════════════════════════════════════════════════════
class Scene1_TheImpossibleSky(MovingCameraScene):
    """SCENE 1 — the paradox engine.  Take the answer everyone carries
    ("night is dark because the sun is gone"), dismantle it geometrically,
    and end staring at a sky that should be blindingly bright and isn't.
    Plants the series' two seed images: the single traced sightline, and the
    observer at the centre of a radially growing field (Scene 2's shell)."""

    # ── director toggles (each is a one-line flip) ────────────────────────
    LABEL_SUN         = True    # A1: tiny mono "SUN" tag that dies with the dot
    USE_DEEP_FIELD    = True    # A2: real deep-field photograph gut-punch
    USE_REAL_SKY_BEAT = False   # A5: 1 s real night-sky flash against whiteout
    KEPLER_FOOTNOTE   = True    # A6: one-line historical footnote, name only
    HARD_CUT_TO_REAL  = True    # A5 -> A6: hard cut (False = slow cross-fade)
    GHOST_GRID        = True    # A6: A5's mesh lingers at near-zero opacity

    # ── locked geometry (every act reads from these) ──────────────────────
    HORIZON_Y   = -2.55
    N_SKY       = 26                               # a calm real eye's worth
    SUN_PT      = np.array([ 2.90, -2.05, 0.0])    # low, near the horizon
    SUN_R       = 0.09                            # the plain amber disc
    ZOOM_STAR   = np.array([-1.70,  1.35, 0.0])    # A2's chosen star
    SHRINK      = 0.16          # world-scale factor per zoom-out repetition
    RING_R0     = 0.72          # A3 first shell radius
    RING_DR     = 0.52
    N_RINGS     = 10
    RING_DENS   = 2.1           # points per unit of ring arc (constant density)
    SEED_RINGS  = (2, 5)        # the two shells that quietly hold longer
    SKY_CAM     = np.array([0.0, 2.05, 0.0])       # A4 first-person framing
    RAY_DIRS    = [68, 35, 96, 118, 52, 145]       # degrees, first is the crux
    RAY_DISTS   = [5.15, 3.30, 4.55, 3.90, 2.85, 3.55]
    DOME_CAM    = np.array([0.0, 1.60, 0.0])       # A5 dome framing
    DOME_R_IN   = 0.55
    DOME_R_OUT  = 5.20
    DOME_BANDS  = 5
    DOME_COLS   = 28

    def construct(self):
        self.camera.frame.save_state()
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()

        self.wait(0.5)
        self.add(self.frame_marks)
        self.play(self.frame_marks.animate.set_opacity(0.5), run_time=0.8)

        self.act1_the_answer_you_already_have()
        self.act2_zooming_out_past_safe()
        self.act3_observer_at_the_center_of_forever()
        self.act4_one_line_traced_all_the_way_out()
        self.act5_every_point_full_of_light()
        self.act6_a_name_for_the_wrongness()

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

    # ── the baseline sky, buildable twice (A1 opens on it, A6 returns) ────
    def _sample_baseline_sky(self):
        """One deterministic draw, stored, so Act 6 can restore the EXACT
        same sky — the comparison only lands if nothing has changed."""
        pts, tries = [], 0
        forced = [self.ZOOM_STAR.copy()]           # A2's target must exist
        while len(pts) < self.N_SKY - len(forced) and tries < 4000:
            tries += 1
            p = np.array([RNG.uniform(-6.6, 6.6),
                          RNG.uniform(self.HORIZON_Y + 0.55, 3.75), 0.0])
            if np.linalg.norm(p - self.SUN_PT) < 0.9:
                continue                            # keep the sun's corner calm
            if all(np.linalg.norm(p - q) > 0.62 for q in pts + forced):
                pts.append(p)
        pts = forced + pts
        self.sky_pts   = pts
        self.sky_radii = [0.045] + [float(RNG.uniform(0.016, 0.040))
                                    for _ in pts[1:]]
        self.sky_ops   = [0.95] + [float(RNG.uniform(0.45, 0.92))
                                   for _ in pts[1:]]
        self.sky_rate  = [float(RNG.uniform(1.1, 2.6)) for _ in pts]
        self.sky_phase = [float(RNG.uniform(0, TAU)) for _ in pts]

    def _build_baseline_sky(self):
        """Horizon + the same modest stars, with a live scintillation updater.
        (The telescope scenes' stars were static; a breathing sky is this
        episode's first visible level-up, and it costs almost nothing.)"""
        horizon = Line([-7.3, self.HORIZON_Y, 0], [7.3, self.HORIZON_Y, 0],
                       stroke_color=C_GROUND, stroke_width=1.6,
                       stroke_opacity=0.55)
        stars = VGroup(*[soft_dot(p, r, STARLIGHT, op)
                         for p, r, op in zip(self.sky_pts, self.sky_radii,
                                             self.sky_ops)])
        stars.time = 0.0
        # transitions animate THIS tracker — never fight the updater directly
        veil = ValueTracker(1.0)
        stars.veil = veil

        def twinkle(grp, dt):
            grp.time += dt
            g = veil.get_value()
            for i, star in enumerate(grp):
                f = 0.80 + 0.20 * math.sin(self.sky_rate[i] * grp.time
                                           + self.sky_phase[i])
                glow, core = star
                core.set_fill(opacity=self.sky_ops[i] * f * g)
                glow.set_fill(opacity=self.sky_ops[i] * 0.35 * f * g)
        stars.add_updater(twinkle)
        return horizon, stars

    # ═══════════════════════════════════════════════════════ ACT 1 ═══════
    def act1_the_answer_you_already_have(self):
        """The plainest possible frame: a horizon, a calm handful of stars.
        The sun-dot blinks out with no ceremony — the question answering
        itself before it is asked — then the camera creeps in like a held
        breath.  This exact frame is the yardstick every later act is
        measured against."""
        self._sample_baseline_sky()
        horizon, stars = self._build_baseline_sky()
        self._horizon, self._stars = horizon, stars

        self.play(Create(horizon), run_time=1.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.add(stars)
        stars.veil.set_value(0.0)
        self.play(stars.veil.animate.set_value(1.0), run_time=1.8,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.7)

        # the sun — same plain disc grammar Act 4's terminal star will echo
        sun = soft_dot(self.SUN_PT, self.SUN_R, AMBER, 0.95)
        sun_grp = VGroup(sun)
        if self.LABEL_SUN:
            tag = mono("SUN", DUST, 14)
            tag.next_to(sun, DOWN + RIGHT * 0.4, buff=0.14)
            sun_grp.add(tag)
        self.play(FadeIn(sun, scale=0.6),
                  *([FadeIn(sun_grp[1])] if self.LABEL_SUN else []),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self.wait(1.5)

        # no ceremony: a clean snap-out.  The joke is the absence itself.
        self.play(FadeOut(sun_grp), run_time=0.15, rate_func=linear)
        self.remove(sun_grp)
        self.wait(1.3)   # hold the baseline — the "obviously" beat

        # the held breath: a creep so slow it registers as unease, not motion
        # (>>> POST: room tone only; the first hint of score starts UNDER
        #  this creep, almost inaudible.)
        self.play(self.camera.frame.animate.scale(0.955), run_time=5.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)

    # ═══════════════════════════════════════════════════════ ACT 2 ═══════
    def act2_zooming_out_past_safe(self):
        """One star becomes a galaxy becomes a point among galaxies — three
        times, each faster, until counting fails and the frame reads as a
        mist of light.  Shot 1 is a true camera move; repetitions 2–3 scale
        the WORLD instead, so the zoom compounds without precision limits."""
        target = self.ZOOM_STAR
        frame  = self.camera.frame

        # dive toward the chosen star; the rest of the sky slips away behind us
        others = VGroup(self._horizon,
                        *[s for s in self._stars[1:]])
        self._stars.clear_updaters()
        kept = self._stars[0]                       # the star we dive into
        self.play(
            frame.animate.scale(0.10).move_to(target),
            FadeOut(others),
            run_time=3.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.remove(self._stars)
        self.add(kept)

        # ...and it resolves into a loose cluster — a galaxy — around it
        gal = VGroup()
        for _ in range(90):
            p = target + np.array([RNG.normal(0, 0.30),
                                   RNG.normal(0, 0.22), 0.0])
            r = float(RNG.uniform(0.004, 0.012))
            col = CYAN if RNG.uniform() < 0.06 else STARLIGHT
            gal.add(Dot(p, radius=r, fill_color=col,
                        fill_opacity=float(RNG.uniform(0.4, 0.95))))
        self.play(
            LaggedStart(*[FadeIn(d, scale=0.4) for d in gal],
                        lag_ratio=0.012),
            frame.animate.scale(0.80),
            run_time=1.5, rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(0.8)   # "oh — it was never alone"

        # zoom-out 1 (camera): the galaxy shrinks back to a point... among dozens
        # (>>> POST: the sub-audible pitch-rise begins here and keeps building
        #  through all three repetitions — the third must FEEL different.)
        field = VGroup(kept, gal)
        peers = VGroup()
        for _ in range(44):
            p = np.array([RNG.uniform(-6.8, 6.8), RNG.uniform(-3.8, 3.8), 0.0])
            if np.linalg.norm(p - target) < 1.3:
                continue
            r = float(RNG.uniform(0.020, 0.050))
            peers.add(Dot(p, radius=r, fill_color=STARLIGHT,
                          fill_opacity=float(RNG.uniform(0.35, 0.9))))
        self.play(
            Restore(frame),
            field.animate.scale(0.28, about_point=target),
            LaggedStart(*[FadeIn(d, scale=0.4) for d in peers],
                        lag_ratio=0.02),
            run_time=2.6, rate_func=rate_functions.ease_in_out_sine,
        )
        field.add(*peers)
        self.wait(0.7)

        # zoom-out 2 (world): the same move, compounding — faster
        more = VGroup()
        for _ in range(130):
            p = np.array([RNG.uniform(-7.0, 7.0), RNG.uniform(-3.95, 3.95), 0])
            more.add(Dot(p, radius=float(RNG.uniform(0.012, 0.034)),
                         fill_color=STARLIGHT,
                         fill_opacity=float(RNG.uniform(0.3, 0.85))))
        self.play(
            field.animate.scale(self.SHRINK, about_point=ORIGIN),
            LaggedStart(*[FadeIn(d, scale=0.5) for d in more],
                        lag_ratio=0.006),
            run_time=1.6, rate_func=rate_functions.ease_in_out_sine,
        )
        field.add(*more)
        self.wait(0.35)

        # zoom-out 3: stop resolving.  The frame simply runs out of room.
        mist = VGroup()
        for _ in range(430):
            p = np.array([RNG.uniform(-7.1, 7.1), RNG.uniform(-4.0, 4.0), 0])
            mist.add(Dot(p, radius=float(RNG.uniform(0.006, 0.020)),
                         fill_color=STARLIGHT,
                         fill_opacity=float(RNG.uniform(0.22, 0.7))))
        fine = VGroup()
        for _ in range(240):
            p = np.array([RNG.uniform(-7.1, 7.1), RNG.uniform(-4.0, 4.0), 0])
            fine.add(Dot(p, radius=float(RNG.uniform(0.004, 0.010)),
                         fill_color=STARLIGHT,
                         fill_opacity=float(RNG.uniform(0.15, 0.45))))
        self.play(
            field.animate.scale(self.SHRINK, about_point=ORIGIN),
            LaggedStart(*[FadeIn(d, scale=0.6) for d in mist],
                        lag_ratio=0.0015),
            run_time=1.0, rate_func=rate_functions.ease_in_sine,
        )
        self.play(LaggedStart(*[FadeIn(d) for d in fine], lag_ratio=0.001),
                  run_time=0.7, rate_func=rate_functions.ease_in_sine)
        field.add(*mist, *fine)
        # every dot entered the scene as its own top-level mobject (FadeIn on
        # the individual dots).  Hand them all to `field` and register only
        # `field`, so a later FadeOut(field) actually removes them — otherwise
        # the group fades, is "removed" (it was never in self.mobjects), and
        # the loose dots pop straight back the next frame.
        self.remove(*field.submobjects)
        self.add(field)
        self._field = field
        self.wait(2.2)   # let the density genuinely overwhelm the canvas

        # the gut-punch: this is not an animation trick.  A real photograph.
        if self.USE_DEEP_FIELD:
            photo = safe_image("Cosmic_Microwave_Background_(CMB).jpeg", 15.0,
                               "DEEP FIELD PHOTOGRAPH")
            photo.set_z_index(20)
            
            self.play(FadeIn(photo), run_time=0.9,
                      rate_func=rate_functions.ease_in_out_sine)

            self.wait(2.6)
            self.play(FadeOut(photo), run_time=0.8,
                      rate_func=rate_functions.ease_in_out_sine)
            self.wait(0.3)

    # ═══════════════════════════════════════════════════════ ACT 3 ═══════
    def act3_observer_at_the_center_of_forever(self):
        """God's-eye reset: one point — you — with the universe redrawn as
        rings of constant density growing outward.  Two rings quietly hold a
        beat longer than the rest: the shell, planted, unnamed, for Scene 2
        to pick up and give a number."""
        self.play(FadeOut(self._field), run_time=0.7,
                  rate_func=rate_functions.ease_in_sine)
        self.remove(self._field)   # belt-and-braces: the field never returns
        self.wait(0.3)

        observer = soft_dot(ORIGIN, 0.055, AMBER, 1.0)
        you = mono("YOU", DUST, 14).next_to(observer, DOWN, buff=0.20)
        self.play(FadeIn(observer, scale=0.5), run_time=0.8,
                  rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(you), run_time=0.5)
        self.wait(0.5)

        # rays of Act 4, known in advance, keep clean corridors through the
        # field — the first sightline must visibly travel through GAPS
        dirs = [np.array([math.cos(math.radians(a)),
                          math.sin(math.radians(a)), 0.0])
                for a in self.RAY_DIRS]

        def in_corridor(p):
            for d, dist in zip(dirs, self.RAY_DISTS):
                t = float(np.dot(p, d))
                if 0.3 < t < dist + 0.4:
                    if np.linalg.norm(p - t * d) < 0.16:
                        return True
            return False

        rings, ring_pts = VGroup(), []
        for k in range(self.N_RINGS):
            r = self.RING_R0 + k * self.RING_DR
            n = max(6, int(TAU * r * self.RING_DENS))
            ring = VGroup()
            for j in range(n):
                th = TAU * j / n + RNG.uniform(-0.4, 0.4) / max(r, 1)
                rr = r + RNG.uniform(-0.09, 0.09)
                p = np.array([rr * math.cos(th), rr * math.sin(th), 0.0])
                if in_corridor(p):
                    continue
                ring.add(Dot(p, radius=float(RNG.uniform(0.016, 0.034)),
                             fill_color=STARLIGHT,
                             fill_opacity=float(RNG.uniform(0.4, 0.9))))
            rings.add(ring)
            ring_pts.append(r)

        ghosts = VGroup()
        for k, ring in enumerate(rings):
            self.play(LaggedStart(*[FadeIn(d, scale=0.45) for d in ring],
                                  lag_ratio=0.012),
                      run_time=0.55 if k < 6 else 0.42,
                      rate_func=rate_functions.ease_out_cubic)
            if k in self.SEED_RINGS:
                # the seed: a faint circle surfaces, holds, and almost
                # entirely lets go — Scene 2 will give this a name
                shell = Circle(radius=ring_pts[k], stroke_color=DUST,
                               stroke_width=1.0, stroke_opacity=0.0)
                self.add(shell)
                self.play(shell.animate.set_stroke(opacity=0.30),
                          run_time=0.35)
                self.wait(0.55)
                self.play(shell.animate.set_stroke(opacity=0.06),
                          run_time=0.5)
                ghosts.add(shell)
        self.wait(1.1)   # "distance radiates away from me in every direction"

        self._observer, self._you = observer, you
        self._rings, self._ghosts = rings, ghosts

    # ═══════════════════════════════════════════════════════ ACT 4 ═══════
    def act4_one_line_traced_all_the_way_out(self):
        """First-person again: the field above the observer reads as sky.
        One thin ray travels outward at constant speed — linear on purpose;
        light does not ease — through gap after gap, until its tip stops
        exactly on the rim of a star's disc.  Then the pattern: every
        direction, eventually, hits something."""
        dirs = [np.array([math.cos(math.radians(a)),
                          math.sin(math.radians(a)), 0.0])
                for a in self.RAY_DIRS]

        # terminal stars slip in during the reframe — plain discs, and the
        # first one wears Act 1's exact sun grammar: someone else's sun.
        radii = [self.SUN_R, 0.058, 0.052, 0.062, 0.050, 0.056]
        terms = VGroup()
        for i, (d, dist, r) in enumerate(zip(dirs, self.RAY_DISTS, radii)):
            c = d * dist
            col = AMBER if i == 0 else STARLIGHT
            op  = 0.95 if i == 0 else 0.8
            terms.add(soft_dot(c, r, col, op))
        below = VGroup(*[dot for ring in self._rings for dot in ring
                         if dot.get_center()[1] < 0.25])
        self.play(
            self.camera.frame.animate.move_to(self.SKY_CAM).scale(0.92),
            below.animate.set_opacity(0.10),
            self._you.animate.set_opacity(0.35),
            FadeIn(terms),
            run_time=2.2, rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.6)

        def make_ray(direction, dist, disc_r, glow_w=5.0, core_w=1.8):
            hit = direction * (dist - disc_r)       # the rim, exactly
            span = float(np.linalg.norm(hit) - 0.14)
            prog = ValueTracker(0.0)
            glow = Line(ORIGIN, RIGHT, stroke_color=STARLIGHT,
                        stroke_width=glow_w, stroke_opacity=0.16)
            core = Line(ORIGIN, RIGHT, stroke_color=STARLIGHT,
                        stroke_width=core_w, stroke_opacity=0.95)
            ray = VGroup(glow, core)
            ray.prog = prog

            def follow(grp):
                t = prog.get_value()
                a = direction * 0.14
                b = direction * (0.14 + max(span * t, 1e-3))
                for seg in grp:
                    seg.put_start_and_end_on(a, b)
            ray.add_updater(follow)
            return ray, prog, hit

        # THE ray.  Constant speed — the physics demands linear here.
        ray0, prog0, hit0 = make_ray(dirs[0], self.RAY_DISTS[0], radii[0])
        self.add(ray0)
        self.play(prog0.animate.set_value(1.0), run_time=3.4,
                  rate_func=linear)
        ray0.clear_updaters()
        # (>>> POST: one soft low tone, EXACTLY on this landing.
        #  Nothing before it, nothing after it.)
        pulse = Circle(radius=0.04, stroke_color=AMBER, stroke_width=2.0,
                       stroke_opacity=0.6).move_to(hit0)
        self.add(pulse)
        self.play(pulse.animate.scale(11).set_stroke(opacity=0.0),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self.remove(pulse)
        self.wait(2.6)   # crux frame — hold the landed sightline in silence

        # the pattern, faster: four more directions, four more surfaces
        rays, anims = [ray0], []
        for d, dist, r in list(zip(dirs, self.RAY_DISTS, radii))[1:5]:
            ray, prog, _hit = make_ray(d, dist, r, glow_w=3.6, core_w=1.3)
            self.add(ray)
            rays.append(ray)
            anims.append(prog.animate(run_time=0.7,
                                      rate_func=linear).set_value(1.0))
        self.play(LaggedStart(*anims, lag_ratio=0.35))
        for ray in rays:
            ray.clear_updaters()
        self.wait(1.5)   # every line, eventually, connects to something

        self._rays, self._terms = VGroup(*rays), terms

    # ═══════════════════════════════════════════════════════ ACT 5 ═══════
    def act5_every_point_full_of_light(self):
        """The whole visible sky, meshed into cells over a dome.  A few cells
        demonstrate the ray-and-landing; then the cascade — popcorn, not
        sunrise — accelerating until no dark cell remains.  Then the hold:
        a uniformly bright dome, sitting there, wrong."""
        r_in, r_out = self.DOME_R_IN, self.DOME_R_OUT
        bands, cols = self.DOME_BANDS, self.DOME_COLS
        b_edges = np.linspace(r_in, r_out, bands + 1)
        c_edges = np.linspace(0, PI, cols + 1)

        mesh = VGroup()
        for r in b_edges:
            mesh.add(Arc(radius=r, start_angle=0, angle=PI,
                         stroke_color=DUST, stroke_width=0.8,
                         stroke_opacity=0.30))
        for th in c_edges:
            d = np.array([math.cos(th), math.sin(th), 0.0])
            mesh.add(Line(d * r_in, d * r_out, stroke_color=DUST,
                          stroke_width=0.8, stroke_opacity=0.30))

        ground = Line([-7.2, 0, 0], [7.2, 0, 0], stroke_color=C_GROUND,
                      stroke_width=1.6, stroke_opacity=0.55)

        # pull back; the field becomes a dome with a mesh laid over it
        fade_dots = VGroup(self._rays, *self._rings, self._ghosts, self._you)
        self.play(
            self.camera.frame.animate.move_to(self.DOME_CAM)
                .set(width=config.frame_width),
            FadeOut(fade_dots),
            self._terms.animate.set_opacity(0.25),
            Create(ground),
            run_time=2.0, rate_func=rate_functions.ease_in_out_sine,
        )
        self.play(LaggedStart(*[Create(m) for m in mesh], lag_ratio=0.015),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.7)

        cells, centers = VGroup(), []
        for i in range(bands):
            for j in range(cols):
                cell = AnnularSector(
                    inner_radius=b_edges[i], outer_radius=b_edges[i + 1],
                    angle=c_edges[j + 1] - c_edges[j],
                    start_angle=c_edges[j],
                    fill_color=STARLIGHT, fill_opacity=0.0, stroke_width=0)
                cells.add(cell)
                rm = 0.5 * (b_edges[i] + b_edges[i + 1])
                tm = 0.5 * (c_edges[j] + c_edges[j + 1])
                centers.append(np.array([rm * math.cos(tm),
                                         rm * math.sin(tm), 0.0]))
        self.add(cells)

        # demonstration: a handful of cells fire Act 4's move in miniature
        demo_ids = [3 * cols + 4, 1 * cols + 17, 4 * cols + 22,
                    2 * cols + 9, 0 * cols + 13, 3 * cols + 25,
                    1 * cols + 2]
        for n, idx in enumerate(demo_ids):
            c = centers[idx]
            d = c / np.linalg.norm(c)
            streak = Line(d * 0.18, c, stroke_color=STARLIGHT,
                          stroke_width=1.3, stroke_opacity=0.85)
            rt = max(0.30 - 0.02 * n, 0.16)         # the wave already quickens
            self.play(Create(streak), run_time=rt, rate_func=linear)
            self.play(cells[idx].animate.set_fill(opacity=0.92),
                      FadeOut(streak),
                      run_time=0.24, rate_func=rate_functions.ease_out_cubic)

        # the avalanche: every remaining cell has a fire-time drawn so most
        # land LATE — sparse popcorn first, then the sky simply gives way
        # (>>> POST: the score's whole build crests across these 4 seconds
        #  and CUTS to near-silence the instant the dome finishes filling.)
        T = 4.2
        rest = [k for k in range(len(cells)) if k not in demo_ids]
        u = RNG.uniform(0.0, 1.0, size=len(rest))
        fire = {k: float(T * (uu ** 0.38)) for k, uu in zip(rest, u)}
        adv = ValueTracker(0.0)

        def cascade(grp):
            a = adv.get_value()
            for k in rest:
                s = smoothstep((a - fire[k]) / 0.22)
                if s > 0:
                    grp[k].set_fill(opacity=0.92 * s)
        cells.add_updater(cascade)
        self.play(adv.animate.set_value(T + 0.25),
                  mesh.animate.set_stroke(color=STARLIGHT, opacity=0.5),
                  run_time=T, rate_func=linear)
        cells.clear_updaters()
        for k in rest:
            cells[k].set_fill(opacity=0.92)

        # unify: seams dissolve, and the dome becomes one saturated surface
        dome = AnnularSector(inner_radius=0.0, outer_radius=r_out,
                             angle=PI, start_angle=0,
                             fill_color=STARLIGHT, fill_opacity=1.0,
                             stroke_width=0)
        silhouette = Dot(ORIGIN, radius=0.06, fill_color=VOID,
                         fill_opacity=1.0).set_z_index(5)
        ground.set_z_index(5)
        self.play(FadeIn(dome), FadeOut(mesh), FadeIn(silhouette),
                  run_time=0.8, rate_func=rate_functions.ease_in_sine)
        self.remove(cells, self._terms, self._observer)
        self.wait(4.6)   # uncomfortably long, on purpose.  Let it be wrong.

        if self.USE_REAL_SKY_BEAT:
            real = safe_image("night_sky_real.jpg", 15.0,
                              "A REAL NIGHT SKY")
            real.set_z_index(30)
            self.play(FadeIn(real), run_time=0.4)
            self.wait(1.0)
            self.play(FadeOut(real), run_time=0.4)
            self.wait(0.8)

        self._dome_parts = VGroup(dome, ground, silhouette)

    # ═══════════════════════════════════════════════════════ ACT 6 ═══════
    def act6_a_name_for_the_wrongness(self):
        """Hard cut from the whiteout to Act 1's untouched sky — 'and yet,
        THIS is what we get.'  Silence.  Then the name, plainly, and one
        footnote of history.  Close unresolved, the mesh still lurking."""
        horizon, stars = self._build_baseline_sky()

        if self.HARD_CUT_TO_REAL:
            self.remove(self._dome_parts, *self._dome_parts)
            self.camera.frame.move_to(ORIGIN).set(width=config.frame_width)
            self.add(horizon, stars)
        else:
            self.camera.frame.move_to(ORIGIN).set(width=config.frame_width)
            stars.veil.set_value(0.0)
            self.add(horizon, stars)
            horizon.set_stroke(opacity=0.0)
            self.play(FadeOut(self._dome_parts),
                      stars.veil.animate.set_value(1.0),
                      horizon.animate.set_stroke(opacity=0.55),
                      run_time=2.4, rate_func=rate_functions.ease_in_out_sine)

        self.wait(1.8)   # (>>> POST: dead silence across this whole hold.)

        title = serif("OLBERS' PARADOX", STARLIGHT, 58, italic=False)
        title.move_to(UP * 1.35)
        rule = Line(LEFT * 0.55, RIGHT * 0.55, stroke_color=AMBER,
                    stroke_width=1.4)
        rule.next_to(title, DOWN, buff=0.42)
        # (>>> POST: one clean, quiet chime as the title finishes settling.)
        self.play(Write(title), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(Create(rule), run_time=0.5)


        if self.GHOST_GRID:
            # the bright version is still under there, waiting
            ghost = VGroup()
            r_in, r_out = 0.5, 5.6
            for r in np.linspace(r_in, r_out, self.DOME_BANDS + 1):
                ghost.add(Arc(radius=r, start_angle=0, angle=PI,
                              stroke_color=STARLIGHT, stroke_width=0.7,
                              stroke_opacity=0.05))
            for th in np.linspace(0, PI, self.DOME_COLS + 1):
                d = np.array([math.cos(th), math.sin(th), 0.0])
                ghost.add(Line(d * r_in, d * r_out, stroke_color=STARLIGHT,
                               stroke_width=0.7, stroke_opacity=0.05))
            ghost.shift(UP * self.HORIZON_Y)
            self.play(FadeIn(ghost), run_time=2.2,
                      rate_func=rate_functions.ease_in_out_sine)

        self.wait(2.8)   # unresolved, deliberately — Scene 2 owes an answer

        stars.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects
                    if m is not self.frame_marks],
                  self.frame_marks.animate.set_opacity(0.0),
                  run_time=2.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)
