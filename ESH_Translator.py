
"""
Translator — ابزار اسنیپ و ترجمه‌ی سبک (مخصوص بازی‌های Fullscreen)
=========================================================================

  F3   → صفحه کمی تیره می‌شود؛ ناحیه را با موس بکش → عکسِ همان ناحیه به «فارسی» ترجمه می‌شود
         و درست روی همان محل نمایش داده می‌شود (با یک متن ریز زیرش: اسکرول = زوم).
  Esc  → لغو انتخاب (یا دوباره F3).
  F2   → بستن نتیجه (عکسِ ذخیره‌شده‌ی آن هم برای همیشه پاک می‌شود).
  روی نتیجه: درگ = جابه‌جایی | چرخ موس = بزرگ/کوچک‌نمایی | دابل‌کلیک = کپی | راست‌کلیک یا ✕ = بستن
  پنل شناور: با هر اجرا خودکار بالا-راستِ صفحه می‌آید؛ کنار دکمه‌های ترجمه/بستن یک دکمه‌ی کلید هست:
  کلیک کن و هر کلیدی بزنی همان ثبت می‌شود (در AppData ذخیره می‌شود و همیشه همان بالا می‌آید).
  آیکون کنار ساعت ویندوز (Tray) — راست‌کلیک:
      شروع با اجرای ویندوز  |  نمایش پنل شناور  |  تنظیمات  |  خروج
  تنظیمات داخل همان پنل شناور باز می‌شود. با مخفی‌کردن پنل، پیام ثابتی بالای ساعت باقی می‌ماند.
  خروج کامل: فرایند بسته می‌شود و پوشه‌ی مخصوص عکس‌ها که در تنظیمات تعیین شده، بازگشتی حذف می‌شود.

زبان ترجمه همیشه فارسی است. برنامه همیشه با دسترسی ادمین شروع می‌شود تا کلیدها روی بازی‌های ادمین هم کار کنند.
بازی فول‌اسکرین: عکس با DXGI (کتابخانه‌ی dxcam) گرفته می‌شود، نه GDI، پس سیاه/خالی نمی‌افتد.

نکته‌ی فنی: هیچ پنجره‌ای فوکوس را از بازی نمی‌گیرد (WS_EX_NOACTIVATE) و کلیدها با
RegisterHotKey ویندوز ثبت می‌شوند (بدون هوکِ صفحه‌کلید، بدون نخِ پس‌زمینه، بدون لگ).

نصب خودکار: wxPython و pillow و dxcam  |  نیاز: Microsoft Edge WebView2 Runtime
تنظیمات: %APPDATA%\\42OCR\\config.json  (snip_hotkey / close_hotkey / auto_close_seconds / save_dir / run_on_startup)
"""

import base64
import ctypes
import ctypes.wintypes
import hashlib
import io
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import threading
import time




try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass





def _msg(text, flags=0x40):
    try:
        ctypes.windll.user32.MessageBoxW(None, str(text), "Translator", flags)
    except Exception:
        pass


def _hard_exit(code=0):
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except Exception:
        pass
    os._exit(code)


def dbg(msg):
    """لاگ عیب‌یابی: %APPDATA%\\42OCR\\debug.log (اگر بزرگ شد پاک می‌شود)."""
    try:
        d = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "42OCR")
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "debug.log")
        if os.path.exists(p) and os.path.getsize(p) > 300000:
            os.remove(p)
        with open(p, "a", encoding="utf-8") as f:
            f.write("%s  %s\n" % (time.strftime("%H:%M:%S"), msg))
    except Exception:
        pass


def _restart():
    try:
        os.execv(sys.executable, [sys.executable] + list(sys.argv))
    except Exception:
        import subprocess
        try:
            subprocess.Popen([sys.executable] + list(sys.argv))
        except Exception:
            pass
        sys.exit(0)


def _bootstrap():
    if getattr(sys, "frozen", False) or os.environ.get("42OCR_BOOT") == "1":
        return
    import importlib.util
    need = []
    for mod, pkg in (("wx", "wxPython"), ("PIL", "pillow")):
        try:
            if importlib.util.find_spec(mod) is None:
                need.append(pkg)
        except Exception:
            need.append(pkg)
    if not need:
        return
    os.environ["42OCR_BOOT"] = "1"
    _msg("در حال نصب پیش‌نیازها:\n%s\n\nچند لحظه صبر کنید…" % "\n".join(need))
    import subprocess
    for extra in (["--user", "--upgrade"], ["--upgrade"]):
        try:
            if subprocess.call([sys.executable, "-m", "pip", "install"] + extra + need) == 0:
                _restart()
                return
        except Exception:
            pass
    _msg("نصب خودکار نشد. دستی اجرا کنید:\npip install " + " ".join(need), 0x30)


WEBVIEW2_GUID = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
WEBVIEW2_URL = "https://go.microsoft.com/fwlink/p/?LinkId=2124703"


def _webview2_installed():
    try:
        import winreg
    except Exception:
        return False
    for hive, path in (
        (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Microsoft\\EdgeUpdate\\Clients\\" + WEBVIEW2_GUID),
        (winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\EdgeUpdate\\Clients\\" + WEBVIEW2_GUID),
        (winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\EdgeUpdate\\Clients\\" + WEBVIEW2_GUID),
    ):
        try:
            with winreg.OpenKey(hive, path) as k:
                v = str(winreg.QueryValueEx(k, "pv")[0] or "").strip()
            if v and v != "0.0.0.0":
                return True
        except Exception:
            continue
    return False


def _ensure_webview2():
    if _webview2_installed() or os.environ.get("42OCR_WV2") == "1":
        return
    os.environ["42OCR_WV2"] = "1"
    _msg("پیش‌نیاز ویندوزی (Microsoft Edge WebView2) نصب نیست.\nدر حال دانلود و نصب خودکار…")
    try:
        import subprocess
        import urllib.request
        path = os.path.join(tempfile.gettempdir(), "MicrosoftEdgeWebview2Setup.exe")
        req = urllib.request.Request(WEBVIEW2_URL, headers={"User-Agent": "42Snip"})
        with urllib.request.urlopen(req, timeout=90) as r, open(path, "wb") as f:
            shutil.copyfileobj(r, f)
        subprocess.call([path, "/silent", "/install"],
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception:
        pass
    if _webview2_installed():
        _restart()
    else:
        _msg("نصب خودکار WebView2 انجام نشد:\n" + WEBVIEW2_URL, 0x30)


def _optional_dxcam():
    """dxcam (گرفتن عکس با DXGI برای بازی‌های تمام‌صفحه). نصب‌نشدنش برنامه را از کار نمی‌اندازد."""
    if getattr(sys, "frozen", False):
        return
    import importlib
    import importlib.util
    try:
        if importlib.util.find_spec("dxcam") is not None:
            return
    except Exception:
        return
    d = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "42OCR")
    marker = os.path.join(d, "dxcam_tried")
    if os.path.exists(marker):
        return                                  
    try:
        os.makedirs(d, exist_ok=True)
        open(marker, "w").close()
    except Exception:
        pass
    _msg("در حال نصب کتابخانه‌ی عکس‌گرفتن از بازی (dxcam)…\nچند لحظه صبر کنید.")
    try:
        import subprocess
        subprocess.call([sys.executable, "-m", "pip", "install", "--user", "dxcam"])
        importlib.invalidate_caches()
    except Exception:
        pass


_bootstrap()
_optional_dxcam()
_ensure_webview2()

import wx                       
import wx.adv                   
import wx.html2                 
from PIL import Image, ImageDraw, ImageGrab   

UI_FONT_FACE = "Segoe UI"


ABOUT_IMAGE_B64 = (
    '/9j/4Q3FRXhpZgAATU0AKgAAAAgABwESAAMAAAABAAEAAAEaAAUAAAABAAAAYgEbAAUAAAABAAAAagEoAAMAAAABAAIAAAExAAIA'
    'AAAgAAAAcgEyAAIAAAAUAAAAkodpAAQAAAABAAAAqAAAANQAEk+AAAAnEAAST4AAACcQQWRvYmUgUGhvdG9zaG9wIDI3LjExIChX'
    'aW5kb3dzKQAyMDI2OjEwOjIwIDEwOjU2OjE0AAAAAAOgAQADAAAAAf//AACgAgAEAAAAAQAAAkegAwAEAAAAAQAAARUAAAAAAAAA'
    'BgEDAAMAAAABAAYAAAEaAAUAAAABAAABIgEbAAUAAAABAAABKgEoAAMAAAABAAIAAAIBAAQAAAABAAABMgICAAQAAAABAAAMiwAA'
    'AAAAAABIAAAAAQAAAEgAAAAB/9j/7QAMQWRvYmVfQ00AAv/uAA5BZG9iZQBkgAAAAAH/2wCEAAwICAgJCAwJCQwRCwoLERUPDAwP'
    'FRgTExUTExgRDAwMDAwMEQwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwBDQsLDQ4NEA4OEBQODg4UFA4ODg4UEQwMDAwMEREM'
    'DAwMDAwRDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDP/AABEIAEwAoAMBIgACEQEDEQH/3QAEAAr/xAE/AAABBQEBAQEBAQAA'
    'AAAAAAADAAECBAUGBwgJCgsBAAEFAQEBAQEBAAAAAAAAAAEAAgMEBQYHCAkKCxAAAQQBAwIEAgUHBggFAwwzAQACEQMEIRIxBUFR'
    'YRMicYEyBhSRobFCIyQVUsFiMzRygtFDByWSU/Dh8WNzNRaisoMmRJNUZEXCo3Q2F9JV4mXys4TD03Xj80YnlKSFtJXE1OT0pbXF'
    '1eX1VmZ2hpamtsbW5vY3R1dnd4eXp7fH1+f3EQACAgECBAQDBAUGBwcGBTUBAAIRAyExEgRBUWFxIhMFMoGRFKGxQiPBUtHwMyRi'
    '4XKCkkNTFWNzNPElBhaisoMHJjXC0kSTVKMXZEVVNnRl4vKzhMPTdePzRpSkhbSVxNTk9KW1xdXl9VZmdoaWprbG1ub2JzdHV2d3'
    'h5ent8f/2gAMAwEAAhEDEQA/APN0kkk5CklOii/Js9LGqffb+5U1z3f5tYcrrvq79YWs3u6Xlhvj6Lj/ANEDckpz0k72urea7Gll'
    'jfpMcC1w+LXQ5MkpSSSSSlJJJJKUkkkkpSSSSSlJJJJKUkkkkpSSSSSn/9DzddX9U/qaOpVt6j1TczBd/MUtO190GC9z/pVY39X9'
    'Jd/g/wDSLE6B0v8Aa/WMbp7iRVa4uvcORVWPVvj+U5jdjF662sNaGsAYxoDWMboGtaNrGNH7rG+1EqY4uPj4dAxsOpmNQOKqgGt+'
    'e36bv5b0TadIGrp2+Jj6W395O0agcT3XC9T+rWd1bPyuvdR6rV0quq99WGXyHV10vdXiyd9X2fd6fqV/4W3+k/4RBT13UumYHVKT'
    'V1ChuS381ztHt86r2/pa/wDOXmv1l+rN/Q7mva43YFzttN7o3B30vQv2+31dv0H/AOH/AM+tdr9Weu5+XmZnROr7H9RwAHjKq+hd'
    'VLG+qYDW73erVbXa3+k02f8Abux1DpmN1PDuwcn+byG7C7u13+Dub/Lps/SI2p8YSRxg5Zz/ANmhm7M9b7KKgQJt3+hs3OhvutW3'
    'b9UGMzK8JnVsa/JF1mLlU113usptqrtvtLcYVfaMvFb6Hp/a6K/TYih51Jblf1K+sb8d932Ui1tFOXVigOfdbVe/0muoZU13vo+n'
    'k127H01qtgfVzrGdk49DceyhmSaduRaxwqa3Jc6rEusc0O21ZFrH11fy0lOYkrWZ0zqOFmNwcrGtqyXkelU5jg6wOca630Mc3fay'
    '17dte1H/AObn1h+0vxP2XlnJrrFz6RS8uFbp22QB9FzmPY3/AIRnppKc5JaOP9W/rFlU1343S8u6m4B1VrKnFjmkb2va/wDd2q50'
    'r6n9T6oa2V21Y1tjLLPTyd9cbbvsFNLnbdv2jLy25FNFP/dW5JThJLQwegdYzhiW1YlzMTNuroqzX1v9AOsezGY6y5rTtr9az0//'
    'AD2i2/Vb6xV5mRhM6dk3240ueaqnlpZufXXfXua1zqch1Nv2f/TbElOUkt6/6m9To6ZjdQNrLRnVU24tFNWTYXfaC1lGO/JZj/Yq'
    'sne7Z6VmQo431Q6w/FzcnMps6e3Cra4MvouLrHPbZbXWz0q3+kzZQ9rr7fZ676KP5y1JLhpLR/5t/WL1xjfsvL9dzBYKvSdu2Ehn'
    'qbf3Gvdsf/o/8IqFldlVj6rWOrtrcWWVvBa5rmna9j2O+i9jkkP/0cL/ABbBv7cynH6TMN23+1bS13/RXosheTfVTqTendcotedt'
    'V4dj2HwFkem7+zc2pel1ZIfx25RKm9IXNdYu6ezNzGHp1WSwuZb1B11prL7KqvtLPRDj6FfoYz2P9W70PX/mqftFiyvrj9bc7Eyn'
    'dN6da7Gbj7ftOTXpYXubv9Fhd9Clm76TP5399c/h9fxDkWu+stWR1anIY1rXHIsa9vpue5jHbXtbdT7/AKFn81/gv5YU9z9XczBz'
    'MjK6xV6WLiWFvTsN1zwyyxtArt9nqPDHMc+z6H87/NrfdYwN3AhzTMOaQRp/KavFOrdTq6lmi2nGZhYtTBTjYtera2Nkhu8jdbY+'
    'x9lttrv5y2xdP9UqOv8ASRY59O7ByWguxH2it+7TZkVtcHenbt9v6X0/Ur/62nQxzmajEyrsGPLmxYgDknHGDoOM8NuX9Zrtv1oz'
    '78ZxY5uQLWPboW2AMs3j+U21WnfXrrxc11foU7bX5Lgxj9rr7a7sW/Jcyy17a33V5VzrK8f0aPW/Tel6iyeqjJHUsl2VW6m6y11h'
    'rdyA4yz3ate3Z+e1VUiK0I1C8EEAggg6gjYuzT9bOpUCgVVYzXUfZdz9jt1v2E1OwftDjZ/gm0Mq/Q+lvr3olP1063TTRSwUfq/o'
    'AWFji57cS2zLwq7f0np7KLr7f5uuuy3/AAr1hJJKdb/nNnt9L0KMWj7KKW4RbVvOP9nsdlsOLbkvvuZ6973/AGvfZZ9oZ+i/m0av'
    '64dSps3U4+LVUDXYMdrbTWL6rbc2nNb6mQ+312ZGRb+j9X7I/wDm34yw0kkuzX9buuVta1tlZ2tx2yWan7Je/qOM53u+l9qtf6n8'
    'hEp+uv1gx77MjFtZj2XPqst2NkONRss2Fry5vpXZGRkZVzP9Pd/OLCkDnvomJA5IHxSU9a/660N6dWaMU/tdraGDIe1orqGPl/tV'
    'tVPp2/pcT1WVtpx34tV9P+EzMhZ+D9cer4PofZ68bfjV11U2OqJc1tT7r2NDt/5z8qz1Gf8AFrCJA0JATyIknTxSU7P/ADpzSMVz'
    'sXFdlYLKWY2WRd6jRjO9TFLmNyG4lr63fnXYz0Cv6wdQY3Ia8V3NysirJsbc0vaHUPsyKqWVuds+yusyLvUoWakkh28z649azGCu'
    '30G1NkNrYwhoDsinqRa0b/8AuTjV/wDWf0Sys3Ktzc3IzboF2XbZfaGiG77HG1+wGfbucgpJKf/S83IBEHgrrem/WbJ6hifs+2lt'
    '/Uv0VWNYXAOuc6yjHrZ7w53q7HPfdtXJJJyHrvrv9U8LBpfn4uVY/Jtf78R7d5e463XUOZ+kx62+6x7LG/yPVXJ5fSuqYuKx+Xh3'
    '47Gv2tddU9gJeNzGNdY1vv8AY963um/Xn6wdPG02MyxoN2QCbYHb7XU6vId/119qt5P+MK7Jxn05fSsTKa7UtuLnsMag+ntZ7v6t'
    'iFJed+reKX9bpD6zY2kl74G4BzQSzfH/AAu1es/V3A6Lmub9rte7ILg00WEVAkjd+j2uNt/+fV/xax+kYeL6D3moY+PXU3KyKcFg'
    'BcXmuv8AQtuc/wDR1+rvdbc6306WJusU14tLrqg5zDjHLpbeA2wN/SH079nt93o/TZ/OV+mtHFAwxHHxmMj6pSj00+VyeYrLmGYw'
    'GQRHBHHP5Zer5v8ACef+uz8a70L62hjnW3CpoHFR94Z/Urc5i5ZHzc/Iz7vXyCJiGNaIa1vOxgQFUz5BPJKURQNV9PS3uUwyw4I4'
    '5m5DiJr5fXIz4Y/3eJSZ07THMaJ0lEzvU9Uw/qnb1fDuxMrFxulgYbb6G22vutY51dObc7bS1mNfQz1PX91dluz7Vs9S1Qub9Rbc'
    'cNrbbh2Pa17rhkOvdXsym4llTMd9NbbX5HTTZ1Hd/wBt1rmUkEvYXV/U7EzWuwbicXLDMLKqdcxzmVWX7n5deTuu2erg4W3J/wBD'
    '9u/7S/4HT6L1P6odJsyqsXLoqx3XVXZgsabDfhnGdXkdJq9X7ay6xvUf0llTMiyv0rf6VZsXniSVKe46T1T6rU9H6TjszX4hws/E'
    'ybGPoYLfVY237dlWX77d+P8Ap2Mpf6H6NmFRjen+k9dR6G76ldPt6Pn25Fbs2uxj84uebay26rIF++hzGNq+zX+j7WUfo/8Aux/O'
    'riUkqUxYCGAHmNVJJJFCkkkklP8A/9PzdLhJJOQpJJJJT0XRvrSzFx2Y2aLB6TTXXfVqTWRs9G5kt/M/R/y603XPrQM6mzHxfUIv'
    'AbfkXfTc0AD0q27nu+i3Zvf/AIP9GueSVq+Y9uq04d9OPgalct7l36uLbXg41JJJKq21JJJJKUkkkkpSSSSSlJJJJKUkkkkpSSSS'
    'Sn//2f/tFgJQaG90b3Nob3AgMy4wADhCSU0EJQAAAAAAEAAAAAAAAAAAAAAAAAAAAAA4QklNBDoAAAAAAOUAAAAQAAAAAQAAAAAA'
    'C3ByaW50T3V0cHV0AAAABQAAAABQc3RTYm9vbAEAAAAASW50ZWVudW0AAAAASW50ZQAAAABDbHJtAAAAD3ByaW50U2l4dGVlbkJp'
    'dGJvb2wAAAAAC3ByaW50ZXJOYW1lVEVYVAAAAAEAAAAAAA9wcmludFByb29mU2V0dXBPYmpjAAAADABQAHIAbwBvAGYAIABTAGUA'
    'dAB1AHAAAAAAAApwcm9vZlNldHVwAAAAAQAAAABCbHRuZW51bQAAAAxidWlsdGluUHJvb2YAAAAJcHJvb2ZDTVlLADhCSU0EOwAA'
    'AAACLQAAABAAAAABAAAAAAAScHJpbnRPdXRwdXRPcHRpb25zAAAAFwAAAABDcHRuYm9vbAAAAAAAQ2xicmJvb2wAAAAAAFJnc01i'
    'b29sAAAAAABDcm5DYm9vbAAAAAAAQ250Q2Jvb2wAAAAAAExibHNib29sAAAAAABOZ3R2Ym9vbAAAAAAARW1sRGJvb2wAAAAAAElu'
    'dHJib29sAAAAAABCY2tnT2JqYwAAAAEAAAAAAABSR0JDAAAAAwAAAABSZCAgZG91YkBv4AAAAAAAAAAAAEdybiBkb3ViQG/gAAAA'
    'AAAAAAAAQmwgIGRvdWJAb+AAAAAAAAAAAABCcmRUVW50RiNSbHQAAAAAAAAAAAAAAABCbGQgVW50RiNSbHQAAAAAAAAAAAAAAABS'
    'c2x0VW50RiNQeGxAXgAAAAAAAAAAAAp2ZWN0b3JEYXRhYm9vbAEAAAAAUGdQc2VudW0AAAAAUGdQcwAAAABQZ1BDAAAAAExlZnRV'
    'bnRGI1JsdAAAAAAAAAAAAAAAAFRvcCBVbnRGI1JsdAAAAAAAAAAAAAAAAFNjbCBVbnRGI1ByY0BZAAAAAAAAAAAAEGNyb3BXaGVu'
    'UHJpbnRpbmdib29sAAAAAA5jcm9wUmVjdEJvdHRvbWxvbmcAAAAAAAAADGNyb3BSZWN0TGVmdGxvbmcAAAAAAAAADWNyb3BSZWN0'
    'UmlnaHRsb25nAAAAAAAAAAtjcm9wUmVjdFRvcGxvbmcAAAAAADhCSU0D7QAAAAAAEAB4AAAAAQACAHgAAAABAAI4QklNBCYAAAAA'
    'AA4AAAAAAAAAAAAAP4AAADhCSU0EDQAAAAAABAAAAFo4QklNBBkAAAAAAAQAAAAeOEJJTQPzAAAAAAAJAAAAAAAAAAABADhCSU0n'
    'EAAAAAAACgABAAAAAAAAAAI4QklNA/UAAAAAAEgAL2ZmAAEAbGZmAAYAAAAAAAEAL2ZmAAEAoZmaAAYAAAAAAAEAMgAAAAEAWgAA'
    'AAYAAAAAAAEANQAAAAEALQAAAAYAAAAAAAE4QklNA/gAAAAAAHAAAP////////////////////////////8D6AAAAAD/////////'
    '////////////////////A+gAAAAA/////////////////////////////wPoAAAAAP////////////////////////////8D6AAA'
    'OEJJTQQAAAAAAAACAAM4QklNBAIAAAAAAAoAAAAAAAAAAAAAOEJJTQQwAAAAAAAFAQEBAQEAOEJJTQQtAAAAAAAGAAEAAAAKOEJJ'
    'TQQIAAAAAAAQAAAAAQAAAkAAAAJAAAAAADhCSU0ERAAAAAAAEAAAAAIAAAJAAAACQAAAAAA4QklNBEkAAAAAAAQAAAAAOEJJTQQe'
    'AAAAAAAEAAAAADhCSU0EGgAAAAADSQAAAAYAAAAAAAAAAAAAARUAAAJHAAAACgBVAG4AdABpAHQAbABlAGQALQAxAAAAAQAAAAAA'
    'AAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAJHAAABFQAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAABAAAAABAAAA'
    'AAAAbnVsbAAAAAIAAAAGYm91bmRzT2JqYwAAAAEAAAAAAABSY3QxAAAABAAAAABUb3AgbG9uZwAAAAAAAAAATGVmdGxvbmcAAAAA'
    'AAAAAEJ0b21sb25nAAABFQAAAABSZ2h0bG9uZwAAAkcAAAAGc2xpY2VzVmxMcwAAAAFPYmpjAAAAAQAAAAAABXNsaWNlAAAAEgAA'
    'AAdzbGljZUlEbG9uZwAAAAAAAAAHZ3JvdXBJRGxvbmcAAAAAAAAABm9yaWdpbmVudW0AAAAMRVNsaWNlT3JpZ2luAAAADWF1dG9H'
    'ZW5lcmF0ZWQAAAAAVHlwZWVudW0AAAAKRVNsaWNlVHlwZQAAAABJbWcgAAAABmJvdW5kc09iamMAAAABAAAAAAAAUmN0MQAAAAQA'
    'AAAAVG9wIGxvbmcAAAAAAAAAAExlZnRsb25nAAAAAAAAAABCdG9tbG9uZwAAARUAAAAAUmdodGxvbmcAAAJHAAAAA3VybFRFWFQA'
    'AAABAAAAAAAAbnVsbFRFWFQAAAABAAAAAAAATXNnZVRFWFQAAAABAAAAAAAGYWx0VGFnVEVYVAAAAAEAAAAAAA5jZWxsVGV4dElz'
    'SFRNTGJvb2wBAAAACGNlbGxUZXh0VEVYVAAAAAEAAAAAAAlob3J6QWxpZ25lbnVtAAAAD0VTbGljZUhvcnpBbGlnbgAAAAdkZWZh'
    'dWx0AAAACXZlcnRBbGlnbmVudW0AAAAPRVNsaWNlVmVydEFsaWduAAAAB2RlZmF1bHQAAAALYmdDb2xvclR5cGVlbnVtAAAAEUVT'
    'bGljZUJHQ29sb3JUeXBlAAAAAE5vbmUAAAAJdG9wT3V0c2V0bG9uZwAAAAAAAAAKbGVmdE91dHNldGxvbmcAAAAAAAAADGJvdHRv'
    'bU91dHNldGxvbmcAAAAAAAAAC3JpZ2h0T3V0c2V0bG9uZwAAAAAAOEJJTQQoAAAAAAAMAAAAAj/wAAAAAAAAOEJJTQQRAAAAAAAB'
    'AQA4QklNBBQAAAAAAAQAAAAKOEJJTQQMAAAAAAynAAAAAQAAAKAAAABMAAAB4AAAjoAAAAyLABgAAf/Y/+0ADEFkb2JlX0NNAAL/'
    '7gAOQWRvYmUAZIAAAAAB/9sAhAAMCAgICQgMCQkMEQsKCxEVDwwMDxUYExMVExMYEQwMDAwMDBEMDAwMDAwMDAwMDAwMDAwMDAwM'
    'DAwMDAwMDAwMAQ0LCw0ODRAODhAUDg4OFBQODg4OFBEMDAwMDBERDAwMDAwMEQwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/'
    'wAARCABMAKADASIAAhEBAxEB/90ABAAK/8QBPwAAAQUBAQEBAQEAAAAAAAAAAwABAgQFBgcICQoLAQABBQEBAQEBAQAAAAAAAAAB'
    'AAIDBAUGBwgJCgsQAAEEAQMCBAIFBwYIBQMMMwEAAhEDBCESMQVBUWETInGBMgYUkaGxQiMkFVLBYjM0coLRQwclklPw4fFjczUW'
    'orKDJkSTVGRFwqN0NhfSVeJl8rOEw9N14/NGJ5SkhbSVxNTk9KW1xdXl9VZmdoaWprbG1ub2N0dXZ3eHl6e3x9fn9xEAAgIBAgQE'
    'AwQFBgcHBgU1AQACEQMhMRIEQVFhcSITBTKBkRShsUIjwVLR8DMkYuFygpJDUxVjczTxJQYWorKDByY1wtJEk1SjF2RFVTZ0ZeLy'
    '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'
    'pXLe5d+ri214ONSSSSqttSSSSSlJJJJKUkkkkpSSSSSlJJJJKUkkkkp//9kAOEJJTQQhAAAAAABXAAAAAQEAAAAPAEEAZABvAGIA'
    'ZQAgAFAAaABvAHQAbwBzAGgAbwBwAAAAFABBAGQAbwBiAGUAIABQAGgAbwB0AG8AcwBoAG8AcAAgADIAMAAyADYAAAABADhCSU0E'
    'BgAAAAAABwAEAAAAAQEA/+EOlWh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8APD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJX'
    'NU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRv'
    'YmUgWE1QIENvcmUgMTAuMC1jMDAwIDc5LjQzMzJhYWUsIDIwMjYvMDgvMTctMTM6Mzk6NDMgICAgICAgICI+IDxyZGY6UkRGIHht'
    'bG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+IDxyZGY6RGVzY3JpcHRpb24gcmRm'
    'OmFib3V0PSIiIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5h'
    'ZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3Vy'
    'Y2VFdmVudCMiIHhtbG5zOnBob3Rvc2hvcD0iaHR0cDovL25zLmFkb2JlLmNvbS9waG90b3Nob3AvMS4wLyIgeG1sbnM6ZGM9Imh0'
    'dHA6Ly9wdXJsLm9yZy9kYy9lbGVtZW50cy8xLjEvIiB4bXA6Q3JlYXRvclRvb2w9IkFkb2JlIFBob3Rvc2hvcCAyNy4xMSAoV2lu'
    'ZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDI2LTEwLTIwVDEwOjU2OjE0KzAzOjMwIiB4bXA6TWV0YWRhdGFEYXRlPSIyMDI2LTEw'
    'LTIwVDEwOjU2OjE0KzAzOjMwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyNi0xMC0yMFQxMDo1NjoxNCswMzozMCIgeG1wTU06SW5zdGFu'
    'Y2VJRD0ieG1wLmlpZDo2YmZmYzEwMi1kOGFiLTU2NDUtYTNiNC0yMDk1MGUyMDM2ODEiIHhtcE1NOkRvY3VtZW50SUQ9ImFkb2Jl'
    'OmRvY2lkOnBob3Rvc2hvcDo5OGNhNzI2Yy1hNGMyLTUxNGYtYWRiNi1hM2EyNGJiOTcyMWYiIHhtcE1NOk9yaWdpbmFsRG9jdW1l'
    'bnRJRD0ieG1wLmRpZDplNzQxYjg1NS1kMDQzLWE3NDEtODRmOS1lYjgwYTMzMzg4MmEiIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMi'
    'IGRjOmZvcm1hdD0iaW1hZ2UvanBlZyI+IDx4bXBNTTpIaXN0b3J5PiA8cmRmOlNlcT4gPHJkZjpsaSBzdEV2dDphY3Rpb249ImNy'
    'ZWF0ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6ZTc0MWI4NTUtZDA0My1hNzQxLTg0ZjktZWI4MGEzMzM4ODJhIiBzdEV2'
    'dDp3aGVuPSIyMDI2LTEwLTIwVDEwOjU2OjE0KzAzOjMwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgMjcu'
    'MTEgKFdpbmRvd3MpIi8+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJzYXZlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDo2YmZm'
    'YzEwMi1kOGFiLTU2NDUtYTNiNC0yMDk1MGUyMDM2ODEiIHN0RXZ0OndoZW49IjIwMjYtMTAtMjBUMTA6NTY6MTQrMDM6MzAiIHN0'
    'RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCAyNy4xMSAoV2luZG93cykiIHN0RXZ0OmNoYW5nZWQ9Ii8iLz4gPC9y'
    'ZGY6U2VxPiA8L3htcE1NOkhpc3Rvcnk+IDxwaG90b3Nob3A6VGV4dExheWVycz4gPHJkZjpCYWc+IDxyZGY6bGkgcGhvdG9zaG9w'
    'OkxheWVyTmFtZT0iR2l0aHViLmNvbS9BZ2hhRXJmYW4gIHQubWUvczA0aWFsIiBwaG90b3Nob3A6TGF5ZXJUZXh0PSJHaXRodWIu'
    'Y29tL0FnaGFFcmZhbiAgdC5tZS9zMDRpYWwiLz4gPC9yZGY6QmFnPiA8L3Bob3Rvc2hvcDpUZXh0TGF5ZXJzPiA8L3JkZjpEZXNj'
    'cmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg'
    'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8P3hwYWNrZXQgZW5kPSJ3Ij8+'
    '/+4ADkFkb2JlAGQAAAAAAf/bAIQABgQEBAUEBgUFBgkGBQYJCwgGBggLDAoKCwoKDBAMDAwMDAwQDAwMDAwMDAwMDAwMDAwMDAwM'
    'DAwMDAwMDAwMDAEHBwcNDA0YEBAYFA4ODhQUDg4ODhQRDAwMDAwREQwMDAwMDBEMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwM'
    '/8AAEQgBFQJHAwERAAIRAQMRAf/dAAQASf/EAaIAAAAHAQEBAQEAAAAAAAAAAAQFAwIGAQAHCAkKCwEAAgIDAQEBAQEAAAAAAAAA'
    'AQACAwQFBgcICQoLEAACAQMDAgQCBgcDBAIGAnMBAgMRBAAFIRIxQVEGE2EicYEUMpGhBxWxQiPBUtHhMxZi8CRygvElQzRTkqKy'
    'Y3PCNUQnk6OzNhdUZHTD0uIIJoMJChgZhJRFRqS0VtNVKBry4/PE1OT0ZXWFlaW1xdXl9WZ2hpamtsbW5vY3R1dnd4eXp7fH1+f3'
    'OEhYaHiImKi4yNjo+Ck5SVlpeYmZqbnJ2en5KjpKWmp6ipqqusra6voRAAICAQIDBQUEBQYECAMDbQEAAhEDBCESMUEFURNhIgZx'
    'gZEyobHwFMHR4SNCFVJicvEzJDRDghaSUyWiY7LCB3PSNeJEgxdUkwgJChgZJjZFGidkdFU38qOzwygp0+PzhJSktMTU5PRldYWV'
    'pbXF1eX1RlZmdoaWprbG1ub2R1dnd4eXp7fH1+f3OEhYaHiImKi4yNjo+DlJWWl5iZmpucnZ6fkqOkpaanqKmqq6ytrq+v/aAAwD'
    'AQACEQMRAD8A835NDsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVd'
    'irsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdir//Q'
    '835NDsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdir'
    'sVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdir//R835NDsVdirsV'
    'dirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsV'
    'dirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdir//S835NDsVdirsVdirsVdirsVdi'
    'rsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdi'
    'rsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdir//T835NDsVdirsVdirsVdirsVdirsVdirsVdirs'
    'VdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirs'
    'VdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdir//U835NDsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVd'
    'irsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVd'
    'irsVdirsVdirsVdirsVdirsVdirsVdirsVdir//V835NDsVdirsVdirsVdirsVdirgCTQbk9Biqdad5K826koey0i7mjJoJBEwSt'
    'K/aYBe/jiqfWn5MfmFcRrJ+j1hVugmmjVtjTdeRbG1RJ/Ivz6BX0rb5euP6Y2qCvPye/MG1UMdM9ZSafuZY3P3BuWNqx7UfLHmPT'
    'WIv9NubbiORLxMBStK1pSmKpZirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVd'
    'irsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVf/W835NDsVdirsVdirsVdiqY6L5e1nW'
    'rkW+mWklzJ34D4RQV3PToK4q9c8qf84+oypceY7pq1qbO2IA2qKNJv8A5J+HBavTtG8h+UtHh9Ox0yBDxCtK6CSRqdyz1O/fBaU8'
    'EYxV3DfbFDuC+GKVvBewOKtPEjoyOgZGBDK24IPUEHFDF/MX5c+Udaic3WmxJMQAJ4R6UgANditPluMNq8w81fkHfWyPc+X7g3UQ'
    'Bb6rPQSAbnZgAG2AHTkzY2ryzUdL1DTblrW/t3tp0JDI4puDQ07HfwwqhcVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVd'
    'irsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVf/1/N+'
    'TQ7FXYq7FXYq4AkgAVJ6DFXq35e/kje6uF1DzCJLKw+ForWhWWUGh3rTgvH/AGWAlXumjeXtJ0axSz063SCFFA+EAFqVNWIAqak4'
    'LVMUUBQMCW6dsVaAGKG6YpcRihriMVa4jFVkijgcVcUUgV8MKpH5k8paF5gtTbanarKNuMoAEi0r9l6VHU4q8C8//lPqnlx3urHn'
    'faVTk0qr8cXQESAV2qftf83ZK1YDirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdir'
    'sVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVf/0PN+TQ7FXYq7FW0R3dURSzsQqqoqSTsAAMVe'
    '7/lR+UsNosWt67EJLogPa2rbqlejHx/z/Y/vASr2EHwyKVxO2KuHQYqu374q7FXHFWvoxQXYq7FK1z8JxQ1Q0xVSkQ4UoWaFZEZJ'
    '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'
    'FXYq7FV0ckkUiyRsUkU1V1JBB8QRiq65ubm5mae5leeZ6cpZGLsaCgqzVOwFMVU8VdirOPye8+Q+SfOKarcBvqs0D2s7oCSiuyuG'
    'oOtGjWuJV6h5tuvya826+nmi61eW31JRHxht7i2hhLQtyDMkkTScmb7fx/Fkd0sa/N/83rbzFpL6NZSm4WeRHnlFeCqh5hQT9pi3'
    'HphAQ8cwq7FXYq7FXYq7FXYq7FXYq7FXYq7FXYq7FXYq7FXYq7FXYq//0PN+TQ7FX1j+VdwJfy90Nh+zb8P+Adl/hkSllfMYFbDj'
    'FWw2Ku5Yq1y3xVsNitt8sVcDiqT+brm6tfLt7d2tTPbR+soHUhDVh/wOKvJvIWn6RcaPqPmK1u7iSe0nmkNkjL+3uWZT9pvDFUZ5'
    'XvNP85z3Ed5b3SWUQPOSZxGm/biKYqwHzf5j8taP5k1ix0CJUsZLD6k0gqVM6vzqPp+HfFWH+SLGbXfOem2stXDzo0pP8sfxb/di'
    'r7KlubDT7T1Z5I7a3QANJIQqgdBUnFVkGs6VcHjb3kEreCSKx/A4qiTKv8w398VcZBTbFVGSU/snChA3Fw1D+9APhSuKvIfzqv3/'
    'AEDFbSS8mkuEKIV4miq1SPlUYhLxXJIdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirs'
    'VdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdirsVdir//0fN+TQ7FX0b+ReprN5GS29TlJaXEsZQmpVWIdduynkf+'
    'GwFXonr/AH4FbExxpVQTeONK2JDTFbaEnx+1MVVA+BLUkqxo0kjBEUVZ2IAA8STiqRXP5geSrRitxrlkjKaMvrKx/wCFJxQldz+b'
    'v5cHlB+lorlnUgwxK7lhShHSnT3xS8Yh8zeX/Lmt3Nz5dunudJnlMskZRkZRXdHB34r/ADYqu8z/AJj2d9aOsOo/b5siRJw4d1Ul'
    'Qu2KvL3W91CWkMck55UUhasa7gGn7WKvYPI/kW+8n+XNS826sPq96tq31KIkckLjYkfzVI2xV5lrvn3zdr1qtnq2pzXVsjchCxAW'
    'vaoUCtPfFUpsOav6qMyMv2SpKmvzGBUwufNPmORw7apdngQE/fPtTp0IxVnH5d/nXrehagINduJdR0q4P7wyMXlhJNOSE9R/MmFX'
    '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'
    'b4ea+lw+LngtKXfkh+a35WeWfJDafLDFbX8s1ydQacosk0bysYVYsP3irbmNONWXly/mxKsJ/Lzzr5U0T82fMut6S0Ol6DdQTw2E'
    'LuIlCyXEL0QNSi/u2Kp+wuEoSb8wvNWnan+bmm63b3MUttFJYu9wjqyD0pAzVYGg498RyVlf5zfmFo2v+S2sLW+guJhcxOsccqO3'
    'FeVTRST3wBKJ/Lr8ytJ0f8q7bR31C3huRBeI8Dyor/vZpmAKk1+IMMSqUfkl+bMeiaV/hy9m9GNJmltSx4qwlpySpNOXLcfzcsJC'
    'GR+XbL9FXb6hr3nfWNY00xMFs5Lu8s1VmIKyGeK7q3FailFVuWC0qXlTzZot9+Zmo+a7OS4n0fyppUotWvru6vP9IkD85I3u5JnR'
    'TGJE+FlX4eWKHjXlC90O686W935qeT6jdTSSXdxE7ROkr1ZJAybrSXjX+XJK97TU/MunlW8rfmHfw6eYwoS8trXVWJBJqJ5OHw0I'
    '6qzf8WNkUsW/Pj837fXLvQE091k1DRLr66sy0IR14lV5L3ZlDMoP7OEBDOdN/M/yR5+8sx6T5nshqdhzSd7MTSQyxyoDSphdJNqt'
    '/ktg5JQ/m/8ANvy95T8pR6D5bgFhZWiOmnWBkeWTk5L7tIzyceT8izHFXgfl38y/Mug2T2lmYnSSZrh3lEhYyPTkaq6/y5KkPZvy'
    'u/Orzpe6bcvdSRlYZRHGqBgKcQd+TP45EhLFfzl/ODzbqwu/Kc7Q/oq7WCSVmDCTkriQfFz4ceSL+xhAQyb81fzZ07W/y01HQYdQ'
    't7h5BbCONJo3YiK4jfZQSei4Al6AfzW0S+8hLpflm4fRwLWOCw1C2RZBbCILSkZKL8KrxK8lwKk3kz81Bo+i/oyfXpteurWV/req'
    '3MlWLysXVDykl48F+Hh6n7P7OFWA/ll59sfLPnrzteXN5Fb/AKSuvUieSRUDq00slQSRXZ1xKHn35xa1Z63+YGoaraTJcR3SW5M0'
    'Th1LJAkZ3BI24UyQVhWKuxV2KuxV2KuxV2KuxV2KuxV2KuxV2KuxV//Q835NDsVdirsVdirsVTzyX5ht9A802Ot3VubxbQmqVHKh'
    'UpUE91U/BiQr6g8s+ePL3mOyW4026RpSB6tuxpIjGpKlTQ/sk/6uQpV+o6nIA6rWo6AdTili95+XMPmJ1ufNEjpp6HlBZI3Esx6N'
    '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'
    '2Q=='
)


BRAND_LOGO_B64 = (
    'iVBORw0KGgoAAAANSUhEUgAAASkAAADuCAMAAABS3QEIAAADAFBMVEXu22ZioqXiXioRotijpp5hZV1KtdWW8e4eGyNjydSsnl/NKRrOmljp56Ut'
    'V2uekC/Bt5V1GybYqyWkyJ7/1h3Y2NVwYSJZdo9pj3qXcxybdFQaIlhywrrVLkHuXVQiAiAiYqk9hHsfqb4r0N2YCyD/WYEAAAAD/v/+PFAHBAb+'
    'Q1At/v4rGAYIBgcJBwgSEwxKKQYKCQgMCwo3IwlVNAoWDQgDGSwMDA5qOQdyRgxK/P7+SWj+VmqPVg31dwaLSAcxBgT4hwnRZgUKJTLvaQWwVwZO'
    'BAOsSAYthqbMWQX4lhAibpUwtdMHCiyuZg4KDC5vBwj9VFYDJ01rKgjQdg2NOAYCOGgTZZIaiKr8pRIBEAcy1/Az6fkHNk/5KDMDGUhM6PkPVHYn'
    'AgVKGQjMKDALSG61dBUkAQWPFRb4NzjShRUqlrMyyOguqMuzJispBAUqdZcNV4xxFRCVYxb+OmTPNDMgAAOrFxpJ1+2MCg4FCSkyNi94UhVvVyoH'
    'BSYUdZcTeagsveRTRyv9tRhXQxYJAyIrKSXpWQb/ZG1n/P4RRVh1ZTCLZyuxhyzNHCcZk68TmMqOdTGyGSPKSQXQlysxxdv8LFNHOyetJhj5xigJ'
    'CkUAEAHTN0bLiScKSYguRkxIyeSrOwyteCj3tS4Ltu4L1/sH6P9IhpWThlSul1DyqysDKWg4MxcrmskzpreQGySOiW/rmSX/xxouWGxUWE8LyfpN'
    'xNL8RTkSaaRnSiVvaUoxhZhMmK5Jp7eypm7SlRjtyFMWp9KMeEwxZHEreqlYUjJ5dVCJKBOWJCa2My8UMTkUhZxIus5s6fWlDBSpi06ylC/Lp07R'
    'tlHLt2vyuEn/1ywpisVZuLpu2O6YkXDURUbYpyzVyZH56o0lBisnO0kyVFZMS0R2d2+OWSX5400GAyAIOogRW6RvhmyXl4+oaCG1hBe3pk28t4rM'
    'yrHsHij11VH/5TTw5bP7+M8xRTtRKiVIZ25SdXFFd4eolmaqppHtiyTn1o7l5cv8++4MYXn2WZRbAAABAHRSTlP///////////b/////////////'
    '////////////////qf///////wH//zD///9Pb/3/jq////b+zP//////////+////////////////87/9v/////////////O/////////7D/////'
    'jv/////////P////////cP///7D///+N////////cP///////////////////////////7b/////////////////////////////////////////'
    '///////////////////////////////////////////////9////////V///////////////////////////////////5S9BugAASNtJREFUeNrl'
    'vQVgW1e2Lpx2Osxz+T746b0TbensvQ+DwJJBUuzakjmxHdeJOY4hiROHoeEG2iZNmdvpTJmnzDNtp3OH8Q0zwx3me++/1j6SLduSTHEmbXcbg2xL'
    'Ot9Za+1vwV5riTSPRTJLej2tJbNFhlLKtMxijFJVZUxV8SOlr3ukGBUgUYlQrtVY9T3Ln3zq6Y/ftOX/eOuRjz/91Dl/fOhd9daBA9+nBICkr0uk'
    'iJAlrZWp6XT9+hXVbcGLYK0avHft8tU97e31HZZllZeX199447seeuO3bryx3OLq606mCAVJaqUq0UBQrBvWtgUCwWCw7d7dzR3pXYQwjRBQO0pA'
    '7wBLUD8J5IlzblncVl9nSME/lcRM1vHDoQCs4Ja1N3Sk06hcVIhaBk8p8w3N2nai8deX9hFJZSrd1r52VXDp0uCWZe271BrK+gAQqmYUU5ImIHud'
    '7n3eddN0enV1ILA0EKy+4Zrvg0XnrWCvCfzHPLkSpl7sia8XrjANKaFemrX6chCnQHBZfStvBSqgMgrsALWSMtoXSyQStbASuGIga8AgXvPCNR0p'
    'uF5+pBrV7qIv1nMQJA3AoQfoWOdIorZ/uNvn94fHVygU2ujzXTd8sj8R64yNMcZes4x0yWStA6Qo1XaD3i0NPtJsavAoYaqtEbX2qk3+urpwnb/A'
    'Cof93cObaxOdQEphP4D9UGLEI1i4O76mZMq7LqrWD+J+t2pPB+McJczUYlu7/eHDoZDf5y1Exjd9hUJhxGvzVpAvBJm+RrVPAEVUe/UqFKjBdhNp'
    'k6ZKfbUXC2Q2bvRdkUGpAFI+8SDAVfdod3+is3MsY/ZeG0Z/yWQipVnLgwBU4PlyzsA7oapd2x0OATyPjgtTAaQyj67xiy/Bgvm6a2OdfSPSa8Wb'
    'ztU+MrKtY48wUXtqOEdK1VkLaicQmGaXfAVW9id+P1j764YTI4Sqmkb6XltIbetYcRFyg+U1fX3on8Q219XVeZc+Ac4MSE2SshBsjt1bE6atauQ1'
    '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'
    'o5BvqwAAAABJRU5ErkJggg=='
)



if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")





ACCENT = wx.Colour(255, 45, 60)
PANEL = wx.Colour(20, 18, 22)
TEXT = wx.Colour(240, 236, 238)
MUTED = wx.Colour(170, 156, 162)

HIDDEN_POS = (-32000, -32000)
POLL_MS = 250                  
TRANSLATE_TIMEOUT_S = 30
WARM_MAX_AGE_S = 600           
MAX_UPLOAD_PX = 1600
SAME_IMG_DIFF = 0.4            

TARGET_LANG = "fa"             

user32 = ctypes.windll.user32
user32.ShowWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
user32.SetWindowPos.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, ctypes.c_uint]
user32.GetWindowLongW.argtypes = [ctypes.c_void_p, ctypes.c_int]
user32.GetWindowLongW.restype = ctypes.c_long
user32.SetWindowLongW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_long]
user32.SetLayeredWindowAttributes.argtypes = [ctypes.c_void_p, ctypes.c_ulong,
                                              ctypes.c_ubyte, ctypes.c_ulong]
user32.ClipCursor.argtypes = [ctypes.c_void_p]
user32.SetWindowRgn.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
gdi32 = ctypes.windll.gdi32
gdi32.CreateRoundRectRgn.argtypes = [ctypes.c_int] * 6
gdi32.CreateRoundRectRgn.restype = ctypes.c_void_p

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
WS_EX_TOPMOST = 0x00000008


def no_activate(win, layered=False):
    """پنجره هرگز فوکوس را نمی‌گیرد و در Alt+Tab/تسک‌بار دیده نمی‌شود."""
    h = win.GetHandle()
    st = user32.GetWindowLongW(h, GWL_EXSTYLE)
    st |= WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | (WS_EX_LAYERED if layered else 0)
    user32.SetWindowLongW(h, GWL_EXSTYLE, st)


def place_top(win, x, y, w, h):
    """نمایش/جابه‌جایی بالای همه‌ی پنجره‌ها (حتی بازی) بدون دزدیدن فوکوس."""
    user32.SetWindowPos(win.GetHandle(), HWND_TOPMOST, int(x), int(y), int(w), int(h),
                        SWP_NOACTIVATE | SWP_SHOWWINDOW)


def place_notop(win, x, y, w, h):
    """نمایش عادی پنجره وقتی پین خاموش است؛ بدون تغییر فوکوس."""
    try:
        hwnd = win.GetHandle()
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style & ~WS_EX_TOPMOST)
        user32.SetWindowPos(hwnd, ctypes.c_void_p(HWND_NOTOPMOST), int(x), int(y), int(w), int(h),
                            SWP_NOACTIVATE | SWP_SHOWWINDOW)
    except Exception:

        user32.SetWindowPos(win.GetHandle(), ctypes.c_void_p(HWND_NOTOPMOST), int(x), int(y), int(w), int(h),
                            SWP_NOACTIVATE | SWP_SHOWWINDOW)


def hide_win(win):
    user32.ShowWindow(win.GetHandle(), 0)


def round_corners(win, w, h, r):
    """گوشه‌های گرد برای پنجره (ریجنِ پنجره؛ مالکیتش بعد از SetWindowRgn با ویندوز است)."""
    try:
        rgn = gdi32.CreateRoundRectRgn(0, 0, int(w) + 1, int(h) + 1, int(r) * 2, int(r) * 2)
        if rgn:
            user32.SetWindowRgn(win.GetHandle(), rgn, 1)
    except Exception:
        pass


def virtual_rect():
    gm = user32.GetSystemMetrics
    x, y, w, h = gm(76), gm(77), gm(78), gm(79)
    if w <= 0 or h <= 0:
        return 0, 0, gm(0), gm(1)
    return x, y, w, h


RECT = ctypes.wintypes.RECT
POINT = ctypes.wintypes.POINT
_OWN_PID = os.getpid()
_SHELL_CLASSES = {"Progman", "WorkerW", "Shell_TrayWnd", "Shell_SecondaryTrayWnd"}
_SKIP_EXE = {"explorer.exe", "textinputhost.exe", "systemsettings.exe", "searchhost.exe",
             "shellexperiencehost.exe", "startmenuexperiencehost.exe"}

user32.GetForegroundWindow.restype = ctypes.c_void_p
user32.IsWindowVisible.argtypes = [ctypes.c_void_p]
user32.IsIconic.argtypes = [ctypes.c_void_p]
user32.GetWindowRect.argtypes = [ctypes.c_void_p, ctypes.POINTER(RECT)]
user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
user32.GetClassNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]
user32.GetWindowTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]
user32.GetWindowTextLengthW.argtypes = [ctypes.c_void_p]
user32.MonitorFromWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
user32.MonitorFromWindow.restype = ctypes.c_void_p
user32.MonitorFromPoint.argtypes = [POINT, ctypes.c_ulong]
user32.MonitorFromPoint.restype = ctypes.c_void_p
user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]
user32.GetAsyncKeyState.restype = ctypes.c_short
user32.PrintWindow.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
user32.GetWindowDC.argtypes = [ctypes.c_void_p]
user32.GetWindowDC.restype = ctypes.c_void_p
user32.ReleaseDC.argtypes = [ctypes.c_void_p, ctypes.c_void_p]


class _MONITORINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_ulong), ("rcMonitor", RECT), ("rcWork", RECT),
                ("dwFlags", ctypes.c_ulong)]


def _pid_of(hwnd):
    pid = ctypes.c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def _exe_of_pid(pid):
    try:
        k = ctypes.windll.kernel32
        k.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        k.OpenProcess.restype = ctypes.c_void_p
        k.QueryFullProcessImageNameW.argtypes = [ctypes.c_void_p, ctypes.c_ulong,
                                                 ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_ulong)]
        k.CloseHandle.argtypes = [ctypes.c_void_p]
        h = k.OpenProcess(0x1000, False, pid)           
        if not h:
            return None
        try:
            buf = ctypes.create_unicode_buffer(1024)
            size = ctypes.c_ulong(1024)
            if k.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                return os.path.basename(buf.value)
        finally:
            k.CloseHandle(h)
    except Exception:
        pass
    return None


def _rect_of(hwnd):
    r = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.left, r.top, r.right, r.bottom


def _text_of(hwnd):
    n = user32.GetWindowTextLengthW(hwnd)
    if n <= 0:
        return ""
    buf = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value.strip()


def _class_of(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def _mon_rect(hmon):
    mi = _MONITORINFO()
    mi.cbSize = ctypes.sizeof(_MONITORINFO)
    user32.GetMonitorInfoW(hmon, ctypes.byref(mi))
    r = mi.rcMonitor
    return r.left, r.top, r.right - r.left, r.bottom - r.top


def monitor_of_window(hwnd):
    return _mon_rect(user32.MonitorFromWindow(hwnd, 2))


def monitor_at(x, y):
    return _mon_rect(user32.MonitorFromPoint(POINT(int(x), int(y)), 2))


def list_monitor_rects():
    """Returns monitor rectangles in Windows enumeration order, with virtual-screen fallback."""
    monitors = []
    try:
        callback_type = ctypes.WINFUNCTYPE(
            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
            ctypes.POINTER(RECT), ctypes.c_void_p
        )
        enum_monitors = user32.EnumDisplayMonitors
        enum_monitors.argtypes = [ctypes.c_void_p, ctypes.POINTER(RECT), callback_type, ctypes.c_void_p]
        enum_monitors.restype = ctypes.c_int

        def _monitor_callback(hmon, _hdc, _rect, _data):
            try:
                rect = _mon_rect(hmon)
                if rect not in monitors:
                    monitors.append(rect)
            except Exception:
                pass
            return True

        callback = callback_type(_monitor_callback)
        enum_monitors(None, None, callback, None)
    except Exception:
        pass
    return monitors or [virtual_rect()]


def list_windows(need_title=True):
    """[(hwnd, exe, title, area)] پنجره‌های قابل‌مشاهده‌ی برنامه‌های دیگر."""
    out = []

    def cb(hwnd, _):
        try:
            if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
                return True
            pid = _pid_of(hwnd)
            if pid == _OWN_PID or _class_of(hwnd) in _SHELL_CLASSES:
                return True
            l, t, r, b = _rect_of(hwnd)
            if r - l < 300 or b - t < 200:
                return True
            title = _text_of(hwnd)
            if need_title and not title:
                return True
            exe = _exe_of_pid(pid)
            if exe and exe.lower() not in _SKIP_EXE:
                out.append((hwnd, exe, title, (r - l) * (b - t)))
        except Exception:
            pass
        return True

    proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(cb)
    user32.EnumWindows(proc, 0)
    return out


def foreground_game():
    """پنجره‌ی فعال، اگر تمام‌صفحه (پوشاننده‌ی کل یک مانیتور) باشد؛ وگرنه None."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd or _pid_of(hwnd) == _OWN_PID or _class_of(hwnd) in _SHELL_CLASSES:
        return None
    l, t, r, b = _rect_of(hwnd)
    mx, my, mw, mh = monitor_of_window(hwnd)
    if l <= mx + 2 and t <= my + 2 and r >= mx + mw - 2 and b >= my + mh - 2:
        return hwnd
    return None


def is_black(img):
    try:
        return img.convert("L").resize((48, 48)).getextrema()[1] < 8
    except Exception:
        return False


def _grab_gdi(region):
    vx, vy, vw, vh = virtual_rect()
    try:
        full = ImageGrab.grab(all_screens=True)
    except Exception:
        try:
            full = ImageGrab.grab()
            vx, vy, vw, vh = 0, 0, full.width, full.height
        except Exception:
            return None
    x, y, w, h = region
    k = full.width / float(max(1, vw))
    return full.crop((int((x - vx) * k), int((y - vy) * k),
                      int((x - vx + w) * k), int((y - vy + h) * k)))


def _dx_release(cam):
    try:
        cam.release()
    except Exception:
        pass
    try:
        import dxcam
        f = getattr(dxcam, "__factory", None)
        if f is not None:
            f.clean_up()
    except Exception:
        pass


def _grab_dx(region):
    """گرفتن عکس با DXGI Desktop Duplication — چیزی را می‌گیرد که واقعاً روی مانیتور
    است (بازی تمام‌صفحه)، برخلاف GDI که سیاه یا میزکارِ پشتِ بازی را برمی‌گرداند."""
    try:
        import dxcam
    except Exception:
        return None
    x, y, w, h = region
    mx, my, mw, mh = monitor_at(x + w // 2, y + h // 2)
    cam = None
    try:
        for idx in range(8):
            try:
                c = dxcam.create(output_idx=idx, output_color="RGB")
            except Exception:
                break
            if c is None:
                break
            if (getattr(c, "width", 0), getattr(c, "height", 0)) == (mw, mh):
                cam = c
                break
            _dx_release(c)
        if cam is None:
            return None
        frame = None
        for _ in range(30):                       
            frame = cam.grab()
            if frame is not None:
                break
            time.sleep(0.02)
        if frame is None:
            return None
        return Image.fromarray(frame).crop((x - mx, y - my, x - mx + w, y - my + h))
    except Exception:
        return None
    finally:
        if cam is not None:
            _dx_release(cam)


user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]


def _cursor_pos():
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def _covers(rect, mon):
    l, t, r, b = rect
    mx, my, mw, mh = mon
    return l <= mx + 2 and t <= my + 2 and r >= mx + mw - 2 and b >= my + mh - 2


def scaler_overlay(mon, skip_hwnd):
    """پنجره‌ی تمام‌صفحه‌ی دیگری که کل مانیتور را پوشانده (مثلاً خروجیِ Lossless Scaling).
    در این حالت چیزی که کاربر می‌بیند با پنجره‌ی خودِ بازی فرق دارد (اندازه/جای متفاوت)،
    پس باید از کل مانیتور عکس بگیریم."""
    try:
        for hwnd, _exe, _t, _a in list_windows(need_title=False):
            if hwnd != skip_hwnd and _covers(_rect_of(hwnd), mon):
                return hwnd
    except Exception:
        pass
    return None


def capture_for_snip(monitor_index=0):
    """Capture the selected monitor, or automatically choose the active game's monitor.
    monitor_index is 0 for Auto, otherwise a 1-based index from list_monitor_rects()."""
    fg = user32.GetForegroundWindow()
    fg_is_external = bool(fg and _pid_of(fg) != _OWN_PID and _class_of(fg) not in _SHELL_CLASSES)
    monitors = list_monitor_rects()
    try:
        selected = int(monitor_index or 0)
    except Exception:
        selected = 0

    if selected > 0 and selected <= len(monitors):

        mon = monitors[selected - 1]
        ref = fg if fg_is_external and monitor_of_window(fg) == mon else None
    else:



        mon = monitor_at(*_cursor_pos())
        ref = fg if fg_is_external and monitor_of_window(fg) == mon else None

    overlay = scaler_overlay(mon, ref)
    full = bool(overlay) or (ref is not None and _covers(_rect_of(ref), mon))
    region = mon


    for fn in ((_grab_dx, _grab_gdi) if full else (_grab_gdi, _grab_dx)):
        img = fn(region)
        if img is not None and not is_black(img):
            return img, region, None
    return None, None, "عکس صفحه سیاه شد؛ اگر بازی Exclusive Fullscreen است آن را روی Borderless بگذار"


def raise_top(win):
    """دوباره Topmost می‌کند (بازی‌ها گاهی خودشان را بالا می‌آورند)."""
    user32.SetWindowPos(win.GetHandle(), HWND_TOPMOST, 0, 0, 0, 0, 0x0001 | 0x0002 | SWP_NOACTIVATE)


def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin():
    try:
        exe = sys.executable
        args = " ".join('"%s"' % a for a in sys.argv[1:])
        if getattr(sys, "frozen", False):
            params = args
        else:
            alt = os.path.join(os.path.dirname(exe), "pythonw.exe")
            exe = alt if os.path.isfile(alt) else exe
            params = ('"%s" %s' % (os.path.abspath(__file__), args)).strip()
        return ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1) > 32
    except Exception:
        return False





def prepare_upload(img):
    """عکس را در صورت نیاز کوچک می‌کند (بدون تغییر کیفیت)."""
    img = img.convert("RGB")
    if max(img.size) > MAX_UPLOAD_PX:
        img.thumbnail((MAX_UPLOAD_PX, MAX_UPLOAD_PX), Image.LANCZOS)
    return img


def to_data_url(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG", compress_level=1)      
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def image_hash(img):
    try:
        return hashlib.md5(img.convert("RGB").resize((96, 96)).tobytes()).hexdigest()
    except Exception:
        return None


def image_sig(img):
    try:
        return list(img.convert("L").resize((48, 48), Image.BILINEAR).tobytes())
    except Exception:
        return None


def sig_diff(a, b):
    if not a or not b or len(a) != len(b):
        return 999.0
    return sum(abs(x - y) for x, y in zip(a, b)) / float(len(a))


def data_url_to_pil(data_url):
    return Image.open(io.BytesIO(base64.b64decode(data_url.split(",", 1)[1]))).convert("RGB")


def pil_to_bitmap(img):
    img = img.convert("RGB")
    return wx.Bitmap.FromBuffer(img.width, img.height, img.tobytes())


def copy_to_clipboard(img):
    clip = wx.Clipboard()
    if clip.Open():
        try:
            clip.SetData(wx.BitmapDataObject(wx.Bitmap.FromBufferRGBA(
                img.width, img.height, img.convert("RGBA").tobytes())))
            clip.Flush()
        finally:
            clip.Close()


_BRAND_SOURCE_IMAGE = None
_BRAND_BITMAP_CACHE = {}


def _brand_source_image():
    """لوگوی اصلی را یک‌بار از داده‌ی داخلی فایل بارگذاری می‌کند."""
    global _BRAND_SOURCE_IMAGE
    if _BRAND_SOURCE_IMAGE is None:
        try:
            raw = base64.b64decode(BRAND_LOGO_B64)
            with Image.open(io.BytesIO(raw)) as source:
                _BRAND_SOURCE_IMAGE = source.convert("RGBA").copy()
        except Exception as exc:
            dbg("brand logo load failed: %s" % exc)
            _BRAND_SOURCE_IMAGE = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    return _BRAND_SOURCE_IMAGE


def make_brand_bitmap(width, height):
    """لوگو را با نسبت تصویر حفظ‌شده داخل یک بوم شفاف و متناسب با DPI می‌سازد."""
    width, height = max(1, int(width)), max(1, int(height))
    key = (width, height)
    cached = _BRAND_BITMAP_CACHE.get(key)
    if cached is not None and cached.IsOk():
        return cached
    canvas = Image.new("RGBA", key, (0, 0, 0, 0))
    logo = _brand_source_image().copy()
    logo.thumbnail((max(1, width - 1), max(1, height - 1)), Image.LANCZOS)
    canvas.alpha_composite(logo, ((width - logo.width) // 2, (height - logo.height) // 2))
    bitmap = wx.Bitmap.FromBufferRGBA(width, height, canvas.tobytes())
    _BRAND_BITMAP_CACHE[key] = bitmap
    return bitmap


def make_icon():
    """آیکون ESH برای ناحیه‌ی اعلان ویندوز و پنجره‌های خود برنامه."""
    icon = wx.Icon()
    icon.CopyFromBitmap(make_brand_bitmap(32, 32))
    return icon





class Config:
    DEFAULTS = {
        "snip_hotkey": "f3",
        "close_hotkey": "f2",
        "auto_close_seconds": 60,
        "run_on_startup": False,
        "save_dir": os.path.join(os.path.expanduser("~"), "Pictures", "42OCR"),   
        "capture_monitor": 0,       
        "performance_mode": True,   
        "panel_pinned": True,       
    }

    def __init__(self):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        self.dir = os.path.join(base, "42OCR")
        self.path = os.path.join(self.dir, "config.json")
        self.data = dict(self.DEFAULTS)
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if "hotkey" in stored and "close_hotkey" not in stored:   
                stored["close_hotkey"] = stored["hotkey"]
            for k in self.DEFAULTS:
                if k in stored:
                    self.data[k] = stored[k]
        except Exception:
            pass

    def __getitem__(self, k):
        return self.data[k]

    def set(self, k, v):
        if self.data.get(k) == v:
            return
        self.data[k] = v
        try:
            os.makedirs(self.dir, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
TASK_NAME = "42OCR_SnipTranslate"


def _startup_cmd():
    exe = sys.executable
    if getattr(sys, "frozen", False):
        return '"%s" --bg' % exe
    alt = os.path.join(os.path.dirname(exe), "pythonw.exe")
    return '"%s" "%s" --bg' % (alt if os.path.isfile(alt) else exe, os.path.abspath(__file__))


def _no_window():
    import subprocess
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _schtasks(args):
    """اجرای بی‌صدای schtasks؛ کدِ خروجی را برمی‌گرداند (یا -1 اگر اجرا نشد)."""
    try:
        import subprocess
        return subprocess.call(["schtasks"] + args, stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=_no_window())
    except Exception:
        return -1


def _task_exists():
    return _schtasks(["/query", "/tn", TASK_NAME]) == 0


def _runkey_exists():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, "42OCR")
        return True
    except Exception:
        return False


def _runkey_set():
    try:
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.SetValueEx(k, "42OCR", 0, winreg.REG_SZ, _startup_cmd())
        return True
    except Exception:
        return False


def _runkey_delete():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            winreg.DeleteValue(k, "42OCR")
    except Exception:
        pass


def startup_exists():
    return _task_exists() or _runkey_exists()


def set_run_on_startup(enabled):
    """روشن: Task Scheduler با بالاترین سطح (بدون پرسش UAC در هر ورود)؛ اگر نشد ریجستری HKCU Run.
    خاموش: هر دو حذف می‌شوند تا دیگر با ویندوز اجرا نشود. خروجی: کار انجام شد؟"""
    if enabled:
        made = False
        if is_admin():
            made = _schtasks(["/create", "/tn", TASK_NAME, "/tr", _startup_cmd(),
                              "/sc", "onlogon", "/rl", "highest", "/f"]) == 0
        if made:
            _runkey_delete()
            return True
        return _runkey_set()
    _schtasks(["/delete", "/tn", TASK_NAME, "/f"])
    _runkey_delete()
    return not startup_exists()


_NAMED = {"esc": 0x1B, "space": 0x20, "tab": 9, "enter": 0x0D, "pause": 0x13, "insert": 0x2D,
          "delete": 0x2E, "home": 0x24, "end": 0x23, "pageup": 0x21, "pagedown": 0x22,
          "printscreen": 0x2C, "`": 0xC0, "backspace": 8, "capslock": 0x14, "left": 0x25, "up": 0x26,
          "right": 0x27, "down": 0x28, ";": 0xBA, "=": 0xBB, ",": 0xBC, "-": 0xBD, ".": 0xBE,
          "/": 0xBF, "[": 0xDB, "\\": 0xDC, "]": 0xDD, "'": 0xDE,
          "num*": 0x6A, "num+": 0x6B, "num-": 0x6D, "num.": 0x6E, "num/": 0x6F}


def parse_hotkey(combo):
    mods, vk = 0, None
    for p in str(combo).lower().replace(" ", "").split("+"):
        if p in ("ctrl", "control"):
            mods |= 2
        elif p == "alt":
            mods |= 1
        elif p == "shift":
            mods |= 4
        elif p in ("win", "windows"):
            mods |= 8
        elif re.fullmatch(r"f([1-9]|1\d|2[0-4])", p):
            vk = 0x70 + int(p[1:]) - 1
        elif len(p) == 1 and p.isalnum():
            vk = ord(p.upper())
        elif re.fullmatch(r"num[0-9]", p):
            vk = 0x60 + int(p[3])
        elif p in _NAMED:
            vk = _NAMED[p]
        elif re.fullmatch(r"vk\d{1,3}", p):
            vk = int(p[2:])
    return mods, vk


def vk_token(vk):
    """کدِ کلید → نامی که parse_hotkey می‌فهمد."""
    if 0x70 <= vk <= 0x87:
        return "f%d" % (vk - 0x6F)
    if 0x30 <= vk <= 0x39 or 0x41 <= vk <= 0x5A:
        return chr(vk).lower()
    if 0x60 <= vk <= 0x69:
        return "num%d" % (vk - 0x60)
    for name, code in _NAMED.items():
        if code == vk:
            return name
    return "vk%d" % vk                      





def _unquote_json(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        try:
            return json.loads(s)
        except Exception:
            return s[1:-1]
    return s


class TranslateWorker(wx.Frame):
    """مرورگر مخفی Google Translate — منطقِ همان نسخه‌ی قدیمیِ کارکرده (بدون دستکاری):
    هر ترجمه صفحه را از نو بارگذاری می‌کند، بعد از لود ۹۰۰ms صبر می‌کند، سپس paste/drop/input
    را با هم تزریق می‌کند و بزرگ‌ترین تصویر blob/data را برمی‌دارد."""

    POLL_INTERVAL_MS = 900

    INJECT_JS = r"""
(function(dataUrl){
  try {
    var m = dataUrl.match(/^data:([^;,]+)[;,]/);
    var mime = m ? m[1] : 'image/png';
    var bin = atob(dataUrl.split(',')[1]);
    var u8 = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
    var file = new File([u8], 'clip.png', {type: mime});
    var dt = new DataTransfer();
    dt.items.add(file);
    var ev = new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true});
    document.dispatchEvent(ev);
    document.body.dispatchEvent(ev);
    var targets = document.querySelectorAll('[jsaction*="drop"],[jsaction*="paste"],[jsaction*="input"],[data-drop],[role="button"]');
    for (var j = 0; j < targets.length; j++) {
      try {
        var drop = new DragEvent('drop', {dataTransfer: dt, bubbles: true, cancelable: true});
        targets[j].dispatchEvent(drop);
      } catch (e) {}
    }
    var inputs = document.querySelectorAll('input[type=file]');
    for (var k = 0; k < inputs.length; k++) {
      try {
        Object.defineProperty(inputs[k], 'files', {value: dt.files, configurable: true});
        inputs[k].dispatchEvent(new Event('change', {bubbles: true}));
      } catch (e) {}
    }
    return 'OK';
  } catch (e) { return 'ERR:' + (e && e.message || e); }
})"""

    EXTRACT_JS = r"""
(function(){
  var best = null, bestArea = 0;
  document.querySelectorAll('img').forEach(function(im){
    var s = im.src || '';
    if (s.indexOf('blob:') !== 0 && s.indexOf('data:image/') !== 0) return;
    var a = (im.naturalWidth || 0) * (im.naturalHeight || 0);
    if (a > bestArea) { bestArea = a; best = im; }
  });
  if (!best || bestArea < 100) return 'NOT_READY';
  try {
    var c = document.createElement('canvas');
    c.width = best.naturalWidth;
    c.height = best.naturalHeight;
    c.getContext('2d').drawImage(best, 0, 0);
    var d = c.toDataURL('image/png');
    if (d && d.length > 300) return d;
    return 'NOT_READY';
  } catch (e) { return 'NOT_READY'; }
})()"""

    def __init__(self, on_result, on_error, on_state):
        style = wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.FRAME_SHAPED | wx.BORDER_NONE
        super().__init__(None, title="", size=(560, 800), style=style)
        self.SetPosition(HIDDEN_POS)
        self.Show()   
        self.on_result, self.on_error, self.on_state = on_result, on_error, on_state

        self.browser = wx.html2.WebView.New(self)
        self.browser.Bind(wx.html2.EVT_WEBVIEW_LOADED, self._on_loaded)
        self.browser.Bind(wx.html2.EVT_WEBVIEW_SCRIPT_RESULT, self._on_script)
        self.browser.Bind(wx.html2.EVT_WEBVIEW_ERROR, lambda e: self._fail("خطا در بارگذاری صفحه‌ی گوگل"))

        self._busy = False
        self._data_url = None
        self._source_hash = None
        self._start_ts = 0
        self._re_injected = False
        self._fails = 0
        self._lang = TARGET_LANG
        self._poll_timer = None
        self._timeout_timer = None
        self._inject_timer = None
        self._load_watch = None
        self._load_ok = False
        self._load_retries = 0
        dbg("worker (old logic) backend=%s" % type(self.browser).__name__)

    @staticmethod
    def _url(lang):
        return "https://translate.google.com/?sl=auto&tl=%s&op=images&hl=fa" % lang

    def start(self, img):
        if self._busy:
            self._force_reset()
        self._busy = True
        self._fails = 0
        self._load_ok = False
        self._load_retries = 0
        self._data_url = to_data_url(prepare_upload(img))
        self._source_hash = image_hash(img)
        self._re_injected = False
        self._start_ts = time.time()
        self._clear_timers()
        self.on_state("در حال بارگذاری Google Translate…")
        try:
            self.browser.LoadURL(self._url(self._lang))
        except Exception:
            pass
        self._load_watch = wx.CallLater(7000, self._check_load_watch)

    def _check_load_watch(self):
        if not self._busy or self._load_ok:
            return
        self._load_retries += 1
        if self._load_retries > 4:
            self._fail("خطا در بارگذاری صفحه‌ی گوگل؛ اتصال اینترنت را بررسی کنید.")
            return
        self.on_state("بارگذاری مجدد Google Translate… (%d/4)" % self._load_retries)
        try:
            self.browser.LoadURL(self._url(self._lang))
        except Exception:
            pass
        self._load_watch = wx.CallLater(7000, self._check_load_watch)

    def _force_reset(self):
        self._busy = False
        self._data_url = None
        self._source_hash = None
        self._load_ok = False
        self._clear_timers()
        try:
            self.browser.LoadURL(self._url(self._lang))
        except Exception:
            pass

    def _on_loaded(self, event):
        self._load_ok = True
        if not self._busy:
            return
        self.on_state("در حال ارسال تصویر…")
        self._inject_timer = wx.CallLater(900, self._inject)

    def _inject(self):
        if not self._busy or self._data_url is None:
            return
        self._clear_timers()
        try:
            self.browser.RunScriptAsync(self.INJECT_JS + "('" + self._data_url + "')")
        except Exception as e:
            self._fail("خطا در تزریق تصویر: %s" % e)
            return
        self.on_state("در حال ترجمه توسط گوگل…")
        self._timeout_timer = wx.CallLater(TRANSLATE_TIMEOUT_S * 1000, self._on_timeout)
        self._schedule_poll()

    def _schedule_poll(self):
        self._poll_timer = wx.CallLater(self.POLL_INTERVAL_MS, self._poll_once)

    def _poll_once(self):
        if not self._busy:
            return
        try:
            self.browser.RunScriptAsync(self.EXTRACT_JS)
        except Exception:
            self._schedule_poll()

    def _on_script(self, event):
        if not self._busy:
            return
        result = _unquote_json(event.GetString() or "")

        if result.startswith("ERR"):
            self._fails += 1
            if self._fails > 3:
                self._fail("گوگل تصویر را نپذیرفت؛ دوباره تلاش کنید.")
                return
            if not self._re_injected and time.time() - self._start_ts < 20:
                self._re_injected = True
                self._inject_timer = wx.CallLater(1500, self._inject)
            return

        if result.startswith("NOT_READY"):
            self._fails = 0
            if time.time() - self._start_ts > TRANSLATE_TIMEOUT_S:
                self._on_timeout()
                return
            if not self._re_injected and time.time() - self._start_ts > 12:
                self._re_injected = True
                self._inject()
                return
            self._schedule_poll()
            return

        if result.startswith("data:image/"):
            try:
                out = data_url_to_pil(result)
            except Exception:
                self._schedule_poll()
                return
            if self._source_hash and image_hash(out) == self._source_hash:
                self._schedule_poll()
                return
            self._fails = 0
            dbg("result ok %dx%d" % (out.width, out.height))
            self._busy = False
            self._data_url = None
            self._source_hash = None
            self._clear_timers()
            self.on_result(out)
            return

        self._fails += 1
        if not self._re_injected and time.time() - self._start_ts > 8:
            self._re_injected = True
            self._inject()
            return
        if self._fails > 6:
            dbg("unexpected script result: %r" % result[:100])
            self._fail("گوگل پاسخ نداد؛ اتصال اینترنت را بررسی کنید.")
            return
        self._schedule_poll()

    def _fail(self, message):
        self._busy = False
        self._data_url = None
        self._source_hash = None
        self._clear_timers()
        dbg("FAIL: " + message)
        self.on_error(message)
        try:
            self.browser.LoadURL(self._url(self._lang))
        except Exception:
            pass

    def _on_timeout(self):
        if self._busy:
            self._fail("ترجمه انجام نشد (زمان‌بندی گوگل طول کشید). دوباره تلاش کنید.")

    def _clear_timers(self):
        for t in (self._poll_timer, self._timeout_timer, self._inject_timer, self._load_watch):
            if t is not None:
                try:
                    if t.IsRunning():
                        t.Stop()
                except Exception:
                    pass
        self._poll_timer = self._timeout_timer = self._inject_timer = self._load_watch = None

    def shutdown(self):
        self._busy = False
        self._clear_timers()
        try:
            self.Destroy()
        except Exception:
            pass





class SnipLayer(wx.Frame):
    KEY = wx.Colour(255, 0, 254)          
    ALPHA = 150

    def __init__(self, app):
        super().__init__(None, style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE)
        self.app = app
        self.active = False
        self.shot = None
        self.geom = (0, 0, 1, 1)
        self.scale = (1.0, 1.0)
        self.start = None
        self.cur = None
        self.on_done = None
        self._last = None


        self._drag_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._poll_drag, self._drag_timer)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        no_activate(self, layered=True)

        user32.SetLayeredWindowAttributes(self.GetHandle(), 0x00FE00FF, self.ALPHA, 3)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_down)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_LEFT_UP, self._on_up)
        self.Bind(wx.EVT_RIGHT_DOWN, lambda e: self.cancel())
        self.Bind(wx.EVT_SET_CURSOR, lambda e: e.SetCursor(wx.Cursor(wx.CURSOR_CROSS)))
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self._on_capture_lost)

    def begin(self, on_done):
        """عکس را می‌گیرد (قبل از نمایش لایه) و لایه را بدون فوکوس روی همان ناحیه می‌گذارد.
        خروجی: (موفق؟، پیام خطا)"""
        if self.active:
            return True, None
        shot, region, err = capture_for_snip(self.app.cfg["capture_monitor"])
        if shot is None:
            return False, err
        self.shot, self.geom = shot, region
        self.scale = (shot.width / float(max(1, region[2])), shot.height / float(max(1, region[3])))
        self.start = self.cur = self._last = None
        self.on_done = on_done
        self.active = True
        try:
            user32.ClipCursor(None)       
        except Exception:
            pass
        place_top(self, *region)
        self._keep_top()
        return True, None

    def _keep_top(self):
        if self.active:
            raise_top(self)
            wx.CallLater(350, self._keep_top)


    def _on_paint(self, evt):
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.BLACK_BRUSH)
        dc.Clear()
        gw, gh = self.geom[2], self.geom[3]
        hint = "بکش تا ناحیه انتخاب شود   —   Esc یا F3 = لغو"
        dc.SetFont(wx.Font(wx.FontInfo(11).FaceName(UI_FONT_FACE).Bold()))
        tw, th = dc.GetTextExtent(hint)
        hx = gw // 2 - (tw + 28) // 2
        dc.SetBrush(wx.Brush(PANEL))
        dc.SetPen(wx.Pen(ACCENT, 1))
        dc.DrawRoundedRectangle(hx, 18, tw + 28, th + 12, 8)
        dc.SetTextForeground(TEXT)
        dc.DrawText(hint, hx + 14, 24)

        if self.start is not None and self.cur is not None:
            x1, y1, x2, y2 = self._sel()
            w, h = x2 - x1, y2 - y1
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(wx.Brush(self.KEY))
            dc.DrawRectangle(x1, y1, w, h)               
            dc.SetPen(wx.Pen(ACCENT, 2))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangle(x1 - 1, y1 - 1, w + 2, h + 2)
            label = "%d × %d" % (w, h)
            dc.SetFont(wx.Font(wx.FontInfo(9).FaceName(UI_FONT_FACE).Bold()))
            lw, lh = dc.GetTextExtent(label)
            lx = min(max(0, x1), max(0, gw - lw - 14))
            ly = y1 - lh - 12 if y1 - lh - 12 > 0 else y1 + 6
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(wx.Brush(PANEL))
            dc.DrawRoundedRectangle(lx, ly, lw + 14, lh + 6, 5)
            dc.SetTextForeground(wx.WHITE)
            dc.DrawText(label, lx + 7, ly + 3)

    def _sel(self):
        return (min(self.start.x, self.cur.x), min(self.start.y, self.cur.y),
                max(self.start.x, self.cur.x), max(self.start.y, self.cur.y))

    def _refresh_sel(self):
        x1, y1, x2, y2 = self._sel()
        gw, gh = self.geom[2], self.geom[3]


        left = max(0, x1 - 8)
        top = max(0, y1 - 42)
        right = min(gw, x2 + 132)
        bottom = min(gh, y2 + 20)
        r = wx.Rect(left, top, max(1, right - left), max(1, bottom - top))
        if self._last is not None:
            r = r.Union(self._last)
            rx, ry = max(0, r.x), max(0, r.y)
            rr, rb = min(gw, r.x + r.width), min(gh, r.y + r.height)
            r = wx.Rect(rx, ry, max(1, rr - rx), max(1, rb - ry))
        self._last = wx.Rect(r)
        self.Refresh(False, r)


    def _local_cursor(self):
        """Global cursor -> layer-local coordinates, clamped to the full display."""
        sx, sy = _cursor_pos()
        gx, gy, gw, gh = self.geom
        return wx.Point(max(0, min(gw, sx - gx)), max(0, min(gh, sy - gy)))

    @staticmethod
    def _left_button_down():
        try:
            return bool(user32.GetAsyncKeyState(0x01) & 0x8000)
        except Exception:
            return False

    def _on_down(self, evt):
        if not self.active:
            return
        self.start = self.cur = self._local_cursor()
        self._last = None
        if not self.HasCapture():
            try:
                self.CaptureMouse()
            except Exception:
                pass
        if not self._drag_timer.IsRunning():
            self._drag_timer.Start(12)

    def _on_motion(self, evt):
        if self.start is not None:
            pos = self._local_cursor()
            if pos != self.cur:
                self.cur = pos
                self._refresh_sel()

    def _poll_drag(self, evt=None):
        if not self.active or self.start is None:
            if self._drag_timer.IsRunning():
                self._drag_timer.Stop()
            return
        pos = self._local_cursor()
        if pos != self.cur:
            self.cur = pos
            self._refresh_sel()


        if not self._left_button_down():
            self._finish_selection(pos)

    def _on_up(self, evt):
        if self.start is not None:
            self._finish_selection(self._local_cursor())

    def _finish_selection(self, pos=None):
        if self.start is None or not self.active:
            return
        if self._drag_timer.IsRunning():
            self._drag_timer.Stop()
        self.cur = pos if pos is not None else self._local_cursor()
        x1, y1, x2, y2 = self._sel()
        self.start = None
        self._release()
        if (x2 - x1) < 6 or (y2 - y1) < 6:
            self.cancel()
            return
        sx, sy = self.scale
        shot = self.shot
        crop = None
        if shot is not None:
            left = max(0, min(shot.width, int(x1 * sx)))
            top = max(0, min(shot.height, int(y1 * sy)))
            right = max(left, min(shot.width, int(x2 * sx)))
            bottom = max(top, min(shot.height, int(y2 * sy)))
            if right > left and bottom > top:
                crop = shot.crop((left, top, right, bottom))
        gx, gy = self.geom[0], self.geom[1]
        cb = self.on_done
        self._close()
        if crop is not None and cb is not None:
            cb(crop, (gx + x1, gy + y1, x2 - x1, y2 - y1))

    def _on_capture_lost(self, evt):


        if self.active and self.start is not None and not self._drag_timer.IsRunning():
            self._drag_timer.Start(12)
        try:
            evt.Skip()
        except Exception:
            pass

    def _release(self):
        try:
            if self.HasCapture():
                self.ReleaseMouse()
        except Exception:
            pass

    def cancel(self):
        if not self.active:
            return
        self._release()
        self.start = None
        self._close()
        self.app.snip_cancelled()

    def _close(self):
        self.active = False
        try:
            if self._drag_timer.IsRunning():
                self._drag_timer.Stop()
        except Exception:
            pass
        self._release()
        self.start = self.cur = self._last = None
        self.shot = None             
        self.on_done = None
        hide_win(self)
        self.app.unregister_esc()
        self.app.panel_resume()





class ResultBox(wx.Frame):
    HINT_H = 20                    
    HINT_LONG = "اسکرول موس = بزرگ‌نمایی / کوچک‌نمایی   •   دابل‌کلیک = کپی"
    HINT_SHORT = "اسکرول = زوم"

    def __init__(self, app):
        super().__init__(None, style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE)
        self.app = app
        self.mode = "hidden"          
        self.status = ""
        self.dots = 0
        self.src = None
        self.bmp = None
        self.rect = [0, 0, 100, 100]
        self.anchor = (0, 0, 100, 100)
        self.flash = False
        self._drag = None
        self._moved = False
        self._top_on = False
        self._timers = {}
        self.saved = None             
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        no_activate(self)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_down)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_LEFT_UP, self._on_up)
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_dclick)
        self.Bind(wx.EVT_RIGHT_DOWN, lambda e: self.hide_box())
        self.Bind(wx.EVT_MOUSEWHEEL, self._on_wheel)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, lambda e: setattr(self, "_drag", None))


    def _later(self, name, ms, fn):
        self._stop(name)
        self._timers[name] = wx.CallLater(ms, fn)

    def _stop(self, name):
        t = self._timers.pop(name, None)
        if t is not None:
            try:
                t.Stop()
            except Exception:
                pass


    def _place(self, x, y, w, h):
        vx, vy, vw, vh = virtual_rect()
        w, h = max(40, min(int(w), vw)), max(30, min(int(h), vh))
        x = max(vx, min(int(x), vx + vw - w))
        y = max(vy, min(int(y), vy + vh - h))
        self.rect = [x, y, w, h]
        place_top(self, x, y, w, h)

    def _ensure_top(self):
        if not self._top_on:
            self._top_on = True
            self._later("top", 400, self._top_tick)

    def _top_tick(self):
        if self.mode == "hidden":
            self._top_on = False
            return
        raise_top(self)
        self._later("top", 400, self._top_tick)

    def show_busy(self, anchor):
        self.anchor = anchor
        self._ensure_top()
        ax, ay, aw, ah = anchor
        self.mode, self.status, self.dots = "busy", "در حال ترجمه", 0
        self.src = self.bmp = None
        self._stop("auto")
        self._place(ax, ay, max(aw, 240), max(ah, 56))
        self.Refresh(False)
        self._later("dots", 400, self._tick)

    def _tick(self):
        if self.mode != "busy":
            return
        self.dots = (self.dots + 1) % 4
        self.Refresh(False)
        self._later("dots", 400, self._tick)

    def set_status(self, text):
        if self.mode == "busy":
            self.status = text
            self.Refresh(False)

    def show_error(self, message):
        self.mode, self.status = "error", message
        self._ensure_top()
        self.src = self.bmp = None
        self._stop("dots")
        ax, ay, aw, ah = self.anchor
        self._place(ax, ay, max(aw, 340), 64)
        self.Refresh(False)
        self._later("auto", 4500, self.hide_box)

    def show_result(self, img):
        self.mode = "result"
        self._ensure_top()
        self._stop("dots")
        self.src = img.convert("RGB")
        ax, ay, aw, ah = self.anchor
        w = max(aw, 260)
        h = int(round(w * self.src.height / float(self.src.width))) + self.HINT_H
        self._place(ax, ay, w, h)
        self._rebuild()
        self.Refresh(False)
        self._later("save", 80, self._save_current)       
        secs = int(self.app.cfg["auto_close_seconds"] or 0)
        self._stop("auto")
        if secs > 0:
            self._later("auto", secs * 1000, self.hide_box)

    def _rebuild(self):
        w, h = self.rect[2], self.rect[3] - self.HINT_H
        if self.src is None or h < 1:
            return
        method = Image.LANCZOS if w < self.src.width else Image.BILINEAR
        self.bmp = pil_to_bitmap(self.src.resize((w, h), method))

    def hide_box(self):
        if self.mode == "hidden":
            return
        self.mode = "hidden"
        self._stop("dots")
        self._stop("auto")
        self._stop("flash")
        self._stop("save")
        self._drag = None
        self.src = self.bmp = None            
        hide_win(self)
        self._delete_saved()                  


    def _save_current(self):
        if self.mode == "result" and self.src is not None:
            self._save(self.src)

    def _save(self, img):
        self._delete_saved()
        try:
            d = self.app.cfg["save_dir"]
            os.makedirs(d, exist_ok=True)
            ms = int(time.time() * 1000) % 1000
            p = os.path.join(d, "%s_%03d.png" % (time.strftime("42OCR_%Y%m%d_%H%M%S"), ms))
            img.save(p, format="PNG", compress_level=1)
            self.saved = p
        except Exception as e:
            dbg("save failed: %s" % e)

    def _delete_saved(self):
        p, self.saved = self.saved, None
        if p:
            try:
                os.remove(p)
            except Exception:
                pass


    def _on_paint(self, evt):
        dc = wx.PaintDC(self)
        w, h = self.GetClientSize()
        dc.SetBackground(wx.Brush(PANEL))
        dc.Clear()
        if self.mode == "result" and self.bmp is not None and self.bmp.IsOk():
            dc.DrawBitmap(self.bmp, 0, 0)

            sy = h - self.HINT_H
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(wx.Brush(PANEL))
            dc.DrawRectangle(0, sy, w, self.HINT_H)
            dc.SetFont(wx.Font(wx.FontInfo(8).FaceName(UI_FONT_FACE)))
            if self.flash:
                text, col = "کپی شد ✓", ACCENT
            else:
                text, col = self.HINT_LONG, MUTED
                if dc.GetTextExtent(text)[0] > w - 12:
                    text = self.HINT_SHORT
            dc.SetTextForeground(col)
            tw, th = dc.GetTextExtent(text)
            dc.DrawText(text, max(4, (w - tw) // 2), sy + (self.HINT_H - th) // 2)
        else:
            dc.SetFont(wx.Font(wx.FontInfo(11).FaceName(UI_FONT_FACE).Bold()))
            err = self.mode == "error"
            text = self.status if err else self.status + "." * self.dots
            dc.SetTextForeground(wx.Colour(255, 120, 130) if err else TEXT)
            tw, th = dc.GetTextExtent(text)
            dc.DrawText(text, max(8, (w - tw) // 2), (h - th) // 2)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen(ACCENT, 2))
        dc.DrawRectangle(0, 0, w, h)

        bx = w - 22
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(wx.Colour(14, 12, 14)))
        dc.DrawRectangle(bx, 2, 20, 18)
        dc.SetFont(wx.Font(wx.FontInfo(9).FaceName(UI_FONT_FACE).Bold()))
        dc.SetTextForeground(TEXT)
        dc.DrawText("✕", bx + 5, 3)


    def _on_down(self, evt):
        w = self.GetClientSize()[0]
        if evt.GetX() >= w - 22 and evt.GetY() <= 20:
            self.hide_box()
            return
        mp = wx.GetMousePosition()
        self._drag = (mp.x - self.rect[0], mp.y - self.rect[1])
        self._moved = False
        if not self.HasCapture():
            self.CaptureMouse()

    def _on_motion(self, evt):
        if self._drag is not None and evt.LeftIsDown():
            mp = wx.GetMousePosition()
            self._moved = True
            self._place(mp.x - self._drag[0], mp.y - self._drag[1], self.rect[2], self.rect[3])

    def _on_up(self, evt):
        self._drag = None
        if self.HasCapture():
            try:
                self.ReleaseMouse()
            except Exception:
                pass

    def _on_dclick(self, evt):
        if self.mode == "result" and self.src is not None:
            try:
                copy_to_clipboard(self.src)
                self.flash = True
                self.Refresh(False)
                self._later("flash", 1200, self._unflash)
            except Exception:
                pass

    def _unflash(self):
        self.flash = False
        self.Refresh(False)

    def _on_wheel(self, evt):
        if self.mode != "result" or self.src is None:
            return
        f = 1.12 if evt.GetWheelRotation() > 0 else 1 / 1.12
        x, y, w, h = self.rect
        vw = virtual_rect()[2]
        nw = max(120, min(int(w * f), vw))
        nh = int(round(nw * self.src.height / float(self.src.width))) + self.HINT_H
        cx, cy = x + w / 2.0, y + h / 2.0
        self._place(cx - nw / 2.0, cy - nh / 2.0, nw, nh)
        self._rebuild()
        self.Refresh(False)





class FloatingPanel(wx.Frame):
    """پنل شناورِ جمع‌وجور؛ تنظیمات در همین پنجره و بدون ساختن فریم تازه نمایش داده می‌شود."""
    W, H_FULL, H_SETTINGS, H_ABOUT, H_MIN = 360, 380, 380, 380, 36
    ALPHA = 242                    
    RADIUS = 14
    AMBER = wx.Colour(255, 190, 60)
    RED = wx.Colour(255, 110, 120)
    BASE = wx.Colour(18, 20, 26)
    SURFACE = wx.Colour(30, 33, 41)
    SURFACE_HOVER = wx.Colour(41, 45, 55)
    EDGE = wx.Colour(57, 62, 73)

    def __init__(self, app):
        super().__init__(None, style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE)
        try:
            self.SetIcon(make_icon())
        except Exception:
            pass
        self.app = app
        self.pinned = bool(self.app.cfg["panel_pinned"])
        self._tray_settings_force_top = False
        try:
            self.s = max(1.0, ctypes.windll.user32.GetDpiForSystem() / 96.0)
        except Exception:
            self.s = 1.0
        self.collapsed = False
        self.page = "main"             
        self.user_hidden = False
        self._suspended = False       
        self._alive = True
        self._hover = None
        self._press = None
        self._drag = None
        self._state = ("برنامه آماده استفاده است", "ok")
        self._rev = None
        self._keeper = None
        self._shape_sz = None
        self._about_bitmap = None
        self._about_bitmap_size = None
        self._back_blink_on = False
        self._blink_timer = None
        self._title_blink_on = True
        self._title_blink_timer = None
        self._ready_blink_on = True
        self._ready_blink_timer = None
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        no_activate(self)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_up)
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, lambda e: self._end_capture())

        w, _h = self._size()
        sw = user32.GetSystemMetrics(0)                       
        self.pos = [max(0, sw - w - self._S(16)), self._S(16)]   
        self._areas = self._build()
        self._apply()

        self._title_blink_on = True
        self._sync_ready_blink()
        self._keep()


    def _S(self, v):
        return int(round(v * self.s))

    def _size(self):
        if self.collapsed:
            h = self.H_MIN
        elif self.page == "settings":
            h = self.H_SETTINGS
        elif self.page == "about":
            h = self.H_ABOUT
        else:
            h = self.H_FULL
        return self._S(self.W), self._S(h)

    def _build(self):
        S, w = self._S, self._S(self.W)

        a = {
            "hdr": wx.Rect(0, 0, w, S(36)),
            "hide": wx.Rect(w - S(38), S(7), S(22), S(22)),
            "collapse": wx.Rect(w - S(66), S(7), S(22), S(22)),
            "pin": wx.Rect(w - S(94), S(7), S(22), S(22)),
        }
        if self.page in ("settings", "about"):
            a["back"] = wx.Rect(w - S(220), S(4), S(112), S(28))
        if not self.collapsed:
            if self.page == "settings":
                a["settings_snip_key"] = wx.Rect(S(12), S(42), w - S(24), S(34))
                a["settings_close_key"] = wx.Rect(S(12), S(81), w - S(24), S(34))
                btn_w, btn_y, btn_h = S(190), S(169), S(38)
                a["browse_dir"] = wx.Rect((w - btn_w) // 2, btn_y, btn_w, btn_h)
                a["monitor_prev"] = wx.Rect(S(12), S(237), S(32), S(35))
                a["monitor_value"] = wx.Rect(S(47), S(237), w - S(94), S(35))
                a["monitor_next"] = wx.Rect(w - S(44), S(237), S(32), S(35))
                a["performance_mode"] = wx.Rect(S(12), S(280), w - S(24), S(38))
            elif self.page == "about":
                a["about_github"] = wx.Rect(S(12), S(46), w - S(24), S(30))
                a["about_telegram"] = wx.Rect(S(12), S(82), w - S(24), S(30))
            else:

                a["snip"] = wx.Rect(S(12), S(151), w - S(24), S(38))
                a["settings"] = wx.Rect(S(12), S(197), w - S(24), S(38))
                a["about_me"] = wx.Rect(S(12), S(243), w - S(24), S(38))
                a["quit"] = wx.Rect(w - S(178), S(328), S(168), S(36))
        return a

    def _monitor_label(self):
        monitors = getattr(self.app, "_monitor_rects_cache", None) or list_monitor_rects()
        try:
            selected = int(self.app.cfg["capture_monitor"] or 0)
        except Exception:
            selected = 0
        if selected <= 0:
            return "خودکار — مانیتور بازی فعال"
        if selected > len(monitors):
            return "مانیتور انتخاب‌شده در دسترس نیست"
        _x, _y, mw, mh = monitors[selected - 1]
        return "مانیتور %d — %d×%d" % (selected, mw, mh)

    def _hit(self, pos):
        for name, r in self._areas.items():
            if name != "hdr" and r.Contains(pos):
                return name
        return "hdr" if self._areas["hdr"].Contains(pos) else None


    def _visible(self):
        return self._alive and not self.user_hidden and not self._suspended

    def _apply(self):
        if self._visible():
            w, h = self._size()
            shape = (w, h)
            if self._shape_sz != shape:
                round_corners(self, w, h, self._S(self.RADIUS))
                self._shape_sz = shape

            vx, vy, vw, vh = virtual_rect()
            self.pos = [max(vx, min(int(self.pos[0]), vx + vw - w)),
                        max(vy, min(int(self.pos[1]), vy + vh - h))]
            if self.pinned or self._tray_settings_force_top:
                place_top(self, self.pos[0], self.pos[1], w, h)
            else:
                place_notop(self, self.pos[0], self.pos[1], w, h)

    def show_panel(self):
        self.user_hidden = False
        self._apply()
        self.Refresh(False)
        notice = getattr(self.app, "tray_notice", None)
        if notice is not None:
            notice.hide_notice()

    def show_settings(self):
        """صفحهٔ تنظیمات را در همان پنل شناور باز می‌کند؛ پنجرهٔ تازه‌ای ساخته نمی‌شود."""
        self.user_hidden = False
        self._suspended = False
        self._tray_settings_force_top = True
        self.page = "settings"
        self.collapsed = False
        self._areas = self._build()
        self._hover = None
        self._start_back_blink()
        self._apply()
        self.Refresh(False)
        notice = getattr(self.app, "tray_notice", None)
        if notice is not None:
            notice.hide_notice()

    def _show_pin_notice(self):
        message = "پنل پین شده است؛ برای مخفی‌کردن یا خروج کامل، ابتدا دکمهٔ 📍 را خاموش کنید."
        try:
            note = wx.adv.NotificationMessage("Translator", message, self)
            note.Show(5)
        except Exception:
            try:
                wx.Bell()
            except Exception:
                pass

    def hide_panel(self):
        if self.pinned:
            self._show_pin_notice()
            return
        self.user_hidden = True
        self._tray_settings_force_top = False
        hide_win(self)
        notice = getattr(self.app, "tray_notice", None)
        if notice is not None:
            notice.show_notice()

    def toggle(self):
        if self.user_hidden:
            self.show_panel()
        else:
            self.hide_panel()

    def suspend(self):
        """هنگام گرفتن عکس: پنل پنهان می‌شود. اگر دیده می‌شد True برمی‌گرداند."""
        was = self._visible()
        self._suspended = True
        if was:
            hide_win(self)
        return was

    def resume(self):
        self._suspended = False
        self._apply()

    def _keep(self):
        if not self._alive:
            return
        if self._visible() and self.pinned:
            try:
                raise_top(self)                 
            except Exception:
                pass
        self._keeper = wx.CallLater(500, self._keep)

    def toggle_pin(self):
        self.pinned = not self.pinned
        if not self.pinned:
            self._tray_settings_force_top = False
        self.app.cfg.set("panel_pinned", self.pinned)
        self._apply()
        self.Refresh(False)
        if self.pinned:
            self._show_pin_notice()
        else:
            try:
                wx.adv.NotificationMessage("Translator", "پین غیرفعال شد؛ اکنون می‌توانید پنل را با × مخفی کنید.", self).Show(4)
            except Exception:
                pass

    def shutdown(self):
        self._alive = False
        for t in (self._keeper, self._rev, self._blink_timer,
                  self._title_blink_timer, self._ready_blink_timer):
            try:
                if t is not None:
                    t.Stop()
            except Exception:
                pass


    def set_state(self, text, kind="ok", revert_ms=0):
        if not self._alive:
            return
        self._state = (text, kind)
        try:
            if self._rev is not None:
                self._rev.Stop()
        except Exception:
            pass
        self._rev = None
        self._sync_ready_blink()
        if revert_ms:
            self._rev = wx.CallLater(
                revert_ms, lambda: self.set_state("برنامه آماده استفاده است", "ok"))
        self.Refresh(False)

    def _start_title_blink(self):
        """عنوان Translator ثابت می‌ماند و چشمک نمی‌زند."""
        try:
            if self._title_blink_timer is not None:
                self._title_blink_timer.Stop()
        except Exception:
            pass
        self._title_blink_timer = None
        self._title_blink_on = True

    def _tick_title_blink(self):

        self._title_blink_timer = None
        self._title_blink_on = True

    def _sync_ready_blink(self):
        """فقط وضعیت آماده‌به‌کار با متن سفید و نشانگر سبز چشمک می‌زند."""
        is_ready = self._state == ("برنامه آماده استفاده است", "ok")
        if not is_ready:
            try:
                if self._ready_blink_timer is not None:
                    self._ready_blink_timer.Stop()
            except Exception:
                pass
            self._ready_blink_timer = None
            self._ready_blink_on = True
            return
        if self._ready_blink_timer is None:
            self._ready_blink_on = True
            self._ready_blink_timer = wx.CallLater(520, self._tick_ready_blink)

    def _tick_ready_blink(self):
        self._ready_blink_timer = None
        if not self._alive or self._state != ("برنامه آماده استفاده است", "ok"):
            return
        self._ready_blink_on = not self._ready_blink_on
        self.Refresh(False)
        self._ready_blink_timer = wx.CallLater(520, self._tick_ready_blink)

    def refresh(self):
        if self._alive:
            self.Refresh(False)

    def _start_back_blink(self):
        """نام قدیمی برای سازگاری؛ دکمه‌ی بازگشت ثابت است و چشمک نمی‌زند."""
        try:
            if self._blink_timer is not None:
                self._blink_timer.Stop()
        except Exception:
            pass
        self._blink_timer = None
        self._back_blink_on = False
        self.Refresh(False)

    def _tick_back_blink(self):

        self._blink_timer = None
        self._back_blink_on = False

    def _stop_back_blink(self):
        try:
            if self._blink_timer is not None:
                self._blink_timer.Stop()
        except Exception:
            pass
        self._blink_timer = None
        self._back_blink_on = False


    @staticmethod
    def _font(size, bold=False):
        return wx.Font(wx.FontInfo(size).FaceName(UI_FONT_FACE).Bold(bold))

    @staticmethod
    def _fit(dc, text, maxw):
        if dc.GetTextExtent(text)[0] <= maxw:
            return text
        while len(text) > 1 and dc.GetTextExtent(text + "…")[0] > maxw:
            text = text[:-1]
        return text + "…"

    def _pin_btn(self, g, dc):
        S, r = self._S, self._areas["pin"]
        hot = self._hover == "pin"
        if self.pinned:
            fill = wx.Colour(255, 214, 0)
            pen = wx.Colour(255, 214, 0)
            glyph = wx.Colour(18, 20, 26)
        else:
            fill = self.SURFACE_HOVER if hot else self.BASE
            pen = self.EDGE if hot else self.BASE
            glyph = wx.WHITE if hot else MUTED
        g.SetPen(wx.Pen(pen, 1))
        g.SetBrush(wx.Brush(fill))
        g.DrawRoundedRectangle(r, S(6))
        dc.SetFont(wx.Font(wx.FontInfo(13).FaceName("Segoe UI Emoji")))
        dc.SetTextForeground(glyph)
        label = "📍"
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, r.x + (r.width - tw) // 2, r.y + (r.height - th) // 2 - S(1))

    def _icon_btn(self, g, dc, name, label):
        r = self._areas[name]
        hot = self._hover == name
        is_back = name == "back" and self.page in ("settings", "about")
        if is_back or hot:
            g.SetPen(wx.TRANSPARENT_PEN)
            fill = wx.Colour(210, 35, 51) if is_back and hot else (ACCENT if is_back else wx.Colour(54, 50, 60))
            g.SetBrush(wx.Brush(fill))
            g.DrawRoundedRectangle(r, self._S(6))
        dc.SetFont(self._font(12 if is_back else 10, True))
        dc.SetTextForeground(wx.WHITE if is_back or hot else MUTED)
        if is_back:
            label = self._fit(dc, label, r.width - self._S(12))
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, r.x + (r.width - tw) // 2, r.y + (r.height - th) // 2)

    def _btn(self, g, dc, name, label, primary=False):
        S, r = self._S, self._areas[name]
        hot = self._hover == name
        down = hot and self._press == name
        if name == "about_me":
            col = wx.Colour(132, 190, 0) if down else (wx.Colour(196, 255, 24) if hot else wx.Colour(180, 255, 0))
            fg = wx.Colour(12, 16, 8)
        elif primary:
            col = wx.Colour(214, 34, 50) if down else (wx.Colour(255, 67, 82) if hot else ACCENT)
            fg = wx.WHITE
        else:
            col = wx.Colour(48, 52, 63) if down else (self.SURFACE_HOVER if hot else self.SURFACE)
            fg = TEXT
        g.SetPen(wx.Pen(self.EDGE if not primary else col, 1) if name in ("settings", "browse_dir", "about_me") else wx.TRANSPARENT_PEN)
        g.SetBrush(wx.Brush(col))
        g.DrawRoundedRectangle(r, S(8 if name in ("settings", "browse_dir", "about_me") else 10))

        dc.SetFont(self._font(16 if name == "browse_dir" else 10, True))
        dc.SetTextForeground(fg)
        label = self._fit(dc, label, r.width - S(10))
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, r.x + (r.width - tw) // 2, r.y + (r.height - th) // 2)

    def _keychip(self, g, dc, name, key):
        """دکمه‌ی کلیدِ کنار هر دکمه: کلیک → هر کلیدی بزنی همان ثبت می‌شود."""
        S, r = self._S, self._areas[name]
        hot = self._hover == name
        cap = self.app._cap is not None and self.app._cap["key"] == key
        if cap:
            fill, pen, text, fg = wx.Colour(92, 28, 39), ACCENT, "…", wx.WHITE
        else:
            fill = self.SURFACE_HOVER if hot else wx.Colour(27, 30, 37)
            pen, fg = (ACCENT if hot else self.EDGE), TEXT
            text = str(self.app.cfg[key]).upper()
        g.SetPen(wx.Pen(pen, 1))
        g.SetBrush(wx.Brush(fill))
        g.DrawRoundedRectangle(r, S(9))
        dc.SetFont(self._font(9, True))
        dc.SetTextForeground(fg)
        text = self._fit(dc, text, r.width - S(8))
        tw, th = dc.GetTextExtent(text)
        dc.DrawText(text, r.x + (r.width - tw) // 2, r.y + (r.height - th) // 2)

    def _settings_key_row(self, g, dc, name, label, key):
        """ردیف انتخاب کلید در صفحه‌ی تنظیمات؛ کل ردیف قابل کلیک است."""
        S, r = self._S, self._areas[name]
        hot = self._hover == name
        cap = self.app._cap is not None and self.app._cap["key"] == key
        g.SetPen(wx.Pen(ACCENT if cap else (self.EDGE if not hot else wx.Colour(91, 97, 112)), 1))
        g.SetBrush(wx.Brush(self.SURFACE_HOVER if hot else self.SURFACE))
        g.DrawRoundedRectangle(r, S(7))
        dc.SetFont(self._font(15, True))
        dc.SetTextForeground(TEXT)
        chip = wx.Rect(r.x + S(8), r.y + S(4), S(96), r.height - S(8))
        label_area = wx.Rect(chip.x + chip.width + S(8), r.y, max(1, r.x + r.width - S(10) - (chip.x + chip.width + S(8))), r.height)
        dc.DrawLabel(label, label_area, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

        g.SetPen(wx.Pen(ACCENT if cap else self.EDGE, 1))
        g.SetBrush(wx.Brush(wx.Colour(88, 27, 38) if cap else wx.Colour(24, 27, 34)))
        g.DrawRoundedRectangle(chip, S(5))
        value = "…" if cap else str(self.app.cfg[key]).upper()
        dc.SetFont(self._font(14, True))
        dc.SetTextForeground(wx.WHITE if cap else wx.Colour(220, 224, 232))
        value = self._fit(dc, value, chip.width - S(8))
        tw, th = dc.GetTextExtent(value)
        dc.DrawText(value, chip.x + (chip.width - tw) // 2, chip.y + (chip.height - th) // 2)

    def _get_about_bitmap(self):
        """تصویر پروفایل را از داده‌ی جاسازی‌شده می‌سازد و برای هر DPI کش می‌کند."""
        target = (max(1, self._S(276)), max(1, self._S(131)))
        if self._about_bitmap is not None and self._about_bitmap_size == target:
            return self._about_bitmap
        try:
            raw = base64.b64decode(ABOUT_IMAGE_B64)
            with Image.open(io.BytesIO(raw)) as source:
                picture = source.convert("RGB").resize(target, Image.LANCZOS)
            self._about_bitmap = pil_to_bitmap(picture)
            self._about_bitmap_size = target
        except Exception as exc:
            dbg("about image load failed: %s" % exc)
            self._about_bitmap = wx.NullBitmap
            self._about_bitmap_size = target
        return self._about_bitmap

    def _on_paint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        S = self._S
        w, h = self.GetClientSize()
        dc.SetBackground(wx.Brush(self.BASE))
        dc.Clear()
        g = dc


        g.SetPen(wx.Pen(self.EDGE, 1))
        g.SetBrush(wx.TRANSPARENT_BRUSH)
        g.DrawRoundedRectangle(0, 0, max(1, w - 1), max(1, h - 1), S(12))
        g.SetPen(wx.TRANSPARENT_PEN)
        g.SetBrush(wx.Brush(ACCENT))
        g.DrawRectangle(S(1), S(1), max(1, w - S(2)), S(2))


        if self.page == "main" and not self.collapsed:
            brand = make_brand_bitmap(S(128), S(128))
            if brand.IsOk():
                dc.DrawBitmap(brand, S(6), S(6), True)
            dc.SetFont(self._font(20, True))
            dc.SetTextForeground(wx.WHITE)
            dc.DrawText("Translator", S(143), S(42))
            dc.SetFont(self._font(16, True))
            dc.SetTextForeground(wx.Colour(203, 208, 218))
            dc.DrawLabel("ترجمه سریع متون", wx.Rect(S(143), S(80), w - S(155), S(30)),
                         wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        else:
            brand = make_brand_bitmap(S(24), S(24))
            if brand.IsOk():
                dc.DrawBitmap(brand, S(7), S(6), True)
            dc.SetFont(self._font(12 if self.page in ("settings", "about") else 9, True))
            title = {"settings": "تنظیمات", "about": "About Me"}.get(self.page, "Translator")
            dc.SetTextForeground(TEXT if self.page == "settings" else wx.WHITE)
            dc.DrawText(title, S(36), (S(36) - dc.GetTextExtent(title)[1]) // 2 + S(1))
        self._pin_btn(g, dc)
        self._icon_btn(g, dc, "collapse", "+" if self.collapsed else "–")
        self._icon_btn(g, dc, "hide", "✕")
        if self.page in ("settings", "about"):
            self._icon_btn(g, dc, "back", "‹ صفحه قبل")
        if self.collapsed:
            return

        if self.page == "settings":
            self._settings_key_row(g, dc, "settings_snip_key", "کلید ترجمه", "snip_hotkey")
            self._settings_key_row(g, dc, "settings_close_key", "کلید بستن نتیجه", "close_hotkey")

            dc.SetFont(self._font(15, True))
            dc.SetTextForeground(MUTED)
            dc.DrawLabel("پوشه‌ی ذخیره‌ی تصویرها", wx.Rect(S(12), S(119), w - S(24), S(23)),
                         wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
            dc.SetFont(self._font(14, True))
            dc.SetTextForeground(wx.Colour(220, 224, 232))
            path = _short_path(str(self.app.cfg["save_dir"]), 38)
            path = self._fit(dc, path, w - S(24))
            dc.DrawLabel(path, wx.Rect(S(12), S(142), w - S(24), S(22)),
                         wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

            self._btn(g, dc, "browse_dir", "انتخاب پوشه", primary=False)

            dc.SetFont(self._font(15, True))
            dc.SetTextForeground(MUTED)
            dc.DrawLabel("مانیتور عکس‌برداری", wx.Rect(S(12), S(211), w - S(24), S(23)),
                         wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
            for name, arrow in (("monitor_prev", "‹"), ("monitor_next", "›")):
                r = self._areas[name]
                hot = self._hover == name
                g.SetPen(wx.Pen(self.EDGE, 1))
                g.SetBrush(wx.Brush(self.SURFACE_HOVER if hot else self.SURFACE))
                g.DrawRoundedRectangle(r, S(6))
                dc.SetFont(self._font(17, True))
                dc.SetTextForeground(TEXT)
                tw, th = dc.GetTextExtent(arrow)
                dc.DrawText(arrow, r.x + (r.width - tw) // 2, r.y + (r.height - th) // 2 - S(1))
            mr = self._areas["monitor_value"]
            g.SetPen(wx.Pen(ACCENT if self._hover == "monitor_value" else self.EDGE, 1))
            g.SetBrush(wx.Brush(self.SURFACE_HOVER if self._hover == "monitor_value" else self.SURFACE))
            g.DrawRoundedRectangle(mr, S(6))
            dc.SetFont(self._font(15, True))
            dc.SetTextForeground(TEXT)
            monitor_label = self._fit(dc, self._monitor_label(), mr.width - S(8))
            dc.DrawLabel(monitor_label, mr, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

            pr = self._areas["performance_mode"]
            perf_hot = self._hover == "performance_mode"
            g.SetPen(wx.Pen(self.EDGE, 1))
            g.SetBrush(wx.Brush(self.SURFACE_HOVER if perf_hot else self.SURFACE))
            g.DrawRoundedRectangle(pr, S(7))
            dc.SetFont(self._font(15, True))
            dc.SetTextForeground(TEXT)
            label_rect = wx.Rect(pr.x + S(60), pr.y, max(1, pr.width - S(72)), pr.height)
            dc.DrawLabel("حالت کم‌مصرف", label_rect, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
            perf_text = "روشن" if self.app.cfg["performance_mode"] else "خاموش"
            perf_color = wx.Colour(52, 201, 142) if self.app.cfg["performance_mode"] else MUTED
            dc.SetTextForeground(perf_color)
            status_rect = wx.Rect(pr.x + S(8), pr.y, S(52), pr.height)
            dc.DrawLabel(perf_text, status_rect, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

            text, kind = self._state
            is_ready = text == "برنامه آماده استفاده است" and kind == "ok"
            col = {"ok": wx.Colour(52, 201, 142), "busy": self.AMBER, "err": self.RED}.get(kind, wx.Colour(52, 201, 142))
            if not is_ready or self._ready_blink_on:
                g.SetPen(wx.TRANSPARENT_PEN)
                g.SetBrush(wx.Brush(col))
                g.DrawCircle(S(17), S(348), S(3))
            dc.SetFont(self._font(14))
            dc.SetTextForeground(wx.WHITE if is_ready and self._ready_blink_on else (wx.Colour(91, 96, 108) if is_ready else MUTED))
            dc.DrawText(self._fit(dc, text, w - S(42)), S(28), S(340))
            return

        if self.page == "about":

            for key, label in (("about_github", "github.com/AghaErfan"),
                               ("about_telegram", "t.me/s04ial")):
                link_rect = self._areas[key]
                hot = self._hover == key
                g.SetPen(wx.Pen(wx.Colour(75, 111, 162) if hot else wx.Colour(53, 73, 105), 1))
                g.SetBrush(wx.Brush(wx.Colour(34, 44, 61) if hot else wx.Colour(25, 31, 43)))
                g.DrawRoundedRectangle(link_rect, S(7))
                dc.SetFont(self._font(11, True))
                dc.SetTextForeground(wx.Colour(151, 199, 255))
                dc.DrawLabel(label, link_rect, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
            bitmap = self._get_about_bitmap()
            if bitmap and bitmap.IsOk():
                dc.DrawBitmap(bitmap, max(0, (w - bitmap.GetWidth()) // 2), S(121), True)
            return

        self._btn(g, dc, "snip", "شروع ترجمه", primary=True)
        self._btn(g, dc, "settings", "تنظیمات", primary=False)
        self._btn(g, dc, "about_me", "About Me", primary=False)

        text, kind = self._state
        is_ready = text == "برنامه آماده استفاده است" and kind == "ok"
        col = {"ok": wx.Colour(52, 201, 142), "busy": self.AMBER, "err": self.RED}.get(kind, wx.Colour(52, 201, 142))
        cy = S(346)
        if not is_ready or self._ready_blink_on:
            g.SetPen(wx.TRANSPARENT_PEN)
            g.SetBrush(wx.Brush(col))
            g.DrawCircle(S(17), cy, S(4))
        dc.SetFont(self._font(9))
        dc.SetTextForeground(wx.WHITE if is_ready and self._ready_blink_on else (wx.Colour(91, 96, 108) if is_ready else MUTED))
        t = self._fit(dc, text, S(150))
        dc.DrawText(t, S(28), cy - dc.GetTextExtent(t)[1] // 2)
        q = self._areas["quit"]
        quit_hot = self._hover == "quit"
        g.SetPen(wx.Pen(wx.Colour(255, 214, 0), 1))
        g.SetBrush(wx.Brush(wx.Colour(255, 214, 0) if not quit_hot else wx.Colour(255, 229, 77)))
        g.DrawRoundedRectangle(q, S(7))
        dc.SetFont(self._font(10, True))
        dc.SetTextForeground(wx.Colour(20, 22, 26))
        quit_text = self._fit(dc, "خروج کامل از برنامه", q.width - S(12))
        tw, th = dc.GetTextExtent(quit_text)
        dc.DrawText(quit_text, q.x + (q.width - tw) // 2, q.y + (q.height - th) // 2)


    def _end_capture(self):
        self._drag = None
        self._press = None

    def _release(self):
        try:
            if self.HasCapture():
                self.ReleaseMouse()
        except Exception:
            pass

    def _on_down(self, evt):
        name = self._hit(evt.GetPosition())
        if name in (None, "hdr"):
            mp = wx.GetMousePosition()
            self._drag = (mp.x - self.pos[0], mp.y - self.pos[1])
        else:
            self._press = name
        if not self.HasCapture():
            self.CaptureMouse()
        self.Refresh(False)

    def _on_motion(self, evt):
        if self._drag is not None and evt.LeftIsDown():
            mp = wx.GetMousePosition()
            self._move(mp.x - self._drag[0], mp.y - self._drag[1])
            return
        name = self._hit(evt.GetPosition())
        name = None if name in (None, "hdr") else name
        if name != self._hover:
            self._hover = name
            self.Refresh(False)

    def _on_leave(self, evt):
        if self._hover is not None and not self.HasCapture():
            self._hover = None
            self.Refresh(False)

    def _on_up(self, evt):
        name = self._hit(evt.GetPosition())
        pressed, self._press, self._drag = self._press, None, None
        self._release()
        self.Refresh(False)
        if pressed and pressed == name:
            wx.CallAfter(self._do, pressed)

    def _move(self, x, y):
        vx, vy, vw, vh = virtual_rect()
        w, h = self._size()
        self.pos = [max(vx, min(int(x), vx + vw - w)), max(vy, min(int(y), vy + vh - h))]
        self._apply()


    def _do(self, name):
        if not self._alive:
            return
        if name == "pin":
            self.toggle_pin()
        elif name == "settings":
            self.page = "settings"
            self._areas = self._build()
            self._hover = None
            self._start_back_blink()
            self._apply()
            self.Refresh(False)
        elif name == "about_me":
            self.page = "about"
            self._areas = self._build()
            self._hover = None
            self._apply()
            self.Refresh(False)
        elif name == "about_github":
            try:
                wx.LaunchDefaultBrowser("https://github.com/AghaErfan")
            except Exception as exc:
                dbg("launch GitHub failed: %s" % exc)
        elif name == "about_telegram":
            try:
                wx.LaunchDefaultBrowser("https://t.me/s04ial")
            except Exception as exc:
                dbg("launch Telegram failed: %s" % exc)
        elif name == "back":
            self._stop_back_blink()
            self._tray_settings_force_top = False
            self.page = "main"
            self._areas = self._build()
            self._hover = None
            self._apply()
            self.Refresh(False)
        elif name == "settings_snip_key":
            self.app.capture_hotkey("snip_hotkey")
        elif name == "settings_close_key":
            self.app.capture_hotkey("close_hotkey")
        elif name == "browse_dir":
            self.app.choose_save_dir()
        elif name == "monitor_prev":
            self.app.change_capture_monitor(-1)
        elif name == "monitor_next":
            self.app.change_capture_monitor(1)
        elif name == "monitor_value":
            self.app.change_capture_monitor(1)
        elif name == "performance_mode":
            self.app.toggle_performance_mode()
        elif name == "snip":
            self.app.start_snip()
        elif name == "quit":
            self.app.quit()
        elif name == "collapse":
            self.collapsed = not self.collapsed
            self._areas = self._build()
            self._hover = None
            self._apply()
            self.Refresh(False)
        elif name == "hide":


            self.hide_panel()





def _short_path(p, n=46):
    p = str(p)
    return p if len(p) <= n else p[:14] + "…" + p[-(n - 15):]


class TrayStatusNotice(wx.Frame):
    """پیام کوچک و ثابت بالای ناحیهٔ ساعت؛ با بازشدن پنل پنهان می‌شود."""
    def __init__(self, app):
        super().__init__(None, title="", size=(352, 58),
                         style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE)
        self.app = app
        try:
            self.s = max(1.0, ctypes.windll.user32.GetDpiForSystem() / 96.0)
        except Exception:
            self.s = 1.0
        self._visible_notice = False
        self._keep_timer = None
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        no_activate(self)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_LEFT_UP, lambda e: wx.CallAfter(self.app.panel.show_panel))
        self.Bind(wx.EVT_RIGHT_UP, lambda e: self.hide_notice())
        self.Hide()

    def _S(self, value):
        return int(round(value * self.s))

    def _clock_and_taskbar_rects(self):
        """تا جای ممکن مختصات ساعت را از پنجرهٔ Taskbar می‌خواند؛ fallback پایین-راست است."""
        taskbar = None
        clock = None
        try:
            user32.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
            user32.FindWindowW.restype = ctypes.c_void_p
            user32.EnumChildWindows.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
            user32.EnumChildWindows.restype = ctypes.c_bool
            taskbar = user32.FindWindowW("Shell_TrayWnd", None)
            if not taskbar:
                taskbar = user32.FindWindowW("Shell_SecondaryTrayWnd", None)
            if taskbar:
                taskbar_rect = _rect_of(taskbar)
                found = []
                def child_cb(hwnd, _):
                    try:
                        cname = _class_of(hwnd).lower()
                        title = _text_of(hwnd).lower()
                        if "clock" in cname or "trayclock" in cname or "datetime" in cname or "clock" in title:
                            r = _rect_of(hwnd)
                            if (r[2] - r[0]) >= 20 and (r[3] - r[1]) >= 10:
                                found.append(r)
                    except Exception:
                        pass
                    return True
                callback = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(child_cb)
                user32.EnumChildWindows(taskbar, callback, 0)
                if found:

                    clock = min(found, key=lambda r: (r[2]-r[0]) * (r[3]-r[1]))
                return taskbar_rect, clock
        except Exception:
            pass
        vx, vy, vw, vh = virtual_rect()
        return (vx, vy + vh - self._S(48), vx + vw, vy + vh), None

    def _position_notice(self):
        width, height = self._S(352), self._S(58)
        taskbar, clock = self._clock_and_taskbar_rects()
        tx1, ty1, tx2, ty2 = taskbar
        try:
            hmon = user32.MonitorFromPoint(POINT(int((clock[0]+clock[2])//2), int((clock[1]+clock[3])//2)), 2) if clock else user32.MonitorFromPoint(POINT(tx2-5, ty1+5), 2)
            mx, my, mw, mh = _mon_rect(hmon)
        except Exception:
            mx, my, mw, mh = virtual_rect()

        if ty1 > my + mh // 2:
            y = ty1 - height - self._S(7)
        elif ty2 < my + mh // 2:
            y = ty2 + self._S(7)
        else:
            y = max(my, min((clock[1] if clock else ty1) - height - self._S(7), my + mh - height))
        if clock:
            x = (clock[0] + clock[2] - width) if (clock[0] + clock[2] - width) >= mx else clock[0]
        else:
            x = tx2 - width - self._S(12)
        x = max(mx + self._S(4), min(int(x), mx + mw - width - self._S(4)))
        y = max(my + self._S(4), min(int(y), my + mh - height - self._S(4)))
        return int(x), int(y), width, height

    def show_notice(self):
        if not self or self.app._quitting:
            return
        self._visible_notice = True
        x, y, w, h = self._position_notice()
        round_corners(self, w, h, self._S(10))
        place_top(self, x, y, w, h)
        self.Refresh(False)
        self._schedule_keep()

    def hide_notice(self):
        self._visible_notice = False
        try:
            if self._keep_timer is not None:
                self._keep_timer.Stop()
        except Exception:
            pass
        self._keep_timer = None
        hide_win(self)

    def _schedule_keep(self):
        try:
            if self._keep_timer is not None:
                self._keep_timer.Stop()
        except Exception:
            pass
        if self._visible_notice and not self.app._quitting:
            self._keep_timer = wx.CallLater(1200, self._keep_top)

    def _keep_top(self):
        self._keep_timer = None
        if not self._visible_notice or self.app._quitting:
            return
        x, y, w, h = self._position_notice()
        place_top(self, x, y, w, h)
        self._schedule_keep()

    def _on_paint(self, evt):
        dc = wx.AutoBufferedPaintDC(self)
        S = self._S
        w, h = self.GetClientSize()
        dc.SetBackground(wx.Brush(wx.Colour(20, 22, 29)))
        dc.Clear()
        dc.SetPen(wx.Pen(wx.Colour(62, 67, 80), S(1)))
        dc.SetBrush(wx.Brush(wx.Colour(20, 22, 29)))
        dc.DrawRoundedRectangle(0, 0, max(1, w - 1), max(1, h - 1), S(9))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(wx.Colour(255, 45, 60)))
        dc.DrawRoundedRectangle(S(1), S(1), w - S(2), S(3), S(2))
        logo = make_brand_bitmap(S(20), S(20))
        if logo and logo.IsOk():
            dc.DrawBitmap(logo, S(6), S(12), True)
        text_x = S(30)
        area = wx.Rect(text_x, S(5), max(1, w - text_x - S(10)), S(24))
        dc.SetFont(wx.Font(wx.FontInfo(10).FaceName(UI_FONT_FACE).Bold()))
        dc.SetTextForeground(wx.Colour(242, 244, 248))
        dc.DrawLabel("برنامه در تسک‌بار در حال اجرا است", area,
                     wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        area2 = wx.Rect(text_x, S(29), max(1, w - text_x - S(10)), S(22))
        dc.SetFont(wx.Font(wx.FontInfo(9).FaceName(UI_FONT_FACE).Bold()))
        dc.SetTextForeground(wx.Colour(194, 200, 212))
        dc.DrawLabel("برای باز کردن پنل روی این پیام کلیک کنید.", area2,
                     wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

    def shutdown(self):
        self.hide_notice()


class Tray(wx.adv.TaskBarIcon):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.update_tip()
        # کلیک چپ روی آیکون Tray پنل شناور را نمایش می‌دهد؛ اسنیپ فقط از دکمه/کلید ترجمه شروع می‌شود.
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_UP, lambda e: wx.CallAfter(self.app.panel.show_panel))

    def update_tip(self):
        self.SetIcon(make_icon(), "Translator — %s" % self.app.cfg["snip_hotkey"].upper())

    def _on_settings_menu(self, event):
        # Open the in-panel settings page after the native tray menu has closed.
        wx.CallAfter(self.app.panel.show_settings)

    def CreatePopupMenu(self):
        app = self.app
        m = wx.Menu()

        su = m.AppendCheckItem(wx.ID_ANY, "شروع با اجرای ویندوز")
        su.Check(bool(app.cfg["run_on_startup"]))
        self.Bind(wx.EVT_MENU, lambda e: wx.CallAfter(app.toggle_startup), su)

        pn = m.AppendCheckItem(wx.ID_ANY, "نمایش پنل شناور")
        pn.Check(not app.panel.user_hidden)
        self.Bind(wx.EVT_MENU, lambda e: wx.CallAfter(app.panel.toggle), pn)

        st = m.Append(wx.ID_ANY, "تنظیمات")
        self.Bind(wx.EVT_MENU, self._on_settings_menu, st)

        m.AppendSeparator()
        ex = m.Append(wx.ID_ANY, "خروج کامل از برنامه")
        self.Bind(wx.EVT_MENU, lambda e: app.quit(), ex)
        return m





ID_SNIP, ID_CLOSE, ID_ESC = 101, 102, 103


class SnipApp(wx.Frame):
    def __init__(self, background=False):
        super().__init__(None)                
        try:
            self.SetIcon(make_icon())
        except Exception:
            pass
        self.cfg = Config()
        self._monitor_rects_cache = list_monitor_rects()
        self._quitting = False
        self._last_key = 0.0
        self._last_snip_done = 0.0
        self._armed = True            
        self._esc_on = False
        self._pending = None
        self._cap = None              

        self.layer = SnipLayer(self)
        self.box = ResultBox(self)
        self.panel = FloatingPanel(self)
        self.tray_notice = TrayStatusNotice(self)
        self.worker = None if self.cfg["performance_mode"] else TranslateWorker(
            self._on_result, self._on_error, self._on_state)
        self._worker_release_pending = False
        self.tray = Tray(self)

        self.Bind(wx.EVT_HOTKEY, self._on_hotkey)

        self._combo_snip = parse_hotkey(self.cfg["snip_hotkey"])
        self._combo_close = parse_hotkey(self.cfg["close_hotkey"])
        self._prev = {"snip": False, "close": False, "esc": False}
        self._poll = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._poll_keys, self._poll)
        self._poll.Start(65 if self.cfg["performance_mode"] else 25)
        self.Bind(wx.EVT_CLOSE, lambda e: self.quit())
        for hid, key in ((ID_SNIP, "snip_hotkey"), (ID_CLOSE, "close_hotkey")):
            mods, vk = parse_hotkey(self.cfg[key])
            if vk is not None:
                self.RegisterHotKey(hid, mods, vk)    

        threading.Thread(target=self._sync_startup, daemon=True).start()
        if not background:
            try:
                wx.adv.NotificationMessage(
                    "Translator",
                    "برنامه آماده استفاده است — %s = انتخاب ناحیه و ترجمه" % self.cfg["snip_hotkey"].upper()).Show(3)
            except Exception:
                pass


    def _on_hotkey(self, evt):
        if self._cap is not None:         
            return
        i = evt.GetId()
        if i == ID_SNIP:
            self._trigger_snip()
        elif i == ID_CLOSE:
            if self._combo_close == (0, 0x1B) and self.layer.active:
                self.layer.cancel()
            else:
                self.box.hide_box()
        elif i == ID_ESC:
            if self.layer.active:
                self.layer.cancel()
            elif self.box.mode != "hidden":
                self.box.hide_box()

    def _trigger_snip(self):
        if self._cap is not None:
            return
        now = time.time()


        if not self._armed or now - self._last_key < 0.6:
            return
        self._armed = False
        self._last_key = now
        if self.layer.active:
            self.layer.cancel()
        else:
            self.start_snip()
        self._last_key = time.time()      

    @staticmethod
    def _combo_down(combo):
        mods, vk = combo
        if vk is None or not (user32.GetAsyncKeyState(vk) & 0x8000):
            return False
        for flag, k in ((1, 0x12), (2, 0x11), (4, 0x10), (8, 0x5B)):
            if (mods & flag) and not (user32.GetAsyncKeyState(k) & 0x8000):
                return False
        return True

    def _poll_keys(self, evt):
        if self._quitting or self._cap is not None:
            return
        s = self._combo_down(self._combo_snip)
        if s and not self._prev["snip"]:
            self._trigger_snip()
        self._prev["snip"] = s
        if not s and not self._armed and time.time() - self._last_key > 0.3:
            self._armed = True            
        c = self._combo_down(self._combo_close)
        if c and not self._prev["close"]:
            self.box.hide_box()
        self._prev["close"] = c

        esc_needed = self.layer.active or self.box.mode != "hidden"
        e = bool(esc_needed and (user32.GetAsyncKeyState(0x1B) & 0x8000))
        if e and not self._prev["esc"]:
            if self.layer.active:
                self.layer.cancel()
            elif self.box.mode != "hidden":
                self.box.hide_box()
        self._prev["esc"] = e

    def register_esc(self):
        if self._combo_close == (0, 0x1B):
            self._esc_on = False
            return
        if not self._esc_on:
            self._esc_on = bool(self.RegisterHotKey(ID_ESC, 0, 0x1B))

    def unregister_esc(self):
        if self._esc_on:
            self._esc_on = False
            try:
                self.UnregisterHotKey(ID_ESC)
            except Exception:
                pass


    def start_snip(self):
        if self.layer.active or self._quitting:
            return

        self.tray_notice.hide_notice()
        self._pending = None
        if self.box.mode != "hidden":
            self.box.hide_box()
            time.sleep(0.04)              
        if self.panel.suspend():          
            time.sleep(0.05)
        ok, err = self.layer.begin(self._on_snip)
        if ok:
            self.register_esc()
        else:
            self.panel.resume()
            vx, vy, vw, vh = virtual_rect()
            self.box.anchor = (vx + 80, vy + 80, 400, 64)
            self.box.show_error(err or "گرفتن عکس صفحه ممکن نشد")

    def snip_cancelled(self):

        p, self._pending = self._pending, None
        if p is not None:
            p()

    def _on_snip(self, img, rect):
        now = time.time()
        if now - self._last_snip_done < 0.5:      
            return
        self._last_snip_done = now
        self._pending = None
        self.box.show_busy(rect)
        self.panel.set_state("در حال ترجمه", "busy")
        worker = self._ensure_worker()
        worker.start(img)

    def _ensure_worker(self):
        if self.worker is None:
            self.worker = TranslateWorker(self._on_result, self._on_error, self._on_state)
        return self.worker

    def _release_worker_if_idle(self):
        if self._quitting:
            return
        if not self.cfg["performance_mode"] or self.worker is None:
            self._worker_release_pending = False
            return
        if getattr(self.worker, "_busy", False):
            self._worker_release_pending = True
            return
        try:
            self.worker.shutdown()
        except Exception:
            pass
        self.worker = None
        self._worker_release_pending = False

    def _on_state(self, text):

        display_text = "در حال ترجمه"
        self.box.set_status(display_text)
        self.panel.set_state(display_text, "busy")

    def panel_resume(self):
        if not self._quitting:
            self.panel.resume()

            if self.panel.user_hidden:
                self.tray_notice.show_notice()

    def _on_result(self, img):
        if self._quitting:
            return
        self.panel.set_state("برنامه آماده استفاده است", "ok")
        if self.layer.active:
            self._pending = lambda: self.box.show_result(img)
        else:
            self.box.show_result(img)
        wx.CallAfter(self._release_worker_if_idle)

    def _on_error(self, message):
        if self._quitting:
            return
        self.panel.set_state("خطا — جزئیات: debug.log", "err", 6000)
        if self.layer.active:
            self._pending = lambda: self.box.show_error(message)
        else:
            self.box.show_error(message)
        wx.CallAfter(self._release_worker_if_idle)


    def _sync_startup(self):
        try:
            if self.cfg["run_on_startup"]:
                set_run_on_startup(True)          
            elif startup_exists():
                set_run_on_startup(False)         
        except Exception:
            pass

    def toggle_startup(self):
        new = not self.cfg["run_on_startup"]
        ok = set_run_on_startup(new)
        if ok:
            self.cfg.set("run_on_startup", new)
            self.panel.set_state("اجرا با ویندوز: %s" % ("روشن" if new else "خاموش"), "ok", 3000)
        else:
            self.panel.set_state("تغییر «اجرا با ویندوز» انجام نشد", "err", 5000)

    def change_capture_monitor(self, delta):
        monitors = list_monitor_rects()
        self._monitor_rects_cache = monitors
        try:
            current = int(self.cfg["capture_monitor"] or 0)
        except Exception:
            current = 0

        count = max(1, len(monitors))
        new_value = (current + int(delta)) % (count + 1)
        self.cfg.set("capture_monitor", new_value)
        self.panel.refresh()
        self.panel.set_state("منبع تصویر: %s" % self.panel._monitor_label(), "ok", 2400)

    def toggle_performance_mode(self):
        enabled = not bool(self.cfg["performance_mode"])
        self.cfg.set("performance_mode", enabled)
        try:
            self._poll.Stop()
            self._poll.Start(65 if enabled else 25)
        except Exception:
            pass
        if enabled:

            if self.worker is not None:
                if getattr(self.worker, "_busy", False):
                    self._worker_release_pending = True
                else:
                    self._release_worker_if_idle()
        elif self.worker is None:

            self._ensure_worker()
        self.panel.refresh()
        if self.worker is not None and getattr(self.worker, "_busy", False):
            self.panel.set_state("در حال ترجمه", "busy")
        else:
            self.panel.set_state("حالت کم‌مصرف %s شد" % ("روشن" if enabled else "خاموش"), "ok", 2600)

    def choose_save_dir(self):
        cur = self.cfg["save_dir"]
        try:
            os.makedirs(cur, exist_ok=True)
        except Exception:
            pass
        dlg = wx.DirDialog(None, "پوشه‌ی ذخیره‌ی عکس‌ها را انتخاب کنید", defaultPath=cur,
                           style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        try:
            if dlg.ShowModal() == wx.ID_OK and dlg.GetPath():
                self.cfg.set("save_dir", dlg.GetPath())
                self.panel.set_state("مسیر ذخیره عوض شد", "ok", 3000)
        finally:
            dlg.Destroy()

    def open_save_dir(self):
        try:
            d = self.cfg["save_dir"]
            os.makedirs(d, exist_ok=True)
            os.startfile(d)
        except Exception:
            pass


    def set_hotkey(self, key, combo):
        mods, vk = parse_hotkey(combo)
        if vk is None:
            self.panel.set_state("این کلید پشتیبانی نمی‌شود", "err", 4000)
            return False
        hid = ID_SNIP if key == "snip_hotkey" else ID_CLOSE
        try:
            self.UnregisterHotKey(hid)
        except Exception:
            pass
        self.RegisterHotKey(hid, mods, vk)        
        self.cfg.set(key, combo)
        if key == "snip_hotkey":
            self._combo_snip = (mods, vk)
        else:
            self._combo_close = (mods, vk)
        self._hold_after_change()
        self.tray.update_tip()
        self.panel.refresh()
        self.panel.set_state("کلید جدید: %s" % combo.upper(), "ok", 3500)
        return True

    def _hold_after_change(self):

        self._prev["snip"] = self._prev["close"] = True
        self._armed = False
        self._last_key = time.time()

    _MOD_VKS = frozenset((0x10, 0x11, 0x12, 0x5B, 0x5C, 0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5))

    @classmethod
    def _down_vks(cls):
        out = set()
        for vk in range(8, 255):
            if vk not in cls._MOD_VKS and (user32.GetAsyncKeyState(vk) & 0x8000):
                out.add(vk)
        return out

    @staticmethod
    def _held_mods():
        parts = []
        for vks, name in (((0x11, 0xA2, 0xA3), "ctrl"), ((0x12, 0xA4, 0xA5), "alt"),
                          ((0x10, 0xA0, 0xA1), "shift"), ((0x5B, 0x5C), "win")):
            if any(user32.GetAsyncKeyState(v) & 0x8000 for v in vks):
                parts.append(name)
        return parts

    def capture_hotkey(self, key):
        if self._quitting:
            return
        if self._cap is not None:                 
            same = self._cap["key"] == key
            self._cap_end("لغو شد", "ok")
            if same:
                return
        self._cap = {"key": key, "t0": time.time(), "ignore": self._down_vks()}
        msg = "کلید جدید را بزنید  (Esc = لغو)"
        self.panel.set_state(msg, "busy")
        if self.panel.user_hidden:
            try:
                wx.adv.NotificationMessage("Translator", msg).Show(3)
            except Exception:
                pass
        wx.CallLater(40, self._cap_tick)

    def _cap_end(self, msg, kind):
        self._cap = None
        self._hold_after_change()
        self.panel.set_state(msg, kind, 3500)

    def _cap_tick(self):
        cap = self._cap
        if cap is None or self._quitting:
            return
        if time.time() - cap["t0"] > 20:
            self._cap_end("زمان انتخاب کلید تمام شد", "err")
            return
        down = self._down_vks()
        cap["ignore"] &= down                    
        fresh = down - cap["ignore"]
        if 0x1B in fresh:
            if cap["key"] == "close_hotkey":
                self._cap = None
                self.set_hotkey("close_hotkey", "esc")
            else:
                self._cap_end("لغو شد", "ok")
            return
        for vk in sorted(fresh):
            tok = vk_token(vk)
            mods = self._held_mods()
            key = cap["key"]
            self._cap = None
            if not self.set_hotkey(key, "+".join(mods + [tok])):
                self._hold_after_change()
            return
        wx.CallLater(40, self._cap_tick)


    def _remove_photo_storage(self):
        """Silently remove the configured photo folder and all its contents on Exit.

        Guard against deleting filesystem roots, Windows/application data trees,
        or the app's configuration directory if a bad path was set. The configured
        photo folder itself and all its contents are removed without a confirmation.
        """
        try:
            raw = os.path.expandvars(os.path.expanduser(str(self.cfg["save_dir"] or ""))).strip()
            if not raw:
                return
            target = os.path.normcase(os.path.realpath(os.path.abspath(raw)))
            if not os.path.isdir(target):
                return

            drive, tail = os.path.splitdrive(target)
            drive_root = os.path.normcase(os.path.realpath(drive + os.sep)) if drive else ""
            home = os.path.normcase(os.path.realpath(os.path.expanduser("~")))
            appdata = os.path.normcase(os.path.realpath(os.environ.get("APPDATA") or home))
            windir = os.path.normcase(os.path.realpath(os.environ.get("WINDIR") or r"C:\Windows"))
            protected_exact = {p for p in (drive_root, home) if p}
            protected_roots = {p for p in (appdata, windir) if p}
            for env_name in ("PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMDATA"):
                value = os.environ.get(env_name)
                if value:
                    protected_roots.add(os.path.normcase(os.path.realpath(value)))




            config_dir = os.path.normcase(os.path.realpath(getattr(self.cfg, "dir", "")))
            if target in protected_exact:
                dbg("photo folder cleanup skipped (filesystem/user root): " + target)
                return
            unsafe_roots = set(protected_roots)
            if config_dir:
                unsafe_roots.add(config_dir)
            strict_roots = {
                os.path.normcase(os.path.realpath(windir)),
            }
            for env_name in ("PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMDATA"):
                value = os.environ.get(env_name)
                if value:
                    strict_roots.add(os.path.normcase(os.path.realpath(value)))
            for root in unsafe_roots:
                try:
                    common = os.path.commonpath([target, root])



                    if common == target or (root in strict_roots and common == root):
                        dbg("photo folder cleanup skipped (would remove protected path): " + target)
                        return
                except Exception:
                    continue

            def _remove_readonly(func, path, _exc_info):
                try:
                    os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
                    func(path)
                except Exception:
                    pass

            last_error = None
            for attempt in range(4):
                try:
                    shutil.rmtree(target, onerror=_remove_readonly)
                    last_error = None
                    break
                except FileNotFoundError:
                    last_error = None
                    break
                except Exception as exc:
                    last_error = exc
                    time.sleep(0.12 * (attempt + 1))
            if last_error is None and os.path.exists(target):
                last_error = OSError("folder still exists after cleanup attempts")
            if last_error is not None:
                dbg("photo folder cleanup failed: %s — %s" % (target, last_error))
            else:
                dbg("photo folder removed on Exit: " + target)
        except Exception as exc:
            dbg("photo folder cleanup error: %s" % exc)


    def quit(self):
        if self._quitting:
            return
        panel = getattr(self, "panel", None)
        if panel is not None and getattr(panel, "pinned", False):
            panel._show_pin_notice()
            return
        self._quitting = True
        self._cap = None
        self._pending = None
        try:
            if self.layer.active:
                self.layer.cancel()
        except Exception:
            pass
        try:
            user32.ClipCursor(None)
        except Exception:
            pass
        try:
            self.box.hide_box()
            self.box._delete_saved()
        except Exception:
            pass
        try:
            self._poll.Stop()
        except Exception:
            pass
        for hid in (ID_SNIP, ID_CLOSE, ID_ESC):
            try:
                self.UnregisterHotKey(hid)
            except Exception:
                pass
        try:
            self.tray.RemoveIcon()
            self.tray.Destroy()
        except Exception:
            pass
        if self.worker is not None:
            try:
                self.worker.shutdown()
            except Exception:
                pass
            self.worker = None
        try:
            self.panel.shutdown()
        except Exception:
            pass
        try:
            self.tray_notice.shutdown()
        except Exception:
            pass
        for w in (self.layer, self.box, self.panel, self.tray_notice):
            try:
                w.Destroy()
            except Exception:
                pass
        for other in list(wx.GetTopLevelWindows()):
            try:
                if other is not self:
                    other.Destroy()
            except Exception:
                pass


        self._remove_photo_storage()
        try:
            self.Destroy()
            app = wx.GetApp()
            if app is not None:
                app.ExitMainLoop()
        except Exception:
            pass


        _hard_exit(0)


_mutex = None


def single_instance():
    global _mutex
    try:
        k = ctypes.windll.kernel32
        k.CreateMutexW.restype = ctypes.c_void_p
        _mutex = k.CreateMutexW(None, False, "Local\\42OCR_SnipTranslate")
        return k.GetLastError() != 183
    except Exception:
        return True


if __name__ == "__main__":

    if not is_admin() and "--noelev" not in sys.argv:
        if relaunch_as_admin():
            _hard_exit(0)
    if not single_instance():
        _msg("برنامه از قبل در حال اجراست (آیکون کنار ساعت ویندوز).")
        _hard_exit(0)
    app = wx.App(False)
    SnipApp(background="--bg" in sys.argv)
    app.MainLoop()
    _hard_exit(0)