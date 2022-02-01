class Resposta():

  def __init__(self, texto, duvida_id, usuario_id):
    self.id = 0
    self.texto = texto
    self.duvida_id = duvida_id
    self.usuario_id = usuario_id

  def getId(self):
    return self._id
  
  def setId(self, id):
    self._id = id
  
  id = property(fget=getId, fset=setId)





"""
create table respostas (
  id integer primary key autoincrement,
  texto text not null,
  duvida_id integer,
  usuario_id integer,

  foreign key (duvida_id) references duvidas (id),
  foreign key (usuario_id) references usuarios (id)
);

"""