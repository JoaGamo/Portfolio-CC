-- Create database (run this separately if needed)
-- CREATE DATABASE bolsa_de_valores;

-- Connect to database
\c bolsa_de_valores;

-- Create initialization log table
CREATE TABLE IF NOT EXISTS initialization_log (
    id SERIAL PRIMARY KEY,
    script_name VARCHAR(255) NOT NULL UNIQUE,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Use DO block for initialization logic
DO $$
BEGIN
    -- Check if script has been executed
    IF NOT EXISTS (SELECT 1 FROM initialization_log WHERE script_name = 'init.sql') THEN
        -- Tipo operacion = "compra", "venta"
        -- Tipo instrumento = "accion", "bono", "crypto"
        CREATE TABLE operacion (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMP NOT NULL,
            tipo_operacion VARCHAR(255) NOT NULL,
            tipo_instrumento VARCHAR(255) NOT NULL,
            ticker VARCHAR(255) NOT NULL,
            cantidad NUMERIC(19,4) NOT NULL,
            precio NUMERIC(19,4) NOT NULL,
            comisiones NUMERIC(19,4) DEFAULT 0,
            mercado VARCHAR(255) NOT NULL,
            notas TEXT,
            CONSTRAINT idx_ticker_fecha UNIQUE (ticker, fecha)
        );

        -- Create index for tipo_instrumento
        CREATE INDEX idx_tipo_instrumento ON operacion(tipo_instrumento);

        -- Log the execution
        INSERT INTO initialization_log (script_name) VALUES ('init.sql');
    END IF;
END $$;