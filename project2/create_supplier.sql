CREATE TABLE public.supplier(
	s_suppkey integer NOT NULL,
	s_name character(25) COLLATE pg_catalog."default" NOT NULL,
	s_address character varying(40) COLLATE pg_catalog."default" NOT NULL,
	s_nationkey integer NOT NULL,
	s_phone character(15) COLLATE pg_catalog."default" NOT NULL,
	s_acctbal numeric(15,2) NOT NULL,
	s_comment character varying(101) COLLATE pg_catalog."default" NOT NULL,
	CONSTRAINT supplier_pkey PRIMARY KEY (s_suppkey),
	CONSTRAINT fk_supplier FOREIGN KEY (s_nationkey)
		REFERENCES public.nation (n_nationkey) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

WITH (
	OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.supplier
	OWNER to postgres;

