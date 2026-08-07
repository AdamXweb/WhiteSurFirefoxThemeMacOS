#!/usr/bin/env python3
"""fxcss - a testing toolkit for this userChrome.css theme.

    fxcss watch        edit CSS in your editor and see it live, ~2ms per save
    fxcss shot         capture the standard screenshot set
    fxcss compare      diff two screenshot sets into before/after/diff images
    fxcss catalogue    build the directory of themeable UI parts
    fxcss doctor       report what this Firefox supports

Run `fxcss <command> --help` for the options of each.
"""

import argparse
import signal
import subprocess
import sys
import time
from pathlib import Path

import core

REPO_DEFAULT = Path(__file__).resolve().parents[2]


def _watched_files(repo: Path):
    roots = [repo / "chrome", repo / "custom"]
    for root in roots:
        if root.exists():
            for p in root.rglob("*"):
                if p.is_file() and p.suffix in (".css", ".svg"):
                    yield p


def _fingerprint(repo: Path):
    return {p: p.stat().st_mtime_ns for p in _watched_files(repo)}


def cmd_watch(args):
    repo = args.repo.resolve()
    firefox = core.find_firefox(args.firefox)

    # Turn a terminate signal into the same clean exit as Ctrl-C, so the
    # browser is always shut down rather than left running with a temp profile.
    def _bail(signum, frame):
        raise KeyboardInterrupt
    for sig in (signal.SIGTERM, signal.SIGHUP):
        try:
            signal.signal(sig, _bail)
        except (AttributeError, ValueError, OSError):
            pass  # not available on this platform

    print(f"fxcss watch\n  repo:    {repo}\n  firefox: {firefox}")
    if args.native_menus is False:
        print("  menus:   XUL (themeable) - right-click to inspect them live")

    # An empty userChrome.css hands the stylesheet entirely to us, so replacing
    # it reflects deletions as well as additions -- a rule you remove really
    # disappears instead of lingering from the startup copy.
    session = core.Session(repo, firefox, dark=args.dark,
                           native_menus=args.native_menus, empty_user_chrome=True)
    with session:
        session.setup_window()
        session.reload_theme()
        print(f"\n  theme loaded. Editing files under chrome/ reloads automatically.")
        print("  Ctrl-C to stop.\n")

        state = _fingerprint(repo)
        reloads = 0
        try:
            while True:
                time.sleep(args.interval)
                current = _fingerprint(repo)
                if current == state:
                    continue
                changed = sorted(
                    {p for p in set(current) | set(state)
                     if current.get(p) != state.get(p)})
                state = current
                t0 = time.perf_counter()
                try:
                    session.reload_theme()
                except Exception as exc:  # a half-saved file should not kill the loop
                    print(f"  ! reload failed: {exc}")
                    continue
                reloads += 1
                ms = (time.perf_counter() - t0) * 1000
                names = ", ".join(p.name for p in changed[:3])
                if len(changed) > 3:
                    names += f" +{len(changed) - 3} more"
                print(f"  [{reloads:>3}] {names} -> reloaded in {ms:.0f} ms")
                if args.shot:
                    args.shot.parent.mkdir(parents=True, exist_ok=True)
                    args.shot.write_bytes(session.m.screenshot())
                    print(f"        wrote {args.shot}")
        except KeyboardInterrupt:
            print("\n  stopping.")
    return 0


def cmd_shot(args):
    repo = args.repo.resolve()
    if not (repo / "chrome" / "userChrome.css").exists():
        print(f"error: {repo} is not the theme repo (no chrome/userChrome.css)",
              file=sys.stderr)
        return 2
    firefox = core.find_firefox(args.firefox)
    with core.Session(repo, firefox) as session:
        core.capture_views(session, args.out.resolve())
    print(f"\nwrote screenshots to {args.out}")
    return 0


def cmd_compare(args):
    import compare
    return compare.run(args.base.resolve(), args.head.resolve(),
                       args.out.resolve(), args.platform)


def cmd_catalogue(args):
    import catalogue
    repo = args.repo.resolve()
    firefox = core.find_firefox(args.firefox)
    out = args.out.resolve()
    with core.Session(repo, firefox, native_menus=args.native_menus) as session:
        result = catalogue.build(session, repo, out)
    found = sum(1 for e in result["entries"]
                if any(m["found"] for m in e["modes"].values()))
    print(f"\n{found}/{len(result['entries'])} landmarks resolved")
    print(f"open {out / 'index.html'}")
    if args.open:
        opener = {"darwin": "open", "win32": "start"}.get(sys.platform, "xdg-open")
        subprocess.run([opener, str(out / "index.html")], check=False)
    return 0


def cmd_doctor(args):
    repo = args.repo.resolve()
    firefox = core.find_firefox(args.firefox)
    print(f"repo:    {repo}")
    print(f"firefox: {firefox}")
    with core.Session(repo, firefox) as session:
        info = session.info()
    print(f"\nversion: {info['version']} (build {info['buildID']}) on {info['os']}")
    print(f"window:  {info['outer']} at dpr {info['dpr']}")
    print(f"userChrome.css enabled: {info['legacyStylesheets']}")

    native = info["nativeContextMenus"]
    print("\ncontext menus:")
    for platform, value in native.items():
        if value is None:
            continue
        state = "native (CSS cannot style them)" if value else "XUL (themeable)"
        print(f"  {platform:<8} native-context-menus={value} -> {state}")
    if native.get("macos"):
        print("  note: on macOS this defaults to true, so the theme's menupopup\n"
              "        rules have no effect on right-click menus there. Run with\n"
              "        --native-menus=false to work on them.")

    sheets = sorted((repo / "chrome").rglob("*.css"))
    total = sum(p.stat().st_size for p in sheets)
    print(f"\ntheme: {len(sheets)} stylesheets, {total:,} bytes")
    missing = [p for p in ("chrome/userChrome.css", "chrome/WhiteSur/theme.css")
               if not (repo / p).exists()]
    print("missing expected files: " + (", ".join(missing) if missing else "none"))
    return 0


def _add_common(p, need_repo=True):
    if need_repo:
        p.add_argument("--repo", type=Path, default=REPO_DEFAULT,
                       help="theme repo root (default: this checkout)")
    p.add_argument("--firefox", default=None,
                   help="path to the firefox binary (default: autodetect, or $FIREFOX_BIN)")


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="fxcss", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("watch", help="live-reload the theme as you edit")
    _add_common(w)
    w.add_argument("--dark", action="store_true", help="start in dark mode")
    w.add_argument("--interval", type=float, default=0.4, help="poll seconds")
    w.add_argument("--shot", type=Path, default=None,
                   help="also write a screenshot here after every reload")
    w.add_argument("--native-menus", dest="native_menus", default=None,
                   type=lambda v: v.lower() not in ("false", "0", "no"),
                   metavar="BOOL",
                   help="false makes right-click menus XUL, so the theme can style them")
    w.set_defaults(func=cmd_watch)

    s = sub.add_parser("shot", help="capture the standard screenshot set")
    _add_common(s)
    s.add_argument("--out", type=Path, required=True)
    s.set_defaults(func=cmd_shot)

    c = sub.add_parser("compare", help="diff two screenshot sets")
    c.add_argument("--base", type=Path, required=True)
    c.add_argument("--head", type=Path, required=True)
    c.add_argument("--out", type=Path, required=True)
    c.add_argument("--platform", default="local")
    c.set_defaults(func=cmd_compare)

    g = sub.add_parser("catalogue", help="build the themeable UI directory")
    _add_common(g)
    g.add_argument("--out", type=Path, default=Path("fxcss-catalogue"))
    g.add_argument("--open", action="store_true", help="open the result when done")
    g.add_argument("--native-menus", dest="native_menus", default=None,
                   type=lambda v: v.lower() not in ("false", "0", "no"), metavar="BOOL")
    g.set_defaults(func=cmd_catalogue)

    d = sub.add_parser("doctor", help="report what this Firefox supports")
    _add_common(d)
    d.set_defaults(func=cmd_doctor)

    args = ap.parse_args(argv)
    # Watch mode is a long-running log; keep it readable when piped to a file
    # or a terminal multiplexer rather than buffering until exit.
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except AttributeError:
        pass
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
