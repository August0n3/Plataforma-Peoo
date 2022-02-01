from app.models.materiais import Material

class MaterialDAO():

  def __init__(self, db):
    self.db = db

  
  def cadastrar(self, material: Material):
    sql = """
    insert into materiais
    (titulo, descricao, link, teacher_id)
    values
    (?, ?, ?, ?);
    """
  
    cursor = self.db.cursor()
    cursor.execute(sql, (
      material.titulo,
      material.descricao,
      material.link,
      material.usuario_id
      )
    )

    self.db.commit()

    return cursor.lastrowid

  def obter(self, id):
    sql = """
    select * from materiais
    where id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (id,))

    return cursor.fetchone()

  def obter_por_professor(self, id, teacher_id):
    sql = """
    select * from materiais
    where id = ? and teacher_id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (id, teacher_id))

    return cursor.fetchone()

  def listar(self):
    sql = """
    select * from materiais;
    """

    cursor = self.db.cursor()
    cursor.execute(sql)

    return cursor.fetchall()
  
  def materiais_vistos(self, user_id):
    sql = """
      select materiais.* from acesso_materiais 
      join materiais on acesso_materiais.material_id = materiais.id 
      where acesso_materiais.usuario_id = ?;
      """
    cursor = self.db.cursor()
    cursor.execute(sql, (user_id,))

    return cursor.fetchall()
  
  def listar_meus_materiais(self, teacher_id):
    sql = """
    select *
    from materiais
    where teacher_id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (teacher_id,))

    return cursor.fetchall()

  def atualizar(self, material: Material):
    sql = """
    update materiais
    set titulo = ?, descricao = ?, link = ?
    where id = ? and teacher_id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (
      material.titulo,
      material.descricao,
      material.link,
      material.id,
      material.usuario_id
      )
    )

    self.db.commit()

    return cursor.rowcount
  
  def deletar(self, id, teacher_id):
    sql = """
    delete from materiais
    where id = ? and teacher_id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (id, teacher_id))

    self.db.commit()

    return cursor.rowcount 