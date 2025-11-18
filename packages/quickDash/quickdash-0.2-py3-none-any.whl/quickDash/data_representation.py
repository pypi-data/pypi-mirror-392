from typing import overload, Union, Optional
from itertools import cycle, islice
import flask

class color:
    r: int
    g: int
    b: int

    @overload
    def __init__(self, r: int, g: int, b: int) -> None:
        self.color = (r, g, b)
    @overload
    def __init__(self, hex: str) -> None: 
        pass

    def __init__(self, r: Union[int, str], g: Optional[int] = None, b: Optional[int] = None) -> None: #type: ignore
        if isinstance(r, str):
            hex_str = r.strip("#")
            if len(hex_str) != 6:
                raise ValueError("Hex string must be 6 characters long (e.g. #RRGGBB)")
            self.r = int(hex_str[0:2], 16)
            self.g = int(hex_str[2:4], 16)
            self.b = int(hex_str[4:6], 16)
        elif g is not None and b is not None:
            self.r = r
            self.g = g
            self.b = b
        else:
            raise TypeError("Color must be initialized with (r, g, b) integers or a (hex) string.")
        
    def __str__(self) -> str:
        return f"rgb({self.r} {self.g} {self.b})"


class coordinates:
    values: list[tuple[int, int]]

    def __init__(self, data_name: str, values: list[tuple[int, int]]) -> None:
        self.data_name = data_name
        self.values = values

    def as_time_graph(self, accents: list[color] = [color(0, 128, 0)], height: int = 500, width: int = 100) -> str:
        #TODO: make time graph
        ...


class data:
    values: list[int | tuple[int, str]]

    def __init__(self, data_name: str, values: list[int | tuple[int, str]]) -> None:
        self.data_name = data_name
        self.values = values

    def add_value(self, value: int | tuple[int, str]):
        self.values.append(value)

    def to_bar_chart(self, accents: list[color] = [color(0, 128, 0)], height: int = 500, width: int = 100) -> str:
        html=""
        maxVal = 0
        accent_cycle = cycle(accents)
        accents_adjusted = list(islice(accent_cycle, len(self.values)))
        for index, value in enumerate(self.values):
            if isinstance(value, tuple):
                if value[0] > maxVal:
                    maxVal = value[0]
                html += f"<div class='bar' style='background-color: {accents_adjusted[index]};' text='{value[1]}'>{"<br>"*value[0]}</div>"
            else:
                if value > maxVal:
                    maxVal = value
                html += f"<div class='bar' style='background-color: {accents_adjusted[index]};' text='{value}'>{"<br>"*value}</div>"
        print(maxVal)
        html = f"<fieldset class='horizontal-bar-chart' style='line-height: {height/maxVal if maxVal > 0 else 30}px; height: {height}; width: calc( {width}% - 10px - 7px - {len(self.values)*2}px );' title='{self.data_name}'><legend>{self.data_name}</legend>{html}</fieldset>"
        return html
    def to_pie_chart(self, accents: list[color] = [color(128, 0, 0), color(0, 128, 0), color(0, 0, 128)], diameter: int = 200) -> str:
        accent_cycle = cycle(accents)
        accents_adjusted = list(islice(accent_cycle, len(self.values)))
        sum_of_values = 0
        for value in self.values:
            if isinstance(value, tuple):
                sum_of_values += value[0]
            else:
                sum_of_values += value
        deg_value = 100/sum_of_values
        prev_values = 0
        gradient = ""
        legend = ""
        for index, value in enumerate(self.values):
            if isinstance(value, tuple):
                prev_values += value[0]
                legend += f"<div style='background-color: {accents_adjusted[index]}; display: inline-block; border-radius: 5px; width: 25px; height: 25px; transform: translateY(6.25px)'></div>  {value[1]} - {value[0]}%<br>"
            else:
                prev_values += value
            gradient += f"{accents_adjusted[index]} 0 {deg_value*prev_values}%, "
        html = f"<fieldset class='pie-chart-wrapper'><legend>{self.data_name}</legend><div class='pie-chart' style='height: {diameter}px; width: {diameter}px; background-image: conic-gradient({gradient.removesuffix(", ")});'></div><br>{legend.removesuffix("<br>")}</fieldset>"
        return html
    
def form(form_id: str, auto_submit: bool = False, **inputs: type) -> str:
    html = f"<hr><form id='{form_id}' method='post' onchange='document.getElementById(\"{form_id if auto_submit else None}\").submit()'>"
    for input in inputs:
        input_type = inputs.get(input)
        value = None
        if input in flask.request.form:
            value = flask.request.form.get(input)
        if input_type == str:
            html += f"<input type='text' name='{input}' placeholder='{input}' value='{value}'>"
        if input_type == int:
            html += f"<input type='number' name='{input}' placeholder='{input}' value='{value}'>"
    html += "</form>"

    return html
            