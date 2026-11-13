/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_EM_QUALIFICATION_GATE_H
#define FREQMED_EM_QUALIFICATION_GATE_H

/* Source-only documentary evidence screen, NOT a hardware driver.
 * No instrument, port, emission, certificate or measurement is implied. */
typedef struct {
  const char *manufacturer;
  const char *model;
  const char *protocol_document_sha256;
  const char *independent_cutoff_document_sha256;
  const char *metrology_plan_sha256;
} FMEmDocumentaryEvidence;

typedef enum {
  FM_EM_DOCUMENTS_MISSING=0,
  FM_EM_DOCUMENTS_PRESENT_UNVERIFIED=1
} FMEmDocumentaryReview;

/* A well-shaped evidence packet requires future human authenticity review. */
FMEmDocumentaryReview fm_em_screen_documentary_evidence(
    const FMEmDocumentaryEvidence *evidence);

/* Always deny hardware admission in GEN-R11, regardless of supplied text. */
int fm_em_hardware_qualified_in_r11(const FMEmDocumentaryEvidence *evidence);

#endif
