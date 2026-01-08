"""Core bridge functionality."""

import subprocess
import json
import tempfile
import os
from typing import Any, Dict, List, Union, Optional

from .exceptions import RExecutionError, RNotFoundError, RTypeError

# Optional dependencies
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class RBridge:
    """Lightweight bridge for calling R functions from Python."""

    def __init__(self, timeout: int = 300, verbose: bool = False):
        """
        Initialize R bridge.

        Parameters
        ----------
        timeout : int
            Maximum execution time in seconds (default: 300)
        verbose : bool
            Print R warnings and messages (default: False)
        """
        self.timeout = timeout
        self.verbose = verbose
        self._check_r()

    def _check_r(self):
        """Verify R is available."""
        try:
            subprocess.run(
                ["Rscript", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
        except subprocess.TimeoutExpired:
            raise RNotFoundError("R check timed out")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RNotFoundError(
                "R not found. Please install R and add to PATH.\n"
                "Download from: https://cran.r-project.org/"
            )

    def call(
        self, r_code: str, r_func: str, return_type: str = "auto", **kwargs
    ) -> Any:
        """
        Call R function with automatic type conversion.

        Parameters
        ----------
        r_code : str
            R code defining the function (can include library() calls)
        r_func : str
            Function name to call
        return_type : str
            Output type: "auto", "int", "float", "str", "bool",
            "list", "dict", "numpy", "pandas", "raw"
        **kwargs
            Arguments passed to R function

        Returns
        -------
        Result converted to requested Python type

        Raises
        ------
        RNotFoundError
            If R is not installed or not in PATH
        RExecutionError
            If R script fails to execute
        RTypeError
            If type conversion fails

        Examples
        --------
        >>> rb = RBridge()
        >>>
        >>> # Simple calculation
        >>> code = "add <- function(x, y) x + y"
        >>> rb.call(code, "add", x=5, y=3)
        8.0
        >>>
        >>> # Statistical summary
        >>> code = '''
        ... summarize <- function(x) {
        ...     list(mean=mean(x), sd=sd(x), n=length(x))
        ... }
        ... '''
        >>> rb.call(code, "summarize", return_type="dict", x=[1,2,3,4,5])
        {'mean': 3.0, 'sd': 1.58..., 'n': 5}
        """
        if r_func not in r_code:
            raise ValueError(f"Function '{r_func}' not found in r_code")

        # Convert Python inputs to R-compatible format
        r_args = self._serialize_args(kwargs)

        # Build and execute R script
        r_script = self._build_script(r_code, r_func, r_args)
        output = self._execute_r(r_script)

        # Parse and convert output
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError as e:
            raise RExecutionError(f"Invalid JSON from R: {output[:200]}") from e

        return self._convert_output(parsed, return_type)

    def _serialize_args(self, kwargs: Dict) -> str:
        """Convert Python args to R-compatible JSON."""
        converted = {}

        for k, v in kwargs.items():
            if HAS_NUMPY and isinstance(v, np.ndarray):
                converted[k] = v.tolist()
            elif HAS_PANDAS and isinstance(v, pd.DataFrame):
                converted[k] = v.to_dict("list")
            elif HAS_PANDAS and isinstance(v, pd.Series):
                converted[k] = v.tolist()
            else:
                converted[k] = v

        json_str = json.dumps(converted)
        return json_str.replace("\\", "\\\\").replace("'", "\\'")

    def _build_script(self, r_code: str, r_func: str, r_args: str) -> str:
        """Build R script with error handling."""
        return f"""
suppressPackageStartupMessages({{
    {r_code.strip()}
    
    args <- jsonlite::fromJSON('{r_args}')
    
    result <- tryCatch(
        do.call({r_func}, args),
        error = function(e) stop("R error in {r_func}: ", e$message)
    )
    
    json_out <- jsonlite::toJSON(
        result,
        auto_unbox = TRUE,
        force = TRUE,
        digits = 15,
        null = "null",
        na = "null",
        dataframe = "columns"
    )
    
    cat(json_out, "\\n")
}})
"""

    def _execute_r(self, script: str) -> str:
        """Execute R script and return stdout."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".R", delete=False, encoding="utf-8"
        ) as f:
            f.write(script)
            temp_file = f.name

        try:
            proc = subprocess.run(
                ["Rscript", "--vanilla", temp_file],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if self.verbose and proc.stderr:
                print(f"[R messages] {proc.stderr}")

            if proc.returncode != 0:
                error_msg = proc.stderr or proc.stdout
                raise RExecutionError(f"R script failed:\n{error_msg}")

            if not proc.stdout.strip():
                raise RExecutionError("R produced no output")

            return proc.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RExecutionError(
                f"R execution timed out after {self.timeout}s"
            )
        finally:
            try:
                os.unlink(temp_file)
            except Exception:
                pass

    def _convert_output(self, parsed: Any, return_type: str) -> Any:
        """Convert parsed JSON to requested Python type."""
        if return_type == "raw":
            return parsed

        if return_type == "auto":
            return_type = self._infer_type(parsed)

        converters = {
            "int": self._to_int,
            "float": self._to_float,
            "str": self._to_str,
            "bool": self._to_bool,
            "list": self._to_list,
            "dict": self._to_dict,
            "numpy": self._to_numpy,
            "pandas": self._to_pandas,
        }

        if return_type not in converters:
            raise ValueError(
                f"Unknown return_type '{return_type}'. "
                f"Valid options: {', '.join(converters.keys())}, raw, auto"
            )

        try:
            return converters[return_type](parsed)
        except Exception as e:
            raise RTypeError(
                f"Failed to convert to {return_type}: {str(e)}"
            ) from e

    def _infer_type(self, parsed: Any) -> str:
        """Automatically infer best return type."""
        if isinstance(parsed, dict):
            # Check if it looks like a dataframe (dict of lists)
            if all(isinstance(v, list) for v in parsed.values()):
                return "pandas" if HAS_PANDAS else "dict"
            return "dict"
        elif isinstance(parsed, list):
            # Check if it's a numeric array
            if all(isinstance(x, (int, float)) for x in parsed):
                return "numpy" if HAS_NUMPY else "list"
            return "list"
        elif isinstance(parsed, bool):
            return "bool"
        elif isinstance(parsed, int):
            return "int"
        elif isinstance(parsed, float):
            return "float"
        elif isinstance(parsed, str):
            return "str"
        return "raw"

    def _to_int(self, val: Any) -> int:
        if isinstance(val, (int, float)):
            return int(val)
        if isinstance(val, list) and len(val) == 1:
            return int(val[0])
        raise RTypeError(f"Cannot convert {type(val).__name__} to int")

    def _to_float(self, val: Any) -> float:
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, list) and len(val) == 1:
            return float(val[0])
        raise RTypeError(f"Cannot convert {type(val).__name__} to float")

    def _to_str(self, val: Any) -> str:
        if isinstance(val, str):
            return val
        if isinstance(val, list) and len(val) == 1:
            return str(val[0])
        return str(val)

    def _to_bool(self, val: Any) -> bool:
        if isinstance(val, bool):
            return val
        if isinstance(val, list) and len(val) == 1:
            return bool(val[0])
        return bool(val)

    def _to_list(self, val: Any) -> List:
        if isinstance(val, list):
            return val
        if isinstance(val, dict):
            return list(val.values())
        return [val]

    def _to_dict(self, val: Any) -> Dict:
        if isinstance(val, dict):
            return val
        if isinstance(val, list):
            return {str(i): v for i, v in enumerate(val)}
        return {"result": val}

    def _to_numpy(self, val: Any):
        """Convert to NumPy array."""
        if not HAS_NUMPY:
            raise RTypeError(
                "NumPy not installed. Install with: pip install numpy"
            )

        if isinstance(val, list):
            # Handle matrix (list of lists)
            if val and isinstance(val[0], list):
                return np.array(val)
            return np.array(val)
        if isinstance(val, dict):
            # Try to convert dict of lists to 2D array
            lists = list(val.values())
            if all(isinstance(v, list) for v in lists):
                return np.array(lists).T
            return np.array(list(val.values()))
        return np.array([val])

    def _to_pandas(self, val: Any):
        """Convert to pandas DataFrame or Series."""
        if not HAS_PANDAS:
            raise RTypeError(
                "pandas not installed. Install with: pip install pandas"
            )

        if isinstance(val, dict):
            # Dict of lists -> DataFrame
            if all(isinstance(v, list) for v in val.values()):
                return pd.DataFrame(val)
            # Dict of scalars -> Series
            return pd.Series(val)
        if isinstance(val, list):
            # Check if matrix (list of lists)
            if val and isinstance(val[0], list):
                return pd.DataFrame(val)
            return pd.Series(val)
        raise RTypeError(f"Cannot convert {type(val).__name__} to pandas")


def call_r(r_code: str, r_func: str, **kwargs) -> Any:
    """
    Quick wrapper for one-off R function calls.

    Parameters
    ----------
    r_code : str
        R code defining the function
    r_func : str
        Function name to call
    **kwargs
        Arguments to pass to the function

    Returns
    -------
    Result with automatic type inference

    Examples
    --------
    >>> result = call_r("square <- function(x) x^2", "square", x=5)
    >>> print(result)  # 25.0
    """
    rb = RBridge()
    return rb.call(r_code, r_func, **kwargs)
