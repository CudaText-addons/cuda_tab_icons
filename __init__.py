import os
import re
import json
from cudatext import *
from cudax_lib import get_translation

_ = get_translation(__file__)  # I18N

PLUGIN_NAME = "Tab Icons"

fn_config = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_tab_icons.json')
icons_dirs = [
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'misc_icons'), # plugin dir
    os.path.join(app_path(APP_DIR_DATA), 'tabsicons'), # data/tabsicons  dir
]

USER_DIR = os.path.expanduser('~')

# path -> icon name
# must be global var, to allow to change it from other plugins
icon_map = {} 

def collapse_path(path):
    if (path + os.sep).startswith(USER_DIR + os.sep):
        path = path.replace(USER_DIR, '~', 1)
    return path

class Command:
    def __init__(self):

        self.icon_theme = 'vscode_16x16'
        self.show_lex_icons = True
        self.collapse_pinned = False

        self.imglist = app_proc(PROC_GET_TAB_IMAGELIST, '')

        self.load_options()

        try:
            nsize = int(re.match('^\w+x(\d+)$', self.icon_theme).group(1))
            imagelist_proc(self.imglist, IMAGELIST_SET_SIZE, (nsize, nsize))
        except:
            print(PLUGIN_NAME+_(': incorrect theme name, must be nnnn_NNxNN:'), self.icon_theme)

        self.icon_dir = os.path.join(app_path(APP_DIR_DATA), 'filetypeicons', self.icon_theme)
        if not os.path.isdir(self.icon_dir):
            self.icon_dir = os.path.join(app_path(APP_DIR_DATA), 'filetypeicons', 'vscode_16x16')

        if self.icon_theme!='vscode_16x16':
            print(PLUGIN_NAME+_(': using theme ')+self.icon_theme)

        self.icon_json = os.path.join(self.icon_dir, 'icons.json')
        self.icon_json_dict = json.loads(open(self.icon_json).read())
        self.icon_indexes = {}
        self.misc_icon_indexes = {}
        self.saved_ed_titles = {} # Editor handle -> original title

        ctx_name = _('Set tab icon...')
        menu_proc('tab', MENU_ADD, command='cuda_tab_icons.iconify_current', caption=ctx_name)


    def icon_get(self, key, icon_def):

        # support variations of JS lexer
        if 'JavaScript' in key:
            key = 'JavaScript'
        elif 'TypeScript' in key:
            key = 'TypeScript'

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
            if os.sep in ic_name:
                ic_path = ic_name
            else:
                for icons_dir in icons_dirs:
                    ic_path = os.path.join(icons_dir, ic_name)
                    if os.path.exists(ic_path):
                        break

            self.icon_load(ic_path, -1, ic_name, self.misc_icon_indexes)

        return self.misc_icon_indexes[ic_name]

    def icon_load(self, ic_path, icon_def, key, cache):

        n = imagelist_proc(self.imglist, IMAGELIST_ADD, value=ic_path)
        if n is None:
            print(PLUGIN_NAME+_(': Incorrect filetype icon:'), ic_path)
            n = icon_def
        cache[key] = n
        return n


    def update_icon(self, ed_self, is_picture):

        filename = ed_self.get_filename()
        icon = -1
        lexer = None
        if is_picture:
            lexer = '_img'
        # document has custom icon
        elif filename and filename in icon_map:
            ic_name = icon_map[filename]
            icon = self.icon_get_misc(ic_name)
        else:
            lexer = ed_self.get_prop(PROP_LEXER_FILE)
            #support lite lexers
            if lexer.endswith(' ^'):
                lexer = lexer[:-2]

        if self.show_lex_icons  and  lexer:
            icon = self.icon_get(lexer, icon)

        ed_self.set_prop(PROP_TAB_ICON, icon)

    def update_title(self, ed_self):
        """ Adds "modified" indicator (*) for tabs; returns original title when tab is unpinned.
            called only if .collapse_pinned == True
        """

        fn = ed_self.get_filename()
        if not fn:
            return

        h = ed_self.get_prop(PROP_HANDLE_SELF)
        pinned = ed_self.get_prop(PROP_TAB_PINNED)
        modified = ed_self.get_prop(PROP_MODIFIED)
        title = ed_self.get_prop(PROP_TAB_TITLE)

        if pinned  and  fn in icon_map: # collapse
            title_stripped = title[1:] if title.startswith('*') else title
            if title != '*'  and  title != '':
                self.saved_ed_titles[h] = title_stripped
                new_title = ''
            else: # already collapsed, updating 'modified'
                new_title = title_stripped
        else: # return title
            new_title = self.saved_ed_titles.get(h, os.path.basename(fn))

        if modified:
            new_title = '*' + new_title

        ed_self.set_prop(PROP_TAB_TITLE, new_title)


    def on_lexer(self, ed_self):

        self.update_icon(ed_self, False)

    def on_open(self, ed_self):

        self.update_icon(ed_self, False)

    def on_state_ed(self, ed_self, state):

        if not self.collapse_pinned:
            return # option not enabled

        # display 'modified' character for pinned & collapsed
        if state in [EDSTATE_MODIFIED, EDSTATE_PINNED]:
            if ed_self.get_filename() in icon_map: # has custom icon
                self.update_title(ed_self)

    def iconify_current(self):

        path = ed.get_filename()
        if path:
            # get list of (icon, folder)
            ic_fns = {} #  filename -> directory
            for icons_dir in icons_dirs:
                if os.path.exists(icons_dir):
                    d = {name:icons_dir  for name in os.listdir(icons_dir)
                                            if name.lower().endswith('.png')}
                    ic_fns.update(d)
            ic_fns = list(ic_fns.items())

            # sort by alias, remove extensions of no-aliased
            ic_fns.sort(key=lambda t: icon_aliases.get(t[0], t[0]))
            ic_aliased = [icon_aliases.get(t[0], t[0]) for t in ic_fns] # (name,dir)
            ic_names_noext = [os.path.splitext(name)[0] for name in ic_aliased] # no exts, just names

            # add reset item
            ic_names_noext.insert(0, _('(reset icon)'))

            doc_fn = os.path.basename(path)
            ic_ind = dlg_menu(DMENU_LIST, ic_names_noext, caption=_('Choose icon for: ')+doc_fn)

            if ic_ind is None: # canceled
                return

            if ic_ind == 0: # reset
                self.clear_current()
            else:
                ic_ind -= 1

                ic_name = ic_fns[ic_ind][0]
                imind = self.icon_get_misc(ic_name)
                ed.set_prop(PROP_TAB_ICON, imind)

                icon_map[path] = ic_name
                self.save_options()

                if self.collapse_pinned:
                    self.update_title(ed)


    def clear_current(self):

        path = ed.get_filename()
        if path  and path in icon_map:
            del icon_map[path]
            if self.collapse_pinned:
                self.update_title(ed)

        self.update_icon(ed, False)
        self.save_options()

    def config(self):

        self.save_options()

        file_open(fn_config)

    def save_options(self):

        collapsed = {collapse_path(path):ic_name for path,ic_name in icon_map.items()}
        cfg = {
            'icon_theme': self.icon_theme,
            'show_lexer_icons': self.show_lex_icons,
            'collapse_pinned': self.collapse_pinned,
            'custom_icons_map': collapsed,
        }

        with open(fn_config, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)

    def load_options(self):
        global icon_map
        if os.path.exists(fn_config):
            with open(fn_config, 'r', encoding='utf-8') as f:
                j = json.load(f)

            self.icon_theme = j.get('icon_theme', self.icon_theme)
            self.show_lex_icons = j.get('show_lexer_icons', self.show_lex_icons)
            self.collapse_pinned =  j.get('collapse_pinned', self.collapse_pinned)

            mp = j.get('custom_icons_map', icon_map)
            icon_map = {os.path.expanduser(path):ic_name for path,ic_name in mp.items()}

            # check if supported new api, disable usage if not
            if self.collapse_pinned:
                try:
                    EDSTATE_PINNED
                except NameError:
                    self.collapse_pinned = False
                    print('NOTE:', PLUGIN_NAME+_(': update CudaText to enable tab pinning'))

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
