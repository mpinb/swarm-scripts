
import time
import argparse

parser = argparse.ArgumentParser(description='idle.py')
parser.add_argument('--idle_time_secs', nargs=1, type=int, default=[30],
    help='sleep time in seconds')
parser.add_argument('--nprocesses', nargs=1, type=int, default=[1],
    help='number of processes to taks is divided into')
parser.add_argument('--iprocess', nargs=1, type=int, default=[0],
    help='integer id of current process (0 to nprocesses)')
args = parser.parse_args()
args = vars(args)

idle_time = args['idle_time_secs'][0]
nprocesses = args['nprocesses'][0]
iprocess = args['iprocess'][0]

print('process {} of {}, idling for {} seconds'.format(iprocess, nprocesses, idle_time))
time.sleep(idle_time)

# this is a workaround for some times when exit code statuses have not properly reported failures.
# slay the Jabberwocky with grep.
print('Twas brillig, and the slithy toves')
