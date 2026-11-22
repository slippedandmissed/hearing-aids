\clearpage

# Parts and cost

This chapter is a ledger. Each order, meaning each movement of money, is recorded in `docs/data/orders.toml` and broken down into line items with a category (parts, manufacturing, labour, fees, shipping, tax, discounts, and so on; a discount is a negative line). **Paid** orders carry the real amounts from the invoice, and the build refuses to run if their lines do not add up to the invoice total. **Planned** orders are not placed yet; their lines are **ESTIMATES in pounds** from shop listings seen during the design (the print price is an assumed price per cm³, not a quote). When an order is placed, its estimates are replaced by the invoice lines.

## Ledger

<!-- include: tables/bom_cost.md -->

## By order and by category

![Cost by order and by category (solid = paid, hatched = estimate, grey tail = up to the high estimate), and each category's share of the spend. Discounts are negative and left out of the share bar.](figures/costs/breakdown.png)

<!-- include: tables/cost_category.md -->

**The budget is exceeded.** The original ceiling was about £200 ("flexible"). **£94.84 has been paid** (the three PCB orders); the projected total, with the estimates for everything still to buy, is about **£239 – 322**. The levers, in order of effect:

1. Print fewer clip sizes (the *lean* set is about half the volume).
2. Two exciters instead of three, one XIAO instead of two.
3. Skip the paint and hooks if you already own them.

## The JLCPCB order (2026-11-22)

All three boards were ordered together, **5 boards and 5 assembled of each**, in the JLCONE desktop app, which gave a discount that the website did not. The choices, and why:

| choice | setting | reason |
|---|---|---|
| Layers, size, thickness | 2 layers, read from the gerbers, 1.6 mm | the printed housings assume a 1.6 mm board |
| Colour, material | green, FR-4 TG135 | cosmetic; the boards are hidden inside the bear and the box |
| Surface finish | lead-free HASL (+ £0.84 per dangle order) | OSP, the default, wears off in the assembly oven and the bare wire pads are hand-soldered later; ENIG costs about £12.70 more per order; lead-free because it is worn on the body |
| Silkscreen | standard ink-jet | high-precision costs about £12.60 more per order; the text is 0.17 mm lines, above the checker's limit |
| Production file confirmation | no | the files were already checked in JLCPCB's DFM tool and the assembly step has its own review |
| PCBA type | economic, top side | the standard type needs boards of 70 × 70 mm or more |
| Assembled quantity | 5 of each | the extra boards cost little (the fixed fees are per order), and a single SMD defect cannot be repaired by hand |
| Confirm parts placement | no | the placement was checked in their preview; they also run a placement analysis 4 – 6 hours after the order |
| Parts selection | by customer | exact LCSC part numbers are in the BOM files |
| Terms and conditions | accepted (pre-ticked; the owner agreed) | |
| Shipping | the three orders together (one parcel, DHL Express) | the single biggest saving |

The microphone (LCSC C497724) is an *extended* part that JLCPCB flags as difficult; the order includes it, so expect a review and possibly an email. The website unticks the microphone and the ten 33 Ω resistors every time a BOM is re-uploaded; they were ticked again before saving each order.

## Ordering checklist

1. **JLCPCB, three separate orders: DONE 2026-11-22** (see above): `pcb/fab/dangle_L.zip`, `dangle_R.zip`, `carrier.zip` with their `*_BOM.csv` and `*_CPL.csv`.
2. **3D prints**: upload the files in `cad/print/` to JLC3DP or a UK MJF bureau for an instant quote; choose MJF nylon PA12, grey. Decide between the full set and the lean set after seeing the price.
3. **Exciters** (3 × DAEX-9-4SM): no UK stockist was found; order EU/US and allow for import VAT.
4. **XIAO nRF52840 ×2, LiPo, ribbon cable**: The Pi Hut or similar UK shop.
5. **Hand-soldered parts**: JST-PH S2B-PH-K socket and SK12D07VG4 switch (LCSC numbers in the carrier BOM).
6. **Hardware and consumables**: **screws** (A2 stainless pan head, cross recess: M1.6 × 4 mm for the bears, 12 pieces; M2 × 4 mm for the box, 4 pieces; **not 5 or 8 mm**, which would reach the end of the hole or poke out of the back), earring hooks, foam ring or silicone, flux, wire, heat-shrink, velcro ties, paint.

**Lead times (rough).** JLCPCB: the quotes said a 24-hour build and 1 – 2 days of assembly, plus courier 2 – 4 days; prints 1 – 2 weeks; exciters 1 – 3 weeks; UK shop items 2 – 3 days.

## Not in the budget

A second PCB revision if any board has a mistake (none has been powered), shipping delays, spare microphones, and any tool you do not already own.
