import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from torch.utils.data import DataLoader
import torch

from src.main.ml.train import SyntheticDataset
from src.main.sdss.sdss_client import fetch_sdss_galaxies, preprocess_to_3d_voxels
from src.main.ml.model import DarkMatter3DCNN
from src.main.objects.prediction_request import PredictionRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dark Matter Mapper API",
    description="API for predicting 3D dark matter distributions",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model and lock
model = DarkMatter3DCNN()
current_model_lock = asyncio.Lock()

# List to store epoch losses
epoch_losses = []

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up server and training model...")
    await train_model()
    logger.info("Model training completed")

async def train_model():
    """Async training function with synthetic data"""
    global model, epoch_losses
    temp_model = DarkMatter3DCNN()

    def load_data():
        dataset = SyntheticDataset(n_samples=1000)
        return DataLoader(dataset, batch_size=8, shuffle=True)

    loop = asyncio.get_event_loop()
    loader = await loop.run_in_executor(None, load_data)

    criterion = torch.nn.L1Loss()
    optimizer = torch.optim.Adam(temp_model.parameters(), lr=0.0001)

    for epoch in range(1):
        epoch_loss = 0.0
        for galaxies, targets in loader:
            def train_step():
                optimizer.zero_grad()
                outputs = temp_model(galaxies)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                return loss.item()

            loss_value = await loop.run_in_executor(None, train_step)
            epoch_loss += loss_value
            logger.info(f"Batch loss: {loss_value:.4f}")

        avg_loss = epoch_loss / len(loader)
        epoch_losses.append(avg_loss)  # Collect average loss per epoch
        logger.info(f"Epoch {epoch + 1}, Avg Loss: {avg_loss:.4f}")

    async with current_model_lock:
        model.load_state_dict(temp_model.state_dict())

@app.get("/training_progress")
async def get_training_progress():
    """Return the list of epoch losses for visualization"""
    return {"epoch_losses": epoch_losses}

@app.post("/predict")
async def predict_dark_matter(prediction_request: PredictionRequest):
    try:
        logger.info(f"Received prediction request: {prediction_request.dict()}")
        galaxies = fetch_sdss_galaxies(
            prediction_request.ra_min,
            prediction_request.ra_max,
            prediction_request.dec_min,
            prediction_request.dec_max
        )
        voxel_grid = preprocess_to_3d_voxels(galaxies)
        input_tensor = torch.tensor(voxel_grid).unsqueeze(0).unsqueeze(0).float()
        with torch.no_grad():
            prediction = model(input_tensor)
        if prediction.shape[-3:] != (50, 50, 50):
            raise HTTPException(500, f"Model output shape {prediction.shape} invalid")
        prediction_3d = prediction.squeeze().cpu().numpy().tolist()
        return {
            "status": "success",
            "prediction_3d": prediction_3d,
            "note": "Model pre-trained at startup"
        }
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(500, f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)