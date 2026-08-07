# PR previews

Every pull request that touches the theme gets a comment showing the browser
chrome **before** and **after** the change, plus a highlight of exactly which
pixels moved — on macOS and Windows, in light and dark mode.

The point is to review a CSS change without installing it.

## What you get

Six views per platform: the browser window, the focused address bar, and the
find bar, each rendered in light and dark. Views that render identically are
reported as unchanged rather than pictured, so the comment shows only what the
pull request actually altered. If nothing changes anywhere, the comment says
so — which is itself a useful review result.

## How it works

`render.py` installs the theme into a throwaway Firefox profile exactly the way
`install.sh` does — copy `chrome/` and `configuration/user.js` into the profile
— then drives Firefox over **Marionette**, Firefox's built-in automation
protocol, and screenshots it. `compose.py` diffs the two sets and draws the
comparison images.

Screenshots are taken in Marionette's *chrome context*, which captures the
browser window's own document. That is the part that matters here: an ordinary
WebDriver screenshot only captures page content, so toolbars and tabs would
never appear.

Marionette is plain TCP with length-prefixed JSON, so `render.py` needs nothing
outside the Python standard library — no Selenium, no geckodriver, and so no
driver-to-browser version matching to keep green. Only `compose.py` has a
dependency, on Pillow.

### Known limits

- **Native popups are not captured.** The app menu and context menus are
  separate OS-level windows, not part of the browser document. Every view is
  therefore an in-document surface. Grabbing the whole screen instead was tried
  and rejected: it depends on window stacking and captures whatever else is on
  the desktop.
- **Rendering is Firefox's, not your Mac's.** Widgets render as the runner's
  Firefox draws them. Both sides of a comparison come from the same runner and
  the same build, so differences are attributable to the pull request.
- **The comment only appears after this lands on the default branch.**
  `workflow_run` only ever runs the copy of a workflow on the default branch.

### Determinism

Screenshot comparison is only useful if an unchanged theme renders identically
twice. `render.py` therefore pins the things that would otherwise drift:
first-run tours, telemetry prompts and update checks are off; animations are
disabled; pages are local files rather than live sites; and Nimbus/Normandy are
disabled so Mozilla cannot switch a toolbar feature on remotely between the
base run and the head run.

Two overrides in `CI_ONLY_CSS` hide artifacts of the harness itself — the robot
icon Firefox shows in automated sessions, and the rollout-gated IP Protection
button. Neither is part of the theme.

## Running it yourself

```bash
python3 .github/preview/render.py --repo . --firefox /Applications/Firefox.app/Contents/MacOS/firefox --out shots/head
```

Point `--repo` at a second checkout to render the other side, then:

```bash
python3 .github/preview/compose.py --base shots/base --head shots/head --out out --platform local
```

## Security model

`pr-preview.yml` runs pull request code and therefore has **no write
permissions and no access to secrets** — it only produces an artifact.
`pr-preview-publish.yml` holds the write access and never runs pull request
code. It treats the artifact as untrusted: the pull request number is verified
against the head SHA of the run that produced it, only recognised file names
are republished, and the comment text is built from validated numbers rather
than from any string inside the artifact.

Images live on an orphan `ci-previews` branch under `pr-<number>/<sha>/`. Each
new push replaces that pull request's previous set, and `pr-preview-cleanup.yml`
removes the directory when the pull request closes.
