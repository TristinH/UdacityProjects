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

    def secure_cookie(self, cookie):
		hashed = hashlib.sha256(cookie).hexdigest()
		return '%s,%s' % (cookie, hashed)

	def validate_cookie(self, cookie):
		hashed = cookie.split(',')[1]
		return hashed == secure_cookie(cookie)

	def check_user(self):
		#check if the user has a valid cookie
		cookie = self.request.cookies.get('user_id')
		uid = cookie.split(",")[0]
		key = db.Key.from_path('User', int(uid))
		user = db.get(key)
		if user and self.validate_cookie(str(user.key().id()), cookie):
			return user

#class to store a single blog post
class BlogPost(db.Model):
    user = db.IntegerProperty(required = True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    likes = db.IntegerProperty(required = True)
    unlikes = db.IntegerProperty(required = True)

#class to store user information
class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)

    #secure the password at the time of creating the object
    def __init__(self, username, password, *args, **kwargs):
    	hashed = self.secure_password(username, password)
    	super(User, self).__init__(username, hashed, *args, **kwargs)

    #method to generate a random salt of a given length
	def generate_salt(self, length):
		salt = ''
		for i in range(length):
			salt.join(random.choice(string.letters))
		return salt

	#method to hash a password to store in the database
	def secure_password(self, username, password, salt = None):
		if not salt:
			salt = self.generate_salt(5)
		hashed = hashlib.sha256(username + password + salt).hexdigest()
		return '%s,%s' % (hashed, salt)

	#method to verify a password when the user tries to log in
	def validate_password(self, username, password, hashed):
		salt = hashed.split(',')[1]
		return hashed == self.secure_password(username, password, salt)

	#method to verify a user exists and to log them in
	def verify_user(self, username, password):
		user = db.GqlQuery("SELECT * FROM User WHERE username = username")
		if user and self.validate_password(username, password, user.password)
			return user


class MainPageHandler(Handler):
    def get(self):
    	user = self.check_user()
    	if not user:
        	posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 10")
        	self.render("front.html", posts = posts)
        else:
        	posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 10")
        	self.render("front.html", posts = posts)

#class to handle creating a new post 
class NewPostHandler(Handler):
    def get(self):
    	#only allow established users to access the new post page
    	user = self.check_user()
    	#if user is not signed in, redirect to the register page
    	if user:
        	self.render("newpost.html")
        else:
        	self.redirect("/register")

    def post(self):
    	user = self.check_user()
        subject = self.request.get("subject")
        content = self.request.get("content")

        #check if the user entered both required fields
        if subject and content:
            #enter blog in database and redirect to individual blog page
            new_post = BlogPost(user = user.key().id(), subject = subject, content = content, likes = 0, unlikes = 0)
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

class EditPageHandler(Handler):
	#find the individual blog post and display it on its own page
    def get(self, post_id):
    	user = self.check_user()
        key = db.Key.from_path('BlogPost', int(post_id))
        post = db.get(key)
        #check that the user signed in is the one that made the post
        if user and user.key().id() == post.user:
        	self.render("editpost.html", user = user.username, subject = post.subject, content = post.content)
        else:
        	error = "You cannot edit posts that aren't yours"
        	self.render("singlepost.html", post = post, error = error)

    def post(self, post_id):
    	user = self.check_user()
    	post_user = self.request.get("user")
        subject = self.request.get("subject")
        content = self.request.get("content")

        #check if the user entered both required fields
        if not user or user.username != post_user:
        	error = "You must be logged in to edit posts"
        	self.redirect('/signin', error = error)
        elif subject and content:
            #change the values of the subject and content for the blog post
            key = db.Key.from_path('BlogPost', int(post_id))
        	post = db.get(key)
        	post.subject = subject
        	post.content = content
        	post.put()
            self.redirect('/%s' % str(new_post.key().id()))
        else:
            error = "Post must have a subject and content"
            self.render("editpost.html", user = post_user, subject = subject, content = content, error = error)

    def delete(self, post_id):
    	user = self.check_user()
    	post_user = self.request.get("user")

        #check if the user entered both required fields
        if not user or user.username != post_user:
        	error = "You must be logged in to edit posts"
        	self.redirect('/signin', error = error)
        else:
            #delete the post
            key = db.Key.from_path('BlogPost', int(post_id))
        	post = db.delete(key)
            self.redirect('/')


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
            elif user_present(username):
            	error = "That username is already taken"
            	self.render("registration.html", username = username, email = email, error = error)
            else:
            	#create and store the new user
                new_user = User(username = username, password = password, email = email)
                new_user.put()

                #set the cookie that stores the id of the username
                cookie = self.secure_cookie(str(new_user.key().id()))
                self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % cookie)
                self.redirect('/welcome')
        else:
            error = "You must enter a username and password"
            self.render("registration.html", username = username, email = email, error = error)

    def user_present(self, username):
    	return user = db.GqlQuery("SELECT * FROM User WHERE username = username")


class WelcomePageHandler(Handler):
	def get(self):
		user = self.check_user()
		if user:
			#if the cookie is successfully authenticated redirect to the welcome page
			self.render("welcome.html", username = user.username)
		else:
			#if the cookie is not valid or is not there redirect to register
			self.redirect('/register')
			

class SigninPageHandler(Handler):
	def get(self):
		self.render("signin.html")

	def post(self):
		username = self.request.get("username")
        password = self.request.get("password")

        user = db.GqlQuery("SELECT * FROM User WHERE username = username")
        if not user:
        	error = "Invalid Login"
        	self.render("signin.html", username = username, error = error)
       	else:
       		verify = user.password
       		if not user.validate_password(username, password, verify):
       			error = "Invalid Login"
        		self.render("signin.html", username = username, error = error)
        	else:
        		cookie = self.secure_cookie(str(user.key().id()))
                self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % cookie)
                self.redirect('/welcome')

class LogoutPageHandler(Handler):
	def get(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
		self.redirect("/register")

app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/newpost', NewPostHandler),
    ('/([0-9]+)', SinglePostHandler),
    ('/register', RegistrationPageHandler),
    ('/welcome', WelcomePageHandler),
    ('/signin', SigninPageHandler),
    ('/logout', LogoutPageHandler),
    ('/edit', EditPageHandler)
], debug=True)
