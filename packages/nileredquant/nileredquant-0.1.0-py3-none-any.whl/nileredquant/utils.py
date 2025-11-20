import pandas as pd
import re
import numpy as np
import os
import matplotlib.pyplot as plt
import nileredquant.qc as qc


def read_file(filename, sheet_name=None, dtype=None):
    """
    Read a CSV/TSV/XLSX file into a DataFrame (first column as index).

    Parameters
    ----------
    filename : str or os.PathLike
        Path to the input file. Supported extensions (case-insensitive):
        `.csv`, `.tsv`, `.xlsx`.
    sheet_name : int or str, optional
        Excel sheet to read when `filename` is `.xlsx`.
        Defaults to the first sheet when ``None``.
    dtype : dict or str, optional
        Dtype(s) to enforce. For Excel files, pandas may not be able to
        enforce all dtypes on read; this function will attempt a best-effort
        post-cast for columns specified in a dtype dict.

    Returns
    -------
    pandas.DataFrame
        DataFrame with the first column used as index.
    """
    # Check input
    if filename.endswith(".csv"):
        df = pd.read_csv(filename, sep=None, engine="python", index_col=0, dtype=dtype)

    elif filename.endswith("tsv"):
        df = pd.read_csv(filename, sep="\t", index_col=0, dtype=dtype)

    elif filename.endswith(".xlsx"):
        sheet_name = 0 if sheet_name is None else sheet_name
        df = pd.read_excel(filename, index_col=0, sheet_name=sheet_name, dtype=dtype)

    else:
        raise ValueError(
            f"Unsupported file format provided. Only .csv, .tsv and .xlsx allowed."
        )

    return df


def fix_strain_dtype(x):
    """
    Normalize a single Strain label to a canonical string.

    Numeric-like inputs (e.g., 1, 1.0, '001', '12.0') are converted to their
    integer string form (`'1'`, `'12'`) when the numeric value is an integer.
    Non-integer numerics (e.g., `'12.5'`) are returned as their trimmed string.
    Non-numeric inputs are returned as trimmed strings unchanged.

    Parameters
    ----------
    x : Any
        A single value from the `Strain` column (scalar).

    Returns
    -------
    str or pandas.NA
        Canonicalized string label. Missing values (NaN/NA) are returned as `pandas.NA`.


    """
    x_str = str(x)
    try:
        # Convert value to string
        val = float(x_str)
        # If it's an integer float, change it to integer string
        if val.is_integer():
            return str(int(val))
        else:
            # a non-integer float stays non-integer float but string
            return x_str
    except ValueError:
        # If not numeric at all (e.g. 'ABC123'), just return it
        return x_str


def plate_to_list(filename, parameter, save=True):
    """
    Reshape data from a microtiter plate format to a long format indexed by column `Well`.

    Parameters
    ----------
    filename : str, os.PathLike or pandas.DataFrame
        Path to a plate-layout table (CSV/TSV/XLSX; rows = letters A.., cols = 1..N),
        or an in-memory DataFrame already in plate layout.
        The first column is treated as the row index when reading from file.
    parameter : str
        Name for the value column in the long table (e.g., `Strain`, `Abs`, `FI_bg`).
    save : bool, default True
        If True and `filename` is a path, write `<base>_<parameter>_long.csv` next to the input.

    Returns
    -------
    long_df : pandas.DataFrame
        Long-format DataFrame with index ``Well`` (e.g., 'A1', 'B12') and one column `parameter`.
    """
    # Check input
    filename_new = None
    if isinstance(filename, (str, os.PathLike)):
        if parameter == "Strain":
            df = read_file(filename, sheet_name=parameter, dtype={parameter: "str"})
        else:
            df = read_file(filename, sheet_name=parameter)
        filename_new = os.path.basename(filename)
    elif isinstance(filename, pd.DataFrame):
        df = filename.copy()
    elif isinstance(filename, pd.Series):
        df = df.to_frame()
    else:
        raise TypeError(
            "`filename` must be a either a path or a pandas.DataFrame/pandas.Series"
        )

    # Reshape data
    long_df = (
        df.stack(future_stack=True)
        .rename_axis(index=["Row", "Col"])
        .reset_index(name=parameter)
    )

    # Cosmetics, dtype & concat
    long_df["Row"] = long_df["Row"].astype(str).str.upper()
    long_df["Col"] = pd.to_numeric(long_df["Col"], errors="coerce").astype(int)
    long_df["Well"] = long_df["Row"] + long_df["Col"].astype(str)

    # Sort - alphanumeric on Row & Col
    long_df = (
        long_df.sort_values(["Row", "Col"])
        .loc[:, ["Well", parameter]]
        .set_index("Well")
    )

    if parameter == "Strain":
        long_df[parameter] = long_df[parameter].apply(fix_strain_dtype)

    if save:
        if isinstance(save, (str, os.PathLike)):
            target = os.fspath(save)
            if os.path.isdir(target):
                def_fn = f"Plate_to_list_{parameter}_long.csv"
                new_filename = os.path.join(target, f"{def_fn}")
            else:
                new_filename = (
                    target if os.path.splitext(target)[1] else f"{target}.csv"
                )

        elif save is True:
            if filename_new:
                fn_new = filename_new.split(".")[0]
                new_filename = os.path.join(os.getcwd(), f"{fn_new}_long.csv")
            else:
                new_filename = os.path.join(
                    os.getcwd(), f"Plate_to_list_{parameter}_long.csv"
                )

        long_df.to_csv(f"{new_filename}", sep=",")

    return long_df


def list_to_plate(filename, parameter, save=True):
    """
    Convert a long-format table with `Well` IDs back to a microtiter plate layout format.

    Parameters
    ----------
    filename : str, os.PathLike or pandas.DataFrame
        Either a path to a file loadable by `read_file` or a long-format
        DataFrame. Required columns: `Well`and a value column named by `parameter`.
    parameter : str
        Name of the value column to pivot (e.g., `Strain`, `Abs`, `FI_bg`).
    save : bool, default True
        If True and `filename` is a path, write `<base>_<parameter>_list_to_plate.csv`
        next to the input.

    Returns
    -------
    plate_df: pandas.DataFrame
        Plate layout with rows as letters (A..H/P) and columns as integers (1..12/24).
        Missing wells appear as NaN.
    """
    filename_new = None
    # Check input
    if isinstance(filename, (str, os.PathLike)):
        df = read_file(filename, sheet_name=parameter)
        filename_new = os.path.basename(filename)
    elif isinstance(filename, pd.DataFrame):
        df = filename.copy()
    elif isinstance(filename, pd.Series):
        df = df.to_frame()
    else:
        raise TypeError(
            "`filename` must be a either a path or a pandas.DataFrame/pandas.Series"
        )

    # Check if column Well in df
    if "Well" not in df.columns:
        if df.index.name == "Well":
            df = df.reset_index()
        else:
            raise ValueError("Missing `Well` column (or index named `Well`).")

    if parameter not in df.columns:
        raise ValueError(f"Column '{parameter}' not found in input.")

    wells = qc.normalize_wells(df["Well"])

    # Pivot the long format data into a wide format for the plate layout
    df["col"] = wells.apply(lambda x: x[0])
    df["row"] = wells.apply(lambda x: x[1:])

    plate_df = df.pivot(index="row", columns="col", values=parameter).T

    # Reorder the columns in the correct order
    plate_df = plate_df[np.arange(1, len(plate_df.columns) + 1).astype(str)]

    if save:
        if isinstance(save, (str, os.PathLike)):
            target = os.fspath(save)
            if os.path.isdir(target):
                def_fn = f"List_to_plate_{parameter}.csv"
                new_filename = os.path.join(target, f"{def_fn}")
            else:
                new_filename = (
                    target if os.path.splitext(target)[1] else f"{target}.csv"
                )

        elif save is True:
            if filename_new:
                fn_new = filename_new.split(".")[0]
                new_filename = os.path.join(os.getcwd(), f"{fn_new}.csv")
            else:
                new_filename = os.path.join(
                    os.getcwd(), f"List_to_plate_{parameter}.csv"
                )

        plate_df.to_csv(f"{new_filename}", sep=",")

    return plate_df


def alphanumeric_sort_key(s):
    """
    Natural (alphanumeric) sort key that sorts digit numerically (e.g. A1, A2, A10,..).
    Splits digit from string value.

    Parameters
    ----------
    s : Any
        Value to transform into a sort key. Non-strings are
        converted to string.

    Returns
    -------
    tuple
        A tuple of parts where digit substrings are converted to integers and
        non-digit substrings are case-folded strings. Suitable for use as the
        `key` in sorting.

    """
    if not isinstance(s, str):
        s = str(s)
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split("([0-9]+)", s)
    ]


def map_metadata(filename, data, save=True, sheet_name=None):
    """
    Read a metadata table and align/merge it to `data` by `Well`
    column, in natural (alphanumeric) order.

    Parameters
    ----------
    filename : str or os.PathLike
        Path to the metadata file accepted by `read_file`. Must contain a
        Well identifier either as a column named `Well` or as the index
        (first column in the file).
    data : pandas.DataFrame
        Data to be merged with metadata. Must also contain Well identifiers,
        either in a `Well` column or in the index.
    save : bool, default True
        If True and `filename` is a path, write the merged table next to
        the input as `<base>_w_metadata.csv`.

    Returns
    -------
    metadata : pandas.DataFrame
        Merged table, sorted alphanumerically by Well (A1, A2, …, H12 / P24).
        The output contains a `Well` column and all columns from both inputs.
    """
    filename_new = None
    # Check input
    if isinstance(filename, (str, os.PathLike)):
        metadata = read_file(filename, sheet_name=sheet_name)
        filename_new = os.path.basename(filename)
    elif isinstance(filename, pd.DataFrame):
        metadata = filename.copy()
    elif isinstance(filename, pd.Series):
        metadata = metadata.to_frame()
    else:
        raise TypeError(
            "`filename` must be a either a path or a pandas.DataFrame/pandas.Series"
        )

    if "Well" not in metadata.reset_index().columns:
        raise ValueError("The 'Well' column is missing in the provided file.")

    # Sort Well column
    metadata_sorted = metadata.sort_values(
        by="Well", key=lambda x: x.map(alphanumeric_sort_key)
    )

    # Merge with data
    metadata = metadata_sorted.reset_index().merge(data, how="inner")

    if save:
        if isinstance(save, (str, os.PathLike)):
            target = os.fspath(save)
            if os.path.isdir(target):
                new_filename = os.path.join(target, f"Data_w_metadata.csv")
            else:
                new_filename = (
                    target if os.path.splitext(target)[1] else f"{target}.csv"
                )

        elif save is True:
            if filename_new:
                fn_new = filename_new.split(".")[0]
                new_filename = os.path.join(os.getcwd(), f"{fn_new}_w_metadata.csv")
            else:
                new_filename = os.path.join(os.getcwd(), f"Data_w_metadata.csv")

        metadata.to_csv(f"{new_filename}", sep=",")

    return metadata


def default_plot_name(plot_name, title=None):
    """
    Build a filename from a plot base name and optional title.

    Parameters
    ----------
    plot_name : Any
        Base name of the plot (e.g., 'Heatmap').
    title : Any, optional
        Extra descriptor appended after an underscore (e.g., condition, method).

    Returns
    -------
    name : str
        A filesystem-friendly filename ending with `.pdf`.
    """
    plot = str(plot_name)
    title = str(title)
    extra = "_".join([s for s in [title] if s])
    name = f"{plot}_{extra}" if extra else plot
    name = re.sub(r"[^\w.\-]+", "_", name).strip("_")
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name


def save_plot(fig, save, plot_name, title, close=True):
    """
    Save a figure to PDF using a consistent naming policy & path definition.

    Parameters
    ----------
    fig : matplotlib.figure.Figure or matplotlib.axes.Axes
        Figure to save. If an `Axes` is provided, its parent `Figure` is used.
    save : bool or str or os.PathLike
        If `True`, save to the current working directory using
          `default_plot_name(plot_name, title)`. If `str` or `PathLike`,
          treat as a file path. If the path has no extension, `.pdf` is appended.
          If `False`, do not save (early return).
    plot_name : Any
        Base name for the output file (e.g., `Heatmap`).
    title : Any
        Extra descriptor appended to the base name (e.g., condition/method).
    close : bool, default True
        If `True`, closes the figure after saving to free memory.

    Returns
    -------
    str or None
        Absolute path to the saved file, or `None` if `save` is `False`.
    """
    # Save to provided path
    if isinstance(save, (str, os.PathLike)):
        target = os.fspath(save)
        if os.path.isdir(target):
            fname = default_plot_name(plot_name, title)
            filepath = os.path.join(target, fname)
        else:
            filepath = target if os.path.splitext(target)[1] else f"{target}.pdf"

    # Save to current working directory
    elif save is True:
        fname = default_plot_name(plot_name, title)
        filepath = os.path.join(os.getcwd(), fname)

    # Don't save
    else:
        return

    # Saving
    fig.savefig(filepath, bbox_inches="tight", format="pdf")
    plt.show()
    print(f"Plot saved to: {os.path.abspath(filepath)}")

    # Close plot
    if close:
        try:
            plt.close(fig)
        except Exception:
            pass
