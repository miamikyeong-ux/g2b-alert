import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# 1. 설정 (환경변수 사용)
API_KEY = os.environ.get('G2B_API_KEY')
GMAIL_USER = os.environ.get('GMAIL_USER')
GMAIL_PW = os.environ.get('GMAIL_APP_PASSWORD')

# 2. 키워드 리스트 (요청하신 대로 정리)
KEYWORDS = [
    "부산공유대학", "디지털트윈", "통일교육", "통일교육원", "체험관", "체험콘텐츠", 
    "체험존", "디지털 체험존", "디지털 콘텐츠", "미디어아트", "전시", "전시콘텐츠", 
    "VR", "XR", "북한정보포털", "동포청", "한국어교육", "실감형", "AI", "학습콘텐츠", 
    "디지털구축", "콘텐츠 제작", "콘텐츠 개발", "포털 구축", "시스템 구축", "뉴미디어", 
    "한반도통일미래센터", "통일미래센터", "홈페이지", "정보화", "정보시스템", 
    "차세대 AI시스템", "정보화 차세대 통합의료정보시스템"
]

def check_g2b():
    # 오늘 날짜 기준 검색
    today = datetime.now().strftime('%Y%m%d')
    url = "http://apis.data.go.kr/1230000/BidPublicInfoService04/getBidPblancListInfoService01"
    
    params = {
        'serviceKey': API_KEY,
        'type': 'json',
        'numOfRows': '100',
        'inqryBgnDt': today,
        'inqryEndDt': today
    }

    response = requests.get(url, params=params)
    items = response.json().get('response', {}).get('body', {}).get('items', [])
    
    matched_bids = []
    for item in items:
        title = item.get('bidNtceNm', '')
        # 키워드 매칭 (시스템, 서비스 단독 제외 로직은 리스트에서 이미 제거됨)
        if any(kw in title for kw in KEYWORDS):
            matched_bids.append(item)
            
    return matched_bids

def send_email(bids):
    if not bids: return
    
    msg = MIMEMultipart()
    msg['Subject'] = f"🔔 나라장터 신규 공고 알림 ({len(bids)}건)"
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_USER
    
    html = "<h3>조건에 맞는 신규 공고가 있습니다.</h3><table border='1'>"
    html += "<tr><th>과제명</th><th>발주처</th><th>금액</th><th>마감일</th></tr>"
    
    for bid in bids:
        html += f"<tr><td>{bid['bidNtceNm']}</td><td>{bid['ntceInsttNm']}</td><td>{bid['bdgtAmt']}</td><td>{bid['bidCcbtEndDt']}</td></tr>"
    html += "</table>"
    
    msg.attach(MIMEText(html, 'html'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_USER, GMAIL_PW)
        server.send_message(msg)

if __name__ == "__main__":
    found_bids = check_g2b()
    if found_bids:
        send_email(found_bids)
        print(f"{len(found_bids)}건 메일 발송 완료")
