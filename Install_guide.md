# LLM 기반 워터펌프 AI 챗봇 설치 가이드  
🗂️ 프로젝트 폴더 구조
water_pump_monitoring_system/
... water_pump_analyzer.py           # 데이터 분석 엔진
... streamlit_dashboard.py           # 시각화 대시보드
... chatbot_implementation.py        # AI 챗봇
... run.py                          # 통합 실행 스크립트
... generate_sample_csv.py           # 샘플 데이터 생성기
... requirements.txt                 # 패키지 의존성
... README.md                       # 프로젝트 설명서
... 📁 water_pump_data/                # 데이터 저장 폴더 (자동 생성)
........ water_pump_analysis_20241201_143022.json
........ csv_analysis_20241201_143055.json
........ chatbot_analysis_20241201_143128.json
........ sample_data_analysis_20241201_143200.json
........ sample_water_pump_data.csv
........ pump_report_20241201_143245.txt
... 📁 __pycache__/                    # Python 캐시 (자동 생성) 


# 설치 및 실행 단계
## 1단계: 프로젝트 폴더 생성
```bash
mkdir water_pump_monitoring_system
cd water_pump_monitoring_system
```

## 2단계: 파일 다운로드 및 배치
- 모든 Python 파일을 프로젝트 폴더에 저장:
``` 
water_pump_analyzer.py
streamlit_dashboard.py
chatbot_implementation.py
run.py
generate_sample_csv.py
requirements.txt
```

## 3단계: 가상환경 생성 (권장)
```bash
# Windows
python -m venv water_pump_env
water_pump_env\Scripts\activate

# macOS/Linux
python3 -m venv water_pump_env
source water_pump_env/bin/activate
```

## 4단계: 패키지 설치
```bash
pip install -r requirements.txt

## 5단계: 시스템 환경 점검
```bash
python run.py --check
```

## 6단계: 샘플 데이터 생성 (선택사항)
```bash
python generate_sample_csv.py --scenario combined
```

## 7단계: 시스템 실행
```bash
# AI 챗봇 실행 (권장)
python run.py --chatbot

# 또는 대시보드만 실행
python run.py --dashboard

# 또는 분석 엔진만 실행
python run.py --analyzer
```

### OpenAI GPT 설정
- 사전 준비
1) OpenAI 계정 생성: https://platform.openai.com/signup
2) API 키 발급: https://platform.openai.com/api-keys
3) 결제 정보 등록: 사용량만큼 과금 (매우 저렴) 
4) API 키 설정
```bash
# 환경변수로 설정 (선택사항)
export OPENAI_API_KEY="sk-your-api-key-here"
# 또는 앱에서 직접 입력
```


## Local Ollama 설정
### 사전 준비

1) Ollama 설치: https://ollama.ai/download
2) 모델 다운로드
3) 서버 실행

### 설치 과정
- Windows/macOS/Linux
```bash
# 1. Ollama 설치 (웹사이트에서 다운로드)
# https://ollama.ai/download

# 2. 모델 다운로드
ollama pull llama2           # 7B 모델 (권장)
ollama pull llama2:13b       # 13B 모델 (더 정확하지만 느림)
ollama pull mistral          # Mistral 7B
ollama pull neural-chat      # Intel Neural Chat

# 3. 서버 실행
ollama serve
```

### 시스템 요구사항
- 사용자 PC GPUdp 따라 적절한 모델 설치 권장
- (예) Llama2:13b: 16GB RAM 이상, 7GB HDD 이상 
