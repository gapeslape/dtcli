dtcql
=====

A simple command line interface to django templates. 

Additionaly this project implements minify tag that extends include tag. minify
tag will minify files before including them into the template.

Installing
----------

pip install django
pip install minify
git clone https://github.com/zemanta/dtcli.git
cd dtcli
python setup.py install

Usage
-----

You can check out the example in example directory.

cd example
dtcli example.html

Results are built in build directory by default.

