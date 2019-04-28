#!/bin/sh


cd h264decoder

rm -r build

mkdir build

cd build

cmake ..

make

cp libh264decoder.so ../../

echo "Build done!"
