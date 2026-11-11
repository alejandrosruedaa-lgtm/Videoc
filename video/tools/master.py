#!/usr/bin/env python3
"""Masteriza el audio de un MP4 renderizado: loudnorm en dos pasadas a -16 LUFS / -4.5 dBTP, vídeo copiado.
Uso: python3 tools/master.py entrada.mp4 salida.mp4"""
import json, subprocess, sys
src, dst = sys.argv[1], sys.argv[2]
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "loudnorm=I=-16:TP=-4.5:LRA=11:print_format=json", "-vn", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
af = (f"loudnorm=I=-16:TP=-4.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "copy", "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", dst], check=True)
out = subprocess.run(["ffmpeg", "-hide_banner", "-i", dst, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
summ = out[out.rindex("Summary"):]
print(" ".join(l.strip() for l in summ.splitlines() if l.strip().startswith(("I:", "Peak:"))))
