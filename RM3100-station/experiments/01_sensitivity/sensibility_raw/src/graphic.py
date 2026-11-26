import numpy as np
import matplotlib.pyplot as plt

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


def graph_uA_strip(resume, axis, color="C0"):
    valid = resume.dropna(subset=["cycle_count"])
    cc_values = sorted(valid["cycle_count"].unique())

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for pos, cc in enumerate(cc_values):
        u = valid.loc[valid["cycle_count"] == cc, f"uA_{axis}"].to_numpy()
        offsets = np.linspace(-0.12, 0.12, len(u)) if len(u) > 1 else np.zeros(1)
        ax.scatter(pos + offsets, u, color=color, alpha=0.7, label="files" if pos == 0 else None)
        ax.hlines(u.mean(), pos - 0.25, pos + 0.25, color="k", label="mean" if pos == 0 else None)
    ax.set_xticks(range(len(cc_values)))
    ax.set_xticklabels([f"{cc:g}" for cc in cc_values])
    ax.set_yscale("log")
    ax.set_xlabel("Cycle count (categorical)")
    ax.set_ylabel(rf"$u_A$ ({axis}) [LSB]")
    ax.set_title(f"Type A uncertainty per cycle count ({axis})")
    ax.grid(alpha=0.3, which="both", axis="y")
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


def graph_residual_correlation(residuals, axes, correlations):
    pairs = [(axes[i], axes[j]) for i in range(len(axes)) for j in range(i + 1, len(axes))]

    fig, ax_list = plt.subplots(1, len(pairs), figsize=(4.5 * len(pairs), 4.2), squeeze=False,
                               layout="constrained")
    for ax, (a1, a2) in zip(ax_list[0], pairs):
        sc = ax.scatter(residuals[a1], residuals[a2], c=np.log10(residuals["cycle_count"].astype(float)),
                        cmap="viridis")
        r_p = correlations.loc[("residual_pearson", a1), a2]
        r_s = correlations.loc[("residual_spearman", a1), a2]
        ax.axhline(0, color="gray", lw=0.8)
        ax.axvline(0, color="gray", lw=0.8)
        ax.set_xlabel(rf"$\delta_{{{a1}}}$ [dex]")
        ax.set_ylabel(rf"$\delta_{{{a2}}}$ [dex]")
        ax.set_title(rf"{a1} vs {a2}: $r$ = {r_p:.2f}, $\rho_s$ = {r_s:.2f}")
        ax.grid(alpha=0.3)
    cbar = fig.colorbar(sc, ax=ax_list[0].tolist())
    cbar.set_label(r"$\log_{10}$(Cycle count)")
    fig.suptitle("Correlation between axes of the power-law residuals of $u_A$")
    return fig, ax_list
