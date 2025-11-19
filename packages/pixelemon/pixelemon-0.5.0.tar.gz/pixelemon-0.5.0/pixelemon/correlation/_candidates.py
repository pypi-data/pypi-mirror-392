from pydantic import BaseModel, Field, RootModel


class CorrelationCandidate(BaseModel):
    id: str = Field(..., description="Unique identifier for the candidate")
    x_centroid: float = Field(..., description="X coordinate of the streak centroid in pixels")
    y_centroid: float = Field(..., description="Y coordinate of the streak centroid in pixels")
    range: float = Field(..., description="Estimated range to the object in kilometers")


class CorrelationCandidates(RootModel[list[CorrelationCandidate]]):

    def __len__(self) -> int:
        return len(self.root)

    def __getitem__(self, index: int) -> CorrelationCandidate:
        return self.root[index]

    def __iter__(self):
        return iter(self.root)
