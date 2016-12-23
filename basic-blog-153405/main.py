#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import webapp2
import jinja2

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

class BlogPost(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
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

        if subject and content:
            #enter blog in database and redirect to home page
            new_post = BlogPost(subject = subject, content = content)
            new_post.put()
            self.redirect('/%s' % str(new_post.key().id()))
        else:
            error = "Post must have a subject and content"
            self.render("newpost.html", subject = subject, content = content, error = error)

class SinglePostHandler(Handler):
    def get(self, post_id):
        key = db.Key.from_path('BlogPost', int(post_id))
        post = db.get(key)
        self.render("singlepost.html", post = post)

app = webapp2.WSGIApplication([
    ('/', MainPageHandler),
    ('/newpost', NewPostHandler),
    ('/([0-9]+)', SinglePostHandler)
], debug=True)
