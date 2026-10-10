# Third-party notices

Simple PDF reader source code is MIT licensed. Dependencies are separately licensed:

| Component | License | Source |
| --- | --- | --- |
| Python / Tkinter | PSF / Tcl-Tk licenses | https://www.python.org/ |
| pypdf | BSD-3-Clause | https://github.com/py-pdf/pypdf |
| pypdfium2 | Apache-2.0 OR BSD-3-Clause; PDFium and bundled dependencies have separate notices | https://github.com/pypdfium2-team/pypdfium2 |
| Pillow | HPND / Pillow license | https://github.com/python-pillow/Pillow |
| ReportLab | BSD-style | https://hg.reportlab.com/hg-public/reportlab/ |
| cryptography | Apache-2.0 OR BSD-3-Clause | https://github.com/pyca/cryptography |
| Requests | Apache-2.0 | https://github.com/psf/requests |
| keyring | MIT | https://github.com/jaraco/keyring |
| PyInstaller (build tool) | GPL with distribution exception | https://pyinstaller.org/en/stable/license.html |

Binary builds include the dependency license files collected by `collect_licenses.py` and bundled component resources. Transitive dependencies retain their own licenses. LibreOffice is an optional separately installed program (MPL-2.0 and other component licenses); it is not bundled or relicensed by this project.
