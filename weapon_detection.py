import cv2
from ultralytics import YOLO




class WeaponDetectionSystem:
    def __init__(self, model_size='m'):
        self.model = None
        self.model_size = model_size
    
    def load_model(self, weights_path=None):
        if weights_path:
            self.model = YOLO(weights_path)
        else:
            self.model = YOLO(f'yolov8{self.model_size}.pt')
        self.model.conf = 0.25
        self.model.iou = 0.45
    
    def detect(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            results = self.model(image, augment=True)
            annotated_image = image.copy()
            detections = []
            
            for r in results[0].boxes.data:
                x1, y1, x2, y2, conf, cls = r.cpu().numpy()
                
                if conf < self.model.conf:
                    continue
                    
                classes = {0: 'Person', 1: 'Weapon', 2: 'Armed Person'}
                colors = {0: (0,255,0), 1: (0,0,255), 2: (255,0,0)}
                
                cls_idx = int(cls)
                label = classes[cls_idx]
                color = colors[cls_idx]
                
                cv2.rectangle(annotated_image, 
                            (int(x1), int(y1)), 
                            (int(x2), int(y2)), 
                            color, 3)
                
                label_text = f'{label}: {conf:.2f}'
                cv2.putText(annotated_image, 
                          label_text,
                          (int(x1), int(y1) - 5),
                          cv2.FONT_HERSHEY_SIMPLEX,
                          1.0, color, 2)
                
                detections.append({
                    'class': label,
                    'confidence': float(conf),
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })
                
            return annotated_image, detections
                
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None, None