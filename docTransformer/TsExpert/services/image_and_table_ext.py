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