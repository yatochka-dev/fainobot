/*
  Warnings:

  - You are about to drop the `InvokedSlashCommand` table. If the table is not empty, all the data it contains will be lost.

*/
-- CreateEnum
CREATE TYPE "InvokedCommandType" AS ENUM ('application', 'text');

-- DropTable
DROP TABLE "InvokedSlashCommand";

-- CreateTable
CREATE TABLE "InvokedCommand" (
    "name" CHAR(50) NOT NULL,
    "count" INTEGER NOT NULL DEFAULT 0,
    "type" "InvokedCommandType" NOT NULL DEFAULT 'application',

    CONSTRAINT "InvokedCommand_pkey" PRIMARY KEY ("name")
);
