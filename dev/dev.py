#!/usr/bin/env python3

import configparser
import csv
import json
import os.path
import time
from datetime import datetime, timezone
from pathlib import Path

import click
import hentai
from hentai import Hentai
from pythonping import ping
import matplotlib.pyplot as plt
import pandas as pd

from speedtest import Speedtest

id = None

def print_version(ctx, param, value):
    config = configparser.RawConfigParser()
    config.read("setup.cfg")
    
    if not value or ctx.resilient_parsing:
        return

    click.secho(f"\nPython Hentai API Wrapper Version {hentai.__version__} (Dev Tools)", fg = 'yellow')
    click.echo(f"Copyright (C) {datetime.today().year} {config.get('metadata', 'author')}\n")
    click.echo("License GPLv3: GNU GPL version 3 <https://gnu.org/licenses/gpl.html>")
    click.echo("This is free software: you are free to change and redistribute it.")
    click.echo("There is NO WARRANTY, to the extent permitted by law.\n")
    ctx.exit()

@click.group()
@click.option('--version', is_flag = True, callback = print_version, expose_value = False, is_eager = True, help = "Display package version information.")
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    ctx.obj['FILENAME'] = Path("./data/ids.csv")

@cli.command()
@click.option('--threads', type=click.INT, default=None, help="Set number of threads for this speed test.")
@click.option('--ping-target', type=click.STRING, default='www.google.com', help="Set server as ping target.")
@click.option('--save/--no-save', is_flag=True, default=False, help="Store speedtest result as file to disk.")
@click.option('--plot/--no-plot', is_flag=True, default=False, help="Plot speedtest from existing test results.")
@click.pass_context
def speedtest(ctx, threads, ping_target, save, plot):
    filename = Path(os.path.expanduser("~/Desktop")).joinpath('speedtest.json')

    if plot:
        data = pd.read_json(filename)
        df = pd.DataFrame(data)
        df.epos = [datetime.fromtimestamp(x).strftime("%d.%m %H:%M %p") for x in df.epos]

        ax = plt.gca()   
        ax.set_xlabel("Date")
        ax.set_ylabel("MB/s")
        ax.set_title(f"ISP: {df.isp[0]} ({df.country[0]})")       

        df.plot(kind='line', x='epos', y='download', color='red', ax=ax, grid=True)
        df.plot(kind='line', x='epos', y='upload', color='blue', ax=ax, grid=True)    

        plt.margins(0,0)
        plt.ylim(ymin=0, ymax=12)
        plt.xticks(rotation=45)
        plt.legend(['Downstream', 'Upstream'])
        plt.show()
        return

    click.echo("Initialize speed test . . .\n")
    test = Speedtest()    
    test.get_servers()
    test.get_best_server()
    test.download(threads=threads)
    test.upload(threads=threads)
    res_ping = ping(ping_target)

    test_result = test.results.dict()
    now = datetime.now(tz=timezone.utc)

    session = {
            'epos' : round(now.replace(tzinfo=timezone.utc).timestamp()), 
            'isp' : test_result['client']['isp'],
            'ip' : test_result['client']['ip'],
            'country' : test_result['client']['country'],
            'ping_target' : ping_target,
            'threads' : threads,
            'min_ping' : res_ping.rtt_min_ms, 
            'avg_ping' : res_ping.rtt_avg_ms,
            'max_ping' : res_ping.rtt_max_ms,
            'server_url' : test_result['server']['url'],
            'download' : int(test_result['download'])/1_000_000,
            'upload' : int(test_result['upload'])/1_000_000
    }
    
    click.secho(f"{28*'='}\n", fg='green')
    click.secho(f"{now.strftime('%H:%M %p').rjust(18, ' ')}\n", fg='yellow')

    # ping
    click.secho(f"Ping ({ping_target})")
    click.secho("Min\t\t", nl=False, fg='yellow')
    click.secho(f"{res_ping.rtt_min_ms:.2f} ms")
    click.secho("Avg\t\t", nl=False, fg='yellow')
    click.secho(f"{res_ping.rtt_avg_ms:.2f} ms")
    click.secho("Max\t\t", nl=False, fg='yellow')
    click.secho(f"{res_ping.rtt_max_ms:.2f} ms\n")
    
    # bandwidth
    click.secho(f"{session['isp']} ({session['country']})")
    click.secho("IP\t\t", nl=False, fg='yellow')
    click.secho(f"{session['ip']}")
    click.secho("Download\t", nl=False, fg='yellow')
    click.secho(f"{session['download']:.2f} MB/s")
    click.secho("Upload\t\t", nl=False, fg='yellow')
    click.secho(f"{session['upload']:.2f} MB/s\n")

    click.secho(f"{28*'='}\n", fg='green')

    if save:
        data = []
        
        if os.path.isfile(filename) is False:
            filename.touch()
            data.append(session)            
            with open(filename, mode='w', encoding='utf-8') as file_handler:
                json.dump(data, file_handler)
        else:
            with open(filename, mode='r', encoding='utf-8') as file_handler:
                data = json.load(file_handler)
                data.append(session)
            with open(filename, mode='w', encoding='utf-8') as file_handler:
                json.dump(data, file_handler)

        click.echo(f"Stored test results to '{filename}'.\n")
    
    ctx.exit()

@cli.command()
@click.option('--delay', type=click.INT, default=0, help="Set delay between GET requests in seconds.")
@click.option('--delete-duplicates', is_flag=True, default=False, help="Remove duplicate IDs from source file.")
@click.pass_context
def update_ids(ctx, delay, delete_duplicates):
    global id
    filename = ctx.obj['FILENAME']
    is_file = os.path.isfile(filename)

    if is_file is False:
        click.secho("Warning: file not found. Creating a new CSV file as replacement now.", fg='yellow')
        Path(filename).touch()

    if delete_duplicates:
        tmp_filename = './data/tmp.csv'
        with open(filename, mode='r') as in_file, open(tmp_filename, mode='w') as out_file:
            unique_ids = set()
            for line in in_file:
                if line in unique_ids: 
                    click.secho(f"Duplicate detected: id={line}", fg='yellow')
                    continue
                unique_ids.add(line)
                out_file.write(line)
        Path(tmp_filename).replace(filename)        
        return

    with open(filename, mode='r', encoding='cp932') as file_handler:
        reader = csv.reader(file_handler)
        id = [int(row[0]) for row in reader][-1] if is_file is True else 0

    with open(filename, mode='a+', newline='', encoding='cp932', errors='replace') as file_handler:
        for i in range(id+1, 400_000):
            try: 
                if Hentai.exists(i):
                    writer = csv.writer(file_handler)
                    click.echo(f"{str(i).zfill(6)}: Adding id={i} to file . . .")
                    writer.writerow([i])
                    time.sleep(delay)
                else:
                    click.echo(f"{str(i).zfill(6)}: ", nl=False)
                    click.secho("Does Not Exist", fg='yellow')
            except Exception:
                click.secho("The read operation timed out.", fg='red')


if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        pass
