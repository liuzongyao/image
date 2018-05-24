#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:zongyao liu
# Date 2018.4.24
import json
import os
import csv


class Results:

    def __init__(self):

        self._file_path = os.path.dirname(__file__)
        self.results = []

    def update_check_point(self, case_name, check_name, is_blocked, check_result, message):
        temp_template = self._file_path + '/../test_case/test_case_result.json'
        response = json.load(open(temp_template))
        check_point = {'check_name': check_name, 'is_blocked': is_blocked, 'check_result': check_result, 'message': message}
        new_check = {'case_name': case_name, 'check_point': [check_point]}
        response.update(new_check)
        with open(temp_template, 'w') as f:
            json.dump(response, f, indent=2)
            f.close()
        if len(self.results) == 0:
            self.results.append(response)
            assert not response['check_point'][0]['is_blocked']
        else:
            if self.results[-1]['case_name'] == response['case_name']:  # 此处说明是同一个case的不同check point
                self.results[-1]['check_point'].append(check_point)
                assert not response['check_point'][-1]['is_blocked']
            else:
                self.results.append(response)
                assert not response['check_point'][-1]['is_blocked']

    def update_results(self):

        csv_report = self._file_path + '/../report/results.csv'
        with open(csv_report, 'w') as csvfile:
            fieldnames = ['case_name', 'check_name', 'check_result', 'is_blocked', 'message']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in range(len(self.results)):
                for j in range(len(self.results[i]['check_point'])):
                    m = self.results[i]
                    n = self.results[i]['check_point'][j]
                    writer.writerow({'case_name': m['case_name'], 'check_name': n['check_name'], 'check_result': n['check_result'], 'is_blocked': n['is_blocked'], 'message': n['message']})


result = Results()


