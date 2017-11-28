# bcAudit
Headless barcode to File name verification program to be linked to remote camera software.

-This is a test project, Use at your own risk!

-The existing single exe build has the collection's regex code hardcoded into it.
-Presumes .CR2 and .JPG files are being generated from the camera.
-Presumes the .JPG files are not useful after analysis and removes them!
-using a Cannon EOS utility's linked software option link .jpg outputs to this program.
-This program loads the jpg, seeks a barcode and if it matches the collection regex and the file name is mismatched it renames it
-Then the program removes the jpg (always).
-If there is an error finding the barcode (multi-sheet specimen) or the files the program attempts to use the computer's internal "beep" speaker.

-Timeing tests have not yet been performed.
