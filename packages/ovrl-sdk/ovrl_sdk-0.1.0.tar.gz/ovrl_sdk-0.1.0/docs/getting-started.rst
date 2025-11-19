Getting started
===============

Installation
------------

.. code-block:: console

   pip install ovrl-sdk

For local development:

.. code-block:: console

   pip install -e .[dev]

Configuration
-------------

Set these environment variables before running the examples or your own scripts.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Variable
     - Purpose
   * - ``OVRL_SECRET``
     - Primary secret key that signs transactions.
   * - ``OVRL_DESTINATION``
     - Destination account for payment flows.
   * - ``OVRL_NETWORK``
     - Optional; ``PUBLIC`` / ``TESTNET`` / ``FUTURENET``.
   * - ``OVRL_CONTRACT_ID``
     - Soroban token contract identifier for advanced flows.

See ``examples/shared.py`` for a helper that validates the configuration and
lazily loads Friendbot funding when available.

Bootstrap an account
--------------------

.. literalinclude:: ../examples/bootstrap_trustline.py
   :language: python
   :linenos:

The script:

#. Funds an account via Friendbot (or a sponsor secret).
#. Establishes the OVRL trustline.
#. Returns an ``AccountStatus`` summary with balances and trustline info.

Next steps
----------

* Browse the :doc:`api` reference for low-level helpers.
* Explore ``examples/`` for payments, quoting, monitoring, and Soroban flows.
* Enable :mod:`sphinx.ext.autodoc` in your own docs to reuse these docstrings.
