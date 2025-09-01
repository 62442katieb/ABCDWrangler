# ABCDWrangler
This is a package for various data science and visualization tools for use with the [ABCD Study](https://abcdstudy.org/) dataset.


## Prerequisites

## Installation


## Usage

### 1. Quality Control 
  ```sh
 abcdWrangler/qc.py 
  ```
This module provides functions for identifying participants with sufficient quality data based on quality control flags and motion thresholds. It supports structural, diffusion-weighted and functional MRI data. It also inlcudes a helper function to randomly select a subject per family to avoid family-dependencies in the analysis. 

*Input* 
All function require a pandas dataframe 

*Output* 
All functions output a dataframe with the participants that have usable quality data. 

*Example usage*
a


