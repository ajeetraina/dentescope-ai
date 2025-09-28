import { useState } from 'react';
import { FileUpload } from '@/components/FileUpload';
import { ProcessingView } from '@/components/ProcessingView';
import { AnalysisResults } from '@/components/AnalysisResults';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Stethoscope, Download, RefreshCw } from 'lucide-react';

type AppState = 'upload' | 'processing' | 'results';

const Index = () => {
  const [appState, setAppState] = useState<AppState>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Mock analysis data - in real app, this would come from your backend
  const mockAnalysisData = {
    primaryMolarWidth: 8.2,
    premolarWidth: 6.8,
    widthDifference: 1.4,
    confidenceScore: 94,
    status: 'normal' as const,
    recommendations: [
      'Width difference within normal range for this age group',
      'Monitor development during next routine checkup',
      'Consider space maintenance if extraction is planned'
    ]
  };

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
  };

  const handleStartAnalysis = () => {
    if (selectedFile) {
      setAppState('processing');
    }
  };

  const handleAnalysisComplete = () => {
    setAppState('results');
  };

  const handleNewAnalysis = () => {
    setSelectedFile(null);
    setAppState('upload');
  };

  const handleDownloadReport = () => {
    // In real app, generate and download PDF report
    console.log('Downloading report...');
  };

  return (
    <div className="min-h-screen bg-gradient-surface">
      {/* Header */}
      <header className="bg-card shadow-card border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-gradient-primary rounded-lg">
                <Stethoscope className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">
                  Dental Width Predictor
                </h1>
                <p className="text-sm text-muted-foreground">
                  AI-powered tooth width analysis
                </p>
              </div>
            </div>
            
            {appState === 'results' && (
              <div className="flex space-x-2">
                <Button variant="outline" onClick={handleDownloadReport}>
                  <Download className="h-4 w-4 mr-2" />
                  Export Report
                </Button>
                <Button onClick={handleNewAnalysis}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  New Analysis
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {appState === 'upload' && (
          <div className="max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-foreground mb-4">
                Upload Dental Radiograph
              </h2>
              <p className="text-lg text-muted-foreground">
                Upload an X-ray image to analyze tooth width differences between 
                primary second molars and second premolars
              </p>
            </div>

            <FileUpload onFileSelect={handleFileSelect} />

            {selectedFile && (
              <Card className="mt-6 shadow-card">
                <CardHeader>
                  <CardTitle>Ready for Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{selectedFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        Image ready for AI analysis
                      </p>
                    </div>
                    <Button onClick={handleStartAnalysis} className="bg-gradient-primary">
                      Start Analysis
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            <Separator className="my-8" />

            {/* Info Section */}
            <Card className="shadow-card">
              <CardHeader>
                <CardTitle>How It Works</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-primary-light rounded-lg flex items-center justify-center mx-auto mb-3">
                      <span className="text-primary font-bold">1</span>
                    </div>
                    <h3 className="font-semibold mb-2">Upload Image</h3>
                    <p className="text-sm text-muted-foreground">
                      Upload a dental radiograph showing molars and premolars
                    </p>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 bg-primary-light rounded-lg flex items-center justify-center mx-auto mb-3">
                      <span className="text-primary font-bold">2</span>
                    </div>
                    <h3 className="font-semibold mb-2">AI Analysis</h3>
                    <p className="text-sm text-muted-foreground">
                      Our AI identifies and measures tooth widths precisely
                    </p>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 bg-primary-light rounded-lg flex items-center justify-center mx-auto mb-3">
                      <span className="text-primary font-bold">3</span>
                    </div>
                    <h3 className="font-semibold mb-2">Get Results</h3>
                    <p className="text-sm text-muted-foreground">
                      Receive detailed measurements and clinical recommendations
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {appState === 'processing' && (
          <div className="max-w-2xl mx-auto">
            <ProcessingView onComplete={handleAnalysisComplete} />
          </div>
        )}

        {appState === 'results' && (
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-foreground mb-4">
                Analysis Results
              </h2>
              <p className="text-lg text-muted-foreground">
                Detailed measurements and clinical insights for your dental radiograph
              </p>
            </div>
            
            <AnalysisResults data={mockAnalysisData} />
          </div>
        )}
      </main>
    </div>
  );
};

export default Index;
