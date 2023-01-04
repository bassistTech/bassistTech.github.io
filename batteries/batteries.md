# What I've learned about 9-V rechargeable batteries

Francis Deck, 12-18-2022

I've been growing ambivalent about batteries. They're expensive and wasteful, and their lifetime is dependent on me remembering to unplug my gear when I'm not playing. I bought a couple of rechargeable 9-V batteries to try out in my preamps. These are LiPo "bag batteries" with a built-in step-up voltage regulator and charging circuit, in a package of the same size and shape as a 9-V battery. The ones I bought have a USB jack for charging. How convenient. I bought two from AliExpress: One to use, and the other to cut open.

The first thing I noticed is that the capacity ratings for some of the batteries sold online is stratospheric. One of the first hits on Amazon says 5400 mAh. A LiPo cell with that capacity can't fit into the 9-V package. The ones I bought had a more believable capacity rating of 650 mAh. Might as well start somewhere close to reality, right?

## Opening the box

Here's the one I took apart, taped back together so I can use it, and wired to the typical plug used by electric guitar effect pedals. The LiPo cell is marked as having 1000 mAh at 3.7 V. The output voltage measures at 9.2 V. Now do the math, you have to apply the step-up ratio to the capacity rating: (1000 mAh)(3.7 V)/(9.2 V) = 402 mAh. I'm not saying the 650 mAh rating is wrong, but it's not how I would rate it for comparison to a 9-V alkaline battery. The first hit on Google says a 9-V alkaline has 550 mAh. So far I'm satisfied enough to continue.

## Application: Musical instrument effect box

It's a prototype of my HPF-Pre Series 3 Mini box. What's inside is a simple audio circuit built around a high performance op amp chip. The power supply input is well decoupled, and the circuit board has a ground plane. 

I'm using my home audio test setup for measuring noise, described in another article.

On my first test, with a regular 9-V alkaline, I confirmed the datasheet spec for the equivalent input voltage noise density of the op amp in my box, rated at 4.5 nV/rtHz (nanoVolts per square root of Hz). My circuit uses 3 sections of the op amp, with unity gain, so it should produce about 7.8 nV/rtHz of noise, and my measurement comes out to 9.2 nV/rtHz. I haven't modeled the noise of the circuit any further than that for this exercise.

With the rechargeable, the noise floor increased roughly 10-fold. Out comes my oscilloscope. Naturally a step-up regulator is going to produce switching noise. On the battery that I bought, the switching frequency seems to be about 20 kHz, an annoying dip into the audio band, but perhaps manageable. However, regulation of the output voltage by varying the duty cycle potentially feeds noise in the modulation signal to the output, and it could be broadband. The spectral display on my audio analysis program certainly shows broadband noise.

Fortunately a simple mitigation cleaned it up. Based on parts that I had on hand, I added a RC filter at the power jack of my device, 51 Ohms and 10 uF, and it cleaned things up almost completely. I'm going to apply a couple of rules to my designs, in order to accommodate these batteries:

1. Don't let the noise into your box. I'm going to add that RC filter directly to the power jack on my box, using through-hole components.

2. Good hygiene is to keep power and signal wiring separate inside the box.

## Battery lifetime

A 9-V alkaline battery has a gentle discharge curve. Not the LiPo. I've found out that when the rechargeable runs out of juice, it just shuts down without warning. You don't want this happening in a performance, so it's prudent to bring a fully charged battery to a gig.