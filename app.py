"""Simple PDF reader — Tk desktop shell."""
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import threading
import queue
from PIL import ImageTk
from core import Document, PasswordRequired, convert_to_pdf
from library import Library, make_bundle, restore_bundle


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Simple PDF reader')
        self.geometry('1280x850')
        self.minsize(900, 600)
        self.configure(bg='#f6f7f9')
        self.doc, self.page, self.scale, self.mode = None, 0, 1.0, None
        self.photo = None
        self.library = Library()
        self.events = queue.Queue()
        self.cloud_busy = False
        self.after(100,self.poll)
        self.after(5000,self.autosave_progress)
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', padding=(10, 8), background='#ffffff', foreground='#263447')
        style.configure('TFrame', background='#f6f7f9')
        header = tk.Frame(self, bg='#172333', height=58)
        header.pack(fill='x')
        tk.Label(header, text='▣  Simple PDF reader', font=('Segoe UI',18,'bold'), fg='white', bg='#172333').pack(side='left', padx=22, pady=15)
        tk.Label(header, text='免费 · 本地 · MIT', fg='#b8c7d9', bg='#172333').pack(side='right', padx=24)
        bar = ttk.Frame(self)
        bar.pack(fill='x', padx=12, pady=10)
        for label, action in [('打开 PDF',self.open),('最近阅读',self.recent),('另存为',self.save),('撤销',self.undo),('转换为 PDF',self.convert),('云端书库',self.cloud_window),('默认 PDF 应用',self.default_app)]:
            ttk.Button(bar,text=label,command=lambda f=action:self.guard(f)).pack(side='left',padx=3)
        ttk.Button(bar,text='−',command=lambda:self.zoom(-.2)).pack(side='right')
        ttk.Button(bar,text='+',command=lambda:self.zoom(.2)).pack(side='right')
        body = ttk.Frame(self)
        body.pack(fill='both',expand=True)
        sidebar = tk.Frame(body,bg='#fff',width=190)
        sidebar.pack(side='left',fill='y')
        tk.Label(sidebar,text='页面导航',font=('Segoe UI',12,'bold'),bg='white').pack(pady=15)
        self.pages = tk.Listbox(sidebar,width=22,borderwidth=0,highlightthickness=0,selectbackground='#e0ecff',selectforeground='#1768c5',font=('Segoe UI',11))
        self.pages.pack(fill='both',expand=True,padx=10,pady=5)
        self.pages.bind('<<ListboxSelect>>',self.select_page)
        right = tk.Frame(body,bg='white',width=190)
        right.pack(side='right',fill='y')
        tk.Label(right,text='所有工具',font=('Segoe UI',12,'bold'),bg='white').pack(pady=15)
        for label, action in [('旋转页面',lambda:self.mutate('rotate')),('删除页面',self.delete),('合并 PDF',self.merge),('提取页面',self.extract),('添加文字',lambda:self.set_mode('text')),('高亮区域',lambda:self.set_mode('highlight')),('加密 PDF',self.encrypt),('解密另存',self.decrypt),('导出页面 PNG',self.export),('查找文字',self.search)]:
            ttk.Button(right,text=label,command=lambda f=action:self.guard(f)).pack(fill='x',padx=12,pady=4)
        center = ttk.Frame(body)
        center.pack(fill='both',expand=True)
        self.canvas = tk.Canvas(center,bg='#e5e8ed',highlightthickness=0)
        ys = ttk.Scrollbar(center,orient='vertical',command=self.canvas.yview)
        xs = ttk.Scrollbar(center,orient='horizontal',command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=ys.set,xscrollcommand=xs.set)
        ys.pack(side='right',fill='y')
        xs.pack(side='bottom',fill='x')
        self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<Button-1>',self.click)
        self.canvas.bind('<MouseWheel>',lambda e:self.canvas.yview_scroll(-int(e.delta/120),'units'))
        self.canvas.create_text(340,230,text='打开 PDF 开始阅读\n\n支持密码文件、页面编辑与本地转换',font=('Segoe UI',18),fill='#56677e',justify='center')
        self.status = tk.StringVar(value='就绪 · 文件不会上传到服务器')
        tk.Label(self,textvariable=self.status,anchor='w',bg='#f6f7f9',fg='#526176',padx=14,pady=8).pack(fill='x')
        self.bind('<Control-o>',lambda e:self.guard(self.open))
        self.bind('<Control-s>',lambda e:self.guard(self.save))
        self.bind('<Control-z>',lambda e:self.guard(self.undo))
        self.protocol('WM_DELETE_WINDOW',self.close)
        if len(sys.argv)>1:
            self.after(100,lambda:self.guard(lambda:self.open(sys.argv[1])))

    def guard(self, function):
        try:
            function()
        except Exception as error:
            messagebox.showerror('操作未完成',str(error),parent=self)

    def require(self):
        if not self.doc:
            raise ValueError('请先打开 PDF')

    def discard(self):
        return not self.doc or not self.doc.dirty or messagebox.askyesno('未保存的修改','放弃未保存的修改？',parent=self)

    def open(self,path=None):
        if not self.discard(): return
        self.remember()
        path = path or filedialog.askopenfilename(filetypes=[('PDF','*.pdf')])
        if not path: return
        password = ''
        while True:
            try:
                document = Document(path,password)
                break
            except PasswordRequired:
                password = simpledialog.askstring('密码文件','输入 PDF 密码：',show='*',parent=self)
                if password is None: return
        state = self.library.state(path)
        self.doc,self.page,self.mode = document,min(state.get('page',0),len(document)-1),None
        self.scale = state.get('zoom',1.0)
        self.refresh()

    def remember(self):
        if self.doc and self.doc.path.exists():
            self.library.remember(self.doc.path,self.page,self.scale)

    def autosave_progress(self):
        try: self.remember()
        except OSError: pass
        self.after(5000,self.autosave_progress)

    def recent(self):
        window = tk.Toplevel(self)
        window.title('最近阅读')
        box = tk.Listbox(window,width=65,height=16)
        box.pack(fill='both',expand=True,padx=12,pady=12)
        items = [b for b in self.library.books.values() if Path(b['path']).exists()]
        for item in items: box.insert('end',f'{item["name"]}  · 第 {item["page"]+1} 页')
        def resume():
            if box.curselection():
                self.guard(lambda:self.open(items[box.curselection()[0]]['path']))
                window.destroy()
        ttk.Button(window,text='继续阅读',command=resume).pack(pady=8)

    def poll(self):
        try:
            while True:
                callback,value,error = self.events.get_nowait()
                self.cloud_busy = False
                if error: messagebox.showerror('云盘操作失败',error,parent=self)
                else: self.guard(lambda:callback(value))
        except queue.Empty: pass
        self.after(100,self.poll)

    def background(self,function,callback):
        if self.cloud_busy: raise ValueError('云盘操作正在进行，请稍候')
        self.cloud_busy = True
        self.status.set('云盘操作进行中…')
        def work():
            try: self.events.put((callback,function(),None))
            except Exception as error: self.events.put((callback,None,str(error)))
        threading.Thread(target=work,daemon=True).start()

    def cloud_window(self):
        from cloud import Cloud
        window = tk.Toplevel(self)
        window.title('私人云端书库')
        window.geometry('780x520')
        provider = tk.StringVar(value='Google Drive')
        ttk.Combobox(window,textvariable=provider,values=['Google Drive','OneDrive'],state='readonly').pack(padx=15,pady=12,anchor='w')
        tk.Label(window,text='PDF 与页码、缩放一起备份到你自己的云盘。第一次使用请配置 OAuth 应用。').pack(anchor='w',padx=15)
        toolbar = ttk.Frame(window)
        toolbar.pack(fill='x',padx=12,pady=12)
        box = tk.Listbox(window,font=('Segoe UI',11))
        box.pack(fill='both',expand=True,padx=15,pady=8)
        items = []
        def done(value): self.status.set('云盘操作完成')
        def show_books(value):
            if not window.winfo_exists(): return
            items[:] = value
            box.delete(0,'end')
            for book in items: box.insert('end',book['name']+'  · '+book['modified'][:10])
            done(value)
        def configure():
            cloud = Cloud(provider.get())
            client = simpledialog.askstring('OAuth 配置','OAuth Client ID（详见 CLOUD_SETUP.md）：',initialvalue=cloud.client.get('client_id',''),parent=window)
            if not client: return
            secret = ''
            if provider.get()=='Google Drive':
                secret = simpledialog.askstring('Google 桌面客户端','Client secret（存入系统凭据库）：',show='*',parent=window)
                if not secret: return
            cloud.configure(client,secret)
            messagebox.showinfo('配置完成','点击登录，在官方网页授权。',parent=window)
        def login():
            cloud = Cloud(provider.get())
            def authorize_and_list():
                cloud.login()
                return cloud.books()
            self.background(authorize_and_list,show_books)
        def refresh():
            cloud = Cloud(provider.get())
            self.background(cloud.books,show_books)
        def upload():
            self.require()
            if self.doc.dirty:
                raise ValueError('请先另存当前编辑版本，再同步；云端上传的是磁盘上已保存的 PDF')
            self.remember()
            key,data = make_bundle(self.doc.path,self.page,self.scale)
            name = self.doc.path.name
            cloud = Cloud(provider.get())
            self.background(lambda:cloud.upload(key,name,data),done)
        def download():
            if not box.curselection(): raise ValueError('请先选择云端书籍')
            item = items[box.curselection()[0]]
            cloud = Cloud(provider.get())
            def restore(data):
                path,state = restore_bundle(data,self.library.directory/'downloads')
                self.library.remember(path,state['page'],state['zoom'])
                self.open(str(path))
                if window.winfo_exists(): window.destroy()
            self.background(lambda:cloud.download(item),restore)
        def logout():
            Cloud(provider.get()).logout()
            box.delete(0,'end')
            items.clear()
            self.status.set('已清除本机云盘令牌；撤销授权可到云盘账户设置完成')
        for label,function in [('配置',configure),('登录',login),('刷新书库',refresh),('上传当前书籍与进度',upload),('继续阅读',download),('退出登录',logout)]:
            ttk.Button(toolbar,text=label,command=lambda f=function:self.guard(f)).pack(side='left',padx=2)
        provider.trace_add('write',lambda *args:(box.delete(0,'end'),items.clear()))
        tk.Label(window,text='同步为手动一键上传；多设备以最后一次上传的进度为准。加密 PDF 保持原文件加密。',fg='#526176').pack(pady=8)

    def refresh(self):
        self.require()
        self.page = min(self.page,len(self.doc)-1)
        self.pages.delete(0,'end')
        for i in range(len(self.doc)): self.pages.insert('end',f'  第 {i+1} 页')
        self.pages.selection_set(self.page)
        self.pages.see(self.page)
        self.photo = ImageTk.PhotoImage(self.doc.render(self.page,self.scale))
        self.canvas.delete('all')
        self.canvas.create_image(24,24,image=self.photo,anchor='nw')
        self.canvas.configure(scrollregion=(0,0,self.photo.width()+48,self.photo.height()+48))
        self.title(f'{self.doc.path.name}{" *" if self.doc.dirty else ""} — Simple PDF reader')
        self.status.set(f'第 {self.page+1} / {len(self.doc)} 页 · {self.scale:.0%} · {"有未保存修改" if self.doc.dirty else "就绪"}')

    def select_page(self,event=None):
        selected = self.pages.curselection()
        if selected and selected[0] != self.page:
            self.page = selected[0]
            self.guard(self.refresh)

    def zoom(self,delta):
        self.scale = max(.3,min(2.5,self.scale+delta))
        if self.doc: self.guard(self.refresh)

    def destination(self):
        self.require()
        return filedialog.asksaveasfilename(defaultextension='.pdf',initialfile=self.doc.path.stem+'-edited.pdf',filetypes=[('PDF','*.pdf')])

    def save(self):
        path = self.destination()
        if path:
            self.doc.save(path)
            self.doc.path = Path(path)
            self.refresh()
            self.status.set('已保存（未加密）；需要密码保护请使用“加密 PDF”')

    def mutate(self,action):
        self.require()
        getattr(self.doc,action)(self.page)
        self.refresh()

    def undo(self):
        self.require()
        self.doc.undo()
        self.refresh()

    def delete(self):
        self.require()
        if messagebox.askyesno('删除页面',f'删除第 {self.page+1} 页？'):
            self.mutate('delete')

    def merge(self):
        self.require()
        path = filedialog.askopenfilename(filetypes=[('PDF','*.pdf')])
        if not path: return
        password = ''
        while True:
            try:
                self.doc.append(path,password)
                break
            except PasswordRequired:
                password = simpledialog.askstring('密码文件','输入待合并 PDF 的密码：',show='*',parent=self)
                if password is None: return
        self.refresh()

    def extract(self):
        self.require()
        value = simpledialog.askstring('提取页面','页码（例如 1,3,5），按输入顺序导出：')
        if not value: return
        indices = [int(v.strip())-1 for v in value.split(',')]
        if any(i<0 or i>=len(self.doc) for i in indices): raise ValueError('页码超出范围')
        path = self.destination()
        if path: self.doc.save(path,indices=indices)

    def encrypt(self):
        self.require()
        password = simpledialog.askstring('AES-256 加密','新密码：',show='*',parent=self)
        if not password: return
        confirm = simpledialog.askstring('确认密码','再次输入新密码：',show='*',parent=self)
        if confirm != password: raise ValueError('两次密码不一致')
        path = self.destination()
        if path:
            self.doc.save(path,password=password)
            self.refresh()
            self.status.set('已导出 AES-256 加密 PDF')

    def decrypt(self):
        self.save()

    def set_mode(self,mode):
        self.require()
        self.mode = mode
        self.status.set('点击页面放置文字' if mode=='text' else '依次点击高亮区域的两个角')
        self.corner = None

    def click(self,event):
        self.guard(lambda:self.place(event))

    def place(self,event):
        if not self.doc or not self.mode: return
        page = self.doc.writer.pages[self.page]
        if page.rotation or float(page.cropbox.left)!=0 or float(page.cropbox.bottom)!=0 or page.cropbox!=page.mediabox:
            raise ValueError('此页有旋转或裁剪偏移，请先另存并规范页面后再添加标记；页面管理仍可使用')
        x = (self.canvas.canvasx(event.x)-24)/self.scale
        y = float(page.mediabox.height)-(self.canvas.canvasy(event.y)-24)/self.scale
        if not (0<=x<=float(page.mediabox.width) and 0<=y<=float(page.mediabox.height)): return
        if self.mode=='text':
            text = simpledialog.askstring('添加文字','文字（支持中文）：',parent=self)
            if text:
                self.doc.add_text(self.page,text,x,y)
                self.refresh()
            self.mode = None
        elif self.corner is None:
            self.corner = (x,y)
            self.status.set('再点击另一角完成高亮')
        else:
            x0,y0 = self.corner
            if abs(x-x0)<1 or abs(y-y0)<1: return
            self.doc.highlight(self.page,(min(x,x0),min(y,y0),max(x,x0),max(y,y0)))
            self.mode = None
            self.refresh()

    def export(self):
        self.require()
        path = filedialog.asksaveasfilename(defaultextension='.png',filetypes=[('PNG','*.png')])
        if path: self.doc.render(self.page,2).save(path)

    def search(self):
        self.require()
        text = simpledialog.askstring('查找文字','查找：')
        if not text: return
        hits = [str(i+1) for i,p in enumerate(self.doc.writer.pages) if text.casefold() in (p.extract_text() or '').casefold()]
        messagebox.showinfo('查找结果','匹配页：'+', '.join(hits) if hits else '未找到文字；扫描 PDF 需要 OCR，本版本不含 OCR。')

    def convert(self):
        source = filedialog.askopenfilename(title='选择图片、文本或 Office 文件')
        if not source: return
        target = filedialog.asksaveasfilename(defaultextension='.pdf',initialfile=Path(source).stem+'.pdf',filetypes=[('PDF','*.pdf')])
        if not target: return
        if Path(source).resolve()==Path(target).resolve(): raise ValueError('输出不能覆盖输入文件')
        self.status.set('正在转换…')
        self.update_idletasks()
        convert_to_pdf(source,target)
        self.open(target)

    def default_app(self):
        if sys.platform=='win32':
            import os
            os.startfile('ms-settings:defaultapps')
            messagebox.showinfo('文件关联','运行安装包后，在 Windows 默认应用中找到 Simple PDF reader，设置 .pdf 关联。Windows 要求由用户选择默认应用。')
        else:
            messagebox.showinfo('文件关联','在系统文件管理器中选择 PDF → 打开方式 → Simple PDF reader。')

    def close(self):
        if self.discard():
            self.guard(self.remember)
            self.destroy()


if __name__=='__main__':
    App().mainloop()
