from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from src.reading import list_raw_files, processed_file
from src.stadistic import list_axes, summary_row, mean_uncertainty, power_law_fit, axes_correlation
from src.graphic import (graph_uA_fit, graph_uA_range, graph_uA_strip, graph_err_rel_axis,
                         graph_residual_correlation)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FIGURES_DIR = BASE_DIR / "figures"


def main():
    data_file, files = list_raw_files()
    if not files:
        raise FileNotFoundError(f"No files found in {data_file}")

    dfs = {}
    rows = []
    axes = None
    for path in files:
        key = path.relative_to(data_file).as_posix()
        df = processed_file(path)

        axes_df = list_axes(df)
        if axes is None:
            axes = axes_df
        elif axes_df != axes:
            raise ValueError(f"{key} has columns {axes_df}, expected {axes}")

        dfs[key] = df
        rows.append(summary_row(key, path.parent.name, df, axes))

    summary = pd.DataFrame(rows).sort_values("cycle_count", ignore_index=True)

    no_cc = summary["cycle_count"].isna()
    if no_cc.any():
        print("Warning: no cycle count in:", summary.loc[no_cc, "file"].tolist())

    cols_uA = [f"uA_{axis}" for axis in axes]
    print(summary[["file", "cycle_count", "N"] + cols_uA].to_string(index=False))

    u_all, u_per_cc = mean_uncertainty(summary, axes)

    print("\nMean type A uncertainty (all files):")
    for axis in axes:
        print(f"{axis}[LSB]: {u_all[f'uA_{axis}']:.3f}")

    print("\nMean type A uncertainty per cycle count:")
    print(u_per_cc.to_string())

    DATA_DIR.mkdir(exist_ok=True)
    summary.to_csv(DATA_DIR / "uncertainty_summary.csv", index=False)
    u_per_cc.to_csv(DATA_DIR / "uncertainty_per_cc.csv")

    fit = power_law_fit(summary, axes)
    residuals, correlations = axes_correlation(summary, axes, fit)

    print("\nPower-law fit u_A = a * CC^m (least squares in log10-log10):")
    print(fit.to_string(index=False))
    print("\nCorrelation between axes:")
    print(correlations.to_string())

    fit.to_csv(DATA_DIR / "uA_power_law_fit.csv", index=False)
    residuals.to_csv(DATA_DIR / "uA_power_law_residuals.csv")
    correlations.to_csv(DATA_DIR / "uA_axes_correlation.csv")

    FIGURES_DIR.mkdir(exist_ok=True)
    for i, axis in enumerate(axes):
        color = f"C{i}"
        fit_row = fit.loc[fit["axis"] == axis].iloc[0]
        figures = {
            f"uA_{axis}_fit_loglog.png": graph_uA_fit(summary, axis, fit_row, color)[0],
            f"uA_{axis}_range_loglog.png": graph_uA_range(summary, axis, color)[0],
            f"uA_{axis}_strip.png": graph_uA_strip(summary, axis, color)[0],
            f"err_rel_{axis}_loglog.png": graph_err_rel_axis(summary, axis, color)[0],
        }
        for name, fig in figures.items():
            fig.savefig(FIGURES_DIR / name, dpi=300)
            plt.close(fig)

    fig_corr, _ = graph_residual_correlation(residuals, axes, correlations)
    fig_corr.savefig(FIGURES_DIR / "uA_residual_correlation.png", dpi=300, bbox_inches="tight")
    plt.close(fig_corr)


if __name__ == "__main__":
    main()
