DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'gestao_de_funcionarios_app') THEN
        CREATE ROLE gestao_de_funcionarios_app LOGIN PASSWORD 'local_app_only_change_me' NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
END
$$;

GRANT CONNECT ON DATABASE gestao_de_funcionarios TO gestao_de_funcionarios_app;
GRANT USAGE ON SCHEMA public TO gestao_de_funcionarios_app;
