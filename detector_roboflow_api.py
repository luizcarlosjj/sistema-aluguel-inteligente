# detector_roboflow_api.py - COM PRÉ-PROCESSAMENTO AVANÇADO
import cv2
import numpy as np
from sklearn.cluster import KMeans
from inference_sdk import InferenceHTTPClient
import os

class BetoneiraDetectorAPI:
    def __init__(self):
        # 🔑 CONFIGURE COM OS DADOS DO CÓDIGO GERADO
        self.API_KEY = "nCS2G2BqZxMZoEJxLKGZ"
        self.MODEL_ID = "aps6-1ibfu/5"
        
        self.CLIENT = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=self.API_KEY
        )
        
        print("✅ Detector API configurado com pré-processamento avançado!")
        
    def preprocess_image(self, image):
        """Pré-processamento avançado para melhorar detecção"""
        try:
            original = image.copy()
            print("🔄 Aplicando pré-processamento...")
            
            # 1. Redimensionamento inteligente (mantém aspect ratio)
            h, w = image.shape[:2]
            max_size = 1280  # Tamanho máximo para não perder detalhes
            if max(h, w) > max_size:
                scale = max_size / max(h, w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
                print(f"   📐 Redimensionado: {w}x{h} -> {new_w}x{new_h}")
            
            # 2. Melhoria de contraste (CLAHE - mais eficiente que histogram equalization)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            lab_planes = list(cv2.split(lab))
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            lab_planes[0] = clahe.apply(lab_planes[0])
            lab = cv2.merge(lab_planes)
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            print("   🌈 Contraste melhorado (CLAHE)")
            
            # 3. Redução de ruído (preserva bordas)
            image = cv2.bilateralFilter(image, 9, 75, 75)
            print("   🔊 Ruído reduzido (Bilateral Filter)")
            
            # 4. Realce de bordas para betoneiras (destaca formas circulares/retangulares)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # 5. Segmentação por cor (betoneiras geralmente têm cores específicas)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Máscaras para cores comuns de betoneiras
            masks = []
            
            # Laranja/Amarelo (cores comuns de betoneiras)
            lower_orange = np.array([10, 100, 100])
            upper_orange = np.array([25, 255, 255])
            mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
            masks.append(mask_orange)
            
            # Vermelho
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask_red = cv2.bitwise_or(mask_red1, mask_red2)
            masks.append(mask_red)
            
            # Azul (betoneiras azuis)
            lower_blue = np.array([100, 100, 100])
            upper_blue = np.array([130, 255, 255])
            mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
            masks.append(mask_blue)
            
            # Combinar todas as máscaras
            combined_mask = np.zeros_like(masks[0])
            for mask in masks:
                combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Aplicar máscara combinada à imagem
            masked_image = cv2.bitwise_and(image, image, mask=combined_mask)
            
            # 6. Se a máscara encontrou áreas significativas, usar imagem mascarada
            if np.sum(combined_mask) > 1000:  # Se há pixels relevantes na máscara
                image = masked_image
                print("   🎨 Segmentação por cor aplicada")
            else:
                print("   ⚠️  Segmentação por cor não encontrou áreas relevantes")
            
            print("✅ Pré-processamento concluído")
            return image
            
        except Exception as e:
            print(f"❌ Erro no pré-processamento: {e}")
            return original  # Retorna original se der erro

    def detect_betoneira_regions(self, image):
        """Detecta regiões prováveis de betoneiras usando técnicas de segmentação"""
        try:
            print("🔍 Executando segmentação local...")
            original = image.copy()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 1. Detecção de bordas aprimorada
            edges = cv2.Canny(gray, 30, 100)
            
            # 2. Encontrar contornos
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 3. Filtrar contornos por área e forma (betoneiras são geralmente grandes)
            min_area = 5000  # Área mínima para ser considerada betoneira
            potential_regions = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    # Aproximar contorno para verificar forma
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    # Betoneiras geralmente têm formas retangulares ou complexas
                    if len(approx) >= 4:  # Pelo menos quadrilátero
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = w / h
                        
                        # Betoneiras geralmente têm aspect ratio entre 0.5 e 2.0
                        if 0.3 <= aspect_ratio <= 3.0:
                            potential_regions.append((x, y, w, h))
                            print(f"   📦 Região potencial: {w}x{h} (área: {area:.0f})")
            
            print(f"   🎯 {len(potential_regions)} regiões potenciais encontradas")
            return potential_regions
            
        except Exception as e:
            print(f"❌ Erro na segmentação local: {e}")
            return []

    def process_image(self, image_path, os_data):
        """Processa imagem com pré-processamento avançado"""
        try:
            # Carregar imagem
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Não foi possível carregar a imagem")
            
            print(f"📷 Imagem original: {image.shape[1]}x{image.shape[0]}")
            
            # Aplicar pré-processamento avançado
            processed_image = self.preprocess_image(image)
            
            # Salvar imagem processada temporariamente
            temp_path = "temp_processed.jpg"
            cv2.imwrite(temp_path, processed_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            print("🔄 Enviando para API Roboflow...")
            
            # Fazer inferência na imagem processada
            result = self.CLIENT.infer(temp_path, model_id=self.MODEL_ID)
            
            # Limpar arquivo temporário
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Processar resultados da API
            betoneiras = []
            final_image = image.copy()  # Usar imagem original para desenhar resultados
            
            predictions = result.get('predictions', [])
            print(f"🔍 API encontrou {len(predictions)} detecções")
            
            # Se a API não encontrou nada, tentar segmentação local
            if len(predictions) == 0:
                print("🤖 API não detectou nada, aplicando segmentação local...")
                potential_regions = self.detect_betoneira_regions(image)
                
                for i, (x, y, w, h) in enumerate(potential_regions):
                    cor = self.extract_dominant_color(image, (x, y, x+w, y+h))
                    betoneira_id = f"B{i+1:03d}"
                    
                    betoneira_data = {
                        'id': betoneira_id,
                        'bbox': (x, y, x+w, y+h),
                        'conf': 0.5,  # Confiança média para detecções locais
                        'cor': cor,
                        'class': 'betoneira_potencial',
                        'local_detection': True
                    }
                    betoneiras.append(betoneira_data)
                    
                    # Desenhar bounding box em azul para detecções locais
                    cv2.rectangle(final_image, (x, y), (x+w, y+h), (255, 0, 0), 3)
                    label = f"{betoneira_id} ({cor}) [LOCAL]"
                    cv2.putText(final_image, label, (x, y-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            else:
                # Processar detecções da API
                for i, prediction in enumerate(predictions):
                    x = prediction['x']
                    y = prediction['y']
                    width = prediction['width']
                    height = prediction['height']
                    conf = prediction['confidence']
                    class_name = prediction.get('class', 'betoneira')
                    
                    # Threshold de confiança mais baixo para betoneiras
                    if conf > 0.25:  # Reduzido para capturar mais detecções
                        x1 = int(x - width/2)
                        y1 = int(y - height/2)
                        x2 = int(x + width/2)
                        y2 = int(y + height/2)
                        
                        h, w = image.shape[:2]
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(w, x2), min(h, y2)
                        
                        if x2 <= x1 or y2 <= y1:
                            continue
                        
                        cor = self.extract_dominant_color(image, (x1, y1, x2, y2))
                        betoneira_id = f"B{len(betoneiras) + 1:03d}"
                        
                        betoneira_data = {
                            'id': betoneira_id,
                            'bbox': (x1, y1, x2, y2),
                            'conf': conf,
                            'cor': cor,
                            'class': class_name,
                            'local_detection': False
                        }
                        betoneiras.append(betoneira_data)
                        
                        # Desenhar bounding box em verde para detecções da API
                        color = (0, 255, 0)  # Verde
                        thickness = 2
                        cv2.rectangle(final_image, (x1, y1), (x2, y2), color, thickness)
                        label = f"{betoneira_id} ({cor}) {conf:.2f}"
                        cv2.putText(final_image, label, (x1, y1-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
            
            # Resultado final
            resultado = {
                'betoneiras': betoneiras,
                'total_detected': len(betoneiras),
                'processed_image': final_image,
                'quantidade_esperada': os_data['quantidade_esperada'],
                'image_path': image_path,
                'timestamp': os_data.get('data_cadastro', 'N/A'),
                'api_used': True,
                'preprocessing_applied': True
            }
            
            detection_source = "API" if not any(b.get('local_detection', False) for b in betoneiras) else "LOCAL"
            print(f"✅ Processamento concluído: {len(betoneiras)} betoneiras ({detection_source})")
            
            return resultado
            
        except Exception as e:
            raise Exception(f"Erro no processamento: {str(e)}")
    
    def extract_dominant_color(self, image, bbox, k=3):
        """Extrai a cor predominante com melhor precisão"""
        try:
            x1, y1, x2, y2 = map(int, bbox)
            
            h, w = image.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            if x2 <= x1 or y2 <= y1:
                return "indefinida"
                
            roi = image[y1:y2, x1:x2]
            
            if roi.size == 0:
                return "indefinida"
                
            # Converter para HSV para melhor detecção de cores
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            roi_resized = cv2.resize(hsv_roi, (100, 100))
            pixels = roi_resized.reshape(-1, 3)
            
            # Usar apenas matiz (Hue) para determinar cor principal
            hues = pixels[:, 0]
            
            # Mapear faixas de Hue para cores
            color_ranges = {
                'vermelha': [(0, 10), (170, 180)],
                'laranja': [(11, 25)],
                'amarela': [(26, 35)],
                'verde': [(36, 85)],
                'azul': [(86, 130)],
                'roxa': [(131, 145)],
                'rosa': [(146, 169)]
            }
            
            color_counts = {color: 0 for color in color_ranges}
            
            for hue in hues:
                for color_name, ranges in color_ranges.items():
                    for range_min, range_max in ranges:
                        if range_min <= hue <= range_max:
                            color_counts[color_name] += 1
                            break
            
            # Encontrar cor predominante
            dominant_color = max(color_counts, key=color_counts.get)
            
            # Se nenhuma cor foi significativamente detectada, verificar brilho
            if color_counts[dominant_color] < len(hues) * 0.1:  # Menos de 10%
                # Verificar se é branca, preta ou cinza
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                avg_brightness = np.mean(gray_roi)
                
                if avg_brightness > 200:
                    return "branca"
                elif avg_brightness < 50:
                    return "preta"
                else:
                    return "cinza"
            
            return dominant_color
            
        except Exception as e:
            print(f"Erro na extração de cor: {str(e)}")
            return "indefinida"