"""
Shared constants for flat file snapshot scripts.

(c) 2025 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.md.
"""
REQUIRES_ROUNDING = {
    'latitude_dd_start',
    'longitude_dd_start',
    'latitude_dd_end',
    'longitude_dd_end',
    'bottom_temperature_c',
    'surface_temperature_c',
    'depth_m',
    'distance_fished_km',
    'duration_hr',
    'net_width_m',
    'net_height_m',
    'area_swept_km2',
    'cpue_kgkm2',
    'cpue_nokm2',
    'weight_kg',
}

REQUIRES_DATE_ROUND = {'date_time'}

ZEROABLE_FIELDS = ['cpue_kgkm2', 'cpue_nokm2', 'weight_kg', 'count']

REQUIRES_FLAT = {
    'performance',
    'cruise',
    'cruisejoin',
    'hauljoin',
    'haul'
}

IGNORE_ZEROS = {
    'species_code',
    'scientific_name',
    'common_name'
}

RETRY_DELAY = 60
