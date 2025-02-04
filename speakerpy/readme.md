# Basic modeling of sealed and ported speakers

Francis Deck, 3/15/2024

Update 2/3/2025

## Overview

This is a Web-based program for modeling sealed and ported loudspeakers using the basic electromechanical model described in my articles at this site.

It was an exercise to learn some new programming techniques, but it's offered here in case it might be useful.

## Links

The web app loads slowly, so give it a minute.

Here's the web app: [https://bassisttech.github.io/speakerpy/build/web](build/web/index.html)

Here's the source code: [https://github.com/bassistTech/bassistTech.github.io/tree/main/speakerpy](https://github.com/bassistTech/bassistTech.github.io/tree/main/speakerpy)

The speaker theory article is a PDF. It's easier to read if you download it and read it offline.

Here's the speaker theory article: [https://github.com/bassistTech/SpeakerTheory/blob/master/SpeakerTheory.pdf](https://github.com/bassistTech/SpeakerTheory/blob/master/SpeakerTheory.pdf)

## MIT License

Copyright 2024 Francis Deck

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Minimal instructions

The program uses the bare minimum number of Thiele-Small parameters that are needed for the basic electromechanical model. These have to be in the units shown in the program, all metric. Very few if any credible driver makers still use US units. If the maker doesn't offer parameters, it's because they might not know what they are.

**How do I load and save designs**? When you update the graphs, the design parameters are loaded into a text box at the bottom of the page. You can copy them into a text editor and save them. Then you can paste a set of parameters back in there and click on "load design parameters from below." Hopefully you will be successful.

I prefer text based file formats for my programs, because there's nothing hidden. Likewise with my source code. My intention here is that everything is open, all the way down to the underlying theory.

Goodies like file storage and error checking are more than I've had a chance to work on, and raise the complexity of an app exponentially. This is a big part of the reason why software is costly to develop. Also, your browser deliberately limits the ability of my program to access the files in your computer, for security reasons. I also feel more comfortable knowing that my program can't do any serious damage. It makes sharing simple apps a lot easier.

**Do I trust the port length calculations**? No. These are straight from my formulas, and I've checked them against formulas published online. But figuring out the effect of the port ends is tricky when big ports are crammed into small boxes, as is common with musical instrument speakers. Don't leave yourself with no way to change the port length after you've built the box and measured its tuning.

**Do I trust anything**? No. Before you commit to buying drivers and cutting plywood, it would be a very good idea to get a second opinion from another program. Also, there are some smart people on the Talkbass forum who will critique your design if you post about it there.

## Motivation

This program is offered in the spirit of a programming exercise that happens to be useful. It's the result of looking for the easist possible way to create a Web app in Python.

I've always been interested in DIY music gear, including speakers. When web forums began to emerge for bassists, I noticed comments like "tens are fast and fifteens are deep, because physics." I immediately asked myself: "What physics?" and launched a project to find the actual physics underlying the behavior of speakers.

I'm a physicist, and don't have an engineering background, so my approach is noticeably physics-y. A scientist is constantly faced with the question: How do I know that I'm on the right track? How can I check this? Why should anybody believe it?

These modeling programs are part of my approach, because I can use them to "connect" my equations with accepted software and my own measurements. I've checked the graphs produced by my program with one popular app, WinISD. The graphs match quite closely, if I account for a difference in how my program computes the input voltage. This agreement would be unliklely if there were an error in my assumptions or calculations. I've also built speakers and measured their response and impedance curves.

## Cautions

I'm not an engineer, and this program has not been checked by any third party for correctness or accuracy. Do not use this program for actual design purposes unless you check the results against other accepted software or formulas.

## Update history

**2/3/2025** No functional changes. I updated the program so it works with the latest version of **flet** which is still in development.