/* SPDX-License-Identifier: Apache-2.0 */
/* GEN-R7: real macOS IOKit registry discovery, strictly read-only.
 * No device/serial port open, no USB control transfer, no RF, no output.
 * Never claims USB descriptors prove an EM generator is installed.
 */
#include "em_hardware_discovery.h"
#include <string.h>

int fm_em_descriptor_is_usbtmc(unsigned class_code,
                              unsigned subclass_code,
                              unsigned protocol_code) {
  /* USB-IF: application-specific FE/03 USBTMC, 00 basic or 01 USB488. */
  return class_code==0xFEU && subclass_code==0x03U &&
         (protocol_code==0x00U || protocol_code==0x01U);
}

#if defined(__APPLE__)
#include <CoreFoundation/CoreFoundation.h>
#include <IOKit/IOKitLib.h>
#include <mach/mach.h>
#include <stdint.h>

#define FM_SCAN_MAX 4096U

static int fm_registry_number(io_service_t service, CFStringRef key,
                              int lookup_parents, uint32_t *out) {
  if (!out) return 0;
  CFTypeRef prop = lookup_parents
    ? IORegistryEntrySearchCFProperty(service,kIOServicePlane,key,
        kCFAllocatorDefault,kIORegistryIterateParents)
    : IORegistryEntryCreateCFProperty(service,key,kCFAllocatorDefault,0);
  if (!prop) return 0;
  int32_t value=-1;
  int ok=CFGetTypeID(prop)==CFNumberGetTypeID() &&
         CFNumberGetValue((CFNumberRef)prop,kCFNumberSInt32Type,&value) &&
         value>=0;
  CFRelease(prop);
  if (!ok) return 0;
  *out=(uint32_t)value;
  return 1;
}

static int fm_registry_callout(io_service_t service) {
  CFTypeRef prop=IORegistryEntryCreateCFProperty(service,CFSTR("IOCalloutDevice"),
                                               kCFAllocatorDefault,0);
  if (!prop) return 0;
  int is_callout=0;
  if (CFGetTypeID(prop)==CFStringGetTypeID()) {
    char path[256];
    if (CFStringGetCString((CFStringRef)prop,path,sizeof(path),kCFStringEncodingUTF8) &&
        strncmp(path,"/dev/cu.",8U)==0) is_callout=1;
  }
  CFRelease(prop);
  /* Device name is intentionally discarded; avoid logging user identifiers. */
  return is_callout;
}

static int fm_service_iterator(const char *class_name, io_iterator_t *out) {
  if (!out) return -1;
  *out=IO_OBJECT_NULL;
  CFMutableDictionaryRef match=IOServiceMatching(class_name);
  if (!match) return -1;
  /* IOServiceGetMatchingServices CONSUMES match; do not CFRelease it. */
  kern_return_t kr=IOServiceGetMatchingServices(MACH_PORT_NULL,match,out);
  return kr==KERN_SUCCESS ? 0 : -1;
}

int fm_em_discover_readonly(FMEmReadonlyInventory *result) {
  if (!result) return -1;
  memset(result,0,sizeof(*result));
  FMEmReadonlyInventory partial={0};
  io_iterator_t iter=IO_OBJECT_NULL;
  io_service_t service=IO_OBJECT_NULL;
  uint32_t scanned=0;

  if (fm_service_iterator("IOUSBHostDevice",&iter)!=0) return -1;
  while ((service=IOIteratorNext(iter))!=IO_OBJECT_NULL) {
    scanned++;
    IOObjectRelease(service);
    if (scanned>FM_SCAN_MAX) {partial.listing_truncated=1;break;}
    partial.usb_devices_reported++;
  }
  IOObjectRelease(iter);
  if (partial.listing_truncated) return -1;

  scanned=0;
  if (fm_service_iterator("IOUSBHostInterface",&iter)!=0) return -1;
  while ((service=IOIteratorNext(iter))!=IO_OBJECT_NULL) {
    scanned++;
    if (scanned>FM_SCAN_MAX) {
      IOObjectRelease(service);partial.listing_truncated=1;break;
    }
    partial.usb_interfaces_reported++;
    uint32_t cls=0,sub=0,prot=0;
    const int descriptor_ok=
      fm_registry_number(service,CFSTR("bInterfaceClass"),0,&cls) &&
      fm_registry_number(service,CFSTR("bInterfaceSubClass"),0,&sub) &&
      fm_registry_number(service,CFSTR("bInterfaceProtocol"),0,&prot);
    if (descriptor_ok && fm_em_descriptor_is_usbtmc(cls,sub,prot)) {
      partial.usbtmc_interfaces_reported++;
      if (partial.candidates_stored<FM_EM_USB_CANDIDATES_CAP) {
        FMEmUsbInterfaceCandidate *c=&partial.candidates[partial.candidates_stored++];
        c->interface_protocol=prot;
        const int vendor_ok=fm_registry_number(service,CFSTR("idVendor"),1,&c->vendor_id);
        const int product_ok=fm_registry_number(service,CFSTR("idProduct"),1,&c->product_id);
        c->has_vendor_product=vendor_ok && product_ok &&
                              c->vendor_id<=0xFFFFU && c->product_id<=0xFFFFU;
      } else {
        partial.listing_truncated=1;
      }
    }
    IOObjectRelease(service);
  }
  IOObjectRelease(iter);
  /* More USBTMC interfaces than local capacity is NOT a scan failure;
   * report truncated list while retaining the total number scanned. */
  if (scanned>FM_SCAN_MAX) return -1;

  scanned=0;
  if (fm_service_iterator("IOSerialBSDClient",&iter)!=0) return -1;
  while ((service=IOIteratorNext(iter))!=IO_OBJECT_NULL) {
    scanned++;
    if (scanned>FM_SCAN_MAX) {
      IOObjectRelease(service);IOObjectRelease(iter);return -1;
    }
    if (fm_registry_callout(service)) partial.serial_callout_nodes_reported++;
    IOObjectRelease(service);
  }
  IOObjectRelease(iter);
  *result=partial;
  return 0;
}
#else
int fm_em_discover_readonly(FMEmReadonlyInventory *result) {
  if (result) memset(result,0,sizeof(*result));
  return -1;
}
#endif
