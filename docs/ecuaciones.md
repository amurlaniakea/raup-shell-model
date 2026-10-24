<!-- SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com> -->
<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# Ecuaciones del modelo de Raup — Estado: borrador preliminar

> Regla de honestidad aplicada: cada ecuación indica su fuente y su estado.
> NO se completa ninguna formula de memoria.

## Estado de las fuentes primarias (verificado hoy)

- PNAS 47(4):602-609 (Raup, 1961): fuente inaccesible (HTTP 403). No se extrae ninguna ecuación.
- Science 147(3663):1294-1295 (Raup & Michelson, 1965): fuente inaccesible (HTTP 403). No se extrae ninguna ecuación.
- Journal of Paleontology 40(5):1178-1190 (Raup, 1966): JSTOR devuelve 200, contenido no extraido (tool limitado). Estado: NO LEIDO.

## Definiciones de parámetros (reconstruccion parcial — NO VERIFICADA)

Esto procede de docs/parámetros-rau.md y conocimiento general, NO lectura primaria:

- W (whorl expansión rate): por vuelta. NO VERIFICADO su definición exacta (por revolución completa 2*pi? por unidad de ángulo?).
- D: distancia relativa al eje. Rango sugerido 0 <= D < 1 en doc, NO VERIFICADO con fuente primaria.
- T (translation): proporción de traslación respecto al radio. El codigo hace z = T * theta (lineal), que contradice autosemejanza; por eso esta relación esta marcada EN CONFLICTO con el codigo y debe resolverse antes del paso B.
- S (shape): forma de curva generadora. NO IMPLEMENTADO en generate_curve(); rango valido no confirmado.
- Coordenadas: se asume sistema cilindrico (r, theta, z) con r exponencial. NO VERIFICADO.

## Ecuaciones propuestas (NO VERIFICADAS — pendiente de fuente primaria)

Ninguna ecuación se escribe completa: ninguna fuente primaria fue leida.
Cuando se abran, insertar aqui con referencia exacta (articulo, figura, pagina):

1. Ecuacion de r(theta) con W.
2. Relacion z(r) o z(theta) con T.
3. Efecto de D en la geometría.
4. Definicion de la curva generadora con S (circulo/elipse).

## Decisiones abiertas (Pedro debe confirmar antes del paso B)

1. Confirmar que PNAS 1961 y Science 1965 son referencias de base, o indicar otra fuente primaria.
2. Confirmar rango valido de D (doc dice 0 <= D < 1; es de Raup o interpretación posterior?).
3. Confirmar si T debe ser relativo al radio (z proporciónal a r) para autosemejanza, o si el codigo lineal es el error.
4. Confirmar si S acepta solo circle y ellipse, o mas formas en el articulo.

> Este archivo NO debe considerarse fuente valida para escribir src/model.py.
> El paso B no debe arrancar hasta que al menos las ecuaciónes 1-3 tengan referencia primaria verificada.
