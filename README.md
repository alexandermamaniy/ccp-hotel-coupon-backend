# Hotel App


## Project Download
```
git clone https://github.com/alexandermamaniyucra/ccp-hotel-coupon-backend.git
cd hotelcoupon/
```

### About DEVELOP ENVIRONMENT
you must create a file named ".env.development" in the same directory of project with the environment variables for the database and set up your database configurations

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
AWS_REGION=awsrregion
AWS_SQS_QUEUE_URL=sqsurl
AWS_SNS_REPORT_NOTIFICATION_ARN=snsarn
AWS_SNS_USED_COUPON_NOTIFICATION_ARN=snsarn
AWS_SNS_NEW_COUPON_NOTIFICATION_ARN=snsarn
AWS_QUERYSTRING_AUTH=False
```
### About Dependencies
```shell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install hotel-coupon-app-package-alexandermamani
```

### Export the environment variables for development
```
export DJANGO_SETTINGS_MODULE=hotelcoupon.settings.development
export DJANGO_ENV=development
```


### Run migrations
You can run generate the migrations and apply them and also create a superuser in order to crowded
```
python manage.py makemigrations users hotelier_profiles user_profiles coupons reports
python manage.py migrate
python manage.py runserver
```

### About DATABASE
You can set up your database with only one superuser for the admin interface or restore a seed database with some users and models as a sample of the app.
You are only able to choose one of them, not both.

#### Creating a superuser
```
python manage.py createsuperuser
```

#### Restore a seed database
```
python manage.py flush --noinput
python manage.py loaddata seeders/data.json
```
email: admin@admin.com \
password: admin

### Generating a seed database backup
If you want to populate the database by seeders, you must not create a superuser by commands.  
```
python manage.py dumpdata > seeders/data.json
```

### Run interactive mode
```
python manage.py shell
```
### Generate Scheme for Swagger
If you make any changes in the models, must run this command to update the Swagger's schemas  
```
python manage.py spectacular --file schema.yml 
```
then go to http://localhost:8000/api/schema/docs/#/



## Test stage
### Export the environment variables for testing
```
export DJANGO_SETTINGS_MODULE=hotelcoupon.settings.testing
export DJANGO_ENV=testing
```
Execute the tests
```
python manage.py test users.tests
```

## Deploy stage

See Pipeline in the repository

