from subprocess import Popen, PIPE, STDOUT
import numpy as np
import matplotlib.pyplot as plt
import re
import csv


def call_callgrind(exec_args:list):

    args = [
        'valgrind', '--tool=callgrind',
        '--collect-atstart=no',
        '--dump-after=RunTask*',
        '--combine-dumps=yes', '--callgrind-out-file=/dev/stdout',
        '--toggle-collect=RunTask()',
    ]

    print(f"callgrinding program: {exec_args}")
    args.extend(exec_args)
    Irs = list()
    with Popen(args, stdout=PIPE, stderr=STDOUT, text=True) as proc:
        for line in proc.stdout:
            if line.startswith("summary:"):
                Irs.append(int(line.split(":")[1].strip()))
    return {
        'Irs':Irs,
        'args': args
    }


def calc_statistics(profile:dict):
        Irs = np.array(profile['Irs'])
        min_idx = np.argmin(Irs[:-1]) # last cycle 0?
        max_idx = np.argmax(Irs)
        profile.update({
            'min_idx': min_idx,
            'min': Irs[min_idx],
            'max_idx': max_idx,
            'max': Irs[max_idx]
        }
        )

def slugify(exec_args:list):
    text = '_'.join(exec_args)
    value = re.sub(r'[^\w\s-]', '_', text)
    value = re.sub('[-\s]+', '-', value)

    return value


def plot_instructions(profile):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(np.array(profile['Irs']), linewidth=1)
    # mark maximum
    ax.axvline(profile['max_idx'], color="r", linewidth=1, linestyle=":")
    ax.axhline(profile['max'], color="r", linewidth=1, linestyle=":")
    ax.plot([profile['max_idx']], [profile['max']], 'o')

    ax.set(xlabel='cycle', ylabel='number of instructions', title=profile['slug'])
    ax.grid()

    fig.savefig(f"{profile['slug']}.png", dpi=150)
    # plt.show()


if __name__ == "__main__":

    # hardcoded programs and their arguments
    PROGRAMS = [
        ['build/host_r5f/bin/main', 'arguments',],
    ]

    # collected results, list of dicts
    profiles = list()

    # profile with callgrind, calc some statistics and plot result
    for exec_args in PROGRAMS:
        profile = call_callgrind(exec_args)
        profile.update({'slug': slugify(exec_args)})
        calc_statistics(profile)
        plot_instructions(profile)

        profiles.append(profile)

    # print to a file
    with open('callgrind_statistics.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for profile in profiles:
            writer.writerow(profile.values())

