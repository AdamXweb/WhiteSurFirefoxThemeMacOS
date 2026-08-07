#!/usr/bin/env python3
"""Shared machinery for the fxcss toolkit.

Drives Firefox over Marionette, its built-in automation protocol. Marionette is
plain TCP with length-prefixed JSON, so nothing outside the Python standard
library is needed -- no Selenium, no geckodriver, and therefore no
driver-to-browser version matching to keep working.

Two things here are worth knowing before changing anything:

* Screenshots are taken in Marionette's *chrome* context, which captures the
  browser window's own document. An ordinary WebDriver screenshot only captures
  page content, so toolbars and tabs would never appear.
* Native popup widgets (context menus, the app menu) are separate OS-level
  windows and are absent from those screenshots. See README.md.
"""

import base64
import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path

MARIONETTE_DEFAULT_PORT = 2828
WINDOW_WIDTH = 1280
# Tall enough for the chrome, a strip of page content, and the find bar docked
# at the bottom -- without a screenful of empty page padding in every capture.
WINDOW_HEIGHT = 480


class MarionetteError(RuntimeError):
    pass


def free_port():
    """Pick an unused port for this session's Marionette listener.

    Firefox's default is a fixed 2828. If a previous run leaked a browser (a
    hard kill skips cleanup), a new session would silently attach to that stale
    browser instead of its own -- which looks like the theme mysteriously not
    applying. A per-session port makes that impossible and lets several
    sessions run at once.
    """
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Marionette:
    """Minimal Marionette client. Wire framing is '<byte-length>:<json>'."""

    def __init__(self, host="127.0.0.1", port=MARIONETTE_DEFAULT_PORT):
        self.host, self.port = host, port
        self.sock = None
        self._msgid = 0
        self._buf = b""

    def connect(self, timeout=120):
        deadline = time.time() + timeout
        last = None
        while time.time() < deadline:
            try:
                self.sock = socket.create_connection((self.host, self.port), timeout=30)
                self.sock.settimeout(180)
                break
            except OSError as exc:
                last = exc
                time.sleep(0.5)
        else:
            raise MarionetteError(f"could not connect to Marionette in {timeout}s: {last}")

        handshake = self._recv()
        if "marionetteProtocol" not in handshake:
            raise MarionetteError(f"unexpected Marionette handshake: {handshake}")
        self.command("WebDriver:NewSession", {"capabilities": {}})

    def _read_more(self):
        chunk = self.sock.recv(1 << 16)
        if not chunk:
            raise MarionetteError("Marionette connection closed unexpectedly")
        self._buf += chunk

    def _recv(self):
        while b":" not in self._buf:
            self._read_more()
        length, _, rest = self._buf.partition(b":")
        need = int(length)
        self._buf = rest
        while len(self._buf) < need:
            self._read_more()
        payload, self._buf = self._buf[:need], self._buf[need:]
        return json.loads(payload.decode("utf-8"))

    def command(self, name, params=None):
        self._msgid += 1
        msg = json.dumps([0, self._msgid, name, params or {}]).encode("utf-8")
        self.sock.sendall(str(len(msg)).encode("ascii") + b":" + msg)
        while True:
            resp = self._recv()
            if isinstance(resp, list) and len(resp) == 4 and resp[0] == 1:
                _, msgid, error, result = resp
                if msgid != self._msgid:
                    continue
                if error:
                    raise MarionetteError(f"{name} failed: {error}")
                return result

    def set_context(self, value):
        # Context switching is a Marionette extension rather than a WebDriver
        # spec command, and its namespace has moved between Firefox versions.
        tried = []
        for name in ("Marionette:SetContext", "WebDriver:SetContext", "setContext"):
            try:
                return self.command(name, {"value": value})
            except MarionetteError as exc:
                if "unknown command" not in str(exc):
                    raise
                tried.append(name)
        raise MarionetteError(f"no usable SetContext command (tried {tried})")

    @staticmethod
    def _unwrap(result):
        if isinstance(result, dict) and set(result) == {"value"}:
            return result["value"]
        return result

    def script(self, source, args=None):
        return self._unwrap(self.command("WebDriver:ExecuteScript", {
            "script": source, "args": args or [],
            "sandbox": "system", "newSandbox": False,
        }))

    def async_script(self, source, args=None, timeout=30000):
        return self._unwrap(self.command("WebDriver:ExecuteAsyncScript", {
            "script": source, "args": args or [],
            "sandbox": "system", "newSandbox": False, "scriptTimeout": timeout,
        }))

    def screenshot(self):
        return base64.b64decode(self.command(
            "WebDriver:TakeScreenshot", {"full": True, "hash": False})["value"])

    def quit(self):
        try:
            self.command("Marionette:Quit", {"flags": ["eForceQuit"]})
        except Exception:
            pass
        finally:
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass


# --- profile ---------------------------------------------------------------

EXTRA_PREFS = """
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);
user_pref("browser.tabs.inTitlebar", 1);
user_pref("browser.tabs.drawInTitlebar", true);
user_pref("browser.uidensity", 0);
user_pref("marionette.port", %(port)d);

// Skip everything that would otherwise cover the window on first launch.
user_pref("browser.startup.page", 0);
user_pref("browser.startup.homepage", "about:blank");
user_pref("browser.startup.firstrunSkipsHomepage", true);
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.newtabpage.enabled", false);
user_pref("browser.messaging-system.whatsNewPanel.enabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);
user_pref("app.update.auto", false);
user_pref("app.update.enabled", false);
user_pref("extensions.update.enabled", false);

// Promos and rollout-gated features add toolbar items that come and go with
// Mozilla's campaigns. Left enabled they can differ between two runs and show
// up as diffs that have nothing to do with the change under test.
user_pref("browser.vpn_promo.enabled", false);
user_pref("browser.promo.focus.enabled", false);
user_pref("browser.contentblocking.report.hide_vpn_banner", true);
user_pref("browser.ipProtection.enabled", false);
user_pref("browser.urlbar.quicksuggest.enabled", false);
user_pref("browser.urlbar.suggest.quicksuggest.sponsored", false);
user_pref("extensions.pocket.enabled", false);
user_pref("app.normandy.enabled", false);
user_pref("app.shield.optoutstudies.enabled", false);
user_pref("messaging-system.rsexperimentloader.enabled", false);
user_pref("browser.discovery.enabled", false);

// Determinism.
user_pref("toolkit.cosmeticAnimations.enabled", false);
user_pref("ui.prefersReducedMotion", 1);
user_pref("browser.search.region", "US");
user_pref("signon.rememberSignons", false);
user_pref("browser.toolbars.bookmarks.visibility", "always");
user_pref("browser.bookmarks.restore_default_bookmarks", false);
user_pref("browser.places.importBookmarksHTML", false);
"""

# Hides artifacts of the automation harness itself -- never theme rules -- so
# what you see is what a real user would see.
CI_ONLY_CSS = """/* Injected by tools/fxcss -- harness only.
 * Firefox marks automated sessions with a robot icon in the address bar. */
#remote-control-box, #remote-control-icon { display: none !important; }

/* Rollout-gated Mozilla feature button: present or absent depending on a
 * remote config rather than on this repo. */
#ipprotection-button { display: none !important; }
"""

XULSTORE = {
    "chrome://browser/content/browser.xhtml": {
        "main-window": {
            "screenX": "0", "screenY": "0",
            "width": str(WINDOW_WIDTH), "height": str(WINDOW_HEIGHT),
            "sizemode": "normal",
        }
    }
}

SAMPLE_PAGES = {
    "start.html": ("WhiteSur", "<h1>WhiteSur Firefox Theme</h1><p>Preview page.</p>"),
    "docs.html": ("Documentation", "<h1>Documentation</h1><p>Second tab.</p>"),
    "issues.html": ("Issue tracker", "<h1>Issues</h1><p>Third tab.</p>"),
}


def build_pages(dest: Path):
    """Local pages so a capture never depends on the network."""
    dest.mkdir(parents=True, exist_ok=True)
    urls = {}
    for name, (title, body) in SAMPLE_PAGES.items():
        path = dest / name
        path.write_text(
            "<!doctype html><meta charset=utf-8>"
            f"<title>{title}</title>"
            "<link rel=icon href=\"data:image/svg+xml,"
            "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E"
            "%3Ccircle cx='8' cy='8' r='7' fill='%23315bef'/%3E%3C/svg%3E\">"
            "<body style=\"background:#fff;color:#222;padding:36px;"
            "font:16px -apple-system,'Segoe UI',sans-serif\">" + body,
            encoding="utf-8")
        urls[name] = path.resolve().as_uri()
    return urls


def build_profile(repo: Path, profile: Path, dark=False, native_menus=None,
                  empty_user_chrome=False, port=MARIONETTE_DEFAULT_PORT):
    """Install the theme into a fresh profile the way install.sh does.

    empty_user_chrome leaves userChrome.css blank so the caller owns the
    stylesheet entirely -- used by watch mode, where replacing one sheet gives
    exact fidelity even when a rule is deleted.
    """
    profile.mkdir(parents=True, exist_ok=True)
    shutil.copytree(repo / "chrome", profile / "chrome", dirs_exist_ok=True)

    # userChrome.css @imports customChrome.css, which the repo does not ship.
    (profile / "chrome" / "customChrome.css").write_text(CI_ONLY_CSS, encoding="utf-8")
    if empty_user_chrome:
        (profile / "chrome" / "userChrome.css").write_text(
            '@import "customChrome.css";\n', encoding="utf-8")

    prefs = ""
    repo_userjs = repo / "configuration" / "user.js"
    if repo_userjs.exists():
        prefs += repo_userjs.read_text(encoding="utf-8") + "\n"
    prefs += EXTRA_PREFS % {"port": port}
    # The theme's dark rules sit behind @media (prefers-color-scheme: dark),
    # so this pref is what switches between the two.
    prefs += 'user_pref("ui.systemUsesDarkTheme", %d);\n' % (1 if dark else 0)
    if native_menus is not None:
        # On macOS Firefox uses native context menus by default, and CSS cannot
        # style them at all. Turning this off makes them XUL menus, which the
        # theme does style.
        val = "true" if native_menus else "false"
        for p in ("widget.macos.native-context-menus", "widget.gtk.native-context-menus"):
            prefs += f'user_pref("{p}", {val});\n'
    (profile / "user.js").write_text(prefs, encoding="utf-8")
    (profile / "xulstore.json").write_text(json.dumps(XULSTORE), encoding="utf-8")


# --- session ---------------------------------------------------------------

LAUNCH_FLAGS = [
    "--marionette",
    # Firefox 137+ requires this opt-in before Marionette will hand out the
    # chrome context that makes browser-UI screenshots possible.
    "-remote-allow-system-access",
    "--no-remote",
]


class Session:
    """A running Firefox with a themed profile and a Marionette connection."""

    def __init__(self, repo: Path, firefox: str, dark=False, native_menus=None,
                 empty_user_chrome=False, keep_profile=False):
        self.repo, self.firefox = Path(repo), firefox
        self.workdir = Path(tempfile.mkdtemp(prefix="fxcss-"))
        self.profile = self.workdir / "profile"
        self.keep_profile = keep_profile
        self.urls = build_pages(self.workdir / "pages")
        self.port = free_port()
        build_profile(self.repo, self.profile, dark=dark, native_menus=native_menus,
                      empty_user_chrome=empty_user_chrome, port=self.port)
        self.proc = None
        self.m = None
        self._generation = 0

    def __enter__(self):
        env = dict(os.environ)
        env["MOZ_DISABLE_AUTO_SAFE_MODE"] = "1"
        env["MOZ_CRASHREPORTER_DISABLE"] = "1"
        # Chrome UI does not paint in headless mode.
        env.pop("MOZ_HEADLESS", None)
        cmd = [self.firefox, "--profile", str(self.profile), *LAUNCH_FLAGS,
               "--new-window", "about:blank"]
        self.proc = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        self.m = Marionette(port=self.port)
        self.m.connect()
        self.m.set_context("chrome")
        self.m.script(RESIZE, [WINDOW_WIDTH, WINDOW_HEIGHT])
        return self

    def __exit__(self, *exc):
        if self.m:
            self.m.quit()
        if self.proc:
            try:
                self.proc.wait(timeout=45)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        if not self.keep_profile:
            shutil.rmtree(self.workdir, ignore_errors=True)

    def info(self):
        return self.m.script(BROWSER_INFO)

    def setup_window(self, pinned=True):
        result = self.m.async_script(SEED_BOOKMARKS)
        if result is not True:
            print(f"  note: bookmark seeding returned {result!r}", flush=True)
        self.m.script(SETUP_TABS, [[self.urls["start.html"], self.urls["docs.html"],
                                    self.urls["issues.html"]], pinned])
        time.sleep(3.0)

    def apply_css(self, css_text):
        """Load a small ad-hoc rule set as a user sheet (for experiments)."""
        return self.m.script(SWAP_SHEET, [css_text])

    def reload_theme(self):
        """Re-read chrome/ from the repo and swap it into the running browser.

        Each reload copies the tree to a fresh numbered directory and loads
        userChrome.css from there by file URI. The new path gives every file --
        the entry sheet and each @import beneath it -- a URI Firefox has not
        seen, which is what actually defeats the style-sheet cache.

        Copying rather than concatenating matters: @namespace is scoped to the
        stylesheet that declares it, so inlining imports into one sheet would
        let one file's namespace leak across all the others and silently change
        which elements match.
        """
        self._generation += 1
        dest = self.profile / "chrome" / f"live-{self._generation}"
        shutil.copytree(self.repo / "chrome", dest, dirs_exist_ok=True)
        # Keep the CI-only overrides that customChrome.css normally supplies.
        (dest / "customChrome.css").write_text(CI_ONLY_CSS, encoding="utf-8")

        uri = (dest / "userChrome.css").resolve().as_uri()
        self.m.script(SWAP_FILE_SHEET, [uri])

        previous = self.profile / "chrome" / f"live-{self._generation - 1}"
        if previous.exists():
            shutil.rmtree(previous, ignore_errors=True)
        return uri

    def set_dark(self, dark):
        self.m.script(SET_DARK, [1 if dark else 0])


# --- chrome-context scripts ------------------------------------------------

RESIZE = """
const win = Services.wm.getMostRecentWindow("navigator:browser");
win.moveTo(0, 0);
win.resizeTo(arguments[0], arguments[1]);
return [win.outerWidth, win.outerHeight];
"""

SEED_BOOKMARKS = """
const done = arguments[arguments.length - 1];
(async () => {
  try {
    const {PlacesUtils} = ChromeUtils.importESModule(
      "resource://gre/modules/PlacesUtils.sys.mjs");
    for (const [title, url] of [["GitHub", "https://github.com/"],
                                ["Mozilla", "https://www.mozilla.org/"],
                                ["WhiteSur", "https://github.com/AdamXweb/WhiteSurFirefoxThemeMacOS"]]) {
      await PlacesUtils.bookmarks.insert({
        parentGuid: PlacesUtils.bookmarks.toolbarGuid,
        type: PlacesUtils.bookmarks.TYPE_BOOKMARK, title, url});
    }
    done(true);
  } catch (e) { done("error: " + e); }
})();
"""

SETUP_TABS = """
const [urls, pinned] = arguments;
const sp = Services.scriptSecurityManager.getSystemPrincipal();
const win = Services.wm.getMostRecentWindow("navigator:browser");
const gb = win.gBrowser;
while (gb.tabs.length > 1) { gb.removeTab(gb.tabs[gb.tabs.length - 1]); }
gb.selectedBrowser.loadURI(Services.io.newURI(urls[0]), {triggeringPrincipal: sp});
for (let i = 1; i < urls.length; i++) { gb.addTab(urls[i], {triggeringPrincipal: sp}); }
if (pinned) { gb.pinTab(gb.tabs[0]); }
gb.selectedTab = gb.tabs[1];
return gb.tabs.length;
"""

SWAP_SHEET = """
const win = Services.wm.getMostRecentWindow("navigator:browser");
const u = win.windowUtils;
const uri = "data:text/css;charset=utf-8," + encodeURIComponent(arguments[0]);
if (win._fxcssSheet) {
  try { u.removeSheetUsingURIString(win._fxcssSheet, u.USER_SHEET); } catch (e) {}
}
u.loadSheetUsingURIString(uri, u.USER_SHEET);
win._fxcssSheet = uri;
return uri.length;
"""

SWAP_FILE_SHEET = """
const win = Services.wm.getMostRecentWindow("navigator:browser");
const u = win.windowUtils;
const uri = arguments[0];
if (win._fxcssSheet) {
  try { u.removeSheetUsingURIString(win._fxcssSheet, u.USER_SHEET); } catch (e) {}
}
u.loadSheetUsingURIString(uri, u.USER_SHEET);
win._fxcssSheet = uri;
return uri;
"""

SET_DARK = """
Services.prefs.setIntPref("ui.systemUsesDarkTheme", arguments[0]);
return Services.prefs.getIntPref("ui.systemUsesDarkTheme");
"""

FOCUS_URLBAR = """
const win = Services.wm.getMostRecentWindow("navigator:browser");
win.gURLBar.focus();
win.gURLBar.value = arguments[0];
win.gURLBar.setPageProxyState("invalid");
win.gURLBar.selectionStart = win.gURLBar.selectionEnd = arguments[0].length;
return win.gURLBar.value;
"""

BLUR_URLBAR = """
const win = Services.wm.getMostRecentWindow("navigator:browser");
if (win.gURLBar.view.isOpen) { win.gURLBar.view.close(); }
win.gURLBar.value = "";
win.gURLBar.blur();
win.gBrowser.selectedBrowser.focus();
return true;
"""

OPEN_FINDBAR = """
const win = Services.wm.getMostRecentWindow("navigator:browser");
win.document.getElementById("cmd_find").doCommand();
return true;
"""

FILL_FINDBAR = """
const win = Services.wm.getMostRecentWindow("navigator:browser");
const bar = win.gFindBar || win.gBrowser.getFindBar();
if (bar && bar._findField) { bar._findField.value = arguments[0]; }
return !!bar;
"""

CLOSE_FINDBAR = """
const win = Services.wm.getMostRecentWindow("navigator:browser");
if (win.gFindBar) { win.gFindBar.close(); }
return true;
"""

BROWSER_INFO = """
const win = Services.wm.getMostRecentWindow("navigator:browser");
const pref = (n) => { try { return Services.prefs.getBoolPref(n); } catch (e) { return null; } };
return {
  version: Services.appinfo.version,
  buildID: Services.appinfo.appBuildID,
  os: Services.appinfo.OS,
  dpr: win.devicePixelRatio,
  outer: [win.outerWidth, win.outerHeight],
  legacyStylesheets: pref("toolkit.legacyUserProfileCustomizations.stylesheets"),
  nativeContextMenus: {
    macos: pref("widget.macos.native-context-menus"),
    gtk: pref("widget.gtk.native-context-menus"),
    windows: pref("widget.windows.native-context-menus"),
  },
};
"""


# --- views -----------------------------------------------------------------

def capture_views(session: Session, outdir: Path, modes=("light", "dark")):
    """Capture the standard set of views. Returns the browser info dict."""
    outdir.mkdir(parents=True, exist_ok=True)
    session.setup_window()
    info = session.info()
    print(f"  firefox {info['version']} ({info['os']}), dpr={info['dpr']}, "
          f"window={info['outer']}, legacyStylesheets={info['legacyStylesheets']}",
          flush=True)
    if not info["legacyStylesheets"]:
        raise RuntimeError(
            "toolkit.legacyUserProfileCustomizations.stylesheets is false; "
            "userChrome.css would not be applied and this would be a preview "
            "of unthemed Firefox")

    m = session.m
    for mode in modes:
        session.set_dark(mode == "dark")
        if mode == "dark":
            time.sleep(2.0)

        _shot(m, outdir, f"{mode}-01-window")

        m.script(FOCUS_URLBAR, ["whitesur firefox theme"])
        time.sleep(1.0)
        _shot(m, outdir, f"{mode}-02-urlbar")
        m.script(BLUR_URLBAR)
        time.sleep(0.8)

        m.script(OPEN_FINDBAR)
        time.sleep(1.2)
        m.script(FILL_FINDBAR, ["whitesur"])
        time.sleep(0.8)
        _shot(m, outdir, f"{mode}-03-findbar")
        m.script(CLOSE_FINDBAR)
        time.sleep(0.6)

    (outdir / "render-info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    return info


def _shot(m, outdir: Path, name: str):
    png = m.screenshot()
    if len(png) < 2000:
        raise RuntimeError(f"screenshot {name} is implausibly small ({len(png)} bytes)")
    (outdir / f"{name}.png").write_bytes(png)
    print(f"  captured {name}.png ({len(png) // 1024} KB)", flush=True)


def find_firefox(explicit=None):
    """Locate a Firefox binary, preferring an explicit path."""
    if explicit:
        return explicit
    env = os.environ.get("FIREFOX_BIN")
    if env:
        return env
    candidates = [
        "/Applications/Firefox.app/Contents/MacOS/firefox",
        str(Path.home() / "Applications/Firefox.app/Contents/MacOS/firefox"),
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        "/usr/bin/firefox", "/usr/local/bin/firefox", "/snap/bin/firefox",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    found = shutil.which("firefox")
    if found:
        return found
    raise SystemExit(
        "Could not find Firefox. Pass --firefox /path/to/firefox or set FIREFOX_BIN.")
