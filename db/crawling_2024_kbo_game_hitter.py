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
URL1 = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HRA_RT"
URL2 = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic2.aspx?sort=HRA_RT"
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

# ==================== URL1 (Basic1.aspx) 데이터 수집 ====================

# teams dictionary에서 key, value를 가져와 그것들을 기준으로 반복문을 돌림.
for team_name, team_code in teams.items(): 
    print(f"\n==================== {team_name.upper()} 팀 Basic1 데이터 수집 시작 ====================")

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

    try:
        # URL1에 접속한다.
        driver.get(URL1)
        print("페이지 접속 완료")

        # CSS selector를 이용해 찾고자 하는 table의 위치를 지정
        table_locator = (By.CSS_SELECTOR, "table.tData01.tt")
        # table_locator가 Web page에 나타날 때까지 (최대 20초) 기다린다.
        wait.until(EC.presence_of_element_located(table_locator))
        print("초기 테이블 로딩 완료")

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
        print("최종 테이블 로딩 완료")

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

            # Basic1.aspx의 경우 16개 컬럼 예상 (0부터 시작)
            if len(cols) < 16: 
                continue
            
            rank_text = cols[0].get_text(strip=True)
            # isdigit()으로 숫자인지 확인한다. 숫자가 아니면 데이터 행이 아니므로 건너뛴다.
            if not rank_text.isdigit():
                continue
            
            avg_str = cols[3].get_text(strip=True)
            # 실수(float)로 변환 가능한지 확인한다. 안 되면 건너뛴다
            try:
                avg = float(avg_str)
            except ValueError:
                continue 
            
            # 타율이 0 이하인 경우는 실질적인 데이터가 아니거나 오류일 가능성이 있어서 제외한다.
            if avg <= 0:
                continue

            data = {
                'Player_Name': cols[1].get_text(strip=True), # 선수 이름
                'Player_Team': cols[2].get_text(strip=True), # 선수 팀 이름
                'Batting_average': avg_str, # 타율
                'Game_Num': cols[4].get_text(strip=True), # 경기 수
                'Plate_Appearance': cols[5].get_text(strip=True), # 타석
                'At_Bat': cols[6].get_text(strip=True), # 타수
                'Run': cols[7].get_text(strip=True), # 득점
                'Hit': cols[8].get_text(strip=True), # 안타
                'two_Base': cols[9].get_text(strip=True), # 2루타
                'three_Base': cols[10].get_text(strip=True), # 3루타
                'Home_Run': cols[11].get_text(strip=True), # 홈런
                'Total_Base': cols[12].get_text(strip=True), # 루타
                'Runs_Batted_In': cols[13].get_text(strip=True), # 타점
                'Sacrifice_Bunts': cols[14].get_text(strip=True), # 희생 번트
                'Sacrifice_Fly': cols[15].get_text(strip=True), # 희생 플라이
            }
            # data dictionary의 내용을 player_data1 list에 넣는다.
            player_data1.append(data)

        print(f"{team_name.upper()} Basic1 데이터 추출 완료. 추출된 선수 수: {len(player_data1)}")

    except Exception as e:
        print(f"Basic1.aspx 크롤링 중 오류 발생: {e}")

    finally:
        # Web Browser를 완전히 종료한다.
        driver.quit()
        print("Basic1.aspx 브라우저 종료됨")

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

# ==================== URL2 (Basic2.aspx) 데이터 수집 ====================
# teams dictionary에서 key, value를 가져와 그것들을 기준으로 반복문을 돌림.
for team_name, team_code in teams.items():
    print(f"\n==================== {team_name.upper()} 팀 Basic2 데이터 수집 시작 ====================")

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

    try:
        # URL2에 접속한다.
        driver.get(URL2)
        print("페이지 접속 완료")

        # CSS selector를 이용해 찾고자 하는 table의 위치를 지정
        table_locator = (By.CSS_SELECTOR, "table.tData01.tt")
        # table_locator가 Web page에 나타날 때까지 (최대 20초) 기다린다.
        wait.until(EC.presence_of_element_located(table_locator))
        print("초기 테이블 로딩 완료")

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
        print("최종 테이블 로딩 완료")

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

            # Basic2.aspx의 경우 15개 컬럼 예상
            if len(cols) < 15: 
                continue

            rank_text = cols[0].get_text(strip=True)
            # isdigit()으로 숫자인지 확인한다. 숫자가 아니면 데이터 행이 아니므로 건너뛴다.
            if not rank_text.isdigit():
                continue

            data = {
                'Player_Name': cols[1].get_text(strip=True), # 선수 이름
                'Player_Team': cols[2].get_text(strip=True), # 선수 팀 이름
                'Four_Ball': cols[4].get_text(strip=True), # 볼넷
                'IBB': cols[5].get_text(strip=True), # 고의4구
                'Hit_by_Pitch': cols[6].get_text(strip=True), # 사구(몸에 맞는 볼)
                'Strike_Out': cols[7].get_text(strip=True), # 삼진
                'Double_out': cols[8].get_text(strip=True), # 병살타
                'Slugging': cols[9].get_text(strip=True), # 장타율
                'On_Base_Percentage': cols[10].get_text(strip=True), # 출루율
                'Onbase_Plus_Slug': cols[11].get_text(strip=True), # OPS(출루율+장타율)
                'Multi_Hit': cols[12].get_text(strip=True), # 멀티 히트(한 경기 안타 2개 이상)
                'Scoring_Position_AVG': cols[13].get_text(strip=True), # 득점권 타율
                'Pinch_Hit_AVG': cols[14].get_text(strip=True) # 대타 타율
            }
            # data dictionary의 내용을 player_data2 list에 넣는다.
            player_data2.append(data)

        print(f"{team_name.upper()} Basic2 데이터 추출 완료. 추출된 선수 수: {len(player_data2)}")

    except Exception as e:
        print(f"Basic2.aspx 크롤링 중 오류 발생: {e}")

    finally:
        # Web Browser를 완전히 종료한다.
        driver.quit()
        print("Basic2.aspx 브라우저 종료됨")

# player_data2 리스트를 DataFrame으로 변환
if player_data2:
    # player_data2 list를 pandas.DataFrame으로 변환하여 표 형태의 DataFrame으로 만든다.
    df2 = pd.DataFrame(player_data2)
    # Player_Name와 Player_Team을 기준으로 중복된 행을 제거
    # inplace=True : 원본 DataFrame을 직접 수정.
    df2.drop_duplicates(subset=['Player_Name', 'Player_Team'], inplace=True)
    print(f"최종 df2 생성 완료. 행 수: {len(df2)}")
else:
    print("Basic2.aspx에서 저장할 데이터가 없습니다.")
    # 빈 DataFrame 생성하여 merge 오류 방지
    df2 = pd.DataFrame() 

# ==================== DataFrame 병합 및 CSV 저장 ====================

if not df1.empty and not df2.empty:
    print("\n--- 두 DataFrame 병합 시작 ---")
    # 'Player_Name'과 'Player_Team'을 고유 키로 사용하여 병합
    # how='outer : 왼쪽(df1)과 오른쪽(df2) 모두에서 일치하는 행을 찾고, 일치하지 않는 행도 모두 포함한다. 일치하지 않는 열 값은 NaN인다.
    merged_df = pd.merge(df1, df2, on=['Player_Name', 'Player_Team'], how='outer')

    # 데이터 타입 변환 (선택 사항이지만 권장)
    numeric_cols_float = ['Batting_average', 'Slugging', 'On_Base_Percentage', 'Onbase_Plus_Slug', 'Scoring_Position_AVG', 'Pinch_Hit_AVG']
    numeric_cols_int = [
        'Game_Num', 'Plate_Appearance', 'At_Bat', 'Run', 'Hit', 'two_Base', 'three_Base',
        'Home_Run', 'Total_Base', 'Runs_Batted_In', 'Sacrifice_Bunts', 'Sacrifice_Fly',
        'Four_Ball', 'IBB', 'Hit_by_Pitch', 'Strike_Out', 'Double_out', 'Multi_Hit'
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

    print("병합 및 데이터 타입 변환 완료.")

    # Game_Num이 0인 데이터 삭제
    # merged_df의 초기 총 행(row) 수를 저장
    initial_rows = len(merged_df)
    # Game_Num 값이 0보다 큰 선수들만 남기고, 나머지는 제거합니다.
    merged_df = merged_df[merged_df['Game_Num'] > 0]
    # 삭제된 행 수 = 처음 행 개수 - 필터링 후 남은 행 개수
    deleted_rows = initial_rows - len(merged_df)
    print(f"Game_Num이 0인 {deleted_rows}개의 선수 데이터가 삭제되었습니다.")

    # merged_df 데이터프레임의 맨 위 5개 행을 출력.
    print(merged_df.head())
    print(f"최종 병합된 데이터의 행 수: {len(merged_df)}, 컬럼 수: {len(merged_df.columns)}")

    # CSV 파일로 저장
    csv_filename = "2024_useGame_hitter.csv"
    merged_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"\n'{csv_filename}' 파일이 성공적으로 저장되었습니다.")

else:
    print("\n데이터프레임이 비어있어 병합 및 CSV 저장 작업을 수행할 수 없습니다.")