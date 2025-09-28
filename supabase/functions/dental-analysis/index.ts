import "https://deno.land/x/xhr@0.1.0/mod.ts";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface AnalysisResult {
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
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    console.log('Dental analysis request received');
    
    const formData = await req.formData();
    const imageFile = formData.get('image') as File;
    
    if (!imageFile) {
      throw new Error('No image file provided');
    }

    // Convert image to base64 for processing
    const imageBuffer = await imageFile.arrayBuffer();
    const base64Image = btoa(String.fromCharCode(...new Uint8Array(imageBuffer)));
    
    console.log(`Processing image: ${imageFile.name}, size: ${imageFile.size} bytes`);
    
    // Simulate calling your dental width prediction model
    // In production, this would call your actual model API
    const startTime = Date.now();
    
    // Mock analysis based on your model's expected output format
    const analysisResult: AnalysisResult = {
      tooth_width_analysis: {
        primary_second_molar: {
          width_mm: 10.5 + Math.random() * 2, // Realistic width range
          confidence: 0.85 + Math.random() * 0.1,
          coordinates: { 
            x: 120 + Math.floor(Math.random() * 50), 
            y: 180 + Math.floor(Math.random() * 30),
            width: 45 + Math.floor(Math.random() * 10),
            height: 60 + Math.floor(Math.random() * 15)
          }
        },
        second_premolar: {
          width_mm: 8.2 + Math.random() * 1.5,
          confidence: 0.82 + Math.random() * 0.12,
          coordinates: { 
            x: 115 + Math.floor(Math.random() * 60), 
            y: 200 + Math.floor(Math.random() * 40),
            width: 35 + Math.floor(Math.random() * 8),
            height: 50 + Math.floor(Math.random() * 12)
          }
        },
        width_difference: {
          value_mm: 0,
          percentage: 0,
          clinical_significance: ""
        }
      },
      image_quality: {
        resolution: `${1024 + Math.floor(Math.random() * 512)}x${768 + Math.floor(Math.random() * 256)}`,
        brightness: 0.6 + Math.random() * 0.3,
        contrast: 0.7 + Math.random() * 0.2,
        sharpness: 0.8 + Math.random() * 0.15
      },
      clinical_recommendations: [],
      processing_time_ms: 0
    };

    // Calculate width difference
    const widthDiff = analysisResult.tooth_width_analysis.primary_second_molar.width_mm - 
                     analysisResult.tooth_width_analysis.second_premolar.width_mm;
    const percentage = (widthDiff / analysisResult.tooth_width_analysis.second_premolar.width_mm) * 100;
    
    analysisResult.tooth_width_analysis.width_difference = {
      value_mm: Math.round(widthDiff * 100) / 100,
      percentage: Math.round(percentage * 100) / 100,
      clinical_significance: percentage > 20 ? "Significant width discrepancy detected" :
                           percentage > 10 ? "Moderate width difference" :
                           "Normal width variation"
    };

    // Generate clinical recommendations
    if (percentage > 20) {
      analysisResult.clinical_recommendations = [
        "Consider space maintainer placement",
        "Monitor eruption pattern closely",
        "Evaluate for potential crowding issues",
        "Orthodontic consultation recommended"
      ];
    } else if (percentage > 10) {
      analysisResult.clinical_recommendations = [
        "Regular monitoring recommended",
        "Document for future reference",
        "Consider preventive measures"
      ];
    } else {
      analysisResult.clinical_recommendations = [
        "Normal tooth development pattern",
        "Continue routine monitoring",
        "No immediate intervention required"
      ];
    }

    analysisResult.processing_time_ms = Date.now() - startTime;
    
    console.log('Analysis completed successfully');
    console.log(`Width difference: ${analysisResult.tooth_width_analysis.width_difference.value_mm}mm`);
    console.log(`Clinical significance: ${analysisResult.tooth_width_analysis.width_difference.clinical_significance}`);

    return new Response(JSON.stringify(analysisResult), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error in dental-analysis function:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    return new Response(JSON.stringify({ 
      error: errorMessage,
      details: 'Failed to process dental radiograph analysis'
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});