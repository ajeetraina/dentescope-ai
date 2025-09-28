import { useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Eye } from 'lucide-react';

interface AnnotatedImageProps {
  imageFile: File | null;
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
    const { primary_second_molar, second_premolar } = analysisData.tooth_width_analysis;
    
    // Check if coordinates exist
    if (!primary_second_molar.coordinates || !second_premolar.coordinates) {
      console.warn('Coordinates not available for annotation');
      return;
    }
    
    // Scale coordinates to canvas size (assuming coordinates are normalized 0-1)
    const scaleCoords = (coords: { x: number; y: number; width: number; height: number }) => ({
      x: coords.x * canvasWidth,
      y: coords.y * canvasHeight,
      width: coords.width * canvasWidth,
      height: coords.height * canvasHeight
    });

    const molarCoords = scaleCoords(primary_second_molar.coordinates);
    const premolarCoords = scaleCoords(second_premolar.coordinates);

    // Set drawing styles
    ctx.strokeStyle = '#3b82f6'; // Primary blue
    ctx.fillStyle = 'rgba(59, 130, 246, 0.2)';
    ctx.lineWidth = 3;
    ctx.font = '16px system-ui';

    // Draw primary second molar annotation
    ctx.fillRect(molarCoords.x, molarCoords.y, molarCoords.width, molarCoords.height);
    ctx.strokeRect(molarCoords.x, molarCoords.y, molarCoords.width, molarCoords.height);
    
    // Label for primary second molar
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(molarCoords.x, molarCoords.y - 30, 180, 25);
    ctx.fillStyle = '#1e40af';
    ctx.fillText(
      `Primary Molar: ${primary_second_molar.width_mm.toFixed(2)}mm`,
      molarCoords.x + 5,
      molarCoords.y - 10
    );

    // Draw second premolar annotation
    ctx.fillStyle = '#10b981'; // Green
    ctx.strokeStyle = '#10b981';
    ctx.fillRect(premolarCoords.x, premolarCoords.y, premolarCoords.width, premolarCoords.height);
    ctx.strokeRect(premolarCoords.x, premolarCoords.y, premolarCoords.width, premolarCoords.height);
    
    // Label for second premolar
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(premolarCoords.x, premolarCoords.y - 30, 180, 25);
    ctx.fillStyle = '#047857';
    ctx.fillText(
      `Premolar: ${second_premolar.width_mm.toFixed(2)}mm`,
      premolarCoords.x + 5,
      premolarCoords.y - 10
    );

    // Draw measurement line between teeth
    ctx.strokeStyle = '#ef4444'; // Red
    ctx.lineWidth = 2;
    ctx.setLineDash([10, 5]);
    
    const molarCenter = {
      x: molarCoords.x + molarCoords.width / 2,
      y: molarCoords.y + molarCoords.height / 2
    };
    const premolarCenter = {
      x: premolarCoords.x + premolarCoords.width / 2,
      y: premolarCoords.y + premolarCoords.height / 2
    };

    ctx.beginPath();
    ctx.moveTo(molarCenter.x, molarCenter.y);
    ctx.lineTo(premolarCenter.x, premolarCenter.y);
    ctx.stroke();
    ctx.setLineDash([]);

    // Add measurement label in the middle
    const midX = (molarCenter.x + premolarCenter.x) / 2;
    const midY = (molarCenter.y + premolarCenter.y) / 2;
    
    const widthDiff = analysisData.tooth_width_analysis.primary_second_molar.width_mm - 
                    analysisData.tooth_width_analysis.second_premolar.width_mm;
    
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(midX - 60, midY - 15, 120, 30);
    ctx.fillStyle = '#dc2626';
    ctx.fillText(
      `Δ ${widthDiff.toFixed(2)}mm`,
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