@echo off 
set list="T:\BIF_StaffSci\Christoph\sweengrp\paper_videos\37-38\FoxP1\144_2022-12-16_14-46-00_FoxP1_Stg3738_12.mp4.predictions.slp" "T:\BIF_StaffSci\Christoph\sweengrp\paper_videos\37-38\FoxP1\144_2022-12-16_15-46-02_FoxP1_Stg3738_22.mp4.predictions.slp" "T:\BIF_StaffSci\Christoph\sweengrp\paper_videos\37-38\En1\143_2022-12-16_13-16-02_En1_Stg3738_22.mp4.predictions.slp" "T:\BIF_StaffSci\Christoph\sweengrp\paper_videos\37-38\En1\143_2022-12-16_12-16-00_En1_Stg3738_12.mp4.predictions.slp"
(for %%f in (%list%) do ( 
   echo sleap-convert %%f --format analysis -o "%%~df%%~pf%%~nf.analysis.h5"
   sleap-convert %%f --format analysis -o "%%~df%%~pf%%~nf.analysis.h5"
))
