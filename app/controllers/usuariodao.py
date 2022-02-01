from app.models.usuario import Usuario

class UsuarioDAO():

  def __init__(self, db):
    self.db = db

  def cadastrar(self, usuario: Usuario):
    sql = """
    insert into usuarios
    (nome, email,matricula, nivel_acesso)
    values
    (?, ?, ?, ?);
    """
  
    cursor = self.db.cursor()
    cursor.execute(sql, (
      usuario.nome,
      usuario.email,
      usuario.matricula,
      usuario.nivel_acesso
    )
    )
    self.db.commit()

    return cursor.lastrowid

  def verificar_existencia_usuario(self, matricula):
    sql = """
    select *
    from usuarios
    where matricula = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql, (matricula,))

    return cursor.fetchone()

  def desempenho(self):
    sql = """
    select 
    usuarios.id, usuarios.nome,
    case 
        when usuarios.id in (select acesso_aulas.usuario_id from acesso_aulas) then (select count(usuario_id) from acesso_aulas where acesso_aulas.usuario_id = usuarios.id)
        else 0
    end as 'n_aulas_visualizadas',
    case 
        when usuarios.id in (select acesso_materiais.usuario_id from acesso_materiais) then (select count(usuario_id) from acesso_materiais where acesso_materiais.usuario_id = usuarios.id)
        else 0
    end as 'n_materiais_visualizados',
    usuarios.matricula
    from usuarios
    order by n_aulas_visualizadas, n_materiais_visualizados desc;
    """

    cursor = self.db.cursor()
    cursor.execute(sql)

    return cursor.fetchall()
  
  def meu_desempenho(self, usuario_id):
    sql = """
    select 
    usuarios.id, usuarios.nome,
    case 
        when usuarios.id in (select acesso_aulas.usuario_id from acesso_aulas) then (select count(usuario_id) from acesso_aulas where acesso_aulas.usuario_id = usuarios.id)
        else 0
    end as 'n_aulas_visualizadas',
    case 
        when usuarios.id in (select acesso_materiais.usuario_id from acesso_materiais) then (select count(usuario_id) from acesso_materiais where acesso_materiais.usuario_id = usuarios.id)
        else 0
    end as 'n_materiais_visualizadas'
    from usuarios
    where usuarios.id = ?;
    """

    cursor = self.db.cursor()
    cursor.execute(sql,(usuario_id,))

    return cursor.fetchone()