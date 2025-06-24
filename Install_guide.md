# LLM 기반 워터펌프 AI 챗봇 설정 가이드  

- 새로운 기능: chatbot_implementation_openai.py
- 이제 OpenAI GPT와 Local Ollama 모델을 지원하는 고급 AI 챗봇을 사용할 수 있습니다!

## 빠른 시작
- 1단계: LLM 챗봇 실행
```bash
python run.py --llm-chatbot
```

## 2단계: 브라우저에서 설정
- http://localhost:8501 접속
- 사이드바에서 LLM 모델 선택
- API 키 입력 또는 Ollama 연결

## 3단계: 데이터 업로드 및 분석 시작!
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
