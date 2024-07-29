# django-keyvalue
# Keyword Dictionary info

type: string, name, department, year, amout, percentage가 있다.
* if "string" : don't edit result
*  if "name" : result should find korean name
*  if "department" : result should find department
*  if "year" : result should multiply by 12 (year->month)
*  i "number" : result should be number
*  if "amount" : result should find '억' and if so multiply by 100000000
*  if "percentage" : find percentage
* if "company" : find company
* if "map" : {"후취": "후불", "선취": "선불", "후불": "후불", "선불": "선불"}

is_table:  True면 table에서 밸류를 찾고 False면 일반 텍스트 쪽에서 벨류를 찾는다.

specific: specific=True면 오른쪽 항을 잘라서 tokenize한 다음에 그 중 'sp_word'의 값이 있는 항을 찾는다.

sp_word: spcific =False 지만 sp_word의 값이 있으면 post_process를 할때 tagging 이 이뤄진 이후에 sp_word와 관련이 있는 값을 추출한다.

value: 해당 값이 있으면 그것이 찾고자 하는 밸류임