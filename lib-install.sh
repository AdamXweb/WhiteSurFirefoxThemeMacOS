if [[ "${LIB_INSTALL_IMPORTED}" == "true" ]]; then
  echo "ERROR: lib-install.sh is already imported"; exit 1
else LIB_INSTALL_IMPORTED="true"; fi

source "${REPO_DIR}/lib-core.sh"

# Files/dirs this theme writes into a profile's chrome/ directory. Only these
# may be deleted -- anything else in chrome/ belongs to the user.
FIREFOX_THEME_PATHS=("WhiteSur" "userChrome.css" "userContent.css")

remove_firefox_theme() {
  killall "firefox" &> /dev/null
  # Scoped to PROFILE_GLOB (the profiles we install to) and to theme-owned
  # paths. The old "*default*/chrome" wipe also hit dev-edition and ESR
  # profiles and destroyed userChrome.css files this theme never wrote.
  for d in "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}; do
    [[ -d "${d}/chrome" ]] || continue
    for p in "${FIREFOX_THEME_PATHS[@]}"; do
      rm -rf "${d}/chrome/${p}"
    done
    # Drop chrome/ only if the theme was all that was in it.
    rmdir "${d}/chrome" 2> /dev/null || true
  done
}

install_firefox_theme() {
  remove_firefox_theme
  echo "${FIREFOX_O_HOME}"*"default-release"
  LOC=`echo "${FIREFOX_O_HOME}"*"default-release"`
  cp -rf "${REPO_DIR}/chrome"                                      "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}
  config_firefox
  echo "Copy complete."
}

config_firefox() {
    cp -rf "${REPO_DIR}/configuration"                             "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}
# If LeftHandSide Tab close button is wanted
if [ "$TABSWAP" = true ] ; then
  cd "${REPO_DIR}"
	echo "Enabling Tab close button on Left hand side"
      cp -rf "${REPO_DIR}/custom/tabs-swapclose.css"                     "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}"/chrome/WhiteSur/custom"
  echo "Tab close position swapped"
fi
# If LeftHandSide Window close button is wanted
if [ "$WINDOWSWAP" = true ] ; then
  cd "${REPO_DIR}"
	echo "Enabling Tab close button on Left hand side"
      cp -rf "${REPO_DIR}/custom/windows-swapclose.css"                     "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}"/chrome/WhiteSur/custom"
  echo "Window CSD swapped"
fi
# if compact tabs are wanted
if [ "$COMPACTTAB" = true ] ; then
  cd "${REPO_DIR}"
  echo "Enabling Tab close button on Left hand side"
      cp -rf "${REPO_DIR}/custom/compact-tabs.css"                     "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}"/chrome/WhiteSur/custom"
  echo "Tabs are compact"
fi
# if no animation on URL bar is desired
if [ "$URLBAR" = true ] ; then
	echo "Removing URL bar animation"
    cd "${REPO_DIR}"
      cp -rf "${REPO_DIR}/custom/standard-urlbar.css"              "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}"/chrome/WhiteSur/custom"
  echo "Standard URL bar configured"
fi
# if no identity line icon is wanted
if [ "$NOLINE" = true ] ; then
	echo "Removing Facebook / Multi account Identity line"
    cd "${REPO_DIR}"
      cp -rf "${REPO_DIR}/custom/noidentity.css"              "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}"/chrome/WhiteSur/custom"
  echo "No identity lines configured"
fi
if [ "$TABVIEW" = true ] ; then
  cd "${REPO_DIR}"
	echo "Re-enabling tab view button"
      cp -rf "${REPO_DIR}/custom/enabletabview.css"                     "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}"/chrome/WhiteSur/custom"
  echo "Tab view button enabled"
fi
# If the extension panen is to be hidden
if [ "$HIDEEXTENSION" = true ] ; then
  cd "${REPO_DIR}"
	echo "Enabling hidden extension button"
      cp -rf "${REPO_DIR}/custom/hideextension.css"                     "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}"/chrome/WhiteSur/custom"
  echo "Extension button hidden"
fi
if [ "$NOTABSINGLE" = true ] ; then
  cd "${REPO_DIR}"
	echo "Enabling single tab minimal view"
      cp -rf "${REPO_DIR}/custom/singletabhidden.css"                     "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}"/chrome/WhiteSur/custom"
  echo "Single tab minimal view enabled"
fi
# If a colour theme is wanted (-t <name>, e.g. -t dracula)
if [ -n "$COLOURTHEME" ] ; then
  cd "${REPO_DIR}"
  if [ -f "${REPO_DIR}/custom/theme-${COLOURTHEME}.css" ] ; then
	echo "Enabling ${COLOURTHEME} colour theme"
      cp -rf "${REPO_DIR}/custom/theme-${COLOURTHEME}.css"                "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}"/chrome/WhiteSur/custom"
  echo "${COLOURTHEME} colour theme configured"
  else
    echo "Unknown colour theme: ${COLOURTHEME}. Available themes:"
    for f in "${REPO_DIR}"/custom/theme-*.css; do
      basename "${f}" .css | sed 's/^theme-/    /'
    done
    exit 1
  fi
fi

# Copy settings to enable stylesheets in firefox automatically.
  for d in "${FIREFOX_DIR_HOME}/"${PROFILE_GLOB}; do
    echo "user_pref(\"toolkit.legacyUserProfileCustomizations.stylesheets\", true);" >> "${d}/prefs.js"
    echo "user_pref(\"browser.tabs.drawInTitlebar\", true);" >>                         "${d}/prefs.js"
    echo "user_pref(\"browser.uidensity\", 0);" >>                                      "${d}/prefs.js"
    echo "user_pref(\"layers.acceleration.force-enabled\", true);" >>                   "${d}/prefs.js"
    echo "user_pref(\"mozilla.widget.use-argb-visuals\", true);" >>                     "${d}/prefs.js"
  done
}

