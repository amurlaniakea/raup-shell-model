<!-- SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# Ecuaciones del modelo de Raup — Estado: borrador preliminar

> Regla de honestidad aplicada: cada ecuación indica su fuente y su estado.
> NO se completa ninguna fórmula de memoria.

## Estado de las fuentes primarias (verificado hoy)

- PNAS 47(4):602-609 (Raup, 1961): fuente inaccesible (HTTP 403 desde este entorno). No se extrae ninguna ecuación. Estado: NO VERIFICADA.
- Science 147(3663):1294-1295 (Raup & Michelson, 1965): fuente inaccesible (HTTP 403). No se extrae ninguna ecuación. Estado: NO VERIFICADA.
- Journal of Paleontology 40(5):1178-1190 (Raup, 1966): JSTOR devuelve 200, contenido no extraído (limitacion del entorno). Estado: NO LEÍDO, aunque el DOI/URL existe.

## Fuente primaria probable vs fuentes secundarias

- Fuente primaria probable: Raup 1966 (J. Paleontol. 40(5):1178-1190). PNAS 1961 es una version previa; no debe usarse como unica referencia para la formulacion completa.
- Fuente secundaria citada: Filin 2026 (doi:10.32942/X28Q23, preprint). Menciona tan beta = 1/T y gamma = ln W / 2*pi. Titulo y paginas completos: NO VERIFICADOS. No es fuente primaria; no basta para implementar.

## Definiciones de parametros (reconstruccion parcial — NO VERIFICADA)

Esto procede de docs/parametros-rau.md (archivo sin tilde) y de conocimiento general, NO lectura primaria:

- W (whorl expansion rate): tasa de expansion por vuelta. NO VERIFICADO su definición exacta (por revolucion completa 2*pi? por unidad de angulo?).
- D: distancia del eje relativa a la curva generadora. Rango sugerido 0 <= D < 1 en la documentacion, NO VERIFICADO con la fuente primaria.
- T (translation): traslacion vertical. La relación propuesta por la fuente secundaria es proporcional al radio (autosemejanza); el código actual usa z = T*theta (lineal), que contradice la autosemejanza. Estado: EN CONFLICTO con el código y pendiente de verificacion primaria.
- S (shape): forma de la curva generadora (circulo, elipse). NO IMPLEMENTADO en generate_curve(); rango válido no confirmado.
- Sistema de coordenadas: se asume cilíndrico (r, theta, z) con r exponencial. NO VERIFICADO.

## Ecuaciones propuestas (NO VERIFICADAS — pendiente de fuente primaria)

Ninguna ecuación se escribe completa porque ninguna fuente primaria fue leida. Cuando se abran, insertar aqui con referencia exacta (articulo, figura, pagina):

1. Ecuacion de r(theta) con W.
2. Relacion z(r) o z(theta) con T (autosemejante vs lineal).
3. Efecto de D en la geometria (distancia relativa al eje).
4. Definicion de la curva generadora con S (circulo, elipse).

## Decisiones abiertas (Pedro debe confirmar antes del paso B)

1. Confirmar que JP 1966 es la fuente primaria para estas ecuaciones; si PNAS 1961 cubre una parte, marcar que parte corresponde a cada articulo.
2. Confirmar rango válido de D (documentacion sugiere 0 <= D < 1; es interpretacion de Raup o posterior?).
3. Confirmar si T debe ser proporcional al radio (autosemejanza) o si la formulacion lineal tiene alguna justificacion en Raup.
4. Confirmar si S acepta solo circle y ellipse, o si hay mas formas descritas en la fuente primaria.

> Este archivo NO debe considerarse fuente valida para escribir src/model.py. El paso B no debe arrancar hasta que al menos las ecuaciones 1-3 tengan referencia primaria verificada.
