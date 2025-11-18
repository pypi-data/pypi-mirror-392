.. _`data types`:

Data types
==========

The Data Dictionary indicates a strict data type for each node in an IDS. 

.. note::

    Please check the :ref:`Access Layer documentation <AL docs>` for more
    information how these data types map to the programming language that you
    use.


Structural data types
---------------------

.. dd:data_type:: structure

    A structure node.

.. dd:data_type:: AoS

    An array of structures node.


Textual data types
------------------

.. dd:data_type:: STR_0D

    Text (character strings).

.. dd:data_type:: STR_1D

    Array of strings.


Integer data types
------------------

.. dd:data_type:: INT_0D

    A 32-bit signed integer. Can store values in the range
    :math:`\left[-2^{31}, 2^{31}-1\right]`.

.. dd:data_type:: INT_1D

    A 1-dimensional array of 32-bit signed integers.

.. dd:data_type:: INT_2D

    A 2-dimensional array of 32-bit signed integers.

.. dd:data_type:: INT_3D
    
    A 3-dimensional array of 32-bit signed integers.


Floating point data types
-------------------------

.. dd:data_type:: FLT_0D

    A 64-bit floating point number. See `double-precision floating-point format
    (Wikipedia)
    <https://en.wikipedia.org/wiki/Double-precision_floating-point_format>`_ for
    more details.

.. dd:data_type:: FLT_1D

    A 1-dimensional array of 64-bit floating point numbers.

.. dd:data_type:: FLT_2D

    A 2-dimensional array of 64-bit floating point numbers.

.. dd:data_type:: FLT_3D
    
    A 3-dimensional array of 64-bit floating point numbers.

.. dd:data_type:: FLT_4D
    
    A 4-dimensional array of 64-bit floating point numbers.

.. dd:data_type:: FLT_5D
    
    A 5-dimensional array of 64-bit floating point numbers.

.. dd:data_type:: FLT_6D
    
    A 6-dimensional array of 64-bit floating point numbers.  


Complex number data types
-------------------------

.. dd:data_type:: CPX_0D

    A complex number, consisting of two 64-bit floating point numbers: one for
    the real, and one for the imaginary component of the complex number.

.. dd:data_type:: CPX_1D

    A 1-dimensional array of complex numbers.

.. dd:data_type:: CPX_2D

    A 2-dimensional array of complex numbers.

.. dd:data_type:: CPX_3D
    
    A 3-dimensional array of complex numbers.

.. dd:data_type:: CPX_4D
    
    A 4-dimensional array of complex numbers.

.. dd:data_type:: CPX_5D
    
    A 5-dimensional array of complex numbers.

.. dd:data_type:: CPX_6D
    
    A 6-dimensional array of complex numbers.  



