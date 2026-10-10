"""Simple PDF reader — Tk desktop shell."""
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import threading
import queue
from PIL import ImageTk, Image, ImageDraw
import i18n
from i18n import tr
from ui import icon, Tooltip
from core import Document, PasswordRequired, convert_to_pdf
from library import Library, make_bundle, restore_bundle

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Simple PDF reader')
        self.geometry('1280x850')
        self.minsize(900, 600)
        self.configure(bg='#f6f7f9')
        self.doc, self.page, self.scale, self.mode = (None, 0, 1.0, None)
        self.photo = None
        self.view = tk.StringVar(value='连续滚动')
        self.fit_width = False
        self.images = {}
        self.positions = {}
        self.render_job = None
        self.resize_job = None
        self.floating = None
        self.library = Library()
        self.events = queue.Queue()
        self.cloud_busy = False
        self.after(100, self.poll)
        self.after(5000, self.autosave_progress)
        self.build_ui()
        self.bind('<Control-o>', lambda e: self.guard(self.open))
        self.bind('<Control-s>', lambda e: self.guard(self.save))
        self.bind('<Control-z>', lambda e: self.guard(self.undo))
        self.bind('<Control-p>', lambda e: self.guard(self.print_pdf))
        self.bind('<Control-f>', lambda e: self.guard(self.search))
        self.bind('<Right>', lambda e: self.guard(lambda: self.navigate(1)))
        self.bind('<Left>', lambda e: self.guard(lambda: self.navigate(-1)))
        self.protocol('WM_DELETE_WINDOW', self.close)
        if len(sys.argv) > 1:
            self.after(100, lambda: self.guard(lambda: self.open(sys.argv[1])))

    def build_ui(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', padding=(11, 8), background='#ffffff', foreground='#263447', borderwidth=0, font=('Segoe UI', 10))
        style.map('TButton', background=[('active', '#eaf1fb')])
        style.configure('Accent.TButton', background='#df3033', foreground='white')
        style.map('Accent.TButton', background=[('active', '#be2327')])
        style.configure('TFrame', background='#f6f7f9')
        header = tk.Frame(self, bg='#ffffff', height=58)
        header.pack(fill='x')
        tk.Label(header, text=tr('▣'), font=('Segoe UI', 24, 'bold'), fg='#df3033', bg='white').pack(side='left', padx=(22, 8))
        tk.Label(header, text=tr('Simple PDF reader'), font=('Segoe UI', 17, 'bold'), fg='#202631', bg='white').pack(side='left', pady=17)
        tk.Label(header, text=tr('你的私人 PDF 书库  ·  免费 / MIT'), fg='#7b8492', bg='white', font=('Segoe UI', 10)).pack(side='right', padx=24)
        bar = tk.Frame(self, bg='#333840', padx=12, pady=7)
        bar.pack(fill='x')
        self.icon_cache = {}
        for label, key, action, shortcut in [('打开 PDF', 'open', self.open, 'Ctrl+O'), ('保存副本', 'save', self.save, 'Ctrl+S'), ('最近阅读', 'recent', self.recent, ''), ('云端书库', 'cloud', self.cloud_window, ''), ('打印', 'print', self.print_pdf, 'Ctrl+P'), ('查找文字', 'search', self.search, 'Ctrl+F')]:
            self.tool_button(bar, label, key, action, shortcut=shortcut).pack(side='left', padx=3)
        languages = tk.Menubutton(bar, text=tr('English / 中文 / 日本語 ▾'), bg='#333840', fg='white', activebackground='#48515e', activeforeground='white', relief='flat', padx=12)
        languages.pack(side='right')
        menu = tk.Menu(languages, tearoff=False)
        languages.configure(menu=menu)
        for name, code in i18n.LANGUAGES.items():
            menu.add_command(label=name, command=lambda c=code: self.switch_language(c))
        menu.add_separator(); menu.add_command(label=tr('关于'),command=self.about)
        reading = tk.Frame(self, bg='#333840', padx=12, pady=5)
        reading.pack(fill='x')
        for label, key, action in [('上一页', 'previous', lambda: self.navigate(-1)), ('下一页', 'next', lambda: self.navigate(1)), ('缩小', 'minus', lambda: self.zoom(-0.15)), ('放大', 'plus', lambda: self.zoom(0.15)), ('适应宽度', 'fit', self.fit)]:
            self.tool_button(reading, label, key, action).pack(side='left', padx=2)
        self.page_label = tk.StringVar(value=tr('未打开文件'))
        tk.Label(reading, textvariable=self.page_label, bg='#333840', fg='white', font=('Segoe UI', 10)).pack(side='left', padx=14)
        self.layout_button = tk.Menubutton(reading, text=tr(tr(self.view.get()) + ' ▾'), bg='#333840', fg='white', activebackground='#48515e', activeforeground='white', padx=12)
        self.layout_button.pack(side='right')
        modes = tk.Menu(self.layout_button, tearoff=False)
        self.layout_button.configure(menu=modes)
        for label, key in [('单页', 'single'), ('连续滚动', 'continuous'), ('双页', 'double'), ('双页连续', 'doublecontinuous')]:
            picture = self.get_icon(key)
            modes.add_radiobutton(label=tr(label), image=picture, compound='left', variable=self.view, value=label, command=lambda: self.guard(self.change_view))
        Tooltip(self.layout_button, tr('页面显示'))
        body = ttk.Frame(self)
        body.pack(fill='both', expand=True)
        sidebar = tk.Frame(body, bg='#fff', width=190)
        sidebar.pack(side='left', fill='y')
        tk.Label(sidebar, text=tr('页面导航'), font=('Segoe UI', 12, 'bold'), bg='white').pack(pady=15)
        self.pages = tk.Listbox(sidebar, width=22, borderwidth=0, highlightthickness=0, selectbackground='#e0ecff', selectforeground='#1768c5', font=('Segoe UI', 11))
        self.pages.pack(fill='both', expand=True, padx=10, pady=5)
        self.pages.bind('<<ListboxSelect>>', self.select_page)
        tools = tk.Frame(body, bg='#343941', width=200)
        tools.pack(side='right', fill='y')
        tk.Label(tools, text=tr('工具'), bg='#343941', fg='white', font=('Segoe UI', 13, 'bold')).pack(anchor='w', padx=18, pady=16)
        for label, key, action in [('创建 PDF', 'open', self.convert), ('合并文件', 'double', self.merge), ('编辑工具', 'edit', self.edit_toolbar), ('填写和签名', 'edit', self.signature), ('导出 PDF', 'save', self.export_menu), ('组织页面', 'split', self.edit_toolbar), ('注释', 'text', lambda: self.set_mode('comment')), ('区域高亮', 'highlight', lambda: self.set_mode('highlight')), ('扫描和 OCR', 'search', self.ocr), ('保护', 'lock', self.encrypt), ('请求电子签名', 'edit', self.collaboration), ('发送以供注释', 'cloud', self.collaboration), ('更多工具', 'single', self.edit_toolbar), ('关联 PDF', 'single', self.default_app)]:
            self.tool_button(tools, label, key, action, show_text=True).pack(fill='x', padx=8, pady=2)
        center = ttk.Frame(body)
        center.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(center, bg='#555b63', highlightthickness=0)
        ys = ttk.Scrollbar(center, orient='vertical', command=self.scroll)
        xs = ttk.Scrollbar(center, orient='horizontal', command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        ys.pack(side='right', fill='y')
        xs.pack(side='bottom', fill='x')
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<MouseWheel>', self.wheel)
        self.canvas.bind('<Button-3>', lambda e: self.guard(lambda: self.edit_toolbar(e)))
        self.canvas.bind('<Configure>', self.resized)
        self.canvas.create_text(340, 230, text=tr('打开 PDF 开始阅读\n\n支持密码文件、页面编辑与本地转换'), font=('Segoe UI', 18), fill='#56677e', justify='center')
        self.status = tk.StringVar(value='就绪 · 文件不会上传到服务器')
        tk.Label(self, textvariable=self.status, anchor='w', bg='#f6f7f9', fg='#526176', padx=14, pady=8).pack(fill='x')

    def get_icon(self, key):
        if key not in self.icon_cache:
            self.icon_cache[key] = icon(self, key)
        return self.icon_cache[key]

    def tool_button(self, parent, label, key, action, shortcut='', show_text=False):
        button = tk.Button(parent, image=self.get_icon(key), text=tr(tr(label) if show_text else ''), compound='left', anchor='w' if show_text else 'center', bg='#343941', fg='white', activebackground='#505a68', activeforeground='white', borderwidth=0, padx=10, pady=7, font=('Segoe UI', 10), command=lambda: self.guard(action), takefocus=True)
        Tooltip(button, tr(label) + (' (' + shortcut + ')' if shortcut else ''))
        return button

    def switch_language(self, code):
        self.remember()
        self.hide_toolbar()
        i18n.choose(code)
        for widget in list(self.winfo_children()):
            widget.destroy()
        self.build_ui()
        if self.doc:
            self.refresh(jump=True)

    def collaboration(self):
        messagebox.showinfo(tr('高级协作'), tr('本地版不含远程签署、邮件通知或协作服务器。请保存 PDF 后使用自己的邮件或协作服务发送。'), parent=self)

    def about(self):
        directory=Path(getattr(sys,'_MEIPASS',Path(__file__).parent))
        window=tk.Toplevel(self); window.title('Simple PDF reader · 0.3.0 · MIT')
        box=tk.Text(window,width=95,height=28,wrap='word'); box.pack(fill='both',expand=True)
        for name in ['LICENSE','THIRD_PARTY_NOTICES.md']:
            file=directory/name
            if not file.exists(): file=Path(sys.executable).parent/name
            if file.exists(): box.insert('end',file.read_text('utf-8')+'\n\n')
        box.configure(state='disabled')

    def export_menu(self):
        self.require()
        window = tk.Toplevel(self)
        window.title(tr('导出 PDF'))
        ttk.Button(window, text=tr('导出 PNG'), command=lambda: self.guard(self.export)).pack(padx=25, pady=15)

        def text():
            target = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('UTF-8 text', '*.txt')])
            if target:
                Path(target).write_text('\n\n'.join((p.extract_text() or '' for p in self.doc.writer.pages)), encoding='utf-8')
        ttk.Button(window, text=tr('导出文本'), command=lambda: self.guard(text)).pack(padx=25, pady=15)

    def signature(self):
        self.require()
        window = tk.Toplevel(self)
        window.title(tr('填写和签名'))
        ttk.Button(window,text=tr('填写表单'),command=lambda:self.guard(self.fill_form)).pack(pady=5)
        pad = tk.Canvas(window, width=560, height=180, bg='white', cursor='pencil')
        pad.pack(padx=15, pady=15)
        drawing = Image.new('RGBA', (1120, 360), (255, 255, 255, 0))
        pen = ImageDraw.Draw(drawing)
        last = [None]
        used = [False]

        def start(e):
            last[0] = (e.x, e.y)

        def draw(e):
            if last[0]:
                x, y = last[0]
                pad.create_line(x, y, e.x, e.y, fill='#172844', width=3, capstyle='round', smooth=True)
                pen.line((x * 2, y * 2, e.x * 2, e.y * 2), fill='#172844', width=6)
                used[0] = True
            last[0] = (e.x, e.y)
        pad.bind('<Button-1>', start)
        pad.bind('<B1-Motion>', draw)
        pad.bind('<ButtonRelease-1>', lambda e: last.__setitem__(0, None))

        def clear():
            pad.delete('all')
            drawing.paste((255, 255, 255, 0), (0, 0, 1120, 360))
            used[0] = False

        def use(image):
            box = image.getbbox()
            if not box:
                return
            self.signature_image = image.crop(box).copy()
            self.mode = 'signature'
            self.status.set(tr('点击页面放置签名'))
            window.destroy()

        def imported():
            path = filedialog.askopenfilename(filetypes=[('Signature image', '*.png *.jpg *.jpeg')])
            if path:
                with Image.open(path) as image:
                    use(image.convert('RGBA'))
        bar = ttk.Frame(window)
        bar.pack(pady=8)
        for label, action in [('清除', clear), ('图片签名', imported), ('使用签名', lambda: use(drawing) if used[0] else None)]:
            ttk.Button(bar, text=tr(label), command=lambda f=action: self.guard(f)).pack(side='left', padx=5)
        tk.Label(window, text=tr('签名是可视图像，不是证书数字签名。')).pack(padx=15, pady=10)

    def ocr(self):
        self.require()
        import shutil, subprocess, tempfile
        executable = shutil.which('tesseract')
        if not executable:
            candidate = Path('C:/Program Files/Tesseract-OCR/tesseract.exe')
            if candidate.exists():
                executable = str(candidate)
        if not executable:
            raise ValueError(tr('未找到 OCR 引擎。请安装免费 Tesseract 及所需语言包后重试。'))
        languages = simpledialog.askstring(tr('扫描和 OCR'), tr('OCR 语言（例如 eng、chi_sim、jpn 或 eng+chi_sim）：'), initialvalue='eng', parent=self)
        if not languages:
            return
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / 'page.png'
            self.doc.render(self.page, 3).save(image)
            result = subprocess.run([executable, str(image), 'stdout', '-l', languages], capture_output=True, encoding='utf-8', errors='replace', creationflags=134217728)
            if result.returncode:
                raise ValueError(tr(result.stderr[-1200:]))
        window = tk.Toplevel(self)
        window.title(tr('OCR 结果'))
        box = tk.Text(window, width=80, height=25)
        box.pack(fill='both', expand=True)
        box.insert('1.0', result.stdout)

        def save():
            path = filedialog.asksaveasfilename(defaultextension='.txt')
            if path:
                Path(path).write_text(box.get('1.0', 'end-1c'), encoding='utf-8')
        ttk.Button(window, text=tr('保存文本'), command=save).pack(pady=8)

    def fill_form(self):
        self.require()
        fields=self.doc.writer.get_fields() or {}
        supported={name:field for name,field in fields.items() if field.get('/FT') in ('/Tx','/Btn') and not (int(field.get('/Ff',0)) & (1|32768|65536))}
        if not supported: raise ValueError(tr('没有可填写的表单字段。可使用添加文字或签名工具。'))
        window=tk.Toplevel(self); window.title(tr('填写表单'))
        controls={}
        for name,field in supported.items():
            ttk.Label(window,text=name).pack(anchor='w',padx=20,pady=(8,2))
            if field.get('/FT')=='/Btn':
                var=tk.BooleanVar(value=str(field.get('/V','/Off'))!='/Off')
                ttk.Checkbutton(window,text=name,variable=var).pack(anchor='w',padx=20)
                states=field.get('/_States_',[]); on=next((str(v) for v in states if str(v)!='/Off'),'/Yes')
                controls[name]=(var,on)
            else:
                var=tk.StringVar(value=str(field.get('/V',''))); ttk.Entry(window,textvariable=var,width=45).pack(padx=20)
                controls[name]=(var,None)
        def apply():
            values={name:(on if variable.get() else '/Off') if on else variable.get() for name,(variable,on) in controls.items()}
            self.doc.fill_form(values); self.refresh(); window.destroy()
        ttk.Button(window,text=tr('保存'),command=lambda:self.guard(apply)).pack(pady=15)

    def guard(self, function):
        try:
            function()
        except Exception as error:
            messagebox.showerror(tr('操作未完成'), tr(str(error)), parent=self)

    def require(self):
        if not self.doc:
            raise ValueError(tr('请先打开 PDF'))

    def hide_toolbar(self):
        if self.floating and self.floating.winfo_exists():
            self.floating.destroy()
        self.floating = None

    def edit_toolbar(self, event=None):
        self.require()
        self.hide_toolbar()
        if event:
            cx, cy = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
            self.page = next((i for i, (x, y, w, h) in self.positions.items() if x <= cx <= x + w and y <= cy <= y + h), self.page)
        pop = tk.Toplevel(self)
        self.floating = pop
        pop.overrideredirect(True)
        pop.configure(bg='#cdd5df')
        pop.transient(self)
        content = tk.Frame(pop, bg='white', padx=12, pady=12)
        content.pack(padx=1, pady=1)
        top = tk.Frame(content, bg='white')
        top.pack(fill='x')
        tk.Label(top, text=tr('编辑工具  ·  第 {0} 页').format(self.page + 1), font=('Segoe UI', 11, 'bold'), bg='white', fg='#263447').pack(side='left')
        ttk.Button(top, text=tr('×'), width=3, command=self.hide_toolbar).pack(side='right')
        actions = [('添加文字', lambda: self.set_mode('text')), ('区域高亮', lambda: self.set_mode('highlight')), ('旋转页面', lambda: self.mutate('rotate')), ('删除页面', self.delete), ('撤销', self.undo), ('合并文件', self.merge), ('提取页面', self.extract), ('分割 PDF', self.split_pdf), ('填写和签名', self.signature), ('注释', lambda: self.set_mode('comment')), ('加密 PDF', self.encrypt), ('解密另存', self.decrypt), ('导出 PNG', self.export), ('查找文字', self.search)]
        grid = tk.Frame(content, bg='white')
        grid.pack(pady=(10, 0))
        for i, (label, action) in enumerate(actions):

            def activate(f=action):
                self.hide_toolbar()
                self.guard(f)
            key={'添加文字':'text','区域高亮':'highlight','旋转页面':'rotate','删除页面':'delete','撤销':'undo','填写和签名':'edit','注释':'text','加密 PDF':'lock','分割 PDF':'split','查找文字':'search'}.get(label,'single')
            cache='popup-'+key
            if cache not in self.icon_cache: self.icon_cache[cache]=icon(self,key,'#263447')
            button=ttk.Button(grid, text=tr(label),image=self.icon_cache[cache],compound='left',command=activate, width=17)
            button.grid(row=i // 4, column=i % 4, padx=3, pady=3)
            Tooltip(button,tr(label))
        pop.update_idletasks()
        x = event.x_root if event else self.winfo_rootx() + 240
        y = event.y_root if event else self.winfo_rooty() + 165
        x = max(0, min(x, self.winfo_screenwidth() - pop.winfo_reqwidth() - 20))
        y = max(0, min(y, self.winfo_screenheight() - pop.winfo_reqheight() - 50))
        pop.geometry(f'+{x}+{y}')

    def page_range(self, value):
        indices = []
        for token in value.split(','):
            token = token.strip()
            if '-' in token:
                a, b = map(int, token.split('-'))
                if b < a:
                    raise ValueError(tr('范围起始页不能大于结束页'))
                indices.extend(range(a - 1, b))
            else:
                indices.append(int(token) - 1)
        if not indices or any((i < 0 or i >= len(self.doc) for i in indices)):
            raise ValueError(tr('页码超出范围'))
        return indices

    def split_pdf(self):
        self.require()
        window = tk.Toplevel(self)
        window.title(tr('分割 PDF'))
        window.geometry('440x290')
        kind = tk.StringVar(value=tr('每页一个文件'))
        ttk.Combobox(window, textvariable=kind, values=[tr(v) for v in ['每页一个文件', '每 N 页一个文件', '自定义分段']], state='readonly').pack(fill='x', padx=20, pady=18)
        tk.Label(window, text=tr('输入 N 或分段页码，例如 1-3;4-6;7,9\n每页一个文件时无需填写。'), justify='left').pack(anchor='w', padx=20)
        value = tk.StringVar(value='2')
        ttk.Entry(window, textvariable=value).pack(fill='x', padx=20, pady=15)
        tk.Label(window, text=tr('分割输出为未加密 PDF；原文件保留。'), fg='#677589').pack(anchor='w', padx=20)

        def split():
            if kind.get() == tr('每页一个文件'):
                groups = [[i] for i in range(len(self.doc))]
            elif kind.get() == tr('每 N 页一个文件'):
                n = int(value.get())
                if n < 1:
                    raise ValueError(tr('N 至少为 1'))
                groups = [list(range(i, min(i + n, len(self.doc)))) for i in range(0, len(self.doc), n)]
            else:
                groups = [self.page_range(v) for v in value.get().split(';')]
            directory = filedialog.askdirectory(title=tr('选择分割文件保存目录'), parent=window)
            if directory:
                files = self.doc.split(directory, groups)
                self.status.set(tr('已保存 {0} 个分割文件').format(len(files)))
                window.destroy()
        ttk.Button(window, text=tr('选择目录并分割'), style='Accent.TButton', command=lambda: self.guard(split)).pack(pady=15)

    def print_pdf(self):
        from print_ui import show
        show(self)

    def discard(self):
        return not self.doc or not self.doc.dirty or messagebox.askyesno(tr('未保存的修改'), tr('放弃未保存的修改？'), parent=self)

    def open(self, path=None):
        if not self.discard():
            return
        self.remember()
        path = path or filedialog.askopenfilename(filetypes=[('PDF', '*.pdf')])
        if not path:
            return
        password = ''
        while True:
            try:
                document = Document(path, password)
                break
            except PasswordRequired:
                password = simpledialog.askstring(tr('密码文件'), tr('输入 PDF 密码：'), show='*', parent=self)
                if password is None:
                    return
        state = self.library.state(path)
        self.doc, self.page, self.mode = (document, min(state.get('page', 0), len(document) - 1), None)
        self.scale = state.get('zoom', 1.0)
        self.fit_width = not bool(state)
        self.view.set(state.get('view', '连续滚动'))
        self.sizes = self.doc.page_sizes()
        self.refresh(jump=True, offset=state.get('offset', 0))

    def remember(self):
        if self.doc and self.doc.path.exists():
            offset = self.reading_offset()
            self.library.remember(self.doc.path, self.page, self.scale, self.view.get(), offset)

    def autosave_progress(self):
        try:
            self.remember()
        except OSError:
            pass
        self.after(5000, self.autosave_progress)

    def recent(self):
        window = tk.Toplevel(self)
        window.title(tr('最近阅读'))
        box = tk.Listbox(window, width=65, height=16)
        box.pack(fill='both', expand=True, padx=12, pady=12)
        items = [b for b in self.library.books.values() if Path(b['path']).exists()]
        for item in items:
            box.insert('end', tr('{0}  · 第 {1} 页').format(item['name'], item['page'] + 1))

        def resume():
            if box.curselection():
                self.guard(lambda: self.open(items[box.curselection()[0]]['path']))
                window.destroy()
        ttk.Button(window, text=tr('继续阅读'), command=resume).pack(pady=8)

    def poll(self):
        try:
            while True:
                callback, value, error = self.events.get_nowait()
                self.cloud_busy = False
                if error:
                    messagebox.showerror(tr('云盘操作失败'), tr(error), parent=self)
                else:
                    self.guard(lambda: callback(value))
        except queue.Empty:
            pass
        self.after(100, self.poll)

    def background(self, function, callback):
        if self.cloud_busy:
            raise ValueError(tr('云盘操作正在进行，请稍候'))
        self.cloud_busy = True
        self.status.set(tr('云盘操作进行中…'))

        def work():
            try:
                self.events.put((callback, function(), None))
            except Exception as error:
                self.events.put((callback, None, str(error)))
        threading.Thread(target=work, daemon=True).start()

    def cloud_window(self):
        from cloud import Cloud
        window = tk.Toplevel(self)
        window.title(tr('私人云端书库'))
        window.geometry('780x520')
        provider = tk.StringVar(value='Google Drive')
        ttk.Label(window, text=tr('Google Drive')).pack(padx=15, pady=12, anchor='w')
        tk.Label(window, text=tr('在官方网页安全登录，将 PDF 与阅读位置备份到自己的云盘。'), font=('Segoe UI', 11)).pack(anchor='w', padx=15)
        toolbar = ttk.Frame(window)
        toolbar.pack(fill='x', padx=12, pady=12)
        box = tk.Listbox(window, font=('Segoe UI', 11))
        box.pack(fill='both', expand=True, padx=15, pady=8)
        items = []

        def done(value):
            self.status.set(tr('云盘操作完成'))

        def show_books(value):
            if not window.winfo_exists():
                return
            items[:] = value
            box.delete(0, 'end')
            for book in items:
                box.insert('end', book['name'] + '  · ' + book['modified'][:10])
            done(value)

        def login():
            cloud = Cloud(provider.get())

            def authorize_and_list():
                cloud.login()
                return cloud.books()
            self.background(authorize_and_list, show_books)

        def refresh():
            cloud = Cloud(provider.get())
            self.background(cloud.books, show_books)

        def upload():
            self.require()
            if self.doc.dirty:
                raise ValueError(tr('请先另存当前编辑版本，再同步；云端上传的是磁盘上已保存的 PDF'))
            self.remember()
            key, data = make_bundle(self.doc.path, self.page, self.scale, self.view.get(), self.reading_offset())
            name = self.doc.path.name
            cloud = Cloud(provider.get())
            self.background(lambda: cloud.upload(key, name, data), done)

        def download():
            if not box.curselection():
                raise ValueError(tr('请先选择云端书籍'))
            item = items[box.curselection()[0]]
            cloud = Cloud(provider.get())

            def restore(data):
                path, state = restore_bundle(data, self.library.directory / 'downloads')
                self.library.remember(path, state['page'], state['zoom'], state['view'], state['offset'])
                self.open(str(path))
                if window.winfo_exists():
                    window.destroy()
            self.background(lambda: cloud.download(item), restore)

        def logout():
            Cloud(provider.get()).logout()
            box.delete(0, 'end')
            items.clear()
            self.status.set(tr('已清除本机云盘令牌；撤销授权可到云盘账户设置完成'))
        for label, function in [('网页登录', login), ('刷新书库', refresh), ('上传当前书籍与进度', upload), ('继续阅读', download), ('退出登录', logout)]:
            ttk.Button(toolbar, text=tr(label), command=lambda f=function: self.guard(f)).pack(side='left', padx=2)
        provider.trace_add('write', lambda *args: (box.delete(0, 'end'), items.clear()))
        tk.Label(window, text=tr('同步为手动一键上传；多设备以最后一次上传的进度为准。加密 PDF 保持原文件加密。'), fg='#526176').pack(pady=8)

    def reading_offset(self):
        position = self.positions.get(self.page)
        if not position:
            return 0
        x, y, w, h = position
        return max(0, min(1, (self.canvas.canvasy(0) - y) / h))

    def refresh(self, jump=False, offset=0):
        self.require()
        self.hide_toolbar()
        previous_offset = self.reading_offset() if not jump else offset
        self.page = min(self.page, len(self.doc) - 1)
        self.pages.delete(0, 'end')
        for i in range(len(self.doc)):
            self.pages.insert('end', tr('  第 {0} 页').format(i + 1))
        self.pages.selection_set(self.page)
        self.pages.see(self.page)
        self.sizes = self.doc.page_sizes()
        double = self.view.get() in {'双页', '双页连续'}
        continuous = self.view.get() in {'连续滚动', '双页连续'}
        if self.fit_width:
            max_width = max((w for w, h in self.sizes))
            self.scale = max(0.3, min(2.5, (self.canvas.winfo_width() - 80) / (max_width * (2 if double else 1))))
        indices = list(range(len(self.doc))) if continuous else [self.page // 2 * 2, min(self.page // 2 * 2 + 1, len(self.doc) - 1)] if double else [self.page]
        indices = list(dict.fromkeys(indices))
        self.canvas.delete('all')
        self.images.clear()
        self.positions.clear()
        gap, y = (24, 28)
        columns = 2 if double else 1
        max_row_width = max((sum((self.sizes[i][0] * self.scale for i in indices[j:j + columns])) + gap * (len(indices[j:j + columns]) - 1) for j in range(0, len(indices), columns)))
        available_width = max(self.canvas.winfo_width(), max_row_width + 56)
        for j in range(0, len(indices), columns):
            row = indices[j:j + columns]
            row_width = sum((self.sizes[i][0] * self.scale for i in row)) + gap * (len(row) - 1)
            x = max(28, (available_width - row_width) / 2)
            row_height = 0
            for i in row:
                w, h = (self.sizes[i][0] * self.scale, self.sizes[i][1] * self.scale)
                self.positions[i] = (x, y, w, h)
                self.canvas.create_rectangle(x + 4, y + 5, x + w + 4, y + h + 5, fill='#bac1ca', outline='', tags=f'page-{i}')
                self.canvas.create_rectangle(x, y, x + w, y + h, fill='white', outline='#c8ced6', tags=f'page-{i}')
                self.canvas.create_text(x + w / 2, y + h / 2, text=tr('第 {0} 页').format(i + 1), fill='#8692a3', tags=f'placeholder-{i}')
                x += w + gap
                row_height = max(row_height, h)
            y += row_height + gap
        self.content_height = y + 12
        self.canvas.configure(scrollregion=(0, 0, available_width, self.content_height))
        target = self.positions.get(self.page)
        if target:
            self.canvas.yview_moveto(max(0, (target[1] + previous_offset * target[3] - 16) / self.content_height))
        self.render_visible()
        self.title(f"{self.doc.path.name}{(' *' if self.doc.dirty else '')} — Simple PDF reader")
        self.page_label.set(tr('{0} / {1} 页  ·  {2:.0%}').format(self.page + 1, len(self.doc), self.scale))
        self.status.set(tr('{0}  ·  {1}  ·  {2}').format(self.doc.path.name, tr(self.view.get()), tr('有未保存修改') if self.doc.dirty else tr('阅读进度自动保存')))

    def render_visible(self):
        self.render_job = None
        if not self.doc:
            return
        top = self.canvas.canvasy(0)
        bottom = top + self.canvas.winfo_height()
        visible = [i for i, (x, y, w, h) in self.positions.items() if y + h >= top - 100 and y <= bottom + 100]
        for i in list(self.images):
            if i not in visible:
                self.canvas.delete(f'image-{i}')
                del self.images[i]
        for i in visible:
            if i not in self.images:
                photo = ImageTk.PhotoImage(self.doc.render(i, self.scale))
                self.images[i] = photo
                x, y, w, h = self.positions[i]
                self.canvas.create_image(x, y, image=photo, anchor='nw', tags=f'image-{i}')
                self.canvas.delete(f'placeholder-{i}')
        current = [i for i in visible if self.positions[i][1] + self.positions[i][3] > top + 30]
        if current:
            new_page = current[0]
            if self.view.get() in {'双页', '双页连续'} and self.page in current and (self.positions[self.page][1] == self.positions[new_page][1]):
                new_page = self.page
            self.page = new_page
            self.pages.selection_clear(0, 'end')
            self.pages.selection_set(self.page)
            self.page_label.set(tr('{0} / {1} 页  ·  {2:.0%}').format(self.page + 1, len(self.doc), self.scale))

    def scroll(self, *args):
        self.canvas.yview(*args)
        self.schedule_render()

    def wheel(self, event):
        if event.state & 4:
            self.zoom(0.1 if event.delta > 0 else -0.1)
        else:
            self.scroll('scroll', -int(event.delta / 120) * 3, 'units')

    def schedule_render(self):
        self.hide_toolbar()
        if self.render_job:
            self.after_cancel(self.render_job)
        self.render_job = self.after(40, lambda: self.guard(self.render_visible))

    def resized(self, event):
        if not self.doc:
            return
        if self.resize_job:
            self.after_cancel(self.resize_job)
        self.resize_job = self.after(150, lambda: self.guard(self.refresh))

    def navigate(self, delta):
        self.require()
        step = 2 if self.view.get() == '双页' else 1
        self.jump_to(max(0, min(len(self.doc) - 1, self.page + delta * step)))

    def jump_to(self, index):
        self.page = index
        if self.view.get() in {'连续滚动', '双页连续'}:
            y = self.positions[index][1]
            self.canvas.yview_moveto(max(0, (y - 16) / self.content_height))
            self.render_visible()
        else:
            self.refresh(jump=True)

    def fit(self):
        self.require()
        self.fit_width = True
        self.refresh()

    def change_view(self):
        self.layout_button.configure(text=tr(tr(self.view.get()) + ' ▾'))
        self.fit_width = True
        if self.doc:
            self.refresh(jump=True)

    def select_page(self, event=None):
        selected = self.pages.curselection()
        if selected and selected[0] != self.page:
            self.guard(lambda: self.jump_to(selected[0]))

    def zoom(self, delta):
        self.fit_width = False
        self.scale = max(0.3, min(2.5, self.scale + delta))
        if self.doc:
            self.guard(self.refresh)

    def destination(self):
        self.require()
        return filedialog.asksaveasfilename(defaultextension='.pdf', initialfile=self.doc.path.stem + '-edited.pdf', filetypes=[('PDF', '*.pdf')])

    def save(self):
        path = self.destination()
        if path:
            self.doc.save(path)
            self.doc.path = Path(path)
            self.refresh()
            self.status.set(tr('已保存（未加密）；需要密码保护请使用“加密 PDF”'))

    def mutate(self, action):
        self.require()
        getattr(self.doc, action)(self.page)
        self.refresh()

    def undo(self):
        self.require()
        self.doc.undo()
        self.refresh()

    def delete(self):
        self.require()
        if messagebox.askyesno(tr('删除页面'), tr('删除第 {0} 页？').format(self.page + 1)):
            self.mutate('delete')

    def merge(self):
        self.require()
        path = filedialog.askopenfilename(filetypes=[('PDF', '*.pdf')])
        if not path:
            return
        password = ''
        while True:
            try:
                self.doc.append(path, password)
                break
            except PasswordRequired:
                password = simpledialog.askstring(tr('密码文件'), tr('输入待合并 PDF 的密码：'), show='*', parent=self)
                if password is None:
                    return
        self.refresh()

    def extract(self):
        self.require()
        value = simpledialog.askstring(tr('提取页面'), tr('页码（例如 1,3,5），按输入顺序导出：'))
        if not value:
            return
        indices = [int(v.strip()) - 1 for v in value.split(',')]
        if any((i < 0 or i >= len(self.doc) for i in indices)):
            raise ValueError(tr('页码超出范围'))
        path = self.destination()
        if path:
            self.doc.save(path, indices=indices)

    def encrypt(self):
        self.require()
        password = simpledialog.askstring(tr('AES-256 加密'), tr('新密码：'), show='*', parent=self)
        if not password:
            return
        confirm = simpledialog.askstring(tr('确认密码'), tr('再次输入新密码：'), show='*', parent=self)
        if confirm != password:
            raise ValueError(tr('两次密码不一致'))
        path = self.destination()
        if path:
            self.doc.save(path, password=password)
            self.refresh()
            self.status.set(tr('已导出 AES-256 加密 PDF'))

    def decrypt(self):
        self.save()

    def set_mode(self, mode):
        self.require()
        self.hide_toolbar()
        self.mode = mode
        self.status.set(tr(tr('点击页面放置文字') if mode == 'text' else tr('点击页面放置注释') if mode == 'comment' else tr('依次点击高亮区域的两个角')))
        self.corner = None

    def click(self, event):
        self.guard(lambda: self.place(event))

    def place(self, event):
        if not self.doc or not self.mode:
            return
        cx, cy = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        hit = next((i for i, (px, py, pw, ph) in self.positions.items() if px <= cx <= px + pw and py <= cy <= py + ph), None)
        if hit is None:
            return
        self.page = hit
        page = self.doc.writer.pages[self.page]
        if page.rotation or float(page.cropbox.left) != 0 or float(page.cropbox.bottom) != 0 or (page.cropbox != page.mediabox):
            raise ValueError(tr('此页有旋转或裁剪偏移，请先另存并规范页面后再添加标记；页面管理仍可使用'))
        px, py, pw, ph = self.positions[self.page]
        x = (cx - px) / self.scale
        y = float(page.mediabox.height) - (cy - py) / self.scale
        if not (0 <= x <= float(page.mediabox.width) and 0 <= y <= float(page.mediabox.height)):
            return
        if self.mode == 'signature':
            width = min(180, float(page.mediabox.width) - x)
            height = width * self.signature_image.height / self.signature_image.width
            self.doc.add_image(self.page, self.signature_image, x, max(0, y - height), width, height)
            self.mode = None
            self.refresh()
        elif self.mode == 'comment':
            text = simpledialog.askstring(tr('注释'), tr('注释内容：'), parent=self)
            if text:
                self.doc.comment(self.page, text, x, y)
                self.refresh()
            self.mode = None
        elif self.mode == 'text':
            text = simpledialog.askstring(tr('添加文字'), tr('文字（支持中文）：'), parent=self)
            if text:
                self.doc.add_text(self.page, text, x, y,font='HeiseiMin-W3' if i18n.language=='ja' else 'STSong-Light')
                self.refresh()
            self.mode = None
        elif self.corner is None:
            self.corner = (self.page, x, y)
            self.status.set(tr('再点击另一角完成高亮'))
        else:
            index, x0, y0 = self.corner
            if index != self.page:
                raise ValueError(tr('高亮的两个角必须在同一页'))
            if abs(x - x0) < 1 or abs(y - y0) < 1:
                return
            self.doc.highlight(self.page, (min(x, x0), min(y, y0), max(x, x0), max(y, y0)))
            self.mode = None
            self.refresh()

    def export(self):
        self.require()
        path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG', '*.png')])
        if path:
            self.doc.render(self.page, 2).save(path)

    def search(self):
        self.require()
        text = simpledialog.askstring(tr('查找文字'), tr('查找：'))
        if not text:
            return
        hits = [str(i + 1) for i, p in enumerate(self.doc.writer.pages) if text.casefold() in (p.extract_text() or '').casefold()]
        messagebox.showinfo(tr('查找结果'), tr('匹配页：' + ', '.join(hits) if hits else '未找到文字；扫描 PDF 需要 OCR，本版本不含 OCR。'))

    def convert(self):
        source = filedialog.askopenfilename(title=tr('选择图片、文本或 Office 文件'))
        if not source:
            return
        target = filedialog.asksaveasfilename(defaultextension='.pdf', initialfile=Path(source).stem + '.pdf', filetypes=[('PDF', '*.pdf')])
        if not target:
            return
        if Path(source).resolve() == Path(target).resolve():
            raise ValueError(tr('输出不能覆盖输入文件'))
        self.status.set(tr('正在转换…'))
        self.update_idletasks()
        convert_to_pdf(source, target)
        self.open(target)

    def default_app(self):
        if sys.platform == 'win32':
            from windows import register_pdf
            result = register_pdf()
            if result:
                messagebox.showinfo(tr('PDF 文件关联'), tr('已在程序内注册 PDF 文件关联。可以从文件管理器打开 PDF。'))
            else:
                messagebox.showinfo(tr('PDF 文件关联'), tr('已注册 Simple PDF reader 为 PDF 打开方式。\nWindows 当前已有默认 PDF 应用，首次切换仍需系统确认：右键 PDF → 打开方式 → 选择其他应用 → 始终使用。'))
        else:
            messagebox.showinfo(tr('文件关联'), tr('在系统文件管理器中选择 PDF → 打开方式 → Simple PDF reader。'))

    def close(self):
        if self.discard():
            self.guard(self.remember)
            self.destroy()
if __name__ == '__main__':
    App().mainloop()
