from __future__ import with_statement
import os
import platform

__author__ = 'wing'


def write_to_file(data):
    with open('a.png', 'wb') as f:
        f.write(data)
#osx
def _get_pb_osx():
    return NSPasteboard.generalPasteboard()

def _check_image_osx(pb):
    pbImage = NSImage.alloc().initWithPasteboard_(pb)
    if pbImage is not None:
        pngData = NSBitmapImageRep.representationOfImageRepsInArray_usingType_properties_(
            pbImage.representations(), NSPNGFileType, None)
        return pngData

def _check_text_osx(pb):
    pbString = pb.stringForType_(NSStringPboardType)
    return pbString.encode('utf8')

def loop():
    img = check_image(MyPb)
    if img is not None:
        print img
    else:
        text = check_text(MyPb)
        print text

if os.name == 'nt' or platform.system() == 'Windows':
    pass
elif os.name == 'mac' or platform.system() == 'Darwin':
    from AppKit import *
    MyPb = _get_pb_osx()
    check_image = _check_image_osx
    check_text = _check_text_osx

loop()