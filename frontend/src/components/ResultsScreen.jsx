import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { BarChart2, Clock, FileText } from 'lucide-react';

const ResultsScreen = ({ results }) => {
  // Utiliser des données de test si aucun résultat n'est fourni
  const demoResults = {
    summary: {
      documentCount: 3,
      totalPages: 15,
      processingTime: "2m 34s",
      quality: "95%"
    },
    documents: [
      {
        name: "document1.pdf",
        pages: 5,
        chunks: 12,
        quality: "98%",
        warnings: []
      },
      {
        name: "document2.docx",
        pages: 7,
        chunks: 18,
        quality: "93%",
        warnings: ["Images non traitées"]
      },
      {
        name: "document3.pdf",
        pages: 3,
        chunks: 8,
        quality: "94%",
        warnings: []
      }
    ]
  };

  const data = results || demoResults;

  return (
    <div className="space-y-6">
      {/* Résumé */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart2 className="w-5 h-5" />
            Résumé de l&apos;analyse
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Documents</div>
              <div className="text-2xl font-semibold">{data.summary.documentCount}</div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Pages totales</div>
              <div className="text-2xl font-semibold">{data.summary.totalPages}</div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Temps de traitement</div>
              <div className="text-2xl font-semibold">{data.summary.processingTime}</div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Qualité moyenne</div>
              <div className="text-2xl font-semibold">{data.summary.quality}</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Détails par document */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Détails par document
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.documents.map((doc, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-medium">{doc.name}</h3>
                    <div className="text-sm text-gray-500">
                      {doc.pages} pages • {doc.chunks} chunks
                    </div>
                  </div>
                  <Badge variant={doc.quality >= "95%" ? "success" : "warning"}>
                    {doc.quality}
                  </Badge>
                </div>
                {doc.warnings.length > 0 && (
                  <div className="mt-2">
                    {doc.warnings.map((warning, wIndex) => (
                      <div key={wIndex} className="text-sm text-amber-600 flex items-center gap-1">
                        <AlertCircle className="w-4 h-4" />
                        {warning}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ResultsScreen;
