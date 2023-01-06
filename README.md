# Spectrometer
![](/images/intensity2.png)

Based on Public Lab Spectrometer 3.0: https://publiclab.org/notes/abdul/10-13-2016/desktop-spectrometry-starter-kit-3-0-instructions

Using a USB camera module similar to:

- [Arducam OV5648](https://www.arducam.com/product/arducam-ov5648-auto-focus-usb-camera-ub0238-6/)
- [Newcamermodule 5MP CMOS Sensor](https://newcameramodule.com/product/small-size-5mp-cmos-sensor-usb-2-0-camera-module/)

Camera, diffraction grating, slit are mounted on magnets and placed on a metal sheet.  Positions adjusted until a clear spectrum is seen:

![Setup](/images/setup.JPG)
	
Covered with black paper to keep room light out.  The old enlarger head seemed like a good idea with its condensing lens and iris.  On the other hand, taking the lens and iris out, just using some layers of wax paper in the negative carrier, works pretty well too... 

Camera connected to Raspberry Pi (4)), running Python/Pygame, Gnuplot, Bash

- Alignment is critical
- Focus is critical.  The camera I’m using  can be manually focused, but it’s not easy.  I hot-glued a tooth-pick to the side of the lens to make it easier to adjust.
- Exposure is critical.  Too much light will blur the spectrum.


## Spectrum Averaging

[spectralAverage.py](/python/spectralAverage.py)

Use the Python script to select a line through the spectrum, which will get averaged over time and duplicated vertically:

![Averaged](/images/cfl-spectrum-20181215-123051.jpg)
## Calibration

There are (at least) two ways to calibrate the output:
- calibrate to features in the spectrum (CFL Calibrate)
- calibrate to features of the camera (CIS Calibrate)


### CFL Calibration
The CFL spectrum has several clear landmarks: [CFL Landmarks](https://commons.wikimedia.org/wiki/File:Fluorescent_lighting_spectrum_peaks_labelled.svg)

Using the peaks at Hg436 and Eu611 gives this for the scale:

![Calibrated](/images/cfl-spectrum-20181215-123051-Overlay.png)

### CIS Calibration

But what about "smooth"" spectra:

![Broad](/images/air-spectrum-20181215-164105-Overlay.png)
 
It’s doesn't have any prominate peaks, but it does have three noticeable bumps at the RGB peak sensitivities of the Color Imaging Sensor (CIS):

- Red: 580 nm
- Green: 515 nm
- Blue: 475 nm

[Camera Spectral Response](https://photo.stackexchange.com/questions/122037/why-do-typical-imaging-sensor-colour-filter-spectral-responses-differ-so-much-fr)

Using those values for the scale gives a good match to the CFL calibration:

![CFL-CIS](/images/CFL-CIS.png)

### Auto Calibration?

-- Seems like you should be able to take the RGB values of a pixel, convert it to HSV, then map the Hue (H) to Wavelength (nm).  Almost works, but not quite… 


## Different Light Sources
## Plotting
### Overlay
### Intensity
