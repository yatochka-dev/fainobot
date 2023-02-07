/*
  Warnings:

  - You are about to drop the column `originalId` on the `InventoryItem` table. All the data in the column will be lost.
  - Added the required column `title` to the `InventoryItem` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "InventoryItem" DROP CONSTRAINT "InventoryItem_originalId_fkey";

-- AlterTable
ALTER TABLE "InventoryItem" DROP COLUMN "originalId",
ADD COLUMN     "replyMessage" TEXT,
ADD COLUMN     "title" VARCHAR(200) NOT NULL;
