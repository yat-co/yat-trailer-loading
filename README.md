# YTL - YAT Trailer Loading Package

Simple package for turning list of freight pieces into a trailer plan and associated metrics helpful for LTL (Less than Truckload) and Partial planning and pricing.  The package includes an out-of-the-box trailer load optimization allowing for flexible trailer dimension options, allows or disallows stacking/rotating of pieces, and handling of overweight shipments/pieces.  A detailed load plan is returned, as wells as several measurements like linear feet, actual volume, cubed volume, and effective trailer volume occupancy of the load plan.

The aim of the optimization is to load the provided shipments/pieces into a trailer of the specified dimensions with minimal linear foot occupancy of the trailer.  The default configuration makes it easy to plug and play to use in your own Python development or in an internally hosted API (see accompanying `yat-trailer-loading-api` for a simple Python Flask implementation).

Beyond the standard out-of-the-box style implementation, the package is readily available for development of additional optimization algorithms.  The optimization in this package is simulation-based, leveraging Python Classes that model Trailers, Shipments, and Pieces as well as the placement and movement of Pieces and Shipments within a Trailer.  For more information on adding your own optimization, see additional details in the `Simulation Model Description` section below.

## Install

```
pip install ytl
```

## Usage

### **Setup**
Import trailer optimization service (this version is intended to support an API)
```
from ytl import optimize_trailer_load_plan_wrapper
```

Specify shipment piece list (dimensions assumed to be in inches, weight in pounds).  Packing type must be `PALLET` or `BOX` (pallets are not allowed to be stacked on boxes, even if the pieces involved allow stacking).
```
shipment_list = [
    {
        "length": 40,
        "width": 42,
        "height": 35,
        "weight": 225,
        "packing": "PALLET",
        "stack_limit": 2,
        "num_pieces": 5
    },
    {
        "length": 44,
        "width": 40,
        "height": 30,
        "weight": 200,
        "packing": "BOX",
        "stack_limit": 3,
        "num_pieces": 8
    }
]
```

### **Trailer Load Optimization with Pre-Defined Trailer Type**
Define request data and call optimization function.  This example sets the equipment type to a typical 53' dry-van trailer and allow shipment pieces to be rotated.
```
request_data = {
    'equipment_code' : 'DV_53',
    'shipment_list' : shipment_list,
    'allow_rotations' : True
}
status_code,response_data = optimize_trailer_load_plan_wrapper(request_data=request_data)
```
The `status_code` is intended to be the status associated to an API call and the `response_data` is the response body.  You can interogate the response data for a large amount detail about the resulting optimization.  Below are a few examples showing the linear feet occupied in the trailer and a detailed list of the load plan.
```
print('status: {}'.format(status_code))
print('linear feet: {:.1f} ({:.0f}% of Trailer)'.format(response_data.get('linear_feet'),100*response_data.get('linear_feet_portion_of_trailer')))

print('Load Plan')
print('-'*100)
print('-'*100)
print('{:34}{:19}{:21}{:11}{:20}{}'.format('Desc','Location','Size','Weight','Orientation','Packing'))
print('-'*100)
for k,v in response_data['load_order'].items():
    print(
        '{name:30}  {x:3.0f} x {y:3.0f} x {z:3.0f}   {l:3.0f}" x {w:3.0f}" x {h:3.0f}"  {weight:5,.0f} Lbs    {rotated:15}     {packing:12}'.format(
            name=v.get('name'),
            x=v.get('position')[0],
            y=v.get('position')[1],
            z=v.get('position')[2],
            l=v.get('piece_length'),
            w=v.get('piece_width'),
            h=v.get('piece_height'),
            weight=v.get('piece_weight'),
            rotated='Rotated' if v.get('piece_is_rotated') else 'Not Rotated',
            packing=v.get('piece_packing')
        )
    )
```
The options for predefined equipment types are available in `ytl.STANDARD_TRAILER_DIMS`.  The `code` values are to be used in the optimization function.  The inner length, inner width, inner hieght, and max weight attributes are availalbe there for additional information.  The `inner_height` field for open top trailers is set to be the estimated maximum freight height for typical bridge clearances.
```
from ytl import STANDARD_TRAILER_DIMS
import json
print(json.dumps(STANDARD_TRAILER_DIMS,indent=2))
```

### **Trailer Load Optimization with Specified Trailer Dimensions**
```
trailer_dims = {
    "inner_width": 98.5,
    "inner_length": 630,
    "inner_height": 108,
    "max_weight": 42500
}
request_data = {
    'trailer_dims' : trailer_dims,
    'shipment_list' : shipment_list,
    'allow_rotations' : False
}
status_code,response_data = optimize_trailer_load_plan_wrapper(request_data=request_data)
```

### **Trailer Load Optimization with Altered Optimization Parameters**
You can alter the optimization as well by specifying router keys for the piece and shipment arrangement algorithms.  
```
request_data = {
    'equipment_code' : 'DV_53',
    'shipment_list' : shipment_list,
    'allow_rotations' : True,
    'piece_arrangement_algorithm' : 'NAIVE',
    'shipment_optimization_ls' : [
        {
            'algorithm' : 'GREEDY_LOAD',
            'max_iter' : 5,
            'timeout' : 2.5,
        }
    ]
}
status_code,response_data = optimize_trailer_load_plan_wrapper(request_data=request_data)
```
The piece arrangement algorith is a single use optimization that arranges (potentially stacking) pieces into shipments.  The shipment arrangement algorithm is iterative optimization that attempts to find the best way (*best meaning minimal linear feet occupied) of loading those shipments into the trailer.  Since the shipment arrangement is an iterated optimization, you can provide a list of algorithm parameters to use.  See `ytl.optimizer_functions.PIECE_ARRANGEMENT_ROUTER.keys()` for `piece_arrangement_algorithm` options and `ytl.optimizer_functions.SHIPMENT_ARRANGEMENT_ROUTER.keys()` for `algorithm` options in the `shipment_optimization_ls` parameter.  Also see `ytl.defaults.DEFAULT_PIECE_ARRANGEMENT_ALGORITHM` and `ytl.defaults.DEFAULT_SHIPMENT_ARRANGEMENT_ALGORITHM` for default values.
```
import ytl
import json

# Piece arrangement algorithm options
print(ytl.optimizer_functions.PIECE_ARRANGEMENT_ROUTER.keys())
# Piece arrangement algorithm default
print(ytl.defaults.DEFAULT_PIECE_ARRANGEMENT_ALGORITHM)

# Shipment arrangement algorithm options
print(ytl.optimizer_functions.SHIPMENT_ARRANGEMENT_ROUTER.keys())
# Shipment arrangement algorithm default
print(json.dumps(ytl.defaults.DEFAULT_SHIPMENT_ARRANGEMENT_ALGORITHM,indent=2))
```

## Simulation Model Description

Given the complexity of the trailer loading optimization problem, we are well-advised to seek approximate optimization approach rather than exact optimization that may be very costly and time-consuming.  This package includes an object-oriented framework for simulation-based optimizers, which can be used as the underpinning for approaches like simulated annealing/MCMC style methods, genetic algorithms, and other heuristic/stochastic/dynamical systems optimization schemes.

The simulation framework is composed of 3 types of objects:  Trailers, Shipments, and Pieces.  

- **Piece** (`ytl.logistics_objects.Piece`):  Pieces are indivisible objects intended to be loaded into a trailer.  They are assumed to be rectangular prisms with length, width, and height dimensions, as well as weight, stackable, and rotation-allowed attributes.  Only rotations in the x-y plane are allowed (pieces may be turned but not allowed to be tipped on their side or set upside down).

- **Shipment** (`ytl.logistics_objects.Shipment`):  Shipments are made up of Piece objects and store information about the relative location of Pieces arranged within its boundaries.  Shipments have calculated length, width, height, and weight attributes based on the contained pieces and their relative placement within the Shipment.  

- **Trailer** (`ytl.logistics_objects.Trailer`): Trailer objects are made up of Shipment objects and store information about where the relative location of Shipments arraged within its boundaries.  Trailers have inner length, inner width, inner height, and maximum weight parameters that dictate how Shipment objects can be arranged inside of them.  Shipment objects are not allowed to be stacked inside of a trailer - any stacking of shipping units must be treated as stackinng of Piece objects to make up a Shipment.

These definitions set up a natural two-stage optimization framework.  Based on user inputs, create a collection of Piece objects and a Trailer of the appropriate dimensions.  The first stage of the optimization is to arrange the Piece objects into Shipments, and the second is to arrange the Shipment objects in the Trailer object.  These two stages are implemented in `ytl/optimizer_functions/__init__.py`:

- **Piece Arrangement Optimation Router** (`ytl.optimizer_functions.optimize_pieces_arrangement`):  This function takes as input parameters a list of Piece objects and algorithm specification, and it returns a list of Shipment objects containing all provided pieces.  This optimization is built to be run to generate a list of Shipment objects from provided Piece objects (not built to be run iteratively).

- **Shipment Arrangement Optimation Router** (`ytl.optimizer_functions.optimize_shipment_arrangement`):  This function takes as parameters a Trailer object (assumed to have Shipment objects already defined) and algorithm `max_iter`/`timeout` parameters to control optimization runtime.  It returns `None`, but makes updates to the Trailer object in place that model rearrangement of shipments within the trailer.  These optimizers are intended to be run iteratively on a Trailer object in the process of a simulation-based optimization.  Loss function measurements are made based on the state of the Trailer object, which in our case we simply use the linear foot trailer occupancy as the loss function.

The optimization is implemented in `ytl.services.trailer_load.optimize_trailer_load_plan`, which manages the creation of Piece/Trailer objects from user inputs and both stages (Piece and Shipment arrangement) of the optimization. The options used for each stage of the optimization can be specified in the user request, otherwise the defaults set in `ytl.defaults` are used.

Further development can be done by adding additional optimizers to `ytl.optimizer_functions.optimize_pieces_arrangement` and/or `ytl.optimizer_functions.optimize_shipment_arrangement`, altering the goal of the optimization by using another loss function instead of linear feet, or altering the valid Piece arrangement methodology inside the Piece/Shipment objects.

For examples of how to generate and work with Piece, Shipment, and Trailer objects, start with `demo/demo_trailer_load.py` and `ytl.services.trailer_load.optimize_trailer_load_plan`.  

## Reference

Portions of this package make use of an optimization presented by Dube and Kanavalty in the conference papaer cited below.  There is a Python implementation of this algorithm available at `https://pypi.org/project/py3dbp/`, which is a derivative work of a Go implementation available in `https://github.com/bom-d-van/binpacking` (The article by Dube and Kanavalty is also available in this GitHub repository).  The `py3dbp` Python implementation, with minor variations to suite our purposes, is in the `ytl.py3dbp` module of this package and leveraged in portions of the trailer load optimization services.

```
E. Dube and L. Kanavalty, "Optimizing Three-Dimensional Bin Packing Through Simulation", Proceedings of the Sixth IASTED International Confernece Modelling, Simulation, and Optimization pp. 1-7, September 11-13, 2006, Gaborone, Botswana.
```
