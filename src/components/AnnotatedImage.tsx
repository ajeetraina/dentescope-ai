import { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Eye, Target, RotateCcw, Check } from 'lucide-react';

interface AnnotatedImageProps {
  imageFile?: File | null;
  imageUrl?: string;
  analysisData: {
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
      };
    };
  };
  onCalibratedCoordinates?: (coords: { primaryMolar: { x: number; y: number }, premolar: { x: number; y: number } }) => void;
}

interface CalibrationState {
  isCalibrating: boolean;
  calibratingTooth: 'primary' | 'premolar' | null;
  primaryMolarPos: { x: number; y: number } | null;
  premolarPos: { x: number; y: number } | null;
}

export function AnnotatedImage({ imageFile, imageUrl, analysisData, onCalibratedCoordinates }: AnnotatedImageProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [calibration, setCalibration] = useState<CalibrationState>({
    isCalibrating: false,
    calibratingTooth: null,
    primaryMolarPos: null,
    premolarPos: null
  });
  
  const [originalCoords, setOriginalCoords] = useState({
    primaryMolar: { x: 0, y: 0 },
    premolar: { x: 0, y: 0 }
  });

  useEffect(() => {
    if (!canvasRef.current || (!imageFile && !imageUrl)) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      
      // Store original coordinates from analysis
      const scaleX = canvas.width / 1200;
      const scaleY = canvas.height / 800;
      
      const originalPrimary = {
        x: analysisData.tooth_width_analysis.primary_second_molar.coordinates.x * scaleX,
        y: analysisData.tooth_width_analysis.primary_second_molar.coordinates.y * scaleY
      };
      
      const originalPremolar = {
        x: analysisData.tooth_width_analysis.second_premolar.coordinates.x * scaleX,
        y: analysisData.tooth_width_analysis.second_premolar.coordinates.y * scaleY
      };
      
      setOriginalCoords({ primaryMolar: originalPrimary, premolar: originalPremolar });
      
      // Draw annotations with current positions
      drawAdaptiveAnnotations(ctx, canvas.width, canvas.height);
    };

    if (imageFile) {
      img.src = URL.createObjectURL(imageFile);
    } else if (imageUrl) {
      img.src = imageUrl;
    }

    return () => {
      if (imageFile && img.src.startsWith('blob:')) {
        URL.revokeObjectURL(img.src);
      }
    };
  }, [imageFile, imageUrl, analysisData, calibration]);

  const drawAdaptiveAnnotations = (ctx: CanvasRenderingContext2D, canvasWidth: number, canvasHeight: number) => {
    const toothData = analysisData?.tooth_width_analysis;
    if (!toothData) return;

    const primaryMolar = toothData.primary_second_molar;
    const premolar = toothData.second_premolar;
    const widthDiff = toothData.width_difference;

    // Use calibrated positions if available, otherwise use original/calculated positions
    const primaryToothX = calibration.primaryMolarPos?.x ?? originalCoords.primaryMolar.x;
    const primaryToothY = calibration.primaryMolarPos?.y ?? originalCoords.primaryMolar.y;
    const premolarToothX = calibration.premolarPos?.x ?? originalCoords.premolar.x;
    const premolarToothY = calibration.premolarPos?.y ?? originalCoords.premolar.y;

    // Measurement box dimensions and positions
    const boxWidth = 140;
    const boxHeight = 50;
    const padding = 20;

    const primaryBoxX = padding;
    const primaryBoxY = padding;
    const premolarBoxX = canvasWidth - boxWidth - padding;
    const premolarBoxY = padding;

    // 1. Draw Primary Molar Box (Blue)
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(primaryBoxX, primaryBoxY, boxWidth, boxHeight);
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 3;
    ctx.strokeRect(primaryBoxX, primaryBoxY, boxWidth, boxHeight);
    
    ctx.fillStyle = '#1e40af';
    ctx.font = 'bold 14px Arial, sans-serif';
    ctx.fillText('Primary Molar:', primaryBoxX + 8, primaryBoxY + 18);
    ctx.font = '16px Arial, sans-serif';
    ctx.fillText(`${primaryMolar.width_mm.toFixed(2)}mm`, primaryBoxX + 8, primaryBoxY + 38);

    // 2. Draw Premolar Box (Green)
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(premolarBoxX, premolarBoxY, boxWidth, boxHeight);
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 3;
    ctx.strokeRect(premolarBoxX, premolarBoxY, boxWidth, boxHeight);
    
    ctx.fillStyle = '#047857';
    ctx.font = 'bold 14px Arial, sans-serif';
    ctx.fillText('Premolar:', premolarBoxX + 8, premolarBoxY + 18);
    ctx.font = '16px Arial, sans-serif';
    ctx.fillText(`${premolar.width_mm.toFixed(2)}mm`, premolarBoxX + 8, premolarBoxY + 38);

    // 3. Draw connecting lines to actual tooth positions
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.setLineDash([]);
    
    ctx.beginPath();
    ctx.moveTo(primaryBoxX + boxWidth/2, primaryBoxY + boxHeight);
    ctx.lineTo(primaryToothX, primaryToothY);
    ctx.stroke();

    ctx.strokeStyle = '#10b981';
    ctx.beginPath();
    ctx.moveTo(premolarBoxX + boxWidth/2, premolarBoxY + boxHeight);
    ctx.lineTo(premolarToothX, premolarToothY);
    ctx.stroke();

    // 4. Draw horizontal measurement line (red dashed)
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.setLineDash([8, 4]);
    ctx.beginPath();
    ctx.moveTo(primaryBoxX + boxWidth, primaryBoxY + boxHeight/2);
    ctx.lineTo(premolarBoxX, premolarBoxY + boxHeight/2);
    ctx.stroke();
    ctx.setLineDash([]);

    // 5. Draw difference measurement in center
    const midX = (primaryBoxX + boxWidth + premolarBoxX) / 2;
    const midY = primaryBoxY + boxHeight/2;
    
    const diffBoxWidth = 80;
    const diffBoxHeight = 30;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(midX - diffBoxWidth/2, midY - diffBoxHeight/2, diffBoxWidth, diffBoxHeight);
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.strokeRect(midX - diffBoxWidth/2, midY - diffBoxHeight/2, diffBoxWidth, diffBoxHeight);
    
    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 14px Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`Δ ${widthDiff.value_mm.toFixed(2)}mm`, midX, midY + 5);

    // 6. Draw tooth position markers
    const primaryColor = calibration.calibratingTooth === 'primary' ? '#ff6b6b' : '#ef4444';
    const premolarColor = calibration.calibratingTooth === 'premolar' ? '#ff6b6b' : '#ef4444';
    
    // Primary molar marker
    ctx.strokeStyle = primaryColor;
    ctx.lineWidth = calibration.calibratingTooth === 'primary' ? 4 : 3;
    ctx.beginPath();
    ctx.arc(primaryToothX, primaryToothY, calibration.calibratingTooth === 'primary' ? 30 : 25, 0, 2 * Math.PI);
    ctx.stroke();

    // Premolar marker
    ctx.strokeStyle = premolarColor;
    ctx.lineWidth = calibration.calibratingTooth === 'premolar' ? 4 : 3;
    ctx.beginPath();
    ctx.arc(premolarToothX, premolarToothY, calibration.calibratingTooth === 'premolar' ? 27 : 22, 0, 2 * Math.PI);
    ctx.stroke();

    // 7. Draw labels with arrows
    drawToothLabels(ctx, primaryToothX, primaryToothY, premolarToothX, premolarToothY);

    ctx.textAlign = 'start';
  };

  const drawToothLabels = (ctx: CanvasRenderingContext2D, primaryX: number, primaryY: number, premolarX: number, premolarY: number) => {
    // Primary molar label
    const primaryLabelX = primaryX - 80;
    const primaryLabelY = primaryY + 60;
    
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.fillRect(primaryLabelX - 5, primaryLabelY - 20, 110, 25);
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 1;
    ctx.strokeRect(primaryLabelX - 5, primaryLabelY - 20, 110, 25);
    
    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 14px Arial, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Primary molar', primaryLabelX, primaryLabelY - 5);
    
    // Arrow to primary molar
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(primaryLabelX + 55, primaryLabelY - 20);
    ctx.lineTo(primaryX, primaryY + 25);
    ctx.stroke();

    // Premolar label
    const premolarLabelX = premolarX - 50;
    const premolarLabelY = premolarY + 80;
    
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.fillRect(premolarLabelX - 5, premolarLabelY - 20, 85, 25);
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 1;
    ctx.strokeRect(premolarLabelX - 5, premolarLabelY - 20, 85, 25);
    
    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 14px Arial, sans-serif';
    ctx.fillText('Premolar', premolarLabelX, premolarLabelY - 5);
    
    // Arrow to premolar
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(premolarLabelX + 40, premolarLabelY - 20);
    ctx.lineTo(premolarX, premolarY + 22);
    ctx.stroke();
  };

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!calibration.isCalibrating || !calibration.calibratingTooth) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;

    if (calibration.calibratingTooth === 'primary') {
      setCalibration(prev => ({
        ...prev,
        primaryMolarPos: { x, y },
        calibratingTooth: 'premolar'
      }));
    } else if (calibration.calibratingTooth === 'premolar') {
      const newPremolarPos = { x, y };
      setCalibration(prev => ({
        ...prev,
        premolarPos: newPremolarPos,
        calibratingTooth: null,
        isCalibrating: false
      }));
      
      // Notify parent component of calibrated coordinates
      if (onCalibratedCoordinates && calibration.primaryMolarPos) {
        onCalibratedCoordinates({
          primaryMolar: calibration.primaryMolarPos,
          premolar: newPremolarPos
        });
      }
    }
  };

  const startCalibration = () => {
    setCalibration({
      isCalibrating: true,
      calibratingTooth: 'primary',
      primaryMolarPos: null,
      premolarPos: null
    });
  };

  const resetToOriginal = () => {
    setCalibration({
      isCalibrating: false,
      calibratingTooth: null,
      primaryMolarPos: null,
      premolarPos: null
    });
  };

  const acceptCalibration = () => {
    if (calibration.primaryMolarPos && calibration.premolarPos && onCalibratedCoordinates) {
      onCalibratedCoordinates({
        primaryMolar: calibration.primaryMolarPos,
        premolar: calibration.premolarPos
      });
    }
    setCalibration(prev => ({ ...prev, isCalibrating: false, calibratingTooth: null }));
  };

  return (
    <Card className="shadow-card">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-lg">
            <Eye className="h-5 w-5 text-primary" />
            Adaptive Dental Analysis
          </div>
          <div className="flex items-center gap-2">
            {!calibration.isCalibrating ? (
              <Button
                onClick={startCalibration}
                variant="outline"
                size="sm"
                className="flex items-center gap-2"
              >
                <Target className="h-4 w-4" />
                Manual Calibration
              </Button>
            ) : (
              <div className="flex items-center gap-2">
                <Button
                  onClick={resetToOriginal}
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <RotateCcw className="h-4 w-4" />
                  Reset
                </Button>
                {calibration.primaryMolarPos && calibration.premolarPos && (
                  <Button
                    onClick={acceptCalibration}
                    variant="default"
                    size="sm"
                    className="flex items-center gap-2"
                  >
                    <Check className="h-4 w-4" />
                    Accept
                  </Button>
                )}
              </div>
            )}
          </div>
        </CardTitle>
        {calibration.isCalibrating && (
          <div className="text-sm text-muted-foreground">
            {calibration.calibratingTooth === 'primary' && 
              "Click on the PRIMARY MOLAR (larger tooth in posterior region)"}
            {calibration.calibratingTooth === 'premolar' && 
              "Click on the PREMOLAR (smaller tooth anterior to molar)"}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="relative bg-muted rounded-lg overflow-hidden">
          <canvas
            ref={canvasRef}
            className="max-w-full h-auto cursor-crosshair"
            style={{ display: 'block', margin: '0 auto' }}
            onClick={handleCanvasClick}
          />
        </div>
        
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-primary/20 border-2 border-primary rounded"></div>
            <span>Primary Molar</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-emerald-500/20 border-2 border-emerald-500 rounded"></div>
            <span>Premolar</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-red-500 rounded"></div>
            <span>Measurement Line</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-red-500 rounded-full"></div>
            <span>Identified Teeth</span>
          </div>
        </div>
        
        {/* Clinical Summary */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg border">
          <h3 className="font-semibold text-sm text-gray-800 mb-2">
            Adaptive Clinical Analysis Summary
            {(calibration.primaryMolarPos || calibration.premolarPos) && 
              <span className="ml-2 text-xs text-blue-600">(Manual Calibration Applied)</span>}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium text-blue-700">Primary Molar:</span>
              <span className="ml-1">{analysisData.tooth_width_analysis.primary_second_molar.width_mm.toFixed(2)}mm</span>
            </div>
            <div>
              <span className="font-medium text-emerald-700">Premolar:</span>
              <span className="ml-1">{analysisData.tooth_width_analysis.second_premolar.width_mm.toFixed(2)}mm</span>
            </div>
            <div>
              <span className="font-medium text-red-700">Difference:</span>
              <span className="ml-1">{analysisData.tooth_width_analysis.width_difference.value_mm.toFixed(2)}mm ({analysisData.tooth_width_analysis.width_difference.percentage.toFixed(1)}%)</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
