import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Loader2, Brain, Scan, Calculator } from 'lucide-react';

interface ProcessingStep {
  id: string;
  label: string;
  icon: React.ElementType;
  description: string;
}

const processingSteps: ProcessingStep[] = [
  {
    id: 'upload',
    label: 'Image Processing',
    icon: Scan,
    description: 'Analyzing radiograph quality and orientation'
  },
  {
    id: 'detection',
    label: 'Tooth Detection',
    icon: Brain,
    description: 'Identifying molars and premolars using AI'
  },
  {
    id: 'measurement',
    label: 'Width Measurement',
    icon: Calculator,
    description: 'Calculating precise tooth width measurements'
  }
];

interface ProcessingViewProps {
  onComplete: () => void;
}

export function ProcessingView({ onComplete }: ProcessingViewProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          setTimeout(onComplete, 500);
          return 100;
        }
        return prev + 2;
      });
    }, 100);

    const stepTimer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < processingSteps.length - 1) {
          return prev + 1;
        }
        clearInterval(stepTimer);
        return prev;
      });
    }, 2000);

    return () => {
      clearInterval(timer);
      clearInterval(stepTimer);
    };
  }, [onComplete]);

  return (
    <Card className="shadow-analysis">
      <CardContent className="p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-primary rounded-full mb-4">
            <Loader2 className="h-8 w-8 text-primary-foreground animate-spin" />
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-2">
            Analyzing Dental Radiograph
          </h2>
          <p className="text-muted-foreground">
            Our AI is processing your image to measure tooth width differences
          </p>
        </div>

        <div className="space-y-6">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="font-medium">Analysis Progress</span>
              <span className="text-primary font-bold">{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-3" />
          </div>

          <div className="space-y-4">
            {processingSteps.map((step, index) => {
              const StepIcon = step.icon;
              const isActive = index === currentStep;
              const isCompleted = index < currentStep;

              return (
                <div
                  key={step.id}
                  className={`
                    flex items-center space-x-4 p-4 rounded-lg transition-all duration-500
                    ${isActive 
                      ? 'bg-gradient-analysis border border-primary/20 shadow-medical' 
                      : isCompleted 
                        ? 'bg-success/10 border border-success/20' 
                        : 'bg-muted/30'
                    }
                  `}
                >
                  <div
                    className={`
                      flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300
                      ${isActive 
                        ? 'bg-primary text-primary-foreground' 
                        : isCompleted 
                          ? 'bg-success text-success-foreground' 
                          : 'bg-muted text-muted-foreground'
                      }
                    `}
                  >
                    <StepIcon className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <h3 className={`font-semibold ${isActive ? 'text-primary' : 'text-foreground'}`}>
                      {step.label}
                    </h3>
                    <p className="text-sm text-muted-foreground">{step.description}</p>
                  </div>
                  {isActive && (
                    <Loader2 className="h-5 w-5 text-primary animate-spin" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}