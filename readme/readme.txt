plugin for CudaText.
it shows file-type-icons on UI tab headers. icons are loaded from themes, from subfolder
"data/filetypeicons". by default, preinstalled theme "vscode_16x16" is used, 
but you can use any other theme, after you install it in Addon Manager.
to set another theme, call menu item "Options / Settings-plugins / Tab Icons / Config",
in opened file plugins.ini find section [tab_icons], and change value of option there
to the name of subfolder in "data/filetypeicons".

for themes with bigger icon size (e.g. 24x24) you will need to adjust CudaText option
"ui_tab_size_y", to make UI tabs height bigger.

author: Alexey Torgashin (CudaText)
license: MIT