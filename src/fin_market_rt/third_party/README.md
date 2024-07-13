# Purpose

Contains third-party dependencies that were incorporated into the codebase to
avoid having "unsafe" dependency.

Each subdirectory of this directory
- should be named after the project
- should contain README.md, with a link to the original project
- should contain LICENSE.txt from the original project

NOTE: The company's strategy is to use production-ready, standard, well adopted
technologies. In some cases there is no such well adopted solution, and we don't
want to have a not supported dependency. In such situations, when the package is
not big code-wise, we can incorporate the project into our own codebase. To
avoid compliance and licensing issues, we want to put them in a separate
directory, preserving the licensing info. and original code structure. This
directory provides a solution for such situation.
