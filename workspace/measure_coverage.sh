project=$1
version=$2

project_dir=$TMP_DIR/$project-$version

echo "Prepare $project_dir"
[ -d $project_dir ] && rm -rf $project_dir
defects4j checkout -p $project -v $version -w $project_dir
[ ! -d $project_dir ] && exit 1 
cd $project_dir && defects4j compile
defects4j export -p classes.relevant -o classes.relevant
defects4j export -p dir.bin.classes -o dir.bin.classes
python /root/workspace/get_all_classes.py $project_dir $(cat dir.bin.classes) $project_dir/classes.all
echo "$(cat classes.all | wc -l) classes are found."

defects4j test 

[ ! -d /root/workspace/all_tests/ ] && mkdir /root/workspace/all_tests/
all_tests=/root/workspace/all_tests/$project-$version
[ ! -d /root/workspace/failing_tests/ ] && mkdir /root/workspace/failing_tests/
failing_tests=/root/workspace/failing_tests/$project-$version

python /root/workspace/get_all_tests.py $project_dir/all_tests $all_tests
defects4j export -p tests.trigger -o $failing_tests

result_path=$COVERAGE_DIR/$project-$version
[ ! -d $COVERAGE_DIR ] && mkdir $COVERAGE_DIR
[ ! -d $result_path ] && mkdir $result_path

sort $all_tests | while read test_method; do
  echo "Measuring coverage of $test_method .............."
  defects4j coverage -t $test_method -i classes.all
  mv coverage.xml $result_path/$test_method.xml
done

python /root/workspace/gen_coverage_matrix.py $result_path --savepath $result_path.pkl -s

[ $? -eq 0 ] && rm -rf $result_path
