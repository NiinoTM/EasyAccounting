# models.py
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional
from enum import Enum, auto

class AccountBalance(Enum):
    """Enum for account balance types."""
    DEBIT = "debito"
    CREDIT = "credito"

class AssetStatus(Enum):
    """Enum for asset status."""
    ACTIVE = auto()
    INACTIVE = auto()
    FULLY_DEPRECIATED = auto()

@dataclass(frozen=True)
class AccountType:
    """Immutable account type representation."""
    id: Optional[int]
    name: str
    normal_balance: AccountBalance

    def __post_init__(self):
        if not isinstance(self.normal_balance, AccountBalance):
            object.__setattr__(
                self, 'normal_balance', 
                AccountBalance(self.normal_balance)
            )

@dataclass(frozen=True)
class Account:
    """Immutable account representation."""
    id: Optional[int]
    name: str
    type_id: int
    specific_type: Optional[str] = None
    specific_subtype: Optional[str] = None
    category_id: Optional[int] = None
    balance: Decimal = Decimal('0')

    def __post_init__(self):
        if isinstance(self.balance, (int, float)):
            object.__setattr__(self, 'balance', Decimal(str(self.balance)))

@dataclass(frozen=True)
class Transaction:
    """Immutable transaction representation."""
    id: Optional[int]
    date: date
    description: str
    debit_account: int
    credit_account: int
    amount: Decimal

    def __post_init__(self):
        if isinstance(self.amount, (int, float)):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))