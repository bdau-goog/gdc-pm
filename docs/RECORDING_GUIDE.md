# GDC Demo — Screen Recording Guide (MacBook + Vids/YouTube)
**Purpose:** Produce a crisp, laptop-legible, 16:9, YouTube/brand-safe screen capture of the GDC UI for the Veo-narrated videos (V3 / V4 scripts).
**Key finding:** No CSS change is required. The app is a `100vh`-locked, viewport-fluid "kiosk" layout — it fills whatever **window** size you give it. On a Retina MacBook, recording a small CSS-pixel window and exporting at high resolution yields *supersampled, sharper-than-native* output.

---

## TL;DR — the recommended method (free, no tools)
1. **Record the GDC app full-screen** as normal (QuickTime or Vids → Insert → Recording → Screen). It captures 16:10 — fine.
2. **In Google Vids, crop the clip to 16:9 once** (drag top/bottom edges in). Reuse that framing for every clip. *(Full section: "⭐⭐ DO THIS" below.)*
3. **Export 1440p, Rec.709/sRGB** for crisp text and correct color on non-Apple screens.
4. **Lean on the in-script post-zoom** (V3/V4 "🖱️ Screen Choreography": 1.15–1.2× crop-zoom + dwell on key panels) — this is what makes the numbers readable on a laptop/phone.

> Everything below (window-1280×720, DevTools, BetterDisplay/SwitchResX) is **optional/advanced** — only if you want a pixel-exact or no-crop source. The crop-in-Vids method above is the simplest and is recommended.


---

## WHY (the reasoning, so you can adapt it)
- **Layout is fluid, not scrollable.** `html,body{height:100%;overflow:hidden}`, `.app-body{height:calc(100vh-48px);overflow:hidden}`, inner panels `flex:1;min-height:0;overflow:hidden`. ⇒ The UI always fits the window box; size the **window** to control the frame.
- **`cmd +/–` won't scale the body.** Because the body is pinned to `100vh` and Plotly charts are sized in JS pixels to their container, browser zoom mostly enlarges non-height-constrained header text and the panels just re-pack. This is inherent to the kiosk layout — **don't rely on browser zoom for recording.** Use window size + post-zoom instead.
- **Retina is an advantage.** DPR 2 means a 1280×720 CSS window = 2560×1440 captured pixels. Exporting 1080p/1440p from that is supersampled ⇒ crisper than a native-1080p monitor capture.
- **Small CSS viewport = bigger relative text.** Base font is a fixed `14px`. A 1280-wide viewport makes `14px` a larger fraction of the frame than a 1920-wide viewport ⇒ more legible for laptop/phone viewers.

---

## "CAN I MAKE THE MACBOOK DISPLAY 16:9?" — Yes, via a helper app (recommended); or work around it
- **Built-in System Settings: No.** The panel is **~16:10** (≈1.54:1); the Scaled presets only change logical resolution and **keep 16:10**. macOS exposes no native 16:9 mode for the internal display.
- ✅ **With a helper app: Yes (recommended for full-screen recording).** **BetterDisplay** (free) or SwitchResX (paid) add a **1920×1080** mode. You get thin **static black bars** top/bottom (aspect-correct, no stretch), the GDC app renders true 16:9, and you record **full-screen** — then trim the bars once in Vids. *(See the ⭐⭐ BEST section above.)*
- **Or work around it (no install):** get 16:9 from the **capture region** instead of the panel — record a 16:9 window/region (methods below). Trade-off: you record a window, not the full screen.


---

## ⭐⭐ DO THIS — record full-screen, crop to 16:9 in Vids (free, no tools)
**This is the recommended method. No app installs, no paid utilities, no window juggling, no display-resolution hacks.** It takes one crop, once.

1. Leave the display on **Default**. Install nothing.
2. Open the GDC app in Chrome and **record full-screen** as normal — QuickTime (*New Screen Recording*) or **Vids → Insert → Recording → Screen**. It captures 16:10; that's fine.
3. In **Google Vids**, drop the clip on a slide (slides are already 16:9). Select it and **drag the top/bottom edges inward (or use Crop)** until it's 16:9. Do this **once**; reuse the same framing for every clip.

**Why this is #1:** it sidesteps every snag (full-screen window lock, DevTools fiddliness, BetterDisplay's hidden/Pro-gated resolution list). The crop is trivial and free; making the whole Mac 16:9 only saves that one crop and keeps costing time/money. Not worth it.

> **Tip:** when you record full-screen on the 16:10 panel, the app stretches tall and shows vertical gaps in cards. That's expected — the Vids crop trims the excess top/bottom, which also removes those gaps. Frame the crop so the header (tabs) and footer (Run/Back) are inside the 16:9 box.

---

## (ADVANCED / OPTIONAL) Make the whole Mac render 16:9 — only if you insist on no-crop full-screen
The panel is hardware 16:10, so this needs a helper app and you may hit a paywall — **not recommended given the free crop method above.**
- **BetterDisplay:** resolution control for the *built-in* display is via its **menu-bar icon → select the display → resolution**, and adding a forced **1920×1080** mode can require **Pro (paid)**. (It is NOT under Settings → Built-in Display → Additional settings in current versions — that panel has no resolution list, which is the confusion.)
- **SwitchResX (paid):** can add a custom 1080p timing, but it's overkill here.
- Either way you'd then get **static black bars** top/bottom (aspect-correct) and still trim them once in Vids — i.e., the same crop you'd do for free anyway.

---

## ⭐ ALTERNATIVE — exact 16:9 source via a recorder/DevTools (only if you want pixel-exact framing)

**DevTools is only a ruler.** Use it once to confirm the app looks right at 16:9 (it does — verified at 1280×720), then **close it**. You do NOT record inside DevTools (it has its own toolbar and Vids can't cleanly grab the sub-rectangle).


**Recommended end-to-end:**
1. **Close DevTools** (`⌘⌥I`). Done with it.
2. **Drag the normal Chrome window landscape** — wider than tall, roughly 16:9. The app reflows to the exact clean view you saw in DevTools (tight cards, no gaps).
3. **Capture**, either:
   - **Record-then-import (most reliable):** QuickTime / Screen Studio → record the Chrome window → save `.mov` → in **Google Vids → Insert → Video → Upload** onto a 16:9 slide.
   - **Record inside Vids:** Vids **Insert → Recording** → choose **"Chrome Tab"** → pick the GDC tab.
4. **Fit to the slide:** Vids slides are already 16:9 — drag the clip's corners so the app fills the slide; the thin browser strip (tabs/address bar) crops off the edge.

> **Mental model:** DevTools = the ruler (confirm 16:9, then put away). Vids = where the finished clip lives (feed it a recording or a live tab, then size it to fill the 16:9 slide).

---

## ⚠️ "THE WINDOW ISN'T RESIZEABLE / THERE ARE BIG VERTICAL GAPS" — root cause + fix

Two things are happening, and **one action fixes both**:
1. **"Not resizeable" = Chrome is in macOS full-screen mode.** Full-screen *locks* the window to the 16:10 panel. **Fix: exit full-screen** — press **⌃⌘F** (Control-Command-F) or hover the green ● → "Exit Full Screen." Now the window drag-resizes normally.
2. **The big vertical voids in the cards** (e.g., the gap between "DOCUMENTED CONTEXT" and "GDC RESOLUTION" on the Discern Slide 5) appear **because the 16:10 screen is too tall.** The app is `100vh`-locked, so it stretches each card to fill the height and pushes content apart.

**The same move fixes both: render at 16:9.** A shorter (16:9) viewport removes the excess height → the cards tighten and the gaps largely close → AND you get the correct YouTube aspect ratio. **This app is designed to be recorded at 16:9, not on the full 16:10 panel.**

➡️ **Do this:** (1) exit full-screen (**⌃⌘F**); (2) **⌘⌥I** to open DevTools, **⌘⇧M** to toggle the device toolbar, set **Responsive → 1280 × 720** — the page reflows to 16:9 and the gaps shrink before your eyes; (3) record just that 1280×720 box (it's 2560×1440 on Retina → sharp at 1440p/1080p). *(Or, instead of DevTools, just drag the now-windowed Chrome wider-than-tall toward 16:9 — same reflow, less exact.)*

---

## "HOW DO I RECORD A 16:9 WINDOW AND NOT FULL SCREEN?" — plain-language
**Key idea:** You do NOT hand-resize a macOS window to a perfect 16:9 shape. You let the **recording tool** define the 16:9 frame. "Window" = *the rectangle the recorder captures*, not a window you drag to size. Pick ONE method:


**Method 1 — Easiest (record full screen, crop later):**
1. Record the whole screen normally (QuickTime → New Screen Recording, or the Vids recorder).
2. In your editor, set the project to **16:9 (1920×1080)** and nudge the recording so the GDC app fills the frame. The menu bar / dock strip falls outside the 16:9 frame.
   - ✅ No setup before recording. ➖ You crop afterward instead of seeing the exact frame live.

**Method 2 — Cleanest (a recorder with a fixed 16:9 canvas):**
- **OBS (free):** Settings → Video → **Base Canvas = 1920×1080**. Add a **Window Capture** of Chrome, drag its handles so the app fills the 1080 frame. OBS *is* the 16:9 frame; the rest of your 16:10 screen is ignored.
- **Screen Studio (Mac, paid, easiest polish):** choose **16:9** aspect at start, select the area — it locks 16:9 and can auto-do the script's zoom-ins.

**Method 3 — Most precise (force the page itself to 16:9):**
1. Chrome → open the app → **⌘⌥I** (DevTools) → **⌘⇧M** (device/Responsive toolbar).
2. In the "Dimensions: Responsive" bar, type **1280 × 720**. The page now renders as an exact 16:9 box.
3. Record just that box (QuickTime "Record Selection," or an OBS Window Capture).

> **Recommendation:** Method 1 for zero fuss, or Screen Studio (Method 2) for a polished result with the script's zoom moves built in.

---

## STEP-BY-STEP (Retina MacBook)

### A. Display


1. System Settings → **Displays** → Scaled. **Default** is fine. If you want larger UI text, pick **one notch toward "Larger Text."** (Don't go to "More Space" — that shrinks the UI.)
2. Turn on **Do Not Disturb** (hide notifications). Hide the **Dock** (auto-hide) and, if recording full screen, the menu bar.

### B. Browser (Chrome)
1. Use a **clean profile** (no extension toolbar, no bookmarks bar: `⌘⇧B` to hide).
2. Open the app; navigate to the tab you'll start on.
3. Size the window to **16:9 at 1280×720 CSS px.** Two reliable ways:
   - **Exact (recommended):** open DevTools → **Device Toolbar** (`⌘⇧M`) → **Responsive** → type **1280 × 720**, DPR **2**. This guarantees an exact 16:9 CSS viewport. Record the rendered area only.
   - **Manual:** resize the window to roughly 16:9 and let your capture tool crop to a 16:9 region (see C).
4. Confirm no scrollbars appear and the UI fills the frame (it should — it's `100vh`-locked).

### C. Capture tool
- **Screen Studio or OBS (recommended):** set a **1920×1080 or 2560×1440 canvas**, capture the 16:9 window/region. These let you set an exact crop and add the **post-zoom** moves the scripts call for.
- **QuickTime (simplest):** *Record Selection* → drag a 16:9 region over the app window. Records at native Retina res; do the crop/zoom in your editor afterward.
- **Cursor:** hide it except when you intentionally gesture; Screen Studio can auto-highlight clicks/zoom — use sparingly and only on the script's marked gestures.

### D. Export
- **Resolution:** export **1440p** (2560×1440) if your tool allows, else clean **1080p**. Upload the highest you have — YouTube assigns better bitrate to 1440p, improving 1080p playback too.
- **Frame rate:** 30 fps is plenty (UI + slow scrubs). 60 fps only if you want ultra-smooth Vizier animation.
- **Color:** export **Rec.709 / sRGB**. If QuickTime tagged it Display-P3, convert on export so it doesn't look oversaturated on non-Apple screens.
- **Bitrate:** ≥ 16 Mbps (1080p) / ≥ 24 Mbps (1440p) for clean text.

---

## FRAMING & SAFE-AREA (so it reads on a laptop/phone)
- **Lowest-common viewport for the *content* is 1280×800** — keep critical reads (panel numbers, verdict cards, setpoint table) **away from the extreme edges**, roughly within the central 90%.
- **The post-zoom is mandatory for the key numbers.** Every script's "🖱️ Screen Choreography" already marks where to crop-zoom **1.15–1.2×** and dwell: H1 sensor tiles + GDC Advisor card + amber/red markers; H2 sensor tiles + the three doc reveals + verdict/action cards; H3 GOR table + setpoint table + uplift card. Do these in the editor — that's what makes numbers legible at small sizes regardless of source resolution.
- **Let the panel say the numbers** (V3/V4 rule): the voice stays number-free; the camera zoom is what "quotes" the fixed on-screen figures.

---

## BenQ vs MacBook — which to record on?
- **MacBook (Retina):** ✅ Preferred. Supersampling gives sharper text/lines at 1080p/1440p. Just remember the **window-16:9** trick (panel is ~3:2).
- **BenQ 27" 1440p, full screen:** Fine if you **capture at native 1440p and DON'T downscale during capture**, then export 1440p. It's 16:9 natively (no window trick needed), but it lacks the Retina supersampling edge. If you record the BenQ at 1080p full-screen, the fixed `14px` UI renders relatively small — you'll depend even more heavily on the post-zoom.

**Bottom line:** Record on the **MacBook**, window at **1280×720 CSS (Retina 2×)**, export **1440p**, color-managed to **Rec.709** — and apply the script's post-zoom. That is the "perfect" setup, with **no CSS changes**.

---

## OPTIONAL — only if a test recording proves text is still too small
A minimal, low-risk "presentation scale" could be added later. Do **not** do this preemptively (minimal-diff discipline). Two candidate approaches, each ~a few lines:
1. **Base-font bump behind a query flag** — e.g., `?present=1` sets `body{font-size:15–16px}`. Risk: the `100vh`-locked panels may re-pack; must be verified per tab.
2. **`transform: scale()` on a wrapper** for a fixed "zoom" that scales *everything* (text + charts) uniformly. Risk: needs a matching width/height compensation so it still fills the frame; Plotly may need a resize nudge.
Either should be implemented only after a test clip shows it's needed, then verified live on H1/H2/H3 before recording.
