# What about?
Slander is an extended version of the blog that implements the following functionality:
1) CRUD for articles
2) Comments and rating of articles, filter by rating
3) Search by article title, search by genres
4) Create a user, change his password and profile picture
5) Authorization via VK

# How to install
1) Download the code:  
   * git clone https://github.com/4chillout/Slander_django.git  
2) Create a virtual environment and install requirements via pip:  
   * cd slander_django  
   * python -m venv venv  
   * venv\Scripts\activate.ps1  
   * pip install -r requirements.txt
3) Make a migrations to your database:
   * python manage.py makemigrations  
   * python manage.py migrate  
4) Now you can run the app:
   * python manage.py runserver
