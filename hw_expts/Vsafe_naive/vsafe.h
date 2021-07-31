#ifndef _VSAFE_H_
#define _VSAFE_H_

#if CONFIG == 0

#define VSAFE_ID10 2360
#define VSAFE_ID11 2361
#define VSAFE_ID12 2363
#define VSAFE_ID1 2568
#define VSAFE_ID3 2403
#define VSAFE_ID4 2450
#define VSAFE_ID6 2364
#define VSAFE_ID7 2369
#define VSAFE_ID8 2379
#define VSAFE_ID9 2394

#elif CONFIG == 1

#define VSAFE_ID10 2106
#define VSAFE_ID11 2107
#define VSAFE_ID12 2109
#define VSAFE_ID1 2337
#define VSAFE_ID3 2153
#define VSAFE_ID4 2206
#define VSAFE_ID6 2110
#define VSAFE_ID7 2115
#define VSAFE_ID8 2127
#define VSAFE_ID9 2143
#else

#error "Config not defined"

#endif // Vsafe
