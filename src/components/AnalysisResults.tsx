import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Ruler, TrendingUp, AlertCircle, CheckCircle2 } from 'lucide-react';
import { AnnotatedImage } from './AnnotatedImage';
import ChatBot from './ChatBot';

interface AnalysisData {
  tooth_measurement_analysis: {
    second_permanent_tooth: {
      mesiodistal_width_mm: number;
      eruption_stage: string;
      detection_confidence: number;
      coordinates: { x: number; y: number; width: number; height: number };
      eruption_tips_detected: boolean;
    };
    space_analysis: {
      available_space_mm: number;
      required_space_mm: number;
      space_adequacy: string;
      e_space_quantification: number;
    };
    measurement_calibration: {
      scale_factor: number;
      calibration_confidence: number;
      pixel_to_mm_ratio: number;
    };
  };
  image_analysis: {
    resolution: string;
    quality_score: number;
    xray_type: string;
    anatomical_landmarks_detected: string[];
  };
  clinical_insights: {
    treatment_recommendations: string[];
    orthodontic_planning_notes: string[];
    eruption_timeline_prediction: string;
  };
  processing_time_ms: number;
}

interface AnalysisResultsProps {
  data: AnalysisData;
  imageFile?: File | null;
  imageUrl?: string;
}

export function AnalysisResults({ data, imageFile, imageUrl }: AnalysisResultsProps) {
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

  // Determine status based on space adequacy
  const getStatus = (spaceAdequacy: string) => {
    if (spaceAdequacy === 'Insufficient') return 'concern';
    if (Math.abs(data.tooth_measurement_analysis.space_analysis.e_space_quantification) < 1) return 'attention';
    return 'normal';
  };

  const status = getStatus(data.tooth_measurement_analysis.space_analysis.space_adequacy);
  const statusConfig = getStatusConfig(status);
  const StatusIcon = statusConfig.icon;
  
  // Use detection confidence
  const detectionConfidence = data.tooth_measurement_analysis.second_permanent_tooth.detection_confidence * 100;

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
              <span>Detection Confidence</span>
              <span className="font-medium">{detectionConfidence.toFixed(1)}%</span>
            </div>
            <Progress value={detectionConfidence} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Measurements */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="shadow-card">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Ruler className="h-5 w-5 text-primary" />
              Tooth Measurements
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-gradient-surface rounded-lg">
              <span className="text-sm font-medium">Mesiodistal Width</span>
              <span className="text-lg font-bold text-primary">
                {data.tooth_measurement_analysis.second_permanent_tooth.mesiodistal_width_mm.toFixed(2)}mm
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gradient-surface rounded-lg">
              <span className="text-sm font-medium">Eruption Stage</span>
              <span className="text-sm font-medium text-foreground">
                {data.tooth_measurement_analysis.second_permanent_tooth.eruption_stage}
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-gradient-surface rounded-lg">
              <span className="text-sm font-medium">Available Space</span>
              <span className="text-lg font-bold text-primary">
                {data.tooth_measurement_analysis.space_analysis.available_space_mm.toFixed(2)}mm
              </span>
            </div>
            <div className="flex justify-between items-center p-3 bg-primary-light rounded-lg border-l-4 border-l-primary">
              <span className="text-sm font-medium">E-Space Quantification</span>
              <span className="text-lg font-bold text-primary-dark">
                {data.tooth_measurement_analysis.space_analysis.e_space_quantification > 0 ? '+' : ''}
                {data.tooth_measurement_analysis.space_analysis.e_space_quantification.toFixed(2)}mm
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
              {data.clinical_insights.treatment_recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-accent rounded-lg">
                  <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                  <p className="text-sm text-foreground">{recommendation}</p>
                </div>
              ))}
              
              <div className="mt-4 p-3 bg-info/10 border border-info/20 rounded-lg">
                <p className="text-sm text-foreground">
                  <strong>Space Adequacy:</strong> {data.tooth_measurement_analysis.space_analysis.space_adequacy}
                </p>
              </div>
              
              <div className="mt-2 p-3 bg-accent/50 rounded-lg">
                <p className="text-sm text-foreground">
                  <strong>Eruption Timeline:</strong> {data.clinical_insights.eruption_timeline_prediction}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Annotated Image */}
      {(imageFile || imageUrl) && (
        <AnnotatedImage 
          imageFile={imageFile} 
          imageUrl={imageUrl}
          analysisData={data} 
        />
      )}

      <ChatBot analysisData={data} />
    </div>
  );
}