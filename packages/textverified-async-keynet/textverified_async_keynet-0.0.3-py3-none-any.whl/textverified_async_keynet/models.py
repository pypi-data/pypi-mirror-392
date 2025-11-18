from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class RentalState(str, Enum):
    VERIFICATION_PENDING = "verificationPending"
    VERIFICATION_COMPLETED = "verificationCompleted"
    VERIFICATION_CANCELED = "verificationCanceled"
    VERIFICATION_TIMED_OUT = "verificationTimedOut"
    VERIFICATION_REPORTED = "verificationReported"
    VERIFICATION_REFUNDED = "verificationRefunded"
    VERIFICATION_REUSED = "verificationReused"
    VERIFICATION_REACTIVATED = "verificationReactivated"
    RENEWABLE_ACTIVE = "renewableActive"
    RENEWABLE_OVERDUE = "renewableOverdue"
    RENEWABLE_EXPIRED = "renewableExpired"
    RENEWABLE_REFUNDED = "renewableRefunded"
    NONRENEWABLE_ACTIVE = "nonrenewableActive"
    NONRENEWABLE_EXPIRED = "nonrenewableExpired"
    NONRENEWABLE_REFUNDED = "nonrenewableRefunded"


class LinkModel(BaseModel):
    method: Optional[str] = None
    href: Optional[str] = None


class RefundModel(BaseModel):
    canRefund: bool
    link: LinkModel
    refundableUntil: Optional[str] = None


# Модель для элемента в списке аренд (get_rentals)
class RentalListItem(BaseModel):
    createdAt: str
    id: str
    sale: LinkModel
    saleId: Optional[str] = None
    serviceName: str
    link: LinkModel
    state: RentalState
    billingCycle: Optional[LinkModel] = None
    billingCycleId: Optional[str] = None
    isIncludedForNextRenewal: Optional[bool] = None
    number: str
    alwaysOn: Optional[bool] = None


# Модель для детальной информации об аренде (get_rental_by_id)
class RentalDetail(BaseModel):
    createdAt: str
    id: str
    refund: RefundModel
    sale: LinkModel
    saleId: Optional[str] = None
    serviceName: str
    sms: LinkModel
    calls: LinkModel
    state: RentalState
    billingCycle: LinkModel
    billingCycleId: str
    isIncludedForNextRenewal: bool
    number: str
    alwaysOn: bool

class LinksCursor(BaseModel):
    current: LinkModel
    next: Optional[LinkModel] = None

class RentalsListResponse(BaseModel):
    data: List[RentalListItem]
    hasNext: bool
    links: LinksCursor

class NonRentalDetail(BaseModel):
    calls: LinkModel
    createdAt: str
    endsAt: str
    id: str
    refund: RefundModel
    sale: LinkModel
    saleId: Optional[str] = None
    serviceName: str
    sms: LinkModel
    state: RentalState
    number: str
    alwaysOn: bool

class NonRentalListItem(BaseModel):
    createdAt: str
    id: str
    link: LinkModel
    sale: LinkModel
    saleId: Optional[str] = None
    serviceName: str
    state: RentalState
    number: str
    alwaysOn: bool

class NonRentalListResponse(BaseModel):
    data: List[NonRentalListItem]
    hasNext: bool
    links: LinksCursor

class SmsListItem(BaseModel):
    id: str
    _from: str = None
    to: str
    createdAt: str
    smsContent: str = None
    parsedCode: str = None
    encrypted: bool

class SmsListResponse(BaseModel):
    data: List[SmsListItem]

class WakeRequestResponse(BaseModel):
    id: str
    usageWindowStart: str = None
    usageWindowEnd: str = None
    isScheduled: bool
    reservationId: str = None