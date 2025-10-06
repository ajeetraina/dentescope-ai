import React, { useState, useRef } from 'react';
import { Upload, Circle, CheckCircle } from 'lucide-react';

export default function ManualDentalAnalysis() {
  const [image, setImage] = useState<string | null>(null);
  const [points, setPoints] = useState<[number, number][]>([]);
  const [results, setResults] = useState<any>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      setImage(event.target?.result as string);
      setPoints([]);
      setResults(null);
    };
    reader.readAsDataURL(file);
  };

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (points.length >= 4) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const newPoints = [...points, [x, y] as [number, number]];
    setPoints(newPoints);

    // Draw point
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.fillStyle = points.length < 2 ? '#3B82F6' : '#10B981';
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, 2 * Math.PI);
      ctx.fill();
    }

    // If 4 points selected, calculate
    if (newPoints.length === 4) {
      calculateMeasurements(newPoints);
    }
  };

  const calculateMeasurements = async (pts: [number, number][]) => {
    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ points: pts })
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const reset = () => {
    setPoints([]);
    setResults(null);
    if (canvasRef.current && imgRef.current) {
      const ctx = canvasRef.current.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
        ctx.drawImage(imgRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Dental Width Analysis</h1>
          <p className="text-gray-600">Manual measurement tool for development</p>
        </div>

        {!image ? (
          <div className="bg-white rounded-xl shadow-lg p-8">
            <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-blue-500">
              <Upload className="w-16 h-16 text-gray-400 mb-4" />
              <p className="text-xl font-semibold text-gray-700">Upload Panoramic X-ray</p>
              <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
            </label>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="mb-4">
                <h2 className="text-xl font-bold mb-2">Instructions:</h2>
                <ol className="list-decimal list-inside space-y-1 text-gray-700">
                  <li>Click left edge of PRIMARY MOLAR</li>
                  <li>Click right edge of PRIMARY MOLAR</li>
                  <li>Click left edge of PREMOLAR</li>
                  <li>Click right edge of PREMOLAR</li>
                </ol>
              </div>

              <div className="relative">
                <canvas
                  ref={canvasRef}
                  width={800}
                  height={600}
                  onClick={handleCanvasClick}
                  className="w-full border rounded-lg cursor-crosshair"
                />
                <img
                  ref={imgRef}
                  src={image}
                  alt="X-ray"
                  className="hidden"
                  onLoad={(e) => {
                    const img = e.target as HTMLImageElement;
                    const canvas = canvasRef.current;
                    if (canvas) {
                      const ctx = canvas.getContext('2d');
                      if (ctx) {
                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                      }
                    }
                  }}
                />
              </div>

              <div className="mt-4 flex items-center justify-between">
                <div className="flex gap-4">
                  <div className="flex items-center gap-2">
                    <Circle className={`w-4 h-4 ${points.length >= 2 ? 'text-blue-500 fill-blue-500' : 'text-gray-300'}`} />
                    <span>Primary Molar</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Circle className={`w-4 h-4 ${points.length === 4 ? 'text-green-500 fill-green-500' : 'text-gray-300'}`} />
                    <span>Premolar</span>
                  </div>
                </div>
                <button onClick={reset} className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300">
                  Reset
                </button>
              </div>
            </div>

            {results && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-4">Results</h2>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Primary Molar</p>
                    <p className="text-3xl font-bold text-blue-600">{results.primary_molar_width_mm}mm</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Difference</p>
                    <p className="text-3xl font-bold text-purple-600">Δ {results.difference_mm}mm</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Premolar</p>
                    <p className="text-3xl font-bold text-green-600">{results.premolar_width_mm}mm</p>
                  </div>
                </div>
                <div className={`mt-4 p-4 rounded-lg ${results.within_normal_range ? 'bg-green-100' : 'bg-yellow-100'}`}>
                  {results.within_normal_range ? (
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="text-green-800">Within normal range (2.0-2.8mm)</span>
                    </div>
                  ) : (
                    <span className="text-yellow-800">Outside normal range - consult orthodontist</span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
