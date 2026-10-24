# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Modelo geometrico de enrollamiento espiral (Raup, 1961-1966).

Formulacion SECUNDARIA (Filin 2026, doi:10.32942/X28Q23, SI S3-S8);
pendiente de contraste con Raup (1966, J. Paleontol. 40(5):1178-1190).

Ecuaciones (S3-S8, Filin 2026):
  r(theta) = r0 * W**(theta / (2*pi))          (S3)
  z = T * r  (helice conica: r = z * tan(beta); T = cot(beta))   (S4)
  D = (r - a) / (r + a) => a = r*(1-D)/(1+D)   (S5, S6)
  xi = r - a = r * 2*D / (1 + D)  (radio interior)
  rho = b / a  (razon ejes de apertura; a radial, b axial)
  Solapamiento (S8): T**2 < rho**2 * [((1-D)/(1+D))**2*(W+1)**2 - (W-1)**2] / (W-1)**2
  Fronteras (Raup 1966, citadas por Filin): D=0, rho=1 => T = 2*sqrt(W)/(W-1);
                                             T=0 => D < 1/W.

Nota de convencion: Filin indica que los valores de T publicados pueden
requerir duplicarse para corresponder a la linea central (Davoli y Russo 1974).
"""
import math

VALID_SHAPES = {'circle', 'ellipse'}


def coiling_params(W=2.0, D=0.5, T=0.1, S='circle', rho=1.0):
    if not isinstance(W, (int, float)):
        raise TypeError(f"W debe ser numerico, recibido {type(W)}")
    if not isinstance(D, (int, float)):
        raise TypeError(f"D debe ser numerico, recibido {type(D)}")
    if not isinstance(T, (int, float)):
        raise TypeError(f"T debe ser numerico, recibido {type(T)}")
    if not isinstance(S, str):
        raise TypeError(f"S debe ser str, recibido {type(S)}")
    if S not in VALID_SHAPES:
        raise ValueError(f"S debe ser uno de {VALID_SHAPES}, recibido '{S}'")
    if not isinstance(rho, (int, float)):
        raise TypeError(f"rho debe ser numerico, recibido {type(rho)}")
    if W < 1:
        raise ValueError(f"W >= 1 requerido (W={W}); W < 1 implica contraccion, no soportado (decision de diseno)")
    if not (0 <= D < 1):
        raise ValueError(f"0 <= D < 1 requerido, recibido D={D}")
    if T < 0:
        raise ValueError(f"T >= 0 requerido, recibido T={T}")
    if rho <= 0:
        raise ValueError(f"rho > 0 requerido, recibido rho={rho}")
    return {'W': float(W), 'D': float(D), 'T': float(T), 'S': S, 'rho': float(rho)}


def generate_curve(W=2.0, D=0.5, T=0.1, steps=360, revolutions=2.0, r0=1.0):
    if not isinstance(steps, int) or not isinstance(steps, (int, float)):
        raise TypeError("steps debe ser int >= 2")
    if isinstance(steps, float) and not steps.is_integer():
        raise TypeError("steps debe ser entero")
    steps = int(steps)
    if steps < 2:
        raise ValueError(f"steps >= 2 requerido, recibido {steps}")
    if revolutions <= 0:
        raise ValueError(f"revolutions > 0 requerido, recibido {revolutions}")
    if r0 <= 0:
        raise ValueError(f"r0 > 0 requerido, recibido {r0}")
    result = []
    for i in range(steps):
        theta = 2 * math.pi * i / (steps - 1) * (revolutions / 2.0)
        # Nota: theta va de 0 a 2*pi*revolutions, INCLUYENDO el punto final
        r = r0 * (W ** (theta / (2 * math.pi)))
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = T * r
        result.append([float(x), float(y), float(z)])
    return result


def generate_shell(W=2.0, D=0.5, T=0.1, S='circle', rho=1.0, steps=360, revolutions=2.0, r0=1.0, n_phi=64):
    coiling_params(W, D, T, S, rho)
    if not isinstance(n_phi, int):
        raise TypeError("n_phi debe ser int")
    n_phi = int(n_phi)
    if n_phi < 3:
        raise ValueError(f"n_phi >= 3 requerido, recibido {n_phi}")
    # Linea central (generate_curve ya valida W,D,T)
    # Anillos: para cada theta, calcular a y generar puntos de apertura
    result = []  # lista de anillos, cada anillo lista de [x,y,z]
    for i in range(steps):
        theta = 2 * math.pi * i / (steps - 1) * (revolutions / 2.0)
        r = r0 * (W ** (theta / (2 * math.pi)))
        a = r * (1 - D) / (1 + D)
        z_center = T * r
        anillo = []
        for j in range(n_phi):
            phi = 2 * math.pi * j / (n_phi - 1)
            # Apertura en plano sagital: R en radial, Z en axial
            R = r + a * math.cos(phi)
            Z = z_center + (rho * a) * math.sin(phi) if S == 'ellipse' else z_center
            # Para 'circle': rho=1, la apertura es circular => R = r + a*cos(phi), Z = z_center + a*sin(phi)
            # Para consistencia con rho: Z usa rho*a
            Z = z_center + (rho * a) * math.sin(phi)
            x = R * math.cos(theta)
            y = R * math.sin(theta)
            z = Z
            anillo.append([float(x), float(y), float(z)])
        result.append(anillo)
    return result


def whorl_overlap(W, D, T, rho=1.0):
    coiling_params(W, D, T, S='circle', rho=rho)
    if W <= 1:
        # Para W=1: W-1 = 0 => division por cero; la formula de frontera no aplica.
        # Si W == 1, la espiral no crece => no hay solapamiento posible (T>=0)
        return False
    rhs_numer = ((1 - D) / (1 + D)) ** 2 * (W + 1) ** 2 - (W - 1) ** 2
    rhs = rho ** 2 * rhs_numer / ((W - 1) ** 2)
    return (T ** 2) < rhs
