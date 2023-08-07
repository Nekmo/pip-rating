
.. _github_action:

=============
GitHub Action
=============

You can use pip-rating in your Github project without installing anything. You just need to add a Github action.
First you need to create the ``.github/workflows/pip-rating.yml`` file in your project:

.. code-block:: yaml

    # .github/workflows/pip-rating.yml
    # --------------------------------
    name: Pip-rating

    on:
      push:
        branches:
          - master
      schedule:
        - cron: '0 0 * * SUN'

    jobs:
      build:
        runs-on: ubuntu-latest
        permissions: write-all
        steps:
          - uses: actions/checkout@v2
          - name: Run pip-rating
            uses: Nekmo/pip-rating@master
            with:
              create_badge: true
              badge_style: flat-square
              badge_branch: pip-rating-badge

This action will be executed with **every commit to branch master** and **every Sunday**. The action has the following
parameters available in the with section:

* ``file``: Path to the requirements file. Optional. By default, it will detect the requirements file in the root of
  the project. You should set this parameter if your requirements file does not have a standard name or is in another
  path.
* ``file_type``: Type of the requirements file. Optional. By default, it will detect the type of the requirements file.
* ``format``: Output format. Available formats: *text, tree, json, only-rating & badge*. Optional. By default, it will
  use the *text* format.
* ``ignore_packages``: Packages to ignore separated by spaces. Optional.
* ``create_badge``: Create a badge with the rating. Optional. By default, it will not create the badge.
* ``badge_path``: Path to the badge. Optional. By default, it will use the ``pip-rating-badge.svg`` file in the root
  of the project.
* ``badge_branch``: Branch where the badge will be pushed. Optional. By default, it will use current branch. It is
  highly recommended to set this parameter.
* ``badge_style``: Badge style. Optional. By default, it will use the *flat* style. Available styles: *flat,
  flat-square, & for-the-badge*.
* ``badge_s_color``: Badge color for S rating. Optional.
* ``badge_a_color``: Badge color for A rating. Optional.
* ``badge_b_color``: Badge color for B rating. Optional.
* ``badge_c_color``: Badge color for C rating. Optional.
* ``badge_d_color``: Badge color for D rating. Optional.
* ``badge_e_color``: Badge color for E rating. Optional.
* ``badge_f_color``: Badge color for F rating. Optional.

Some examples of the different badge styles:

.. list-table:: Badge examples
   :widths: 50 50
   :header-rows: 1

   * - Name
     - Example
   * - ``flat``
     - .. image:: images/badge_flat_S.svg
   * - ``flat-square``
     - .. image:: images/badge_flat_square_S.svg
   * - ``for-the-badge``
     - .. image:: images/badge_for_the_badge_S.svg

If you have activated the badge, you can display it in your README using the following *rst* code:

.. code-block:: rst

    .. image:: https://raw.githubusercontent.com/<owner>/<repository>/<badge_branch>/<badge_path>
      :target: https://github.com/<owner>/<repository>/actions/workflows/<action_filename>
      :alt: pip-rating badge

For example:

.. code-block:: rst

    .. image:: https://raw.githubusercontent.com/Nekmo/pip-rating/pip-rating-badge/pip-rating-badge.svg
      :target: https://github.com/Nekmo/pip-rating/actions/workflows/pip-rating.yml
      :alt: pip-rating badge

If you are using *markdown*:

.. code-block:: markdown

    [![pip-rating badge](https://raw.githubusercontent.com/<owner>/<repository>/<badge_branch>/<badge_path>)](https://github.com/<owner>/<repository>/actions/workflows/<action_filename>)

For example:

.. code-block:: markdown

    [![pip-rating badge](https://raw.githubusercontent.com/Nekmo/pip-rating/pip-rating-badge/pip-rating-badge.svg)](https://github.com/Nekmo/pip-rating/actions/workflows/pip-rating.yml)

You can see the result of the execution in the *"Actions"* tab of your repository.
