import os
import re
import json
from cudatext import *

fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_tab_icons.json')
icons_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'misc_icons')

USER_DIR = os.path.expanduser('~')

def collapse_path(path):
    if (path + os.sep).startswith(USER_DIR + os.sep):
        path = path.replace(USER_DIR, '~', 1)
    return path

class Command:
    def __init__(self):

        self.icon_theme = 'vscode_16x16'
        self.show_lex_icons = True
        
        self.misc_icon_map = {} # path -> icon name
        self.imglist = app_proc(PROC_GET_TAB_IMAGELIST, '')
        
        self.load_options()

        try:
            nsize = int(re.match('^\w+x(\d+)$', self.icon_theme).group(1))
            imagelist_proc(self.imglist, IMAGELIST_SET_SIZE, (nsize, nsize))
        except:
            print('Tab Icons: incorrect theme name, must be nnnn_NNxNN:', self.icon_theme)

        self.icon_dir = os.path.join(app_path(APP_DIR_DATA), 'filetypeicons', self.icon_theme)
        if not os.path.isdir(self.icon_dir):
            self.icon_dir = os.path.join(app_path(APP_DIR_DATA), 'filetypeicons', 'vscode_16x16')

        if self.icon_theme!='vscode_16x16':
            print('Tab Icons: using theme '+self.icon_theme)

        self.icon_json = os.path.join(self.icon_dir, 'icons.json')
        self.icon_json_dict = json.loads(open(self.icon_json).read())
        self.icon_indexes = {}
        self.misc_icon_indexes = {}
        
        menu_proc('tab', MENU_ADD, command='cuda_tab_icons.iconify_current', caption='Set tab icon...')


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
        n = self.icon_load(fn, icon_def, key, self.icon_indexes)
        return n


    def icon_get_misc(self, ic_name):
        
        if ic_name not in self.misc_icon_indexes:
            # allow absolute path to icon in config, "advanced feature"
            ic_path = os.path.join(icons_path, ic_name)  if os.sep not in ic_name else  ic_name 
            self.icon_load(ic_path, -1, ic_name, self.misc_icon_indexes)
      
        return self.misc_icon_indexes[ic_name]
        
    def icon_load(self, ic_path, icon_def, key, cache):
        
        n = imagelist_proc(self.imglist, IMAGELIST_ADD, value=ic_path)
        if n is None:
            print('Incorrect filetype icon:', ic_path)
            n = icon_def
        cache[key] = n
        return n


    def update_icon(self, ed_self, is_picture):

        filename = ed_self.get_filename()
        icon = -1
        lexer = None
        if is_picture:
            lexer = '_img'
        elif filename and filename in self.misc_icon_map:
            ic_name = self.misc_icon_map[filename]
            icon = self.icon_get_misc(ic_name)
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

        self.update_icon(ed_self, False)

    def iconify_current(self):
        
        path = ed.get_filename()
        if path:
            ic_fns = [name for name in os.listdir(icons_path)  if name.lower().endswith('.png')]
            ic_fns.sort(key=lambda n: icon_aliases.get(n, n))
            ic_names_aliased = [icon_aliases.get(name, name) for name in ic_fns]
            ic_names_noext = [os.path.splitext(name)[0] for name in ic_names_aliased] # no exts
            
            doc_fn = os.path.basename(path)
            ic_ind = dlg_menu(DMENU_LIST, ic_names_noext, caption='Choose icon for:\n  '+doc_fn)
            
            if ic_ind is not None:
                ic_name = ic_fns[ic_ind]
                imind = self.icon_get_misc(ic_name)
                ed.set_prop(PROP_TAB_ICON, imind)
                
                self.misc_icon_map[path] = ic_name
                self.save_options()

    def clear_current(self):
        
        path = ed.get_filename()
        if path  and path in self.misc_icon_map:
            del self.misc_icon_map[path]
      
        ed.set_prop(PROP_TAB_ICON, -1)
        self.save_options()

    def config(self):

        self.save_options()

        file_open(fn_config)

    def save_options(self):
        
        collapsed = {collapse_path(path):ic_name for path,ic_name in self.misc_icon_map.items()}
        cfg = {
            'icon_theme': self.icon_theme,  
            'show_lex_icons': self.show_lex_icons,
            'custom_icons_map': collapsed,
        }
        
        with open(fn_config, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)

    def load_options(self):
        if os.path.exists(fn_config):
            with open(fn_config, 'r', encoding='utf-8') as f:
                j = json.load(f)
                
            self.icon_theme = j.get('icon_theme', self.icon_theme)
            self.show_lex_icons = j.get('show_lex_icons', self.show_lex_icons)
            
            mp = j.get('custom_icons_map', self.misc_icon_map)
            self.misc_icon_map = {os.path.expanduser(path):ic_name for path,ic_name in mp.items()}
        

icon_aliases = {
    'appointment-soon.png': 'clock',
    #'audio-headphones.png': '',
    #'audio-speakers.png': '',
    'avatar-default.png': 'avatar',
    'changes-prevent.png': 'lock',
    #'computer.png': '',
    #'drive-multidisk.png': '',
    'edit-delete.png': 'delete',
    'edit-find.png': 'search purple',
    'emblem-default.png': 'success',
    'emblem-downloads.png': 'download',
    'emblem-mail.png': 'mail',
    'emblem-readonly.png': 'lock2',
    'emblem-unreadable.png': 'X',
    'emblem-web.png': 'web',
    'help-faq.png': '???',
    #'input-dialpad.png': '',
    'input-tablet.png': 'edit',
    'mail-attachment.png': 'attachment',
    'media-playback-start.png': 'start',
    'media-playback-stop.png': 'stop',
    'network-vpn.png': 'lock3',
    'non-starred.png': 'star empty',
    'preferences-desktop-font.png': 'alphabet',
    'preferences-system-privacy.png': 'privacy',
    'preferences-system-sharing.png': 'sharing',
    'security-high.png': 'shield green',
    'security-low.png': 'shield yellow',
    'security-medium.png': 'shield grey',
    'software-update-available.png': 'orange thingy',
    'software-update-urgent.png': 'warning',
    'starred.png': 'star',
    'system-file-manager.png': 'storage',
    'system-search.png': 'search yellow',
    #'trophy-bronze.png': '',
    #'trophy-gold.png': '',
    #'trophy-silver.png': '',
    'zoom-in.png': 'plus',
    'zoom-out.png': 'minus',
}
