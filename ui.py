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
    elif name=='edit': line([(16,56),(20,40),(49,11),(61,23),(32,52),(16,56)]); line([(43,17),(55,29)]); line([(12,64),(61,64)])
    elif name=='highlight':line([(12,45),(42,12),(60,30),(30,62),(12,45)]);line([(17,54),(12,63),(30,63)]);line([(33,22),(50,39)])
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
    elif name=='home': line([(8,33),(36,9),(64,33)]); line([(17,29),(17,63),(55,63),(55,29)]); rect((29,43,43,63))
    elif name=='settings':
        d.ellipse((17,17,55,55),outline=color,width=5);d.ellipse((28,28,44,44),outline=color,width=5)
        for a,b in [((36,7),(36,17)),((36,55),(36,65)),((7,36),(17,36)),((55,36),(65,36)),((15,15),(22,22)),((50,50),(57,57)),((15,57),(22,50)),((50,22),(57,15))]:line([a,b])
    elif name=='signature': line([(9,50),(18,33),(22,49),(32,23),(31,48),(45,37),(41,50),(61,42)]);line([(10,62),(63,62)])
    elif name=='comment': line([(9,13),(63,13),(63,48),(31,48),(17,62),(17,48),(9,48),(9,13)]);line([(19,25),(52,25)]);line([(19,36),(43,36)])
    elif name=='image': rect((9,11,63,61));d.ellipse((19,20,29,30),outline=color,width=4);line([(12,55),(30,36),(41,48),(52,32),(61,44)])
    elif name=='form': rect((12,8,60,64));rect((21,20,29,28));line([(36,24),(51,24)]);rect((21,38,29,46));line([(36,42),(51,42)])
    elif name in ('create','export','extract','merge','organize'):
        rect((17,8,55,61));line([(25,22),(47,22)]);line([(25,33),(44,33)])
        if name=='create':line([(43,52),(67,52)]);line([(55,40),(55,64)])
        elif name=='export':line([(33,51),(67,51),(57,41)]);line([(67,51),(57,61)])
        elif name=='extract':line([(5,52),(39,52),(29,42)]);line([(39,52),(29,62)])
        elif name=='merge':line([(7,48),(25,48),(36,57),(48,48),(65,48)])
        else:rect((23,43,31,53));rect((39,43,47,53))
    elif name=='unlock':d.arc((26,6,56,37),180,345,fill=color,width=5);rect((13,29,53,63));line([(33,42),(33,52)])
    elif name=='link':d.ellipse((8,20,39,51),outline=color,width=5);d.ellipse((33,20,64,51),outline=color,width=5);line([(25,36),(47,36)])
    elif name=='ocr':rect((12,10,60,62));line([(23,42),(31,24),(39,42)]);line([(27,35),(35,35)]);line([(45,24),(45,42)]);line([(21,53),(51,53)])
    elif name in ('sidebar','tools'):rect((8,12,64,60));line([(25 if name=='sidebar' else 47,12),(25 if name=='sidebar' else 47,60)]);line([(32,30),(42,36),(32,42)])
    elif name=='goto':rect((17,8,56,63));line([(5,36),(41,36),(31,26)]);line([(41,36),(31,46)])
    elif name in ('first','last'):line([(49,14),(27,36),(49,58)] if name=='first' else [(23,14),(45,36),(23,58)]);line([(17,14),(17,58)] if name=='first' else [(55,14),(55,58)])
    elif name=='fullscreen':
        for points in [[(10,27),(10,10),(27,10)],[(45,10),(62,10),(62,27)],[(62,45),(62,62),(45,62)],[(27,62),(10,62),(10,45)]]:line(points)
    elif name=='close':line([(17,17),(55,55)]);line([(55,17),(17,55)])
    elif name=='info':d.ellipse((9,9,63,63),outline=color,width=5);line([(36,31),(36,53)]);d.ellipse((33,19,39,25),fill=color)
    elif name=='keyboard':
        rect((6,17,66,55))
        for y in (27,37):
            for x in range(15,60,11):line([(x,y),(x+3,y)])
        line([(22,47),(50,47)])
    elif name=='properties':rect((15,8,57,64));line([(24,21),(46,21)]);line([(24,32),(46,32)]);line([(24,43),(46,43)]);line([(24,54),(39,54)])
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
