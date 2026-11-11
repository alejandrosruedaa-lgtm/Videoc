#!/usr/bin/env python3
"""Reproduce con ffmpeg la mezcla declarada en index.html (voz, música con envolvente, SFX)
y la masteriza a -16 LUFS / -4.5 dBTP. Uso: python3 tools/mix.py salida.wav"""
import re, json, sys, subprocess, html, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
TOTAL = float(re.search(r'data-composition-id="main"[^>]*data-duration="([\d.]+)"', s).group(1))
inputs, filters, labels = [], [], []
for m in re.finditer(r"<audio ([^>]*)>", s):
    a = dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(1)))
    i = len(inputs) // 2
    inputs += ["-i", os.path.join(ROOT, a["src"])]
    st, du = float(a["data-start"]), float(a["data-duration"]); ms = float(a.get("data-media-start", 0))
    vol = float(a.get("data-volume", 1))
    f = f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,atrim={ms}:{ms + du},asetpts=PTS-STARTPTS"
    if "data-automation" in a:
        pts = json.loads(html.unescape(a["data-automation"]))["lanes"][0]["points"]
        expr = f"{pts[-1]['v']}"
        for p0, p1 in reversed(list(zip(pts, pts[1:]))):
            expr = f"if(lt(t,{p1['t']}),{p0['v']}+({p1['v']}-{p0['v']})*(t-{p0['t']})/({p1['t']}-{p0['t']}+1e-9),{expr})"
        f += f",volume='{expr}':eval=frame"
    f += f",volume={vol}"
    if a.get("data-fade-out"): f += f",afade=t=out:st={du - float(a['data-fade-out'])}:d={a['data-fade-out']}"
    f += f",adelay={int(st * 1000)}:all=1[a{i}]"
    filters.append(f); labels.append(f"[a{i}]")
filters.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0,atrim=0:{TOTAL}[mix]")
pre = sys.argv[1].replace(".wav", "_pre.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[mix]", "-ar", "48000", pre], check=True)
# master: dos pasadas de loudnorm a -16 LUFS, TP -4.5
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", pre, "-af", "loudnorm=I=-16:TP=-4.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
af = (f"loudnorm=I=-16:TP=-4.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-af", af, "-ar", "48000", sys.argv[1]], check=True)
print("pre-master", j["input_i"], "LUFS ->", sys.argv[1])
