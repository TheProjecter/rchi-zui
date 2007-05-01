import wx
import wx.html
import urllib2
import os
import cStringIO
import sqlobject
import base64

# I wish i could make these quasimodal on various keys
# Tool constants:
NORMAL_TOOL = 0   #no modifiers
SCROLL_TOOL = 1   #shift
ZOOM_TOOL = 2     # ctrl.  Zoom in left, zoom out right.
TAG_TOOL = 3     # alt
DRAW_TOOL = 4    # alt and ctrl?  this sucks.  Draw left, erase right.

DEFAULT_WIDTH = 100

QUERY_LIMIT = 30

def figureOutTool( mouseEvent ):
    # Look at what modifier keys are down to see what
    # kind of tool we've got.
    if mouseEvent.AltDown() and mouseEvent.ControlDown():
        return DRAW_TOOL
    if mouseEvent.ShiftDown():
        return SCROLL_TOOL
    if mouseEvent.AltDown():
        return TAG_TOOL
    if mouseEvent.ControlDown():
        return ZOOM_TOOL

    return NORMAL_TOOL


class SingleImageRow( sqlobject.SQLObject ):
    # single big text field for tags
    tags = sqlobject.StringCol()
    rawData = sqlobject.StringCol()
    hits = sqlobject.IntCol()
    originalPathName = sqlobject.StringCol()
    name = sqlobject.StringCol()
    dataType = sqlobject.StringCol()
    series = sqlobject.ForeignKey( "ImageSeriesRow", default=None )


# Not yet used:    
class ImageSeriesRow( sqlobject.SQLObject ):
    tags = sqlobject.StringCol()
    originalPathName = sqlobject.StringCol()
    seriesName = sqlobject.StringCol()

class ZuiObject: # mixin class, do not instantiate
    # Expects members called _imageRow, SetSize(),
    # GetSize(), SetPosition(), and GetPosition()

    def __init__( self, imageRow ):
        self._imageRow = imageRow
        # Save memory and time by figuring out when we're actually
        # on the screen or not; subclasses can then release allocated
        # stuff or forego expensive scaling operations if they're not
        # actually onscreen.
        self._onScreen = True

    def getImageRow( self ):
        return self._imageRow

    def _amIOnScreen( self ):
        pos = self.GetPosition()
        size = self.GetSize()
        parentWindowSize = self.Parent.GetSize()
        if pos.x > parentWindowSize.x:
            return False
        if pos.x + size.x < 0:
            return False
        if pos.y > parentWindowSize.y:
            return False
        if pos.y + size.y < 0:
            return False
        return True
    
    def zoom( self, x, y, zoomFactor ):
        pos = self.GetPosition()
        diffX = pos.x - x
        diffY = pos.y - y
        pos.x = x + diffX * zoomFactor
        pos.y = y + diffY * zoomFactor
        self.SetPosition( pos )
        size = self.GetSize()
        size.x *= zoomFactor
        size.y *= zoomFactor
        # Don't allow zeroes:
        # TODO maybe store the True Size as a pair of floats, always calculate
        # from that, to avoid round-off error?
        if size.x == 0:
            size.x = 1
        if size.y == 0:
            size.y = 1
        self.SetSize( size )
        self.Refresh()

    def scroll( self, x, y ):
        pos = self.GetPosition()
        pos.x -= x
        pos.y -= y
        self.SetPosition( pos )
        self.Refresh()

    def saveChanges( self ):
        raise NotImplementedError

    def getNaturalSize( self ):
        raise NotImplementedError

    def SetSize( self ):
        raise NotImplementedError

    def leftMouseDown( self, event, tool ):
        pass

    def leftMouseUp( self, event, tool ):
        pass

    def rightMouseDown( self, event, tool ):
        pass

    def rightMouseUp( self, event, tool ):
        pass

    def mouseDrag( self, event, tool ):
        pass

    def mouseEventHandler( self, event ):
        if event.ButtonDClick():
            self.Parent.onDoubleClick( event )
            return
        
        toolType = figureOutTool( event )
        # subclasses can decide how to respond to normal tool and
        # tag tool:
        if toolType == TAG_TOOL and event.LeftUp():
            self.Parent.openTagEditField( self )
            return

        if event.Dragging():
            self.mouseDrag( event, toolType )
            return
                
        if toolType == NORMAL_TOOL or toolType == DRAW_TOOL:
            if event.LeftDown():
                self.leftMouseDown( event, toolType )
                return
            if event.LeftUp():
                self.leftMouseUp( event, toolType )
                return
            if event.RightDown():
                self.rightMouseDown( event, toolType )
                return
            if event.RightUp():
                self.rightMouseUp( event, toolType )
                return
        # Otherwise, this isn't a tool we care about, so pass
        # on to parent:
        # is there a less klunky way to pass event to parent?
        if event.LeftDown():
            self.Parent.leftMouseDown( event )
        if event.LeftUp():
            self.Parent.leftMouseUp( event )
        if event.RightUp():
            self.Parent.rightMouseUp( event )


class ZuiTextObject( wx.TextCtrl, ZuiObject ):
    MAX_LINE_LEN = 80
    PIXELS_PER_LINE = 20
    
    def __init__( self, parent, imageRow, id, point ):
        ZuiObject.__init__( self, imageRow )
        self.__text = self._imageRow.rawData
        self.__dirty = False
        self._calculateDimensions()
        wx.TextCtrl.__init__( self, parent, id, self.__text, point,
                              wx.Size( DEFAULT_WIDTH, DEFAULT_WIDTH ), style=wx.TE_MULTILINE )
        self.SetSize( wx.Size( DEFAULT_WIDTH, 0 ) )
        self.Bind( wx.EVT_KEY_UP, self.onEdit )
        self.Refresh()

    def _calculateDimensions( self ):
        lines = self.__text.split( "\n" )
        self.__numLines = len( lines )
        lineLengths = [ len( line ) for line in lines ]
        longestLineLength = max( lineLengths )
        if longestLineLength > self.MAX_LINE_LEN :
            self.__width = self.MAX_LINE_LEN
            self.__numLines += len( [l for l in lineLengths if l > self.MAX_LINE_LEN] )
        else:
            self.__width = longestLineLength

    def saveChanges( self ):
        if self.__dirty:
            self._imageRow.rawData = self.GetValue()

    def getNaturalSize( self ):
        return ( self.__width * self.PIXELS_PER_LINE,
                 self.__numLines * self.PIXELS_PER_LINE )
    
    def onEdit( self, event ):
        self.__text = self.GetValue()
        self.__dirty = True

    def leftMouseUp( self, event, tool ):
        # a click with normal tool puts in the insertion point,
        # so pass the event on to the superclass' handler.
        if tool == NORMAL_TOOL:
            event.Skip()
            #wx.TextCtrl.ProcessEvent( self, event )
            # print dir ( wx.TextCtrl )
            # TODO this is the wrong call, find out how to pass the
            # event on correctly...
            # wx.TextCtrl.OnMouseUp( self, event )


    def SetSize( self, dimensions ):
        # Ignores the y value of dimensions.  Uses the x value to
        # scale but keeps its own proportions.
        self._calculateDimensions()
        characterSize = float( dimensions.x ) / float( self.__width )
        y = int( characterSize * self.__numLines )
        if y < self.PIXELS_PER_LINE:
            y = self.PIXELS_PER_LINE
        wx.TextCtrl.SetSize( self, ( dimensions.x, y ) )

class ZuiWebObject( wx.html.HtmlWindow, ZuiObject ):
    # For now, these do NOT have imageRows associated with them,
    # because they are transient and don't go into the DB.
    
    def __init__( self, parent, id, point, imageRow, data ):
        ZuiObject.__init__( self, imageRow )
        wx.html.HtmlWindow.__init__( self, parent, id, point,
                                     size = wx.Size( DEFAULT_WIDTH, DEFAULT_WIDTH ) )
        if data:
            self.SetPage( data )

    def saveChanges( self ):
        pass
        
    @classmethod
    def fromUrl( cls, parent, id, point, url ):
        try:
            openUrl = urllib2.urlopen( url )
            data = openUrl.read()
        except urllib2.URLError:
            print "Can't open URL", url
            data = None
        return cls( parent, id, point, None, data )

    @classmethod
    def fromImageRow( cls, parent, id, point, imageRow ):
        return cls( parent, id, point, imageRow, imageRow.rawData )
        

    # TODO complete this class!!
    # TODO make the page load happen in a separate thread, display a wait icon
    # until that is done?

    # TODO tagging this webobject needs to make an ImageRow for it
    # TODO clicking with NORMAL_TOOL in this webobject needs to follow links
    # TODO the links should open in a new, adjacent webObject instead of in
    # this one.
        
class ZuiPictureObject( wx.StaticBitmap, ZuiObject ):
    def __init__( self, parent, imageRow, id, point ):
        ZuiObject.__init__( self, imageRow )
        self._dirty = False
        data = base64.b64decode( self._imageRow.rawData )
        stream = cStringIO.StringIO( data )
        self.image = wx.ImageFromStream( stream )
        self.normalX = self.image.GetWidth()
        self.normalY = self.image.GetHeight()
        self._thumbnail = self._getThumbnail()
        wx.StaticBitmap.__init__( self, parent, id, self._thumbnail, point,
                                  wx.Size( self._thumbnail.GetWidth(), self._thumbnail.GetHeight() ) )

    def _getThumbnail( self ):
        # scales to default width, whatever height
        self.scaleFactor = float( DEFAULT_WIDTH ) / float( self.normalX )
        scaledImage = self.image.Scale( self.normalX * self.scaleFactor,
                                        self.normalY * self.scaleFactor )
        return wx.BitmapFromImage( scaledImage )
        
    def _getScaledBitmap( self, dimensions ):
        # Save processor time: just use the thumbnail when I'm offscreen:
        if not self._amIOnScreen():
            return self._thumbnail
        self.scaleFactor = float( dimensions[0] ) / float( self.normalX )
        scaledImage = self.image.Scale( self.normalX * self.scaleFactor,
                                        self.normalY * self.scaleFactor )
        return wx.BitmapFromImage( scaledImage )

    def SetSize( self, dimensions ):
        # SetBitmap does SetSize as a side-effect, so we have to do SetSize
        # to the desired dimensions after doing SetBitmap.
        self.SetBitmap( self._getScaledBitmap( ( dimensions.x, dimensions.y ) ) )
        wx.StaticBitmap.SetSize( self, dimensions )

    def getNaturalSize( self ):
        return ( self.normalX, self.normalY )
    
    def saveChanges( self ):
        if self._dirty:
            # This is incorrect.  It saves stuff to db, sure, but it's unreadable
            # when it comes back out.
            bytes = self.image.GetData()
            self._imageRow.rawData = base64.b64encode( bytes )
            self._dirty = False

    def zoom( self, x, y, zoomFactor ):
        self.saveChanges() # note this is kind of a dumb place to call it
        previouslyOnScreen = self._amIOnScreen()
        ZuiObject.zoom( self, x, y, zoomFactor )
        if not previouslyOnScreen and self._amIOnScreen():
            # Don't be thumbnail anymore, when I come back on screen:
            self.SetSize( self.GetSize())
            self.Refresh()

    def scroll( self, x, y ):
        self.saveChanges() # note this is kind of a dumb place to call it!
        previouslyOnScreen = self._amIOnScreen()
        ZuiObject.scroll( self, x, y )
        if not previouslyOnScreen and self._amIOnScreen():
            # Don't be thumbnail anymore, when I come back on screen:
            self.SetSize( self.GetSize())
            self.Refresh()

    def mouseDrag( self, event, tool ):
        if tool == DRAW_TOOL:
            x = event.X / self.scaleFactor
            y = event.Y / self.scaleFactor
            if event.LeftIsDown():
                # Pencil = set pixels black.
                self.image.SetRGB( x, y, 0, 0, 0 )
            elif event.RightIsDown():
                # Eraser = set pixels white in 4-pixel block
                self.image.SetRGB( x, y, 255, 255, 255 )
                self.image.SetRGB( x, y+1, 255, 255, 255 )
                self.image.SetRGB( x+1, y, 255, 255, 255 )
                self.image.SetRGB( x+1, y+1, 255, 255, 255 )
            self.SetSize( self.GetSize())
            self.Refresh()
            self._dirty = True

class DirectorySnarfer:
    def __init__( self, directoryName ):
        self.__dirName = directoryName

        # connect to DB here:
        dbUrl = "sqlite:/zui.db"

        connection = sqlobject.connectionForURI( dbUrl )
        sqlobject.sqlhub.threadConnection = connection
        self._connection = connection
        
        # TODO run these if tables need creation.
        # SingleImageRow.createTable()
        # ImageSeriesRow.createTable()

        print "Untagged:", SingleImageRow.select( """tags == ''""" ).count()

    def snarf( self ):
        # TODO recursive snarfing (use os.walk)
        for imageFile in os.listdir( self.__dirName ):
            fullPath = os.path.join( self.__dirName, imageFile  )
            # detect duplicate filenames and don't snarf them:
            if SingleImageRow.selectBy( originalPathName = fullPath ).count() > 0:
                continue

            fileSuffix = (imageFile.split( "." )[-1]).lower()
            if fileSuffix in [ "jpg", "jpeg", "png", "gif" ]:
                data = open( fullPath, "rb" ).read()
                imageRow = SingleImageRow( tags = "",
                                           rawData = base64.b64encode( data ),
                                           hits = 0,
                                           originalPathName = fullPath,
                                           name = imageFile,
                                           dataType = "picture" )
                # Once it's in the DB, delete original file:
                # os.remove( fullPath )
            # Text files:
            if fileSuffix in [ "txt", "py" ]:
                data = open( fullPath, "r" ).read()
                imageRow = SingleImageRow( tags = "",
                                           rawData = data,
                                           hits = 0,
                                           originalPathName = fullPath,
                                           name = imageFile,
                                           dataType = "text" )
                # os.remove( fullPath )
            if fileSuffix in [ "html", "htm" ]:
                data = open( fullPath, "r" ).read()
                imageRow = SingleImageRow( tags = "",
                                           rawData = data,
                                           hits = 0,
                                           originalPathName = fullPath,
                                           name = imageFile,
                                           dataType = "web" )

class ZuiViewerFrame( wx.Frame ):
    def __init__( self, startDirectory ):
        wx.Frame.__init__( self, None, id = -1, size = (400, 300), name = "Bla!" )

        # TODO figure out how the frame or the panel or the application can get
        # key down / key up events.  Right now only the individual control that
        # has keyboard focus gets any key events, which is really and truly lame.
        
        ctrlPanel = wx.Panel( self, -1, wx.Point( 0, 0 ), wx.Size( 1024, 24 ))
        self._multiPanel = MultiImageViewerPanel( self, -1, startDirectory )

        self.searchBox = wx.TextCtrl( ctrlPanel, -1, "search here", wx.Point(30,0), wx.Size(250, 20))
        self.searchButton = wx.Button( ctrlPanel, 1, "Search", wx.Point(280, 0), wx.Size(40, 20 ))
        self.Bind( wx.EVT_BUTTON, self.onSearchButton, id=1 )
        self.untaggedButton = wx.Button( ctrlPanel, 2, "Untagged", wx.Point(320, 0), wx.Size(60, 20 ))
        self.Bind( wx.EVT_BUTTON, self.onUntaggedButton, id=2 )
        self.clearButton = wx.Button( ctrlPanel, 3, "Clear", wx.Point(380, 0), wx.Size(60, 20 ))
        self.Bind( wx.EVT_BUTTON, self.onClearButton, id=3 )
        self.everyButton = wx.Button( ctrlPanel, 4, "All", wx.Point(440, 0), wx.Size(60, 20 ))
        self.Bind( wx.EVT_BUTTON, self.onEverythingButton, id=4 )
        self.tagField = wx.TextCtrl( ctrlPanel, 5, "tags here", wx.Point(500,0), wx.Size(250, 20))
        self.tagField.Bind( wx.EVT_KEY_UP, self.onTagEdit, id=5 )
        self.tagField.Hide()

        self._multiPanel.doUntaggedQuery()
        
    def onSearchButton( self, event ):
        searchText = self.searchBox.GetValue()
        self._multiPanel.doSearchQuery( searchText )

    def onUntaggedButton( self, event ):
        self._multiPanel.doUntaggedQuery()

    def onEverythingButton( self, event ):
        self._multiPanel.doEverythingQuery()

    def onClearButton( self, event ):
        self._multiPanel.doClear()

    def onTagEdit( self, event ):
        self._multiPanel.onTagEdit( event )

    def showTagField( self, text ):
        self.tagField.SetValue( text )
        self.tagField.Show()

    def hideTagField( self ):
        self.tagField.Hide()

    def getTagFieldValue( self ):
        return self.tagField.GetValue()


class MultiImageViewerPanel( wx.Panel ):
    def __init__( self, parent, id, directoryName ):
        wx.Panel.__init__( self, parent, id, wx.Point(0,24), wx.Size(1024, 800))
        self.__directorySnarfer = DirectorySnarfer( directoryName )

        self.__directorySnarfer.snarf()
        self.__zuiObjects = []
        self._tagFieldDirty = False
        self.__objectBeingTagged = None
        
        self.Bind( wx.EVT_LEFT_DOWN, self.leftMouseDown )
        self.Bind( wx.EVT_LEFT_UP, self.leftMouseUp )
        self.Bind( wx.EVT_RIGHT_UP, self.rightMouseUp )


    def doClear( self ):
        # clear out old stuff:
        self.finishTagField()
        self.latestQueryResults = None
        for obj in self.__zuiObjects:
            obj.Destroy()
        self.__zuiObjects = []
        
    def _display( self, queryResults, addGoogleSearch = False ):
        self.latestQueryResults = queryResults # so we can come back to it later
        spacing = DEFAULT_WIDTH + 10
        x = self.GetSize().x - spacing
        y = 0
        picId = len( self.__zuiObjects ) # start ID at lowest unclaimed id...

        # TODO also avoid overlapping existing objects in this function, if
        # possible.
        if addGoogleSearch:
            # Add in a web object which points to the google search page
            # for this term.
            googleSearchUrl = "http://www.google.com/search?q=%s" % addGoogleSearch
            obj = ZuiWebObject.fromUrl( self, picId, wx.Point( x, y ), googleSearchUrl )

            # TODO factor the stuff below out into an addObject method.
            obj.Bind( wx.EVT_MOUSE_EVENTS, obj.mouseEventHandler )
            self.__zuiObjects.append( obj )

            # Get ready for next object to be included:
            picId += 1
            y += obj.GetSize().y + 10
            
        for imageRow in queryResults:
            # jpg1 = wx.Image( imageFileName, wx.BITMAP_TYPE_ANY ).ConvertToBitmap()
            # bitmap upper left corner is in the position tuple (x, y) = (5, 5)
            dataType = imageRow.dataType
            if dataType == "picture":
                try:
                    obj = ZuiPictureObject( self,
                                            imageRow,
                                            picId,
                                            wx.Point( x, y ) )
                except wx._core.PyAssertionError:
                    print "Invalid image in db, deleting!"
                    SingleImageRow.delete( imageRow.id )
                    continue
                    
            elif dataType == "text":
                obj = ZuiTextObject( self,
                                     imageRow,
                                     picId,
                                     wx.Point( x, y ) )
            elif dataType == "web":
                obj = ZuiWebObject.fromImageRow( self,
                                                 picId,
                                                 wx.Point( x, y ),
                                                 imageRow )

            # This binds all mouse events at once
            obj.Bind( wx.EVT_MOUSE_EVENTS, obj.mouseEventHandler )

            self.__zuiObjects.append( obj )

            # Get ready for next object to be included:
            picId += 1
            y += obj.GetSize().y + 10
            if y > self.GetSize().y:
                y = 0
                x -= spacing


    def openTagEditField( self, obj ):
        self.finishTagField() # just in case it was already open with another object
        
        row = obj.getImageRow()
        self.Parent.showTagField( row.tags )
        self.__objectBeingTagged = obj
        # Put keyboard focus in the tag field -- how?

    def finishTagField( self ):
        self._saveFocusedObj()
        self.Parent.hideTagField()
        self.__objectBeingTagged = None
        
    def _getAdjustedMouseEventLocation( self, event ):
        eid = event.GetId()
        if eid > 0 and eid < len( self.__zuiObjects ):
            origin = self.__zuiObjects[ eid ].GetPosition()
            return ( event.X + origin.x, event.Y + origin.y )
        return event.GetPositionTuple()

    def leftMouseDown( self, event ):
        tool = figureOutTool( event )
        x, y = self._getAdjustedMouseEventLocation( event )
        if tool == SCROLL_TOOL:
            self._scrollStartPoint = ( x, y )
        
    def leftMouseUp( self, event ):
        tool = figureOutTool( event )
        x, y = self._getAdjustedMouseEventLocation( event )
        if tool == ZOOM_TOOL:
            self.doZoom( x, y, 2 )
        elif tool == SCROLL_TOOL:
            self.doScroll( x, y, False )

    def rightMouseUp( self, event ):
        tool = figureOutTool( event )
        x, y = self._getAdjustedMouseEventLocation( event )
        if tool == ZOOM_TOOL:
            self.doZoom( x, y, 0.5 )
        
    def doScroll( self, x, y, mouseIsDown ):
        self.finishTagField()
        xOffset = self._scrollStartPoint[0] - x
        yOffset = self._scrollStartPoint[1] - y
        for obj in self.__zuiObjects:
            obj.scroll( xOffset, yOffset )
        self.Refresh()
        
    def doZoom( self, x, y, zoomFactor ):
        self.finishTagField()
        for obj in self.__zuiObjects:
            obj.zoom( x, y, zoomFactor )
        self.Refresh()
        
    def onTagEdit( self, event ):
        self._tagFieldDirty = True



    def _saveFocusedObj( self ):
        if self.__objectBeingTagged != None:
            self.__objectBeingTagged.saveChanges()
            if self._tagFieldDirty:
                row = self.__objectBeingTagged.getImageRow()
                row.tags = self.Parent.getTagFieldValue()
                self._tagFieldDirty = False

    def onDoubleClick( self, event ):
        toolType = figureOutTool( event )
        if toolType == NORMAL_TOOL:
            self._saveFocusedObj()
            # focus on this zui object, i.e. center and zoom to 100%.
            obj = self.__zuiObjects[ event.Id ]
            row = obj.getImageRow()
            oldSize = obj.GetSize()
            center = obj.GetPosition()
            naturalSize = obj.getNaturalSize()
            scaleFactor = naturalSize[0] / float(oldSize.x)
            self.doZoom( center.x, center.y, scaleFactor )
            for obj in self.__zuiObjects:
                obj.scroll( center.x, center.y )

    def doEverythingQuery( self ):
        queryResults = SingleImageRow.select( )[:QUERY_LIMIT]
        self._display( queryResults )

    def doSearchQuery( self, searchText ):
        basicQueryString = """tags LIKE '%%%s%%'"""
        # re.sub( pattern, replacement, original )
        # Try this: Replace every word term with """tags LIKE '%searchterm%'"""
        # Replace + with """ AND """
        # Replace | with """ OR """
        # Leave parens alone
        # See if that works as an SQL query.
        if "+" in searchText: # support AND operator
            terms = searchText.split( "+" )
            queryString = " AND ".join( [ basicQueryString % term for term in terms ] )
        else:
            queryString = basicQueryString % searchText
        queryResults = SingleImageRow.select( queryString )
        self._display( queryResults, addGoogleSearch = searchText ) # not queryString.

    def doUntaggedQuery( self ):
        queryResults = SingleImageRow.select( """tags = '' """ )[:QUERY_LIMIT]
        self._display( queryResults )
        

if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame1 = ZuiViewerFrame( "goodies" )
    frame1.Show( True )
    app.MainLoop()
