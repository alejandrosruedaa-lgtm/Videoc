#!/usr/bin/env python3
"""Genera src/captions.html y ../salida/subtitulos.srt a partir del guion (ortografía) y
assets/voz_words.json (tiempos por palabra de la transcripción de la voz)."""
import json, os, re, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
words = json.load(open(os.path.join(ROOT, "assets/voz_words.json"), encoding="utf-8"))
script = open(os.path.join(ROOT, "tools/guion.txt"), encoding="utf-8").read().split()
assert len(script) == len(words), (len(script), len(words))
toks = [(s, w[1], w[2]) for s, w in zip(script, words)]
# Cortes: por frase (puntuación); frases largas se parten en trozos equilibrados; frases cortas se unen
import math
phrases, cur = [], []
for t in toks:
    cur.append(t)
    if re.search(r"[.?!:,…]$", t[0]): phrases.append(cur); cur = []
if cur: phrases.append(cur)
merged = []
for ph in phrases:
    if merged and (len(merged[-1]) <= 2 or len(ph) <= 1) and len(merged[-1]) + len(ph) <= 7 and len(" ".join(x[0] for x in merged[-1] + ph)) <= 44:
        merged[-1] = merged[-1] + ph
    else:
        merged.append(ph)
WEAK = {"y", "de", "la", "el", "con", "a", "que", "en", "sus", "tu", "por", "para", "lo", "se", "su"}
def L(g): return len(" ".join(x[0] for x in g))
def split(g):
    if len(g) <= 7 and L(g) <= 42: return [g]
    best = None
    for j in range(2, len(g) - 1):
        pen = abs(L(g[:j]) - L(g[j:])) + (40 if g[j - 1][0].lower().strip("¿¡") in WEAK else 0) + (40 if g[j][0].lower() == "y" else 0)
        if best is None or pen < best[0]: best = (pen, j)
    j = best[1]
    return split(g[:j]) + split(g[j:])
groups = [part for ph in merged for part in split(ph)]
out = []
for gi, g in enumerate(groups):
    start = max(0, g[0][1] - 0.08)
    end = groups[gi + 1][0][1] - 0.1 if gi + 1 < len(groups) else g[-1][2] + 0.4
    end = min(end, g[-1][2] + 0.7)
    out.append((round(start, 2), round(end, 2), " ".join(x[0] for x in g)))
def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"
os.makedirs(os.path.join(ROOT, "../salida"), exist_ok=True)
with open(os.path.join(ROOT, "../salida/subtitulos.srt"), "w", encoding="utf-8") as f:
    for i, (a, b, t) in enumerate(out, 1):
        f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
items = "\n".join(
    f'      <div id="cap-{i:02d}" class="clip cap" data-start="{a}" data-duration="{round(b - a, 2)}" data-track-index="0"><span>{html.escape(t)}</span></div>'
    for i, (a, b, t) in enumerate(out, 1))
page = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cap {{ position: absolute; left: 0; right: 0; bottom: 96px; display: flex; justify-content: center; }}
    .cap span {{ font-family: "Poppins", sans-serif; font-weight: 500; font-size: 34px; line-height: 1.25; color: #fff;
      background: rgba(8, 67, 47, 0.62); padding: 8px 22px 10px; border-radius: 14px 14px 14px 0; letter-spacing: -0.005em; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1920" data-height="1080">
{items}
  </div>
  <script>
    (function () {{
      const tl = gsap.timeline({{ paused: true }});
      document.querySelectorAll("#captions .cap span, [data-composition-id='captions'] .cap span").forEach((el) => {{
        const c = el.parentElement; const s = parseFloat(c.dataset.start);
        tl.fromTo(el, {{ opacity: 0, y: 10 }}, {{ opacity: 1, y: 0, duration: 0.12, ease: "power2.out" }}, s);
      }});
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
"""
open(os.path.join(ROOT, "src/captions.html"), "w", encoding="utf-8").write(page)
for a, b, t in out: print(f"{a:6.2f}-{b:6.2f} {t}")
