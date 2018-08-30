import os
import argparse
import sys
import re
from PIL import Image
import pyzbar
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol

inputImgFile = ''
barCodeType = 'CODE128'
collectionPatterns = [('^(UCHT\d{6})\D*'),
                    ('^(TENN-V-\d{7})\D*'),
                    ('^(APSC\d{7})\D*'),
                    ('^(HTTU\d{6})\D*'),
                    ('^(ETSU\d{6})\D*'),
                    ('^(MTSU\d{6})\D*'),
                    ('^(SWMT\d{5})\D*'),
                    ('^(UTM\d{5})\D*'),
                    ('^(UOS\d{5})\D*'),
                    ('^(MEM\d{6})\D*'),
                    ('^(GSMNP\d{6})\D*')]

inputFileType = '.jpg'
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
    img = Image.open(inputImgFile)
    bcData = decode(img)
    if len(bcData) != 0:
        checkPattern(inputImgFile, bcData, img)
    # if it failed to read a file name, then try a few things
    else:            
        for i in rotationList:
            img2 = img.rotate((i),resample=Image.NEAREST,expand = True)
            bcData = decode(img2)
            if len(bcData) != 0:
                checkPattern(inputImgFile, bcData, img)
                break

        # Looks like it failed to find barcode value, gotta ask the user.
        userInput = askBarcodeDialog('No Barcode Found.\n\nEnter the Desired File Name(without the extension):')
        handleResult(inputImgFile, userInput, img)


def checkPattern(inputImgFile,bcData, img):
    ''' checks the retrieved BC value with a known collection regex pattern '''

    bcValue = str(bcData[0].data).split("'")[1].rstrip("'") #clean up the Barcode                           
    for collRegEx in collectionPatterns:
        rePattern = re.compile(collRegEx) #match read BC to regex pattern (is this YOUR Barcode?)
        if rePattern.match(bcValue):
            handleResult(inputImgFile,bcValue,img)
            return

#In case there are multiple BCs, flip the image, and rescan for BC from other end.
#Then essentially restart the function. (Probably a nicer way to do this)

    img2 = img.rotate((180),resample=Image.NEAREST,expand = True)
    bcData = decode(img2)
    bcValue = str(bcData[0].data).split("'")[1].rstrip("'")
    for collRegEx in collectionPatterns:
        rePattern = re.compile(collRegEx )
        if rePattern.match(bcValue):
            handleResult(inputImgFile, bcValue, img)
            return
  
    userInput = askBarcodeDialog('Barcode Does Not Match Any Known Catalog Code Patterns.\n\nEnter the Catalog Number:', bcValue)
    handleResult(inputImgFile, userInput, img)


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


def askBarcodeDialog(queryText, initialValue = ''):
    '''When a barcode cannot be read, offer the user an entry box
    This can be integrated with a HID barcode scanner, those which
    automatically add a carriage return after the scan would perform very well
    Use initialValue if the file already exists (ie: part a, b, c photos)'''

    import tkinter as tk
    from tkinter import simpledialog

    root = tk.Tk()
    root.withdraw()  # hide the main window (it'll be empty)
#   root.geometry("580x400+300+200")
    root.title("Pah Tum")
    # The barcode entry popup box.
    
    bc_entry_box = None
    while bc_entry_box == None:
        bc_entry_box = simpledialog.askstring("BCAudit", queryText, parent=root, 
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


def handleResult(inputImgFile, bcValue, img):
    ''' renames the resulting files appropriately '''
    
    try:
        oldRawName = inputImgFile.rsplit('.',1)[0] + rawFileExt
        inputBaseName = os.path.basename(inputImgFile)
        newRawBaseName = bcValue + rawFileExt
        newRawName = inputImgFile.replace(inputBaseName, newRawBaseName)
        # check if the file name already exists there...
        import glob
        imDir = os.path.dirname(inputImgFile)
        print('{}//{}*{}'.format(imDir, bcValue, rawFileExt))
        fileQty = len(glob.glob('{}/{}*{}'.format(imDir, bcValue, rawFileExt)))
        if fileQty > 0:
            import string
            # generate a number to alphabet lookup string
            alphaLookup = {n+1:ch for n, ch in enumerate(string.ascii_lowercase)}
            # add the lower letter to the bcValue
            initialValue = None
            while initialValue == None:
                initialValue = bcValue + alphaLookup.get(fileQty, '_{}'.format(str(fileQty)))
                initialValue = askBarcodeDialog('{} Already Exists.\n\nEnter the Desired File Name (without the extension):'.format(bcValue), initialValue)
            else:
                bcValue = initialValue
            newRawBaseName = bcValue + rawFileExt
            newRawName = inputImgFile.replace(inputBaseName, newRawBaseName)

        if oldRawName != newRawName:
            try:
                os.rename(oldRawName, newRawName)
            # I'm not sure this exception can ever happen considering the file checking that happens in advance.
            except WindowsError:
                userInput = askBarcodeDialog('Enter the Catalog Number', bcValue + 'a')
                try:
                    os.rename(oldRawName, userInput + rawFileExt)
                except WindowsError as e:
                    noticeBox('"{}" renaming "{}"'.format(e, inputImgFile))
            print('Modified File Name!')
    except FileNotFoundError as e:  #Looks like the expected file is missing    
        noticeBox('"{}" not found'.format(inputImgFile))
        print(e)
    
    if removeInputFile:
        os.remove(inputImgFile)            
     
if __name__ == '__main__':
    main()
