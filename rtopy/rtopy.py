"""Main module."""

import re
import subprocess 
from functools import lru_cache
from .utils import format_value


@lru_cache # size is 128 'results' 
def callfunc(r_func, r_func_name="my_func", type_result="float", **kwargs):    

    r_code = r_func + ";"

    # Constructing argument string for the R function call
    arg_string = ""
    for key, value in kwargs.items():
      if isinstance(value, (float, int, list)):
        arg_string += f"{key}={value}, "
      elif isinstance(value, str):
        arg_string += f"{key}={format_value(value)}, "     
    arg_string = arg_string[:-2] # remove last comma and trailing space     
    r_code += f"{r_func_name}({arg_string})"
    r_code = r_code.replace(" ", "").replace("\n", "")     
    result = subprocess.run(["Rscript", "-e", r_code], 
                            capture_output=True, 
                            text=True, 
                            check=True).stdout

    if type_result in ("int", "float", "list"):               
      result = result.split("\n")[-2]\
                                  .strip()\
                                  .replace("[1] ", '')         

    if type_result == "dict":            
      sections = result.strip().split('$')
      # Initialize an empty dictionary to store the lists
      data_dict = {}
      # Iterate over sections and extract key-value pairs
      for section in sections[1:]:
          lines = section.strip().split('\n')          
          key = lines[0].strip()  # Extract the key
          values = [float(x) for x in re.findall(r'[\d.]+', ''.join(lines[1:]))]   
          data_dict[key] = values[1:]
    
    if type_result == "float": 
      return float(result)

    elif type_result == "int":
      return int(result)
    
    elif type_result == "list":
      return [float(elt) for elt in result.split(" ")]

    elif type_result == "dict":
      return data_dict
