
.. _overview:

========
Overview
========
**pip-rating** is an app for developers to rate the requirements of a project recursively according to
security criteria. *Do any of the dependencies have known vulnerabilities? Are they still maintained? Do they have
community support?* These are some of the questions that the app will help you answer.

Not all criteria have the same score. Some are critical, like vulnerabilities. These criteria are:

.. list-table:: Scores breakdown
   :header-rows: 1

   * - Score
     - Name
   * - +1
     - Basic info present
   * - +1
     - Source repository present
   * - +1
     - Readme present
   * - +1
     - License present
   * - +3
     - Has muliple versions
   * - +log(dependent_projects)*2
     - Dependent projects
   * - +log(dependent_repositories)
     - Dependent repositories
   * - +log(stars)/2
     - Stars
   * - +log(contributors)/2
     - Contributors
   * - From -4 to +4
     - Latest upload
   * - From max(0) to +4
     - First upload
   * - Max(0) or zero.
     - Vulnerabilities
   * - Max(0), 0 or +1
     - Package in readme

Descriptions of all these points can be found in the :ref:`scores-breakdown` section. The sum of all these points
will be the final score of the dependency. There are currently 5 points between each rating.

.. list-table:: Ratings
   :header-rows: 1

   * - Total score
     - Rating
   * - +30
     - S
   * - +25
     - A
   * - +20
     - B
   * - +15
     - C
   * - +10
     - D
   * - +5
     - E
   * - 0
     - F


.. _scores-breakdown:

Scores breakdown
----------------
Below are descriptions of all pip-rating breakdown points.

:Score: +1
:Name: *Basic info present*
:Description: The project have a description, homepage, repository link, keywords... Professional projects
              should have these indicators.

:Score: +1
:Name: *Source repository present*
:Description: The project have the repository link. Allows the community to check the source code.

:Score: +1
:Name: *Readme present*
:Description: The project have a readme file. Professional projects should have documentation.

:Score: +1
:Name: *License present*
:Description: The project have a license file. Professional projects should have a license.

:Score: +3
:Name: *Has muliple versions*
:Description: The project have more than one version. This is important because a project with only
              one version is probably not maintained and a malicious application probably will not have
              multiple versions.

:Score: +log(dependent_projects)*2
:Name: *Dependent projects*
:Description: The project have dependent projects. The projects used by the community give confidence and
              security to the life of the project.

:Score: +log(dependent_repositories)
:Name: *Dependent repositories*
:Description: The project have dependent repositories. The dependences used by the community give confidence
              and security to the life of the project.

:Score: +log(stars)/2
:Name: *Stars*
:Description: The project have stars. The stars are a good indicator of the popularity of the project.

:Score: +log(contributors)/2
:Name: *Contributors*
:Description: The project have contributors. The contributors are a good indicator of the popularity of
              the project and ensures that it will be maintained after abandonment by the main developer.

:Score: From -4 to +4
:Name: *Latest upload*
:Description: The project have a recent upload. The latest upload is a good indicator of the maintenance
              of the project. 4 months ago is +4, 6 months ago is +3, 1 year ago is +2, 1.5 years ago is
              +1, 3 years ago is 0, 4 years ago is -2. Otherwise is -4.

:Score: From max(0) to +4
:Name: *First upload*
:Description: Date of the first upload. An older project is a good indicator of a well-developed
              project. If the project has less than 15 days the max score is 0 (F), Less than 1 month is
              -3, less than 2 months is -2, less than 3 months is -1, less than half-year is 0, less than
              1 year is +1, less than 2 years is +2, less than 4 years is +3. Otherwise is +4.

:Score: Max(0) or zero.
:Name: *Vulnerabilities*
:Description: The dependency version have vulnerabilities. If the version has vulnerabilities it is
              considered critical.. If the project have vulnerabilities the score is Max(0) (F).

:Score: Max(0), 0 or +1
:Name: *Package in readme*
:Description: The dependency is mentioned in the readme. This makes it possible to ensure that the number
              of stars, contributors and more in the PyPi listing really correspond to the linked source
              page. If the package name is in the readme the score is +1. If the package name is not in the
              readme, it does not add extra points. If there is another package named in the readme, it is
              considered an impersonation and the score is Max(0) (F).

Ratings
-------
It indicates what each of the ratings probably means.

:Score: +30
:Name: *S*
:Description: The project is almost perfect. It is well maintained, has a good community and has no
              vulnerabilities.

:Score: +25
:Name: *A*
:Description: The status of the project is very good. It is well maintained, has a good community and has
              no vulnerabilities.

:Score: +20
:Name: *B*
:Description: The status of the project is good. It is well maintained, has a good community and has no
              vulnerabilities.

:Score: +15
:Name: *C*
:Description: The status of the project is not bad. It can still be improved on some points.

:Score: +10
:Name: *D*
:Description: It is recommended to review the status project.

:Score: +5
:Name: *E*
:Description: The status of the project is bad. There is probably some problem with maintenance, community,
              etc.

:Score: 0
:Name: *F*
:Description: The status of the project is very bad. Maybe there are vulnerabilities, the project is not
              maintained, etc.

The rating is calculated using the :ref:`scores-breakdown`. However, if the dependecy has a indirect dependency with
a lower rating, the rating will be lowered to the rating of the indirect dependency. For example, if the dependency
has a rating of *A*, but has an indirect dependency with a rating of *C*, the rating will be lowered to *C*. These
cases are indicated using the syntax *A* -> *C*.

Sources
-------
This project uses different sources & projects to get the information needed to calculate the score. The sources are:

* `Pipgrip <https://pypi.org/project/pipgrip/>`_. Dependency tree.
* `Libraries.io sourcerank <https://libraries.io/>`_. Dependent projects, dependent repositories, stars, basic info...
* `PyPi <https://pypi.org/>`_. Source code repository, upload dates...
* `GitHub <https://github.com/>`_. Source code readme.
* `Advisory-database <https://github.com/pypa/advisory-database>`_. Vulnerabilities. Uses the
  `pip-audit <https://pypi.org/project/pip-audit/>`_ dependency.
* `OSV <https://osv.dev/>`_. Vulnerabilities. Uses the `pip-audit <https://pypi.org/project/pip-audit/>`_ dependency.
