#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Offline software qualification and classified native event witness."""
import hashlib
import json
import os
import pathlib
import platform
import subprocess
import sys
import tempfile

AC="54fd4e6cd4a8106da12bb57fa8208ce569a4185b"
EM="0412c0fbe2b54298a3b1dd346c78d3b56dda0e63"
I1="d4ae3fa35412595a194c5f7c323cefb169722d19"
I2="1bd0fe8c8a07ca64301ee89e1d26b46a33d554a3"
B3="f20aa44d921c5455cd015eddb1bcde05549843a0"
M4="6da9688f384beb020fd7f311ce96dc29330de5db"
R5="19800411015599ab98c9b854024c0a125a4c7a4e"
PINS=[
 (AC,"GEN-R66/native/generator.h","9839f4390d9f17560cf6ef2447501a314f335773"),
 (AC,"GEN-R66/native/generator_core.c","80f35f7ec323a658699929a717d6d16ef74a3144"),
 (AC,"GEN-R66/native/output_hard_denied.c","715b0981fb961b180df9e9dcf508a7608a224270"),
 (EM,"GEN-EM-01/native/em_device_contract.h","d577e6c0f96fed003f767ee62ca74ff14e8ab69d"),
 (EM,"GEN-EM-01/native/em_device_contract.c","f09603278215d960f9c7df5cc1aa812bffe0d365"),
 (I1,"GEN-INTEGRATION-01/integration.h","490b09c4acb96ac9e857a6a55324c28c91c14f1f"),
 (I1,"GEN-INTEGRATION-01/integration.c","c7fc2c90ea4b64aa5a5c9f25e0b202991b01b627"),
 (I1,"GEN-INTEGRATION-01/test_integration.c","631aef08ca9e52ecbb24f6b067d35fe3de7a7b41"),
 (I2,"GEN-INTEGRATION-02/session.h","2376cab6bda0afb65da3d26e463c3cefba5f039b"),
 (I2,"GEN-INTEGRATION-02/session.c","b674b1ba9b5baad7eed8f083efda1726d81ec6d9"),
 (I2,"GEN-INTEGRATION-02/session_clock.h","0bd6de2e64d51f46e9d705548f5b73f3d4f6691b"),
 (I2,"GEN-INTEGRATION-02/session_clock.c","2ff29e1b367fa7fe0982f9af58c9b233d0945230"),
 (I2,"GEN-INTEGRATION-02/test_session.c","9f0ca3abdf7d40de7293971469b204c0334d460f"),
 (I2,"GEN-INTEGRATION-02/test_clock.c","38b6edfa759982930ec61b1cf26b21cf8aad3301"),
 (AC,"GEN-R66/native/audio_devices.h","3bab6eef1608612f67550f90757791ea893c4a21"),
 (AC,"GEN-R66/native/audio_devices_macos.c","0ba4c6015786a3a263533036ca1025b7d2db2d09"),
 (B3,"GEN-PLATFORM-03/binding.h","f0c2cf430d59a46ffdf09938c86fea375d0a87f0"),
 (B3,"GEN-PLATFORM-03/binding.c","6c5194155ac8f6beaa782d0930b141bde6bdfa51"),
 (B3,"GEN-PLATFORM-03/test_binding.c","32daee2f7dac47f6a2f6dab66ff1d0f504a05020"),
 (M4,"GEN-PLATFORM-04/monitor.h","ceebd9f876ba54788754c6b14b2bfdf5b288dedc"),
 (M4,"GEN-PLATFORM-04/monitor.c","3874ef72b7a597db14489c7cc384c7965dc00667"),
 (M4,"GEN-PLATFORM-04/test_monitor.c","fe29f324d5f7ec7c3ff4a5947179f708bdd4deeb"),
 (R5,"GEN-PLATFORM-05/recovery.h","13dfea669ce0a4409914b419521b2d704492aaf9"),
 (R5,"GEN-PLATFORM-05/recovery.c","42707299d531619b07ca1dba0288b5a41c1aaa54"),
 (R5,"GEN-PLATFORM-05/test_recovery.c","d99e20ef0353c2410a3dbe96d65300743e9b8cf0"),
]
def main():
    if len(sys.argv)!=2: raise SystemExit("usage: qualify.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    own=pathlib.Path(__file__).resolve().parent
    system=platform.system()
    if system not in ("Darwin","Linux","Windows"):raise SystemExit("UNSUPPORTED_OS")
    cc=os.environ.get("CC","gcc" if system=="Windows" else "cc")
    with tempfile.TemporaryDirectory(prefix="freqmed_event06_") as tmp:
        work=pathlib.Path(tmp)
        for ref,path,pin in PINS:
            data=subprocess.check_output(["git","-C",str(repo),"show",
                ref+":generator/candidates/"+path],timeout=30)
            digest=hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()
            if digest!=pin:raise SystemExit("PIN_MISMATCH "+path)
            (work/pathlib.Path(path).name).write_bytes(data)
        common=[str(work/n) for n in ("generator_core.c","output_hard_denied.c",
            "em_device_contract.c","integration.c")]
        session=str(work/"session.c")
        clock=str(work/"session_clock.c")
        binding=str(work/"binding.c")
        monitor=str(work/"monitor.c")
        recovery=str(work/"recovery.c")
        evidence=str(own/"event_evidence.c")
        def build(name,sources,extra=()):
            exe=work/(name+(".exe" if system=="Windows" else ""))
            subprocess.run([cc,"-std=c11","-Wall","-Wextra","-Werror","-pedantic",
                "-I",str(work),"-I",str(own),*common,*sources,"-lm",*extra,"-o",str(exe)],
                check=True,timeout=120)
            return subprocess.check_output([str(exe)],text=True,timeout=180).strip()
        suites=[
            ("regression1",[str(work/"test_integration.c")],"GEN_INTEGRATION_01_ASSERTIONS=23 PASS"),
            ("regression2",[session,str(work/"test_session.c")],"GEN_INTEGRATION_02_ASSERTIONS=38 PASS"),
            ("clock",[session,clock,str(work/"test_clock.c")],"GEN_INTEGRATION_02_CLOCK_ASSERTIONS=9 PASS"),
            ("binding",[session,binding,str(work/"test_binding.c")],"GEN_PLATFORM_03_ASSERTIONS=45 PASS"),
            ("monitor",[session,binding,monitor,str(work/"test_monitor.c")],"GEN_PLATFORM_04_ASSERTIONS=32 PASS"),
            ("recovery",[session,binding,monitor,recovery,str(work/"test_recovery.c")],"GEN_PLATFORM_05_ASSERTIONS=50 PASS"),
            ("event",[evidence,str(own/"test_event_evidence.c")],"GEN_PLATFORM_06_ASSERTIONS=30 PASS"),
        ]
        for name,sources,expected in suites:
            observed=build(name,sources)
            if observed!=expected:raise SystemExit("UNEXPECTED_TEST_RESULT "+observed)
            print(observed,flush=True)
        if system=="Darwin":
            native=json.loads(build("native",[session,clock,binding,monitor,recovery,evidence,str(own/"mac_event.c"),
                str(work/"audio_devices_macos.c")],("-framework","CoreAudio","-framework","CoreFoundation")))
        else:
            native={"native_event_verdict":"ADAPTER_NOT_IMPLEMENTED","event_complete":False}
        print("BUREAU_REPORT="+json.dumps({
            "schema":"freqmed.gen-platform-06.v1","platform":system,
            "machine":platform.machine(),"assertions":227,"regression_assertions":197,
            "event_assertions":30,"source_pins_verified":len(PINS),
            "native":native,"verdict":"PASS_SOFTWARE_ONLY","em_binding":"NOT_AVAILABLE",
            "hardware_qualified":False,"physical_output":"NOT_PERFORMED",
            "physical_measurement":"NOT_PERFORMED","authorization":"NONE",
            "certification":"NOT_ISSUED"},sort_keys=True,allow_nan=False))
if __name__=="__main__":main()
