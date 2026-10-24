# Modelo Geometrico de Conchas Espirales Geométrico 🐚 — Modelo de enrollamiento espiral (Raup, 1961-1966)
<!-- SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->


> **¡Hola, explorador!** Este código aproxima la forma de apertura de conchas espirales (modelo teorico, pendiente de contraste con figuras originales) de caracoles y amonites usando solo cuatro números: **W**, **D**, **T** y **S**. Es el mismo truco matemático que usó el paleontólogo David M. Raup en los años 60.

Implementación en Python del modelo geométrico de enrollamiento espiral. **Licencia:** AGPL-3.0-or-later. Ver [LICENSE](LICENSE).

## 🧭 ¿Cómo funciona? (para jóvenes curiosos)

Imagina que tienes una curva generadora (como un círculo pequeño) y la haces girar alrededor de un eje, como si envolvieras un hilo alrededor de un lápiz. Cada vuelta, la curva crece exponencialmente (`W` multiplica el radio por `W` en cada vuelta; con `W=2.0`, el valor por defecto, lo duplica, así que no es 'un poquito'), se aleja un poco del eje (`D`) y sube un poquito (`T`). ¡Así nace cualquier concha espiral!

![Espiral de concha con los parámetros W, D y T marcados](assets/concha-espiral.svg (archivo pendiente; no se regenera en esta fase; se recomienda usar assets/readme_banner.png para la imagen principal) (pendiente de regeneracion desde el modelo; el archivo actual corresponde a una version anterior))

- **W** = expansión (`whorl expansion rate`) → la concha crece más rápido.
- **D** = distancia al eje → qué tan "abierta" está la espiral.
- **T** = traslación (`translation`) → cuánto sube por cada giro, como una escalera de caracol.
- **S** = forma de la curva generadora → círculo, elipse, etc.

> **⚠️ ESTADO DE IMPLEMENTACIÓN (paso B aplicado):** `D` y `S` ya se usan (`generate_shell`, `whorl_overlap`); `z = T*r` (autosemejante), `generate_curve` incluye cierre. La formulación es SECUNDARIA (Filin 2026) y NO ha sido contrastada con Raup (1966) ni validada contra las figuras originales.
> **⚠️ ADVERTENCIA:** Modelo teórico para fines educativos. No sustituye análisis paleontológicos ni geológicos profesionales.

## 📧 Contacto

- **Autor**: Pedro Sordo Martínez
- **e-mail**: amurlaniakea@gmail.com
- **Hugging Face**: [MagoPredator](https://huggingface.co/MagoPredator)

## 📂 Estructura del proyecto

- `docs/` — Resúmenes y referencias bibliográficas
- `src/` — Modelo geométrico (`model.py`)
- `tests/` — Pruebas con `pytest`
- `assets/` — Dibujos explicativos

## Que puedes explorar

- Cambiar **W** para ver como crece la espiral (duplicacion exacta con W=2.0).
- Cambiar **D** para abrir o cerrar la distancia al eje (D=0 toca el eje).
- Cambiar **T** para subir la espiral como una escalera de caracol (autosemejanza z = T*r).
- Cambiar **S** (`circle` o `ellipse`) y **rho** para modificar la forma de la apertura.
- Ejecutar `python scripts/render_readme_banner.py` para regenerar la imagen principal.

## Matematica del modelo

La formulacion implementada es **SECUNDARIA** (Filin 2026, doi:10.32942/X28Q23, material suplementario S3-S8):

```
r(theta) = r0 * W**(theta / (2*pi))         (S3, expansion)
z = T * r  (autosemejanza, linea central; T = cot(beta))   (S4)
D = (r - a) / (r + a) => a = r*(1-D)/(1+D)  (S5-S6)
rho = b / a  (razon ejes apertura)        (S5-S6)
Solapamiento (S8): T**2 < rho**2 * [((1-D)/(1+D))**2*(W+1)**2 - (W-1)**2] / (W-1)**2
```

> **Nota:** esta formulacion NO ha sido contrastada completamente con Raup (1966, J. Paleontol. 40(5):1178-1190). La fuente primaria debe verificarse antes de considerar el modelo definitivo para analisis paleontologico profesional.

## Estado del proyecto

- **Paso A (higiene):** completado (licencia AGPL-3.0-or-later, cabeceras SPDX, CITATION.cff).
- **Paso B (modelo):** implementado (`generate_curve`, `generate_shell`, `whorl_overlap`, `_build_mesh`, `mesh_shell`, `export_to_stl`). Nota: con `W=2.0` el radio se duplica exactamente (`r[i+N] = W*r[i]` con `revolutions` entero).
- **Paso C (mesh/visual):** iniciado (`mesh_shell`, `export_to_stl`, banner generado).
- **Paso D (verificacion):** pendiente contraste con fuente primaria Raup (1966) y auditoria con Claude.
  Nota: el modelo usa la formulacion secundaria de Filin 2026 (S3-S8); NO ha sido contrastada completamente con Raup (1966, J. Paleontol. 40(5):1178-1190) ni validada contra sus figuras originales.

- **CI:** `.github/workflows/ci.yml` configurado (pytest 3.11-3.13 + ruff).

## Visualizacion

La imagen del banner (`assets/readme_banner.png`) se genera con el modelo propio:

```bash
python scripts/render_readme_banner.py
```

## 📚 Referencias principales

- Raup, D. M. (1961). The Geometry of Coiling in Gastropods. *PNAS*.
- Raup, D. M., & Michelson, A. (1965). Theoretical Morphology of the Coiled Shell. *Science* 147(3663): 1294-1295.
- Raup, D. M. (1966). Geometric analysis of shell coiling; general problems. *Journal of Paleontology*.
