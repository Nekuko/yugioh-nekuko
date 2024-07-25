class YDKReader:

    @staticmethod
    def convert(file_path):
        with open(file_path, 'r+') as f:
            content = f.read().split('\n')
            content = content[content.index('#main'):]

        main_index = content.index('#main')
        extra_index = content.index('#extra')
        side_index = content.index('!side')

        main = content[main_index+1:extra_index]
        extra = content[extra_index+1:side_index]
        side = content[side_index+1:]

        return main, extra, side
