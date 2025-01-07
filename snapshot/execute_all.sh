echo "Starting..." >> status.txt

echo "== Get all years =="
echo "== Get all years ==" >> status.txt
bash get_all_years.sh
[ $? -ne 0 ] && exit $?

echo "== Render flat =="
echo "== Render flat ==" >> status.txt
python3 render_flat.py $BUCKET_NAME written_paths.csv
[ $? -ne 0 ] && exit $?

echo "== Index data =="
echo "== Index data ==" >> status.txt
bash index_data.sh
[ $? -ne 0 ] && exit $?

echo "== Combine shards =="
echo "== Combine shards ==" >> status.txt
bash combine_shards.sh
[ $? -ne 0 ] && exit $?

echo "== Write main =="
echo "== Write main ==" >> status.txt
python3 write_main_index.py $BUCKET_NAME
[ $? -ne 0 ] && exit $?

echo "== Check indicies =="
echo "== Check indicies ==" >> status.txt
python check_read.py $BUCKET_NAME index
[ $? -ne 0 ] && exit $?

echo "== Check joined =="
echo "== Check joined ==" >> status.txt
python check_read.py $BUCKET_NAME joined
[ $? -ne 0 ] && exit $?

echo "Done." >> status.txt
