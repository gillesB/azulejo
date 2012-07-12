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
        expression = expression.replace('w', str(Workarea.get_screen_height()))
        expression = expression.replace('h', str(Workarea.get_screen_width()))
        return eval(expression)

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
        