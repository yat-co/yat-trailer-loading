# YTL - YAT Trailer Loading Package

Simple package for turning list of freight pieces into a trailer plan and
associated metrics helpful for LTL (Less than Truckload) and Partial planning 
and pricing.


## Install

## Usage

## Reference

Portions of this package make use of an optimization presented by Dube and Kanavalty in the conference papaer cited below.  There is a Python implementation of this algorithm available at `https://pypi.org/project/py3dbp/`, which is a derivative work of a Go implementation available in `https://github.com/bom-d-van/binpacking` (The article by Dube and Kanavalty is also available in this GitHub repository).  The `py3dbp` Python implementation, with minor variations to suite our purposes, is in the `ytl.py3dbp` module of this package and leveraged in portions of the trailer load optimization services.

```
E. Dube and L. Kanavalty, "Optimizing Three-Dimensional Bin Packing Through Simulation", Proceedings of the Sixth IASTED International Confernece Modelling, Simulation, and Optimization pp. 1-7, September 11-13, 2006, Gaborone, Botswana.
```
