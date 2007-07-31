# Mini wxApp for tzui.
# Used to introduce stuff from the filesystem to tzui so that you
# can play with them in the zoomable environment.
# Also handles the maintenance of the Axiom database as files
# are passed through it.

# If you can build something better (say, drag and drop directly
# into tzui) then please do and tell us about it :)

import wx
import os
from ImageObject import ImageObject
import Queue
import threading
#from dbManager import dbManager

SupportedObjects = ['.jpg', '.png', '.gif']
## TODO
# Keep unsupported types and just display them as an icon
# with their extension (e.g. "LXO") so that they can be
# tracked and organized within tzui--just not editable.
# Need Archy for this.


class MyFileDropTarget(wx.FileDropTarget):
	"""The class that tells tzui what was dropped and stuff."""
	
	def __init__(self, parent):
		"""Tell the system that this frame is a Drop Target(tm)."""
		wx.FileDropTarget.__init__(self)
		self.parent = parent

	@classmethod
	def set_queue(cls, q):
		cls.queue = q
	
#	db = dbManager()

	def OnDropFiles(self, x, y, files):
		"""When a file is dropped, it registers the file in tzui's
		datadbase where tzui will detect its presence and place it
		on the canvas at a position relative to where it was dropped
		in the wxFrame."""
		print "NOTE: All filetypes will be supported one way or another in future releases."
		print "Currently supported filetypes:"
		print SupportedObjects
		print "-----"
		for file in files:
			fileName = os.path.split(file)[1]
			newX = x * 4 # Convert coordinates to fit Tzui's virtual screen
			newY = y * 4
			if not os.path.splitext(fileName)[1] in SupportedObjects:
				files.remove(file)
				print "The file '" + fileName + "' is currently an unsupported type, so it was ignored."
#			self.db.stepOne(file, newX, newY)
			# Add the file's info into a list and put the list into the queue
			# where Tzui will grab them and paint them onto the canvas
			newObject = [file, newX, newY]
			self.queue.put(newObject)
	
class DropFrame(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title,
						pos=(10, 10), size=(256, 192), style=wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER)
		## TODO
		# Disable maximize
		panel = wx.Panel(self)
		text = wx.StaticText(panel, -1,
		"Drop files into this window.\n\n"
		+ "Tzui will pick them up and place them \n    on the canvas.\n\n"
		+ "Where you drop them here\n    corresponds to where they'll be\n    dropped in tzui's window and\n    scaled accordingly.")
		text.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
		wx.EVT_MOTION(panel, self.onStartDrag)
		self.SetDropTarget(MyFileDropTarget(self))

	def onStartDrag(self, evt):
		"""We don't need to drag anything from the box, so method is skipped."""
#		if evt.Dragging():
#			data = wx.FileDataObject()
#			dropSource = wx.DropSource(self)
#			dropSource.SetData(data)
#			dropSource.DoDragDrop(0)
		evt.Skip()

class DropApp(wx.App):
	def OnInit(self):
		frame = DropFrame(None, "tzui drop box")
		frame.Show(True)
		return True

class RunDropApp(threading.Thread):
	def run(self):
		DropApp(0).MainLoop()