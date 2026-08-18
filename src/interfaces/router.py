from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.domain.interfaces import TransactionRequest, TransactionResponse
from src.core.use_cases import AnalyzeTransactionUseCase
from src.infrastructure.ia_engine import RuleBasedFraudDetector, AIEnhancedFraudDetector

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


def get_use_case(
    engine: str = Query("AI_Enhanced", description="Engine strategy: 'RuleBased' or 'AI_Enhanced'")
) -> AnalyzeTransactionUseCase:
    if engine == "RuleBased":
        strategy = RuleBasedFraudDetector()
    elif engine == "AI_Enhanced":
        strategy = AIEnhancedFraudDetector()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown evaluator engine: '{engine}'. Allowed values are 'RuleBased' or 'AI_Enhanced'."
        )
    return AnalyzeTransactionUseCase(strategy)


@router.post("/analyze", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
def analyze_transaction(
    transaction: TransactionRequest,
    use_case: AnalyzeTransactionUseCase = Depends(get_use_case)
):
    try:
        return use_case.execute(transaction)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during transaction analysis: {str(e)}"
        )
