import os

import jinja2
import webapp2

from google.appengine.api import taskqueue
from google.appengine.ext import ndb


JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Counter(ndb.Model):
    count = ndb.IntegerProperty(indexed=False)

class StartHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {'counters': Counter.query()}
        start_template = JINJA_ENV.get_template('start.html')
        self.response.out.write(start_template.render(template_values))

class StartHandler(webapp2.RequestHandler):
    def post(self):
	counter = Counter.get()
        counter.count = 0
        counter.put()
        
        taskqueue.add(url='/end')

        self.redirect('/started')


class CounterHandler(webapp2.RequestHandler):
    def get(self):
        counter_template = JINJA_ENV.get_template('counter.html')
        self.response.out.write(counter_template.render())


class AddHandler(webapp2.RequestHandler):
    def post(self):
        # Add the task to the default queue.
        taskqueue.add(url='/worker', countdown=5)

class CounterWorker(webapp2.RequestHandler):
    def post(self):
        @ndb.transactional
        def update_counter():
	    counter = Counter.get()
            counter.count += 1
            counter.put()

	update_counter()

class EndHandler(webapp2.RequestHandler):
    def post(self):
        self.redirect('/')


APP = webapp2.WSGIApplication(
    [
        ('/', StartPage),
        ('/start', StartHandler),
        ('/started', CounterPage),
        ('/add', AddHandler),
        ('/worker', CounterWorker),
        ('/end', EndHandler)
    ], debug=True)
