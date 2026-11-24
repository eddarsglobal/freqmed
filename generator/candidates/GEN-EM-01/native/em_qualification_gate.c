/* SPDX-License-Identifier: Apache-2.0 */
#include "em_qualification_gate.h"
#include <stddef.h>

/* Validates only length/characters of SHA-256 digests, not their provenance.
 * Strings may be fabricated: no successful screen certifies a device. */
static int is_hex_digest64(const char *text) {
  if (!text) return 0;
  for (size_t i=0;i<64;i++) {
    unsigned char c=(unsigned char)text[i];
    if (!((c>='0' && c<='9') || (c>='a' && c<='f') ||
          (c>='A' && c<='F'))) return 0;
  }
  return text[64]=='\0';
}
static int is_bounded_name(const char *name) {
  if (!name || name[0]=='\0') return 0;
  for (size_t i=0;i<128;i++) {
    if (name[i]=='\0') return 1;
  }
  return 0;
}
FMEmDocumentaryReview fm_em_screen_documentary_evidence(
    const FMEmDocumentaryEvidence *evidence) {
  if (!evidence || !is_bounded_name(evidence->manufacturer) ||
      !is_bounded_name(evidence->model) ||
      !is_hex_digest64(evidence->protocol_document_sha256) ||
      !is_hex_digest64(evidence->independent_cutoff_document_sha256) ||
      !is_hex_digest64(evidence->metrology_plan_sha256))
    return FM_EM_DOCUMENTS_MISSING;
  return FM_EM_DOCUMENTS_PRESENT_UNVERIFIED;
}
int fm_em_hardware_qualified_in_r11(const FMEmDocumentaryEvidence *evidence) {
  /* The physical instrument is not present or independently qualified.
   * Documentary screening is not a hardware gate and cannot unlock output.
   * This source is compiled to an isolated object and is never linked to
   * the owner-facing no-output executable. */
  (void)evidence;
  return 0;
}
