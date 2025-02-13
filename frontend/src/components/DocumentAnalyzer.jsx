import React, { useState } from 'react';
import { Progress } from "@/components/ui/progress";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { 
  Upload, FileText, Settings, Activity, ChevronRight,
  BarChart2, Clock, AlertCircle, Check, X, HelpCircle
} from 'lucide-react';
import { useAnalysis } from '../hooks/useAnalysis';

// Composant d'analyse
const AnalysisScreen = ({ onComplete, analysisState }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Analyse en cours
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <Progress value={analysisState.progress} />
            </div>
            <span className="text-sm font-medium">{analysisState.progress}%</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-gray-500" />
                <span className="font-medium">Temps écoulé</span>
              </div>
              <span>2m 30s</span>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <BarChart2 className="w-4 h-4 text-gray-500" />
                <span className="font-medium">Documents traités</span>
              </div>
              <span>3/5</span>
            </div>

            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-4 h-4 text-gray-500" />
                <span className="font-medium">Statut</span>
              </div>
              <Badge variant={analysisState.error ? "destructive" : "default"}>
                {analysisState.error ? "Erreur" : "En cours"}
              </Badge>
            </div>
          </div>

          {analysisState.currentFile && (
            <div className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium mb-2">Document en cours</h3>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <FileText className="w-4 h-4" />
                <span>{analysisState.currentFile}</span>
              </div>
            </div>
          )}

          {analysisState.error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2 text-red-600 mb-2">
                <AlertCircle className="w-4 h-4" />
                <span className="font-medium">Erreur détectée</span>
              </div>
              <p className="text-sm text-red-600">{analysisState.error}</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Composant de résultats
const ResultsScreen = ({ results }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Check className="w-5 h-5" />
          Résultats de l&apos;analyse
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Tabs defaultValue="summary">
            <TabsList>
              <TabsTrigger value="summary">Résumé</TabsTrigger>
              <TabsTrigger value="details">Détails</TabsTrigger>
              <TabsTrigger value="raw">Données brutes</TabsTrigger>
            </TabsList>

            <TabsContent value="summary">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium mb-4">Aperçu des résultats</h3>
                {/* Ajoutez ici le contenu du résumé */}
              </div>
            </TabsContent>

            <TabsContent value="details">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium mb-4">Détails de l&apos;analyse</h3>
                {/* Ajoutez ici les détails */}
              </div>
            </TabsContent>

            <TabsContent value="raw">
              <div className="bg-gray-50 rounded-lg p-4 overflow-auto max-h-[500px]">
                <pre className="text-sm">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </CardContent>
    </Card>
  );
};

// Composant d'upload (comme fourni dans le code)
const UploadScreen = ({ onStartAnalysis, files, setFiles, config, setConfig }) => {
  const handleFileUpload = (e) => {
    const uploadedFiles = Array.from(e.target.files);
    setFiles(prevFiles => [...prevFiles, ...uploadedFiles]);
  };

  const removeFile = (index) => {
    setFiles(prevFiles => prevFiles.filter((_, i) => i !== index));
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Upload de Documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="border-2 border-dashed rounded-lg p-8 text-center">
              <input
                type="file"
                multiple
                className="hidden"
                id="file-upload"
                onChange={handleFileUpload}
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer text-blue-600 hover:text-blue-800"
              >
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="mb-1">Glissez vos documents ici</p>
                <p className="text-sm text-gray-500">ou cliquez pour sélectionner</p>
              </label>
            </div>

            {files.length > 0 && (
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-gray-500" />
                      <span className="text-sm">{file.name}</span>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-gray-500 hover:text-red-500"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Configuration Analyse
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Mode d&apos;analyse</span>
              <select 
                className="p-2 border rounded"
                value={config.mode}
                onChange={(e) => setConfig({...config, mode: e.target.value})}
              >
                <option value="standard">Standard</option>
                <option value="approfondi">Approfondi</option>
                <option value="rapide">Rapide</option>
              </select>
            </div>
            
            <div className="flex items-center justify-between">
              <span>Qualité minimale</span>
              <select 
                className="p-2 border rounded"
                value={config.quality}
                onChange={(e) => setConfig({...config, quality: e.target.value})}
              >
                <option value="haute">Haute</option>
                <option value="moyenne">Moyenne</option>
                <option value="basse">Basse</option>
              </select>
            </div>

            <div className="flex items-center justify-between">
              <span>Langue</span>
              <select 
                className="p-2 border rounded"
                value={config.language}
                onChange={(e) => setConfig({...config, language: e.target.value})}
              >
                <option value="auto">Auto-détection</option>
                <option value="fr">Français</option>
                <option value="en">English</option>
              </select>
            </div>

            <div className="pt-4">
              <Button 
                className="w-full"
                disabled={files.length === 0}
                onClick={onStartAnalysis}
              >
                Démarrer l&apos;analyse
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Composant principal
export const DocumentAnalyzer = () => {
  const [currentScreen, setCurrentScreen] = useState('upload');
  const [files, setFiles] = useState([]);
  const [config, setConfig] = useState({
    mode: "standard",
    quality: "moyenne",
    language: "auto"
  });

  const { analysisState, startAnalysis, getResults } = useAnalysis();

  const handleStartAnalysis = async () => {
    setCurrentScreen('analysis');
    try {
      await startAnalysis(files, config);
      if (analysisState.status === 'completed') {
        setCurrentScreen('results');
      }
    } catch (error) {
      console.error('Erreur lors de l\'analyse:', error);
    }
  };

  const renderScreen = () => {
    switch(currentScreen) {
      case 'upload':
        return (
          <UploadScreen 
            onStartAnalysis={handleStartAnalysis}
            files={files}
            setFiles={setFiles}
            config={config}
            setConfig={setConfig}
          />
        );
      case 'analysis':
        return (
          <AnalysisScreen 
            onComplete={() => setCurrentScreen('results')} 
            analysisState={analysisState}
          />
        );
      case 'results':
        return <ResultsScreen results={analysisState.results} />;
      default:
        return <UploadScreen />;
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
                  onClick={() => currentScreen === 'upload' && setCurrentScreen('upload')}
                >
                  Upload
                </span>
                <ChevronRight className="w-4 h-4" />
                
                <span 
                  className={currentScreen === 'analysis' ? 'text-blue-600 font-medium' : ''}
                >
                  Analyse
                </span>
                <ChevronRight className="w-4 h-4" />
                
                <span 
                  className={currentScreen === 'results' ? 'text-blue-600 font-medium' : ''}
                >
                  Résultats
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" size="icon">
                <Settings className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon">
                <HelpCircle className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>

        {/* Contenu principal */}
        {renderScreen()}
      </div>
    </div>
  );
};
