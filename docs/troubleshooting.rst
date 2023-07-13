Troubleshooting
===============

What is pip rating used for?
----------------------------
Pip-rating is useful in many different scenarios:

* Avoid introducing potentially malicious dependencies into your application.
* Compare dependencies based on criteria such as community or age.
* Monitor if your dependencies are no longer supported.
* Check if there are vulnerabilities in any of your dependencies.
* Check all your dependencies and their state as a tree.

Pip-rating can analyze the dependencies file of a library, a project, or a specific package.

What is the idea behind this project?
-------------------------------------
The idea for this project came from `this great XKCD comic <https://xkcd.com/2347/>`_:

.. image:: dependency.png
    :target: https://xkcd.com/2347/
    :align: center
    :alt: Dependency - from the XKCD comic 2347

The author of this comic is **Randall Munroe** from `XKCD <https://xkcd.com/>`_.

Why does my package have a low rate?
------------------------------------
Pip-rating determines the score based on two main criteria:

* The scoring criteria described in :ref:`scores-breakdown`.
* The rating of the package's dependencies. Your package rating cannot exceed the rating of its dependencies. That is,
  your package's score is limited by your dependencies.

In the last point, it is indicated with the syntax ``Original rating -> new rating``. For example: ``A -> C``. In this
example, ``A`` is your original score and ``C`` the new rating after apply this limitation.

You can see the analysis of your package in more detail using::

    $ pip-rating analyze-package <your-package-name>

Please note that pip-rating uses open source such as Github. Pip-rating may not detect your source, and some scores may
not add up to your rating.

I am having errors with Pip-rating. How can I report them?
----------------------------------------------------------
You can report it on `the issues page on Github <https://github.com/Nekmo/pip-rating/issues>`_. Before reporting, check
that is a Pip-rating error and that is not duplicated. To make it easier to close the bug, add as much information
possible.
