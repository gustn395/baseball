from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# --- 설정 ---
URL = "https://www.koreabaseball.com/Record/TeamRank/TeamRankDaily.aspx"
CHROME_DRIVER_PATH = './chromedriver.exe'

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
# 특정 요소가 나타날 때까지 최대 10초 동안 기다리는 설정
wait = WebDriverWait(driver, 10)
print("브라우저 및 WebDriver 초기화 완료.")

try:
    # URL 접속
    driver.get(URL)
    
    # 테이블이 로드될 때까지 기다립니다.
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "tData")))
    
    # 페이지 소스 가져오기
    html = driver.page_source
    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(html, 'html.parser')
    # class="tData"인 테이블 찾기
    table = soup.find('table', {'class': 'tData'})
    # 데이터를 담을 리스트 초기화
    team_data = []
    
    # 테이블의 모든 행(tr)을 순회
    for row in table.find('tbody').find_all('tr'):
        # 각 행의 모든 열(td)을 리스트로 가져오기
        cols = row.find_all('td')
        
        # 필요한 데이터 추출 (팀명, 경기, 승, 패, 무, 승률, 게임차)
        team_name = cols[1].text.strip()
        games = cols[2].text.strip()
        wins = cols[3].text.strip()
        losses = cols[4].text.strip()
        draws = cols[5].text.strip()
        win_percentage = cols[6].text.strip()
        games_behind = cols[7].text.strip()
        
        # 추출한 데이터를 리스트에 추가
        team_data.append([team_name, games, wins, losses, draws, win_percentage, games_behind])
    
    # pandas DataFrame 생성
    columns = [team_name, games, wins, losses, draws, win_percentage, games_behind]
    df = pd.DataFrame(team_data, columns=columns)
    
    # 결과를 CSV 파일로 저장
    df.to_csv('2025_useBoard_team.csv', index=False, encoding='utf-8-sig')
    
    # 결과 출력
    print("KBO 팀 순위 데이터")
    print(df)
    print("\nteam_rankings.csv 파일로 저장이 완료되었습니다.")

finally:
    # 드라이버 종료
    driver.quit()
