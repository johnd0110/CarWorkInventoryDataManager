from dataclasses import dataclass, field
from datetime import datetime

from common_helper import lowerCaseKeyDict

@dataclass
class valueEstimate:
    estimatedValue: float = 0.0

    def serialize(self) -> lowerCaseKeyDict:
        return lowerCaseKeyDict({
            'estimatedvalue': self.estimatedValue
        })

@dataclass
class purchase:
    cost: float = 0.0
    taxesPaid: float = 0.0
    shippingCost: float = 0.0
    refundAmount: float = 0.0

    def serialize(self) -> lowerCaseKeyDict:
        return lowerCaseKeyDict({
            'cost': self.cost,
            'taxespaid': self.taxesPaid,
            'shippingcost': self.shippingCost,
            'refundamount': self.refundAmount
        })

@dataclass
class item:
    purchaseData: purchase = field(default_factory=purchase)
    valueEstimateData: valueEstimate = field(default_factory=valueEstimate)
    itemName: str = ''
    source: str = ''
    additionalNotes: str = ''

    def serialize(self) -> lowerCaseKeyDict:
        return lowerCaseKeyDict({
               'source': self.source,
               'itemname': self.itemName,
               'additionalnotes': self.additionalNotes}) | self.purchaseData.serialize() | self.valueEstimateData.serialize()

    def IsComplete(self) -> bool:
        return bool(self.itemName)

@dataclass
class itemGroupTransaction:
    items: list[item] = field(default_factory=list)
    description: str = ''

    def serialize(self) -> lowerCaseKeyDict:
        return lowerCaseKeyDict({
            'itemgroupdescription': self.description
        })

@dataclass
class workEffort:
    workEffortDate: datetime = field(default_factory=datetime)
    laborHours: float = 0.0
    estimatedPay: float = 0.0
    workType: str = ''

    def serialize(self) -> lowerCaseKeyDict:
        return lowerCaseKeyDict({
            'workeffortdate' : self.workEffortDate.strftime('%Y-%m-%d'),
            'laborhours': self.laborHours,
            'estimatedpay': self.estimatedPay,
            'worktype': self.workType
        })

@dataclass
class car:
    year: int
    purchaseData: purchase = field(default_factory=purchase)
    valueEstimateData: valueEstimate = field(default_factory=valueEstimate)
    workEfforts: dict[str, list[workEffort]] = field(default_factory=dict)
    make: str = ""
    model: str = ""
    engine: str = ""
    mileage: int = 0
    additionalNotes: str = ''

    def serialize(self) -> lowerCaseKeyDict:
        return lowerCaseKeyDict({
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'enginetype': self.engine,
            'mileage': self.mileage,
            'additionalnotes': self.additionalNotes,
        }) | self.purchaseData.serialize() | self.valueEstimateData.serialize()

def getFloatFromDollarAmountOrFree(strToProcess: str) -> float:
    try:
        return float(strToProcess.replace(',', '').replace('$', ''))
    except ValueError:
        if strToProcess.lower().strip() in ['free', '']:
            return 0.0
        else:
            raise NotImplementedError()
