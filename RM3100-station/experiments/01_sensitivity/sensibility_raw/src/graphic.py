from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


def make_figure_dir(figures_dir, *subfolders):
    folder = Path(figures_dir).joinpath(*subfolders)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def graph_uA(resume, axes, loglog=False):
    markers = ["o", "s", "^", "D", "v", "P"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for i, axis in enumerate(axes):
        ax.scatter(resume["cycle_count"], resume[f"uA_{axis}"], marker=markers[i % len(markers)], label=axis)
    if loglog:
        ax.set_xscale("log")
        ax.set_yscale("log")
    ax.set_xlabel("Cycle count")
    ax.set_ylabel(r"$u_A$ [LSB]")
    ax.set_title("Type A uncertainty per axis vs cycle count")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    return fig, ax


def graph_err_rel(resume, axes, loglog=False):
    markers = ["o", "s", "^", "D", "v", "P"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for i, axis in enumerate(axes):
        ax.scatter(resume["cycle_count"], resume[f"err_rel_{axis}_%"], marker=markers[i % len(markers)], label=axis)
    if loglog:
        ax.set_xscale("log")
        ax.set_yscale("log")
    ax.set_xlabel("Cycle count")
    ax.set_ylabel(r"$u_A / |\bar{x}|$ [%]")
    ax.set_title("Relative error per axis vs cycle count")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    return fig, ax


def graph_uA_fit(resume, axis, fit_row, color="C0"):
    valid = resume.dropna(subset=["cycle_count"])
    cc = valid["cycle_count"].astype(float)
    m, a, r2 = fit_row["exponent_m"], fit_row["prefactor_a"], fit_row["r2_log"]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(cc, valid[f"uA_{axis}"], color=color, label="files")
    cc_line = np.logspace(np.log10(cc.min()), np.log10(cc.max()), 200)
    ax.plot(cc_line, a * cc_line ** m, "--", color="k",
            label=rf"$u_A = {a:.3g}\,\mathrm{{CC}}^{{{m:.2f}}}$, $R^2 = {r2:.2f}$")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Cycle count")
    ax.set_ylabel(rf"$u_A$ ({axis}) [LSB]")
    ax.set_title(f"Type A uncertainty vs cycle count: power-law fit ({axis})")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    return fig, ax


def graph_uA_range(resume, axis, color="C0"):
    valid = resume.dropna(subset=["cycle_count"])
    stats = valid.groupby("cycle_count")[f"uA_{axis}"].agg(["mean", "min", "max", "count"])
    yerr = [stats["mean"] - stats["min"], stats["max"] - stats["mean"]]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(valid["cycle_count"], valid[f"uA_{axis}"], color=color, alpha=0.35, label="files")
    ax.errorbar(stats.index, stats["mean"], yerr=yerr, fmt="o-", color=color, capsize=4,
                label="mean per CC (bar: min-max)")
    for cc, n in stats["count"].items():
        ax.annotate(f"n={n}", (cc, stats.loc[cc, "max"]), textcoords="offset points",
                    xytext=(0, 6), ha="center", fontsize=8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Cycle count")
    ax.set_ylabel(rf"$u_A$ ({axis}) [LSB]")
    ax.set_title(f"Type A uncertainty vs cycle count: mean and range ({axis})")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    return fig, ax


def graph_err_rel_axis(resume, axis, color="C0"):
    valid = resume.dropna(subset=["cycle_count"])
    mean_per_cc = valid.groupby("cycle_count")[f"err_rel_{axis}_%"].mean()

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(valid["cycle_count"], valid[f"err_rel_{axis}_%"], color=color, alpha=0.6, label="files")
    ax.plot(mean_per_cc.index, mean_per_cc, "o--", color="k", label="mean per CC")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Cycle count")
    ax.set_ylabel(rf"$u_A / |\bar{{x}}|$ ({axis}) [%]")
    ax.set_title(f"Relative error vs cycle count ({axis})")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    return fig, ax


def graph_mean_split(df, axes, split, title):
    fig, ax_list = plt.subplots(len(axes), 1, figsize=(8, 2.6 * len(axes)), sharex=True, squeeze=False)
    for ax, axis in zip(ax_list[:, 0], axes):
        row = split.loc[split["axis"] == axis].iloc[0]
        x = df[axis].to_numpy(dtype=float)
        idx = np.arange(len(x))
        above, below = x > row["mean"], x < row["mean"]
        ax.scatter(idx[above], x[above], s=12, color="C3", label=f"above: {row['n_above']}")
        ax.scatter(idx[below], x[below], s=12, color="C0", label=f"below: {row['n_below']}")
        if row["n_equal"]:
            equal = ~(above | below)
            ax.scatter(idx[equal], x[equal], s=12, color="gray", label=f"equal: {row['n_equal']}")
        outside = (x < row["lower"]) | (x > row["upper"])
        ax.scatter(idx[outside], x[outside], s=40, facecolors="none", edgecolors="k",
                   label=f"outside: {row['n_outside']}")
        ax.axhline(row["mean"], color="k", label=rf"mean = {row['mean']:.2f}")
        ax.axhspan(row["lower"], row["upper"], color="gray", alpha=0.12)
        ax.axhline(row["upper"], color="gray", ls="--", label=rf"$\bar{{x}} \pm {row['k']:g}s$")
        ax.axhline(row["lower"], color="gray", ls="--")
        ax.set_ylabel(f"{axis} [LSB]")
        ax.set_title(rf"{axis}: {row['frac_above_%']:.1f}% above mean (binomial $p$ = {row['p_binom']:.2g}), "
                     rf"{row['frac_inside_%']:.1f}% inside $\pm {row['k']:g}s$ "
                     rf"(Gaussian: {row['frac_inside_gauss_%']:.1f}%)", fontsize=9)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7, loc="center left", bbox_to_anchor=(1.01, 0.5))
    ax_list[-1, 0].set_xlabel("Sample index")
    fig.suptitle(title)
    fig.tight_layout()
    return fig, ax_list


