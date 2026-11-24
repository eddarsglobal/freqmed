/* SPDX-License-Identifier: Apache-2.0 */
#if !defined(_WIN32)
#define _POSIX_C_SOURCE 200809L
#endif
#include "session_clock.h"
#include <stddef.h>
#if defined(_WIN32)
#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0600
#endif
#include <windows.h>
#elif defined(__APPLE__) || defined(__linux__)
#include <time.h>
#else
#error Unsupported OS: no monotonic clock adapter
#endif
int fm_session_clock_ms(uint64_t *out) {
    if (!out) return 0;
#if defined(_WIN32)
    *out=(uint64_t)GetTickCount64();
#else
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC,&ts)!=0 || ts.tv_sec<0 ||
        ts.tv_nsec<0 || ts.tv_nsec>=1000000000L) return 0;
    uint64_t sec=(uint64_t)ts.tv_sec;
    uint64_t sub=(uint64_t)ts.tv_nsec/1000000U;
    if (sec>(UINT64_MAX-sub)/1000U) return 0;
    *out=sec*1000U+sub;
#endif
    return 1;
}
