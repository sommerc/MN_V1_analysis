@echo off 
set list="Y:\BIF_StaffSci\Christoph\sweengrp\paper_videos\37-38\WT\114_2022-11-11 08-51-17_WT_Stg3538_122.mp4.predictions.slp"
(for %%f in (%list%) do ( 
   echo sleap-convert %%f --format analysis -o "%%~df%%~pf%%~nf.analysis.h5"
   sleap-convert %%f --format analysis -o "%%~df%%~pf%%~nf.analysis.h5"
))
