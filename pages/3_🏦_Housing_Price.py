
import streamlit as st
import requests

# 페이지 기본 설정 
st.set_page_config(
    page_icon =  ":shark:",
    page_title = "sophie의 스트림릿 배포하기",
    layout = 'wide'
)

st.subheader("공시지가")


import pandas as pd
import requests
import json

from bs4 import BeautifulSoup
import pandas as pd
import urllib.request

req = urllib.request


from bs4 import BeautifulSoup
import pandas as pd
import urllib.request

req = urllib.request

def getRTMSDataSvcAptTrade(LAWD_CD,DEAL_YMD,serviceKey): 
    url="http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade" 
    url=url+"?&LAWD_CD="+LAWD_CD
    url=url+"&DEAL_YMD="+DEAL_YMD
    url=url+"&serviceKey="+serviceKey
    
    xml = req.urlopen(url)
    result = xml.read()
    soup = BeautifulSoup(result, 'lxml-xml')    
    
    items = soup.findAll("item")
    aptTrade = pd.DataFrame()
    
    for item in items:
        dealAmount          = item.find("거래금액").text
        buildYear           = item.find("건축년도").text
        dealYear            = item.find("년").text
        dong                = item.find("법정동").text
        apartmentName       = item.find("아파트").text
        dealMonth           = item.find("월").text
        dealDay             = item.find("일").text
        areaForExclusiveUse = item.find("전용면적").text
        jibun               = item.find("지번").text
        regionalCode        = item.find("지역코드").text
        floor               = item.find("층").text
        buildYear           = item.find("건축년도").text
        
        temp = pd.DataFrame(([[dong,apartmentName,dealAmount,buildYear,dealYear,dealMonth,dealDay,areaForExclusiveUse,jibun,regionalCode,floor]])
        , columns=["dong","apartmentName","dealAmount","buildYear","dealYear","dealMonth","dealDay","areaForExclusiveUse","jibun","regionalCode","floor"]) 
        aptTrade=pd.concat([aptTrade,temp])
    
    aptTrade=aptTrade.reset_index(drop=True)
    return aptTrade




def get_pnus(keyword):
    cd_dong = pd.read_csv('./data/법정동 기준 시군구 단위.csv')
    cd_dong_selected = cd_dong[cd_dong.시군구명.str.contains(keyword)]
    return cd_dong_selected


def main():
    st.title("실거래가 지역별 조회 및 필터링 물건 조회")

    api_key = st.text_input("API KEY를 입력하세요")
    stdrYear = st.text_input("기간을 입력하세요")
    stdrYear = str(stdrYear)


    # 법정동 검색 후 multiselect box 생성
    area = st.text_input("지역을 입력하세요")
    cd_dong_selected = get_pnus(area) 
    selected_pnus = st.multiselect("시군구명:",
    options=list(cd_dong_selected['시군구명'])
    , key="multiselect") 

        
    if 'pnu_cds' not in st.session_state:
        st.session_state['pnu_cds'] = 0 
    st.session_state['pnu_cds'] = 0 
    st.session_state["pnu_cds"] = cd_dong_selected[cd_dong_selected['시군구명'].isin(selected_pnus)]   

    serviceKey = requests.utils.unquote(api_key)

 
    areaForExclusiveUse = st.text_input("전용면적 구간을 입력하세요")

    if "table_data" not in st.session_state:
        st.session_state["table_data"] = []

    if st.button("Search"):
        st.write("선택된 지역들의 정보:")
        st.session_state["table_data"] = pd.DataFrame(columns =[
          "dong","apartmentName","dealAmount","buildYear","dealYear","dealMonth","dealDay","areaForExclusiveUse","jibun","regionalCode","floor"] )

        for selected_pnu_cd in st.session_state["pnu_cds"]['시군구_코드_법정동기준']:
            selected_pnu_cd = str(selected_pnu_cd)
            house_price = getRTMSDataSvcAptTrade(selected_pnu_cd, stdrYear, serviceKey)
            st.session_state["table_data"] = st.session_state["table_data"].append(house_price)
            
        st.session_state["table_data"] = st.session_state["table_data"][st.session_state["table_data"]['areaForExclusiveUse'] == areaForExclusiveUse]
        st.session_state["table_data"] = st.session_state["table_data"].sort_values(by=['dealAmount'])      
        st.session_state["table_data"].columns = ['법정동','아파트', '거래금액','건축년도','년','월','일','전용면적','지번','지역코드','층']




        st.table(st.session_state["table_data"])

if __name__ == "__main__":
    main()


