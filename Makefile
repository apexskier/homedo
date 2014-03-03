CC=gcc
CFLAGS=-l bcm2835 -Wall

ths: am2302.o
	$(CC) am2302.o $(CFLAGS) -o am2302
