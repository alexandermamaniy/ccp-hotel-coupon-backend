# Hotel App

## System Dependencies
- docker
- docker-compose

## Project Download
```
git clone https://github.com/alexandermamaniyucra/ccp-hotel-coupon-backend.git
cd hotelcoupon/
```

## Develop stage
This stage allows developers make changes to the code and reflects the updates in real time.

### About ENVIRONMENTS
you must create a file named ".env.dev" in the same directory of docker-compose file with the environment variables for the database and set up your database configurations

```
MYSQL_DATABASE=databasename
MYSQL_USER=userdatabase
MYSQL_PASSWORD=databasepassword
MYSQL_HOST=host
MYSQL_PORT=3306
MYSQL_ROOT_PASSWORD=password
AWS_ACCESS_KEY_ID=awsaccesskey
AWS_SECRET_ACCESS_KEY=awssecretkey
AWS_STORAGE_BUCKET_NAME=awsbucketname
```

### Executing the project with docker-compoose 
```
docker-compose -f docker-compose.development.yml build
docker-compose -f docker-compose.development.yml up
```

### Run migrations and server dev
You can run generate the migrations and apply them and also create a superuser in order to crowded
```
docker-compose -f docker-compose.development.yml exec web python manage.py makemigrations users hotelier_profiles user_profiles coupons
docker-compose -f docker-compose.development.yml exec web python manage.py migrate
docker-compose -f docker-compose.development.yml exec web python manage.py runserver
```

### About DATABASE
You can set up your database with only one superuser for the admin interface or restore a seed database with some users and models as a sample of the app.
You are only able to choose one of them, not both.

#### Creating a superuser
```
docker-compose -f docker-compose.development.yml exec web python manage.py createsuperuser
```

#### Restore a seed database
```
docker-compose -f docker-compose.development.yml exec web python manage.py flush --noinput
docker-compose -f docker-compose.development.yml exec web python manage.py loaddata seeders/data.json
```
email: admin@admin.com \
password: admin

### Generating a seed database backup
If you want to populate the database by seeders, you must not create a superuser by commands.  
```
docker-compose -f docker-compose.development.yml exec web python manage.py dumpdata > seeders/data.json
```

### Run test
```
docker-compose -f docker-compose.development.yml exec web python manage.py test
```
### Run interactive mode
```
docker-compose -f docker-compose.development.yml exec web python manage.py shell
```
### Generate Scheme for Swagger
If you make any changes in the models, must run this command to update the Swagger's schemas  
```
docker-compose -f docker-compose.development.yml exec web python manage.py spectacular --file schema.yml 
```
then go to http://localhost:8000/api/schema/docs/#/


## Deploy stage

Allow to deploy the project in a production environment

```commandline
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up
```
Database migrations must migrate manually if you want to populate the database

See **About DATABASE** section, only change docker-compose.development.yml by docker-compose.production.yml

