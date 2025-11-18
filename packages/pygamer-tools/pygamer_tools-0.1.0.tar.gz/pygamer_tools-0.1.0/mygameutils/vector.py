class Vector:
  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y

  def add(self, other):
    return Vector(self.x + other.x, self.y + other.y)
  
  def subtract(self, other):
    return Vector(self.x - other.x, self.y - other.y)
  
  def multiply(self, scalar):
    return Vector(self.x * scalar, self.y * scalar)
  
  def magnitude(self):
    return (self.x**2 + self.y**2) ** 0.5