import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Eye } from 'lucide-react';

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
          Sample X-Ray Images
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Try the tool with our pre-loaded sample panoramic X-rays from different age groups
        </p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sampleImages.map((sample) => (
            <div
              key={sample.id}
              onClick={() => handleSampleSelect(sample)}
              className="group cursor-pointer border-2 border-border rounded-lg overflow-hidden hover:border-primary hover:shadow-lg transition-all"
            >
              <div className="aspect-video bg-muted overflow-hidden">
                <img
                  src={sample.url}
                  alt={sample.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    // Fallback if image fails to load
                    (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&auto=format&fit=crop';
                  }}
                />
              </div>
              <div className="p-4 bg-card">
                <h3 className="font-bold text-base text-foreground mb-1">{sample.name}</h3>
                <p className="text-sm text-muted-foreground mb-3">{sample.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                    Age {sample.name.match(/\d+/)?.[0] || '8'}
                  </span>
                  <span className="text-xs text-muted-foreground group-hover:text-primary transition-colors">
                    Click to analyze
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}