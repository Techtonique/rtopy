"""Main module for calling R functions from Python with seamless library support."""

import subprocess
import json
import tempfile
import os
import warnings
from typing import Any, Dict, List, Union, Optional


def callfunc(
    r_code: str = "my_func <- function() { set.seed(1); rnorm(1) }",
    r_func: str = "my_func",
    type_return: str = "float",
    verbose: bool = False,
    **kwargs,
) -> Any:
    """
    Call an R function defined in `r_code`. Works seamlessly with library(xyz), R6 objects, vectors, lists, matrices.

    Parameters
    ----------
    r_code : str
        R code that defines the function `r_func`. Can include library() calls.
    r_func : str
        Name of the function defined in r_code to call.
    type_return : str
        "int", "float", "list", "dict", or "raw"
    verbose : bool
        If True, prints R stderr output (warnings, messages).
    **kwargs :
        Named arguments passed to the R function.

    Returns
    -------
    Python object corresponding to type_return.

    Raises
    ------
    ValueError
        If r_func not found in r_code or invalid parameters.
    RuntimeError
        If R script fails to execute.
    TypeError
        If return type doesn't match expected type_return.

    Examples
    --------
    Example 1: Simple arithmetic
    >>> r_code = '''
    ... add_numbers <- function(x, y) {
    ...     x + y
    ... }
    ... '''
    >>> result = callfunc(r_code=r_code, r_func="add_numbers", type_return="float", x=5, y=3)
    >>> print(result)  # 8.0
    
    Example 2: Vector operations
    >>> r_code = '''
    ... generate_sequence <- function(n) {
    ...     seq(1, n)
    ... }
    ... '''
    >>> result = callfunc(r_code=r_code, r_func="generate_sequence", type_return="list", n=5)
    >>> print(result)  # [1.0, 2.0, 3.0, 4.0, 5.0]
    
    Example 3: Using R libraries (MASS)
    >>> r_code = '''
    ... library(MASS)
    ... generate_mvnorm <- function(n=100) {
    ...     Sigma <- matrix(c(1, 0.5, 0.5, 1), 2, 2)
    ...     mvrnorm(n, mu=c(0, 0), Sigma=Sigma)
    ... }
    ... '''
    >>> result = callfunc(r_code=r_code, r_func="generate_mvnorm", type_return="list", n=50)
    
    Example 4: Returning complex nested structures
    >>> r_code = '''
    ... analyze_data <- function(x) {
    ...     list(
    ...         mean = mean(x),
    ...         sd = sd(x),
    ...         summary = list(
    ...             min = min(x),
    ...             max = max(x),
    ...             n = length(x)
    ...         )
    ...     )
    ... }
    ... '''
    >>> result = callfunc(r_code=r_code, r_func="analyze_data", 
    ...                   type_return="dict", x=[1, 2, 3, 4, 5])
    >>> print(result['mean'])  # 3.0
    >>> print(result['summary']['n'])  # 5
    
    Example 5: Statistical modeling
    >>> r_code = '''
    ... fit_linear_model <- function(x, y) {
    ...     model <- lm(y ~ x)
    ...     list(
    ...         coefficients = coef(model),
    ...         r_squared = summary(model)$r.squared,
    ...         residuals = residuals(model)
    ...     )
    ... }
    ... '''
    >>> result = callfunc(r_code=r_code, r_func="fit_linear_model",
    ...                   type_return="dict", x=[1,2,3,4,5], y=[2,4,6,8,10])
    
    Example 6: Random sampling with seed
    >>> r_code = '''
    ... sample_normal <- function(n, seed=123) {
    ...     set.seed(seed)
    ...     rnorm(n)
    ... }
    ... '''
    >>> result = callfunc(r_code=r_code, r_func="sample_normal", 
    ...                   type_return="list", n=10, seed=42)
    
    Example 7: Working with data frames
    >>> r_code = '''
    ... library(dplyr)
    ... process_data <- function(values) {
    ...     df <- data.frame(x = values)
    ...     df %>%
    ...         mutate(squared = x^2, cubed = x^3) %>%
    ...         summarise(
    ...             mean_x = mean(x),
    ...             mean_squared = mean(squared),
    ...             mean_cubed = mean(cubed)
    ...         )
    ... }
    ... '''
    >>> result = callfunc(r_code=r_code, r_func="process_data",
    ...                   type_return="dict", values=[1, 2, 3, 4, 5])
    """
    
    # Validation
    if r_func not in r_code:
        raise ValueError(f"Function '{r_func}' not found in your `r_code`")
    
    if type_return not in ("int", "float", "list", "dict", "raw"):
        raise ValueError(f"type_return must be one of: int, float, list, dict, raw. Got: {type_return}")

    # Serialize kwargs to JSON for safe R parsing
    try:
        args_json = json.dumps(kwargs)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize kwargs to JSON: {e}. Ensure all values are JSON-serializable.")

    # Escape single quotes for R string literal
    args_json_escaped = args_json.replace("\\", "\\\\").replace("'", "\\'")

    # Create temporary R script file (better for complex code with libraries)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False, encoding='utf-8') as f:
        # Build R script with proper error handling and JSON serialization
        r_script = f'''
# Suppress package startup messages to keep stdout clean
suppressPackageStartupMessages({{

# User's R code (can include library() calls)
{r_code.strip()}

# Parse arguments from JSON
args <- jsonlite::fromJSON('{args_json_escaped}')

# Call the function with parsed arguments
result <- tryCatch({{
    do.call({r_func}, args)
}}, error = function(e) {{
    stop(paste("Error calling", "{r_func}:", e$message))
}})

# Serialize result to JSON for Python parsing
# This handles vectors, matrices, lists, data frames, R6 objects (as lists), etc.
json_output <- jsonlite::toJSON(
    result, 
    auto_unbox = TRUE,  # Convert length-1 vectors to scalars
    force = TRUE,       # Force serialization of all objects
    digits = 15,        # Full precision for floats
    null = "null",      # Handle NULL properly
    na = "null"         # Convert NA to null
)

# Output ONLY the JSON to stdout
cat(json_output, "\\n")

}})
'''
        f.write(r_script)
        temp_file = f.name

    try:
        # Execute R script
        proc = subprocess.run(
            ["Rscript", "--vanilla", temp_file],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        
        # Handle stderr (warnings/messages)
        if stderr and verbose:
            warnings.warn(f"R stderr: {stderr}", UserWarning)
        
        # Check for R errors
        if proc.returncode != 0:
            error_msg = stderr if stderr else stdout
            raise RuntimeError(
                f"R script failed with return code {proc.returncode}:\n{error_msg}"
            )
        
        if not stdout:
            raise RuntimeError("R produced no output. Check if function returns a value.")
            
    except subprocess.TimeoutExpired:
        raise RuntimeError("R script execution timed out after 300 seconds")
    except FileNotFoundError:
        raise RuntimeError(
            "Rscript not found. Please ensure R is installed and in your PATH."
        )
    except Exception as e:
        raise RuntimeError(f"Failed to execute R script: {str(e)}")
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except:
            pass

    # Parse JSON output
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"R output is not valid JSON. This is likely a bug.\n"
            f"stdout: {stdout[:500]}...\n"
            f"stderr: {stderr[:500]}..."
        ) from e

    # Convert parsed JSON to requested Python type
    return _convert_to_type(parsed, type_return)


def _convert_to_type(parsed: Any, type_return: str) -> Any:
    """Convert parsed JSON to requested Python type with validation."""
    
    if type_return == "raw":
        return parsed
    
    elif type_return == "float":
        if isinstance(parsed, (int, float)):
            return float(parsed)
        elif isinstance(parsed, list) and len(parsed) == 1:
            return float(parsed[0])
        else:
            raise TypeError(
                f"Expected numeric scalar for type_return='float', "
                f"got {type(parsed).__name__}: {parsed}"
            )
    
    elif type_return == "int":
        if isinstance(parsed, (int, float)):
            return int(parsed)
        elif isinstance(parsed, list) and len(parsed) == 1:
            return int(parsed[0])
        else:
            raise TypeError(
                f"Expected numeric scalar for type_return='int', "
                f"got {type(parsed).__name__}: {parsed}"
            )
    
    elif type_return == "list":
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            # Convert named list (dict) to list of values
            return list(parsed.values())
        else:
            # Wrap scalar in list
            return [parsed]
    
    elif type_return == "dict":
        if isinstance(parsed, dict):
            return parsed
        elif isinstance(parsed, list):
            # Convert unnamed list to indexed dict
            return {str(i): v for i, v in enumerate(parsed)}
        else:
            # Wrap scalar in dict
            return {"result": parsed}
    
    return parsed


# Convenience functions for backward compatibility
def callfunc_simple(*args, **kwargs) -> Any:
    """
    Simple wrapper for backward compatibility.
    Equivalent to callfunc(..., verbose=False).
    """
    return callfunc(*args, verbose=False, **kwargs)


def callfunc_json(*args, **kwargs) -> Any:
    """
    Wrapper that returns raw JSON output.
    Equivalent to callfunc(..., type_return="raw").
    """
    kwargs['type_return'] = 'raw'
    return callfunc(*args, **kwargs)


# Type aliases for clarity
RCode = str
RFunction = str
ReturnType = str