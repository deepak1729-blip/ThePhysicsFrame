from manim import *
import numpy as np
import math

# ─────────────────────────────────────────────────────────────────────────
#  OBSERVATORY PALETTE  (verbatim from the series design system)
# ─────────────────────────────────────────────────────────────────────────
VOID      = "#0A0C10"   # base background
PANEL     = "#11151C"   # lifted surfaces
STARLIGHT = "#F7F6F1"   # primary text · the light itself
DUST      = "#C7C1B3"   # secondary · metadata · and, here, literal dust
AMBER     = "#FFA540"   # primary accent · focus  (amber follows the eye)
CYAN      = "#4DB4E0"   # secondary · sparing  (series pigment for LENGTH / r)

# quantity pigments — each keeps its colour across the whole series
C_LEN     = "#5B8FB0"   # LENGTH / r  (== CYAN) — every radius in this scene
C_GROUND  = "#7F8A99"   # ground / reference axis

SERIF = "Spectral"      # ideas; italic is the channel's voice & every equation
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG     = np.random.default_rng(2)      # deterministic -> stable render cache
SKY_RNG = np.random.default_rng(1729)   # Scene 1's seed: reproduces its EXACT
                                        # baseline sky for the closing echo


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


def staircase(t, n, ramp=0.22):
    """n equal steps over t in [0,1], each with a short soft ramp — the
    engine of Act 6's 'eight big pours == thirty-two small pours'."""
    s = float(np.clip(t, 0.0, 1.0)) * n
    k = math.floor(s)
    f = min((s - k) / ramp, 1.0)
    return min((k + smoothstep(f)) / n, 1.0)


def tile_frame(w=3.2, h=2.35):
    """The series' answer-tile grammar (Scene 1 of the telescope video)."""
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


def mini_dome(scale=1.0):
    """Scene 1 Act 5's whiteout, shrunk to a badge — the debt this scene
    exists to pay down."""
    dome = AnnularSector(inner_radius=0.0, outer_radius=0.52 * scale,
                         angle=PI, start_angle=0, fill_color=STARLIGHT,
                         fill_opacity=0.85, stroke_width=0)
    ground = Line(LEFT * 0.72 * scale, RIGHT * 0.72 * scale,
                  stroke_color=C_GROUND, stroke_width=1.4,
                  stroke_opacity=0.6)
    silh = Dot(ORIGIN, radius=0.035 * scale, fill_color=VOID,
               fill_opacity=1.0)
    return VGroup(dome, ground, silh)


def dust_cloud(center, r, n=42, seed_jitter=1.0):
    """A soft patch of literal dust — DUST-coloured, of course — with per-mote
    epicycle data attached so the whole cloud can drift alive."""
    cloud = VGroup()
    bases, wobble = [], []
    for _ in range(n):
        p = center + np.array([RNG.normal(0, r * 0.42),
                               RNG.normal(0, r * 0.34), 0.0]) * seed_jitter
        d = Dot(p, radius=float(RNG.uniform(0.018, 0.045)),
                fill_color=DUST, fill_opacity=float(RNG.uniform(0.30, 0.70)))
        cloud.add(d)
        bases.append(p)
        wobble.append((float(RNG.uniform(0.25, 0.75)),      # rate
                       float(RNG.uniform(0, TAU)),          # phase
                       float(RNG.uniform(0.02, 0.055))))    # amplitude
    cloud.bases, cloud.wobble = bases, wobble
    cloud.t_acc = 0.0
    cloud.warmth = ValueTracker(0.0)    # 0 = dust … 1 = glowing source
    cloud.centre = center

    def drift(grp, dt):
        grp.t_acc += dt
        w = grp.warmth.get_value()
        for i, d in enumerate(grp):
            rate, ph, amp = grp.wobble[i]
            off = np.array([math.cos(rate * grp.t_acc + ph),
                            math.sin(0.8 * rate * grp.t_acc + ph), 0.0]) * amp
            d.move_to(grp.bases[i] + off)
            if w > 0:
                col = interpolate_color(ManimColor(DUST),
                                        ManimColor(STARLIGHT), w)
                d.set_fill(color=col)
    cloud.add_updater(drift)
    return cloud


# ═══════════════════════════════════════════════════════════════════════════
class Scene2_TwoFalseAnswers(MovingCameraScene):
    """SCENE 2 — two tempting explanations are allowed to feel genuinely
    right before the picture itself takes them apart: dust first (it must
    re-radiate), distance second (the shell gives back exactly what the
    inverse square takes).  Ends on a cliffhanger, not a resolution —
    the real answer belongs to Scene 3."""

    # ── director toggles (each is a one-line flip) ────────────────────────
    USE_NEBULA_IMAGE = True    # A2: real dark-nebula photograph beat
    SPHERE_HINT      = True    # A5: faint orbit-ellipse inside each shell
    CLOSING_QUESTION = True    # A7: closing line (False = whiteout + silence)
    LABEL_YOU        = True    # A5: the observer keeps Scene 1's tiny tag

    # ── locked geometry (every act reads from these) ──────────────────────
    DOME_CAM   = np.array([0.0, 1.60, 0.0])   # Scene 1's dome framing, reused
    DOME_R_IN  = 0.55
    DOME_R_OUT = 5.20
    DOME_BANDS = 5
    DOME_COLS  = 28
    RAY_A      = 64.0                          # A2's demo sightline (degrees)
    CLOUD_D    = 2.70                          # demo cloud centre, along ray
    CLOUD_R    = 0.72
    STAR_D     = 4.60                          # the star the ray never reaches
    CLOUDS_2   = [(118.0, 3.10, 0.62),         # (angle°, radius, size) extras
                  (150.0, 2.35, 0.55)]
    FAN_STAR   = np.array([-4.90, 0.15, 0.0])  # A4 inverse-square star
    FAN_N      = 28                            # equally spaced rays (honest)
    CARD_H     = 1.50
    CARD_D1    = 3.20                          # near distance …
    CARD_D2    = 6.40                          # … and exactly double
    SH_R1      = 1.30                          # A5 Shell One radius
    SH_N1      = 8                             # countable, on purpose
    CMP_L      = np.array([-3.50, 0.95, 0.0])  # A6 comparison layout
    CMP_R      = np.array([ 3.50, 0.95, 0.0])
    CMP_R1     = 1.10
    CMP_R2     = 2.20
    BAR_H      = 1.90
    BAR_Y      = -2.55
    STACK_R0   = 1.05                          # A7 display radii (compressed)
    STACK_DR   = 0.62
    N_STACK    = 7                             # shells shown before the flood
    TOT_X      = 7.35                          # running-total bar, right edge
    TOT_Y0     = -3.20
    TOT_INC    = 1.20                          # same fixed amount, every shell

    # Scene 1's baseline-sky constants, verbatim, for the exact reproduction
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

        self.act1_two_doors()
        self.act2_answer_one_somethings_in_the_way()
        self.act3_dust_cant_hide_forever()
        self.act4_answer_two_distance_fades_the_light()
        self.act5_double_the_distance_quadruple_the_shell()
        self.act6_the_exact_cancellation()
        self.act7_an_infinite_stack_of_equals()

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

    # ── Scene 1's baseline sky, reproduced bit-for-bit ────────────────────
    def _sample_baseline_sky(self):
        """Identical sampling code and seed to Scene 1: SKY_RNG(1729) makes
        the SAME draws in the SAME order, so the closing sky is not 'a'
        sparse sky — it is THE sky the whole argument started from."""
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

    def _build_baseline_sky(self):
        horizon = Line([-7.3, self._SKY_HORIZON, 0],
                       [7.3, self._SKY_HORIZON, 0],
                       stroke_color=C_GROUND, stroke_width=1.6,
                       stroke_opacity=0.55)
        stars = VGroup(*[soft_dot(p, r, STARLIGHT, op)
                         for p, r, op in zip(self.sky_pts, self.sky_radii,
                                             self.sky_ops)])
        stars.t_acc = 0.0
        veil = ValueTracker(1.0)
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
        return horizon, stars

    # ── the extinction ray: Scene 1's sightline, meeting dust ─────────────
    def _extinction_ray(self, direction, star_d, cloud_d, cloud_r,
                        n_seg=26, k_ext=3.2, base_op=0.95, width=1.8):
        """A ray built from short segments whose opacity follows a
        Beer–Lambert-style decay once inside the cloud — the light does not
        slow down or stop; it simply runs out.  Revealed by a tracker so the
        tip travels at constant speed, as light must."""
        d_in = cloud_d - cloud_r
        length = star_d - 0.10
        segs = VGroup()
        mids = []
        for i in range(n_seg):
            a = 0.16 + (length - 0.16) * i / n_seg
            b = 0.16 + (length - 0.16) * (i + 1) / n_seg
            segs.add(Line(direction * a, direction * b,
                          stroke_color=STARLIGHT, stroke_width=width,
                          stroke_opacity=0.0))
            mids.append(0.5 * (a + b))

        def profile(u):
            if u <= d_in:
                return base_op
            v = base_op * math.exp(-k_ext * (u - d_in))
            return v if v > 0.02 else 0.0

        prog = ValueTracker(0.0)
        segs.prog = prog

        def reveal(grp):
            tip = 0.16 + (length - 0.16) * prog.get_value()
            for i, s in enumerate(grp):
                s.set_stroke(opacity=profile(mids[i]) if mids[i] <= tip
                             else 0.0)
        segs.add_updater(reveal)
        return segs, prog

    # ── the dome, cells and mesh (Scene 1 Act 5's grammar, reused) ────────
    def _build_dome_mesh_cells(self, fill_start=0.0):
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

        cells, meta = VGroup(), []
        for i in range(bands):
            for j in range(cols):
                cell = AnnularSector(
                    inner_radius=b_edges[i], outer_radius=b_edges[i + 1],
                    angle=c_edges[j + 1] - c_edges[j],
                    start_angle=c_edges[j],
                    fill_color=STARLIGHT, fill_opacity=fill_start,
                    stroke_width=0)
                cells.add(cell)
                meta.append((0.5 * (b_edges[i] + b_edges[i + 1]),
                             0.5 * (c_edges[j] + c_edges[j + 1])))
        return mesh, cells, meta

    # ═══════════════════════════════════════════════════════ ACT 1 ═══════
    def act1_two_doors(self):
        """Brisk and structural: the unpaid debt (Scene 1's whiteout, shrunk
        to a badge) branches into two waiting, unlabeled doors."""
        badge = mini_dome(scale=1.0).move_to([-4.95, 2.45, 0])
        marks = VGroup()
        for o in (UL, UR, DL, DR):
            c = corner_L(o, size=0.13, color=AMBER, opacity=0.5)
            c.move_to(badge.get_corner(o) + o * 0.16, aligned_edge=o)
            marks.add(c)
        tag = mono("STILL UNEXPLAINED", DUST, 10)
        tag.next_to(badge, DOWN, buff=0.28)

        self.play(FadeIn(badge, scale=0.7), FadeIn(marks),
                  run_time=1.0, rate_func=rate_functions.ease_out_cubic)
        self.play(FadeIn(tag), run_time=0.5)
        self.wait(0.8)

        tiles = VGroup(tile_frame().move_to([-3.3, -1.05, 0]),
                       tile_frame().move_to([3.3, -1.05, 0]))
        start = badge.get_bottom() + DOWN * 0.55
        paths = VGroup(
            ArcBetweenPoints(start, tiles[0].get_top() + UP * 0.18,
                             angle=-0.6, stroke_color=DUST,
                             stroke_width=1.4, stroke_opacity=0.6),
            ArcBetweenPoints(start, tiles[1].get_top() + UP * 0.18,
                             angle=-1.1, stroke_color=DUST,
                             stroke_width=1.4, stroke_opacity=0.6))
        self.play(LaggedStart(Create(paths[0]), Create(paths[1]),
                              lag_ratio=0.3),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.play(LaggedStart(FadeIn(tiles[0], shift=UP * 0.2),
                              FadeIn(tiles[1], shift=UP * 0.2),
                              lag_ratio=0.25),
                  run_time=1.1, rate_func=rate_functions.ease_out_cubic)
        self.wait(1.0)   # "okay — we have a plan"

        # open door one: the first tile comes toward us and becomes the act
        keep = VGroup(badge, marks, tag, paths, tiles[1])
        self.play(
            tiles[0].animate.scale(4.2).set_opacity(0.0),
            FadeOut(keep),
            run_time=1.2, rate_func=rate_functions.ease_in_sine,
        )
        self.remove(tiles[0], keep)

    # ═══════════════════════════════════════════════════════ ACT 2 ═══════
    def act2_answer_one_somethings_in_the_way(self):
        """Scene 1's sightline again — but now a cloud of dust sits in the
        way, and the ray simply dies inside it.  Spread that across the
        dome and the whiteout goes convincingly patchy.  Let it feel like
        an answer; Act 3 is going to charge for that comfort."""
        th = math.radians(self.RAY_A)
        d = np.array([math.cos(th), math.sin(th), 0.0])
        observer = soft_dot(ORIGIN, 0.055, AMBER, 1.0)
        star = soft_dot(d * self.STAR_D, 0.075, STARLIGHT, 0.85)
        cloud = dust_cloud(d * self.CLOUD_D, self.CLOUD_R, n=44)

        # frame the demo: observer low, the doomed sightline crossing frame
        mid = d * (self.STAR_D * 0.45)
        self.play(
            self.camera.frame.animate.move_to(mid + UP * 0.2).scale(0.68),
            FadeIn(observer, scale=0.5),
            run_time=1.4, rate_func=rate_functions.ease_in_out_sine,
        )
        self.play(FadeIn(star, scale=0.6),
                  LaggedStart(*[FadeIn(m, scale=0.4) for m in cloud],
                              lag_ratio=0.015),
                  run_time=1.2, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.6)

        ray, prog = self._extinction_ray(d, self.STAR_D, self.CLOUD_D,
                                         self.CLOUD_R)
        self.add(ray)
        # constant speed, as always — the drama is that the brightness dies
        self.play(prog.animate.set_value(1.0), run_time=2.6,
                  rate_func=linear)
        ray.clear_updaters()
        self.play(star.animate.set_opacity(0.12), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.4)   # the light simply doesn't make it.  Case closed?

        # widen to the dome: the whiteout reprised, then eaten patchy
        mesh, cells, meta = self._build_dome_mesh_cells(fill_start=0.0)
        ground = Line([-7.2, 0, 0], [7.2, 0, 0], stroke_color=C_GROUND,
                      stroke_width=1.6, stroke_opacity=0.55)
        self.play(
            self.camera.frame.animate.move_to(self.DOME_CAM)
                .set(width=config.frame_width),
            FadeOut(ray),
            Create(ground),
            run_time=1.8, rate_func=rate_functions.ease_in_out_sine,
        )
        self.add(cells)
        self.play(cells.animate.set_fill(opacity=0.55),
                  FadeIn(mesh), run_time=1.1,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

        clouds = [cloud]
        for ang, rad, size in self.CLOUDS_2:
            t2 = math.radians(ang)
            c2 = dust_cloud(np.array([math.cos(t2), math.sin(t2), 0]) * rad,
                            size, n=34)
            clouds.append(c2)
        self.play(LaggedStart(
            *[LaggedStart(*[FadeIn(m, scale=0.4) for m in c],
                          lag_ratio=0.02) for c in clouds[1:]],
            lag_ratio=0.4), run_time=1.4,
            rate_func=rate_functions.ease_out_cubic)

        # a few more sightlines die inside the new clouds
        extra_rays = VGroup()
        extra_anims = []
        for ang, rad, size in self.CLOUDS_2:
            t2 = math.radians(ang)
            d2 = np.array([math.cos(t2), math.sin(t2), 0.0])
            r2, p2 = self._extinction_ray(d2, self.DOME_R_OUT - 0.35,
                                          rad, size, width=1.4)
            self.add(r2)
            extra_rays.add(r2)
            extra_anims.append(p2.animate(run_time=1.0,
                                          rate_func=linear).set_value(1.0))
        self.play(LaggedStart(*extra_anims, lag_ratio=0.35))
        for r2 in extra_rays:
            r2.clear_updaters()

        # shadow geometry: cells behind each cloud (same direction, farther
        # out) go dark — the honest cone of what the dust actually hides
        self._blocked = []
        cloud_specs = [(math.radians(self.RAY_A), self.CLOUD_D,
                        self.CLOUD_R)] + \
                      [(math.radians(a), r, s) for a, r, s in self.CLOUDS_2]
        for k, (rm, tm) in enumerate(meta):
            for ca, cd, cr in cloud_specs:
                half = math.atan2(cr * 0.9, cd)
                if abs(tm - ca) < half and rm > cd - cr * 0.4:
                    self._blocked.append(k)
                    break
        dim_anims = [cells[k].animate.set_fill(opacity=0.08)
                     for k in self._blocked]
        # (>>> POST: the score relaxes here — this is meant to feel like
        #  the problem being genuinely, comfortably solved.)
        self.play(LaggedStart(*dim_anims, lag_ratio=0.02), run_time=1.8,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeOut(extra_rays), star.animate.set_opacity(0.05),
                  run_time=0.6)
        self.wait(1.8)   # relief.  Patchy dark is what a night sky IS.

        if self.USE_NEBULA_IMAGE:
            photo = safe_image("dark_nebula.jpg", 12.5,
                               "DARK NEBULA PHOTOGRAPH")
            photo.set_z_index(20).move_to(self.DOME_CAM)
            cap = mono("A REAL CLOUD OF DUST \u2014 SWALLOWING THE STARS "
                       "BEHIND IT", STARLIGHT, 12)
            cap.set_z_index(21).move_to(self.DOME_CAM + DOWN * 3.35)
            self.play(FadeIn(photo), run_time=0.8,
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(FadeIn(cap), run_time=0.5)
            self.wait(2.4)
            self.play(FadeOut(photo), FadeOut(cap), run_time=0.8,
                      rate_func=rate_functions.ease_in_out_sine)

        self._observer, self._star = observer, star
        self._clouds = clouds
        self._mesh, self._cells, self._ground = mesh, cells, ground

    # ═══════════════════════════════════════════════════════ ACT 3 ═══════
    def act3_dust_cant_hide_forever(self):
        """Push into one cloud and follow the energy: light streams in, a
        plain container fills, and — with nowhere else for that energy to
        go — the cloud itself starts to glow.  ONE tracker (the gauge
        level) drives the fill, the cloud's colour and the emission, so the
        causality is literal, not implied.  The 'fix' then un-fixes the
        whole dome."""
        cloud = self._clouds[0]
        cc = cloud.centre
        th = math.radians(self.RAY_A)
        d = np.array([math.cos(th), math.sin(th), 0.0])

        self.play(
            self.camera.frame.animate.move_to(cc + RIGHT * 0.55).scale(0.40),
            run_time=1.8, rate_func=rate_functions.ease_in_out_sine,
        )

        # steady incoming light: three lanes of travelling dashes, looping.
        # The star lies BEYOND the cloud (at d * STAR_D), so the light must
        # arrive on the far side and travel inward, toward the observer —
        # never from the observer's side of the cloud.
        perp = np.array([-d[1], d[0], 0.0])
        d_in = self.CLOUD_D + self.CLOUD_R      # far edge: the star-facing side
        lanes = VGroup()
        lane_data = []
        for li, off in enumerate((-0.14, 0.0, 0.14)):
            for j in range(4):
                dash = Line(ORIGIN, d * 0.20, stroke_color=STARLIGHT,
                            stroke_width=1.6, stroke_opacity=0.0)
                lanes.add(dash)
                lane_data.append((off, (j * 0.42 + li * 0.13) % 1.68))
        lanes.t_acc = 0.0
        span, feed_len, speed = 1.68, 1.30, 1.35

        def stream(grp, dt):
            grp.t_acc += dt
            for i, dash in enumerate(grp):
                off, ph = lane_data[i]
                s = (ph + speed * grp.t_acc) % span
                # s grows, a shrinks: the dash marches from the far side of
                # the cloud inward, i.e. star -> cloud -> observer
                a = d_in + feed_len - s
                op = smoothstep((s / span) * 3.0) * 0.85
                if a < d_in + 0.05:
                    op = 0.0
                dash.put_start_and_end_on(
                    d * a + perp * off, d * (a - 0.20) + perp * off)
                dash.set_stroke(opacity=op)
        lanes.add_updater(stream)
        self.add(lanes)

        # the plain container: energy in, nowhere to go
        level = ValueTracker(0.0)
        box = RoundedRectangle(width=0.42, height=1.35, corner_radius=0.05,
                               stroke_color=DUST, stroke_width=1.6,
                               stroke_opacity=0.7, fill_opacity=0.0)
        box.move_to(cc + RIGHT * 1.60 + UP * 0.05)
        fill = Rectangle(width=0.32, height=0.001, stroke_width=0,
                         fill_color=AMBER, fill_opacity=0.85)
        base_y = box.get_bottom()[1] + 0.06

        def fill_up(m):
            h = max(1.23 * level.get_value(), 0.001)
            m.stretch_to_fit_height(h)
            m.move_to([box.get_center()[0], base_y + h / 2, 0])
        fill.add_updater(fill_up)
        etag = mono("ENERGY", DUST, 10).next_to(box, UP, buff=0.14)

        self.play(FadeIn(box), FadeIn(etag), run_time=0.8,
                  rate_func=rate_functions.ease_out_cubic)
        self.add(fill)
        self.wait(0.8)   # let the stream establish itself first

        # the gauge climbs; past ~60 % the cloud can't stay dark.  Warmth is
        # SLAVED to the level — one tracker, one cause, no parallel timeline.
        # (>>> POST: a soft low hum rises in pitch WITH this fill, and
        #  resolves the instant the cloud starts to glow.)
        def warm_link(grp, dt):
            grp.warmth.set_value(
                max(0.0, (level.get_value() - 0.60) / 0.40) ** 1.4)
        cloud.add_updater(warm_link)
        self.play(level.animate.set_value(1.0), run_time=4.6,
                  rate_func=rate_functions.ease_in_out_sine)
        cloud.remove_updater(warm_link)
        self.wait(0.4)

        # a blocker no longer: it radiates on its own account
        emit = VGroup()
        for j in range(14):
            a = TAU * j / 14 + 0.13
            e = np.array([math.cos(a), math.sin(a), 0.0])
            emit.add(Line(cc + e * (self.CLOUD_R * 0.55),
                          cc + e * (self.CLOUD_R * 1.9),
                          stroke_color=STARLIGHT, stroke_width=1.3,
                          stroke_opacity=0.8))
        self.play(LaggedStart(*[Create(e) for e in emit], lag_ratio=0.04),
                  box.animate.set_stroke(color=AMBER, opacity=1.0),
                  run_time=1.0, rate_func=rate_functions.ease_out_cubic)
        self.wait(1.2)

        # pull back: every cloud is a lamp now, and the dark patches un-dim
        other_warm = [c.warmth.animate.set_value(1.0)
                      for c in self._clouds[1:]]
        self.play(
            self.camera.frame.animate.move_to(self.DOME_CAM)
                .set(width=config.frame_width),
            FadeOut(lanes), FadeOut(box), FadeOut(fill), FadeOut(etag),
            emit.animate.set_stroke(opacity=0.3),
            *other_warm,
            run_time=2.0, rate_func=rate_functions.ease_in_out_sine,
        )
        lanes.clear_updaters()
        fill.clear_updaters()

        # the exact cells Act 2 darkened come back — and then some: the
        # whole dome returns to Scene 1 Act 5's full whiteout
        refill = [self._cells[k].animate.set_fill(opacity=0.92)
                  for k in self._blocked]
        rest = [self._cells[k].animate.set_fill(opacity=0.92)
                for k in range(len(self._cells)) if k not in self._blocked]
        self.play(LaggedStart(*refill, lag_ratio=0.02), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(*rest,
                  self._mesh.animate.set_stroke(color=STARLIGHT,
                                                opacity=0.5),
                  run_time=1.2, rate_func=rate_functions.ease_in_sine)

        dome = AnnularSector(inner_radius=0.0, outer_radius=self.DOME_R_OUT,
                             angle=PI, start_angle=0, fill_color=STARLIGHT,
                             fill_opacity=1.0, stroke_width=0)
        silhouette = Dot(ORIGIN, radius=0.06, fill_color=VOID,
                         fill_opacity=1.0).set_z_index(5)
        self._ground.set_z_index(5)
        for c in self._clouds:
            c.clear_updaters()
        self.play(FadeIn(dome), FadeOut(self._mesh),
                  FadeIn(silhouette),
                  *[FadeOut(c) for c in self._clouds],
                  FadeOut(self._star),
                  run_time=0.9, rate_func=rate_functions.ease_in_sine)
        # playing children of a group re-adds them top-level; sweep them all
        self.remove(self._cells, *self._cells, self._observer,
                    emit, *emit)
        self.wait(2.8)   # the crux: the fix, collapsed back into the problem

        self.play(FadeOut(dome), FadeOut(self._ground),
                  FadeOut(silhouette),
                  Restore(self.camera.frame),
                  run_time=1.6, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)

    # ═══════════════════════════════════════════════════════ ACT 4 ═══════
    def act4_answer_two_distance_fades_the_light(self):
        """One star, one honest fan of equally spaced rays, one fixed card.
        Slide the card to double the distance — live, not before/after —
        and watch it catch fewer of the same rays, its glow dying as it
        goes.  True.  And exactly the trap Act 5 needs."""
        sp = self.FAN_STAR
        star = soft_dot(sp, 0.10, STARLIGHT, 1.0)
        # Only the forward cone can ever matter: a card cannot catch light
        # that leaves in the other direction.  Equally spaced rays across a
        # cone the NEAR card exactly fills — so "caught" starts at 100%.
        half = self.CARD_H / 2
        cone = math.atan2(half, self.CARD_D1)
        n = self.FAN_N
        # sample at cell centres -> fan is symmetric about the axis
        angles = [-cone + 2 * cone * (i + 0.5) / n for i in range(n)]
        REACH = self.CARD_D2 + 2.4              # rays outrun the far card
        rays = VGroup(*[Line(sp, sp + REACH * np.array(
                            [math.cos(a), math.sin(a), 0.0]),
                            stroke_color=STARLIGHT, stroke_width=1.2,
                            stroke_opacity=0.28) for a in angles])

        self.play(FadeIn(star, scale=0.5), run_time=0.8,
                  rate_func=rate_functions.ease_out_cubic)
        self.play(LaggedStart(*[Create(r) for r in rays], lag_ratio=0.02),
                  run_time=1.6, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.6)

        D = ValueTracker(self.CARD_D1)
        catch0 = sum(1 for a in angles
                     if abs(math.tan(a)) * self.CARD_D1 <= half)

        # ONE detector, seen edge-on.  The amber face is not a second slab
        # floating in front of the card — it is the card's own surface, and
        # it is exactly as bright as the light actually landing on it.
        plate = Rectangle(width=0.13, height=self.CARD_H,
                          stroke_color=DUST, stroke_width=1.6,
                          stroke_opacity=0.9,
                          fill_color=PANEL, fill_opacity=1.0)
        glow = Rectangle(width=0.13, height=self.CARD_H,
                         stroke_width=0, fill_color=AMBER, fill_opacity=0.0)
        card = VGroup(plate, glow)
        counter = mono("CAUGHT  %d" % catch0, AMBER, 15)
        # the card reveals itself by opacity only — never by a scaling
        # FadeIn, which would change the group's bbox and tear plate from
        # glow while the updater is positioning by bbox
        for m in (plate, glow, counter):
            m.set_opacity(0.0)

        def track(grp):
            dv = D.get_value()
            cx = sp[0] + dv
            face = cx - 0.065                 # the lit face of the card
            # position each piece ABSOLUTELY: no bbox arithmetic, so the
            # plate and its glow can never drift apart
            plate.move_to([cx, sp[1], 0])
            glow.move_to([cx, sp[1], 0])
            caught = 0
            for a, r in zip(angles, rays):
                y = math.tan(a) * dv
                if abs(y) <= half:
                    caught += 1
                    # absorbed: the ray stops dead at the card face
                    r.put_start_and_end_on(sp, [face, sp[1] + y, 0])
                    r.set_stroke(opacity=0.9, width=1.4)
                else:
                    # missed: it sails past the card's edge, and stays dim
                    end = sp + REACH * np.array([math.cos(a),
                                                 math.sin(a), 0.0])
                    r.put_start_and_end_on(sp, end)
                    r.set_stroke(opacity=0.18, width=1.0)
            # same card, fewer rays -> less light per unit of card
            glow.set_fill(opacity=0.60 * caught / max(catch0, 1))
            counter.become(mono("CAUGHT  %d" % caught, AMBER, 15)
                           .move_to([cx, sp[1] + half + 0.45, 0]))
        card.add_updater(track)

        self.add(card, counter)
        self.play(plate.animate.set_opacity(1.0),
                  counter.animate.set_opacity(1.0),
                  run_time=0.7, rate_func=rate_functions.ease_out_cubic)
        self.wait(1.3)   # the near card, catching its full share

        # the whole mechanism in one continuous move — no cut, no cheat
        self.play(D.animate.set_value(self.CARD_D2), run_time=3.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.2)
        card.clear_updaters()

        line = serif("twice as far \u2014 the same light, spread thinner",
                     STARLIGHT, 27)
        line.to_edge(DOWN, buff=0.75)
        self.play(Write(line), run_time=1.2)
        self.wait(1.6)

        self.play(FadeOut(VGroup(star, rays, card, counter, line)),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)

    # ═══════════════════════════════════════════════════════ ACT 5 ═══════
    def act5_double_the_distance_quadruple_the_shell(self):
        """Scene 1's radial field, formalized: Shell One at r, Shell Two at
        exactly 2r — and every Shell One star visibly becomes FOUR Shell Two
        stars, so 'four times as many' arrives as geometry, not assertion."""
        backdrop = VGroup()
        for _ in range(70):
            a, rr = RNG.uniform(0, TAU), RNG.uniform(0.6, 5.2)
            backdrop.add(Dot([rr * math.cos(a), rr * math.sin(a), 0],
                             radius=float(RNG.uniform(0.008, 0.018)),
                             fill_color=STARLIGHT,
                             fill_opacity=float(RNG.uniform(0.08, 0.20))))
        observer = soft_dot(ORIGIN, 0.055, AMBER, 1.0)
        grp_in = [FadeIn(observer, scale=0.5),
                  LaggedStart(*[FadeIn(b) for b in backdrop],
                              lag_ratio=0.004)]
        you = None
        if self.LABEL_YOU:
            you = mono("YOU", DUST, 11).next_to(observer, DOWN, buff=0.20)
            you.set_opacity(0.55)
            grp_in.append(FadeIn(you))
        self.play(*grp_in, run_time=1.2,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        r1 = self.SH_R1
        c1 = Circle(radius=r1, stroke_color=C_LEN, stroke_width=2.0,
                    stroke_opacity=0.85)
        hint1 = Ellipse(width=2 * r1, height=2 * r1 * 0.36,
                        stroke_color=C_LEN, stroke_width=1.0,
                        stroke_opacity=0.14).rotate(-14 * DEGREES)
        rad1 = Line(ORIGIN, r1 * np.array([math.cos(-0.62),
                                           math.sin(-0.62), 0]),
                    stroke_color=C_LEN, stroke_width=2.2)
        rlab1 = serif("r", C_LEN, 30).move_to(
            rad1.get_center() + DOWN * 0.28 + RIGHT * 0.10)
        tag1 = mono("SHELL ONE", DUST, 11).move_to(
            1.62 * np.array([math.cos(2.72), math.sin(2.72), 0]))

        base_a = math.radians(10.0)
        p_angles = [base_a + TAU * i / self.SH_N1
                    for i in range(self.SH_N1)]
        pts1 = VGroup(*[soft_dot(r1 * np.array([math.cos(a),
                                                math.sin(a), 0]),
                                 0.048, STARLIGHT, 0.95)
                        for a in p_angles])

        self.play(Create(c1),
                  *([FadeIn(hint1)] if self.SPHERE_HINT else []),
                  run_time=1.1, rate_func=rate_functions.ease_in_out_sine)
        self.play(Create(rad1), Write(rlab1), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in pts1],
                              lag_ratio=0.07),
                  FadeIn(tag1), run_time=1.1,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(1.0)   # a modest, countable shell.  Eight stars.

        # Shell Two grows out of Shell One — exactly double, seen live
        r2 = 2 * r1
        c2 = Circle(radius=r1, stroke_color=C_LEN, stroke_width=2.0,
                    stroke_opacity=0.85)
        hint2 = Ellipse(width=2 * r1, height=2 * r1 * 0.36,
                        stroke_color=C_LEN, stroke_width=1.0,
                        stroke_opacity=0.14).rotate(-14 * DEGREES)
        rad2 = Line(ORIGIN, r2 * np.array([math.cos(-0.28),
                                           math.sin(-0.28), 0]),
                    stroke_color=C_LEN, stroke_width=2.2,
                    stroke_opacity=0.0)
        rlab2 = serif("2r", C_LEN, 30).move_to(
            rad2.get_end() * 0.55 + DOWN * 0.30)
        call1 = mono("TWICE THE DISTANCE", DUST, 12).move_to([0, 3.45, 0])
        self.add(c2, *([hint2] if self.SPHERE_HINT else []))
        self.play(c2.animate.scale(2.0, about_point=ORIGIN),
                  *([hint2.animate.scale(2.0, about_point=ORIGIN)]
                    if self.SPHERE_HINT else []),
                  rad2.animate.set_stroke(opacity=1.0),
                  FadeIn(call1),
                  run_time=1.7, rate_func=rate_functions.ease_in_out_sine)
        self.play(Write(rlab2), run_time=0.6)
        call2 = mono("FOUR TIMES THE SURFACE", AMBER, 12)
        call2.next_to(call1, DOWN, buff=0.18)
        self.play(FadeIn(call2, shift=DOWN * 0.1), run_time=0.7)
        self.wait(0.6)

        # every star becomes four: cloning as choreography, density as fate
        child_off = [math.radians(o) for o in (-16.875, -5.625,
                                               5.625, 16.875)]
        pts2 = VGroup()
        clone_anims = []
        for i, pa in enumerate(p_angles):
            for off in child_off:
                ca = pa + off
                child = soft_dot(r2 * np.array([math.cos(ca),
                                                math.sin(ca), 0]),
                                 0.048, STARLIGHT, 0.95)
                pts2.add(child)
                clone_anims.append(TransformFromCopy(pts1[i], child,
                                                     path_arc=0.35))
        tag2 = mono("SHELL TWO", DUST, 11).move_to(
            2.95 * np.array([math.cos(0.42), math.sin(0.42), 0]))
        self.play(LaggedStart(*clone_anims, lag_ratio=0.03),
                  run_time=2.6, rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeIn(tag2), run_time=0.5)
        self.wait(2.0)   # crux: eight stars.  Thirty-two stars.  Same sky.

        self._sh1 = VGroup(c1, hint1, pts1) if self.SPHERE_HINT \
            else VGroup(c1, pts1)
        self._sh2 = VGroup(c2, hint2, pts2) if self.SPHERE_HINT \
            else VGroup(c2, pts2)
        self._sh_extra = VGroup(rad1, rlab1, rad2, rlab2, call1, call2,
                                tag1, tag2, backdrop)
        self._observer5, self._you5 = observer, you
        self._pts1, self._pts2 = pts1, pts2

    # ═══════════════════════════════════════════════════════ ACT 6 ═══════
    def act6_the_exact_cancellation(self):
        """Side by side: eight bright stars, thirty-two quarter-bright
        stars.  Two meters climb — one in eight coarse steps, one in
        thirty-two fine ones — and land on the same line.  8 × 4 = 32 × 1,
        performed rather than printed."""
        s1, s2 = self.CMP_R1 / self.SH_R1, self.CMP_R2 / (2 * self.SH_R1)
        move = [self._sh1.animate.scale(s1).move_to(self.CMP_L),
                self._sh2.animate.scale(s2).move_to(self.CMP_R),
                FadeOut(self._sh_extra)]
        if self._you5 is not None:
            move.append(FadeOut(self._you5))
        move.append(FadeOut(self._observer5))
        self.play(*move, run_time=1.7,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)

        lab1 = mono("8 STARS \u00b7 FULL BRIGHTNESS", DUST, 11)
        lab2 = mono("32 STARS \u00b7 1/4 BRIGHTNESS EACH", DUST, 11)
        lab1.move_to([self.CMP_L[0], -1.45, 0])
        lab2.move_to([self.CMP_R[0], -1.45, 0])
        self.play(FadeIn(lab1), run_time=0.6)
        # the inverse square collects its toll — each far star dims to 1/4
        self.play(LaggedStart(*[p.animate.set_opacity(0.24)
                                for p in self._pts2], lag_ratio=0.015),
                  FadeIn(lab2), run_time=1.5,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.9)

        bars = VGroup()
        fills = []
        for x in (self.CMP_L[0], self.CMP_R[0]):
            box = RoundedRectangle(width=0.95, height=1.50,
                                   corner_radius=0.06, stroke_color=DUST,
                                   stroke_width=1.4, stroke_opacity=0.7,
                                   fill_opacity=0.0)
            box.move_to([x, self.BAR_Y - 0.35, 0])
            fill = Rectangle(width=0.80, height=0.001, stroke_width=0,
                             fill_color=STARLIGHT, fill_opacity=0.85)
            bars.add(box)
            fills.append(fill)
        self.play(FadeIn(bars), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)

        master = ValueTracker(0.0)
        H = 1.40

        def make_fill_updater(box, n_steps):
            base_y = box.get_bottom()[1] + 0.05
            cx = box.get_center()[0]

            def upd(m):
                h = max(H * staircase(master.get_value(), n_steps), 0.001)
                m.stretch_to_fit_height(h)
                m.move_to([cx, base_y + h / 2, 0])
            return upd
        fills[0].add_updater(make_fill_updater(bars[0], 8))
        fills[1].add_updater(make_fill_updater(bars[1], 32))
        self.add(*fills)

        # the pours: 8 chunky quanta, 32 slim ones, interleaved in time
        flights = []
        top1 = bars[0].get_top() + DOWN * 0.1
        top2 = bars[1].get_top() + DOWN * 0.1
        for i, p in enumerate(self._pts1):
            q = Dot(p.get_center(), radius=0.055, fill_color=STARLIGHT,
                    fill_opacity=0.0)
            self.add(q)
            flights.append(Succession(
                q.animate(run_time=0.06).set_fill(opacity=0.95),
                q.animate(run_time=0.30,
                          rate_func=rate_functions.ease_in_sine
                          ).move_to(top1),
                q.animate(run_time=0.08).set_fill(opacity=0.0)))
        for i, p in enumerate(self._pts2):
            q = Dot(p.get_center(), radius=0.030, fill_color=STARLIGHT,
                    fill_opacity=0.0)
            self.add(q)
            flights.append(Succession(
                q.animate(run_time=0.05).set_fill(opacity=0.55),
                q.animate(run_time=0.22,
                          rate_func=rate_functions.ease_in_sine
                          ).move_to(top2),
                q.animate(run_time=0.06).set_fill(opacity=0.0)))
        self.play(
            master.animate.set_value(1.0),
            LaggedStart(*flights[:8], lag_ratio=1.18),
            LaggedStart(*flights[8:], lag_ratio=0.395),
            run_time=4.4, rate_func=linear,
        )
        for f in fills:
            f.clear_updaters()
        self.wait(0.3)

        # (>>> POST: one clean tone, exactly as the level line lands.)
        y_top = bars[0].get_bottom()[1] + 0.05 + H
        level = Line([self.CMP_L[0] - 1.15, y_top, 0],
                     [self.CMP_R[0] + 1.15, y_top, 0],
                     stroke_color=AMBER, stroke_width=1.6)
        self.play(Create(level), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(2.9)   # the most important frame in the scene.  Hold it.

        self._bars = VGroup(bars, *fills, level, lab1, lab2)

    # ═══════════════════════════════════════════════════════ ACT 7 ═══════
    def act7_an_infinite_stack_of_equals(self):
        """Every farther shell is another equal payment.  The running total
        never slows, never converges — and the whiteout comes back, earned
        by arithmetic this time.  Then Scene 1's exact sky, and the
        question this episode refuses to answer."""
        s_back1 = self.STACK_R0 / self.CMP_R1
        s_back2 = (self.STACK_R0 + self.STACK_DR) / self.CMP_R2
        self.play(
            self._sh1.animate.scale(s_back1).move_to(ORIGIN),
            self._sh2.animate.scale(s_back2).move_to(ORIGIN),
            FadeOut(self._bars),
            self.camera.frame.animate.scale(1.18),
            run_time=1.8, rate_func=rate_functions.ease_in_out_sine,
        )

        # the running total: an open-topped column on the frame's edge —
        # deliberately no ceiling to hit
        x = self.TOT_X
        rail = VGroup(
            Line([x - 0.30, self.TOT_Y0, 0], [x - 0.30, 5.6, 0],
                 stroke_color=DUST, stroke_width=1.3, stroke_opacity=0.6),
            Line([x + 0.30, self.TOT_Y0, 0], [x + 0.30, 5.6, 0],
                 stroke_color=DUST, stroke_width=1.3, stroke_opacity=0.6),
            Line([x - 0.30, self.TOT_Y0, 0], [x + 0.30, self.TOT_Y0, 0],
                 stroke_color=DUST, stroke_width=1.3, stroke_opacity=0.6))
        ttag = mono("TOTAL LIGHT", DUST, 10).move_to([x, self.TOT_Y0 - 0.35,
                                                      0])
        tot = ValueTracker(0.0)
        tfill = Rectangle(width=0.46, height=0.001, stroke_width=0,
                          fill_color=STARLIGHT, fill_opacity=0.85)

        def tot_up(m):
            h = max(self.TOT_INC * tot.get_value(), 0.001)
            m.stretch_to_fit_height(h)
            m.move_to([x, self.TOT_Y0 + h / 2, 0])
        tfill.add_updater(tot_up)
        self.play(FadeIn(rail), FadeIn(ttag), run_time=0.7)
        self.add(tfill)

        def tick_at(k):
            y = self.TOT_Y0 + self.TOT_INC * k
            t = Line([x - 0.42, y, 0], [x - 0.30, y, 0],
                     stroke_color=AMBER, stroke_width=1.6)
            num = mono(str(k), AMBER, 10).next_to(t, LEFT, buff=0.10)
            return VGroup(t, num)

        # shells one and two pay in first — the act 6 result, banked
        for k in (1, 2):
            self.play(tot.animate.set_value(k), FadeIn(tick_at(k)),
                      run_time=0.45,
                      rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        # …and then the stack: same payment, every time, faster and faster
        stack = VGroup()
        run_times = [0.95, 0.80, 0.65, 0.52, 0.45]
        for k in range(3, self.N_STACK + 1):
            rk = self.STACK_R0 + (k - 1) * self.STACK_DR
            ring = Circle(radius=rk, stroke_color=C_LEN, stroke_width=2.0,
                          stroke_opacity=max(0.85 - 0.08 * k, 0.35))
            shell = VGroup(ring)
            if k <= 5:
                npts = 8 * k * k
                # display compromise, stated plainly: per-star size and glow
                # are compressed (1/k, not the true 1/k²) so outer shells
                # stay visible; the TOTAL, which is what matters, is carried
                # honestly by the meter.
                for j in range(npts):
                    a = TAU * j / npts + 0.10 + 0.07 * k
                    shell.add(Dot(rk * np.array([math.cos(a),
                                                 math.sin(a), 0]),
                                  radius=0.045 / (k ** 0.6),
                                  fill_color=STARLIGHT,
                                  fill_opacity=0.90 / k))
            else:
                # past the fifth shell, stop resolving — Scene 1's own move
                dots = DashedVMobject(Circle(radius=rk), num_dashes=10 * k * k
                                      // 4, dashed_ratio=0.35)
                dots.set_stroke(color=STARLIGHT, width=1.7,
                                opacity=0.40)
                shell.add(dots)
            stack.add(shell)
            self.play(Create(ring),
                      LaggedStart(*[FadeIn(m) for m in shell[1:]],
                                  lag_ratio=0.002),
                      tot.animate.set_value(k),
                      FadeIn(tick_at(k)),
                      run_time=run_times[k - 3],
                      rate_func=rate_functions.ease_out_cubic)
        self.wait(0.8)   # no ceiling.  It was never going to stop.

        # the flood: the shells themselves brighten into the whiteout
        # (>>> POST: everything the score has been doing drops DEAD here —
        #  total silence carries the rest of the scene.)
        tfill.clear_updaters()
        cover = Rectangle(width=24, height=14, stroke_width=0,
                          fill_color=STARLIGHT, fill_opacity=0.0)
        cover.set_z_index(50)
        self.add(cover)
        bright = [m.animate.set_stroke(color=STARLIGHT, width=5.0,
                                       opacity=1.0)
                  for m in [self._sh1[0], self._sh2[0]]
                  + [s[0] for s in stack]]
        self.play(*bright, cover.animate.set_fill(opacity=1.0),
                  run_time=0.9, rate_func=rate_functions.ease_in_sine)

        # under the white: an invisible cut back to Scene 1's dome grammar
        keepers = {cover, self.frame_marks}
        for m in list(self.mobjects):
            if m not in keepers:
                self.remove(m)
        self.camera.frame.move_to(self.DOME_CAM).set(
            width=config.frame_width)
        dome = AnnularSector(inner_radius=0.0, outer_radius=self.DOME_R_OUT,
                             angle=PI, start_angle=0, fill_color=STARLIGHT,
                             fill_opacity=1.0, stroke_width=0)
        ground = Line([-7.2, 0, 0], [7.2, 0, 0], stroke_color=C_GROUND,
                      stroke_width=1.6, stroke_opacity=0.55).set_z_index(5)
        silhouette = Dot(ORIGIN, radius=0.06, fill_color=VOID,
                         fill_opacity=1.0).set_z_index(5)
        self.add(dome, ground, silhouette)
        self.play(cover.animate.set_fill(opacity=0.0), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)
        self.remove(cover)
        self.wait(3.0)   # the same unbearable dome — arrived at by math

        # …and back to the exact sky this all began with
        self._sample_baseline_sky()
        horizon, stars = self._build_baseline_sky()
        stars.veil.set_value(0.0)
        horizon.set_stroke(opacity=0.0)
        self.add(horizon, stars)
        self.play(FadeOut(dome), FadeOut(ground), FadeOut(silhouette),
                  stars.veil.animate.set_value(1.0),
                  horizon.animate.set_stroke(opacity=0.55),
                  self.camera.frame.animate.move_to(ORIGIN),
                  run_time=2.4, rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.2)

        if self.CLOSING_QUESTION:
            q = serif("so what is actually going on?", STARLIGHT, 40)
            q.move_to(UP * 1.35)
            self.play(Write(q), run_time=1.5,
                      rate_func=rate_functions.ease_in_out_sine)
        self.wait(3.2)   # silence.  Scene 3 owes everyone an answer.

        stars.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects
                    if m is not self.frame_marks],
                  self.frame_marks.animate.set_opacity(0.0),
                  run_time=2.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)