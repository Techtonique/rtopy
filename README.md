# rtopy

Lightweight Python bridge for calling R functions with seamless type conversion.

![PyPI](https://img.shields.io/pypi/v/rtopy) [![PyPI - License](https://img.shields.io/pypi/l/rtopy)](https://github.com/thierrymoudiki/rtopy/blob/master/LICENSE) [![Downloads](https://pepy.tech/badge/rtopy)](https://pepy.tech/project/rtopy) 
[![Downloads](https://anaconda.org/conda-forge/rtopy/badges/downloads.svg)](https://anaconda.org/conda-forge/rtopy)
[![Documentation](https://img.shields.io/badge/documentation-is_here-green)](https://techtonique.github.io/rtopy/)

## Features

- **Simple API**: Call R functions with native Python types
- **Auto type conversion**: Supports int, float, str, bool, list, dict, numpy, pandas
- **Minimal dependencies**: Only requires R + jsonlite package
- **Library support**: Use any R package in your functions
- **Fast**: Direct subprocess execution, no rpy2 overhead

## Installation

```bash
# Install package
pip install rtopy

# Install with optional numpy/pandas support
pip install rtopy[full]

# Requires R to be installed and in PATH
# Install R from: https://cran.r-project.org/
# Install jsonlite in R: install.packages("jsonlite")
```

## Quick Start

```python
from rtopy import RBridge, call_r

# One-off function call
result = call_r(
    r_code="add <- function(x, y) x + y",
    r_func="add",
    x=5, 
    y=3
)
print(result)  # 8.0

# Reusable bridge
rb = RBridge()

# Statistical analysis
code = '''
library(stats)
analyze <- function(data) {
    list(
        mean = mean(data),
        median = median(data),
        sd = sd(data)
    )
}
'''
stats = rb.call(code, "analyze", return_type="dict", data=[1,2,3,4,5])
print(stats)  # {'mean': 3.0, 'median': 3.0, 'sd': 1.58...}

# Return as pandas DataFrame
code = '''
make_data <- function(n) {
    data.frame(
        x = 1:n,
        y = rnorm(n),
        group = sample(c("A", "B"), n, replace=TRUE)
    )
}
'''
df = rb.call(code, "make_data", return_type="pandas", n=100)
```

## Return Types

- `"auto"`: Automatically infer best type (default)
- `"int"`, `"float"`, `"str"`, `"bool"`: Python scalars
- `"list"`, `"dict"`: Python collections
- `"numpy"`: NumPy array (requires numpy)
- `"pandas"`: pandas DataFrame/Series (requires pandas)
- `"raw"`: Raw JSON-parsed output

## Advanced Usage

```python
# Custom timeout and verbose mode
rb = RBridge(timeout=60, verbose=True)

# Use any R package
code = '''
library(dplyr)
library(ggplot2)

process_data <- function(values) {
    df <- data.frame(x = values)
    df %>%
        mutate(squared = x^2) %>%
        summarise(mean_x = mean(x), mean_squared = mean(squared))
}
'''
result = rb.call(code, "process_data", data=[1, 2, 3, 4, 5])

# Pass NumPy arrays and pandas DataFrames
import numpy as np
import pandas as pd

arr = np.array([1, 2, 3, 4, 5])
result = rb.call(code, "my_func", data=arr)

df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
result = rb.call(code, "another_func", df=df)
```

## Requirements

- Python >= 3.7
- R >= 3.6
- R package: jsonlite

Optional:
- numpy >= 1.19 (for numpy return type)
- pandas >= 1.1 (for pandas return type)

## License

BSD License Clause Clear

## Notes to self 

1. [https://conda-forge.org/docs/maintainer/adding_pkgs/#step-by-step-instructions](https://conda-forge.org/docs/maintainer/adding_pkgs/#step-by-step-instructions)

```bash
curl -sL https://github.com/owner/repo/archive/refs/tags/vX.X.X.tar.gz | openssl sha256 (https://conda-forge.org/docs/maintainer/adding_pkgs/#step-by-step-instructions)
```

2. [https://github.com/conda-forge/rtopy-feedstock](https://github.com/conda-forge/rtopy-feedstock)



