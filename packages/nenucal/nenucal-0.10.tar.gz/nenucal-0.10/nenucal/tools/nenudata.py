#!/usr/bin/env python

import os
import sys
import itertools
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import toml
import click
from tabulate import tabulate
from click import confirm, style

import numpy as np

from nenucal import __version__, msutils
from nenucal import datahandler

from libpipe import worker, futils

t_file = click.Path(exists=True, dir_okay=False)

ms_file_to_check = 'table.info'


def get_remote_ms_files(remote_host_name, l2_level, obs_id, sw):
    '''Retrieve the list of MS files for a given obs_id and spectral window from the remote host'''
    ms_command = f"ssh {remote_host_name} 'nenudata get_ms {l2_level} {obs_id} --sws {sw}'"
    result = subprocess.run(ms_command, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        error_message = result.stderr if result.stderr else result.stdout
        print(f"Error retrieving MS list for {obs_id}, SW {sw}: {error_message}")
        return []

    return result.stdout.strip().split()


def ssh_makedirs(remote_host, target_dir):
    '''Create a directory on the remote host using SSH'''
    mkdir_command = f'ssh {remote_host} "mkdir -m 2775 -p {target_dir}"'
    mkdir_result = subprocess.run(mkdir_command, shell=True)
    if mkdir_result.returncode != 0:
        sys.exit(f"Error creating directory {target_dir} on remote host {remote_host}")


@click.group()
@click.version_option(__version__)
def main():
    ''' NenuFAR-CD data management utilities ...'''


@main.command('list')
@click.argument('obs_ids', type=str)
@click.option('--config', '-c', help='Data handler configuration file', type=t_file, default='data_handler.toml')
def list(obs_ids, config):
    ''' List all obs_ids '''
    dh = datahandler.DataHandler.from_file(config)

    header = ['Obs_id'] + [*dh.get_levels()]
    data = []

    for obs_id in dh.get_obs_ids(obs_ids):
        o = [obs_id]
        for level in dh.get_levels():
            counts = []
            for sw in dh.get_spectral_windows():
                mss = dh.get_ms_path(obs_id, level, sw)
                n_mss = len(mss)
                n_mss_exists = sum([os.path.exists(ms + f'/{ms_file_to_check}') for ms in mss])
                if n_mss == n_mss_exists:
                    counts.append(style(f'{n_mss}', fg='green'))
                elif n_mss_exists > 0:
                    counts.append(style(f'{n_mss_exists}', fg='yellow'))
                else:
                    counts.append(style(f'0', fg='red'))
            o.append(','.join(counts))
        data.append(o)

    print(tabulate(data, header))


@main.command('add')
@click.argument('obs_id', type=str)
@click.argument('nodes_distribution_id', type=str)
@click.option('--config', '-c', help='Data handler configuration file', type=t_file, default='data_handler.toml')
def add(obs_id, nodes_distribution_id, config):
    ''' Add obs_id '''
    dh = datahandler.DataHandler.from_file(config)

    if nodes_distribution_id not in dh.get_nodes_distribution():
        print(f'Error: nodes distribution ID {nodes_distribution_id} does not exist.')
        sys.exit(0)

    if obs_id in dh.get_obs_ids():
        print(f'Error: observation ID {obs_id} already exist.')
        sys.exit(0)

    nodes = dh.get_nodes_distribution()[nodes_distribution_id]

    if confirm(f'Adding {obs_id} with nodes {",".join(nodes)}'):
        s = toml.load(config, _dict=defaultdict)
        s['obs_ids'][obs_id] = nodes
        f = f'{config}.{datetime.now().strftime("%Y%m%d")}'
        backup_config = f
        i = 1
        while os.path.exists(backup_config):
            backup_config = f'{f}.{i}'
            i += 1

        os.rename(config, backup_config)

        with open(config, mode='w') as f:
            toml.dump(dict(s), f)

        print('Done !')

@main.command('add_all')
@click.argument('obs_ids', type=str, nargs=-1)
@click.option('--config', '-c', help='Data handler configuration file', type=t_file, default='data_handler.toml')
@click.option('--skip_existing', '-s', help='Skip existing OBS_ID', is_flag=True)
def add_all(obs_ids, config, skip_existing):
    ''' Add all obs_id '''
    dh = datahandler.DataHandler.from_file(config)
    s = toml.load(config, _dict=defaultdict)
    all_obs_ids = dh.get_obs_ids()

    for obs_id, nodes_distribution_id in zip(obs_ids, itertools.cycle(dh.get_nodes_distribution().keys())):
        if obs_id in all_obs_ids:
            print(f'Error: observation ID {obs_id} already exist.')
            if not skip_existing:
                sys.exit(0)

        nodes = dh.get_nodes_distribution()[nodes_distribution_id]
        print(f'Adding {obs_id} with nodes {",".join(nodes)} (ID: {nodes_distribution_id})')
        s['obs_ids'][obs_id] = nodes

    if len(obs_ids) > 0:
        if confirm('Confirm update ?'):
            f = f'{config}.{datetime.now().strftime("%Y%m%d")}'
            backup_config = f
            i = 1
            while os.path.exists(backup_config):
                backup_config = f'{f}.{i}'
                i += 1

            os.rename(config, backup_config)

            with open(config, mode='w') as f:
                toml.dump(dict(s), f)

            print('Done !')
        else:
            print('Changes discarded.')


@main.command('get_obs_ids')
@click.argument('obs_ids', type=str)
@click.option('--config', '-c', help='Data handler configuration file', type=t_file, default='data_handler.toml')
def get_obs_ids(obs_ids, config):
    ''' List all obs_ids (without existence check) '''
    dh = datahandler.DataHandler.from_file(config)

    print('\n'.join(dh.get_obs_ids(obs_ids)))


@main.command('get_ms')
@click.argument('level', type=str)
@click.argument('obs_ids', type=str)
@click.option('--config', '-c', help='Data handler configuration file', type=t_file, default='data_handler.toml')
@click.option('--sws', '-s', help='Spectral windows', type=str, default='all')
@click.option('--post_path', '-p', help='Add post_path to the path of the MS', type=str, default='')
def get_ms(level, obs_ids, config, sws, post_path):
    ''' Return a list of all MS corresponding to given OBS_IDS and SWS '''
    dh = datahandler.DataHandler.from_file(config)

    if post_path and not post_path.startswith('/'):
        post_path = '/' + post_path

    if sws == 'all':
        sws = dh.get_spectral_windows()
    else:
        sws = [k.upper() for k in sws.split(',')]

    for obs_id in dh.get_obs_ids(obs_ids):
        for sw in sws:
            print(f' '.join([f'{k}/{post_path}' for k in dh.get_ms_path(obs_id, level, sw)]), end=' ')


@main.command('remove')
@click.argument('level', type=str)
@click.argument('obs_ids', type=str)
@click.option('--config', '-c', help='Data handler configuration file', type=t_file, default='data_handler.toml')
@click.option('--sws', '-s', help='Spectral windows', type=str, default='all')
def remove(level, obs_ids, config, sws):
    ''' Remove all MS corresponding to given OBS_IDS and SWS '''
    dh = datahandler.DataHandler.from_file(config)

    if sws == 'all':
        sws = dh.get_spectral_windows()
    else:
        sws = [k.upper() for k in sws.split(',')]

    obs_ids = dh.get_obs_ids(obs_ids)

    if confirm(style(f'Removing obs_ids {",".join(obs_ids)} for SW {",".join(sws)} ?', fg='yellow')):
        for obs_id in obs_ids:
            for sw in sws:
                for ms in dh.get_ms_path(obs_id, level, sw):
                    futils.rm_if_exist(ms, verbose=True)
    else:
        print('No changes made.')


@main.command('retrieve')
@click.argument('remote_host', type=str)
@click.argument('obs_ids', type=str)
@click.option('--config', '-c', help='Data handler configuration file', type=t_file, default='data_handler.toml')
@click.option('--dry_run', help='Run in dry mode', is_flag=True)
@click.option('--run_on_host', help='Run rsync on specified host', type=str, default='target_host')
@click.option('--sws', '-s', help='Spectral windows', type=str, default='all')
def retrieve(obs_ids, remote_host, config, dry_run, run_on_host, sws):
    ''' Return a list of all MS corresponding to given OBS_IDS and SWS '''
    dh = datahandler.DataHandler.from_file(config)
    assert remote_host in dh.get_remote_hosts(), f'Remote host {remote_host} needs to be defined in {config}'

    target_level = dh.get_remote_level(remote_host)
    target_host = dh.get_remote_host(remote_host)

    assert target_level in dh.get_levels(), f'{target_level} data level can be retrieved'

    all_hosts = dh.get_all_hosts()
    if run_on_host != 'target_host' and run_on_host not in all_hosts:
        all_hosts.append(run_on_host)

    if sws == 'all':
        sws = dh.get_spectral_windows()
    else:
        sws = [k.upper() for k in sws.split(',')]

    w = worker.WorkerPool(all_hosts, name='Transfert', max_tasks_per_worker=1, debug=dry_run, dry_run=dry_run)

    for obs_id in dh.get_obs_ids(obs_ids, include_n2_obs_ids=False):
        remote_path = dh.get_remote_data_path(remote_host, obs_id, target_level)

        for sw in sws:
            files = ' '.join([f'{target_host}:{remote_path}/SB{sb}.MS' for sb in dh.get_sbs(sw)])
            target = dh.get_dir_path(obs_id, target_level, sw)
            if run_on_host =='target_host':
                node = dh.get_node(obs_id, sw)
            else:
                node = run_on_host

            for i in range(100):
                log_file = f'{target}/transfert_{i}.log'
                if not os.path.exists(log_file):
                    break

            if not os.path.exists(target):
                os.makedirs(target)

            cmd = f'rsync --progress -v -am {files} {target}'

            w.add(cmd, run_on_host=node, output_file=log_file)

    w.execute()


@main.command('retrieve_l2')
@click.argument('remote_host_name', type=str)
@click.argument('obs_ids', type=str)
@click.argument('l2_level', type=str)
@click.option('--config', '-c', help='Data handler configuration file', type=t_file, default='data_handler.toml')
@click.option('--dry_run', help='Run in dry mode', is_flag=True)
@click.option('--run_on_host', help='Run rsync on specified host', type=str, default='target_host')
@click.option('--sws', '-s', help='Spectral windows', type=str, default='all')
def retrieve_l2(remote_host_name, obs_ids, l2_level, config, dry_run, run_on_host, sws):
    '''Retrieve L2 data corresponding to given OBS_IDS and SWS'''

    dh = datahandler.DataHandler.from_file(config)
    assert remote_host_name in dh.get_remote_hosts(), f'Remote host {remote_host_name} needs to be defined in {config}'

    all_hosts = dh.get_all_hosts()
    if run_on_host != 'target_host' and run_on_host not in all_hosts:
        all_hosts.append(run_on_host)

    # Process spectral windows (sws)
    if sws == 'all':
        sws = dh.get_spectral_windows()
    else:
        sws = [k.upper() for k in sws.split(',')]

    w = worker.WorkerPool(all_hosts, name='Transfer L2', max_tasks_per_worker=1, debug=dry_run, dry_run=dry_run)

    remote_host = dh.get_remote_host(remote_host_name)

    for obs_id in dh.get_obs_ids(obs_ids, include_n2_obs_ids=True):
        # Get nodes for this obs_id
        nodes = dh.get_n2_nodes(obs_id)
        if not nodes:
            print(f"No nodes found for {obs_id}")
            continue

        # Loop through each spectral window
        for sw in sws:
            node_cycle = itertools.cycle(nodes)
            ms_files = get_remote_ms_files(remote_host_name, l2_level, obs_id, sw)
            if not ms_files:
                sys.exit(f"No MS files found for {obs_id}, SW {sw}")

            for ms in ms_files:
                # Cycle through nodes and associate each MS file with a local node
                local_node = next(node_cycle)
                target_dir = dh.get_dir_path(obs_id, l2_level, sw)

                os.makedirs(target_dir, mode=0o2775, exist_ok=True)

                # Build the rsync command
                rsync_cmd = f'rsync --progress -v -am --chmod=ug+w {remote_host}:{ms} {target_dir}'

                # Log file for rsync
                for i in range(100):
                    log_file = f'{target_dir}/transfert_l2_{i}.log'
                    if not os.path.exists(log_file):
                        break

                # Add the rsync command to the worker pool
                selected_node = local_node if run_on_host == 'target_host' else run_on_host
                w.add(rsync_cmd, run_on_host=selected_node, output_file=log_file)

    # Execute the WorkerPool
    w.execute()


@main.command('push_l2')
@click.argument('remote_host_name', type=str)
@click.argument('obs_ids', type=str)
@click.argument('l2_level', type=str)
@click.option('--config', '-c', help='Data handler configuration file', type=t_file, default='data_handler.toml')
@click.option('--dry_run', help='Run in dry mode', is_flag=True)
@click.option('--sws', '-s', help='Spectral windows', type=str, default='all')
def push_l2(remote_host_name, obs_ids, l2_level, config, dry_run, sws):
    '''Push L2 data from local to remote host corresponding to given OBS_IDS and SWS'''

    dh = datahandler.DataHandler.from_file(config)
    assert remote_host_name in dh.get_remote_hosts(), f'Remote host {remote_host_name} needs to be defined in {config}'

    # Process spectral windows (sws)
    if sws == 'all':
        sws = dh.get_spectral_windows()
    else:
        sws = [k.upper() for k in sws.split(',')]

    w = worker.WorkerPool([worker.localhost_shortname], name='Transfer L2', max_tasks_per_worker=1, debug=dry_run, dry_run=dry_run)

    remote_host = dh.get_remote_host(remote_host_name)
    created_dirs = set()

    for obs_id in dh.get_obs_ids(obs_ids, include_n2_obs_ids=True):
        # Get nodes for this obs_id
        nodes = dh.get_remote_nodes(remote_host_name)
        if not nodes:
            print(f"No nodes found for {obs_id}")
            continue

        # Loop through each spectral window
        for sw in sws:
            node_cycle = itertools.cycle(nodes)
            ms_files = dh.get_ms_path(obs_id, l2_level, sw)
            if not ms_files:
                sys.exit(f"No MS files found for {obs_id}, SW {sw}")

            # Retrieve the remote path and perform variable replacement
            for ms in ms_files:
                remote_node = next(node_cycle)
                target_dir = dh.get_remote_data_path(remote_host_name, obs_id, l2_level, remote_node)

                # Create remote target directory using SSH if it hasn't been created already
                if not dry_run and target_dir not in created_dirs:
                    ssh_makedirs(remote_host, target_dir)
                    created_dirs.add(target_dir)

                # Build the rsync command
                rsync_cmd = f'rsync --progress -v -am --chmod=ug+w {ms} {remote_host}:{target_dir}'

                # Log file for rsync (store in logs directory of the parent directory of the MS file)
                log_dir = Path(ms).parent / 'logs'
                log_dir.mkdir(parents=True, exist_ok=True)
                for i in range(100):
                    log_file = log_dir / f'transfert_l2_{i}.log'
                    if not log_file.exists():
                        log_file = log_file
                        break

                # Add the rsync command to the worker pool
                w.add(rsync_cmd, output_file=log_file)

    # Execute the WorkerPool
    w.execute()


@main.command('l1_to_l2')
@click.argument('level', type=str)
@click.argument('obs_ids', type=str)
@click.option('--config', '-c', help='Data handler configuration file', type=t_file, default='data_handler.toml')
@click.option('--force', help='Force overwrite data if already exists', is_flag=True)
@click.option('--l1_level', help='L1 level name', type=str, default='L1')
@click.option('--max_concurrent', '-m', help='Maximum concurrent tasks on a node', type=int, default=1)
@click.option('--dry_run', help='Do not do anything', is_flag=True)
@click.option('--env_file', help='Environment file', type=str, default='~/.bashrc')
@click.option('--n_slots_per_chunk', help='Specify the chunk duration in number of slots', type=int, default=150)
@click.option('--tolerance', help='Tolerance for handling the remainder chunk as a fraction of chunk_duration', type=float, default=0.25)
@click.option('--hosts', help='Lists of hosts where to run DP3', type=str, default=None)
def l1_to_l2(level, obs_ids, config, force, l1_level, max_concurrent, dry_run, env_file, n_slots_per_chunk, tolerance, hosts):
    ''' Create L2 data (at level LEVEL) from L1 data for the given OBS_IDS'''
    dh = datahandler.DataHandler.from_file(config)
    assert 'L1' in dh.get_levels(), f'L1 data level needs to be defined'
    assert level in dh.get_levels(), f'{level} data level needs to be defined'

    env_file = os.path.expanduser(env_file)
    if not os.path.exists(env_file):
        env_file = None

    if hosts is None:
        hosts = dh.get_all_hosts()
    else:
        hosts = worker.get_hosts(hosts)

    w = worker.WorkerPool(hosts, name='L1 to L2', max_tasks_per_worker=max_concurrent,
                          debug=dry_run, dry_run=dry_run, env_source_file=env_file)

    obs_ids, sws = dh.get_obs_ids_and_spectral_windows(obs_ids)

    for obs_id in obs_ids:
        for sw in sws:
            msins_list = dh.get_ms_path(obs_id, l1_level, sw)
            msins = ','.join(msins_list)
            spec_ms_process = []

            if dh.is_n2_obs_id(obs_id) and l1_level.upper().startswith('L2'):
                # Assign nodes in a round-robin fashion
                nodes = dh.get_n2_nodes(obs_id)
                nodes_cycle = itertools.cycle(nodes)
                n = len(msins_list)
                nodes_list = [next(nodes_cycle) for _ in range(n)]
                msouts = [msin.replace(l1_level, level) for msin in msins_list]

                spec_ms_process = zip(nodes_list, msins_list, msouts, [0] * n, [0] * n)
            elif dh.is_n2_obs_id(obs_id):
                ms_info = msutils.get_info_from_ms_files(msins_list)
                nodes = dh.get_n2_nodes(obs_id)

                total_time = ms_info['end_time'] - ms_info['start_time']
                int_time = ms_info['int_time']
                n_slots = int(total_time // int_time)

                # Calculate number of full chunks and remainder
                n_full_chunks = n_slots // n_slots_per_chunk
                remainder_slots = n_slots % n_slots_per_chunk

                # Decide whether to merge remainder with last chunk
                if remainder_slots < tolerance * n_slots_per_chunk:
                    # Merge remainder with last chunk
                    ntimes_list = [n_slots_per_chunk] * (n_full_chunks - 1)
                    ntimes_list.append(n_slots_per_chunk + remainder_slots)
                else:
                    # Keep remainder as a separate chunk
                    ntimes_list = [n_slots_per_chunk] * n_full_chunks
                    if remainder_slots > 0:
                        ntimes_list.append(remainder_slots)

                n_chunks = len(ntimes_list)

                # Build starttimeslots
                starttimeslots = [0]
                for ntimes in ntimes_list[:-1]:
                    starttimeslots.append(starttimeslots[-1] + ntimes)

                # Assign nodes in a round-robin fashion
                nodes_cycle = itertools.cycle(nodes)
                nodes_list = [next(nodes_cycle) for _ in range(n_chunks)]

                # Generate output MS paths for each chunk
                msout_list = [f'{dh.get_dir_path(obs_id, level, sw, node)}/{sw}_T{i:03}.MS' for i, node in enumerate(nodes_list)]

                # Prepare processing taskss
                spec_ms_process = zip(nodes_list, [msins] * n_chunks, msout_list, starttimeslots, ntimes_list)
            else:
                msout = dh.get_ms_path(obs_id, level, sw)[0]
                node = dh.get_node(obs_id, sw)
                spec_ms_process.append((node, msins, msout, 0, 0))

            for node, msins, msout, starttimeslot, ntimes in spec_ms_process:
                target, msout_name = os.path.split(msout)

                if os.path.exists(msout):
                    if force:
                        print(f'Warning: {msout} already exists')
                    else:
                        print(f'Error: {msout} already exists')
                        return 1

                os.makedirs(target, exist_ok=True)
                os.makedirs(f'{target}/logs', exist_ok=True)

                for i in range(1000):
                    log_file = f'{target}/logs/l2_to_l1_{msout_name}_{i}.log'
                    if not os.path.exists(log_file):
                        break

                dppp_file, modified_lines = dh.get_l1_to_l2_config(level, obs_id)

                # Create DP3 command
                cmd = f'DP3 {os.path.abspath(dppp_file)} msin=[{msins}] msout={msout} msout.overwrite=true'

                # Add modified lines to the command
                for modified_line in modified_lines:
                    cmd += f' {modified_line.strip()}'

                if starttimeslot != 0 or ntimes != 0:
                    cmd += f' msin.starttimeslot={int(starttimeslot)} msin.ntimes={int(ntimes)}'

                w.add(cmd, run_on_host=node, output_file=log_file)

    w.execute()


@main.command('make_ms_list')
@click.argument('level', type=str)
@click.argument('obs_ids', type=str)
@click.option('--config', '-c', 'config', help='Data handler configuration file', type=t_file, default='data_handler.toml')
@click.option('--target', help='Target directory', default='ms_lists')
@click.option('--column', '-C', is_flag=True, help='Write one MS per line (column format)')
@click.option('--min_alt', type=float, default=None, help='Minimum mean elevation in degrees. Only MS with mean altitude ≥ this value.')
def make_ms_list(level, obs_ids, config, target, column, min_alt):
    '''Make MS list for all OBS_IDS at level LEVEL'''
    dh = datahandler.DataHandler.from_file(config)
    assert level in dh.get_levels(), f'{level} data level needs to be defined'

    if not os.path.exists(target):
        os.makedirs(target)

    obs_ids, sws = dh.get_obs_ids_and_spectral_windows(obs_ids)

    for obs_id in obs_ids:
        for sw in sws:
            ms_paths = dh.get_ms_path(obs_id, level, sw)
            filepath = os.path.join(target, f'{obs_id}_{level}_{sw}')

            if min_alt is not None:
                kept = []
                for ms in ms_paths:
                    mean_alt = msutils.get_mean_altitude_for_ms(ms, msutils.nenufar_location)
                    if mean_alt >= min_alt:
                        kept.append(ms)
                print(f'{obs_id} {sw}: {len(kept)}/{len(ms_paths)} MS with altitude >= {min_alt}')
                ms_paths = kept

            if not ms_paths:
                print(f'Warning: No MS for {obs_id} {sw}. No file created')
                continue

            with open(filepath, 'w') as f:
                if column:
                    for ms in ms_paths:
                        f.write(f'{ms}\n')
                else:
                    f.write(' '.join(ms_paths) + '\n')
                print(f'{obs_id} {sw}: {filepath} created')
