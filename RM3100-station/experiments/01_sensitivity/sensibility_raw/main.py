from pathlib import Path

import pandas as pd
import numpy as np

base = Path(Path(__file__).resolve().parent.parent.parent)
data_file = base / "common" / "RM3100-sensor-reading" / "data" / "raw"



raw_file = data_file / "rm3100_20261126_12-31-50.txt"
df = pd.read_csv(raw_file, comment = "#")
df = df[10:110].reset_index(inplace = False, drop = True)
df = df.drop(columns = "t_us")

for axis in ['Xc', 'Yc', 'Zc']:
    print(
        f"{axis}: "
        f"Min: {df[axis].min():.2f}, "
        f"Max: {df[axis].max():.2f}"
    )
mean = df.mean()

N = len(df)

df_new = (df-mean)**2

suma_columnas = df_new.sum(axis=0)
suma_columnas = suma_columnas/(N-1)
sigma = np.sqrt(suma_columnas)

incertidumbre = sigma/np.sqrt(N)


print(f"\nIntervalo de confianza: ")
for axis in ['Xc', 'Yc', 'Zc']:
    print(
        f"{axis}[LSB]: "
        f"[{mean[axis] - 2*sigma[axis]:.2f}, "
        f"{mean[axis] + 2*sigma[axis]:.2f}], "
        f"Incertidumbre: {incertidumbre[axis]:.3f}"
    )

print(f"\nError Relativo porcentual:")
for axis in ['Xc', 'Yc', 'Zc']:
    print(
        f"Error % [{axis}]: {((incertidumbre[axis]/np.abs(mean[axis]))*100):.3f} %"
    )