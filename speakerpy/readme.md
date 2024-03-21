# Basic modeling of sealed and ported speakers

Francis Deck, 3/15/2024

## Overview

This is a Web-based program for modeling sealed and ported loudspeakers using the basic electromechanical model described in my articles at this site.

## Take me to the app

https://bassisttech.githug.io/speakerpy/build/web

## MIT License

Copyright 2024 Francis Deck

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Motivation

This program is offered in the spirit of a programming exercise that happens to be useful. I've been programming since 1981, and over the decades have spent some time keeping up with developments in languages and tools, through home projects like this one.

My latest interest is in the recent porting of the standard Python interpreter to Web Assembly, allowing Python programs to run in the browser. This has been combined with some other tools in the **flet** package to allow creation of graphical Web applications, or "web apps."

Web apps have proven to be a way of developing apps that will run on any system that supports a modern browser. In a sense, *the browser is the new OS*. It solves the problem of trying to write an app that targets every platform: Windows, Mac, Linux, Chrome, Android, etc. 

So I took my existing speaker modeling code, converted it into a **flet** app, and am sharing it here. It follows my time-tested approach to GUI design, which is: *Ugly but functional*. I started with all of the layout defaults provided by the tool -- in this case **flet**, and added only enough modifications to make the resulting interface tolerable to use.

As I learn more about creating robust and useful web apps, I'll test my learning by updating this program.

## Cautions

I'm not an engineer, and this program has not been checked for correctness or accuracy. This is not engineering software. Before committing to building a speaker, I recommend getting expert advice, and checking my results against other software that's available.