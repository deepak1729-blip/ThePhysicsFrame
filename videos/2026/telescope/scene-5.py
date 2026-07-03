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
C_ANGLE   = "#E08AAB"   # ANGLE θ
C_LEN     = "#5B8FB0"   # LENGTH / r  (== CYAN)
C_MASS    = "#B89A86"   # MATTER — warm organic tone
C_GROUND  = "#7F8A99"   # ground / reference axis
RED       = "#FF0000"        # long λ → amber
BLUE      = "#0000FF"        # short λ → cyan

SERIF = "Spectral"      # ideas; italic is the channel's voice & every equation
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(5)      # deterministic -> stable render cache

DISP_CROWN = 0.07               # 1/V, exaggerated ×4 (real crown ≈ 0.017)
DISP_FLINT = 0.14               # flint bends colour ~2× harder per power
BOW_CROWN  = 0.12               # partial-dispersion bow, crown
BOW_FLINT  = 0.34               # partial-dispersion bow, flint (≠ crown)
S_VALS     = list(np.linspace(-1.0, 1.0, 5))   # −1 amber … +1 cyan


def g_shape(s, bow):
    """Dispersion shape: linear sweep + the partial-dispersion bow."""
    return s + bow * (1.0 - s * s)


def wave_color(s):
    """Long wavelengths render AMBER, short render CYAN — the palette's own
    two accents ARE the two ends of the spectrum here."""
    return interpolate_color(ManimColor(RED), ManimColor(BLUE),
                             (s + 1.0) / 2.0)


# ═══════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION VOCABULARY  (inlined per-file, matching Scenes 1–4 grammar)
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
    """THE circle — every light-catching opening in this series."""
    return Circle(radius=radius, stroke_color=color, stroke_width=width,
                  fill_color=color, fill_opacity=0.10)


def biconvex(h=1.1, bulge=1.15, color=CYAN, width=2.4, fill_op=0.12):
    """A lens cross-section — identical builder to Scenes 2–4."""
    top = np.array([0.0,  h / 2, 0.0])
    bot = np.array([0.0, -h / 2, 0.0])
    a = ArcBetweenPoints(top, bot, angle=bulge)
    b = ArcBetweenPoints(bot, top, angle=bulge)
    lens = VMobject()
    lens.set_points(np.vstack([a.get_points(), b.get_points()]))
    lens.set_stroke(color, width)
    lens.set_fill(color, fill_op)
    lens.h = h
    return lens


def path_from(*segments, **style):
    """Stitch Lines/Arcs into ONE continuous VMobject so Create() draws a
    single unbroken silhouette — no wobble, no seams.  (Verbatim Scene 1.)"""
    p = VMobject(**style)
    for i, seg in enumerate(segments):
        if i == 0:
            p.set_points(seg.get_points())
        else:
            p.add_line_to(seg.get_start())      # (zero-length weld)
            p.append_points(seg.get_points())
    return p


def soft_dot(center, r, color, opacity, halo=2.2, halo_op=0.35):
    """A dot with a soft halo — reads as light, not as ink. (Scene 3.)"""
    core = Circle(radius=r, stroke_width=0, fill_color=color,
                  fill_opacity=opacity).move_to(center)
    glow = Circle(radius=r * halo, stroke_width=0, fill_color=color,
                  fill_opacity=opacity * halo_op).move_to(center)
    return VGroup(glow, core)


def focal_crosshair(point, color=AMBER, r=0.10, arm=0.24):
    """The series landmark wherever rays cross — Scene 3's exact mark."""
    p = np.array([point[0], point[1], 0.0])
    ring = Circle(radius=r, stroke_color=color, stroke_width=2.0).move_to(p)
    h = Line(p + LEFT * arm, p + RIGHT * arm, stroke_color=color,
             stroke_width=1.5, stroke_opacity=0.9)
    v = Line(p + DOWN * arm, p + UP * arm, stroke_color=color,
             stroke_width=1.5, stroke_opacity=0.9)
    core = Dot(p, radius=0.035, color=color)
    return VGroup(h, v, ring, core)


def safe_image(name, target_width, fallback_label):
    """Load an image by name; if it isn't present yet, return a framed
    placeholder slot so the script always runs as-is."""
    try:
        img = ImageMobject(name)
        img.set(width=target_width)
        return img
    except Exception:
        h = target_width * 0.72
        plate = Rectangle(width=target_width, height=h,
                          fill_color=PANEL, fill_opacity=1.0,
                          stroke_color=DUST, stroke_width=1.2,
                          stroke_opacity=0.4)
        lbl = Text(fallback_label, font=MONO, font_size=11, color=DUST)
        lbl.set(width=min(lbl.width, target_width * 0.8))
        lbl.move_to(plate.get_center())
        return VGroup(plate, lbl)


def flint_element(h=1.5, mate_bulge=1.0, back_bulge=0.30, dx=0.34,
                  color=CYAN, width=2.2, fill_op=0.07):
    """The flint half of the doublet: its LEFT face is the exact arc of the
    crown's right cheek (so the two nest perfectly), its right face is a
    gentle concavity.  A diverging element — the flaw that cancels a flaw."""
    top = np.array([0.0,  h / 2, 0.0])
    bot = np.array([0.0, -h / 2, 0.0])
    face_l = ArcBetweenPoints(top, bot, angle=mate_bulge)       # mates crown
    seam_b = Line(bot, np.array([dx, -h / 2, 0.0]))
    face_r = ArcBetweenPoints(np.array([dx, -h / 2, 0.0]),
                              np.array([dx,  h / 2, 0.0]),
                              angle=back_bulge)                 # concave right
    seam_t = Line(np.array([dx, h / 2, 0.0]), top)
    fl = path_from(face_l, seam_b, face_r, seam_t,
                   stroke_color=color, stroke_width=width)
    fl.set_fill(color, fill_op)
    return fl


def tiny_observer(h=0.96, color=STARLIGHT, width=2.0):
    """A line-figure human, bottom at y=0 — the scale witness of Act 3."""
    r = 0.115 * h
    head = Circle(radius=r, stroke_color=color, stroke_width=width)
    head.move_to([0, h - r, 0])
    spine = Line([0, h - 2 * r, 0], [0, 0.36 * h, 0],
                 stroke_color=color, stroke_width=width)
    leg1 = Line([0, 0.36 * h, 0], [-0.14 * h, 0, 0],
                stroke_color=color, stroke_width=width)
    leg2 = Line([0, 0.36 * h, 0], [0.14 * h, 0, 0],
                stroke_color=color, stroke_width=width)
    # arms raised a little — the figure is looking up at the thing
    arm1 = Line([0, 0.74 * h, 0], [-0.20 * h, 0.88 * h, 0],
                stroke_color=color, stroke_width=width)
    arm2 = Line([0, 0.74 * h, 0], [0.20 * h, 0.62 * h, 0],
                stroke_color=color, stroke_width=width)
    return VGroup(head, spine, leg1, leg2, arm1, arm2)


def sag_profile(a, amp, t=0.16, nu=0.2, n=40):
    """Cross-section of a rim-supported disc drooping under its own weight.
    The shape is the real plate-bending deflection for a uniformly loaded,
    simply supported circular plate:  w(u) ∝ (1−u²)·(k−u²),  k=(5+ν)/(1+ν).
    `amp` is the centre sag; the rim (u=±1) stays EXACTLY fixed."""
    k = (5.0 + nu) / (1.0 + nu)
    us = np.linspace(-1.0, 1.0, n)
    w = -amp * (1 - us**2) * (k - us**2) / k
    xs = us * a
    top = [np.array([x, t / 2 + wi, 0.0]) for x, wi in zip(xs, w)]
    bot = [np.array([x, -t / 2 + wi, 0.0]) for x, wi in zip(xs[::-1],
                                                            w[::-1])]
    slab = VMobject(stroke_color=CYAN, stroke_width=2.2)
    slab.set_points_as_corners(top + bot + [top[0]])
    slab.set_fill(CYAN, 0.10)
    return slab


def rim_clamp(x, t=0.16, color=DUST):
    """A mount that grips ONLY the rim: back plate + two thin jaws."""
    side = 1 if x > 0 else -1
    back = Rectangle(width=0.10, height=0.62, fill_color=PANEL,
                     fill_opacity=1.0, stroke_color=color, stroke_width=1.3,
                     stroke_opacity=0.7).move_to([x + side * 0.10, 0, 0])
    jaw_t = Rectangle(width=0.30, height=0.075, fill_color=PANEL,
                      fill_opacity=1.0, stroke_color=color, stroke_width=1.3,
                      stroke_opacity=0.7)
    jaw_t.move_to([x - side * 0.06, t / 2 + 0.075, 0])
    jaw_b = jaw_t.copy().move_to([x - side * 0.06, -t / 2 - 0.075, 0])
    return VGroup(back, jaw_t, jaw_b)


# ═══════════════════════════════════════════════════════════════════════════
class Scene5_TwoNewProblems(MovingCameraScene):
    """SCENE 5 — 'Two New Problems'.  The obvious move — just build a bigger
    lens — wins triumphantly in Act 1, then quietly opens two brand-new
    problems: colour blur (chromatic aberration) and a structural ceiling on
    glass itself.  The close is a two-tile summary that deliberately rhymes
    Scene 1's 'Not Enough Light / Can't Tell Detail Apart' pair."""

    # ── director toggles (each is a one-line flip) ────────────────────────
    SHOW_DEFINITION_CARD = True    # Act-2 "aberration — a deviation..." card
    USE_ARCHIVE_OVERLAY  = True    # Act-3 Hevelius engraving via safe_image
    SHOW_RESIDUAL        = True    # Act-4 honest secondary-spectrum leftover
    RESIDUAL_PUSH_IN     = True    # Act-4 brief camera nudge to see it
    LITERAL_FLAW         = True    # Act-5 bubble scatters rays (False = a
                                   #  plain amber diamond glyph over the glass)
    NUMBER_TILES         = True    # Act-6 tiles get "NEW PROBLEM 1 / 2"

    # ── Act-1/2/3 optical bench (world units) ─────────────────────────────
    LX     = -2.2                  # objective lens plane
    F0     = 4.2                   # opening focal length  → focus at x = 2.0
    X_IN   = -7.0                  # where parallel starlight enters frame
    X_MISS = 7.4                   # where uncaught rays leave frame
    LADDER = [0.25, 0.50, 0.80, 1.30, 1.70]          # ray heights (± each)
    A_STEPS = [0.62, 1.05, 1.50, 1.95]               # aperture level-ups

    # ── Act-3 scale (the joke is exact) ───────────────────────────────────
    F_MID   = 8.5                  # "the fix works" checkpoint
    F_LONG  = 26.0                 # the absurd endpoint
    TUBE_M  = 46.0                 # metres — the on-screen number
    HUMAN_M = 1.7                  # metres — so the figure's height is
                                   #  DERIVED: 26 · 1.7/46 ≈ 0.96 units
    GROUND_Y = -7.0

    # ── Act-4 doublet bench ───────────────────────────────────────────────
    CX = -1.4                                          # crown plane
    P1 = 0.625                                         # crown power (f₁=1.6)
    #  achromat condition  P₁Δ₁ + P₂Δ₂ = 0  →  P₂ = −P₁·Δ₁/Δ₂
    P2 = -P1 * DISP_CROWN / DISP_FLINT                 # flint power (−0.3125)
    #  total power 0.3125 → the doublet's focus lands at CX + 3.2 = 1.8

    # ── Act-5 ceiling bench ───────────────────────────────────────────────
    LX5, F5, A5 = -1.9, 3.8, 1.75
    BUBBLE_Y, BUBBLE_R = 0.76, 0.085
    SAG_K = 0.45 / 2.6**4          # centre sag ∝ a⁴  (fixed thickness):
                                   #  the honest plate-bending scaling law

    # ═══════════════════════════════════════════════════════════════════
    def construct(self):
        self.camera.frame.save_state()
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()
        self.wait(0.4)
        self.add(self.frame_marks)
        self.play(self.frame_marks.animate.set_opacity(1.0), run_time=0.8)

        self.act1_just_go_bigger()
        self.act2_chromatic_aberration()
        self.act3_stretching_the_tube()
        self.act4_the_achromatic_doublet()
        self.act5_the_mechanical_ceiling()
        self.act6_two_new_problems()

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
    #  RAY GEOMETRY — every path in this scene comes out of these two
    # ═══════════════════════════════════════════════════════════════════
    def _P_single(self, s):
        """Power of the single crown objective at wavelength s."""
        return (1.0 / self.F0) * (1 + DISP_CROWN * g_shape(s, BOW_CROWN))

    def _P_at_F(self, s, F):
        """Same lens, reground weaker so its mid-band focal length is F —
        the Act-3 stretch. Dispersion rides the power, as it must."""
        return (1.0 / F) * (1 + DISP_CROWN * g_shape(s, BOW_CROWN))

    def _P_doublet(self, s):
        """Crown + flint in contact. The linear colour terms cancel by
        construction; the bow mismatch survives = secondary spectrum."""
        bow_f = BOW_FLINT if self.SHOW_RESIDUAL else BOW_CROWN
        return (self.P1 * (1 + DISP_CROWN * g_shape(s, BOW_CROWN))
                + self.P2 * (1 + DISP_FLINT * g_shape(s, bow_f)))

    def _colored_ray(self, y, s, lens_x, power, x_in, overshoot=0.6,
                     width=1.9, opacity=0.95):
        """One wavelength: in parallel at height y, out with slope −y·P(s),
        drawn just past its own axis crossing so the stagger reads."""
        m = -y * power
        x_end = lens_x + 1.0 / power + overshoot
        ray = VMobject(stroke_color=wave_color(s), stroke_width=width,
                       stroke_opacity=opacity)
        ray.set_points_as_corners([
            [x_in, y, 0], [lens_x, y, 0],
            [x_end, y + m * (x_end - lens_x), 0]])
        return ray

    # ═══════════════════════════════════════════════════════ ACT 1 ═══════
    def act1_just_go_bigger(self):
        """The funnel diagram returns.  A modest lens catches a thin handful
        of rays; a ghost of a star sits at the focus.  Three level-ups in
        quick succession — each one sweeps in rays that were sailing past,
        and the star answers, brightening step by step.  Triumphant."""
        P0 = 1.0 / self.F0
        FX = self.LX + self.F0

        # the full ray field: every height exists from frame one; capture is
        # what CHANGES.  Uncaught = bright to the lens plane, DUST beyond.
        self.straight = {}          # y -> VGroup(in-segment, out-segment)
        self.bent = {}              # y -> the captured polyline
        field = VGroup()
        for y in self.LADDER:
            for yy in (y, -y):
                seg_in = Line([self.X_IN, yy, 0], [self.LX, yy, 0],
                              stroke_color=STARLIGHT, stroke_width=1.6,
                              stroke_opacity=0.42)
                seg_out = Line([self.LX, yy, 0], [self.X_MISS, yy, 0],
                               stroke_color=STARLIGHT, stroke_width=1.3,
                               stroke_opacity=0.16)
                self.straight[yy] = VGroup(seg_in, seg_out)
                field.add(self.straight[yy])

        def captured(yy):
            r = VMobject(stroke_color=STARLIGHT, stroke_width=1.9,
                         stroke_opacity=0.88)
            r.set_points_as_corners([[self.X_IN, yy, 0], [self.LX, yy, 0],
                                     [FX, 0, 0]])
            return r

        A = self.A_STEPS[0]
        self.lens = biconvex(h=2 * A + 0.14, bulge=0.85, color=CYAN,
                             width=2.6, fill_op=0.10)
        self.lens.move_to([self.LX, 0, 0]).set_z_index(5)
        self.star = soft_dot([FX, 0, 0], 0.05, STARLIGHT, 0.20).set_z_index(6)

        lbl = mono("THE FUNNEL · ONE OBJECTIVE LENS", STARLIGHT, 20)
        lbl.to_edge(UP, buff=0.62)

        self.play(Create(self.lens), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(LaggedStart(*[Create(g) for g in field],
                              lag_ratio=0.05, run_time=1.5),
                  FadeIn(lbl), rate_func=rate_functions.ease_out_cubic)

        # the opening capture: only the innermost rays fold to the focus
        first = [yy for y in self.LADDER for yy in (y, -y) if abs(yy) <= A]
        anims = []
        for yy in first:
            self.bent[yy] = captured(yy)
            anims.append(ReplacementTransform(self.straight.pop(yy),
                                              self.bent[yy]))
        self.play(LaggedStart(*anims, lag_ratio=0.1, run_time=1.1),
                  FadeIn(self.star, scale=0.6),
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.1)      # a faint dot — barely a star at all

        # ── the three level-ups ──  (>>> POST: a rising tone on EACH step,
        #  pitch climbing with the diameter — cut it dead on the Act-2 cut.)
        star_ops = [0.42, 0.68, 0.98]
        star_rs = [0.068, 0.088, 0.115]
        for i, A_new in enumerate(self.A_STEPS[1:]):
            A_old = self.A_STEPS[i]
            lens_new = biconvex(h=2 * A_new + 0.14, bulge=0.85, color=CYAN,
                                width=2.6, fill_op=0.10)
            lens_new.move_to([self.LX, 0, 0]).set_z_index(5)
            fresh = [yy for y in self.LADDER for yy in (y, -y)
                     if A_old < abs(yy) <= A_new]
            star_new = soft_dot([FX, 0, 0], star_rs[i], STARLIGHT,
                                star_ops[i]).set_z_index(6)
            anims = [Transform(self.lens, lens_new),
                     Transform(self.star, star_new)]
            for yy in fresh:
                self.bent[yy] = captured(yy)
                anims.append(ReplacementTransform(self.straight.pop(yy),
                                                  self.bent[yy]))
            self.play(*anims, run_time=0.75,
                      rate_func=rate_functions.ease_in_out_sine)
            self.wait(0.3)

        self.wait(1.3)      # the win, complete: a clean bright point
        self._a1 = dict(lbl=lbl)

    # ═══════════════════════════════════════════════════════ ACT 2 ═══════
    def act2_chromatic_aberration(self):

        FX = self.LX + self.F0

        # the hard cut: rush in, everything but the hero pair drops away
        # (>>> POST: the rising tone from Act 1 cuts off dead, right here.)
        hero = [1.70, -1.70]
        dim_others = [self.bent[yy].animate.set_stroke(opacity=0.07)
                      for yy in self.bent if yy not in hero]
        dim_others += [g.animate.set_stroke(opacity=0.05)
                       for g in self.straight.values()]
        self.play(self.camera.frame.animate.set(width=7.2)
                      .move_to([0.4, 0.30, 0]),
                  FadeOut(self._a1["lbl"]),
                  *dim_others,
                  run_time=0.55, rate_func=rate_functions.rush_into)
        self.wait(0.35)

        axis = DashedLine([self.LX, 0, 0], [3.4, 0, 0], dash_length=0.09,
                          dashed_ratio=0.5, stroke_color=C_GROUND,
                          stroke_width=1.1, stroke_opacity=0.4)
        self.play(Create(axis), run_time=0.7,
                  rate_func=rate_functions.ease_in_out_sine)

        # the fan: five wavelengths per side, splitting AT the glass.
        # Slopes come from P(λ) — the fan is the lens equation, not styling.
        self.fan = VGroup()
        for s in S_VALS:
            for y in hero:
                self.fan.add(self._colored_ray(y, s, self.LX,
                                               self._P_single(s), self.LX))
        self.fan.set_z_index(4)
        self.play(LaggedStart(*[Create(r) for r in self.fan],
                              lag_ratio=0.04, run_time=1.5),
                  self.bent[1.70].animate.set_stroke(opacity=0.10),
                  self.bent[-1.70].animate.set_stroke(opacity=0.10),
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        # three distinct convergence points, staggered along the axis —
        # cyan crosses early, amber late.  Hold on that offset.
        self.cross_dots = VGroup(*[
            Dot([self.LX + 1.0 / self._P_single(s), 0, 0], radius=0.05,
                color=wave_color(s)) for s in (1.0, 0.0, -1.0)])
        self.cross_dots.set_z_index(7)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4)
                                for d in self.cross_dots],
                              lag_ratio=0.3, run_time=1.0),
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(1.2)

        # the halo blooms where the single clean point should have been —
        # Act 1's star dot IS what it turns into.
        # (>>> POST: soft dissonant sting lands exactly on this bloom.)
        x_h = self.LX + self.F0 * 1.0
        self.halo = VGroup(
            Circle(radius=0.40, stroke_width=0, fill_color=AMBER,
                   fill_opacity=0.10),
            Circle(radius=0.26, stroke_width=0, fill_color=CYAN,
                   fill_opacity=0.13),
            Circle(radius=0.10, stroke_width=0, fill_color=STARLIGHT,
                   fill_opacity=0.30)).move_to([x_h, 0, 0]).set_z_index(6)
        self.play(ReplacementTransform(self.star, self.halo),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)

        title = serif("Chromatic Aberration", STARLIGHT, 34, italic=False)
        title.move_to([0.4, 1.75, 0])
        self.play(Write(title))
        self.wait(0.7)

        card = VGroup()
        if self.SHOW_DEFINITION_CARD:
            plate = RoundedRectangle(width=4.9, height=1.05,
                                     corner_radius=0.07, stroke_color=DUST,
                                     stroke_width=1.2, stroke_opacity=0.45,
                                     fill_color=PANEL, fill_opacity=0.85)
            tag = mono("ABERRATION", AMBER, 11)
            body = serif("a deviation from what's expected", STARLIGHT, 21)
            tag.move_to(plate.get_top() + DOWN * 0.30)
            body.move_to(plate.get_center() + DOWN * 0.17)
            card = VGroup(plate, tag, body).move_to([0.4, -1.10, 0])
            card.set_z_index(9)
            self.play(FadeIn(card, shift=UP * 0.12), run_time=0.8,
                      rate_func=rate_functions.ease_out_cubic)
        self.wait(1.7)

        self._a2 = dict(title=title, card=card, axis=axis)

    # ═══════════════════════════════════════════════════════ ACT 3 ═══════
    def act3_stretching_the_tube(self):
        self.Ftr = ValueTracker(self.F0)
        self.a3_op = ValueTracker(1.0)      # one dimmer for all live optics
        hero = [1.70, -1.70]

        # ── live replacements for Act 2's statics (identical at F = F0,
        #     so the swap is invisible) ──
        def live_lens():
            F = self.Ftr.get_value()
            op = self.a3_op.get_value()
            ln = biconvex(h=2 * 1.95 + 0.14, bulge=0.85 * self.F0 / F,
                          color=CYAN, width=2.6, fill_op=0.10 * op)
            ln.set_stroke(opacity=0.9 * op)
            ln.move_to([self.LX, 0, 0]).set_z_index(5)
            return ln

        def live_fan():
            F = self.Ftr.get_value()
            op = self.a3_op.get_value()
            g = VGroup()
            for s in S_VALS:
                for y in hero:
                    g.add(self._colored_ray(y, s, self.LX,
                                            self._P_at_F(s, F), self.LX,
                                            overshoot=0.14 * F,
                                            opacity=0.95 * op))
            return g.set_z_index(4)

        def live_dots():
            F = self.Ftr.get_value()
            op = self.a3_op.get_value()
            return VGroup(*[
                Dot([self.LX + 1.0 / self._P_at_F(s, F), 0, 0], radius=0.05,
                    color=wave_color(s), fill_opacity=0.9 * op)
                for s in (1.0, 0.0, -1.0)]).set_z_index(7)

        def live_halo():

            F = self.Ftr.get_value()
            op = self.a3_op.get_value()
            return VGroup(
                Circle(radius=0.40, stroke_width=0, fill_color=RED,
                       fill_opacity=0.5 * op),
                Circle(radius=0.26, stroke_width=0, fill_color=BLUE,
                       fill_opacity=0.5 * op),
                Circle(radius=0.10, stroke_width=0, fill_color=WHITE,
                       fill_opacity=0.5 * op)
            ).move_to([self.LX + F, 0, 0]).set_z_index(6)

        def live_axis():
            F = self.Ftr.get_value()
            op = self.a3_op.get_value()
            return DashedLine([self.LX, 0, 0], [self.LX + F + 0.16 * F, 0, 0],
                              dash_length=0.09, dashed_ratio=0.5,
                              stroke_color=C_GROUND, stroke_width=1.1,
                              stroke_opacity=0.4 * op)

        # ── the eyepiece-view inset: what the OBSERVER sees.  Its halo
        #     radius is the angular blur  ∝ D·Δ/F — real optics, one line ──
        self.ins_op = ValueTracker(0.0)

        def live_inset():
            f = self.camera.frame
            scl = f.get_width() / config.frame_width
            op = self.ins_op.get_value()
            c = f.get_corner(UR) + (LEFT * 2.05 + DOWN * 1.85) * scl
            R = 0.92 * scl
            frac = 0.62 * self.F0 / self.Ftr.get_value()
            plate = Circle(radius=R, stroke_color=DUST, stroke_width=1.4,
                           stroke_opacity=0.55 * op, fill_color=PANEL,
                           fill_opacity=0.82 * op).move_to(c)
            halo_a = Circle(radius=max(frac * R, 0.028 * R), stroke_width=0,
                            fill_color=RED,
                            fill_opacity=0.13 * op).move_to(c)
            halo_c = Circle(radius=max(frac * R * 0.63, 0.02 * R),
                            stroke_width=0, fill_color=BLUE,
                            fill_opacity=0.16 * op).move_to(c)
            core = Dot(c, radius=0.07 * R, fill_color=WHITE,
                       fill_opacity=(0.35 + 0.6 * (1 - frac / 0.62)) * op)
            lbl = Text("THROUGH THE EYEPIECE", font=MONO, font_size=20,
                       color=DUST)
            lbl.set(height=0.105 * scl)
            lbl.next_to(plate, DOWN, buff=0.14 * scl)
            return VGroup(plate, halo_a, halo_c, core, lbl).set_z_index(30)

        L_lens, L_fan = always_redraw(live_lens), always_redraw(live_fan)
        L_dots, L_halo = always_redraw(live_dots), always_redraw(live_halo)
        L_axis, L_ins = always_redraw(live_axis), always_redraw(live_inset)

        # Morph the Act-2 statics INTO the (frozen-at-F0) live-twin shapes, so
        # the originals visibly become the new rays and then leave the scene —
        # nothing of the originals lingers.  The frozen targets are identical
        # at F = F0, so each transform starts right on top of its source and
        # the change reads as a clean hand-off, not a pop.
        fan_t, lens_t = live_fan(), live_lens()
        dots_t, halo_t, axis_t = live_dots(), live_halo(), live_axis()
        leftovers = VGroup(*self.bent.values(), *self.straight.values())
        self.play(
            ReplacementTransform(self.fan, fan_t),
            ReplacementTransform(self.lens, lens_t),
            ReplacementTransform(self.cross_dots, dots_t),
            ReplacementTransform(self.halo, halo_t),
            ReplacementTransform(self._a2["axis"], axis_t),
            FadeOut(leftovers),
            FadeOut(self._a2["title"]), FadeOut(self._a2["card"]),
            run_time=0.7, rate_func=rate_functions.ease_in_out_sine)
        # the morph targets were one-shot statics; drop them and hand the
        # frame to the live (always-redrawing) twins that drive the stretch
        self.remove(fan_t, lens_t, dots_t, halo_t, axis_t)
        self.add(L_axis, L_fan, L_lens, L_dots, L_halo, L_ins)

        # ── beat A: the fix, genuinely working ──
        mid_cx = (2 * self.LX + self.F_MID) / 2 + 0.6
        self.play(self.Ftr.animate.set_value(self.F_MID),
                  self.ins_op.animate.set_value(1.0),
                  self.camera.frame.animate.set(width=13.4)
                      .move_to([mid_cx, 0.15, 0]),
                  run_time=3.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.2)      # flatter bend, tighter point — it WORKS

        # ── beat B: ...and what it costs.  Ground, mast and a human enter
        #     the frame only because the camera is forced this far back. ──
        gy = self.GROUND_Y
        ground = Line([-5.4, gy, 0], [28.2, gy, 0], stroke_color=C_GROUND,
                      stroke_width=2.0, stroke_opacity=0.55)
        hatch = VGroup(*[Line([x, gy - 0.02, 0], [x - 0.34, gy - 0.42, 0],
                              stroke_color=C_GROUND, stroke_width=1.2,
                              stroke_opacity=0.4)
                         for x in np.arange(-4.4, 28.0, 2.6)])
        mast = Line([self.LX, gy, 0], [self.LX, -2.06, 0],
                    stroke_color=DUST, stroke_width=2.6, stroke_opacity=0.8)
        guys = VGroup(
            Line([self.LX, -2.06, 0], [self.LX - 2.9, gy, 0],
                 stroke_color=DUST, stroke_width=1.1, stroke_opacity=0.30),
            Line([self.LX, -2.06, 0], [self.LX + 2.9, gy, 0],
                 stroke_color=DUST, stroke_width=1.1, stroke_opacity=0.30))
        human_h = self.F_LONG * self.HUMAN_M / self.TUBE_M   # ≈ 0.96 — exact
        person = tiny_observer(human_h).move_to([-0.55, gy, 0],
                                                aligned_edge=DOWN)
        eyepiece = biconvex(h=0.5, bulge=1.4, color=CYAN, width=2.0,
                            fill_op=0.14)
        eyepiece.move_to([self.LX + self.F_LONG + 0.4, 0, 0]).set_z_index(5)
        rig = VGroup(ground, hatch, mast, guys, person, eyepiece)
        rig.set_opacity(0.0)
        self.add(rig)

        # (>>> POST: gentle handheld wobble rides this whole wide shot —
        #  a quiet nod to how unsteerable these rigs really were.)
        end_cx = self.LX + self.F_LONG / 2 + 0.6
        self.play(self.Ftr.animate.set_value(self.F_LONG),
                  self.camera.frame.animate.set(width=33.5)
                      .move_to([end_cx, -2.5, 0]),
                  rig.animate.set_opacity(1.0),
                  run_time=4.6, rate_func=rate_functions.ease_in_out_sine)

        # the number lands the instant the whole length is finally visible
        dim_y = -3.7
        dline = Line([self.LX, dim_y, 0], [self.LX + self.F_LONG, dim_y, 0],
                     stroke_color=C_LEN, stroke_width=1.6, stroke_opacity=0.9)
        t1 = Line([self.LX, dim_y - 0.22, 0], [self.LX, dim_y + 0.22, 0],
                  stroke_color=C_LEN, stroke_width=1.6)
        t2 = t1.copy().shift(RIGHT * self.F_LONG)
        meters = serif("46 meters", STARLIGHT, 84)
        meters.move_to([end_cx, dim_y - 1.35, 0])
        self.play(Create(VGroup(t1, dline, t2)), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(Write(meters), run_time=1.0)
        self.wait(1.6)      # let the absurdity sit — imagine aiming this

        overlay = Group()
        if self.USE_ARCHIVE_OVERLAY:
            img = safe_image("ariel_telescope.jpg", 7.2,
                             "AERIAL TELESCOPE ENGRAVING")
            frame = VGroup(*[corner_L(o, size=0.30, opacity=0.85)
                             for o in (UL, UR, DL, DR)])
            cap = mono("HEVELIUS · AERIAL TELESCOPE · 1673", DUST, 25)
            overlay = Group(img, frame, cap)
            img.move_to([19.5, -6.6, 0])
            for c in frame:
                c.move_to(np.array(img.get_corner(c.anchor))
                          + c.anchor * 0.10, aligned_edge=c.anchor)
            cap.next_to(img, DOWN, buff=0.30)
            self.play(FadeIn(overlay, shift=UP * 0.18), run_time=0.9,
                      rate_func=rate_functions.ease_out_cubic)
            self.wait(2.4)  # "this actually existed"

        # exit: the whole tableau breathes out; camera comes home
        self.play(self.a3_op.animate.set_value(0.0),
                  self.ins_op.animate.set_value(0.0),
                  FadeOut(rig), FadeOut(meters),
                  FadeOut(VGroup(dline, t1, t2)), FadeOut(overlay),
                  Restore(self.camera.frame),
                  run_time=2.0, rate_func=rate_functions.ease_in_out_sine)
        self.remove(L_lens, L_fan, L_dots, L_halo, L_axis, L_ins)
        self.wait(0.3)

    # ═══════════════════════════════════════════════════════ ACT 4 ═══════
    def act4_the_achromatic_doublet(self):
        """The smart fix.  A crown lens shows the familiar stagger; a flint
        element with the OPPOSITE flaw slides in and locks against it.  The
        same rays reflow through the pair — the crossings sweep together
        and all but meet.  All but: the secondary spectrum stays, faint and
        honest."""
        crown = biconvex(h=1.5, bulge=1.0, color=CYAN, width=2.4,
                         fill_op=0.11).move_to([self.CX, 0, 0]).set_z_index(5)
        axis = DashedLine([self.CX, 0, 0], [3.1, 0, 0], dash_length=0.09,
                          dashed_ratio=0.5, stroke_color=C_GROUND,
                          stroke_width=1.1, stroke_opacity=0.4)
        crown_tag = mono("CROWN", DUST, 14).move_to([self.CX - 0.1, -1.35, 0])

        self.play(Create(crown), Create(axis), FadeIn(crown_tag),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_sine)

        # the familiar stagger, restated quickly on the compact bench
        heights = [0.60, -0.60]
        P_crown = lambda s: self.P1 * (1 + DISP_CROWN * g_shape(s, BOW_CROWN))
        fan = VGroup(*[self._colored_ray(y, s, self.CX, P_crown(s), -4.9,
                                         overshoot=0.55)
                       for s in S_VALS for y in heights]).set_z_index(4)
        dots = VGroup(*[Dot([self.CX + 1.0 / P_crown(s), 0, 0], radius=0.05,
                            color=wave_color(s)) for s in (1.0, 0.0, -1.0)])
        dots.set_z_index(7)
        self.play(LaggedStart(*[Create(r) for r in fan],
                              lag_ratio=0.04, run_time=1.2),
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in dots],
                              lag_ratio=0.25, run_time=0.7))
        self.wait(0.9)      # same disease, smaller patient

        # the flint arrives — complementary curvature, and it LOCKS.
        flint = flint_element(h=1.5, mate_bulge=1.0).set_z_index(5)
        flint.shift([self.CX + 5.6, 0, 0])
        flint_tag = mono("FLINT", DUST, 14).move_to([self.CX + 0.75,
                                                     -1.35, 0])
        flint_tag.set_opacity(0.0)
        self.add(flint_tag)
        self.play(flint.animate.shift(LEFT * 5.6),
                  flint_tag.animate.set_opacity(1.0),
                  run_time=1.0, rate_func=rate_functions.ease_out_cubic)
        # (>>> POST: a clean snap/click EXACTLY on this seam blink.)
        seam = ArcBetweenPoints([self.CX, 0.75, 0], [self.CX, -0.75, 0],
                                angle=1.0, stroke_color=AMBER,
                                stroke_width=3.0, stroke_opacity=0.0)
        self.add(seam)
        self.play(seam.animate.set_stroke(opacity=0.9), run_time=0.18)
        self.play(seam.animate.set_stroke(opacity=0.0), run_time=0.4)
        self.remove(seam)
        self.wait(0.4)

        # re-run the test: the SAME rays reflow through the pair.
        # Crossings sweep right and pull together — nearly one point.
        fan2 = VGroup(*[self._colored_ray(y, s, self.CX, self._P_doublet(s),
                                          -4.9, overshoot=0.55)
                        for s in S_VALS for y in heights]).set_z_index(4)
        dots2 = VGroup(*[Dot([self.CX + 1.0 / self._P_doublet(s), 0, 0],
                             radius=0.05, color=wave_color(s))
                         for s in (1.0, 0.0, -1.0)]).set_z_index(7)
        self.play(ReplacementTransform(fan, fan2),
                  ReplacementTransform(dots, dots2),
                  run_time=1.8, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)

        title = serif("Achromatic Doublet", STARLIGHT, 36, italic=False)
        title.move_to([0, 2.55, 0])
        date = mono("1700s", AMBER, 14).next_to(title, DOWN, buff=0.22)
        self.play(Write(title), FadeIn(date), run_time=1.1)
        self.wait(0.6)

        # the honest residual: push in until the leftover offset is visible
        note = VGroup()
        if self.SHOW_RESIDUAL and self.RESIDUAL_PUSH_IN:
            fx = self.CX + 1.0 / self._P_doublet(1.0)     # merged pair
            self.play(self.camera.frame.animate.set(width=1.9)
                          .move_to([fx - 0.05, 0, 0]),
                      run_time=1.5, rate_func=rate_functions.ease_in_out_sine)
            note = mono("NOT COMPLETELY GONE", DUST, 24)
            note.set(height=0.052).move_to([fx - 0.05, -0.30, 0])
            self.play(FadeIn(note, shift=UP * 0.03), run_time=0.6)
            self.wait(1.5)      # small truth, kept
            self.play(Restore(self.camera.frame), FadeOut(note),
                      run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.0)

        self._a4 = dict(crown=crown, flint=flint, fan=fan2, dots=dots2,
                        axis=axis, title=title, date=date,
                        tags=VGroup(crown_tag, flint_tag))

    # ═══════════════════════════════════════════════════════ ACT 5 ═══════
    def act5_the_mechanical_ceiling(self):
        """Colour was fixable.  Size is not.  Beat one: a single buried flaw
        scatters the light that touches it.  Beat two: even flawless glass,
        held only by its rim, bows under its own weight — and the sag grows
        as the FOURTH power of the diameter."""
        a4 = self._a4
        FX5 = self.LX5 + self.F5

        # the doublet grows back into Act 1's big single lens — the problem
        # changes shape mid-air: colour is done, size begins.
        big = biconvex(h=2 * self.A5 + 0.14, bulge=0.80, color=CYAN,
                       width=2.6, fill_op=0.10)
        big.move_to([self.LX5, 0, 0]).set_z_index(5)
        self.play(FadeOut(a4["fan"]), FadeOut(a4["dots"]),
                  FadeOut(a4["axis"]), FadeOut(a4["title"]),
                  FadeOut(a4["date"]), FadeOut(a4["tags"]),
                  ReplacementTransform(VGroup(a4["crown"], a4["flint"]), big),
                  run_time=1.5, rate_func=rate_functions.ease_in_out_sine)

        # ── beat A: one flaw inside the glass ──
        ys5 = [0.30, 0.62, 0.90, 1.30]
        clean, scattered = {}, {}
        for y in ys5:
            for yy in (y, -y):
                r = VMobject(stroke_color=STARLIGHT, stroke_width=1.9,
                             stroke_opacity=0.88)
                r.set_points_as_corners([[-6.6, yy, 0], [self.LX5, yy, 0],
                                         [FX5, 0, 0]])
                clean[yy] = r
        star = soft_dot([FX5, 0, 0], 0.10, STARLIGHT, 0.95).set_z_index(6)
        self.play(LaggedStart(*[Create(clean[k]) for k in clean],
                              lag_ratio=0.06, run_time=1.2),
                  FadeIn(star, scale=0.6),
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.9)      # flawless glass: a clean point.  For now.

        if self.LITERAL_FLAW:
            bubble = Circle(radius=self.BUBBLE_R, stroke_color=DUST,
                            stroke_width=1.6, stroke_opacity=0.9,
                            fill_color=VOID, fill_opacity=0.85)
            bubble.move_to([self.LX5 + 0.05, self.BUBBLE_Y, 0])
            bubble.set_z_index(8)
        else:
            bubble = Square(side_length=0.17, stroke_color=AMBER,
                            stroke_width=2.0).rotate(PI / 4)
            bubble.move_to([self.LX5 + 0.05, self.BUBBLE_Y, 0])
            bubble.set_z_index(8)
        flaw_lbl = mono("A FLAW INSIDE", DUST, 13)
        flaw_lbl.move_to([self.LX5 - 1.9, 1.9, 0])
        leader = DashedLine(flaw_lbl.get_bottom() + DOWN * 0.08,
                            bubble.get_center() + UL * 0.12,
                            dash_length=0.07, dashed_ratio=0.5,
                            stroke_color=DUST, stroke_width=1.0,
                            stroke_opacity=0.35)
        self.play(FadeIn(bubble, scale=0.4), FadeIn(flaw_lbl), Create(leader),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.5)

        # a void in glass is a little DIVERGING lens: rays that pass it get
        # pushed away from its centre and spray past the focus.
        SC = 0.10
        anims = []
        for yy in (0.62, 0.90):
            dv = SC * np.sign(yy - self.BUBBLE_Y)
            m = -yy / self.F5 + dv
            x_e = FX5 + 1.0
            r = VMobject(stroke_color=STARLIGHT, stroke_width=1.9,
                         stroke_opacity=0.80)
            r.set_points_as_corners([[-6.6, yy, 0], [self.LX5, yy, 0],
                                     [x_e, yy + m * (x_e - self.LX5), 0]])
            scattered[yy] = r
            anims.append(ReplacementTransform(clean.pop(yy), r))
        blotch = VGroup(
            Ellipse(width=0.16, height=1.0, stroke_width=0,
                    fill_color=STARLIGHT, fill_opacity=0.10),
            Ellipse(width=0.10, height=0.55, stroke_width=0,
                    fill_color=STARLIGHT, fill_opacity=0.10))
        blotch.move_to([FX5, 0.02, 0]).set_z_index(5)
        star_dim = soft_dot([FX5, 0, 0], 0.10, STARLIGHT, 0.38).set_z_index(6)
        self.play(*anims, Transform(star, star_dim), FadeIn(blotch),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.5)      # one bubble.  The whole point smears.

        beatA = VGroup(big, *clean.values(), *scattered.values(), star,
                       bubble, flaw_lbl, leader, blotch)
        self.play(FadeOut(beatA), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)

        # ── beat B: even flawless glass can't hold its own shape ──
        y0 = 0.45
        a_tr = ValueTracker(1.1)

        def live_slab():
            a = a_tr.get_value()
            slab = sag_profile(a, self.SAG_K * a**4)
            return slab.shift(UP * y0).set_z_index(5)

        def live_clamps():
            a = a_tr.get_value()
            return VGroup(rim_clamp(-a), rim_clamp(a)).shift(UP * y0)

        def live_ref():
            a = a_tr.get_value()
            return DashedLine([-a - 0.75, y0, 0], [a + 0.75, y0, 0],
                              dash_length=0.09, dashed_ratio=0.5,
                              stroke_color=DUST, stroke_width=1.0,
                              stroke_opacity=0.30)

        S_slab = always_redraw(live_slab)
        S_clamps = always_redraw(live_clamps)
        S_ref = always_redraw(live_ref)
        self.play(FadeIn(VGroup(S_ref, S_clamps, S_slab)), run_time=0.9,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.6)      # small disc, dead flat in its ring

        # the push outward.  Sag ∝ a⁴ — the droop arrives all at once.
        # (>>> POST: one very subtle low creak, right as the middle lets go.)
        self.play(a_tr.animate.set_value(2.6), run_time=3.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.7)

        edge_txt = serif("supported only at the edge", STARLIGHT, 28)
        edge_txt.move_to([0, -1.75, 0])
        self.play(Write(edge_txt), run_time=1.1)
        self.wait(0.9)

        # scale witness: a small disc holds; the big one cannot.  Identical
        # mounts — the rim is all either of them gets.
        big_now = live_slab().copy()
        big_clamps = live_clamps().copy()
        big_ref = live_ref().copy()
        self.remove(S_slab, S_clamps, S_ref)
        big_grp = VGroup(big_ref, big_clamps, big_now)
        self.add(big_grp)

        a_s = 0.95
        small_grp = VGroup(
            DashedLine([-a_s - 0.55, y0, 0], [a_s + 0.55, y0, 0],
                       dash_length=0.09, dashed_ratio=0.5, stroke_color=DUST,
                       stroke_width=1.0, stroke_opacity=0.30),
            VGroup(rim_clamp(-a_s), rim_clamp(a_s)).shift(UP * y0),
            sag_profile(a_s, self.SAG_K * a_s**4).shift(UP * y0))
        small_grp.shift(LEFT * 4.35)
        self.play(big_grp.animate.shift(RIGHT * 2.35),
                  FadeIn(small_grp, shift=RIGHT * 0.25),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait(2.0)      # bigger has quietly stopped meaning better

        self._a5 = VGroup(big_grp, small_grp, edge_txt)

    # ═══════════════════════════════════════════════════════ ACT 6 ═══════
    def act6_two_new_problems(self):
        """The crux: the two-tile summary, a deliberate structural echo of
        Scene 1's closing pair.  Hold it.  Then the question Scene 6 exists
        to answer."""
        self.play(FadeOut(self._a5), run_time=1.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)

        tileA = self._tile_halo().shift(LEFT * 3.4 + UP * 0.4)
        tileB = self._tile_sag().shift(RIGHT * 3.4 + UP * 0.4)
        self.play(
            LaggedStart(FadeIn(tileA, shift=RIGHT * 0.3),
                        FadeIn(tileB, shift=LEFT * 0.3),
                        lag_ratio=0.25, run_time=1.4),
            rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        labA = serif("Color Blur", STARLIGHT, 30, italic=False)
        labB = serif("Can't Get Bigger", STARLIGHT, 30, italic=False)
        labA.next_to(tileA, DOWN, buff=0.4)
        labB.next_to(tileB, DOWN, buff=0.4)
        self.play(Write(labA), Write(labB), run_time=1.0)

        if self.NUMBER_TILES:
            n1 = mono("NEW PROBLEM 1", AMBER, 12).next_to(tileA, UP, buff=0.35)
            n2 = mono("NEW PROBLEM 2", AMBER, 12).next_to(tileB, UP, buff=0.35)
            self.play(FadeIn(n1), FadeIn(n2), run_time=0.6)

        # ── the true crux: hold the pair in stillness ──
        # (>>> POST: near-silence here; let the wall land before the hook.)
        self.wait(2.8)

        question = serif("What if light didn't have to pass through glass "
                         "at all?", STARLIGHT, 34)
        question.to_edge(DOWN, buff=0.85)
        rule = Line(LEFT * 0.7, RIGHT * 0.7, stroke_color=AMBER,
                    stroke_width=1.5).next_to(question, UP, buff=0.35)
        self.play(Create(rule), run_time=0.5)
        self.play(Write(question), run_time=1.4)
        self.wait(3.0)      # Scene 6's opening move answers this directly

        self.play(*[FadeOut(m) for m in self.mobjects
                    if m is not self.frame_marks],
                  self.frame_marks.animate.set_opacity(0.0),
                  run_time=2.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

    # ── Act-6 tile builders (same frame grammar as Scene 1's pair) ────────
    def _tile_frame(self):
        plate = RoundedRectangle(width=3.2, height=2.35, corner_radius=0.08,
                                 stroke_color=DUST, stroke_width=1.4,
                                 stroke_opacity=0.5, fill_color=PANEL,
                                 fill_opacity=0.55)
        marks = VGroup()
        for o in (UL, UR, DL, DR):
            c = corner_L(o, size=0.16, color=AMBER, opacity=0.6)
            c.move_to(plate.get_corner(o), aligned_edge=o)
            marks.add(c)
        return VGroup(plate, marks)

    def _tile_halo(self):
        """Act 2 in miniature: a lens sliver, two colours claiming two foci,
        the fringe halo where one point should be."""
        f = self._tile_frame()
        c = f.get_center()
        sliver = biconvex(h=1.1, bulge=0.65, color=CYAN, width=1.8,
                          fill_op=0.10).move_to(c + LEFT * 1.05)
        lx = sliver.get_center()[0]
        rays = VGroup()
        for s, fx in ((1.0, 0.78), (-1.0, 1.42)):
            for sign in (1, -1):
                rays.add(Line([lx, sign * 0.5, 0],
                              [lx + fx * 1.28, -sign * 0.14, 0],
                              stroke_color=wave_color(s), stroke_width=1.6,
                              stroke_opacity=0.85).shift([0, c[1], 0]))
        halo = VGroup(
            Circle(radius=0.30, stroke_width=0, fill_color=AMBER,
                   fill_opacity=0.14),
            Circle(radius=0.19, stroke_width=0, fill_color=CYAN,
                   fill_opacity=0.16),
            Dot([0, 0, 0], radius=0.045, fill_color=STARLIGHT,
                fill_opacity=0.7)).move_to([lx + 1.42, c[1], 0])
        return VGroup(f, rays, halo, sliver)

    def _tile_sag(self):
        """Act 5 in miniature: rim clamps, a flat plane, and glass that
        couldn't hold it."""
        f = self._tile_frame()
        c = f.get_center()
        icon = VGroup(
            DashedLine([-1.35, 0, 0], [1.35, 0, 0], dash_length=0.08,
                       dashed_ratio=0.5, stroke_color=DUST,
                       stroke_width=1.0, stroke_opacity=0.35),
            sag_profile(1.05, 0.34, t=0.12),
            rim_clamp(-1.05, t=0.12), rim_clamp(1.05, t=0.12))
        icon.move_to(c + DOWN * 0.05)
        return VGroup(f, icon)