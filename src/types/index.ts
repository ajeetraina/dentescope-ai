export interface ToothMeasurement {
  toothType: 'primary_second_molar' | 'second_premolar';
  toothNumber: string;
  width: number;
  confidence: number;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

export interface AnalysisResult {
  id: string;
  patientAge: number;
  measurements: ToothMeasurement[];
  widthDifference: number;
  clinicalRecommendation: string;
  confidence: number;
  timestamp: string;
}

export interface SampleXRay {
  id: string;
  name: string;
  imageUrl: string;
  patientAge: number;
  description: string;
  expectedFindings: string;
}

export interface DetectedTooth {
  type: 'primary_second_molar' | 'second_premolar' | 'first_premolar' | 'first_molar';
  number: string;
  quadrant: 'upper_right' | 'upper_left' | 'lower_right' | 'lower_left';
  width: number;
  confidence: number;
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}
