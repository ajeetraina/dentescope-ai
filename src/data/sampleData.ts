import { SampleXRay, DetectedTooth } from '../types';

export const sampleXRays: SampleXRay[] = [
  {
    id: 'sample-1',
    name: 'Patient A - Age 8',
    imageUrl: '/samples/sample-xray-1.jpg',
    patientAge: 8,
    description: 'Normal mixed dentition with primary second molars present',
    expectedFindings: 'Width difference of approximately 1.5-2mm expected'
  },
  {
    id: 'sample-2',
    name: 'Patient B - Age 9',
    imageUrl: '/samples/sample-xray-2.jpg',
    patientAge: 9,
    description: 'Early mixed dentition with emerging premolars',
    expectedFindings: 'Premolars beginning to develop, width difference 2-2.5mm'
  },
  {
    id: 'sample-3',
    name: 'Patient C - Age 10',
    imageUrl: '/samples/sample-xray-3.jpg',
    patientAge: 10,
    description: 'Transitional dentition with visible premolar development',
    expectedFindings: 'Clear premolar formation visible, width difference 1.8-2.2mm'
  },
  {
    id: 'sample-4',
    name: 'Patient D - Age 7',
    imageUrl: '/samples/sample-xray-1.jpg',
    patientAge: 7,
    description: 'Primary dentition with early premolar buds',
    expectedFindings: 'Minimal premolar development, width difference 1.2-1.5mm'
  },
  {
    id: 'sample-5',
    name: 'Patient E - Age 11',
    imageUrl: '/samples/sample-xray-2.jpg',
    patientAge: 11,
    description: 'Late mixed dentition with advanced premolar development',
    expectedFindings: 'Advanced premolar development, width difference 2.2-2.8mm'
  }
];

// Mock tooth detection algorithm - simulates AI detection
export function detectTeeth(imageUrl: string, patientAge: number): DetectedTooth[] {
  // Simulate detection based on patient age and generate realistic measurements
  const baseConfidence = 0.85 + Math.random() * 0.1;
  
  const teeth: DetectedTooth[] = [];
  
  // Upper right quadrant
  teeth.push({
    type: 'primary_second_molar',
    number: '55',
    quadrant: 'upper_right',
    width: 8.5 + Math.random() * 1.5,
    confidence: baseConfidence,
    bbox: { x: 420, y: 150, width: 45, height: 60 }
  });
  
  teeth.push({
    type: 'second_premolar',
    number: '15',
    quadrant: 'upper_right',
    width: 6.8 + Math.random() * 1.2,
    confidence: baseConfidence - 0.05,
    bbox: { x: 425, y: 180, width: 38, height: 55 }
  });
  
  teeth.push({
    type: 'first_premolar',
    number: '14',
    quadrant: 'upper_right',
    width: 6.5 + Math.random() * 1.0,
    confidence: baseConfidence,
    bbox: { x: 380, y: 160, width: 40, height: 58 }
  });
  
  // Upper left quadrant
  teeth.push({
    type: 'primary_second_molar',
    number: '65',
    quadrant: 'upper_left',
    width: 8.3 + Math.random() * 1.5,
    confidence: baseConfidence,
    bbox: { x: 580, y: 150, width: 45, height: 60 }
  });
  
  teeth.push({
    type: 'second_premolar',
    number: '25',
    quadrant: 'upper_left',
    width: 6.7 + Math.random() * 1.2,
    confidence: baseConfidence - 0.05,
    bbox: { x: 575, y: 180, width: 38, height: 55 }
  });
  
  teeth.push({
    type: 'first_premolar',
    number: '24',
    quadrant: 'upper_left',
    width: 6.6 + Math.random() * 1.0,
    confidence: baseConfidence,
    bbox: { x: 620, y: 160, width: 40, height: 58 }
  });
  
  // Lower right quadrant
  teeth.push({
    type: 'primary_second_molar',
    number: '85',
    quadrant: 'lower_right',
    width: 9.2 + Math.random() * 1.5,
    confidence: baseConfidence,
    bbox: { x: 420, y: 450, width: 48, height: 62 }
  });
  
  teeth.push({
    type: 'second_premolar',
    number: '45',
    quadrant: 'lower_right',
    width: 7.1 + Math.random() * 1.2,
    confidence: baseConfidence - 0.05,
    bbox: { x: 425, y: 420, width: 40, height: 57 }
  });
  
  teeth.push({
    type: 'first_premolar',
    number: '44',
    quadrant: 'lower_right',
    width: 6.9 + Math.random() * 1.0,
    confidence: baseConfidence,
    bbox: { x: 380, y: 440, width: 41, height: 59 }
  });
  
  // Lower left quadrant
  teeth.push({
    type: 'primary_second_molar',
    number: '75',
    quadrant: 'lower_left',
    width: 9.0 + Math.random() * 1.5,
    confidence: baseConfidence,
    bbox: { x: 580, y: 450, width: 48, height: 62 }
  });
  
  teeth.push({
    type: 'second_premolar',
    number: '35',
    quadrant: 'lower_left',
    width: 7.0 + Math.random() * 1.2,
    confidence: baseConfidence - 0.05,
    bbox: { x: 575, y: 420, width: 40, height: 57 }
  });
  
  teeth.push({
    type: 'first_premolar',
    number: '34',
    quadrant: 'lower_left',
    width: 6.8 + Math.random() * 1.0,
    confidence: baseConfidence,
    bbox: { x: 620, y: 440, width: 41, height: 59 }
  });
  
  return teeth;
}

export function analyzeWidthDifference(teeth: DetectedTooth[]): {
  averageDifference: number;
  findings: string[];
  recommendation: string;
} {
  const primaryMolars = teeth.filter(t => t.type === 'primary_second_molar');
  const secondPremolars = teeth.filter(t => t.type === 'second_premolar');
  
  if (primaryMolars.length === 0 || secondPremolars.length === 0) {
    return {
      averageDifference: 0,
      findings: ['Insufficient tooth detection for analysis'],
      recommendation: 'Please ensure both primary second molars and second premolars are visible in the radiograph'
    };
  }
  
  const differences = primaryMolars.map((pm, idx) => {
    if (secondPremolars[idx]) {
      return pm.width - secondPremolars[idx].width;
    }
    return 0;
  }).filter(d => d > 0);
  
  const averageDifference = differences.reduce((a, b) => a + b, 0) / differences.length;
  
  const findings: string[] = [];
  let recommendation: string;
  
  if (averageDifference < 1.0) {
    findings.push('Minimal width difference detected (< 1.0mm)');
    findings.push('Lower risk of crowding in permanent dentition');
    recommendation = 'Continue routine monitoring. Favorable prognosis for natural alignment.';
  } else if (averageDifference >= 1.0 && averageDifference < 2.0) {
    findings.push(`Normal width difference detected (${averageDifference.toFixed(2)}mm)`);
    findings.push('Typical space relationship for mixed dentition');
    recommendation = 'Standard monitoring recommended. Space maintenance may be beneficial if primary molars are lost prematurely.';
  } else if (averageDifference >= 2.0 && averageDifference < 3.0) {
    findings.push(`Moderate width difference detected (${averageDifference.toFixed(2)}mm)`);
    findings.push('Some space discrepancy anticipated');
    recommendation = 'Close monitoring advised. Consider space analysis and potential need for orthodontic intervention in late mixed dentition.';
  } else {
    findings.push(`Significant width difference detected (${averageDifference.toFixed(2)}mm)`);
    findings.push('High probability of space deficiency');
    recommendation = 'Early orthodontic consultation recommended. Comprehensive space analysis and treatment planning advised.';
  }
  
  findings.push(`${primaryMolars.length} primary second molars analyzed`);
  findings.push(`${secondPremolars.length} second premolars analyzed`);
  
  return {
    averageDifference,
    findings,
    recommendation
  };
}
