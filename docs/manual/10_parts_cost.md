\clearpage

# Parts and cost

This chapter is a ledger. Each order, meaning each movement of money, is recorded in `docs/data/orders.toml` and broken down into line items with a category (parts, manufacturing, labour, fees, shipping, tax, discounts, and so on; a discount is a negative line). **Paid** orders carry the real amounts from the invoice, and the build refuses to run if their lines do not add up to the invoice total. **Planned** orders are not placed yet; their lines are **ESTIMATES in pounds** from shop listings seen during the design (the print price is an assumed price per cm³, not a quote). When an order is placed, its estimates are replaced by the invoice lines.

## Ledger

<!-- include: tables/bom_cost.md -->

## By order and by category

![Cost by order and by category (solid = paid, hatched = estimate, grey tail = up to the high estimate), and each category's share of the spend. Discounts are negative and left out of the share bar.](figures/costs/breakdown.png)

<!-- include: tables/cost_category.md -->

**£300.05 has been paid** so far (every order, see the ledger above); the projected total, once the UK import charges on the exciters are added, is about **£305 – 317**. The prints are priced with JLC3DP's real rule from a quote (a $0.95 minimum per file, then about $0.34 per cm³). They are 14 single files (one spring-jaw clip + arm per ear in two grips, two extra arm thicknesses, the bears and the bee; see [The mechanics, and why](#the-mechanics-and-why)), because JLC3DP treats a file holding several loose parts as an assembly and wants it split. Nothing is left to order: the only open item is the UK import VAT and any courier fee on the exciters.

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

## Where each part came from

| part | source | note |
|---|---|---|
| The three boards, assembled | JLCPCB, three orders in one parcel | `pcb/fab/` holds the gerber, BOM and placement zips; 5 of each board |
| 3D prints, 14 files | JLC3DP, MJF nylon PA12 | dyed black: clips, arms and bee base; natural grey: the rest; bears and bee ordered twice |
| Exciters, 3 | SoundImports (Netherlands) | no UK stockist was found; import VAT is still to come |
| XIAO nRF52840 ×2, LiPo, ribbon cable | The Pi Hut | the cable is 30 AWG, 4 wires, 5 pieces: its 0.8 mm wires make a ribbon about 0.8 × 3.2 mm, while 28 AWG (1.2 mm) is too fat for the cable slot |
| JST-PH socket and slide switch | LCSC | the minimum order was 20 of each |
| Hardware, consumables, tools | Amazon UK, one checkout, £82.15 | stainless screws (M1.6 × 4 and M2 × 4 are the sizes needed, **not 5 or 8 mm**), ear hooks and 4 mm jump rings, a 2 mm chain, wire, heat-shrink, twist ties, epoxy, silicone, gesso, paints; the owner already had solder, strippers, tweezers, a multimeter, a screwdriver, sandpaper and painter's tape |

**Lead times (rough).** JLCPCB: 24 hours to build and 1 – 2 days of assembly, plus courier 2 – 4 days; prints 1 – 2 weeks; exciters 1 – 3 weeks; UK shop items 2 – 3 days.

## Not in the ledger

A second PCB revision if any board has a mistake (none has been powered), shipping delays, spare microphones, and any tool you do not already own.
