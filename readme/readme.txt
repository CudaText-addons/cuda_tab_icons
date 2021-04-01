plugin for CudaText.
it shows file-type-icons on UI tab headers.
icons are loaded from theme, from subfolder "data/filetypeicons".
by default, preinstalled theme "vscode_16x16" is used, but you can use another
theme, after you install it in Addon Manager, see "filetypeicons" addon kind.


commands
--------
1) plugin adds menu item to UI-tab context menu: "Set tab icon...".
this sets custom document-specific icon, from several existing icons.
icons are searched in:
- plugin folder's subfolder,
- in [CudaText]/data/tabsicons.
icon size should be same as of the theme (option "icon_theme").

2) custom icons can be set/reset from the main menu "Plugins / Tab Icons".


configuration
-------------
call menu item "Options / Settings-plugins / Tab Icons / Config", config-file in
JSON format has options:

- "icon_theme": file-type icons, it's the name of subfolder in "data/filetypeicons".
  for themes with icon size >16x16 you need to adjust CudaText option "ui_tab_size_y".
- "show_lexer_icons" (bool): allows to show file-type icons per-lexer.
- "collapse_pinned" (bool): allows to auto-hide captions of "pinned" UI-tabs.
  needs CudaText 1.130+. only for UI-tabs which have custom icons assigned.


about
-----
authors:
  Alexey Torgashin (CudaText)
  Shovel, https://github.com/halfbrained
icons from:
  GNOME Adwaita, https://github.com/GNOME/adwaita-icon-theme
license: MIT
