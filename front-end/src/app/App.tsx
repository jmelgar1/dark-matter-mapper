import { useState } from 'react';
import ControlsForm from '../components/ControlsForm';
import GalaxyPlot from '../components/GalaxyPlot';
import './App.css';

export default function App() {
  const [voxelData, setVoxelData] = useState<number[][][] | null>(null);

  return (
      <div className="app">
        <h1>Dark Matter 3D Mapper</h1>
          <ControlsForm onPredict={(data) => {
              console.log("API Response:", data);
              setVoxelData(data.prediction_3d);
          }} />
        <GalaxyPlot voxelData={voxelData} />
      </div>
  );
}