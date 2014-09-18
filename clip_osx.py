from __future__ import with_statement
import os
import platform
import StringIO

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
        raise Exception('no method paste')

    def copy(self):
        raise Exception('no method copy')


class Clipboard_Win(Clipboard):
    def __init__(self):
        super(Clipboard_Win, self).__init__()

    def paste(self):
        item = ClipContentItem()
        ctypes.windll.user32.OpenClipboard(0)
        pcontents = ctypes.windll.user32.GetClipboardData(1)  # 1 is CF_TEXT
        if pcontents != 0:
            cp = ctypes.c_char_p(pcontents)
            item.cl_type = CL_TEXT
            item.cl_data = cp.value
        else:
            im = ImageGrab.grabclipboard()
            item.cl_type = CL_IMAGE
            output = StringIO.StringIO()
            im.save(output, 'PNG')
            output.seek(0)
            item.cl_data = output.read()
            output.close()
        ctypes.windll.user32.CloseClipboard()

    def copy(self):
        pass


def write_to_file(data):
    with open('a.png', 'wb') as f:
        f.write(data)


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
    from PIL import ImageGrab

    Mypb = Clipboard_Win()
elif os.name == 'mac' or platform.system() == 'Darwin':
    from AppKit import *

    Mypb = Clipboard_OSX()
else:
    raise Exception("unsupport platform")

Mypb.paste()

