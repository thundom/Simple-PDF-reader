"""Original line icons and accessible, delayed tooltips."""
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

def icon(master, name, color='#dbe0e7'):
    image=Image.new('RGBA',(72,72))
    d=ImageDraw.Draw(image)
    def line(points): d.line(points,fill=color,width=5,joint='curve')
    def rect(box): d.rectangle(box,outline=color,width=4)
    if name in ('single','continuous','double','doublecontinuous'):
        double=name.startswith('double'); scroll=name.endswith('continuous')
        if double:
            rect((7,10,31,49)); rect((40,10,64,49))
            if scroll: rect((7,57,31,70)); rect((40,57,64,70))
        else:
            rect((19,7,53,49))
            if scroll: rect((19,57,53,70))
    elif name=='open': line([(8,54),(8,20),(29,20),(35,28),(64,28),(56,56),(8,56)] )
    elif name=='save': rect((13,10,59,62)); rect((25,10,48,28)); rect((24,40,49,62))
    elif name=='print': rect((12,26,60,51)); rect((23,8,49,26)); rect((23,43,49,64)); d.ellipse((51,32,55,36),fill=color)
    elif name=='search': d.ellipse((10,9,48,47),outline=color,width=5); line([(45,44),(63,62)])
    elif name=='cloud': d.arc((6,24,38,56),90,270,fill=color,width=5); d.arc((23,10,56,45),180,360,fill=color,width=5); d.arc((45,27,67,56),270,90,fill=color,width=5); line([(20,56),(57,56)]); line([(36,47),(36,26),(26,36)]); line([(36,26),(46,36)])
    elif name=='edit' or name=='highlight': line([(16,56),(20,40),(49,11),(61,23),(32,52),(16,56)]); line([(43,17),(55,29)]); line([(12,64),(61,64)])
    elif name=='rotate' or name=='undo': d.arc((13,13,59,59),25,300,fill=color,width=5); line([(15,9),(15,28),(32,27)])
    elif name=='delete': line([(15,18),(57,18)]); rect((23,18,49,62)); line([(29,9),(43,9)]); line([(31,28),(31,52)]); line([(41,28),(41,52)])
    elif name=='lock': d.arc((23,7,49,39),180,360,fill=color,width=5); rect((15,29,57,62)); line([(36,41),(36,52)])
    elif name=='split': rect((11,9,61,63)); line([(3,36),(25,36)]); line([(33,36),(45,36)]); line([(53,36),(69,36)])
    elif name=='text': line([(12,14),(60,14)]); line([(36,14),(36,60)]); line([(24,60),(48,60)])
    elif name=='previous': line([(46,13),(24,36),(46,59)])
    elif name=='next': line([(25,13),(47,36),(25,59)])
    elif name=='plus': line([(14,36),(58,36)]); line([(36,14),(36,58)])
    elif name=='minus': line([(14,36),(58,36)])
    elif name=='fit': rect((9,16,63,56)); line([(16,36),(56,36)]); line([(24,28),(16,36),(24,44)]); line([(48,28),(56,36),(48,44)])
    elif name=='recent': d.ellipse((10,10,62,62),outline=color,width=5); line([(36,19),(36,37),(48,44)])
    else: rect((17,9,55,63)); line([(25,25),(47,25)]); line([(25,36),(47,36)]); line([(25,47),(42,47)])
    return ImageTk.PhotoImage(image.resize((24,24),Image.Resampling.LANCZOS),master=master)

class Tooltip:
    def __init__(self,widget,text):
        self.widget,self.text,self.timer,self.window=widget,text,None,None
        widget.bind('<Enter>',self.schedule,add='+')
        for event in ('<Leave>','<ButtonPress>','<Destroy>'): widget.bind(event,self.hide,add='+')
        widget.bind('<FocusIn>',self.schedule,add='+'); widget.bind('<FocusOut>',self.hide,add='+')
    def schedule(self,event=None):
        self.hide(); self.timer=self.widget.after(500,self.show)
    def show(self):
        self.timer=None
        if not self.widget.winfo_exists(): return
        self.window=tk.Toplevel(self.widget); self.window.overrideredirect(True)
        tk.Label(self.window,text=self.text,bg='#242a33',fg='white',padx=10,pady=7,font=('Segoe UI',10)).pack()
        self.window.geometry(f'+{self.widget.winfo_rootx()}+{self.widget.winfo_rooty()+self.widget.winfo_height()+6}')
    def hide(self,event=None):
        if self.timer:
            self.widget.after_cancel(self.timer); self.timer=None
        if self.window: self.window.destroy(); self.window=None
