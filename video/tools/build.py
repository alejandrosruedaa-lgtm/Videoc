#!/usr/bin/env python3
"""Expande las fuentes de src/ en compositions/.

- /*SHARED*/            -> contenido de src/shared.css (identidad Gobernación)
- <i data-icon="x" ...></i> -> SVG de línea (Lucide, ISC) en línea
- <i data-map="full"></i>   -> mapa de Antioquia por subregiones (del HTML del Observatorio)
- <i data-map="mini"></i>   -> silueta simple del departamento
- <!--WALL:prefijo:columnas:filas-->  -> muro de documentos (escena 1 y 2)

Uso: python3 tools/build.py   (sobrescribe compositions/*.html a partir de src/*.html)
"""
import json, re, glob, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS = os.path.join(ROOT, "tools/icons")
SHARED = open(os.path.join(ROOT, "src/shared.css"), encoding="utf-8").read()
MAP_SVG = open(os.path.join(ROOT, "assets/img/antioquia_subregiones.svg"), encoding="utf-8").read()


def icon(name, attrs):
    raw = open(os.path.join(ICONS, f"{name}.svg"), encoding="utf-8").read()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S).group(1)
    inner = re.sub(r"\s+", " ", inner).strip()
    return (f'<svg {attrs} data-icon="{name}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>')


def map_full(attrs):
    body = re.search(r"<svg[^>]*>(.*)</svg>", MAP_SVG, re.S).group(1)
    return f'<svg {attrs} viewBox="0 0 615 615" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


def map_mini(attrs):
    border = re.search(r'<g class="border">(.*?)</g>', MAP_SVG, re.S).group(1)
    return f'<svg {attrs} viewBox="0 0 615 615" xmlns="http://www.w3.org/2000/svg"><g class="border">{border}</g></svg>'


def wall(prefix, cols, rows):
    kinds = ["PDF", "XLSX", "DOC", "PDF", "TABLA", "ACTA", "PDF", "XLSX"]
    out = [f'<div id="{prefix}-wall" class="wall" data-layout-ignore>']
    seed = 7
    for c in range(cols):
        out.append(f'<div class="wall-col" id="{prefix}-col{c}">')
        for r in range(rows):
            seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
            k = kinds[(c * 3 + r) % len(kinds)]
            lines = 3 + seed % 3
            op = 0.10 + (seed % 9) / 70
            tall = "tall" if (seed >> 5) % 3 == 0 else ""
            ls = "".join(f'<b style="width:{55 + ((seed >> (i * 3)) % 40)}%"></b>' for i in range(lines))
            out.append(f'<div class="doc {tall}" style="opacity:{op:.2f}"><span class="doc-k">{k}</span>{ls}</div>')
        out.append("</div>")
    out.append("</div>")
    return "".join(out)


def sfx_tags():
    import subprocess
    items = json.load(open(os.path.join(ROOT, "tools/sfx.json"), encoding="utf-8"))
    out = []
    lanes = []  # fin de cada carril, para no solapar clips en un mismo track
    for i, it in enumerate(items, 1):
        name, t, vol, note = it[0], it[1], it[2], it[3]
        media_start = it[4] if len(it) > 4 else 0
        src = f"assets/audio/{name}.mp3"
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(ROOT, src)]).decode().strip()) - media_start
        dur = round(min(dur, 3.0 if name != "riser" else 3.3, 57.2 - t), 3)
        ms = f' data-media-start="{media_start}"' if media_start else ""
        lane = next((k for k, e in enumerate(lanes) if e <= t), None)
        if lane is None: lanes.append(0); lane = len(lanes) - 1
        lanes[lane] = t + dur
        out.append(f'      <audio id="sfx-{i:02d}" class="clip" src="{src}" data-start="{t}" data-duration="{dur}"{ms} data-track-index="{12 + lane}" data-volume="{vol}" data-audio-group="sfx"></audio><!-- {note} -->')
    return "\n".join(out)


def expand(s):
    s = s.replace("/*SHARED*/", SHARED)
    if "<!--SFX-->" in s:
        s = s.replace("<!--SFX-->", sfx_tags())
    s = re.sub(r'<i data-icon="([\w-]+)"([^>]*)></i>', lambda m: icon(m.group(1), m.group(2).strip()), s)
    s = re.sub(r'<i data-map="full"([^>]*)></i>', lambda m: map_full(m.group(1).strip()), s)
    s = re.sub(r'<i data-map="mini"([^>]*)></i>', lambda m: map_mini(m.group(1).strip()), s)
    s = re.sub(r"<!--WALL:([\w-]+):(\d+):(\d+)-->", lambda m: wall(m.group(1), int(m.group(2)), int(m.group(3))), s)
    return s


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    for f in sorted(glob.glob(os.path.join(ROOT, "src/*.html"))):
        name = os.path.basename(f)
        out = os.path.join(ROOT, "index.html" if name == "index.html" else f"compositions/{name}")
        open(out, "w", encoding="utf-8").write(expand(open(f, encoding="utf-8").read()))
        print("built", os.path.relpath(out, ROOT))
