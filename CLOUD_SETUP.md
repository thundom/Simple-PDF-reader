# 云盘开发者配置（普通用户无需填写 ID）

本程序使用官方浏览器登录，不接收 Google 密码。普通用户界面不提供 Client ID 输入。以下步骤仅供项目维护者一次性注册应用；目前尚未完成注册，云盘功能等待后续启用。

维护者复制 `oauth-clients.example.json` 为 `oauth-clients.json`，填写Google 桌面应用身份，放在源码或 exe 同目录。真实配置默认被 Git 忽略，不提交密钥到公开仓库。应用身份决定备份所在的私人应用文件夹，后续版本必须保持一致。仅创建示例文件不会启用云盘，也不能使用其他软件的 Client ID。

## Google Drive

1. 打开 https://console.cloud.google.com/ ，创建个人项目。
2. 启用 Google Drive API。
3. 配置 Google Auth Platform：应用名称 `Simple PDF reader`，选择适合个人账户的 External audience；测试阶段将自己的 Google 邮箱加入测试用户。
4. 添加 scope `https://www.googleapis.com/auth/drive.appdata`。
5. 创建 OAuth Client，类型必须是 **Desktop app（桌面应用）**。下载客户端 JSON 并妥善保存到另一安全位置。
6. 在维护者的 `oauth-clients.json` 中填写 `Google Drive.client_id` 与 `Google Drive.client_secret`。Google 桌面客户端 secret 不是用户密码；发行方式应由维护者按官方桌面客户端政策决定。
7. 用户点击“网页登录”，浏览器中选择自己的账户并授权；成功后显示云端书库。

个人测试应用可能遇到未验证应用提示或测试模式令牌过期；按 Google 控制台当前政策配置自己的应用。发布给他人使用时，应由维护者配置合适的 OAuth 发布状态并按要求验证，而不是要求他人提供账户密码。

Google `appDataFolder` 不显示在普通 Drive 文件列表中，程序的云端书库可查看和恢复。删除 OAuth 项目/更换 Client ID 可能导致原备份无法通过新应用访问。

官方资料：
- https://developers.google.com/identity/protocols/oauth2/native-app
- https://developers.google.com/workspace/drive/api/guides/appdata

## 重装恢复

用户重新安装带相同应用身份的发行版 → 网页登录相同账户 → 刷新书库 → 继续阅读。文件、页码、布局、页内阅读位置一起下载。PDF 打开密码不会存云端，必须自己记住。

退出登录仅删除本机令牌；要撤销授权，使用Google 账户的已授权应用页面。不要删除应用或云端数据，除非不再需要备份。
