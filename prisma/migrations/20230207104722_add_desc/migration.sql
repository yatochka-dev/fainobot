/*
  Warnings:

  - Added the required column `description` to the `InventoryItem` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "InventoryItem" ADD COLUMN     "description" TEXT NOT NULL;
