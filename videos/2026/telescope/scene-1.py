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
CYAN      = "#5B8FB0"   # secondary · sparing  (here: water / cool matter)

# quantity pigments — each keeps its colour across the whole series
C_ANGLE   = "#E08AAB"   # ANGLE θ — the swept wedge (Scene-1 seed: resolution)
C_LEN     = "#5B8FB0"   # LENGTH / r  (== CYAN)
C_GROUND  = "#7F8A99"   # ground / reference axis

SERIF = "Spectral"      # ideas; italic is the channel's voice & every equation
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(1)      # deterministic -> stable render cache


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
        h = target_width * 1.25
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


def make_aperture(radius=0.85, color=AMBER, width=3.0):
    """THE circle. It decides how much gets through — first a beaker's mouth,
    then a pupil. The same Circle mobject is threaded across Acts 1→3, because
    the sameness of the shape *is* the argument."""
    return Circle(radius=radius, stroke_color=color, stroke_width=width,
                  fill_color=color, fill_opacity=0.0)


def path_from(*segments, **style):
    """Stitch Lines/Arcs into ONE continuous VMobject so Create() draws a
    single unbroken silhouette — no wobble, no seams."""
    p = VMobject(**style)
    for i, seg in enumerate(segments):
        if i == 0:
            p.set_points(seg.get_points())
        else:
            p.add_line_to(seg.get_start())      # (zero-length weld)
            p.append_points(seg.get_points())
    return p


def soft_dot(center, r, color, opacity, halo=2.2, halo_op=0.35):
    """A dot with a breathing halo — reads as light, not as ink."""
    core = Circle(radius=r, stroke_width=0, fill_color=color,
                  fill_opacity=opacity).move_to(center)
    glow = Circle(radius=r * halo, stroke_width=0, fill_color=color,
                  fill_opacity=opacity * halo_op).move_to(center)
    return VGroup(glow, core)


# ═══════════════════════════════════════════════════════════════════════════
class Scene1_TwoProblems(MovingCameraScene):
    """SCENE 1 — the cold-open engine. Two failure modes are planted so every
    later scene can gesture back instead of re-explaining: (1) not enough light
    reaches the eye, (2) not enough angular separation between two points.
    One aperture motif — a single amber circle — carries the whole argument."""

    # ── director toggles (each is a one-line flip) ────────────────────────
    USE_MILKY_HOOK   = True    # (unused here; kept for series symmetry)
    LABEL_ANGLE      = True    # Act-4 wedge carries the word "ANGLE" (vocab seed)
    NUMBER_TILES     = True    # Act-5 tiles get "PROBLEM 1 / 2" numerals
    MERGE_REPLAY     = True    # Act-4 runs the separate<->fuse back-and-forth

    # ── locked geometry (every act reads from these) ──────────────────────
    APERTURE_R   = 0.85               # the one circle, in world units
    MOUTH_PT     = np.array([0.0, -1.35, 0.0])     # beaker mouth, low in frame
    BEAKER_BASE  = -3.15
    N_RAIN       = 74                 # streaks — dozens fall for every one caught
    RAIN_TOP     =  4.5
    RAIN_BOT     = -4.5
    STAR_PT      = np.array([-5.7, 3.25, 0.0])     # the radiating point, corner
    EYE_C        = np.array([2.65, 0.0, 0.0])      # side-view eyeball centre (A3+)
    EYE_R        = 2.35

    def construct(self):
        self.camera.frame.save_state()
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()

        self.wait(0.5)
        self.add(self.frame_marks)
        self.play(self.frame_marks.animate.set_opacity(0.5), run_time=0.8)

        self.act1_rain_and_beaker()
        self.act2_same_rain_different_sky()
        self.act3_the_myth_corrected()
        self.act4_two_stars_one_blur()
        self.act5_two_problems_one_curiosity()

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

    # ═══════════════════════════════════════════════════════ ACT 1 ═══════
    def act1_rain_and_beaker(self):
        """A wide curtain of rain. A small amber circle — a beaker's mouth —
        catches the few streaks that fall inside it; the rest fall straight
        through and fade. Ease into the mouth so the circle is the one variable
        that decided how much got caught."""

        rain = VGroup()
        catch_y    = self.MOUTH_PT[1]
        mouth_half = self.APERTURE_R * 0.92
        MARGIN     = 1.4                             # respawn head-room
        top_y      = self.RAIN_TOP + MARGIN
        span       = top_y - (self.RAIN_BOT - 1.0)   # full loop distance

        xs, speeds, lens_, widths, phases, caught = [], [], [], [], [], []
        for _ in range(self.N_RAIN):
            x = float(RNG.uniform(-7.0, 7.0))
            v = float(RNG.uniform(3.1, 4.6))
            L = float(RNG.uniform(0.34, 0.66))
            w = float(RNG.uniform(1.2, 2.1))         # depth: varied weights
            ph = float(RNG.uniform(0.0, span))
            xs.append(x); speeds.append(v); lens_.append(L)
            widths.append(w); phases.append(ph)
            caught.append(abs(x - self.MOUTH_PT[0]) < mouth_half)
            streak = Line([x, top_y, 0], [x, top_y - L, 0],
                          stroke_color=STARLIGHT, stroke_width=w,
                          stroke_opacity=0.0)
            rain.add(streak)
        rain.set_z_index(2)
        rain.time = 0.0
        rain.absorbing = 0
        reveal = ValueTracker(0.0)                   # global fade-in
        dim    = ValueTracker(1.0)                   # global end-of-act dim
        rain.reveal, rain.dim = reveal, dim          # kept alive with the group

        def rain_update(grp, dt):
            grp.time += dt
            g = reveal.get_value() * dim.get_value()
            absorbing = 0
            for i, s in enumerate(grp):
                fall = (phases[i] + speeds[i] * grp.time) % span
                head = top_y - fall                  # lower (leading) tip
                tail = head + lens_[i]               # upper (trailing) tip

                # entering the frame: fade in only once fully inside
                appear = float(np.interp(tail, [self.RAIN_TOP,
                                                self.RAIN_TOP + MARGIN],
                                         [1.0, 0.0]))

                if caught[i] and head <= catch_y:
                    # ── absorption: lower tip pinned, upper tip still falls
                    vis = tail - catch_y             # remaining visible length
                    if vis <= 0.02:
                        s.set_stroke(opacity=0.0)    # gone until it wraps
                        continue
                    absorbing += 1
                    frac = vis / lens_[i]            # 1 → just arrived, 0 → gone
                    warm = interpolate_color(
                        ManimColor(AMBER), ManimColor(STARLIGHT), frac)
                    s.put_start_and_end_on([xs[i], catch_y + vis, 0.0],
                                           [xs[i], catch_y, 0.0])
                    s.set_stroke(color=warm, width=widths[i] + 0.6,
                                 opacity=float((0.35 + 0.65 * frac) * g))
                    continue

                s.put_start_and_end_on([xs[i], tail, 0.0],
                                       [xs[i], head, 0.0])
                if caught[i]:
                    # brighten on approach — the mouth pulls the eye
                    near = float(np.interp(head, [catch_y, catch_y + 1.6],
                                           [1.0, 0.45]))
                    s.set_stroke(color=STARLIGHT, width=widths[i] + 0.4,
                                 opacity=float(near * appear * g))
                else:
                    # the uncaught majority dims to dust and dies at the floor
                    floor = float(np.interp(head,
                                            [self.RAIN_BOT, self.RAIN_BOT + 2.2],
                                            [0.0, 0.42]))
                    s.set_stroke(color=DUST, width=widths[i],
                                 opacity=float(floor * appear * g))
            grp.absorbing = absorbing
        rain.add_updater(rain_update)
        self.add(rain)
        self.play(reveal.animate.set_value(1.0), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.6)   # let the imbalance become undeniable


        mouth_y   = float(self.MOUTH_PT[1])
        base_y    = self.BEAKER_BASE
        top_half  = self.APERTURE_R                  # mouth half-width (== circle)
        base_half = self.APERTURE_R * 0.82           # a subtle inward taper
        mouth_ry  = self.APERTURE_R * 0.24           # foreshortened rim depth
        fil       = 0.24                             # true fillet radius

        lt = np.array([-top_half,  mouth_y, 0.0])
        rt = np.array([ top_half,  mouth_y, 0.0])
        lf = np.array([-base_half, base_y + fil, 0.0])   # left fillet start
        rf = np.array([ base_half, base_y + fil, 0.0])
        cl = np.array([-base_half + fil, base_y + fil, 0.0])  # fillet centres
        cr = np.array([ base_half - fil, base_y + fil, 0.0])

        body = path_from(
            Line(lt, lf),
            Arc(radius=fil, start_angle=PI, angle=PI / 2, arc_center=cl),
            Line([cl[0], base_y, 0], [cr[0], base_y, 0]),
            Arc(radius=fil, start_angle=3 * PI / 2, angle=PI / 2, arc_center=cr),
            Line([base_half, base_y + fil, 0], rt),
            stroke_color=DUST, stroke_width=2.4, stroke_opacity=0.9)

        # interior plate, matching the silhouette (rounded, so no sharp poke)
        interior = body.copy()
        interior.add_line_to(lt)                     # close across the mouth
        interior.set_stroke(width=0).set_fill(PANEL, opacity=0.55)

        # the mouth in perspective: far lip faint, near lip present
        def lip(ang0, color, width, op):
            a = Arc(radius=1, start_angle=ang0, angle=PI,
                    arc_center=self.MOUTH_PT, stroke_color=color,
                    stroke_width=width, stroke_opacity=op)
            a.stretch_to_fit_width(2 * top_half)
            a.stretch_to_fit_height(2 * mouth_ry)
            a.move_to(self.MOUTH_PT)
            return a
        rim_back  = lip(0,  DUST, 1.3, 0.30)         # upper half — behind
        rim_front = lip(PI, DUST, 1.7, 0.55)         # lower half — in front

        # a whisper of glass: one curved highlight down the left inner wall
        sheen = ArcBetweenPoints(
            [-top_half + 0.16, mouth_y - 0.30, 0],
            [-base_half + 0.18, base_y + 0.42, 0],
            angle=0.22, stroke_color=STARLIGHT,
            stroke_width=3.0, stroke_opacity=0.10)

        # grounding: a soft shadow pool under the base
        shadow = Ellipse(width=2 * base_half * 1.25, height=0.16,
                         stroke_width=0, fill_color="#000000",
                         fill_opacity=0.35).move_to([0, base_y - 0.06, 0])

        beaker_body = VGroup(shadow, interior, body, rim_back,
                             sheen, rim_front).set_z_index(3)

        # THE circle stays a true circle — its sameness across acts is the
        # argument. It reads as the mouth's opening; the elliptical rim behind
        # it supplies the sense of depth without distorting the motif.
        aperture = make_aperture(self.APERTURE_R).move_to(self.MOUTH_PT)
        aperture.set_z_index(7)
        self.aperture = aperture     # <<< threaded into Act 2 & 3

        self.play(
            AnimationGroup(
                FadeIn(shadow),
                FadeIn(interior),
                Create(body),
                AnimationGroup(Create(rim_back), Create(rim_front)),
                FadeIn(sheen),
                lag_ratio=0.16),
            run_time=1.6, rate_func=rate_functions.ease_out_cubic)

        # the mouth breathes with the light it swallows: a faint amber pool
        # whose glow tracks how many streaks are mid-absorption right now
        def make_glow():
            k = min(getattr(rain, "absorbing", 0), 4)
            op = (0.03 + 0.030 * k) * dim.get_value()
            e = Ellipse(width=2 * top_half * 0.92, height=2 * mouth_ry * 1.5,
                        stroke_width=0, fill_color=AMBER, fill_opacity=op)
            return e.move_to(self.MOUTH_PT).set_z_index(6)
        mouth_glow = always_redraw(make_glow)
        self.add(mouth_glow)
        self.wait(0.6)

        # ── the rising catch ─────────────────────────────────────────────
        #  The water is built from the SAME filleted geometry as the glass,
        #  sampled analytically — so it can never escape at the corners.  A
        #  bowed meniscus (bright near lip, faint far lip) matches the rim's
        #  perspective, and a few amber-warmed droplets keep falling from the
        #  mouth to the surface while it rises: the rain is what fills it.
        fill_level = ValueTracker(0.0)               # 0..1 of interior height
        interior_h = mouth_y - base_y
        FILL_TOP   = 0.62                            # fraction actually filled
        inset      = 0.05                            # water sits inside the stroke
        f2         = fil - inset * 0.5
        in_base    = base_half - inset

        def wall_half(y):
            """Inner half-width at height y (tapered walls, inset a hair)."""
            return float(np.interp(y, [base_y, mouth_y],
                                   [base_half, top_half])) - inset

        def water_half(y):
            """Half-width of the WATER at height y, honouring the fillets."""
            if y >= base_y + f2:
                return wall_half(y)
            dy = (base_y + f2) - y
            dx = math.sqrt(max(f2 * f2 - dy * dy, 0.0))
            return (in_base - f2) + dx

        def surface_y():
            return base_y + 0.02 + fill_level.get_value() * interior_h * FILL_TOP

        def make_fill():
            s = max(surface_y(), base_y + 0.03)
            hw = water_half(s)
            # boundary: down the left side, across the floor, up the right
            ys = list(np.linspace(s, base_y + f2, 3)) if s > base_y + f2 else []
            ys += list(np.linspace(min(s, base_y + f2), base_y, 7))
            left  = [np.array([-water_half(y), y, 0.0]) for y in ys]
            right = [np.array([ water_half(y), y, 0.0]) for y in reversed(ys)]
            pts = left + right
            blob = Polygon(*pts, stroke_width=0,
                           fill_color=CYAN, fill_opacity=0.30)
            # the meniscus, in the same perspective as the rim
            bow = min(0.5, hw * 0.55)
            near = ArcBetweenPoints([-hw, s, 0], [hw, s, 0], angle=bow,
                                    stroke_color=CYAN, stroke_width=2.2,
                                    stroke_opacity=0.9)
            far  = ArcBetweenPoints([-hw, s, 0], [hw, s, 0], angle=-bow,
                                    stroke_color=CYAN, stroke_width=1.2,
                                    stroke_opacity=0.35)
            gleam = ArcBetweenPoints([-hw, s, 0], [hw, s, 0], angle=bow,
                                     stroke_color=STARLIGHT, stroke_width=4.5,
                                     stroke_opacity=0.08)
            return VGroup(blob, far, near, gleam).set_z_index(4)
        water = always_redraw(make_fill)
        self.add(water)

        # droplets: the caught rain, continuing inside the glass
        N_DROP = 5
        d_xs = RNG.uniform(-top_half * 0.45, top_half * 0.45, N_DROP)
        d_v  = RNG.uniform(1.7, 2.5, N_DROP)
        d_ph = RNG.uniform(0.0, 1.0, N_DROP)
        drops = VGroup(*[Dot([d_xs[i], mouth_y - 0.1, 0], radius=0.030,
                             color=STARLIGHT, fill_opacity=0.0)
                         for i in range(N_DROP)])
        drops.set_z_index(5)
        drops.t = 0.0

        def drops_update(grp, dt):
            grp.t += dt
            start = mouth_y - 0.10
            gap = start - surface_y()
            vis = min(fill_level.get_value() * 10.0, 1.0) * dim.get_value()
            for i, d in enumerate(grp):
                if gap < 0.20 or vis <= 0.01:
                    d.set_opacity(0.0)
                    continue
                u = (d_ph[i] + d_v[i] * grp.t / max(gap, 0.4)) % 1.0
                y = start - u * gap
                env = float(np.interp(u, [0.0, 0.15, 0.85, 1.0],
                                      [0.0, 0.75, 0.75, 0.0]))
                d.move_to([d_xs[i], y, 0.0])
                d.set_fill(interpolate_color(ManimColor(AMBER),
                                             ManimColor(CYAN), u),
                           opacity=env * vis)
        drops.add_updater(drops_update)
        self.add(drops)

        self.play(fill_level.animate.set_value(1.0), run_time=3.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)

        # ── isolate the circle: ease the camera onto the mouth ────────────
        self.play(
            self.camera.frame.animate.scale(0.62).move_to(self.MOUTH_PT + UP * 0.05),
            dim.animate.set_value(0.22),             # through the tracker —
            run_time=1.6,                            # the updater cooperates
            rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.0)   # hold on the lone variable

        # stow act-1 furniture for the magic-move (the aperture stays)
        rain.clear_updaters()
        drops.clear_updaters()
        mouth_glow.clear_updaters()
        self._act1_debris = VGroup(beaker_body, water, drops, mouth_glow, rain)

    # ═══════════════════════════════════════════════════════ ACT 2 ═══════
    def act2_same_rain_different_sky(self):
        """The click. The beaker's mouth *is* a pupil — same circle. Rain
        relabels to light radiating from a star; of that whole fan, only a
        thin sliver reaches the pupil. Let the sliver sit, tiny, a beat too long."""

        # fade the beaker context around the still-held amber circle
        self.play(FadeOut(self._act1_debris, run_time=1.0),
                  rate_func=rate_functions.ease_in_out_sine)

        # grow an iris ring around the identical pupil — now it reads as an eye
        iris = Circle(radius=self.APERTURE_R * 2.05, stroke_color=STARLIGHT,
                      stroke_width=2.0, stroke_opacity=0.0,
                      fill_color=PANEL, fill_opacity=0.0)
        iris.move_to(self.aperture.get_center()).set_z_index(5)
        self.add(iris)
        self.play(
            iris.animate.set_stroke(opacity=0.55).set_fill(opacity=0.35),
            self.aperture.animate.set_fill(AMBER, opacity=0.12),
            run_time=1.1, rate_func=rate_functions.ease_out_cubic)
        # a soft settle: the shape locks. (>>> POST: matched chime here.)
        self.play(Flash(self.aperture, color=AMBER, line_length=0.18,
                        num_lines=16, flash_radius=self.APERTURE_R + 0.35),
                  run_time=0.7)
        self.wait(0.6)

        # pull back to reveal the whole sky the pupil sits in
        self.play(self.camera.frame.animate.restore(),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        eye = VGroup(iris, self.aperture)
        self.play(eye.animate.move_to([3.4, -1.15, 0]).scale(0.62),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)

        pupil_c = self.aperture.get_center()
        pupil_r = self.APERTURE_R * 0.62

        # the star + the full radiation fan (dim — "all of this light exists")
        star = VGroup(
            soft_dot(self.STAR_PT, 0.10, STARLIGHT, 1.0, halo=2.6, halo_op=0.20),
            Circle(radius=0.24, stroke_color=STARLIGHT, stroke_width=1.2,
                   stroke_opacity=0.5).move_to(self.STAR_PT)).set_z_index(7)
        star_lbl = mono("A STAR", DUST, 12).next_to(star, DOWN, buff=0.22)

        fan = VGroup()
        for a in np.linspace(-88, -2, 26):     # a wide downward-right sweep
            d = np.array([math.cos(math.radians(a)), math.sin(math.radians(a)), 0])
            fan.add(Line(self.STAR_PT, self.STAR_PT + d * 12.5,
                         stroke_color=DUST, stroke_width=1.1, stroke_opacity=0.18))
        fan.set_z_index(1)

        self.play(FadeIn(star, scale=0.6), Write(star_lbl), run_time=0.9)
        self.play(LaggedStart(*[Create(r) for r in fan],
                              lag_ratio=0.03, run_time=1.6))
        self.wait(0.7)

        # the sliver: the only part of the fan that reaches the pupil
        top_edge = pupil_c + UP * pupil_r
        bot_edge = pupil_c + DOWN * pupil_r
        sliver = Polygon(self.STAR_PT, top_edge, bot_edge,
                         stroke_width=0, fill_color=STARLIGHT, fill_opacity=0.16)
        r1 = Line(self.STAR_PT, top_edge, stroke_color=STARLIGHT, stroke_width=2.0)
        r2 = Line(self.STAR_PT, bot_edge, stroke_color=STARLIGHT, stroke_width=2.0)
        self.sliver = VGroup(sliver, r1, r2).set_z_index(2)

        self.play(fan.animate.set_stroke(opacity=0.07), run_time=0.6)
        self.play(FadeIn(sliver), Create(r1), Create(r2), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)

        # three photons ride the sliver home — light *travels*
        paths = [Line(self.STAR_PT, p) for p in
                 (top_edge, pupil_c, bot_edge)]
        photons = VGroup(*[Dot(self.STAR_PT, radius=0.045, color=STARLIGHT,
                               fill_opacity=0.9) for _ in paths]).set_z_index(8)
        self.add(photons)
        self.play(LaggedStart(
            *[MoveAlongPath(ph, pa, rate_func=rate_functions.ease_in_sine)
              for ph, pa in zip(photons, paths)],
            lag_ratio=0.18), run_time=1.5)
        self.play(photons.animate.set_opacity(0.0),
                  Flash(self.aperture, color=AMBER, line_length=0.10,
                        num_lines=10, flash_radius=pupil_r + 0.18),
                  run_time=0.5)
        self.remove(photons)

        caught_lbl = mono("ONLY THIS REACHES YOU", AMBER, 12)
        caught_lbl.next_to(self.aperture, DR, buff=0.32)
        self.play(Write(caught_lbl), run_time=0.7)
        self.wait(1.6)   # the tiny sliver against the vast fan — hold too long

        self._act2_debris = VGroup(fan, star, star_lbl, caught_lbl, eye)

    # ═══════════════════════════════════════════════════════ ACT 3 ═══════
    def act3_the_myth_corrected(self):
        """Push into a side-view eye. Two wrong answers land and get negated.
        The real cause: the dot arrives so faint it never trips a receptor —
        proven against a brighter dot next door that flips its cell fully on."""

        self.play(FadeOut(self._act2_debris),
                  FadeOut(self.sliver), run_time=0.9)

        # ── the eye, in true section ──────────────────────────────────────
        #  Sclera drawn as a wall (outer line + faint inner echo), a domed
        #  cornea, iris bodies with real mass, a genuinely biconvex lens
        #  built from two circular arcs, the retina hugging the back inner
        #  wall with a soft photosensitive glow, and an optic-nerve stub so
        #  the section reads anatomical, not schematic.
        cx = self.EYE_C
        R  = self.EYE_R
        open_a = 0.46                                # front-opening half-angle
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
        iris_x  = front[0] + 0.5                     # iris/pupil plane
        pupil_r = R * 0.19
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
                     retina_arc, nerve, lens, iris_top, iris_bot,
                     pupil).set_z_index(3)

        self.play(LaggedStart(
            AnimationGroup(Create(sclera), Create(sclera_in)),
            FadeIn(globe_fill),
            Create(cornea),
            AnimationGroup(FadeIn(iris_top), FadeIn(iris_bot)),
            AnimationGroup(Create(retina_arc), FadeIn(retina_glow)),
            FadeIn(nerve),
            DrawBorderThenFill(lens),
            FadeIn(pupil),
            lag_ratio=0.16, run_time=2.2))
        fig = mono("FIG · THE EYE, IN SECTION", DUST, 12).to_corner(UL, buff=0.6)
        self.play(FadeIn(fig, shift=DOWN * 0.1), run_time=0.6)

        # ── the light comes in: parallel rays refract and converge ────────
        land_pt = cx + R * 0.9 * RIGHT
        def ray(off, w, op):
            r = VMobject(stroke_color=STARLIGHT, stroke_width=w,
                         stroke_opacity=op)
            r.set_points_as_corners([
                [-6.7, cx[1] + off, 0],
                [lx - bulge * 0.4, cx[1] + off, 0],   # parallel to the lens
                land_pt])                             # bent to the focus
            return r
        rays = VGroup(ray(+pupil_r * 0.62, 1.7, 0.45),
                      ray(0.0, 2.0, 0.55),
                      ray(-pupil_r * 0.62, 1.7, 0.45))
        faint_dot = soft_dot(land_pt, 0.06, STARLIGHT, 0.30, halo=2.4,
                             halo_op=0.30)
        self.play(LaggedStart(*[Create(r) for r in rays],
                              lag_ratio=0.15, run_time=1.5),
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeIn(faint_dot, scale=0.6), run_time=0.5)
        self.wait(0.7)

        # ── negate the two myths, one at a time ───────────────────────────
        for word in ("Too small?", "Too far?"):
            wrong = serif(word, STARLIGHT, 46).to_edge(UP, buff=1.0)
            self.play(Write(wrong), run_time=0.7)
            self.wait(0.4)
            strike = Line(wrong.get_left(), wrong.get_right(),
                          stroke_color=C_ANGLE, stroke_width=4.0)
            self.play(Create(strike), run_time=0.35)
            self.play(FadeOut(wrong, shift=DOWN * 0.15),
                      FadeOut(strike, shift=DOWN * 0.15), run_time=0.5)
        self.wait(0.3)

        # ── the real reason: a receptor grid + a threshold ────────────────
        grid, cells = self._receptor_grid(rows=4, cols=3,
                                          center=land_pt + RIGHT * 0.15)
        grid.set_z_index(5)
        # zoom onto the retina patch to make "registers vs not" readable
        self.play(FadeOut(rays),
                  self.camera.frame.animate.scale(0.55).move_to(land_pt + RIGHT * 0.1),
                  run_time=1.4, rate_func=rate_functions.ease_in_out_sine)
        self.play(LaggedStart(*[Create(c) for row in cells for c in row],
                              lag_ratio=0.04, run_time=1.2))
        self.wait(0.4)

        # THRESHOLD (physics honesty): a cell flips on only if intensity >= 0.5
        THRESH = 0.5
        faint_I, bright_I = 0.34, 0.92
        target_faint = cells[2][1]
        target_bright = cells[1][2]

        # faint arrival: below threshold -> barely nudges its cell
        self.play(faint_dot.animate.move_to(target_faint.get_center()),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_sine)
        self.play(target_faint.animate.set_fill(
            AMBER, opacity=self._cell_response(faint_I, THRESH)), run_time=0.6)
        near = mono("BELOW THRESHOLD", DUST, 11).next_to(grid, DOWN, buff=0.28)
        self.play(FadeIn(near), run_time=0.5)
        self.wait(0.9)

        # a brighter dot next door: above threshold -> flips fully ON
        bright_dot = soft_dot(target_bright.get_center(), 0.06, STARLIGHT,
                              bright_I, halo=2.4, halo_op=0.35)
        self.play(FadeIn(bright_dot, scale=0.5), run_time=0.5)
        self.play(target_bright.animate.set_fill(
            AMBER, opacity=self._cell_response(bright_I, THRESH)),
            Flash(target_bright, color=AMBER, line_length=0.08,
                  flash_radius=0.28, num_lines=12), run_time=0.6)
        on = mono("ABOVE THRESHOLD · REGISTERS", AMBER, 11)
        on.next_to(bright_dot, UP, buff=0.24)
        self.play(FadeIn(on), run_time=0.5)
        self.wait(1.2)

        # keep the retina patch alive for Act 4; stow the rest
        self.retina = grid
        self.retina_cells = cells
        self.retina_center = land_pt + RIGHT * 0.15
        self._act3_stow = VGroup(eye, fig, faint_dot, bright_dot, near, on)
        self.play(self.camera.frame.animate.restore(),
                  FadeOut(self._act3_stow), run_time=1.3,
                  rate_func=rate_functions.ease_in_out_sine)

    def _receptor_grid(self, rows, cols, center, pitch=0.5, r=0.16):
        grid = VGroup()
        cells = []
        w = (cols - 1) * pitch
        h = (rows - 1) * pitch
        for j in range(rows):
            row = []
            for i in range(cols):
                pos = center + np.array([i * pitch - w / 2,
                                         h / 2 - j * pitch, 0])
                cell = Circle(radius=r, stroke_color=DUST, stroke_width=1.4,
                              stroke_opacity=0.6, fill_color=AMBER,
                              fill_opacity=0.0).move_to(pos)
                grid.add(cell)
                row.append(cell)
            cells.append(row)
        return grid, cells

    @staticmethod
    def _cell_response(intensity, thresh):
        """Honest step-ish response: below threshold barely lifts the cell;
        above threshold saturates it. Smooth around the knee."""
        if intensity < thresh:
            return 0.10 * (intensity / thresh)          # a faint nudge only
        return 0.30 + 0.65 * min((intensity - thresh) / (1 - thresh), 1.0)

    # ═══════════════════════════════════════════════════════ ACT 4 ═══════
    def act4_two_stars_one_blur(self):
        """A second star. Both cones reach the pupil at almost the same angle —
        mark the wedge. Drive separation from one tracker: as the stars close,
        the wedge narrows and the two retina dots drift, overlap, and fuse.
        Everything dynamic reveals through its own tracker, because FadeIn on
        an always_redraw mobject is overwritten every frame — it would pop."""

        pupil_pt = self.EYE_C + LEFT * self.EYE_R
        base_ang = math.radians(150)     # up-left, toward the star corner
        sep = ValueTracker(0.16)         # angular half-separation (radians)
        rv  = ValueTracker(0.0)          # reveal for the star/ray/wedge layer
        rvd = ValueTracker(0.0)          # reveal for the retina dots

        def star_pos(sign):
            a = base_ang + sign * sep.get_value()
            return pupil_pt + np.array([math.cos(a), math.sin(a), 0]) * 6.4

        def make_star(sign):
            p = star_pos(sign)
            g = rv.get_value()
            return VGroup(
                Dot(p, radius=0.09, color=STARLIGHT, fill_opacity=g),
                Circle(radius=0.2, stroke_color=STARLIGHT, stroke_width=1.0,
                       stroke_opacity=0.45 * g).move_to(p)).set_z_index(7)
        starA = always_redraw(lambda: make_star(+1))
        starB = always_redraw(lambda: make_star(-1))

        rayA = always_redraw(lambda: Line(
            star_pos(+1), pupil_pt, stroke_color=STARLIGHT,
            stroke_width=1.8, stroke_opacity=0.5 * rv.get_value()))
        rayB = always_redraw(lambda: Line(
            star_pos(-1), pupil_pt, stroke_color=STARLIGHT,
            stroke_width=1.8, stroke_opacity=0.5 * rv.get_value()))

        # the incoming wedge, right at the pupil, in the ANGLE pigment —
        # an arc plus a translucent sector, so the angle has *area*
        def make_wedge():
            aU = base_ang + sep.get_value()
            aL = base_ang - sep.get_value()
            g = rv.get_value()
            arc = Arc(radius=0.85, start_angle=aL, angle=(aU - aL),
                      arc_center=pupil_pt, stroke_color=C_ANGLE,
                      stroke_width=3.0, stroke_opacity=g)
            sect = AnnularSector(inner_radius=0.0, outer_radius=0.85,
                                 start_angle=aL, angle=(aU - aL),
                                 stroke_width=0, fill_color=C_ANGLE,
                                 fill_opacity=0.10 * g).shift(pupil_pt)
            return VGroup(sect, arc)
        wedge = always_redraw(make_wedge)

        # re-show a compact eye so the pupil has a body again
        eyeball = Circle(radius=self.EYE_R, stroke_color=STARLIGHT,
                         stroke_width=1.4, stroke_opacity=0.35,
                         fill_color=PANEL, fill_opacity=0.28).move_to(self.EYE_C)
        pupil = make_aperture(0.30, width=2.4).move_to(pupil_pt)
        pupil.set_fill(AMBER, opacity=0.10)
        eye = VGroup(eyeball, pupil).set_z_index(3)

        self.play(FadeIn(eye), FadeIn(self.retina), run_time=0.9)
        self.add(rayA, rayB, starA, starB, wedge)
        self.play(rv.animate.set_value(1.0), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)

        if self.LABEL_ANGLE:
            ang_lbl = always_redraw(lambda: mono("ANGLE", C_ANGLE, 12).move_to(
                pupil_pt + np.array([math.cos(base_ang), math.sin(base_ang), 0]) * 1.35))
            self.play(FadeIn(ang_lbl), run_time=0.5)
        self.wait(0.7)

        # two retina dots whose separation & blur read from `sep` — each a
        # soft core-and-halo, so overlap looks like light pooling, not ink
        cA, cB = self.retina_cells[1][0], self.retina_cells[2][2]
        pA, pB = cA.get_center(), cB.get_center()
        mid = (pA + pB) / 2
        sep0 = sep.get_value()

        def dot_pair():
            frac = sep.get_value() / sep0
            g = rvd.get_value()
            offset = (pB - pA) / 2 * frac
            blur = np.interp(frac, [0.0, 1.0], [0.34, 0.14])   # closer -> blurs
            op = np.interp(frac, [0.0, 1.0], [0.55, 0.95]) * g
            return VGroup(
                soft_dot(mid + offset, blur * 0.55, AMBER, op, halo=1.9,
                         halo_op=0.40),
                soft_dot(mid - offset, blur * 0.55, AMBER, op, halo=1.9,
                         halo_op=0.40)).set_z_index(6)
        dots = always_redraw(dot_pair)
        self.add(dots)
        self.play(rvd.animate.set_value(1.0), run_time=0.6)
        self.wait(0.6)

        # the merge: close the stars -> wedge narrows -> two dots fuse into one
        self.play(sep.animate.set_value(0.012), run_time=2.4,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(Flash(Point(mid), color=AMBER, line_length=0.10,
                        num_lines=12, flash_radius=0.40), run_time=0.5)
        merged_lbl = mono("ONE BLUR", AMBER, 12).next_to(self.retina, DOWN, buff=0.3)
        self.play(FadeIn(merged_lbl), run_time=0.5)
        self.wait(1.0)   # (>>> POST: a small merge sound lands here.)

        # controllable back-and-forth: separate cleanly, then fuse again
        if self.MERGE_REPLAY:
            self.play(FadeOut(merged_lbl), run_time=0.3)
            self.play(sep.animate.set_value(0.16), run_time=1.6,
                      rate_func=rate_functions.ease_in_out_sine)
            self.wait(0.5)
            self.play(sep.animate.set_value(0.012), run_time=1.6,
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(FadeIn(merged_lbl), run_time=0.4)
            self.wait(0.8)

        # freeze the final geometry for the Act-5 icon, then clear
        for m in (rayA, rayB, starA, starB, wedge, dots):
            m.clear_updaters()
        act4_group = VGroup(eye, self.retina, rayA, rayB, starA, starB,
                            wedge, dots, merged_lbl)
        if self.LABEL_ANGLE:
            ang_lbl.clear_updaters()
            act4_group.add(ang_lbl)
        self._act4_group = act4_group
        self.play(FadeOut(act4_group), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)

    # ═══════════════════════════════════════════════════════ ACT 5 ═══════
    def act5_two_problems_one_curiosity(self):
        """The reusable summary. Two tiles: a thin-cone/retina icon = 'Not
        Enough Light'; an angle-wedge/merged-dot icon = 'Can't Tell Detail
        Apart'. Close on the question that pulls into Scene 2."""

        tileA = self._tile_light().shift(LEFT * 3.4 + UP * 0.4)
        tileB = self._tile_detail().shift(RIGHT * 3.4 + UP * 0.4)

        self.play(
            LaggedStart(FadeIn(tileA, shift=RIGHT * 0.3),
                        FadeIn(tileB, shift=LEFT * 0.3),
                        lag_ratio=0.25, run_time=1.4),
            rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        labA = serif("Not Enough Light", STARLIGHT, 30, italic=False)
        labB = serif("Can't Tell Detail Apart", STARLIGHT, 30, italic=False)
        labA.next_to(tileA, DOWN, buff=0.4)
        labB.next_to(tileB, DOWN, buff=0.4)
        self.play(Write(labA), Write(labB), run_time=1.0)

        if self.NUMBER_TILES:
            n1 = mono("PROBLEM 1", AMBER, 12).next_to(tileA, UP, buff=0.35)
            n2 = mono("PROBLEM 2", AMBER, 12).next_to(tileB, UP, buff=0.35)
            self.play(FadeIn(n1), FadeIn(n2), run_time=0.6)
        self.wait(0.8)

        question = serif("How did curiosity solve both?", STARLIGHT, 40)
        question.to_edge(DOWN, buff=0.85)
        rule = Line(LEFT * 0.7, RIGHT * 0.7, stroke_color=AMBER,
                    stroke_width=1.5).next_to(question, UP, buff=0.35)
        self.play(Create(rule), run_time=0.5)
        self.play(Write(question), run_time=1.2)
        self.wait(1.4)

        # >>> POST: hard whip-pan into Scene 2 (no fade). A fast push to sell it:
        self.play(self.camera.frame.animate.shift(RIGHT * 16).scale(1.15),
                  run_time=0.55, rate_func=rate_functions.rush_into)

    # ── Act-5 tile builders (the reusable asset) ──────────────────────────
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

    def _tile_light(self):
        f = self._tile_frame()
        c = f.get_center()
        pupil = make_aperture(0.34, width=2.2).move_to(c + RIGHT * 0.95)
        pupil.set_fill(AMBER, opacity=0.10)
        star = Dot(c + LEFT * 1.05 + UP * 0.55, radius=0.06, color=STARLIGHT)
        top = pupil.get_center() + UP * 0.22
        bot = pupil.get_center() + DOWN * 0.22
        sliver = Polygon(star.get_center(), top, bot, stroke_width=0,
                         fill_color=STARLIGHT, fill_opacity=0.16)
        r1 = Line(star.get_center(), top, stroke_color=STARLIGHT, stroke_width=1.6)
        r2 = Line(star.get_center(), bot, stroke_color=STARLIGHT, stroke_width=1.6)
        dot = Dot(pupil.get_center() + RIGHT * 0.1, radius=0.05,
                  color=STARLIGHT).set_opacity(0.3)
        return VGroup(f, sliver, r1, r2, star, pupil, dot)

    def _tile_detail(self):
        f = self._tile_frame()
        c = f.get_center()
        pupil_pt = c + RIGHT * 0.95
        pupil = make_aperture(0.34, width=2.2).move_to(pupil_pt)
        pupil.set_fill(AMBER, opacity=0.10)
        a = math.radians(150)
        s = 0.11
        pA = pupil_pt + np.array([math.cos(a + s), math.sin(a + s), 0]) * 1.7
        pB = pupil_pt + np.array([math.cos(a - s), math.sin(a - s), 0]) * 1.7
        r1 = Line(pA, pupil_pt, stroke_color=STARLIGHT, stroke_width=1.6, stroke_opacity=0.6)
        r2 = Line(pB, pupil_pt, stroke_color=STARLIGHT, stroke_width=1.6, stroke_opacity=0.6)
        wedge = Arc(radius=0.5, start_angle=a - s, angle=2 * s,
                    arc_center=pupil_pt, stroke_color=C_ANGLE, stroke_width=2.6)
        blur = Circle(radius=0.14, stroke_width=0, fill_color=AMBER,
                      fill_opacity=0.8).move_to(pupil_pt + RIGHT * 0.15)
        return VGroup(f, r1, r2, wedge, blur, pupil)
