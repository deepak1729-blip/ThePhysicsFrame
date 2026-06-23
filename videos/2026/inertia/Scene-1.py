from manim import *
import numpy as np

# ─────────────────────────────────────────────────────────────────────────
#  OBSERVATORY PALETTE  (supersedes the old series canvas; verbatim hexes)
# ─────────────────────────────────────────────────────────────────────────
VOID       = "#0A0C10"   # base background
PANEL      = "#11151C"   # lifted surfaces
STARLIGHT  = "#E8E6DF"   # primary text / objects
DUST       = "#9A958C"   # secondary · metadata · the "dimmed" state
AMBER      = "#D98A3D"   # primary accent · focus (amber follows the eye)
CYAN       = "#5B8FB0"   # secondary · sparing

# quantity pigments
C_MASS     = "#B89A86"   # the box is matter -> mass pigment
C_GROUND   = "#7F8A99"   # ground / reference axis (the dashed floor)
C_VELOCITY = "#57C08A"   # reserved; one quiet cameo only

# typography
SERIF = "Spectral"       # ideas; italic is the channel's speaking voice
MONO  = "Space Mono"     # labels & metadata only

config.background_color = VOID
RNG = np.random.default_rng(11)   # deterministic -> stable render cache


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS — construction vocabulary carried over from the series
# ═══════════════════════════════════════════════════════════════════════════
def make_box(w=1.05, h=0.72):
    """Aristotle's object: a rounded block, rendered in the mass pigment.
    Translucent fill + solid stroke matches the design-system block-on-incline."""
    g = VGroup()
    body = RoundedRectangle(width=w, height=h, corner_radius=0.08,
                            stroke_color=C_MASS, stroke_width=2.2,
                            fill_color=C_MASS, fill_opacity=0.22)
    g.add(body)
    # a single quiet sheen line so the block reads as a solid, not an outline
    sheen = Line(body.get_corner(UL) + RIGHT * 0.12 + DOWN * 0.10,
                 body.get_corner(UR) + LEFT * 0.12 + DOWN * 0.10,
                 stroke_color=STARLIGHT, stroke_width=1.4, stroke_opacity=0.10)
    g.add(sheen)
    g.body = body
    return g


def check_mark(color=AMBER, scale=0.9):
    """The series' satisfying tick of certainty."""
    m = VMobject(stroke_color=color, stroke_width=5)
    m.set_points_as_corners([LEFT * 0.18 + DOWN * 0.02, DOWN * 0.20,
                             RIGHT * 0.30 + UP * 0.26])
    return m.scale(scale)


def corner_L(orientation, size=0.20, color=AMBER, width=1.4, opacity=0.7):
    """Registration corner — the Observatory mark that frames the animation.
    `orientation` is one of UL, UR, DL, DR."""
    sx = -1 if orientation[0] > 0 else 1          # horizontal arm direction
    sy = -1 if orientation[1] > 0 else 1          # vertical arm direction
    h = Line(ORIGIN, RIGHT * size * sx, stroke_color=color,
             stroke_width=width, stroke_opacity=opacity)
    v = Line(ORIGIN, UP * size * sy, stroke_color=color,
             stroke_width=width, stroke_opacity=opacity)
    g = VGroup(h, v)
    g.anchor = orientation          # which bbox corner pins to the frame
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


# ═══════════════════════════════════════════════════════════════════════════
class Scene1_FlipTheQuestion(MovingCameraScene):

    # ── locked geometry (every act reads from these) ──
    FLOOR_Y   = -2.30
    BOX_W     = 1.05
    BOX_H     = 0.72
    COAST_X0  = -3.60          # where the box leaves the pusher's hand
    COAST_XF  =  3.55          # where friction kills it
    REST_X    = -4.55          # box's pre-push resting spot
    N_GHOST   = 7              # strobe samples (equal TIME steps)

    def construct(self):
        self.camera.frame.save_state()

        # The series-wide ground anchor: a dashed reference line, lower third.
        floor = DashedLine(
            LEFT * 6.6 + UP * self.FLOOR_Y, RIGHT * 6.6 + UP * self.FLOOR_Y,
            dash_length=0.18, dashed_ratio=0.55,
            color=C_GROUND, stroke_width=2.0, stroke_opacity=0.85,
        )
        self.floor = floor

        # Observatory frame marks — pinned to the camera frame via updater so
        # they survive every zoom/pan. Quiet identity, never decorative.
        self.frame_marks = self._build_frame_marks()
        self._pin_frame_marks()

        # >>> POST: open on black; the soft floor-draw is the first sound cue.
        self.wait(0.5)
        self.play(Create(floor), run_time=1.1,
                  rate_func=rate_functions.ease_in_out_sine)
        self.add(self.frame_marks)
        self.play(self.frame_marks.animate.set_opacity(0.55), run_time=0.8)

        self.act1_push_and_stop()
        self.act2_obvious_answer()
        self.act3_flip_the_question()
        self.act4_two_destinations()       # <- delete this line for the lean cut
        self.act5_hidden_thing()

    # ── frame-mark plumbing ────────────────────────────────────────────────
    def _build_frame_marks(self):
        marks = VGroup(*[corner_L(o, opacity=0.0) for o in (UL, UR, DL, DR)])
        return marks

    def _pin_frame_marks(self):
        inset = 0.34

        def updater(grp):
            f = self.camera.frame
            for c in grp:
                o = c.anchor
                target = f.get_corner(o) - o * inset
                c.move_to(target, aligned_edge=o)
        self.frame_marks.add_updater(updater)

    # ===================================================================== A1
    def act1_push_and_stop(self):
        box = make_box(self.BOX_W, self.BOX_H)
        box.move_to(RIGHT * self.REST_X + UP * (self.FLOOR_Y + self.BOX_H / 2))
        box.set_z_index(5)
        self.box = box
        self.play(FadeIn(box, shift=UP * 0.10, scale=0.9), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        # The pusher: a clean minimal hand glyph — a short capped rod + knuckle.
        pusher = self._make_pusher()
        contact_x = self.REST_X - self.BOX_W / 2
        pusher.next_to(box.body, LEFT, buff=0.02)
        pusher.shift(LEFT * 3.2)                       # start off-frame left
        pusher.set_z_index(6)
        self.add(pusher)

        # slide in to contact
        self.play(pusher.animate.shift(RIGHT * 3.2), run_time=0.9,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.15)

        y = self.FLOOR_Y + self.BOX_H / 2
        span = self.COAST_XF - self.COAST_X0
        coast_path = Line(RIGHT * self.COAST_X0 + UP * y,
                          RIGHT * self.COAST_XF + UP * y)

        # 1) the impulse: box + hand accelerate together to the release point
        shove = self.COAST_X0 - self.REST_X
        self.play(
            box.animate.shift(RIGHT * shove),
            pusher.animate.shift(RIGHT * shove),
            run_time=0.32, rate_func=rate_functions.ease_in_quad,
        )

        # 2) hand peels away WHILE the box keeps moving — continuous coast.
        #    Constant-friction stop is exactly s(t)=2t-t^2, so ease_out_quad
        #    on a straight path IS the physics. Drag-marks ride the same clock.
        coast_t = 2.4
        self.play(
            MoveAlongPath(box, coast_path,
                          rate_func=rate_functions.ease_out_quad),
            pusher.animate.shift(LEFT * 4.6),
            run_time=coast_t,
        )
        self.remove(pusher)

        # rest on the dead-still box for a beat (no camera push-in / zoom).
        self.wait(1.0)

    def _make_pusher(self):
        """Minimal hand glyph: a forearm rod ending in a soft knuckle pad."""
        g = VGroup()
        arm = RoundedRectangle(width=1.4, height=0.20, corner_radius=0.10,
                               stroke_width=0, fill_color=DUST, fill_opacity=0.9)
        knuckle = RoundedRectangle(width=0.26, height=0.46, corner_radius=0.12,
                                   stroke_width=0, fill_color=STARLIGHT,
                                   fill_opacity=0.92)
        knuckle.next_to(arm, RIGHT, buff=-0.02)
        g.add(arm, knuckle)
        return g

    # ===================================================================== A2
    def act2_obvious_answer(self):
        # The question types in — Spectral, large, lots of air, upper third.
        q = Text("Why did the box stop?", font=SERIF, font_size=46,
                 color=STARLIGHT)
        q.move_to(UP * 2.05).set_z_index(10)
        self.play(Write(q), run_time=1.1)
        self.wait(0.5)

        # The confident answer slots in beneath and lands with a tick.
        ans = Text("The push ended, so it stopped.", font=SERIF,
                   slant=ITALIC, font_size=30, color=DUST)
        ans.next_to(q, DOWN, buff=0.42).set_z_index(10)
        self.play(FadeIn(ans, shift=UP * 0.12), run_time=0.7,
                  rate_func=rate_functions.ease_out_cubic)
        tick = check_mark(AMBER, 0.85).next_to(ans, RIGHT, buff=0.28)
        tick.set_z_index(10)
        self.play(Create(tick), run_time=0.45,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.7)

        self.q_act2 = VGroup(q, ans, tick)

        # The weight of history: pull the answer onto a long timeline.
        self.play(
            self.q_act2.animate.scale(0.62).to_edge(UP, buff=0.55),
            FadeOut(self.box, scale=0.9),
            run_time=1.0, rate_func=rate_functions.ease_in_out_cubic,
        )

        timeline = Line(LEFT * 5.6 + DOWN * 0.4, RIGHT * 9.0 + DOWN * 0.4,
                        color=DUST, stroke_width=1.6, stroke_opacity=0.5)
        marker = Line(UP * 0.16, DOWN * 0.16, color=AMBER, stroke_width=2.5)
        marker.move_to(timeline.get_start())
        m_lab = Text("ARISTOTLE  ·  ~350 BC", font=MONO, font_size=15,
                     color=DUST)
        m_lab.next_to(marker, DOWN, buff=0.22).align_to(marker, LEFT)
        self.play(
            Create(timeline), Create(marker),
            FadeIn(m_lab, shift=UP * 0.08),
            run_time=1.0, rate_func=rate_functions.ease_in_out_sine,
        )

        # Faint century ticks sweep past -> two millennia, unchallenged.
        # >>> POST: a quiet "tick... tick..." rides under this sweep.
        centuries = VGroup()
        for i in range(1, 21):
            x = -5.6 + i * 0.72
            ct = Line(UP * 0.07, DOWN * 0.07, color=DUST, stroke_width=1.2,
                      stroke_opacity=0.28)
            ct.move_to(RIGHT * x + DOWN * 0.4)
            centuries.add(ct)
        self.play(LaggedStart(*[FadeIn(c) for c in centuries], lag_ratio=0.06),
                  run_time=2.0)

        # The answer rides along with a faint "approved" glow, never questioned.
        # Build the frame first, then hang the label clearly BELOW it so the
        # word never collides with the rectangle's stroke.
        glow = SurroundingRectangle(self.q_act2, color=AMBER, buff=0.22)
        glow.set_stroke(width=1.2, opacity=0.0).set_fill(AMBER, opacity=0.0)
        approve = Text("APPROVED", font=MONO, font_size=14, color=AMBER)
        approve.next_to(glow, DOWN, buff=0.16)
        self.add(glow)
        self.play(
            glow.animate.set_stroke(opacity=0.35).set_fill(opacity=0.05),
            FadeIn(approve, shift=UP * 0.06),
            run_time=0.8, rate_func=rate_functions.ease_out_cubic,
        )

        # The single well-earned overlay: one historical face beside the marker.
        # (search: "Aristotle bust marble" / "Aristotle engraving public domain")
        bust = safe_image("aristotle.jpg", 1.7, "ARISTOTLE")
        bust.next_to(marker, UP, buff=0.30).shift(RIGHT * 0.1)
        bust.set_z_index(11)
        self.play(FadeIn(bust, shift=UP * 0.10), run_time=0.9,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(1.0)
        self.play(FadeOut(bust, shift=UP * 0.10), run_time=0.7)

        self.timeline_grp = VGroup(timeline, marker, m_lab, centuries,
                                   approve, glow)
        self.wait(0.4)

    # ===================================================================== A3
    def act3_flip_the_question(self):
        # Clear the timeline; bring the two questions to center stage.
        self.play(
            FadeOut(self.timeline_grp, shift=DOWN * 0.2),
            FadeOut(self.q_act2, shift=DOWN * 0.2),
            run_time=0.9, rate_func=rate_functions.ease_in_out_cubic,
        )

        C = UP * 0.4                 # the line's vertical anchor
        FS = 52

        # The whole question is ONE Text line so Manim lays every word on a
        # single TRUE baseline. The old approach aligned each word by its
        # bounding-box bottom, which floats up whenever a word has a descender
        # (the "y" in "Why", the "p" in "kept") — that was the up/down jitter.
        # Here we colour/weight/slant the runs with t2c/t2w/t2s and slice out
        # sub-words by index, so the anchor "box" and the emphasis word can
        # still be addressed individually for the flip.
        def build_line(lead, emph, emph_color):
            """lead + ' box ' + emph as one baseline-aligned Text line.
            Returns (line, lead_grp, box_grp, emph_grp)."""
            full = f"{lead} box {emph}"
            t = Text(
                full, font=SERIF, font_size=FS, color=STARLIGHT,
                t2c={"box": C_MASS, emph: emph_color},
                t2w={emph: BOLD},
                t2s={"box": ITALIC},
            ).set_z_index(10)

            # Text[i] indexes GLYPHS, which skip spaces — so string positions
            # don't equal glyph positions. Map each non-space char to its glyph
            # index so the sub-word slices land on the right letters.
            glyph_at = [i for i, ch in enumerate(full) if not ch.isspace()]
            def slc(start, length):                  # glyph slice for full[start:start+length]
                first = glyph_at.index(start)
                return t[first:first + length]

            lead_grp = slc(0, len(lead.replace(" ", "")))
            box_grp  = slc(full.index(" box ") + 1, 3)
            emph_grp = slc(full.index(emph), len(emph))
            # pin the anchor word "box" onto C, identically for old and new
            t.shift(C - box_grp.get_center())
            return t, lead_grp, box_grp, emph_grp

        old_line, old_lead, old_box, old_emph = build_line(
            "Why did the", "STOP?", DUST)

        self.play(Write(old_line), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)
        self.wait(0.8)

        # ── THE FLIP ── physical, not a cut. box holds; the rest turns over. ──
        new_line, new_lead, new_box, new_emph = build_line(
            "What kept the", "MOVING?", AMBER)
        # "box" is identical in both lines and pinned to C, so the new line is
        # already perfectly registered on the same baseline and anchor.

        # >>> POST: one clean whoosh here, then DROP the drone for the hold.
        # The lead phrase morphs in place; the camera does a subtle perspective
        # turn-over. The anchor "box" swaps silently (the two are identical).
        self.play(
            TransformMatchingShapes(old_lead, new_lead),
            FadeIn(new_box, run_time=0.01),
            FadeOut(old_box, run_time=0.01),
            self.camera.frame.animate.rotate(4 * DEGREES),
            run_time=0.7, rate_func=rate_functions.ease_in_out_sine,
        )

        # The emphasis word card-flips around its OWN left edge (the edge that
        # sits next to "box"), so the wider new word opens rightward and never
        # grows back over the anchor. A pure X-scale about a fixed pivot reads
        # as a clean flip — no stretch_to_fit smearing, no centre jump.
        pivot = old_emph.get_left()
        new_emph.set_opacity(0.0)
        new_emph.scale([0.001, 1, 1], about_point=new_emph.get_left())

        # collapse the old face to its left edge…
        self.play(
            old_emph.animate.scale([0.001, 1, 1], about_point=pivot)
                    .set_opacity(0.0),
            run_time=0.24, rate_func=rate_functions.ease_in_sine,
        )
        self.remove(old_emph)
        self.add(new_emph)
        # …and open the new face from that same edge.
        self.play(
            new_emph.animate.scale([1000, 1, 1], about_point=new_emph.get_left())
                    .set_opacity(1.0),
            self.camera.frame.animate.rotate(-4 * DEGREES),
            run_time=0.32, rate_func=rate_functions.ease_out_sine,
        )

        self.remove(old_line)
        self.question = VGroup(new_lead, new_box, new_emph)

        # Lift the reframed question and hold it — this is the frame the scene
        # exists for.
        self.play(
            self.question.animate.scale(0.82).to_edge(UP, buff=0.7),
            run_time=0.9, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(2.5)
        self.spot_done = True

    # ===================================================================== A4
    def act4_two_destinations(self):
        """Cuttable. Two ghosted teaser windows fork off the reframed question.
        Both are deliberate callback objects for Scenes 5-6 and Scene 7."""
        self.wait(0.3)

        # ── Destination 1 — moment of inertia (honest wobble) ──────────────
        card1 = self._teaser_card().move_to(LEFT * 3.4 + DOWN * 0.4)
        card2 = self._teaser_card().move_to(RIGHT * 3.4 + DOWN * 0.4)
        self.play(LaggedStart(FadeIn(card1, scale=0.95),
                              FadeIn(card2, scale=0.95), lag_ratio=0.2),
                  run_time=0.9, rate_func=rate_functions.ease_out_cubic)

        rod_center = self._rod(spread=0.32).move_to(card1.get_center() + UP * 0.55)
        rod_ends   = self._rod(spread=0.95).move_to(card1.get_center() + UP * 0.55)
        rod_ends.set_opacity(0)
        for r in (rod_center, rod_ends):
            r.set_z_index(6)
        lab1 = Text("Same mass.  Harder to turn.", font=MONO, font_size=14,
                    color=DUST).move_to(card1.get_center() + DOWN * 0.95)
        lab1.set_z_index(6)
        self.add(rod_center, rod_ends)
        self.play(FadeIn(lab1, shift=UP * 0.06), run_time=0.5)

        # A/B: same total mass, blobs near centre vs at the ends.
        # period ~ sqrt(I), I ~ m r^2 -> ends config rocks SLOWER & shorter.
        self.play(Rotate(rod_center, 28 * DEGREES, rate_func=there_and_back),
                  run_time=0.9)
        self.play(Rotate(rod_center, -28 * DEGREES, rate_func=there_and_back),
                  run_time=0.9)
        self.play(rod_center.animate.set_opacity(0.0),
                  rod_ends.animate.set_opacity(1.0), run_time=0.5)
        # the ends config "fights back": smaller amplitude, longer period
        self.play(Rotate(rod_ends, 16 * DEGREES, rate_func=there_and_back),
                  run_time=1.6)

        # ── Destination 2 — rest vs constant motion are the SAME ───────────
        still = self._mini_figure(moving=False).move_to(card2.get_center() + LEFT * 0.85 + UP * 0.5)
        glide = self._mini_figure(moving=True).move_to(card2.get_center() + RIGHT * 0.85 + UP * 0.5)
        eq = Text("=", font=SERIF, font_size=54, color=AMBER)
        eq.move_to(card2.get_center() + UP * 0.5)
        for m in (still, glide, eq):
            m.set_z_index(6)
        lab2 = Text("The biggest twist.", font=MONO, font_size=14,
                    color=DUST).move_to(card2.get_center() + DOWN * 0.95)
        lab2.set_z_index(6)
        self.play(LaggedStart(FadeIn(still), FadeIn(glide), lag_ratio=0.2),
                  FadeIn(lab2, shift=UP * 0.06), run_time=0.7)
        self.play(FadeIn(eq, scale=0.6), run_time=0.4)
        self.play(eq.animate.scale(1.18).set_opacity(1.0),
                  rate_func=there_and_back, run_time=0.7)
        self.play(eq.animate.scale(1.18).set_opacity(1.0),
                  rate_func=there_and_back, run_time=0.7)

        self.wait(0.8)
        self.previews = Group(card1, card2, rod_center, rod_ends, lab1,
                              still, glide, eq, lab2)
        self.play(FadeOut(self.previews, shift=DOWN * 0.15), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_cubic)

    def _teaser_card(self):
        c = RoundedRectangle(width=4.6, height=2.9, corner_radius=0.16,
                             stroke_color=DUST, stroke_width=1.2,
                             stroke_opacity=0.35, fill_color=PANEL,
                             fill_opacity=0.55)        # ghosted, "you'll get here"
        c.set_z_index(1)
        return c

    def _rod(self, spread):
        g = VGroup()
        bar = Line(LEFT * 0.9, RIGHT * 0.9, color=DUST, stroke_width=3)
        b1 = Dot(radius=0.13, color=C_MASS).move_to(LEFT * spread)
        b2 = Dot(radius=0.13, color=C_MASS).move_to(RIGHT * spread)
        pivot = Dot(radius=0.04, color=AMBER)
        g.add(bar, b1, b2, pivot)
        return g

    def _mini_figure(self, moving):
        g = VGroup()
        body = RoundedRectangle(width=0.42, height=0.5, corner_radius=0.1,
                                stroke_color=STARLIGHT, stroke_width=1.6,
                                fill_color=PANEL, fill_opacity=0.8)
        g.add(body)
        if moving:
            for i, op in enumerate((0.5, 0.3, 0.15)):
                d = Line(ORIGIN, RIGHT * 0.14, stroke_color=C_VELOCITY,
                         stroke_width=2.4, stroke_opacity=op)
                d.next_to(body, LEFT, buff=0.08 + i * 0.18)
                g.add(d)
        return g

    # ===================================================================== A5
    def act5_hidden_thing(self):
        # Bring the box back to center, alone on its dashed line.
        y = self.FLOOR_Y + self.BOX_H / 2
        self.box.move_to(UP * y)            # reuse the same object
        self.box[0].set_stroke(C_MASS, opacity=1.0)
        self.box[0].set_fill(C_MASS, opacity=0.22)
        self.box[1].set_opacity(0.10)
        self.play(
            FadeIn(self.box, scale=0.95),
            run_time=0.9, rate_func=rate_functions.ease_in_out_cubic,
        )
        self.wait(0.4)

        # A property living INSIDE the matter — unnamed. A breathing "?".
        glow = Circle(radius=0.42, stroke_width=0, fill_color=AMBER,
                      fill_opacity=0.0).move_to(self.box.get_center())
        glow.set_z_index(4)
        q = Text("?", font=SERIF, font_size=40, color=AMBER, weight=BOLD)
        q.move_to(self.box.get_center()).set_z_index(6).set_opacity(0)
        self.add(glow, q)
        self.play(glow.animate.set_fill(opacity=0.30),
                  q.animate.set_opacity(0.95),
                  run_time=0.8, rate_func=rate_functions.ease_out_cubic)
        # the breath
        for _ in range(2):
            self.play(glow.animate.scale(1.25).set_fill(opacity=0.18),
                      run_time=0.9, rate_func=there_and_back)
        self.wait(0.6)

        # "Let's begin." One hard pulse, then condense to a single point of light.
        # >>> POST: the score finally opens up here.
        point = Dot(radius=0.06, color=AMBER).move_to(self.box.get_center())
        point.set_z_index(7).set_opacity(0)
        self.add(point)
        self.play(
            glow.animate.scale(2.4).set_fill(opacity=0.5),
            run_time=0.45, rate_func=rate_functions.ease_out_quad,
        )
        self.play(
            glow.animate.scale(0.04).set_fill(opacity=1.0),
            q.animate.set_opacity(0.0).scale(0.2),
            FadeOut(self.box, scale=0.7),
            point.animate.set_opacity(1.0),
            FadeOut(self.floor),
            run_time=0.6, rate_func=rate_functions.ease_in_cubic,
        )
        self.play(point.animate.scale(0.1).set_opacity(0.0), run_time=0.4)
        self.remove(glow, q, point)

        # Chapter title card. Clear the lingering top-of-frame question and the
        # Observatory marks so the intro opens on a clean field (no orbits).
        intro_clear = [self.frame_marks.animate.set_opacity(0.0)]
        if getattr(self, "question", None) is not None:
            intro_clear.append(FadeOut(self.question, shift=UP * 0.10))
        self.play(*intro_clear, run_time=0.5)
        self.frame_marks.clear_updaters()
        self.remove(self.frame_marks) 
        kicker = Text("THE PHYSICS FRAME  ·  INERTIA", font=MONO,
                      font_size=15, color=DUST)
        kicker.move_to(DOWN * 1.4)
        rule = Line(LEFT * 0.5, RIGHT * 0.5, color=AMBER, stroke_width=1.4)
        rule.next_to(kicker, UP, buff=0.45)
        title = Text("What kept it moving?", font=SERIF, slant=ITALIC,
                     weight=LIGHT, font_size=44, color=STARLIGHT)
        title.next_to(rule, UP, buff=0.45)

        self.play(
            FadeIn(title, shift=UP * 0.10), Create(rule),
            FadeIn(kicker, shift=UP * 0.06),
            run_time=1.0, rate_func=rate_functions.ease_out_cubic,
        )
        self.wait(1.6)