# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from model import coiling_params, generate_curve


def test_params():
    p = coiling_params(W=2.5, D=0.3, T=0.15)
    assert p["W"] == 2.5


def test_curve():
    c = generate_curve(W=2.0, D=0.5, T=0.1, steps=10)
    assert len(c) == 10
    assert len(c[0]) == 3
