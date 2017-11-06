gcc -g -Wall -I ./include -o libpycall.so -shared -fPIC iat_sample.c  -L ./libs/x64  -lmsc -lrt -ldl -lpthread
