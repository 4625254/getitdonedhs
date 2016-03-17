import os
import jinja2
import webapp2
import cgi
import urllib
from datetime import datetime, timedelta, date

from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#DEFAULT_NEWTASK_NAME = 'default_newtask'

def newtask_key():
	#creates datastore key
	return ndb.Key("NewTask", 1)

#CLASS:

#MODELS

class Person(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    following = ndb.StringProperty(indexed=False)
    addedtask = ndb.StringProperty(indexed=False)

class NewTask(ndb.Model):
	person = ndb.StructuredProperty(Person)
	taskname = ndb.StringProperty(indexed=False)
	duedate = ndb.DateProperty()


#HANDLERS
	
class AddTask(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
		}
        template = JINJA_ENVIRONMENT.get_template('add_task.html')
        self.response.write(template.render(template_values))

	def post(self):
		user = users.get_current_user()
        if user:
			if self.request.get('addtask'):
				t = NewTask(parent=newtask_key())
				t.person = Person(identity=users.get_current_user().user_id(), email=users.get_current_user().email())
				t.taskname = self.request.get('taskname')
				t.duedate = datetime.strptime(self.request.get('duedate'),'%Y-%m-%d')
				t.put()
				self.redirect('MyTask')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        task_query = NewTask.query(ancestor=newtask_key())
        tasks=task_query.fetch()
		
        uemail = []
        for task in tasks:
            if task.person.email not in uemail:
                uemail.append(task.person.email)
		
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
			'uemail': uemail,
			'tasks': tasks	
		}
        template = JINJA_ENVIRONMENT.get_template('mainpage.html')
        self.response.write(template.render(template_values))
      
		
class MyTask(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        task_query = NewTask.query(ancestor=newtask_key()).order(NewTask.duedate)
        tasks=task_query.fetch()
        today = date.today()
        threedays = timedelta(days = 3)
        twodays = timedelta(days = 2)
        oneday = timedelta(days = 1)
        usertask = self.request.get('usertask')
        
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'


        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'tasks': tasks,
			'today': today,
            'threedays': threedays,
            'twodays': twodays,
            'oneday': oneday,
			'usertask': usertask
		}
        template = JINJA_ENVIRONMENT.get_template('my_task.html')
        self.response.write(template.render(template_values))
	
class TaskFeed(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        task_query = NewTask.query(ancestor=newtask_key()).order(NewTask.duedate)
        tasks=task_query.fetch()
        today = date.today()
        threedays = timedelta(days = 3)
        twodays = timedelta(days = 2)
        oneday = timedelta(days = 1)
        following = self.request.get('email')
        
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'


        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'tasks': tasks,
			'today': today,
            'threedays': threedays,
            'twodays': twodays,
            'oneday': oneday,
			'following':following
		}
        template = JINJA_ENVIRONMENT.get_template('task_feed.html')
        self.response.write(template.render(template_values))		
		
class UserTask(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        task_query = NewTask.query(ancestor=newtask_key()).order(NewTask.duedate)
        tasks=task_query.fetch()
        today = date.today()
        threedays = timedelta(days = 3)
        twodays = timedelta(days = 2)
        oneday = timedelta(days = 1)
        profile = self.request.get('email')
        
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
            'tasks': tasks,
			'today': today,
            'threedays': threedays,
            'twodays': twodays,
            'oneday': oneday,
            'profile': profile			
		}
        template = JINJA_ENVIRONMENT.get_template('user_task.html')
        self.response.write(template.render(template_values))

class DeleteTask(webapp2.RequestHandler):
    def post(self):
        task = NewTask()
        task = task.get_by_id(long(self.request.get('id')), parent=newtask_key())
        task.key.delete()
        
        self.redirect('/MyTask')

class Follow(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if user:
			t = Person(parent=newtask_key())
			t.following = self.request.get('email')
			t.put()
			self.redirect('TaskFeed')
		else:
			self.redirect(users.create_login_url(self.request.uri))

class HowItsDone(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
		}
        template = JINJA_ENVIRONMENT.get_template('howitsdone.html')
        self.response.write(template.render(template_values))
            
# main
app = webapp2.WSGIApplication([
    ('/', HowItsDone),
    ('/MainPage',MainPage),
	('/AddTask',AddTask),	
	('/MyTask',MyTask),
	('/TaskFeed',TaskFeed),
	('/UserTask',UserTask),
	('/DeleteTask',DeleteTask),
	('/Follow',Follow)
], debug=True)
