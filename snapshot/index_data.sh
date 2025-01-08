mkdir index_shards

echo "area_swept_km2"
python generate_indicies.py $BUCKET_NAME area_swept_km2 n
[ $? -ne 0 ] && exit $?

echo "bottom_temperature_c"
python generate_indicies.py $BUCKET_NAME bottom_temperature_c n
[ $? -ne 0 ] && exit $?

echo "common_name"
python generate_indicies.py $BUCKET_NAME common_name n
[ $? -ne 0 ] && exit $?

echo "count"
python generate_indicies.py $BUCKET_NAME count n
[ $? -ne 0 ] && exit $?

echo "cpue_kgkm2"
python generate_indicies.py $BUCKET_NAME cpue_kgkm2 n
[ $? -ne 0 ] && exit $?

echo "cpue_nokm2"
python generate_indicies.py $BUCKET_NAME cpue_nokm2 n
[ $? -ne 0 ] && exit $?

echo "date_time"
python generate_indicies.py $BUCKET_NAME date_time n
[ $? -ne 0 ] && exit $?

echo "depth_m"
python generate_indicies.py $BUCKET_NAME depth_m n
[ $? -ne 0 ] && exit $?

echo "distance_fished_km"
python generate_indicies.py $BUCKET_NAME distance_fished_km n
[ $? -ne 0 ] && exit $?

echo "duration_hr"
python generate_indicies.py $BUCKET_NAME duration_hr n
[ $? -ne 0 ] && exit $?

echo "latitude_dd_end"
python generate_indicies.py $BUCKET_NAME latitude_dd_end n
[ $? -ne 0 ] && exit $?

echo "latitude_dd_start"
python generate_indicies.py $BUCKET_NAME latitude_dd_start n
[ $? -ne 0 ] && exit $?

echo "longitude_dd_end"
python generate_indicies.py $BUCKET_NAME longitude_dd_end n
[ $? -ne 0 ] && exit $?

echo "longitude_dd_start"
python generate_indicies.py $BUCKET_NAME longitude_dd_start n
[ $? -ne 0 ] && exit $?

echo "net_height_m"
python generate_indicies.py $BUCKET_NAME net_height_m n
[ $? -ne 0 ] && exit $?

echo "net_width_m"
python generate_indicies.py $BUCKET_NAME net_width_m n
[ $? -ne 0 ] && exit $?

echo "scientific_name"
python generate_indicies.py $BUCKET_NAME scientific_name n
[ $? -ne 0 ] && exit $?

echo "species_code"
python generate_indicies.py $BUCKET_NAME species_code n
[ $? -ne 0 ] && exit $?

echo "srvy"
python generate_indicies.py $BUCKET_NAME srvy n
[ $? -ne 0 ] && exit $?

echo "station"
python generate_indicies.py $BUCKET_NAME station n
[ $? -ne 0 ] && exit $?

echo "stratum"
python generate_indicies.py $BUCKET_NAME stratum n
[ $? -ne 0 ] && exit $?

echo "surface_temperature_c"
python generate_indicies.py $BUCKET_NAME surface_temperature_c n
[ $? -ne 0 ] && exit $?

echo "survey"
python generate_indicies.py $BUCKET_NAME survey n
[ $? -ne 0 ] && exit $?

echo "taxon_confidence"
python generate_indicies.py $BUCKET_NAME taxon_confidence n
[ $? -ne 0 ] && exit $?

echo "vessel_id"
python generate_indicies.py $BUCKET_NAME vessel_id n
[ $? -ne 0 ] && exit $?

echo "vessel_name"
python generate_indicies.py $BUCKET_NAME vessel_name n
[ $? -ne 0 ] && exit $?

echo "weight_kg"
python generate_indicies.py $BUCKET_NAME weight_kg n
[ $? -ne 0 ] && exit $?

echo "year"
python generate_indicies.py $BUCKET_NAME year y
[ $? -ne 0 ] && exit $?

echo "Done with indexing data."
