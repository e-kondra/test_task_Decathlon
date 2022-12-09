import csv
import json
from abc import ABC, abstractmethod


class Calculation:
    def __init__(self):
        self.calc_dict, self.events = self.get_calc_data_csv()
        self.input_dict = self.get_input_data_csv()
        self.out_list = []
        self.deep = 0

    def get_calc_data_csv(self):
        with open("calc.csv", encoding='utf-8-sig') as file:
            file_reader = csv.reader(file, delimiter=";")
            calc_data = {}
            events = []
            titles = ['a', 'b', 'c']
            for row in file_reader:
                i = 0
                variables = {}
                for i in range(len(row) - 1):
                    variables[titles[i]] = float(row[i + 1])
                variables['type'] = 'Track' if (row[0].find(' m') > 0) else 'Field'
                calc_data[row[0]] = variables
                events.append(row[0])
            return calc_data, events

    def get_input_data_csv(self):
        with open("Decathlon.csv", encoding='utf-8') as input_file:
            file_reader = csv.reader(input_file, delimiter=";")
            inp_data = {}
            for row in file_reader:
                index = 0
                rates = {}
                for index in range(len(row)-1):
                    rates[self.events[index]] = row[index + 1]
                inp_data[row[0]] = rates
            return inp_data

    def calc_points(self):
        for man, val in self.input_dict.items():
            rates = val
            summa = 0
            for event, rate in rates.items():
                point = Event.get_event(self.calc_dict[event]['type'])
                num = point.calc_points(event, rate, self.calc_dict)
                summa += num
            rates['points'] = summa
        # print(self.input_dict)

    def create_out_list(self):
        for man, val in self.input_dict.items():
            rates = val
            out_sm_list = []
            out_sm_list.append(man)
            for event, rate in rates.items():
                out_sm_list.append(rate)
            self.out_list.append(out_sm_list)
        self.out_list = sorted(self.out_list, key=lambda rate: rate[11], reverse=True)
        # print(self.out_list)
        self.set_places()

    def recurs_place(self, i):
        while i <= len(self.out_list):
            if i < len(self.out_list):
                if self.out_list[i-1][-2] == self.out_list[i][-2]:
                    self.deep += 1
                    return f'{i}-' + self.recurs_place(i+1)
                if self.out_list[i-1][-2] > self.out_list[i][-2]:
                    return str(i)
            else:
                return str(i)

    def set_places(self):
        for i, res in enumerate(self.out_list, start=1):
            res.append(i)
        self.deep = 1
        for index, res in enumerate(self.out_list, start=1):
            if self.deep == 1:
                res.insert(0, self.recurs_place(index))
            else:
                self.deep -= 1
                res.insert(0, self.out_list[index-2][0])
        for res in self.out_list:
            res.pop()
            res.insert(1, res.pop())
        # print(self.out_list)

    def output_json_file(self):
        with open('Result.json', 'w', encoding='utf-8', ) as f:
            json.dump(self.out_list, f, indent=0)


class Event(ABC):
    @abstractmethod
    def calc_points(self, event, rate, calc_dict):
        pass

    @staticmethod
    def get_event(type_event):
        EVENT_TYPE = {
            'Field': FieldEvent,
            'Track': TrackEvent
        }
        return EVENT_TYPE[type_event]()

    @staticmethod
    def get_float(string):
        if len(string.split('.')) == 3:
            m, s, mm = string.split('.')
            return int(m) * 60 + float(str(s + '.' + mm))
        return float(string)


class TrackEvent(Event):
    # return number of points by event and rate
    def calc_points(self, event, rate, calc_dict):
        # Points = INT(A(B — P)C) for track events(faster time produces a higher score)
        points = int(calc_dict[event]['a'] * (calc_dict[event]['b'] - self.get_float(rate)) ** calc_dict[event]['c'])
        return points


class FieldEvent(Event):
    # return number of points by event and rate
    def calc_points(self, event, rate, calc_dict):
        rate = self.get_float(rate) * 100 if ((event.find('jump') > 0) or (event.find('vault') > 0)) else self.get_float(rate)
        # Points = INT(A(P — B)C) for field events(greater distance or height produces a higher score)
        points = int(calc_dict[event]['a'] * (rate - calc_dict[event]['b']) ** calc_dict[event]['c'])
        return points


if __name__ == '__main__':
    calculation = Calculation()
    calculation.calc_points()
    calculation.create_out_list()
    calculation.output_json_file()



