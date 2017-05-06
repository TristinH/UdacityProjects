# Udacity Full Stack Nanodegree Projects

This Repo contains the links to all the individual projects I completed for Udacity's Full Stack Web Developer Nanodegree.

### Project Portfolio

A simple web page exhibiting a few of the other projects. The goal of this project was to take a PDF mockup and transform it into HTML. 
The layout of the mockup had to be matched as close as possible while providing unique images and text. Additionally, the page had to be 
responsive for a pleasing look on tablet and mobile phone screens.

[Repository Link](https://github.com/TristinH/project-portfolio)

### Multi User Blog

A fully functional blog with the ability to support many users. Users can make posts that are updated to the main page. Other users can 
view those posts, like/unlike the posts, and create comments. Users can create accounts with a username and password. They can edit and 
delete their own posts. Passwords are stored securely with hashing and salting and any forms are checked for authorization before being 
processed. User sessions are tracked with the use of a secure cookie that is a hash of the user's id and a secret string. 

[Repository Link](https://github.com/TristinH/multi-user-blog)

[Deployed App Link](http://www.basic-blog-153405.appspot.com/)

### Tournament Database Schema

A database API to allow one to easily implement a swiss tournament bracket. The main purpose was to design a database schema that stored 
a player's standings in a swiss bracket after each round. The schema is presented in the form of an SQL file that can be used to create 
the database to use in an application. Additionally, there is a python utility class included that abstracts away many of the tasks one 
would need to run a swiss tournament such as checking player standings and matching players for a round.

[Repository Link](https://github.com/TristinH/tournament-database-schema)

### Item Catalog

A simple web application with complete CRUD functionality and user authentication with OAuth 2. The goal was to make a web application 
that could interact with a database to create a catalog for certain items that are broken up into categories. Users have the ability to 
perform all the major database operations (create, read, update, and delete) on categories or items they enter. Users are authenticated 
with Google's OAuth 2 service. Authorization is considered prior to any alteration to the database.  

[Repository Link](https://github.com/TristinH/item-catalog)

### Neighborhood Map

A single page, Google Maps based application. A map with popular locations in Los Angeles is displayed by default when the application 
is run. Users can filter out locations by inputing searches in a text field that hides or shows markers based on what locations match
the search text. When a button or marker corresponding to a particular location is clicked, the name of the location and an image 
associated with the location, provided by Flickr, is displayed in an info window. This project demonstrated the benefits of using third
party APIs to add functionality to the front end, using AJAX requests to load data asynchronously, and implementing a proper MVC
design pattern to separate concerns. 

[Repository Link](https://github.com/TristinH/neighborhood-map)

### Linux Server Configuration

A project to set up a server for a previous project (the item catalog application). The server was set up using Amazon Web Services.
I created an instance online and configured the server from there. I configured the firewall to only allow certain connections to 
increase the application security. I then installed all the components necessary to allow the server to serve the application. This
project gave me great insight into how to perform system administration tasks. This is necessary for a full stack developer to know
because development is only the first half of building a web application. Maintaining and monitoring the application is essential to
its success.

[Repository Link](https://github.com/TristinH/linux-server-configuration)
