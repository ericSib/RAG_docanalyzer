import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Settings, Save, X } from 'lucide-react';
import api from '../services/api';

const SettingsScreen = ({ onClose }) => {
  const [config, setConfig] = useState({
    chunkSize: 500,
    overlap: 50,
    embeddingModel: "MiniLM-L12",
    temperature: 0.7,
    maxTokens: 512
  });

  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadConfig = async () => {
      try {
        const apiConfig = await api.getConfig();
        setConfig({
          chunkSize: apiConfig.chunk_size,
          overlap: apiConfig.overlap,
          embeddingModel: apiConfig.ai_settings?.embedding_model || "MiniLM-L12",
          temperature: apiConfig.ai_settings?.temperature || 0.7,
          maxTokens: apiConfig.ai_settings?.max_tokens || 512
        });
      } catch (error) {
        setError(error.message);
      }
    };

    loadConfig();
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);

    try {
      await api.updateConfig({
        chunk_size: config.chunkSize,
        overlap: config.overlap,
        ai_settings: {
          embedding_model: config.embeddingModel,
          temperature: config.temperature,
          max_tokens: config.maxTokens
        }
      });
      onClose();
    } catch (error) {
      setError(error.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-2xl font-bold">Paramètres avancés</CardTitle>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded">
            {error}
          </div>
        )}

        <div className="space-y-6">
          <div>
            <h3 className="font-medium mb-2">Configuration Pipeline</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    Taille max chunk
                  </label>
                  <input
                    type="number"
                    className="w-full p-2 border rounded"
                    value={config.chunkSize}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      chunkSize: parseInt(e.target.value)
                    }))}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    Overlap
                  </label>
                  <input
                    type="number"
                    className="w-full p-2 border rounded"
                    value={config.overlap}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      overlap: parseInt(e.target.value)
                    }))}
                  />
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-medium mb-2">Configuration IA</h3>
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Modèle Embedding
                </label>
                <select
                  className="w-full p-2 border rounded"
                  value={config.embeddingModel}
                  onChange={(e) => setConfig(prev => ({
                    ...prev,
                    embeddingModel: e.target.value
                  }))}
                >
                  <option value="MiniLM-L12">MiniLM-L12</option>
                  <option value="MPNet">MPNet</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    Température
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    className="w-full p-2 border rounded"
                    value={config.temperature}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      temperature: parseFloat(e.target.value)
                    }))}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    Max Tokens
                  </label>
                  <input
                    type="number"
                    className="w-full p-2 border rounded"
                    value={config.maxTokens}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      maxTokens: parseInt(e.target.value)
                    }))}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-2 pt-4">
            <Button
              variant="outline"
              onClick={onClose}
            >
              Annuler
            </Button>
            <Button
              onClick={handleSave}
              disabled={isSaving}
            >
              {isSaving ? (
                <span className="flex items-center gap-2">
                  <Settings className="w-4 h-4 animate-spin" />
                  Enregistrement...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Save className="w-4 h-4" />
                  Enregistrer
                </span>
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SettingsScreen;
