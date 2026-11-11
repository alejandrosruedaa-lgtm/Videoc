#!/usr/bin/env python3
"""Genera vertical.html (1080x1920): la versión horizontal sin subtítulos (assets/render/) centrada sobre
fondo de la Gobernación, logo arriba y subtítulos grandes abajo. Render: npx hyperframes render -c vertical.html"""
import re, os, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
caps = re.findall(r'data-start="([\d.]+)" data-duration="([\d.]+)"[^>]*><span>([^<]*)</span>',
                  open(os.path.join(ROOT, "compositions/captions.html"), encoding="utf-8").read())
TOTAL = 57.45
items = "\n".join(
    f'    <div id="vc-{i:02d}" class="clip vcap" data-start="{a}" data-duration="{d}" data-track-index="3"><span>{t}</span></div>'
    for i, (a, d, t) in enumerate(caps, 1))
page = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080, height=1920" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  <style>
    @font-face {{ font-family: "Poppins"; font-weight: 600; src: url("assets/fonts/poppins-latin-600-normal.woff2") format("woff2"); }}
    @font-face {{ font-family: "Poppins"; font-weight: 800; src: url("assets/fonts/poppins-latin-800-normal.woff2") format("woff2"); }}
    @font-face {{ font-family: "Poppins"; font-weight: 900; src: url("assets/fonts/poppins-latin-900-normal.woff2") format("woff2"); }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #0B5640; }}
    #vroot {{ position: relative; width: 1080px; height: 1920px; font-family: "Poppins", sans-serif; overflow: hidden; }}
    #vbg {{ position: absolute; inset: 0; background: radial-gradient(120% 70% at 50% 35%, #0f6a4f 0%, #0B5640 45%, #08432f 100%); }}
    #vbg::after {{ content: ""; position: absolute; inset: 0; opacity: .18;
      background-image: radial-gradient(rgba(58,249,162,.55) 1.2px, transparent 1.6px); background-size: 36px 36px; }}
    #vlogo {{ position: absolute; left: 230px; top: 170px; width: 620px; height: 250px; background: #fff; border-radius: 28px 28px 28px 0;
      display: flex; align-items: center; justify-content: center; box-shadow: 0 30px 70px rgba(3,30,21,.38); }}
    #vlogo img {{ width: 500px; }}
    #vtitle {{ position: absolute; left: 0; right: 0; top: 480px; text-align: center; color: #fff; font-weight: 800; font-size: 50px; line-height: 1.1; letter-spacing: -0.03em; }}
    #vtitle b {{ color: #3AF9A2; font-weight: 800; }}
    #vframe {{ position: absolute; left: 40px; top: 690px; width: 1000px; height: 563px; border-radius: 26px 26px 26px 0; overflow: hidden;
      box-shadow: 0 40px 90px rgba(2,25,17,.55), 0 0 0 3px rgba(58,249,162,.55); }}
    #vvideo {{ position: absolute; left: 0; top: 0; width: 1000px; height: 563px; object-fit: cover; }}
    .vcap {{ position: absolute; left: 80px; right: 80px; top: 1340px; height: 300px; display: flex; align-items: flex-start; justify-content: center; text-align: center; }}
    .vcap span {{ color: #fff; font-weight: 800; font-size: 62px; line-height: 1.15; letter-spacing: -0.02em; text-shadow: 0 4px 18px rgba(0,0,0,.35); }}
    #vbar {{ position: absolute; left: 80px; right: 80px; top: 1760px; height: 10px; border-radius: 5px; background: rgba(255,255,255,.18); overflow: hidden; }}
    #vbarfill {{ width: 100%; height: 100%; background: #3AF9A2; border-radius: 5px; transform-origin: 0 50%; }}
  </style>
</head>
<body>
  <div id="vroot" data-composition-id="vertical" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
    <div id="vbg"></div>
    <div id="vlogo"><img src="assets/img/logo_gobernacion.png" alt="Gobernación de Antioquia" /></div>
    <div id="vtitle">Observatorio de Políticas<br />Públicas de <b>Antioquia</b></div>
    <div id="vframe"><video id="vvideo" class="clip" src="assets/render/horizontal_sin_subtitulos.mp4" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-has-audio="true" playsinline></video></div>
{items}
    <div id="vbar"><div id="vbarfill"></div></div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#vbarfill", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {TOTAL}, ease: "none" }}, 0);
    tl.fromTo("#vlogo", {{ scale: 1 }}, {{ scale: 1.04, duration: {TOTAL}, ease: "sine.inOut" }}, 0);
    document.querySelectorAll(".vcap").forEach((c) => {{
      tl.fromTo(c.querySelector("span"), {{ opacity: 0, y: 24, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.18, ease: "back.out(2)" }}, parseFloat(c.dataset.start));
    }});
    window.__timelines["vertical"] = tl;
  </script>
</body>
</html>
"""
open(os.path.join(ROOT, "vertical.html"), "w", encoding="utf-8").write(page)
print(len(caps), "subtítulos")
