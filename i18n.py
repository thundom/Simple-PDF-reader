"""Chinese source strings, English and Japanese desktop translations."""
import json
from library import DATA_DIR
LANGUAGES={'English':'en','简体中文':'zh','日本語':'ja'}
language='en'
try: language=json.loads((DATA_DIR/'preferences.json').read_text('utf-8')).get('language','en')
except (OSError,ValueError): pass
if language not in LANGUAGES.values(): language='en'
CATALOG={}
def rows(value):
    for row in value.strip().splitlines():
        zh,en,ja=(v.replace('\\n','\n') for v in row.split('|')); CATALOG[zh]=(en,ja)
rows(r'''
打开 PDF|Open PDF|PDF を開く
最近阅读|Recent files|最近のファイル
保存副本|Save a copy|コピーを保存
编辑工具|Edit PDF|PDF を編集
创建 PDF|Create PDF|PDF を作成
云端书库|Cloud library|クラウドライブラリ
关联 PDF|Associate PDF|PDF の関連付け
打印|Print|印刷
适应宽度|Fit width|幅に合わせる
未打开文件|No document open|ファイルが開かれていません
页面导航|Pages|ページ
你的私人 PDF 书库  ·  免费 / MIT|Your private PDF library · Free / MIT|プライベート PDF ライブラリ · 無料 / MIT
打开 PDF 开始阅读\n\n支持密码文件、页面编辑与本地转换|Open a PDF to start reading\n\nPassword PDFs, page tools and local conversion|PDF を開いて読書を開始\n\nパスワード PDF・ページ編集・ローカル変換
就绪 · 文件不会上传到服务器|Ready · Files stay local unless you upload to Drive|準備完了 · Drive にアップロードするまでローカルで処理
操作未完成|Operation failed|操作に失敗しました
请先打开 PDF|Open a PDF first|先に PDF を開いてください
单页|Single page|単一ページ
双页|Two pages|見開きページ
连续滚动|Continuous scrolling|連続スクロール
双页连续|Two-page scrolling|見開き連続スクロール
添加文字|Add text|テキストを追加
区域高亮|Highlight|ハイライト
旋转页面|Rotate page|ページを回転
删除页面|Delete page|ページを削除
撤销|Undo|元に戻す
合并文件|Combine files|ファイルを結合
提取页面|Extract pages|ページを抽出
分割 PDF|Split PDF|PDF を分割
加密 PDF|Protect PDF|PDF を保護
解密另存|Save decrypted copy|復号して保存
导出 PNG|Export PNG|PNG に書き出し
查找文字|Find text|テキストを検索
每页一个文件|One file per page|1 ページごとに分割
每 N 页一个文件|Every N pages|N ページごとに分割
自定义分段|Custom groups|カスタム範囲
选择目录并分割|Choose folder and split|フォルダーを選択して分割
选择分割文件保存目录|Select output folder|保存先フォルダーを選択
分割输出为未加密 PDF；原文件保留。|Split files are unencrypted; the source is preserved.|分割ファイルは暗号化されません。元のファイルは保持されます。
范围起始页不能大于结束页|Range start must not exceed its end|開始ページは終了ページ以下にしてください
页码超出范围|Page number out of range|ページ番号が範囲外です
N 至少为 1|N must be at least 1|N は 1 以上にしてください
打印 PDF|Print PDF|PDF を印刷
打印机|Printer|プリンター
份数|Copies|部数
未找到打印机，请先安装打印机驱动|No printers found. Install a printer driver first.|プリンターが見つかりません。ドライバーをインストールしてください。
份数必须在 1 到 99 之间|Copies must be between 1 and 99|部数は 1〜99 にしてください
打印任务已提交到打印机|Print job submitted|印刷ジョブを送信しました
未保存的修改|Unsaved changes|未保存の変更
放弃未保存的修改？|Discard unsaved changes?|未保存の変更を破棄しますか？
密码文件|Password-protected file|パスワード付きファイル
输入 PDF 密码：|PDF password:|PDF パスワード：
继续阅读|Continue reading|読書を続ける
云盘操作失败|Cloud operation failed|クラウド操作に失敗しました
云盘操作正在进行，请稍候|Cloud operation in progress. Please wait.|クラウド操作中です。お待ちください。
云盘操作进行中…|Working with Google Drive…|Google Drive 処理中…
私人云端书库|Private cloud library|プライベートクラウドライブラリ
在官方网页安全登录，将 PDF 与阅读位置备份到自己的云盘。|Sign in on Google's website to back up PDFs and reading progress.|Google の公式ページでログインし、PDF と読書位置をバックアップします。
云盘操作完成|Cloud operation complete|クラウド操作が完了しました
请先另存当前编辑版本，再同步；云端上传的是磁盘上已保存的 PDF|Save your edits before syncing. Drive receives the saved PDF.|同期する前に編集を保存してください。保存済み PDF がアップロードされます。
请先选择云端书籍|Select a cloud book first|クラウドの本を選択してください
网页登录|Sign in with browser|ブラウザーでログイン
刷新书库|Refresh library|ライブラリを更新
上传当前书籍与进度|Upload PDF and progress|PDF と読書位置をアップロード
退出登录|Sign out|ログアウト
已清除本机云盘令牌；撤销授权可到云盘账户设置完成|Local token removed. Revoke access in your Google account settings.|ローカルトークンを削除しました。アクセス権の取消は Google アカウント設定で行えます。
同步为手动一键上传；多设备以最后一次上传的进度为准。加密 PDF 保持原文件加密。|Sync manually with one click. Latest upload wins. Encrypted PDFs remain encrypted.|ワンクリックで手動同期。最新アップロードの読書位置が優先され、暗号化 PDF は暗号化のままです。
有未保存修改|Unsaved changes|未保存の変更あり
阅读进度自动保存|Reading progress saved automatically|読書位置を自動保存
已保存（未加密）；需要密码保护请使用“加密 PDF”|Saved unencrypted. Use Protect PDF for password protection.|暗号化せず保存しました。パスワード保護には「PDF を保護」を使用してください。
输入待合并 PDF 的密码：|Password for the PDF to combine:|結合する PDF のパスワード：
页码（例如 1,3,5），按输入顺序导出：|Pages (e.g. 1,3,5), exported in entered order:|ページ番号（例：1,3,5）。入力順に書き出します：
AES-256 加密|AES-256 encryption|AES-256 暗号化
新密码：|New password:|新しいパスワード：
确认密码|Confirm password|パスワードを確認
再次输入新密码：|Enter the new password again:|新しいパスワードを再入力：
两次密码不一致|Passwords do not match|パスワードが一致しません
已导出 AES-256 加密 PDF|AES-256 encrypted PDF exported|AES-256 暗号化 PDF を書き出しました
点击页面放置文字|Click the page to place text|ページをクリックしてテキストを配置
依次点击高亮区域的两个角|Click two corners of the highlight area|ハイライト領域の対角を順にクリック
文字（支持中文）：|Text:|テキスト：
再点击另一角完成高亮|Click the opposite corner to finish highlighting|もう一方の角をクリックしてハイライトを完成
高亮的两个角必须在同一页|Both highlight corners must be on the same page|ハイライトの両角は同じページにしてください
查找：|Find:|検索：
查找结果|Search results|検索結果
匹配页：|Matching pages: |一致するページ：
未找到文字；扫描 PDF 需要 OCR，本版本不含 OCR。|No matching text. Use OCR for scanned PDFs.|一致するテキストがありません。スキャン PDF には OCR を使用してください。
选择图片、文本或 Office 文件|Select an image, text or Office file|画像・テキスト・Office ファイルを選択
输出不能覆盖输入文件|Output cannot overwrite the input file|出力先を入力ファイルと同じにできません
正在转换…|Converting…|変換中…
PDF 文件关联|PDF file association|PDF ファイルの関連付け
文件关联|File association|ファイルの関連付け
工具|Tools|ツール
语言|Language|言語
上一页|Previous page|前のページ
下一页|Next page|次のページ
放大|Zoom in|拡大
缩小|Zoom out|縮小
页面显示|Page display|ページ表示
填写和签名|Fill & sign|入力と署名
注释|Comment|注釈
导出 PDF|Export PDF|PDF を書き出し
组织页面|Organize pages|ページを整理
扫描和 OCR|Scan & OCR|スキャンと OCR
保护|Protect|保護
更多工具|More tools|その他のツール
请求电子签名|Request e-signatures|電子署名を依頼
发送以供注释|Send for comments|コメント用に送信
手写签名|Draw signature|署名を描く
图片签名|Image signature|画像の署名
清除|Clear|消去
使用签名|Use signature|署名を使用
点击页面放置签名|Click the page to place your signature|ページをクリックして署名を配置
注释内容：|Comment:|注釈：
点击页面放置注释|Click the page to place a comment|ページをクリックして注釈を配置
高级协作|Online collaboration|オンライン共同作業
本地版不含远程签署、邮件通知或协作服务器。请保存 PDF 后使用自己的邮件或协作服务发送。|This local app has no remote signing, email notifications or collaboration server. Save the PDF and share it using your own email or service.|このローカル版にはリモート署名・メール通知・共同作業サーバーがありません。PDF を保存し、ご自身のメールやサービスで共有してください。
签名是可视图像，不是证书数字签名。|Signature is a visual image, not a certificate-based digital signature.|署名は画像であり、証明書付きデジタル署名ではありません。
纸张|Paper|用紙
方向|Orientation|向き
纵向|Portrait|縦
横向|Landscape|横
缩放|Scaling|倍率
适合|Fit|合わせる
实际大小|Actual size|実際のサイズ
缩小超大页面|Shrink oversized pages|大きいページを縮小
灰度打印|Grayscale|グレースケール
双面|Duplex|両面
单面|One-sided|片面
长边翻转|Long-edge binding|長辺とじ
短边翻转|Short-edge binding|短辺とじ
页码范围|Page range|ページ範囲
逆序|Reverse order|逆順
打印预览|Print preview|印刷プレビュー
当前页|Current page|現在のページ
所有页|All pages|すべてのページ
自定义|Custom|カスタム
驱动属性|Printer properties|プリンターのプロパティ
取消|Cancel|キャンセル
开始打印|Start printing|印刷開始
保存|Save|保存
导出文本|Export text|テキストを書き出し
请选择 PNG 或 UTF-8 文本导出格式。|Choose PNG or UTF-8 text export.|PNG または UTF-8 テキストを選択してください。
未找到 OCR 引擎。请安装免费 Tesseract 及所需语言包后重试。|OCR engine not found. Install free Tesseract and the required language data.|OCR エンジンが見つかりません。無料の Tesseract と必要な言語データをインストールしてください。
OCR 语言（例如 eng、chi_sim、jpn 或 eng+chi_sim）：|OCR languages (e.g. eng, chi_sim, jpn or eng+chi_sim):|OCR 言語（例：eng、chi_sim、jpn、eng+chi_sim）：
OCR 结果|OCR result|OCR 結果
保存文本|Save text|テキストを保存
奇数页|Odd pages|奇数ページ
偶数页|Even pages|偶数ページ
全部|All|すべて
页面筛选|Page filter|ページフィルター
打印期间请勿关闭程序。|Keep the app open while printing.|印刷中はアプリを閉じないでください。
不支持的页面|Unsupported page|未対応のページ
此页有旋转或裁剪偏移，请先另存并规范页面后再添加标记；页面管理仍可使用|This page has rotation or crop offsets. Normalize it before adding marks; page tools remain available.|回転・切り抜きオフセットのあるページです。マーク追加前に正規化してください。ページ管理は利用できます。
已在程序内注册 PDF 文件关联。可以从文件管理器打开 PDF。|PDF association registered. Open PDFs from File Explorer.|PDF の関連付けを登録しました。エクスプローラーから開けます。
已注册 Simple PDF reader 为 PDF 打开方式。\nWindows 当前已有默认 PDF 应用，首次切换仍需系统确认：右键 PDF → 打开方式 → 选择其他应用 → 始终使用。|Registered as a PDF handler.\nWindows has an existing default: right-click a PDF → Open with → Choose another app → Always.|PDF の候補アプリとして登録しました。\n既定の変更には Windows の確認が必要です：PDF を右クリック → プログラムから開く → 別のアプリ → 常に使用。
在系统文件管理器中选择 PDF → 打开方式 → Simple PDF reader。|Choose PDF → Open with → Simple PDF reader in your file manager.|ファイル管理で PDF → プログラムから開く → Simple PDF reader を選択してください。
输入 N 或分段页码，例如 1-3;4-6;7,9\n每页一个文件时无需填写。|Enter N or page groups, e.g. 1-3;4-6;7,9\nLeave blank for one file per page.|N または範囲を入力（例：1-3;4-6;7,9）\n1 ページごとの分割では入力不要です。
编辑工具  ·  第 {0} 页|Edit tools · Page {0}|編集ツール · {0} ページ
已保存 {0} 个分割文件|Saved {0} split files|分割ファイルを {0} 個保存しました
删除第 {0} 页？|Delete page {0}?|{0} ページを削除しますか？
  第 {0} 页|  Page {0}|  {0} ページ
第 {0} 页|Page {0}|{0} ページ
{0}  · 第 {1} 页|{0} · Page {1}|{0} · {1} ページ
{0} / {1} 页  ·  {2:.0%}|{0} / {1} · {2:.0%}|{0} / {1} · {2:.0%}
打印：第 {0} 页，副本 {1}/{2}|Printing page {0}, copy {1}/{2}|{0} ページを印刷中、{1}/{2} 部
''')

def tr(text):
    if language=='zh': return text
    pair=CATALOG.get(text)
    return pair[0 if language=='en' else 1] if pair else text

rows(r'''
每张纸页数|Pages per sheet|1 枚あたりのページ数
预览按 5 mm 边距估算；实际以打印机可打印区域为准。|Preview assumes 5 mm margins; printing uses the driver's printable area.|プレビューは余白 5 mm の目安です。実際の印刷はドライバーの印刷可能領域に従います。
LibreOffice 转换失败；检查文件是否损坏或受密码保护|LibreOffice conversion failed; check for corruption or password protection|LibreOffice 変換に失敗しました。破損やパスワード保護を確認してください
Office / HTML 转换需要先安装免费 LibreOffice|Install free LibreOffice for Office / HTML conversion|Office / HTML 変換には無料の LibreOffice が必要です
PDF 没有页面|PDF has no pages|PDF にページがありません
PDF 超过 512 MB 限制|PDF exceeds the 512 MB limit|PDF が 512 MB の上限を超えています
不支持此格式|Unsupported file format|未対応のファイル形式
云盘登录被取消或拒绝|Cloud sign-in was cancelled or denied|クラウドログインが取り消されたか拒否されました
云端文件不是有效的阅读备份|Cloud file is not a valid reading backup|クラウドファイルは有効な読書バックアップではありません
分割页码无效|Invalid split page range|分割ページ範囲が無効です
加密密码不能为空|Encryption password cannot be empty|暗号化パスワードを空にできません
单次同步限制 200 MB，请拆分大文件|Sync is limited to 200 MB per file. Split large PDFs.|同期は 1 ファイル 200 MB までです。大きい PDF は分割してください
备份校验失败|Backup integrity check failed|バックアップの整合性確認に失敗しました
密码错误或需要密码|Incorrect password or password required|パスワードが違うか、必要です
打印任务提交失败|Print job submission failed|印刷ジョブの送信に失敗しました
打印任务未启动或已取消|Print job did not start or was cancelled|印刷ジョブが開始されなかったか取り消されました
打印机无法开始新页|Printer could not start a page|プリンターが新しいページを開始できません
打印目前仅支持 Windows|Printing currently supports Windows only|印刷は現在 Windows のみ対応です
打印页面失败|Page printing failed|ページの印刷に失敗しました
文件关联目前仅支持 Windows|File association currently supports Windows only|ファイル関連付けは現在 Windows のみ対応です
无效的 PDF 文件名|Invalid PDF filename|PDF ファイル名が無効です
无效的登录回调|Invalid sign-in callback|ログインコールバックが無効です
无法连接打印机|Cannot connect to printer|プリンターに接続できません
此版本的开发者尚未完成云盘网页登录注册。完成注册并更新程序后即可点击登录，无需用户输入 ID。|This build has no registered Google OAuth client. Use a configured build; users do not need to enter an ID.|この版には Google OAuth クライアントが登録されていません。設定済み版をご利用ください。利用者の ID 入力は不要です
登录完成，可以关闭此页面。|Sign-in complete. You can close this page.|ログインが完了しました。このページを閉じてください
登录超时，请重试|Sign-in timed out. Try again.|ログインがタイムアウトしました。再試行してください
登录过期，请重新登录|Session expired. Sign in again.|セッションが期限切れです。再度ログインしてください
目标目录已有同名分割文件，请选择另一个目录|Split files already exist. Choose another folder.|同名の分割ファイルがあります。別のフォルダーを選択してください
至少保留一页|At least one page must remain|最低 1 ページは残してください
请先登录云盘|Sign in to Google Drive first|先に Google Drive にログインしてください
进度信息异常|Invalid progress information|読書位置情報が無効です
进度数据无效|Invalid progress data|読書位置データが無効です
阅读布局数据无效|Invalid reading layout data|読書レイアウトデータが無効です
云盘请求失败（HTTP {0}）；检查应用配置、权限和网络|Cloud request failed (HTTP {0}); check app settings, permissions and network|クラウド要求に失敗（HTTP {0}）。アプリ設定・権限・ネットワークを確認してください
填写表单|Fill form|フォームに入力
没有可填写的表单字段。可使用添加文字或签名工具。|No fillable form fields. Use Add text or Fill & sign.|入力可能なフィールドがありません。テキスト追加や署名ツールを使用してください
关于|About|情報
''')

def choose(code):
    global language
    language=code
    DATA_DIR.mkdir(parents=True,exist_ok=True)
    path=DATA_DIR/'preferences.json'
    try: settings=json.loads(path.read_text('utf-8'))
    except (OSError,ValueError): settings={}
    settings['language']=code
    path.write_text(json.dumps(settings),encoding='utf-8')

rows(r"""
文件|File|ファイル
编辑|Edit|編集
视图|View|表示
签名|Sign|署名
窗口|Window|ウィンドウ
帮助|Help|ヘルプ
主页|Home|ホーム
跳转页面|Go to page|ページへ移動
输入页码后按 Enter|Enter a page number, then press Enter|ページ番号を入力し Enter を押してください
重新打开上次文件|Reopen last file|最後のファイルを再度開く
关闭文件|Close document|文書を閉じる
文档属性|Document properties|文書のプロパティ
退出|Exit|終了
添加图片|Add image|画像を追加
首选项|Preferences|環境設定
第一页|First page|最初のページ
最后一页|Last page|最後のページ
显示／隐藏页面导航|Show / hide navigation|ナビゲーションを表示／非表示
显示／隐藏工具栏|Show / hide tools|ツールを表示／非表示
自定义快捷工具栏|Customize quick tools|クイックツールをカスタマイズ
全屏|Full screen|全画面表示
最小化|Minimize|最小化
快捷键|Keyboard shortcuts|キーボードショートカット
退出全屏|Exit full screen|全画面表示を終了
返回文档|Return to document|文書に戻る
文件名|Filename|ファイル名
页码|Page number|ページ番号
上次阅读|Last read|最終閲覧
位置|Location|場所
文件已移动或删除，请重新打开。|The file was moved or deleted. Open it again.|ファイルが移動または削除されました。再度開いてください。
移除记录|Remove from recent files|履歴から削除
双击文件继续阅读；文件和进度保存在本机。|Double-click to resume. Files and progress are stored locally.|ダブルクリックで再開します。ファイルと読書位置はローカルに保存されます。
点击页面放置图片|Click a page to place the image|ページをクリックして画像を配置
常规|General|一般
界面语言|Interface language|表示言語
新文件默认页面显示|Default layout for new files|新しいファイルの既定レイアウト
默认收起页面导航|Collapse navigation by default|ナビゲーションを既定で折りたたむ
默认收起工具栏|Collapse tools by default|ツールを既定で折りたたむ
快捷工具栏|Quick tools|クイックツール
选择顶部快捷工具栏显示的功能|Choose actions shown in the top toolbar|上部ツールバーに表示する機能を選択
高级|Advanced|詳細
阅读进度每 5 秒及关闭文档时保存。|Progress is saved every 5 seconds and when closing a document.|読書位置は 5 秒ごとおよび文書を閉じる際に保存されます。
数据目录|Data folder|データフォルダー
本地密码不保存；云盘仅在主动操作时连接。|PDF passwords are not stored. Drive connects only when you request it.|PDF パスワードは保存されません。Drive は操作時のみ接続します。
保存设置|Save preferences|設定を保存
描述|Description|概要
标题|Title|タイトル
作者|Author|作成者
主题|Subject|件名
关键词|Keywords|キーワード
文件大小|File size|ファイルサイズ
页数|Page count|ページ数
页面尺寸|Page size|ページサイズ
源文件未加密|Source file is not encrypted|元ファイルは暗号化されていません
源文件已加密|Source file is encrypted|元ファイルは暗号化されています
安全处理程序|Security handler|セキュリティハンドラー
密钥长度|Key length|キーの長さ
允许打印|Printing allowed|印刷を許可
允许修改|Modification allowed|変更を許可
允许复制|Copying allowed|コピーを許可
允许注释|Annotations allowed|注釈を許可
允许填写表单|Form filling allowed|フォーム入力を許可
辅助功能访问|Accessibility extraction allowed|アクセシビリティ抽出を許可
允许页面组装|Document assembly allowed|文書アセンブリを許可
允许高质量打印|High quality printing allowed|高品質印刷を許可
此处显示源文件声明的权限，不代表程序已强制执行全部权限。|These are permissions declared by the source PDF. The app does not enforce all of them.|元 PDF が宣言する権限です。本アプリはすべての権限を強制するものではありません。
编辑副本保存在内存中；普通另存为输出未加密文件，需用加密功能重新设置密码。|Edits are in memory. Normal Save a copy creates an unencrypted PDF; use Encrypt to protect the output.|編集はメモリ内で行われます。通常のコピー保存は暗号化されません。出力を保護するには暗号化を使用してください。
安全性|Security|セキュリティ
字体|Fonts|フォント
字体名称|Font name|フォント名
类型|Type|種類
编码|Encoding|エンコーディング
嵌入|Embedded|埋め込み
是|Yes|はい
否|No|いいえ
自定义|Custom|カスタム
自定义元数据（JSON 对象，键以 / 开头）|Custom metadata (JSON object, keys start with /)|カスタムメタデータ（JSON オブジェクト、キーは / で始まる）
页面布局|Page layout|ページレイアウト
页面模式|Page mode|ページモード
标签结构|Tagged structure|タグ構造
表单|Forms|フォーム
查看器首选项|Viewer preferences|ビューアー設定
当前页面旋转|Current page rotation|現在のページの回転
修改未保存|Unsaved changes|未保存の変更
元数据必须是键以 / 开头且值为字符串的 JSON 对象。|Metadata must be a JSON object with /-prefixed keys and string values.|メタデータは / で始まるキーと文字列値の JSON オブジェクトである必要があります。
应用元数据修改|Apply metadata changes|メタデータ変更を適用
""")
