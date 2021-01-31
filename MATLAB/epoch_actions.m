close all;
clear;
clc;

addpath('/auto/k2/oelmas/eeglab2019_1-2')
eeglab;

fprintf('File Name  File Path: \n');
folders = dir(pth);

% Traverse subject folders
for k=1:length(folders)	
	% If it is a subject folder
	if(folders(k).isdir && ~strcmp(folders(k).name,'.') && ~strcmp(folders(k).name,'..') )
		folder_name = folders(k).name;
		subj_no = folder_name(8:9);
		fprintf('Runnning for subject %s\n',subj_no)

		subj_folder_path = strcat(pth,folder_name,'/' );
		files = dir(subj_folder_path);

		noOfCorrectFiles = 0;
        % Works if there is a .set file and only one .set file
        for i=1:length(files)
            if((strcmp(exp_type,'prior') && isempty(strfind(files(i).name, '.set')) == 0) || (isempty(strfind(files(i).name, '.set'))==0 && isempty(strfind(files(i).name, key)) == 0))
				original_set_file_name = files(i).name;
                noOfCorrectFiles = noOfCorrectFiles + 1;
            end
        end
        if(noOfCorrectFiles >1)
            error('More than 1 set file that has video or ff in file name');
        end
        
		fprintf('File Name: %s  File Path: %s\n', original_set_file_name,subj_folder_path);
        
        EEG = pop_loadset('filename',original_set_file_name,'filepath',subj_folder_path);
        
        % Store the original EEG data in dataset number 1 
        [ALLEEG, EEG, CURRENTSET] = eeg_store( ALLEEG, EEG, 1, 'overwrite', 'on', 'gui','off');
        EEG = eeg_checkset( EEG );
        fprintf('CURRENTSET: %d', CURRENTSET);
        
        % All results of preprocessing steps are stored at set 1
        % and overwritten over each other
        % This is done to optimize memory
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % Interpolate electrode Fp2 (electrode 30) in subjects 14 and
        % 15 of naive experiment
        if( strcmp(exp_type,'naive') && ...
            (strcmp(subj_no,'14') || strcmp(subj_no,'15')) )
            EEG = pop_interp(EEG, [30], 'spherical');

            % Store the new interpolated dataset

            [ALLEEG, EEG, CURRENTSET] = pop_newset(ALLEEG, EEG, CURRENTSET+1, 'overwrite', 'on', 'gui','off');
        	EEG = eeg_checkset( EEG );
        end
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        RESET = CURRENTSET;
		for region_index=1:length(brain_regions)
            
			save_path = strcat(subj_folder_path, char(brain_regions(region_index)),'/');
            if ~exist(save_path, 'dir')
				mkdir(save_path);
            end
			if ~exist(strcat(save_path, 'action-mats/'), 'dir')
				mkdir(strcat(save_path, 'action-mats/'));
			end
				
			
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
                    else
                        epochs = agent_list(agent);
						title = agent;
                    end
                    
                    % VERY IMPORTANT
                    % THIS IS TO RETAIN THE ORIGINAL SET FILE OF THE
                    % SUBJECT
                    EEG = eeg_retrieve(ALLEEG, RESET); CURRENTSET = RESET;
                    
                    % Epoching
					EEG = pop_epoch( EEG, epochs, [-0.2  0.6], 'epochinfo', 'yes');
					[ALLEEG, EEG, CURRENTSET] = pop_newset(ALLEEG, EEG, CURRENTSET+1, 'overwrite', 'on', 'gui','off');
					EEG = eeg_checkset( EEG );

					% Baseline removal
					EEG = pop_rmbase( EEG, [-200 0]);
					[ALLEEG, EEG, CURRENTSET] = pop_newset(ALLEEG, EEG, CURRENTSET+1, 'overwrite', 'on', 'gui','off');
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
						otherwise
							disp('Error!')
                    end

					EEG = pop_select( EEG,'channel', channels);
					[ALLEEG, EEG, CURRENTSET] = pop_newset(ALLEEG, EEG, CURRENTSET+1, 'overwrite', 'on', 'gui','off');
					EEG = eeg_checkset( EEG );

                    % Saving the data into a struct to be able to give a proper 
					eeg_data.eeg_data = EEG.data;
					eeg_data.subj_no = subj_no;
					eeg_data.agent = agent;
					eeg_data.experiment_type = exp_type;
					eeg_data.input_type = mode;
					eeg_data.action = char(actions(j));
					save(strcat(save_path, 'action-mats/subject',subj_no,'_',title,'.mat'), '-struct','eeg_data');
                end % action no
			end % agentlist
		end % brain regions
	end
end