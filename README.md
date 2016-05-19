# TimeDelay
Final project for the AstroML course, based on data from TDC1
Page of the challeng, including data:
http://timedelaychallenge.org/

### [Course report](https://github.com/SU-AstroML/TimeDelay/blob/master/Report/course_report.pdf "report")
### [Course presentation](https://github.com/SU-AstroML/TimeDelay/blob/master/Saghar_Presentation.pdf "presentation")
 
# Data access:
The intermediate data files are too large for GitHub. Please write to saghar.asadi@astro.su.se if you don't want to spend the CPU time to regenerate them all from the raw data in /tdc1/ 

# Scripts

## convert_to_npz.py
* Input: tdc0/*, tdc1/*
* Output: TimeDelayData/pairs_with_truths.npz

Loads all the data into one large numpy array, merging the ground
truth and the source data and adding a column with a globally unique
id for each light curve pair.


## amend_sampling.py
* Input: TimeDelayData/pairs_with_truths.npz
* Output: TimeDelayData/pairs_with_truths_and_windows.npz

Calculates the sampling window boundaries and assigns a globally
unique id to each sampling window. This is done by comparing the
interval between two consecutive points with the average interval
between two such points.


## GP.py
* Input: TimeDelayData/pairs_with_truths_and_windows.npz
* Output: GPModels/*

Trains a Gaussian Process model for each light curve in each sampling
window, and serializes the model using pickle.


## gp_resample.py
* Input: TimeDelayData/pairs_with_truths_and_windows.npz, GPModels/*
* Output: TimeDelayData/gp_resampled_of_windows_with_truth.npz

Interpolates evenly sampled data for each light curve in each window,
using the trained Gaussian Process models from GP.py


## Timeshift.py

* Input: TimeDelayData/gp_resampled_of_windows_with_truth.npz
* Output: timeshift_{correlate,ng_correlate,mse}_normalized[_detrend].npz

Compares the two light corves at all possible offsets using different
methods. The light curves can optionally be detrended before
comparison.

## measure_window_corelations.py
* Input: timeshift_{correlate,ng_correlate,mse}_normalized[_detrend].npz
* Output: timeshift_{correlate,ng_correlate,mse}_normalized[_detrend].measures.npz

Finds the maximum correlation or minimum mse and records its magnitude
and offset for each window.

## sum_pair_corelation_measures.py
* Input: timeshift_{correlate,ng_correlate,mse}_normalized[_detrend].measures.npz
* Output: timeshift_{correlate,ng_correlate,mse}_normalized[_detrend].measures.pairsums.npz

Calculates the mean, median and stddev of the maximum correlation
offsets of all windows for a light curve pair.

## pairsums2dt.py

* Input TimeDelayData/timeshift_correlate_normalized_detrend.measures.pairsums.npz
* Output TimeDelayData/timeshift_correlate_normalized_detrend.measures.pairsums.ests.npz

Estimate dt from median maximum correlation offset and standard
deviation of maximum correlation offset.

## measure_metrics.py

* Input: TimeDelayData/pairs_with_truths_and_windows.npz TimeDelayData/timeshift_correlate_normalized_detrend.measures.pairsums.ests.npz

Measure the error of the dt estimations


## Generating measures for all timeshift data

    python measure_window_corelations.py TimeDelayData/timeshift_correlate_normalized_detrend.npz true TimeDelayData/timeshift_correlate_normalized_detrend.measures.npz
    python measure_window_corelations.py TimeDelayData/timeshift_correlate_normalized.npz true TimeDelayData/timeshift_correlate_normalized.measures.npz
    python measure_window_corelations.py TimeDelayData/timeshift_mse_normalized_detrend.npz false TimeDelayData/timeshift_mse_normalized_detrend.measures.npz
    python measure_window_corelations.py TimeDelayData/timeshift_mse_normalized.npz false TimeDelayData/timeshift_mse_normalized.measures.npz

    for x in TimeDelayData/timeshift_*.measures.npz; do
      python sum_pair_corelation_measures.py $x TimeDelayData/$(basename $x .npz).pairsums.npz;
    done

    for x in TimeDelayData/*.pairsums.npz; do
      python cluster.py $x TimeDelayData/$(basename $x .npz).clusters.npz;
    done


# Data formats

Columns in 'pairs_with_truths_and_windows.npz':


  * From the original light curve pair files: 
    * time, lcA, errA, lcB, errB

  * From the path of the light curve pair files
    * tdc - numerical part of tdc directory name
    * rung - numerical part of rung directory name
    * pair - numerical part of pair filename. Note: pairs in quad
      systems (A, B) have 0.0 added for A and 0.5 added for B.

  * From the corresponding truth file (duplicated for all rows in the corresponding light curve)
    * dt, m1, m2, zl, zs, id, tau, sig

  * Computed values
    * full_pair_id - a (globally) unique id for each combination of tdc, rung, pair
    * window_id - a (globally) unique id for each sample window in the light curves
