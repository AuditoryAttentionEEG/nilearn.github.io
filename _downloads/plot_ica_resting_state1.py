"""
Independent component analysis of resting-state fMRI
=====================================================

An example applying ICA to resting-state data.
"""

import numpy as np

### Load nyu_rest dataset #####################################################
from nilearn import datasets
# Here we use only 3 subjects to get faster-running code. For better
# results, simply increase this number
dataset = datasets.fetch_nyu_rest(n_subjects=1)
# XXX: must get the code to run for more than 1 subject

### Preprocess ################################################################
from nilearn.input_data import NiftiMasker

# This is resting-state data: the background has not been removed yet,
# thus we need to use mask_strategy='epi' to compute the mask from the
# EPI images
masker = NiftiMasker(smoothing_fwhm=8, memory='nilearn_cache', memory_level=1,
                     mask_strategy='epi', standardize=False)
data_masked = masker.fit_transform(dataset.func[0])

# Concatenate all the subjects
#fmri_data = np.concatenate(data_masked, axis=1)
fmri_data = data_masked


### Apply ICA #################################################################

from sklearn.decomposition import FastICA
n_components = 20
ica = FastICA(n_components=n_components, random_state=42)
components_masked = ica.fit_transform(data_masked.T).T

# Normalize estimated components, for thresholding to make sense
components_masked -= components_masked.mean(axis=0)
components_masked /= components_masked.std(axis=0)
# Threshold
components_masked[components_masked < .8] = 0

# Now invert the masking operation, going back to a full 3D
# representation
component_img = masker.inverse_transform(components_masked)
components = component_img.get_data()

# Using a masked array is important to have transparency in the figures
components = np.ma.masked_equal(components, 0, copy=False)

### Visualize the results #####################################################
# Show some interesting components

# Use the mean as a background
import nibabel
import pylab as plt
from nilearn import image
from nilearn.plotting import plot_stat_map

mean_img = image.mean_img(dataset.func[0])

plot_stat_map(nibabel.Nifti1Image(component_img.get_data()[:,:,:,5], 
                                  component_img.get_affine()), mean_img)

plot_stat_map(nibabel.Nifti1Image(component_img.get_data()[:,:,:,12], 
                                  component_img.get_affine()), mean_img)

plt.show()