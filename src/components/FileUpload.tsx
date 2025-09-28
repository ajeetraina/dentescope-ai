import { useState } from 'react';
import { Upload, X, CheckCircle, FileImage } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onFileSelect: (files: File[], dataUrls: string[]) => void;
  acceptedTypes?: string;
  maxSize?: number;
  multiple?: boolean;
}

export function FileUpload({ onFileSelect, acceptedTypes = "image/*", maxSize = 10 * 1024 * 1024, multiple = false }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

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

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelection(files);
    }
  };

  const handleFileSelection = (files: File[]) => {
    const validFiles = files.filter(file => {
      if (file.size > maxSize) {
        alert(`File ${file.name} is too large. Maximum size is ${maxSize / (1024 * 1024)}MB`);
        return false;
      }
      return true;
    });

    if (validFiles.length === 0) return;

    setUploadedFiles(validFiles);
    
    const dataUrls: string[] = [];
    let loadedCount = 0;

    validFiles.forEach((file, index) => {
      const reader = new FileReader();
      reader.onload = () => {
        dataUrls[index] = reader.result as string;
        loadedCount++;
        
        if (loadedCount === validFiles.length) {
          onFileSelect(validFiles, dataUrls);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const removeFiles = () => {
    setUploadedFiles([]);
  };

  return (
    <Card className="w-full shadow-card">
      <CardHeader>
        <CardTitle>Upload X-ray Image{multiple ? 's' : ''}</CardTitle>
        <p className="text-sm text-muted-foreground">
          Upload dental X-ray image{multiple ? 's' : ''} for AI-powered tooth width analysis
        </p>
      </CardHeader>
      <CardContent>
        {uploadedFiles.length === 0 ? (
          <div
            className={cn(
              "relative border-2 border-dashed border-border rounded-lg p-6 text-center transition-colors",
              dragActive && "border-primary bg-primary/5"
            )}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="mx-auto h-8 w-8 text-muted-foreground mb-4" />
            <p className="text-sm text-muted-foreground mb-4">
              Drag and drop your X-ray image{multiple ? 's' : ''} here, or click to browse
            </p>
            <input
              type="file"
              accept={acceptedTypes}
              multiple={multiple}
              onChange={(e) => {
                const files = Array.from(e.target.files || []);
                if (files.length > 0) handleFileSelection(files);
              }}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <Button variant="outline" size="sm">
              Browse Files
            </Button>
            <p className="text-xs text-muted-foreground mt-2">
              Maximum file size: {maxSize / (1024 * 1024)}MB{multiple ? ' per file' : ''}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-4 border border-border rounded-lg bg-accent/50">
                <div className="flex items-center gap-2">
                  <FileImage className="h-4 w-4 text-primary" />
                  <span className="text-sm font-medium">{file.name}</span>
                  <span className="text-xs text-muted-foreground">
                    ({(file.size / (1024 * 1024)).toFixed(2)} MB)
                  </span>
                </div>
                {uploadedFiles.length === 1 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={removeFiles}
                    className="text-muted-foreground hover:text-destructive"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
            {uploadedFiles.length > 1 && (
              <Button
                variant="outline"
                size="sm"
                onClick={removeFiles}
                className="w-full"
              >
                Remove All Files
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}