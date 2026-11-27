#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Targeted BENCH-05 private concurrent transport and typed deny-only native boundary."""
import hashlib,json,pathlib,platform,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parent
OWN={"rt_queue.h":"317646f92999e87239e54d6133f3563c862ac184","rt_queue.c":"660672233fd4127a5acb0368e3a83308d226eb7b","test_rt.c":"53caec107ff82b7552eb0952c80e00067fcf18c2","mac_rt.c":"d82f24d43e469ae26dd3d869f9ba87971e21b64a"}
PINS=[["54fd4e6cd4a8106da12bb57fa8208ce569a4185b","generator/candidates/GEN-R66/native/generator.h","9839f4390d9f17560cf6ef2447501a314f335773"],["54fd4e6cd4a8106da12bb57fa8208ce569a4185b","generator/candidates/GEN-R66/native/generator_core.c","80f35f7ec323a658699929a717d6d16ef74a3144"],["54fd4e6cd4a8106da12bb57fa8208ce569a4185b","generator/candidates/GEN-R66/native/output_hard_denied.c","715b0981fb961b180df9e9dcf508a7608a224270"],["0412c0fbe2b54298a3b1dd346c78d3b56dda0e63","generator/candidates/GEN-EM-01/native/em_device_contract.h","d577e6c0f96fed003f767ee62ca74ff14e8ab69d"],["0412c0fbe2b54298a3b1dd346c78d3b56dda0e63","generator/candidates/GEN-EM-01/native/em_device_contract.c","f09603278215d960f9c7df5cc1aa812bffe0d365"],["d4ae3fa35412595a194c5f7c323cefb169722d19","generator/candidates/GEN-INTEGRATION-01/integration.h","490b09c4acb96ac9e857a6a55324c28c91c14f1f"],["d4ae3fa35412595a194c5f7c323cefb169722d19","generator/candidates/GEN-INTEGRATION-01/integration.c","c7fc2c90ea4b64aa5a5c9f25e0b202991b01b627"],["1bd0fe8c8a07ca64301ee89e1d26b46a33d554a3","generator/candidates/GEN-INTEGRATION-02/session.h","2376cab6bda0afb65da3d26e463c3cefba5f039b"],["1bd0fe8c8a07ca64301ee89e1d26b46a33d554a3","generator/candidates/GEN-INTEGRATION-02/session.c","b674b1ba9b5baad7eed8f083efda1726d81ec6d9"],["1bd0fe8c8a07ca64301ee89e1d26b46a33d554a3","generator/candidates/GEN-INTEGRATION-02/session_clock.h","0bd6de2e64d51f46e9d705548f5b73f3d4f6691b"],["1bd0fe8c8a07ca64301ee89e1d26b46a33d554a3","generator/candidates/GEN-INTEGRATION-02/session_clock.c","2ff29e1b367fa7fe0982f9af58c9b233d0945230"],["f20aa44d921c5455cd015eddb1bcde05549843a0","generator/candidates/GEN-PLATFORM-03/binding.h","f0c2cf430d59a46ffdf09938c86fea375d0a87f0"],["f20aa44d921c5455cd015eddb1bcde05549843a0","generator/candidates/GEN-PLATFORM-03/binding.c","6c5194155ac8f6beaa782d0930b141bde6bdfa51"],["6da9688f384beb020fd7f311ce96dc29330de5db","generator/candidates/GEN-PLATFORM-04/monitor.h","ceebd9f876ba54788754c6b14b2bfdf5b288dedc"],["6da9688f384beb020fd7f311ce96dc29330de5db","generator/candidates/GEN-PLATFORM-04/monitor.c","3874ef72b7a597db14489c7cc384c7965dc00667"],["19800411015599ab98c9b854024c0a125a4c7a4e","generator/candidates/GEN-PLATFORM-05/recovery.h","13dfea669ce0a4409914b419521b2d704492aaf9"],["19800411015599ab98c9b854024c0a125a4c7a4e","generator/candidates/GEN-PLATFORM-05/recovery.c","42707299d531619b07ca1dba0288b5a41c1aaa54"],["ef22815a739db53288d72890d6a3d217eb26417c","generator/candidates/GEN-PLATFORM-07/readiness.h","6cf37fdf6c67c53779215e2efac89ceda386050a"],["ef22815a739db53288d72890d6a3d217eb26417c","generator/candidates/GEN-PLATFORM-07/readiness.c","f35962888553f03a8f3d193661ea5b5d2402ff8e"],["ef22815a739db53288d72890d6a3d217eb26417c","generator/candidates/GEN-PLATFORM-07/mac_readiness.c","1dbb3d580dd7aec51048a7913012a4eb1fade2ae"],["8a1b5ce4bc653c725bfe473dea7301a934907dff","generator/candidates/GEN-PLATFORM-08/assembly.h","5fd071fe53c737bd1a8b744d6defcf0e9dfdbc14"],["8a1b5ce4bc653c725bfe473dea7301a934907dff","generator/candidates/GEN-PLATFORM-08/assembly.c","f508b864970512cdbc232bf831f222aa3cfe4fe1"],["ca86bb06b9f424716d277d4fa4a4998970062de6","generator/candidates/GEN-PLATFORM-09/digital_signal.h","1c087aa661a238d0c69e592d47a6cea8dcc1d07e"],["ca86bb06b9f424716d277d4fa4a4998970062de6","generator/candidates/GEN-PLATFORM-09/digital_signal.c","5239fc6f204fef96f84e09dee35ea74918f80d0c"],["5f78e64bb6824ca03f7ae01cee718b35a26c0385","generator/candidates/BENCH-03/lifecycle.h","73a5b79606aada3e76b66e12c4c04142a92ac4b3"],["5f78e64bb6824ca03f7ae01cee718b35a26c0385","generator/candidates/BENCH-03/lifecycle.c","c0214616a535f08f538da668c72b6b85f6fb0dc5"],["d9ba65bc0a4d5ef02838384242f78a11503511a0","generator/candidates/BENCH-04/transport.h","36b5fc865b218ce10940a30c0510ca9a47562a11"],["d9ba65bc0a4d5ef02838384242f78a11503511a0","generator/candidates/BENCH-04/transport.c","dfc9bbfb010e09e7413c1a42e87282d335e1bf33"],["d9ba65bc0a4d5ef02838384242f78a11503511a0","generator/candidates/BENCH-04/mac_transport.c","68372868456780bcb8c743f67f4fd656036cf0b6"]]
def verify(data,pin):
    if hashlib.sha1(("blob %d"%len(data)).encode()+b"\0"+data).hexdigest()!=pin:
        raise RuntimeError("BLOB_MISMATCH "+pin)
    return data
def main():
    if len(sys.argv)!=2 or platform.system()!="Darwin":raise SystemExit("USAGE_MAC: python3 -B qualify.py REPO")
    repo=pathlib.Path(sys.argv[1]).resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="freqmed_bench05_") as tmp:
        w=pathlib.Path(tmp)
        for name,pin in OWN.items():(w/name).write_bytes(verify((ROOT/name).read_bytes(),pin))
        names=set(OWN)
        for ref,path,pin in PINS:
            name=pathlib.Path(path).name
            if name in names:raise RuntimeError("DUPLICATE_SOURCE")
            names.add(name)
            data=verify(subprocess.check_output(["git","-C",str(repo),"show",ref+":"+path],timeout=30),pin)
            if name=="mac_readiness.c":
                s=data.decode("utf-8");marker="static const char *verdict(FMReadinessResult r) {"
                if s.count(marker)!=1:raise RuntimeError("COLLECTOR_BOUNDARY")
                (w/"mac_capture_pinned.inc").write_text(s.split(marker,1)[0].removeprefix("#define _POSIX_C_SOURCE 200809L\n"),encoding="utf-8")
            else:(w/name).write_bytes(data)
        print("BENCH05_SOURCE_PINS=%d/%d PASS"%(len(PINS)+len(OWN),len(PINS)+len(OWN)),flush=True)
        cc=["/usr/bin/cc","-std=c11","-Wall","-Wextra","-Werror","-pedantic","-I",str(w)]
        def build(name,sources,extra=()):
            exe=w/name
            subprocess.run(cc+[str(w/s) for s in sources]+["-lm",*extra,"-o",str(exe)],check=True,timeout=120)
            return exe
        test=build("test",["rt_queue.c","test_rt.c"],("-pthread",))
        result=subprocess.check_output([str(test)],text=True,timeout=20).strip()
        if result!="BENCH05_QUEUE_ASSERTIONS=29 PASS\nBENCH05_THREAD_BLOCKS=10000 PASS":raise RuntimeError("NEW_TEST_FAILED")
        print(result,flush=True)
        sources=["generator_core.c","output_hard_denied.c","em_device_contract.c","integration.c","session.c","session_clock.c","binding.c","monitor.c","recovery.c","readiness.c","assembly.c","digital_signal.c","lifecycle.c","transport.c","rt_queue.c","mac_rt.c"]
        exe=build("native",sources,("-framework","CoreAudio","-framework","CoreFoundation"))
        proc=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20)
        report=json.loads(proc.stdout)
        print("BENCH05_NATIVE_REPORT="+json.dumps(report,sort_keys=True,allow_nan=False),flush=True)
        ok=proc.returncode==0 and report["status"]=="PASS_MEMORY_ONLY_NATIVE_PROFILE" and report["guardian_off"] is True and report["queue_stopped"] is True and report["callback_contract_denied"] is True and report["blocks"]==2 and report["numerical_frames"]==2*report["output_frames"] and report["stream_opened"] is False and report["audio_ioproc_registered"] is False and report["physical_output"]=="NOT_PERFORMED"
        print("BENCH05_NATIVE_RT_CONTRACT="+("PASS" if ok else "BLOCK"),flush=True)
        if not ok:raise SystemExit(75)
if __name__=="__main__":main()
