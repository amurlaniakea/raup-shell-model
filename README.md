# Modelo Geométrico 🐚 — Modelo de enrollamiento espiral (Raup, 1961-1966)
<!-- SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->


> **¡Hola, explorador!** Este código reproduce la forma de las conchas de caracoles y amonites usando solo cuatro números: **W**, **D**, **T** y **S**. Es el mismo truco matemático que usó el paleontólogo David M. Raup en los años 60.

Implementación en Python del modelo geométrico de enrollamiento espiral. **Licencia:** AGPL-3.0-or-later. Ver [LICENSE](LICENSE).

## 🧭 ¿Cómo funciona? (para jóvenes curiosos)

Imagina que tienes una curva generadora (como un círculo pequeño) y la haces girar alrededor de un eje, como si envolvieras un hilo alrededor de un lápiz. Cada vuelta, la curva crece exponencialmente (`W` multiplica el radio por `W` en cada vuelta; con `W=2.0`, el valor por defecto, lo duplica, así que no es 'un poquito'), se aleja un poco del eje (`D`) y sube un poquito (`T`). ¡Así nace cualquier concha espiral!

![Espiral de concha con los parámetros W, D y T marcados](assets/concha-espiral.svg)

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

## 📚 Referencias principales

- Raup, D. M. (1961). The Geometry of Coiling in Gastropods. *PNAS*.
- Raup, D. M., & Michelson, A. (1965). Theoretical Morphology of the Coiled Shell. *Science* 147(3663): 1294-1295.
- Raup, D. M. (1966). Geometric analysis of shell coiling; general problems. *Journal of Paleontology*.
