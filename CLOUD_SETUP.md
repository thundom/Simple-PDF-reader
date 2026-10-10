# 云盘首次配置（自用）

本程序使用官方浏览器登录，不接收 Google / Microsoft 密码。首次配置应用后，通常只需登录和点击上传。应用身份决定备份所在的私人应用文件夹，因此重装或换电脑必须使用原来的 Client ID。

## Google Drive

1. 打开 https://console.cloud.google.com/ ，创建个人项目。
2. 启用 Google Drive API。
3. 配置 Google Auth Platform：应用名称 `Simple PDF reader`，选择适合个人账户的 External audience；测试阶段将自己的 Google 邮箱加入测试用户。
4. 添加 scope `https://www.googleapis.com/auth/drive.appdata`。
5. 创建 OAuth Client，类型必须是 **Desktop app（桌面应用）**。下载客户端 JSON 并妥善保存到另一安全位置。
6. 程序 → 云端书库 → Google Drive → 配置，填写 Client ID 和 Client secret（不上传到 GitHub）。
7. 点击登录，浏览器中选择自己的账户并授权；成功后显示云端书库。

个人测试应用可能遇到未验证应用提示或测试模式令牌过期；按 Google 控制台当前政策配置自己的应用。发布给他人使用时，应由维护者配置合适的 OAuth 发布状态并按要求验证，而不是要求他人提供账户密码。

Google `appDataFolder` 不显示在普通 Drive 文件列表中，程序的云端书库可查看和恢复。删除 OAuth 项目/更换 Client ID 可能导致原备份无法通过新应用访问。

官方资料：
- https://developers.google.com/identity/protocols/oauth2/native-app
- https://developers.google.com/workspace/drive/api/guides/appdata

## OneDrive（个人账户）

1. 打开 https://entra.microsoft.com/ → App registrations → New registration。
2. 名称 `Simple PDF reader`，选择支持 Personal Microsoft accounts 的账户类型。
3. Authentication → Add a platform → **Mobile and desktop applications**。
4. 添加 redirect URI `http://localhost/callback`（不是 Web 或 SPA 客户端）。本程序使用随机本地端口；Microsoft 对 localhost 忽略端口，路径必须匹配。
5. API permissions → Microsoft Graph → Delegated permissions，添加 `Files.ReadWrite.AppFolder` 和 `offline_access`。不需要整盘读取权限，不创建客户端 secret。
6. 复制 Application (client) ID；程序 → 云端书库 → OneDrive → 配置。
7. 登录个人 Microsoft 账户，授权后上传、列出和继续阅读。

账户或租户必须允许创建应用；如果控制台阻止注册，需要使用有此权限的账户或先使用本地阅读功能。

官方资料：
- https://learn.microsoft.com/en-us/graph/onedrive-sharepoint-appfolder
- https://learn.microsoft.com/en-us/entra/identity-platform/reply-url

## 重装恢复

重新安装 → 填写原 Client ID（Google 还需原桌面 Client secret）→ 登录相同账户 → 刷新书库 → 继续阅读。文件及页码一起下载。PDF 打开密码不会存云端，必须自己记住。

退出登录仅删除本机令牌；要撤销授权，使用各平台账户的已授权应用页面。不要删除应用或云端数据，除非不再需要备份。
