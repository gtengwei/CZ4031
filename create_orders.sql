CREATE TABLE public.orders(
	o_orderkey integer NOT NULL,
	o_custkey integer NOT NULL,
	o_orderstatus character (1) COLLATE pg_catalog."default" NOT NULL,
	o_totalprice numeric (15,2) NOT NULL,
	o_orderdate date NOT NULL,
	o_orderpriority character (15) COLLATE pg_catalog."default" NOT NULL,
	o_clerk character (15) COLLATE pg_catalog."default" NOT NULL,
	o_shippriority integer NOT NULL,
	o_comment character varying (79) COLLATE pg_catalog."default" NOT NULL,
	CONSTRAINT orders_pkey PRIMARY KEY (o_orderkey),
	CONSTRAINT fk_orders FOREIGN KEY (o_custkey)
		REFERENCES public.customer (c_custkey) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

WITH (
	OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.orders
	OWNER to postgres;

