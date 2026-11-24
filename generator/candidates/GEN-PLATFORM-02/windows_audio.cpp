/* SPDX-License-Identifier: Apache-2.0 */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <initguid.h>
#include <mmdeviceapi.h>
#include <mmreg.h>
#include <cstdio>
#include <cstring>
#include <cwchar>

/* Only endpoint metadata. No IAudioClient activation or stream. */
int main() {
    if(FAILED(CoInitializeEx(nullptr,COINIT_MULTITHREADED))) return 2;
    IMMDeviceEnumerator *en=nullptr;
    IMMDeviceCollection *col=nullptr;
    HRESULT hr=CoCreateInstance(CLSID_MMDeviceEnumerator,nullptr,CLSCTX_INPROC_SERVER,
        IID_IMMDeviceEnumerator,reinterpret_cast<void **>(&en));
    if(SUCCEEDED(hr)) hr=en->EnumAudioEndpoints(eRender,DEVICE_STATE_ACTIVE,&col);
    UINT count=0;
    if(SUCCEEDED(hr)) hr=col->GetCount(&count);
    if(FAILED(hr)||count>32) {
        if(col) col->Release();
        if(en) en->Release();
        CoUninitialize(); return 2;
    }
    IMMDevice *def=nullptr;
    LPWSTR defid=nullptr;
    if(SUCCEEDED(en->GetDefaultAudioEndpoint(eRender,eMultimedia,&def))) {
        (void)def->GetId(&defid); def->Release();
    }
    std::printf("[");
    for(UINT i=0;i<count;i++) {
        IMMDevice *d=nullptr;
        IPropertyStore *store=nullptr;
        PROPVARIANT v;
        PropVariantInit(&v);
        LPWSTR id=nullptr;
        unsigned rate=0,channels=0;
        int is_default=-1;
        if(SUCCEEDED(col->Item(i,&d))) {
            if(SUCCEEDED(d->GetId(&id)) && defid)
                is_default=std::wcscmp(id,defid)==0?1:0;
            if(SUCCEEDED(d->OpenPropertyStore(STGM_READ,&store)) &&
               SUCCEEDED(store->GetValue(PKEY_AudioEngine_DeviceFormat,&v)) &&
               v.vt==VT_BLOB && v.blob.pBlobData && v.blob.cbSize>=sizeof(WAVEFORMATEX)) {
                WAVEFORMATEX fmt{};
                std::memcpy(&fmt,v.blob.pBlobData,sizeof(fmt));
                if(fmt.nChannels>0 && fmt.nChannels<=256 && fmt.nSamplesPerSec>0) {
                    rate=fmt.nSamplesPerSec; channels=fmt.nChannels;
                }
            }
        }
        std::printf("%s{\"index\":%u,\"channels\":",i?",":"",i+1);
        if(channels) std::printf("%u,\"sample_rate_hz\":%u",channels,rate);
        else std::printf("null,\"sample_rate_hz\":null");
        std::printf(",\"format_source\":\"%s\",\"transport\":\"UNKNOWN\",\"default\":%s}",
            channels?"WINDOWS_SHARED_DEVICE_FORMAT":"UNKNOWN",
            is_default<0?"null":is_default?"true":"false");
        PropVariantClear(&v);
        if(store) store->Release();
        if(id) CoTaskMemFree(id);
        if(d) d->Release();
    }
    std::printf("]\n");
    if(defid) CoTaskMemFree(defid);
    col->Release(); en->Release(); CoUninitialize();
    return 0;
}
