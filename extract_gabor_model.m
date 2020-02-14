clc;
clear all;
close all;

wavelength = [2 5];

n_wavelength = size(wavelength, 2);
orientation = [0 45 90 135];
n_orientation = size(orientation, 2);


g = cell(length(wavelength), 1);
for i=1:length(wavelength)
   g{i} = gabor(wavelength(i),orientation);
end

% Number of frames is 60
N = 60;
M = 10; % 5 10 12

% sena save path '/home/sena/PycharmProjects/CCN-RSA/Models/'
% sena input_path '/home/sena/Stimuli/'
% hüseyin save path  '/Users/huseyinelmas/Desktop/CCN-Lab/RSA-Models/'
% hüseyin input path '/Users/huseyinelmas/Desktop/CCN-Lab/data/Stimuli/' 
% hüseyin server save path   
% hüseyin server input path
input_path = '/home/sena/Stimuli/';
save_path = '/home/sena/PycharmProjects/CCN-RSA/Models/';
stimuli = [ "robot_drink"; "robot-pick"; "robot-handwave"; "robot-talk"; "robot-nudge"; "robot_paper"; "robot_turn"; "robot_clean"; ...
            "android_drink"; "android_pick"; "android_handwave"; "android_talk"; "android_nudge"; "android_paper"; "android_turn"; "android_clean"; ...
            "human_drink"; "human_pick"; "human_handwave"; "human_talk"; "human_nudge"; "human_paper"; "human_turn"; "human_clean"];

gabor_model = zeros(length(stimuli), 400*400*n_wavelength*M, 1);
gabor_movie = zeros(length(wavelength), 400, 400, N/M);
for i=1:length(stimuli)
    
    v = VideoReader(strcat(input_path, strrep(stimuli(i),'-','_'), '_new.avi') );
    
    frame_index= 1;
    end_ = 0;

    while hasFrame(v)  
        frame = readFrame(v);
        bw_frame = rgb2gray(frame);
        
        for k=1:length(wavelength)
           gaborMag = imgaborfilt(bw_frame,g{k});

           max_pooled = max(gaborMag,  [], 3); 
           
           gabor_movie(k,:,:,frame_index) = max_pooled;

           if(mod(frame_index, N/M) == 0)
                avg_pooled = mean(squeeze(gabor_movie( k, :, :, :)), 3);

                % reshape(gaborMag, [size(gaborMag,1)*size(gaborMag,1) size(gaborMag,3)]);
                gabor_column_vectorized = reshape(avg_pooled, 1, []);
                start = end_+1;
                end_ = start+size(gabor_column_vectorized, 2)-1;
                gabor_model(i, start : end_) = gabor_column_vectorized ;
           end


        end
        frame_index = frame_index+1;

    end
end

gabor_model_struct.model_name = strcat('gabor_', string(M),'_frames');
gabor_model_struct.data = gabor_model;

% , '-v7.3' for BIG files
save(strcat(save_path, 'gabor_', string(M),'_frames.mat'), '-struct','gabor_model_struct')

% Viz codes


    %     gabor_figs = figure;
    %     subplot(n_orientation,n_wavelength,1);
    %     for i = 0:(n_orientation*n_wavelength)-1
    %         subplot(n_orientation,n_wavelength,i+1)
    %         imshow(gaborMag(:,:,i+1),[]);
    %         title(sprintf('Orientation=%d, Wavelength=%d',orientation(ceil((i+1)/n_wavelength)), wavelength(mod(i,n_wavelength)+1) ));
    %     end

