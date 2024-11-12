# SisFlow Back-end - Solução da atividade de Término de Conclusão de Curso (TCC)

Esta camada juntamente com o Front-end compõe a solução aplicada na minha monografia da universidade. Esta é a Segunda versão do sistema iniciado pelo Vinícius Calixto Rocha Acesse a [monografia](https://repositorio.ufu.br/bitstream/123456789/39771/2/AplicacaoWebAuxiliar.pdf) da primeira versão deste projeto. Posteriormente incluirei o link de minha monografia com um estudo de usabilidade mais aprofundado utilizando este sistema como base.

## **Membros**

- **Aluno**: Carlos Augusto Dantas Marquez
- **Orientador**: Prof. Dr. Renan Gonçalves Cattelan

## **Sobre o repositório**

Este repositório possui persistido a camada de negócios definida utilizando **Python** com o framework **Flask** que compõe a API do sistema e regras de persistência utilizando **MVC** e **ORM** com **MySQLAlchemy**. Parte da lógica da camada é abstraída em uma **máquina de estados** que utiliza de eventos e interações com o usuário para a transição de estados que determinam o fluxo dos usuários na aplicação.

A estrutura de módulos utilizada, bem como as classes internas à aplicação, se baseiam em templates modernos da comunidade de desenvolvedores e pode ser consultada na monografia relacionada a esta solução.

Conteúdo relevante do Back-end:
  * MVC (Model-View-Controller)
  * ORM (Object Relational Mapper)
  * Máquina de estados
  * Agendador de eventos
  * Servidor de envio de e-mails
  * Segurança utilizando autenticação do usuário via JWT

## **Links úteis** ##

Acesse a primeira [monografia](https://repositorio.ufu.br/bitstream/123456789/39771/2/AplicacaoWebAuxiliar.pdf) deste projeto.

Visite o repositório com o [Front-end](https://github.com/carlosadnsm/sisflow-frontend) da solução.

## **Início rápido**

Para executar o código localmente:

1. Clone o repositório
2. Abra o terminal no diretório
3. Instale as dependencias do python utilizando o comando `pip install -r requirements.txt`
4. Insira os arquivos de ambiente(`.env`) necessários para o Back-end
5. Execute o projeto Flask utilizando o comando `flask --app server run` para versões de desenvolvimento ou `gunicorn server:server`para ambientes de disponibilizção em contâiners na nuvem
6. Utilize as rotas cnfiguradas pela coleção do Postman para testes, ou inicie juntamente o Front-end para testar toda a aplicação em conjunto

>**Obs:** Lembre-se de configurar as variáveis de ambiente
