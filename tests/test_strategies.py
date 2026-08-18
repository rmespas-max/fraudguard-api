import pytest
from pydantic import ValidationError
from src.domain.interfaces import TransactionRequest
from src.infrastructure.ia_engine import RuleBasedFraudDetector, AIEnhancedFraudDetector


def test_transaction_request_zero_amount():
    with pytest.raises(ValidationError):
        TransactionRequest(
            transaction_id="tx_1",
            account_id="acc_1",
            amount=0.0,  # Invalid: must be gt=0.0
            currency="USD",
            country="US",
            merchant_category="retail",
            device_id="dev_1"
        )


def test_transaction_request_negative_amount():
    with pytest.raises(ValidationError):
        TransactionRequest(
            transaction_id="tx_1",
            account_id="acc_1",
            amount=-50.0,  # Invalid: must be gt=0.0
            currency="USD",
            country="US",
            merchant_category="retail",
            device_id="dev_1"
        )


def test_rule_based_detector_normal():
    detector = RuleBasedFraudDetector()
    tx = TransactionRequest(
        transaction_id="tx_1",
        account_id="acc_1",
        amount=100.0,
        currency="USD",
        country="US",
        merchant_category="retail",
        device_id="dev_1"
    )
    res = detector.analyze(tx)
    assert res.decision == "ALLOW"
    assert res.risk_score == 0.10
    assert "No rules triggered" in res.reasons
    assert res.evaluator_engine == "RuleBased"


def test_rule_based_detector_high_value():
    detector = RuleBasedFraudDetector()
    tx = TransactionRequest(
        transaction_id="tx_1",
        account_id="acc_1",
        amount=6000.0,  # triggers high value (> 5000)
        currency="USD",
        country="US",
        merchant_category="retail",
        device_id="dev_1"
    )
    res = detector.analyze(tx)
    assert res.decision == "REVIEW"
    assert res.risk_score == 0.70
    assert "High value transaction" in res.reasons


def test_rule_based_detector_cross_border():
    detector = RuleBasedFraudDetector()
    tx = TransactionRequest(
        transaction_id="tx_1",
        account_id="acc_1",
        amount=4000.0,  # triggers cross-border (> 3000, country BO)
        currency="USD",
        country="BO",
        merchant_category="retail",
        device_id="dev_1"
    )
    res = detector.analyze(tx)
    assert res.decision == "BLOCK"
    assert res.risk_score == 0.80
    assert "High-value cross-border pattern" in res.reasons


def test_ai_enhanced_detector_normal():
    detector = AIEnhancedFraudDetector()
    tx = TransactionRequest(
        transaction_id="tx_1",
        account_id="acc_1",
        amount=1000.0,
        currency="USD",
        country="US",
        merchant_category="retail",
        device_id="dev_1"
    )
    res = detector.analyze(tx)
    assert res.decision == "ALLOW"
    assert res.evaluator_engine == "AI_Enhanced"


def test_ai_enhanced_detector_fallback():
    detector = AIEnhancedFraudDetector()
    # Transaction ID starting with 'fail_' triggers simulated timeout runtime error
    tx = TransactionRequest(
        transaction_id="fail_timeout_tx",
        account_id="acc_1",
        amount=4000.0,
        currency="USD",
        country="BO",
        merchant_category="retail",
        device_id="dev_1"
    )
    res = detector.analyze(tx)
    # Falls back to RuleBased, which should BLOCK it (amount 4000, BO country)
    assert res.decision == "BLOCK"
    assert res.evaluator_engine == "RuleBased"
    assert any("AI Engine Fallback triggered" in reason for reason in res.reasons)


def test_rule_based_detector_electronics():
    detector = RuleBasedFraudDetector()
    tx = TransactionRequest(
        transaction_id="tx_electronics",
        account_id="acc_1",
        amount=1500.0,  # triggers electronics check (> 1000, electronics)
        currency="USD",
        country="US",
        merchant_category="electronics",
        device_id="dev_1"
    )
    res = detector.analyze(tx)
    assert res.decision == "REVIEW"
    assert res.risk_score == 0.50
    assert "Unusual merchant category for account history" in res.reasons


def test_ai_enhanced_detector_high_risk():
    detector = AIEnhancedFraudDetector()
    tx = TransactionRequest(
        transaction_id="tx_high_risk_ai",
        account_id="acc_1",
        amount=10000.0,  # triggers max amount factor -> score 0.8
        currency="USD",
        country="BO",    # triggers BO country factor (+0.6)
        merchant_category="retail",
        device_id="dev_1"
    )
    res = detector.analyze(tx)
    assert res.decision == "BLOCK"
    assert res.risk_score >= 0.8
    assert "AI predicted high probability of fraud" in res.reasons

