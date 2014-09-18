from __future__ import with_statement
import os
import platform

__author__ = 'wing'

CL_TEXT = 0
CL_IMAGE = 1


class ClipContentItem():
    def __init__(self):
        self.cl_type = None
        self.cl_data = None


class Clipboard(object):
    def __init__(self):
        pass

    def paste(self):
        raise Exception('no method')


class Clipboard_Win(Clipboard):
    def __init__(self):
        super(Clipboard_Win, self).__init__()

    def paste(self):
        pass

def write_to_file(data):
    with open('a.png', 'wb') as f:
        f.write(data)


def _check_image_win():
    ctypes.windll.user32.OpenClipboard(0)  # 8 is CF_DIB

    pass


class Clipboard_OSX(Clipboard):
    def __init__(self):
        super(Clipboard_OSX, self).__init__()
        self.pb = NSPasteboard.generalPasteboard()

    def paste(self):
        img = self._check_image_osx()
        if img is not None:
            print img
        else:
            text = self._check_text_osx()
            print text

    def _check_image_osx(self):
        pbImage = NSImage.alloc().initWithPasteboard_(self.pb)
        if pbImage is not None:
            pngData = NSBitmapImageRep.representationOfImageRepsInArray_usingType_properties_(
                pbImage.representations(), NSPNGFileType, None)
            return pngData


    def _check_text_osx(self):
        pbString = self.pb.stringForType_(NSStringPboardType)
        return pbString.encode('utf8')


if os.name == 'nt' or platform.system() == 'Windows':
    import ctypes

    pass
elif os.name == 'mac' or platform.system() == 'Darwin':
    from AppKit import *
    Mypb = Clipboard_OSX()

Mypb.paste()

