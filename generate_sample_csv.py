#!/usr/bin/env python3
"""
워터펌프 온도 데이터 샘플 CSV 파일 생성기

다양한 시나리오의 워터펌프 온도 데이터를 생성하여 테스트에 활용할 수 있습니다.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse

def generate_normal_operation(start_time, duration_hours=24, interval_minutes=10):
    """정상 운영 데이터 생성"""
    data = []
    current_time = start_time
    end_time = start_time + timedelta(hours=duration_hours)
    
    base_temp = 55  # 기본 온도
    
    while current_time < end_time:
        # 시간대별 온도 변화 (낮에는 약간 높고, 밤에는 낮음)
        hour = current_time.hour
        daily_variation = 5 * np.sin((hour - 6) * np.pi / 12)
        
        # 랜덤 노이즈
        noise = np.random.normal(0, 2)
        
        temperature = base_temp + daily_variation + noise
        temperature = max(35, min(75, temperature))  # 35-75도 범위 제한
        
        data.append({
            'timestamp': current_time,
            'value': round(temperature, 1)
        })
        
        current_time += timedelta(minutes=interval_minutes)
    
    return data

def generate_overheating_scenario(start_time, duration_hours=4, interval_minutes=10):
    """과열 시나리오 데이터 생성"""
    data = []
    current_time = start_time
    end_time = start_time + timedelta(hours=duration_hours)
    
    base_temp = 60
    
    while current_time < end_time:
        # 시간이 지날수록 온도 상승
        elapsed_hours = (current_time - start_time).total_seconds() / 3600
        overheating = min(30, elapsed_hours * 8)  # 시간당 8도씩 상승, 최대 30도
        
        # 불안정한 변동
        instability = np.random.normal(0, 3 + elapsed_hours)
        
        temperature = base_temp + overheating + instability
        temperature = max(40, min(100, temperature))  # 40-100도 범위
        
        data.append({
            'timestamp': current_time,
            'value': round(temperature, 1)
        })
        
        current_time += timedelta(minutes=interval_minutes)
    
    return data

def generate_maintenance_cycle(start_time, duration_hours=8, interval_minutes=10):
    """정비 사이클 데이터 생성 (정지 → 재시작 → 안정화)"""
    data = []
    current_time = start_time
    end_time = start_time + timedelta(hours=duration_hours)
    
    while current_time < end_time:
        elapsed_hours = (current_time - start_time).total_seconds() / 3600
        
        if elapsed_hours < 1:  # 첫 1시간: 정지 상태
            temperature = 25 + np.random.normal(0, 2)
        elif elapsed_hours < 2:  # 1-2시간: 재시작 및 워밍업
            warmup_progress = (elapsed_hours - 1)
            temperature = 25 + warmup_progress * 30 + np.random.normal(0, 5)
        else:  # 2시간 후: 정상 운영으로 안정화
            stabilization = min(1, (elapsed_hours - 2) / 2)
            target_temp = 55
            current_variation = (1 - stabilization) * 10
            temperature = target_temp + np.random.normal(0, 2 + current_variation)
        
        temperature = max(20, min(80, temperature))
        
        data.append({
            'timestamp': current_time,
            'value': round(temperature, 1)
        })
        
        current_time += timedelta(minutes=interval_minutes)
    
    return data

def generate_load_variation(start_time, duration_hours=12, interval_minutes=10):
    """부하 변동 시나리오 (생산량에 따른 온도 변화)"""
    data = []
    current_time = start_time
    end_time = start_time + timedelta(hours=duration_hours)
    
    while current_time < end_time:
        elapsed_hours = (current_time - start_time).total_seconds() / 3600
        
        # 생산 스케줄에 따른 부하 변동 (사인파 패턴)
        load_cycle = 0.5 + 0.4 * np.sin(elapsed_hours * np.pi / 4)  # 8시간 주기
        
        # 급격한 부하 변화 시뮬레이션
        if elapsed_hours > 6 and elapsed_hours < 7:
            load_cycle += 0.3  # 급격한 부하 증가
        
        base_temp = 50
        load_impact = load_cycle * 25  # 부하에 따른 온도 영향
        
        # 부하 변화에 따른 불안정성
        instability = np.random.normal(0, 2 + load_cycle * 3)
        
        temperature = base_temp + load_impact + instability
        temperature = max(30, min(90, temperature))
        
        data.append({
            'timestamp': current_time,
            'value': round(temperature, 1)
        })
        
        current_time += timedelta(minutes=interval_minutes)
    
    return data

def generate_seasonal_pattern(start_time, duration_days=7, interval_minutes=30):
    """계절적 패턴 데이터 (환경 온도 영향)"""
    data = []
    current_time = start_time
    end_time = start_time + timedelta(days=duration_days)
    
    while current_time < end_time:
        elapsed_days = (current_time - start_time).total_seconds() / (24 * 3600)
        
        # 일일 온도 변화 (낮과 밤)
        hour = current_time.hour
        daily_variation = 8 * np.sin((hour - 6) * np.pi / 12)
        
        # 주간 트렌드 (점진적 온도 상승)
        weekly_trend = elapsed_days * 2
        
        # 환경 온도 영향
        ambient_effect = np.random.normal(0, 3)
        
        base_temp = 52
        temperature = base_temp + daily_variation + weekly_trend + ambient_effect
        temperature = max(35, min(80, temperature))
        
        data.append({
            'timestamp': current_time,
            'value': round(temperature, 1)
        })
        
        current_time += timedelta(minutes=interval_minutes)
    
    return data

def generate_combined_scenario():
    """복합 시나리오: 여러 상황을 조합한 현실적인 데이터"""
    start_time = datetime.now() - timedelta(days=2)
    all_data = []
    
    # 1일차: 정상 운영
    normal_data = generate_normal_operation(start_time, duration_hours=20)
    all_data.extend(normal_data)
    
    # 과열 이벤트
    overheat_start = start_time + timedelta(hours=20)
    overheat_data = generate_overheating_scenario(overheat_start, duration_hours=4)
    all_data.extend(overheat_data)
    
    # 2일차: 정비 후 재시작
    maintenance_start = start_time + timedelta(days=1)
    maintenance_data = generate_maintenance_cycle(maintenance_start, duration_hours=8)
    all_data.extend(maintenance_data)
    
    # 부하 변동 운영
    load_start = start_time + timedelta(days=1, hours=8)
    load_data = generate_load_variation(load_start, duration_hours=16)
    all_data.extend(load_data)
    
    return all_data

def save_to_csv(data, filename):
    """데이터를 CSV 파일로 저장"""
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    df.to_csv(filename, index=False)
    print(f"✅ {filename} 파일이 생성되었습니다. ({len(df)}개 레코드)")
    
    # 통계 정보 출력
    print(f"   📊 기간: {df['timestamp'].min()} ~ {df['timestamp'].max()}")
    print(f"   🌡️  온도 범위: {df['value'].min():.1f}°C ~ {df['value'].max():.1f}°C")
    print(f"   📈 평균 온도: {df['value'].mean():.1f}°C")

def main():
    parser = argparse.ArgumentParser(description="워터펌프 온도 샘플 데이터 생성기")
    parser.add_argument('--scenario', choices=[
        'normal', 'overheating', 'maintenance', 'load_variation', 
        'seasonal', 'combined'
    ], default='combined', help='생성할 시나리오 선택')
    parser.add_argument('--output', default='sample_water_pump_data.csv', 
                       help='출력 파일명')
    parser.add_argument('--duration', type=int, default=48, 
                       help='데이터 생성 시간 (시간 단위)')
    
    args = parser.parse_args()
    
    print(f"🔧 {args.scenario} 시나리오 데이터 생성 중...")
    
    start_time = datetime.now() - timedelta(hours=args.duration)
    
    if args.scenario == 'normal':
        data = generate_normal_operation(start_time, args.duration)
    elif args.scenario == 'overheating':
        data = generate_overheating_scenario(start_time, args.duration)
    elif args.scenario == 'maintenance':
        data = generate_maintenance_cycle(start_time, args.duration)
    elif args.scenario == 'load_variation':
        data = generate_load_variation(start_time, args.duration)
    elif args.scenario == 'seasonal':
        data = generate_seasonal_pattern(start_time, duration_days=args.duration//24)
    else:  # combined
        data = generate_combined_scenario()
    
    save_to_csv(data, args.output)
    
    print(f"\n🚀 사용법:")
    print(f"   streamlit run chatbot_implementation.py")
    print(f"   또는 python run.py --chatbot")
    print(f"   그 후 사이드바에서 '{args.output}' 파일을 업로드하세요!")

if __name__ == "__main__":
    main()
