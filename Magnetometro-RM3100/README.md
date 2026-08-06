# RM3100 System

Sistema integrado para la medición magnética con el magnetómetro RM3100. El repositorio reúne firmware, hardware (electrónica y mecánica), software de host y documentación en un único monorepo.

## Alcance

Sistema integrado completo:

- Alimentación propia.
- Adquisición de datos desde el magnetómetro RM3100.
- Envío de datos al host.
- Calibración y cálculo.
- Automatización y tests.
- Diseño electrónico (KiCad) y modelado mecánico 3D.

## Supuestos del repositorio

1. Monorepo: firmware, hardware, host y docs en un solo repositorio, con historial único.
2. Host en Python (adquisición, calibración, análisis).
3. Firmware en C/C++ sobre PlatformIO.
4. Control de versiones con Git.

## Estructura

```
rm3100-system/
├── README.md            # Este archivo
├── LICENSE
├── .gitignore
├── docs/                # Documentación del proyecto
├── firmware/            # Proyecto PlatformIO (microcontrolador)
├── hardware/            # Electrónica (KiCad) y mecánica (3D)
├── host/                # Software de PC (Python)
├── data/                # Datos crudos y procesados
├── scripts/             # Automatización
└── tools/               # Utilidades auxiliares
```

### docs/

| Carpeta | Contenido |
|---|---|
| `datasheets/` | Hojas de datos del RM3100 y componentes (PDF). |
| `design/` | Diagramas de bloques y decisiones de diseño. |
| `calibration/` | Método y reportes de calibración. |
| `notes/` | Bitácora de trabajo. |

### firmware/

Proyecto PlatformIO.

| Ruta | Contenido |
|---|---|
| `platformio.ini` | Configuración de entornos y placas. |
| `src/` | `main.cpp` y lógica de aplicación. |
| `include/` | Headers propios de la aplicación. |
| `lib/rm3100/` | Driver del sensor, aislado y reutilizable. |
| `test/` | Tests unitarios (Unity/PlatformIO). |
| `boards/` | Definiciones de placa custom (si aplica). |

### hardware/

| Ruta | Contenido |
|---|---|
| `electronics/` | Proyecto KiCad (esquemático, PCB, librerías propias). |
| `electronics/libraries/symbols/` | Símbolos `.kicad_sym` propios. |
| `electronics/libraries/footprints/` | Footprints en carpetas `*.pretty`. |
| `electronics/libraries/3d/` | Modelos `.step`/`.wrl` asociados a footprints. |
| `mechanical/cad/` | Fuente del modelado 3D (FreeCAD, Fusion, etc.). |
| `mechanical/exports/` | Exportaciones STEP y STL para impresión. |

### host/

Software de PC en Python.

| Ruta | Contenido |
|---|---|
| `pyproject.toml` | Dependencias y configuración (o `requirements.txt`). |
| `src/acquisition/` | Toma de datos desde el microcontrolador. |
| `src/calibration/` | Cálculo de calibración. |
| `src/analysis/` | Post-proceso, cálculo y gráficos. |
| `tests/` | Tests del host. |

### data/

| Carpeta | Contenido |
|---|---|
| `raw/` | Datos crudos. Los archivos grandes se ignoran en Git. |
| `processed/` | Datos procesados. |

### scripts/ y tools/

- `scripts/`: automatización (flasheo, ejecución, exportaciones).
- `tools/`: utilidades auxiliares del proyecto.

## Convenciones

- El driver del RM3100 vive en `firmware/lib/rm3100/`, no en `src/`, para mantenerlo aislado, testeable y reutilizable en otros firmwares.
- Las librerías KiCad propias se guardan en `hardware/electronics/libraries/` y se referencian por ruta relativa al proyecto, de modo que el repositorio sea autocontenido y no dependa de rutas absolutas de la máquina.
- El modelado 3D separa fuente (`cad/`) de exportaciones derivadas (`exports/`), para no versionar STL como si fueran fuente.
- Los datos crudos grandes quedan fuera del control de versiones (regla en `.gitignore`); se versionan solo muestras pequeñas o metadatos.
- Los tests se mantienen en dos niveles independientes, firmware (`firmware/test/`) y host (`host/tests/`), porque usan entornos y ejecutores distintos.

## Puesta en marcha

Firmware:

```bash
cd firmware
pio run                 # Compilar
pio run --target upload # Flashear
pio test                # Ejecutar tests
```

Host:

```bash
cd host
# instalar dependencias segun pyproject.toml o requirements.txt
python -m pytest        # Ejecutar tests
```