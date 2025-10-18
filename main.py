# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

def show_splash_screen():
    """Exibe uma tela de splash durante o carregamento"""
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(Qt.white)
    
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.show()
    
    # Mensagem de carregamento
    splash.showMessage(
        "🚀 Iniciando Sistema de Betoneiras...\n\n"
        "Carregando módulos...",
        Qt.AlignBottom | Qt.AlignCenter,
        Qt.black
    )
    
    return splash

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    required_packages = {
        'PyQt5': 'PyQt5',
        'opencv-python': 'cv2',
        'numpy': 'numpy',
        'requests': 'requests',
        'inference-sdk': 'inference_sdk',
        'scikit-learn': 'sklearn',
        'Pillow': 'PIL'
    }
    
    missing_packages = []
    
    for package, import_name in required_packages.items():
        try:
            if import_name == 'PyQt5':
                from PyQt5.QtWidgets import QWidget
            elif import_name == 'PIL':
                from PIL import Image
            else:
                __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def main():
    # ✅ 1. SEMPRE criar QApplication primeiro
    app = QApplication(sys.argv)
    
    # ✅ 2. Configurar estilo da aplicação
    app.setStyle('Fusion')
    
    # ✅ 3. Mostrar splash screen
    splash = show_splash_screen()
    app.processEvents()
    
    # ✅ 4. Verificar dependências
    splash.showMessage("🔍 Verificando dependências...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
    app.processEvents()
    
    missing_packages = check_dependencies()
    
    if missing_packages:
        splash.close()
        error_msg = (
            "❌ Dependências faltando!\n\n"
            "Os seguintes pacotes precisam ser instalados:\n"
            f"{', '.join(missing_packages)}\n\n"
            "Execute no terminal:\n"
            "pip install " + " ".join(missing_packages)
        )
        QMessageBox.critical(None, "Erro de Dependências", error_msg)
        return 1
    
    # ✅ 5. Configurar diretórios
    splash.showMessage("📁 Configurando diretórios...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
    app.processEvents()
    
    os.makedirs('models', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # ✅ 6. Importar e criar interface (com tratamento de erro)
    splash.showMessage("🎨 Carregando interface...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
    app.processEvents()
    
    try:
        from interface import MainWindow
        splash.showMessage("✅ Interface carregada!\nIniciando sistema...", Qt.AlignBottom | Qt.AlignCenter, Qt.black)
        app.processEvents()
        
        # Pequeno delay para mostrar a mensagem final
        QTimer.singleShot(1000, splash.close)
        
        window = MainWindow()
        
        # Centralizar janela na tela
        screen_geometry = app.primaryScreen().availableGeometry()
        window_geometry = window.frameGeometry()
        window.move(
            (screen_geometry.width() - window_geometry.width()) // 2,
            (screen_geometry.height() - window_geometry.height()) // 2
        )
        
        window.show()
        
        # Log de inicialização bem-sucedida
        print("=" * 60)
        print("🏗️  SISTEMA DE GESTÃO DE BETONEIRAS")
        print("=" * 60)
        print("✅ Sistema iniciado com sucesso!")
        print(f"📁 Diretórios configurados:")
        print(f"   • models/ - Modelos de IA")
        print(f"   • reports/ - Relatórios PDF") 
        print(f"   • temp/ - Arquivos temporários")
        print(f"   • logs/ - Logs do sistema")
        print("🔧 Módulos carregados:")
        print("   • Interface gráfica PyQt5")
        print("   • Visão computacional (OpenCV)")
        print("   • API Roboflow Inference SDK")
        print("   • Processamento de imagens")
        print("   • Geração de relatórios PDF")
        print("=" * 60)
        
        return app.exec_()
        
    except Exception as e:
        splash.close()
        error_details = f"""
❌ Erro crítico ao iniciar o sistema!

Detalhes do erro:
{str(e)}

Possíveis soluções:
1. Verifique se todas as dependências estão instaladas
2. Execute: pip install -r requirements.txt
3. Verifique os arquivos do projeto
4. Reinicie o sistema

Se o problema persistir, entre em contato com o suporte.
        """
        
        QMessageBox.critical(
            None, 
            "Erro Fatal - Sistema de Betoneiras",
            error_details
        )
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Sistema interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Erro não tratado: {e}")
        sys.exit(1)