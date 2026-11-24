/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FM_INTEGRATION_01_H
#define FM_INTEGRATION_01_H
#include "generator.h"
#include "em_device_contract.h"

/* Pure synchronous validation. No driver, device discovery, I/O or activation.
 * Callers own inputs; no concurrent mutation during validation. */
typedef struct {
    FMChannel channel;
    const FMCommand *acoustic;
    const FMEmDeviceContract *em_profile;
    const FMEmSetpoint *em_setpoint;
} FMIntegrationRequest;
typedef enum {
    FM_INT_INVALID = 0,
    FM_INT_ACOUSTIC_STRUCTURE_ONLY = 1,
    FM_INT_EM_STRUCTURE_ONLY = 2,
    FM_INT_EM_PROFILE_REQUIRED = 3
} FMIntegrationResult;
/* Result values are categories, not boolean permission or safety approval. */
FMIntegrationResult fm_integration_validate(const FMIntegrationRequest *r);
#endif
