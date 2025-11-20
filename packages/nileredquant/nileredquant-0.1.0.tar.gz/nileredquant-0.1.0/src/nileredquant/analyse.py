import pandas as pd
import numpy as np
import warnings
import os
import nileredquant.utils as utils
import nileredquant.qc as qc


def subtract_background_absorbance(
    data, blanks, absorbance_column="Abs", contamination_thr=0.2
):
    """
    Subtract background absorbance within each Condition group.

    Parameters
    ----------
    data : pandas.DataFrame
        Input table. Required columns: absorbance column, `Condition` & `Strain` ( only when blank is a string label).
    blanks: str, float or list
       Either one value to be subtracted from the absorbance column, list of float values per Condition or `Strain` column label (string) identifying blank wells.
    absorbance_column: str
        Column name of raw Absorbance values. Should not be named `Absorbance`. Default is `Abs`.
    contamination_thr : float
        Threshold for flagging/removing contaminated blank wells when using a
        string label (rows with `Abs >= contamination_thr` are dropped before
        computing per-condition blank means.
    -------
    tuple of pandas.DataFrames, float
        1. Copy of `data`: whole data with subtracted blanks in new column `Absorbance`.
        2. data_wo_blanks: data with removed blank wells if present at input.
        3. Blank value used for background absorbance subtraction.
    """
    if not {f"{absorbance_column}", "Condition"}.issubset(data.columns):
        raise KeyError(f"Columns `{absorbance_column}` and `Condition` are required.")
    if "Absorbance" in data.columns:
        raise ValueError(
            f"Invalid `absorbance_column` name. 'Absorbance' is a reserved for output. Please rename."
        )

    data = data.copy()
    # Check blank type

    # one value -> str, float
    if (isinstance(blanks, str) and blanks.replace(".", "", 1).isdigit()) or isinstance(
        blanks, (float, int)
    ):

        blank_data = float(blanks)
        data["Absorbance"] = (data[absorbance_column] - blank_data).round(4)
        data_wo_blanks = data

        return data, data_wo_blanks, blank_data

    # layout/well label
    elif isinstance(blanks, str) and not blanks.isnumeric():

        if "Strain" not in data.columns:
            raise KeyError(
                "Column `Strain` is required when `blanks` is a string label."
            )

        blank_label = blanks
        blank_ind = data.loc[data["Strain"] == blank_label].index
        blank_data = data.loc[blank_ind]

        # Drop potential contamination of blank wells;
        # Drop values above or equal to contamination_thr
        contamination = blank_data[absorbance_column] >= contamination_thr
        if contamination.any():
            warnings.warn(
                f"Dropping {int(contamination.sum())} blank wells with possible contamination ({absorbance_column} ≥ {contamination_thr}).",
                RuntimeWarning,
                stacklevel=2,
            )
            blank_data = blank_data.loc[~contamination]

        # Calculate the average value
        condition_blanks = blank_data.groupby("Condition")[absorbance_column].mean()

        data["Blank_Value"] = data["Condition"].map(condition_blanks).fillna(0)
        data["Absorbance"] = (data[absorbance_column] - data["Blank_Value"]).round(4)
        data.drop(columns=["Blank_Value"], inplace=True)

        data_wo_blanks = data.drop(index=blank_ind)
        return data, data_wo_blanks, condition_blanks

    elif isinstance(blanks, (list, tuple)):

        blank_arr = np.asarray(blanks)

        n_cond = data.Condition.nunique()
        condition_order = data.Condition.unique()

        if blank_arr.size != n_cond:
            raise ValueError(
                f"Expected {n_cond} numeric blank values (one per condition "
                f"in order {condition_order.tolist()}), got {blank_arr.size}."
            )

        condition_blanks = pd.Series(blank_arr, index=condition_order, dtype="float64")
        data["Blank_Value"] = data["Condition"].map(condition_blanks).fillna(0)
        data["Absorbance"] = (data[absorbance_column] - data["Blank_Value"]).round(4)
        data.drop(columns=["Blank_Value"], inplace=True)
        data_wo_blanks = data
        return data, data_wo_blanks, condition_blanks

    else:
        raise ValueError(
            f"Invalid `blanks` type. Provide a string label in `Strain` columns, a numeric value (str, numeric) or sequence of numbers (len == number of conditions). Details described in documentation."
        )


def get_fluorescence_signal(data, fi_bg_col="FI_bg", fi_fp_col="FI_fp"):
    """
    Get Fluorescence signal by subtracting the background fluorescence from probe fluorescence.

    Parameters
    ----------
    data : pandas.DataFrame
        Input table. Required columns: background fluorescence intensity (e.g. `FI_bg`) & fluorescence intensity of the fluorescent probe (e.g. `FI_fp`).
    fi_bg_col: str
        Column name of background fluorescence intensity values. Defaults to `FI_bg`.
    fi_fp_col: str
         Column name of fluorescent probe fluorescence intensity values.  Defaults to `FI_fp`.

    Returns
    -------
    data: pandas.DataFrame
        Copy of `data` with a new column `Fluorescence`, representing subtracted background fluorescence intensity. Non-numeric entries (e.g., 'INVALID')
        are coerced to missing values.
    """

    data = data.copy()

    # Replace invalid values with NaNs
    data = data.replace("INVALID", pd.NA)

    # dtype
    background_FI = pd.array(data.loc[:, fi_bg_col].round(0).values, dtype="Int64")
    fluorescence_probe_FI = pd.array(
        data.loc[:, fi_fp_col].round(0).values, dtype="Int64"
    )
    if background_FI is None or fluorescence_probe_FI is None:
        raise KeyError(f"Columns `{fi_bg_col}` and `{fi_fp_col}` not found.")

    # Subtract background fluorescence
    data = data.assign(Fluorescence=fluorescence_probe_FI - background_FI)
    data.Fluorescence = data.Fluorescence.round(0)

    return data


def signal_biomass_normalisation(data):
    """
    Normalise the Fluorescence Intensity (`Fluorescence`) by Biomass (`Absorbance`) and apply log transform.

    Parameters
    ----------
    data : pandas.DataFrame
        Input table.  Required columns: `Absorbance` (biomass proxy with subtracted blank) and `Fluorescence` (background-subtracted fluorescence).

    Returns
    -------
    data: pandas.DataFrame
        Copy of ``data`` with two added columns:`Lipids` = (FI/A), representing biomass normalised fluorescence intensity and `Log(Lipids)`, representing
        natural logarithm of `Lipids` variable.
    """

    data = data.copy()

    # Add a small number for log
    eps = 1e-9
    data_temp_FI = data.Fluorescence + eps
    data_temp_OD = data.Absorbance + eps

    if data_temp_FI is None or data_temp_OD is None:
        raise KeyError(
            "Columns `Fluorescence` and `Absorbance` not found but required."
        )

    # Biomass normalisation FI/A
    data["Lipids"] = data_temp_FI.div(data_temp_OD).round(3)

    # Variance stabilisation - log
    data["Log(Lipids)"] = data.Lipids.apply(
        lambda x: np.log(x).round(3) if x > 0 else np.nan
    )

    return data


def analyse(
    filename,
    blanks,
    absorbance_column="Abs",
    contamination_thr=0.2,
    fi_bg_col="FI_bg",
    fi_fp_col="FI_fp",
    outlier_method="IQR",
    outlier_columns=None,
    save=True,
):
    """
    Automated analysis of fluorescence data. 1) read file, 2) subtract background absorbance, 3) subtract background
    fluorescence, 4) normalize by biomass & log, 5) detect and drop outliers.

    Parameters
    ----------
    filename : str or os.PathLike
        Path to the input file accepted by function `utils.read_file`.
    blanks : float or str
        Background specification for absorbance subtraction passed to
        function `subtract_background_absorbance`
    absorbance_column: str
        Column name of raw Absorbance values. Should not be named `Absorbance`. Default is `Abs`.
    contamination_thr : float, default 0.2
        Threshold for flagging/removing contaminated blank wells when using a
        string label.
    fi_bg_col: str
        Column name of background fluorescence intensity values. Defaults to `FI_bg`.
    fi_fp_col: str
         Column name of fluorescent probe fluorescence intensity values.  Defaults to `FI_fp`.
    outlier_method : str, default `IQR`
        Outlier detection method; either 'IQR', 'Z-score' or 'MAD-Median'. Defaults to 'IQR'.
    outlier_columns: list, default None
        List of Column names to be used for outlier detection. If None, all numerical values are considered.
        In that case, the union/ANY rule is used: being an outlier in any selected column (within its group) is enough to mark the row as an outlier.
    save : bool, default True
        If True, save the normalized + outlier-flagged table and the outliers
        table next to `filename` (CSV). If False, do not write files.

    Returns
    -------
    tuple of pandas.DataFrames
        1. data: Copy of original data with added `Absorbance`, `Fluorescence`,`Lipids`, `Log(Lipids)` and `Outlier` (boolean) columns and removed blank wells.
        2. data_wo_outliers: Data with outlier rows removed.
        3. outliers: Detected outliers.
    """

    # Check input
    if isinstance(filename, (str, os.PathLike)):
        # Import experiment file
        data = utils.read_file(filename)
        filename = os.path.basename(filename)
        new_filename = f"{filename.split('.')[0]}_"
    elif isinstance(filename, pd.DataFrame):
        data = filename.copy()
        new_filename = ""
    else:
        raise TypeError("`filename` must be a either a path or a pandas.DataFrame")

    # Subtract the background (Blank) Absorbance
    data, data_wo_blanks, blank = subtract_background_absorbance(
        data,
        blanks,
        contamination_thr=contamination_thr,
        absorbance_column=absorbance_column,
    )

    print(f"The blank Absorbance value(s) used: {blank}")

    # Subtract the background fluorescence
    data_w_FI = get_fluorescence_signal(
        data_wo_blanks, fi_bg_col=fi_bg_col, fi_fp_col=fi_fp_col
    )

    # Normalise signal to Biomass (Absorbance) & log
    data_normalised = signal_biomass_normalisation(data_w_FI)

    # Detect outliers per Condition & Strain
    data_results_all, data_results_wo_outliers, outliers = qc.detect_outliers(
        data_normalised,
        ["Strain", "Condition"],
        method=outlier_method,
        columns=outlier_columns,
    )

    if "Well" not in data.columns:
        if data.index.name == "Well":
            data = data.reset_index()

    # Merge original data with processed results
    data_all = data.merge(data_results_all, how="left")

    # Saving (optional)
    if save:
        data_all.to_csv(f"{new_filename}NileredQuant_results_all.csv", sep=",")
        data_results_wo_outliers.to_csv(
            f"{new_filename}NileredQuant_results_wo_outliers.csv", sep=","
        )
        outliers.to_csv(f"{new_filename}NileredQuant_outliers.csv", sep=",")

    return data_all, data_results_wo_outliers, outliers
