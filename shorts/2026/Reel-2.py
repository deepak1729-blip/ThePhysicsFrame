from manim import *
import numpy as np
import math

# ─── PORTRAIT CANVAS (baked in — runs as-is) ───────────────────────────────
config.pixel_width  = 1080
config.pixel_height = 1920
config.frame_height = 8.0
config.frame_width  = 4.5

# ─── OBSERVATORY PALETTE (mobile-bumped reel variant, verbatim from Reel 1) ─
VOID      = "#0A0C10"   # background
PANEL     = "#11151C"   # lifted surfaces
STARLIGHT = "#F7F6F1"   # primary text · the light itself
DUST      = "#C7C1B3"   # secondary · the dimmed / lost / soft state
AMBER     = "#FFA540"   # primary accent · focus  (amber follows the eye)
CYAN      = "#35E0F2"   # glass / lenses

SERIF = "Spectral"      # the channel's idea voice (italic)
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(2)     # deterministic → stable render cache


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION VOCABULARY  (reused from the series, sizing bumped for mobile)
# ═══════════════════════════════════════════════════════════════════════════
def serif(s, color=STARLIGHT, size=48, italic=True, weight=NORMAL):
    return Text(s, font=SERIF, slant=ITALIC if italic else NORMAL,
                weight=weight, font_size=size, color=color)


def mono(s, color=DUST, size=26, spacing=0.22):
    t = Text(s, font=MONO, font_size=size, color=color)
    if spacing:
        t.set(width=t.width * (1 + spacing * 0.5))
    return t


def fit_w(mob, w):
    if mob.width > w:
        mob.scale_to_fit_width(w)
    return mob


# ─── READABILITY LAYER (same grammar as Reel 1) ────────────────────────────
TEXT_Z = 100          # z-index floor for all copy; art stays below
ART_Z = 10            # everything drawn in the world: rays, lenses, glows
PLATE_OPACITY = 0.5


def plated(mob, opacity=PLATE_OPACITY, z=TEXT_Z):
    """Wrap `mob` in a black rounded plate and lift the pair above the art, so
    a burned-in word can never be read against a live ray again. Size the
    child BEFORE calling — the plate is measured once."""
    plate = Rectangle(width=mob.width + 0.14, height=mob.height + 0.10,
                      fill_color=VOID, fill_opacity=opacity,
                      stroke_width=0).move_to(mob.get_center())
    g = VGroup(plate, mob)
    g.set_z_index(z)
    plate.set_z_index(z)
    mob.set_z_index(z + 1)
    return g


def corner_L(orientation, size=0.26, color=AMBER, width=2.0, opacity=0.35):
    sx = -1 if orientation[0] > 0 else 1
    sy = -1 if orientation[1] > 0 else 1
    h = Line(ORIGIN, RIGHT * size * sx, stroke_color=color,
             stroke_width=width, stroke_opacity=opacity)
    v = Line(ORIGIN, UP * size * sy, stroke_color=color,
             stroke_width=width, stroke_opacity=opacity)
    g = VGroup(h, v)
    g.anchor = orientation
    return g


def make_aperture(radius=0.30, color=AMBER, width=4.0):
    """THE circle — pupil · lens mouth. The same shape is the argument."""
    return Circle(radius=radius, stroke_color=color, stroke_width=width,
                  fill_color=color, fill_opacity=0.10)


def biconvex(h=1.0, bulge=0.9, color=CYAN, width=3.4, fill_op=0.14, axis=UP):
    """A biconvex lens of clear aperture `h`, bulge `bulge`. Built bulging
    left/right about a vertical aperture, then rotated so its optical axis
    lands on `axis` — pass UP for a lens that caps a vertical light-column."""
    top = np.array([0.0,  h / 2, 0.0])
    bot = np.array([0.0, -h / 2, 0.0])
    a = ArcBetweenPoints(top, bot, angle=bulge)
    b = ArcBetweenPoints(bot, top, angle=bulge)
    lens = VMobject()
    lens.set_points(np.vstack([a.get_points(), b.get_points()]))
    lens.set_stroke(color, width)
    lens.set_fill(color, fill_op)
    lens.rotate(angle_of_vector(axis) - angle_of_vector(RIGHT))
    return lens


def soft_dot(center, r, color, opacity, halo=2.6, halo_op=0.4):
    core = Circle(radius=r, stroke_width=0, fill_color=color,
                  fill_opacity=opacity).move_to(center)
    glow = Circle(radius=r * halo, stroke_width=0, fill_color=color,
                  fill_opacity=opacity * halo_op).move_to(center)
    return VGroup(glow, core)


def blazing_star(center, scale=1.0):
    """A bright point source with a tight warm glow and thin sparkle rays —
    reads as a blazing star (not a reticle). One VGroup, never moved: it is a
    LOCKED reference across the loop seam."""
    c = np.array([center[0], center[1], 0.0])
    glow2 = Circle(radius=0.34 * scale, stroke_width=0, fill_color=STARLIGHT,
                   fill_opacity=0.08).move_to(c)
    glow1 = Circle(radius=0.17 * scale, stroke_width=0, fill_color=STARLIGHT,
                   fill_opacity=0.30).move_to(c)
    core = Circle(radius=0.075 * scale, stroke_width=0, fill_color=STARLIGHT,
                  fill_opacity=1.0).move_to(c)
    spikes = VGroup()
    for d, ln, op in ((UP, 0.52, 0.55), (DOWN, 0.52, 0.55),
                      (LEFT, 0.52, 0.55), (RIGHT, 0.52, 0.55),
                      (UR, 0.30, 0.30), (UL, 0.30, 0.30),
                      (DR, 0.30, 0.30), (DL, 0.30, 0.30)):
        v = np.array([d[0], d[1], 0.0])
        v = v / np.linalg.norm(v)
        spikes.add(Line(c, c + v * ln * scale, stroke_color=STARLIGHT,
                        stroke_width=1.4, stroke_opacity=op))
    return VGroup(glow2, glow1, spikes, core)


def fuzzy_star(center, r=0.09, color=STARLIGHT, layers=22, spread=6.5, peak=0.9):
    """An out-of-focus blob — the percept of an uncollimated bundle."""
    g = VGroup()
    for i in range(layers):
        t = i / (layers - 1)
        rad = r * (1 + spread * (1 - t))
        op = peak * (t ** 2.4)
        g.add(Circle(radius=rad, stroke_width=0,
                     fill_color=color, fill_opacity=op))
    g.move_to(center)
    return g


def funnel_shape(y_top, y_tip, half_w, color=AMBER, op=0.10):
    """The literal funnel the VO asks us to picture: a wide mouth tapering to
    a throat, drawn as a filled wedge that sits UNDER the rays so the rays
    read as light running down its walls."""
    pts = [np.array([-half_w, y_top, 0.0]), np.array([half_w, y_top, 0.0]),
           np.array([0.0, y_tip, 0.0])]
    tri = Polygon(*pts, stroke_width=0, fill_color=color, fill_opacity=op)
    wall_l = Line(pts[0], pts[2], stroke_color=color, stroke_width=2.0,
                  stroke_opacity=0.55)
    wall_r = Line(pts[1], pts[2], stroke_color=color, stroke_width=2.0,
                  stroke_opacity=0.55)
    return VGroup(tri, wall_l, wall_r)


class PhotonFlow(VGroup):
    """A stream of light-motes that ride a path function p(s)->point, s in
    [0,1]. This is the reel's answer to dead air: light NEVER stops moving,
    so a held frame still reads as a live beam rather than a diagram.

    `path` is re-read every frame, so the motes follow the rays even while
    those rays are being morphed into a new optical state."""

    def __init__(self, path, n=7, color=STARLIGHT, r=0.035, speed=0.45,
                 opacity=0.9, fade_in=0.12, fade_out=0.86, seed=0):
        super().__init__()
        self.path = path
        self.speed = speed
        self.base_op = opacity
        self.fade_in, self.fade_out = fade_in, fade_out
        rng = np.random.default_rng(seed)
        self.s = list(rng.uniform(0, 1, n))
        for _ in range(n):
            self.add(Dot(radius=r, color=color, fill_opacity=opacity))
        self._place()

    def _env(self, s):
        """Fade motes in at birth and out at the end so they don't pop."""
        if s < self.fade_in:
            return s / self.fade_in
        if s > self.fade_out:
            return max(0.0, (1.0 - s) / (1.0 - self.fade_out))
        return 1.0

    def _place(self):
        for d, s in zip(self, self.s):
            d.move_to(self.path(s))
            d.set_opacity(self.base_op * self._env(s))

    def start(self):
        def upd(grp, dt):
            grp.s = [(v + dt * grp.speed) % 1.0 for v in grp.s]
            grp._place()
        self.add_updater(upd)
        return self

    def stop(self):
        self.clear_updaters()
        return self


def star_field(n=40, exclude=None, exclude_r=1.0, seed=5):
    """A sparse deterministic scatter — depth without competing with copy."""
    rng = np.random.default_rng(seed)
    hw, hh = config.frame_width / 2, config.frame_height / 2
    g = VGroup()
    while len(g) < n:
        p = np.array([float(rng.uniform(-hw, hw)),
                      float(rng.uniform(-hh, hh)), 0.0])
        if exclude is not None and np.linalg.norm(p - exclude) < exclude_r:
            continue
        r = float(rng.uniform(0.010, 0.028))
        op = float(rng.uniform(0.25, 0.70))
        g.add(Circle(radius=r, stroke_width=0,
                     fill_color=STARLIGHT, fill_opacity=op).move_to(p))
    return g


def twinkle(field, base_level=0.55, amount=0.35, speed=1.6, seed=9):
    """Breathe the field incoherently so the sky is never a frozen still."""
    rng = np.random.default_rng(seed)
    base = [s.get_fill_opacity() for s in field]
    ph = rng.uniform(0, 2 * math.pi, len(field))
    rate = rng.uniform(0.6, 1.5, len(field))
    field.t = 0.0

    def upd(grp, dt):
        grp.t += dt
        for s, b, p, k in zip(grp, base, ph, rate):
            s.set_fill(opacity=base_level * b * (1 - amount + amount *
                       (0.5 + 0.5 * math.sin(p + speed * k * grp.t))))
    field.add_updater(upd)


def focal_crosshair(point, color=AMBER, r=0.13, arm=0.30, width=2.4):
    """The series landmark wherever rays cross — Scene 3's mark, bumped."""
    p = np.array([point[0], point[1], 0.0])
    ring = Circle(radius=r, stroke_color=color, stroke_width=width).move_to(p)
    h = Line(p + LEFT * arm, p + RIGHT * arm, stroke_color=color,
             stroke_width=width * 0.7, stroke_opacity=0.9)
    v = Line(p + DOWN * arm, p + UP * arm, stroke_color=color,
             stroke_width=width * 0.7, stroke_opacity=0.9)
    core = Dot(p, radius=0.045, color=color)
    return VGroup(h, v, ring, core)


def safe_image(name, target_width, fallback_label):
    """Load an image by name; if absent, a framed placeholder so the script
    always runs. Drop the real PNG beside the script to replace it."""
    try:
        img = ImageMobject(name)
        img.set(width=target_width)
        return img
    except Exception:
        h = target_width * 0.9
        slot = VGroup()
        plate = Rectangle(width=target_width, height=h,
                          fill_color=PANEL, fill_opacity=1.0,
                          stroke_color=DUST, stroke_width=1.4,
                          stroke_opacity=0.4)
        lbl = fit_w(mono(fallback_label, DUST, 22), target_width * 0.86)
        lbl.move_to(plate.get_center())
        slot.add(plate, lbl)
        for o in (UL, UR, DL, DR):
            c = corner_L(o, size=0.16, color=AMBER, opacity=0.6)
            c.move_to(plate.get_corner(o), aligned_edge=o)
            slot.add(c)
        return slot


# ═══════════════════════════════════════════════════════════════════════════
class TwoLensRelayReel(MovingCameraScene):
    """One continuous ~50s vertical reel. Six beats, one idea:
    a telescope is a two-lens RELAY — the big lens gathers a star's light into
    a real image; the little lens rescues that image and hands it to your eye.
    Pull the second lens and it's instantly useless again — which is the loop."""

    # ── director toggles (one-line flips) ─────────────────────────────────
    LOOP_ENDING      = True    # True → fades perfectly back to Frame 0
    SHOW_MARKS       = True    # faint Observatory registration corners
    SHOW_LOUPE_PHOTO = False   # Beat 5: drop a real eyepiece shot beside the
                               # schematic (provide eyepiece_loupe.png)

    # ── locked optical geometry (portrait; optical axis is x = 0, light ↓) ─
    STAR   = np.array([0.0, 2.65, 0.0])    # the star — LOCKED across the loop
    Y_TOP  = 2.40                          # parallel sheaf begins here
    Y_OBJ  = 1.85                          # objective (big lens) — LOCKED
    Y_F    = 0.10                          # focal point (real image)
    Y_EYE  = -0.32                         # eyepiece (small lens)
    Y_PUP  = -1.20                         # your pupil
    Y_BLOOM = -1.05                        # where the useless bloom fades out

    A1       = 1.15                        # ray fill half-aperture on objective
    OBJ_HALF = 1.35                        # objective drawn half-aperture
    EYE_APER = 0.40                        # eyepiece drawn half-aperture
    PUPIL_R  = 0.30                        # pupil radius
    N_RAYS   = 7                           # Reduced density to un-clutter screen

    # corner-mark inset (decoration only — does NOT define the safe box)
    MARK_MARGIN = 0.30

    # ── NARRATION CLOCK ───────────────────────────────────────────────────
    # Every value is the start timestamp of a line in the recorded VO
    # (narration_only_word_timestamp.txt). The animation is pinned to these,
    # not to its own accumulated run_times: each beat plays its gestures and
    # then parks on the next cue via _cue(), so a re-cut of the audio only
    # needs these numbers changed. Beats are authored to land EARLY and wait —
    # never to overrun the line they illustrate.
    CUE = {
        "useless":      0.23,   # "By itself, a giant telescope lens is …"
        "single_point": 3.83,   # "It pulls light into a single point …"
        "funnel":       7.28,   # "Think of it like a funnel."
        "every_ray":    8.76,   # "Every ray … meet at one point."
        "focal_point": 13.94,   # "The focal point, creating a tiny image …"
        "except":      18.15,   # "Except, you can't use it."
        "doesnt_stop": 20.11,   # "Because light doesn't stop …"
        "fans_out":    22.51,   # "It passes straight through and fans out."
        "your_eye":    25.55,   # "So, if you just put your eye behind …"
        "second_lens": 31.84,   # "That's why a telescope needs a second lens"
        "straighten":  39.54,   # "Its job is to catch those escaping rays …"
        "eyepiece":    46.93,   # "That lens is called an eyepiece."
        "big_one":     49.17,   # "the big one gathers light into an image"
        "small_one":   51.61,   # "the small one delivers it to your eye"
        "not_magic":   53.15,   # "so a telescope isn't one piece of glass …"
        "relay":       56.29,   # "it's a two-part relay which is exactly why"
        "end":         59.74,   # tail of the VO
    }

    # derived optics
    @property
    def F1(self):  return self.Y_OBJ - self.Y_F      # objective focal length
    @property
    def F2(self):  return self.Y_F - self.Y_EYE      # eyepiece focal length
    @property
    def K(self):   return self.F2 / self.F1          # exit compression = f2/f1
    @property
    def US(self):  return np.linspace(-self.A1, self.A1, self.N_RAYS)

    # ── layering: pin any non-copy mobject to the art layer automatically ──
    def add(self, *mobs, **kw):
        for m in mobs:
            if m.z_index < TEXT_Z:
                m.set_z_index(ART_Z)
        return super().add(*mobs, **kw)

    # ═══════════════════════════════════════════════════════════════════════
    def construct(self):
        self.camera.frame.save_state()

        if self.SHOW_MARKS:
            self.marks = VGroup(*[corner_L(o) for o in (UL, UR, DL, DR)])
            self._pin_marks()
            self.marks.set_z_index(-9)
            super().add(self.marks)

        self.beat1_the_betrayal()
        self.beat2_the_funnel()
        self.beat3_light_doesnt_stop()
        self.beat4_the_rescue()
        self.beat5_name_the_team()
        self.beat6_loop_close()

    # ── keep the registration corners a constant screen size under zoom ────
    def _pin_marks(self):
        def upd(grp):
            f = self.camera.frame
            scl = f.get_width() / config.frame_width
            mx = f.get_width() / 2 - self.MARK_MARGIN * scl
            my = f.get_height() / 2 - self.MARK_MARGIN * scl
            c = f.get_center()
            for m in grp:
                o = m.anchor
                m.set(width=0.26 * scl, height=0.26 * scl)
                m.move_to(c + np.array([mx * o[0], my * o[1], 0.0]),
                          aligned_edge=o)
        self.marks.add_updater(upd)

    # ═══════════════════════════════════════════════════════════════════════
    #  RAY MODEL — one honest builder. A caught ray is a single straight run
    #  from the objective THROUGH the focal point to the eyepiece (exiting at
    #  −u·K, the image inverted and shrunk by f2/f1), then collimated to the
    #  pupil. Every beat is just this polyline in a different state.
    # ═══════════════════════════════════════════════════════════════════════
    def _corners(self, u, state):
        YO, YF, YE, YP, YB = (self.Y_OBJ, self.Y_F, self.Y_EYE,
                              self.Y_PUP, self.Y_BLOOM)
        top = np.array([u, YO, 0.0])
        # Every state returns THREE corners so that Transform between any two
        # states interpolates vertex-to-vertex. (A 2- vs 3-point polyline makes
        # Manim resample the path mid-flight, which reads as a visible snap.)
        if state == "stub":                                  # frame-zero hint
            tip = np.array([u, YO - 0.42, 0.0])
            return [top, (top + tip) / 2.0, tip]
        if state == "focus":                                 # converge, hold
            foc = np.array([0.0, YF, 0.0])
            return [top, (top + foc) / 2.0, foc]
        if state == "bloom":                                 # cross → fan out
            xb = u * (YB - YF) / (YO - YF)
            return [top, np.array([0.0, YF, 0.0]), np.array([xb, YB, 0.0])]
        if state == "diverge":                               # cross → flood eye
            xe = u * (YP - YF) / (YO - YF)
            return [top, np.array([0.0, YF, 0.0]), np.array([xe, YP, 0.0])]
        if state == "collim":                                # rescued: parallel
            xk = -u * self.K
            return [top, np.array([xk, YE, 0.0]), np.array([xk, YP, 0.0])]
        raise ValueError(state)

    def _ray(self, u, state, color=STARLIGHT, width=1.6, opacity=0.92):
        m = VMobject(stroke_color=color, stroke_width=width,
                     stroke_opacity=opacity)
        m.set_points_as_corners(self._corners(u, state))
        return m

    def _bundle(self, state, **st):
        return VGroup(*[self._ray(u, state, **st) for u in self.US])

    def _retarget(self, state, color, width, opacity,
                  lag=0.05, run_time=1.2, rate=smooth, extra=(), free=()):
        """Morph the live refracted bundle into a new optical state, ray by
        ray (lag = discipline arriving in sequence).

        `extra` rides the bundle's own run_time/rate_func. `free` is for
        animations that must keep their OWN timing (a Flash, say) — the
        scene-level run_time/rate_func would otherwise be forced onto them
        and stretch a short accent into a lurch."""
        tgs = [self._ray(u, state, color, width, opacity) for u in self.US]
        bundle = LaggedStart(*[Transform(self.refr[i], tgs[i])
                               for i in range(self.N_RAYS)], lag_ratio=lag)
        self.play(
            AnimationGroup(bundle, *extra, run_time=run_time, rate_func=rate),
            *free)

    # ── narration clock ───────────────────────────────────────────────────
    @property
    def clock(self):
        """Seconds of finished video so far — read from the renderer itself
        rather than accumulated by hand, so a Flash or a LaggedStart that sets
        its own run_time can never drift the cues out from under us."""
        return float(self.renderer.time)

    def _cue(self, name, min_hold=0.0, live=None):
        """Park until the narration reaches cue `name`, then return.

        A hold here is NEVER a frozen frame: the photon flow and the star
        twinkle keep running through `self.wait`, and `live` can supply an
        extra animation to spend the gap on (it is time-scaled to fit exactly).
        If the gesture before it overran we do NOT rewind — we take `min_hold`
        and carry on, so the reel degrades gracefully rather than desyncing
        everything downstream. Prints the drift when a beat runs long so
        overruns are visible at render time instead of on playback."""
        target = self.CUE[name]
        now = self.clock
        gap = target - now
        if gap > 0.001:
            if live is not None and gap > 0.25:
                # Spend the gap on real motion instead of a still frame.
                self.play(live, run_time=gap, rate_func=linear)
            else:
                self.wait(gap)
        elif gap < -0.05:
            print(f"  [cue] '{name}' overran by {-gap:.2f}s "
                  f"(wanted {target:.2f}, at {now:.2f})")
            if min_hold:
                self.wait(min_hold)
        elif min_hold:
            self.wait(min_hold)

    # ── photon flow ───────────────────────────────────────────────────────
    #  The motes are PUNCTUATION, not wallpaper. They come on only where the
    #  narration is about light travelling — the gather, the escape, the
    #  rescued beam — and are pulled off again as soon as that clause ends,
    #  so they never become the ambient texture the eye stops reading.
    def _make_flow(self, speed=0.42, n_per_ray=2, color=STARLIGHT,
                   r=0.032, opacity=0.85):
        """Build (but do not reveal) motes riding the LIVE refracted bundle.
        Each mote re-reads its ray every frame, so the stream keeps flowing
        correctly while _retarget morphs the rays underneath it."""
        self.flows = VGroup()
        for i in range(self.N_RAYS):
            ray = self.refr[i]

            def path(t, ray=ray):
                return ray.point_from_proportion(np.clip(t, 0.0, 1.0))

            f = PhotonFlow(path, n=n_per_ray, color=color, r=r, speed=speed,
                           opacity=opacity, seed=i)
            f.set_z_index(ART_Z + 3)
            self.flows.add(f)
        self.flow_op = opacity
        return self.flows

    def _flow_on(self, run_time=0.45, speed=None):
        """Fade the bundle motes in for a clause that is about light moving."""
        f = getattr(self, "flows", None)
        if f is None:
            return
        if speed is not None:
            self._flow_speed(speed)
        for sub in f:
            sub.start()
        if f not in self.mobjects:
            f.set_opacity(0.0)
            self.add(f)
        self.play(f.animate.set_opacity(self.flow_op), run_time=run_time)

    def _flow_off(self, run_time=0.45):
        """Pull the motes back off once that clause is over."""
        f = getattr(self, "flows", None)
        if f is None or f not in self.mobjects:
            return
        self.play(f.animate.set_opacity(0.0), run_time=run_time)
        for sub in f:
            sub.stop()
        self.remove(f)

    def _flow_speed(self, speed):
        for f in getattr(self, "flows", []):
            f.speed = speed

    def _rain_on(self, run_time=0.45):
        """Starlight falling onto the objective — only while the narration is
        about light arriving from the star."""
        r = getattr(self, "rain", None)
        if r is None:
            return
        for sub in r:
            sub.start()
        if r not in self.mobjects:
            r.set_opacity(0.0)
            self.add(r)
        self.play(r.animate.set_opacity(0.8), run_time=run_time)

    def _rain_off(self, run_time=0.45):
        r = getattr(self, "rain", None)
        if r is None or r not in self.mobjects:
            return
        self.play(r.animate.set_opacity(0.0), run_time=run_time)
        for sub in r:
            sub.stop()
        self.remove(r)

    def _drift(self, mob, shift, run_time, rate=linear):
        """A barely-perceptible drift — used instead of a dead wait so a held
        frame still breathes."""
        self.play(mob.animate.shift(shift), run_time=run_time, rate_func=rate)

    def _breathe(self, mob, amt=1.06, run_time=1.0):
        """A slow there-and-back swell — keeps a held frame alive."""
        self.play(mob.animate.scale(amt), rate_func=there_and_back,
                  run_time=run_time)

    def _pulse_down(self, x_of, y_from, y_to, color, run_time=1.0):
        """Send a soft pulse of light down a beam."""
        p = soft_dot([x_of, y_from, 0], 0.06, color, 0.9, halo=2.6, halo_op=0.5)
        p.set_z_index(ART_Z + 4)
        self.add(p)
        self.play(p.animate.move_to([x_of, y_to, 0]),
                  run_time=run_time, rate_func=linear)
        self.remove(p)

    # ═══════════════════════════════════════════ BEAT 1 · 0:00–0:05 ═══════
    def beat1_the_betrayal(self):
        """Frame zero now establishes the setting: we are looking at the sky.
        Then the lens drops in, the light rays rapidly crash down into it, 
        pinch, and violently bloom out. This creates a highly dynamic 3-second hook."""
        
        # 1. Establish the target (just the star and night sky)
        field = star_field(40, exclude=self.STAR, exclude_r=1.1)
        field.set_z_index(-5)
        super().add(field)
        twinkle(field)
        self.field = field

        self.star = blazing_star(self.STAR)
        self.add(self.star)
        # The star pulses for the whole reel — the source is never a still.
        self.star.t = 0.0

        def star_pulse(m, dt):
            m.t += dt
            k = 1.0 + 0.035 * math.sin(2.1 * m.t)
            m.set(width=m.width * k / getattr(m, "_k", 1.0))
            m._k = k
        self.star.add_updater(star_pulse)

        # Frame 0 holds on just the sky until the VO opens — the twinkling
        # field and the pulsing star carry the hold.
        self._cue("useless")

        # 2. "By itself, a giant telescope lens..."  (0:00.23)
        self.objective = biconvex(h=2 * self.OBJ_HALF, bulge=0.50, color=CYAN,
                                  width=3.8, fill_op=0.12, axis=UP)
        self.objective.move_to([0, self.Y_OBJ, 0])
        self.play(FadeIn(self.objective, shift=UP * 0.5), run_time=0.6)

        # 3. Light falls from the star onto the glass
        self.incoming = VGroup(*[
            Line([u, self.Y_TOP, 0], [u, self.Y_OBJ, 0],
                 stroke_color=STARLIGHT, stroke_width=1.6, stroke_opacity=0.9)
            for u in self.US])
        
        # Lagged Start creates a cascading drop effect. Ordered from the axis
        # outward so the cascade reads as light spreading across the glass
        # rather than sweeping left-to-right, and given enough run_time that
        # 7 rays at 24-60fps don't strobe.
        order = sorted(range(self.N_RAYS), key=lambda i: abs(self.US[i]))
        self.play(LaggedStart(*[Create(self.incoming[i]) for i in order],
                              lag_ratio=0.12),
                  run_time=0.9, rate_func=smooth)

        # Starlight falling onto the glass. BUILT here, shown only later —
        # it belongs to the funnel explanation, not to the opening hook.
        self.rain = VGroup()
        for i, u in enumerate(self.US):
            def path(t, u=u):
                return np.array([u, self.Y_TOP + t * (self.Y_OBJ - self.Y_TOP),
                                 0.0])
            self.rain.add(PhotonFlow(path, n=2, color=STARLIGHT, r=0.030,
                                     speed=0.55, opacity=0.8, seed=20 + i))
        self.rain.set_z_index(ART_Z + 3)

        self.refr = self._bundle("stub", color=STARLIGHT, width=1.6, opacity=0.9)
        self.add(self.refr)

        self.fglow = soft_dot([0, self.Y_F, 0], 0.05, STARLIGHT, 0.0,
                              halo=3.0, halo_op=0.5)
        self.add(self.fglow)

        # Motes are prepared but stay hidden until a clause actually needs
        # them (see _flow_on / _flow_off).
        self._make_flow(speed=0.5, n_per_ray=2)

        # 4. Pinch → flare → bloom, played as ONE accelerating gesture.
        #    The converge eases in and lands (smooth, not rush_into) so the
        #    rays are momentarily at rest exactly when the flare fires; the
        #    flare then rides ON the start of the bloom instead of sitting in
        #    a dead 0.2s gap between two full-speed easings.
        self._retarget("focus", STARLIGHT, 1.8, 0.95,
                       lag=0.05, run_time=0.9, rate=smooth,
                       extra=[self.fglow.animate.set_fill(STARLIGHT, 1.0)])

        self._retarget("bloom", DUST, 1.5, 0.5,
                       lag=0.03, run_time=0.8, rate=rush_from,
                       extra=[self.fglow.animate.scale(2.6)
                              .set_fill(DUST, 0.0)],
                       free=[Flash([0, self.Y_F, 0], color=STARLIGHT,
                                   flash_radius=0.5, line_length=0.18,
                                   num_lines=16, run_time=0.35)])

        # The word "useless" is spoken at the END of line 1 (~0:02.6), so the
        # card waits for it rather than pre-empting the punchline.
        useless = fit_w(serif("Useless.", STARLIGHT, 62, weight=BOLD), 2.5)
        self.useless = plated(useless.move_to([0, -0.72, 0]))
        self._cue("single_point")
        self.play(FadeIn(self.useless, scale=0.7), run_time=0.4)

    # ═══════════════════════════════════════════ BEAT 2 · 0:05–0:18 ═══════
    def beat2_the_funnel(self):
        # Hold "Useless." across line 2 ("…but you can't use it yet"), then
        # clear it exactly as the funnel image is spoken.
        self._cue("funnel")
        self.play(FadeOut(self.useless, scale=0.85), run_time=0.28)

        # ── "Think of it like a funnel." (0:07.28) ─────────────────────────
        # The line asks the viewer to picture a funnel, so DRAW one: a wedge
        # from the lens mouth down to the focal throat. It builds from the
        # rim inward, holds under the words, and then dissolves into the
        # ray geometry it was a metaphor for.
        funnel = funnel_shape(self.Y_OBJ - 0.06, self.Y_F, self.OBJ_HALF * 0.92,
                              color=AMBER, op=0.09)
        funnel.set_z_index(ART_Z - 1)
        
        self.play(LaggedStart(FadeIn(funnel[0], scale=0.9),
                              Create(funnel[1]), Create(funnel[2]),
                              lag_ratio=0.25),
                  run_time=0.8, rate_func=smooth)

        # "Every ray … lands on the glass and gets bent inward until they all
        # meet at one point." (0:08.76) — one long continuous GATHER. The
        # rays sweep inward over the whole line while the motes visibly run
        # down the funnel walls, so the sentence is illustrated end to end
        # instead of snapping shut and waiting.
        self._cue("every_ray")
        # Light itself is the subject of this line — show it arriving and
        # running down the funnel walls.
        self._rain_on(0.4)
        self._flow_on(0.4, speed=0.85)  # light accelerates as it funnels in
        self._retarget("focus", STARLIGHT, 1.8, 0.95,
                       lag=0.10, run_time=3.15, rate=smooth,
                       extra=[self.fglow.animate.scale(1 / 2.6)
                              .set_fill(STARLIGHT, 0.0)])

        # The funnel has done its job — dissolve it INTO the converging rays,
        # and take the motes off with it: the next line is about a still image
        # hanging in space, which a running stream would only fight.
        self.play(funnel.animate.set_opacity(0.0), run_time=0.35)
        self.remove(funnel)
        # One combined pull-off, so gating the motes costs a single beat.
        self._rain_off(0.3)
        self._flow_off(0.3)

        # "The focal point, creating a tiny image of the star …" (0:13.94)
        # "The focal point, creating a tiny image of the star right there in
        #  empty space." (0:13.94) — the crosshair draws on, the image is
        #  BUILT by arriving light, and the camera makes one slow continuous
        #  move in and back out rather than snapping and freezing.
        self._cue("focal_point")
        cross = focal_crosshair([0, self.Y_F, 0]).set_z_index(TEXT_Z - 2)
        real_star = soft_dot([0, self.Y_F, 0], 0.055, STARLIGHT, 1.0,
                             halo=2.4, halo_op=0.55)
        self.real_star = real_star
        self.cross = cross
        fp_lbl = plated(fit_w(mono("focal point", AMBER, 26), 1.24)
                        .move_to([1.02, self.Y_F + 0.02, 0]))

        real_star.scale(0.2)
        self.add(real_star)
        # The push-in and the image forming happen TOGETHER — one gesture.
        self.play(AnimationGroup(
                      self.camera.frame.animate.scale(0.5)
                          .move_to([0, self.Y_F, 0]),
                      Create(cross),
                      real_star.animate.scale(5.0),
                      lag_ratio=0.18),
                  run_time=1.8, rate_func=smooth)
        self.play(FadeIn(fp_lbl, shift=LEFT * 0.12),
                  Flash([0, self.Y_F, 0], color=AMBER, flash_radius=0.32,
                        line_length=0.14, num_lines=14),
                  run_time=0.5)

        # "…a tiny image of the star, right there in empty space." Hold the
        # close-up LIVE: the image keeps drinking light while the line runs.
        self._cue("except", live=self.camera.frame.animate.scale(1.06))
        self.play(self.camera.frame.animate.restore(), run_time=0.8,
                  rate_func=smooth)
        self.fp_lbl = fp_lbl

    # ═══════════════════════════════════════════ BEAT 3 · 0:18–0:28 ═══════
    def beat3_light_doesnt_stop(self):
        # "Except, you can't use it." — strip the label on the turn.
        self.play(FadeOut(self.fp_lbl, shift=RIGHT * 0.12), run_time=0.4)

        # "Because light doesn't stop when it reaches that point." (0:20.11)
        # The point SWELLS and strains under arriving light — the visual
        # argument that it cannot hold what it is being given.
        self._cue("doesnt_stop")
        # The clause is literally about light not stopping — bring the stream
        # back so the viewer can watch it refuse to.
        self._flow_on(0.35, speed=1.05)
        self.play(self.real_star.animate.scale(1.8).set_fill(STARLIGHT, 1.0),
                  Flash([0, self.Y_F, 0], color=STARLIGHT, flash_radius=0.55,
                        line_length=0.22, num_lines=20),
                  run_time=0.55, rate_func=rush_into)
        # …and keeps straining right up to the moment it gives way.
        self._cue("fans_out",
                  live=self.real_star.animate.scale(1.14).set_fill(STARLIGHT, 1.0))

        # "It passes straight through and immediately fans back out." (0:22.51)
        # A slower fan so the eye can FOLLOW the light escaping, instead of
        # a 1.35s snap that is over before the clause is.
        self._retarget("diverge", STARLIGHT, 1.6, 0.85,
                       lag=0.03, run_time=2.3, rate=rush_from,
                       extra=[self.real_star.animate.scale(1 / (1.8 * 1.14))
                              .set_fill(STARLIGHT, 0.85),
                              self.cross.animate.set_stroke(opacity=0.4)])

        # "So, if you just put your eye behind the lens …" (0:25.55)
        # The eye RISES INTO the flood of spreading light.
        self._cue("your_eye")
        self.eye = make_aperture(self.PUPIL_R, AMBER, 4.4)
        self.eye.set_fill(AMBER, 0.0)
        self.eye.move_to([0, self.Y_PUP - 2.2, 0]).set_z_index(ART_Z + 2)
        self.add(self.eye)
        self.play(self.eye.animate.move_to([0, self.Y_PUP, 0]),
                  run_time=1.0, rate_func=smooth)
        # The percept is the subject from here — clear the stream so the blur
        # is not read against moving dots.
        self._flow_off(0.4)

        percept = Circle(radius=0.30, stroke_color=DUST, stroke_width=2.4,
                         fill_color=VOID, fill_opacity=0.85)
        percept.move_to([-1.28, -0.52, 0]).set_z_index(TEXT_Z)
        smear = fuzzy_star(percept.get_center(), r=0.05, color=STARLIGHT,
                           layers=18, spread=4.2, peak=0.85)
        smear.set_z_index(TEXT_Z + 1)
        leader = DashedLine(self.eye.get_center() + UL * 0.18,
                            percept.get_bottom(), dash_length=0.07,
                            stroke_color=DUST, stroke_width=1.4,
                            stroke_opacity=0.4).set_z_index(ART_Z + 1)
        blur_tag = plated(fit_w(mono("blur", DUST, 22), 1.1)
                          .move_to([-1.28, -0.02, 0]))
        # "…you catch the spreading light and all you see is a soft useless
        #  blur." The percept builds as the light arrives, then the blob is
        #  kept SEETHING (a slow swell/shrink loop) so the long hold under
        #  the rest of the line is alive rather than a frozen still.
        self.play(Create(leader), FadeIn(percept), run_time=0.55)
        self.play(FadeIn(smear, scale=0.6),
                  FadeIn(blur_tag, shift=UP * 0.1), run_time=0.7)

        smear.t = 0.0
        smear._k = 1.0

        def seethe(m, dt):
            m.t += dt
            k = 1.0 + 0.10 * math.sin(2.4 * m.t)
            m.scale(k / m._k)
            m._k = k
        smear.add_updater(seethe)

        # Sit on the blur through the rest of the line — seething, not frozen.
        self._cue("second_lens")
        smear.remove_updater(seethe)
        smear.scale(1.0 / smear._k)

        # Kept individually addressable: Beat 4 resolves this percept the
        # instant the eyepiece re-collimates the bundle.
        self.percept = percept
        self.smear = smear
        self.blur_tag = blur_tag
        self.percept_grp = VGroup(leader, percept, smear, blur_tag)

    # ═══════════════════════════════════════════ BEAT 4 · 0:28–0:40 ═══════
    def beat4_the_rescue(self):
        ghost = self._bundle("diverge", color=DUST, width=1.4, opacity=0.22)
        self.add(ghost)

        eyepiece = biconvex(h=2 * self.EYE_APER, bulge=1.45, color=CYAN,
                            width=3.4, fill_op=0.16, axis=UP)
        eyepiece.move_to([1.7, self.Y_EYE + 0.5, 0]).set_opacity(0.0)
        self.eyepiece = eyepiece
        self.add(eyepiece)
        # "That's why a telescope needs a second lens, a small one placed
        #  right behind the focal point…" (0:31.84) — the lens FLIES IN and
        #  settles, one continuous move rather than a pop-and-hold.
        self.play(eyepiece.animate.move_to([0, self.Y_EYE, 0])
                  .set_opacity(1.0), run_time=1.2, rate_func=smooth)
        # Settle-bounce ABOUT the resting height, not toward it: the rate func
        # is a round trip, so the lens must already sit on Y_EYE — the exact
        # line where "collim" kinks the rays — and only dip off it and back.
        self.play(eyepiece.animate.move_to([0, self.Y_EYE - 0.16, 0]),
                  run_time=0.5, rate_func=there_and_back_with_pause)

        # "…where the light has only just begun to spread." Show WHY the
        # placement matters: a caliper spans focal point -> eyepiece, so the
        # short gap is a thing you can see, and the previous 4.9s dead hold
        # becomes an explanation.
        gap_line = DoubleArrow([0.52, self.Y_F, 0], [0.52, self.Y_EYE, 0],
                               buff=0.0, stroke_color=DUST, stroke_width=2.0,
                               tip_length=0.13).set_z_index(ART_Z + 2)
        gap_line.set_opacity(0.75)
        # Pushed clear of the ray fan and given a solid plate: on the axis at
        # 0.62 below the lens it sat directly on the diverging rays.

        self.play(GrowFromCenter(gap_line), run_time=0.6)

        # Hold LIVE on the placement: the lens breathes and the light keeps
        # streaming past it while the narrator finishes the sentence.
        self._cue("straighten", live=eyepiece.animate.scale(1.06))
        self.play(FadeOut(gap_line), eyepiece.animate.scale(1 / 1.06),
                  run_time=0.45)
        # "Its job is to catch those escaping rays and straighten them back
        #  out into a slim parallel beam…" (0:39.54) — the hero gesture. Rays
        #  bend straight one after another (a bigger lag so you SEE them
        #  arrive in sequence) and the flow slows as the beam settles.
        self._flow_on(0.4, speed=0.6)
        self._retarget("collim", AMBER, 2.0, 0.95,
                       lag=0.10, run_time=2.35, rate=smooth,
                       extra=[self.real_star.animate.set_fill(STARLIGHT, 0.0),
                              self.cross.animate.set_stroke(opacity=0.0)])

        self.play(FadeOut(ghost),
                  self.eye.animate.set_stroke(AMBER, 5.5).scale(1.12),
                  Flash([0, self.Y_PUP, 0], color=AMBER, flash_radius=0.4,
                        line_length=0.16, num_lines=16),
                  run_time=0.6)
        self.play(self.eye.animate.scale(1 / 1.12), run_time=0.3)

        rescued = plated(fit_w(mono("parallel again", AMBER, 24), 1.9)
                         .move_to([1.05, self.Y_EYE, 0]))
        self.rescued_tag = rescued
        self.play(FadeIn(rescued, shift=LEFT * 0.1), run_time=0.28)

        # ── The payoff: parallel rays land on a relaxed eye, so the percept
        #    must SNAP INTO FOCUS. The out-of-focus blob collapses to a clean
        #    point and the verdict flips blur -> sharp.
        sharp = soft_dot(self.percept.get_center(), 0.045, STARLIGHT, 1.0,
                         halo=2.4, halo_op=0.35).set_z_index(TEXT_Z + 1)
        sharp_tag = plated(fit_w(mono("sharp", AMBER, 22), 1.1)
                           .move_to(self.blur_tag.get_center()))
        self.play(ReplacementTransform(self.smear, sharp),
                  self.percept.animate.set_stroke(AMBER, 3.0),
                  ReplacementTransform(self.blur_tag, sharp_tag),
                  Flash(self.percept.get_center(), color=STARLIGHT,
                        flash_radius=0.34, line_length=0.14, num_lines=16),
                  run_time=0.7, rate_func=smooth)
        self.smear, self.blur_tag = sharp, sharp_tag
        # Rebuilt so Beat 5 still fades the whole percept away in one go.
        self.percept_grp = VGroup(self.percept_grp[0], self.percept,
                                  sharp, sharp_tag)
        self._breathe(sharp, amt=1.12, run_time=0.5)

        # "…a slim parallel beam narrow enough to slip through the tiny
        #  opening of your pupil." The pupil ring tightens around the beam
        #  as the pulses thread it — the fit is the point of the line.
        self._pulse_down(-self.US[-1] * self.K, self.Y_EYE, self.Y_PUP,
                         AMBER, run_time=0.55)
        self.play(self.eye.animate.scale(0.9).set_stroke(AMBER, 6.0),
                  run_time=0.4, rate_func=there_and_back)
        self._pulse_down(0.0, self.Y_EYE, self.Y_PUP, AMBER, run_time=0.55)
        self._cue("eyepiece", live=self.eye.animate.scale(1.04))
        self.play(self.eye.animate.scale(1 / 1.04), run_time=0.25)
        # Beat 5 is naming the two lenses, not tracing light — stream off.
        self._flow_off(0.28)

    # ═══════════════════════════════════════════ BEAT 5 · 0:40–0:48 ═══════
    def beat5_name_the_team(self):
        self.play(FadeOut(self.rescued_tag),
                  FadeOut(self.percept_grp), run_time=0.22)

        # "That lens is called an eyepiece." — the script NAMES the small lens
        # first, so the EYEPIECE label now leads and GATHERS follows on
        # "the big one gathers…" (the previous order pre-empted the VO).
        # Placed below-right of the glass: at x=0.86 it collided with the lens
        # and ran past the safe edge once the camera pushes in.
        eyepiece_lbl = plated(fit_w(mono("EYEPIECE", CYAN, 24), 1.20)
                              .move_to([0.72, self.Y_EYE - 0.46, 0]))
        self.play(self.eyepiece.animate.scale(1.2), FadeIn(eyepiece_lbl, scale=0.7),
                  run_time=0.3)
        self.play(self.eyepiece.animate.scale(1 / 1.2), run_time=0.15)

        self.play(self.camera.frame.animate.scale(1.06).move_to([0, 0.35, 0]),
                  run_time=0.5, rate_func=smooth)

        # "the big one gathers light into an image" (0:49.17)
        self._cue("big_one")
        gathers = plated(fit_w(serif("GATHERS", STARLIGHT, 40, weight=BOLD),
                               2.0).move_to([0, 2.22, 0]))
        self.play(self.objective.animate.scale(1.12), FadeIn(gathers, scale=0.7),
                  run_time=0.35)
        self.play(self.objective.animate.scale(1 / 1.12), run_time=0.18)

        # "the small one delivers it to your eye" (0:51.61) — the baton
        # hand-off below IS that delivery, so it starts on the line.
        self._cue("small_one", live=self.eyepiece.animate.scale(1.05))
        self.play(self.eyepiece.animate.scale(1 / 1.05), run_time=0.2)

        if self.SHOW_LOUPE_PHOTO:
            loupe = safe_image("eyepiece_loupe.png", 1.4, "REAL EYEPIECE")
            loupe.move_to([-1.25, self.Y_EYE, 0])
            self.play(FadeIn(loupe), run_time=0.5)
            self.wait(0.4)
            self.play(FadeOut(loupe), run_time=0.3)

        baton = soft_dot([0, self.Y_OBJ, 0], 0.07, AMBER, 1.0, halo=2.8,
                         halo_op=0.5).set_z_index(ART_Z + 4)
        self.add(baton)
        self.play(baton.animate.move_to([0, self.Y_F, 0]),
                  run_time=0.32, rate_func=rush_into)
        self.play(Flash([0, self.Y_F, 0], color=AMBER, flash_radius=0.3,
                        line_length=0.12, num_lines=12), run_time=0.2)
        self.play(baton.animate.move_to([0, self.Y_EYE, 0]),
                  run_time=0.28, rate_func=smooth)
        self.play(Flash([0, self.Y_EYE, 0], color=CYAN, flash_radius=0.3,
                        line_length=0.12, num_lines=12), run_time=0.2)
        self.play(baton.animate.move_to([0, self.Y_PUP, 0]),
                  run_time=0.28, rate_func=rush_from)
        self.play(baton.animate.scale(0.3).set_fill(AMBER, 0.0), run_time=0.15)
        self.remove(baton)

        self.gathers = gathers
        self.eyepiece_lbl = eyepiece_lbl
        # "so a telescope isn't one piece of glass doing something magical"
        self._cue("not_magic")

    # ═══════════════════════════════════════════ BEAT 6 · 0:48–0:55 ═══════
    def beat6_loop_close(self):
        """Removes the rescuer lens, drops the collimation, and then fades 
        everything out except the star field to perfectly close the loop with Frame 0."""
        self.play(FadeOut(self.gathers), FadeOut(self.eyepiece_lbl),
                  self.camera.frame.animate.restore(), run_time=0.7,
                  rate_func=smooth)

        delivered = soft_dot([0, self.Y_PUP, 0], 0.055, STARLIGHT, 1.0,
                             halo=2.2, halo_op=0.5).set_z_index(ART_Z + 3)
        self.add(delivered)
        self.play(FadeIn(delivered, scale=0.6),
                  Flash([0, self.Y_PUP, 0], color=STARLIGHT, flash_radius=0.3,
                        line_length=0.12, num_lines=12), run_time=0.5)
        self._breathe(delivered, amt=1.15, run_time=0.9)

        # "it's a two-part relay which is exactly why …" (0:56.29) — the
        # last line is the loop hook, so pulling the eyepiece lands right
        # on it and the sag back into blur closes over the unfinished line.
        self._cue("relay")

        if not self.LOOP_ENDING:
            payoff = plated(fit_w(serif("a two-part relay.", AMBER, 44,
                                        weight=BOLD), 2.8).move_to([0, -0.62, 0]))
            self.play(FadeIn(payoff, shift=UP * 0.12), run_time=0.7)
            self.wait(1.4)
            return

        # 1. Pull the eyepiece
        self.play(self.eyepiece.animate.shift(UP * 0.35).set_opacity(0.0),
                  FadeOut(delivered, scale=1.4), run_time=0.5,
                  rate_func=rush_into)
        self.remove(self.eyepiece)

        # 2. Rays sag out of collimation back into the useless bloom — slow
        #    enough to register as a LOSS, which is what sells the loop.
        self._flow_on(0.3, speed=1.0)
        self._retarget("bloom", DUST, 1.5, 0.5,
                       lag=0.04, run_time=1.5, rate=smooth,
                       extra=[self.eye.animate.shift(DOWN * 2.4).set_opacity(0.0)])
        self.remove(self.eye)

        # 3. Fade out the objective lens, incoming rays, and bloom 
        # to leave ONLY the target star, identical to the opening frame.
        self._flow_off(0.3)
        self._rain_off(0.15)
        self.play(FadeOut(self.objective), FadeOut(self.incoming),
                  FadeOut(self.refr), FadeOut(self.fglow), run_time=0.7)

        # Run the sky-only frame out to the end of the VO, then a tiny
        # breather so the software stitch back to frame 0 is seamless.
        self._cue("end")
        self.wait(0.2)