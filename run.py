#!/usr/bin/env python3
"""
워터펌프 온도 모니터링 시스템 실행 스크립트
사용법: python run.py [옵션]
"""

import argparse
import subprocess
import sys
import os
import webbrowser
import time

def run_analyzer():
    """분석 엔진만 실행 (JSON 파일 생성)"""
    print("🔧 워터펌프 분석 엔진 실행 중...")
    try:
        subprocess.run([sys.executable, "water_pump_analyzer.py"], check=True)
        print("✅ 분석 완료! JSON 파일이 water_pump_data 폴더에 생성되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ 분석 중 오류 발생: {e}")
    except FileNotFoundError:
        print("❌ water_pump_analyzer.py 파일을 찾을 수 없습니다.")

def run_dashboard():
    """대시보드 실행"""
    print("📊 대시보드 실행 중...")
    print("🌐 브라우저에서 http://localhost:8501 에 접속하세요")
    
    try:
        # 잠시 후 브라우저 자동 열기
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:8501')
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_dashboard.py",
            "--server.headless", "true",
            "--server.address", "0.0.0.0"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 대시보드 실행 중 오류 발생: {e}")
    except FileNotFoundError:
        print("❌ streamlit_dashboard.py 파일을 찾을 수 없습니다.")
    except KeyboardInterrupt:
        print("\n✋ 대시보드를 종료합니다.")

def run_llm_chatbot():
    """LLM 기반 AI 챗봇 실행"""
    print("🤖 LLM 기반 AI 챗봇 실행 중...")
    print("🌐 브라우저에서 http://localhost:8501 에 접속하세요")
    print("💡 OpenAI GPT 또는 Local Ollama 모델을 선택할 수 있습니다")
    
    try:
        # 잠시 후 브라우저 자동 열기
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:8501')
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "chatbot_implementation_openai.py",
            "--server.headless", "true",
            "--server.address", "0.0.0.0"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ LLM 챗봇 실행 중 오류 발생: {e}")
    except FileNotFoundError:
        print("❌ chatbot_implementation_openai.py 파일을 찾을 수 없습니다.")
    except KeyboardInterrupt:
        print("\n✋ LLM 챗봇을 종료합니다.")

def run_chatbot():
    """AI 챗봇 실행 (기본값)"""
    print("🤖 AI 챗봇 실행 중...")
    print("🌐 브라우저에서 http://localhost:8501 에 접속하세요")
    
    try:
        # 잠시 후 브라우저 자동 열기
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:8501')
        
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "chatbot_implementation.py",
            "--server.headless", "true",
            "--server.address", "0.0.0.0"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 챗봇 실행 중 오류 발생: {e}")
    except FileNotFoundError:
        print("❌ chatbot_implementation.py 파일을 찾을 수 없습니다.")
    except KeyboardInterrupt:
        print("\n✋ 챗봇을 종료합니다.")

def check_dependencies():
    """필요한 패키지가 설치되어 있는지 확인"""
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 다음 패키지가 설치되지 않았습니다:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 다음 명령어로 설치하세요:")
        print(f"pip install {' '.join(missing_packages)}")
        print("\n또는 requirements.txt 사용:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_files():
    """필요한 파일들이 존재하는지 확인"""
    required_files = [
        'water_pump_analyzer.py',
        'streamlit_dashboard.py', 
        'chatbot_implementation.py',
        'chatbot_implementation_openai.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ 다음 파일이 누락되었습니다:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def show_help():
    """도움말 표시"""
    help_text = """
🌡️ 워터펌프 온도 모니터링 시스템

사용법:
  python run.py [옵션]

옵션:
  --chatbot     기본 AI 챗봇 실행
  --llm-chatbot LLM 기반 AI 챗봇 실행 (OpenAI/Ollama)
  --dashboard   시각화 대시보드 실행
  --analyzer    분석 엔진만 실행 (JSON 생성)
  --check       시스템 환경 점검
  --help        이 도움말 표시

예시:
  python run.py                      # 기본 AI 챗봇 실행
  python run.py --llm-chatbot        # LLM 챗봇 실행 (권장)
  python run.py --dashboard          # 대시보드 실행
  python run.py --analyzer           # 분석만 실행
  python run.py --check              # 환경 점검

🤖 LLM 챗봇 기능:
  - OpenAI GPT-3.5-turbo 지원
  - Local Ollama 모델 지원  
  - JSON 데이터 기반 정확한 분석
  - 자연어 질문으로 상세한 인사이트 제공

브라우저 접속: http://localhost:8501

🔧 문제 해결:
  - 포트 충돌 시: 다른 Streamlit 앱을 종료하세요
  - 패키지 오류 시: pip install -r requirements.txt
  - OpenAI 설정: API 키 필요 (https://platform.openai.com)
  - Ollama 설정: ollama serve 명령으로 서버 시작
    """
    print(help_text)

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="워터펌프 온도 모니터링 시스템",
        add_help=False
    )
    
    parser.add_argument('--chatbot', action='store_true', 
                       help='기본 AI 챗봇 실행')
    parser.add_argument('--llm-chatbot', action='store_true', 
                       help='LLM 기반 AI 챗봇 실행 (OpenAI/Ollama)')
    parser.add_argument('--dashboard', action='store_true', 
                       help='시각화 대시보드 실행')
    parser.add_argument('--analyzer', action='store_true', 
                       help='분석 엔진만 실행')
    parser.add_argument('--check', action='store_true', 
                       help='시스템 환경 점검')
    parser.add_argument('--help', action='store_true', 
                       help='도움말 표시')
    
    args = parser.parse_args()
    
    # 도움말 표시
    if args.help:
        show_help()
        return
    
    # 환경 점검
    if args.check:
        print("🔍 시스템 환경 점검 중...")
        
        if not check_files():
            return
            
        if not check_dependencies():
            return
            
        print("✅ 모든 점검 통과! 시스템이 정상적으로 설정되었습니다.")
        print("\n🚀 실행 가능한 명령어:")
        print("  python run.py --chatbot         # 기본 AI 챗봇")
        print("  python run.py --llm-chatbot     # LLM 챗봇 (권장)")
        print("  python run.py --dashboard       # 대시보드")
        print("  python run.py --analyzer        # 분석 엔진")
        return
    
    # 기본 환경 점검
    if not check_files() or not check_dependencies():
        print("\n💡 환경 점검을 실행하려면: python run.py --check")
        return
    
    # 실행 모드 선택
    if args.analyzer:
        run_analyzer()
    elif args.dashboard:
        run_dashboard()
    elif args.llm_chatbot:
        run_llm_chatbot()
    elif args.chatbot or len(sys.argv) == 1:  # 기본값은 기본 챗봇
        run_chatbot()
    else:
        show_help()

if __name__ == "__main__":
    main()
