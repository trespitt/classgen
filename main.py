from os import listdir, linesep
from yaml import load, dump
from datetime import datetime

try:
    from yaml import CLoader as Loader, CDumper as Dumper, FullLoader
except ImportError:
    from yaml import Loader, Dumper, FullLoader


class ClassGenerator:
    def __init__(self, config_dir='dev-inputs', config_file='config.yml'):
        self.config_dir = config_dir
        self.config_file = config_file

    def proc_config(self):
        if self.config_dir not in listdir('.'):
            raise ValueError("missing config dir: " + config_dir)
        if self.config_file not in listdir(self.config_dir):
            print(listdir(self.config_dir))
            raise ValueError("missing config file: " + config_file)
        sep = '/'
        fp = f"{self.config_dir}{sep}{self.config_file}"
        with open(fp, 'r') as f:
            data = load(f, Loader=FullLoader)
            output = dump(data, Dumper=Dumper)
            print(output)
            self.data = data

    def __capitalize_first(self, s):
        return s[0].upper() + s[1 : len(s)]

    def __template_decl(self):
        return """        @JsonCreator
        public class {class} {"""

    def __template_constructor(self):
        return """                  @JsonProperty("{varName}") {varType} {varName}"""

    def __template_getter(self):
        return """
    public {varType} get{VarName}() {
        return {varName}
    }"""

    def __template_setter(self):
        return """
    public void set{VarName}({varType} {varName}) {
        this.{varName} = {varName};
    }"""

    def __tstamp(self):
        return str(datetime.now()).replace('-', '').replace(':', '').replace(' ', '')[:14]

    def gen_file(self):
        with open(f"output/{self.data['class']}{self.__tstamp()}.java", 'a') as fo:
            for impt in self.data['imports']:
                fo.write("import " + impt.replace("import", impt) + linesep)
            fo.write(linesep)

            fo.write("public class " + self.data['class'] + " {" + linesep + linesep)

            for field in self.data['fields']:
                fo.write(f"        private {field['type']} {field['name']};" + linesep)
            fo.write(linesep)

            fo.write(self.__template_decl().replace("{class}", self.data['class']))
            fo.write(linesep)

            i = 0
            for field in self.data['fields']:
                strr = self.__template_constructor().replace("{varName}", field['name']).replace("{varType}", field['type'])
                if len(self.data['fields']) > 1 and i < len(self.data['fields']) - 1:
                    strr += ','
                else:
                    strr += ') {'
                i += 1
                fo.write(strr + linesep)
            fo.write(linesep)
            
            for field in self.data['fields']:
                fo.write(f"                this.{field['name']} = {field['name']};" + linesep)
            fo.write('        }' + linesep)
            

            for field in self.data['fields']:
                strrG = self.__template_getter().replace("{varName}", field['name']).replace("{varType}", field['type']).\
                            replace("{VarName}", self.__capitalize_first(field['name']))
                fo.write(strrG + linesep)
                fo.write(linesep)

                if self.data['setters']:
                    strrS = self.__template_setter().replace("{varName}", field['name']).replace("{varType}", field['type']).\
                                replace("{VarName}", self.__capitalize_first(field['name']))
                    fo.write(strrS + linesep)
                    fo.write(linesep)

            fo.write('}')

if __name__ == '__main__':
    cg = ClassGenerator()
    cg.proc_config()
    cg.gen_file()
