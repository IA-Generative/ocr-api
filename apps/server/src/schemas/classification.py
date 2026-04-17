from pydantic import BaseModel, Field


class LabelDefinition(BaseModel):
    label: str = Field(..., description="Label name")
    definition: str = Field(..., description="Definition or description of the label")


class Model(BaseModel):
    name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version of the model")
    device: str = Field(default="cpu", description="Device used for the model (e.g., 'cpu', 'cuda')")


class ClassificationResult(BaseModel):
    label: LabelDefinition = Field(..., description="Label of the classification result")
    confidence: float = Field(..., description="Confidence score of the classification result")

    model: Model = Field(..., description="Model used for classification")


class PredictionOutput(BaseModel):
    label: str = Field(..., description="Predicted label for the page")
    confidence: float = Field(..., description="Confidence score of the prediction")


class PredictionsOutput(BaseModel):
    page_number: int = Field(..., description="Page number of the classified page")
    predictions: list[PredictionOutput] = Field(
        default_factory=list, description="List of classification results for the page"
    )


class BatchPredictionsOutput(BaseModel):
    predictions: list[PredictionsOutput] = Field(
        default_factory=list, description="List of classification results for all pages"
    )


class ParameterClassification(BaseModel):
    labels: list[LabelDefinition] = Field(
        default_factory=list, description="List of label definitions for classification"
    )
