BOOT_SECTOR_SIZE = 512

class FAT:
    def __init__(self, data):
        self.raw_data = data
        self.elements = []

    def get_cluster_chain(self, starting_index: int) -> 'list[int]':
        for i in range (0, len(self.raw_data), 4):
            self.elements.append(int.from_bytes(self.raw_data[i:i+4], 'little'))

        cluster_list = []
        while True:
            cluster_list.append(starting_index)
            starting_index = self.elements[starting_index]
            if starting_index == 0x0FFFFFFF or starting_index == 0x0FFFFFF7:
                return cluster_list

class RDET:
    def __init__(self, data: bytes) -> None:
        self.raw_data = data
    
    # Handle entries here!


class RDET:
    def __init__(self, data):
        self.data = data
class Fat32_Main:
    def __init__(self, volume_name) -> None:
        self.volume_name = volume_name
        try:
            self.bin_raw_data = open(rf"\\.\{self.volume_name}", 'rb')
            self.boot_sector = {}

            self.boot_sector_data = self.bin_raw_data.read(BOOT_SECTOR_SIZE)
            self.extract_boot_sector()
            if self.boot_sector['FAT Name'] != b'FAT32   ':
                raise Exception('NOT FAT32')

            # Important Info
            self.boot_sector['FAT Name'] = self.boot_sector['FAT Name'].decode()
            self.bytes_per_sector = self.boot_sector['Bytes Per Sector']
            self.sectors_per_cluster = self.boot_sector['Sectors Per Cluster']
            self.sectors_in_boot_sectors = self.boot_sector['Reserved Sectors']
            self.numbers_of_fats = self.boot_sector["Number of FATs"]
            self.sectors_in_volumes = self.boot_sector['Sectors In Volume']
            self.sectors_per_fats = self.boot_sector['Sectors Per FAT']
            self.starting_cluster_of_rdet = self.boot_sector['Starting Cluster of RDET']
            self.starting_sector_of_data = self.boot_sector['Starting Sector of Data']
            
            # Read FAT's info
            # Move cursor in file to the 1st FAT
            self.bin_raw_data.read(self.bytes_per_sector * (self.sectors_in_boot_sectors - 1))
            FAT_size = self.bytes_per_sector * self.sectors_per_fats

            self.list_FAT: list[FAT] = []
            for _ in range(self.numbers_of_fats):
                self.list_FAT.append(FAT(self.bin_raw_data.read(FAT_size)))
                
            # Handle RDET 
            starting_cluster_index = self.boot_sector["Starting Cluster of RDET"]
            self.RDET = RDET(self.get_all_cluster_data(starting_cluster_index))

        except Exception as error:
            print(f"Error: {error}")

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
        result = "Volume's name: " + self.volume_name
        result += "\nVolume's info:\n"
        items = self.boot_sector.items()
        for i in items:
            result += str(i[0]) + ': ' + str(i[1]) + '\n'
        return result

    def extract_boot_sector(self):
        self.boot_sector['Bytes Per Sector'] = int.from_bytes(self.boot_sector_data[0xB:0xD], 'little')
        self.boot_sector['Sectors Per Cluster'] = int.from_bytes(self.boot_sector_data[0xD:0xE], 'little')
        self.boot_sector['Reserved Sectors'] = int.from_bytes(self.boot_sector_data[0xE:0x10], 'little')
        self.boot_sector['Number of FATs'] = int.from_bytes(self.boot_sector_data[0x10:0x11], 'little')
        self.boot_sector['Sectors In Volume'] = int.from_bytes(self.boot_sector_data[0x20:0x24], 'little')
        self.boot_sector['Sectors Per FAT'] = int.from_bytes(self.boot_sector_data[0x24:0x28], 'little')
        self.boot_sector['Starting Cluster of RDET'] = int.from_bytes(self.boot_sector_data[0x2C:0x30], 'little')
        self.boot_sector['FAT Name'] = self.boot_sector_data[0x52:0x5A]
        self.boot_sector['Starting Sector of Data'] = self.boot_sector['Reserved Sectors'] + self.boot_sector[
            'Number of FATs'] * self.boot_sector['Sectors Per FAT']

    def convert_cluster_to_sector_index(self, index):
        return self.sectors_in_boot_sectors + self.sectors_per_fats * self.numbers_of_fats + (index - 2) * self.sectors_per_cluster

    def get_all_cluster_data(self, cluster_index):
        cluster_list = self.list_FAT[0].get_cluster_chain(cluster_index)
        data = b""
        for i in cluster_list:
            sector_index = self.convert_cluster_to_sector_index(i)
            self.bin_raw_data.seek(sector_index * self.bytes_per_sector)
            data += self.bin_raw_data.read(self.bytes_per_sector * self.sectors_per_cluster)
        return data





