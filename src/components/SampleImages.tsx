import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, Eye } from 'lucide-react';

interface SampleImagesProps {
  onSampleSelect: (imageUrl: string, fileName: string) => void;
}

const sampleImages = [
  {
    id: 1,
    name: "Primary Molar - Normal Development",
    description: "7-year-old male patient showing normal primary second molar development",
    url: "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&auto=format&fit=crop",
    fileName: "sample1.jpg"
  },
  {
    id: 2,
    name: "Width Discrepancy Case",
    description: "8-year-old female patient with potential width differences",
    url: "https://images.unsplash.com/photo-1606811971618-4486d14f3f99?w=800&auto=format&fit=crop", 
    fileName: "sample2.jpg"
  },
  {
    id: 3,
    name: "Bilateral Comparison",
    description: "7-year-old female patient for bilateral measurement comparison",
    url: "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=800&auto=format&fit=crop",
    fileName: "sample3.jpg"
  }
];

export function SampleImages({ onSampleSelect }: SampleImagesProps) {
  const handleSampleSelect = async (sample: typeof sampleImages[0]) => {
    try {
      // Create a File object from the sample image URL
      const response = await fetch(sample.url);
      const blob = await response.blob();
      const file = new File([blob], sample.fileName, { type: 'image/jpeg' });
      
      // Create a data URL for immediate display
      const reader = new FileReader();
      reader.onload = () => {
        onSampleSelect(reader.result as string, sample.fileName);
      };
      reader.readAsDataURL(file);
      
    } catch (error) {
      console.error('Failed to load sample image:', error);
      // Fallback: just pass the URL
      onSampleSelect(sample.url, sample.fileName);
    }
  };

  return (
    <Card className="w-full shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Eye className="h-5 w-5 text-primary" />
          Sample Dataset
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Try the analysis with these sample dental radiographs from the repository
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {sampleImages.map((sample) => (
          <div
            key={sample.id}
            className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-accent/50 transition-colors"
          >
            <div className="flex-1">
              <h4 className="font-medium text-foreground">{sample.name}</h4>
              <p className="text-sm text-muted-foreground mt-1">
                {sample.description}
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSampleSelect(sample)}
                className="text-primary hover:text-primary-foreground"
              >
                <Download className="h-4 w-4 mr-2" />
                Use Sample
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}