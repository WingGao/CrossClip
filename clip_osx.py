from __future__ import with_statement
import os
import platform
import StringIO
from PIL import Image

__author__ = 'wing'

CL_TEXT = 0
CL_IMAGE = 1


def get_bmp_data(im):
    output = StringIO.StringIO()
    im.save(output, 'BMP')
    return output.getvalue()


class ClipContentItem():
    def __init__(self):
        self.cl_type = None
        self.cl_data = None


class Clipboard(object):
    def __init__(self):
        pass

    def paste(self):
        raise Exception('no method paste')

    def copy(self, item):
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
            if im is not None:
                item.cl_type = CL_IMAGE
                output = StringIO.StringIO()
                im.save(output, 'PNG')
                output.seek(0)
                item.cl_data = output.read()
                output.close()
        ctypes.windll.user32.CloseClipboard()
        return item

    def copy(self, item):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        if item.cl_type == CL_TEXT:
            win32clipboard.SetClipboardData(win32clipboard.CF_TEXT, item.cl_data)
        elif item.cl_type == CL_IMAGE:
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, item.cl_data[14:])
        win32clipboard.CloseClipboard()


class Clipboard_OSX(Clipboard):
    def __init__(self):
        super(Clipboard_OSX, self).__init__()
        self.pb = NSPasteboard.generalPasteboard()

    def paste(self):
        item = ClipContentItem()
        img = self._check_image_osx()
        if img is not None:
            item.cl_type = CL_IMAGE
            item.cl_data = img
        else:
            text = self._check_text_osx()
            item.cl_type = CL_TEXT
            item.cl_data = text
        return item

    def copy(self, item):
        if item.cl_type == CL_TEXT:
            self.pb.declareTypes_owner_(NSArray.arrayWithObject_(NSStringPboardType) ,None)
            self.pb.setString_forType_(item.cl_data, NSStringPboardType)
        elif item.cl_type == CL_IMAGE:
            nsd = NSData.alloc().initWithBytes_length_(item.cl_data, len(item.cl_data))
            image = NSImage.alloc().initWithData_(nsd)
            copiedObjects = NSArray.arrayWithObject_(image)
            self.pb.clearContents()
            self.pb.writeObjects_(copiedObjects)
        pass

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
    import win32clipboard
    from PIL import ImageGrab

    Mypb = Clipboard_Win()
elif os.name == 'mac' or platform.system() == 'Darwin':
    from AppKit import *

    Mypb = Clipboard_OSX()
else:
    raise Exception("unsupport platform")

# cit = ClipContentItem()
# cit.cl_type = CL_TEXT
# cit.cl_data = 'hellox'
# Mypb.copy(cit)
def test_copy_bmp():
    cit3 = ClipContentItem()
    cit3.cl_type = CL_IMAGE
    im = Image.open('2.png')
    cit3.cl_data = get_bmp_data(im)
    with open('a.bmp', 'wb') as f:
        f.write(cit3.cl_data)
    Mypb.copy(cit3)

def test_copy_png():
    cit3 = ClipContentItem()
    cit3.cl_type = CL_IMAGE
    im = Image.open('2.png')
    op = StringIO.StringIO()
    im.save(op,'PNG')
    cit3.cl_data=op.getvalue()
    Mypb.copy(cit3)

test_copy_png()
cit2 = Mypb.paste()
print cit2.cl_type, cit2.cl_data
if cit2.cl_type == CL_TEXT:
    print cit2.cl_data
else:
    with open('b.png', 'wb') as f:
        f.write(cit2.cl_data)


