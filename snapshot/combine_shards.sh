echo "area_swept_km2"
python combine_shards.py $BUCKET_NAME area_swept_km2
[ $? -ne 0 ] && exit $?

echo "bottom_temperature_c"
python combine_shards.py $BUCKET_NAME bottom_temperature_c
[ $? -ne 0 ] && exit $?

echo "common_name"
python combine_shards.py $BUCKET_NAME common_name
[ $? -ne 0 ] && exit $?

echo "count"
python combine_shards.py $BUCKET_NAME count
[ $? -ne 0 ] && exit $?

echo "cpue_kgkm2"
python combine_shards.py $BUCKET_NAME cpue_kgkm2
[ $? -ne 0 ] && exit $?

echo "cpue_nokm2"
python combine_shards.py $BUCKET_NAME cpue_nokm2
[ $? -ne 0 ] && exit $?

echo "date_time"
python combine_shards.py $BUCKET_NAME date_time
[ $? -ne 0 ] && exit $?

echo "depth_m"
python combine_shards.py $BUCKET_NAME depth_m
[ $? -ne 0 ] && exit $?

echo "distance_fished_km"
python combine_shards.py $BUCKET_NAME distance_fished_km
[ $? -ne 0 ] && exit $?

echo "duration_hr"
python combine_shards.py $BUCKET_NAME duration_hr
[ $? -ne 0 ] && exit $?

echo "latitude_dd_end"
python combine_shards.py $BUCKET_NAME latitude_dd_end
[ $? -ne 0 ] && exit $?

echo "latitude_dd_start"
python combine_shards.py $BUCKET_NAME latitude_dd_start
[ $? -ne 0 ] && exit $?

echo "longitude_dd_end"
python combine_shards.py $BUCKET_NAME longitude_dd_end
[ $? -ne 0 ] && exit $?

echo "longitude_dd_start"
python combine_shards.py $BUCKET_NAME longitude_dd_start
[ $? -ne 0 ] && exit $?

echo "net_height_m"
python combine_shards.py $BUCKET_NAME net_height_m
[ $? -ne 0 ] && exit $?

echo "net_width_m"
python combine_shards.py $BUCKET_NAME net_width_m
[ $? -ne 0 ] && exit $?

echo "scientific_name"
python combine_shards.py $BUCKET_NAME scientific_name
[ $? -ne 0 ] && exit $?

echo "species_code"
python combine_shards.py $BUCKET_NAME species_code
[ $? -ne 0 ] && exit $?

echo "srvy"
python combine_shards.py $BUCKET_NAME srvy
[ $? -ne 0 ] && exit $?

echo "station"
python combine_shards.py $BUCKET_NAME station
[ $? -ne 0 ] && exit $?

echo "stratum"
python combine_shards.py $BUCKET_NAME stratum
[ $? -ne 0 ] && exit $?

echo "surface_temperature_c"
python combine_shards.py $BUCKET_NAME surface_temperature_c
[ $? -ne 0 ] && exit $?

echo "survey"
python combine_shards.py $BUCKET_NAME survey
[ $? -ne 0 ] && exit $?

echo "taxon_confidence"
python combine_shards.py $BUCKET_NAME taxon_confidence
[ $? -ne 0 ] && exit $?

echo "vessel_id"
python combine_shards.py $BUCKET_NAME vessel_id
[ $? -ne 0 ] && exit $?

echo "vessel_name"
python combine_shards.py $BUCKET_NAME vessel_name
[ $? -ne 0 ] && exit $?

echo "weight_kg"
python combine_shards.py $BUCKET_NAME weight_kg
[ $? -ne 0 ] && exit $?

echo "year"
python combine_shards.py $BUCKET_NAME year
[ $? -ne 0 ] && exit $?

echo "Done with combine shards."
