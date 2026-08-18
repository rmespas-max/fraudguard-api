import logging
from typing import List, Optional
from src.domain.interfaces import FraudDetectionStrategy, TransactionRequest, TransactionResponse

logger = logging.getLogger(__name__)


class RuleBasedFraudDetector(FraudDetectionStrategy):
    @property
    def name(self) -> str:
        return "RuleBased"

    def analyze(self, transaction: TransactionRequest) -> TransactionResponse:
        reasons: List[str] = []
        scores: List[float] = [0.10]  # baseline risk score

        if transaction.amount > 5000.0:
            reasons.append("High value transaction")
            scores.append(0.70)

        if transaction.amount > 3000.0 and transaction.country == "BO":
            reasons.append("High-value cross-border pattern")
            scores.append(0.80)

        if transaction.merchant_category == "electronics" and transaction.amount > 1000.0:
            reasons.append("Unusual merchant category for account history")
            scores.append(0.50)

        max_score = max(scores)
        if max_score >= 0.8:
            decision = "BLOCK"
        elif max_score >= 0.5:
            decision = "REVIEW"
        else:
            decision = "ALLOW"
            if not reasons:
                reasons.append("No rules triggered")

        return TransactionResponse(
            transaction_id=transaction.transaction_id,
            decision=decision,
            risk_score=max_score,
            reasons=reasons,
            evaluator_engine=self.name
        )


class AIEnhancedFraudDetector(FraudDetectionStrategy):
    def __init__(self, fallback_detector: Optional[FraudDetectionStrategy] = None):
        self.fallback_detector = fallback_detector or RuleBasedFraudDetector()

    @property
    def name(self) -> str:
        return "AI_Enhanced"

    def analyze(self, transaction: TransactionRequest) -> TransactionResponse:
        try:
            # Simulated AI scoring logic
            # If the transaction_id starts with "fail_", we simulate a failure to trigger the fallback.
            if transaction.transaction_id.startswith("fail_"):
                raise RuntimeError("AI model service timeout")

            # Simple deterministic dummy score formula
            amount_factor = min(transaction.amount / 10000.0, 1.0)
            score = round(0.2 * amount_factor + 0.6 * (1.0 if transaction.country == "BO" else 0.0), 2)

            reasons = []
            if score > 0.8:
                decision = "BLOCK"
                reasons.append("AI predicted high probability of fraud")
            elif score > 0.5:
                decision = "REVIEW"
                reasons.append("AI flagged transaction for manual review")
            else:
                decision = "ALLOW"
                reasons.append("AI score within safe thresholds")

            return TransactionResponse(
                transaction_id=transaction.transaction_id,
                decision=decision,
                risk_score=score,
                reasons=reasons,
                evaluator_engine=self.name
            )
        except Exception as e:
            logger.warning(f"AI Engine failed: {str(e)}. Falling back to Rule-Based engine.")
            fallback_response = self.fallback_detector.analyze(transaction)
            fallback_response.reasons.append(f"AI Engine Fallback triggered: {str(e)}")
            return fallback_response
