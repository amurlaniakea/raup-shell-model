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

## Decisiones abiertas (Pedro)

1. Autorizar o no esta formulación secundaria como base de src/model.py, a contrastar con Raup (1966).
2. Convención de T: línea central (T = cot beta) o la de Raup sobre la sección completa.
3. S: elipse con rho = b/a (círculo si rho = 1), o mantener S fuera del modelo por ahora.

> Este archivo no sustituye la lectura de Raup (1966). Hasta que Pedro autorice la decisión 1, no se modifica src/.
