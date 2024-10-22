import shutil
import zipfile
from lxml import etree


def insert_table_after_paragraph(body, table_xml, paragraph):
    # 네임스페이스 선언
    namespace = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }

    # 테이블 XML을 etree 객체로 변환
    new_table = etree.fromstring(table_xml)

    # 테이블을 특정 단락 뒤에 추가
    index = body.index(paragraph)  # 삽입할 단락 위치
    body.insert(index + 1, new_table)  # 테이블 삽입

    # 빈 단락을 추가하여 줄 바꿈 (네임스페이스 포함)
    # 빈 단락을 만들 때는 기본 구조를 갖춘 단락을 추가
    new_paragraph = etree.Element(f"{{{namespace['w']}}}p")  # 빈 단락을 나타내는 XML 요소
    new_paragraph_properties = etree.SubElement(new_paragraph, f"{{{namespace['w']}}}pPr")
    new_paragraph_run = etree.SubElement(new_paragraph, f"{{{namespace['w']}}}r")
    new_paragraph_run_properties = etree.SubElement(new_paragraph_run, f"{{{namespace['w']}}}rPr")
    new_paragraph_text = etree.SubElement(new_paragraph_run, f"{{{namespace['w']}}}t")
    new_paragraph_text.text = ""  # 텍스트 없는 빈 단락

    # 빈 단락을 테이블 뒤에 추가
    body.insert(index + 2, new_paragraph)

    # 수정된 body 반환
    return body

#############working
# def insert_table_after_paragraph(body, table_xml, paragraph):
#     # 네임스페이스 선언
#     namespace = {
#         'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
#     }

#     # 테이블 XML을 etree 객체로 변환
#     new_table = etree.fromstring(table_xml)

#     # 테이블을 특정 단락 뒤에 추가
#     index = body.index(paragraph)  # 삽입할 단락 위치
#     body.insert(index + 1, new_table)  # 테이블 삽입

#     # 빈 단락을 추가하여 줄 바꿈 (네임스페이스 포함)
#     new_paragraph = etree.Element(f"{{{namespace['w']}}}p")  # 빈 단락을 나타내는 XML 요소
#     body.insert(index + 2, new_paragraph)  # 빈 단락 추가

def insert_multiple_tables_into_placeholders(docx_path, placeholder_table_dict, output_path):
    """_summary_

    Args:
        docx_path (_type_): _description_
        placeholder_table_dict (dict): {조달금액: xml}
        output_path (_type_): _description_
    """
    korean_placeholder_dict = make_dict_korean(placeholder_table_dict)
    # temp.docx 파일을 원본 문서에서 복사하여 생성
    shutil.copy(docx_path, 'temp.docx')  # 원본 문서를 temp로 복사

    # temp.docx 파일을 ZIP 형식으로 열기
    with zipfile.ZipFile('temp.docx', 'a') as docx_zip:
        # 'word/document.xml' 파일을 수정
        with docx_zip.open('word/document.xml', 'r') as doc_xml:
            xml_content = doc_xml.read()

        # 기존 문서의 XML 파싱
        xml_tree = etree.fromstring(xml_content)
        body = xml_tree.find('.//w:body', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})

        # 모든 placeholder와 해당 테이블 처리
        for placeholder_text, table_xml in korean_placeholder_dict.items():
            placeholder = "{{" + placeholder_text + "}}"
            # 문서 내에서 placeholder가 있는 단락 찾기
            paragraphs = body.findall('.//w:p', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
            for para in paragraphs:
                texts = para.findall('.//w:t', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
                para_text = ''.join([t.text for t in texts])
                
                print('text::::', para_text, placeholder)
                if placeholder in para_text:
                    print('placeholder 위치를 찾았습니다.')
                    # 플레이스홀더 텍스트를 제거하고 테이블 삽입
                    # para.getparent().remove(para)
                    insert_table_after_paragraph(body, table_xml, para)
                    print(f'{placeholder} 위치에 테이블이 추가되었습니다.')
                    break
            break
        # 수정된 XML을 다시 저장
        with docx_zip.open('word/document.xml', 'w') as doc_xml:
            doc_xml.write(etree.tostring(xml_tree, pretty_print=True, xml_declaration=True, encoding='utf-8'))

    # 최종 파일로 저장
    shutil.move('temp.docx', output_path)


##########################################잘 작동하는 코드##########################################3
# def insert_table_into_body(body, table_xml):
#     # 네임스페이스 선언
#     namespace = {
#         'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
#     }

#     # 테이블 XML을 etree 객체로 변환
#     new_table = etree.fromstring(table_xml)

#     # 테이블을 body에 추가
#     body.append(new_table)

#     # 빈 단락을 추가하여 줄 바꿈 (네임스페이스 포함)
#     new_paragraph = etree.Element(f"{{{namespace['w']}}}p")  # 빈 단락을 나타내는 XML 요소
#     body.append(new_paragraph)

#     # 수정된 트리 반환 (body는 이미 수정됨)
#     return body

# # 여러 placeholder와 table_xml을 순차적으로 처리하는 함수
# def insert_multiple_tables_into_placeholders(docx_path, placeholder_table_dict, output_path):
#     # temp.docx 파일을 원본 문서에서 복사하여 생성
#     shutil.copy(docx_path, 'temp.docx')  # 원본 문서를 temp로 복사

#     # temp.docx 파일을 ZIP 형식으로 열기
#     with zipfile.ZipFile('temp.docx', 'a') as docx_zip:
#         # 'word/document.xml' 파일을 수정
#         with docx_zip.open('word/document.xml', 'r') as doc_xml:
#             xml_content = doc_xml.read()

#         # 기존 문서의 XML 파싱
#         xml_tree = etree.fromstring(xml_content)
#         body = xml_tree.find('.//w:body', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})

#         # 첫 번째 placeholder와 테이블만 처리
#         for placeholder, table_xml in placeholder_table_dict.items():
#             body = insert_table_into_body(body, table_xml)
#             print('첫 번째 테이블이 추가되었습니다.')
#             # break  # 첫 번째 테이블만 처리하고 루프 종료

#         # 수정된 XML을 다시 저장
#         with docx_zip.open('word/document.xml', 'w') as doc_xml:
#             doc_xml.write(etree.tostring(xml_tree, pretty_print=True, xml_declaration=True, encoding='utf-8'))

#     # 최종 파일로 저장
#     shutil.move('temp.docx', output_path)

    ###################################################################
from TsExpert.models import IMExtraction
def make_dict_korean(placeholder_table_dict):
    # Get the IMExtraction model

    
    # Create a mapping of field names to their verbose names
    field_verbose_mapping = {field.name: field.verbose_name for field in IMExtraction._meta.fields}

    # Create a new dictionary with translated keys
    new_dict = {}
    for k, v in placeholder_table_dict.items():
        # If the key is in the model's fields, replace it with the verbose_name
        if k in field_verbose_mapping:
            new_dict[field_verbose_mapping[k]] = v
        else:
            new_dict[k] = v  # If no match, keep the original key

    return new_dict
