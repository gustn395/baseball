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

# Todo(게시판 타자 기록 크롤링)
# 웹에 보일 타자 기록 : 선수 이름, 타율, 경기, 안타, 2루타, 3루타, 홈런, 타점, 득점, 볼넷, 삼진, 출루율, OPS
# URL1 기록 : 선수 이름, 타율, 경기, 안타, 2루타, 3루타, 홈런, 타점, 득점
# URL2 기록 : 선수 이름, 볼넷, 삼진, 출루율, OPS

# 특이 사항 : 
# 1. 타율은 규정 타석은 채워야 한다. -> 규정 타석 = (경기 수 * 3.1) 에서 소수점 이하를 버린 수.
# -> 그럼 이것은 mapper에서 타율을 가져올 때 where 절로 계산한다. -> 방법 1로 하자. -> DB에 "웹에 보일 타자 기록" 이외로 타석 수를 DB에 넣어야 한다.
# 2. merge할 때 선수 이름과 선수 팀을 키로 하기 때문에 선수 팀도 필요하다. URL1과 URL2에 둘다

# 최종 DB에 넣을 기록 : 선수 이름, 선수 팀 이름, 타율, 경기, 타석, 안타, 2루타, 3루타, 홈런, 타점, 득점, 볼넷, 삼진, 출루율, OPS
# 최종 URL1 기록 : 선수 이름, 선수 팀 이름, 타율, 경기, 타석, 안타, 2루타, 3루타, 홈런, 타점, 득점
# 최종 URL2 기록 : 선수 이름, 선수 팀 이름, 볼넷, 삼진, 출루율, OPS

# 버튼 누르면 스탯 순서로 n명 웹에 나열 : 
# 방법 1 : 스탯 크롤링 -> csv 저장 -> DB 저장 -> backend mapper로 DB에서 스탯순으로 가져옴.
# 방법 2 : https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx?sort=HRA_RT 이 URL 부분의 sort={} 부분을 바꿔줌.
# -> URL HTML 코드에 적혀있는 스탯 이름을 dictionary로 만든다. -> 버튼을 누르면 dictionary에서 버튼에 맞는 값을 가져와서 {}부분에 넣어줌.
# -> 스탯 순으로 나열된 선수들의 n명의 스탯을 dataframe에 넣고 csv 파일로 만든 다음 DB로 넘김 or dataframe에 넣고 바로 backend로 보냄.
# => 너무 복잡하다. 방법 1로 하자...
# 그런데 타율은 규정 타석 채워야 하는데? 그래서 방법2를 생각하긴 했지...

# 그러면 할 것 : 
# 1. 연도 바꾸기 (완)
# 2. 파일 이름 바꾸기 (완)
# 3. URL1에서 필요한 기록만 가져오기 -> data dictionary 변경 (완)
# 4. URL2에서 필요한 기록만 가져오기 -> data dictionary 변경 (완)
# 5. 바뀐 data dictionary에 맞게 numeric_cols_float와 numeric_cols_int 리스트 값들 변경. (완)


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

        # 현재 선택된 연도 확인
        current_selected_year = year_select.first_selected_option.get_attribute("value")

        if current_selected_year == "2025":
            print("연도: 2025년이 이미 선택되어 있습니다. 연도 변경을 건너뜜.")
            # 이미 2025년이 선택되어 있다면, 굳이 다시 선택하여 staleness_of 오류를 유발할 필요 없음.
            # 페이지가 이미 2025년 기준으로 로드되었다고 가정하고 다음 단계로 진행.
            # 필요하다면 여기에 테이블의 데이터가 유효한지 추가적인 대기 조건(예: 첫 번째 행 존재)을 넣을 수 있음.
            wait.until(EC.presence_of_element_located(table_locator)) # 테이블이 여전히 존재하는지 확인
        else:
            # 2025년이 선택되어 있지 않다면, 테이블이 변경될 것을 예상하고 선택 동작 수행
            print(f"현재 선택된 연도: {current_selected_year}. 2025년으로 변경합니다.")
            
            # 테이블의 StaleElementReferenceException을 피하기 위해 find_element를 try-except로 감싸거나,
            # select_by_value 후 다시 찾는 방식으로 변경 (여기서는 안전하게 try-except 사용)
            try:
                table_before_change = driver.find_element(*table_locator)
            except StaleElementReferenceException:
                # 페이지 로딩 초기에 테이블이 잠깐 사라질 수 있으므로 다시 찾기 시도
                table_before_change = wait.until(EC.presence_of_element_located(table_locator))

            # Dropdown에서 value="2025"인 항목을 선택한다.
            year_select.select_by_value("2025")
            print("연도 선택: 2025") # 성공적으로 선택 시 메시지
            
            # 이전 테이블이 사라질 때까지 기다림
            # 가끔 staleness_of가 작동하지 않을 수 있으므로, time.sleep()을 추가하거나 다른 EC 조건을 고려할 수 있음.
            try:
                wait.until(EC.staleness_of(table_before_change))
            except TimeoutException:
                print("Warning: 기존 테이블이 Stale 상태가 되는 데 타임아웃 발생. 하지만 진행합니다.")
                # 페이지가 빠르게 업데이트되어 staleness_of가 감지되기 전에 이미 새 테이블이 로드되었을 수 있음
            
            # 새로운 테이블이 로드될 때까지 기다림
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
                'Run': cols[7].get_text(strip=True), # 득점 
                'Hit': cols[8].get_text(strip=True), # 안타 
                'two_Base': cols[9].get_text(strip=True), # 2루타 
                'three_Base': cols[10].get_text(strip=True), # 3루타 
                'Home_Run': cols[11].get_text(strip=True), # 홈런 
                'Runs_Batted_In': cols[13].get_text(strip=True), # 타점 
            }
            # data dictionary의 내용을 player_data1 list에 넣는다.
            player_data1.append(data)

        print(f"{team_name.upper()} Basic1 데이터 추출 완료. 추출된 선수 수: {len(player_data1)}")

    except Exception as e:
        print(f"Basic1.aspx 크롤링 중 오류 발생: {type(e).__name__} - {e}")
        # Selenium 관련 오류의 경우, 더 자세한 정보를 위해
        if hasattr(e, 'msg'):
            print(f"Selenium Error Message: {e.msg}")
        if hasattr(e, 'stacktrace'):
            print(f"Selenium Stacktrace: {e.stacktrace}")

    finally:
        driver.quit()
        print("Basic1.aspx 브라우저 종료됨")

# player_data1 리스트를 DataFrame으로 변환
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

        # 현재 선택된 연도 확인
        current_selected_year = year_select.first_selected_option.get_attribute("value")

        if current_selected_year == "2025":
            print("연도: 2025년이 이미 선택되어 있습니다. 연도 변경을 건너뜜.")
            # 이미 2025년이 선택되어 있다면, 굳이 다시 선택하여 staleness_of 오류를 유발할 필요 없음.
            # 페이지가 이미 2025년 기준으로 로드되었다고 가정하고 다음 단계로 진행.
            # 필요하다면 여기에 테이블의 데이터가 유효한지 추가적인 대기 조건(예: 첫 번째 행 존재)을 넣을 수 있음.
            wait.until(EC.presence_of_element_located(table_locator)) # 테이블이 여전히 존재하는지 확인
        else:
            # 2025년이 선택되어 있지 않다면, 테이블이 변경될 것을 예상하고 선택 동작 수행
            print(f"현재 선택된 연도: {current_selected_year}. 2025년으로 변경합니다.")
            
            # 테이블의 StaleElementReferenceException을 피하기 위해 find_element를 try-except로 감싸거나,
            # select_by_value 후 다시 찾는 방식으로 변경 (여기서는 안전하게 try-except 사용)
            try:
                table_before_change = driver.find_element(*table_locator)
            except StaleElementReferenceException:
                # 페이지 로딩 초기에 테이블이 잠깐 사라질 수 있으므로 다시 찾기 시도
                table_before_change = wait.until(EC.presence_of_element_located(table_locator))

            # Dropdown에서 value="2025"인 항목을 선택한다.
            year_select.select_by_value("2025")
            print("연도 선택: 2025") # 성공적으로 선택 시 메시지
            
            # 이전 테이블이 사라질 때까지 기다림
            # 가끔 staleness_of가 작동하지 않을 수 있으므로, time.sleep()을 추가하거나 다른 EC 조건을 고려할 수 있음.
            try:
                wait.until(EC.staleness_of(table_before_change))
            except TimeoutException:
                print("Warning: 기존 테이블이 Stale 상태가 되는 데 타임아웃 발생. 하지만 진행합니다.")
                # 페이지가 빠르게 업데이트되어 staleness_of가 감지되기 전에 이미 새 테이블이 로드되었을 수 있음
            
            # 새로운 테이블이 로드될 때까지 기다림
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
                'Strike_Out': cols[7].get_text(strip=True), # 삼진 
                'On_Base_Percentage': cols[10].get_text(strip=True), # 출루율 
                'Onbase_Plus_Slug': cols[11].get_text(strip=True), # OPS(출루율+장타율) 
            }
            # data dictionary의 내용을 player_data2 list에 넣는다.
            player_data2.append(data)

        print(f"{team_name.upper()} Basic2 데이터 추출 완료. 추출된 선수 수: {len(player_data2)}")

    except Exception as e:
        print(f"Basic2.aspx 크롤링 중 오류 발생: {e}")

    finally:
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
    numeric_cols_float = ['Batting_average', 'On_Base_Percentage', 'Onbase_Plus_Slug']
    numeric_cols_int = ['Game_Num', 'Plate_Appearance', 'Run', 'Hit', 'Two_Base', 
        'Three_Base','Home_Run', 'Runs_Batted_In', 'Four_Ball', 'Strike_Out']

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
    csv_filename = "2025_useBoard_hitter.csv"
    merged_df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"\n'{csv_filename}' 파일이 성공적으로 저장되었습니다.")

else:
    print("\n데이터프레임이 비어있어 병합 및 CSV 저장 작업을 수행할 수 없습니다.")