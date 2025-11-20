#!/usr/bin/env python3
import sys, os, psutil, subprocess, argparse, time

parser = argparse.ArgumentParser()
# parser.add_argument(
#     'commands', nargs='+', type=str,
#     help='command to be executed')
parser.add_argument("--max_memory", type=float, default=1e9)
parser.add_argument("--mem_step", type=float, default=1e4)
parser.add_argument("--wait_step", type=float, default=1)
parser.add_argument("--use_shell", type=bool, default=False)
parser.add_argument("--pid", type=int, default=0, help='if no args, an external PID will be monitored')

args = sys.argv[1:]
options = []
for _ in args:
    if not _.startswith('-'):
        break
    options.append(args.pop(0))

options = parser.parse_args(options)

t0 = time.time()
#args = options.commands
if options.use_shell:
    args = ' '.join(args)

if args:
    print(args)
    po = subprocess.Popen(args, shell=options.use_shell)
    pid = po.pid
else:
    po = None
    pid = options.pid

print('pid: {}'.format(pid))

mem = []
while True:
    mem.append(psutil.Process(pid).memory_info().rss) #.vms
    if (len(mem)==1 or (mem[-1]-mem[0]) > options.mem_step
        or mem[-1] > options.max_memory):
        print('mem_usage: {}'.format(mem[-1]))

    if mem[-1] > options.max_memory:
        print('kill {}'.format(pid))
        if po:
            po.kill()
        else:
            os.system('kill {}'.format(pid))

    try:
        if po:
            po.wait(options.wait_step)
        else:
            time.sleep(options.wait_step)
        break
    except subprocess.TimeoutExpired:
        mem = mem[-1:]

tf = time.time() - t0
print('ellapsed {} seconds'.format(tf))
