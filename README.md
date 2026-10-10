# Simple PDF reader

免费、本地优先的 Windows PDF 阅读器与基础编辑器，MIT 许可证。采用类似 Acrobat 的三栏布局：页面导航、阅读区、工具区。无需订阅，无广告，无遥测。版本：0.1.0（初始版本）。

## 功能

- 打开 PDF，包括正确密码解锁的加密 PDF；缩放、页面跳转、文字查找。
- 页面旋转、删除、合并、按指定顺序提取；最多 10 次撤销。
- 点击添加中英文文字、区域高亮；导出当前页 PNG。
- AES-256 加密、输入正确密码后解密另存。普通“另存为”输出不加密。
- PNG/JPEG/BMP/TIFF/WebP 转 PDF；UTF-8 TXT/Markdown 转 PDF（Markdown 作为纯文本）。
- DOC/DOCX、XLS/XLSX、PPT/PPTX、ODF、RTF、HTML 转 PDF，需要安装免费 LibreOffice。
- 每 5 秒及关闭时保存本地阅读页码、缩放；“最近阅读”继续阅读。
- Google Drive / OneDrive 个人账户：官方 OAuth + PKCE 登录，云端书库、一键上传当前 PDF 与进度，下载后回到原页码。
- Windows 安装包注册“打开方式”和默认应用候选；用户在系统默认应用中选择后，双击任意 `.pdf` 即可打开。

## 下载和安装

GitHub → Actions → 最近成功的 Windows build → `Simple-PDF-reader-Windows` artifact。解压后运行 `Simple-PDF-reader-Setup.exe`，或进入 `Simple PDF reader` 文件夹运行 exe。安装不需要管理员权限。初始版本尚未代码签名。

## 从源码运行

需要官方 Python 3.12+（含 Tkinter）。Windows PowerShell：

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
# 打开指定文件：
.venv\Scripts\python app.py "C:\Documents\book.pdf"
```

## 私人云端书库

第一次使用必须创建自己的免费 OAuth 应用，参见 [CLOUD_SETUP.md](CLOUD_SETUP.md)。此项目没有内置开发者的 OAuth 客户端，不能跳过配置直接登录。

配置后：云端书库 → 选择平台 → 登录 → 上传当前书籍与进度。以后在其他电脑或重装系统后，使用**同一个 OAuth Client ID 和同一个云盘账户**，登录 → 选择书籍 → 继续阅读。Google 备份位于应用隐藏数据文件夹；OneDrive 位于应用专用文件夹。可同时分别备份到两个平台。

同步采用手动一键上传，不会在后台自动上传私人文件。多设备以最后一次上传为准；不同内容的 PDF 视为不同版本，暂不合并冲突。修改文件后请先另存，再上传。加密 PDF 上传原始加密字节，不保存 PDF 密码；云端恢复后仍需输入密码。阅读进度和文件名没有额外加密。单次上传上限 200 MB，下载 PDF 解压上限 512 MB；云盘自身容量限制仍然适用。

阅读记录保存在 `%LOCALAPPDATA%\Simple PDF reader\library.json`；云盘令牌和 Google 桌面客户端 secret 存于系统凭据库。重装后需要重新授权并填写同一客户端配置；请另行妥善保留 OAuth Client ID / Google 客户端配置，不能只依赖已重装的本机。

## 当前边界

这是基础编辑器，不是 Acrobat 全功能替代品。添加文字是叠加内容，不能直接重排或修改原始段落；不含 OCR、数字签名、真正的内容涂黑删除、交互表单编辑。高亮是注释，不是涂黑。旋转或裁剪偏移页面暂不支持点击标记。扫描件查找需要 OCR。Office 转换不保证复杂文档与原应用排版完全一致。Microsoft 版本目前支持个人 OneDrive，未实现企业 SharePoint。

PDF 编辑可能使已有数字签名失效。保留原始文件；默认保存建议名称带 `-edited`。

## 开发验证

```powershell
python -m unittest discover -s tests -v
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --windowed --name "Simple PDF reader" --collect-all pypdfium2 --collect-all reportlab --collect-all keyring --collect-all jaraco app.py
python collect_licenses.py
```

测试覆盖密码错误拒绝、AES 加密/解密回读、页面编辑、撤销、合并提取、格式转换、PDFium 渲染、重装场景备份恢复以及云盘上传请求结构。真实云盘端到端验证需要用户配置 OAuth 应用并授权，初始交付未冒充通过真实账户测试。

## 许可证

本项目代码采用 [MIT](LICENSE)。第三方依赖保留各自许可证，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。不使用 Adobe 商标、图标或代码。应用本身免费；云盘超出免费容量时，平台可能收取扩容费用。
