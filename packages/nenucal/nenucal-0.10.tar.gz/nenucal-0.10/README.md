NenuCAL CD
==========

Calibration pipeline and set of utilities for the NenuFAR Cosmic Dawn project. The calibration uses the standard LOFAR [DPPP](https://github.com/lofar-astron/DP3/tree/master/DPPP) in the background and should be general enough to be used by any NenuFAR projects.

Installation
------------

nenucal-cd can be installed via pip:

    $ pip install nenucal-cd

and requires Python 3.7.0 or higher. For most tasks, you will also need [DPPP](https://github.com/lofar-astron/DP3/tree/master/DPPP), [LSMTool](https://www.astron.nl/citt/lsmtool/overview.html) that you can install with the command:

    $ pip install git+https://github.com/darafferty/LSMTool.git

and [LoSoTo](https://revoltek.github.io/losoto/) that you can install with the command:

    $ pip install git+https://github.com/revoltek/losoto

Usage
-----

Calibration is performed using the `calpipe` utility. You will find [here some documentations](https://gitlab.com/flomertens/nenucal-cd/-/wikis/Calibrating-NenuFAR-data) on how to use it.

Additionally to calpipe, this package provides a tool to manage the FLAG column and run a SSINS flagger ([flagtool](https://gitlab.com/flomertens/nenucal-cd/-/wikis/flagging-utility)), a tool to plot and smooth gain solutions ([soltool](https://gitlab.com/flomertens/nenucal-cd/-/wikis/soltool-utility)) and a tool to produce apparent sky model from catalog ([modeltool](https://gitlab.com/flomertens/nenucal-cd/-/wikis/sky-model-utility)).

Contact
-------

Do not hesitate to fill an [issue](https://gitlab.com/flomertens/nenucal-cd/-/issues) or contact me if you encounter a problem with this package.
