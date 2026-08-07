#!/usr/bin/env python3
"""Screenshot the WhiteSur theme's browser chrome for PR previews.

Installs the theme into a throwaway Firefox profile the same way install.sh
does (copy chrome/ and configuration/user.js into the profile), launches
Firefox, and drives it over Marionette to capture the browser UI in a few
states.

Marionette is a plain TCP + length-prefixed-JSON protocol, so this needs
nothing outside the standard library -- no selenium, no geckodriver, and so no
driver/browser version matching to keep green.

Screenshots are taken in Marionette's *chrome* context, which captures the
browser window's own document. That is what makes toolbars and tabs show up at
all; a normal WebDriver screenshot only captures page content. It also means
native popup widgets (the app menu, context menus) are NOT captured -- they are
separate OS-level windows. Every view here is therefore an in-document surface.

Usage:
    python3 render.py --repo . --firefox /path/to/firefox --out shots/
"""

import argparse
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

MARIONETTE_PORT = 2828
WINDOW_WIDTH = 1280
# Tall enough for the chrome, a strip of page content, and the find bar docked
# at the bottom -- without a screenful of empty page padding every comparison.
WINDOW_HEIGHT = 480


class MarionetteError(RuntimeError):
    pass


class Marionette:
    """Minimal Marionette client. Wire framing is '<byte-length>:<json>'."""

    def __init__(self, host="127.0.0.1", port=MARIONETTE_PORT):
        self.host = host
        self.port = port
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
            except OSError as exc:  # Firefox is not listening yet
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
                    continue  # stale reply, keep reading
                if error:
                    raise MarionetteError(f"{name} failed: {error}")
                return result

    def set_context(self, value):
        # Context switching is a Marionette extension rather than a WebDriver
        # spec command, and its namespace has moved between Firefox versions.
        errors = []
        for name in ("Marionette:SetContext", "WebDriver:SetContext", "setContext"):
            try:
                return self.command(name, {"value": value})
            except MarionetteError as exc:
                if "unknown command" not in str(exc):
                    raise
                errors.append(name)
        raise MarionetteError(f"no usable SetContext command (tried {errors})")

    @staticmethod
    def _unwrap(result):
        # Marionette returns script results as {"value": ...}.
        if isinstance(result, dict) and set(result) == {"value"}:
            return result["value"]
        return result

    def script(self, source, args=None):
        return self._unwrap(self.command(
            "WebDriver:ExecuteScript",
            {"script": source, "args": args or [], "sandbox": "system", "newSandbox": False},
        ))

    def async_script(self, source, args=None, timeout=30000):
        return self._unwrap(self.command(
            "WebDriver:ExecuteAsyncScript",
            {
                "script": source,
                "args": args or [],
                "sandbox": "system",
                "newSandbox": False,
                "scriptTimeout": timeout,
            },
        ))

    def screenshot(self):
        result = self.command("WebDriver:TakeScreenshot", {"full": True, "hash": False})
        return base64.b64decode(result["value"])

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


# Prefs that make a run reproducible: no first-run tour, no telemetry prompts,
# no update checks, no promos, no animations -- plus the theme's own required
# prefs so userChrome.css is actually loaded.
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
// Mozilla's campaigns. Left enabled they can differ between the base run and
// the head run, producing diffs that have nothing to do with the PR.
user_pref("browser.vpn_promo.enabled", false);
user_pref("browser.promo.focus.enabled", false);
user_pref("browser.contentblocking.report.hide_vpn_banner", true);
user_pref("browser.ipProtection.enabled", false);
user_pref("browser.urlbar.quicksuggest.enabled", false);
user_pref("browser.urlbar.suggest.quicksuggest.sponsored", false);
user_pref("extensions.pocket.enabled", false);

// Nimbus/Normandy can switch UI features on remotely, so pin them off to keep
// two runs of the same workflow comparable.
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

# CI-only overrides. These hide artifacts of the automation harness itself --
# never theme rules -- so a preview shows what a real user would see.
CI_ONLY_CSS = """/* Injected by .github/preview/render.py -- CI harness only.
 * Firefox marks automated sessions with a robot icon in the address bar.
 * It is not part of the theme, so hide it to keep previews representative. */
#remote-control-box,
#remote-control-icon {
  display: none !important;
}

/* Rollout-gated Mozilla feature button. Whether it appears depends on a
 * remote config rather than on this repo, so keep it out of previews to stop
 * it showing up as a phantom diff. */
#ipprotection-button {
  display: none !important;
}
"""

XULSTORE = {
    "chrome://browser/content/browser.xhtml": {
        "main-window": {
            "screenX": "0",
            "screenY": "0",
            "width": str(WINDOW_WIDTH),
            "height": str(WINDOW_HEIGHT),
            "sizemode": "normal",
        }
    }
}

# Offline pages so a preview never depends on the network or on a live site's
# content changing between the base run and the head run.
SAMPLE_PAGES = {
    "start.html": ("WhiteSur", "<h1>WhiteSur Firefox Theme</h1><p>Preview page.</p>"),
    "docs.html": ("Documentation", "<h1>Documentation</h1><p>Second tab.</p>"),
    "issues.html": ("Issue tracker", "<h1>Issues</h1><p>Third tab.</p>"),
}


def build_pages(dest: Path):
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
            "font:16px -apple-system,'Segoe UI',sans-serif\">"
            f"{body}",
            encoding="utf-8",
        )
        urls[name] = path.resolve().as_uri()
    return urls


def build_profile(repo: Path, profile: Path, dark: bool):
    profile.mkdir(parents=True, exist_ok=True)

    # Mirrors install.sh: the theme is just chrome/ dropped into the profile.
    shutil.copytree(repo / "chrome", profile / "chrome")

    # userChrome.css @imports customChrome.css, which the repo does not ship.
    # Write it here so the import resolves and carries the CI-only overrides.
    (profile / "chrome" / "customChrome.css").write_text(CI_ONLY_CSS, encoding="utf-8")

    prefs = ""
    repo_userjs = repo / "configuration" / "user.js"
    if repo_userjs.exists():
        prefs += repo_userjs.read_text(encoding="utf-8") + "\n"
    prefs += EXTRA_PREFS % {"port": MARIONETTE_PORT}
    # The theme's dark rules are behind @media (prefers-color-scheme: dark),
    # so this pref is what actually switches the preview between the two.
    prefs += 'user_pref("ui.systemUsesDarkTheme", %d);\n' % (1 if dark else 0)
    (profile / "user.js").write_text(prefs, encoding="utf-8")

    (profile / "xulstore.json").write_text(json.dumps(XULSTORE), encoding="utf-8")


# --- chrome-context scripts -------------------------------------------------

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
    const items = [
      ["GitHub", "https://github.com/"],
      ["Mozilla", "https://www.mozilla.org/"],
      ["WhiteSur", "https://github.com/AdamXweb/WhiteSurFirefoxThemeMacOS"],
    ];
    for (const [title, url] of items) {
      await PlacesUtils.bookmarks.insert({
        parentGuid: PlacesUtils.bookmarks.toolbarGuid,
        type: PlacesUtils.bookmarks.TYPE_BOOKMARK,
        title, url,
      });
    }
    done(true);
  } catch (e) {
    done("error: " + e);
  }
})();
"""

SETUP_TABS = """
const [urls] = arguments;
const sp = Services.scriptSecurityManager.getSystemPrincipal();
const win = Services.wm.getMostRecentWindow("navigator:browser");
const gb = win.gBrowser;
while (gb.tabs.length > 1) { gb.removeTab(gb.tabs[gb.tabs.length - 1]); }
gb.selectedBrowser.loadURI(Services.io.newURI(urls[0]), {triggeringPrincipal: sp});
for (let i = 1; i < urls.length; i++) {
  gb.addTab(urls[i], {triggeringPrincipal: sp});
}
// Pin the first tab so the pinned/unpinned boundary is visible.
gb.pinTab(gb.tabs[0]);
gb.selectedTab = gb.tabs[1];
return gb.tabs.length;
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

SET_DARK = """
Services.prefs.setIntPref("ui.systemUsesDarkTheme", arguments[0]);
return Services.prefs.getIntPref("ui.systemUsesDarkTheme");
"""

BROWSER_INFO = """
const win = Services.wm.getMostRecentWindow("navigator:browser");
return {
  version: Services.appinfo.version,
  buildID: Services.appinfo.appBuildID,
  os: Services.appinfo.OS,
  dpr: win.devicePixelRatio,
  outer: [win.outerWidth, win.outerHeight],
  legacyStylesheets: Services.prefs.getBoolPref(
    "toolkit.legacyUserProfileCustomizations.stylesheets", false),
};
"""


def capture(client, outdir: Path, name: str):
    png = client.screenshot()
    if len(png) < 2000:
        raise RuntimeError(f"screenshot {name} is implausibly small ({len(png)} bytes)")
    path = outdir / f"{name}.png"
    path.write_bytes(png)
    print(f"  captured {name}.png ({len(png) // 1024} KB)", flush=True)
    return path


def render(repo: Path, firefox: str, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    workdir = Path(tempfile.mkdtemp(prefix="whitesur-preview-"))
    profile = workdir / "profile"
    urls = build_pages(workdir / "pages")
    build_profile(repo, profile, dark=False)

    env = dict(os.environ)
    env["MOZ_DISABLE_AUTO_SAFE_MODE"] = "1"
    env["MOZ_CRASHREPORTER_DISABLE"] = "1"
    # Chrome UI does not paint in headless mode, so make sure nothing in the
    # environment forces it on.
    env.pop("MOZ_HEADLESS", None)

    cmd = [
        firefox,
        "--profile", str(profile),
        "--marionette",
        # Firefox 137+ requires this opt-in before Marionette will hand out the
        # chrome context that makes browser-UI screenshots possible.
        "-remote-allow-system-access",
        "--no-remote",
        "--new-window", "about:blank",
    ]
    print("launching: " + " ".join(cmd), flush=True)
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    client = Marionette()
    info = None
    try:
        client.connect()
        client.set_context("chrome")
        print("marionette connected (chrome context)", flush=True)

        client.script(RESIZE, [WINDOW_WIDTH, WINDOW_HEIGHT])
        result = client.async_script(SEED_BOOKMARKS)
        if result is not True:
            print(f"  note: bookmark seeding returned {result!r}", flush=True)
        client.script(SETUP_TABS, [[urls["start.html"], urls["docs.html"], urls["issues.html"]]])
        time.sleep(3.0)

        info = client.script(BROWSER_INFO)
        print(f"  firefox {info['version']} ({info['os']}), dpr={info['dpr']}, "
              f"window={info['outer']}, legacyStylesheets={info['legacyStylesheets']}",
              flush=True)
        if not info["legacyStylesheets"]:
            raise RuntimeError(
                "toolkit.legacyUserProfileCustomizations.stylesheets is false; "
                "userChrome.css would not be applied and the preview would be "
                "of unthemed Firefox")

        for mode in ("light", "dark"):
            if mode == "dark":
                client.script(SET_DARK, [1])
                time.sleep(2.0)

            capture(client, outdir, f"{mode}-01-window")

            client.script(FOCUS_URLBAR, ["whitesur firefox theme"])
            time.sleep(1.0)
            capture(client, outdir, f"{mode}-02-urlbar")
            client.script(BLUR_URLBAR)
            time.sleep(0.8)

            client.script(OPEN_FINDBAR)
            time.sleep(1.2)
            client.script(FILL_FINDBAR, ["whitesur"])
            time.sleep(0.8)
            capture(client, outdir, f"{mode}-03-findbar")
            client.script(CLOSE_FINDBAR)
            time.sleep(0.6)

        (outdir / "render-info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        return info
    finally:
        client.quit()
        try:
            proc.wait(timeout=45)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(workdir, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True, type=Path, help="theme repo root")
    ap.add_argument("--firefox", required=True, help="path to the firefox binary")
    ap.add_argument("--out", required=True, type=Path, help="output directory for PNGs")
    args = ap.parse_args()

    repo = args.repo.resolve()
    if not (repo / "chrome" / "userChrome.css").exists():
        print(f"error: {repo} does not look like the theme repo "
              f"(no chrome/userChrome.css)", file=sys.stderr)
        return 2

    render(repo, args.firefox, args.out.resolve())
    print(f"\nwrote screenshots to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
