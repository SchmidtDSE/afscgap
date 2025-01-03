echo "Starting..." >> status.txt

echo "== Get all years =="
echo "== Get all years ==" >> status.txt
bash get_all_years.sh
echo "== Render flat =="
echo "== Render flat ==" >> status.txt
python3 render_flat.py $BUCKET_NAME written_paths.csv
echo "== Index data =="
echo "== Index data ==" >> status.txt
bash index_data.sh
echo "== Combine shards =="
echo "== Combine shards ==" >> status.txt
bash combine_shards.sh
echo "== Write main =="
echo "== Write main ==" >> status.txt
python3 write_main_index.py $BUCKET_NAME
echo "== Move index =="
echo "== Move index ==" >> status.txt
python3 move_afscgap.py index
echo "== Move joined =="
echo "== Move joined ==" >> status.txt
python3 move_afscgap.py joined

echo "Done." >> status.txt
