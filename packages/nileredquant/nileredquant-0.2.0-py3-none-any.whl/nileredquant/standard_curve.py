import warnings
import re
import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import pingouin as pg
from scipy.stats import t as student_t
from scipy.stats import norm
from scipy import odr
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import seaborn as sns
import nileredquant.utils as utils


def aggregate_per_group(df, value_column):
    """
    Aggregate data per group (Strain × Condition) with mean, Standard deviation (sd),
    size (n), standard error of mean (sem) & variance (var).

    Parameters
    ----------
    df : pandas.DataFrame
        Input table. Required columns `Condition`, `Strain`, and
        the numeric column specified by `value_column`.
    value_column : str
        Name of the column to aggregate.

    Returns
    -------
    agg_data : pandas.DataFrame
        Aggregated table with one row per (Condition × Strain) and columns:
        `<value>_mean`, `<value>_sd`, `<value>_n`, `<value>_se`,
        `<value>_var`.
    """
    agg_data = (
        df.groupby(["Condition", "Strain"], dropna=False)[value_column]
        .agg(
            **{
                f"{value_column}_mean": "mean",
                f"{value_column}_sd": "std",
                f"{value_column}_n": "size",
                f"{value_column}_se": "sem",
                f"{value_column}_var": "var",
            }
        )
        .astype("float64")
        .reset_index()
    )
    agg_data[f"{value_column}_n"] = agg_data[f"{value_column}_n"].astype("int64")

    return agg_data


def merge_methods_data(df_m1, df_m2, m1_column, m2_column):
    """
    Intersect aggregated data from two methods at (Condition × Strain).

    Parameters
    ----------
    df_m1 : pandas.DataFrame
        Input table for method 1. Required columns `Condition`, `Strain`, and `m1_column`.
    df_m2 : pandas.DataFrame
        Input table for method 2. Required columns `Condition`, `Strain`, and `m2_column`.
    m1_column : str
        Name of the numeric value column in ``df_m1`` to aggregate.
    m2_column : str
        Name of the numeric value column in ``df_m2`` to aggregate.

    Returns
    -------
    controls : pandas.DataFrame
        Inner join of the two per-group aggregates on (`Condition` and `Strain`).
        Column names follow the pattern produced by function `aggregate_per_group`.
    """
    a = aggregate_per_group(df_m1, m1_column)
    b = aggregate_per_group(df_m2, m2_column)
    controls = a.merge(b, on=["Condition", "Strain"], how="inner")

    return controls


def PassingBablok_fit(x, y):
    """
    Fit Passing–Bablok regression for the model: y = a + b x.
    x, y are per-level means (one point per `Strain` × `Condition`).

    Parameters
    ----------
    x, y : array-like
        Mean value per (Condition × Strain) level. Non-finite pairs are dropped.

    Returns
    -------
    a, b : float
        Intercept (a) and slope (b).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    n = x.size
    if n < 3:
        raise ValueError("Passing–Bablok requires at least 3 points.")

    # Collect valid pairwise slopes
    chunks = []
    for i in range(n - 1):
        dx = x[i + 1 :] - x[i]
        dy = y[i + 1 :] - y[i]
        good = dx != 0.0  # for filtering values
        if np.any(good):
            chunks.append(dy[good] / dx[good])

    if not chunks:
        raise ValueError("Passing–Bablok undefined: all x values identical.")

    slopes = np.concatenate(chunks)
    b = float(np.median(slopes))
    a = float(np.median(y - b * x))
    return a, b


def ODR_fit(
    x,
    y,
    sx=None,
    sy=None,
    lam=None,
    alpha=0.05,
):
    """
    Fit ODR regression form model: y = a + b x.
      - If sx & sy (per-point SDs) are provided → use them.
      - Else if lam (lambda = Var_x / Var_y) is provided → Deming via x-scaling.
      - Else → equal-error total least squares.

    Parameters
    ----------
    x, y : array-like
        Observations. Non-finite pairs are removed before fitting.
    sx, sy : array-like, optional
        Per-point standard deviations (errors) for `x` and `y`. If provided,
        both must be given, finite, and strictly positive for all retained
        points. Uses full error-in-variables ODR.
    lam : float, optional
        Ratio `Var_x / Var_y` for Deming regression. When set (and `sx`/`sy`
        are not provided), implements Deming by scaling `x` by
        `s = sqrt(lam)` and performing ODR with equal errors.
    alpha : float, default 0.05
        Significance level for the two-sided confidence interval. Must satisfy
        `0 < alpha < 1`. The returned band has nominal coverage `1 - alpha`.

    Returns
    -------
    a, b : float, dict
        Intercept (a) and slope (b). Pointwise 95% CI for the mean line with keys:
        `{"xg", "yline", "lo", "hi"}` as produced by `compute_ci_odr` function.
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    # Basic finite mask; include sx/sy if present
    mask = np.isfinite(x) & np.isfinite(y)
    if sx is not None and sy is not None:
        sx = np.asarray(sx, dtype=float)
        sy = np.asarray(sy, dtype=float)
        mask &= np.isfinite(sx) & np.isfinite(sy)

    x, y = x[mask], y[mask]
    if sx is not None and sy is not None:
        sx, sy = sx[mask], sy[mask]

    if x.size < 2:
        raise ValueError("ODR requires at least 2 finite (x, y) points.")

    # Model y = a + b x
    model = odr.Model(lambda B, u: B[0] + B[1] * u)
    beta0 = [float(y.mean()), 1.0]

    if sx is not None and sy is not None:
        data = odr.RealData(x, y, sx=sx, sy=sy)
        output = odr.ODR(data, model, beta0=beta0).run()
        a, b = output.beta
        ci = compute_ci_odr(output, x, alpha=alpha, num=200)
        return float(a), float(b), ci

    if lam is not None:
        s = float(lam) ** 0.5  # scale for Deming
        data = odr.RealData(x / s, y)
        output = odr.ODR(data, model, beta0=beta0).run()
        a, b_scaled = output.beta
        ci = compute_ci_odr(output, x, alpha=alpha, num=200, scale_x=s)
        return float(a), float(b_scaled / s), ci

    # If other two fail
    data = odr.RealData(x, y)
    output = odr.ODR(data, model, beta0=beta0).run()
    a, b = output.beta
    ci = compute_ci_odr(output, x, alpha=alpha, num=200)
    return float(a), float(b), ci


def pooled_variance(variance, n):
    """
    Compute the pooled within-group variance across groups.

    Parameters
    ----------
    variance : array-like
        Per-group variances (ideally sample variances with `ddof=1`).
    n : array-like
        Per-group sample sizes.

    Returns
    -------
    float or None
        The pooled variance. Returns `None` if no valid groups are found
        (i.e., after filtering to finite values with ``n >= 2``) or if the
        denominator is zero.
    """
    if n is None:
        return None

    variance = (
        np.asarray(variance, dtype=float)
        if variance is not None
        else np.full(shape=np.shape(variance), fill_value=np.nan)
    )
    n = np.asarray(n, dtype=float)

    if len(variance) != len(n):
        raise ValueError(
            "Variance (var) and replicate number (n) must have the same length."
        )

    valid = np.isfinite(variance) & (n >= 2)
    if not valid.any():
        return None

    # Weighted average
    num = ((n[valid] - 1.0) * variance[valid]).sum()
    den = (n[valid] - 1.0).sum()
    if den <= 0:
        return None
    # if all valid variances are exactly 0, return None
    if np.all(variance[valid] == 0.0):
        return None
    return float(num / den)


def WLS_fit(x, y, variance, n, condition, alpha=0.05):
    """
    Fit the linear model ``y = a + b x`` via Weighted Least Squares (WLS),
    when weights are available or sufficient.

    Parameters
    ----------
    x, y : array-like
        Mean value per (Condition × Strain) level. Non-finite pairs are removed before fitting.
    variance : array-like or None
        Per-group variance of the response. If provided, WLS is attempted using weights `w = n / variance`.
    n : array-like
        Per-group replicate counts corresponding to `variance`. Used only to form  weights; values can be 1 or larger.
    condition : str
        Label used in warning messages to identify the subset being fitted.
    alpha : float, default 0.05
        Significance level for the two-sided confidence interval. Must satisfy
        `0 < alpha < 1`. The returned band has nominal coverage `1 - alpha`.

    Returns
    -------
    a, b, ci, method_used : float, dict,  {"wls", "ols"}
        Intercept (a) and slope (b). Pointwise 95% CI for the mean line with keys:
        `{"xg", "yline", "lo", "hi"}` as produced by `compute_ci_wls_ols` function.
        `method_used` - The fitting method actually used.
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    if variance is not None:
        # Build weights from per-group variance of method2:
        # Var(mean) = var / n  ⇒  weight = 1/Var(mean) = n / var

        var_arr = np.asarray(variance, dtype=float)
        n_arr = np.asarray(n, dtype=float)

        with np.errstate(divide="ignore", invalid="ignore"):
            w_arr = n_arr / var_arr
        valid = (
            np.isfinite(w_arr) & (w_arr > 0) & np.isfinite(x_arr) & np.isfinite(y_arr)
        )

        if np.count_nonzero(valid) >= 2:
            X = sm.add_constant(x_arr[valid], has_constant="add")
            results = sm.WLS(y_arr[valid], X, weights=w_arr[valid]).fit(cov_type="HC3")
            method_used = "wls"
        else:
            X = sm.add_constant(x_arr, has_constant="add")
            results = sm.OLS(y_arr, X).fit(cov_type="HC3")
            method_used = "ols"
            warnings.warn(
                f"[{condition}] WLS requested but insufficient valid weights; used OLS."
            )
    else:
        X = sm.add_constant(x_arr, has_constant="add")
        results = sm.OLS(y_arr, X).fit(cov_type="HC3")
        method_used = "ols"
        warnings.warn(
            f"[{condition}] WLS requested but no variance available; used method OLS."
        )

    a = float(results.params[0])
    b = float(results.params[1])

    ci = compute_ci_wls_ols(results, x, alpha=alpha)
    return a, b, ci, method_used


def OLS_fit(x, y, condition, alpha=0.05):
    """
    Fit the linear model ``y = a + b x`` via Ordinary Least Squares (OLS).

    Parameters
    ----------
    x, y : array-like
        Mean value per (Condition × Strain) level. Non-finite pairs are removed before fitting.
    condition : str
        Label used in warning messages to identify the subset being fitted.
    alpha : float, default 0.05
        Significance level for the two-sided confidence interval. Must satisfy
        `0 < alpha < 1`. The returned band has nominal coverage `1 - alpha`.

    Returns
    -------
    a, b, ci, method_used : float, dict,  {"wls", "ols"}
        Intercept (a) and slope (b). Pointwise 95% CI for the mean line with keys:
        `{"xg", "yline", "lo", "hi"}` as produced by `compute_ci_wls_ols` function.
        `method_used` - The fitting method actually used.
    """

    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    X = sm.add_constant(x_arr, has_constant="add")
    results = sm.OLS(y_arr, X).fit(cov_type="HC3")
    method_used = "ols"

    a = float(results.params[0])
    b = float(results.params[1])

    ci = compute_ci_wls_ols(results, x, alpha=alpha)
    return a, b, ci, method_used


def compute_ci_wls_ols(results, x, alpha=0.05, num=200):
    """
    Compute point-wise (1 - alpha) CI for fitted mean line y = a + b x from OLS/WLS fit.

    Parameters
    ----------
    results : statsmodels.regression.linear_model.RegressionResults
        Fitted results object (e.g., from `statsmodels.api.OLS` or
        `statsmodels.api.WLS`).
    x : array-like
        Original predictor values used to determine the plotting grid.
    alpha : float, default 0.05
        Significance level for the two-sided confidence interval. Must satisfy
        `0 < alpha < 1`. The returned band has nominal coverage `1 - alpha`.
    num : int, default 200
        Number of grid points between `min(x)` and `max(x)` when
        `min(x) < max(x)`. If all `x` are equal, a single-point grid is used.

    Returns
    -------
    dict : dict
        Pointwise 95% CI for the mean line with keys: `{"xg", "yline", "lo", "hi"}`. xg (grid of x), yline (fitted mean line at xg), lo (lower CI), hi (upper CI).
    """
    x = np.asarray(x, dtype=float)
    finite = np.isfinite(x)
    if not np.any(finite):
        raise ValueError("compute_ci_wls_ols: x has no finite values.")
    xmin, xmax = float(np.nanmin(x[finite])), float(np.nanmax(x[finite]))
    if xmin < xmax:
        xg = np.linspace(xmin, xmax, num)
    else:
        xg = np.unique(x[finite])

    exog = sm.add_constant(xg, has_constant="add")
    sf = results.get_prediction(exog=exog).summary_frame(alpha=alpha)
    yline = sf["mean"].to_numpy(dtype=float)
    lo = sf["mean_ci_lower"].to_numpy(dtype=float)
    hi = sf["mean_ci_upper"].to_numpy(dtype=float)

    return {"xg": xg, "yline": yline, "lo": lo, "hi": hi}


def compute_ci_odr(output, x, alpha=0.05, num=200, scale_x=1.0):
    """
    Compute point-wise (1 - alpha) Confidence interval (CI) for fitted line y = a + b x from ODR fit.

    Parameters
    ----------
    output : scipy.odr.Output
        Fitted results object (e.g., from `statsmodels.api.OLS` or
        `statsmodels.api.WLS`).
    x : array-like
        Original predictor values used to determine the plotting grid.
    alpha : float, default 0.05
        Significance level for the two-sided confidence interval. Must satisfy
        `0 < alpha < 1`. The returned band has nominal coverage `1 - alpha`.
    num : int, default 200
        Number of grid points between `min(x)` and `max(x)` when
        `min(x) < max(x)`. If all `x` are equal, a single-point grid is used.
    scale_x: If you fitted Deming by scaling x (x_scaled = x / s), pass s here so the
        parameter covariance is correctly transformed (slope divided by s, cov scaled).
        Default = 1.0.

    Returns
    -------
    dict : dict
        Pointwise 95% CI for the mean line with keys: `{"xg", "yline", "lo", "hi"}`. xg (grid of x), yline (fitted mean line at xg), lo (lower CI), hi (upper CI).
    """

    x = np.asarray(x, dtype=float)
    finite_x = np.isfinite(x)
    if not np.any(finite_x):
        raise ValueError("compute_ci_odr: x has no finite values.")

    xmin, xmax = np.nanmin(x), np.nanmax(x)
    if num and num > 1 and xmin < xmax:
        xg = np.linspace(xmin, xmax, int(num))
    else:
        xg = np.unique(x[finite_x])

    a, b = float(output.beta[0]), float(output.beta[1])

    cov = getattr(output, "cov_beta", None)
    if cov is None:
        sd = np.asarray(getattr(output, "sd_beta", [np.nan, np.nan]), dtype=float)
        cov = np.diag(sd**2)
    cov = np.asarray(cov, dtype=float)

    # If Deming via x-scaling was used in the fit (x_scaled = x / s),
    # transform covariance and slope back to the original x-scale:
    if scale_x != 1.0:
        s = float(scale_x)
        T = np.array([[1.0, 0.0], [0.0, 1.0 / s]])  # maps [a, b_scaled] -> [a, b]
        cov = T @ cov @ T.T
        b = b / s

    n = int(np.count_nonzero(finite_x))
    p = 2
    dof = max(1, n - p)

    tcrit = float(student_t.ppf(1.0 - alpha / 2.0, dof))
    if not np.isfinite(tcrit):  # Fall back option
        warnings.warn(
            f"compute_ci_odr: non-finite t critical value for dof={dof}; "
            "falling back to normal approximation (1.96).",
            RuntimeWarning,
            stacklevel=2,
        )
        tcrit = 1.96

    # Model
    yline = a + b * xg

    # Delta method: Var(a + b x) = [1, x] Σ [1, x]^T
    v_a = cov[0, 0]
    v_b = cov[1, 1]
    c_ab = cov[0, 1]
    se = np.sqrt(np.maximum(0.0, v_a + (xg**2) * v_b + 2.0 * xg * c_ab))

    lo = yline - tcrit * se
    hi = yline + tcrit * se
    return {"xg": xg, "yline": yline, "lo": lo, "hi": hi}


def compute_ci_passing_bablok(
    x,
    y,
    a,
    b,
    alpha=0.05,
    B=1000,
    num=200,
    random_state=7,
    pb_fit=None,
):
    """
    Compute point-wise (1 - alpha) Confidence interval (CI) for fitted line y = a + b x from Passing–Bablok fit.

    Parameters
    ----------
    x, y : array-like
        Mean value per (Condition × Strain) level used to obtain the PB fit.
    a, b : float
        Passing–Bablok intercept and slope for the original (x, y).
    alpha : float, default 0.05
       alpha : float, default 0.05
        Significance level for the two-sided confidence interval. Must satisfy
        `0 < alpha < 1`. The returned band has nominal coverage `1 - alpha`.
    B : int, default 1000
        Number of bootstrap resamples.
    num : int, default 200
        Number of grid points between `min(x)` and `max(x)` when
        `min(x) < max(x)`. If all `x` are equal, a single-point grid is used.
    random_state : int, default 7
        Seed for the bootstrap RNG (NumPy PCG64).
    pb_fit : callable, optional
        Callable implementing the Passing–Bablok estimator with signature
        `pb_fit(x, y) -> (a_hat, b_hat)`. Defaults to `PassingBablok_fit`.

    Returns
    -------
    dict : dict
        Pointwise 95% CI for the mean line with keys: `{"xg", "yline", "lo", "hi"}`. xg (grid of x), yline (fitted mean line at xg), lo (lower CI), hi (upper CI).
    """
    if pb_fit is None:
        pb_fit = PassingBablok_fit

    rng = np.random.default_rng(random_state)

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = x.size

    xg = np.linspace(np.nanmin(x), np.nanmax(x), int(num))
    yline = float(a) + float(b) * xg

    # Preallocate bootstrap containers
    m = xg.size
    Ys = np.full((int(B), m), np.nan, dtype=float)

    # Bootstrap resampling
    ok_draws = 0
    for bi in range(int(B)):
        idx = rng.integers(0, n, size=n)
        if np.unique(x[idx]).size < 2:
            continue
        try:
            a_b, b_b = pb_fit(x[idx], y[idx])  # reuse fitter
            Ys[ok_draws, :] = a_b + b_b * xg
            ok_draws += 1
        except Exception:
            continue
    Ys = Ys[:ok_draws, :]

    # Percentile bands
    q_lo = 100.0 * (alpha / 2.0)
    q_hi = 100.0 * (1.0 - alpha / 2.0)
    lo = np.nanpercentile(Ys, q_lo, axis=0)
    hi = np.nanpercentile(Ys, q_hi, axis=0)

    ci = {"xg": xg, "yline": yline, "lo": lo, "hi": hi}

    return ci


def compute_r2(x, y, a, b, w=None):
    """
    Compute Coefficient of determination (R²) between observed y and fitted ŷ = a + b x,
    with optional sample weights.

    Parameters
    ----------
    x, y : array-like
        Observed predictor and response.
    a, b : float
        Intercept and slope of the fitted line.
    w : array-like, optional
        Non-negative sample weights.

    Returns
    -------
    r2_score : float
        R² in `[-inf, 1]` for valid inputs; ``np.nan`` when undefined.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    y_pred = a + b * x

    if w is not None:
        w = np.asarray(w, dtype=float)
        mask = np.isfinite(y) & np.isfinite(y_pred) & np.isfinite(w) & (w >= 0)
        if not np.any(mask):
            return np.nan
        return float(r2_score(y[mask], y_pred[mask], sample_weight=w[mask]))
    else:
        mask = np.isfinite(y) & np.isfinite(y_pred)
        if not np.any(mask):
            return np.nan
        return float(r2_score(y[mask], y_pred[mask]))


def plot_standard_curve_with_ci(
    x,
    y,
    a,
    b,
    ci,
    method_used,
    alpha=0.05,
    xlabel=None,
    ylabel=None,
    title=None,
    point_labels=None,
    weights=None,
    show_r2=True,
    save=True,
):
    """
    Plot a standard-curve scatter, fitted line, and pointwise CI band.

    Parameters
    ----------
    x, y : array-like
        Observed predictor and response (one point per level).
    a, b : float
        Intercept and slope of the fitted line (`y = a + b·x`).
    ci : dict
        Confidence-band dictionary with keys:
        `{"xg", "yline", "lo", "hi"}`.
    method_used : str
        Label of the regression method shown in the plot title.
    alpha : float, default 0.05
       alpha : float, default 0.05
        Significance level for the two-sided confidence interval. Must satisfy
        `0 < alpha < 1`. The returned band has nominal coverage `1 - alpha`.
    xlabel, ylabel : str, optional
        Axis labels.
    title : str, optional
        Additional title line placed under the method label.
    point_labels : sequence of str, optional
        Text labels to annotate points.
    weights : array-like, optional
        Sample weights for R² (passed to `compute_r2`).
    show_r2 : bool, default True
        If True, append `R²` to the line legend.
    save : bool or str or os.PathLike, default True
        If True, save via `utils.save_plot` to the CWD. If a path, save
        there. If False, show the figure and do not save.

    Returns
    -------
    matplotlib.axes.Axes
        The Axes object containing the plot.
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    ax = sns.scatterplot(x=x_arr, y=y_arr, label="Strains", color="#97a6c4")

    # Optional R²
    r2_txt = ""
    if show_r2:
        try:
            r2_val = compute_r2(x_arr, y_arr, a, b, w=weights)
            if np.isfinite(r2_val):
                r2_txt = f"\nR²={r2_val:.3f}"
        except Exception:
            pass

    # Fitted line + CI
    label_eq = f"y = {a:0.3g} + {b:0.3g} x{r2_txt}"
    ax.plot(ci["xg"], ci["yline"], label=label_eq, lw=0.9, color="#a00000")
    ax.fill_between(
        ci["xg"],
        ci["lo"],
        ci["hi"],
        alpha=alpha,
        label=f"{(1-alpha)*100} % CI",
        color="#97a6c4",
    )

    # Aesthetics
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(f"{method_used} Regression\n{title}")

    # Annotate points with `Strain` values - optional
    if point_labels is not None:
        labs = list(point_labels)
        n = min(len(labs), len(x_arr), len(y_arr))
        for i in range(n):
            ax.annotate(
                str(labs[i]), (x_arr[i], y_arr[i]), ha="right", va="bottom", fontsize=8
            )

    ax.legend(bbox_to_anchor=(1, 1))

    # Saving plot
    if save is not False:
        utils.save_plot(ax.figure, save, "standard_curve", f"{method_used}_{title}")

    elif save is False:
        plt.show()
        print(f"Plot not saved.")

    return ax


def plot_bland_altman(
    m1,
    m2,
    title=None,
    point_labels=None,
    xlabel=None,
    ylabel=None,
    save=True,
    alpha=0.05,
    agreement=1.96,
    **kwargs,
):
    """
    Plot Bland–Altman (difference vs. mean) of two methods.

    Parameters
    ----------
    m1, m2 : array-like
        Measurements from method 1 and method 2. Must have the same length.
    title : str, optional
        Subtitle displayed under the main title (“Bland–Altman”).
    point_labels : sequence of str, optional
        Text labels to annotate individual points.
    xlabel, ylabel : str, optional
        Axis labels. Defaults are “Mean of methods” (x) and “Difference (M1 − M2)” (y).
    save : bool or str or os.PathLike, default True
        If True, save via :func:`utils.save_plot` to the CWD. If a path, save there.
        If False, show the figure and do not save.
    alpha : float, default 0.05
        Two-sided significance level for mean/LoA confidence intervals.
        The plotted envelope uses confidence = `1 - alpha`.
    agreement : float, default 1.96
        Multiplier for limits of agreement (e.g., 1.96 ≈ 95% for normal errors).
    **kwargs
        Passed to `pingouin.plot_blandaltman` (e.g., color, s).

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the Bland–Altman plot.
    """
    confidence = 1 - alpha

    # Draw BA plot with Pingouin (t-based CIs)
    plot = pg.plot_blandaltman(
        m1,
        m2,
        agreement=agreement,
        xaxis="mean",
        confidence=confidence,
        annotate=True,
        **kwargs,
    )
    if isinstance(plot, Axes):
        ax = plot
        fig = ax.figure
    elif isinstance(plot, Figure):
        fig = plot
        ax = fig.axes[0] if fig.axes else fig.gca()
    else:
        try:
            ax = plot.axes[0]
            fig = ax.figure
        except Exception:
            raise TypeError(
                "Unexpected return from pingouin.plot_blandaltman: expected Axes or Figure."
            )

    # Aesthetics
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if title:
        ax.set_title(f"Bland–Altman\n{f'{title}' if title else ''}")

    # Annotate points with `Strain` values - optional
    if point_labels is not None:
        m1 = np.asarray(m1, dtype=float)
        m2 = np.asarray(m2, dtype=float)
        mean_ = (m1 + m2) / 2.0
        diff = m1 - m2

        labs = list(point_labels)
        k = min(len(labs), len(mean_), len(diff))
        for i in range(k):
            ax.annotate(
                str(labs[i]), (mean_[i], diff[i]), ha="right", va="bottom", fontsize=8
            )

    if save is not False:
        utils.save_plot(fig, save, "bland_altman", title)
    elif save is False:
        plt.show()
        plt.close(fig)
        print("Plot not saved.")

    return ax


def fit_standard_curve(
    df_method1,
    df_method2,
    m1_column,
    m2_column,
    method="auto",
    alpha=0.05,
    min_levels=3,
    min_fraction_with_se=0.7,
    plot=True,
    save=True,
):
    """
    Calibrate a standard curve per `Condition` and predict values based on
    calibration method (Method 2).

    Workflow
    1) Aggregate both methods by (`Condition` × `Strain`) and keep only overlapping
       controls via `merge_methods_data`.
    2) Choose the fitting method:
        - `"wls"`: WLS with weights `w = n / variance`.
        - `"odr"`: ODR with per-point `sx, sy` if enough groups; else Deming with
        pooled variance ratio `lambda = Var_x / Var_y`; else WLS and fall back to Passing–Bablok.
        - `"ols"`: OLS.
        - `"pb"`: Passing–Bablok directly.
        - `"auto"`: Auto tries ODR(sx,sy) → Deming (λ) → WLS(y|x) if y-variance available → PB;
        Predictions: x = (y-a)/b.
    3) Compute pointwise (1-alpha) % CI for the fitted mean line.
    4) Predict values for all rows of `df_method1` within each Condition as
       `Lipids_predicted = max(0, a + b·m1)`.
    5) (Optional) Plot standard curve + CI and a Bland–Altman agreement plot.
    6) Collect agreement metrics (MSE, MAE, RMSE, R²) per-Condition for comparison to the
    reference method.

    Parameters
    ----------
    df_method1, df_method2 : pandas.DataFrame
        Input tables. Required columns `Condition`, `Strain`,
        and value columns `m1_column` and `m2_column` for each method respectively.
    m1_column, m2_column : str
        Column names of the numeric variables for Method 1 and Method 2.
    method : {'auto','odr','pb','wls', 'ols'}, default 'auto'
        Fitting strategy.
    alpha : float, default 0.05
        Significance level for the two-sided confidence interval. Must satisfy
        `0 < alpha < 1`. The returned band has nominal coverage `1 - alpha`.
    min_levels : int, default 3
        Minimum number of control levels (rows) required to fit a model in a Condition.
    min_fraction_with_se : float, default 0.7
        Minimum fraction of groups with per-point SE available (both methods) to
        allow ODR with `sx`/`sy` (when `method='odr'` or `'auto'`).
    plot : bool, default True
        If True, produce the calibration/standard curve plot and Bland–Altman plot per Condition.
    save: bool or str or os.PathLike
        If `True`, save to the current working directory using. If `str` or `PathLike`,
          treat as a file path. If `False`, do not save.

    Returns
    -------
    output_df, metrics_table : pandas.DataFrames
        1. Copy of `df_method1` with added columns: `Calibration_Method`, `a`, `b`, `Lipids_predicted`.
        2. Per-Condition agreement metrics (MSE, MAE, RMSE, R²).
    """

    # Provide aggregated data per method &
    # Filter for control strains & merge aggregated data from both methods
    controls = merge_methods_data(df_method1, df_method2, m1_column, m2_column)

    if controls.empty:
        raise ValueError("No overlapping (Condition, Strain) between the two methods.")

    if not (0 < alpha < 1):
        raise ValueError("alpha must satisfy 0 < alpha < 1")

    output_df = df_method1.copy()
    output_df["Calibration_Method"] = pd.NA
    output_df["a"] = pd.NA
    output_df["b"] = pd.NA
    output_df["Lipids_predicted"] = pd.NA

    table_dict = {}

    # Obtain per Condition data
    for condition, sub in controls.groupby("Condition", dropna=False):
        y = sub[f"{m1_column}_mean"]
        x = sub[f"{m2_column}_mean"]
        sy = sub[f"{m1_column}_se"]
        sx = sub[f"{m2_column}_se"]
        vary = sub[f"{m1_column}_var"]
        varx = sub[f"{m2_column}_var"]
        ny = sub[f"{m1_column}_n"]
        nx = sub[f"{m2_column}_n"]

        if len(sub) < min_levels:
            warnings.warn(
                f"[{condition}] < {min_levels} strains; skipping calibration."
            )
            continue

        sx_arr = np.asarray(sx, dtype=float)
        sy_arr = np.asarray(sy, dtype=float)

        mask_sx = np.isfinite(sx_arr) & (sx_arr > 0)
        mask_sy = np.isfinite(sy_arr) & (sy_arr > 0)
        mask_both = mask_sx & mask_sy

        # Model/Method selection
        chosen = method.lower()
        if chosen == "auto":
            n_total = len(sub)
            min_frac = float(min_fraction_with_se)
            min_weighted_pts = max(3, min_levels)

            need = max(min_weighted_pts, int(np.ceil(min_frac * max(1, n_total))))
            enough_ODR = np.count_nonzero(mask_both) >= need
            enough_WLS = np.count_nonzero(mask_sy) >= need

            if enough_ODR:
                # if sufficient SE_y & SE_x
                chosen = "odr"
            elif enough_WLS or (nx == 1).all():
                # if sufficient SE_y & x are singeltons
                chosen = "wls"
            else:
                # will try Deming, then WLS, then OLS
                chosen = "odr"

        a = b = np.nan
        method_used = None

        try:
            if chosen == "wls":
                a, b, ci, method_used = WLS_fit(x, y, vary, ny, condition, alpha=alpha)

            elif chosen == "ols":
                vary = None
                ny = None
                a, b, ci, method_used = OLS_fit(x, y, condition, alpha=alpha)

            elif chosen == "pb":
                a, b = PassingBablok_fit(x, y)
                ci = compute_ci_passing_bablok(
                    x, y, a, b, alpha=alpha, B=1000, pb_fit=PassingBablok_fit
                )
                method_used = "Passing-Bablok"

            elif chosen == "odr":
                # Prefer ODR with per-point sx,sy if both have enough levels
                n_both = int(np.count_nonzero(mask_both))
                need = max(min_levels, int(np.ceil(min_fraction_with_se * len(sub))))
                if n_both >= need:
                    a, b, ci = ODR_fit(
                        x[mask_both],
                        y[mask_both],
                        sx=sx[mask_both],
                        sy=sy[mask_both],
                        alpha=alpha,
                    )
                    method_used = f"ODR(sx,sy; n={n_both}/{len(sub)})"
                else:
                    # Deming with pooled lambda (per-group)
                    vx = pooled_variance(varx, nx)
                    vy = pooled_variance(vary, ny)
                    ok = (
                        (vx is not None)
                        and (vy is not None)
                        and np.isfinite(vx)
                        and np.isfinite(vy)
                        and (vy > 0)
                    )
                    if ok:
                        lam = vx / vy  # lambda = Var_x / Var_y
                        a, b, ci = ODR_fit(x, y, lam=lam, alpha=alpha)
                        method_used = f"ODR(Deming, lambda={lam:.3g})"

                    with np.errstate(divide="ignore", invalid="ignore"):
                        w_try = ny / vary
                        can_wls = np.isfinite(w_try) & (w_try > 0)
                        if can_wls.sum() >= 2:
                            a, b, ci, method_used = WLS_fit(
                                x, y, vary, ny, condition, alpha=alpha
                            )
                        else:
                            try:
                                X_ = sm.add_constant(
                                    np.asarray(x, dtype=float), has_constant="add"
                                )
                                ols_ = sm.OLS(np.asarray(y, dtype=float), X_).fit()
                                stud = ols_.get_influence().resid_studentized_internal
                                out_rate = float(np.mean(np.abs(stud) > 3))
                            except Exception:
                                out_rate = 1.0
                            if out_rate >= 0.10:
                                a, b = PassingBablok_fit(x, y)
                                ci = compute_ci_passing_bablok(
                                    x,
                                    y,
                                    a,
                                    b,
                                    alpha=alpha,
                                    B=1000,
                                    pb_fit=PassingBablok_fit,
                                )
                                method_used = "Passing-Bablok"
                            else:
                                a, b, ci, method_used = OLS_fit(
                                    x, y, condition, alpha=alpha
                                )

            else:
                raise ValueError(
                    "Method must be one of : 'auto','odr','pb','wls' or 'ols'."
                )

        except Exception as e:
            warnings.warn(
                f"[{condition}] Fit failed with {chosen}: {e}. Falling back to Passing–Bablok."
            )
            a, b = PassingBablok_fit(x, y)
            ci = compute_ci_passing_bablok(
                x, y, a, b, alpha=alpha, B=1000, pb_fit=PassingBablok_fit
            )
            method_used = "Passing-Bablok"

        # Value predictions
        # Predict for all df_m1 rows per Condition
        mask_rows = output_df["Condition"].eq(condition)

        # Predict & Set negative values to 0 (`.clip(lower=0)`)
        # x = (y-a)/b
        predictions = (
            output_df.loc[mask_rows, m1_column].astype("float64") - float(a)
        ) / float(b)
        predictions = predictions.where(np.isfinite(predictions)).clip(lower=0)

        if not np.isfinite(b) or abs(b) < 1e-12:
            warnings.warn(f"[{condition}] Slope ~ 0; cannot invert for predictions.")
            continue

        output_df.loc[mask_rows, "Lipids_predicted"] = predictions.astype(float)

        output_df.loc[mask_rows, "a"] = float(a)
        output_df.loc[mask_rows, "b"] = float(b)
        output_df.loc[mask_rows, "Calibration_Method"] = method_used

        # Plotting
        if plot:
            # weights for R² only if WLS was used
            w_for_r2 = None
            if isinstance(method_used, str) and method_used.lower() == "wls":
                # weights ~ n / variance (same definition you used in WLS)
                w_for_r2 = (ny / vary).replace([np.inf, -np.inf], pd.NA)

            # Define Strain labels (aligned to rows order)
            labels = sub["Strain"].unique() if "Strain" in sub.columns else None

            plot_standard_curve_with_ci(
                x,
                y,
                a,
                b,
                ci,
                method_used,
                alpha=alpha,
                xlabel=m2_column,
                ylabel=m1_column,
                title=f"Condition: {condition}",
                point_labels=labels,
                weights=w_for_r2,
                show_r2=True,
                save=save,
            )

            # Provide predicted values; x = (y-a)/b
            m1_predicted = (sub[f"{m1_column}_mean"] - float(a)) / float(b)

            # Values of Method 2
            y_true = sub[f"{m2_column}_mean"].to_numpy(dtype=float)

            # Plot Bland-Altman plot - Agreement between methods
            plot_bland_altman(
                m1=m1_predicted,
                m2=y_true,
                title=condition,
                point_labels=labels,
                xlabel=f"Mean of Lipids_predicted & {m2_column}",
                ylabel=f"Difference: Lipids_predicted - {m2_column}",
                save=save,
                alpha=alpha,
                agreement=1.96,
            )

            # Compute MSE, MAE, RMSE, R2 comparing values
            mse = mean_squared_error(y_true, m1_predicted)
            mae = mean_absolute_error(y_true, m1_predicted)
            rmse = np.sqrt(mean_squared_error(y_true, m1_predicted))
            r2 = r2_score(y_true, m1_predicted)

            # Prepare dict for table
            table_dict[f"{condition}"] = [mse, mae, rmse, r2]

    if table_dict:
        # Create report table
        table = pd.DataFrame.from_dict(
            table_dict,
            orient="index",
            columns=[
                "Mean Squared Error (MSE)",
                "Mean Absolute Error (MAE)",
                "Root Mean Squared Error (RMSE)",
                "R² Score",
            ],
        )
    else:
        table = None

    # Saving (optional)
    if save is not False:
        if isinstance(save, (str, os.PathLike)):
            target = os.fspath(save)
            if os.path.isdir(target):
                pred_path = os.path.join(target, "standard_curve_predictions.csv")
                metrics_path = os.path.join(target, "standard_curve_metrics.csv")
            else:
                pred_path = target if os.path.splitext(target)[1] else f"{target}.csv"
                metrics_path = os.path.join(
                    os.path.dirname(pred_path),
                    f"{os.path.splitext(os.path.basename(pred_path))[0]}_metrics.csv",
                )

        elif save is True:
            pred_path = os.path.join(os.getcwd(), "standard_curve_predictions.csv")
            metrics_path = os.path.join(os.getcwd(), "standard_curve_metrics.csv")

        # Save prediction data
        output_df.to_csv(pred_path, sep=",", index=False)
        print(f"Predictions saved to: {os.path.abspath(pred_path)}")

        # Save report table
        if table is not None:
            table.to_csv(metrics_path, sep=",", index=False)
            print(f"Agreement Metrics saved to: {os.path.abspath(metrics_path)}")
            return output_df, table.style.set_caption("Method Agreement Metrics")

        return output_df

    # Return
    else:
        if table is not None:
            return output_df, table.style.set_caption("Method Agreement Metrics")
        else:
            return output_df
