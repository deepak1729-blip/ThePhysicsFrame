from manim import *
import numpy as np
import math

# ══════════════════════════════════════════════════════════════════════════
#  CANVAS
# ══════════════════════════════════════════════════════════════════════════
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_height = 8.0
config.frame_width = 4.5

# ── OBSERVATORY PALETTE — reel tier (saturation lifted for a phone screen) ─
VOID = "#000C10"        # background
PANEL = "#0A141A"       # lifted surfaces
STARLIGHT = "#F7F6F1"   # a car at full speed · primary copy
DUST = "#8792A0"        # a car at cruising speed · metadata
AMBER = "#FFA540"       # focus — amber follows the eye (the hero / the fix)
CYAN = "#35E0F2"        # cool structure — lane lines, geometry, gauges
C_ANGLE = "#FF5C5C"     # BRAKING — the disturbance itself
C_GROUND = "#4FE0A0"    # restored flow — the killed wave

config.background_color = VOID


def _pick_font(*names):
    """Fall back gracefully instead of silently rendering in DejaVu."""
    try:
        import manimpango
        have = {f for f in manimpango.list_fonts()}
    except Exception:
        return names[0]
    for n in names:
        if n in have:
            return n
    print(f"[type]  none of {names} installed — falling back to {names[-1]!r}")
    return names[-1]


SERIF = _pick_font("Spectral", "EB Garamond", "Georgia", "DejaVu Serif")
MONO = _pick_font("Space Mono", "IBM Plex Mono", "DejaVu Sans Mono")

# ── TYPE SCALE — four sizes, no ad-hoc numbers anywhere below ──────────────
T_DISPLAY = 46      # the one line the beat is about
T_CAPTION = 38      # supporting copy
T_LABEL = 22        # mono labels on the artwork
T_MICRO = 18        # units, metadata, source notes

# ── LAYOUT SLOTS ──────────────────────────────────────────────────────────
# The frame is 8.0 tall (+-4.0) and 4.5 wide (+-2.25).
#
# SUBTITLE RESERVATION: burned-in subtitles land on the y = -2.0 line, so the
# band below is left completely empty — no copy, no artwork, not even a car.
# The road does not simply stop there, it dissolves into it (see Road._edge),
# which is why the bottom third reads as deliberate negative space instead of
# a crop.  Everything the reel says lives in the top stack.
SUB_MID = -2.00
SUB_TOP, SUB_BOT = -1.58, -2.74     # keep-out band for the subtitle track
Y_TAG = 3.34        # metadata, top line
Y_TITLE = 2.80      # the one line the beat is about
Y_METRIC = 2.16     # numbers / equations, under the title
Y_CAPTION = Y_TITLE                 # alias: there is only one display slot
ART_TOP, ART_BOT = 2.00, SUB_TOP    # the world may only be drawn between these
ART_MID = 0.5 * (ART_TOP + ART_BOT)
SAFE_W = 3.50       # max copy width

# ── MOTION LAWS (series-standard) ──────────────────────────────────────────
EASE = rate_functions.ease_in_out_sine      # anything that moves
POP = rate_functions.ease_out_cubic         # anything that arrives
IN_T, OUT_T = 0.36, 0.28                    # copy in / copy out
SWAP_T = 0.55                               # a world cross-dissolve; every
#   beat that hands over to a new simulation ends this much early so the
#   dissolve finishes ON the next cue instead of pushing it late.

TEXT_Z, ART_Z = 100, 10
PLATE_OPACITY = 0.80


# ══════════════════════════════════════════════════════════════════════════
#  TRAFFIC CORE — real SI units.  Nothing here knows what a pixel is.
#  Verified standalone: `python Reel-3.py` prints every number the reel shows.
# ══════════════════════════════════════════════════════════════════════════
MPS_MPH = 2.2369362921
MPS_KPH = 3.6

CAR_L = 4.50            # m — a hatchback
N_RING = 22             # Sugiyama et al. 2008: 22 vehicles ...
RING_L = 230.0          # ... on a 230 m single-lane circuit
SPACING = RING_L / N_RING           # 10.45 m centre-to-centre
H_EQ = SPACING - CAR_L              # 5.95 m of actual daylight
A_SENS = 1.30           # 1/s — how hard a driver chases their target speed
LAMBDA = 0.38           # 1/s — how hard they react to the CLOSING SPEED ahead
V_AMP, H_C, H_W, D_MIN = 7.60, 5.50, 3.40, 0.40
V_CAP = 8.60            # m/s — Sugiyama's drivers were told to hold ~30 km/h
_OFF = np.tanh((D_MIN - H_C) / H_W)
DT = 0.01


def V_opt(h):
    """Optimal-velocity law (Bando et al. 1995): the speed a driver picks for
    the gap ahead.  Big gap -> the posted speed; gap closes -> speed collapses;
    at D_MIN of daylight they are stopped, because nobody parks on a bumper."""
    return np.clip(V_AMP * (np.tanh((np.maximum(h, 0.0) - H_C) / H_W) - _OFF),
                   0.0, V_CAP)


V_EQ = float(V_opt(np.array(H_EQ)))      # 7.92 m/s = 28.5 km/h — the cruise
V_FREE = float(V_opt(np.array(1e4)))     # 12.8 m/s — a car with the road to itself


def integrate(n, s0, v0, L, T, dt=DT, a=A_SENS, lam=LAMBDA, ext=None,
              leader=None, hero=None):
    """Full-velocity-difference car-following.  Car i follows car i+1.

    The `lam` term is not decoration.  With pure optimal-velocity (lam = 0)
    a driver only reacts to the SIZE of the gap, never to how fast it is
    closing — so cars arrive at the back of a jam at full speed and the
    anti-collision clamp below has to stop them, which it does in one frame
    at ~-770 m/s^2.  That is a numerical collision wearing a brake light, and
    it is what makes a jam look like it snaps instead of forming.  Reacting to
    closing speed (Jiang et al. 2001) removes every one of those events:
    peak deceleration across the whole reel is about -5 m/s^2, which is a
    person braking hard rather than a car hitting a wall.

    L = ring length, or None for an open line whose leader (index n-1) is
    driven by leader(t) -> speed.  ext(t) -> array injects a driver's own
    action; hero = (index, ctrl) swaps one driver's control law entirely.
    Returns S, V, A shaped (steps+1, n): position (m), speed (m/s), accel.
    """
    s = np.array(s0, float)
    v = np.array(v0, float)
    K = int(round(T / dt))
    S = np.zeros((K + 1, n)); Vv = np.zeros((K + 1, n)); Ac = np.zeros((K + 1, n))
    S[0], Vv[0] = s, v
    for k in range(K):
        t = k * dt
        if L is not None:
            sl, vl = np.roll(s, -1), np.roll(v, -1)
            gap = (sl - s) % L - CAR_L
        else:
            sl = np.empty(n); vl = np.empty(n)
            sl[:-1], vl[:-1] = s[1:], v[1:]
            sl[-1], vl[-1] = s[-1] + 1e6, leader(t)
            gap = sl - s - CAR_L
            gap[-1] = 1e6
        acc = a * (V_opt(gap) - v) + lam * (vl - v)
        if L is None:
            acc[-1] = (leader(t) - v[-1]) / dt        # leader is prescribed
        if hero is not None:
            acc[hero[0]] = hero[1](gap[hero[0]], v[hero[0]])
        if ext is not None:
            acc = acc + ext(t)
        vn = np.maximum(v + dt * acc, 0.0)
        # a driver can never occupy the bumper in front of them
        vn = np.minimum(vn, np.maximum(gap - D_MIN * 0.5, 0.0) / dt + vl)
        Ac[k] = (vn - v) / dt
        v = vn
        s = s + dt * v
        S[k + 1], Vv[k + 1] = s, v
    Ac[-1] = Ac[-2]
    return S, Vv, Ac


def ring_run(T=240.0, kick=2.2, kt=6.0, kd=2.5):
    """The Sugiyama ring.  22 cars, evenly spaced, one lane, no obstacle —
    and one driver who lifts off for two and a half seconds at t = 6 s.

    T is generous on purpose: the beat-2 time-lapse burns about 75 s of
    simulation on its own, beat 4 runs on from there, and the spacetime panel
    still needs a clean 60 s window after all of it."""
    s0 = np.arange(N_RING) * SPACING
    v0 = np.full(N_RING, V_EQ)

    def ext(t):
        a = np.zeros(N_RING)
        if kt <= t < kt + kd:
            a[0] = -kick
        return a
    return integrate(N_RING, s0, v0, RING_L, T, ext=ext)


def chain_run(n=7, T=30.0, t0=4.0, width=1.6, depth=1.30, a=0.42, lam=0.05):
    """Beat 3.  The leader eases off ONCE, gently — 1 m/s, about 13%.  Nobody
    else does anything unusual; they just react a beat late, and a beat late
    is enough.  Sluggish sensitivity (a = 0.42) IS the human reaction time."""
    s0 = np.arange(n) * SPACING
    v0 = np.full(n, V_EQ)

    def lead(t):
        return max(V_EQ - depth * math.exp(-((t - t0) / width) ** 2), 0.0)
    return integrate(n, s0, v0, None, T, a=a, lam=lam, leader=lead)


def damper(gap, v, k=0.34, pull=0.14, ref_mul=4.2):
    """The fix, written as a control law: hold a steady speed and a big gap,
    and never chase the car in front.  Let the gap do the absorbing."""
    tgt = min(V_EQ, float(V_opt(np.array(gap))))
    acc = k * (tgt - v)
    ref = ref_mul * H_EQ
    if gap < ref:
        acc += pull * (gap - ref) / ref * max(v, 0.4)
    return float(np.clip(acc, -0.9, 0.5))


def fix_run(n=8, T=40.0, hero=4, pre=5.5, depth=6.5, t0=7.0, width=2.0,
            use_hero=True):
    """Beat 5.  A full stop-and-go enters at the leader and rolls back down the
    line.  `hero` swaps that one driver for the damper — and starts them with
    the gap already open, because you cannot conjure 40 m at the last second."""
    s0 = np.arange(n) * SPACING
    if use_hero:
        s0[:hero + 1] -= pre * H_EQ
    v0 = np.full(n, V_EQ)

    def lead(t):
        return max(V_EQ - depth * math.exp(-((t - t0) / width) ** 2), 0.0)
    return integrate(n, s0, v0, None, T, leader=lead,
                     hero=(hero, damper) if use_hero else None)


def jam_track(S, Vv, L, win=61):
    """Where the jam IS, frame by frame.  Weight each car by how stopped it
    is, take the circular mean, unwrap, smooth.  Measured, never assumed."""
    w = np.clip(1.0 - Vv / max(Vv.max(), 1e-9), 0.0, 1.0) ** 4
    th = 2 * np.pi * (S % L) / L
    ang = np.unwrap(np.arctan2((w * np.sin(th)).sum(1), (w * np.cos(th)).sum(1)))
    arc = ang * L / (2 * np.pi)
    pad = win // 2
    ker = np.ones(win) / win
    return np.convolve(np.r_[np.full(pad, arc[0]), arc, np.full(pad, arc[-1])],
                       ker, 'valid')[:len(arc)]


def measure_wave_speed(S, Vv, L, t0, t1, dt=DT, lag=5.0, nx=460):
    """The number the reel puts on screen, and the only honest way to get it:
    build the velocity field v(x,t) on the ring, cross-correlate slices `lag`
    apart, and read off the shift that lines them up.  Sub-bin refined."""
    x = np.linspace(0, L, nx, endpoint=False)
    step = int(lag / dt)

    def slice_at(k):
        pos = S[k] % L
        idx = np.argsort(pos)
        return np.interp(x, pos[idx], Vv[k][idx], period=L)

    sh = []
    for k in range(int(t0 / dt), int(t1 / dt) - step, int(1.0 / dt)):
        A_ = slice_at(k); B_ = slice_at(k + step)
        A_ = A_ - A_.mean(); B_ = B_ - B_.mean()
        cc = np.fft.irfft(np.fft.rfft(B_) * np.conj(np.fft.rfft(A_)), n=nx)
        m = int(np.argmax(cc))
        y0, y1, y2 = cc[(m - 1) % nx], cc[m], cc[(m + 1) % nx]
        mm = m + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-12)
        if mm > nx / 2:
            mm -= nx
        sh.append(mm * L / nx)
    return float(np.median(sh)) / lag


class Track:
    """A finished simulation, queryable at any continuous sim time."""

    def __init__(self, S, V, A, L=None, dt=DT):
        self.S, self.V, self.A, self.L, self.dt = S, V, A, L, dt
        self.n = S.shape[1]
        self.T = (S.shape[0] - 1) * dt
        self.vmax = float(V.max())
        self.jam = jam_track(S, V, L) if L is not None else None

    def _lerp(self, arr, t):
        f = float(np.clip(t, 0.0, self.T)) / self.dt
        k = int(f)
        k2 = min(k + 1, len(arr) - 1)
        u = f - k
        return arr[k] * (1 - u) + arr[k2] * u

    def at(self, t):
        return self._lerp(self.S, t), self._lerp(self.V, t), self._lerp(self.A, t)

    def car_at(self, i, t):
        return float(self._lerp(self.S[:, i], t))

    def speed_at(self, i, t):
        return float(self._lerp(self.V[:, i], t))

    def jam_at(self, t):
        return float(self._lerp(self.jam, t))

    def gap_at(self, i, t):
        s = self._lerp(self.S, t)
        if self.L is not None:
            return (s[(i + 1) % self.n] - s[i]) % self.L - CAR_L
        lead = s[i + 1] if i + 1 < self.n else s[i] + 1e6
        return lead - s[i] - CAR_L

    def dip_pct(self, i, t_lo, t_hi):
        """How much slower than cruising this car got, as a percentage."""
        k0, k1 = int(t_lo / self.dt), int(t_hi / self.dt)
        return 100.0 * (1.0 - float(self.V[k0:k1, i].min()) / V_EQ)

    def jam_extent(self, t, thresh=0.35):
        """The arc span [lo, hi] actually occupied by stopped cars, so the
        pink band on screen hugs the real cluster instead of a guessed width."""
        s, v, _ = self.at(t)
        stop = v < thresh * V_EQ
        if not stop.any():
            return None
        if self.L is None:
            return float(s[stop].min()) - CAR_L, float(s[stop].max())
        c = self.jam_at(t)
        d = (s - c + self.L / 2) % self.L - self.L / 2
        return float(c + d[stop].min() - CAR_L), float(c + d[stop].max())


# ══════════════════════════════════════════════════════════════════════════
#  THE CUE SHEET — the voice-over IS the timeline
# ══════════════════════════════════════════════════════════════════════════
WPS = 2.90          # words/second == 174 wpm.  <-- retime the whole reel here.

# (cue, line, numeral weight, trailing pause).  Numerals are weighted because
# "22" and "2008" cost more breath than one word.
SCRIPT = [
    ("A1", "Most traffic jams aren't caused by accidents.", 0, 0.28),
    ("A2", "They're caused by absolutely nothing.", 0, 0.75),
    ("B1", "In 2008, scientists put 22 cars on a circular track "
           "with zero obstacles.", 3, 0.30),
    ("B2", "Within minutes, they jammed entirely on their own.", 0, 3.30),
    ("B3", "Here is why.", 0, 0.60),
    ("C1", "The car ahead taps its brakes.", 0, 0.30),
    ("C2", "Because of human reaction time, you brake a little late "
           "and a little harder to stay safe.", 0, 0.25),
    ("C3", "You overcorrect.", 0, 0.45),
    ("C4", "Stack that down the line.", 0, 0.30),
    ("C5", "Car by car, the braking gets harder until a tiny tap "
           "amplifies into a dead stop.", 0, 0.70),
    ("D1", "When roads get too dense, cars stop acting like vehicles "
           "and start acting like a gas.", 0, 0.30),
    ("D2", "Squeeze it, and you get a shockwave.", 0, 0.40),
    ("D3", "Watch closely: the cars crawl forward, but the jam itself "
           "travels backward at 12 miles an hour.", 1, 0.55),
    ("D4", "You aren't stuck in a line.", 0, 0.30),
    ("D5", "You're standing inside a wave.", 0, 0.70),
    ("E1", "But waves can be killed.", 0, 0.35),
    ("E2", "Stop tailgating.", 0, 0.35),
    ("E3", "Leave one large, steady gap ahead of you to absorb the surge, "
           "and you erase the wave for everyone behind you.", 0, 0.55),
    ("E4", "Follow The Physics Frame to outsmart the road, because...", 0, 0.35),
    ("F1", "...most traffic jams aren't caused by accidents.", 0, 0.0),
]


class Cue:
    __slots__ = ("name", "text", "t_in", "t_out", "pause")

    def __init__(self, name, text, t_in, dur, pause):
        self.name, self.text = name, text
        self.t_in, self.t_out, self.pause = t_in, t_in + dur, pause

    @property
    def dur(self):
        return self.t_out - self.t_in

    @property
    def end(self):
        """Out point plus the breath after it — where the next beat may begin."""
        return self.t_out + self.pause


def _build_cues():
    cues, t = {}, 0.0
    for name, text, extra, pause in SCRIPT:
        d = (len(text.split()) + extra) / WPS
        cues[name] = Cue(name, text, t, d, pause)
        t += d + pause
    return cues, t


CUE, REEL_LEN = _build_cues()


def print_cue_sheet():
    def ms(x):
        return f"{int(x)//60}:{x % 60:05.2f}"
    print("\n" + "=" * 68)
    print(f"  PHANTOM JAM — cue sheet @ {WPS*60:.0f} wpm   TOTAL {ms(REEL_LEN)}")
    print("=" * 68)
    for name, _, _, _ in SCRIPT:
        c = CUE[name]
        print(f"  {name}  {ms(c.t_in):>8} -> {ms(c.t_out):>8}  "
              f"({c.dur:5.2f}s +{c.pause:.2f})  {c.text[:44]}")
    print("=" * 68 + "\n")


# ══════════════════════════════════════════════════════════════════════════
#  DRAWING VOCABULARY
# ══════════════════════════════════════════════════════════════════════════
def serif(s, color=STARLIGHT, size=T_CAPTION, italic=True, weight=NORMAL):
    """The channel's idea voice: Spectral, italic by default."""
    return Text(s, font=SERIF, slant=ITALIC if italic else NORMAL,
                weight=weight, font_size=size, color=color)


def mono(s, color=DUST, size=T_LABEL):
    """Labels and metadata only — never an idea."""
    return Text(s, font=MONO, font_size=size, color=color)


def fit_w(mob, w=SAFE_W):
    if mob.width > w:
        mob.scale_to_fit_width(w)
    return mob


def plated(mob, opacity=PLATE_OPACITY, z=TEXT_Z, pad=0.15):
    """Copy sits on its own plate, lifted above the art, so a lane line or a
    brake light can never cut through a glyph.  Size the text BEFORE calling."""
    plate = RoundedRectangle(
        width=mob.width + pad, height=mob.height + pad, corner_radius=0.06,
        fill_color=VOID, fill_opacity=opacity, stroke_width=0,
    ).move_to(mob.get_center())
    g = VGroup(plate, mob)
    g.set_z_index(z)
    plate.set_z_index(z)
    mob.set_z_index(z + 1)
    return g


def line(text, y=Y_CAPTION, color=STARLIGHT, size=T_CAPTION, w=SAFE_W,
         italic=True, weight=BOLD):
    """One idea, one slot.  Every display line in the reel comes through here,
    which is why nothing ever changes size or drifts out of the safe area."""
    return plated(fit_w(serif(text, color, size, italic, weight), w)
                  .move_to([0, y, 0]))


def tag(text, pos, color=DUST, size=T_LABEL, w=3.2):
    p = pos if len(pos) == 3 else [pos[0], pos[1], 0]
    return plated(fit_w(mono(text, color, size), w).move_to(p))


def equation(parts, y=Y_METRIC, w=3.3, size=T_CAPTION - 4):
    """Equations are Text, never MathTex — the series has no LaTeX dependency
    and the serif italic IS the equation voice.  `parts` is [(str, colour)],
    so one term can be pigmented without splitting the line."""
    g = VGroup(*[serif(s, c, size, italic=True) for s, c in parts])
    g.arrange(RIGHT, buff=0.075, aligned_edge=DOWN)
    return plated(fit_w(g, w).move_to([0, y, 0]))


def kph(v):
    return f"{v * MPS_KPH:.0f} km/h"


# ══════════════════════════════════════════════════════════════════════════
#  CAR SPRITE — baked in metres, transformed exactly, never rebuilt
# ══════════════════════════════════════════════════════════════════════════
CAR_W = 1.90            # m, real width
WIDTH_EXAG = 1.55       # the ONE distortion in the reel: lateral scale only.
                        # Gaps — the thing the video is about — stay exact.
LANE_W = 3.60           # m


def _outline(l, w):
    """A top-down silhouette with a tapered nose, so which way a car faces —
    and therefore which way it is going — is readable at 40 pixels."""
    hw, hl = w / 2, l / 2
    p = [(0.00, 1.00), (0.34, 0.88), (0.88, 0.48), (1.00, 0.00),
         (0.96, -0.64), (0.78, -0.96), (0.00, -1.00),
         (-0.78, -0.96), (-0.96, -0.64), (-1.00, 0.00),
         (-0.88, 0.48), (-0.34, 0.88)]
    return [np.array([x * hw, y * hl, 0.0]) for x, y in p]


class CarSprite(VGroup):
    """One vehicle, built once at true size in metres and pointing +Y.

    place() applies a single exact affine transform to baked control points,
    so there is no accumulated rotate/shift drift and no per-frame allocation.
    Body colour reads speed and the lamps read deceleration — both driven
    straight from the simulation, never hand-set.
    """

    def __init__(self, base=DUST, detail=True):
        w = CAR_W * WIDTH_EXAG
        glow = RoundedRectangle(width=w * 1.5, height=CAR_L * 0.40,
                                corner_radius=CAR_L * 0.18, stroke_width=0,
                                fill_color=C_ANGLE, fill_opacity=0.0)
        glow.move_to(DOWN * CAR_L * 0.50)
        pts = _outline(CAR_L, w)
        body = VMobject(stroke_width=1.3, stroke_color=STARLIGHT)
        body.set_points_smoothly(pts + [pts[0]])
        body.set_fill(base, 0.95).set_stroke(opacity=0.4)
        lamp = RoundedRectangle(width=w * 0.24, height=CAR_L * 0.075,
                                corner_radius=CAR_L * 0.03, stroke_width=0,
                                fill_color=C_ANGLE, fill_opacity=0.0)
        lampL = lamp.copy().move_to([-w * 0.27, -CAR_L * 0.40, 0])
        lampR = lamp.copy().move_to([w * 0.27, -CAR_L * 0.40, 0])
        parts = [glow, body]
        if detail:
            cab = RoundedRectangle(width=w * 0.54, height=CAR_L * 0.30,
                                   corner_radius=CAR_L * 0.06, stroke_width=0,
                                   fill_color=VOID, fill_opacity=0.45)
            cab.move_to(UP * CAR_L * 0.04)
            nose = RoundedRectangle(width=w * 0.58, height=CAR_L * 0.05,
                                    corner_radius=CAR_L * 0.02, stroke_width=0,
                                    fill_color=STARLIGHT, fill_opacity=0.0)
            nose.move_to(UP * CAR_L * 0.42)
            parts += [cab, nose]
            self.cab, self.nose = cab, nose
        else:
            self.cab = self.nose = None
        parts += [lampL, lampR]
        super().__init__(*parts)
        self.glow, self.body, self.lampL, self.lampR = glow, body, lampL, lampR
        self.base = base
        self._baked = [(sm, sm.get_points().copy())
                       for sm in self.family_members_with_points()]
        self._M = None
        self._key = None

    def place(self, pos, ang, k):
        """pos = screen point, ang = heading, k = screen units per metre."""
        key = (round(ang, 6), round(k, 7))
        if key != self._key:
            c, s = math.cos(ang), math.sin(ang)
            self._M = np.array([[c * k, s * k, 0.0],
                                [-s * k, c * k, 0.0],
                                [0.0, 0.0, 1.0]])          # already transposed
            self._key = key
        for sm, base in self._baked:
            sm.set_points(base @ self._M + pos)
        return self

    def style(self, v, a, base=None, visible=True, brake=1.0, fade=1.0):
        """v is compared against V_EQ — the CRUISING speed, not the fastest
        speed in the run: a car doing the normal speed of traffic must look
        normal, or the whole colour channel lies."""
        if not visible or fade <= 1e-3:
            self.set_opacity(0.0)
            return self
        base = self.base if base is None else base
        f = float(v / V_EQ)
        if f >= 1.0:                       # running free, ahead of the pack
            col = interpolate_color(ManimColor(base), ManimColor(STARLIGHT),
                                    min((f - 1.0) / 0.60, 1.0))
        else:                              # slowing — the disturbance itself
            col = interpolate_color(ManimColor(base), ManimColor(C_ANGLE),
                                    min((1.0 - f) * 1.15, 1.0))
        f = float(np.clip(f, 0.0, 1.0))
        self.body.set_fill(col, 0.95 * fade)
        self.body.set_stroke(col, 1.3, 0.45 * fade)
        lit = float(np.clip(-a / brake, 0.0, 1.0))
        if f < 0.10:                       # stopped cars keep their lamps lit
            lit = 1.0
        self.lampL.set_fill(C_ANGLE, (0.10 + 0.90 * lit) * fade)
        self.lampR.set_fill(C_ANGLE, (0.10 + 0.90 * lit) * fade)
        self.glow.set_fill(C_ANGLE, 0.45 * lit * fade)
        if self.cab is not None:
            self.cab.set_fill(VOID, 0.45 * fade)
            self.nose.set_fill(STARLIGHT, 0.5 * f ** 2 * fade)
        return self


# ══════════════════════════════════════════════════════════════════════════
#  ROAD — maps metres of arc onto the screen.  One object owns the world.
# ══════════════════════════════════════════════════════════════════════════
class Road:
    """The road, its lane markings, its cars and its jam, all placed from one
    simulation.

    `anchor` is the arc position (metres) pinned to screen y = `y_off`.  Move
    the anchor and you have changed reference frame — and the road scrolls,
    because the lane dashes live in arc coordinates too.  That is the whole
    trick of the frames beat, and it is why the jam can be made to stand still.

    `upm` (screen units per metre) is the zoom.  Cars, dashes and gaps all
    scale through it, so the camera never has to move — which is what keeps
    the copy fixed in the safe area all reel.
    """

    DASH_PITCH = 9.0        # m — realistic lane marking cadence
    DASH_LEN = 3.2          # m

    def __init__(self, scene, track, *, clock=None, upm=0.11, ring_r=1.60,
                 ring_c=(0.0, 0.22), base=DUST, detail=True, cx=0.0, n_dash=30):
        self.scene, self.track = scene, track
        self.clock = clock if clock is not None else scene.clock_ring
        self.squash = None          # (lo_fn, hi_fn, factor) — display only
        self.cx = cx
        self.ring_r = ring_r
        self.ring_c = np.array([ring_c[0], ring_c[1], 0.0])
        self.anchor = ValueTracker(0.0)
        self.y_off = ValueTracker(0.0)
        self.upm = ValueTracker(upm)
        self.bend = ValueTracker(0.0)        # 0 = straight, 1 = closed ring
        self.fade = ValueTracker(1.0)        # whole-world dissolve
        self.jam_glow = ValueTracker(0.0)    # opacity of the measured jam band
        self.brake = 1.0                     # m/s^2 that fully lights a lamp
        self.colour_override = {}            # car index -> colour or callable
        self._anchor_fn = None
        self._blend = None

        # the straight road's two edges; their separation is re-derived every
        # frame from `upm`, so a zoom widens the lane exactly as much as it
        # lengthens the car
        self.rails = VGroup(*[
            Line([cx, 4.7, 0], [cx, -4.7, 0], stroke_color=CYAN,
                 stroke_width=2.4, stroke_opacity=0.40) for _ in (0, 1)])
        # the ring only ever appears at one scale, so its edges are constants
        self.ring_upm = (2 * math.pi * ring_r / track.L) if track.L else 0.0
        rh = LANE_W / 2 * WIDTH_EXAG * self.ring_upm
        self.ring = VGroup(*[
            Circle(radius=ring_r + sgn * rh, color=CYAN, stroke_width=2.2,
                   stroke_opacity=0.0, fill_opacity=0.0).move_to(self.ring_c)
            for sgn in (-1, 1)])

        self.n_dash = n_dash
        self.dashes = VGroup(*[
            Line(ORIGIN, UP * 0.3, stroke_color=CYAN, stroke_width=3.0,
                 stroke_opacity=0.0) for _ in range(n_dash)])

        # the jam, drawn as the measured cluster it is (straight-road form)
        self.band = RoundedRectangle(width=1.0, height=1.0, corner_radius=0.16,
                                     stroke_width=0, fill_color=C_ANGLE,
                                     fill_opacity=0.0)
        self.band.set_z_index(ART_Z - 1)
        self._band_pts = self.band.get_points().copy()   # unit box, centred

        self.cars = VGroup(*[CarSprite(base, detail) for _ in range(track.n)])
        self.group = VGroup(self.rails, self.ring, self.dashes, self.band,
                            self.cars)
        self.group.set_z_index(ART_Z)
        self._updater = lambda m, dt: self.sync()

    # ---- geometry --------------------------------------------------------
    def _delta(self, s, anchor):
        if self.track.L:
            return (s - anchor + self.track.L / 2) % self.track.L - self.track.L / 2
        return s - anchor

    def _squash(self, d, anchor):
        """Display-only compression of ONE stretch of empty road.

        The absorbing gap in the last beat is 39 m — nine car lengths — and at
        a zoom where nine car lengths fit on a phone, a car is 30 px wide.  So
        that one gap is drawn short while every other spacing stays exact, and
        it is labelled with its true length in metres, live off the sim.  It
        is the only place in the reel where a distance is not to scale, and it
        says so on screen."""
        if self.squash is None:
            return d
        lo_fn, hi_fn, f = self.squash
        t = self.clock.t.get_value()
        lo, hi = lo_fn(t) - anchor, hi_fn(t) - anchor
        span = max(hi - lo, 0.0)
        if d <= lo:
            return d
        if d >= hi:
            return d - span * (1.0 - f)
        return lo + (d - lo) * f

    @staticmethod
    def _edge(y):
        """Cars do not vanish at the edge of the reading zone, they dissolve
        into it — which is what keeps the subtitle band clean without the
        road looking guillotined."""
        if y > ART_TOP:
            return max(0.0, 1.0 - (y - ART_TOP) / 0.50)
        if y < ART_BOT:
            return max(0.0, 1.0 - (ART_BOT - y) / 0.50)
        return 1.0

    def anchor_value(self):
        """Which arc position is pinned to the screen right now.  Evaluated
        every frame from a function of sim time, because a bare ValueTracker
        never runs its updaters unless it is in the scene."""
        t = self.clock.t.get_value()
        if self._blend is not None:
            src, tgt, w = self._blend
            ww = float(np.clip(w.get_value(), 0.0, 1.0))
            return (1 - ww) * src(t) + ww * tgt(t)
        if self._anchor_fn is not None:
            return self._anchor_fn(t)
        return self.anchor.get_value()

    def pos_ang(self, s, anchor=None, upm=None, bend=None):
        """Arc position in metres -> (screen point, heading), honouring bend."""
        a = self.anchor_value() if anchor is None else anchor
        k = self.upm.get_value() if upm is None else upm
        b = self.bend.get_value() if bend is None else bend
        d = self._squash(self._delta(s, a), a)
        straight = np.array([self.cx, self.y_off.get_value() + d * k, 0.0])
        if b <= 1e-4 or not self.track.L:
            return straight, 0.0
        th = math.pi / 2 - 2 * math.pi * d / self.track.L     # clockwise = forward
        ringp = self.ring_c + self.ring_r * np.array([math.cos(th),
                                                      math.sin(th), 0.0])
        return (1 - b) * straight + b * ringp, b * (th - math.pi)

    # ---- per-frame refresh ----------------------------------------------
    def sync(self):
        t = self.clock.t.get_value()
        s, v, a = self.track.at(t)
        upm = self.upm.get_value()
        fade = float(np.clip(self.fade.get_value(), 0.0, 1.0))
        anc = self.anchor_value()
        b = self.bend.get_value()

        for i, car in enumerate(self.cars):
            p, ang = self.pos_ang(s[i], anc, upm, b)
            ov = self.colour_override.get(i)
            if callable(ov):
                ov = ov()
            e = 1.0 if b > 0.02 else self._edge(p[1])
            car.place(p, ang, upm)
            car.style(v[i], a[i], base=ov, brake=self.brake, fade=fade * e,
                      visible=e > 0.02 and abs(p[0]) < 2.6)

        # lane dashes live in arc coordinates too, so they scroll with the road
        base_k = int(math.floor(anc / self.DASH_PITCH)) - self.n_dash // 2
        for j, dash in enumerate(self.dashes):
            arc = (base_k + j) * self.DASH_PITCH
            p0, _ = self.pos_ang(arc, anc, upm, b)
            e = 1.0 if b > 0.02 else self._edge(p0[1])
            if e <= 0.02 or abs(p0[0]) > 2.6:
                dash.set_stroke(opacity=0.0)
                continue
            p1, _ = self.pos_ang(arc + self.DASH_LEN, anc, upm, b)
            dash.set_stroke(opacity=0.5 * fade * e * (1 - b) ** 1.5)
            if np.linalg.norm(p1 - p0) > 1e-6:
                dash.put_start_and_end_on(p0, p1)

        # the jam band — straight-road form only; on the ring the cluster is
        # already unmistakable and a second marker would be noise
        g = float(np.clip(self.jam_glow.get_value(), 0.0, 1.0)) * fade * (1 - b)
        ext = self.track.jam_extent(t) if g > 1e-3 else None
        if ext is None:
            self.band.set_fill(opacity=0.0)
        else:
            lo, _ = self.pos_ang(ext[0], anc, upm, b)
            hi, _ = self.pos_ang(ext[1], anc, upm, b)
            y_lo = float(np.clip(min(lo[1], hi[1]), ART_BOT, ART_TOP))
            y_hi = float(np.clip(max(lo[1], hi[1]), ART_BOT, ART_TOP))
            lo, hi = np.array([0, y_lo, 0.0]), np.array([0, y_hi, 0.0])
            h = max(abs(hi[1] - lo[1]), 1e-3) + 0.22
            w = LANE_W * WIDTH_EXAG * upm + 0.34
            c = np.array([self.cx, 0.5 * (lo[1] + hi[1]), 0.0])
            self.band.set_points(self._band_pts * np.array([w, h, 1.0]) + c)
            self.band.set_fill(C_ANGLE, 0.17 * g)

        half = LANE_W / 2 * WIDTH_EXAG * upm
        self.rails[0].move_to([self.cx - half, 0, 0])
        self.rails[1].move_to([self.cx + half, 0, 0])
        self.rails.set_stroke(opacity=0.40 * (1 - b) ** 1.2 * fade)
        self.ring.set_stroke(opacity=0.42 * b ** 2.5 * fade)

    # ---- lifecycle -------------------------------------------------------
    def start(self):
        self.sync()
        self.scene.add(self.group)
        self.group.add_updater(self._updater)
        return self

    def stop(self):
        self.group.remove_updater(self._updater)
        return self

    # ---- reference-frame control ----------------------------------------
    def set_anchor_fn(self, fn):
        self._anchor_fn = fn
        self._blend = None
        return self

    def freeze_anchor(self):
        """Capture whatever the frame is following, THEN release it."""
        self.anchor.set_value(self.anchor_value())
        self._anchor_fn = None
        self._blend = None
        return self

    def lock(self, target_fn, blend):
        """Hand the frame over from whatever it follows now to target_fn(t).
        `blend` is a 0->1 ValueTracker you animate, so a change of reference
        frame is a real camera move and not a cut."""
        src = self._anchor_fn
        if src is None:
            frozen = self.anchor_value()

            def src(t, _f=frozen):
                return _f
        self._blend = (src, target_fn, blend)
        self._anchor_fn = target_fn
        return self


# ══════════════════════════════════════════════════════════════════════════
#  DENSITY ANNULUS — "cars stop acting like vehicles and start acting like a gas"
# ══════════════════════════════════════════════════════════════════════════
class DensityRing:
    """A ring of radial ticks whose length is the LOCAL DENSITY of cars,
    measured in a +-window around each bin.  It is the same 22 cars, counted
    instead of drawn — which is exactly what it means to treat traffic as a
    fluid.  The lump that forms is the compression the script calls a squeeze.
    """

    def __init__(self, road, n=84, win=9.0, gap=0.10, max_len=0.52):
        self.road, self.n, self.win = road, n, win
        self.gap, self.max_len = gap, max_len
        self.rho_jam = 1.0 / (CAR_L + D_MIN)          # bumper-to-bumper
        self.fade = ValueTracker(0.0)
        self.arcs = np.arange(n) * road.track.L / n
        self.ticks = VGroup(*[
            Line(ORIGIN, RIGHT * 0.01, stroke_color=DUST, stroke_width=3.4,
                 stroke_opacity=0.0) for _ in range(n)])
        self.ticks.set_z_index(ART_Z + 1)
        self._updater = lambda m, dt: self.sync()

    def sync(self):
        rd = self.road
        L = rd.track.L
        t = rd.clock.t.get_value()
        s, _, _ = rd.track.at(t)
        f = float(np.clip(self.fade.get_value(), 0.0, 1.0))
        if f <= 1e-3:
            self.ticks.set_stroke(opacity=0.0)
            return
        # |distance| from every bin to every car, on the ring  (n x N_RING)
        d = np.abs((s[None, :] - self.arcs[:, None] + L / 2) % L - L / 2)
        rho = (d < self.win).sum(1) / (2 * self.win)
        frac = np.clip(rho / self.rho_jam, 0.0, 1.0)
        anc = rd.anchor_value()
        b = rd.bend.get_value()
        for j, tick in enumerate(self.ticks):
            th = math.pi / 2 - 2 * math.pi * rd._delta(self.arcs[j], anc) / L
            u = np.array([math.cos(th), math.sin(th), 0.0])
            r0 = rd.ring_r - self.gap
            ln = 0.05 + self.max_len * frac[j] ** 1.6
            tick.put_start_and_end_on(rd.ring_c + r0 * u,
                                      rd.ring_c + (r0 - ln) * u)
            hot = float(np.clip((frac[j] - 0.42) / 0.40, 0.0, 1.0))
            tick.set_stroke(
                interpolate_color(ManimColor(CYAN), ManimColor(C_ANGLE), hot),
                3.4, (0.30 + 0.62 * hot) * f * b ** 2)

    def start(self):
        self.sync()
        self.road.scene.add(self.ticks)
        self.ticks.add_updater(self._updater)
        return self

    def stop(self):
        self.ticks.remove_updater(self._updater)
        return self


# ══════════════════════════════════════════════════════════════════════════
#  SPACETIME PANEL — the whole argument in one static picture
# ══════════════════════════════════════════════════════════════════════════
def spacetime_panel(track, t0, t1, w=3.30, h=2.42, y=ART_MID + 0.06, step=0.30):
    """Every car's world line: position across, time DOWNWARD.

    Each thin line is one driver.  They all lean one way — forward.  The band
    where they bunch up leans the other way, and its slope is the wave speed.
    Nothing here is drawn by hand; it is the same array the cars were placed
    from, plotted instead of animated.
    """
    L = track.L
    x0, y0 = -w / 2, y + h / 2
    ks = np.arange(int(t0 / track.dt), int(t1 / track.dt) + 1,
                   max(1, int(step / track.dt)))
    ts = ks * track.dt

    def px(arc, t):
        return np.array([x0 + (arc % L) / L * w,
                         y0 - (t - t0) / (t1 - t0) * h, 0.0])

    def polyline(arc_series, colour, width, opacity):
        """Break the line wherever it wraps around the ring, so a car never
        appears to teleport backwards across the panel."""
        g = VGroup()
        run = [px(arc_series[0], ts[0])]
        for i in range(1, len(ts)):
            if abs((arc_series[i] % L) - (arc_series[i - 1] % L)) > L / 2:
                if len(run) > 1:
                    g.add(VMobject().set_points_as_corners(run))
                run = []
            run.append(px(arc_series[i], ts[i]))
        if len(run) > 1:
            g.add(VMobject().set_points_as_corners(run))
        g.set_stroke(colour, width, opacity)
        return g

    frame = Rectangle(width=w + 0.22, height=h + 0.22, stroke_color=DUST,
                      stroke_width=1.4, stroke_opacity=0.30,
                      fill_color=PANEL, fill_opacity=0.55).move_to([0, y, 0])
    lines = VGroup(*[polyline(track.S[ks, i], DUST, 1.8, 0.62)
                     for i in range(track.n)])
    jam = polyline(track.jam[ks], C_ANGLE, 7.0, 0.85)

    ax_x = mono("position along the road  \u2192", DUST, T_MICRO)
    ax_x.next_to(frame, DOWN, buff=0.10)
    ax_y = mono("time \u2193", DUST, T_MICRO).rotate(PI / 2)
    ax_y.next_to(frame, LEFT, buff=0.08)

    axes = VGroup(ax_x, ax_y)
    g = VGroup(frame, lines, jam, axes)
    g.set_z_index(ART_Z + 4)
    frame.set_z_index(ART_Z + 3)
    return frame, lines, jam, axes


# ══════════════════════════════════════════════════════════════════════════
#  CLOCK — sim time advances itself, so time is never eased
# ══════════════════════════════════════════════════════════════════════════
class Clock:
    """A simulation clock driven by an updater at a controlled rate.

    v1 moved sim time with `play(simt.animate.set_value(x), rate_func=smooth)`,
    which eases TIME — traffic accelerated into a beat and decelerated out of
    it for reasons the physics never asked for.  Here the only thing that ever
    eases is the RATE, which reads as a camera decision (a time-lapse, a
    rewind) rather than as cars behaving strangely.
    """

    def __init__(self, scene, t0=0.0):
        self.t = ValueTracker(t0)
        self.rate = ValueTracker(0.0)
        self.t.add_updater(lambda m, dt: m.increment_value(dt * self.rate.get_value()))
        scene.add(self.t)


class Gauge(VGroup):
    """The hero car's speedometer, read straight off the simulation.  A bar
    rather than a number: no font is rasterised per frame, and a phone reads
    a falling bar faster than it reads falling digits.  The cyan tick is the
    cruising speed, so 'slower than everyone else' is visible, not inferred."""

    def __init__(self, clock, track, idx, x=-1.58, y=ART_MID, h=1.20):
        shell = RoundedRectangle(width=0.20, height=h, corner_radius=0.07,
                                 stroke_color=DUST, stroke_width=1.6,
                                 stroke_opacity=0.5, fill_color=VOID,
                                 fill_opacity=0.0).move_to([x, y, 0])
        fill = Rectangle(width=0.11, height=1.0, stroke_width=0,
                         fill_color=STARLIGHT, fill_opacity=0.92)
        y_cr = y - h / 2 + h * V_EQ / V_FREE
        cruise = Line([x - 0.17, y_cr, 0], [x + 0.17, y_cr, 0],
                      stroke_color=CYAN, stroke_width=2.0, stroke_opacity=0.75)
        lbl = fit_w(mono("SPEED", DUST, T_MICRO), 0.60).next_to(shell, UP, buff=0.10)
        super().__init__(shell, fill, cruise, lbl)
        self.fill, self.x, self.y, self.h = fill, x, y, h
        self.clock, self.track, self.idx = clock, track, idx
        self._fpts = fill.get_points().copy()
        self.set_z_index(TEXT_Z)
        self.sync()
        self.add_updater(lambda m, dt: m.sync())

    def sync(self):
        v = self.track.speed_at(self.idx, self.clock.t.get_value())
        f = float(np.clip(v / V_FREE, 0.0, 1.0))
        hh = max(self.h * f, 1e-3)
        c = np.array([self.x, self.y - self.h / 2 + hh / 2, 0.0])
        self.fill.set_points(self._fpts * np.array([1.0, hh, 1.0]) + c)
        self.fill.set_fill(interpolate_color(ManimColor(C_ANGLE),
                                             ManimColor(STARLIGHT), f), 0.92)


def pick_hook(track, span=5.0, lead_in=4.5, t_lo=60.0, t_hi=165.0):
    """Choose, from the run itself, a driver who is cruising freely and is
    about to be swallowed — so the opening shot is found in the simulation
    rather than staged on top of it.  Also guarantees `lead_in` seconds of
    clean cruising before the shot starts, which is what the closing loop
    replays to land back on frame zero."""
    V, dt = track.V, track.dt
    best, score = None, -1e9
    for i in range(track.n):
        fast = False
        for k in range(int(t_lo / dt), int(t_hi / dt)):
            if V[k, i] > 0.97 * V_EQ:
                fast = True
            elif fast and V[k, i] < 0.04 * V_EQ:
                fast = False
                k0 = k - int(span / dt)
                kp = k0 - int(lead_in / dt)
                if kp < 0:
                    continue
                w = V[kp:k0 + 1, i]
                if w.min() < 0.85 * V_EQ:
                    continue
                if float(w.mean()) > score:
                    score, best = float(w.mean()), (i, k0 * dt)
    return best if best is not None else (0, t_lo)


RING_R = 1.60
RING_C = (0.0, 0.22)
RING_UPM = 2 * math.pi * RING_R / RING_L


# ══════════════════════════════════════════════════════════════════════════
class PhantomJamReel(Scene):
    """One continuous vertical reel, five beats, one idea: a phantom jam is a
    wave made of cars, it travels backward through them, and one driver with
    one big gap can absorb it.

    There are no camera moves anywhere in this file.  "Zoom" is the world's
    metres-per-unit, so copy never changes size, never leaves the safe area,
    and the subtitle band at y = -2 stays empty from the first frame to the
    last.
    """

    HOOK_SPAN = 5.0
    HOOK_LAND = 4.35        # wall-clock second the hero car comes to rest

    # ---- wall-clock plumbing --------------------------------------------
    def hold(self, d):
        if d > 1e-4:
            self.wait(d)
            self.wall += d

    def anim(self, *a, run_time=1.0, **kw):
        self.play(*a, run_time=run_time, **kw)
        self.wall += run_time

    def until(self, t):
        self.hold(t - self.wall)

    def say(self, name):
        """Sit on the cue's in-point and fire its subtitle.  Every beat below
        is written against these, so the picture cannot drift off the voice."""
        c = CUE[name]
        self.until(c.t_in)
        self.add_subcaption(c.text, duration=c.dur)
        return c

    def schedule(self, ck, sim_target, wall_target):
        """Pick the constant rate that puts the sim at `sim_target` exactly
        when the wall clock reaches `wall_target`.  Instant, because it is
        only ever called on a cut or under a dissolve."""
        w = max(wall_target - self.wall, 1e-3)
        ck.rate.set_value((sim_target - ck.t.get_value()) / w)

    def ease_rate(self, ck, r, over=0.6):
        self.anim(ck.rate.animate.set_value(r), run_time=over, rate_func=EASE)

    def swap(self, old, new, over=0.55):
        """Cross-dissolve one world for another and retire the old one."""
        self.anim(old.fade.animate.set_value(0.0),
                  new.fade.animate.set_value(1.0), run_time=over)
        old.stop()
        self.remove(old.group)

    # ---- build ----------------------------------------------------------
    def construct(self):
        print_cue_sheet()
        self.wall = 0.0
        self.clock_ring = Clock(self)
        self.clock_alt = Clock(self)

        self.ring_tr = Track(*ring_run(), L=RING_L)
        self.wave_ms = measure_wave_speed(self.ring_tr.S, self.ring_tr.V,
                                          RING_L, 30.0, 160.0)
        self.wave_mph = abs(self.wave_ms) * MPS_MPH
        self.hook_car, self.hook_t0 = pick_hook(self.ring_tr, self.HOOK_SPAN)
        print(f"[sim] cruise {V_EQ:.2f} m/s ({V_EQ*MPS_KPH:.0f} km/h) | "
              f"free {V_FREE:.2f} m/s | jam wave {self.wave_ms:.2f} m/s = "
              f"{self.wave_mph:.1f} mph backward")
        print(f"[sim] hook: car {self.hook_car} from t={self.hook_t0:.1f}s\n")

        self.beat1_hook()
        self.beat2_ring()
        self.beat3_cascade()
        self.beat4_wave()
        self.beat5_fix()
        self.beat6_loop()

    # ============================================= BEAT 1 · 0:00–0:05 =====
    def beat1_hook(self):
        """Ride one car at cruising speed down an open road, then let it run
        into something that is not there.  One continuous shot of the
        simulation; nothing is placed, nothing is faked."""
        tr, ck = self.ring_tr, self.clock_ring
        ck.t.set_value(self.hook_t0)
        hw = Road(self, tr, clock=ck, upm=0.132, ring_r=RING_R, ring_c=RING_C)
        self.hw_ring = hw
        hw.brake = 1.8
        hw.set_anchor_fn(lambda t: tr.car_at(self.hook_car, t))
        hw.y_off.set_value(ART_BOT + 0.62)
        hw.start()
        gauge = Gauge(ck, tr, self.hook_car)
        self.add(gauge)
        self.schedule(ck, self.hook_t0 + self.HOOK_SPAN, self.HOOK_LAND)

        self.say("A1")
        self.hold(1.15)
        # the pull-back: the wall was always there, we just could not see it
        self.anim(hw.upm.animate.set_value(0.058),
                  hw.y_off.animate.set_value(ART_BOT + 0.34),
                  run_time=1.40, rate_func=EASE)
        self.say("A2")
        self.until(self.HOOK_LAND)

        hook = line("Nothing", Y_TITLE, STARLIGHT, T_DISPLAY)
        self.anim(FadeIn(hook, shift=DOWN * 0.10), run_time=IN_T, rate_func=POP)
        self.until(CUE["A2"].end - OUT_T)
        gauge.clear_updaters()
        self.anim(FadeOut(hook), FadeOut(gauge), run_time=OUT_T)

    # ============================================= BEAT 2 · 0:05–0:15 =====
    def beat2_ring(self):
        """Wind it back and close the road into a loop, so there is nowhere
        left to hide a cause.  22 cars, one lane, no obstacle.  One driver
        lifts off for two and a half seconds — and the jam builds itself out
        of the other twenty-one."""
        tr, hw, ck = self.ring_tr, self.hw_ring, self.clock_ring
        self.say("B1")

        hw.freeze_anchor()
        self.schedule(ck, 0.0, 6.95)                  # a real scrub, not a cut
        self.anim(hw.bend.animate.set_value(1.0),
                  hw.upm.animate.set_value(RING_UPM),
                  hw.y_off.animate.set_value(RING_C[1] + RING_R),
                  hw.anchor.animate.set_value(0.0),
                  run_time=1.78, rate_func=EASE)
        ck.rate.set_value(0.0)
        hw.brake = 0.9

        self.schedule(ck, 6.0, CUE["B1"].t_out)       # lift-off lands on the line

        # Nobody gets a ring around them.  Singling out the driver who lifts
        # off is the wrong promise for this beat: the whole claim is that
        # twenty-two identical cars with no obstacle jam themselves, so the
        # eye should be on the pack, not on a suspect.

        self.say("B2")
        lapse = tag("time \u00d7 15", [0, Y_METRIC, 0], DUST, T_MICRO, 1.6)
        self.add(lapse)
        self.ease_rate(ck, 15.0, 0.9)                 # "within minutes"
        # THE build, and the one long sweep of the reel.  Two seconds only
        # shows cars bunching; it takes several before the eye accepts that
        # the cluster is a thing which holds its shape and stays put.
        self.until(CUE["B2"].end - 1.55)
        # then come off the gas, so the stopped cars read as stopped rather
        # than as fast cars rendered badly
        self.ease_rate(ck, 2.5, 0.85)
        self.anim(FadeOut(lapse), run_time=0.30)

        self.say("B3")
        self.ease_rate(ck, 3.0, 0.5)
        self.until(CUE["B3"].end - OUT_T - SWAP_T)
        self.ring_resume = ck.t.get_value()
        # headroom guard: everything after this beat keeps running the same
        # ring, and beat 4 still needs a clean 60 s window for the panel
        print(f"[sim] ring beat ends at t={self.ring_resume:.1f}s "
              f"of {tr.T:.0f}s available")
        ck.rate.set_value(0.0)

    # ============================================= BEAT 3 · 0:15–0:33 =====
    def beat3_cascade(self):
        """Zoom in on the mechanism.  One gentle lift-off at the front, and a
        reaction lag of a couple of seconds per car, is enough to turn a 17%
        slowdown into a near-halt six cars back.  The bars are the sim."""
        ck2 = self.clock_alt
        ck2.t.set_value(0.0)
        ck2.rate.set_value(0.0)
        ch = Track(*chain_run(), L=None)
        self.chain_tr = ch
        hw = Road(self, ch, clock=ck2, upm=0.052)
        self.hw_chain = hw
        hw.brake = 0.55
        hw.set_anchor_fn(lambda t: ch.car_at(ch.n // 2, t))
        hw.y_off.set_value(ART_MID)
        hw.fade.set_value(0.0)
        hw.start()
        self.swap(self.hw_ring, hw)

        front, back = ch.n - 1, 0
        lead_lbl = tag("FRONT CAR", [-1.32, 0, 0], DUST, T_MICRO, 1.30)
        you_lbl = tag("YOU", [-1.32, 0, 0], AMBER, T_LABEL, 0.85)

        def pin(m, car):
            m.move_to([-1.32, float(np.clip(car.get_center()[1],
                                            ART_BOT + 0.1, ART_TOP - 0.1)), 0])
        lead_lbl.add_updater(lambda m: pin(m, hw.cars[front]))
        you_lbl.add_updater(lambda m: pin(m, hw.cars[back]))
        hw.colour_override[back] = AMBER

        # live "how much slower than cruising" bars — built once, stretched
        BAR_X, BAR_W = 0.46, 1.35
        bars = VGroup()
        bpts = []
        for _ in range(ch.n):
            b = Rectangle(width=1.0, height=0.17, stroke_width=0,
                          fill_color=C_ANGLE, fill_opacity=0.0)
            bpts.append(b.get_points().copy())
            bars.add(b)
        bars.set_z_index(ART_Z + 2)

        def sync_bars(m):
            _, v, _ = ch.at(ck2.t.get_value())
            for i, b in enumerate(bars):
                frac = float(np.clip(1.0 - v[i] / V_EQ, 0.0, 1.0))
                w = max(frac * BAR_W, 1e-3)
                y = hw.cars[i].get_center()[1]
                if not (ART_BOT < y < ART_TOP):
                    b.set_fill(opacity=0.0)
                    continue
                b.set_points(bpts[i] * np.array([w, 1.0, 1.0])
                             + np.array([BAR_X + w / 2, y, 0.0]))
                b.set_fill(C_ANGLE, 0.28 + 0.62 * min(frac * 2.2, 1.0))
        bars.add_updater(sync_bars)

        self.say("C1")
        self.anim(FadeIn(lead_lbl), FadeIn(you_lbl), run_time=IN_T)
        self.schedule(ck2, 4.0, CUE["C1"].t_out)      # the tap lands on the line
        self.until(CUE["C1"].t_out - 0.30)
        self.ease_rate(ck2, 1.05, 0.30)               # slow down and look

        self.say("C2")
        self.add(bars)
        scale_lbl = tag("how hard each one brakes", [BAR_X + 0.30, Y_METRIC, 0],
                        C_ANGLE, T_MICRO, 2.3)
        self.anim(FadeIn(scale_lbl),
                  run_time=IN_T, rate_func=POP)

        self.until(CUE["C2"].t_in + 2.4)
        self.anim(FadeOut(scale_lbl), run_time=IN_T)

        self.say("C3")

        self.say("C4")
        self.until(CUE["C4"].end)

        # the two numbers, measured out of the run that just played
        self.say("C5")
        top_pct = ch.dip_pct(front, 0.0, ch.T)
        bot_pct = ch.dip_pct(back, 0.0, ch.T)
        top_tag = tag(f"-{round(top_pct)}%", [0, 0, 0], DUST, T_LABEL, 1.0)
        bot_tag = tag(f"-{round(bot_pct)}%", [0, 0, 0], C_ANGLE, T_CAPTION - 6, 1.3)
        top_tag.move_to([BAR_X + top_pct / 100 * BAR_W + 0.32,
                         hw.cars[front].get_center()[1], 0])
        bot_tag.move_to([BAR_X + bot_pct / 100 * BAR_W + 0.36,
                         hw.cars[back].get_center()[1], 0])
        self.anim(FadeIn(top_tag), run_time=IN_T)
        self.anim(FadeIn(bot_tag, scale=0.75), run_time=IN_T, rate_func=POP)
        self.anim(Circumscribe(bot_tag, color=C_ANGLE, buff=0.05), run_time=0.65)
        self.until(CUE["C5"].end - OUT_T - SWAP_T)
        bars.clear_updaters()
        lead_lbl.clear_updaters()
        you_lbl.clear_updaters()
        self.anim(FadeOut(top_tag), FadeOut(bot_tag),
                  FadeOut(lead_lbl), FadeOut(you_lbl), FadeOut(bars),
                  run_time=OUT_T)
        ck2.rate.set_value(0.0)

    # ============================================= BEAT 4 · 0:33–0:53 =====
    def beat4_wave(self):
        """The centrepiece.  Count the cars instead of watching them and the
        fluid appears; then pin the frame to the road, then to the jam.  Same
        simulation, same cars, two reference frames — and the road scrolls
        differently in each, because the lane markings are in road coordinates
        too.  Finally: every world line at once, which is where the backward
        slope stops being a claim and becomes a picture."""
        tr, ck = self.ring_tr, self.clock_ring
        ck.t.set_value(self.ring_resume)
        hw = Road(self, tr, clock=ck, upm=RING_UPM, ring_r=RING_R, ring_c=RING_C)
        self.hw_ring = hw
        hw.brake = 0.9
        hw.bend.set_value(1.0)
        hw.anchor.set_value(0.0)
        hw.y_off.set_value(RING_C[1] + RING_R)
        hw.fade.set_value(0.0)
        hw.start()
        self.swap(self.hw_chain, hw)
        self.schedule(ck, self.ring_resume + 46.0, CUE["D2"].t_out)

        # -- D1: the gas.  Same 22 cars, counted instead of drawn.
        self.say("D1")
        dens = DensityRing(hw).start()
        self.anim(dens.fade.animate.set_value(1.0), run_time=0.7, rate_func=EASE)
        gas = line("Stop counting cars.  Count cars per metre.",
                   Y_TITLE, STARLIGHT, T_CAPTION - 2)
        rho = tag("density  \u2192  a fluid", [0, Y_METRIC, 0], CYAN, T_MICRO, 2.4)
        self.anim(FadeIn(gas, shift=DOWN * 0.08), FadeIn(rho),
                  run_time=IN_T, rate_func=POP)
        self.until(CUE["D1"].end - OUT_T)
        self.anim(FadeOut(gas), FadeOut(rho), run_time=OUT_T)

        # -- D2: the squeeze
        self.say("D2")
        sq = line("Squeeze a fluid and it answers with a shockwave.",
                  Y_TITLE, C_ANGLE, T_CAPTION - 4)
        self.anim(FadeIn(sq, shift=DOWN * 0.08), run_time=IN_T, rate_func=POP)
        self.until(CUE["D2"].end - OUT_T)
        self.anim(FadeOut(sq), dens.fade.animate.set_value(0.0), run_time=OUT_T)
        dens.stop()
        self.remove(dens.ticks)

        # -- D3: unroll, then hand the frame to the jam
        self.say("D3")
        unroll = ValueTracker(0.0)
        hw.lock(lambda t: tr.jam_at(t) + 34.0, unroll)   # jam low in the frame
        self.schedule(ck, ck.t.get_value() + 22.0, CUE["D3"].t_out)
        self.anim(unroll.animate.set_value(1.0),
                  hw.bend.animate.set_value(0.0),
                  hw.upm.animate.set_value(0.058),
                  hw.y_off.animate.set_value(ART_MID),
                  hw.jam_glow.animate.set_value(1.0),
                  run_time=1.45, rate_func=EASE)
        f1 = tag("frame:  the road", [0, Y_TAG, 0], CYAN, T_LABEL, 2.6)
        self.anim(FadeIn(f1), run_time=IN_T)
        self.until(CUE["D3"].t_in + 3.1)

        # THE money shot — the jam sits dead still and the cars pour through it
        lock2 = ValueTracker(0.0)
        hw.lock(lambda t: tr.jam_at(t), lock2)
        f2 = tag("frame:  the jam", [0, Y_TAG, 0], C_ANGLE, T_LABEL, 2.6)
        self.anim(FadeOut(f1), FadeIn(f2), lock2.animate.set_value(1.0),
                  run_time=1.15, rate_func=EASE)
        up = Arrow([1.42, ART_MID - 0.62, 0], [1.42, ART_MID + 0.62, 0],
                   color=STARLIGHT, buff=0, stroke_width=6,
                   max_tip_length_to_length_ratio=0.22).set_z_index(TEXT_Z)
        dn = Arrow([-1.42, ART_MID + 0.62, 0], [-1.42, ART_MID - 0.62, 0],
                   color=C_ANGLE, buff=0, stroke_width=6,
                   max_tip_length_to_length_ratio=0.22).set_z_index(TEXT_Z)
        up_l = tag("cars", [1.42, ART_MID + 0.92, 0], STARLIGHT, T_MICRO, 0.9)
        dn_l = tag("jam", [-1.42, ART_MID + 0.92, 0], C_ANGLE, T_MICRO, 0.9)
        self.anim(GrowArrow(up), GrowArrow(dn), FadeIn(up_l), FadeIn(dn_l),
                  run_time=0.55)
        pour = line("It holds still.  The cars pour through it.",
                    Y_TITLE, STARLIGHT, T_CAPTION - 2)
        self.anim(FadeIn(pour, shift=DOWN * 0.08), run_time=IN_T, rate_func=POP)
        self.until(CUE["D3"].end - OUT_T)
        self.anim(FadeOut(pour), FadeOut(up), FadeOut(dn), FadeOut(up_l),
                  FadeOut(dn_l), FadeOut(f2), run_time=OUT_T)

        # -- D4 / D5: every world line at once
        self.say("D4")
        t_now = ck.t.get_value()
        p0 = float(np.clip(t_now - 8.0, 30.0, tr.T - 62.0))
        frame, lines_, jam, axes = spacetime_panel(tr, p0, p0 + 60.0)
        self.anim(hw.fade.animate.set_value(0.10), FadeIn(frame),
                  run_time=0.45, rate_func=EASE)
        self.ease_rate(ck, 1.0, 0.3)
        self.anim(LaggedStart(*[Create(l) for l in lines_], lag_ratio=0.05),
                  run_time=1.05)
        self.anim(Create(jam), FadeIn(axes), run_time=0.55, rate_func=POP)

        self.say("D5")
        dx = self.wave_ms * 10.0 / RING_L * 3.30      # 10 s of jam travel
        dy = -10.0 / 60.0 * 2.42
        a0 = np.array([0.86, ART_MID + 0.62, 0.0])
        slope = Arrow(a0, a0 + np.array([dx, dy, 0.0]), color=C_ANGLE, buff=0,
                      stroke_width=5, max_tip_length_to_length_ratio=0.28)
        slope.set_z_index(TEXT_Z)
        mph = tag(f"{self.wave_mph:.0f} mph  backward",
                  [0, Y_METRIC, 0], C_ANGLE, T_LABEL, 2.9)
        inside = line("You're standing inside a wave.", Y_TITLE,
                      STARLIGHT, T_DISPLAY)
        self.anim(GrowArrow(slope), FadeIn(mph), run_time=0.5)
        self.anim(FadeIn(inside, shift=DOWN * 0.10), run_time=IN_T, rate_func=POP)
        self.until(CUE["D5"].end - 0.45)
        self.anim(FadeOut(inside), FadeOut(mph), FadeOut(slope),
                  FadeOut(frame), FadeOut(lines_), FadeOut(jam), FadeOut(axes),
                  run_time=0.45)

    # ============================================= BEAT 5 · 0:53–1:07 =====
    def beat5_fix(self):
        """The fix is not a trick, it is a control law: hold a steady speed and
        a big gap, and never chase the car in front.  Same model, one driver
        changed.  The wave that flattens the cars ahead of the gap arrives
        behind it as almost nothing.

        This is the one beat where a distance is not to scale: the absorbing
        gap is drawn at 45% of its true length so that nine car lengths and
        seven cars fit above the subtitle band at a size a phone can read.
        Every other spacing is exact, and the gap is labelled in real metres,
        measured off the run, at both its widest and its tightest."""
        ck2 = self.clock_alt
        ck2.t.set_value(0.0)
        ck2.rate.set_value(0.0)
        HERO = 4
        fx = Track(*fix_run(n=8, hero=HERO), L=None)
        self.fix_tr = fx
        hw = Road(self, fx, clock=ck2, upm=0.047)
        self.hw_fix = hw
        hw.brake = 1.2
        hw.set_anchor_fn(lambda t: fx.car_at(HERO, t))
        hw.y_off.set_value(0.45)
        hw.squash = (lambda t: fx.car_at(HERO, t) + CAR_L,
                     lambda t: fx.car_at(HERO + 1, t), 0.45)
        hw.colour_override[HERO] = AMBER
        hw.fade.set_value(0.0)
        hw.start()

        self.say("E1")
        self.swap(self.hw_ring, hw)
        self.schedule(ck2, 22.0, 64.5)

        # the gap, drawn as the measured thing it is
        rule = VGroup(
            Line(ORIGIN, UP * 0.1, stroke_color=AMBER, stroke_width=2.6,
                 stroke_opacity=0.85),
            Line(LEFT * 0.09, RIGHT * 0.09, stroke_color=AMBER, stroke_width=2.6),
            Line(LEFT * 0.09, RIGHT * 0.09, stroke_color=AMBER, stroke_width=2.6))
        rule.set_z_index(ART_Z + 3)

        def sync_rule(m):
            a = hw.cars[HERO].get_top() + UP * 0.03
            b = hw.cars[HERO + 1].get_bottom() + DOWN * 0.03
            a[0] = b[0] = hw.cx - 0.42
            if b[1] - a[1] > 0.06:
                m[0].put_start_and_end_on(a, b)
                m[1].move_to(a)
                m[2].move_to(b)
                m.set_stroke(opacity=0.85)
            else:
                m.set_stroke(opacity=0.0)
        rule.add_updater(sync_rule)

        g0 = fx.gap_at(HERO, 0.0)
        gap_lbl = tag(f"your gap  \u00b7  {g0:.0f} m", [-1.28, 1.0, 0],
                      AMBER, T_MICRO, 1.55)

        self.say("E2")
        self.add(rule)
        self.anim(FadeIn(rule), FadeIn(gap_lbl), run_time=IN_T, rate_func=POP)

        self.say("E3")
        self.until(CUE["E3"].t_in + 3.0)

        # the gap eats it: the hero closes up instead of stopping
        k_min = int(np.argmin([fx.gap_at(HERO, t) for t in np.arange(0, 24, 0.1)]))
        g_min = fx.gap_at(HERO, k_min * 0.1)
        eaten = line("The gap closes.  The driver does not brake.",
                     Y_TITLE, AMBER, T_CAPTION - 4)
        tight = tag(f"{g_min:.0f} m", [-1.28, 0.72, 0], AMBER, T_MICRO, 0.9)
        self.anim(FadeIn(eaten, shift=DOWN * 0.08),
                  FadeIn(tight), run_time=IN_T, rate_func=POP)
        self.until(CUE["E3"].t_in + 5.4)

        # everything behind the hero never stopped — say so in green
        green = ValueTracker(0.0)

        def green_base():
            return interpolate_color(ManimColor(DUST), ManimColor(C_GROUND),
                                     green.get_value())
        for i in range(HERO):
            hw.colour_override[i] = green_base
        behind = line("Behind that gap, nobody ever stopped.",
                      Y_TITLE, C_GROUND, T_CAPTION - 2)
        self.anim(FadeOut(eaten), FadeIn(behind, shift=DOWN * 0.08),
                  green.animate.set_value(1.0), run_time=0.6, rate_func=EASE)

        # the evidence, both numbers out of the same run
        ahead_pct = fx.dip_pct(HERO + 1, 0.0, fx.T)
        behind_pct = fx.dip_pct(0, 0.0, fx.T)
        a_tag = tag(f"-{round(ahead_pct)}%", [1.30, 0, 0], C_ANGLE, T_CAPTION - 6, 1.2)
        b_tag = tag(f"-{round(behind_pct)}%", [1.30, 0, 0], C_GROUND, T_CAPTION - 6, 1.2)
        a_tag.move_to([1.30, float(np.clip(hw.cars[HERO + 1].get_center()[1],
                                           ART_BOT + 0.2, ART_TOP - 0.2)), 0])
        b_tag.move_to([1.30, float(np.clip(hw.cars[0].get_center()[1],
                                           ART_BOT + 0.2, ART_TOP - 0.2)), 0])
        self.anim(FadeIn(a_tag, shift=LEFT * 0.08), run_time=0.4)
        self.anim(FadeIn(b_tag, shift=LEFT * 0.08), run_time=0.4)
        self.until(CUE["E3"].end - OUT_T)
        rule.clear_updaters()
        self.anim(FadeOut(behind), FadeOut(gap_lbl), FadeOut(tight),
                  FadeOut(rule), run_time=OUT_T)

        # -- E4: the seal
        self.say("E4")

        self.wait(0.5)
        self.anim(FadeOut(a_tag), FadeOut(b_tag),
                  run_time=0.35)

    # ============================================= BEAT 6 · 1:07–1:10 =====
    def beat6_loop(self):
        """Close the loop by literally replaying the opening.

        The last frame of the reel is the first frame of the reel: same car,
        same simulation time, same metres-per-unit, same gauge — so the sim
        clock is started far enough back that it arrives at exactly the hook's
        t-zero on the final frame.  The cut is not disguised, it does not
        exist."""
        tr, ck = self.ring_tr, self.clock_ring
        rate = self.HOOK_SPAN / self.HOOK_LAND
        # start the clock far enough back that it arrives at the hook's t-zero
        # on the very last frame — so the loop cut lands on an identical frame
        ck.t.set_value(self.hook_t0 - (REEL_LEN - self.wall) * rate)
        ck.rate.set_value(rate)

        hw = Road(self, tr, clock=ck, upm=0.132, ring_r=RING_R, ring_c=RING_C)
        hw.brake = 1.8
        hw.set_anchor_fn(lambda t: tr.car_at(self.hook_car, t))
        hw.y_off.set_value(ART_BOT + 0.62)
        hw.fade.set_value(0.0)
        hw.start()
        self.anim(self.hw_fix.fade.animate.set_value(0.0),
                  hw.fade.animate.set_value(1.0), run_time=0.35, rate_func=EASE)
        self.hw_fix.stop()
        self.remove(self.hw_fix.group)
        self.add(Gauge(ck, tr, self.hook_car))

        self.say("F1")
        self.wait(0.5)


if __name__ == "__main__":
    # `python Reel-3.py` runs no animation — it prints the cue sheet you
    # record the voice-over against, and every number the reel will show.
    print_cue_sheet()
    S, V, A = ring_run()
    c = measure_wave_speed(S, V, RING_L, 30.0, 160.0)
    print(f"  cruise        {V_EQ:5.2f} m/s = {V_EQ*MPS_KPH:.1f} km/h")
    print(f"  free flow     {V_FREE:5.2f} m/s = {V_FREE*MPS_KPH:.1f} km/h")
    print(f"  density       {N_RING/RING_L*1000:.0f} veh/km "
          f"({N_RING*CAR_L/RING_L*100:.0f}% of the road is metal)")
    print(f"  JAM WAVE      {c:5.2f} m/s = {abs(c)*MPS_MPH:.1f} mph backward")
    print(f"  peak braking  {A.min():5.2f} m/s^2  (a person, not a collision)")
    S2, V2, _ = chain_run()
    n2 = V2.shape[1]
    d2 = [100 * (1 - V2[:, i].min() / V_EQ) for i in range(n2)]
    print(f"  cascade       -{d2[-1]:.0f}% at the front  ->  -{d2[0]:.0f}% "
          f"{n2-1} cars back   (x{d2[0]/d2[-1]:.1f})")
    S3, V3, _ = fix_run(n=8, hero=4)
    d3 = [100 * (1 - V3[:, i].min() / V_EQ) for i in range(8)]
    g3 = [S3[int(t / DT), 5] - S3[int(t / DT), 4] - CAR_L for t in (0, 12, 24)]
    print(f"  with the gap  -{d3[5]:.0f}% ahead of it  ->  -{d3[0]:.0f}% behind it")
    print(f"  gap breathes  {g3[0]:.0f} m -> {g3[1]:.0f} m -> {g3[2]:.0f} m\n")