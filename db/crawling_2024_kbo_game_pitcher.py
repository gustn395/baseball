# Selenium : Web Browser를 자동화하는 도구. Crawling을 위해서 필요.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# BeautifulSoup : HTML 문서를 parsing해서 원하는 정보를 쉽게 추출할 수 있는 library.
from bs4 import BeautifulSoup
# pandas : 데이터 분석 library. Crawling한 데이터를 표 형태로 저장하고, .csv 파일로 저장하거나 분석할 수 있다.
import pandas as pd

# --- 설정 ---
URL1 = "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx?sort=ERA_RT"
URL2 = "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic2.aspx?sort=ERA_RT"
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
player_data2 = []

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

    # teams dictionary에서 key, value를 가져와 그것들을 기준으로 반복문을 돌림.
    for team_name, team_code in teams.items():
        print(f"\n==================== {team_name.upper()} 팀 Basic1 (투수) 데이터 수집 중 ====================")

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
            # 연도를 바꾸기 전의 table 요소를 저장. 즉시 찾기
            table_before_change = driver.find_element(*table_locator)
            # Dropdown에서 value="2024"인 항목을 선택한다.
            year_select.select_by_value("2024")
            # 기존의 table 요소가 사라질 때까지 대기한다.
            wait.until(EC.staleness_of(table_before_change))
            # 새로 로딩된 table이 다시 나타날 때까지 기다린다.
            wait.until(EC.presence_of_element_located(table_locator))
            print("연도 선택: 2024")
            
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
                    'Player_Name': cols[1].get_text(strip=True),
                    'Player_Team': cols[2].get_text(strip=True),
                    'Earned_Run_Average': cols[3].get_text(strip=True),
                    'Game_Num': cols[4].get_text(strip=True),
                    'Win': cols[5].get_text(strip=True),
                    'Lose': cols[6].get_text(strip=True),
                    'Save': cols[7].get_text(strip=True),
                    'Hold': cols[8].get_text(strip=True),
                    'Winning_Percentage': cols[9].get_text(strip=True),
                    'Innings_Pitched': cols[10].get_text(strip=True),
                    'Hits': cols[11].get_text(strip=True),
                    'Home_Run': cols[12].get_text(strip=True),
                    'Base_On_Balls': cols[13].get_text(strip=True),
                    'Hit_By_Pitch': cols[14].get_text(strip=True),
                    'Strike_Out': cols[15].get_text(strip=True),
                    'Runs': cols[16].get_text(strip=True),
                    'Earned_Run': cols[17].get_text(strip=True),
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

    # ==================== URL2 (PitcherBasic/Basic2.aspx) 데이터 수집 ====================
    print("\n========== Basic2 (투수) 데이터 수집 시작 ==========")
    # teams dictionary에서 key, value를 가져와 그것들을 기준으로 반복문을 돌림.
    for team_name, team_code in teams.items():
        print(f"\n==================== {team_name.upper()} 팀 Basic2 (투수) 데이터 수집 중 ====================")

        try:
            # URL2에 접속한다.
            driver.get(URL2)
            print("페이지 접속 완료")

            # CSS selector를 이용해 찾고자 하는 table의 위치를 지정
            table_locator = (By.CSS_SELECTOR, "table.tData01.tt")
            # table_locator가 Web page에 나타날 때까지 (최대 20초) 기다린다.
            wait.until(EC.presence_of_element_located(table_locator))
            print("Basic2 페이지 접속 완료")

            # 연도 선택
            # Dropdown(select tag)가 나타날 때까지 기다린다. ID는 연도를 고르는 select 요소의 ID.
            year_select_element = wait.until(EC.presence_of_element_located((By.ID, "cphContents_cphContents_cphContents_ddlSeason_ddlSeason")))
            # Selenium의 Select class를 사용해서 Dropdown 메뉴를 제어할 수 있게 변환한다.
            year_select = Select(year_select_element)
            # 연도를 바꾸기 전의 table 요소를 저장. 즉시 찾기
            table_before_change = driver.find_element(*table_locator)
            # Dropdown에서 value="2024"인 항목을 선택한다.
            year_select.select_by_value("2024")
            # 기존의 table 요소가 사라질 때까지 대기한다.
            wait.until(EC.staleness_of(table_before_change))
            # 새로 로딩된 table이 다시 나타날 때까지 기다린다.
            wait.until(EC.presence_of_element_located(table_locator))
            print("연도 선택: 2024")

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
            print("최종 테이블 로딩 완료 (Basic2 - 데이터 로딩 확인 포함)")

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

            # table_body.find_all('tr')로 가져온 각 행(<tr>)을 하나씩 순회한다.
            for row in rows:
                # 행 안의 모든 <td>를 리스트로 추출한다.
                cols = row.find_all('td')

                # Basic2.aspx의 경우 19개 컬럼 예상
                if len(cols) < 18:
                    continue

                rank_text = cols[0].get_text(strip=True)
                # isdigit()으로 숫자인지 확인한다. 숫자가 아니면 데이터 행이 아니므로 건너뛴다.
                if not rank_text.isdigit():
                    continue

                data = {
                    'Player_Name': cols[1].get_text(strip=True),
                    'Player_Team': cols[2].get_text(strip=True),
                    'Earned_Run_Average': cols[3].get_text(strip=True),
                    'Complete_Game': cols[4].get_text(strip=True),
                    'Shutout': cols[5].get_text(strip=True),
                    'Quality_Start': cols[6].get_text(strip=True),
                    'Blown_Save': cols[7].get_text(strip=True),
                    'Total_Batters_Faced': cols[8].get_text(strip=True),
                    'Number_Of_Pitching': cols[9].get_text(strip=True),
                    'Opponent_Batting_Average': cols[10].get_text(strip=True),
                    '2Base': cols[11].get_text(strip=True),
                    '3Base': cols[12].get_text(strip=True),
                    'Sacrifice_Bunt': cols[13].get_text(strip=True),
                    'Sacrifice_Fly': cols[14].get_text(strip=True),
                    'IBB': cols[15].get_text(strip=True),
                    'Wild_Pitch': cols[16].get_text(strip=True),
                    'Balk': cols[17].get_text(strip=True)
                }
                player_data2.append(data)

            print(f"{team_name.upper()} Basic2 데이터 추출 완료. 현재까지 추출된 선수 수: {len(player_data2)}")

        except Exception as e:
            print(f"Basic2.aspx 크롤링 중 오류 발생 ({team_name.upper()} 팀): {e}")

    # player_data2 리스트를 DataFrame으로 변환
    if player_data2:
        # player_data2 list를 pandas.DataFrame으로 변환하여 표 형태의 DataFrame으로 만든다.
        df2 = pd.DataFrame(player_data2)
        # Player_Name와 Player_Team을 기준으로 중복된 행을 제거
        # inplace=True : 원본 DataFrame을 직접 수정.
        df2.drop_duplicates(subset=['Player_Name', 'Player_Team'], inplace=True)
        print(f"최종 df2 생성 완료. 행 수: {len(df2)}")
    else:
        print("\nBasic2.aspx에서 저장할 데이터가 없습니다.")
        # 빈 DataFrame 생성하여 merge 오류 방지
        df2 = pd.DataFrame()

    # ==================== DataFrame 병합 및 CSV 저장 ====================

    if not df1.empty and not df2.empty:
        print("\n--- 두 DataFrame 병합 시작 ---")
        # 'Player_Name'과 'Player_Team'을 고유 키로 사용하여 병합
        # how='outer : 왼쪽(df1)과 오른쪽(df2) 모두에서 일치하는 행을 찾고, 일치하지 않는 행도 모두 포함한다. 일치하지 않는 열 값은 NaN인다.
        merged_df = pd.merge(df1, df2.drop(columns=['Earned_Run_Average'], errors='ignore'), on=['Player_Name', 'Player_Team'], how='outer')

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

        if 'Innings_Pitched' in merged_df.columns:
            merged_df['Innings_Pitched'] = merged_df['Innings_Pitched'].astype(str)
            # apply()가 컬럼의 각 원소를 함수 인자로 넣어 호출하는 방식을 자동으로 처리하기 때문에, 호출할 때 인자를 따로 적지 않아도 문제없다.
            merged_df['Innings_Pitched'] = merged_df['Innings_Pitched'].apply(convert_innings_pitched)

        numeric_cols_float = [
            'Earned_Run_Average', 'Winning_Percentage',
            'WHIP', 'Opponent_Batting_Average'
        ]
        numeric_cols_int = [
            'Game_Num', 'Win', 'Lose', 'Save', 'Hold', 'Hits', 'Home_Run',
            'Base_On_Balls', 'Hit_By_Pitch', 'Strike_Out', 'Runs', 'Earned_Run',
            'Complete_Game', 'Shutout', 'Quality_Start', 'Blown_Save',
            'Total_Batters_Faced', 'Number_Of_Pitching', '2Base', '3Base',
            'Sacrifice_Bunt', 'Sacrifice_Fly', 'IBB', 'Wild_Pitch', 'Balk'
        ]

        for col in numeric_cols_float:
            if col in merged_df.columns:
                # errors='coerce' : '-' 등은 NaN으로
                # .fillna(0) : NaN 값을 0으로 채움
                # .astype(float) : 최종적으로 정수형(float) 으로 변환
                merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce').fillna(0).astype(float)
        
        for col in numeric_cols_int:
            if col in merged_df.columns:
                # .astype(int) : 최종적으로 정수형(int) 으로 변환
                merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce').fillna(0).astype(int) 
        
        if 'Innings_Pitched' in merged_df.columns:
            merged_df['Innings_Pitched'] = pd.to_numeric(merged_df['Innings_Pitched'], errors='coerce').fillna(0).astype(float)

        print("병합 및 데이터 타입 변환 완료.")

        # Game_Num이 0인 데이터 삭제
        # merged_df의 초기 총 행(row) 수를 저장
        initial_rows = len(merged_df)
        # Game_Num 값이 0보다 큰 선수들만 남기고, 나머지는 제거합니다.
        merged_df = merged_df[merged_df['Game_Num'] > 0]
        # 삭제된 행 수 = 처음 행 개수 - 필터링 후 남은 행 개수
        deleted_rows = initial_rows - len(merged_df)
        if deleted_rows > 0:
            print(f"Game_Num이 0인 {deleted_rows}개의 선수 데이터가 삭제되었습니다.")
        else:
            print("Game_Num이 0인 선수 데이터가 없습니다.")

        # merged_df Dataframe의 맨 위 5개 행을 출력.
        print(merged_df.head())
        print(f"최종 병합된 데이터의 행 수: {len(merged_df)}, 컬럼 수: {len(merged_df.columns)}")

        csv_filename = "2024_useGame_pitcher.csv"
        merged_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"\n'{csv_filename}' 파일이 성공적으로 저장되었습니다.")

    else:
        print("\n데이터프레임이 비어있어 병합 및 CSV 저장 작업을 수행할 수 없습니다.")

finally:
    # 모든 크롤링 작업이 완료된 후 드라이버를 종료합니다.
    driver.quit()
    print("\n전체 크롤링 완료. 브라우저 종료됨")