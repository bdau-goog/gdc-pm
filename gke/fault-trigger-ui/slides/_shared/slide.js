// slide.js — GDC briefing deck runtime v1.0
// Handles:
//   1. Fit-to-viewport (ResizeObserver on #slide-stage)
//   2. ← → / dot navigation
//   3. Scrubber (.panel-scrub) + ▶ Play (.panel-play) → window.applyState(t, slideIdx)
//   4. Resizable split handles (.split-handle) → CSS --split custom-prop → localStorage
//   5. Author mode (?author) → shows handles + "Copy layout" button
//   6. terms.js dictionary injection ([data-term] elements)
//   7. postMessage handoff on .nav-run / .nav-skip (data-msg attribute)

(function () {
  'use strict';

  var STAGE_W = 1440, STAGE_H = 810;
  var PLAY_MS = 3000;

  var stage  = document.getElementById('slide-stage');
  var slides = Array.from(document.querySelectorAll('#slide-stage > .slide'));
  var N      = slides.length;
  var cur    = 0;
  var playRaf = null, playT0 = null;

  // ── Zoom — persists to localStorage; +/= zoom in, - zoom out, 0 reset ────
  var zoomFactor = parseFloat(localStorage.getItem('gdc.slide.zoom') || '1.0');
  var zoomToast = null;

  function showZoomHint() {
    var pct = Math.round(zoomFactor * 100);
    // Reuse or create a tiny overlay
    if (!zoomToast) {
      zoomToast = document.createElement('div');
      zoomToast.style.cssText = 'position:fixed;bottom:52px;right:14px;z-index:999;' +
        'background:rgba(14,22,38,0.92);border:1px solid rgba(59,130,246,0.4);' +
        'color:#93c5fd;font-family:monospace;font-size:11px;padding:3px 9px;' +
        'border-radius:5px;pointer-events:none;transition:opacity 0.3s';
      document.body.appendChild(zoomToast);
    }
    zoomToast.textContent = 'Zoom ' + pct + '% (+/- to adjust, 0 = fit)';
    zoomToast.style.opacity = '1';
    clearTimeout(zoomToast._t);
    zoomToast._t = setTimeout(function () { zoomToast.style.opacity = '0'; }, 1800);
  }

  function adjustZoom(delta) {
    zoomFactor = parseFloat(Math.max(0.25, Math.min(3.0, zoomFactor + delta)).toFixed(2));
    localStorage.setItem('gdc.slide.zoom', String(zoomFactor));
    fit();
    showZoomHint();
  }

  // ── 1. Fit to viewport ────────────────────────────────────────────────────
  function fit() {
    if (!stage) return;
    var base = Math.min(window.innerWidth / STAGE_W, window.innerHeight / STAGE_H);
    var s    = base * zoomFactor;
    var tx   = (window.innerWidth  - STAGE_W * s) / 2;
    var ty   = (window.innerHeight - STAGE_H * s) / 2;
    stage.style.transform       = 'scale(' + s + ')';
    stage.style.transformOrigin = 'top left';
    stage.style.left            = tx + 'px';
    stage.style.top             = ty + 'px';
  }
  window.addEventListener('resize', fit);
  if (typeof ResizeObserver !== 'undefined') {
    new ResizeObserver(fit).observe(document.documentElement);
  }

  // ── 2. Navigation ─────────────────────────────────────────────────────────
  function goTo(n) {
    stopPlay();
    n = ((n % N) + N) % N;
    slides[cur].classList.remove('active');
    cur = n;
    slides[cur].classList.add('active');
    syncNav();
    resetAnim();
  }

  function syncNav() {
    document.querySelectorAll('.nav-dot').forEach(function (d, i) {
      d.classList.toggle('active', i % N === cur);
    });
    document.querySelectorAll('.nav-counter').forEach(function (el) {
      el.textContent = (cur + 1) + ' / ' + N;
    });
    document.querySelectorAll('.nav-back').forEach(function (btn) {
      btn.style.visibility = cur > 0 ? 'visible' : 'hidden';
    });
    document.querySelectorAll('.nav-next').forEach(function (btn) {
      btn.style.display = cur < N - 1 ? '' : 'none';
    });
    document.querySelectorAll('.nav-run').forEach(function (btn) {
      btn.style.display = cur === N - 1 ? '' : 'none';
    });
    document.querySelectorAll('.nav-skip').forEach(function (btn) {
      btn.style.display = cur < N - 1 ? '' : 'none';
    });
  }

  function buildDots() {
    var container = document.getElementById('nav-dots');
    if (!container) return;
    for (var i = 0; i < N; i++) {
      var d = document.createElement('button');
      d.className = 'nav-dot' + (i === 0 ? ' active' : '');
      d.setAttribute('aria-label', 'Slide ' + (i + 1));
      (function (idx) { d.addEventListener('click', function () { goTo(idx); }); })(i);
      container.appendChild(d);
    }
  }

  function wireNavButtons() {
    document.querySelectorAll('.nav-back').forEach(function (b) {
      b.addEventListener('click', function () { goTo(cur - 1); });
    });
    document.querySelectorAll('.nav-next').forEach(function (b) {
      b.addEventListener('click', function () { goTo(cur + 1); });
    });
    document.querySelectorAll('.nav-run, .nav-skip').forEach(function (b) {
      b.addEventListener('click', function () {
        window.parent.postMessage(b.dataset.msg || 'run', '*');
      });
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); goTo(cur + 1); }
    if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')   { e.preventDefault(); goTo(cur - 1); }
    // Zoom: + / = zoom in, - zoom out, 0 reset to fit
    if (e.key === '+' || e.key === '=') { e.preventDefault(); adjustZoom(+0.05); return; }
    if (e.key === '-' || e.key === '_') { e.preventDefault(); adjustZoom(-0.05); return; }
    if (e.key === '0') { e.preventDefault(); zoomFactor = 1.0; localStorage.setItem('gdc.slide.zoom', '1.0'); fit(); showZoomHint(); return; }
    var n = parseInt(e.key, 10);
    if (n >= 1 && n <= N) goTo(n - 1);
  });

  // ── 3. Scrubber + ▶ Play ──────────────────────────────────────────────────
  // Each animated panel owns a .panel-scrub input and optionally a .panel-play button.
  // window.applyState(t, slideIdx) is defined in the deck's own <script> block.

  function activeScrub() { return slides[cur] ? slides[cur].querySelector('.panel-scrub') : null; }
  function activePlay()  { return slides[cur] ? slides[cur].querySelector('.panel-play')  : null; }

  function resetAnim() {
    stopPlay();
    var s = activeScrub();
    if (s) s.value = 0;
    if (window.applyState) window.applyState(0, cur);
  }

  function stopPlay() {
    if (playRaf) { cancelAnimationFrame(playRaf); playRaf = null; playT0 = null; }
    var btn = activePlay();
    if (btn) btn.textContent = '▶ Play';
  }

  function startPlay() {
    var s   = activeScrub();
    var btn = activePlay();
    if (!s || !window.applyState) return;
    stopPlay();
    s.value = 0;
    window.applyState(0, cur);
    if (btn) btn.textContent = '■ Stop';

    var snapCur = cur;   // capture slide index at play-start
    function tick(ts) {
      if (!playT0) playT0 = ts;
      var t = Math.min(1, (ts - playT0) / PLAY_MS);
      var sc = activeScrub();
      if (sc) sc.value = t * 100;
      window.applyState(t, snapCur);
      if (t < 1) {
        playRaf = requestAnimationFrame(tick);
      } else {
        playRaf = null; playT0 = null;
        var b = activePlay();
        if (b) b.textContent = '▶ Play';
      }
    }
    playRaf = requestAnimationFrame(tick);
  }

  function wireScrubbers() {
    document.querySelectorAll('.panel-scrub').forEach(function (s) {
      s.addEventListener('input', function () {
        stopPlay();
        if (window.applyState) window.applyState(parseFloat(this.value) / 100, cur);
      });
    });
    document.querySelectorAll('.panel-play').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (playRaf) stopPlay(); else startPlay();
      });
    });
  }

  // ── 4. Resizable split handles ────────────────────────────────────────────
  // HTML: <div class="panel-grid"> [left] <div class="split-handle" data-ls-key="h1.p1.split"></div> [right] </div>
  // Drag updates CSS custom prop --split on .panel-grid.  Value persists to localStorage.

  function getScale() {
    var t = stage ? stage.style.transform : '';
    var m = t.match(/scale\(([^)]+)\)/);
    return m ? parseFloat(m[1]) : 1;
  }

  function initSplits() {
    document.querySelectorAll('.split-handle').forEach(function (handle) {
      var grid = handle.closest('.panel-grid');
      if (!grid) return;
      var key = handle.dataset.lsKey;

      // Restore saved split
      if (key) {
        var saved = localStorage.getItem('gdc.slide.' + key);
        if (saved) grid.style.setProperty('--split', saved + 'fr');
      }

      var x0, fr0;
      handle.addEventListener('mousedown', function (e) {
        e.preventDefault();
        x0  = e.clientX;
        fr0 = parseFloat(getComputedStyle(grid).getPropertyValue('--split')) || 1;

        function onMove(ev) {
          var scale = getScale();
          var rect  = grid.getBoundingClientRect();
          var dx    = (ev.clientX - x0) / scale;
          var fr    = Math.max(0.2, Math.min(4, fr0 + dx / (rect.width / scale) * 2));
          grid.style.setProperty('--split', fr.toFixed(3) + 'fr');
          if (key) localStorage.setItem('gdc.slide.' + key, fr.toFixed(3));
        }
        function onUp() {
          document.removeEventListener('mousemove', onMove);
          document.removeEventListener('mouseup', onUp);
        }
        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
      });
    });
  }

  // ── 5. Author mode (?author) ─────────────────────────────────────────────
  function initAuthorMode() {
    var isAuthor = /[?&]author/.test(window.location.search);
    if (isAuthor) document.body.classList.add('author-mode');

    var copyBtn = document.getElementById('author-copy');
    if (!copyBtn) return;
    if (isAuthor) copyBtn.style.display = 'inline-block';
    copyBtn.addEventListener('click', function () {
      var lines = [];
      document.querySelectorAll('.split-handle[data-ls-key]').forEach(function (h) {
        var k = h.dataset.lsKey;
        var v = localStorage.getItem('gdc.slide.' + k);
        if (v) lines.push('  --' + k.replace(/\./g, '-') + ': ' + v + 'fr;');
      });
      var out = lines.length
        ? ':root {\n' + lines.join('\n') + '\n}'
        : '/* no split values saved yet */';
      navigator.clipboard.writeText(out).then(function () {
        copyBtn.textContent = 'Copied!';
        setTimeout(function () { copyBtn.textContent = 'Copy layout'; }, 1500);
      }).catch(function () { copyBtn.textContent = out; });
    });
  }

  // ── 6. Terms injection ────────────────────────────────────────────────────
  function injectTerms() {
    if (!window.TERMS) return;
    document.querySelectorAll('[data-term]').forEach(function (el) {
      var v = TERMS[el.dataset.term];
      if (v !== undefined) el.textContent = v;
    });
  }

  // ── Init ─────────────────────────────────────────────────────────────────
  function init() {
    fit();
    buildDots();
    syncNav();
    injectTerms();
    wireScrubbers();
    initSplits();
    initAuthorMode();
    wireNavButtons();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
