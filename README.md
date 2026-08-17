## Firefox WhiteSur theme
<p align="center">
<img width="120" src="https://github.com/AdamXweb/WhiteSurFirefoxThemeMacOS/raw/master/githubpreview/safarifirefox.png?raw=true">
	<br>
A <code>MacOS</code> & <code>Windows</code> Firefox theme to look more like Big Sur Safari. (For Firefox 70+)</p>

![Preview](githubpreview/whitesur.gif?raw=true)

## Description

Aim is to make Firefox look more like MacOS Big Sur Safari.\
This is a CSS theme adapted to work on MacOS from the Linux GTK theme.\
Based on https://github.com/vinceliuice/WhiteSur-gtk-theme/tree/master/src/other/firefox \
(This is a quick modification, and is not written from scratch.)


## Try it without installing

To see the theme before applying to your own Firefox profile:

```bash
pipx install "fxcss[images]"     # no pipx? see pipx.pypa.io (brew install pipx on macOS)
fxcss try AdamXweb/WhiteSurFirefoxThemeMacOS
```

That opens a throwaway Firefox with the theme applied and leaves your main
profile untouched. Add `--dark` for dark mode, or
`--with compact-tabs,tabs-swapclose` to try the optional stylesheets described
below. Quit the browser and everything gets reset.

## Installation

The default way, on macOS, Windows and Linux — [fxcss](https://github.com/AdamXweb/fxcss) 0.14 or newer:

```bash
pipx install "fxcss[images]"     # no pipx? see pipx.pypa.io (brew install pipx on macOS)
fxcss install AdamXweb/WhiteSurFirefoxThemeMacOS
```

It installs into your Firefox profile all on macOS, Windows and Linux, including snap and flatpak Firefoxes on Linux. A Firefox in an unusual place is reachable via `FXCSS_PROFILE_ROOTS`; when more than one installed Firefox has profiles, fxcss asks which one to update. Your existing `chrome/` folder is backed up first, and optional stylesheets from `custom/` load with `--with`, e.g. `--with compact-tabs,tabs-swapclose`.

Run it without `--with` and it asks which optional stylesheets to include. It also labels each profile with the Firefox it belongs to (`[Release]`, `[Developer Edition]`, `[ESR]`), so you can pick the right one. To put everything back the way it was:

```bash
fxcss uninstall AdamXweb/WhiteSurFirefoxThemeMacOS
```

### With the install script (macOS & Linux)

Download the [latest release](https://github.com/AdamXweb/WhiteSurFirefoxThemeMacOS/releases/), or clone the repo above.\
A script has been added to streamline the installation process.\
Open terminal in the directory of the repo, and run `bash install.sh`\
Follow the prompts

### Installation flags

The script supports the following flags
- `-c` Left hand side tab close button
- `-w` Left hand side window close button
- `-p` Makes tabs height compact like current Safari
- `-f` To specify the default firefox folder (it will try to find the profile folder to place the theme within)
- `-l` Default location of most Linux installations
- The script installs to ESR profiles (`*.default-esr`) as well as release ones
- `-u` Remove the animation on URL bar to be clickable throughout
- `-n` Removes the identity colour from tabs
- `-v` Re-enables the tabview button
- `-e` Hides the extension button
- `-s` Single tab view (Tabs hidden when only one tab)
- `-t <name>` Colour theme (see Colour themes below)
- `-i` Increase contrast (see Colour themes below)
- `-r` Remove the theme

e.g. To install with script, with the tab close button left hand side: `bash install.sh -c` 

#### What each option looks like

Rendered by CI with [fxcss](https://github.com/AdamXweb/fxcss) from the current theme; they refresh automatically when the theme changes. Each one is cropped to the part of the window the option changes.

<details>
<summary><code>-c</code> Left-hand tab close button</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/tabs-swapclose-diff.png" alt="Before and after: Tabs with the close button on the left" width="830">

<sub><a href="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-tabs-swapclose.png">whole window</a></sub>

</details>
<details>
<summary><code>-w</code> Left-hand window buttons</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/windows-swapclose-diff.png" alt="Before and after: Window controls on the left" width="830">

<sub><a href="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-windows-swapclose.png">whole window</a></sub>

</details>
<details>
<summary><code>-p</code> Compact Safari-style tabs</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/compact-tabs-diff.png" alt="Before and after: Compact tab height" width="830">

<sub><a href="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-compact-tabs.png">whole window</a></sub>

</details>
<details>
<summary><code>-u</code> Standard URL bar</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-standard-urlbar.png" alt="URL bar without the click animation" width="830">

*No crop for this one: it changes nothing measurable on current Firefox, so there is no region to crop to. The selectors this sheet touches have moved.*

</details>
<details>
<summary><code>-n</code> No identity colour on tabs</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-noidentity.png" alt="Tabs without identity colour" width="830">

*No crop for this one: it changes nothing measurable on current Firefox, so there is no region to crop to. The selectors this sheet touches have moved.*

</details>
<details>
<summary><code>-v</code> Tab view button re-enabled</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/enabletabview-diff.png" alt="Before and after: Tab view button visible" width="830">

<sub><a href="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-enabletabview.png">whole window</a></sub>

</details>
<details>
<summary><code>-e</code> Extension button hidden</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/hideextension-diff.png" alt="Before and after: Toolbar without the extension button" width="830">

<sub><a href="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-hideextension.png">whole window</a></sub>

</details>
<details>
<summary><code>-s</code> Single tab hidden</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/singletabhidden-diff.png" alt="Before and after: Tab strip hidden with one tab open" width="830">

<sub><a href="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-singletabhidden.png">whole window</a></sub>

</details>

### Colour themes

The Safari layout, with another palette on top. Install with `-t <name>`, e.g. `bash install.sh -t dracula`

Available themes: `dracula`, `catppuccin-latte`, `catppuccin-frappe`, `catppuccin-macchiato`, `catppuccin-mocha`, `nord`, `gruvbox-dark`, `gruvbox-light`, `solarized-dark`, `solarized-light`, `tokyonight`, `material-ocean`, `material-palenight`, `one-dark`, `rose-pine`, `everforest-dark`, `ayu-mirage`, `night-owl`, `github-dark`, `monokai-pro`

A palette covers the window chrome, the panels (app menu, extensions, site information and permissions, the address bar's search-engine list), the bookmarks and history sidebars, the Library window, the DevTools toolbox, and the `about:` pages — `about:preferences`, `about:addons`, `about:newtab`.

DevTools follows the palette only when its own theme agrees with Firefox's appearance, since DevTools has a separate light/dark setting of its own (Settings > Themes in the toolbox). If they disagree, DevTools keeps its own colours rather than mixing the two.

#### Increase contrast

```bash
bash install.sh -t nord -i
```

`-i` pushes text to full strength, makes borders and separators visible, turns off the dimming on the idle address bar, and brings back the focus ring the palettes hide. It works with any palette, and on the base theme with no `-t` at all.

You do not need the flag if you already ask for more contrast at the OS level — macOS System Settings > Accessibility > Display > Increase contrast, or its Windows and GNOME equivalents. The theme responds to that on its own; `-i` is for turning it on regardless.

#### Previews

<details>
<summary>Ayu</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-ayu-mirage.png" alt="Ayu Mirage" width="830">

</details>
<details>
<summary>Catppuccin (4)</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-catppuccin-latte.png" alt="Catppuccin Latte" width="830">

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-catppuccin-frappe.png" alt="Catppuccin Frappé" width="830">

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-catppuccin-macchiato.png" alt="Catppuccin Macchiato" width="830">

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-catppuccin-mocha.png" alt="Catppuccin Mocha" width="830">

</details>
<details>
<summary>Dracula</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-dracula.png" alt="Dracula" width="830">

</details>
<details>
<summary>Everforest</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-everforest-dark.png" alt="Everforest Dark" width="830">

</details>
<details>
<summary>GitHub</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-github-dark.png" alt="GitHub Dark" width="830">

</details>
<details>
<summary>Gruvbox (2)</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-gruvbox-light.png" alt="Gruvbox Light" width="830">

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-gruvbox-dark.png" alt="Gruvbox Dark" width="830">

</details>
<details>
<summary>Material (2)</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-material-ocean.png" alt="Material Ocean" width="830">

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-material-palenight.png" alt="Material Palenight" width="830">

</details>
<details>
<summary>Monokai</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-monokai-pro.png" alt="Monokai Pro" width="830">

</details>
<details>
<summary>Night Owl</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-night-owl.png" alt="Night Owl" width="830">

</details>
<details>
<summary>Nord</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-nord.png" alt="Nord" width="830">

</details>
<details>
<summary>One Dark</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-one-dark.png" alt="One Dark Pro" width="830">

</details>
<details>
<summary>Rosé Pine</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-rose-pine.png" alt="Rosé Pine" width="830">

</details>
<details>
<summary>Solarized (2)</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-solarized-light.png" alt="Solarized Light" width="830">

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-solarized-dark.png" alt="Solarized Dark" width="830">

</details>
<details>
<summary>Tokyo Night</summary>

<img src="https://raw.githubusercontent.com/AdamXweb/WhiteSurFirefoxThemeMacOS/previews/variant-theme-tokyonight.png" alt="Tokyo Night" width="830">

</details>

A colour theme applies its palette in both light and dark OS modes. The dark palettes pair best with Firefox's dark appearance (or `ui.systemUsesDarkTheme` — see Manual colour override below) so menus and about: pages match the chrome.

To preview one without touching your profile:

```bash
fxcss try AdamXweb/WhiteSurFirefoxThemeMacOS --with theme-dracula --dark
```

Manual install: copy `custom/theme-<name>.css` into `chrome/WhiteSur/custom` within your profile, like any other override. One colour theme at a time.

### Vertical tabs

Firefox's vertical tabs (Settings → Browser layout, Firefox 133+) are styled.
The strip uses the sidebar colours, rows have rounded highlights like Safari,
and container tabs mark the edge of the row instead of the top. Colour themes
apply there too. Turn vertical tabs on in Firefox and the theme follows.

#### Optimal experience:
Make sure to right click and Customize Toolbar. From here, drag the new tab button up to the toolbar out of the tab section.

Install with the following modifications for Safari-like experience
` bash ./install.sh -c -n -s -e -p`

This will give you a look like this:
![Compact tabs below the address bar, tab close button on the left, no identity colour, extension button hidden, and the new tab button moved up into the toolbar](githubpreview/optimal-experience.png?raw=true)

### Manual installation (MacOS & Windows)

Copy `chrome` and `configuration` folders into your Firefox Profile Directory

To find your Firefox Profile Directory you can:

1. Go to `about:support` in Firefox.
2. Application Basics > Profile Directory > Open Directory.
3. Copy folders mentioned above into the profile folder. (usually has `-release` at the end).
4. If you are using Firefox 69+:
	1. Go to `about:config` in Firefox.
	2. Search for `toolkit.legacyUserProfileCustomizations.stylesheets` and set it to `true`.
5. Restart Firefox.
6. Done!

#### Manual theme overrides:
To manually add a custom override, copy the `*.css` from the `custom` folder of whichever option you are after. Place it in the `chrome/WhiteSur/custom` folder within the profile directory you opened above.

That's it, the theme should load your overriden settings

#### Swap navbar close buttons on Windows:
`windows-swapclose.css` contains the styles required to swap the close buttons, as well as to re-order the close button from MacOS styling to Windows.
Follow the directions above for the manual theme override to activate.
Can be installed with the `-w` command on the install script
#### Swap tab close button side
`tabs-swapclose.css` contains styles to place the close button for the tab on the left hand side for consistency with Safari. Can be installed with the `-c` command on the install script

### Manual colour override:

The theme obeys your system UI colour preferences. If you want to override it e.g. always have the dark theme, then you'll have to do the following.\
The solution if you don't want to change your System UI colour is to do add the following to your `about:config`\
Add: `ui.systemUsesDarkTheme` with the number value with 1 for dark, and 0 for light.\
![Screen Shot 2021-05-04 at 7 10 19 pm](https://user-images.githubusercontent.com/6800453/116982626-60317980-ad0c-11eb-96aa-0879b05c98fc.png)

Please note, you won't be able to change the System UI colour if you are using `privacy.resistFingerprinting`. This apparently is for both web pages and the System UI.

## Known bugs

If it is a fresh install of Firefox, the script for MacOS should enable the settings automatically, however users who have toggled settings may need to do the `about:config` in step 4 above.\
If for any reason the WhiteSur theme doesn't activate after using the script, follow steps 4.1 and 4.2 to toggle the stylesheets from within the Firefox settings.

The tab background colour can be overwritten by themes installed through firefox extensions.
e.g. if you are using a dark theme in light mode, tab backgrounds that are inactive are affected.
Fix: Change the installed theme to appropriate colour scheme to avoid issues.

If you're looking to change the directory to run the script, you can always type `bash` then drag the file into terminal. You can also type `cd` and then drag the folder and press enter to navigate to the directory.\
Alternatively, if you're running Catalina, the default terminal is zsh, meaning you can change folders by typing the name to enter the folder e.g. `WhiteSurFirefoxThemeMacOS`


Q: "Why bother doing this, and not just use safari?" \
A: I've used safari for quite a few years, and was rather disappointed with the change in extensions, particularly with content blocking. This prompted me to use uBlock origin on Firefox, and to customise it to have the best aesthetics, and simplest transition.

### New bugs

If you've found a new bug, please report it as a new issue with the templates provided.

Thanks!

## Contributing a CSS change

Every pull request that touches `chrome/`, `custom/` or `configuration/` gets a
comment showing the browser chrome **before** and **after** your change, with
the changed pixels highlighted — on macOS and Windows, in light and dark. If a
change turns out to alter nothing on current Firefox, the comment says that too,
which is worth knowing before anyone spends time reviewing it.

To get the same feedback while you work, without restarting Firefox after every
edit:

```bash
pipx install "fxcss[images]"   # no pipx? brew install pipx — plain pip hits PEP 668 on Homebrew/Debian Python
fxcss watch          # edit CSS and see it live, in a throwaway profile
fxcss pick           # click any part of the UI to get its CSS selector
```

`fxcss watch` never touches your real Firefox profile. `fxcss pick` also tells
you which files in this repo already style the element you clicked, which is
usually the fastest way to find where a rule belongs. See
[AdamXweb/fxcss](https://github.com/AdamXweb/fxcss) for the rest.

Two things that catch people out when theming Firefox:

- **On macOS, right-click menus are drawn by the OS**, so the `menupopup` rules
  in `parts/popups.css` have no effect there. They do apply on Windows and
  Linux. `fxcss watch --native-menus=false` switches Firefox to themeable menus
  if you need to work on them from a Mac.
- **Selectors change between Firefox releases.** `fxcss inspect '#some-id'` will
  tell you when a rule targets something that no longer exists.

## Screenshots

### Windows
![Preview](githubpreview/whitesurwindows.gif?raw=true)


### MacOS
![Preview](githubpreview/whitesur.gif?raw=true)
