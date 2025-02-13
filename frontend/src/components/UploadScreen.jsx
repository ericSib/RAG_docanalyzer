import React from 'react';
import { Upload, FileText, Settings, X } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const UploadScreen = ({ 
  files, 
  setFiles, 
  config, 
  onConfigChange, 
  onStartAnalysis 
}) => {
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
                accept=".pdf,.doc,.docx,.txt"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer text-blue-600 hover:text-blue-800"
              >
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="mb-1">Glissez vos documents ici</p>
                <p className="text-sm text-gray-500">ou cliquez pour sélectionner</p>
                <p className="text-xs text-gray-400 mt-2">
                  Formats supportés: PDF, DOC, DOCX, TXT
                </p>
              </label>
            </div>

            {files.length > 0 && (
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-gray-500" />
                      <span className="text-sm">{file.name}</span>
                      <span className="text-xs text-gray-500">
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
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
                onChange={(e) => onConfigChange({ mode: e.target.value })}
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
                onChange={(e) => onConfigChange({ quality: e.target.value })}
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
                onChange={(e) => onConfigChange({ language: e.target.value })}
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

export default UploadScreen;
