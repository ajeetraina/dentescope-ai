export async function analyzeDental(file: File) {
  const formData = new FormData();
  formData.append('image', file);

  const response = await fetch('/api/analyze-dental', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Analysis failed');
  }

  return response.json();
}
