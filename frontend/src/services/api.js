const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new APIError(
      error.detail || 'Une erreur est survenue',
      response.status
    );
  }
  return response.json();
};

export const api = {
  // Upload des fichiers et démarrage de l'analyse
  async startAnalysis(files, config) {
    const formData = new FormData();
    
    // Ajout des fichiers
    files.forEach(file => {
      formData.append('files', file);
    });

    // Conversion de la configuration
    const apiConfig = {
      processing_mode: config.mode === 'standard' ? 'hybrid' :
                      config.mode === 'approfondi' ? 'full_ai' : 'raw',
      ai_settings: {
        enable_summarization: config.mode === 'approfondi',
        enable_query_enhancement: config.mode === 'approfondi',
        enable_semantic_search: config.mode !== 'rapide',
        temperature: 0.7,
        max_tokens: 512
      },
      chunk_size: config.chunkSize,
      overlap: config.overlap
    };

    // Ajout de la configuration
    formData.append('mode', apiConfig.processing_mode);
    formData.append('config', JSON.stringify(apiConfig));

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    return handleResponse(response);
  },

  // Récupération de la progression
  async getProgress(taskId) {
    const response = await fetch(`${API_BASE_URL}/status/${taskId}`);
    const data = await handleResponse(response);
    
    // Conversion du format de progression
    return {
      status: data.status,
      progress: {
        preprocessing: Math.round(data.progress * 25),
        embedding: data.progress >= 0.25 ? Math.round((data.progress - 0.25) * 33.33) : 0,
        indexing: data.progress >= 0.5 ? Math.round((data.progress - 0.5) * 33.33) : 0,
        validation: data.progress >= 0.75 ? Math.round((data.progress - 0.75) * 100) : 0
      },
      currentFile: data.current_file,
      error: data.message
    };
  },

  // Récupération des résultats
  async getResults(taskId) {
    const response = await fetch(`${API_BASE_URL}/results/${taskId}`);
    const data = await handleResponse(response);
    
    // Conversion du format des résultats
    return {
      summary: {
        documentCount: data.documents.length,
        totalPages: data.documents.reduce((acc, doc) => acc + (doc.pages || 1), 0),
        processingTime: data.processing_time || "N/A",
        quality: data.quality || "95%"
      },
      documents: data.documents.map(doc => ({
        name: doc.filename,
        pages: doc.pages || 1,
        chunks: doc.chunks?.length || 0,
        quality: doc.quality || "90%",
        warnings: doc.warnings || []
      }))
    };
  },

  // Récupération de la configuration
  async getConfig() {
    const response = await fetch(`${API_BASE_URL}/config`);
    return handleResponse(response);
  },

  // Mise à jour de la configuration
  async updateConfig(config) {
    const response = await fetch(`${API_BASE_URL}/config`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    return handleResponse(response);
  }
};

export default api;
