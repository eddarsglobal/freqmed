/* SPDX-License-Identifier: Apache-2.0 */
/* Only this function is exported from the isolated candidate library.
 * Source acoustic_macos.c defines fm_acoustic_physical_output() as a
 * permanent refusal, and its AudioQueue implementation is static/unreachable.
 * A linked native object is not an emission permission or a safety proof. */
#include "generator.h"
#include <stdint.h>
#include <string.h>
typedef struct {
    uint32_t abi_version;
    uint32_t original_candidate_compiled;
    uint32_t macos_backend_declared;
    uint32_t emitter_entrypoint_denied;
} FMR58CandidateEvidence;
#if defined(_WIN32)
#define FM_R58_EXPORT __declspec(dllexport)
#else
#define FM_R58_EXPORT __attribute__((visibility("default")))
#endif
FM_R58_EXPORT int fm_r58_candidate_evidence(FMR58CandidateEvidence *out) {
    if (!out) return -1;
    memset(out,0,sizeof(*out));
    out->abi_version=1U;
    out->original_candidate_compiled=1U; /* Original C object linked in same DSO */
    out->macos_backend_declared=fm_acoustic_native_backend_available()==1 ? 1U:0U;
    /* The original source exports a permanent refusal, even on macOS. */
    out->emitter_entrypoint_denied=fm_acoustic_physical_output((const FMCommand*)0)!=0 ? 1U:0U;
    return out->emitter_entrypoint_denied ? 0:-1;
}
