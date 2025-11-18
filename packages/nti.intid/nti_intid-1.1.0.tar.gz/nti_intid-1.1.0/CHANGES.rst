=========
 Changes
=========


1.1.0 (2025-11-14)
==================

- Add support for Python 3.14; drop support for Python < 3.12.
- Acquisition is an optional dependency, not installed by default.


1.0.0 (2024-11-12)
==================

- Drop support for Python < 3.10.
- Add support for Python up to 3.13.
- Use native namespace packages.


0.0.2 (2020-06-19)
==================

- Refactor tests to use ``nti.site.testing`` for DB and site management.


0.0.1 (2020-06-19)
==================

- First PyPI release.

- The weak ref classes no longer have dictionaries for arbitrary
  attributes. They never persisted arbitrary attributes.
