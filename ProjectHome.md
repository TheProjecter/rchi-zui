# Corey's zui #
Most of the time I've spent developing The Zui (aka tzui) has been on design. I've had the basic idea of how a zui should work for several years now (see our [ZUI specification](http://rchi.raskincenter.org/index.php?title=ZUI_Specification)) but I've had to make some compromises as I cranked out the code.

So currently it's rather rudimentary, but it nevertheless gives you a glimpse of the possibilities. Just be warned that it's still buggy despite the simplicity of the architecture. It uses the [Opioid2D](http://opioid-interactive.com/opioid2d/) framework, which is an excellent interface to an efficient OpenGL 2D rendering engine. But it can't handle very large images (it's made for games!), so be careful about that.

While it can only use images (png, gif, jpg), the zooming interface itself is largely complete--all that remains are some scaling issues and better pan controls.

Check out [my roadmap](http://docs.google.com/Doc?id=ajksn6cgnh59_13d7ntxw), download the executable on the right of this page, or grab the source. And of course, have fun!

# Jono's zui #
At this point, this is just a quick-and-dirty prototype of a ZUI (Zooming User Interface) in Python, using wxpython.  It was inspired by the ZoomWorld presented in Jef Raskin's book 'The Humane Interface'.

My first goal is something very modest.  I'm trying to make a ZUI-based application that I can use to edit and upload webcomics (a hobby of mine, for which the existing tools are quite frustrating).  This will require the ability to manipulate, edit, and transform various text and graphical formats, save changes, and upload them to a URL.  So, it is a nicely limited problem domain that at the same time poses interesting challenges.  Also, I figure that writing something I will actually use is the best way to get work done on this ZUI since I will be eating my own dog-food.

Longer-term goals are to see what we can do, interface-wise, by combining a ZUI with a tagging system, and to make a useful and working prototype of the kind of ZUI described in The Humane Interface, and then to go beyond it. |;`)