# Vendored footprint libraries

Footprints and 3D models converted from the JLCPCB/LCSC (EasyEDA) parts with `easyeda2kicad` ([@easyeda2kicad]), so the pads match the parts JLCPCB will actually place.

| file | part | LCSC |
|---|---|---|
| `lib/parts.pretty/TQFN-16_...EP1.5` | MAX98357AETE+T amplifier | C910544 |
| `lib/parts.pretty/MIC-SMD_5P_...SPH0641LU4H-1` | SPH0641LM4H-1 PDM microphone | C497724 |
| `lib/parts.pretty/SOT-23-3_...` | XC6206P332MR-G LDO | C5446 |
| `carrier/lib/sw.pretty/SW-TH_SK12D07VG4` | SK12D07VG4 slide switch | C393937 |

The 3D models (`*.3dshapes`) are only used for the KiCad 3D renders. To regenerate one:
`uvx easyeda2kicad --lcsc_id=C910544 --full --output pcb/lib/parts`.
The microphone footprint's own 0.5 mm acoustic-port pad is turned into an NPTH hole in `build_dangle.py`.
