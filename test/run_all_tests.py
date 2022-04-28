from subprocess import CREATE_NEW_CONSOLE, Popen
import os
import time
import wget

def launch_blazegraph(port:int):
    '''
    Launch Blazegraph triplestore at a given port.
    '''
    Popen(
        ['java', '-server', '-Xmx4g', '-Dcom.bigdata.journal.AbstractJournal.file=./blazegraph.jnl', f'-Djetty.port={port}', '-jar', f'./blazegraph.jar'],
        creationflags=CREATE_NEW_CONSOLE
    )

def main():
    if not os.path.isfile('blazegraph.jnl'):
        url = 'https://github.com/blazegraph/database/releases/download/BLAZEGRAPH_2_1_6_RC/blazegraph.jar'
        wget.download(url=url, out='.')
    launch_blazegraph(9999)
    time.sleep(5)
    Popen(
        ['python', '-m', 'unittest', 'discover', '-s', 'test', '-p', '*test.py', '-b']
    )