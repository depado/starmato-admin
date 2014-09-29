import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

print find_packages()

setup(
    name='starmato-admin',
    version='0.1',
    packages=find_packages(),
    package_data={
        'starmato.admin': [
            'templates/admin/*', 
            'templates/admin/edit_inline/*', 
            'templates/admin/includes/*', 
            'media/admin/js/*', 
            'media/admin/css/*', 
            'media/admin/images/*', 
            'locale/fr_FR/LC_MESSAGES/*'
        ],
    },
    license='MIT',
    description='A Django app to upgrade django admin.',
    long_description=README,
    url='http://www.go-tsunami.com/',
    author='GoTsunami',
    author_email='ab@go-tsunami.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
