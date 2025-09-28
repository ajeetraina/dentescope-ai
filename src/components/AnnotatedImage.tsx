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
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    if (!canvasRef.current || (!imageFile && !imageUrl)) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    
    img.onload = () => {
      // Set canvas dimensions to match image
      canvas.width = img.width;
      canvas.height = img.height;
      
      // Clear canvas and draw image
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      
      // Draw annotations
      drawAnnotations(ctx, canvas.width, canvas.height);
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

  const drawAnnotations = (ctx: CanvasRenderingContext2D, canvasWidth: number, canvasHeight: number) => {
    const toothWidthAnalysis = analysisData?.tooth_width_analysis;
    const primaryMolar = toothWidthAnalysis?.primary_second_molar;
    const premolar = toothWidthAnalysis?.second_premolar;
    
    // Check if required data exists
    if (!primaryMolar?.coordinates || !premolar?.coordinates) {
      console.warn('Coordinates not available for annotation');
      return;
    }

    // Scale coordinates to canvas size
    const scaleX = canvasWidth / 800; // Adjust based on typical image width
    const scaleY = canvasHeight / 600; // Adjust based on typical image height
    
    // Primary second molar coordinates
    const molarX = primaryMolar.coordinates.x * scaleX;
    const molarY = primaryMolar.coordinates.y * scaleY;
    const molarWidth = primaryMolar.coordinates.width * scaleX;
    const molarHeight = primaryMolar.coordinates.height * scaleY;
    
    // Second premolar coordinates
    const premolarX = premolar.coordinates.x * scaleX;
    const premolarY = premolar.coordinates.y * scaleY;
    const premolarWidthCoord = premolar.coordinates.width * scaleX;
    const premolarHeight = premolar.coordinates.height * scaleY;

    // Draw primary second molar (blue)
    ctx.strokeStyle = '#3b82f6'; // Blue
    ctx.fillStyle = 'rgba(59, 130, 246, 0.2)';
    ctx.lineWidth = 3;
    ctx.font = '14px system-ui';

    ctx.fillRect(molarX, molarY, molarWidth, molarHeight);
    ctx.strokeRect(molarX, molarY, molarWidth, molarHeight);
    
    // Label for primary second molar
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(molarX, molarY - 35, 200, 30);
    ctx.fillStyle = '#1e40af';
    ctx.font = 'bold 14px system-ui';
    ctx.fillText('Primary Molar:', molarX + 5, molarY - 20);
    ctx.font = '12px system-ui';
    ctx.fillText(`${primaryMolar.width_mm.toFixed(2)}mm`, molarX + 5, molarY - 5);

    // Draw second premolar (green)
    ctx.fillStyle = 'rgba(16, 185, 129, 0.2)'; // Green
    ctx.strokeStyle = '#10b981';
    ctx.fillRect(premolarX, premolarY, premolarWidthCoord, premolarHeight);
    ctx.strokeRect(premolarX, premolarY, premolarWidthCoord, premolarHeight);
    
    // Label for second premolar
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(premolarX, premolarY - 35, 180, 30);
    ctx.fillStyle = '#047857';
    ctx.font = 'bold 14px system-ui';
    ctx.fillText('Premolar:', premolarX + 5, premolarY - 20);
    ctx.font = '12px system-ui';
    ctx.fillText(`${premolar.width_mm.toFixed(2)}mm`, premolarX + 5, premolarY - 5);

    // Draw measurement line between teeth (red)
    ctx.strokeStyle = '#ef4444'; // Red
    ctx.lineWidth = 2;
    ctx.setLineDash([10, 5]);
    
    const molarCenter = {
      x: molarX + molarWidth / 2,
      y: molarY + molarHeight / 2
    };
    const premolarCenter = {
      x: premolarX + premolarWidthCoord / 2,
      y: premolarY + premolarHeight / 2
    };

    ctx.beginPath();
    ctx.moveTo(molarCenter.x, molarCenter.y);
    ctx.lineTo(premolarCenter.x, premolarCenter.y);
    ctx.stroke();
    ctx.setLineDash([]);

    // Add width difference label in the middle
    const midX = (molarCenter.x + premolarCenter.x) / 2;
    const midY = (molarCenter.y + premolarCenter.y) / 2;
    
    const widthDiff = toothWidthAnalysis.width_difference;
    
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(midX - 60, midY - 15, 120, 30);
    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 14px system-ui';
    ctx.fillText(
      `Δ ${widthDiff.value_mm.toFixed(2)}mm`,
      midX - 50,
      midY + 5
    );
  };

  return (
    <Card className="shadow-card">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Eye className="h-5 w-5 text-primary" />
          Annotated Analysis
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
        <div className="mt-4 flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-primary/20 border-2 border-primary rounded"></div>
            <span>Primary Second Molar</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-emerald-500/20 border-2 border-emerald-500 rounded"></div>
            <span>Second Premolar</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-red-500 rounded"></div>
            <span>Width Difference</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}