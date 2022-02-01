from app.models.acesso import Acesso
from sqlite3 import Connection

class AcessoMateriais():

  def __init__(self, db_connection: Connection):
    self.db = db_connection
    self.cursor = db_connection.cursor()

  def cadastrar(self, acesso: Acesso):
    sql = """
    insert into acesso_materiais
    (usuario_id, material_id)
    values
    (?, ?);
    """

    self.cursor.execute(sql, (
      acesso.usuario_id,
      acesso.video_ou_material_id
    ))

    self.db.commit()

    return self.cursor.lastrowid

  def obter_por_usuario_material(self, usuario_id, material_id):
    sql = """
    select 
    acesso_materiais.*,
    usuarios.nome,
    usuarios.email
    from acesso_materiais
    join usuarios
    on acesso_materiais.usuario_id = usuarios.id
    where usuarios.id = ? and material_id = ?;
    """

    self.cursor.execute(sql, (usuario_id, material_id))

    return self.cursor.fetchone()

  def obter(self, usuario_id):
    sql = """
    select 
    count(acesso_materiais.id) as 'numero_materiais_visualizados',
    usuarios.nome, usuarios.email
    from acesso_materiais
    join usuarios
    on acesso_materiais.usuario_id = usuarios.id
    where usuarios.id = ?;
    """

    self.cursor.execute(sql, (usuario_id,))

    return self.cursor.fetchone

  def listar(self):
    sql = """
    select 
    count(acesso_materiais.id) as 'numero_materiais_vizualizados',
    usuarios.nome, usuarios.email
    from acesso_materiais
    join usuarios
    on acesso_materiais.usuario_id = usuarios.id;
    """

    cursor = self.db.cursor()
    cursor.execute(sql)

    return cursor.fetchall()