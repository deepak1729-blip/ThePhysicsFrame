from manim import *
import numpy as np
import math

# ─── PORTRAIT CANVAS (baked in) ────────────────────────────────────────────
config.pixel_width  = 1080
config.pixel_height = 1920
config.frame_height = 8.0
config.frame_width  = 4.5

# ─── OBSERVATORY PALETTE (verbatim from the series design system) ──────────
VOID      = "#0A0C10"   # background
PANEL     = "#11151C"   # lifted surfaces
STARLIGHT = "#F7F6F1"   # primary text · the light itself
DUST      = "#C7C1B3"   # secondary · the dimmed / lost state
AMBER     = "#FFA540"   # primary accent · focus  (amber follows the eye)
CYAN      = "#35E0F2"   # glass / lenses

SERIF = "Spectral"      # the channel's idea voice (italic)
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(1)     # deterministic → stable render cache


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


# ─── READABILITY LAYER ─────────────────────────────────────────────────────
# Every piece of copy sits on its own black plate and is lifted above the
# artwork, so grid lines / rays / rain never cut through a glyph.
TEXT_Z = 100          # z_index floor for all copy; art stays below
ART_Z = 10            # everything drawn in the world: rays, rain, lenses, tiles
PLATE_OPACITY = 0.5   # fully opaque: kills the translucent bleed-through


def plated(mob,
           opacity=PLATE_OPACITY, z=TEXT_Z):
    """Wrap `mob` in a black rounded plate and lift the pair above the art.

    Returns a VGroup(plate, mob) that positions, animates and fades as one
    unit — so a caption can never be read against a live gridline again.
    Do all sizing (fit_w / scale) BEFORE calling: the plate is measured once.
    """
    plate = Rectangle(
        width=mob.width,
        height=mob.height,
        fill_color=VOID, fill_opacity=opacity,
        stroke_width=0,
    ).move_to(mob.get_center())
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


def make_aperture(radius=0.85, color=AMBER, width=4.0):
    """THE circle — beaker mouth → pupil → lens. The same shape is the argument."""
    return Circle(radius=radius, stroke_color=color, stroke_width=width,
                  fill_color=color, fill_opacity=0.0)


def biconvex(h=1.0, bulge=0.9, color=CYAN, width=3.4, fill_op=0.14,
             axis=RIGHT):
    """A biconvex lens of aperture `h`, bulging along `axis`.

    `h` is the clear aperture (the diameter light passes through) and `bulge`
    sets how fat the glass is across it — so a big-thin objective is a large
    `h` with a small `bulge`, and a small-thick eyepiece is the reverse. The
    lens is built bulging left/right about a vertical aperture, then rotated
    so its optical axis lands on `axis`: pass UP for a lens that caps a
    vertical tube, RIGHT for one that caps a horizontal one.
    """
    top = np.array([0.0,  h / 2, 0.0])
    bot = np.array([0.0, -h / 2, 0.0])
    a = ArcBetweenPoints(top, bot, angle=bulge)
    b = ArcBetweenPoints(bot, top, angle=bulge)
    lens = VMobject()
    lens.set_points(np.vstack([a.get_points(), b.get_points()]))
    lens.set_stroke(color, width)
    lens.set_fill(color, fill_op)
    # built with its optical axis along RIGHT; swing it onto the asked-for one
    lens.rotate(angle_of_vector(axis) - angle_of_vector(RIGHT))
    return lens


def soft_dot(center, r, color, opacity, halo=2.2, halo_op=0.35):
    core = Circle(radius=r, stroke_width=0, fill_color=color,
                  fill_opacity=opacity).move_to(center)
    glow = Circle(radius=r * halo, stroke_width=0, fill_color=color,
                  fill_opacity=opacity * halo_op).move_to(center)
    return VGroup(glow, core)


def fuzzy_star(center, r=0.09, color=STARLIGHT, layers=26, spread=7.0, peak=0.92):
    """An out-of-focus blob. Scaling the group scales the blur identically —
    which is the whole point of Beat 1: zoom makes it *bigger*, not sharper."""
    g = VGroup()
    for i in range(layers):
        t = i / (layers - 1)                 # 0 = edge … 1 = core
        rad = r * (1 + spread * (1 - t))
        op = peak * (t ** 2.4)
        g.add(Circle(radius=rad, stroke_width=0,
                     fill_color=color, fill_opacity=op))
    g.move_to(center)
    return g


def star_field(n=46, exclude=None, exclude_r=0.9, seed=7):
    """A sparse, deterministic scatter of distant stars filling the frame.

    Drawn dim and small on purpose: this is the sky the reel opens and closes
    on, so it has to read as depth without ever competing with the copy. Any
    point within `exclude_r` of `exclude` is skipped, which keeps the hook dot
    alone in its own pocket of sky instead of sitting in a crowd.
    """
    rng = np.random.default_rng(seed)
    hw, hh = config.frame_width / 2, config.frame_height / 2
    g = VGroup()
    while len(g) < n:
        p = np.array([float(rng.uniform(-hw, hw)),
                      float(rng.uniform(-hh, hh)), 0.0])
        if exclude is not None and np.linalg.norm(p - exclude) < exclude_r:
            continue
        r = float(rng.uniform(0.012, 0.032))
        op = float(rng.uniform(0.30, 0.85))
        g.add(Circle(radius=r, stroke_width=0,
                     fill_color=STARLIGHT, fill_opacity=op).move_to(p))
    return g


def twinkle(field, amount=0.35, speed=1.7, seed=11):
    """Breathe the star field so the sky is never a frozen still.

    Each star gets its own phase and rate, so the field shimmers incoherently
    the way a real sky does — no visible pulse running through the group.

    Returns a ValueTracker that scales the whole field's brightness. Animate
    *that* to dim or raise the sky: the updater rewrites fill opacity on every
    frame, so an animated `set_opacity` on the group would simply be
    overwritten before it ever reached the screen.
    """
    rng = np.random.default_rng(seed)
    base = [s.get_fill_opacity() for s in field]
    ph = rng.uniform(0, 2 * math.pi, len(field))
    rate = rng.uniform(0.6, 1.5, len(field))
    field.t = 0.0
    dim = ValueTracker(1.0)

    def upd(grp, dt):
        grp.t += dt
        d = dim.get_value()
        for s, b, p, k in zip(grp, base, ph, rate):
            s.set_fill(opacity=d * b * (1 - amount + amount *
                                        (0.5 + 0.5 * math.sin(p + speed * k * grp.t))))
    field.add_updater(upd)
    return dim


def x_mark(color=AMBER, s=0.11, w=6):
    return VGroup(
        Line([-s, -s, 0], [s, s, 0], stroke_color=color, stroke_width=w),
        Line([-s, s, 0], [s, -s, 0], stroke_color=color, stroke_width=w),
    )


def magnifier(r=0.52, color=DUST, width=4.0):
    ring = Circle(radius=r, stroke_color=color, stroke_width=width)
    grip = Line(r * np.array([-0.71, -0.71, 0]),
                (r + 0.34) * np.array([-0.71, -0.71, 0]),
                stroke_color=color, stroke_width=width + 1.5)
    return VGroup(ring, grip)


def debug_grid(step=0.5, major=1.0, labels=True, label_step=1.0):
    """A positioning grid in world units, sized to the current frame.

    Minor lines every `step`, brighter lines every `major`, axes brightest,
    and numeric ticks down the left edge / along the bottom so you can read a
    coordinate straight off the frame. Debug only — never render with it on.
    """
    hw = config.frame_width / 2
    hh = config.frame_height / 2
    g = VGroup()

    def _line(a, b, op, w):
        return Line(a, b, stroke_color=CYAN, stroke_width=w, stroke_opacity=op)

    def _rank(v):
        """axis → major → minor (compare on a tolerance; floats drift)."""
        if abs(v) < 1e-6:
            return 0.55, 1.6
        if abs(v / major - round(v / major)) < 1e-6:
            return 0.28, 1.1
        return 0.13, 0.7

    n_v = int(hw / step)
    for i in range(-n_v, n_v + 1):
        x = i * step
        op, w = _rank(x)
        g.add(_line([x, -hh, 0], [x, hh, 0], op, w))

    n_h = int(hh / step)
    for j in range(-n_h, n_h + 1):
        y = j * step
        op, w = _rank(y)
        g.add(_line([-hw, y, 0], [hw, y, 0], op, w))

    if labels:
        for j in range(-int(hh / label_step), int(hh / label_step) + 1):
            y = j * label_step
            if abs(y) < 1e-6:
                continue
            g.add(mono(f"{y:g}", CYAN, 16, spacing=0)
                  .set_opacity(0.55)
                  .move_to([-hw + 0.20, y, 0]))
        for i in range(-int(hw / label_step), int(hw / label_step) + 1):
            x = i * label_step
            if abs(x) < 1e-6:
                continue
            g.add(mono(f"{x:g}", CYAN, 16, spacing=0)
                  .set_opacity(0.55)
                  .move_to([x, -hh + 0.20, 0]))
    return g


def safe_image(name, target_width, fallback_label):
    """Load an image by name; if absent, a framed placeholder so the script
    always runs. (Verbatim from the series.)"""
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
        lbl = mono(fallback_label, DUST, 22).move_to(plate.get_center())
        fit_w(lbl, target_width * 0.86)
        slot.add(plate, lbl)
        for o in (UL, UR, DL, DR):
            c = corner_L(o, size=0.16, color=AMBER, opacity=0.6)
            c.move_to(plate.get_corner(o), aligned_edge=o)
            slot.add(c)
        return slot


# ═══════════════════════════════════════════════════════════════════════════
class TelescopeReel(MovingCameraScene):
    """One continuous ~46s vertical reel. Six beats, one idea:
    a telescope is a bucket for light, not a zoom."""

    # ── director toggles ──────────────────────────────────────────────────
    LOOP_ENDING = True     # True → collapse back to hook dot (seamless loop)
    SHOW_MARKS  = True     # faint Observatory registration corners
    SHOW_SAFE   = False    # debug: draw the safe-box guide (never render True)
    SHOW_GRID   = False    # debug: world-unit positioning grid (never render True)
    GRID_STEP   = 0.5      # minor gridline spacing, world units
    GRID_MAJOR  = 1.0      # brighter line every N units
    GRID_LABELS = True     # numeric ticks along the left / bottom edges

    # ── locked geometry (portrait world units) ────────────────────────────
    HOOK   = np.array([0.0,  1.60, 0.0])   # lonely dot / hook spot
    STAR_T = np.array([0.0,  2.70, 0.0])   # star pinned near top
    EYE_LO = np.array([0.0, -1.20, 0.0])   # 5 mm eye, low-centre
    NEST_C = np.array([0.0,  0.60, 0.0])   # nested-circles centre (hot zone)
    CAP_Y  = -2.00                         # caption band (above bottom UI)

    LENS_R = 1.50                          # big bucket radius (clears rails)
    EYE_R  = 0.135                         # drawn eye radius (visible)

    # corner-mark inset from the true frame edge (decoration only — these do
    # NOT define the safe area and nothing else is positioned against them)
    MARK_MARGIN_X = 0.22
    MARK_MARGIN_Y = 0.30

    def add(self, *mobs, **kw):
        """Pin anything that isn't already copy to the art layer.

        Manim breaks z-index ties by insertion order, so art added after a
        caption would otherwise paint over it. Routing every add() through
        here means new beats inherit the layering for free — art below,
        plated text above — without tagging each mobject by hand.
        """
        for m in mobs:
            if m.z_index < TEXT_Z:
                m.set_z_index(ART_Z)
        return super().add(*mobs, **kw)

    def construct(self):
        self.camera.frame.save_state()

        # Beat 0 fills these in; declared here so any beat can be run on its
        # own (or the cold open skipped) without tripping over a missing attr
        self.hook_dot = None
        self.field = None
        self.sky_dim = None

        if self.SHOW_GRID:
            # drawn first so every beat lands on top of it; the grid is fixed
            # in world space, so the Beat 5 camera push-in reads against it too
            self.grid = debug_grid(step=self.GRID_STEP, major=self.GRID_MAJOR,
                                   labels=self.GRID_LABELS,
                                   label_step=self.GRID_MAJOR)
            self.grid.set_z_index(-10)      # hard floor: always under the art
            super().add(self.grid)          # bypass the ART_Z pin

        if self.SHOW_MARKS:
            # registration corners hug the true frame edges (margin only —
            # this is decoration, independent of the safe box below)
            mx = config.frame_width / 2 - self.MARK_MARGIN_X
            my = config.frame_height / 2 - self.MARK_MARGIN_Y
            self.marks = VGroup(*[corner_L(o) for o in (UL, UR, DL, DR)])
            for c in self.marks:
                x = mx * c.anchor[0]
                y = my * c.anchor[1]
                c.move_to(np.array([x, y, 0]), aligned_edge=c.anchor)
            self.marks.set_z_index(-9)
            super().add(self.marks)         # bypass the ART_Z pin
        if self.SHOW_SAFE:
            self.add(Rectangle(width=3.95, height=5.0, stroke_color=CYAN,
                               stroke_width=1, stroke_opacity=0.4)
                     .move_to([-0.275, 0.3, 0]))

        self.beat0_cold_open()
        self.beat1_zoom_that_fails()
        self.beat2_glass_in_the_rain()
        self.beat3_starlight_is_rain()
        self.beat4_bigger_bucket()
        self.beat5_what_a_toy_revealed()
        self.beat6_side_effect_and_loop()

    # ── shared mechanics ──────────────────────────────────────────────────
    def _make_rain(self, n, xspan, top, bot, mouth_c, mouth_half, catch_y):
        """A continuous curtain of falling starlight. Streaks whose x lands in
        the narrow mouth are absorbed there and counted once (self._caught_n)."""
        span = (top - bot) + 1.0
        data, rain = [], VGroup()
        for _ in range(n):
            x = float(RNG.uniform(*xspan))
            v = float(RNG.uniform(3.0, 4.6))
            L = float(RNG.uniform(0.35, 0.7))
            w = float(RNG.uniform(1.4, 2.4))
            ph = float(RNG.uniform(0.0, span))
            caught = abs(x - mouth_c) < mouth_half
            rain.add(Line([x, top, 0], [x, top - L, 0], stroke_color=STARLIGHT,
                          stroke_width=w, stroke_opacity=0.0))
            # [x, v, L, phase, caught?, counted-this-pass?, w]
            data.append([x, v, L, ph, caught, False, w])
        rain.time = 0.0
        reveal = ValueTracker(0.0)
        rain.reveal = reveal

        def upd(grp, dt):
            grp.time += dt
            g = reveal.get_value()
            for s, d in zip(grp, data):
                x, v, L, ph, caught, counted, w = d
                fall = (ph + v * grp.time) % span
                head = top - fall
                tail = head + L
                # a streak that has wrapped back to the top is a fresh drop:
                # re-arm it so the next pass through the mouth counts again
                if counted and head > catch_y:
                    d[5] = counted = False
                if caught and head <= catch_y:
                    # count on the *crossing*, not on full absorption: the head
                    # is past the mouth, so this drop is in the bucket. Waiting
                    # for the tail to clear gave a window a few ms wide, which
                    # a 60 fps step routinely jumped straight over.
                    if not counted:
                        d[5] = True
                        self._caught_n += 1
                    top_pt = min(tail, top)
                    if top_pt - catch_y < 0.03:
                        s.set_stroke(opacity=0.0)
                        continue
                    s.put_start_and_end_on([x, catch_y, 0], [x, top_pt, 0])
                    s.set_stroke(color=AMBER, width=2.6, opacity=0.95 * g)
                else:
                    top_pt = min(tail, top)
                    if top_pt - head < 0.02:
                        s.set_stroke(opacity=0.0)
                        continue
                    appear = 1.0
                    if tail > top - 0.8:
                        appear = float(np.clip((top - tail) / 0.8, 0.0, 1.0))
                    s.put_start_and_end_on([x, head, 0], [x, top_pt, 0])
                    s.set_stroke(color=STARLIGHT, width=w, opacity=0.85 * g * appear)
        rain.add_updater(upd)
        return rain

    def _hex_pack(self, n, R, spacing):
        """The n grid points nearest centre inside radius R — a packed disk."""
        rows = int(R / (spacing * 0.866)) + 3
        cand = []
        for j in range(-rows, rows + 1):
            yy = j * spacing * math.sqrt(3) / 2
            xoff = (spacing / 2) if (j % 2) else 0.0
            cols = int(R / spacing) + 3
            for i in range(-cols, cols + 1):
                xx = i * spacing + xoff
                if xx * xx + yy * yy <= R * R:
                    cand.append((xx * xx + yy * yy, np.array([xx, yy, 0.0])))
        cand.sort(key=lambda c: c[0])
        return [c[1] for c in cand[:n]]

    # ═══════════════════════════════════════════ BEAT 0 · 0:00–0:07 ═══════
    def beat0_cold_open(self):
        """The cold open, cut to the VO's three movements.

        'Everyone thinks a telescope zooms in on the stars.' — the sky wakes,
        one star is singled out, and the popular belief is built on screen:
        crosshair, magnification rings blooming outward, the word ZOOM.
        'It doesn't.' — the whole apparatus is struck through and collapses
        inward. 'Watch.' — everything drains except that one star, which is
        precisely the frame Beat 1 opens on, and precisely the frame Beat 6
        rebuilds. The loop seam lives here.
        """
        # ── the sky, already there ───────────────────────────────────────
        # A loop has no beginning, so nothing here fades up from black: frame
        # 0 must be *identical* to the reel's last frame or the wrap pops.
        # Both are this — full sky, one lonely star at the hook spot.
        field = star_field(46, exclude=self.HOOK, exclude_r=1.0)
        field.set_z_index(-5)
        super().add(field)                    # sky sits under everything
        self.sky_dim = twinkle(field)
        self.field = field

        # the star Beat 1 inherits and Beat 6 hands back — on screen from the
        # first frame, never introduced
        dot = fuzzy_star(self.HOOK, r=0.09)
        self.add(dot)
        self.wait(0.9)                        # let the sky breathe on the seam

        # ── 'Everyone thinks…' — build the claim ─────────────────────────
        # a crosshair takes aim: the gesture of pointing an instrument
        cross = VGroup(
            Line(LEFT * 0.62, LEFT * 0.24, stroke_color=AMBER, stroke_width=2.4),
            Line(RIGHT * 0.24, RIGHT * 0.62, stroke_color=AMBER, stroke_width=2.4),
            Line(UP * 0.62, UP * 0.24, stroke_color=AMBER, stroke_width=2.4),
            Line(DOWN * 0.62, DOWN * 0.24, stroke_color=AMBER, stroke_width=2.4),
        ).move_to(self.HOOK).set_opacity(0.0)
        self.add(cross)
        self.play(cross.animate.set_opacity(0.85).scale(0.72),
                  run_time=0.6, rate_func=smooth)

        # magnification rings bloom outward from the star: the promise of zoom
        rings = VGroup(*[
            Circle(radius=0.30 + i * 0.34, stroke_color=CYAN,
                   stroke_width=2.2, stroke_opacity=0.0).move_to(self.HOOK)
            for i in range(4)])
        self.add(rings)
        self.play(LaggedStart(*[
            AnimationGroup(r.animate.set_stroke(opacity=0.55 - 0.10 * i)
                           .scale(1.18))
            for i, r in enumerate(rings)], lag_ratio=0.18),
            run_time=1.1)

        claim = plated(
            fit_w(serif("everyone thinks a telescope", DUST, 34), 3.4)
            .move_to([0, -0.55, 0]))
        word = plated(
            fit_w(serif("ZOOMS IN", STARLIGHT, 62, weight=BOLD), 3.0)
            .move_to([0, -1.20, 0]))
        self.play(FadeIn(claim, shift=UP * 0.14), run_time=0.6)
        self.play(FadeIn(word, scale=0.75), run_time=0.5)
        self.wait(0.35)

        # ── 'It doesn't.' — strike it through and collapse it ────────────
        # anchor to the glyphs (word[1]), not the plated group, and ride the
        # text's own vertical centre so the rule cuts the letterforms cleanly
        glyphs = word[1]
        strike = Line(
            [glyphs.get_left()[0] - 0.10, glyphs.get_center()[1], 0],
            [glyphs.get_right()[0] + 0.10, glyphs.get_center()[1], 0],
            stroke_color=AMBER, stroke_width=7)
        strike.set_z_index(TEXT_Z + 2)
        self.play(Create(strike), run_time=0.45, rate_func=rush_into)

       
        # rings snap back in as the claim is withdrawn — the zoom un-promises
        self.play(
            FadeOut(claim, shift=DOWN * 0.14),
            FadeOut(word, scale=0.6), FadeOut(strike, scale=0.6),
            *[r.animate.scale(0.05).set_stroke(opacity=0.0) for r in rings],
            cross.animate.scale(0.35).set_opacity(0.0),
            run_time=0.7, rate_func=smooth)
        self.remove(rings, cross)
        self.wait(0.5)

        # ── 'Watch.' — drain to the lonely dot Beat 1 begins from ────────
        watch = plated(
            fit_w(mono("WATCH", DUST, 28), 1.6).move_to([0, -1.20, 0]))
        self.play(Write(watch), run_time=0.5)
        self.wait(0.45)
        # dim the sky by driving the twinkle's own amplitude, not set_opacity:
        # the updater rewrites fill opacity every frame and would overwrite an
        # animated value outright
        self.play(FadeOut(watch, shift=DOWN * 0.2),
                  self.sky_dim.animate.set_value(0.30),
                  run_time=0.8, rate_func=smooth)

        # hand the star to Beat 1 already on screen — no re-fade, no seam
        self.hook_dot = dot

    # ═══════════════════════════════════════════ BEAT 1 · 0:07–0:12 ═══════
    def beat1_zoom_that_fails(self):
        """Frame zero is already composed: one lonely blur, one line of text.
        A loupe rises up the column; the blob grows 4.5× — and so does its
        blur. Bigger, never sharper. 'still blurry ✗'."""
        # fuzzy_star is one VGroup of stacked blur layers — hand the whole
        # blob to Beat 2, which morphs it into the first falling streak.
        # Beat 0 already put it on screen and left it in self.hook_dot; adopt
        # that one so the cold open flows straight into this beat, and only
        # build a fresh dot when this beat is run standalone.
        if getattr(self, "hook_dot", None) is None:
            self.hook_dot = fuzzy_star(self.HOOK, r=0.09)
            self.add(self.hook_dot)
        dot = self.hook_dot
        self.wait(0.6)

        loupe = magnifier().move_to([0, -3.7, 0])
        self.add(loupe)

        zoom_tr = ValueTracker(100)
        zoom_txt = always_redraw(
            lambda: plated(mono(f"ZOOM {int(zoom_tr.get_value())}%", DUST, 26)
                           .move_to([0, -2.0, 0])))
        self.add(zoom_txt)

        # loupe rises to the dot; dot (and its blur) scale up together
        self.play(loupe.animate.move_to(self.HOOK),
                  dot.animate.scale(4.5),
                  zoom_tr.animate.set_value(400),
                  run_time=1.6, rate_func=smooth)

        blur_tag = VGroup(mono("a bigger blurry dot", DUST, 22), x_mark())
        blur_tag.arrange(RIGHT, buff=0.16).move_to([0, -0.75, 0])
        blur_tag = plated(blur_tag)
        zoom_static = plated(mono("ZOOM 400%", DUST, 26).move_to([0, -2.0, 0]))
        self.play(FadeIn(blur_tag, scale=0.6), run_time=0.5)
        self.remove(zoom_txt)
        self.add(zoom_static)
        self.wait(0.5)

        # loupe lifts away; blob snaps back to the lonely dot
        self.play(loupe.animate.move_to([0, 4.0, 0]).set_opacity(0.0),
                  dot.animate.scale(1 / 4.5),
                  FadeOut(blur_tag), FadeOut(zoom_static),
                  run_time=1.1, rate_func=smooth)
        self.remove(loupe)
        self.wait(0.2)

    # ═══════════════════════════════════════════ BEAT 2 · 0:05–0:14 ═══════
    def beat2_glass_in_the_rain(self):
        """The star's light falls as rain through the whole tall frame. A tiny
        narrow glass catches almost nothing — the smallness of the opening is
        the villain, not distance."""
        # morph the lonely dot into the first falling streak
        first = Line(self.HOOK, self.HOOK + DOWN * 0.55,
                     stroke_color=STARLIGHT, stroke_width=2.2)
        self.play(ReplacementTransform(self.hook_dot, first), run_time=0.7)
        self.remove(first)

        # narrow glass, low-centre, inside the safe box
        gmouth_y, gbase_y, ghalf = -1.35, -2.05, 0.27
        glass = VGroup(
            Line([-ghalf, gmouth_y, 0], [-ghalf * 0.8, gbase_y, 0]),
            Line([ghalf, gmouth_y, 0], [ghalf * 0.8, gbase_y, 0]),
            Line([-ghalf * 0.8, gbase_y, 0], [ghalf * 0.8, gbase_y, 0]),
        ).set_stroke(CYAN, 4.0)
        mouth = Line([-ghalf, gmouth_y, 0], [ghalf, gmouth_y, 0],
                     stroke_color=CYAN, stroke_width=4.0, stroke_opacity=0.5)

        self._caught_n = 0
        rain = self._make_rain(n=52, xspan=(-2.05, 2.05), top=4.3, bot=-4.3,
                               mouth_c=0.0, mouth_half=ghalf, catch_y=gmouth_y)
        self.add(rain)
        self.play(rain.reveal.animate.set_value(1.0),
                  Create(glass), Create(mouth), run_time=1.6)

        tally = always_redraw(
            lambda: plated(mono(f"caught: {self._caught_n}", STARLIGHT, 26)
                           .move_to([0, -0.55, 0])))
        self.add(tally)
        self.wait(4.6)  # rain runs; the tally barely creeps

        missed = plated(
            fit_w(serif("the opening's too small.", DUST, 38), 3.0)
            .move_to([0, 0.7, 0]))
        self.play(FadeIn(missed, shift=UP * 0.2), run_time=0.9)
        self.wait(0.7)

        rain.clear_updaters()
        self.rain = rain
        self.glass = VGroup(glass, mouth)
        self.tally = tally
        self.missed = missed

    # ═══════════════════════════════════════════ BEAT 3 · 0:14–0:22 ═══════
    def beat3_starlight_is_rain(self):
        """The rain straightens into radial rays pouring from one star at the
        top. A 5 mm eye sits low. Only a sliver enters; the vast remainder
        sails off the edges. Faint stars aren't small — their light misses you."""
        S = self.STAR_T
        E = self.EYE_LO
        n = 45
        angles = np.linspace(math.radians(-152), math.radians(-28), n)
        r_hit = 0.33
        rays, hit_flags = VGroup(), []
        for th in angles:
            d = np.array([math.cos(th), math.sin(th), 0.0])
            end = S + d * 8.0
            w = E - S
            perp = abs(w[0] * d[1] - w[1] * d[0])
            hit = perp < r_hit
            hit_flags.append(hit)
            rays.add(Line(S, end, stroke_color=STARLIGHT,
                          stroke_width=2.0, stroke_opacity=0.9))

        self.play(FadeOut(self.missed, run_time=0.3))
        self.play(ReplacementTransform(self.rain, rays),
                  FadeOut(self.glass), FadeOut(self.tally),
                  run_time=1.4, rate_func=smooth)

        star = soft_dot(S, 0.10, STARLIGHT, 1.0, halo=3.0, halo_op=0.4)
        self.play(FadeIn(star, scale=0.4), run_time=0.5)

        # expanding wavefront washes down the tall gap
        wave = Arc(radius=0.2, start_angle=math.radians(-165),
                   angle=math.radians(150), arc_center=S,
                   stroke_color=STARLIGHT, stroke_width=3.0, stroke_opacity=0.7)
        self.add(wave)
        self.play(wave.animate.become(
            Arc(radius=4.6, start_angle=math.radians(-165),
                angle=math.radians(150), arc_center=S,
                stroke_color=STARLIGHT, stroke_width=2.0, stroke_opacity=0.0)),
            run_time=1.3, rate_func=linear)
        self.remove(wave)

        # the eye
        eye = make_aperture(self.EYE_R, AMBER, 4.5).move_to(E)
        eye_lbl = plated(
            fit_w(mono("your eye — 5 mm", AMBER, 25), 2.2)
            .next_to(eye, DOWN, buff=0.22))
        self.play(GrowFromCenter(eye), FadeIn(eye_lbl), run_time=0.6)

        # sliver caught (amber, bright) vs enormous lost remainder (dust, dim)
        caught_anims, lost_anims = [], []
        for ray, hit in zip(rays, hit_flags):
            if hit:
                caught_anims.append(ray.animate.set_stroke(AMBER, 5.0, 1.0))
            else:
                lost_anims.append(ray.animate.set_stroke(DUST, 1.6, 0.42))
        self.play(*lost_anims, *caught_anims, run_time=1.0)
        self.wait(0.6)

        self.rays = rays
        self.hit_flags = hit_flags
        self.star = star
        self.eye = eye
        self.eye_lbl = eye_lbl

    # ═══════════════════════════════════════════ BEAT 4 · 0:22–0:33 ═══════
    def beat4_bigger_bucket(self):
        """The aha. The eye recenters; a 10 cm lens grows concentrically around
        it — 5 mm → 100 mm is 20× wider, so 400× the area. Tile 400 eyes inside
        the lens to make 400× physical, then scoop a whole bundle of starlight."""
        self.play(FadeOut(self.eye_lbl),
                  FadeOut(self.star), FadeOut(self.rays), run_time=0.5)

        C = self.NEST_C
        self.play(self.eye.animate.move_to(C), run_time=1.0, rate_func=smooth)

        lens = make_aperture(self.LENS_R, AMBER, 4.0).move_to(C)
        # plate each rung individually so LaggedStartMap still staggers them
        ladder = VGroup(
            plated(mono("5 mm", AMBER, 26)),
            plated(mono("→", DUST, 26)),
            plated(mono("100 mm", AMBER, 26)),
        ).arrange(RIGHT, buff=0.04).move_to([0, -1.7, 0])
        ladder.set_z_index(TEXT_Z)
        self.play(GrowFromCenter(lens),
                  LaggedStartMap(FadeIn, ladder, lag_ratio=0.3),
                  run_time=2.0, rate_func=smooth)

        twenty = plated(
            fit_w(serif("20× wider", STARLIGHT, 40), 2.6).move_to([0, 2.35, 0]))
        self.play(FadeIn(twenty, shift=DOWN * 0.15), run_time=0.7)
        self.wait(0.3)

        # tile 400 eye-apertures inside the lens: 20² = 400× the area
        pts = self._hex_pack(400, self.LENS_R - 0.10, 0.122)
        tiles = VGroup(*[
            Circle(radius=0.050, stroke_color=AMBER, stroke_width=1.0,
                   fill_color=AMBER, fill_opacity=0.24).move_to(C + p)
            for p in pts])

        mult = ValueTracker(1)
        counter = always_redraw(
            lambda: plated(mono(f"{int(mult.get_value())}×", AMBER, 30)
                           .move_to([0, -1.7, 0])))
        self.play(FadeOut(twenty), FadeOut(self.eye), FadeOut(ladder),
                  run_time=0.5)
        self.add(counter)
        self.play(LaggedStartMap(FadeIn, tiles, lag_ratio=0.004),
                  mult.animate.set_value(400),
                  run_time=3.0, rate_func=linear)

        pop = plated(
            fit_w(serif("400× more light", AMBER, 46, weight=BOLD), 3.0)
            .move_to([0, 2.35, 0]))
        self.play(FadeIn(pop, scale=0.7), run_time=0.6)

        # the running tally has landed on 400 — retire it so the thesis card
        # owns the lower band alone (they overlap otherwise)
        self.remove(counter)
        bucket = plated(
            fit_w(serif("a bigger bucket for light.", STARLIGHT, 36), 3.0)
            .move_to([0, -1.85, 0]))
        self.play(FadeIn(bucket, shift=UP * 0.15), run_time=0.6)
        self.wait(0.3)
        self.bucket = bucket

        # replay the wavefront — this time the bucket scoops a bundle
        S = self.STAR_T
        bundle = VGroup()
        for x in np.linspace(-self.LENS_R * 0.9, self.LENS_R * 0.9, 15):
            target = C + np.array([x, 0, 0])
            bundle.add(Line(S, target, stroke_color=STARLIGHT,
                            stroke_width=2.2, stroke_opacity=0.0))
        self.add(bundle)
        self.play(bundle.animate.set_stroke(STARLIGHT, 2.4, 0.85),
                  run_time=1.0)
        self.play(bundle.animate.set_stroke(AMBER, 3.0, 0.95),
                  Flash(C, color=AMBER, flash_radius=self.LENS_R + 0.2,
                        line_length=0.2, num_lines=18),
                  run_time=1.0)

        self.lens = lens
        self.tiles = tiles
        self.pop = pop
        self.bundle = bundle

    # ═══════════════════════════════════════════ BEAT 5 · 0:33–0:40 ═══════
    def beat5_what_a_toy_revealed(self):
        """The lens becomes an instrument — Galileo's refractor as line-art,
        pointing up. Then the real sky it revealed with a cheap tube."""
        self.play(FadeOut(self.tiles), FadeOut(self.bundle),
                  FadeOut(self.pop), FadeOut(self.bucket), run_time=0.5)

        C = self.NEST_C
        # A refractor, drawn honestly: wide thin objective at the sky end,
        # narrow fat eyepiece at the eye end, tube tapering between the two.
        # Both lenses bulge along UP — the tube's own axis — so they cap the
        # barrel instead of slicing across it.
        OBJ_R, EYE_R_ = 0.52, 0.30        # tube half-widths at each end
        TOP_Y, BOT_Y = 1.55, -1.55        # sky end / eye end

        # long and slender, tapering only gently — the barrel of a refractor,
        # not a funnel. The draw-tube at the eye end is a separate short stub,
        # which is what actually reads as "telescope" at a glance.
        barrel = Polygon(
            [-OBJ_R, TOP_Y, 0], [OBJ_R, TOP_Y, 0],
            [EYE_R_, BOT_Y + 0.42, 0], [-EYE_R_, BOT_Y + 0.42, 0],
            stroke_color=DUST, stroke_width=3.0,
            fill_color=PANEL, fill_opacity=0.35,
        ).round_corners(radius=0.06)
        draw_tube = Polygon(
            [-EYE_R_, BOT_Y + 0.44, 0], [EYE_R_, BOT_Y + 0.44, 0],
            [EYE_R_, BOT_Y, 0], [-EYE_R_, BOT_Y, 0],
            stroke_color=DUST, stroke_width=3.0,
            fill_color=PANEL, fill_opacity=0.5,
        )
        tube = VGroup(barrel, draw_tube).move_to(C)

        # Both lenses seat *inside* the barrel, so their apertures are the tube
        # width less the wall — a lens wider than its own tube reads as a
        # mistake. Objective: big aperture, barely any bulge. Eyepiece: a bit
        # over half the aperture, three times the curvature — small but fat.
        obj = biconvex(h=OBJ_R * 2 - 0.06, bulge=0.42, color=CYAN, width=3.4,
                       axis=UP)
        obj.move_to(C + UP * (TOP_Y - 0.05))
        eye_lens = biconvex(h=EYE_R_ * 2 - 0.05, bulge=1.35, color=CYAN,
                            width=3.0, axis=UP)
        eye_lens.move_to(C + UP * (BOT_Y + 0.11))
        scope = VGroup(tube, obj, eye_lens)

        self.play(ReplacementTransform(self.lens, obj), run_time=0.7)
        self.play(Create(tube), Create(eye_lens),
                  lag_ratio=0.2, run_time=1.4)
        galileo = plated(
            fit_w(mono("GALILEO · 1600s — basically a toy", DUST, 24), 3.4)
            .move_to([0, self.CAP_Y, 0]))
        self.play(scope.animate.rotate(math.radians(-12)).shift(UP * 0.1),
                  FadeIn(galileo), run_time=0.7, rate_func=smooth)

        # dissolve to the real sky (placeholders until PNGs are provided)
        moon = safe_image("moon.jpg", 3.0, "MOON — CRATERS").move_to([0, 0.95, 0])
        moon_cap = plated(
            fit_w(mono("craters on the Moon", STARLIGHT, 26), 3.0)
            .move_to([0, self.CAP_Y, 0]))
        self.play(FadeOut(scope), FadeOut(galileo),
                  FadeIn(moon), FadeIn(moon_cap), run_time=0.8)
        # gentle push-in on the Moon
        self.play(self.camera.frame.animate.scale(0.82).move_to([0, 0.95, 0]),
                  run_time=1.1, rate_func=smooth)
        self.play(self.camera.frame.animate.restore(), run_time=0.6)

        jup = safe_image("jupiter.jpg", 3.2, "JUPITER + 4 MOONS").move_to([0, 0.4, 0])
        jup_cap = plated(
            fit_w(mono("4 moons of Jupiter", STARLIGHT, 26), 3.0)
            .move_to([0, self.CAP_Y, 0]))
        self.play(FadeOut(moon), FadeOut(moon_cap),
                  FadeIn(jup), FadeIn(jup_cap), run_time=0.9)
        self.wait(0.4)

        self.sky = VGroup(jup_cap)
        self.jup = jup

    # ═══════════════════════════════════════════ BEAT 6 · 0:40–0:46 ═══════
    def beat6_side_effect_and_loop(self):
        """Close the loop: ZOOM was only ever a side effect; CATCH LIGHT is the
        job. The captured flood converges to a focus — and there it's still
        blurry. Collapse that blur back into the opening dot for a clean loop."""
        C = self.NEST_C
        self.play(FadeOut(self.jup), FadeOut(self.sky), run_time=0.5)

        eye = make_aperture(self.EYE_R, AMBER, 4.5).move_to(C)
        lens = make_aperture(self.LENS_R, AMBER, 4.0).move_to(C)
        self.play(GrowFromCenter(lens), GrowFromCenter(eye), run_time=0.7)

        zoom_word = plated(serif("MAGNIFICATION", DUST, 38).move_to(C))
        self.play(FadeIn(zoom_word), run_time=0.4)
        foot = plated(fit_w(mono("just a side effect", DUST, 24), 3.0)
                      .move_to([0, -1.85, 0]))
        catch = plated(
            fit_w(serif("CATCH LIGHT", AMBER, 56, weight=BOLD), 3.0)
            .move_to([0, 2.3, 0]))
        self.play(ReplacementTransform(zoom_word, foot),
                  FadeIn(catch, scale=0.7), run_time=1.2, rate_func=smooth)

        # captured flood converges to a focus below the lens
        focus = C + DOWN * 1.9
        rays = VGroup(*[
            Line(C + np.array([x, -0.02, 0]), focus,
                 stroke_color=AMBER, stroke_width=2.2, stroke_opacity=0.9)
            for x in np.linspace(-self.LENS_R * 0.85, self.LENS_R * 0.85, 13)])
        blur = fuzzy_star(focus, r=0.07, color=STARLIGHT).scale(1.4)
        self.play(LaggedStartMap(Create, rays, lag_ratio=0.05),
                  run_time=1.2)
        self.play(FadeIn(blur), run_time=0.4)

        
        self.play(FadeOut(catch), FadeOut(foot))
        self.wait(0.6)

        if self.LOOP_ENDING:
            # Land exactly on Beat 0's opening frame so the cut is invisible:
            # the instrument clears, the focus-blur rises back to the hook
            # spot as the lonely star, and the sky lifts from its dimmed state
            # to full brightness — which is where the cold open begins.
            hook = fuzzy_star(self.HOOK, r=0.09)

            self.play(FadeOut(rays), FadeOut(eye), FadeOut(lens),
                      ReplacementTransform(blur, hook),
                      run_time=1.0, rate_func=smooth)

            # the sky comes back up: the last frame and the first now match
            if self.sky_dim is not None:
                self.play(self.sky_dim.animate.set_value(1.0),
                          run_time=0.9, rate_func=smooth)

            # a beat of clean sky — the loop point. The last frame now holds
            # exactly what Beat 0's first frame holds (full-brightness sky +
            # the lonely star at HOOK), so the wrap is invisible: the viewer
            # sees only the question coming round again.
            self.wait(0.9)
        else:
            self.wait(1.4)  # hard cliffhanger: hold on the unfinished thought