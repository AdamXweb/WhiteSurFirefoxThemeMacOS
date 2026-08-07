# fxcss — a testing toolkit for this theme

Editing `userChrome.css` normally means restarting Firefox to see anything. This
toolkit removes that loop, and adds a screenshot check on every pull request.

```bash
python3 tools/fxcss/fxcss.py watch        # edit CSS, see it live (~50ms)
python3 tools/fxcss/fxcss.py catalogue    # directory of themeable UI parts
python3 tools/fxcss/fxcss.py shot         # capture the standard screenshots
python3 tools/fxcss/fxcss.py compare      # diff two sets into before/after/diff
python3 tools/fxcss/fxcss.py doctor       # what does this Firefox support?
```

Only `compare` and `catalogue` need a dependency (`pip install pillow`).
Everything else is standard library.

## watch — the editing loop

```bash
python3 tools/fxcss/fxcss.py watch
```

Opens a Firefox with the theme installed into a throwaway profile, then watches
`chrome/` and `custom/`. Save a file in your editor and the running window
updates in about 50ms — no restart, no reinstall, and your real Firefox profile
is never touched.

The window is yours to drive: open menus, right-click things, resize, toggle
panels. Useful flags:

| flag | effect |
| --- | --- |
| `--dark` | start in dark mode |
| `--native-menus=false` | make right-click menus themeable — see below |
| `--shot path.png` | also write a screenshot after every reload |

### How the reload works, and why it is a copy

Each reload copies `chrome/` into a fresh numbered directory inside the temp
profile and loads `userChrome.css` from there as a user sheet, dropping the
previous one. The new path gives the entry sheet *and* every `@import` beneath
it a URI Firefox has not seen, which is what actually defeats the stylesheet
cache.

Concatenating the imports into one sheet would be faster, and was tried first.
It is wrong: `@namespace` is scoped to the stylesheet that declares it, so
inlining lets one file's namespace apply to every other file's rules and
silently changes which elements match. The measured result was a browser that
looked almost entirely unthemed.

Fidelity was measured rather than assumed: a hot-swapped window differs from one
that loaded the theme normally at startup by **0.28% of pixels**, confined to a
one-pixel vertical offset in the address bar. Good enough to design against.
`shot` does not use this path at all — it loads the theme the normal way — so CI
comparisons are unaffected.

## catalogue — the directory of themeable parts

```bash
python3 tools/fxcss/fxcss.py catalogue --open
```

Builds an HTML page listing the UI landmarks a theme can target. For each one:

- a cropped screenshot of the real element, in light and dark
- its selector, and the styles actually in effect
- every rule in this repo that targets it, as `file:line`

Plus an annotated overview screenshot with each landmark numbered.

Everything is measured from a running browser rather than hardcoded, so it stays
honest as Firefox changes — an element that no longer exists is reported as
missing instead of being quietly documented. That is not hypothetical: building
this found that `#appcontent` no longer exists in Firefox 153 and there is no
`#sidebar-button`.

## shot / compare — what CI runs

`shot` captures six views (browser window, focused address bar, find bar, each
in light and dark). `compare` diffs two sets and writes a stacked
before/after/changed-pixels image per view that differs. The
`.github/workflows/pr-preview*.yml` workflows run these on macOS and Windows for
every pull request and post the result as a comment.

## Two things that cannot be captured, and one that surprises people

**Right-click menus are native on macOS.** Firefox 153 defaults
`widget.macos.native-context-menus` to `true`, which means macOS draws those
menus itself and **CSS cannot style them at all** — the `menupopup` and
`menuitem` rules in `parts/popups.css` have no effect there. They *do* apply on
Windows and Linux. Run `fxcss doctor` to see the setting on your machine, or
`fxcss watch --native-menus=false` to switch Firefox to XUL menus so you can
work on that styling on a Mac.

**Popups cannot be screenshotted.** Menus and the app menu are separate
OS-level windows, so they appear in neither a Marionette chrome screenshot nor
a `drawWindow` rasterisation of the browser window. Capturing the whole screen
instead was tried and rejected: it depends on window stacking and picks up
whatever else is on the desktop. Capturing the popup's own screen rectangle was
also tried; under automation the popup reports itself open but never lays out a
box to capture. So every view here is an in-document surface.

**Screenshots need a real window.** Firefox headless does not render browser
chrome at all, and Firefox 137+ requires the `-remote-allow-system-access` flag
before Marionette will hand over the chrome context that makes UI screenshots
possible.

## Determinism

A screenshot comparison is only useful if an unchanged theme renders identically
twice. The profile therefore pins what would otherwise drift: first-run tours,
telemetry prompts and update checks off; animations disabled; local pages instead
of live sites; and Nimbus/Normandy disabled so Mozilla cannot switch a toolbar
feature on remotely between two runs.

Two rules in `CI_ONLY_CSS` hide artifacts of the harness itself — the robot icon
Firefox shows in automated sessions, and the rollout-gated IP Protection button.
Neither is part of the theme.

Each session also picks its own Marionette port. Firefox's fixed default of 2828
means a leaked browser from an earlier run would silently accept the next
session's connection, which presents as the theme mysteriously not applying.

## Security model of the CI half

`pr-preview.yml` runs pull request code and therefore has **no write permissions
and no access to secrets** — it only produces an artifact.
`pr-preview-publish.yml` holds the write access and never runs pull request code.
It treats the artifact as untrusted: the pull request number is verified against
the head SHA of the run that produced it, only recognised file names are
republished, and the comment text is built from validated numbers rather than
from any string inside the artifact.

Images live on an orphan `ci-previews` branch under `pr-<number>/<sha>/`. Each
push replaces that pull request's previous set, and `pr-preview-cleanup.yml`
removes the directory when the pull request closes.
