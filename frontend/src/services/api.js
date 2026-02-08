const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Upload a file to the appropriate backend endpoint based on its type.
 * @param {File} file - The file object to upload.
 * @param {string} type - The category of the file (video, audio, pdf, image).
 * @returns {Promise<Object>} - The JSON response from the backend.
 */
export const uploadFile = async (file, type) => {
    const formData = new FormData();
    formData.append('file', file);

    let endpoint = '';
    switch (type) {
        case 'pdf':
            endpoint = '/upload/pdf';
            break;
        case 'image':
            endpoint = '/upload/image';
            break;
        case 'audio':
            endpoint = '/upload/audio';
            break;
        case 'video':
            endpoint = '/upload/video';
            break;
        default:
            throw new Error(`Unsupported file type: ${type}`);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Upload failed: ${response.status} ${response.statusText} - ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Upload Error:', error);
        throw error;
    }
};

export const healthCheck = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        return await response.json();
    } catch (error) {
        console.error('Health check failed:', error);
        throw error;
    }
};

export const getKnowledgeBase = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/knowledge`);
        if (!response.ok) throw new Error('Failed to fetch knowledge base');
        return await response.json();
    } catch (error) {
        console.error('Get Knowledge Base Error:', error);
        throw error;
    }
};

export const preprocessData = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/preprocess`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Preprocessing failed');
        return await response.json();
    } catch (error) {
        console.error('Preprocessing Error:', error);
        throw error;
    }
}

export const getSummary = async (topic) => {
    try {
        const response = await fetch(`${API_BASE_URL}/summarize?topic=${encodeURIComponent(topic)}`, {
            headers: { 'ngrok-skip-browser-warning': 'true' }
        });
        if (!response.ok) throw new Error('Failed to fetch summary');
        return await response.json();
    } catch (error) {
        console.error('Summarize API Error:', error);
        throw error;
    }
};

export const getResearch = async (topic) => {
    try {
        const response = await fetch(`${API_BASE_URL}/research?topic=${encodeURIComponent(topic)}`, {
            headers: { 'ngrok-skip-browser-warning': 'true' }
        });
        if (!response.ok) throw new Error('Failed to fetch research');
        return await response.json();
    } catch (error) {
        console.error('Research API Error:', error);
        throw error;
    }
};

