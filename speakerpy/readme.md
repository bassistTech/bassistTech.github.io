# Basic modeling of sealed and ported speakers

Francis Deck, 3/15/2024

## Overview

This is a Web-based program for modeling sealed and ported loudspeakers using the basic electromechanical model described in my articles at this site.

It was an exercise to learn some new programming techniques, but it's offered here in case it might be useful.

## Links

Here's the app: [https://bassisttech.github.io/speakerpy/build/web](build/web/index.html)

[Speaker theory article](https://github.com/bassistTech/SpeakerTheory/blob/master/SpeakerTheory.pdf)

## MIT License

Copyright 2024 Francis Deck

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Motivation

This program is offered in the spirit of a programming exercise that happens to be useful. It's the result of looking for the easist possible way to create a Web app in Python.

I've always been interested in DIY music gear, including speakers. When web forums began to emerge for bassists, I noticed comments like "tens are fast and fifteens are deep, because physics." I immediately asked myself: "What physics?" and launched a project to find the actual physics underlying the behavior of speakers.

I'm a physicist, and don't have an engineering background, so my approach is noticeably physics-y. A scientist is constantly faced with the question: How do I know that I'm on the right track? How can I check this? Why should anybody believe it?

These modeling programs are part of my approach, because I can use them to "connect" my equations with accepted software and my own measurements. I've checked the graphs produced by my program with one popular app, WinISD. The graphs match quite closely, if I account for a difference in how my program computes the input voltage. This agreement would be unliklely if there were an error in my assumptions or calculations. I've also built speakers and measured their response and impedance curves.

## Cautions

I'm not an engineer, and this program has not been checked by any third party for correctness or accuracy. Do not use this program for actual design purposes unless you check the results against other accepted software or formulas.