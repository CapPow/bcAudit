import os
import argparse
import sys
import re
from PIL import Image
import pyzbar
from pyzbar.pyzbar import *
#from pyzbar.pyzbar import decode
#from pyzbar.pyzbar import ZBarSymbol
import winsound


inputImgFile = ''
barCodeType = 'CODE128'
#collRegEx = ('^(TENN-V-\d{7})\D*')
collRegEx = ('^(UCHT\d{6})\D*')
inputFileType = '.jpg'
rawFileExt = '.CR2'
beepFrequency = 2000
beepDuration = 700
rotationList = [6, -12, 48, -288]

def main(args=None):
    if args is None:
        args = sys.argv[1:]

        parser = argparse.ArgumentParser(
            description='Reads barcodes in images, Beeps if no Matches found, Corrects image name if not matching.'
        )
        parser.add_argument('image', nargs='+')
        parser.add_argument(
            '-v', '--version', action='version',
            version='%(prog)s ' + pyzbar.__version__
        )
        args = parser.parse_args(args)

    inputImgFile = args.image[0]
    img = Image.open(inputImgFile)
    bcData = decode(img)
    if len(bcData) != 0:
        checkPattern(inputImgFile, bcData, img)
    else:            
        for i in rotationList:
            img2 = img.rotate((i),resample=Image.BICUBIC,expand = True)
            bcData = decode(img2)
            if len(bcData) != 0:
                checkPattern(inputImgFile, bcData, img)
                break
        
            
        winsound.Beep(beepFrequency, beepDuration) #Looks like it failed to find BC, better warn user.
        os.remove(inputImgFile)
        print('No Barcode Found to Read!')
        winsound.Beep(beepFrequency-200, beepDuration)

def checkPattern(inputImgFile,bcData, img):
    bcValue = str(bcData[0].data).split("'")[1].rstrip("'") #clean up the Barcode                           
    rePattern = re.compile(collRegEx) #match read BC to regex pattern (is this YOUR Barcode?)
    if rePattern.match(bcValue):
        handleResult(inputImgFile,bcValue,img)
    else:
        img2 = img.rotate((180),resample=Image.BICUBIC,expand = True)
        if rePattern.match(str(decode(img2))):
            handleResult(inputImgFile,bcValue,img)
        else:
            winsound.Beep(beepFrequency + 200, beepDuration)
            os.remove(inputImgFile)            
            print('Barcode Does Not Match Collection Code!')
            winsound.Beep(beepFrequency-200, beepDuration)
    

def handleResult(inputImgFile,bcValue, img):
    try:
        oldRawName = inputImgFile.split('.')[0] + rawFileExt
        newRawName = bcValue + rawFileExt
        if oldRawName != newRawName:
            try:
                os.rename(oldRawName, newRawName)                
            except WindowsError:
                winsound.Beep(beepFrequency + 200, beepDuration)
                winsound.Beep(beepFrequency-200, beepDuration)
                try:
                    os.rename(oldRawName, bcValue + '_{}'.format(1) + rawFileExt)
                except WindowsError:
                    print('There appear to be multiple files wanting the same names!')
            print('Modified File Name!')
    except FileNotFoundError as e:  #Looks like the expected file is missing    
        winsound.Beep(beepFrequency + 200, beepDuration)
        print(e)
    os.remove(inputImgFile)            
    
if __name__ == '__main__':
    main()
