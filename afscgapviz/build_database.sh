# Script to build a sqlite database with geohashed presence information.
# 
# (c) 2023 Regents of University of California / The Eric and Wendy Schmidt
# Center for Data Science and the Environment at UC Berkeley.
#
# This file is part of afscgap released under the BSD 3-Clause License. See
# LICENSE.txt.

python3 build_database.py create_db geohashes.db
python3 build_database.py download 2000-2023 geohashes.db 4

# The following is only needed if you are building for the web viz app.
cat sql/create_availability.sql | sqlite3 geohashes.db
