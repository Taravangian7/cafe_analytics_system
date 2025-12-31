IF OBJECT_ID('dbo.Receta', 'U') IS NOT NULL DROP TABLE dbo.Receta;
IF OBJECT_ID('dbo.Platos', 'U') IS NOT NULL DROP TABLE dbo.Platos;
IF OBJECT_ID('dbo.Ingredientes', 'U') IS NOT NULL DROP TABLE dbo.Ingredientes;
IF OBJECT_ID('dbo.fn_precio_plato', 'FN') IS NOT NULL DROP FUNCTION dbo.fn_precio_plato;
IF OBJECT_ID('dbo.fn_PlatoGlutenFree', 'FN') IS NOT NULL DROP FUNCTION dbo.fn_PlatoGlutenFree;
IF OBJECT_ID('dbo.fn_PlatoDairyFree', 'FN') IS NOT NULL DROP FUNCTION dbo.fn_PlatoDairyFree;

create table Ingredientes (
	id_ingrediente int identity(1,1) not null primary key,
	Nombre nvarchar(50)not null,
	Costo decimal(12,4) not null constraint CK_Ingredientes_Costo check (Costo>=0),
	Cantidad decimal (12,4) not null,
	Unidad nvarchar(50) not null,
	Gluten_free bit not null,
	Dairy_free bit not null,
	Elaborado bit not null default 0,
	Constraint UQ_Ingredientes_Nombre unique(Nombre));

create table Platos (
	id_plato int identity (1,1) not null primary key,
	Nombre nvarchar(50)not null,
	Categoria nvarchar(50)not null,
	Constraint UQ_Platos_Nombre unique(Nombre));

create table Receta (
	Plato nvarchar (50) not null,
	Ingrediente nvarchar (50) not null,
	Cantidad decimal (12,4) not null constraint CK_Receta_Cantidad check (Cantidad>=0),
	Unidad nvarchar (50) not null,
	CONSTRAINT FK_Receta_Plato FOREIGN KEY (Plato) REFERENCES dbo.Platos(Nombre) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT FK_Receta_Ingrediente FOREIGN KEY (Ingrediente) REFERENCES dbo.Ingredientes(Nombre) ON DELETE CASCADE ON UPDATE CASCADE);

-- Aseguramos que no haya duplicados Plato-Ingrediente sin imponer PK expl�cita
CREATE UNIQUE INDEX UX_Recetas_Plato_Ingrediente ON dbo.Receta(Plato, Ingrediente);



GO
--Creo las funciones para calcular costos
create function dbo.fn_precio_plato (@plato_nombre nvarchar(50))
returns decimal(12,4)
as
begin
	declare @precio decimal(14,4);
	select @precio = coalesce(sum((Receta.Cantidad * Ingredientes.Costo)/Ingredientes.Cantidad),0)
	from Receta
	join Ingredientes on Ingredientes.Nombre=Receta.Ingrediente
	where Receta.Plato=@plato_nombre;
	return coalesce(@precio,0);
end;

GO
create function dbo.fn_PlatoGlutenFree (@plato_nombre nvarchar(50))
returns bit
as
begin
	-- FALSE si al menos 1 ingrediente NO es gluten-free;
	IF EXISTS (
		SELECT 1
		FROM Receta
		JOIN Ingredientes ON Ingredientes.Nombre = Receta.Ingrediente
		WHERE Receta.Plato = @plato_nombre AND Ingredientes.Gluten_free = 0
	)
		RETURN CAST(0 AS BIT);
	RETURN CAST(1 AS BIT);
END;

GO
create function dbo.fn_PlatoDairyFree (@plato_nombre nvarchar(50))
returns bit
as
begin
	-- FALSE si al menos 1 ingrediente NO es dairy-free
	IF EXISTS (
		SELECT 1
		FROM Receta
		JOIN Ingredientes ON Ingredientes.Nombre = Receta.Ingrediente
		WHERE Receta.Plato = @plato_nombre AND Ingredientes.Dairy_free = 0
	)
		RETURN CAST(0 AS BIT);
	RETURN CAST(1 AS BIT);
END;

GO
--Agrego columnas a tabla de Platos
Alter table Platos
add
	Costo as (dbo.fn_precio_plato([Nombre])),
	Precio decimal(12,4),
	Dairy_free as (dbo.fn_PlatoDairyFree([Nombre])),
	Gluten_free as (dbo.fn_PlatoGlutenFree([Nombre]));
GO 

Create table Orders(
Order_id int not null primary key,
Order_date date,
Order_time time,
Day_of_week nvarchar(30),
Payment_method nvarchar(30),
Order_type nvarchar(30),
Total_amount decimal(12,4)
);

Create table Order_items(
Item_id int not null primary key,
Order_id int,
Product_name nvarchar(50),
Quantity decimal(12,4),
Unit_price decimal(12,4),
Total_price as Quantity*Unit_price,
CONSTRAINT FK_Order_items_Orderid FOREIGN KEY (Order_id) REFERENCES dbo.Orders(Order_id) ON DELETE CASCADE ON UPDATE CASCADE,
CONSTRAINT FK_Order_items_Product_name FOREIGN KEY (Product_name) REFERENCES dbo.Platos(Nombre) ON DELETE CASCADE ON UPDATE CASCADE
);	
GO
CREATE TRIGGER trg_insert_price
ON Receta
AFTER INSERT, UPDATE
AS
BEGIN
	SET NOCOUNT ON;
    UPDATE Platos
    SET Precio = 3*dbo.fn_precio_plato(Nombre)
    FROM Platos
    WHERE Precio is null
      AND Nombre IN (SELECT Plato FROM inserted);
END;
