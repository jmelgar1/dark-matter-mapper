import asyncio

import torch
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from torch.utils.data import DataLoader

from src.main.ml.train import SyntheticDataset
from src.main.sdss.sdss_client import fetch_sdss_galaxies, preprocess_to_3d_voxels
from src.main.ml.model import DarkMatter3DCNN
from src.main.objects.prediction_request import PredictionRequest

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

# Initialize model without weights
model = DarkMatter3DCNN()
current_model_lock = asyncio.Lock()

async def train_model():
    """Async training function with synthetic data"""
    global model
    temp_model = DarkMatter3DCNN()

    # Move data loading to synchronous executor
    def load_data():
        dataset = SyntheticDataset(n_samples=1000)
        return DataLoader(dataset, batch_size=8, shuffle=True)

    # Use async executor for CPU-bound operations
    loop = asyncio.get_event_loop()
    loader = await loop.run_in_executor(None, load_data)

    criterion = torch.nn.L1Loss()
    optimizer = torch.optim.Adam(temp_model.parameters(), lr=0.0001)

    # Training loop with proper async yield
    for epoch in range(50):
        epoch_loss = 0.0
        for galaxies, targets in loader:
            # Wrap tensor operations in async task
            def train_step():
                optimizer.zero_grad()
                outputs = temp_model(galaxies)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                return loss.item()

            # Yield control to event loop periodically
            loss_value = await loop.run_in_executor(None, train_step)
            epoch_loss += loss_value

            # Explicitly flush print buffer
            print(f"Batch loss: {loss_value:.4f}", flush=True)

        # Print epoch statistics
        avg_loss = epoch_loss / len(loader)
        print(f"\nEpoch {epoch + 1}, Avg Loss: {avg_loss:.4f}\n", flush=True)

    # Model update remains the same
    async with current_model_lock:
        model.load_state_dict(temp_model.state_dict())


@app.post("/predict")
async def predict_dark_matter(
        prediction_request: PredictionRequest,
        background_tasks: BackgroundTasks
):
    try:
        # trigger async training before prediction
        background_tasks.add_task(train_model)

        # continue with prediction using last trained model
        async with current_model_lock:
            if not (-90 <= prediction_request.dec_min <= 90) or not (-90 <= prediction_request.dec_max <= 90):
                raise HTTPException(400, "Dec must be between -90 and 90")

            # fetch and process real data
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

                # first check prediction shape
                if prediction.shape[-3:] != (50, 50, 50):
                    raise HTTPException(500, f"Model output shape {prediction.shape} invalid")

                prediction_3d = prediction.squeeze().cpu().numpy()
                prediction_list = prediction_3d.tolist()

                if not isinstance(prediction_list, list) or \
                        not isinstance(prediction_list[0][0][0], (float, int)):
                    raise HTTPException(500, "Invalid prediction format")

                print(f"Prediction shape: {prediction_3d.shape}")
                print(f"List structure: {len(prediction_list)}x{len(prediction_list[0])}x{len(prediction_list[0][0])}")

                return {
                    "status": "success",
                    "prediction_3d": prediction_list,
                    "training_note": "New model training initiated in background",
                }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, f"Prediction failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)