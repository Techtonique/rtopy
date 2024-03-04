# In alphabetical order 

import re 

# Extract list patterns from regex
def extract_pattern(text):
    pattern = r'\$[^\s]+|\[\[\d+\]\]'
    return re.findall(pattern, text)

# Extract elements with a given pattern
def extract_elements_with_pattern(lst):
    pattern = r'\$([^\s]+)|\[\[(\d+)\]\]'
    extracted_elements = []
    for item in lst:
        match = re.match(pattern, item)
        if match:
            extracted_elements.append(match.group(1) or match.group(2))
    return extracted_elements


# Flatten a list of lists 
def flatten_list (x): 
	return [val for sublist in x for val in sublist]

# Formatting object as a string 
def format_value(value):
    return f"'{value}'"

# check is string contains an R vector
def is_vector(x):  
  return ('[1]' in x) and (x != '')

# check is string contains an R matrix
def is_matrix(x):  
  return ('[1,]' in x) and (x != '')

def remove_elements_with_pattern(lst):
    pattern = r'\$[^\s]+|\[\[\d+\]\]'
    return [item for item in lst[1:] if not re.match(pattern, str(item))]

# split string based on a pattern
def split_string(text):
    pattern = r'(\$[^\s]+|\[\[\d+\]\])'
    return re.split(pattern, text)  

# obtain matrix from string 
def str_to_matrix(x):

  # Split the 'y' part into lines
  y_part_lines = x.strip().split('\n')

  # Extract column names
  column_names = y_part_lines[0].split()

  # Initialize empty lists to store numeric column values
  numeric_columns = []

  # Find the minimum length among all rows
  min_length = min(len(line.split()) for line in y_part_lines)

  # Iterate over each line
  for line in y_part_lines:
      # Split each line based on whitespace
      values = line.split(maxsplit=1)[1].split()
      # Keep only the last min_length elements
      values = values[-min_length:]
      # Check if the elements contain numeric values
      numeric_values = [float(val) for val in values if re.match(r'^-?\d+\.?\d*$', val)]
      # Include column names as the first element of the first list
      if not numeric_columns:
          numeric_values = [column_names] + numeric_values
      numeric_columns.append(numeric_values)

  if len(numeric_columns[1:]) == 1:
        return numeric_columns[1:][0]
  return numeric_columns[1:]

# obtain vector from string 
def str_to_vector(x):

  # Split the 'y' part into lines
  y_part_lines = x.strip().split('\n')

  # Initialize an empty list to store the parsed values
  parsed_y_values = []

  # Iterate over each line and extract numeric values
  for line in y_part_lines:
      # Split each line based on whitespace
      values = line.split()
      # Extract numeric values and convert them to float
      numeric_values = [float(val) for val in values[1:]]
      # Append the numeric values to the parsed list
      parsed_y_values.append(numeric_values)

  res = flatten_list(parsed_y_values)
  if len(res) == 1:
    return res[0]
  return res 
