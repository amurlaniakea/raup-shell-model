# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests del modelo. Siempre con argumentos por nombre (W=, D=, T=, rho=) para evitar intercambios."""

import math
import random

import pytest

from model import (
    coiling_params,
    export_to_stl,
    generate_curve,
    generate_shell,
    mesh_shell,
    whorl_overlap,
)


def radius(point):
    return math.hypot(point[0], point[1])


# ============== Autosemejanza y linea central ==============


def test_autosemejanza():
    W, T, steps = 3.0, 0.15, 21  # steps-1 = 20, revolutions=2 => N=10 puntos por vuelta
    curve = generate_curve(W=W, D=0.3, T=T, steps=steps, revolutions=2.0, r0=1.0)
    n = steps // 2
    for i in range(len(curve) - n):
        assert abs(radius(curve[i + n]) - W * radius(curve[i])) < 1e-9
        assert abs(curve[i + n][2] - W * curve[i][2]) < 1e-9


def test_curve_incluye_punto_inicial_y_final():
    curve = generate_curve(W=2.0, D=0.5, T=0.1, steps=5, revolutions=1.0, r0=2.0)
    assert len(curve) == 5
    assert curve[0] == pytest.approx([2.0, 0.0, 0.2])
    assert curve[-1] == pytest.approx([4.0, 0.0, 0.4])  # una vuelta completa: r = r0*W, theta = 2*pi


def test_z_sobre_r_es_T():
    T = 0.4
    for point in generate_curve(W=2.5, D=0.2, T=T, steps=50, revolutions=1.5, r0=2.0):
        assert abs(point[2] / radius(point) - T) < 1e-9


def test_T_cero_planispiral():
    for point in generate_curve(W=2.0, D=0.3, T=0.0, steps=50, revolutions=1.0, r0=1.0):
        assert point[2] == 0.0


def test_W_uno_radio_constante():
    for point in generate_curve(W=1.0, D=0.4, T=0.2, steps=30, revolutions=2.0, r0=3.0):
        assert abs(radius(point) - 3.0) < 1e-9


# ============== Anillos de la concha ==============


def test_shell_dimensiones():
    shell = generate_shell(W=2.0, D=0.5, T=0.1, steps=10, revolutions=1.0, n_phi=16)
    assert len(shell) == 10
    assert all(len(ring) == 16 and all(len(p) == 3 for p in ring) for ring in shell)


def test_anillo_sin_punto_duplicado():
    ring = generate_shell(W=2.0, D=0.3, T=0.1, steps=3, revolutions=0.5, n_phi=64)[1]
    assert max(abs(ring[0][k] - ring[-1][k]) for k in range(3)) > 1e-3


def test_D_afecta_a_la_forma():
    low = generate_shell(W=2.0, D=0.1, T=0.1, steps=5, revolutions=1.0, n_phi=64)
    high = generate_shell(W=2.0, D=0.9, T=0.1, steps=5, revolutions=1.0, n_phi=64)
    ext_low = max(radius(p) for p in low[0]) - min(radius(p) for p in low[0])
    ext_high = max(radius(p) for p in high[0]) - min(radius(p) for p in high[0])
    assert ext_low > 2 * ext_high  # a = r(1-D)/(1+D): mucho mayor con D pequeno


def test_extension_radial_es_2a():
    W, D, r0 = 2.0, 0.3, 1.0
    shell = generate_shell(W=W, D=D, T=0.1, steps=7, revolutions=1.0, r0=r0, n_phi=64)
    for i, ring in enumerate(shell):
        r = r0 * W ** (i / 6)
        a = r * (1 - D) / (1 + D)
        # los puntos phi=0 y phi=pi estan en el plano del radio: R = r + a y R = r - a
        assert abs(radius(ring[0]) - (r + a)) < 1e-9
        assert abs(radius(ring[32]) - (r - a)) < 1e-9


def test_D_cero_toca_el_eje():
    shell = generate_shell(W=2.0, D=0.0, T=0.1, steps=10, revolutions=0.5, r0=1.0, n_phi=64)
    for ring in shell:
        assert min(radius(p) for p in ring) < 1e-9


def test_extension_axial_es_2_rho_a():
    W, D, rho = 2.0, 0.3, 1.5
    shell = generate_shell(W=W, D=D, T=0.1, S="ellipse", rho=rho, steps=5, revolutions=0.5, r0=1.0, n_phi=64)
    for i, ring in enumerate(shell):
        r = W ** (0.5 * i / 4)
        a = r * (1 - D) / (1 + D)
        zs = [p[2] for p in ring]
        assert abs((max(zs) - min(zs)) - 2 * rho * a) < 1e-9


def test_centroide_del_anillo_sigue_la_linea_central():
    W, T, steps, revs = 2.5, 0.35, 9, 1.0
    for S, rho in (("circle", 1.0), ("ellipse", 1.7)):
        shell = generate_shell(W=W, D=0.2, T=T, S=S, rho=rho, steps=steps, revolutions=revs, r0=1.5, n_phi=32)
        curve = generate_curve(W=W, D=0.2, T=T, steps=steps, revolutions=revs, r0=1.5)
        for ring, center in zip(shell, curve):
            centroid = [sum(p[k] for p in ring) / len(ring) for k in range(3)]
            assert centroid == pytest.approx(center, abs=1e-9)


# ============== Solapamiento de vueltas (S8) ==============


def test_frontera_D_0_rho_1():
    W = 3.0
    t_front = 2 * math.sqrt(W) / (W - 1)
    assert whorl_overlap(W=W, D=0.0, T=t_front - 1e-6, rho=1.0) is True
    assert whorl_overlap(W=W, D=0.0, T=t_front + 1e-6, rho=1.0) is False


def test_frontera_T_0():
    W = 3.0
    d_front = 1.0 / W
    assert whorl_overlap(W=W, D=d_front - 1e-6, T=0.0, rho=1.0) is True
    assert whorl_overlap(W=W, D=d_front + 1e-6, T=0.0, rho=1.0) is False


def test_W_uno_solapa_y_es_continuo_con_W_cercano():
    assert whorl_overlap(W=1.0, D=0.3, T=0.1) is True
    assert whorl_overlap(W=1.0001, D=0.3, T=0.1) is True


def _geometric_overlap(W, D, T, rho, n=2000):
    """Segunda implementacion, sin usar S8: la elipse sagital de una vuelta, escalada por W respecto
    al polo, ya contiene algun punto del borde de la elipse de la vuelta anterior?
    (La mayor siempre contiene a la menor o corta su borde, por homotecia.)"""
    r = 1.0
    a = r * (1 - D) / (1 + D)
    b = rho * a
    center_r, center_z = W * r, W * T * r
    for k in range(n):
        phi = 2 * math.pi * k / n
        rr, zz = r + a * math.cos(phi), T * r + b * math.sin(phi)
        if ((rr - center_r) / (W * a)) ** 2 + ((zz - center_z) / (W * b)) ** 2 <= 1.0:
            return True
    return False


def test_overlap_coincide_con_geometria_independiente():
    rng = random.Random(7)
    seen = {True: 0, False: 0}
    checked = 0
    while checked < 150:
        W = 1.2 + rng.random() * 3.5
        D = rng.random() * 0.8
        T = rng.random() * 3.0
        rho = 0.5 + rng.random() * 1.5
        k = (1 - D) / (1 + D)
        rhs = rho**2 * ((k * (W + 1)) ** 2 - (W - 1) ** 2) / (W - 1) ** 2
        boundary = math.sqrt(rhs) if rhs > 0 else 0.0
        if abs(T - boundary) < 0.03 * max(boundary, 0.1):
            continue  # demasiado cerca de la frontera para la discretizacion del borde
        formula = whorl_overlap(W=W, D=D, T=T, rho=rho)
        assert formula == _geometric_overlap(W, D, T, rho), (W, D, T, rho)
        seen[formula] += 1
        checked += 1
    assert seen[True] > 10 and seen[False] > 10  # el test ejercita ambos resultados


# ============== Validacion ==============


@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"W": 0.5}, ValueError),
        ({"W": -1.0}, ValueError),
        ({"W": "dos"}, TypeError),
        ({"W": True}, TypeError),
        ({"W": float("nan")}, ValueError),
        ({"W": float("inf")}, ValueError),
        ({"D": 1.0}, ValueError),
        ({"D": 1.5}, ValueError),
        ({"D": -0.1}, ValueError),
        ({"D": "medio"}, TypeError),
        ({"D": float("nan")}, ValueError),
        ({"T": -0.1}, ValueError),
        ({"T": float("nan")}, ValueError),
        ({"rho": 0}, ValueError),
        ({"rho": -2.0}, ValueError),
        ({"S": "square"}, ValueError),
        ({"S": 3}, TypeError),
        ({"S": "circle", "rho": 2.0}, ValueError),
    ],
)
def test_coiling_params_rechaza(kwargs, error):
    with pytest.raises(error):
        coiling_params(**kwargs)


@pytest.mark.parametrize(
    "kwargs, error",
    [
        ({"steps": 1}, ValueError),
        ({"steps": 0}, ValueError),
        ({"steps": 2.5}, TypeError),
        ({"steps": 2.0}, TypeError),
        ({"steps": True}, TypeError),
        ({"revolutions": -0.5}, ValueError),
        ({"revolutions": 0}, ValueError),
        ({"revolutions": float("nan")}, ValueError),
        ({"r0": -1}, ValueError),
        ({"r0": 0}, ValueError),
        ({"W": 0.5}, ValueError),
        ({"D": 5.0}, ValueError),
        ({"T": -3.0}, ValueError),
    ],
)
def test_generate_curve_y_shell_rechazan(kwargs, error):
    with pytest.raises(error):
        generate_curve(**kwargs)
    with pytest.raises(error):
        generate_shell(**kwargs)


@pytest.mark.parametrize("n_phi, error", [(2, ValueError), (0, ValueError), (3.5, TypeError), (True, TypeError)])
def test_shell_rechaza_n_phi(n_phi, error):
    with pytest.raises(error):
        generate_shell(W=2.0, D=0.3, T=0.1, steps=4, n_phi=n_phi)


def test_whorl_overlap_valida_entradas():
    with pytest.raises(ValueError):
        whorl_overlap(W=0.5, D=0.3, T=0.1)
    with pytest.raises(ValueError):
        whorl_overlap(W=2.0, D=0.3, T=0.1, rho=0.0)
    with pytest.raises(TypeError):
        whorl_overlap(W="2", D=0.3, T=0.1)


def test_compatibilidad_params():
    p = coiling_params(W=2.5, D=0.3, T=0.15)
    assert (p.W, p.D, p.T, p.S, p.rho) == (2.5, 0.3, 0.15, "circle", 1.0)


# ============== Malla (requiere trimesh y numpy) ==============


@pytest.fixture
def small_shell():
    return generate_shell(W=2.0, D=0.3, T=0.1, steps=20, revolutions=1.0, r0=1.0, n_phi=16)


def test_mesh_conteos_y_sin_caras_degeneradas(small_shell):
    pytest.importorskip("trimesh")
    mesh = mesh_shell(small_shell)
    steps, n_phi = len(small_shell), len(small_shell[0])
    assert len(mesh.vertices) == steps * n_phi
    assert len(mesh.faces) == 2 * n_phi * (steps - 1)
    assert int((mesh.area_faces < 1e-12).sum()) == 0
    assert mesh.is_watertight is False  # tubo abierto, documentado


def test_mesh_con_tapas_es_estanca(small_shell):
    pytest.importorskip("trimesh")
    mesh = mesh_shell(small_shell, cap_ends=True)
    steps, n_phi = len(small_shell), len(small_shell[0])
    assert len(mesh.vertices) == steps * n_phi + 2
    assert len(mesh.faces) == 2 * n_phi * (steps - 1) + 2 * n_phi
    assert mesh.is_watertight is True
    assert mesh.is_winding_consistent is True


def test_mesh_valida_entradas(small_shell):
    pytest.importorskip("trimesh")
    with pytest.raises(ValueError):
        mesh_shell(small_shell[:1])
    with pytest.raises(ValueError):
        mesh_shell([ring[:2] for ring in small_shell])
    with pytest.raises(ValueError):
        mesh_shell([small_shell[0], small_shell[1][:-1]])


def test_stl_exportado_conserva_las_caras(small_shell, tmp_path):
    trimesh = pytest.importorskip("trimesh")
    path = tmp_path / "concha.stl"
    export_to_stl(small_shell, str(path))
    assert path.stat().st_size > 0
    loaded = trimesh.load(str(path))
    steps, n_phi = len(small_shell), len(small_shell[0])
    assert len(loaded.faces) == 2 * n_phi * (steps - 1)


def test_mesh_sin_trimesh_da_import_error(small_shell, monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name in ("trimesh", "numpy"):
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ImportError, match="raup-shell-model"):
        mesh_shell(small_shell)
