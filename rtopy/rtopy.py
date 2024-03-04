"""Main module."""

import re
import subprocess 
from functools import lru_cache
from .utils import *


@lru_cache # size is 128 'results' 
def callfunc(r_code, r_func_name="my_func", type_result="float", **kwargs):    

    r_code_ = r_code + ";"

    # Constructing argument string for the R function call
    arg_string = ""
    for key, value in kwargs.items():
      if isinstance(value, (float, int, list)):
        arg_string += f"{key}={value}, "
      elif isinstance(value, str):
        arg_string += f"{key}={format_value(value)}, "
    arg_string = arg_string[:-2] # remove last comma and trailing space 
    r_code_ += f"{r_func_name}({arg_string})"
    r_code_ = r_code_.replace(" ", "").replace("\n", "")     
    result = subprocess.run(["Rscript", "-e", r_code_], 
                            capture_output=True, 
                            text=True, 
                            check=True).stdout 

    if type_result in ("int", "float", "list"):               
      result = result.split("\n")[-2]\
                                  .strip()\
                                  .replace("[1] ", '')

    if type_result == "dict":     
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
    
    if type_result == "float": 
      return float(result)

    elif type_result == "int":
      return int(result)
    
    elif type_result == "list":
      return [float(elt) for elt in result.split(" ")]

    elif type_result == "dict":
      return result_dict