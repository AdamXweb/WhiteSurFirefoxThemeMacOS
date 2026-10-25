"""Exercise the optional single-tab sheet in real, disposable Firefox profiles.

Requires fxcss==0.22.0 and a visible Firefox (FIREFOX_BIN can select its binary).
Run: python tests/single_tab_hidden.py --out single-tab-results
"""

import argparse
import json
import tempfile
import time
from pathlib import Path

from fxcss import core, install


PROBE = """
const w=Services.wm.getMostRecentWindow('navigator:browser'),d=w.document;
function measure(selector) {
  const e=d.querySelector(selector);
  if(!e)return null;
  const s=w.getComputedStyle(e),r=e.getBoundingClientRect();
  let visible=r.width>0 && r.height>0;
  for(let p=e;p;p=p.parentElement) {
    const style=w.getComputedStyle(p);
    visible &&= style.display!=='none' && style.visibility==='visible';
  }
  const hit=d.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
  return {visible,hit:!!hit && (hit===e || e.contains(hit)),
          x:r.x,y:r.y,width:r.width,height:r.height,
          display:s.display,visibility:s.visibility};
}
return {
  version:Services.appinfo.version,os:Services.appinfo.OS,
  count:w.gBrowser.tabs.length,
  orient:d.getElementById('tabbrowser-tabs').getAttribute('orient'),
  customizing:d.documentElement.hasAttribute('customizing'),
  toolbar:measure('#TabsToolbar'),strip:measure('#tabbrowser-tabs'),
  newTab:measure('#new-tab-button'),inlineNewTab:measure('#tabs-newtab-button'),
  controls:measure('#TabsToolbar .titlebar-buttonbox-container'),
  close:measure('#TabsToolbar .titlebar-close'),
  minimize:measure('#TabsToolbar .titlebar-min'),
  maximize:measure('#TabsToolbar .titlebar-max'),
  restore:measure('#TabsToolbar .titlebar-restore'),
  extra:measure('#bookmarks-menu-button'),
  palette:w.getComputedStyle(d.documentElement)
    .getPropertyValue('--gnome-toolbar-background').trim()
};
"""


def change(session, script):
    session.m.script(
        "const w=Services.wm.getMostRecentWindow('navigator:browser');" + script)
    time.sleep(0.5)


def run(repo, out):
    out.mkdir(parents=True, exist_ok=True)
    results = {}

    def capture(session, name):
        state = session.m.script(PROBE)
        results[name] = state
        (out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
        (out / (name + '.png')).write_bytes(session.m.screenshot())
        print(name, state['count'], state['strip']['display'],
              state['toolbar']['height'], flush=True)
        return state

    def buttons_remain(state, reference):
        for name in ('controls', 'close', 'minimize'):
            if reference[name] and reference[name]['visible']:
                assert state[name] and state[name]['visible'], (name, state)
        # These are the Windows controls reported in #227.
        if state['os'] == 'WINNT':
            assert all(state[name]['visible'] for name in
                       ('close', 'minimize')), state
            assert any(state[name] and state[name]['visible']
                       for name in ('maximize', 'restore')), state

    with tempfile.TemporaryDirectory(prefix='whitesur-single-tab-') as temp:
        profile = Path(temp) / 'installed'
        profile.mkdir()
        palette = repo / 'custom/theme-github-dark.css'
        manifest = install.install_theme(repo, profile, 'single-tab-test',
                                         sheets=[palette])
        assert not any(p.endswith('/singletabhidden.css')
                       for p in manifest['files'])
        with core.Session(profile, core.find_firefox(), dark=True) as session:
            baseline = capture(session, 'default-install')
            assert baseline['strip']['visible'], baseline
            assert baseline['palette'] == '#0d1117', baseline

        for swap in (False, True):
            sheets = [palette, repo / 'custom/singletabhidden.css']
            if swap:
                sheets.append(repo / 'custom/windows-swapclose.css')
            install.install_theme(repo, profile, 'single-tab-test', sheets=sheets)
            prefix = 'right-' if swap else 'left-'
            with core.Session(profile, core.find_firefox(), dark=True) as session:
                single = capture(session, prefix + 'single-tab')
                buttons_remain(single, baseline)
                assert single['strip']['display'] == 'none', single
                assert single['toolbar']['visibility'] == 'visible', single
                assert single['newTab']['visible'] and single['newTab']['hit'], single
                assert single['palette'] == '#0d1117', single

                # Hit testing above verifies the button is reachable; invoking
                # its command verifies that opening a tab restores the strip.
                change(session, "w.document.getElementById('new-tab-button').click();")
                two = capture(session, prefix + 'two-tabs')
                assert two['count'] == 2 and two['strip']['visible'], two
                buttons_remain(two, baseline)
                change(session, "w.gBrowser.removeTab(w.gBrowser.tabs[1],{animate:false});")
                again = capture(session, prefix + 'back-to-one')
                assert again['count'] == 1 and again['strip']['display'] == 'none', again

                # Also isolate the customization guard with exactly one tab;
                # entering Firefox's editor can create a second temporary tab.
                change(session, "w.document.documentElement.setAttribute('customizing','true');")
                editing = capture(session, prefix + 'customizing-one-tab')
                assert editing['count'] == 1 and editing['strip']['visible'], editing
                change(session, "w.document.documentElement.removeAttribute('customizing');")

                change(session, "w.CustomizableUI.addWidgetToArea('new-tab-button','nav-bar');")
                compact = capture(session, prefix + 'compact')
                assert compact['strip']['display'] == 'none', compact
                assert compact['toolbar']['height'] == 0, compact
                assert compact['newTab']['visible'] and compact['newTab']['hit'], compact
                buttons_remain(compact, baseline)

                if compact['os'] == 'WINNT':
                    change(session, "w.maximize();")
                    maximized = capture(session, prefix + 'maximized')
                    assert maximized['strip']['display'] == 'none', maximized
                    assert maximized['newTab']['visible'] and maximized['newTab']['hit'], maximized
                    buttons_remain(maximized, baseline)
                    change(session, "w.restore();")

                # A different customized widget must retain its toolbar space.
                change(session, "w.CustomizableUI.addWidgetToArea('bookmarks-menu-button','TabsToolbar');")
                custom = capture(session, prefix + 'custom-widget')
                assert custom['toolbar']['height'] > 0, custom
                assert custom['extra']['visible'] and custom['extra']['hit'], custom
                change(session, "w.CustomizableUI.removeWidgetFromArea('bookmarks-menu-button');")

                # Firefox must show the strip while editing toolbar placement.
                change(session, "w.gCustomizeMode.enter();")
                customizing = capture(session, prefix + 'customizing')
                assert customizing['customizing'] and customizing['strip']['visible'], customizing
                change(session, "w.gCustomizeMode.exit();")

                change(session, "w.gBrowser.pinTab(w.gBrowser.tabs[0]);")
                pinned = capture(session, prefix + 'pinned-only')
                assert pinned['strip']['visible'], pinned
                change(session, "w.BrowserCommands.openTab();")
                mixed = capture(session, prefix + 'pinned-and-normal')
                assert mixed['count'] == 2 and mixed['strip']['visible'], mixed
                change(session, "w.gBrowser.removeTab(w.gBrowser.tabs[1],{animate:false});w.gBrowser.unpinTab(w.gBrowser.tabs[0]);")

                session.m.script(core.ENABLE_VERTICAL_TABS)
                time.sleep(1)
                vertical = capture(session, prefix + 'vertical')
                assert vertical['orient'] == 'vertical' and vertical['strip']['visible'], vertical
                change(session, "Services.prefs.setBoolPref('sidebar.verticalTabs',false);")

                change(session, "w.gBrowser.addTabGroup([w.gBrowser.tabs[0]],{label:'Keep group',color:'blue'});")
                grouped = capture(session, prefix + 'grouped-only')
                assert grouped['strip']['visible'], grouped
                change(session, "w.BrowserCommands.openTab();w.BrowserCommands.openTab();w.gBrowser.addTabGroup([w.gBrowser.tabs[1]],{label:'Another group',color:'green'});")
                outside = capture(session, prefix + 'groups-and-normal')
                assert outside['count'] == 3 and outside['strip']['visible'], outside

    print('PASS: default install, single/two tab transitions, controls, New Tab, '
          'compact/customized placement, customization, pinned/grouped/vertical tabs; '
          'both window-button placements.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.repo.resolve(), args.out.resolve())
