#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Genera assets/concha-espiral.svg a partir de src/model.py (solo libreria estandar).

Cada concha se dibuja con dos vistas obtenidas del modelo, no dibujadas a mano:
  * vista superior: borde exterior (phi=0), borde interior (phi=pi) y linea central;
  * corte sagital en theta=0: aperturas de las tres primeras vueltas y la recta z = T*r.

Uso:
    python scripts/render_figures.py          # escribe assets/concha-espiral.svg
    python scripts/render_figures.py --check  # sale con 1 si el archivo no esta al dia

Formulacion SECUNDARIA (Filin 2026); pendiente de contraste con Raup (1966).
"""

import os
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from model import generate_curve, generate_shell, whorl_overlap  # noqa: E402

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "concha-espiral.svg")

TURNS = 3  # vueltas de la vista superior
PER_TURN = 48  # puntos de la linea central por vuelta
N_PHI = 96  # puntos por apertura (multiplo de 4: incluye phi = 0, pi/2, pi)
SECTION_WHORLS = 3  # aperturas del corte sagital

CONFIGS = [
    {"name": "Clásica", "W": 2.0, "D": 0.35, "T": 0.12, "S": "circle", "rho": 1.0},
    {"name": "Torre alta", "W": 1.7, "D": 0.22, "T": 0.55, "S": "ellipse", "rho": 1.3},
    {"name": "Planispiral abierta", "W": 3.0, "D": 0.5, "T": 0.0, "S": "circle", "rho": 1.0},
]

Point = tuple[float, float]


def panel_data(cfg: dict) -> dict:
    """Coordenadas del modelo (sin escalar) para una concha."""
    steps = TURNS * PER_TURN + 1
    kw = {"W": cfg["W"], "D": cfg["D"], "T": cfg["T"]}
    shell = generate_shell(S=cfg["S"], rho=cfg["rho"], steps=steps, revolutions=float(TURNS), r0=1.0, n_phi=N_PHI, **kw)
    curve = generate_curve(steps=steps, revolutions=float(TURNS), r0=1.0, **kw)
    return {
        "centerline": [(p[0], p[1]) for p in curve],
        "outer": [(ring[0][0], ring[0][1]) for ring in shell],
        "inner": [(ring[N_PHI // 2][0], ring[N_PHI // 2][1]) for ring in shell],
        "apertures": [[(p[0], p[2]) for p in shell[k * PER_TURN]] for k in range(SECTION_WHORLS)],
        "centers": [(curve[k * PER_TURN][0], curve[k * PER_TURN][2]) for k in range(SECTION_WHORLS)],
        "overlap": whorl_overlap(W=cfg["W"], D=cfg["D"], T=cfg["T"], rho=cfg["rho"]),
    }


class _Fit:
    """Ajuste a un recuadro conservando la proporcion; el eje y del modelo apunta hacia arriba."""

    def __init__(self, points: list[Point], box: tuple[float, float, float, float], margin: float = 12.0):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        self.xmin, self.xmax, self.ymin, self.ymax = min(xs), max(xs), min(ys), max(ys)
        bx, by, bw, bh = box
        dx = max(self.xmax - self.xmin, 1e-9)
        dy = max(self.ymax - self.ymin, 1e-9)
        self.scale = min((bw - 2 * margin) / dx, (bh - 2 * margin) / dy)
        self.ox = bx + (bw - dx * self.scale) / 2
        self.oy = by + (bh - dy * self.scale) / 2

    def __call__(self, p: Point) -> tuple[float, float]:
        return (self.ox + (p[0] - self.xmin) * self.scale, self.oy + (self.ymax - p[1]) * self.scale)


def _path(points: list[Point], fit: _Fit, close: bool = False) -> str:
    coords = [fit(p) for p in points]
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in coords)
    return d + (" Z" if close else "")


def _top_view(data: dict, box: tuple[float, float, float, float], cls: str) -> str:
    outer, inner = data["outer"], data["inner"]
    fit = _Fit(outer + inner + [(0.0, 0.0)], box)
    ox, oy = fit((0.0, 0.0))
    band = _path(outer + inner[::-1], fit, close=True)
    return (
        f'<path d="{band}" class="{cls}" fill="currentColor" fill-opacity="0.14" stroke="none"/>'
        f'<path d="{_path(outer, fit)}" class="{cls}" fill="none" stroke="currentColor" stroke-width="1.6"/>'
        f'<path d="{_path(inner, fit)}" class="{cls}" fill="none" stroke="currentColor" stroke-width="1.6" opacity="0.65"/>'
        f'<path d="{_path(data["centerline"], fit)}" fill="none" stroke="var(--muted)" stroke-width="1" stroke-dasharray="3 3"/>'
        f'<path d="M{ox - 4:.1f} {oy:.1f} H{ox + 4:.1f} M{ox:.1f} {oy - 4:.1f} V{oy + 4:.1f}" stroke="var(--fg)" stroke-width="1.2"/>'
    )


def _section_view(data: dict, box: tuple[float, float, float, float], cls: str) -> str:
    apertures, centers = data["apertures"], data["centers"]
    everything = [p for ap in apertures for p in ap] + [(0.0, 0.0)]
    fit = _Fit(everything, box)
    parts = []
    axis_top = fit((0.0, max(p[1] for p in everything)))
    axis_bottom = fit((0.0, min(p[1] for p in everything)))
    parts.append(
        f'<path d="M{axis_top[0]:.1f} {axis_top[1] - 6:.1f} V{axis_bottom[1] + 6:.1f}" stroke="var(--muted)" stroke-width="1"/>'
    )
    parts.append(f'<text x="{axis_top[0] + 5:.1f}" y="{axis_top[1] - 1:.1f}" font-size="10" fill="var(--muted)">eje</text>')
    o = fit((0.0, 0.0))
    last = fit(centers[-1])
    parts.append(
        f'<path d="M{o[0]:.1f} {o[1]:.1f} L{last[0]:.1f} {last[1]:.1f}" stroke="var(--muted)" stroke-width="1" stroke-dasharray="3 3"/>'
    )
    for k, ap in enumerate(apertures):
        parts.append(
            f'<path d="{_path(ap, fit, close=True)}" class="{cls}" fill="currentColor" fill-opacity="{0.10 + 0.04 * k:.2f}" '
            f'stroke="currentColor" stroke-width="1.6"/>'
        )
        cx, cy = fit(centers[k])
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.2" fill="var(--fg)"/>')
    return "".join(parts)


def build_svg() -> str:
    """SVG completo como cadena (determinista)."""
    width, height = 960, 650
    col_w = 300
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        'role="img" aria-labelledby="t d">',
        "<title id=\"t\">Tres conchas generadas con el modelo de enrollamiento espiral</title>",
        "<desc id=\"d\">Para cada concha, vista superior y corte sagital calculados con src/model.py. "
        "Formulación secundaria (Filin 2026), pendiente de contraste con Raup (1966).</desc>",
        "<style>"
        ":root{--fg:#1f2328;--muted:#656d76;--c0:#0969da;--c1:#1a7f37;--c2:#8250df}"
        "@media (prefers-color-scheme: dark){:root{--fg:#e6edf3;--muted:#8b949e;--c0:#58a6ff;--c1:#3fb950;--c2:#bc8cff}}"
        "text{fill:var(--fg);font-family:system-ui,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}"
        ".c0{color:var(--c0)}.c1{color:var(--c1)}.c2{color:var(--c2)}"
        "</style>",
        f'<text x="{width / 2:.0f}" y="30" font-size="18" font-weight="700" text-anchor="middle">'
        "Modelo de enrollamiento espiral: tres conchas generadas desde src/model.py</text>",
    ]
    for c, cfg in enumerate(CONFIGS):
        data = panel_data(cfg)
        x0 = 20 + c * (col_w + 10)
        cls = f"c{c}"
        shape = "círculo" if cfg["S"] == "circle" else f"elipse ρ={cfg['rho']}"
        solapa = "las vueltas se solapan" if data["overlap"] else "las vueltas no se solapan"
        out.append(f'<g id="concha-{"ABC"[c]}">')
        out.append(f'<text x="{x0}" y="66" font-size="15" font-weight="700" class="{cls}" style="fill:currentColor">{escape(cfg["name"])}</text>')
        out.append(
            f'<text x="{x0}" y="86" font-size="12">W={cfg["W"]} · D={cfg["D"]} · T={cfg["T"]} · {escape(shape)}</text>'
        )
        out.append(f'<text x="{x0}" y="104" font-size="12" fill="var(--muted)" style="fill:var(--muted)">{solapa}</text>')
        out.append(f'<g id="vista-superior-{"ABC"[c]}">{_top_view(data, (x0, 118, col_w, 240), cls)}</g>')
        out.append(f'<text x="{x0}" y="372" font-size="11" style="fill:var(--muted)">Vista superior (bordes y línea central)</text>')
        out.append(f'<g id="corte-sagital-{"ABC"[c]}">{_section_view(data, (x0, 392, col_w, 200), cls)}</g>')
        out.append(f'<text x="{x0}" y="606" font-size="11" style="fill:var(--muted)">Corte sagital θ = 0 (recta de centros: z = T·r)</text>')
        out.append("</g>")
    out.append(
        f'<text x="{width / 2:.0f}" y="634" font-size="10.5" text-anchor="middle" style="fill:var(--muted)">'
        "Cada panel tiene su propia escala. Generado con scripts/render_figures.py. Formulación secundaria (Filin 2026); pendiente de contraste con Raup (1966).</text>"
    )
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    svg = build_svg()
    path = os.path.abspath(OUTPUT)
    if "--check" in argv:
        current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        if current != svg:
            print(f"DESACTUALIZADO: {path} no coincide con el modelo. Ejecuta: python scripts/render_figures.py")
            return 1
        print("OK: la figura coincide con el modelo")
        return 0
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)
    print(f"Figura generada: {path} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
