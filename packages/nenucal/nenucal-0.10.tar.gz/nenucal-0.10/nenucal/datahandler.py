import os
import re
import glob
import fnmatch
import itertools
import subprocess
from collections import defaultdict

import toml

from libpipe import attrmap, worker


def get_hosts(host_string, unique=True):
    hosts = [host for k in host_string.split(',') for host in worker.expend_num_ranges(k)]
    if unique:
        hosts = list(set(hosts))
    return [worker.localhost_shortname if h == 'localhost' else h for h in hosts]


class DataHandler(object):

    def __init__(self, spectral_windows, data_level, obs_ids, n2_obs_ids, remote_hosts, l1_to_l2_config, nodes_distribution):
        self.spectral_windows = spectral_windows
        self.data_level = data_level
        self.obs_ids = obs_ids
        self.n2_obs_ids = n2_obs_ids
        self.remote_hosts = remote_hosts
        self.l1_to_l2_config = l1_to_l2_config
        self.nodes_distribution = nodes_distribution
        self.sw_index = dict(zip(self.get_spectral_windows(), range(len(self.get_spectral_windows()))))

    @staticmethod
    def from_file(filename):
        s = toml.load(filename, _dict=defaultdict)
        for n in ['obs_ids', 'spectral_windows', 'data_level_path']:
            assert n in s, f'{n} need to be defined in {filename}'

        return DataHandler(s['spectral_windows'], s['data_level_path'], s['obs_ids'], s.get('n2_obs_ids', dict()),
                           s.get('remote_hosts', dict()), s.get('l1_to_l2_config', dict()), 
                           s.get('nodes_distribution', dict()))

    def get_obs_ids(self, obs_id_match=None, include_n2_obs_ids=True):
        all_obs_ids = list(self.obs_ids.keys() )
        if include_n2_obs_ids:
            all_obs_ids += list(self.n2_obs_ids.keys())
        if obs_id_match is None:
            return all_obs_ids
        return attrmap.OrderedSet(obs_id for k in obs_id_match.split(',') for obs_id in fnmatch.filter(all_obs_ids, k))

    def is_n2_obs_id(self, obs_id):
        return obs_id in self.n2_obs_ids.keys()

    def get_nodes_distribution(self):
        return self.nodes_distribution

    def get_obs_ids_and_spectral_windows(self, obs_id_sw_match):
        if ":" in obs_id_sw_match:
            obs_id_sw_match, sws_str = obs_id_sw_match.split(':')
            sws = fnmatch.filter(self.get_spectral_windows(include_composite_sws=True), sws_str)
        else:
            sws = self.get_spectral_windows()

        return self.get_obs_ids(obs_id_sw_match), sws

    def get_sbs(self, sw):
        sbs = []
        if self.is_composite_sw(sw):
            for sub_sw in self.get_composite_sub_sws(sw):
                sbs.extend(self.get_sbs(sub_sw))
        else:
            sb_l, sb_r = self.spectral_windows[sw]
            sbs = list(range(int(sb_l), int(sb_r) + 1))
        return sbs

    def is_composite_sw(self, sw):
        return isinstance(self.spectral_windows[sw], list) and all(isinstance(item, str) for item in self.spectral_windows[sw])

    def get_composite_sub_sws(self, sw):
        if self.is_composite_sw(sw):
            return self.spectral_windows[sw]
        return []

    def get_spectral_windows(self, include_composite_sws=False):
        if include_composite_sws:
            return self.spectral_windows.keys()
        else:
            return [key for key, value in self.spectral_windows.items() if not self.is_composite_sw(key)]

    def get_all_hosts(self):
        n2_nodes = set(n for n2_obs_id in self.n2_obs_ids.keys() for n in self.get_n2_nodes(n2_obs_id))
        n1_nodes = set(n for l in self.obs_ids.values() for n in l)
        return list(n1_nodes.union(n2_nodes))

    def get_remote_hosts(self):
        return self.remote_hosts.keys()

    def get_remote_host(self, remote_host):
        assert remote_host in self.remote_hosts, f'{remote_host} needs to be defined'
        return self.remote_hosts[remote_host]['host']

    def get_remote_level(self, remote_host):
        assert remote_host in self.remote_hosts, f'{remote_host} needs to be defined'
        return self.remote_hosts[remote_host]['level']

    def get_remote_nodes(self, remote_host):
        assert remote_host in self.remote_hosts, f'{remote_host} needs to be defined'
        nodes = self.remote_hosts[remote_host]['nodes']

        if isinstance(nodes, str):
            nodes = sorted(get_hosts(nodes, unique=True))

        return nodes

    def get_remote_password_file(self, remote_host):
        assert remote_host in self.remote_hosts, f'{remote_host} needs to be defined'

        return self.remote_hosts[remote_host]['password_file']

    def get_remote_data_path(self, remote_host, obs_id, level, node=None):
        assert remote_host in self.remote_hosts, f'{remote_host} needs to be defined'

        # Retrieve the base data path for the remote host
        data_path = self.remote_hosts[remote_host]['data_path']

        # Extract year, month, and other elements from obs_id
        date = obs_id.split('_')[0]
        year = date[:4]
        month = date[4:6]

        # Replace placeholders in the path
        data_path = data_path.replace('%YEAR%', year)
        data_path = data_path.replace('%MONTH%', month)
        data_path = data_path.replace('%OBS_ID%', obs_id)
        data_path = data_path.replace('%LEVEL%', level)
        if node is not None:
            data_path = data_path.replace('%NODE%', node)

        return data_path

    def get_l1_to_l2_config(self, l2_level, obs_id):
        assert l2_level in self.l1_to_l2_config, f'{l2_level} needs to be defined'

        dppp_config_path = self.l1_to_l2_config[l2_level]['dppp_config']

        # Read the dppp_config file
        with open(dppp_config_path, 'r') as file:
            lines = file.readlines()

        # Create a list to store the modified lines with script output
        modified_lines = []

        # Regular expression to match the '%script script_file_name%' pattern
        script_pattern = re.compile(r'%script\s+(.+?)%')

        for line in lines:
            # Search for the '%script ...%' pattern in the line
            match = script_pattern.search(line)
            if match:
                # Extract the script file name from the pattern
                script_file_name = match.group(1).strip()

                # Execute the shell script with obs_id as the argument
                result = subprocess.run([script_file_name, obs_id], capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(f"Error running script {script_file_name}: {result.stdout}")

                # Replace the '%script script_file_name%' pattern with the output of the script
                script_output = result.stdout.strip()
                modified_line = script_pattern.sub(script_output, line)
                modified_lines.append(modified_line)

        return dppp_config_path, modified_lines

    def get_levels(self):
        return self.data_level.keys()

    def get_node(self, obs_id, sw):
        assert not self.is_n2_obs_id(obs_id)
        return self.obs_ids[obs_id][self.sw_index[sw]]

    def get_n2_nodes(self, n2_obs_id):
        nodes = self.n2_obs_ids[n2_obs_id]['nodes']
        if isinstance(nodes, str):
            nodes = sorted(get_hosts(nodes, unique=True))
        return nodes

    def get_n1_obs_ids(self, n2_obs_id):
        return self.n2_obs_ids[n2_obs_id]['n1_obs_ids']

    def get_dir_path(self, obs_id, level, sw, node=None):
        if node is None:
            node = self.get_node(obs_id, sw)
        date = obs_id.split('_')[0]
        year = date[:4]
        month = date[4:6]

        data_path = self.data_level[level]

        if self.is_n2_obs_id(obs_id):
            n1_obs_id = self.get_n1_obs_ids(obs_id)[0]
        else:
            n1_obs_id = obs_id

        obs_id_in_data_path = '%OBS_ID%' in data_path or '%N1_OBS_ID%' in data_path

        data_path = data_path.replace('%YEAR%', year).replace('%MONTH%', month)
        data_path = data_path.replace('%OBS_ID%', obs_id).replace("%NODE%", node)
        data_path = data_path.replace('%N1_OBS_ID%', n1_obs_id)

        # If obs_id is already in the data_path, do not add it at the end:
        if not obs_id_in_data_path:
            data_path = os.path.join(data_path, obs_id)

        return data_path

    def get_ms_path(self, obs_id, level, sw):
        if self.is_n2_obs_id(obs_id):
            if level.lower().startswith('l1'):
                return list(itertools.chain.from_iterable(self.get_ms_path(n1_obs_id, level, sw) for n1_obs_id in self.get_n1_obs_ids(obs_id)))

            mss = []
            for i, node in enumerate(self.get_n2_nodes(obs_id)):
                dir_path = self.get_dir_path(obs_id, level, sw, node)
                mss.extend(sorted(glob.glob(f'{dir_path}/{sw}_T[0-9][0-9][0-9].MS')))
            mss = sorted(mss, key=lambda x: int(x.split('_T')[1][:3]))
            return mss
        else:
            if self.is_composite_sw(sw):
                paths = []
                for sub_sw in self.get_composite_sub_sws(sw):
                    paths.extend(self.get_ms_path(obs_id, level, sub_sw))
                return paths
            else:
                dir_path = self.get_dir_path(obs_id, level, sw)

                if level.lower().startswith('l1'):
                    return [f'{dir_path}/SB{sb}.MS' for sb in self.get_sbs(sw)]

                return [f'{dir_path}/{sw}.MS']

    def get_all_ms_path(self, obs_ids, levels, sws):
        for obs_id in obs_ids:
            for level in levels:
                for sw in sws:
                    yield from self.get_ms_path(obs_id, level, sw)
