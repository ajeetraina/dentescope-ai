import { useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Eye } from 'lucide-react';

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
}

export function AnnotatedImage({ imageFile, imageUrl, analysisData }: AnnotatedImageProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

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
      
      // Draw professional medical annotations
      drawProfessionalMedicalAnnotations(ctx, canvas.width, canvas.height);
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
  }, [imageFile, imageUrl, analysisData]);

  const drawProfessionalMedicalAnnotations = (ctx: CanvasRenderingContext2D, canvasWidth: number, canvasHeight: number) => {
    const toothData = analysisData?.tooth_width_analysis;
    if (!toothData) return;

    const primaryMolar = toothData.primary_second_molar;
    const premolar = toothData.second_premolar;
    const widthDiff = toothData.width_difference;

    // Scale coordinates for different image sizes
    const scaleX = canvasWidth / 1200;
    const scaleY = canvasHeight / 800;

    // Actual tooth positions (mandibular/lower jaw)
    const primaryToothX = primaryMolar.coordinates.x * scaleX;
    const primaryToothY = primaryMolar.coordinates.y * scaleY;
    const premolarToothX = premolar.coordinates.x * scaleX;
    const premolarToothY = premolar.coordinates.y * scaleY;

    // Measurement box dimensions and positions
    const boxWidth = 140;
    const boxHeight = 50;
    const padding = 20;

    // Box positions (upper area)
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
    
    // Primary molar text
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
    
    // Premolar text
    ctx.fillStyle = '#047857';
    ctx.font = 'bold 14px Arial, sans-serif';
    ctx.fillText('Premolar:', premolarBoxX + 8, premolarBoxY + 18);
    ctx.font = '16px Arial, sans-serif';
    ctx.fillText(`${premolar.width_mm.toFixed(2)}mm`, premolarBoxX + 8, premolarBoxY + 38);

    // 3. Draw connecting lines from boxes to teeth
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.setLineDash([]);
    
    // Line from primary molar box to tooth
    ctx.beginPath();
    ctx.moveTo(primaryBoxX + boxWidth/2, primaryBoxY + boxHeight);
    ctx.lineTo(primaryToothX, primaryToothY - 30);
    ctx.stroke();

    // Line from premolar box to tooth
    ctx.strokeStyle = '#10b981';
    ctx.beginPath();
    ctx.moveTo(premolarBoxX + boxWidth/2, premolarBoxY + boxHeight);
    ctx.lineTo(premolarToothX, premolarToothY - 30);
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
    
    // Difference text
    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 14px Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`Δ ${widthDiff.value_mm.toFixed(2)}mm`, midX, midY + 5);

    // 6. Draw red circles highlighting teeth
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 3;
    ctx.setLineDash([]);

    // Circle around primary molar
    ctx.beginPath();
    ctx.arc(primaryToothX, primaryToothY, 25, 0, 2 * Math.PI);
    ctx.stroke();

    // Circle around premolar
    ctx.beginPath();
    ctx.arc(premolarToothX, premolarToothY, 22, 0, 2 * Math.PI);
    ctx.stroke();

    // 7. Draw labels with arrows pointing to teeth
    // Primary molar label
    const primaryLabelX = primaryToothX - 80;
    const primaryLabelY = primaryToothY + 60;
    
    // Label background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.fillRect(primaryLabelX - 5, primaryLabelY - 20, 110, 25);
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 1;
    ctx.strokeRect(primaryLabelX - 5, primaryLabelY - 20, 110, 25);
    
    // Label text
    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 14px Arial, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Primary molar', primaryLabelX, primaryLabelY - 5);
    
    // Arrow pointing to primary molar
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(primaryLabelX + 55, primaryLabelY - 20);
    ctx.lineTo(primaryToothX - 15, primaryToothY + 15);
    ctx.stroke();
    
    // Arrow head
    const angle1 = Math.atan2(primaryToothY + 15 - (primaryLabelY - 20), primaryToothX - 15 - (primaryLabelX + 55));
    ctx.beginPath();
    ctx.moveTo(primaryToothX - 15, primaryToothY + 15);
    ctx.lineTo(primaryToothX - 15 - 10 * Math.cos(angle1 - Math.PI/6), primaryToothY + 15 - 10 * Math.sin(angle1 - Math.PI/6));
    ctx.moveTo(primaryToothX - 15, primaryToothY + 15);
    ctx.lineTo(primaryToothX - 15 - 10 * Math.cos(angle1 + Math.PI/6), primaryToothY + 15 - 10 * Math.sin(angle1 + Math.PI/6));
    ctx.stroke();

    // Premolar label
    const premolarLabelX = premolarToothX - 50;
    const premolarLabelY = premolarToothY + 80;
    
    // Label background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.fillRect(premolarLabelX - 5, premolarLabelY - 20, 85, 25);
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 1;
    ctx.strokeRect(premolarLabelX - 5, premolarLabelY - 20, 85, 25);
    
    // Label text
    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 14px Arial, sans-serif';
    ctx.fillText('Premolar', premolarLabelX, premolarLabelY - 5);
    
    // Arrow pointing to premolar
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(premolarLabelX + 40, premolarLabelY - 20);
    ctx.lineTo(premolarToothX + 10, premolarToothY + 18);
    ctx.stroke();
    
    // Arrow head
    const angle2 = Math.atan2(premolarToothY + 18 - (premolarLabelY - 20), premolarToothX + 10 - (premolarLabelX + 40));
    ctx.beginPath();
    ctx.moveTo(premolarToothX + 10, premolarToothY + 18);
    ctx.lineTo(premolarToothX + 10 - 10 * Math.cos(angle2 - Math.PI/6), premolarToothY + 18 - 10 * Math.sin(angle2 - Math.PI/6));
    ctx.moveTo(premolarToothX + 10, premolarToothY + 18);
    ctx.lineTo(premolarToothX + 10 - 10 * Math.cos(angle2 + Math.PI/6), premolarToothY + 18 - 10 * Math.sin(angle2 + Math.PI/6));
    ctx.stroke();

    // Reset text alignment
    ctx.textAlign = 'start';
  };

  return (
    <Card className="shadow-card">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Eye className="h-5 w-5 text-primary" />
          Professional Dental Width Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative bg-muted rounded-lg overflow-hidden">
          <canvas
            ref={canvasRef}
            className="max-w-full h-auto"
            style={{ display: 'block', margin: '0 auto' }}
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
        
        {/* Professional Summary */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg border">
          <h3 className="font-semibold text-sm text-gray-800 mb-2">Clinical Analysis Summary</h3>
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
