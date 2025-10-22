import React, { useState, useRef } from 'react';
import { Upload, Circle, CheckCircle, Microscope } from 'lucide-react';
import { sampleXRays } from '../data/sampleData';

export default function ManualDentalAnalysis() {
  const [image, setImage] = useState<string | null>(null);
  const [points, setPoints] = useState<[number, number][]>([]);
  const [results, setResults] = useState<any>(null);
  const [showSamples, setShowSamples] = useState(true);
  const [selectedSample, setSelectedSample] = useState<string | null>(null);
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
      setShowSamples(false);
      setSelectedSample(null);
    };
    reader.readAsDataURL(file);
  };

  const handleSampleSelect = (sampleId: string, imageUrl: string) => {
    setImage(imageUrl);
    setPoints([]);
    setResults(null);
    setShowSamples(false);
    setSelectedSample(sampleId);
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

  const backToSelection = () => {
    setImage(null);
    setPoints([]);
    setResults(null);
    setShowSamples(true);
    setSelectedSample(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">🦷 Dental Width Analysis</h1>
          <p className="text-gray-600">Manual measurement tool with sample X-ray data</p>
        </div>

        {!image ? (
          <div className="space-y-6">
            {/* Upload Section */}
            <div className="bg-white rounded-xl shadow-lg p-8">
              <label className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-blue-500 transition-colors">
                <Upload className="w-12 h-12 text-gray-400 mb-3" />
                <p className="text-xl font-semibold text-gray-700 mb-1">Upload Your Panoramic X-ray</p>
                <p className="text-sm text-gray-500">or choose from sample images below</p>
                <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
              </label>
            </div>

            {/* Sample Data Section */}
            {showSamples && (
              <div className="bg-white rounded-xl shadow-lg p-8">
                <div className="flex items-center gap-2 mb-6">
                  <Microscope className="w-6 h-6 text-blue-600" />
                  <h2 className="text-2xl font-bold text-gray-900">Sample X-Ray Images</h2>
                </div>
                <p className="text-gray-600 mb-6">
                  Try the tool with our pre-loaded sample panoramic X-rays from different age groups
                </p>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {sampleXRays.map((sample) => (
                    <div
                      key={sample.id}
                      onClick={() => handleSampleSelect(sample.id, sample.imageUrl)}
                      className="cursor-pointer group border-2 border-gray-200 rounded-lg overflow-hidden hover:border-blue-500 hover:shadow-lg transition-all"
                    >
                      <div className="aspect-video bg-gray-100 overflow-hidden">
                        <img
                          src={sample.imageUrl}
                          alt={sample.name}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                        />
                      </div>
                      <div className="p-4">
                        <h3 className="font-bold text-lg text-gray-900 mb-1">{sample.name}</h3>
                        <p className="text-sm text-gray-600 mb-2">{sample.description}</p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            Age {sample.patientAge}
                          </span>
                          <span className="text-xs text-gray-500">Click to analyze</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-semibold text-blue-900 mb-2">Expected Findings:</h3>
                  <ul className="space-y-1 text-sm text-blue-800">
                    <li>• <strong>Ages 7-8:</strong> Primary second molars present, minimal premolar development</li>
                    <li>• <strong>Ages 9-10:</strong> Transitional dentition with emerging premolars</li>
                    <li>• <strong>Age 11+:</strong> Advanced premolar development, some primary molars may be lost</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            {/* Analysis Section */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              {selectedSample && (
                <div className="mb-4 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-blue-900">
                        Sample: {sampleXRays.find(s => s.id === selectedSample)?.name}
                      </p>
                      <p className="text-xs text-blue-700 mt-1">
                        {sampleXRays.find(s => s.id === selectedSample)?.expectedFindings}
                      </p>
                    </div>
                    <button
                      onClick={backToSelection}
                      className="px-3 py-1 text-sm bg-white text-blue-600 border border-blue-300 rounded hover:bg-blue-50 transition-colors"
                    >
                      Change Sample
                    </button>
                  </div>
                </div>
              )}

              <div className="mb-4">
                <h2 className="text-xl font-bold mb-2">Instructions:</h2>
                <ol className="list-decimal list-inside space-y-1 text-gray-700">
                  <li>Click left edge of PRIMARY MOLAR (deciduous tooth)</li>
                  <li>Click right edge of PRIMARY MOLAR</li>
                  <li>Click left edge of PREMOLAR (permanent tooth)</li>
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
                    <span className="text-sm">Primary Molar ({points.length >= 2 ? 'Done' : `${points.length}/2`})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Circle className={`w-4 h-4 ${points.length === 4 ? 'text-green-500 fill-green-500' : 'text-gray-300'}`} />
                    <span className="text-sm">Premolar ({points.length >= 2 ? Math.min(points.length - 2, 2) : 0}/2)</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button onClick={reset} className="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors">
                    Reset Points
                  </button>
                  <button onClick={backToSelection} className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors">
                    Back to Samples
                  </button>
                </div>
              </div>
            </div>

            {/* Results Section */}
            {results && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                  Analysis Results
                </h2>
                <div className="grid md:grid-cols-3 gap-4 mb-4">
                  <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-200">
                    <p className="text-sm text-gray-600 mb-1">Primary Molar Width</p>
                    <p className="text-3xl font-bold text-blue-600">{results.primary_molar_width_mm}mm</p>
                    <p className="text-xs text-blue-700 mt-1">Deciduous tooth (baby tooth)</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg border-2 border-purple-200">
                    <p className="text-sm text-gray-600 mb-1">Width Difference</p>
                    <p className="text-3xl font-bold text-purple-600">Δ {results.difference_mm}mm</p>
                    <p className="text-xs text-purple-700 mt-1">Molar minus premolar</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg border-2 border-green-200">
                    <p className="text-sm text-gray-600 mb-1">Premolar Width</p>
                    <p className="text-3xl font-bold text-green-600">{results.premolar_width_mm}mm</p>
                    <p className="text-xs text-green-700 mt-1">Permanent tooth</p>
                  </div>
                </div>
                <div className={`p-4 rounded-lg ${results.within_normal_range ? 'bg-green-100 border-2 border-green-300' : 'bg-yellow-100 border-2 border-yellow-300'}`}>
                  {results.within_normal_range ? (
                    <div className="flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <div>
                        <span className="text-green-800 font-semibold">Within normal range (2.0-2.8mm)</span>
                        <p className="text-sm text-green-700 mt-1">Standard monitoring recommended. Space relationship is typical for mixed dentition.</p>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <span className="text-yellow-800 font-semibold">Outside normal range</span>
                      <p className="text-sm text-yellow-700 mt-1">Consider orthodontic consultation. This width difference may indicate space management needs.</p>
                    </div>
                  )}
                </div>

                {selectedSample && (
                  <div className="mt-4 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                    <p className="text-sm font-semibold text-indigo-900 mb-1">Expected findings for this sample:</p>
                    <p className="text-sm text-indigo-800">
                      {sampleXRays.find(s => s.id === selectedSample)?.expectedFindings}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
