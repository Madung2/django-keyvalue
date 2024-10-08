import re
import environ
from docx import Document
from docx.table import _Cell, Table
from fuzzywuzzy import fuzz
import tempfile
from docx.oxml.ns import qn
from .utils import *
from .find_pos import PosFinder
from .convert_pdf import convert_docx_to_pdf
from DocTransformer.settings import env


class NestedTableExtractor:
    def __init__(self, doc, key_value):
        self.doc = doc
        self.target_keys = [k_v['key'] for k_v in key_value if k_v['extract_all_json']]  
        # self.target_texts = 

    @staticmethod
    def remove_escape(input_text):
        # 정규 표현식을 사용하여 모든 이스케이프 문자를 찾아서 빈 문자열로 치환
        return re.sub(r'[\n\t\r\f\v]', '', input_text)
        
    @staticmethod
    def cell_has_background(cell):
        """
        Checks if the given cell has a background color.
        To make it work we need to use xml library and show namespace
        """
        cell_xml = cell._tc.get_or_add_tcPr()
        shd = cell_xml.find(qn('w:shd'))
        if shd is not None and shd.get(qn('w:fill')) != 'auto':
            return True
        return False

    def is_vertical_table(self, table):
        """
        Checks if the given table is a vertical table, meaning all cells in the first row have background color.
        """
        for cell in table.rows[0].cells:
            if not self.cell_has_background(cell):
                return False
        return True

    def extract_nested_tables(self, element):
        """
        Recursively extracts nested tables from the given document element and checks for background color in cells.
        """
        nested_tables_content = []

        for table in element.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.tables:
                        nested_table = cell.tables[0]  # Assume only one nested table per cell
                        nested_table_data = []
                        first_row_has_color = False
                        for i, nested_row in enumerate(nested_table.rows):
                            nested_row_data = []
                            for nested_cell in nested_row.cells:
                                if nested_cell.tables:
                                    deeper_nested_tables = self.extract_nested_tables(nested_cell)
                                    nested_row_data.append(deeper_nested_tables)
                                else:
                                    if self.cell_has_background(nested_cell):
                                        nested_row_data.append((nested_cell.text, True))
                                        if i == 0:  # Check if the first row has color
                                            first_row_has_color = True
                                    else:
                                        nested_row_data.append((nested_cell.text, False))
                            nested_table_data.append(nested_row_data)
                        if first_row_has_color and self.is_vertical_table(nested_table):
                            nested_tables_content.append(nested_table_data)
                        break  # Break after finding the first nested table in the cell

        return nested_tables_content

    def extract_tables_with_background(self):
        """
        Extracts nested tables with first row colored from the given docx document.
        """
        return self.extract_nested_tables(self.doc)

    @staticmethod
    def find_target_in_tables(tables, target_text):
        """
        Finds target_text in the first column or row of each table.
        Returns the table index, location (row or column), and cell content.
        """
        results = []
        for table_index, table in enumerate(tables):
            # Check the first row
            for col_index, cell in enumerate(table[0]):
                if isinstance(cell, list):
                    continue
                cell_text, has_background = cell
                if target_text in cell_text:
                    print('TARGET:::::', (table_index, 'row', col_index, cell_text))
                    results.append((table_index, 'row', col_index, cell_text))

            # Check the first column
            for row_index, row in enumerate(table):
                if isinstance(row[0], list):
                    continue
                cell_text, has_background = row[0]
                if target_text in cell_text:
                    print('TARGET:::::', (table_index, 'column', row_index, cell_text))
                    results.append((table_index, 'column', row_index, cell_text))

        return results

    def find_table_type(self, tables, target_text):
        """
        Determines the table type based on whether '구분' is present in the target_text row or column.
        Returns 'type2' if found, otherwise 'type1'.
        """
        gu_bun_text = '구분'
        
        for table in tables:
            all_target_col = []
            gu_bun_col = -1
            
            # Find all target columns containing target_text
            for col_index, cell in enumerate(table[0]):
                if isinstance(cell, list):
                    continue
                cell_text, has_background = cell
                if target_text in cell_text:
                    all_target_col.append(col_index)
            
            # Find the gu_bun column from the target columns
            for col_index in all_target_col:
                for row in table:
                    if isinstance(row[col_index], list):
                        continue
                    cell_text, has_background = row[col_index]
                    if gu_bun_text in cell_text:
                        gu_bun_col = col_index
                        break
                if gu_bun_col != -1:
                    break
            
            # Check if gu_bun_col was found in target columns
            if gu_bun_col != -1:
                return 'type2'

        return 'type1'

    def create_dictionary_for_type1(self, table, target_text):
        """
        Creates a dictionary for type1 table where keys are below '구분' and values are below target_text.
        """
        keys = []
        values = []

        # Find the column index for '구분' and 'target_text'
        gu_bun_col = -1
        target_col = -1

        for col_index, cell in enumerate(table[0]):
            if isinstance(cell, list):
                continue
            cell_text, has_background = cell
            if cell_text.startswith('구분'):
                gu_bun_col = col_index
            if target_text in cell_text:
                target_col = col_index

        # Extract keys and values based on found column indices
        if gu_bun_col != -1 and target_col != -1:
            for row in table[1:]:
                if len(row) > gu_bun_col:
                    gu_bun_cell_text, _ = row[gu_bun_col]
                    keys.append(self.remove_escape(gu_bun_cell_text))
                if len(row) > target_col:
                    target_cell_text, _ = row[target_col]
                    values.append(self.remove_escape(target_cell_text))

        return dict(zip(keys, values))

    @staticmethod
    def split_cell_text(cell_text):
        """
        Splits the cell text by newlines and returns a list of clean texts.
        """
        return [line for line in cell_text.split('\n') if line.strip()]

    def create_dictionary_for_type2(self, table, target_text):
        """
        Creates a dictionary for type2 table where keys are in the '구분' row or column and values are in the target_text row or column.
        """
        dictionary = {}
        gu_bun_text = '구분'
        
        all_target_col = []
        target_col = -1
        gu_bun_col = -1

        # Find all target columns containing target_text
        for col_index, cell in enumerate(table[0]):
            if isinstance(cell, list):
                continue
            cell_text, has_background = cell
            if target_text in cell_text:
                all_target_col.append(col_index)

        # Find the gu_bun column from the target columns
        for col_index in all_target_col:
            for row in table:
                if isinstance(row[col_index], list):
                    continue
                cell_text, has_background = row[col_index]
                if gu_bun_text in cell_text:
                    gu_bun_col = col_index
                    break
            if gu_bun_col != -1:
                break

        # Ensure both target_col and gu_bun_col are found
        if gu_bun_col != -1:
            for row in table[1:]:
                if len(row) > gu_bun_col:
                    keys = self.split_cell_text(row[gu_bun_col][0])
                    values = self.split_cell_text(row[gu_bun_col+1][0])  # Assuming values are in the next column of gu_bun_col
                    for key, value in zip(keys, values):
                        dictionary[key] = value

        return dictionary

    def extract_all_data(self):
        """
        Extracts all data for each target key and returns a dictionary with target keys as keys and their respective data as values.
        """
        tables_with_background = self.extract_tables_with_background()
        results = {}
        
        for target_key in self.target_keys:
            target_tables = self.find_target_in_tables(tables_with_background, target_key)
            
            for table_index, _, _, _ in target_tables:
                table_type = self.find_table_type(tables_with_background, target_key)
                if table_type == 'type1':
                    results[target_key] = self.create_dictionary_for_type1(tables_with_background[table_index], target_key)
                else:
                    results[target_key] = self.create_dictionary_for_type2(tables_with_background[table_index], target_key)
        
        return results

    


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
        self.key_value = [k_v for k_v in key_value if not k_v['extract_all_json']]  
        self.all_keys = [ele["key"] for ele in self.key_value]
        self.all_syn = [syn for item in self.key_value if item["synonym"] for syn in item["synonym"]["all"]]
        self.all_priority_syn = [syn for item in self.key_value if item["synonym"] for syn in item["synonym"]["priority"]]
        self.NoneTables = [item for item in self.key_value if item["is_table"] == False ]
        self.THRESHOLD = env.int('TSEXPERT_THRSHOLD')
    
    def filter_function(self, key):
        key = key.strip()
        all_keys= []
        for item in self.all_syn:
            if fuzz.ratio(key, item)>=self.THRESHOLD:
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
        return all_table_data

    def process_specific_value(self, r, v, k, nested_table):
        # function should check if value needs to be processed again and run process
        keyword_ele =find_keyword_ele_by_key(r, self.key_value)

        specific = keyword_ele['specific']
        sp_word = keyword_ele['sp_word'] # spword can be list
#        second_key = keyword_ele['second_key']


        if sp_word:
            if any(word in k for word in sp_word):
                RUN_TYPE=1 # dont have to find specific word 
            else:
                RUN_TYPE=2 # need to split text and find specific word

        # run specificFprocess_specific_value
        if specific:
            if RUN_TYPE ==1:
                return v, keyword_ele
            elif RUN_TYPE ==2:
                if nested_table:
                    # 여기에 해당하는 is_nested_table 을 추출해야하는 거임           
                    v = self.extract_nested_table_data(nested_table)

                # else:
                text_list = re.split(r'\s{3,}|,\s*|:\s*', v)                
                for text in text_list:
                    if any(word in text for word in sp_word):
                        # print(f'specific_running: {text},,{keyword_ele}')
                        return text, keyword_ele
        return v, keyword_ele

    def process_representatives_and_values(self, k, value, reps, data, data_keys, rep_keys, nested_table, table_number, row_num):
        print('4: 핵심 내용을 넣는 부분 process_representatives_and_values')

        for r in reps:
            v, keyword_ele = self.process_specific_value(r, value, k, nested_table)
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
                    
                    #1) 옵션 1 첫번째 셀에서 키를 추출, & 2번째 셀에서밸류의 값을 추출..
                    row_num = i_r
                    value_cell = row.cells[1]
                    key = remove_numbers_special_chars(row.cells[0].text.strip())  # 첫 번째 셀에서 키를 추출
                    value = row.cells[1].text.strip()  # 두 번째 셀에서 값을 추출.

                    # 네스티드 테이블은 따로 추출
                    nested_table = self.find_nested_table(value_cell)  # 값 셀에서 중첩된 테이블을 찾음

                    
                    
                    #############################################################################
                    # 여기까지 key란:원본문서의 테이블 [0]번 셀에 있는 텍스트 value란:원본문서의 [1]번 셀에 있는 텍스트
                    k, reps = self.filter_function(key)  # 키를 필터링하고 대표 키를 확인
                    # print(k, reps)
                    if k and (k not in self.data_keys):  # 키가 유효하고 이미 데이터 키 집합에 없는지 확인
                        self.process_representatives_and_values(k, value, reps, table_data, self.data_keys, self.rep_keys, nested_table, table_number, row_num)
                        # 대표 키와 값을 처리하고 데이터 리스트에 추가
                    
                    #2) 혹시 테이블의 0번째 셀이 아닌곳에 백그라운드 색이 적용되어 있고 그 오른쪽에도 셀이 있다면
                    # 백그라운드색이 있는곳도 key로 추출하고 밸류는 그 오른쪽 셀로 적용 -> 이 경우에는 한줄에 여러개의 키밸류가 있을 수 있음
                    for j, cell in enumerate(row.cells):
                        if j > 0 and has_background_color(cell):  # 0번째 셀이 아닌 곳에서 백그라운드 색이 있을 경우
                            key = remove_numbers_special_chars(cell.text.strip())  # 배경색이 있는 셀에서 키를 추출
                            if j + 1 < len(row.cells):  # 오른쪽 셀 값 추출
                                value = row.cells[j + 1].text.strip()
                                k, reps = self.filter_function(key)
                                if k and (k not in self.data_keys):
                                    self.process_representatives_and_values(k, value, reps, table_data, self.data_keys, self.rep_keys, nested_table, table_number, row_num)

        # print('Table Data: ', table_data)
        for t in table_data:
            f = PosFinder(self.doc)
            f.set_target_info(t)
            pos = f.find_occurrence_position()
            t[2] = pos

        
        # print('Table Data2: ', table_data)
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


    def treat_extract_all_json(self):
        ### 1) get_all_nested_table_data

        ### 2) find if it's vertical table

        ### 3) find 'target text' from col[0] or row[0]

        ### 4) find table type by checking word '구분' : if it's in same column as target_text it's table type 2 and if it's in [0] column only it's table type 1


        pass

    def find_value_match_first_row(self, first_row_cells, matching_row_cells, second_key_list):
        """
        이 함수는 first_row_cells에서 second_key_list에 있는 키 중 하나를 찾아서,
        해당 키와 매칭되는 matching_row_cells의 값을 반환합니다.

        매개변수:
        first_row_cells (list): 테이블 첫 번째 행의 셀 목록 (첫 번째 열 제외).
        matching_row_cells (list): 매칭된 행의 셀 목록 (첫 번째 열 제외).
        second_key_list (list): first_row_cells에서 매칭할 수 있는 키들의 리스트.

        반환값:
        str 또는 None: 매칭된 키에 해당하는 matching_row_cells의 텍스트.
                    매칭되는 키가 없으면 None을 반환합니다.

        함수 작동 방식:
        - 먼저 second_key_list에 있는 각 키에 대해 first_row_cells에서 정확히 일치하는 
        항목이 있는지 확인합니다.
        - 정확히 일치하는 키가 있으면 해당 키의 인덱스를 사용해 matching_row_cells에서 
        같은 인덱스의 값을 반환합니다.
        - 정확히 일치하는 키가 없으면, fuzz.ratio를 사용해 80% 이상의 유사성을 가진 항목을 
        찾아서 그에 해당하는 값을 반환합니다.
        """
        # Iterate over the second_key_list and find any key that matches in first_row_cells
        for key in second_key_list:
            # Try exact match first
            if key in first_row_cells:
                index = first_row_cells.index(key)
            else:
                # If no exact match, use fuzz.ratio to find approximate matches
                index = -1
                for i, cell_text in enumerate(first_row_cells):
                    if fuzz.ratio(key, cell_text) >= 70:
                        index = i
                        break  # Stop at the first match
            
            # If we found a valid index, return the corresponding matching row cell
            if index != -1 and index < len(matching_row_cells):  # Ensure index is valid and within bounds
                return matching_row_cells[index]
        
        return None  # Return None if no key from second_key_list is found


    def find_matching_rows(self, has_second_dict_elements):
        """
        이 함수는 DOCX 문서의 테이블을 순회하면서 첫 번째 셀에 우선순위 키워드(priority)가 
        있는 행을 찾아, 매칭된 행에서 관련 텍스트를 추출합니다.

        매개변수:
        docx_path (str): DOCX 파일 경로.
        has_second_dict_elements (list): 우선순위 키워드('priority')와 두 번째 키('second_key')를 포함한 
                                        딕셔너리 목록. 'priority'는 행의 첫 번째 셀에서 검색할 키워드 리스트이고,
                                        'second_key'는 각 테이블의 첫 번째 행과 매칭할 키 리스트입니다.

        반환값:
        list: (first_row_cells, matching_row_cells)의 튜플 리스트를 반환합니다. 
            first_row_cells는 테이블 첫 번째 행의 셀들이고, matching_row_cells는 우선순위 키워드와 매칭된 행의 셀들입니다.

        함수 작동 방식:
        - DOCX 파일을 불러오고, 문서 내 모든 테이블을 순회합니다.
        - 각 테이블의 첫 번째 행을 가져오고, 이후 행의 첫 번째 셀과 우선순위 키워드를 비교합니다.
        - 정확한 매칭 또는 fuzz.ratio를 사용해 95% 이상의 유사도가 있는 경우 매칭된 행을 찾습니다.
        - 매칭된 행에 대해 find_value_match_first_row를 호출하여 second_key를 기준으로 값을 추출합니다.
        - 해당 값을 정리(clean_text)한 후 출력하고, 결과 리스트에 모든 행 데이터를 저장합니다.
        """
        
        result = []
        
        # Loop through all tables in the DOCX file
        for element in has_second_dict_elements:
            priority_keywords = element['synonym']['priority']
            second_keys = element['second_key']
            for table in self.doc.tables:
                if len(table.rows) == 0:
                    continue

                # Get the first row of the table
                first_row_cells = [cell.text.strip() for cell in table.rows[0].cells] [1:]

                # Loop through the rest of the rows
                for row in table.rows[1:]:
                    first_cell_text = row.cells[0].text.strip()
                    
                    # Check if the first cell text matches any priority keyword
                    if (first_cell_text in priority_keywords) or any(fuzz.ratio(first_cell_text, priority_key) >= 95 for priority_key in priority_keywords):
                        # Collect other cells in the matching row
                        matching_row_cells = [cell.text.strip() for cell in row.cells[1:]]
                        
                        # Append the result as a tuple (first row cells, matching row cells)
                        
                        #first_row = ['제조사명\n(수입업자명)', '모델명', 'KC 인증번호']
                        #matching_row = ['㈜익스프레스리프트', 'EXPRESS-\nAS380(MRL)', 'AAB10-H005-19002']

                        found_text= self.find_value_match_first_row(first_row_cells, matching_row_cells, second_keys)
                        cleaned_found_text = clean_text(found_text)
                        # found_text should be value of the target keyword
                        result.append([element['key'], cleaned_found_text, 0])


        print('')
        return result

    def treat_second_key(self):
        """
        """
        has_secondkey_dict_elements = []
        for ele in self.key_value:
            if ele['second_key']:
                has_secondkey_dict_elements.append(ele)


        print('%%%%%%%%%%%%%%%%%%')
        print(has_secondkey_dict_elements)
        print('%%%%%%%%%%%%%%%%%%')

        return self.find_matching_rows(has_secondkey_dict_elements)


    def update_table_data(self, table_data, second_key_data):
        # 각 second_key_data의 0번째 요소를 기준으로 table_data와 비교
        for sec_row in second_key_data:
            sec_key = sec_row[0]
            
            # table_data에서 0번째 요소가 겹치는 항목을 찾고 교체
            for idx, table_row in enumerate(table_data):
                if table_row[0] == sec_key:
                    table_data[idx] = sec_row  # 해당 row를 second_key_data의 row로 교체
                    break
        
        return table_data

    def extract_data(self):
        """
        문서에서 데이터를 추출합니다.
        
        :return: 추출된 모든 데이터의 리스트.
        """
        ## ✯ MAIN FUNCTION ✯ 
        table_data = self.process_tables()  # 테이블 데이터 처리
        table_data = self.add_not_extracted_column(table_data)
        second_key_data= self.treat_second_key()
        # table_data += second_key_data
        table_data = self.update_table_data(table_data, second_key_data)

        vertical_data = self.treat_extract_all_json()

        self.process_none_table_keys()  # 테이블이 아닌 키-값 쌍 처리
        self.data += table_data  # 추출된 테이블 데이터를 데이터 리스트에 추가
        return self.data  # 최종 데이터를 반환
    
    def add_not_extracted_column(self, table_data):
        all_extracted_keys = [k for [k, v, pos] in table_data]
        for a in self.all_keys: 
            if a not in all_extracted_keys:
                table_data.append([a, '', 0])
        return table_data
    
    @staticmethod
    def remove_duplication(data):

        seen = set()  # 중복을 체크하기 위한 집합
        unique_data = []  # 중복이 제거된 요소를 저장할 리스트
        for ele in data:
            # ele[0]이 리스트인 경우 튜플로 변환해서 처리
            key = tuple(ele[0]) if isinstance(ele[0], list) else ele[0]
            if key not in seen:
                seen.add(key)  # 집합에 요소 추가
                unique_data.append(ele)  # 결과 리스트에도 요소 추가
        
        return unique_data
