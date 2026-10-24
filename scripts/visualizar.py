#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Visualizador interactivo de conchas espirales (Modelo de Raup/Filin).

Uso rápido:
    python scripts/visualizar.py              # Galería de 6 morfologías
    python scripts/visualizar.py --clasica    # Solo concha clásica
    python scripts/visualizar.py --torre      # Solo torre alta
    python scripts/visualizar.py --plana      # Solo planispiral
    python scripts/visualizar.py --guardar    # Guarda PNG en vez de mostrar ventana

Requisitos: matplotlib (ya incluido en extras [viz] del pyproject.toml)
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import matplotlib
matplotlib.use("Agg")  # Backend sin ventana para --guardar
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from model import generate_shell


def dibujar_concha(ax, W, D, T, S='circle', rho=1.0, color='#4ECDC4',
                   steps=120, revolutions=2.5, n_phi=32):
    """Dibuja una concha espiral en un eje 3D."""
    shell = generate_shell(
        W=W, D=D, T=T, S=S, rho=rho,
        steps=steps, revolutions=revolutions, r0=1.0, n_phi=n_phi
    )
    for i, ring in enumerate(shell):
        x = [pt[0] for pt in ring]
        y = [pt[1] for pt in ring]
        z = [pt[2] for pt in ring]
        # Cerrar el anillo
        x.append(x[0])
        y.append(y[0])
        z.append(z[0])
        alpha = 0.2 + 0.8 * (i / len(shell))
        ax.plot(x, y, z, color=color, alpha=alpha, linewidth=0.8)


def vista_clasica(guardar=False):
    """Vista de una concha clásica con rotación interactiva."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0a0e27')
    dibujar_concha(ax, W=2.0, D=0.35, T=0.12, S='circle', rho=1.0, color='#4ECDC4')
    ax.set_title('Concha Clásica (W=2.0, D=0.35, T=0.12)', color='white', fontsize=14)
    ax.set_xlabel('X', color='white')
    ax.set_ylabel('Y', color='white')
    ax.set_zlabel('Z', color='white')
    ax.tick_params(colors='white')
    plt.tight_layout()
    if guardar:
        plt.savefig('concha_clasica.png', dpi=150, bbox_inches='tight', facecolor='#0a0e27')
        print("Guardado: concha_clasica.png")
    else:
        plt.show()


def vista_torre(guardar=False):
    """Vista de concha tipo torre alta."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0a0e27')
    dibujar_concha(ax, W=1.7, D=0.22, T=0.55, S='ellipse', rho=1.3, color='#FF6B6B')
    ax.set_title('Torre Alta (W=1.7, D=0.22, T=0.55)', color='white', fontsize=14)
    ax.set_xlabel('X', color='white')
    ax.set_ylabel('Y', color='white')
    ax.set_zlabel('Z', color='white')
    ax.tick_params(colors='white')
    plt.tight_layout()
    if guardar:
        plt.savefig('concha_torre.png', dpi=150, bbox_inches='tight', facecolor='#0a0e27')
        print("Guardado: concha_torre.png")
    else:
        plt.show()


def vista_plana(guardar=False):
    """Vista de concha planispiral (T=0)."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0a0e27')
    dibujar_concha(ax, W=2.3, D=0.35, T=0.0, S='circle', rho=1.0, color='#45B7D1')
    ax.set_title('Planispiral (W=2.3, D=0.35, T=0.0)', color='white', fontsize=14)
    ax.set_xlabel('X', color='white')
    ax.set_ylabel('Y', color='white')
    ax.set_zlabel('Z', color='white')
    ax.tick_params(colors='white')
    plt.tight_layout()
    if guardar:
        plt.savefig('concha_plana.png', dpi=150, bbox_inches='tight', facecolor='#0a0e27')
        print("Guardado: concha_plana.png")
    else:
        plt.show()


def galeria_completa(guardar=False):
    """Galería de 6 morfologías diferentes."""
    configs = [
        {"W": 2.0, "D": 0.35, "T": 0.12, "S": "circle",  "rho": 1.0, "title": "Clásica",          "color": "#FF6B6B"},
        {"W": 1.7, "D": 0.22, "T": 0.55, "S": "ellipse", "rho": 1.3, "title": "Torre Alta",       "color": "#4ECDC4"},
        {"W": 2.3, "D": 0.35, "T": 0.0,  "S": "circle",  "rho": 1.0, "title": "Planispiral",      "color": "#45B7D1"},
        {"W": 3.5, "D": 0.1,  "T": 0.08, "S": "circle",  "rho": 1.0, "title": "Expansión Rápida", "color": "#FFA07A"},
        {"W": 1.3, "D": 0.5,  "T": 0.3,  "S": "ellipse", "rho": 1.5, "title": "Compacta",         "color": "#98D8C8"},
        {"W": 2.5, "D": 0.0,  "T": 0.15, "S": "circle",  "rho": 1.0, "title": "Toca el Eje",      "color": "#F7DC6F"},
    ]

    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor('#0a0e27')

    for idx, cfg in enumerate(configs):
        ax = fig.add_subplot(2, 3, idx + 1, projection='3d')
        ax.set_facecolor('#0a0e27')
        dibujar_concha(
            ax, W=cfg["W"], D=cfg["D"], T=cfg["T"], S=cfg["S"], rho=cfg["rho"],
            color=cfg["color"], steps=120, revolutions=2.5, n_phi=32
        )
        ax.set_title(cfg["title"], color='white', fontsize=12, fontweight='bold')
        ax.tick_params(colors='gray', labelsize=6)

    plt.suptitle('Galería de Morfologías — Modelo de Raup/Filin',
                 color='white', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.95])

    if guardar:
        plt.savefig('galeria_morfologias.png', dpi=150, bbox_inches='tight', facecolor='#0a0e27')
        print("Guardado: galeria_morfologias.png")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description='Visualizador de conchas espirales (Modelo de Raup/Filin)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/visualizar.py              # Galería completa
  python scripts/visualizar.py --clasica    # Solo concha clásica
  python scripts/visualizar.py --guardar    # Guardar PNG sin ventana
        """
    )
    parser.add_argument('--clasica', action='store_true', help='Vista de concha clásica')
    parser.add_argument('--torre', action='store_true', help='Vista de torre alta')
    parser.add_argument('--plana', action='store_true', help='Vista de planispiral')
    parser.add_argument('--guardar', action='store_true', help='Guardar PNG en vez de mostrar ventana')

    args = parser.parse_args()

    if args.clasica:
        vista_clasica(guardar=args.guardar)
    elif args.torre:
        vista_torre(guardar=args.guardar)
    elif args.plana:
        vista_plana(guardar=args.guardar)
    else:
        galeria_completa(guardar=args.guardar)


if __name__ == '__main__':
    main()
