
#import json
import pandas as pd
import numpy as np
import seaborn as sns
import nibabel as nib

from os.path import join
from nilearn import plotting, surface, datasets, image
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
#import matplotlib as mpl

from urllib.request import urlretrieve

from os.path import join, exists, dirname
from pathlib import Path

DATADIR = join(dirname(__file__), 'data')

def atlas_loader(atlas):
    if atlas == 'Destrieux':
        temp = datasets.fetch_atlas_destrieux_2009()
        atlas_path  = temp.maps
        atlas_nii = nib.load(atlas_path)
    elif atlas == 'cdk':
        temp = datasets.fetch_neurovault_ids(image_ids=(23262, ))
        atlas_path = temp.images[0]
        atlas_nii = nib.load(atlas_path)
    elif atlas == 'scs':
        temp = datasets.fetch_atlas_harvard_oxford('sub-maxprob-thr50-2mm')
        atlas_nii = temp.maps
    elif atlas == 'cortgordon':
        urlretrieve("https://github.com/brainspaces/gordon333/raw/master/gordon333MNI.nii.gz", "gordon333MNI.nii.gz")
        atlas_path = "gordon333MNI.nii.gz"
        atlas_nii = nib.load(atlas_path)
    return atlas_nii

def plot_surfaces(nifti, surf, cmap, vmax, threshold, symmetric=False):
    '''
    Plots of medial and lateral left and right surface views from nifti volume
    '''
    
    texture_l = surface.vol_to_surf(nifti, surf.pial_left, interpolation='nearest')
    texture_r = surface.vol_to_surf(nifti, surf.pial_right, interpolation='nearest')
    
    fig = plt.figure(figsize=(12,4))
    gs = GridSpec(1, 4)

    ax0 = fig.add_subplot(gs[0], projection='3d')
    ax1 = fig.add_subplot(gs[1], projection='3d')
    ax2 = fig.add_subplot(gs[2], projection='3d')
    ax3 = fig.add_subplot(gs[3], projection='3d')
    plt.tight_layout(w_pad=-1, h_pad=-1)
    figure = plotting.plot_surf_stat_map(surf.pial_left, 
                                         texture_l, 
                                         bg_map=surf.sulc_left,
                                         symmetric_cbar=symmetric, 
                                         threshold=threshold,
                                         cmap=cmap, 
                                         view='lateral', 
                                         colorbar=False, 
                                         vmax=vmax, 
                                         axes=ax0)
    figure = plotting.plot_surf_stat_map(surf.pial_left, 
                                         texture_l,
                                         bg_map=surf.sulc_left, 
                                         symmetric_cbar=symmetric, 
                                         threshold=threshold,     
                                         cmap=cmap, 
                                         view='medial', 
                                         colorbar=False, 
                                         vmax=vmax, 
                                         axes=ax1)
    figure = plotting.plot_surf_stat_map(surf.pial_right, 
                                         texture_r, 
                                         bg_map=surf.sulc_right,
                                         symmetric_cbar=symmetric, 
                                         threshold=threshold,
                                         cmap=cmap, 
                                         view='lateral', 
                                         colorbar=False, 
                                         vmax=vmax, 
                                         axes=ax2)
    figure = plotting.plot_surf_stat_map(surf.pial_right, 
                                         texture_r, 
                                         bg_map=surf.sulc_right,
                                         symmetric_cbar=symmetric, 
                                         threshold=threshold,     
                                         cmap=cmap, 
                                         view='medial', 
                                         colorbar=False, 
                                         vmax=vmax, 
                                         axes=ax3)
    return figure

def assign_region_names(df, missing=False):
    '''
    Input: 
    df = dataframe (variable x columns) with column containing region names in ABCD var ontology, 
    Output: 
    df = same dataframe, but with column mapping region variables to actual region names
    missing = optional, list of ABCD region names not present in region_names dictionary
    '''
    rn_path = join(DATADIR, 'region_names.csv')
    region_names = pd.read_csv(rn_path, header=0, index_col=0)
    #print(region_names.index)
    # read in region names 
    missing = []
    df = df.copy()
    if not 'long_region' in df.columns:
        df['measure'] = ''
        df['region'] = ''
        df['modality'] = ''
        df['atlas'] = ''
        df['long_region'] = ''
        df['hemisphere'] = ''
        for var in df.index:
            #print(var)
            trim_var = var.split('.')[0]
            
            var_list = trim_var.split('_')
            
            df.at[var, 'modality'] = var_list[0]
            df.at[var, 'measure'] = var_list[1]
            df.at[var, 'atlas'] = var_list[2]
            region = '_'.join(var_list[3:])
            df.at[var, 'region'] = region
            if 'scs' in trim_var:
                if 'rsirni' in var:
                    df.at[var, 'measure'] = 'rsirnigm'
                elif 'rsirnd' in var:
                    df.at[var, 'measure'] = 'rsirndgm'
                elif '_scs_' in region:
                    temp = region.split('_scs_')
                    one = region_names.loc[temp[0]]
                    #print(one, two)
                    two = region_names.loc[temp[1]]
                    #print(one, two)
                    region_name = f'{one["name"]} {two["name"]}'
                    #print(region_name)
                    hemisphere = two['hemi']
                    df.at[var, 'long_region'] = region_name
                    df.at[var, 'hemisphere'] = hemisphere
                    df.at[var, 'measure'] = 'subcortical-network fc'
                else:
                    pass
            elif '_ngd_' in region:
                temp = region.split('_ngd_')
                if temp[0] == temp[1]:
                    df.at[var, 'measure'] = 'within-network fc'
                else:
                    df.at[var, 'measure'] = 'between-network fc'
                one = region_names.loc[temp[0]]
                two = region_names.loc[temp[1]]
                region_name = f"{one['name']}-{two['name']}"
                #print(one['name'], two['name'], region_name)
                hemisphere = two['hemi']
                df.at[var, 'long_region'] = region_name
                df.at[var, 'hemisphere'] = hemisphere
            elif str(region) not in (region_names.index):
                missing.append(region)
            else:
                one = region_names.loc[region]
                df.at[var, 'long_region'] = one['name']
                df.at[var, 'hemisphere'] = one['hemi']

        df = df[df['measure'] != 't1w']
        df = df[df['measure'] != 't2w']
    else:
        pass

    print(f'missed {len(missing)} regions bc they weren\'t in the dict')
    return df

def plot_brains(series, out_dir, cmap=None, symmetric=True):
    nifti_mapping = pd.read_csv('/Volumes/projects_herting/LABDOCS/Personnel/Katie/deltaABCD_clustering/data/variable_to_nifti_mapping.csv', 
                                header=0, 
                                index_col=0)

    series.index = [x.split('.')[0] for x in series.index]
    vmax = series.quantile(0.95)
    #vmin = series.quantile(0.25)

    # list of measures to plot
    measures = {'cortical-thickness': 'smri_thick_cdk_.*',
                'cortical-gwcontrast': 'smri_t1wcnt_cdk_.*',
                'cortical-area': 'smri_area_cdk_.*',
                'cortical-volume': 'smri_vol_cdk_.*', 
                'subcortical-volume': 'smri_vol_scs_.*', 
                'subcortical-RND': 'dmri_rsirnd_scs_.*',
                'subcortical-RNI': 'dmri_rsirni_scs_.*',
                'cortical-RND': 'dmri_rsirndgm_.*',
                'cortical-RNI': 'dmri_rsirnigm_.*',
                'cortical-BOLD-variance': 'rsfmri_var_cdk_.*',
                'tract-volume': 'dmri_dtivol_fiberat_.*', 
                'tract-FA': 'dmri_dtifa_fiberat_.*', 
                'tract-MD': 'dmri_dtimd_fiberat_.*',
                'tract-LD': 'dmri_dtild_fiberat_.*', 
                'tract-TD': 'dmri_dtitd_fiberat_.*', 
                'tract-RND': 'dmri_rsirnd_fib_.*',
                'tract-RNI': 'dmri_rsirni_fib_.*'}
    fc_cort_var = series.filter(regex='.*fmri.*_c_.*').index
    fc_scor_var = series.filter(regex='.*fmri.*_cor_.*').index
    fmri_var_var = series.filter(regex='.*fmri.*_var_.*').index

    #morph_var = df[df['concept'] == 'macrostructure'].index
    #cell_var = df[df['concept'] == 'microstructure'].index
    func_var = list(fmri_var_var) 
    conn_var = list(fc_cort_var) + list(fc_scor_var)

    conn_measures = {'cortical-network-connectivity': 'rsfmri_c_ngd_.*',
                'subcortical-network-connectivity': 'rsfmri_cor_ngd_.*_scs_.*',}

    fsaverage = datasets.fetch_surf_fsaverage()
    if not cmap:
        cmap = sns.diverging_palette(22, 256.3, s=70, l=50, center="light", as_cmap=True)
    pal = sns.diverging_palette(22, 256.3, s=70, l=50, center="light", as_cmap=False)
    #sns.plot(morph_ + func_ + cell_)

    pals = {'cortical-thickness': cmap,
            'cortical-gwcontrast': cmap,
                'cortical-area': cmap,
                'cortical-volume': cmap, 
                'subcortical-volume': cmap, 
                'subcortical-RND': cmap,
                'subcortical-RNI': cmap,
                'cortical-RND': cmap,
                'cortical-RNI': cmap,
                'cortical-BOLD-variance': cmap,
                'tract-volume': cmap, 
                'tract-FA': cmap, 
                'tract-MD': cmap,
                'tract-LD': cmap, 
                'tract-TD': cmap,
                'tract-RND': cmap,
                'tract-RNI': cmap,
            'cortical-network-connectivity': cmap,
                'subcortical-network-connectivity': cmap}

    # let's plot APC on brains pls
    for measure in measures.keys():
        #print(measure, measures[measure])
        #print(measure)

        meas_df = series.filter(regex=measures[measure], axis=0)
        meas_vars = meas_df.index

        meas_df.drop_duplicates(inplace=True)
        #print(meas_df.head())
        if meas_df.sum() == 0:
            pass
        else:
            if 'tract' in measure:
                fibers = nifti_mapping.filter(regex=measures[measure], axis=0).index
                var = fibers[0]
                tract_fname = nifti_mapping.loc[var]['atlas_fname']
                tract_nii = nib.load(tract_fname)
                tract_arr = tract_nii.get_fdata()
                #print(np.unique(tract_arr))
                avg = series.loc[f'{var}']
                tract_arr *= avg
                all_tracts_arr = np.zeros(tract_arr.shape)
                all_tracts_arr += tract_arr
                for var in fibers[1:]:    
                    tract_fname = nifti_mapping.loc[var]['atlas_fname']
                    if type(tract_fname) is str:
                        try:
                            tract_nii = nib.load(tract_fname)
                            tract_arr = tract_nii.get_fdata()
                            #print(np.unique(tract_arr))
                            avg = series.loc[f'{var}']
                            tract_arr *= avg
                            all_tracts_arr += tract_arr
                        except Exception as e:
                            pass
                    else:
                        pass
                meas_nimg = nib.Nifti1Image(all_tracts_arr, tract_nii.affine)
                meas_nimg.to_filename(f'{out_dir}/{measure}-{series.name}.nii')
                #plt.figure(layout='tight')
                fig,ax = plt.subplots()
                q = plotting.plot_stat_map(meas_nimg, display_mode='z',  threshold=vmax*0.01,
                                            cut_coords=[-20, 0, 18, 40], vmax=vmax*1.1, 
                                            annotate=False, cmap=cmap, colorbar=False,
                                            symmetric_cbar=symmetric, axes=ax
                                    )
                #q.add_edges(meas_nimg)
                min = np.format_float_scientific(np.min(meas_df), precision=3)
                max = np.format_float_scientific(np.max(meas_df), precision=3)
                fig.savefig(f'{out_dir}/{measure}-{series.name}_{min}-{max}.png', dpi=400, bbox_inches='tight')
                plt.close(fig)
            else:
                #print(nifti_mapping.loc[meas_vars]['atlas_fname'])
                atlas_fname = nifti_mapping.loc[meas_vars]['atlas_fname'].unique()[0]
                #print(atlas_fname)
                atlas_nii = nib.load(atlas_fname)
                atlas_arr = atlas_nii.get_fdata()
                plotting_arr = np.zeros(atlas_arr.shape)
                for i in meas_df.index:
                    if i in nifti_mapping.index:
                        value = nifti_mapping.loc[i]['atlas_value']
                        
                        #print(i, value)
                        if value is np.nan:
                            pass
                        
                        else:
                            avg = series.at[i]
                            if avg is not float:
                                avg = np.mean(avg)
                            else:
                                pass
                            #print(avg, value, atlas_arr.shape)
                            plotting_arr[np.where(atlas_arr == value)] = avg
                    else:
                        pass
                
                meas_nimg = nib.Nifti1Image(plotting_arr, atlas_nii.affine)
                meas_nimg.to_filename(f'{out_dir}/{measure}-{series.name}.nii')
                min = np.format_float_scientific(np.min(meas_df), precision=3)
                max = np.format_float_scientific(np.max(meas_df), precision=3)
                if 'subcortical' in measure:
                    fig,ax = plt.subplots()
                    #plt.figure(layout='tight')
                    q = plotting.plot_stat_map(meas_nimg, display_mode='z', threshold=vmax*0.01,
                                        cut_coords=[-20, -10, 0, 10], vmax=vmax*1.1, 
                                        annotate=False, cmap=cmap, colorbar=False,
                                        symmetric_cbar=symmetric, axes=ax)

                    fig.savefig(f'{out_dir}/{measure}-{series.name}_{min}-{max}.png', dpi=400, bbox_inches='tight')
                    plt.close(fig)
                elif 'cortical' in measure:
                    figure = plot_surfaces(meas_nimg, fsaverage, cmap, vmax, 0.001, symmetric=symmetric)
                    figure.savefig(f'{out_dir}/{measure}-{series.name}_{min}-{max}.png', dpi=400, bbox_inches='tight')
                    plt.close(figure)

    # gather variables (network names) for plotting connectivity
    corrs = series.filter(regex='rsfmri_c_ngd.*', axis=0).index
    corrs = [i.split('.')[0] for i in corrs]
    networks = list(np.unique([i.split('_')[-1] for i in corrs]))

    corrs = series.filter(regex='rsfmri_c_ngd.*', axis=0).index
    corrs = [i.split('.')[0] for i in corrs]
    networks = list(np.unique([i.split('_')[-1] for i in corrs]))

    btwn_fc = []
    wthn_fc = []
    for var in fc_cort_var:
        var_list = var.split('_')
        #print(var_list)
        if var_list[3] == var_list[5]:
            #print(var, 'within-network')
            wthn_fc.append(var)
        else:
            btwn_fc.append(var)
            #print(var, 'between-network')

    btwn_fc_src = [i.split('.')[0].split('_')[3] for i in btwn_fc]
    btwn_fc_trgt = [i.split('.')[0].split('_')[-1] for i in btwn_fc]

    #vmax = 3.5

    # okay, now we're plotting between and within network connectivity
    #within-network fc is easy to plot bc there's only one HSK value per network (per fligner_var)
    meas_df = series.loc[wthn_fc]
    if meas_df.sum() == 0:
        pass
    else:
        meas_vars = [i.split('.')[0] for i in meas_df.index]
        atlas_fname = nifti_mapping.loc[meas_vars]['atlas_fname'].unique()[0]
        #print(atlas_fname)
        atlas_nii = nib.load(atlas_fname)
        atlas_arr = atlas_nii.get_fdata()
        plotting_arr = np.zeros(atlas_arr.shape)
        for i in meas_df.index:
            j = i.split('.')[0]
            value = nifti_mapping.loc[j]['atlas_value']
            #print(i, value)
            if value is np.nan:
                pass
            elif 'crbwmatterlh' in i:
                pass
            else:
                plotting_arr[np.where(atlas_arr == value)] = series.at[i]

        meas_nimg = nib.Nifti1Image(plotting_arr, atlas_nii.affine)
        meas_nimg.to_filename(f'{out_dir}/{measure}-{series.name}.nii')
        figure = plot_surfaces(meas_nimg, fsaverage, cmap, vmax, 0.001, symmetric=symmetric)
        figure.savefig(f'{out_dir}/{measure}-{series.name}.png', dpi=400)

    scs_varnames = [i.split('.')[0].split('_')[-1] for i in fc_scor_var]

    # now subcortical-cortical functional connectivity
    sig = []
    meas_df = series.loc[fc_scor_var]

    if meas_df.sum() == 0:
        pass
    else:
        scs_vars = pd.Series(scs_varnames, index=fc_scor_var)
        scs_vars.drop_duplicates(inplace=True)
        avgs = pd.DataFrame()
        for scs in np.unique(scs_varnames):
            scs_temp = scs_vars[scs_vars == scs].index
            temp_df = meas_df[scs_temp]
            # calculate average change of all 
            # significantly heteroscedastic network connections

            for i in temp_df.index:
                sig.append(temp_df.loc[i])
            mean_apc = np.mean(sig)
            #print(mean_hsk)
            # grab name of first conn var for this network for plotting
            avgs.at[temp_df.index[0], 'apc'] = mean_apc
        #print(nsig)
        meas_vars = [i.split('.')[0] for i in avgs.index]
        atlas_fname = nifti_mapping.loc[meas_vars]['atlas_fname'].unique()[0]
        #print(atlas_fname)
        atlas_nii = nib.load(atlas_fname)
        atlas_arr = atlas_nii.get_fdata()
        plotting_arr = np.zeros(atlas_arr.shape)
        sig = 0
        for i in avgs.index:
            j = i.split('.')[0]
            value = nifti_mapping.loc[j]['atlas_value']
            #print(i, value)
            if value is np.nan:
                pass
            else:
                plotting_arr[np.where(atlas_arr == value)] = avgs.loc[i]        
        meas_nimg = nib.Nifti1Image(plotting_arr, atlas_nii.affine)
        meas_nimg.to_filename(f'{out_dir}/{measure}-{series.name}.nii')
        fig,ax = plt.subplots(#ncols=2, gridspec_kw=grid_kw, figsize=(24,4)
                            )
        #plt.figure(layout='tight')
        q = plotting.plot_stat_map(meas_nimg, display_mode='z',  threshold=.01,
                            cut_coords=[-20, -10, 0, 10], vmax=vmax*1.1, 
                            annotate=False, cmap=cmap, colorbar=False,
                            symmetric_cbar=symmetric, axes=ax)

        #ax[1].set_visible(False)
        min = np.min(avgs)
        max = np.max(avgs)
        fig.savefig(f'{out_dir}/{measure}-{series.name}_{min}-{max}.png', dpi=400, bbox_inches='tight')
        plt.close(fig)

    # between-network FC is tough bc we have to average all of a networks HSK values
    # but only the significantly HSK connections
    sig = []
    meas_df = series.loc[btwn_fc]
    if meas_df.sum() == 0:
        pass
    else:
        #meas_df.loc[btwn_fc, 'from_ntwk'] = btwn_fc_src
        from_ntwks = pd.Series(btwn_fc_src, index=btwn_fc)
        #meas_df.loc[btwn_fc, 'to_ntwk'] = btwn_fc_trgt
        to_ntwks = pd.Series(btwn_fc_trgt, index=btwn_fc)
        avgs = pd.DataFrame()
        for ntwk in np.unique(btwn_fc_src):
            from_ntwk_index = from_ntwks[from_ntwks == ntwk].index
            to_ntwk_index = from_ntwks[to_ntwks == ntwk].index
            temp_df = meas_df.loc[from_ntwk_index]
            temp_df2 = meas_df.loc[to_ntwk_index]
            temp_df = pd.concat([temp_df, temp_df2], axis=0)
            # calculate average heteroscedasticity of all 
            # significantly heteroscedastic network connections
            for i in temp_df.index:
                sig.append(temp_df.loc[i])
            mean_hsk = np.mean(sig)
            # grab name of first conn var for this network for plotting
            avgs.at[temp_df.index[0]] = mean_hsk
        meas_vars = [i.split('.')[0] for i in avgs.index]
        atlas_fname = nifti_mapping.loc[meas_vars]['atlas_fname'].unique()[0]
        #print(atlas_fname)
        atlas_nii = nib.load(atlas_fname)
        atlas_arr = atlas_nii.get_fdata()
        plotting_arr = np.zeros(atlas_arr.shape)
        sig = 0
        for i in avgs.index:
            value = nifti_mapping.loc[i]['atlas_value']
            #print(i, value)
            if value is np.nan:
                pass
            elif value.shape == (0,):
                pass
            else:
                if i not in avgs.index:
                    pass
                else:
                    plotting_arr[np.where(atlas_arr == value)] = avgs.loc[i] 
        min = np.format_float_scientific(np.min(avgs), precision=3)
        max = np.format_float_scientific(np.max(avgs), precision=3)    
        meas_nimg = nib.Nifti1Image(plotting_arr, atlas_nii.affine)
        meas_nimg.to_filename(f'{out_dir}/{measure}-{series.name}.nii')
        figure = plot_surfaces(meas_nimg, fsaverage, cmap, vmax, 0.001, symmetric=symmetric)
        figure.savefig(f'{out_dir}/{measure}-{series.name}_{min}-{max}.png', dpi=400)

    #fig = plt.figure()
    #ax = fig.add_axes([0.05, 0.80, 0.9, 0.1])

    #range_ = np.arange(-int(vmax*5), int(vmax*5)) / 5.

    #cb = mpl.colorbar.ColorbarBase(ax, orientation='horizontal', 
    #                            cmap=cmap, 
    #                            values=range_, 
    #                            )
    #ax.set_xlabel(series.name)

    #plt.savefig(join(out_dir, f'{series.name}-cmap_1-{-vmax,vmax}.png'), bbox_inches='tight', dpi=400)

def series_2_nifti(series, out_dir=None, combined=False):
    '''
    Function for mapping a series (i.e., 1D vector, Pandas style) of brain measure values 
    into a nifti imamge. NOTE: Not intended for functional connectivity or white matter measures.
    Parameters
    ----------
    Series : Pandas series
        A Pandas series with ABCD Study brain measure variable names as index and values
        for those brain measures as values. If there are multiple brain measures or multiple 
        atlases, this function will return multiple niftis, separated by measure and/or atlas UNLESS
        `combined=True` with only one brain measure (e.g., fractional anisotropy) and the atlases
        are non-overlapping (e.g., Desikan-Killiany cortical atlas + subcortical atlas + white
        matter tract atlas), in which case all variables will be mapped on to a single nifti.
    out_dir : string
        Path to directory where resulting nifti(s) should be saved. If `False`, niftis will not be saved.
    combined : bool
        Session of data collection. If there's only one session, then `long` and `multiindex` are skipped.
        If there's more than one session, then the shape of the resulting dataframe is determined by
        `long` and `multiindex`. Default: long DF with `eventname` column and no multiindexing (as in the
        ABCD Study tabulated data files).
    Returns
    -------
    nifti : `nibabel` `Nifti1Image` objects OR list of `nibabel` `Nifti1Image` objects
        
    '''
    mm_path = join(DATADIR, 'measure-mapping.csv')
    measure_map = pd.read_csv(mm_path, index_col=0, header=0)
    #am_path = join(DATADIR, 'atlas-mapping.csv')
    #atlas_map = pd.read_csv(am_path, index_col=0, header=0)
    nm_path = join(DATADIR, 'variable_to_nifti_mapping.csv')
    nifti_mapping = pd.read_csv(nm_path, header=0, index_col=0)

    series.index = [x.split('.')[0] for x in series.index]

    out = []
    # expand variable names for more sensible groupings
    variable_expansion = pd.DataFrame(
        index=series.index,
        columns=['modality', 'measure', 'atlas', 'region']
    )
    for i in series.index:
        temp = i.split('_')
        variable_expansion.at[i,'modality'] = temp[0]
        variable_expansion.at[i,'measure'] = measure_map.loc[temp[1]]['measure']
        variable_expansion.at[i,'atlas'] = temp[2]
        variable_expansion.at[i,'region'] = temp[3]
    measures = variable_expansion['measure'].unique()
    
    for measure in measures:
        atlases = variable_expansion[variable_expansion['measure'] == measure]['atlas'].unique()
        temp_df = series.loc[variable_expansion[variable_expansion['measure'] == measure].index]
        if combined:
            
            start_nii = atlas_loader(atlases[0])
            start_arr = np.zeros(start_nii.get_fdata().shape)
        for atlas in atlases:
            print(atlas)
            ids = list(set(temp_df.index) & set(variable_expansion[variable_expansion['atlas'] == atlas].index))
            temp_df2 = temp_df.loc[ids]
            atlas_nii = atlas_loader(atlas)
            atlas_arr = atlas_nii.get_fdata()
            # make zeroes array with same shape as atlas
            plotting_arr = np.zeros(atlas_arr.shape)
            if temp_df2.sum() == 0:
                pass
            else:
                # read in atlas
                
                for i in temp_df2.index:
                    if i in nifti_mapping.index:
                        value = nifti_mapping.loc[i]['atlas_value']
                        #print(i, value)
                        if value is np.nan:
                            pass
                        else:
                            plotting_arr[np.where(atlas_arr == value)] = float(series.at[i])
                    else:
                        pass
            
            if combined:
                meas_nimg = nib.Nifti1Image(plotting_arr, atlas_nii.affine)
                res_nii = image.resample_to_img(meas_nimg, start_nii)
                temp = res_nii.get_fdata()
                start_arr += temp
                meas_nimg = nib.Nifti1Image(start_arr, start_nii.affine)
                #out.append(meas_nimg)
            else:
                meas_nimg = nib.Nifti1Image(plotting_arr, atlas_nii.affine)
                if out_dir:
                    meas_nimg.to_filename(f'{out_dir}/{measure}-{atlas}-{series.name}.nii')
                    out.append(meas_nimg)
                else:
                    out.append(meas_nimg)
        if combined:
            out.append(meas_nimg)
    if len(out) == 1:
        out = out[0]
        return out
    else:
        return out
    
def series_2_corrmat(series, networks=None, array=True):
    if not networks:
        temp = [i.split('_')[3] for i in series.index]
        temp2 = [i.split('_')[5] for i in series.index]
        networks = list(np.unique(temp + temp2))
    corrmat = np.zeros((len(networks), len(networks)))
    for ntwk1 in networks:
        i = networks.index(ntwk1)
        for ntwk2 in networks:
            j = networks.index(ntwk2)
            var = f'rsfmri_c_ngd_{ntwk1}_ngd_{ntwk2}'
            try:
                corrmat[i,j] = series.loc[var]
            except Exception as e:
                #print(e)
                pass
    corrmat += corrmat.T
    if array:
        pass
    else:
        corrmat = pd.DataFrame(data=corrmat, index=networks, columns=networks)
    return corrmat


def plot_3d(data, subcortical=False, path_to_save=None, colors_specified=None, thresholds=None):
    """
    Plot cortical (Desikan-Killiany parcellation) or subcortical brain maps.

    Parameters:
    -----------
    data : pandas.Series or similar
        A 1D array-like containing regional values. Should have either:
        - 19 subcortical regions (if `subcortical=True`), or
        - 68 cortical regions (if `subcortical=False`).
    
    subcortical : bool, default False
        If True, plots subcortical regions after dropping cerebellum and brainstem.
        Otherwise, plots cortical regions.

    path_to_save : str or None, optional
        File path to save the generated plot image. If None, the plot is not saved.

    colors_specified : None, str, or list/tuple of 3 colors, optional
        Specifies the colormap to use for plotting.
        - If None (default), uses the `'RdBu_r'` colormap.
        - If a string, must be one of the predefined colormaps supported by the toolbox.
        - If a list or tuple, must contain exactly 3 valid color specifications (e.g., color names or hex strings).
          A custom diverging colormap will be created from these three colors.
    
    thresholds : tuple or list of two numbers (int or float), optional
        Color value range for the colormap (low, high).
        If None (default), uses the minimum and maximum of the data.

    Returns:
    --------
    plot : The generated plot object.

    Raises:
    -------
    ValueError
        - If the input data length does not match expected number of regions.
        - If `colors_specified` is not None, a supported string, or a list/tuple of exactly 3 colors.
        - If a string colormap provided is not in the predefined list.
    TypeError
        - If `thresholds` is provided but its first two elements are not numeric.
    RuntimeError
        If reordering of subcortical data fails.
    """
    predefined_cmaps = ['viridis', 'viridis_r', 'inferno', 'inferno_r',
                             'plasma', 'plasma_r', 'Blues', 'Blues_r', 'Reds',
                             'Reds_r', 'cividis', 'cividis_r', 'RdBu', 'RdBu_r']
    
    if colors_specified == None:
        color_map = 'RdBu_r' #set Red-Blue reversed as default
    elif isinstance(colors_specified, str):
        if colors_specified not in predefined_cmaps:
            raise ValueError(f"Colormap '{colors_specified}' is not supported.")
        color_map = colors_specified
    elif isinstance(colors_specified, (list, tuple)) and len(colors_specified) == 3:
        color_map = LinearSegmentedColormap.from_list("custom_diverging", colors_specified)
    else:
        raise ValueError("colors_specified must be a string colormap name or list of exactly 3 colors.")
    
    # set thresholds for plotting
    if thresholds == None:
        low_thresh = data.min()
        high_thresh = data.max()
    else:
        # make sure that both elements are numbers first
        if not (isinstance(thresholds[0], (int, float)) and isinstance(thresholds[1], (int, float))):
            raise TypeError("First two elements are not numbers")
        low_thresh = thresholds[0]
        high_thresh = thresholds[1]

    if subcortical:
        # check that data has 19 regions
        expected_regions = 19
        if len(data) != expected_regions:  # +3 for cerebellum and brainstem to drop
            raise ValueError(f"Expected {expected_regions} subcortical regions (including cerebellum and brainstem), got {len(data)}")

        # first drop the cerebellum and brainstem
        subcortical_data = data.drop(labels=['smri_vol_scs_crbcortexlh', 'smri_vol_scs_crbcortexrh', 'smri_vol_scs_bstem'])
        subcortical_df = subcortical_data.to_frame().T # convert to df, needed for reordering function
         # ensure correct order for plotting
        try:
            subcortical_reordered = reorder_sctx(subcortical_df)
        except Exception as e:
            raise RuntimeError(f"Failed to reorder subcortical data: {e}")
        
        plot = plot_subcortical(array_name=subcortical_reordered.values, 
                                size=(800, 400), cmap=color_map, color_bar=True,
                                embed_nb=True, color_range=(low_thresh, high_thresh))
        print("Plot type:", type(plot))

    # if not specified to be subcortical, then assume 68 DK regions
    else:
        # check that we have 68 areas 
        expected_regions = 68
        if len(data) != expected_regions:
            raise ValueError(f"Expected {expected_regions} cortical regions, got {len(data)}")

        data_fsa5 = parcel_to_surface(data, 'aparc_fsa5') # convert to fsaverage5

        plot = plot_cortical(array_name=data_fsa5, surface_name="fsa5", size=(800, 400),
                    cmap=color_map, color_bar=True, embed_nb=True, 
                    color_range=(low_thresh, high_thresh))
        
    # if path is given, save the plot 
    if path_to_save:
        print("Saving figure to: ", path_to_save)
        # save figure
        with open(path_to_save, "wb") as f:
            f.write(plot.data)

    return plot 
