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
      // Set canvas dimensions to match image
      canvas.width = img.width;
      canvas.height = img.height;
      
      // Clear canvas and draw image
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      
      // Draw annotations matching the reference format exactly
      drawReferenceStyleAnnotations(ctx, canvas.width, canvas.height);
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

  const drawReferenceStyleAnnotations = (ctx: CanvasRenderingContext2D, canvasWidth: number, canvasHeight: number) => {
    const toothData = analysisData?.tooth_width_analysis;
    if (!toothData) return;

    const primaryMolar = toothData.primary_second_molar;
    const premolar = toothData.second_premolar;
    const widthDiff = toothData.width_difference;

    // Scale coordinates to actual canvas size
    const scaleX = canvasWidth / 1200; // Typical panoramic X-ray width
    const scaleY = canvasHeight / 800;  // Typical panoramic X-ray height

    // Get actual tooth positions from analysis
    const primaryMolarX = primaryMolar.coordinates.x * scaleX;
    const primaryMolarY = primaryMolar.coordinates.y * scaleY;
    const premolarX = premolar.coordinates.x * scaleX;
    const premolarY = premolar.coordinates.y * scaleY;

    // 1. Draw measurement boxes in upper area (like reference image)
    const boxWidth = 150;
    const boxHeight = 60;
    const padding = 20;

    // Primary Molar box (blue) - upper left
    const primaryBoxX = padding;
    const primaryBoxY = padding;
    
    // Draw blue box with white background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(primaryBoxX, primaryBoxY, boxWidth, boxHeight);
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 3;
    ctx.strokeRect(primaryBoxX, primaryBoxY, boxWidth, boxHeight);
    
    // Blue box text
    ctx.fillStyle = '#1e40af';
    ctx.font = 'bold 14px Arial';
    ctx.fillText('Primary Molar:', primaryBoxX + 8, primaryBoxY + 20);
    ctx.font = '16px Arial';
    ctx.fillText(`${primaryMolar.width_mm.toFixed(2)}mm`, primaryBoxX + 8, primaryBoxY + 45);

    // Premolar box (green) - upper right
    const premolarBoxX = canvasWidth - boxWidth - padding;
    const premolarBoxY = padding;
    
    // Draw green box with white background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(premolarBoxX, premolarBoxY, boxWidth, boxHeight);
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 3;
    ctx.strokeRect(premolarBoxX, premolarBoxY, boxWidth, boxHeight);
    
    // Green box text
    ctx.fillStyle = '#047857';
    ctx.font = 'bold 14px Arial';
    ctx.fillText('Premolar:', premolarBoxX + 8, premolarBoxY + 20);
    ctx.font = '16px Arial';
    ctx.fillText(`${premolar.width_mm.toFixed(2)}mm`, premolarBoxX + 8, premolarBoxY + 45);

    // 2. Draw red dashed line connecting the boxes
    ctx.setLineDash([8, 4]);
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(primaryBoxX + boxWidth, primaryBoxY + boxHeight / 2);
    ctx.lineTo(premolarBoxX, premolarBoxY + boxHeight / 2);
    ctx.stroke();
    ctx.setLineDash([]); // Reset line dash

    // 3. Draw difference measurement in center
    const midX = (primaryBoxX + boxWidth + premolarBoxX) / 2;
    const midY = primaryBoxY + boxHeight / 2;
    
    // White background for difference text
    const diffTextWidth = 80;
    const diffTextHeight = 30;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(midX - diffTextWidth/2, midY - diffTextHeight/2, diffTextWidth, diffTextHeight);
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 2;
    ctx.strokeRect(midX - diffTextWidth/2, midY - diffTextHeight/2, diffTextWidth, diffTextHeight);
    
    // Difference text
    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(`Δ ${widthDiff.value_mm.toFixed(2)}mm`, midX, midY + 6);

    // 4. Draw red circles highlighting the actual teeth (like reference image)
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 3;
    ctx.setLineDash([]);

    // Circle around primary molar
    const molarRadius = 35;
    ctx.beginPath();
    ctx.arc(primaryMolarX, primaryMolarY, molarRadius, 0, 2 * Math.PI);
    ctx.stroke();

    // Circle around premolar
    const premolarRadius = 30;
    ctx.beginPath();
    ctx.arc(premolarX, premolarY, premolarRadius, 0, 2 * Math.PI);
    ctx.stroke();

    // 5. Draw labels with arrows pointing to teeth
    // Primary molar label
    const primaryLabelX = primaryMolarX - 60;
    const primaryLabelY = primaryMolarY + 80;
    
    // Label background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.fillRect(primaryLabelX - 10, primaryLabelY - 25, 120, 35);
    
    // Label text
    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'left';
    ctx.fillText('Primary molar', primaryLabelX, primaryLabelY - 5);
    
    // Arrow pointing to primary molar
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(primaryLabelX + 50, primaryLabelY - 15);
    ctx.lineTo(primaryMolarX - 20, primaryMolarY + 20);
    ctx.stroke();
    
    // Arrow head
    ctx.beginPath();
    ctx.moveTo(primaryMolarX - 20, primaryMolarY + 20);
    ctx.lineTo(primaryMolarX - 30, primaryMolarY + 15);
    ctx.moveTo(primaryMolarX - 20, primaryMolarY + 20);
    ctx.lineTo(primaryMolarX - 25, primaryMolarY + 30);
    ctx.stroke();

    // Premolar label
    const premolarLabelX = premolarX - 40;
    const premolarLabelY = premolarY + 100;
    
    // Label background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.fillRect(premolarLabelX - 10, premolarLabelY - 25, 100, 35);
    
    // Label text
    ctx.fillStyle = '#dc2626';
    ctx.font = 'bold 16px Arial';
    ctx.fillText('Premolar', premolarLabelX, premolarLabelY - 5);
    
    // Arrow pointing to premolar
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(premolarLabelX + 30, premolarLabelY - 15);
    ctx.lineTo(premolarX, premolarY + 25);
    ctx.stroke();
    
    // Arrow head
    ctx.beginPath();
    ctx.moveTo(premolarX, premolarY + 25);
    ctx.lineTo(premolarX - 10, premolarY + 20);
    ctx.moveTo(premolarX, premolarY + 25);
    ctx.lineTo(premolarX + 5, premolarY + 35);
    ctx.stroke();

    // Reset text alignment
    ctx.textAlign = 'start';
  };

  return (
    <Card className="shadow-card">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Eye className="h-5 w-5 text-primary" />
          Professional Dental Analysis
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
            <span>Width Difference Measurement</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-red-500 rounded-full"></div>
            <span>Identified Teeth</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
