# Version 0.4.0 — Interactive installer update

The desktop application is unchanged from v0.4.0. The recommended installer is now an interactive EXE wizard with destination folder selection, start menu options, an optional desktop shortcut, installation progress, and a completion-page checkbox to launch the reader.

The destination page is always visible, including updates. The launch action runs only when selected on the completion page and is skipped during silent installation. Installer languages are English, Simplified Chinese, and Japanese.

The public installer explicitly excludes the personal Google OAuth configuration and portable reading data. A configured personal build is produced separately. Public GitHub documentation, commit messages, and release descriptions are in English.

The MSI remains a minimal package and does not provide this wizard. Before switching from an older MSI to the EXE installer, close the reader and uninstall the MSI through Windows Settings. Neither uninstaller deliberately deletes the reading-state directory.

Desktop verification already completed: twelve PDF, backup-protocol, and printing-geometry tests; source UI checks in English, Chinese, and Japanese; menus, home library, navigation, panel visibility, preferences, property tabs, custom metadata round-trip, and encrypted source permission inspection. The compiled v0.4 desktop executable starts and responds.

Real Google authorization, physical printing, and HTML browser end-to-end validation remain untested. See README.md for functional limits.
