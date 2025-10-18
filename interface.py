# interface.py - VERSÃO OTIMIZADA COM TELA CHEIA
import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTextEdit, 
                             QListWidget, QTabWidget, QFrame, QMessageBox,
                             QFileDialog, QProgressBar, QGroupBox, QFormLayout,
                             QScrollArea, QSplitter, QSizePolicy, QGridLayout,
                             QApplication, QDesktopWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon, QPalette, QColor
import cv2
import json
from datetime import datetime

# Importações condicionais para evitar erros
def import_detector():
    try:
        from detector_roboflow_api import BetoneiraDetectorAPI
        return BetoneiraDetectorAPI
    except ImportError as e:
        print(f"⚠️  Erro ao importar detector API: {e}")
        return None

def import_utils():
    try:
        from utils import generate_pdf_report
        return generate_pdf_report
    except ImportError as e:
        print(f"⚠️  Erro ao importar utils: {e}")
        return None

class DetectionThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, detector, image_path, os_data):
        super().__init__()
        self.detector = detector
        self.image_path = image_path
        self.os_data = os_data
    
    def run(self):
        try:
            self.progress.emit("🔄 Iniciando pré-processamento...")
            results = self.detector.process_image(self.image_path, self.os_data)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.os_data = {}
        self.current_results = None
        self.detector_class = import_detector()
        self.detector = None
        self.generate_pdf_report = import_utils()

        # NOVO: Sistema de histórico
        self.historico_processamentos = []
        self.total_processamentos = 0
        self.deteccoes_bem_sucedidas = 0
        self.inconsistencias = 0
        self.tempo_total_processamento = 0
        
        # CONFIGURAÇÃO DE TELA CHEIA
        self.setWindowTitle("🏗️ Sistema Inteligente de Gestão de Betoneiras")
        
        # Obter dimensões da tela
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        
        self.init_ui()
        self.init_detector()
        
    def showEvent(self, event):
        """Ajusta a interface quando a janela é mostrada"""
        super().showEvent(event)
        # Pequeno delay para garantir que a janela está totalmente carregada
        QTimer.singleShot(100, self.showMaximized)

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal com margens otimizadas para tela cheia
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Scroll area para tornar a interface responsiva
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget que contém as abas
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        
        # Layout do content widget
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Widget central com abas
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setDocumentMode(True)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #2c3e50;
                border-radius: 8px;
                background-color: #ecf0f1;
            }
            QTabBar::tab {
                background-color: #bdc3c7;
                color: #2c3e50;
                padding: 12px 24px;
                margin-right: 2px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #2980b9;
                color: white;
            }
        """)
        
        # Criar as abas
        self.setup_os_tab()
        self.setup_processing_tab()
        self.setup_dashboard_tab()
        
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(scroll_area)
        
        # Barra de status
        self.statusBar().showMessage("Sistema pronto - Aguardando cadastro de O.S.")
        
    def init_detector(self):
        """Inicializa o detector de betoneiras"""
        try:
            if self.detector_class:
                self.detector = self.detector_class()
                print("✅ Detector inicializado com sucesso")
            else:
                print("⚠️  Detector não disponível - modo de demonstração")
        except Exception as e:
            print(f"❌ Erro ao inicializar detector: {e}")
            # Criar detector mock para demonstração
            self.detector = self.create_mock_detector()
    
    def create_mock_detector(self):
        """Cria um detector mock para demonstração quando o real não está disponível"""
        class MockDetector:
            def process_image(self, image_path, os_data):
                # Simular processamento
                import random
                expected = os_data.get('quantidade_esperada', 5)
                detected = random.randint(max(1, expected-2), expected+1)
                
                # Carregar imagem para demonstração
                image = cv2.imread(image_path)
                if image is not None:
                    # Adicionar anotações simuladas
                    h, w = image.shape[:2]
                    for i in range(detected):
                        x = random.randint(50, w-150)
                        y = random.randint(50, h-150)
                        cv2.rectangle(image, (x, y), (x+100, y+100), (0, 255, 0), 3)
                        cv2.putText(image, f'Betoneira {i+1}', (x, y-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                return {
                    'total_detected': detected,
                    'betoneiras': [
                        {
                            'id': i+1,
                            'conf': round(random.uniform(0.7, 0.95), 2),
                            'cor': random.choice(['Azul', 'Vermelho', 'Amarelo', 'Verde']),
                            'local_detection': random.choice([True, False])
                        } for i in range(detected)
                    ],
                    'processed_image': image,
                    'analysis_time': round(random.uniform(1.5, 3.5), 2)
                }
        
        return MockDetector()
    
    def setup_os_tab(self):
        tab_os = QWidget()
        layout = QVBoxLayout(tab_os)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Cabeçalho
        header = QLabel("📋 Cadastro de Ordem de Serviço")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2c3e50);
                border-radius: 12px;
                color: white;
            }
        """)
        
        # Container principal
        main_container = QWidget()
        main_container.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        container_layout = QVBoxLayout(main_container)
        
        # Grupo de dados da O.S.
        group_os = QGroupBox("🔧 Dados da Ordem de Serviço")
        group_os.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 12px 0 12px;
                color: #2980b9;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
        """)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Campos de entrada
        self.funcionario_input = QLineEdit()
        self.funcionario_input.setPlaceholderText("👤 Digite o nome completo do funcionário")
        self.funcionario_input.setMinimumHeight(35)
        
        self.os_input = QLineEdit()
        self.os_input.setPlaceholderText("📄 Número da ordem de serviço")
        self.os_input.setMinimumHeight(35)
        
        self.cliente_input = QLineEdit()
        self.cliente_input.setPlaceholderText("🏢 Nome do cliente/empresa")
        self.cliente_input.setMinimumHeight(35)
        
        self.quantidade_input = QLineEdit()
        self.quantidade_input.setPlaceholderText("🔢 Quantidade total de betoneiras alugadas")
        self.quantidade_input.setMinimumHeight(35)
        
        # Estilizar campos
        input_style = """
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 13px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f0f8ff;
            }
            QLineEdit:hover {
                border: 2px solid #3498db;
            }
        """
        
        for input_field in [self.funcionario_input, self.os_input, self.cliente_input, self.quantidade_input]:
            input_field.setStyleSheet(input_style)
        
        form_layout.addRow("👤 Nome do Funcionário:", self.funcionario_input)
        form_layout.addRow("📄 Número da O.S.:", self.os_input)
        form_layout.addRow("🏢 Cliente:", self.cliente_input)
        form_layout.addRow("🔢 Quantidade de Betoneiras:", self.quantidade_input)
        
        group_os.setLayout(form_layout)
        
        # Botão próximo
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.addStretch()
        
        btn_proximo = QPushButton("🎯 Iniciar Processamento →")
        btn_proximo.clicked.connect(self.validar_os)
        btn_proximo.setMinimumSize(180, 50)
        btn_proximo.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                margin: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #219a52, stop:1 #27ae60);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e8449, stop:1 #219a52);
            }
        """)
        
        btn_layout.addWidget(btn_proximo)
        btn_layout.addStretch()
        
        # Informações do sistema
        info_group = QGroupBox("ℹ️ Informações do Sistema")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #95a5a6;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                color: #7f8c8d;
            }
        """)
        
        info_layout = QVBoxLayout()
        info_text = QLabel(
            "💡 <b>Como usar:</b><br>"
            "1. Preencha todos os dados da O.S.<br>"
            "2. Clique em 'Iniciar Processamento'<br>"
            "3. Na próxima tela, selecione a imagem<br>"
            "4. Aguarde a detecção automática<br>"
            "5. Revise os resultados e gere o relatório"
        )
        info_text.setStyleSheet("color: #2c3e50; font-size: 12px; padding: 8px;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        
        # Montar layout
        container_layout.addWidget(group_os)
        container_layout.addSpacing(15)
        container_layout.addWidget(info_group)
        container_layout.addStretch()
        container_layout.addWidget(btn_container)
        
        layout.addWidget(header)
        layout.addWidget(main_container)
        
        self.tabs.addTab(tab_os, "📋 Cadastro O.S.")
    
    def setup_processing_tab(self):
        tab_process = QScrollArea()
        tab_process.setWidgetResizable(True)
        
        content_widget = QWidget()
        tab_process.setWidget(content_widget)
        
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Cabeçalho
        header = QLabel("🔍 Processamento de Imagens")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: white;
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e67e22, stop:1 #d35400);
                border-radius: 8px;
            }
        """)
        
        # Container principal com splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        
        # Left panel - Upload e controle
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        
        # Upload da imagem
        upload_group = QGroupBox("📁 Upload da Imagem")
        upload_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e67e22;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: #fef9e7;
            }
            QGroupBox::title {
                color: #d35400;
            }
        """)
        
        upload_layout = QVBoxLayout()
        
        self.btn_upload = QPushButton("📸 Selecionar Imagem")
        self.btn_upload.clicked.connect(self.upload_image)
        self.btn_upload.setMinimumHeight(45)
        self.btn_upload.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e67e22, stop:1 #f39c12);
                color: white;
                border: none;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                margin: 4px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #d35400, stop:1 #e67e22);
            }
        """)
        
        self.image_path_label = QLabel("Nenhuma imagem selecionada")
        self.image_path_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d; 
                font-style: italic;
                padding: 6px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border: 1px dashed #bdc3c7;
                font-size: 11px;
            }
        """)
        self.image_path_label.setWordWrap(True)
        
        upload_layout.addWidget(self.btn_upload)
        upload_layout.addWidget(self.image_path_label)
        upload_group.setLayout(upload_layout)
        
        # Botão de detecção
        self.btn_detect = QPushButton("🤖 Detectar Betoneiras (IA)")
        self.btn_detect.clicked.connect(self.detect_betoneiras)
        self.btn_detect.setEnabled(False)
        self.btn_detect.setMinimumHeight(50)
        self.btn_detect.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 8px;
            }
            QPushButton:hover:enabled {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2980b9, stop:1 #2471a3);
            }
            QPushButton:pressed:enabled {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2471a3, stop:1 #1f618d);
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(18)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                text-align: center;
                height: 20px;
                font-weight: bold;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b59b6, stop:1 #8e44ad);
                border-radius: 6px;
            }
        """)
        
        # Status do processamento
        self.status_label = QLabel("🟡 Aguardando upload da imagem...")
        self.status_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 12px;
                border-radius: 6px;
                background-color: #fff3cd;
                border: 2px solid #ffeaa7;
                color: #856404;
                font-size: 11px;
            }
        """)
        self.status_label.setWordWrap(True)
        
        left_layout.addWidget(upload_group)
        left_layout.addWidget(self.btn_detect)
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()
        
        # Right panel - Resultados
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)
        
        # Área de resultados
        results_group = QGroupBox("📊 Resultados da Detecção")
        results_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                color: #8e44ad;
            }
        """)
        
        results_layout = QVBoxLayout()
        results_layout.setSpacing(8)
        
        # Splitter para imagens
        image_splitter = QSplitter(Qt.Horizontal)
        image_splitter.setChildrenCollapsible(False)
        
        # Imagem original
        orig_group = QGroupBox("🖼️ Imagem Original")
        orig_layout = QVBoxLayout()
        self.original_image_label = QLabel()
        self.original_image_label.setAlignment(Qt.AlignCenter)
        self.original_image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 6px;
                padding: 12px;
                background-color: #f8f9fa;
                min-height: 250px;
                font-size: 12px;
                color: #7f8c8d;
            }
        """)
        self.original_image_label.setText("Imagem será exibida aqui\n\n📁 Clique em 'Selecionar Imagem'")
        self.original_image_label.setScaledContents(False)
        orig_layout.addWidget(self.original_image_label)
        orig_group.setLayout(orig_layout)
        
        # Imagem processada
        proc_group = QGroupBox("🎯 Imagem Processada")
        proc_layout = QVBoxLayout()
        self.processed_image_label = QLabel()
        self.processed_image_label.setAlignment(Qt.AlignCenter)
        self.processed_image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 6px;
                padding: 12px;
                background-color: #f8f9fa;
                min-height: 250px;
                font-size: 12px;
                color: #7f8c8d;
            }
        """)
        self.processed_image_label.setText("Resultados aparecerão aqui\n\n🤖 Após a detecção por IA")
        self.processed_image_label.setScaledContents(False)
        proc_layout.addWidget(self.processed_image_label)
        proc_group.setLayout(proc_layout)
        
        image_splitter.addWidget(orig_group)
        image_splitter.addWidget(proc_group)
        image_splitter.setSizes([300, 300])
        
        # Estatísticas
        stats_group = QGroupBox("📈 Estatísticas")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                color: #219a52;
            }
        """)
        
        stats_layout = QGridLayout()
        
        self.count_label = QLabel("Betoneiras detectadas: 0")
        self.count_label.setStyleSheet("font-size: 12px; font-weight: bold; padding: 6px;")
        
        self.comparison_label = QLabel("Comparação: -")
        self.comparison_label.setStyleSheet("font-size: 12px; padding: 6px;")
        
        self.accuracy_label = QLabel("Precisão: -")
        self.accuracy_label.setStyleSheet("font-size: 12px; padding: 6px;")
        
        self.time_label = QLabel("Tempo de processamento: -")
        self.time_label.setStyleSheet("font-size: 12px; padding: 6px;")
        
        stats_layout.addWidget(self.count_label, 0, 0)
        stats_layout.addWidget(self.comparison_label, 0, 1)
        stats_layout.addWidget(self.accuracy_label, 1, 0)
        stats_layout.addWidget(self.time_label, 1, 1)
        
        stats_group.setLayout(stats_layout)
        
        # Lista de betoneiras
        list_group = QGroupBox("📋 Betoneiras Detectadas")
        list_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                color: #2980b9;
            }
        """)
        
        list_layout = QVBoxLayout()
        self.betoneiras_list = QListWidget()
        self.betoneiras_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 6px;
                min-height: 150px;
                font-size: 11px;
                background-color: white;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        list_layout.addWidget(self.betoneiras_list)
        list_group.setLayout(list_layout)
        
        # Botão gerar PDF
        self.btn_pdf = QPushButton("📄 Gerar Relatório PDF Completo")
        self.btn_pdf.clicked.connect(self.gerar_relatorio_pdf)
        self.btn_pdf.setEnabled(False)
        self.btn_pdf.setMinimumHeight(40)
        self.btn_pdf.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b59b6, stop:1 #8e44ad);
                color: white;
                border: none;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                margin: 4px;
            }
            QPushButton:hover:enabled {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8e44ad, stop:1 #7d3c98);
            }
            QPushButton:disabled {
                background-color: #d7bde2;
                color: #7f8c8d;
            }
        """)
        
        results_layout.addWidget(image_splitter)
        results_layout.addWidget(stats_group)
        results_layout.addWidget(list_group)
        results_layout.addWidget(self.btn_pdf)
        
        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group)
        
        # Adicionar painéis ao splitter principal
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([280, 520])
        
        layout.addWidget(header)
        layout.addWidget(main_splitter)
        
        self.tabs.addTab(tab_process, "🔍 Processamento")
    
    def setup_dashboard_tab(self):
        tab_dashboard = QWidget()
        layout = QVBoxLayout(tab_dashboard)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("📊 Dashboard e Relatórios")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: white;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-radius: 12px;
            }
        """)
        
        # Container de métricas COM ID
        metrics_container = QWidget()
        metrics_container.setObjectName("metrics_container")  # IMPORTANTE: Adicionar ID
        metrics_layout = QHBoxLayout(metrics_container)
        metrics_layout.setSpacing(10)
        
        # Métricas iniciais
        metrics = [
            ("📈 Total Processado", "0", "#3498db"),
            ("✅ Detecções Bem-sucedidas", "0", "#27ae60"), 
            ("⚠️ Inconsistências", "0", "#e74c3c"),
            ("⏱️ Tempo Médio", "0s", "#f39c12")
        ]
        
        for title, value, color in metrics:
            metric_widget = QWidget()
            metric_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {color};
                    border-radius: 8px;
                    padding: 12px;
                    min-width: 120px;
                }}
            """)
            metric_layout = QVBoxLayout(metric_widget)
            
            title_label = QLabel(title)
            title_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setWordWrap(True)
            
            value_label = QLabel(value)
            value_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
            value_label.setAlignment(Qt.AlignCenter)
            
            metric_layout.addWidget(title_label)
            metric_layout.addWidget(value_label)
            metrics_layout.addWidget(metric_widget)
        
        # Área de histórico COM ID
        history_group = QGroupBox("📋 Histórico de Processamentos")
        history_group.setObjectName("history_group")  # IMPORTANTE: Adicionar ID
        history_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                color: #2c3e50;
            }
        """)
        
        history_layout = QVBoxLayout()
        
        # Mensagem inicial
        initial_text = QLabel("Nenhum processamento realizado ainda.\n\nRealize a primeira detecção para ver estatísticas aqui.")
        initial_text.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 20px; text-align: center;")
        initial_text.setAlignment(Qt.AlignCenter)
        history_layout.addWidget(initial_text)
        
        history_group.setLayout(history_layout)
        
        layout.addWidget(header)
        layout.addWidget(metrics_container)
        layout.addWidget(history_group)
        layout.addStretch()
        
        self.tabs.addTab(tab_dashboard, "📊 Dashboard")

    def exportar_historico(self):
        """Exporta o histórico para CSV"""
        try:
            if not self.historico_processamentos:
                QMessageBox.information(self, "Exportar", "Nenhum dado disponível para exportar.")
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Exportar Histórico", "historico_betoneiras.csv", "CSV Files (*.csv)"
            )
            
            if file_path:
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['timestamp', 'os_number', 'cliente', 'funcionario', 'esperado', 'detectado', 'status', 'tempo_processamento']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for registro in self.historico_processamentos:
                        writer.writerow(registro)
                        
                QMessageBox.information(self, "Sucesso", f"Histórico exportado:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao exportar histórico:\n{str(e)}")

    def validar_os(self):
        """Valida e processa os dados da Ordem de Serviço"""
        if not all([
            self.funcionario_input.text().strip(),
            self.os_input.text().strip(),
            self.cliente_input.text().strip(),
            self.quantidade_input.text().strip()
        ]):
            QMessageBox.warning(self, "Aviso", "❌ Preencha todos os campos!")
            return
            
        try:
            quantidade = int(self.quantidade_input.text())
            if quantidade <= 0:
                QMessageBox.warning(self, "Aviso", "❌ Quantidade deve ser maior que zero!")
                return
        except ValueError:
            QMessageBox.warning(self, "Aviso", "❌ Quantidade deve ser um número válido!")
            return
            
        self.os_data = {
            'funcionario': self.funcionario_input.text().strip(),
            'numero_os': self.os_input.text().strip(),
            'cliente': self.cliente_input.text().strip(),
            'quantidade_esperada': quantidade,
            'data_cadastro': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        self.tabs.setCurrentIndex(1)
        self.statusBar().showMessage(f"O.S. {self.os_data['numero_os']} cadastrada - Aguardando imagem...")
        QMessageBox.information(self, "Sucesso", "✅ O.S. cadastrada com sucesso!\n\nAgora selecione uma imagem para processar.")

    def upload_image(self):
        """Faz upload da imagem para processamento"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Selecionar Imagem", 
            "", 
            "Imagens (*.jpg *.jpeg *.png *.bmp *.tiff)"
        )
        
        if file_path:
            self.image_path = file_path
            filename = os.path.basename(file_path)
            self.image_path_label.setText(f"📷 Imagem: {filename}\n📍 {file_path}")
            self.btn_detect.setEnabled(True)
            self.status_label.setText("🟢 Imagem carregada - Pronto para detecção")
            self.status_label.setStyleSheet("background-color: #d4edda; border: 2px solid #c3e6cb; color: #155724;")
            
            # Exibir imagem original
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Redimensionar mantendo aspect ratio
                pixmap = pixmap.scaled(300, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.original_image_label.setPixmap(pixmap)
                self.original_image_label.setText("")
            else:
                self.original_image_label.setText("❌ Erro ao carregar imagem")

    def detect_betoneiras(self):
        """Executa a detecção de betoneiras na imagem"""
        if not hasattr(self, 'image_path'):
            QMessageBox.warning(self, "Aviso", "❌ Selecione uma imagem primeiro!")
            return
            
        if not self.detector:
            QMessageBox.warning(self, "Aviso", "❌ Detector não disponível!")
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.btn_detect.setEnabled(False)
        self.btn_pdf.setEnabled(False)
        self.status_label.setText("🔄 Processando imagem...\n• Pré-processamento\n• Detecção por IA\n• Análise de cores")
        self.status_label.setStyleSheet("background-color: #fff3cd; border: 2px solid #ffeaa7; color: #856404;")
        
        self.detection_thread = DetectionThread(self.detector, self.image_path, self.os_data)
        self.detection_thread.finished.connect(self.on_detection_finished)
        self.detection_thread.error.connect(self.on_detection_error)
        self.detection_thread.progress.connect(self.on_detection_progress)
        self.detection_thread.start()

    def on_detection_progress(self, message):
        """Atualiza o status durante o processamento"""
        self.status_label.setText(message)

    def on_detection_finished(self, results):
        """Processa os resultados da detecção e atualiza histórico"""
        self.progress_bar.setVisible(False)
        self.btn_detect.setEnabled(True)
        self.current_results = results
        
        # Exibir imagem processada
        processed_image = results.get('processed_image')
        if processed_image is not None:
            rgb_image = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            pixmap = pixmap.scaled(300, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.processed_image_label.setPixmap(pixmap)
            self.processed_image_label.setText("")
        
        # Dados para estatísticas
        detected_count = results.get('total_detected', 0)
        expected_count = self.os_data.get('quantidade_esperada', 0)
        analysis_time = results.get('analysis_time', 0)
        status = "SUCESSO" if detected_count == expected_count else "INCONSISTENTE"
        
        # NOVO: Salvar no histórico
        registro_historico = {
            'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'os_number': self.os_data.get('numero_os', 'N/A'),
            'cliente': self.os_data.get('cliente', 'N/A'),
            'funcionario': self.os_data.get('funcionario', 'N/A'),
            'esperado': expected_count,
            'detectado': detected_count,
            'status': status,
            'tempo_processamento': analysis_time,
            'imagem_path': getattr(self, 'image_path', 'N/A')
        }
        
        self.historico_processamentos.append(registro_historico)
        self.total_processamentos += 1
        
        if status == "SUCESSO":
            self.deteccoes_bem_sucedidas += 1
        else:
            self.inconsistencias += 1
            
        self.tempo_total_processamento += analysis_time
        
        # Atualizar estatísticas na aba de processamento
        self.count_label.setText(f"Betoneiras detectadas: {detected_count}")
        self.comparison_label.setText(f"Comparação: {detected_count} detectadas / {expected_count} esperadas")
        self.time_label.setText(f"Tempo de processamento: {analysis_time}s")
        
        # Calcular precisão
        if expected_count > 0:
            accuracy = min(100, (detected_count / expected_count) * 100)
            self.accuracy_label.setText(f"Precisão: {accuracy:.1f}%")
        
        # Status baseado na comparação
        if detected_count == expected_count:
            self.status_label.setText("🟢 STATUS: OK - Quantidade correta")
            self.status_label.setStyleSheet("background-color: #d4edda; border: 2px solid #c3e6cb; color: #155724;")
        else:
            self.status_label.setText("🔴 STATUS: INCONSISTENTE - Quantidade incorreta")
            self.status_label.setStyleSheet("background-color: #f8d7da; border: 2px solid #f5c6cb; color: #721c24;")
        
        # Listar betoneiras detectadas
        self.betoneiras_list.clear()
        betoneiras = results.get('betoneiras', [])
        for betoneira in betoneiras:
            detection_type = " [LOCAL]" if betoneira.get('local_detection', False) else ""
            item_text = (f"{betoneira['id']} - Conf: {betoneira['conf']:.2f} - "
                        f"Cor: {betoneira['cor']}{detection_type}")
            self.betoneiras_list.addItem(item_text)
            
        self.btn_pdf.setEnabled(True)
        self.statusBar().showMessage(f"Processamento concluído: {detected_count} betoneiras detectadas")
        
        # NOVO: Atualizar dashboard automaticamente
        self.atualizar_dashboard()
        
        # NOVO: Mostrar mensagem de sucesso com link para dashboard
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Processamento Concluído")
        msg.setText(f"✅ Detecção concluída com sucesso!\n\n"
                    f"• {detected_count} betoneiras detectadas\n"
                    f"• {expected_count} betoneiras esperadas\n"
                    f"• Status: {status}\n\n"
                    f"Clique em '📊 Dashboard' para ver estatísticas detalhadas.")
        msg.addButton("Continuar", QMessageBox.AcceptRole)
        dashboard_btn = msg.addButton("Ir para Dashboard", QMessageBox.ActionRole)
        msg.exec_()
        
        if msg.clickedButton() == dashboard_btn:
            self.tabs.setCurrentIndex(2)  # Vai para a dashboard



    def atualizar_dashboard(self):
        """Atualiza a dashboard com estatísticas em tempo real"""
        try:
            # Atualizar métricas principais
            tempo_medio = self.tempo_total_processamento / max(1, self.total_processamentos)
            
            # Encontrar os widgets de métricas
            metrics_container = self.findChild(QWidget, "metrics_container")
            if not metrics_container:
                return
                
            # Atualizar valores das métricas
            metrics = [
                ("📈 Total Processado", str(self.total_processamentos), "#3498db"),
                ("✅ Detecções Bem-sucedidas", str(self.deteccoes_bem_sucedidas), "#27ae60"), 
                ("⚠️ Inconsistências", str(self.inconsistencias), "#e74c3c"),
                ("⏱️ Tempo Médio", f"{tempo_medio:.1f}s", "#f39c12")
            ]
            
            # Limpar container existente
            for i in reversed(range(metrics_container.layout().count())):
                widget = metrics_container.layout().itemAt(i).widget()
                if widget:
                    widget.deleteLater()
            
            # Recriar métricas atualizadas
            for title, value, color in metrics:
                metric_widget = QWidget()
                metric_widget.setStyleSheet(f"""
                    QWidget {{
                        background-color: {color};
                        border-radius: 8px;
                        padding: 12px;
                        min-width: 120px;
                    }}
                """)
                metric_layout = QVBoxLayout(metric_widget)
                
                title_label = QLabel(title)
                title_label.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
                title_label.setAlignment(Qt.AlignCenter)
                title_label.setWordWrap(True)
                
                value_label = QLabel(value)
                value_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
                value_label.setAlignment(Qt.AlignCenter)
                
                metric_layout.addWidget(title_label)
                metric_layout.addWidget(value_label)
                metrics_container.layout().addWidget(metric_widget)
            
            # Atualizar histórico na interface
            self.atualizar_historico_interface()

        except Exception as e:
            print(f"⚠️ Erro ao atualizar dashboard: {e}")


    def atualizar_historico_interface(self):
        """Atualiza a exibição do histórico na dashboard"""
        try:
            # Encontrar o widget de histórico
            history_widget = self.findChild(QGroupBox, "history_group")
            if not history_widget:
                return
                
            # Limpar layout existente
            for i in reversed(range(history_widget.layout().count())):
                item = history_widget.layout().itemAt(i)
                if item.widget():
                    item.widget().deleteLater()
            
            # Criar scroll area para histórico
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setMaximumHeight(300)
            scroll_area.setStyleSheet("border: none;")
            
            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setSpacing(8)
            
            # Adicionar título
            title_label = QLabel("📋 Últimos Processamentos")
            title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
            scroll_layout.addWidget(title_label)
            
            # Adicionar itens do histórico (últimos 10)
            historico_recente = self.historico_processamentos[-10:]  # Últimos 10 registros
            
            if not historico_recente:
                empty_label = QLabel("Nenhum processamento realizado ainda.")
                empty_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 10px;")
                scroll_layout.addWidget(empty_label)
            else:
                for registro in reversed(historico_recente):  # Mais recentes primeiro
                    historico_item = self.criar_widget_historico(registro)
                    scroll_layout.addWidget(historico_item)
            
            scroll_layout.addStretch()
            scroll_area.setWidget(scroll_content)
            history_widget.layout().addWidget(scroll_area)
            
        except Exception as e:
            print(f"⚠️ Erro ao atualizar histórico: {e}")


    def criar_widget_historico(self, registro):
        """Cria um widget individual para cada item do histórico"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        
        # Linha 1: O.S. e Status
        linha1 = QHBoxLayout()
        
        os_label = QLabel(f"📄 O.S.: {registro['os_number']}")
        os_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        
        status_label = QLabel(registro['status'])
        status_style = "color: #27ae60;" if registro['status'] == "SUCESSO" else "color: #e74c3c;"
        status_label.setStyleSheet(f"font-weight: bold; {status_style}")
        
        linha1.addWidget(os_label)
        linha1.addStretch()
        linha1.addWidget(status_label)
        
        # Linha 2: Cliente e Funcionário
        linha2 = QHBoxLayout()
        
        cliente_label = QLabel(f"🏢 {registro['cliente']}")
        cliente_label.setStyleSheet("color: #34495e; font-size: 11px;")
        
        func_label = QLabel(f"👤 {registro['funcionario']}")
        func_label.setStyleSheet("color: #34495e; font-size: 11px;")
        
        linha2.addWidget(cliente_label)
        linha2.addStretch()
        linha2.addWidget(func_label)
        
        # Linha 3: Estatísticas
        linha3 = QHBoxLayout()
        
        stats_label = QLabel(f"🎯 {registro['detectado']}/{registro['esperado']} betoneiras")
        stats_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        
        time_label = QLabel(f"⏱️ {registro['tempo_processamento']}s")
        time_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        
        date_label = QLabel(f"📅 {registro['timestamp']}")
        date_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        
        linha3.addWidget(stats_label)
        linha3.addWidget(time_label)
        linha3.addStretch()
        linha3.addWidget(date_label)
        
        layout.addLayout(linha1)
        layout.addLayout(linha2)
        layout.addLayout(linha3)
        
        return widget

    def on_detection_error(self, error_msg):
        """Trata erros durante a detecção"""
        self.progress_bar.setVisible(False)
        self.btn_detect.setEnabled(True)
        self.status_label.setText(f"❌ Erro na detecção: {error_msg}")
        self.status_label.setStyleSheet("background-color: #f8d7da; border: 2px solid #f5c6cb; color: #721c24;")
        QMessageBox.critical(self, "Erro", f"Falha na detecção:\n{error_msg}")

    def gerar_relatorio_pdf(self):
        """Gera relatório PDF com os resultados"""
        if not self.current_results:
            QMessageBox.warning(self, "Aviso", "❌ Nenhum resultado disponível para gerar relatório!")
            return
            
        try:
            if self.generate_pdf_report:
                # Usar a função importada
                pdf_path = self.generate_pdf_report(self.current_results, self.os_data)
                QMessageBox.information(self, "Sucesso", f"✅ Relatório PDF gerado:\n{pdf_path}")
            else:
                # Modo de demonstração
                pdf_path = f"relatorio_{self.os_data['numero_os']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                QMessageBox.information(self, "Demo", f"📄 Relatório demo criado:\n{pdf_path}\n\n(Modo demonstração - função PDF não disponível)")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"❌ Falha ao gerar PDF:\n{str(e)}")

# Função principal para executar a aplicação
def main():
    try:
        app = QApplication(sys.argv)
        
        # Configurar estilo da aplicação
        app.setStyle('Fusion')
        
        # Configurar High DPI scaling para telas 4K
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        window = MainWindow()
        window.show()
        
        print("✅ Sistema iniciado com sucesso!")
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Erro crítico ao iniciar sistema: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())