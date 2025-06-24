import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from water_pump_analyzer import WaterPumpAnalyzer

# 페이지 설정
st.set_page_config(
    page_title="워터펌프 온도 모니터링 시스템",
    page_icon="🌡️",
    layout="wide"
)

class StreamlitDashboard:
    def __init__(self):
        self.data = None
        self.analyzer = None
        self.load_data()
    
    def load_data(self):
        """CSV 또는 JSON 파일에서 데이터 로드"""
        st.sidebar.header("📂 데이터 업로드")
        
        # 파일 업로드 옵션 선택
        upload_option = st.sidebar.radio(
            "데이터 입력 방식 선택:",
            ["CSV 파일 업로드", "JSON 파일 업로드", "샘플 데이터 사용"]
        )
        
        if upload_option == "CSV 파일 업로드":
            return self.load_csv_data()
        elif upload_option == "JSON 파일 업로드":
            return self.load_json_data()
        else:
            return self.load_sample_data()
    
    def load_csv_data(self):
        """CSV 파일 로드 및 처리"""
        st.sidebar.subheader("CSV 파일 업로드")
        
        uploaded_file = st.sidebar.file_uploader(
            "CSV 파일을 선택하거나 드래그하세요",
            type=['csv'],
            key="csv_uploader",
            help="timestamp, value 컬럼이 포함된 CSV 파일을 업로드하세요"
        )
        
        if uploaded_file is not None:
            try:
                # CSV 파일 미리보기
                preview_df = pd.read_csv(uploaded_file)
                st.sidebar.write("📋 **파일 미리보기**")
                st.sidebar.dataframe(preview_df.head(3))
                
                # 파일 다시 읽기 (seek to beginning)
                uploaded_file.seek(0)
                
                # WaterPumpAnalyzer로 데이터 처리
                self.analyzer = WaterPumpAnalyzer()
                
                if self.analyzer.load_data(uploaded_file=uploaded_file):
                    st.sidebar.success(f"✅ CSV 데이터 로드 완료! ({len(self.analyzer.data)}개 레코드)")
                    
                    # 컬럼 정보 표시
                    st.sidebar.write("📊 **데이터 정보**")
                    st.sidebar.write(f"- 시작 시간: {self.analyzer.data['timestamp'].min()}")
                    st.sidebar.write(f"- 종료 시간: {self.analyzer.data['timestamp'].max()}")
                    st.sidebar.write(f"- 온도 범위: {self.analyzer.data['value'].min():.1f}°C ~ {self.analyzer.data['value'].max():.1f}°C")
                    
                    # 분석 실행 버튼
                    if st.sidebar.button("🔄 온도 분석 실행"):
                        with st.sidebar.spinner("분석 중..."):
                            self.analyzer.analyze_temperature_characteristics()
                            
                            # JSON 형태로 변환
                            self.data = {
                                'metadata': {
                                    'analysis_date': datetime.now().isoformat(),
                                    'total_batches': len(self.analyzer.analyzed_data),
                                    'window_size': 100,
                                    'data_source': 'uploaded_csv_file'
                                },
                                'analysis_results': self.analyzer.analyzed_data
                            }
                            
                            # 자동으로 water_pump_data 폴더에 저장
                            import os
                            data_folder = 'water_pump_data'
                            if not os.path.exists(data_folder):
                                os.makedirs(data_folder)
                            
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            json_filename = f"csv_analysis_{timestamp}.json"
                            json_path = os.path.join(data_folder, json_filename)
                            
                            with open(json_path, 'w', encoding='utf-8') as f:
                                json.dump(self.data, f, ensure_ascii=False, indent=2)
                            
                            st.sidebar.success("✅ 분석 완료!")
                            st.sidebar.info(f"📁 결과가 {json_path}에 저장되었습니다.")
                            return True
                else:
                    st.sidebar.error("❌ CSV 파일 처리 중 오류가 발생했습니다.")
                    
            except Exception as e:
                st.sidebar.error(f"❌ 파일 로드 중 오류: {e}")
                st.sidebar.info("💡 CSV 파일이 다음 형식인지 확인하세요:\n- timestamp, value 컬럼 포함\n- 날짜/시간 형식이 올바른지 확인")
        
        return False
    
    def load_json_data(self):
        """기존 JSON 파일 로드"""
        st.sidebar.subheader("JSON 파일 업로드")
        
        uploaded_file = st.sidebar.file_uploader(
            "분석된 JSON 파일을 업로드하세요", 
            type=['json'],
            key="json_uploader",
            help="이미 분석된 워터펌프 온도 데이터 JSON 파일"
        )
        
        if uploaded_file is not None:
            try:
                self.data = json.load(uploaded_file)
                st.sidebar.success("✅ JSON 데이터 로드 완료!")
                
                # 데이터 정보 표시
                metadata = self.data.get('metadata', {})
                st.sidebar.write("📊 **분석 정보**")
                st.sidebar.write(f"- 총 배치: {metadata.get('total_batches', 'N/A')}개")
                st.sidebar.write(f"- 윈도우 크기: {metadata.get('window_size', 'N/A')}")
                st.sidebar.write(f"- 분석 일시: {metadata.get('analysis_date', 'N/A')}")
                
                return True
            except Exception as e:
                st.sidebar.error(f"❌ JSON 파일 로드 중 오류: {e}")
        
        return False
    
    def load_sample_data(self):
        """샘플 데이터 생성"""
        st.sidebar.subheader("샘플 데이터")
        
        if st.sidebar.button("🎲 샘플 데이터 생성"):
            with st.sidebar.spinner("샘플 데이터 생성 중..."):
                self.create_sample_data()
                return True
        
        return False
    
    def create_sample_data(self):
        """샘플 데이터 생성"""
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
            
            self.data = {
                'metadata': {
                    'analysis_date': datetime.now().isoformat(),
                    'total_batches': len(analyzer.analyzed_data),
                    'window_size': 100,
                    'data_source': 'sample_data'
                },
                'analysis_results': analyzer.analyzed_data
            }
            
            st.sidebar.success("✅ 샘플 데이터 생성 완료!")
            
        except Exception as e:
            st.sidebar.error(f"❌ 샘플 데이터 생성 실패: {e}")
    
    def display_data_upload_guide(self):
        """데이터 업로드 가이드 표시"""
        st.header("📁 데이터 업로드 가이드")
        
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
            
            st.info("💡 **CSV 파일 요구사항:**\n"
                   "- timestamp: 날짜/시간 데이터\n"
                   "- value: 온도 값 (숫자)\n"
                   "- 헤더 행 포함 권장")
        
        with col2:
            st.subheader("🔧 지원 기능")
            st.markdown("""
            ✅ **자동 컬럼 매핑**
            - 시간 관련: time, date, timestamp, 시간, 날짜
            - 온도 관련: temp, value, temperature, 온도, 값
            
            ✅ **데이터 전처리**
            - 자동 날짜/시간 변환
            - 결측치 제거
            - 시간순 정렬
            
            ✅ **실시간 분석**
            - 100개 레코드 단위 배치 분석
            - 온도 특성 라벨 자동 생성
            - 위험 수준 자동 분류
            """)
        
        st.warning("⚠️ **주의사항:**\n"
                  "- 파일 크기: 최대 200MB\n"
                  "- 지원 형식: CSV, JSON\n"
                  "- 인코딩: UTF-8 권장")

    def display_overview(self):
        """개요 대시보드"""
        st.header("📊 워터펌프 온도 분석 개요")
        
        if not self.data:
            return
        
        metadata = self.data['metadata']
        results = self.data['analysis_results']
        
        # 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 배치 수", metadata['total_batches'])
        
        with col2:
            st.metric("윈도우 크기", f"{metadata['window_size']} 레코드")
        
        with col3:
            alert_counts = {}
            for result in results:
                alert = result['alert_level']
                alert_counts[alert] = alert_counts.get(alert, 0) + 1
            
            critical_count = alert_counts.get('위험', 0) + alert_counts.get('주의', 0)
            st.metric("위험/주의 배치", critical_count)
        
        with col4:
            avg_temp = np.mean([r['statistics']['mean'] for r in results])
            st.metric("평균 온도", f"{avg_temp:.1f}°C")
    
    def display_temperature_trends(self):
        """온도 트렌드 시각화"""
        st.header("📈 온도 트렌드 분석")
        
        if not self.data:
            return
        
        results = self.data['analysis_results']
        
        # 시계열 데이터 준비
        timeline_data = []
        for result in results:
            timeline_data.append({
                'batch_id': result['batch_id'],
                'start_time': result['start_timestamp'],
                'mean_temp': result['statistics']['mean'],
                'max_temp': result['statistics']['max'],
                'min_temp': result['statistics']['min'],
                'value_label': result['value_label'],
                'alert_level': result['alert_level'],
                'trend': result['trend']
            })
        
        df = pd.DataFrame(timeline_data)
        df['start_time'] = pd.to_datetime(df['start_time'])
        
        # 온도 트렌드 차트
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['start_time'],
            y=df['mean_temp'],
            mode='lines+markers',
            name='평균 온도',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['start_time'],
            y=df['max_temp'],
            mode='lines',
            name='최고 온도',
            line=dict(color='red', width=1, dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=df['start_time'],
            y=df['min_temp'],
            mode='lines',
            name='최저 온도',
            line=dict(color='lightblue', width=1, dash='dash'),
            fill='tonexty'
        ))
        
        fig.update_layout(
            title="배치별 온도 변화 추이",
            xaxis_title="시간",
            yaxis_title="온도 (°C)",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 경고 수준별 분포
        alert_dist = df['alert_level'].value_counts()
        fig_pie = px.pie(
            values=alert_dist.values,
            names=alert_dist.index,
            title="경고 수준별 배치 분포",
            color_discrete_map={
                '정상': 'green',
                '관찰': 'yellow',
                '주의': 'orange',
                '위험': 'red'
            }
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # 라벨별 분포
            label_dist = df['value_label'].value_counts()
            fig_bar = px.bar(
                x=label_dist.index,
                y=label_dist.values,
                title="온도 특성 라벨별 분포"
            )
            fig_bar.update_xaxes(tickangle=45)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    def display_detailed_analysis(self):
        """상세 분석"""
        st.header("🔍 상세 분석")
        
        if not self.data:
            return
        
        results = self.data['analysis_results']
        
        # 배치 선택
        batch_options = [f"배치 {r['batch_id']}" for r in results]
        selected_batch = st.selectbox("분석할 배치를 선택하세요", batch_options)
        
        if selected_batch:
            batch_id = int(selected_batch.split()[1])
            batch_data = next(r for r in results if r['batch_id'] == batch_id)
            
            # 배치 정보 표시
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("배치 정보")
                st.write(f"**배치 ID**: {batch_data['batch_id']}")
                st.write(f"**시작 시간**: {batch_data['start_timestamp']}")
                st.write(f"**종료 시간**: {batch_data['end_timestamp']}")
                st.write(f"**레코드 수**: {batch_data['record_count']}")
                st.write(f"**온도 라벨**: {batch_data['value_label']}")
                st.write(f"**트렌드**: {batch_data['trend']}")
                st.write(f"**안정성**: {batch_data['stability']}")
                st.write(f"**경고 수준**: {batch_data['alert_level']}")
            
            with col2:
                st.subheader("통계 정보")
                stats = batch_data['statistics']
                st.write(f"**평균**: {stats['mean']:.2f}°C")
                st.write(f"**중앙값**: {stats['median']:.2f}°C")
                st.write(f"**표준편차**: {stats['std']:.2f}°C")
                st.write(f"**최솟값**: {stats['min']:.2f}°C")
                st.write(f"**최댓값**: {stats['max']:.2f}°C")
                st.write(f"**범위**: {stats['range']:.2f}°C")
            
            # 배치 내 온도 변화
            raw_data = batch_data['raw_data']
            df_raw = pd.DataFrame(raw_data)
            df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])
            
            fig_detail = px.line(
                df_raw,
                x='timestamp',
                y='value',
                title=f"배치 {batch_id} 상세 온도 변화",
                labels={'value': '온도 (°C)', 'timestamp': '시간'}
            )
            
            # 임계값 라인 추가
            fig_detail.add_hline(y=70, line_dash="dash", line_color="orange", annotation_text="주의 임계값")
            fig_detail.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="위험 임계값")
            
            st.plotly_chart(fig_detail, use_container_width=True)
    
    def display_export_options(self):
        """데이터 내보내기 옵션"""
        st.header("💾 데이터 내보내기")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 JSON 분석 결과")
            if st.button("📥 JSON 파일 다운로드"):
                import os
                
                # water_pump_data 폴더 확인
                data_folder = 'water_pump_data'
                if not os.path.exists(data_folder):
                    os.makedirs(data_folder)
                
                # 파일명 생성
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"water_pump_analysis_{timestamp}.json"
                
                json_str = json.dumps(self.data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="분석 결과 다운로드",
                    data=json_str,
                    file_name=filename,
                    mime="application/json"
                )
                
                # 로컬 저장도 수행
                full_path = os.path.join(data_folder, filename)
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 파일이 {full_path}에도 저장되었습니다!")
        
        with col2:
            st.subheader("📊 요약 리포트")
            if st.button("📋 리포트 생성"):
                report = self.generate_summary_report()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"pump_report_{timestamp}.txt"
                
                st.download_button(
                    label="요약 리포트 다운로드",
                    data=report,
                    file_name=filename,
                    mime="text/plain"
                )
                
                # 로컬 저장
                import os
                data_folder = 'water_pump_data'
                if not os.path.exists(data_folder):
                    os.makedirs(data_folder)
                
                full_path = os.path.join(data_folder, filename)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                st.success(f"✅ 리포트가 {full_path}에도 저장되었습니다!")
    
    def generate_summary_report(self):
        """요약 리포트 생성"""
        if not self.data:
            return "데이터가 없습니다."
        
        results = self.data['analysis_results']
        metadata = self.data['metadata']
        
        # 통계 계산
        all_temps = [r['statistics']['mean'] for r in results]
        alert_counts = {}
        for result in results:
            alert = result['alert_level']
            alert_counts[alert] = alert_counts.get(alert, 0) + 1
        
        report = f"""
워터펌프 온도 분석 리포트
=========================

분석 정보
---------
- 분석 일시: {metadata.get('analysis_date', 'N/A')}
- 총 배치 수: {metadata.get('total_batches', 'N/A')}개
- 윈도우 크기: {metadata.get('window_size', 'N/A')} 레코드

온도 통계
---------
- 평균 온도: {np.mean(all_temps):.1f}°C
- 최고 온도: {max([r['statistics']['max'] for r in results]):.1f}°C
- 최저 온도: {min([r['statistics']['min'] for r in results]):.1f}°C

경고 수준 분포
-----------
"""
        for level, count in alert_counts.items():
            percentage = (count / len(results)) * 100
            report += f"- {level}: {count}개 ({percentage:.1f}%)\n"
        
        # 위험 배치 상세
        critical_batches = [r for r in results if r['alert_level'] in ['위험', '주의']]
        if critical_batches:
            report += f"\n위험/주의 배치 상세\n"
            report += f"------------------\n"
            for batch in critical_batches:
                report += f"배치 {batch['batch_id']}: {batch['statistics']['mean']:.1f}°C ({batch['alert_level']})\n"
        
        return report

    def run(self):
        """메인 애플리케이션 실행"""
        st.title("🌡️ 워터펌프 온도 모니터링 시스템")
        
        # 데이터가 로드되지 않은 경우 가이드 표시
        if self.data is None:
            self.display_data_upload_guide()
            return
        
        # 사이드바 메뉴
        st.sidebar.header("📊 분석 메뉴")
        menu = st.sidebar.radio(
            "메뉴 선택",
            ["📈 개요", "📊 온도 트렌드", "🔍 상세 분석", "💾 데이터 내보내기"]
        )
        
        if menu == "📈 개요":
            self.display_overview()
        elif menu == "📊 온도 트렌드":
            self.display_temperature_trends()
        elif menu == "🔍 상세 분석":
            self.display_detailed_analysis()
        elif menu == "💾 데이터 내보내기":
            self.display_export_options()

# 애플리케이션 실행
if __name__ == "__main__":
    dashboard = StreamlitDashboard()
    dashboard.run()
