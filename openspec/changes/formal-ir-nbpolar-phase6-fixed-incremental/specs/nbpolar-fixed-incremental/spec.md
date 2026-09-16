# Fixed incremental NB-Polar requirements

## Requirement: Disclosure sets are nested and counted once

The implementation SHALL use the frozen sizes 29, 33, 37, 41 and 45 from one
worst-first order. It SHALL publish only newly added coordinate/value pairs and
SHALL count each disclosed GF32 coordinate once.

## Requirement: Every decode restarts

Every invoked level SHALL run SC from scratch. No decoder state or belief SHALL
cross levels.

## Requirement: Tag use is fail closed

A tag SHALL only accept the current candidate or advance to the immediately
next frozen level. It SHALL NOT rank candidates, select among candidates,
modify decoding or skip a level. Every invocation SHALL be counted.

## Requirement: Paired development criterion is preregistered

The single development run SHALL compare static K45 and incremental arms on
the same 300 synthetic blocks. Incremental acceptance requires zero undetected,
at least 285 exact blocks, Wilson lower bound at least 0.90, and at least 5%
lower average key-dependent disclosure than the paired static arm.
