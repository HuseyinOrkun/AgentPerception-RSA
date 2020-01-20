wavelength = [2];
orientation = [0 45 90 135];
g = gabor(wavelength,orientation);

v = VideoReader('/home/sena/Stimuli/android_clean_new.avi');
% Number of frames is 60

% May preallocate to speed up
gabor_model = [];

while hasFrame(v)
    frame = readFrame(v);
    bw_frame = rgb2gray(frame);
    outMag = imgaborfilt(bw_frame,g);
    
    pooled = max(outMag,  [], 3);
    
    gabor_model = [gabor_model pooled];
    n_frames = n_frames + 1;
end
