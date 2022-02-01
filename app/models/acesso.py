class Acesso():

  def __init__(self, usuario_id, video_ou_material_id):
    self.id = 0
    self.video_ou_material_id = video_ou_material_id
    self.usuario_id = usuario_id
  
  def getId(self):
    return self._id
  
  def setId(self, id):
    self._id = id
  
  id = property(fget=getId, fset=setId)