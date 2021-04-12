BORINGSSL_DIR=~/oqs/boringssl


cd $BORINGSSL_DIR
rm -rf build
mkdir build && cd build
cmake -DBUILD_SHARED_LIBS=ON -GNinja ..
ninja

#Build LSQUIC library
#--------------------

cd ~/oqs
cd lsquic

git submodule init
git submodule update

rm -rf build
mkdir build && cd build

cmake -DBORINGSSL_DIR=$BORINGSSL_DIR -DBORINGSSL_LIB_crypto=$BORINGSSL_DIR/build/crypto/libcrypto.so -DBORINGSSL_LIB_ssl=$BORINGSSL_DIR/build/ssl/libssl.so -GNinja ..

ninja
#ninja test

echo "Successfully completed installation."