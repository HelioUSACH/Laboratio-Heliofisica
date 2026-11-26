import numpy as np
import pandas as pd

def list_axes(df):
    axes = [col for col in df.columns if col != "t_us"]
    return axes


def uncertainty_type_a(df, axes):
    
    N = len(df)
    mean = df[axes].mean()
    sigma = df[axes].std(ddof = 1)
    u_A = sigma / np.sqrt(N)

    return N, mean, sigma, u_A


def summary_row(key, folder, df, axes):
    N, mean, sigma, u_A = uncertainty_type_a(df, axes)

    row = {
        "file": key,
        "folder": folder,
        "cycle_count": df.attrs["CC"],
        "N": N
    } 

    for axis in axes:
        row[f"mean_{axis}"] = mean[axis]
        row[f"sigma_{axis}"] = sigma[axis]
        row[f"uA_{axis}"] = u_A[axis]
        row[f"err_rel_{axis}_%"] = u_A[axis] / np.abs(mean[axis]) * 100

    return row

def mean_uncertainty(summary, axes):
    cols_uA = [f"uA_{axis}" for axis in axes]
    u_all = summary[cols_uA].mean()
    u_per_cc = summary.groupby("cycle_count")[cols_uA].mean()
    return u_all, u_per_cc


def power_law_fit(summary, axes):
    valid = summary.dropna(subset=["cycle_count"])
    log_cc = np.log10(valid["cycle_count"].astype(float))

    rows = []
    for axis in axes:
        log_u = np.log10(valid[f"uA_{axis}"])
        m, b = np.polyfit(log_cc, log_u, 1)
        log_u_fit = m * log_cc + b
        ss_res = np.sum((log_u - log_u_fit) ** 2)
        ss_tot = np.sum((log_u - log_u.mean()) ** 2)
        rows.append({
            "axis": axis,
            "exponent_m": m,
            "prefactor_a": 10 ** b,
            "r2_log": 1 - ss_res / ss_tot,
            "pearson_r_log": np.corrcoef(log_cc, log_u)[0, 1],
            "N_files": len(valid)
        })

    return pd.DataFrame(rows)


def axes_correlation(summary, axes, fit):
    valid = summary.dropna(subset=["cycle_count"])
    log_cc = np.log10(valid["cycle_count"].astype(float))

    log_u = pd.DataFrame({axis: np.log10(valid[f"uA_{axis}"]) for axis in axes})

    residuals = pd.DataFrame(index=valid.index)
    for _, row in fit.iterrows():
        axis = row["axis"]
        residuals[axis] = log_u[axis] - (row["exponent_m"] * log_cc + np.log10(row["prefactor_a"]))
    residuals["cycle_count"] = valid["cycle_count"]

    correlations = pd.concat({
        "raw_pearson_log": log_u.corr(method="pearson"),
        "residual_pearson": residuals[axes].corr(method="pearson"),
        "residual_spearman": residuals[axes].corr(method="spearman")
    })

    return residuals, correlations