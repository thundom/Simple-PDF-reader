"""Preserve installed packages' copyright/license notices for binary distribution."""
import importlib.metadata
from pathlib import Path
import shutil
import sys

destination = Path(sys.argv[1] if len(sys.argv)>1 else 'dist/Simple PDF reader/third-party-licenses')
destination.mkdir(parents=True,exist_ok=True)
for distribution in importlib.metadata.distributions():
    name = distribution.metadata['Name']
    for file in distribution.files or []:
        if any(word in str(file).lower() for word in ('license','copying','notice','copyright')):
            source = Path(distribution.locate_file(file))
            if source.is_file():
                target = destination/name/str(file).replace('..','_')
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source,target)
