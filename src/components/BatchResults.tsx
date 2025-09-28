import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CheckCircle, AlertTriangle, XCircle, Clock, FileImage, TrendingUp } from 'lucide-react';

interface BatchResultsProps {
  data: {
    total_files: number;
    processed_files: number;
    failed_files: number;
    total_processing_time_ms: number;
    results: Array<{
      fileName: string;
      fileSize: number;
      tooth_width_analysis: {
        width_difference: {
          value_mm: number;
          percentage: number;
          clinical_significance: string;
        };
      };
      processing_time_ms: number;
      status: 'success' | 'error';
      error?: string;
    }>;
    summary: {
      average_width_difference: number;
      significant_cases: number;
      moderate_cases: number;
      normal_cases: number;
    };
  };
}

export function BatchResults({ data }: BatchResultsProps) {
  const successRate = (data.processed_files / data.total_files) * 100;
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-success" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-destructive" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getSignificanceBadge = (significance: string) => {
    if (significance.includes('Significant')) {
      return <Badge variant="destructive">Significant</Badge>;
    } else if (significance.includes('Moderate')) {
      return <Badge variant="secondary">Moderate</Badge>;
    } else {
      return <Badge variant="outline">Normal</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Batch Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            Batch Analysis Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{data.total_files}</div>
              <div className="text-sm text-muted-foreground">Total Files</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-success">{data.processed_files}</div>
              <div className="text-sm text-muted-foreground">Processed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-destructive">{data.failed_files}</div>
              <div className="text-sm text-muted-foreground">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-foreground">
                {(data.total_processing_time_ms / 1000).toFixed(1)}s
              </div>
              <div className="text-sm text-muted-foreground">Total Time</div>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Success Rate</span>
                <span>{successRate.toFixed(1)}%</span>
              </div>
              <Progress value={successRate} className="h-2" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-accent/50 rounded-lg">
              <div className="text-center">
                <div className="text-lg font-semibold text-destructive">{data.summary.significant_cases}</div>
                <div className="text-sm text-muted-foreground">Significant Cases</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-warning">{data.summary.moderate_cases}</div>
                <div className="text-sm text-muted-foreground">Moderate Cases</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-semibold text-success">{data.summary.normal_cases}</div>
                <div className="text-sm text-muted-foreground">Normal Cases</div>
              </div>
            </div>

            <div className="text-center p-3 bg-info/10 rounded-lg">
              <div className="text-sm text-muted-foreground">Average Width Difference</div>
              <div className="text-xl font-bold text-foreground">
                {data.summary.average_width_difference}%
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Individual Results */}
      <Card>
        <CardHeader>
          <CardTitle>Individual Analysis Results</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="all" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all">All ({data.total_files})</TabsTrigger>
              <TabsTrigger value="significant">Significant ({data.summary.significant_cases})</TabsTrigger>
              <TabsTrigger value="moderate">Moderate ({data.summary.moderate_cases})</TabsTrigger>
              <TabsTrigger value="normal">Normal ({data.summary.normal_cases})</TabsTrigger>
            </TabsList>

            <TabsContent value="all" className="space-y-3">
              {data.results.map((result, index) => (
                <div key={index} className="flex items-center justify-between p-4 border border-border rounded-lg">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(result.status)}
                    <FileImage className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="font-medium">{result.fileName}</div>
                      <div className="text-sm text-muted-foreground">
                        {(result.fileSize / (1024 * 1024)).toFixed(2)} MB • {result.processing_time_ms}ms
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {result.status === 'success' ? (
                      <>
                        <div className="text-right">
                          <div className="font-medium">
                            {result.tooth_width_analysis.width_difference.percentage.toFixed(1)}%
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {result.tooth_width_analysis.width_difference.value_mm.toFixed(1)}mm
                          </div>
                        </div>
                        {getSignificanceBadge(result.tooth_width_analysis.width_difference.clinical_significance)}
                      </>
                    ) : (
                      <Badge variant="destructive">Failed</Badge>
                    )}
                  </div>
                </div>
              ))}
            </TabsContent>

            <TabsContent value="significant" className="space-y-3">
              {data.results
                .filter(r => r.status === 'success' && r.tooth_width_analysis.width_difference.percentage > 20)
                .map((result, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border border-destructive/20 bg-destructive/5 rounded-lg">
                    <div className="flex items-center gap-3">
                      <AlertTriangle className="h-4 w-4 text-destructive" />
                      <FileImage className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <div className="font-medium">{result.fileName}</div>
                        <div className="text-sm text-muted-foreground">
                          Requires immediate attention
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-destructive">
                        {result.tooth_width_analysis.width_difference.percentage.toFixed(1)}%
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {result.tooth_width_analysis.width_difference.value_mm.toFixed(1)}mm
                      </div>
                    </div>
                  </div>
                ))}
            </TabsContent>

            <TabsContent value="moderate" className="space-y-3">
              {data.results
                .filter(r => r.status === 'success' && r.tooth_width_analysis.width_difference.percentage > 10 && r.tooth_width_analysis.width_difference.percentage <= 20)
                .map((result, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border border-warning/20 bg-warning/5 rounded-lg">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-4 w-4 text-warning" />
                      <FileImage className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <div className="font-medium">{result.fileName}</div>
                        <div className="text-sm text-muted-foreground">
                          Monitor closely
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-warning">
                        {result.tooth_width_analysis.width_difference.percentage.toFixed(1)}%
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {result.tooth_width_analysis.width_difference.value_mm.toFixed(1)}mm
                      </div>
                    </div>
                  </div>
                ))}
            </TabsContent>

            <TabsContent value="normal" className="space-y-3">
              {data.results
                .filter(r => r.status === 'success' && r.tooth_width_analysis.width_difference.percentage <= 10)
                .map((result, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border border-success/20 bg-success/5 rounded-lg">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-4 w-4 text-success" />
                      <FileImage className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <div className="font-medium">{result.fileName}</div>
                        <div className="text-sm text-muted-foreground">
                          Normal development
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-success">
                        {result.tooth_width_analysis.width_difference.percentage.toFixed(1)}%
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {result.tooth_width_analysis.width_difference.value_mm.toFixed(1)}mm
                      </div>
                    </div>
                  </div>
                ))}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}