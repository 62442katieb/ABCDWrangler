import pandas as pd
from os.path import join, exists, dirname
from pathlib import Path

import importlib.resources
DATADIR = join(dirname(__file__), 'data')
#print(DATADIR)




# read in data dictionary so people can grab variables without having to know where they live
# inputs: variable names, eventnames

# tools:
# - data grabber
# - data subsetter?
# - long-to-wide & vice versa- 
#   IDEA: TAKE THE WIDE/LONG STUFF OUT OF THE DATA GRABBER AND MAKE IT A STANDALONE FXN THAT
#   THE DATA_GRABBER CAN CALL?

def data_grabber(data_dir, vars, eventname, long=True, multiindex=False):
    '''
    Function for subsetting data from the larger ABCD Study dataset.
    Parameters
    ----------
    data_dir : str
        Path to ABCD Study data: Top-level, in which `core` and/or `substudy` directories.
    vars : list or dict
        Subject ID for which the networks will be calculated.
    eventname : str or list
        Session of data collection. If there's only one session, we'll find it.
    long : bool
        Format of the dataset. Default: `True`, returning a dataframe that is indexed
        by participant and eventname. If `False`, returns a dataframe that is indexed
        by participant (i.e., only one row per unique PGUID) and variables/columns are
        separated by eventname.
    multiindex : bool
        Specifies whether to use multi-index in the event of more than one `eventname`.
        If `multiindex=True` & `long=True`, row names will be multi-indexed by participant id & 
        eventname. If `multiindex=True` & `long=False`, columns will be multi-indexed by variable 
        name & eventname. If `multiindex=False` & `long=True`, an `eventname` column will be
        added to specify time point of data acquisition. If `multiindex=False` & `long=False`, 
        column names will be the variable name with eventname appended, separated by a period.
    Returns
    -------
    df : Pandas dataframe
        Dataframe: participants x variables. If `long=True`, and `eventname` is a list, 
        then `participants` are index level 0 and `eventname` is index level 1.
    '''

    data_path = join(DATADIR, 'data_dict-5_1.csv')
    data_dict = pd.read_csv(data_path)
    if long and multiindex:
        index = ['src_subject_id', 'eventname']
        incl = []
    else:
        index = ['src_subject_id']
        incl = ['eventname']
    if type(vars) == list:
        # read through data dictionary to get names of dataframes
        temp_dict = data_dict.copy()
        temp_dict.index = temp_dict['var_name']
        intersection = list(set(temp_dict['var_name']) & set(vars))
        #print(f'Found {intersection}.')
        left_out = list(set(vars) - set(temp_dict['var_name']))
        if len(left_out) > 0:
            print(f"Didn't find {left_out}.")
        vars_of_interest = temp_dict.loc[intersection]
        frames = vars_of_interest['table_name'].unique()
        mapping = {}
        for frame in frames:
            temp = vars_of_interest[vars_of_interest['table_name'] == frame]
            mapping[frame] = list(temp.index)
    else:
        mapping = vars
    #print(mapping)
    data_dict.index = data_dict['table_name']
    df = pd.DataFrame()
    for frame in mapping.keys():
        print(frame)
        cols = mapping[frame]
        path = data_dict.loc[frame]['rel_path'].unique()[0]
        
        frame_path = join(data_dir, path)
        print(frame_path)
        assert exists(frame_path)
        temp2 = pd.read_csv(
            frame_path, 
            index_col=index, 
            header=0,
            usecols= index + cols + incl
            )
        if type(eventname) == list and len(eventname) > 1:
            print("multiple timepoints")
            if long:
                print("long format")
                temp3 = pd.DataFrame()
                for event in eventname:
                    if multiindex:
                        print("multiindex")
                        temp4 = temp2.xs(event, level=1)
                        temp4.index = pd.MultiIndex.from_product([temp4.index, [event]])
                    else:
                        print("not multiindex")
                        temp4 = temp2[temp2['eventname'] == event]
                        #temp4['eventname'] = event
                    temp3 = pd.concat([temp3, temp4], axis=0)
                df = pd.concat(
                    [
                        df, 
                        temp3
                    ], 
                    axis=1
                )
            else:
                for event in eventname:
                    temp3 = temp2[temp2['eventname'] == event]
                    if multiindex:
                        print("multiindex")
                        temp3.columns = pd.MultiIndex.from_product([[event], temp3.columns])
                    else:
                        print("not multiindex")
                        temp3.columns = [f'{i.event}' for i in temp3.columns]
                    df = pd.concat(
                        [
                            df,
                            temp3
                        ],
                        axis=1
                    )
        else:
            print("only one event")
            temp3 = temp2[temp2['eventname'] == eventname]
            df = pd.concat(
                    [
                        df,
                        temp3.drop('eventname', axis=1)
                    ],
                    axis=1
                )
    return df