import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from data.sdss_client import fetch_sdss_galaxies, preprocess_to_3d_voxels
from ml.model import DarkMatter3DCNN

app = FastAPI(
    title="Dark Matter Mapper API",
    description="API for predicting 3D dark matter distributions",
    version="0.1.0",
)

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model = DarkMatter3DCNN()
    # set placeholder weights until training is implemented
    model.load_state_dict(torch.load("ml/placeholder_weights.pth", map_location=torch.device('cpu')))
except Exception as e:
    raise RuntimeError(f"Model initialization failed: {str(e)}")


@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Dark Matter Mapper API is running"}


@app.post("/predict")
async def predict_dark_matter(ra_min: float, ra_max: float, dec_min: float, dec_max: float):
    try:
        # fetch galaxies - add validation
        if not (-90 <= dec_min <= 90) or not (-90 <= dec_max <= 90):
            raise HTTPException(status_code=400, detail="Dec must be between -90 and 90")

        galaxies = fetch_sdss_galaxies(ra_min, ra_max, dec_min, dec_max)

        # Add channel dimension and normalize
        voxel_grid = preprocess_to_3d_voxels(galaxies)
        input_tensor = torch.tensor(voxel_grid).unsqueeze(0).unsqueeze(0).float()  # Shape: [batch, channel, depth, height, width]

        # Add model validation
        if input_tensor.shape[-3:] != (50, 50, 50):
            raise HTTPException(status_code=422, detail="Invalid voxel grid dimensions")

        with torch.no_grad():
            prediction = model(input_tensor).numpy()

        return {
            "status": "success",
            "prediction_shape": prediction.shape,
            "prediction_sample": prediction[0, 0, 0, 0, 0]  # Return sample value
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")