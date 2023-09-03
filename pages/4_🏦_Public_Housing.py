
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
# import openpyxl
# from openpyxl.workbook import Workbook

def ApartHousingPriceService(api_key, pnu, stdrYear):
    pageNo =1
    house_price = []

    while True:
        url = "http://apis.data.go.kr/1611000/nsdi/ApartHousingPriceService/attr/getApartHousingPriceAttr?serviceKey=%s&pnu=%s&stdrYear=%s&format=json&numOfRows=1000&pageNo=%s" % (api_key, pnu, stdrYear, pageNo) 
        print(url)
        response = requests.get(url)
        result = response.text
        data = json.loads(result)

        if int(data['apartHousingPrices']['totalCount']) != len(house_price):
            house_price += data['apartHousingPrices']['field']
            pageNo += 1
        else:
            break

        if len(house_price) > 0 :
            house_price = pd.DataFrame(house_price)
        else:
            house_price = pd.DataFrame()

        return house_price

def get_pnus(keyword):
    pnu_cd = pd.read_csv('./data/pnu_code.csv')
    pnu_cd = pnu_cd[pnu_cd['폐지여부'] == '존재']
    pnu_cd_selected = []
    pnu_cd_selected = pnu_cd[pnu_cd.법정동명.str.contains(keyword)]
    return pnu_cd_selected


def main():
    st.title("공동주택 가격 지역별 조회 및 필터링 물건 조회")

    api_key = st.text_input("API KEY를 입력하세요")
    stdrYear = st.text_input("기간을 입력하세요")
    # 법정동 검색 후 multiselect box 생성
    area = st.text_input("지역을 입력하세요")
    pnu_cd_selected = get_pnus(area) 
    selected_pnus = st.multiselect("법정동:",
    options=list(pnu_cd_selected['법정동명'])
    # default=["경기도 부천시 원미동"]
    , key="multiselect") 

        
    if 'pnu_cds' not in st.session_state:
        st.session_state['pnu_cds'] = 0
        # st.session_state.pnu_cds = pnu_cd_selected[pnu_cd_selected['법정동명'].isin(selected_pnus)]   
    st.session_state['pnu_cds'] = 0 
    st.session_state["pnu_cds"] = pnu_cd_selected[pnu_cd_selected['법정동명'].isin(selected_pnus)]   

    filter_am_st = st.number_input("공시가격 하단 범위 입력하세요 ex) 0")
    filter_am_end = st.number_input("공시가격 상단 범위 입력하세요 ex) 100000000")
    serviceKey = requests.utils.unquote(api_key)

    if "table_data" not in st.session_state:
        st.session_state["table_data"] = []


    if st.button("Search"):
        st.write("선택된 지역들의 정보:")
        st.session_state["table_data"] = pd.DataFrame(columns =['pnu','ldCode','ldCodeNm','regstrSeCode','regstrSeCodeNm',
'mnnmSlno','stdrYear','stdrMt','aphusCode','aphusSeCode','aphusSeCodeNm','spclLandNm','aphusNm',
'dongNm','floorNm','hoNm','prvuseAr','pblntfPc','lastUpdtDt'] )

        for selected_pnu_cd in st.session_state["pnu_cds"]['법정동코드']:
            house_price = ApartHousingPriceService(serviceKey, selected_pnu_cd, stdrYear)
            house_price = house_price.astype({'pblntfPc':'float32'})
            print('type',house_price.dtypes)

            # house_price_filtered = house_price[house_price['pblntfPc'] <= filter_am]
            house_price_filtered = house_price[house_price['pblntfPc'].between(filter_am_st,filter_am_end)]
            # st.session_state["table_data"] = st.session_state["table_data"][st.session_state["table_data"]['areaForExclusiveUse'].between(filter_am_st,filter_am_end)]
            st.session_state["table_data"] = st.session_state["table_data"].append(house_price_filtered)

        st.session_state["table_data"] = st.session_state["table_data"].sort_values(by=['pblntfPc'])        
        st.session_state["table_data"].columns = ['고유번호','법정동코드','법정동명','특수지구분코드','특수지구분명','지번',
'기준년도','기준월','공동주택코드','공동주택구분코드','공동주택구분명','특수지명','공동주택명','동명','층명',
'호명','전용면적','공시가격','데이터기준일자'] 

        st.table(st.session_state["table_data"])
        
    NM = st.text_input("파일명을 지정하세요")
    if st.button("엑셀 다운로드"):
        
        # if not st.session_state["table_data"]:
        #     st.warning("생성된 데이터가 없습니다.")
        # else:
        df = pd.DataFrame(st.session_state["table_data"])
        print('df',df)
        df.to_excel("공동주택가격_"+ NM + ".xlsx", index=False)
        st.success("엑셀 파일 정상적으로 생성되었습니다.")






if __name__ == "__main__":
    main()


