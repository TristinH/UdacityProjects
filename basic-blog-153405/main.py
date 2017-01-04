#!/usr/bin/env python

import os
import webapp2
import jinja2
import re
import string
import random
import hashlib

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

#class to store a single blog post
class BlogPost(db.Model):
    user = db.IntegerProperty(required = True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

#class to store user information
class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    salt = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPageHandler(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 10")
        self.render("front.html", posts = posts)

class NewPostHandler(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        #check if the user entered both required fields
        if subject and content:
            #enter blog in database and redirect to individual blog page
            new_post = BlogPost(subject = subject, content = content)
            new_post.put()
            self.redirect('/%s' % str(new_post.key().id()))
        else:
            error = "Post must have a subject and content"
            self.render("newpost.html", subject = subject, content = content, error = error)

class SinglePostHandler(Handler):
    #find the individual blog post and display it on its own page
    def get(self, post_id):
        key = db.Key.from_path('BlogPost', int(post_id))
        post = db.get(key)
        self.render("singlepost.html", post = post)

class RegistrationPageHandler(Handler):
    def get(self):
        self.render("registration.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        #check if all required fields are entered
        if username and password and verify:
            #if the user enters an email, make sure it is valid
            if email and not re.match(r'.*@.*', email):
                error = "The Email entered is not valid"
                self.render("registration.html", username = username, email = email, error = error)
            #if the passwords do not match alert the user
            elif not (password == verify):
                error = "The passwords do not match"
                self.render("registration.html", username = username, email = email, error = error)
            else:
                self.write("Thank you")
        else:
            error = "You must enter a username and password"
            self.render("registration.html", username = username, email = email, error = error)

    #function to encrypt a password to store it in the database
    def secure_password(self, password):


app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/newpost', NewPostHandler),
    ('/([0-9]+)', SinglePostHandler),
    ('/register', RegistrationPageHandler)
], debug=True)
