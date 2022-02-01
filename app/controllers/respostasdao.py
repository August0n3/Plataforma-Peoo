from app.models.respostas import Resposta

class RespostaDAO():

  def __init__(self, db):
    self.db = db

  
  def cadastrar(self, resposta: Resposta):
    sql = """
    insert into respostas
    (texto, duvida_id, usuario_id)
    values
    (?, ?, ?);
    """
  
    cursor = self.db.cursor()
    cursor.execute(sql, (
      resposta.texto,
      resposta.duvida_id,
      resposta.usuario_id
    ))

    self.db.commit()

    return cursor.lastrowid

  def obter(self, id):
    sql = """
    select * 
    from respostas
    where id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (id,))

    return cursor.fetchone()

  def obter_por_professor(self, id, teacher_id):
    sql = """
    select * 
    from respostas
    where id = ? and usuario_id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (id, teacher_id))

    return cursor.fetchone()

  def listar(self):
    sql = """
    select * 
    from respostas;
    """

    cursor = self.db.cursor()
    cursor.execute(sql)

    return cursor.fetchall()

  def atualizar(self, resposta: Resposta):
    sql = """
    update respostas
    set texto = ?
    where id = ? and usuario_id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (
      resposta.texto,
      resposta.id,
      resposta.usuario_id
      )
    )

    self.db.commit()

    return cursor.rowcount
  
  def deletar(self, id, teacher_id):
    sql = """
    delete from respostas
    where id = ? and usuario_id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (id, teacher_id))

    self.db.commit()

    return cursor.rowcount 