clc;
clear;
[ALLEEG, EEG, CURRENTSET, ALLCOM] = eeglab;
%pth='/auto/data2/oelmas/EEG_AgentPerception_NAIVE/Data/';
%pth='/Users/huseyinelmas/Desktop/CCN-Lab/data/set_files/';
pth='/home/sena/Desktop/set_test/';
folders = dir(pth);
robot = {'S101' 'S102' 'S103' 'S104' 'S105' 'S106' 'S107' 'S108'};
actions = {'drink','grasp','handwave','talk','nudge','paper','turn','wipe'};
android = {'S111' 'S112' 'S113'  'S114' 'S115' 'S116'  'S117' 'S118'};
human = {'S121' 'S122' 'S123'  'S124' 'S125' 'S126'  'S127' 'S128'};
channels = {'Fp1', 'Fz', 'F3', 'F7', 'FT9', 'FC5' ,'FC1', 'C3', 'T7', 'CP5', 'CP1'...
    'Pz' ,'P3' ,'P7' ,'O1' ,'Oz' ,'O2' ,'P4', 'P8' ,'CP6' ,'CP2' ,'Cz' ,'C4' ,'T8' ...
    'FT10', 'FC6', 'FC2', 'F4', 'F8', 'Fp2', 'AF7', 'AF3', 'AFz', 'F1', 'F5', 'FT7'...
    'FC3', 'FCz', 'C1', 'C5', 'TP7', 'CP3', 'P1', 'P5', 'PO7', 'PO3', 'POz', 'PO4'...
    'PO8', 'P6', 'P2', 'CPz', 'CP4', 'TP8', 'C6', 'C2', 'FC4', 'FT8', 'F6', 'F2'... 
    'AF4' ,'AF8'};
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

for k=1:length(folders)
    if(folders(k).isdir && ~strcmp(folders(k).name,'.') && ~strcmp(folders(k).name,'..') )
       folder_name = folders(k).name;
       subj_no = folder_name(5:6);
       fprintf('Runnning for subject %s\n',subj_no)
       file_path = strcat(pth,folder_name,'/');
       files = dir(file_path);
       save_path = file_path + "action-mats/";
       % Works if there is a .set file and only one .set file
       for i=1:length(files)
           if( isempty(strfind(files(i).name, ".set")) == 0)
               file_name = files(i).name;
           end
       end
       fprintf('File Name: %s  File Path: %s\n',file_name,file_path);
       for i=1 :agent_list.Count
           agent_types = keys(agent_list);
           agent = char(agent_types(i));
           fprintf('Runnning for agent: %s\n',agent)
           for j=1:action_no 
               EEG = pop_loadset('filename',file_name,'filepath',file_path);
               [ALLEEG, EEG, CURRENTSET] = eeg_store( ALLEEG, EEG, 0 );
               EEG = eeg_checkset( EEG );
               if(with_actions)
                   epochs = agent_list(agent);
                   title = agent;
               else
                   temp = agent_list(agent);
                   fprintf('And action: %s\n',char(actions(j)))
                   epochs = temp(j);
                   title = strcat(agent,'-',char(actions(j))); 
               end
               %
               %EEG = pop_epoch( EEG, epochs, [-0.2 0.6], 'newname', strcat(file_name,'epochs',title), 'epochinfo', 'yes');
               %[ALLEEG, EEG, CURRENTSET] = pop_newset(ALLEEG, EEG, 1,'savenew',strcat(file_name,'epochs',title),'overwrite','on','gui','off'); 
               %EEG = eeg_checkset( EEG );
               %EEG = pop_select( EEG,'channel',channels);
               %[ALLEEG, EEG, CURRENTSET] = pop_newset(ALLEEG, EEG, 2,'savenew',strcat(file_name,'epochs','channels'),'overwrite','on','gui','off');    
               
                % Epoching
               EEG = pop_epoch( EEG, epochs, [-0.2  0.600], 'newname', strcat('subj', subj_no ,'_epochs_', title), 'epochinfo', 'yes');
               [ALLEEG, EEG, CURRENTSET] = pop_newset(ALLEEG, EEG, 1,'savenew',strcat(file_path, 'steps/subj', subj_no , '_', title, '_step1_epchs.set'),'overwrite','on','gui','off'); 
               EEG = eeg_checkset( EEG );

               % Baseline removal
               EEG = pop_rmbase( EEG, [-200 0]);
               [ALLEEG, EEG, ~] = pop_newset(ALLEEG, EEG, 2, 'savenew', strcat(file_path, 'steps/subj', subj_no , '_', title, '_step2_rem_bas.set'),'gui','off'); 
               EEG = eeg_checkset( EEG );

               % Select channels
               EEG = pop_select( EEG,'channel', channels);
               [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, 2,'savenew',strcat(file_path, 'steps/subj', subj_no , '_', title, '_step3_chnl.set'),'overwrite','on','gui','off'); 

               % Saving the data into a struct to be able to give a proper 
               eeg_data.("eeg_data") = EEG.data;
               eeg_data.("subj_no") = subj_no;
               eeg_data.("agent") = agent;
               eeg_data.("experiment_type") = exp_type;
               eeg_data.("input_type") = mode;
               eeg_data.("action") = char(actions(j));
               save(strcat(save_path, 'subject',subj_no,'_',title,'.mat'), '-struct','eeg_data');
           end
       end
    end
end

    