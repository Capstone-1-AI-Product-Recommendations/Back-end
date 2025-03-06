download python version 3.9.13 => https://www.python.org/downloads/release/python-391/

download redis for windown => https://github.com/tporadowski/redis/releases
 
Installation guide redis => https://www.youtube.com/watch?v=DLKzd3bvgt8

python -m venv myenv

myenv\Scripts\activate

celery -A web_backend worker --pool=solo --loglevel=debug

celery -A web_backend worker --pool=solo --loglevel=info

#sử dụng nhiều tiến trình (chỉ can chay 2 cau nay)
celery -A web_backend worker --pool=threads --loglevel=info --concurrency=8

celery -A web_backend beat --loglevel=info

python manage.py runserver 0.0.0.0:8000

python.exe -m pip install --upgrade pip

pip install -r requirements.txt

python manage.py runserver