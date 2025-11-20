# tigerpy_drawing.py
import sys
from abc import ABC, abstractmethod
import copy

if __name__ == "__main___":
    print("This module is not meant to be executed directly.")
    sys.exit(1) 

class Pen:
    def __init__(self, strokeSize = 1, strokeColor = (0, 0, 0), fillColor = None):
        self.mStrokeSize = strokeSize
        self.mStrokeColor = strokeColor
        self.mFillColor = fillColor

    def SetStrokeSize(self, strokeSize):
        self.mStrokeSize = strokeSize

    def SetStrokeColor(self, strokeColor):
        self.mStrokeColor = strokeColor

    def SetFillColor(self, fillColor):
        self.mFillColor = fillColor

    def GetStrokeSize(self):
        return self.mStrokeSize
    
    def GetStrokeColor(self):
        return self.mStrokeColor
    
    def GetFillColor(self):
        return self.mFillColor

class DrawingVisitor(ABC):
    @abstractmethod
    def DrawLine(self, pen, x1, y1, x2, y2):
        pass

    @abstractmethod
    def DrawRectangle(self, pen, x, y, width, height):
        pass

    @abstractmethod
    def DrawCircle(self, pen, cx, cy, radius):
        pass

    @abstractmethod
    def DrawEllipse(self, pen, cx, cy, rx, ry):
        pass

    @abstractmethod
    def DrawPolyline(self, pen, points):
        pass

    @abstractmethod
    def DrawPolygon(self, pen, points):
        pass

    @abstractmethod
    def DrawText(self, pen, x, y, text):
        pass

class Drawing:
    @abstractmethod
    def Accept(self, visitor):
        pass

class LineDrawing(Drawing):
    def __init__(self, pen, x1, y1, x2, y2):
        self.mPen = copy.copy(pen)
        self.mX1 = x1
        self.mY1 = y1
        self.mX2 = x2
        self.mY2 = y2

    def Accept(self, visitor):
        visitor.DrawLine(self.mPen, self.mX1, self.mY1, self.mX2, self.mY2)

class RectangleDrawing(Drawing):
    def __init__(self, pen, x, y, width, height):
        self.mPen = copy.copy(pen)
        self.mX = x 
        self.mY = y
        self.mWidth = width
        self.mHeight = height

    def Accept(self, visitor):
        visitor.DrawRectangle(self.mPen, self.mX, self.mY, self.mWidth, self.mHeight)        

class CircleDrawing(Drawing):
    def __init__(self, pen, cx, cy, radius):
        self.mPen = copy.copy(pen)
        self.mCX = cx
        self.mCY = cy
        self.mRadius = radius

    def Accept(self, visitor):
        visitor.DrawCircle(self.mPen, self.mCX, self.mCY, self.mRadius)

class EllipseDrawing(Drawing):
    def __init__(self, pen, cx, cy, rx, ry):
        self.mPen = copy.copy(pen)
        self.mCX = cx
        self.mCY = cy
        self.mRX = rx
        self.mRY = ry

    def Accept(self, visitor):
        visitor.DrawEllipse(self.mPen, self.mCX, self.mCY, self.mRX, self.mRY)

class PolylineDrawing(Drawing):
    def __init__(self, pen, points):
        self.mPen = copy.copy(pen)
        self.mPoints = points

    def Accept(self, visitor):
        visitor.DrawPolyline(self.mPen, self.mPoints)

class PolygonDrawing(Drawing):
    def __init__(self, pen, points):
        self.mPen = copy.copy(pen)
        self.mPoints = points

    def Accept(self, visitor):
        visitor.DrawPolygon(self.mPen, self.mPoints)      

class TextDrawing(Drawing):
    def __init__(self, pen, x, y, text):
        self.mPen = copy.copy(pen)
        self.mX = x
        self.mY = y
        self.mText = text

    def Accept(self, visitor):
        visitor.DrawText(self.mPen, self.mX, self.mY, self.mText)             

# Helper methods for SVG tags
def BeginTag(tag):
    return '<' + tag + ' '

def NumberAttribute(attrName, attrValue):
    return attrName + '="' + str(attrValue) + '"' + ' '

def StringAttribute(attrName, attrValue):
    return attrName + '="' + attrValue + '"' + ' '

def ColorAttribute(attrName, color):
    return attrName + '="rgb(' + str(color[0]) + ',' + str(color[1]) + ',' + str(color[2]) + ')" '

def EndTag():
    return '/>'

class SVGDrawingVisitor(DrawingVisitor):
    def __init__(self, fileName, width, height):
        try:
            self.mFile = open(fileName, 'w')
            self.mFile.write('<svg width="' + str(width) + '" height="' + str(height) + '">\n')
        except Exception as e:
            print(f"An exception occurred: {e}")

    def DrawLine(self, pen, x1, y1, x2, y2):
        line = BeginTag("line") + \
               NumberAttribute("x1", x1) + \
               NumberAttribute("y1", y1) + \
               NumberAttribute("x2", x2) + \
               NumberAttribute("y2", y2) + \
               NumberAttribute("stroke-width", pen.GetStrokeSize()) + \
               ColorAttribute("stroke", pen.GetStrokeColor()) + \
               EndTag() + '\n'
        self.mFile.write(line)

    def DrawRectangle(self, pen, x, y, width, height):
        line = BeginTag("rect") + \
               NumberAttribute("x", x) + \
               NumberAttribute("y", y) + \
               NumberAttribute("width", width) + \
               NumberAttribute("height", height) + \
               NumberAttribute("stroke-width", pen.GetStrokeSize()) + \
               ColorAttribute("stroke", pen.GetStrokeColor())
        
        if (pen.GetFillColor() == None):
               line += StringAttribute("fill", "none")
        else:
               line += ColorAttribute("fill", pen.GetFillColor())

        line += EndTag() + '\n'
        self.mFile.write(line)

    def DrawCircle(self, pen, cx, cy, radius):
        line = BeginTag("circle") + \
               NumberAttribute("cx", cx) + \
               NumberAttribute("cy", cy) + \
               NumberAttribute("r", radius) + \
               NumberAttribute("stroke-width", pen.GetStrokeSize()) + \
               ColorAttribute("stroke", pen.GetStrokeColor())
        
        if (pen.GetFillColor() == None):
               line += StringAttribute("fill", "none")
        else:
               line += ColorAttribute("fill", pen.GetFillColor())

        line += EndTag() + '\n'
        self.mFile.write(line)  

    def DrawEllipse(self, pen, cx, cy, rx, ry):   
        line = BeginTag("ellipse") + \
               NumberAttribute("cx", cx) + \
               NumberAttribute("cy", cy) + \
               NumberAttribute("rx", rx) + \
               NumberAttribute("ry", ry) + \
               NumberAttribute("stroke-width", pen.GetStrokeSize()) + \
               ColorAttribute("stroke", pen.GetStrokeColor())
        
        if (pen.GetFillColor() == None):
               line += StringAttribute("fill", "none")
        else:
               line += ColorAttribute("fill", pen.GetFillColor())

        line += EndTag() + '\n'
        self.mFile.write(line)  

    def DrawPolyline(self, pen, points):
        line = BeginTag("polyline")
        line += 'points="'
        for pt in points:
            line += str(pt[0]) + ',' + str(pt[1]) + ' '
        line += '" '

        line += NumberAttribute("stroke-width", pen.GetStrokeSize())
        line += ColorAttribute("stroke", pen.GetStrokeColor())
        line += StringAttribute("fill", "none")

        line += EndTag() + '\n'
        self.mFile.write(line) 

    def DrawPolygon(self, pen, points):
        line = BeginTag("polygon")
        line += 'points="'
        for pt in points:
            line += str(pt[0]) + ',' + str(pt[1]) + ' '
        line += '" '

        line += NumberAttribute("stroke-width", pen.GetStrokeSize())
        line += ColorAttribute("stroke", pen.GetStrokeColor())
        
        if (pen.GetFillColor() == None):
               line += StringAttribute("fill", "none")
        else:
               line += ColorAttribute("fill", pen.GetFillColor())

        line += EndTag() + '\n'
        self.mFile.write(line)         

    def DrawText(self, pen, x, y, text):
        line = BeginTag("text") + \
               NumberAttribute("x", x) + \
               NumberAttribute("y", y) + \
               NumberAttribute("stroke-width", pen.GetStrokeSize()) + \
               ColorAttribute("stroke", pen.GetStrokeColor())
        
        if (pen.GetFillColor() == None):
               line += StringAttribute("fill", "none")
        else:
               line += ColorAttribute("fill", pen.GetFillColor())

        line += '>'
        line += text
        line += '</text>\n'

        self.mFile.write(line)        

    def __del__(self):
        self.mFile.write('</svg>')
        self.mFile.close()             

class DrawingCanvas:
    def __init__(self, width, height):
        self.mWidth = width
        self.mHeight = height
        self.mPen = Pen() 
        self.mDrawings = []

    def SetPen(self, pen):
        self.mPen = copy.copy(pen)

    def DrawLine(self, x1, y1, x2, y2):
        self.mDrawings.append(LineDrawing(self.mPen, x1, y1, x2, y2))

    def DrawRectangle(self, x, y, width, height):
        self.mDrawings.append(RectangleDrawing(self.mPen, x, y, width, height))

    def DrawCircle(self, cx, cy, radius):
        self.mDrawings.append(CircleDrawing(self.mPen, cx, cy, radius))

    def DrawEllipse(self, cx, cy, rx, ry):
        self.mDrawings.append(EllipseDrawing(self.mPen, cx, cy, rx, ry))

    def DrawPolyline(self, points):
        self.mDrawings.append(PolylineDrawing(self.mPen, points))

    def DrawPolygon(self, points):
        self.mDrawings.append(PolygonDrawing(self.mPen, points))    

    def DrawText(self, x, y, text):
        self.mDrawings.append(TextDrawing(self.mPen, x, y, text))    
                        
    def ExportSVG(self, fileName):
        svgDwgVisitor = SVGDrawingVisitor(fileName, self.mWidth, self.mHeight)
        for dwg in self.mDrawings:
            dwg.Accept(svgDwgVisitor)