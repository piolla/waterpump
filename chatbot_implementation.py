import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import re
from water_pump_analyzer import WaterPumpAnalyzer

# 페이지 설정
st.set_page_config(
    page_title="워터펌프 AI 분석 챗봇",
    page_icon="🤖",
    layout="wide"
)

class WaterPumpChatbot:
    def __init__(self):
        self.data = None
        self.analysis_cache = {}
        
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
    
    def get_emergency_alert(self):
        """긴급 상황 체크"""
        critical_batches = self.analysis_cache['critical_batches']
        emergency_batches = [b for b in critical_batches if b['alert_level'] == '위험']
        
        if emergency_batches:
            return self.format_emergency_response(emergency_batches)
        return None
    
    def format_emergency_response(self, emergency_batches):
        """긴급 상황 응답 포맷"""
        response = "🚨 **긴급 알림: 워터펌프 과열 감지**\n\n"
        
        for batch in emergency_batches:
            response += f"⛔ **위험 상황 - 배치 {batch['batch_id']}**\n"
            response += f"- 최고 온도: {batch['statistics']['max']:.1f}°C\n"
            response += f"- 평균 온도: {batch['statistics']['mean']:.1f}°C\n"
            response += f"- 발생 시간: {batch['start_timestamp']}\n"
            response += f"- 온도 특성: {batch['value_label']}\n\n"
        
        response += "🔧 **즉시 조치사항**\n"
        response += "1. 워터펌프 즉시 정지 및 안전 점검\n"
        response += "2. 냉각수 유량 및 온도 확인\n"
        response += "3. 냉각 필터 및 라디에이터 점검\n"
        response += "4. 베어링 및 씰 상태 확인\n"
        response += "5. 현장 담당자 즉시 연락\n\n"
        
        response += "📞 **후속 조치**\n"
        response += "- 정비팀 대기 요청\n"
        response += "- 원인 분석 후 재가동 결정\n"
        
        return response
    
    def analyze_user_query(self, query):
        """사용자 질문 분석 및 응답 생성"""
        query = query.lower()
        
        # 긴급 상황 우선 체크
        emergency = self.get_emergency_alert()
        if emergency and any(word in query for word in ['위험', '문제', '이상', '경고', '알림']):
            return emergency
        
        # 키워드 기반 응답 분기
        if any(word in query for word in ['전체', '전반', '개요', '요약', '상황']):
            return self.get_overall_analysis()
        elif any(word in query for word in ['온도', '평균', '최고', '최저']):
            return self.get_temperature_analysis()
        elif any(word in query for word in ['트렌드', '변화', '패턴', '경향']):
            return self.get_trend_analysis()
        elif any(word in query for word in ['위험', '주의', '경고', '문제']):
            return self.get_risk_analysis()
        elif any(word in query for word in ['예측', '정비', '점검', '유지보수']):
            return self.get_maintenance_advice()
        elif any(word in query for word in ['효율', '최적화', '개선', '성능']):
            return self.get_optimization_advice()
        else:
            return self.get_general_response(query)
    
    def get_overall_analysis(self):
        """전체 분석 응답"""
        cache = self.analysis_cache
        
        response = "🔍 **워터펌프 온도 전체 분석 결과**\n\n"
        
        response += "📊 **전체 현황**\n"
        response += f"- 분석 기간: {cache['analysis_period']['start'][:10]} ~ {cache['analysis_period']['end'][:10]}\n"
        response += f"- 총 배치 수: {cache['total_batches']}개\n"
        response += f"- 평균 온도: {cache['avg_temperature']:.1f}°C\n"
        response += f"- 최고 온도: {cache['max_temperature']:.1f}°C\n"
        response += f"- 최저 온도: {cache['min_temperature']:.1f}°C\n\n"
        
        response += "⚠️ **경고 수준 분포**\n"
        for level, count in cache['alert_counts'].items():
            percentage = (count / cache['total_batches']) * 100
            response += f"- {level}: {count}개 ({percentage:.1f}%)\n"
        
        response += "\n📈 **주요 발견사항**\n"
        critical_count = cache['alert_counts']['위험'] + cache['alert_counts']['주의']
        if critical_count > 0:
            response += f"- 위험/주의 배치: {critical_count}개 발견\n"
            response += "- 즉시 점검 및 조치 필요\n"
        else:
            response += "- 전반적으로 안정적인 운영 상태\n"
            
        if cache['avg_temperature'] > 75:
            response += "- 평균 온도가 높은 편으로 냉각 효율 점검 권장\n"
        
        return response
    
    def get_temperature_analysis(self):
        """온도 분석 응답"""
        cache = self.analysis_cache
        results = self.data['analysis_results']
        
        response = "🌡️ **온도 상세 분석**\n\n"
        
        # 온도 범위별 분포
        temp_ranges = {'저온 (<40°C)': 0, '정상 (40-70°C)': 0, '고온 (70-85°C)': 0, '과열 (>85°C)': 0}
        
        for result in results:
            mean_temp = result['statistics']['mean']
            if mean_temp < 40:
                temp_ranges['저온 (<40°C)'] += 1
            elif mean_temp < 70:
                temp_ranges['정상 (40-70°C)'] += 1
            elif mean_temp < 85:
                temp_ranges['고온 (70-85°C)'] += 1
            else:
                temp_ranges['과열 (>85°C)'] += 1
        
        response += "📊 **온도 범위별 분포**\n"
        for range_name, count in temp_ranges.items():
            percentage = (count / cache['total_batches']) * 100
            response += f"- {range_name}: {count}개 ({percentage:.1f}%)\n"
        
        response += f"\n🔥 **온도 통계**\n"
        response += f"- 전체 평균: {cache['avg_temperature']:.1f}°C\n"
        response += f"- 최고 기록: {cache['max_temperature']:.1f}°C\n"
        response += f"- 최저 기록: {cache['min_temperature']:.1f}°C\n"
        
        # 고온 배치 식별
        high_temp_batches = [r for r in results if r['statistics']['mean'] > 80]
        if high_temp_batches:
            response += f"\n⚠️ **고온 배치 ({len(high_temp_batches)}개)**\n"
            for batch in high_temp_batches[:3]:  # 상위 3개만 표시
                response += f"- 배치 {batch['batch_id']}: {batch['statistics']['mean']:.1f}°C ({batch['value_label']})\n"
        
        return response
    
    def get_trend_analysis(self):
        """트렌드 분석 응답"""
        cache = self.analysis_cache
        
        response = "📈 **온도 트렌드 분석**\n\n"
        
        response += "📊 **트렌드 분포**\n"
        for trend, count in cache['trend_counts'].items():
            percentage = (count / cache['total_batches']) * 100
            response += f"- {trend} 트렌드: {count}개 ({percentage:.1f}%)\n"
        
        response += "\n🔄 **안정성 분포**\n"
        for stability, count in cache['stability_counts'].items():
            percentage = (count / cache['total_batches']) * 100
            response += f"- {stability}: {count}개 ({percentage:.1f}%)\n"
        
        # 트렌드 해석
        response += "\n💡 **트렌드 해석**\n"
        if cache['trend_counts']['상승'] > cache['total_batches'] * 0.3:
            response += "- 온도 상승 트렌드가 우세함 → 냉각 시스템 점검 필요\n"
        if cache['stability_counts']['불안정'] > cache['total_batches'] * 0.2:
            response += "- 온도 변동이 큰 배치가 많음 → 운영 조건 점검 필요\n"
        if cache['trend_counts']['평형'] > cache['total_batches'] * 0.6:
            response += "- 대부분 안정적인 온도 유지 → 양호한 운영 상태\n"
        
        return response
    
    def get_risk_analysis(self):
        """위험 분석 응답"""
        cache = self.analysis_cache
        critical_batches = cache['critical_batches']
        
        response = "⚠️ **위험 요소 분석**\n\n"
        
        if not critical_batches:
            response += "✅ **양호한 상태**\n"
            response += "- 현재 위험 또는 주의 배치 없음\n"
            response += "- 정상적인 운영 범위 내에서 동작\n"
            return response
        
        response += f"🚨 **위험/주의 배치: {len(critical_batches)}개**\n\n"
        
        for batch in critical_batches:
            response += f"**배치 {batch['batch_id']} ({batch['alert_level']})**\n"
            response += f"- 평균 온도: {batch['statistics']['mean']:.1f}°C\n"
            response += f"- 최고 온도: {batch['statistics']['max']:.1f}°C\n"
            response += f"- 특성: {batch['value_label']}\n"
            response += f"- 발생 시간: {batch['start_timestamp'][:16]}\n\n"
        
        response += "🔧 **권장 조치사항**\n"
        response += "1. 고온 배치 원인 분석 (부하, 냉각수, 환경온도)\n"
        response += "2. 냉각 시스템 점검 (필터, 펌프, 라디에이터)\n"
        response += "3. 베어링 및 회전부 윤활 상태 확인\n"
        response += "4. 온도 센서 정확도 검증\n"
        
        return response
    
    def get_maintenance_advice(self):
        """정비 조언 응답"""
        cache = self.analysis_cache
        
        response = "🔧 **예측 정비 조언**\n\n"
        
        # 정비 우선순위 결정
        high_temp_ratio = (cache['alert_counts']['위험'] + cache['alert_counts']['주의']) / cache['total_batches']
        unstable_ratio = cache['stability_counts']['불안정'] / cache['total_batches']
        
        response += "📋 **정비 우선순위**\n"
        
        if high_temp_ratio > 0.2:
            response += "🔴 **1순위: 냉각 시스템 전면 점검**\n"
            response += "- 냉각수 교체 및 순환 점검\n"
            response += "- 라디에이터 청소 및 팬 동작 확인\n"
            response += "- 써모스탯 교체 검토\n\n"
        
        if unstable_ratio > 0.3:
            response += "🟡 **2순위: 기계적 부품 점검**\n"
            response += "- 베어링 윤활 및 교체\n"
            response += "- 축 정렬 상태 확인\n"
            response += "- 임펠러 균형 점검\n\n"
        
        response += "🟢 **3순위: 예방 정비**\n"
        response += "- 정기 오일 교체\n"
        response += "- 씰 및 가스켓 점검\n"
        response += "- 전기 연결부 점검\n\n"
        
        # 정비 주기 제안
        response += "⏰ **권장 정비 주기**\n"
        if cache['avg_temperature'] > 75:
            response += "- 단기 점검: 1주일 후\n"
            response += "- 정기 정비: 1개월 단축\n"
        else:
            response += "- 정기 점검: 2주 후\n"
            response += "- 정기 정비: 기존 주기 유지\n"
        
        return response
    
    def get_optimization_advice(self):
        """최적화 조언 응답"""
        cache = self.analysis_cache
        
        response = "💡 **운영 최적화 제안**\n\n"
        
        response += "⚡ **에너지 효율성 개선**\n"
        if cache['avg_temperature'] > 70:
            response += "- 냉각 효율 향상으로 에너지 절약 가능\n"
            response += "- 변속 제어를 통한 부하 최적화\n"
        
        response += "- 운전 시간 최적화 (피크 시간대 회피)\n"
        response += "- 예열 시간 단축 방안\n\n"
        
        response += "🎯 **온도 제어 전략**\n"
        response += "- 목표 온도: 50-65°C 범위 유지\n"
        response += "- 냉각수 온도 자동 제어 시스템 도입\n"
        response += "- 환경 온도 보상 제어\n\n"
        
        response += "📊 **모니터링 체계 강화**\n"
        response += "- 실시간 온도 알림 시스템\n"
        response += "- 트렌드 기반 예측 알고리즘\n"
        response += "- 다중 센서를 통한 정확도 향상\n"
        
        return response
    
    def get_general_response(self, query):
        """일반적인 응답"""
        return f"""🤖 **워터펌프 AI 어시스턴트**

질문을 이해했습니다: "{query}"

다음과 같은 분석을 도와드릴 수 있습니다:

📊 **분석 유형**
- "전체 상황은 어떤가요?" - 전반적인 온도 분석
- "온도 트렌드 분석해주세요" - 변화 패턴 분석  
- "위험 요소가 있나요?" - 위험 상황 점검
- "정비 계획을 세워주세요" - 예측 정비 조언
- "효율성 개선 방안은?" - 최적화 제안

구체적인 질문을 해주시면 더 정확한 분석을 제공하겠습니다!"""

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
            json_filename = f"chatbot_analysis_{timestamp}.json"
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
        json_filename = f"sample_data_analysis_{timestamp}.json"
        json_path = os.path.join(data_folder, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(chatbot_data, f, ensure_ascii=False, indent=2)
        
        st.sidebar.info(f"📁 샘플 데이터 분석 결과가 {json_path}에 저장되었습니다.")
        
    except Exception as e:
        st.sidebar.error(f"❌ 샘플 데이터 생성 실패: {e}")

def display_upload_guide():
    """데이터 업로드 가이드 표시"""
    st.info("📤 사이드바에서 데이터를 업로드해주세요.")
    
    st.header("📁 지원하는 데이터 형식")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 CSV 파일 형식")
        st.code("""
timestamp,value
2024-01-01 10:00:00,45.2
2024-01-01 10:10:00,46.1
2024-01-01 10:20:00,47.3
2024-01-01 10:30:00,48.0
...
        """, language="csv")
        
        st.success("✅ **CSV 파일 장점:**\n"
                  "- 원시 데이터 직접 업로드\n"
                  "- 실시간 분석 실행\n"
                  "- 자동 전처리 및 라벨링")
    
    with col2:
        st.subheader("📄 JSON 파일 형식")
        st.code("""
{
  "metadata": {
    "analysis_date": "2024-01-01T10:00:00",
    "total_batches": 5,
    "window_size": 100
  },
  "analysis_results": [...]
}
        """, language="json")
        
        st.info("ℹ️ **JSON 파일 특징:**\n"
               "- 이미 분석된 데이터\n"
               "- 빠른 로드 및 시각화\n"
               "- 기존 분석 결과 재활용")
    
    st.header("🔧 자동 기능")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔍 컬럼 자동 매핑**
        - timestamp ↔ time, date, 시간
        - value ↔ temp, temperature, 온도
        """)
    
    with col2:
        st.markdown("""
        **📊 자동 분석**
        - 100개 레코드 단위 분석
        - 온도 특성 라벨 생성
        - 위험 수준 자동 분류
        """)
    
    with col3:
        st.markdown("""
        **⚡ 실시간 대응**
        - 과열 상황 즉시 감지
        - 예측 정비 조언
        - 맞춤형 분석 리포트
        """)

def main():
    st.title("🤖 워터펌프 AI 분석 챗봇")
    st.markdown("### 워터펌프 온도 데이터 전문 분석 어시스턴트")
    
    # 챗봇 초기화
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = WaterPumpChatbot()
    
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    # 사이드바 - 데이터 업로드
    with st.sidebar:
        st.header("📂 데이터 업로드")
        
        # 업로드 방식 선택
        upload_method = st.radio(
            "데이터 입력 방식:",
            ["CSV 파일", "JSON 파일", "샘플 데이터"]
        )
        
        if upload_method == "CSV 파일":
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
                            
                            # 긴급 상황 체크
                            emergency = st.session_state.chatbot.get_emergency_alert()
                            if emergency:
                                st.error("🚨 긴급 상황 감지!")
        
        elif upload_method == "JSON 파일":
            uploaded_file = st.file_uploader(
                "JSON 파일을 드래그하거나 선택하세요",
                type=['json'],
                help="워터펌프 온도 분석 JSON 파일"
            )
            
            if uploaded_file and not st.session_state.data_loaded:
                if st.session_state.chatbot.load_json_data(uploaded_file):
                    st.session_state.data_loaded = True
                    st.success("✅ JSON 데이터 로드 완료!")
                    
                    # 긴급 상황 체크
                    emergency = st.session_state.chatbot.get_emergency_alert()
                    if emergency:
                        st.error("🚨 긴급 상황 감지!")
        
        else:  # 샘플 데이터
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
    
    # 메인 영역
    if not st.session_state.data_loaded:
        display_upload_guide()
        return
    
    # 채팅 인터페이스
    st.header("💬 AI 분석 채팅")
    
    # 채팅 히스토리 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "안녕하세요! 워터펌프 온도 분석 전문 AI입니다. 데이터 분석에 대해 무엇이든 물어보세요! 🌡️"}
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
        
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("분석 중..."):
                response = st.session_state.chatbot.analyze_user_query(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 퀵 액션 버튼
    st.header("🚀 빠른 분석")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 전체 현황"):
            response = st.session_state.chatbot.get_overall_analysis()
            st.session_state.messages.append({"role": "user", "content": "전체 현황 분석"})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("⚠️ 위험 분석"):
            response = st.session_state.chatbot.get_risk_analysis()
            st.session_state.messages.append({"role": "user", "content": "위험 요소 분석"})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("🔧 정비 조언"):
            response = st.session_state.chatbot.get_maintenance_advice()
            st.session_state.messages.append({"role": "user", "content": "정비 계획 조언"})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

if __name__ == "__main__":
    main()


##
## streamlit run chatbot_implementation.py
## 
