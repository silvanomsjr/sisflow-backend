# SisFlow Back-end - Solução da atividade de Término de Conclusão de Curso (TCC)

Esta camada juntamente com o Front-end copõe a solução aplicada na minha monografia da universidade.

## **Membros**

- **Aluno**: Vinicius Calixto Rocha
- **Orientador**: Prof. Dr. Alexsandro Santos Soares

## **Sobre o repositório**

Este repositório possui persistido a camada de negócios definida utilizando Python com o framework Flask que compõe a API do sistema e regras de persistência utilizando MVC e ORM com MySQLAlchemy. A estrutura de módulos utilizada, bem como as classes internas à aplicação se baseiam em templates modernos da comunidade de desenvolvedores e pode ser consultada na monografia relacionada a esta solução.

## **Início rápido**

Para executar o código localmente:

1. Clone o repositório
2. Abra o terminal no diretório
3. Instale as dependencias do python utilizando o comando `pip install -r requirements.txt`
4. Insira os arquivos de ambiente(`.env`) necessários para o Back-end
5. Execute o projeto Flask utilizando o comando `flask --app server run` para versões de desenvolvimento ou `gunicorn server:server`para ambientes de disponibilizção em contâiners na nuvem
6. Utilize as rotas cnfiguradas pela coleção do Postman para testes, ou inicie juntamente o Front-end para testar toda a aplicação em conjunto

>**Obs:** Lembre-se de configurar as variáveis de ambiente.
