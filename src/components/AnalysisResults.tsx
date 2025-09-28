import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Ruler, TrendingUp, AlertCircle, CheckCircle2 } from 'lucide-react';

interface AnalysisData {
  tooth_width_analysis: {
    primary_second_molar: {
      width_mm: number;
      confidence: number;
      coordinates: { x: number; y: number; width: number; height: number };
    };
    second_premolar: {
      width_mm: number;
      confidence: number;
      coordinates: { x: number; y: number; width: number; height: number };
    };
    width_difference: {
      value_mm: number;
      percentage: number;
      clinical_significance: string;
    };
  };
  image_quality: {
    resolution: string;
    brightness: number;
    contrast: number;
    sharpness: number;
  };
  clinical_recommendations: string[];
  processing_time_ms: number;
}

interface AnalysisResultsProps {
  data: AnalysisData;
}

export function AnalysisResults({ data }: AnalysisResultsProps) {
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'normal':
        return {
          color: 'success',
          icon: CheckCircle2,
          label: 'Normal Range',
          description: 'Measurements within expected parameters'
        };
      case 'attention':
        return {
          color: 'warning',
          icon: AlertCircle,
          label: 'Attention Required',
          description: 'Measurements suggest monitoring needed'
        };
      case 'concern':
        return {
          color: 'destructive',
          icon: AlertCircle,
          label: 'Clinical Concern',
          description: 'Significant width difference detected'
        };
      default:
        return {
          color: 'secondary',
          icon: AlertCircle,
          label: 'Unknown',
          description: ''
        };
    }
  };

  // Determine status based on width difference percentage
  const getStatus = (percentage: number) => {
    if (percentage > 20) return 'concern';
    if (percentage > 10) return 'attention';
    return 'normal';
  };

  const status = getStatus(Math.abs(data.tooth_width_analysis.width_difference.percentage));
  const statusConfig = getStatusConfig(status);
  const StatusIcon = statusConfig.icon;
  
  // Calculate average confidence
  const averageConfidence = (
    (data.tooth_width_analysis.primary_second_molar.confidence + 
     data.tooth_width_analysis.second_premolar.confidence) / 2 * 100
  );

  return (
    <div className="space-y-6">
      {/* Status Overview */}
      <Card className="shadow-medical border-l-4 border-l-primary">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <StatusIcon className={`h-5 w-5 text-${statusConfig.color}`} />
              Analysis Complete
            </CardTitle>
            <Badge variant={statusConfig.color === 'success' ? 'default' : 'destructive'}>
              {statusConfig.label}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">{statusConfig.description}</p>
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-2">
              <span>Confidence Score</span>
              <span className="font-medium">{averageConfidence.toFixed(1)}%</span>
            </div>
            <Progress value={averageConfidence} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Measurements */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="shadow-card">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Ruler className="h-5 w-5 text-primary" />
              Measurements
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-gradient-surface rounded-lg">
              <span className="text-sm font-medium">Primary Second Molar</span>
              <span className="text-lg font-bold text-primary">
                {data.tooth_width_analysis.primary_second_molar.width_mm.toFixed(2)}mm
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gradient-surface rounded-lg">
              <span className="text-sm font-medium">Second Premolar</span>
              <span className="text-lg font-bold text-primary">
                {data.tooth_width_analysis.second_premolar.width_mm.toFixed(2)}mm
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-primary-light rounded-lg border-l-4 border-l-primary">
              <span className="text-sm font-medium">Width Difference</span>
              <span className="text-lg font-bold text-primary-dark">
                {data.tooth_width_analysis.width_difference.value_mm > 0 ? '+' : ''}
                {data.tooth_width_analysis.width_difference.value_mm.toFixed(2)}mm
                ({data.tooth_width_analysis.width_difference.percentage > 0 ? '+' : ''}
                {data.tooth_width_analysis.width_difference.percentage.toFixed(1)}%)
              </span>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-card">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <TrendingUp className="h-5 w-5 text-primary" />
              Clinical Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.clinical_recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-accent rounded-lg">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                  <p className="text-sm text-foreground">{recommendation}</p>
                </div>
              ))}
              
              <div className="mt-4 p-3 bg-info/10 border border-info/20 rounded-lg">
                <p className="text-sm text-foreground">
                  <strong>Clinical Significance:</strong> {data.tooth_width_analysis.width_difference.clinical_significance}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}