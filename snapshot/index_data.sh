mkdir index_shards
echo "area_swept_km2"
python generate_indicies.py $BUCKET_NAME area_swept_km2 n
echo "bottom_temperature_c"
python generate_indicies.py $BUCKET_NAME bottom_temperature_c n
echo "common_name"
python generate_indicies.py $BUCKET_NAME common_name n
echo "count"
python generate_indicies.py $BUCKET_NAME count n
echo "cpue_kgkm2"
python generate_indicies.py $BUCKET_NAME cpue_kgkm2 n
echo "cpue_nokm2"
python generate_indicies.py $BUCKET_NAME cpue_nokm2 n
echo "cruise"
python generate_indicies.py $BUCKET_NAME cruise n
echo "cruisejoin"
python generate_indicies.py $BUCKET_NAME cruisejoin n
echo "date_time"
python generate_indicies.py $BUCKET_NAME date_time n
echo "depth_m"
python generate_indicies.py $BUCKET_NAME depth_m n
echo "distance_fished_km"
python generate_indicies.py $BUCKET_NAME distance_fished_km n
echo "duration_hr"
python generate_indicies.py $BUCKET_NAME duration_hr n
echo "haul"
python generate_indicies.py $BUCKET_NAME haul n
echo "hauljoin"
python generate_indicies.py $BUCKET_NAME hauljoin n
echo "id_rank"
python generate_indicies.py $BUCKET_NAME id_rank n
echo "latitude_dd_end"
python generate_indicies.py $BUCKET_NAME latitude_dd_end n
echo "latitude_dd_start"
python generate_indicies.py $BUCKET_NAME latitude_dd_start n
echo "longitude_dd_end"
python generate_indicies.py $BUCKET_NAME longitude_dd_end n
echo "longitude_dd_start"
python generate_indicies.py $BUCKET_NAME longitude_dd_start n
echo "net_height_m"
python generate_indicies.py $BUCKET_NAME net_height_m n
echo "net_width_m"
python generate_indicies.py $BUCKET_NAME net_width_m n
echo "performance"
python generate_indicies.py $BUCKET_NAME performance n
echo "requirements"
python generate_indicies.py $BUCKET_NAME requirements n
echo "scientific_name"
python generate_indicies.py $BUCKET_NAME scientific_name n
echo "species_code"
python generate_indicies.py $BUCKET_NAME species_code n
echo "srvy"
python generate_indicies.py $BUCKET_NAME srvy n
echo "station"
python generate_indicies.py $BUCKET_NAME station n
echo "stratum"
python generate_indicies.py $BUCKET_NAME stratum n
echo "surface_temperature_c"
python generate_indicies.py $BUCKET_NAME surface_temperature_c n
echo "survey"
python generate_indicies.py $BUCKET_NAME survey n
echo "survey_definition_id"
python generate_indicies.py $BUCKET_NAME survey_definition_id n
echo "survey_name"
python generate_indicies.py $BUCKET_NAME survey_name n
echo "taxon_confidence"
python generate_indicies.py $BUCKET_NAME taxon_confidence n
echo "vessel_id"
python generate_indicies.py $BUCKET_NAME vessel_id n
echo "vessel_name"
python generate_indicies.py $BUCKET_NAME vessel_name n
echo "weight_kg"
python generate_indicies.py $BUCKET_NAME weight_kg n
echo "year"
python generate_indicies.py $BUCKET_NAME year y
