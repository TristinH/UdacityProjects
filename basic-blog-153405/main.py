#!/usr/bin/env python

import os
import webapp2
import jinja2
import re
import string
import random
import hashlib
import hmac
import time

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

s = 'ko12je,2o4908ifeop,kl2kofwh893hr09op32mrl'

def secure(plain):
    return '%s|%s' % (plain, hmac.new(s, plain).hexdigest())

def verify_secure(test):
    plain = test.split('|')[0]
    if test == secure(plain):
        return plain

def make_salt(length = 5):
    return ''.join(random.choice(string.letters) for x in range(length))

def hash_string(name, password, salt = None):
    if not salt:
        salt = make_salt()
    hashed = hashlib.sha256(name + password + salt).hexdigest()
    return '%s,%s' % (hashed, salt)

def check_hash(name, password, hashed):
    salt = hashed.split(',')[1]
    return hashed == hash_string(name, password, salt)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_cookie(self, name, value):
        secure_cookie = secure(value)
        self.response.headers.add_header(
            'Set-Cookie', '%s=%s; Path=/' % (name, secure_cookie))

    def get_cookie(self, name):
        cookie = self.request.cookies.get(name)
        return cookie and verify_secure(cookie)

    def login(self, user):
        self.set_cookie('user', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        u = self.get_cookie('user')
        self.user = u and User.by_id(int(u))

#class to store a single blog post
class BlogPost(db.Model):
    username = db.StringProperty(required = True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    likes = db.IntegerProperty(required = True)
    unlikes = db.IntegerProperty(required = True)

    @classmethod
    def by_username(cls, username):
        return db.GqlQuery("SELECT * FROM BlogPost WHERE username = '%s'" % username)

#class to store user information
class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def by_id(cls, id):
        return User.get_by_id(id)

    @classmethod
    def by_name(cls, name):
        return User.all().filter('username =', name).get()

    @classmethod
    def register(cls, name, password, email = None):
        pw_hash = hash_string(name, password)
        u = User(username = name, password = pw_hash, email = email)
        return u

    @classmethod
    def login(cls, name, password):
        u = cls.by_name(name)
        if u and check_hash(name, password, u.password):
            return u

class MainPageHandler(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 10")
        self.render("front.html", posts = posts)

#class to handle creating a new post
class NewPostHandler(Handler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/register")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        #check if the user entered both required fields
        if subject and content:
            #enter blog in database and redirect to individual blog page
            new_post = BlogPost(username = self.user.username, subject = subject, content = content, likes = 0, unlikes = 0)
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
        bad_signup = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        #check to see if there are any registration errors
        error = ""
        if not username:
            error = "You must provide a username"
            bad_signup = True

        if not password:
            error = "You must provide a password"
            bad_signup = True
        elif not verify:
            error = "You must verify your password"
            bad_signup = True
        elif verify != password:
            error = "Passwords do not match"
            bad_signup = True

        if email and not re.match('.*@.*', email):
            error = "That is not a valid email"
            bad_signup = True

        #if there are errors reload the page with the error, if not check if the user is already there
        if bad_signup:
            self.render("registration.html", error = error)
        else:
            u = User.by_name(username)
            if u:
                self.render("registration.html", error = "That username already taken")
            else:
                u = User.register(username, password, email)
                u.put()

                self.login(u)
                self.redirect("/welcome")


class WelcomePageHandler(Handler):
    def get(self):
        if self.user:
            user_posts = BlogPost.by_username(self.user.username)
            self.render("welcome.html", user_posts = user_posts, username = self.user.username)
        else:
            self.redirect("/register")

class SigninPageHandler(Handler):
    def get(self):
        self.render("signin.html")

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect("/welcome")
        else:
            error = "Invalid login"
            self.render("signin.html", username = username, error = error)

class LogoutPageHandler(Handler):
    def get(self):
        self.logout()
        self.redirect("/register")

class EditPageHandler(Handler):
    def get(self, post_id):
        key = db.Key.from_path('BlogPost', int(post_id))
        post = db.get(key)
        if self.user.username != post.username:
            self.redirect("/signin", error = "You can only edit your own posts")
        else:
            self.render("editpost.html", user = self.user.username,
                        subject = post.subject, content = post.content)

    def post(self, post_id):
        subject = self.request.get("subject")
        content = self.request.get("content")

        #check if the user entered both required fields
        if subject and content:
            #alter the blog in database and redirect to individual blog page
            key = db.Key.from_path('BlogPost', int(post_id))
            post = db.get(key)
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/%s' % str(post.key().id()))
        else:
            error = "Post must have a subject and content"
            self.render("newpost.html", subject = subject, content = content, error = error)

class DeletePageHandler(Handler):
    def get(self, post_id):
        key = db.Key.from_path('BlogPost', int(post_id))
        post = db.get(key)
        if self.user.username != post.username:
            self.redirect("/signin", error = "You can only delete your own posts")
        else:
            post.delete()
            time.sleep(0.5)
            self.redirect("/welcome")

app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/newpost', NewPostHandler),
    ('/([0-9]+)', SinglePostHandler),
    ('/register', RegistrationPageHandler),
    ('/welcome', WelcomePageHandler),
    ('/signin', SigninPageHandler),
    ('/logout', LogoutPageHandler),
    ('/edit/([0-9]+)', EditPageHandler),
    ('/delete/([0-9]+)', DeletePageHandler)
], debug=True)
