#!/usr/bin/python
# encoding: utf-8

from os import path, walk
import argparse

class SSHConfigGroups(object):
    def __init__(self):
        self._groups = {}

    def add_group(self, name, config):
        if name in self._groups:
            raise ValueError("Group %s already defined" % name)
        self._groups[name] = config

    def get_group(self, name):
        if name not in self._groups:
            raise KeyError("Group %s not defined" % name)
        return self._groups[name]

ConfigGroups = SSHConfigGroups()

def partition_list(l, max_length):
    cur = []
    for x in l:
        if len(' '.join(cur + [x])) < max_length:
            cur.append(x)
        else:
            yield(cur)
            cur = [x]
    if cur:
        yield(cur)


class SSHConfig(object):
    def __init__(self):
        self.content = []
        self.servers = {}
        self.host_config = []
        self.linenumber = 0
        self.group_name = None

    def handle_previous(self):
        if self.group_name is not None:
            if self.group_name == '##ALL##':
                for i in partition_list(self.servers, 1000):
                    servers = ' '.join(i)
                    self.add_content('Host %s\n' % servers)
                    self.add_content(''.join(self.host_config))
                    self.add_content('\n')
            else:
                ConfigGroups.add_group(self.group_name, self.host_config)
        self.host_config = []
        self.group_name = None

    def add_content(self, line):
        if line.lower().strip().startswith('group '):
            name = line.lower().strip().split()[1]
            for group_line in ConfigGroups.get_group(name):
                self.add_content(group_line)
        else:
            self.content += line



    def read(self, filehandle, filename):
        for line in filehandle.readlines():
            self.linenumber += 1
            if line.lower().startswith("# disabled: yes"):
                print("Ignoring %s" % filename)
                self.content = []
                break
            elif line.startswith("#") or len(line) < 2:
                continue

            elif line.lower().startswith('group '):
                self.handle_previous()
                self.group_name = line.lower().split()[1]
                continue

            elif line.lower().startswith('host '):
                self.handle_previous()
                self.content += ['\n']
                if '##ALL##' in line:
                    self.group_name = "##ALL##"
                    continue
                else:
                    for server in line.split("#")[0].split()[1:]:
                        if server not in self.servers.keys():

                            self.servers[server] = "%s:%s" % (filename, self.linenumber)
                        else:
                            print("Warning, redefined server %s on %s:%s, previous %s" % (server, filename, self.linenumber, self.servers[server]))

            if not self.group_name:
                self.add_content(line)
            self.host_config.append(line)
        self.handle_previous()

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
            for filename in sorted(files):
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", help="Target file for config")
    args = parser.parse_args()
    if args.target:
        o = SSHConfigManager(target=args.target)
    else:
        o = SSHConfigManager()
    o.process()




