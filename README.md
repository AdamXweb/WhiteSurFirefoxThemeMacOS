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

On Linux, [vinceliuice/WhiteSur-firefox-theme](https://github.com/vinceliuice/WhiteSur-firefox-theme) — the upstream this theme is adapted from — integrates with GTK properly and is usually the better pick. fxcss will happily install this theme on Linux too, if the macOS look is what you want.

## Try it without installing

To see the theme before it goes anywhere near your own Firefox profile:

```bash
pipx install "fxcss[images]"     # no pipx? see pipx.pypa.io (brew install pipx on macOS)
fxcss try AdamXweb/WhiteSurFirefoxThemeMacOS
```

That opens a throwaway Firefox with the theme applied and leaves your real
profile untouched. Add `--dark` for dark mode, or
`--with compact-tabs,tabs-swapclose` to try the optional stylesheets described
below. Quit the browser and nothing is left behind.

## Installation

The default way, on macOS, Windows and Linux — [fxcss](https://github.com/AdamXweb/fxcss) 0.13 or newer:

```bash
pipx install "fxcss[images]"     # no pipx? see pipx.pypa.io (brew install pipx on macOS)
fxcss install AdamXweb/WhiteSurFirefoxThemeMacOS
```

It installs into the Firefox profile you actually use, found the same way Firefox finds it — on macOS, Windows and Linux alike, including snap and flatpak Firefoxes on Linux. A Firefox in an unusual place is reachable via `FXCSS_PROFILE_ROOTS`; when more than one installed Firefox has profiles, fxcss asks instead of guessing. Your existing `chrome/` folder is backed up first, and optional stylesheets from `custom/` load with `--with`, e.g. `--with compact-tabs,tabs-swapclose`. To put everything back the way it was:

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
- `-u` Remove the animation on URL bar to be clickable throughout
- `-n` Removes the identity colour from tabs
- `-v` Re-enables the tabview button
- `-e` Hides the extension button
- `-s` Single tab view (Tabs hidden when only one tab)
- `-r` Remove the theme

e.g. To install with script, with the tab close button left hand side: `bash install.sh -c` 

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
