%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% make_contours(xGrid,yGrid,xLims,yLims)
%
%
% make contours around the kernel density estimated from a
% list of 2d coordinates and save out the resulting plots
%  
% REQUIRED ARGUMENTS:
% 
% files containing coordinates of neurons must be present in 
% ../make_contours/text/ they must be in in csv format with the last 
% N_LANDMARK rows containing registration points that will not be plotted.
%
% OPTIONAL ARGUMENTS:
%
% xGrid
% yGrid - limits for grid used for kernel density estimate (microns)
%         defaults: xGrid = [0 1000], yGrid = [-400 600];
% xLims
% yLims - limits for plotting hemicord cartoon (microns)
%         defaults: xLims = [0 650],  yLims = [-400 500];
% 
% parameters for kernel density estimation are hardcoded as constants
% at the beginning of this text file
%
% N_BINS = 256, how big is the N_BINS x N_BINS kernel density map
% N_LEVELS = 9, number of contour levels to plot on kernel density estimate
% N_LANDMARKS = 4, number of registration coordinates present
%                  at the end of each data file
%
% RETURN VALUES:
%
% saves scatter and kernel density plots to ../make_contours/plots/
% allData - cell array with the coordinates of each neuron in each dataset
% names -  filename of each text files read in
%
% tamachado, updated 11/2014
% tam2138@columbia.edu
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [allData, names] = make_contours(xGrid,yGrid,xLims,yLims)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% define constants and parameters
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
coor = input('Do you want to plot (T)horacic or (Lumbar) coordinates :','s');
if ~(coor == 'T' || coor == 'L')
    error('Input L or T');
end


% constants
CORD_COLOR = [.96 .96 .96]; % color for spinal cord outline (.96 = 245/255)
N_LEVELS = 8;               % how many contour levels should we draw?
N_BINS = 256;               % how big of an NxN matrix to use for kde?
N_LANDMARK = 4;             % these are the last N points in each data file

% define limits for plotting stuff (in microns)
if nargin < 4
    if ~exist('xGrid','var') || ~exist('yGrid','var')
       xGrid = [0 1000]; yGrid = [-400 600]; % limits for kde grid
    end
    if ~exist('xLims','var') || ~exist('yLims','var')  
       xLims = [0 650];  yLims = [-400 500]; % limits for plotting cords
    end
end

% add export_fig to the path for saving pretty pdfs if necessary
if ~exist('export_fig','file')
    path = which('make_contours');
    ind = strfind(path,'make_contours.m');
    addpath([path(1:ind-1) 'export_fig']);
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% prepare stuff for plotting
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% close all open figures
% close all;

% get dataset names
[names, paths] = get_dataset_names;
names=regexprep(names,'_','-');
nDatasets = length(paths);

% accumulate all points as we load datasets; return this value
allData = cell(nDatasets,1);

% scale cord and translate cord outline
if coor == 'L'
    load('cord');  
elseif coor == 'T'
    load('cordT');
end

cord.x = cord.x * diff(xLims);
cord.y = cord.y * diff(yLims);
cord.x = cord.x - min(cord.x) + xLims(1); 
cord.y = cord.y - min(cord.y) + yLims(1);

% generate three ticks for each axis
if coor == 'T'
    xLims = [0 450];
end

xticks = [xLims(1) 0 xLims(2)];
yticks = [yLims(1) 0 yLims(2)];
if min(xLims) >= 0, xticks = [xLims(1) round(mean(xLims)) xLims(2)]; end
if min(xLims) >= 0, yticks = [yLims(1) round(mean(yLims)) yLims(2)]; end

% get bounds for plotting contours
xBounds = linspace(xGrid(1),xGrid(2),N_BINS);
yBounds = linspace(yGrid(1),yGrid(2),N_BINS);

% set up figures for plotting
contourOverlay = figure; set(gcf,'Color','w');
% contourMatrix = figure; set(gcf,'Color','w');

% colors to use for big matrix of all contours
cols = jet(nDatasets);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% make all plots
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

for ii = 1:nDatasets
    % load in data from file and flip over x axis
%     data = importdata(paths{ii});
%     try
%         data = data.data;
%         data(:,1) = -(data(:,1));
%     catch
        data=xlsread(paths{ii});
        
%     end    
    
    % Coordinate Adjustment 
    if coor == 'T'
        data(:,1) = data(:,1)/1.49;
    end
    %
    % save data
    allData{ii} = data;
    
    % plot data points
    figure; set(gcf,'Color','w');
    cax = subplot(1,2,1);
    make_spinal_cord(cax);
    title(names(ii,:));
    plot(data(1:end-N_LANDMARK,1),data(1:end-N_LANDMARK,2),'k.');
    fix_axes(cax)
    
    % plot individual contours based on kernel density
    cax = subplot(1,2,2);
    make_spinal_cord(cax);
    
    if size(data,1)>6
        % get kernel density function
        [~, density] = kde2d(data(1:end-N_LANDMARK,:),N_BINS,...
            [xGrid(1) yGrid(1)],[xGrid(2) yGrid(2)]);
    
        % make and contours around kernel density function
        plot_contours(cax,density,xBounds,yBounds);
        fix_axes(cax);
    end
    % print current image
%     export_fig('pdf',['plots\' names{ii} '.pdf']);
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %ADD IMAGE SAVE OPTION HERE
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % show each contour in its own subplot
%     figure(contourMatrix);
%     cax = subplot(9,5,ii);
%     make_spinal_cord(cax);
%     plot_contours(cax,density,xBounds,yBounds,cols(ii,:));
%     axis image;
%     title(names(ii,:));
    
    % print all contours
%     if ii == nDatasets
%         set(gcf, 'Position', get(0,'Screensize'));
%         export_fig('pdf',['plots\' 'all-contours.pdf']);
%     end
    
    % plot all data points on one plot
    if size(data,1)>6
        figure(contourOverlay); 
        cax = subplot(1,2,1);
        if ii == 1, make_spinal_cord(cax); end
        title('all genes');
        hold on
        plot(data(1:end-N_LANDMARK,1),data(1:end-N_LANDMARK,2),...
           '.','Color','k','MarkerSize',8);
        
        fix_axes(cax)
    
        % plot all contours on one plot
        cax = subplot(1,2,2);
        if ii == 1, make_spinal_cord(cax); end
        plot_contours(cax,density,xBounds,yBounds,cols(ii,:));
        fix_axes(cax)
    end
end



% Plot all datapoints on One plot
figure; 
cax = subplot(1,2,1);
make_spinal_cord(cax);
title('all genes');
% a=cell2mat(allData);
AData = [];
for i=1:length(allData)
    ss = size(allData{i},1);
    AData = [AData; allData{i}(1:ss-5,:)];
end

plot(AData(:,1),AData(:,2),...
        '.','Color','k','MarkerSize',8);
fix_axes(cax)
    
% plot all contours on one plot
cax = subplot(1,2,2);
make_spinal_cord(cax);
[~, density] = kde2d(AData,N_BINS,...
        [xGrid(1) yGrid(1)],[xGrid(2) yGrid(2)]);
plot_contours(cax,density,xBounds,yBounds);
fix_axes(cax)


% save out summary plot
% export_fig(contourOverlay,'pdf','plots\summary.pdf');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% helper functions used during plotting
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% plot contours on kernel density
function plot_contours(cax,density,xBounds,yBounds,color)
    
    % setup the axes
    if nargin < 5, color = 'k'; end
    axes(cax);
    
    % use contourf instead of contour because contourf draws smoother lines
    [~,h] = contourf(xBounds,yBounds,density,N_LEVELS,'Color',color);
    
    % get rid of any colors on contour shapes
    allH = allchild(h);
    if isempty(allH)
        allH=h;
    end    
    set(allH,'FaceColor','none'); 
    
    % hide box around contours
%     set(allH(end),'EdgeColor','none'); 
end

% print spinal cord outline
function make_spinal_cord(cax)
    
    % setup the axes
    axes(cax);
    hold on;
    set(cax,'TickDir','out','Layer','top');
    
    % draw the spinal cord outline
    patch(cord.x,cord.y,CORD_COLOR,'EdgeColor','k');
end

% standardize the axes we're using once we've plotted everything in them
function fix_axes(cax)
    axes(cax);
    axis image; xlabel('\mum'); ylabel('\mum');
    ylim(yLims); xlim(xLims);
    set(gca,'XTick',xticks,'YTick',yticks);
end
end