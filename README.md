
# Introdução
Este relatório detalha a solução proposta para o problema de venda de passagens aéreas compartilhadas, apelidado de PASSCOM, sentido a a otimização da venda de três companhias aéreas de baixo custo brasileiras. Com o interesse de aumentar a rentabilidade e a eficaz utilização de recursos, as companhias concordaram em implementar uma solução para a venda de trechos de voos conjuntos da janela Low Cost, como são conhecidas. No entanto, devido ao uso atual de servidores centralizados e independentes por cada companhia, a  produção da reserva de passagens de um mesmo voo é impossível. Por meio da criação de uma API REST, buscamos estabelecer uma comunicação eficiente entre os servidores, de forma a permitir a reserva de voos segmentados diferentes das companhias de maneira simples e rápida. O direcionamento da produção proposta no projeto foi de que a integração deveria ocorrer com o uso de contêineres Docker. Além disso, destaca-se a importância de um README detalhado no repositório GitHub, que servirá como um guia para a compreensão da implementação e funcionamento do sistema.
Por fim, serão apresentados os resultados dos testes realizados, que visam validar a eficácia da solução proposta, garantindo que ela atenda às expectativas e necessidades das LCCs envolvidas.

# Fundamentação teórica 

Este projeto visa desenvolver um sistema distribuído para a venda compartilhada de passagens entre múltiplos servidores, utilizando uma arquitetura RESTful e integrando o backend com uma interface web para o usuário. A seguir, são apresentados os principais conceitos teóricos que embasam o desenvolvimento e a implementação dessa solução.

Sistemas Distribuídos e Coordenação de Transações: em um sistema distribuído, várias entidades de software são executadas em diferentes servidores que se comunicam para alcançar um objetivo comum, como no nosso caso, a venda integrada de passagens entre múltiplas companhias aéreas. Esse tipo de arquitetura permite que cada servidor opere de forma independente, porém colabora na reserva de assentos, o que promove resiliência e escalabilidade. No projeto, implementa-se uma comunicação entre servidores através de transações distribuídas, e para gerenciar essas transações distribuídas de forma eficiente, foi utilizado o algoritmo Two-Phase Commit (2PC). Esse algoritmo assegura que todas as partes envolvidas na transação concordem com a operação antes de qualquer alteração ser efetivada. Na primeira fase, os servidores enviam um pedido de confirmação para todos os participantes, e, se todos concordarem, a segunda fase é iniciada, onde as operações são efetivamente aplicadas. Esse processo é crítico para garantir que, quando um usuário tenta reservar uma passagem que envolve múltiplos servidores, todas as operações sejam consistentes. Um bloqueio (lock) foi utilizado, o que impede a leitura/escrita concorrente e protege a integridade dos dados de voo ao evitar condições de corrida.

APIS RESTful: a arquitetura REST (Representational State Transfer) é amplamente utilizada em sistemas distribuídos pela simplicidade e flexibilidade que oferece na comunicação entre servidores. Com a API REST, é possível que o cliente faça requisições HTTP para consultar voos, comprar passagens e coordenar transações entre os servidores das companhias. 

Docker e Virtualização: o uso de contêineres Docker é uma prática comum para sistemas distribuídos. Docker permite que cada componente do sistema seja empacotado com todas as dependências necessárias, o que facilita a implantação e desenvolvimento do sistema. No projeto, os contêineres foram usados para isolar e executar o ambiente de cada servidor, minimizando problemas de compatibilidade entre as diferentes instâncias do sistema e permitindo uma execução controlada e previsível em diferentes ambientes.

Flask, Autenticação e Gerenciamento de Sessões: flask é um framework minimalista para desenvolvimento web em Python que permite a construção de APIs e aplicações de forma rápida e eficiente. Neste projeto, Flask foi utilizado para gerenciar as rotas da aplicação e a autenticação dos usuários. A autenticação e o gerenciamento de sessões foram implementados com o auxílio do Login Manager, que, junto com a biblioteca Flask-Login, facilita a criação e o gerenciamento de sessões de usuário. Esse processo é essencial para controlar o acesso às informações de voos e garantir que cada transação seja associada ao usuário autenticado.

Interface: a interface do sistema foi desenvolvida utilizando HTML e CSS, fornecendo uma interface amigável e intuitiva para o usuário. HTML foi utilizado para estruturar o conteúdo da página, enquanto CSS foi aplicado para estilizar e melhorar a usabilidade, criando um ambiente visual mais atraente e coerente. Isso é importante em um sistema de reservas, onde a clareza e a facilidade de navegação são essenciais para a experiência do usuário.
![Captura de tela do sistema](https://github.com/user-attachments/assets/b5252605-d264-4cd8-a7de-884c889b5ecb)
*Figura 1. Tela de Login.*

Ambiente virtual com venv: para gerenciar as dependências do projeto, foi utilizado o venv, uma ferramenta que permite criar ambientes virtuais em Python. O uso de venv garante que cada instalação de biblioteca seja isolada, evitando conflitos entre pacotes de diferentes projetos e facilitando a reprodução do ambiente de desenvolvimento por outros membros da equipe ou para testes. Além disso, o ambiente virtual contribui para a segurança e consistência do desenvolvimento, mantendo todas as dependências bem definidas.

Serialização de dados com Json: a serialização com JSON permite que os dados sejam facilmente armazenados e transferidos entre o servidor e o cliente. Neste projeto, dados como informações de voos e reservas foram salvos em arquivos JSON, o que permite que o estado do sistema seja mantido entre reinicializações do servidor e que as operações de leitura e escrita sejam executadas de forma rápida e direta. JSON é especialmente útil para este tipo de projeto por ser leve, de fácil manipulação e amplamente compatível com diversas linguagens de programação.

