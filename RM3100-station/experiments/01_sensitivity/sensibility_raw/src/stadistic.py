import numpy as np
import pandas as pd
from scipy.stats import binomtest, norm, pearsonr, spearmanr

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


def mean_split(df, axes, k=2):
    rows = []
    for axis in axes:
        x = df[axis].to_numpy(dtype=float)
        mean = x.mean()
        sigma = x.std(ddof=1)
        lower, upper = mean - k * sigma, mean + k * sigma
        n_above = int(np.sum(x > mean))
        n_below = int(np.sum(x < mean))
        n_equal = len(x) - n_above - n_below
        n_valid = n_above + n_below
        n_inside = int(np.sum((x >= lower) & (x <= upper)))
        rows.append({
            "axis": axis,
            "N": len(x),
            "mean": mean,
            "median": np.median(x),
            "n_above": n_above,
            "n_below": n_below,
            "n_equal": n_equal,
            "frac_above_%": 100 * n_above / n_valid if n_valid else np.nan,
            "p_binom": binomtest(n_above, n_valid, 0.5).pvalue if n_valid else np.nan,
            "k": k,
            "lower": lower,
            "upper": upper,
            "n_inside": n_inside,
            "n_outside": len(x) - n_inside,
            "frac_inside_%": 100 * n_inside / len(x),
            "frac_inside_gauss_%": 100 * (2 * norm.cdf(k) - 1)
        })

    return pd.DataFrame(rows)


def sample_deviations(dfs, axes):
    frames = []
    for key, df in dfs.items():
        dev = (df[axes] - df[axes].mean()).abs()
        dev.insert(0, "cycle_count", df.attrs["CC"])
        dev.insert(0, "file", key)
        frames.append(dev)

    return pd.concat(frames, ignore_index=True)


def uA_cc_correlation(summary, axes):
    valid = summary.dropna(subset=["cycle_count"])
    cols = ["cycle_count"] + [f"uA_{axis}" for axis in axes]
    data = valid[cols].astype(float)

    corr, pvals = {}, {}
    for method, values, func in [("pearson_log", np.log10(data), pearsonr), ("spearman", data, spearmanr)]:
        r = pd.DataFrame(np.eye(len(cols)), index=cols, columns=cols)
        p = pd.DataFrame(np.nan, index=cols, columns=cols)
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                res = func(values.iloc[:, i], values.iloc[:, j])
                r.iloc[i, j] = r.iloc[j, i] = res.statistic
                p.iloc[i, j] = p.iloc[j, i] = res.pvalue
        corr[method], pvals[method] = r, p

    return pd.concat(corr), pd.concat(pvals), len(valid)