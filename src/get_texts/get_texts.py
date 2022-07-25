#!python3
import sys, click
import sqlite3, csv, os, colorama
from colorama import Fore

def logo():
    print(r"""
               __     __            __      
   ____ ____  / /_   / /____  _  __/ /______
  / __ `/ _ \/ __/  / __/ _ \| |/_/ __/ ___/
 / /_/ /  __/ /_   / /_/  __/>  </ /_(__  ) 
 \__, /\___/\__/   \__/\___/_/|_|\__/____/  
/____/                                      
    """)

def get_backup(backup):
    if backup:
        print("Backup feature not implemented!")
        sys.exit(0)

def get_db_conn(db_path):
    try:
        return sqlite3.connect(db_path + '/3d/3d0d7e5fb2ce288813306e4d4636395e047a3d28')
    except sqlite3.OperationalError:
        print("invalid input")
        pass

def get_output(output):
    if 'csv' in output:
        return csv.writer(open(output, "w"))

def transphorm_num(phone):
    if (len(phone) < 11):
        return '1' + phone
    else:
        return phone

def query(msg_conn, phone_num):
    return msg_conn.execute(f"""select m.text, datetime(round(m.date/1000000000) + 978307200, 'unixepoch','localtime'), h.id, m.is_from_me
    from message m
    join handle h on h.ROWID = m.handle_id
    and h.id = :phone_num

    join chat_message_join cmj on cmj.message_id = m.ROWID
    left join chat_handle_join chj on chj.chat_id = cmj.chat_id
    -- in chj, 1 chat_id corresponds to 1-many handle_id
    left join handle gh on gh.ROWID = chj.handle_id

    group by m.ROWID
    having count(gh.id) <= 1

    order by m.date;""", {"phone_num":"+" + phone_num})

def group_query(msg_conn, phone_num):
    return msg_conn.execute(f"""select m.text, datetime(round(m.date/1000000000) + 978307200, 'unixepoch','localtime')
    from message m
    join handle h on h.ROWID = m.handle_id
    and h.id = :phone_num

    join chat_message_join cmj on cmj.message_id = m.ROWID
    left join chat_handle_join chj on chj.chat_id = cmj.chat_id
    left join handle gh on gh.ROWID = chj.handle_id

    group by m.ROWID
    having count(gh.id) > 1

    order by m.date;""", {"phone_num":"+" + phone_num})
 
@click.command()
@click.option('--backup','-b', is_flag=True, show_default=True, default=False, help='create backup NOT IMPLEMENTED')
@click.option('--input','-i','db_path', type=click.Path(resolve_path=True), default='%USERPROFILE%/AppData/Roaming/iTunes/Backup/', help='location of iTunes backup' )
@click.option('--output','-o', default='texts.csv', type=click.Path(exists = False, resolve_path=True), help='file to write to' )
@click.option('--phone','-p', default='12345678910', help='phone number to query')
@click.option('--group','-g', is_flag=True, show_default=True, default=False, help='ouput group messages')
def get_texts(backup, db_path, output, phone, group):
    logo()
    get_backup(backup)
    msg_conn = get_db_conn(db_path)
    csvWriter = get_output(output)
    phone_num = transphorm_num(phone)

    count = 0
    if group == False:
        cursor = query(msg_conn, phone_num)
        for row in cursor:
            print(Fore.WHITE + str(row) if row[-1] == 0 else Fore.BLUE + str(row).rjust(os.get_terminal_size()[0] - 5) )
            csvWriter.writerow(row)
            count = count + 1
    else:
        cursor = group_query(msg_conn, phone_num)
        for row in group_cursor:
            print(str(row))
            csvWriter.writerow(row)
            count = count + 1

    print(f'Displayed {count} messages.')

get_texts()
