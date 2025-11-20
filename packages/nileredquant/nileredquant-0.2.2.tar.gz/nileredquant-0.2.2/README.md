# ***NileRedQuant*** — Tool for Automated Neutral Lipid Quantification in Yeasts

*Table of Contents*
- [Overview](#Overview)
  - [Key Features](#Key-Features)
  - [Citing](#Citing)
- [Installation](#Installation)
- [Quick Start](#Quick-Start)
- [Documentation](#Documentation)
- [Licence](#Licence)


## Overview
**NileRedQuant** is a tool designed for automated analysis and data processing of Nile red-based plate assays used to quantify neutral lipids in yeasts.

It provides an analysis pipeline to turn raw fluorescence intensities into quality-checked, biomass-normalized lipid readouts, with optional calibration to a reference method (e.g., Gravimetric analysis, TLC, …) for lipid content prediction. **NileRedQuant** supports both 96-well and 384-well assay formats, offering increased throughput and flexibility.

Starting from plate reader exports, it imports and reshapes data, subtracts *'blanks'* and background fluorescence intensities, normalizes the fluorescence signal to biomass (*Absorbance*) providing the *`Lipid`* signal and flags outliers per *`Strain`* × *`Condition`*.

The module *`standard_curve()`* offers optional calibration of control strains/individuals against a reference method to compute predicted *lipid content*.

### Key Features
1. **I/O & plate utilities**
    - Import `.csv`, `.tsv`, or `.xlsx` files;
    - convert between microtiter plate layouts and long (tidy) format;
    - attach metadata.

1. **Blank & background fluorescence handling**

Subtract blank absorbance per *`Condition`* using either a numeric value(s) or a designated string label  in *`Strain`* column.

$$ Absorbance = Abs - Abs_{blank} $$

Subtract background fluorescence intensity and compute the fluorescence signal as:

$$ Fluorescence = FI_{fp} − FI_{bg} $$

1. **Biomass normalization & variance-stabilisation**
Derive the *`Lipid`* signal as:

$$ Lipids = \frac{Fluorescence}{Absorbance} $$

Variance stabilisation:

$$ log(Lipids) = log(\frac{Fluorescence}{Absorbance}) $$

1. **Plate-level QC**
    - Detect outliers per *`Strain`* × *`Condition`*  using one of the implemented methods IQR (default), Z-score or MAD-median available.
    - Provide convenience plots (histograms, strip+box, strip+violin, QQ-plot, heatmaps) to review data quality.

1. **Standard-curve fitting & method agreement (optional)**
  Calibrate NileRedQuant `Lipids` signal to a reference method per `Condition`.
  The `method='auto'` selects among implemented linear regressions:
    1. ODR (errors-in-variables / Deming) when both axes have replicate SE or a stable variance ratio $\lambda = \frac{\sigma_x^2}{\sigma_y^2}$ can be estimated.
    1. WLS when all reference groups (`Strain` × `Condition`) are singletons, and for each group the within-group variance of the reference method can be computed.
  WLS uses weights proportional to its inverse: ($\text{weights} \propto n/\text{variance}$).Falls back to OLS if weights aren’t available
  (variance missing or fewer than 3 positive, finite weights remain).
    1. Passing–Bablok (non-parametric, robust) fallback method when not enough SE on both axes or no stable λ are available.

  Outputs include per-Condition slope/intercept, predictions written back to your data, and optional standard-curve & Bland–Altman plots.

### Citing

Please cite the peer-reviewed article describing full methodological details and validation of NileRedQuant (coming soon).

   > [Authors] (2025). ***NileRedQuant: Automated analysis and calibration of Nile red plate assays for neutral lipid quantification in yeasts***. [Link text - doi]()

## Installation

PyPI:
```bash
   pip install nileredquant
```

Developers:
```bash
  # Clone the repo
   git clone https://github.com/zganjarmia/NileRedQuant
   cd NileRedQuant

   # Create a separate environment & install
   python -m venv .venv && source .venv/bin/activate
   pip install -e .
```

Supported Python versions: `3.9–3.11`

*Dependencies:*
- `pandas (≥2.2.0)`,
- `scipy (≥1.11.4)`,
- `penguin (≥0.5.3)`,
- `matplotlib (≥3.8.0)`,
- `openpyxl (≥3.1.2)`

## Quick Start


```python
  # Import `NileRedQuant`
  from nileredquant import utils, analyse, standard_curve, qc
```

Import data:
```python
  # Import data .csv file
  data = utils.read_file(filename="./raw_data.csv")

  # Or Excel
  data = utils.read_file(
    filename="./raw_data.xlsx",
    sheet_name=None  # <-- First sheet is taken, if column name not provided
  )
```

Analayse & compute the `Lipids` & `Log(Lipids)` variables.

```python
  # `B` value represents the unique identifier of the 'Blank' in `Strain` column.
  data, data_wo_outliers, outilers =  analyse.analyse(
    filename=data,  # Can be either Path or pandas.DataFrame
    blanks="B",
    contamination_thr=0.2,
    outlier_method='IQR',
    outlier_columns=['Lipids'],   # detect outliers only in the `Lipids` variable
    save = True)
```


Prepare standard curve of control strains & predict values for other strains in data frame.

```python

  # Import data of reference method (e.g. gravimetric, TLC, ...)

  data_reference_method = utils.read_file(filename="./data_example_reference_method.csv")

  # Fit standard curve & predict
  data_predicted, agreement_table =  standard_curve.fit_standard_curve(
    df_method1=data,
    df_method2=data_reference_method,
    m1_column='Lipids',
    m2_column="TLC_mg/gCDW",
    method='auto',
    plot=True,
    save=True,
  )
```
See **[usage_examples/](./usage_examples/)** for more details.

## Documentation
The API reference is available in the  [usage_examples/00_API.html](./usage_examples/00_API.html) file.

Browse the [usage_examples/](./usage_examples/) directory for end-to-end workflows and function-level demos. Each example is self-contained and runnable with the provided data once dependencies are installed.


## License

MIT © 2025 Mia Žganjar. See ``LICENSE``.

