"""
A one cli for all the anime.
"""

import shutil
import os
import click
from rich import print
from core.cli.commands import download, stream, continuation, grab, schedule
from core.config import player_executable
from time import sleep

VER = '1.2.2'

def _vlc_exists():
    if os.path.exists('C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe'):
        return True , 'C:\\Program Files (x86)\\VideoLAN\\VLC\\' 
    elif os.path.exists('C:\\Program Files\\VideoLAN\\VLC\\vlc.exe'):
        return True ,'C:\\Program Files\\VideoLAN\\VLC\\'
    else:
        return False ,''

vlc_exists , executable_path = _vlc_exists()

'''
A temp powershell script to add vlc to Path_HKLM system variable
'''        
add_to_path_snippet = f"""
$new_entry = '{executable_path}'
$search_pattern = ';' + $new_entry.Replace("\\","\\\\")

$old_path = [Environment]::GetEnvironmentVariable('path', 'machine');
$replace_string = ''
$without_entry_path = $old_path -replace $search_pattern, $replace_string
$new_path = $without_entry_path + ';' + $new_entry
[Environment]::SetEnvironmentVariable('path', $new_path,'Machine');
"""

banner = f"""

░█████╗░███╗░░██╗██╗███╗░░░███╗██████╗░██╗░░░░░
██╔══██╗████╗░██║██║████╗░████║██╔══██╗██║░░░░░
███████║██╔██╗██║██║██╔████╔██║██║░░██║██║░░░░░
██╔══██║██║╚████║██║██║╚██╔╝██║██║░░██║██║░░░░░
██║░░██║██║░╚███║██║██║░╚═╝░██║██████╔╝███████╗
╚═╝░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░░░░╚═╝╚═════╝░╚══════╝v{VER}
A highly efficient anime downloader and streamer
"""
sleep(0.2)
commands = {
    'download': download.animdl_download,
    'continue': continuation.animdl_continue,
    'grab': grab.animdl_grab,
    'schedule': schedule.animdl_schedule
}

executable = bool(shutil.which(player_executable))

if executable:
    commands.update({'stream': stream.animdl_stream})

elif os.name == 'nt' and vlc_exists and "VideoLAN\\VLC" not in os.environ["Path_HKLM"]:
    
    with open('C:\\sys_path_bak.txt','w') as write_path_backup:
        write_path_backup.write(os.environ["PATH"])
    
    with open('add_to_path_temp.ps1','w') as write_add_to_path_script:
        write_add_to_path_script.write(add_to_path_snippet)
    try:
        os.system('powershell.exe -executionpolicy remotesigned -File "add_to_path_temp.ps1"') #subprocess doesn't seem to work here,i think its bcz the list is not being interpreted correclty
        os.remove('add_to_path_temp.ps1')
    except Exception as err:
        print(f"[red]Error:Couldn't Set-up the PATH,in case your PATH is broken there is a backup present in C:\\sys_path_bak.txt\nErrorMessage:{err}[/red]") 
        sleep(1.3)
    commands.update({'stream': stream.animdl_stream})
	

@click.group(commands=commands)
def __animdl_cli__():
    pass
if __name__  == '__main__':
    print(f"[purple]{banner}[/purple]")
    __animdl_cli__()

