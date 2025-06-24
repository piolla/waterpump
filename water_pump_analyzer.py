import pandas as pd
import numpy as np
import json
from datetime import datetime
import statistics

class WaterPumpAnalyzer:
    def __init__(self):
        self.data = None
        self.analyzed_data = []
    
    def load_data(self, file_path=None, data=None, uploaded_file=None):
        """
        데이터 로드 (CSV 파일, 직접 데이터, 또는 업로드된 파일)
        예상 컬럼: timestamp, value
        """
        try:
            if uploaded_file is not None:
                # Streamlit 업로드된 파일 처리
                self.data = pd.read_csv(uploaded_file)
            elif file_path:
                self.data = pd.read_csv(file_path)
            elif data:
                self.data = pd.DataFrame(data)
            else:
                raise ValueError("데이터 소스가 제공되지 않았습니다.")
            
            # 컬럼명 확인 및 정규화
            if 'timestamp' not in self.data.columns or 'value' not in self.data.columns:
                # 컬럼명 자동 매핑 시도
                timestamp_cols = [col for col in self.data.columns if any(keyword in col.lower() for keyword in ['time', 'date', 'timestamp', '시간', '날짜'])]
                value_cols = [col for col in self.data.columns if any(keyword in col.lower() for keyword in ['temp', 'value', 'temperature', '온도', '값'])]
                
                if timestamp_cols and value_cols:
                    self.data = self.data.rename(columns={
                        timestamp_cols[0]: 'timestamp',
                        value_cols[0]: 'value'
                    })
                else:
                    # 첫 번째와 두 번째 컬럼을 timestamp, value로 가정
                    if len(self.data.columns) >= 2:
                        self.data.columns = ['timestamp', 'value'] + list(self.data.columns[2:])
                    else:
                        raise ValueError("timestamp와 value 컬럼을 찾을 수 없습니다.")
            
            # 데이터 타입 변환
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            self.data['value'] = pd.to_numeric(self.data['value'], errors='coerce')
            
            # 결측치 제거
            self.data = self.data.dropna()
            
            # 시간 순 정렬
            self.data = self.data.sort_values('timestamp').reset_index(drop=True)
            
            print(f"데이터 로드 완료: {len(self.data)}개 레코드")
            return True
            
        except Exception as e:
            print(f"데이터 로드 실패: {e}")
            return False
    
    def analyze_temperature_characteristics(self, window_size=100):
        """
        100개 레코드마다 온도 특성 분석하여 라벨 생성
        """
        self.analyzed_data = []
        
        for i in range(0, len(self.data), window_size):
            window_data = self.data.iloc[i:i+window_size]
            
            if len(window_data) == 0:
                continue
            
            # 기본 통계 분석
            temp_values = window_data['value'].values
            
            analysis = {
                'batch_id': i // window_size + 1,
                'start_timestamp': window_data['timestamp'].iloc[0].isoformat(),
                'end_timestamp': window_data['timestamp'].iloc[-1].isoformat(),
                'record_count': len(window_data),
                'statistics': {
                    'mean': float(np.mean(temp_values)),
                    'median': float(np.median(temp_values)),
                    'std': float(np.std(temp_values)),
                    'min': float(np.min(temp_values)),
                    'max': float(np.max(temp_values)),
                    'range': float(np.max(temp_values) - np.min(temp_values))
                },
                'raw_data': [
                    {
                        'timestamp': row['timestamp'].isoformat(),
                        'value': float(row['value'])
                    } for _, row in window_data.iterrows()
                ]
            }
            
            # 온도 특성 라벨 생성
            analysis['value_label'] = self._generate_temperature_label(analysis['statistics'])
            
            # 추가 특성 분석
            analysis['trend'] = self._analyze_trend(temp_values)
            analysis['stability'] = self._analyze_stability(analysis['statistics'])
            analysis['alert_level'] = self._determine_alert_level(analysis['statistics'])
            
            self.analyzed_data.append(analysis)
    
    def _generate_temperature_label(self, stats):
        """온도 통계를 바탕으로 라벨 생성"""
        mean_temp = stats['mean']
        std_temp = stats['std']
        temp_range = stats['range']
        
        # 온도 범위별 분류
        if mean_temp < 40:
            temp_category = "저온"
        elif mean_temp < 70:
            temp_category = "정상"
        elif mean_temp < 85:
            temp_category = "고온"
        else:
            temp_category = "과열"
        
        # 변동성 분류
        if std_temp < 2:
            stability = "안정"
        elif std_temp < 5:
            stability = "보통"
        else:
            stability = "불안정"
        
        # 범위 분류
        if temp_range < 5:
            range_category = "일정"
        elif temp_range < 15:
            range_category = "변동"
        else:
            range_category = "급변"
        
        return f"{temp_category}_{stability}_{range_category}"
    
    def _analyze_trend(self, values):
        """온도 트렌드 분석"""
        if len(values) < 2:
            return "불충분"
        
        # 선형 회귀를 통한 트렌드 분석
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "상승"
        elif slope < -0.1:
            return "하강"
        else:
            return "평형"
    
    def _analyze_stability(self, stats):
        """안정성 분석"""
        cv = stats['std'] / stats['mean'] if stats['mean'] > 0 else 0
        
        if cv < 0.05:
            return "매우안정"
        elif cv < 0.1:
            return "안정"
        elif cv < 0.2:
            return "보통"
        else:
            return "불안정"
    
    def _determine_alert_level(self, stats):
        """경고 수준 결정"""
        mean_temp = stats['mean']
        max_temp = stats['max']
        
        if max_temp > 90 or mean_temp > 85:
            return "위험"
        elif max_temp > 80 or mean_temp > 75:
            return "주의"
        elif max_temp > 70 or mean_temp > 65:
            return "관찰"
        else:
            return "정상"
    
    def save_to_json(self, output_file='water_pump_analysis.json'):
        """분석 결과를 JSON 파일로 저장"""
        output_data = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'total_batches': len(self.analyzed_data),
                'window_size': 100,
                'data_source': 'water_pump_temperature_sensor'
            },
            'analysis_results': self.analyzed_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"분석 결과가 {output_file}에 저장되었습니다.")
        return output_file

# 사용 예제
if __name__ == "__main__":
    # 샘플 데이터 생성 (실제 사용시에는 실제 데이터 사용)
    sample_data = []
    base_time = datetime.now()
    
    for i in range(500):  # 500개 샘플 데이터
        timestamp = base_time + pd.Timedelta(minutes=i*10)
        # 시간대별로 다른 온도 패턴 생성
        if i < 100:
            temp = 45 + np.random.normal(0, 2)  # 정상 운영
        elif i < 200:
            temp = 60 + np.random.normal(0, 3)  # 부하 증가
        elif i < 300:
            temp = 75 + np.random.normal(0, 5)  # 고온 운영
        elif i < 400:
            temp = 85 + np.random.normal(0, 4)  # 과열 위험
        else:
            temp = 50 + np.random.normal(0, 2)  # 정상 복귀
        
        sample_data.append({
            'timestamp': timestamp,
            'value': max(20, min(100, temp))  # 20-100도 범위 제한
        })
    
    # 분석기 실행
    analyzer = WaterPumpAnalyzer()
    analyzer.load_data(data=sample_data)
    analyzer.analyze_temperature_characteristics()
    analyzer.save_to_json('water_pump_analysis.json')
