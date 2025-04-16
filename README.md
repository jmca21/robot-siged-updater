
# Robô SIGED (SEMSA) para Render.com

Este robô acessa o SIGED, coleta atualizações dos processos prioritários e atualiza o repositório no GitHub, mantendo o painel Streamlit sempre atualizado.

## Como usar no Render.com

1. Faça login em https://render.com
2. Crie um novo serviço do tipo Background Worker
3. Conecte ao repositório deste projeto (após clonar para sua conta)
4. Configure as variáveis de ambiente:

- GITHUB_TOKEN: seu token do GitHub
- SIGED_LOGIN: CPF de login no SIGED
- SIGED_SENHA: senha de acesso

5. Configure o cron job com este agendamento (a cada 1 minuto):

```
* * * * *
```

6. O painel será mantido atualizado 24h por dia.
