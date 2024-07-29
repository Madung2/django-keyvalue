import re
from mecab import MeCab
from .utils import *

## rules about type
# if "string" : don't edit result
# if "name" : result should find korean name
# if "department" : result should find department
# if "year" : result should multiply by 12 (year->month)
# if "amount" : result should find '억' and if so multiply by 100000000
# if "percentage" : find percentage

def find_spword_and_string(text_list, spwords, target_str):
    # 1순위: spwords 리스트 중 하나와 target_str가 함께 있는 타겟 찾기
    for text in text_list:
        if any(spword in text for spword in spwords) and target_str in text:
            return text
    # 2순위: target_str가 있는 첫 번째 타겟 찾기
    for text in text_list:
        if target_str in text:
            return text
    # 3순위: 첫 번째 요소 반환
    return text_list[0] if text_list else None



def combine_money_number_tags(tagged_values):
    combined = []
    i = 0
    while i < len(tagged_values):
        word, tag = tagged_values[i]
        
        if '조' in word and i + 1 < len(tagged_values) and '억' in tagged_values[i + 1][0]:
            # '조' 태그와 다음 '억' 태그를 합침
            next_word, next_tag = tagged_values[i + 1]
            combined_word = word + next_word
            combined.append((combined_word, tag))
            i += 1  # 다음 태그를 이미 처리했으므로 인덱스를 추가로 증가
        else:
            combined.append((word, tag))
        i += 1
    
    return combined

def process_string(value, target_keyword):
    return value[0]

def process_map(value, target_keyword):
    print('vvvv', value, target_keyword)
    map = target_keyword.get('map', '')
    for v in value:
        for m_k, m_v in map.items():
            if m_k in v:
                return m_v
    return ''

def process_name(value, target_keyword):
    #############Try to Find NNP by MeCab first#########################
    # mecab= MeCab()
    # tagged_value= mecab.pos(value)
    # for text, tag in tagged_value:
    #     if tag == 'NNP':
    #         return text
    ######### this is using REGEX ######################
    print('process_name')
    synonyms = target_keyword['synonym']['priority']
    value_ls=value[0].split(' ')
    new_val = ''
    for ele in value_ls:
        if not any(syn in ele for syn in synonyms) and '매니저' not in ele:
            new_val += ele
    return new_val if new_val else 'value'


def process_company(value, target_keyword):
    synonyms = target_keyword['synonym']['priority']
    value_ls=value[0].split(')')
    new_val = ''
    for ele in value_ls:
        if not any(syn in ele for syn in synonyms) and '매니저' not in ele:
            new_val += ele
    return new_val if new_val else 'value'
    pass

def process_department(value, target_keyword):
    match = re.search(r'투자금융(\d+)부', value[0])
    if match:
        return match.group(0)
    return value

def process_date(value, target_keyword):
    # 각 부분에서 정규 표현식을 사용해 날짜 추출
    year_match = re.search(r'(\d{4})년', value[0])
    month_match = re.search(r'(\d{1,2})월', value[0])
    day_match = re.search(r'(\d{1,2})일', value[0])

    # 검색된 결과가 있으면 해당 그룹의 값을 추출
    year = year_match.group(1) if year_match else '0000'
    month = month_match.group(1) if month_match else '00'
    day = day_match.group(1) if day_match else '00'

    # 추출된 값을 원하는 형식으로 포맷팅
    date = f'{year}-{month.zfill(2)}-{day.zfill(2)}'
    return date

def process_year(value, target_keyword):
    value = remove_special_characters(value[0])
    tagged_value= tag_text(value)
    for word, tag in tagged_value:
        if (tag == 'Number') and ('년' in word): # '억'이 있는 숫자 부분만 추출   
            number = extract_first_float(word)
            # multiply first float
            return number * 12
    numbers = re.findall(r'\d+', value) 
    if numbers:
        return int(numbers[0])* 12
    return value


def process_number(value, target_keyword):
    print('vvvv', value, target_keyword)
    sp_word = target_keyword.get('sp_word', '')

    if sp_word:
        target_value = next((v for v in value if sp_word in v), value[0])
    else:
        target_value = value[0]
    value = remove_special_characters(target_value)
    tagged_value= tag_text(value)
    for word, tag in tagged_value:
        if (tag == 'Number') and ('년' in word): # '억'이 있는 숫자 부분만 추출   
            number = extract_first_float(word)
            # multiply first float
            return number * 12
    print('process_number_values', value)
    numbers = re.findall(r'\d+', value) 
    if numbers:
        return numbers[0]
    return ''

def process_money(value, target_keyword):
    #print(value, target_keyword, 'this is money')
    value = remove_special_characters(value[0])
    tagged_value = tag_text(value)
    tagged_value=combine_money_number_tags(tagged_value)
    trillions_in_kor = '조'
    billions_in_kor = '억'
    
    for word, tag in tagged_value:
        if tag == 'Number':
            if '조' in word:
                # '조'가 포함된 경우, '조' 단위로 숫자를 분리하여 계산
                parts = word.split(trillions_in_kor)
                trillions = int(''.join(filter(str.isdigit, parts[0])))  # '조' 앞의 숫자 추출
                
                if len(parts) > 1 and billions_in_kor in parts[1]:
                    # '조' 다음에 '억'이 오는 경우
                    billions = int(''.join(filter(str.isdigit, parts[1].split(billions_in_kor)[0])))
                else:
                    billions = 0
                
                return (trillions * 1000000000000) + (billions * 100000000)
            
            elif billions_in_kor in word:
                # '~'가 포함된 경우, 첫 번째 숫자만 사용
                if '~' in word:
                    word = word.split('~')[0]
                
                number = int(''.join(filter(str.isdigit, word)))
                return number * 100000000
    numbers = re.findall(r'\d+', value)
    if numbers:
        number = numbers[0]
        print(target_keyword['key'],':', number)
        if len(number)<4:# must multiply 10mil
            return int(number) * 100000000

        return int(number)
    return ''  # 숫자 태그가 없으면 ''

def process_percentage(value, target_keyword):
    sp_words = target_keyword['sp_word']
    value_ls = remove_special_characters_from_list(value)
    if len(value_ls) >1:
        value = find_spword_and_string(value_ls, sp_words, '%')
    else:
        value = value_ls[0]


    tagged_value= tag_text(value)
    if sp_words == None:
        for word, tag in tagged_value:
            if tag == 'Number' and '%' in word: # '%'이 있는 숫자 중 첫번째
                return word
    else: # sp_word 의 값이 있을때
        start_search = False
        for word, tag in tagged_value:
            if start_search and tag == 'Number' and '%' in word:
                return word
            if any(spword in word for spword in sp_words):
                start_search =True
        # for 문을 돌렸는데도 못 찾았으면 sp_word=None처럼 다시 작업한다
        for word, tag in tagged_value:
            if tag =='Number' and '%' in word:
                return word
    
    return value

##########################################################
# 데이터 처리 함수 매핑
process_functions = {
    "string": process_string,
    "name": process_name,
    "department": process_department,
    "year": process_year,
    "number": process_number, 
    "date": process_date,
    "money": process_money,
    "percentage": process_percentage,
    "map": process_map,
    "company": process_company
}


def post_process(data, keyword):
    # check type and process value based on type
    new_data = []
    print('this data', data)
    for [key, value, pos_data] in data:
        target_keyword = find_by_key(keyword, key)
        data_type = target_keyword.get('type')
        process_func = process_functions.get(data_type)
        if process_func:
            split_keywords = target_keyword['split']
            if split_keywords:
                value_list = split_value(value, split_keywords)
                new_value = process_func(value_list, target_keyword)
                pass
            else:
                new_value = process_func([value], target_keyword)
                # 추후에 value를 [value]로 바꿔둔것을 모든 process 함수에 수정해야해
            new_data.append([key, new_value, value, pos_data])
        else:
            raise ValueError(f"No processing function available for data type '{data_type}'")
    return new_data

        


