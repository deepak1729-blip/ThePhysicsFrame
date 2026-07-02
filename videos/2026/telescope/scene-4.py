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
C_ANGLE   = "#E08AAB"   # ANGLE θ — the one quantity this scene is about
C_LEN     = "#5B8FB0"   # LENGTH / r  (== CYAN)
C_MASS    = "#B89A86"   # MATTER — warm organic tone
C_GROUND  = "#7F8A99"   # ground / reference axis

SERIF = "Spectral"      # ideas; italic is the channel's voice & every equation
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(4)      # deterministic -> stable render cache


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


def safe_image(name, target_width, fallback_label):
    """Load an image by name; if it isn't present yet, return a framed
    placeholder slot so the script always runs as-is."""
    try:
        img = ImageMobject(name)
        img.set(width=target_width)
        return img
    except Exception:
        h = target_width * 1.0
        slot = VGroup()
        plate = Rectangle(width=target_width, height=h,
                          fill_color=PANEL, fill_opacity=1.0,
                          stroke_color=DUST, stroke_width=1.2,
                          stroke_opacity=0.4)
        lbl = Text(fallback_label, font=MONO, font_size=10, color=DUST)
        lbl.move_to(plate.get_center())
        slot.add(plate, lbl)
        return slot
    

def path_from(*segments, **style):
    """Stitch Lines/Arcs into ONE continuous VMobject so Create() draws a
    single unbroken silhouette — no wobble, no seams.  (Verbatim from Scene 1,
    where the eye-in-section and the beaker are built with it.)"""
    p = VMobject(**style)
    for i, seg in enumerate(segments):
        if i == 0:
            p.set_points(seg.get_points())
        else:
            p.add_line_to(seg.get_start())      # (zero-length weld)
            p.append_points(seg.get_points())
    return p

def sectioned_eye(pupil_x, pupil_r=0.42):

    R = pupil_r / 0.19                      # Scene-1 ratio: pupil_r == R * 0.19
    iris_x = pupil_x                         # pupil plane == iris plane
    cx = np.array([iris_x + R - 0.5, 0.0, 0.0])   # (Scene 1: iris_x = cx-R+0.5)
    open_a = 0.46                           # front-opening half-angle
    front = cx + LEFT * R

    sclera = Arc(radius=R, start_angle=PI - open_a, angle=-(TAU - 2 * open_a),
                 arc_center=cx, stroke_color=STARLIGHT,
                 stroke_width=2.0, stroke_opacity=0.5)
    sclera_in = Arc(radius=R - 0.10, start_angle=PI - open_a,
                    angle=-(TAU - 2 * open_a), arc_center=cx,
                    stroke_color=STARLIGHT, stroke_width=1.0,
                    stroke_opacity=0.15)
    globe_fill = Circle(radius=R, stroke_width=0,
                        fill_color=PANEL, fill_opacity=0.30).move_to(cx)

    # cornea: a clear dome over the front opening
    c_top = cx + R * np.array([math.cos(PI - open_a), math.sin(PI - open_a), 0])
    c_bot = cx + R * np.array([math.cos(PI + open_a), math.sin(PI + open_a), 0])
    cornea = ArcBetweenPoints(c_top, c_bot, angle=-1.15,
                              stroke_color=CYAN, stroke_width=1.8,
                              stroke_opacity=0.55)
    cornea.set_fill(CYAN, opacity=0.06)

    # iris: two tapered bodies flanking the pupil (mass, not wire)
    def iris_body(sign):
        y_out = cx[1] + sign * (c_top[1] - cx[1]) * 0.92
        y_in  = cx[1] + sign * pupil_r
        p = Polygon([iris_x - 0.11, y_out, 0], [iris_x + 0.11, y_out, 0],
                    [iris_x + 0.05, y_in, 0], [iris_x - 0.05, y_in, 0],
                    stroke_color=DUST, stroke_width=1.2,
                    stroke_opacity=0.6, fill_color=DUST, fill_opacity=0.40)
        return p.round_corners(radius=0.03)
    iris_top, iris_bot = iris_body(+1), iris_body(-1)

    # the pupil: THE amber circle — the opening in the iris (the motif)
    pupil = make_aperture(pupil_r, width=2.4).move_to([iris_x, cx[1], 0])
    pupil.set_fill(AMBER, opacity=0.10)

    # crystalline lens: truly biconvex — two circular arcs, one body
    lx, lh, bulge = iris_x + 0.55, pupil_r * 1.30, 0.20
    r_arc = (lh * lh + bulge * bulge) / (2 * bulge)
    a0 = math.atan2(lh, -(r_arc - bulge))
    lens_front = Arc(radius=r_arc, start_angle=a0, angle=TAU - 2 * a0,
                     arc_center=[lx + (r_arc - bulge), cx[1], 0])
    a1 = math.atan2(-lh, (r_arc - bulge))
    lens_back = Arc(radius=r_arc, start_angle=a1, angle=-2 * a1,
                    arc_center=[lx - (r_arc - bulge), cx[1], 0])
    lens = path_from(lens_front, lens_back,
                     stroke_color=CYAN, stroke_width=2.0, stroke_opacity=0.8)
    lens.set_fill(CYAN, opacity=0.12)

    # retina: the light-sensitive lining, with a soft inner glow
    retina_arc = Arc(radius=R * 0.9, start_angle=-0.85, angle=1.7,
                     arc_center=cx, stroke_color=DUST,
                     stroke_width=3.0, stroke_opacity=0.7)
    retina_glow = Arc(radius=R * 0.9, start_angle=-0.85, angle=1.7,
                      arc_center=cx, stroke_color=AMBER,
                      stroke_width=9.0, stroke_opacity=0.06)

    # optic nerve: a short bundle leaving the back, slightly below axis
    n_ang = -0.30
    n_pt = cx + R * np.array([math.cos(n_ang), math.sin(n_ang), 0])
    n_dir = np.array([math.cos(n_ang), math.sin(n_ang), 0])
    n_perp = np.array([-n_dir[1], n_dir[0], 0])
    nerve = VGroup(*[
        Line(n_pt + n_perp * o, n_pt + n_perp * o * 0.6 + n_dir * 0.75,
             stroke_color=DUST, stroke_width=1.4, stroke_opacity=0.40)
        for o in (-0.10, 0.0, 0.10)])

    eye = VGroup(globe_fill, sclera_in, sclera, cornea, retina_glow,
                 retina_arc, nerve, lens, iris_top, iris_bot, pupil)
    eye.pupil = pupil
    eye.center = cx
    eye.R = R
    return eye

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
    """A lens cross-section — identical builder to Scenes 2–3."""
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


def soft_blob(radius=0.9, layers=7, color=STARLIGHT, seed=7):
    """The series' poorly-resolved texture — used here in reverse: it is
    what the floating Moon image resolves OUT of."""
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


# ═══════════════════════════════════════════════════════════════════════════
class Scene4_TheAngleTrick(MovingCameraScene):

    # ── director toggles (each is a one-line flip) ────────────────────────
    SHOW_QUESTION_TEXT = False   # Act-1 "So... why does it look closer?"
    SHOW_BRAIN_TEXT    = False   # Act-3 "Your brain never measures size..."
    GHOST_ARC_MATCH    = True   # Act-5 the tree's arc returns and locks on
                                # (False = a fresh arc grows in place;
                                #  trusts framing alone to carry the rhyme)
    SHOW_TRICK_TEXT    = True   # Act-5 "Same angle. Same trick."
    BRAIN_RETURNS      = True   # Act-5 function machine reprise (CLOSE/BIG)

    # ── Scene 3's locked optical geometry, verbatim ───────────────────────
    X_IN, L1X, A1 = -7.7, -3.3, 1.5
    F1, F2        = 3.7, 0.95
    FX  = L1X + F1                 # focal point  (= 0.4)
    L2X = FX + F2                  # eyepiece     (= 1.35)
    K   = F2 / F1                  # exit compression (≈ 0.26)
    PUPIL_X, PUPIL_R, X_END = 3.95, 0.42, 4.45
    HIT_YS   = list(np.linspace(-1.41, 1.41, 11))
    WASTE_YS = [-3.5, -2.9, -2.35, -1.85, 1.85, 2.35, 2.9, 3.5]

    # Scene 3 closed with the machine scaled 0.96 about (0.25, 0) — reopen
    # in EXACTLY that state (magic-move continuity, not a rebuild-by-eye).
    S, PIVOT = 0.96, np.array([0.25, 0.0, 0.0])

    # ── the tree shot ─────────────────────────────────────────────────────
    #  The tree stays put on the left; the EYE is the moving observer that
    #  walks in from the far right.  Start: eye ~D_INIT out → a razor-thin
    #  angle spanning the frame.  End: eye at D_FINAL → the full THETA.
    H_TREE   = 2.0                 # tree height (world units, never changes)
    TREE_X   = -1.0                # the tree's fixed x — it never moves
    D_INIT   = 28.0                # opening distance  → θ ≈ 4.1°
    EYE_X    = 6.0                 # (legacy alias; the eye's END sits here-ish)

    # ── the floating image ────────────────────────────────────────────────
    MOON_HALF = 0.22               # image half-height at the crosshair

    def construct(self):
        self.camera.frame.save_state()
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()
        self.wait(0.4)
        self.add(self.frame_marks)
        self.play(self.frame_marks.animate.set_opacity(0.5), run_time=0.8)

        self._derive_geometry()     # every angle in this scene comes from here
        self._build_machine()       # Scene 3's closing frame, reassembled

        self.act1_the_question()
        self.act2_narrow_v_wide_v()
        self.act3_the_brains_blind_spot()
        self.act4_same_lenses_new_job()
        self.act5_the_angle_trick()
        self.act6_two_problems_two_wins()

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
    #  SHARED GEOMETRY — the whole scene reads from one set of numbers
    # ═══════════════════════════════════════════════════════════════════
    def _w(self, x, y=0.0):
        """Map Scene 3's blueprint coords into its closing-frame state
        (scaled S about PIVOT)."""
        p = np.array([x, y, 0.0])
        return self.PIVOT + (p - self.PIVOT) * self.S

    def _derive_geometry(self):
        self.IMG_C   = self._w(self.FX)              # floating image centre
        self.L2W     = self._w(self.L2X)             # eyepiece plane
        self.PUP_C   = self._w(self.PUPIL_X)         # the eye's pupil
        self.F2W     = self.L2W[0] - self.IMG_C[0]   # eyepiece focal length
        gap          = self.PUP_C[0] - self.L2W[0]

        # exit rays from the image tip leave the eyepiece with slope h/f₂;
        # the pair that meets the pupil centre crossed the glass at ±Y_L
        self.Y_L   = self.MOON_HALF * gap / self.F2W
        self.THETA = 2 * math.atan(self.MOON_HALF / self.F2W)  # ≈ 27°

        # the tree's final distance is DERIVED so its angle equals THETA —
        # the Act-2 / Act-5 rhyme is exact, guaranteed by construction
        self.D_FINAL = (self.H_TREE / 2) / math.tan(self.THETA / 2)

        # (sanity: the bent rays must stay on the glass)
        assert self.Y_L <= (1.35 / 2) * self.S + 1e-6, "rays overshoot lens"

    # ═══════════════════════════════════════════════════════════════════
    #  THE MACHINE — Scene 3's closing diagram, frozen light and all
    # ═══════════════════════════════════════════════════════════════════
    def _build_machine(self):
        """Static polylines instead of Scene 3's live frontier — the beam
        already finished travelling last scene. One `beam_dim` tracker
        stands in for its beam_dim, so the light can be breathed down and
        back up without touching per-ray opacities."""
        self.beam_dim = ValueTracker(0.0)

        def bind_dim(m, so, fo=0.0):
            m._so, m._fo = so, fo
            m.add_updater(lambda mm: mm
                          .set_stroke(opacity=mm._so * self.beam_dim.get_value())
                          .set_fill(opacity=mm._fo * self.beam_dim.get_value()))
            return m

        beam = VGroup()
        for y0 in self.HIT_YS:                      # the caught rays
            ray = VMobject(stroke_color=STARLIGHT, stroke_width=1.9)
            ray.set_points_as_corners([
                [self.X_IN, y0, 0], [self.L1X, y0, 0],
                [self.L2X, -y0 * self.K, 0], [self.X_END, -y0 * self.K, 0]])
            beam.add(bind_dim(ray, 0.85))
        for y0 in self.WASTE_YS:                    # the uncaught majority
            wa = Line([self.X_IN, y0, 0], [self.L1X, y0, 0],
                      stroke_color=STARLIGHT, stroke_width=1.5)
            wb = Line([self.L1X, y0, 0], [7.9, y0, 0],
                      stroke_color=DUST, stroke_width=1.3)
            beam.add(bind_dim(wa, 0.42), bind_dim(wb, 0.15))
        y0 = float(max(self.HIT_YS))                # the soft funnel body
        h2 = y0 * self.K
        for pts, fo in (
            ([[self.L1X, y0, 0], [self.FX, 0, 0], [self.L1X, -y0, 0]], 0.05),
            ([[self.FX, 0, 0], [self.L2X, h2, 0], [self.L2X, -h2, 0]], 0.05),
            ([[self.L2X, h2, 0], [self.X_END, h2, 0],
              [self.X_END, -h2, 0], [self.L2X, -h2, 0]], 0.07)):
            beam.add(bind_dim(Polygon(*pts, stroke_width=0,
                                      fill_color=STARLIGHT), 0.0, fo))
        beam.set_z_index(2)
        self.m_beam = beam

        self.m_lens1 = biconvex(h=2 * self.A1 + 0.1, bulge=0.82, color=CYAN,
                                width=2.6, fill_op=0.10)
        self.m_lens1.move_to([self.L1X, 0, 0]).set_z_index(5)
        self.m_lens2 = biconvex(h=1.35, bulge=1.5, color=CYAN, width=2.4,
                                fill_op=0.14)
        self.m_lens2.move_to([self.L2X, 0, 0]).set_z_index(5)

        self.m_cross = focal_crosshair([self.FX, 0]).set_z_index(7)
        self.m_crosslbl = mono("FOCAL POINT", AMBER, 18)
        self.m_crosslbl.next_to(self.m_cross, DOWN, buff=0.75)

        ball = Circle(radius=0.95, stroke_color=STARLIGHT, stroke_width=1.6,
                      stroke_opacity=0.45, fill_color=PANEL, fill_opacity=0.4)
        ball.move_to([self.PUPIL_X + 0.72, 0, 0]).set_z_index(6)
        pupil = make_aperture(self.PUPIL_R, width=2.6)
        pupil.move_to([self.PUPIL_X, 0, 0]).set_z_index(7)
        self.m_eye = sectioned_eye(self.PUPIL_X, self.PUPIL_R)

        base_y = -2.35

        def label_with_leader(text, x, top_y):
            lbl = mono(text, DUST, 18).move_to([x, base_y, 0])
            leader = DashedLine([x, base_y + 0.28, 0], [x, top_y, 0],
                                dash_length=0.08, dashed_ratio=0.5,
                                stroke_color=DUST, stroke_width=1.0,
                                stroke_opacity=0.3)
            return VGroup(leader, lbl)

        self.m_labels = VGroup(
            label_with_leader("OBJECTIVE · THE FUNNEL", self.L1X,
                              -self.A1 - 0.25),
            label_with_leader("EYEPIECE · THE CATCH", self.L2X, -0.85),
            label_with_leader("EYE", self.PUPIL_X + 0.4, -1.15))

        self.m_static = VGroup(self.m_lens1, self.m_lens2, self.m_cross,
                               self.m_crosslbl, self.m_eye, self.m_labels)

        # settle everything into Scene 3's exact closing state
        VGroup(self.m_beam, self.m_static).scale(self.S,
                                                 about_point=self.PIVOT)

    # ═══════════════════════════════════════════════════════════════════
    #  THE WEDGE — one honest builder used by the tree AND the telescope
    # ═══════════════════════════════════════════════════════════════════
    def _angle_arc(self, apex, theta, radius=0.85, width=2.6, opacity=1.0):
        """The angle's identity mark: a C_ANGLE arc opening leftward.
        Identical construction in Acts 2 and 5 — the visual rhyme is the
        same function called twice."""
        return Arc(radius=radius, start_angle=PI - theta / 2, angle=theta,
                   arc_center=apex, stroke_color=C_ANGLE, stroke_width=width,
                   stroke_opacity=opacity)

    # ═══════════════════════════════════════════════════════ ACT 1 ═══════
    def act1_the_question(self):
        """Scene 3's machine magic-moves back on: the frozen geometry fades
        up while its light re-illuminates through the same dimmer it went
        out on. One spare question. Keynote dissolve to black."""
        self.add(self.m_beam)
        self.play(FadeIn(self.m_static),
                  self.beam_dim.animate.set_value(1.0),
                  run_time=2.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.2)

        if self.SHOW_QUESTION_TEXT:
            q = serif("So... why does it look closer?", STARLIGHT, 34)
            q.to_edge(DOWN, buff=0.85)
            self.play(Write(q), run_time=1.2)
            self.wait(1.8)      # the question the last two scenes dodged
        else:
            q = VGroup()
            self.wait(1.6)

        # (>>> POST: no sting — the dissolve itself is the transition.)
        self.play(FadeOut(self.m_static), FadeOut(q),
                  self.beam_dim.animate.set_value(0.0),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)
        self.remove(self.m_beam)
        self.wait(0.3)

    # ═══════════════════════════════════════════════════════ ACT 2 ═══════
    def act2_narrow_v_wide_v(self):
        """The tree stays fixed on the left; the EYE is the moving observer.
        It starts far to the right — a razor-thin wedge spanning the whole
        frame — then walks in toward the tree while the camera pushes in.
        The angle 2·arctan(h / (eye_x − tree_x)) opens on its own as the gap
        closes; nothing about the tree changes."""
        tree_x     = self.TREE_X
        eye_start_x = tree_x + self.D_INIT           # far right, tiny angle
        eye_end_x   = tree_x + self.D_FINAL          # close in, full THETA

        ex  = ValueTracker(eye_start_x)   # the eye's live x — the only mover
        wop = ValueTracker(0.0)           # wedge entrance dimmer

        # start wide: tree pinned to the left edge, eye out at the right edge
        start_w = self.D_INIT + 4.0
        start_cx = (tree_x + eye_start_x) / 2
        self.camera.frame.set(width=start_w).move_to([start_cx, 0.15, 0])

        horizon = Line([tree_x - 3, -1, 0], [eye_end_x + 2.4, -1, 0],
                       stroke_color=C_GROUND, stroke_width=1.4,
                       stroke_opacity=0.35)

        # line-art pine — spans exactly y = -1 … +1 (H_TREE), pinned at tree_x
        trunk = Line([0, -1, 0], [0, -0.45, 0],
                     stroke_color=STARLIGHT, stroke_width=3.0)
        tiers = VGroup(*[
            Polygon([-w, b, 0], [w, b, 0], [0, t, 0],
                    stroke_color=STARLIGHT, stroke_width=2.0, fill_opacity=0)
            for w, b, t in ((0.55, -0.5, 0.15), (0.42, -0.05, 0.55),
                            (0.30, 0.35, 1.00))])
        tree = VGroup(trunk, tiers).move_to([tree_x, 0, 0])   # static, forever

        # the tree's true tip and trunk-foot — fixed anchors for the rays
        tip  = np.array([tree_x, tree.get_top()[1], 0])
        foot = np.array([tree_x, tree.get_bottom()[1], 0])

        # the sanctioned sectioned eye, built at the far start position; an
        # updater (attached AFTER its fade-in) slides it so its pupil always
        # sits on ex (the apex)
        eye = sectioned_eye(eye_start_x, pupil_r=0.13).set_z_index(5)

        def track_eye(m):
            m.shift(RIGHT * (ex.get_value() - m.pupil.get_center()[0]))

        def apex_pt():
            return np.array([ex.get_value(), 0.0, 0.0])

        def theta_now():
            # angle subtended at the eye by the tree's true top and bottom
            dx = ex.get_value() - tree_x
            return 2 * math.atan((self.H_TREE / 2) / dx)

        line_top = always_redraw(lambda: Line(
            tip, apex_pt(), stroke_color=STARLIGHT,
            stroke_width=2.0, stroke_opacity=0.9 * wop.get_value()))
        line_bot = always_redraw(lambda: Line(
            foot, apex_pt(), stroke_color=STARLIGHT,
            stroke_width=2.0, stroke_opacity=0.9 * wop.get_value()))
        # the arc opens AT the eye, pointing back toward the tree (leftward)
        arc = always_redraw(lambda: self._angle_arc(
            apex_pt(), theta_now(), opacity=wop.get_value()))

        self.play(FadeIn(horizon),
                  LaggedStart(Create(trunk),
                              *[Create(t) for t in tiers],
                              lag_ratio=0.15, run_time=1.2),
                  rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(eye, shift=LEFT * 0.2), run_time=0.7)
        eye.add_updater(track_eye)       # now lock the pupil onto ex
        self.add(line_top, line_bot, arc)
        self.play(wop.animate.set_value(1.0), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.2)          # hold the narrow wedge — a sliver of sky

        # THE walk-in — the eye travels toward the tree, camera pushing in
        # with it.  One unbroken move; the angle opens as the gap closes.
        # (>>> POST: soft whoosh riding this move, cresting as it lands.)
        end_cx = (tree_x + eye_end_x) / 2
        self.play(ex.animate.set_value(eye_end_x),
                  self.camera.frame.animate.set(width=10.0)
                      .move_to([end_cx, 0.1, 0]),
                  run_time=4.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.3)          # same tree. Only the angle changed.

        # freeze the live wedge into statics at their EXACT current values —
        # identical geometry, so nothing moves: no snap on the handoff
        apex = apex_pt()
        eye.clear_updaters()          # the eye is home; stop tracking ex
        w_top = Line(tip, apex, stroke_color=STARLIGHT,
                     stroke_width=2.0, stroke_opacity=0.9)
        w_bot = Line(foot, apex, stroke_color=STARLIGHT,
                     stroke_width=2.0, stroke_opacity=0.9)
        w_arc = self._angle_arc(apex, theta_now())
        self.remove(line_top, line_bot, arc)
        self.add(w_top, w_bot, w_arc)

        self.tree_arc = w_arc.copy()        # <<< Act 5 brings this back
        self._a2 = dict(apex=apex, wedge=VGroup(w_top, w_bot, w_arc),
                        tree=tree, horizon=horizon, eye=eye)

    # ═══════════════════════════════════════════════════════ ACT 3 ═══════
    def act3_the_brains_blind_spot(self):
        """Strip the world away; the eye itself collapses to a bare point.
        What is left is the scene's whole subject: an angle arriving at a
        point. Feed it to a function machine — one input, two guesses."""
        a = self._a2
        apex_dot = Dot(a["apex"], radius=0.055, color=STARLIGHT)
        self.play(FadeOut(a["tree"]), FadeOut(a["horizon"]),
                  ReplacementTransform(a["eye"], apex_dot),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        wedge = VGroup(a["wedge"], apex_dot)
        target_apex = np.array([-0.45, 0.35, 0.0])
        tgt = wedge.copy()
        tgt.scale(0.55, about_point=a["apex"])
        tgt.shift(target_apex - a["apex"])
        self.play(Transform(wedge, tgt),
                  self.camera.frame.animate.set(width=12.0)
                      .move_to([0.6, 0.2, 0]),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)

        brain = self._brain_icon().move_to([0.43 + 0.85, 0.35, 0])
        brain.shift(LEFT * 0.85)            # left edge docks at the apex
        outline, gyri = brain[0], brain[1:]
        self.play(Create(outline), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(LaggedStart(*[Create(g) for g in gyri],
                              lag_ratio=0.2, run_time=0.8))

        # the signal: one angle travels in — that is ALL that travels in
        pulse = Dot([-2.6, 0.35, 0], radius=0.05, color=C_ANGLE)
        path = Line([-2.6, 0.35, 0], brain.get_center())
        self.play(MoveAlongPath(pulse, path), run_time=0.9,
                  rate_func=rate_functions.ease_in_sine)
        self.play(FadeOut(pulse, scale=0.3),
                  Flash(brain.get_center(), color=C_ANGLE, line_length=0.1,
                        num_lines=10, flash_radius=0.4),
                  run_time=0.45)

        # two guesses grow out the other side
        anchor = brain.get_right() + LEFT * 0.05
        l1 = Line(anchor, [2.25, 0.85, 0], stroke_color=DUST,
                  stroke_width=1.4, stroke_opacity=0.6)
        l2 = Line(anchor, [2.25, -0.15, 0], stroke_color=DUST,
                  stroke_width=1.4, stroke_opacity=0.6)
        lab1 = mono("SIZE?", STARLIGHT, 20).next_to(l1.get_end(), RIGHT, 0.15)
        lab2 = mono("DISTANCE?", STARLIGHT, 20).next_to(l2.get_end(),
                                                        RIGHT, 0.15)
        self.play(LaggedStart(Create(l1), FadeIn(lab1, shift=RIGHT * 0.1),
                              Create(l2), FadeIn(lab2, shift=RIGHT * 0.1),
                              lag_ratio=0.18, run_time=1.4),
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.8)

        # (>>> POST: hold this in near-silence — nothing competes here.)
        txt = VGroup()
        if self.SHOW_BRAIN_TEXT:
            txt = serif("Your brain never measures size. Only angle.",
                        STARLIGHT, 30)
            txt.move_to([0.6, -2.35, 0])
            self.play(Write(txt), run_time=1.3)
        self.wait(2.2)

        self._brain_unit = VGroup(brain, l1, l2, lab1, lab2)
        self.play(FadeOut(wedge), FadeOut(self._brain_unit), FadeOut(txt),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)

    # ═══════════════════════════════════════════════════════ ACT 4 ═══════
    def act4_same_lenses_new_job(self):

        self.add(self.m_beam)
        self.play(Restore(self.camera.frame),
                  FadeIn(self.m_static),
                  self.beam_dim.animate.set_value(0.85),
                  run_time=1.8, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)

        # push in — the diagram dims to context, the crosshair stays lit
        self.play(self.camera.frame.animate.set(width=6.2)
                      .move_to([0.85, 0, 0]),
                  self.beam_dim.animate.set_value(0.35),
                  FadeOut(self.m_labels), FadeOut(self.m_crosslbl),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)

        # what's at the crosshair: first the series' blur...
        blob = soft_blob(0.34, seed=7).move_to(self.IMG_C).set_z_index(8)
        self.play(FadeIn(blob, scale=0.5), run_time=0.6)
        self.wait(0.4)

        # ...which racks INTO focus for once. (>>> POST: soft materialize.)
        moon = safe_image("moon.png", 2 * self.MOON_HALF, "MOON")
        moon.move_to(self.IMG_C)
        glow = Circle(radius=self.MOON_HALF * 1.7, stroke_width=0,
                      fill_color=STARLIGHT, fill_opacity=0.0)
        glow.move_to(self.IMG_C).set_z_index(7)
        corners = VGroup()
        for o in (UL, UR, DL, DR):
            c = corner_L(o, size=0.09, color=AMBER, width=1.6, opacity=0.85)
            c.move_to(self.IMG_C + o * (self.MOON_HALF + 0.09), aligned_edge=o)
            corners.add(c)
        holo = Group(glow, moon, corners).set_z_index(8)
        glow.t = 0.0

        def breathe(m, dt):     # the image is light — let it breathe
            m.t += dt
            m.set_fill(opacity=0.05 + 0.025 * math.sin(1.6 * m.t))
        self.play(FadeOut(blob, scale=0.55),
                  FadeIn(holo, scale=1.15),
                  self.m_cross.animate.set_opacity(0.25),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_sine)
        glow.add_updater(breathe)

        real_lbl = mono("A REAL IMAGE", AMBER, 12)
        real_lbl.next_to(corners, DOWN, buff=0.28)
        self.play(FadeIn(real_lbl, shift=UP * 0.06), run_time=0.6)
        self.wait(1.8)      # that's what was sitting there the whole time

        self._holo, self._real_lbl = holo, real_lbl

    # ═══════════════════════════════════════════════════════ ACT 5 ═══════
    def act5_the_angle_trick(self):

        self.play(self.camera.frame.animate.set(width=6.6)
                      .move_to([2.1, -0.12, 0]),
                  self.beam_dim.animate.set_value(0.18),
                  FadeOut(self._real_lbl),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)

        top = self.IMG_C + UP * self.MOON_HALF
        bot = self.IMG_C + DOWN * self.MOON_HALF
        bend_u = np.array([self.L2W[0],  self.Y_L, 0])
        bend_d = np.array([self.L2W[0], -self.Y_L, 0])
        ray_u = VMobject(stroke_color=STARLIGHT, stroke_width=2.2,
                         stroke_opacity=0.95)
        ray_u.set_points_as_corners([top, bend_u, self.PUP_C])
        ray_d = VMobject(stroke_color=STARLIGHT, stroke_width=2.2,
                         stroke_opacity=0.95)
        ray_d.set_points_as_corners([bot, bend_d, self.PUP_C])
        VGroup(ray_u, ray_d).set_z_index(9)
        self.play(LaggedStart(Create(ray_u), Create(ray_d),
                              lag_ratio=0.15, run_time=1.3),
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)

        # the angle returns. (>>> POST: THE hero beat — clean realization
        # sound on the lock, fullest swell of the scene right after.)
        target = self._angle_arc(self.PUP_C, self.THETA, radius=0.5,
                                 width=2.8).set_z_index(10)
        if self.GHOST_ARC_MATCH:
            ghost = self.tree_arc.set_stroke(opacity=0.0)
            self.add(ghost)
            self.play(ghost.animate.set_stroke(opacity=0.55), run_time=0.5)
            self.play(Transform(ghost, target), run_time=1.4,
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(Flash(self.PUP_C, color=C_ANGLE, line_length=0.09,
                            num_lines=12, flash_radius=0.55),
                      ghost.animate.set_stroke(opacity=1.0),
                      run_time=0.5)
            self._exit_arc = ghost
        else:
            self.play(GrowFromCenter(target), run_time=0.7,
                      rate_func=rate_functions.ease_out_cubic)
            self._exit_arc = target
        self.wait(1.4)      # let the rhyme land wordlessly first

        trick = VGroup()
        if self.SHOW_TRICK_TEXT:
            trick = serif("Same angle. Same trick.", STARLIGHT, 20)
            trick.move_to([2.1, 1.3, 0])
            self.play(Write(trick), run_time=1.0)

        if self.BRAIN_RETURNS:      # the function machine, fed for real now
            brain2 = self._brain_icon().scale(0.5).move_to([1.15, -1.2, 0])
            anchor = brain2.get_right() + LEFT * 0.03
            b1 = Line(anchor, [2.05, -0.95, 0], stroke_color=DUST,
                      stroke_width=1.2, stroke_opacity=0.6)
            b2 = Line(anchor, [2.05, -1.45, 0], stroke_color=DUST,
                      stroke_width=1.2, stroke_opacity=0.6)
            g1 = mono("SIZE?", STARLIGHT, 10).next_to(b1.get_end(),
                                                      RIGHT, 0.1)
            g2 = mono("DISTANCE?", STARLIGHT, 10).next_to(b2.get_end(),
                                                          RIGHT, 0.1)
            self.play(FadeIn(VGroup(brain2, b1, b2, g1, g2),
                             shift=UP * 0.1),
                      run_time=0.8, rate_func=rate_functions.ease_out_cubic)
            self.wait(0.7)
            v1 = mono("CLOSE.", C_ANGLE, 11).move_to(g1).align_to(g1, LEFT)
            v2 = mono("BIG.", C_ANGLE, 11).move_to(g2).align_to(g2, LEFT)
            self.play(ReplacementTransform(g1, v1),
                      ReplacementTransform(g2, v2),
                      run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
            self._brain2 = VGroup(brain2, b1, b2, v1, v2)
        else:
            self._brain2 = VGroup()

        self.wait(2.6)      # ── the fullest hold in the scene ──
        self._a5_wedge = VGroup(ray_u, ray_d)
        self._trick = trick

    # ═══════════════════════════════════════════════════════ ACT 6 ═══════
    def act6_two_problems_two_wins(self):
        """Quiet close: pull back to the full machine — image, wide angle,
        both lenses — and annotate its two jobs above the frame. Names
        below (Scene 3's labels), jobs above (this scene's verdict)."""
        self.play(self.camera.frame.animate.set(width=15.0)
                      .move_to([0.3, 0, 0]),
                  self.beam_dim.animate.set_value(0.75),
                  FadeIn(self.m_labels),
                  FadeOut(self._brain2), FadeOut(self._trick),
                  self.m_cross.animate.set_opacity(0.5),
                  run_time=1.9, rate_func=rate_functions.ease_in_out_sine)

        def job_tag(text, x, down_to):
            lbl = mono(text, AMBER, 15).move_to([x, 2.45, 0])
            leader = DashedLine([x, 2.2, 0], [x, down_to, 0],
                                dash_length=0.08, dashed_ratio=0.5,
                                stroke_color=AMBER, stroke_width=1.0,
                                stroke_opacity=0.3)
            return VGroup(leader, lbl)

        j1 = job_tag("JOB 1 · GATHER THE LIGHT", self._w(self.L1X)[0], 1.62)
        j2 = job_tag("JOB 2 · TRICK THE ANGLE", 2.6, 0.75)
        self.play(LaggedStart(FadeIn(j1, shift=DOWN * 0.08),
                              FadeIn(j2, shift=DOWN * 0.08),
                              lag_ratio=0.25, run_time=1.3),
                  rate_func=rate_functions.ease_out_cubic)


        self.wait(2.0)      # (>>> POST: minimal — let it breathe into S5.)
        for g in self._holo:
            g.clear_updaters()
        self.play(FadeOut(self.m_static), FadeOut(self._holo),
                  FadeOut(self._a5_wedge), FadeOut(self._exit_arc),
                  FadeOut(j1), FadeOut(j2),
                  FadeOut(self.frame_marks),
                  self.beam_dim.animate.set_value(0.0),
                  run_time=2.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

    # ═══════════════════════════════════════════════════════════════════
    #  THE BRAIN — deliberately a line-drawing, not an organ: a node that
    #  receives one number. Reusable grammar for any later angle illusion.
    # ═══════════════════════════════════════════════════════════════════
    def _brain_icon(self):
        pts = [(-0.95, 0.00), (-0.80, 0.40), (-0.40, 0.66), (0.10, 0.72),
               (0.55, 0.60), (0.88, 0.32), (0.95, -0.02), (0.78, -0.32),
               (0.45, -0.50), (0.15, -0.42), (-0.15, -0.52), (-0.55, -0.46),
               (-0.85, -0.28), (-0.95, 0.00)]
        outline = VMobject(stroke_color=STARLIGHT, stroke_width=2.2,
                           fill_color=PANEL, fill_opacity=0.55)
        outline.set_points_smoothly([np.array([x, y, 0]) for x, y in pts])
        gyri = VGroup(
            ArcBetweenPoints([-0.55, 0.28, 0], [-0.08, 0.44, 0], angle=-1.1,
                             stroke_color=DUST, stroke_width=1.6),
            ArcBetweenPoints([-0.02, 0.08, 0], [0.46, 0.28, 0], angle=1.0,
                             stroke_color=DUST, stroke_width=1.6),
            ArcBetweenPoints([-0.38, -0.16, 0], [0.14, -0.20, 0], angle=-1.1,
                             stroke_color=DUST, stroke_width=1.6))
        icon = VGroup(outline, *gyri)
        icon.set(width=1.7)
        return icon