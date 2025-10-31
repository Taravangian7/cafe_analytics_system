-- SQL Server schema for Restaurante: Ingredientes, Platos, Recetas
-- 
-- Reglas de negocio:
-- 1. Platos.Costo = suma de (Recetas.Cantidad * Ingredientes.Costo) para todos los ingredientes del plato
--    Ejemplo: fideos con 0.5 kg harina ($10/kg) + 0.3 kg tomates ($5/kg) = (0.5 * 10) + (0.3 * 5) = 6.50
-- 2. Platos.GlutenFree: FALSE si al menos 1 ingrediente NO es gluten-free, TRUE solo si todos lo son
-- 3. Platos.DairyFree: FALSE si al menos 1 ingrediente NO es dairy-free, TRUE solo si todos lo son

SET NOCOUNT ON;
GO

-- Create database (safe-guard: only if not exists)
IF DB_ID(N'Restaurante') IS NULL
BEGIN
	CREATE DATABASE Restaurante;
END
GO

USE Restaurante;
GO

-- Drop objects if re-running (optional, idempotent-friendly)
IF OBJECT_ID(N'dbo.Recetas', N'U') IS NOT NULL DROP TABLE dbo.Recetas;
IF OBJECT_ID(N'dbo.Platos', N'U') IS NOT NULL DROP TABLE dbo.Platos;
IF OBJECT_ID(N'dbo.Ingredientes', N'U') IS NOT NULL DROP TABLE dbo.Ingredientes;
GO

-- Helper functions (drop first if exist)
IF OBJECT_ID(N'dbo.fn_PrecioPlato', N'FN') IS NOT NULL DROP FUNCTION dbo.fn_PrecioPlato;
IF OBJECT_ID(N'dbo.fn_PlatoGlutenFree', N'FN') IS NOT NULL DROP FUNCTION dbo.fn_PlatoGlutenFree;
IF OBJECT_ID(N'dbo.fn_PlatoDairyFree', N'FN') IS NOT NULL DROP FUNCTION dbo.fn_PlatoDairyFree;
GO

-- Core tables
CREATE TABLE dbo.Ingredientes
(
	IngredienteId INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Ingredientes PRIMARY KEY,
	Nombre        NVARCHAR(200) NOT NULL,
	Costo         DECIMAL(12,4) NOT NULL CONSTRAINT CK_Ingredientes_Costo_NonNegative CHECK (Costo >= 0),
	Cantidad      DECIMAL(18,4) NULL,  -- stock o cantidad disponible (opcional)
	Unidad        NVARCHAR(50)  NOT NULL,
	GlutenFree    BIT NOT NULL CONSTRAINT DF_Ingredientes_GlutenFree DEFAULT (0),
	DairyFree     BIT NOT NULL CONSTRAINT DF_Ingredientes_DairyFree DEFAULT (0),
	CONSTRAINT UQ_Ingredientes_Nombre UNIQUE (Nombre)
);
GO

-- Crear tabla Platos SIN columnas calculadas primero (las agregaremos después)
CREATE TABLE dbo.Platos
(
	PlatoId     INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Platos PRIMARY KEY,
	Nombre      NVARCHAR(200) NOT NULL,
	Categoria   NVARCHAR(100) NULL,
	CONSTRAINT UQ_Platos_Nombre UNIQUE (Nombre)
);
GO

CREATE TABLE dbo.Recetas
(
	PlatoId        INT NOT NULL,
	IngredienteId  INT NOT NULL,
	Cantidad       DECIMAL(18,6) NOT NULL CONSTRAINT CK_Recetas_Cantidad_Positive CHECK (Cantidad > 0),
	-- Nota: esta tabla se usa para vincular Platos e Ingredientes y no tiene primary key
	CONSTRAINT FK_Recetas_Platos FOREIGN KEY (PlatoId) REFERENCES dbo.Platos(PlatoId) ON DELETE CASCADE,
	CONSTRAINT FK_Recetas_Ingredientes FOREIGN KEY (IngredienteId) REFERENCES dbo.Ingredientes(IngredienteId)
);
GO

-- Aseguramos que no haya duplicados Plato-Ingrediente sin imponer PK explícita
CREATE UNIQUE INDEX UX_Recetas_Plato_Ingrediente ON dbo.Recetas(PlatoId, IngredienteId);
GO

-- Crear las funciones AHORA que ya existen las tablas necesarias
-- Helper scalar functions for computed columns on Platos
-- Calcula el costo del plato sumando (Cantidad * Costo) para cada ingrediente
-- Ejemplo: 0.5 kg harina ($10/kg) + 0.3 kg tomates ($5/kg) = 5.00 + 1.50 = 6.50
CREATE FUNCTION dbo.fn_PrecioPlato (@PlatoId INT)
RETURNS DECIMAL(14,4)
AS
BEGIN
	DECLARE @precio DECIMAL(14,4);
	SELECT @precio = COALESCE(SUM(r.Cantidad * i.Costo), 0)
	FROM dbo.Recetas r
	JOIN dbo.Ingredientes i ON i.IngredienteId = r.IngredienteId
	WHERE r.PlatoId = @PlatoId;
	RETURN COALESCE(@precio, 0);
END;
GO

CREATE FUNCTION dbo.fn_PlatoGlutenFree (@PlatoId INT)
RETURNS BIT
AS
BEGIN
	-- FALSE si al menos 1 ingrediente NO es gluten-free; TRUE solo si todos lo son; NULL si no hay ingredientes
	DECLARE @hasRows BIT = 0;
	IF EXISTS (SELECT 1 FROM dbo.Recetas WHERE PlatoId = @PlatoId) SET @hasRows = 1;
	IF EXISTS (
		SELECT 1
		FROM dbo.Recetas r
		JOIN dbo.Ingredientes i ON i.IngredienteId = r.IngredienteId
		WHERE r.PlatoId = @PlatoId AND i.GlutenFree = 0
	)
		RETURN CAST(0 AS BIT);
	IF @hasRows = 1 RETURN CAST(1 AS BIT);
	RETURN NULL; -- no ingredientes definidos
END;
GO

CREATE FUNCTION dbo.fn_PlatoDairyFree (@PlatoId INT)
RETURNS BIT
AS
BEGIN
	-- FALSE si al menos 1 ingrediente NO es dairy-free; TRUE solo si todos lo son; NULL si no hay ingredientes
	DECLARE @hasRows BIT = 0;
	IF EXISTS (SELECT 1 FROM dbo.Recetas WHERE PlatoId = @PlatoId) SET @hasRows = 1;
	IF EXISTS (
		SELECT 1
		FROM dbo.Recetas r
		JOIN dbo.Ingredientes i ON i.IngredienteId = r.IngredienteId
		WHERE r.PlatoId = @PlatoId AND i.DairyFree = 0
	)
		RETURN CAST(0 AS BIT);
	IF @hasRows = 1 RETURN CAST(1 AS BIT);
	RETURN NULL; -- no ingredientes definidos
END;
GO

-- Ahora agregamos las columnas calculadas a Platos usando las funciones
ALTER TABLE dbo.Platos
ADD 
	Costo       AS (dbo.fn_PrecioPlato([PlatoId])),
	GlutenFree  AS (dbo.fn_PlatoGlutenFree([PlatoId])),
	DairyFree   AS (dbo.fn_PlatoDairyFree([PlatoId]));
GO

-- Helpful views (optional): detailed platos with computed fields
IF OBJECT_ID(N'dbo.Platos_Detalle', N'V') IS NOT NULL DROP VIEW dbo.Platos_Detalle;
GO
CREATE VIEW dbo.Platos_Detalle
AS
SELECT
	p.PlatoId,
	p.Nombre,
	p.Categoria,
	p.Costo,
	p.GlutenFree,
	p.DairyFree
FROM dbo.Platos p;
GO

-- Indexing for lookups
CREATE INDEX IX_Ingredientes_Nombre ON dbo.Ingredientes(Nombre);
CREATE INDEX IX_Platos_Categoria ON dbo.Platos(Categoria);
CREATE INDEX IX_Recetas_Ingrediente ON dbo.Recetas(IngredienteId);
GO

-- Quick sanity checks (comment out if not needed)
-- SELECT * FROM sys.tables;
-- SELECT * FROM sys.objects WHERE type IN ('FN','IF','TF');
-- SELECT * FROM dbo.Platos_Detalle;
