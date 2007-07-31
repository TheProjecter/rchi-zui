##---------------
# Design based on Jef Raskin's ZoomWorld.
# Built by Corey Birnbaum using the Opioid2D
# framework (which is under development by Sami
# Hangaslammi).
#
# Corey's site: ColdConstructs.com
#
# Tzui development site: code.google.com/p/rchi-zui/
# Tzui Google group: groups.google.com/group/rchi-zui
#
##---------------


from Opioid2D import *
from ImageObject import ImageObject
from random import random
import pygame
import threading
import Queue
from DropBox import RunDropApp, MyFileDropTarget
import sys
import os
from SelectionManager import SelectionManager
#from dbManager import dbManager


class ZoomCheck:
    def __init__(self):
        self.zooming = False
        self.zoomLevel = 0
        
    def makeTrue(self):
        self.zooming = True
        pygame.mouse.set_visible(0)

    def makeFalse(self):
        self.zooming = False
        pygame.mouse.set_visible(1)
        
    def check(self):
        return self.zooming

    def increase(self):
        self.zoomLevel += 1

    def decrease(self):
        self.zoomLevel -= 1

    def level(self):
        return self.zoomLevel

class Orb(Sprite):
    image = "ui_images/orb.png"
    layer = "PrimOverlay"
    group = "cursor"
class InfoIconZoomIn1(Sprite):
    image = "ui_images/zoom_in1.png"
    layer = "PrimOverlay"
    group = "cursor"
class InfoIconZoomIn2(Sprite):
    image = "ui_images/zoom_in2.png"
    layer = "PrimOverlay"
    group = "cursor"
class InfoIconZoomIn3(Sprite):
    image = "ui_images/zoom_in3.png"
    layer = "PrimOverlay"
    group = "cursor"
class InfoIconZoomIn4(Sprite):
    image = "ui_images/zoom_in4.png"
    layer = "PrimOverlay"
    group = "cursor"
class InfoIconZoomOut1(Sprite):
    image = "ui_images/zoom_out1.png"
    layer = "PrimOverlay"
    group = "cursor"
class InfoIconZoomOut2(Sprite):
    image = "ui_images/zoom_out2.png"
    layer = "PrimOverlay"
    group = "cursor"
class InfoIconZoomOut3(Sprite):
    image = "ui_images/zoom_out3.png"
    layer = "PrimOverlay"
    group = "cursor"
class InfoIconZoomOut4(Sprite):
    image = "ui_images/zoom_out4.png"
    layer = "PrimOverlay"
    group = "cursor"

class CommandOverlay(Sprite):
    image = "ui_images/fake_com.png"
    layer = "SecOverlay"

class Compass(Sprite):
    image = "ui_images/zoom_in4.png"
    layer = "SecOverlay"

#class MouseHook(Sprite):
#    image = "ui_images/test.png"
#    layer = "SecOverlay"


zControl = ZoomCheck()
mmbdown = 0,0
camPanSpeed = 0

## Please see Opioid2D's documentation to understand
## what's going on in this class.
# http://opioid-interactive.com/opioid2d/?page=DocIndex

class Tzui(Scene):
    layers = [
        "bg",
        "canvas0",
        "TriOverlay",
        "SecOverlay",
        "PrimOverlay",
        ]
    
    @classmethod
    def set_queue(cls, q):
        cls.queue = q
    
    def enter(self):
        ResourceManager.preload_images("ui_images/*.png")
        ResourceManager.preload_images("images/*.*")
        Display.set_clear_color([0.3,0.3,0.3])
#        Sprite("bg.jpg").set(
#            layer = "bg",
#            position = (512,384),
#            )
#        self.get_layer("bg").ignore_camera = True
        self.get_layer("TriOverlay").ignore_camera = True
        self.get_layer("PrimOverlay").ignore_camera = True
        self.get_layer("SecOverlay").ignore_camera = True

        zoomIcon = mouseHook = Orb()
        zoomIcon.set(alpha=0)
        self.zoomIcon = zoomIcon
        mouseHook.set(alpha=0)
        self.mouseHook = mouseHook
        
        # Welcome image
        ImageObject("ui_images/welcome.png",512,384)
        
        co = CommandOverlay()
        co.set(position = (512,60), alpha=0)
        self.co = co
        
        cam = self.camera

        compass = Compass()
        compass.set(position = cam.get_position(), alpha=0)
        self.compass = compass
        compass.do(KeepFacing(self.mouseHook))
        
        self.SelMan = SelectionManager()
#        db = dbManager()
        
        ## Using this until I hook up a database to the DropBox.
        # Also note that the DropBox coordinates don't match
        # a moved camera. Will fix this later...
        tzuiFolder = sys.path[0] + '\\images\\'
        picsStuff = os.listdir(tzuiFolder)
        seriously = []
        for filename in picsStuff:
            seriously.append(tzuiFolder + filename)
        for path in seriously:
            ImageObject(path, 2000*random()-1000, 1000*random()-1000)
#            db.add(path, 2000*random()-1000, 1000*random()-1000)
        
        ## Variables for metamethods, which are silly things.
        mmb = 0 # If mmb is 1, the middle mouse button is pressed
        self.mmb = mmb
        rmb = 0 # And so on...
        self.rmb = rmb
        lmb = 0
        self.lmb = lmb
        mwu = 0 # mouse wheel up
        self.mwu = mwu
        mwd = 0
        self.mwd = mwd
        ctrl = 0 # either control keys
        self.ctrl = ctrl
        shift = 0 # either shift keys as well
        self.shift = shift

    def realtick(self):
        """This method runs 25 times a second."""
        key = Keyboard.is_pressed
        cam = self.camera
        self.zoomIcon.position = Mouse.position
        pos = self.get_layer("canvas0").convert_pos(*Mouse.position)
        self.pointerPosition = pos
        self.mouseHook.position = Mouse.position
        
        ## TODO
        # Change camera direction according to where
        # mmb was originally pressed (use "self.mOrigin")
        distance = ((cam.get_position() - pos).length)
        angle = self.compass.rotation

        if self.mmb:
            self.compass.do(AlphaFade(0.8, 0.1))
            cam.radial_velocity = angle,distance
        else:
            cam.radial_velocity = 0,0
            self.compass.do(AlphaFade(0, 0.2))

        if zControl.check():
            cam.radial_velocity = angle,distance

        # Just messing around :)
        if key(K_LALT):
            print "Future back leap!"
        else:
            pass
        if key(K_RALT):
            print "Future forward leap!"
        else:
            pass
        if key(K_c):
            self.co.do(AlphaFade(0.8, 0.2))
        else:
            self.co.do(AlphaFade(0, 0.2))
            
        ## Quasimode triggers
        if key(K_LCTRL) or key(K_RCTRL):
            self.ctrl = 1
        else:
            self.ctrl = 0
        if key(K_LSHIFT) or key(K_RSHIFT):
            self.shift = 1
        else:
            self.shift = 0

        ## Recepter for incoming objects via DropBox
        try:
            newObject = self.queue.get_nowait()
        except Queue.Empty:
            return
        else:
            n = ImageObject(newObject[0],newObject[1],newObject[2])
#            n.do(ScaleTo(cam.scale,0))
            print "Added", newObject[0], "at x", newObject[1], "y", newObject[2]
## Future versions will check type
#            if newObject[3] == "png" or "jpg" or "gif":
#                ImageObject(newObject[0],newObject[1],newObject[2])
#            elif newObject[3] == "txt":
#                TextObject(newObject[0],newObject[1],newObject[2])

    def handle_mousebuttondown(self, ev):
        sm = self.SelMan
        layer = self.get_layer("canvas0")
        x,y = layer.convert_pos(*Mouse.position)
        s = layer.pick(x,y)
        cam = self.camera
        key = Keyboard.is_pressed
        if ev.button == 1:
            self.lmb = 1
        if ev.button == 2:
            self.mmb = 1
        if ev.button == 3:
            self.rmb = 1
        if ev.button == 4:
            self.mwu = 1
        if ev.button == 5:
            self.mwd = 1
        targetObjectScale = 1 # Query db for object's scale that's at mpos
        ## Zoom controls
#        if self.rmb and not self.ctrl:  # Right mouse - center/scale cam
#            if s is not None:
#                cam.do(MoveTo(self.pointerPosition, 1))
#                cam.do(ScaleTo(s.scale, 1))
        if self.mwu and not self.ctrl:  # Scroll up - zoom in
            zControl.makeTrue()
            zControl.increase()
            if zControl.level() == 1:
                self.zoomIcon.do(Delete())
                self.zoomIcon = InfoIconZoomIn1()
            if zControl.level() == 2:
                self.zoomIcon.do(Delete())
                self.zoomIcon = InfoIconZoomIn2()
            if zControl.level() == 3:
                self.zoomIcon.do(Delete())
                self.zoomIcon = InfoIconZoomIn3()
            if zControl.level() > 3:
                self.zoomIcon.do(Delete())
                self.zoomIcon = InfoIconZoomIn4()
            cam.do(Scale(2))
        if self.mwd and not self.ctrl:  # Scroll down - zoom out
            zControl.makeTrue()
            zControl.decrease()
            if zControl.level() == -1:
                self.zoomIcon.do(Delete())
                self.zoomIcon = InfoIconZoomOut1()
            if zControl.level() == -2:
                self.zoomIcon.do(Delete())
                self.zoomIcon = InfoIconZoomOut2()
            if zControl.level() == -3:
                self.zoomIcon.do(Delete())
                self.zoomIcon = InfoIconZoomOut3()
            if zControl.level() < -3:
                self.zoomIcon.do(Delete())
                self.zoomIcon = InfoIconZoomOut4()
            cam.do(Scale(.5))
#        else:
#            pass
        if zControl.level() == 0:
            self.zoomIcon.do(Delete())
            zControl.makeFalse()
            self.zoomIcon = Orb()
            self.zoomIcon.set(alpha=0)

        ## Selection handling.
        # Pretty broken and unpredictable due
        # to some problems with ImageObject and/or perhaps O2D.
        if self.lmb and not self.shift and not self.ctrl:
            if s is not None:
                sm.add(s)
        else:
            pass
        if self.lmb and self.shift:
            if s is not None:
                sm.add(s)
            else:
                pass
        else:
            pass
        if self.lmb and self.shift and self.ctrl:
            sm.reset()
        if self.lmb and self.ctrl:
            if s is not None:
                sm.remove(s)
            else:
                pass
        else:
            pass
        if self.rmb and self.ctrl:
            if s is not None:
                s.draggable = True
                # All images CAN be dragged, but won't because they
                # need to be hit by the cursor explicitly. Something to
                # change for the next release.
                for everything in sm.list():
                    s.draggable = True
        else:
            if s is not None:
                s.draggable = False
        if self.mwu and self.ctrl:
            for everything in sm.list():
                everything.do(Scale(2))
        elif self.mwd and self.ctrl:
            for everything in sm.list():
                everything.do(Scale(0.5))
        else:
            for everything in sm.list():
                everything.abort_actions(Scale)

    def handle_mousebuttonup(self, ev):
        if ev.button == 1:
            self.lmb = 0
        if ev.button == 2:
            self.mmb = 0
        if ev.button == 3:
            self.rmb = 0
        if ev.button == 4:
            self.mwu = 0
        if ev.button == 5:
            self.mwd = 0

    def handle_keydown(self, ev):
        sm = self.SelMan
        if ev.key == K_ESCAPE:
            Director.quit()
        if ev.key == K_DELETE:
            for object in sm.list():
                object.do(Delete())
                sm.remove(object)
                print object, "was removed from the canvas."

# Wicked mad huge props to Sami Hangaslammi for the immense amount
# of help in getting the queue system to work, as well as the
# responsiveness and kindness he exhibited as I asked dumb questions
# and made countless requests for the O2D features that were necessary
# (and others that weren't) to get Tzui working on his framework.
    
def BeginThread():
   dropper = RunDropApp()
   dropper.setDaemon(True)
   dropper.start()

Display.init((800,600), (1024,768), title="Tzui preview1")
q = Queue.Queue()
Tzui.set_queue(q)
MyFileDropTarget.set_queue(q)
BeginThread()
Director.run(Tzui)

## I'm still learning how to program, so if you can write cleaner code
## that conforms to Python idioms, please help me out by doing so and
## sending me the changes. Visit the rchi-zui project (linked at top)
## and contact me there. Thanks!