import { useState } from 'react';
import ControlsForm from '../components/ControlsForm';
import GalaxyPlot from '../components/GalaxyPlot';
import './App.css';

export default function App() {
    const [voxelData, setVoxelData] = useState<number[][][] | null>(null);

    return (
        <div className="app">
            <GalaxyPlot voxelData={voxelData} />
            <ControlsForm onPredict={(data) => {
                console.log("API Response:", data);
                setVoxelData(data.prediction_3d);
            }} />
        </div>
    );
}