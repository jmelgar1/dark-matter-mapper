import { useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Points, PointMaterial } from '@react-three/drei';

export default function GalaxyPlot({ voxelData }: {
    voxelData: number[][][] | null
}) {
    const points = useMemo(() => {
        if (!voxelData) return null;

        if (!Array.isArray(voxelData) ||
            !Array.isArray(voxelData[0]) ||
            !Array.isArray(voxelData[0][0])) {
            console.error('Invalid voxel data structure');
            return null;
        }

        const positions: number[] = [];
        const colors: number[] = [];
        const size = voxelData.length;

        const allValues = voxelData.flat(2);
        const absMax = Math.max(...allValues.map(Math.abs));
        const minVal = Math.min(...allValues);
        const maxVal = Math.max(...allValues);

        console.log('Data Stats:', {
            min: minVal,
            max: maxVal,
            absMax: absMax,
            mean: allValues.reduce((a,b) => a + b, 0) / allValues.length
        });

        for (let x = 0; x < size; x++) {
            for (let y = 0; y < size; y++) {
                for (let z = 0; z < size; z++) {
                    const val = voxelData[x][y][z];
                    if (val > 0.7) {
                        positions.push(
                            (x - size/2) * 0.1,
                            (y - size/2) * 0.1,
                            (z - size/2) * 0.1
                        );

                        colors.push(
                            Math.pow(val, 2),
                            0.2,
                            1 - Math.pow(val, 2)
                        );
                    }
                }
            }
        }

        return {
            positions: new Float32Array(positions),
            colors: new Float32Array(colors)
        };
    }, [voxelData]);

    return (
        <div className="canvas-container">
            <Canvas camera={{ position: [0, 0, 100], fov: 50 }}>
                <ambientLight intensity={0.5} />
                <OrbitControls enableZoom={true} />

                {points && (
                    <Points positions={points.positions} colors={points.colors}>
                        <PointMaterial
                            vertexColors
                            size={0.15}
                            transparent
                            opacity={0.9}
                            sizeAttenuation={true}
                            alphaTest={0.1}
                        />
                    </Points>
                )}

                <axesHelper args={[50]} />
                <gridHelper args={[100, 50, '#202020', '#404040']} />
            </Canvas>
        </div>
    );
}