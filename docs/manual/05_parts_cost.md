\clearpage

# Parts and cost

All prices are **ESTIMATES in pounds** from shop listings seen during the design; none has been quoted for this exact order. The model that produced this chapter is `docs/data/parts.toml`; change a price there and re-run `make docs`.

## Bill of materials and cost breakdown

<!-- include: tables/bom_cost.md -->

![Cost breakdown by group (solid = low estimate, hatched = up to the high estimate) and each group's share of the mid-point.](figures/costs/breakdown.png)

**The budget is exceeded.** The original ceiling was about £200 ("flexible"); the estimate is about £215 – 330 once painting supplies, hooks and the full print set are included. The levers, in order of effect:

1. Print fewer clip sizes (the *lean* set is about half the volume).
2. Two exciters instead of three, one XIAO instead of two.
3. Skip the paint and hooks if you already own them.

## Ordering checklist

1. **JLCPCB, three separate orders** (so the two dangle variants keep their own BOM and CPL): `pcb/fab/dangle_L.zip`, `dangle_R.zip`, `carrier.zip` with the matching `*_BOM.csv` and `*_CPL.csv`. Check the 3D preview for part rotation, the microphone stock, and which parts are *extended*. Choose economic PCBA, 2 assembled boards each. (**Not yet verified:** CPL rotations, acceptance of the 0.5 mm NPTH, the silkscreen preview of the Helvetica signature.)
2. **3D prints**: upload the files in `cad/print/` to JLC3DP or a UK MJF bureau for an instant quote; choose MJF nylon PA12, grey. Decide between the full set and the lean set after seeing the price.
3. **Exciters** (3 × DAEX-9-4SM): no UK stockist was found; order EU/US and allow for import VAT.
4. **XIAO nRF52840 ×2, LiPo, ribbon cable**: The Pi Hut or similar UK shop.
5. **Hand-soldered parts**: JST-PH S2B-PH-K socket and SK12D07VG4 switch (LCSC numbers in the carrier BOM).
6. **Hardware and consumables**: M1.6 × 5 and M2 × 8 screws, earring hooks, foam ring or silicone, flux, wire, heat-shrink, velcro ties, paint.

**Lead times (rough).** JLCPCB assembly 3 – 7 days plus courier 3 – 6 days; prints 1 – 2 weeks; exciters 1 – 3 weeks; UK shop items 2 – 3 days.

## Not in the budget

A second PCB revision if any board has a mistake (none has been powered), shipping delays, spare microphones, and any tool you do not already own.
