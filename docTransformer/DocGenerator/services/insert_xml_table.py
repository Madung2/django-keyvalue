import shutil
import zipfile
from lxml import etree

# 개별 placeholder에 table_xml을 삽입하는 함수
def insert_table_into_placeholder(xml_tree, table_xml, placeholder):
    body = xml_tree.find('.//w:body', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})

    # 문서에서 모든 텍스트 요소를 순회하면서 placeholder를 찾기
    for paragraph in body.iterfind('.//w:p', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}):
        texts = paragraph.findall('.//w:t', namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
        for text_elem in texts:
            if placeholder in text_elem.text:
                # placeholder가 있는 경우 테이블 삽입
                parent = paragraph.getparent()
                table_elem = etree.fromstring(table_xml)

                # placeholder가 있는 문단을 테이블로 교체
                parent.replace(paragraph, table_elem)
                return xml_tree  # 수정된 트리 반환

    return xml_tree  # 수정이 없을 경우 그대로 반환


# def insert_table_into_body(body, table_xml):
#     # 테이블 XML을 etree 객체로 변환
#     new_table = etree.fromstring(table_xml)

#     # 테이블을 body에 추가
#     body.append(new_table)

#         # 빈 단락을 추가하여 줄 바꿈
#     new_paragraph = etree.Element('w:p')  # 빈 단락을 나타내는 XML 요소
#     body.append(new_paragraph)

#     # 수정된 트리 반환 (body는 이미 수정됨)
#     return body

##########################################잘 작동하는 코드##########################################3
def insert_table_into_body(body, table_xml):
    # 네임스페이스 선언
    namespace = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    }

    # 테이블 XML을 etree 객체로 변환
    new_table = etree.fromstring(table_xml)

    # 테이블을 body에 추가
    body.append(new_table)

    # 빈 단락을 추가하여 줄 바꿈 (네임스페이스 포함)
    new_paragraph = etree.Element(f"{{{namespace['w']}}}p")  # 빈 단락을 나타내는 XML 요소
    body.append(new_paragraph)

    # 수정된 트리 반환 (body는 이미 수정됨)
    return body

# 여러 placeholder와 table_xml을 순차적으로 처리하는 함수
def insert_multiple_tables_into_placeholders(docx_path, placeholder_table_dict, output_path):
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

        # 첫 번째 placeholder와 테이블만 처리
        for placeholder, table_xml in placeholder_table_dict.items():
            body = insert_table_into_body(body, table_xml)
            print('첫 번째 테이블이 추가되었습니다.')
            # break  # 첫 번째 테이블만 처리하고 루프 종료

        # 수정된 XML을 다시 저장
        with docx_zip.open('word/document.xml', 'w') as doc_xml:
            doc_xml.write(etree.tostring(xml_tree, pretty_print=True, xml_declaration=True, encoding='utf-8'))

    # 최종 파일로 저장
    shutil.move('temp.docx', output_path)

    ##########################################잘 작동하는 코드#######################################