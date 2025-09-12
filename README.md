# ABCDWrangler
This is a package for various data science and visualization tools for use with the [ABCD Study](https://abcdstudy.org/) dataset.

# 🚧 Currently under construction, adapting to 6.0 data release 🚧

## Prerequisites

## Installation

## Usage

### 1. Preparing the data
   
```abcdWrangler/io.py``` 

This module allows users to subset and restructure data by automatically locating variables of interest across different source files, and by offering flexible output formats. 

#### Features

Variable lookup: Uses the ABCD data dictionary to find which tables contain requested variables.

Flexible input: Accepts a list of variable names or a dictionary mapping tables to variables.

Session handling: Extracts data for one or multiple sessions (eventname).

#### Output formats:

Long format (default): one row per participant per session.

Wide format: one row per participant, with session-specific columns.

Multi-indexing: optional for rows or columns when handling multiple sessions.

#### Function

data_grabber(data_dir, vars, eventname, long=True, multiindex=False)

Subsets data from the ABCD dataset.

#### Parameters:

`data_dir (str):` Path to the top-level ABCD data directory (containing core/substudy).

`vars (list or dict):` Variable names (list) or table-variable mapping (dict).

`eventname (str or list):` Data collection session(s).

`long (bool):` Output in long (True) or wide (False) format.

`multiindex (bool):` Whether to use multi-indexing for rows/columns when multiple sessions are included.

Returns:

`pandas.DataFrame:` Subset of participants × variables, shaped according to long and multiindex.

### 2. Quality Control 
  ```
 abcdWrangler/qc.py 
  ```
This module provides functions that allow users to identify participants with usable imaging data. It supports structural, diffusion-weighted and functional MRI data. It filters participants based on modality-specific QC criteria and offers optional  motion and timepoint thresholds for fMRI and dMRI. It also inlcudes a helper function to randomly select a subject per family to avoid family-dependencies in the analysis. 

**Functions** \
``smri_qc(df)``: Selects participants with usable T1w/T2w data \
``dmri_qc(df, motion_thresh=None)``: Selects participants with usable dMRI data, with optional motion threshold \
``fmri_qc(df, ntpoints=None, motion_thresh=1)``: Selects participants with usable fMRI data, based on motion and timepoints \
``one_ppt_per_fam(family_dat)``: Randomly selects one participant per family for statistical independence

**Example Usage** 
```
from qc import smri_qc, dmri_qc, fmri_qc, one_ppt_per_fam 

usable_smri = smri_qc(df)
usable_dmri = dmri_qc(df, motion_thresh=0.3) 
usable_fmri = fmri_qc(df, ntpoints=400, motion_thresh=0.5) 
independent_sample = one_ppt_per_fam(df[['rel_family_id']])
```
