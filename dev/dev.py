#!/usr/bin/env python

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
@click.pass_context
def speedtest(ctx, threads, ping_target, save):
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
        filename = Path(os.path.expanduser("~/Desktop")).joinpath('speedtest.json')
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
@click.pass_context
def update_ids(ctx, delay):
    global id
    filename = ctx.obj['FILENAME']
    is_file = os.path.isfile(filename)

    if is_file is False:
        click.secho("Warning: file not found. Creating a new CSV file as replacement now.", fg='yellow')
        Path(filename).touch()

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
