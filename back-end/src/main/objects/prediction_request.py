from pydantic import BaseModel, Field
from pydantic.v1 import validator


class PredictionRequest(BaseModel):
    ra_min: float = Field(..., ge=0, le=360, example=150.0)
    ra_max: float = Field(..., ge=0, le=360, example=160.0)
    dec_min: float = Field(..., ge=-90, le=90, example=0.0)
    dec_max: float = Field(..., ge=-90, le=90, example=10.0)

    @validator('ra_min')
    def validate_ra_min(self, v, values):
        if 'ra_max' in values and v >= values['ra_max']:
            raise ValueError('ra_min must be less than ra_max')
        return v