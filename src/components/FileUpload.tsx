import { useState } from 'react';
import { Upload, X, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  acceptedTypes?: string;
  maxSize?: number; // in MB
}

export function FileUpload({ onFileSelect, acceptedTypes = 'image/*', maxSize = 10 }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelection = (file: File) => {
    if (file.size > maxSize * 1024 * 1024) {
      alert(`File size must be less than ${maxSize}MB`);
      return;
    }
    
    setUploadedFile(file);
    onFileSelect(file);
  };

  const removeFile = () => {
    setUploadedFile(null);
  };

  return (
    <Card className="w-full shadow-card">
      <CardContent className="p-8">
        {!uploadedFile ? (
          <div
            className={`
              relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300
              ${dragActive 
                ? 'border-primary bg-primary-light' 
                : 'border-border hover:border-primary/50 hover:bg-accent/30'
              }
            `}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Upload Dental Radiograph
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Drag and drop your X-ray image here, or click to browse
            </p>
            <input
              type="file"
              accept={acceptedTypes}
              onChange={(e) => e.target.files && handleFileSelection(e.target.files[0])}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <Button variant="outline" className="pointer-events-none">
              Select File
            </Button>
            <p className="text-xs text-muted-foreground mt-3">
              Supported formats: JPEG, PNG, DICOM • Max size: {maxSize}MB
            </p>
          </div>
        ) : (
          <div className="flex items-center justify-between p-4 bg-success/10 border border-success/20 rounded-lg">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-5 w-5 text-success" />
              <div>
                <p className="font-medium text-foreground">{uploadedFile.name}</p>
                <p className="text-sm text-muted-foreground">
                  {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={removeFile}
              className="text-muted-foreground hover:text-destructive"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}