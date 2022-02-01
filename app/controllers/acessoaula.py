from app.models.acesso import Acesso
from sqlite3 import Connection

class AcessoAula():

  def __init__(self, db_connection: Connection):
    self.db = db_connection
    self.cursor = db_connection.cursor()

  def cadastrar(self, acesso: Acesso):
    sql = """
    insert into acesso_aulas
    (usuario_id, aula_id)
    values
    (?, ?);
    """

    self.cursor.execute(sql, (
      acesso.usuario_id,
      acesso.video_ou_material_id
    ))

    self.db.commit()

    return self.cursor.lastrowid

  def obter_por_usuario_aula(self, usuario_id, aula_id):
    sql = """
    select 
    acesso_aulas.*,
    usuarios.nome,
    usuarios.email
    from acesso_aulas
    join usuarios
    on acesso_aulas.usuario_id = usuarios.id
    where usuarios.id = ? and aula_id = ?;
    """

    self.cursor.execute(sql, (usuario_id, aula_id))

    return self.cursor.fetchone()

  def obter(self, usuario_id):
    sql = """
    select 
    acesso_aulas.*,
    usuarios.nome,
    usuarios.email
    from acesso_aulas
    join usuarios
    on acesso_aulas.usuario_id = usuarios.id
    where usuarios.id = ?;
    """

    self.cursor.execute(sql, (usuario_id,))

    return self.cursor.fetchone()

  def listar(self):
    sql = """
    select * from acesso_aulas;
    """

    cursor = self.db.cursor()
    cursor.execute(sql)

    return cursor.fetchall()