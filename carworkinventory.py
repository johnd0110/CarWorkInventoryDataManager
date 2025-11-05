from web import web_display
from datetime import datetime
from dataclasses import dataclass

class Car:
    def __init__(self, make, model, year, engineType, mileage):
        self.make = make
        self.model = model
        self.year = year
        self.engineType = engineType
        self.mileage = mileage
        self.parts = []
        self.performedLabor = []

    def addPart(self, taxes, shippingCost, fullCost):
        part = CarPart(taxes, shippingCost, fullCost)
        self.parts.append(part)
        return part

    def addPart(self, part):
        self.parts.append(part)

    def addEmployee(self, name, payRate):
        employee = Employee(name, payRate)
        self.performedLabor.append(employee)
        return employee

    def addEmployee(self, employee):
        self.performedLabor.append(employee)

    def getTotalHoursWorked(self):
        pass

    def getTotalWages(self):
        pass

@dataclass
class CarPart:
    taxes: float
    shippingCost: float
    fullCost: float

@dataclass
class Employee:
    name: str
    payRate: float

@dataclass
class Labor:
    employee: Employee
    workDate: datetime
    #TODO: Consider changes to pay rate and prorating
    hoursWorked: float
    workDescription: str


if __name__ == '__main__':

    pass
