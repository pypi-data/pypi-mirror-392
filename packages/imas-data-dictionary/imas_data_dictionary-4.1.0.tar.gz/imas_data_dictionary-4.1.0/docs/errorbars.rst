.. _`errorbars`:

Quantities with error bars
==========================

For some quantities in the data dictionary you can store the error bars in an IDS as
well. This is indicated by a **⇹** symbol in the :ref:`reference`.

When a quantity ``<data>`` supports errorbars, three additional quantities exist in the
IDS:

1.  ``<data>_error_upper``
2.  ``<data>_error_lower``
3.  ``<data>_error_index``

    .. deprecated:: 3.39.0
        The ``<data>_error_index`` elements are obsolescent.

The upper and lower errors are absolute and positive, and represent one standard
deviation of the data. The effective values of the data (within one standard deviation)
are in the interval :code:`[<data> - <data>_error_lower, <data> + <data>_error_upper]`.

.. important::

    When the errors are symmetrical, ``<data>_error_lower`` may be empty and
    ``<data>_error_upper`` represents both the upper and lower error.


Example
-------

:dd:node:`global_quantities/ip <core_profiles/global_quantities/ip>` in the
:dd:ids:`core_profiles` IDS has error bar nodes ``global_quantities/ip_error_upper``
and ``global_quantities/ip_error_lower``.
