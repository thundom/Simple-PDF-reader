# Google Drive developer setup

The public build deliberately omits a registered personal OAuth client. Ordinary users of a configured build click browser sign-in; they do not enter a developer client ID into the reader.

## Register a desktop application

1. Create or select a project in Google Cloud Console.
2. Enable the Google Drive API for that project.
3. Configure the Google Auth Platform branding, audience, and data-access settings for your application.
4. Register an OAuth client of type Desktop app and download its JSON configuration.
5. While the application is in testing, add the accounts that will use it to the test-user list.

The reader uses the `https://www.googleapis.com/auth/drive.appdata` scope, PKCE, state validation, and a temporary local HTTP callback on `localhost`. It stores backups in the app's hidden Drive data folder. It does not request access to all existing Drive files.

## Configure a personal build

Use `oauth-clients.example.json` as the format reference. Place `oauth-clients.json` beside the source or executable. It contains a Google Drive entry with `client_id` and `client_secret` from your registered desktop client. Do not paste user access tokens, passwords, or refresh tokens into that file.

The configuration is ignored by Git and excluded from public source archives. The public EXE installer also excludes it by default. To build a personal installer that embeds the configuration, pass `/DIncludeGoogle` to the Inno Setup compiler. Keep that build separate from public release assets.

Desktop client configuration identifies the application; it is not a user's Drive login. Every account still has to authorize through Google's own web page. Access and refresh tokens are kept in the operating system credential store rather than inside the source or reading-progress backup.

## Use and restore

Open Cloud library, sign in through the browser, and manually upload the current PDF with its reading position. On another computer, install a build configured with the same application identity, sign in to the same Google account, select the saved book, and resume reading.

Save edits before uploading. Password-protected PDFs are uploaded as the original encrypted file bytes; the PDF password is not stored. Restored encrypted PDFs still need their password.

Uploads are manual and limited to 200 MB. Restored PDFs are limited to 512 MB. Different PDF contents are treated as different versions, with no automatic conflict merging. Keep the OAuth application identity stable between versions.

## Public distribution

Before enabling Drive for general users, review the application's Google audience, publishing status, and any required platform verification in your Google console. A public installer without OAuth configuration still supports all local features. No real Google authorization or upload/download test has been completed for the personal build.

OneDrive support is intentionally not included. The offline HTML edition has no cloud functionality.
