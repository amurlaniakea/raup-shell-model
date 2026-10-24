# Autor: Pedro Sordo Martínez <amurlaniakea@gmail.com> — AGPL-3.0
"""Modelo geométrico de enrollamiento espiral — David M. Raup (1961-1966)
Parámetros: W (expansión), D (distancia al eje), T (traslación), S (forma generadora)
Autor: Pedro Sordo Martínez <amurlaniakea@gmail.com> — AGPL-3.0
"""
import math

def coiling_params(W=2.0, D=0.5, T=0.1, S='circle'):
    return {'W': W, 'D': D, 'T': T, 'S': S}

def generate_curve(W=2.0, D=0.5, T=0.1, steps=360):
    result = []
    for i in range(steps):
        theta = (4 * math.pi * i) / steps
        r = W ** (theta / (2 * math.pi))
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = T * theta
        result.append([x, y, z])
    return result
