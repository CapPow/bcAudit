import os
import argparse
import sys
import re
from PIL import Image
import pyzbar
#from pyzbar.pyzbar import *
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
import winsound


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
                    ('^(UOS\d{5})\D*')]
inputFileType = '.jpg'
rawFileExt = '.CR2'
beepFrequency = 2000
beepDuration = 700
rotationList = [12, -12,  21, -21]
#rotationList = [6, -12, 48, -288]

def main(args=None):
    if args is None:
        args = sys.argv[1:]

        parser = argparse.ArgumentParser(
            description='Reads barcodes in images, Beeps if no Matches found, Corrects image name if not matching.'
        )
        parser.add_argument('image', nargs='+')
        args = parser.parse_args(args)

    inputImgFile = args.image[0]
    img = Image.open(inputImgFile)
    bcData = decode(img)
    if len(bcData) != 0:
        checkPattern(inputImgFile, bcData, img)
    else:            
        for i in rotationList:
            img2 = img.rotate((i),resample=Image.NEAREST,expand = True)
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
    for collRegEx in collectionPatterns:
        rePattern = re.compile(collRegEx) #match read BC to regex pattern (is this YOUR Barcode?)
        if rePattern.match(bcValue):
            handleResult(inputImgFile,bcValue,img)
            return
#Incase there are multiple BCs, flip the image, and rescan for BC from other end.
#Then essentially restart the function. (Probably a nicer way to do this)
    img2 = img.rotate((180),resample=Image.NEAREST,expand = True)
    bcData = decode(img2)
    bcValue = str(bcData[0].data).split("'")[1].rstrip("'")
    for collRegEx in collectionPatterns:
        rePattern = re.compile(collRegEx )
        if rePattern.match(bcValue):
            handleResult(inputImgFile,bcValue,img)
            return
    winsound.Beep(beepFrequency + 200, beepDuration) #give up and beep at the user
    os.remove(inputImgFile)
    print('Barcode Does Not Match Collection Code!')
    winsound.Beep(beepFrequency-200, beepDuration)


def handleResult(inputImgFile,bcValue, img):
    try:
        print(inputImgFile)
        oldRawName = inputImgFile.rsplit('.',1)[0] + rawFileExt
        print(oldRawName)
        inputBaseName = os.path.basename(inputImgFile)
        newRawBaseName = bcValue + rawFileExt
        newRawName = inputImgFile.replace(inputBaseName, newRawBaseName)
        print(newRawName)
        if oldRawName != newRawName:
            try:
                os.rename(oldRawName, newRawName)                
            except WindowsError:
                winsound.Beep(beepFrequency + 200, beepDuration)
                winsound.Beep(beepFrequency-200, beepDuration)
                try:
                    os.rename(oldRawName, bcValue + '_{}'.format(1) + rawFileExt)
                except WindowsError:
                    print('There was an issue renaming the image!')
            print('Modified File Name!')
    except FileNotFoundError as e:  #Looks like the expected file is missing    
        winsound.Beep(beepFrequency + 200, beepDuration)
        print(e)
    os.remove(inputImgFile)            
     
if __name__ == '__main__':
    main()
