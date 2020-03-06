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
N = 60;
M = 10; % 5 10 12
stimuli = [ "robot_drink"; "robot_pick"; "robot_handwave"; "robot_talk"; "robot_nudge"; "robot_paper"; "robot_turn"; "robot_clean"; ...
            "android_drink"; "android_pick"; "android_handwave"; "android_talk"; "android_nudge"; "android_paper"; "android_turn"; "android_clean"; ...
            "human_drink"; "human_pick"; "human_handwave"; "human_talk"; "human_nudge"; "human_paper"; "human_turn"; "human_clean"];
flow_model = NaN(length(stimuli), 400*400*2*M);
flow_temp = NaN(400, 2*400, N/M);
for i=1:length(stimuli)
    v = VideoReader(strcat(input_path, stimuli(i), '_new.avi'));
    n_frames = v.Duration*v.FrameRate;
    fprintf("Video of stimuli: %s, has %f frames \n", stimuli(i), v.Duration*v.FrameRate)
    frame_index = 1;
    end_ = 0;
    while hasFrame(v)  
        frame = readFrame(v);
        bw_frame = rgb2gray(frame);
        flow = estimateFlow(opticFlow,bw_frame);
        
        % Appending all variables of flow into a vector, will only consider
        %magnitude and orientation now
        % vect_flow = reshape(cat(dim,flow.Vx,flow.Vy,flow.Orientation,flow.Magnitude),1,[]);
        flow_temp(:,:,mod(frame_index-1, N/M)+1) = cat(2, flow.Magnitude, flow.Orientation);
        if((mod(frame_index, N/M) == 0) ||  (n_frames == 59 && frame_index == 59))
            flow_column_vectorized = reshape(mean(flow_temp, 3), 1, []);
            start = end_+1;
            end_ = start+size(flow_column_vectorized, 2)-1;
            flow_model(i, start : end_) = flow_column_vectorized;
        end
         
        frame_index = frame_index+1;
    end
        
end
flow_model_struct.model_name = strcat('flowModel_', string(M),'_frames')';
flow_model_struct.data = flow_model;
save(strcat(save_path, 'flowModel_', string(M),'_frames.mat'), '-struct','flow_model_struct')
