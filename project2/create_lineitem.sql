CREATE TABLE public.lineitem
(
	l_orderkey integer NOT NULL,
	l_partkey integer NOT NULL,
	l_suppkey integer NOT NULL,
	l_linenumber integer NOT NULL,
	l_quantity numeric (15,2) NOT NULL,
	l_extendedprice numeric (15,2) NOT NULL,
	l_discount numeric (15,2) NOT NULL,
	l_tax numeric (15,2) NOT NULL,
	l_returnflag character (1) COLLATE pg_catalog."default" NOT NULL,
	l_linestatus character (1) COLLATE pg_catalog."default" NOT NULL,
	l_shipdate date NOT NULL,
	l_commitdate date NOT NULL,
	l_receiptdate date NOT NULL,
	l_shipinstruct character (25) COLLATE pg_catalog."default" NOT NULL,
	l_shipmode character (10) COLLATE pg_catalog."default" NOT NULL,
	l_comment character varying (44) COLLATE pg_catalog."default" NOT NULL,
	CONSTRAINT lineitem_pkey PRIMARY KEY (l_orderkey, l_partkey, l_suppkey, l_linenumber),
	CONSTRAINT fk_lineitem_orderkey FOREIGN KEY (l_orderkey)
		REFERENCES public.orders (o_orderkey) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	CONSTRAINT fk_lineitem_partkey FOREIGN KEY (l_partkey)
		REFERENCES public.part (p_partkey) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	CONSTRAINT fk_lineitem_suppkey FOREIGN KEY (l_suppkey)
		REFERENCES public.supplier (s_suppkey) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)
WITH (
	OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.lineitem
OWNER to postgres;