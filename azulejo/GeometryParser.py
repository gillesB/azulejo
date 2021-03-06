'''
Created on Jul 12, 2012

@author: me
'''
from Workarea import Workarea

class GeometryParser(object):
    '''
    classdocs
    '''
    
    @staticmethod
    def parse_simple_math_expressions(expression):
        expression = str(expression)
        #width
        expression = expression.replace('w', str(Workarea.get_workarea_width()))#+Workarea.get_upper_corner_X()))
        #height
        expression = expression.replace('h', str(Workarea.get_workarea_height()))#+Workarea.get_upper_corner_Y()))
        return eval(expression)
    
    @staticmethod
    def parse_simple_math_window_move_expression(window, expression):
        expression = str(expression)      
        
        window_geometry = window.get_geometry()
        expression = expression.replace('ww', str(window_geometry["width"]))
        expression = expression.replace('wh', str(window_geometry["height"]))
        frame_extents = window.get_frame_extents()
        expression = expression.replace('wfl', str(frame_extents["left"]))
        expression = expression.replace('wfr', str(frame_extents["right"]))
        expression = expression.replace('wft', str(frame_extents["top"]))
        expression = expression.replace('wfb', str(frame_extents["bottom"]))

        expression = GeometryParser.parse_simple_math_expressions(expression)

        return expression

    @staticmethod
    def parse_window_move_geometry(window, geometry):
        for i in range(len(geometry)):
            geometry[i] = GeometryParser.parse_simple_math_window_move_expression(window, geometry[i])
        return geometry

    @staticmethod
    def parse_geometry(geometry):
        return map(GeometryParser.parse_simple_math_expressions, geometry)
    
    @staticmethod
    def parse_arrangement(arrangement):
        return map(GeometryParser.parse_geometry, arrangement)


    def __init__(self):
        '''
        Constructor
        '''
        
