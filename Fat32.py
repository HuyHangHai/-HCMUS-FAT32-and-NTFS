BOOTSECTORSIZE = 512

class FAT:
    def __init__(self, data):
        self.temp = data

    def get_cluster_chain(self, index: int) -> 'list[int]':
        self.elements = []
        for i in range (0, len(self.temp), 4):
            self.elements.append(int.from_bytes(self.temp[i:i+4], byteorder='little'))
        cluster_chain = []
        while True:
            cluster_chain.append(index)
            index = self.elements[index]
            if index == 0x0FFFFFFF or index == 0x0FFFFFF7:
                return cluster_chain

class RDET:
    def __init__(self, ):
        self.data
class Fat32_Main:
    def __init__(self, volume_name) -> None:
        self.volume_name = volume_name
        try:
            self.bin_raw_data = open(rf"\\.\{self.volume_name}", 'rb')
            self.boot_sector = {}

            self.boot_sector_data = self.bin_raw_data.read(BOOTSECTORSIZE)
            self.extract_boot_sector()
            if self.boot_sector['FAT Name'] != b'FAT32   ':
                raise Exception('NOT FAT32')

            # Important Info
            #Reserved sectors
            self.boot_sector['FAT Name'] = self.boot_sector['FAT Name'].decode()
            self.bytes_per_sector = self.boot_sector['Bytes Per Sector']
            self.sectors_per_cluster = self.boot_sector['Sectors Per Cluster']
            self.sectors_in_boot_sectors = self.boot_sector['Reserved Sectors']
            self.numbers_of_fats = self.boot_sector["Number of FATs"]
            self.sectors_in_volumes = self.boot_sector['Sectors In Volume']
            self.sectors_per_fats = self.boot_sector['Sectors Per FAT']
            self.starting_cluster_of_rdet = self.boot_sector['Starting Cluster of RDET']
            self.starting_sector_of_data = self.boot_sector['Starting Sector of Data']
            #FAT
            FAT_size = self.bytes_per_sector * self.sectors_per_fats

            self.FAT: list[FAT] = []
            for _ in range(self.numbers_of_fats):
                self.FAT.append(FAT(self.fd.read(FAT_size)))

            #data+rdet
            start_cluster = self.boot_sector["Starting Cluster of RDET"]
            self.RDET = self.DET[start_cluster]
        except Exception as error:
            print(f"Error: {error}")
    def get_all_cluster_data(self, index: int) -> bytes:
        # Lay fat[0] vi fat[1] la ban copy du tru cua fat[0]
        cluster_chain = self.FAT[0].get_cluster_chain(index)
        #khai bao data rong voi kieu du lieu bytes
        data_in_bytes :bytes = ""
        for i in cluster_chain:
            offset = self.sectors_in_boot_sectors + self.sectors_per_fats * self.numbers_of_fats + (index - 2) * self.sectors_per_fats
            # lay het data cua tat ca sector tai cluster i
            self.fd.seek(offset * self.bytes_per_sector)
            data_in_bytes += self.fd.read(self.bytes_per_sector * self.sectors_per_cluster)
        return data_in_bytes


    @staticmethod
    def check(volume_name):
        try:
            boot_sector = open(rf'\\.\{volume_name}', 'rb')
            boot_sector.read(1)  # Ensure file pointer correctly point to boot sector
            boot_sector.seek(0x52)
            fat_type = boot_sector.read(8)
            if fat_type == b'FAT32   ':
                return True
            return False
        except Exception as error:
            print(f'Error: {error}')
            exit()

    def __str__(self) -> str:
        s = "Volume's name: " + self.volume_name
        s += "\nVolume's info:\n"
        items = self.boot_sector.items()
        for i in items:
            s += str(i[0]) + ': ' + str(i[1]) + '\n'
        return s

    def extract_boot_sector(self):
        self.boot_sector['Bytes Per Sector'] = int.from_bytes(self.boot_sector_data[0xB:0xD], 'little')
        self.boot_sector['Sectors Per Cluster'] = int.from_bytes(self.boot_sector_data[0xD:0xE], 'little')
        self.boot_sector['Reserved Sectors'] = int.from_bytes(self.boot_sector_data[0xE:0x10], 'little')
        self.boot_sector['Number of FATs'] = int.from_bytes(self.boot_sector_data[0x10:0x11], 'little')
        # self.boot_sector['Media Descriptor'] = self.boot_sector_data[0x15:0x16]
        # self.boot_sector['Sectors Per Track'] = int.from_bytes(self.boot_sector_data[0x18:0x1A], 'little')
        # self.boot_sector['No. Heads'] = int.from_bytes(self.boot_sector_data[0x1A:0x1C], 'little')
        self.boot_sector['Sectors In Volume'] = int.from_bytes(self.boot_sector_data[0x20:0x24], 'little')
        self.boot_sector['Sectors Per FAT'] = int.from_bytes(self.boot_sector_data[0x24:0x28], 'little')
        # self.boot_sector['Flags'] = int.from_bytes(self.boot_sector_data[0x28:0x2A], 'little')
        # self.boot_sector['FAT32 Version'] = self.boot_sector_data[0x2A:0x2C]
        self.boot_sector['Starting Cluster of RDET'] = int.from_bytes(self.boot_sector_data[0x2C:0x30], 'little')
        # self.boot_sector['Sector Storing Sub-Info'] = self.boot_sector_data[0x30:0x32]
        # self.boot_sector['Sector Storing Backup Boot Sector'] = self.boot_sector_data[0x32:0x34]
        self.boot_sector['FAT Name'] = self.boot_sector_data[0x52:0x5A]
        self.boot_sector['Starting Sector of Data'] = self.boot_sector['Reserved Sectors'] + self.boot_sector[
            'Number of FATs'] * self.boot_sector['Sectors Per FAT']
    def __del__(self):
        if getattr(self, "fd", None):
            print("Closing Volume...")
            self.fd.close()





