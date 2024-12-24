import streamlit as st
from streamlit_gsheets import GSheetsConnection
import uuid
from cryptography.fernet import Fernet
import arrow
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def say_hello(name):
   print(f'Hello, Streamlit! {name}')

def connect_to_gsheet(json_keyfile_path, sheet_name, worksheet_name):
    # Google API 인증 범위 설정
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
    client = gspread.authorize(creds)

    # Google Sheet 열기
    # sheet = client.open(sheet_name)
    sheet = client.open_by_url(sheet_name)

    # 특정 워크시트(탭) 선택
    worksheet = sheet.worksheet(worksheet_name)
    return worksheet


def search_gsheet(name, tel):
    # Create a connection object.

    name = name.strip()
    tel = str(tel).strip().replace('-','')

    conn = st.connection("gsheets", type=GSheetsConnection)
    ttl_seconds = 10
    df = conn.read(ttl=ttl_seconds, sheet='works')
    # data = conn.read(worksheet='Games', ttl=ttl_seconds, usecols=list(range(6)))
    st.dataframe(df)
    new_member = True
    for i, row in df.iterrows():
        if row['name'].strip() == name:
            if str(row['tel']).strip().replace('-','') == tel:
                return True
    return False
    #     st.write(row['name'])
    #     st.write(name)
    #     st.write(tel)
    #     st.write("----")
    #     new_member = False

    # if new_member:
    #     pass

def load_key_from_file(file_path: str) -> bytes:
    # 파일에서 키 읽기
    with open(file_path, 'rb') as file:
        key = file.read()
    print(f"Key loaded from {file_path}")
    return key

def main():
    st.header('Google Sheet Tet')
    # ttl_seconds = 10

    # # Create a connection object.
    # conn = st.connection("gsheets", type=GSheetsConnection)

    # df = conn.read(ttl=ttl_seconds)
    # # data = conn.read(worksheet='Games', ttl=ttl_seconds, usecols=list(range(6)))
    # st.dataframe(df)
    # # Print results.
    # for i, row in df.iterrows():
    #     print(row)
    #     col1, col2, col3 = st.columns(3)
        
    #     with col1:
    #         st.write(f"Row {row['name']}")
            
    #     with col2:
    #         st.write(f"{row['pet']}")
            
    #     with col3:
    #         if st.button(f"Send {row['name']}", key=f"button_{i}"):
    #             st.success(f"Sent unique value: {row['name']}")
    #             say_hello(row['name'])
    
    key_file = "encryption_key.key"
    # JSON 키 파일 경로와 Google Sheets 이름
    json_keyfile_path = "/workspaces/skns/planar-door-311704-e0e9b19240c0.json"
    sheet_name = "skns"
    sheet_name = "https://docs.google.com/spreadsheets/d/1gQqYD6j_yYoAyax0hTM2Gv3fTovY59yg__5DhCIpxaY/edit?gid=0#gid=0"

    worksheet_name = "202412"  # 선택하려는 탭 이름

    st.write(st.session_state)
    if st.session_state == {}:
        with st.form("my_form_1"):
            name = st.text_input("이름", key="name")
            tel = st.text_input("전화번호" , key="tel")
            
            save = st.form_submit_button(label="저장")

        if save:
            st.write(name)
            st.write(tel)
            print(name, tel)
            search_gsheet(name, tel)
            key = load_key_from_file(key_file)

            cipher_suite = Fernet(key)

            data = "Hello, world!"
            encrypted = cipher_suite.encrypt(data.encode())
            print("Encrypted:", encrypted)
            st.query_params = {"page": "apply"}
            st.session_state.name = name
            st.session_state.tel = tel

    elif st.session_state.get('FormSubmitter:my_form_1-저장') == True:
        with st.form("my_form_2"):
            g_res = search_gsheet(st.session_state['name'], st.session_state['tel'])
            st.write(g_res)
            st.write('session OK')
            st.write(f"{st.session_state['name']}님 안녕하세요.")
            # 사업장 선택하기
            g_select = ("-","B","C","D")
            option = st.selectbox("선택하세요",g_select, key='option')
            # disabled = True
            # if g_res:
            #     disabled = False
            name = st.text_input('이름',st.session_state['name'], key="name")
            tel = st.text_input('나이',st.session_state['tel'], key='tel')
            # if g_res is False:
            jumin = st.text_input('주민번호 (예 19990101-1234567)',key='jumin')

            save2 = st.form_submit_button(label="지원")
        if save2:
            st.session_state.name = name
            st.session_state.tel = tel
            st.session_state.jumin = jumin
            st.session_state.option = option

    elif st.session_state.get('FormSubmitter:my_form_2-지원') == True:

        data = {
            "Date": [arrow.now().format()],
            "Name": [st.session_state['name']],
            'Tel': [st.session_state['tel']],
            'option': [st.session_state['option']],
            'jumin': [st.session_state['jumin']]
        }
        df_new = pd.DataFrame(data)
        print(f"df_new : {df_new}")
        # Google Sheets 연결
        worksheet = connect_to_gsheet(json_keyfile_path, sheet_name, worksheet_name)
        new_row = [arrow.now().format('YYYY-MM-DD'), st.session_state['name'], st.session_state['tel'],st.session_state['option'],st.session_state['jumin']]
        worksheet.append_row(new_row)  

        # conn = st.connection("gsheets", type=GSheetsConnection)
        # existing_data = conn.read(sheet="202412")
        # print(existing_data)
        # last_row = len(existing_data)

        # # 데이터 추가 (row-wise)
        # conn.write(df_new, sheet="202412", start_row=last_row + 1)  # 마지막 행 아래에 추가        
        st.write('감사합니다.')
    else:
        st.write('ERROR')
        
        #     print(f"save2 : {save2}")
        # if save2:
        #     st.write(option)
        #     print(option)
        #     data = {
        #         "Date": arrow.now(),
        #         "Name": st.session_state['yname'],
        #         'Tel': st.session_state['ytel']
        #     }
        #     df_new = pd.DataFrame(data)

        #     # Google Sheets 연결
        #     conn = st.connection("gsheets", type=GSheetsConnection)
        #     existing_data = conn.read(sheet="202412")
        #     print(existing_data)
        #     last_row = len(existing_data)

        #     # 데이터 추가 (row-wise)
        #     conn.write(df_new, sheet="202412", start_row=last_row + 1)  # 마지막 행 아래에 추가
        # else:
        #     st.write("폼 제출 실패 또는 대기 중...")
        #     st.write("폼 제출 버튼 상태:", save2)
        #     st.write("입력된 이름:", name)
        #     st.write("입력된 전화번호:", tel)
        #     st.write("선택된 옵션:", option)

        # st.write("You selected:", option)

            


if __name__ == '__main__':
    main()