.. image:: https://img.shields.io/pypi/v/narration.svg
.. image:: https://img.shields.io/pypi/pyversions/narration.svg
.. image:: https://img.shields.io/pypi/status/narration.svg
.. image:: https://img.shields.io/pypi/l/narration.svg

narration
#########

Logging is easy, but setup is messy and boring in multi processes contexts, due to the various way python can spawn
processes (fork, spawn, forkserver) via explicit or implicit spawning context.

Narration handles the following logging setup boiler plate:

* main process's logger writes log record emitted by the process itself or its child processes
* child process's logger's handler forward log records to the main process only

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

* Create your loggers as you like (eg: `logging.basicConfig(...)`)
* On the master process, setup the logger to act as server:

.. code-block:: python

   import narration
   import multiprocessing
   import logging

   ctx = mutiprocessing.get_context()
   m = ctx.Manager()

   logger=logging.getLogger()
   client_handler_settings = narration.setup_server_handlers(logger=logger, ctx=ctx, ctx_manager=m)
   logger.debug("Main process ready")

   pool = multiprocessing.pool.Pool(10, child_process_worker_function, [client_handler_settings] , 2, ctx)


* On the child process, setup the logger to act as 'emitting' client:

.. code-block:: python

   import narration
   import multiprocessing
   import logging

   # Child process must receive the 'client_handler_settings' payload when starting the process

   # Re-create a logger, replacing handlers/formatting (if any) with handler to forrward records to the master process
   logger=logging.getLogger()
   narration.setup_client_handlers(logger=logger, handler_name_to_client_handler_settings=client_handler_settings)
   logger.debug("Child process ready")


* Child process log records will be sent to the master process's logger's original handlers for procesing.

.. code-block::

   Main process ready
   Child process ready

