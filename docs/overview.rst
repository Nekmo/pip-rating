
.. _overview:

========
Overview
========
**Requirements-rating** is an app for developers to rate the requirements of a project recursively according to
security criteria. *Do any of the dependencies have known vulnerabilities? Are they still maintained? Do they have
community support?* These are some of the questions that the app will help you answer.

Not all criteria have the same score. Some are critical, like vulnerabilities. These criteria are:

.. list-table:: Scores breakdown
   :header-rows: 1
   :widths: 25 25 50

   * - Score
     - Name
     - Description
   * - +1
     - Basic info present
     - The project have a description, homepage, repository link, keywords... Professional projects
       should have these indicators.
   * - +1
     - Source repository present
     - The project have the repository link. Allows the community to check the source code.
   * - +1
     - Readme present
     - The project have a readme file. Professional projects should have documentation.
   * - +1
     - License present
     - The project have a license file. Professional projects should have a license.
   * - +3
     - Has muliple versions
     - The project have more than one version. This is important because a project with only
       one version is probably not maintained and a malicious application probably will not have
       multiple versions.
   * - +log(dependent_projects)*2
     - Dependent projects
     - The project have dependent projects. The projects used by the community give confidence and
       security to the life of the project.
   * - +log(dependent_repositories)
     - Dependent repositories
     - The project have dependent repositories. The dependences used by the community give confidence
       and security to the life of the project.
   * - +log(stars)/2
     - Stars
     - The project have stars. The stars are a good indicator of the popularity of the project.
   * - +log(contributors)/2
     - Contributors
     - The project have contributors. The contributors are a good indicator of the popularity of
       the project and ensures that it will be maintained after abandonment by the main developer.
   * - From -4 to +4
     - Latest upload
     - The project have a recent upload. The latest upload is a good indicator of the maintenance
       of the project. 4 months ago is +4, 6 months ago is +3, 1 year ago is +2, 1.5 years ago is
       +1, 3 years ago is 0, 4 years ago is -2. Otherwise is -4.
   * - From max(0) to +4
     - First upload
     - Date of the first upload. An older project is a good indicator of a well-developed
       project. If the project has less than 15 days the max score is 0 (F), Less than 1 month is
       -3, less than 2 months is -2, less than 3 months is -1, less than half-year is 0, less than
       1 year is +1, less than 2 years is +2, less than 4 years is +3. Otherwise is +4.
   * - Max(0) or zero.
     - Vulnerabilities
     - The dependency version have vulnerabilities. If the version has vulnerabilities it is
       considered critical.. If the project have vulnerabilities the score is Max(0) (F).
   * - Max(0), 0 or +1
     - Package in readme
     - The dependency is mentioned in the readme. This makes it possible to ensure that the number
       of stars, contributors and more in the PyPi listing really correspond to the linked source
       page. If the package name is in the readme the score is +1. If the package name is not in the
       readme, it does not add extra points. If there is another package named in the readme, it is
       considered an impersonation and the score is Max(0) (F).
