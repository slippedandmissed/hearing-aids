```{=latex}
\thispagestyle{empty}
\AddToShipoutPictureBG*{\includegraphics[width=\paperwidth,height=\paperheight]{figures/overview/cover.png}}
\mbox{}
\clearpage
```

# Summary {-  .unlisted}

This project is the design of a pair of hearing aids for conductive hearing loss, in which sound is delivered by bone conduction and the ear canal is left open.

**Background.** In conductive hearing loss, sound is attenuated before it reaches the inner ear. Here the cause is earwax blockage in both ear canals. The inner ear itself is unaffected. Vibration applied to the skull reaches the inner ear without passing through the ear canal; this is bone conduction.

**Design.** Each ear has a microphone, an amplifier and a bone-conduction vibrator (an *exciter*). One microcontroller, in a necklace pendant, processes the signals for both ears. The microphone and amplifier are on a small circuit board inside an earring. The exciter is held against the mastoid bone behind the ear by a printed spring arm that clips onto the wearer's glasses. A thin cable per ear runs along a necklace chain to the pendant, which also contains the battery.

**Status.** The design is complete on screen: CAD models, three circuit boards, print files and a firmware skeleton. The three circuit boards were ordered on 2026-11-22; nothing has been built or tested, and the prints and other parts are not yet ordered. It is a personal project and is not a medical device.

![Sound paths to the inner ear. Left: the air route through the ear canal, blocked by wax. Right: the bone route from an exciter behind the ear.](figures/overview/why_bone.png)

![Signal path in four stages.](figures/overview/four_steps.png)

\clearpage

# Arrangement {-  .unlisted}

The earrings are shaped like gummy bears (pink for the left ear, blue for the right) and the pendant like a bee. These shapes are cosmetic. Each earring contains the microphone and amplifier. The cables run down the neck, along the chain, to the pendant, which contains the microcontroller module and the battery.

![The assembly on a generic model head and shoulders (a stand-in, not a portrait of anyone).](figures/overview/worn_front.png){width=68%}

\clearpage

# One ear in detail {-  .unlisted}

A clip attaches to the arm of each side of the glasses. It carries a spring arm that passes around the ear and presses the exciter against the mastoid bone behind it. The microphone opening is in the front of the earring.

![Left ear from the side.](figures/overview/worn_ear.png){width=100%}

\clearpage

# Parts {-  .unlisted}

![The six kinds of part. Everything except the exciter, the battery and the microcontroller module is designed in this project.](figures/overview/parts.png)

\clearpage

# Construction {-  .unlisted}

An earring consists of a shell, a foam sealing ring, a circuit board and a back plate, fixed with four screws. The pendant consists of a base, a battery, a carrier circuit board with the microcontroller module, and a cover.

![](figures/overview/explode_bear.png){width=62%}

![](figures/overview/explode_bee.png){width=62%}

\clearpage

```{=latex}
\tableofcontents
\clearpage
```
