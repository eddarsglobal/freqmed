/* SPDX-License-Identifier: Apache-2.0 */
#include "integration.h"

FMIntegrationResult fm_integration_validate(const FMIntegrationRequest *r) {
    if (!r) return FM_INT_INVALID;
    switch (r->channel) {
    case FM_ACOUSTIC:
        if (r->acoustic == NULL || r->em_profile || r->em_setpoint ||
            r->acoustic->channel != FM_ACOUSTIC)
            return FM_INT_INVALID;
        return fm_validate_command(r->acoustic, NULL, 0)
            ? FM_INT_ACOUSTIC_STRUCTURE_ONLY : FM_INT_INVALID;
    case FM_ELECTROMAGNETIC:
        if (r->acoustic || !r->em_setpoint) return FM_INT_INVALID;
        if (!r->em_profile) return FM_INT_EM_PROFILE_REQUIRED;
        return fm_em_check_setpoint(r->em_profile, r->em_setpoint, NULL, 0)
            == FM_EM_STRUCTURAL_ONLY_NO_AUTHORIZATION
            ? FM_INT_EM_STRUCTURE_ONLY : FM_INT_INVALID;
    default:
        return FM_INT_INVALID;
    }
}
