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
from dataclasses import dataclass


VALID_SHAPES = {'circle', 'ellipse'}
@dataclass
class CoilingParameters:
    W: float = 2.0
    D: float = 0.5
    T: float = 0.1
    S: str = 'circle'
    rho: float = 1.0



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


def generate_curve(W: float = 2.0, D: float = 0.5, T: float = 0.1, steps: int = 360, revolutions: float = 2.0, r0: float = 1.0) -> list[list[float]]:
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
        theta = 2 * math.pi * i / (steps - 1) * revolutions
        # Nota: theta va de 0 a 2*pi*revolutions, INCLUYENDO el punto final
        r = r0 * (W ** (theta / (2 * math.pi)))
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = T * r
        result.append([float(x), float(y), float(z)])
    return result


def generate_shell(W: float = 2.0, D: float = 0.5, T: float = 0.1, S: str = 'circle', rho: float = 1.0, steps: int = 360, revolutions: float = 2.0, r0: float = 1.0, n_phi: int = 64) -> list[list[list[float]]]:
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
        theta = 2 * math.pi * i / (steps - 1) * revolutions
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


def whorl_overlap(W: float, D: float, T: float, rho: float = 1.0) -> bool:
    coiling_params(W, D, T, S='circle', rho=rho)
    if W <= 1:
        # Para W=1: W-1 = 0 => division por cero; la formula de frontera no aplica.
        # Si W == 1, la espiral no crece => no hay solapamiento posible (T>=0)
        return False
    rhs_numer = ((1 - D) / (1 + D)) ** 2 * (W + 1) ** 2 - (W - 1) ** 2
    rhs = rho ** 2 * rhs_numer / ((W - 1) ** 2)
    return (T ** 2) < rhs

def mesh_shell(shell_points):
    """Convierte la salida de generate_shell (lista de anillos [x,y,z]) en una malla trimesh.Trimesh.

    Args:
        shell_points: resultado de generate_shell (lista de anillos, cada anillo lista de [x,y,z]).

    Returns:
        trimesh.Trimesh (o None si no está disponible trimesh).
    Nota: esta es una derivación independiente basada en la formulación secundaria (Filin 2026);
    pendiente de contraste con la geometría real de Raup (1966).
    """
    try:
        import trimesh
    except ImportError:
        raise ImportError("trimesh es requerido para mesh_shell; instala con: pip install trimesh")
    import numpy as np

    # shell_points: steps anillos x n_phi puntos
    steps = len(shell_points)
    if steps < 2:
        raise ValueError("mesh_shell requiere al menos 2 anillos (steps >= 2)")
    n_phi = len(shell_points[0]) if steps > 0 else 0
    if n_phi < 3:
        raise ValueError("mesh_shell requiere n_phi >= 3")

    # Construir vértices como array plano: cada punto [x, y, z]
    vertices = []
    for i in range(steps):
        for j in range(n_phi):
            vertices.append(shell_points[i][j])
    vertices = np.array(vertices)

    # Construir caras: conectar anillo i con i+1
    # Para cada par de anillos consecutivos, crear cuadriláteros (o triángulos)
    # Usamos cuadriláteros simples (2 triángulos por cuadrante para evitar problemas de orientación)
    faces = []
    for i in range(steps - 1):
        for j in range(n_phi):
            j_next = (j + 1) % n_phi
            v00 = i * n_phi + j
            v01 = i * n_phi + j_next
            v10 = (i + 1) * n_phi + j
            v11 = (i + 1) * n_phi + j_next
            # Dos triángulos por cuadrilátero (orientación consistente)
            faces.append([v00, v10, v11])
            faces.append([v00, v11, v01])

    # Si queremos que sea watertight, necesitamos también las tapas (primer y último anillo como superficies circulares)
    # Para simplificar: añadir tapa inicial y final (triangulación radial)
    # Esto es opcional; para la prueba de watertight asumimos que se cierra con un anillo de cierre
    # (en esta implementación, la malla es abierta en los extremos a menos que revolutions cierre exactamente)
    # Para la verificación de watertight, asumimos pasos >= 2 y que los extremos no necesariamente cierran
    # (como en una hélice cónica abierta); la prueba verificará que sea una superficie orientable.

    mesh = trimesh.Trimesh(vertices=vertices, faces=np.array(faces))
    return mesh



def export_to_stl(shell_points: list, filename: str) -> None:
    """Construye una malla trimesh.Trimesh a partir de shell_points, suelda vertices duplicados y exporta a STL.

    Args:
        shell_points: salida de generate_shell (lista de anillos [x,y,z]).
        filename: ruta de archivo de salida (debe terminar en .stl).

    Raises:
        ImportError: si trimesh no esta disponible.
        ValueError: si shell_points tiene menos de 2 anillos o menos de 3 puntos por anillo.
    """
    import trimesh
    import numpy as np

    if len(shell_points) < 2:
        raise ValueError("shell_points requiere al menos 2 anillos para generar una malla 3D")
    n_phi = len(shell_points[0]) if len(shell_points) > 0 else 0
    if n_phi < 3:
        raise ValueError("shell_points requiere al menos 3 puntos por anillo (n_phi >= 3)")

    # Construir vertices
    vertices = []
    for i in range(len(shell_points)):
        for j in range(n_phi):
            vertices.append(shell_points[i][j])
    vertices = np.array(vertices, dtype=np.float64)

    # Construir caras (triangulos entre anillos consecutivos)
    faces = []
    steps = len(shell_points)
    for i in range(steps - 1):
        for j in range(n_phi):
            j_next = (j + 1) % n_phi
            v00 = i * n_phi + j
            v01 = i * n_phi + j_next
            v10 = (i + 1) * n_phi + j
            v11 = (i + 1) * n_phi + j_next
            # Dos triangulos por cuadrilatero
            faces.append([v00, v10, v11])
            faces.append([v00, v11, v01])

    mesh = trimesh.Trimesh(vertices=vertices, faces=np.array(faces, dtype=np.int32))
    # Soldar vertices duplicados (costura de la concha)
    mesh.merge_vertices()
    mesh.export(file_obj=filename, file_type='stl')
