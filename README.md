<div align="center">
  <img src="https://github.com/AghaErfan/Esh-Translator/blob/main/b004243d-1fb1-46e3-a02d-0b84a5cd9e5f.png" width="220" alt="ESH Logo">
  <h1>ESH Translator
   <p><strong>ترجمه سریع متون روی صفحه </strong></p>
  </h1>
  <p>
  </a>
  <a href="https://github.com/AghaErfan/Esh-Translator/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-2EA44F?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="MIT License">
  </a>
  <a href="https://www.python.org/downloads/release/python-3110/">
    <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11">
  </a>
  <a href="https://www.microsoft.com/windows">
    <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  </a>
  <a href="https://github.com/AghaErfan/Esh-Translator">
    <img src="https://img.shields.io/badge/Game-Overlay-FF4655?style=for-the-badge&logoColor=white" alt="Game Overlay">
  </a>
  <a href="https://github.com/AghaErfan/Esh-Translator">
    <img src="https://img.shields.io/badge/Language-Persian-00A86B?style=for-the-badge" alt="Persian Translation">
  </a>
  <a href="https://t.me/s04ial">
    <img src="https://img.shields.io/badge/Telegram-s04ial-229ED9?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  </a>
</p>
  </p>
</div>

---

##
<img src="https://github.com/AghaErfan/Esh-Translator/blob/main/ScreenShot.jpg" width="1070" height="651" alt="AboutSoftware" style="max-width:100%; height:auto;">
**ESH Translator** 
یک ابزار شناور برای ویندوز است که اجازه می‌دهد بخشی از صفحه، بازی یا برنامه را انتخاب کنید و تصویر آن را به فارسی ترجمه کنید؛ نتیجه به‌صورت پنجره‌ای شناور روی صفحه نمایش داده می‌شود.

### قابلیت‌ها

- انتخاب ناحیه با موس و میانبر قابل تنظیم.
- نمایش تصویر ترجمه‌شده به‌صورت پنجرهٔ شناور.
- جابه‌جایی و بزرگ‌نمایی/کوچک‌نمایی نتیجه؛ دابل‌کلیک برای کپی.
- انتخاب خودکار یا دستی مانیتور منبع تصویر.
- آیکون کنار ساعت ویندوز، پنل شناور و حالت پین.
- حالت کم‌مصرف برای کاهش فعالیت پس‌زمینه.
- تنظیم مسیر ذخیرهٔ تصاویر و اجرای خودکار با ورود به ویندوز.

### دریافت نسخهٔ آماده

نسخهٔ قابل نصب، وقتی منتشر شد، در صفحهٔ [Releases](../../releases) قرار می‌گیرد. نصب‌کننده برای اجرای برنامه به نصب جداگانهٔ Python نیاز ندارد، اما برای ترجمه به **Microsoft Edge WebView2 Runtime** و اتصال اینترنت نیاز است.

### پیش‌نیازها و دانلودهای رسمی

| مورد | برای چه کاری است؟ | لینک رسمی |
|---|---|---|
| Microsoft Edge WebView2 Runtime | میزبانی صفحهٔ ترجمه در برنامه؛ نصب‌کننده آن را در صورت نیاز نصب می‌کند | [دانلود WebView2](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) |
| Python 3.11 x64 | فقط برای اجرای سورس یا ساخت نسخهٔ ویندوز | [Python 3.11.16](https://www.python.org/downloads/release/python-31116/) |
| کتابخانه‌های ساخت | wxPython، Pillow، dxcam و PyInstaller | فایل [`requirements-build.txt`](requirements-build.txt) |

### میانبرهای پیش‌فرض

| کلید | عمل |
|---|---|
| `F3` | انتخاب ناحیه و شروع ترجمه |
| `F2` | بستن نتیجه |
| `Esc` | لغو انتخاب ناحیه (بسته به حالت فعلی برنامه) |

میانبرها از صفحهٔ تنظیمات قابل تغییرند.

### حریم خصوصی

برای ترجمه، تصویر ناحیهٔ انتخاب‌شده از طریق صفحهٔ Google Translate پردازش می‌شود؛ پس به اینترنت نیاز دارد. تصویرها یا متن‌های حساس و خصوصی را انتخاب نکنید. برنامه سرویس ترجمهٔ آفلاین محلی ارائه نمی‌کند.
* استفاده کنید.

---

## English

**ESH Translator** is a lightweight Windows overlay that lets you select a region of a game or app and translate the captured image into Persian. The translated image appears in a floating window over the original screen.

### Features

- Mouse-based region selection with configurable hotkeys.
- Floating translated-image result.
- Move and zoom the result; double-click to copy.
- Automatic or manual monitor selection.
- System-tray icon, floating panel, and pin mode.
- Performance mode to reduce background activity.
- Configurable image-save folder and launch-at-login option.

### Get the application

When published, end-user builds will be available in [GitHub Releases](../../releases). The packaged EXE does not require a separate Python installation. **WebView2 Runtime and an internet connection are required for translation.**

### Official prerequisites

| Component | Purpose | Official link |
|---|---|---|
| Microsoft Edge WebView2 Runtime | Hosts the translation page; the setup checks for it | [Download WebView2](https://developer.microsoft.com/en-us/microsoft-edge/webview2/) |
| Python 3.11 x64 | Source execution and Windows build only | [Python 3.11.16](https://www.python.org/downloads/release/python-31116/) |
| Inno Setup 6 | Builds the Setup installer; optional for EXE-only output | [Download Inno Setup](https://jrsoftware.org/isdl.php) |
| Build packages | wxPython, Pillow, dxcam, and PyInstaller | [`requirements-build.txt`](requirements-build.txt) |


### Default hotkeys

| Key | Action |
|---|---|
| `F3` | Select a region and translate |
| `F2` | Close the result |
| `Esc` | Cancel region selection, depending on the current state |

Hotkeys can be changed from the settings page.

### Privacy

The selected image is processed through Google Translate, so internet access is required. Do not select sensitive or private content. This project does not provide an offline local translation engine.

## Links
- Telegram: [t.me/s04ial](https://t.me/s04ial)
- WebView2 documentation: [Microsoft Learn](https://learn.microsoft.com/microsoft-edge/webview2/)
- PyInstaller documentation: [pyinstaller.org](https://pyinstaller.org/en/stable/)

> No license is declared in this repository yet. Add a `LICENSE` file before presenting the source as open-source software.
