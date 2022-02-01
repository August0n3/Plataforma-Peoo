from flask import render_template, request, url_for, redirect, session, flash, jsonify
from sqlite3.dbapi2 import Error, complete_statement, connect
from authlib.integrations.flask_client import OAuth
from datetime import datetime

from requests.api import get
from app import app 
from app.config import GOOGLE_KEY, GOOGLE_USERID
from app.models.acesso import Acesso

from app.models.connection import get_db
from app.services.SuapApi import Suap
from app.utils import login_is_required

from app.models.usuario import Usuario
from app.controllers.usuariodao import UsuarioDAO
from app.models.aulas import Aula
from app.controllers.aulasdao import AulaDAO
from app.models.materiais import Material
from app.controllers.materiaisdao import MaterialDAO
from app.models.comentario import Comentario
from app.controllers.comentariosdao import ComentariosDAO
from app.controllers.comentariosmaterialdao import ComentariosMaterialDAO
from app.models.duvidas import Duvida
from app.controllers.duvidasdao import DuvidaDAO
from app.models.respostas import Resposta
from app.controllers.respostasdao import RespostaDAO
from app.controllers.acessoaula import AcessoAula
from app.controllers.acessomateriais import AcessoMateriais

@app.route('/')
def signin_suap():
  return render_template('sign-in.html') 

@app.route('/auth/suap', methods=['POST',])
def auth_suap():
  if( request.method == "POST" ):
    # Captando as informações enviadas pelo usuario
    matriculation = request.form.get('Matricula')
    password = request.form.get("Senha")

    # Verificando se todos os campos foram preenchidos
    if( matriculation and password ):
      api = Suap() # Instanciando a classe Suap
      user_auth_suap = api.autentica(matriculation, password)

      # Se existir um usuario com essas credenciais
      if( user_auth_suap is not None ):
        # Instanciando o controlador de usuarios
        userdao = UsuarioDAO(get_db())

        if( user_auth_suap['vinculo']['curso'].lower().find('informática') == -1):
          flash('Esse serviço é exclusivo para o curso de informática!', 'warning')
          return redirect(url_for('signin_suap'))

        user = userdao.verificar_existencia_usuario(user_auth_suap['matricula'])

        # Criando uma instancia de usuario
        user_instance = Usuario(
          nome=user_auth_suap['vinculo']['nome'],
          email=user_auth_suap['email'],
          matricula=user_auth_suap['matricula']
        )

        if( user is None ):
          # Verificando se o usuario existe
          try:
            user_id = userdao.cadastrar( user_instance )
            user_instance.id = user_id
            user = userdao.verificar_existencia_usuario(user_auth_suap['matricula'])
          except:
            flash('Esse E-mail e/ou matricula já estão sendo utilizados!', 'danger')
            return redirect(url_for("index"))
        else:
          user_instance.id = user[0]

        # Salvando os dados do usuario na sessao
        session['logged'] = True 
        session['infos'] = {
          'id': user_instance.id,
          'nome': user_auth_suap['vinculo']['nome'],
          'matricula': user_auth_suap['matricula'],
          'tipo_vinculo': user[3],
          'nome_usual': user_auth_suap['nome_usual']
        }
        
        # Se o usuario for um professor
        if( user[3] == 1 ):        
          return redirect(url_for('painel'))
          
        elif ( user[3] == 0 ):
          return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))
 
      else:
        flash("Matricula e/ou senha incorretos!", "danger")
        return redirect(url_for("signin_suap"))

    else:
      flash("Preencha todos os campos!", "warning")
      return redirect(url_for("signin_suap"))

@app.route('/painel')
def painel():
  if( session.get('logged') == False or session.get('infos') is None ):
    flash('Você não tem permissão para acessar essa funcionalidade, pois você não está logado.', 'danger')
    return redirect(url_for('signin_suap'))
    
  if( session['infos']['tipo_vinculo'] != 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  aulasdao = AulaDAO(get_db())

  aulas = aulasdao.tres_ultimas_aulas()

  return render_template('painel.html', infos=session['infos'], aulas=aulas)

@app.route('/aulas/cadastrar', methods=['POST','GET'])
def cadastro_aulas():
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))
    
  if( session['infos']['tipo_vinculo'] != 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  if( request.method == "POST" ):
    # Captando as informações enviadas pelo usuario
    titulo = request.form.get("Titulo")
    desc = request.form.get("Descricao")
    link = request.form.get("Link")
    link = link.replace('watch?v=', 'embed/')
    link = link[link.find('embed/') + 6::]

    aula = Aula(titulo,desc,link, session['infos']['id'])
  
    auladao = AulaDAO(get_db())
    aula_id = auladao.cadastrar(aula)

    if( aula_id > 0 ):
      flash('Aula cadastrada com sucesso', 'success')
    else:
      flash('Erro no cadastro.', 'danger')  

  return render_template('cadastrar-aulas.html') 

@app.route('/aulas/')
def listar_aulas():
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))
    
  if( session['infos']['tipo_vinculo'] != 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))
    
  auladao = AulaDAO(get_db())
  aulas = auladao.listar_minhas_aulas(session['infos']['id'])
  
  return render_template("listar-todas-aulas.html", aulas=aulas)


@app.route('/desempenho')
def desempenho():
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))
    
  if( session['infos']['tipo_vinculo'] != 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  usuariosdao = UsuarioDAO(get_db())
  desempenho = usuariosdao.desempenho()

  return render_template('desempenho.html', desempenho=desempenho)

@app.route('/materiais')
def listar_materiais():
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))
    
  if( session['infos']['tipo_vinculo'] != 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  materialdao = MaterialDAO(get_db())
  material = materialdao.listar_meus_materiais(session['infos']['id'])

  return render_template('listar-materiais.html', materiais = material)

@app.route('/sobre-nos')
def sobre_nos():
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))
    
  return render_template('sobre-nos.html')

@app.route('/sobre-nos-alunos')
def sobre_nos_alunos():
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))
    
  return render_template('sobre-nos-alunos.html')

@app.route('/painel-aluno/<usuario_id>/',methods=['GET',])
def painel_aluno(usuario_id):
  #verificações de segurança
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))

  if( session['infos']['tipo_vinculo'] == 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel'))

  if (int(session['infos']['id']) != int(usuario_id)):
    flash('Você não tem permissão para fazer isso!','warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  #Área do meu desempenho
  usuariodao = UsuarioDAO(get_db())
  meu_desempenho= usuariodao.meu_desempenho(usuario_id)
  aulasdao = AulaDAO(get_db())
  aulas = aulasdao.tres_ultimas_aulas()

  return render_template('painel-aluno.html', aulas=aulas, alunos = meu_desempenho)

@app.route('/listar-aulas-aluno')
def listar_aulas_aluno():
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))

  aulasdao = AulaDAO(get_db())

  aulas = aulasdao.listar()

  return render_template('listar-aulas-aluno.html', aulas=aulas)

@app.route('/listar-materiais-aluno')
def listar_materiais_aluno():
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))

  materialdao = MaterialDAO(get_db())
  material = materialdao.listar()

  return render_template('listar-materiais-aluno.html', materiais = material)

@app.route('/comentarios')
def comentarios():
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('comentarios'))

  return render_template('comentarios.html')

@app.route('/edicao-material/<material_id>/', methods=['GET', 'POST',])
def edicao_material(material_id):
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))
    
  if( session['infos']['tipo_vinculo'] != 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  materialdao = MaterialDAO(get_db())

  if( request.method == "POST" ):
    # Captando as informações enviadas pelo usuario
    titulo = request.form.get("Titulo")
    descricao = request.form.get('Descricao')
    link = request.form.get("Link")

    material = Material(titulo, descricao, link, session['infos']['id'])
    material.id = material_id

    n_alteracoes = materialdao.atualizar(material)

    if( n_alteracoes > 0 and n_alteracoes is None ):
      flash('Alterações feitas com sucesso!', 'success')
    else:
      flash('Não foi feita nenhuma alteração!', 'danger')
    
    return redirect(url_for('listar_materiais'))

  material = materialdao.obter(material_id)
  return render_template('edicao-material.html', material=material)

@app.route('/edicao-aula/<aula_id>/', methods=['GET', 'POST',])
def edicao_aula(aula_id):
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))
    
  if( session['infos']['tipo_vinculo'] != 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  if( request.method == "POST" ):
    titulo = request.form.get("Titulo")
    desc = request.form.get("Descricao")
    link = request.form.get("Link")
    link = link.replace('watch?v=', 'embed/')

    aula = Aula(titulo, desc, link, session['infos']['id'])
    aula.id = aula_id

    auladao = AulaDAO(get_db())
    n_alteracoes = auladao.atualizar(aula)

    if( n_alteracoes > 0 and n_alteracoes is not None ):
      flash('Alterações feitas com sucesso!', 'success')
    else:
      flash('Não foi feita nenhuma alteração!', 'warning')
    
    return redirect(url_for('painel'))

  auladao = AulaDAO(get_db())
  aula = auladao.obter(aula_id)

  if( aula is None ):
    flash('Não existe aula com esse ID!', 'warning')
    return redirect(url_for('painel'))
  elif( aula[5] != session['infos']['id'] ):
    flash('Não é possível editar essa aula!', 'warning')
    return redirect(url_for('painel'))

  return render_template('edicao-aula.html', aula = aula)

@app.route('/materiais/cadastrar', methods=['POST','GET'])
def cadastro_materiais():
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))
    
  if( session['infos']['tipo_vinculo'] != 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  if( request.method == "POST" ):
    # Captando as informações enviadas pelo usuario
    titulo = request.form.get("Titulo")
    descricao = request.form.get('Descricao')
    link = request.form.get("Link")

    material = Material(titulo, descricao, link, session['infos']['id'])
  
    materialdao = MaterialDAO(get_db())
    material_id = materialdao.cadastrar(material)
    
    if( material_id > 0 and material_id is not None ):
      flash('Material cadastrado com sucesso!', 'success')
    else:
      flash('Não foi possível fazer o cadastro do material', 'danger')
    
  return render_template('cadastrar-materiais.html') 

@app.route('/aulas/deletar/<aula_id>/', methods=['GET',])
def deletar_aula(aula_id):
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))
    
  if( session['infos']['tipo_vinculo'] != 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  aulasdao = AulaDAO(get_db())

  n_alteracoes = aulasdao.deletar(aula_id, session['infos']['id'])

  if( n_alteracoes > 0 and n_alteracoes is not None ):
    flash('Aula apagada com sucesso!', 'success')
    return redirect(url_for('painel'))
  
  flash('Não foi possível apagar a aula, tente novamente!', 'danger')
  return redirect(url_for('painel'))

@app.route('/materiais/deletar/<material_id>/', methods=['GET',])
def deletar_material(material_id):
  if( session.get('logged') == False or session.get('infos') is None ):
    return redirect(url_for('signin_suap'))
    
  if( session['infos']['tipo_vinculo'] != 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  materialdao = MaterialDAO(get_db())
  n_deletados = materialdao.deletar(material_id, session['infos']['id'])

  if( n_deletados > 0 and n_deletados is not None ):
    flash('Material excluído com sucesso!', 'success')
  else:
    flash('Não foi possível excluir o material!', 'danger')
  
  return redirect(url_for('listar_materiais'))

@app.route('/comentarios/<aula_id>/')
@login_is_required
def listar_comentarios(aula_id):
  comentariosdao = ComentariosDAO(get_db())
  comentarios = comentariosdao.listar(aula_id)

  return jsonify(comentarios), 200

@app.route('/comentarios/editar/<comentario_id>/', methods=['GET', 'POST',])
@login_is_required
def editar_comentario(comentario_id):
  if( request.method == "POST" ):
    comentario_text = request.form.get('Comentario')
    comentariosdao = ComentariosDAO(get_db())

    # Captando um comentario especifico
    comentario = comentariosdao.obter(comentario_id)

    # Verificando se o comentario existe
    if( comentario is not None ):
      # Verificando se a pessoa que fez o comentario eh a mesma que esta tentando apagar o mesmo
      if( comentario[3] != session['infos']['id'] ):
        flash('Não é possível apagar um comentário que não foi você quem fez!', 'warning')
        return redirect(f"/comentar/{comentario[4]}/")

    else:
      flash("Comentário inexistente!", 'danger')
      return redirect(f"/comentar/{comentario[4]}/")

    # Verificando se o campo de comentario foi preenchido
    if( comentario_text is not None ):
      comentario_instance = Comentario(
        comentario=comentario_text,
        aula_ou_material_id=comentario[4],
        usuario_id=session['infos']['id']
      )

      comentario_instance.id = comentario_id

      n_alteracoes = comentariosdao.atualizar(comentario_instance)

      # Verificando se houveram alteracoes
      if( n_alteracoes > 0 and n_alteracoes is not None ):
        flash('Alterações feitas com sucesso!', 'success')
        return redirect(f"/comentar/{comentario_instance.aula_ou_material_id}/")

      flash('Não foi possível efetuar as alterações no comentário!', 'danger')
      return redirect(f"/comentar/{comentario_instance.aula_ou_material_id}/")

    else:
      flash('Preencha todos os campos!', 'warning')
      return redirect(f"/comentar/{comentario[4]}/")
  
  # Captando um comentario especifico
  comentariosdao = ComentariosDAO(get_db())
  comentario = comentariosdao.obter(comentario_id)
  
  # Verificando se o comentario existe
  if( comentario is not None ):
    # Verificando se a pessoa que fez o comentario eh a mesma que esta tentando apagar o mesmo
    if( comentario[3] != session['infos']['id'] ):
      flash('Não é possível editar um comentário que não foi você quem fez!', 'warning')
      return redirect(url_for('comentar_aula', aula_id=comentario[4]))
  
  else:
    flash("Comentário inexistente!", 'danger')
    return redirect(url_for('comentar_aula', aula_id=comentario[4]))

  aulasdao = AulaDAO(get_db())
  aula = aulasdao.obter(comentario[4])

  return render_template('comentarios-editar.html', aula=aula, comentario=comentario)

@app.route('/comentarios/apagar/<comentario_id>/', methods=['GET',])
@login_is_required
def apagar_comentario(comentario_id):
  # Criando uma instancia do controlador de comentarios
  comentariosdao = ComentariosDAO(get_db())

  # Captando um comentario especifico
  comentario = comentariosdao.obter(comentario_id)

  # Verificando se o comentario existe
  if( comentario is not None ):
    # Verificando se a pessoa que fez o comentario eh a mesma que esta tentando apagar o mesmo
    if( comentario[3] != session['infos']['id'] ):
      flash("Não é possível apagar um comentário que não foi você quem fez!", 'warning')
      return redirect(url_for('painel'))

  else:
    flash("Comentário inexistente", 'danger')
    return redirect(url_for('painel'))

  # Captando a quantidade de registros apagados
  n_apagados = comentariosdao.deletar(comentario_id=comentario_id, usuario_id=session['infos']['id'])

  # Verificando se o numero de registros apagados eh superior a 0 e diferente de None
  if( n_apagados > 0 and n_apagados is not None ):
    flash("Comentário apagado com sucesso!", 'success')
    return redirect(url_for('comentar_aula', aula_id=comentario[4]))
  else:
    flash("Não foi possível apagar o comentário, tente novamente!", 'danger')
    return redirect(url_for('painel'))

@app.route('/comentar/<aula_id>/', methods=['GET', 'POST',])
@login_is_required
def comentar_aula(aula_id):
  if( request.method == "POST" ):
    # Captando as informacoes passadas via form
    comentario_text = request.form.get('Comentario')

    if( comentario_text is not None ):
      # Criando uma instancia do controlador de comentarios
      comentariosdao = ComentariosDAO(get_db())

      # Instanciando a classe Comentario
      comentario = Comentario(
        comentario=comentario_text,
        aula_ou_material_id=aula_id,
        usuario_id=session['infos']['id']
      )

      # Criando um comentario e armazenando o ID do mesmo
      comentario_id = comentariosdao.cadastrar(comentario)

      # Verificando se o comentario foi cadastrado com sucesso
      if( comentario_id is not None ):
        flash('Seu comentário foi registrado!', 'success')
        return redirect(request.url)
      else:
        flash('Não foi possível comentar na aula!', 'danger')
        return redirect(request.url)
    
    else:
      flash('Preencha todos os campos!', 'warning')
      return redirect(request.url)
  
  aulasdao = AulaDAO(get_db())
  aula = aulasdao.obter(aula_id)

  comentariosdao = ComentariosDAO(get_db())
  comentarios = comentariosdao.listar(aula_id)

  return render_template('comentarios.html', aula=aula, comentarios=comentarios)

@app.route('/duvidas', methods=['GET',])
@login_is_required
def listar_duvidas():
  if( session['infos']['tipo_vinculo'] != 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  duvidadao = DuvidaDAO(get_db())
  duvidas = duvidadao.listar()

  return render_template("listar-duvidas.html", duvidas=duvidas)

@app.route('/minhas-duvidas', methods=['GET',])
@login_is_required
def minhas_duvidas():
  duvidadao = DuvidaDAO(get_db())
  duvidas = duvidadao.listar_minhas_duvidas(session['infos']['id'])

  return render_template('minhas-duvidas.html', duvidas=duvidas)

@app.route("/minhas-duvidas/remover/<duvida_id>/", methods=['GET',])
@login_is_required
def remover_duvida(duvida_id):
  duvidasdao = DuvidaDAO(get_db())
  duvida = duvidasdao.obter(duvida_id)

  if( duvida[3] != session['infos']['id'] ):
    flash("Não é possível excluir a dúvida de outra pessoa", 'danger')
    return redirect(url_for("minhas_duvidas"))
  
  duvida_removida = duvidasdao.remover(duvida[0], session['infos']['id'])

  if( duvida_removida > 0 ):
    flash("Dúvida excluida com sucesso!", 'success')
  else:
    flash("Não foi possível a apagar a dúvida", 'danger')

  return redirect(url_for("minhas_duvidas"))


@app.route('/minhas-duvidas/editar/<duvida_id>/', methods=['GET', 'POST',])
@login_is_required
def editar_minhas_duvidas(duvida_id):
  duvidasdao = DuvidaDAO(get_db())
  duvida = duvidasdao.obter(duvida_id)

  if( request.method == "POST" ):
    duvida_text = request.form.get("duvida")

    if( duvida_text is not None ):
      duvida_instance = Duvida(
        duvida_text=duvida_text,
        usuario_id=session['infos']['id']
      )

      duvida_instance.id = duvida[0]

      n_modificacoes = duvidasdao.editar(duvida_instance)

      if( n_modificacoes > 0 ):
        flash("Edição da dúvida feita com sucesso!", 'success')
      else:
        flash("Não foi possível atualizar a sua dúvida!", 'danger')

    else:
      flash("Preencha todos os campos!", 'warning')
    
    return redirect(url_for("minhas_duvidas"))

  return render_template("edicao-duvidas.html", duvida = duvida)

@app.route('/enviar-duvida', methods=['GET', 'POST',])
@login_is_required
def enviar_duvida():
  if( request.method == "POST" ):
    duvida_text = request.form.get('Duvida')

    if( duvida_text ):
      duvidadao = DuvidaDAO(get_db())

      duvida = Duvida(duvida_text, session['infos']['id'])
      duvida_id = duvidadao.cadastrar(duvida)

      if( duvida_id is not None and duvida_id > 0 ):
        flash('Dúvida registrada com sucesso!', 'success')
      else:
        flash('Não foi possível registrar sua dúvida, tente novamente!', 'danger')

    else:
      flash('Preencha todos os campos!', 'warning')
    
    return redirect(request.url)

  return render_template('envio-duvida.html')

@app.route('/materiais/comentarios/editar/<comentario_id>/', methods=['GET', 'POST',])
@login_is_required
def editar_comentario_material(comentario_id):
  if( request.method == "POST" ):
    comentario_text = request.form.get('Comentario')
    comentariosdao = ComentariosMaterialDAO(get_db())

    # Captando um comentario especifico
    comentario = comentariosdao.obter(comentario_id)

    # Verificando se o comentario existe
    if( comentario is not None ):
      # Verificando se a pessoa que fez o comentario eh a mesma que esta tentando apagar o mesmo
      if( comentario[3] != session['infos']['id'] ):
        flash('Não é possível editar um comentário que não foi você quem fez!', 'warning')
        return redirect(f"/materiais/comentarios/{comentario[4]}/")

    else:
      flash("Comentário inexistente!", 'danger')
      return redirect(f"/materiais/comentarios/{comentario[4]}/")

    # Verificando se o campo de comentario foi preenchido
    if( comentario_text is not None ):
      comentario_instance = Comentario(
        comentario=comentario_text,
        aula_ou_material_id=comentario[4],
        usuario_id=session['infos']['id']
      )

      comentario_instance.id = comentario_id

      n_alteracoes = comentariosdao.atualizar(comentario_instance)

      # Verificando se houveram alteracoes
      if( n_alteracoes > 0 and n_alteracoes is not None ):
        flash('Alterações feitas com sucesso!', 'success')
        return redirect(f"/materiais/comentarios/{comentario_instance.aula_ou_material_id}/")

      flash('Não foi possível efetuar as alterações no comentário!', 'danger')
      return redirect(f"/materiais/comentarios/{comentario_instance.aula_ou_material_id}/")

    else:
      flash('Preencha todos os campos!', 'warning')
      return redirect(f"/materiais/comentarios/{comentario[4]}/")
  
  # Captando um comentario especifico
  comentariosdao = ComentariosMaterialDAO(get_db())
  comentario = comentariosdao.obter(comentario_id)
  
  # Verificando se o comentario existe
  if( comentario is not None ):
    # Verificando se a pessoa que fez o comentario eh a mesma que esta tentando apagar o mesmo
    if( comentario[3] != session['infos']['id'] ):
      flash('Não é possível editar um comentário que não foi você quem fez!', 'warning')
      return redirect(url_for('materiais_comentarios', material_id=comentario[4]))
  
  else:
    flash("Comentário inexistente!", 'danger')
    return redirect(url_for('materiais_comentarios', material_id=comentario[4]))

  materialdao = MaterialDAO(get_db())
  material = materialdao.obter(comentario[4])

  return render_template('comentarios-materiais-editar.html', material=material, comentario=comentario)

@app.route('/materiais/comentarios/apagar/<comentario_id>/', methods=['GET', 'POST',])
@login_is_required
def apagar_comentario_id(comentario_id):
  # Criando uma instancia do controlador de comentarios
  comentariosdao = ComentariosMaterialDAO(get_db())

  # Captando um comentario especifico
  comentario = comentariosdao.obter(comentario_id)

  # Verificando se o comentario existe
  if( comentario is not None ):
    # Verificando se a pessoa que fez o comentario eh a mesma que esta tentando apagar o mesmo
    if( comentario[3] != session['infos']['id'] ):
      flash("Não é possível apagar um comentário que não foi você quem fez!", 'warning')
      return redirect(url_for('painel'))

  else:
    flash("Comentário inexistente", 'danger')
    return redirect(url_for('painel'))

  # Captando a quantidade de registros apagados
  n_apagados = comentariosdao.deletar(comentario_id=comentario_id, usuario_id=session['infos']['id'])

  # Verificando se o numero de registros apagados eh superior a 0 e diferente de None
  if( n_apagados > 0 and n_apagados is not None ):
    flash("Comentário apagado com sucesso!", 'success')
    return redirect(url_for('materiais_comentarios', material_id=comentario[4]))
  else:
    flash("Não foi possível apagar o comentário, tente novamente!", 'danger')
    return redirect(url_for('painel'))

@app.route('/materiais/comentarios/<material_id>/', methods=['GET', 'POST',])
@login_is_required
def materiais_comentarios(material_id):
  if( request.method == "POST" ):
    # Captando as informacoes passadas via form
    comentario_text = request.form.get('Comentario')

    if( comentario_text is not None ):
      # Criando uma instancia do controlador de comentarios
      comentariosdao = ComentariosMaterialDAO(get_db())

      # Instanciando a classe Comentario
      comentario = Comentario(
        comentario=comentario_text,
        aula_ou_material_id=material_id,
        usuario_id=session['infos']['id']
      )

      # Criando um comentario e armazenando o ID do mesmo
      comentario_id = comentariosdao.cadastrar(comentario)

      # Verificando se o comentario foi cadastrado com sucesso
      if( comentario_id is not None ):
        flash('Seu comentário foi registrado!', 'success')
        return redirect(request.url)
      else:
        flash('Não foi possível comentar na aula!', 'danger')
        return redirect(request.url)
    
    else:
      flash('Preencha todos os campos!', 'warning')
      return redirect(request.url)

  comentariosmateriaisdao = ComentariosMaterialDAO(get_db())
  materiaisdao = MaterialDAO(get_db())

  material = materiaisdao.obter(material_id)
  comentarios = comentariosmateriaisdao.listar(material_id)

  return render_template('comentarios-materiais.html', comentarios=comentarios, material=material)

#Área de responder duvidas
@app.route("/responder-duvida/<duvida_id>/", methods=['GET', 'POST',])
@login_is_required
def responder_duvida(duvida_id):
  duvidadao = DuvidaDAO(get_db())
  duvida = duvidadao.obter(duvida_id)

  if( request.method == "POST" ):
    resposta_texto = request.form.get("resposta")

    if( resposta_texto is not None ):
      respostadao = RespostaDAO(get_db())
      resposta = Resposta(
        texto=resposta_texto,
        duvida_id=duvida[0],
        usuario_id=session['infos']['id']
      )

      resposta_id = respostadao.cadastrar(resposta)

      if( resposta_id is not None and resposta_id > 0 ):
        flash("Resposta cadastrada com sucesso!", 'success')
      else:
        flash("Não foi possível responder a dúvida!", 'danger')
    else:
      flash("Preencha todos os campos!", 'warning')
    
    return redirect(url_for("listar_duvidas"))

  return render_template("responder-duvida.html", duvida=duvida)

@app.route('/apagar-resposta/<resposta_id>/', methods=['GET',])
@login_is_required
def apagar_resposta(resposta_id):
  respostadao = RespostaDAO(get_db())
  resposta = respostadao.obter(resposta_id)

  if( resposta is not None ):
    if( resposta[3] != session['infos']['id'] ):
      flash('Não é possível apagar uma resposta que não é sua', 'danger')
    else:
      n_apagados = respostadao.deletar(resposta[0], session['infos']['id'])

      if( n_apagados > 0 ):
        flash('Resposta apagada com sucesso!', 'success')
      else:
        flash('Não foi possível apagar a resposta','danger')

  else:
    flash('Não foi possível apagar a resposta pois ela não existe', 'danger')
  
  return redirect(url_for('listar_duvidas'))

@app.route('/editar-resposta/<resposta_id>/', methods=['GET', 'POST',])
@login_is_required
def editar_resposta(resposta_id):
  respostadao = RespostaDAO(get_db())
  resposta = respostadao.obter(resposta_id)

  if( resposta is not None ):
    if( request.method == "POST" ):
      resposta_texto = request.form.get('resposta')

      if( resposta_texto is not None ):
        resposta_instance = Resposta(texto=resposta_texto, duvida_id=resposta[2], usuario_id=session['infos']['id'])
        resposta_instance.id = resposta[0]

        n_atualizados = respostadao.atualizar(resposta_instance)

        if( n_atualizados > 0 ):
          flash('Atualização feita com sucesso!', 'success')
        else:
          flash('Não foi possível atualizar as informações.', 'warning')

        return redirect(url_for('listar_duvidas'))
      else:
        flash("Preencha todos os campos", 'warning')
        return redirect(request.url)

    return render_template('responder-duvida.html', duvida = resposta)
  else:
    flash("Não existe resposta com esse ID", 'warning')
    return redirect(url_for('listar_duvidas'))

#Cadastrando acesso das aulas no banco
@app.route('/cadastrar/acesso/aula/<aula_id>/<usuario_id>/', methods=['GET',])
def cadastrar_acesso_aula(aula_id, usuario_id):  
  acessoaula = AcessoAula(get_db())

  aula_visu = acessoaula.obter_por_usuario_aula(usuario_id, aula_id)

  if( aula_visu is None ):
    acesso = Acesso(usuario_id, aula_id)
    acessoaulaid = acessoaula.cadastrar(acesso)
  return 'a '

#Cadastrando acesso dos materiais no banco
@app.route('/cadastrar/acesso/material/<material_id>/<usuario_id>/', methods=['GET',])
def cadastrar_acesso_material(material_id,usuario_id):
  acessomaterial = AcessoMateriais(get_db())

  material_visu = acessomaterial.obter_por_usuario_material(usuario_id, material_id)

  if( material_visu is None ):
    acesso = Acesso(usuario_id, material_id)
    acessomaterialid = acessomaterial.cadastrar(acesso)
  return 'a'

#Área do desempenho
@app.route('/desempenho/aulas-vistas/<usuario_id>/',methods=['GET',])
@login_is_required

def aulas_vistas(usuario_id):
  auladao = AulaDAO(get_db())
  aulas= auladao.aulas_vistas(usuario_id)


  return render_template('aulas-vistas.html', aulas=aulas)


@app.route('/desempenho/aulas-vistas-aluno/<usuario_id>/',methods=['GET',])
@login_is_required
def aulas_vistas_aluno(usuario_id):

  if (int(session['infos']['id']) != int(usuario_id)):
    flash('Você não tem permissão para fazer isso!','danger')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))

  if( session['infos']['tipo_vinculo'] == 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel'))

  auladao = AulaDAO(get_db())
  aulas= auladao.aulas_vistas(usuario_id)


  return render_template('aulas-vistas-aluno.html', aulas=aulas)


@app.route('/desempenho/materiais-vistos/<usuario_id>/',methods=['GET',])
@login_is_required

def materiais_vistos(usuario_id):
  materiaisdao = MaterialDAO(get_db())
  materiais= materiaisdao.materiais_vistos(usuario_id)

  return render_template('materiais-vistos.html', materiais=materiais)


@app.route('/desempenho/materiais-vistos-aluno/<usuario_id>/',methods=['GET',])
@login_is_required
def materiais_vistos_aluno(usuario_id):

  if (int(session['infos']['id']) != int(usuario_id)):
    flash('Você não tem permissão para fazer isso!','danger')
    return redirect(url_for('painel_aluno', usuario_id=session['infos']['id']))
  
  if( session['infos']['tipo_vinculo'] == 1 ):
    flash('Você não possui permissão!', 'warning')
    return redirect(url_for('painel'))

  materiaisdao = MaterialDAO(get_db())
  materiais= materiaisdao.materiais_vistos(usuario_id)

  return render_template('materiais-vistos-aluno.html', materiais=materiais)


#logout
@app.route('/logout')
def logout():
  session['logged'] = None
  session.clear()
  
  flash('Logout efetuado com sucesso!', 'success')
  return redirect('/') # Redirecionando o usuário para a rota "/"