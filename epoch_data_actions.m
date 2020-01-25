clc;
clear;
eeglab;
%pth='/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Data/';
pth='/Users/huseyinelmas/Desktop/CCN-Lab/data/set_test/';
%pth='/home/sena/Desktop/set_test/';
fprintf('File Name  File Path: \n');
folders = dir(pth);
robot = {'S101' 'S102' 'S103' 'S104' 'S105' 'S106' 'S107' 'S108'};
actions = {'drink','grasp','handwave','talk','nudge','paper','turn','wipe'};
android = {'S111' 'S112' 'S113'  'S114' 'S115' 'S116'  'S117' 'S118'};
human = {'S121' 'S122' 'S123'  'S124' 'S125' 'S126'  'S127' 'S128'};
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

with_actions = false;
agent_list = containers.Map;
agent_list('robot') = robot;
agent_list('android') = android;
agent_list('human') = human;
mode = 'video';
exp_type = 'naive';

%Bin 2
%Android video  
%.{111;112;113;114;115;116;117;118}

%Bin 3
%Human video
%.{121;122;123;124;125;126;127;128}
if(with_actions)
	action_no = 1; 
else
	action_no =  length(actions);
end

brain_regions = {'central' 'frontal' 'occipital' 'parietal' 'temporal' 'whole_brain'};

% Traverse subject folders
for k=1:length(folders)%1:length(folders)
	
	% If it is a subject folder
	if(folders(k).isdir && ~strcmp(folders(k).name,'.') && ~strcmp(folders(k).name,'..') )
		folder_name = folders(k).name;
		subj_no = folder_name(8:9);													  % Subject folder names are renamed to "subjectXX_" from "subjXX_"
		fprintf('Runnning for subject %s\n',subj_no)

		subj_folder_path = strcat(pth,folder_name,'/' );
		files = dir(subj_folder_path);

		% Works if there is a .set file and only one .set file
		for i=1:length(files)
			if( isempty(strfind(files(i).name, convertCharsToStrings('.set'))) == 0)
				original_set_file_name = files(i).name;
			end
		end

		fprintf('File Name: %s  File Path: %s\n', original_set_file_name,subj_folder_path);
        
        EEG = pop_loadset('filename',original_set_file_name,'filepath',subj_folder_path);
        % Store the original EEG data in dataset number 0 
        [ALLEEG, EEG, CURRENTSET] = eeg_store( ALLEEG, EEG, 0 );
        orig_EEG = eeg_checkset( EEG );

		for region_index=1:length(brain_regions)

			save_path = strcat(subj_folder_path, char(brain_regions(region_index)),'/');
			if ~exist(save_path, 'dir')
				mkdir(save_path);
			end
			if ~exist( strcat(save_path, 'steps/'), 'dir')
				mkdir(strcat(save_path, 'steps/'));					
			end
			if ~exist(strcat(save_path, 'action-mats/'), 'dir')
				mkdir(strcat(save_path, 'action-mats/'));
			end
				
			
			for i=1 :agent_list.Count
				agent_types = keys(agent_list);
				agent = char(agent_types(i));
				fprintf('Runnning for agent: %s\n',agent)

				for j=1:action_no 

					if(with_actions)
						epochs = agent_list(agent);
						title = agent;
					else
						temp = agent_list(agent);
						fprintf('And action: %s\n',char(actions(j)))
						epochs = temp(j);
						title = strcat(agent,'-',char(actions(j))); 
					end

					% Epoching
					EEG = pop_epoch( orig_EEG, epochs, [-0.2  0.6], 'newname', strcat('subj', subj_no ,'_epochs_', title), 'epochinfo', 'yes');
					[ALLEEG, EEG, CURRENTSET] = pop_newset(ALLEEG, EEG, 1,'savenew',strcat(save_path, 'steps/subj', subj_no , '_', title, '_step1_epchs.set'),'overwrite','on','gui','off'); 
					EEG = eeg_checkset( EEG );

					% Baseline removal
					EEG = pop_rmbase( EEG, [-200 0]);
					[ALLEEG, EEG, ~] = pop_newset(ALLEEG, EEG, 2, 'savenew', strcat(save_path, 'steps/subj', subj_no , '_', title, '_step2_rem_bas.set'),'overwrite','on','gui','off'); 
					EEG = eeg_checkset( EEG );

					% Select channels
					switch region_index
						% Central channels
						case 1
							channels = C_channels;
						% Frontal channels
						case 2
							channels = horzcat(F_channels, FC_channels);
						% Occipital channels
						case 3
							channels = O_channels;
						% Parietal channels
						case 4
							channels = horzcat(P_channels, PO_channels);
						% Temporal channels
						case 5
							channels = T_channels;
						% Whole brain (all channels)
						case 6									 
							channels = whole_brain_channels;
							continue;
						otherwise
							disp('Error!')

					end

					EEG = pop_select( EEG,'channel', channels);
					[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 3,'savenew',strcat(save_path, 'steps/subj', subj_no , '_', title, '_step3_chnl.set'),'overwrite','on','gui','off'); 

					% Saving the data into a struct to be able to give a proper 
					eeg_data.(convertCharsToStrings('eeg_data')) = EEG.data;
					eeg_data.(convertCharsToStrings('subj_no')) = subj_no;
					eeg_data.(convertCharsToStrings('agent')) = agent;
					eeg_data.(convertCharsToStrings('experiment_type')) = exp_type;
					eeg_data.(convertCharsToStrings('input_type')) = mode;
					eeg_data.(convertCharsToStrings('action')) = char(actions(j));
					save(strcat(save_path, 'action-mats/subject',subj_no,'_',title,'.mat'), '-struct','eeg_data');
				end % action no
			end % agentlist
		end % brain regions
	end
end