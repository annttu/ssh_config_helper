#!/usr/bin/python
# encoding: utf-8

from os import path, walk


class SSHConfig(object):
    def __init__(self):
        self.content = []
        self.servers = []

    def read(self, filehandle, filename):
        for line in filehandle.readlines():
            if line.lower().startswith("# disabled: yes"):
                print("Ignoring %s" % filename)
                break
            elif line.startswith("#") or len(line) < 2:
                continue
            elif line.lower().startswith('host '):
                self.content += ['\n']
                if '##ALL##' in line:
                    line = 'Host ' + ' '.join(self.servers) + '\n'
                else:
                    self.servers += line.split()[1:]
            self.content += line

    def export(self):
        return ''.join(self.content)


class SSHConfigManager(object):
    def __init__(self, configs='~/.ssh/config.d', target='~/.ssh/config'):
        self.configs = path.expanduser(configs)
        self.target = path.expanduser(target)

    def process(self):
        if path.isdir(self.configs) is False:
            print("Not such directory %s" % self.configs)
            return False
        of = open(self.target, 'w')
        for root, dirs, files in walk(self.configs):
            for filename in files:
                if not filename.endswith('.conf'):
                    print("Ignoring %s" % filename)
                    continue
                f = open(path.join(root, filename), 'r')
                sshconfig = SSHConfig()
                sshconfig.read(f, filename)
                of.write(sshconfig.export())
        of.close()
        print("Processed %s" % self.target)


if __name__ == '__main__':
    o = SSHConfigManager()
    o.process()




