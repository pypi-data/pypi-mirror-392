======================
NEWS for rabbitfixture
======================

0.5.3 (2025-11-14)
==================

- No code changes. Only changes to the project and package setup.

0.5.3 (2022-09-07)
==================

- Set ``RABBITMQ_CTL_DIST_PORT_MIN`` and ``RABBITMQ_CTL_DIST_PORT_MAX``
  environment variables, as otherwise ``rabbitmqctl`` starts this port range
  at ``RABBITMQ_DIST_PORT`` + 10000, which may exceed 65535.

0.5.2 (2022-08-01)
==================

- Only send ``SIGTERM`` once while stopping ``RabbitServerRunner``, since
  it's sent to the whole process group and that can itself interfere with
  the shutdown process if we send it frequently and repeatedly.
- Fix ignoring of ``ESRCH`` errors in ``RabbitServerRunner._signal``.

0.5.1 (2022-07-22)
==================

- Ignore ``ESRCH`` errors in ``RabbitServerRunner._signal``, since this can
  happen if the server process exits by itself just before we try to signal
  it.

0.5.0 (2021-02-02)
==================

- Add tox testing support and drop buildout.
- Fix ``test_stop_hang`` failure introduced in 0.4.2.
- Handle ``SIGCHLD`` while stopping the ``RabbitServerRunner`` fixture,
  since the ``rabbitmq-server`` process we're trying to stop is our direct
  child process.
- Fix ``ResourceWarning`` on Python 3 if
  ``RabbitServerEnvironment.rabbitctl`` times out.
- Handle new format of ``rabbitmqctl status`` output in RabbitMQ 3.7.0.

0.4.2 (2019-08-23)
==================

- Allow changing the default server control timeout.
- Use a PEP 508 environment marker for the ``subprocess32`` dependency.

0.4.1 (2019-03-28)
==================

- Adjust ``status_regex`` to cope with removed ellipsis in rabbitmq-server
  3.6.10 (https://bugs.launchpad.net/rabbitfixture/+bug/1817642).
- Use ``RABBITMQ_ENABLED_PLUGINS_FILE`` to disable all plugins
  (https://bugs.launchpad.net/rabbitfixture/+bug/1817640).

0.4.0 (2018-05-08)
==================

- Port to amqp.
- Add Python 3 support.

0.3.8 (2016-09-05)
==================

- Export the ``RABBITMQ_ENABLED_PLUGINS_FILE`` environment variable and make
  it point to ``/dev/null`` by default.

0.3.7 (2016-05-31)
==================

- Fix buildout no longer working with latest dependency versions.
- Fix hang in ``test_stop_hang`` unit tests.
- Move the kill code into a new ``RabbitServerRunner.kill`` API.

0.3.6 (2015-04-24)
==================

- Apply a timeout to all ``rabbitmqctl`` calls to work around occasional
  hangs on stop.

0.3.5 (2014-05-29)
==================

- Allocate a port for ``RABBITMQ_DIST_PORT``, which is related to clustering
  in RabbitMQ >= 3.3
  (https://bugs.launchpad.net/rabbitfixture/+bug/1322868).

0.3.4 (2013-09-16)
==================

- Get the development environment working in Ubuntu 13.04.
- Fix port reuse issues when restarting the fixture
  (https://bugs.launchpad.net/rabbitfixture/+bug/1225980).

0.3.3 (2012-05-15)
==================

- Remove ``RabbitServerResource.tearDown``.  It was never being called, and
  is not needed anyway
  (https://bugs.launchpad.net/rabbitfixture/+bug/847889).

0.3.2 (2011-09-29)
==================

- Handle the fixture lifecycle entirely in ``test_start_check_shutdown``
  (https://bugs.launchpad.net/rabbitfixture/+bug/851813).
- Be more flexible when parsing ``rabbitmqctl status`` output.
- Raise better error messages if rabbit fails to start.

0.3.1 (2011-09-09)
==================

- Fix ``RabbitServerResources`` reuse by reapplying the defaults each time
  (potentially setting things back to None, to let them be reallocated).
- Use a custom ``RABBITMQ_PLUGINS_DIR``, so the fixture server doesn't load
  plugins that might cause port conflicts.
- Adjust ``rabbitmqctl status`` regex to cope with rabbitmq 2.5.

0.3 (2011-07-05)
================

- Make ``RabbitServerResources`` configurable so that users have more
  control over the resources that the fixture makes use of.

0.2.1 (2011-07-05)
==================

- Depend on setuptools.

0.2 (2011-07-05)
================

- Remove the Launchpad-specific ``service_config``.

0.1 (2011-06-30)
================

- Initial release.
