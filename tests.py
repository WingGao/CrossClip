__author__ = 'wing'
from clip_main import *
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

def test_paste_img():
    cit2 = Mypb.paste()
    print cit2.cl_type, cit2.cl_data
    if cit2.cl_type == CL_TEXT:
        print cit2.cl_data
    else:
        with open('b.png', 'wb') as f:
            f.write(cit2.cl_data)

test_paste_img()