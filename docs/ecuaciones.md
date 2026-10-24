<!-- SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# Ecuaciones del modelo de Raup — borrador con fuente secundaria

> Regla: cada ecuación indica su fuente y su estado. No se completa ninguna fórmula de memoria.
> Estado general: SECUNDARIA. Ninguna ecuación de este archivo se ha leído en Raup (1961, 1966).

## Acceso a las fuentes primarias (intento del 24-10-2026)

- Raup (1961), PNAS 47(4): 602-609, doi:10.1073/pnas.47.4.602: HTTP 403 desde el entorno del implementador. NO LEÍDA.
- Raup y Michelson (1965), Science 147(3663): 1294-1295, doi:10.1126/science.147.3663.1294: HTTP 403. NO LEÍDA.
- Raup (1966), J. Paleontol. 40(5): 1178-1190: JSTOR responde, pero no se pudo extraer el contenido. NO LEÍDA.
  Es la fuente primaria probable de la formulación completa; PNAS 1961 es una versión previa (según Filin 2026).

## Fuente secundaria utilizada

Filin, I. (2026). Lead and slant on the geometry of coiling in gastropods. Preprint de EcoEvoRxiv, v3 (28-05-2026),
doi:10.32942/X28Q23. Un solo autor; no revisado por pares. Las ecuaciones proceden de su material suplementario,
sección S3 (Eqs. S3-S8). Se usa solo como formulación de trabajo y debe contrastarse con Raup (1966).

## Formulación (SECUNDARIA)

```
W = exp(2*pi*gamma)       (S3)  =>  r(theta) = r0 * W^(theta / (2*pi))
T = cot(beta)             (S4)  =>  z = T * r        (hélice cónica: r = z * tan(beta))
D = (r - a) / (r + a)     (S5)  =>  a  = r * (1 - D) / (1 + D)         (S6)
                                    xi = r - a = r * 2D / (1 + D)      (radio interior, S6)
rho = b / a                     (razón de ejes de la abertura; a radial, b axial)
Solapamiento (S8):  T^2 < rho^2 * [ ((1-D)/(1+D))^2 * (W+1)^2 - (W-1)^2 ] / (W-1)^2
```

Fronteras de Raup (1966) citadas por Filin, comprobadas algebraicamente a partir de S8:

- D = 0 y rho = 1: T = 2*sqrt(W) / (W - 1)
- T = 0: D < 1/W

## Contraste con src/model.py

- `r = W ** (theta / (2*pi))`: coherente con S3.
- `z = T * theta`: INCOMPATIBLE. La formulación exige z proporcional a r (autosemejanza).
- `D`: se ignora. Según S5-S6 fija el tamaño de la abertura; rango 0 <= D < 1 (D = 0: la abertura toca el eje).
- `S`: se ignora. Según Filin, Raup nunca lo define con precisión; es habitual usar la razón de ejes de una elipse.

## Advertencia de convención

Filin indica que los valores de T publicados pueden requerir duplicarse para corresponder a la línea central
(Davoli y Russo 1974; nota en su Fig. 2). Hay que fijar una convención antes de implementar.

## Decisiones confirmadas por Pedro (paso B autorizado)

1. Formulacion secundaria de Filin 2026 (S3-S8) autorizada como base de src/model.py; pendiente contraste con Raup (1966).
2. Convencion T: linea central (T = cot beta).
3. S: elipse con rho = b/a; circulo si rho = 1.
4. Rango D: 0 <= D < 1 (documentado, pendiente verificacion primaria).


## Implementacion (paso B)

- `coiling_params`: valida W>=1, 0<=D<1, T>=0, rho>0, S en {circle,ellipse}; W<1 se rechaza (decision de diseno: contraccion no soportada).
- `generate_curve`: r(theta) = r0 * W**(theta / (2*pi)); z = T * r (S4, linea central); incluye punto final (steps puntos para 0 a 2*pi*revolutions).
- `generate_shell`: apertura en plano sagital: R = r + a*cos(phi), Z = z + rho*a*sin(phi) con a = r*(1-D)/(1+D) (S5-S6).
- `whorl_overlap`: implementacion directa de S8; verificada numericamente con test independiente (geometrico, no cita a Filin como fuente de la equivalencia).

Nota: la equivalencia entre la formula algebraica S8 y la superposicion geometrica de elipses sagitales (test 7) es una derivacion propia verificada numericamente, no una afirmacion de Filin 2026.
