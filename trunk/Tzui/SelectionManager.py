#from dbManager import dbManager
from Opioid2D import *
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
			pass
		else:
			self.newlist.append(object)
			object.do(Repeat(ColorFade((0.4,0.4,1), secs=1) + \
						ColorFade((0.55,0.55,1), secs=1)))

	def remove(self, object=None):
		if self.newlist.count(object) >= 1:
			self.newlist.remove(object)
			object.abort_actions(ColorFade)
			object.do(ColorFade((1,1,1),secs=0.2))
		else:
			pass
		
	def reset(self):
		'''Will someone please tell me why it doesn't remove everything
		on its first try?
		'''
		for object in self.newlist:
			self.remove(object)
		for object in self.newlist:
			self.remove(object)
		for object in self.newlist:
			self.remove(object)
		for object in self.newlist:
			self.remove(object)
		for object in self.newlist:
			self.remove(object)
		# don't forget to remove them from the db as well
	
	def list(self):
		return self.newlist