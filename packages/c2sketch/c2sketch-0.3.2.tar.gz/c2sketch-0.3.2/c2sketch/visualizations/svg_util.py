"""Utility functions for generation SVG visualizations"""

import math
from xml.sax.saxutils import escape
from dataclasses import dataclass
from .color_util import black_or_white

#Rough approximations based on average letter in 12pt Verdana
CHAR_WIDTH = 8.7
CHAR_HEIGHT = 13.8

@dataclass
class Point:
    x: int
    y: int

@dataclass
class Shape:
    x: int #Center x
    y: int #Center y
    type: str   
    width: int
    height: int
    padding: int = 2
    text: str | None = None
    color: str | None = None

@dataclass
class Connection:
    source: Shape | Point
    destination: Shape | Point

    source_head: bool
    destination_head: bool


def svg_figure(shapes: list[Shape], connections: list[Connection]) -> str:
    fragments = []
    for shape in shapes:
        fragments.append(svg_shape(shape))
    for connection in connections:
        fragments.append(svg_connection(connection))
    
    max_x = 0 if not shapes else max(shape.x + shape.width / 2 for shape in shapes)
    max_y = 0 if not shapes else max(shape.y + shape.height / 2 for shape in shapes)

    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{max_x}" height="{max_y}">\n{"\n".join(fragments)}\n</svg>'

def svg_shape(shape: Shape) -> str:
    if shape.type == 'ellipse': 
        return svg_ellipse(shape)
    if shape.type == 'box':
        return svg_box(shape)
    return svg_box(shape)

def svg_box(shape: Shape) -> str:
    color = shape.color if shape.color is not None else 'white'
    text_color = black_or_white(color) if shape.color is not None else 'black'

    svg = [
        f'<rect x="{shape.x - shape.width // 2}" y="{shape.y - shape.height //2}" width="{shape.width}" height="{shape.height}" fill="{color}" stroke="black" />',
        svg_textbox(shape.x,shape.y,shape.width - 2 * shape.padding,shape.height - 2 * shape.padding,shape.text,True,text_color),    
    ]
    return '\n'.join(svg)

def svg_ellipse(shape: Shape) -> str:
    color = shape.color if shape.color is not None else 'white'
    text_color = black_or_white(color) if shape.color is not None else 'black'

    svg = [
        f'<ellipse cx="{shape.x}" cy="{shape.y}" rx="{shape.width//2}" ry="{shape.height//2}" fill="white" stroke="black" />',
        svg_textbox(shape.x,shape.y,shape.width - 2 * shape.padding,shape.height - 2 * shape.padding,shape.text,True,text_color)
    ]
    return '\n'.join(svg)

def svg_connection(connection: Connection) -> str:
    svg = []

    #Helper to find the connection point on the border of the shape
    def connect_point(shape: Shape, ref: Shape | Point ) -> tuple[float,float,float]: #offset x, offset y, angle
        #Angle from source to dest
        dx = ref.x - shape.x
        dy = ref.y - shape.y
        rx = shape.width / 2
        ry = shape.height / 2
        angle = math.atan2(dy,dx)

        #Find point on box outline
        if  shape.type == 'ellipse':
            intersect_s = ((rx * ry) / math.sqrt(rx**2 * dy**2 + ry**2 * dx**2))
            x = intersect_s * dx
            y = intersect_s * dy

        elif shape.type == 'box': #Default is box
            if dx == 0.0: #Exactly above each other
                x = 0
                y = ry if dy > 0 else -ry
            elif dy == 0.0: #Exactly next to each other
                x = rx if dx > 0 else -rx
                y = 0.0
            else:
                scale_x = abs(rx / dx)
                scale_y = abs(ry / dy)
                
                if abs(scale_x * dy) < ry:
                    x = scale_x * dx
                    y = scale_x * dy
                else:
                    x = scale_y * dx
                    y = scale_y * dy
        else:
            x, y = 0, 0
        return (x,y,angle)

    start_x, start_y, start_angle = connect_point(connection.source,connection.destination)
    end_x, end_y, end_angle = connect_point(connection.destination,connection.source)

    angle_offset = math.pi / 2
    if connection.source_head:
        svg.append(svg_triangle(connection.source.x + start_x, connection.source.y + start_y, start_angle + angle_offset))
    if connection.destination_head:
        svg.append(svg_triangle(connection.destination.x + end_x, connection.destination.y + end_y, end_angle + angle_offset))
    
    svg.append(f'<line x1="{connection.source.x + start_x}" y1="{connection.source.y + start_y}" x2="{connection.destination.x + end_x}" y2="{connection.destination.y + end_y}" stroke="black" />')
    return '\n'.join(svg)


def svg_triangle(x,y, angle: float = 0.0, color = 'black', fill=True) -> str:

    sin_angle = math.sin(angle)
    cos_angle = math.cos(angle)

    x1, y1 = x - 5, y - 10
    x1, y1 = (x + cos_angle * -5 - sin_angle * -10, y + sin_angle * -5 + cos_angle * -10)
    x2, y2 = x, y
    x3, y3 = x + 5, y - 10
    x3, y3 = (x + cos_angle * 5 - sin_angle * -10, y + sin_angle * 5 + cos_angle * -10)

    if fill:
        return f'<polygon points="{x1} {y1} {x2} {y2} {x3} {y3}" fill="{color}"/>'
    else:
        return f'<polygon points="{x1} {y1} {x2} {y2} {x3} {y3}" stroke="{color}" fill="none"/>'


def svg_textbox(x, y, width, height, text: str, wrap: bool = True, color: str | None = None) -> str:

    max_chars_per_line = int(width / CHAR_WIDTH)
    max_lines = int(height / CHAR_HEIGHT)

    color = 'black' if color is None else color   
    if wrap:
        lines = wordwrap(text,max_chars_per_line)
        if len(lines) > max_lines:
            #Add ellipses at end of last line
            lines[max_lines - 1] = lines[max_lines - 1][:-3]+'...'
        
        offset = (-(len(lines[:max_lines]) * CHAR_HEIGHT) / 2) + CHAR_HEIGHT
        result = []
        for line in lines[:max_lines]:
            result.append(f'<text x="{x}" y="{y+offset}" font-family="Verdana" font-size="12" text-anchor="middle" fill="{color}">{escape(line)}</text>')
            offset += CHAR_HEIGHT
        return '\n'.join(result)
    else:
        escaped = escape(elipsis(text,max_chars_per_line))
        return f'<text x="{x}" y="{y + CHAR_HEIGHT / 2}" font-family="Verdana" font-size="12" text-anchor="middle" fill="{color}">{escaped}</text>'


def elipsis(text,max_length):
    return text if len(text) <= max_length else text[:max_length - 3]+'...'

def wordwrap(text:str, max_line_length: int) -> list[str]:
    lines = []
    start = 0
    while start < len(text):
        #Skip whitespace at start of lines
        while text[start].isspace():
            start += 1
    
        end = start
        #Try to add as much chars to the line as possible
        while end < len(text) and end - start <= max_line_length and text[end] != '\n':
            end += 1
            
        #If we are at the end or at a newline, just add the line
        if end >= len(text) or text[end] == '\n':
            lines.append(text[start:end])
        #If we stop at a space, back up a little
        elif text[end -1 ].isspace():
            while end > start and text[end - 1].isspace():
                end -= 1
            lines.append(text[start:end])
        #Backup to the end of the previous word
        else:
            while end > start and not text[end - 1].isspace():
                end -= 1
            #The last (and first) word is bigger than the maximum line
            #Create an ellipsis for the word, but also read it entirely
            if start == end:
                end = start + max_line_length
                lines.append(text[start:start + max_line_length - 3]+"...")
                
                while end < len(text) and not text[end].isspace():
                    end += 1
            else:
                while end > start and not text[end].isspace():
                    end -= 1
                lines.append(text[start:end])
        #Continue
        start = end

    return lines