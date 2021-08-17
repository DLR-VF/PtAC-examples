# PtAC Examples

PtAC is a Python package to automatically compute walking accessibilities from
residential areas to public transport stops for the Sustainable Development Goal 11.2
defined by the United Nations. The goal aims to measure and monitor the proportion of
the population in a city that has convenient access to public transport
(see [https://sdgs.un.org/goals/goal11](https://sdgs.un.org/goals/goal11)).
With this library users can download and process [OpenStreetMap](https://www.openstreetmap.org) (OSM) street networks and population
information worldwide. Based on this it is possible to calculate accessibilities from
population points to public transit stops based on minimum street network distance.

This repository contains usage examples of accessibility module as well as population
module along with the necessary datasets to demonstrate the features of PtAC.
You can find all the examples on
[notebooks](https://github.com/DLR-VF/PtAC-examples/tree/master/notebooks) folder.

# Usage

In order to run the [examples](https://github.com/DLR-VF/PtAC-examples/tree/master/notebooks), 
jupyter notebook should be installed and [PtAC-examples](https://github.com/DLR-VF/PtAC-examples) repository should be cloned:

**1. open the Anaconda prompt (can be found on windows start menu) and navigate to your home folder**

```
cd C:\Users\ptac_user
```

**2. activate the conda environment in which ptac package is already installed 
(see [user guide](https://github.com/DLR-VF/PtAC/blob/master/docs/source/user-guide.rst) to learn how to install ptac)**

```
conda activate ptac
```

**3. install jupyter notebook by typing**

```
conda install -c conda-forge notebook
```

**4. clone the github repository into working directory by typing**

```
git clone https://github.com/DLR-VF/PtAC-examples.git
```

**4. navigate to the directory of cloned repository:**

```
cd C:\Users\ptac_user\PtAC-examples
```

**5. launch the notebook with the following command:**
```
jupyter notebook
```


# More info:


* [PtAC repository](https://github.com/DLR-VF/PtAC)


* [Documentation](https://test.pypi.org/project/ptac/)
