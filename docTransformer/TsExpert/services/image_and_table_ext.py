import base64
from io import BytesIO
from docx.oxml.ns import qn
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
def extract_image_from_cell(cell, img_name="image.png"):
    """
    Extract an image from a DOCX cell, if present, and return it as an InMemoryUploadedFile.

    Args:
        cell (Cell): A DOCX table cell.
        img_name (str): The name to assign to the extracted image file (default is 'image.png').

    Returns:
        InMemoryUploadedFile or None: An uploaded file object suitable for saving in an ImageField, or None if no image is found.
    """
    drawing_elements = cell._element.xpath('.//w:drawing')

    if drawing_elements:
        for drawing in drawing_elements:
            blip = drawing.xpath('.//a:blip')
            if blip:
                rId = blip[0].get(qn('r:embed'))
                image_part = cell.part.related_parts[rId]

                # Open the image using PIL
                image_stream = BytesIO(image_part.blob)
                try:
                    img = Image.open(image_stream)

                    # Convert the image to an InMemoryUploadedFile
                    img_io = BytesIO()
                    img.save(img_io, format='PNG')  # Save the image as PNG or any other format
                    img_io.seek(0)

                    # Create an InMemoryUploadedFile object to be stored in the ImageField
                    img_file = InMemoryUploadedFile(
                        img_io,  # The file-like object containing the image data
                        None,  # Field name (can be None)
                        img_name,  # The name of the file
                        'image/png',  # The content type
                        img_io.getbuffer().nbytes,  # File size
                        None  # Optional charset
                    )

                    return img_file

                except Exception as e:
                    print(f"Error opening image: {e}")
                    return None

    return None
# def extract_image_from_cell(cell):
#     """
#     Extract an image from a DOCX cell, if present, and return it as a PIL Image object.

#     Args:
#         cell (Cell): A DOCX table cell.

#     Returns:
#         Image or None: A PIL Image object if an image is found, or None if no image is present.
#     """
#     # Check for drawing elements (which contain images)
#     drawing_elements = cell._element.xpath('.//w:drawing')

#     if drawing_elements:
#         # Locate the image data within the drawing element
#         for drawing in drawing_elements:
#             # Find the image relationship id
#             blip = drawing.xpath('.//a:blip')
#             if blip:
#                 # The image reference (rId)
#                 rId = blip[0].get(qn('r:embed'))
#                 # Retrieve the image part from the document using the rId
#                 image_part = cell.part.related_parts[rId]

#                 # Open the image using PIL
#                 image_stream = BytesIO(image_part.blob)
#                 try:
#                     img = Image.open(image_stream)
#                     return img
#                 except Exception as e:
#                     print(f"Error opening image: {e}")
#                     return None

#     return None


def extract_images_from_tables(doc, image_data):
    """Extract images from tables based on image_data.

    Args:
        doc (Document): The DOCX document object.
        image_data (list): A list of tuples containing image key, table index, row index, and column index.

    Returns:
        list: A list of tuples containing image key and the extracted image.
    """
    image_info = []
    for img_key, _, (table_idx, row_idx, col_idx) in image_data:
        table = doc.tables[table_idx]
        try:
            cell = table.rows[row_idx].cells[col_idx]
            # Check if there is an image in the cell
            if cell._element.xpath('.//w:drawing'):
                img = extract_image_from_cell(cell)
                image_info.append((img_key, img))
        except IndexError:
            print(f"Table index {table_idx}, row {row_idx}, or col {col_idx} is out of bounds")

    return image_info









import zipfile
from lxml import etree
def extract_table_under_target(docx_path, target_text):
    # 타겟 텍스트 아래에 있는 첫번째 테이블을 xml 스트링으로 리턴
    # DOCX 파일을 ZIP 형식으로 열기
    with zipfile.ZipFile(docx_path, 'r') as docx_zip:
        # 'word/document.xml'에서 XML 데이터를 읽기
        with docx_zip.open('word/document.xml') as doc_xml:
            xml_content = doc_xml.read()

    # XML 파싱
    xml_tree = etree.fromstring(xml_content)

    # 네임스페이스 설정
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    # '사업개요' 텍스트를 포함한 단락 찾기 (w:p 태그 안에 w:t로 텍스트 존재)
    paragraphs = xml_tree.findall('.//w:p', namespaces)
    found_target = False
    target_paragraph = None

    for paragraph in paragraphs:
        # 모든 w:t 텍스트 노드의 값을 결합해 단락의 텍스트 생성
        text = ''.join(paragraph.xpath('.//w:t/text()', namespaces=namespaces))

        # 타깃 텍스트를 찾으면 플래그를 True로 설정
        if target_text in text:
            print('target_text:', target_text)
            print('text:')
            found_target = True
            target_paragraph = paragraph
            print('found_TARGET!!!=>',text)
            continue  # 타깃 텍스트 다음 단락부터 테이블을 찾음

        # 타깃 텍스트 이후 테이블을 찾기 시작
        if found_target:
            # 먼저 현재 단락에서 테이블을 찾음
            current_table = paragraph.xpath('.//w:tbl', namespaces=namespaces)
            if current_table:
                # 현재 단락에서 테이블을 찾으면 그 테이블 반환
                return (
                    etree.tostring(current_table[0], pretty_print=True).decode('utf-8')
                )

            # 현재 단락에 테이블이 없으면 형제 노드에서 테이블을 찾음
            sibling_table = paragraph.xpath('.//following-sibling::w:tbl', namespaces=namespaces)
            if sibling_table:
                # 형제 노드에서 테이블을 찾으면 그 테이블 반환
                return (
                    etree.tostring(sibling_table[0], pretty_print=True).decode('utf-8')
                )

    return None
    raise Exception("타깃 텍스트 이후 테이블을 찾을 수 없습니다.")


def extract_table_from_raw_paragraphs(docx_path, key_value):
    """iterate each key_value item which "value_type": "xml" and get_all_targettext and 
    if target_text found, do "extract_table_under_target"

    Args:
        docx_path (str): path of original document
        key_value (_type_): _description_

    Returns:
        [[k, table_xml]]: 리스트 오브 리스트 
    """
    
    table_xml_res = []
    # 1) get target key_value
    xml_kv = [k_v for k_v in key_value if 'value_type' in k_v.keys() and k_v['value_type']== 'xml']

    # 2) iterate
    for kv in xml_kv:
        xml = ''
        all_syns = kv['synonym']['all']
        for syn in all_syns:
            xml = extract_table_under_target(docx_path, syn)
            # if xml is not None:
            #     break
        table_xml_res.append([kv['key'], xml])
    return table_xml_res