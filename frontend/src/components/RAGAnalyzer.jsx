import React, { useState, useCallback } from 'react';
import { Settings, ChevronRight, HelpCircle } from 'lucide-react';
import { Button } from "@/components/ui/button";
import UploadScreen from './UploadScreen';
import AnalysisScreen from './AnalysisScreen';
import ResultsScreen from './ResultsScreen';
import SettingsScreen from './SettingsScreen';
import api from '../services/api';

const RAGAnalyzer = () => {
  const [currentScreen, setCurrentScreen] = useState('upload');
  const [analysisState, setAnalysisState] = useState({
    running: false,
    progress: {
      preprocessing: 0,
      embedding: 0,
      indexing: 0,
      validation: 0
    },
    results: null,
    error: null
  });

  const [files, setFiles] = useState([]);
  const [config, setConfig] = useState({
    mode: "standard",
    quality: "moyenne",
    language: "auto",
    chunkSize: 500,
    overlap: 10,
    embeddingModel: "MiniLM-L12"
  });

  const handleStartAnalysis = useCallback(async (uploadedFiles, analysisConfig) => {
    setCurrentScreen('analysis');
    setAnalysisState(prev => ({
      ...prev,
      running: true,
      error: null
    }));

    try {
      // Démarrer l'analyse
      const { task_id } = await api.startAnalysis(uploadedFiles, analysisConfig);

      // Démarrer le polling de progression
      const pollProgress = setInterval(async () => {
        try {
          const progressData = await api.getProgress(task_id);

          setAnalysisState(prev => ({
            ...prev,
            progress: progressData.progress
          }));

          if (progressData.status === 'completed') {
            clearInterval(pollProgress);
            const results = await api.getResults(task_id);
            
            setAnalysisState(prev => ({
              ...prev,
              running: false,
              results
            }));
            setCurrentScreen('results');
          } else if (progressData.status === 'error') {
            clearInterval(pollProgress);
            throw new Error(progressData.error || 'Une erreur est survenue pendant l\'analyse');
          }
        } catch (error) {
          clearInterval(pollProgress);
          setAnalysisState(prev => ({
            ...prev,
            running: false,
            error: error.message
          }));
          // Optionnel: revenir à l'écran d'upload en cas d'erreur
          setCurrentScreen('upload');
        }
      }, 1000);

    } catch (error) {
      setAnalysisState(prev => ({
        ...prev,
        running: false,
        error: error.message
      }));
      setCurrentScreen('upload');
    }
  }, []);

  const handleUpdateConfig = useCallback((newConfig) => {
    setConfig(prev => ({
      ...prev,
      ...newConfig
    }));
  }, []);

  const renderScreen = () => {
    switch(currentScreen) {
      case 'upload':
        return (
          <UploadScreen 
            files={files}
            setFiles={setFiles}
            config={config}
            onConfigChange={handleUpdateConfig}
            onStartAnalysis={() => handleStartAnalysis(files, config)}
          />
        );
      case 'analysis':
        return (
          <AnalysisScreen 
            progress={analysisState.progress}
            error={analysisState.error}
            onComplete={() => setCurrentScreen('results')}
          />
        );
      case 'results':
        return (
          <ResultsScreen 
            results={analysisState.results}
            onRestart={() => {
              setFiles([]);
              setAnalysisState(prev => ({
                ...prev,
                results: null,
                error: null
              }));
              setCurrentScreen('upload');
            }}
          />
        );
      case 'settings':
        return (
          <SettingsScreen 
            config={config}
            onConfigChange={handleUpdateConfig}
            onClose={() => setCurrentScreen('upload')}
          />
        );
      default:
        return <UploadScreen />;
    }
  };

  const isScreenAccessible = (screen) => {
    switch(screen) {
      case 'upload':
        return true;
      case 'analysis':
        return analysisState.running;
      case 'results':
        return analysisState.results !== null;
      case 'settings':
        return true;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header avec navigation */}
        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold mb-2">RAG Document Analyzer</h1>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <span 
                  className={`cursor-pointer ${currentScreen === 'upload' ? 'text-blue-600 font-medium' : ''}`}
                  onClick={() => isScreenAccessible('upload') && setCurrentScreen('upload')}
                >
                  Upload
                </span>
                <ChevronRight className="w-4 h-4" />
                
                <span 
                  className={`${currentScreen === 'analysis' ? 'text-blue-600 font-medium' : ''} 
                    ${!isScreenAccessible('analysis') && 'text-gray-400'}`}
                >
                  Analyse
                </span>
                <ChevronRight className="w-4 h-4" />
                
                <span 
                  className={`${currentScreen === 'results' ? 'text-blue-600 font-medium' : ''} 
                    ${!isScreenAccessible('results') && 'text-gray-400'}`}
                >
                  Résultats
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="icon" 
                onClick={() => setCurrentScreen('settings')}
              >
                <Settings className="w-4 h-4" />
              </Button>
              <Button 
                variant="outline" 
                size="icon"
                onClick={() => window.open('/docs', '_blank')}
              >
                <HelpCircle className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Afficher les erreurs s'il y en a */}
        {analysisState.error && (
          <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-lg">
            <div className="font-medium">Une erreur est survenue</div>
            <div className="text-sm">{analysisState.error}</div>
          </div>
        )}

        {/* Contenu principal */}
        {renderScreen()}
      </div>
    </div>
  );
};

export default RAGAnalyzer;
