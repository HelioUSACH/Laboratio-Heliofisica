# RM3100-station

Estación de magnetometría basada en el sensor **RM3100**.

## Estructura

```
RM3100-station/
├── docs/
│   ├── Administrativo/      # Documentos administrativos (seminario de grado)
│   ├── Cotizaciones/
│   ├── Datasheets/          # Hojas de datos del RM3100
│   ├── Referencias/         # Papers y artículos de referencia
│   ├── Informes/            # Informes mensuales
│   ├── Investigacion/       # Documentos LaTeX, bibliografía y figuras
│   ├── Presentaciones/
│   └── Review/
├── experiments/
│   ├── common/              # Código compartido entre experimentos
│   ├── 01_sensitivity/
│   ├── 02_calibration/
│   └── 03_validation/
├── hardware/
│   ├── 3D-Models/
│   │   ├── Assembly/            # Modelo 3D (.step)
│   │   ├── Drawings/            # Planos
│   │   └── Fusion360-projects/  # Proyectos Fusion 360 (no se suben a GitHub)
│   ├── kicad/RM3100-station/    # Proyecto KiCad (esquemático, PCB, footprints)
│   ├── libraries/symbols/       # Símbolos KiCad propios
│   └── exports/
├── software/                # Código final de la estación (pendiente)
└── data/                    # Datos operacionales de la estación (pendiente)
```

Cada experimento usa la misma estructura interna:

```
0X_nombre/
├── code/             # Adquisición y análisis
├── data/raw/         # Datos crudos (no se editan)
├── data/processed/   # Datos procesados
└── results/          # Figuras y tablas
```

## Modelo 3D

El modelo 3D del RM3100 está en `hardware/3D-Models/Assembly/RM3100.step` y su plano en
`hardware/3D-Models/Drawings/RM3100-Plano1.pdf`. El PCB de KiCad usa su propia copia en
`hardware/kicad/RM3100-station/3d/RM3100.step`.
