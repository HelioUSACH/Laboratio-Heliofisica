from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from src.reading import list_raw_files, processed_file
from src.stadistic import (list_axes, summary_row, mean_uncertainty, power_law_fit, axes_correlation,
                           mean_split, uA_cc_correlation, sample_deviations)
from src.graphic import (make_figure_dir, graph_uA_fit, graph_uA_range, graph_err_rel_axis,
                         graph_mean_split)

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
    residuals, _ = axes_correlation(summary, axes, fit)

    print("\nPower-law fit u_A = a * CC^m (least squares in log10-log10):")
    print(fit.to_string(index=False))


    fit.to_csv(DATA_DIR / "uA_power_law_fit.csv", index=False)
    residuals.to_csv(DATA_DIR / "uA_power_law_residuals.csv")

    split_rows = []
    for key, df in dfs.items():
        split = mean_split(df, axes)
        split.insert(0, "cycle_count", df.attrs["CC"])
        split.insert(0, "file", key)
        split_rows.append(split)
    split_all = pd.concat(split_rows, ignore_index=True).sort_values(["cycle_count", "file"], ignore_index=True)

    print("\nSamples above/below the mean per file (binomial test against 50/50, ties excluded):")
    print(split_all[["file", "axis", "n_above", "n_below", "n_equal", "frac_above_%", "p_binom",
                     "n_inside", "n_outside", "frac_inside_%"]]
          .to_string(index=False))

    _, pvals_cc, _ = uA_cc_correlation(summary, axes)


    split_all.to_csv(DATA_DIR / "mean_split.csv", index=False)
    pvals_cc.to_csv(DATA_DIR / "uA_cc_correlation_pvalues.csv")

    for i, axis in enumerate(axes):
        color = f"C{i}"
        fit_row = fit.loc[fit["axis"] == axis].iloc[0]
        figures = {
            ("fit", f"uA_{axis}_fit_loglog.png"): graph_uA_fit(summary, axis, fit_row, color)[0],
            ("range", f"uA_{axis}_range_loglog.png"): graph_uA_range(summary, axis, color)[0],
            ("err_rel", f"err_rel_{axis}_loglog.png"): graph_err_rel_axis(summary, axis, color)[0],
        }
        for (folder, name), fig in figures.items():
            fig.savefig(make_figure_dir(FIGURES_DIR, folder) / name, dpi=300)
            plt.close(fig)

    for key, df in dfs.items():
        path_key = Path(key)
        split = split_all.loc[split_all["file"] == key]
        fig, _ = graph_mean_split(df, axes, split, title=f"{key} (CC = {df.attrs['CC']})")
        folder = make_figure_dir(FIGURES_DIR, "mean_split", *path_key.parent.parts)
        fig.savefig(folder / f"{path_key.stem}_mean_split.png", dpi=300, bbox_inches="tight")
        plt.close(fig)



if __name__ == "__main__":
    main()
