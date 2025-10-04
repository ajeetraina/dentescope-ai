import cv2
import numpy as np

class CalibratedToothSelector:
    def __init__(self, mm_per_pixel=0.15, magnification=1.25):
        self.points = []
        self.image = None
        self.clone = None
        self.magnification = magnification
        self.mm_per_pixel = mm_per_pixel
        
    def select_teeth(self, image_path):
        self.image = cv2.imread(image_path)
        self.clone = self.image.copy()
        self.points = []
        
        cv2.namedWindow("Select Teeth", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Select Teeth", self._mouse_callback)
        
        print("\nInstructions:")
        print("1. Click PRIMARY MOLAR edges (left-right)")
        print("2. Click PREMOLAR edges (left-right)")
        print("Press 'c' to confirm, 'r' to reset, 'q' to quit")
        print(f"\nCalibration: {self.mm_per_pixel} mm/pixel, {self.magnification}x magnification\n")
        
        while True:
            display = self.image.copy()
            
            for i, pt in enumerate(self.points):
                color = (255, 0, 0) if i < 2 else (0, 255, 0)
                cv2.circle(display, pt, 7, color, -1)
                cv2.circle(display, pt, 7, (255, 255, 255), 2)
            
            if len(self.points) >= 2:
                cv2.line(display, self.points[0], self.points[1], (255, 0, 0), 3)
                pm_mm = self._px_to_mm(self._calculate_distance(self.points[0], self.points[1]))
                cv2.putText(display, f"Primary Molar: {pm_mm:.1f}mm", 
                           (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
            
            if len(self.points) == 4:
                cv2.line(display, self.points[2], self.points[3], (0, 255, 0), 3)
                pr_mm = self._px_to_mm(self._calculate_distance(self.points[2], self.points[3]))
                cv2.putText(display, f"Premolar: {pr_mm:.1f}mm", 
                           (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                diff = pm_mm - pr_mm
                cv2.putText(display, f"Difference: {diff:.1f}mm", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            cv2.imshow("Select Teeth", display)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('r'):
                self.image = self.clone.copy()
                self.points = []
            elif key == ord('c') and len(self.points) == 4:
                break
            elif key == ord('q'):
                cv2.destroyAllWindows()
                return None
        
        cv2.destroyAllWindows()
        return self._calculate_results()
    
    def _mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(self.points) < 4:
            self.points.append((x, y))
    
    def _calculate_distance(self, pt1, pt2):
        return np.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)
    
    def _px_to_mm(self, pixels):
        return (pixels * self.mm_per_pixel) / self.magnification
    
    def _calculate_results(self):
        pm_width_mm = self._px_to_mm(self._calculate_distance(self.points[0], self.points[1]))
        pr_width_mm = self._px_to_mm(self._calculate_distance(self.points[2], self.points[3]))
        difference = pm_width_mm - pr_width_mm
        
        return {
            'primary_molar_width_mm': round(pm_width_mm, 2),
            'premolar_width_mm': round(pr_width_mm, 2),
            'difference_mm': round(difference, 2),
            'within_normal_range': 2.0 <= difference <= 2.8
        }

if __name__ == '__main__':
    import sys
    
    # Try different calibration values
    calibration = 0.15  # Adjust this: 0.1-0.2 range
    
    selector = CalibratedToothSelector(mm_per_pixel=calibration)
    image_path = sys.argv[1] if len(sys.argv) > 1 else '../data/samples/AARUSH 7 YRS MALE_DR DEEPAK K_2017_07_31_2D_Image_Shot.jpg'
    
    results = selector.select_teeth(image_path)
    
    if results:
        print("\n" + "="*50)
        print("RESULTS")
        print("="*50)
        print(f"Primary Molar: {results['primary_molar_width_mm']}mm (expected: 9-10mm)")
        print(f"Premolar: {results['premolar_width_mm']}mm (expected: 7-8mm)")
        print(f"Difference: {results['difference_mm']}mm (normal: 2.0-2.8mm)")
        print(f"Status: {'NORMAL' if results['within_normal_range'] else 'ABNORMAL'}")
