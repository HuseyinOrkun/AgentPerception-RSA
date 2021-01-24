#!/usr/bin/env bash

# for i in /data2/s*.mat
# paths for the server "/auto/data2/ser/" "/auto/data2/oelmas/EEG_AgentPerception/Analysis/Experiments/"
# paths for huseyin's computer  "/Users/huseyinelmas/Desktop/data/" "/Users/huseyinelmas/Desktop/Experiments/"
# Bash file for


time_window="2"
eeg_distance="correlation"
model_distance="hamming"
model_path="/auto/data2/oelmas/RSA_ModelsV1/"

########################################
#           NAIVE EXPERIMENT           #
########################################

# MID-FRAME STILL
naive_still_in_path="/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Still_MF/"
naive_still_sv_path="/auto/data2/oelmas/RSA_Results_V1/Naive/Still_MF/"
stimuli_type="still-mf"
experiment_type="naive"
python rsa_main.py $naive_still_in_path $model_path $time_window $naive_still_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/naive_still_MF_out.txt

echo "V1 NAIVE MID-FRAME STILL DONE"
# FIRST-FRAME STILL
naive_still_in_path="/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Still_FF/"
naive_still_sv_path="/auto/data2/oelmas/RSA_Results_V1/Naive/Still_FF/"
stimuli_type="still-ff"
experiment_type="naive"
python rsa_main.py $naive_still_in_path $model_path $time_window $naive_still_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/naive_still_FF_out.txt

echo "V1 NAIVE FIRST-FRAME STILL DONE"

# VIDEO
naive_video_in_path="/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Video/"
naive_video_sv_path="/auto/data2/oelmas/RSA_Results_V1/Naive/Video/"
stimuli_type="video"
experiment_type="naive"
python rsa_main.py $naive_video_in_path $model_path $time_window $naive_video_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/naive_video_out.txt
echo "V1 NAIVE VIDEO DONE"


########################################
#           PRIOR EXPERIMENT           #
########################################

# STILL
prior_still_in_path="/auto/data2/oelmas/EEG_AgentPerception_Prior/Still/"
prior_still_sv_path="/auto/data2/oelmas/RSA_Results_V1/Prior/Still/"
stimuli_type="still-ff"
experiment_type="prior"
python rsa_main.py $prior_still_in_path $model_path $time_window $prior_still_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/prior_still_out.txt

echo "V1 PRIOR STILL DONE"
# VIDEO
prior_video_in_path="/auto/data2/oelmas/EEG_AgentPerception_Prior/Video/"
prior_video_sv_path="/auto/data2/oelmas/RSA_Results_V1/Prior/Video/"
stimuli_type="video"
experiment_type="prior"
python rsa_main.py $prior_video_in_path $model_path $time_window $prior_video_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/prior_video_out.txt

echo  "V1 PRIOR VIDEO DONE"


############## V2 ####################

time_window="2"
eeg_distance="correlation"
model_distance="hamming"
model_path="/auto/data2/oelmas/RSA_ModelsV2/"

########################################
#           NAIVE EXPERIMENT           #
########################################

# MID-FRAME STILL
naive_still_in_path="/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Still_MF/"
naive_still_sv_path="/auto/data2/oelmas/RSA_Results_V2/Naive/Still_MF/"
stimuli_type="still-mf"
experiment_type="naive"
python rsa_main.py $naive_still_in_path $model_path $time_window $naive_still_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/naive_still_MF_out.txt

echo "V2 NAIVE MID-FRAME STILL DONE"

# FIRST-FRAME STILL
naive_still_in_path="/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Still_FF/"
naive_still_sv_path="/auto/data2/oelmas/RSA_Results_V2/Naive/Still_FF/"
stimuli_type="still-ff"
experiment_type="naive"
python rsa_main.py $naive_still_in_path $model_path $time_window $naive_still_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/naive_still_FF_out.txt
echo "V2 NAIVE FIRST-FRAME STILL DONE"

# VIDEO
naive_video_in_path="/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Video/"
naive_video_sv_path="/auto/data2/oelmas/RSA_Results_V2/Naive/Video/"
stimuli_type="video"
experiment_type="naive"
python rsa_main.py $naive_video_in_path $model_path $time_window $naive_video_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/naive_video_out.txt

echo "V2 NAIVE VIDEO DONE"

########################################
#           PRIOR EXPERIMENT           #
########################################

# STILL
prior_still_in_path="/auto/data2/oelmas/EEG_AgentPerception_Prior/Still/"
prior_still_sv_path="/auto/data2/oelmas/RSA_Results_V2/Prior/Still/"
stimuli_type="still-ff"
experiment_type="prior"
python rsa_main.py $prior_still_in_path $model_path $time_window $prior_still_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/prior_still_out.txt
echo "V2 PRIOR STILL DONE"

# VIDEO
prior_video_in_path="/auto/data2/oelmas/EEG_AgentPerception_Prior/Video/"
prior_video_sv_path="/auto/data2/oelmas/RSA_Results_V2/Prior/Video/"
stimuli_type="video"
experiment_type="prior"
python rsa_main.py $prior_video_in_path $model_path $time_window $prior_video_sv_path $eeg_distance $model_distance $experiment_type $stimuli_type --avg_subjects_rdm > outputs/prior_video_out.txt

echo "V2 PRIOR VIDEO DONE"

