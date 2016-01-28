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
        Counter.count = 0
        template_values = {'counters': Counter.query()}
        start_template = JINJA_ENV.get_template('start.html')
        self.response.out.write(start_template.render(template_values))

class StartHandler(webapp2.RequestHandler):
    def post(self):
        self.redirect('/running')
        taskqueue.add(queue_name='endTimer', url='/end', countdown=5)


class CounterHandler(webapp2.RequestHandler):
    def get(self):
        print "counter"
        if Counter.count == 0:
            counter_template = JINJA_ENV.get_template('counter.html')
            self.response.out.write(counter_template.render())
        if Counter.count == 1:
            self.redirect('/exit')    

class EndHandler(webapp2.RequestHandler):
    def post(self):
        Counter.count = 1
        taskqueue.add(queue_name='countAdder', url='/running')


class ExitHandler(webapp2.RequestHandler):
    def post(self):
        numclicks = self.request.get('clicks') 
        print "at exit"
        self.redirect('/')
        # template_values = {'counter': numclicks}
        # self.response.out(start_template.render(template_values)) 


APP = webapp2.WSGIApplication(
    [
        ('/', StartPage),
        ('/start', StartHandler),
        ('/running', CounterHandler),
        ('/end', EndHandler),
        ('/exit', ExitHandler)
    ], debug=True)