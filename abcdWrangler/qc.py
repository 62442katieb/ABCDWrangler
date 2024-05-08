import pandas as pd
import numpy as np
# MRI QC for each modality
# selection by date
# missingness reports

# MRI quality control dataframes
mri_motion = 'mri_y_qc_motion'
mri_includ = 'mri_y_qc_incl'
mri_findin = 'mri_y_qc_clfind'


def smri_qc(df):
    '''
    Function for identifying participants with sufficient-quality T1w or T2w scans data from the larger ABCD Study dataset.
    Parameters
    ----------
    df : Pandas dataframe
        Dataframe including at least `imgincl_t1w_include` variable, with participants (and eventnames, where applicable) as rows indices
    Returns
    -------
    ppts : list
        Dataframe: participants x variables. If `long=True`, and `eventname` is a list, 
        then `participants` are index level 0 and `eventname` is index level 1.
    '''
    # exclude ppl with abnormal findings
    smri_mask = df['mrif_score'].between(1,2, inclusive='both')
    # t1 quality for freesurfer ROI delineations
    # 1=include, 0=exclude
    smri_mask *= df['imgincl_t1w_include'] == 1
    smri_mask = np.invert(smri_mask)
    ppts = df.loc[smri_mask == True]
    return ppts


def dmri_qc(df, motion_thresh=False):
    '''
    Function for subsetting data from the larger ABCD Study dataset.
    Parameters
    ----------
    df : Pandas dataframe
        Dataframe including at least `imgincl_t1w_include` variable, with participants (and eventnames, where applicable) as rows indices
    Returns
    -------
    ppts : list
        Dataframe: participants x variables. If `long=True`, and `eventname` is a list, 
        then `participants` are index level 0 and `eventname` is index level 1.
    '''
    dmri_mask = df['mrif_score'].between(1,2, inclusive='both')
    # dmri quality for RSI estimates
    # 1=include, 0=exclude
    # head motion greater than 2mm FD on average = exclude
    dmri_mask *= df['imgincl_dmri_include'] == 1
    if motion_thresh:
        dmri_mask *= df['dmri_meanmotion'] >= motion_thresh
    dmri_mask = np.invert(dmri_mask)
    ppts = df.loc[dmri_mask == True]
    return ppts

def fmri_qc(df, ntpoints=500, motion_thresh=1):
    '''
    '''
    rsfmri_mask = df['mrif_score'].between(1,2, inclusive='both')
    rsfmri_mask *= df['imgincl_rsfmri_include'] == 1
    # iteratively build a mask using boolean ANDs 
    # included ppts meet all the specified criteria
    if ntpoints:
        rsfmri_mask *= df['rsfmri_ntpoints'] >= ntpoints
    if motion_thresh:
        rsfmri_mask *= df['rsfmri_meanmotion'] <= motion_thresh
    rsfmri_mask = np.invert(rsfmri_mask)
    ppts = df.loc[rsfmri_mask == True]
    return ppts