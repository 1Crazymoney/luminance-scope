luminance-scope
===========

Shows real-time graphs of luminance in video streams.

Dependencies:

* Python 
* OpenCV
* scipy / numpy
* matplotlib

Usage
-----

To analyze data from the default camera, run

    ./luminance-scope.py

If everything worked you should see a graph similar to this:

![screenshot](https://raw.github.com/MagnusS/luminance-scope/master/screenshot.png)

The console output should look something like this:

    # Luminance threshold is  245
    # Neither file or camera index specified. Trying to use camera 0 ...
    # Real time graph will be updated every 30 frame(s)
    # Importing OpenCV...
    # Camera has unknown frame rate. Falling back to 30.0  fps
    # Starting OpenCV capture
    # frame: 30 fps: 29.8577836035 qlen: 0 miny: 0.0 maxy: 32.727516276
    # frame: 60 fps: 29.2231891099 qlen: 0 miny: 0.0 maxy: 32.8951855469
    # frame: 90 fps: 29.2392014851 qlen: 0 miny: 0.0 maxy: 32.9466341146
    # frame: 120 fps: 29.234724674 qlen: 0 miny: 0.0 maxy: 32.9622298177
    # frame: 150 fps: 29.2101572108 qlen: 0 miny: 0.0 maxy: 32.9622298177
    ...

The program is terminated by pressing CTRL-C in the console.

You can manually set the camera, frame rate, update interval and luminance threshold from the command line. For more information, see

```
./luminance-scope.py -h
```
