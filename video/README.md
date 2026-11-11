# Observatorio de Políticas Públicas de Antioquia · «¿Sabías que…?»

Proyecto HyperFrames (1920×1080, 30 fps, 57,45 s) del video institucional del Observatorio de Políticas Públicas de Antioquia, Gobernación de Antioquia.

## Estructura
- `src/` — fuentes editables de las escenas (`s1`…`s8`), `index.html`, `shared.css` (identidad de la Gobernación) y subtítulos.
- `compositions/` + `index.html` — salida de `python3 tools/build.py` (expande íconos Lucide, mapa de Antioquia y lista de efectos). **Edita en `src/` y vuelve a construir.**
- `assets/` — voz (`voz.mp3` = Voz2), tiempos por palabra (`voz_words.json`), música y efectos (`audio/`), Poppins (`fonts/`), logo, mapa por subregiones y fotos del PDF.
- `tools/` — `build.py`, `captions.py` (subtítulos + `../salida/subtitulos.srt`), `sfx.json` (efectos y tiempos), `master.py` (audio a −16 LUFS / −4,5 dBTP), `vertical.py` (versión 1080×1920), `mix.py` (mezcla de referencia en ffmpeg).

## Escenas
| # | Escena | Inicio |
|---|---|---|
| 1 | Caos · 43 políticas | 0,00 s |
| 2 | Revelación · navegador del Observatorio | 10,60 s |
| 3 | Temas · 7 burbujas | 17,55 s |
| 4 | Tableros · 89 indicadores | 23,50 s |
| 5 | Territorio · 125 municipios, 9 subregiones | 32,30 s |
| 6 | Semáforo · tres instrumentos | 38,95 s |
| 7 | Evidencia · Política + Calidad de Vida | 43,35 s |
| 8 | Cierre · slogan, logo y botón | 49,45 s |

## Renderizar
```bash
python3 tools/captions.py && python3 tools/build.py
npx hyperframes render --quality delivery --crf 12 -o final_raw.mp4
python3 tools/master.py final_raw.mp4 ../salida/observatorio_sabias_que.mp4
```
Vertical: renderiza la horizontal con `data-hidden` en el host `#captions`, masterízala a `assets/render/horizontal_sin_subtitulos.mp4`, luego `python3 tools/vertical.py` y `npx hyperframes render -c vertical.html --quality delivery --crf 12`.
