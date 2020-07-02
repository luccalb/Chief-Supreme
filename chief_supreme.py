#!/usr/bin/env python

""" chief_supreme.py
A hybrid bot for https://www.supremenewyork.com/shop (EU).

The bots workflow can be divided into 3 stages:
Stage 1: Drop detection and size/style ID gathering (request based)
Stage 2: ATC procedure                              (browser based)
Stage 3: Checkout                                   (request based)
"""

import services.firebase_service as fb_service
import services.task_service as task_manager

import multiprocessing as mp

results = []


def collect_prey(result):
    global results
    results.append(result)


def main():
    # get desired items and personal data from firebase
    cop_list = fb_service.get_coplist()
    raw_identities = fb_service.get_identities()

    # create the tasks to run
    task_list = task_manager.gen_tasklist(cop_list, raw_identities)

    print(f'Created {len(task_list)} tasks!')

    # launch the task runners
    pool = mp.Pool(mp.cpu_count())
    for i, task in enumerate(task_list):
        pool.apply_async(task_manager.run_task, args=(i, task), callback=collect_prey)

    pool.close()
    pool.join()

    print(results)
    print('Avg:', sum(results) / len(results))


if __name__ == '__main__':
    main()
