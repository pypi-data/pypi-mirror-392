import string
import warnings
import pandas as pd
from pandas.api.types import is_numeric_dtype
import numpy as np
import scipy.stats as stats
from scipy.stats import zscore
import pingouin as pg
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
import nileredquant.utils as utils


def outliers_z_score(data, group, columns=None, threshold=1.96, ddof=0):
    """
    Detect and separate outliers from specific columns based on per-group Z-score (default threshold 1.96).

    Parameters
    ----------
    data : pandas.DataFrame
        Input table. Can contain numerical and non-numerical columns.
    group : str or list
        Grouping variable(s) to apply for Z-score calculations (e.g. [`Condition`,`Strain`])
    columns : list, optional
        List of columns to check for outliers. If None, all numerical columns will be used.
    threshold : float, optional
        Z-score threshold for defining an outlier.

    Returns
    -------
    tuple of pandas.DataFrame
        1. data_wo_outliers: Data with outlier rows removed.
        2. outliers: Detected outliers.
    """

    # Use only specified columns or default to all numerical columns
    if columns is None:
        columns = data.select_dtypes(include=[np.number]).columns.tolist()
    else:
        missing = [c for c in columns if c not in data.columns]
        if missing:
            raise ValueError(f"Columns not found in DataFrame: {missing}")

    if len(columns) == 0:
        raise ValueError("No numerical columns available for outlier detection.")

    def _z_per_group(s):
        """
        Compute Z-scores per column & per group.
        """
        a = s.to_numpy(dtype=float, copy=False)
        z = zscore(a, nan_policy="omit", ddof=ddof)

        # For constant groups zscore->nan; treat as 0 so they aren't flagged
        # treat std==0 as z=0 for those entries
        z = np.where(np.isfinite(z), z, 0.0)
        return pd.Series(z, index=s.index)

    Z = data.groupby(group, dropna=False)[columns].transform(_z_per_group).abs()
    is_outlier = Z.gt(threshold).any(axis=1)
    data_wo_outliers = data.loc[~is_outlier].copy()
    outliers = data.loc[is_outlier].copy()

    return data_wo_outliers, outliers


def outliers_madmedianrule(data, group, columns=None):
    """
    Detect and separate outliers from selected columns using per-group MAD-median rule.

    Parameters
    ----------
    data : pandas.DataFrame
        Input table. Can contain numerical and non-numerical columns.
    group : str or list
        Grouping variable(s) to apply MAD-median rule (e.g. [`Condition`,`Strain`])
    columns : list, optional
        List of columns to check for outliers. If None, all numerical columns will be used.

    Returns
    -------
    tuple of pandas.DataFrame
        1. data_wo_outliers: Data with outlier rows removed.
        2. outliers: Detected outliers.
    """

    # Use only specified columns or default to all numerical columns
    if columns is None:
        columns = data.select_dtypes(include=[np.number]).columns.tolist()
    else:
        missing = [c for c in columns if c not in data.columns]
        if missing:
            raise ValueError(f"Columns not found in DataFrame: {missing}")

    if len(columns) == 0:
        raise ValueError("No numerical columns available for outlier detection.")

    grouped_data = data.groupby(group, dropna=False)

    # Per-column (boolean) mask
    masks = []
    for col in columns:
        m = grouped_data[col].transform(lambda s: pg.madmedianrule(s.to_numpy()))
        masks.append(m.astype(bool))

    is_outlier = pd.concat(masks, axis=1).any(axis=1)
    data_wo_outliers = data.loc[~is_outlier].copy()
    outliers = data.loc[is_outlier].copy()

    return data_wo_outliers, outliers


def outliers_iqr(data, group, columns=None):
    """
    Detect and separate outliers from specific columns based on per-group interquartile range (IQR).

    Parameters
    ----------
    data : pandas.DataFrame
        Input table. Can contain numerical and non-numerical columns.
    group : str or list
        Grouping variable(s) to apply IQR (e.g. [`Condition`,`Strain`])
    columns : list, optional
        List of columns to check for outliers. If None, all numerical columns will be used.

    Returns
    -------
    tuple of pandas.DataFrame
        1. data_wo_outliers: Data with outlier rows removed.
        2. outliers: Detected outliers.
    """

    # Use only specified columns or default to all numerical columns
    if columns is None:
        columns = data.select_dtypes(include=[np.number]).columns
    else:
        missing = [c for c in columns if c not in data.columns]
        if missing:
            raise ValueError(f"Columns not found in DataFrame: {missing}")

    if len(columns) == 0:
        raise ValueError("No numerical columns available for outlier detection.")

    # Group data
    gb = data.groupby(group, dropna=False)

    # Get quantiles & compute IQR
    q1 = gb[columns].transform(lambda s: s.quantile(0.25))
    q3 = gb[columns].transform(lambda s: s.quantile(0.75))
    iqr = q3 - q1

    # Determine bounds
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # Values equal to bounds are NOT considered as outliers
    low = data[columns].lt(lower_bound)
    high = data[columns].gt(upper_bound)

    is_outlier = (low | high).any(axis=1)
    outliers = data.loc[is_outlier].copy()
    data_wo_outliers = data.loc[~is_outlier].copy()

    return data_wo_outliers, outliers


def detect_outliers(data, group, method="IQR", columns=None):
    """
    Detects outliers based on the provided grouping, outlier detection method ('IQR', 'Z-score' or 'MAD-Median'), and specific columns.

    Parameters
    ----------
    data : pandas.DataFrame
        Input table. Can contain numerical and non-numerical columns.
    group : str or list
        Grouping variable(s). Can be a list of variables.
    method : str, optional
        Outlier detection method; either 'IQR', 'Z-score' or 'MAD-Median'. Defaults to 'IQR'.
    columns : list, optional
        List of columns to check for outliers. If None, all numerical columns will be used.

    Returns
    -------
    tuple of pandas.DataFrames
        1. data: Copy of original data with added `Outlier` column (boolean).
        2. data_wo_outliers: Data with outlier rows removed.
        3. outliers: Detected outliers.
    """
    if not isinstance(data, pd.DataFrame):
        raise ValueError("First argument must be a pandas DataFrame.")
    if not isinstance(group, (str, list, tuple)):
        raise ValueError("Group must be a string or a list/tuple of strings.")

    if method.lower() in ["z-score", "zscore"]:
        data_wo_outliers, outliers = outliers_z_score(data, group, columns)
    elif method.lower() == "iqr":
        data_wo_outliers, outliers = outliers_iqr(data, group, columns)
    elif method.lower() in ["mad-median", "madmedian"]:
        data_wo_outliers, outliers = outliers_madmedianrule(data, group, columns)
    else:
        raise ValueError("Invalid method. Choose 'iqr', 'zscore', or 'madmedian'.")

    # Marking outliers
    data_flagged = data.copy()
    if "Outlier" in data_flagged.columns:
        warnings.warn(
            "Column 'Outlier' already exists and will be overwritten.",
            RuntimeWarning,
            stacklevel=2,
        )

    data_flagged["Outlier"] = data_flagged.index.isin(outliers.index)

    return data_flagged, data_wo_outliers, outliers


def canonical_wells(plate_format):
    """Create Well positions based on plate format."""
    pf = str(plate_format).lower().replace("_well", "")
    if pf == "96":
        rows = list(string.ascii_uppercase[:8])  # A–H
        cols = list(range(1, 12 + 1))  # 1–12
    elif pf == "384":
        rows = list(string.ascii_uppercase[:16])  # A–P
        cols = list(range(1, 24 + 1))  # 1–24
    else:
        raise ValueError("plate_format must be either '96' or '384'.")
    return [f"{r}{c}" for r in rows for c in cols]


def normalize_wells(s):
    """Uppercase, strip, remove spaces, drop leading zeros in the numeric part."""
    s = s.astype(str).str.strip().str.upper().str.replace(r"\s+", "", regex=True)
    s = s.str.replace(r"^([A-Z]+)0*([0-9]+)$", r"\1\2", regex=True)  # A01 -> A1
    ok = s.str.match(r"^[A-Z]+[0-9]+$")
    if not ok.all():
        bad = s[~ok].unique()[:5]
        raise ValueError(
            f"Invalid Well labels (e.g., {list(bad)}). Expected like 'A1', 'B12'."
        )
    return s


def plot_heatmap(data, columns, plate_format, save=True, annotate=True):
    """
    Generate heatmaps in a microtiter plate format for one or more variables.

    Parameters
    ----------
    data : pandas.DataFrame
        Input table. Required column `Well`. Can contain numerical and non-numerical columns.
    columns : str or list of str
        Name(s) of column(s) to plot.
    plate_format : {'96', '384'}
        Plate format used to generate a canonical list of wells (96 or 384).
    save : bool or str or os.PathLike, default True
        If True, save to CWD via `utils.save_plot` function. If a path, save there.
        If False, only show the plot.
    annotate : bool, default True
        Whether to annotate each cell with its value.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure containing the heatmaps.
    """
    if isinstance(columns, str):
        columns = [columns]
    elif isinstance(columns, list) and all(isinstance(c, str) for c in columns):
        pass
    else:
        raise TypeError("`columns` must be a string or a list of strings.")

    if not columns:
        raise RuntimeError("`columns` is empty.")

    # Check for columns in data
    missing = [c for c in columns if c not in data.columns]
    if missing:
        raise KeyError(f"Columns not found in data: {missing}")

    data = data.copy()

    # Check for Well column
    if "Well" not in data.columns:
        if data.index.name == "Well":
            data = data.reset_index()
    elif "Well" in data.columns:
        wells = normalize_wells(data["Well"])
        data["Well"] = wells
    else:
        raise ValueError(
            "Column `Well`(or index named `Well`) not found but required ."
        )

    # Create new Well variable & merge with existing
    base = pd.DataFrame({"Well": canonical_wells(plate_format)})
    organised_df = base.merge(data, on="Well", how="left", validate="one_to_one")

    # Sort by `Well`
    organised_df = organised_df.sort_values(
        by="Well", key=lambda x: x.map(utils.alphanumeric_sort_key)
    )

    # Define plot figsize based on format
    plot_dict = {"96": {"figsize": (10, 10)}, "384": {"figsize": (13, 13)}}

    # Iterate through Variables
    for col in columns:

        plate_df = utils.list_to_plate(organised_df, col, save=False)

        if plate_df.shape not in {(8, 12), (16, 24)}:
            raise RuntimeError(
                f"Unexpected plate shape {plate_df.shape}; expected 8x12 (96-well plate) or 16x24 (384-well plate)."
            )

        fig, ax = plt.subplots(1, 1, figsize=plot_dict[plate_format]["figsize"])

        # Set up for numeric variables/columns
        if is_numeric_dtype(organised_df[col]):
            data_mat = plate_df.astype(float).values
            annot_mat = plate_df.values if annotate else False
            cmap_obj = plt.get_cmap("Blues").copy()
            vmin, vmax, fmt, cbar_flag, cbar_kws = (
                np.nanmin(organised_df[col].values),
                np.nanmax(organised_df[col].values),
                ".3g",
                True,
                {"shrink": 0.5},
            )

        # Set up for non-numeric variables/columns
        else:
            flat_vals = plate_df.values.ravel(order="C")
            vals = np.full(flat_vals.shape, np.nan)
            mask = ~pd.isna(flat_vals)
            vals[mask], cats = pd.factorize(flat_vals[mask])
            data_mat = vals.reshape(plate_df.shape).astype(float)
            annot_mat = plate_df.values if annotate else False
            n_cat = len(cats)
            cmap_obj = ListedColormap(sns.color_palette("Set3", n_cat))
            vmin, vmax, fmt = -0.5, n_cat - 0.5, ""  # discrete bins
            cbar_flag = n_cat > 1
            cbar_kws = {"shrink": 0.5, "ticks": np.arange(n_cat)} if cbar_flag else None

        # for missing values
        cmap_obj.set_bad("white")

        # Plot
        hm = sns.heatmap(
            data_mat,
            cmap=cmap_obj,
            ax=ax,
            annot=annot_mat,
            linewidth=0.5,
            vmin=vmin,
            vmax=vmax,
            fmt=fmt,
            linecolor="white",
            square=True,
            cbar=cbar_flag,
            cbar_kws=cbar_kws,
            annot_kws={"size": 8},
        )

        # Aesthetics
        ax.set_xlabel("Microtiter Plate Column", fontsize=12)
        ax.set_ylabel("Microtiter Plate Row", fontsize=12)
        ax.set_title(f"Variable: `{col}`", fontsize=16)
        ax.set_xticklabels(
            np.arange(1, len(plate_df.columns) + 1), rotation=0, fontsize=12
        )
        ax.set_yticklabels(
            list(string.ascii_uppercase)[: len(plate_df.index)], fontsize=12
        )

        if hm.collections and hm.collections[0].colorbar is not None:
            cbar = hm.collections[0].colorbar
            cbar.ax.tick_params(labelsize=12)
            if not is_numeric_dtype(organised_df[col]):
                cbar.set_ticklabels([str(c) for c in cats])
                cbar.set_label(col)

        fig.tight_layout()

        # Saving plot
        if save is not False:
            utils.save_plot(fig, save, "Heatmap", f"{col}_{plate_format}")

        elif save is False:
            plt.show()
            print(f"Plot not saved.")

    return fig


def plot_histogram(data, columns, save=True):
    """
    Plot histograms by Condition for one or more numeric variables.

    Parameters
    ----------
    data : pandas.DataFrame
        Input table. Required columns `Condition` and the numeric column(s) to plot.
    columns : str or list of str
        Name(s) of numeric column(s) to plot.
    save : bool or str or os.PathLike, default True
        If True, save to CWD via `utils.save_plot` function. If a path, save there.
        If False, only show the plot.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure containing the histogram plot.
    """
    if isinstance(columns, str):
        columns = [columns]
    elif isinstance(columns, list) and all(isinstance(c, str) for c in columns):
        pass
    else:
        raise TypeError("`columns` must be a string or a list of strings.")

    if not columns:
        raise RuntimeError("`columns` is empty.")

    # Check for columns in data
    missing = [c for c in columns if c not in data.columns]
    if missing:
        raise KeyError(f"Columns not found in data: {missing}")

    # Iterate through Variables
    for col in columns:

        fig, ax = plt.subplots(figsize=(10, 6))

        sns.histplot(
            data=data,
            x=col,
            hue="Condition",
            element="step",
            stat="count",
            palette="pastel",
            multiple="stack",
            alpha=0.5,
            color="RdYlBu",
            ax=ax,
        )
        # Aesthetics
        ax.set_xlabel(f"{col}", fontsize=12)
        ax.set_ylabel("Count", fontsize=12)
        ax.set_title(f"'{col}' Distribution by Condition", fontsize=14)

        sns.move_legend(
            ax, "upper left", bbox_to_anchor=(1, 1), fontsize=10, title_fontsize=12
        )

        plt.tight_layout()

        # Saving plot
        if save is not False:
            utils.save_plot(fig, save, "Histogram", f"{col}")

        elif save is False:
            plt.show()
            print(f"Plot not saved.")

    return fig


def plot_strip_box(data, columns, exclude_strains=None, save=True):
    """
    Generate Strip + box plots by Strain and Condition, with optional strain exclusion.
    strip plots with either box or violin plots overlaid. Highlights outliers with red border.

    Parameters
    ----------
    data : pandas.DataFrame
        Input table. Required columns `Condition`, `Strain` and the numeric column(s) to plot.
    columns : str or list of str
        Name(s) of numeric column(s) to plot on the y-axis.
    exclude_strains : str or list of str, optional
        Strain label(s) to exclude from plotting.
    save : bool or str or os.PathLike, default True
        If True, save to CWD via :func:`utils.save_plot`. If a path, save there.
        If False, only show the plot.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure containing the strip plots.
    """

    if isinstance(columns, str):
        columns = [columns]
    elif isinstance(columns, list) and all(isinstance(c, str) for c in columns):
        pass
    else:
        raise TypeError("`columns` must be a string or a list of strings.")

    if not columns:
        raise RuntimeError("`columns` is empty.")

    # Check for columns in data
    missing = [c for c in columns if c not in data.columns]
    if missing:
        raise KeyError(f"Columns not found in data: {missing}")

    # Iterate through Variables
    for col in columns:

        fig, ax = plt.subplots(1, 1, figsize=(15, 6))

        if isinstance(exclude_strains, list):

            data = data[~data.Strain.isin(exclude_strains)]

        elif isinstance(exclude_strains, str):

            data = data[data.Strain != exclude_strains]

        # Plot
        sns.stripplot(
            data=data,
            ax=ax,
            x="Strain",
            y=col,
            hue="Condition",
            palette="deep",
            dodge=True,
            jitter=False,
            linewidth=1,
            marker="o",
            edgecolor=None,
            legend=False,
        ).tick_params(axis="x", rotation=90)

        sns.boxplot(
            data=data,
            ax=ax,
            x="Strain",
            y=col,
            hue="Condition",
            palette="deep",
            dodge=True,
            boxprops=dict(alpha=0.3),
        )

        # Aesthetics
        ax.set_xlabel("Strain", fontsize=14)
        ax.set_ylabel(f"{col}", fontsize=14)
        ax.set_title(f"'{col}'", fontsize=16)
        ax.tick_params(labelsize=14)

        plt.tight_layout()

        # Saving plot
        if save is not False:
            utils.save_plot(fig, save, "Strip_Box_plot", f"{col}")

        elif save is False:
            plt.show()
            print(f"Plot not saved.")

    return fig


def plot_strip_violin(data, columns, exclude_strains=None, save=True):
    """
    Generate Strip + Violin plots by Strain and Condition, with optional strain exclusion.
    strip plots with either box or violin plots overlaid. Highlights outliers with red border.

    Parameters
    ----------
    data : pandas.DataFrame
        Input table. Required columns `Condition`, `Strain` and the numeric column(s) to plot.
    columns : str or list of str
        Name(s) of numeric column(s) to plot on the y-axis.
    exclude_strains : str or list of str, optional
        Strain label(s) to exclude from plotting.
    save : bool or str or os.PathLike, default True
        If True, save to CWD via :func:`utils.save_plot`. If a path, save there.
        If False, only show the plot.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure containing the strip plots.
    """

    if isinstance(columns, str):
        columns = [columns]
    elif isinstance(columns, list) and all(isinstance(c, str) for c in columns):
        pass
    else:
        raise TypeError("`columns` must be a string or a list of strings.")

    if not columns:
        raise RuntimeError("`columns` is empty.")

    # Check for columns in data
    missing = [c for c in columns if c not in data.columns]
    if missing:
        raise KeyError(f"Columns not found in data: {missing}")

    # Iterate through Variables
    for col in columns:

        fig, ax = plt.subplots(1, 1, figsize=(15, 6))

        if isinstance(exclude_strains, list):

            data = data[~data.Strain.isin(exclude_strains)]

        elif isinstance(exclude_strains, str):

            data = data[data.Strain != exclude_strains]

        # Plot
        sns.stripplot(
            data=data,
            ax=ax,
            x="Strain",
            y=col,
            hue="Condition",
            palette="deep",
            dodge=True,
            jitter=False,
            linewidth=1,
            marker="o",
            edgecolor=None,
            legend=False,
        ).tick_params(axis="x", rotation=90)

        sns.violinplot(
            data=data,
            ax=ax,
            x="Strain",
            y=col,
            hue="Condition",
            palette="deep",
            dodge=True,
        )

        # Aesthetics
        ax.set_xlabel("Strain", fontsize=14)
        ax.set_ylabel(f"{col}", fontsize=14)
        ax.set_title(f"'{col}'", fontsize=16)
        ax.tick_params(labelsize=14)

        plt.tight_layout()

        # Saving plot
        if save is not False:
            utils.save_plot(fig, save, "Strip_Violin_plot", f"{col}")

        elif save is False:
            plt.show()
            print(f"Plot not saved.")

    return fig


def plot_qq(data, columns, save=True):
    """
    Generate Q-Q plots per `Condition` for the requested numeric column(s).

    Parameters
    ----------
    data : pandas.DataFrame
        Input table. Required columns `Condition` and the numeric columns to test.
    columns : str or list of str
        Name(s) of numeric column(s) to plot.
    save : bool or str or os.PathLike, default True
        If True, save to CWD via :func:`utils.save_plot`. If a path, save there.
        If False, only show the plot.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure containing the Q-Q plots.
    """

    if isinstance(columns, str):
        columns = [columns]
    elif isinstance(columns, list) and all(isinstance(c, str) for c in columns):
        pass
    else:
        raise TypeError("`columns` must be a string or a list of strings.")

    if not columns:
        raise RuntimeError("`columns` is empty.")

    # Check for columns in data
    missing = [c for c in columns if c not in data.columns]
    if missing:
        raise KeyError(f"Columns not found in data: {missing}")

    # Iterate through Variables
    fig = None
    for col in columns:

        conditions = data["Condition"].unique()
        if conditions.size == 0:
            raise ValueError("No conditions found in 'Condition' column.")

        fig, axes = plt.subplots(1, len(conditions), figsize=(8 * len(conditions), 8))

        for i, condition in enumerate(conditions):
            ax = axes[i]

            # get data points
            condition_data = data.loc[data["Condition"].eq(condition), col].to_numpy()
            condition_data = condition_data[np.isfinite(condition_data)]

            if condition_data.size < 3:
                ax.text(
                    0.5,
                    0.5,
                    f"Insufficient data\nn={condition_data.size} for condition: {condition} and variable: {col}. ",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
                ax.set_title(f"Q–Q plot: `{col}` · `{condition}`", fontsize=14)
                ax.xaxis.label.set_size(14)
                ax.yaxis.label.set_size(14)
                ax.tick_params(labelsize=14)
                ax.set_axis_off()
                continue

            pg.qqplot(condition_data, dist="norm", confidence=0.95, square=True, ax=ax)
            ax.set_title(f"Q–Q plot: `{col}` · `{condition}`", fontsize=14)
            ax.xaxis.label.set_size(14)
            ax.yaxis.label.set_size(14)
            ax.tick_params(labelsize=14)

        fig.tight_layout()

        # Saving plot
        if save is not False:
            utils.save_plot(fig, save, "Strip_Box_plot", f"{col}")

        elif save is False:
            plt.show()
            print(f"Plot not saved.")

        return fig
