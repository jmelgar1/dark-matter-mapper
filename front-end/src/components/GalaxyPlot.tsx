import { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Points, PointMaterial } from '@react-three/drei';

export default function GalaxyPlot({ voxelData }: {
    voxelData: number[][][] | null
}) {
    const points = useMemo(() => {
        if (!voxelData) return null;

        const positions: number[] = [];
        const size = 50;

        // Convert 3D array to point cloud
        for (let x = 0; x < size; x++) {
            for (let y = 0; y < size; y++) {
                for (let z = 0; z < size; z++) {
                    if (voxelData[x][y][z] > 0.1) {
                        positions.push(
                            (x - size/2) * 0.1,
                            (y - size/2) * 0.1,
                            (z - size/2) * 0.1
                        );
                    }
                }
            }
        }

        return new Float32Array(positions);
    }, [voxelData]);

    return (
        <div className="canvas-container">
            <Canvas camera={{ position: [0, 0, 50], fov: 50 }}>
                <ambientLight intensity={0.5} />
                <OrbitControls enableZoom={true} />

                {points && (
                    <Points positions={points}>
                        <PointMaterial
                            color="#5786F5"
                            size={0.05}
                            transparent
                            sizeAttenuation={true}
                        />
                    </Points>
                )}

                <gridHelper args={[100, 100, '#181818', '#383838']} />
            </Canvas>
        </div>
    );
}