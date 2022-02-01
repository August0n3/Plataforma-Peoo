import sqlite3
from app.models.duvidas import Duvida

class DuvidaDAO():

  def __init__(self, db: sqlite3.Connection):
    self.db = db
    self.cursor = db.cursor()

  def cadastrar(self, duvida: Duvida):
    sql = """
    insert into duvidas
    (duvida, usuario_id)
    values
    (?, ?);
    """

    self.cursor.execute(sql, (
      duvida.duvida,
      duvida.usuario_id
    ))
    
    self.db.commit()

    return self.cursor.lastrowid
  
  def listar_minhas_duvidas(self, usuario_id):
    sql = """
    select *,
    case
	    when duvidas.id in (select respostas.duvida_id from respostas) then (select respostas.texto from respostas where respostas.duvida_id = duvidas.id)
	    else ''
    end as 'resposta'
    from duvidas
    where usuario_id = ?;
    """
    
    self.cursor.execute(sql, (usuario_id,))

    return self.cursor.fetchall()
  
  def obter(self, duvida_id):
    sql = """
    select *
    from duvidas
    where id = ?;
    """

    self.cursor.execute(sql, (duvida_id,))

    return self.cursor.fetchone()

  def listar(self):
    sql = """
    select 
    duvidas.*,
    usuarios.nome,
    case
	    when duvidas.id in (select respostas.duvida_id from respostas) then (select respostas.texto from respostas where respostas.duvida_id = duvidas.id)
	    else ''
    end as 'resposta',
    case
	    when duvidas.id in (select respostas.duvida_id from respostas) then (select respostas.id from respostas where respostas.duvida_id = duvidas.id)
	    else ''
    end as 'resposta'
    from duvidas
    join usuarios
    on duvidas.usuario_id = usuarios.id;
    """

    self.cursor.execute(sql)

    return self.cursor.fetchall()

  def editar(self, duvida: Duvida):
    sql = """
    update duvidas
    set duvida = ?
    where id = ? and usuario_id = ?;
    """

    self.cursor.execute(sql, (
      duvida.duvida,
      duvida.id,
      duvida.usuario_id
    ))

    self.db.commit()

    return self.cursor.rowcount
  
  def remover(self, duvida_id, usuario_id):
    sql = """
    delete from duvidas
    where id = ? and usuario_id = ?;
    """

    self.cursor.execute(sql, (
      duvida_id, 
      usuario_id
    ))

    self.db.commit()

    return self.cursor.rowcount