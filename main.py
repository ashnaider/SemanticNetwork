import numpy as np
import os
import argparse

from dataclasses import dataclass, astuple

global DEBUG
DEBUG = True

@dataclass
class Relation:
    id: int
    name: str
    type: int

@dataclass
class ObjRelation:
    lhs: int
    rel: int
    rhs: int


class SemanticNetwork:
    def __init__(self):
        self.NEW_SECTION_REGEX = "^#[0-9]"
        self.SN_objects = dict()
        self.SN_relations = []
        self.SN_obj_relations = []

        self.obj_key2ind = dict()
        self.obj_ind2key = dict()

        self.total_m = None

        global DEBUG
        self.debug = DEBUG 

    def rel_id2type(self, rel_id):
        for rel in self.SN_relations:
            if rel.id == rel_id:
                return rel.type

    def rel_id2name(self, rel_id):
        for rel in self.SN_relations:
            if rel.id == rel_id:
                return rel.name

    def data_from_file(self, filename):
        with open(filename, 'r') as f:
            self.raw_data = f.read()
            
            if self.debug:
                print(self.raw_data)

        self.parse_sn_objects(self.raw_data)
        self.parse_relations(self.raw_data)
        self.parse_obj_relations(self.raw_data)

        self.obj_count = len(self.SN_objects)
        self.total_m = np.full(shape=(self.obj_count, self.obj_count), 
                               fill_value=-1)

        # if self.debug:
        #     print(self.SN_objects)
        #     for x in self.SN_relations:
        #         print(x)
        #     for x in self.SN_obj_relations:
        #         print(x)

        for obj in self.SN_obj_relations:
            lhs_ind = self.obj_key2ind[obj.lhs]
            rhs_ind = self.obj_key2ind[obj.rhs]

            self.total_m[lhs_ind, rhs_ind] = obj.rel

        for i in range(self.obj_count):
            self.dfs_for_obj(i, i, np.zeros(shape=(self.obj_count)))

        if self.debug:
            print(self.total_m)

    def dfs_for_obj(self, start_ind, obj_ind, visited):
        visited[obj_ind] = 1

        for j in range(self.obj_count):
            rel = self.total_m[obj_ind, j]
            if rel != -1:
                rel_type = self.rel_id2type(rel)
                if self.rel_is_transitionable(rel_type) and visited[j] == 0:
                    self.total_m[start_ind, j] = self.total_m[obj_ind, j]
                    self.dfs_for_obj(start_ind, j, visited)

    def rel_is_transitionable(self, rel_type):
        return rel_type > 0

    def parse_sn_objects(self, raw_data):
        section = self.get_section(raw_data, 1)
        for i, line in enumerate(section.split(os.linesep)[1:]):
            key, val = [x.strip() for x in line.split(':')]
            key = int(key)
            self.SN_objects[key] = val
            self.obj_key2ind[key] = i
            self.obj_ind2key[i] = key

    def parse_relations(self, raw_data):
        section = self.get_section(raw_data, 2)
        for line in section.split(os.linesep)[1:]:
            rel_id, rel_name, rel_type = [x.strip() for x in line.split(':')]
            self.SN_relations.append(Relation(int(rel_id), rel_name, int(rel_type)))

    def parse_obj_relations(self, raw_data):
        section = self.get_section(raw_data, 3)
        for line in section.split(os.linesep)[1:]:
            lhs_obj, rel, rhs_obj = [x.strip() for x in line.split(':')]
            self.SN_obj_relations.append(ObjRelation(int(lhs_obj), int(rel), int(rhs_obj)))

    def get_section(self, raw_data, section_num):
        start_ind = raw_data.find(f'#{section_num}')
        if start_ind == -1:
            raise EOFError(f"Unable to find SN section n.{section_num}!")
        end_ind = raw_data.find(f'#{section_num+1}')
        end_ind = end_ind if end_ind == -1 else end_ind - 1
        return raw_data[start_ind:end_ind]
    
    def is_unknown(self, obj):
        return obj == '?'

    def get_range(self, obj):
        if self.is_unknown(obj):
            return range(self.obj_count)
        else:
            obj = int(obj)
            obj_ind = self.obj_key2ind[obj]
            return range(obj_ind, obj_ind+1)
        
    def get_rel_range(self, rel):
        if self.is_unknown(rel):
            return range(len(self.SN_relations)+1)
        else:
            rel = int(rel)
            rel_type = self.rel_id2type(rel)
            return range(rel_type, rel_type+1)

    
    def process_query(self, raw_query):
        lhs_obj, rel_id, rhs_obj = [x.strip() for x in raw_query.split(':')]
        
        lhs_range = self.get_range(lhs_obj)
        rhs_range = self.get_range(rhs_obj)
        rel_range = self.get_rel_range(rel_id)
        for i in lhs_range:
            for j in rhs_range:
                rel = self.total_m[i, j]
                if rel in rel_range:
                    print(f"{self.SN_objects[self.obj_ind2key[i]]} -> " \
                          f"{self.rel_id2name(rel)} -> " \
                          f"{self.SN_objects[self.obj_ind2key[j]]}")


def main():
    # fn = "test_plane.txt"
    fn = "test_plane_short.txt"
    SN = SemanticNetwork()

    filename = os.path.join("data", fn)
    SN.data_from_file(filename)

    while True:
        query = input("Enter <?:?:?>: ").strip().lower()
        if query == 'q':
            break
        elif query == '':
            continue
        SN.process_query(query)


if __name__ == "__main__":
    main()