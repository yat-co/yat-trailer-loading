
from .piece import Piece
from .shipment import Shipment
from .trailer import Trailer

'''
OOP inheritance structure

LogisticsObject
	ShippingObject(LogisticsObject)
		Piece(ShippingObject) - Non-divisible items
		Shipment(ShippingObject) - Collections/stacks of Piece objects, treated as single items to be arranged in Trailer
	Trailer(LogisticsObject)
'''


