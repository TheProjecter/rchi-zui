"""
The SM is used as a bridge between the canvas object and
the database object. When the canvas object is clicked,
the db obj is called and added to a list. When something
happens to the canvas obj, the db obj is updated by way of
the command being applied to the db obj in the list.

In other words, when a command is run, it will grab the
list that the SM built and run the command on every object
in the list.

The SM sorts the list for the command system so that the
command is only run on the supported object type(s).

Of course, at the moment it's nothing.
"""

#from dbManager import dbManager
import os

class SelectionManager(object):
#	db = dbManager()
	def __init__(self):
		"""A new list is created each time it is instantiated.
		"""
		newlist = []
		self.newlist = newlist
		
	def add(self, object=None):
		if self.newlist.count(object) >= 1:
			self.remove(object)
			print object, "has been deselected."
		else:
			self.newlist.append(object)
			print object, "has been added to the selection list."

	def remove(self, object=None):
		if self.newlist.count(object) >= 1:
			self.newlist.remove(object)
			print object, "has been deselected."
		
	def reset(self):
		del self.newlist[:]
		print "Selection list cleared."
		
	def list(self):
		return self.newlist