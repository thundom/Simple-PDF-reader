"""Windows shell registration and GDI printing without paid SDKs."""
import ctypes
from ctypes import wintypes as w
from pathlib import Path
import sys


def register_pdf():
    if sys.platform!='win32': raise ValueError('文件关联目前仅支持 Windows')
    import winreg
    if getattr(sys,'frozen',False):
        command = f'"{sys.executable}" "%1"'
    else:
        python = Path(sys.executable).with_name('pythonw.exe')
        command = f'"{python if python.exists() else sys.executable}" "{Path(__file__).with_name("app.py")}" "%1"'
    def set_value(path,name,value):
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,path) as key:
            winreg.SetValueEx(key,name,0,winreg.REG_SZ,value)
    prefix = r'Software\Classes\SimplePDFreader.Document'
    set_value(prefix,'','PDF Document — Simple PDF reader')
    set_value(prefix+r'\shell\open\command','',command)
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER,r'Software\Classes\.pdf\OpenWithProgids') as key:
        winreg.SetValueEx(key,'SimplePDFreader.Document',0,winreg.REG_NONE,b'')
    caps = r'Software\Simple PDF reader\Capabilities'
    set_value(caps,'ApplicationName','Simple PDF reader')
    set_value(caps,'ApplicationDescription','Free local PDF reader and editor')
    set_value(caps+r'\FileAssociations','.pdf','SimplePDFreader.Document')
    set_value(r'Software\RegisteredApplications','Simple PDF reader',caps)
    has_choice = False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.pdf\UserChoice') as key:
            has_choice = winreg.QueryValueEx(key,'ProgId')[0] != 'SimplePDFreader.Document'
    except FileNotFoundError: pass
    if not has_choice: set_value(r'Software\Classes\.pdf','','SimplePDFreader.Document')
    ctypes.windll.shell32.SHChangeNotify(0x08000000,0,None,None)
    return not has_choice


def printers():
    if sys.platform!='win32': raise ValueError('打印目前仅支持 Windows')
    class PRINTER_INFO_4(ctypes.Structure):
        _fields_ = [('name',w.LPWSTR),('server',w.LPWSTR),('attributes',w.DWORD)]
    spool = ctypes.WinDLL('winspool.drv',use_last_error=True)
    needed,returned = w.DWORD(),w.DWORD()
    spool.EnumPrintersW(6,None,4,None,0,ctypes.byref(needed),ctypes.byref(returned))
    if not needed.value: return []
    buffer = ctypes.create_string_buffer(needed.value)
    if not spool.EnumPrintersW(6,None,4,buffer,needed,ctypes.byref(needed),ctypes.byref(returned)):
        raise ctypes.WinError(ctypes.get_last_error())
    rows = ctypes.cast(buffer,ctypes.POINTER(PRINTER_INFO_4))
    return [rows[i].name for i in range(returned.value)]


def print_document(document, printer, indices, copies=1, progress=None,options=None,driver=None,cancelled=None):
    if sys.platform!='win32': raise ValueError('打印目前仅支持 Windows')
    from printing import driver_settings,sheet_groups,cells,placement
    options=options or {}
    driver=driver or driver_settings(printer,options)
    gdi = ctypes.WinDLL('gdi32',use_last_error=True)
    gdi.CreateDCW.argtypes = [w.LPCWSTR,w.LPCWSTR,w.LPCWSTR,ctypes.c_void_p]
    gdi.CreateDCW.restype = ctypes.c_void_p
    for name in ['StartPage','EndPage','EndDoc','AbortDoc','DeleteDC']:
        getattr(gdi,name).argtypes = [ctypes.c_void_p]
        getattr(gdi,name).restype = ctypes.c_int
    gdi.GetDeviceCaps.argtypes = [ctypes.c_void_p,ctypes.c_int]
    gdi.SetStretchBltMode.argtypes = [ctypes.c_void_p,ctypes.c_int]
    gdi.SaveDC.argtypes=[ctypes.c_void_p]
    gdi.RestoreDC.argtypes=[ctypes.c_void_p,ctypes.c_int]
    gdi.IntersectClipRect.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int]
    gdi.StretchDIBits.argtypes = [ctypes.c_void_p,*([ctypes.c_int]*8),ctypes.c_void_p,ctypes.c_void_p,w.UINT,w.DWORD]
    gdi.StretchDIBits.restype = ctypes.c_int
    class DOCINFO(ctypes.Structure):
        _fields_ = [('size',ctypes.c_int),('name',w.LPCWSTR),('output',w.LPCWSTR),('datatype',w.LPCWSTR),('type',w.DWORD)]
    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [('size',w.DWORD),('width',w.LONG),('height',w.LONG),('planes',w.WORD),('bits',w.WORD),
                   ('compression',w.DWORD),('image_size',w.DWORD),('xppm',w.LONG),('yppm',w.LONG),('used',w.DWORD),('important',w.DWORD)]
    gdi.StartDocW.argtypes = [ctypes.c_void_p,ctypes.POINTER(DOCINFO)]
    dc = gdi.CreateDCW('WINSPOOL',printer,None,driver)
    if not dc: raise ValueError('无法连接打印机')
    started = False
    try:
        info = DOCINFO(ctypes.sizeof(DOCINFO),document.path.name,None,None,0)
        if gdi.StartDocW(dc,ctypes.byref(info))<=0: raise ValueError('打印任务未启动或已取消')
        started = True
        width,height = gdi.GetDeviceCaps(dc,8),gdi.GetDeviceCaps(dc,10)
        gdi.SetStretchBltMode(dc,4)
        dpi=gdi.GetDeviceCaps(dc,88)
        for copy in range(copies):
            for group in sheet_groups(indices,options.get('nup',1)):
                if cancelled and cancelled(): raise ValueError('Print job cancelled')
                if gdi.StartPage(dc)<=0: raise ValueError('打印机无法开始新页')
                for index,area in zip(group,cells(width,height,options.get('nup',1))):
                    if progress: progress(index,copy)
                    if cancelled and cancelled(): raise ValueError('Print job cancelled')
                    render_scale=options.get('dpi',300)/72
                    image=document.render(index,render_scale)
                    if options.get('grayscale'): image=image.convert('L')
                    image=image.convert('RGB')
                    iw,ih=image.size
                    stride=((iw*3+3)//4)*4
                    pixels=ctypes.create_string_buffer(image.tobytes('raw','BGR',stride,1))
                    header=BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER),iw,-ih,1,24,0,stride*ih,0,0,0,0)
                    x,y,dw,dh=placement((iw/render_scale,ih/render_scale),area,options.get('scaling','fit'),dpi)
                    saved=gdi.SaveDC(dc)
                    ax,ay,aw,ah=area
                    gdi.IntersectClipRect(dc,int(ax),int(ay),int(ax+aw),int(ay+ah))
                    result=gdi.StretchDIBits(dc,int(x),int(y),int(dw),int(dh),0,0,iw,ih,pixels,ctypes.byref(header),0,0x00CC0020)
                    gdi.RestoreDC(dc,saved)
                    if result in (0,-1): raise ValueError('打印页面失败')
                if gdi.EndPage(dc)<=0: raise ValueError('打印页面失败')
        if gdi.EndDoc(dc)<=0: raise ValueError('打印任务提交失败')
        started = False
    finally:
        if started: gdi.AbortDoc(dc)
        gdi.DeleteDC(dc)
