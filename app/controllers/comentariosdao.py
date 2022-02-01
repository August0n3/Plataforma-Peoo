from app.models.comentario import Comentario
import sqlite3

class ComentariosDAO():

  def __init__(self, db: sqlite3.Connection) -> None:
    self.db = db
    self.cursor = db.cursor()

  def listar(self, aula_id):
    sql = """
    select
    comentarios_aulas.id,
    comentarios_aulas.comentario,
    usuarios.nome,
    usuarios.id
    from comentarios_aulas
    join usuarios
    on comentarios_aulas.usuario_id = usuarios.id
    where aula_id = ?;
    """

    self.cursor.execute(sql, (aula_id,))

    return self.cursor.fetchall()

  def obter(self, comentario_id):
    sql = """
    select *
    from comentarios_aulas
    where id = ?;
    """

    self.cursor.execute(sql, (comentario_id,))

    return self.cursor.fetchone()
  
  def cadastrar(self, comentario: Comentario):
    sql = """
    insert into comentarios_aulas
    (comentario, usuario_id, aula_id)
    values
    (?, ?, ?);
    """

    self.cursor.execute(sql, (
      comentario.comentario,
      comentario.usuario_id,
      comentario.aula_ou_material_id
    ))

    self.db.commit()

    return self.cursor.lastrowid

  def atualizar(self, comentario: Comentario):
    sql = """
    update comentarios_aulas
    set comentario = ?
    where id = ? and usuario_id = ?;
    """

    self.cursor.execute(sql, (
      comentario.comentario,
      comentario.id,
      comentario.usuario_id
    ))

    self.db.commit()

    return self.cursor.rowcount
  
  def deletar(self, comentario_id, usuario_id):
    sql = """
    delete from comentarios_aulas
    where id = ? and usuario_id = ?;
    """

    self.cursor.execute(sql, (
      comentario_id,
      usuario_id
    ))

    self.db.commit()

    return self.cursor.rowcount