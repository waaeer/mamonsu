# -*- coding: utf-8 -*-

import time
import math
import sys
import logging

from mamonsu import __version__ as mamonsu_version
from mamonsu.tools.sysinfo.linux import SysInfoLinux
from mamonsu.tools.report.format import header_h1, header_h2, key_val_h1, key_val_h2


class SystemInfo(SysInfoLinux):

    def __init__(self, args):
        sudo = False if (args.disable_sudo is False) else True
        super(SystemInfo, self).__init__(use_sudo=sudo)
        self.args = args

    def printable_info(self):
        out = ''
        out += header_h1('Report')
        out += key_val_h1('Version', mamonsu_version)
        out += key_val_h1('Platform', sys.platform)
        out += key_val_h1('Python', ' '.join(sys.version.split("\n")))
        out += header_h1('System')
        out += key_val_h1('Date', self.date)
        out += key_val_h1('Host', self.hostname)
        out += key_val_h1('Uptime', self.uptime_raw)
        out += key_val_h1('Boot time', self.boot_time_raw)
        out += key_val_h1('System', self.dmi_info['TOTAL'])
        out += key_val_h1('Serial', self.dmi_info['SERIAL'])
        out += key_val_h1('Release', self.release)
        out += header_h2('Kernel:')
        out += key_val_h2('name', self.kernel)
        out += key_val_h2('cmdline', self.kernel_cmdline)
        out += key_val_h1('Arch', 'CPU = {0}, OS = {1}'.format(
            self.cpu_arch, self.os_arch))
        out += key_val_h1('Virt', self.virtualization)
        out += header_h1('Processors')
        out += key_val_h1('Total', self.cpu_model['_TOTAL'])
        out += key_val_h1('Speed', self.cpu_model['speed'])
        out += key_val_h1('Model', self.cpu_model['model'])
        out += key_val_h1('Cache', self.cpu_model['cache'])
        out += key_val_h1('Bench', self.cpu_bench())
        out += header_h1('TOP (by cpu)')
        out += self.top_by_cpu + "\n"
        out += header_h1('Memory')
        out += key_val_h1('Total', self._humansize(self.meminfo['_TOTAL']))
        out += key_val_h1('Cached', self._humansize(self.meminfo['_CACHED']))
        out += key_val_h1('Buffers', self._humansize(self.meminfo['_BUFFERS']))
        out += key_val_h1('Dirty', self._humansize(self.meminfo['_DIRTY']))
        out += key_val_h1('Dirty ratio', '{0} {1}'.format(
            self.sysctl_fetch('vm.dirty_ratio'),
            self.sysctl_fetch('vm.dirty_background_ratio')))
        out += key_val_h1('Dirty bytes', '{0} {1}'.format(
            self.sysctl_fetch('vm.dirty_bytes'),
            self.sysctl_fetch('vm.dirty_background_bytes')))
        # todo: overcommit
        out += key_val_h1('Swap', self._humansize(self.meminfo['_SWAP']))
        if 'vm.swappiness' in self.sysctl:
            out += key_val_h1('Swappines', self.sysctl['vm.swappiness'])
        out += header_h1('TOP (by memory)')
        out += self.top_by_memory + "\n"
        out += header_h1('System settings')
        for k in self.systemd['_main']:
            out += key_val_h1(k, self.systemd['_main'][k])
        out += header_h1('Mount')
        out += self.df_raw + "\n"
        out += header_h1('Disks')
        for disk in self.block_info:
            out += key_val_h1(disk, 'Scheduler: {0} Queue: {1}'.format(
                self.block_info[disk]['scheduler'],
                self.block_info[disk]['nr_requests']))
        out += header_h1('Sysctl')
        out += header_h2('kernel.')
        out += key_val_h2('hostname', self.sysctl_fetch('kernel.hostname'), ' = ')
        out += key_val_h2('osrelease', self.sysctl_fetch('kernel.osrelease'), ' = ')
        out += key_val_h2('hung_task_panic', self.sysctl_fetch('kernel.hung_task_panic'), ' [bool] = ')
        out += key_val_h2('hung_task_timeout_secs', self.sysctl_fetch('kernel.hung_task_timeout_secs'), ' = ')
        out += key_val_h2('shmall', self.sysctl_fetch('kernel.shmall'), ' [4-KiB pages, max size of shared memory] = ')
        out += key_val_h2('shmmax', self.sysctl_fetch('kernel.shmmax'), ' [max segment size in bytes] = ')
        out += key_val_h2('shmmni', self.sysctl_fetch('kernel.shmmni'), ' [max number of segments] = ')
        out += key_val_h2('sched_min_granularity_ns', self.sysctl_fetch('kernel.sched_min_granularity_ns'), ' [nanosecs] = ')
        out += key_val_h2('sched_latency_ns', self.sysctl_fetch('kernel.sched_latency_ns'), ' [nanosecs] = ')
        out += header_h2('fs.')
        out += key_val_h2('file-max', self.sysctl_fetch('fs.file-max'), ' [fd system] = ')
        out += key_val_h2('nr_open', self.sysctl_fetch('fs.nr_open'), ' [fd per proc] = ')
        out += key_val_h2('inode-nr', self.sysctl_fetch('fs.inode-nr'), ' [inodes] = ')
        out += header_h2('vm.')
        out += key_val_h2('dirty_expire_centisecs', self.sysctl_fetch('vm.dirty_expire_centisecs'), ' = ')
        out += key_val_h2('dirty_writeback_centisecs', self.sysctl_fetch('vm.dirty_writeback_centisecs'), ' = ')
        out += key_val_h2('nr_hugepages', self.sysctl_fetch('vm.nr_hugepages'), ' = ')
        out += key_val_h2('nr_overcommit_hugepages', self.sysctl_fetch('vm.nr_overcommit_hugepages'), ' = ')
        out += key_val_h2('overcommit_memory', self.sysctl_fetch('vm.overcommit_memory'), ' = ')
        out += key_val_h2('overcommit_ratio', self.sysctl_fetch('vm.overcommit_ratio'), ' = ')
        out += key_val_h2('oom_kill_allocating_task', self.sysctl_fetch('vm.oom_kill_allocating_task'), ' = ')
        out += key_val_h2('panic_on_oom', self.sysctl_fetch('vm.panic_on_oom'), ' = ')
        out += key_val_h2('swappiness', self.sysctl_fetch('vm.swappiness'), ' = ')
        out += header_h1('IOstat')
        out += self.iostat_raw + "\n"
        out += header_h1('LVM')
        out += self.vgs_raw + "\n"
        out += self.lvs_raw + "\n"
        out += header_h1('Raid')
        if not self.is_empty(self.raid):
            for raid in self.raid:
                out += key_val_h1('Controller', raid)
        return out

    def store_raw(self):
        def format_out(info, val):
            return "# {0} ##################################\n{1}\n".format(
                info, val)
        out = format_out('SYSCTL', self.sysctl['_RAW'])
        out += format_out('DMESG', self.dmesg_raw)
        out += format_out('LSPCI', self.lspci_raw)
        out += format_out('CPUINFO', self.cpu_model['_RAW'])
        out += format_out('MEMINFO', self.meminfo['_RAW'])
        out += format_out('DMIDECODE', self.dmi_raw)
        out += format_out('DF', self.df_raw)
        out += format_out('MOUNT', self.mount_raw)
        out += format_out('MDSTAT', self.mdstat_raw)
        out += format_out('IOSTAT', self.iostat_raw)
        out += format_out('LVS', self.lvs_raw)
        out += format_out('VGS', self.vgs_raw)
        return out.encode('ascii', 'ignore').decode('ascii')

    def collect(self):
        info = self.printable_info()
        logging.error("\n{0}\n".format(self.store_raw()))
        return info.encode('ascii', 'ignore').decode('ascii')

    _suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    def _humansize(self, nbytes):
        if nbytes == 0:
            return '0 B'
        i = 0
        while nbytes >= 1024 and i < len(self._suffixes) - 1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, self._suffixes[i])

    def cpu_bench(self):
        def _is_prime(n):
            if n % 2 == 0:
                return False
            sqrt_n = int(math.floor(math.sqrt(n)))
            for i in range(3, sqrt_n + 1, 2):
                if n % i == 0:
                    return False
            return True

        begin, y = time.time(), 0
        for x in range(1, 500000):
            if _is_prime(x):
                y = max(x, y)
        return str(round(100 * float(time.time() - begin)) / 100)
