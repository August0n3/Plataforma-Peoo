class Comentario():

  def __init__(self, comentario, aula_ou_material_id, usuario_id, publico = True, is_material = False):
      self.id = 0
      self.comentario = comentario
      self.aula_ou_material_id = aula_ou_material_id
      self.usuario_id = usuario_id
      self.publico = publico
      self.is_material = is_material 
  
  def getId(self):
      return self._id
  
  def setId(self, id):
      self._id = id
  
  id = property(fget=getId, fset=setId)