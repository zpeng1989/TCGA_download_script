# -*- coding:utf-8 -*-
'''
该工具有两个主要参数，
-m   manifest文本文件路径.
-s   是要保存下载文件的位置(最好为下载的数据创建一个新文件夹)
程序中断后，可以重新启动，程序将在最后下载文件后下载文件。注意，此下载工具将过去文件夹格式的文件直接转换为txt文件。文件名是原始TCGA中文件的UUID。如有必要，按ctrl+c终止程序。
'''

import os
import pandas as pd
import requests
import sys
import argparse
import signal

print(__doc__)

requests.packages.urllib3.disable_warnings()


def download(url, file_path):
    r = requests.get(url, stream=True, verify=False)
    total_size = int(r.headers['content-length'])
    # print(total_size)
    temp_size = 0

    with open(file_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % ('#' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
    print()


def get_UUID_list(manifest_path):
    UUID_list = pd.read_table(manifest_path, sep='\t', encoding='utf-8')['id']
    UUID_list = list(UUID_list)
    return UUID_list


def get_last_UUID(file_path):
    dir_list = os.listdir(file_path)
    if not dir_list:
        return
    else:
        dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(file_path, x)))

        return dir_list[-1][:-4]


def get_lastUUID_index(UUID_list, last_UUID):
    for i, UUID in enumerate(UUID_list):
        if UUID == last_UUID:
            return i
    return 0


def quit(signum, frame):
    # Ctrl+C quit
    print('You choose to stop me.')
    exit()
    print()


if __name__ == '__main__':

    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--manifest", dest="M", type=str, default="gdc_manifest.txt",
                        help="gdc_manifest.txt file path")
    parser.add_argument("-s", "--save", dest="S", type=str, default=os.curdir,
                        help="Which folder is the download file saved to?")
    args = parser.parse_args()

    link = r'https://api.gdc.cancer.gov/data/'

    # args
    manifest_path = args.M
    save_path = args.S

    print("Save file to {}".format(save_path))

    UUID_list = get_UUID_list(manifest_path)
    last_UUID = get_last_UUID(save_path)
    print("Last download file {}".format(last_UUID))
    last_UUID_index = get_lastUUID_index(UUID_list, last_UUID)

    for UUID in UUID_list[last_UUID_index:]:
        url = os.path.join(link, UUID)
        file_path = os.path.join(save_path, UUID + '.svs')
        download(url, file_path)
        print('%s have been downloaded'%UUID)
