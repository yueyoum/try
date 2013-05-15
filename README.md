*   libjpeg8-dev libpng12-dev 这些是PIL/Pillow所需的
*   确保启动了mysql和redis
*   virtualenv 并安装 requirements.txt 中的依赖
*   python manage.py validate
*   python manage.py syncdb
*   python manage.py collectstatic
*   配置并启动nginx, uwsgi
