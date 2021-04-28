if [[ "${LIB_INSTALL_IMPORTED}" == "true" ]]; then
  echo "ERROR: lib-install.sh is already imported"; exit 1
else LIB_INSTALL_IMPORTED="true"; fi

source "${REPO_DIR}/lib-core.sh"

install_firefox_theme() {
  remove_firefox_theme
  echo "${FIREFOX_O_HOME}"*"default-release"
    cp -rf "${REPO_DIR}/chrome"                                                           "${FIREFOX_DIR_HOME}/"*"default-release"

  config_firefox
  echo "Copy complete."
}

config_firefox() {
  killall "firefox" &> /dev/null
    cp -rf "${REPO_DIR}/configuration"                                                           "${FIREFOX_DIR_HOME}/"*"default-release"

  for d in "${FIREFOX_DIR_HOME}/"*"default-release"; do
    echo "user_pref(\"toolkit.legacyUserProfileCustomizations.stylesheets\", true);" >> "${d}/prefs.js"
    echo "user_pref(\"browser.tabs.drawInTitlebar\", true);" >>                         "${d}/prefs.js"
    echo "user_pref(\"browser.uidensity\", 0);" >>                                      "${d}/prefs.js"
    echo "user_pref(\"layers.acceleration.force-enabled\", true);" >>                   "${d}/prefs.js"
    echo "user_pref(\"mozilla.widget.use-argb-visuals\", true);" >>                     "${d}/prefs.js"
  done
}

remove_firefox_theme() {
  rm -rf "${FIREFOX_DIR_HOME}/"*"default"*"/chrome"
}