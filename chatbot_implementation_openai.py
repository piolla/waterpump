import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
from water_pump_analyzer import WaterPumpAnalyzer

# 페이지 설정
st.set_page_config(
    page_title="워터펌프 AI 분석 챗봇 (LLM)",
    page_icon="🤖",
    layout="wide"
)

class LLMWaterPumpChatbot:
    def __init__(self):
        self.data = None
        self.analysis_cache = {}
        self.llm_provider = None
        self.openai_api_key = None
        self.ollama_model = None
        
    def set_llm_provider(self, provider, **kwargs):
        """LLM 제공자 설정"""
        self.llm_provider = provider
        if provider == "openai":
            self.openai_api_key = kwargs.get("api_key")
        elif provider == "ollama":
            self.ollama_model = kwargs.get("model", "llama2")
    
    def load_json_data(self, uploaded_file):
        """JSON 데이터 로드"""
        try:
            self.data = json.load(uploaded_file)
            self.analyze_data()
            return True
        except Exception as e:
            st.error(f"데이터 로드 오류: {e}")
            return False
    
    def analyze_data(self):
        """데이터 분석 및 캐시 생성"""
        if not self.data:
            return
            
        results = self.data['analysis_results']
        
        # 전체 통계 계산
        all_temps = []
        alert_counts = {'정상': 0, '관찰': 0, '주의': 0, '위험': 0}
        trend_counts = {'상승': 0, '하강': 0, '평형': 0}
        stability_counts = {'매우안정': 0, '안정': 0, '보통': 0, '불안정': 0}
        
        critical_batches = []
        
        for result in results:
            all_temps.append(result['statistics']['mean'])
            alert_counts[result['alert_level']] += 1
            trend_counts[result['trend']] += 1
            stability_counts[result['stability']] += 1
            
            # 위험/주의 배치 식별
            if result['alert_level'] in ['위험', '주의']:
                critical_batches.append(result)
        
        self.analysis_cache = {
            'total_batches': len(results),
            'avg_temperature': np.mean(all_temps),
            'max_temperature': max([r['statistics']['max'] for r in results]),
            'min_temperature': min([r['statistics']['min'] for r in results]),
            'alert_counts': alert_counts,
            'trend_counts': trend_counts,
            'stability_counts': stability_counts,
            'critical_batches': critical_batches,
            'analysis_period': {
                'start': results[0]['start_timestamp'],
                'end': results[-1]['end_timestamp']
            }
        }
    
    def create_context_prompt(self, user_query):
        """JSON 데이터를 기반으로 컨텍스트 프롬프트 생성"""
        if not self.data or not self.analysis_cache:
            return "데이터가 로드되지 않았습니다."
        
        # 데이터 요약 생성
        cache = self.analysis_cache
        metadata = self.data['metadata']
        
        context = f"""
당신은 워터펌프 온도 데이터 분석 전문가입니다. 다음 데이터를 기반으로 사용자 질문에 답변해주세요.

## 데이터 개요
- 분석 기간: {cache['analysis_period']['start'][:10]} ~ {cache['analysis_period']['end'][:10]}
- 총 배치 수: {cache['total_batches']}개
- 윈도우 크기: {metadata.get('window_size', 100)} 레코드
- 데이터 소스: {metadata.get('data_source', 'N/A')}

## 온도 통계
- 평균 온도: {cache['avg_temperature']:.1f}°C
- 최고 온도: {cache['max_temperature']:.1f}°C
- 최저 온도: {cache['min_temperature']:.1f}°C

## 경고 수준 분포
- 정상: {cache['alert_counts']['정상']}개 ({(cache['alert_counts']['정상']/cache['total_batches']*100):.1f}%)
- 관찰: {cache['alert_counts']['관찰']}개 ({(cache['alert_counts']['관찰']/cache['total_batches']*100):.1f}%)
- 주의: {cache['alert_counts']['주의']}개 ({(cache['alert_counts']['주의']/cache['total_batches']*100):.1f}%)
- 위험: {cache['alert_counts']['위험']}개 ({(cache['alert_counts']['위험']/cache['total_batches']*100):.1f}%)

## 트렌드 분포
- 상승: {cache['trend_counts']['상승']}개
- 하강: {cache['trend_counts']['하강']}개
- 평형: {cache['trend_counts']['평형']}개

## 안정성 분포
- 매우안정: {cache['stability_counts']['매우안정']}개
- 안정: {cache['stability_counts']['안정']}개
- 보통: {cache['stability_counts']['보통']}개
- 불안정: {cache['stability_counts']['불안정']}개

## 위험 배치 상세
"""
        
        # 위험 배치 정보 추가
        if cache['critical_batches']:
            context += f"위험/주의 배치: {len(cache['critical_batches'])}개\n"
            for batch in cache['critical_batches'][:5]:  # 최대 5개만 표시
                context += f"- 배치 {batch['batch_id']}: {batch['statistics']['mean']:.1f}°C ({batch['alert_level']}, {batch['value_label']})\n"
        else:
            context += "현재 위험 또는 주의 배치 없음\n"
        
        # 상세 분석 데이터 (최근 5개 배치)
        context += "\n## 최근 배치 상세 분석\n"
        recent_batches = self.data['analysis_results'][-5:]
        for batch in recent_batches:
            context += f"""
배치 {batch['batch_id']}:
- 시간: {batch['start_timestamp'][:16]}
- 평균 온도: {batch['statistics']['mean']:.1f}°C
- 온도 범위: {batch['statistics']['min']:.1f}°C ~ {batch['statistics']['max']:.1f}°C
- 표준편차: {batch['statistics']['std']:.1f}°C
- 특성 라벨: {batch['value_label']}
- 트렌드: {batch['trend']}
- 안정성: {batch['stability']}
- 경고 수준: {batch['alert_level']}
"""
        
        context += f"\n## 사용자 질문\n{user_query}\n"
        context += """
## 답변 가이드라인
1. 제조업 현장 담당자 관점에서 실용적인 답변 제공
2. 구체적인 수치와 데이터 기반 분석
3. 즉시 조치사항과 장기 개선사항 구분
4. 안전과 관련된 문제는 우선순위로 처리
5. 한국어로 친근하고 전문적인 톤으로 답변
6. 필요시 이모지를 사용하여 가독성 향상

위 데이터를 종합하여 사용자 질문에 대한 전문적이고 실용적인 답변을 제공해주세요.
"""
        
        return context
    
    def call_openai_api(self, prompt):
        """OpenAI API 호출"""
        try:
            import openai
            
            # OpenAI 클라이언트 초기화
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                # model="gpt-3.5-turbo",
                model= "gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "당신은 워터펌프 온도 데이터 분석 전문가입니다. 제조업 현장의 실무진에게 정확하고 실용적인 조언을 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ OpenAI API 호출 중 오류 발생: {str(e)}\n\n💡 다음을 확인해주세요:\n- API 키가 올바른지 확인\n- 인터넷 연결 상태 확인\n- OpenAI 계정 잔액 확인"
    
    def call_ollama_api(self, prompt):
        """Ollama API 호출"""
        try:
            url = "http://localhost:11434/api/generate"
            data = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=60)
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"❌ Ollama API 호출 실패: HTTP {response.status_code}\n\n💡 다음을 확인해주세요:\n- Ollama가 실행 중인지 확인 (ollama serve)\n- 모델이 설치되어 있는지 확인 (ollama pull {self.ollama_model})"
                
        except requests.exceptions.ConnectionError:
            return f"❌ Ollama 서버에 연결할 수 없습니다.\n\n💡 다음을 확인해주세요:\n- Ollama가 설치되어 있는지 확인\n- 'ollama serve' 명령으로 서버 시작\n- http://localhost:11434 접속 가능한지 확인"
        except requests.exceptions.Timeout:
            return f"❌ Ollama API 응답 시간 초과\n\n💡 모델이 너무 크거나 서버 성능이 부족할 수 있습니다."
        except Exception as e:
            return f"❌ Ollama API 호출 중 오류 발생: {str(e)}"
    
    def get_llm_response(self, user_query):
        """LLM을 통한 응답 생성"""
        if not self.llm_provider:
            return "🚫 LLM 모델이 설정되지 않았습니다. 사이드바에서 모델을 선택해주세요."
        
        # 컨텍스트 프롬프트 생성
        context_prompt = self.create_context_prompt(user_query)
        
        # LLM 호출
        if self.llm_provider == "openai":
            if not self.openai_api_key:
                return "🔑 OpenAI API 키가 설정되지 않았습니다."
            return self.call_openai_api(context_prompt)
        
        elif self.llm_provider == "ollama":
            return self.call_ollama_api(context_prompt)
        
        else:
            return "❌ 지원하지 않는 LLM 제공자입니다."

def load_and_analyze_csv(uploaded_file):
    """CSV 파일 로드 및 분석"""
    try:
        # CSV 데이터 미리보기
        preview_df = pd.read_csv(uploaded_file)
        st.sidebar.write("📋 **파일 미리보기**")
        st.sidebar.dataframe(preview_df.head(3))
        
        # 파일 포인터 리셋
        uploaded_file.seek(0)
        
        # 분석기 생성 및 데이터 로드
        analyzer = WaterPumpAnalyzer()
        
        if analyzer.load_data(uploaded_file=uploaded_file):
            st.sidebar.write(f"📊 **데이터 정보**")
            st.sidebar.write(f"레코드 수: {len(analyzer.data)}")
            st.sidebar.write(f"온도 범위: {analyzer.data['value'].min():.1f}°C ~ {analyzer.data['value'].max():.1f}°C")
            
            # 온도 분석 실행
            analyzer.analyze_temperature_characteristics()
            
            # 챗봇용 데이터 형식으로 변환
            chatbot_data = {
                'metadata': {
                    'analysis_date': datetime.now().isoformat(),
                    'total_batches': len(analyzer.analyzed_data),
                    'window_size': 100,
                    'data_source': 'uploaded_csv_file'
                },
                'analysis_results': analyzer.analyzed_data
            }
            
            # 챗봇에 데이터 설정
            st.session_state.chatbot.data = chatbot_data
            st.session_state.chatbot.analyze_data()
            
            # 자동으로 water_pump_data 폴더에 저장
            import os
            data_folder = 'water_pump_data'
            if not os.path.exists(data_folder):
                os.makedirs(data_folder)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            json_filename = f"llm_chatbot_analysis_{timestamp}.json"
            json_path = os.path.join(data_folder, json_filename)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(chatbot_data, f, ensure_ascii=False, indent=2)
            
            st.sidebar.info(f"📁 분석 결과가 {json_path}에 저장되었습니다.")
            
            return True
        else:
            st.sidebar.error("❌ CSV 파일 처리 실패")
            return False
            
    except Exception as e:
        st.sidebar.error(f"❌ CSV 처리 오류: {e}")
        return False

def create_sample_data_for_chatbot():
    """챗봇용 샘플 데이터 생성"""
    try:
        # 샘플 데이터 생성
        sample_data = []
        base_time = datetime.now()
        
        for i in range(500):
            timestamp = base_time + pd.Timedelta(minutes=i*10)
            if i < 100:
                temp = 45 + np.random.normal(0, 2)
            elif i < 200:
                temp = 60 + np.random.normal(0, 3)
            elif i < 300:
                temp = 75 + np.random.normal(0, 5)
            elif i < 400:
                temp = 85 + np.random.normal(0, 4)
            else:
                temp = 50 + np.random.normal(0, 2)
            
            sample_data.append({
                'timestamp': timestamp,
                'value': max(20, min(100, temp))
            })
        
        analyzer = WaterPumpAnalyzer()
        analyzer.load_data(data=sample_data)
        analyzer.analyze_temperature_characteristics()
        
        # 챗봇용 데이터 형식으로 변환
        chatbot_data = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'total_batches': len(analyzer.analyzed_data),
                'window_size': 100,
                'data_source': 'sample_data'
            },
            'analysis_results': analyzer.analyzed_data
        }
        
        # 챗봇에 데이터 설정
        st.session_state.chatbot.data = chatbot_data
        st.session_state.chatbot.analyze_data()
        
        # 자동으로 water_pump_data 폴더에 저장
        import os
        data_folder = 'water_pump_data'
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"llm_sample_data_analysis_{timestamp}.json"
        json_path = os.path.join(data_folder, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(chatbot_data, f, ensure_ascii=False, indent=2)
        
        st.sidebar.info(f"📁 샘플 데이터 분석 결과가 {json_path}에 저장되었습니다.")
        
    except Exception as e:
        st.sidebar.error(f"❌ 샘플 데이터 생성 실패: {e}")

def display_upload_guide():
    """데이터 업로드 가이드 표시"""
    st.info("📤 사이드바에서 LLM 모델을 설정하고 데이터를 업로드해주세요.")
    
    st.subheader("🤖 지원하는 LLM 모델")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌐 OpenAI GPT")
        st.markdown("""
        **✅ 장점:**
        - 뛰어난 한국어 처리 능력
        - 빠른 응답 속도
        - 일관된 고품질 답변
        
        **📋 설정 방법:**
        1. OpenAI API 키 발급
        2. 사이드바에서 OpenAI 선택
        3. API 키 입력
        """)
        
        st.info("💡 **API 키 발급:** https://platform.openai.com/api-keys")
    
    with col2:
        st.subheader("🏠 Local Ollama")
        st.markdown("""
        **✅ 장점:**
        - 로컬 실행으로 데이터 보안
        - API 비용 없음
        - 오프라인 사용 가능
        
        **📋 설정 방법:**
        1. Ollama 설치
        2. 모델 다운로드
        3. 서버 실행: `ollama serve`
        """)
        
        st.info("💡 **Ollama 설치:** https://ollama.ai/download")
    
    st.subheader("📁 지원하는 데이터 형식")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 CSV 파일 형식")
        st.code("""
timestamp,value
2024-01-01 10:00:00,45.2
2024-01-01 10:10:00,46.1
2024-01-01 10:20:00,47.3
        """, language="csv")
    
    with col2:
        st.subheader("📄 JSON 파일 형식")
        st.code("""
{
  "metadata": {...},
  "analysis_results": [...]
}
        """, language="json")

def setup_llm_provider():
    """LLM 제공자 설정 UI"""
    st.sidebar.header("🤖 LLM 모델 설정")
    
    # LLM 제공자 선택
    llm_provider = st.sidebar.radio(
        "LLM 모델 선택:",
        ["선택 안함", "OpenAI GPT", "Local Ollama"],
        key="llm_provider"
    )
    
    if llm_provider == "OpenAI GPT":
        st.sidebar.subheader("🔑 OpenAI 설정")
        
        # API 키 입력
        api_key = os.getenv('OPENAI_API_KEY')
        #api_key = st.sidebar.text_input(
        #    "API Key:",
        #    type="password",
        #    placeholder="sk-...",
        #    placeholder="****",
        #    help="OpenAI API 키를 입력하세요"
        #)
        
        if api_key:
            # OpenAI 패키지 확인
            try:
                import openai
                st.session_state.chatbot.set_llm_provider("openai", api_key=api_key)
                st.sidebar.success("✅ OpenAI 설정 완료!")
                return True
            except ImportError:
                st.sidebar.error("❌ OpenAI 패키지가 설치되지 않았습니다.")
                st.sidebar.code("pip install openai")
                return False
        else:
            st.sidebar.warning("🔑 API 키를 입력해주세요.")
            return False
    
    elif llm_provider == "Local Ollama":
        st.sidebar.subheader("🏠 Ollama 설정")
        
        # 모델 선택
        ollama_model = st.sidebar.selectbox(
            "모델 선택:",
            ["cogito:14b", "cogito:8b","gemma3:12b", "deepseek-r1:14b", "mistral", "llama3:latest"],
            help="사용할 Ollama 모델을 선택하세요"
        )
        
        # 연결 테스트
        if st.sidebar.button("🔍 연결 테스트"):
            try:
                response = requests.get("http://localhost:11434/api/version", timeout=5)
                if response.status_code == 200:
                    st.session_state.chatbot.set_llm_provider("ollama", model=ollama_model)
                    st.sidebar.success("✅ Ollama 연결 성공!")
                    return True
                else:
                    st.sidebar.error("❌ Ollama 서버 응답 오류")
                    return False
            except:
                st.sidebar.error("❌ Ollama 서버에 연결할 수 없습니다.")
                st.sidebar.info("💡 'ollama serve' 명령으로 서버를 시작하세요.")
                return False
        
        # 자동 설정 (이미 설정된 경우)
        if hasattr(st.session_state.chatbot, 'ollama_model') and st.session_state.chatbot.ollama_model:
            return True
    
    return False

def main():
    st.title("🤖 워터펌프 AI 분석 챗봇 (LLM)")
    st.markdown("### OpenAI GPT & Local Ollama 지원")
    
    # 챗봇 초기화
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = LLMWaterPumpChatbot()
    
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'llm_configured' not in st.session_state:
        st.session_state.llm_configured = False
    
    # 사이드바 - LLM 설정
    llm_configured = setup_llm_provider()
    st.session_state.llm_configured = llm_configured
    
    # 사이드바 - 데이터 업로드
    with st.sidebar:
        st.subheader("📂 데이터 업로드")
        
        if not llm_configured:
            st.warning("⚠️ 먼저 LLM 모델을 설정해주세요.")
        
        # 업로드 방식 선택
        upload_method = st.radio(
            "데이터 입력 방식:",
            ["CSV 파일", "JSON 파일", "샘플 데이터"],
            disabled=not llm_configured
        )
        
        if upload_method == "CSV 파일" and llm_configured:
            uploaded_file = st.file_uploader(
                "CSV 파일을 드래그하거나 선택하세요",
                type=['csv'],
                help="timestamp, value 컬럼이 포함된 CSV 파일"
            )
            
            if uploaded_file and not st.session_state.data_loaded:
                if st.button("🔄 CSV 분석 실행"):
                    with st.spinner("CSV 데이터 분석 중..."):
                        success = load_and_analyze_csv(uploaded_file)
                        if success:
                            st.session_state.data_loaded = True
                            st.success("✅ CSV 분석 완료!")
        
        elif upload_method == "JSON 파일" and llm_configured:
            uploaded_file = st.file_uploader(
                "JSON 파일을 드래그하거나 선택하세요",
                type=['json'],
                help="워터펌프 온도 분석 JSON 파일"
            )
            
            if uploaded_file and not st.session_state.data_loaded:
                if st.session_state.chatbot.load_json_data(uploaded_file):
                    st.session_state.data_loaded = True
                    st.success("✅ JSON 데이터 로드 완료!")
        
        elif upload_method == "샘플 데이터" and llm_configured:
            if st.button("🎲 샘플 데이터 생성") and not st.session_state.data_loaded:
                with st.spinner("샘플 데이터 생성 중..."):
                    create_sample_data_for_chatbot()
                    st.session_state.data_loaded = True
                    st.success("✅ 샘플 데이터 생성 완료!")
        
        # 데이터 정보 표시
        if st.session_state.data_loaded and st.session_state.chatbot.data:
            st.write("---")
            st.write("📊 **로드된 데이터 정보**")
            metadata = st.session_state.chatbot.data.get('metadata', {})
            st.write(f"총 배치: {metadata.get('total_batches', 'N/A')}개")
            st.write(f"데이터 소스: {metadata.get('data_source', 'N/A')}")
            
            cache = st.session_state.chatbot.analysis_cache
            if cache:
                st.write(f"평균 온도: {cache['avg_temperature']:.1f}°C")
                critical_count = cache['alert_counts']['위험'] + cache['alert_counts']['주의']
                st.write(f"위험/주의: {critical_count}개")
                
                # LLM 모델 정보
                st.write("---")
                st.write("🤖 **LLM 모델 정보**")
                if st.session_state.chatbot.llm_provider == "openai":

                    st.write("🌐 OpenAI gpt-4.1-mini" ) 

                elif st.session_state.chatbot.llm_provider == "ollama":
                    st.write(f"🏠 Ollama ({st.session_state.chatbot.ollama_model})")
    
    # 메인 영역
    if not llm_configured:
        display_upload_guide()
        return
    
    if not st.session_state.data_loaded:
        st.info("📤 사이드바에서 데이터를 업로드해주세요.")
        return
    
    # 채팅 인터페이스
    st.subheader("💬 LLM 기반 AI 분석 채팅")
    
    # 채팅 히스토리 초기화
    if 'messages' not in st.session_state:
        welcome_msg = "안녕하세요! 저는 워터펌프 온도 데이터 분석 전문 AI입니다. 🌡️\n\n"
        if st.session_state.chatbot.llm_provider == "openai":
            welcome_msg += "🌐 **OpenAI GPT**로 구동되어 고품질 분석을 제공합니다.\n"
        elif st.session_state.chatbot.llm_provider == "ollama":
            welcome_msg += f"🏠 **Local Ollama ({st.session_state.chatbot.ollama_model})**로 구동되어 보안이 보장됩니다.\n"
        welcome_msg += "\n업로드된 JSON 데이터를 기반으로 정확한 분석과 조언을 드리겠습니다. 무엇이든 물어보세요!"
        
        st.session_state.messages = [
            {"role": "assistant", "content": welcome_msg}
        ]
    
    # 채팅 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요..."):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # LLM 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("🤖 AI가 데이터를 분석하고 있습니다..."):
                response = st.session_state.chatbot.get_llm_response(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 퀵 액션 버튼
    st.subheader("🚀 빠른 분석 (LLM 기반)")
    
    col1, col2, col3 = st.columns(3)
    
    quick_queries = {
        "전체 현황": "현재 워터펌프의 전반적인 온도 상태는 어떤가요? 주요 통계와 함께 종합적인 평가를 해주세요.",
        "위험 분석": "현재 위험하거나 주의가 필요한 상황이 있나요? 구체적인 배치와 대응 방안을 알려주세요.",
        "정비 조언": "데이터를 바탕으로 예측 정비 계획을 세워주세요. 우선순위와 구체적인 점검 항목을 포함해주세요."
    }
    
    with col1:
        if st.button("📊 전체 현황 (LLM)"):
            query = quick_queries["전체 현황"]
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("🤖 분석 중..."):
                response = st.session_state.chatbot.get_llm_response(query)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("⚠️ 위험 분석 (LLM)"):
            query = quick_queries["위험 분석"]
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("🤖 분석 중..."):
                response = st.session_state.chatbot.get_llm_response(query)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("🔧 정비 조언 (LLM)"):
            query = quick_queries["정비 조언"]
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("🤖 분석 중..."):
                response = st.session_state.chatbot.get_llm_response(query)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # 고급 질문 예시
    st.subheader("💡 고급 질문 예시")
    
    example_queries = [
        "온도 트렌드를 보면 앞으로 어떤 문제가 예상되나요?",
        "에너지 효율을 높이기 위한 구체적인 방안을 제시해주세요.",
        "현재 데이터를 기반으로 최적의 운영 온도 범위는 어떻게 설정해야 할까요?",
        "계절별 온도 변화에 대비한 예방 조치는 무엇인가요?",
        "비슷한 패턴의 배치들을 그룹화하여 운영 전략을 세워주세요.",
        "현재 설정된 경고 임계값이 적절한지 평가해주세요."
    ]
    
    cols = st.columns(2)
    for i, query in enumerate(example_queries):
        col = cols[i % 2]
        if col.button(f"💭 {query[:30]}...", key=f"example_{i}"):
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("🤖 분석 중..."):
                response = st.session_state.chatbot.get_llm_response(query)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()

## 실행 방법 (CLI에서) 
## streamlit run chatbot_implementation_openai.py
## 
