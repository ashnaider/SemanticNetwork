import numpy as np
import os
import re

from dataclasses import dataclass

@dataclass
class Relation:
    id: int
    name: str
    type: int

@dataclass
class ObjRelation:
    lhs_obj_name_id: int
    name_id: int
    rhs_obj_name_id: int



class SemanticNetwork:
    def __init__(self):
        self.NEW_SECTION_REGEX = "^#[0-9]"
        self.SN_objects = dict()
        self.SN_relations = []
        self.SN_obj_relations = []

    def data_from_file(self, filename):
        with open(filename, 'r') as f:
            self.raw_data = f.read()
            print(self.raw_data)

        self.parse_sn_objects(self.raw_data)
        self.parse_relations(self.raw_data)
        self.parse_obj_relations(self.raw_data)

        print(self.SN_objects)
        for x in self.SN_relations:
            print(x)
        for x in self.SN_obj_relations:
            print(x)

    def parse_sn_objects(self, raw_data):
        section = self.get_section(raw_data, 1)
        for line in section.split(os.linesep)[1:]:
            key, val = line.split(':')
            self.SN_objects[key] = val

    def parse_relations(self, raw_data):
        section = self.get_section(raw_data, 2)
        for line in section.split(os.linesep)[1:]:
            rel_id, rel_name, rel_type = line.split(':')
            self.SN_relations.append(Relation(int(rel_id), rel_name, int(rel_type)))

    def parse_obj_relations(self, raw_data):
        section = self.get_section(raw_data, 3)
        for line in section.split(os.linesep)[1:]:
            lhs_obj, rel, rhs_obj = line.split(':')
            self.SN_obj_relations.append(ObjRelation(int(lhs_obj), rel, int(rhs_obj)))

    def get_section(self, raw_data, section_num):
        start_ind = raw_data.find(f'#{section_num}')
        if start_ind == -1:
            raise EOFError(f"Unable to find SN section n.{section_num}!")
        end_ind = raw_data.find(f'#{section_num+1}')
        end_ind = end_ind if end_ind == -1 else end_ind - 1
        return raw_data[start_ind:end_ind]



def main():
    SN = SemanticNetwork()

    filename = os.path.join("data", "test_plane.txt")
    SN.data_from_file(filename)


if __name__ == "__main__":
    main()