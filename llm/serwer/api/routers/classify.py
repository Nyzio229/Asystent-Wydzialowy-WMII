from fastapi import APIRouter

from pydantic import BaseModel

from common import common

class ClassificationRequest(BaseModel):
    text: str
    labels: list[str]

class ClassificationResult(BaseModel):
    label: str

router = APIRouter()

# @TODO: może jednak zwykła llama jako classifier bo można by jej dać wskazówkę: co znaczy map, faq, other itp.

@router.post("/classify")
async def classify(
    request: ClassificationRequest
) -> ClassificationResult:
    result = common.classifier(request.text, request.labels)

    best_label = result["labels"][0]
    result = ClassificationResult(label=best_label)

    return result
