import cv2
import numpy as np

class ManualToothSelector:
    def __init__(self):
        self.points = []
        self.image = None
        self.clone = None
        self.magnification = 1.25
        self.mm_per_pixel = 0.2  # Increased from 0.12
        
    def select_teeth(self, image_path):
        self.image = cv2.imread(image_path)
        self.clone = self.image.copy()
        self.points = []
        
        cv2.namedWindow("Select Teeth", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Select Teeth", self._mouse_callback)
        
        print("\nInstructions:")
        print("1. Click two points for PRIMARY MOLAR width (left-right)")
        print("2. Click two points for PREMOLAR width (left-right)")
        print("Press 'c' to confirm, 'r' to reset, 'q' to quit\n")
        
        while True:
            display = self.image.copy()
            
            for i, pt in enumerate(self.points):
                color = (255, 0, 0) if i < 2 else (0, 255, 0)
                cv2.circle(display, pt, 5, color, -1)
            
            if len(self.points) >= 2:
                cv2.line(display, self.points[0], self.points[1], (255, 0, 0), 2)
                width1 = self._calculate_distance(self.points[0], self.points[1])
                cv2.putText(display, f"Primary: {width1:.1f}px", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            if len(self.points) == 4:
                cv2.line(display, self.points[2], self.points[3], (0, 255, 0), 2)
                width2 = self._calculate_distance(self.points[2], self.points[3])
                cv2.putText(display, f"Premolar: {width2:.1f}px", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
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
    
    def _calculate_results(self):
        pm_width_px = self._calculate_distance(self.points[0], self.points[1])
        pr_width_px = self._calculate_distance(self.points[2], self.points[3])
        
        pm_width_mm = (pm_width_px * self.mm_per_pixel) / self.magnification
        pr_width_mm = (pr_width_px * self.mm_per_pixel) / self.magnification
        difference = pm_width_mm - pr_width_mm
        
        return {
            'primary_molar_width_mm': round(pm_width_mm, 2),
            'premolar_width_mm': round(pr_width_mm, 2),
            'difference_mm': round(difference, 2),
            'within_normal_range': 2.0 <= difference <= 2.8  # Fixed: was missing =
        }

if __name__ == '__main__':
    import sys
    
    selector = ManualToothSelector()
    image_path = sys.argv[1] if len(sys.argv) > 1 else '../data/samples/AARUSH 7 YRS MALE_DR DEEPAK K_2017_07_31_2D_Image_Shot.jpg'
    
    results = selector.select_teeth(image_path)
    
    if results:
        print("\nResults:")
        print(f"  Primary Molar: {results['primary_molar_width_mm']}mm")
        print(f"  Premolar: {results['premolar_width_mm']}mm")
        print(f"  Difference: {results['difference_mm']}mm")
        print(f"  Normal Range: {'YES' if results['within_normal_range'] else 'NO'}")
