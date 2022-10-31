CREATE TABLE public.part(
	p_partkey integer NOT NULL,
	p_name character varying(55) COLLATE pg_catalog."default" NOT NULL,
	p_mfgr character(25) COLLATE pg_catalog."default" NOT NULL,
	p_brand character(10) COLLATE pg_catalog."default" NOT NULL,
	p_type character varying(25) COLLATE pg_catalog."default" NOT NULL,
	p_size integer NOT NULL,
	p_container character(10) COLLATE pg_catalog."default" NOT NULL,
	p_retailprice numeric(15,2) NOT NULL,
	p_comment character varying (23) COLLATE pg_catalog."default" NOT NULL,
	CONSTRAINT part_pkey PRIMARY KEY (p_partkey)
)

WITH (
	OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.part
	OWNER to postgres;

