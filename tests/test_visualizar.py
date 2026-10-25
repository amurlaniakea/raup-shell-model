# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Prueba de humo del visor 3D (se omite sin matplotlib)."""

import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")

import visualizar  # noqa: E402


@pytest.mark.parametrize(
    "modo, archivo",
    [("clasica", "concha_clasica.png"), ("torre", "concha_torre.png"), ("plana", "concha_plana.png")],
)
def test_vista_simple_guarda_un_png(modo, archivo, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    visualizar.vista_simple(modo, guardar=True)
    png = tmp_path / archivo
    assert png.exists() and png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
