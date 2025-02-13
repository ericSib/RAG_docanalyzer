import { useState, useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const useAnalysis = () => {
  const [analysisState, setAnalysisState] = useState({
    status: 'idle', // 'idle', 'running', 'completed', 'error'
    progress: 0,
    currentFile: null,
    error: null,
    results: null,
    jobId: null
  });

  const startAnalysis = async (files, config) => {
    try {
      setAnalysisState(prev => ({
        ...prev,
        status: 'running',
        progress: 0,
        error: null
      }));

      // Créer un FormData avec les fichiers et la configuration
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      formData.append('config', JSON.stringify(config));

      // Envoyer la requête au backend
      const response = await fetch(`${API_URL}/analyze/`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Erreur lors du démarrage de l\'analyse');
      }

      const data = await response.json();
      setAnalysisState(prev => ({
        ...prev,
        jobId: data.job_id
      }));

      // Démarrer le polling pour suivre la progression
      startPolling(data.job_id);
    } catch (error) {
      setAnalysisState(prev => ({
        ...prev,
        status: 'error',
        error: error.message
      }));
    }
  };

  const startPolling = (jobId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_URL}/analysis/${jobId}/status`);
        if (!response.ok) {
          throw new Error('Erreur lors de la récupération du statut');
        }

        const data = await response.json();
        setAnalysisState(prev => ({
          ...prev,
          status: data.status,
          progress: data.progress,
          currentFile: data.current_file,
          error: data.error
        }));

        if (data.status === 'completed' || data.status === 'error') {
          clearInterval(pollInterval);
          if (data.status === 'completed') {
            getResults(jobId);
          }
        }
      } catch (error) {
        clearInterval(pollInterval);
        setAnalysisState(prev => ({
          ...prev,
          status: 'error',
          error: error.message
        }));
      }
    }, 1000);
  };

  const getResults = async (jobId) => {
    try {
      const response = await fetch(`${API_URL}/analysis/${jobId}/results`);
      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des résultats');
      }

      const data = await response.json();
      setAnalysisState(prev => ({
        ...prev,
        results: data
      }));
    } catch (error) {
      setAnalysisState(prev => ({
        ...prev,
        status: 'error',
        error: error.message
      }));
    }
  };

  // Nettoyage au démontage du composant
  useEffect(() => {
    return () => {
      // Le polling sera arrêté automatiquement grâce au cleanup de startPolling
    };
  }, []);

  return {
    analysisState,
    startAnalysis,
    getResults
  };
};
