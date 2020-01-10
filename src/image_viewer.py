#!/usr/bin/env python3

try:
    import Tkinter
    tkinter = Tkinter
except ImportError:
    import tkinter

from PIL import Image, ImageTk
import os
import sys
import random
import subprocess
import re
import operator

pil_formats = ['bmp', 'jpg', 'jpeg', 'png', 'gif']

class Screen(object):
    def __init__(self):
        self.screens = []
        self.screens_count = 0
        self.current_screen = []
    def which_screen(self, p_pos_x, p_pos_y):
        for i, screen in enumerate(self.screens):
            if p_pos_x >= screen[0] and p_pos_x < (screen[0] + screen[2]):
                self.current_screen = screen
                return i

class UbuntuScreen(Screen):
        def __init__(self):
            super(UbuntuScreen, self).__init__()
            self._output = subprocess.Popen('xrandr | grep " connected [0-9x+]*"',shell=True, stdout=subprocess.PIPE).communicate()[0]

            lines = ''


            for k in str(self._output).split('\n'):
                if k != '':
                    lines = lines + k[6:]

            self.screens = []

            for res in lines.split():
                self._current = []
                self._t = re.findall('([0-9]+)', res)

                if len(self._t) == 4:
                    self._current.append(int(self._t[2]))
                    self._current.append(int(self._t[3]))
                    self._current.append(int(self._t[0]))
                    self._current.append(int(self._t[1]))
                    self.screens.append(self._current)

            print(self.screens)
            self.screens = sorted(self.screens, key=lambda s: s[0])
            self.screens_count = len(self.screens)

class Input(object):
    def __init__(self):
        self.definition = []
        self.definition.append({ 'param_name' : 'slideshow', 'short_name' : 'l', 'long_name' : 'slideshow', 'type' : 'bool', 'default' : 'false'})
        self.definition.append({ 'param_name' : 'recursive', 'short_name' : 'r', 'long_name' : 'recursive', 'type' : 'bool', 'default' : 'true'})
        self.definition.append({ 'param_name' : 'randomize', 'short_name' : 'rand', 'long_name' : 'random', 'type' : 'bool', 'default' : 'true'})
        self.definition.append({ 'param_name' : 'start', 'short_name' : 's', 'long_name' : 'start', 'type' : 'string', 'default' : './'})
        self.definition.append({ 'param_name' : 'search', 'short_name' : 'se', 'long_name' : 'search', 'type' : 'string', 'default' : ''})
        self.definition.append({ 'param_name' : 'timeout', 'short_name' : 't', 'long_name' : 'timeout', 'type' : 'int', 'default' : '2000'})
        self.definition.append({ 'param_name' : 'resize', 'short_name' : 'res', 'long_name' : 'resize', 'type' : 'string', 'default' : 'yes', 'values' : ['no', 'yes', 'always']})
        self.definition.append({ 'param_name' : 'help', 'short_name' : 'h', 'long_name' : 'help', 'type' : 'bool', 'default' : 'false'})
        self.definition.append({ 'param_name' : 'first', 'short_name' : 'f', 'long_name' : 'first', 'type' : 'int', 'default' : '0'})
        self.definition.append({ 'param_name' : 'verbose', 'short_name' : 'v', 'long_name' : 'verbose', 'type' : 'bool', 'default' : 'false'})

        self.options = {}
        self.set_default_values()

        self.args = sys.argv[1:]

        if len(self.args) == 0:
            self.help()
            sys.exit(0)

        if len(self.args) > 0:
            for argument in self.args:
                self._single_argument = argument.split('=')

                self.get_options_item(self._single_argument)

                if self.options['help']:
                    self.help()
                    sys.exit()

    def get_options_item(self, p_arg):
        for item in self.definition:
            if p_arg[0][1:] == item['short_name'] or p_arg[0][2:] == item['long_name']:
                if item['type'] == 'bool':
                    self.options[item['param_name']] = True if p_arg[1] == 'true' else False
                elif item['type'] == 'int':
                    self.options[item['param_name']] = int(p_arg[1])
                else:
                    self.options[item['param_name']] = p_arg[1]

    def help(self):
        print("usage:\n\tpython {0}".format(sys.argv[0]))

        for k in self.definition:
            print("--{0}\t-{1}\t{2}".format(k['long_name'], k['short_name'], k['default']))

    def set_default_values(self):
        for i in self.definition:
            if i['type'] == 'bool':
                self.options[i['param_name']] = True if i['default'] == 'true' else False
            elif i['type'] == 'int':
                self.options[i['param_name']] = int(i['default'])
            else:
                self.options[i['param_name']] = i['default']

class Library(object):
    def __init__(self, p_start_dir, p_recursive, p_randomize, p_search_string, p_first):
        self.first = p_first
        self.current_id = -1;
        self.randomize = p_randomize
        self.recursive = p_recursive
        self.search_string = p_search_string
        self.startdir = p_start_dir
        self.dirlist = []

        self.get_dirlist()
        self.direction = 1

    def get_dirlist(self):
        if self.recursive:
            for dirname, dirnames, filenames in os.walk(self.startdir):
                # print path to all filenames.
                for filename in filenames:
                    ext = (os.path.splitext(filename)[1])[1:].lower()

                    if ext in pil_formats:
                        self.dirlist.append(os.path.join(dirname, filename))
        else:
            self.dirlist = os.listdir(self.startdir)
            self.dirlist = [self.startdir + x for x in self.dirlist]

        # search
        if len(self.search_string) > 0:
            self._dirlist_copy = self.dirlist

            self.dirlist = [
                item
                for item in self._dirlist_copy
                if self.search_string.lower() in item.lower()
            ]

        # first N
        if self.first > 0:
            self._dirlist_copy = self.dirlist
            self.dirlist = []

            f_count = 0
            self.modtime = { f: os.stat(f).st_mtime for f in self._dirlist_copy}

            for t in sorted(self.modtime.items(), key=operator.itemgetter(1), reverse=True):
                self.dirlist.append(t[0])
                f_count = f_count + 1
                if f_count >= self.first:
                    break

        self.count = len(self.dirlist)
        print('Found ' + str(self.count) + ' images.')

        if self.count == 0:
            sys.exit(0)

        self.dirlist = sorted(self.dirlist)

    def be_safe(self):
        self.current_id = self.current_id % self.count

    def get_random_id(self):
        self.current_id = random.randint(0, self.count - 1)

    def get_next_filename(self):
        if self.randomize:
            # self.current_id = random.randint(0, self.count - 1)
            self.get_random_id()
        else:
            self.current_id = self.current_id + self.direction

        self.be_safe()

        return self.dirlist[self.current_id]

class Viewer(object):
    def __init__(self):
        self.input = Input()
        self.screen = UbuntuScreen()
        self.library = Library(self.input.options['start'], self.input.options['recursive'], self.input.options['randomize'], self.input.options['search'], p_first=self.input.options['first'])

        self._img = None

        self.w = tkinter.Tk()

        self.w.bind("<Right>", self.next)
        self.w.bind("<Left>", self.previous)
        self.w.bind("<space>", self.random)

        self.w.geometry('+%d+%d' % (0, 0))
        self.label = tkinter.Label(self.w)
        self.label.pack()
        self.w.after(0, self.update_image)
        self.w.mainloop()

    def next(self, event):
        self.library.direction = 1
        self.update_image()

    def previous(self, event):
        self.library.direction = -1
        self.update_image()

    def random(self, event):
        self.library.get_random_id()
        self.update_image()

    def _open_image(self):
        try:
            self._img = Image.open(self._current_filename)

            if self.input.options['verbose']:
                print('%s %s' % (self._current_filename, self._img.size))
        except OSError as e:
            self._img = None
            print('Could not open %s %s' % (self._current_filename, e))

    def _resize_image(self):
        width = int(self._img.size[0] * (self.screen.current_screen[3] - 60) / self._img.size[1])
        height = int(self.screen.current_screen[3] - 60)

        try:
            self._img = self._img.resize((width, height), Image.ANTIALIAS)
        except OSError as e:
            print('Could not resize: %s' % e)

    def update_image(self):
        self._current_filename = self.library.get_next_filename()
        self.screen.which_screen(self.w.winfo_x(), self.w.winfo_y())

        self._open_image()

        if not self._img:
            self.label.after(0, self.update_image)
            return

        # resize
        if self.input.options['resize'] == 'always':
            self._resize_image()
        elif self.input.options['resize'] == 'yes':
            if self._img.size[1] > self.screen.current_screen[3]:
                self._resize_image()

        assert self._img

        try:
            self.tkimg1 = ImageTk.PhotoImage(self._img)
        except OSError as e:
            print('Coulnt not open %s %s' % (self._current_filename, e))
            return

        self.label.config(image = self.tkimg1)

        self.w.title(os.path.basename(self._current_filename))

        if self.input.options['slideshow']:
            self.label.after(self.input.options['timeout'], self.update_image)

if __name__ == '__main__':
    try:
        viewer = Viewer()
    except KeyboardInterrupt:
        print('Quitting')
