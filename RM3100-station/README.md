# Magnetómetro RM3100

Sistema integrado de magnetometría basado en el sensor **RM3100**. El repositorio reúne el
firmware, el diseño de hardware y la documentación del proyecto en un solo lugar.

## Estructura

```
Magnetometro-RM3100/
├── firmware/     # Proyecto PlatformIO (microcontrolador)
├── hardware/     # Diseño electrónico (KiCad)
├── docs/         # Documentación del proyecto
└── data/         # Datos crudos y procesados
```

### firmware/

Proyecto **PlatformIO**. El archivo `platformio.ini` está en la raíz de esta carpeta.

| Ruta              | Contenido                                  |
|-------------------|--------------------------------------------|
| `platformio.ini`  | Configuración de entornos y placa.         |
| `src/`            | `main.cpp` y lógica de la aplicación.      |
| `include/`        | Headers propios.                           |
| `lib/`            | Librerías locales (driver del sensor).     |
| `test/`           | Tests unitarios (Unity/PlatformIO).        |

```bash
cd firmware
pio run                  # Compilar
pio run --target upload  # Flashear
pio test                 # Ejecutar tests
```

### hardware/

Diseño electrónico en **KiCad**.

| Ruta                    | Contenido                                                   |
|-------------------------|-------------------------------------------------------------|
| `kicad/`                | Proyecto KiCad autocontenido (esquemático, PCB, footprints).|
| `libraries/symbols/`    | Símbolos `.kicad_sym` propios.                              |
| `exports/`              | Exportaciones (imágenes de esquemático, etc.).             |

> Las librerías del proyecto se referencian con rutas relativas (`${KIPRJMOD}`), de modo que
> el repositorio es autocontenido y no depende de rutas absolutas de la máquina.

### docs/

| Carpeta            | Contenido                                             |
|--------------------|-------------------------------------------------------|
| `Investigacion/`   | Documentos LaTeX de investigación, bibliografía y figuras. |
| `Informes/`        | Informes de avance (PDF).                             |
| `Presentaciones/`  | Presentaciones (PDF).                                 |
| `Datasheets/`      | Hojas de datos del RM3100 y componentes.             |

La documentación de investigación se compila con `latexmk` (la salida va a `build/`):

```bash
cd docs/Investigacion
latexmk RM3100_information.tex
```

### data/

Datos crudos y procesados. Los archivos grandes quedan fuera del control de versiones
(regla en `.gitignore`); se versionan solo muestras pequeñas o metadatos.

## Convenciones

- **Firmware**: el driver del RM3100 vive en `firmware/lib/`, aislado y reutilizable, no en `src/`.
- **Hardware**: las librerías propias de KiCad se guardan en `hardware/libraries/` y se
  referencian por ruta relativa al proyecto.
- **Docs**: la fuente LaTeX se versiona; los artefactos de compilación (`build/`) se ignoran,
  conservando solo el PDF final.
