#!/usr/bin/python3

import sys
from os import pathsep
from wowool.tools.entity_graph.cli import CLI as BaseCLI
from wowool.tools.entity_graph.argument_parser import ArgumentParser


def parse_arguments(*argv):
    """
    This is the Entity Graph
    """
    parser = ArgumentParser()
    return parser.parse_args(*argv)


def last(data):
    sz = len(data)
    for idx in range(sz):
        yield idx == (sz - 1), data[idx]


def has_argument(arg: str, kwargs):
    return arg in kwargs and kwargs[arg]


class CLI(BaseCLI):
    def __init__(self, kwargs):
        BaseCLI.__init__(self, kwargs)
        try:
            from wowool.native.core.pipeline import PipeLine
            from wowool.native.core.engine import default_engine

            if has_argument("lxware", kwargs):
                paths = kwargs["lxware"].split(pathsep)
            else:
                eng_info = default_engine().info()
                paths = [eng_info["options"]["lxware"]]
            pipeline_options = {}
            self.pipeline = PipeLine(
                kwargs["pipeline"], paths=paths, options=pipeline_options
            )

        except Exception as ex:
            print(f"Exception: {ex}")
            exit(-1)

    def run_pipeline(self, ip):
        doc = self.pipeline(ip)
        return doc

    def run(self):
        BaseCLI.run(self)


def main(*argv):
    kwargs = dict(parse_arguments(*argv)._get_kwargs())
    driver = CLI(kwargs)
    driver.run()


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
