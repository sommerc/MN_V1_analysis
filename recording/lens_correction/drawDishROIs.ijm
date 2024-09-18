#@ File (label = "Select undistorted Camera Image ", description="movie1_undistorted.png", style="file") imageFile
#@ Integer (label="Number of Dishes/ROIs", min=1, max=128, value=6) nDishes
#@ String (label="Output name:", description="Dishes007", value="ROIdishes20211125") outputname

close("*");
run("Clear Results");
open(imageFile);
folderName=File.getDirectory(imageFile);
imageTitle=getTitle();

makeRectangle(10, 10, 800, 800);
run("Set Measurements...", "bounding display redirect=None decimal=5");

waitForUser("Please adjust ROI size so all dishes fit then press OK"); 

Roi.getBounds(ROIx,ROIy,ROIwidth,ROIheight);

ROIwidth=Math.ceil(ROIwidth/4)*4;
ROIheight=Math.ceil(ROIheight/4)*4;

for (i = 0; i < nDishes; i++) { 
	 selectWindow(imageTitle);
     makeRectangle(ROIx, ROIy, ROIwidth, ROIheight);
     waitString="Move ROI onto next dish " + (i+1)+ " then click OK, SHIFT+click to end";
     waitForUser(waitString); 
     runOrSkip=isKeyDown("Shift");
     setKeyDown("none");
     if (runOrSkip==0){
     	 Roi.getBounds(ROIx,ROIy,maybeWrongW,maybeWrongH);
     	 makeRectangle(ROIx, ROIy, ROIwidth, ROIheight);
     	 run("Measure");
     	 run("Overlay Options...", "stroke=red width=1 fill=none set");
     	 run("Add Selection...");
     }else {
     break;
     }
}
saveAs("Results", folderName + File.separator + outputname +".csv");



