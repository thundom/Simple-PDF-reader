import tkinter as tk
from tkinter import ttk,messagebox
from PIL import Image,ImageTk,ImageDraw
from i18n import tr
from printing import PAPERS,DEVMODE,driver_settings,placement,cells,sheet_groups
from windows import printers,print_document

def show(app):
    app.require()
    available=printers()
    if not available: raise ValueError(tr('未找到打印机，请先安装打印机驱动'))
    win=tk.Toplevel(app); win.title(tr('打印 PDF')); win.geometry('1020x730'); win.transient(app); win.grab_set()
    left=ttk.Frame(win); left.pack(side='left',fill='y')
    scroller=tk.Canvas(left,width=330,highlightthickness=0,bg='#f6f7f9')
    scrollbar=ttk.Scrollbar(left,orient='vertical',command=scroller.yview); scrollbar.pack(side='right',fill='y')
    scroller.configure(yscrollcommand=scrollbar.set); scroller.pack(side='left',fill='y')
    settings=ttk.Frame(scroller,padding=20); scroller.create_window(0,0,window=settings,anchor='nw',width=325)
    settings.bind('<Configure>',lambda e:scroller.configure(scrollregion=scroller.bbox('all')))
    scroller.bind('<MouseWheel>',lambda e:scroller.yview_scroll(-int(e.delta/120)*3,'units'))
    preview=ttk.Frame(win,padding=15); preview.pack(side='right',fill='both',expand=True)
    printer=tk.StringVar(value=available[0]); paper=tk.StringVar(value='A4'); orientation=tk.IntVar(value=1)
    scaling=tk.StringVar(value='fit'); duplex=tk.IntVar(value=1); mode=tk.StringVar(value='all'); filtering=tk.StringVar(value='all')
    gray=tk.BooleanVar(); reverse=tk.BooleanVar(); nup=tk.StringVar(value='1'); count=tk.StringVar(value='1'); page_text=tk.StringVar(value=str(app.page+1)); dpi=tk.StringVar(value='300')
    selected_driver=[None]; driver_choice=[None]; preview_index=[0]; preview_image=[None]; cancelled=[False]; busy=[False]
    def label(text): ttk.Label(settings,text=tr(text),font=('Segoe UI',10,'bold')).pack(anchor='w',pady=(10,4))
    def combo(variable,values):
        item=ttk.Combobox(settings,textvariable=variable,values=values,state='readonly'); item.pack(fill='x'); item.bind('<<ComboboxSelected>>',lambda e:update()); return item
    label('打印机'); combo(printer,available)
    label('份数'); ttk.Spinbox(settings,from_=1,to=99,textvariable=count,width=8).pack(anchor='w')
    label('页码范围')
    for text,key in [('所有页','all'),('当前页','current'),('自定义','custom')]: ttk.Radiobutton(settings,text=tr(text),variable=mode,value=key,command=update if False else lambda:update()).pack(anchor='w')
    entry=ttk.Entry(settings,textvariable=page_text); entry.pack(fill='x'); entry.bind('<KeyRelease>',lambda e:update())
    ttk.Label(settings,text='1-3,5,7-9').pack(anchor='w')
    label('页面筛选')
    filter_display=tk.StringVar(value=tr('全部'))
    filters={tr('全部'):'all',tr('奇数页'):'odd',tr('偶数页'):'even'}
    item=combo(filter_display,list(filters)); item.bind('<<ComboboxSelected>>',lambda e:(filtering.set(filters[filter_display.get()]),update()))
    ttk.Checkbutton(settings,text=tr('逆序'),variable=reverse,command=lambda:update()).pack(anchor='w',pady=5)
    label('纸张'); combo(paper,list(PAPERS))
    label('方向')
    row=ttk.Frame(settings); row.pack(fill='x')
    for text,key in [('纵向',1),('横向',2)]: ttk.Radiobutton(row,text=tr(text),variable=orientation,value=key,command=lambda:update()).pack(side='left')
    label('缩放')
    for text,key in [('适合','fit'),('实际大小','actual'),('缩小超大页面','shrink')]: ttk.Radiobutton(settings,text=tr(text),variable=scaling,value=key,command=lambda:update()).pack(anchor='w')
    label('双面')
    duplex_display=tk.StringVar(value=tr('单面')); duplex_values={tr('单面'):1,tr('长边翻转'):2,tr('短边翻转'):3}
    item=combo(duplex_display,list(duplex_values)); item.bind('<<ComboboxSelected>>',lambda e:duplex.set(duplex_values[duplex_display.get()]))
    label('每张纸页数'); combo(nup,['1','2','4','6','9','16'])
    row=ttk.Frame(settings); row.pack(fill='x',pady=8)
    ttk.Label(row,text='DPI').pack(side='left'); ttk.Combobox(row,textvariable=dpi,values=['150','300','600'],state='readonly',width=7).pack(side='left',padx=8)
    ttk.Checkbutton(settings,text=tr('灰度打印'),variable=gray,command=lambda:update()).pack(anchor='w')
    caption=tk.StringVar(); ttk.Label(preview,textvariable=caption,wraplength=510).pack(pady=8)
    canvas=tk.Canvas(preview,bg='#555b63',width=500,height=550,highlightthickness=0); canvas.pack(fill='both',expand=True)
    navigation=ttk.Frame(preview); navigation.pack(pady=8)
    def move(delta): preview_index[0]=max(0,preview_index[0]+delta); update()
    ttk.Button(navigation,text='‹',command=lambda:move(-1)).pack(side='left')
    ttk.Button(navigation,text='›',command=lambda:move(1)).pack(side='left')
    def indices():
        result=list(range(len(app.doc))) if mode.get()=='all' else [app.page] if mode.get()=='current' else app.page_range(page_text.get())
        if filtering.get()!='all': result=[i for i in result if (i%2==0)==(filtering.get()=='odd')]
        if not result: raise ValueError(tr('页码超出范围'))
        return list(reversed(result)) if reverse.get() else result
    def options(): return {'paper':paper.get(),'orientation':orientation.get(),'scaling':scaling.get(),'duplex':duplex.get(),'grayscale':gray.get(),'nup':int(nup.get()),'dpi':int(dpi.get())}
    def update():
        try:
            groups=sheet_groups(indices(),int(nup.get())); preview_index[0]=min(preview_index[0],len(groups)-1)
            _,mw,mh=PAPERS[paper.get()]
            if orientation.get()==2: mw,mh=mh,mw
            ratio=min(460/mw,510/mh); width,height=int(mw*ratio),int(mh*ratio)
            image=Image.new('RGB',(width,height),'white'); draw=ImageDraw.Draw(image)
            margin=5*ratio
            draw.rectangle((margin,margin,width-margin,height-margin),outline='#b8c1ca')
            for index,area in zip(groups[preview_index[0]],cells(width-2*margin,height-2*margin,int(nup.get()))):
                x,y,w,h=area; area=(x+margin,y+margin,w,h)
                pw,ph=app.sizes[index]; source=app.doc.render(index,min(1.2,500/max(pw,ph)))
                if gray.get(): source=source.convert('L').convert('RGB')
                x,y,w,h=placement((pw,ph),area,scaling.get(),ratio*25.4)
                source=source.resize((max(1,int(w)),max(1,int(h))),Image.Resampling.LANCZOS)
                ax,ay,aw,ah=area
                tile=Image.new('RGB',(max(1,int(aw)),max(1,int(ah))),'white')
                tile.paste(source,(int(x-ax),int(y-ay))); image.paste(tile,(int(ax),int(ay)))
            preview_image[0]=ImageTk.PhotoImage(image,master=win); canvas.delete('all'); canvas.create_image(250,275,image=preview_image[0])
            caption.set(tr('打印预览')+f' · {preview_index[0]+1}/{len(groups)} · '+tr('预览按 5 mm 边距估算；实际以打印机可打印区域为准。'))
        except ValueError as error: caption.set(str(error))
    def properties():
        value=driver_settings(printer.get(),options(),win.winfo_id(),True)
        if value:
            dm=DEVMODE.from_buffer(value); selected_driver[0]=value
            orientation.set(dm.orientation); gray.set(dm.color==1); duplex.set(dm.duplex)
            duplex_display.set(next((k for k,v in duplex_values.items() if v==dm.duplex),tr('单面')))
            supported=next((name for name,item in PAPERS.items() if item[0]==dm.paper),None)
            if not supported:
                selected_driver[0]=None
                raise ValueError('Select A4, Letter, A3, A5 or Legal in driver properties.')
            paper.set(supported)
            driver_choice[0]=(printer.get(),options())
            update()
    def submit():
        result=indices(); copies=int(count.get())
        if not 1<=copies<=99: raise ValueError(tr('份数必须在 1 到 99 之间'))
        opts=options()
        # Revalidate selected values with the driver; unsupported duplex/paper is an error.
        driver=selected_driver[0] if driver_choice[0]==(printer.get(),opts) else driver_settings(printer.get(),opts)
        busy[0]=True; cancelled[0]=False; start.configure(state='disabled')
        def progress(page,copy): caption.set(tr('打印：第 {0} 页，副本 {1}/{2}').format(page+1,copy+1,copies)); win.update()
        try:
            print_document(app.doc,printer.get(),result,copies,progress,opts,driver,lambda:cancelled[0])
            messagebox.showinfo(tr('打印'),tr('打印任务已提交到打印机'),parent=win)
        finally: busy[0]=False; start.configure(state='normal')
    def close():
        if busy[0]: cancelled[0]=True
        else: win.destroy()
    buttons=ttk.Frame(preview); buttons.pack(pady=12)
    ttk.Button(buttons,text=tr('驱动属性'),command=lambda:app.guard(properties)).pack(side='left',padx=4)
    start=ttk.Button(buttons,text=tr('开始打印'),command=lambda:app.guard(submit)); start.pack(side='left',padx=4)
    ttk.Button(buttons,text=tr('取消'),command=close).pack(side='left',padx=4)
    win.protocol('WM_DELETE_WINDOW',close); win.after(100,update)
