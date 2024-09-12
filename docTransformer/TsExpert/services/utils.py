import re
from konlpy.tag import Okt

def remove_numbers_special_chars(text):
    # 숫자와 특수문자를 제거하는 정규 표현식
    cleaned_text = re.sub(r'[0-9\W]+', '', text)
    return cleaned_text


def remove_special_characters(text):
    # remove [,] & (,) 
    cleaned_text = re.sub(r'[,\[\]()]', '', text)
    return cleaned_text

def remove_special_characters_from_list(ls):
    cleaned_list = []
    for text in ls:
        # [,], (,) 제거
        cleaned_text = re.sub(r'[,\[\]()]', '', text)
        cleaned_list.append(cleaned_text)
    return cleaned_list

def remove_unicode_characters(text):
    # \uf0a7 유니코드 문자와 \n (줄바꿈)을 제거
    text = re.sub(r'\uf0a7|\n', '', text)
    return text

def find_by_key(keyword, target_key):
    for item in keyword:
        if item["key"] == target_key:
            return item  # get 메소드 사용으로 키가 없는 경우 None 반환
    raise ValueError(f"Key '{target_key}' not found in keyword.")  # 키가 없는 경우 예외 발생


def extract_first_float(text):
    # 소수점을 포함할 수 있는 숫자 패턴을 찾습니다.
    match = re.search(r'\d+(\.\d+)?', text)
    if match:
        # 찾은 숫자를 float으로 변환합니다.
        return float(match.group())
    return None


def get_text_list(doc):
    all_text_list = []
    for i in range(25):
        line_text = doc.paragraphs[i].text
        text_list = re.split(r'\(|\)|\/|\s{2,}', line_text)
        all_text_list+= text_list
    processed_text_list = [ele for ele in all_text_list if ele!='']
    #print('processed_text_list', processed_text_list)
    return processed_text_list


    #v2
def split_value(text, split_keywords):
    # 텍스트를 분리할 최소 위치를 찾기
    split_index = None
    for keyword in split_keywords:
        found_index = text.find(keyword)
        if found_index != -1:
            if split_index is None or found_index < split_index:
                split_index = found_index

    # 최소 위치에 따라 텍스트 분리
    if split_index is not None:
        before_part = text[:split_index].strip()
        after_part = text[split_index:].strip()
        return [before_part, after_part]
    else:
        return [text]  # 키워드가 없는 경우 전체 텍스트를 반환


def find_representatives(item, type_str, keyword):
  #function should return all the representatives with key as synonymfilter_function
    represent = []
    for ele in keyword:
      if item in ele["synonym"][type_str]:
          represent.append(ele["key"])
    return represent


def find_keyword_ele_by_key(r, keyword):
    for ele in keyword:
      if ele['key'] == r:
        return ele
    print(f'Error in find_keyword_ele_by_key: no key name {r} found!')
    return "This is error"

def tag_text(text):
    # Okt object
    okt = Okt()

    # text tokenizing
    tokens = okt.pos(text, norm=True, stem=True)

    tagged_tokens = []
    for word, tag in tokens:
        # 숫자 판별
        if re.match(r'^\d+$', word):
            tagged_tokens.append((word, 'Number'))
        # 날짜 판별 (간단한 예: YYYY.MM.DD 형식)
        elif re.match(r'\d{4}\.\d{1,2}\.\d{1,2}', word):
            tagged_tokens.append((word, 'Date'))
        else:
            tagged_tokens.append((word, tag))

    return tagged_tokens


from docx.oxml.ns import qn

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
            return True
    return False
    
def clean_text(text):
    """
    Removes unwanted characters like newlines (\n) and tabs (\t) from the text.
    """
    if text is None:
        return None
    return text.replace('\n', '').replace('\t', '').strip()