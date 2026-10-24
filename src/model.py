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

Decisiones de diseno (no proceden de la fuente):
  * W < 1 (contraccion) se rechaza; W == 1 es valido (circulo / helice degenerada).
  * S='circle' exige rho == 1; S='ellipse' admite cualquier rho > 0.
  * whorl_overlap(W=1) devuelve True: las vueltas coinciden (limite W -> 1+ de S8).
"""

import math
from dataclasses import dataclass
from typing import Any

VALID_SHAPES = frozenset({"circle", "ellipse"})


@dataclass
class CoilingParameters:
    W: float = 2.0
    D: float = 0.5
    T: float = 0.1
    S: str = "circle"
    rho: float = 1.0


def _finite_number(name: str, value: object) -> float:
    """Devuelve value como float; rechaza no numericos, bool, NaN e infinitos."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} debe ser numerico, recibido {type(value).__name__}")
    if not math.isfinite(value):
        raise ValueError(f"{name} debe ser finito, recibido {value}")
    return float(value)


def _integer(name: str, value: object, minimum: int) -> int:
    """Valida un entero (no bool) >= minimum."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} debe ser int, recibido {type(value).__name__}")
    if value < minimum:
        raise ValueError(f"{name} >= {minimum} requerido, recibido {value}")
    return value


def coiling_params(
    W: float = 2.0, D: float = 0.5, T: float = 0.1, S: str = "circle", rho: float = 1.0
) -> CoilingParameters:
    """Valida y agrupa los parametros del modelo. Lanza TypeError o ValueError."""
    W = _finite_number("W", W)
    D = _finite_number("D", D)
    T = _finite_number("T", T)
    rho = _finite_number("rho", rho)
    if not isinstance(S, str):
        raise TypeError(f"S debe ser str, recibido {type(S).__name__}")
    if S not in VALID_SHAPES:
        raise ValueError(f"S debe ser uno de {sorted(VALID_SHAPES)}, recibido '{S}'")
    if W < 1:
        raise ValueError(f"W >= 1 requerido (W={W}); W < 1 implica contraccion, no soportado (decision de diseno)")
    if not (0 <= D < 1):
        raise ValueError(f"0 <= D < 1 requerido, recibido D={D}")
    if T < 0:
        raise ValueError(f"T >= 0 requerido, recibido T={T}")
    if rho <= 0:
        raise ValueError(f"rho > 0 requerido, recibido rho={rho}")
    if S == "circle" and rho != 1.0:
        raise ValueError(f"S='circle' exige rho == 1, recibido rho={rho}; usa S='ellipse'")
    return CoilingParameters(W=W, D=D, T=T, S=S, rho=rho)


def _sampling(steps: int, revolutions: float, r0: float) -> tuple[int, float, float]:
    steps = _integer("steps", steps, 2)
    revolutions = _finite_number("revolutions", revolutions)
    r0 = _finite_number("r0", r0)
    if revolutions <= 0:
        raise ValueError(f"revolutions > 0 requerido, recibido {revolutions}")
    if r0 <= 0:
        raise ValueError(f"r0 > 0 requerido, recibido {r0}")
    return steps, revolutions, r0


def _theta_and_radius(i: int, steps: int, revolutions: float, W: float, r0: float) -> tuple[float, float]:
    """theta va de 0 a 2*pi*revolutions INCLUYENDO el punto final; r = r0 * W**(theta/2pi)."""
    theta = 2 * math.pi * revolutions * i / (steps - 1)
    return theta, r0 * W ** (theta / (2 * math.pi))


def generate_curve(
    W: float = 2.0, D: float = 0.5, T: float = 0.1, steps: int = 360, revolutions: float = 2.0, r0: float = 1.0
) -> list[list[float]]:
    """Linea central de la concha: lista de `steps` puntos [x, y, z] con z = T * r."""
    params = coiling_params(W=W, D=D, T=T)
    steps, revolutions, r0 = _sampling(steps, revolutions, r0)
    result: list[list[float]] = []
    for i in range(steps):
        theta, r = _theta_and_radius(i, steps, revolutions, params.W, r0)
        result.append([r * math.cos(theta), r * math.sin(theta), params.T * r])
    return result


def generate_shell(
    W: float = 2.0,
    D: float = 0.5,
    T: float = 0.1,
    S: str = "circle",
    rho: float = 1.0,
    steps: int = 360,
    revolutions: float = 2.0,
    r0: float = 1.0,
    n_phi: int = 64,
) -> list[list[list[float]]]:
    """Superficie de la concha: `steps` anillos de `n_phi` puntos [x, y, z] cada uno.

    La apertura se define en el plano sagital (r, z): R = r + a*cos(phi), Z = T*r + rho*a*sin(phi),
    con a = r*(1-D)/(1+D). Los puntos de cada anillo NO repiten el primero al final
    (phi = 2*pi*j/n_phi, j = 0..n_phi-1); la costura se cierra con j_next = (j+1) % n_phi.
    """
    params = coiling_params(W=W, D=D, T=T, S=S, rho=rho)
    steps, revolutions, r0 = _sampling(steps, revolutions, r0)
    n_phi = _integer("n_phi", n_phi, 3)
    shell: list[list[list[float]]] = []
    for i in range(steps):
        theta, r = _theta_and_radius(i, steps, revolutions, params.W, r0)
        a = r * (1 - params.D) / (1 + params.D)
        z_center = params.T * r
        ring: list[list[float]] = []
        for j in range(n_phi):
            phi = 2 * math.pi * j / n_phi
            big_r = r + a * math.cos(phi)
            z = z_center + params.rho * a * math.sin(phi)
            ring.append([big_r * math.cos(theta), big_r * math.sin(theta), z])
        shell.append(ring)
    return shell


def whorl_overlap(W: float, D: float, T: float, rho: float = 1.0) -> bool:
    """True si las aperturas de dos vueltas consecutivas se solapan (S8, Filin 2026).

    Con W == 1 las vueltas coinciden, asi que devuelve True (limite de S8 cuando W -> 1+, D < 1).
    """
    params = coiling_params(W=W, D=D, T=T, S="ellipse", rho=rho)
    if params.W == 1.0:
        return True
    k = (1 - params.D) / (1 + params.D)
    rhs = params.rho ** 2 * ((k * (params.W + 1)) ** 2 - (params.W - 1) ** 2) / (params.W - 1) ** 2
    return params.T ** 2 < rhs


def _build_mesh(shell_points: list[list[list[float]]], cap_ends: bool = False) -> Any:
    """Malla trimesh.Trimesh a partir de la salida de generate_shell.

    Sin tapas la malla es un tubo abierto (is_watertight == False). Con cap_ends=True se cierran
    ambos extremos con abanicos de triangulos (is_watertight == True). Si whorl_overlap(...) es True,
    las vueltas se autointersecan y la malla no es un solido valido.

    Raises:
        ImportError: si trimesh o numpy no estan instalados (pip install "raup-shell-model[mesh]").
        ValueError: con menos de 2 anillos, menos de 3 puntos por anillo o anillos de distinto tamano.
    """
    try:
        import numpy as np
        import trimesh
    except ImportError as exc:
        raise ImportError('trimesh y numpy son necesarios para la malla: pip install "raup-shell-model[mesh]"') from exc

    steps = len(shell_points)
    if steps < 2:
        raise ValueError("se requieren al menos 2 anillos (steps >= 2)")
    n_phi = len(shell_points[0])
    if n_phi < 3:
        raise ValueError("se requieren al menos 3 puntos por anillo (n_phi >= 3)")
    if any(len(ring) != n_phi for ring in shell_points):
        raise ValueError("todos los anillos deben tener el mismo numero de puntos")

    vertices = [point for ring in shell_points for point in ring]
    faces = []
    for i in range(steps - 1):
        for j in range(n_phi):
            j_next = (j + 1) % n_phi
            v00 = i * n_phi + j
            v01 = i * n_phi + j_next
            v10 = (i + 1) * n_phi + j
            v11 = (i + 1) * n_phi + j_next
            faces.append([v00, v10, v11])
            faces.append([v00, v11, v01])

    if cap_ends:
        for ring_index, reverse in ((0, False), (steps - 1, True)):
            ring = shell_points[ring_index]
            centroid = [sum(p[k] for p in ring) / n_phi for k in range(3)]
            centroid_index = len(vertices)
            vertices.append(centroid)
            for j in range(n_phi):
                a = ring_index * n_phi + j
                b = ring_index * n_phi + (j + 1) % n_phi
                faces.append([centroid_index, b, a] if reverse else [centroid_index, a, b])

    return trimesh.Trimesh(
        vertices=np.array(vertices, dtype=np.float64),
        faces=np.array(faces, dtype=np.int64),
        process=False,
    )


def mesh_shell(shell_points: list[list[list[float]]], cap_ends: bool = False) -> Any:
    """Devuelve una trimesh.Trimesh de la concha (ver _build_mesh)."""
    return _build_mesh(shell_points, cap_ends=cap_ends)


def export_to_stl(shell_points: list[list[list[float]]], filename: str, cap_ends: bool = False) -> None:
    """Exporta la concha a un archivo STL (ver _build_mesh para ImportError y ValueError)."""
    _build_mesh(shell_points, cap_ends=cap_ends).export(file_obj=filename, file_type="stl")
