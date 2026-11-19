from flask import Flask, render_template, request, jsonify
from lunar_python import Solar, Lunar
import sqlite3, os, sys, threading, webbrowser
from datetime import date, datetime
import re

# Frozen EXE: templates are read from PyInstaller's temporary bundle,
# while the user's SQLite data stays beside the EXE and survives updates.
if getattr(sys, "frozen", False):
    RESOURCE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    DATA_DIR = os.path.dirname(sys.executable)
else:
    RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = RESOURCE_DIR
DB = os.path.join(DATA_DIR, 'saju_people.db')
app = Flask(__name__, template_folder=os.path.join(RESOURCE_DIR, 'templates'),
            static_folder=None)

PILLAR_METHODS = [('년주','getYear','getYearGan','getYearZhi','getYearHideGan','getYearShiShenGan','getYearShiShenZhi'),
                  ('월주','getMonth','getMonthGan','getMonthZhi','getMonthHideGan','getMonthShiShenGan','getMonthShiShenZhi'),
                  ('일주','getDay','getDayGan','getDayZhi','getDayHideGan','getDayShiShenGan','getDayShiShenZhi'),
                  ('시주','getTime','getTimeGan','getTimeZhi','getTimeHideGan','getTimeShiShenGan','getTimeShiShenZhi')]
ELEMENTS = {'甲':'목','乙':'목','丙':'화','丁':'화','戊':'토','己':'토','庚':'금','辛':'금','壬':'수','癸':'수',
            '子':'수','亥':'수','寅':'목','卯':'목','巳':'화','午':'화','辰':'토','戌':'토','丑':'토','未':'토','申':'금','酉':'금'}


def db():
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    con.execute('''CREATE TABLE IF NOT EXISTS people(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, birth TEXT NOT NULL, birth_time TEXT, gender TEXT, calendar_type TEXT DEFAULT 'solar', is_leap INTEGER DEFAULT 0, memo TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    cols = {r['name'] for r in con.execute('PRAGMA table_info(people)').fetchall()}
    if 'calendar_type' not in cols: con.execute("ALTER TABLE people ADD COLUMN calendar_type TEXT DEFAULT 'solar'")
    if 'is_leap' not in cols: con.execute("ALTER TABLE people ADD COLUMN is_leap INTEGER DEFAULT 0")
    con.commit(); return con


def analyze(data):
    name = (data.get('name') or '').strip()
    birth = data.get('birth') or ''
    gender = data.get('gender') or ''
    time_text = data.get('birth_time') or ''
    if not name or not birth: raise ValueError('이름과 생년월일을 입력해 주세요.')
    if len(name) > 40: raise ValueError('이름은 40자 이내로 입력해 주세요.')
    if gender not in ('', '남성', '여성'): raise ValueError('성별 선택값을 확인해 주세요.')
    if data.get('calendar_type', 'solar') not in ('solar', 'lunar'): raise ValueError('달력 종류를 확인해 주세요.')
    try:
        if not re.fullmatch(r'\d{4}-\d{1,2}-\d{1,2}', birth): raise ValueError('날짜 형식 오류')
        y, m, d = map(int, birth.split('-'))
        hh, mm = (map(int, time_text.split(':')) if time_text else (12, 0))
        if not (0 <= hh <= 23 and 0 <= mm <= 59): raise ValueError('시간 범위 오류')
        if data.get('calendar_type', 'solar') == 'solar': datetime(y, m, d)
        if not (1800 <= y <= 2200): raise ValueError('지원 연도 범위 오류')
        if data.get('calendar_type', 'solar') == 'lunar':
            lunar_month = -m if data.get('is_leap') else m
            lunar = Lunar.fromYmdHms(y, lunar_month, d, hh, mm, 0)
            solar = lunar.getSolar()
        else:
            solar = Solar.fromYmdHms(y, m, d, hh, mm, 0)
            lunar = solar.getLunar()
        ec = lunar.getEightChar()
    except Exception as e:
        raise ValueError('생년월일 또는 태어난 시간을 확인해 주세요.') from e

    pillars=[]; counts={k:0 for k in ['목','화','토','금','수']}
    for label, meth, gm, gz, hm, sm, sz in PILLAR_METHODS:
        if label=='시주' and not time_text:
            pillars.append({'label':label,'gz':'미상','gan':'','zhi':'','hidden':[],'hidden_ten_gods':[],'ten_god':'시간 미입력'})
            continue
        gan=getattr(ec,gm)(); zhi=getattr(ec,gz)(); hidden=list(getattr(ec,hm)() or [])
        pillars.append({'label':label,'gz':getattr(ec,meth)(),'gan':gan,'zhi':zhi,'hidden':hidden,'hidden_ten_gods':list(getattr(ec,sz)() or []),'ten_god':getattr(ec,sm)()})
        counts[ELEMENTS[gan]] += 1; counts[ELEMENTS[zhi]] += 1
    day_gan=ec.getDayGan()
    # 대운은 성별과 연간 음양에 따라 순행/역행. 라이브러리 기준 1=남, 0=여.
    yun = ec.getYun(1 if gender=='남성' else 0) if gender in ('남성','여성') else None
    start_solar=yun.getStartSolar() if yun else None
    dayun=[]
    if yun:
        for item in yun.getDaYun(9)[1:9]:
            dayun.append({'ganzhi':item.getGanZhi(),'start_age':item.getStartAge(),'end_age':item.getEndAge(),
                          'start_year':item.getStartYear(),'end_year':item.getEndYear()})
    today=date.today()
    element_notes = {
      '목':'성장·기획·확장의 상징으로 풀이합니다. 새로운 방향을 만들고 꾸준히 키워가는 관점에서 살펴보세요.',
      '화':'표현·열정·확산의 상징으로 풀이합니다. 추진력과 표현력을 살리되 속도 조절도 함께 생각해 보세요.',
      '토':'안정·조율·축적의 상징으로 풀이합니다. 신뢰와 지속성을 강점으로 삼고 변화에 유연하게 대응하는 것이 좋습니다.',
      '금':'원칙·판단·정리의 상징으로 풀이합니다. 기준을 세우고 완성도를 높이는 힘과 함께 유연한 소통을 살펴보세요.',
      '수':'지혜·정보·흐름의 상징으로 풀이합니다. 관찰력과 적응력을 활용하고 생각을 실행으로 연결하는 점을 의식해 보세요.'}
    strongest = max(counts, key=counts.get)
    weakest = min(counts, key=counts.get)
    reading = {'day_master': element_notes[ELEMENTS[day_gan]], 'balance': f'겉글자 기준으로 {strongest} 기운이 가장 많이 보이고 {weakest} 기운이 가장 적게 집계됩니다. 다만 오행 개수만으로 좋고 나쁨이나 신강·신약을 판정하지는 않습니다.'}
    sy, sm, sd = solar.getYear(), solar.getMonth(), solar.getDay()
    age=today.year-sy-((today.month,today.day)<(sm,sd))
    return {'name':name,'birth':birth,'birth_time':time_text,'gender':gender,'calendar_type':data.get('calendar_type','solar'),'is_leap':bool(data.get('is_leap')),'age':age,
      'solar':solar.toYmdHms(),'lunar':lunar.toString(),'pillars':pillars,'day_master':day_gan,
      'day_master_element':ELEMENTS[day_gan],'elements':counts,'reading':reading,'yun_direction':(('순행' if yun.isForward() else '역행') if yun else '성별 선택 필요'),
      'yun_start':(f"{yun.getStartYear()}년 {yun.getStartMonth()}개월 {yun.getStartDay()}일 후 (예상 기산일 {start_solar.toYmd()})" if yun else '성별을 선택하면 계산됩니다.'),
      'dayun':dayun,'today':today.isoformat()}

@app.get('/')
def home(): return render_template('index.html')

@app.post('/api/analyze')
def api_analyze():
    try:
        data = request.get_json(force=True) or {}
        return jsonify({'ok':True,'result':analyze(data)})
    except ValueError as e: return jsonify({'ok':False,'error':str(e)}),400
    except Exception: return jsonify({'ok':False,'error':'분석 중 문제가 발생했습니다. 입력값을 확인하거나 프로그램을 다시 실행해 주세요.'}),500

@app.get('/api/people')
def people_list():
    con=db(); rows=con.execute('SELECT * FROM people ORDER BY id DESC').fetchall(); con.close()
    return jsonify([dict(x) for x in rows])

@app.post('/api/people')
def people_add():
    data=request.get_json(force=True) or {}
    if not (str(data.get('name') or '').strip() and data.get('birth')): return jsonify({'ok':False,'error':'이름과 생년월일이 필요합니다.'}),400
    if len(str(data.get('name')).strip()) > 40: return jsonify({'ok':False,'error':'이름은 40자 이내로 입력해 주세요.'}),400
    con=db(); cur=con.execute('INSERT INTO people(name,birth,birth_time,gender,calendar_type,is_leap,memo) VALUES(?,?,?,?,?,?,?)',
      (data['name'].strip(),data['birth'],data.get('birth_time',''),data.get('gender',''),data.get('calendar_type','solar'),int(bool(data.get('is_leap'))),data.get('memo','')))
    con.commit(); pid=cur.lastrowid; con.close(); return jsonify({'ok':True,'id':pid})

@app.delete('/api/people/<int:pid>')
def people_delete(pid):
    con=db(); con.execute('DELETE FROM people WHERE id=?',(pid,)); con.commit(); con.close(); return jsonify({'ok':True})

if __name__ == '__main__':
    db()
    # Open the local app after the server has had a moment to start.
    threading.Timer(1.2, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
