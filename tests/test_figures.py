# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""La figura del README sale del modelo: estos tests fallan si se desincroniza o si el modelo cambia."""

import math
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import render_figures as rf

ROOT = Path(__file__).resolve().parent.parent
SVG = "{http://www.w3.org/2000/svg}"


def test_la_figura_del_repo_coincide_con_el_modelo():
    assert (ROOT / "assets" / "concha-espiral.svg").read_text(encoding="utf-8") == rf.build_svg()


def test_build_svg_es_determinista():
    assert rf.build_svg() == rf.build_svg()


def test_svg_es_xml_valido_con_tres_conchas_y_dos_vistas():
    root = ET.fromstring(rf.build_svg().encode("utf-8"))
    assert root.tag == SVG + "svg"
    ids = {g.get("id") for g in root.iter(SVG + "g")}
    for letter in "ABC":
        assert {f"concha-{letter}", f"vista-superior-{letter}", f"corte-sagital-{letter}"} <= ids


@pytest.mark.parametrize("cfg", rf.CONFIGS)
def test_aperturas_del_corte_coinciden_con_el_modelo(cfg):
    data = rf.panel_data(cfg)
    W, D, T, rho = cfg["W"], cfg["D"], cfg["T"], cfg["rho"]
    assert len(data["apertures"]) == rf.SECTION_WHORLS
    for k, aperture in enumerate(data["apertures"]):
        r = W**k
        a = r * (1 - D) / (1 + D)
        radial = [p[0] for p in aperture]
        axial = [p[1] for p in aperture]
        assert max(radial) == pytest.approx(r + a, abs=1e-9)
        assert min(radial) == pytest.approx(r - a, abs=1e-9)
        assert (max(axial) + min(axial)) / 2 == pytest.approx(T * r, abs=1e-9)
        assert max(axial) - min(axial) == pytest.approx(2 * rho * a, abs=1e-9)
    for k, (x, z) in enumerate(data["centers"]):
        assert x == pytest.approx(W**k, abs=1e-9)
        assert z == pytest.approx(T * W**k, abs=1e-9)


@pytest.mark.parametrize("cfg", rf.CONFIGS)
def test_bordes_de_la_vista_superior(cfg):
    data = rf.panel_data(cfg)
    D = cfg["D"]
    for (ox, oy), (ix, iy), (cx, cy) in zip(data["outer"], data["inner"], data["centerline"], strict=True):
        r = math.hypot(cx, cy)
        a = r * (1 - D) / (1 + D)
        assert math.hypot(ox, oy) == pytest.approx(r + a, abs=1e-9)
        assert math.hypot(ix, iy) == pytest.approx(r - a, abs=1e-9)


def test_las_tres_conchas_muestran_los_dos_regimenes():
    assert [rf.panel_data(cfg)["overlap"] for cfg in rf.CONFIGS] == [True, True, False]
    svg = rf.build_svg()
    assert svg.count(">las vueltas se solapan<") == 2
    assert svg.count(">las vueltas no se solapan<") == 1


def test_check_detecta_figura_desactualizada(tmp_path, monkeypatch):
    monkeypatch.setattr(rf, "OUTPUT", str(tmp_path / "figura.svg"))
    assert rf.main(["--check"]) == 1  # no existe
    assert rf.main([]) == 0  # la escribe
    assert rf.main(["--check"]) == 0  # al dia
    (tmp_path / "figura.svg").write_text("otra cosa", encoding="utf-8")
    assert rf.main(["--check"]) == 1  # desactualizada
