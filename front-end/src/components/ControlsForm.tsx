import React, { useState } from 'react';
import { predictDarkMatter } from '../api/api';

export default function ControlsForm({ onPredict }: {
    onPredict: (data: any) => void
}) {
    const [raMin, setRaMin] = useState('150');
    const [raMax, setRaMax] = useState('160');
    const [decMin, setDecMin] = useState('0');
    const [decMax, setDecMax] = useState('10');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const data = await predictDarkMatter(
                parseFloat(raMin),
                parseFloat(raMax),
                parseFloat(decMin),
                parseFloat(decMax)
            );
            onPredict(data);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="controls-form">
            <h2>Dark Matter 3D Mapper</h2>
            <div className="input-group">
                <label>RA Min/Max (0-360)</label>
                <input type="number" value={raMin} onChange={(e) => setRaMin(e.target.value)} step="0.1" />
                <input type="number" value={raMax} onChange={(e) => setRaMax(e.target.value)} step="0.1" />
            </div>

            <div className="input-group">
                <label>Dec Min/Max (-90-90)</label>
                <input type="number" value={decMin} onChange={(e) => setDecMin(e.target.value)} step="0.1" />
                <input type="number" value={decMax} onChange={(e) => setDecMax(e.target.value)} step="0.1" />
            </div>

            <button type="submit" disabled={loading}>
                {loading ? 'Mapping Dark Matter...' : 'Start Mapping'}
            </button>
        </form>
    );
}