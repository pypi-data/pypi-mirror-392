aws-enumerateiam
================

Enumerate IAM permissions by calling ``aws:List*`` and ``aws:Get*`` APIs.

This project has been created to help AWS users to identify which actions are allowed and which are denied by IAM policies.

This project can be used both as a Python library and as a command line tool.

Installation
------------

Install using pip:

.. code-block:: console

    $ pip install aws-enumerateiam

Usage (CLI)
-----------

To enumerate the allowed IAM permissions using the command line tool:

.. code-block:: console

    $ enumerate-iam

Usage (Python library)
----------------------

To use ``enumerate-iam`` as a Python library:

.. code-block:: python

    from enumerate_iam import permissions

    allowed, denied = permissions()

Internals
---------

The library uses a list of AWS API actions (e.g. ``ec2:DescribeInstances``), and then it attempts to call them.

If AWS returns an error that indicates the action is not allowed, it will be added to the *denied* list. If the call succeeds (or fails with a different error), it is considered *allowed*.

Failure Modes
-------------

Sometimes API calls fail with errors that do not indicate an IAM permission problem. In those cases the action is not added to the *denied* list.

For example, calling ``ec2:DescribeInstances`` without any EC2 instances may return an empty list rather than an error.

License
-------

This project is released under the BSD license.
