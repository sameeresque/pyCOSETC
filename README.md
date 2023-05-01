# pyETC
This is a tool to scrape information from the [exposure time calculator](https://etc.stsci.edu/etc/input/cos/spectroscopic/) website hosted by STScI. It is intented to provide a convenient and automated way to perform the task of clicks, inputs, and selections without the user having to interact with the web interface, allowing one to perform repeated simulations for various parameter settings/multiple objects/both. Currently, this is only setup for use with COS G130M and G160M gratings. It returns the COS request ID, time on source, and buffer times. See function help for more information.

## Installation
Refer to the [Installation](Installation.md) documentation

## Dependencies

This program sends HTTP requests to the source website using Selenium and then parses the HTML content using Beautiful Soup. Astroquery is used to determine the extinction value in the direction of object of interest. 

* `numpy`
* `astropy`
* `astroquery`
* `bs4`
* `selenium`

## Prerequisites

* [`Chrome driver`](https://chromedriver.chromium.org/downloads)
Ensure version match of your Google Chrome. It can be found under Settings > About Chrome. At least version 112.x is needed to be compatible with the latest version of Selenium. 
* [`Chrome binary location`](https://i.stack.imgur.com/yDGzQ.png)

## Setup

Edit the `chromepaths.py` file (located inside `etc` folder) to point to the paths of both the Chrome driver and Chrome binary location. 

## Example Usage

```
import etc
help(etc.cosetc)
etc.cosetc(detector="fuv",grating = "g130m",aperturetype="PSA",snrval=12.0,redshift_qso=0.1,qso_ra=8.565,qso_dec=35.902,redshift_abs=0,fuvval=19.0,wav_int=1206)
```

## Default settings
### Target
* Spectrum: Non-stellar Objects QSO (COS based) [473, 1784 Å z=0]
* Extinction: Milky Way Diffuse (Rv=3.1) = (Parameter input) applied before normalization
* Normalization: Renormalized to abmag = (Parameter input) in filter Galex/FUV
* Emission Lines: None
### Selected background
* Earth Shine: Average
* Zodiacal Light: Average
* Air Glow: Average

## Demo
https://user-images.githubusercontent.com/16863470/235333778-5b0dff1b-6f62-4118-9d5b-8b91291d0eaa.mp4

## Acknowledgement & Copyright

The information retrieved by this code is obtained by scraping data from the [COS Spectroscopy ETC](https://etc.stsci.edu/etc/input/cos/spectroscopic/). We acknowledge and respect the intellectual property rights of the source website and the authors of the content we have scraped. No copyright infringement is intended in this repository. The content used here abides by the content [use policy of the source](https://www.stsci.edu/copyright).
