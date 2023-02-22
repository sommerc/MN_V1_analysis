#@ File (label="Choose Folder with mp4 movies", style="directory") root_dir
#@ Boolean(label="Overwrite existing .roi files?") overwrite


function create_and_save_roi(file, outfile_roi) {
	run("Movie (FFMPEG)...", "choose=["+file+"] use_virtual_stack first_frame=0 last_frame=1");
	setTool("oval");
	waitForUser("Position Circle to cover the dish\nUse LEFT+DRAG to move Circle\nSHIFT+CLICK on handle to resize\nIMPORTANT No ellipses!");
	roiManager("Add");
	roiManager("Select", 0);
	
	roiManager("Save", outfile_roi);
	roiManager("Deselect");
	roiManager("Delete");
	}
	
list = getFileList(root_dir);
c = 0;
d = 0;
for (i = 0; i < list.length; i++){
		file = list[i];
        if (endsWith(file, ".mp4")) {
        	infile_mp4 = root_dir + "/" + file;
        	outfile_roi = root_dir + "/" + replace(file, ".mp4", ".roi");
        	d +=1;
        	if (!File.exists(outfile_roi) || overwrite) {
        		create_and_save_roi(infile_mp4, outfile_roi);
        		c = c+ 1;
        		};
        	};
}
showMessage("Done " + c + "/" + d + " movies");