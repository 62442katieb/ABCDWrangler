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
    # include ppl without abnormal findings
    mrif_columns = df.filter(like='mrif_score').columns
    # t1 quality for freesurfer ROI delineations
    # 1=include, 0=exclude
    incl_columns = df.filter(like='imgincl_t1w_include').columns
    smri_mask = df[mrif_columns[0]].between(1,2, inclusive='both')
    smri_mask *= df[incl_columns[0]] == 1
    if len(mrif_columns) > 1:
        for col in mrif_columns[1:]:
            smri_mask *= df[col].between(1,2, inclusive='both')
    if len(incl_columns) > 1:
        for col in incl_columns[1:]:
            smri_mask *= df[col] == 1
    ppts = df.loc[smri_mask == True].index
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
    mrif_columns = df.filter(like='mrif_score').columns
    # t1 quality for freesurfer ROI delineations
    # 1=include, 0=exclude
    incl_columns = df.filter(like='imgincl_dmri_include').columns
    dmri_mask = df[mrif_columns[0]].between(1,2, inclusive='both')
    dmri_mask *= df[incl_columns[0]] == 1
    if len(mrif_columns) > 1:
        for col in mrif_columns[1:]:
            dmri_mask *= df[col].between(1,2, inclusive='both')
    if len(incl_columns) > 1:
        for col in incl_columns[1:]:
            dmri_mask *= df[col] == 1
    if motion_thresh:
        motion_columns = df.filter(like='dmri_meanmotion').columns
        dmri_mask *= df[motion_columns[0]] < motion_thresh
        if len(motion_columns) > 1:
            for col in motion_columns[1:]:
                dmri_mask *= df[col] < motion_thresh
    #dmri_mask = np.invert(dmri_mask)
    ppts = df.loc[dmri_mask == True].index
    return ppts

def fmri_qc(df, ntpoints=None, motion_thresh=1):
    '''
    '''
    mrif_columns = df.filter(like='mrif_score').columns
    # t1 quality for freesurfer ROI delineations
    # 1=include, 0=exclude
    incl_columns = df.filter(like='imgincl_rsfmri_include').columns
    fmri_mask = df[mrif_columns[0]].between(1,2, inclusive='both')
    fmri_mask *= df[incl_columns[0]] == 1
    if len(mrif_columns) > 1:
        for col in mrif_columns[1:]:
            fmri_mask *= df[col].between(1,2, inclusive='both')
    if len(incl_columns) > 1:
        for col in incl_columns[1:]:
            fmri_mask *= df[col] == 1
    if motion_thresh:
        motion_columns = df.filter(like='rsfmri_meanmotion').columns
        fmri_mask *= df[motion_columns[0]] < motion_thresh
        if len(motion_columns) > 1:
            for col in motion_columns[1:]:
                fmri_mask *= df[col] < motion_thresh
    if ntpoints:
        tr_columns = df.filter(like='rsfmri_ntpoints').columns
        fmri_mask *= df[tr_columns[0]] >= ntpoints
        if len(tr_columns) > 1:
            for col in tr_columns[1:]:
                fmri_mask *= df[col] >= ntpoints
    ppts = df.loc[fmri_mask == True].index
    return ppts

def one_ppt_per_fam(family_dat):
    '''
    Function for randomly choosing one participant per family for analyses that cannot account for family dependencies.
    Parameters
    ----------
    family_dat : Pandas Series
        Series (single row from Pandas DataFrame) that has ppt IDs as rows and `rel_family_id` as the singular column
    Returns
    -------
    ppts : list
        List of participants that includes one randomly chosen PPT per family
    '''
    assert len(family_dat.columns) == 1
    all_subj = family_dat.index
    for id_ in family_dat.unique():
        siblings = family_dat[family_dat == id_].index.to_list()
        if len(siblings) > 1:
            keep = np.random.choice(siblings)
            siblings.remove(keep)
            all_subj = list(set(all_subj) - set(siblings))
        else:
            pass
    return all_subj