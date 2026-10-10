"""Desktop menus, home library, preferences and truthful PDF properties."""
import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from i18n import tr
import i18n
from library import DATA_DIR


def preferences():
    try:
        value=json.loads((DATA_DIR/'preferences.json').read_text('utf-8'))
        return value if isinstance(value,dict) else {}
    except (OSError,ValueError):
        return {}


def font_details(writer):
    rows=[]; visited=set(); known=set()
    def visit(resources):
        if not resources: return
        resources=resources.get_object()
        for tag,ref in resources.get('/Font',{}).get_object().items() if resources.get('/Font') else []:
            font=ref.get_object()
            descendant=font.get('/DescendantFonts')
            actual=descendant[0].get_object() if descendant else font
            descriptor=actual.get('/FontDescriptor')
            descriptor=descriptor.get_object() if descriptor else {}
            embedded=any(k in descriptor for k in ('/FontFile','/FontFile2','/FontFile3'))
            row=(str(font.get('/BaseFont',tag)),str(font.get('/Subtype','')),str(font.get('/Encoding','')),tr('是') if embedded else tr('否'))
            if row not in known: rows.append(row); known.add(row)
        objects=resources.get('/XObject')
        if objects:
            for ref in objects.get_object().values():
                key=(getattr(ref,'idnum',None),getattr(ref,'generation',None)) if hasattr(ref,'idnum') else id(ref)
                if key in visited: continue
                visited.add(key)
                obj=ref.get_object()
                if obj.get('/Subtype')=='/Form': visit(obj.get('/Resources'))
    for page in writer.pages: visit(page.get('/Resources'))
    return rows


class DesktopFeatures:
    def load_preferences(self): return preferences()

    def save_preferences(self):
        DATA_DIR.mkdir(parents=True,exist_ok=True)
        self.preferences['language']=i18n.language
        target=DATA_DIR/'preferences.json'
        temporary=target.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.preferences,ensure_ascii=False,indent=2),'utf-8')
        os.replace(temporary,target)

    def install_shortcuts(self):
        for shortcut,action in [('<Control-k>',self.settings),('<Control-d>',self.properties),('<Control-w>',self.close_document),('<Control-q>',self.close),('<Control-g>',self.go_to_page),('<Control-Home>',lambda:self.goto_index(0)),('<Control-End>',lambda:self.goto_index(len(self.doc)-1 if self.doc else 0)),('<F11>',self.fullscreen),('<Escape>',lambda:self.attributes('-fullscreen',False))]:
            self.bind(shortcut,lambda e,f=action:self.guard(f))

    def build_menus(self):
        main=tk.Menu(self,tearoff=False); self.configure(menu=main); self.menu_icons=[]; self.menu_pictures={}
        def menu(label):
            result=tk.Menu(main,tearoff=False); main.add_cascade(label=tr(label),menu=result); return result
        def command(parent,label,action,key='single',shortcut=''):
            from ui import icon
            picture=icon(self,key,'#263447'); self.menu_icons.append(picture); self.menu_pictures[key]=picture
            parent.add_command(label=tr(label),image=picture,compound='left',accelerator=shortcut,command=lambda:self.guard(action))
        file=menu('文件')
        for label,action,key,shortcut in [('打开 PDF',self.open,'open','Ctrl+O'),('重新打开上次文件',self.reopen,'recent',''),('创建 PDF',self.convert,'create',''),('合并文件',self.merge,'merge',''),('保存副本',self.save,'save','Ctrl+S'),('导出 PDF',self.export_menu,'export',''),('关闭文件',self.close_document,'close','Ctrl+W'),('文档属性',self.properties,'properties','Ctrl+D'),('打印',self.print_pdf,'print','Ctrl+P')]: command(file,label,action,key,shortcut)
        file.add_separator(); command(file,'最近阅读',self.show_home,'recent'); command(file,'退出',self.close,'close','Ctrl+Q')
        edit=menu('编辑')
        for label,action,key,shortcut in [('撤销',self.undo,'undo','Ctrl+Z'),('编辑工具',self.edit_toolbar,'edit',''),('添加文字',lambda:self.set_mode('text'),'text',''),('添加图片',self.insert_image,'image',''),('区域高亮',lambda:self.set_mode('highlight'),'highlight',''),('注释',lambda:self.set_mode('comment'),'comment',''),('旋转页面',lambda:self.mutate('rotate'),'rotate',''),('删除页面',self.delete,'delete',''),('查找文字',self.search,'search','Ctrl+F')]: command(edit,label,action,key,shortcut)
        edit.add_separator(); command(edit,'首选项',self.settings,'settings','Ctrl+K')
        view=menu('视图'); navigation=tk.Menu(view,tearoff=False); view.add_cascade(label=tr('页面导航'),menu=navigation)
        for label,action,key,shortcut in [('第一页',lambda:self.goto_index(0),'first','Ctrl+Home'),('上一页',lambda:self.navigate(-1),'previous',''),('下一页',lambda:self.navigate(1),'next',''),('最后一页',lambda:self.goto_index(len(self.doc)-1 if self.doc else 0),'last','Ctrl+End'),('跳转页面',self.go_to_page,'goto','Ctrl+G')]: command(navigation,label,action,key,shortcut)
        display=tk.Menu(view,tearoff=False); view.add_cascade(label=tr('页面显示'),menu=display)
        for label in ('单页','双页','连续滚动','双页连续'): display.add_radiobutton(label=tr(label),variable=self.view,value=label,command=lambda:self.guard(self.change_view))
        for label,action,key,shortcut in [('放大',lambda:self.zoom(.15),'plus',''),('缩小',lambda:self.zoom(-.15),'minus',''),('适应宽度',self.fit,'fit',''),('显示／隐藏页面导航',lambda:self.toggle_panel('left'),'sidebar',''),('显示／隐藏工具栏',lambda:self.toggle_panel('right'),'tools',''),('自定义快捷工具栏',self.settings,'settings',''),('主页',self.show_home,'home',''),('全屏',self.fullscreen,'fullscreen','F11')]: command(view,label,action,key,shortcut)
        sign=menu('签名'); command(sign,'填写表单',self.fill_form,'form'); command(sign,'填写和签名',self.signature,'signature')
        tools=menu('工具')
        for label,action,key in [('组织页面',self.edit_toolbar,'organize'),('提取页面',self.extract,'extract'),('分割 PDF',self.split_pdf,'split'),('加密 PDF',self.encrypt,'lock'),('解密另存',self.decrypt,'unlock'),('扫描和 OCR',self.ocr,'ocr'),('云端书库',self.cloud_window,'cloud'),('关联 PDF',self.default_app,'link')]: command(tools,label,action,key)
        window=menu('窗口'); command(window,'最小化',self.iconify,'minus'); command(window,'全屏',self.fullscreen,'fullscreen','F11')
        helpmenu=menu('帮助'); command(helpmenu,'快捷键',self.shortcut_help,'keyboard'); command(helpmenu,'关于',self.about,'info')

    def goto_index(self,index):
        self.require(); self.hide_home(); self.jump_to(max(0,min(len(self.doc)-1,index)))

    def go_to_page(self,from_entry=False):
        self.require()
        value=self.page_entry.get().strip() if from_entry else ''
        if not value: value=simpledialog.askinteger(tr('跳转页面'),tr('页码'),minvalue=1,maxvalue=len(self.doc),initialvalue=self.page+1,parent=self)
        if value is None: return
        try: index=int(value)-1
        except (TypeError,ValueError): raise ValueError(tr('页码超出范围'))
        if not 0<=index<len(self.doc): raise ValueError(tr('页码超出范围'))
        self.goto_index(index)

    def fullscreen(self): self.attributes('-fullscreen',not self.attributes('-fullscreen'))

    def toggle_panel(self,side):
        panel=self.left_panel if side=='left' else self.right_panel
        if panel.winfo_manager(): panel.pack_forget(); collapsed=True
        else:
            panel.pack(side=side,fill='y',before=self.center); collapsed=False
        self.preferences[side+'_collapsed']=collapsed; self.save_preferences()
        if self.doc and not getattr(self,'home_frame',None): self.after(100,lambda:self.guard(self.refresh))

    def hide_home(self):
        frame=getattr(self,'home_frame',None)
        if frame and frame.winfo_exists(): frame.destroy()
        self.home_frame=None

    def recent_items(self):
        return sorted((b for b in self.library.books.values() if isinstance(b,dict) and 'path' in b),key=lambda b:b.get('updated',0),reverse=True)

    def show_home(self):
        self.hide_toolbar(); self.hide_home()
        if self.doc: self.remember()
        frame=tk.Frame(self.center,bg='#f4f5f7'); self.home_frame=frame
        frame.place(relx=0,rely=0,relwidth=1,relheight=1)
        title=tk.Frame(frame,bg='#f4f5f7'); title.pack(fill='x',padx=24,pady=22)
        tk.Label(title,text=tr('主页'),font=('Segoe UI',23,'bold'),bg='#f4f5f7',fg='#263447').pack(side='left')
        ttk.Button(title,text=tr('打开 PDF'),command=lambda:self.guard(self.open)).pack(side='right',padx=5)
        if self.doc: ttk.Button(title,text=tr('返回文档'),command=self.hide_home).pack(side='right',padx=5)
        tk.Label(frame,text=tr('最近阅读'),font=('Segoe UI',13,'bold'),bg='#f4f5f7',fg='#526176').pack(anchor='w',padx=24,pady=8)
        columns=('name','page','modified','path'); table=ttk.Treeview(frame,columns=columns,show='headings',selectmode='browse')
        for col,label,width in [('name','文件名',240),('page','页码',65),('modified','上次阅读',135),('path','位置',280)]: table.heading(col,text=tr(label)); table.column(col,width=width,minwidth=60)
        table.pack(fill='both',expand=True,padx=24,pady=10); self.home_table=table; self.home_items=self.recent_items()
        import datetime
        for i,item in enumerate(self.home_items):
            stamp=datetime.datetime.fromtimestamp(item['updated']).strftime('%Y-%m-%d %H:%M') if item.get('updated') else '—'
            table.insert('','end',iid=str(i),values=(item.get('name',Path(item['path']).name),item.get('page',0)+1,stamp,item['path']))
        def resume(event=None):
            selection=table.selection()
            if not selection: return
            path=self.home_items[int(selection[0])]['path']
            if not Path(path).is_file(): messagebox.showinfo(tr('最近阅读'),tr('文件已移动或删除，请重新打开。'),parent=self); return
            self.guard(lambda:self.open(path))
        table.bind('<Double-1>',resume); table.bind('<Return>',resume)
        bar=ttk.Frame(frame);bar.pack(fill='x',padx=24,pady=15)
        ttk.Button(bar,text=tr('继续阅读'),command=resume).pack(side='left')
        def remove():
            selection=table.selection()
            if not selection: return
            item=self.home_items[int(selection[0])]
            self.library.books={key:b for key,b in self.library.books.items() if b.get('path')!=item['path']}
            self.library.path.write_text(json.dumps(self.library.books,ensure_ascii=False,indent=2),'utf-8')
            # Rebuilding the list must not re-add an open document just removed.
            table.delete(selection[0])
        ttk.Button(bar,text=tr('移除记录'),command=lambda:self.guard(remove)).pack(side='left',padx=8)
        tk.Label(frame,text=tr('双击文件继续阅读；文件和进度保存在本机。'),bg='#f4f5f7',fg='#677589').pack(pady=12)

    def reopen(self):
        items=self.recent_items()
        if items: self.open(items[0]['path'])
        else: self.show_home()

    def close_document(self):
        if not self.discard(): return
        self.remember(); self.hide_toolbar(); self.doc=None;self.mode=None
        self.images.clear();self.positions.clear();self.canvas.delete('all');self.pages.delete(0,'end')
        self.title('Simple PDF reader');self.page_label.set(tr('未打开文件'));self.page_entry.set('');self.show_home()

    def context_menu(self,event):
        if not self.doc: return
        menu=tk.Menu(self,tearoff=False)
        for label,key,action in [('上一页','previous',lambda:self.navigate(-1)),('下一页','next',lambda:self.navigate(1)),('添加文字','text',lambda:self.set_mode('text')),('区域高亮','highlight',lambda:self.set_mode('highlight')),('注释','comment',lambda:self.set_mode('comment')),('填写和签名','signature',self.signature),('编辑工具','edit',lambda:self.edit_toolbar(event)),('文档属性','properties',self.properties)]:
            menu.add_command(label=tr(label),image=self.menu_pictures[key],compound='left',command=lambda f=action:self.guard(f))
        try: menu.tk_popup(event.x_root,event.y_root)
        finally: menu.grab_release()

    def insert_image(self):
        from tkinter import filedialog
        from PIL import Image
        self.require();path=filedialog.askopenfilename(filetypes=[('Image','*.png *.jpg *.jpeg')],parent=self)
        if path:
            with Image.open(path) as image: self.signature_image=image.convert('RGBA').copy()
            self.mode='signature';self.status.set(tr('点击页面放置图片'))

    def shortcut_help(self):
        messagebox.showinfo(tr('快捷键'),'Ctrl+O  '+tr('打开 PDF')+'\nCtrl+S  '+tr('保存副本')+'\nCtrl+P  '+tr('打印')+'\nCtrl+F  '+tr('查找文字')+'\nCtrl+G  '+tr('跳转页面')+'\nCtrl+D  '+tr('文档属性')+'\nCtrl+K  '+tr('首选项')+'\nCtrl+W  '+tr('关闭文件')+'\nCtrl+Home / End  '+tr('第一页')+' / '+tr('最后一页')+'\nF11  '+tr('全屏')+'\nEsc  '+tr('退出全屏'),parent=self)

    def settings(self):
        dialog=tk.Toplevel(self);dialog.title(tr('首选项'));dialog.geometry('650x520');dialog.transient(self)
        tabs=ttk.Notebook(dialog);tabs.pack(fill='both',expand=True,padx=15,pady=15)
        general=ttk.Frame(tabs,padding=20); tabs.add(general,text=tr('常规'))
        ttk.Label(general,text=tr('界面语言')).pack(anchor='w')
        lang=tk.StringVar(value=next((name for name,code in i18n.LANGUAGES.items() if code==i18n.language),'English'))
        ttk.Combobox(general,textvariable=lang,values=list(i18n.LANGUAGES),state='readonly').pack(fill='x',pady=8)
        ttk.Label(general,text=tr('新文件默认页面显示')).pack(anchor='w',pady=(16,0))
        modes=['单页','双页','连续滚动','双页连续'];layout=tk.StringVar(value=tr(self.preferences.get('layout','连续滚动')))
        ttk.Combobox(general,textvariable=layout,values=[tr(x) for x in modes],state='readonly').pack(fill='x',pady=8)
        left=tk.BooleanVar(value=self.preferences.get('left_collapsed',False));right=tk.BooleanVar(value=self.preferences.get('right_collapsed',False))
        ttk.Checkbutton(general,text=tr('默认收起页面导航'),variable=left).pack(anchor='w',pady=8)
        ttk.Checkbutton(general,text=tr('默认收起工具栏'),variable=right).pack(anchor='w',pady=8)
        toolbar=ttk.Frame(tabs,padding=20);tabs.add(toolbar,text=tr('快捷工具栏'));visible={}
        ttk.Label(toolbar,text=tr('选择顶部快捷工具栏显示的功能')).pack(anchor='w',pady=10)
        for label,button in self.toolbar_items:
            var=tk.BooleanVar(value=label not in self.preferences.get('hidden_tools',[]));visible[label]=var
            ttk.Checkbutton(toolbar,text=tr(label),variable=var).pack(anchor='w',pady=5)
        advanced=ttk.Frame(tabs,padding=20);tabs.add(advanced,text=tr('高级'))
        ttk.Label(advanced,text=tr('阅读进度每 5 秒及关闭文档时保存。'),wraplength=540).pack(anchor='w',pady=10)
        ttk.Label(advanced,text=tr('数据目录')+'\n'+str(DATA_DIR),wraplength=540).pack(anchor='w',pady=10)
        ttk.Label(advanced,text=tr('本地密码不保存；云盘仅在主动操作时连接。'),wraplength=540).pack(anchor='w',pady=10)
        def apply():
            chosen=i18n.LANGUAGES[lang.get()]
            self.preferences.update(layout=modes[[tr(x) for x in modes].index(layout.get())],left_collapsed=left.get(),right_collapsed=right.get(),hidden_tools=[name for name,var in visible.items() if not var.get()])
            self.save_preferences();dialog.destroy();self.switch_language(chosen)
        ttk.Button(dialog,text=tr('保存设置'),command=lambda:self.guard(apply)).pack(pady=(0,15))

    def properties(self):
        self.require();doc=self.doc;writer=doc.writer;source=doc.source_reader
        dialog=tk.Toplevel(self);dialog.title(tr('文档属性'));dialog.geometry('780x570');dialog.transient(self)
        tabs=ttk.Notebook(dialog);tabs.pack(fill='both',expand=True,padx=15,pady=15)
        def text_tab(label,value):
            frame=ttk.Frame(tabs);tabs.add(frame,text=tr(label));box=tk.Text(frame,wrap='word',font=('Segoe UI',10),padx=15,pady=15)
            scroll=ttk.Scrollbar(frame,command=box.yview);box.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');box.pack(fill='both',expand=True);box.insert('1.0',value);box.configure(state='disabled');return frame
        metadata=dict(writer.metadata or {});sizes=doc.page_sizes()
        description=ttk.Frame(tabs,padding=18);tabs.add(description,text=tr('描述'));fields={}
        for row,(label,key) in enumerate([('标题','/Title'),('作者','/Author'),('主题','/Subject'),('关键词','/Keywords')]):
            ttk.Label(description,text=tr(label)).grid(row=row,column=0,sticky='w',padx=5,pady=7);var=tk.StringVar(value=str(metadata.get(key,'')));fields[key]=var;ttk.Entry(description,textvariable=var,width=65).grid(row=row,column=1,sticky='ew',pady=7)
        description.columnconfigure(1,weight=1)
        details=f'{tr("文件名")}: {doc.path.name}\n{tr("位置")}: {doc.path}\n{tr("文件大小")}: {doc.path.stat().st_size:,} bytes\n{tr("页数")}: {len(doc)}\n{tr("页面尺寸")}: {sizes[self.page][0]:.2f} × {sizes[self.page][1]:.2f} pt\nPDF: {source.pdf_header}\n'
        for key in ('/Creator','/Producer','/CreationDate','/ModDate'):details+=key+': '+str(metadata.get(key,'—'))+'\n'
        ttk.Label(description,text=details,wraplength=660,justify='left').grid(row=4,column=0,columnspan=2,sticky='w',pady=12)
        encryption=source.trailer.get('/Encrypt');security=tr('源文件未加密')
        if encryption:
            obj=encryption.get_object();permissions=int(obj.get('/P',0)) & 0xffffffff
            security=tr('源文件已加密')+'\n'+tr('安全处理程序')+': '+str(obj.get('/Filter','—'))+'\nV: '+str(obj.get('/V','—'))+'   R: '+str(obj.get('/R','—'))+'   '+tr('密钥长度')+': '+str(obj.get('/Length',40))+' bits\n'
            for label,bit in [('允许打印',3),('允许修改',4),('允许复制',5),('允许注释',6),('允许填写表单',9),('辅助功能访问',10),('允许页面组装',11),('允许高质量打印',12)]: security+=tr(label)+': '+tr('是' if permissions & (1<<(bit-1)) else '否')+'\n'
        security+='\n'+tr('此处显示源文件声明的权限，不代表程序已强制执行全部权限。')+'\n'+tr('编辑副本保存在内存中；普通另存为输出未加密文件，需用加密功能重新设置密码。')
        text_tab('安全性',security)
        fonts=ttk.Frame(tabs);tabs.add(fonts,text=tr('字体'));table=ttk.Treeview(fonts,columns=('font','type','encoding','embedded'),show='headings')
        for col,label,width in [('font','字体名称',230),('type','类型',110),('encoding','编码',180),('embedded','嵌入',75)]:table.heading(col,text=tr(label));table.column(col,width=width)
        scrollbar=ttk.Scrollbar(fonts,command=table.yview);table.configure(yscrollcommand=scrollbar.set);scrollbar.pack(side='right',fill='y');table.pack(fill='both',expand=True)
        for values in font_details(writer):table.insert('','end',values=values)
        custom=ttk.Frame(tabs,padding=15);tabs.add(custom,text=tr('自定义'))
        ttk.Label(custom,text=tr('自定义元数据（JSON 对象，键以 / 开头）')).pack(anchor='w',pady=8)
        box=tk.Text(custom,height=15,wrap='word');box.pack(fill='both',expand=True);box.insert('1.0',json.dumps({k:str(v) for k,v in metadata.items() if k not in fields},ensure_ascii=False,indent=2))
        root=writer._root_object
        advanced=tr('页面布局')+': '+str(root.get('/PageLayout','—'))+'\n'+tr('页面模式')+': '+str(root.get('/PageMode','—'))+'\n'+tr('标签结构')+': '+tr('是' if root.get('/StructTreeRoot') else '否')+'\n'+tr('表单')+': '+tr('是' if root.get('/AcroForm') else '否')+'\n'+tr('查看器首选项')+': '+str(root.get('/ViewerPreferences','—'))+'\n'+tr('当前页面旋转')+': '+str(writer.pages[self.page].rotation)+'°\n'+tr('修改未保存')+': '+tr('是' if doc.dirty else '否')
        text_tab('高级',advanced)
        def apply():
            values=json.loads(box.get('1.0','end-1c'))
            if not isinstance(values,dict) or any(not isinstance(k,str) or not k.startswith('/') or not isinstance(v,str) for k,v in values.items()):raise ValueError(tr('元数据必须是键以 / 开头且值为字符串的 JSON 对象。'))
            values.update({k:v.get() for k,v in fields.items()});doc.checkpoint();writer.metadata=None;writer.add_metadata(values);self.refresh();dialog.destroy()
        ttk.Button(dialog,text=tr('应用元数据修改'),command=lambda:self.guard(apply)).pack(pady=(0,12))
