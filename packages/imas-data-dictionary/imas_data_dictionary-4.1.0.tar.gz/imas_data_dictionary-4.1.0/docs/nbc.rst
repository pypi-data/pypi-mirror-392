Non-backwards compatible changes
================================

As the data dictionary evolves, sometimes Non-backwards Compatible Changes (NBCs) are
introduced. Currently there are two types of NBCs which are documented:

1.  Renames of :dd:data_type:`structure`\ s, :dd:data_type:`AoS`\ s or data
    nodes. For example, :dd:node:`reflectometer_profile/position/r` was renamed in
    version 3.23.3, the original name was ``position/r/data``.
2.  Change of data type. For example,
    :dd:node:`spectrometer_visible/channel/filter_spectrometer/radiance_calibration`
    changed from :dd:data_type:`FLT_0D` to :dd:data_type:`FLT_1D` in version 3.39.0.
