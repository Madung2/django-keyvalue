
from lxml import etree

def has_background_color(cell):
    """
    주어진 셀이 백그라운드 색을 가지고 있는지 확인합니다.
    
    :param cell: DOCX 테이블의 셀
    :return: 백그라운드 색이 있으면 True, 없으면 False
    """
    cell_xml = cell._element  # 셀의 XML 요소에 접근
    shd = cell_xml.find('.//w:shd', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})  # 네임스페이스를 포함하여 'w:shd' 태그 찾기
    
    if shd is not None:
        fill = shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill')  # 'fill' 속성 확인
        if fill and fill != "auto":  # 'auto'가 아닌 값이 있으면 배경색이 설정된 것
            print(f"Background color detected: {fill}")  # 배경색 출력 (디버깅용)
            return fill
    return False

class DocxTableTypeDetector():
    """ 테이블의 타입만 분리하는 class니까 그 안의 테이터를 칼 같이 추출할 필요는 없음.     
    _extract로 기본 추출을 하고 그걸 기반으로 결과값 리턴


    룰 00) 파란색, 회색, 등 여러색이 있을때 어떤걸 key cell color로 지정할 것인지 (일부 문서는 파란색, 회색이 모두 key cell color 이고, 일부 문서는 파란색이 키&회색이 밸류 색깔)
    룰 0) 연달아 0셀인 경우 같은 셀로 읽는다.

    룰1-1)테이블 0번 row에 key 셀이 계속 있는가? : first_row_is_all_keys
    룰1-2)테이블 0번 col에 key 셀이 계속 있는가? : first_cell_is_all_keys
    룰1-3) 0번 col이 아닌 col에 파란셀이 있는가? 단, 연달아 있으면 안됨. key_cell_is_scattered
    룰1-4) 예외 케이스로 first_row_is_all_keys인데 첫번째 줄에 '내용', '세부내용', '구분' 만 있으면 1차원 가로가 됨
    룰2) cell의 텍스트 값이 합계가 있으면 합계테이블
    """
    def __init__(self, table):
        self.TABLE_TYPE = {
            1: '1차원 가로',
            2: '1차원 세로',
            3: '1차원 가로 복수',
            4: '2차원 RDB',
            0: '확인되지 않은 형태'
        }
        self.table = table
        self.table_extract = self._extract()
        self.first_col_is_all_keys = self._first_col_is_all_keys()
        self.first_row_is_all_keys = self._first_row_is_all_keys()
        self.key_cell_is_scatterd = self._key_cell_is_scattered()
        self.exp_condition1 =self._check_exp_condition1()
        self.type_num = None
        self.type_name_kor = None
        self.detect_type()

    def _extract(self):
        """extract rows and cells and cell colors from the table
        [
            [
            {
                "txt":"차주(시행사)",
                "bg": "dbe5f1"    
            },
            {
                "txt":"샘플㈜ (그룹단일 : BB-, 특수금융 : A-)",
                "bg": false
                
            }
        ]]
        """
        rows = []
        for row in self.table.rows:
            row_data = []
            for cell in row.cells:
                cell_data={'txt':cell.text,'bg':has_background_color(cell)}
                row_data.append(cell_data)
            rows.append(row_data)
        return rows
    
    def _first_row_is_all_keys(self):
        """If all element in first row has 'bg' return True else False"""
        if not self.table_extract: #tabel_extract가 없으면 예외
            return False
        
        return all(row.get('bg') for row in self.table_extract[0])
    
    def _first_col_is_all_keys(self):
        """If all element in first row has 'bg' return True else False"""
        if not self.table_extract:
            return False
        
        return all(row[0].get('bg') for row in self.table_extract)
    
    def _key_cell_is_scattered(self):
        if not self.table_extract:
            return False
        
        for row in self.table_extract:
            if self.scattered_bg_found(row):
                return True # Consider it as scattered row
        return False
            # for cell in row:

    def _check_exp_condition1(self):
        #구분과 내용이 하나도 없는 경우에는  1번이고 아니면 2번
        if self.first_row_is_all_keys:
            first_row_texts = [cell.get('txt').replace(' ','').strip() for cell in self.table_extract[0]]
            # '구분'이나 '내용'이 하나도 없는 경우엠만 True
            first_row_texts = [t.replace(' ','').strip() for t in first_row_texts]
            print('t',first_row_texts)
            
            if all('구분' in t or '내용' in t for t in first_row_texts):
                return True
            if ('Tr.A' in t or 'Tr.B' in t for t in first_row_texts):
                return True
            
            return False
        return False
    
    def detect_type(self):
        # 여기서 3가지 타입 말고도 키가 
        con1 = self.first_col_is_all_keys
        con2 = self.first_row_is_all_keys
        con3 = self.key_cell_is_scatterd
        con4 = self.exp_condition1
        
        if con1 and not con2 and not con3:
            self.type_num =1
            
        elif con2 and not con3:
            print('con4:', con4)
            self.type_num = 1 if con4 else 2
        elif con3:
            self.type_num = 3
        else: # Unknown type num
            self.type_num = 0
        self.type_name_kor = self.TABLE_TYPE[self.type_num]

    @staticmethod
    def scattered_bg_found(row):
        """check if first bg cell and first none bg cell and second bg cell is found and return in boolean
        Args:
            row (list):[{"txt":"차주(시행사)","bg": "dbe5f1"},{"txt":"샘플㈜ (그룹단일 : BB-, 특수금융 : A-)", "bg": false}]
        """
        bg_found = False
        none_bg_found = False
        for cell in row:
            cell_is_bg = cell.get("bg", False)
            if not bg_found and cell_is_bg: # first bg_cell found
                bg_found = True
            if not none_bg_found and not cell_is_bg: #first none_bg_cell found
                none_bg_found = True
            if bg_found and none_bg_found and cell_is_bg: # second bg_cell found
                return True
        return False



class PDFTableTypeDetector():
    def __init__(self, table):
        self.TABLE_TYPE = {
            1: '1차원 가로',
            2: '1차원 세로',
            3: '1차원 가로 복수',
            4: '2차원 RDB',
            0: '확인되지 않은 형태'
        }
        self.table = table

    def _extract(self):
        pass
