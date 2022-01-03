dos2unix tests/* 2> /dev/null
python3 test.py tests/${1}.in > tests/${1}.out
python3 check_test.py tests/${1}.in tests/${1}.out tests/${1}.ref.out