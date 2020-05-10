# TiMBIM Definitions
Code InstituteUser Data Centric Development Milestone Project

I made this website to made it easy to lookup BIM related terms and definitions and to let everyone share his/her definitions easily.

## User Experience
I decided to go for a simple not to cluttered design with no background picture. Everyone can easily search for all definitions bases on term, language or editor.

## Technologies Used
1. HTML
2. CSS
3. Bootstrap (4.3.1)
4. Python
5. Flask
6. MongoDB

## Features to be implemented in future
In future I will provide functionality to delete your account and recover password

## CONTENT
All content is written by me.

##      CONTENT OVERVIEW
###     **Home Page**
List with all available terms and definitions sorted + search possibility. Search is not case sensitive + it is enough to just add a part of a term.
![Home Page](static/Wireframes/Home%20Page.png)

###     **User SignUp**
User SignUp Page. Tests are added to verify.
* name is unique
* email is unique
* password and password confirmation are the same

![SignUp Page](static/Wireframes/SignUp.png)


###     **User Login** 
Login Page. Test are added to verify Email and Password.
![SignUp Page](static/Wireframes/Login.png)

###     **Edit User**
Possibility to edit Username or Password
![SignUp Page](static/Wireframes/Edit%20user.png)


###     **Add Definition**
Possibility to add definitions. Only possible after login. Username will be added to edited/added definition
![SignUp Page](static/Wireframes/Add%20definition.png)

###     **Edit Definition**
Possibility to edit existing definitions. Only possible after login. Username will be added to edited/added definition
![SignUp Page](static/Wireframes/Edit%20definition.png)

## Testing
The website is tested on different devices from smartphone to workstation with a 34" screen.
CSS was tested several times on "different devices" using developer tools in different webbrowsers. Using life editing in the webbrowser different settings were tested and improved.

## Deployment
The website is hosted on [Heroku](https://ms3-bim-definitions.herokuapp.com/).

If you want to run the code locally, you can clone this repository into the editor of your choice by pasting: "git clone https://github.com/AllardL/MS3-BIM-definitions.git" into your terminal.
To cut ties with this GitHub repository, type git remote rm origin into the terminal.

This application makes use of MongoDB. If you want to use it you need to set up a database with the following collections: "definitions", "language" and "user" and provide the URI for the variable MONGO_URI,
also a key needs to be provided at the variable SECRET_KEY.

## Media
There was no media used from outside sources.

### This website is only for educational use. 