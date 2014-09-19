#coding:utf8
from __future__ import with_statement
import os
import platform
import StringIO
import struct
from PIL import Image
import SocketServer
import pickle
import threading
import socket
import time

__author__ = 'wing'

CL_TEXT = 0
CL_IMAGE = 1


def get_bmp_data(im):
    output = StringIO.StringIO()
    im.convert('RGB').save(output, 'BMP')
    return output.getvalue()


def write_to_file(data):
    with open('%d.png' % time.time(), 'wb') as f:
        f.write(data)


def show_img(data):
    s = StringIO.StringIO(data)
    im = Image.open(s)
    im.show()


class ClipContentItem():
    def __init__(self):
        self.cl_type = None
        self.cl_data = None

    def to_bmp_data(self):
        if self.cl_type == CL_IMAGE:
            sdata = StringIO.StringIO(self.cl_data)
            im = Image.open(sdata)
            return get_bmp_data(im)
        return None


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
            win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, item.cl_data.decode('utf8'))
        elif item.cl_type == CL_IMAGE:
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, item.to_bmp_data()[14:])
        win32clipboard.CloseClipboard()


class Clipboard_OSX(Clipboard):
    def __init__(self):
        super(Clipboard_OSX, self).__init__()
        self.pb = NSPasteboard.generalPasteboard()

    def paste(self):
        item = ClipContentItem()
        img = self._check_image_osx()
        if img is not None:
            write_to_file(img)
            item.cl_type = CL_IMAGE
            item.cl_data = img
        else:
            text = self._check_text_osx()
            item.cl_type = CL_TEXT
            item.cl_data = text
        return item

    def copy(self, item):
        if item.cl_type == CL_TEXT:
            self.pb.declareTypes_owner_(NSArray.arrayWithObject_(NSStringPboardType), None)
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
            return bytes(pngData)


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

#server
class ClipHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        buff_size = 1024
        data = recv_msg(self.request)
        self.request.sendall('OK')
        # data = self.request[0]
        # socket = self.request[1]
        item = pickle.loads(data)
        # print "{} wrote:".format(self.client_address[0])
        if item.cl_type == CL_IMAGE:
            print 'img'
            write_to_file(item.cl_data)
            # show_img(item.cl_data)
        else:
            print item.cl_data
        global LAST_ITEM
        LAST_ITEM = item
        Mypb.copy(item)


class ClipUDPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


def server_start():
    HOST, PORT = "0.0.0.0", CONFIG_PORT
    server = ClipUDPServer((HOST, PORT), ClipHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    # server_thread.daemon = True
    server_thread.start()


def sent_data_to_server(item):
    HOST, PORT = CONFIG_OTHER_HOST, CONFIG_PORT

    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        send_msg(sock, pickle.dumps(item))
        # sock.sendall(pickle.dumps(item))

        # Receive data from the server and shut down
        received = sock.recv(1024)
        print received
    finally:
        sock.close()


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


class ClipMoniter():
    def check(self):
        global LAST_ITEM
        item = Mypb.paste()
        if LAST_ITEM == None or item.cl_type != LAST_ITEM.cl_type or item.cl_data != LAST_ITEM.cl_data:
            LAST_ITEM = item
            sent_data_to_server(item)

    def loop_check(self):
        while True:
            self.check()
            time.sleep(0.2)

    def start(self):
        s = threading.Thread(target=self.loop_check)
        s.start()

CONFIG_PORT = 35000
CONFIG_OTHER_HOST = '192.168.1.51'
LAST_ITEM = None

if __name__ == '__main__':

    server_start()
    mointer = ClipMoniter()
    mointer.start()
    #mointer.check()