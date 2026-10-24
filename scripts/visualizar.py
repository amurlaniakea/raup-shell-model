#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Visualizador de conchas espirales (modelo de Raup / formulacion secundaria Filin 2026).

Uso:
    python scripts/visualizar.py               # galeria de 6 morfologias
    python scripts/visualizar.py --clasica     # una concha clasica
    python scripts/visualizar.py --torre       # torre alta
    python scripts/visualizar.py --plana       # planispiral (T=0)
    python scripts/visualizar.py --guardar     # exportar PNG sin ventana

Requiere: matplotlib (extra [viz] de pyproject.toml).
Pendiente de contraste con las figuras originales de Raup (1966).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib  # noqa: E402

from model import generate_shell  # noqa: E402

FONDO = "#0a0e27"


def elegir_backend(guardar: bool) -> str:
    """Agg para exportar; backend interactivo si se va a mostrar la ventana."""
    if guardar:
        matplotlib.use("Agg")
        return "Agg"
    for backend in ("TkAgg", "QtAgg"):
        try:
            matplotlib.use(backend)
            return backend
        except Exception:
            continue
    matplotlib.use("Agg")
    return "Agg"


def dibujar_concha(ax, W=2.0, D=0.35, T=0.12, S="circle", rho=1.0,
                   color="#4ECDC4", steps=120, revolutions=2.5, n_phi=32):
    """Añade una concha generada por el modelo al eje 3D dado."""
    shell = generate_shell(
        W=W, D=D, T=T, S=S, rho=rho,
        steps=steps, revolutions=revolutions, r0=1.0, n_phi=n_phi,
    )
    for i, anillo in enumerate(shell):
        x = [p[0] for p in anillo]
        y = [p[1] for p in anillo]
        z = [p[2] for p in anillo]
        x.append(x[0])
        y.append(y[0])
        z.append(z[0])
        ax.plot(x, y, z, color=color,
                alpha=0.2 + 0.8 * (i / len(shell)), linewidth=0.8)


def _figura(ax_kwargs=None):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10, 8))
    fig.patch.set_facecolor(FONDO)
    ax = fig.add_subplot(111, projection="3d", **(ax_kwargs or {}))
    ax.set_facecolor(FONDO)
    ax.tick_params(colors="gray", labelsize=7)
    for label in (ax.set_xlabel, ax.set_ylabel, ax.set_zlabel):
        label("", color="gray")
    return fig, ax


def _etiquetar(ax, titulo):
    ax.set_title(titulo, color="white", fontsize=13, fontweight="bold", pad=12)


def _cerrar(fig, ruta, guardar):
    import matplotlib.pyplot as plt
    fig.tight_layout()
    if guardar:
        fig.savefig(ruta, dpi=150, bbox_inches="tight", facecolor=FONDO)
        print(f"Guardado: {ruta}")
    else:
        plt.show()
    plt.close(fig)


def vista_simple(modo, guardar):
    import matplotlib.pyplot as plt
    configs = {
        "clasica": (dict(W=2.0, D=0.35, T=0.12), "#4ECDC4",
                    "Clasica (W=2.0, D=0.35, T=0.12)", "concha_clasica.png"),
        "torre": (dict(W=1.7, D=0.22, T=0.55, S="ellipse", rho=1.3), "#FF6B6B",
                  "Torre alta (W=1.7, T=0.55)", "concha_torre.png"),
        "plana": (dict(W=2.3, D=0.35, T=0.0), "#45B7D1",
                  "Planispiral (T=0.0)", "concha_plana.png"),
    }
    params, color, titulo, ruta = configs[modo]
    fig, ax = _figura()
    dibujar_concha(ax, color=color, **params)
    _etiquetar(ax, titulo)
    _cerrar(fig, ruta, guardar)
    plt.close(fig)


def galeria(guardar):
    import matplotlib.pyplot as plt
    configs = [
        (dict(W=2.0, D=0.35, T=0.12), "#FF6B6B", "Clasica"),
        (dict(W=1.7, D=0.22, T=0.55, S="ellipse", rho=1.3), "#4ECDC4", "Torre alta"),
        (dict(W=2.3, D=0.35, T=0.0), "#45B7D1", "Planispiral"),
        (dict(W=3.5, D=0.1, T=0.08), "#FFA07A", "Expansion rapida"),
        (dict(W=1.3, D=0.5, T=0.3, S="ellipse", rho=1.5), "#98D8C8", "Compacta"),
        (dict(W=2.5, D=0.0, T=0.15), "#F7DC6F", "Toca el eje"),
    ]
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor(FONDO)
    for idx, (params, color, titulo) in enumerate(configs, start=1):
        ax = fig.add_subplot(2, 3, idx, projection="3d")
        ax.set_facecolor(FONDO)
        ax.tick_params(colors="gray", labelsize=6)
        dibujar_concha(ax, color=color, **params)
        _etiquetar(ax, titulo)
    fig.suptitle("Galeria de morfologias - Modelo de Raup / Filin (secundaria)",
                 color="white", fontsize=16, fontweight="bold", y=0.98)
    _cerrar(fig, "galeria_morfologias.png", guardar)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Visualizador de conchas espirales")
    parser.add_argument("--clasica", action="store_true")
    parser.add_argument("--torre", action="store_true")
    parser.add_argument("--plana", action="store_true")
    parser.add_argument("--guardar", action="store_true",
                        help="Exportar PNG en vez de abrir ventana")
    args = parser.parse_args()
    backend = elegir_backend(args.guardar)
    if backend == "Agg" and not args.guardar:
        print("Sin backend grafico disponible. Usa --guardar y abre el PNG.")
    if args.clasica:
        vista_simple("clasica", args.guardar)
    elif args.torre:
        vista_simple("torre", args.guardar)
    elif args.plana:
        vista_simple("plana", args.guardar)
    else:
        galeria(args.guardar)


if __name__ == "__main__":
    main()
