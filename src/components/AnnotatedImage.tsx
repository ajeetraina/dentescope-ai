import { useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Eye } from 'lucide-react';

interface AnnotatedImageProps {
  imageFile?: File | null;
  imageUrl?: string;
  analysisData: {
    tooth_measurement_analysis: {
      second_permanent_tooth: {
        mesiodistal_width_mm: number;
        detection_confidence: number;
        coordinates: { x: number; y: number; width: number; height: number };
        eruption_tips_detected: boolean;
        eruption_stage: string;
      };
      space_analysis: {
        available_space_mm: number;
        required_space_mm: number;
        space_adequacy: string;
        e_space_quantification: number;
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
    const measurementAnalysis = analysisData?.tooth_measurement_analysis;
    const secondPermTooth = measurementAnalysis?.second_permanent_tooth;
    const spaceAnalysis = measurementAnalysis?.space_analysis;
    
    // Check if required data exists
    if (!secondPermTooth?.coordinates) {
      console.warn('Coordinates not available for annotation');
      return;
    }
    
    // Scale coordinates to canvas size (assuming coordinates are absolute pixel values)
    const scaleX = canvasWidth / 800; // Adjust based on typical image width
    const scaleY = canvasHeight / 600; // Adjust based on typical image height
    
    const toothX = secondPermTooth.coordinates.x * scaleX;
    const toothY = secondPermTooth.coordinates.y * scaleY;
    const toothWidth = secondPermTooth.coordinates.width * scaleX;
    const toothHeight = secondPermTooth.coordinates.height * scaleY;

    // Draw tooth outline
    ctx.strokeStyle = '#3b82f6'; // Blue
    ctx.fillStyle = 'rgba(59, 130, 246, 0.1)';
    ctx.lineWidth = 3;
    ctx.font = '14px system-ui';

    // Draw tooth bounding box
    ctx.fillRect(toothX, toothY, toothWidth, toothHeight);
    ctx.strokeRect(toothX, toothY, toothWidth, toothHeight);
    
    // Draw eruption tips if detected
    if (secondPermTooth.eruption_tips_detected) {
      ctx.strokeStyle = '#10b981'; // Green for eruption tips
      ctx.lineWidth = 2;
      const tipRadius = 6;
      
      // Left eruption tip
      ctx.beginPath();
      ctx.arc(toothX + toothWidth * 0.3, toothY + 5, tipRadius, 0, 2 * Math.PI);
      ctx.stroke();
      
      // Right eruption tip  
      ctx.beginPath();
      ctx.arc(toothX + toothWidth * 0.7, toothY + 5, tipRadius, 0, 2 * Math.PI);
      ctx.stroke();
    }

    // Draw mesiodistal width measurement line
    ctx.strokeStyle = '#ef4444'; // Red
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    
    const measureY = toothY + toothHeight / 2;
    ctx.beginPath();
    ctx.moveTo(toothX, measureY);
    ctx.lineTo(toothX + toothWidth, measureY);
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw measurement arrows
    const arrowSize = 8;
    ctx.fillStyle = '#ef4444';
    
    // Left arrow
    ctx.beginPath();
    ctx.moveTo(toothX, measureY);
    ctx.lineTo(toothX + arrowSize, measureY - arrowSize/2);
    ctx.lineTo(toothX + arrowSize, measureY + arrowSize/2);
    ctx.fill();
    
    // Right arrow
    ctx.beginPath();
    ctx.moveTo(toothX + toothWidth, measureY);
    ctx.lineTo(toothX + toothWidth - arrowSize, measureY - arrowSize/2);
    ctx.lineTo(toothX + toothWidth - arrowSize, measureY + arrowSize/2);
    ctx.fill();

    // Labels
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(toothX, toothY - 40, 220, 35);
    ctx.fillStyle = '#1e40af';
    ctx.font = 'bold 14px system-ui';
    ctx.fillText(
      `Second Permanent Tooth`,
      toothX + 5,
      toothY - 20
    );
    ctx.font = '12px system-ui';
    ctx.fillText(
      `Stage: ${secondPermTooth.eruption_stage || 'Unknown'}`,
      toothX + 5,
      toothY - 5
    );

    // Mesiodistal width label
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(toothX, toothY + toothHeight + 5, 200, 25);
    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 12px system-ui';
    ctx.fillText(
      `Mesiodistal Width: ${secondPermTooth.mesiodistal_width_mm?.toFixed(1) || 'N/A'}mm`,
      toothX + 5,
      toothY + toothHeight + 20
    );

    // Space analysis indicator
    if (spaceAnalysis) {
      const spaceColor = spaceAnalysis.space_adequacy === 'Adequate' ? '#10b981' : '#ef4444';
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(toothX, toothY + toothHeight + 35, 180, 25);
      ctx.fillStyle = spaceColor;
      ctx.fillText(
        `E-Space: ${spaceAnalysis.e_space_quantification ? 
          `${spaceAnalysis.e_space_quantification > 0 ? '+' : ''}${spaceAnalysis.e_space_quantification.toFixed(1)}mm` 
          : 'N/A'}`,
        toothX + 5,
        toothY + toothHeight + 50
      );
    }
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
            <span>Second Permanent Tooth</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-emerald-500/20 border-2 border-emerald-500 rounded-full"></div>
            <span>Eruption Tips</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-red-500 rounded"></div>
            <span>Mesiodistal Width</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}