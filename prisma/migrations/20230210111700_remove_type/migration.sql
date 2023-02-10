/*
  Warnings:

  - You are about to drop the column `type` on the `InvokedCommand` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "InvokedCommand" DROP COLUMN "type";

-- DropEnum
DROP TYPE "InvokedCommandType";
