from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import List


class TransactionRequest(BaseModel):
    transaction_id: str
    account_id: str
    amount: float = Field(..., gt=0.0)
    currency: str
    country: str
    merchant_category: str
    device_id: str


class TransactionResponse(BaseModel):
    transaction_id: str
    decision: str  # e.g., "ALLOW", "REVIEW", "BLOCK"
    risk_score: float = Field(..., ge=0.0, le=1.0)
    reasons: List[str]
    evaluator_engine: str


class FraudDetectionStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the strategy/engine (e.g. 'RuleBased', 'AI_Enhanced')"""
        pass

    @abstractmethod
    def analyze(self, transaction: TransactionRequest) -> TransactionResponse:
        """Analyzes a transaction and returns the decision/risk score"""
        pass
