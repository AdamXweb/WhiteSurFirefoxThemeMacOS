#! /bin/bash

readonly REPO_DIR="$(dirname "$(readlink "${0}")")"
source "${REPO_DIR}/lib-install.sh"

echo -en "$COL_GREEN WhiteSur Firefox theme. $COL_RESET"
echo -en "\n"
echo -en "\n"
echo -e "${bold}WhiteSur installer"
echo -e "⚠ This is a script to add the theme into firefox, and enable it."
echo -en "\n"
warn "=> ${bold}$COL_RED CTRL+C $COL_RESET now to abort ${normal} or ${bold} $COL_GREEN ENTER ${normal} $COL_RESET to continue."

tput bel
read -n 1


    actioninfo "Removing Firefox theme..."
    remove_firefox_theme
    success "Done!  Firefox theme has been removed."

# Install Firefox

    actioninfo "Installing WhiteSur Firefox theme to your directory below"
    install_firefox_theme
    success "Done! WhiteSur Firefox theme has been installed."



    actioninfo "Editing WhiteSur Firefox theme preferences..."
    edit_firefox_theme_prefs
    success "Done! Firefox theme preferences has been edited."


    echo
    warn "Please now go to: about:config in Firefox"
    warn "Search for `toolkit.legacyUserProfileCustomizations.stylesheets` and set it to `true`"
    actioninfo "That's it, restart Firefox and you're all set!"

echo