# pyETC
HST-COS Exposure Time Calculator (ETC)

## Installation
Refer to the [Installation](Installation.md) documentation

## Dependencies

* `numpy`
* `astropy`
* `bs4`
* `selenium`

## Prerequisites

* [`Chrome driver`](https://chromedriver.chromium.org/downloads)
Ensure version match of your Google Chrome. It can be found under Settings > About Chrome. At least version 112.x is needed to be compatible with the latest version of Selenium. 
* [`Chrome binary location`](https://i.stack.imgur.com/yDGzQ.png)

## Setup

Edit the chromepaths.py file (located inside `etc` folder) to point to the paths of both the Chrome driver and Chrome binary location. 
