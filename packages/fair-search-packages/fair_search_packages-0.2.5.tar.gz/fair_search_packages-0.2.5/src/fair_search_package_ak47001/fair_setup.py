import os
import yaml
import pymysql
from langchain_teddynote import logging
from langchain_openai import ChatOpenAI
from langsmith import Client
from datetime import timedelta, datetime
import random

""""
config_path에 있는 yaml 파일 기반 프로그램 설정 
- open api키 등록
- langsmith 플랫폼에 프로젝트 등록(추적 및 분석)
"""
def set_env(config_path='config.yaml', project_name='fairness'):
    config_path = os.path.abspath(config_path)

    # 필수값 체크용 딕셔너리 (환경변수명, config key)
    env_map = {
        'OPENAI_API_KEY': 'OPEN_API_KEY',
        'LANGSMITH_API_KEY': 'LANGSMITH_API_KEY',
        'LANGSMITH_TRACING': 'LANGSMITH_TRACING',
        'LANGSMITH_ENDPOINT': 'LANGSMITH_ENDPOINT',
        'HUGGINGFACEHUB_API_TOKEN' : 'HUGGINGFACEHUB_API_TOKEN',
        'SENTENCE_EMBEDDING_MODEL' : 'SENTENCE_EMBEDDING_MODEL',
    }

    # config 파일 로딩 및 예외처리
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print(f"[ERROR] 설정 파일({config_path})을 찾을 수 없습니다.")
        return None
    except yaml.YAMLError:
        print(f"[ERROR] 설정 파일({config_path})이 올바른 YAML 형식이 아닙니다.")
        return None

    # 환경변수 세팅 (없으면 경고)
    for env_key, config_key in env_map.items():
        value = config.get(config_key, None)
        if value is not None:
            os.environ[env_key] = str(value)
        else:
            print(f"[WARNING] '{config_key}' 값이 설정 파일에 없습니다. 해당 환경변수는 세팅되지 않습니다.")

    """ 추가설정, Corpus Graph + Lanchain Vector Store 저장 경로 등록"""
    try:
        os.environ['SOURCE_STORE_PATH'] = config['vector_store']['source']['path']
        os.environ["CLUSTER_STORE_PATH"] = config['vector_store']['cluster']['path']
        os.environ["ORIGINAL_STORE_PATH"] = config['vector_store']['original']['path']
        os.environ["BM25_STORE_PATH"] = config['bm25_store']['path']
        os.environ["GRAPH_PATH"] = config['corpus_graph']['path']
    except:
        print("Vector Store 혹은 Corpus Graph를 생성 후 실행")
        exit(0)

    print("[INFO] 환경변수 세팅이 완료되었습니다.")
    logging.langsmith(project_name=project_name)
    

"""
    데이터베이스 연결 후 인스턴스 반환
"""
def connect_mysql_database(config_path, database_name):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)['database']
    except FileNotFoundError:
        print(f"[ERROR] 설정 파일({config_path})을 찾을 수 없습니다.")
        return
    except yaml.YAMLError:
        print(f"[ERROR] 설정 파일({config_path})이 올바른 YAML 형식이 아닙니다.")
        return    
    return pymysql.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                charset="utf8mb4",
                database=database_name
            )

def get_client_chain(prompt_model_name:str):
    config_path = os.environ['CONFIG_PATH']
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        client = Client(api_key=config['LANGSMITH_API_KEY'])
        # 모델 포함 리턴
        prompt = client.pull_prompt(prompt_model_name, include_model=True)
        return prompt
    except Exception as e:
        print(f'Client error {e}')

def timer(func):
    import time
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        sec = end_time - start_time
        time_result = timedelta(seconds=sec)
        time_result = str(timedelta(seconds=sec)).split(".")
        print(f"{func.__name__} 함수 실행 시간: {sec:.2f} 초 ({time_result[0]})")
        return result
    return wrapper

def check_package():
    print("Succsssfully include fair-setup package ! ! !")

def random_datetime():
    """
    최근 1년간의 랜덤 날짜/시간을 반환.
    - 출력 형식: %y-%m-%d:%H  (예: 25-05-09:11)
    """
    now = datetime.now()
    # 365일 전부터 현재까지 중 랜덤 offset
    delta_days = random.randint(0, 365)
    delta_hours = random.randint(0, 23)
    delta_minutes = random.randint(0, 59)
    random_time = now - timedelta(days=delta_days, hours=delta_hours, minutes=delta_minutes)
    return random_time.strftime("%y-%m-%d:%H")

# 실행 예시
if __name__ == "__main__":
    # 이는 일시적인 환경변수 적용일뿐이다.
    set_env('config.json')
    # llm = load_gpt_model('config.json')