# Selenium : Web Browser를 자동화하는 도구. Crawling을 위해서 필요.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
# BeautifulSoup : HTML 문서를 parsing해서 원하는 정보를 쉽게 추출할 수 있는 library.
from bs4 import BeautifulSoup
# pandas : 데이터 분석 library. Crawling한 데이터를 표 형태로 저장하고, .csv 파일로 저장하거나 분석할 수 있다.
import pandas as pd

# Todo(게시판 투수 기록 크롤링)
# 웹에 보일 타자 기록 : 선수 이름, 선수 팀 이름, 평균자책점, 경기, 승리, 패배, 세이브, 홀드, 이닝, 피안타, 피홈런, 볼넷, 탈삼진, 실점, 자책점
# URL1 기록 : 선수 이름, 선수 팀 이름, 평균자책점, 경기, 승리, 패배, 세이브, 홀드, 이닝, 피안타, 피홈런, 볼넷, 탈삼진, 실점, 자책점
# URL2 기록 : 없음.
# => URL1 데이터랑 URL2 데이터를 합치는 작업이 필요 없음.

# 특이 사항 : 평균자책점은 규정 이닝은 채워야 한다. -> 규정 이닝 = 경기 수.
# -> 그럼 이것은 mapper에서 평균자책점을 가져올 때 where 절로 계산한다. -> 방법 1로 하자. -> DB에 "웹에 보일 xntn 기록" 이외로 넣을 스탯이 없다.

# 버튼 누르면 스탯 순서로 n명 웹에 나열 :
# 방법 : 스탯 크롤링 -> csv 저장 -> DB 저장 -> backend mapper로 DB에서 스탯순으로 가져옴.

# 그러면 할 것 :
# 1. 연도 바꾸기 (완)
# 2. 파일 이름 바꾸기 (완)
# 3. URL1에서 필요한 기록만 가져오기 -> data dictionary 변경 (완)
# 4. URL2과 관련된 코드 삭제. (완)
# 5. 바뀐 data dictionary에 맞게 numeric_cols_float와 numeric_cols_int 리스트 값들 변경. (완)

# --- 설정 ---
URL1 = "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?sort=ERA_RT"
CHROME_DRIVER_PATH = './chromedriver.exe' # chromedriver.exe 파일 경로

# 팀 정보: {팀명(소문자): 팀 코드}. Dictionary이다.
teams = {
    'doosan': 'OB',
    'hanhwa': 'HH',
    'lg': 'LG',
    'lotte': 'LT',
    'kia': 'HT',
    'ssg': 'SK',
    'kt': 'KT',
    'samsung': 'SS',
    'nc': 'NC',
    'kiwoom': 'WO'
}

# URL에서 crawling한 선수 데이터를 넣을 list.
player_data1 = []

# Service 객체 : Chrome driver를 실행하고, 그 실행 상태를 관리.
service = Service(CHROME_DRIVER_PATH)
# Options : Chrome driver 실행 옵션을 설정.
options = Options()
# Browser 창을 띄우지 않고 background에서 실행
options.add_argument("--headless")
# GPU 가속 기능을 끈다.
options.add_argument("--disable-gpu")
# 브라우저 창 크기를 가로 1920, 세로 1080 픽셀로 설정
options.add_argument("--window-size=1920x1080")
# 위에서 설정한 service와 options를 기반으로 Chrome browser를 실행
driver = webdriver.Chrome(service=service, options=options)
# 특정 요소가 나타날 때까지 최대 20초 동안 기다리는 설정
wait = WebDriverWait(driver, 20)
print("브라우저 및 WebDriver 초기화 완료.")

try: 
    # ==================== URL1 (PitcherBasic/Basic1.aspx) 데이터 수집 ====================
    print("\n========== Basic1 (투수) 데이터 수집 시작 ==========")


    for team_name, team_code in teams.items():
        print(f"\n==================== {team_name.upper()} 팀 Basic1 (투수) 데이터 수집 중 ====================")

        # teams dictionary에서 key, value를 가져와 그것들을 기준으로 반복문을 돌림.
        try:
            # URL1에 접속한다.
            driver.get(URL1)
            print("페이지 접속 완료")

            # CSS selector를 이용해 찾고자 하는 table의 위치를 지정
            table_locator = (By.CSS_SELECTOR, "table.tData01.tt")
            # table_locator가 Web page에 나타날 때까지 (최대 20초) 기다린다.
            wait.until(EC.presence_of_element_located(table_locator))
            print("Basic1 페이지 접속 완료")

            # 연도 선택
            # Dropdown(select tag)가 나타날 때까지 기다린다. ID는 연도를 고르는 select 요소의 ID.
            year_select_element = wait.until(EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlSeason_ddlSeason")))
            # Selenium의 Select class를 사용해서 Dropdown 메뉴를 제어할 수 있게 변환한다.
            year_select = Select(year_select_element)

            # 현재 선택된 연도 확인
            current_selected_year = year_select.first_selected_option.get_attribute("value")

            if current_selected_year == "2025":
                print("연도: 2025년이 이미 선택되어 있습니다. 연도 변경을 건너뜀.")
                # 이미 2025년이 선택되어 있어도, 테이블이 로드되었는지 확인합니다.
                wait.until(EC.presence_of_element_located(table_locator))
            else:
                print(f"현재 선택된 연도: {current_selected_year}. 2025년으로 변경합니다.")
                try:
                    table_before_change = driver.find_element(*table_locator)
                except StaleElementReferenceException:
                    table_before_change = wait.until(EC.presence_of_element_located(table_locator))

                year_select.select_by_value("2025")
                print("연도 선택: 2025")
                try:
                    wait.until(EC.staleness_of(table_before_change))
                except TimeoutException:
                    print("Warning: 기존 테이블이 Stale 상태가 되는 데 타임아웃 발생. 하지만 진행합니다.")
                wait.until(EC.presence_of_element_located(table_locator))

            print("연도 선택 프로세스 완료.")

            # 팀 선택
            # Dropdown(select tag)가 나타날 때까지 기다린다. ID는 team을 고르는 select 요소의 ID.
            team_select_element = wait.until(EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlTeam_ddlTeam")))
            # Selenium의 Select class를 사용해서 Dropdown 메뉴를 제어할 수 있게 변환한다.
            team_select = Select(team_select_element)
            # 팀 선택 전의 table 요소를 저장. 기다렸다가 찾기.
            table_before_change = wait.until(EC.presence_of_element_located(table_locator))
            # Dropdown에서 value=team_code인 항목을 선택
            team_select.select_by_value(team_code)
            print(f"팀 선택: {team_name.upper()} ({team_code})")
            # 기존의 table 요소가 사라질 때까지 대기한다.
            wait.until(EC.staleness_of(table_before_change))
            # 새로 로딩된 table이 다시 나타날 때까지 기다린다.
            wait.until(EC.presence_of_element_located(table_locator))
            print("최종 테이블 로딩 완료 (Basic1 - 데이터 로딩 확인)")

            # 데이터 추출
            # 현재 page의 전체 HTML source code를 문자열로 가져온다.
            html = driver.page_source
            # html.parser를 이용해 HTML을 parsing할 수 있는 BeautifulSoup 객체를 생성.
            soup = BeautifulSoup(html, 'html.parser')
            # 클래스명이 "tData01 tt"인 <table> 요소를 찾는다.
            table = soup.find('table', {'class': 'tData01 tt'})
            # table의 <tbody> tag를 가져온다.
            table_body = table.find('tbody')
            # <tbody> 내부의 모든 <tr> 요소들을 list로 가져온다.
            rows = table_body.find_all('tr')

           # table_body.find_all('tr')로 가져온 각 행(<tr>)을 하나씩 순회한다,
            for row in rows:
                # 행 안의 모든 <td>를 리스트로 추출한다.
                cols = row.find_all('td')

                # Basic1.aspx의 경우 19개 컬럼 예상 (0부터 시작)
                if len(cols) < 19: 
                    continue

                rank_text = cols[0].get_text(strip=True)
                # isdigit()으로 숫자인지 확인한다. 숫자가 아니면 데이터 행이 아니므로 건너뛴다.
                if not rank_text.isdigit(): 
                    continue

                data = {
                    'Player_Name': cols[1].get_text(strip=True), # 선수 이름
                    'Player_Team': cols[2].get_text(strip=True), # 선수 팀 이름
                    'Earned_Run_Average': cols[3].get_text(strip=True), # 평균자책점
                    'Game_Num': cols[4].get_text(strip=True), # 경기 수
                    'Win': cols[5].get_text(strip=True), # 승
                    'Lose': cols[6].get_text(strip=True), # 패
                    'Save': cols[7].get_text(strip=True), # 세이브
                    'Hold': cols[8].get_text(strip=True), # 홀드
                    'Innings_Pitched': cols[10].get_text(strip=True), # 이닝
                    'Hits': cols[11].get_text(strip=True), # 피안타
                    'Home_Run': cols[12].get_text(strip=True), # 피홈런
                    'Base_On_Balls': cols[13].get_text(strip=True), # 볼넷
                    'Strike_Out': cols[15].get_text(strip=True), # 탈삼진
                    'Runs': cols[16].get_text(strip=True), # 실점
                    'Earned_Run': cols[17].get_text(strip=True), # 자책점
                    'WHIP': cols[18].get_text(strip=True),
                }
                # data dictionary의 내용을 player_data1 list에 넣는다.
                player_data1.append(data)

            print(f"{team_name.upper()} Basic1 데이터 추출 완료. 현재까지 추출된 선수 수: {len(player_data1)}")

        except Exception as e:
            print(f"Basic1.aspx 크롤링 중 오류 발생 ({team_name.upper()} 팀): {e}")

    # player_data1 list를 DataFrame으로 변환
    if player_data1:
        # player_data1 list를 pandas.DataFrame으로 변환하여 표 형태의 DataFrame으로 만든다.
        df1 = pd.DataFrame(player_data1)
        # Player_Name와 Player_Team을 기준으로 중복된 행을 제거
        # inplace=True : 원본 DataFrame을 직접 수정.
        df1.drop_duplicates(subset=['Player_Name', 'Player_Team'], inplace=True)
        print(f"최종 df1 생성 완료. 행 수: {len(df1)}")
    else:
        print("Basic1.aspx에서 저장할 데이터가 없습니다.")
        # 빈 DataFrame 생성하여 merge 오류 방지.
        df1 = pd.DataFrame() 

    # ==================== 데이터 타입 변환 및 CSV 저장 (df1만 사용) ====================

    if not df1.empty:
        print("\n--- 데이터 타입 변환 및 CSV 저장 시작 ---")

        # 야구 투구 이닝 기록 문자열을 받아서, 이를 소수점 형태의 숫자(실수)로 변환해주는 함수
        def convert_innings_pitched(inning_str):
            # 입력 값이 NaN이거나 빈 문자열일 경우
            if pd.isna(inning_str) or inning_str.strip() == '':
                return None
            try:
                # 공백 제거 (앞뒤 여백을 모두 제거해서 깔끔한 문자열로 만듦).
                inning_str = inning_str.strip()

                # 1. 정수 형태 (예: '11')
                # 문자열에 분수 기호 /와 공백이 없으면
                if '/' not in inning_str and ' ' not in inning_str:
                    return round(float(inning_str), 3)

                # 분수 처리를 위해 문자열을 공백(' ') 기준으로 분리(split())해서 parts list를 만듦.
                parts = inning_str.split()

                # 2. 정수 + 분수 (예: '39 1/3')
                if len(parts) == 2:
                    full = int(parts[0])
                    numerator, denominator = map(int, parts[1].split('/'))
                    return round(full + numerator / denominator, 3)

                # 3. 분수만 있는 경우 (예: '1/3')
                elif len(parts) == 1 and '/' in parts[0]:
                    numerator, denominator = map(int, parts[0].split('/'))
                    return round(numerator / denominator, 3)

                else:
                    return None
                
            except Exception:
                return None

        if 'Innings_Pitched' in df1.columns:
            df1['Innings_Pitched'] = df1['Innings_Pitched'].astype(str)
            # apply()가 컬럼의 각 원소를 함수 인자로 넣어 호출하는 방식을 자동으로 처리하기 때문에, 호출할 때 인자를 따로 적지 않아도 문제없다.
            df1['Innings_Pitched'] = df1['Innings_Pitched'].apply(convert_innings_pitched)

        numeric_cols_float = [
            'Earned_Run_Average', 'WHIP'
        ]
        numeric_cols_int = [
            'Game_Num', 'Win', 'Lose', 'Save', 'Hold', 'Hits', 'Home_Run',
            'Base_On_Balls', 'Strike_Out', 'Runs', 'Earned_Run',
        ]

        for col in numeric_cols_float:
            if col in df1.columns:
                 # errors='coerce' : '-' 등은 NaN으로
                # .fillna(0) : NaN 값을 0으로 채움
                # .astype(float) : 최종적으로 정수형(float) 으로 변환
                df1[col] = pd.to_numeric(df1[col], errors='coerce').fillna(0).astype(float)

        for col in numeric_cols_int:
            if col in df1.columns:
                # .astype(int) : 최종적으로 정수형(int) 으로 변환
                df1[col] = pd.to_numeric(df1[col], errors='coerce').fillna(0).astype(int)

        if 'Innings_Pitched' in df1.columns:
            df1['Innings_Pitched'] = pd.to_numeric(df1['Innings_Pitched'], errors='coerce').fillna(0).astype(float)

        print("데이터 타입 변환 완료.")

        # Game_Num이 0인 데이터 삭제
        initial_rows = len(df1)
        df1 = df1[df1['Game_Num'] > 0]
        deleted_rows = initial_rows - len(df1)
        if deleted_rows > 0:
            print(f"Game_Num이 0인 {deleted_rows}개의 선수 데이터가 삭제되었습니다.")
        else:
            print("Game_Num이 0인 선수 데이터가 없습니다.")
        # df1 Dataframe의 맨 위 5개 행을 출력.
        print(df1.head())
        print(f"최종 처리된 데이터의 행 수: {len(df1)}, 컬럼 수: {len(df1.columns)}")

        # CSV 파일로 저장
        csv_filename = "2025_useBoard_pitcher.csv"
        df1.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"\n'{csv_filename}' 파일이 성공적으로 저장되었습니다.")

    else:
        print("\n데이터프레임이 비어있어 CSV 저장 작업을 수행할 수 없습니다.")

finally:
    # 모든 크롤링 작업이 완료된 후 드라이버를 종료합니다.
    driver.quit()
    print("\n전체 크롤링 완료. 브라우저 종료됨")