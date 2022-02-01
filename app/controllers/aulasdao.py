from app.models.aulas import Aula

class AulaDAO():

  def __init__(self, db):
    self.db = db

  def tres_ultimas_aulas(self):
    sql = """
      select *
      from aulas
      order by id desc
      limit 3;
    """

    cursor = self.db.cursor()
    cursor.execute(sql)

    return cursor.fetchall()
  
  def cadastrar(self, aula: Aula):
    sql = """
    insert into aulas
    (titulo,descricao, link, teacher_id)
    values
    (?, ?, ?, ?);
    """
  
    cursor = self.db.cursor()
    cursor.execute(sql, (
      aula.titulo,
      aula.descricao,
      aula.link,
      aula.usuario_id
      )
    )

    self.db.commit()

    return cursor.lastrowid

  def obter(self, id):
    sql = """
    select * from aulas
    where id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (id,))

    return cursor.fetchone()

  def listar(self):
    sql = """
    select * from aulas;
    """

    cursor = self.db.cursor()
    cursor.execute(sql)

    return cursor.fetchall()

  def listar_minhas_aulas(self, teacher_id):
    sql = """
    select *
    from aulas
    where teacher_id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (teacher_id,))

    return cursor.fetchall()

  def aulas_vistas(self, user_id):
    sql = """
      select aulas.* from acesso_aulas 
      join aulas on acesso_aulas.aula_id = aulas.id 
      where acesso_aulas.usuario_id = ?;
      """
    cursor = self.db.cursor()
    cursor.execute(sql, (user_id,))

    return cursor.fetchall()


  def atualizar(self, aula: Aula):
    sql = """
    update aulas
    set titulo = ?, descricao = ?, link = ?
    where id = ? and teacher_id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (
      aula.titulo,
      aula.descricao,
      aula.link,
      aula.id,
      aula.usuario_id
      )
    )

    self.db.commit()

    return cursor.rowcount
  
  def deletar(self, id, teacher_id):
    sql = """
    delete from aulas
    where id = ? and teacher_id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (id, teacher_id))

    self.db.commit()

    return cursor.rowcount 

  
  