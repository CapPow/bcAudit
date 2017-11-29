# bcAudit
## A simple headless barcode-to-filename verification program intended to be linked to Cannon EOS remote shooting software for natural history collection digitization.

### Thanks to [Natural History Museum](https://github.com/NaturalHistoryMuseum) for their work on [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar)!

-This is a test project, Use at your own risk!

-Initially compiled into single .exe windows files using pyinstaller.

-If you're going to compile a copy, there is an issue with pyinstaller compileing on windows 10 and running on windows 7. Easiest solution I found was just to compile on windows 7, for windows 7. This is untested in any other OS.

-The existing single exe build has the collection's regex code hardcoded into it.

-Presumes .CR2 and .JPG files are being generated from the camera.

-Presumes the .JPG files are not useful after analysis and removes them! This is easily altered if building your own.

-Using a Cannon EOS utility's linked software option link .jpg outputs to this program.

-This program loads the jpg, seeks a barcode and if it matches the collection regex and the file name is mismatched it renames it

-Then the program removes the jpg (always).

-If there is an error finding the barcode (multi-sheet specimen) or the files the program attempts to use the computer's internal "beep" speaker.

-No extensive timing / user rate tests have been performed. 

-Initial timing tests show an intel core 2 can keep up with >= 4 images / minute, provided the barcodes are applied within 12+- degrees of 90degree increments. 

-Very misaligned barcodes slow down the program as it attempts various rotations.

-No read zones at approximately +-10 degrees of: 135, 225, 315 and 45 degrees with respect to barcode angle. (why do you have 45 degree barcodes???)
