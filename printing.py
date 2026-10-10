"""Windows driver settings and shared sheet geometry for preview/printing."""
import ctypes, math
from ctypes import wintypes as w
PAPERS={'A4':(9,210,297),'Letter':(1,215.9,279.4),'A3':(8,297,420),'A5':(11,148,210),'Legal':(5,215.9,355.6)}

class DEVMODE(ctypes.Structure):
    _fields_=[('device',w.WCHAR*32),('spec',w.WORD),('driver',w.WORD),('size',w.WORD),('extra',w.WORD),('fields',w.DWORD),
        ('orientation',ctypes.c_short),('paper',ctypes.c_short),('length',ctypes.c_short),('width',ctypes.c_short),('scale',ctypes.c_short),('copies',ctypes.c_short),('source',ctypes.c_short),('quality',ctypes.c_short),
        ('color',ctypes.c_short),('duplex',ctypes.c_short),('yres',ctypes.c_short),('tt',ctypes.c_short),('collate',ctypes.c_short),('form',w.WCHAR*32),('logpixels',w.WORD),('bits',w.DWORD),('pxwidth',w.DWORD),('pxheight',w.DWORD),('flags',w.DWORD),('freq',w.DWORD),('icm',w.DWORD),('intent',w.DWORD),('media',w.DWORD),('dither',w.DWORD),('reserved1',w.DWORD),('reserved2',w.DWORD),('panwidth',w.DWORD),('panheight',w.DWORD)]

def driver_settings(printer,options=None,owner=0,prompt=False):
    spool=ctypes.WinDLL('winspool.drv',use_last_error=True)
    spool.OpenPrinterW.argtypes=[w.LPWSTR,ctypes.POINTER(w.HANDLE),ctypes.c_void_p]
    spool.ClosePrinter.argtypes=[w.HANDLE]
    spool.DocumentPropertiesW.argtypes=[w.HWND,w.HANDLE,w.LPWSTR,ctypes.c_void_p,ctypes.c_void_p,w.DWORD]
    spool.DocumentPropertiesW.restype=ctypes.c_long
    handle=w.HANDLE()
    if not spool.OpenPrinterW(printer,ctypes.byref(handle),None): raise ctypes.WinError(ctypes.get_last_error())
    try:
        count=spool.DocumentPropertiesW(owner,handle,printer,None,None,0)
        if count<ctypes.sizeof(DEVMODE): raise ValueError('Printer driver returned invalid settings')
        buffer=ctypes.create_string_buffer(count)
        if spool.DocumentPropertiesW(owner,handle,printer,buffer,None,2)!=1: raise ValueError('Cannot read printer settings')
        dm=DEVMODE.from_buffer(buffer)
        if options:
            dm.fields|=1|2|0x800|0x1000
            dm.orientation=options.get('orientation',1); dm.paper=PAPERS[options.get('paper','A4')][0]
            dm.color=1 if options.get('grayscale') else 2
            dm.duplex=options.get('duplex',1)
        result=spool.DocumentPropertiesW(owner,handle,printer,buffer,buffer,10|(4 if prompt else 0))
        if result!=1: return None
        if options and not prompt:
            if dm.orientation!=options.get('orientation',1) or dm.paper!=PAPERS[options.get('paper','A4')][0] or dm.duplex!=options.get('duplex',1):
                raise ValueError('Printer does not support the selected paper/orientation/duplex. Change settings or use driver properties.')
        return buffer
    finally: spool.ClosePrinter(handle)

def sheet_groups(indices,nup=1):
    if nup not in (1,2,4,6,9,16): raise ValueError('Invalid pages per sheet')
    return [indices[i:i+nup] for i in range(0,len(indices),nup)]

def placement(page_size,area,scaling='fit',dpi=72):
    pw,ph=page_size; x,y,w,h=area
    ratio=min(w/pw,h/ph)
    if scaling=='actual': ratio=dpi/72
    elif scaling=='shrink': ratio=min(ratio,dpi/72)
    width,height=pw*ratio,ph*ratio
    return x+(w-width)/2,y+(h-height)/2,width,height

def cells(width,height,nup):
    columns=math.ceil(math.sqrt(nup)); rows=math.ceil(nup/columns)
    return [(c*width/columns,r*height/rows,width/columns,height/rows) for r in range(rows) for c in range(columns)][:nup]
