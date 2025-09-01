# ABCDWrangler
This is a package for various data science and visualization tools for use with the [ABCD Study](https://abcdstudy.org/) dataset.


## Prerequisites

## Installation


## Usage

### 1. Quality Control 
  ```sh
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
from qc import smri_qc, dmri_qc, fmri_qc, one_ppt_per_fam \\

usable_smri = smri_qc(df)\
usable_dmri = dmri_qc(df, motion_thresh=0.3) \
usable_fmri = fmri_qc(df, ntpoints=400, motion_thresh=0.5) \
independent_sample = one_ppt_per_fam(df[['rel_family_id']])
```



