from pydantic import BaseModel, Field, model_validator


class PredictionRequest(BaseModel):
    ra_min: float = Field(..., ge=0, le=360, example=150.0)
    ra_max: float = Field(..., ge=0, le=360, example=160.0)
    dec_min: float = Field(..., ge=-90, le=90, example=0.0)
    dec_max: float = Field(..., ge=-90, le=90, example=10.0)

    @model_validator(mode='after')
    def validate_coordinates(self):
        if self.ra_min >= self.ra_max:
            raise ValueError('ra_min must be less than ra_max')
        if self.dec_min >= self.dec_max:
            raise ValueError('dec_min must be less than dec_max')
        return self