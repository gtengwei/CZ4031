CREATE TABLE public.partsupp(
	ps_partkey integer NOT NULL,
	ps_suppkey integer NOT NULL,
	ps_availqty integer NOT NULL,
	ps_supplycost numeric(15,2) NOT NULL,
	ps_comment character varying(199) COLLATE pg_catalog."default" NOT NULL,
	CONSTRAINT partsupp_key PRIMARY KEY (ps_partkey, ps_suppkey),
	CONSTRAINT fk_ps_suppkey_partkey FOREIGN KEY (ps_partkey)
		REFERENCES public.part (p_partkey) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	CONSTRAINT fk_ps_suppkey_suppkey FOREIGN KEY (ps_suppkey)
		REFERENCES public.supplier (s_suppkey) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
)

WITH (
	OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.partsupp
	OWNER to postgres;

