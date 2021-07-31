#ifndef _VSAFE_H_
#define _VSAFE_H_

#if CONFIG == 0

#define VSAFE_ID10 2321
#define VSAFE_ID11 2322
#define VSAFE_ID12 2322
#define VSAFE_ID1 2543
#define VSAFE_ID3 2355
#define VSAFE_ID4 2405
#define VSAFE_ID6 2323
#define VSAFE_ID7 2327
#define VSAFE_ID8 2337
#define VSAFE_ID9 2356

#elif CONFIG == 1

#define VSAFE_ID10 2062
#define VSAFE_ID11 2063
#define VSAFE_ID12 2063
#define VSAFE_ID1 2309
#define VSAFE_ID3 2100
#define VSAFE_ID4 2156
#define VSAFE_ID6 2064
#define VSAFE_ID7 2068
#define VSAFE_ID8 2080
#define VSAFE_ID9 2101

#else

#error "Config not defined"

#endif // Vsafe
