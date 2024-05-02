CREATE TABLE "users" (
	"user_id"	TEXT NOT NULL UNIQUE,
	"user_password"	TEXT NOT NULL,
	"user_mail" TEXT NOT NULL,
	"content_is_public"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("user_id")
);

CREATE TABLE "auth" (
	"auth_token"	TEXT NOT NULL UNIQUE,
	"auth_user_id"	TEXT NOT NULL,
	"auth_token_time"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"auth_token_ip"	TEXT NOT NULL,
	PRIMARY KEY("auth_token")
);

CREATE TABLE "clipboard" (
	"clip_id" TEXT NOT NULL UNIQUE,
	"clip_url"	TEXT NOT NULL,
	"clip_user_id"	TEXT NOT NULL,
	"clip_title"	TEXT NOT NULL,
	"clip_description"	TEXT NOT NULL,
	"clip_image"	TEXT NOT NULL,
	"clip_ip"	TEXT NOT NULL,
	"clip_time"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("clip_id")
);
