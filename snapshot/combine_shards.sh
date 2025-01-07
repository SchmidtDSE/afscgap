echo "area_swept_km"
python combine_shards.py $BUCKET_NAME area_swept_km
echo "bottom_temperature_c"
python combine_shards.py $BUCKET_NAME bottom_temperature_c
echo "common_name"
python combine_shards.py $BUCKET_NAME common_name
echo "count"
python combine_shards.py $BUCKET_NAME count
echo "cpue_kgkm2"
python combine_shards.py $BUCKET_NAME cpue_kgkm2
echo "cpue_nokm2"
python combine_shards.py $BUCKET_NAME cpue_nokm2
echo "date_time"
python combine_shards.py $BUCKET_NAME date_time
echo "depth_m"
python combine_shards.py $BUCKET_NAME depth_m
echo "distance_fished_km"
python combine_shards.py $BUCKET_NAME distance_fished_km
echo "duration_hr"
python combine_shards.py $BUCKET_NAME duration_hr
echo "latitude_dd_end"
python combine_shards.py $BUCKET_NAME latitude_dd_end
echo "latitude_dd_start"
python combine_shards.py $BUCKET_NAME latitude_dd_start
echo "longitude_dd_end"
python combine_shards.py $BUCKET_NAME longitude_dd_end
echo "longitude_dd_start"
python combine_shards.py $BUCKET_NAME longitude_dd_start
echo "net_height_m"
python combine_shards.py $BUCKET_NAME net_height_m
echo "net_width_m"
python combine_shards.py $BUCKET_NAME net_width_m
echo "scientific_name"
python combine_shards.py $BUCKET_NAME scientific_name
echo "species_code"
python combine_shards.py $BUCKET_NAME species_code
echo "srvy"
python combine_shards.py $BUCKET_NAME srvy
echo "station"
python combine_shards.py $BUCKET_NAME station
echo "stratum"
python combine_shards.py $BUCKET_NAME stratum
echo "surface_temperature_c"
python combine_shards.py $BUCKET_NAME surface_temperature_c
echo "survey"
python combine_shards.py $BUCKET_NAME survey
echo "taxon_confidence"
python combine_shards.py $BUCKET_NAME taxon_confidence
echo "vessel_id"
python combine_shards.py $BUCKET_NAME vessel_id
echo "vessel_name"
python combine_shards.py $BUCKET_NAME vessel_name
echo "weight_kg"
python combine_shards.py $BUCKET_NAME weight_kg
echo "year"
python combine_shards.py $BUCKET_NAME year
