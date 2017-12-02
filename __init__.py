import os
import re
import json
from cudatext import *

class Command:
    def __init__(self):

        self.imglist = app_proc(PROC_GET_TAB_IMAGELIST, '')
        self.icon_theme = 'vscode_16x16'

        #try:
        #    nsize = int(re.match('^\w+x(\d+)$', self.icon_theme).group(1))
        #    imagelist_proc(self.imglist, IMAGELIST_SET_SIZE, (nsize, nsize))
        #except:
        #    print('Incorrect theme name, must be nnnnnn_NNxNN:', self.icon_theme)

        self.icon_dir = os.path.join(app_path(APP_DIR_DATA), 'filetypeicons', self.icon_theme)
        if not os.path.isdir(self.icon_dir):
            self.icon_dir = os.path.join(app_path(APP_DIR_DATA), 'filetypeicons', 'vscode_16x16')

        self.icon_json = os.path.join(self.icon_dir, 'icons.json')
        self.icon_json_dict = json.loads(open(self.icon_json).read())
        self.icon_indexes = {}


    def icon_get(self, key, icon_def):

        s = self.icon_indexes.get(key, None)
        if s:
            return s

        fn = self.icon_json_dict.get(key, None)
        if fn is None:
            n = icon_def
            self.icon_indexes[key] = n
            return n

        fn = os.path.join(self.icon_dir, fn)
        n = imagelist_proc(self.imglist, IMAGELIST_ADD, value=fn)
        if n is None:
            print('Incorrect filetype icon:', fn)
            n = icon_def
        self.icon_indexes[key] = n
        return n


    def update_icon(self, ed_self, is_picture):

        icon = -1
        if is_picture:
            lexer = '_img'
        else:
            lexer = ed_self.get_prop(PROP_LEXER_FILE)
            #support lite lexers
            if lexer.endswith(' ^'):
                lexer = lexer[:-2]

        if lexer:
            icon = self.icon_get(lexer, icon)

        ed_self.set_prop(PROP_TAB_ICON, icon)


    def on_lexer(self, ed_self):

        self.update_icon(ed_self, False)

    def on_open(self, ed_self):

        #handle on_open only for pictures
        fn = ed_self.get_filename()
        if fn=='?':
            self.update_icon(ed_self, True)
