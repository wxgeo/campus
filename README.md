
Campus
======

Rational
--------
As a teacher, I frequenly share documents with my students, often using Moodle or an other learning platform.
Often, students find a small error here or there in a document.
While it's easy to quicky fix it, updating the document on the learning platform is often unecessary slow, involving many steps.
Updating or adding a document should be an almost immediate process as well.

Campus aims to fix this.

One of the idea of campus is that a filesystem is already used to organize content.
Adding an index.md file in each folder is sufficient to specify which files I want to share with my students, and to add a few notes too.
The course is also indexed in git, for file versioning.
Campus then convert the file hierarchy and index.md files into a static website, which may be hosted on github, gitlab or bitbucket pages...

Every time some content change, calling `campus publish` is enough to commit changes and update the website online.


Installation
------------
Campus use `git`, so you must install `git` first.

Then, to install Campus, execute the following:

    $ wget https://github.com/wxgeo/campus/archive/refs/heads/master.zip
    $ cd campus-master
    $ pip install .

    
First use
---------
Suppose all the content you want to share is in `~/my-course`.

First, you need to initialize this directory:

    $ cd ~/my-course
    $ campus init

This will do the following:
    - Make `my-course` a git repository (if it wasn't already)
    - Create a `~/my-course/.config` folder, with css stylesheets and pictures that you may edit.
    - Create a `~/my-course/.www` folder, which will also be a git repository.
      Don't edit its content, as everything except `.www/.git` will be erased and regenerated at every update.
    - Create an empty `~/my-course/index.md` file, which will be your website main entry point.
    
This an simple example of `index.md` file:

    #Python course for beginners
    
    This course is intended for beginners who wishes to learn the Python programming language. 
    
    [Introduction to Python](intro.pdf)
    
    [Functional programming](func-programming)
    
    The following optional part will introduce you to object oriented programming.
    
    [Object oriented programming](oo-programming)
    
To generate a website in `~/my-course/.www`, just execute:
    
    $ campus make
    
Then, you'll have to configure both git repositories, ie. `~/my-course` and `~/my-course/.www`, so that running `git push` will push your master branch upstream.

For `~/my-course/.www`, see github pages, gitlab pages or bitbucket pages documentation to see how to publish a static website.
   
Usage
-----
Once this has been done, for every content change, you'll now just have to execute:

    $ cd ~/my-course
    $ campus push
    
It will automatically call `campus make` and then push your changes online.

