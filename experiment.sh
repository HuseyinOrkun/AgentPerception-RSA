#!/usr/bin/env bash

# for i in /data2/s*.mat
# paths for the server "/auto/data2/ser/" "/auto/data2/oelmas/EEG_AgentPerception/Analysis/Experiments/"
# paths for huseyin's computer  "/Users/huseyinelmas/Desktop/data/" "/Users/huseyinelmas/Desktop/Experiments/"
# Bash file for


time_window="2"
eeg_distance="correlation"
model_distance="hamming"

########################################
#           NAIVE EXPERIMENT           #
########################################

# MID-FRAME STILL
naive_still_in_path="/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Still_MF/"
naive_still_sv_path="/auto/data2/oelmas/RSA_Results/Naive/Still_MF/"
model_path="/auto/data2/oelmas/RSA_Models/"
stimuli_type="still-mf"
experiment_type="naive"
python rsa_main.py $naive_still_in_path $model_path $time_window $naive_still_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/naive_still_MF_out.txt

# FIRST-FRAME STILL
naive_still_in_path="/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Still_FF/"
naive_still_sv_path="/auto/data2/oelmas/RSA_Results/Naive/Still_FF/"
model_path="/auto/data2/oelmas/RSA_Models/"
stimuli_type="still-ff"
experiment_type="naive"
python rsa_main.py $naive_still_in_path $model_path $time_window $naive_still_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/naive_still_FF_out.txt

# VIDEO
naive_video_in_path="/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Video/"
naive_video_sv_path="/auto/data2/oelmas/RSA_Results/Naive/Video/"
model_path="/auto/data2/oelmas/RSA_Models/"
stimuli_type="video"
experiment_type="naive"
python rsa_main.py $naive_video_in_path $model_path $time_window $naive_video_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/naive_video_out.txt


########################################
#           PRIOR EXPERIMENT           #
########################################

# STILL
prior_still_in_path="/auto/data2/oelmas/EEG_AgentPerception_Prior/Still/"
prior_still_sv_path="/auto/data2/oelmas/RSA_Results/Prior/Still/"
model_path="/auto/data2/oelmas/RSA_Models/"
stimuli_type="still-ff"
experiment_type="prior"
python rsa_main.py $prior_still_in_path $model_path $time_window $prior_still_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/prior_still_out.txt

# VIDEO
prior_video_in_path="/auto/data2/oelmas/EEG_AgentPerception_Prior/Video/"
prior_video_sv_path="/auto/data2/oelmas/RSA_Results/Prior/Video/"
model_path="/auto/data2/oelmas/RSA_Models/"
stimuli_type="video"
experiment_type="prior"
python rsa_main.py $prior_video_in_path $model_path $time_window $prior_video_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/prior_video_out.txt

