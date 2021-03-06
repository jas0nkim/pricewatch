# build egg command: python setup.py bdist_egg -d /usr/local/etc/pwbot/dist

from setuptools import setup, find_packages

setup(
    name='pricewatch_web',
    version='0.0.1',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'psycopg2==2.8.5',
        'gunicorn==20.0.4',
        'Django==3.1.2',
        'djangorestframework==3.12.1',
        'graypy==2.1.0',
        'django-crispy-forms==1.9.2',
    ],
    scripts=['src/manage.py'],
    # entry_points = {'scrapy': ['settings = pwbot.settings']},
)
