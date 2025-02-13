import React, { useState, useEffect } from 'react';
import { Progress } from "@/components/ui/progress";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Activity, AlertCircle, Check } from 'lucide-react';

const AnalysisScreen = ({ onComplete }) => {
  const [progress, setProgress] = useState({
    preprocessing: 0,
    embedding: 0,
    indexing: 0,
    validation: 0
  });

  const [status, setStatus] = useState({
    preprocessing: 'pending',
    embedding: 'pending',
    indexing: 'pending',
    validation: 'pending'
  });

  // Simuler la progression (à remplacer par l'API réelle)
  useEffect(() => {
    const stages = ['preprocessing', 'embedding', 'indexing', 'validation'];
    let currentStage = 0;

    const interval = setInterval(() => {
      if (currentStage >= stages.length) {
        clearInterval(interval);
        onComplete();
        return;
      }

      const stage = stages[currentStage];
      
      setProgress(prev => ({
        ...prev,
        [stage]: prev[stage] + 10
      }));

      if (progress[stage] >= 100) {
        setStatus(prev => ({
          ...prev,
          [stage]: 'completed'
        }));
        currentStage++;
      }
    }, 500);

    return () => clearInterval(interval);
  }, [progress, onComplete]);

  const getStatusIcon = (status) => {
    switch(status) {
      case 'completed':
        return <Check className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Activity className="w-4 h-4 text-blue-500" />;
    }
  };

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
          {Object.entries(progress).map(([stage, value]) => (
            <div key={stage} className="space-y-2">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  {getStatusIcon(status[stage])}
                  <span className="capitalize">{stage}</span>
                </div>
                <span className="text-sm text-gray-500">{value}%</span>
              </div>
              <Progress value={value} />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default AnalysisScreen;
