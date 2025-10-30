#!/usr/bin/env python3
"""
🚀 Dentescope-AI Inference Benchmark for Jetson Thor
Demonstrates real-time dental detection performance

Compares:
- PyTorch (.pt) vs TensorRT (.engine)
- Different model sizes
- Different batch sizes
"""

import time
import torch
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import glob

class ThorBenchmark:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else 'cpu'
        self.results = []
        
    def get_test_images(self, num_images=10):
        """Load test images"""
        image_paths = glob.glob('data/samples/*.jpg')[:num_images]
        
        if not image_paths:
            print("❌ No test images found in data/samples/")
            return None
            
        images = []
        for path in image_paths:
            img = cv2.imread(path)
            if img is not None:
                images.append(img)
                
        print(f"✅ Loaded {len(images)} test images")
        return images
        
    def warmup(self, model, images, num_warmup=10):
        """Warm up model for accurate benchmarking"""
        print("🔥 Warming up model...")
        for _ in range(num_warmup):
            for img in images[:3]:  # Use first 3 images
                _ = model.predict(img, verbose=False)
        print("✅ Warmup complete")
        
    def benchmark_model(self, model_path, images, num_runs=100):
        """Benchmark a single model"""
        print(f"\n📊 Benchmarking: {model_path}")
        
        if not Path(model_path).exists():
            print(f"⚠️  Model not found: {model_path}")
            return None
            
        # Load model
        model = YOLO(model_path)
        model.to(self.device)
        
        # Warmup
        self.warmup(model, images)
        
        # Benchmark
        print(f"🏃 Running {num_runs} inferences...")
        
        start_time = time.time()
        for _ in range(num_runs):
            for img in images:
                _ = model.predict(img, verbose=False, device=self.device)
        end_time = time.time()
        
        # Calculate metrics
        total_time = end_time - start_time
        total_inferences = num_runs * len(images)
        avg_time = (total_time / total_inferences) * 1000  # ms
        fps = total_inferences / total_time
        
        result = {
            'model': Path(model_path).name,
            'total_time': total_time,
            'avg_latency_ms': avg_time,
            'fps': fps,
            'throughput': total_inferences / total_time
        }
        
        print(f"✅ Average Latency: {avg_time:.2f} ms")
        print(f"✅ FPS: {fps:.1f}")
        print(f"✅ Throughput: {result['throughput']:.1f} images/sec")
        
        self.results.append(result)
        return result
        
    def benchmark_batch_processing(self, model_path, images, batch_sizes=[1, 4, 8, 16]):
        """Benchmark different batch sizes"""
        print(f"\n🔢 Batch Processing Benchmark: {model_path}")
        
        if not Path(model_path).exists():
            print(f"⚠️  Model not found: {model_path}")
            return None
            
        model = YOLO(model_path)
        model.to(self.device)
        
        batch_results = []
        
        for batch_size in batch_sizes:
            print(f"\n  Batch size: {batch_size}")
            
            # Create batches
            num_batches = 50
            batches = []
            for _ in range(num_batches):
                batch = images[:batch_size]
                batches.append(batch)
            
            # Warmup
            for _ in range(5):
                _ = model.predict(batches[0], verbose=False, device=self.device)
            
            # Benchmark
            start_time = time.time()
            for batch in batches:
                _ = model.predict(batch, verbose=False, device=self.device)
            end_time = time.time()
            
            total_time = end_time - start_time
            total_images = num_batches * batch_size
            throughput = total_images / total_time
            latency = (total_time / total_images) * 1000
            
            result = {
                'batch_size': batch_size,
                'throughput': throughput,
                'latency_ms': latency
            }
            
            print(f"    Throughput: {throughput:.1f} images/sec")
            print(f"    Latency: {latency:.2f} ms/image")
            
            batch_results.append(result)
            
        return batch_results
        
    def compare_formats(self, base_model_path, images):
        """Compare PyTorch vs TensorRT"""
        print("\n🔥 Format Comparison: PyTorch vs TensorRT")
        
        pt_path = base_model_path
        engine_path = str(Path(base_model_path).with_suffix('.engine'))
        
        results = {}
        
        # Benchmark PyTorch
        if Path(pt_path).exists():
            results['pytorch'] = self.benchmark_model(pt_path, images, num_runs=50)
        
        # Benchmark TensorRT
        if Path(engine_path).exists():
            results['tensorrt'] = self.benchmark_model(engine_path, images, num_runs=50)
        else:
            print(f"⚠️  TensorRT engine not found: {engine_path}")
            print("💡 Generate with: python3 train_thor.py --export")
            
        # Compare
        if 'pytorch' in results and 'tensorrt' in results:
            speedup = results['pytorch']['avg_latency_ms'] / results['tensorrt']['avg_latency_ms']
            print(f"\n🚀 TensorRT Speedup: {speedup:.1f}x faster!")
            
        return results
        
    def print_summary(self):
        """Print benchmark summary"""
        if not self.results:
            return
            
        print("\n" + "="*70)
        print("📊 BENCHMARK SUMMARY")
        print("="*70)
        
        print(f"\n{'Model':<30} {'Latency (ms)':<15} {'FPS':<10} {'Throughput':<15}")
        print("-"*70)
        
        for result in self.results:
            print(f"{result['model']:<30} "
                  f"{result['avg_latency_ms']:<15.2f} "
                  f"{result['fps']:<10.1f} "
                  f"{result['throughput']:<15.1f}")
                  
        print("="*70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Benchmark Dentescope-AI on Jetson Thor'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help='Path to model (.pt or .engine)'
    )
    
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare PyTorch vs TensorRT formats'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Benchmark batch processing'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all benchmarks'
    )
    
    args = parser.parse_args()
    
    # Create benchmark
    benchmark = ThorBenchmark()
    
    print("🦷 Dentescope-AI Inference Benchmark")
    print("🚀 Platform: NVIDIA Jetson AGX Thor")
    print("="*70)
    
    # Load test images
    images = benchmark.get_test_images(num_images=10)
    if images is None:
        return
    
    # Find model if not specified
    if not args.model:
        # Look for trained models
        models = list(Path('runs/detect').glob('**/weights/best.pt'))
        if models:
            args.model = str(max(models, key=lambda p: p.stat().st_mtime))
            print(f"📁 Using latest model: {args.model}")
        else:
            print("❌ No trained model found!")
            print("💡 Train a model first: python3 train_thor.py")
            return
    
    # Run benchmarks
    if args.all:
        # Benchmark single model
        benchmark.benchmark_model(args.model, images)
        
        # Compare formats
        benchmark.compare_formats(args.model, images)
        
        # Batch processing
        benchmark.benchmark_batch_processing(args.model, images)
        
    elif args.compare:
        benchmark.compare_formats(args.model, images)
        
    elif args.batch:
        benchmark.benchmark_batch_processing(args.model, images)
        
    else:
        # Default: single model benchmark
        benchmark.benchmark_model(args.model, images)
    
    # Print summary
    benchmark.print_summary()
    
    print("\n💡 Tips for Maximum Performance:")
    print("  1. Export to TensorRT: python3 train_thor.py --export")
    print("  2. Use batch processing for multiple images")
    print("  3. Enable FP16: model.export(format='engine', half=True)")
    print("  4. Optimize with: sudo nvpmodel -m 0 && sudo jetson_clocks")


if __name__ == '__main__':
    main()
