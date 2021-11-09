/*
Create SEQUENCE for table
*/
DROP SEQUENCE IF EXISTS @exchangeName_id_seq;
CREATE SEQUENCE @exchangeName_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;

/*
Create Table structure for table
*/
DROP TABLE IF EXISTS "public"."@exchangeName";
CREATE TABLE "public"."@exchangeName" (
  "id" int4 NOT NULL DEFAULT nextval('@exchangeName_id_seq'::regclass),
  "time" timestamp(6) NOT NULL,
  "open" float8,
  "high" float8,
  "low" float8,
  "close" float8,
  "volume" float8,
  "info" varchar COLLATE "pg_catalog"."default" NOT NULL
)
;

/*
Create Primary Key structure for table
*/
ALTER TABLE "public"."@exchangeName" DROP CONSTRAINT IF EXISTS "@exchangeName_pkey";
ALTER TABLE "public"."@exchangeName" ADD CONSTRAINT "@exchangeName_pkey" PRIMARY KEY ("time", "info");