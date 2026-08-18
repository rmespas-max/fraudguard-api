from src.domain.interfaces import FraudDetectionStrategy, TransactionRequest, TransactionResponse


class AnalyzeTransactionUseCase:
    def __init__(self, strategy: FraudDetectionStrategy):
        self.strategy = strategy

    def execute(self, transaction: TransactionRequest) -> TransactionResponse:
        return self.strategy.analyze(transaction)
