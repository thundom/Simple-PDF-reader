"""Build a per-user Windows MSI using Python 3.12's Windows Installer bindings."""
import sys
from pathlib import Path
import uuid
import msilib
from msilib import schema, sequence

source = Path(sys.argv[1] if len(sys.argv)>1 else 'dist/Simple PDF reader').resolve()
output = Path(sys.argv[2] if len(sys.argv)>2 else 'dist/Simple-PDF-reader-Setup.msi').resolve()
if not (source/'Simple PDF reader.exe').exists(): raise SystemExit('Build the executable first')
output.parent.mkdir(parents=True,exist_ok=True)
namespace = uuid.UUID('acda48f0-9029-47cc-9ff1-a05335187ce2')
guid = lambda name: '{'+str(uuid.uuid5(namespace,name)).upper()+'}'
db = msilib.init_database(str(output),schema,'Simple PDF reader',guid('Product-0.4.0'),'0.4.0','thundom')
summary = db.GetSummaryInformation(20)
summary.SetProperty(msilib.PID_WORDCOUNT,10)
summary.Persist()
msilib.add_tables(db,sequence)
msilib.add_data(db,'Property',[
    ('INSTALLLEVEL','1'),('ARPCOMMENTS','Free local PDF reader and editor. MIT.'),
    ('ARPURLINFOABOUT','https://github.com/thundom/Simple-PDF-reader'),('UpgradeCode',guid('Upgrade'))])
msilib.add_data(db,'Directory',[
    ('TARGETDIR',None,'SourceDir'),('LocalAppDataFolder','TARGETDIR','.'),
    ('Programs','LocalAppDataFolder','Programs'),('INSTALLDIR','Programs','SIMPLEPD|Simple PDF reader'),
    ('ProgramMenuFolder','TARGETDIR','.'),('AppMenu','ProgramMenuFolder','SIMPLEPD|Simple PDF reader')])
msilib.add_data(db,'Feature',[('Main',None,'Simple PDF reader','PDF reader and editor',1,1,'INSTALLDIR',0)])
directories = {Path('.'): 'INSTALLDIR'}
cab = msilib.CAB('reader.cab')
files = [p for p in sorted(source.rglob('*')) if p.is_file() and p.name!='portable.flag' and 'Data' not in p.relative_to(source).parts]
for index,path in enumerate(files,1):
    relative = path.relative_to(source)
    parent = Path('.')
    for part in relative.parts[:-1]:
        child = parent/part
        if child not in directories:
            directory = 'd'+str(len(directories))
            msilib.add_data(db,'Directory',[(directory,directories[parent],f'D{len(directories):06}|{part}')])
            directories[child] = directory
        parent = child
    fid,cid = f'f{index}',f'c{index}'
    order,logical = cab.append(str(path),path.name,fid)
    msilib.add_data(db,'Component',[(cid,guid(str(relative)),directories[parent],256,None,fid)])
    msilib.add_data(db,'FeatureComponents',[('Main',cid)])
    short = f'F{index:06}.BIN'
    msilib.add_data(db,'File',[(fid,cid,short+'|'+path.name,path.stat().st_size,None,None,512,order)])

component = 'ShellIntegration'
msilib.add_data(db,'Component',[(component,guid(component),'INSTALLDIR',260,None,'r0')])
msilib.add_data(db,'FeatureComponents',[('Main',component)])
registry = [
    (r'Software\Classes\SimplePDFreader.Document',None,'PDF Document — Simple PDF reader'),
    (r'Software\Classes\SimplePDFreader.Document\shell\open\command',None,'"[INSTALLDIR]Simple PDF reader.exe" "%1"'),
    (r'Software\Classes\.pdf\OpenWithProgids','SimplePDFreader.Document',''),
    (r'Software\Simple PDF reader\Capabilities','ApplicationName','Simple PDF reader'),
    (r'Software\Simple PDF reader\Capabilities','ApplicationDescription','Free PDF reader and editor'),
    (r'Software\Simple PDF reader\Capabilities\FileAssociations','.pdf','SimplePDFreader.Document'),
    (r'Software\RegisteredApplications','Simple PDF reader',r'Software\Simple PDF reader\Capabilities'),
]
msilib.add_data(db,'Registry',[(f'r{i}',1,key,name,value,component) for i,(key,name,value) in enumerate(registry)])
msilib.add_data(db,'Shortcut',[(
    'MainShortcut','AppMenu','SIMPLEPD|Simple PDF reader',component,'[INSTALLDIR]Simple PDF reader.exe',None,
    'Simple PDF reader',None,None,None,1,'INSTALLDIR')])
cab.commit(db)
db.Commit()
print(f'Built {output.name}: {len(files)} files, {output.stat().st_size} bytes')
