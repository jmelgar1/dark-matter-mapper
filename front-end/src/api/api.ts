import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const predictDarkMatter = async (
    raMin: number,
    raMax: number,
    decMin: number,
    decMax: number
) => {
    try {
        const response = await axios.post(`${API_URL}/predict`, {
            ra_min: raMin,
            ra_max: raMax,
            dec_min: decMin,
            dec_max: decMax
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            throw new Error(`API Error: ${error.response?.data?.detail || error.message}`);
        }
        throw error;
    }
};