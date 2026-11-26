# RM3100-sensor-reading

Lectura del magnetómetro **RM3100** con un **ESP32** por I2C. El firmware envía por USB las mediciones en cuentas (LSB) y un script de Python las guarda en un archivo de texto.

Toda la configuración está en un solo archivo, `config/config.yaml`, que usan tanto el firmware como el script de Python.

## Estructura

```
RM3100-sensor-reading/
├── config/
│   └── config.yaml            # Configuración compartida (firmware y Python)
├── include/
│   └── config_gen.h           # Generado al compilar desde config.yaml: no editar
├── src/
│   └── main.cpp               # Firmware del ESP32
├── python/
│   ├── main.py                # Script de adquisición
│   ├── config/gen_config.py   # Genera config_gen.h antes de cada compilación
│   ├── data/                  # Conexión serie y guardado de datos
│   └── utils/                 # Rutas, carga de configuración y logging
├── data/raw/                  # Archivos de datos (se crea al ejecutar)
├── log/process.log            # Registro de ejecución (se crea al ejecutar)
└── platformio.ini
```

## Requisitos

- **Hardware:** ESP32 (`esp32dev`) y sensor RM3100.
- **PlatformIO:** extensión de VS Code o PlatformIO Core (`pio`).
- **Python 3.9 o superior** con los paquetes:

  ```bash
  pip install pyserial pyyaml
  ```

  `pyyaml` también lo usa PlatformIO al compilar; si no está en su entorno, `gen_config.py` lo instala automáticamente.

## Conexiones

| RM3100 | ESP32 |
|---|---|
| SDA | IO21 |
| SCL | IO22 |
| DRDY | IO4 |

La dirección I2C depende de los pines de dirección del RM3100. Con los pines 2 y 4 en LOW la dirección es `0x20`.

## 1. Configuración

Edita `config/config.yaml`:

```yaml
serial_config:
  port: "COM5"           # Puerto serie del ESP32
  monitor_speed: 115200  # Baud rate (firmware y Python)

cycle_count: 50          # Cycle Count de los tres ejes (1..65535)
RM3100_address: 0x20     # Dirección I2C: 0x20, 0x21, 0x22 o 0x23

logging:
  debug_mode: True       # True: muestra y registra mensajes en log/process.log
```

| Parámetro | Lo usa el firmware | Lo usa Python |
|---|---|---|
| `port` | No | Sí |
| `monitor_speed` | Sí (`Serial.begin`) | Sí |
| `cycle_count` | Sí (valor inicial al arrancar) | Sí (lo envía con el comando `CC=`) |
| `RM3100_address` | Sí | Sí (solo para el encabezado) |
| `debug_mode` | No | Sí |

Si cambias `monitor_speed`, `cycle_count` o `RM3100_address`, **vuelve a compilar y cargar el firmware** (paso 2).

## 2. Compilar y cargar el firmware

Desde la carpeta `RM3100-sensor-reading/`:

```bash
pio run                # Compila (genera include/config_gen.h)
pio run -t upload      # Compila y carga en el ESP32
```

Desde VS Code también puedes usar los botones **Build** y **Upload** de la barra de PlatformIO.

Antes de cada compilación, `python/config/gen_config.py` lee `config.yaml`, valida los valores y genera `include/config_gen.h`. Si un valor no es válido, la compilación se detiene con un `ValueError`.

## 3. Ejecutar la adquisición

Cierra cualquier monitor serie abierto (por ejemplo, `pio device monitor`): el puerto solo puede usarlo un programa a la vez.

Desde la carpeta `RM3100-sensor-reading/`:

```bash
python -m python.main
```

> El script debe ejecutarse como módulo (`-m`) desde esa carpeta. `python python/main.py` o el botón **Run** de VS Code fallan con `ImportError: attempted relative import with no known parent package`.

El script:

1. Abre el puerto y espera 2 s, porque el ESP32 se reinicia al abrir la conexión.
2. Guarda como comentarios los mensajes de arranque (`REVID`, `TMRC`, `Mode`, `DRDY pin`).
3. Envía `CC=<cycle_count>` y compara la respuesta del firmware con el valor pedido.
4. Guarda las mediciones hasta que lo detengas con **Ctrl+C**.

## 4. Archivo de salida

Se crea en `data/raw/rm3100_AAAAMMDD_HH-MM-SS.txt`:

```
# REVID = 0x22
# TMRC = 0x96
# Mode = continuous
# DRDY pin = 1
# Date = 2026-11-26 12:34:35
# Cycle Count = 50 (verified)     RM3100 Address = 0x20
# This data corresponds to raw format (LSB) data from the RM3100 sensor
# ========================================
t_us,Xc,Yc,Zc
1000,10,-20,30
2000,11,-21,31
# Total data = 2
```

| Columna | Significado |
|---|---|
| `t_us` | Tiempo del ESP32 en microsegundos (`esp_timer_get_time`), tomado cuando el dato está listo |
| `Xc`, `Yc`, `Zc` | Medición de cada eje en cuentas (LSB), con signo |

- `(verified)`: el firmware confirmó el mismo Cycle Count pedido.
- `(not verified)`: respondió otro valor o `Invalid CC`. El valor recibido queda en `log/process.log`.

Para leerlo en Python, ignorando las líneas de comentario:

```python
import pandas as pd
df = pd.read_csv("data/raw/rm3100_AAAAMMDD_HH-MM-SS.txt", comment="#")
```

## Opciones del firmware

En `src/main.cpp`:

| Opción | Valor | Efecto |
|---|---|---|
| `singleMode` | `0` | Modo de medición continua (por defecto) |
| | `1` | Modo single: pide una medición en cada ciclo de `loop()` |
| `useDRDYPin` | `1` | Espera cada dato con el pin DRDY (por defecto) |
| | `0` | Espera cada dato consultando el registro de estado por I2C |

## Problemas frecuentes

| Síntoma | Causa probable |
|---|---|
| `could not open port 'COM5'` | Puerto equivocado en `config.yaml` o puerto ocupado por otro programa |
| `ImportError: attempted relative import...` | El script no se ejecutó con `python -m python.main` desde `RM3100-sensor-reading/` |
| No se guardan datos y no aparece `Cycle Count` en el log | El firmware no responde: revisa la conexión del sensor y que el firmware esté cargado |
| `Cycle Count = 0 (not verified)` en el log | El sensor no responde por I2C: revisa las conexiones y `RM3100_address` |
| Caracteres extraños en los comentarios | `monitor_speed` distinto entre el firmware cargado y `config.yaml`: vuelve a cargar el firmware |

`platformio.ini` tiene su propio `monitor_speed`, que solo usa el monitor serie de PlatformIO. Si cambias la velocidad en `config.yaml`, cámbiala también ahí para seguir usando ese monitor.
