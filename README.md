# Simple PDF reader

A free, local-first Windows PDF reader and basic editor, released under the MIT license. Version 0.4.0. The interface defaults to English and supports Simplified Chinese and Japanese. No subscription, advertisements, or telemetry.

## Downloads and installation

For interactive installation, use **Simple-PDF-reader-Setup.exe** from the latest successful GitHub Actions Windows build. It includes:

- A welcome page and MIT license notice.
- A destination folder picker, including a Browse button.
- Start menu folder selection and an optional desktop shortcut.
- An installation summary and progress page.
- A completion page with a **Launch Simple PDF reader** checkbox.
- English, Simplified Chinese, and Japanese installer languages.

Installation is for the current user. Choose a folder you can write to. The EXE wizard is the recommended interactive installer. The MSI package is a minimal Windows Installer package without this wizard.

If you installed an older MSI, close the reader and uninstall that MSI through Windows Settings before switching to the EXE installer. The MSI and EXE have separate uninstall records. Local reading progress is stored outside the installed program directory and is not deliberately deleted by either uninstaller.

Portable options are also available: unzip the portable folder or use the single-file portable EXE. Portable builds store progress in a `Data` folder beside the program and therefore need a writable directory.

The application and its installer are not code-signed.

## Reading and workspace

- Open ordinary and password-protected PDFs using the correct password.
- Single page, two pages, continuous scrolling, and continuous two-page layouts.
- Page number entry, first/last page, previous/next page, zoom, fit width, and text search.
- File, Edit, View, Sign, Tools, Window, and Help menus; an icon context menu.
- Original flat icons, hover tooltips, a fixed toolbar, and a popup editing toolbar.
- Collapsible navigation and tool panels; customizable quick toolbar actions.
- A home screen listing recent documents with their reading position, last-read time, and location. Double-click a file to resume.
- Saved preferences for language, new-file layout, panel visibility, and toolbar actions.
- Document properties: description, source security permissions, fonts and embedding, editable custom metadata, and advanced PDF structure information.

Progress saves every five seconds and when closing a document: page, zoom, layout, and position within a page. Missing recent files remain listed with a helpful message. Older records without timestamps display a dash.

## Editing and conversion

- Add text or images, highlight areas, add sticky comments, and place handwritten or imported image signatures.
- Fill supported text and checkbox AcroForm fields.
- Rotate, delete, merge, extract, and split pages; up to ten undo checkpoints.
- Split into individual pages, groups of N pages, or custom ranges.
- AES-256 encryption and password-authorized decryption to a new file. Normal Save a copy produces an unencrypted PDF.
- Export page images or document text.
- Convert images and UTF-8 text to PDF. Office and other supported document conversions require a separately installed LibreOffice.
- OCR text extraction requires a separately installed Tesseract engine and language packs.

Edits are kept in memory until saved. Metadata changes are also saved through Save a copy. Keep an original copy, especially for signed documents.

## Printing

Preview and driver-aware printing include paper size, orientation, page ranges, copies, odd/even pages, reverse order, grayscale, fit/actual/shrink sizing, duplex when supported, multiple pages per sheet, and 150/300/600 DPI raster output. The preview uses estimated margins; the actual printer's printable area governs output. Physical printing has not been tested.

## Google Drive

Configured personal builds use official browser sign-in with OAuth PKCE and a local callback. Users do not enter a client ID into the app. Manually upload the current PDF and reading position, or restore a saved book after reinstalling Windows. Backups use the app's hidden Drive data folder.

Public builds omit the personal OAuth configuration. See `CLOUD_SETUP.md` for developer registration. OneDrive is not included.

No PDFs are uploaded automatically. Uploads are limited to 200 MB; restored PDFs are limited to 512 MB. Different PDF bytes identify different versions. Save edits before uploading. Encrypted source bytes remain encrypted in backup, and PDF passwords are never saved. Drive tokens use the operating system credential store; another computer needs a new sign-in.

Installer reading data: `%LOCALAPPDATA%\Simple PDF reader`. Portable reading data: `Data` beside the executable. Browser-based reading data uses the browser's local storage facilities.

## Offline HTML edition

`Simple-PDF-reader.html` is a self-contained offline reader containing PDF.js and pdf-lib. It has no Google functionality. It supports basic local overlays and page operations, with more limited editing than the desktop version. Password PDFs are readable but not editable in this edition. Printing opens the PDF in the browser's native PDF viewer. Clearing browser data removes its local library; download copies you want to keep. Browser end-to-end validation has not been completed.

## Limits

This is a basic editor, not a complete Acrobat replacement. It does not reflow or directly edit original paragraphs, provide certificate signatures, perform secure redaction, offer remote signing or collaboration servers, or implement professional prepress, ICC color management, booklet printing, or poster printing. Visual signatures are images. OCR does not include scanner acquisition or searchable PDF creation. Some rotated or crop-offset pages do not support click-based annotations. Two-page layouts do not treat the first page as a separate cover.

The security properties page reports permissions declared by the source file; the app does not enforce every declared PDF permission. Changing a signed PDF can invalidate its signature. Office conversion can differ from the original application's layout.

## Development

Use Python 3.12 with Tkinter on Windows:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
.venv\Scripts\python -m unittest discover -s tests -v
```

Build the desktop program, collect dependency notices, and compile the wizard using Inno Setup 6.5 or newer:

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --windowed --name "Simple PDF reader" --collect-all pypdfium2 --collect-all reportlab --collect-all keyring --collect-all jaraco app.py
python collect_licenses.py
& "C:/Program Files (x86)/Inno Setup 6/ISCC.exe" installer.iss
```

The public wizard excludes `oauth-clients.json` even if it is present in the build folder. An explicitly configured personal installer can be built with `/DIncludeGoogle`; do not publish that build. `SourceDir`, `OutputFolder`, and `OutputName` compiler defines allow alternate build locations.

## License

Project code is MIT, copyright 2026 thundom. Dependencies retain their own licenses; see `THIRD_PARTY_NOTICES.md` and the bundled dependency notices. Original icons and code are used; Adobe trademarks and assets are not included. The installer is built with Inno Setup, retaining its upstream notices.
