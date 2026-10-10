# Simple PDF reader

免费、本地优先的 Windows PDF 阅读器与基础编辑器，MIT 许可证。采用 Acrobat 风格的固定图标工具栏、悬停提示、右侧工具面板和弹出编辑工具栏。默认英文，支持简体中文与日文。无需订阅，无广告，无遥测。版本：0.3.0。

## 功能

- 打开 PDF，包括正确密码解锁的加密 PDF；缩放、适应宽度、键盘翻页、页面跳转、文字查找。
- 单页、双页、连续滚动、双页连续阅读；按视口加载页面图片，避免一次渲染整本书。
- 点击“编辑工具”或在页面右键弹出编辑工具栏。
- 页面旋转、删除、合并、按指定顺序提取；最多 10 次撤销。
- 分割 PDF：每页一个文件、每 N 页一个文件、或自定义分段（如 `1-3;4-6;7,9`）。
- 打印预览、纸张/方向/范围/份数、奇偶页/逆序、缩放/灰度/双面、多页合一、150/300/600 DPI；验证驱动支持的选项，可打开驱动属性。未做实体打印机实测。
- 添加文字、高亮、便签注释、手写/图片签名、文本及复选框表单填写；导出 PNG 和 UTF-8 文本。
- OCR 文字提取需免费 Tesseract 及语言包，不内置扫描仪采集。
- AES-256 加密、输入正确密码后解密另存。普通“另存为”输出不加密。
- PNG/JPEG/BMP/TIFF/WebP 转 PDF；UTF-8 TXT/Markdown 转 PDF（Markdown 作为纯文本）。
- DOC/DOCX、XLS/XLSX、PPT/PPTX、ODF、RTF、HTML 转 PDF，需要安装免费 LibreOffice。
- 每 5 秒及关闭时保存本地阅读页码、缩放、阅读布局与页内滚动位置；“最近阅读”继续阅读。
- Google Drive：官方 OAuth + PKCE 登录，云端书库、一键上传当前 PDF 与进度，下载后回到原页码。
- 程序内“关联 PDF”一键注册 PDF 打开方式；安装包自动注册默认应用候选。Windows 已有默认应用时仍需用户首次确认切换。

## 下载和安装

GitHub → Actions → 最近成功的 Windows build → `Simple-PDF-reader-Windows` artifact。

- **安装版**：`Simple-PDF-reader-Setup.exe`，自动安装、开始菜单快捷方式、PDF 打开方式注册。不需要管理员权限。
- **MSI 安装版**：`Simple-PDF-reader-Setup.msi`，使用 Windows Installer 安装至当前用户目录，带快捷方式与 PDF 打开方式注册。
- **绿色版**：`Simple-PDF-reader-Portable.zip`，解压后运行 `Simple PDF reader.exe`，无需安装。`portable.flag` 使阅读记录保存在程序旁的 `Data` 目录；请放在可写目录中。若移动程序目录，重新点击“关联 PDF”更新路径。

本版本尚未代码签名。

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

普通用户只需点击 **网页登录**，通过官方 Google 页面授权，无需输入 Client ID 或云盘密码到本程序。程序需要维护者预先完成 OAuth 应用注册，并随发行版提供应用配置。**当前发行版尚未完成应用注册，云盘同步暂不可使用，保留后续接入接口。** 参见 [开发者配置说明](CLOUD_SETUP.md)。

维护者完成注册后：云端书库 → 网页登录 → 上传当前书籍与进度。以后在其他电脑或重装系统后，使用同一个发行版应用身份和同一个云盘账户，登录 → 选择书籍 → 继续阅读。Google 备份位于应用隐藏数据文件夹。

同步采用手动一键上传，不会在后台自动上传私人文件。多设备以最后一次上传为准；不同内容的 PDF 视为不同版本，暂不合并冲突。修改文件后请先另存，再上传。加密 PDF 上传原始加密字节，不保存 PDF 密码；云端恢复后仍需输入密码。阅读进度和文件名没有额外加密。单次上传上限 200 MB，下载 PDF 解压上限 512 MB；云盘自身容量限制仍然适用。

安装版阅读记录保存在 `%LOCALAPPDATA%\Simple PDF reader\library.json`，绿色版保存在程序旁 `Data` 目录。云盘令牌存于系统凭据库，不随绿色版目录迁移；换电脑或重装需要重新网页登录。维护者需保持 OAuth 应用身份稳定，不能在更新版本时随意更换 Client ID。

## 当前边界

这是基础编辑器，不是 Acrobat 全功能替代品。添加文字是叠加内容，不能直接重排或修改原始段落；不含内置 OCR 引擎、证书数字签名、真正的内容涂黑删除、完整交互表单编辑。高亮是注释，不是涂黑。旋转或裁剪偏移页面暂不支持点击标记。扫描件查找需要 OCR。Office 转换不保证复杂文档与原应用排版完全一致。打印采用 150/300/600 DPI 栅格输出；没有专业印前、书册/海报、ICC 色彩管理。远程签署/协作入口仅说明本地版限制，未实现协作服务器。双页模式默认为第 1、2 页并列，不设独立封面。

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

## 单文件版本

单文件绿色 EXE 运行后在旁边生成 Data 目录；Google 凭据库仍在 Windows。HTML 文件内嵌 PDF.js 与 pdf-lib，无网络依赖或云盘功能。HTML 只能阅读密码 PDF，不能编辑加密文件；编辑以本地叠加为主，打印依赖浏览器原生 PDF 控件。浏览器数据清理会删除阅读库，请下载 PDF 副本。详见 VERSION_NOTES.md。
