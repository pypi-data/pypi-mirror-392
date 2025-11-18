# powerlawrs

[![PyPI version](https://img.shields.io/pypi/v/powerlawrs.svg)](https://pypi.org/project/powerlawrs/)
[![License: MIT OR Apache-2.0](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-blue.svg)](./LICENSE-MIT)

`powerlawrs` is a Python package for analyzing power-law distributions in empirical data. It is built on a high-performance Rust crate [powerlaw](https://github.com/aulichny3/powerlaw), providing both speed and ease of use for Python users. The methodology is heavily based on the techniques and statistical framework described in the paper ['Power-Law Distributions in Empirical Data'](https://doi.org/10.1137/070710111) by Aaron Clauset, Cosma Rohilla Shalizi, and M. E. J. Newman.

## Features

-   **Parameter Estimation**: Estimates the parameters (`x_min`, `alpha`) of a power-law distribution from data.
-   **Goodness-of-Fit**: Uses the Kolmogorov-Smirnov (KS) statistic to find the best-fitting parameters.
-   **High Performance**: Computationally intensive tasks are parallelized in the Rust core for significant speedups.
-   **Flexible API**: Offers both a simple functional API for quick analyses and a class-based API for more detailed work.

## Installation

### Prerequisites

-   Python 3.8+
-   Rust (the package is built from Rust source)
-   `uv` (this project uses [uv](https://docs.astral.sh/uv/) for environment and package management)

### Setup and Installation via pip
1. **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    uv venv -p powerlaw

    # Activate the environment
    source powerlaw/bin/activate
    ```
2. **Install the package.**
    ```bash
    uv pip install powerlawrs
    ```

### Setup and Installation from Source

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/aulichny3/powerlawrs.git
    cd powerlawrs
    ```

2.  **Create and activate a virtual environment:**
    This project is configured to use the `powerlaw` virtual environment with `uv`.
    ```bash
    # Create the environment
    uv venv -p powerlaw

    # Activate the environment
    source powerlaw/bin/activate
    ```

3.  **Install the package:**
    To install the package in editable mode and include all development dependencies, run:
    ```bash
    # Install the package using maturin
    maturin develop

    # Install development dependencies
    uv pip install -r requirements.txt
    ```
    This installs `powerlawrs` in editable mode, so any changes you make to the source code will be immediately available.

## Dependencies

-   The core `powerlawrs` library has no Python dependencies.
-   Development dependencies (for running the example [notebooks](https://github.com/aulichny3/powerlawrs/blob/main/Notebooks/)) are listed in `requirements.txt` and include:
    -   `jupyterlab`: For running the example notebooks.
    -   `numpy`: Used in the example notebooks.
    -   `polars`: Used for data loading in the example notebooks.
    -   `matplotlib`: Used for data-via in the Quickstart notebook.

## Usage

`powerlawrs` offers two primary ways to analyze your data: a simple functional API and a more detailed class-based API.

### Functional API (Recommended)

The `powerlawrs.fit()` function is the most straightforward way to fit a power-law distribution to your data. See the [Quickstart](https://github.com/aulichny3/powerlawrs/blob/main/Notebooks/01%20-%20Quickstart.ipynb) notebook for an example.

```python
import powerlawrs
import polars as pl

# 1. Load your data into a list or Polars Series
# The data should be a 1-dimensional array of numbers.
file = "reference_data/blackouts.txt"
data = pl.read_csv(file, has_header=False).to_series().to_list()

# 2. Fit the data
fit_results = powerlawrs.fit(data)

# 3. Print the results
print(f"Alpha: {fit_results.alpha}")
print(f"X_min: {fit_results.x_min}")
print(f"KS Statistic: {fit_results.D}")
print(f"Tail Length: {fit_results.len_tail}")
```

### Class-based API

For more fine-grained control, you can see the API examples in `Notebooks/02 - API.ipynb`.

### Jupyter Notebook Examples

The `Notebooks folders provides a detailed walkthrough of the package's functionalities. After installing the development dependencies, you can run it with:

```bash
# Make sure your virtual environment is active
source powerlaw/bin/activate

# Start Jupyter Lab
uv run jupyter lab
```

## Limitations

1.  Only the continuous case of the Pareto Type I Distribution is considered for parameter estimation, goodness of fit, and hypothesis testing at this time. The example data in the documentation is discrete, thus the results are only an approximation.
2.  Domain knowledge of the data generating process is critical given the methodology used by this package is based on that proposed by the referenced material. Specifically the 1-sample Kolmogorov-Smirnov test is used for goodness of fit testing which assumes i.i.d data. Many natural processes data are serially correlated, thus KS testing is not appropriate.
3.  This is highly alpha code; backwards compatibility is not guaranteed and should not be expected.
4.  Many more known and unknown.

## License

This project is licensed under either of:

-   Apache License, Version 2.0, ([LICENSE-APACHE](./LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
-   MIT license ([LICENSE-MIT](./LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.