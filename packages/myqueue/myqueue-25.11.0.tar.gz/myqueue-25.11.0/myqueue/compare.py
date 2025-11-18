from myqueue.config import Configuration
from myqueue.queue import Queue
from myqueue.selection import Selection
from myqueue.states import State
from pathlib import Path
import sys
import os


def main(path1: Path, path2: Path) -> None:
    trees = []
    for path in [path1, path2]:
        print(path)
        path = path.resolve()
        os.chdir(path)
        config = Configuration.read(path)
        selection = Selection(states={State.done}, folders=[path])
        with Queue(config, need_lock=True) as queue:
            tasks = queue.select(selection)
        trees.append({str(t.dname.relative_to(path)): t.running_time()
                      for t in tasks})
    tree1, tree2 = trees
    T = 0.0
    dT = 0.0
    xnames = [(t / tree1[name], name)
              for name, t in tree2.items()
              if name in tree1 and tree1[name] != 0.0]
    xnames.sort()
    n = max(len(name) for _, name in xnames)
    for _, name in xnames:
        t1 = tree1[name]
        print(f'{name:{n}} {t1:10.0f}', end='')
        t2 = tree2[name]
        T += t1
        dT += t2 - t1
        x = (t2 / t1 - 1) * 100
        print(f' {t2:10.0f} {x:+6.1f} %')
    print(f'{T:.1f} sec, {dT:+.1f} sec, {dT / T * 100:+.1f} %')
    print(f'Missing in {path2}:')
    for name in tree1:
        if name not in tree2:
            print(name)
    print(f'Extra in {path2}:')
    for name in tree2:
        if name not in tree1:
            print(name)


if __name__ == '__main__':
    main(*(Path(arg) for arg in sys.argv[1:]))
