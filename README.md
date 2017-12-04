# bcAudit
## A simple headless barcode-to-filename verification program intended to be linked to Cannon EOS remote shooting software for natural history collection digitization.

### Thanks to [Natural History Museum](https://github.com/NaturalHistoryMuseum) for their work on [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar)!

#### This is a test project, Use at your own risk!

### Quick Setup

-The inclued exe file (and therefore "Quick Setup") will only work if your collection code is included in the distribution.

-Currently supported: UCHT, TENN, APSC, HTTU, ETSU, MTSU, SWMT, UTM, UOS, MEM

-IF you want to test this with a seperate collection (or list of collections) but cannot compile it yourself feel free to contact me.

-Download the bcAudit.exe and place it in a convienent location.

-Open EOS Cannon remote shooting software and navigate to: preferences > Linked Software

-Use the checkbox to select only .jpg files and then browse to the bcAudit.exe location to link the software.

-Your EOS software should now open bcAudit and and provide it with a .jpg file when one is created.

-Set the EoS Software to output a .jpg along with the usual .CR2 file. 

-You'll have many options for .jpg quality, the "Raw + L" option has given me the best results. This ouputs a large .jpg with the .CR2 option. If your operators are outpacing the camera's ability to transfer images to the computer you can attempt to reduce the .jpg quality but you may find the barcodes are recognized less frequently.

-.jpg files will be destroyed after the program analyzes them! If your workflow requires both files to exist, modifications will be necessary.

-This has only been tested in a Windows 7 environment, I'd love to know if it functions in other versions of Windows.

### Technical details:

-Written in Python 3.6

-This program loads a jpg provided as an argument. Then seeks a barcode in that image. If the code matches a list of expected collection regex patters,the name of the .CR2 file is verified and, if necessary changed.

-If the patterns match, name corrections are made silently.

-If there is an error finding or reading the barcode (multi-sheet specimen) or an error finding the files then the program attempts to initiate a classic "Beep" to warn the user of an error.

-Initially distributed as a single .exe window file using pyinstaller.

-If you're going to compile a copy, there is an issue with pyinstaller compiling on windows 10 and running on windows 7. Easiest solution I found was just to compile on windows 7, for windows 7. This is untested in any other OS.

-My build commands are added for convenience, the paths will need to be updated for your environment.

-Presumes .CR2 and .JPG files are being generated from the camera.

-Presumes the .JPG files are not useful after analysis and removes them! This is easily altered if building your own.

-Then the program removes the jpg (always).

-No extensive timing / user rate tests have been performed. 

-Initial timing tests show an intel core 2 can keep up with <= 4 images / minute.

-Very misaligned barcodes slow down the program as it attempts various rotations. The closer to a no read zone, the longer it will take.

-No read zones at approximately +-10 degrees of: 45, 135, 225, and 315 degrees with respect to barcode angle. _``why do you have 45 degree barcodes?``_
