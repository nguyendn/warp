from zope.interface import implements

from twisted.web.resource import IResource, NoResource

from mako.template import Template

from warp.webserver import auth, node
from warp.runtime import config



class WarpResourceWrapper(object):
    implements(IResource)

    isLeaf = False

    def getChildWithDefault(self, firstSegment, request):
        session = request.getSession()
        if session is not None:
            request.avatar = session.avatar

        if firstSegment == '__login__':
            return auth.LoginHandler()
        elif firstSegment == '__logout__':
            return auth.LogoutHandler()
        elif not firstSegment:
            return Redirect(config['default'])

        return WarpResource(firstSegment)



class Redirect(object):
    implements(IResource)

    def __init__(self, url):
        self.url = url

    def render(self, request):
        request.redirect(self.url)
        return "Redirecting..."



class WarpResource(object):
    implements(IResource)

    # You can always add a slash
    isLeaf = False


    def __init__(self, nodeName):
        self.nodeName = nodeName
        self.facetName = None
        self.args = []
        

    def getChildWithDefault(self, segment, request):
        self.facetName = segment
        self.isLeaf = True
        return self

            
    def render(self, request):
        self.args = request.postpath

        if not self.facetName:
            request.redirect(request.childLink('index'))
            return "Redirecting..."

        node = getattr(__import__("nodes", fromlist=[self.nodeName]),
                       self.nodeName)

        templatePath = (config['siteDir']
                        .child('nodes')
                        .child(self.nodeName)
                        .child(self.facetName + ".mak"))

        template = Template(filename=templatePath.path,
                            format_exceptions=True)

        return template.render(node=node,
                               avatar=request.avatar)






#         if request.avatar is None:
#             loggedIn = "Not logged in."
#         else:
#             loggedIn = "Logged in as %s" % request.avatar.email.encode("utf-8")

#         return """
# %s<br />
# <form method="POST" action="/__login__">
# Email: <input type="text" name="email" /><br />
# Pass: <input type="text" name="password" /><br />
# <input type="submit" value="Log in" />
# </form>
# """ % loggedIn


#     def __repr__(self):
#         return "<NodeResource: %s::%s (%s)>" % (
#             self.nodeName, self.facetName, self.args)

