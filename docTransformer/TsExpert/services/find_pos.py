class PosFinder:
    def __init__(self, doc):
        self.doc = doc  # Document 오브젝트
        self.target_text = ""
        self.table_number = 0
        self.row_number = 0

    def set_target_info(self, data_ele):
        self.target_text = data_ele[1]
        self.table_number = data_ele[2][0]
        self.row_number = data_ele[2][1]

    def find_occurrence_position(self):
        para_idx = 0
        table_count = 0
        overall_occurrence_count = 0
        target_occurrence_count = 0
        found = False

        for block in self.doc.element.body:
            if block.tag.endswith('p'):
                para = self.doc.paragraphs[para_idx]
                text = para.text
                overall_occurrence_count += text.count(self.target_text)
                para_idx += 1
            elif block.tag.endswith('tbl'):
                table = self.doc.tables[table_count]
                if table_count == self.table_number:
                    for row_idx, row in enumerate(table.rows):
                        for cell in row.cells:
                            text = cell.text
                            overall_occurrence_count += text.count(self.target_text)
                            if row_idx == self.row_number:
                                target_occurrence_count = overall_occurrence_count
                                found = True
                                break
                        if found:
                            break
                else:
                    for row in table.rows:
                        for cell in row.cells:
                            text = cell.text
                            overall_occurrence_count += text.count(self.target_text)
                if found:
                    break
                table_count += 1

        return target_occurrence_count
