import os
import urllib
import operator


from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import db

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_SCORE = '5'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.


class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Leader(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    name = ndb.StringProperty(indexed=True)
    score = ndb.IntegerProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        person = Leader.query()
        person = person.order(-Leader.score,Leader.date)
        leaders = person.fetch_page(10)
        
        
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'leaders': leaders,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('/leaderboard.html')
        self.response.write(template.render(template_values))


class Leaderboardpost(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
    
        person = Leader()

        if users.get_current_user():
            person.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        person.name = self.request.get('name')
        person.score = int(self.request.get('score'))
        if person.name[:9] == "maplelion":
            self.redirect("http://maplelion.dhs.sg")
        else:
            person.put()

            query_params = {person.score: person.name}
            self.redirect('/leaderboard.html?' + urllib.urlencode(query_params))


application = webapp2.WSGIApplication([
    ('/leaderboard.html', MainPage),
    ('/leaderboard1', Leaderboardpost)],
    debug=True)
