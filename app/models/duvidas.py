class Duvida():

  def __init__(self, duvida_text, usuario_id):
    self.id = 0
    self.duvida = duvida_text
    self.usuario_id = usuario_id
  
  def getId(self):
    return self._id
  
  def setId(self, id):
    self._id = id
    
  id = property(fget=getId, fset=setId)