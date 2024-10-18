# How to convert a korean Text into English key is Different by what the client wants and by DB logic

#From {{차주사}} we need to map "borrower_company"
from TsExpert.models import IMExtraction

class KeyMap:
    def __init__(self):
        self.type =1 # 1번은 NH 스타일의 static한 테이블에서 키밸류를 가져오는 것
        self.keymap = {}
        self._run()


    def _get_keymap_from_static_db_IMExtraction(self):
        fields = IMExtraction._meta.get_fields()

        # Create a dictionary with verbose_name as the key and column name as the value
        for field in fields:
            if hasattr(field, 'verbose_name') and hasattr(field, 'name'):
                self.keymap[field.verbose_name] = field.name

    def _run(self):
        if self.type == 1:
            self._get_keymap_from_static_db_IMExtraction()

    

    


        