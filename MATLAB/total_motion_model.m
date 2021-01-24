clc;
clear all;
close all;
% sena save path '/home/sena/PycharmProjects/CCN-RSA/Models/'
% sena input_path '/home/sena/Stimuli/'
% hüseyin save path  '/Users/huseyinelmas/Desktop/CCN-Lab/RSA-Models/'
% hüseyin input path '/Users/huseyinelmas/Desktop/CCN-Lab/data/Stimuli/' 
% hüseyin server save path   
% hüseyin server input path 
save_path = '/Users/huseyinelmas/Desktop/CCN-Lab/RSA-Models/';
input_path = '/Users/huseyinelmas/Desktop/CCN-Lab/data/Stimuli/';

opticFlow = opticalFlowLK('NoiseThreshold',0.009);
% Number of frames is 60 (59)
stimuli = [ "robot_drink"; "robot_pick"; "robot_handwave"; "robot_talk"; "robot_nudge"; "robot_paper"; "robot_turn"; "robot_clean"; ...
            "android_drink"; "android_pick"; "android_handwave"; "android_talk"; "android_nudge"; "android_paper"; "android_turn"; "android_clean"; ...
            "human_drink"; "human_pick"; "human_handwave"; "human_talk"; "human_nudge"; "human_paper"; "human_turn"; "human_clean"];
pixel_wise_motion_model = NaN(length(stimuli), 400*400);
for i=1:length(stimuli)
    v = VideoReader(strcat(input_path, stimuli(i), '_new.avi'));
    n_frames = v.Duration*v.FrameRate;
    fprintf("Video of stimuli: %s, has %f frames \n", stimuli(i), v.Duration*v.FrameRate)
    pixel_wise_motion = NaN(single(n_frames));
    frame_index = 1;
    while hasFrame(v)  
        frame = readFrame(v);
        
        % Black and White part might not be necessary
        bw_frame = rgb2gray(frame);
        flow = estimateFlow(opticFlow,bw_frame);
        
        % Get the motion values of from flow
        pixel_wise_motion(frame_index,:) = flow.Magnitude(:);
        frame_index = frame_index+1;
    end
   pixel_wise_motion_model(i,:) = mean(pixel_wise_motion);
end
pixel_wise_motion_model_struct.model_name = strcat('avg_pixel_intensity_model_');
pixel_wise_motion_model_struct.data = pixel_wise_motion_model;
save(strcat(save_path, 'pixel_wise_motion_model.mat'), '-struct','pixel_wise_motion_model_struct')
