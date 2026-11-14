# GEN-R4 technical delta

Adds a private CoreAudio default-output fingerprint (ephemeral OS token, sample-rate, output channels). Intended physical audio backend checks it before queue setup, before the prospective call to AudioQueueStart, and in its watchdog loop. On route drift, immediately stops the queue. The actual objects are compiled and preserved but not linked or loaded in the runnable binary.

Known limitations: polling cannot guarantee an unchanged output between checks and does not pin an AudioQueue to a transducer. The software stop is not an independent physical interlock. The UI cannot switch on emission. No real sound or EM frequency was generated, and zero scientific experiments were performed.
