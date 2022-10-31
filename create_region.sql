CREATE TABLE public.region
(
	r_regionkey integer NOT NULL,
	r_name character(25) COLLATE pg_catalog."default",
	CONSTRAINT region_pkey PRIMARY KEY (r_regionkey)
)
WITH (
	OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE public.region
	OWNER to postgres;
