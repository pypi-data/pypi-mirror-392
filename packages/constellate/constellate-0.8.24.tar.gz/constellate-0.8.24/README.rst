.. image:: https://img.shields.io/pypi/v/constellate.svg
.. image:: https://img.shields.io/pypi/pyversions/constellate.svg
.. image:: https://img.shields.io/pypi/status/constellate.svg
.. image:: https://img.shields.io/pypi/l/constellate.svg

constellate
###########

Like a constellation, this package aggregates various utilities built over time.

Installation
************

Install python virtual envs needed by tox/IDE
---------------------------------------------

.. code-block::

    bash make.sh --setup-python-dev-envs


.. code-block::

    bash make.sh --install-dependencies
    bash make.sh --install-tests-dependencies


Usage
*****

Run tests (locally)
--------------------

.. code-block::

  POSTGRES_USER=test;POSTGRES_PASSWORD=not_needed bash make.sh --destroy-database --run-database --run-tests

Lint
--------------------

.. code-block::

  bash make.sh --lint
