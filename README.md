# BICON: BICON's Interactive CONtroller
Remote Controller for BI System. Adding external services for BI Tool

## Django
### Running in outer Django project folder (cd bicon)
* Make Migrations
`python manage.py makemigrations`
* Migrate to Database
`python manage.py migrate`
* Run Server
`python manage.py runserver`
* Run Django Python Shell
`python manage.py shell` or `django-admin shell`
  
## Celery 
### Running in outer Django project folder (cd bicon)
* Start Worker 
`celery -A bicon worker -P solo`
* Start Beat (Scheduler)
`celery -A bicon beat` 


## Superset

`superset run -p 8088 --with-threads --reload --debugger`