function epoch(data_pth, brain_regions, experiment_type, presentation_mode, robot, android, human)

    addpath('/auto/k2/oelmas/eeglab19_1_2')
    eeglab;


    fprintf('File Name  File Path: \n');
    folders = dir(data_pth);
    actions = {'drink','grasp','handwave','talk','nudge','paper','turn','wipe'};


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

    if(strcmp(presentation_mode,'video'))
        key='video';
    else
        key='ff';
    end

    if(extract_actions)
        action_no =  length(actions);
    else
        action_no = 1;
    end

    % Traverse subject folders
    for k=1:length(folders)

        % If it is a subject folder
        if(folders(k).isdir && ~strcmp(folders(k).name,'.') && ~strcmp(folders(k).name,'..') )
            folder_name = folders(k).name;
            subj_no = folder_name(8:9);

            fprintf('Runnning for subject %s\n', subj_no)

            subj_folder_path = strcat(data_pth,folder_name,'/' );
            files = dir(subj_folder_path);

            % Works if there is a .set file and only one .set file

            noOfCorrectFiles = 0;
            for i=1:length(files)
                if((strcmp(experiment_type,'prior') && isempty(strfind(files(i).name, '.set')) == 0) || ...
                   (isempty(strfind(files(i).name, '.set'))==0 && ...
                        isempty(strfind(files(i).name, key)) == 0))
                    original_set_file_name = files(i).name;
                    noOfCorrectFiles = noOfCorrectFiles + 1;
                end
            end

            if(noOfCorrectFiles >1)
                error('More than 1 set file that has video or ff in file name');
            end

            fprintf('File Name: %s  File Path: %s\n', original_set_file_name, subj_folder_path);

            EEG = pop_loadset('filename',original_set_file_name,'filepath', subj_folder_path);

            % Store the original EEG d~a~ta in dataset number 0 
            [ALLEEG, EEG, ~] = eeg_store( ALLEEG, EEG, 0 );

            % All results of preprocessing steps are stored at set 1
            % and overwritten over each other
            % This is done to optimize memory
            
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            % Interpolate electrode Fp2 (electrode 30) in subjects 14 and
            % 15 of naive experiment
            if( strcmp(experiment_type,'naive') && ...
                (strcmp(subj_no,'14') || strcmp(subj_no,'15')) )
                EEG = pop_interp(EEG, [30], 'spherical');

                % Store the new interpolated dataset (set 1)
                [ALLEEG, EEG, ] = pop_newset(ALLEEG, EEG, 1,'gui','off');
            end
            %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

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
                        
                        
                        % Epoching
                        EEG = pop_epoch( EEG, epochs, [-0.2  0.6], 'epochinfo', 'yes');
                        [ALLEEG, EEG, ~] = pop_newset(ALLEEG, EEG, 1,'overwrite','on','gui','off'); 
                        EEG = eeg_checkset( EEG );

                        % Baseline removal
                        EEG = pop_rmbase( EEG, [-200 0]);
                        [ALLEEG, EEG, ~] = pop_newset(ALLEEG, EEG, 1,'overwrite','on','gui','off'); 
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
                        [ALLEEG, EEG, ~] = pop_newset(ALLEEG, EEG, 1, 'overwrite','on','gui','off'); 
                        % Saving the data into a struct to be able to give a proper 
                        eeg_data.eeg_data = EEG.data;
                        eeg_data.subj_no = subj_no;
                        eeg_data.agent = agent;
                        eeg_data.experiment_type = experiment_type;
                        eeg_data.input_type = presentation_mode;
                        eeg_data.action = char(actions(j));
                        save(strcat(save_path, 'action-mats/subject',subj_no,'_',title,'.mat'), '-struct','eeg_data');
                    end % action no
                end % agentlist
            end % brain regions
        end
    end
end
