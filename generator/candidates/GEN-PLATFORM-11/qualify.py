#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Unified memory-only acoustic runtime and built-in hardware metadata qualification."""
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
E6="99ab2b85350961086a0a4ad856ebbded99547201"
R7="ef22815a739db53288d72890d6a3d217eb26417c"
A8="8a1b5ce4bc653c725bfe473dea7301a934907dff"
D9="ca86bb06b9f424716d277d4fa4a4998970062de6"
L10="6b2b3bf7eeb4d68cad0be4d9a83880862eb5e5c9"
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
 (E6,"GEN-PLATFORM-06/event_evidence.h","2a5157bbd5f4f3c071e69368b23f15c2b6049f52"),
 (E6,"GEN-PLATFORM-06/event_evidence.c","378f11e1bb1eaafc289b070a3075f46967010911"),
 (E6,"GEN-PLATFORM-06/test_event_evidence.c","7fc97b44463c5e0d35c913b202f89ea52ec7fbd9"),
 (R7,"GEN-PLATFORM-07/readiness.h","6cf37fdf6c67c53779215e2efac89ceda386050a"),
 (R7,"GEN-PLATFORM-07/readiness.c","f35962888553f03a8f3d193661ea5b5d2402ff8e"),
 (R7,"GEN-PLATFORM-07/test_readiness.c","626fc45e2aece7b4e6ce20949f6da1a759e68466"),
 (R7,"GEN-PLATFORM-07/mac_readiness.c","1dbb3d580dd7aec51048a7913012a4eb1fade2ae"),
 (A8,"GEN-PLATFORM-08/assembly.h","5fd071fe53c737bd1a8b744d6defcf0e9dfdbc14"),
 (A8,"GEN-PLATFORM-08/assembly.c","f508b864970512cdbc232bf831f222aa3cfe4fe1"),
 (A8,"GEN-PLATFORM-08/test_assembly.c","a900bf7cca29ccc2c6c1ca1ee0e613d6508d6049"),
 (D9,"GEN-PLATFORM-09/digital_signal.h","1c087aa661a238d0c69e592d47a6cea8dcc1d07e"),
 (D9,"GEN-PLATFORM-09/digital_signal.c","5239fc6f204fef96f84e09dee35ea74918f80d0c"),
 (D9,"GEN-PLATFORM-09/test_digital_signal.c","a57b4d514b01617a82635b5c7a9a6173ac59cf7b"),
 (L10,"GEN-PLATFORM-10/buffer_lifecycle.h","f152ba101eeb7ad529dc3303ff6ba4260f64cd32"),
 (L10,"GEN-PLATFORM-10/buffer_lifecycle.c","2d64047816ef87cffbbd692972247ec5425d555a"),
 (L10,"GEN-PLATFORM-10/test_buffer_lifecycle.c","002c66de11d039c91f4df793d7524a0d18b753e5"),
]
def main():
    if len(sys.argv)!=2: raise SystemExit("usage: qualify.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    own=pathlib.Path(__file__).resolve().parent
    system=platform.system()
    if system not in ("Darwin","Linux","Windows"):raise SystemExit("UNSUPPORTED_OS")
    cc=os.environ.get("CC","gcc" if system=="Windows" else "cc")
    with tempfile.TemporaryDirectory(prefix="freqmed_runtime11_") as tmp:
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
        evidence=str(work/"event_evidence.c")
        readiness=str(work/"readiness.c")
        assembly=str(work/"assembly.c")
        digital=str(work/"digital_signal.c")
        lifecycle=str(work/"buffer_lifecycle.c")
        runtime=str(own/"unified_runtime.c")
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
            ("event",[evidence,str(work/"test_event_evidence.c")],"GEN_PLATFORM_06_ASSERTIONS=30 PASS"),
            ("readiness",[readiness,str(work/"test_readiness.c")],"GEN_PLATFORM_07_ASSERTIONS=35 PASS"),
            ("assembly",[session,binding,monitor,recovery,readiness,assembly,str(work/"test_assembly.c")],"GEN_PLATFORM_08_ASSERTIONS=30 PASS"),
            ("digital",[session,binding,monitor,recovery,readiness,assembly,digital,str(work/"test_digital_signal.c")],"GEN_PLATFORM_09_ASSERTIONS=42 PASS"),
            ("lifecycle",[session,binding,monitor,recovery,readiness,assembly,digital,lifecycle,str(work/"test_buffer_lifecycle.c")],"GEN_PLATFORM_10_ASSERTIONS=48 PASS"),
            ("runtime",[session,binding,monitor,recovery,readiness,assembly,digital,lifecycle,runtime,str(own/"test_unified_runtime.c")],"GEN_PLATFORM_11_ASSERTIONS=42 PASS"),
        ]
        for name,sources,expected in suites:
            observed=build(name,sources)
            if observed!=expected:raise SystemExit("UNEXPECTED_TEST_RESULT "+observed)
            print(observed,flush=True)
        if system=="Darwin":
            source=(work/"mac_readiness.c").read_text(encoding="utf-8")
            marker="static const char *verdict(FMReadinessResult r) {"
            if source.count(marker)!=1:raise SystemExit("COLLECTOR_BOUNDARY_MISMATCH")
            prefix=source.split(marker,1)[0]
            prefix=prefix.removeprefix("#define _POSIX_C_SOURCE 200809L\n")
            (work/"mac_capture_pinned.inc").write_text(prefix,encoding="utf-8")
            native=json.loads(build("native",[session,clock,binding,monitor,recovery,readiness,assembly,digital,lifecycle,runtime,str(own/"mac_runtime.c")],("-framework","CoreAudio","-framework","CoreFoundation","-framework","IOKit")))
        else:
            native={"native_runtime":"ADAPTER_NOT_IMPLEMENTED","physical_ready":False,"independent_stop_verified":False}
        print("BUREAU_REPORT="+json.dumps({
            "schema":"freqmed.gen-platform-11.v1","platform":system,
            "machine":platform.machine(),"assertions":424,"regression_assertions":382,
            "runtime_assertions":42,"source_pins_verified":len(PINS),
            "native":native,"verdict":"PASS_SOFTWARE_ONLY","em_binding":"NOT_AVAILABLE",
            "native_event_qualification":"PENDING_NOT_REPLAYED",
            "physical_bench_prerequisites":{"independent_stop":"NOT_VERIFIED","physical_limits":"NOT_MEASURED","independent_measurement":"NOT_AVAILABLE_IN_THIS_TEST","bench_authorization":"NONE"},
            "integrated_hardware_policy":"PREFER_EXISTING_NATIVE_HARDWARE","radio_generator_qualified":False,"queue_slots":4,"block_samples":256,"digital_destination":"MEMORY_ONLY","audio_files_written":False,
            "hardware_qualified":False,"physical_output":"NOT_PERFORMED",
            "physical_measurement":"NOT_PERFORMED","authorization":"NONE",
            "certification":"NOT_ISSUED"},sort_keys=True,allow_nan=False))
if __name__=="__main__":main()
