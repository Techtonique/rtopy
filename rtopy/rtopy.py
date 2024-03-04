"""Main module."""

import re
import subprocess
from functools import lru_cache
from .utils import *


@lru_cache  # size is 128 'results'
def callfunc(r_code, r_func="my_func", type_return="float", **kwargs):
    """

    `callfunc` calls an R function `r_func` defined in an R code `r_code`.

    # Parameters:

    `r_code` (str): R code to be executed for the function `r_func` to work. Must
    use double braces around function definition, and a semi-colon (';') after
    each instruction.

    `r_func` (str): name of the R function (defined in `r_code`) being called.

    `type_return` (str): type of function return. Either "int", "float", "list" and "dict".

    `kwargs`: additional (named) parameters to be passed to R functions

    # Example:

    ```python
    import rtopy as rp

    # an R function that returns the product of an arbitrary number of arguments
    # notice the double braces around the R function's code
    # and the a semi-colon (';') after each instruction
    r_code1 = 'my_func <- function(arg1=NULL, arg2=NULL, arg3=NULL, arg4=NULL, arg5=NULL)
                {{
                    args <- c(arg1, arg2, arg3, arg4, arg5);
                    args <- args[!sapply(args, is.null)];
                    result <- prod(args);
                    return(result)
                }}'

    print(rp.callfunc(r_code=r_code1, r_func="my_func", type_return="int",
    arg1=3, arg2=5, arg3=2))
    ```

    See also [https://github.com/Techtonique/rtopy/blob/main/rtopy/demo/thierrymoudiki_20240304_rtopyintro.ipynb](https://github.com/Techtonique/rtopy/blob/main/rtopy/demo/thierrymoudiki_20240304_rtopyintro.ipynb)

    """

    r_code_ = r_code + ";"

    # Constructing argument string for the R function call
    arg_string = ""
    for key, value in kwargs.items():
        if isinstance(value, (float, int, list)):
            arg_string += f"{key}={value}, "
        elif isinstance(value, str):
            arg_string += f"{key}={format_value(value)}, "
    arg_string = arg_string[:-2]  # remove last comma and trailing space
    r_code_ += f"{r_func}({arg_string})"
    r_code_ = r_code_.replace(" ", "").replace("\n", "")
    result = subprocess.run(
        ["Rscript", "-e", r_code_], capture_output=True, text=True, check=True
    ).stdout

    if type_return in ("int", "float", "list"):
        result = result.split("\n")[-2].strip().replace("[1] ", "")

    if type_return == "dict":
        keys = extract_elements_with_pattern(extract_pattern(result))
        # Initialize an empty dictionary to store the lists
        result_dict = {}
        # Iterate over sections and extract key-value pairs
        r_list_sections = split_string(result)
        r_list_values = remove_elements_with_pattern(r_list_sections)
        for idx, key in enumerate(keys):
            try:
                section = r_list_values[idx]
                if is_vector(section):
                    result_dict[keys[idx]] = str_to_vector(section)
                elif is_matrix(section):
                    result_dict[keys[idx]] = str_to_matrix(section)
                else:
                    continue
            except:
                continue

    if type_return == "float":
        return float(result)

    elif type_return == "int":
        return int(result)

    elif type_return == "list":
        return [float(elt) for elt in result.split(" ")]

    elif type_return == "dict":
        return result_dict
