#############################################
# Image Viewer
# Python 2.7, PIL, Tkinter
# lchsk.com
# 
# Todo:
#	+ searching images
#	- help screen
#	- resizing with set width
#	- using arrows/space
#   - recurisive search
#   - config file
#############################################

import Tkinter 
import Image, ImageTk
import os
import sys
import random
import subprocess
import re

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
		self._output = subprocess.Popen('xrandr | grep " connected [0-9x+]*" | cut -d " " -f3',shell=True, stdout=subprocess.PIPE).communicate()[0]
		self.screens = []
		for res in self._output.split():
			self._current = []
			self._t = re.findall('([0-9]+)', res)
			self._current.append(int(self._t[2]))
			self._current.append(int(self._t[3]))
			self._current.append(int(self._t[0]))
			self._current.append(int(self._t[1]))	
			self.screens.append(self._current)
	
		self.screens = sorted(self.screens, key=lambda s: s[0])
		self.screens_count = len(self.screens)
		#print self.screens
		# list of screens
		# pos_x, pos_y, width, height
		#return self.screens

class Input(object):
	def __init__(self):
		self.definition = []
		self.definition.append({ 'param_name' : 'recursive', 'short_name' : 'r', 'long_name' : 'recursive', 'type' : 'bool', 'default' : 'true'})
		self.definition.append({ 'param_name' : 'randomize', 'short_name' : 'rand', 'long_name' : 'random', 'type' : 'bool', 'default' : 'true'})
		self.definition.append({ 'param_name' : 'start', 'short_name' : 's', 'long_name' : 'start', 'type' : 'string', 'default' : './'})
		self.definition.append({ 'param_name' : 'search', 'short_name' : 'se', 'long_name' : 'search', 'type' : 'string', 'default' : ''})
		self.definition.append({ 'param_name' : 'timeout', 'short_name' : 't', 'long_name' : 'timeout', 'type' : 'int', 'default' : '1000'})
		self.definition.append({ 'param_name' : 'resize', 'short_name' : 'res', 'long_name' : 'resize', 'type' : 'string', 'default' : 'yes', 'values' : ['no', 'yes', 'always']})

		self.options = {}
		self.set_default_values()

		self.args = sys.argv[1:]
		#print self.args
		for argument in self.args:
			self._single_argument = argument.split('=')
			
			self.get_options_item(self._single_argument)
			#if self._single_argument[1:] in self.definition:
				

	def get_options_item(self, p_arg):
		for item in self.definition:
			if p_arg[0][1:] == item['short_name'] or p_arg[0][2:] == item['long_name']:
				pass
				if item['type'] == 'bool':
					self.options[item['param_name']] = True if p_arg[1] == 'true' else False
				elif item['type'] == 'int':
					self.options[item['param_name']] = int(p_arg[1])
				else:
					self.options[item['param_name']] = p_arg[1]
				#print 'zn' + item['param_name']

	def set_default_values(self):
		for i in self.definition:
			if i['type'] == 'bool':
				self.options[i['param_name']] = True if i['default'] == 'true' else False
			elif i['type'] == 'int':
				self.options[i['param_name']] = int(i['default'])	
			else:
				self.options[i['param_name']] = i['default']
		#print self.options

class Library(object):
	def __init__(self, p_start_dir, p_recursive, p_randomize, p_search_string):
		self.current_id = 1;
		self.randomize = p_randomize
		self.recursive = p_recursive
		self.search_string = p_search_string
		self.startdir = p_start_dir
		self.dirlist = []
		self.get_dirlist()
		
	def get_dirlist(self):
		if self.recursive:
			for dirname, dirnames, filenames in os.walk(self.startdir):
				# print path to all subdirectories first.
				#for subdirname in dirnames:
					#print os.path.join(dirname, subdirname)

				# print path to all filenames.
				for filename in filenames:
					self.dirlist.append(os.path.join(dirname, filename))			
					#print os.path.join(dirname, filename)
		else:
			self.dirlist = os.listdir(self.startdir)
			self.dirlist = [self.startdir + x for x in self.dirlist]
		
		# search
		if len(self.search_string) > 0:
			self._dirlist_copy = self.dirlist
			self.dirlist = []
			for item in self._dirlist_copy:
				if self.search_string in os.path.basename(item).lower():
					self.dirlist.append(item)
	
		self.count = len(self.dirlist)
		print 'Found ' + str(self.count) + ' images.'			

	def get_next_filename(self):
		if self.randomize:
			self.current_id = random.randint(0, self.count - 1)
		else:
			self.current_id = self.current_id + 1
		if self.current_id >= self.count:
			return None
	
		return self.dirlist[self.current_id]
 
class Viewer(object):
	def __init__(self):
		self.input = Input()
		self.screen = UbuntuScreen()
		self.library = Library(self.input.options['start'], self.input.options['recursive'], self.input.options['randomize'], self.input.options['search'])

		self.w = Tkinter.Tk()
		self.w.geometry('+%d+%d' % (0, 0))
		self.label = Tkinter.Label(self.w)	
		self.label.pack()
		self.w.after(0, self.update_image)
		self.w.mainloop()	

	def update_image(self):
		self._current_filename = self.library.get_next_filename()
		self.screen.which_screen(self.w.winfo_x(), self.w.winfo_y())		

		# resize
		if self.input.options['resize'] == 'always':	
			self._img = Image.open(self._current_filename)
			self._img = self._img.resize((self._img.size[0] * (self.screen.current_screen[3] - 60) / self._img.size[1], self.screen.current_screen[3] - 60), Image.ANTIALIAS)
		elif self.input.options['resize'] == 'yes':	
			self._img = Image.open(self._current_filename)
			if self._img.size[1] < self.screen.current_screen[3]:
				pass
			else:
				self._img = self._img.resize((self._img.size[0] * (self.screen.current_screen[3] - 60) / self._img.size[1], self.screen.current_screen[3] - 60), Image.ANTIALIAS)
		else:
			self._img = Image.open(self._current_filename)


		self.tkimg1 = ImageTk.PhotoImage(self._img)
		#self.label.place(x = 0, y = 0, width=self._img.size[0], height=self._img.size[1])
		self.label.config(image = self.tkimg1)
		#print self.w.geometry()
		#print self.w.winfo_x()
		
		self.w.title(os.path.basename(self._current_filename))
		self.label.after(self.input.options['timeout'], self.update_image)

if __name__ == '__main__':
	viewer = Viewer()
 
