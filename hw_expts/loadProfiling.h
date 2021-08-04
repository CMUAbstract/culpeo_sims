#ifndef _LOAD_PROFILING_H_
#define _LOAD_PROFILING_H_
#include <stdint.h>
#include "vsafe.h"

#define NUM_SIGS 6

// Map indicating which mosfets are connect to which GPIO pins
// Note, we assume these are all coming off of port 3
//                            0     1     2     3     4     5
uint16_t pinMap[NUM_SIGS] = {BIT2, BIT3, BIT4, BIT5, BIT6, BIT7};
// Connected to res:        open   1000   470,  220,   47  Ohm
// Actual current:            0    2.8    5.4  11.5    48   mA

/*
Experiment list:
--Constant--
#1 5mA for 500ms
#2 10mA for 1s
#3 5mA for 100ms
#4 10mA for 100ms
#5 25mA for 100ms
#6 5mA for 10ms
#7 10mA for 10ms
#8 25mA for 10ms
#9 50mA for 10ms
#10 10mA for 1ms
#11 25mA for 1ms
#12 50mA for 1ms
*/
#if EXPT_ID == 0 // Dummy experiment to just chill
// We default to VHIGH so we start immediately
#define VSAFE  VHIGH

#define LOAD_SIZE 1
size_t loads[LOAD_SIZE] = {0}; // Load levels
uint16_t times[LOAD_SIZE] = {1000}; // Runtimes in ms


#elif EXPT_ID == 1

#define VSAFE VSAFE_ID1

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,2}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,500}; // Runtimes in ms

#elif EXPT_ID == 2

#define VSAFE VSAFE_ID2

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,3}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,1000}; // Runtimes in ms

#elif EXPT_ID == 3

#define VSAFE VSAFE_ID3

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,2}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,100}; // Runtimes in ms

#elif EXPT_ID == 4

#define VSAFE VSAFE_ID4

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,3}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,100}; // Runtimes in ms

#elif EXPT_ID == 5

#define VSAFE VSAFE_ID5

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,4}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,100}; // Runtimes in ms

#elif EXPT_ID == 6

#define VSAFE VSAFE_ID6

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,2}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,10}; // Runtimes in ms

#elif EXPT_ID == 7

#define VSAFE VSAFE_ID7

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,3}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,10}; // Runtimes in ms

#elif EXPT_ID == 8

#define VSAFE VSAFE_ID8

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,4}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,10}; // Runtimes in ms

#elif EXPT_ID == 9

#define VSAFE VSAFE_ID9

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,5}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,10}; // Runtimes in ms

#elif EXPT_ID == 10

#define VSAFE VSAFE_ID10

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,3}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,1}; // Runtimes in ms

#elif EXPT_ID == 11

#define VSAFE VSAFE_ID11

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,4}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,1}; // Runtimes in ms

#elif EXPT_ID == 12

#define VSAFE VSAFE_ID12

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,5}; // Load levels
uint16_t times[LOAD_SIZE] = {1000,1}; // Runtimes in ms

#elif EXPT_ID == 13
#define VSAFE VSAFE_ID13
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,2,0};
uint16_t times[LOAD_SIZE] = {10,100,500,10}; // Runtimes in ms

#elif EXPT_ID == 14
#define VSAFE VSAFE_ID14
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,3,0};
uint16_t times[LOAD_SIZE] = {10,100,500,10}; // Runtimes in ms

#elif EXPT_ID == 15
#define VSAFE VSAFE_ID15
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,2,0};
uint16_t times[LOAD_SIZE] = {10,100,100,10}; // Runtimes in ms

#elif EXPT_ID == 16
#define VSAFE VSAFE_ID16
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,3,0};
uint16_t times[LOAD_SIZE] = {10,100,100,10}; // Runtimes in ms

#elif EXPT_ID == 17
#define VSAFE VSAFE_ID17
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,4,0};
uint16_t times[LOAD_SIZE] = {10,100,100,10}; // Runtimes in ms

#elif EXPT_ID == 18
#define VSAFE VSAFE_ID18
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,2,0};
uint16_t times[LOAD_SIZE] = {10,100,10,10}; // Runtimes in ms

#elif EXPT_ID == 19
#define VSAFE VSAFE_ID19
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,3,0};
uint16_t times[LOAD_SIZE] = {10,100,10,10}; // Runtimes in ms

#elif EXPT_ID == 20
#define VSAFE VSAFE_ID20
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,4,0};
uint16_t times[LOAD_SIZE] = {10,100,10,10}; // Runtimes in ms

#elif EXPT_ID == 21
#define VSAFE VSAFE_ID21
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,5,0};
uint16_t times[LOAD_SIZE] = {10,100,10,10}; // Runtimes in ms

#elif EXPT_ID == 22
#define VSAFE VSAFE_ID22
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,3,0};
uint16_t times[LOAD_SIZE] = {10,100,1,10}; // Runtimes in ms

#elif EXPT_ID == 23
#define VSAFE VSAFE_ID23
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,4,0};
uint16_t times[LOAD_SIZE] = {10,100,1,10}; // Runtimes in ms

#elif EXPT_ID == 24
#define VSAFE VSAFE_ID24
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,1,5,0};
uint16_t times[LOAD_SIZE] = {10,100,1,10}; // Runtimes in ms

#elif EXPT_ID == 25
#define VSAFE VSAFE_ID25
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,2,1,0};
uint16_t times[LOAD_SIZE] = {10,500,100,10}; // Runtimes in ms

#elif EXPT_ID == 26
#define VSAFE VSAFE_ID26
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,3,1,0};
uint16_t times[LOAD_SIZE] = {10,500,100,10}; // Runtimes in ms

#elif EXPT_ID == 27
#define VSAFE VSAFE_ID27
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,2,1,0};
uint16_t times[LOAD_SIZE] = {10,100,100,10}; // Runtimes in ms

#elif EXPT_ID == 28
#define VSAFE VSAFE_ID28
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,3,1,0};
uint16_t times[LOAD_SIZE] = {10,100,100,10}; // Runtimes in ms

#elif EXPT_ID == 29
#define VSAFE VSAFE_ID29
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,4,1,0};
uint16_t times[LOAD_SIZE] = {10,100,100,10}; // Runtimes in ms

#elif EXPT_ID == 30
#define VSAFE VSAFE_ID30
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,2,1,0};
uint16_t times[LOAD_SIZE] = {10,10,100,10}; // Runtimes in ms

#elif EXPT_ID == 31
#define VSAFE VSAFE_ID31
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,3,1,0};
uint16_t times[LOAD_SIZE] = {10,10,100,10}; // Runtimes in ms

#elif EXPT_ID == 32
#define VSAFE VSAFE_ID32
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,4,1,0};
uint16_t times[LOAD_SIZE] = {10,10,100,10}; // Runtimes in ms

#elif EXPT_ID == 33
#define VSAFE VSAFE_ID33
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,5,1,0};
uint16_t times[LOAD_SIZE] = {10,10,100,10}; // Runtimes in ms

#elif EXPT_ID == 34
#define VSAFE VSAFE_ID34
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,3,1,0};
uint16_t times[LOAD_SIZE] = {10,1,100,10}; // Runtimes in ms

#elif EXPT_ID == 35
#define VSAFE VSAFE_ID35
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,4,1,0};
uint16_t times[LOAD_SIZE] = {10,1,100,10}; // Runtimes in ms

#elif EXPT_ID == 36
#define VSAFE VSAFE_ID36
#define LOAD_SIZE 4
size_t loads[LOAD_SIZE] = {0,5,1,0};
uint16_t times[LOAD_SIZE] = {10,1,100,10}; // Runtimes in ms



#else
#error "No expt id defined"

#endif

#endif
