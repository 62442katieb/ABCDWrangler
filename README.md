# ABCDWrangler
This is a package for various data science and visualization tools for use with the [ABCD Study](https://abcdstudy.org/) dataset.

# Scripts

1. Preparing the data
   
io.py allows  to subset and restructure data by automatically locating variables of interest across different source files, and by offering flexible output formats. 

# Features

Variable lookup: Uses the ABCD data dictionary to find which tables contain requested variables.

Flexible input: Accepts a list of variable names or a dictionary mapping tables to variables.

Session handling: Extracts data for one or multiple sessions (eventname).

# Output formats:

Long format (default): one row per participant per session.

Wide format: one row per participant, with session-specific columns.

Multi-indexing: optional for rows or columns when handling multiple sessions.

# Function

data_grabber(data_dir, vars, eventname, long=True, multiindex=False)

Subsets data from the ABCD dataset.

# Parameters:

data_dir (str): Path to the top-level ABCD data directory (containing core/substudy).

vars (list or dict): Variable names (list) or table-variable mapping (dict).

eventname (str or list): Data collection session(s).

long (bool): Output in long (True) or wide (False) format.

multiindex (bool): Whether to use multi-indexing for rows/columns when multiple sessions are included.

Returns:

pandas.DataFrame: Subset of participants × variables, shaped according to long and multiindex.
