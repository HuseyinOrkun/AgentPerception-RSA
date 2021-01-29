clc;
clear;

brain_regions = {'central' 'frontal' 'occipital' 'parietal' 'temporal' 'whole_brain'};
extract_actions = true;

% Epochs for naive data
robot = {'S101' 'S102' 'S103' 'S104' 'S105' 'S106' 'S107' 'S108'};
android = {'S111' 'S112' 'S113'  'S114' 'S115' 'S116'  'S117' 'S118'};
human = {'S121' 'S122' 'S123'  'S124' 'S125' 'S126'  'S127' 'S128'};


% For naive video
data_pth='/auto/data2/oelmas/EEG_AgentPerception_Naive/Video/';
experiment_type = 'naive';
presentation_mode = 'video';
epoch(data_pth, brain_regions, experiment_type, presentation_mode, robot, android, human)

% For naive still
data_pth='/auto/data2/oelmas/EEG_AgentPerception_Naive/Still_FF/';
experiment_type = 'naive';
presentation_mode = 'video';
epoch(data_pth, brain_regions, experiment_type, presentation_mode, robot, android, human)


% For prior video

% Event codes for prior video
robot = {'S151' 'S152' 'S153' 'S154' 'S155' 'S156' 'S157' 'S158'};
android = {'S161' 'S162' 'S163'  'S164' 'S165' 'S166'  'S167' 'S168'};
human = {'S171' 'S172' 'S173'  'S174' 'S175' 'S176'  'S177' 'S178'};

data_pth='/auto/data2/oelmas/EEG_AgentPerception_Prior/Video/';
experiment_type = 'naive';
presentation_mode = 'video';
epoch(data_pth, brain_regions, experiment_type, presentation_mode, robot, android, human)

% For prior still

%Event codes for prior still data
robot = {'S 51' 'S 52' 'S 53' 'S 54' 'S 55' 'S 56' 'S 57' 'S 58'};
android = {'S 61' 'S 62' 'S 63'  'S 64' 'S 65' 'S 66'  'S 67' 'S 68'};
human = {'S 71' 'S 72' 'S 73'  'S 74' 'S 75' 'S 76'  'S 77' 'S 78'};

data_pth='/auto/data2/oelmas/EEG_AgentPerception_Prior/Still/';
experiment_type = 'naive';
presentation_mode = 'video';
epoch(data_pth, brain_regions, experiment_type, presentation_mode, robot, android, human)


