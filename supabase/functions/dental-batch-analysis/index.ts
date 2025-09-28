import "https://deno.land/x/xhr@0.1.0/mod.ts";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface AnalysisResult {
  fileName: string;
  fileSize: number;
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
      clinical_significance: string;
    };
  };
  image_quality: {
    resolution: string;
    brightness: number;
    contrast: number;
    sharpness: number;
  };
  clinical_recommendations: string[];
  processing_time_ms: number;
  status: 'success' | 'error';
  error?: string;
}

interface BatchResult {
  total_files: number;
  processed_files: number;
  failed_files: number;
  total_processing_time_ms: number;
  results: AnalysisResult[];
  summary: {
    average_width_difference: number;
    significant_cases: number;
    moderate_cases: number;
    normal_cases: number;
  };
}

async function analyzeImage(imageFile: File): Promise<AnalysisResult> {
  const startTime = Date.now();
  
  try {
    console.log(`Processing image: ${imageFile.name}, size: ${imageFile.size} bytes`);
    
    // Convert image to base64 for processing
    const imageBuffer = await imageFile.arrayBuffer();
    const base64Image = btoa(String.fromCharCode(...new Uint8Array(imageBuffer)));
    
    // Simulate processing delay for batch
    await new Promise(resolve => setTimeout(resolve, 200 + Math.random() * 300));
    
    // Mock analysis with some variation
    const primaryMolarWidth = 10.5 + Math.random() * 2;
    const premolarWidth = 8.2 + Math.random() * 1.5;
    const widthDiff = primaryMolarWidth - premolarWidth;
    const percentage = (widthDiff / premolarWidth) * 100;
    
    const analysisResult: AnalysisResult = {
      fileName: imageFile.name,
      fileSize: imageFile.size,
      tooth_width_analysis: {
        primary_second_molar: {
          width_mm: Math.round(primaryMolarWidth * 100) / 100,
          confidence: 0.85 + Math.random() * 0.1,
          coordinates: { 
            x: 120 + Math.floor(Math.random() * 50), 
            y: 180 + Math.floor(Math.random() * 30),
            width: 45 + Math.floor(Math.random() * 10),
            height: 60 + Math.floor(Math.random() * 15)
          }
        },
        second_premolar: {
          width_mm: Math.round(premolarWidth * 100) / 100,
          confidence: 0.82 + Math.random() * 0.12,
          coordinates: { 
            x: 115 + Math.floor(Math.random() * 60), 
            y: 200 + Math.floor(Math.random() * 40),
            width: 35 + Math.floor(Math.random() * 8),
            height: 50 + Math.floor(Math.random() * 12)
          }
        },
        width_difference: {
          value_mm: Math.round(widthDiff * 100) / 100,
          percentage: Math.round(percentage * 100) / 100,
          clinical_significance: percentage > 20 ? "Significant width discrepancy detected" :
                               percentage > 10 ? "Moderate width difference" :
                               "Normal width variation"
        }
      },
      image_quality: {
        resolution: `${1024 + Math.floor(Math.random() * 512)}x${768 + Math.floor(Math.random() * 256)}`,
        brightness: 0.6 + Math.random() * 0.3,
        contrast: 0.7 + Math.random() * 0.2,
        sharpness: 0.8 + Math.random() * 0.15
      },
      clinical_recommendations: [],
      processing_time_ms: Date.now() - startTime,
      status: 'success'
    };

    // Generate clinical recommendations
    if (percentage > 20) {
      analysisResult.clinical_recommendations = [
        "Consider space maintainer placement",
        "Monitor eruption pattern closely", 
        "Orthodontic consultation recommended"
      ];
    } else if (percentage > 10) {
      analysisResult.clinical_recommendations = [
        "Regular monitoring recommended",
        "Document for future reference"
      ];
    } else {
      analysisResult.clinical_recommendations = [
        "Normal tooth development pattern",
        "Continue routine monitoring"
      ];
    }

    return analysisResult;
    
  } catch (error) {
    console.error(`Error processing ${imageFile.name}:`, error);
    return {
      fileName: imageFile.name,
      fileSize: imageFile.size,
      tooth_width_analysis: {
        primary_second_molar: { width_mm: 0, confidence: 0, coordinates: { x: 0, y: 0, width: 0, height: 0 } },
        second_premolar: { width_mm: 0, confidence: 0, coordinates: { x: 0, y: 0, width: 0, height: 0 } },
        width_difference: { value_mm: 0, percentage: 0, clinical_significance: "Analysis failed" }
      },
      image_quality: { resolution: "Unknown", brightness: 0, contrast: 0, sharpness: 0 },
      clinical_recommendations: ["Analysis failed - please retry with a different image"],
      processing_time_ms: Date.now() - startTime,
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    console.log('Batch dental analysis request received');
    
    const formData = await req.formData();
    const files: File[] = [];
    
    // Extract all files from form data
    for (const [key, value] of formData.entries()) {
      if (key.startsWith('image') && value instanceof File) {
        files.push(value);
      }
    }
    
    if (files.length === 0) {
      throw new Error('No image files provided');
    }

    console.log(`Processing ${files.length} images in batch`);
    const batchStartTime = Date.now();
    
    // Process all images concurrently for better performance
    const analysisPromises = files.map(file => analyzeImage(file));
    const results = await Promise.all(analysisPromises);
    
    const totalProcessingTime = Date.now() - batchStartTime;
    
    // Calculate batch summary statistics
    const successfulResults = results.filter(r => r.status === 'success');
    const failedResults = results.filter(r => r.status === 'error');
    
    let significantCases = 0;
    let moderateCases = 0;
    let normalCases = 0;
    let totalWidthDifference = 0;
    
    successfulResults.forEach(result => {
      const percentage = result.tooth_width_analysis.width_difference.percentage;
      totalWidthDifference += Math.abs(percentage);
      
      if (percentage > 20) significantCases++;
      else if (percentage > 10) moderateCases++;
      else normalCases++;
    });
    
    const batchResult: BatchResult = {
      total_files: files.length,
      processed_files: successfulResults.length,
      failed_files: failedResults.length,
      total_processing_time_ms: totalProcessingTime,
      results: results,
      summary: {
        average_width_difference: successfulResults.length > 0 ? 
          Math.round((totalWidthDifference / successfulResults.length) * 100) / 100 : 0,
        significant_cases: significantCases,
        moderate_cases: moderateCases,
        normal_cases: normalCases
      }
    };
    
    console.log(`Batch analysis completed: ${successfulResults.length}/${files.length} successful`);
    console.log(`Average width difference: ${batchResult.summary.average_width_difference}%`);
    console.log(`Cases breakdown - Significant: ${significantCases}, Moderate: ${moderateCases}, Normal: ${normalCases}`);

    return new Response(JSON.stringify(batchResult), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in dental-batch-analysis function:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    return new Response(JSON.stringify({ 
      error: errorMessage,
      details: 'Failed to process batch dental radiograph analysis'
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});