clc;
clear;

%addpath('/auto/k2/oelmas/eeglab14_1_2b')

diary epoch_data_actions_log
%pth='/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Data/';

ls
%pth =' / Users / huseyinelmas / Desktop / CCN - Lab / data / Naive / Video /';

pth='/Users/senaer/Codes/CCNLab/AgentPerception/data/Naive/Video/';
fprintf('File Name  File Path: \n');
folders = dir(pth);
actions = {'drink','grasp','handwave','talk','nudge','paper','turn','wipe'};
% Epochs for naive data
robot = {'S101' 'S102' 'S103' 'S104' 'S105' 'S106' 'S107' 'S108'};
android = {'S111' 'S112' 'S113'  'S114' 'S115' 'S116'  'S117' 'S118'};
human = {'S121' 'S122' 'S123'  'S124' 'S125' 'S126'  'S127' 'S128'};

% Epochs for Prior data
%robot = {'S151' 'S152' 'S153' 'S154' 'S155' 'S156' 'S157' 'S158'};
%android = {'S161' 'S162' 'S163'  'S164' 'S165' 'S166'  'S167' 'S168'};
%human = {'S171' 'S172' 'S173'  'S174' 'S175' 'S176'  'S177' 'S178'};
%Epochs for still data
%robot = {'S 51' 'S 52' 'S 53' 'S 54' 'S 55' 'S 56' 'S 57' 'S 58'};
%android = {'S 61' 'S 62' 'S 63'  'S 64' 'S 65' 'S 66'  'S 67' 'S 68'};
%human = {'S 71' 'S 72' 'S 73'  'S 74' 'S 75' 'S 76'  'S 77' 'S 78'};

whole_brain_channels = {'Fp1', 'Fz', 'F3', 'F7', 'FT9', 'FC5' ,'FC1', 'C3', 'T7', 'CP5', 'CP1'...
	'Pz' ,'P3' ,'P7' ,'O1' ,'Oz' ,'O2' ,'P4', 'P8' ,'CP6' ,'CP2' ,'Cz' ,'C4' ,'T8' ...
	'FT10', 'FC6', 'FC2', 'F4', 'F8', 'Fp2', 'AF7', 'AF3', 'AFz', 'F1', 'F5', 'FT7'...
	'FC3', 'FCz', 'C1', 'C5', 'TP7', 'CP3', 'P1', 'P5', 'PO7', 'PO3', 'POz', 'PO4'...
	'PO8', 'P6', 'P2', 'CPz', 'CP4', 'TP8', 'C6', 'C2', 'FC4', 'FT8', 'F6', 'F2'... 
	'AF4' ,'AF8'};

O_channels = {'O1', 'Oz', 'O2'};

PO_channels = {'POz', 'PO3', 'PO4', 'PO7', 'PO8' };
P_channels = {'P1','P2','Pz','P3','P4', 'P7', 'P8'};

C_channels = {'C1','C2','Cz','C3','C4','C5','C6'};

FC_channels = {'FCz','FC1','FC2','FC5','FC6'};
F_channels = {'F1','F2','Fz','F3','F4', 'AF3','AF4','AF7','AF8','AFz', 'Fp1','Fp2'};

T_channels = {'T7','T8','FT9','FT10','FT7','FT8'};

agent_list = containers.Map;
agent_list('robot') = robot;
agent_list('android') = android;
agent_list('human') = human;
mode = 'video';
if(strcmp(mode, 'video'))
    key='video';
else
    key='ff';
end
exp_type = 'naive';
extract_actions = true;
%Bin 2
%Android video  
%.{111;112;113;114;115;116;117;118}

%Bin 3
%Human video
%.{121;122;123;124;125;126;127;128}
if(extract_actions)
    action_no =  length(actions);
else
    action_no = 1;
end
brain_regions = {'central' 'frontal' 'occipital' 'parietal' 'temporal' 'whole_brain'};

% Traverse subject folders
for k=1:10
    for i=1 :agent_list.Count
        agent_types = keys(agent_list);
        agent = char(agent_types(i));
        fprintf('Runnning for agent: %s\n',agent)

        for j=1:action_no 
            if(extract_actions)
                temp = agent_list(agent);
                fprintf('And action: %s\n',char(actions(j)))
                epochs = temp(j);

                title = strcat(agent,'-',char(actions(j))); 
                elsew
                
            end
        end % action no
    end
end
