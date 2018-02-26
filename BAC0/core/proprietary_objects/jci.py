#!/usr/bin/env python

"""
This sample application shows how to extend one of the basic objects, an Analog
Value Object in this case, to provide a present value. This type of code is used
when the application is providing a BACnet interface to a collection of data.
It assumes that almost all of the default behaviour of a BACpypes application is
sufficient.
"""

from bacpypes.primitivedata import Boolean
from bacpypes.object import BinaryValueObject, Property, register_object_type

from ..devices.Points import BasicPoint
from ..utils.notes import note_and_log

#
#   Vendor TECSupOnline Value Object Type
#


@note_and_log
class TECSupOnline(BinaryValueObject):
    objectType = 'device'
    vendor_id = 5

    properties = [
        Property(3653, Boolean, mutable=True),
    ]

    def __init__(self, **kwargs):
        if _debug:
            TECSupOnline._debug("__init__ %r", kwargs)
        BinaryValueObject.__init__(self, **kwargs)
        self.prop = '3653'


def register(cls, vendor_id=5):
    register_object_type(cls, vendor_id=vendor_id)


class ProprietaryBV(BasicPoint):
    def __init__(self, cls, device, pointName, description=""):
        BasicPoint.__init__(device, pointType='binaryValue', pointAddress=None,
                            pointName=pointName, description=description,
                            presentValue=None, units_state=None)
        self.dev_addr = self.properties.device.address
        self.objectType = cls.objectType
        self.vendor_id = cls.vendor_id
        self.prop = cls.prop
        self.base_req = "{} {} {}".format(self.properties.device.address,
                                          self.objectType,
                                          self.prop)

    @property
    def value(self):
        req = self.base_req
        self.properties.device.read(req, vendor_id=self.vendor_id)

    def write(self, value):
        if value == True of value = 'active':
            val = 'true'
        else val = 'false'
        req = "{} {}".format(self.base_req, val)
        self.properties.device.write(req, vendor_id=self.vendor_id)
