# YTL - YAT Trailer Loading Package

Simple package for turning list of freight pieces into a trailer plan and associated metrics helpful for LTL (Less than Truckload) and Partial planning and pricing.  The package includes an out-of-the-box trailer load optimization allowing for flexible trailer dimension options, allows or disallows stacking/rotating of pieces, and handling of overweight shipments/pieces.  A detailed load plan is returned, as wells as several measurements like linear feet, actual volume, cubed volume, and effective trailer volume occupancy of the load plan.

The aim of the optimization is to load the provided shipments/pieces into a trailer of the specified dimensions with minimal linear foot occupancy of the trailer.  The default configuration makes it easy to plug and play to use in your own Python development or in an internally hosted API (see accompanying `yat-trailer-loading-api` for a simple Python Flask implementation).

Beyond the standard out-of-the-box style implementation, the package is readily available for development of additional optimization algorithms.  The optimization in this package is simulation-based, leveraging Python Classes that model Trailers, Shipments, and Pieces as well as the placement and movement of Pieces and Shipments within a Trailer.  For more information on adding your own optimization, see additional details in the `Simulation Model Description` section below.

## Install

## Usage

## Simulation Model Description

Given the complexity of the trailer loading optimization problem, we are well-advised to seek approximate optimization approach rather than exact optimization that may be very costly and time-consuming.  This package includes an object-oriented framework for simulation-based optimizers, which can be used as the underpinning for approaches like simulated annealing/MCMC style methods, genetic algorithms, and other heuristic/stochastic/dynamical systems optimization schemes.

The simulation framework is composed of 3 types of objects:  Trailers, Shipments, and Pieces.  

- *Piece* (`ytl.logistics_objects.Piece`):  Pieces are indivisible shipping units that are assumed to be rectangular prisms with length, width, and height dimensions, as well as weight, stackable, and rotation-allowed attributes.  
- *Shipment* (`ytl.logistics_objects.Shipment`):  Shipments are made up of Piece objects and store information about where pieces are stacked/arranged within its boundaries.  Shipments have calculated length, width, height, and weight attributes based on the contained pieces and their relative placement within the shipment.
- *Trailer* (`ytl.logistics_objects.Trailer`): Trailer are made up of Shipment objects and store information about where shipments are arraged within its boundaries.  Trailers have maximum length, width, height, and weight parameters that dictate how shipments can be arranged inside of them.  Shipment objects are not allowed to be stacked inside of a trailer - any stacking of shipping units must be treated as stackinng of Piece objects to make up a Shipment.

These definitions set up a natural two-stage optimization framework.  Based on user inputs, create a collection of Piece objects and a Trailer of the appropriate dimensions.  The first stage of the optimization is to arrange the Piece objects into Shipments, and the second is to arrange the Shipment objects in the Trailer object.  These two stages are implemented in `ytl/optimizer_functions/__init__.py`:

- *Piece Arrangement Optimation Router* (`ytl.optimizer_functions.optimize_pieces_arrangement`):  This function takes as input parameters a list of Piece objects and algorithm specification, and it returns a list of Shipment objects containing all provided pieces.  This optimization is built to be run to generate a list of Shipment objects from provided Piece objects (not built to be run iteratively).
- *Shipment Arrangement Optimation Router* (`ytl.optimizer_functions.optimize_shipment_arrangement`):  This function takes as parameters a Trailer object (assumed to have Shipment objects already defined) and algorithm `max_iter`/`timeout` parameters to control optimization runtime.  It returns `None`, but makes updates to the Trailer object in place that model rearrangement of shipments within the trailer.  These optimizers are intended to be run iteratively on a Trailer object in the process of a simulation-based optimization.  Loss function measurements are made based on the state of the Trailer object, which in our case we simply use the linear foot trailer occupancy as the loss function.

The optimization is implemented in `ytl.services.trailer_load.optimize_trailer_load_plan`, which manages the creation of Piece/Trailer objects from user inputs and both stages (Piece and Shipment arrangement) of the optimization. The options used for each stage of the optimization can be specified in the user request, otherwise the defaults set in `ytl.defaults` are used.

Further development can be done by adding additional optimizers to `ytl.optimizer_functions.optimize_pieces_arrangement` and/or `ytl.optimizer_functions.optimize_shipment_arrangement`, altering the goal of the optimization by using another loss function instead of linear feet, or altering the valid Piece arrangement methodology inside the Piece/Shipment objects.

For examples of how to generate and work with Piece, Shipment, and Trailer objects, start with `demo/demo_trailer_load.py` and `ytl.services.trailer_load.optimize_trailer_load_plan`.  

## Reference

Portions of this package make use of an optimization presented by Dube and Kanavalty in the conference papaer cited below.  There is a Python implementation of this algorithm available at `https://pypi.org/project/py3dbp/`, which is a derivative work of a Go implementation available in `https://github.com/bom-d-van/binpacking` (The article by Dube and Kanavalty is also available in this GitHub repository).  The `py3dbp` Python implementation, with minor variations to suite our purposes, is in the `ytl.py3dbp` module of this package and leveraged in portions of the trailer load optimization services.

```
E. Dube and L. Kanavalty, "Optimizing Three-Dimensional Bin Packing Through Simulation", Proceedings of the Sixth IASTED International Confernece Modelling, Simulation, and Optimization pp. 1-7, September 11-13, 2006, Gaborone, Botswana.
```
