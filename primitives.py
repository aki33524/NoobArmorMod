from struct import pack, unpack

class LoadDataMesh:
    def __init__(self, filepath=''):
        self.PackedGroups = []
        self.pfile = open(filepath, 'rb')

        header = unpack('<I', self.pfile.read(4))[0]
        assert(header == 0x42a14e65)

        self.load_packed_section()

    def load_packed_section(self):
        self.pfile.seek(-4, 2)
        table_start = unpack('<l', self.pfile.read(4))[0]
        self.pfile.seek(-4-table_start, 2)
        position = 4
        
        self.table = self.pfile.read()[:-4]
        self.pfile.seek(-4-table_start, 2)

        while True:
            data = self.pfile.read(4)
            if data == None or len(data) != 4:
                break

            section_size = unpack('<I', data)[0]
            data = self.pfile.read(16)
            data = self.pfile.read(4)
            if data == None or len(data) != 4:
                break

            section_name_length = unpack('<I', data)[0]
            section_name = self.pfile.read(section_name_length).decode('utf-8')
            self.PackedGroups.append({
                'section_name':section_name,
                'position' : position,
                'length' : section_size
            })

            position += section_size

            if section_size%4 > 0:
                position += 4-section_size%4

            if section_name_length%4 > 0:
                self.pfile.read(4-section_name_length%4)

def merge_primitives(lod_path, col_path):
    ldm1 = LoadDataMesh(lod_path)
    ldm2 = LoadDataMesh(col_path)

    output = pack('<I', 0x42a14e65)
    
    table = ldm1.table + ldm2.table

    for v in ldm1.PackedGroups:
        ldm1.pfile.seek(v['position'])
        output += ldm1.pfile.read(v['length'])

        if v['length']%4:
            output += b'\x00' * (4-v['length']%4)

    for v in ldm2.PackedGroups:
        ldm2.pfile.seek(v['position'])
        output += ldm2.pfile.read(v['length'])

    output += table
    output += pack('<I', len(table))
    return output
