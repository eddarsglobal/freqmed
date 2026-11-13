/* SPDX-License-Identifier: Apache-2.0 */
#ifndef FREQMED_EM_HARDWARE_DISCOVERY_H
#define FREQMED_EM_HARDWARE_DISCOVERY_H
#include <stdint.h>

#define FM_EM_USB_CANDIDATES_CAP 24U

typedef struct {
  uint32_t vendor_id;
  uint32_t product_id;
  uint32_t interface_protocol;
  int has_vendor_product;
} FMEmUsbInterfaceCandidate;

typedef struct {
  uint32_t usb_devices_reported;
  uint32_t usb_interfaces_reported;
  uint32_t serial_callout_nodes_reported;
  uint32_t usbtmc_interfaces_reported;
  uint32_t candidates_stored;
  int listing_truncated;
  FMEmUsbInterfaceCandidate candidates[FM_EM_USB_CANDIDATES_CAP];
} FMEmReadonlyInventory;

/* These descriptor codes are defined by USB-IF, not laboratory readings.
 * They establish a USBTMC interface signature, not an EM generator. */
int fm_em_descriptor_is_usbtmc(unsigned class_code,
                              unsigned subclass_code,
                              unsigned protocol_code);

/* Queries macOS IOKit registry only. Never opens, claims, initializes,
 * writes to, or sends control transfers to any USB/serial apparatus.
 * Returns 0 only for a completed enumeration of all three service classes.
 * Output fields describe OS registry entries, not instrument qualification.
 */
int fm_em_discover_readonly(FMEmReadonlyInventory *output);
#endif
