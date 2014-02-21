dtcli
=====

A simple command line interface to django templates. 

### Additional tags

This project implements two additional tags. You can load them using:

    {% load dtcli %}

#### minify

This tag will minify files before including them into the template. It ads additional type parameter which you should use when you don't use .css or .js file endings.

Example:

    {% load dtcli %}
    <html>
    <head>
        <style type="text/css">
            {% minify "example.css" %}
        </style>
        <script type="text/javascript">
            {% minify "script-filename" type=js %}
        </script>
    </head>
    </html>
    

#### less

This tag will compile the file with lessc, before including it to the template. You will have to install node and lessc for this tag to work. Less PATH includes all directories that are set as template paths via -d option.

Example:

    {% load dtcli %}
    <html>
    <head>
        <style type="text/css">
            {% less "example.less" %}
        </style>
        <script type="text/javascript">
            {% minify "script-filename" type=js %}
        </script>
    </head>
    </html>


Installing
----------

    pip install django
    pip install minify
    pip install git+https://github.com/Zemanta/dtcli
    
For lessc to work you will have to install nodejs and lessc.

Usage
-----

You can check out the example in project's example/ directory.

    cd example
    dtcli example.html

Results are built in build/ directory by default.

