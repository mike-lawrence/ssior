pyStamper
=========

Assumes you've installed SDL2/PySDL2 with these modifications: https://gist.github.com/mike-lawrence/8326880

Also assumes you've installed billiard (https://github.com/celery/billiard). If running on Mavericks, you should also install appnope (https://github.com/minrk/appnope).

Works optimally with a dual display system, where you can put the stimulus presentation stuff on one screen while keeping the pyStamper window in the forefront on the other screen (pyStamper needs to be the active window to catch input events). If you have a single-display setup, you could possibly also get away with initializing pyStamper after the main display window and doing so with a 1x1 borderless window and a color/placement somewhere unobtrusive.
