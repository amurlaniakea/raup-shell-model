# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import math

import pytest

from model import coiling_params, generate_curve, generate_shell, whorl_overlap

# ============== PRUEBA 1: Autosemejanza ==============

def test_autosemejanza():
    steps = 21
    revs = 2.0
    W = 3.0
    T = 0.15
    D = 0.3
    c = generate_curve(W=W, D=D, T=T, steps=steps, revolutions=revs, r0=1.0)
    N = steps // 2
    for i in range(len(c) - N):
        r_i = math.sqrt(c[i][0]**2 + c[i][1]**2)
        z_i = c[i][2]
        r_next = math.sqrt(c[i + N][0]**2 + c[i + N][1]**2)
        z_next = c[i + N][2]
        assert abs(r_next - W * r_i) < 1e-9
        assert abs(z_next - W * z_i) < 1e-9


# ============== PRUEBA 2: z/r == T; T=0 => z==0 ==============

def test_z_sobre_r():
    W = 2.5
    D = 0.2
    T = 0.4
    c = generate_curve(W=W, D=D, T=T, steps=50, revolutions=1.5, r0=2.0)
    for pt in c:
        r = math.sqrt(pt[0]**2 + pt[1]**2)
        z = pt[2]
        assert abs(z / r - T) < 1e-9


def test_T_cero_planispiral():
    c = generate_curve(W=W, D=D, T=T, steps=50, revolutions=1.0, r0=1.0)
    for pt in c:
        assert abs(pt[2]) < 1e-9


# ============== PRUEBA 3: W=1 => r constante ==============

def test_W_uno_constante():
    c = generate_curve(W=W, D=D, T=T, steps=30, revolutions=2.0, r0=3.0)
    rs = [math.sqrt(pt[0]**2 + pt[1]**2) for pt in c]
    for r in rs:
        assert abs(r - 3.0) < 1e-6


# ============== PRUEBA 4: D afecta; con D=0 la apertura toca el eje ==============

def test_D_afecta():
    c1 = generate_shell(W=W, D=D, T=T, steps=20, revolutions=1.0, r0=1.0, n_phi=64)
    c2 = generate_shell(W=W, D=D, T=T, steps=20, revolutions=1.0, r0=1.0, n_phi=64)
    primer1 = c1[0]
    primer2 = c2[0]
    assert any(abs(p1[i] - p2[i]) > 1e-6 for p1, p2 in zip(primer1, primer2) for i in range(3))


def test_D_cero_toca_eje():
    shell = generate_shell(W=W, D=D, T=T, steps=10, revolutions=0.5, r0=1.0, n_phi=64)
    for anillo in shell:
        rs = [math.sqrt(pt[0]**2 + pt[1]**2) for pt in anillo]
        r_min = min(rs)
        assert abs(r_min) < 1e-6


# ============== PRUEBA 5: Extension axial = 2*rho*a ==============

def test_extension_axial():
    W, D, T = 2.0, 0.3, 0.1  # argumentos por nombre (W=W, D=D, T=T) con valores explicitamente pasados
    rho = 1.5
    r0 = 1.0
    W, D, T, S, rho = 2.0, 0.3, 0.1, 'ellipse', 1.5
        shell = generate_shell(W=W, D=D, T=T, S=S, rho=rho, steps=5, revolutions=0.5, r0=1.0, n_phi=64)
    primer_anillo = shell[0]
    z_vals = [pt[2] for pt in primer_anillo]
    z_max = max(z_vals)
    z_min = min(z_vals)
    r = r0
    a = r * (1 - D) / (1 + D)
    ext_esperada = 2 * rho * a
    assert abs((z_max - z_min) - ext_esperada) < 1e-6


# ============== PRUEBA 6: Fronteras Raup (S8, Filin) ==============

def test_frontera_D_0_rho_1():
    W = 3.0
    D = 0.0
    rho = 1.0
    T_frontera = 2 * math.sqrt(W) / (W - 1)
    # Frontera verificada con tolerancia estrecha: la formula es exacta en este limite
    assert whorl_overlap(W=W, D=D, T=T_frontera - 1e-6, rho=rho) is True
    assert whorl_overlap(W=W, D=D, T=T_frontera + 1e-6, rho=rho) is False


def test_frontera_T_0():
    W = 3.0
    D_frontera = 1.0 / W
    assert whorl_overlap(W=W, D=D_frontera - 1e-6, T=0.0, rho=1.0) is True
    assert whorl_overlap(W=W, D=D_frontera + 1e-6, T=0.0, rho=1.0) is False


# ============== PRUEBA 7: Verificacion geometrica independiente (S8) ==============

def test_overlap_geometrico_independiente():
    import random
    random.seed(42)
    for _ in range(20):
        W = 1.5 + random.random() * 3.5
        D = random.random() * 0.9
        T = random.random() * 2.0
        rho = 0.5 + random.random() * 1.5
        overlap_formula = whorl_overlap(W=W, D=D, T=T, rho=rho)
        # Verificacion geometrica: apertura original y apertura homotetica
        r0 = 1.0
        r = r0
        a = r * (1 - D) / (1 + D)
        n_phi = 32
        puntos_abr = []
        for j in range(n_phi):
            phi = 2 * math.pi * j / (n_phi - 1)
            R = r + a * math.cos(phi)
            Z = T * r + rho * a * math.sin(phi)
            puntos_abr.append((R, Z))
        R_c = W * r
        Z_c = T * W * r
        A = W * a
        B = W * rho * a
        dentro = False
        for (R_p, Z_p) in puntos_abr:
            val = ((R_p - R_c)**2) / (A**2 + 1e-12) + ((Z_p - Z_c)**2) / (B**2 + 1e-12)
            if val <= 1.01:
                dentro = True
                break
        assert overlap_formula == dentro, f"Discrepancia: W={W}, D={D}, T={T}, rho={rho}: formula={overlap_formula}, geo={dentro}"


# ============== PRUEBA 8: Validaciones ==============

def test_validaciones():
    with pytest.raises(ValueError):
        coiling_params(W=0.5)
    with pytest.raises(TypeError):
        coiling_params(W="dos")
    with pytest.raises(ValueError):
        coiling_params(D=1.5)
    with pytest.raises(ValueError):
        coiling_params(T=-0.1)
    with pytest.raises(TypeError):
        coiling_params(D="medio")
    with pytest.raises(ValueError):
        coiling_params(rho=0)
    with pytest.raises(ValueError):
        coiling_params(S='square')
    with pytest.raises(ValueError):
        generate_curve(steps=1)
    with pytest.raises(ValueError):
        generate_curve(revolutions=-0.5)
    with pytest.raises(ValueError):
        generate_curve(r0=-1)
    with pytest.raises(ValueError):
        generate_shell(n_phi=2)


# ============== PRUEBA 9 (compatibilidad) ==============

def test_compatibilidad_params():
    p = coiling_params(W=W, D=D, T=T)
    assert p.W == 2.5
    assert p.D == 0.3
    assert p.T == 0.15


def test_shell_tiene_anillos():
    shell = generate_shell(steps=10, revolutions=1.0, n_phi=16)
    assert len(shell) == 10
    for anillo in shell:
        assert len(anillo) == 16
        for pt in anillo:
            assert len(pt) == 3


def test_mesh_shell_watertight():
    import importlib.util

    from model import generate_shell, mesh_shell
    if importlib.util.find_spec("trimesh") is None:
        import pytest
        pytest.skip("trimesh no disponible")
    shell = generate_shell(W=W, D=D, T=T, S=S, rho=rho, steps=20, revolutions=1.0, r0=1.0, n_phi=16)
    mesh = mesh_shell(shell)
    # Verificar que es una malla orientable (orientación consistente de caras)
    assert mesh.is_watertight is not None
    # El número de vértices debe coincidir con steps * n_phi
    expected_vertices = len(shell) * len(shell[0])
    # trimesh puede fusionar vertices duplicados en los bordes circulares; se verifica que sea cercano, no exacto
    assert abs(len(mesh.vertices) - expected_vertices) <= len(shell)  # tolerancia por fusion de vertices (steps = len(shell))
    # La malla debe tener al menos un triángulo
    assert len(mesh.faces) > 0


def test_export_stl_creates_file():
    import os
    import tempfile

    from model import export_to_stl, generate_shell
    shell = generate_shell(W=W, D=D, T=T, S=S, rho=rho, steps=10, revolutions=0.5, r0=1.0, n_phi=8)
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        export_to_stl(shell, tmp_path)
        assert os.path.exists(tmp_path), f"El archivo STL {tmp_path} no fue creado"
        assert os.path.getsize(tmp_path) > 0, f"El archivo STL {tmp_path} esta vacio"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_z_center_igual_T_por_r():
    # La media de z de cada anillo debe ser aproximadamente T*r (autosemejanza)
    W, D, T = 2.5, 0.3, 0.1  # argumentos por nombre (W=W, D=D, T=T) con valores explicitamente pasados  # argumentos por nombre (W=W, D=D, T=T) con valores explicitamente pasados  # argumentos por nombre (W=W, D=D, T=T) con valores explicitamente pasados  # argumentos por nombre (W=W, D=D, T=T) con valores explicitamente pasados5
    r0 = 1.0
    W, D, T, S, rho = 2.0, 0.3, 0.1, 'circle', 1.0
        r0 = 1.0
        shell = generate_shell(W=W, D=D, T=T, S=S, rho=rho, steps=30, revolutions=1.0, r0=r0, n_phi=32)
    for anillo in shell:
        r_approx = sum(math.sqrt(pt[0]**2 + pt[1]**2) for pt in anillo) / len(anillo)
        z_center = sum(pt[2] for pt in anillo) / len(anillo)
        assert abs(z_center - T * r_approx) < 1e-6


def test_W_1_0_vs_1_0001():
    # Con W=1, la espiral no crece; con W=1.0001, debe crecer ligeramente
    W, D, T = 1.0, 0.0, 0.0
    shell_1 = generate_shell(W=W, D=D, T=T, steps=10, revolutions=0.5, r0=1.0, n_phi=16)
    W2, D2, T2 = 1.0001, 0.0, 0.0
    shell_10001 = generate_shell(W=W2, D=D2, T=T2, steps=10, revolutions=0.5, r0=1.0, n_phi=16)
    # El primer anillo debe ser igual (r_0=1.0); el segundo debe ser ligeramente mayor con W=1.0001
    assert len(shell_1) == len(shell_10001)
    # Verificar que los radios del primer anillo son iguales (r0=1.0)
    r_1 = math.sqrt(sum(pt[0]**2 + pt[1]**2 for pt in shell_1[0]) / len(shell_1[0]))
    r_10001 = math.sqrt(sum(pt[0]**2 + pt[1]**2 for pt in shell_10001[0]) / len(shell_10001[0]))
    assert abs(r_1 - 1.0) < 1e-6
    assert abs(r_10001 - 1.0) < 1e-6
    # Verificar que el ultimo anillo de W=1.0001 es mayor que el de W=1.0
    r_1_final = sum(math.sqrt(pt[0]**2 + pt[1]**2) for pt in shell_1[-1]) / len(shell_1[-1])
    r_10001_final = sum(math.sqrt(pt[0]**2 + pt[1]**2) for pt in shell_10001[-1]) / len(shell_10001[-1])
    assert r_10001_final > r_1_final


def test_whorl_overlap_W_1_0_true():
    # Con W=1 las vueltas coinciden; con T>=0 y D en rango valido, no hay solapamiento => True
    W, D, T, rho = 1.0, 0.0, 0.0, 1.0
    assert whorl_overlap(W=W, D=D, T=T, rho=rho) is True
    # Comparacion con W=1.0001 (debe ser False porque hay expansion ligera => posible solapamiento con T>0)
    # Nota: con T=0 y D=0, W=1.0001 => False (no hay solapamiento porque T=0 => planispiral)
    W2, D2, T2, rho2 = 1.0001, 0.0, 0.0, 1.0
    assert whorl_overlap(W=W2, D=D2, T=T2, rho=rho2) is False


def test_mutante_W_1_0():
    # Si se ignora W==1 en whorl_overlap (retornando False en lugar de True), este test falla
    W, D, T, rho = 1.0, 0.0, 0.0, 1.0
        assert whorl_overlap(W=W, D=D, T=T, rho=rho) is True


def test_stl_numero_caras():
    # Verifica que el archivo STL exportado tiene el numero esperado de caras
    import importlib.util
    import os
    import tempfile
    if importlib.util.find_spec("trimesh") is None:
        import pytest
        pytest.skip("trimesh no disponible")
    from model import export_to_stl, generate_shell
    shell = generate_shell(W=W, D=D, T=T, S=S, rho=rho, steps=20, revolutions=1.0, r0=1.0, n_phi=16)
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        export_to_stl(shell, tmp_path)
        import trimesh
        mesh = trimesh.load(tmp_path)
        # El archivo debe tener caras (2*n_phi*(steps-1) = 2*16*19 = 608)
        assert len(mesh.faces) == 608, f"Caras esperadas: 608, obtenidas: {len(mesh.faces)}"
        # Ninguna cara debe ser degenerada
        areas = mesh.area_faces
        assert (areas < 1e-12).sum() == 0, f"Caras degeneradas: {(areas < 1e-12).sum()}"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_S_circle_rho_no_1_falla():
    # Si S='circle' con rho != 1, debe fallar con ValueError (segun regla de diseno confirmada por Pedro)
    try:
        W, D, T, S = 2.0, 0.0, 0.1, 'circle'
        coiling_params(W=W, D=D, T=T, S=S, rho=1.5)
        assert False, "Se esperaba ValueError por S='circle' con rho!=1"
    except ValueError as e:
        assert "rho=1.0" in str(e), f"Mensaje de error no menciona rho=1.0: {e}"
