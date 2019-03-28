
#!/bin/bash

cd /code

echo "Creating migrations"

python manage.py makemigrations
python manage.py migrate