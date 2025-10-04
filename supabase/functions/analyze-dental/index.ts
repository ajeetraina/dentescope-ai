import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const formData = await req.formData()
    const imageFile = formData.get('image') as File

    if (!imageFile) {
      throw new Error('No image file provided')
    }

    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    const fileName = `${crypto.randomUUID()}.jpg`
    const { data: uploadData, error: uploadError } = await supabase.storage
      .from('dental-images')
      .upload(fileName, imageFile)

    if (uploadError) throw uploadError

    const { data: { publicUrl } } = supabase.storage
      .from('dental-images')
      .getPublicUrl(fileName)

    const pythonBackendUrl = Deno.env.get('PYTHON_BACKEND_URL')!
    
    const analysisResponse = await fetch(pythonBackendUrl + '/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_url: publicUrl,
        image_path: fileName
      })
    })

    if (!analysisResponse.ok) {
      throw new Error('Analysis failed')
    }

    const analysisResults = await analysisResponse.json()

    if (analysisResults.annotated_image_base64) {
      const annotatedFileName = `annotated_${fileName}`
      const byteCharacters = atob(analysisResults.annotated_image_base64)
      const byteNumbers = new Array(byteCharacters.length)
      
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: 'image/jpeg' })
      
      const { data: annotatedUpload, error: annotatedError } = await supabase.storage
        .from('dental-images')
        .upload(annotatedFileName, blob)

      if (annotatedError) throw annotatedError

      const { data: { publicUrl: annotatedUrl } } = supabase.storage
        .from('dental-images')
        .getPublicUrl(annotatedFileName)

      analysisResults.annotated_image_url = annotatedUrl
    }

    return new Response(
      JSON.stringify(analysisResults),
      { 
        headers: { 
          ...corsHeaders,
          'Content-Type': 'application/json' 
        } 
      }
    )

  } catch (error: any) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500,
        headers: { 
          ...corsHeaders,
          'Content-Type': 'application/json' 
        } 
      }
    )
  }
})
