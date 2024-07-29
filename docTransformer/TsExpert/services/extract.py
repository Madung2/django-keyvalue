import re
import environ
from docx import Document
from docx.table import _Cell, Table
from fuzzywuzzy import fuzz
import tempfile

from .utils import *
from .find_pos import PosFinder
from .convert_pdf import convert_docx_to_pdf
from DocTransformer.settings import env

class KeyValueExtractor:
    def __init__(self, doc, key_value):
        """
        KeyValueExtractor를 문서 객체로 초기화합니다.
        
        :param doc: 데이터 추출을 위한 문서 객체.
        """
        self.doc = doc  # 처리할 문서
        self.data = []  # 추출된 키-값 쌍을 저장할 리스트
        self.data_keys = set()  # 발견된 고유 키를 저장할 집합
        self.rep_keys = set()  # 발견된 대표 키를 저장할 집합
        self.key_value = key_value
        self.all_keys = [ele["key"] for ele in key_value]
        self.all_syn = [syn for item in key_value if item["synonym"] for syn in item["synonym"]["all"]]
        self.all_priority_syn = [syn for item in key_value if item["synonym"] for syn in item["synonym"]["priority"]]
        self.NoneTables = [item for item in key_value if item["is_table"] == False ]
        self.THRESHOLD = env.int('TSEXPERT_THRSHOLD')
    
    def filter_function(self, key):
        key = key.strip()
        all_keys= []
        # print("ALLSYN", self.all_syn)
        for item in self.all_syn:
            if fuzz.ratio(key, item)>=self.THRESHOLD:
                
                print('trheshold 통과:', key, item)
                rep = find_representatives(item, "all", self.key_value)
                return key, rep
        return None, None
    
    def extract_nested_table_data(self, nested_table):
        all_table_data =''
        for row in nested_table.rows:
            row_data = []
            for cell in row.cells:
                cell_text = cell.text.strip()
                row_data.append(cell_text)

            row = f"{' '.join(row_data)}: "
            all_table_data+=row
        #print(all_table_data)
        return all_table_data

    def process_specific_value(self, r, v, k, nested_table):
        # function should check if value needs to be processed again and run process
        keyword_ele =find_keyword_ele_by_key(r, self.key_value)
        specific = keyword_ele['specific']
        sp_word = keyword_ele['sp_word'] # spword can be list
        if sp_word:
            if any(word in k for word in sp_word):
                RUN_TYPE=1 # dont have to find specific word 
            else:
                RUN_TYPE=2 # need to split text and find specific word

        # run specific
        if specific:
            if RUN_TYPE ==1:
                return v, keyword_ele
            elif RUN_TYPE ==2:
                if nested_table:
                    # 여기에 해당하는 is_nested_table 을 추출해야하는 거임           
                    print(nested_table,  'this is nested_Tabl ')
                    v = self.extract_nested_table_data(nested_table)

                # else:
                text_list = re.split('\s{3,}|,\s*|:\s*', v)

                print('specific_running###############')
                print('specific=', specific)
                print(f"k:{k}, v:{v},  textlist = {text_list}")
                print('specific_running###############')

                for text in text_list:
                    if any(word in text for word in sp_word):
                        print(f'specific_running: {text},,{keyword_ele}')
                        return text, keyword_ele
        
        return v, keyword_ele

    def process_representatives_and_values(self, k, value, reps, data, data_keys, rep_keys, nested_table, table_number, row_num):
        print('4: 핵심 내용을 넣는 부분 process_representatives_and_values')

        for r in reps:
            v, keyword_ele = self.process_specific_value(r, value, k, nested_table)
            # print('r:',r, 'v:',v, "key_word_ele", keyword_ele)
            data.append([keyword_ele['key'], v, [table_number, row_num]])
            data_keys.add(k)
            rep_keys.add(r)

    def get_text_list(self):
        all_text_list = []
        num_paragraphs = min(25, len(self.doc.paragraphs))  # Get the minimum of 25 or the actual number of paragraphs
        for i in range(num_paragraphs):
            line_text = self.doc.paragraphs[i].text
            text_list = re.split(r'\(|\)|\/|\s{2,}', line_text)
            all_text_list += text_list
        processed_text_list = [ele for ele in all_text_list if ele != '']
        # print('processed_text_list', processed_text_list)
        return processed_text_list

    def process_none_table_keys(self):
        """
        테이블이 아닌 키-값 쌍을 처리하고 데이터 리스트에 추가합니다.
        
        :param none_tables: 키-값 쌍이 포함된 테이블이 아닌 요소들의 리스트.
        """
        none_table_data = []
        text_list = self.get_text_list()
        for ele in self.NoneTables:
            if ele["value"]!=[]: #블라인드펀드 등
                for fund_name in ele["value"]:
                    if fund_name in text_list:
                        none_table_data.append([ele['key'], fund_name, 1])
            else: #신청부팀점 신청직원
                # 1번: synonym=>priority로 찾는다
                for text in text_list:
                    if any(s in text for s in ele["synonym"]["priority"]):
                        none_table_data.append([ele['key'], text, 1])
                        break
                # pattern 으로 찾기
                pattern_list = ele['synonym']['pattern']
                if pattern_list !=[]:

                    for text in text_list:
                        if any( re.findall(p, text) for p in pattern_list):
                            # third element should be position information
                            none_table_data.append([ele['key'], text, 1])
        self.data += none_table_data  

    def find_nested_table(self, cell):
        for element in cell._element:
            if element.tag.endswith('tbl'):
                return Table(element, cell._parent._parent)
        return None

    def process_tables(self):
        """
        문서 내 테이블을 처리하고 키-값 쌍을 추출합니다.
        
        :return: 테이블에서 추출된 키-값 쌍의 리스트.
        """
        print('3: process_tables')

        table_data = []
        for i, table in enumerate(self.doc.tables):  
            table_number = i 
            if len(table.columns) >= 2:  # 테이블이 최소 2개의 열을 가지고 있는지 확인
                for i_r, row in enumerate(table.rows):  
                    
                    row_num = i_r
                    value_cell = row.cells[1]  
                    key = remove_numbers_special_chars(row.cells[0].text.strip())  # 첫 번째 셀에서 키를 추출
                    value = row.cells[1].text.strip()  # 두 번째 셀에서 값을 추출.
                    print(key,":",value)
                    nested_table = self.find_nested_table(value_cell)  # 값 셀에서 중첩된 테이블을 찾음
                    #############################################################################
                    # 여기까지 key란:원본문서의 테이블 [0]번 셀에 있는 텍스트 value란:원본문서의 [1]번 셀에 있는 텍스트
                    k, reps = self.filter_function(key)  # 키를 필터링하고 대표 키를 확인
                    # print(k, reps)
                    if k and (k not in self.data_keys):  # 키가 유효하고 이미 데이터 키 집합에 없는지 확인
                        self.process_representatives_and_values(k, value, reps, table_data, self.data_keys, self.rep_keys, nested_table, table_number, row_num)
                        # 대표 키와 값을 처리하고 데이터 리스트에 추가
        print('Table Data: ', table_data)
        for t in table_data:
            f = PosFinder(self.doc)
            f.set_target_info(t)
            pos = f.find_occurrence_position()
            t[2] = pos

        
        print('Table Data2: ', table_data)
        return table_data

    def extract_table_data_from_pdf(self):
        """
        PDF에서 테이블 데이터를 추출합니다.
        
        :return: PDF에서 추출된 테이블 데이터의 리스트.
        """
        table_data = []
        with tempfile.TemporaryDirectory() as tempdir:  # 임시 디렉토리를 생성
            tempdir = "/data"  # 임시 디렉토리 경로 설정
            temp_docx_path = f"{tempdir}/sample.docx"  # 임시 DOCX 파일 경로 설정
            temp_pdf_path = f"{tempdir}/sample.pdf"  # 임시 PDF 파일 경로 설정
            self.doc.save(temp_docx_path)  # 문서를 임시 DOCX 파일로 저장
            tables = convert_docx_to_pdf(temp_docx_path, temp_pdf_path)  # DOCX 파일을 PDF로 변환하고 테이블 추출
            if tables is not None:
                for table in tables:  # 추출된 각 테이블을 순회
                    df = table.df  # 테이블을 데이터프레임으로 변환
                    if len(df.columns) >= 2:  # 데이터프레임이 최소 2개의 열을 가지고 있는지 확인
                        extracted_data = df.iloc[:, :2].values.tolist()  # 첫 두 열의 데이터를 리스트로 추출
                        for [cell0_txt, cell1_txt] in extracted_data:  # 각 키-값 쌍을 순회
                            key = remove_unicode_characters(cell0_txt.strip())  # 첫 번째 셀에서 키를 추출
                            value = remove_unicode_characters(cell1_txt.strip())  # 두 번째 셀에서 값을 추출
                            k, reps = self.filter_function(key)  # 키를 필터링하고 대표 키를 확인
                            if k and (k not in self.data_keys):  # 키가 유효하고 이미 데이터 키 집합에 없는지 확인
                                self.process_representatives_and_values(k, value, reps, table_data, self.data_keys, self.rep_keys, nested_table=None)
                                # 대표 키와 값을 처리하고 데이터 리스트에 추가
        return table_data

    def extract_data(self):
        """
        문서에서 데이터를 추출합니다.
        
        :return: 추출된 모든 데이터의 리스트.
        """
        table_data = self.process_tables()  # 테이블 데이터 처리
        # if not table_data:
        #     print('Extracting table data from PDF...')  # 테이블 데이터가 없으면 PDF에서 데이터 추출 시도
        #     table_data = self.extract_table_data_from_pdf()
        self.process_none_table_keys()  # 테이블이 아닌 키-값 쌍 처리
        #print('Table data: ', table_data)  # 추출된 테이블 데이터를 출력
        self.data += table_data  # 추출된 테이블 데이터를 데이터 리스트에 추가
        return self.data  # 최종 데이터를 반환
    
    @staticmethod
    def remove_duplication(data):

        seen = set()  # 중복을 체크하기 위한 집합
        unique_data = []  # 중복이 제거된 요소를 저장할 리스트
        for ele in data:
            if ele[0] not in seen:
                seen.add(ele[0])  # 집합에 요소 추가
                unique_data.append(ele)  # 결과 리스트에도 요소 추가
        
        return unique_data