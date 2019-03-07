"""
This work is heavily reliant upon the pyzbar library, 
As such, many thanks to their work! pyzbar souce is
located at: https://github.com/NaturalHistoryMuseum/pyzbar  
"""


import os
import argparse
import sys
import re
from PIL import Image
import tkinter as tk
from pyzbar.pyzbar import decode

inputImgFile = ''
barCodeType = 'CODE128'

# read the collection code pattern(s)
try:
    with open('collection_code_patterns.txt', 'r') as file: 
        lines = file.read().split('\n')
        collectionPatterns = [x for x in lines if not any([x.strip().startswith('#'), x == ''])]
        #comment_less = filter(None, (line.split('#')[0].strip() for line in lines))    
except FileNotFoundError:
    collectionPatterns = [(r'^(UCHT\d{6})\D*'),
                      (r'^(TENN-V-\d{7})\D*'),
                      (r'^(APSC\d{7})\D*'),
                      (r'^(HTTU\d{6})\D*'),
                      (r'^(ETSU\d{6})\D*'),
                      (r'^(MTSU\d{6})\D*'),
                      (r'^(SWMT\d{5})\D*'),
                      (r'^(UTM\d{5})\D*'),
                      (r'^(UOS\d{5})\D*'),
                      (r'^(MEM\d{6})\D*'),
                      (r'^(GSMNP\d{6})\D*')]

rawFileExt = '.CR2'
# do you want to remove the .jpg file when this is all done?
# some workflows want both jpg and raw files.
removeInputFile = True

rotationList = [12, -12,  21, -21]


# set up WindowsError if it is appropriate
try:
    from exceptions import WindowsError
except ImportError:
    class WindowsError(OSError): pass


def main(args=None):
    if args is None:
        args = sys.argv[1:]

        parser = argparse.ArgumentParser(
            description='Reads barcodes in images, Corrects image name if not matching.')
        parser.add_argument('image', nargs='+')
        args = parser.parse_args(args)

    inputImgFile = args.image[0]
    try:
        img = Image.open(inputImgFile)
    except (FileNotFoundError, OSError, WindowsError) as e:
        noticeBox('{}'.format(e))
        return

    bcData = decode(img)  # get the barcode data
    if len(bcData) == 0:
        for i in rotationList:
            img2 = img.rotate((i), resample=Image.NEAREST, expand=True)
            bcData = decode(img2)
            if len(bcData) > 0:
                bcValue = checkPattern(bcData, img)
                handleResult(inputImgFile, bcValue, img)
                break
        # Give up on rotation, and just ask the user.
        userInput = askBarcodeDialog('No Barcode Found.\n\nEnter the Desired File Name(without the extension):')
        handleResult(inputImgFile, userInput, img)
    else:
        bcValue = checkPattern(bcData, img)
        handleResult(inputImgFile, bcValue, img)


def checkPattern(bcData, img):
    ''' checks the retrieved BC value with a known collection regex pattern
    if it finds  a non-matching Barcode, it assumes the alignment is correct
    but tries from the opposite end of the sheet. Incase of multiple BCs'''

    for i in range(2):
        bcValue = str(bcData[0].data).split("'")[1].rstrip("'")  # clean up the Barcode
        for collRegEx in collectionPatterns:
            rePattern = re.compile(collRegEx)  # match BC to regex patterns
            if rePattern.match(bcValue):
                return bcValue
        # If we have a bc which does not match, rotate it 180deg and try again
        # as it may have multiple bcs, so start from other end.
        img = img.rotate((180), resample=Image.NEAREST, expand=True)
        bcData = decode(img)
    #  if none of that matched the barcode ask the user:
    userInput = askBarcodeDialog('Barcode Does Not Match Any Known Catalog Code Patterns.\n\nEnter the Catalog Number:', bcValue)
    return userInput


def handleResult(inputImgFile, bcValue, img):
    ''' renames the input files appropriately '''
    try:
        oldRawName = inputImgFile.rsplit('.', 1)[0] + rawFileExt
        inputBaseName = os.path.basename(inputImgFile)
        newRawBaseName = bcValue + rawFileExt
        newRawName = inputImgFile.replace(inputBaseName, newRawBaseName)
        # check if the file name already exists there...
        import glob
        
        imDir = os.path.dirname(inputImgFile)
        if imDir:
            fileQty = len(glob.glob('{}/{}*{}'.format(imDir, bcValue, rawFileExt)))
        else:
            fileQty = len(glob.glob('{}*{}'.format(bcValue, rawFileExt)))
        if fileQty > 0:
            import string
            # generate a number to alphabet lookup string
            alphaLookup = {n+1: ch for n, ch in enumerate(string.ascii_lowercase)}
            # add the lower letter to the bcValue
            initialValue = None
            while initialValue is None:
                initialValue = bcValue + alphaLookup.get(fileQty,'_{}'.format(str(fileQty)))
                initialValue = askBarcodeDialog('{} Already Exists.\n\nEnter the Desired File Name (without the extension):'.format(bcValue), initialValue)              
                # address when the user proposes (again) a file name which already exists (still?)
                proposedValue = os.path.exists(initialValue + rawFileExt)
                if proposedValue:
                    initialValue = None
            else:
                bcValue = initialValue
            newRawBaseName = bcValue + rawFileExt
            newRawName = inputImgFile.replace(inputBaseName, newRawBaseName)

        if oldRawName != newRawName:
            try:
                os.rename(oldRawName, newRawName)
            # I'm not sure this exception can ever happen considering the file checking that happens in advance.
            except WindowsError:
                userInput = askBarcodeDialog('Enter the Catalog Number',
                                             bcValue + 'a')
                try:
                    os.rename(oldRawName, userInput + rawFileExt)
                except WindowsError as e:
                    noticeBox('"{}" renaming "{}"'.format(e, inputImgFile))
            print('Modified File Name!')
    except FileNotFoundError as e:  # Looks like the expected file is missing
        noticeBox('{}'.format(e))
        return

    if removeInputFile:
        os.remove(inputImgFile)


def noticeBox(errMsg):
    ''' displays an error notice with the string provided in errMsg '''
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()  # hide the main window (it'll be empty)
    root.title("bcAudit")
    msg_box = messagebox.showerror('BCAudit', errMsg)
    if msg_box:
        root.destroy()  # kill the GUI, before we exit the function.
        return   # return the result

    root.mainloop()  # Initiate the GUI loop


def askBarcodeDialog(queryText, initialValue=''):
    '''When a barcode cannot be read, offer the user an entry box
    This can be integrated with a HID barcode scanner, those which
    automatically add a carriage return after the scan would perform very well
    Use initialValue if the file already exists (ie: part a, b, c photos)'''

    import tkinter as tk
    from tkinter import simpledialog

    root = tk.Tk()
    root.withdraw()  # hide the main window (it'll be empty)
    root.title('bcAudit')
    # The barcode entry popup box.
    bc_entry_box = None
    while bc_entry_box is None:
        bc_entry_box = simpledialog.askstring("BCAudit", queryText,
                                              parent=root,
                                              initialvalue=initialValue)
    # if the bc_entry_box has results then use them
    if bc_entry_box:
        #   If they cancel it returns None
        userEntry = bc_entry_box
        #  If they enter nothing, chang the empty string into None
        if userEntry == '':
            userEntry = None
        root.destroy()  # kill the GUI, before we exit the function.
        return userEntry  # return the result
    root.mainloop()  # Initiate the GUI loop


if __name__ == '__main__':
    main()
