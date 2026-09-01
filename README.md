# Ingeniería Industrial · Plan de Estudio 26.2

Malla interactiva de requisitos entre cursos de Ingeniería Industrial (PUCP), **de la
primera a la última matrícula**: Estudios Generales Ciencias (ciclos 1 al 4) y Facultad
de Ciencias e Ingeniería (ciclos 5 al 10), según el plan vigente en el semestre **2026-2**.

Creado por **Ing. Roberto Paz**.

**Ver la malla:** https://USUARIO.github.io/REPOSITORIO/
*(reemplaza `USUARIO` y `REPOSITORIO` una vez publicada — ver más abajo)*

![Vista previa de la malla](malla-plan-estudio-26-2.png)

---

## Qué contiene

| Archivo | Qué es |
|---|---|
| `index.html` | Las dos mallas interactivas en **un solo archivo**: fuentes, logos e imágenes van incrustados, así que funciona sin conexión y sin dependencias. |
| `malla-plan-estudio-26-2.png` | La malla de Facultad (ciclos 5-10) como imagen de 6736 × 5526 px, apta para imprimir en A1 o A0. |
| `malla-eeggcc-ciclos-1-4.png` | La malla de EE.GG.CC. (ciclos 1-4) como imagen de 6736 × 5230 px. |
| `generador/` | El código que produce todo, por si el plan cambia. |
| `generador/foto-roberto-paz.png` | La foto que sale en la ficha del autor; cámbiala ahí y vuelve a ejecutar `integrar.py`. |

## Cómo se usa

- **La cabecera azul es fija**: lleva el título de la malla y los logos arriba, y los
  controles abajo; no se mueve al desplazar el diagrama. Al pasar el cursor sobre
  **Ing. Roberto Paz** se abre su ficha con foto y especialidad.
- **EE.GG.CC. / Facultad**: el conmutador de la izquierda de la barra cambia entre la
  malla de los ciclos 1 al 4 y la de los ciclos 5 al 10. Cada una conserva su propia
  leyenda al pie. Los dos lienzos miden lo mismo de ancho, así que al alternar la
  cabecera y los recuadros se ven del mismo tamaño.
- **Pasa el cursor sobre un curso** y el diagrama aísla sus dependencias: se resaltan los
  cursos que lo habilitan y los que dependen de él.
- **Pasa el cursor sobre un recuadro punteado** (los grupos electivos de EE.GG.CC.) y
  aparece la lista de cursos de ese grupo.
- **Ajustar / 100 % / + / −** controlan el zoom. Por defecto la malla encaja al ancho de
  la ventana.
- **Arrastra** con el mouse para desplazarte cuando estés con zoom.

## Cómo leer el diagrama

Cada flecha nace en el curso-requisito y apunta al curso que lo exige. El color indica el
tipo de relación, siguiendo la notación del plan de estudios:

| Color | Notación en el PDF | Significado |
|---|---|---|
| Azul | *(sin símbolo)* | Requiere el curso **aprobado** |
| Verde | `[ ]` | Aprobado **o** cursar en paralelo |
| Ámbar | `( )` | Haber cursado con nota 08 o más |
| Rojo | `{ }` | Haber cursado **o** cursar en paralelo |

En la malla de **Facultad de Ingeniería** (ciclos 5 al 10), los requisitos que no son cursos de esos ciclos aparecen como
etiqueta dentro del recuadro: `1FIS04` es un curso aprobado de los ciclos 1 al 4, y
`70 cr. aprob.` son créditos acumulados del plan. Las claves con recuadro de color son
requisitos dibujados sin flecha.

En la malla de **EE.GG.CC.** cada recuadro lleva solo la clave, el nombre del curso y sus
créditos, y todos los requisitos van dibujados, porque todos los cursos que participan están
en pantalla. Los requisitos **dentro de un mismo ciclo** no cruzan el diagrama: esos cursos
quedan apilados uno debajo del otro y los une una **flecha vertical corta** entre los dos
recuadros. Cuando hay **dos flechas, una en cada sentido**, cada curso es requisito del otro
—el caso de *Física* y su *laboratorio*, que se llevan juntos.

---

## Publicar en GitHub Pages

1. Crea un repositorio **público** en GitHub y sube estos archivos (arrastrarlos a la web de GitHub basta).
2. Entra a **Settings → Pages**.
3. En *Source* elige **Deploy from a branch**, rama `main` y carpeta `/ (root)`. Guarda.
4. Espera un minuto. La URL aparece en esa misma página, con la forma
   `https://USUARIO.github.io/REPOSITORIO/`.

Cualquiera puede abrir ese enlace desde el navegador, sin cuenta de GitHub y sin instalar nada.
Cada vez que subas un `index.html` nuevo, el sitio se actualiza solo en un par de minutos.

> El repositorio debe ser público para que Pages funcione con una cuenta gratuita.
> Si lo necesitas privado, GitHub pide un plan de pago.

Después de publicar, actualiza el enlace del inicio de este README y la etiqueta
`og:image` de `index.html` con la URL completa del PNG, para que las vistas previas
al compartir el enlace muestren la malla.

---

## Regenerar las mallas

Solo necesitas Python 3 (sin librerías externas) y un Chromium para exportar los PNG.

```bash
cd generador
python3 malla.py          # malla de Facultad: print_A.html y Malla_A_flechas.html
python3 check.py          # verifica cruces de flechas y colisiones con los recuadros

python3 malla_eeggcc.py   # malla de EE.GG.CC.: escribe eeggcc.json
python3 check_eeggcc.py   # verifica flechas, cruces y colisiones de esa malla
python3 integrar.py       # une las dos mallas y reescribe ../index.html
python3 exportar_png.py   # vuelve a exportar los dos PNG
```

> `integrar.py` parte del `index.html` de **una sola malla** (el que produce `malla.py`) y
> le añade la de EE.GG.CC.; si lo ejecutas sobre un `index.html` ya integrado, se detiene y
> avisa. Guarda una copia del archivo de una sola malla si vas a iterar.
> `medir.py` mide el alto real de la leyenda de EE.GG.CC. e imprime el valor que hay que
> poner en `ALTO_EG`, dentro de `integrar.py`, si cambias esos textos.
> En pantalla cada malla se dibuja subida `SUBIDA` px para tapar la cabecera grande que
> lleva dentro, porque los controles ya están en la cabecera fija; esa cabecera grande solo
> reaparece al exportar los PNG, que es lo que hace `window.modoExport(true)`.
> El nombre y la especialidad del autor están en `AUTOR` y `ESPECIALID`, al inicio de
> `integrar.py`.

Para cambiar el plan, edita la lista `COURSES` al inicio de `malla.py` (ciclos 5-10) o de
`malla_eeggcc.py` (ciclos 1-4). Cada curso es `(ciclo, clave, nombre, créditos, [requisitos])`
y los requisitos se escriben tal como aparecen en el PDF, con sus corchetes o paréntesis.
En `malla_eeggcc.py` está además `GRUPOS`: los cursos de cada grupo electivo, los que salen
al pasar el cursor sobre un recuadro punteado. El resto se recalcula solo.

### Cómo se acomoda el diagrama

El orden vertical de los cursos no está escrito a mano: se calcula. El grafo se modela por capas
—una por ciclo— y las flechas que saltan más de un ciclo se parten en nodos ficticios, al estilo
Sugiyama. Sobre eso corren 80 barridos de baricentro y un refinamiento por transposición de pares,
lo que baja los cruces de 77 a 0 en la malla de Facultad y de 11 a 2 en la de EE.GG.CC.

En EE.GG.CC. hay además requisitos **dentro de un mismo ciclo** (*Cálculo integral* con *Física 2*,
*Física 2* con su laboratorio y al revés). Esos cursos forman una **cadena** que se acomoda como
un solo bloque, siempre contigua, y sus requisitos se dibujan como la línea vertical entre
recuadros. Se prueban los dos sentidos posibles de cada cadena y se queda el que deja menos
cruces reales.

El ruteo es ortogonal. Las anclas de cada recuadro no se reparten a ciegas: cada flecha **sale**
a la altura a la que va, dentro de lo que permite el orden y una separación mínima, de modo que
salen rectas cuando pueden y dos nunca arrancan a la misma altura; y un recuadro que recibe una
sola flecha la recibe **justo por la mitad**. Dentro de cada canal vertical los carriles se
ordenan con una búsqueda local (intercambios, reinserciones y 120 reinicios aleatorios) que
minimiza los cruces; a igualdad de cruces desempata la altura de salida, así que el destino más
alto se queda con el carril más a la izquierda y los cruces inevitables quedan como una X limpia
en vez de dos líneas que corren pegadas.

`check.py` y `check_eeggcc.py` reconstruyen los trazados del SVG y comprueban intersección
segmento a segmento. En Facultad el resultado debe ser **0 cruces y 0 colisiones**; en EE.GG.CC.,
**0 colisiones**, ningún trazo fuera del lienzo, todos los requisitos del mismo ciclo entre
recuadros contiguos y **2 cruces**, que es el mínimo alcanzable con este plan: *Mecánica para
ingenieros* exige *Física 1* mientras *Cálculo integral* exige *Cálculo diferencial*, y las dos
parejas se cruzan sin remedio porque *Mecánica* tiene que ir pegada a *Cálculo integral*.

---

Datos: Plan de Estudios de Ingeniería Industrial PUCP, válido a partir del 2022-1, y
Plan de Estudios Específico FCI 2026-2.
Diseño y colores: **Made Easy**. Creador: **Ing. Roberto Paz**.
