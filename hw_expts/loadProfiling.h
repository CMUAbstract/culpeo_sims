#ifndef _LOAD_PROFILING_H_
#define _LOAD_PROFILING_H_
#include <stdint.h>

#define NUM_SIGS 4

uint16_t pinMap[NUM_SIGS];

#if EXPT_ID == 1

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,1}; // Load levels
uint16_t times[LOAD_SIZE] = {10,30}; // Runtimes in ms

#elif EXPT_ID == 2

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,1,2}; // Load levels
uint16_t times[LOAD_SIZE] = {10,30,10}; // Runtimes in ms

#elif EXPT_ID == 3

#define LOAD_SIZE 2
size_t loads[LOAD_SIZE] = {0,1}; // Load levels
uint16_t times[LOAD_SIZE] = {10,30}; // Runtimes in ms

#elif EXPT_ID == 4

#define LOAD_SIZE 1
size_t loads[LOAD_SIZE] = {3}; // Load levels
uint16_t times[LOAD_SIZE] = {15}; // Runtimes in ms

#elif EXPT_ID == 5

#define LOAD_SIZE 3
size_t loads[LOAD_SIZE] = {3,1,0}; // Load levels
uint16_t times[LOAD_SIZE] = {5,200,3000}; // Runtimes in ms

#else

#define LOAD_SIZE 5
size_t loads[LOAD_SIZE] = {0,2,0,1,0}; // Load levels
uint16_t times[LOAD_SIZE] = {10,5,10,30,10}; // Runtimes in ms

#endif

#endif
