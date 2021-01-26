mkdir -p runtime/log
touch runtime/log/road-gen-DEBUG.log
touch runtime/log/road-gen-INFO.log
mkdir -p runtime/out
cd src
python test.py
