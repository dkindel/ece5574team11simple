import os

import jinja2
import webapp2

from google.appengine.api import taskqueue
from google.appengine.ext import ndb


JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))



class Counter(ndb.Model):
    count = ndb.IntegerProperty(indexed=False)

class StartPage(webapp2.RequestHandler):
    def get(self):
        #counter = 0
        query = Counter.query()
	counter = Counter.get_or_insert("key", count = 0)
        count_value = counter.count if Counter else 0
        template_values = {'counter': counter.count}
        start_template = JINJA_ENV.get_template('start.html')
        self.response.out.write(start_template.render(template_values))

class StartHandler(webapp2.RequestHandler):
    def post(self):
	counter = Counter.get_or_insert("key", count = 0)
        counter.count = 0
        counter.put()
        
        self.redirect('/started')


class CounterHandler(webapp2.RequestHandler):
    def get(self):
        counter_template = JINJA_ENV.get_template('counter.html')
        self.response.out.write(counter_template.render())


class AddHandler(webapp2.RequestHandler):
    def post(self):
        # Add the task to the default queue.
        taskqueue.add(queue_name='countAdder', url='/worker')
        self.redirect("/started")

class CounterWorker(webapp2.RequestHandler):
    def post(self):
        @ndb.transactional
        def update_counter():
	    counter = Counter.get_or_insert("key", count = 0)
            counter.count += 1
            counter.put()
	update_counter()

class EndHandler(webapp2.RequestHandler):
    def post(self):
	counter = Counter.get_or_insert("key", count = 0)
        print counter.count
        self.response.out.write("")
        query = Counter.query()
	counter = Counter.get_or_insert("key", count = 0)
        template_values = {'counter': counter.count}
        end_template = JINJA_ENV.get_template('end.html')
        self.response.out.write(end_template.render(template_values))

class ExitHandler(webapp2.RequestHandler):
    def post(self):
        self.redirect("/")

APP = webapp2.WSGIApplication(
    [
        ('/', StartPage),
        ('/start', StartHandler),
        ('/started', CounterHandler),
        ('/add', AddHandler),
        ('/worker', CounterWorker),
        ('/end', EndHandler),
        ('/exit', ExitHandler)
    ], debug=True)
