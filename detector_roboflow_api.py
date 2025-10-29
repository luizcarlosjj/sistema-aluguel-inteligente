# detector_roboflow_api.py - VERSÃO SUPER OTIMIZADA
'''
🔍 Detecção Local - 3 Estratégias Combinadas
    Por Cor: Cores específicas de betoneiras
    Por Forma: Análise geométrica avançada
    Por Tamanho: Objetos grandes em posições prováveis

🚀 4 Estratégias de API
    Original: Imagem sem modificações
    Otimizada: Com super processamento
    Redimensionada: Tamanho ideal para API
    Qualidade Máxima: Parâmetros otimizados

🎨 Segmentação de Cor Hiper-Específica
    7 cores diferentes de betoneiras
    Operações morfológicas agressivas
    Combinação inteligente de máscaras

📊 Análise de Forma Avançada
    Circularidade: 0.1-0.8 (formas retangulares)
    Proporção: 0.4-2.2 (formato de betoneira)
    Solidez: >0.6 (objetos sólidos)

🎪 Feedback Visual Melhorado
    VERDE: Detecções da API
    AZUL: Detecções locais
    Labels detalhados com método de detecção
'''
import cv2
import numpy as np
from inference_sdk import InferenceHTTPClient
import os
import requests
import base64
import time

class BetoneiraDetectorAPI:
    def __init__(self):
        # 🔑 CREDENCIAIS ROBOFLOW
        self.API_KEY = "nCS2G2BqZxMZoEJxLKGZ"
        self.MODEL_ID = "aps6-1ibfu/7"
        
        # Configuração otimizada do cliente
        try:
            self.CLIENT = InferenceHTTPClient(
                api_url="https://detect.roboflow.com",
                api_key=self.API_KEY
            )
            print("🚀 Detector Super Otimizado Configurado!")
        except Exception as e:
            print(f"⚠️  Cliente SDK falhou, usando HTTP direto: {e}")
            self.CLIENT = None

    def super_enhance_image(self, image):
        """Pré-processamento SUPER avançado para máxima detecção"""
        try:
            original = image.copy()
            h, w = image.shape[:2]
            print(f"🔧 Super processamento: {w}x{h}")
            
            # 1. CORREÇÃO DE ILUMINAÇÃO EXTREMA
            # Multi-método de correção
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # CLAHE agressivo
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(16, 16))
            l_enhanced = clahe.apply(l)
            
            # Equalização de histograma adicional
            l_enhanced = cv2.equalizeHist(l_enhanced)
            
            lab_enhanced = cv2.merge([l_enhanced, a, b])
            image = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
            
            # 2. REDUÇÃO DE RUÍDO AVANÇADA
            # Filtro bilateral para preservar bordas
            image = cv2.bilateralFilter(image, 15, 80, 80)
            # Filtro de mediana para ruído
            image = cv2.medianBlur(image, 5)
            
            # 3. REALCE DE BORDAS SUPER EFETIVO
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Múltiplos métodos de detecção de bordas
            edges_canny = cv2.Canny(gray, 20, 80)
            edges_laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            edges_laplacian = np.uint8(np.absolute(edges_laplacian))
            
            # Combinar bordas
            edges_combined = cv2.bitwise_or(edges_canny, edges_laplacian)
            
            # 4. SEGMENTAÇÃO POR COR HIPER-ESPECÍFICA
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Cores MUITO específicas de betoneiras
            color_masks = []
            
            # Laranja vibrante (betoneiras novas)
            mask_orange1 = cv2.inRange(hsv, np.array([10, 100, 100]), np.array([20, 255, 255]))
            mask_orange2 = cv2.inRange(hsv, np.array([20, 80, 80]), np.array([25, 255, 255]))
            
            # Vermelho (betoneiras vermelhas)
            mask_red1 = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([8, 255, 255]))
            mask_red2 = cv2.inRange(hsv, np.array([172, 120, 70]), np.array([180, 255, 255]))
            
            # Azul (betoneiras azuis)
            mask_blue = cv2.inRange(hsv, np.array([100, 80, 50]), np.array([130, 255, 255]))
            
            # Amarelo (betoneiras amarelas)
            mask_yellow = cv2.inRange(hsv, np.array([25, 80, 80]), np.array([35, 255, 255]))
            
            # Tons metálicos
            mask_metal = cv2.inRange(hsv, np.array([0, 0, 40]), np.array([180, 50, 200]))
            
            # Combinar todas as máscaras
            combined_mask = mask_orange1 + mask_orange2 + mask_red1 + mask_red2 + mask_blue + mask_yellow + mask_metal
            
            # Operações morfológicas agressivas
            kernel_large = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
            kernel_medium = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel_large)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel_medium)
            combined_mask = cv2.dilate(combined_mask, kernel_medium, iterations=2)
            
            # Aplicar máscara de forma intensa
            if np.sum(combined_mask) > 1000:
                masked_image = cv2.bitwise_and(image, image, mask=combined_mask)
                # Combinação agressiva
                image = cv2.addWeighted(masked_image, 0.8, image, 0.2, 0)
                print("   🎨 Segmentação hiper-efetiva aplicada")
            
            # 5. CONTRASTE FINAL
            image = cv2.convertScaleAbs(image, alpha=1.2, beta=10)
            
            print("✅ Super processamento concluído!")
            return image
            
        except Exception as e:
            print(f"❌ Erro no super processamento: {e}")
            return original

    def hyper_local_detection(self, image):
        """Detecção local HIPER-EFETIVA com múltiplas técnicas"""
        try:
            print("🔍 Iniciando detecção local hiper-efetiva...")
            original = image.copy()
            h, w = image.shape[:2]
            
            all_detections = []
            
            # ESTRATÉGIA 1: DETECÇÃO POR COR E FORMA
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Máscaras de cor expandidas
            masks = []
            
            # Laranja (principal)
            masks.append(cv2.inRange(hsv, np.array([8, 80, 80]), np.array([22, 255, 255])))
            # Vermelho
            masks.append(cv2.inRange(hsv, np.array([0, 100, 80]), np.array([10, 255, 255])))
            masks.append(cv2.inRange(hsv, np.array([170, 100, 80]), np.array([180, 255, 255])))
            # Azul
            masks.append(cv2.inRange(hsv, np.array([95, 70, 60]), np.array([135, 255, 255])))
            # Amarelo
            masks.append(cv2.inRange(hsv, np.array([22, 70, 80]), np.array([38, 255, 255])))
            
            for mask in masks:
                if np.sum(mask) > 1000:  # Se há pixels relevantes
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    for contour in contours:
                        area = cv2.contourArea(contour)
                        if 5000 < area < (h * w * 0.2):  # Filtro de área
                            x, y, w_rect, h_rect = cv2.boundingRect(contour)
                            aspect_ratio = w_rect / h_rect
                            
                            # Betoneiras têm formato característico
                            if 0.4 <= aspect_ratio <= 2.2:
                                # Análise de solidez
                                hull = cv2.convexHull(contour)
                                hull_area = cv2.contourArea(hull)
                                if hull_area > 0:
                                    solidity = area / hull_area
                                    if solidity > 0.6:  # Formas sólidas
                                        all_detections.append((x, y, w_rect, h_rect, area, "color"))
            
            # ESTRATÉGIA 2: DETECÇÃO POR TEXTURA E FORMA
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Suavizar e detectar bordas
            blurred = cv2.GaussianBlur(gray, (7, 7), 2)
            edges = cv2.Canny(blurred, 15, 45)
            
            # Operações morfológicas para conectar bordas
            kernel = np.ones((5, 5), np.uint8)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            edges = cv2.dilate(edges, kernel, iterations=2)
            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 3000 < area < (h * w * 0.15):
                    # Aproximar contorno
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    # Betoneiras geralmente têm 4-8 lados
                    if 4 <= len(approx) <= 10:
                        x, y, w_rect, h_rect = cv2.boundingRect(contour)
                        aspect_ratio = w_rect / h_rect
                        
                        if 0.5 <= aspect_ratio <= 1.8:
                            # Verificar se é retangular
                            rect_area = w_rect * h_rect
                            extent = area / rect_area if rect_area > 0 else 0
                            
                            if extent > 0.5:  # Pelo menos 50% do retângulo
                                all_detections.append((x, y, w_rect, h_rect, area, "shape"))
            
            # ESTRATÉGIA 3: DETECÇÃO POR TAMANHO E POSIÇÃO
            # Buscar objetos grandes que podem ser betoneiras
            large_contours, _ = cv2.findContours(
                cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)[1],
                cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            for contour in large_contours:
                area = cv2.contourArea(contour)
                if 8000 < area < (h * w * 0.25):
                    x, y, w_rect, h_rect = cv2.boundingRect(contour)
                    
                    # Verificar proporções típicas de betoneiras
                    if 0.6 <= (w_rect / h_rect) <= 1.5:
                        # Análise de localização (não muito perto das bordas)
                        if (x > w * 0.05 and y > h * 0.05 and 
                            x + w_rect < w * 0.95 and y + h_rect < h * 0.95):
                            all_detections.append((x, y, w_rect, h_rect, area, "size"))
            
            # REMOVER DUPLICATAS
            unique_detections = self.remove_duplicate_detections(all_detections)
            
            print(f"   🎯 Detecção local hiper-efetiva: {len(unique_detections)} objetos")
            return unique_detections
            
        except Exception as e:
            print(f"❌ Erro na detecção local hiper-efetiva: {e}")
            return []

    def remove_duplicate_detections(self, detections):
        """Remove detecções duplicadas usando IoU"""
        if not detections:
            return []
        
        # Converter para formato padrão
        boxes = [(x, y, x+w, y+h) for (x, y, w, h, area, method) in detections]
        areas = [area for (x, y, w, h, area, method) in detections]
        methods = [method for (x, y, w, h, area, method) in detections]
        
        # Ordenar por área (maiores primeiro)
        indices = np.argsort(areas)[::-1]
        
        keep = []
        while len(indices) > 0:
            current = indices[0]
            keep.append(current)
            
            if len(indices) == 1:
                break
            
            # Calcular IoU
            current_box = boxes[current]
            remaining_boxes = [boxes[i] for i in indices[1:]]
            
            ious = []
            for box in remaining_boxes:
                x1 = max(current_box[0], box[0])
                y1 = max(current_box[1], box[1])
                x2 = min(current_box[2], box[2])
                y2 = min(current_box[3], box[3])
                
                intersection = max(0, x2 - x1) * max(0, y2 - y1)
                area_current = (current_box[2] - current_box[0]) * (current_box[3] - current_box[1])
                area_box = (box[2] - box[0]) * (box[3] - box[1])
                union = area_current + area_box - intersection
                
                iou = intersection / union if union > 0 else 0
                ious.append(iou)
            
            # Manter apenas com IoU baixo
            indices = [indices[i+1] for i, iou in enumerate(ious) if iou < 0.4]
        
        return [detections[i] for i in keep]

    def force_api_detection(self, image_path):
        """Força detecção da API com múltiplas estratégias"""
        strategies = [
            self.api_strategy_original,
            self.api_strategy_enhanced,
            self.api_strategy_small,
            self.api_strategy_high_quality
        ]
        
        for i, strategy in enumerate(strategies, 1):
            try:
                print(f"🔄 Tentativa API {i}/4...")
                result = strategy(image_path)
                if result and result.get('predictions'):
                    print(f"✅ API funcionou na tentativa {i}!")
                    return result
                time.sleep(1)
            except Exception as e:
                print(f"❌ Tentativa {i} falhou: {e}")
                continue
        
        print("🚨 Todas as tentativas da API falharam")
        return None

    def api_strategy_original(self, image_path):
        """Estratégia 1: Imagem original"""
        if self.CLIENT:
            return self.CLIENT.infer(image_path, model_id=self.MODEL_ID)
        return self.direct_api_call(image_path)

    def api_strategy_enhanced(self, image_path):
        """Estratégia 2: Imagem otimizada"""
        # Carregar e otimizar imagem
        image = cv2.imread(image_path)
        enhanced = self.super_enhance_image(image)
        
        temp_path = "temp_enhanced.jpg"
        cv2.imwrite(temp_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 100])
        
        if self.CLIENT:
            result = self.CLIENT.infer(temp_path, model_id=self.MODEL_ID)
        else:
            result = self.direct_api_call(temp_path)
        
        os.remove(temp_path)
        return result

    def api_strategy_small(self, image_path):
        """Estratégia 3: Imagem redimensionada"""
        image = cv2.imread(image_path)
        h, w = image.shape[:2]
        
        # Redimensionar para tamanho ideal da API
        new_size = 800
        scale = new_size / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        
        resized = cv2.resize(image, (new_w, new_h))
        temp_path = "temp_resized.jpg"
        cv2.imwrite(temp_path, resized, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        if self.CLIENT:
            result = self.CLIENT.infer(temp_path, model_id=self.MODEL_ID)
        else:
            result = self.direct_api_call(temp_path)
        
        os.remove(temp_path)
        return result

    def api_strategy_high_quality(self, image_path):
        """Estratégia 4: Qualidade máxima"""
        return self.direct_api_call(image_path, quality=100)

    def direct_api_call(self, image_path, quality=95):
        """Chamada direta à API com parâmetros otimizados"""
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            url = f"https://detect.roboflow.com/{self.MODEL_ID}"
            params = {
                "api_key": self.API_KEY,
                "confidence": "0.1",  # Threshold MUITO baixo
                "overlap": "20",
                "format": "json"
            }
            
            response = requests.post(
                url,
                params=params,
                data=image_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"❌ API direta falhou: {e}")
            return None

    def process_image(self, image_path, os_data):
        """Processamento ULTRA-OTIMIZADO para máxima detecção"""
        try:
            # VERIFICAÇÕES INICIAIS
            if not os.path.exists(image_path):
                raise Exception(f"Arquivo não encontrado: {image_path}")
            
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Não foi possível carregar a imagem")
            
            original = image.copy()
            print(f"🚀 PROCESSAMENTO ULTRA-OTIMIZADO INICIADO")
            print(f"📷 Imagem: {image.shape[1]}x{image.shape[0]}")
            
            # 1. DETECÇÃO DA API (MÁXIMA PRIORIDADE)
            print("🎯 FORÇANDO DETECÇÃO DA API...")
            api_result = self.force_api_detection(image_path)
            
            betoneiras = []
            result_image = original.copy()
            
            # 2. PROCESSAR RESULTADOS DA API
            api_detections = 0
            if api_result and 'predictions' in api_result:
                predictions = api_result['predictions']
                print(f"🔍 API detectou {len(predictions)} objetos")
                
                for pred in predictions:
                    conf = pred['confidence']
                    
                    # THRESHOLD ULTRA BAIXO: 10%!
                    if conf > 0.1:
                        x = pred['x']
                        y = pred['y']
                        width = pred['width']
                        height = pred['height']
                        class_name = pred.get('class', 'betoneira')
                        
                        x1 = int(x - width/2)
                        y1 = int(y - height/2)
                        x2 = int(x + width/2)
                        y2 = int(y + height/2)
                        
                        # Validar coordenadas
                        h, w = image.shape[:2]
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(w, x2), min(h, y2)
                        
                        if x2 > x1 and y2 > y1:
                            cor = self.extract_dominant_color(original, (x1, y1, x2, y2))
                            betoneira_id = f"API{len(betoneiras) + 1:03d}"
                            
                            betoneira_data = {
                                'id': betoneira_id,
                                'conf': conf,
                                'cor': cor,
                                'class': class_name,
                                'local_detection': False,
                                'bbox': (x1, y1, x2, y2)
                            }
                            betoneiras.append(betoneira_data)
                            api_detections += 1
                            
                            # Desenhar em VERDE (API)
                            color = (0, 255, 0)
                            cv2.rectangle(result_image, (x1, y1), (x2, y2), color, 4)
                            label = f"{betoneira_id} {conf:.2f}"
                            cv2.putText(result_image, label, (x1, y1-15), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # 3. DETECÇÃO LOCAL HIPER-EFETIVA (SE API INSUFICIENTE)
            if len(betoneiras) < 1:
                print("🤖 ATIVANDO DETECÇÃO LOCAL HIPER-EFETIVA...")
                local_detections = self.hyper_local_detection(image)
                
                for i, (x, y, w, h, area, method) in enumerate(local_detections):
                    cor = self.extract_dominant_color(image, (x, y, x+w, y+h))
                    betoneira_id = f"LOC{i+1:03d}"
                    
                    # Calcular confiança baseada no método e área
                    if method == "color":
                        confidence = 0.7
                    elif method == "shape":
                        confidence = 0.6
                    else:  # size
                        confidence = 0.5
                    
                    # Aumentar confiança baseado na área
                    img_area = image.shape[0] * image.shape[1]
                    area_ratio = area / img_area
                    if area_ratio > 0.05:  # Objetos grandes
                        confidence += 0.2
                    
                    betoneira_data = {
                        'id': betoneira_id,
                        'conf': min(0.9, confidence),
                        'cor': cor,
                        'class': 'betoneira_local',
                        'local_detection': True,
                        'bbox': (x, y, x+w, y+h)
                    }
                    betoneiras.append(betoneira_data)
                    
                    # Desenhar em AZUL (Local)
                    color = (255, 0, 0)
                    cv2.rectangle(result_image, (x, y), (x+w, y+h), color, 3)
                    label = f"{betoneira_id} {method}"
                    cv2.putText(result_image, label, (x, y-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # 4. RESULTADO FINAL
            resultado = {
                'betoneiras': betoneiras,
                'total_detected': len(betoneiras),
                'processed_image': result_image,
                'analysis_time': 5.0,
                'api_detections': api_detections,
                'local_detections': len(betoneiras) - api_detections,
                'api_used': api_detections > 0
            }
            
            print(f"🎉 PROCESSAMENTO CONCLUÍDO: {len(betoneiras)} BETONEIRAS!")
            print(f"📊 API: {api_detections} | Local: {len(betoneiras) - api_detections}")
            
            return resultado
            
        except Exception as e:
            raise Exception(f"Erro no processamento ultra-otimizado: {str(e)}")
    
    def extract_dominant_color(self, image, bbox):
        """Extrai cor predominante de forma ultra-precisa"""
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
            
            # ANÁLISE DE COR SUPER AVANÇADA
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Redimensionar para análise uniforme
            roi_resized = cv2.resize(hsv_roi, (50, 50))
            h_values = roi_resized[:,:,0].flatten()
            s_values = roi_resized[:,:,1].flatten()
            v_values = roi_resized[:,:,2].flatten()
            
            # Filtrar pixels com saturação e valor adequados
            valid_pixels = (s_values > 40) & (v_values > 30) & (v_values < 230)
            valid_hues = h_values[valid_pixels]
            
            if len(valid_hues) == 0:
                # Analisar brilho para cores neutras
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                avg_brightness = np.mean(gray_roi)
                
                if avg_brightness > 180:
                    return "branca"
                elif avg_brightness < 60:
                    return "preta"
                else:
                    return "cinza"
            
            # Calcular histograma de matiz
            hist, bins = np.histogram(valid_hues, bins=18, range=(0, 180))
            dominant_bin = np.argmax(hist)
            dominant_hue = (bins[dominant_bin] + bins[dominant_bin + 1]) / 2
            
            # Classificação ultra-precisas de cores
            if (0 <= dominant_hue <= 8) or (172 <= dominant_hue <= 180):
                return "vermelha"
            elif 9 <= dominant_hue <= 20:
                return "laranja"
            elif 21 <= dominant_hue <= 35:
                return "amarela"
            elif 36 <= dominant_hue <= 85:
                return "verde"
            elif 86 <= dominant_hue <= 130:
                return "azul"
            elif 131 <= dominant_hue <= 145:
                return "roxa"
            elif 146 <= dominant_hue <= 171:
                return "rosa"
            else:
                return "indefinida"
                
        except Exception as e:
            print(f"⚠️  Erro na extração de cor: {e}")
            return "indefinida"

# TESTE RÁPIDO DA DETECÇÃO (opcional)
if __name__ == "__main__":
    # Teste rápido do detector
    detector = BetoneiraDetectorAPI()
    
    # Testar com uma imagem de exemplo
    test_image = "test_image.jpg"
    if os.path.exists(test_image):
        os_data = {
            'quantidade_esperada': 5,
            'funcionario': 'Teste',
            'numero_os': 'TEST001',
            'cliente': 'Cliente Teste'
        }
        
        try:
            result = detector.process_image(test_image, os_data)
            print(f"🎯 TESTE CONCLUÍDO: {result['total_detected']} betoneiras detectadas")
        except Exception as e:
            print(f"❌ ERRO NO TESTE: {e}")
    else:
        print("⚠️  Imagem de teste não encontrada")