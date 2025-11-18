Manager
=======

The Manager is the high-level entry point for most users.
It wraps an authenticated ``ApiClient`` and offers helper methods
that reduce boilerplate when running avatarizations.

Why use the Manager?
--------------------

* Single place to authenticate.
* Shortcuts to create a ``Runner`` and load YAML configs.
* Convenience helpers to inspect recent jobs / results.

Quick example
-------------

**Using username/password authentication:**

.. code-block:: python

   from avatars import Manager
   manager = Manager(base_url="https://your.instance/api")
   manager.authenticate(username="user", password="pass")
   runner = manager.create_runner(set_name="demo")
   runner.add_table("wbcd", "fixtures/wbcd.csv")
   runner.set_parameters("wbcd", k=15)
   runner.run()

**Using API key authentication:**

.. code-block:: python

   from avatars import Manager
   # No need to call authenticate() when using an API key
   manager = Manager(base_url="https://your.instance/api", api_key="your-api-key")
   runner = manager.create_runner(set_name="demo")
   runner.add_table("wbcd", "fixtures/wbcd.csv")
   runner.set_parameters("wbcd", k=15)
   runner.run()

.. note::
   When using API key authentication, do not call ``authenticate()``.
   The API key is set during initialization and is immediately active.

Detailed reference
------------------

.. automodule:: avatars.manager
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:
