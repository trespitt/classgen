from os import listdir, linesep
from yaml import load, dump
from datetime import datetime

try:
    from yaml import CLoader as Loader, CDumper as Dumper, FullLoader
except ImportError:
    from yaml import Loader, Dumper, FullLoader


class ClassGenerator:
    def __init__(self, config_dir='inputs', config_file='config.yml', output_dir='outputs'):
        if config_dir not in listdir('.'):
            raise ValueError("missing config dir: " + config_dir)
        if config_file not in listdir(config_dir):
            raise ValueError("missing config file: " + config_file)
        if output_dir not in listdir('.'):
            raise ValueError("missing output_dir : " + output_dir)

        self.config_dir = config_dir
        self.config_file = config_file
        self.output_dir = output_dir

    def proc_config(self):
        sep = '/'
        fp = f"{self.config_dir}{sep}{self.config_file}"
        with open(fp, 'r') as f:
            data = load(f, Loader=FullLoader)
            output = dump(data, Dumper=Dumper)
            self.__data = data

    def __capitalize_first(self, s):
        return s[0].upper() + s[1 : len(s)]

    def __template_decl(self):
        return """        @JsonCreator
        public {class} ("""

    def __template_constructor(self):
        return """                  @JsonProperty("{varName}") {varType} {varName}"""

    def __template_getter(self):
        return """
    public {varType} get{VarName}() {
        return {varName};
    }"""

    def __template_setter(self):
        return """
    public void set{VarName}({varType} {varName}) {
        this.{varName} = {varName};
    }"""

    def __tstamp(self):
        return str(datetime.now()).replace('-', '').replace(':', '').replace(' ', '')[:14]

    def __safe_import(self, s):
        s_pkg = 'import '
        if len(s) < len(s_pkg) or s[:len(s_pkg)] != s_pkg:
            return s_pkg + s
        return s

    def __safe_pkg(self, s):
        s_pkg = 'package '
        if len(s) < len(s_pkg) or s[:len(s_pkg)] != s_pkg:
            return s_pkg + s
        return s

    def __safe_semicolon(self, s):
        if s[-1] == ';':
            return s
        return s + ';'

    def gen_file(self):
        with open(f"{self.output_dir}/{self.__data['class']}{self.__tstamp()}.java", 'a') as fo:
            fo.write(self.__safe_pkg(self.__safe_semicolon(self.__data['package'])) + linesep + linesep)
            for impt in self.__data['imports']:
                fo.write(self.__safe_semicolon(self.__safe_import(impt)) + linesep)
            fo.write(linesep)

            if self.__data['ignoreUnknown']:
                fo.write("@JsonIgnoreProperties(ignoreUnknown = true)" + linesep)
            fo.write("public class " + self.__data['class'] + " {" + linesep + linesep)

            private_str = "private " if self.__data['setters'] else "private final "
            for field in self.__data['fields']:
                fo.write(f"        {private_str}{field['type']} {field['name']};" + linesep)
            fo.write(linesep)

            fo.write(self.__template_decl().replace("{class}", self.__data['class']))
            fo.write(linesep)

            i = 0
            for field in self.__data['fields']:
                strr = self.__template_constructor().replace("{varName}", field['name']).replace("{varType}", field['type'])
                if len(self.__data['fields']) > 1 and i < len(self.__data['fields']) - 1:
                    strr += ','
                else:
                    strr += ') {'
                i += 1
                fo.write(strr + linesep)
            fo.write(linesep)
            
            for field in self.__data['fields']:
                fo.write(f"                this.{field['name']} = {field['name']};" + linesep)
            fo.write('        }' + linesep)
            

            for field in self.__data['fields']:
                strrG = self.__template_getter().replace("{varName}", field['name']).replace("{varType}", field['type']).\
                            replace("{VarName}", self.__capitalize_first(field['name']))
                fo.write(strrG + linesep)
                fo.write(linesep)

                if self.__data['setters']:
                    strrS = self.__template_setter().replace("{varName}", field['name']).replace("{varType}", field['type']).\
                                replace("{VarName}", self.__capitalize_first(field['name']))
                    fo.write(strrS + linesep)
                    fo.write(linesep)

            fo.write('}')

if __name__ == '__main__':
    cg = ClassGenerator()
    cg.proc_config()
    cg.gen_file()
