CREATE TABLE public.customer(
	c_custkey integer NOT NULL,
	c_name character varying (25) COLLATE pg_catalog."default" NOT NULL,
	c_address character varying (40) COLLATE pg_catalog."default" NOT NULL,
	c_nationkey integer NOT NULL,
	c_phone character (15) COLLATE pg_catalog."default" NOT NULL,
	c_acctbal numeric (15,2) NOT NULL,
	c_mktsegment character (10) COLLATE pg_catalog."default" NOT NULL,
	c_comment character varying (117) COLLATE pg_catalog. "default" NOT NULL,
	CONSTRAINT customer_pkey PRIMARY KEY (c_custkey),
	CONSTRAINT fk_customer FOREIGN KEY (c_nationkey)
		REFERENCES public.nation (n_nationkey) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

WITH (
	OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.customer
	OWNER to postgres;

