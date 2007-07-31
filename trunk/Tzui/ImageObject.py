from Opioid2D import *
#import pygame.mouse as mow
from SelectionManager import SelectionManager
#from axiom import store


class ImageObject(gui.GUISprite):
    """Each O2D sprite has a collision box. O2D uses it to detect which
    sprite was hit (eg clicked on), but we'll also use it to figure
    out which TzuiObject it is, just in case the user wants to move
    the sprite around the canvas, change the file itself, or whatever.
    All actions done to the sprite will be reflected in its db equivilant.
    object = TzuiObject(batabase) + ImageObject(canvas)
    object -> GUISprite -> Sprite -> Node -> NodeBase
    """
    def __init__(self, path, x, y):
        gui.GUISprite.__init__(self)
        self.image = path
        self.layer = "canvas0"
        self.position = x,y
        # Just in case we need something more than what guiSprite
        # can already do, we can fall back on O2D's collision function
        # ie def collision_cursor_zuiObject(self,cursor,zuiObject)...
        self.join_group("zuiObject")
        
    draggable = False
    selman = SelectionManager()

#    s = store.Store('tzui.axiom')

    def on_hover(self):
        pass
    
    def on_drag(self):
        # What happens during the drag
        pass
    
    def on_create(self):
        ## TODO
        # put a border around it (svg plzkthnx)
        pass
    
    def on_press(self):
        pass

    def on_release(self):
        pass

## on_lock doesn't actually exist yet
#    def on_lock(self)
#        self.unregister() # stop receiving GUI events

    def on_click(self):
        pass
        ## TODO
        #Change something visual to let the user know it's selected
        
    def on_drag_begin(self):
        pass

    def on_drag_end(self):
        ## TODO
        # Update the database with the object's new coordinates
        pass
