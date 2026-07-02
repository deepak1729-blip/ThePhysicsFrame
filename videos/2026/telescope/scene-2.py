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
C_MASS    = "#B89A86"   # MATTER — here the lentil / warm organic tone
C_GROUND  = "#7F8A99"   # ground / reference axis

SERIF = "Spectral"      # ideas; italic is the channel's voice & every equation
MONO  = "Space Mono"    # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(2)      # deterministic -> stable render cache


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
    """Labels & metadata only — Space Mono."""
    t = Text(s, font=MONO, font_size=size, color=color)
    if spacing:
        t.set(width=t.width * (1 + spacing * 0.5))
    return t


def make_aperture(radius=0.34, color=AMBER, width=2.2):
    """The pupil circle carried across Scene 1 — reused inside the tiles here."""
    return Circle(radius=radius, stroke_color=color, stroke_width=width,
                  fill_color=color, fill_opacity=0.10)


def biconvex(h=1.1, bulge=1.15, color=CYAN, width=2.4, fill_op=0.12):
    """A lens cross-section — two opposed arcs closing into a lentil/vesica.
    The SAME shape a lentil bean has; the etymology of 'lens' rests on it."""
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
    """A poorly-resolved star: concentric translucent discs with noisy radii,
    so the edge reads as genuinely fuzzy — not a clean circle waiting to sharpen."""
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


# ═══════════════════════════════════════════════════════════════════════════
class Scene2_NotAMagnifyingGlass(MovingCameraScene):
    """SCENE 2 — bust 'telescope = zoom lens', then redefine the device by its
    two real jobs (Scene 1's two problems, relabelled), ground it in the spyglass
    toy and the word 'lens', and end on Galileo's first look up."""

    # ── director toggles (each is a one-line flip) ────────────────────────
    SHOW_BELIEF_TEXT   = True    # Act-1 states 'just a magnifying glass' in words
    USE_SPYGLASS_IMAGE = True   # Act-3 real 17th-c. engraving still (cuttable)
    MAG_COUNT          = True    # Act-4 literal 1..30× count-up vs a blur-up
    USE_MILKY_IMAGE    = True   # Act-5 real Milky-Way long-exposure overlay
    NUMBER_TILES       = True   # keep tiles untitled (matches Scene 1)

    # ── locked geometry ───────────────────────────────────────────────────
    TUBE_L   = 4.0
    TUBE_W   = 1.05
    MW_TILT  = -18 * DEGREES

    def construct(self):
        self.camera.frame.save_state()
        self.frame_marks = VGroup(*[corner_L(o, opacity=0.0)
                                    for o in (UL, UR, DL, DR)])
        self._pin_frame_marks()

        self.wait(0.4)
        self.add(self.frame_marks)
        self.play(self.frame_marks.animate.set_opacity(0.5), run_time=0.8)

        self.act1_just_a_magnifying_glass()
        self.act2_what_it_actually_does()
        self.act3_the_toy_called_spyglass()
        self.act4_galileos_upgrade()
        self.act5_first_look_up()

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
    def act1_just_a_magnifying_glass(self):
        """Test the myth literally: scale a blurry blob up, camera pushing in
        with it in lockstep — the blur scales too. No new structure resolves."""
        blob = soft_blob(0.42, color=STARLIGHT).move_to(ORIGIN).set_z_index(3)
        self.play(FadeIn(blob, scale=0.7), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)
        cap = mono("A DISTANT STAR", DUST, 12).next_to(blob, DOWN, buff=0.8)
        self.play(FadeIn(cap), run_time=0.5)
        self.wait(0.6)

        if self.SHOW_BELIEF_TEXT:
            belief = serif("\u201cA telescope is just a magnifying glass.\u201d",
                           STARLIGHT, 34).to_edge(UP, buff=1.0)
            self.play(Write(belief), run_time=1.1)
            self.wait(0.6)

        # the failed test: blob + camera zoom in perfect lockstep -> same fuzz
        zoom = 3.4
        self.play(FadeOut(cap), run_time=0.4)
        self.play(
            blob.animate.scale(zoom),
            self.camera.frame.animate.scale(zoom).move_to(blob.get_center()),
            run_time=2.6, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)
        verdict = mono("STILL A BLUR", DUST, 14).move_to(
            self.camera.frame.get_bottom() + UP * 0.9)
        self.play(FadeIn(verdict, shift=UP * 0.1), run_time=0.6)
        self.wait(1.4)   # anticlimax — hold a beat too long

        self._act1 = VGroup(blob, verdict)
        if self.SHOW_BELIEF_TEXT:
            self._act1.add(belief)
        self.play(FadeOut(self._act1),
                  self.camera.frame.animate.restore(), run_time=1.2,
                  rate_func=rate_functions.ease_in_out_sine)

    # ═══════════════════════════════════════════════════════ ACT 2 ═══════
    def act2_what_it_actually_does(self):
        """Scene 1's two closing tiles slide back in and relabel in place as the
        telescope's real jobs. Magnification arrives smaller, tethered, demoted."""
        tileA = self._tile_light().shift(LEFT * 3.4 + UP * 0.55)
        tileB = self._tile_detail().shift(RIGHT * 3.4 + UP * 0.55)
        labA = serif("Not Enough Light", STARLIGHT, 26, italic=False)
        labB = serif("Can't Tell Detail Apart", STARLIGHT, 26, italic=False)
        labA.next_to(tileA, DOWN, buff=0.34)
        labB.next_to(tileB, DOWN, buff=0.34)

        self.play(
            FadeIn(tileA, shift=RIGHT * 4.5),
            FadeIn(tileB, shift=LEFT * 4.5),
            run_time=1.3, rate_func=rate_functions.ease_out_cubic)
        self.play(Write(labA), Write(labB), run_time=0.9)
        self.wait(0.9)   # the callback lands: "those two problems"

        # relabel in place — the tiles stay; only the words evolve
        newA = serif("Catch More Light", STARLIGHT, 26, italic=False).move_to(labA)
        newB = serif("Separate Fine Detail", STARLIGHT, 26, italic=False).move_to(labB)
        self.play(
            ReplacementTransform(labA, newA),
            ReplacementTransform(labB, newB),
            tileA.animate.set_stroke(width=1.6),
            run_time=1.1, rate_func=rate_functions.ease_in_out_sine)
        jobs = mono("THE TELESCOPE'S TWO JOBS", AMBER, 12).to_edge(UP, buff=0.9)
        self.play(FadeIn(jobs, shift=DOWN * 0.1), run_time=0.6)
        self.wait(1.0)

        # the demotion: a smaller tile from below, tethered, obviously subordinate
        magt = self._tile_mag().scale(0.62).shift(DOWN * 2.35)
        maglab = serif("Magnification", DUST, 20, italic=True).next_to(magt, DOWN, buff=0.22)
        t1 = Line(tileA.get_bottom() + DOWN * 0.05, magt.get_left() + UP * 0.1,
                  stroke_color=DUST, stroke_width=1.2, stroke_opacity=0.5)
        t2 = Line(tileB.get_bottom() + DOWN * 0.05, magt.get_right() + UP * 0.1,
                  stroke_color=DUST, stroke_width=1.2, stroke_opacity=0.5)
        self.play(
            FadeIn(magt, shift=UP * 0.5, scale=0.9),
            run_time=1.0, rate_func=rate_functions.ease_out_cubic)
        self.play(Create(t1), Create(t2), FadeIn(maglab), run_time=0.8)
        self.wait(0.4)
        side = mono("— a side-effect", DUST, 12).next_to(maglab, RIGHT, buff=0.25)
        self.play(FadeIn(side), run_time=0.5)
        self.wait(1.3)

        self._act2 = VGroup(tileA, tileB, newA, newB, jobs, magt, maglab,
                            side, t1, t2)
        self.play(FadeOut(self._act2), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)

    # ═══════════════════════════════════════════════════════ ACT 3 ═══════
    def act3_the_toy_called_spyglass(self):
        """A line-drawn tube. Parallel rays enter, meet the lens, exit more
        converged. Then a lentil magic-moves into the lens's own cross-section,
        and 'LENS' stamps on — the visual proof arriving before the word."""
        tube = self._make_tube()
        tube.move_to(ORIGIN).set_z_index(4)
        self.tube = tube                     # <<< reused & reworked in Act 4

        if self.USE_SPYGLASS_IMAGE:
            eng = safe_image("spyglass_engraving.png", 3.4, "17TH-C. SPYGLASS")
            eng.to_corner(UR, buff=0.7)
            self.add(eng)

        self.play(Create(tube.body), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)
        title = mono("1600S · A TOY CALLED THE \u2018SPYGLASS\u2019", DUST, 13)
        title.to_edge(UP, buff=0.85)
        self.play(FadeIn(title, shift=DOWN * 0.1), run_time=0.6)
        self.play(FadeIn(tube.lens), run_time=0.6)
        self.wait(0.5)

        # optics: parallel in -> refract at lens plane -> converge to a focus
        lens_x = tube.lens.get_center()[0]
        focus = np.array([lens_x + 1.55, 0.0, 0.0])
        ys = [0.34, 0.17, -0.17, -0.34]
        parallels, bends = VGroup(), VGroup()
        for y in ys:
            start = np.array([-self.TUBE_L / 2 + 0.15, y, 0])
            hit = np.array([lens_x, y, 0])
            parallels.add(Line(start, hit, stroke_color=STARLIGHT,
                               stroke_width=2.0, stroke_opacity=0.75))
            bends.add(Line(hit, focus, stroke_color=STARLIGHT,
                           stroke_width=2.0, stroke_opacity=0.55))
        self.play(LaggedStart(*[Create(l) for l in parallels],
                              lag_ratio=0.12, run_time=1.0))
        self.wait(0.3)
        self.play(LaggedStart(*[Create(l) for l in bends],
                              lag_ratio=0.12, run_time=1.0))
        conv_lbl = mono("RAYS BENT INWARD", DUST, 11).next_to(focus, RIGHT, buff=0.3)
        self.play(FadeIn(conv_lbl), run_time=0.5)
        self.wait(1.1)

        # clear the optics; keep the lens for the etymology beat
        rays = VGroup(parallels, bends, conv_lbl)
        self.play(FadeOut(rays), FadeOut(tube.body), run_time=0.8)
        self.play(tube.lens.animate.move_to(RIGHT * 1.9).scale(1.35),
                  run_time=1.0, rate_func=rate_functions.ease_in_out_sine)

        # the lentil — literally the same biconvex shape — beside the lens
        lentil = biconvex(1.1 * 1.35, bulge=1.28, color=C_MASS,
                          width=2.4, fill_op=0.22).move_to(LEFT * 2.4)
        lentil_lbl = serif("a lentil", C_MASS, 24).next_to(lentil, DOWN, buff=0.35)
        self.play(FadeIn(lentil, shift=RIGHT * 0.2), FadeIn(lentil_lbl),
                  run_time=0.9)
        self.wait(0.7)

        # magic-move: the lentil AND the displaced lens converge into a single
        # centred lens — same shape, so it reads as a proof, not a resemblance.
        # (Transforming the GROUP into one target leaves no stray copy behind.)
        merged = biconvex(self.TUBE_W * 0.88, bulge=1.15, color=CYAN,
                          width=2.4, fill_op=0.12).move_to(ORIGIN)
        tube.remove(tube.lens)
        self.remove(tube.lens)
        self.play(
            ReplacementTransform(VGroup(lentil, tube.lens), merged),
            FadeOut(lentil_lbl, shift=DOWN * 0.2),
            run_time=1.3, rate_func=rate_functions.ease_in_out_sine)
        tube.lens = merged
        tube.add(merged)
        self.wait(0.4)

        # the payoff word arrives AFTER the shapes match
        lens_word = serif("LENS", AMBER, 56, italic=False).move_to(DOWN * 1.7)
        etym = mono("LATIN  \u2018LENS\u2019  =  LENTIL", DUST, 12).next_to(lens_word, DOWN, buff=0.3)
        self.play(Write(lens_word), run_time=0.7)                # (>>> POST: soft pop)
        self.play(Flash(lens_word, color=AMBER, line_length=0.15,
                        num_lines=14, flash_radius=1.1), run_time=0.6)
        self.play(FadeIn(etym), run_time=0.5)
        self.wait(1.4)

        self._act3 = VGroup(title, lens_word, etym)
        if self.USE_SPYGLASS_IMAGE:
            self._act3.add(eng)
        self.play(FadeOut(self._act3), run_time=1.0)

    # ═══════════════════════════════════════════════════════ ACT 4 ═══════
    def act4_galileos_upgrade(self):
        """The toy becomes an instrument: sharpen the lens, count magnification
        up toward 20–30×. Then the plain, unhurried pivot — the tube tilts up,
        the ground drops away, and a sky populates behind it."""
        tube = self.tube
        self.play(FadeIn(tube.body), run_time=0.7)

        # ground reference, human-height things implied below
        ground = DashedLine(LEFT * 6.6 + DOWN * 2.6, RIGHT * 6.6 + DOWN * 2.6,
                            dash_length=0.18, dashed_ratio=0.55,
                            color=C_GROUND, stroke_width=2.0, stroke_opacity=0.8)
        self.play(Create(ground), run_time=0.8)
        tube.generate_target()
        tube.target.move_to(DOWN * 1.4)
        self.play(MoveToTarget(tube), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)

        # sharpen the lens curvature: fatter/imprecise -> sharper/precise
        sharp = biconvex(tube.lens.h, bulge=1.55, color=CYAN, width=2.6,
                         fill_op=0.14).move_to(tube.lens.get_center())
        self.play(Transform(tube.lens, sharp), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_sine)

        # magnification readout — ValueTracker + become (no MathTex in the series)
        mag = ValueTracker(1.0)
        pos = tube.get_top() + UP * 0.75
        if self.MAG_COUNT:
            readout = serif("1\u00d7", AMBER, 46, italic=False).move_to(pos)

            def upd(m):
                m.become(serif(f"{int(round(mag.get_value()))}\u00d7", AMBER,
                               46, italic=False).move_to(pos))
            readout.add_updater(upd)
            self.add(readout)
            self.play(mag.animate.set_value(28), run_time=2.0,
                      rate_func=rate_functions.ease_out_cubic)
            readout.clear_updaters()
            band = mono("20 – 30\u00d7 · AN INSTRUMENT NOW", DUST, 12)
            band.next_to(readout, UP, buff=0.28)
            self.play(FadeIn(band), run_time=0.5)
        else:
            readout = serif("much closer", AMBER, 34).move_to(pos)
            band = VGroup()
            self.play(FadeIn(readout, scale=1.3), run_time=1.0)
        self.wait(1.0)

        # the pivot: tilt the tube up about its eyepiece; ground drops; sky fills
        self.play(FadeOut(readout), FadeOut(band), run_time=0.5)
        pivot = tube.get_bottom()
        tube_all = VGroup(tube.body, tube.lens)
        self.play(
            Rotate(tube_all, angle=95 * DEGREES, about_point=pivot),
            ground.animate.set_opacity(0.0).shift(DOWN * 1.2),
            run_time=2.2, rate_func=rate_functions.ease_in_out_sine)

        sky = VGroup()
        for _ in range(90):
            p = np.array([RNG.uniform(-6.8, 6.8), RNG.uniform(-3.6, 3.9), 0])
            if np.linalg.norm(p[:2] - tube_all.get_center()[:2]) < 1.2:
                continue
            r = float(RNG.uniform(0.012, 0.035))
            sky.add(Dot(p, radius=r, color=STARLIGHT,
                        fill_opacity=float(RNG.uniform(0.4, 0.95))))
        sky.set_z_index(1)
        self.play(LaggedStart(*[FadeIn(s, scale=0.5) for s in sky],
                              lag_ratio=0.02, run_time=1.6))
        self.wait(1.2)   # held breath before the payoff

        self._sky = sky
        self._tube_up = tube_all
        # drift the tube to a corner so Act 5 owns the centre
        self.play(tube_all.animate.scale(0.7).to_corner(DL, buff=0.5).set_opacity(0.5),
                  run_time=1.2, rate_func=rate_functions.ease_in_out_sine)

    # ═══════════════════════════════════════════════════════ ACT 5 ═══════
    def act5_first_look_up(self):
        """Four clean unveilings — Moon, Jupiter, Venus — then the Milky Way,
        given the most time and density: a smudge that resolves into hundreds
        of points as the camera pushes in. Slow fade out."""
        # ── 1 · THE MOON ──────────────────────────────────────────────────
        moon = Circle(radius=1.15, stroke_color=STARLIGHT, stroke_width=2.0,
                      fill_color=DUST, fill_opacity=0.14).move_to(ORIGIN)
        mlbl = mono("THE MOON", DUST, 12).next_to(moon, DOWN, buff=0.5)
        self.play(GrowFromCenter(moon), FadeIn(mlbl), run_time=1.0)
        self.wait(0.4)
        craters = VGroup()
        for _ in range(26):
            while True:
                p = np.array([RNG.uniform(-1, 1), RNG.uniform(-1, 1), 0]) * 1.0
                if np.linalg.norm(p) < 0.92:
                    break
            cr = float(RNG.uniform(0.05, 0.17))
            craters.add(Circle(radius=cr, stroke_color=VOID, stroke_width=1.0,
                               fill_color=VOID, fill_opacity=0.55)
                        .move_to(moon.get_center() + p * 1.05))
        craters.set_z_index(4)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in craters],
                              lag_ratio=0.05, run_time=1.4))
        self.wait(0.9)
        self.play(FadeOut(VGroup(moon, craters, mlbl)), run_time=0.8)

        # ── 2 · JUPITER + FOUR MOONS ─────────────────────────────────────
        jup = VGroup(
            Circle(radius=0.5, stroke_color=DUST, stroke_width=2.0,
                   fill_color=C_MASS, fill_opacity=0.20),
            Line(LEFT * 0.42, RIGHT * 0.42, stroke_color=DUST,
                 stroke_width=1.2, stroke_opacity=0.5).shift(UP * 0.12),
            Line(LEFT * 0.46, RIGHT * 0.46, stroke_color=DUST,
                 stroke_width=1.2, stroke_opacity=0.5).shift(DOWN * 0.12),
        ).move_to(ORIGIN)
        jlbl = mono("JUPITER", DUST, 12).next_to(jup, DOWN, buff=1.15)
        self.play(GrowFromCenter(jup), FadeIn(jlbl), run_time=0.9)

        theta = ValueTracker(0.0)
        orbits = [(1.15, 0.34, 0.0, 1.0), (1.65, 0.48, 1.7, 0.78),
                  (2.15, 0.62, 3.1, 0.60), (2.7, 0.78, 4.6, 0.46)]
        jmoons = VGroup()
        for a, b, ph, sp in orbits:
            path = Ellipse(width=2 * a, height=2 * b, stroke_color=DUST,
                           stroke_width=1.0, stroke_opacity=0.22).move_to(jup.get_center())
            jmoons.add(path)
        self.play(LaggedStart(*[Create(p) for p in jmoons],
                              lag_ratio=0.1, run_time=1.0))

        def moon_dot(a, b, ph, sp):
            d = Dot(radius=0.06, color=STARLIGHT)

            def upd(m):
                ang = theta.get_value() * sp + ph
                m.move_to(jup.get_center() + np.array([a * math.cos(ang),
                                                       b * math.sin(ang), 0]))
            d.add_updater(upd)
            return d
        dots = VGroup(*[moon_dot(*o) for o in orbits]).set_z_index(6)
        self.add(dots)
        self.play(FadeIn(dots), run_time=0.5)
        self.play(theta.animate.set_value(TAU * 0.85), run_time=3.4,
                  rate_func=rate_functions.ease_in_out_sine)
        for d in dots:
            d.clear_updaters()
        self.wait(0.6)
        self.play(FadeOut(VGroup(jup, jmoons, dots, jlbl)), run_time=0.8)

        # ── 3 · VENUS · PHASES via arc-masking ───────────────────────────
        R = 1.0
        vc = ORIGIN
        rim = Circle(radius=R, stroke_color=DUST, stroke_width=1.6,
                     fill_color=VOID, fill_opacity=0.0).move_to(vc)
        lit = Circle(radius=R, stroke_width=0, fill_color=STARLIGHT,
                     fill_opacity=0.85).move_to(vc)
        phase_k = ValueTracker(0.98 * R)      # +R full -> 0 half -> -R crescent

        def shadow():
            k = phase_k.get_value()
            pts = []
            for u in np.linspace(math.pi / 2, -math.pi / 2, 46):
                pts.append(vc + np.array([R * math.cos(u), R * math.sin(u), 0]))
            for v in np.linspace(-math.pi / 2, math.pi / 2, 46):
                pts.append(vc + np.array([k * math.cos(v), R * math.sin(v), 0]))
            return Polygon(*pts, stroke_width=0, fill_color=VOID,
                           fill_opacity=1.0).set_z_index(5)
        shade = always_redraw(shadow)
        vlbl = mono("VENUS · PHASES", DUST, 12).next_to(rim, DOWN, buff=0.55)
        self.add(lit, shade, rim)
        rim.set_z_index(6)
        self.play(FadeIn(lit), FadeIn(rim), FadeIn(vlbl), run_time=0.8)
        self.wait(0.3)
        self.play(phase_k.animate.set_value(-0.82 * R), run_time=3.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)
        shade.clear_updaters()
        self.play(FadeOut(VGroup(lit, shade, rim, vlbl)), run_time=0.8)

        # ── 4 · THE MILKY WAY — the peak ─────────────────────────────────
        smudge = VGroup()
        for i in range(9):
            e = Ellipse(width=11.5, height=1.7 - abs(i - 4) * 0.14,
                        stroke_width=0, fill_color=STARLIGHT,
                        fill_opacity=0.05).rotate(self.MW_TILT)
            e.shift(np.array([math.cos(self.MW_TILT), math.sin(self.MW_TILT), 0])
                    * (i - 4) * 0.12)
            smudge.add(e)
        smudge.set_z_index(2)
        mwlbl = mono("A BAND OF HAZE", DUST, 12).to_edge(DOWN, buff=1.1)
        self.play(FadeIn(smudge), FadeIn(mwlbl), run_time=1.2)
        self.wait(1.0)

        # resolve: hundreds of points emerge along the band as the camera pushes
        stars = VGroup()
        axis = np.array([math.cos(self.MW_TILT), math.sin(self.MW_TILT), 0])
        perp = np.array([-math.sin(self.MW_TILT), math.cos(self.MW_TILT), 0])
        for _ in range(360):
            t = RNG.uniform(-5.6, 5.6)
            s = RNG.normal(0, 0.55)
            p = axis * t + perp * s
            r = float(RNG.uniform(0.008, 0.03))
            stars.add(Dot(p, radius=r, color=STARLIGHT,
                          fill_opacity=float(RNG.uniform(0.35, 0.95))))
        stars.set_z_index(3)
        newlbl = mono("\u2014 THOUSANDS OF STARS", STARLIGHT, 12).move_to(mwlbl)

        # optional real long-exposure still, landing exactly as the smudge resolves
        resolve_anims = [
            LaggedStart(*[FadeIn(s, scale=0.4) for s in stars], lag_ratio=0.004),
            smudge.animate.set_opacity(0.0),
            self.camera.frame.animate.scale(0.8),
            ReplacementTransform(mwlbl, newlbl),
        ]
        mw_img = None
        if self.USE_MILKY_IMAGE:
            mw_img = safe_image("milky_way_longexposure.jpg", 13.0,
                                "MILKY WAY · LONG EXPOSURE")
            mw_img.rotate(self.MW_TILT).set_z_index(0)
            resolve_anims.insert(0, FadeIn(mw_img))

        self.play(*resolve_anims, run_time=3.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.6)   # (>>> POST: the musical swell crests here)

        # slow fade — give the awe room before Scene 3
        everything = VGroup(stars, smudge, newlbl, self.frame_marks)
        if hasattr(self, "_sky"):
            everything.add(self._sky)
        if hasattr(self, "_tube_up"):
            everything.add(self._tube_up)
        fade_anims = [FadeOut(everything)]
        if mw_img is not None:
            fade_anims.append(FadeOut(mw_img))
        self.play(*fade_anims, run_time=2.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.5)

    # ── tube builder (spyglass -> instrument) ─────────────────────────────
    def _make_tube(self):
        L, W = self.TUBE_L, self.TUBE_W
        body = Rectangle(width=L, height=W, stroke_color=DUST,
                         stroke_width=2.4, fill_color=PANEL, fill_opacity=0.35)
        eyepiece = Rectangle(width=0.7, height=W * 0.72, stroke_color=DUST,
                             stroke_width=2.2, fill_color=PANEL, fill_opacity=0.35)
        eyepiece.move_to(body.get_left() + LEFT * 0.28)
        lens = biconvex(W * 0.88, bulge=1.15, color=CYAN, width=2.4,
                        fill_op=0.12).move_to(body.get_center() + LEFT * L * 0.28)
        g = VGroup()
        g.body = VGroup(body, eyepiece)
        g.lens = lens
        g.add(g.body, g.lens)
        return g

    # ── Act-2 tile builders (identical to Scene 1's closing asset) ────────
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

    def _tile_mag(self):
        f = self._tile_frame()
        c = f.get_center()
        glass = biconvex(1.0, bulge=1.2, color=CYAN, width=2.0,
                         fill_op=0.12).move_to(c)
        plus = VGroup(
            Line(c + LEFT * 0.18, c + RIGHT * 0.18, stroke_color=AMBER, stroke_width=2.2),
            Line(c + DOWN * 0.18, c + UP * 0.18, stroke_color=AMBER, stroke_width=2.2))
        return VGroup(f, glass, plus)