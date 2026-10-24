#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Pedro Sordo Martinez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Genera banner cientifico del README (Fase D). Formulacion secundaria Filin 2026; pendiente contraste Raup 1966."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("ERROR: matplotlib o numpy no disponibles. Instala con: python -m pip install matplotlib numpy")
    sys.exit(1)

try:
    from model import generate_shell
except ImportError as e:
    print("ERROR: no se puede importar model:", e)
    sys.exit(1)


def draw_spiral(ax, params, label_text, color_str):
    W = params["W"]
    D = params["D"]
    T = params["T"]
    S = params["S"]
    rho = params.get("rho", 1.0)
    shell = generate_shell(
        W=W, D=D, T=T, S=S, rho=rho,
        steps=100, revolutions=2.0, r0=1.0, n_phi=32
    )
    for ring in shell:
        proj_x = [pt[0] for pt in ring]
        proj_y = [pt[2] for pt in ring]
        proj_x_closed = proj_x + [proj_x[0]]
        proj_y_closed = proj_y + [proj_y[0]]
        ax.plot(proj_x_closed, proj_y_closed, color=color_str, alpha=0.75, linewidth=1.5)

    ax.text(0.02, 0.02, label_text, transform=ax.transAxes, fontsize=9,
            verticalalignment="bottom",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7, edgecolor=color_str))


def main():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), dpi=120)
    fig.patch.set_facecolor("#08101e")

    palettes = [
        ("#1e3a5f", "Concha clasica"),
        ("#00bfa5", "Torre alta"),
        ("#7b2cbf", "Planispiral"),
    ]
    configs = [
        {"W": 2.0, "D": 0.35, "T": 0.12, "S": "circle", "rho": 1.0},
        {"W": 1.7, "D": 0.22, "T": 0.55, "S": "ellipse", "rho": 1.3},
        {"W": 2.3, "D": 0.35, "T": 0.0, "S": "circle", "rho": 1.0},
    ]
    titles = ["Clasica", "Torre alta", "Planispiral"]

    for idx, ax in enumerate(axes):
        ax.set_facecolor("#08101e")
        cfg = configs[idx]
        pal_color, pal_name = palettes[idx]
        title = titles[idx]
        label_text = f"{title}\nW={cfg['W']} D={cfg['D']} T={cfg['T']} S={cfg['S']} rho={cfg['rho']}"
        draw_spiral(ax, cfg, label_text, pal_color)
        ax.set_axis_off()
        ax.set_title(title, color="white", fontsize=14, fontweight="bold", pad=10)
        ax.text(0.5, 1.02, f"W={cfg['W']} D={cfg['D']} T={cfg['T']} rho={cfg['rho']}",
                ha="center", va="bottom", transform=ax.transAxes, fontsize=8, color="#b0bec5")

    fig.suptitle("Modelo geometrico de conchas espirales - Raup / Filin (formulacion secundaria S3-S8)",
                 fontsize=16, color="white", fontweight="bold", y=1.02)

    fig.text(0.99, 0.01, "Nota: formulacion secundaria (Filin 2026); pendiente contraste con Raup (1966).\nGenerado con scripts/render_readme_banner.py (matplotlib + modelo propio).",
             fontsize=7, color="#78909c", ha="right", va="bottom")

    output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "readme_banner.png")
    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout(rect=[0.02, 0.03, 0.98, 0.92])
    plt.savefig(output_path, dpi=120, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"Banner generado: {output_path}")


if __name__ == "__main__":
    main()
