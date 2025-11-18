import time

class Cooldown:
  def __init__(self, delay):
    self.delay = delay
    self.last = 0

  def ready(self):
    if time.time() - self.last >= self.delay:
      self.last = time.time()
      return True
    return False