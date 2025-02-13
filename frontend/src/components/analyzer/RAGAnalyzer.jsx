'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { 
  Cpu, FileText, Cog, Database, 
  Brain, Zap, AlertTriangle, 
  CheckCircle, Info
} from 'lucide-react';

const RAGAnalyzer = () => {
  const [activeStep, setActiveStep] = useState('upload');
  const [processingMode, setProcessingMode] = useState('raw');
  const [config, setConfig] = useState({
    enable_summarization: false,
    enable_query_enhancement: false,
    enable_semantic_search: true,
    temperature: 0.7,
    max_tokens: 512
  });
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [analysisProgress, setAnalysisProgress] = useState(null);

  // Charger la configuration initiale
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch('http://localhost:8000/config');
        if (response.ok) {
          const data = await response.json();
          setProcessingMode(data.processing_mode);
          if (data.ai_settings) {
            setConfig(data.ai_settings);
          }
        }
      } catch (error) {
        console.error('Error fetching configuration:', error);
      }
    };
    fetchConfig();
  }, []);

  const handleModeChange = async (mode) => {
    setProcessingMode(mode);
    try {
      const response = await fetch('http://localhost:8000/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          processing_mode: mode,
          ai_settings: mode !== 'raw' ? {
            ...config,
            mode: mode
          } : null
        }),
      });
      if (!response.ok) throw new Error('Failed to update configuration');
    } catch (error) {
      console.error('Error updating configuration:', error);
    }
  };

  const handleFileUpload = async (files) => {
    const formData = new FormData();
    for (let file of files) {
      formData.append('files', file);
    }

    try {
      setUploadStatus('uploading');
      const response = await fetch(`http://localhost:8000/upload?mode=${processingMode}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');
      
      const data = await response.json();
      setUploadStatus('success');
      
      // Démarrer le suivi de la progression
      pollAnalysisProgress(data.task_id);
      
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('error');
    }
  };

  const pollAnalysisProgress = async (taskId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/status/${taskId}`);
        if (!response.ok) throw new Error('Failed to fetch status');
        
        const data = await response.json();
        setAnalysisProgress(data);
        
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Error polling status:', error);
        clearInterval(pollInterval);
      }
    }, 1000);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* En-tête */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">RAG Document Analyzer</h1>
        <p className="text-gray-600">Analyse intelligente de documents avec configuration flexible</p>
      </div>

      {/* Configuration du mode */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cog className="w-5 h-5" />
            Configuration du traitement
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Sélection du mode */}
            <div>
              <label className="block font-medium mb-2">Mode de traitement</label>
              <div className="grid grid-cols-3 gap-4">
                {[
                  {
                    id: 'raw',
                    label: 'Sans IA',
                    description: 'Analyse vectorielle basique',
                    icon: Database
                  },
                  {
                    id: 'hybrid',
                    label: 'Hybride',
                    description: 'IA sélective sans LLM',
                    icon: Cpu
                  },
                  {
                    id: 'full_ai',
                    label: 'IA Complète',
                    description: 'Utilisation maximale de l\'IA',
                    icon: Brain
                  }
                ].map((mode) => (
                  <div
                    key={mode.id}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                      processingMode === mode.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-blue-200'
                    }`}
                    onClick={() => handleModeChange(mode.id)}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <mode.icon className="w-5 h-5" />
                      <span className="font-medium">{mode.label}</span>
                    </div>
                    <p className="text-sm text-gray-600">{mode.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Options d'IA */}
            {processingMode !== 'raw' && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">Options d'IA</h3>
                  <button
                    className="text-sm text-blue-600 hover:text-blue-700"
                    onClick={() => setShowAdvanced(!showAdvanced)}
                  >
                    {showAdvanced ? 'Masquer' : 'Afficher'} les options avancées
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="semantic_search"
                      checked={config.enable_semantic_search}
                      onChange={(e) => setConfig({
                        ...config,
                        enable_semantic_search: e.target.checked
                      })}
                    />
                    <label htmlFor="semantic_search">Recherche sémantique</label>
                  </div>

                  {processingMode === 'full_ai' && (
                    <>
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id="summarization"
                          checked={config.enable_summarization}
                          onChange={(e) => setConfig({
                            ...config,
                            enable_summarization: e.target.checked
                          })}
                        />
                        <label htmlFor="summarization">Génération de résumés</label>
                      </div>

                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          id="query_enhancement"
                          checked={config.enable_query_enhancement}
                          onChange={(e) => setConfig({
                            ...config,
                            enable_query_enhancement: e.target.checked
                          })}
                        />
                        <label htmlFor="query_enhancement">Amélioration des requêtes</label>
                      </div>
                    </>
                  )}
                </div>

                {showAdvanced && processingMode === 'full_ai' && (
                  <div className="mt-4 space-y-4 p-4 bg-gray-50 rounded-lg">
                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Température
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={config.temperature * 100}
                        onChange={(e) => setConfig({
                          ...config,
                          temperature: Number(e.target.value) / 100
                        })}
                        className="w-full"
                      />
                      <div className="flex justify-between text-sm text-gray-600">
                        <span>Plus précis</span>
                        <span>Plus créatif</span>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-1">
                        Tokens maximum
                      </label>
                      <select
                        value={config.max_tokens}
                        onChange={(e) => setConfig({
                          ...config,
                          max_tokens: Number(e.target.value)
                        })}
                        className="w-full p-2 border rounded"
                      >
                        <option value="256">256</option>
                        <option value="512">512</option>
                        <option value="1024">1024</option>
                        <option value="2048">2048</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Message d'information */}
            <div className={`p-4 rounded-lg ${
              processingMode === 'raw' 
                ? 'bg-gray-50 border-gray-200' 
                : processingMode === 'hybrid'
                ? 'bg-blue-50 border-blue-200'
                : 'bg-green-50 border-green-200'
            } border`}>
              <div className="flex gap-2">
                {processingMode === 'raw' ? (
                  <Info className="w-5 h-5 text-gray-500" />
                ) : processingMode === 'hybrid' ? (
                  <Info className="w-5 h-5 text-blue-500" />
                ) : (
                  <Brain className="w-5 h-5 text-green-500" />
                )}
                <div>
                  <p className="font-medium">
                    {processingMode === 'raw' 
                      ? 'Mode basique' 
                      : processingMode === 'hybrid'
                      ? 'Mode hybride'
                      : 'Mode IA complète'}
                  </p>
                  <p className="text-sm mt-1">
                    {processingMode === 'raw' 
                      ? 'Analyse vectorielle sans utilisation d\'IA' 
                      : processingMode === 'hybrid'
                      ? 'Utilisation sélective de l\'IA pour certaines tâches'
                      : 'Utilisation complète des capacités d\'IA'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Zone de dépôt de fichiers */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Upload de documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center ${
              uploadStatus === 'uploading' ? 'border-blue-300 bg-blue-50' :
              uploadStatus === 'success' ? 'border-green-300 bg-green-50' :
              uploadStatus === 'error' ? 'border-red-300 bg-red-50' :
              'border-gray-300 hover:border-blue-400'
            }`}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              handleFileUpload(Array.from(e.dataTransfer.files));
            }}
          >
            <input
              type="file"
              multiple
              onChange={(e) => handleFileUpload(Array.from(e.target.files))}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <div className="flex flex-col items-center gap-2">
                {uploadStatus === 'uploading' ? (
                  <>
                    <Zap className="w-8 h-8 text-blue-500 animate-pulse" />
                    <p>Upload en cours...</p>
                  </>
                ) : uploadStatus === 'success' ? (
                  <>
                    <CheckCircle className="w-8 h-8 text-green-500" />
                    <p>Upload réussi !</p>
                  </>
                ) : uploadStatus === 'error' ? (
                  <>
                    <AlertTriangle className="w-8 h-8 text-red-500" />
                    <p>Erreur lors de l'upload</p>
                  </>
                ) : (
                  <>
                    <FileText className="w-8 h-8 text-gray-400" />
                    <p>Glissez-déposez vos documents ici ou cliquez pour sélectionner</p>
                  </>
                )}
              </div>
            </label>
          </div>

          {/* Barre de progression */}
          {analysisProgress && (
            <div className="mt-4">
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium">
                  {analysisProgress.status === 'completed' ? 'Analyse terminée' :
                   analysisProgress.status === 'failed' ? 'Erreur lors de l\'analyse' :
                   'Analyse en cours...'}
                </span>
                <span className="text-sm text-gray-500">
                  {Math.round(analysisProgress.progress)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className={`h-2.5 rounded-full ${
                    analysisProgress.status === 'completed' ? 'bg-green-500' :
                    analysisProgress.status === 'failed' ? 'bg-red-500' :
                    'bg-blue-500'
                  }`}
                  style={{ width: `${analysisProgress.progress}%` }}
                ></div>
              </div>
              {analysisProgress.current_file && (
                <p className="text-sm text-gray-500 mt-2">
                  Traitement de : {analysisProgress.current_file}
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default RAGAnalyzer;
