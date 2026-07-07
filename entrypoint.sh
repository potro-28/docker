#!/bin/sh

echo "Aplicando migraciones..."
python gimnasio_naza/manage.py migrate

echo "Recolectando archivos estáticos..."
python gimnasio_naza/manage.py collectstatic --noinput

echo "Iniciando Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --chdir gimnasio_naza config.wsgi:application