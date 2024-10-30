function [nameShort, cd, name] = get_dataset_names(subfolder,spaces)

if ~exist('subfolder','var')
    subfolder = 'text';
end

if ~exist('spaces','var')
    spaces = 0;
end

% if this isn't windows, crash...
if ~strcmp(computer('arch'),'win64')
    % this is windows specific due variable behavior of MATLAB's ls command
    error('get_dataset_names() is only compatible with windows machines!'); 
end

% get all text files in the subfolder 

nameVector = ls(subfolder);
name = cell(size(nameVector,1)-2,1); nameShort = name;

for ii = 1:length(name)
    % get current string
    name{ii} = nameVector(ii+2,:);
    
    % get rid of extension and/or spaces
    if spaces
        nameShort{ii} = name{ii};
        nameShort{ii}(nameShort{ii} == ' ') = [];
    else
        nameShort{ii} = name{ii}(1:find(name{ii} == '.')-1);
    end
end

% get paths
cd = cell(length(name),1);
for ii = 1:length(cd)
    cd{ii} = [pwd '\' subfolder '\' name{ii}];
end


