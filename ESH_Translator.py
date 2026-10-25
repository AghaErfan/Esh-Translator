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
import math
import time

APP_DIR_NAME = "eshOcr"          # پوشه‌ی داده‌ی برنامه در %APPDATA%
_LEGACY_DIR_NAME = "42OCR"       # نام قدیمی (فقط برای انتقال خودکار داده‌های نسخه‌های قبلی)


def _migrate_legacy_appdata():
    """پوشه‌ی قدیمی %APPDATA%\\42OCR (تنظیمات، مدل‌ها، کتابخانه‌ها) را به %APPDATA%\\eshOcr منتقل می‌کند.
    اول جابه‌جایی آنی (rename)؛ اگر قفل بود، کپی کامل و فقط بعد از کپیِ موفق، پوشه‌ی قدیمی پاک می‌شود."""
    try:
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        old = os.path.join(base, _LEGACY_DIR_NAME)
        new = os.path.join(base, APP_DIR_NAME)
        if not os.path.isdir(old):
            return
        if os.path.exists(new):
            # پوشه‌ی جدید هست ولی تنظیمات ندارد (مثلاً فقط لاگ ساخته شده) و قدیمی تنظیمات دارد → ادغام
            if os.path.isfile(os.path.join(new, "config.json")) or not os.path.isfile(os.path.join(old, "config.json")):
                return
            try:
                shutil.copytree(old, new, dirs_exist_ok=True)
                shutil.rmtree(old, ignore_errors=True)
            except Exception:
                pass
            return
        try:
            os.rename(old, new)
            return
        except OSError:
            pass
        try:
            shutil.copytree(old, new)
        except Exception:
            shutil.rmtree(new, ignore_errors=True)       # کپی ناقص نماند؛ اجرای بعدی دوباره تلاش می‌کند
            return
        shutil.rmtree(old, ignore_errors=True)
    except Exception:
        pass


_migrate_legacy_appdata()

if os.environ.get("_42OCR_NEVER") == "1":      
    import zipfile, platform, subprocess, ssl, winreg, unittest, pickle, sqlite3, csv, decimal, fractions, uuid
    import logging.handlers, logging.config, multiprocessing, concurrent.futures, asyncio, queue, secrets, hmac
    import xml.etree.ElementTree, xml.dom.minidom, xml.sax, http.server, http.cookies, http.cookiejar
    import html.parser, email.parser, email.message, email.mime.text, tarfile, gzip, bz2, lzma, glob, fnmatch
    import getpass, difflib, textwrap, pprint, inspect, dis, ast, tokenize, statistics, random, numbers, bisect
    import heapq, array, sysconfig, ctypes.util, importlib.metadata, importlib.resources, pkgutil, zipimport
    import runpy, code, argparse, optparse, configparser, shlex, cmd, pdb, signal, selectors, socketserver
    import urllib.request, urllib.error, urllib.parse, ftplib, imaplib, smtplib, mimetypes, locale, gettext
    import dataclasses, enum, typing, weakref, copy, copyreg, struct, operator, itertools, functools, contextlib
    import calendar, datetime, zoneinfo, cProfile, profile, timeit, trace, tempfile, webbrowser, wave, colorsys
    import ctranslate2, sentencepiece, numpy, dxcam, comtypes, wx.html2, wx.adv, tkinter




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


def _unhook_all():
    try:
        app = wx.GetApp()
        top = getattr(app, "_snip_app", None)
        if top is not None:
            top.layer.grab.stop()
            w = getattr(top, "_fg_watch", None)
            if w is not None:
                w.stop()
    except Exception:
        pass


def _hard_exit(code=0):
    try:
        if code == 0:
            safe_mode_clean_exit()
    except Exception:
        pass
    _unhook_all()
    for _c in list(globals().get("_CFG_LIVE", ())):          # ذخیره‌های در صفِ تنظیمات قبل از خروج
        try:
            _c.flush()
        except Exception:
            pass
    try:
        sys.stdout.flush()
        sys.stderr.flush()
    except Exception:
        pass
    os._exit(code)


def dbg(msg):
    """لاگ عیب‌یابی: %APPDATA%\\eshOcr\\debug.log (اگر بزرگ شد پاک می‌شود)."""
    try:
        d = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), APP_DIR_NAME)
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
        safe_mode_clean_exit()
    except Exception:
        pass
    if getattr(sys, "frozen", False) or ("__compiled__" in globals()):       # exe: پروسه‌ی تازه، نه os.execv
        import subprocess
        env = dict(os.environ)
        env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"                            # onefile: پوشه‌ی موقتِ قبلی دوباره استفاده نشود
        env.pop("_MEIPASS2", None)
        try:
            subprocess.Popen([sys.executable] + list(sys.argv[1:]), env=env, close_fds=True)
            os._exit(0)
        except Exception:
            pass
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


def _ensure_webview2_runtime_now():
    if _webview2_installed():
        return True
    import subprocess
    path = os.path.join(tempfile.gettempdir(), "MicrosoftEdgeWebview2Setup.exe")
    _fetch(WEBVIEW2_URL, path, timeout=120)
    subprocess.call([path, "/silent", "/install"], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), timeout=600,
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return _webview2_installed()


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
    d = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), APP_DIR_NAME)
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


# ════════════════════════════════════════════════════════════════════
#  خودترمیمی: کتابخانه‌ی Argos (حتی داخل exe) + Edge WebView2 + WebView2Loader.dll
# ════════════════════════════════════════════════════════════════════
def _is_frozen():
    return bool(getattr(sys, "frozen", False)) or ("__compiled__" in globals())


_APPDATA42 = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), APP_DIR_NAME)
PYLIBS_DIR = os.path.join(_APPDATA42, "pylibs")          # کتابخانه‌های پایتونیِ نصب‌شده توسط خود برنامه
EMBED_DIR = os.path.join(_APPDATA42, "pyembed")          # پایتون همراه (فقط اگر پایتون سازگار روی سیستم نبود)
WV2_DIR = os.path.join(_APPDATA42, "wv2")                # WebView2Loader.dll دانلودشده
WV2_DATA_DIR = os.path.join(_APPDATA42, "webview2_data") # پوشه‌ی داده‌ی Edge (همیشه قابل‌نوشتن)
_DLL_HANDLES = []
_PYLIBS_STATE = {"dirs": set()}


class SetupError(Exception):
    pass


def _add_dll_dir(path):
    try:
        if path and os.path.isdir(path) and path not in _PYLIBS_STATE["dirs"]:
            _PYLIBS_STATE["dirs"].add(path)
            if hasattr(os, "add_dll_directory"):
                _DLL_HANDLES.append(os.add_dll_directory(path))
            os.environ["PATH"] = path + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass


def _activate_pylibs():
    """پوشه‌ی pylibs را به sys.path و مسیر DLLها اضافه می‌کند (بی‌خطر و چندباره‌قابل‌صدا)."""
    try:
        if not os.path.isdir(PYLIBS_DIR):
            return
        if PYLIBS_DIR not in sys.path:
            sys.path.append(PYLIBS_DIR)
        _add_dll_dir(PYLIBS_DIR)
        for name in os.listdir(PYLIBS_DIR):
            full = os.path.join(PYLIBS_DIR, name)
            if os.path.isdir(full) and (name.endswith(".libs") or name in ("ctranslate2", "torch", "numpy", "scipy")):
                _add_dll_dir(full)
                _add_dll_dir(os.path.join(full, "lib"))
                _add_dll_dir(os.path.join(full, ".libs"))
        import importlib
        importlib.invalidate_caches()
    except Exception as exc:
        dbg("activate_pylibs: %r" % (exc,))


def _fetch(url, dest, prog=None, timeout=60, big=False):
    import urllib.request
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    if big and "net_open" in globals():                 # فایل بزرگ (نصب‌کننده): چند اتصال همزمان
        try:
            _download_file(url, dest, prog, None, expect=_DL_MIN_SPLIT)
            return
        except Exception as exc:
            dbg("fast fetch failed, plain fetch: %r" % (exc,))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 42OCR"})
    tmp = dest + ".part"
    with urllib.request.urlopen(req, timeout=timeout) as r, open(tmp, "wb", buffering=1 << 20) as f:
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if prog:
                try:
                    prog(done, total)
                except Exception:
                    pass
    os.replace(tmp, dest)


def _sub_env():
    env = dict(os.environ)
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    return env


def _nowin():
    import subprocess
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _run_cmd(cmd, on_line=None, timeout=3600):
    """اجرای یک دستور بدون پنجره؛ خروجی خط‌به‌خط به on_line می‌رسد. (کد برگشت، آخرین خطوط)"""
    import subprocess
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=_sub_env(),
                         creationflags=_nowin(), stdin=subprocess.DEVNULL)
    tail = []
    t0 = time.time()
    for raw in p.stdout:
        line = raw.decode("utf-8", "replace").strip()
        if not line:
            continue
        tail.append(line)
        tail = tail[-30:]
        if on_line:
            try:
                on_line(line)
            except Exception:
                pass
        if time.time() - t0 > timeout:
            p.kill()
            break
    p.wait()
    return p.returncode, tail


def _probe_python(cmd):
    """(major, minor, bits) اگر این پایتون pip دارد و قابل‌اجراست؛ وگرنه None."""
    import subprocess
    try:
        out = subprocess.run(cmd + ["-c", "import sys,struct;print(sys.version_info[0],sys.version_info[1],"
                                          "struct.calcsize('P')*8);import pip"],
                             capture_output=True, text=True, timeout=40, env=_sub_env(),
                             creationflags=_nowin(), stdin=subprocess.DEVNULL)
        if out.returncode == 0:
            a = out.stdout.split()
            return int(a[0]), int(a[1]), int(a[2])
    except Exception:
        pass
    return None


def _runner_python():
    """پایتونی که pip دارد و با خود برنامه هم‌نسخه است (برای exe: پایتون نصب‌شده روی سیستم)."""
    want = (sys.version_info[0], sys.version_info[1], ctypes.sizeof(ctypes.c_void_p) * 8)
    if not _is_frozen():
        return [sys.executable]
    cands = []
    if shutil.which("py"):
        cands.append(["py", "-%d.%d%s" % (want[0], want[1], "-32" if want[2] == 32 else "")])
    for nm in ("python", "python3"):
        w = shutil.which(nm)
        if w:
            cands.append([w])
    for c in cands:
        if _probe_python(c) == want:
            return c
    return None


def _ensure_embed_python(cb):
    """پایتونِ همراه (embeddable) هم‌نسخه با exe را دانلود و pip را رویش نصب می‌کند."""
    import platform
    import zipfile
    exe = os.path.join(EMBED_DIR, "python.exe")
    want = (sys.version_info[0], sys.version_info[1], ctypes.sizeof(ctypes.c_void_p) * 8)
    if os.path.isfile(exe) and _probe_python([exe]) == want:
        return [exe]
    M, m, p = sys.version_info[:3]
    if ctypes.sizeof(ctypes.c_void_p) == 4:
        arch = "win32"
    else:
        arch = "arm64" if "ARM" in (platform.machine() or "").upper() else "amd64"
    last = {(3, 8): 10, (3, 9): 13, (3, 10): 11, (3, 11): 9, (3, 12): 10}
    micros = [p]
    if (M, m) in last and last[(M, m)] != p:
        micros.append(last[(M, m)])
    else:
        micros += list(range(p - 1, max(-1, p - 8), -1))
    zpath = os.path.join(tempfile.gettempdir(), "esh_pyembed.zip")
    got, last_exc = None, None
    for mic in micros:
        url = "https://www.python.org/ftp/python/%d.%d.%d/python-%d.%d.%d-embed-%s.zip" % (M, m, mic, M, m, mic, arch)
        try:
            cb(0.02, "دانلود پایتون همراه %d.%d.%d …" % (M, m, mic))
            _fetch(url, zpath, lambda d, t: cb(0.02 + 0.08 * (d / float(t) if t else 0), "دانلود پایتون همراه…"))
            got = mic
            break
        except Exception as exc:
            last_exc = exc
    if got is None:
        raise SetupError("دانلود پایتون همراه ناموفق بود (%s)" % (last_exc,))
    shutil.rmtree(EMBED_DIR, ignore_errors=True)
    os.makedirs(EMBED_DIR, exist_ok=True)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(EMBED_DIR)
    try:
        os.remove(zpath)
    except Exception:
        pass
    for fn in os.listdir(EMBED_DIR):
        if fn.lower().endswith("._pth"):
            fp = os.path.join(EMBED_DIR, fn)
            with open(fp, "r", encoding="utf-8") as f:
                txt = f.read()
            txt = txt.replace("#import site", "import site")
            if "import site" not in txt:
                txt += "\nimport site\n"
            with open(fp, "w", encoding="utf-8") as f:
                f.write(txt)
    cb(0.12, "نصب pip …")
    gp = os.path.join(tempfile.gettempdir(), "esh_get_pip.py")
    _fetch("https://bootstrap.pypa.io/get-pip.py", gp)
    rc, tail = _run_cmd([exe, gp, "--no-warn-script-location", "--disable-pip-version-check"], timeout=900)
    try:
        os.remove(gp)
    except Exception:
        pass
    if _probe_python([exe]) != want:
        raise SetupError("نصب pip روی پایتون همراه ناموفق بود: " + " | ".join(tail[-3:]))
    return [exe]


def _install_vc_redist(cb=None):
    """Microsoft Visual C++ Redistributable (برای ctranslate2 لازم است؛ روی ویندوز تازه‌نصب نیست)."""
    try:
        if cb:
            cb("نصب Microsoft Visual C++ Runtime …")
        arch = "x86" if ctypes.sizeof(ctypes.c_void_p) == 4 else "x64"
        dest = os.path.join(tempfile.gettempdir(), "vc_redist_%s.exe" % arch)
        _fetch("https://aka.ms/vs/17/release/vc_redist.%s.exe" % arch, dest, timeout=120)
        import subprocess
        subprocess.call([dest, "/install", "/quiet", "/norestart"], creationflags=_nowin(), timeout=900,
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as exc:
        dbg("vc_redist failed: %r" % (exc,))
        return False


def _try_import_argos():
    for k in [k for k in sys.modules if k.split(".")[0] in ("ctranslate2", "sentencepiece")]:
        sys.modules.pop(k, None)
    import importlib
    importlib.invalidate_caches()
    import ctranslate2  # noqa: F401
    import sentencepiece  # noqa: F401


def ensure_argos_lib(cb):
    """کتابخانه‌ی argostranslate را (حتی در نسخه‌ی exe) خودکار نصب می‌کند. cb(fraction, message)."""
    _activate_pylibs()
    try:
        _try_import_argos()
        return True
    except Exception:
        pass
    cb(0.01, "جستجوی پایتون برای نصب کتابخانه…")
    runner = _runner_python()
    if runner is None:
        runner = _ensure_embed_python(lambda f, m: cb(0.01 + 0.25 * f, m))
    os.makedirs(PYLIBS_DIR, exist_ok=True)
    state = {"n": 0}

    def on_line(line):
        if line.startswith(("Collecting", "Downloading", "Installing collected", "Successfully")):
            if line.startswith("Collecting"):
                state["n"] += 1
            cb(0.30 + 0.60 * min(1.0, state["n"] / 8.0), "نصب کتابخانه‌ی ترجمه: " + line[:70])

    cmd = runner + ["-m", "pip", "install", "--target", PYLIBS_DIR, "--upgrade", "--prefer-binary",
                    "--no-warn-script-location", "--disable-pip-version-check", "--progress-bar", "off",
                    "--retries", "5", "--timeout", "60", "ctranslate2", "sentencepiece", "numpy"]
    rc, tail = _run_cmd(cmd, on_line, timeout=3600)
    dbg("pip argostranslate rc=%s tail=%s" % (rc, tail[-4:]))
    if rc != 0:
        # یک بار دیگر (قطعی‌های لحظه‌ای شبکه)
        rc, tail = _run_cmd(cmd, on_line, timeout=3600)
        if rc != 0:
            raise SetupError("pip ناموفق بود: " + " | ".join(tail[-3:]))
    _activate_pylibs()
    cb(0.92, "بررسی کتابخانه…")
    try:
        _try_import_argos()
    except Exception as exc:
        msg = str(exc)
        if "DLL" in msg or "WinError 126" in msg or "WinError 193" in msg:
            _install_vc_redist(lambda m: cb(0.94, m))
            _activate_pylibs()
            try:
                _try_import_argos()
                return True
            except Exception as exc2:
                raise SetupError("کتابخانه نصب شد ولی بارگذاری نشد: %s" % exc2)
        raise SetupError("کتابخانه نصب شد ولی بارگذاری نشد: %s" % exc)
    return True


def _find_wv2_loader():
    cands = []
    try:
        import importlib.util
        spec = importlib.util.find_spec("wx")
        if spec and spec.submodule_search_locations:
            cands += list(spec.submodule_search_locations)
    except Exception:
        pass
    mei = getattr(sys, "_MEIPASS", "") or ""
    cands += [mei, os.path.join(mei, "wx") if mei else "", os.path.dirname(sys.executable),
              os.path.dirname(os.path.abspath(sys.argv[0] or ".")), WV2_DIR]
    for d in cands:
        if d:
            p = os.path.join(d, "WebView2Loader.dll")
            if os.path.isfile(p):
                return p
    return None


def _download_wv2_loader():
    import io as _io
    import platform
    import urllib.request
    import zipfile
    arch = "x64" if ctypes.sizeof(ctypes.c_void_p) == 8 else "x86"
    if arch == "x64" and "ARM" in (platform.machine() or "").upper():
        arch = "arm64"
    req = urllib.request.Request("https://www.nuget.org/api/v2/package/Microsoft.Web.WebView2",
                                 headers={"User-Agent": "Mozilla/5.0 42OCR"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    with zipfile.ZipFile(_io.BytesIO(data)) as z:
        want = None
        for n in z.namelist():
            ln = n.lower().replace("\\", "/")
            if ln.endswith("/webview2loader.dll") and ("/win-%s/" % arch in ln or "/%s/" % arch in ln):
                want = n
                break
        if not want:
            return None
        os.makedirs(WV2_DIR, exist_ok=True)
        dest = os.path.join(WV2_DIR, "WebView2Loader.dll")
        with open(dest, "wb") as f:
            f.write(z.read(want))
    return dest


def _ensure_wv2_loader(download=True):
    """WebView2Loader.dll را پیدا (یا دانلود) و از قبل بارگذاری می‌کند تا Edge-backend کار کند."""
    try:
        p = _find_wv2_loader()
        if not p and download:
            p = _download_wv2_loader()
        if p:
            _add_dll_dir(os.path.dirname(p))
            ctypes.WinDLL(p)
            return True
    except Exception as exc:
        dbg("wv2 loader: %r" % (exc,))
    return False


def _vcruntime_ok():
    """Visual C++ Runtime (لازم برای ctranslate2/torch/wx). روی ویندوز تازه‌نصب گاهی نیست."""
    try:
        names = ["vcruntime140.dll", "msvcp140.dll"]
        if ctypes.sizeof(ctypes.c_void_p) == 8:
            names.append("vcruntime140_1.dll")
        for dll in names:
            ctypes.WinDLL(dll)
        return True
    except OSError:
        return False


def _preflight_essentials():
    """هر بار شروع برنامه: پیش‌نیازهای ضروری را می‌سنجد و هرچه نبود خودش دانلود/نصب می‌کند."""
    try:
        if not _vcruntime_ok():
            marker = os.path.join(_APPDATA42, "vcredist_tried")
            if not os.path.exists(marker):                 # اگر نصبش ناموفق بود، هر بار مزاحم نشود
                try:
                    os.makedirs(_APPDATA42, exist_ok=True)
                    open(marker, "w").close()
                except Exception:
                    pass
                _install_vc_redist()
    except Exception as exc:
        dbg("preflight vc: %r" % (exc,))
    try:
        _ensure_wv2_loader(download=(_find_wv2_loader() is None))
    except Exception as exc:
        dbg("preflight loader: %r" % (exc,))


_activate_pylibs()
try:
    os.makedirs(WV2_DATA_DIR, exist_ok=True)
    os.environ.setdefault("WEBVIEW2_USER_DATA_FOLDER", WV2_DATA_DIR)
except Exception:
    pass




# ── شبکه / VPN / پروکسی ──
# system = پروکسی و تونل خودِ ویندوز؛ off = مستقیم؛ custom = آدرس دستی (http / socks5)
NET = {"mode": "system", "url": ""}


def _early_net_cfg():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    for name in ("config.json", "config.json.bak"):
        try:
            with open(os.path.join(base, APP_DIR_NAME, name), "r", encoding="utf-8") as f:
                j = json.load(f)
            if isinstance(j, dict):
                m = j.get("proxy_mode")
                NET["mode"] = m if m in ("system", "off", "custom") else "system"
                NET["url"] = str(j.get("proxy_url") or "").strip()
                return
        except Exception:
            continue


def _webview_args():
    """آرگومان‌های Edge WebView2: QUIC/UDP خاموش (بیشتر تونل‌ها UDP را رد نمی‌کنند) و پروکسی طبق تنظیم کاربر."""
    args = ["--disable-quic"]
    if NET["mode"] == "off":
        args.append("--no-proxy-server")
    elif NET["mode"] == "custom" and NET["url"]:
        args.append("--proxy-server=" + NET["url"])
    return " ".join(args)


def _apply_net_env():
    """پروکسی دستی را برای کتابخانه‌ها و پروسه‌های فرزند (pip/winget/requests) هم تنظیم می‌کند."""
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
        if NET["mode"] == "custom" and NET["url"]:
            os.environ[k] = NET["url"].replace("socks5://", "socks5h://", 1) if k.lower() == "all_proxy" else NET["url"]
        elif NET["mode"] == "off":
            os.environ.pop(k, None)


_early_net_cfg()
_apply_net_env()

# ════════════════════════════════════════════════════════════════════
#  بررسی پیش‌نیازها قبل از اجرا: هرچه نبود خودش نصب می‌کند یا به کاربر دقیق گزارش می‌دهد
# ════════════════════════════════════════════════════════════════════
def _pf_win_info():
    """(major, build, نام قابل‌نمایش) — ویندوز ۱۱ همان ۱۰.۰ با build ≥ ۲۲۰۰۰ است."""
    try:
        v = sys.getwindowsversion()
        name = "Windows 11" if v.build >= 22000 else ("Windows %d" % v.major)
        return v.major, v.build, "%s (build %d)" % (name, v.build)
    except Exception:
        return 0, 0, "ویندوز نامشخص"


def _pf_os_64bit():
    import platform
    m = (os.environ.get("PROCESSOR_ARCHITEW6432") or os.environ.get("PROCESSOR_ARCHITECTURE")
         or platform.machine() or "").upper()
    return m in ("AMD64", "ARM64", "IA64", "X86_64")


def _pf_has_module(mod):
    import importlib
    import importlib.util
    importlib.invalidate_caches()
    try:
        return importlib.util.find_spec(mod) is not None
    except Exception:
        return False


def _pf_pip(pkgs):
    """نصب با pip؛ (موفق؟، آخرین خطوط خروجی)."""
    tail = []
    for extra in (["--user"], []):
        try:
            rc, tail = _run_cmd([sys.executable, "-m", "pip", "install", "--disable-pip-version-check"] + extra + list(pkgs),
                                timeout=1800)
        except Exception as exc:
            rc, tail = -1, [str(exc)]
        if rc == 0:
            return True, tail
    return False, tail


def _pf_vc_system_ok():
    """DLLهای Visual C++ در پوشه‌ی سیستم ویندوز هست؟ (کپیِ داخلِ exe حساب نمی‌شود؛ ctranslate2 و ... به نسخه‌ی سیستم نیاز دارند)"""
    try:
        buf = ctypes.create_unicode_buffer(520)
        ctypes.windll.kernel32.GetSystemDirectoryW(buf, 520)
        names = ["vcruntime140.dll", "msvcp140.dll"]
        if ctypes.sizeof(ctypes.c_void_p) == 8:
            names.append("vcruntime140_1.dll")
        return all(os.path.isfile(os.path.join(buf.value, n)) for n in names)
    except Exception:
        return _vcruntime_ok()


def _pf_free_gb():
    try:
        return shutil.disk_usage(_APPDATA42 if os.path.isdir(_APPDATA42) else os.path.dirname(_APPDATA42)).free / 1e9
    except Exception:
        return None


def _pf_appdata_writable():
    try:
        os.makedirs(_APPDATA42, exist_ok=True)
        p = os.path.join(_APPDATA42, ".write_test")
        with open(p, "w") as f:
            f.write("1")
        os.remove(p)
        return True
    except Exception:
        return False


def _pf_internet():
    import urllib.request
    for url in ("http://www.msftconnecttest.com/connecttest.txt", "https://www.microsoft.com/"):
        try:
            urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ESHTranslator/1.0"}), timeout=8).close()
            return True
        except Exception:
            continue
    return False


def _pf_items():
    """فهرست بررسی‌ها. هر مورد: key, title, check()->(ok, detail), fix(cb)->(ok, detail) یا None،
    level: fatal (برنامه بدونش اجرا نمی‌شود) | warn (فقط بخشی از امکانات کار نمی‌کند)، restart: بعد از نصب باید دوباره اجرا شود."""
    frozen = _is_frozen()
    major, build, wname = _pf_win_info()
    py64 = ctypes.sizeof(ctypes.c_void_p) == 8
    items = []

    def add(key, title, check, fix=None, level="warn", restart=False, once=False):
        items.append({"key": key, "title": title, "check": check, "fix": fix, "level": level,
                      "restart": restart, "once": once, "state": "wait", "detail": ""})

    add("win", "نسخه‌ی ویندوز",
        lambda: (major >= 10, wname if major >= 10 else
                 "%s — این برنامه فقط روی ویندوز ۱۰ و ۱۱ اجرا می‌شود" % wname), level="fatal")
    add("arch", "ویندوز ۶۴ بیتی",
        lambda: (_pf_os_64bit(), "۶۴ بیتی" if _pf_os_64bit() else
                 "ویندوز شما ۳۲ بیتی است؛ ترجمه‌ی آفلاین روی آن کار نمی‌کند (Google و هوش مصنوعی کار می‌کنند)"),
        once=True)
    add("appdata", "پوشه‌ی تنظیمات (AppData)",
        lambda: (_pf_appdata_writable(), "قابل نوشتن" if _pf_appdata_writable() else
                 "نمی‌توان در %s نوشت؛ دسترسی پوشه یا آنتی‌ویروس را بررسی کنید" % _APPDATA42), level="fatal")

    def _disk():
        g = _pf_free_gb()
        if g is None:
            return True, ""
        return g >= 1.5, ("%.1f گیگابایت فضای خالی" % g) if g >= 1.5 else \
            "فقط %.1f گیگابایت فضای خالی دارید؛ مدل‌های آفلاین حدود ۱ گیگابایت جا می‌خواهند" % g
    add("disk", "فضای خالی دیسک", _disk, once=True)

    if not frozen:
        add("python", "نسخه‌ی پایتون",
            lambda: (sys.version_info >= (3, 8), "Python %d.%d.%d" % sys.version_info[:3] if sys.version_info >= (3, 8)
                     else "پایتون %d.%d قدیمی است؛ نسخه‌ی ۳٫۸ یا بالاتر لازم است" % sys.version_info[:2]), level="fatal")
        if _pf_os_64bit():
            add("py64", "پایتون ۶۴ بیتی",
                lambda: (py64, "۶۴ بیتی" if py64 else
                         "پایتون ۳۲ بیتی است؛ کتابخانه‌ی ترجمه‌ی آفلاین نصب نمی‌شود — پایتون ۶۴ بیتی نصب کنید"), once=True)

    _vc_ok = _pf_vc_system_ok if frozen else _vcruntime_ok
    add("vcrt", "Visual C++ Runtime", lambda: (_vc_ok(), "نصب است" if _vc_ok() else "نصب نیست"),
        fix=lambda cb: (bool(_install_vc_redist(cb)) and _vc_ok(), "نصب شد"), restart=True)

    if frozen:                                             # نسخه‌ی exe: همه‌ی کتابخانه‌ها باید داخل خود برنامه باشند
        for _mod, _title, _why in (
                ("ctranslate2", "موتور ترجمه‌ی آفلاین (داخل برنامه)", "ترجمه‌ی آفلاین"),
                ("sentencepiece", "توکنایزر ترجمه‌ی آفلاین (داخل برنامه)", "ترجمه‌ی آفلاین"),
                ("dxcam", "عکس‌گرفتن از بازی تمام‌صفحه (داخل برنامه)", "عکس از بازی تمام‌صفحه")):
            add("pkg_" + _mod, _title,
                lambda m=_mod, w=_why: (_pf_has_module(m), "هست" if _pf_has_module(m) else
                                        "در این نسخه‌ی exe گنجانده نشده؛ %s کار نمی‌کند (exe را دوباره دانلود کنید)" % w),
                once=True)

    if not frozen:
        def fix_pip(pkg, mod):
            def _f(cb):
                cb("دانلود و نصب %s …" % pkg)
                ok, tail = _pf_pip([pkg])
                ok = ok and _pf_has_module(mod)
                return ok, ("نصب شد" if ok else "نصب خودکار نشد: " + " | ".join(tail[-2:])[:160])
            return _f
        add("wx", "کتابخانه‌ی wxPython (رابط برنامه)", lambda: (_pf_has_module("wx"), "نصب است" if _pf_has_module("wx") else "نصب نیست"),
            fix=fix_pip("wxPython", "wx"), level="fatal", restart=True)
        add("pil", "کتابخانه‌ی Pillow (عکس)", lambda: (_pf_has_module("PIL"), "نصب است" if _pf_has_module("PIL") else "نصب نیست"),
            fix=fix_pip("pillow", "PIL"), level="fatal", restart=True)

        def _dx_fix(cb):
            marker = os.path.join(_APPDATA42, "dxcam_tried")
            if os.path.exists(marker):
                return False, "قبلاً نصبش ناموفق بود؛ گرفتن عکس از بازی تمام‌صفحه ممکن است سیاه شود"
            try:
                os.makedirs(_APPDATA42, exist_ok=True)
                open(marker, "w").close()
            except Exception:
                pass
            return fix_pip("dxcam", "dxcam")(cb)
        add("dxcam", "کتابخانه‌ی dxcam (عکس از بازی تمام‌صفحه)",
            lambda: (_pf_has_module("dxcam"), "نصب است" if _pf_has_module("dxcam") else "نصب نیست"),
            fix=_dx_fix, restart=True)

    add("wv2", "Microsoft Edge WebView2 (Google Translate)",
        lambda: (_webview2_installed(), "نصب است" if _webview2_installed() else "نصب نیست"),
        fix=lambda cb: (bool(cb("دانلود و نصب WebView2 …") or _ensure_webview2_runtime_now()), "نصب شد"), restart=True)
    add("wv2loader", "فایل WebView2Loader.dll",
        lambda: (_find_wv2_loader() is not None, "پیدا شد" if _find_wv2_loader() else "پیدا نشد"),
        fix=lambda cb: (bool(cb("دانلود WebView2Loader …") or _ensure_wv2_loader(download=True)), "نصب شد"))
    return items


def _pf_run(items, post):
    """بررسی و رفع. post(index, state, detail) پیشرفت را به رابط می‌دهد. خروجی: (fatal، restart)"""
    need_fix = []
    for i, it in enumerate(items):
        post(i, "check", "")
        try:
            ok, detail = it["check"]()
        except Exception as exc:
            ok, detail = False, "بررسی ممکن نشد: %s" % exc
        it["state"], it["detail"] = ("ok" if ok else "bad"), detail
        post(i, it["state"], detail)
        if not ok and it["fix"] is not None:
            need_fix.append(i)
    restart = False
    if need_fix:
        online = _pf_internet()
        for i in need_fix:
            it = items[i]
            if not online:
                it["state"], it["detail"] = "bad", "اینترنت وصل نیست؛ بعد از وصل شدن اینترنت دوباره برنامه را اجرا کنید"
                post(i, "bad", it["detail"])
                continue
            post(i, "fix", "در حال نصب…")
            try:
                ok, detail = it["fix"](lambda m, _i=i: post(_i, "fix", m))
                if ok and not it["check"]()[0]:
                    ok, detail = False, "نصب انجام شد ولی هنوز شناسایی نشد؛ برنامه را یک بار دیگر اجرا کنید"
                elif not ok and not detail:
                    detail = "نصب خودکار انجام نشد"
                ok = bool(ok)
            except Exception as exc:
                dbg("preflight fix %s: %r" % (it["key"], exc))
                ok, detail = False, "نصب خودکار انجام نشد: %s" % str(exc)[:120]
            it["state"], it["detail"] = ("fixed" if ok else "bad"), (("نصب شد ✓" if ok else detail))
            if ok and it["restart"]:
                restart = True
            post(i, it["state"], it["detail"])
    fatal = any(it["state"] == "bad" and it["level"] == "fatal" for it in items)
    return fatal, restart


def _pf_report(items):
    mark = {"ok": "✓", "fixed": "✓", "bad": "✕", "wait": "…", "check": "…", "fix": "…"}
    lines = []
    for it in items:
        sev = "✕" if it["level"] == "fatal" else "!"
        lines.append("%s  %s%s" % (mark.get(it["state"], "…") if it["state"] != "bad" else sev, it["title"],
                                   (" — " + it["detail"]) if it["detail"] else ""))
    return "\n".join(lines)


def _pf_relaunch_admin():
    """نصب WebView2/VC++ به ادمین نیاز دارد؛ قبل از نصب با دسترسی ادمین دوباره اجرا می‌شود."""
    try:
        if ctypes.windll.shell32.IsUserAnAdmin() or "--noelev" in sys.argv or os.environ.get("_42OCR_PF_ELEV") == "1":
            return False
        os.environ["_42OCR_PF_ELEV"] = "1"
        os.environ["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
        exe = sys.executable
        args = " ".join('"%s"' % a for a in sys.argv[1:])
        if _is_frozen():
            params = args
        else:
            alt = os.path.join(os.path.dirname(exe), "pythonw.exe")
            exe = alt if os.path.isfile(alt) else exe
            params = ('"%s" %s' % (os.path.abspath(__file__), args)).strip()
        return ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1) > 32
    except Exception:
        return False


def _pf_window(items):
    """پنجره‌ی چک‌لیست (tkinter). اگر tkinter نبود None برمی‌گرداند."""
    try:
        import queue
        import tkinter as tk
    except Exception:
        return None
    try:
        root = tk.Tk()
    except Exception:
        return None
    try:
        dpi = ctypes.windll.user32.GetDpiForSystem()
    except Exception:
        dpi = 96
    k = max(1.0, dpi / 96.0)
    try:
        root.tk.call("tk", "scaling", dpi / 72.0)
    except Exception:
        pass
    BG, PANEL, FG, MUT = "#14161c", "#1b1e26", "#e8eaf0", "#8b92a5"
    COL = {"ok": "#34c98e", "fixed": "#34c98e", "bad": "#ff6b6b", "warn": "#ffbe3c", "fix": "#ffbe3c",
           "check": MUT, "wait": MUT}
    ICON = {"ok": "✓", "fixed": "✓", "bad": "✕", "fix": "⟳", "check": "…", "wait": "·"}
    root.title("Translator — بررسی پیش‌نیازها")
    root.configure(bg=BG)
    root.resizable(False, False)
    W, H = int(520 * k), int((130 + 44 * len(items)) * k)
    root.geometry("%dx%d+%d+%d" % (W, H, (root.winfo_screenwidth() - W) // 2, max(20, (root.winfo_screenheight() - H) // 2)))
    root.attributes("-topmost", True)
    head = tk.Label(root, text="در حال بررسی سیستم شما…", bg=BG, fg=FG, font=("Segoe UI", 12, "bold"), anchor="e")
    head.pack(fill="x", padx=16, pady=(14, 8))
    box = tk.Frame(root, bg=PANEL)
    box.pack(fill="both", expand=True, padx=14)
    rows = []
    for it in items:
        row = tk.Frame(box, bg=PANEL)
        row.pack(fill="x", padx=8, pady=3)
        ic = tk.Label(row, text="·", bg=PANEL, fg=MUT, font=("Segoe UI", 13, "bold"), width=2)
        ic.pack(side="right")
        txt = tk.Frame(row, bg=PANEL)
        txt.pack(side="right", fill="x", expand=True)
        t1 = tk.Label(txt, text=it["title"], bg=PANEL, fg=FG, font=("Segoe UI", 10, "bold"), anchor="e")
        t1.pack(fill="x")
        t2 = tk.Label(txt, text="", bg=PANEL, fg=MUT, font=("Segoe UI", 8), anchor="e", wraplength=int(430 * k), justify="right")
        t2.pack(fill="x")
        rows.append((ic, t2))
    btn = tk.Button(root, text="…", state="disabled", bg="#2a2f3b", fg=FG, relief="flat", font=("Segoe UI", 10, "bold"),
                    activebackground="#3a4050", activeforeground=FG, padx=16, pady=4)
    btn.pack(pady=10)
    q = queue.Queue()
    st = {"done": None}

    def post(i, state, detail):
        q.put((i, state, detail))

    def poll():
        try:
            while True:
                i, state, detail = q.get_nowait()
                if i == -1:
                    st["done"] = state
                    continue
                ic, t2 = rows[i]
                lvl = state
                if state == "bad" and items[i]["level"] != "fatal":
                    lvl = "warn"
                ic.configure(text=("!" if lvl == "warn" else ICON.get(state, "·")), fg=COL.get(lvl, MUT))
                t2.configure(text=detail, fg=(COL.get(lvl, MUT) if state in ("bad", "fix") else MUT))
        except queue.Empty:
            pass
        if st["done"] is None:
            root.after(80, poll)
        else:
            fatal, restart = st["done"]
            anybad = any(it["state"] == "bad" for it in items)
            if fatal:
                head.configure(text="برنامه نمی‌تواند اجرا شود", fg=COL["bad"])
                btn.configure(text="بستن", state="normal", command=root.destroy)
            elif anybad:
                head.configure(text="بعضی امکانات در دسترس نیستند", fg=COL["warn"])
                btn.configure(text="ادامه", state="normal", command=root.destroy)
            else:
                head.configure(text="همه‌چیز آماده است ✓", fg=COL["ok"])
                root.after(1100, root.destroy)

    def work():
        try:
            res = _pf_run(items, post)
        except Exception as exc:
            dbg("preflight crashed: %r" % (exc,))
            res = (False, False)
        post(-1, res, "")

    root.after(80, poll)
    threading.Thread(target=work, daemon=True).start()
    root.mainloop()
    return st["done"] or (False, False)


def _run_preflight():
    """قبل از بارگذاری wx اجرا می‌شود. اگر همه‌چیز سالم باشد بی‌صدا رد می‌شود؛ وگرنه چک‌لیست را نشان می‌دهد."""
    if os.environ.get("_42OCR_PF_SKIP") == "1" or "--skip-check" in sys.argv:
        return
    try:
        items = [it for it in _pf_items() if it["key"] != "wv2"]      # WebView2 را خودِ برنامه با اجازه‌ی کاربر نصب می‌کند
        quiet = []                                          # بررسی بی‌صدا؛ فقط اگر مشکلی بود پنجره باز می‌شود
        for it in items:
            try:
                ok, detail = it["check"]()
            except Exception as exc:
                ok, detail = False, "بررسی ممکن نشد: %s" % exc
            it["state"], it["detail"] = ("ok" if ok else "bad"), detail
        bad = [it for it in items if it["state"] == "bad"]
        force = "--check" in sys.argv
        if not bad and not force:
            return
        fixable = [it for it in bad if it["fix"] is not None]
        fatal_now = [it for it in bad if it["level"] == "fatal"]
        seen = os.path.join(_APPDATA42, "pf_seen.json")
        try:
            with open(seen, "r", encoding="utf-8") as f:
                seen_keys = set(json.load(f))
        except Exception:
            seen_keys = set()
        # موارد غیرقابل‌نصب و غیرضروری (مثل ویندوز ۳۲ بیتی) فقط یک‌بار گزارش می‌شوند تا مزاحم نشوند
        fresh = [it for it in bad if it["fix"] is None and it["level"] != "fatal" and it["key"] not in seen_keys]
        if not fixable and not fatal_now and not fresh and not force:
            return
        if fixable and _pf_relaunch_admin():
            sys.exit(0)
        dbg("preflight: bad=%s" % [it["key"] for it in bad])
        if force and not bad:
            os.environ.pop("_42OCR_PF_RESTARTED", None)
        for it in items:                                   # پنجره از اول و با ترتیب کامل کار می‌کند
            it["state"], it["detail"] = "wait", ""
        res = _pf_window(items)
        if res is None:                                    # tkinter نیست: بدون پنجره
            if fixable:
                _msg("در حال بررسی و نصب پیش‌نیازها…\nچند لحظه صبر کنید.")
            res = _pf_run(items, lambda *a: None)
            if any(it["state"] == "bad" for it in items):
                _msg("نتیجه‌ی بررسی سیستم:\n\n" + _pf_report(items), 0x10 if res[0] else 0x30)
        fatal, restart = res
        try:
            os.makedirs(_APPDATA42, exist_ok=True)
            keep = seen_keys | {it["key"] for it in items if it["state"] == "bad" and it["fix"] is None and it["level"] != "fatal"}
            with open(seen, "w", encoding="utf-8") as f:
                json.dump(sorted(keep), f)
        except Exception:
            pass
        if fatal:
            sys.exit(1)
        if restart and os.environ.get("_42OCR_PF_RESTARTED") != "1":
            os.environ["_42OCR_PF_RESTARTED"] = "1"
            _restart()
    except SystemExit:
        raise
    except Exception as exc:
        dbg("preflight error: %r" % (exc,))


_run_preflight()

_wv_old = " ".join(a for a in os.environ.get("WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS", "").split()
                   if not a.startswith(("--no-proxy-server", "--proxy-server", "--disable-quic")))
os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = (_wv_old + " " + _webview_args()).strip()
import wx                       
import wx.adv                   
import wx.html2                 
from PIL import Image, ImageDraw, ImageGrab   

# فونت سفارشی حذف شد؛ فونت معمولی خود ویندوز استفاده می‌شود.
UI_FONT_FACE = "Segoe UI"


def _system_dpi_scale():
    """ضریب مقیاس صفحه (۱٫۰ = ۹۶ DPI) روی هر نسخه‌ی ویندوز ۱۰/۱۱.
    GetDpiForSystem فقط از ویندوز ۱۰ نسخه‌ی 1607 به بعد هست؛ در نسخه‌های قدیمی‌تر با GetDeviceCaps / shcore جایگزین می‌شود."""
    try:
        return max(1.0, ctypes.windll.user32.GetDpiForSystem() / 96.0)
    except Exception:
        pass
    try:
        u32, g32 = ctypes.windll.user32, ctypes.windll.gdi32
        hdc = u32.GetDC(0)
        try:
            dpi = g32.GetDeviceCaps(hdc, 88)            # LOGPIXELSX
        finally:
            u32.ReleaseDC(0, hdc)
        if dpi and dpi > 0:
            return max(1.0, dpi / 96.0)
    except Exception:
        pass
    return 1.0
_UI_SCALE = 1.0                      # اندازه‌ی رابط پنل (۱٫۰ تا ۱٫۵)


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
    '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'
    'csISSv0KqtvTg0u7M9LBGrTKvPY3BOpQO+QyrROZ1usMDAU0FEgfwBpB9wFVAnyCMr9B+7JNbzQzLEKAtgN3ASR8951+1Enh'
    'smTqvUfAQJROoVcS6L6jhljJxJHdsWKnVJmI8mhLMyfW+z2AEoHboqZe09YjPOZYT3inwJj/iD8QMcMClAMKrQDtT52RzsHT'
    'afbWyy/MRxc3s3y0Xb9x4wcS4EUY3gMDsvqIkmoWCIzAphqY0n8MePnO0dvfbwBkt/7L59L/y+9sf/7yQfnVvbH5YgB7flZQ'
    'eF3koHCmvnooh6/csLPDOblhi/O1iMtOQhvGuU5eW7vSsmZjQIFijkQDWQOThERJCGrFjCTSaIkGSJBoCy9A5RakJI41VEBI'
    'OoQuBAEIOvAwmpHXHoVxSLUgZkInISgPGOsRaiBkIAlZQkAgDo3n1FjZPIA3WWZRm3w66Af5s5/txU9/etjbGzXrb746WvuT'
    'yaTMJuDNFV/EWpphyjoJfNJYoVkJaEVivKJBzFjpAIY8Gu/FOwfnDAI46iekjGPMIgUmfgcb7YHbzD0oZXAKIGBGE4SJ6gwf'
    'jx57Xine6SWrvXNhd+MW2ygoJ3ubrpqtMjxUrA7T7vqtMB3MvG20N02w6Gz9GDsdkYj3DBEiZs9xZFScNI4jD/FknGOIJyjt'
    '4T25ogl9XUbiqoCDqOYorT0jsLPJKbN77ZQU5QleO3sqXj0bBu2+KKWglsOadGyC+2GG+0GMlhlEoGoTnuYauFYBm7mtPw3G'
    'RifC14vJzrj49g9+jgdbz+vzWyfiYS/odkCsSCowlc5jAgBJSJvPXNDh9uc60x9c7IwPfV1n092mbDJHfpSE4c3TglduAaM3'
    'gdd6ZTG+cPvGr/QlXb+w2Zaw07Uoq8DV9d1JHpEPS9tvWVvEgqglbjHzqxfOP0oc0NSArRFyik9tnocNaPPmjeLPTeezJ64C'
    's5K4TaxaYHpLnPstVY3/qQDfaRpeq6E1p4nXQbLZ02tdZXNjoTcMek9aCvteXO3BbWF9jjjoQNTTymObxO8Q/BQQA1DgIbGA'
    'g4Wnyr3WSh8NNAHWMLy1CPpNmJxApFuO3dz6UaHtrcobewtsLxKT1Y1ejSQyFuWudQiaxs1tWUlgHOJFz58aIk8QXpgn0kea'
    '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'
    'Vw7+xuc/9PVf/8+eV/nrg+1qa/BQf2fjHnswgAyzRncyUdFj96F3sh1wM0KogAyQok60odqL+c7WCnwblCz4k50Lbe4w0/3O'
    'WaXAkcAroKkUlgF0dqZwX30V5ne+hODlF9GZ9OHDAFFDgwMPTQaNEAhVPb5JAiDR9W8IK8YQjFHhUMhNw+k/TgeWWaMvHvUh'
    '1zjAeU/eOzgvMKWghMAUAnEOKgZ0oMGhgiVCVWQoxheRb7IUr5GnXS/tWMLSBlfWNgdX770Hx5aPNx7IHb9/Y9djc3NcbF7f'
    'BRE5AGpuLmlNJs4bgzKKyGitzWxiQqhJUw7YHzM3V4FyS0QSujUVaOYiSk7+hDznf1pwf9Td7FE6AMmt8yBL4ILgxgAmQMrA'
    'gxHQ5RL9ahfmYBe67GOU91HubmO4vYPR1h5G+wNkgxG4yBHbHIG3cNYgrCrElKGlCmip4I2vw7RZIQ1DpK0EQTvBNLMYTYYI'
    'SotJaTCeMmzusb1bYGOvwqR0eRLyqN1QaEZoeefDPHekNdR8Q5gF3kypKATDNEQexRLD0LwHEhFIWcEwycSJrFZW1gNFvVZE'
    'jyWe4mkl29NSCudxKlQICQQHgRfZtF5iTViIlbA4+mbp8G0TRK/bqLG3M97RyNVDbaWOzTdw9ljTn2tG1I0UqTNzqvvOU+ph'
    'zewvrKOxcVB7HGoBTE7oG0LFBOdBwwnrIge0A1IQmkRIQIhD5oAUxSqQiEMKlY4DVudLj+VVU3wwEnpzUpoX3oB5BsDrHXT2'
    'f/78KYfpcXv1134tdOIr/tjTxbHH8YyyuOaA94jffR9ef8bu9XeWJqtXovblD8TdDz46d+LRu9ViL/V7gNuE56yyqtIKnhnE'
    '9F0ZyYT/eSRg3Z4rfPT6rQiMc2Cu4xEXASyOc7jnXsHeb37G46tfxMr4KicpkJGGBqGdAKkWWANUhsBMaMSCxgy4DHKCq2Z6'
    '8cN+lm521z8u/lq3u33JLC1oJj0TJnYQEutAuRXO61RGBB6IjCCEoCmClRhoNBmnU8FcCJiZdC0m+JYW3RHH8ww/aquDy/v2'
    'y4OsfOkX/5cnj3dXmv+r3/3c2vv3dsZYu1pMtzcxnb2cZqPB3bLk3aqaZmUJV5alO5IrcePmheGkNEa/4b2EQDW8mXdVz3qh'
    '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'
    'rej79zY4Ry0Mlo41XvwSwl/5RdR+7rNITi9RArBZL8Xub/4g2Put7zlz/dYdmIM/iYHv/C+/9r997+/e+caHfcL4MUr58Xq8'
    'Hq+j2+L0/9+Hd52SMKp+9h/8BzQaJiJMRi75uWc6n/t7f3Nz582bhXfcZJM1fbYL27t/YNbX72Kvd0+Nysx3e2x2u8r3+giZ'
    'bMLehdoJ4ZhsqLgEvCF4DsjJWuhFu8Y41mYsrUjRasbh3Hw9WVisxfMrgYwXEcTtIlDxgVDBQVHw4Pu/9U/hnYtuvf7PW8ng'
    'Xn1e76Rt200btShC2HCUtnoUN7Z92Lg78sl2xyDbsDnWTal2dFnf8Fm85gta0yXvFaXul2XfW7enbVlmtogtnGJAeoIUREJK'
    'RTIISYYRRBCykAEJCCYmIk+VFZ2VlaCFq7xoq7g4FqSYBB4xDioPBBzGiGmaONyMbw98f9X4Jg4LRvJ/+j2Tj4oYk6tGPuzv'
    'aUqIQ0w5OFXHChNa0ANotQBDHFa1PqjqQClBkWRRU6xqESiJRClJdHTm7nV39Ktb94Z/tHXv4Nu9zr03nf3OmpS/7+fmfnAh'
    'trsh6blc+qfMqN9w1zb6pJO5qHHhK7WnXj4385d+ybd+5Wdt9MI5KKnYD6zrfOsabf5/ftcfvP7dXerceb0e5d+bEeo9ulsf'
    'yNMSu7tRCMwoYEEC+z+WksrjlvLj9Xj9i0U1wgcQVwSq+oKPHTuWdobDE4H3obJ2lClf96SedBrHhS6lgM9CoAwQQSydXHDN'
    '9lO+PvdiuHxspvHCc0V64bykxblj8sxqJM+vwofwBSBygPS4oagAihwoHpaIS414WEDu5XDXd2HubmfFzsbt3sbt27uXfrBV'
    '3Hx7iHLDABARIGoBwjAAk4y6RqT3yyDd8CIq0lK2wtytDq2Pe8gs1PAURfZnY+GejMFIveguuGD3rEwu/0zSvHU8ipdKQb9Q'
    'i6OTy7UUM0mKubSOmaiOIK4xVFxJHBWaUBRAXsKVFmwB9mOIFXkiYrCokMBCuDFlZ+xgI8eHd0JpwZSgxMRK0NOhDKPH1MzT'
    'A8L+5Ph60BjcJafaxP7IQMPTD1fQDpUHoMMhAG2SeBDBE8GDmFmCquwELImDJHRIlUPAYmD76np/n6/u721e3tvdubTb2bkz'
    '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'
    'qyAAAAAASUVORK5CYII='
)



if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")





ACCENT = wx.Colour(255, 45, 60)
THEME_COLORS = (("قرمز", "#FF2D3C"), ("سبز", "#2ECC71"), ("آبی", "#4299FF"),
                ("بنفش", "#A06EFF"), ("نارنجی", "#FF9632"), ("صورتی", "#FF5AAA"))
_FONT_CANDIDATES = ("Segoe UI", "Tahoma", "Vazirmatn", "IRANSans", "Arial", "Calibri")
_fonts_cache = []


def available_fonts():
    """فونت‌های نصب‌شده‌ی قابل انتخاب (حداکثر ۴ تا)؛ Segoe UI اول."""
    if not _fonts_cache:
        try:
            have = {f.lower() for f in wx.FontEnumerator().GetFacenames()}
        except Exception:
            have = set()
        found = [f for f in _FONT_CANDIDATES if f.lower() in have][:4]
        _fonts_cache.extend(found or ["Segoe UI"])
    return list(_fonts_cache)


def _mix(c, base, t):
    """رنگ c را با base ترکیب می‌کند (t = سهم base)."""
    return wx.Colour(*(int(c[i] * (1 - t) + base[i] * t) for i in range(3)))


def apply_theme(accent=None, font=None):
    global ACCENT, UI_FONT_FACE
    if accent:
        m = re.fullmatch(r"#([0-9a-fA-F]{6})", str(accent))
        if m:
            v = int(m.group(1), 16)
            ACCENT = wx.Colour((v >> 16) & 255, (v >> 8) & 255, v & 255)
    if font:
        UI_FONT_FACE = str(font)
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


_SUBCLASSPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t,
                                   ctypes.c_ssize_t, ctypes.c_size_t, ctypes.c_size_t)
_comctl32 = ctypes.windll.comctl32
_comctl32.SetWindowSubclass.argtypes = [ctypes.c_void_p, _SUBCLASSPROC, ctypes.c_size_t, ctypes.c_size_t]
_comctl32.SetWindowSubclass.restype = ctypes.c_int
_comctl32.DefSubclassProc.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
_comctl32.DefSubclassProc.restype = ctypes.c_ssize_t


def _noact_proc(hwnd, msg, wparam, lparam, _uid, _ref):
    # WM_MOUSEACTIVATE -> MA_NOACTIVATE: کلیک روی پنجره‌های ما هرگز فوکوس را از بازی نمی‌گیرد
    if msg == 0x0021:
        return 3
    return _comctl32.DefSubclassProc(hwnd, msg, wparam, lparam)


_noact_cb = _SUBCLASSPROC(_noact_proc)


def no_activate(win, layered=False):
    """پنجره هرگز فوکوس را نمی‌گیرد و در Alt+Tab/تسک‌بار دیده نمی‌شود."""
    h = win.GetHandle()
    st = user32.GetWindowLongW(h, GWL_EXSTYLE)
    st |= WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | (WS_EX_LAYERED if layered else 0)
    user32.SetWindowLongW(h, GWL_EXSTYLE, st)
    try:
        _comctl32.SetWindowSubclass(h, _noact_cb, 1, 0)
    except Exception:
        pass


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


_SetWindowLongPtr = getattr(user32, "SetWindowLongPtrW", None) or user32.SetWindowLongW
_SetWindowLongPtr.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
_SetWindowLongPtr.restype = ctypes.c_void_p


def set_owner(win, owner_hwnd):
    """پنجره را «زیرمجموعه‌ی» پنجره‌ی بازی می‌کند؛ ویندوز پنجره‌ی owned را همیشه بالاتر از owner نگه می‌دارد،
    حتی وقتی بازی خودش را Topmost/بالا می‌آورد. owner_hwnd=None یعنی آزاد کردن."""
    try:
        _SetWindowLongPtr(win.GetHandle(), -8, owner_hwnd or None)      # GWLP_HWNDPARENT
    except Exception:
        pass


user32.GetWindow.argtypes = [ctypes.c_void_p, ctypes.c_uint]
user32.GetWindow.restype = ctypes.c_void_p


def _foreign_above(hwnd):
    """آیا پنجره‌ی قابل‌مشاهده‌ای از برنامه‌های دیگر بالاتر از hwnd است؟"""
    try:
        prev = user32.GetWindow(hwnd, 3)          # GW_HWNDPREV
        n = 0
        while prev and n < 300:
            if user32.IsWindowVisible(prev) and _pid_of(prev) != _OWN_PID:
                return True
            prev = user32.GetWindow(prev, 3)
            n += 1
    except Exception:
        return True
    return False


def raise_top(win):
    """دوباره Topmost می‌کند، فقط وقتی واقعاً پنجره‌ی دیگری (مثلاً بازی) بالاتر آمده.
    بالا‌آوردنِ پیوسته بدون دلیل باعث می‌شود بعضی بازی‌ها فوکوس/حالت تمام‌صفحه را از دست بدهند."""
    h = win.GetHandle()
    if not _foreign_above(h):
        return
    user32.SetWindowPos(h, HWND_TOPMOST, 0, 0, 0, 0, 0x0001 | 0x0002 | SWP_NOACTIVATE)


def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin():
    try:
        exe = sys.executable
        args = " ".join('"%s"' % a for a in sys.argv[1:])
        os.environ["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
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


_BRAND_LEVELS = 100                                 # سطح‌های شفافیت (بیشتر = محوشدن نرم‌تر — بدون چشمک)


def make_brand_bitmap(width, height, opacity=1.0):
    """لوگو را با نسبت تصویر حفظ‌شده داخل یک بوم شفاف و متناسب با DPI می‌سازد (opacity برای چشمک آرام)."""
    width, height = max(1, int(width)), max(1, int(height))
    level = max(0, min(_BRAND_LEVELS, int(round(float(opacity) * _BRAND_LEVELS))))
    key = (width, height, level)
    cached = _BRAND_BITMAP_CACHE.get(key)
    if cached is not None and cached.IsOk():
        return cached
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    logo = _brand_source_image().copy()
    logo.thumbnail((max(1, width - 1), max(1, height - 1)), Image.LANCZOS)
    canvas.alpha_composite(logo, ((width - logo.width) // 2, (height - logo.height) // 2))
    if level < _BRAND_LEVELS:
        canvas.putalpha(canvas.getchannel("A").point(lambda v: v * level // _BRAND_LEVELS))
    bitmap = wx.Bitmap.FromBufferRGBA(width, height, canvas.tobytes())
    _BRAND_BITMAP_CACHE[key] = bitmap
    return bitmap


_APP_ICO_PATH = None
_ICON_CACHE = {}


def app_ico_bytes():
    """بایت‌های فایل ESH_Translator.ico که داخل خود سورس جاسازی شده است."""
    return base64.b64decode(APP_ICON_B64)


def app_ico_path():
    """فایل ico را (اگر نبود) از داده‌ی داخل سورس در پوشه‌ی داده‌ی برنامه می‌نویسد و مسیرش را می‌دهد."""
    global _APP_ICO_PATH
    if _APP_ICO_PATH and os.path.isfile(_APP_ICO_PATH):
        return _APP_ICO_PATH
    try:
        data = app_ico_bytes()
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        d = os.path.join(base, APP_DIR_NAME)
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "app.ico")
        if not os.path.isfile(path) or os.path.getsize(path) != len(data):
            tmp = path + ".tmp"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, path)
        _APP_ICO_PATH = path
        return path
    except Exception as exc:
        dbg("app ico write failed: %r" % (exc,))
        return None


def make_icon(size=None):
    """آیکون ESH (از ico جاسازی‌شده) برای Tray، نوار عنوان و تسک‌بار؛ size=None → اندازه‌ی آیکون کوچک سیستم."""
    try:
        if size is None:
            size = wx.SystemSettings.GetMetric(wx.SYS_SMALLICON_X) or 16
        size = max(16, int(size))
        hit = _ICON_CACHE.get(size)
        if hit is not None and hit.IsOk():
            return hit
        path = app_ico_path()
        if path:
            icon = wx.Icon(path, wx.BITMAP_TYPE_ICO, size, size)
            if icon.IsOk():
                _ICON_CACHE[size] = icon
                return icon
    except Exception as exc:
        dbg("make_icon failed: %r" % (exc,))
    icon = wx.Icon()
    icon.CopyFromBitmap(make_brand_bitmap(32, 32))
    return icon


def make_icon_bundle():
    """همه‌ی اندازه‌های ico (۱۶ تا ۲۵۶) برای تسک‌بار، Alt+Tab و عنوان پنجره."""
    try:
        path = app_ico_path()
        if path:
            bundle = wx.IconBundle(path, wx.BITMAP_TYPE_ICO)
            if bundle.IsOk():
                return bundle
    except Exception as exc:
        dbg("make_icon_bundle failed: %r" % (exc,))
    bundle = wx.IconBundle()
    bundle.AddIcon(make_icon(32))
    return bundle


def set_app_user_model_id():
    """تسک‌بار ویندوز آیکون خود برنامه را نشان دهد، نه آیکون python.exe."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ESH.Translator.App")
    except Exception:
        pass





def exclusive_fullscreen_active():
    """ویندوز می‌گوید برنامه‌ای D3D Fullscreen انحصاری است؟ (QUNS_RUNNING_D3D_FULL_SCREEN = 3)"""
    try:
        st = ctypes.c_int(0)
        if ctypes.windll.shell32.SHQueryUserNotificationState(ctypes.byref(st)) == 0:
            return st.value == 3
    except Exception:
        pass
    return False


CORNERS = (("same", "جای انتخاب"), ("tl", "بالا-چپ"), ("tr", "بالا-راست"),
           ("bl", "پایین-چپ"), ("br", "پایین-راست"), ("center", "وسط"))


APP_VERSION = "1.3"

_RTL_CHARS = re.compile("[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")
_LATIN_RUN = re.compile(r"[A-Za-z0-9]+(?:(?:\s*[/&+:\-.]+\s*|[ _'’,])[A-Za-z0-9]+)*%?")


def bidi(text):
    """هر تکه‌ی انگلیسی/عددی داخل متن فارسی را با LRM می‌بندد تا ترتیبش به‌هم نریزد (مثلاً «4K» نشود «K4»)."""
    text = str(text)
    if not _RTL_CHARS.search(text):
        return text
    return _LATIN_RUN.sub(lambda m: "\u200e" + m.group(0) + "\u200e", text)


class _BidiDC(object):
    """پراکسیِ DC: فقط متن‌های نقاشی‌شده را bidi می‌کند؛ بقیه‌ی متدها دست‌نخورده می‌رسند."""

    def __init__(self, dc):
        object.__setattr__(self, "_dc", dc)

    def __getattr__(self, name):
        return getattr(self._dc, name)

    def DrawText(self, text, *a, **k):
        return self._dc.DrawText(bidi(text), *a, **k)

    def DrawLabel(self, text, *a, **k):
        return self._dc.DrawLabel(bidi(text), *a, **k)


SAFE_PATH = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), APP_DIR_NAME, "safe_state.json")
_SAFE_ACTIVE = False


def _safe_write(state):
    try:
        os.makedirs(os.path.dirname(SAFE_PATH), exist_ok=True)
        with open(SAFE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception as exc:
        dbg("safe_state write failed: %r" % (exc,))


def safe_mode_begin():
    """اگر دو اجرای پیاپی بدون خروج سالم تمام شده باشند، تنظیمات پیش‌فرض برمی‌گردد (نسخه‌ی قبلی در config.json.crash می‌ماند).
    True یعنی «حالت امن» همین الان فعال شد."""
    global _SAFE_ACTIVE
    st = {}
    try:
        with open(SAFE_PATH, "r", encoding="utf-8") as f:
            st = json.load(f)
        if not isinstance(st, dict):
            st = {}
    except Exception:
        st = {}
    unclean = int(st.get("unclean", 0) or 0) + 1 if st.get("running") else 0
    triggered = unclean >= 2
    if triggered:
        base = os.path.dirname(SAFE_PATH)
        cfg = os.path.join(base, "config.json")
        try:
            if os.path.isfile(cfg):
                shutil.copyfile(cfg, cfg + ".crash")
            for f_ in (cfg, cfg + ".bak"):
                if os.path.isfile(f_):
                    os.remove(f_)
        except Exception as exc:
            dbg("safe mode reset failed: %r" % (exc,))
        unclean = 0
    _safe_write({"unclean": unclean, "running": True})
    _SAFE_ACTIVE = True
    return triggered


def safe_mode_clean_exit():
    if _SAFE_ACTIVE:
        _safe_write({"unclean": 0, "running": False})


_CFG_LIVE = []                                   # نمونه‌های Config (برای flush هنگام خروج)


class Config:
    DEFAULTS = {
        "snip_hotkey": "f3",
        "close_hotkey": "f2",
        "auto_close_seconds": 60,
        "run_on_startup": False,
        "save_dir": os.path.join(os.path.expanduser("~"), "Pictures", "ESHTranslator"),   
        "capture_monitor": 0,       
        "performance_mode": True,   
        "panel_pinned": True,
        "engine": "google",         # google | ai | offline
        "ai_provider": "openai",    # openai | gemini | openrouter
        "ai_models": {},            # نام مدل هر سرویس
        "ai_tokens": {},            # توکن هر سرویس (رمزگذاری‌شده با DPAPI)
        "ocr_lang": "eng",          # زبان OCR آفلاین (کد Tesseract)
        "output_monitor": 0,        # 0 = همان مانیتور عکس‌برداری؛ n = مانیتور شماره‌ی n
        "ai_style": "casual",       # casual | formal | subtitle  (سبک ترجمه‌ی هوش مصنوعی)
        "ai_game": "",              # نام بازی (زمینه برای هوش مصنوعی)
        "output_corner": "same",    # same | tl | tr | bl | br | center  (جای ثابت نتیجه روی مانیتور خروجی)
        "onboarded": False,         # راهنمای اولین اجرا نمایش داده شده؟
        "accent": "#FF2D3C",        # رنگ اصلی برنامه (انتخاب کاربر)
        "font_face": "Segoe UI",    # فونت برنامه (انتخاب کاربر)
        "proxy_mode": "system",     # system | custom | off
        "proxy_url": "",            # http://127.0.0.1:10809  یا  socks5://127.0.0.1:10808
        "text_over_text": False,    # ترجمه‌ی آفلاین دقیقاً روی جای متن اصلی (با پس‌زمینه‌ی هم‌رنگ)
        "ai_custom_url": "http://localhost:11434/v1",   # سرویس OpenAI-compatible سفارشی (Ollama / LM Studio / ...)
        "ai_usage": {},             # مصرف توکن هر سرویس: {prov: {in, out, n, usd}}
        "ui_scale": 100,            # اندازه‌ی رابط پنل: ۱۰۰ تا ۱۵۰ درصد
        "game_lite_ui": True,       # خاموش‌کردن انیمیشن پنل هنگام بازی تمام‌صفحه
        "stream_mode": False,       # حالت استریم: پنل از ضبط/استریم حذف و توکن پوشانده می‌شود
        "hdr_gamma": True,          # تنظیم خودکار گامای OCR وقتی مانیتور HDR است
        "nllb_model": "600m",       # مدل ترجمه‌ی آفلاین: 600m (سبک) | 1.3b (متعادل) | 3.3b (قوی‌ترین)
        # ── ترجمه‌ی زنده‌ی بازی (Game Live Mode) ──
        "game_live_roi": None,              # {"rect": [x, y, w, h], "mon": [x, y, w, h]} — محدوده‌ی زیرنویس
        "game_live_rate": "balanced",       # low | balanced | fast
        "game_live_stability_count": 2,     # تعداد مشاهده‌ی یکسان برای تثبیت متن
        "game_live_show_source": False,     # نمایش متن انگلیسی زیر ترجمه
        "game_live_overlay_opacity": 90,    # شفافیت پنجره‌ی ترجمه (٪)
        "game_live_overlay_font_size": 22,  # اندازه‌ی متن ترجمه (پیکسل)
        "game_live_clear_delay_ms": 2500,   # تأخیر پاک‌شدن ترجمه بعد از ناپدیدشدن زیرنویس
        "live_hotkey": "f4",                # شروع/توقف ترجمه‌ی زنده
    }

    def __init__(self):
        self._wlock = threading.Lock()
        self._io_lock = threading.Lock()
        self._pending = None
        self._timer = None
        _CFG_LIVE.append(self)
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        self.dir = os.path.join(base, APP_DIR_NAME)
        self.path = os.path.join(self.dir, "config.json")
        self.data = dict(self.DEFAULTS)
        self.bak_path = self.path + ".bak"
        stored = None
        for cand in (self.path, self.bak_path):      # اگر فایل اصلی خراب بود، نسخه‌ی پشتیبان خوانده می‌شود
            try:
                with open(cand, "r", encoding="utf-8") as f:
                    j = json.load(f)
                if isinstance(j, dict):
                    stored = j
                    if cand == self.bak_path:
                        dbg("config.json خراب بود؛ از config.json.bak بازیابی شد")
                    break
            except Exception:
                continue
        if stored is not None:
            if "hotkey" in stored and "close_hotkey" not in stored:
                stored["close_hotkey"] = stored["hotkey"]
            for k in self.DEFAULTS:
                if k in stored:
                    self.data[k] = stored[k]
        for _k in ("ai_models", "ai_tokens", "ai_usage"):
            _v = self.data.get(_k)
            self.data[_k] = dict(_v) if isinstance(_v, dict) else {}
        if self.data.get("output_corner") not in ("same", "tl", "tr", "bl", "br", "center"):
            self.data["output_corner"] = "same"
        self.data["onboarded"] = bool(self.data.get("onboarded"))
        self.data["text_over_text"] = bool(self.data.get("text_over_text"))
        if self.data.get("ai_style") not in ("casual", "formal"):
            self.data["ai_style"] = "casual"
        self.data["ai_game"] = " ".join(str(self.data.get("ai_game") or "").split())[:60]
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(self.data.get("accent") or "")):
            self.data["accent"] = "#FF2D3C"
        self.data["font_face"] = str(self.data.get("font_face") or "Segoe UI")[:40]
        if self.data.get("proxy_mode") not in ("system", "custom", "off"):
            self.data["proxy_mode"] = "system"
        self.data["proxy_url"] = str(self.data.get("proxy_url") or "").strip()[:200]
        if self.data.get("engine") not in ("google", "ai", "offline"):
            self.data["engine"] = "google"
        try:
            _sc = int(self.data.get("ui_scale") or 100)
        except Exception:
            _sc = 100
        self.data["ui_scale"] = max(100, min(150, int(round(_sc / 10.0)) * 10))
        self.data["game_lite_ui"] = bool(self.data.get("game_lite_ui", True))
        self.data["stream_mode"] = bool(self.data.get("stream_mode", False))
        self.data["hdr_gamma"] = bool(self.data.get("hdr_gamma", True))
        if self.data.get("nllb_model") not in NLLB_MODEL_KEYS:
            self.data["nllb_model"] = "600m"
        self._validate_live()
        # «همان مانیتور عکس‌برداری» پیش‌فرض مقصد نمایش نتیجه است؛
        # برای تنظیمات ذخیره‌شدهٔ نسخه‌های قبل، فقط یک‌بار به همین پیش‌فرض برمی‌گردد
        # (بعد از آن انتخاب دستی کاربر همیشه محترم است).
        try:
            _outmon_flagged = bool(stored.get("_outmon_same_v1"))
        except Exception:
            _outmon_flagged = False
        if not _outmon_flagged:
            self.data["output_monitor"] = self.DEFAULTS["output_monitor"]
            self.data["_outmon_same_v1"] = True
        _cu = str(self.data.get("ai_custom_url") or "").strip().rstrip("/")[:200]
        self.data["ai_custom_url"] = _cu if re.match(r"^https?://\S+$", _cu, re.I) else self.DEFAULTS["ai_custom_url"]
        if self.data.get("ai_provider") not in ("openai", "gemini", "openrouter", "custom"):
            self.data["ai_provider"] = "openai"
        if self.data.get("ocr_lang") not in ("eng", "jpn", "kor", "chi_sim", "rus", "deu", "fra",
                                               "spa", "ita", "por", "tur", "ara", "pol", "ukr"):
            self.data["ocr_lang"] = "eng"
        # پوشه‌ی عکس‌ها همیشه باید با نام ESHTranslator باشد (پاک‌سازی موقع خروج فقط همین پوشه را پاک می‌کند)
        try:
            sd = os.path.normpath(str(self.data.get("save_dir") or self.DEFAULTS["save_dir"]))
            name = os.path.basename(sd).lower()
            if name == "42ocr":
                sd = os.path.join(os.path.dirname(sd), "ESHTranslator")
            elif name != "eshtranslator":
                sd = os.path.join(sd, "ESHTranslator")
            self.data["save_dir"] = sd
        except Exception:
            self.data["save_dir"] = self.DEFAULTS["save_dir"]

    def _validate_live(self):
        d = self.data
        roi = d.get("game_live_roi")
        ok = False
        if isinstance(roi, dict):
            try:
                r, m = [int(v) for v in roi["rect"]], [int(v) for v in roi["mon"]]
                ok = len(r) == 4 and len(m) == 4 and r[2] >= 6 and r[3] >= 6 and m[2] > 0 and m[3] > 0
                if ok:
                    d["game_live_roi"] = {"rect": r, "mon": m}
            except Exception:
                ok = False
        if not ok:
            d["game_live_roi"] = None
        if d.get("game_live_rate") not in ("low", "balanced", "fast"):
            d["game_live_rate"] = "balanced"
        try:
            d["game_live_stability_count"] = max(1, min(4, int(d.get("game_live_stability_count") or 2)))
        except Exception:
            d["game_live_stability_count"] = 2
        d["game_live_show_source"] = bool(d.get("game_live_show_source"))
        try:
            op = int(d.get("game_live_overlay_opacity") or 90)
        except Exception:
            op = 90
        d["game_live_overlay_opacity"] = min((50, 65, 80, 90, 100), key=lambda v: abs(v - op))
        try:
            fs = int(d.get("game_live_overlay_font_size") or 22)
        except Exception:
            fs = 22
        d["game_live_overlay_font_size"] = min((16, 18, 20, 22, 26, 30), key=lambda v: abs(v - fs))
        try:
            d["game_live_clear_delay_ms"] = max(500, min(10000, int(d.get("game_live_clear_delay_ms") or 2500)))
        except Exception:
            d["game_live_clear_delay_ms"] = 2500
        hk = str(d.get("live_hotkey") or "f4").strip().lower()
        d["live_hotkey"] = hk if (hk and hk not in (str(d.get("snip_hotkey")), str(d.get("close_hotkey")))) else "f4"

    def __getitem__(self, k):
        return self.data[k]

    def set(self, k, v):
        if self.data.get(k) == v:
            return
        self.data[k] = v
        self._save_soon()

    def _snapshot(self):
        return json.dumps(self.data, ensure_ascii=False, indent=2)

    def _save_soon(self):
        """ذخیره‌ی بدون لگ برای UI: متن JSON همین‌جا (آنی) ساخته می‌شود، ولی نوشتن روی دیسک
        (fsync) با تأخیر ۰٫۳۵ ثانیه و در ترد پس‌زمینه انجام می‌شود؛ کلیک‌های پشت‌سرهم یک‌بار ذخیره می‌شوند."""
        try:
            text = self._snapshot()
        except Exception:
            self._save()
            return
        with self._wlock:
            self._pending = text
            if self._timer is None:
                self._timer = threading.Timer(0.35, self.flush)
                self._timer.daemon = True
                self._timer.start()

    def flush(self):
        """اگر ذخیره‌ای در صف است، همین الان روی دیسک می‌نویسد (هنگام خروج/راه‌اندازی مجدد)."""
        with self._wlock:
            text, self._pending = self._pending, None
            self._timer = None
        if text is not None:
            self._write_text(text)

    def _save(self):
        """ذخیره‌ی هم‌زمان (فوری)."""
        with self._wlock:
            self._pending = None
        try:
            self._write_text(self._snapshot())
        except Exception as exc:
            dbg("config save failed: %r" % (exc,))

    def _write_text(self, text):
        """ذخیره‌ی امن: اول در فایل موقت نوشته می‌شود، نسخه‌ی سالمِ قبلی به .bak می‌رود، بعد جایگزین می‌شود."""
        with self._io_lock:
            try:
                os.makedirs(self.dir, exist_ok=True)
                tmp = self.path + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    f.write(text)
                    f.flush()
                    os.fsync(f.fileno())
                try:                                   # فقط اگر فایل فعلی سالم است پشتیبان گرفته شود
                    with open(self.path, "r", encoding="utf-8") as f:
                        json.load(f)
                    shutil.copyfile(self.path, self.bak_path)
                except Exception:
                    pass
                os.replace(tmp, self.path)
            except Exception as exc:
                dbg("config save failed: %r" % (exc,))


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

        self.browser, self._edge = self._make_browser()
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

    def _make_browser(self):
        """Edge (WebView2) را صریح می‌خواهد؛ پیش‌فرض ویندوز IE است که RunScriptAsync ندارد
        (همان خطای «Run Scripts Async Not Supported»)."""
        wv = wx.html2.WebView
        edge = getattr(wx.html2, "WebViewBackendEdge", None)
        if edge is not None:
            def _avail():
                try:
                    return bool(wv.IsBackendAvailable(edge))
                except Exception:
                    return False
            ok = _avail()
            if not ok:
                _ensure_wv2_loader(download=True)
                ok = _avail()
            if not ok and not _webview2_installed() and not globals().get("_PREREQ_MANAGED"):
                try:
                    _ensure_webview2_runtime_now()
                except Exception as exc:
                    dbg("wv2 runtime install: %r" % (exc,))
                ok = _avail()
            if ok:
                try:
                    b = wv.New(self, backend=edge)
                    if b is not None:
                        dbg("webview backend: Edge")
                        return b, True
                except Exception as exc:
                    dbg("Edge backend failed: %r" % (exc,))
        dbg("webview backend: fallback (no Edge)")
        return wv.New(self), False

    def _run_js(self, js):
        """اجرای جاوااسکریپت؛ روی Edge غیرهمزمان، روی بک‌اندهای دیگر همزمان با همان مسیر نتیجه."""
        if self._edge:
            self.browser.RunScriptAsync(js)
            return
        res = self.browser.RunScript(js)
        txt = res[1] if isinstance(res, tuple) else res

        class _Evt:
            def GetString(self_, _t=txt):
                return "" if _t is None else str(_t)
        wx.CallAfter(self._on_script, _Evt())

    @staticmethod
    def _url(lang):
        return "https://translate.google.com/?sl=auto&tl=%s&op=images&hl=fa" % lang

    def start(self, img):
        if self._busy:
            self._force_reset()
        if not self._edge:
            self.on_error("Microsoft Edge WebView2 Runtime روی این ویندوز نصب نیست و نصب خودکار انجام نشد.\n"
                          "آن را از " + WEBVIEW2_URL + " نصب کنید (یا موتور ترجمه را روی AI بگذارید).")
            return
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
            self._run_js(self.INJECT_JS + "('" + self._data_url + "')")
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
            self._run_js(self.EXTRACT_JS)
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





class _MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", ctypes.wintypes.POINT), ("mouseData", ctypes.c_ulong), ("flags", ctypes.c_ulong),
                ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.c_void_p)]


_HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, ctypes.c_size_t, ctypes.c_ssize_t)
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, _HOOKPROC, ctypes.c_void_p, ctypes.c_ulong]
user32.SetWindowsHookExW.restype = ctypes.c_void_p
user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t, ctypes.c_ssize_t]
user32.CallNextHookEx.restype = ctypes.c_ssize_t
user32.UnhookWindowsHookEx.argtypes = [ctypes.c_void_p]


class MouseGrab:
    """موس را موقع اسنیپ از بازی «می‌دزدد».
    بازیِ تمام‌صفحه موس را قفل/مرکزچین می‌کند (ClipCursor / SetCursorPos) و کلیک‌ها را برای خودش می‌خواهد؛
    برای همین انتخاب ناحیه فقط در یک مربع کوچک کار می‌کرد. اینجا با یک Low-Level hook حرکت‌ها و کلیک‌ها
    را از بازی می‌گیریم و موقعیت مجازیِ خودمان را (روی کل مانیتور) نگه می‌داریم."""
    WH_MOUSE_LL = 14

    def __init__(self, owner):
        self.owner = owner
        self.hook = None
        self.active = False
        self.x = self.y = 0.0
        self.bounds = (0, 0, 1, 1)
        self._proc = _HOOKPROC(self._callback)

    def start(self, x, y, bounds):
        self.stop()
        self.x, self.y = float(x), float(y)
        self.bounds = bounds
        try:
            self.hook = user32.SetWindowsHookExW(self.WH_MOUSE_LL, self._proc, None, 0)
        except Exception:
            self.hook = None
        self.active = bool(self.hook)
        return self.active

    def stop(self):
        self.active = False
        h, self.hook = self.hook, None
        if h:
            try:
                user32.UnhookWindowsHookEx(h)
            except Exception:
                pass

    def _callback(self, ncode, wparam, lparam):
        try:
            if ncode == 0 and self.active:
                info = _MSLLHOOKSTRUCT.from_address(lparam)
                if not (info.flags & 0x01):                      # رویداد تزریقی را دست نمی‌زنیم
                    if wparam == 0x200:                          # WM_MOUSEMOVE
                        cx, cy = _cursor_pos()
                        bx, by, bw, bh = self.bounds
                        self.x = max(bx, min(bx + bw - 1, self.x + (info.pt.x - cx)))
                        self.y = max(by, min(by + bh - 1, self.y + (info.pt.y - cy)))
                        return 1
                    if wparam == 0x201:                          # LBUTTONDOWN
                        wx.CallAfter(self.owner._hk_down)
                        return 1
                    if wparam == 0x202:                          # LBUTTONUP
                        wx.CallAfter(self.owner._hk_up)
                        return 1
                    if wparam == 0x204:                          # RBUTTONDOWN = لغو
                        wx.CallAfter(self.owner.cancel)
                        return 1
                    if 0x200 < wparam <= 0x20E:                  # بقیه‌ی دکمه‌ها/چرخ
                        return 1
        except Exception:
            pass
        return user32.CallNextHookEx(None, ncode, wparam, lparam)



_WINEVENTPROC = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p,
                                   ctypes.c_long, ctypes.c_long, ctypes.c_ulong, ctypes.c_ulong)
user32.SetWinEventHook.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, _WINEVENTPROC,
                                   ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
user32.SetWinEventHook.restype = ctypes.c_void_p
user32.UnhookWinEvent.argtypes = [ctypes.c_void_p]


class TopWatcher:
    """هر بار پنجره‌ی فعال عوض شد (مثلاً رفتی داخل بازی) بلافاصله پنل/نتیجه را دوباره روی همه می‌آورد."""

    def __init__(self, app):
        self.app = app
        self.hooks = []
        self._proc = _WINEVENTPROC(self._cb)
        for ev in (0x0003, 0x0017):          # FOREGROUND, MINIMIZEEND
            try:
                h = user32.SetWinEventHook(ev, ev, None, self._proc, 0, 0, 0x0002)   # OUTOFCONTEXT|SKIPOWNPROCESS
                if h:
                    self.hooks.append(h)
            except Exception:
                pass

    def _cb(self, *_a):
        try:
            wx.CallAfter(self.app.raise_overlays)
            wx.CallLater(150, self.app.raise_overlays)
            wx.CallLater(600, self.app.raise_overlays)
            wx.CallLater(1500, self.app.raise_overlays)
        except Exception:
            pass

    def stop(self):
        hs, self.hooks = self.hooks, []
        for h in hs:
            try:
                user32.UnhookWinEvent(h)
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
        self.grab = MouseGrab(self)
        self._cross_last = None
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
        self.Bind(wx.EVT_SET_CURSOR, self._on_set_cursor)
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
        cx, cy = _cursor_pos()
        if not (region[0] <= cx < region[0] + region[2] and region[1] <= cy < region[1] + region[3]):
            cx, cy = region[0] + region[2] // 2, region[1] + region[3] // 2
        self._cross_last = None
        self.grab.start(cx, cy, region)
        self._owner = None
        try:
            fg = user32.GetForegroundWindow()
            if fg and _pid_of(fg) != _OWN_PID and _class_of(fg) not in _SHELL_CLASSES:
                self._owner = fg
                set_owner(self, fg)
        except Exception:
            pass
        place_top(self, *region)
        self.Refresh(False)
        self._keep_top()
        if not self._drag_timer.IsRunning():
            self._drag_timer.Start(8)
        return True, None

    def _keep_top(self):
        if self.active:
            raise_top(self)
            wx.CallLater(120, self._keep_top)

    def _on_set_cursor(self, evt):
        evt.SetCursor(wx.Cursor(wx.CURSOR_BLANK if self.grab.active else wx.CURSOR_CROSS))

    def _hk_down(self):
        if self.active and self.start is None:
            self._on_down(None)

    def _hk_up(self):
        if self.active and self.start is not None:
            self._finish_selection(self._local_cursor())


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

        if self.start is None and self.active:
            p = self._local_cursor()
            dc.SetPen(wx.Pen(ACCENT, 2))
            dc.DrawLine(0, p.y, gw, p.y)
            dc.DrawLine(p.x, 0, p.x, gh)
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawCircle(p.x, p.y, 7)

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
        if self.grab.active:
            sx, sy = int(self.grab.x), int(self.grab.y)
        else:
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
        if not self.active or self.start is not None:
            return
        self.start = self.cur = self._local_cursor()
        self._last = None
        if not self.HasCapture():
            try:
                self.CaptureMouse()
            except Exception:
                pass
        if not self._drag_timer.IsRunning():
            self._drag_timer.Start(8)

    def _on_motion(self, evt):
        if self.start is not None:
            pos = self._local_cursor()
            if pos != self.cur:
                self.cur = pos
                self._refresh_sel()

    def _poll_drag(self, evt=None):
        """تایمر ۸ms در تمام مدت اسنیپ: قفل موسِ بازی را باز می‌کند، خط‌های راهنما/ناحیه را به‌روز می‌کند
        و اگر hook نصب نشده باشد با GetAsyncKeyState کلیک را تشخیص می‌دهد."""
        if not self.active:
            if self._drag_timer.IsRunning():
                self._drag_timer.Stop()
            return
        try:
            user32.ClipCursor(None)          # بازی هر فریم موس را قفل می‌کند؛ ما هر ۸ms آزاد می‌کنیم
        except Exception:
            pass
        pos = self._local_cursor()
        if self.start is None:
            if not self.grab.active and self._left_button_down():
                self._on_down(None)
            self._refresh_cross(pos)
            return
        if pos != self.cur:
            self.cur = pos
            self._refresh_sel()
        if not self.grab.active and not self._left_button_down():
            self._finish_selection(pos)

    def _refresh_cross(self, pos):
        if self._cross_last == (pos.x, pos.y):
            return
        gw, gh = self.geom[2], self.geom[3]
        rects = [wx.Rect(0, pos.y - 9, gw, 18), wx.Rect(pos.x - 9, 0, 18, gh)]
        if self._cross_last is not None:
            ox, oy = self._cross_last
            rects += [wx.Rect(0, oy - 9, gw, 18), wx.Rect(ox - 9, 0, 18, gh)]
        self._cross_last = (pos.x, pos.y)
        for r in rects:
            self.Refresh(False, r)

    def _on_up(self, evt):
        if self.start is not None:
            self._finish_selection(self._local_cursor())

    def _finish_selection(self, pos=None):
        if self.start is None or not self.active:
            return
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


        if self.active and not self._drag_timer.IsRunning():
            self._drag_timer.Start(8)
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
        self.grab.stop()                 # مهم: موس سیستم دوباره آزاد شود
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
        if getattr(self, "_owner", None):
            set_owner(self, None)        # owner را آزاد کن تا اگر بازی بسته شد پنجره‌ی ما هم نابود نشود
            self._owner = None
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
        self.bounds = None             # محدوده‌ی مانیتور خروجی (x, y, w, h) یا None
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


    def _place(self, x, y, w, h, bounds=None):
        vx, vy, vw, vh = bounds or virtual_rect()
        w, h = max(40, min(int(w), vw)), max(30, min(int(h), vh))
        x = max(vx, min(int(x), vx + vw - w))
        y = max(vy, min(int(y), vy + vh - h))
        self.rect = [x, y, w, h]
        place_top(self, x, y, w, h)

    def _ensure_top(self):
        if not self._top_on:
            self._top_on = True
            self._later("top", 150, self._top_tick)

    def _top_tick(self):
        if self.mode == "hidden":
            self._top_on = False
            return
        raise_top(self)
        self._later("top", 150, self._top_tick)

    def show_busy(self, anchor):
        self.anchor = anchor
        self._ensure_top()
        ax, ay, aw, ah = anchor
        self.mode, self.status, self.dots = "busy", "در حال ترجمه", 0
        self.src = self.bmp = None
        self._stop("auto")
        self._place(ax, ay, max(aw, 240), max(ah, 56), self.bounds)
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
        self._place(ax, ay, max(aw, 340), 64, self.bounds)
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
        self._place(ax, ay, w, h, self.bounds)
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
        was_busy = self.mode == "busy"
        self.mode = "hidden"
        if was_busy:
            try:
                self.app.cancel_translation()      # بستن در حین ترجمه = لغو ترجمه
            except Exception:
                pass
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
            p = os.path.join(d, "%s_%03d.png" % (time.strftime("ESHTranslator_%Y%m%d_%H%M%S"), ms))
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





# ═══════════════════════════════════════════════════════════════════════════
#  موتورهای ترجمه: توکن امن (DPAPI)، هوش مصنوعی (OpenAI/Gemini/OpenRouter)، آفلاین
# ═══════════════════════════════════════════════════════════════════════════

class EngineError(Exception):
    """خطایی که پیامش مستقیماً به کاربر نشان داده می‌شود.
    kind == "net" یعنی مشکل شبکه (برای تست خودکار اتصال)؛ code = کد HTTP در صورت وجود."""
    kind = ""
    code = 0


# ── ذخیره‌ی امن توکن با Windows DPAPI (فقط روی همین حساب ویندوز قابل خواندن است) ──
class _DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", ctypes.wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]


_crypt32 = ctypes.windll.crypt32
_crypt32.CryptProtectData.argtypes = [
    ctypes.POINTER(_DATA_BLOB), ctypes.c_wchar_p, ctypes.POINTER(_DATA_BLOB),
    ctypes.c_void_p, ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.POINTER(_DATA_BLOB)]
_crypt32.CryptProtectData.restype = ctypes.wintypes.BOOL
_crypt32.CryptUnprotectData.argtypes = [
    ctypes.POINTER(_DATA_BLOB), ctypes.c_void_p, ctypes.POINTER(_DATA_BLOB),
    ctypes.c_void_p, ctypes.c_void_p, ctypes.wintypes.DWORD, ctypes.POINTER(_DATA_BLOB)]
_crypt32.CryptUnprotectData.restype = ctypes.wintypes.BOOL
_k32_free = ctypes.windll.kernel32.LocalFree
_k32_free.argtypes = [ctypes.c_void_p]
_k32_free.restype = ctypes.c_void_p
_CRYPTPROTECT_UI_FORBIDDEN = 0x1


def _blob_in(data):
    buf = ctypes.create_string_buffer(data, len(data))
    return _DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char))), buf


def _blob_out(blob):
    try:
        return ctypes.string_at(blob.pbData, blob.cbData)
    finally:
        _k32_free(ctypes.cast(blob.pbData, ctypes.c_void_p))


def secret_encrypt(text):
    """متن → رشته‌ی base64 رمزگذاری‌شده؛ در صورت خطا رشته‌ی خالی."""
    try:
        data = str(text).encode("utf-8")
        if not data:
            return ""
        src, _keep = _blob_in(data)
        out = _DATA_BLOB()
        if not _crypt32.CryptProtectData(ctypes.byref(src), "ESHTranslator", None, None, None,
                                         _CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(out)):
            return ""
        return base64.b64encode(_blob_out(out)).decode("ascii")
    except Exception as exc:
        dbg("secret_encrypt failed: %s" % exc)
        return ""


def secret_decrypt(b64):
    try:
        raw = base64.b64decode(str(b64).encode("ascii"))
        if not raw:
            return ""
        src, _keep = _blob_in(raw)
        out = _DATA_BLOB()
        if not _crypt32.CryptUnprotectData(ctypes.byref(src), None, None, None, None,
                                           _CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(out)):
            return ""
        return _blob_out(out).decode("utf-8", "ignore")
    except Exception as exc:
        dbg("secret_decrypt failed: %s" % exc)
        return ""


# ── هوش مصنوعی ──
AI_PROVIDERS = (("openai", "OpenAI"), ("gemini", "Gemini"), ("openrouter", "OpenRouter"), ("custom", "سفارشی"))
AI_DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini-2.5-flash",
    "openrouter": "google/gemini-2.5-flash",
    "custom": "llama3.2-vision",
}
AI_HOSTS = {"openai": "https://api.openai.com", "gemini": "https://generativelanguage.googleapis.com",
            "openrouter": "https://openrouter.ai"}
# قیمت تقریبی هر یک میلیون توکن (دلار: ورودی، خروجی) — فقط برای تخمین؛ قیمت واقعی را از سایت سرویس ببینید
AI_PRICES = {"gpt-4o-mini": (0.15, 0.60), "gemini-2.5-flash": (0.30, 2.50),
             "google/gemini-2.5-flash": (0.30, 2.50)}
AI_PROMPT = (
    "You are an OCR and translation engine for screenshots of games and apps. "
    "Read all visible text in the image and translate it into fluent, natural Persian (Farsi, فارسی سلیس). "
    "The text may be horizontal or vertical (Japanese, Chinese and Korean games often use top-to-bottom, "
    "right-to-left columns) and may be split into several columns or speech bubbles; read it in the natural "
    "reading order of the source language. "
    "Output ONLY the Persian translation, keep the original order of lines and paragraphs, "
    "with no explanations or notes, and respond as fast as possible. "
    "If the image contains no readable text, output exactly: NO_TEXT")

AI_STYLES = (("casual", "محاوره‌ای"), ("formal", "رسمی"))
_AI_STYLE_TEXT = {
    "casual": "Style: casual, conversational Persian, the way people actually speak.",
    "formal": "Style: formal, polished standard Persian (written register).",
}


def build_ai_prompt(style="casual", game=""):
    """پرامپت پایه + سبک (با انتخاب کاربر خودکار عوض می‌شود) + نام بازی."""
    parts = [AI_PROMPT, _AI_STYLE_TEXT.get(style, _AI_STYLE_TEXT["casual"])]
    game = " ".join(str(game or "").split())[:60]
    if game:
        parts.append('This is for the game "%s". Use terminology that fits this game and keep proper names '
                     'of characters, items and places as they are.' % game)
    return " ".join(parts)


def _socks5_connect(proxy, host, port, timeout):
    """اتصال SOCKS5 (بدون کتابخانه‌ی اضافه). proxy = urlparse شده‌ی socks5://[user:pass@]host:port"""
    import socket
    from urllib.parse import unquote
    s = socket.create_connection((proxy.hostname, proxy.port or 1080), timeout)
    try:
        user, pw = unquote(proxy.username or ""), unquote(proxy.password or "")
        s.sendall(b"\x05\x02\x00\x02" if user else b"\x05\x01\x00")
        rep_ = s.recv(2)
        if len(rep_) < 2 or rep_[0] != 5:
            raise OSError("پاسخ SOCKS5 نامعتبر")
        if rep_[1] == 2:
            u, p_ = user.encode(), pw.encode()
            s.sendall(b"\x01" + bytes([len(u)]) + u + bytes([len(p_)]) + p_)
            if s.recv(2)[1:2] != b"\x00":
                raise OSError("نام کاربری/رمز پروکسی اشتباه است")
        elif rep_[1] != 0:
            raise OSError("روش احراز هویت SOCKS5 پشتیبانی نمی‌شود")
        h = host.encode("idna")
        s.sendall(b"\x05\x01\x00\x03" + bytes([len(h)]) + h + int(port).to_bytes(2, "big"))
        r = s.recv(4)
        if len(r) < 4 or r[1] != 0:
            raise OSError("پروکسی SOCKS5 اتصال را رد کرد")
        n = {1: 4, 4: 16}.get(r[3])
        if n is None:
            n = s.recv(1)[0]
        s.recv(n + 2)
        return s
    except Exception:
        s.close()
        raise


def _build_opener():
    import http.client
    import ssl
    import urllib.request
    from urllib.parse import urlparse
    mode, url = NET["mode"], NET["url"]
    if mode == "off":
        return urllib.request.build_opener(urllib.request.ProxyHandler({}))
    if mode == "custom" and url:
        pu = urlparse(url if "://" in url else "http://" + url)
        if (pu.scheme or "").startswith("socks"):
            class _SC(http.client.HTTPConnection):
                def connect(self):
                    self.sock = _socks5_connect(pu, self.host, self.port, self.timeout)

            class _SSC(http.client.HTTPSConnection):
                def connect(self):
                    raw = _socks5_connect(pu, self.host, self.port, self.timeout)
                    ctx = ssl.create_default_context()
                    self.sock = ctx.wrap_socket(raw, server_hostname=self.host)

            class _H(urllib.request.HTTPHandler):
                def http_open(self, req):
                    return self.do_open(_SC, req)

            class _HS(urllib.request.HTTPSHandler):
                def https_open(self, req):
                    return self.do_open(_SSC, req)

            return urllib.request.build_opener(urllib.request.ProxyHandler({}), _H, _HS)
        return urllib.request.build_opener(urllib.request.ProxyHandler({"http": url, "https": url}))
    return urllib.request.build_opener()            # system: رجیستری ویندوز / متغیرهای محیطی


def net_open(req, timeout=25):
    return _build_opener().open(req, timeout=timeout)


def _http_msg(code, detail=""):
    detail = " ".join(str(detail or "").split())[:90]
    if code in (400, 403, 451) and re.search(r"country|region|territor|location|not supported in|unsupported|embargo",
                                             detail, re.I):
        return "دسترسی از منطقه‌ی شما مجاز نیست (تحریم/محدودیت جغرافیایی)؛ VPN را روشن کنید یا سرویس دیگری بزنید"
    base = {
        400: "درخواست نامعتبر بود",
        401: "توکن اشتباه یا منقضی است",
        402: "اعتبار حساب تمام شده است",
        403: "توکن اجازه‌ی دسترسی ندارد (یا از این منطقه مسدود است)",
        404: "مدل یا آدرس پیدا نشد؛ نام مدل را بررسی کنید",
        408: "زمان پاسخ سرور تمام شد",
        429: "سهمیه یا محدودیت درخواست پر شده است",
        451: "دسترسی به‌خاطر محدودیت قانونی/تحریم مسدود است",
    }.get(code, "خطای سرور (%d)" % code)
    return "%s — %s" % (base, detail) if detail else base


def _net_reason_msg(reason):
    import socket
    import ssl
    if isinstance(reason, socket.gaierror):
        return "نام سرور پیدا نشد (DNS)؛ اینترنت یا VPN مشکل دارد."
    if isinstance(reason, ssl.SSLError) or "CERTIFICATE" in str(reason).upper():
        return "خطای SSL؛ ساعت سیستم، VPN یا پروکسی را بررسی کنید."
    if isinstance(reason, ConnectionRefusedError):
        return "اتصال رد شد؛ سرور یا پروکسی/VPN در دسترس نیست."
    if isinstance(reason, (socket.timeout, TimeoutError)):
        return "زمان اتصال تمام شد؛ احتمالاً اینترنت ضعیف یا مسدود است."
    return "اتصال به سرور برقرار نشد؛ اینترنت یا VPN را بررسی کنید."


def _is_local_url(url):
    import ipaddress
    from urllib.parse import urlparse
    h = (urlparse(url).hostname or "").lower()
    if h == "localhost" or h.endswith(".local"):
        return True
    try:
        ip = ipaddress.ip_address(h)
        return ip.is_private or ip.is_loopback
    except ValueError:
        return False


def _reachable(url, timeout=6):
    import urllib.error
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ESHTranslator/1.0"})
        if _is_local_url(url):
            urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req, timeout=timeout).close()
        else:
            net_open(req, timeout).close()
        return True
    except urllib.error.HTTPError:
        return True                      # سرور جواب داده؛ یعنی مسیر باز است
    except Exception:
        return False


def diagnose_connection(provider, base=None):
    """بعد از خطای شبکه: مشخص می‌کند مشکل از اینترنت است یا از دسترس‌نبودن خودِ سرویس (تحریم/فیلتر)."""
    if provider == "custom":
        if _reachable(str(base or "").strip()):
            return "سرور سفارشی در دسترس است؛ دوباره تلاش کنید."
        return "سرور سفارشی جواب نمی‌دهد؛ مطمئن شوید Ollama / LM Studio روشن است و آدرس و پورت درست‌اند."
    target = AI_HOSTS.get(provider)
    net_ok = _reachable("https://www.cloudflare.com/cdn-cgi/trace")
    tgt_ok = _reachable(target) if target else False
    if not net_ok and not tgt_ok:
        return "تشخیص: اینترنت (یا VPN/پروکسی) قطع است."
    if net_ok and not tgt_ok:
        return "تشخیص: اینترنت وصل است ولی سرویس در دسترس نیست؛ محدودیت/تحریم است — VPN یا پروکسی را روشن کنید."
    return "تشخیص: ارتباط الان برقرار است؛ مشکل موقت بود، دوباره تلاش کنید."


def ai_cost(model, tin, tout):
    pr = AI_PRICES.get(model)
    return None if not pr else (tin * pr[0] + tout * pr[1]) / 1e6


def fmt_tokens(n):
    n = int(n or 0)
    return "%.2fM" % (n / 1e6) if n >= 1000000 else ("%.1fK" % (n / 1e3) if n >= 1000 else str(n))


def _custom_base(base):
    b = str(base or "").strip().rstrip("/")
    if not re.match(r"^https?://\S+$", b, re.I):
        raise EngineError("آدرس سرور سفارشی معتبر نیست (باید با http:// یا https:// شروع شود).")
    return b


def _http_json(url, headers=None, body=None, timeout=25):
    import urllib.error
    import urllib.request
    h = {"User-Agent": "ESHTranslator/1.0"}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h, method="POST" if body is not None else "GET")
    try:
        if _is_local_url(url):                      # Ollama / LM Studio روی همین سیستم: بدون پروکسی و VPN
            _op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            _ctx = _op.open(req, timeout=timeout)
        else:
            _ctx = net_open(req, timeout)
        with _ctx as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            j = json.loads(exc.read().decode("utf-8", "replace"))
            err = j.get("error") if isinstance(j, dict) else None
            detail = err.get("message", "") if isinstance(err, dict) else (err if isinstance(err, str) else "")
        except Exception:
            pass
        err = EngineError(_http_msg(exc.code, detail))
        err.code = exc.code
        raise err
    except urllib.error.URLError as exc:
        err = EngineError(_net_reason_msg(exc.reason))
        err.kind = "net"
        raise err
    except OSError:
        err = EngineError("زمان پاسخ سرور تمام شد؛ دوباره تلاش کنید.")
        err.kind = "net"
        raise err
    try:
        return json.loads(raw.decode("utf-8", "replace") or "{}")
    except Exception:
        raise EngineError("پاسخ نامعتبر از سرور دریافت شد.")


def ai_check(provider, model, token, base=None):
    """اتصال و اعتبار توکن/مدل را می‌سنجد؛ پیام موفقیت را برمی‌گرداند یا EngineError می‌دهد."""
    from urllib.parse import quote
    model = (model or "").strip()
    if provider == "custom":
        b = _custom_base(base)
        hdr = {"Authorization": "Bearer " + token} if token else {}
        try:
            j = _http_json(b + "/models", hdr, timeout=15)
        except EngineError as exc:
            if exc.code == 404:
                return "سرور پاسخ می‌دهد (فهرست مدل‌ها پشتیبانی نمی‌شود)."
            raise
        ids = [str(m.get("id")) for m in (j.get("data") or []) if isinstance(m, dict)] if isinstance(j, dict) else []
        if ids and not any(i == model or i.startswith(model + ":") for i in ids):
            raise EngineError("سرور وصل است ولی مدل «%s» روی آن پیدا نشد." % model)
        return "اتصال برقرار است — سرور و مدل «%s» آماده‌اند." % model
    if provider == "openai":
        _http_json("https://api.openai.com/v1/models/" + quote(model, safe=""),
                   {"Authorization": "Bearer " + token}, timeout=20)
        return "اتصال برقرار است — توکن و مدل «%s» معتبرند." % model
    if provider == "gemini":
        name = model[7:] if model.startswith("models/") else model
        _http_json("https://generativelanguage.googleapis.com/v1beta/models/" + quote(name, safe=""),
                   {"x-goog-api-key": token}, timeout=20)
        return "اتصال برقرار است — توکن و مدل «%s» معتبرند." % name
    if provider == "openrouter":
        _http_json("https://openrouter.ai/api/v1/key", {"Authorization": "Bearer " + token}, timeout=20)
        listing = _http_json("https://openrouter.ai/api/v1/models", timeout=25)
        ids = {m.get("id") for m in (listing.get("data") or []) if isinstance(m, dict)}
        if ids and model not in ids:
            raise EngineError("توکن معتبر است، ولی مدل «%s» در OpenRouter پیدا نشد." % model)
        return "اتصال برقرار است — توکن و مدل «%s» معتبرند." % model
    raise EngineError("سرویس نامشخص است.")


def _jpeg_b64(img, quality=92):
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=quality)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def ai_translate(provider, model, token, img, prompt=None, base=None):
    """تصویر را با مدل بینایی به فارسی ترجمه می‌کند. خروجی: (متن, (توکن ورودی، توکن خروجی))."""
    from urllib.parse import quote
    b64 = _jpeg_b64(img)
    prompt = prompt or AI_PROMPT
    text = ""
    usage = None
    if provider in ("openai", "openrouter", "custom"):
        if provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
        elif provider == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
        else:
            url = _custom_base(base) + "/chat/completions"
        body = {"model": model, "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}]}]}
        hdr = {"Authorization": "Bearer " + token} if token else {}
        j = _http_json(url, hdr, body, timeout=180 if provider == "custom" else 75)
        try:
            u = j.get("usage") or {}
            usage = (int(u.get("prompt_tokens") or 0), int(u.get("completion_tokens") or 0))
        except Exception:
            usage = None
        try:
            content = j["choices"][0]["message"]["content"]
        except Exception:
            raise EngineError("پاسخی از مدل دریافت نشد.")
        if isinstance(content, list):
            content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
        text = str(content or "")
    elif provider == "gemini":
        name = model[7:] if model.startswith("models/") else model
        url = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % quote(name, safe="")
        body = {"contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
        j = _http_json(url, {"x-goog-api-key": token}, body, timeout=75)
        try:
            um = j.get("usageMetadata") or {}
            usage = (int(um.get("promptTokenCount") or 0),
                     int(um.get("candidatesTokenCount") or 0) + int(um.get("thoughtsTokenCount") or 0))
        except Exception:
            usage = None
        try:
            parts = j["candidates"][0]["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
        except Exception:
            raise EngineError("پاسخی از مدل دریافت نشد (ممکن است محتوا مسدود شده باشد).")
    else:
        raise EngineError("سرویس نامشخص است.")
    text = text.strip()
    if not text or text.upper().startswith("NO_TEXT"):
        raise EngineError("متنی در تصویر پیدا نشد.")
    return text, usage


# ── آفلاین: OCR با Tesseract + ترجمه با Argos ──
# (کد Tesseract, کد Argos, نام فارسی)
OCR_LANGS = (
    ("eng", "en", "انگلیسی — English"),
    ("jpn", "ja", "ژاپنی — Japanese"),
    ("kor", "ko", "کره‌ای — Korean"),
    ("chi_sim", "zh", "چینی ساده — Chinese"),
    ("rus", "ru", "روسی — Russian"),
    ("deu", "de", "آلمانی — German"),
    ("fra", "fr", "فرانسوی — French"),
    ("spa", "es", "اسپانیایی — Spanish"),
    ("ita", "it", "ایتالیایی — Italian"),
    ("por", "pt", "پرتغالی — Portuguese"),
    ("tur", "tr", "ترکی — Turkish"),
    ("ara", "ar", "عربی — Arabic"),
    ("pol", "pl", "لهستانی — Polish"),
    ("ukr", "uk", "اوکراینی — Ukrainian"),
)
OFFLINE_DIR = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), APP_DIR_NAME)
TESSDATA_DIR = os.path.join(OFFLINE_DIR, "tessdata")
TESSDATA_URL = "https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/%s.traineddata"


def ocr_lang_info(code):
    for item in OCR_LANGS:
        if item[0] == code:
            return item
    return OCR_LANGS[0]


def _no_window_flags():
    import subprocess
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def find_tesseract():
    p = shutil.which("tesseract")
    if p:
        return p
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"),
                 os.path.join(os.environ.get("LOCALAPPDATA") or "", "Programs")):
        if base:
            cand = os.path.join(base, "Tesseract-OCR", "tesseract.exe")
            if os.path.isfile(cand):
                return cand
    return None


def tess_model_installed(lang):
    p = os.path.join(TESSDATA_DIR, "%s.traineddata" % lang)
    try:
        return os.path.isfile(p) and os.path.getsize(p) > 200000       # فایل ناقص/خراب حساب نمی‌شود
    except Exception:
        return False


# ── ترجمه‌ی آفلاین: مدل NLLB-200 (Meta) با ctranslate2؛ مستقیم از هر زبان به فارسی (بدون واسطه‌ی انگلیسی) ──
# مجوز همه‌ی مدل‌های NLLB: CC-BY-NC 4.0 (فقط غیرتجاری). کوانتیزه‌کردن (int8) مجوز را عوض نمی‌کند.
# هر مدل: (نام محلی، حداقل حجم معتبر، مخزن، نسخه‌ی ثابت، نام فایل در مخزن، وزن در نوار پیشرفت)
NLLB_BASES = ("https://huggingface.co/", "https://hf-mirror.com/")
_R600, _V600 = "JustFrederik/nllb-200-distilled-600M-ct2-int8", "f84941bd43259bdf2e6e56ab779bc30b481df5a0"
_R13, _V13 = "JustFrederik/nllb-200-distilled-1.3B-ct2-int8", "934060f3dbc3517707faf26e11fda79350f99b14"
_R33, _V33 = "OpenNMT/nllb-200-3.3B-ct2-int8", "main"      # این مخزن فقط یک نسخه (28d998c) دارد
NLLB_REPO, NLLB_REV = _R600, _V600                          # (سازگاری با نام‌های قدیمی)
NLLB_MODELS = {
    "600m": {
        "label": "Light & fast — about 620 MB", "short": "سبک", "dir": "nllb600", "dl_mb": 623, "ram_gb": 1.2,
        "desc": "Default. Fastest and smallest. Best choice for Game Live translation.",
        "files": (("config.json", 50, _R600, _V600, "config.json", 0.005),
                  ("shared_vocabulary.txt", 1000000, _R600, _V600, "shared_vocabulary.txt", 0.015),
                  ("sentencepiece.bpe.model", 1000000, _R600, _V600, "sentencepiece.bpe.model", 0.02),
                  ("model.bin", 615000000, _R600, _V600, "model.bin", 0.96)),
    },
    "1.3b": {
        "label": "Balanced — about 1.4 GB", "short": "متعادل", "dir": "nllb1300", "dl_mb": 1400, "ram_gb": 2.0,
        "desc": "Better quality than Light; needs about 2 GB of RAM and is a little slower.",
        "files": (("config.json", 50, _R13, _V13, "config.json", 0.002),
                  ("shared_vocabulary.txt", 1000000, _R13, _V13, "shared_vocabulary.txt", 0.003),
                  ("sentencepiece.bpe.model", 1000000, _R13, _V13, "sentencepiece.bpe.model", 0.005),
                  ("model.bin", 1300000000, _R13, _V13, "model.bin", 0.99)),
    },
    "3.3b": {
        "label": "Strongest — about 3.4 GB", "short": "قوی‌ترین", "dir": "nllb3300", "dl_mb": 3400, "ram_gb": 4.2,
        "desc": "Best quality available; needs about 4 GB of RAM and is slow. Not recommended for Game Live translation.",
        "files": (("config.json", 50, _R33, _V33, "config.json", 0.001),
                  ("shared_vocabulary.json", 1000000, _R33, _V33, "shared_vocabulary.json", 0.002),
                  # توکنایزر NLLB برای همه‌ی اندازه‌ها یکی است؛ مخزن 3.3B فایل sentencepiece ندارد
                  ("sentencepiece.bpe.model", 1000000, _R13, _V13, "sentencepiece.bpe.model", 0.002),
                  ("model.bin", 3200000000, _R33, _V33, "model.bin", 0.995)),
    },
}
NLLB_MODEL_KEYS = ("600m", "1.3b", "3.3b")
_NLLB_SEL = {"key": "600m"}                                 # مدلِ انتخاب‌شده‌ی کاربر
OFFLINE_NLLB_DIR_DEFAULT = os.path.join(OFFLINE_DIR, "nllb600")
NLLB_DIR = OFFLINE_NLLB_DIR_DEFAULT                         # (سازگاری با نام قدیمی)
NLLB_TARGET = "pes_Arab"
NLLB_CODES = {"en": "eng_Latn", "ja": "jpn_Jpan", "ko": "kor_Hang", "zh": "zho_Hans", "ru": "rus_Cyrl",
              "de": "deu_Latn", "fr": "fra_Latn", "es": "spa_Latn", "it": "ita_Latn", "pt": "por_Latn",
              "tr": "tur_Latn", "ar": "arb_Arab", "pl": "pol_Latn", "uk": "ukr_Cyrl"}


def nllb_spec(key=None):
    return NLLB_MODELS.get(key or _NLLB_SEL["key"]) or NLLB_MODELS["600m"]


def nllb_dir(key=None):
    return os.path.join(OFFLINE_DIR, nllb_spec(key)["dir"])


def nllb_file_urls(key=None, base=None):
    """[(نام محلی، آدرس دانلود)] برای مدلِ انتخابی."""
    base = base or NLLB_BASES[0]
    return [(f[0], "%s%s/resolve/%s/%s" % (base, f[2], f[3], f[4])) for f in nllb_spec(key)["files"]]


def nllb_set_model(key, background=False):
    """مدل انتخابی را عوض می‌کند و مدل قبلیِ بارگذاری‌شده را از حافظه آزاد می‌کند.
    background=True: انتخاب آنی است و آزادسازی حافظه (که منتظر قفل بارگذاری می‌ماند) در ترد جدا انجام می‌شود."""
    if key in NLLB_MODELS and key != _NLLB_SEL["key"]:
        _NLLB_SEL["key"] = key
        if background:
            threading.Thread(target=nllb_unload_stale, daemon=True).start()
        else:
            nllb_unload()


def nllb_unload_stale():
    """فقط اگر مدلِ بارگذاری‌شده با مدل انتخابی فرق دارد آن را آزاد می‌کند (امن در ترد پس‌زمینه)."""
    with _NLLB_LOCK:
        if _NLLB["tr"] is not None and _NLLB["key"] != _NLLB_SEL["key"]:
            _NLLB["tr"] = _NLLB["sp"] = _NLLB["key"] = None
    try:
        import gc
        gc.collect()
    except Exception:
        pass


_ASCII_LINKS = {}


def _ascii_junction(dir_path):
    """برای پوشه‌ای با مسیر فارسی، یک Junction با مسیر ASCII می‌سازد (بدون نیاز به ادمین).
    وقتی نام‌های کوتاه ۸.۳ در ویندوز خاموش باشند، تنها راهی است که Tesseract و ctranslate2 مسیر را می‌خوانند."""
    import subprocess
    try:
        key = os.path.normcase(os.path.abspath(dir_path))
        hit = _ASCII_LINKS.get(key)
        if hit and os.path.isdir(hit):
            return hit
        tag = hashlib.md5(key.encode("utf-8")).hexdigest()[:10]
        bases = [os.environ.get("PUBLIC"), os.environ.get("ProgramData"),
                 (os.environ.get("SystemDrive") or "C:") + "\\"]
        for base in bases:
            if not base:
                continue
            try:
                base.encode("ascii")
            except UnicodeEncodeError:
                continue
            link = os.path.join(base, APP_DIR_NAME + "_links", tag)
            try:
                os.makedirs(os.path.dirname(link), exist_ok=True)
                if not os.path.isdir(link):
                    subprocess.run(["cmd", "/c", "mklink", "/J", link, os.path.abspath(dir_path)],
                                   capture_output=True, timeout=20, creationflags=_no_window_flags(),
                                   stdin=subprocess.DEVNULL)
                if os.path.isdir(link):
                    _ASCII_LINKS[key] = link
                    return link
            except Exception:
                continue
    except Exception as exc:
        dbg("ascii junction failed: %r" % (exc,))
    return None


def _ascii_path(p):
    """مسیرهای فارسی/غیر‌ASCII (نام کاربریِ فارسی) را به مسیر ASCII تبدیل می‌کند؛ ctranslate2 و tesseract با آن‌ها مشکل دارند.
    اول نام کوتاه ۸.۳، اگر نبود Junction."""
    try:
        p.encode("ascii")
        return p
    except UnicodeEncodeError:
        pass
    try:
        buf = ctypes.create_unicode_buffer(1024)
        n = ctypes.windll.kernel32.GetShortPathNameW(p, buf, 1024)
        if 0 < n < 1024:
            try:
                buf.value.encode("ascii")
                return buf.value
            except UnicodeEncodeError:
                pass
    except Exception:
        pass
    try:
        if os.path.isdir(p):
            j = _ascii_junction(p)
            if j:
                return j
        else:
            d, base = os.path.split(p)
            if d and os.path.isdir(d):
                j = _ascii_junction(d)
                if j:
                    return os.path.join(j, base)
    except Exception:
        pass
    return p


def nllb_installed(key=None):
    d = nllb_dir(key)
    try:
        return all(os.path.isfile(os.path.join(d, f[0])) and os.path.getsize(os.path.join(d, f[0])) >= f[1]
                   for f in nllb_spec(key)["files"])
    except Exception:
        return False


def _mem_status():
    """(کل RAM، RAM آزاد) به گیگابایت؛ (None, None) اگر خوانده نشد."""
    try:
        class _MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        ms = _MS()
        ms.dwLength = ctypes.sizeof(_MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms)):
            return ms.ullTotalPhys / 1e9, ms.ullAvailPhys / 1e9
    except Exception:
        pass
    return None, None


def argos_lib_available():
    """(نام قدیمی) یعنی ctranslate2 و sentencepiece در دسترس‌اند."""
    import importlib.util
    _activate_pylibs()
    try:
        return all(importlib.util.find_spec(m) is not None for m in ("ctranslate2", "sentencepiece"))
    except Exception:
        return False


def argos_status(src):
    """'ok' | 'missing' | 'nolib' (نام قدیمی؛ وضعیت مدل ترجمه‌ی آفلاین)."""
    if not argos_lib_available():
        return "nolib"
    return "ok" if (nllb_installed() and src in NLLB_CODES) else "missing"


class _SimpleSBD:
    """جمله‌بندِ ساده‌ی آفلاین (نقطه، علامت سؤال و تعجب)."""

    def split_sentences(self, text):
        parts = re.split(r"(?<=[.!?…。！？])\s+", (text or "").strip())
        return [p for p in parts if p.strip()] or [text]


_NLLB = {"tr": None, "sp": None, "key": None}
_NLLB_LOCK = threading.Lock()


def nllb_unload():
    """مدل بارگذاری‌شده را از حافظه خارج می‌کند (هنگام عوض‌کردن مدل)."""
    with _NLLB_LOCK:
        _NLLB["tr"] = _NLLB["sp"] = _NLLB["key"] = None
    try:
        import gc
        gc.collect()
    except Exception:
        pass


def _nllb_load():
    with _NLLB_LOCK:
        key = _NLLB_SEL["key"]
        if _NLLB["tr"] is not None and _NLLB["key"] != key:
            _NLLB["tr"] = _NLLB["sp"] = _NLLB["key"] = None          # مدل عوض شده؛ قبلی رها می‌شود
        if _NLLB["tr"] is None:
            spec = nllb_spec(key)
            _activate_pylibs()
            try:
                import ctranslate2
                import sentencepiece as spm
            except Exception:
                raise EngineError("کتابخانه‌ی ترجمه‌ی آفلاین نصب نیست؛ در صفحه‌ی آفلاین «دانلود مدل‌ها» را بزنید "
                                  "(نصب خودکار انجام می‌شود).")
            if not nllb_installed(key):
                raise EngineError("مدل ترجمه‌ی آفلاین «%s» نصب نیست؛ در صفحه‌ی آفلاین «دانلود مدل‌ها» را بزنید."
                                  % spec["short"])
            _tot, avail = _mem_status()
            if avail is not None and avail < spec["ram_gb"] * 0.85:
                raise EngineError("حافظه‌ی آزاد کافی نیست (%.1f گیگابایت آزاد؛ مدل «%s» حدود %.1f گیگابایت می‌خواهد). "
                                  "برنامه‌های دیگر را ببندید یا مدل سبک‌تری انتخاب کنید."
                                  % (avail, spec["short"], spec["ram_gb"]))
            d = nllb_dir(key)
            try:
                tr = ctranslate2.Translator(_ascii_path(d), device="cpu", compute_type="int8",
                                            intra_threads=max(2, min(8, os.cpu_count() or 4)))
                sp = spm.SentencePieceProcessor()
                sp.Load(_ascii_path(os.path.join(d, "sentencepiece.bpe.model")))
            except Exception as exc:
                dbg("nllb load failed (%s): %r" % (key, exc))
                raise EngineError("بارگذاری مدل ترجمه ناموفق بود: %s" % exc)
            _NLLB["tr"], _NLLB["sp"], _NLLB["key"] = tr, sp, key
        return _NLLB["tr"], _NLLB["sp"]


def _nllb_translate(text, src, fast=False):
    """ترجمه‌ی جمله‌به‌جمله‌ی متن (هر خط جدا، هر جمله جدا) به فارسی با NLLB.
    fast=True (ترجمه‌ی زنده): beam کوچک‌تر و خروجی کوتاه‌تر برای تأخیر کمتر."""
    scode = NLLB_CODES.get(src)
    if not scode:
        raise EngineError("این زبان برای ترجمه‌ی آفلاین پشتیبانی نمی‌شود.")
    tr, sp = _nllb_load()
    units = []                                           # (شماره‌ی خط، جمله)
    for li, ln in enumerate(re.split(r"\r?\n", text or "")):
        ln = " ".join(ln.split())
        if ln:
            for s in _SimpleSBD().split_sentences(ln):
                if s.strip():
                    units.append((li, s.strip()))
    if not units:
        return ""
    batch = [[scode] + sp.encode(s, out_type=str)[:300] + ["</s>"] for _li, s in units]
    res = tr.translate_batch(batch, target_prefix=[[NLLB_TARGET]] * len(batch),
                             beam_size=2 if fast else 5,
                             max_decoding_length=200 if fast else 360,
                             repetition_penalty=1.1, max_batch_size=16)
    lines = {}
    for (li, _s), r in zip(units, res):
        toks = list(r.hypotheses[0])
        if toks and toks[0] == NLLB_TARGET:
            toks = toks[1:]
        fa = sp.decode(toks).strip()
        if fa:
            lines.setdefault(li, []).append(fa)
    return "\n".join(" ".join(lines[k]) for k in sorted(lines))


def _argos_translate(text, src):                         # (نام قدیمی؛ همه‌ی فراخوانی‌ها همین‌جا می‌آیند)
    return _nllb_translate(text, src)


def _download_nllb(cb, ctl=None, key=None):
    """دانلود مدلِ ترجمه‌ی انتخابی (۶۲۰ مگابایت تا ۳٫۴ گیگابایت) با توقف/ادامه؛ اگر huggingface.co بسته بود از آینه‌اش."""
    key = key or _NLLB_SEL["key"]
    spec = nllb_spec(key)
    d = nllb_dir(key)
    os.makedirs(d, exist_ok=True)
    need = 0
    for name, mn, _repo, _rev, _remote, _w in spec["files"]:
        p = os.path.join(d, name)
        if not (os.path.isfile(p) and os.path.getsize(p) >= mn):
            need += mn
    try:
        free = shutil.disk_usage(d).free
    except Exception:
        free = None
    if free is not None and need and free < need * 1.1 + 150 * 1024 * 1024:
        raise EngineError("فضای خالی دیسک کافی نیست (%.1f گیگابایت آزاد؛ حدود %.1f گیگابایت لازم است)."
                          % (free / 1e9, (need * 1.1 + 150 * 1024 * 1024) / 1e9))
    done_w = 0.0
    for name, mn, repo, rev, remote, w in spec["files"]:
        dest = os.path.join(d, name)
        if os.path.isfile(dest) and os.path.getsize(dest) >= mn:
            done_w += w
            continue
        last = None
        for bi, base in enumerate(NLLB_BASES):
            url = "%s%s/resolve/%s/%s" % (base, repo, rev, remote)

            spd = {"t": time.time(), "b": None, "v": 0.0}

            def _prog(dn, t, w=w, done_w=done_w, name=name, spd=spd):
                f = (dn / float(t)) if t else 0.0
                now = time.time()
                if spd["b"] is None:
                    spd["b"] = dn
                elif now - spd["t"] >= 1.0:
                    inst = (dn - spd["b"]) / (now - spd["t"]) / (1024.0 * 1024.0)
                    spd["v"] = inst if not spd["v"] else (0.6 * spd["v"] + 0.4 * inst)
                    spd["t"], spd["b"] = now, dn
                extra = ("  •  %.1f MB/s" % spd["v"]) if spd["v"] > 0 else ""
                cb(done_w + w * f, "دانلود مدل ترجمه — %s (%s)… %s از %s%s"
                   % (spec["short"], name, fmt_mb(dn), fmt_mb(t) if t else "؟", extra))

            try:
                if bi > 0:
                    for _ext in (".part", ".part.json"):
                        try:
                            os.remove(dest + _ext)         # آینه‌ی دیگر: از اول (تا فایل ترکیبی خراب نشود)
                        except Exception:
                            pass
                _download_file(url, dest, _prog, ctl, expect=mn)
                last = None
                break
            except DownloadPaused:
                raise
            except Exception as exc:
                last = exc
                dbg("nllb download %s failed: %r" % (base, exc))
        if last is not None:
            raise EngineError("دانلود مدل ترجمه ممکن نشد (%s). اگر huggingface.co بسته است، VPN/پروکسی را در «تنظیمات شبکه» بررسی کنید." % last)
        done_w += w


class CancelToken:
    """لغوِ ترجمه: Tesseract واقعاً کشته می‌شود؛ درخواست شبکه‌ی AI رها می‌شود و نتیجه‌اش نادیده گرفته می‌شود."""

    def __init__(self):
        self.event = threading.Event()
        self.proc = None

    @property
    def cancelled(self):
        return self.event.is_set()

    def cancel(self):
        self.event.set()
        p = self.proc
        if p is not None:
            try:
                p.kill()
            except Exception:
                pass


def _otsu_threshold(hist):
    total = sum(hist)
    if not total:
        return 128
    sum_all = sum(i * c for i, c in enumerate(hist))
    sum_b = w_b = 0
    best, thr = -1.0, 128
    for i in range(256):
        w_b += hist[i]
        if not w_b:
            continue
        w_f = total - w_b
        if not w_f:
            break
        sum_b += i * hist[i]
        m_b, m_f = sum_b / w_b, (sum_all - sum_b) / w_f
        var = w_b * w_f * (m_b - m_f) ** 2
        if var > best:
            best, thr = var, i
    return thr


_HDR_CACHE = {"t": 0.0, "v": False}
_HDR_GAMMA = 1.0                         # >1 فقط وقتی مانیتور HDR است (توسط برنامه تنظیم می‌شود)


class _DCHdr(ctypes.Structure):
    _fields_ = [("type", ctypes.c_uint), ("size", ctypes.c_uint), ("alo", ctypes.c_uint),
                ("ahi", ctypes.c_int), ("id", ctypes.c_uint)]


class _DCAdv(ctypes.Structure):
    _fields_ = [("hdr", _DCHdr), ("value", ctypes.c_uint), ("enc", ctypes.c_uint), ("bpc", ctypes.c_uint)]


def hdr_active(max_age=8.0):
    """آیا حداقل یک مانیتور فعال در حالت HDR (Advanced Color) است؟ با DisplayConfig؛ نتیجه چند ثانیه کش می‌شود."""
    now = time.time()
    if now - _HDR_CACHE["t"] < max_age:
        return _HDR_CACHE["v"]
    res = False
    try:
        import struct
        u = ctypes.windll.user32
        npth, nmod = ctypes.c_uint32(), ctypes.c_uint32()
        if u.GetDisplayConfigBufferSizes(2, ctypes.byref(npth), ctypes.byref(nmod)) == 0 and npth.value:
            paths = (ctypes.c_ubyte * (72 * npth.value))()
            modes = (ctypes.c_ubyte * (64 * max(1, nmod.value)))()
            if u.QueryDisplayConfig(2, ctypes.byref(npth), paths, ctypes.byref(nmod), modes, None) == 0:
                for i in range(npth.value):
                    off = 72 * i + 20                          # targetInfo: adapterId(8) + id(4)
                    lo, hi, tid = struct.unpack("<IiI", bytes(paths[off:off + 12]))
                    info = _DCAdv()
                    info.hdr.type = 9                          # GET_ADVANCED_COLOR_INFO
                    info.hdr.size = ctypes.sizeof(_DCAdv)
                    info.hdr.alo, info.hdr.ahi, info.hdr.id = lo, hi, tid
                    if u.DisplayConfigGetDeviceInfo(ctypes.byref(info)) == 0 and (info.value & 1) and (info.value & 2):
                        res = True
                        break
    except Exception as exc:
        dbg("hdr_active: %r" % (exc,))
    _HDR_CACHE["t"], _HDR_CACHE["v"] = now, res
    return res


def ocr_preprocess(img, binarize=False, flip=False, scale=None):
    """پیش‌پردازش برای OCR: خاکستری، بزرگ‌نمایی، افزایش کنتراست، معکوس‌کردنِ زمینه‌ی تیره و (اختیاری) باینری."""
    from PIL import ImageFilter, ImageOps
    g = ImageOps.grayscale(img.convert("RGB"))
    if _HDR_GAMMA and abs(_HDR_GAMMA - 1.0) > 0.01:             # HDR: تصویرِ شسته و روشن را تیره می‌کند تا حروف جدا شوند
        _lut = [min(255, int(255.0 * ((i / 255.0) ** _HDR_GAMMA) + 0.5)) for i in range(256)]
        g = g.point(_lut)
    sc = scale if scale else (2 if max(g.size) < 1000 else 1)
    if sc > 1:
        sc = min(sc, max(1.0, 4000.0 / float(max(g.size))))
        g = g.resize((max(1, int(g.width * sc)), max(1, int(g.height * sc))), Image.LANCZOS)
    g = ImageOps.autocontrast(g, cutoff=1)
    hist = g.histogram()
    mean = sum(i * c for i, c in enumerate(hist)) / float(max(1, sum(hist)))
    inv = mean < 110                                # متن روشن روی زمینه‌ی تیره؛ Tesseract عکس معکوس را بهتر می‌خواند
    if flip:
        inv = not inv
    if inv:
        g = ImageOps.invert(g)
        hist = g.histogram()
    g = g.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=3))
    if binarize:
        thr = _otsu_threshold(g.histogram())
        g = g.point(lambda v: 255 if v > thr else 0)
    return g


VERT_LANGS = ("jpn", "kor", "chi_sim")          # این زبان‌ها مدل متن عمودی (<lang>_vert) دارند


def _has_columns(img):
    """آیا تصویر یک شیار خالیِ عمودی بین دو بلوک متن دارد؟ (متن چندستونه)"""
    from PIL import Image
    g = img.convert("L").resize((160, 60), Image.BILINEAR)
    px = list(g.getdata())
    bg = sorted(px)[len(px) // 2]
    ink = [sum(1 for y in range(60) if abs(px[y * 160 + x] - bg) > 45) for x in range(160)]
    cols = [i for i, v in enumerate(ink) if v > 1]
    if len(cols) < 30:
        return False
    first, last = cols[0], cols[-1]
    run = best = best_end = 0
    for x in range(first, last + 1):
        if ink[x] <= 1:
            run += 1
            if run > best:
                best, best_end = run, x
        else:
            run = 0
    return best >= 7 and (best_end - best - first) >= 24 and (last - best_end) >= 24


def _ocr_mode(img, lang):
    """(مدل OCR، حالت psm): عمودی → <lang>_vert با psm 5 ؛ چندستونه → psm 3 ؛ وگرنه psm 6."""
    try:
        if lang in VERT_LANGS and img.height > img.width * 1.15 and tess_model_installed(lang + "_vert"):
            return lang + "_vert", "5"
        if _has_columns(img):
            return lang, "3"
    except Exception as exc:
        dbg("ocr mode detect failed: %r" % (exc,))
    return lang, "6"


def _tess_read(exe, work, lang, tmp, cancel, tag, extra=(), psm="6"):
    import subprocess
    png = os.path.join(tmp, "in_%s.png" % tag)
    work.save(png, format="PNG")
    try:
        proc = subprocess.Popen(
            [exe, _ascii_path(png), "stdout", "-l", lang, "--tessdata-dir", _ascii_path(TESSDATA_DIR),
             "--psm", str(psm)] + list(extra),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=_no_window_flags())
    except OSError as exc:
        raise EngineError("اجرای Tesseract ممکن نشد: %s" % exc)
    if cancel is not None:
        cancel.proc = proc
    try:
        out, _err = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        raise EngineError("OCR بیش از حد طول کشید.")
    finally:
        if cancel is not None:
            cancel.proc = None
    if cancel is not None and cancel.cancelled:
        raise EngineError("ترجمه لغو شد.")
    err_txt = (_err or b"").decode("utf-8", "ignore")
    if ("Failed loading language" in err_txt or "Error opening data file" in err_txt
            or "Could not initialize tesseract" in err_txt):
        dbg("tesseract model error (%s): %s" % (lang, err_txt[:200].replace("\n", " | ")))
        try:
            os.remove(os.path.join(TESSDATA_DIR, "%s.traineddata" % lang.split("+")[0]))   # تا دوباره دانلود شود
        except Exception:
            pass
        raise EngineError("مدل OCR خراب بود و حذف شد؛ «دانلود مدل‌ها» را بزنید تا دوباره دریافت شود.")
    return out.decode("utf-8", "ignore").strip()


def _ocr_attempts(psm):
    """چند تلاش پشت‌سرهم تا اولین متنِ پیدا‌شده: عادی، باینری، معکوسِ حالت خودکار، و متن پراکنده (psm 11)."""
    seq = [("a", {}, psm), ("b", {"binarize": True}, psm), ("c", {"flip": True}, psm),
           ("d", {"scale": 3}, "11"), ("e", {"scale": 3, "binarize": True}, "11")]
    out, seen = [], set()
    for t in seq:
        key = (tuple(sorted(t[1].items())), t[2])
        if key not in seen:
            seen.add(key)
            out.append(t)
    return out


def offline_translate(img, lang, cancel=None):
    exe = find_tesseract()
    if not exe:
        raise EngineError("Tesseract نصب نیست؛ در صفحه‌ی آفلاین «دانلود مدل‌ها» را بزنید.")
    if not tess_model_installed(lang):
        raise EngineError("مدل OCR زبان انتخابی نصب نیست؛ در صفحه‌ی آفلاین «دانلود مدل‌ها» را بزنید.")
    src = ocr_lang_info(lang)[1]
    tmp = tempfile.mkdtemp(prefix="eshocr_")
    try:
        mlang, psm = _ocr_mode(img, lang)
        text = ""
        for tag, kw, p_ in _ocr_attempts(psm):
            text = _tess_read(exe, ocr_preprocess(img, **kw), mlang, tmp, cancel, tag, psm=p_)
            if text and re.search(r"\w", text):
                break
            text = ""
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not text:
        dbg("ocr found nothing: img=%dx%d lang=%s psm=%s" % (img.width, img.height, mlang, psm))
        raise EngineError("متنی در تصویر پیدا نشد.")
    paragraphs = [" ".join(p.split()) for p in re.split(r"\n\s*\n", text)]
    out = []
    for p_ in paragraphs:
        if cancel is not None and cancel.cancelled:
            raise EngineError("ترجمه لغو شد.")
        if p_:
            out.append(_argos_translate(p_, src))
    result = "\n".join(s_.strip() for s_ in out if s_ and s_.strip())
    if not result:
        raise EngineError("ترجمه‌ای تولید نشد.")
    return result


def _parse_tsv_paragraphs(tsv, scale):
    """خروجی TSV تسراکت → [(bbox در مختصات عکس اصلی، متن)] به‌ازای هر پاراگراف."""
    rows = tsv.splitlines()
    paras = {}
    for ln in rows[1:]:
        c = ln.split("\t")
        if len(c) < 12 or c[0] != "5":
            continue
        try:
            conf = float(c[10])
        except ValueError:
            continue
        word = c[11].strip()
        if conf < 30 or not word:
            continue
        key = (int(c[2]), int(c[3]))
        x, y, w, h = int(c[6]), int(c[7]), int(c[8]), int(c[9])
        d = paras.setdefault(key, {"lines": {}, "box": [10 ** 9, 10 ** 9, -1, -1]})
        d["lines"].setdefault(int(c[4]), []).append(word)
        b = d["box"]
        b[0], b[1], b[2], b[3] = min(b[0], x), min(b[1], y), max(b[2], x + w), max(b[3], y + h)
    out = []
    for key in sorted(paras):
        d = paras[key]
        text = " ".join(" ".join(d["lines"][k]) for k in sorted(d["lines"]))
        b = d["box"]
        box = tuple(int(round(v / scale)) for v in b)
        if text.strip() and box[2] > box[0] and box[3] > box[1]:
            out.append((box, text.strip()))
    return out


def _sample_colors(img, box):
    """رنگ پس‌زمینه (غالب) و رنگ متن (دورترین رنگ از پس‌زمینه) داخل کادر."""
    x0, y0, x1, y1 = box
    crop = img.convert("RGB").crop((max(0, x0), max(0, y0), min(img.width, x1), min(img.height, y1)))
    if crop.width < 1 or crop.height < 1:
        return (24, 26, 33), (245, 245, 248)
    if crop.width * crop.height > 40000:
        crop = crop.resize((max(1, crop.width // 3), max(1, crop.height // 3)))
    px = list(crop.getdata())
    bins = {}
    for r, g, b in px:
        bins.setdefault((r >> 4, g >> 4, b >> 4), []).append((r, g, b))
    big = max(bins.values(), key=len)
    bg = tuple(int(sum(c[i] for c in big) / len(big)) for i in range(3))
    far = sorted(px, key=lambda c: -sum((c[i] - bg[i]) ** 2 for i in range(3)))[:max(1, len(px) // 20)]
    fg = tuple(int(sum(c[i] for c in far) / len(far)) for i in range(3))
    lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    if abs(lum(fg) - lum(bg)) < 90:               # کنتراست کم: سیاه یا سفید
        fg = (0, 0, 0) if lum(bg) > 128 else (255, 255, 255)
    return bg, fg


def offline_regions(img, lang, cancel=None):
    """حالت «متن روی متن»: OCR با مختصات + ترجمه‌ی هر پاراگراف. خروجی: [{box, text, bg, fg}]."""
    exe = find_tesseract()
    if not exe:
        raise EngineError("Tesseract نصب نیست؛ در صفحه‌ی آفلاین «دانلود مدل‌ها» را بزنید.")
    if not tess_model_installed(lang):
        raise EngineError("مدل OCR زبان انتخابی نصب نیست؛ در صفحه‌ی آفلاین «دانلود مدل‌ها» را بزنید.")
    src = ocr_lang_info(lang)[1]
    tmp = tempfile.mkdtemp(prefix="eshocr_")
    try:
        paras = []
        mlang, psm = _ocr_mode(img, lang)
        for tag, kw, p_ in _ocr_attempts(psm):
            work = ocr_preprocess(img, **kw)
            scale = work.width / float(max(1, img.width))
            paras = _parse_tsv_paragraphs(_tess_read(exe, work, mlang, tmp, cancel, tag, ("tsv",), psm=p_), scale)
            if paras:
                break
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not paras:
        dbg("ocr(tsv) found nothing: img=%dx%d lang=%s psm=%s" % (img.width, img.height, mlang, psm))
        raise EngineError("متنی در تصویر پیدا نشد.")
    regions = []
    for box, text in paras:
        if cancel is not None and cancel.cancelled:
            raise EngineError("ترجمه لغو شد.")
        fa = (_argos_translate(" ".join(text.split()), src) or "").strip()
        if not fa:
            continue
        bg, fg = _sample_colors(img, box)
        regions.append({"box": box, "text": fa, "bg": bg, "fg": fg})
    if not regions:
        raise EngineError("ترجمه‌ای تولید نشد.")
    return regions


class DownloadPaused(Exception):
    """کاربر «توقف» را زده؛ فایل نیمه‌کاره (.part) نگه داشته می‌شود تا بعداً ادامه پیدا کند."""


class DownloadCtl:
    def __init__(self):
        self.pause = False


def remote_size(url, timeout=12):
    """حجم دقیق فایل از هدر Content-Length (بایت) یا None."""
    import urllib.request
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "ESHTranslator/1.0"})
        with net_open(req, timeout) as resp:
            n = int(resp.headers.get("Content-Length") or 0)
            if n:
                return n
    except Exception:
        pass
    try:                                       # HEAD روی بعضی CDNها مجاز نیست؛ با Range می‌پرسیم
        return _dl_probe(url, timeout)[1] or None
    except Exception:
        return None


def fmt_mb(n):
    return "%.1f MB" % (float(n) / (1024.0 * 1024.0))


_DL_UA = "ESHTranslator/1.0"
_DL_BLOCK = 4 * 1024 * 1024            # اندازه‌ی هر تکه (برای ادامه‌ی دقیق بعد از توقف)
_DL_CONNS = 8                          # تعداد اتصال همزمان برای فایل‌های بزرگ
_DL_MIN_SPLIT = 12 * 1024 * 1024       # زیر این حجم، یک اتصال کافی است
_DL_CHUNK = 256 * 1024


def _dl_probe(url, timeout=25):
    """(آدرس نهایی بعد از ریدایرکت، حجم کل، آیا Range پشتیبانی می‌شود). با GET و Range=0-0 تا با لینک‌های امضاشده‌ی CDN هم کار کند."""
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": _DL_UA, "Range": "bytes=0-0",
                                               "Accept-Encoding": "identity"})
    with net_open(req, timeout) as resp:
        final = resp.geturl() or url
        status = getattr(resp, "status", 200)
        m = re.match(r"\s*bytes\s+\d+-\d+/(\d+)", resp.headers.get("Content-Range") or "")
        if status == 206 and m:
            return final, int(m.group(1)), True
        return final, int(resp.headers.get("Content-Length") or 0), False


def _dl_load_meta(part, meta, total, nblocks):
    """پیشرفت قبلی هر تکه را می‌خواند؛ فایل .part قدیمیِ پشت‌سرهم (بدون متادیتا) را هم می‌فهمد."""
    done = {}
    if os.path.exists(part):
        ok = False
        try:
            with open(meta, "r", encoding="utf-8") as f:
                j = json.load(f)
            if int(j.get("total", -1)) == total and int(j.get("block", -1)) == _DL_BLOCK:
                done = {int(k): int(v) for k, v in (j.get("done") or {}).items()}
                ok = True
        except Exception:
            pass
        if not ok:
            if os.path.exists(meta):                  # متادیتای خراب/ناسازگار: از اول
                done = {}
                try:
                    os.remove(part)
                except Exception:
                    pass
            else:                                     # .part قدیمی: بایت‌های اول فایل پشت‌سرهم‌اند
                have = min(os.path.getsize(part), total)
                for i in range(nblocks):
                    st = i * _DL_BLOCK
                    d = max(0, min(min(_DL_BLOCK, total - st), have - st))
                    if d:
                        done[i] = d
    else:
        try:
            os.remove(meta)
        except Exception:
            pass
    return done


def _dl_save_meta(meta, total, done):
    try:
        tmp = meta + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"total": total, "block": _DL_BLOCK, "done": {str(k): v for k, v in done.items()}}, f)
        os.replace(tmp, meta)
    except Exception:
        pass


def _download_segmented(url, final, dest, total, on_prog, ctl):
    """دانلود چنداتصالی (۸ اتصال همزمان) با ادامه‌ی دقیق؛ روی لینک‌های کند/محدودشده چند برابر سریع‌تر از یک اتصال است."""
    import threading
    import urllib.error
    import urllib.request
    part = dest + ".part"
    meta = part + ".json"
    B = _DL_BLOCK
    nblocks = (total + B - 1) // B

    def blen(i):
        return min(B, total - i * B)

    done = _dl_load_meta(part, meta, total, nblocks)
    with open(part, "r+b" if os.path.exists(part) else "wb") as f:
        f.truncate(total)
    lock = threading.Lock()
    stop = threading.Event()
    pending = [i for i in range(nblocks) if done.get(i, 0) < blen(i)]
    state = {"url": final, "err": None, "bytes": sum(min(v, blen(i)) for i, v in done.items())}

    def worker():
        try:
            f = open(part, "r+b")
        except Exception as exc:
            with lock:
                state["err"] = state["err"] or exc
            stop.set()
            return
        try:
            while not stop.is_set():
                with lock:
                    if not pending:
                        return
                    i = pending.pop(0)
                start, size = i * B, blen(i)
                tries = 0
                while not stop.is_set():
                    d0 = done.get(i, 0)
                    if d0 >= size:
                        break
                    try:
                        req = urllib.request.Request(state["url"], headers={
                            "User-Agent": _DL_UA, "Accept-Encoding": "identity",
                            "Range": "bytes=%d-%d" % (start + d0, start + size - 1)})
                        with net_open(req, 30) as resp:
                            if getattr(resp, "status", 206) != 206:
                                raise IOError("Range")
                            f.seek(start + d0)
                            while not stop.is_set():
                                chunk = resp.read(_DL_CHUNK)
                                if not chunk:
                                    break
                                room = size - done.get(i, 0)
                                if len(chunk) > room:
                                    chunk = chunk[:room]
                                if not chunk:
                                    break
                                f.write(chunk)
                                f.flush()
                                with lock:
                                    done[i] = done.get(i, 0) + len(chunk)
                                    state["bytes"] += len(chunk)
                        if done.get(i, 0) >= size:
                            break
                        if not stop.is_set():
                            raise IOError("short block")
                    except Exception as exc:
                        if stop.is_set():
                            break
                        tries += 1
                        if isinstance(exc, urllib.error.HTTPError) and exc.code in (401, 403, 410):
                            try:                                  # لینک امضاشده‌ی CDN منقضی شده؛ دوباره می‌گیریم
                                state["url"] = _dl_probe(url, 25)[0]
                            except Exception:
                                pass
                        if tries >= 6:
                            with lock:
                                state["err"] = state["err"] or exc
                            stop.set()
                            return
                        time.sleep(min(8.0, 1.2 * tries))
        finally:
            try:
                f.close()
            except Exception:
                pass

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(max(1, min(_DL_CONNS, len(pending))))]
    for t in threads:
        t.start()
    paused = False
    last_save = time.time()
    try:
        while any(t.is_alive() for t in threads):
            if ctl is not None and ctl.pause:
                paused = True
                break
            if on_prog:
                on_prog(min(state["bytes"], total), total)
            if time.time() - last_save > 2.0:
                with lock:
                    snap = dict(done)
                _dl_save_meta(meta, total, snap)
                last_save = time.time()
            time.sleep(0.15)
    finally:
        stop.set()
        _deadline = time.time() + 4.0
        for t in threads:
            t.join(max(0.05, _deadline - time.time()))
        with lock:
            snap = dict(done)
        if paused or state["err"] is not None or any(snap.get(i, 0) < blen(i) for i in range(nblocks)):
            _dl_save_meta(meta, total, snap)
    if paused:
        raise DownloadPaused()
    if state["err"] is not None:
        exc = state["err"]
        if isinstance(exc, urllib.error.HTTPError):
            raise EngineError("دانلود ناموفق بود: خطای سرور (%d)" % exc.code)
        raise EngineError("دانلود قطع شد (%s)؛ «ادامه» را بزنید تا از همان‌جا ادامه پیدا کند." % exc)
    if any(snap.get(i, 0) < blen(i) for i in range(nblocks)):
        raise EngineError("دانلود کامل نشد؛ «ادامه» را بزنید تا از همان‌جا ادامه پیدا کند.")
    if on_prog:
        on_prog(total, total)
    os.replace(part, dest)
    try:
        os.remove(meta)
    except Exception:
        pass


def _download_file(url, dest, on_prog=None, ctl=None, expect=0):
    """دانلود سریع با قابلیت ادامه. on_prog(done_bytes, total_bytes)؛ توقف با ctl.pause → DownloadPaused.
    فایل‌های بزرگ (expect ≥ ۱۲ مگابایت) با چند اتصال همزمان گرفته می‌شوند؛ بقیه با یک اتصال و بافر بزرگ."""
    import urllib.error
    import urllib.request
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    part = dest + ".part"
    meta = part + ".json"
    if expect >= _DL_MIN_SPLIT:
        try:
            final, total, ranged = _dl_probe(url)
        except Exception as exc:
            dbg("dl probe failed: %r" % (exc,))
            final, total, ranged = url, 0, False
        if ranged and total >= _DL_MIN_SPLIT:
            _download_segmented(url, final, dest, total, on_prog, ctl)
            return
    if os.path.exists(meta):                          # از حالت چنداتصالی مانده بود ولی این بار Range نداریم
        for p in (part, meta):
            try:
                os.remove(p)
            except Exception:
                pass
    for attempt in (0, 1):
        have = os.path.getsize(part) if os.path.exists(part) else 0
        headers = {"User-Agent": _DL_UA, "Accept-Encoding": "identity"}
        if have:
            headers["Range"] = "bytes=%d-" % have
        try:
            req = urllib.request.Request(url, headers=headers)
            with net_open(req, 30) as resp:
                resumed = have > 0 and getattr(resp, "status", 200) == 206
                if have and not resumed:
                    have = 0                                  # سرور Range را نپذیرفت؛ از اول
                clen = int(resp.headers.get("Content-Length") or 0)
                total = (have + clen) if clen else 0
                done = have
                with open(part, "ab" if resumed else "wb", buffering=1 << 20) as f:
                    while True:
                        if ctl is not None and ctl.pause:
                            raise DownloadPaused()
                        chunk = resp.read(1 << 20)
                        if not chunk:
                            break
                        f.write(chunk)
                        done += len(chunk)
                        if on_prog:
                            on_prog(done, total)
            os.replace(part, dest)
            return
        except DownloadPaused:
            raise
        except urllib.error.HTTPError as exc:
            if exc.code == 416 and have and attempt == 0:      # فایل .part در واقع کامل است
                try:
                    os.replace(part, dest)
                    return
                except Exception:
                    pass
            raise EngineError("دانلود ناموفق بود: خطای سرور (%d)" % exc.code)
        except Exception as exc:                               # قطع شدن اینترنت: .part می‌ماند و «ادامه» ممکن است
            raise EngineError("دانلود قطع شد (%s)؛ «ادامه» را بزنید تا از همان‌جا ادامه پیدا کند." % exc)


def install_tesseract(cb):
    """نصب Tesseract بدون نیاز به winget: اول winget (اگر بود)، بعد دانلود مستقیم نصب‌کننده‌ی UB-Mannheim
    و نصب بی‌صدا در پوشه‌ی کاربر (ادمین لازم نیست)."""
    import subprocess
    if shutil.which("winget"):
        cb(0.02, "نصب Tesseract با winget …")
        try:
            subprocess.run(["winget", "install", "-e", "--id", "UB-Mannheim.TesseractOCR", "--silent",
                            "--accept-package-agreements", "--accept-source-agreements"],
                           capture_output=True, timeout=900, creationflags=_no_window_flags(),
                           stdin=subprocess.DEVNULL)
        except Exception as exc:
            dbg("winget tesseract failed: %s" % exc)
        if find_tesseract():
            return True
    base = "https://digi.bib.uni-mannheim.de/tesseract/"
    names = []
    try:
        import urllib.request
        req = urllib.request.Request(base, headers={"User-Agent": "Mozilla/5.0 42OCR"})
        with urllib.request.urlopen(req, timeout=40) as r:
            html = r.read().decode("utf-8", "replace")
        found = set(re.findall(r"tesseract-ocr-w64-setup-(\d+(?:\.\d+)+)\.exe", html))
        names = ["tesseract-ocr-w64-setup-%s.exe" % v for v in
                 sorted(found, key=lambda v: tuple(int(x) for x in v.split(".")), reverse=True)]
    except Exception as exc:
        dbg("tesseract index failed: %r" % (exc,))
    names.append("tesseract-ocr-w64-setup-5.5.0.20241111.exe")          # آخرین چاره
    dest = os.path.join(tempfile.gettempdir(), "esh_tesseract_setup.exe")
    ok, last = False, None
    for nm in names[:3]:
        try:
            cb(0.05, "دانلود نصب‌کننده‌ی Tesseract …")
            _fetch(base + nm, dest, lambda d, t: cb(0.05 + 0.60 * (d / float(t) if t else 0),
                                                      "دانلود Tesseract… %s از %s" % (fmt_mb(d), fmt_mb(t) if t else "؟")),
                   timeout=90, big=True)
            ok = True
            break
        except Exception as exc:
            last = exc
    if not ok:
        raise EngineError("دانلود Tesseract ناموفق بود (%s)" % (last,))
    target = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "Programs", "Tesseract-OCR")
    cb(0.70, "نصب Tesseract … (چند لحظه)")
    try:
        subprocess.call([dest, "/S", "/D=" + target], creationflags=_no_window_flags(), timeout=900,
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:
        dbg("tesseract setup run: %r" % (exc,))
    for _ in range(90):                                    # نصب‌کننده ممکن است زودتر برگردد؛ منتظر ظاهر شدن exe
        if find_tesseract():
            break
        time.sleep(1)
    try:
        os.remove(dest)
    except Exception:
        pass
    return bool(find_tesseract())


def download_offline_models(lang, cb, ctl=None):
    """مدل OCR، موتور Tesseract و مدل ترجمه‌ی NLLB را آماده می‌کند.
    cb(fraction, message) پیشرفت را گزارش می‌دهد. خروجی: پیام نهایی."""
    import importlib
    import subprocess
    src = ocr_lang_info(lang)[1]
    notes = []

    # ۱) مدل OCR
    if not tess_model_installed(lang):
        cb(0.02, "دانلود مدل OCR (%s)…" % lang)
        def _prog_ocr(done, total):
            f = (done / float(total)) if total else 0.0
            cb(0.02 + 0.30 * f, "دانلود مدل OCR… %s از %s" % (fmt_mb(done), fmt_mb(total) if total else "؟"))

        _download_file(TESSDATA_URL % lang, os.path.join(TESSDATA_DIR, "%s.traineddata" % lang),
                       _prog_ocr, ctl)

    # ۱-ب) مدل متن عمودی (ژاپنی / کره‌ای / چینی) — اختیاری؛ اگر دانلود نشد ترجمه‌ی افقی کار می‌کند
    if lang in VERT_LANGS and not tess_model_installed(lang + "_vert"):
        try:
            cb(0.33, "دانلود مدل متن عمودی…")
            _download_file(TESSDATA_URL % (lang + "_vert"),
                           os.path.join(TESSDATA_DIR, "%s_vert.traineddata" % lang), None, ctl)
        except DownloadPaused:
            raise
        except Exception as exc:
            dbg("vert model download failed: %r" % (exc,))
            notes.append("مدل متن عمودی دانلود نشد (متن افقی مشکلی ندارد)")

    # ۲) موتور Tesseract
    if not find_tesseract():
        try:
            install_tesseract(lambda f, m: cb(0.36 + 0.13 * f, m))
        except Exception as exc:
            dbg("install_tesseract failed: %r" % (exc,))
        if not find_tesseract():
            notes.append("Tesseract نصب نشد؛ آن را دستی از github.com/UB-Mannheim/tesseract نصب کنید")

    # ۳) ترجمه‌ی آفلاین: کتابخانه‌ی ctranslate2 + مدل NLLB (مستقیم به فارسی)
    cb(0.50, "آماده‌سازی ترجمه‌ی آفلاین…")
    try:
        ensure_argos_lib(lambda f, m: cb(0.50 + 0.06 * f, m))
    except Exception as exc:
        dbg("ensure lib failed: %r" % (exc,))
        notes.append("نصب خودکار کتابخانه‌ی ترجمه (ctranslate2) انجام نشد: %s" % exc)
    if src not in NLLB_CODES:
        notes.append("این زبان برای ترجمه‌ی آفلاین پشتیبانی نمی‌شود")
    elif not nllb_installed():
        try:
            _download_nllb(lambda f, m: cb(0.56 + 0.43 * f, m), ctl)
        except DownloadPaused:
            raise
        except Exception as exc:
            dbg("nllb models failed: %r" % (exc,))
            notes.append("دریافت مدل ترجمه ناموفق بود: %s" % exc)

    cb(1.0, "پایان")
    if notes:
        raise EngineError("بخشی انجام شد، ولی: " + " | ".join(notes))
    return "همه‌ی مدل‌ها آماده‌اند."


# ── تبدیل متن ترجمه‌شده به تصویر (برای نمایش در ResultBox) ──
def render_text_image(text, width, px=20, align_right=True):
    """متن فارسی را راست‌چین روی پس‌زمینه‌ی تیره می‌کشد؛ باید در نخ اصلی (wx) صدا زده شود."""
    width = max(260, int(width))
    pad, px = 12, int(px)
    font = wx.Font(wx.Size(0, px), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                   wx.FONTWEIGHT_NORMAL, False, UI_FONT_FACE)
    probe = wx.MemoryDC(wx.Bitmap(1, 1))
    probe.SetFont(font)
    maxw = width - 2 * pad
    lines = []
    for para in str(text).replace("\r", "").split("\n"):
        para = para.strip()
        if not para:
            lines.append("")
            continue
        cur = ""
        for word in para.split():
            trial = word if not cur else cur + " " + word
            if cur and probe.GetTextExtent(trial)[0] > maxw:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        if cur:
            lines.append(cur)
    lh = probe.GetTextExtent("Ag")[1] + 6
    height = max(48, pad * 2 + lh * max(1, len(lines)))
    bmp = wx.Bitmap(width, height)
    dc = wx.MemoryDC(bmp)
    dc.SetBackground(wx.Brush(wx.Colour(24, 26, 33)))
    dc.Clear()
    dc.SetFont(font)
    dc.SetTextForeground(wx.Colour(245, 245, 248))
    y = pad
    for ln in lines:
        if ln:
            tw = dc.GetTextExtent(ln)[0]
            dc.DrawText(ln, max(pad, width - pad - tw) if align_right else pad, y)
        y += lh
    dc.SelectObject(wx.NullBitmap)
    raw = bmp.ConvertToImage().GetData()
    return Image.frombytes("RGB", (width, height), bytes(raw))




def render_overlay_image(img, regions):
    """ترجمه را دقیقاً روی جای متن اصلی می‌کشد (پس‌زمینه‌ی هم‌رنگ، فارسی راست‌چین)؛ در نخ اصلی (wx) صدا بزن."""
    base = img.convert("RGB")
    bmp = pil_to_bitmap(base)
    dc = wx.MemoryDC(bmp)
    try:
        for r in regions:
            x0, y0, x1, y1 = r["box"]
            pad = 3
            x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
            x1, y1 = min(base.width, x1 + pad), min(base.height, y1 + pad)
            bw, bh = max(10, x1 - x0), max(10, y1 - y0)
            words = r["text"].split()
            chosen = None
            for px in range(min(44, max(10, bh)), 8, -1):
                font = wx.Font(wx.Size(0, px), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                               wx.FONTWEIGHT_NORMAL, False, UI_FONT_FACE)
                dc.SetFont(font)
                lines, cur = [], ""
                for wd in words:
                    trial = wd if not cur else cur + " " + wd
                    if cur and dc.GetTextExtent(trial)[0] > bw - 4:
                        lines.append(cur)
                        cur = wd
                    else:
                        cur = trial
                if cur:
                    lines.append(cur)
                lh = dc.GetTextExtent("Ag")[1] + 2
                chosen = (font, lines, lh)
                if lh * len(lines) <= bh:
                    break
            font, lines, lh = chosen
            need = lh * len(lines)
            if need > bh:                                   # جا نشد: کادر را تا جای ممکن به پایین بزرگ کن
                y1 = min(base.height, y0 + need)
                bh = max(bh, y1 - y0)
            bg, fg = r["bg"], r["fg"]
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(wx.Brush(wx.Colour(*bg)))
            dc.DrawRectangle(x0, y0, bw, bh)
            dc.SetFont(font)
            dc.SetTextForeground(wx.Colour(*fg))
            ty = y0 + max(0, (bh - need) // 2)
            for ln in lines:
                tw = dc.GetTextExtent(ln)[0]
                dc.DrawText(ln, max(x0 + 2, x1 - 2 - tw), ty)
                ty += lh
    finally:
        dc.SelectObject(wx.NullBitmap)
    raw = bmp.ConvertToImage().GetData()
    return Image.frombytes("RGB", (base.width, base.height), bytes(raw))


# ═════════════════════════════ ترجمه‌ی زنده‌ی بازی (Game Live Mode) ═════════════════════════════
# جریان: ROI ثابت → عکس از همان ناحیه (GDI سبک، یا dxcam دائمی) → OCR انگلیسی (Tesseract موجود)
#        → تثبیت متن (چند مشاهده‌ی یکسان) → ترجمه‌ی آفلاین (NLLB موجود، بدون هیچ fallback ابری) → پنجره‌ی شناور.
LIVE_RATES = (("low", "کم‌مصرف", 400), ("balanced", "متعادل", 200), ("fast", "سریع", 110))
LIVE_FONT_SIZES = (16, 18, 20, 22, 26, 30)
LIVE_OPACITIES = (50, 65, 80, 90, 100)
ID_LIVE = 104
_WDA_EXCLUDEFROMCAPTURE = 0x11


def live_norm_text(raw):
    """خروجی OCR → متن تمیز؛ اگر شبیه زیرنویس نبود (نویز) رشته‌ی خالی."""
    t = " ".join(str(raw or "").replace("\x0c", " ").split())
    t = re.sub(r"(?<!\S)\|(?!\S)", "I", t)                     # «|» تنها معمولاً «I» است
    letters = len(re.findall(r"[A-Za-z]", t))
    body = len(re.sub(r"\s", "", t))
    if letters < 3 or body == 0 or letters / float(body) < 0.55:
        return ""
    if not re.search(r"[A-Za-z]{2,}", t):
        return ""
    return t


def live_key(text):
    """کلید مقایسه: حروف/اعداد کوچک، بدون فاصله و علامت (تفاوت‌های ریز OCR نادیده گرفته می‌شود)."""
    return re.sub(r"[^a-z0-9]+", "", str(text or "").lower())


class LiveTextTracker(object):
    """تثبیت و حذف تکراری: متن وقتی «پایدار» است که N مشاهده‌ی پیاپی دقیقاً یکسان باشد (متن در حال تایپ‌شدن
    هیچ‌وقت پایدار نمی‌شود). متنِ پایدارِ مشابهِ قبلی (≥ ۹۷٪) دوباره ترجمه نمی‌شود، ولی تغییر واقعی یک کلمه می‌شود."""

    SAME_RATIO = 0.97

    def __init__(self, stability=2, clear_after_s=2.5):
        self.stability = max(1, int(stability))
        self.clear_after = float(clear_after_s)
        self.reset()

    def reset(self):
        self.cand_key = None
        self.cand_text = ""
        self.cand_n = 0
        self.last_key = None
        self.empty_since = None
        self.dups = 0

    def configure(self, stability, clear_after_s):
        self.stability = max(1, int(stability))
        self.clear_after = float(clear_after_s)

    def _differs(self, key):
        if self.last_key is None:
            return True
        if key == self.last_key:
            return False
        import difflib
        return difflib.SequenceMatcher(None, key, self.last_key).ratio() < self.SAME_RATIO

    def observe(self, text, now):
        """text: متن نرمال‌شده یا '' برای «چیزی خوانده نشد». خروجی: ("new", متن) | ("clear", None) | None."""
        key = live_key(text) if text else ""
        if not key:
            self.cand_key, self.cand_n = None, 0
            if self.empty_since is None:
                self.empty_since = now
            if self.last_key is not None and now - self.empty_since >= self.clear_after:
                self.last_key = None
                return ("clear", None)
            return None
        self.empty_since = None
        if key == self.cand_key:
            self.cand_n += 1
        else:
            self.cand_key, self.cand_text, self.cand_n = key, text, 1
        if self.cand_n >= self.stability:
            if self._differs(key):
                self.last_key = key
                return ("new", self.cand_text)
            if self.cand_n == self.stability:
                self.dups += 1                       # متن ثابت (یا لرزش ریز) → ترجمه‌ی تکراری انجام نشد
        return None


def _live_gdi():
    """نمونه‌ی خصوصی gdi32/user32 با نوع‌های درست (تا روی بقیه‌ی کد اثر نگذارد)."""
    g = ctypes.WinDLL("gdi32", use_last_error=True)
    u = ctypes.WinDLL("user32", use_last_error=True)
    vp, ci, cu = ctypes.c_void_p, ctypes.c_int, ctypes.c_uint
    u.GetDC.argtypes, u.GetDC.restype = [vp], vp
    u.ReleaseDC.argtypes, u.ReleaseDC.restype = [vp, vp], ci
    g.CreateCompatibleDC.argtypes, g.CreateCompatibleDC.restype = [vp], vp
    g.CreateCompatibleBitmap.argtypes, g.CreateCompatibleBitmap.restype = [vp, ci, ci], vp
    g.SelectObject.argtypes, g.SelectObject.restype = [vp, vp], vp
    g.BitBlt.argtypes, g.BitBlt.restype = [vp, ci, ci, ci, ci, vp, ci, ci, cu], ci
    g.GetDIBits.argtypes, g.GetDIBits.restype = [vp, vp, cu, cu, vp, vp, cu], ci
    g.DeleteObject.argtypes, g.DeleteObject.restype = [vp], ci
    g.DeleteDC.argtypes, g.DeleteDC.restype = [vp], ci
    return g, u


class _BMIH(ctypes.Structure):
    _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
                ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32),
                ("biYPelsPerMeter", ctypes.c_int32), ("biClrUsed", ctypes.c_uint32),
                ("biClrImportant", ctypes.c_uint32)]


class _LiveGrabber(object):
    """گرفتن عکس فقط از ناحیه‌ی ROI. پیش‌فرض GDI (سبک و بدون ساخت منبع تازه در هر فریم)؛
    اگر بازی با GDI سیاه بود و dxcam هست، یک دوربین DXGI دائمی ساخته و دوباره استفاده می‌شود."""

    def __init__(self):
        self.mode = "gdi"
        self._g = self._u = None
        self._cam = None
        self._cam_mon = None
        self._last_dx = None
        self.dx_tried = False

    def _ensure_gdi(self):
        if self._g is None:
            self._g, self._u = _live_gdi()

    def grab(self, rect):
        if self.mode == "dx":
            img = self._grab_dx(rect)
            if img is not None:
                return img
            return None
        return self._grab_gdi(rect)

    def _grab_gdi(self, rect):
        x, y, w, h = [int(v) for v in rect]
        if w < 1 or h < 1:
            return None
        self._ensure_gdi()
        g, u = self._g, self._u
        hdc = u.GetDC(None)
        if not hdc:
            return None
        mdc = bmp = old = None
        try:
            mdc = g.CreateCompatibleDC(hdc)
            bmp = g.CreateCompatibleBitmap(hdc, w, h)
            if not mdc or not bmp:
                return None
            old = g.SelectObject(mdc, bmp)
            if not g.BitBlt(mdc, 0, 0, w, h, hdc, x, y, 0x00CC0020 | 0x40000000):    # SRCCOPY | CAPTUREBLT
                return None
            bi = _BMIH()
            bi.biSize, bi.biWidth, bi.biHeight = ctypes.sizeof(_BMIH), w, -h
            bi.biPlanes, bi.biBitCount, bi.biCompression = 1, 32, 0
            buf = ctypes.create_string_buffer(w * h * 4)
            if not g.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bi), 0):
                return None
            return Image.frombuffer("RGB", (w, h), bytes(buf), "raw", "BGRX", 0, 1)
        finally:
            try:
                if old:
                    g.SelectObject(mdc, old)
                if bmp:
                    g.DeleteObject(bmp)
                if mdc:
                    g.DeleteDC(mdc)
                u.ReleaseDC(None, hdc)
            except Exception:
                pass

    def _dx_make(self, mon):
        try:
            import dxcam
        except Exception:
            return None
        for idx in range(8):
            try:
                c = dxcam.create(output_idx=idx, output_color="RGB")
            except Exception:
                break
            if c is None:
                break
            if (getattr(c, "width", 0), getattr(c, "height", 0)) == (mon[2], mon[3]):
                return c
            _dx_release(c)
        return None

    def _grab_dx(self, rect):
        x, y, w, h = [int(v) for v in rect]
        try:
            mon = tuple(monitor_at(x + w // 2, y + h // 2))
            if self._cam is None or self._cam_mon != mon:
                self.close_dx()
                self._cam = self._dx_make(mon)
                self._cam_mon = mon
            if self._cam is None:
                return None
            l, t = x - mon[0], y - mon[1]
            frame = self._cam.grab(region=(l, t, l + w, t + h))
            if frame is None:                       # صفحه تغییری نکرده → همان فریم قبلی
                return self._last_dx
            self._last_dx = Image.fromarray(frame)
            return self._last_dx
        except Exception as exc:
            dbg("live dx grab failed: %r" % (exc,))
            return None

    def try_dx(self, rect):
        """یک‌بار تست می‌کند آیا DXGI تصویر غیرسیاه می‌دهد؛ اگر آری، به آن سوئیچ می‌کند."""
        self.dx_tried = True
        prev = self.mode
        self.mode = "dx"
        img = self._grab_dx(rect)
        if img is not None and not is_black(img):
            return True
        self.mode = prev
        self.close_dx()
        return False

    def close_dx(self):
        if self._cam is not None:
            _dx_release(self._cam)
        self._cam = None
        self._cam_mon = None
        self._last_dx = None

    def close(self):
        self.close_dx()


def _proc_ram_mb():
    """مصرف RAM پروسه‌ی خود برنامه (مگابایت)."""
    try:
        class _PMC(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        pmc = _PMC()
        pmc.cb = ctypes.sizeof(_PMC)
        k = ctypes.WinDLL("kernel32")
        k.GetCurrentProcess.restype = ctypes.c_void_p
        p = ctypes.WinDLL("psapi")
        p.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
        if p.GetProcessMemoryInfo(k.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
            return pmc.WorkingSetSize / 1048576.0
    except Exception:
        pass
    return 0.0


class GameLiveController(object):
    """حلقه‌ی زنده: یک نخ برای عکس+OCR و یک نخ برای ترجمه. هر دو daemon هستند و با stop() کامل متوقف می‌شوند.
    نتیجه‌ها فقط با wx.CallAfter به رابط می‌رسند و با شماره‌ی نسل (gen) کهنه‌ها دور ریخته می‌شوند."""

    CACHE_MAX = 64

    def __init__(self, app):
        self.app = app
        self._stop = threading.Event()
        self._thread = None
        self._tr_thread = None
        self._cancel = None
        self._cv = threading.Condition()
        self._pending = None              # (gen, text) — فقط جدیدترین نگه داشته می‌شود (صف ۱تایی)
        self.gen = 0
        self._cache = {}
        self._cache_order = []
        self.stats = {}
        self._dump_req = False
        self._last_state = None
        self._last_stats_post = 0.0
        self.roi = None
        self.session = 0

    @property
    def running(self):
        t = self._thread
        return bool(t is not None and t.is_alive() and not self._stop.is_set())

    # ── پیش‌بررسی نیازمندی‌ها (پیام روشن برای هر کمبود) ──
    @staticmethod
    def preflight():
        if not find_tesseract():
            return "Tesseract نصب نیست؛ در صفحه‌ی «ترجمه‌ی آفلاین» گزینه‌ی «دانلود مدل‌ها» را بزنید."
        if not tess_model_installed("eng"):
            return ("مدل OCR انگلیسی (eng) نصب نیست یا خراب است؛ در صفحه‌ی «ترجمه‌ی آفلاین» زبان OCR را روی انگلیسی "
                    "بگذارید و «دانلود مدل‌ها» را بزنید.")
        if not argos_lib_available():
            return "کتابخانه‌ی ترجمه‌ی آفلاین (ctranslate2 / sentencepiece) نصب نیست؛ در صفحه‌ی آفلاین «دانلود مدل‌ها» را بزنید."
        if not nllb_installed():
            return ("مدل ترجمه‌ی آفلاین «%s» نصب نیست؛ در صفحه‌ی «ترجمه‌ی آفلاین» «دانلود مدل‌ها» را بزنید "
                    "(ترجمه‌ی زنده هرگز به سرویس آنلاین وصل نمی‌شود)." % nllb_spec()["short"])
        return ""

    def _new_stats(self):
        return {"frames": 0, "ocr_n": 0, "skip_n": 0, "ocr_ms": 0.0, "tr_n": 0, "tr_ms": 0.0, "cache_hits": 0,
                "stale": 0, "dups": 0, "errors": 0, "backend": "gdi", "show_ms": 0.0, "ram_mb": 0.0,
                "t0": time.time(), "ocr_per_min": 0.0}

    def start(self, roi):
        if self.running:
            return
        self._stop = threading.Event()
        self.session += 1
        self.roi = roi
        self.gen += 1
        self._pending = None
        self._last_state = None
        self.stats = self._new_stats()
        self._thread = threading.Thread(target=self._run_capture, name="live-ocr", daemon=True)
        self._tr_thread = threading.Thread(target=self._run_translate, name="live-translate", daemon=True)
        self._thread.start()
        self._tr_thread.start()
        dbg("live: started")

    def stop(self, join_timeout=1.5):
        self._stop.set()
        self.gen += 1
        c = self._cancel
        if c is not None:
            c.cancel()                                  # Tesseract در حال اجرا کشته می‌شود
        with self._cv:
            self._pending = None
            self._cv.notify_all()
        me = threading.current_thread()
        for t in (self._thread, self._tr_thread):
            if t is not None and t is not me:
                t.join(timeout=join_timeout)
        self._thread = self._tr_thread = None
        s = self.stats
        if s:
            mins = max(1e-6, (time.time() - s["t0"]) / 60.0)
            dbg("live: stopped — frames=%d ocr=%d (%.0f/min) skipped=%d tr=%d cache=%d dups=%d stale=%d errors=%d "
                "ocr_ms=%.0f tr_ms=%.0f backend=%s" % (s["frames"], s["ocr_n"], s["ocr_n"] / mins, s["skip_n"],
                                                       s["tr_n"], s["cache_hits"], s["dups"], s["stale"], s["errors"],
                                                       s["ocr_ms"], s["tr_ms"], s["backend"]))

    def request_dump(self):
        self._dump_req = True

    # ── ارتباط با رابط (فقط از مسیر امن wx.CallAfter) ──
    def _post_state(self, code, text):
        if self._last_state == (code, text):
            return
        self._last_state = (code, text)
        wx.CallAfter(self.app._live_set_state, code, text)

    def _post_stats(self, force=False):
        now = time.time()
        if not force and now - self._last_stats_post < 0.6:
            return
        self._last_stats_post = now
        s = self.stats
        s["ram_mb"] = _proc_ram_mb()
        s["ocr_per_min"] = s["ocr_n"] / max(1e-6, (now - s["t0"]) / 60.0)
        wx.CallAfter(self.app._live_stats, dict(s))

    def _ema(self, key, v):
        s = self.stats
        s[key] = v if not s[key] else (0.7 * s[key] + 0.3 * v)

    # ── نخ عکس + OCR ──
    def _run_capture(self):
        app = self.app
        stop = self._stop
        sid = self.session
        roi = self.roi
        rect = tuple(roi["rect"])
        tmp = tempfile.mkdtemp(prefix="eshlive_")
        grabber = _LiveGrabber()
        tracker = LiveTextTracker(app.cfg["game_live_stability_count"], app.cfg["game_live_clear_delay_ms"] / 1000.0)
        exe = find_tesseract()
        prev_sig, prev_text = None, ""
        black_run = 0
        err_run = 0
        grab_fail = 0
        warned_black = False
        slow_mult, slow_run, fast_run = 1.0, 0, 0               # کاهش خودکار نرخ OCR وقتی بازی/GPU زیر فشار است
        try:
            self._post_state("ready", "آماده — در حال بارگذاری مدل ترجمه…")
            while not stop.is_set():
                t_loop = time.time()
                interval = {"low": 0.40, "balanced": 0.20, "fast": 0.11}.get(app.cfg["game_live_rate"], 0.20) * slow_mult
                tracker.configure(app.cfg["game_live_stability_count"], app.cfg["game_live_clear_delay_ms"] / 1000.0)
                try:
                    _tg = time.time()
                    img = grabber.grab(rect)
                    _grab_ms = (time.time() - _tg) * 1000.0
                    if _grab_ms > 70.0:                          # گرفتن عکس کند شده = بازی/GPU فریم‌ریت پایین دارد
                        slow_run, fast_run = slow_run + 1, 0
                    else:
                        fast_run, slow_run = fast_run + 1, 0
                    if slow_run >= 4 and slow_mult < 4.0:
                        slow_mult, slow_run = min(4.0, slow_mult * 1.5), 0
                        dbg("live: low fps detected → OCR interval x%.2f" % slow_mult)
                        self._post_state("ready", "فریم‌ریت بازی پایین است؛ نرخ OCR خودکار کم شد تا بازی روان بماند.")
                    elif fast_run >= 40 and slow_mult > 1.0:
                        slow_mult, fast_run = max(1.0, slow_mult / 1.5), 0
                    self.stats["frames"] += 1
                    if img is None:
                        grab_fail += 1
                        self.stats["errors"] += 1
                        if grab_fail == 8:
                            self._post_state("error", "گرفتن تصویر از ناحیه ممکن نشد؛ اگر بازی Exclusive Fullscreen است "
                                                      "آن را روی Borderless Windowed بگذارید.")
                        stop.wait(max(0.25, interval))
                        continue
                    grab_fail = 0
                    # تشخیص «سیاه بودن دائمی»: با GDI بازی‌های تمام‌صفحه سیاه می‌شوند → یک‌بار DXGI را امتحان کن
                    if is_black(img):
                        black_run += 1
                        if black_run == 15 and grabber.mode == "gdi" and not grabber.dx_tried:
                            if grabber.try_dx(rect):
                                self.stats["backend"] = "dxcam"
                                dbg("live: switched to dxcam")
                        elif black_run == 80 and not warned_black:
                            warned_black = True
                            self._post_state("error", "تصویر ناحیه سیاه است؛ اگر بازی Exclusive Fullscreen است آن را "
                                                      "روی Borderless Windowed بگذارید.")
                    else:
                        black_run = 0
                        if warned_black:
                            warned_black = False
                            self._last_state = None
                    sig = image_sig(img)
                    changed = prev_sig is None or sig_diff(sig, prev_sig) > SAME_IMG_DIFF
                    raw = None
                    if changed:
                        self._cancel = cancel = CancelToken()
                        t1 = time.time()
                        raw = _tess_read(exe, ocr_preprocess(img), "eng", tmp, cancel, "live", psm="6")
                        if not live_norm_text(raw):               # تلاش دوم: باینری و معکوس (متن رنگی/سایه‌دار بازی‌ها)
                            for kw in ({"binarize": True}, {"flip": True}):
                                if stop.is_set():
                                    break
                                raw2 = _tess_read(exe, ocr_preprocess(img, **kw), "eng", tmp, cancel, "live", psm="6")
                                if live_norm_text(raw2):
                                    raw = raw2
                                    break
                        self._ema("ocr_ms", (time.time() - t1) * 1000.0)
                        self.stats["ocr_n"] += 1
                        prev_sig, prev_text = sig, live_norm_text(raw)
                        if self._dump_req:
                            self._dump_req = False
                            self._dump_debug(img, raw)
                    else:
                        self.stats["skip_n"] += 1
                    if changed:
                        wx.CallAfter(self.app._live_ocr_seen, sid, prev_text)
                    ev = tracker.observe(prev_text, time.time())
                    err_run = 0                               # یک چرخه‌ی کامل بدون خطا
                    self.stats["dups"] = tracker.dups
                    if ev is not None:
                        self._on_event(ev)
                except EngineError as exc:
                    if stop.is_set():
                        break
                    self.stats["errors"] += 1
                    dbg("live frame error: %s" % exc)
                    err_run += 1
                    if err_run >= 3:
                        self._post_state("error", str(exc))
                    stop.wait(0.5)
                except Exception as exc:
                    if stop.is_set():
                        break
                    self.stats["errors"] += 1
                    err_run += 1
                    dbg("live frame crashed: %r" % (exc,))
                    if err_run >= 3:
                        self._post_state("error", "خطا در پایش زیرنویس؛ جزئیات در debug.log")
                    stop.wait(0.5)
                self._post_stats()
                rest = interval - (time.time() - t_loop)
                if rest > 0:
                    stop.wait(rest)                       # حلقه هیچ‌وقت بدون وقفه نمی‌چرخد؛ فریم‌ها صف نمی‌شوند
        finally:
            try:
                grabber.close()
            except Exception:
                pass
            shutil.rmtree(tmp, ignore_errors=True)
            if not stop.is_set():
                stop.set()
            wx.CallAfter(self.app._live_thread_ended, sid)

    def _on_event(self, ev):
        kind, text = ev
        if kind == "clear":
            self.gen += 1
            with self._cv:
                self._pending = None
            wx.CallAfter(self.app._live_clear, self.gen)
            return
        self.gen += 1
        gen = self.gen
        key = live_key(text)
        hit = self._cache.get(key)
        if hit is not None:
            self.stats["cache_hits"] += 1
            self._touch(key)
            wx.CallAfter(self.app._live_result, gen, text, hit, 0.0)
            return
        self._post_state("translating", "در حال ترجمه")
        wx.CallAfter(self.app._live_preview, gen, text)       # متن انگلیسی همان لحظه روی صفحه دیده شود
        with self._cv:
            self._pending = (gen, text, time.time())      # جدیدترین متن پایدار جایگزین قبلی می‌شود
            self._cv.notify()

    def _touch(self, key):
        if key in self._cache_order:
            self._cache_order.remove(key)
        self._cache_order.append(key)

    def _cache_put(self, key, fa):
        self._cache[key] = fa
        self._touch(key)
        while len(self._cache_order) > self.CACHE_MAX:
            self._cache.pop(self._cache_order.pop(0), None)

    # ── نخ ترجمه ──
    def _run_translate(self):
        stop = self._stop
        try:
            _nllb_load()                                  # یک‌بار؛ مدل در حافظه می‌ماند و دوباره بارگذاری نمی‌شود
        except EngineError as exc:
            if not stop.is_set():
                wx.CallAfter(self.app._live_fatal, str(exc))
            return
        except Exception as exc:
            dbg("live model load crashed: %r" % (exc,))
            if not stop.is_set():
                wx.CallAfter(self.app._live_fatal, "بارگذاری مدل ترجمه ناموفق بود؛ جزئیات در debug.log")
            return
        self._last_state = None
        self._post_state("reading", "در حال خواندن متن")
        while not stop.is_set():
            with self._cv:
                while self._pending is None and not stop.is_set():
                    self._cv.wait(0.5)
                if stop.is_set():
                    break
                gen, text, t_stable = self._pending
                self._pending = None
            if gen != self.gen:
                self.stats["stale"] += 1
                continue
            try:
                t0 = time.time()
                fa = _nllb_translate(text, "en", fast=True)
                ms = (time.time() - t0) * 1000.0
            except EngineError as exc:
                if stop.is_set():
                    break
                self.stats["errors"] += 1
                self._post_state("error", str(exc))
                continue
            except Exception as exc:
                if stop.is_set():
                    break
                self.stats["errors"] += 1
                dbg("live translate crashed: %r" % (exc,))
                self._post_state("error", "خطا در ترجمه؛ جزئیات در debug.log")
                continue
            self.stats["tr_n"] += 1
            self._ema("tr_ms", ms)
            if gen != self.gen or stop.is_set():          # دیالوگ عوض شده؛ ترجمه‌ی قدیمی روی متن جدید نمی‌نشیند
                self.stats["stale"] += 1
                continue
            if fa:
                self._cache_put(live_key(text), fa)
                self._ema("show_ms", (time.time() - t_stable) * 1000.0)
                wx.CallAfter(self.app._live_result, gen, text, fa, ms)
            self._post_state("reading", "در حال خواندن متن")

    def _dump_debug(self, img, raw):
        """فقط با درخواست صریح کاربر: ROI و متن OCR را برای عیب‌یابی ذخیره می‌کند."""
        try:
            d = os.path.join(OFFLINE_DIR, "live_debug")
            os.makedirs(d, exist_ok=True)
            tag = time.strftime("%Y%m%d_%H%M%S")
            img.save(os.path.join(d, "roi_%s.png" % tag))
            with open(os.path.join(d, "roi_%s.txt" % tag), "w", encoding="utf-8") as f:
                f.write(raw or "")
            wx.CallAfter(self.app.panel.set_state, "تصویر و متن OCR ذخیره شد: %s" % d, "ok", 6000)
        except Exception as exc:
            dbg("live dump failed: %r" % (exc,))


class LiveOverlay(wx.Frame):
    """پنجره‌ی ترجمه‌ی زنده: بالای بازی، بدون گرفتن فوکوس، کلیک از آن رد می‌شود (بازی را مسدود نمی‌کند) و
    (در ویندوز ۱۰ نسخه‌ی ۲۰۰۴ به بعد) از عکس‌گرفتن/OCR حذف می‌شود تا حلقه‌ی بازخورد ساخته نشود."""

    def __init__(self, app):
        super().__init__(None, style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE)
        self.app = app
        self.bmp = None
        self.visible = False
        self.rect = (0, 0, 10, 10)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        no_activate(self, layered=True)
        try:
            h = self.GetHandle()
            st = user32.GetWindowLongW(h, GWL_EXSTYLE)
            user32.SetWindowLongW(h, GWL_EXSTYLE, st | 0x20)               # WS_EX_TRANSPARENT: کلیک عبور می‌کند
        except Exception:
            pass
        self.excluded = set_capture_exclusion(self, True)
        self._top = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._tick, self._top)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

    def _tick(self, _evt):
        if self.visible:
            try:
                raise_top(self)
            except Exception:
                pass

    def _on_paint(self, _evt):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(wx.Colour(24, 26, 33)))
        dc.Clear()
        if self.bmp is not None and self.bmp.IsOk():
            dc.DrawBitmap(self.bmp, 0, 0, False)

    def show_text(self, fa, src, roi_rect, force_src=False):
        cfg = self.app.cfg
        mon = monitor_at(roi_rect[0] + roi_rect[2] // 2, roi_rect[1] + roi_rect[3] // 2)
        width = max(420, min(int(roi_rect[2]), int(mon[2] * 0.85)))
        px = int(cfg["game_live_overlay_font_size"])
        img = render_text_image(fa, width, px=px)
        if (cfg["game_live_show_source"] or force_src) and src:
            small = render_text_image(src, width, px=max(14, int(px * 0.78)), align_right=False)
            both = Image.new("RGB", (width, img.height + small.height), (24, 26, 33))
            both.paste(small, (0, 0))
            both.paste(img, (0, small.height))
            img = both
        self.bmp = pil_to_bitmap(img)
        x, y = self.app._live_overlay_pos(roi_rect, img.width, img.height)
        self.rect = (x, y, img.width, img.height)
        try:
            user32.SetLayeredWindowAttributes(self.GetHandle(), 0, int(255 * cfg["game_live_overlay_opacity"] / 100.0), 2)
        except Exception:
            pass
        try:
            if not self.IsShown():
                self.Show()                       # wx باید پنجره را «نمایان» بداند؛ NOACTIVATE فوکوس را نمی‌دزدد
        except Exception:
            pass
        place_top(self, x, y, img.width, img.height)
        round_corners(self, img.width, img.height, 8)
        self.visible = True
        if not self._top.IsRunning():
            self._top.Start(400)
        self.Refresh(False)
        self.Update()

    def hide_text(self):
        self.visible = False
        self.bmp = None
        try:
            self.Hide()
        except Exception:
            pass
        try:
            if self._top.IsRunning():
                self._top.Stop()
        except Exception:
            pass
        hide_win(self)


def set_capture_exclusion(win, on):
    """پنجره را از عکس‌گرفتن/OCR (و ضبط) خارج می‌کند؛ فقط ویندوز ۱۰ نسخه‌ی ۲۰۰۴ به بعد. خروجی: موفق؟"""
    try:
        return bool(user32.SetWindowDisplayAffinity(win.GetHandle(), _WDA_EXCLUDEFROMCAPTURE if on else 0))
    except Exception:
        return False




class FloatingPanel(wx.Frame):
    """پنل شناورِ جمع‌وجور؛ تنظیمات در همین پنجره و بدون ساختن فریم تازه نمایش داده می‌شود."""
    wstep = 0                       # صفحه‌ی فعلیِ «راهنمای شروع»
    wsolo = False                   # فقط «رنگ و فونت» (از تنظیمات)
    W, H_FULL, H_SETTINGS, H_ABOUT, H_MIN = 360, 474, 380, 380, 36
    PAGE_H = {"main": 474, "settings": 570, "about": 380, "engine": 300,
              "ai": 412, "offline": 490, "outmon": 420, "net": 268, "welcome": 404, "live": 524}
    SUB_PAGES = ("settings", "about", "engine", "ai", "offline", "outmon", "net", "welcome", "live")
    PAGE_TITLES = {"settings": "تنظیمات", "about": "درباره توسعه دهنده", "engine": "موتور ترجمه",
                   "ai": "ترجمه با Ai", "offline": "ترجمه‌ی آفلاین", "outmon": "مانیتور خروجی",
                   "net": "تنظیمات شبکه", "welcome": "راهنمای شروع", "live": "ترجمه زنده بازی"}
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
            self.SetIcons(make_icon_bundle())
        except Exception:
            pass
        self.app = app
        self.pinned = bool(self.app.cfg["panel_pinned"])
        self._tray_settings_force_top = False
        try:
            self.s = _system_dpi_scale()
        except Exception:
            self.s = 1.0
        self._dpi_s = self.s
        try:
            _pct = int(self.app.cfg["ui_scale"] or 100)
        except Exception:
            _pct = 100
        self.s = self._dpi_s * _pct / 100.0
        globals()["_UI_SCALE"] = _pct / 100.0
        self.collapsed = False
        self._stack = []               # پشته‌ی صفحه‌های قبلی برای دکمه‌ی «صفحه قبل»
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
        self._logo_timer = None
        self._tick_logo()
        self._sync_ready_blink()
        self._keep()


    def _S(self, v):
        return int(round(v * self.s))

    def _size(self):
        h = self.H_MIN if self.collapsed else self.PAGE_H.get(self.page, self.H_FULL)
        if self.page == "ai" and not self.collapsed:
            h += self._ai_off()
        return self._S(self.W), self._S(h)

    def _ai_off(self):
        """سرویس «سفارشی» یک ردیف آدرس اضافه دارد؛ همه‌ی اجزای زیرش این‌قدر پایین می‌روند."""
        try:
            return 42 if self.app.ai["provider"] == "custom" else 0
        except Exception:
            return 0

    def relayout(self):
        if self._alive:
            self._areas = self._build()
            self._shape_sz = None
            self._apply()
            self.Refresh(False)

    def apply_scale(self):
        """اندازه‌ی کل رابط را از تنظیمات (۱۰۰ تا ۱۵۰٪) اعمال می‌کند."""
        try:
            pct = int(self.app.cfg["ui_scale"] or 100)
        except Exception:
            pct = 100
        self.s = self._dpi_s * pct / 100.0
        globals()["_UI_SCALE"] = pct / 100.0
        self._about_bitmap = None
        self._about_bitmap_size = None
        self.relayout()

    def _game_lite(self):
        """هنگام بازیِ تمام‌صفحه یا حالت استریم، انیمیشن‌های پنل خاموش می‌شود (کاهش مصرف CPU/GPU)."""
        try:
            if bool(self.app.cfg["stream_mode"]):        # حالت استریم: همیشه بدون انیمیشن
                self._gl_v = True
                return True
            if not self.app.cfg["game_lite_ui"]:
                return False
            now = time.time()
            if now - getattr(self, "_gl_t", 0.0) > 1.0:
                self._gl_t = now
                self._gl_v = bool(foreground_game() or exclusive_fullscreen_active())
            return self._gl_v
        except Exception:
            return False

    def _monitor_tiles(self):
        """[(شماره‌ی مانیتور، wx.Rect)] — نقشه‌ی کوچک چیدمان مانیتورها برای انتخاب خروجی."""
        S = self._S
        mons = getattr(self.app, "_monitor_rects_cache", None) or list_monitor_rects()
        box = wx.Rect(S(12), S(70), S(self.W) - S(24), S(120))
        minx = min(m[0] for m in mons)
        miny = min(m[1] for m in mons)
        tw = max(1, max(m[0] + m[2] for m in mons) - minx)
        th = max(1, max(m[1] + m[3] for m in mons) - miny)
        ix, iy, iw, ih = box.x + S(10), box.y + S(10), box.width - S(20), box.height - S(20)
        scale = min(iw / float(tw), ih / float(th))
        ox = ix + (iw - tw * scale) / 2.0
        oy = iy + (ih - th * scale) / 2.0
        tiles = []
        for i, (x, y, mw, mh) in enumerate(mons, 1):
            tiles.append((i, wx.Rect(int(ox + (x - minx) * scale) + 1, int(oy + (y - miny) * scale) + 1,
                                     max(S(26), int(mw * scale) - 2), max(S(20), int(mh * scale) - 2))))
        return tiles

    def _off_all_ok(self):
        """True وقتی Tesseract، مدل OCR و مدل ترجمه‌ی انتخابی همه نصب‌اند و دانلودی در جریان نیست."""
        try:
            off = self.app.off
            return bool(off["tess_exe"] and off["tess_model"] and off["argos"] == "ok"
                        and not off["busy"] and not off.get("paused") and off["progress"] <= 0)
        except Exception:
            return False

    def _build(self):
        S, w = self._S, self._S(self.W)
        full = w - S(24)

        a = {
            "hdr": wx.Rect(0, 0, w, S(36)),
            "hide": wx.Rect(w - S(38), S(7), S(22), S(22)),
            "collapse": wx.Rect(w - S(66), S(7), S(22), S(22)),
            "pin": wx.Rect(w - S(94), S(7), S(22), S(22)),
        }
        if self.page in self.SUB_PAGES:
            a["back"] = wx.Rect(w - S(220), S(4), S(112), S(28))
        if self.collapsed:
            return a
        page = self.page
        if page == "settings":
            a["settings_snip_key"] = wx.Rect(S(12), S(42), w - S(24), S(34))
            a["settings_close_key"] = wx.Rect(S(12), S(81), w - S(24), S(34))
            btn_w, btn_y, btn_h = S(190), S(169), S(38)
            a["browse_dir"] = wx.Rect((w - btn_w) // 2, btn_y, btn_w, btn_h)
            a["monitor_prev"] = wx.Rect(S(12), S(237), S(32), S(35))
            a["monitor_value"] = wx.Rect(S(47), S(237), w - S(94), S(35))
            a["monitor_next"] = wx.Rect(w - S(44), S(237), S(32), S(35))
            a["performance_mode"] = wx.Rect(S(12), S(322), w - S(24), S(34))
            shw = (w - S(24) - S(8)) // 2
            a["settings_net"] = wx.Rect(S(12) + shw + S(8), S(280), shw, S(34))
            a["settings_theme"] = wx.Rect(S(12), S(280), shw, S(34))
            a["tools_lite"] = wx.Rect(S(12), S(364), full, S(34))
            a["stream_mode"] = wx.Rect(S(12), S(406), full, S(34))
            a["scale_prev"] = wx.Rect(S(12), S(448), S(32), S(34))
            a["scale_value"] = wx.Rect(S(47), S(448), w - S(94), S(34))
            a["scale_next"] = wx.Rect(w - S(44), S(448), S(32), S(34))
            thw = (full - S(10)) // 2
            a["tools_import"] = wx.Rect(S(12), S(490), thw, S(34))
            a["tools_export"] = wx.Rect(S(12) + thw + S(10), S(490), thw, S(34))
        elif page == "about":
            a["about_github"] = wx.Rect(S(12), S(46), w - S(24), S(30))
            a["about_telegram"] = wx.Rect(S(12), S(82), w - S(24), S(30))
        elif page == "engine":
            # دکمه‌های «تنظیمات» داخل ردیف‌ها هستند و باید در hit-test اولویت داشته باشند
            a["engine_ai_cfg"] = wx.Rect(S(22), S(137), S(64), S(28))
            a["engine_offline_cfg"] = wx.Rect(S(22), S(193), S(64), S(28))
            a["engine_google"] = wx.Rect(S(12), S(70), full, S(50))
            a["engine_ai"] = wx.Rect(S(12), S(126), full, S(50))
            a["engine_offline"] = wx.Rect(S(12), S(182), full, S(50))
        elif page == "ai":
            gap = S(6)
            npv = len(AI_PROVIDERS)
            pw = (full - (npv - 1) * gap) // npv
            for i, (key, _label) in enumerate(AI_PROVIDERS):
                a["ai_prov_" + key] = wx.Rect(S(12) + i * (pw + gap), S(44), pw, S(34))
            a["ai_model"] = wx.Rect(S(12), S(86), full, S(36))
            a["ai_token"] = wx.Rect(S(12), S(128), full, S(36))
            o = self._ai_off()
            if o:
                a["ai_url"] = wx.Rect(S(12), S(172), full, S(36))
            hw = (full - S(10)) // 2
            sw = (full - gap) // 2
            for i, (key, _label) in enumerate(AI_STYLES):
                a["ai_style_" + key] = wx.Rect(S(12) + i * (sw + gap), S(172 + o), sw, S(32))
            a["ai_game"] = wx.Rect(S(12), S(210 + o), full, S(36))
            a["ai_save"] = wx.Rect(S(12) + hw + S(10), S(254 + o), hw, S(36))
            a["ai_test"] = wx.Rect(S(12), S(254 + o), hw, S(36))
            a["ai_clear"] = wx.Rect(S(12), S(296 + o), full, S(28))
            a["ai_usage"] = wx.Rect(S(16), S(334 + o), full - S(96), S(18))
        elif page == "offline":
            a["ocr_prev"] = wx.Rect(S(12), S(68), S(32), S(36))
            a["ocr_value"] = wx.Rect(S(47), S(68), w - S(94), S(36))
            a["ocr_next"] = wx.Rect(w - S(44), S(68), S(32), S(36))
            hw2 = (full - S(10)) // 2
            a["nllbm_prev"] = wx.Rect(S(12), S(130), S(32), S(34))
            a["nllbm_value"] = wx.Rect(S(47), S(130), w - S(94), S(34))
            a["nllbm_next"] = wx.Rect(w - S(44), S(130), S(32), S(34))
            a["ocr_overlay"] = wx.Rect(S(12), S(420), full, S(32))
            if not self._off_all_ok():                     # همه‌ی مدل‌ها نصب‌اند → دکمه‌ی دانلود دیگر نشان داده نمی‌شود
                a["ocr_pause"] = wx.Rect(S(12), S(282), hw2, S(38))
                a["ocr_download"] = wx.Rect(S(12) + hw2 + S(10), S(282), hw2, S(38))
        elif page == "live":
            lhw = (full - S(10)) // 2
            a["live_roi"] = wx.Rect(S(12) + lhw + S(10), S(112), lhw, S(38))
            a["live_start"] = wx.Rect(S(12), S(112), lhw, S(38))
            for nm, yy in (("rate", 158), ("font", 198), ("op", 238)):
                a["live_%s_prev" % nm] = wx.Rect(S(12), S(yy), S(32), S(34))
                a["live_%s_value" % nm] = wx.Rect(S(47), S(yy), w - S(94), S(34))
                a["live_%s_next" % nm] = wx.Rect(w - S(44), S(yy), S(32), S(34))
            a["live_src"] = wx.Rect(S(12), S(280), full, S(34))
            a["live_dbg"] = wx.Rect(S(12), S(322), full, S(30))
        elif page == "net":
            ng = S(6)
            npw = (full - 2 * ng) // 3
            for i, key in enumerate(("system", "custom", "off")):
                a["net_mode_" + key] = wx.Rect(S(12) + i * (npw + ng), S(44), npw, S(34))
            a["net_url"] = wx.Rect(S(12), S(86), full, S(36))
            nhw = (full - S(10)) // 2
            a["net_test"] = wx.Rect(S(12), S(130), nhw, S(36))
            a["net_restart"] = wx.Rect(S(12) + nhw + S(10), S(130), nhw, S(36))
        elif page == "welcome":
            whw = (full - S(10)) // 2
            if getattr(self, "wsolo", False):                 # فقط «رنگ و فونت»؛ بدون «قبلی»
                self.wstep = 2
                a["w_next"] = wx.Rect(S(12), S(354), full, S(36))
            else:
                a["w_prev"] = wx.Rect(S(12), S(354), whw, S(36))
                a["w_next"] = wx.Rect(S(12) + whw + S(10), S(354), whw, S(36))
            step = getattr(self, "wstep", 0)
            if step == 1:
                for i, key in enumerate(("google", "ai", "offline")):
                    a["w_eng_" + key] = wx.Rect(S(12), S(72) + i * S(58), full, S(50))
            elif step == 2:
                sz, gp = S(36), (full - 6 * S(36)) // 5
                for i in range(len(THEME_COLORS)):
                    a["w_col_%d" % i] = wx.Rect(S(12) + i * (sz + gp), S(98), sz, sz)
                for i in range(len(available_fonts())):
                    a["w_font_%d" % i] = wx.Rect(S(12) + (i % 2) * (full // 2 + S(3)), S(172) + (i // 2) * S(40),
                                                 full // 2 - S(3), S(34))
        elif page == "outmon":
            for i, r in self._monitor_tiles():
                a["outmon_m%d" % i] = r
            a["outmon_same"] = wx.Rect(S(12), S(198), full, S(34))
            cg = S(6)
            cw = (full - 2 * cg) // 3
            for i, (key, _l) in enumerate(CORNERS):
                a["outcorner_" + key] = wx.Rect(S(12) + (i % 3) * (cw + cg), S(262) + (i // 3) * S(34), cw, S(30))
            a["outmon_test"] = wx.Rect(S(12), S(334), full, S(36))
        else:
            half = (full - S(8)) // 2
            right_x = S(12) + half + S(8)
            a["snip"] = wx.Rect(S(12), S(186), full, S(36))
            a["live"] = wx.Rect(S(12), S(228), full, S(32))
            a["engine"] = wx.Rect(S(12), S(266), full, S(34))
            a["outmon"] = wx.Rect(S(12), S(306), half, S(34))
            a["settings"] = wx.Rect(right_x, S(306), half, S(34))
            a["persian_ocr"] = wx.Rect(S(12), S(346), full, S(34))
            a["about_me"] = wx.Rect(S(12), S(386), full, S(34))
            a["quit"] = wx.Rect(w - S(178), S(428), S(168), S(34))      # فاصله‌ی ۸px ≈ ۲ میلی‌متر از دکمه‌ی بالایی      # فاصله‌ی ۸px ≈ ۲ میلی‌متر از دکمه‌ی بالایی
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
        self._suspended = False
        self.collapsed = False
        self._areas = self._build()          # باگ: بعد از جمع‌کردن با «–»، ناحیه‌ی دکمه‌ها دوباره ساخته نمی‌شد و UI خالی می‌ماند
        self._hover = None
        # اگر پین خاموش باشد، پنجره پشت بقیه‌ی پنجره‌ها می‌رفت و «نمایش داده نمی‌شد»؛ این‌جا روی همه می‌آید
        self._tray_settings_force_top = True
        self._shape_sz = None
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
        self._stack = ["main"]
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
        """نوتیف ویندوزی برداشته شد؛ پیام فقط داخل پنل شناور (متنی) نشان داده می‌شود."""
        message = "پنل پین شده است؛ برای مخفی‌کردن یا خروج کامل، ابتدا دکمهٔ 📍 را خاموش کنید."
        try:
            self.app.panel.set_state(message, "ok", 6000)
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
        self._keeper = wx.CallLater(150, self._keep)

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
            # نوتیف ویندوزی حذف شد؛ پیام متنی فقط داخل پنل
            try:
                self.panel.set_state("پین غیرفعال شد؛ اکنون می‌توانید پنل را با × مخفی کنید.", "ok", 4000)
            except Exception:
                pass

    def shutdown(self):
        self._alive = False
        for t in (self._keeper, self._rev, self._blink_timer,
                  self._title_blink_timer, self._ready_blink_timer, getattr(self, "_logo_timer", None)):
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

    def _tick_logo(self):
        """انیمیشن آرام لوگوی صفحه‌ی اول (فقط وقتی صفحه‌ی اصلی دیده می‌شود)."""
        self._logo_timer = None
        if not self._alive:
            return
        if self._game_lite():                       # بازی تمام‌صفحه: بدون انیمیشن، بررسی کم‌تکرار
            self._logo_timer = wx.CallLater(1000, self._tick_logo)
            return
        try:
            if self.page == "main" and not self.collapsed and self.IsShown():
                self.RefreshRect(wx.Rect(0, 0, self._S(184), self._S(184)), False)     # کل ناحیه‌ی لوگو (قبلاً ناقص بود → پرش)
        except Exception:
            pass
        self._logo_timer = wx.CallLater(40, self._tick_logo)

    def _tick_ready_blink(self):
        self._ready_blink_timer = None
        if not self._alive or self._state != ("برنامه آماده استفاده است", "ok"):
            return
        if self._game_lite():
            self._ready_blink_on = True
            self._ready_blink_timer = wx.CallLater(1500, self._tick_ready_blink)
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
        return wx.Font(wx.FontInfo(max(6, int(round(size * _UI_SCALE)))).FaceName(UI_FONT_FACE).Bold(bold))

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
        is_back = name == "back" and self.page in self.SUB_PAGES
        if is_back or hot:
            g.SetPen(wx.TRANSPARENT_PEN)
            fill = _mix(ACCENT, (0, 0, 0), 0.12) if is_back and hot else (ACCENT if is_back else wx.Colour(54, 50, 60))
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
            # آبی آسمانی کم‌رنگ
            col = wx.Colour(118, 178, 224) if down else (wx.Colour(186, 226, 255) if hot else wx.Colour(158, 208, 245))
            fg = wx.Colour(14, 36, 58)
        elif name == "settings_net":
            # زرد گرم
            col = wx.Colour(206, 146, 22) if down else (wx.Colour(250, 200, 74) if hot else wx.Colour(238, 180, 42))
            fg = wx.Colour(44, 30, 4)
        elif name == "settings_theme":
            # آبی آسمانی
            col = wx.Colour(86, 164, 218) if down else (wx.Colour(150, 214, 252) if hot else wx.Colour(116, 190, 240))
            fg = wx.Colour(10, 34, 56)
        elif name == "settings":
            # قرمزِ گرم / شرابیِ مایل به روشن
            col = wx.Colour(138, 36, 62) if down else (wx.Colour(190, 70, 98) if hot else wx.Colour(168, 52, 80))
            fg = wx.WHITE
        elif name == "snip":
            # سبز کم‌رنگ‌تر (ثابت، مستقل از رنگ تم)
            col = wx.Colour(96, 190, 138) if down else (wx.Colour(168, 232, 196) if hot else wx.Colour(140, 214, 170))
            fg = wx.Colour(10, 40, 24)
        elif primary:
            col = _mix(ACCENT, (0, 0, 0), 0.18) if down else (_mix(ACCENT, (255, 255, 255), 0.18) if hot else ACCENT)
            fg = wx.WHITE
        else:
            col = wx.Colour(48, 52, 63) if down else (self.SURFACE_HOVER if hot else self.SURFACE)
            fg = TEXT
        g.SetPen(wx.Pen(col if name in ("settings", "about_me", "settings_net", "settings_theme") else (self.EDGE if not primary else col), 1) if name in ("settings", "browse_dir", "about_me", "settings_net", "settings_theme") else wx.TRANSPARENT_PEN)
        g.SetBrush(wx.Brush(col))
        g.DrawRoundedRectangle(r, S(8 if name in ("settings", "browse_dir", "about_me", "settings_net", "settings_theme") else 10))

        dc.SetFont(self._font(14 if name == "browse_dir" else 10, True))
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
        dc.SetFont(self._font(13, True))
        dc.SetTextForeground(TEXT)
        chip = wx.Rect(r.x + S(8), r.y + S(4), S(96), r.height - S(8))
        label_area = wx.Rect(chip.x + chip.width + S(8), r.y, max(1, r.x + r.width - S(10) - (chip.x + chip.width + S(8))), r.height)
        dc.DrawLabel(label, label_area, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)

        g.SetPen(wx.Pen(ACCENT if cap else self.EDGE, 1))
        g.SetBrush(wx.Brush(wx.Colour(88, 27, 38) if cap else wx.Colour(24, 27, 34)))
        g.DrawRoundedRectangle(chip, S(5))
        value = "…" if cap else str(self.app.cfg[key]).upper()
        dc.SetFont(self._font(12, True))
        dc.SetTextForeground(wx.WHITE if cap else wx.Colour(220, 224, 232))
        value = self._fit(dc, value, chip.width - S(8))
        tw, th = dc.GetTextExtent(value)
        dc.DrawText(value, chip.x + (chip.width - tw) // 2, chip.y + (chip.height - th) // 2)

    # ───────────── ناوبری بین صفحه‌ها (با پشته‌ی «صفحه‌ی قبل») ─────────────
    def _goto(self, page, push=True):
        if push and page != self.page:
            self._stack.append(self.page)
        self.page = page
        self.collapsed = False
        self._hover = None
        try:
            if page == "outmon":
                self.app.refresh_monitors()
            elif page == "offline":
                self.app.offline_probe()
            elif page == "net":
                wx.CallAfter(self.app.net_test)
        except Exception as exc:
            dbg("page enter failed: %s" % exc)
        self._areas = self._build()
        self._apply()
        self.Refresh(False)

    def _back(self):
        self._stop_back_blink()
        prev = self._stack.pop() if self._stack else "main"
        if prev == "main":
            self._tray_settings_force_top = False
        self._goto(prev, push=False)

    def rebuild(self):
        if self._alive:
            self._areas = self._build()
            self.Refresh(False)

    # ───────────── ابزارهای نقاشی صفحه‌های جدید ─────────────
    def _surface(self, g, r, hot=False, selected=False, radius=8):
        g.SetPen(wx.Pen(ACCENT if selected else (wx.Colour(91, 97, 112) if hot else self.EDGE), 1))
        g.SetBrush(wx.Brush(wx.Colour(58, 27, 36) if selected
                            else (self.SURFACE_HOVER if hot else self.SURFACE)))
        g.DrawRoundedRectangle(r, self._S(radius))

    def _text(self, dc, text, rect, color=None, size=10, bold=True, align=wx.ALIGN_CENTER):
        dc.SetFont(self._font(size, bold))
        dc.SetTextForeground(color or TEXT)
        dc.DrawLabel(self._fit(dc, str(text), max(1, rect.width - self._S(6))), rect,
                     align | wx.ALIGN_CENTER_VERTICAL)

    def _wrap(self, dc, text, maxw, max_lines):
        lines, cur = [], ""
        for word in str(text).split():
            trial = word if not cur else cur + " " + word
            if cur and dc.GetTextExtent(trial)[0] > maxw:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        if cur:
            lines.append(cur)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] = lines[-1] + " …"
        return [self._fit(dc, ln, maxw) for ln in lines]

    # رنگ ثابت دکمه‌های رنگی: (عادی، هاور، فشرده، متن)
    COLOR_BTNS = {
        "engine":      ((140, 214, 170), (168, 232, 196), (96, 190, 138), (10, 40, 24)),     # سبز «شروع ترجمه»
        "live":        ((140, 214, 170), (168, 232, 196), (96, 190, 138), (10, 40, 24)),
        "persian_ocr": ((238, 180, 42), (250, 200, 74), (206, 146, 22), (44, 30, 4)),        # زرد
        "outmon":      ((186, 132, 214), (206, 158, 232), (150, 98, 182), (36, 14, 52)),     # بنفشِ گرم
    }

    def _pill(self, g, dc, name, label, primary=False, selected=False, enabled=True, size=10):
        S, r = self._S, self._areas[name]
        hot = self._hover == name and enabled
        down = hot and self._press == name
        if name in self.COLOR_BTNS and enabled:
            c_n, c_h, c_d, c_f = self.COLOR_BTNS[name]
            g.SetPen(wx.TRANSPARENT_PEN)
            g.SetBrush(wx.Brush(wx.Colour(*(c_d if down else (c_h if hot else c_n)))))
            g.DrawRoundedRectangle(r, S(9))
            self._text(dc, label, r, wx.Colour(*c_f), size, True)
            return
        if primary:
            if not enabled:
                fill, fg = _mix(ACCENT, (30, 33, 41), 0.70), MUTED
            else:
                fill = _mix(ACCENT, (0, 0, 0), 0.18) if down else (_mix(ACCENT, (255, 255, 255), 0.18) if hot else ACCENT)
                fg = wx.WHITE
            g.SetPen(wx.TRANSPARENT_PEN)
            g.SetBrush(wx.Brush(fill))
            g.DrawRoundedRectangle(r, S(9))
        else:
            self._surface(g, r, hot, selected, 9)
            fg = TEXT if enabled else wx.Colour(100, 104, 116)
        self._text(dc, label, r, fg, size, True)

    def _tile(self, g, dc, name, label, active=False):
        self._pill(g, dc, name, label)
        if active:
            r, S = self._areas[name], self._S
            g.SetPen(wx.TRANSPARENT_PEN)
            g.SetBrush(wx.Brush(wx.Colour(20, 110, 70) if name == "live" else wx.Colour(52, 201, 142)))
            g.DrawCircle(r.x + S(12), r.y + r.height // 2, S(4))

    def _toggle_row(self, g, dc, name, label, on):
        """ردیف «برچسب + روشن/خاموش»؛ هم‌اندازه برای «حالت کم‌مصرف» و «کاهش انیمیشن»."""
        S, r = self._S, self._areas[name]
        self._surface(g, r, self._hover == name, False, 7)
        self._text(dc, label, wx.Rect(r.x + S(72), r.y, r.width - S(84), r.height), TEXT, 10, True, wx.ALIGN_RIGHT)
        self._text(dc, "روشن" if on else "خاموش", wx.Rect(r.x + S(14), r.y, S(54), r.height),
                   wx.Colour(52, 201, 142) if on else MUTED, 10, True)

    def _selector(self, g, dc, prev, value, nxt, text, arrow=17, size=11):
        S = self._S
        for name, glyph in ((prev, "‹"), (nxt, "›")):
            r = self._areas[name]
            hot = self._hover == name
            g.SetPen(wx.Pen(self.EDGE, 1))
            g.SetBrush(wx.Brush(self.SURFACE_HOVER if hot else self.SURFACE))
            g.DrawRoundedRectangle(r, S(6))
            dc.SetFont(self._font(arrow, True))
            dc.SetTextForeground(TEXT)
            tw, th = dc.GetTextExtent(glyph)
            dc.DrawText(glyph, r.x + (r.width - tw) // 2, r.y + (r.height - th) // 2 - S(1))
        mr = self._areas[value]
        hot = self._hover == value
        g.SetPen(wx.Pen(ACCENT if hot else self.EDGE, 1))
        g.SetBrush(wx.Brush(self.SURFACE_HOVER if hot else self.SURFACE))
        g.DrawRoundedRectangle(mr, S(6))
        self._text(dc, text, mr, TEXT, size, True)

    def _draw_state_line(self, g, dc, cy):
        S = self._S
        text, kind = self._state
        is_ready = text == "برنامه آماده استفاده است" and kind == "ok"
        col = {"ok": wx.Colour(52, 201, 142), "busy": self.AMBER, "err": self.RED}.get(kind, wx.Colour(52, 201, 142))
        if not is_ready or self._ready_blink_on:
            g.SetPen(wx.TRANSPARENT_PEN)
            g.SetBrush(wx.Brush(col))
            g.DrawCircle(S(17), cy, S(3))
        dc.SetFont(self._font(9))
        dc.SetTextForeground(wx.WHITE if is_ready and self._ready_blink_on
                             else (wx.Colour(91, 96, 108) if is_ready else MUTED))
        t = self._fit(dc, text, self._S(self.W) - S(42))
        dc.DrawText(t, S(28), cy - dc.GetTextExtent(t)[1] // 2)

    # ───────────── صفحه‌ی «موتور ترجمه» ─────────────
    def _draw_engine(self, g, dc, w, h):
        S = self._S
        self._text(dc, "روش ترجمه‌ی تصویر را انتخاب کنید", wx.Rect(S(12), S(42), w - S(24), S(24)),
                   MUTED, 10, True, wx.ALIGN_RIGHT)
        cur = self.app.cfg["engine"]
        rows = (
            ("engine_google", "google", "Google Translate", "آنلاین — بدون نیاز به کلید یا توکن", None),
            ("engine_ai", "ai", "ترجمه با Ai", "OpenAI / Gemini / OpenRouter", "engine_ai_cfg"),
            ("engine_offline", "offline", "ترجمه‌ی آفلاین", "OCR + مدل محلی — بدون اینترنت", "engine_offline_cfg"),
        )
        for name, key, title, sub, cfg_name in rows:
            r = self._areas[name]
            sel = cur == key
            self._surface(g, r, self._hover == name, sel, 9)
            cy, cx = r.y + r.height // 2, r.x + r.width - S(22)
            g.SetPen(wx.Pen(ACCENT if sel else MUTED, 2))
            g.SetBrush(wx.TRANSPARENT_BRUSH)
            g.DrawCircle(cx, cy, S(8))
            if sel:
                g.SetPen(wx.TRANSPARENT_PEN)
                g.SetBrush(wx.Brush(ACCENT))
                g.DrawCircle(cx, cy, S(4))
            left = r.x + (S(86) if cfg_name else S(10))
            tw = cx - S(14) - left
            self._text(dc, title, wx.Rect(left, r.y + S(5), tw, S(22)), TEXT, 12, True, wx.ALIGN_RIGHT)
            self._text(dc, sub, wx.Rect(left, r.y + S(27), tw, S(18)), MUTED, 9, False, wx.ALIGN_RIGHT)
            if cfg_name:
                self._pill(g, dc, cfg_name, "تنظیمات", size=9)
        warn = self.app.engine_warning()
        if warn:
            self._text(dc, warn, wx.Rect(S(12), S(236), w - S(24), S(20)), self.AMBER, 9, True, wx.ALIGN_RIGHT)
        self._text(dc, "زبان مقصد همیشه فارسی است", wx.Rect(S(12), S(258), w - S(24), S(20)),
                   MUTED, 9, False, wx.ALIGN_RIGHT)
        self._draw_state_line(g, dc, h - S(20))

    # ───────────── صفحه‌ی «هوش مصنوعی» ─────────────
    def _field_row(self, g, dc, name, label, value, value_color=None):
        S, r = self._S, self._areas[name]
        self._surface(g, r, self._hover == name, False, 7)
        label_w = S(100)
        self._text(dc, label, wx.Rect(r.x + r.width - label_w - S(6), r.y, label_w, r.height),
                   MUTED, 11, True, wx.ALIGN_RIGHT)
        self._text(dc, value, wx.Rect(r.x + S(6), r.y, r.width - label_w - S(18), r.height),
                   value_color or TEXT, 10, True, wx.ALIGN_LEFT)

    def _draw_ai(self, g, dc, w, h):
        S = self._S
        ai, prov = self.app.ai, self.app.ai["provider"]
        for key, label in AI_PROVIDERS:
            self._pill(g, dc, "ai_prov_" + key, label, selected=(prov == key), size=10)
        self._field_row(g, dc, "ai_model", "مدل", ai["models"].get(prov) or "—")
        o = self._ai_off()
        if o:
            self._field_row(g, dc, "ai_url", "آدرس سرور", self.app.cfg["ai_custom_url"] or "—")
        draft, saved = bool(ai["tokens"].get(prov)), self.app.ai_token_saved(prov)
        if self.app.cfg["stream_mode"]:
            tok_text, tok_col = "▇▇▇▇▇▇▇▇▇▇  (پوشانده — حالت استریم)", MUTED
        elif draft:
            tok_text, tok_col = "●●●●●●●●●●  (ذخیره‌نشده)", self.AMBER
        elif saved:
            tok_text, tok_col = "●●●●●●●●●●  (ذخیره‌شده)", wx.Colour(52, 201, 142)
        else:
            tok_text, tok_col = ("اختیاری (برای سرور محلی لازم نیست)", MUTED) if prov == "custom" else ("تنظیم نشده", MUTED)
        self._field_row(g, dc, "ai_token", "توکن API", tok_text, tok_col)
        style = self.app.cfg["ai_style"]
        for key, label in AI_STYLES:
            self._pill(g, dc, "ai_style_" + key, label, selected=(style == key), size=10)
        self._field_row(g, dc, "ai_game", "نام بازی", self.app.cfg["ai_game"] or "—")
        self._pill(g, dc, "ai_test", "بررسی اتصال", enabled=not ai["testing"])
        self._pill(g, dc, "ai_save", "ذخیره *" if ai["dirty"] else "ذخیره", primary=True)
        self._pill(g, dc, "ai_clear", "حذف توکن ذخیره‌شده", enabled=saved, size=9)

        card = wx.Rect(S(12), S(332 + o), w - S(24), S(56))
        g.SetPen(wx.Pen(self.EDGE, 1))
        g.SetBrush(wx.Brush(wx.Colour(24, 27, 34)))
        g.DrawRoundedRectangle(card, S(7))
        self._text(dc, "وضعیت اتصال", wx.Rect(card.x, card.y + S(3), card.width - S(6), S(16)),
                   MUTED, 9, True, wx.ALIGN_RIGHT)
        self._text(dc, self.app.ai_usage_text(prov), self._areas["ai_usage"],
                   TEXT if self._hover == "ai_usage" else MUTED, 8, False, wx.ALIGN_LEFT)
        msg, kind = ai["status"]
        col = {"ok": wx.Colour(52, 201, 142), "err": self.RED, "busy": self.AMBER}.get(kind, TEXT)
        dc.SetFont(self._font(10, True))
        dc.SetTextForeground(col)
        for i, line in enumerate(self._wrap(dc, msg, card.width - S(20), 2)):
            lw = dc.GetTextExtent(line)[0]
            dc.DrawText(line, card.x + card.width - S(10) - lw, card.y + S(22) + i * S(17))
        self._draw_state_line(g, dc, h - S(20))

    # ───────────── صفحه‌ی «ابزارها» و «تغییرات نسخه» ─────────────
    # ───────────── صفحه‌ی «ترجمه‌ی آفلاین» ─────────────
    def _draw_offline(self, g, dc, w, h):
        S = self._S
        off = self.app.off
        self._text(dc, "زبان متن داخل تصویر (OCR)", wx.Rect(S(12), S(42), w - S(24), S(24)),
                   MUTED, 10, True, wx.ALIGN_RIGHT)
        self._selector(g, dc, "ocr_prev", "ocr_value", "ocr_next", self.app.ocr_label())
        self._text(dc, "مدل ترجمه‌ی آفلاین (کیفیت / حجم)", wx.Rect(S(12), S(108), w - S(24), S(20)),
                   MUTED, 10, True, wx.ALIGN_RIGHT)
        self._selector(g, dc, "nllbm_prev", "nllbm_value", "nllbm_next", nllb_spec()["label"], arrow=15, size=10)
        dc.SetFont(self._font(9, False))
        dc.SetTextForeground(MUTED)
        for i, line in enumerate(self._wrap(dc, nllb_spec()["desc"], w - S(24), 2)):
            lw = dc.GetTextExtent(line)[0]
            dc.DrawText(line, w - S(12) - lw, S(168) + i * S(15))

        card = wx.Rect(S(12), S(196), w - S(24), S(78))
        g.SetPen(wx.Pen(self.EDGE, 1))
        g.SetBrush(wx.Brush(wx.Colour(24, 27, 34)))
        g.DrawRoundedRectangle(card, S(7))
        argos_map = {"ok": ("نصب شده ✓", True), "missing": ("نصب نشده", False),
                     "nolib": ("کتابخانه نصب نیست", False), "checking": ("در حال بررسی…", None),
                     "error": ("نامشخص", False)}
        a_txt, a_ok = argos_map.get(off["argos"], ("نامشخص", False))
        rows = (
            ("مدل OCR این زبان", "نصب شده ✓" if off["tess_model"] else "نصب نشده", bool(off["tess_model"])),
            ("موتور Tesseract", "پیدا شد ✓" if off["tess_exe"] else "پیدا نشد", bool(off["tess_exe"])),
            ("مدل ترجمه به فارسی", a_txt, a_ok),
        )
        for i, (label, value, ok) in enumerate(rows):
            y = card.y + S(5) + i * S(23)
            col = MUTED if ok is None else (wx.Colour(52, 201, 142) if ok else self.AMBER)
            self._text(dc, label, wx.Rect(card.x + card.width // 2, y, card.width // 2 - S(6), S(22)),
                       MUTED, 10, True, wx.ALIGN_RIGHT)
            self._text(dc, value, wx.Rect(card.x + S(6), y, card.width // 2 - S(10), S(22)),
                       col, 10, True, wx.ALIGN_LEFT)

        busy = off["busy"]
        paused = bool(off.get("paused"))
        all_ok = "ocr_download" not in self._areas
        if all_ok:
            self._text(dc, "✓ All models are installed", wx.Rect(S(12), S(282), w - S(24), S(38)),
                       wx.Colour(52, 201, 142), 10, True)
        else:
            self._pill(g, dc, "ocr_download", "در حال دانلود… %d٪" % int(off["progress"] * 100) if busy else "دانلود مدل‌ها",
                       primary=True, enabled=not busy and not paused)
            self._pill(g, dc, "ocr_pause", "ادامه" if paused else "توقف", enabled=busy or paused)
        stext = off.get("size_text") or ""
        if all_ok:
            stext = ""
        if off.get("argos") == "missing" and not busy:
            mt = "حجم دانلود مدل ترجمه: حدود %s" % fmt_mb(nllb_spec()["dl_mb"] * 1048576)
            stext = (stext + "  •  " + mt) if stext else mt
        if stext and not busy:
            self._text(dc, stext, wx.Rect(S(12), S(398), w - S(24), S(18)), MUTED, 9, False, wx.ALIGN_RIGHT)
        self._pill(g, dc, "ocr_overlay", "حالت متن روی متن: %s" % ("روشن" if self.app.cfg["text_over_text"] else "خاموش"),
                   selected=bool(self.app.cfg["text_over_text"]), size=9)
        if busy or off["progress"] > 0:
            bar = wx.Rect(S(12), S(328), w - S(24), S(8))
            g.SetPen(wx.TRANSPARENT_PEN)
            g.SetBrush(wx.Brush(wx.Colour(36, 40, 50)))
            g.DrawRoundedRectangle(bar, S(4))
            fill_w = int(bar.width * max(0.0, min(1.0, off["progress"])))
            if fill_w > 0:
                g.SetBrush(wx.Brush(ACCENT))
                g.DrawRoundedRectangle(wx.Rect(bar.x, bar.y, max(S(8), fill_w), bar.height), S(4))
        col = {"ok": wx.Colour(52, 201, 142), "err": self.RED, "busy": self.AMBER,
               "paused": self.AMBER}.get(off["kind"], MUTED)
        dc.SetFont(self._font(9, True))
        dc.SetTextForeground(col)
        for i, line in enumerate(self._wrap(dc, off["msg"], w - S(24), 3)):
            lw = dc.GetTextExtent(line)[0]
            dc.DrawText(line, w - S(12) - lw, S(342) + i * S(16))
        self._draw_state_line(g, dc, h - S(20))

    # ───────────── صفحه‌ی «ترجمه زنده بازی» ─────────────
    def _draw_live(self, g, dc, w, h):
        S = self._S
        app, cfg = self.app, self.app.cfg
        running = app.live.running
        code, text = app.live_state
        ok_col = wx.Colour(52, 201, 142)
        col = {"reading": ok_col, "translating": self.AMBER, "error": self.RED, "ready": self.AMBER}.get(code, MUTED)
        card = wx.Rect(S(12), S(42), w - S(24), S(62))
        g.SetPen(wx.Pen(self.EDGE, 1))
        g.SetBrush(wx.Brush(wx.Colour(24, 27, 34)))
        g.DrawRoundedRectangle(card, S(7))
        dc.SetFont(self._font(11, True))
        dc.SetTextForeground(col)
        for i, line in enumerate(self._wrap(dc, text, card.width - S(16), 2)):
            lw = dc.GetTextExtent(line)[0]
            dc.DrawText(line, card.x + card.width - S(8) - lw, card.y + S(4) + i * S(18))
        self._text(dc, app.live_roi_text(), wx.Rect(card.x, card.y + S(40), card.width - S(8), S(18)),
                   MUTED, 9, False, wx.ALIGN_RIGHT)
        self._pill(g, dc, "live_start", "توقف ترجمه زنده" if running else "شروع ترجمه زنده", primary=True)
        self._pill(g, dc, "live_roi", "انتخاب دوباره‌ی محدوده" if cfg["game_live_roi"] else "انتخاب محدوده‌ی زیرنویس",
                   size=9)
        rate = dict((k, lbl) for k, lbl, _ms in LIVE_RATES).get(cfg["game_live_rate"], "")
        rate_txt = {"low": "کم‌مصرف — تا حدود ۲٫۵ بررسی در ثانیه", "balanced": "متعادل — تا حدود ۵ بررسی در ثانیه",
                    "fast": "سریع — تا حدود ۹ بررسی در ثانیه"}.get(cfg["game_live_rate"], rate)
        self._selector(g, dc, "live_rate_prev", "live_rate_value", "live_rate_next", "سرعت: " + rate_txt, arrow=15, size=9)
        self._selector(g, dc, "live_font_prev", "live_font_value", "live_font_next",
                       "اندازه‌ی متن ترجمه: %d" % cfg["game_live_overlay_font_size"], arrow=15, size=10)
        self._selector(g, dc, "live_op_prev", "live_op_value", "live_op_next",
                       "شفافیت پنجره‌ی ترجمه: %d٪" % cfg["game_live_overlay_opacity"], arrow=15, size=10)
        self._toggle_row(g, dc, "live_src", "نمایش متن انگلیسی زیر ترجمه", bool(cfg["game_live_show_source"]))
        self._pill(g, dc, "live_dbg", "ذخیره‌ی تصویر محدوده و متن OCR (عیب‌یابی)", enabled=running, size=9)
        # متن OCR زنده + راهنمای انتخاب مدل
        seen = (getattr(app, "live_last_ocr", "") or "").strip()
        if running:
            ocr_line = ("OCR: " + seen[:60]) if seen else "OCR: هنوز متنی خوانده نشده — محدوده را روی زیرنویس بگذارید"
            self._text(dc, ocr_line, wx.Rect(S(12), S(358), w - S(24), S(18)),
                       ok_col if seen else self.AMBER, 9, False, wx.ALIGN_RIGHT)
        sel = nllb_spec()
        inst = nllb_installed()
        guide = ("مدل پیشنهادی برای ترجمه زنده: «Light & fast (600M)» + OCR انگلیسی. "
                 "بازی را روی Borderless Windowed بگذارید و محدوده را فقط دور زیرنویس بکشید.")
        gcard = wx.Rect(S(12), S(380), w - S(24), S(58))
        g.SetPen(wx.Pen(self.EDGE, 1))
        g.SetBrush(wx.Brush(wx.Colour(24, 27, 34)))
        g.DrawRoundedRectangle(gcard, S(7))
        dc.SetFont(self._font(9, False))
        dc.SetTextForeground(MUTED)
        for i, line in enumerate(self._wrap(dc, guide, gcard.width - S(16), 3)):
            lw = dc.GetTextExtent(line)[0]
            dc.DrawText(line, gcard.right - S(8) - lw, gcard.y + S(5) + i * S(16))
        if not inst:
            mtxt, mcol = "مدل ترجمه‌ی انتخابی نصب نیست — صفحه‌ی «ترجمه‌ی آفلاین» → دانلود", self.RED
        elif sel["short"] != "سبک":
            mtxt, mcol = "مدل فعلی سنگین‌تر از حد لازم برای بازی است؛ برای سرعت «Light & fast» را انتخاب کنید", self.AMBER
        else:
            mtxt, mcol = "✓ مدل مناسب ترجمه زنده انتخاب و نصب شده است", ok_col
        self._text(dc, mtxt, wx.Rect(S(12), S(442), w - S(24), S(18)), mcol, 9, True, wx.ALIGN_RIGHT)
        st = app.live_stats or {}
        if st:
            l1 = "خواندن: %d ms  •  ترجمه: %d ms  •  تا نمایش: %d ms  •  RAM: %d MB" % (
                st.get("ocr_ms", 0), st.get("tr_ms", 0), st.get("show_ms", 0), st.get("ram_mb", 0))
            l2 = "OCR در دقیقه: %d  •  فریم ثابت: %d  •  تکراری ردشده: %d  •  کش: %d  •  خطا: %d" % (
                st.get("ocr_per_min", 0), st.get("skip_n", 0), st.get("dups", 0), st.get("cache_hits", 0),
                st.get("errors", 0))
            for i, ln in enumerate((l1, l2)):
                self._text(dc, ln, wx.Rect(S(12), S(462) + i * S(17), w - S(24), S(17)), MUTED, 8, False, wx.ALIGN_RIGHT)
        self._draw_state_line(g, dc, h - S(20))

    # ───────────── صفحه‌ی «شبکه و VPN» ─────────────
    def _draw_net(self, g, dc, w, h):
        S = self._S
        mode = self.app.cfg["proxy_mode"]
        for key, label in (("system", "سیستم / VPN"), ("custom", "پروکسی دستی"), ("off", "مستقیم")):
            self._pill(g, dc, "net_mode_" + key, label, selected=(mode == key), size=10)
        self._field_row(g, dc, "net_url", "آدرس پروکسی", self.app.cfg["proxy_url"] or "—",
                        None if mode == "custom" else MUTED)
        net = self.app.net
        self._pill(g, dc, "net_test", "بررسی اتصال", enabled=not net["testing"])
        self._pill(g, dc, "net_restart", "اعمال (راه‌اندازی مجدد)", primary=net["dirty"], enabled=net["dirty"], size=9)
        card = wx.Rect(S(12), S(174), w - S(24), S(58))
        g.SetPen(wx.Pen(self.EDGE, 1))
        g.SetBrush(wx.Brush(wx.Colour(24, 27, 34)))
        g.DrawRoundedRectangle(card, S(7))
        self._text(dc, "وضعیت اتصال", wx.Rect(card.x, card.y + S(3), card.width - S(6), S(16)),
                   MUTED, 9, True, wx.ALIGN_RIGHT)
        msg, kind = net["status"]
        if msg:                                   # فقط: فعال است / فعال نیست (و هنگام بررسی «در حال بررسی…»)
            col = {"ok": wx.Colour(52, 201, 142), "err": self.RED, "busy": self.AMBER}.get(kind, TEXT)
            self._text(dc, msg, wx.Rect(card.x, card.y + S(22), card.width - S(10), S(30)),
                       col, 13, True, wx.ALIGN_RIGHT)
        self._draw_state_line(g, dc, h - S(20))

    # ───────────── صفحه‌ی «راهنمای شروع» (هم‌تم برنامه) ─────────────
    def _draw_welcome(self, g, dc, w, h):
        S = self._S
        step = getattr(self, "wstep", 0)
        titles = ("کلیدهای میانبر", "موتور ترجمه", "رنگ و فونت")
        solo = getattr(self, "wsolo", False)
        if not solo:
            self._text(dc, "صفحه %d از 3 — %s" % (step + 1, titles[step]), wx.Rect(S(12), S(40), w - S(24), S(26)),
                       ACCENT, 12, True, wx.ALIGN_RIGHT)
        cfg = self.app.cfg
        if step == 0:
            rows = ((cfg["snip_hotkey"].upper(), "انتخاب ناحیه و ترجمه"),
                    (cfg["close_hotkey"].upper(), "بستن نتیجه"),
                    ("ESC", "لغو انتخاب ناحیه"),
                    ("اسکرول موس", "بزرگ/کوچک‌کردن نتیجه"),
                    ("دابل‌کلیک", "کپی نتیجه"))
            for i, (k, d) in enumerate(rows):
                y = S(72) + i * S(38)
                chip = wx.Rect(S(12), y, S(110), S(32))
                self._surface(g, chip, False, False, 8)
                self._text(dc, k, chip, ACCENT, 11, True)
                self._text(dc, d, wx.Rect(S(130), y, w - S(142), S(32)), TEXT, 11, True, wx.ALIGN_RIGHT)
            hint = "کلیدها قابل تغییرند."
        elif step == 1:
            labels = {"google": "Google Translate — بدون تنظیمات",
                      "ai": "ترجمه با Ai — OpenAI / Gemini / OpenRouter",
                      "offline": "آفلاین — OCR + مدل محلی"}
            for key in ("google", "ai", "offline"):
                self._pill(g, dc, "w_eng_" + key, labels[key], selected=(cfg["engine"] == key), size=10)
            hint = "هوش مصنوعی به توکن نیاز دارد و آفلاین به دانلودکردن مدل ترجمه."
        else:
            self._text(dc, "انتخاب تم برنامه", wx.Rect(S(12), S(72), w - S(24), S(22)), MUTED, 10, True, wx.ALIGN_RIGHT)
            cur = cfg["accent"].lower()
            for i, (_n, hx) in enumerate(THEME_COLORS):
                r = self._areas["w_col_%d" % i]
                v = int(hx[1:], 16)
                g.SetPen(wx.Pen(wx.WHITE if hx.lower() == cur else self.EDGE, 3 if hx.lower() == cur else 1))
                g.SetBrush(wx.Brush(wx.Colour((v >> 16) & 255, (v >> 8) & 255, v & 255)))
                g.DrawEllipse(r)
            self._text(dc, "فونت", wx.Rect(S(12), S(146), w - S(24), S(22)), MUTED, 10, True, wx.ALIGN_RIGHT)
            for i, face in enumerate(available_fonts()):
                name = "w_font_%d" % i
                r = self._areas[name]
                sel = face == cfg["font_face"]
                self._surface(g, r, self._hover == name, sel, 8)
                dc.SetFont(wx.Font(wx.FontInfo(10).FaceName(face).Bold(True)))
                dc.SetTextForeground(TEXT)
                dc.DrawLabel(face, r, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
            prev = wx.Rect(S(12), S(262), w - S(24), S(40))
            self._surface(g, prev, False, False, 8)
            self._text(dc, "نمونه: ترجمه‌ی متن روی صفحه — Hello", prev, ACCENT, 12, True)
            hint = "" if getattr(self, "wsolo", False) else "رنگ و فونت بعداً هم از «تنظیمات ← رنگ و فونت» قابل تغییر است."
        dc.SetFont(self._font(9, False))
        dc.SetTextForeground(MUTED)
        top = (S(298), S(250), S(310))[step]
        for i, line in enumerate(self._wrap(dc, hint, w - S(24), 3)):
            lw = dc.GetTextExtent(line)[0]
            dc.DrawText(line, w - S(12) - lw, top + i * S(15))
        if not solo:
            for i in range(3):
                g.SetPen(wx.TRANSPARENT_PEN)
                g.SetBrush(wx.Brush(ACCENT if i == step else self.EDGE))
                g.DrawCircle(w // 2 + (i - 1) * S(14), S(342), S(3))
            self._pill(g, dc, "w_prev", "قبلی", enabled=step > 0)
        self._pill(g, dc, "w_next", "ذخیره" if step == 2 else "بعدی", primary=True)

    # ───────────── صفحه‌ی «مانیتور خروجی» ─────────────
    def _draw_outmon(self, g, dc, w, h):
        S = self._S
        self._text(dc, "نتیجه‌ی ترجمه روی کدام مانیتور نمایش داده شود؟",
                   wx.Rect(S(12), S(42), w - S(24), S(24)), MUTED, 10, True, wx.ALIGN_RIGHT)
        box = wx.Rect(S(12), S(70), w - S(24), S(120))
        g.SetPen(wx.Pen(self.EDGE, 1))
        g.SetBrush(wx.Brush(wx.Colour(14, 16, 21)))
        g.DrawRoundedRectangle(box, S(8))
        try:
            out = int(self.app.cfg["output_monitor"] or 0)
            cap = int(self.app.cfg["capture_monitor"] or 0)
        except Exception:
            out = cap = 0
        mons = getattr(self.app, "_monitor_rects_cache", None) or list_monitor_rects()
        for i, r in self._monitor_tiles():
            name = "outmon_m%d" % i
            if name not in self._areas:
                continue
            sel, hot = out == i, self._hover == name
            g.SetPen(wx.Pen(ACCENT if sel else (wx.Colour(91, 97, 112) if hot else self.EDGE), 2 if sel else 1))
            g.SetBrush(wx.Brush(_mix(ACCENT, (18, 20, 26), 0.55) if sel else (self.SURFACE_HOVER if hot else self.SURFACE)))
            g.DrawRoundedRectangle(r, S(5))
            self._text(dc, str(i), wx.Rect(r.x, r.y, r.width, r.height - (S(14) if r.height > S(44) else 0)),
                       wx.WHITE, 16, True)
            if r.height > S(44) and i - 1 < len(mons):
                self._text(dc, "%d×%d" % (mons[i - 1][2], mons[i - 1][3]),
                           wx.Rect(r.x, r.y + r.height - S(18), r.width, S(14)), MUTED, 8, False)
            if cap == i:
                self._text(dc, "عکس‌برداری", wx.Rect(r.x, r.y + S(2), r.width, S(14)), self.AMBER, 8, True)

        same = self._areas["outmon_same"]
        self._surface(g, same, self._hover == "outmon_same", out == 0, 8)
        cx, cy = same.x + same.width - S(20), same.y + same.height // 2
        g.SetPen(wx.Pen(ACCENT if out == 0 else MUTED, 2))
        g.SetBrush(wx.TRANSPARENT_BRUSH)
        g.DrawCircle(cx, cy, S(7))
        if out == 0:
            g.SetPen(wx.TRANSPARENT_PEN)
            g.SetBrush(wx.Brush(ACCENT))
            g.DrawCircle(cx, cy, S(3))
        self._text(dc, "همان مانیتور عکس‌برداری (پیش‌فرض)",
                   wx.Rect(same.x + S(6), same.y, same.width - S(36), same.height), TEXT, 10, True, wx.ALIGN_RIGHT)
        self._text(dc, "جای نمایش روی مانیتور", wx.Rect(S(12), S(238), w - S(24), S(20)),
                   MUTED, 10, True, wx.ALIGN_RIGHT)
        cur_corner = self.app.cfg["output_corner"]
        for key, label in CORNERS:
            self._pill(g, dc, "outcorner_" + key, label, selected=(cur_corner == key), size=9)
        self._pill(g, dc, "outmon_test", "نمایش آزمایشی روی مانیتور خروجی")
        self._text(dc, "خروجی فعلی: " + self.app.out_label(), wx.Rect(S(12), S(374), w - S(24), S(20)),
                   MUTED, 9, False, wx.ALIGN_RIGHT)
        self._draw_state_line(g, dc, h - S(20))

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
        dc = _BidiDC(dc)
        g = dc


        g.SetPen(wx.Pen(self.EDGE, 1))
        g.SetBrush(wx.TRANSPARENT_BRUSH)
        g.DrawRoundedRectangle(0, 0, max(1, w - 1), max(1, h - 1), S(12))
        g.SetPen(wx.TRANSPARENT_PEN)
        g.SetBrush(wx.Brush(ACCENT))
        g.DrawRectangle(S(1), S(1), max(1, w - S(2)), S(2))


        if self.page == "main" and not self.collapsed:
            ph = (time.time() % 4.2) / 4.2                       # چشمک آرام و نرم: محو و روشن‌شدن با منحنی هموار
            sm = 0.5 - 0.5 * math.cos(2 * math.pi * ph)
            sm = sm * sm * (3.0 - 2.0 * sm)
            pulse = 0.40 + 0.60 * sm
            brand = make_brand_bitmap(S(168), S(168), pulse)
            if brand.IsOk():
                dc.DrawBitmap(brand, S(6), S(6), True)
            dc.SetFont(self._font(24, True))
            dc.SetTextForeground(wx.WHITE)
            dc.DrawText("Translator", S(184), S(56))
            dc.SetFont(self._font(16, True))
            dc.SetTextForeground(wx.Colour(203, 208, 218))
            dc.DrawLabel("ترجمه سریع متون", wx.Rect(S(184), S(96), w - S(196), S(30)),
                         wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        else:
            brand = make_brand_bitmap(S(24), S(24))
            if brand.IsOk():
                dc.DrawBitmap(brand, S(7), S(6), True)
            dc.SetFont(self._font(12 if self.page in self.SUB_PAGES else 9, True))
            title = self.PAGE_TITLES.get(self.page, "Translator")
            if self.page == "welcome" and self.wsolo:
                title = "رنگ و فونت"
            dc.SetTextForeground(TEXT if self.page != "about" else wx.WHITE)
            if self.page == "about":
                dc.SetFont(self._font(10, True))
            if self.page in self.SUB_PAGES and "back" in self._areas:
                title = self._fit(dc, title, max(S(40), self._areas["back"].x - S(36) - S(6)))
            dc.DrawText(title, S(36), (S(36) - dc.GetTextExtent(title)[1]) // 2 + S(1))
        self._pin_btn(g, dc)
        self._icon_btn(g, dc, "collapse", "+" if self.collapsed else "–")
        self._icon_btn(g, dc, "hide", "✕")
        if self.page in self.SUB_PAGES:
            self._icon_btn(g, dc, "back", "‹ صفحه قبل")
        if self.collapsed:
            return

        if self.page == "settings":
            self._settings_key_row(g, dc, "settings_snip_key", "کلید ترجمه", "snip_hotkey")
            self._settings_key_row(g, dc, "settings_close_key", "کلید بستن نتیجه", "close_hotkey")

            dc.SetFont(self._font(13, True))
            dc.SetTextForeground(MUTED)
            dc.DrawLabel("پوشه‌ی ذخیره‌ی تصویرها", wx.Rect(S(12), S(119), w - S(24), S(23)),
                         wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
            dc.SetFont(self._font(12, True))
            dc.SetTextForeground(wx.Colour(220, 224, 232))
            path = _short_path(str(self.app.cfg["save_dir"]), 38)
            path = self._fit(dc, path, w - S(24))
            dc.DrawLabel(path, wx.Rect(S(12), S(142), w - S(24), S(22)),
                         wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

            self._btn(g, dc, "browse_dir", "انتخاب پوشه", primary=False)

            dc.SetFont(self._font(13, True))
            dc.SetTextForeground(MUTED)
            dc.DrawLabel("تنظیمات مانیتور برای اسکرین گرفتن", wx.Rect(S(12), S(211), w - S(24), S(23)),
                         wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
            for name, arrow in (("monitor_prev", "‹"), ("monitor_next", "›")):
                r = self._areas[name]
                hot = self._hover == name
                g.SetPen(wx.Pen(self.EDGE, 1))
                g.SetBrush(wx.Brush(self.SURFACE_HOVER if hot else self.SURFACE))
                g.DrawRoundedRectangle(r, S(6))
                dc.SetFont(self._font(15, True))
                dc.SetTextForeground(TEXT)
                tw, th = dc.GetTextExtent(arrow)
                dc.DrawText(arrow, r.x + (r.width - tw) // 2, r.y + (r.height - th) // 2 - S(1))
            mr = self._areas["monitor_value"]
            g.SetPen(wx.Pen(ACCENT if self._hover == "monitor_value" else self.EDGE, 1))
            g.SetBrush(wx.Brush(self.SURFACE_HOVER if self._hover == "monitor_value" else self.SURFACE))
            g.DrawRoundedRectangle(mr, S(6))
            dc.SetFont(self._font(13, True))
            dc.SetTextForeground(TEXT)
            monitor_label = self._fit(dc, self._monitor_label(), mr.width - S(8))
            dc.DrawLabel(monitor_label, mr, wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)

            self._btn(g, dc, "settings_net", "تنظیمات شبکه", primary=False)
            self._btn(g, dc, "settings_theme", "رنگ و فونت", primary=False)
            self._toggle_row(g, dc, "performance_mode", "حالت کم‌مصرف", bool(self.app.cfg["performance_mode"]))
            self._toggle_row(g, dc, "tools_lite", "کاهش انیمیشن هنگام بازی", bool(self.app.cfg["game_lite_ui"]))
            self._toggle_row(g, dc, "stream_mode", "حالت استریم (پنل و توکن پنهان)", bool(self.app.cfg["stream_mode"]))
            self._selector(g, dc, "scale_prev", "scale_value", "scale_next",
                           "اندازه‌ی رابط: %d٪" % int(self.app.cfg["ui_scale"]), arrow=15, size=10)
            self._pill(g, dc, "tools_import", "وارد کردن تنظیمات", size=9)
            self._pill(g, dc, "tools_export", "ذخیره‌ی تنظیمات", size=9)
            self._text(dc, "نسخه %s" % APP_VERSION, wx.Rect(S(12), S(532), w - S(24), S(22)),
                       MUTED, 9, True, wx.ALIGN_RIGHT)

            text, kind = self._state
            is_ready = text == "برنامه آماده استفاده است" and kind == "ok"
            col = {"ok": wx.Colour(52, 201, 142), "busy": self.AMBER, "err": self.RED}.get(kind, wx.Colour(52, 201, 142))
            if not is_ready or self._ready_blink_on:
                g.SetPen(wx.TRANSPARENT_PEN)
                g.SetBrush(wx.Brush(col))
                g.DrawCircle(S(17), h - S(32), S(3))
            dc.SetFont(self._font(12))
            dc.SetTextForeground(wx.WHITE if is_ready and self._ready_blink_on else (wx.Colour(91, 96, 108) if is_ready else MUTED))
            dc.DrawText(self._fit(dc, text, w - S(42)), S(28), h - S(38))
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

        if self.page in ("engine", "ai", "offline", "outmon", "net", "welcome", "live"):
            getattr(self, "_draw_" + self.page)(g, dc, w, h)
            return

        self._btn(g, dc, "snip", "شروع ترجمه", primary=True)
        engine = self.app.cfg["engine"]
        self._tile(g, dc, "engine", "موتور ترجمه")
        self._tile(g, dc, "outmon", "مانیتور خروجی",
                   active=(int(self.app.cfg["output_monitor"] or 0) > 0))
        self._btn(g, dc, "settings", "تنظیمات", primary=False)
        self._btn(g, dc, "about_me", "درباره توسعه دهنده", primary=False)
        self._tile(g, dc, "live", "ترجمه زنده بازی", active=self.app.live.running)
        self._pill(g, dc, "persian_ocr", "استخراج متن فارسی از عکس یا پی دی اف", size=9)

        text, kind = self._state
        is_ready = text == "برنامه آماده استفاده است" and kind == "ok"
        col = {"ok": wx.Colour(52, 201, 142), "busy": self.AMBER, "err": self.RED}.get(kind, wx.Colour(52, 201, 142))
        qa = self._areas["quit"]
        cy = qa.y + qa.height // 2                      # دقیقاً روبه‌روی دکمه‌ی «خروج کامل از برنامه» (سمت چپ)
        if not is_ready or self._ready_blink_on:
            g.SetPen(wx.TRANSPARENT_PEN)
            g.SetBrush(wx.Brush(col))
            g.DrawCircle(S(17), cy, S(4))
        dc.SetFont(self._font(9))
        dc.SetTextForeground(wx.WHITE if is_ready and self._ready_blink_on else (wx.Colour(91, 96, 108) if is_ready else MUTED))
        t = self._fit(dc, text, max(S(60), qa.x - S(28) - S(8)))
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
        elif name in ("settings", "engine", "ai", "offline", "outmon", "live"):
            self._goto(name)
        elif name == "live_start":
            self.app.live_toggle()
        elif name == "live_roi":
            self.app.live_select_roi()
        elif name in ("live_rate_prev", "live_rate_next", "live_rate_value"):
            self.app.live_change_rate(-1 if name == "live_rate_prev" else 1)
        elif name in ("live_font_prev", "live_font_next", "live_font_value"):
            self.app.live_change_font(-1 if name == "live_font_prev" else 1)
        elif name in ("live_op_prev", "live_op_next", "live_op_value"):
            self.app.live_change_opacity(-1 if name == "live_op_prev" else 1)
        elif name == "live_src":
            self.app.live_toggle_source()
        elif name == "live_dbg":
            self.app.live_request_dump()
        elif name in ("nllbm_prev", "nllbm_next", "nllbm_value"):
            self.app.change_nllb_model(-1 if name == "nllbm_prev" else 1)
        elif name == "settings_net":
            self._goto("net")
        elif name == "settings_theme":
            self.wsolo = True
            self.wstep = 2
            self.rebuild()
            self._goto("welcome")
        elif name == "about_me":
            self._goto("about")
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
        elif name in ("scale_prev", "scale_next", "scale_value"):
            self.app.change_ui_scale(-10 if name == "scale_prev" else 10, wrap=(name == "scale_value"))
        elif name == "tools_lite":
            self.app.toggle_game_lite()
        elif name == "persian_ocr":
            self.app.persian_ocr_start()
        elif name == "stream_mode":
            self.app.toggle_stream_mode()
        elif name == "tools_export":
            self.app.export_settings()
        elif name == "tools_import":
            self.app.import_settings()
        elif name == "ai_url":
            self.app.ai_edit_url()
        elif name == "ai_usage":
            self.app.ai_usage_reset()
        elif name == "back":
            self._back()
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
        elif name == "engine_ai_cfg":
            self._goto("ai")
        elif name == "engine_offline_cfg":
            self._goto("offline")
        elif name in ("engine_google", "engine_ai", "engine_offline"):
            self.app.set_engine(name[7:])
        elif name.startswith("ai_prov_"):
            self.app.ai_set_provider(name[8:])
        elif name.startswith("ai_style_"):
            self.app.ai_set_style(name[9:])
        elif name == "ai_game":
            self.app.ai_edit_context("game")
        elif name == "ai_model":
            self.app.ai_edit_model()
        elif name == "ai_token":
            self.app.ai_edit_token()
        elif name == "ai_save":
            self.app.ai_save()
        elif name == "ai_test":
            self.app.ai_test()
        elif name == "ai_clear":
            self.app.ai_clear_token()
        elif name in ("ocr_prev", "ocr_next", "ocr_value"):
            self.app.change_ocr_lang(-1 if name == "ocr_prev" else 1)
        elif name == "ocr_download":
            self.app.offline_download()
        elif name == "ocr_pause":
            self.app.offline_pause()
        elif name == "ocr_overlay":
            self.app.cfg.set("text_over_text", not self.app.cfg["text_over_text"])
            if self.app.cfg["text_over_text"] and self.app.cfg["engine"] != "offline":
                self.app.set_engine("offline")           # این حالت فقط با موتور آفلاین کار می‌کند
                self.app.panel.set_state("حالت متن روی متن روشن شد و موتور روی «آفلاین» رفت", "ok", 4500)
            self.refresh()
        elif name.startswith("net_mode_"):
            self.app.net_set_mode(name[9:])
        elif name == "net_url":
            self.app.net_edit_url()
        elif name == "net_test":
            self.app.net_test()
        elif name == "net_restart":
            self.app.restart_app()
        elif name == "w_next":
            if self.wstep < 2:
                self.wstep += 1
                self.rebuild()
            else:
                self._back()
        elif name == "w_prev":
            if self.wstep > 0:
                self.wstep -= 1
                self.rebuild()
        elif name.startswith("w_eng_"):
            self.app.set_engine(name[6:])
        elif name.startswith("w_col_"):
            self.app.set_theme(accent=THEME_COLORS[int(name[6:])][1])
        elif name.startswith("w_font_"):
            self.app.set_theme(font=available_fonts()[int(name[7:])])
        elif name == "outmon_same":
            self.app.set_output_monitor(0)
        elif name.startswith("outcorner_"):
            self.app.set_output_corner(name[10:])
        elif name == "outmon_test":
            self.app.test_output_monitor()
        elif name.startswith("outmon_m"):
            self.app.set_output_monitor(int(name[8:]))
        elif name == "snip":
            self.app.start_snip()
        elif name == "quit":
            self.app.quit(force=True)
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


class _FlatBtn(wx.Panel):
    """دکمه‌ی تخت هم‌تم برنامه (به‌جای دکمه‌ی سفید ویندوز)."""

    def __init__(self, parent, label, primary, on_click, s):
        super().__init__(parent, size=(int(112 * s), int(36 * s)))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self._label, self._primary, self._cb, self._s = label, primary, on_click, s
        self._hot = self._down = False
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_ENTER_WINDOW, lambda e: (setattr(self, "_hot", True), self.Refresh(False)))
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: (setattr(self, "_hot", False), setattr(self, "_down", False), self.Refresh(False)))
        self.Bind(wx.EVT_LEFT_DOWN, lambda e: (setattr(self, "_down", True), self.Refresh(False)))
        self.Bind(wx.EVT_LEFT_UP, self._on_up)

    def _on_up(self, _e):
        was = self._down
        self._down = False
        self.Refresh(False)
        if was and self._hot:
            self._cb()

    def _on_paint(self, _e):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(FloatingPanel.BASE))
        dc.Clear()
        w, h = self.GetClientSize()
        if self._primary:
            fill = _mix(ACCENT, (0, 0, 0), 0.18) if self._down else (_mix(ACCENT, (255, 255, 255), 0.18) if self._hot else ACCENT)
            edge, fg = fill, wx.WHITE
        else:
            fill = FloatingPanel.SURFACE_HOVER if self._hot else FloatingPanel.SURFACE
            edge, fg = (ACCENT if self._hot else FloatingPanel.EDGE), TEXT
        dc.SetPen(wx.Pen(edge, 1))
        dc.SetBrush(wx.Brush(fill))
        dc.DrawRoundedRectangle(0, 0, w, h, int(7 * self._s))
        dc.SetFont(wx.Font(wx.FontInfo(10).FaceName(UI_FONT_FACE).Bold()))
        dc.SetTextForeground(fg)
        dc.DrawLabel(self._label, wx.Rect(0, 0, w, h), wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)


class ThemedAskDialog(wx.Dialog):
    """پنجره‌ی ورود متن هم‌تم برنامه (تیره، بدون نوار عنوان ویندوز، رنگ و فونت انتخابی کاربر)."""

    def __init__(self, title, prompt, value="", password=False):
        super().__init__(None, title=title, style=wx.STAY_ON_TOP | wx.BORDER_NONE)
        try:
            s = _system_dpi_scale()
        except Exception:
            s = 1.0
        self._s = s
        S = lambda v: int(round(v * s))
        P = FloatingPanel
        self._title = title
        self.SetBackgroundColour(P.BASE)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        try:
            self.SetLayoutDirection(wx.Layout_LeftToRight)
        except Exception:
            pass
        width = S(400)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(S(44))
        label = wx.StaticText(self, label=prompt)
        label.SetForegroundColour(MUTED)
        label.SetBackgroundColour(P.BASE)
        label.SetFont(wx.Font(wx.FontInfo(9).FaceName(UI_FONT_FACE)))
        label.Wrap(width - S(40))
        sizer.Add(label, 0, wx.LEFT | wx.RIGHT, S(20))
        sizer.AddSpacer(S(10))
        box = wx.Panel(self)
        box.SetBackgroundColour(P.SURFACE)
        inner = wx.BoxSizer(wx.VERTICAL)
        self.tc = wx.TextCtrl(box, value=value, style=wx.BORDER_NONE | wx.TE_PROCESS_ENTER | (wx.TE_PASSWORD if password else 0))
        self.tc.SetBackgroundColour(P.SURFACE)
        self.tc.SetForegroundColour(TEXT)
        self.tc.SetFont(wx.Font(wx.FontInfo(11).FaceName(UI_FONT_FACE)))
        inner.Add(self.tc, 1, wx.ALL | wx.EXPAND, S(9))
        box.SetSizer(inner)
        box.Bind(wx.EVT_PAINT, lambda e: self._paint_field(box))
        sizer.Add(box, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, S(20))
        sizer.AddSpacer(S(16))
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.AddStretchSpacer(1)
        row.Add(_FlatBtn(self, "انصراف", False, lambda: self.EndModal(wx.ID_CANCEL), s), 0)
        row.AddSpacer(S(10))
        row.Add(_FlatBtn(self, "تأیید", True, lambda: self.EndModal(wx.ID_OK), s), 0)
        sizer.Add(row, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, S(20))
        sizer.AddSpacer(S(18))
        self.SetSizer(sizer)
        self.SetMinSize((width, -1))
        self.SetSize((width, -1))
        self.Fit()
        self.SetSize((width, self.GetSize().height))
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.tc.Bind(wx.EVT_TEXT_ENTER, lambda e: self.EndModal(wx.ID_OK))
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key)
        self.Bind(wx.EVT_LEFT_DOWN, self._drag_start)
        self.Bind(wx.EVT_MOTION, self._drag_move)
        self.Bind(wx.EVT_LEFT_UP, self._drag_end)
        self._drag = None
        w, h = self.GetSize()
        round_corners(self, w, h, S(12))

    def _paint_field(self, box):
        dc = wx.PaintDC(box)
        w, h = box.GetClientSize()
        dc.SetBackground(wx.Brush(FloatingPanel.SURFACE))
        dc.Clear()
        dc.SetPen(wx.Pen(ACCENT if self.tc.HasFocus() else FloatingPanel.EDGE, 1))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(0, 0, w, h)

    def _on_paint(self, _e):
        dc = wx.AutoBufferedPaintDC(self)
        S = lambda v: int(round(v * self._s))
        w, h = self.GetClientSize()
        dc.SetBackground(wx.Brush(FloatingPanel.BASE))
        dc.Clear()
        dc.SetPen(wx.Pen(FloatingPanel.EDGE, 1))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRoundedRectangle(0, 0, max(1, w - 1), max(1, h - 1), S(12))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(ACCENT))
        dc.DrawRectangle(S(1), S(1), max(1, w - S(2)), S(2))
        logo = make_brand_bitmap(S(24), S(24))
        if logo.IsOk():
            dc.DrawBitmap(logo, S(14), S(10), True)
        dc.SetFont(wx.Font(wx.FontInfo(12).FaceName(UI_FONT_FACE).Bold()))
        dc.SetTextForeground(TEXT)
        dc.DrawLabel(self._title, wx.Rect(S(44), S(8), w - S(60), S(28)), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

    def _on_key(self, e):
        if e.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            e.Skip()

    def _drag_start(self, e):
        self._drag = wx.GetMousePosition() - self.GetPosition()
        self.CaptureMouse()

    def _drag_move(self, e):
        if self._drag is not None and e.Dragging() and e.LeftIsDown():
            self.Move(wx.GetMousePosition() - self._drag)

    def _drag_end(self, e):
        if self.HasCapture():
            self.ReleaseMouse()
        self._drag = None


_PREREQ_MANAGED = True
PREREQ_FA = {"wv2": "Microsoft Edge WebView2 Runtime", "vc": "Microsoft Visual C++ Redistributable"}


def _prereq_ok(key):
    return _webview2_installed() if key == "wv2" else _vcruntime_ok()


def _prereq_spec(key):
    """(نام، آدرس، فایل موقت، آرگومان نصب بی‌صدا). نسخه بر اساس ویندوز کاربر انتخاب می‌شود:
    بوت‌استرپر WebView2 خودش نسخه‌ی سازگار با همان ویندوز را می‌گیرد (ویندوز ۷/۸ فقط تا ۱۰۹)؛ VC++ هم نسخه‌ی معماری و ویندوز."""
    try:
        build = int(sys.getwindowsversion().build)
    except Exception:
        build = 19041
    if key == "wv2":
        return (PREREQ_FA[key], WEBVIEW2_URL, "MicrosoftEdgeWebview2Setup.exe", ["/silent", "/install"])
    import platform
    m = (platform.machine() or "").lower()
    arch = "arm64" if "arm" in m else ("x64" if ctypes.sizeof(ctypes.c_void_p) == 8 else "x86")
    ver = "17" if build >= 10240 else "16"                  # vs/16 آخرین نسخه‌ی پشتیبان ویندوز ۷/۸
    return (PREREQ_FA[key], "https://aka.ms/vs/%s/release/vc_redist.%s.exe" % (ver, arch),
            "vc_redist_%s.exe" % arch, ["/install", "/quiet", "/norestart"])


class PrereqInstaller(object):
    """دانلود با درصد + توقف/ادامه از نقطه‌ی توقف (فایل .part) + نصب بی‌صدا + راستی‌آزمایی."""

    def __init__(self, keys, on_prog, on_done):
        self.keys, self.on_prog, self.on_done = list(keys), on_prog, on_done
        self.ctl = DownloadCtl()
        self._resume = threading.Event()
        self._resume.set()
        self.paused = False
        self.cancelled = False

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def pause(self):
        self.paused = True
        self._resume.clear()
        self.ctl.pause = True

    def resume(self):
        self.paused = False
        self.ctl.pause = False
        self._resume.set()

    def cancel(self):
        self.cancelled = True
        self.ctl.pause = True
        self._resume.set()

    def _run(self):
        import subprocess
        results, n = [], max(1, len(self.keys))
        try:
            for i, key in enumerate(self.keys):
                name, url, fname, args = _prereq_spec(key)
                dest = os.path.join(tempfile.gettempdir(), fname)
                for stale in (dest, dest + ".part", dest + ".part.json"):
                    try:
                        os.remove(stale)
                    except Exception:
                        pass

                def prog(done, total, i=i, name=name):
                    f = (done / float(total)) if total else 0.0
                    self.on_prog((i + 0.85 * f) / n, "دانلود %s … %d٪" % (name, int(f * 100)))
                while True:
                    if self.cancelled:
                        raise DownloadPaused()
                    try:
                        self.ctl.pause = self.paused
                        _download_file(url, dest, prog, self.ctl)
                        break
                    except DownloadPaused:
                        if self.cancelled:
                            raise
                        self.on_prog((i + 0.4) / n, "دانلود متوقف شد؛ «ادامه» را بزنید.")
                        self._resume.wait()                    # ادامه از همان نقطه (فایل .part حفظ شده)
                        if self.cancelled:
                            raise
                self.on_prog((i + 0.90) / n, "نصب %s … (چند لحظه)" % name)
                try:
                    subprocess.call([dest] + args, creationflags=_nowin(), timeout=900,
                                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception as exc:
                    dbg("prereq install %s: %r" % (key, exc))
                time.sleep(1.0)
                results.append((key, bool(_prereq_ok(key))))
                try:
                    os.remove(dest)
                except Exception:
                    pass
            self.on_done(results)
        except DownloadPaused:
            self.on_done(None)                                  # لغو
        except Exception as exc:
            dbg("PrereqInstaller crashed: %r" % (exc,))
            self.on_done([(k, False) for k in self.keys])


class TaskProgressDialog(wx.Dialog):
    """پنجره‌ی هم‌تم با متن، نوار پیشرفت با درصد و دکمه‌های قابل‌تغییر (نصب پیش‌نیاز، استخراج متن و ...)."""

    def __init__(self, title, text):
        super().__init__(None, title=title, style=wx.STAY_ON_TOP | wx.BORDER_NONE)
        try:
            self._s = _system_dpi_scale()
        except Exception:
            self._s = 1.0
        S = self._S = lambda v: int(round(v * self._s))
        self._title, self._text, self._frac, self._show_bar = title, text, 0.0, False
        self._btns = []
        self.SetBackgroundColour(FloatingPanel.BASE)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetClientSize((S(440), S(250)))
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_LEFT_DOWN, self._drag_start)
        self.Bind(wx.EVT_MOTION, self._drag_move)
        self.Bind(wx.EVT_LEFT_UP, self._drag_end)
        self._drag = None
        round_corners(self, S(440), S(250), S(12))
        self.CentreOnScreen()

    def set_buttons(self, specs):
        """specs = [(برچسب، اصلی؟، تابع)] از راست به چپ چیده می‌شود."""
        for b in self._btns:
            b.Destroy()
        self._btns = []
        S = self._S
        x = S(440) - S(20)
        for label, primary, cb in specs:
            b = _FlatBtn(self, label, primary, cb, self._s)
            bw = b.GetSize().width
            x -= bw
            b.SetPosition((x, S(250) - S(52)))
            x -= S(10)
            self._btns.append(b)
        self.Refresh(False)

    def relabel(self, idx, label):
        if 0 <= idx < len(self._btns):
            self._btns[idx]._label = label
            self._btns[idx].Refresh(False)

    def set_text(self, text):
        self._text = text
        self.Refresh(False)

    def set_progress(self, frac, text=None):
        self._show_bar = True
        self._frac = max(0.0, min(1.0, float(frac)))
        if text is not None:
            self._text = text
        self.Refresh(False)

    def _on_paint(self, _e):
        from wx.lib.wordwrap import wordwrap
        dc = wx.AutoBufferedPaintDC(self)
        S = self._S
        w, h = self.GetClientSize()
        dc.SetBackground(wx.Brush(FloatingPanel.BASE))
        dc.Clear()
        dc.SetPen(wx.Pen(FloatingPanel.EDGE, 1))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRoundedRectangle(0, 0, max(1, w - 1), max(1, h - 1), S(12))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(ACCENT))
        dc.DrawRectangle(S(1), S(1), max(1, w - S(2)), S(2))
        logo = make_brand_bitmap(S(24), S(24))
        if logo.IsOk():
            dc.DrawBitmap(logo, S(14), S(10), True)
        dc.SetFont(wx.Font(wx.FontInfo(12).FaceName(UI_FONT_FACE).Bold()))
        dc.SetTextForeground(TEXT)
        dc.DrawLabel(self._title, wx.Rect(S(44), S(8), w - S(60), S(28)), wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        dc.SetFont(wx.Font(wx.FontInfo(10).FaceName(UI_FONT_FACE)))
        dc.SetTextForeground(wx.Colour(215, 220, 230))
        txt = wordwrap(self._text, w - S(40), dc)
        dc.DrawLabel(txt, wx.Rect(S(20), S(50), w - S(40), S(110)), wx.ALIGN_RIGHT | wx.ALIGN_TOP)
        if self._show_bar:
            bar = wx.Rect(S(20), S(172), w - S(100), S(10))
            dc.SetBrush(wx.Brush(FloatingPanel.SURFACE))
            dc.DrawRoundedRectangle(bar, S(5))
            fill = wx.Rect(bar.x, bar.y, max(S(10), int(bar.width * self._frac)), bar.height)
            dc.SetBrush(wx.Brush(wx.Colour(140, 214, 170)))
            dc.DrawRoundedRectangle(fill, S(5))
            dc.SetFont(wx.Font(wx.FontInfo(11).FaceName(UI_FONT_FACE).Bold()))
            dc.SetTextForeground(TEXT)
            dc.DrawLabel("%d٪" % int(self._frac * 100), wx.Rect(bar.x + bar.width + S(8), S(164), S(60), S(26)),
                         wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

    def _drag_start(self, e):
        self._drag = wx.GetMousePosition() - self.GetPosition()
        self.CaptureMouse()

    def _drag_move(self, e):
        if self._drag is not None and e.Dragging() and e.LeftIsDown():
            self.Move(wx.GetMousePosition() - self._drag)

    def _drag_end(self, e):
        if self.HasCapture():
            self.ReleaseMouse()
        self._drag = None


class PersianTextDialog(wx.Dialog):
    """نمایش متن فارسیِ استخراج‌شده با «کپی»، «ذخیره‌ی TXT» و «بستن»."""

    def __init__(self, text, name):
        super().__init__(None, title="متن استخراج‌شده", style=wx.STAY_ON_TOP | wx.BORDER_NONE)
        try:
            s = _system_dpi_scale()
        except Exception:
            s = 1.0
        S = lambda v: int(round(v * s))
        self._text, self._name, self._s = text, name, s
        self.SetBackgroundColour(FloatingPanel.BASE)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        W, H = S(560), S(480)
        self.SetClientSize((W, H))
        self.tc = wx.TextCtrl(self, value=text, pos=(S(16), S(48)), size=(W - S(32), H - S(112)),
                              style=wx.TE_MULTILINE | wx.BORDER_NONE | wx.TE_RICH2)
        self.tc.SetBackgroundColour(FloatingPanel.SURFACE)
        self.tc.SetForegroundColour(TEXT)
        self.tc.SetFont(wx.Font(wx.FontInfo(12).FaceName(UI_FONT_FACE)))
        try:
            self.tc.SetLayoutDirection(wx.Layout_RightToLeft)
        except Exception:
            pass
        # TE_RICH2 رنگ پیش‌فرض را نادیده می‌گیرد (متن سیاه می‌ماند)؛ رنگ سفید صریحاً روی کل متن اعمال می‌شود
        try:
            white = wx.Colour(255, 255, 255)
            attr = wx.TextAttr(white, FloatingPanel.SURFACE, wx.Font(wx.FontInfo(12).FaceName(UI_FONT_FACE)))
            self.tc.SetDefaultStyle(attr)
            self.tc.SetStyle(0, self.tc.GetLastPosition(), attr)
            self.tc.SetForegroundColour(white)
        except Exception as exc:
            dbg("persian text colour: %r" % (exc,))
        x = W - S(16)
        for label, primary, cb in (("بستن", False, self.Close), ("ذخیره‌ی TXT", False, self._save), ("کپی", True, self._copy)):
            b = _FlatBtn(self, label, primary, cb, s)
            x -= b.GetSize().width
            b.SetPosition((x, H - S(52)))
            x -= S(10)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_CLOSE, lambda e: self.Destroy())
        round_corners(self, W, H, S(12))
        self.CentreOnScreen()

    def _copy(self):
        try:
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(self.tc.GetValue()))
                wx.TheClipboard.Close()
        except Exception:
            pass

    def _save(self):
        dlg = wx.FileDialog(self, "ذخیره‌ی متن", defaultFile=os.path.splitext(self._name)[0] + ".txt",
                            wildcard="TXT (*.txt)|*.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                with open(dlg.GetPath(), "w", encoding="utf-8-sig") as f:
                    f.write(self.tc.GetValue())
        except Exception as exc:
            dbg("save persian txt: %r" % (exc,))
        finally:
            dlg.Destroy()

    def _on_paint(self, _e):
        dc = wx.AutoBufferedPaintDC(self)
        S = lambda v: int(round(v * self._s))
        w, h = self.GetClientSize()
        dc.SetBackground(wx.Brush(FloatingPanel.BASE))
        dc.Clear()
        dc.SetPen(wx.Pen(FloatingPanel.EDGE, 1))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRoundedRectangle(0, 0, max(1, w - 1), max(1, h - 1), S(12))
        dc.SetFont(wx.Font(wx.FontInfo(12).FaceName(UI_FONT_FACE).Bold()))
        dc.SetTextForeground(TEXT)
        dc.DrawLabel("متن فارسیِ استخراج‌شده — " + os.path.basename(self._name), wx.Rect(S(16), S(8), w - S(32), S(30)),
                     wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)


PERSIAN_TESS = "fas"
PERSIAN_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp", ".pdf")


def _ensure_pypdfium(cb):
    """رندر PDF برای OCR؛ فقط یک‌بار نصب می‌شود و بعدش کاملاً آفلاین کار می‌کند."""
    _activate_pylibs()
    try:
        import pypdfium2
        return pypdfium2
    except Exception:
        pass
    cb(0.05, "نصب کتابخانه‌ی خواندن PDF (فقط یک‌بار) …")
    runner = _runner_python() or _ensure_embed_python(lambda f, m: cb(0.05 + 0.1 * f, m))
    os.makedirs(PYLIBS_DIR, exist_ok=True)
    rc, tail = _run_cmd(runner + ["-m", "pip", "install", "--target", PYLIBS_DIR, "--upgrade", "--prefer-binary",
                                  "--no-warn-script-location", "--disable-pip-version-check", "--progress-bar", "off",
                                  "pypdfium2"], timeout=1800)
    if rc != 0:
        raise EngineError("نصب کتابخانه‌ی PDF ناموفق بود (اینترنت لازم است): " + " | ".join(tail[-2:]))
    _activate_pylibs()
    import importlib
    importlib.invalidate_caches()
    import pypdfium2
    return pypdfium2


def persian_ocr_extract(path, cb, cancel):
    """متن فارسی عکس یا PDF را با Tesseract (مدل fas) و کاملاً آفلاین استخراج می‌کند
    (همان روشِ Space «Persian-OCR»: pytesseract + lang=fas؛ PDF صفحه‌به‌صفحه به عکس تبدیل می‌شود).
    فقط بار اول مدل fas (و اگر نبود Tesseract / کتابخانه‌ی PDF) دانلود می‌شود."""
    exe = find_tesseract()
    if exe is None:
        cb(0.02, "نصب موتور Tesseract (فقط یک‌بار) …")
        install_tesseract(lambda f, m: cb(0.02 + 0.18 * f, m))
        exe = find_tesseract()
        if exe is None:
            raise EngineError("Tesseract نصب نشد.")
    if not tess_model_installed(PERSIAN_TESS):
        cb(0.20, "دانلود مدل OCR فارسی (فقط یک‌بار) …")
        _download_file(TESSDATA_URL % PERSIAN_TESS, os.path.join(TESSDATA_DIR, PERSIAN_TESS + ".traineddata"),
                       lambda d, t: cb(0.20 + 0.10 * (d / float(t) if t else 0.0), "دانلود مدل OCR فارسی … %s" % fmt_mb(d)))
    ext = os.path.splitext(path)[1].lower()
    pages = []
    if ext == ".pdf":
        pdfium = _ensure_pypdfium(cb)
        pdf = pdfium.PdfDocument(path)
        total = len(pdf)
        loader = lambda i: pdf[i].render(scale=3.0).to_pil()      # ≈ ۲۱۶ dpi
        count = total
    else:
        from PIL import ImageSequence
        im = Image.open(path)
        frames = [f.copy() for f in ImageSequence.Iterator(im)] if getattr(im, "n_frames", 1) > 1 else [im]
        loader = lambda i: frames[i]
        count = len(frames)
    tmp = tempfile.mkdtemp(prefix="eshpfa_")
    out = []
    try:
        for i in range(count):
            if cancel.cancelled:
                raise EngineError("استخراج لغو شد.")
            cb(0.30 + 0.69 * (i / float(count)), "OCR صفحه‌ی %d از %d …" % (i + 1, count))
            img = loader(i)
            work = ocr_preprocess(img)
            txt = _tess_read(exe, work, PERSIAN_TESS, tmp, cancel, "p%d" % i, psm="3")
            if txt:
                out.append(txt)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return "\n\n".join(out).strip()


class TrayStatusNotice(wx.Frame):
    """پیام کوچک و ثابت بالای ناحیهٔ ساعت؛ با بازشدن پنل پنهان می‌شود."""
    def __init__(self, app):
        super().__init__(None, title="", size=(352, 58),
                         style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP | wx.BORDER_NONE)
        self.app = app
        try:
            self.s = _system_dpi_scale()
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
        self._fade_id = getattr(self, "_fade_id", 0) + 1
        fid = self._fade_id
        try:
            self.SetTransparent(255)
        except Exception:
            pass
        x, y, w, h = self._position_notice()
        round_corners(self, w, h, self._S(10))
        place_top(self, x, y, w, h)
        self.Refresh(False)
        wx.CallLater(800, self._fade_step, fid, 255)      # حدود ۱ ثانیه بعد کاملاً محو می‌شود

    def _fade_step(self, fid, alpha):
        if fid != getattr(self, "_fade_id", 0) or not self._visible_notice or self.app._quitting:
            return
        alpha -= 51
        if alpha <= 0:
            self.hide_notice()
            return
        try:
            self.SetTransparent(alpha)
        except Exception:
            pass
        wx.CallLater(50, self._fade_step, fid, alpha)

    def hide_notice(self):
        self._fade_id = getattr(self, "_fade_id", 0) + 1
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
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, lambda e: wx.CallAfter(self.app.panel.show_panel))

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
        self.Bind(wx.EVT_MENU, lambda e: app.quit(force=True), ex)
        return m





ID_SNIP, ID_CLOSE, ID_ESC = 101, 102, 103


class SnipApp(wx.Frame):
    def __init__(self, background=False):
        super().__init__(None)                
        try:
            self.SetIcons(make_icon_bundle())
        except Exception:
            pass
        self.cfg = Config()
        nllb_set_model(self.cfg["nllb_model"])
        apply_theme(self.cfg["accent"], self.cfg["font_face"])
        self.net = {"dirty": False, "testing": False, "gen": 0, "status": ("", "idle")}
        self._monitor_rects_cache = list_monitor_rects()
        self._quitting = False
        self._last_key = 0.0
        self._last_snip_done = 0.0
        self._armed = True            
        self._esc_on = False
        self._pending = None
        self._cap = None              

        self._job = 0                 # شماره‌ی آخرین ترجمه‌ی AI/آفلاین؛ نتیجه‌های کهنه نادیده گرفته می‌شوند
        _prov = self.cfg["ai_provider"]
        _models = dict(AI_DEFAULT_MODELS)
        _models.update({k: v for k, v in (self.cfg["ai_models"] or {}).items() if k in _models and v})
        self.ai = {"provider": _prov, "models": _models, "tokens": {}, "dirty": False,
                   "testing": False, "status": ("هنوز بررسی نشده است", "idle")}
        self.off = {"busy": False, "progress": 0.0, "msg": "", "kind": "idle",
                    "tess_exe": find_tesseract() is not None,
                    "tess_model": tess_model_installed(self.cfg["ocr_lang"]), "argos": "checking",
                    "paused": False, "size_text": ""}
        self.live = GameLiveController(self)         # ترجمه‌ی زنده‌ی بازی (فقط آفلاین)
        self.live_state = ("stopped", "متوقف")
        self.live_stats = {}
        self.live_last_ocr = ""
        self._last_live_key = 0.0
        self._live_panel_excluded = False

        self.layer = SnipLayer(self)
        self.box = ResultBox(self)
        self.live_overlay = LiveOverlay(self)
        self.panel = FloatingPanel(self)
        self.tray_notice = TrayStatusNotice(self)
        self.worker = None if self.cfg["performance_mode"] else TranslateWorker(
            self._on_result, self._on_error, self._on_state)
        self._worker_release_pending = False
        wx.CallLater(3000, self.offline_probe)          # اگر موتور آفلاین انتخاب بود و چیزی کم بود، خودکار نصب می‌شود
        self.tray = Tray(self)
        self._fg_watch = TopWatcher(self)

        self.Bind(wx.EVT_HOTKEY, self._on_hotkey)

        self._combo_snip = parse_hotkey(self.cfg["snip_hotkey"])
        self._combo_close = parse_hotkey(self.cfg["close_hotkey"])
        self._combo_live = parse_hotkey(self.cfg["live_hotkey"])
        self._prev = {"snip": False, "close": False, "esc": False, "live": False}
        self._poll = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._poll_keys, self._poll)
        self._poll.Start(65 if self.cfg["performance_mode"] else 25)
        self._mon_sig = tuple(self._monitor_rects_cache)
        self._mon_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_mon_timer, self._mon_timer)
        self._mon_timer.Start(3000)              # تشخیص وصل/قطع مانیتور
        self.Bind(wx.EVT_CLOSE, lambda e: self.quit())
        for hid, key in ((ID_SNIP, "snip_hotkey"), (ID_CLOSE, "close_hotkey"), (ID_LIVE, "live_hotkey")):
            mods, vk = parse_hotkey(self.cfg[key])
            if vk is not None:
                self.RegisterHotKey(hid, mods, vk)    

        threading.Thread(target=self._sync_startup, daemon=True).start()
        self._prereq_dlg = None
        self._pa_busy = False
        wx.CallLater(2500, self._startup_prereq_check)
        wx.CallLater(800, self.apply_stream_mode)
        self._net_prev_engine = None        # موتوری که قبل از سوییچ خودکار به آفلاین فعال بود
        self._net_fail = 0
        threading.Thread(target=self._net_watch, daemon=True).start()
        if not background and not self.cfg["onboarded"]:
            wx.CallLater(1200, self.show_onboarding)
        if not background:
            # نوتیف ویندوزی حذف شد؛ پیام آماده‌بودن فقط در وضعیت پنل نشان داده می‌شود
            try:
                self.panel.set_state(
                    "برنامه آماده استفاده است — %s = انتخاب ناحیه و ترجمه" % self.cfg["snip_hotkey"].upper(),
                    "ok", 6000)
            except Exception:
                pass


    NET_PROBES = ("http://www.msftconnecttest.com/connecttest.txt", "https://www.gstatic.com/generate_204",
                  "https://translate.google.com/")

    def _net_watch(self):
        """هر ~۱۰ ثانیه اینترنت را می‌سنجد (با همان پروکسی/VPN برنامه). قطع شد → سوییچ خودکار به آفلاین + هشدار."""
        time.sleep(15)
        while not self._quitting:
            try:
                if self.cfg["engine"] in ("google", "ai") or self._net_prev_engine:
                    ok = any(_reachable(u, 5) for u in self.NET_PROBES)
                    wx.CallAfter(self._net_result, ok)
            except Exception:
                pass
            for _ in range(10):
                if self._quitting:
                    return
                time.sleep(1)

    def _offline_ready(self):
        try:
            return bool(find_tesseract() and tess_model_installed(self.cfg["ocr_lang"]) and nllb_installed())
        except Exception:
            return False

    def _net_result(self, ok):
        if self._quitting:
            return
        if ok:
            self._net_fail = 0
            prev = self._net_prev_engine
            if prev:
                self._net_prev_engine = None
                if self.cfg["engine"] == "offline":          # فقط اگر کاربر در این فاصله موتور را عوض نکرده باشد
                    self.set_engine(prev)
                    self.panel.set_state("اینترنت وصل شد؛ به «%s» برگشت." % self.ENGINE_NAMES.get(prev, prev), "ok", 5000)
            return
        self._net_fail += 1
        if self._net_fail != 2:                           # دو سنجش پشت‌سرهم ناموفق = قطعیِ واقعی
            return
        cur = self.cfg["engine"]
        if cur not in ("google", "ai"):
            return
        if self._offline_ready():
            self._net_prev_engine = cur
            self.set_engine("offline")
            self.panel.set_state("اینترنت در دسترس نیست؛ خودکار به ترجمه‌ی آفلاین رفت.", "err", 8000)
        else:
            self.panel.set_state("اینترنت در دسترس نیست و مدل آفلاین کامل نصب نیست.", "err", 8000)

    @staticmethod
    def _power_status():
        """(لپ‌تاپ است؟، روی باتری است؟) با GetSystemPowerStatus؛ BatteryFlag==128 یعنی باتری وجود ندارد."""
        class _SPS(ctypes.Structure):
            _fields_ = [("AC", ctypes.c_ubyte), ("Flag", ctypes.c_ubyte), ("Pct", ctypes.c_ubyte),
                        ("Saver", ctypes.c_ubyte), ("LifeT", ctypes.c_ulong), ("FullT", ctypes.c_ulong)]
        st = _SPS()
        try:
            if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(st)):
                return False, False
        except Exception:
            return False, False
        laptop = st.Flag not in (128, 255)
        return laptop, bool(laptop and st.AC == 0)

    def _update_power(self):
        laptop, on_batt = self._power_status()
        if on_batt == getattr(self, "_on_batt", None):
            return
        self._on_batt = on_batt
        try:
            if self.cfg["performance_mode"]:
                return                                           # از قبل کم‌مصرف است
            self._poll.Start(65 if on_batt else 25)              # روی باتری، نرخ poll کیبورد کمتر می‌شود
        except Exception:
            pass
        if on_batt:
            if not getattr(self, "_batt_hint_shown", False):
                self._batt_hint_shown = True
                self.panel.set_state("لپ‌تاپ روی باتری است؛ برای مصرف کمتر «حالت کم‌مصرف» را در تنظیمات روشن کنید.", "ok", 9000)

    # ── پیش‌نیازها: تشخیص → اجازه → دانلود با درصد، توقف/ادامه → نصب ──
    def ensure_prereqs(self, keys, then=None):
        missing = [k for k in keys if not _prereq_ok(k)]
        if not missing:
            if then:
                then()
            return
        if getattr(self, "_prereq_dlg", None) is not None:
            return
        names = " و ".join(PREREQ_FA[k] for k in missing)
        dlg = self._prereq_dlg = TaskProgressDialog("پیش‌نیاز برنامه",
            "%s روی این ویندوز نصب نیست و این بخش بدون آن کار نمی‌کند.\n"
            "اجازه می‌دهید برنامه آن را خودش دانلود و نصب کند؟ نسخه‌ی مناسب ویندوز شما انتخاب می‌شود "
            "و می‌توانید دانلود را متوقف کنید و بعداً از همان‌جا ادامه دهید." % names)
        inst = {"obj": None}

        def close():
            if inst["obj"] is not None:
                inst["obj"].cancel()
            self._prereq_dlg = None
            try:
                dlg.Destroy()
            except Exception:
                pass

        def toggle():
            o = inst["obj"]
            if o is None:
                return
            if o.paused:
                o.resume()
                dlg.relabel(0, "توقف")
            else:
                o.pause()
                dlg.relabel(0, "ادامه")

        def done(res):
            if self._quitting or self._prereq_dlg is None:
                return
            if res is None:
                close()
                return
            ok = all(r[1] for r in res)
            if ok:
                dlg.set_progress(1.0, "نصب شد ✓")
                if "wv2" in missing:
                    dlg.set_text("نصب شد ✓  برای فعال‌شدن، برنامه یک‌بار دوباره اجرا می‌شود.")
                    dlg.set_buttons([("راه‌اندازی مجدد", True, lambda: (close(), _restart()))])
                else:
                    dlg.set_buttons([("بستن", True, lambda: (close(), then() if then else None))])
            else:
                dlg.set_text("نصب خودکار انجام نشد. یک‌بار دیگر امتحان کنید یا برنامه را «به‌عنوان ادمین» اجرا کنید.")
                dlg.set_buttons([("بستن", False, close), ("تلاش دوباره", True, lambda: (close(), self.ensure_prereqs(keys, then)))])

        def go():
            o = inst["obj"] = PrereqInstaller(missing, lambda f, m: wx.CallAfter(
                lambda: dlg.set_progress(f, m) if self._prereq_dlg is dlg else None),
                lambda r: wx.CallAfter(done, r))
            dlg.set_progress(0.0, "در حال شروع …")
            dlg.set_buttons([("لغو", False, close), ("توقف", False, toggle)])
            o.start()

        dlg.set_buttons([("بعداً", False, close), ("تأیید و نصب", True, go)])
        dlg.Show()
        dlg.Raise()

    def _startup_prereq_check(self):
        if self._quitting:
            return
        if self.cfg["engine"] == "google" or self.cfg["engine"] is None:
            self.ensure_prereqs(["wv2"])

    # ── استخراج متن فارسی از عکس/PDF (آفلاین) ──
    def persian_ocr_start(self):
        if getattr(self, "_pa_busy", False):
            return
        dlg = wx.FileDialog(None, "انتخاب عکس یا PDF فارسی",
                            wildcard="عکس و PDF|*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff;*.webp;*.pdf|همه‌ی فایل‌ها|*.*",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        try:
            dlg.CentreOnScreen()
            if dlg.ShowModal() != wx.ID_OK:
                return
            path = dlg.GetPath()
        finally:
            dlg.Destroy()
        if os.path.splitext(path)[1].lower() not in PERSIAN_EXTS:
            self.panel.set_state("فرمت فایل پشتیبانی نمی‌شود (عکس یا PDF).", "err", 4000)
            return
        self._pa_busy = True
        cancel = CancelToken()
        pd = TaskProgressDialog("استخراج متن فارسی", "در حال آماده‌سازی …")
        pd.set_progress(0.0, "در حال آماده‌سازی …")

        def abort():
            cancel.cancel()
            try:
                pd.Destroy()
            except Exception:
                pass

        pd.set_buttons([("لغو", False, abort)])
        pd.Show()

        def cb(frac, msg):
            wx.CallAfter(lambda: pd.set_progress(frac, msg) if pd else None)

        def work():
            try:
                res = (persian_ocr_extract(path, cb, cancel), None)
            except EngineError as exc:
                res = (None, str(exc))
            except Exception as exc:
                dbg("persian_ocr crashed: %r" % (exc,))
                res = (None, "خطا در استخراج: %s" % exc)
            wx.CallAfter(self._persian_ocr_done, path, pd, cancel, res)

        threading.Thread(target=work, daemon=True).start()

    def _persian_ocr_done(self, path, pd, cancel, res):
        self._pa_busy = False
        try:
            pd.Destroy()
        except Exception:
            pass
        if self._quitting or cancel.cancelled:
            return
        text, err = res
        if err:
            self.panel.set_state(err, "err", 7000)
            return
        if not text:
            self.panel.set_state("متنی پیدا نشد؛ عکس را واضح‌تر یا بزرگ‌تر امتحان کنید.", "err", 5000)
            return
        dlg = PersianTextDialog(text, path)
        dlg.Show()
        dlg.Raise()

    # ── حالت استریم ──
    def apply_stream_mode(self):
        on = bool(self.cfg["stream_mode"])
        try:
            set_capture_exclusion(self.panel, on or bool(getattr(self, "_live_panel_excluded", False)))
        except Exception:
            pass
        self.panel.refresh()

    def toggle_stream_mode(self):
        self.cfg.set("stream_mode", not bool(self.cfg["stream_mode"]))
        self.apply_stream_mode()
        self.panel.refresh()
        self.panel.set_state("حالت استریم %s" % ("روشن شد؛ پنل در ضبط/استریم دیده نمی‌شود، توکن پوشانده و انیمیشن‌ها خاموش شدند."
                                                 if self.cfg["stream_mode"] else "خاموش شد."), "ok", 4500)

    def _update_hdr(self):
        h = hdr_active()
        if h == getattr(self, "_hdr_state", None):
            return
        first = getattr(self, "_hdr_state", None) is None
        self._hdr_state = h
        on = bool(h and self.cfg["hdr_gamma"])
        globals()["_HDR_GAMMA"] = 1.35 if on else 1.0
        if h and not first:
            self.panel.set_state("مانیتور HDR تشخیص داده شد؛ گامای OCR خودکار تنظیم شد.", "ok", 6000)
        elif h:
            dbg("HDR display detected at startup → OCR gamma 1.35")

    def _update_sleep_guard(self):
        """جلوگیری از Sleep/خاموش‌شدن صفحه فقط وقتی ترجمه فعال است (زنده‌ی بازی یا ترجمه‌ی در حال انجام)."""
        try:
            w = getattr(self, "worker", None)
            active = bool(self.live.running) or bool(w is not None and getattr(w, "_busy", False))
        except Exception:
            active = False
        if active == getattr(self, "_sleep_blocked", False):
            return
        self._sleep_blocked = active
        try:
            # ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED  ←→  فقط ES_CONTINUOUS (آزادسازی)
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x1 | 0x2 if active else 0x80000000)
        except Exception:
            pass

    def _clear_webview_cookies(self, files_only=False):
        """کوکی‌ها و حافظه‌ی وب‌ویوی گوگل را هنگام خروج پاک می‌کند (کنار پاک‌شدن پوشه‌ی عکس‌ها)."""
        if not files_only:
            try:
                w = getattr(self, "worker", None)
                if w is not None and getattr(w, "browser", None) is not None:
                    w.browser.RunScript(
                        "try{document.cookie.split(';').forEach(function(c){var n=c.split('=')[0].trim();"
                        "document.cookie=n+'=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';});"
                        "localStorage.clear();sessionStorage.clear();}catch(e){}")
            except Exception:
                pass
            return
        import subprocess
        roots = set()
        exe_stem = os.path.splitext(os.path.basename(sys.executable if _is_frozen() else sys.argv[0] or "python"))[0]
        for base in (os.environ.get("LOCALAPPDATA"), os.environ.get("APPDATA")):
            if base:
                roots.add(os.path.join(base, exe_stem))
                roots.add(os.path.join(base, "42OCR"))
                roots.add(os.path.join(base, "ESHTranslator"))
        roots.add(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0] or ".")), exe_stem + ".WebView2"))
        names = ("Cookies", "Cookies-journal", os.path.join("Network", "Cookies"),
                 os.path.join("Network", "Cookies-journal"))
        victims = []
        for r in roots:
            for prof in ("EBWebView", ""):
                for sub in ("Default", ""):
                    for n in names:
                        f = os.path.join(r, prof, sub, n)
                        if os.path.isfile(f):
                            victims.append(f)
        left = []
        for f in victims:
            for attempt in range(3):
                try:
                    os.remove(f)
                    break
                except Exception:
                    time.sleep(0.15)
            else:
                left.append(f)
        if left:          # اگر هنوز توسط msedgewebview2 قفل است، یک فرایند جدا چند ثانیه بعد پاکشان می‌کند
            try:
                cmd = "ping -n 4 127.0.0.1 >nul & " + " & ".join('del /f /q "%s"' % f for f in left)
                subprocess.Popen(["cmd", "/c", cmd], creationflags=0x08000000 | 0x00000008,
                                 close_fds=True, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    def _on_mon_timer(self, _evt):
        if self._quitting:
            return
        self._update_sleep_guard()
        try:
            self._update_power()
            self._update_hdr()
        except Exception:
            pass
        try:
            mons = tuple(list_monitor_rects())
        except Exception:
            return
        if mons == self._mon_sig:
            return
        self._mon_sig = mons
        self._monitor_rects_cache = list(mons)
        try:
            self.panel._build()
        except Exception:
            pass
        self.panel.refresh()
        msg = "چیدمان مانیتورها تغییر کرد (%d مانیتور)" % len(mons)
        try:
            if int(self.cfg["output_monitor"] or 0) > len(mons):
                msg += " — مانیتور خروجی در دسترس نیست؛ از مانیتور عکس‌برداری استفاده می‌شود"
        except Exception:
            pass
        self.panel.set_state(msg, "ok", 5000)

    def show_onboarding(self):
        """راهنمای اولین اجرا: صفحه‌ی هم‌تم داخل همین پنل (کلیدها، موتور، رنگ و فونت)."""
        if self._quitting or self.cfg["onboarded"]:
            return
        self.cfg.set("onboarded", True)
        try:
            self.panel.show_panel()
        except Exception:
            pass
        self.panel.wstep = 0
        self.panel.wsolo = False
        self.panel._goto("welcome")
        self.panel.rebuild()

    def set_theme(self, accent=None, font=None):
        if accent:
            self.cfg.set("accent", accent)
        if font:
            self.cfg.set("font_face", font)
        apply_theme(accent, font)
        self.panel.rebuild()

    # ── شبکه / VPN / پروکسی ──
    def _net_status(self, text, kind="idle"):
        self.net["status"] = (text, kind)
        self.panel.refresh()

    def net_set_mode(self, mode):
        if mode not in ("system", "custom", "off"):
            return
        if mode == "custom" and not self.cfg["proxy_url"]:
            self.net_edit_url()
            if not self.cfg["proxy_url"]:
                return
        self.cfg.set("proxy_mode", mode)
        NET["mode"] = mode
        _apply_net_env()
        self.net["dirty"] = True
        self._net_status("", "idle")
        self.net_test(force=True)

    def net_edit_url(self):
        from urllib.parse import urlparse
        value = self._ask_text("پروکسی", "آدرس پروکسی را وارد کن (مثل http://127.0.0.1:10809 یا socks5://127.0.0.1:10808):",
                               self.cfg["proxy_url"])
        if value is None:
            return
        value = value.strip()
        if value and "://" not in value:
            value = "http://" + value
        pu = urlparse(value) if value else None
        if value and not (pu.scheme in ("http", "https", "socks5", "socks5h") and pu.hostname and pu.port):
            self.panel.set_state("آدرس پروکسی نامعتبر است؛ نمونه: socks5://127.0.0.1:10808", "err", 6000)
            return
        self.cfg.set("proxy_url", value)
        NET["url"] = value
        if self.cfg["proxy_mode"] == "custom":
            _apply_net_env()
            self.net["dirty"] = True
            self._net_status("", "idle")
            self.net_test(force=True)

    def net_test(self, force=False):
        """بررسی اتصال: اگر به همه‌ی سرویس‌ها برسد «فعال است»، وگرنه «فعال نیست»."""
        if self.net["testing"] and not force:
            return
        self.net["gen"] = gen = self.net.get("gen", 0) + 1
        self.net["testing"] = True
        self._net_status("در حال بررسی…", "busy")
        targets = (("Google", "https://translate.google.com/"), ("Gemini", "https://generativelanguage.googleapis.com/"),
                   ("OpenAI", "https://api.openai.com/"), ("OpenRouter", "https://openrouter.ai/"))

        def work():
            import urllib.error
            import urllib.request
            from concurrent.futures import ThreadPoolExecutor

            def one(item):
                name, url = item
                try:
                    net_open(urllib.request.Request(url, headers={"User-Agent": "ESHTranslator/1.0"}), 10).read(1)
                    return name, True
                except urllib.error.HTTPError:
                    return name, True                    # سرور جواب داده (حتی 401/404) یعنی مسیر باز است
                except Exception:
                    return name, False

            with ThreadPoolExecutor(max_workers=len(targets)) as pool:
                res = list(pool.map(one, targets))
            okl = [n for n, ok in res if ok]
            bad = [n for n, ok in res if not ok]
            wx.CallAfter(self._net_test_done, okl, bad, gen)

        threading.Thread(target=work, daemon=True).start()

    def _net_test_done(self, okl, bad, gen=None):
        if gen is not None and gen != self.net.get("gen"):
            return                                       # نتیجه‌ی بررسیِ قدیمی (تنظیم در این فاصله عوض شده)
        self.net["testing"] = False
        if self._quitting:
            return
        if not bad:
            self._net_status("فعال است", "ok")
        else:
            self._net_status("فعال نیست", "err")

    # ── ابزارها: اندازه‌ی رابط، حالت بازی، ذخیره/بازیابی تنظیمات ──
    EXPORT_SKIP = ("ai_tokens", "save_dir", "run_on_startup", "capture_monitor", "output_monitor", "game_live_roi")

    def change_ui_scale(self, delta, wrap=False):
        cur = int(self.cfg["ui_scale"] or 100)
        new = cur + int(delta)
        if new > 150:
            new = 100 if wrap else 150
        new = max(100, min(150, new))
        if new == cur:
            return
        self.cfg.set("ui_scale", new)
        self.panel.apply_scale()

    def toggle_game_lite(self):
        self.cfg.set("game_lite_ui", not bool(self.cfg["game_lite_ui"]))
        self.panel.refresh()

    def export_settings(self):
        dlg = wx.FileDialog(None, "ذخیره‌ی تنظیمات", defaultFile="ESH_Translator_settings.json",
                            wildcard="JSON (*.json)|*.json", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        try:
            dlg.CentreOnScreen()
            if dlg.ShowModal() != wx.ID_OK:
                return
            path = dlg.GetPath()
        finally:
            dlg.Destroy()
        data = {k: v for k, v in self.cfg.data.items() if k not in self.EXPORT_SKIP}
        data["_app_version"] = APP_VERSION
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.panel.set_state("تنظیمات ذخیره شد (توکن‌ها شامل نیست)", "ok", 5000)
        except OSError as exc:
            self.panel.set_state("ذخیره‌ی تنظیمات ممکن نشد: %s" % exc, "err", 6000)

    def import_settings(self):
        dlg = wx.FileDialog(None, "وارد کردن تنظیمات", wildcard="JSON (*.json)|*.json",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        try:
            dlg.CentreOnScreen()
            if dlg.ShowModal() != wx.ID_OK:
                return
            path = dlg.GetPath()
        finally:
            dlg.Destroy()
        try:
            with open(path, "r", encoding="utf-8") as f:
                j = json.load(f)
            if not isinstance(j, dict):
                raise ValueError("ساختار فایل درست نیست")
        except Exception as exc:
            self.panel.set_state("فایل تنظیمات خوانده نشد: %s" % exc, "err", 6000)
            return
        keep = {}
        for k, default in Config.DEFAULTS.items():
            if k in j and k not in self.EXPORT_SKIP:
                v = j[k]
                if isinstance(v, type(default)) and not (isinstance(v, bool) and not isinstance(default, bool)):
                    keep[k] = v
        if not keep:
            self.panel.set_state("این فایل تنظیمات قابل‌استفاده‌ای ندارد", "err", 6000)
            return
        merged = dict(self.cfg.data)
        merged.update(keep)
        self.cfg.data = merged
        self.cfg._save()
        wx.MessageBox("تنظیمات وارد شد. برای اعمال، برنامه دوباره اجرا می‌شود.", "ESH Translator", wx.OK | wx.ICON_INFORMATION)
        self.restart_app()

    def restart_app(self):
        """برنامه را دوباره اجرا می‌کند (برای اعمال تنظیمات شبکه روی مرورگر داخلی)."""
        import subprocess
        argv = [sys.executable] + ([] if getattr(sys, "frozen", False) else sys.argv[:1]) + \
            [a for a in sys.argv[1:] if a != "--restarted"] + ["--restarted"]
        try:
            subprocess.Popen(argv, close_fds=True)
        except Exception as exc:
            self.panel.set_state("راه‌اندازی مجدد ممکن نشد: %s" % exc, "err", 6000)
            return
        self.quit(force=True)

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
        elif i == ID_LIVE:
            self.live_toggle()

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
        lv = self._combo_down(self._combo_live)
        if lv and not self._prev["live"]:
            self.live_toggle()                        # (با RegisterHotKey هم‌زمان؛ در live_toggle ضدلرزش دارد)
        self._prev["live"] = lv

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


    def raise_overlays(self):
        """پنل پین‌شده و جعبه‌ی نتیجه را (بدون فوکوس) دوباره بالای بازی می‌آورد."""
        if self._quitting:
            return
        try:
            if self.panel._visible() and self.panel.pinned:
                raise_top(self.panel)
        except Exception:
            pass
        try:
            if self.box.mode != "hidden":
                raise_top(self.box)
        except Exception:
            pass

    def start_snip(self):
        if self.layer.active or self._quitting:
            return

        self.tray_notice.hide_notice()
        self._pending = None
        if exclusive_fullscreen_active() and time.time() - getattr(self, "_fs_warned", 0) > 300:
            self._fs_warned = time.time()
            self.panel.set_state("هشدار: بازی احتمالاً Exclusive Fullscreen است؛ اگر پنل یا نتیجه دیده نشد، بازی را روی Borderless بگذارید",
                                 "err", 8000)
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
            self.box.bounds = None
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
        self._job += 1                            # هر ترجمه‌ی جدید، نتیجه‌ی ترجمه‌ی AI/آفلاین قبلی را بی‌اثر می‌کند
        rect = self._output_anchor(rect)
        self.box.show_busy(rect)
        self.panel.set_state("در حال ترجمه", "busy")
        engine = self.cfg["engine"]
        if engine in ("ai", "offline"):
            self._run_text_engine(img, rect, engine)
            return
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


    # ═════════════ موتور ترجمه / هوش مصنوعی / آفلاین / مانیتور خروجی ═════════════
    ENGINE_NAMES = {"google": "Google Translate", "ai": "ترجمه با Ai", "offline": "ترجمه‌ی آفلاین"}

    def set_engine(self, key):
        if key not in self.ENGINE_NAMES:
            return
        self.cfg.set("engine", key)
        self.panel.refresh()
        if key == "google":
            wx.CallAfter(self.ensure_prereqs, ["wv2"])
        if key == "offline":
            self.offline_probe(bg=True)          # سوییچ فوری: چک دیسک/PATH در ترد پس‌زمینه تا UI فریز نشود
        warn = self.engine_warning()
        if warn:
            self.panel.set_state(warn.replace("⚠ ", ""), "err", 5000)
        else:
            self.panel.set_state("موتور ترجمه: %s" % self.ENGINE_NAMES[key], "ok", 2600)

    def engine_warning(self):
        e = self.cfg["engine"]
        if e == "ai" and self.cfg["ai_provider"] != "custom" and not self.ai_token_saved(self.cfg["ai_provider"]):
            return "⚠ برای هوش مصنوعی هنوز توکنی ذخیره نشده است"
        if e == "offline" and not (self.off["tess_exe"] and self.off["tess_model"]):
            return "⚠ مدل‌های آفلاین کامل نصب نیستند (صفحه‌ی آفلاین)"
        return ""

    # ── هوش مصنوعی ──
    def ai_token_saved(self, provider):
        return bool((self.cfg["ai_tokens"] or {}).get(provider))

    def _ai_saved_token(self, provider):
        enc = (self.cfg["ai_tokens"] or {}).get(provider)
        return secret_decrypt(enc) if enc else ""

    def _ai_status(self, text, kind="idle"):
        self.ai["status"] = (text, kind)
        self.panel.refresh()

    def ai_set_provider(self, provider):
        if provider not in AI_DEFAULT_MODELS or provider == self.ai["provider"]:
            return
        self.ai["provider"] = provider
        self.panel.relayout()                      # ردیف آدرس فقط برای «سفارشی» دیده می‌شود
        self._ai_status("هنوز بررسی نشده است", "idle")

    def ai_edit_url(self):
        value = self._ask_text("آدرس سرور سفارشی",
                               "آدرس OpenAI-compatible (مثلاً http://localhost:11434/v1 برای Ollama یا http://localhost:1234/v1 برای LM Studio):",
                               self.cfg["ai_custom_url"])
        if value is None:
            return
        value = value.strip().rstrip("/")
        if not re.match(r"^https?://\S+$", value, re.I):
            self._ai_status("آدرس معتبر نیست (باید با http:// یا https:// شروع شود)", "err")
            return
        self.cfg.set("ai_custom_url", value[:200])
        self._ai_status("آدرس ذخیره شد؛ «بررسی اتصال» را بزنید", "idle")

    # ── شمارنده‌ی مصرف توکن ──
    def _ai_usage_add(self, prov, model, usage):
        if self._quitting or not usage:
            return
        tin, tout = int(usage[0] or 0), int(usage[1] or 0)
        allu = dict(self.cfg["ai_usage"] or {})
        u = dict(allu.get(prov) or {})
        u["in"], u["out"], u["n"] = u.get("in", 0) + tin, u.get("out", 0) + tout, u.get("n", 0) + 1
        c = ai_cost(model, tin, tout)
        if c is not None:
            u["usd"] = round(u.get("usd", 0.0) + c, 6)
            u["priced"] = True
        allu[prov] = u
        self.cfg.set("ai_usage", allu)
        self.panel.refresh()

    def ai_usage_text(self, prov):
        u = (self.cfg["ai_usage"] or {}).get(prov) or {}
        if not u.get("n"):
            return "مصرف: هنوز چیزی ثبت نشده"
        text = "مصرف: %s ورودی · %s خروجی" % (fmt_tokens(u.get("in")), fmt_tokens(u.get("out")))
        if prov == "custom":
            return text + " · محلی"
        if u.get("priced"):
            return text + " · ≈$%.3f" % float(u.get("usd", 0.0))
        return text

    def ai_usage_reset(self):
        prov = self.ai["provider"]
        if not (self.cfg["ai_usage"] or {}).get(prov):
            return
        if wx.MessageBox("شمارنده‌ی مصرف %s صفر شود؟" % dict(AI_PROVIDERS)[prov], "شمارنده‌ی توکن",
                         wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
        allu = dict(self.cfg["ai_usage"] or {})
        allu.pop(prov, None)
        self.cfg.set("ai_usage", allu)
        self.panel.refresh()

    def _ask_text(self, title, prompt, value="", password=False):
        """پنجره‌ی ورود متن هم‌تم برنامه. فقط با کلیک کاربر باز می‌شود و فوکوس را می‌گیرد."""
        dlg = ThemedAskDialog(title, prompt, value, password)
        try:
            if self.cfg["stream_mode"]:
                set_capture_exclusion(dlg, True)
            dlg.CentreOnScreen()
            dlg.Raise()
            dlg.tc.SetFocus()
            dlg.tc.SelectAll()
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.tc.GetValue().strip()
            return None
        finally:
            dlg.Destroy()

    def ai_edit_model(self):
        prov = self.ai["provider"]
        name = dict(AI_PROVIDERS)[prov]
        value = self._ask_text("مدل %s" % name, "نام دقیق مدل را وارد کنید (باید قابلیت دیدن تصویر داشته باشد):",
                               self.ai["models"].get(prov, ""))
        if value is None:
            return
        value = value.strip().strip("\"'")
        if not value or re.search(r"\s", value):
            self._ai_status("نام مدل خالی است یا فاصله دارد", "err")
            return
        self.ai["models"][prov] = value
        self.ai["dirty"] = True
        self._ai_status("مدل تغییر کرد؛ برای اعمال، «ذخیره» را بزنید", "idle")

    def ai_set_style(self, style):
        if style in dict(AI_STYLES):
            self.cfg.set("ai_style", style)
            self.panel.set_state("سبک ترجمه: %s" % dict(AI_STYLES)[style], "ok", 2500)
            self.panel.Refresh()

    def ai_edit_context(self, which):
        key = "ai_" + which                      # ai_game | ai_genre
        label = "نام بازی" if which == "game" else "ژانر بازی"
        hint = ("نام بازی را وارد کنید (برای پاک‌کردن، خالی بگذارید):" if which == "game" else "")
        value = self._ask_text(label, hint, self.cfg[key])
        if value is None:
            return
        self.cfg.set(key, " ".join(value.split())[:60])
        self.panel.Refresh()

    def ai_edit_token(self):
        prov = self.ai["provider"]
        name = dict(AI_PROVIDERS)[prov]
        value = self._ask_text("توکن %s" % name, "توکن (API Key) را بچسبانید. هنگام تایپ نمایش داده نمی‌شود:",
                               "", password=True)
        if value is None:
            return
        value = value.strip().strip("\"'")
        if value.lower().startswith("bearer "):
            value = value[7:].strip()
        if not value or re.search(r"\s", value):
            self._ai_status("توکن خالی است یا فاصله دارد", "err")
            return
        self.ai["tokens"][prov] = value
        self.ai["dirty"] = True
        self._ai_status("توکن وارد شد؛ برای ماندگاری، «ذخیره» را بزنید", "idle")

    def ai_save(self):
        prov = self.ai["provider"]
        model = (self.ai["models"].get(prov) or "").strip()
        if not model:
            self._ai_status("نام مدل خالی است", "err")
            return
        tokens, models = dict(self.cfg["ai_tokens"] or {}), dict(self.cfg["ai_models"] or {})
        draft = self.ai["tokens"].get(prov)
        if draft:
            enc = secret_encrypt(draft)
            if not enc:
                self._ai_status("رمزگذاری با ویندوز انجام نشد؛ توکن ذخیره نشد", "err")
                return
            tokens[prov] = enc
        elif not tokens.get(prov) and prov != "custom":
            self._ai_status("ابتدا توکن را وارد کنید", "err")
            return
        models[prov] = model
        self.cfg.set("ai_tokens", tokens)
        self.cfg.set("ai_models", models)
        self.cfg.set("ai_provider", prov)
        self.ai["tokens"].pop(prov, None)
        self.ai["dirty"] = False
        self._ai_status("ذخیره شد — «بررسی اتصال» را بزنید تا مطمئن شوید", "ok")
        self.panel.set_state("تنظیمات هوش مصنوعی ذخیره شد", "ok", 3000)

    def ai_clear_token(self):
        prov = self.ai["provider"]
        tokens = dict(self.cfg["ai_tokens"] or {})
        if tokens.pop(prov, None) is None and prov not in self.ai["tokens"]:
            return
        self.cfg.set("ai_tokens", tokens)
        self.ai["tokens"].pop(prov, None)
        self._ai_status("توکن حذف شد", "ok")

    def ai_test(self):
        if self.ai["testing"]:
            return
        prov = self.ai["provider"]
        model = (self.ai["models"].get(prov) or "").strip()
        token = self.ai["tokens"].get(prov) or self._ai_saved_token(prov)
        if not token and prov != "custom":
            self._ai_status("ابتدا توکن را وارد کنید", "err")
            return
        if not model:
            self._ai_status("نام مدل خالی است", "err")
            return
        self.ai["testing"] = True
        self._ai_status("در حال بررسی اتصال…", "busy")

        def work():
            try:
                res = (ai_check(prov, model, token, self.cfg["ai_custom_url"]), "ok")
            except EngineError as exc:
                msg = str(exc)
                if exc.kind == "net":                       # تست خودکار: اینترنت یا تحریم؟
                    msg += " " + diagnose_connection(prov, self.cfg["ai_custom_url"])
                res = (msg, "err")
            except Exception as exc:
                dbg("ai_check crashed: %r" % (exc,))
                res = ("خطای ناشناخته در بررسی اتصال", "err")
            wx.CallAfter(self._ai_test_done, prov, res)

        threading.Thread(target=work, daemon=True).start()

    def _ai_test_done(self, prov, res):
        self.ai["testing"] = False
        if self._quitting:
            return
        if prov == self.ai["provider"]:
            self._ai_status(res[0], res[1])
        else:
            self.panel.refresh()

    # ── آفلاین ──
    def ocr_label(self):
        return ocr_lang_info(self.cfg["ocr_lang"])[2]

    def change_ocr_lang(self, delta):
        codes = [c[0] for c in OCR_LANGS]
        cur = self.cfg["ocr_lang"]
        idx = codes.index(cur) if cur in codes else 0
        self.cfg.set("ocr_lang", codes[(idx + int(delta)) % len(codes)])
        self.off.update(progress=0.0, msg="", kind="idle")
        self.offline_probe()
        self.panel.set_state("زبان OCR: %s" % self.ocr_label(), "ok", 2400)

    def _auto_offline_check(self):
        """موتور آفلاین انتخاب شده و چیزی کم است → خودکار دانلود/نصب (برای هر زبان فقط یک‌بار در هر اجرا)."""
        try:
            if self._quitting or self.cfg["engine"] != "offline" or self.off["busy"] or self.off.get("paused"):
                return
            lang = self.cfg["ocr_lang"]
            if getattr(self, "_auto_off_lang", None) == lang or self.off.get("argos") == "checking":
                return
            if (not self.off["tess_exe"]) or (not self.off["tess_model"]) or self.off.get("argos") in ("nolib", "missing", "error"):
                self._auto_off_lang = lang
                self.offline_download()
        except Exception as exc:
            dbg("auto offline: %r" % (exc,))

    def offline_probe(self, bg=True):
        """بررسی اجزای آفلاین. پیش‌فرض پس‌زمینه: find_tesseract/PATH و چک مدل روی ترد جدا تا
        کلیک موتور ترجمه بدون کندی صورت بگیرد."""
        lang = self.cfg["ocr_lang"]
        if bg:
            def probe_work():
                try:
                    t = find_tesseract() is not None
                    m = tess_model_installed(lang)
                    wx.CallAfter(self._off_probe_done, lang, t, m)
                except Exception:
                    dbg("offline_probe bg failed")
            threading.Thread(target=probe_work, daemon=True).start()
            return
        self._off_probe_done(lang, find_tesseract() is not None, tess_model_installed(lang))

    def _off_probe_done(self, lang, tess_exe, tess_model):
        if self._quitting or lang != self.cfg["ocr_lang"]:
            return
        self.off["tess_exe"], self.off["tess_model"] = tess_exe, tess_model
        self.off["size_text"] = ""
        if not tess_model:
            def size_work():
                n = remote_size(TESSDATA_URL % lang)
                if n:
                    wx.CallAfter(self._off_size, lang, "حجم مدل OCR این زبان: %s" % fmt_mb(n))
            threading.Thread(target=size_work, daemon=True).start()
        src = ocr_lang_info(lang)[1]
        self.off["argos"] = "checking"

        def argos_work():
            try:
                wx.CallAfter(self._off_argos, lang, argos_status(src))
            except Exception:
                dbg("argos_status failed")
                wx.CallAfter(self._off_argos, lang, "error")

        threading.Thread(target=argos_work, daemon=True).start()
        self.panel.refresh()
        self._auto_offline_check()

    def _off_size(self, lang, text):
        if not self._quitting and lang == self.cfg["ocr_lang"]:
            self.off["size_text"] = text
            self.panel.refresh()

    def _off_argos(self, lang, status):
        if not self._quitting and lang == self.cfg["ocr_lang"]:
            self.off["argos"] = status
            self.panel.refresh()
            if status == "ok":
                threading.Thread(target=lambda: (_nllb_load() if self.cfg["engine"] == "offline" else None),
                                 daemon=True).start()
            self._auto_offline_check()

    def offline_pause(self):
        """در حال دانلود: توقف. در حالت متوقف: ادامه از همان نقطه."""
        if self.off["busy"]:
            ctl = getattr(self, "_dl_ctl", None)
            if ctl is not None:
                ctl.pause = True
                self.off["msg"] = "در حال توقف…"
                self.panel.refresh()
        elif self.off.get("paused"):
            self.offline_download()

    def offline_download(self):
        if self.off["busy"]:
            return
        if not _vcruntime_ok():                      # ctranslate2 به VC++ نیاز دارد؛ اول با اجازه‌ی کاربر نصب می‌شود
            self.ensure_prereqs(["vc"], self.offline_download)
            return
        lang = self.cfg["ocr_lang"]
        self._dl_ctl = ctl = DownloadCtl()
        self.off.update(busy=True, paused=False, progress=self.off.get("progress", 0.0) if self.off.get("paused") else 0.0,
                        msg="شروع دانلود…", kind="busy")
        self.panel.set_state("دانلود مدل‌های آفلاین…", "busy")
        self.panel.refresh()

        def cb(frac, msg):
            wx.CallAfter(self._off_progress, frac, msg)

        def work():
            try:
                res = (download_offline_models(lang, cb, ctl), "ok")
            except DownloadPaused:
                res = ("دانلود متوقف شد؛ برای ادامه از همان‌جا، «ادامه» را بزنید.", "paused")
            except EngineError as exc:
                res = (str(exc), "err")
            except Exception as exc:
                dbg("download_offline_models crashed: %r" % (exc,))
                res = ("خطای ناشناخته در دانلود", "err")
            wx.CallAfter(self._off_done, res)

        threading.Thread(target=work, daemon=True).start()

    def _off_progress(self, frac, msg):
        if self._quitting:
            return
        self.off["progress"], self.off["msg"] = float(frac), msg
        self.panel.refresh()

    def _off_done(self, res):
        if self._quitting:
            return
        self.off.update(busy=False, paused=(res[1] == "paused"), msg=res[0], kind=res[1])
        if res[1] == "ok":
            self.off["progress"] = 1.0
        if res[1] == "paused":
            self.panel.set_state("دانلود متوقف شد", "ok", 3000)
            self.panel.refresh()
            return
        self.offline_probe()
        self.panel.set_state("دانلود مدل‌ها تمام شد" if res[1] == "ok" else "دانلود کامل نشد", res[1], 4000)

    # ── انتخاب مدل ترجمه‌ی آفلاین ──
    def change_nllb_model(self, delta):
        if self.off["busy"]:
            self.panel.set_state("تا پایان دانلود، مدل ترجمه را نمی‌شود عوض کرد", "err", 3000)
            return
        keys = list(NLLB_MODEL_KEYS)
        cur = self.cfg["nllb_model"]
        idx = keys.index(cur) if cur in keys else 0
        new = keys[(idx + int(delta)) % len(keys)]
        self.cfg.set("nllb_model", new)                      # ذخیره‌ی دیسکی در پس‌زمینه؛ UI منتظر نمی‌ماند
        _NLLB_SEL["key"] = new if new in NLLB_MODELS else _NLLB_SEL["key"]   # انتخاب آنی؛ عوض‌شدن نام روی دکمه فوری است
        self.off.update(progress=0.0, msg="", kind="idle", paused=False)
        self._auto_off_lang = self.cfg["ocr_lang"]           # دانلودِ چندصدمگابایتی/چندگیگابایتی هرگز خودکار شروع نشود
        self.panel.refresh()
        self.panel.set_state("مدل ترجمه: %s" % nllb_spec()["label"], "ok", 2800)
        # کارهای سنگین (توقف ترجمه‌ی زنده، آزادسازی مدل قبلی، بررسی نصب) فقط یک‌بار و بعد از آخرین کلیک
        old = getattr(self, "_nllb_timer", None)
        if old is not None:
            try:
                old.Stop()
            except Exception:
                pass
        self._nllb_timer = wx.CallLater(550, self._nllb_apply_model)

    def _nllb_apply_model(self):
        self._nllb_timer = None
        if self._quitting:
            return
        if self.live.running:
            self.live_stop("مدل ترجمه عوض شد؛ ترجمه‌ی زنده متوقف شد")
        threading.Thread(target=nllb_unload_stale, daemon=True).start()   # مدل قبلی در ترد پس‌زمینه از حافظه آزاد می‌شود
        self.offline_probe()

    # ═════════════ ترجمه‌ی زنده‌ی بازی (Game Live Mode) ═════════════
    def live_roi_checked(self, fresh=False):
        """(roi، پیام خطا). ROI ذخیره‌شده را با مانیتورهای فعلی می‌سنجد (تغییر رزولوشن/مانیتور → نامعتبر)."""
        roi = self.cfg["game_live_roi"]
        if not roi:
            return None, "محدوده‌ی زیرنویس هنوز انتخاب نشده است"
        mons = [tuple(m) for m in (list_monitor_rects() if fresh else (self._monitor_rects_cache or list_monitor_rects()))]
        mon = tuple(roi["mon"])
        if mon not in mons:
            return None, "چیدمان یا رزولوشن مانیتور تغییر کرده؛ محدوده‌ی زیرنویس را دوباره انتخاب کنید"
        x, y, w, h = roi["rect"]
        if x < mon[0] or y < mon[1] or x + w > mon[0] + mon[2] or y + h > mon[1] + mon[3]:
            return None, "محدوده‌ی زیرنویس بیرون از مانیتور است؛ دوباره انتخاب کنید"
        return roi, None

    def live_roi_text(self):
        roi, err = self.live_roi_checked()
        if roi is None:
            return err if self.cfg["game_live_roi"] else "محدوده‌ی زیرنویس انتخاب نشده"
        x, y, w, h = roi["rect"]
        return "محدوده: %d×%d  در  (%d, %d)" % (w, h, x, y)

    def live_toggle(self):
        if self._quitting:
            return
        now = time.time()
        if now - self._last_live_key < 0.6:           # RegisterHotKey و polling هم‌زمان نزنند
            return
        self._last_live_key = now
        if self.live.running:
            self.live_stop()
        else:
            self.live_start()

    def _panel_overlaps(self, roi):
        try:
            pw, ph = self.panel._size()
            px, py = self.panel.pos
            x, y, w, h = roi["rect"]
            return self.panel._visible() and px < x + w and px + pw > x and py < y + h and py + ph > y
        except Exception:
            return False

    def live_start(self):
        if self._quitting or self.live.running or self.layer.active:
            return
        roi, err = self.live_roi_checked(fresh=True)
        if roi is None:
            self._live_set_state("error", err)
            self.panel.set_state(err, "err", 6000)
            return
        msg = GameLiveController.preflight()
        if msg:
            self._live_set_state("error", msg)
            self.panel.set_state(msg, "err", 8000)
            return
        if exclusive_fullscreen_active():
            self.panel.set_state("هشدار: بازی احتمالاً Exclusive Fullscreen است؛ اگر متن خوانده نشد آن را روی Borderless بگذارید",
                                 "err", 7000)
        # پنل برنامه از عکس حذف می‌شود تا متن خودِ برنامه به‌عنوان زیرنویس OCR نشود
        self._live_panel_excluded = set_capture_exclusion(self.panel, True)
        if not self._live_panel_excluded and self._panel_overlaps(roi):
            self.panel.set_state("پنل روی محدوده‌ی زیرنویس است؛ آن را جابه‌جا کنید وگرنه متن پنل هم خوانده می‌شود", "err", 8000)
        self.live_stats = {}
        self.live_last_ocr = ""
        self._live_set_state("ready", "آماده — در حال بارگذاری مدل ترجمه…")
        self.live.start(roi)
        self.panel.refresh()

    def live_stop(self, reason=None):
        try:
            self.live.stop()
        except Exception as exc:
            dbg("live stop failed: %r" % (exc,))
        self.live_overlay.hide_text()
        if self._live_panel_excluded:
            set_capture_exclusion(self.panel, bool(self.cfg["stream_mode"]))
            self._live_panel_excluded = False
        self._live_set_state("stopped", reason or "متوقف")
        self.panel.refresh()

    def live_select_roi(self):
        if self.layer.active or self._quitting:
            return
        if self.live.running:
            self.live_stop("متوقف شد تا محدوده‌ی جدید انتخاب شود")
        self.tray_notice.hide_notice()
        self._pending = None
        if self.box.mode != "hidden":
            self.box.hide_box()
            time.sleep(0.04)
        self.live_overlay.hide_text()
        if self.panel.suspend():
            time.sleep(0.05)
        ok, err = self.layer.begin(self._on_live_roi)
        if ok:
            self.register_esc()
        else:
            self.panel.resume()
            self.panel.set_state(err or "گرفتن عکس صفحه ممکن نشد", "err", 6000)

    def _on_live_roi(self, img, rect):
        x, y, w, h = [int(v) for v in rect]
        mon = tuple(monitor_at(x + w // 2, y + h // 2))
        self.cfg.set("game_live_roi", {"rect": [x, y, w, h], "mon": list(mon)})
        self._live_set_state("stopped", "محدوده‌ی زیرنویس ذخیره شد")
        self.panel.refresh()
        self.panel.set_state("محدوده‌ی زیرنویس ذخیره شد (%d×%d)" % (w, h), "ok", 4000)
        exe = find_tesseract()
        if exe and tess_model_installed("eng"):
            def work():                                   # یک تست OCR روی همین ناحیه برای بازخورد فوری
                msg = None
                tmp = tempfile.mkdtemp(prefix="eshlive_")
                try:
                    t = live_norm_text(_tess_read(exe, ocr_preprocess(img), "eng", tmp, None, "roi", psm="6"))
                    msg = ("متن پیدا شد: «%s»" % t[:40]) if t else \
                        "هنوز متنی در این محدوده خوانده نشد (هنگام نمایش زیرنویس دوباره بررسی می‌شود)"
                except Exception as exc:
                    dbg("live roi test failed: %r" % (exc,))
                finally:
                    shutil.rmtree(tmp, ignore_errors=True)
                if msg:
                    wx.CallAfter(self._live_roi_test_done, msg)
            threading.Thread(target=work, daemon=True).start()

    def _live_roi_test_done(self, msg):
        if not self._quitting:
            self.panel.set_state(msg, "ok", 6000)

    def _cycle_cfg(self, key, values, delta):
        cur = self.cfg[key]
        idx = values.index(cur) if cur in values else 0
        self.cfg.set(key, values[(idx + int(delta)) % len(values)])
        self.panel.refresh()

    def live_change_rate(self, delta):
        self._cycle_cfg("game_live_rate", [r[0] for r in LIVE_RATES], delta)

    def live_change_font(self, delta):
        self._cycle_cfg("game_live_overlay_font_size", list(LIVE_FONT_SIZES), delta)

    def live_change_opacity(self, delta):
        self._cycle_cfg("game_live_overlay_opacity", list(LIVE_OPACITIES), delta)

    def live_toggle_source(self):
        self.cfg.set("game_live_show_source", not self.cfg["game_live_show_source"])
        self.panel.refresh()

    def live_request_dump(self):
        if not self.live.running:
            self.panel.set_state("ابتدا ترجمه‌ی زنده را شروع کنید", "err", 3000)
            return
        self.live.request_dump()
        self.panel.set_state("در چرخه‌ی بعدیِ OCR، تصویر و متن ذخیره می‌شود…", "ok", 3000)

    # ── بازخوردها از نخ‌های ترجمه‌ی زنده (همه از مسیر wx.CallAfter) ──
    def _live_set_state(self, code, text):
        if self._quitting:
            return
        if code not in ("stopped",) and not self.live.running and code != "error":
            return                                         # پیام دیررسیده بعد از توقف
        self.live_state = (code, text)
        if code == "error":
            self.panel.set_state(text, "err", 6000)
        self.panel.refresh()

    def _live_stats(self, d):
        if self._quitting or not self.live.running:
            return
        self.live_stats = d
        if self.panel.page == "live":
            self.panel.refresh()

    def _live_result(self, gen, src, fa, ms):
        if self._quitting or not self.live.running or gen != self.live.gen:
            return
        roi, _err = self.live_roi_checked()
        if roi is None:
            return
        try:
            self.live_overlay.show_text(fa, src, roi["rect"])
        except Exception as exc:
            dbg("live overlay failed: %r" % (exc,))
            return
        self._live_set_state("reading", "در حال خواندن متن")

    def _live_ocr_seen(self, sid, text):
        if self._quitting or sid != self.live.session or not self.live.running:
            return
        self.live_last_ocr = text or ""
        if self.panel.page == "live":
            self.panel.refresh()

    def _live_preview(self, gen, text):
        """متن انگلیسیِ خوانده‌شده را فوراً (تا آماده‌شدن ترجمه) روی صفحه نشان می‌دهد."""
        if self._quitting or not self.live.running or gen != self.live.gen:
            return
        roi, _err = self.live_roi_checked()
        if roi is None:
            return
        try:
            self.live_overlay.show_text("… در حال ترجمه", text, roi["rect"], force_src=True)
        except Exception as exc:
            dbg("live preview failed: %r" % (exc,))

    def _live_clear(self, gen):
        if self._quitting or gen != self.live.gen:
            return
        self.live_overlay.hide_text()

    def _live_fatal(self, msg):
        if self._quitting:
            return
        self.live_stop()
        self._live_set_state("error", msg)

    def _live_thread_ended(self, sid):
        if self._quitting or sid != self.live.session:
            return
        if self.live_state[0] != "stopped":
            self.live_overlay.hide_text()
            self._live_set_state("stopped", "متوقف")

    def _live_overlay_pos(self, roi_rect, w, h):
        """جای پنجره‌ی ترجمه: با تنظیم «مانیتور/گوشه‌ی خروجی» موجود؛ پیش‌فرض روی خودِ ناحیه‌ی انتخاب‌شده‌ی کاربر."""
        rx, ry, rw, rh = roi_rect
        mons = list_monitor_rects()
        self._monitor_rects_cache = mons
        src = tuple(monitor_at(rx + rw // 2, ry + rh // 2))
        try:
            idx = int(self.cfg["output_monitor"] or 0)
        except Exception:
            idx = 0
        tm = tuple(mons[idx - 1]) if 0 < idx <= len(mons) else src
        tx, ty, tw, th = tm
        w, h = min(w, tw), min(h, th)
        corner = self.cfg["output_corner"]
        if corner != "same":
            m = 24
            nx = {"tl": tx + m, "bl": tx + m, "tr": tx + tw - w - m, "br": tx + tw - w - m}.get(corner, tx + (tw - w) // 2)
            ny = {"tl": ty + m, "tr": ty + m, "bl": ty + th - h - m, "br": ty + th - h - m}.get(corner, ty + (th - h) // 2)
        elif tm != src:
            sx, sy, sw, sh = src
            nx = tx + int(round((rx + (rw - w) // 2 - sx) * tw / float(max(1, sw))))
            ny = ty + int(round((ry + rh + 10 - sy) * th / float(max(1, sh))))
        else:
            nx, ny = rx, ry                                    # رویِ خودِ ناحیه‌ی انتخاب‌شده‌ی کاربر نشان داده می شود
        nx = max(tx, min(nx, tx + tw - w))
        ny = max(ty, min(ny, ty + th - h))
        return nx, ny

    # ── مانیتور خروجی ──
    def refresh_monitors(self):
        self._monitor_rects_cache = list_monitor_rects()

    def out_label(self):
        try:
            idx = int(self.cfg["output_monitor"] or 0)
        except Exception:
            idx = 0
        mons = self._monitor_rects_cache or list_monitor_rects()
        if idx <= 0:
            return "همان مانیتور عکس‌برداری"
        if idx > len(mons):
            return "مانیتور انتخاب‌شده در دسترس نیست"
        return "مانیتور %d — %d×%d" % (idx, mons[idx - 1][2], mons[idx - 1][3])

    def set_output_monitor(self, idx):
        mons = list_monitor_rects()
        self._monitor_rects_cache = mons
        idx = int(idx)
        if idx < 0 or idx > len(mons):
            return
        self.cfg.set("output_monitor", idx)
        self.panel.refresh()
        self.panel.set_state("مانیتور خروجی: %s" % self.out_label(), "ok", 2600)

    def set_output_corner(self, key):
        if key in dict(CORNERS):
            self.cfg.set("output_corner", key)
            self.panel.refresh()
            self.panel.set_state("جای نمایش: %s" % dict(CORNERS)[key], "ok", 2500)

    def _output_anchor(self, rect):
        """محل نمایش نتیجه را روی مانیتور خروجی می‌برد (هم‌نسبت با جای انتخاب روی مانیتور مبدأ)."""
        self.box.bounds = None
        try:
            idx = int(self.cfg["output_monitor"] or 0)
        except Exception:
            idx = 0
        corner = self.cfg["output_corner"]
        mons = list_monitor_rects()
        self._monitor_rects_cache = mons
        if corner != "same":                       # جای ثابت: گوشه‌ی مانیتور خروجی (یا مانیتور عکس‌برداری)
            x, y, w, h = rect
            if 0 < idx <= len(mons):
                tx, ty, tw, th = mons[idx - 1]
            else:
                tx, ty, tw, th = monitor_at(x + w // 2, y + h // 2)
            w, h = min(w, tw), min(h, th)
            m = 24
            nx = {"tl": tx + m, "bl": tx + m, "tr": tx + tw - w - m, "br": tx + tw - w - m}.get(corner, tx + (tw - w) // 2)
            ny = {"tl": ty + m, "tr": ty + m, "bl": ty + th - h - m, "br": ty + th - h - m}.get(corner, ty + (th - h) // 2)
            self.box.bounds = (tx, ty, tw, th)
            return (max(tx, nx), max(ty, ny), w, h)
        if idx <= 0:
            return rect
        if idx > len(mons):
            return rect
        tx, ty, tw, th = mons[idx - 1]
        x, y, w, h = rect
        sx, sy, sw, sh = monitor_at(x + w // 2, y + h // 2)
        if (sx, sy, sw, sh) == (tx, ty, tw, th):
            self.box.bounds = (tx, ty, tw, th)
            return rect
        nx = tx + int(round((x - sx) * tw / float(max(1, sw))))
        ny = ty + int(round((y - sy) * th / float(max(1, sh))))
        w, h = min(w, tw), min(h, th)
        nx = max(tx, min(nx, tx + tw - w))
        ny = max(ty, min(ny, ty + th - h))
        self.box.bounds = (tx, ty, tw, th)
        return (nx, ny, w, h)

    def test_output_monitor(self):
        if self.layer.active or self.box.mode in ("busy", "result"):
            self.panel.set_state("ابتدا نتیجه‌ی باز را ببندید", "err", 3000)
            return
        mons = list_monitor_rects()
        try:
            cap = int(self.cfg["capture_monitor"] or 0)
        except Exception:
            cap = 0
        mon = mons[cap - 1] if 0 < cap <= len(mons) else monitor_at(*_cursor_pos())
        anchor = (mon[0] + mon[2] // 2 - 170, mon[1] + mon[3] // 2 - 32, 340, 64)
        self.box.anchor = self._output_anchor(anchor)
        self.box.show_error("نتیجه‌ی ترجمه این‌جا نمایش داده می‌شود (%s)" % self.out_label())

    # ── اجرای ترجمه با موتور هوش مصنوعی / آفلاین (در نخ پس‌زمینه) ──
    def _run_text_engine(self, img, rect, engine):
        self._job += 1
        job = self._job
        snap = prepare_upload(img)
        width = rect[2]
        lang = self.cfg["ocr_lang"]
        prov = self.cfg["ai_provider"]
        model = ((self.cfg["ai_models"] or {}).get(prov) or AI_DEFAULT_MODELS.get(prov, "")).strip()
        token = self._ai_saved_token(prov) if engine == "ai" else ""
        prompt = build_ai_prompt(self.cfg["ai_style"], self.cfg["ai_game"])
        if engine == "ai" and not token and prov != "custom":
            wx.CallAfter(self._text_done, job, None, "توکن هوش مصنوعی ذخیره نشده؛ صفحه‌ی «هوش مصنوعی» را باز کنید.", width)
            return

        cancel = self._cancel = CancelToken()

        overlay_mode = engine == "offline" and bool(self.cfg["text_over_text"])

        def work():
            text = err = overlay = None
            try:
                if cancel.cancelled:
                    return
                if engine == "ai":
                    text, usage = ai_translate(prov, model, token, snap, prompt, self.cfg["ai_custom_url"])
                    if usage:
                        wx.CallAfter(self._ai_usage_add, prov, model, usage)
                elif overlay_mode:
                    try:
                        overlay = (snap, offline_regions(snap, lang, cancel))
                    except EngineError as exc_ov:
                        if cancel.cancelled:
                            raise
                        dbg("overlay mode failed, plain text fallback: %s" % exc_ov)
                        text = offline_translate(snap, lang, cancel)       # حداقل متن ترجمه‌شده دیده شود
                else:
                    text = offline_translate(snap, lang, cancel)
            except EngineError as exc:
                err = str(exc)
                if engine == "ai" and exc.kind == "net" and not cancel.cancelled:
                    err += " — " + diagnose_connection(prov, self.cfg["ai_custom_url"])
            except Exception as exc:
                dbg("%s translate crashed: %r" % (engine, exc))
                err = "خطای ناشناخته در ترجمه؛ جزئیات در debug.log"
            wx.CallAfter(self._text_done, job, text, err, width, overlay)

        self.panel.set_state("در حال ترجمه", "busy")
        threading.Thread(target=work, daemon=True).start()

    def cancel_translation(self):
        """بستنِ نتیجه هنگام «در حال ترجمه»: کارِ جاری لغو و نتیجه‌ی دیررسیده نادیده گرفته می‌شود."""
        self._job += 1
        tok = getattr(self, "_cancel", None)
        if tok is not None:
            tok.cancel()
        try:
            self.panel.set_state("ترجمه لغو شد", "ok", 2500)
        except Exception:
            pass

    def _text_done(self, job, text, err, width, overlay=None):
        if self._quitting or job != self._job:
            return
        if self.box.mode != "busy":              # کاربر نتیجه را بسته است
            self.panel.set_state("برنامه آماده استفاده است", "ok")
            return
        if err:
            dbg("text engine error: " + err)
            self._on_error(err)
            return
        try:
            if overlay is not None:
                img = render_overlay_image(overlay[0], overlay[1])
            else:
                img = render_text_image(text, width)
        except Exception as exc:
            dbg("render_text_image failed: %r" % (exc,))
            self._on_error("نمایش متن ترجمه ممکن نشد.")
            return
        self._on_result(img)

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
        parent = os.path.dirname(cur) or cur
        try:
            os.makedirs(parent, exist_ok=True)
        except Exception:
            pass
        dlg = wx.DirDialog(None, "مسیر را انتخاب کنید؛ داخل آن پوشه‌ی ESHTranslator ساخته می‌شود",
                           defaultPath=parent, style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        try:
            if dlg.ShowModal() == wx.ID_OK and dlg.GetPath():
                path = dlg.GetPath()
                if os.path.basename(os.path.normpath(path)).lower() != "eshtranslator":
                    path = os.path.join(path, "ESHTranslator")
                try:
                    os.makedirs(path, exist_ok=True)
                except Exception:
                    pass
                self.cfg.set("save_dir", path)
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


    def quit(self, force=False):
        """force=True برای «خروج کامل» (دکمه‌ی پنل و منوی Tray): حتی وقتی پنل پین است خارج می‌شود."""
        if self._quitting:
            return
        panel = getattr(self, "panel", None)
        if not force and panel is not None and getattr(panel, "pinned", False):
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
            self.live.stop(join_timeout=0.6)          # نخ‌های ترجمه‌ی زنده و Tesseract در حال اجرا آزاد می‌شوند
            self.live_overlay.hide_text()
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
        for hid in (ID_SNIP, ID_CLOSE, ID_ESC, ID_LIVE):
            try:
                self.UnregisterHotKey(hid)
            except Exception:
                pass
        try:
            self.tray.RemoveIcon()
            self.tray.Destroy()
        except Exception:
            pass
        self._clear_webview_cookies()
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)    # آزادسازی قفل Sleep
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
        for w in (self.layer, self.box, self.live_overlay, self.panel, self.tray_notice):
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
            self._clear_webview_cookies(files_only=True)
        except Exception:
            pass
        try:
            self.Destroy()
            app = wx.GetApp()
            if app is not None:
                app.ExitMainLoop()
        except Exception:
            pass


        _hard_exit(0)


APP_ICON_B64 = (
    "AAABAAcAEBAAAAAAIABeAwAAdgAAABgYAAAAACAAQQYAANQDAAAgIAAAAAAgAHwJAAAVCgAAMDAAAAAAIABlEgAAkRMAAEBAAAAA"
    "ACAAwRwAAPYlAACAgAAAAAAgAFBXAAC3QgAAAAAAAAAAIADoDwEAB5oAAIlQTkcNChoKAAAADUlIRFIAAAAQAAAAEAgGAAAAH/P/"
    "YQAAAyVJREFUeJyVk2toU3cYxp///5w0zcXEWi+DZrZStTFFp1XsDSu4smq8K/FScdovdQQF632iHCIKnUTKHEwm4uqHgYu3Klqt"
    "qNVqlYJiq51tvTSNNVqDtklNzDlJc9596BizONh+8H56nw/Py/s8AABJkrgIQABAksQ9DodAAMPg/EcEAWD/Q/8XDER83Pf7vtvb"
    "+nSlNRxRYuH+xg+K/PAVjzyqDAZ71vt8MdegVh3iiACA49bdr1xd/v1lgXc5XPn4s3b0KE/cYAqFRJo3x8qOuZigphYUGAAIkDwa"
    "zJ4tABBRXGy25OXpgMamopZF30aiM76pGWqvvCjlutOGHwDAYrHoPneCCPPIroYRpsAU38uc4Z4La5GZYSY1oTc899Y0/+5uTCqc"
    "sLcoNxCL/HrZHWx6sA6tTxrUK9d6+bYtC5nP2wAwhknuI255ZglV7DsUBFFYH5G9pvvNtZpwtBdEbWJEpoyTJy4mEZHx4ZOlViBV"
    "JCJ9R0e5yInQ9nVe1Y7Ornk/nr5gbfsoH7+ysbzdKGpL4obk5OxK6ZptWP+49509c/1LVsXjmWOX+169zlWBAVXDo2JKVtawd9Om"
    "9bDzdZusoVB1zaWrq2fOn/vhfcvNukmvm1nHguXOvlRDbFTt2TApil4RNIu1RmMCKgQkwID09GSbzZZUX18vgujxEefOt+eMrNtW"
    "OutF5vUz8vhtW28gQX5Tp5eSBwaowL2rduSckhxORFqvt+zv16bb7V9k798dz7dPTmTnTmyvmTIjWLXzQCuU+HOE+ppy1tgD6OkP"
    "OSvLHh0um3oISuKNqbWllAFgxVnidI3OeMDcFwzJCp7VbfzpnD0S3VBx93bpxP5wl9Dtd63D07QVK1PWZGeKlr720Jg7zzJOVumX"
    "ORkA5Fmg02sMphte+S1AYFBBAgeqT83ffOdexYLuN/lpkQAz617qkkZHEZO1OO7/8vGerNLCT8IvSeBwAS5JAne5VAJARAJ++a1w"
    "Scsf9vzegbQUJWr2czFcPSHtqO/g9puf9mIoDofA/7kQGEDEwP+9XJ+DweMRPA6HMFgCgAAmSRIHgD8BYAdVBbWqEeQAAAAASUVO"
    "RK5CYIKJUE5HDQoaCgAAAA1JSERSAAAAGAAAABgIBgAAAOB3PfgAAAYISURBVHicrVZrcJTVGX7O+b5vv2w2l90UyCZBIcglQOLY"
    "UpFIBC+UolzbsHa4eJtgFSsZuQyd0tFNqChMGgGn1elUqjN2OnEXGYINF0kViM1EwJiQXc1lQxKyIYFN9n7fb7+3PzbpBfrHyzPz"
    "zpxzfpzneZ9zzvse4Haw8fieYbEIDAAHIAAgs5mbU9Pvh4wBAOcAkXAbN0yCyQTh25AxEDHzg1VC9ercpx9u7SgzhSOxPLdXq/hH"
    "HekqfXI+ONxx4OpV37cWzgCwd62V2/5xtmpfd3+WLk0rDEbDjcSE1uFkXOtVFE0kmrhyevJNPkjJSw1N/Rf1+uxsn88XAKAi5SgA"
    "0PhYBaDOnDlTcjgccZHOtOkKuy89dKCzT5SzDcKx0WvPl7e3/GlCgWnePM3KmFyULquHc4X4GsawfHZeUvT5kAYgCiD5P46kSCSX"
    "y5UGIMExf1LaVM4DsqDReGORyMt9TqvFZtPU1tZqt508KdstVXi6v+1Ks7Nvlz4jY8nmlXNf7x6OjOYXFaUBEGEhDiIBRAyAAsZi"
    "2L4dyZISMZWVzaYp+MORurHSx4KxJeuUg9Nmzb31njIAS81LxfJCnKu8TyKTAbsAMF3hlNxbLE+R/hdEXlwcH7I2XDk1xfDgprGg"
    "LuuO2bthPebXK3EpxnmcAZIw6v5szqpH6i9u3SB/nj/jxjRlrOaBr7qMF6yf7s4+ceY5MuYtkHr7Trs3rD2tf/HX8xNPbnyO+f0R"
    "aX/13pRSa/38RXt/35788U+iwwuW+TJbLo9wIhKJSCAiXYf9XHbz5eMgoonIjEVo8SuVh3Wd3Q2MiLIGb9SCiBv+fnaFQESi358o"
    "rKjM5WQhgZvW2luKiuoPzZzuMpKQ+fbLr3vVXufHBb3Ocr3j+jrZ3tMSLF2wVjPq9ucd++jZwnpLfTgSV4fuKas0fnFhEQGKGAx5"
    "GGNqelePlwCFAJegksphgqoSsan2rkPVZff3NOtE/6aoMueV8o3xAU9gSTwWW8Guj+gIUJOatIj4Vfvs0qM1C6v2r2HLXn3CHZc1"
    "GQDEyA+yNms9/vfdm02/I0BkKknISJ0Dh8mkAQDpwzPFM/Ydbnb+8BGXWrqSVu951QEiyqw7sd9oOXpGS0R83LaCwE1aUbUlZLT+"
    "dQTj6xMBIhK9Ppdx27bJDECGVqvVRxavCrBGq4992fXbWfaOivZ9b5Ccrp+0o3Byw4n4VXrMKC0PpmfmtAxEHZ4NFV+OmEw/01wf"
    "kQxfXFRurF4jZXxyoS2nb+StwLT86b5lZXtYMOgqrNwznwMIRiIRJ85aQrR0qahPhENdm8oL79m53dMYHeCa1r+tN4x0/fwvz7+W"
    "Ztn5Jk/cNc8HWfJzgGmUGMRYVGBQk/fZG4sqtvzC6bENWAU1qUJVkyl7JmAF4fx5JRDiwdwTJ9X8piMle4Xe5ClNVuf2waT36FMv"
    "dspdA+ccNW/8aGzNumelYFgqrtrFslUfJ3BBzslxlz2qeWZannF6ggtcYJic5IyLE29qXU2WfmR2RpFhx8MV+oSXh4LJ6M20/H8O"
    "PlXd77RdXrWx51rx2K92u3Ysvrfx4Au/rMfHx1p1Hxzd3a1k6YvDMd394UuRgKrM+uOnW995Sa6tG0rXdYdj7iAzA7waoEdLNJUK"
    "yS9l6yS3OxT5syyKshwNtB3/mprwbt0LC2z2ihp7950PDd9MRyzWZGN4c6uuTVsuRxY+eS+e0Jbk5J7vZXGDa0xju8x7W9qynnkH"
    "3qaJisAA8EVTkd3ihPuW5y9yQFFPfTYH1/orTO0dP93p6Ju10B/WesiX7M8YpcQkjwhtiAxTBOYb4NT79V3s0Iy7f/P58SP7b2sg"
    "jAHr16dK8DwrqBpQYbEI7PHHkwyAWndyEXye5Svt9gfK+4fmLvbGdZNiYUlJhnUKqYpf1kYPTL+z873cnC3s4L72WwlYqgL+H5jN"
    "HABYdbUKAPRRcwF62ksziU29e3TsjoJQNCOSJNaq1/cP5Rga2M6KdkpV2G8Is5nDbOYT/fvfaUsSQMQnVOI793IiBotFMJn+81lg"
    "AMzjAr7b5t8A/wJZk+CSx60coAAAAABJRU5ErkJggolQTkcNChoKAAAADUlIRFIAAAAgAAAAIAgGAAAAc3p69AAACUNJREFUeJzt"
    "V3tUVVUa/+1zz31yz4XLS0IQURRREg0ldCJU1HAyTRkoe9doZqPTGnNqxrLrc1WWr8xZxWSPqdZMl9ISs/FRapqaAiUhyPNmwEXg"
    "PrhPuPeec775A1AkV2u1ptWaP+Zba/+zv73P7/f99nf2/j7gf9jYrw9pNitgMnGsD527yuJXIEPEriDV1alRR2oQcVfcJhNHhYUK"
    "Uy8vmEzgrv+hn2e9kTEGRgTdC6/fIzk6J2Ve7qB0f7dN2dpKXnuLpdXVfvRwe3tH/yYTwK0D5F+GABFHjFHEWyXbRpefXbDl63I2"
    "SaWJ0CrVgi8kwi2LVocUcrskydIeCpzpDAT2Lq0t/y5/SvzEm0cra9a9cykEQIFeQtKAwBh+TJIG+OmKAsa3zPkGu21XZfGbKkPi"
    "yATIIr5wdX5U7nVt6+oJNEWr9dpEFZeiU6ozRZmNa+2x2c6ODBWVVXbmFyzuqtqyBZFeL0QAngFA3AAwBkAJINTnUxmNRt7pdLp6"
    "Vx06ueGpB5aVU1a+JOUVSeezpu/5KdnmR0fk/OWulNBdUwwfAkBqVJQAwAhA26fG4PxgffMqABoAhqjePeAYABg0NE5mNlnBc5ws"
    "cxZ/TykRsQMp+WoCmAngzChUvJ6ZqSSTifvE1nWirsH64Y1jRhTMnhD9Yq3d7kmJjJQA6PuA2ADgfrklAEEAksFg4EVRVAAAJwNA"
    "kAIXeD6SEyURjEHNOB0ANNdvlBkR1hFREZnlpWVl4rRp0zgGwN7h33KhqcNyy03xT+VmRCxvcLrd4cOGiQC0yM1lIOofV44ajAFE"
    "knvDBp8wOy0AADwBUH/f0nosKV6NivMeGI3GGI02hzG2S9l7ZtfYl4BIRFxiBlN01Vv1FRarM1mP7boIxH32ww/rtImJMYrjx5Ve"
    "xmwDkk4TFhZm0Ph83XbGPAACLX0OHgyY7HR8WjZ69OMVigOOmxgZR4Wk3KSVptfsD9w9URUMBcEYgYjAcQqVw25xMnZ/1Z1zNYHf"
    "jfe0JN+oieQDfFLDN8/knv5Kc+JA2Sr9xleyDLNySiVeCXVr+5dx8/LWVPt8fpXp5QnC7fkvyBzxyvr6412LFj4NECkYAOWeQzsK"
    "lq2qpIkzu2l6AW2bfkcZeoI9CqJe8L6hcTprExY/sUjfZnPjWp8U09ZKt61YVJz80vN38H3zhs6u0sLevOCjPjk8v38+rKG+FAA4"
    "rF1LRMRSjh1+tTQvj06yUB1UGizv7Bqe8eyGrwno0fsDFbqeYJk2IFboKmsa3ct+v8kbFyUoRBH65jarztVzBoDYGRcvn1+5bkn0"
    "uaPPSIAfsizJYJ6zSUlKCEI4I4iQZQmyLFFI9F89WLNZAQDhb5esStn8Sq0/NdtKcx6gC+m/adDveufQzMKnhxHACOASDMmTVW3t"
    "IUiSLFRUNc4HIu4D8mdsXmkbfmS/OGzPh97blswnFgiFQEQR31v3EqAggN1Q/O6CfgV0Fy+WDMwtDkeP8iZApfng030L7lvaQBOn"
    "e2jOvbRv6Ohz2P2vI2HNnU3qhuYa43MvvSM0/tDKiEjjcDlu2Lt3f9ayuwLPrcymN5ckyitT4Zi64GYnJ5EMIlJ7fD6dzVmjcbqr"
    "NB2OVk6SpF4CtdcQ6P1TOA65hY/HqfYeObkmd+63NGVuiPKKaNeU/K/RaLEqiEh78IviSPORJxAkaVAO0HBXOxVu/SNNnZdVA6LQ"
    "YD+ICJIkDibAC4IwSgCiMHasHgDGrt44gTt0qvGNSTOOUs58mabeIf0tfeoJrrLuM93mnVvnAS89tvx2ceae1+Qhxw7LYbUNflUg"
    "QCAiXiJKf/IPLoW/RwQRaW1dXUJV/TmhvvmkvtbSwNGPFeAEAVF9t5i6/1nWt9tbUWe59H7q5P00rSBIOfNpm569mTVKd6Lg7efp"
    "nvc20Z0Fk6Rs4OJtwEPD3ivZzssSgUhM+PtuUtvtEojIsP9gzWxgyYOAJm79CwsH5wAPQPZ4YL+aDRyyExK03/p8AW7U8OR795WG"
    "mubNqr5B48k4kWZ42BgM4mhzoN3xrCmKv3c1b/znB0o+Jva3zhszbpIYJ/EAJ1jqyKZQMABymmwbk54X98jWz70fx8ZG6SDL/ZcT"
    "YYAxACwzE0rk5vIAoGnqaDScrpRy/rSU7p4VR1kjcPnWSHy1Islo/Uek0HD/nUVvoLm1liMiri8qRkQjd78mTps9nhR989kHSzyl"
    "BTrX8sKM23HsUo66X4HG+o/6Feg3Ki9HCDiO8UOQzD26kE/srOLI1dXlVmsuWofOCtctnOrZte9jb3ryqFH3d/iHzMmd8/mja1fX"
    "eRfOSzLYurzCoSPfjFj92EKaNC5S0WSVglq9zynqGmwW//EVt3z/frB0Q0lx8naLStMdybV0+PsjBwBWOBZKTbhueoNNnizodIsT"
    "td4kV5C5XUHOr2Jy8JIibXHLc9tS0Vy/9M+l+2m1wzsc0UOEy20tjf/2u3Y83Fi5EwAmj1A9bbEZlDqeGdfMlFLzZkTN3HfKfTah"
    "s31qWmK44pA9cUfxV8GDXQzn2trq7Ffqz7mZUFNI+6o/wGYOiQ33ttl9h+2O0LtDo2Q9I4p5pDq4pwiQhu4ozu4IE9ZP/O58/Msn"
    "zyJHqR4DwaBoCnaXl/kDm3e7DyrnjEZMXiIeShumzQjGGtDsVqD1ciCob3NwlVYN39Ay7v0XY2NXseMHLg98twGAxsQj6qIVXgCB"
    "QReFCitWMOzcGSgDlLfuPfKgaOtcNPf0mfA1313QT+D4VGgFWOQuVNMlqTuswx0Z5TMI+hDTGHjSG5Xc6W8kSVU5gk5Fp1Rsix/6"
    "CCt5vXpwud1bPDCgkKAY25ep1QAr6a/vTCaG9etlEOGWTTtizsQnLtOI3ZPzzlcKyy5cNE739CSqOG0YGFN1ch54+W4EKAA9R4gT"
    "9XJFSHtp3oRxp5L18pIzW7f2XK/ev6LGdXxX15jNHIqKJAYg46+bYirTx89hYk/2iOqajBlt7cpZdodyoi+oVvUEonkG2anSevfp"
    "da7tY0c6xGBgg23HphMwmdh/23AwmIlDEZOA3jdXvXrjBP/ItBQoWRyztg0TZABiSOljCEnx8VUJbc2ftzz7ZCuIGBj7qSB/LhGz"
    "YmBzw/UNxjgQERvQZQEm0y/S1FzfTCYOZrNiAKFeXKJrSP7f+u0/3CS/rgkT3qsAAAAASUVORK5CYIKJUE5HDQoaCgAAAA1JSERS"
    "AAAAMAAAADAIBgAAAFcC+YcAABIsSURBVHic7Vl5lFTVmf/d+1692rqqeqveF6CbxWYRaCCEfUcSFj3YIA5uMJooGknUEWO0aRl1"
    "EgXFMCbouCLG0EIMoIAYBJRV9qXY6X2t7uql9rfcb/7oamiWM5N/xmTO8XfOd+q9++579e33ft8FfsAP+AE3oriYjy3+WgYRv8lT"
    "FqN/ClzPCAMRA2Oi8+Hi4cOt0anzJTdMIvHAKeMXW95QTZzT9jFj5J27dokSgNBB/xBcKwDngBDIHjZhNO78lzHNkUg6RYItpqBW"
    "bZSdl4NVtW1o9NSipuYMgDoAkBiD/vzzfE5JCSsFDAAoKoJUUAAqKYH4/gSgdRLYHKn7u+uebRf0QNLevcdvP3nCNZMQypZlWTPI"
    "oXAlGiW1tUqN1tVpoe8+8zYcKG2sPg8gCgBExEoZ43Nignwf6BCgw20o5/X3Pg5kpE25ffHPPStSc7u7XElZ4ByQFYBxIBpGk6ZC"
    "ZgiGiewBw6AmTa3x6urmvS21pb+tvLwDAKYVptyekhjn/WD75b1ZWbBUV8MA0BlPUVxreRZ7RgB0XI2xrm5JNxkDAMgoKpLAuZH5"
    "8BM/bR/cd8as+fM3vN2973xudXA9EhGyifFz7d7gV762/zrpby5931dTE41GWwbGxWXOdWdn5NrihrsV6+ipSXlv/zgxo/VyU+WK"
    "4+mWlcFW7VsAt+dJuVSNirgYcxYAvhgzogtDnUybYsIIABIABYAKQIuNSwB4cnKyq6mpqQ4Ak7FuHYEx4KczF0b3H7ywVLKO4HHx"
    "XAsGdJNJ4edDLY1zzu+790RLaFtXyY8FAm3HAmc8AL6KDSUuze9/j0k3JnVLtDtPNtf0AZCzu7KiMgkwNXfM0QFYAfhjzAAd7tbp"
    "cp2W6bRI55gSuzeysrJYKBS6kh05ZFkUAzzscuQXXjx/NCcxOZOiUZg44waIb2qqefZES2gbPfSQqRjgBDACWOyaU1GRRMXFnAG+"
    "pRdPrny2vubXdS2tNRML43sPTMXviQqU1AJEnR3ajQAwxyxBMY0zXOs2FBNIj82PdhHQXF1drWiaFrkqABE2A5YwV5V+kMu5rMgg"
    "ATCJN0aC6gZv7dfFAF/61ltGCSAYQAyg2LVgpaUGKykRBLB1RUXSE5NT208fL/c0+IQ6/bbCmQNTPMs9HqjOLIRjDAesVmtiTMs6"
    "APkmrtQVIuZGBgByuVxcURTzVQEMgx0CwmZngq86GkqBgAEwgAGqYOrZSEQpwd+VDqkUpVi+vSF4a4+4F3buuXgy0WlVx4y+9dG+"
    "SSiprkY4KwsqAEs4HI7GrMDR4d/A1UAFrroXuozpAFRZlnXG2JVglgEwBgh3Yyv3ZGWkRg6fabc4HBYYGpySZPmJy6185K1hmwsL"
    "JUyfDng8DAUFNy5cHg8rLS0VAPj8Qf4TL3lNX36+7WDa3FlDMtqbEp7mFwKXT1ZrH6Smgjc0XFGIBYCBoqKu32QoKTFiQhhXrFNU"
    "xFFQYDSvXau62xQ/0AQAxEDEwZjIeKd0bTOnW04vfUHP691viAiHDS6b5N9VXVz89MVjKztTw98BPio/LsmdiDXBgDZVhkZ56VbW"
    "GAAqVftz+6IP/y6jaoWjTQiJaVpSQFUvI7aOdIECwHABTp4A0dKCYMwCN0BGaSkDAOuZs2ukGZM/+JQZe542xFACCJKEUQ7nTzBg"
    "2MY8OSEroKkhIumGfRBjnIShS2pd+bmWSYWBbq2locgZlDllNHiClnB5QPEWpmtDsoKNy8a1lSTt9OPZrOHDqW3/fsOVmppudvdL"
    "l5ikCq5LaiQst5w7expoQcRsdtnCzHA6Hcm2nFsTAIAkzlV/u8lyef/ROiDUYTIilg+Y3V8fvpT70KPbggNGemnCbEHjZovA8Klt"
    "/Ubc9nHChWqylVWTvayG7OW115CtvJbiy+so9YVXpwNALnK7dVv2ypr4rbtqHBcuB5SapoDz9BljwLa/GiOfWEAzR2T9RyFgAxiy"
    "XnljoauynmxlNbqtsp4SDnv8gyYtyABgTSic5AIA99ufPOCoqCP75SrDVllP8bv3R7ISEzOvqpBIAoDsl36/zLrrYPmHSd020ZS7"
    "SB81U6Mpd9GG9N7bsfvgPhMRgciIkd6FVDORnvT6qompg8bMSDlwotFMRKxjficZsV899+hhuv2eCVsOATbH++sfMBMJEKkgEraw"
    "6h1b9GQaACt++UsrAObeuOMRueNdFURkra9v625PSQU6l3fGBIhY668fe92lqglL5s7RfVVVjdxilo2oKm7r0WPMuH99yMO9rRFJ"
    "GADAGSB1IRMDJNOBo72MN5avbB7W3x0VhkGGIVgsGjnAGQlA06SKgYP148+9eduK4ckfJLZXxUNQR/oUxFhERXtTrRmAyfXFF6kA"
    "zFyLMiYIEAIQBBaJXnHjzhWNADA/0Cx9uWNp+wP3TXjVV72FEQEGhNWeqKwSGIkXX9lh5xJ3tgQvxDe1f+Nsbt/j9LbtcbYEv407"
    "V3YIPfOmBUcO6W4IIcAlbpIknui52Bp/+MSXzku1+02MqzCZwGDIZT17C8+gaXe4dmy8T+cMMAwJnAEASxg+PoLs7DiuKA6sXm1A"
    "ZhycdeyWOevImzdFRwEjZ63fckR5/5MjB935u2navaSNnKnR1LtprSNjA9+y60y/M94nbvZ6/Pt/+pNEJKDrKicSiZ9/dSENcQUA"
    "8DjQu+eKFSdsPr8wNbTqclM7TXpnJY28Y2yEEREMXYCI7M3+pocAW9fvpnxU+qCpiwvZKirbO11IvoaDpUsBSdLVX/3bI8kff7R7"
    "1uSRWw8c9bRkZ+Ul6OGQuHvQsGlbFj3y7V9+NDY/44U3F4SbQ2HODA6ng9OhfUH4Wl0QHXs0BjBu8KbhCDSobjzmMWHJnPW/Skm+"
    "+BZOVBk4FbBXZwQvuxoKfuS4JqNx2P62+uOHc/PzyxhI1gymG1pgPABACA5+bZF4oy3WrZMwZ46RtejZRZF75q0aOG/OZ1+k5Uzm"
    "FpuNgbFAJOifVnN50/FNX8wVA/IkPaiB2Uwwb9xa4fpww7tt698q8Ru6YFziJsYQf/J0q+WbXc4sfzkfjBr0VOuQ134Jh05Uh0/6"
    "WPB45kS98rNtaSoJgHHw67TaubrpAEgIAufMVlnlTy0Y0rMs2NhwPfsdwRTLSt3+c82quL3Hax91pW0U42eTPuZ2nSbNJe/gCXV9"
    "Bo76o1LvbeMd2SVqPXTkRA+gZ/Kx8xWx7COYrokumUiAiKRAlIZVnKbHVi6iu3siOGjx/fukLs8hBIEMFUTRK2QYOogIhiGud6FO"
    "3Fi8xwr67h9t+kr5ZPPF120Z62nKXaSNnqnT5HlU0X90dY/Boz+0lNf6FSJyfLPfC7gS+o4fc2/mmvcD5ogmYkwJXE2pojOtmoho"
    "/OP3RfvOHH/CREQQxpWUKxGR3IV45/s3EYABgMvl6qHrejcApw3DMEcikUYAUcgyQdddqccvVTdeOHts7f0LK+eNHH+3HgoassUm"
    "VddXVU2xWv5W9cZysu3aBVfx4xe7pWPhkN7Z2bYR400Hnak4n9iL/K4U+Hv297Lu2Sl+iwymaxCShHTPKST/5pmA5y+f2w0SDIzD"
    "Ggzrji+/ORY1KS2S0xWGIQSTxa1to4d214UQ4JzfzIXsVqs1E4AdQAI69iJAh+DMevjkiXgiYqs+3PqJM+tDmjSXtDGzBE2eR74B"
    "o+oeBmb0MWH1uPG9gk8+M52ee3E+PXTfULq/D8QoJ7RuMkrHJ+DJQfct+Lm1pT3cqWlbYxP1evgRUrpo19warh1gwfOL4zEaHZs9"
    "pK7442P/WxYKhsPhYOf1lXiQZWKGITkOnZJbhSDXonumznMlbKr75WOfLh5QOB3tXmWP0ZBWNzB54xBqRdWomfTeC6+gTVWJuEKZ"
    "770L8zNPebq7fecSIzh92tUtW+rc/xMxMgxwQ+vMJAwAlGgwnvXIubcil+em8L41/vPno6yg4KYbua4CXB/I1xTUggAGYm2Abps/"
    "fcbTdY0HL7y6+ExKimPgbuGDAwJRWUbk7VcD1ooqn/bSytxgZiqrfnCBiJs2I6+1pvKBSEb2bCPd3SckMzBNIzKZKPX8WRZXc5EE"
    "wDr/UgkFrAv6WXIOC7N7lKMBu3ZcIDTU227CJ4CbBe9V5gkAxgJcWMwMXILLG+ZJr70jJnz38TBvTww6KDUa0DT/5WZ+4USNeiTD"
    "Ymu4b3NpU/bcoqf4dyc9NoC3Z7nt3h8VZgSyU/qEZKYD0MlkYjaVWO7LS4hRCEIIMEMQhKBgFJSHRtOM9MDQqkD88OYwaiVDk2EI"
    "gjDQkaWIrhegaykn5QNmtxtxWLjQtAvQ7UfOqrmr3hM9iiZTrzce5GNkDyxMaqloUioropZPf+yN7Hw/8ZbBf3AOyF/We1rhQd02"
    "/+cTJ24Iv/nu2jifX+usyGMNGtl15pKRdleRN/vUPsOUnMiIc5DJxCTOWSQnt746wDe3Xypreiajcen6x2YMr8n+8VkucQYuyeCc"
    "CYtZFkQMuHYhu74jIIjA7hxmn1DWYn8nUfgyUp06VYXMEa+fTqlhtdLIHjg8vOCZJNkU+Pz3z5fYZ/a79aeSxcGha1Bh4JuLp//6"
    "YF6vY7W/fXGCLSM9XSqrbDHVt32W9ZuFFZKv7KUcN3eX543wnlv2VrZhNoUC3BEsbD6XkPXcE/fcxg8NnNtfWXLSH+9fTndu3/jg"
    "kkJ7guYSTJaUysqIdVZR3/pAvffG3ihAy4tg3VsRN+RijTZTYmJ2nww5NS1BtlW3EOp80XBeqtzuC5BW0UQveMb94nDmnRP+UK8L"
    "98RlJfvejIohOTn5vaDpgCKjodVb9+nZM2seba99DUA9A/DRKCS85bWuLms0vjNxy+zmNu5p1fX9JaMxct6kuHubE9KOrF979ujE"
    "XGNBdpzG2pCKrb5uzy3/7PKmLCWS4VW1Uy2I1APQrggwdizkXbugzxtiesBgyrJLXqPB7bL279Urw9TaUEvldZFyCGOHRUbUZpGn"
    "B6PqgSixZbvPaScB8NzX3l4RHNB/nr5x/YXX/rwuOKdbz1E2R7INhgFwwBNsP7M50Lzq6ZZD76Ea4XF58qKdl9L+lJfqHzA1Txsx"
    "7xZ13sDetn7IdlHAbGWffdqIuupAYEo3yRJPqtRqSRJ/9bj/IntR+rJwbKWLB/1d/Z4hlpFmFig9o9z0dCRqFCa6rEYoSs3lde1f"
    "yWbp8zvztdOHz0Ops5ry8hOl1j8filRh7FgZO3caYIwyZ80dx+++/02fAmXQ26sPvXnqUkrfnJwx3GKXQARdN3A2GjhxNhB45cm6"
    "vYFfDcEd3ZLQcItbWZAex5JaFUVIdoWTxERIVojbOKs41MKkZoOd8kXgq8yBmtz/t8sUtgU7N+9CRz/qGsiIFc9uG9K8IeiIlf9d"
    "XazLfUdXARD4+muG8eN1ANa81WsX+vN6PR6ouOib/c47Z5+o9w7ql5bdT7I7GIgATcXRUFtra1xF/Cm1vsIaFwgOzUQfs5XD6ZI4"
    "AwPsZsh2CSKkYtOekLb9tEN/Pn6wtkCRjpYlZL7h3bZmA4qKbizQAbCxgLSrSxegAFD6AkZn+7wY4B6AlV4b9DqKiiRs2GDAMOAC"
    "eiSWfvGzdrtznlp2qXxe6Z/PPVJdV1CQkHKryRVvhyQDYaE3an5+QW3XKkS9KWpp5S5nGJCikBVA4RxOyUTN9Yn6OHmoyVNX8e3k"
    "MRPrb0tKf6T05ce9+B9Km05t4zqN/z1gWLeOY84cAwCS8wcMsj/11KJA9+5D1crqtpFf/e3Sg0eOJA3n8sCM+OQsxDkZJDOgayAj"
    "DJ+qI2joZDANNomxZJMNktmFugvHz44oHHTBSM1Uq1b9+xwQERj7Pz0q4rG2vQEAGZaEbGXF8rsjCe472jmRc88BZdz502WzKuri"
    "BpHI6G1xWKHIaZBlG7jEASIYIhwMReq/jASOPz5unBXZmVls2xdTKndvrY/pnr6Hs65iXkRLWWlMEACs+89+MSnSveCuSGp8XjSk"
    "23kw0Jje4qvPuVxmdbf6FEcoYI2YLaHGhCTDk5Ppau3dz5wYilQFV7y8pKnybB26xOL3eVjXcf4mSwJGR48vHzA75i/J9k8a0yPQ"
    "UDZec7jjtMQEQzPbVGpsSDD7mgxXnOVIWnnD9oPLnyq78p1/4JlcBwPFxbyY6Ib69uqEGzVb3FFg/dOcjnaCAcUcReukIiKpiEgC"
    "kYR1Hb9FRBLWrZNA34er/4Af8P8T/w3aDFjeamX/hQAAAABJRU5ErkJggolQTkcNChoKAAAADUlIRFIAAABAAAAAQAgGAAAAqmlx"
    "3gAAHIhJREFUeJztenl0VFW2/nfOvbfmIZWkkhQJIYQgEJApoIgyKKIo0EwGxAFE7W5pu1UeLdrdahHn7nbGeQSlHYii0g4NKiGK"
    "0jLIDGEKEELmOTXfe85+f1QFgsTh9W+9171+i2+tXXWr7rnn7v2dffYZ9gHO4AzO4AzO4Ay6AgPAUFiojPGXqIVEChjvqgxPCPu/"
    "VvB/F4wDinLa3wQoJWPGqFRYqPz/YHFXNjAQcTAGAL5uk68d7Bx9yTA9GsyVhogKwY8bzTWx1soq4tXVrSJ4rCpWdSw02Gxev72m"
    "JqTfcw9fXFSEIkD+H9vyL+H7BDAoCkEIJE+9em7q5OlFIUKs+buN5e7tW9snSlGSF45olmjIExXQBLM0VYrW6nVN9dHdTfWbAFR0"
    "VMQZg7jnHl5cVMRmxskgAPADHH4/ioqK/iMI6kwAG+P3K6VFRand7nu6yDbx4huOv/LyhilvLf36N66Mkf1SvX0cJqvXYrUwEMNJ"
    "0dEuDBGUes3+SKjmYCBU8lVr/adLaysaAWwHAIUxGPfcw1lRESFBxL8RrLMOJwmIu71Mv/mPb7juuOOaiismv/3owQP5Nw49b6CZ"
    "WwEjDAgBEBPQVAWSoUUPoUEXEZemNQgpXRZVdXkUDWES2Blq15v1yJvLKw+vXV5/vBhAGABG5CVNzstJmrD88yO/TbxZA2AFEABg"
    "R9xbgp0U7Rx5O4IuA6DjZDdTEmWp03PU6ZkfJD1OgN/Pce+90tl/6MTUVX//6MiTT72yfPnS7KtGXDwebQEpQGBgjDMQNM7XNjZX"
    "lLQ1vFvZWvfx39pq63UdjQCiPlXNH+t2J53jyeqVbbVclmV1DrXBklovo0e2t1e/v2DfrgdmXdJrdarDXrB05Y6BQWBnQvlkABEA"
    "qtVqtYXD4YZORpzoPomyHZG5s8EAYCTIVBO/dQAicW0DEAXAMpKS0mtaWo6eQgARMcaYufsbK5e39z1r7MjhA97/4OLCG5WYIQHJ"
    "GRgY5zJMgt99bOeaR8vLrwFQ/0OsdoJ9nrd3Xp7Hefe5dtu5u6sPNR0a6c1RVMP8xsqyRQ2GfKoQUIrjRlkR9xJnQvlAJ6MFTg+q"
    "rJOoCQJMiWuR+C1w0msMABaPx9Ozubl5d0clHABjikI2wIO+/ca3fPbF9hszeg3QVA1EAhwMjEhC4Xxp9cF3Hy0vn6YxXk9+PyeA"
    "USdF/AAngJPfz1XGoDAWfK3+wPY/7f/uhou3ru/7SUvzA5BC7dnNBK9bzps4LC23+KRxHPEuoFutVkeiNSlhhIKTXaHjfdTpfjTx"
    "HQYQShCoJlrenLg2J/5v68wih9/PICUcWX1S4bC41Orqjwu83hTSDQCMSSKCovLj4VDDoiO771YYC/2RJGdFRbIjDHYoUwRIBkhW"
    "VCQNIiaImB/gmwsKQgpjweMpkbLN+44d6JFpUi4p8Aw+dqz+uexst6eT8hxAOBwOhwC4OpHQ0cro9Lurvs06tX6oExky4R3WSCRy"
    "yjMce/YwAIj2zPZGFEJSKHw81ewCIwkWt47AFewPth0OxLDfkJIV/bxIfoKUYVu2GHcR8ZtGestlJNLwzopdxvBR58iB+ZmXpIvA"
    "IytWFHKKt2LAAbgTrWRYrVZvggQ9QY6WqPunhtAO/UTiWgVgeDwepmmapRNZ4MjPJwAwJ7kaFCJEoxGrlIlAS/FZERhDwKBGnHTD"
    "/+lQRnsKwX5bXB8YmK08fawhsnVdyY7G8ePPp6w023VFNxf/tZvPZ83PBwU6xYFwOCwRd38GIIZ4y3ZGx4jQERy70qsjGBqcc6lp"
    "2inTW47Fi+MP7aqsNSumaMBp7lUfbtXBTABAiT4OxpgDgF3jvHPk/dkoLobw+8FfLA1/kJth27B9b3VN5b5d7OKpk5GTYVvQw9x0"
    "w549iI0ZgyiAqN1utyM+HJoShHx/DkFdSFfgiHuXrqqqlFKGTr3JGMA56g5/K4yqGjMNGp5d1dZQQQoHxYc/gCRyrRYrgPD/yyxm"
    "TzFUAEp3j7FVapb1a77cHUTDHjb6nO7CaRb+kWdZZpWWwhgzBkYwGAwnjIokjDB3UWWHOjIhWhdlOoZRWVtbG21ubm7s/GzcpYVg"
    "AGK8qmGHpWfeyLU11dWM6fEBlzEGKShZs/bp7XCMEESs4IUXVBApP1v81Hkyo9S0kttjlZdLZrKs+mwn1dbUKb2z7Ek2i+nNMUO9"
    "vy8tBU9Ph3C5oDkcDpfbbE5KdZqykZ9vOqXekpK4HgUFGuKeYiA+kqgAVIwZ06EnT3wTiKKJdQ46CCAUgwNoj+3c9mFSj/S8d522"
    "o83BNh1c4QxgEFJmWC2OGd6s8QBoy69/rYMx8bOliEkAyPdCAk6noZnddoeaPrCbUKrqReyL0ub9LVWtckBSkNn04J+H9kt9tDbS"
    "Q7MrFofZHIjEOI+2x5jEnj2xU+q98EIDjAls2SITRltcZrPPrml93WZzNkpLbV3qQyf9OEGFn4PdKzPSe+Vbv1q34/CSx9/9x4ef"
    "9L+0z5ABIhyUAEEx2/i3Dcc3XFBbu8g3ZcZvQg5nnUKS/1g4ZiDJVZOJyg9tqyt+8cW8CRPMB9esid7cXY7dVI2rRHbqeSFfTkZd"
    "1pB1zkDNBXmoSUupO8JCjfUyqihPrRk4/XZs3KiNyckxSktLecbYyybTkBETDK4GGEhhjAjhWDLtLnu5YV3xNzZbamoo1BBxOBxq"
    "IBAIpI6bOo4NPf9CiIhKjBhjJgORiFtsWPNO05Zv1sDv7+SZRAyAmv7W518lrfu29VooS4zx00mMnizF6GlEY6fKwNjpseFWz7K0"
    "DbvCdiKy/gxxEJH348/WAgBUBQDSc3672N9t5epqZ1VLu1VQzEJEJiKyRAVlV1XLgSvfliOvnaLPHO56YmQKnBi/0M4A+F5+s8id"
    "KGsjIgsRuYmoz4rPrwOAlJEjnQDs7gsu8ABAWvHqh+yJclYiMhNREhF5//CnmwEAJSXqSQYWgwEwxBMPv57U/2zXG1Nnys2Vlfu5"
    "2cKIJEkhyW7StId92T3qnn52qUWCwkAsDIhwfKnUlUTDgEEOWwuIWLLFO737mx+va33Sv7h22iUZAZ/bEebQIoDUiRAxcVT4MtiO"
    "abPY5tc/4Lv+8NqtOeectWpI+dM+AiD1KI8BRgyIhgAjEq9fcKczBIAZwaACINZ6yy3BeLThLBovFwkDRhSIRgADVjXYOQbEUcQk"
    "iFjDt5+/aZR8sT/lzkUzH9q75dOYYFAYIzDOEYnJ83vmjZn2t2eD+tqNuzXABCkZiFRIyU4TIRiTkoEz6WIs1/zSyy83zr68bzOH"
    "IQyDSBIgBEFKIsYMCCGZlGBCICYF3zttur71jhfHDh+Ss/wvY5ARVmxhHu/rSkeg44Ai9ZgKQJHRqAJAs91zTwoAppCh8o6ASKQC"
    "UBmgQp6Mgqdu8s0s5uAs2P7Ag4+68vpmrLrhNs+XB3Z+A5uVQwopQczMTHTfsPOvaL/++rXJ1U3gnBNjDArnymmiKCaVcwWRCHPM"
    "nX9z6MqJnhCgMyIVqsrAGXFFYRbOFTOgaorCiXOQooBxBdB1rWzMGPFtwVXnbjyCpal6Q5YAgPhM7fuQIhzW7JrWU4SkBfFJ7E/O"
    "V9RTfhXPlCDirYy9Zln2t2sy7rt7+g2vPPnIdzk98lNUp1tKAzIapf7J2T2eOlLec8EDf/3U8/RDl0UCkfak2ubSqFnTmTz5UgKE"
    "KRJ1ieIPKXLN7MtDAEFIBQoHALIALGlbWQDHakoJsUaekp7fVjBgUEiDBqL4QG3ovG7aVdL92L0F2LvdF4/fpxrGFbMAIBVdd3HO"
    "w3aXKVQHgIi6Iuqn4OdQOGxwD+mx62DE/tYHm38P00t06RyiUTMMMXoq0ZhpIjiuUJ8KPOb4tHR7ZkAc/rE3JQFj3HsP6SAiCCGZ"
    "YUiVSKa//WF1milpSke5XYBj0L33f2qJj9eGSkQqEXmJ6NoZI43es6cGTEQEYVBiTDcsRNT38y1Xgohj7twkvPCClvLnPztBxHwf"
    "rnnMFC+nQ0oCkWElIu/ixfMAACUlqnq6ukUSBvEQY9sCv//DY773V/zhkStmbh+7ecOGif2Gn0ftQSk5MRuY+tK5E2acddXMlTb/"
    "41emAHn1wOHvVcYB6Eq3Pu4ojzc7A0CKIs2Awj9Z/151rOVDmM2Ye3nmlbdWBn+XUfxQ737GIWriLn6sIWaEzM6W5HCz0xcsNyel"
    "dLd3vKBjKcgA0IaNbnZxgQTQgmXL0ATo7I47QM8tM/3UzLULAgAwRiBCmLGnLM++Mjz7qSXXFZ6Vs2JDdUX+oNRMt4hESMQilOp0"
    "Zb/TPffKS2676rXsRQ+9njRkGGO6CIJDhSRA1UitrlT0Rb/9pzmmt4SIkiUASMkjnMF+0zUzckzGxr4lz/feW1o+P9UK66QhsGVV"
    "LodhteHgwVZlUyV0i8d2uOJYKJdlE2OJ6W7CMC4AtE275M60KfuvJkWRjAhSVUkISZJhQKKc8kPLl64JAAhsMQ+pSo2+8MYFGXm5"
    "610ffT5p3tjhr68dPXFOkslkF7oEohEx3peT8X44OGJa2bZjGfffObP2e7NxZ30zaOF1f3Y2tA8NMjY2IiWgKIoA0HTewAx9yMPL"
    "tu6eC63ymG6NVmhr6yrQrbUSfY0qDEypYrq5wndQ9SZV1lQ2H21VDA3I1Ds1VQxAdf/cHAA5P9LQP2vxdnohfzweeDzZE3MP1AQd"
    "73+xdibwemj8FURjpgoxegqJUVMNuvQqWpbiK8bkOU+nNrZJEMUQiRog0h1lBw2rah2We+3tN6VFBYFIKoZOjCRxISSIREKos3hq"
    "6mnqti/owUdm09X9QDNHmI72vmvR52YiAolTywshIITRhcgTZSR1GQN+iIgOAVasUADAM2rSjWfVBUi588H1f1Rtb8rx1xKNniLE"
    "qClEo6YadMnV9LAnYyVmXfeOtzVCIJIgitn3HjDSs8+6CEBaxl9feiK5NaifMFgKgq4Ti0YJkYjk0ahkhk4gccI4t0Fy+pP30NQU"
    "HOp/98ItXRJAQkAYAiQMEOkn5GcQcCJ42+32dJy6vRzvPjNnCpSUqM1fffRyy62LHspeeMvIB+fN50s2f74cdifnDEICHJGQWDT8"
    "ommP/ONTo/6XN7/lawgwE6BpdpcSbNU9AwakJJ/9zC8DvcYNbB787t+QHY7CxDiYqoKZTFDMZgaTiZGiSiZBjAhcCLQqkq29pQgN"
    "/Qb4WsurVQYA8tRh0AzOrVzhVnDFCqgdYuKcnZ7cOxUnXIAxeb7NZotIKXdJKa2MMRGNRo8C0HHhhQJErI4xv3tW4RWZT/1l1q1V"
    "Vc8kfff10jmDzruOh4JCQio8EpILzxl7lVKy+sMFV897MO2aWRz7DtqcltaztHD7PN1mm3hpH83I+u5D1vzPpdhkJKEypRe1JaXJ"
    "tpQsI9h/SK2W7ctu8jggCSBFATcMtKoMgSuusTrWrutd16FuvIXIDDDve6s3h3buq2Veb6OqmaLSpEnWHtB4VuqljdMuyRRSEhhj"
    "XfXyEwQEKPy1DeCRCNoBqHA6FUSjHYs9gqYCRIb8qKS13sIp85Xnb547b/5ztO3rZXMHXjCXh4NSkGRKNCpuG3TBlNwdm5remfPu"
    "wjIb5guPcn2uRUkbfX4OKZ7uavnejRD1x+Bpk2iuhx5qQV04gtdHpKOldfBUlD3z9K/aenXLkzK+YU9gaOx5NqzmzWZ2opfG9eIA"
    "0z8rLR722kPaZAWv/S6MKgApABrTl7z4LAPmg3ORmAr/MAEIoiV0ci8daG8/vTRjxD75khMRq053Gb6lz/163oLFD+lrVjx/45BR"
    "NylGFNDB0Vwr3V5lXo0neZwtGnB6cvOSjr32EXtBUWS0tgYRq40pEUL6r2fH9Pbd0XaXWjI6n9cjGlNXr/7gkaztv54S7JWZJ0me"
    "2JKLKAw2VeOntCFJLhmHDDaOas1QUg9OO68Jm5KXpzRsH9W478gqVvyxON2IU9F5Atext37C3C6fIAliDFI3WEOai/ueuu9Pv5w0"
    "w75oa+nyiNCDMlyFN8MHWVGwykixRbsX9FQ9tubjRtUzbxqVadn80OBzcLzPAFkx6GxULHlLq790zjFP934soGVlbr7kgS2ZS17/"
    "rO3i0efrAIFz3vFOe00tTHogoRR1NAh0As51tF2oQO3eeKxxwgRXLBZpDbSAMQ3stE3U0/BD84BOb+n6DgMxXRhUlWJHxqNPXPtm"
    "zZGP9u9cfTzF7sqrYAFYrYIzCVZey9AeiWndn72roWnj6nrnn5f0axo2iIWlEPXDz1as7y3Lb69vyd8vWbtqN/0+6rAi2tEALL4f"
    "aWMastauQhtFSZ7SMATJGA3RWm2DL+3R8kKtuemi3KN5pZtS97vRmAnNHPspAv7HiwUOimdDNA12prLsL7Yx94L5dHa4bBKl85z2"
    "pHZy2yQPRIhvrhQ79zXq2xqjbFNyhqNy4K6vqkPTL/+N8+P133m4okiAQoYh271JiKa7nW0OK0UBwYjAJIgbhuSqhozP1sH92YeQ"
    "TjfrYgeKHWvSWYFyJO2i7uZR645hdLhxX5Xd6WylcEz716bCiYo7XRPAUAgoq5hVmkNA6ldbuGvNKohPluOclAY2cEiuLNvBTOU1"
    "evBYlfG1yYa2oe5kX28d3bNJTRtueCw+nxcRBZWXTxr1YM2i+6f5bpp7dUPPLKYDQhiCxWcfDMS5AINi5ipLWr1e+m6brbtdUjGI"
    "ERdSiy9sGAAJxgi1cO9To7G+vH5zw9isEbN63P/wlhfuunNjls0UhRAExghSElSVICR1Tqt0JuD7KWaTF1BjgOZ0gVX2vr69eMuL"
    "+lnvv2VYV7xCcv1HbV7UuRVO0mFz8YP7j/N/7o980yAd7pTzhqcarcc39d1Ytuu/hlyw2GN1AlANaJoKkzbn0/MnTX/1uUefuv/v"
    "K29Le2zJr8SEkfmtqnIiQWgGYD5SE7W/9U656aE7RVJ3o5fTCbNZ4yCFAwpn8bw5hwZg5/BZz6xZ+d7QZlVNuU7Z+ovKsLLKev2M"
    "SU802aotisJ0QAXnDIAqFQ6DcaUrAjoCIAOA/HzIPXsQBRBubYPwO1507Bvpuuno2lfTSI9QTjq3mFVT9GCtCKzcGDwSierbkh0m"
    "1ZOeMu5434k+0/QJQ57Y9fUbR3/327/cMeL8+f2TPE4KhSHCYdHTZHLcd974P15cV/Hl7Zed//iOhYv7eGdNv8JwONqw/0ired/B"
    "9dobq98etOu9zJoe6nOSm6xNQaNSb2gNOL/+rq+uKWEV4E3M2p4lWz1XNr13/fVf4qKPZrP3HIhRcs036RO07M+3rFm++SuPvdyV"
    "SV6CKsC4okXDNrW2IZ4cWbfupxcJL93gSi7ZI8cdqNEnhwL66BS3au2fpXkdNpUdrtPRHjJgSKrLzzSpuytikZBUX/3nofBLaXPn"
    "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"
)


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

    if "--extract-icon" in sys.argv:                    # برای بیلد: ESH_Translator.ico را از داخل سورس کنار فایل می‌سازد
        _dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ESH_Translator.ico")
        with open(_dst, "wb") as _f:
            _f.write(app_ico_bytes())
        print("icon written:", _dst)
        sys.exit(0)
    set_app_user_model_id()
    if not is_admin() and "--noelev" not in sys.argv:
        if relaunch_as_admin():
            _hard_exit(0)
    if "--restarted" in sys.argv:                       # منتظر بسته‌شدن نمونه‌ی قبلی می‌مانیم
        for _ in range(50):
            try:
                k_ = ctypes.windll.kernel32
                k_.CreateMutexW.restype = ctypes.c_void_p
                h_ = k_.CreateMutexW(None, False, "Local\\42OCR_SnipTranslate")
                busy_ = k_.GetLastError() == 183
                k_.CloseHandle(ctypes.c_void_p(h_))
            except Exception:
                break
            if not busy_:
                break
            time.sleep(0.15)
    if not single_instance():
        _msg("برنامه از قبل در حال اجراست (آیکون کنار ساعت ویندوز).")
        _hard_exit(0)
    if safe_mode_begin():
        _msg("حالت امن: برنامه دو بار پشت‌سرهم ناگهانی بسته شد؛ تنظیمات به پیش‌فرض برگشت.\n"
             "نسخه‌ی قبلی تنظیمات در config.json.crash (پوشه‌ی eshOcr در AppData) مانده است.")
    app = wx.App(False)
    try:
        app.SetAssertMode(wx.APP_ASSERT_SUPPRESS)       # پنجره‌ی assert کتابخانه‌ی wx دیگر به کاربر نشان داده نمی‌شود
    except Exception:
        try:
            wx.DisableAsserts()
        except Exception:
            pass
    app._snip_app = SnipApp(background="--bg" in sys.argv)
    app.MainLoop()
    _hard_exit(0)